"""FastAPI entry point for the WordLock dashboard backend."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import push_service
from .database import Database
from .routers import admin, dashboard, security, webhook
from .version import __version__

log = logging.getLogger("wordlock.api")

PUSH_POLL_SECONDS = int(os.environ.get("PUSH_POLL_SECONDS", "20"))

# Discord snowflake IDs exceed Number.MAX_SAFE_INTEGER (2^53 - 1). JavaScript
# would round them in JSON.parse, corrupting every subsequent lookup. We ship
# such big ints as strings so the dashboard can round-trip them exactly.
MAX_SAFE_INT = 2**53 - 1


def _safe(o):
    if isinstance(o, dict):
        return {k: _safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_safe(v) for v in o]
    if isinstance(o, int) and not isinstance(o, bool) and (o > MAX_SAFE_INT or o < -MAX_SAFE_INT):
        return str(o)
    return o


class SafeJSONResponse(JSONResponse):
    def render(self, content):
        return (
            json.dumps(
                _safe(content),
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")
        )


async def _push_poll_loop(db: Database) -> None:
    """Periodically send pending security push notifications."""
    log.info("Push notification poller started (every %ss)", PUSH_POLL_SECONDS)
    while True:
        await asyncio.sleep(PUSH_POLL_SECONDS)
        try:
            sent = await push_service.process_pending(db)
            if sent:
                log.info("Sent %s push notification(s)", sent)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Push poll iteration failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    dsn = os.environ.get(
        "DATABASE_URL", "postgresql://wordlock:wordlock@localhost:5432/wordlock"
    )
    db = Database(dsn)
    await db.connect()
    app.state.db = db
    app.state.started_at = datetime.now(timezone.utc).isoformat()
    log.info("WordLock API v%s connected to database", __version__)
    poller = asyncio.create_task(_push_poll_loop(db))
    try:
        yield
    finally:
        poller.cancel()
        try:
            await poller
        except (asyncio.CancelledError, Exception):
            pass
        await db.close()


app = FastAPI(
    title="WordLock API",
    description="Backend for the WordLock Discord moderation dashboard.",
    version=__version__,
    lifespan=lifespan,
    default_response_class=SafeJSONResponse,
)

origins = [
    o.strip()
    for o in os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(security.router)
app.include_router(webhook.router)


@app.get("/")
async def root() -> dict:
    return {"name": "WordLock API", "version": __version__, "docs": "/docs"}


@app.get("/api/health")
async def health(request: Request) -> dict:
    db: Database = request.app.state.db
    db_ok = True
    try:
        async with db._pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "version": __version__,
    }


@app.get("/api/status")
async def api_status(request: Request) -> dict:
    import time as _time

    db: Database = request.app.state.db
    started_at = getattr(request.app.state, "started_at", None)
    database = "unreachable"
    try:
        async with db._pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        database = "connected"
    except Exception:
        pass

    bot = "offline"
    last_hb = await db.last_heartbeat()
    if last_hb:
        age = _time.time() - last_hb
        bot = "online" if age < 120 else "offline"

    return {
        "version": __version__,
        "started_at": started_at,
        "status": {
            "api": "online",
            "database": database,
            "bot": bot,
        },
        "stats": {
            "active_servers": await db.active_server_count(),
            "servers": await db.server_count(),
            "active_users": await db.active_users(),
            "violations_today": await db.violations_today(),
            "violations_total": await db.violations_total(),
        },
        "maintenance": await db.maintenance_mode(),
    }
