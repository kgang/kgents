"""
Festival: Seasonal creative challenges in Tiny Atelier.

A Festival is a time-bounded creative event where multiple participants
create pieces around a theme. Inspired by game jams, art festivals,
and the seasonal rhythm of creative communities.

From the plan:
    "Festival mode: Seasonal creative challenges"
    - Themed creative prompts
    - Time-bounded participation
    - Community voting/curation
    - Exhibition of entries

The Categorical View:
    Festival : Theme × Duration → Collection[Piece]
    The festival is a functor from creative intent to curated collection.

Example:
    festival = Festival.create(
        title="Winter Solstice",
        theme="longest night, first light",
        duration_hours=72,
    )

    # Enter the festival
    entry = await festival.enter("calligrapher", "a haiku about waiting")

    # View all entries
    entries = festival.entries

    # End festival, create exhibition
    exhibition = await festival.conclude()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class FestivalStatus(Enum):
    """Status of a festival."""

    UPCOMING = "upcoming"  # Not yet started
    ACTIVE = "active"  # Accepting entries
    VOTING = "voting"  # Entries closed, voting open
    CONCLUDED = "concluded"  # Festival finished


class Season(Enum):
    """Seasonal themes for festivals."""

    SPRING = "spring"  # Renewal, beginnings, growth
    SUMMER = "summer"  # Abundance, warmth, celebration
    AUTUMN = "autumn"  # Harvest, change, reflection
    WINTER = "winter"  # Rest, stillness, introspection

    @property
    def theme_suggestions(self) -> list[str]:
        """Get theme suggestions for this season."""
        suggestions = {
            Season.SPRING: [
                "first bloom",
                "thawing ground",
                "returning birds",
                "seeds of intention",
            ],
            Season.SUMMER: [
                "long shadows",
                "abundance",
                "the weight of noon",
                "wild growth",
            ],
            Season.AUTUMN: [
                "letting go",
                "harvest moon",
                "migration",
                "last warmth",
            ],
            Season.WINTER: [
                "longest night",
                "stillness",
                "the space between",
                "waiting for light",
            ],
        }
        return suggestions.get(self, [])

    @classmethod
    def current(cls) -> "Season":
        """Get the current season based on date (Northern Hemisphere)."""
        now = datetime.now(timezone.utc)
        month = now.month

        if month in (3, 4, 5):
            return cls.SPRING
        elif month in (6, 7, 8):
            return cls.SUMMER
        elif month in (9, 10, 11):
            return cls.AUTUMN
        else:
            return cls.WINTER


@dataclass
class FestivalEntry:
    """
    An entry in a festival.

    Represents a participant's submission to a festival challenge.
    """

    id: str
    festival_id: str
    artisan: str
    prompt: str
    content: str
    piece_id: str | None  # Link to created Piece if exists
    votes: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "festival_id": self.festival_id,
            "artisan": self.artisan,
            "prompt": self.prompt,
            "content": self.content,
            "piece_id": self.piece_id,
            "votes": self.votes,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FestivalEntry":
        return cls(
            id=data["id"],
            festival_id=data["festival_id"],
            artisan=data["artisan"],
            prompt=data["prompt"],
            content=data["content"],
            piece_id=data.get("piece_id"),
            votes=data.get("votes", 0),
            created_at=datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else data.get("created_at", datetime.now(timezone.utc)),
        )


@dataclass
class Festival:
    """
    A seasonal creative challenge.

    Festivals bring the community together around a shared creative prompt,
    with time-bounded participation and collective curation.
    """

    id: str
    title: str
    theme: str
    description: str
    season: Season
    status: FestivalStatus
    starts_at: datetime
    ends_at: datetime
    voting_ends_at: datetime | None
    entries: list[FestivalEntry] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        title: str,
        theme: str,
        *,
        description: str | None = None,
        duration_hours: int = 72,
        voting_hours: int = 24,
        season: Season | None = None,
        constraints: list[str] | None = None,
        start_now: bool = True,
    ) -> "Festival":
        """
        Create a new festival.

        Args:
            title: Festival name
            theme: The creative theme/prompt
            description: Optional longer description
            duration_hours: How long entries are accepted
            voting_hours: How long voting lasts after entries close
            season: Seasonal association (defaults to current)
            constraints: Optional creative constraints
            start_now: Whether to start immediately

        Returns:
            New Festival instance
        """
        now = datetime.now(timezone.utc)
        season = season or Season.current()

        starts_at = now if start_now else now + timedelta(hours=1)
        ends_at = starts_at + timedelta(hours=duration_hours)
        voting_ends_at = ends_at + timedelta(hours=voting_hours)

        return cls(
            id=f"fest-{uuid4().hex[:8]}",
            title=title,
            theme=theme,
            description=description or f"A {season.value} festival exploring: {theme}",
            season=season,
            status=FestivalStatus.ACTIVE if start_now else FestivalStatus.UPCOMING,
            starts_at=starts_at,
            ends_at=ends_at,
            voting_ends_at=voting_ends_at,
            constraints=constraints or [],
        )

    @property
    def is_accepting_entries(self) -> bool:
        """Check if festival is accepting entries."""
        if self.status != FestivalStatus.ACTIVE:
            return False
        now = datetime.now(timezone.utc)
        return self.starts_at <= now < self.ends_at

    @property
    def is_voting(self) -> bool:
        """Check if festival is in voting phase."""
        if self.status != FestivalStatus.VOTING:
            return False
        now = datetime.now(timezone.utc)
        return self.ends_at <= now < (self.voting_ends_at or self.ends_at)

    @property
    def time_remaining(self) -> timedelta | None:
        """Get time remaining for entries."""
        if not self.is_accepting_entries:
            return None
        now = datetime.now(timezone.utc)
        return self.ends_at - now

    def enter(
        self,
        artisan: str,
        prompt: str,
        content: str,
        *,
        piece_id: str | None = None,
    ) -> FestivalEntry | None:
        """
        Submit an entry to the festival.

        Args:
            artisan: Name of artisan/creator
            prompt: The specific prompt for this entry
            content: The created content
            piece_id: Optional link to a Piece in the gallery

        Returns:
            The created entry, or None if festival is not accepting entries
        """
        if not self.is_accepting_entries:
            return None

        entry = FestivalEntry(
            id=f"entry-{uuid4().hex[:8]}",
            festival_id=self.id,
            artisan=artisan,
            prompt=prompt,
            content=content,
            piece_id=piece_id,
        )
        self.entries.append(entry)
        return entry

    def vote(self, entry_id: str, count: int = 1) -> bool:
        """
        Cast votes for an entry.

        Args:
            entry_id: ID of the entry to vote for
            count: Number of votes (default 1)

        Returns:
            True if vote was recorded, False if entry not found or invalid state
        """
        # Allow voting during active or voting phase
        if self.status not in (FestivalStatus.ACTIVE, FestivalStatus.VOTING):
            return False

        for entry in self.entries:
            if entry.id == entry_id:
                entry.votes += count
                return True
        return False

    def advance_status(self) -> FestivalStatus:
        """
        Advance festival status based on time.

        Returns:
            The new status
        """
        now = datetime.now(timezone.utc)

        if self.status == FestivalStatus.UPCOMING and now >= self.starts_at:
            self.status = FestivalStatus.ACTIVE
        elif self.status == FestivalStatus.ACTIVE and now >= self.ends_at:
            self.status = FestivalStatus.VOTING
        elif self.status == FestivalStatus.VOTING:
            if self.voting_ends_at and now >= self.voting_ends_at:
                self.status = FestivalStatus.CONCLUDED

        return self.status

    def get_leaderboard(self, limit: int = 10) -> list[FestivalEntry]:
        """Get top entries by votes."""
        return sorted(self.entries, key=lambda e: e.votes, reverse=True)[:limit]

    def get_entry(self, entry_id: str) -> FestivalEntry | None:
        """Get an entry by ID."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def conclude(self) -> dict[str, Any]:
        """
        Conclude the festival and generate summary.

        Returns:
            Summary dict with winners and statistics
        """
        self.status = FestivalStatus.CONCLUDED

        leaderboard = self.get_leaderboard(limit=3)
        total_votes = sum(e.votes for e in self.entries)
        participating_artisans = set(e.artisan for e in self.entries)

        return {
            "festival_id": self.id,
            "title": self.title,
            "theme": self.theme,
            "total_entries": len(self.entries),
            "total_votes": total_votes,
            "participating_artisans": list(participating_artisans),
            "winners": [e.to_dict() for e in leaderboard],
            "concluded_at": datetime.now(timezone.utc).isoformat(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "theme": self.theme,
            "description": self.description,
            "season": self.season.value,
            "status": self.status.value,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "voting_ends_at": self.voting_ends_at.isoformat()
            if self.voting_ends_at
            else None,
            "entries": [e.to_dict() for e in self.entries],
            "constraints": self.constraints,
            "created_at": self.created_at.isoformat(),
            "entry_count": len(self.entries),
            "is_accepting_entries": self.is_accepting_entries,
            "is_voting": self.is_voting,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Festival":
        return cls(
            id=data["id"],
            title=data["title"],
            theme=data["theme"],
            description=data["description"],
            season=Season(data["season"]),
            status=FestivalStatus(data["status"]),
            starts_at=datetime.fromisoformat(data["starts_at"]),
            ends_at=datetime.fromisoformat(data["ends_at"]),
            voting_ends_at=datetime.fromisoformat(data["voting_ends_at"])
            if data.get("voting_ends_at")
            else None,
            entries=[FestivalEntry.from_dict(e) for e in data.get("entries", [])],
            constraints=data.get("constraints", []),
            created_at=datetime.fromisoformat(data["created_at"])
            if isinstance(data.get("created_at"), str)
            else datetime.now(timezone.utc),
        )


class FestivalManager:
    """
    Manages festivals across the atelier.

    Provides lifecycle management for festivals including
    creation, entry submission, voting, and conclusion.

    Usage:
        manager = FestivalManager()
        festival = manager.create("Winter Tales", "stories of the longest night")
        manager.enter(festival.id, "calligrapher", "haiku", "snow falls gently...")
        manager.vote(festival.id, "entry-abc123")
    """

    def __init__(self) -> None:
        self._festivals: dict[str, Festival] = {}

    def create(
        self,
        title: str,
        theme: str,
        *,
        description: str | None = None,
        duration_hours: int = 72,
        voting_hours: int = 24,
        season: Season | None = None,
        constraints: list[str] | None = None,
    ) -> Festival:
        """Create and register a new festival."""
        festival = Festival.create(
            title=title,
            theme=theme,
            description=description,
            duration_hours=duration_hours,
            voting_hours=voting_hours,
            season=season,
            constraints=constraints,
            start_now=True,
        )
        self._festivals[festival.id] = festival
        return festival

    def get(self, festival_id: str) -> Festival | None:
        """Get a festival by ID."""
        return self._festivals.get(festival_id)

    def list_festivals(
        self,
        status: FestivalStatus | None = None,
        season: Season | None = None,
    ) -> list[Festival]:
        """
        List festivals with optional filtering.

        Args:
            status: Filter by status
            season: Filter by season

        Returns:
            List of matching festivals
        """
        festivals = list(self._festivals.values())

        if status:
            festivals = [f for f in festivals if f.status == status]
        if season:
            festivals = [f for f in festivals if f.season == season]

        return sorted(festivals, key=lambda f: f.starts_at, reverse=True)

    def active(self) -> list[Festival]:
        """Get all active festivals."""
        return self.list_festivals(status=FestivalStatus.ACTIVE)

    def enter(
        self,
        festival_id: str,
        artisan: str,
        prompt: str,
        content: str,
        *,
        piece_id: str | None = None,
    ) -> FestivalEntry | None:
        """Submit an entry to a festival."""
        festival = self.get(festival_id)
        if not festival:
            return None
        return festival.enter(artisan, prompt, content, piece_id=piece_id)

    def vote(self, festival_id: str, entry_id: str, count: int = 1) -> bool:
        """Vote for an entry in a festival."""
        festival = self.get(festival_id)
        if not festival:
            return False
        return festival.vote(entry_id, count)

    def conclude(self, festival_id: str) -> dict[str, Any] | None:
        """Conclude a festival and get summary."""
        festival = self.get(festival_id)
        if not festival:
            return None
        return festival.conclude()

    def advance_all(self) -> list[str]:
        """
        Advance status for all festivals based on time.

        Returns:
            List of festival IDs that changed status
        """
        changed = []
        for festival in self._festivals.values():
            old_status = festival.status
            new_status = festival.advance_status()
            if old_status != new_status:
                changed.append(festival.id)
        return changed

    def suggest_theme(self, season: Season | None = None) -> str:
        """
        Suggest a theme for a new festival.

        Args:
            season: Season to base suggestion on (defaults to current)

        Returns:
            A suggested theme
        """
        import random

        season = season or Season.current()
        suggestions = season.theme_suggestions
        return random.choice(suggestions) if suggestions else "the creative spirit"

    def to_dict(self) -> dict[str, Any]:
        """Serialize all festivals."""
        return {
            "festivals": {fid: f.to_dict() for fid, f in self._festivals.items()},
            "active_count": len(self.active()),
            "total_count": len(self._festivals),
        }


# =============================================================================
# Module Singleton
# =============================================================================

_festival_manager: FestivalManager | None = None


def get_festival_manager() -> FestivalManager:
    """Get the global festival manager instance."""
    global _festival_manager
    if _festival_manager is None:
        _festival_manager = FestivalManager()
    return _festival_manager


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Festival",
    "FestivalEntry",
    "FestivalStatus",
    "FestivalManager",
    "Season",
    "get_festival_manager",
]
