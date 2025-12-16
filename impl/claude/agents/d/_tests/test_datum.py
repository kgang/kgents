"""
Tests for Datum dataclass.

Tests verify:
1. Datum creation and serialization
2. Content-addressed IDs
3. Causal linking with derive()
4. JSON/JSONL roundtrip
"""

from __future__ import annotations

import json
import time

import pytest

from ..datum import Datum


class TestDatumCreation:
    """Tests for Datum creation patterns."""

    def test_create_with_auto_id(self) -> None:
        """create() generates unique IDs by default."""
        d1 = Datum.create(b"hello")
        d2 = Datum.create(b"hello")

        assert d1.id != d2.id
        assert len(d1.id) == 32  # UUID hex

    def test_create_with_explicit_id(self) -> None:
        """create() accepts explicit ID."""
        d = Datum.create(b"test", id="my-custom-id")
        assert d.id == "my-custom-id"

    def test_create_content_addressed(self) -> None:
        """create() with content_addressed=True uses SHA-256."""
        d1 = Datum.create(b"hello", content_addressed=True)
        d2 = Datum.create(b"hello", content_addressed=True)

        assert d1.id == d2.id  # Same content = same ID
        assert len(d1.id) == 64  # SHA-256 hex

    def test_create_sets_timestamp(self) -> None:
        """create() sets created_at to current time."""
        before = time.time()
        d = Datum.create(b"test")
        after = time.time()

        assert before <= d.created_at <= after

    def test_create_with_causal_parent(self) -> None:
        """create() accepts causal_parent."""
        parent = Datum.create(b"parent")
        child = Datum.create(b"child", causal_parent=parent.id)

        assert child.causal_parent == parent.id

    def test_create_with_metadata(self) -> None:
        """create() accepts metadata."""
        d = Datum.create(b"test", metadata={"type": "test", "source": "unit"})

        assert d.metadata == {"type": "test", "source": "unit"}


class TestDatumDerivation:
    """Tests for derive() causal linking."""

    def test_derive_links_parent(self) -> None:
        """derive() sets causal_parent to parent ID."""
        parent = Datum.create(b"parent")
        child = parent.derive(b"child")

        assert child.causal_parent == parent.id

    def test_derive_preserves_metadata(self) -> None:
        """derive() can set new metadata."""
        parent = Datum.create(b"parent", metadata={"v": "1"})
        child = parent.derive(b"child", metadata={"v": "2"})

        assert child.metadata == {"v": "2"}

    def test_derive_chain(self) -> None:
        """derive() supports chained derivation."""
        a = Datum.create(b"a")
        b = a.derive(b"b")
        c = b.derive(b"c")

        assert b.causal_parent == a.id
        assert c.causal_parent == b.id


class TestDatumWithMetadata:
    """Tests for with_metadata() immutable update."""

    def test_with_metadata_adds_keys(self) -> None:
        """with_metadata() adds new keys."""
        d = Datum.create(b"test", metadata={"a": "1"})
        d2 = d.with_metadata(b="2", c="3")

        assert d2.metadata == {"a": "1", "b": "2", "c": "3"}
        assert d.metadata == {"a": "1"}  # Original unchanged

    def test_with_metadata_overwrites_keys(self) -> None:
        """with_metadata() overwrites existing keys."""
        d = Datum.create(b"test", metadata={"a": "1"})
        d2 = d.with_metadata(a="updated")

        assert d2.metadata == {"a": "updated"}


class TestDatumSerialization:
    """Tests for JSON/JSONL serialization."""

    def test_to_json_roundtrip(self) -> None:
        """to_json() / from_json() roundtrips correctly."""
        original = Datum.create(
            b"hello world",
            causal_parent="parent-123",
            metadata={"type": "test"},
        )

        json_data = original.to_json()
        restored = Datum.from_json(json_data)

        assert restored.id == original.id
        assert restored.content == original.content
        assert restored.created_at == original.created_at
        assert restored.causal_parent == original.causal_parent
        assert restored.metadata == original.metadata

    def test_to_jsonl_line_is_valid_json(self) -> None:
        """to_jsonl_line() produces valid JSON."""
        d = Datum.create(b"test")
        line = d.to_jsonl_line()

        # Should be valid JSON
        parsed = json.loads(line)
        assert parsed["id"] == d.id

    def test_from_jsonl_line_roundtrip(self) -> None:
        """to_jsonl_line() / from_jsonl_line() roundtrips correctly."""
        original = Datum.create(b"test data", metadata={"key": "value"})
        line = original.to_jsonl_line()
        restored = Datum.from_jsonl_line(line)

        assert restored.id == original.id
        assert restored.content == original.content

    def test_json_handles_binary_content(self) -> None:
        """JSON serialization handles arbitrary binary content."""
        # Binary with non-UTF8 bytes
        binary_content = bytes([0, 1, 2, 255, 254, 253])
        d = Datum.create(binary_content)

        json_data = d.to_json()
        restored = Datum.from_json(json_data)

        assert restored.content == binary_content


class TestDatumProperties:
    """Tests for Datum properties."""

    def test_size_property(self) -> None:
        """size returns content length in bytes."""
        d = Datum.create(b"hello")
        assert d.size == 5

    def test_size_empty_content(self) -> None:
        """size handles empty content."""
        d = Datum.create(b"")
        assert d.size == 0

    def test_repr_shows_preview(self) -> None:
        """__repr__ shows content preview."""
        d = Datum.create(b"short")
        assert "short" in repr(d)

    def test_repr_truncates_long_content(self) -> None:
        """__repr__ truncates long content."""
        d = Datum.create(b"a" * 100)
        r = repr(d)
        assert "..." in r
        assert len(r) < 150  # Reasonable repr length


class TestDatumFrozen:
    """Tests for frozen dataclass behavior."""

    def test_datum_is_immutable(self) -> None:
        """Datum instances are immutable."""
        d = Datum.create(b"test")

        with pytest.raises(AttributeError):
            d.id = "new-id"  # type: ignore

    def test_datum_equality_by_value(self) -> None:
        """Datum equality is by value, not identity."""
        # Same ID and content = equal
        d1 = Datum(
            id="same-id",
            content=b"test",
            created_at=1000.0,
            causal_parent=None,
            metadata={},
        )
        d2 = Datum(
            id="same-id",
            content=b"test",
            created_at=1000.0,
            causal_parent=None,
            metadata={},
        )

        assert d1 == d2

        # Different ID = not equal
        d3 = Datum(
            id="different-id",
            content=b"test",
            created_at=1000.0,
            causal_parent=None,
            metadata={},
        )

        assert d1 != d3
