"""
PersonaGarden: The soul's memory garden.

K-gent's PersonaGarden provides persistent storage for persona patterns,
preferences, and observed behaviors using the garden metaphor.

Integration:
    - Wraps D-gent's MemoryGarden for persistence
    - Bridges with HypnagogicCycle patterns
    - Provides `kgents soul garden` interface

Lifecycle:
    SEED     - Newly observed pattern, low confidence
    SAPLING  - Pattern seen multiple times, growing
    TREE     - Established pattern, high confidence
    FLOWER   - Peak insight, ready to influence dialogue
    COMPOST  - Deprecated pattern, recycled into nutrients

Philosophy:
    "Data management should feel like gardening, not filing."

Usage:
    from agents.k.garden import PersonaGarden

    garden = PersonaGarden()
    await garden.plant_preference("Direct communication style")
    await garden.nurture_pattern("categorical", evidence="Used in 5 dialogues")
    stats = await garden.stats()
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .hypnagogia import HypnagogicCycle, Pattern


# =============================================================================
# Types
# =============================================================================


class EntryType(str, Enum):
    """Types of entries in the persona garden."""

    PREFERENCE = "preference"  # Explicit preference (from user)
    PATTERN = "pattern"  # Observed pattern (from hypnagogia)
    VALUE = "value"  # Core value (from eigenvectors)
    BEHAVIOR = "behavior"  # Behavioral tendency
    INSIGHT = "insight"  # Harvested insight


class GardenLifecycle(str, Enum):
    """Lifecycle stages for garden entries."""

    SEED = "seed"  # New, unvalidated
    SAPLING = "sapling"  # Growing, partially validated
    TREE = "tree"  # Established, high confidence
    FLOWER = "flower"  # Peak insight, ready for harvest
    COMPOST = "compost"  # Deprecated, being recycled


class GardenSeason(str, Enum):
    """Seasonal rhythms for the garden.

    Spring: Planting focus - auto-plant new patterns readily
    Summer: Growth focus - nurturing and evidence gathering
    Autumn: Harvest focus - promote patterns to flowers, reap insights
    Winter: Composting focus - decay stale patterns, prune aggressively
    """

    SPRING = "spring"  # Planting - new patterns welcomed
    SUMMER = "summer"  # Growth - nurturing focus
    AUTUMN = "autumn"  # Harvest - promote and reap
    WINTER = "winter"  # Composting - decay and prune


@dataclass
class GardenEntry:
    """An entry in the persona garden."""

    id: str
    content: str
    entry_type: EntryType
    lifecycle: GardenLifecycle = GardenLifecycle.SEED
    confidence: float = 0.3
    source: str = "manual"  # manual, hypnagogia, dialogue, etc.

    # Timestamps
    planted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_nurtured: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Evidence tracking
    evidence: list[str] = field(default_factory=list)
    occurrences: int = 1

    # Metadata
    tags: list[str] = field(default_factory=list)
    eigenvector_affinities: dict[str, float] = field(default_factory=dict)

    @property
    def age_days(self) -> float:
        """Age since planting in days."""
        delta = datetime.now(timezone.utc) - self.planted_at
        return delta.total_seconds() / 86400

    @property
    def staleness_days(self) -> float:
        """Days since last nurturing."""
        delta = datetime.now(timezone.utc) - self.last_nurtured
        return delta.total_seconds() / 86400

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "entry_type": self.entry_type.value,
            "lifecycle": self.lifecycle.value,
            "confidence": self.confidence,
            "source": self.source,
            "planted_at": self.planted_at.isoformat(),
            "last_nurtured": self.last_nurtured.isoformat(),
            "evidence": self.evidence,
            "occurrences": self.occurrences,
            "tags": self.tags,
            "eigenvector_affinities": self.eigenvector_affinities,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GardenEntry":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            entry_type=EntryType(data["entry_type"]),
            lifecycle=GardenLifecycle(data["lifecycle"]),
            confidence=data.get("confidence", 0.3),
            source=data.get("source", "manual"),
            planted_at=datetime.fromisoformat(data["planted_at"]),
            last_nurtured=datetime.fromisoformat(data["last_nurtured"]),
            evidence=data.get("evidence", []),
            occurrences=data.get("occurrences", 1),
            tags=data.get("tags", []),
            eigenvector_affinities=data.get("eigenvector_affinities", {}),
        )


@dataclass
class GardenStats:
    """Statistics about the persona garden."""

    total_entries: int
    by_type: dict[str, int]
    by_lifecycle: dict[str, int]
    average_confidence: float
    total_evidence: int
    oldest_entry_days: float
    newest_entry_days: float
    current_season: GardenSeason = GardenSeason.SUMMER
    auto_planted_count: int = 0  # Patterns auto-planted from dialogue


@dataclass
class SeasonConfig:
    """Configuration for seasonal behaviors."""

    # Thresholds for auto-planting (lower = more planting)
    auto_plant_threshold: float = 0.5  # Default confidence threshold

    # Decay rates (per day)
    staleness_decay_rate: float = 0.01  # Confidence decay per day of staleness

    # Season-specific modifiers
    spring_plant_boost: float = 0.2  # Extra confidence for spring plantings
    winter_decay_multiplier: float = 2.0  # Faster decay in winter

    # Promotion thresholds for harvest
    autumn_promote_threshold: float = 0.7  # Lower threshold for autumn promotion

    @classmethod
    def for_season(cls, season: GardenSeason) -> "SeasonConfig":
        """Get config optimized for a season."""
        base = cls()
        if season == GardenSeason.SPRING:
            base.auto_plant_threshold = 0.3  # Plant more readily
        elif season == GardenSeason.AUTUMN:
            base.autumn_promote_threshold = 0.65  # Promote more readily
        elif season == GardenSeason.WINTER:
            base.staleness_decay_rate = 0.02  # Faster decay
        return base


# =============================================================================
# PersonaGarden
# =============================================================================


class PersonaGarden:
    """
    The soul's memory garden.

    Stores and manages persona patterns, preferences, and insights using
    the garden metaphor. Provides persistence to ~/.kgents/garden/.

    Example:
        >>> garden = PersonaGarden()
        >>>
        >>> # Plant a preference (explicit)
        >>> await garden.plant(
        ...     content="Prefer concise communication",
        ...     entry_type=EntryType.PREFERENCE,
        ...     source="manual"
        ... )
        >>>
        >>> # Get stats
        >>> stats = await garden.stats()
        >>> print(f"Total entries: {stats.total_entries}")
        >>>
        >>> # Format for display
        >>> print(garden.format_summary())
    """

    def __init__(
        self,
        storage_path: Optional[Path] = None,
        auto_save: bool = True,
        season: Optional[GardenSeason] = None,
    ) -> None:
        """
        Initialize persona garden.

        Args:
            storage_path: Path to store garden data. Defaults to ~/.kgents/garden/
            auto_save: Automatically save after modifications
            season: Current season (defaults to auto-detect based on month)
        """
        if storage_path is None:
            storage_path = Path.home() / ".kgents" / "garden"
        self._storage_path = storage_path
        self._auto_save = auto_save

        # Season tracking
        self._season = season or self._detect_season()
        self._season_config = SeasonConfig.for_season(self._season)

        # Entry storage
        self._entries: dict[str, GardenEntry] = {}
        self._entry_counter = 0

        # Auto-plant tracking
        self._auto_planted_count = 0

        # Load existing data
        self._load()

    def _detect_season(self) -> GardenSeason:
        """Detect season based on current month."""
        month = datetime.now().month
        if month in (3, 4, 5):
            return GardenSeason.SPRING
        elif month in (6, 7, 8):
            return GardenSeason.SUMMER
        elif month in (9, 10, 11):
            return GardenSeason.AUTUMN
        else:
            return GardenSeason.WINTER

    @property
    def season(self) -> GardenSeason:
        """Get current garden season."""
        return self._season

    @season.setter
    def season(self, value: GardenSeason) -> None:
        """Set garden season and update config."""
        self._season = value
        self._season_config = SeasonConfig.for_season(value)

    @property
    def storage_path(self) -> Path:
        """Get storage path."""
        return self._storage_path

    @property
    def entries(self) -> dict[str, GardenEntry]:
        """Get all entries (copy)."""
        return self._entries.copy()

    # ─────────────────────────────────────────────────────────────────────────
    # Planting
    # ─────────────────────────────────────────────────────────────────────────

    async def plant(
        self,
        content: str,
        entry_type: EntryType,
        source: str = "manual",
        confidence: float = 0.3,
        tags: Optional[list[str]] = None,
        eigenvector_affinities: Optional[dict[str, float]] = None,
    ) -> GardenEntry:
        """
        Plant a new entry in the garden.

        Args:
            content: The content of the entry
            entry_type: Type of entry (preference, pattern, etc.)
            source: Source of the entry (manual, hypnagogia, etc.)
            confidence: Initial confidence (0.0-1.0)
            tags: Optional tags for categorization
            eigenvector_affinities: Optional eigenvector connections

        Returns:
            The planted GardenEntry
        """
        self._entry_counter += 1
        entry_id = f"{entry_type.value}_{self._entry_counter}_{int(datetime.now().timestamp())}"

        entry = GardenEntry(
            id=entry_id,
            content=content,
            entry_type=entry_type,
            lifecycle=self._confidence_to_lifecycle(confidence),
            confidence=confidence,
            source=source,
            tags=tags or [],
            eigenvector_affinities=eigenvector_affinities or {},
        )

        self._entries[entry_id] = entry
        self._save_if_auto()

        return entry

    async def plant_preference(
        self,
        content: str,
        confidence: float = 0.5,
        tags: Optional[list[str]] = None,
    ) -> GardenEntry:
        """Convenience method to plant a preference."""
        return await self.plant(
            content=content,
            entry_type=EntryType.PREFERENCE,
            source="manual",
            confidence=confidence,
            tags=tags,
        )

    async def plant_pattern(
        self,
        content: str,
        source: str = "hypnagogia",
        confidence: float = 0.3,
        eigenvector_affinities: Optional[dict[str, float]] = None,
    ) -> GardenEntry:
        """Convenience method to plant a pattern."""
        return await self.plant(
            content=content,
            entry_type=EntryType.PATTERN,
            source=source,
            confidence=confidence,
            eigenvector_affinities=eigenvector_affinities,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Nurturing
    # ─────────────────────────────────────────────────────────────────────────

    async def nurture(
        self,
        entry_id: str,
        evidence: str,
        confidence_boost: float = 0.05,
    ) -> Optional[GardenEntry]:
        """
        Nurture an entry with evidence.

        Args:
            entry_id: ID of entry to nurture
            evidence: Evidence supporting the entry
            confidence_boost: How much to boost confidence

        Returns:
            Updated entry, or None if not found
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            return None

        if entry.lifecycle == GardenLifecycle.COMPOST:
            return entry  # Cannot nurture composted entries

        # Add evidence
        entry.evidence.append(evidence)
        entry.occurrences += 1
        entry.last_nurtured = datetime.now(timezone.utc)

        # Boost confidence
        entry.confidence = min(1.0, entry.confidence + confidence_boost)

        # Update lifecycle based on confidence
        entry.lifecycle = self._confidence_to_lifecycle(entry.confidence)

        self._save_if_auto()
        return entry

    # ─────────────────────────────────────────────────────────────────────────
    # Querying
    # ─────────────────────────────────────────────────────────────────────────

    async def get(self, entry_id: str) -> Optional[GardenEntry]:
        """Get entry by ID."""
        return self._entries.get(entry_id)

    async def list_by_type(self, entry_type: EntryType) -> list[GardenEntry]:
        """List entries by type."""
        return [e for e in self._entries.values() if e.entry_type == entry_type]

    async def list_by_lifecycle(self, lifecycle: GardenLifecycle) -> list[GardenEntry]:
        """List entries by lifecycle stage."""
        return [e for e in self._entries.values() if e.lifecycle == lifecycle]

    async def seeds(self) -> list[GardenEntry]:
        """Get all seeds."""
        return await self.list_by_lifecycle(GardenLifecycle.SEED)

    async def saplings(self) -> list[GardenEntry]:
        """Get all saplings."""
        return await self.list_by_lifecycle(GardenLifecycle.SAPLING)

    async def trees(self) -> list[GardenEntry]:
        """Get all trees (established patterns)."""
        return await self.list_by_lifecycle(GardenLifecycle.TREE)

    async def flowers(self) -> list[GardenEntry]:
        """Get all flowers (peak insights)."""
        return await self.list_by_lifecycle(GardenLifecycle.FLOWER)

    async def preferences(self) -> list[GardenEntry]:
        """Get all preferences."""
        return await self.list_by_type(EntryType.PREFERENCE)

    async def patterns(self) -> list[GardenEntry]:
        """Get all patterns."""
        return await self.list_by_type(EntryType.PATTERN)

    # ─────────────────────────────────────────────────────────────────────────
    # Composting
    # ─────────────────────────────────────────────────────────────────────────

    async def compost(self, entry_id: str) -> Optional[GardenEntry]:
        """
        Compost an entry (mark as deprecated).

        Args:
            entry_id: ID of entry to compost

        Returns:
            Composted entry, or None if not found
        """
        entry = self._entries.get(entry_id)
        if entry is None:
            return None

        entry.lifecycle = GardenLifecycle.COMPOST
        entry.last_nurtured = datetime.now(timezone.utc)

        self._save_if_auto()
        return entry

    async def prune_stale(self, days_threshold: int = 30) -> list[GardenEntry]:
        """
        Compost entries that haven't been nurtured recently.

        Args:
            days_threshold: Days of staleness before composting

        Returns:
            List of composted entries
        """
        composted: list[GardenEntry] = []

        for entry in self._entries.values():
            if entry.lifecycle != GardenLifecycle.COMPOST and entry.staleness_days > days_threshold:
                entry.lifecycle = GardenLifecycle.COMPOST
                composted.append(entry)

        if composted:
            self._save_if_auto()

        return composted

    async def staleness_decay(self) -> list[tuple[GardenEntry, float]]:
        """
        Apply natural confidence decay to stale entries.

        Confidence decays based on staleness_days * decay_rate.
        Winter season accelerates decay. Entries that decay below
        0.1 confidence are automatically composted.

        Returns:
            List of (entry, decay_amount) tuples for entries that decayed
        """
        decayed: list[tuple[GardenEntry, float]] = []
        decay_rate = self._season_config.staleness_decay_rate

        # Winter accelerates decay
        if self._season == GardenSeason.WINTER:
            decay_rate *= self._season_config.winter_decay_multiplier

        for entry in self._entries.values():
            if entry.lifecycle == GardenLifecycle.COMPOST:
                continue

            # Calculate decay based on staleness
            staleness = entry.staleness_days
            if staleness > 1:  # Only decay after 1 day of staleness
                decay_amount = (staleness - 1) * decay_rate
                entry.confidence = max(0.0, entry.confidence - decay_amount)

                if decay_amount > 0.001:  # Meaningful decay
                    decayed.append((entry, decay_amount))

                # Auto-compost if confidence drops too low
                if entry.confidence < 0.1:
                    entry.lifecycle = GardenLifecycle.COMPOST
                else:
                    # Update lifecycle based on new confidence
                    entry.lifecycle = self._confidence_to_lifecycle(entry.confidence)

        if decayed:
            self._save_if_auto()

        return decayed

    async def cross_pollinate(
        self,
        other: "PersonaGarden",
        similarity_threshold: float = 0.8,
    ) -> list[GardenEntry]:
        """
        Cross-pollinate patterns from another garden.

        Merges similar patterns (boosting confidence) and imports
        new patterns that don't exist in this garden.

        Args:
            other: Another PersonaGarden to cross-pollinate from
            similarity_threshold: How similar patterns must be to merge (0-1)

        Returns:
            List of newly imported entries
        """
        imported: list[GardenEntry] = []

        for other_entry in other._entries.values():
            if other_entry.lifecycle == GardenLifecycle.COMPOST:
                continue

            # Check for similar existing entry
            similar = self._find_similar_entry(other_entry.content, similarity_threshold)

            if similar:
                # Merge: boost confidence, combine evidence
                similar.confidence = min(
                    1.0,
                    similar.confidence + (other_entry.confidence * 0.3),
                )
                similar.evidence.extend(other_entry.evidence[-3:])  # Last 3 evidence
                similar.occurrences += other_entry.occurrences
                similar.last_nurtured = datetime.now(timezone.utc)
                similar.lifecycle = self._confidence_to_lifecycle(similar.confidence)
            else:
                # Import as new entry (with reduced confidence)
                new_entry = await self.plant(
                    content=other_entry.content,
                    entry_type=other_entry.entry_type,
                    source="cross_pollination",
                    confidence=other_entry.confidence * 0.5,  # Halved for imports
                    tags=other_entry.tags + ["imported"],
                    eigenvector_affinities=other_entry.eigenvector_affinities,
                )
                imported.append(new_entry)

        if imported:
            self._save_if_auto()

        return imported

    def _find_similar_entry(self, content: str, threshold: float) -> Optional[GardenEntry]:
        """Find an entry with similar content.

        Returns None if content is empty or whitespace-only.
        """
        if not content or not content.strip():
            return None

        content_words = set(content.lower().split())

        for entry in self._entries.values():
            if entry.lifecycle == GardenLifecycle.COMPOST:
                continue

            entry_words = set(entry.content.lower().split())

            # Jaccard similarity
            if not content_words or not entry_words:
                continue

            intersection = len(content_words & entry_words)
            union = len(content_words | entry_words)
            similarity = intersection / union if union > 0 else 0

            if similarity >= threshold:
                return entry

        return None

    async def auto_plant_from_dialogue(
        self,
        message: str,
        response: str,
        detected_patterns: Optional[list[str]] = None,
        eigenvector_affinities: Optional[dict[str, float]] = None,
    ) -> list[GardenEntry]:
        """
        Auto-plant patterns detected from dialogue.

        This is the feedback loop: every dialogue can nurture existing
        patterns or plant new ones based on what was discussed.

        Args:
            message: The user's message
            response: K-gent's response
            detected_patterns: Optional list of detected patterns (from LLM)
            eigenvector_affinities: Optional eigenvector connections

        Returns:
            List of entries that were planted or nurtured
        """
        affected: list[GardenEntry] = []

        # Season affects auto-planting threshold
        threshold = self._season_config.auto_plant_threshold
        base_confidence = 0.25

        # Spring boost for new plantings
        if self._season == GardenSeason.SPRING:
            base_confidence += self._season_config.spring_plant_boost

        # If explicit patterns detected, plant them
        if detected_patterns:
            for pattern in detected_patterns:
                # Check if similar pattern exists
                similar = self._find_similar_entry(pattern, 0.7)
                if similar:
                    # Nurture existing
                    await self.nurture(
                        similar.id,
                        f"Dialogue: {message[:50]}",
                        confidence_boost=0.05,
                    )
                    affected.append(similar)
                else:
                    # Plant new
                    entry = await self.plant_pattern(
                        content=pattern,
                        source="dialogue",
                        confidence=base_confidence,
                        eigenvector_affinities=eigenvector_affinities,
                    )
                    self._auto_planted_count += 1
                    affected.append(entry)

        # Also check for implicit patterns in the dialogue
        implicit = self._detect_implicit_patterns(message, response)
        for pattern_content, pattern_confidence in implicit:
            if pattern_confidence >= threshold:
                similar = self._find_similar_entry(pattern_content, 0.8)
                if similar:
                    await self.nurture(
                        similar.id,
                        "Implicit in dialogue",
                        confidence_boost=0.03,
                    )
                    affected.append(similar)
                elif pattern_confidence >= threshold + 0.1:  # Higher bar for implicit
                    entry = await self.plant_pattern(
                        content=pattern_content,
                        source="dialogue_implicit",
                        confidence=base_confidence * 0.8,  # Lower confidence
                    )
                    self._auto_planted_count += 1
                    affected.append(entry)

        return affected

    def _detect_implicit_patterns(self, message: str, response: str) -> list[tuple[str, float]]:
        """
        Detect implicit patterns from dialogue content.

        Returns list of (pattern_description, confidence) tuples.
        """
        patterns: list[tuple[str, float]] = []
        combined = f"{message} {response}".lower()

        # Pattern indicators with confidence
        indicators = [
            ("always", "Consistent behavior pattern", 0.6),
            ("prefer", "Preference pattern", 0.5),
            ("usually", "Habitual pattern", 0.5),
            ("tend to", "Tendency pattern", 0.4),
            ("whenever", "Conditional behavior", 0.4),
            ("important to me", "Core value", 0.7),
            ("i believe", "Belief pattern", 0.6),
            ("my approach", "Methodology pattern", 0.5),
        ]

        for indicator, pattern_type, base_conf in indicators:
            if indicator in combined:
                # Extract surrounding context (simplified)
                idx = combined.find(indicator)
                context = combined[max(0, idx - 30) : idx + 50]
                patterns.append((f"{pattern_type}: {context.strip()}", base_conf))

        return patterns[:3]  # Limit to top 3

    # ─────────────────────────────────────────────────────────────────────────
    # Hypnagogia Integration
    # ─────────────────────────────────────────────────────────────────────────

    async def sync_from_hypnagogia(self, cycle: "HypnagogicCycle") -> int:
        """
        Sync patterns from HypnagogicCycle.

        Args:
            cycle: The HypnagogicCycle to sync from

        Returns:
            Number of patterns synced
        """
        synced = 0

        for pattern_id, pattern in cycle.patterns.items():
            # Check if already in garden
            existing = None
            for entry in self._entries.values():
                if entry.content == pattern.content:
                    existing = entry
                    break

            if existing:
                # Update existing entry
                existing.occurrences = max(existing.occurrences, pattern.occurrences)
                existing.last_nurtured = datetime.now(timezone.utc)
                existing.evidence = list(set(existing.evidence + pattern.evidence))
            else:
                # Create new entry
                confidence = self._pattern_maturity_to_confidence(pattern.maturity.value)
                await self.plant_pattern(
                    content=pattern.content,
                    source="hypnagogia",
                    confidence=confidence,
                    eigenvector_affinities=pattern.eigenvector_affinities,
                )
                synced += 1

        if synced > 0:
            self._save_if_auto()

        return synced

    # ─────────────────────────────────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────────────────────────────────

    async def stats(self) -> GardenStats:
        """Get garden statistics."""
        entries = list(self._entries.values())

        if not entries:
            return GardenStats(
                total_entries=0,
                by_type={},
                by_lifecycle={},
                average_confidence=0.0,
                total_evidence=0,
                oldest_entry_days=0.0,
                newest_entry_days=0.0,
                current_season=self._season,
                auto_planted_count=self._auto_planted_count,
            )

        by_type: dict[str, int] = {}
        by_lifecycle: dict[str, int] = {}

        for entry in entries:
            by_type[entry.entry_type.value] = by_type.get(entry.entry_type.value, 0) + 1
            by_lifecycle[entry.lifecycle.value] = by_lifecycle.get(entry.lifecycle.value, 0) + 1

        avg_confidence = sum(e.confidence for e in entries) / len(entries)
        total_evidence = sum(len(e.evidence) for e in entries)

        ages = [e.age_days for e in entries]

        return GardenStats(
            total_entries=len(entries),
            by_type=by_type,
            by_lifecycle=by_lifecycle,
            average_confidence=avg_confidence,
            total_evidence=total_evidence,
            oldest_entry_days=max(ages),
            newest_entry_days=min(ages),
            current_season=self._season,
            auto_planted_count=self._auto_planted_count,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Formatting
    # ─────────────────────────────────────────────────────────────────────────

    def format_summary(self) -> str:
        """Format garden summary for display."""
        entries = list(self._entries.values())

        if not entries:
            return "[GARDEN] Empty - no patterns planted yet"

        # Count by lifecycle
        by_lifecycle: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for entry in entries:
            by_lifecycle[entry.lifecycle.value] = by_lifecycle.get(entry.lifecycle.value, 0) + 1
            by_type[entry.entry_type.value] = by_type.get(entry.entry_type.value, 0) + 1

        lines = [
            "[GARDEN] PersonaGarden Summary",
            "",
            f"  Total entries: {len(entries)}",
            "",
            "  By lifecycle:",
        ]

        # Lifecycle icons
        lifecycle_icons = {
            "seed": ".",
            "sapling": "|",
            "tree": "T",
            "flower": "*",
            "compost": "~",
        }

        for lc in ["seed", "sapling", "tree", "flower", "compost"]:
            count = by_lifecycle.get(lc, 0)
            icon = lifecycle_icons.get(lc, " ")
            if count > 0:
                lines.append(f"    {icon} {lc}: {count}")

        lines.append("")
        lines.append("  By type:")
        for entry_type, count in sorted(by_type.items()):
            lines.append(f"    {entry_type}: {count}")

        # Show top trees
        trees = [e for e in entries if e.lifecycle == GardenLifecycle.TREE]
        if trees:
            lines.append("")
            lines.append("  Established patterns (trees):")
            for tree in sorted(trees, key=lambda t: -t.confidence)[:5]:
                lines.append(f"    T {tree.content[:50]} ({tree.confidence:.0%})")

        # Show recent seeds
        seeds = [e for e in entries if e.lifecycle == GardenLifecycle.SEED]
        if seeds:
            lines.append("")
            lines.append("  Recent seeds:")
            for seed in sorted(seeds, key=lambda s: s.planted_at, reverse=True)[:3]:
                lines.append(f"    . {seed.content[:50]}")

        return "\n".join(lines)

    def format_entry(self, entry: GardenEntry) -> str:
        """Format a single entry for display."""
        lifecycle_icons = {
            "seed": ".",
            "sapling": "|",
            "tree": "T",
            "flower": "*",
            "compost": "~",
        }
        icon = lifecycle_icons.get(entry.lifecycle.value, " ")

        lines = [
            f"{icon} [{entry.entry_type.value}] {entry.content}",
            f"  Confidence: {entry.confidence:.0%}",
            f"  Source: {entry.source}",
            f"  Age: {entry.age_days:.1f} days",
            f"  Evidence: {len(entry.evidence)} items",
        ]

        if entry.tags:
            lines.append(f"  Tags: {', '.join(entry.tags)}")

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────────────────
    # Persistence
    # ─────────────────────────────────────────────────────────────────────────

    def _save(self) -> None:
        """Save garden to disk."""
        self._storage_path.mkdir(parents=True, exist_ok=True)
        file_path = self._storage_path / "garden.json"

        data = {
            "version": 1,
            "entry_counter": self._entry_counter,
            "entries": {eid: e.to_dict() for eid, e in self._entries.items()},
        }

        # Atomic write
        temp_path = file_path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)
        temp_path.replace(file_path)

    def _load(self) -> None:
        """Load garden from disk."""
        file_path = self._storage_path / "garden.json"

        if not file_path.exists():
            return

        try:
            with open(file_path) as f:
                data = json.load(f)

            self._entry_counter = data.get("entry_counter", 0)

            for eid, entry_data in data.get("entries", {}).items():
                self._entries[eid] = GardenEntry.from_dict(entry_data)

        except (json.JSONDecodeError, KeyError) as e:
            # Corrupted file - start fresh
            import logging

            logging.getLogger(__name__).warning(f"Failed to load garden: {e}")

    def _save_if_auto(self) -> None:
        """Save if auto_save is enabled."""
        if self._auto_save:
            self._save()

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _confidence_to_lifecycle(self, confidence: float) -> GardenLifecycle:
        """Map confidence to lifecycle stage."""
        if confidence >= 0.9:
            return GardenLifecycle.FLOWER
        elif confidence >= 0.7:
            return GardenLifecycle.TREE
        elif confidence >= 0.4:
            return GardenLifecycle.SAPLING
        else:
            return GardenLifecycle.SEED

    def _pattern_maturity_to_confidence(self, maturity: str) -> float:
        """Map HypnagogicCycle pattern maturity to confidence."""
        maturity_confidence = {
            "seed": 0.3,
            "sapling": 0.5,
            "tree": 0.8,
            "compost": 0.1,
        }
        return maturity_confidence.get(maturity, 0.3)


# =============================================================================
# Factory Functions
# =============================================================================


# Module-level singleton
_garden_instance: Optional[PersonaGarden] = None


def get_garden() -> PersonaGarden:
    """Get or create the global PersonaGarden instance."""
    global _garden_instance
    if _garden_instance is None:
        _garden_instance = PersonaGarden()
    return _garden_instance


def set_garden(garden: PersonaGarden) -> None:
    """Set the global PersonaGarden instance."""
    global _garden_instance
    _garden_instance = garden


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "EntryType",
    "GardenLifecycle",
    "GardenSeason",
    "GardenEntry",
    "GardenStats",
    "SeasonConfig",
    # The Garden
    "PersonaGarden",
    # Factories
    "get_garden",
    "set_garden",
]
