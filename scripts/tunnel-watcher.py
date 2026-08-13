#!/usr/bin/env python3
"""tunnel-watcher: propagiert die aktuelle trycloudflare-URL ins Git-Repo
und überwacht gleichzeitig API/Backend + Bot-Heartbeat.

Ausfall-Überwachung:
  - API wird per HTTP-Healthcheck geprüft, der Bot über bot_heartbeat.
  - Ist eines von beiden länger als DOWN_THRESHOLD (Default 5 min) down,
    wird eine Web-Push-Nachricht an alle Admin-Subscriptions geschickt.
  - Während der Ausfall anhält, wird alle RESEND_INTERVAL (Default 30 min)
    erneut gepusht.
  - Über die API (POST /api/admin/monitor/mute) kann der aktuelle Ausfall
    stummgeschaltet werden (State in DB, monitor_settings). Beim nächsten
    Ausfall (nach Erholung) wird wieder benachrichtigt.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import subprocess
import time
from pathlib import Path

import asyncpg
import httpx

log = logging.getLogger("tunnel-watcher")
logging.basicConfig(level=logging.INFO, format="[watcher] %(message)s")

LOG = Path("/tunnel-log/tunnel.log")
REPO_DIR = Path("/repo")
BRANCH = os.environ.get("REPO_BRANCH", "main")
URL_INTERVAL = int(os.environ.get("INTERVAL", "15"))
FILE = os.environ.get("REPO_FILE", "config/instance-url.json")

REPO_URL = os.environ.get("REPO_URL")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GIT_USER_NAME = os.environ.get("GIT_USER_NAME", "wordlock-tunnel-watcher")
GIT_USER_EMAIL = os.environ.get("GIT_USER_EMAIL", "tunnel-watcher@users.noreply.github.com")

DATABASE_URL = os.environ.get("DATABASE_URL")
API_HEALTH_URL = os.environ.get("API_HEALTH_URL", "http://wordlock-api:8000/api/health")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "30"))
DOWN_THRESHOLD = int(os.environ.get("DOWN_THRESHOLD", "300"))
RESEND_INTERVAL = int(os.environ.get("RESEND_INTERVAL", "1800"))
HEARTBEAT_MAX_AGE = int(os.environ.get("HEARTBEAT_MAX_AGE", "120"))

VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_SUBJECT = os.environ.get("VAPID_SUBJECT", "mailto:dev@wordlock.example")

URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def push_configured() -> bool:
    return bool(VAPID_PUBLIC_KEY and VAPID_PRIVATE_KEY)


# ---------------------------------------------------------------------------
# Tunnel-URL Propagation
# ---------------------------------------------------------------------------


def get_url() -> str | None:
    if not LOG.exists():
        return None
    try:
        content = LOG.read_text(errors="ignore")
    except OSError:
        return None
    matches = URL_RE.findall(content)
    return matches[-1] if matches else None


def _run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)


def auth_url() -> str:
    if not REPO_URL or not GITHUB_TOKEN:
        raise RuntimeError("REPO_URL and GITHUB_TOKEN are required")
    return f"https://x-access-token:{GITHUB_TOKEN}@{REPO_URL.removeprefix('https://')}"


def clone_or_pull() -> None:
    if not (REPO_DIR / ".git").exists():
        log.info("Cloning repository ...")
        if REPO_DIR.exists():
            subprocess.run(["rm", "-rf", str(REPO_DIR)], timeout=120)
        _run(["git", "clone", "--depth", "1", "--branch", BRANCH, auth_url(), str(REPO_DIR)])
    else:
        _run(["git", "-C", str(REPO_DIR), "remote", "set-url", "origin", auth_url()])
        log.info("Pulling latest changes ...")
        res = _run(["git", "-C", str(REPO_DIR), "pull", "--ff-only", "origin", BRANCH])
        if res.returncode != 0:
            log.warning("Pull failed: %s", res.stderr.strip() or res.stdout.strip())


def push_url(url: str) -> None:
    clone_or_pull()
    payload = json.dumps({"url": url})
    target = REPO_DIR / FILE
    if target.exists() and target.read_text().strip() == payload:
        log.info("URL unchanged in repo, nothing to do.")
        return

    REPO_DIR.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload + "\n")
    _run(["git", "-C", str(REPO_DIR), "config", "user.name", GIT_USER_NAME])
    _run(["git", "-C", str(REPO_DIR), "config", "user.email", GIT_USER_EMAIL])
    _run(["git", "-C", str(REPO_DIR), "add", FILE])
    commit = _run(["git", "-C", str(REPO_DIR), "commit", "-m", f"chore: tunnel URL -> {url}"])
    if commit.returncode != 0:
        log.info("Nothing to commit")
        return
    log.info("Pushing tunnel URL to %s ...", BRANCH)
    _run(["git", "-C", str(REPO_DIR), "push", "origin", BRANCH])
    log.info("Done.")


async def url_loop() -> None:
    last = ""
    while True:
        try:
            url = get_url()
            if url and url != last:
                log.info("Detected tunnel URL: %s", url)
                last = url
                await asyncio.to_thread(push_url, url)
        except Exception:
            log.exception("URL propagation failed")
        await asyncio.sleep(URL_INTERVAL)


# ---------------------------------------------------------------------------
# Downtime monitoring + push
# ---------------------------------------------------------------------------


def _now() -> float:
    return time.time()


async def api_is_healthy() -> bool:
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(API_HEALTH_URL)
            return resp.status_code == 200
    except Exception:
        return False


async def bot_is_healthy(pool: asyncpg.Pool) -> bool:
    try:
        row = await pool.fetchval("SELECT EXTRACT(EPOCH FROM last_seen) FROM bot_heartbeat WHERE id = 1")
    except Exception:
        return False
    return bool(row is not None and (_now() - float(row)) < HEARTBEAT_MAX_AGE)


async def load_settings(pool: asyncpg.Pool) -> dict:
    row = await pool.fetchrow("SELECT muted, down_since, last_notified FROM monitor_settings WHERE id = 1")
    if not row:
        await pool.execute(
            "INSERT INTO monitor_settings (id, muted) VALUES (1, FALSE) ON CONFLICT (id) DO NOTHING"
        )
        return {"muted": False, "down_since": None, "last_notified": None}
    return {
        "muted": bool(row["muted"]),
        "down_since": row["down_since"].timestamp() if row["down_since"] else None,
        "last_notified": row["last_notified"].timestamp() if row["last_notified"] else None,
    }


async def save_settings(pool: asyncpg.Pool, down_since: float | None, last_notified: float | None) -> None:
    await pool.execute(
        "UPDATE monitor_settings SET down_since = CASE WHEN $1::float IS NULL "
        "THEN NULL ELSE to_timestamp($1) END, "
        "last_notified = CASE WHEN $2::float IS NULL THEN NULL ELSE to_timestamp($2) END, "
        "updated_at = now() WHERE id = 1",
        down_since,
        last_notified,
    )


def _describe_outage(api_ok: bool, bot_ok: bool) -> str:
    parts = []
    if not api_ok:
        parts.append("Backend")
    if not bot_ok:
        parts.append("Bot")
    return " + ".join(parts)


async def send_push(pool: asyncpg.Pool, down_since: float) -> None:
    if not push_configured():
        log.warning("VAPID not configured — skipping push")
        return

    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        log.warning("pywebpush is not installed — skipping push")
        return

    rows = await pool.fetch(
        "SELECT ps.id, ps.endpoint, ps.keys FROM push_subscriptions ps "
        "JOIN users u ON u.discord_id = ps.user_id "
        "WHERE u.role IN ('owner', 'developer', 'moderator')"
    )
    if not rows:
        log.info("No admin push subscriptions — nothing to send")
        return

    duration = int(_now() - down_since)
    minutes = max(1, duration // 60)
    payload = {
        "title": "⚠️ WordLock Ausfall",
        "body": f"Backend/Bot sind seit ~{minutes} Min. nicht erreichbar.",
        "icon": "/icon-192.png",
        "badge": "/icon-192.png",
        "url": "/admin",
        "tag": "wordlock-outage",
        "downId": int(down_since),
        "actions": [
            {"action": "mute", "title": "🔕 Für diesen Ausfall stummschalten"},
        ],
    }

    sent = 0
    for row in rows:
        try:
            await asyncio.to_thread(
                webpush,
                subscription_info={
                    "endpoint": row["endpoint"],
                    "keys": json.loads(row["keys"]),
                },
                data=json.dumps(payload),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_SUBJECT},
                timeout=10,
            )
            sent += 1
        except WebPushException as exc:
            if getattr(exc.response, "status_code", None) in (404, 410):
                await pool.execute(
                    "DELETE FROM push_subscriptions WHERE id = $1", row["id"]
                )
            else:
                log.debug("Push failed: %s", exc)
        except Exception:
            log.exception("Unexpected push error")
    log.info("Sent %s push notification(s)", sent)


async def monitor_loop(pool: asyncpg.Pool) -> None:
    log.info(
        "Monitor started: down-threshold %ss, resend every %ss, check every %ss",
        DOWN_THRESHOLD,
        RESEND_INTERVAL,
        CHECK_INTERVAL,
    )
    while True:
        try:
            api_ok = await api_is_healthy()
            bot_ok = await bot_is_healthy(pool)
            settings = await load_settings(pool)
            now = _now()

            down = not (api_ok and bot_ok)
            if down:
                if settings["down_since"] is None:
                    log.warning("Outage started: %s down", _describe_outage(api_ok, bot_ok))
                    await save_settings(pool, now, None)
                elif not settings["muted"]:
                    age = now - settings["down_since"]
                    last = settings["last_notified"]
                    if (
                        age >= DOWN_THRESHOLD
                        and (last is None or (now - last) >= RESEND_INTERVAL)
                    ):
                        await send_push(pool, settings["down_since"])
                        last = now
                    await save_settings(pool, settings["down_since"], last)
            else:
                if settings["down_since"] is not None:
                    log.info("System healthy again — outage ended, mute cleared.")
                await save_settings(pool, None, None)
                if settings["muted"]:
                    await pool.execute(
                        "UPDATE monitor_settings SET muted = FALSE, updated_at = now() WHERE id = 1"
                    )
        except Exception:
            log.exception("Monitor iteration failed")
        await asyncio.sleep(CHECK_INTERVAL)


async def main() -> None:
    if not DATABASE_URL:
        log.error("DATABASE_URL is required")
        raise SystemExit(1)

    pool = await asyncpg.create_pool(DATABASE_URL)
    await pool.execute(
        "CREATE TABLE IF NOT EXISTS monitor_settings ("
        " id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),"
        " muted BOOLEAN NOT NULL DEFAULT FALSE,"
        " down_since TIMESTAMPTZ,"
        " last_notified TIMESTAMPTZ,"
        " updated_at TIMESTAMPTZ DEFAULT now())"
    )
    await pool.execute(
        "INSERT INTO monitor_settings (id, muted) VALUES (1, FALSE) ON CONFLICT (id) DO NOTHING"
    )

    try:
        await asyncio.gather(url_loop(), monitor_loop(pool))
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
