"""
Tests for HotData infrastructure.

Tests the core HotData protocol for loading and refreshing pre-computed data.
Implements AD-004 (Pre-Computed Richness) verification.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from .. import (
    FIXTURES_DIR,
    DictSerializable,
    HotData,
    HotDataRegistry,
    Serializable,
    get_hotdata_registry,
)

# ─────────────────────────────────────────────────────────────────────────────
# Test Fixtures (the pytest kind)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class MockSnapshot:
    """Mock type implementing DictSerializable."""

    id: str
    name: str
    value: float = 0.0
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MockSnapshot":
        return cls(
            id=data["id"],
            name=data["name"],
            value=data.get("value", 0.0),
            tags=data.get("tags", []),
        )


@dataclass
class MockSerializable:
    """Mock type implementing Serializable directly."""

    content: str
    metadata: dict[str, str] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "content": self.content,
                "metadata": self.metadata,
            },
            indent=2,
        )

    @classmethod
    def from_json(cls, data: str) -> "MockSerializable":
        parsed = json.loads(data)
        return cls(
            content=parsed["content"],
            metadata=parsed.get("metadata", {}),
        )


@pytest.fixture
def tmp_fixtures_dir(tmp_path: Path) -> Path:
    """Create a temporary fixtures directory."""
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    return fixtures


@pytest.fixture
def mock_snapshot() -> MockSnapshot:
    """Create a mock snapshot."""
    return MockSnapshot(
        id="test-001",
        name="Test Agent",
        value=0.75,
        tags=["demo", "test"],
    )


@pytest.fixture
def mock_serializable() -> MockSerializable:
    """Create a mock serializable."""
    return MockSerializable(
        content="Test content",
        metadata={"author": "test", "version": "1.0"},
    )


# ─────────────────────────────────────────────────────────────────────────────
# HotData Basic Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestHotDataBasic:
    """Basic HotData functionality tests."""

    def test_exists_false_for_missing(self, tmp_fixtures_dir: Path) -> None:
        """HotData.exists() returns False for missing files."""
        hd = HotData(
            path=tmp_fixtures_dir / "nonexistent.json",
            schema=MockSnapshot,
        )
        assert not hd.exists()

    def test_exists_true_for_present(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """HotData.exists() returns True for existing files."""
        path = tmp_fixtures_dir / "present.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        hd = HotData(path=path, schema=MockSnapshot)
        assert hd.exists()

    def test_load_dict_serializable(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """HotData.load() works with DictSerializable types."""
        path = tmp_fixtures_dir / "snapshot.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        hd = HotData(path=path, schema=MockSnapshot)
        loaded = hd.load()

        assert loaded.id == mock_snapshot.id
        assert loaded.name == mock_snapshot.name
        assert loaded.value == mock_snapshot.value
        assert loaded.tags == mock_snapshot.tags

    def test_load_serializable(
        self, tmp_fixtures_dir: Path, mock_serializable: MockSerializable
    ) -> None:
        """HotData.load() works with Serializable types."""
        path = tmp_fixtures_dir / "serializable.json"
        path.write_text(mock_serializable.to_json())

        hd = HotData(path=path, schema=MockSerializable)
        loaded = hd.load()

        assert loaded.content == mock_serializable.content
        assert loaded.metadata == mock_serializable.metadata

    def test_load_or_default_returns_loaded(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """load_or_default() returns loaded data when file exists."""
        path = tmp_fixtures_dir / "snapshot.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        hd = HotData(path=path, schema=MockSnapshot)
        default = MockSnapshot(id="default", name="Default")

        loaded = hd.load_or_default(default)
        assert loaded.id == mock_snapshot.id

    def test_load_or_default_returns_default(self, tmp_fixtures_dir: Path) -> None:
        """load_or_default() returns default when file missing."""
        path = tmp_fixtures_dir / "missing.json"
        default = MockSnapshot(id="default", name="Default")

        hd = HotData(path=path, schema=MockSnapshot)
        loaded = hd.load_or_default(default)

        assert loaded.id == "default"
        assert loaded.name == "Default"

    def test_load_missing_raises(self, tmp_fixtures_dir: Path) -> None:
        """HotData.load() raises FileNotFoundError for missing files."""
        hd = HotData(
            path=tmp_fixtures_dir / "nonexistent.json",
            schema=MockSnapshot,
        )
        with pytest.raises(FileNotFoundError):
            hd.load()


# ─────────────────────────────────────────────────────────────────────────────
# HotData TTL Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestHotDataTTL:
    """TTL-based freshness tests."""

    def test_is_fresh_without_ttl(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """Files without TTL are always fresh."""
        path = tmp_fixtures_dir / "snapshot.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        hd = HotData(path=path, schema=MockSnapshot, ttl=None)
        assert hd._is_fresh()

    def test_is_fresh_within_ttl(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """Files within TTL are fresh."""
        path = tmp_fixtures_dir / "snapshot.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        hd = HotData(
            path=path,
            schema=MockSnapshot,
            ttl=timedelta(hours=1),
        )
        assert hd._is_fresh()

    def test_is_stale_outside_ttl(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """Files outside TTL are stale."""
        path = tmp_fixtures_dir / "snapshot.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        # Set mtime to 2 hours ago
        old_mtime = time.time() - 7200
        import os

        os.utime(path, (old_mtime, old_mtime))

        hd = HotData(
            path=path,
            schema=MockSnapshot,
            ttl=timedelta(hours=1),
        )
        assert not hd._is_fresh()

    def test_age_seconds(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """age_seconds() returns correct age."""
        path = tmp_fixtures_dir / "snapshot.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        hd = HotData(path=path, schema=MockSnapshot)
        age = hd.age_seconds()

        assert age is not None
        assert age >= 0
        assert age < 5  # Should be very recent

    def test_age_seconds_missing(self, tmp_fixtures_dir: Path) -> None:
        """age_seconds() returns None for missing files."""
        hd = HotData(
            path=tmp_fixtures_dir / "missing.json",
            schema=MockSnapshot,
        )
        assert hd.age_seconds() is None


# ─────────────────────────────────────────────────────────────────────────────
# HotData Refresh Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestHotDataRefresh:
    """Refresh functionality tests."""

    @pytest.mark.asyncio
    async def test_refresh_creates_file(self, tmp_fixtures_dir: Path) -> None:
        """refresh() creates file when missing."""
        path = tmp_fixtures_dir / "generated.json"
        expected = MockSnapshot(id="generated", name="Generated Agent")

        async def generator() -> MockSnapshot:
            return expected

        hd = HotData(path=path, schema=MockSnapshot)
        result = await hd.refresh(generator)

        assert result.id == expected.id
        assert path.exists()

    @pytest.mark.asyncio
    async def test_refresh_uses_cache_when_fresh(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """refresh() uses cache when data is fresh."""
        path = tmp_fixtures_dir / "cached.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        generator_called = False

        async def generator() -> MockSnapshot:
            nonlocal generator_called
            generator_called = True
            return MockSnapshot(id="new", name="New Agent")

        hd = HotData(path=path, schema=MockSnapshot, ttl=None)
        result = await hd.refresh(generator)

        assert not generator_called
        assert result.id == mock_snapshot.id

    @pytest.mark.asyncio
    async def test_refresh_regenerates_when_stale(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """refresh() regenerates when data is stale."""
        path = tmp_fixtures_dir / "stale.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        # Set mtime to 2 hours ago
        old_mtime = time.time() - 7200
        import os

        os.utime(path, (old_mtime, old_mtime))

        expected = MockSnapshot(id="fresh", name="Fresh Agent")

        async def generator() -> MockSnapshot:
            return expected

        hd = HotData(
            path=path,
            schema=MockSnapshot,
            ttl=timedelta(hours=1),
        )
        result = await hd.refresh(generator)

        assert result.id == expected.id

    @pytest.mark.asyncio
    async def test_refresh_force_regenerates(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """refresh(force=True) regenerates even when fresh."""
        path = tmp_fixtures_dir / "forced.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        expected = MockSnapshot(id="forced", name="Forced Agent")

        async def generator() -> MockSnapshot:
            return expected

        hd = HotData(path=path, schema=MockSnapshot, ttl=None)
        result = await hd.refresh(generator, force=True)

        assert result.id == expected.id


# ─────────────────────────────────────────────────────────────────────────────
# HotDataRegistry Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestHotDataRegistry:
    """Registry tests."""

    def test_register_and_get(self, tmp_fixtures_dir: Path) -> None:
        """Can register and retrieve fixtures."""
        registry = HotDataRegistry()
        hd = HotData(
            path=tmp_fixtures_dir / "test.json",
            schema=MockSnapshot,
        )

        registry.register("test_fixture", hd)
        retrieved = registry.get("test_fixture")

        assert retrieved is hd

    def test_get_unknown_returns_none(self) -> None:
        """get() returns None for unknown fixtures."""
        registry = HotDataRegistry()
        assert registry.get("unknown") is None

    def test_list_all(self, tmp_fixtures_dir: Path) -> None:
        """list_all() returns all registered names."""
        registry = HotDataRegistry()

        registry.register(
            "fixture_a",
            HotData(path=tmp_fixtures_dir / "a.json", schema=MockSnapshot),
        )
        registry.register(
            "fixture_b",
            HotData(path=tmp_fixtures_dir / "b.json", schema=MockSnapshot),
        )

        names = registry.list_all()
        assert set(names) == {"fixture_a", "fixture_b"}

    def test_list_missing(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """list_missing() returns fixtures without files."""
        registry = HotDataRegistry()

        # Create one existing file
        existing_path = tmp_fixtures_dir / "existing.json"
        existing_path.write_text(json.dumps(mock_snapshot.to_dict()))

        registry.register(
            "existing",
            HotData(path=existing_path, schema=MockSnapshot),
        )
        registry.register(
            "missing",
            HotData(path=tmp_fixtures_dir / "missing.json", schema=MockSnapshot),
        )

        missing = registry.list_missing()
        assert missing == ["missing"]

    def test_list_stale(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """list_stale() returns stale fixtures."""
        registry = HotDataRegistry()

        # Create a fresh file
        fresh_path = tmp_fixtures_dir / "fresh.json"
        fresh_path.write_text(json.dumps(mock_snapshot.to_dict()))

        # Create a stale file
        stale_path = tmp_fixtures_dir / "stale.json"
        stale_path.write_text(json.dumps(mock_snapshot.to_dict()))
        old_mtime = time.time() - 7200
        import os

        os.utime(stale_path, (old_mtime, old_mtime))

        registry.register(
            "fresh",
            HotData(path=fresh_path, schema=MockSnapshot, ttl=timedelta(hours=1)),
        )
        registry.register(
            "stale",
            HotData(path=stale_path, schema=MockSnapshot, ttl=timedelta(hours=1)),
        )

        stale = registry.list_stale()
        assert stale == ["stale"]

    def test_get_status(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """get_status() returns detailed fixture info."""
        registry = HotDataRegistry()

        path = tmp_fixtures_dir / "status_test.json"
        path.write_text(json.dumps(mock_snapshot.to_dict()))

        async def gen() -> MockSnapshot:
            return mock_snapshot

        hd = HotData(path=path, schema=MockSnapshot)
        registry.register("test", hd, gen)

        status = registry.get_status("test")
        assert status["exists"] is True
        assert status["fresh"] is True
        assert status["has_generator"] is True
        assert "age_seconds" in status
        assert str(path) == status["path"]

    @pytest.mark.asyncio
    async def test_refresh_specific(self, tmp_fixtures_dir: Path) -> None:
        """Can refresh a specific fixture."""
        registry = HotDataRegistry()

        path = tmp_fixtures_dir / "refresh_test.json"
        expected = MockSnapshot(id="refreshed", name="Refreshed")

        async def gen() -> MockSnapshot:
            return expected

        hd = HotData(path=path, schema=MockSnapshot)
        registry.register("test", hd, gen)

        result = await registry.refresh("test", force=True)
        assert result.id == expected.id

    @pytest.mark.asyncio
    async def test_refresh_without_generator_raises(
        self, tmp_fixtures_dir: Path
    ) -> None:
        """refresh() raises ValueError without generator."""
        registry = HotDataRegistry()

        hd = HotData(
            path=tmp_fixtures_dir / "no_gen.json",
            schema=MockSnapshot,
        )
        registry.register("no_gen", hd)  # No generator

        with pytest.raises(ValueError, match="No generator"):
            await registry.refresh("no_gen")

    @pytest.mark.asyncio
    async def test_refresh_all_stale(
        self, tmp_fixtures_dir: Path, mock_snapshot: MockSnapshot
    ) -> None:
        """refresh_all_stale() refreshes only stale fixtures with generators."""
        registry = HotDataRegistry()

        # Create a stale file
        stale_path = tmp_fixtures_dir / "stale.json"
        stale_path.write_text(json.dumps(mock_snapshot.to_dict()))
        old_mtime = time.time() - 7200
        import os

        os.utime(stale_path, (old_mtime, old_mtime))

        refresh_called = False

        async def gen() -> MockSnapshot:
            nonlocal refresh_called
            refresh_called = True
            return MockSnapshot(id="refreshed", name="Refreshed")

        hd = HotData(path=stale_path, schema=MockSnapshot, ttl=timedelta(hours=1))
        registry.register("stale", hd, gen)

        refreshed = await registry.refresh_all_stale()
        assert refreshed == ["stale"]
        assert refresh_called


# ─────────────────────────────────────────────────────────────────────────────
# Global Registry Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestGlobalRegistry:
    """Global registry singleton tests."""

    def test_get_hotdata_registry_returns_singleton(self) -> None:
        """get_hotdata_registry() returns same instance."""
        r1 = get_hotdata_registry()
        r2 = get_hotdata_registry()
        assert r1 is r2


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestIntegration:
    """Integration tests with real types."""

    def test_fixtures_dir_exists_or_can_be_created(self) -> None:
        """FIXTURES_DIR is a valid path."""
        # Just check that the constant is a Path
        assert isinstance(FIXTURES_DIR, Path)
        # The actual directory may not exist yet in test environment
