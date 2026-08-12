"""Message filtering events (on_message / on_message_edit)."""

from __future__ import annotations

import datetime
import logging

import discord
from discord.ext import commands

from ..version import __version__

log = logging.getLogger("safeword.bot.events")

ACTION_LABELS = {
    "delete": "Message deleted",
    "warn": "Warning",
    "timeout": "Timeout",
    "log": "Logged only",
}

COLORS = {
    "insult": 0xED4245,
    "profanity": 0xED4245,
    "slur": 0xFF0000,
    "sexual": 0xEB459E,
    "threat": 0x992D22,
    "spam": 0xFEE75C,
    "custom": 0x5865F2,
}


class MessageEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        await self._process(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.content != after.content:
            await self._process(after)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        await self.bot.db.upsert_server(
            guild_id=guild.id,
            name=guild.name,
            owner_id=guild.owner_id,
            member_count=guild.member_count,
            bot_version=self.bot.version,
        )
        await self.bot.db.bump_stat("servers_joined", 1)
        log.info("Joined guild %s (%s)", guild.name, guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        if guild_config := await self.bot.db.get_server(guild.id):
            await self.bot.db.update_server(guild.id, status="removed")
        await self.bot.filters.invalidate(guild.id)
        log.info("Left guild %s (%s)", guild.name, guild.id)

    async def _process(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if not message.guild:
            return
        if not message.content:
            return

        server = await self.bot.db.get_server(message.guild.id)
        if not server or server.get("status") != "active":
            return

        if await self._is_bypassed(message, server):
            return

        try:
            engine = await self.bot.filters.get_or_load(message.guild.id)
        except Exception:
            log.exception("Filter build failed for guild %s", message.guild.id)
            return

        result = engine.check(message.content)
        if result is None:
            return

        _, _, _, entry = result
        mod_level = server.get("mod_level") or 3
        actions = self._resolve_actions(entry, server)

        # Words below the moderation level are only logged if no action was
        # explicitly configured (per-word override or server action settings).
        explicit = bool(entry.action) or any(
            server.get(k)
            for k in ("action_delete", "action_warn", "action_timeout", "action_log")
        )
        if entry.severity < mod_level and not explicit:
            actions = ["log"]

        await self.bot.db.log_violation(
            guild_id=message.guild.id,
            user_id=message.author.id,
            message_text=message.content[:1500],
            matched_word=entry.word,
            category=entry.category,
            severity=entry.severity,
            action=",".join(actions) or "log",
        )

        executed: list[str] = []
        member = message.guild.get_member(message.author.id)
        for action in actions:
            if action == "delete" and message.guild.me.guild_permissions.manage_messages:
                try:
                    await message.delete()
                    executed.append("delete")
                except discord.HTTPException:
                    log.debug("Could not delete message %s", message.id)
            elif action == "warn":
                await self.bot.db.add_warning(
                    message.guild.id, message.author.id,
                    reason=f"Filter: {entry.word} ({entry.category})",
                    moderator=self.bot.user.id if self.bot.user else None,
                )
                executed.append("warn")
                await self._dm_warning(message.author, entry)
            elif action == "timeout" and member is not None:
                timeout_ok = (
                    message.guild.me.guild_permissions.moderate_members
                    and message.guild.me.top_role > member.top_role
                )
                if timeout_ok:
                    try:
                        minutes = server.get("timeout_minutes") or 60
                        await member.timeout(
                            discord.utils.utcnow()
                            + datetime.timedelta(minutes=minutes),
                            reason=f"SafeWord: {entry.word} ({entry.category})",
                        )
                        executed.append("timeout")
                    except discord.HTTPException:
                        log.debug("Could not timeout %s", member.id)
            elif action == "log":
                executed.append("log")

        if server.get("log_channel_id") and (
            "log" in actions or server.get("action_log")
        ):
            await self._send_log_embed(message, entry, executed)

    def _resolve_actions(self, entry, server: dict) -> list[str]:
        """Per-word action override wins, server defaults otherwise."""
        if entry.action:
            return [entry.action]
        actions: list[str] = []
        if server.get("action_delete"):
            actions.append("delete")
        if server.get("action_warn"):
            actions.append("warn")
        if server.get("action_timeout"):
            actions.append("timeout")
        if server.get("action_log") or not actions:
            actions.append("log")
        return actions

    async def _is_bypassed(self, message: discord.Message, server: dict) -> bool:
        """Server-side bypass: guild owners, whitelisted users and roles are
        never filtered."""
        member = message.guild.get_member(message.author.id)
        if member is None:
            return False
        if member.id == message.guild.owner_id:
            return True
        if member.guild_permissions.administrator:
            return True
        try:
            bypass_users = server.get("bypass_users") or []
            if isinstance(bypass_users, str):
                import json

                bypass_users = json.loads(bypass_users)
            if message.author.id in {int(u) for u in bypass_users}:
                return True
            bypass_roles = server.get("bypass_roles") or []
            if isinstance(bypass_roles, str):
                import json

                bypass_roles = json.loads(bypass_roles)
            if {r.id for r in member.roles} & {int(r) for r in bypass_roles}:
                return True
        except Exception:
            log.exception("Bypass check failed for guild %s", message.guild.id)
        return False

    async def _dm_warning(self, author: discord.User, entry) -> None:
        try:
            embed = discord.Embed(
                title="SafeWord",
                description=(
                    f"Your message on a server was filtered by SafeWord. "
                    f"Detected: `{entry.word}` (category: {entry.category})."
                ),
                color=0xED4245,
            )
            await author.send(embed=embed)
        except (discord.HTTPException, discord.Forbidden):
            pass

    async def _send_log_embed(
        self, message: discord.Message, entry, executed: list[str]
    ) -> None:
        server = await self.bot.db.get_server(message.guild.id)
        if not server:
            return
        channel = message.guild.get_channel(server.get("log_channel_id"))
        if not isinstance(channel, discord.TextChannel):
            return

        color = COLORS.get(entry.category, 0x5865F2)
        embed = discord.Embed(
            title="Filter violation",
            description=f"**Word:** `{entry.word}`\n**Category:** {entry.category}\n"
            f"**Severity:** {entry.severity}/5\n**Actions:** {', '.join(executed) or '—'}",
            color=color,
        )
        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
        embed.add_field(
            name="Message",
            value=(message.content[:1000] or "*no text*"),
            inline=False,
        )
        embed.set_footer(text=f"SafeWord v{__version__} • User ID: {message.author.id}")
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            log.debug("Could not send log embed in %s", channel.id)
