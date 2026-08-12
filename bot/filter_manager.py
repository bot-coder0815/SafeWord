"""Per-guild compiled filters, cached and rebuilt on config changes."""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

from .database import Database
from .filter_engine import FilterEngine, WordEntry

ACTIONS = ("delete", "warn", "timeout", "log")


class FilterManager:
    """Caches a compiled FilterEngine per guild."""

    def __init__(self, db: Database):
        self.db = db
        self._cache: Dict[int, FilterEngine] = {}
        self._lock = threading.RLock()

    async def build(self, guild_id: int) -> FilterEngine:
        server = await self.db.get_server(guild_id) or {}
        default_lists = server.get("default_lists") or {"de": True, "en": True}
        if isinstance(default_lists, str):
            import json

            default_lists = json.loads(default_lists)
        languages = [lang for lang, active in default_lists.items() if active]

        custom = await self.db.get_custom_words(guild_id, enabled_only=True)
        custom_entries: List[WordEntry] = [
            WordEntry(
                word=row["word"],
                category=row.get("category") or "custom",
                severity=row.get("severity") or 3,
                description="Custom word added by server admin",
                source=f"guild_{guild_id}",
                custom=True,
                action=row.get("action") or "delete",
            )
            for row in custom
        ]

        engine = FilterEngine(default_languages=languages or ("en",))
        overrides = await self.db.get_word_overrides(guild_id)
        override_map = {o["word"]: o for o in overrides}
        engine.reload(custom_entries=custom_entries)
        engine.apply_overrides(override_map)
        return engine

    def get(self, guild_id: int) -> Optional[FilterEngine]:
        with self._lock:
            return self._cache.get(guild_id)

    async def get_or_load(self, guild_id: int) -> FilterEngine:
        with self._lock:
            engine = self._cache.get(guild_id)
        if engine is not None:
            return engine
        engine = await self.build(guild_id)
        self.store(guild_id, engine)
        return engine

    def store(self, guild_id: int, engine: FilterEngine) -> None:
        with self._lock:
            self._cache[guild_id] = engine

    async def rebuild(self, guild_id: int) -> FilterEngine:
        engine = await self.build(guild_id)
        self.store(guild_id, engine)
        return engine

    def invalidate(self, guild_id: int) -> None:
        with self._lock:
            self._cache.pop(guild_id, None)
