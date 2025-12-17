"""
Tests for Festival: Seasonal creative challenges.

Tests cover:
- Festival creation and lifecycle
- Entry submission and validation
- Voting mechanics
- Season detection
- Festival manager operations
"""

from datetime import datetime, timedelta, timezone

import pytest
from agents.atelier.festival import (
    Festival,
    FestivalEntry,
    FestivalManager,
    FestivalStatus,
    Season,
    get_festival_manager,
)


class TestFestival:
    """Tests for the Festival class."""

    def test_create_festival_basic(self) -> None:
        """Test basic festival creation."""
        festival = Festival.create(
            title="Winter Tales",
            theme="longest night",
        )

        assert festival.id.startswith("fest-")
        assert festival.title == "Winter Tales"
        assert festival.theme == "longest night"
        assert festival.status == FestivalStatus.ACTIVE
        assert festival.is_accepting_entries

    def test_create_festival_with_options(self) -> None:
        """Test festival creation with custom options."""
        festival = Festival.create(
            title="Constraint Jam",
            theme="limitation sparks creativity",
            duration_hours=24,
            voting_hours=12,
            season=Season.SUMMER,
            constraints=["no adjectives", "exactly 50 words"],
        )

        assert festival.season == Season.SUMMER
        assert len(festival.constraints) == 2
        assert "no adjectives" in festival.constraints

    def test_festival_time_remaining(self) -> None:
        """Test time remaining calculation."""
        festival = Festival.create(
            title="Test",
            theme="test",
            duration_hours=24,
        )

        remaining = festival.time_remaining
        assert remaining is not None
        # Should be close to 24 hours (allowing some time for test execution)
        assert remaining.total_seconds() > 23 * 3600

    def test_festival_not_accepting_when_concluded(self) -> None:
        """Test that concluded festivals don't accept entries."""
        festival = Festival.create(
            title="Test",
            theme="test",
        )
        festival.status = FestivalStatus.CONCLUDED

        assert not festival.is_accepting_entries
        entry = festival.enter("calligrapher", "test", "content")
        assert entry is None


class TestFestivalEntry:
    """Tests for festival entries."""

    def test_enter_festival(self) -> None:
        """Test submitting an entry."""
        festival = Festival.create(
            title="Test Fest",
            theme="testing",
        )

        entry = festival.enter(
            artisan="calligrapher",
            prompt="a haiku about testing",
            content="tests verify truth\nlines of code dance together\ngreen lights bring me joy",
        )

        assert entry is not None
        assert entry.id.startswith("entry-")
        assert entry.artisan == "calligrapher"
        assert entry.votes == 0
        assert len(festival.entries) == 1

    def test_entry_with_piece_id(self) -> None:
        """Test entry with linked piece."""
        festival = Festival.create(
            title="Test",
            theme="test",
        )

        entry = festival.enter(
            artisan="cartographer",
            prompt="test",
            content="test content",
            piece_id="piece-abc123",
        )

        assert entry is not None
        assert entry.piece_id == "piece-abc123"

    def test_multiple_entries(self) -> None:
        """Test multiple entries from different artisans."""
        festival = Festival.create(
            title="Multi Entry",
            theme="many voices",
        )

        festival.enter("calligrapher", "haiku", "content 1")
        festival.enter("cartographer", "map", "content 2")
        festival.enter("archivist", "synthesis", "content 3")

        assert len(festival.entries) == 3
        artisans = {e.artisan for e in festival.entries}
        assert artisans == {"calligrapher", "cartographer", "archivist"}


class TestVoting:
    """Tests for voting mechanics."""

    def test_vote_for_entry(self) -> None:
        """Test basic voting."""
        festival = Festival.create(
            title="Vote Test",
            theme="voting",
        )
        entry = festival.enter("calligrapher", "test", "content")
        assert entry is not None

        success = festival.vote(entry.id)
        assert success
        assert entry.votes == 1

    def test_vote_multiple_times(self) -> None:
        """Test multiple votes."""
        festival = Festival.create(
            title="Vote Test",
            theme="voting",
        )
        entry = festival.enter("calligrapher", "test", "content")
        assert entry is not None

        festival.vote(entry.id, count=3)
        assert entry.votes == 3

    def test_vote_nonexistent_entry(self) -> None:
        """Test voting for non-existent entry."""
        festival = Festival.create(
            title="Vote Test",
            theme="voting",
        )

        success = festival.vote("nonexistent-id")
        assert not success

    def test_vote_during_voting_phase(self) -> None:
        """Test voting during voting phase."""
        festival = Festival.create(
            title="Vote Test",
            theme="voting",
        )
        entry = festival.enter("calligrapher", "test", "content")
        assert entry is not None

        # Move to voting phase
        festival.status = FestivalStatus.VOTING

        success = festival.vote(entry.id)
        assert success
        assert entry.votes == 1

    def test_vote_during_concluded(self) -> None:
        """Test that voting fails when concluded."""
        festival = Festival.create(
            title="Vote Test",
            theme="voting",
        )
        entry = festival.enter("calligrapher", "test", "content")
        assert entry is not None

        # Conclude festival
        festival.status = FestivalStatus.CONCLUDED

        success = festival.vote(entry.id)
        assert not success

    def test_leaderboard(self) -> None:
        """Test leaderboard ordering."""
        festival = Festival.create(
            title="Leaderboard Test",
            theme="competition",
        )

        e1 = festival.enter("calligrapher", "entry1", "content1")
        e2 = festival.enter("cartographer", "entry2", "content2")
        e3 = festival.enter("archivist", "entry3", "content3")
        assert e1 and e2 and e3

        # Give different vote counts
        festival.vote(e1.id, count=5)
        festival.vote(e2.id, count=10)
        festival.vote(e3.id, count=3)

        leaderboard = festival.get_leaderboard(limit=3)
        assert len(leaderboard) == 3
        assert leaderboard[0].artisan == "cartographer"  # 10 votes
        assert leaderboard[1].artisan == "calligrapher"  # 5 votes
        assert leaderboard[2].artisan == "archivist"  # 3 votes


class TestSeason:
    """Tests for Season enum."""

    def test_season_theme_suggestions(self) -> None:
        """Test that all seasons have theme suggestions."""
        for season in Season:
            suggestions = season.theme_suggestions
            assert len(suggestions) > 0
            assert all(isinstance(s, str) for s in suggestions)

    def test_current_season(self) -> None:
        """Test current season detection."""
        season = Season.current()
        assert season in Season

        # Based on December test run, should be winter
        now = datetime.now(timezone.utc)
        if now.month in (12, 1, 2):
            assert season == Season.WINTER


class TestFestivalManager:
    """Tests for FestivalManager."""

    def test_create_and_get(self) -> None:
        """Test creating and retrieving festivals."""
        manager = FestivalManager()
        festival = manager.create("Test Fest", "testing")

        retrieved = manager.get(festival.id)
        assert retrieved is not None
        assert retrieved.title == "Test Fest"

    def test_list_festivals(self) -> None:
        """Test listing festivals."""
        manager = FestivalManager()
        manager.create("Fest 1", "theme 1")
        manager.create("Fest 2", "theme 2")
        manager.create("Fest 3", "theme 3")

        all_festivals = manager.list_festivals()
        assert len(all_festivals) == 3

    def test_list_by_status(self) -> None:
        """Test filtering by status."""
        manager = FestivalManager()
        f1 = manager.create("Active", "active")
        f2 = manager.create("To Conclude", "conclude")
        f2.status = FestivalStatus.CONCLUDED

        active = manager.list_festivals(status=FestivalStatus.ACTIVE)
        concluded = manager.list_festivals(status=FestivalStatus.CONCLUDED)

        assert len(active) == 1
        assert active[0].id == f1.id
        assert len(concluded) == 1
        assert concluded[0].id == f2.id

    def test_active_shortcut(self) -> None:
        """Test active() shortcut method."""
        manager = FestivalManager()
        manager.create("Active 1", "active")
        manager.create("Active 2", "active")
        f3 = manager.create("Concluded", "done")
        f3.status = FestivalStatus.CONCLUDED

        active = manager.active()
        assert len(active) == 2

    def test_enter_via_manager(self) -> None:
        """Test entering via manager."""
        manager = FestivalManager()
        festival = manager.create("Entry Test", "entries")

        entry = manager.enter(
            festival.id,
            "calligrapher",
            "test prompt",
            "test content",
        )

        assert entry is not None
        assert len(festival.entries) == 1

    def test_vote_via_manager(self) -> None:
        """Test voting via manager."""
        manager = FestivalManager()
        festival = manager.create("Vote Test", "voting")
        entry = manager.enter(festival.id, "calligrapher", "test", "content")
        assert entry is not None

        success = manager.vote(festival.id, entry.id, count=5)
        assert success
        assert entry.votes == 5

    def test_conclude_via_manager(self) -> None:
        """Test concluding via manager."""
        manager = FestivalManager()
        festival = manager.create("Conclude Test", "ending")
        manager.enter(festival.id, "calligrapher", "test", "content")
        manager.vote(festival.id, festival.entries[0].id, count=10)

        summary = manager.conclude(festival.id)

        assert summary is not None
        assert summary["title"] == "Conclude Test"
        assert summary["total_entries"] == 1
        assert summary["total_votes"] == 10
        assert len(summary["winners"]) == 1

    def test_suggest_theme(self) -> None:
        """Test theme suggestion."""
        manager = FestivalManager()
        theme = manager.suggest_theme()

        assert isinstance(theme, str)
        assert len(theme) > 0


class TestFestivalSerialization:
    """Tests for serialization/deserialization."""

    def test_festival_to_dict(self) -> None:
        """Test festival serialization."""
        festival = Festival.create(
            title="Serialize Test",
            theme="serialization",
            constraints=["constraint 1"],
        )
        festival.enter("calligrapher", "test", "content")

        data = festival.to_dict()

        assert data["id"] == festival.id
        assert data["title"] == "Serialize Test"
        assert data["theme"] == "serialization"
        assert data["status"] == "active"
        assert len(data["entries"]) == 1
        assert data["entry_count"] == 1

    def test_festival_from_dict(self) -> None:
        """Test festival deserialization."""
        original = Festival.create(
            title="Deserialize Test",
            theme="deserialization",
        )
        original.enter("calligrapher", "test", "content")

        data = original.to_dict()
        restored = Festival.from_dict(data)

        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.theme == original.theme
        assert len(restored.entries) == 1

    def test_entry_to_dict(self) -> None:
        """Test entry serialization."""
        entry = FestivalEntry(
            id="entry-123",
            festival_id="fest-456",
            artisan="calligrapher",
            prompt="test prompt",
            content="test content",
            piece_id="piece-789",
            votes=5,
        )

        data = entry.to_dict()

        assert data["id"] == "entry-123"
        assert data["artisan"] == "calligrapher"
        assert data["votes"] == 5
        assert data["piece_id"] == "piece-789"


class TestFestivalStatusAdvancement:
    """Tests for status advancement."""

    def test_advance_upcoming_to_active(self) -> None:
        """Test advancing from upcoming to active."""
        festival = Festival.create(
            title="Advance Test",
            theme="advancement",
            start_now=False,
        )
        # Force start time to past
        festival.starts_at = datetime.now(timezone.utc) - timedelta(hours=1)

        # Should be upcoming initially
        assert festival.status == FestivalStatus.UPCOMING

        # Advance should move to active
        new_status = festival.advance_status()
        assert new_status == FestivalStatus.ACTIVE

    def test_advance_active_to_voting(self) -> None:
        """Test advancing from active to voting."""
        festival = Festival.create(
            title="Advance Test",
            theme="advancement",
        )
        # Force end time to past
        festival.ends_at = datetime.now(timezone.utc) - timedelta(hours=1)

        new_status = festival.advance_status()
        assert new_status == FestivalStatus.VOTING

    def test_advance_all(self) -> None:
        """Test advancing all festivals."""
        manager = FestivalManager()
        f1 = manager.create("Fest 1", "theme 1")
        f2 = manager.create("Fest 2", "theme 2")

        # Set f1 to need advancement
        f1.ends_at = datetime.now(timezone.utc) - timedelta(hours=1)

        changed = manager.advance_all()

        assert f1.id in changed
        assert f2.id not in changed  # f2 didn't need to change


class TestGlobalManager:
    """Tests for global singleton."""

    def test_get_festival_manager_singleton(self) -> None:
        """Test that get_festival_manager returns singleton."""
        # Note: This test may fail in isolation due to module state
        # In real usage, the singleton persists across calls
        manager1 = get_festival_manager()
        manager2 = get_festival_manager()

        # Should be the same instance
        assert manager1 is manager2
