"""PostgreSQL access for the SafeWord bot (asyncpg)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import asyncpg

SCHEMA = """
CREATE TABLE IF NOT EXISTS servers (
    guild_id         BIGINT PRIMARY KEY,
    name             TEXT DEFAULT '',
    owner_id         BIGINT,
    status           TEXT DEFAULT 'active',
    language         TEXT DEFAULT 'en',
    mod_level        INTEGER DEFAULT 3,
    log_channel_id   BIGINT,
    action_delete    BOOLEAN DEFAULT TRUE,
    action_warn      BOOLEAN DEFAULT TRUE,
    action_timeout   BOOLEAN DEFAULT TRUE,
    action_log       BOOLEAN DEFAULT TRUE,
    timeout_minutes  INTEGER DEFAULT 60,
    default_lists    JSONB DEFAULT '{"de": true, "en": true}',
    bypass_roles     JSONB DEFAULT '[]',
    bypass_users     JSONB DEFAULT '[]',
    bot_version      TEXT,
    member_count     INTEGER DEFAULT 0,
    created_at       TIMESTAMPTZ DEFAULT now(),
    updated_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS custom_words (
    id          SERIAL PRIMARY KEY,
    guild_id    BIGINT NOT NULL,
    word        TEXT NOT NULL,
    category    TEXT DEFAULT 'custom',
    severity    INTEGER DEFAULT 3,
    action      TEXT DEFAULT 'delete',
    enabled     BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    UNIQUE (guild_id, word)
);

CREATE TABLE IF NOT EXISTS standard_word_overrides (
    guild_id    BIGINT NOT NULL,
    word        TEXT NOT NULL,
    action      TEXT,
    enabled     BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (guild_id, word)
);

CREATE TABLE IF NOT EXISTS violations (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    guild_id     BIGINT,
    user_id      BIGINT,
    message_text TEXT,
    matched_word TEXT,
    category     TEXT,
    severity     INTEGER,
    action       TEXT,
    created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS warnings (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    guild_id   BIGINT NOT NULL,
    user_id    BIGINT NOT NULL,
    reason     TEXT,
    moderator  BIGINT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS global_stats (
    stat_name  TEXT NOT NULL,
    day        DATE NOT NULL DEFAULT CURRENT_DATE,
    value      BIGINT DEFAULT 0,
    PRIMARY KEY (stat_name, day)
);

CREATE TABLE IF NOT EXISTS users (
    discord_id    BIGINT PRIMARY KEY,
    username      TEXT,
    role          TEXT DEFAULT 'user',
    access_token  TEXT,
    refresh_token TEXT,
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS updates (
    id                SERIAL PRIMARY KEY,
    version           TEXT NOT NULL,
    title             TEXT NOT NULL,
    changelog         TEXT,
    maintenance_mode  BOOLEAN DEFAULT FALSE,
    announced         BOOLEAN DEFAULT FALSE,
    kind              TEXT DEFAULT 'announce',
    date              TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS logs (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    type       TEXT NOT NULL,
    level      TEXT DEFAULT 'info',
    guild_id   BIGINT,
    message    TEXT,
    stacktrace TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS incidents (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    guild_id     BIGINT NOT NULL,
    kind         TEXT NOT NULL,
    severity     TEXT DEFAULT 'high',
    actor_id     BIGINT,
    detail       JSONB NOT NULL DEFAULT '{}'::jsonb,
    consequence  TEXT,
    status       TEXT DEFAULT 'open',
    pushed       BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMPTZ DEFAULT now(),
    resolved_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_violations_guild ON violations (guild_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_created ON logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_custom_words_guild ON custom_words (guild_id);
CREATE INDEX IF NOT EXISTS idx_incidents_guild ON incidents (guild_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_open ON incidents (pushed, created_at) WHERE status = 'open';
ALTER TABLE updates ADD COLUMN IF NOT EXISTS announced BOOLEAN DEFAULT FALSE;
ALTER TABLE updates ADD COLUMN IF NOT EXISTS kind TEXT DEFAULT 'announce';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS bypass_roles JSONB DEFAULT '[]';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS bypass_users JSONB DEFAULT '[]';
CREATE TABLE IF NOT EXISTS standard_word_overrides (
    guild_id    BIGINT NOT NULL,
    word        TEXT NOT NULL,
    action      TEXT,
    enabled     BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (guild_id, word)
);
"""


class Database:
    def __init__(self, dsn: Optional[str] = None):
        self._dsn = dsn or os.environ.get(
            "DATABASE_URL", "postgresql://safeword:safeword@localhost:5432/safeword"
        )
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(self._dsn, min_size=1, max_size=10)
        await self.execute(SCHEMA)

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def execute(self, query: str, *args: Any) -> Any:
        return await self._pool.execute(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        return await self._pool.fetchrow(query, *args)

    async def fetch(self, query: str, *args: Any) -> List[asyncpg.Record]:
        return await self._pool.fetch(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        return await self._pool.fetchval(query, *args)

    # ------------------------------------------------------------------
    # Servers / config
    # ------------------------------------------------------------------

    async def upsert_server(
        self,
        guild_id: int,
        name: str = "",
        owner_id: Optional[int] = None,
        member_count: int = 0,
        bot_version: Optional[str] = None,
    ) -> None:
        await self.execute(
            """
            INSERT INTO servers (guild_id, name, owner_id, member_count, bot_version)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id) DO UPDATE SET
                name = EXCLUDED.name,
                member_count = EXCLUDED.member_count,
                bot_version = COALESCE(EXCLUDED.bot_version, servers.bot_version),
                updated_at = now()
            """,
            guild_id,
            name,
            owner_id,
            member_count,
            bot_version,
        )

    async def get_server(self, guild_id: int) -> Optional[Dict[str, Any]]:
        row = await self.fetchrow("SELECT * FROM servers WHERE guild_id = $1", guild_id)
        return dict(row) if row else None

    async def update_server(self, guild_id: int, **fields: Any) -> None:
        if not fields:
            return
        cols = ", ".join(f"{k} = ${i + 1}" for i, k in enumerate(fields))
        values = [
            json.dumps(v) if isinstance(v, (dict, list)) else v for v in fields.values()
        ]
        await self.execute(
            f"UPDATE servers SET {cols}, updated_at = now() WHERE guild_id = ${len(fields) + 1}",
            *values,
            guild_id,
        )

    async def all_servers(self) -> List[Dict[str, Any]]:
        rows = await self.fetch("SELECT * FROM servers ORDER BY created_at ASC")
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Custom words
    # ------------------------------------------------------------------

    async def add_custom_word(
        self, guild_id: int, word: str, category: str, severity: int, action: str
    ) -> bool:
        try:
            await self.execute(
                """
                INSERT INTO custom_words (guild_id, word, category, severity, action)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (guild_id, word) DO UPDATE SET
                    category = EXCLUDED.category,
                    severity = EXCLUDED.severity,
                    action = EXCLUDED.action,
                    enabled = TRUE
                """,
                guild_id,
                word,
                category,
                severity,
                action,
            )
            return True
        except asyncpg.PostgresError:
            return False

    async def remove_custom_word(self, guild_id: int, word: str) -> bool:
        res = await self.execute(
            "DELETE FROM custom_words WHERE guild_id = $1 AND word = $2",
            guild_id,
            word,
        )
        return res.endswith(" 1")

    async def set_custom_word_enabled(self, guild_id: int, word: str, enabled: bool) -> None:
        await self.execute(
            "UPDATE custom_words SET enabled = $3 WHERE guild_id = $1 AND word = $2",
            guild_id,
            word,
            enabled,
        )

    async def get_custom_words(
        self, guild_id: int, enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        q = "SELECT * FROM custom_words WHERE guild_id = $1"
        if enabled_only:
            q += " AND enabled = TRUE"
        q += " ORDER BY created_at ASC"
        rows = await self.fetch(q, guild_id)
        return [dict(r) for r in rows]

    async def get_word_overrides(self, guild_id: int) -> List[Dict[str, Any]]:
        rows = await self.fetch(
            "SELECT * FROM standard_word_overrides WHERE guild_id = $1", guild_id
        )
        return [dict(r) for r in rows]

    async def set_word_override(
        self,
        guild_id: int,
        word: str,
        action: Optional[str],
        enabled: bool = True,
    ) -> None:
        await self.execute(
            """
            INSERT INTO standard_word_overrides (guild_id, word, action, enabled)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (guild_id, word) DO UPDATE SET
                action = EXCLUDED.action,
                enabled = EXCLUDED.enabled,
                created_at = now()
            """,
            guild_id,
            word,
            action,
            enabled,
        )

    async def remove_word_override(self, guild_id: int, word: str) -> bool:
        res = await self.execute(
            "DELETE FROM standard_word_overrides WHERE guild_id = $1 AND word = $2",
            guild_id,
            word,
        )
        return res.endswith(" 1")

    # ------------------------------------------------------------------
    # Violations / warnings
    # ------------------------------------------------------------------

    async def log_violation(
        self,
        guild_id: int,
        user_id: int,
        message_text: str,
        matched_word: str,
        category: str,
        severity: int,
        action: str,
    ) -> None:
        await self.execute(
            """
            INSERT INTO violations (guild_id, user_id, message_text, matched_word, category, severity, action)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            guild_id,
            user_id,
            message_text,
            matched_word,
            category,
            severity,
            action,
        )
        await self.bump_stat("violations", 1)
        await self.bump_stat(f"action_{action}", 1)

    async def add_warning(
        self, guild_id: int, user_id: int, reason: str, moderator: Optional[int] = None
    ) -> None:
        await self.execute(
            "INSERT INTO warnings (guild_id, user_id, reason, moderator) VALUES ($1, $2, $3, $4)",
            guild_id,
            user_id,
            reason,
            moderator,
        )

    async def warning_count(self, guild_id: int, user_id: int) -> int:
        val = await self.fetchval(
            "SELECT COUNT(*) FROM warnings WHERE guild_id = $1 AND user_id = $2",
            guild_id,
            user_id,
        )
        return int(val or 0)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    async def bump_stat(self, name: str, amount: int = 1) -> None:
        await self.execute(
            """
            INSERT INTO global_stats (stat_name, day, value)
            VALUES ($1, CURRENT_DATE, $2)
            ON CONFLICT (stat_name, day) DO UPDATE SET value = global_stats.value + $2
            """,
            name,
            amount,
        )

    async def get_stats(
        self, name: str, days: int = 30
    ) -> List[Dict[str, Any]]:
        rows = await self.fetch(
            """
            SELECT day, value FROM global_stats
            WHERE stat_name = $1 AND day >= CURRENT_DATE - $2::int
            ORDER BY day ASC
            """,
            name,
            days,
        )
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Admin / logging
    # ------------------------------------------------------------------

    async def add_log(
        self,
        log_type: str,
        message: str,
        level: str = "info",
        guild_id: Optional[int] = None,
        stacktrace: Optional[str] = None,
    ) -> None:
        await self.execute(
            """
            INSERT INTO logs (type, level, guild_id, message, stacktrace)
            VALUES ($1, $2, $3, $4, $5)
            """,
            log_type,
            level,
            guild_id,
            message,
            stacktrace,
        )

    # ------------------------------------------------------------------
    # Security / incidents (self-protection)
    # ------------------------------------------------------------------

    async def add_incident(
        self,
        guild_id: int,
        kind: str,
        severity: str = "high",
        actor_id: Optional[int] = None,
        detail: Optional[Dict[str, Any]] = None,
        consequence: Optional[str] = None,
    ) -> Dict[str, Any]:
        row = await self.fetchrow(
            """
            INSERT INTO incidents (guild_id, kind, severity, actor_id, detail, consequence)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            guild_id,
            kind,
            severity,
            actor_id,
            json.dumps(detail or {}),
            consequence,
        )
        await self.bump_stat("incidents", 1)
        return dict(row)

    async def open_incidents(self, guild_id: Optional[int] = None) -> List[Dict[str, Any]]:
        if guild_id is not None:
            rows = await self.fetch(
                "SELECT * FROM incidents WHERE guild_id = $1 ORDER BY created_at DESC",
                guild_id,
            )
        else:
            rows = await self.fetch("SELECT * FROM incidents ORDER BY created_at DESC")
        return [dict(r) for r in rows]

    async def resolve_open_incidents(self, guild_id: int) -> None:
        await self.execute(
            "UPDATE incidents SET status = 'resolved', resolved_at = now() "
            "WHERE guild_id = $1 AND status = 'open'",
            guild_id,
        )

    # ------------------------------------------------------------------
    # Update announcements
    # ------------------------------------------------------------------

    async def unannounced_updates(self) -> List[Dict[str, Any]]:
        rows = await self.fetch(
            "SELECT * FROM updates WHERE announced = FALSE ORDER BY id ASC"
        )
        return [dict(r) for r in rows]

    async def mark_update_announced(self, update_id: int) -> None:
        await self.execute("UPDATE updates SET announced = TRUE WHERE id = $1", update_id)

    async def active_servers_for_announce(self) -> List[Dict[str, Any]]:
        rows = await self.fetch(
            "SELECT guild_id, language, log_channel_id "
            "FROM servers WHERE status = 'active'"
        )
        return [dict(r) for r in rows]