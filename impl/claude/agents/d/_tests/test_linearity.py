"""
Tests for LinearityMap: Resource class tracking for context management.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from agents.d.linearity import (
    LinearityMap,
    ResourceClass,
    ResourceTag,
    TrackedResource,
    classify_by_content,
    classify_by_role,
    create_classifier,
)


class TestResourceClass:
    """Tests for ResourceClass enum."""

    def test_ordering(self) -> None:
        """Resource classes have correct ordering."""
        assert ResourceClass.DROPPABLE < ResourceClass.REQUIRED
        assert ResourceClass.REQUIRED < ResourceClass.PRESERVED
        assert ResourceClass.DROPPABLE < ResourceClass.PRESERVED

    def test_values_are_distinct(self) -> None:
        """Each class has a unique value."""
        values = [rc.value for rc in ResourceClass]
        assert len(values) == len(set(values))


class TestResourceTag:
    """Tests for ResourceTag."""

    def test_immutability(self) -> None:
        """ResourceTag is frozen (immutable)."""
        tag = ResourceTag(
            resource_id="test",
            resource_class=ResourceClass.DROPPABLE,
            created_at=datetime.now(UTC),
            provenance="test",
            rationale="testing",
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            tag.resource_class = ResourceClass.REQUIRED  # type: ignore

    def test_fields_preserved(self) -> None:
        """All fields are correctly stored."""
        now = datetime.now(UTC)
        tag = ResourceTag(
            resource_id="res_123",
            resource_class=ResourceClass.PRESERVED,
            created_at=now,
            provenance="user_input",
            rationale="critical instruction",
        )

        assert tag.resource_id == "res_123"
        assert tag.resource_class == ResourceClass.PRESERVED
        assert tag.created_at == now
        assert tag.provenance == "user_input"
        assert tag.rationale == "critical instruction"


class TestTrackedResource:
    """Tests for TrackedResource."""

    def test_access_tracking(self) -> None:
        """Access count and timestamp are updated."""
        tag = ResourceTag(
            resource_id="test",
            resource_class=ResourceClass.DROPPABLE,
            created_at=datetime.now(UTC),
            provenance="test",
            rationale="testing",
        )
        tracked = TrackedResource(value="hello", tag=tag)

        assert tracked.accessed_count == 0
        assert tracked.last_accessed is None

        result = tracked.access()
        assert result == "hello"
        assert tracked.accessed_count == 1
        assert tracked.last_accessed is not None

        tracked.access()
        assert tracked.accessed_count == 2

    def test_generic_type(self) -> None:
        """TrackedResource works with any type."""
        tag = ResourceTag(
            resource_id="test",
            resource_class=ResourceClass.REQUIRED,
            created_at=datetime.now(UTC),
            provenance="test",
            rationale="testing",
        )

        # Dict
        dict_res = TrackedResource(value={"key": "value"}, tag=tag)
        assert dict_res.access() == {"key": "value"}

        # List
        list_res = TrackedResource(value=[1, 2, 3], tag=tag)
        assert list_res.access() == [1, 2, 3]

        # Custom object
        class MyObj:
            x: int = 42

        obj_res = TrackedResource(value=MyObj(), tag=tag)
        assert obj_res.access().x == 42


class TestLinearityMap:
    """Tests for LinearityMap."""

    def test_tag_creates_resource(self) -> None:
        """Tagging creates a tracked resource."""
        lm = LinearityMap()
        rid = lm.tag("hello", ResourceClass.DROPPABLE, "test")

        assert rid.startswith("res_")
        assert lm.get(rid) == "hello"
        assert lm.get_class(rid) == ResourceClass.DROPPABLE

    def test_tag_with_custom_id(self) -> None:
        """Can specify custom resource ID."""
        lm = LinearityMap()
        rid = lm.tag("hello", ResourceClass.REQUIRED, "test", resource_id="my_id")

        assert rid == "my_id"
        assert lm.get("my_id") == "hello"

    def test_get_nonexistent_returns_none(self) -> None:
        """Getting nonexistent resource returns None."""
        lm = LinearityMap()
        assert lm.get("nonexistent") is None
        assert lm.get_tag("nonexistent") is None
        assert lm.get_class("nonexistent") is None

    def test_promote_increases_class(self) -> None:
        """Promotion increases resource class."""
        lm = LinearityMap()
        rid = lm.tag("important", ResourceClass.DROPPABLE, "test")

        assert lm.get_class(rid) == ResourceClass.DROPPABLE

        success = lm.promote(rid, ResourceClass.REQUIRED, "became important")
        assert success
        assert lm.get_class(rid) == ResourceClass.REQUIRED

        success = lm.promote(rid, ResourceClass.PRESERVED, "now critical")
        assert success
        assert lm.get_class(rid) == ResourceClass.PRESERVED

    def test_promote_monotonicity_enforced(self) -> None:
        """Cannot demote a resource."""
        lm = LinearityMap()
        rid = lm.tag("critical", ResourceClass.PRESERVED, "test")

        # Cannot demote
        success = lm.promote(rid, ResourceClass.REQUIRED, "demote")
        assert not success
        assert lm.get_class(rid) == ResourceClass.PRESERVED

        success = lm.promote(rid, ResourceClass.DROPPABLE, "demote")
        assert not success
        assert lm.get_class(rid) == ResourceClass.PRESERVED

    def test_promote_same_class_fails(self) -> None:
        """Cannot 'promote' to same class."""
        lm = LinearityMap()
        rid = lm.tag("thing", ResourceClass.REQUIRED, "test")

        success = lm.promote(rid, ResourceClass.REQUIRED, "same")
        assert not success

    def test_promote_nonexistent_fails(self) -> None:
        """Cannot promote nonexistent resource."""
        lm = LinearityMap()
        success = lm.promote("nonexistent", ResourceClass.REQUIRED, "test")
        assert not success

    def test_drop_droppable(self) -> None:
        """Can drop DROPPABLE resources."""
        lm = LinearityMap()
        rid = lm.tag("temp", ResourceClass.DROPPABLE, "test")

        assert lm.get(rid) == "temp"
        success = lm.drop(rid)
        assert success
        assert lm.get(rid) is None

    def test_drop_protected_fails(self) -> None:
        """Cannot drop REQUIRED or PRESERVED resources."""
        lm = LinearityMap()
        rid1 = lm.tag("required", ResourceClass.REQUIRED, "test")
        rid2 = lm.tag("preserved", ResourceClass.PRESERVED, "test")

        assert not lm.drop(rid1)
        assert lm.get(rid1) == "required"

        assert not lm.drop(rid2)
        assert lm.get(rid2) == "preserved"

    def test_drop_all_droppable(self) -> None:
        """Can drop all DROPPABLE resources at once."""
        lm = LinearityMap()
        lm.tag("drop1", ResourceClass.DROPPABLE, "test")
        lm.tag("drop2", ResourceClass.DROPPABLE, "test")
        lm.tag("keep1", ResourceClass.REQUIRED, "test")
        lm.tag("keep2", ResourceClass.PRESERVED, "test")

        dropped = lm.drop_all_droppable()
        assert dropped == 2

        counts = lm.count()
        assert counts["droppable"] == 0
        assert counts["required"] == 1
        assert counts["preserved"] == 1

    def test_queries_by_class(self) -> None:
        """Can query resources by class."""
        lm = LinearityMap()
        d1 = lm.tag("drop1", ResourceClass.DROPPABLE, "test")
        d2 = lm.tag("drop2", ResourceClass.DROPPABLE, "test")
        r1 = lm.tag("req1", ResourceClass.REQUIRED, "test")
        p1 = lm.tag("pres1", ResourceClass.PRESERVED, "test")

        droppable = lm.droppable()
        assert set(droppable) == {d1, d2}

        required = lm.required()
        assert required == [r1]

        preserved = lm.preserved()
        assert preserved == [p1]

        all_ids = set(lm.all_ids())
        assert all_ids == {d1, d2, r1, p1}

    def test_count(self) -> None:
        """Count returns correct totals."""
        lm = LinearityMap()
        lm.tag("d", ResourceClass.DROPPABLE, "test")
        lm.tag("r1", ResourceClass.REQUIRED, "test")
        lm.tag("r2", ResourceClass.REQUIRED, "test")
        lm.tag("p", ResourceClass.PRESERVED, "test")

        counts = lm.count()
        assert counts["droppable"] == 1
        assert counts["required"] == 2
        assert counts["preserved"] == 1
        assert counts["total"] == 4

    def test_tag_batch(self) -> None:
        """Can tag multiple resources at once."""
        lm = LinearityMap()
        items = [
            ("a", ResourceClass.DROPPABLE, "test"),
            ("b", ResourceClass.REQUIRED, "test"),
            ("c", ResourceClass.PRESERVED, "test"),
        ]

        ids = lm.tag_batch(items)
        assert len(ids) == 3
        assert lm.get(ids[0]) == "a"
        assert lm.get(ids[1]) == "b"
        assert lm.get(ids[2]) == "c"

    def test_partition(self) -> None:
        """Partition separates resources by class."""
        lm = LinearityMap()
        lm.tag("d1", ResourceClass.DROPPABLE, "test")
        lm.tag("d2", ResourceClass.DROPPABLE, "test")
        lm.tag("r1", ResourceClass.REQUIRED, "test")
        lm.tag("p1", ResourceClass.PRESERVED, "test")

        partition = lm.partition()
        assert set(partition[ResourceClass.DROPPABLE]) == {"d1", "d2"}
        assert partition[ResourceClass.REQUIRED] == ["r1"]
        assert partition[ResourceClass.PRESERVED] == ["p1"]

    def test_stats(self) -> None:
        """Stats include promotions and drops."""
        lm = LinearityMap()
        rid = lm.tag("x", ResourceClass.DROPPABLE, "test")
        lm.tag("y", ResourceClass.DROPPABLE, "test")

        lm.promote(rid, ResourceClass.REQUIRED, "promoted")
        lm.drop_all_droppable()

        stats = lm.stats
        assert stats["total"] == 1
        assert stats["promotions"] == 1
        assert stats["drops"] == 1

    def test_serialization_roundtrip(self) -> None:
        """Can serialize and deserialize."""
        lm = LinearityMap()
        rid1 = lm.tag("hello", ResourceClass.DROPPABLE, "test", rationale="greeting")
        rid2 = lm.tag("world", ResourceClass.PRESERVED, "user", rationale="critical")
        lm.promote(rid1, ResourceClass.REQUIRED, "became important")
        lm.get(rid1)  # Increment access count

        data = lm.to_dict()
        restored = LinearityMap.from_dict(data)

        assert restored.get(rid1) == "hello"
        assert restored.get_class(rid1) == ResourceClass.REQUIRED
        assert restored.get(rid2) == "world"
        assert restored.get_class(rid2) == ResourceClass.PRESERVED

        assert restored._promotions == 1

    def test_class_index_updated_on_promotion(self) -> None:
        """Class index is correctly updated during promotion."""
        lm = LinearityMap()
        rid = lm.tag("x", ResourceClass.DROPPABLE, "test")

        assert rid in lm._class_index[ResourceClass.DROPPABLE]
        assert rid not in lm._class_index[ResourceClass.REQUIRED]

        lm.promote(rid, ResourceClass.REQUIRED, "test")

        assert rid not in lm._class_index[ResourceClass.DROPPABLE]
        assert rid in lm._class_index[ResourceClass.REQUIRED]

    def test_promotion_preserves_creation_time(self) -> None:
        """Promotion keeps original creation timestamp."""
        lm = LinearityMap()
        rid = lm.tag("x", ResourceClass.DROPPABLE, "test")
        original_time = lm.get_tag(rid).created_at  # type: ignore

        lm.promote(rid, ResourceClass.REQUIRED, "test")
        new_tag = lm.get_tag(rid)

        assert new_tag is not None
        assert new_tag.created_at == original_time

    def test_promotion_appends_rationale(self) -> None:
        """Promotion history is preserved in rationale."""
        lm = LinearityMap()
        rid = lm.tag("x", ResourceClass.DROPPABLE, "test", rationale="initial")
        lm.promote(rid, ResourceClass.REQUIRED, "became important")
        lm.promote(rid, ResourceClass.PRESERVED, "now critical")

        tag = lm.get_tag(rid)
        assert tag is not None
        assert "initial" in tag.rationale
        assert "became important" in tag.rationale
        assert "now critical" in tag.rationale


class TestClassifiers:
    """Tests for classification functions."""

    def test_classify_by_role_user(self) -> None:
        """User messages are PRESERVED."""
        assert classify_by_role("user") == ResourceClass.PRESERVED
        assert classify_by_role("USER") == ResourceClass.PRESERVED
        assert classify_by_role("User") == ResourceClass.PRESERVED

    def test_classify_by_role_system(self) -> None:
        """System messages are REQUIRED."""
        assert classify_by_role("system") == ResourceClass.REQUIRED
        assert classify_by_role("SYSTEM") == ResourceClass.REQUIRED

    def test_classify_by_role_assistant(self) -> None:
        """Assistant messages are DROPPABLE."""
        assert classify_by_role("assistant") == ResourceClass.DROPPABLE
        assert classify_by_role("ASSISTANT") == ResourceClass.DROPPABLE

    def test_classify_by_role_unknown(self) -> None:
        """Unknown roles default to DROPPABLE."""
        assert classify_by_role("tool") == ResourceClass.DROPPABLE
        assert classify_by_role("unknown") == ResourceClass.DROPPABLE

    def test_classify_by_content_preserved_markers(self) -> None:
        """Content with PRESERVED markers is PRESERVED."""
        assert classify_by_content("You must do X") == ResourceClass.PRESERVED
        assert classify_by_content("REQUIRED: follow this") == ResourceClass.PRESERVED
        assert (
            classify_by_content("Critical: very important") == ResourceClass.PRESERVED
        )
        assert classify_by_content("```python\ncode```") == ResourceClass.PRESERVED
        assert (
            classify_by_content('def foo():\n    """docstring"""')
            == ResourceClass.PRESERVED
        )

    def test_classify_by_content_required_markers(self) -> None:
        """Content with REQUIRED markers is REQUIRED."""
        assert classify_by_content("Therefore we should") == ResourceClass.REQUIRED
        assert classify_by_content("Decision: use approach A") == ResourceClass.REQUIRED
        assert classify_by_content("The reason is simple") == ResourceClass.REQUIRED
        assert classify_by_content("I will implement X") == ResourceClass.REQUIRED

    def test_classify_by_content_default(self) -> None:
        """Content without markers is DROPPABLE."""
        assert classify_by_content("Just some text") == ResourceClass.DROPPABLE
        assert classify_by_content("Hello world") == ResourceClass.DROPPABLE

    def test_composite_classifier(self) -> None:
        """Composite classifier combines role and content."""
        classifier = create_classifier(role_weight=0.5, content_weight=0.5)

        # User + preserved content = PRESERVED
        assert classifier("user", "Must do X") == ResourceClass.PRESERVED

        # User + generic content = PRESERVED (user wins)
        assert classifier("user", "hello") == ResourceClass.PRESERVED

        # Assistant + preserved content = PRESERVED (content wins)
        assert classifier("assistant", "```code```") == ResourceClass.PRESERVED

        # Assistant + generic content = DROPPABLE
        assert classifier("assistant", "thinking...") == ResourceClass.DROPPABLE

    def test_composite_classifier_weights(self) -> None:
        """Weights affect classification."""
        # Heavy role weight
        role_heavy = create_classifier(role_weight=0.9, content_weight=0.1)
        # Role says DROPPABLE, content says REQUIRED
        # With heavy role weight, should follow role more
        result = role_heavy("assistant", "Therefore we decide")
        # 0.9 * 1 = 0.9 for DROPPABLE, 0.1 * 2 = 0.2 for REQUIRED
        assert result == ResourceClass.DROPPABLE

        # Heavy content weight
        content_heavy = create_classifier(role_weight=0.1, content_weight=0.9)
        result = content_heavy("assistant", "Therefore we decide")
        # 0.1 * 1 = 0.1 for DROPPABLE, 0.9 * 2 = 1.8 for REQUIRED
        assert result == ResourceClass.REQUIRED


class TestLinearityMapEdgeCases:
    """Edge case tests for LinearityMap."""

    def test_empty_map_operations(self) -> None:
        """Operations on empty map don't crash."""
        lm = LinearityMap()

        assert lm.droppable() == []
        assert lm.required() == []
        assert lm.preserved() == []
        assert lm.all_ids() == []
        assert lm.count()["total"] == 0
        assert lm.drop_all_droppable() == 0
        assert lm.partition() == {
            ResourceClass.DROPPABLE: [],
            ResourceClass.REQUIRED: [],
            ResourceClass.PRESERVED: [],
        }

    def test_serialization_empty(self) -> None:
        """Can serialize and deserialize empty map."""
        lm = LinearityMap()
        data = lm.to_dict()
        restored = LinearityMap.from_dict(data)
        assert restored.count()["total"] == 0

    def test_complex_values(self) -> None:
        """Can track complex nested values."""
        lm = LinearityMap()

        complex_value = {
            "messages": [
                {"role": "user", "content": "hello"},
                {"role": "assistant", "content": "hi"},
            ],
            "metadata": {"nested": {"deep": True}},
        }

        rid = lm.tag(complex_value, ResourceClass.PRESERVED, "conversation")
        retrieved = lm.get(rid)

        assert retrieved == complex_value
        assert retrieved["messages"][0]["content"] == "hello"

    def test_access_tracking_increments(self) -> None:
        """Multiple accesses are tracked correctly."""
        lm = LinearityMap()
        rid = lm.tag("x", ResourceClass.DROPPABLE, "test")

        for _ in range(10):
            lm.get(rid)

        tracked = lm._resources[rid]
        assert tracked.accessed_count == 10
