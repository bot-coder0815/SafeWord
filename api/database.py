from datetime import datetime, timedelta, timezone
import json
from typing import Any, Dict, List, Optional

import asyncpg

_SCHEMA = """
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
    bypass_privileged BOOLEAN DEFAULT FALSE,
    std_word_action  TEXT DEFAULT 'delete',
    admin_ok         BOOLEAN DEFAULT TRUE,
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

CREATE TABLE IF NOT EXISTS bot_profile (
    id         INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    avatar     TEXT,
    updated_by BIGINT,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bot_profile_history (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    field      TEXT NOT NULL,
    guild_id   BIGINT,
    updated_by BIGINT,
    value      TEXT,
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

CREATE TABLE IF NOT EXISTS push_subscriptions (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id    BIGINT NOT NULL,
    endpoint   TEXT NOT NULL,
    keys       JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (user_id, endpoint)
);

CREATE INDEX IF NOT EXISTS idx_violations_guild ON violations (guild_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_created ON logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_custom_words_guild ON custom_words (guild_id);
CREATE INDEX IF NOT EXISTS idx_profile_history_created ON bot_profile_history (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_guild ON incidents (guild_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_open ON incidents (pushed, created_at) WHERE status = 'open';
ALTER TABLE updates ADD COLUMN IF NOT EXISTS announced BOOLEAN DEFAULT FALSE;
ALTER TABLE updates ADD COLUMN IF NOT EXISTS kind TEXT DEFAULT 'announce';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS name TEXT DEFAULT '';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS owner_id BIGINT;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'en';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS mod_level INTEGER DEFAULT 3;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS log_channel_id BIGINT;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS action_delete BOOLEAN DEFAULT TRUE;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS action_warn BOOLEAN DEFAULT TRUE;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS action_timeout BOOLEAN DEFAULT TRUE;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS action_log BOOLEAN DEFAULT TRUE;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS timeout_minutes INTEGER DEFAULT 60;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS default_lists JSONB DEFAULT '{"de": true, "en": true}';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS bypass_roles JSONB DEFAULT '[]';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS bypass_users JSONB DEFAULT '[]';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS bypass_privileged BOOLEAN DEFAULT FALSE;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS std_word_action TEXT DEFAULT 'delete';
ALTER TABLE servers ADD COLUMN IF NOT EXISTS admin_ok BOOLEAN DEFAULT TRUE;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS bot_version TEXT;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS member_count INTEGER DEFAULT 0;
ALTER TABLE servers ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE servers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

CREATE TABLE IF NOT EXISTS invites (
    guild_id   BIGINT PRIMARY KEY,
    code       TEXT NOT NULL,
    url        TEXT NOT NULL,
    channel_id BIGINT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS team_members (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    role       TEXT NOT NULL DEFAULT '',
    parent_id  INTEGER REFERENCES team_members(id) ON DELETE SET NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS standard_word_overrides (
    guild_id    BIGINT NOT NULL,
    word        TEXT NOT NULL,
    action      TEXT,
    enabled     BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (guild_id, word)
);

CREATE TABLE IF NOT EXISTS bot_heartbeat (
    id        INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    last_seen TIMESTAMPTZ DEFAULT now()
);
INSERT INTO bot_heartbeat (id, last_seen) VALUES (1, now())
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS monitor_settings (
    id              SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    muted           BOOLEAN NOT NULL DEFAULT FALSE,
    down_since      TIMESTAMPTZ,
    last_notified   TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT now()
);
INSERT INTO monitor_settings (id, muted)
VALUES (1, FALSE)
ON CONFLICT (id) DO NOTHING;
"""


class Database:
    def __init__(self, dsn: str):
        self._dsn = dsn
        self._pool: Optional[asyncpg.Pool] = None

    @staticmethod
    async def _init_conn(conn: asyncpg.Connection) -> None:
        await conn.set_type_codec(
            "jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
        )
        await conn.set_type_codec(
            "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
        )

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(
            self._dsn, min_size=1, max_size=10, init=self._init_conn
        )
        async with self._pool.acquire() as conn:
            await conn.execute(_SCHEMA)
            count = await conn.fetchval("SELECT COUNT(*) FROM team_members")
            if count == 0:
                await conn.execute(
                    "INSERT INTO team_members (name, role, sort_order) "
                    "VALUES ('DevCoder', 'Owner/Head developer', 0)"
                )
    async def close(self) -> None:
        if self._pool:
            await self._pool.close()

    async def _fetchrow(self, q: str, *a: Any) -> Optional[dict]:
        async with self._pool.acquire() as c:
            r = await c.fetchrow(q, *a)
            return dict(r) if r else None

    async def _fetch(self, q: str, *a: Any) -> List[dict]:
        async with self._pool.acquire() as c:
            rows = await c.fetch(q, *a)
            return [dict(r) for r in rows]

    async def _execute(self, q: str, *a: Any) -> Any:
        async with self._pool.acquire() as c:
            return await c.execute(q, *a)

    async def _fetchval(self, q: str, *a: Any) -> Any:
        async with self._pool.acquire() as c:
            return await c.fetchval(q, *a)

    # -- users -----------------------------------------------------------

    async def get_user(self, discord_id: int) -> Optional[dict]:
        return await self._fetchrow("SELECT * FROM users WHERE discord_id = $1", discord_id)

    async def upsert_user(
        self,
        discord_id: int,
        username: str,
        access_token: str,
        refresh_token: Optional[str],
    ) -> dict:
        await self._execute(
            """
            INSERT INTO users (discord_id, username, access_token, refresh_token)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (discord_id) DO UPDATE SET
                username = EXCLUDED.username,
                access_token = EXCLUDED.access_token,
                refresh_token = COALESCE(EXCLUDED.refresh_token, users.refresh_token),
                updated_at = now()
            """,
            discord_id,
            username,
            access_token,
            refresh_token,
        )
        return await self.get_user(discord_id)

    async def set_user_role(self, discord_id: int, role: str) -> None:
        await self._execute(
            "UPDATE users SET role = $2, updated_at = now() WHERE discord_id = $1",
            discord_id,
            role,
        )

    async def list_developers(self) -> List[dict]:
        return await self._fetch(
            "SELECT * FROM users WHERE role IN ('owner','developer','moderator') ORDER BY role"
        )

    # -- servers ---------------------------------------------------------

    async def get_server(self, guild_id: int) -> Optional[dict]:
        return await self._fetchrow("SELECT * FROM servers WHERE guild_id = $1", guild_id)

    async def update_server(self, guild_id: int, **fields: Any) -> None:
        if not fields:
            return
        cols = ", ".join(f"{k} = ${i + 1}" for i, k in enumerate(fields))
        await self._execute(
            f"UPDATE servers SET {cols}, updated_at = now() WHERE guild_id = ${len(fields) + 1}",
            *fields.values(),
            guild_id,
        )

    async def all_servers(self) -> List[dict]:
        return await self._fetch("SELECT * FROM servers ORDER BY created_at ASC")

    async def server_count(self) -> int:
        return int(await self._fetchval("SELECT COUNT(*) FROM servers"))

    async def active_server_count(self) -> int:
        return int(
            await self._fetchval("SELECT COUNT(*) FROM servers WHERE status = 'active'")
        )

    # -- custom words ----------------------------------------------------

    async def get_custom_words(self, guild_id: int, enabled_only: bool = True) -> List[dict]:
        q = "SELECT * FROM custom_words WHERE guild_id = $1"
        if enabled_only:
            q += " AND enabled = TRUE"
        return await self._fetch(q + " ORDER BY created_at ASC", guild_id)

    async def add_custom_word(
        self, guild_id: int, word: str, category: str, severity: int, action: str
    ) -> bool:
        try:
            await self._execute(
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
        res = await self._execute(
            "DELETE FROM custom_words WHERE guild_id = $1 AND word = $2", guild_id, word
        )
        return res.endswith(" 1")

    async def set_custom_word_enabled(self, guild_id: int, word: str, enabled: bool) -> None:
        await self._execute(
            "UPDATE custom_words SET enabled = $3 WHERE guild_id = $1 AND word = $2",
            guild_id,
            word,
            enabled,
        )

    # -- standard word overrides ------------------------------------------

    async def get_word_overrides(self, guild_id: int) -> List[dict]:
        return await self._fetch(
            "SELECT * FROM standard_word_overrides WHERE guild_id = $1", guild_id
        )

    async def set_word_override(
        self,
        guild_id: int,
        word: str,
        action: Optional[str],
        enabled: bool = True,
    ) -> None:
        await self._execute(
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
        res = await self._execute(
            "DELETE FROM standard_word_overrides WHERE guild_id = $1 AND word = $2",
            guild_id,
            word,
        )
        return res.endswith(" 1")

    # -- violations / stats ----------------------------------------------

    async def violations_today(self) -> int:
        return int(
            await self._fetchval(
                "SELECT COUNT(*) FROM violations WHERE created_at >= CURRENT_DATE"
            )
        )

    async def violations_total(self) -> int:
        return int(await self._fetchval("SELECT COUNT(*) FROM violations"))

    async def violations_series(self, guild_id: Optional[int] = None, days: int = 30) -> List[dict]:
        base = "WHERE created_at >= CURRENT_DATE - $1::int"
        args: list[Any] = [days]
        if guild_id:
            base += " AND guild_id = $2"
            args.append(guild_id)
        return await self._fetch(
            f"SELECT created_at::date AS day, COUNT(*) AS value "
            f"FROM violations {base} GROUP BY day ORDER BY day",
            *args,
        )

    async def violations_top_words(self, guild_id: Optional[int] = None, limit: int = 10) -> List[dict]:
        base = ""
        args: list[Any] = [limit]
        if guild_id:
            base = "WHERE guild_id = $2 "
            args.append(guild_id)
        return await self._fetch(
            f"SELECT matched_word, COUNT(*) AS count FROM violations "
            f"{base}GROUP BY matched_word ORDER BY count DESC LIMIT $1",
            *args,
        )

    async def action_counts(self, guild_id: Optional[int] = None) -> List[dict]:
        base = ""
        args: list[Any] = []
        if guild_id:
            base = "WHERE guild_id = $1 "
            args.append(guild_id)
        return await self._fetch(
            f"SELECT action, COUNT(*) AS count FROM violations {base}GROUP BY action ORDER BY count DESC",
            *args,
        )

    async def guild_violation_counts(self) -> List[dict]:
        return await self._fetch(
            "SELECT guild_id, COUNT(*) AS count FROM violations GROUP BY guild_id ORDER BY count DESC"
        )

    async def active_users(self) -> int:
        return int(
            await self._fetchval("SELECT COUNT(DISTINCT user_id) FROM violations")
        )

    async def server_growth(self, days: int = 30) -> List[dict]:
        return await self._fetch(
            "SELECT created_at::date AS day, COUNT(*) AS value FROM servers "
            "WHERE created_at >= CURRENT_DATE - $1::int GROUP BY day ORDER BY day",
            days,
        )

    # -- updates ---------------------------------------------------------

    async def list_updates(self, limit: int = 20) -> List[dict]:
        return await self._fetch("SELECT * FROM updates ORDER BY date DESC LIMIT $1", limit)

    async def add_update(
        self,
        version: str,
        title: str,
        changelog: Optional[str],
        maintenance_mode: bool = False,
        kind: str = "announce",
    ) -> dict:
        row = await self._fetchrow(
            """
            INSERT INTO updates (version, title, changelog, maintenance_mode, kind)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING *
            """,
            version,
            title,
            changelog,
            maintenance_mode,
            kind,
        )
        return row

    async def maintenance_mode(self) -> bool:
        row = await self._fetchrow(
            "SELECT maintenance_mode FROM updates ORDER BY date DESC LIMIT 1"
        )
        return bool(row and row["maintenance_mode"])

    # -- logs ------------------------------------------------------------

    async def add_log(
        self,
        log_type: str,
        message: str,
        level: str = "info",
        guild_id: Optional[int] = None,
        stacktrace: Optional[str] = None,
    ) -> None:
        await self._execute(
            "INSERT INTO logs (type, level, guild_id, message, stacktrace) VALUES ($1,$2,$3,$4,$5)",
            log_type,
            level,
            guild_id,
            message,
            stacktrace,
        )

    async def get_logs(
        self,
        level: Optional[str] = None,
        log_type: Optional[str] = None,
        guild_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[dict]:
        clauses: list[str] = []
        args: list[Any] = []
        if level:
            args.append(level)
            clauses.append(f"level = ${len(args)}")
        if log_type:
            args.append(log_type)
            clauses.append(f"type = ${len(args)}")
        if guild_id:
            args.append(guild_id)
            clauses.append(f"guild_id = ${len(args)}")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        args.append(limit)
        return await self._fetch(
            f"SELECT * FROM logs {where} ORDER BY created_at DESC LIMIT ${len(args)}", *args
        )

    async def error_count(self) -> int:
        return int(
            await self._fetchval(
                "SELECT COUNT(*) FROM logs WHERE level IN ('error','critical')"
            )
        )

    # -- bot profile ------------------------------------------------------

    async def get_bot_profile(self) -> Optional[dict]:
        return await self._fetchrow("SELECT * FROM bot_profile WHERE id = 1")

    async def save_bot_profile(self, fields: Dict[str, Any], updated_by: int) -> dict:
        """Upsert the singleton bot profile row. Values that are None clear a field."""
        if not fields:
            return await self.get_bot_profile()
        existing = await self.get_bot_profile()
        if existing:
            cols = ", ".join(f"{k} = ${i + 1}" for i, k in enumerate(fields))
            await self._execute(
                f"UPDATE bot_profile SET {cols}, updated_by = ${len(fields) + 1}, "
                f"updated_at = now() WHERE id = 1",
                *fields.values(),
                updated_by,
            )
        else:
            cols = ", ".join(["id", *fields.keys(), "updated_by"])
            placeholders = ", ".join(
                [f"${i + 1}" for i in range(len(fields) + 1)]
            )
            await self._execute(
                f"INSERT INTO bot_profile ({cols}) VALUES (1, {placeholders})",
                *fields.values(),
                updated_by,
            )
        return await self.get_bot_profile()

    async def add_profile_history(
        self,
        field: str,
        updated_by: int,
        guild_id: Optional[int] = None,
        value: Optional[str] = None,
    ) -> None:
        await self._execute(
            "INSERT INTO bot_profile_history (field, guild_id, updated_by, value) "
            "VALUES ($1, $2, $3, $4)",
            field,
            guild_id,
            updated_by,
            value,
        )

    async def get_profile_history(self, limit: int = 50) -> List[dict]:
        return await self._fetch(
            "SELECT * FROM bot_profile_history ORDER BY created_at DESC LIMIT $1", limit
        )

    # -- security / incidents --------------------------------------------

    async def list_incidents(
        self, limit: int = 100, guild_id: Optional[int] = None, status: Optional[str] = None
    ) -> List[dict]:
        clauses: list[str] = []
        args: list[Any] = []
        if guild_id:
            args.append(guild_id)
            clauses.append(f"guild_id = ${len(args)}")
        if status:
            args.append(status)
            clauses.append(f"status = ${len(args)}")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        args.append(limit)
        return await self._fetch(
            f"SELECT * FROM incidents {where} ORDER BY created_at DESC LIMIT ${len(args)}",
            *args,
        )

    async def get_incident(self, incident_id: int) -> Optional[dict]:
        return await self._fetchrow("SELECT * FROM incidents WHERE id = $1", incident_id)

    async def open_incident_count(self) -> int:
        return int(
            await self._fetchval("SELECT COUNT(*) FROM incidents WHERE status = 'open'")
        )

    async def resolve_incident(self, incident_id: int) -> bool:
        res = await self._execute(
            "UPDATE incidents SET status = 'resolved', resolved_at = now() WHERE id = $1",
            incident_id,
        )
        return res.endswith(" 1")

    async def resolve_open_incidents(self, guild_id: int) -> int:
        res = await self._execute(
            "UPDATE incidents SET status = 'resolved', resolved_at = now() "
            "WHERE guild_id = $1 AND status = 'open'",
            guild_id,
        )
        try:
            return int(res.split()[-1])
        except (ValueError, IndexError):
            return 0

    async def unprocessed_incidents(self, limit: int = 50) -> List[dict]:
        return await self._fetch(
            "SELECT * FROM incidents WHERE status = 'open' AND pushed = FALSE "
            "ORDER BY created_at ASC LIMIT $1",
            limit,
        )

    async def mark_incident_pushed(self, incident_id: int) -> None:
        await self._execute(
            "UPDATE incidents SET pushed = TRUE WHERE id = $1", incident_id
        )

    # -- push subscriptions ----------------------------------------------

    async def upsert_push_subscription(
        self, user_id: int, endpoint: str, keys: Dict[str, Any]
    ) -> None:
        await self._execute(
            """
            INSERT INTO push_subscriptions (user_id, endpoint, keys)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, endpoint) DO UPDATE SET
                keys = EXCLUDED.keys,
                updated_at = now()
            """,
            user_id,
            endpoint,
            json.dumps(keys),
        )

    async def all_push_subscriptions(self) -> List[dict]:
        return await self._fetch("SELECT * FROM push_subscriptions")

    async def push_subscriptions_for_user(self, user_id: int) -> List[dict]:
        return await self._fetch(
            "SELECT * FROM push_subscriptions WHERE user_id = $1", user_id
        )

    async def admin_push_subscriptions(self) -> List[dict]:
        """All push subscriptions belonging to WordLock staff (owner/developer/moderator)."""
        return await self._fetch(
            "SELECT ps.* FROM push_subscriptions ps "
            "JOIN users u ON u.discord_id = ps.user_id "
            "WHERE u.role IN ('owner', 'developer', 'moderator')"
        )

    async def remove_push_subscription(self, user_id: int, endpoint: str) -> None:
        await self._execute(
            "DELETE FROM push_subscriptions WHERE user_id = $1 AND endpoint = $2",
            user_id,
            endpoint,
        )

    # -- invites ----------------------------------------------------------

    async def get_invite(self, guild_id: int) -> Optional[dict]:
        return await self._fetchrow("SELECT * FROM invites WHERE guild_id = $1", guild_id)

    async def delete_invite(self, guild_id: int) -> None:
        await self._execute("DELETE FROM invites WHERE guild_id = $1", guild_id)

    async def save_invite(
        self,
        guild_id: int,
        code: str,
        url: str,
        channel_id: Optional[int],
        expires_at: datetime,
    ) -> dict:
        await self._execute(
            """
            INSERT INTO invites (guild_id, code, url, channel_id, expires_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (guild_id) DO UPDATE SET
                code = EXCLUDED.code,
                url = EXCLUDED.url,
                channel_id = EXCLUDED.channel_id,
                expires_at = EXCLUDED.expires_at,
                created_at = now()
            """,
            guild_id,
            code,
            url,
            channel_id,
            expires_at,
        )
        return await self.get_invite(guild_id)

    # -- team -------------------------------------------------------------

    async def list_team(self) -> List[dict]:
        return await self._fetch("SELECT * FROM team_members ORDER BY sort_order, id")

    async def add_team_member(
        self, name: str, role: str, parent_id: Optional[int], sort_order: int
    ) -> Optional[dict]:
        return await self._fetchrow(
            "INSERT INTO team_members (name, role, parent_id, sort_order) "
            "VALUES ($1, $2, $3, $4) RETURNING *",
            name,
            role,
            parent_id,
            sort_order,
        )

    async def update_team_member(self, member_id: int, **fields: Any) -> Optional[dict]:
        if not fields:
            return await self._fetchrow(
                "SELECT * FROM team_members WHERE id = $1", member_id
            )
        cols = ", ".join(f"{k} = ${i + 1}" for i, k in enumerate(fields))
        await self._execute(
            f"UPDATE team_members SET {cols} WHERE id = ${len(fields) + 1}",
            *fields.values(),
            member_id,
        )
        return await self._fetchrow("SELECT * FROM team_members WHERE id = $1", member_id)

    async def delete_team_member(self, member_id: int) -> bool:
        res = await self._execute(
            "DELETE FROM team_members WHERE id = $1", member_id
        )
        return res.endswith(" 1")

    # -- heartbeat ---------------------------------------------------------

    async def update_heartbeat(self) -> None:
        await self._execute(
            "INSERT INTO bot_heartbeat (id, last_seen) VALUES (1, now()) "
            "ON CONFLICT (id) DO UPDATE SET last_seen = now()"
        )

    async def last_heartbeat(self) -> Optional[float]:
        row = await self._fetchrow(
            "SELECT EXTRACT(EPOCH FROM last_seen)::float AS ts FROM bot_heartbeat WHERE id = 1"
        )
        return row["ts"] if row else None

    # -- monitor settings (downtime alerts) --------------------------------

    async def get_monitor_settings(self) -> dict:
        row = await self._fetchrow("SELECT * FROM monitor_settings WHERE id = 1")
        return row or {"muted": False, "down_since": None, "last_notified": None}

    async def set_monitor_muted(self, muted: bool) -> None:
        await self._execute(
            "UPDATE monitor_settings SET muted = $1, updated_at = now() WHERE id = 1",
            muted,
        )

    async def set_monitor_state(
        self, down_since: Optional[float], last_notified: Optional[float]
    ) -> None:
        await self._execute(
            "UPDATE monitor_settings "
            "SET down_since = CASE WHEN $1::float IS NULL THEN NULL "
            "   ELSE to_timestamp($1) END, "
            "last_notified = CASE WHEN $2::float IS NULL THEN NULL "
            "   ELSE to_timestamp($2) END, "
            "updated_at = now() "
            "WHERE id = 1",
            down_since,
            last_notified,
        )
