"""Bot avatar endpoints for server admins (dashboard).

Note: Discord allows only ONE global bot avatar. Any change made here
overrides the avatar for all servers (last upload wins). Bot admins can
override or reset it via the admin panel.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from .. import auth, profile_service
from ..database import Database
from .dashboard import require_guild_admin

router = APIRouter(prefix="/api", tags=["profile"])


def get_db(request: Request) -> Database:
    return request.app.state.db


@router.get("/profile")
async def get_profile(request: Request):
    """Current bot avatar (requires login)."""
    await auth.current_user(request)
    profile = await get_db(request).get_bot_profile()
    if not profile:
        return {
            "avatar": None,
            "updated_by": None,
            "updated_at": None,
        }
    return {
        "avatar": profile.get("avatar"),
        "updated_by": profile.get("updated_by"),
        "updated_at": profile.get("updated_at"),
    }


@router.post("/profile/apply")
async def apply_profile(payload: dict, request: Request):
    """Set the bot avatar (guild admin of a server where WordLock is active)."""
    guild_id = int(payload.get("guild_id") or 0)
    if not guild_id:
        raise HTTPException(status_code=400, detail="guild_id is required")
    user = await require_guild_admin(guild_id, request)
    db = get_db(request)
    server = await db.get_server(guild_id)
    if not server:
        raise HTTPException(status_code=404, detail="WordLock is not on this server")

    avatar = payload.get("avatar")
    if not avatar:
        raise HTTPException(status_code=400, detail="avatar is required")
    stored = await profile_service.apply_and_store(db, avatar, user["discord_id"], guild_id)
    return {"ok": True, "avatar": stored.get("avatar")}
