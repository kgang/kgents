"""
Tests for Lesson: Curated Knowledge Layer with Versioning.

Lesson Laws:
- Law 1 (Immutability): Lessons are frozen after creation
- Law 2 (Supersession): New versions explicitly supersede old
- Law 3 (History Preserved): All versions are kept for reference
- Law 4 (Topic Uniqueness): One current version per topic
"""

from datetime import datetime, timedelta

import pytest

from ..lesson import (
    Lesson,
    LessonId,
    LessonStatus,
    LessonStore,
    generate_lesson_id,
    get_lesson_store,
    reset_lesson_store,
    set_lesson_store,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_global_store():
    """Reset global terrace store before each test."""
    reset_lesson_store()
    yield
    reset_lesson_store()


@pytest.fixture
def store() -> LessonStore:
    """Create a fresh LessonStore."""
    return LessonStore()


@pytest.fixture
def sample_terrace() -> Lesson:
    """Create a sample Lesson."""
    return Lesson.create(
        topic="AGENTESE registration",
        content="Use @node decorator. Register in gateway.py.",
        tags=("agentese", "patterns"),
        source="debugging session",
    )


# =============================================================================
# Basic Lesson Tests
# =============================================================================


class TestLessonBasics:
    """Test basic Lesson functionality."""

    def test_create_terrace(self, sample_terrace: Lesson):
        """Lesson can be created."""
        assert sample_terrace.topic == "AGENTESE registration"
        assert sample_terrace.version == 1
        assert sample_terrace.status == LessonStatus.CURRENT
        assert sample_terrace.supersedes is None

    def test_terrace_id_generated(self, sample_terrace: Lesson):
        """Lesson IDs are generated."""
        assert sample_terrace.id.startswith("lesson-")
        assert len(str(sample_terrace.id)) == 19  # "lesson-" + 12 hex chars

    def test_generate_lesson_id(self):
        """IDs can be generated independently."""
        id1 = generate_lesson_id()
        id2 = generate_lesson_id()
        assert id1 != id2
        assert id1.startswith("lesson-")

    def test_terrace_has_tags(self, sample_terrace: Lesson):
        """Lesson preserves tags."""
        assert "agentese" in sample_terrace.tags
        assert "patterns" in sample_terrace.tags

    def test_terrace_has_source(self, sample_terrace: Lesson):
        """Lesson preserves source."""
        assert sample_terrace.source == "debugging session"


# =============================================================================
# Law 1: Immutability
# =============================================================================


class TestImmutability:
    """Test Law 1: Lessons are frozen after creation."""

    def test_terrace_is_frozen(self, sample_terrace: Lesson):
        """Lesson cannot be mutated."""
        with pytest.raises(Exception):  # FrozenInstanceError
            sample_terrace.content = "new content"  # type: ignore

    def test_evolve_returns_new_terrace(self, sample_terrace: Lesson):
        """evolve() returns a new Lesson, not mutating original."""
        evolved = sample_terrace.evolve(
            content="Updated content",
            reason="Test evolution",
        )

        # Original unchanged
        assert sample_terrace.content == "Use @node decorator. Register in gateway.py."
        assert sample_terrace.version == 1

        # New terrace has changes
        assert evolved.content == "Updated content"
        assert evolved.version == 2


# =============================================================================
# Law 2: Supersession
# =============================================================================


class TestSupersession:
    """Test Law 2: New versions explicitly supersede old."""

    def test_evolve_sets_supersedes(self, sample_terrace: Lesson):
        """evolve() sets supersedes to previous ID."""
        evolved = sample_terrace.evolve(content="New content")

        assert evolved.supersedes == sample_terrace.id

    def test_evolve_increments_version(self, sample_terrace: Lesson):
        """evolve() increments version number."""
        v1 = sample_terrace
        v2 = v1.evolve(content="Version 2")
        v3 = v2.evolve(content="Version 3")

        assert v1.version == 1
        assert v2.version == 2
        assert v3.version == 3

    def test_evolve_preserves_topic(self, sample_terrace: Lesson):
        """evolve() preserves the topic."""
        evolved = sample_terrace.evolve(content="New content")

        assert evolved.topic == sample_terrace.topic

    def test_evolve_inherits_tags(self, sample_terrace: Lesson):
        """evolve() inherits tags if not specified."""
        evolved = sample_terrace.evolve(content="New content")

        assert evolved.tags == sample_terrace.tags

    def test_evolve_can_change_tags(self, sample_terrace: Lesson):
        """evolve() can update tags."""
        evolved = sample_terrace.evolve(
            content="New content",
            tags=("new-tag", "different"),
        )

        assert "new-tag" in evolved.tags
        assert "agentese" not in evolved.tags

    def test_evolve_records_reason(self, sample_terrace: Lesson):
        """evolve() records evolution reason."""
        evolved = sample_terrace.evolve(
            content="New content",
            reason="Found a bug in the pattern",
        )

        assert evolved.evolution_reason == "Found a bug in the pattern"

    def test_has_supersedes_property(self, sample_terrace: Lesson):
        """has_supersedes property works correctly."""
        v1 = sample_terrace
        v2 = v1.evolve(content="V2")

        assert v1.has_supersedes is False
        assert v2.has_supersedes is True


# =============================================================================
# Law 3: History Preserved
# =============================================================================


class TestHistoryPreserved:
    """Test Law 3: All versions are kept for reference."""

    def test_store_keeps_all_versions(self, store: LessonStore):
        """Store keeps all versions of a topic."""
        v1 = Lesson.create(topic="Test", content="Version 1")
        store.add(v1)

        v2 = v1.evolve(content="Version 2")
        store.add(v2)

        v3 = v2.evolve(content="Version 3")
        store.add(v3)

        # All versions should be retrievable
        history = store.history("Test")
        assert len(history) == 3
        assert history[0].version == 1
        assert history[1].version == 2
        assert history[2].version == 3

    def test_original_still_retrievable(self, store: LessonStore):
        """Original version can still be retrieved by ID."""
        v1 = Lesson.create(topic="Test", content="Version 1")
        store.add(v1)

        v2 = v1.evolve(content="Version 2")
        store.add(v2)

        # Original still accessible
        original = store.get(v1.id)
        assert original is not None
        assert original.version == 1


# =============================================================================
# Law 4: Topic Uniqueness
# =============================================================================


class TestTopicUniqueness:
    """Test Law 4: One current version per topic."""

    def test_current_returns_latest(self, store: LessonStore):
        """current() returns the latest CURRENT version."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)

        v2 = v1.evolve(content="V2")
        store.add(v2)

        current = store.current("Test")
        assert current is not None
        assert current.version == 2

    def test_add_marks_previous_superseded(self, store: LessonStore):
        """Adding evolved version marks previous as SUPERSEDED."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)

        v2 = v1.evolve(content="V2")
        store.add(v2)

        # Check v1 is now superseded
        v1_updated = store.get(v1.id)
        assert v1_updated is not None
        assert v1_updated.status == LessonStatus.SUPERSEDED

    def test_only_one_current_per_topic(self, store: LessonStore):
        """Only one CURRENT per topic."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)

        v2 = v1.evolve(content="V2")
        store.add(v2)

        v3 = v2.evolve(content="V3")
        store.add(v3)

        # Count CURRENT for this topic
        current_count = sum(1 for t in store.history("Test") if t.is_current)
        assert current_count == 1


# =============================================================================
# Status Transitions
# =============================================================================


class TestStatusTransitions:
    """Test status transitions."""

    def test_deprecate(self, sample_terrace: Lesson):
        """Lesson can be deprecated."""
        deprecated = sample_terrace.deprecate(reason="No longer recommended")

        assert deprecated.status == LessonStatus.DEPRECATED
        assert deprecated.is_deprecated is True
        assert "deprecated_at" in deprecated.metadata

    def test_archive(self, sample_terrace: Lesson):
        """Lesson can be archived."""
        archived = sample_terrace.archive()

        assert archived.status == LessonStatus.ARCHIVED
        assert "archived_at" in archived.metadata

    def test_status_properties(self):
        """Status properties work correctly."""
        current = Lesson.create(topic="Test", content="Content")
        assert current.is_current is True
        assert current.is_superseded is False
        assert current.is_deprecated is False


# =============================================================================
# LessonStore Tests
# =============================================================================


class TestLessonStore:
    """Test LessonStore functionality."""

    def test_add_and_get(self, store: LessonStore):
        """Lessons can be added and retrieved."""
        terrace = Lesson.create(topic="Test", content="Content")
        store.add(terrace)

        retrieved = store.get(terrace.id)
        assert retrieved is not None
        assert retrieved.topic == "Test"

    def test_get_nonexistent(self, store: LessonStore):
        """Getting nonexistent ID returns None."""
        result = store.get(LessonId("nonexistent"))
        assert result is None

    def test_current_returns_none_for_unknown_topic(self, store: LessonStore):
        """current() returns None for unknown topic."""
        result = store.current("Unknown Topic")
        assert result is None

    def test_history_returns_empty_for_unknown(self, store: LessonStore):
        """history() returns empty list for unknown topic."""
        result = store.history("Unknown Topic")
        assert result == []

    def test_latest_vs_current(self, store: LessonStore):
        """latest() returns latest regardless of status."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)

        # Deprecate it (no longer CURRENT)
        v1_deprecated = v1.deprecate()
        store.update(v1_deprecated)

        # current() returns None (no CURRENT)
        assert store.current("Test") is None

        # latest() still returns it
        latest = store.latest("Test")
        assert latest is not None
        assert latest.version == 1


# =============================================================================
# Search and Filtering
# =============================================================================


class TestSearchAndFiltering:
    """Test search and filtering capabilities."""

    def test_by_tag(self, store: LessonStore):
        """Filter by tag works."""
        t1 = Lesson.create(topic="A", content="C1", tags=("python",))
        t2 = Lesson.create(topic="B", content="C2", tags=("rust",))
        t3 = Lesson.create(topic="C", content="C3", tags=("python", "testing"))
        store.add(t1)
        store.add(t2)
        store.add(t3)

        python_terraces = store.by_tag("python")
        assert len(python_terraces) == 2

    def test_by_source(self, store: LessonStore):
        """Filter by source works."""
        t1 = Lesson.create(topic="A", content="C1", source="debugging")
        t2 = Lesson.create(topic="B", content="C2", source="review")
        store.add(t1)
        store.add(t2)

        debugging = store.by_source("debugging")
        assert len(debugging) == 1
        assert debugging[0].topic == "A"

    def test_search_by_topic(self, store: LessonStore):
        """Search matches topics."""
        t1 = Lesson.create(topic="AGENTESE patterns", content="...")
        t2 = Lesson.create(topic="Testing patterns", content="...")
        store.add(t1)
        store.add(t2)

        results = store.search("AGENTESE")
        assert len(results) == 1
        assert results[0].topic == "AGENTESE patterns"

    def test_search_by_content(self, store: LessonStore):
        """Search matches content."""
        t1 = Lesson.create(topic="A", content="Use the @node decorator")
        t2 = Lesson.create(topic="B", content="Use pytest fixtures")
        store.add(t1)
        store.add(t2)

        results = store.search("@node")
        assert len(results) == 1
        assert results[0].topic == "A"

    def test_search_case_insensitive(self, store: LessonStore):
        """Search is case insensitive."""
        t1 = Lesson.create(topic="AGENTESE", content="...")
        store.add(t1)

        results = store.search("agentese")
        assert len(results) == 1


# =============================================================================
# Listing Methods
# =============================================================================


class TestListingMethods:
    """Test listing methods."""

    def test_all_current(self, store: LessonStore):
        """all_current() returns only CURRENT terraces."""
        t1 = Lesson.create(topic="A", content="V1")
        store.add(t1)
        t2 = t1.evolve(content="V2")
        store.add(t2)

        t3 = Lesson.create(topic="B", content="V1")
        store.add(t3)

        current = store.all_current()
        assert len(current) == 2  # t2 (topic A) and t3 (topic B)

    def test_all_topics(self, store: LessonStore):
        """all_topics() returns all topic names."""
        t1 = Lesson.create(topic="Topic A", content="...")
        t2 = Lesson.create(topic="Topic B", content="...")
        store.add(t1)
        store.add(t2)

        topics = store.all_topics()
        assert "Topic A" in topics
        assert "Topic B" in topics

    def test_deprecated(self, store: LessonStore):
        """deprecated() returns deprecated terraces."""
        t1 = Lesson.create(topic="A", content="...")
        store.add(t1)
        t1_deprecated = t1.deprecate()
        store.update(t1_deprecated)

        deprecated = store.deprecated()
        assert len(deprecated) == 1

    def test_recent(self, store: LessonStore):
        """recent() returns most recent terraces."""
        t1 = Lesson.create(topic="A", content="...")
        t2 = Lesson.create(topic="B", content="...")
        t3 = Lesson.create(topic="C", content="...")
        store.add(t1)
        store.add(t2)
        store.add(t3)

        recent = store.recent(limit=2)
        assert len(recent) == 2


# =============================================================================
# Version Traversal
# =============================================================================


class TestVersionTraversal:
    """Test version traversal methods."""

    def test_predecessor(self, store: LessonStore):
        """predecessor() returns previous version."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)
        v2 = v1.evolve(content="V2")
        store.add(v2)

        pred = store.predecessor(v2)
        assert pred is not None
        assert pred.id == v1.id

    def test_predecessor_none_for_first(self, store: LessonStore):
        """predecessor() returns None for first version."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)

        pred = store.predecessor(v1)
        assert pred is None

    def test_successor(self, store: LessonStore):
        """successor() returns next version."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)
        v2 = v1.evolve(content="V2")
        store.add(v2)

        succ = store.successor(v1)
        assert succ is not None
        assert succ.id == v2.id

    def test_successor_none_for_latest(self, store: LessonStore):
        """successor() returns None for latest version."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)

        succ = store.successor(v1)
        assert succ is None

    def test_full_chain(self, store: LessonStore):
        """full_chain() returns complete version history."""
        v1 = Lesson.create(topic="Test", content="V1")
        store.add(v1)
        v2 = v1.evolve(content="V2")
        store.add(v2)
        v3 = v2.evolve(content="V3")
        store.add(v3)

        chain = store.full_chain("Test")
        assert len(chain) == 3
        assert [t.version for t in chain] == [1, 2, 3]


# =============================================================================
# Statistics
# =============================================================================


class TestStatistics:
    """Test statistics methods."""

    def test_stats(self, store: LessonStore):
        """stats() returns store statistics."""
        v1 = Lesson.create(topic="A", content="V1")
        store.add(v1)
        v2 = v1.evolve(content="V2")
        store.add(v2)

        t2 = Lesson.create(topic="B", content="V1")
        store.add(t2)
        t2_deprecated = t2.deprecate()
        store.update(t2_deprecated)

        stats = store.stats()
        assert stats["total"] == 3
        assert stats["topics"] == 2
        assert stats["current"] == 1  # Only v2 is current
        assert stats["superseded"] == 1  # v1
        assert stats["deprecated"] == 1  # t2

    def test_len(self, store: LessonStore):
        """len() returns total terrace count."""
        t1 = Lesson.create(topic="A", content="...")
        t2 = Lesson.create(topic="B", content="...")
        store.add(t1)
        store.add(t2)

        assert len(store) == 2


# =============================================================================
# Serialization
# =============================================================================


class TestSerialization:
    """Test serialization."""

    def test_to_dict(self, sample_terrace: Lesson):
        """Lesson can be converted to dict."""
        data = sample_terrace.to_dict()

        assert data["topic"] == "AGENTESE registration"
        assert data["version"] == 1
        assert data["status"] == "CURRENT"
        assert "agentese" in data["tags"]

    def test_from_dict(self, sample_terrace: Lesson):
        """Lesson can be restored from dict."""
        data = sample_terrace.to_dict()
        restored = Lesson.from_dict(data)

        assert restored.topic == sample_terrace.topic
        assert restored.content == sample_terrace.content
        assert restored.version == sample_terrace.version
        assert restored.tags == sample_terrace.tags

    def test_round_trip(self, sample_terrace: Lesson):
        """Serialization round-trips correctly."""
        evolved = sample_terrace.evolve(
            content="New content",
            reason="Evolution test",
        )

        data = evolved.to_dict()
        restored = Lesson.from_dict(data)

        assert restored.version == 2
        assert restored.supersedes is not None
        assert restored.evolution_reason == "Evolution test"


# =============================================================================
# Global Instance
# =============================================================================


class TestGlobalInstance:
    """Test global terrace store instance."""

    def test_get_global(self):
        """Global store can be retrieved."""
        store = get_lesson_store()
        assert isinstance(store, LessonStore)

    def test_global_is_singleton(self):
        """Global store is a singleton."""
        store1 = get_lesson_store()
        store2 = get_lesson_store()
        assert store1 is store2

    def test_set_global(self):
        """Global store can be set."""
        custom = LessonStore()
        set_lesson_store(custom)

        assert get_lesson_store() is custom

    def test_reset_global(self):
        """Global store can be reset."""
        store1 = get_lesson_store()
        reset_lesson_store()
        store2 = get_lesson_store()

        assert store1 is not store2


# =============================================================================
# Properties
# =============================================================================


class TestProperties:
    """Test Lesson properties."""

    def test_age_days(self, sample_terrace: Lesson):
        """age_days returns positive value."""
        # Just created, should be very close to 0
        assert sample_terrace.age_days >= 0
        assert sample_terrace.age_days < 1  # Less than a day old

    def test_confidence(self):
        """Confidence is preserved and defaults to 1.0."""
        t1 = Lesson.create(topic="A", content="...", confidence=0.8)
        assert t1.confidence == 0.8

        t2 = Lesson.create(topic="B", content="...")
        assert t2.confidence == 1.0

    def test_evolve_updates_confidence(self):
        """evolve() can update confidence."""
        t1 = Lesson.create(topic="A", content="...", confidence=0.5)
        t2 = t1.evolve(content="...", confidence=0.9)

        assert t2.confidence == 0.9


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_content(self):
        """Empty content is allowed."""
        terrace = Lesson.create(topic="Empty", content="")
        assert terrace.content == ""

    def test_empty_tags(self):
        """Empty tags tuple is valid."""
        terrace = Lesson.create(topic="NoTags", content="...")
        assert terrace.tags == ()

    def test_long_content(self):
        """Long content is handled."""
        content = "x" * 100000
        terrace = Lesson.create(topic="Long", content=content)
        assert len(terrace.content) == 100000

    def test_unicode_content(self):
        """Unicode content is handled."""
        terrace = Lesson.create(topic="Unicode", content="Hello, World!")
        assert terrace.content == "Hello, World!"

    def test_multiple_topics_independent(self, store: LessonStore):
        """Multiple topics evolve independently."""
        a1 = Lesson.create(topic="A", content="A1")
        store.add(a1)
        a2 = a1.evolve(content="A2")
        store.add(a2)

        b1 = Lesson.create(topic="B", content="B1")
        store.add(b1)

        # A has 2 versions, B has 1
        assert len(store.history("A")) == 2
        assert len(store.history("B")) == 1

        # Both currents are accessible
        assert store.current("A").content == "A2"
        assert store.current("B").content == "B1"
