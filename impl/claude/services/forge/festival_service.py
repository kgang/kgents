"""
Forge Festival Service: FestivalManager wrapper for seasonal creative events.

Wraps agents/forge/festival.py FestivalManager with service-level interface.
Owns domain semantics for Forge festivals:
- WHEN to hold festivals (seasonal, time-bounded)
- WHY to participate (community, recognition, creative prompts)
- HOW to curate (voting, exhibitions)

AGENTESE aspects exposed:
- world.forge.festival.list - List festivals
- world.forge.festival.create - Create festival
- world.forge.festival.enter - Enter festival
- world.forge.festival.vote - Vote for entry
- world.forge.festival.conclude - End festival

The Categorical View:
    Festival : Theme x Duration -> Collection[Piece]
    The festival is a functor from creative intent to curated collection.

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from agents.forge.festival import (
    Festival,
    FestivalEntry,
    FestivalManager,
    FestivalStatus,
    Season,
    get_festival_manager,
)


@dataclass
class FestivalEntryView:
    """View of a festival entry."""

    id: str
    festival_id: str
    artisan: str
    prompt: str
    content: str
    piece_id: str | None
    votes: int
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "festival_id": self.festival_id,
            "artisan": self.artisan,
            "prompt": self.prompt,
            "content": self.content[:200] + ("..." if len(self.content) > 200 else ""),
            "piece_id": self.piece_id,
            "votes": self.votes,
            "created_at": self.created_at,
        }

    def to_text(self) -> str:
        lines = [
            f"Entry: {self.id}",
            f"Artisan: {self.artisan}",
            f"Prompt: {self.prompt}",
            f"Votes: {self.votes}",
        ]
        content_preview = self.content[:80]
        if len(self.content) > 80:
            content_preview += "..."
        lines.append(f"Content: {content_preview}")
        return "\n".join(lines)


@dataclass
class FestivalView:
    """View of a festival."""

    id: str
    title: str
    theme: str
    description: str
    season: str
    status: str
    starts_at: str
    ends_at: str
    voting_ends_at: str | None
    entry_count: int
    is_accepting_entries: bool
    is_voting: bool
    time_remaining: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "theme": self.theme,
            "description": self.description,
            "season": self.season,
            "status": self.status,
            "starts_at": self.starts_at,
            "ends_at": self.ends_at,
            "voting_ends_at": self.voting_ends_at,
            "entry_count": self.entry_count,
            "is_accepting_entries": self.is_accepting_entries,
            "is_voting": self.is_voting,
            "time_remaining": self.time_remaining,
        }

    def to_text(self) -> str:
        status_icon = {
            "active": "[open]",
            "voting": "[voting]",
            "upcoming": "[upcoming]",
            "concluded": "[concluded]",
        }.get(self.status, f"[{self.status}]")

        lines = [
            f"Festival: {self.title} {status_icon}",
            f"Theme: {self.theme}",
            f"Season: {self.season}",
            f"Entries: {self.entry_count}",
        ]
        if self.time_remaining:
            lines.append(f"Time Remaining: {self.time_remaining}")
        return "\n".join(lines)


@dataclass
class FestivalSummaryView:
    """View of festival conclusion summary."""

    festival_id: str
    title: str
    theme: str
    total_entries: int
    total_votes: int
    participating_artisans: list[str]
    winners: list[FestivalEntryView]
    concluded_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "festival_id": self.festival_id,
            "title": self.title,
            "theme": self.theme,
            "total_entries": self.total_entries,
            "total_votes": self.total_votes,
            "participating_artisans": self.participating_artisans,
            "winners": [w.to_dict() for w in self.winners],
            "concluded_at": self.concluded_at,
        }

    def to_text(self) -> str:
        lines = [
            f"Festival Concluded: {self.title}",
            f"Theme: {self.theme}",
            f"Total Entries: {self.total_entries}",
            f"Total Votes: {self.total_votes}",
            f"Participating Artisans: {len(self.participating_artisans)}",
            "",
            "Winners:",
        ]
        for i, w in enumerate(self.winners, 1):
            lines.append(f"  {i}. {w.artisan} ({w.votes} votes)")
        return "\n".join(lines)


def _entry_to_view(entry: FestivalEntry) -> FestivalEntryView:
    """Convert FestivalEntry to FestivalEntryView."""
    return FestivalEntryView(
        id=entry.id,
        festival_id=entry.festival_id,
        artisan=entry.artisan,
        prompt=entry.prompt,
        content=entry.content,
        piece_id=entry.piece_id,
        votes=entry.votes,
        created_at=entry.created_at.isoformat(),
    )


def _festival_to_view(festival: Festival) -> FestivalView:
    """Convert Festival to FestivalView."""
    time_remaining = None
    if festival.time_remaining:
        td = festival.time_remaining
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        time_remaining = f"{hours}h {minutes}m"

    return FestivalView(
        id=festival.id,
        title=festival.title,
        theme=festival.theme,
        description=festival.description,
        season=festival.season.value,
        status=festival.status.value,
        starts_at=festival.starts_at.isoformat(),
        ends_at=festival.ends_at.isoformat(),
        voting_ends_at=festival.voting_ends_at.isoformat()
        if festival.voting_ends_at
        else None,
        entry_count=len(festival.entries),
        is_accepting_entries=festival.is_accepting_entries,
        is_voting=festival.is_voting,
        time_remaining=time_remaining,
    )


class ForgeFestivalService:
    """
    Service layer for Forge festivals.

    Wraps FestivalManager with service-level methods for:
    - Festival creation and lifecycle
    - Entry submission
    - Voting
    - Leaderboard and conclusion

    Usage:
        service = ForgeFestivalService.create()

        # Create a festival
        festival = service.create_festival(
            title="Winter Solstice",
            theme="longest night, first light",
        )

        # Submit an entry
        entry = service.enter(
            festival_id=festival.id,
            artisan="calligrapher",
            prompt="a haiku about waiting",
            content="snow falls gently...",
        )

        # Vote
        service.vote(festival.id, entry.id)
    """

    def __init__(self, manager: FestivalManager) -> None:
        """
        Initialize with a FestivalManager.

        Args:
            manager: The underlying festival manager
        """
        self._manager = manager

    @classmethod
    def create(cls) -> "ForgeFestivalService":
        """
        Factory method to create a new festival service.

        Returns:
            New ForgeFestivalService instance
        """
        manager = FestivalManager()
        return cls(manager)

    @classmethod
    def from_global(cls) -> "ForgeFestivalService":
        """
        Create service using the global festival manager singleton.

        Returns:
            ForgeFestivalService using global manager
        """
        return cls(get_festival_manager())

    # === Festival Operations ===

    def create_festival(
        self,
        title: str,
        theme: str,
        description: str | None = None,
        duration_hours: int = 72,
        voting_hours: int = 24,
        season: str | Season | None = None,
        constraints: list[str] | None = None,
    ) -> FestivalView:
        """
        Create a new festival.

        Args:
            title: Festival name
            theme: The creative theme/prompt
            description: Optional longer description
            duration_hours: How long entries are accepted
            voting_hours: How long voting lasts
            season: Seasonal association
            constraints: Optional creative constraints

        Returns:
            FestivalView of the created festival
        """
        # Parse season
        if isinstance(season, str):
            season_enum = Season(season)
        else:
            season_enum = season

        festival = self._manager.create(
            title=title,
            theme=theme,
            description=description,
            duration_hours=duration_hours,
            voting_hours=voting_hours,
            season=season_enum,
            constraints=constraints,
        )
        return _festival_to_view(festival)

    def get_festival(self, festival_id: str) -> FestivalView | None:
        """
        Get a festival by ID.

        Args:
            festival_id: ID of the festival

        Returns:
            FestivalView or None if not found
        """
        festival = self._manager.get(festival_id)
        if festival is None:
            return None
        return _festival_to_view(festival)

    def list_festivals(
        self,
        status: str | FestivalStatus | None = None,
        season: str | Season | None = None,
    ) -> list[FestivalView]:
        """
        List festivals with optional filtering.

        Args:
            status: Filter by status
            season: Filter by season

        Returns:
            List of FestivalView
        """
        # Parse filters
        status_enum = None
        if isinstance(status, str):
            status_enum = FestivalStatus(status)
        elif status is not None:
            status_enum = status

        season_enum = None
        if isinstance(season, str):
            season_enum = Season(season)
        elif season is not None:
            season_enum = season

        festivals = self._manager.list_festivals(
            status=status_enum,
            season=season_enum,
        )
        return [_festival_to_view(f) for f in festivals]

    def active_festivals(self) -> list[FestivalView]:
        """
        Get all active festivals.

        Returns:
            List of active FestivalView
        """
        return [_festival_to_view(f) for f in self._manager.active()]

    # === Entry Operations ===

    def enter(
        self,
        festival_id: str,
        artisan: str,
        prompt: str,
        content: str,
        piece_id: str | None = None,
    ) -> FestivalEntryView | None:
        """
        Submit an entry to a festival.

        Args:
            festival_id: ID of the festival
            artisan: Name of artisan/creator
            prompt: The specific prompt for this entry
            content: The created content
            piece_id: Optional link to a Piece

        Returns:
            FestivalEntryView or None if entry failed
        """
        entry = self._manager.enter(
            festival_id=festival_id,
            artisan=artisan,
            prompt=prompt,
            content=content,
            piece_id=piece_id,
        )
        if entry is None:
            return None
        return _entry_to_view(entry)

    def get_entries(self, festival_id: str) -> list[FestivalEntryView]:
        """
        Get all entries for a festival.

        Args:
            festival_id: ID of the festival

        Returns:
            List of FestivalEntryView
        """
        festival = self._manager.get(festival_id)
        if festival is None:
            return []
        return [_entry_to_view(e) for e in festival.entries]

    def get_entry(
        self,
        festival_id: str,
        entry_id: str,
    ) -> FestivalEntryView | None:
        """
        Get a specific entry.

        Args:
            festival_id: ID of the festival
            entry_id: ID of the entry

        Returns:
            FestivalEntryView or None if not found
        """
        festival = self._manager.get(festival_id)
        if festival is None:
            return None
        entry = festival.get_entry(entry_id)
        if entry is None:
            return None
        return _entry_to_view(entry)

    # === Voting Operations ===

    def vote(
        self,
        festival_id: str,
        entry_id: str,
        count: int = 1,
    ) -> bool:
        """
        Cast votes for an entry.

        Args:
            festival_id: ID of the festival
            entry_id: ID of the entry
            count: Number of votes

        Returns:
            True if vote was recorded
        """
        return self._manager.vote(festival_id, entry_id, count)

    def get_leaderboard(
        self,
        festival_id: str,
        limit: int = 10,
    ) -> list[FestivalEntryView]:
        """
        Get top entries by votes.

        Args:
            festival_id: ID of the festival
            limit: Maximum entries to return

        Returns:
            List of FestivalEntryView sorted by votes
        """
        festival = self._manager.get(festival_id)
        if festival is None:
            return []
        return [_entry_to_view(e) for e in festival.get_leaderboard(limit)]

    # === Lifecycle Operations ===

    def conclude(self, festival_id: str) -> FestivalSummaryView | None:
        """
        Conclude a festival and generate summary.

        Args:
            festival_id: ID of the festival

        Returns:
            FestivalSummaryView or None if festival not found
        """
        summary = self._manager.conclude(festival_id)
        if summary is None:
            return None

        winners = []
        for w in summary.get("winners", []):
            winners.append(
                FestivalEntryView(
                    id=w["id"],
                    festival_id=w["festival_id"],
                    artisan=w["artisan"],
                    prompt=w["prompt"],
                    content=w["content"],
                    piece_id=w.get("piece_id"),
                    votes=w["votes"],
                    created_at=w["created_at"],
                )
            )

        return FestivalSummaryView(
            festival_id=summary["festival_id"],
            title=summary["title"],
            theme=summary["theme"],
            total_entries=summary["total_entries"],
            total_votes=summary["total_votes"],
            participating_artisans=summary["participating_artisans"],
            winners=winners,
            concluded_at=summary["concluded_at"],
        )

    def advance_all(self) -> list[str]:
        """
        Advance status for all festivals based on time.

        Returns:
            List of festival IDs that changed status
        """
        return self._manager.advance_all()

    # === Helpers ===

    def suggest_theme(
        self,
        season: str | Season | None = None,
    ) -> str:
        """
        Suggest a theme for a new festival.

        Args:
            season: Season to base suggestion on

        Returns:
            A suggested theme
        """
        season_enum = None
        if isinstance(season, str):
            season_enum = Season(season)
        elif season is not None:
            season_enum = season

        return self._manager.suggest_theme(season_enum)

    def current_season(self) -> str:
        """
        Get the current season.

        Returns:
            Current season value
        """
        return Season.current().value

    @property
    def manager(self) -> FestivalManager:
        """Access the underlying festival manager."""
        return self._manager


__all__ = [
    "ForgeFestivalService",
    "FestivalView",
    "FestivalEntryView",
    "FestivalSummaryView",
]
