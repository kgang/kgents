"""
Ghost Cache Management - Bridge between Glass Terminal and Ghost Infrastructure.

This module provides cache management for the Glass Terminal's offline fallback system.
The Glass Cache lives at ~/.kgents/ghost/ (user's home directory), separate from
the project-level .kgents/ghost/ used by the Ghost Daemon collectors.

The Glass Cache stores:
- Cortex status (from gRPC calls to CortexServicer)
- HoloMap data (from gRPC calls to GetMap)
- Agent states (from gRPC calls to GetAgentStatus)
- Meta information (timestamps, staleness)

AGENTESE Mapping:
    Cache write = self.memory.engram (persist state on successful invocation)
    Cache read = self.memory.manifest (cached last-known-good state)

Design Principles:
    1. Graceful Degradation: Never fail completely
    2. Transparent Infrastructure: Users always know data freshness
    3. Separation: Glass cache is for gRPC fallback, Ghost daemon is for trust loop
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, cast

# The Glass Cache lives in user's home directory (distinct from project .kgents/ghost/)
GLASS_CACHE_DIR = Path.home() / ".kgents" / "ghost"


class GlassCacheManager:
    """
    Manages the Glass Terminal's offline cache.

    The Glass Cache provides offline resilience for the CLI:
    - On successful gRPC calls, data is cached
    - On gRPC failures, cached data is served with [GHOST] prefix
    - Users always see something useful

    This is distinct from the GhostDaemon which handles project-level
    trust loop data collection.

    Usage:
        manager = GlassCacheManager()

        # Write cache entry
        manager.write("status", {"health": "OK", "agents": 5})

        # Read cache entry
        data, age = manager.read("status")
        if data:
            print(f"Cached status from {age.seconds}s ago: {data}")
    """

    def __init__(self, cache_dir: Path | None = None):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Custom cache directory (default: ~/.kgents/ghost/)
        """
        self.cache_dir = cache_dir or GLASS_CACHE_DIR

    def ensure_structure(self) -> None:
        """
        Ensure the cache directory structure exists.

        Structure:
            ~/.kgents/ghost/
            ├── status.json         # Cortex status (self.cortex.manifest)
            ├── map.json            # HoloMap data (world.project.manifest)
            ├── agents/             # Per-agent state (self.agent.{name}.manifest)
            │   ├── d-gent.json
            │   └── l-gent.json
            └── meta.json           # Timestamps, staleness info
        """
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "agents").mkdir(exist_ok=True)

    def write(
        self,
        key: str,
        data: Any,
        agentese_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Write data to the cache.

        Maps to AGENTESE: self.memory.engram

        Args:
            key: Cache key (e.g., "status", "agents/d-gent")
            data: Data to cache (must be JSON-serializable)
            agentese_path: AGENTESE path that produced this data
            metadata: Additional metadata to store
        """
        self.ensure_structure()

        entry = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "agentese_path": agentese_path,
            "metadata": metadata or {},
        }

        # Handle nested keys (e.g., "agents/d-gent")
        if "/" in key:
            parts = key.split("/")
            subdir = self.cache_dir / "/".join(parts[:-1])
            subdir.mkdir(parents=True, exist_ok=True)
            cache_file = subdir / f"{parts[-1]}.json"
        else:
            cache_file = self.cache_dir / f"{key}.json"

        cache_file.write_text(json.dumps(entry, indent=2, default=str))

        # Update meta.json
        self._update_meta(key)

    def read(self, key: str) -> tuple[Any, timedelta | None]:
        """
        Read data from the cache.

        Maps to AGENTESE: self.memory.manifest

        Args:
            key: Cache key to read

        Returns:
            (data, age) or (None, None) if not found
        """
        # Handle nested keys
        if "/" in key:
            parts = key.split("/")
            cache_file = self.cache_dir / "/".join(parts[:-1]) / f"{parts[-1]}.json"
        else:
            cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None, None

        try:
            entry = json.loads(cache_file.read_text())
            timestamp = datetime.fromisoformat(entry["timestamp"])
            age = datetime.now() - timestamp
            return entry["data"], age
        except (json.JSONDecodeError, KeyError, ValueError):
            return None, None

    def exists(self, key: str) -> bool:
        """Check if a cache entry exists."""
        if "/" in key:
            parts = key.split("/")
            cache_file = self.cache_dir / "/".join(parts[:-1]) / f"{parts[-1]}.json"
        else:
            cache_file = self.cache_dir / f"{key}.json"
        return cache_file.exists()

    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.

        Returns:
            True if entry was deleted, False if it didn't exist
        """
        if "/" in key:
            parts = key.split("/")
            cache_file = self.cache_dir / "/".join(parts[:-1]) / f"{parts[-1]}.json"
        else:
            cache_file = self.cache_dir / f"{key}.json"

        if cache_file.exists():
            cache_file.unlink()
            return True
        return False

    def clear(self) -> None:
        """Clear the entire cache."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        self.ensure_structure()

    def get_staleness(self, key: str) -> timedelta | None:
        """
        Get how stale a cache entry is.

        Returns None if entry doesn't exist.
        """
        _, age = self.read(key)
        return age

    def _update_meta(self, key: str) -> None:
        """Update meta.json with latest write info."""
        meta_file = self.cache_dir / "meta.json"

        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
            except (json.JSONDecodeError, ValueError):
                meta = {}
        else:
            meta = {}

        if "last_writes" not in meta:
            meta["last_writes"] = {}
        if "write_counts" not in meta:
            meta["write_counts"] = {}

        now = datetime.now().isoformat()
        meta["last_writes"][key] = now
        meta["last_updated"] = now
        meta["write_counts"][key] = meta["write_counts"].get(key, 0) + 1

        meta_file.write_text(json.dumps(meta, indent=2))

    def get_meta(self) -> dict[str, Any]:
        """Get cache metadata."""
        meta_file = self.cache_dir / "meta.json"
        if not meta_file.exists():
            return {}
        try:
            return cast(dict[str, Any], json.loads(meta_file.read_text()))
        except (json.JSONDecodeError, ValueError):
            return {}

    def get_all_keys(self) -> list[str]:
        """
        Get all cache keys.

        Returns keys including nested ones like "agents/d-gent".
        """
        if not self.cache_dir.exists():
            return []

        keys = []

        # Top-level files
        for file in self.cache_dir.glob("*.json"):
            if file.name != "meta.json":
                keys.append(file.stem)

        # Nested files (e.g., agents/)
        for subdir in self.cache_dir.iterdir():
            if subdir.is_dir():
                for file in subdir.glob("*.json"):
                    keys.append(f"{subdir.name}/{file.stem}")

        return sorted(keys)

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of cache state.

        Useful for debugging and `kgents status --ghost`.
        """
        keys = self.get_all_keys()
        meta = self.get_meta()

        entries = []
        for key in keys:
            data, age = self.read(key)
            if data is not None:
                entries.append(
                    {
                        "key": key,
                        "age_seconds": age.total_seconds() if age else None,
                        "has_data": data is not None,
                    }
                )

        return {
            "cache_dir": str(self.cache_dir),
            "entry_count": len(keys),
            "entries": entries,
            "meta": meta,
        }


# =============================================================================
# Convenience Functions
# =============================================================================


def get_glass_cache() -> GlassCacheManager:
    """Get a GlassCacheManager instance with default configuration."""
    return GlassCacheManager()


def seed_glass_cache(initial_data: dict[str, Any]) -> None:
    """
    Seed the Glass cache with initial data.

    Used by `kgents infra init` after successful infrastructure setup
    to ensure the cache has baseline data.

    Args:
        initial_data: Dict mapping cache keys to data
                      e.g., {"status": {...}, "map": {...}}
    """
    manager = GlassCacheManager()
    for key, data in initial_data.items():
        manager.write(key=key, data=data, agentese_path=f"self.{key}.manifest")


def clear_glass_cache() -> None:
    """Clear the Glass cache entirely."""
    manager = GlassCacheManager()
    manager.clear()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "GlassCacheManager",
    "get_glass_cache",
    "seed_glass_cache",
    "clear_glass_cache",
    "GLASS_CACHE_DIR",
]
