"""
HotData: Pre-Computed Richness Infrastructure.

Philosophy: LLM-once is cheap. Pre-compute rich data, hotload forever.
Demo kgents ARE kgents.

Implements AD-004 (Pre-Computed Richness) from spec/principles.md.

The Three Truths:
1. Demo kgents ARE kgents: No distinction between "demo" and "real"
2. LLM-once is cheap: One LLM call for fixture generation is negligible
3. Hotload everything: Pre-computed outputs swap at runtime for velocity
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Protocol,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class Serializable(Protocol):
    """
    Protocol for types that can be serialized to/from JSON.

    Implementors must provide:
    - to_json() -> str: Serialize to JSON string
    - from_json(cls, data: str) -> Self: Deserialize from JSON string
    """

    def to_json(self) -> str:
        """Serialize to JSON string."""
        ...

    @classmethod
    def from_json(cls, data: str) -> "Serializable":
        """Deserialize from JSON string."""
        ...


@runtime_checkable
class DictSerializable(Protocol):
    """
    Protocol for types that serialize via dict intermediary.

    Many existing types use to_dict/from_dict. This protocol bridges them.
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict."""
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DictSerializable":
        """Create from dict."""
        ...


def dict_to_json(obj: DictSerializable) -> str:
    """Convert DictSerializable to JSON string."""
    return json.dumps(obj.to_dict(), indent=2)


def json_to_dict(cls: type[T], data: str) -> T:
    """Create DictSerializable from JSON string."""
    return cls.from_dict(json.loads(data))  # type: ignore[attr-defined, no-any-return]


@dataclass
class HotData(Generic[T]):
    """
    Hotloadable pre-computed data with optional refresh.

    Philosophy: LLM-once is cheap. Pre-compute rich data, hotload forever.
    Demo kgents ARE kgents.

    Usage:
        # Define a hotdata source
        DEMO_SNAPSHOT = HotData(
            path=FIXTURES_DIR / "agent_snapshots" / "demo.json",
            schema=AgentSnapshot,
        )

        # Load (fast - from file)
        snapshot = DEMO_SNAPSHOT.load()

        # Load with fallback
        snapshot = DEMO_SNAPSHOT.load_or_default(default_snapshot)

        # Refresh via LLM (expensive - only when stale)
        snapshot = await DEMO_SNAPSHOT.refresh(generate_snapshot)

    Attributes:
        path: Path to the JSON file storing pre-computed data
        schema: Type that implements DictSerializable or Serializable
        ttl: Time-to-live for freshness checking. None = forever valid.
    """

    path: Path
    schema: type[T]
    ttl: timedelta | None = None

    def exists(self) -> bool:
        """Check if pre-computed data exists."""
        return self.path.exists()

    def load(self) -> T:
        """
        Load from pre-computed file.

        Raises:
            FileNotFoundError: If fixture doesn't exist
            json.JSONDecodeError: If fixture is malformed
        """
        data = self.path.read_text()

        # Check if schema implements Serializable directly
        if hasattr(self.schema, "from_json"):
            return self.schema.from_json(data)  # type: ignore[attr-defined, no-any-return]

        # Fallback to DictSerializable pattern
        if hasattr(self.schema, "from_dict"):
            return json_to_dict(self.schema, data)

        # Last resort: assume it's a raw JSON-compatible type
        result: T = json.loads(data)
        return result

    def load_or_default(self, default: T) -> T:
        """
        Load from file, or return default if not available.

        This is the preferred pattern for graceful degradation.
        """
        if not self.exists():
            return default
        try:
            return self.load()
        except (json.JSONDecodeError, KeyError, TypeError):
            return default

    async def refresh(
        self,
        generator: Callable[[], Awaitable[T]],
        force: bool = False,
    ) -> T:
        """
        Regenerate via generator if stale or missing.

        The generator is typically an LLM call. It runs once to produce
        rich data, which is then cached.

        Args:
            generator: Async function that produces fresh data
            force: If True, regenerate even if fresh

        Returns:
            The data (either loaded or freshly generated)
        """
        if not force and self._is_fresh():
            return self.load()

        result = await generator()
        self._save(result)
        return result

    def _is_fresh(self) -> bool:
        """Check if data is within TTL."""
        if not self.exists():
            return False
        if self.ttl is None:
            return True  # Forever valid

        mtime = self.path.stat().st_mtime
        age = time.time() - mtime
        return age < self.ttl.total_seconds()

    def _save(self, data: T) -> None:
        """Save data to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Check if data implements Serializable directly
        if hasattr(data, "to_json"):
            self.path.write_text(data.to_json())
            return

        # Fallback to DictSerializable pattern
        if hasattr(data, "to_dict"):
            self.path.write_text(dict_to_json(data))  # type: ignore[arg-type]
            return

        # Last resort: assume it's a raw JSON-compatible type
        self.path.write_text(json.dumps(data, indent=2))

    def age_seconds(self) -> float | None:
        """Get the age of the fixture in seconds, or None if missing."""
        if not self.exists():
            return None
        return time.time() - self.path.stat().st_mtime


@dataclass
class HotDataRegistry:
    """
    Registry of all hotloadable fixtures.

    Allows bulk refresh, validation, and CLI integration.
    Implements the singleton pattern for global fixture tracking.

    Usage:
        registry = HotDataRegistry()
        registry.register("demo_snapshot", DEMO_SNAPSHOT)

        # List all stale fixtures
        stale = registry.list_stale()

        # Refresh all stale fixtures
        await registry.refresh_all_stale(generators)
    """

    _fixtures: dict[str, HotData[Any]] = field(default_factory=dict)
    _generators: dict[str, Callable[[], Awaitable[Any]]] = field(default_factory=dict)

    def register(
        self,
        name: str,
        hotdata: HotData[Any],
        generator: Callable[[], Awaitable[Any]] | None = None,
    ) -> None:
        """
        Register a fixture by name.

        Args:
            name: Unique identifier for the fixture (e.g., "demo_snapshot")
            hotdata: HotData instance pointing to the fixture file
            generator: Optional async function to regenerate the fixture
        """
        self._fixtures[name] = hotdata
        if generator is not None:
            self._generators[name] = generator

    def get(self, name: str) -> HotData[Any] | None:
        """Get a fixture by name."""
        return self._fixtures.get(name)

    def list_all(self) -> list[str]:
        """List all registered fixture names."""
        return list(self._fixtures.keys())

    def list_stale(self) -> list[str]:
        """List all stale fixtures that need refresh."""
        return [name for name, hd in self._fixtures.items() if not hd._is_fresh()]

    def list_missing(self) -> list[str]:
        """List all fixtures that don't exist yet."""
        return [name for name, hd in self._fixtures.items() if not hd.exists()]

    def get_status(self, name: str) -> dict[str, Any]:
        """
        Get detailed status for a fixture.

        Returns dict with:
        - exists: bool
        - fresh: bool
        - age_seconds: float | None
        - path: str
        - has_generator: bool
        """
        hd = self._fixtures.get(name)
        if hd is None:
            return {"error": f"Unknown fixture: {name}"}

        return {
            "exists": hd.exists(),
            "fresh": hd._is_fresh(),
            "age_seconds": hd.age_seconds(),
            "path": str(hd.path),
            "has_generator": name in self._generators,
        }

    async def refresh(self, name: str, force: bool = False) -> Any:
        """
        Refresh a specific fixture.

        Args:
            name: Fixture name
            force: Force refresh even if fresh

        Raises:
            ValueError: If fixture or generator not found
        """
        hd = self._fixtures.get(name)
        if hd is None:
            raise ValueError(f"Unknown fixture: {name}")

        generator = self._generators.get(name)
        if generator is None:
            raise ValueError(f"No generator registered for: {name}")

        return await hd.refresh(generator, force=force)

    async def refresh_all_stale(self) -> list[str]:
        """
        Refresh all stale fixtures that have generators.

        Returns:
            List of fixture names that were refreshed
        """
        refreshed = []
        for name in self.list_stale():
            if name in self._generators:
                await self.refresh(name)
                refreshed.append(name)
        return refreshed


# Global registry singleton
_global_registry: HotDataRegistry | None = None


def get_hotdata_registry() -> HotDataRegistry:
    """Get the global HotData registry singleton."""
    global _global_registry
    if _global_registry is None:
        _global_registry = HotDataRegistry()
    return _global_registry


def register_hotdata(
    name: str,
    hotdata: HotData[Any],
    generator: Callable[[], Awaitable[Any]] | None = None,
) -> None:
    """Convenience function to register with global registry."""
    get_hotdata_registry().register(name, hotdata, generator)


# Fixtures directory constant
FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


__all__ = [
    "HotData",
    "HotDataRegistry",
    "Serializable",
    "DictSerializable",
    "dict_to_json",
    "json_to_dict",
    "get_hotdata_registry",
    "register_hotdata",
    "FIXTURES_DIR",
]
