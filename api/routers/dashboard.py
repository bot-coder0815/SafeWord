"""Public dashboard endpoints (Discord OAuth2 login + guild management)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from .. import auth
from ..database import Database

router = APIRouter(prefix="/api", tags=["dashboard"])

DASHBOARD_URL = os.environ.get(
    "DASHBOARD_URL", "http://localhost:3000"
)
WORD_ACTIONS = ["delete", "warn", "timeout", "log"]
WORD_CATEGORIES = ["insult", "profanity", "slur", "sexual", "threat", "spam", "custom"]


def get_db(request: Request) -> Database:
    return request.app.state.db


async def require_guild_admin(guild_id: int, request: Request):
    """Current user must be able to manage the given guild (or be bot owner)."""
    user = await auth.current_user(request)
    db = get_db(request)
    if user["discord_id"] in auth._whitelist():
        return user
    guilds = await auth.fetch_user_guilds(user.get("access_token") or "")
    for g in guilds:
        if int(g["id"]) == guild_id and (g.get("permissions") or 0) & auth.MANAGE_GUILD:
            return user
    raise HTTPException(status_code=403, detail="You are not an admin of this guild")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


@router.get("/auth/login")
async def auth_login() -> dict:
    return {"url": auth.authorize_url()}


@router.get("/auth/invite")
async def auth_invite() -> dict:
    return {"url": auth.invite_url()}


@router.get("/auth/callback")
async def auth_callback(
    code: str = Query(...),
    state: Optional[str] = None,
    request: Request = None,
    response: Response = None,
):
    db = get_db(request)
    try:
        tokens = await auth.exchange_code(code)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Login failed, please try again")

    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")
    discord_user = await auth.fetch_user(access_token)
    user = await db.upsert_user(
        discord_id=int(discord_user["id"]),
        username=discord_user.get("username", "unknown"),
        access_token=access_token,
        refresh_token=refresh_token,
    )
    token = auth.create_session_token(user["discord_id"])
    auth.set_session_cookie(response, token)
    response.status_code = 302
    response.headers["Location"] = f"{DASHBOARD_URL}/dashboard"
    return response


@router.get("/auth/logout")
async def auth_logout(response: Response) -> dict:
    auth.clear_session_cookie(response)
    return {"ok": True}


@router.get("/auth/me")
async def auth_me(request: Request):
    user = await auth.current_user(request)
    role = auth._effective_role(user)
    db = get_db(request)
    guilds = await auth.fetch_user_guilds(user.get("access_token") or "")
    known_rows = await db.all_servers()
    known = {int(r["guild_id"]): r for r in known_rows}
    admin_guilds = auth.admin_guilds_for(user, guilds, known)
    return {
        "id": str(user["discord_id"]),
        "username": user.get("username"),
        "avatar": user.get("avatar"),
        "role": role,
        "admin_guilds": admin_guilds,
        "maintenance": await db.maintenance_mode(),
    }


@router.get("/auth/guild-permissions")
async def guild_permissions(guild_id: int, request: Request):
    await require_guild_admin(guild_id, request)
    return {"guild_id": guild_id, "can_manage": True}


# ---------------------------------------------------------------------------
# Privacy / GDPR data request
# ---------------------------------------------------------------------------


@router.get("/data-request")
async def data_request_summary(request: Request):
    """Show which personal data SafeWord stores for the logged-in user."""
    user = await auth.current_user(request)
    db = get_db(request)
    uid = user["discord_id"]
    violations = int(
        await db._fetchval("SELECT COUNT(*) FROM violations WHERE user_id = $1", uid) or 0
    )
    warnings = int(
        await db._fetchval("SELECT COUNT(*) FROM warnings WHERE user_id = $1", uid) or 0
    )
    return {
        "user_id": str(uid),
        "username": user.get("username"),
        "violations": violations,
        "warnings": warnings,
        "role": auth._effective_role(user),
    }


@router.post("/data-request")
async def data_request_delete(request: Request, response: Response):
    """Delete all stored data for the logged-in user (GDPR / DSGVO)."""
    user = await auth.current_user(request)
    db = get_db(request)
    uid = user["discord_id"]

    def _deleted_count(tag: str) -> int:
        try:
            return int(tag.split()[-1])
        except (ValueError, IndexError):
            return 0

    violations_tag = await db._execute("DELETE FROM violations WHERE user_id = $1", uid)
    warnings_tag = await db._execute("DELETE FROM warnings WHERE user_id = $1", uid)
    await db._execute(
        "UPDATE users SET access_token = NULL, refresh_token = NULL "
        "WHERE discord_id = $1",
        uid,
    )
    auth.clear_session_cookie(response)
    return {
        "ok": True,
        "deleted_violations": _deleted_count(violations_tag),
        "deleted_warnings": _deleted_count(warnings_tag),
    }


# ---------------------------------------------------------------------------
# Guild configuration
# ---------------------------------------------------------------------------


@router.get("/guilds/{guild_id}")
async def get_guild_config(guild_id: int, request: Request):
    await require_guild_admin(guild_id, request)
    db = get_db(request)
    server = await db.get_server(guild_id)
    if not server:
        raise HTTPException(status_code=404, detail="SafeWord is not on this server")
    return server


@router.get("/guilds/{guild_id}/channels")
async def guild_channels(guild_id: int, request: Request):
    """List the guild's sendable text channels (for the announce/log channel picker)."""
    await require_guild_admin(guild_id, request)
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="DISCORD_TOKEN not configured")
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{auth.DISCORD_API}/guilds/{guild_id}/channels",
            headers={"Authorization": f"Bot {token}"},
            timeout=15,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Could not load channels")
    channels = [
        {"id": str(c["id"]), "name": c.get("name"), "type": c.get("type")}
        for c in resp.json()
        if c.get("type") in (0, 5)
    ]
    return {"channels": channels}


@router.get("/team")
async def public_team(request: Request):
    """Public team hierarchy for the landing page (#team)."""
    return await get_db(request).list_team()


@router.put("/guilds/{guild_id}")
async def update_guild_config(guild_id: int, payload: dict, request: Request):
    await require_guild_admin(guild_id, request)
    db = get_db(request)
    allowed = {
        "language", "mod_level", "log_channel_id", "action_delete",
        "action_warn", "action_timeout", "action_log", "timeout_minutes",
        "default_lists", "bypass_roles", "bypass_users",
    }
    fields = {k: v for k, v in payload.items() if k in allowed}
    if not fields:
        raise HTTPException(status_code=400, detail="No valid fields provided")
    await db.update_server(guild_id, **fields)
    return await db.get_server(guild_id)


@router.get("/guilds/{guild_id}/words")
async def get_guild_words(
    guild_id: int, request: Request, enabled_only: bool = Query(True)
):
    await require_guild_admin(guild_id, request)
    return await get_db(request).get_custom_words(guild_id, enabled_only)


@router.post("/guilds/{guild_id}/words")
async def add_guild_word(guild_id: int, payload: dict, request: Request):
    await require_guild_admin(guild_id, request)
    db = get_db(request)
    word = (payload.get("word") or "").strip().lower()
    if not word or len(word) > 100:
        raise HTTPException(status_code=400, detail="Invalid word")
    category = payload.get("category", "custom")
    severity = int(payload.get("severity", 3))
    action = payload.get("action", "delete")
    if severity not in range(1, 6):
        raise HTTPException(status_code=400, detail="Severity must be 1-5")
    if action not in WORD_ACTIONS:
        raise HTTPException(status_code=400, detail="Invalid action")
    ok = await db.add_custom_word(guild_id, word, category, severity, action)
    if not ok:
        raise HTTPException(status_code=400, detail="Could not add word")
    return {"ok": True, "word": word}


@router.delete("/guilds/{guild_id}/words/{word}")
async def remove_guild_word(guild_id: int, word: str, request: Request):
    await require_guild_admin(guild_id, request)
    ok = await get_db(request).remove_custom_word(guild_id, word.lower())
    if not ok:
        raise HTTPException(status_code=404, detail="Word not found")
    return {"ok": True}


@router.patch("/guilds/{guild_id}/words/{word}/enabled")
async def set_word_enabled(
    guild_id: int, word: str, payload: dict, request: Request
):
    await require_guild_admin(guild_id, request)
    enabled = bool(payload.get("enabled"))
    await get_db(request).set_custom_word_enabled(guild_id, word.lower(), enabled)
    return {"ok": True, "enabled": enabled}


@router.get("/guilds/{guild_id}/lists")
async def available_lists(guild_id: int, request: Request):
    await require_guild_admin(guild_id, request)
    data_dir = Path(
        os.environ.get(
            "DATA_DIR",
            str(Path(__file__).resolve().parent.parent.parent / "data"),
        )
    )
    available = []
    for f in sorted(data_dir.glob("default_words_*.json")):
        lang = f.stem.replace("default_words_", "")
        with f.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        meta = data.get("meta", {})
        available.append(
            {
                "language": lang,
                "name": meta.get("name", lang),
                "version": meta.get("version", "?"),
                "words": len(data.get("words", [])),
            }
        )
    return {"available": available}


@router.get("/guilds/{guild_id}/standard-words")
async def standard_words(guild_id: int, request: Request, enabled_only: bool = Query(False)):
    """Standard list words for this guild, merged with per-guild overrides."""
    await require_guild_admin(guild_id, request)
    db = get_db(request)
    server = await db.get_server(guild_id)
    default_lists = (server or {}).get("default_lists") or {"de": True, "en": True}
    if isinstance(default_lists, str):
        default_lists = json.loads(default_lists)
    languages = [lang for lang, active in default_lists.items() if active]

    data_dir = Path(
        os.environ.get(
            "DATA_DIR",
            str(Path(__file__).resolve().parent.parent.parent / "data"),
        )
    )
    entries: list[dict] = []
    for lang in languages:
        path = data_dir / f"default_words_{lang}.json"
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        for item in payload.get("words", []):
            entries.append(
                {
                    "word": item["word"],
                    "category": item.get("category", "profanity"),
                    "severity": item.get("severity", 3),
                    "language": lang,
                    "enabled": True,
                    "action": None,
                }
            )

    overrides = {o["word"]: o for o in await db.get_word_overrides(guild_id)}
    out = []
    for e in entries:
        ov = overrides.get(e["word"])
        if ov is not None:
            e["enabled"] = bool(ov["enabled"])
            e["action"] = ov.get("action")
        if enabled_only and not e["enabled"]:
            continue
        out.append(e)
    return out


@router.patch("/guilds/{guild_id}/standard-words/{word}")
async def patch_standard_word(guild_id: int, word: str, payload: dict, request: Request):
    """Enable/disable or change the action of a standard word for this guild."""
    await require_guild_admin(guild_id, request)
    db = get_db(request)
    action = payload.get("action")
    enabled = bool(payload.get("enabled", True))
    if action is not None and action not in WORD_ACTIONS:
        raise HTTPException(status_code=400, detail="Invalid action")
    await db.set_word_override(guild_id, word.lower().strip(), action, enabled)
    return {"ok": True, "word": word.lower().strip(), "action": action, "enabled": enabled}


@router.delete("/guilds/{guild_id}/standard-words/{word}")
async def delete_standard_word(guild_id: int, word: str, request: Request):
    """Reset a standard word back to its default behavior for this guild."""
    await require_guild_admin(guild_id, request)
    ok = await get_db(request).remove_word_override(guild_id, word.lower())
    if not ok:
        raise HTTPException(status_code=404, detail="No override found")
    return {"ok": True}


@router.get("/guilds/{guild_id}/stats")
async def guild_stats(guild_id: int, request: Request, days: int = Query(30, le=90)):
    await require_guild_admin(guild_id, request)
    db = get_db(request)
    server = await db.get_server(guild_id)
    today_series = await db.violations_series(guild_id, 1)
    return {
        "guild_id": guild_id,
        "guild_name": (server or {}).get("name", ""),
        "member_count": (server or {}).get("member_count", 0),
        "status": (server or {}).get("status", "unknown"),
        "violations_today": sum(int(r["value"]) for r in today_series),
        "violations_series": await db.violations_series(guild_id, days),
        "top_words": await db.violations_top_words(guild_id, 10),
        "actions": await db.action_counts(guild_id),
        "warning_count": int(
            (await db._fetchval(
                "SELECT COUNT(*) FROM warnings WHERE guild_id = $1", guild_id
            )) or 0
        ),
    }
