"""
Obsidian Pattern Witness - W-gent for observing behavioral patterns.

This module observes actual usage patterns in an Obsidian vault,
providing the "Antithesis" to the extracted "Thesis" (principles).

Observation Strategies:
1. Structural Analysis - Link density, orphan notes, folder structure
2. Temporal Analysis - Update frequency, staleness, daily note patterns
3. Content Analysis - Note length, reflection depth, tag usage

The Witness is read-only and non-judgmental—it only observes.
Judgment happens in the Tension detection phase.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator

from ..types import MirrorConfig, PatternObservation, PatternType


@dataclass
class WitnessResult:
    """Result of pattern observation."""

    observations: list[PatternObservation]
    files_analyzed: int
    total_notes: int
    observation_duration_seconds: float
    errors: list[str]


@dataclass
class NoteMetadata:
    """Metadata about a single note."""

    path: Path
    title: str
    content: str
    word_count: int
    char_count: int
    outgoing_links: list[str]
    incoming_links: list[str]  # Populated during analysis
    tags: list[str]
    created_at: datetime | None
    modified_at: datetime | None
    is_daily_note: bool = False


class ObsidianPatternWitness:
    """
    W-gent for observing behavioral patterns in Obsidian vaults.

    The Witness observes without judgment:
    - What patterns exist in the vault?
    - How is the vault actually being used?
    - What do the metrics reveal about behavior?

    Category Theory:
      Witness: Vault → List[PatternObservation]
      This is a functor from the Obsidian category to the Ontic category.
    """

    def __init__(self, config: MirrorConfig | None = None):
        """Initialize witness with configuration."""
        self.config = config or MirrorConfig()

        # Compile patterns
        self._link_pattern = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
        self._tag_pattern = re.compile(r"#(\w+)")
        self._daily_patterns = [re.compile(p) for p in self.config.daily_note_patterns]

    def observe(self, vault_path: str | Path) -> WitnessResult:
        """
        Observe all patterns in an Obsidian vault.

        Args:
            vault_path: Path to the Obsidian vault root

        Returns:
            WitnessResult with all observed patterns
        """
        start_time = datetime.now()
        vault_path = Path(vault_path)

        if not vault_path.exists():
            return WitnessResult(
                observations=[],
                files_analyzed=0,
                total_notes=0,
                observation_duration_seconds=0.0,
                errors=[f"Vault path does not exist: {vault_path}"],
            )

        # First pass: collect all note metadata
        notes: list[NoteMetadata] = []
        errors: list[str] = []

        for md_file in self._iter_vault_files(vault_path):
            try:
                metadata = self._analyze_note(md_file)
                notes.append(metadata)
            except Exception as e:
                errors.append(f"Error analyzing {md_file}: {e}")

        if not notes:
            return WitnessResult(
                observations=[],
                files_analyzed=0,
                total_notes=0,
                observation_duration_seconds=(
                    datetime.now() - start_time
                ).total_seconds(),
                errors=errors or ["No notes found in vault"],
            )

        # Build backlink index
        self._build_backlink_index(notes)

        # Collect observations
        observations: list[PatternObservation] = []

        if self.config.observe_link_patterns:
            observations.extend(self._observe_link_patterns(notes))

        if self.config.observe_length_patterns:
            observations.extend(self._observe_length_patterns(notes))

        if self.config.observe_update_patterns:
            observations.extend(self._observe_update_patterns(notes))

        if self.config.observe_daily_notes:
            observations.extend(self._observe_daily_note_patterns(notes))

        # Additional structural observations
        observations.extend(self._observe_orphan_notes(notes))
        observations.extend(self._observe_tag_patterns(notes))

        duration = (datetime.now() - start_time).total_seconds()

        return WitnessResult(
            observations=observations,
            files_analyzed=len(notes),
            total_notes=len(notes),
            observation_duration_seconds=duration,
            errors=errors,
        )

    def _iter_vault_files(self, vault_path: Path) -> Iterator[Path]:
        """Iterate over all markdown files in the vault."""
        for ext in self.config.note_extensions:
            for md_file in vault_path.glob(f"**/*{ext}"):
                # Skip excluded folders
                if any(
                    excluded in md_file.parts
                    for excluded in self.config.excluded_folders
                ):
                    continue
                yield md_file

    def _analyze_note(self, file_path: Path) -> NoteMetadata:
        """Analyze a single note and extract metadata."""
        content = file_path.read_text(encoding="utf-8")

        # Extract title (first H1 or filename)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem

        # Count words
        words = re.findall(r"\b\w+\b", content)
        word_count = len(words)

        # Extract links
        links = self._link_pattern.findall(content)

        # Extract tags
        tags = self._tag_pattern.findall(content)

        # Get file times
        stat = file_path.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        # Created time not always available
        try:
            created_at = datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            created_at = modified_at

        # Check if daily note
        is_daily = any(p.search(file_path.stem) for p in self._daily_patterns)

        return NoteMetadata(
            path=file_path,
            title=title,
            content=content,
            word_count=word_count,
            char_count=len(content),
            outgoing_links=links,
            incoming_links=[],  # Populated later
            tags=tags,
            created_at=created_at,
            modified_at=modified_at,
            is_daily_note=is_daily,
        )

    def _build_backlink_index(self, notes: list[NoteMetadata]) -> None:
        """Build index of incoming links for each note."""
        # Create lookup by title/filename
        title_to_note: dict[str, NoteMetadata] = {}
        for note in notes:
            title_to_note[note.title.lower()] = note
            title_to_note[note.path.stem.lower()] = note

        # Populate incoming links
        for note in notes:
            for link in note.outgoing_links:
                link_lower = link.lower()
                if link_lower in title_to_note:
                    target = title_to_note[link_lower]
                    if note.path.stem not in target.incoming_links:
                        target.incoming_links.append(note.path.stem)

    def _observe_link_patterns(
        self, notes: list[NoteMetadata]
    ) -> list[PatternObservation]:
        """Observe link density patterns."""
        observations = []

        # Outgoing link statistics
        outgoing_counts = [len(n.outgoing_links) for n in notes]
        if outgoing_counts:
            avg_outgoing = statistics.mean(outgoing_counts)
            median_outgoing = statistics.median(outgoing_counts)

            observations.append(
                PatternObservation(
                    pattern_type=PatternType.LINK_DENSITY,
                    description="Average outgoing links per note",
                    value=round(avg_outgoing, 2),
                    sample_size=len(notes),
                    confidence=0.95,
                    metadata={
                        "median": median_outgoing,
                        "max": max(outgoing_counts),
                        "min": min(outgoing_counts),
                    },
                )
            )

        # Notes with zero outgoing links
        zero_outgoing = [n for n in notes if len(n.outgoing_links) == 0]
        if notes:
            pct_zero_links = len(zero_outgoing) / len(notes)
            observations.append(
                PatternObservation(
                    pattern_type=PatternType.CONNECTION_PATTERNS,
                    description="Percentage of notes with no outgoing links",
                    value=round(pct_zero_links * 100, 1),
                    sample_size=len(notes),
                    confidence=0.95,
                    examples=tuple(n.title for n in zero_outgoing[:5]),
                    metadata={"count": len(zero_outgoing)},
                )
            )

        return observations

    def _observe_length_patterns(
        self, notes: list[NoteMetadata]
    ) -> list[PatternObservation]:
        """Observe note length patterns."""
        observations = []

        word_counts = [n.word_count for n in notes]
        if word_counts:
            avg_words = statistics.mean(word_counts)
            median_words = statistics.median(word_counts)

            observations.append(
                PatternObservation(
                    pattern_type=PatternType.NOTE_LENGTH,
                    description="Average note length (words)",
                    value=round(avg_words, 0),
                    sample_size=len(notes),
                    confidence=0.95,
                    metadata={
                        "median": median_words,
                        "max": max(word_counts),
                        "min": min(word_counts),
                    },
                )
            )

            # Short notes (< 100 words)
            short_notes = [n for n in notes if n.word_count < 100]
            if notes:
                pct_short = len(short_notes) / len(notes)
                observations.append(
                    PatternObservation(
                        pattern_type=PatternType.NOTE_LENGTH,
                        description="Percentage of notes under 100 words",
                        value=round(pct_short * 100, 1),
                        sample_size=len(notes),
                        confidence=0.95,
                        examples=tuple(n.title for n in short_notes[:5]),
                        metadata={"threshold": 100, "count": len(short_notes)},
                    )
                )

        return observations

    def _observe_update_patterns(
        self, notes: list[NoteMetadata]
    ) -> list[PatternObservation]:
        """Observe update frequency patterns."""
        observations = []
        now = datetime.now()

        # Filter notes with valid modified times
        notes_with_dates = [n for n in notes if n.modified_at]
        if not notes_with_dates:
            return observations

        # Calculate ages in days
        ages = [(now - n.modified_at).days for n in notes_with_dates]
        avg_age = statistics.mean(ages)
        median_age = statistics.median(ages)

        observations.append(
            PatternObservation(
                pattern_type=PatternType.UPDATE_FREQUENCY,
                description="Average note age (days since last update)",
                value=round(avg_age, 0),
                sample_size=len(notes_with_dates),
                confidence=0.9,
                metadata={
                    "median": median_age,
                    "max": max(ages),
                    "min": min(ages),
                },
            )
        )

        # Stale notes (not updated in 90+ days)
        stale_threshold = 90
        stale_notes = [
            n for n in notes_with_dates if (now - n.modified_at).days > stale_threshold
        ]
        if notes_with_dates:
            pct_stale = len(stale_notes) / len(notes_with_dates)
            observations.append(
                PatternObservation(
                    pattern_type=PatternType.STALENESS,
                    description=f"Percentage of notes not updated in {stale_threshold}+ days",
                    value=round(pct_stale * 100, 1),
                    sample_size=len(notes_with_dates),
                    confidence=0.9,
                    examples=tuple(n.title for n in stale_notes[:5]),
                    metadata={
                        "threshold_days": stale_threshold,
                        "count": len(stale_notes),
                    },
                )
            )

        return observations

    def _observe_daily_note_patterns(
        self, notes: list[NoteMetadata]
    ) -> list[PatternObservation]:
        """Observe daily note usage patterns."""
        observations = []

        daily_notes = [n for n in notes if n.is_daily_note]
        if not daily_notes:
            observations.append(
                PatternObservation(
                    pattern_type=PatternType.DAILY_NOTE_USAGE,
                    description="Daily notes detected",
                    value=0,
                    sample_size=len(notes),
                    confidence=0.8,
                )
            )
            return observations

        observations.append(
            PatternObservation(
                pattern_type=PatternType.DAILY_NOTE_USAGE,
                description="Total daily notes",
                value=len(daily_notes),
                sample_size=len(notes),
                confidence=0.95,
            )
        )

        # Average daily note length
        daily_word_counts = [n.word_count for n in daily_notes]
        avg_daily_words = statistics.mean(daily_word_counts)
        observations.append(
            PatternObservation(
                pattern_type=PatternType.DAILY_NOTE_USAGE,
                description="Average daily note length (words)",
                value=round(avg_daily_words, 0),
                sample_size=len(daily_notes),
                confidence=0.9,
                metadata={
                    "median": statistics.median(daily_word_counts),
                    "max": max(daily_word_counts),
                    "min": min(daily_word_counts),
                },
            )
        )

        # Daily notes with links
        daily_with_links = [n for n in daily_notes if len(n.outgoing_links) > 0]
        pct_with_links = len(daily_with_links) / len(daily_notes)
        observations.append(
            PatternObservation(
                pattern_type=PatternType.DAILY_NOTE_USAGE,
                description="Percentage of daily notes with links",
                value=round(pct_with_links * 100, 1),
                sample_size=len(daily_notes),
                confidence=0.9,
            )
        )

        return observations

    def _observe_orphan_notes(
        self, notes: list[NoteMetadata]
    ) -> list[PatternObservation]:
        """Observe orphan note patterns."""
        observations = []

        # Notes with no incoming or outgoing links
        orphans = [
            n
            for n in notes
            if len(n.outgoing_links) == 0 and len(n.incoming_links) == 0
        ]

        if notes:
            pct_orphan = len(orphans) / len(notes)
            observations.append(
                PatternObservation(
                    pattern_type=PatternType.ORPHAN_NOTES,
                    description="Percentage of orphan notes (no links in or out)",
                    value=round(pct_orphan * 100, 1),
                    sample_size=len(notes),
                    confidence=0.95,
                    examples=tuple(n.title for n in orphans[:5]),
                    metadata={"count": len(orphans)},
                )
            )

        return observations

    def _observe_tag_patterns(
        self, notes: list[NoteMetadata]
    ) -> list[PatternObservation]:
        """Observe tag usage patterns."""
        observations = []

        # Collect all tags
        all_tags: list[str] = []
        notes_with_tags = 0
        for note in notes:
            if note.tags:
                notes_with_tags += 1
                all_tags.extend(note.tags)

        if notes:
            pct_tagged = notes_with_tags / len(notes)
            observations.append(
                PatternObservation(
                    pattern_type=PatternType.TAG_USAGE,
                    description="Percentage of notes with tags",
                    value=round(pct_tagged * 100, 1),
                    sample_size=len(notes),
                    confidence=0.95,
                )
            )

        if all_tags:
            # Count tag frequency
            from collections import Counter

            tag_counts = Counter(all_tags)
            top_tags = tag_counts.most_common(5)

            observations.append(
                PatternObservation(
                    pattern_type=PatternType.TAG_USAGE,
                    description="Unique tags in vault",
                    value=len(tag_counts),
                    sample_size=len(notes),
                    confidence=0.95,
                    metadata={
                        "top_tags": dict(top_tags),
                        "total_tag_uses": len(all_tags),
                    },
                )
            )

        return observations


# =============================================================================
# Convenience Functions
# =============================================================================


def observe_vault_patterns(
    vault_path: str | Path,
    config: MirrorConfig | None = None,
) -> list[PatternObservation]:
    """
    Observe patterns in an Obsidian vault.

    This is the main entry point for pattern observation.

    Args:
        vault_path: Path to the Obsidian vault
        config: Optional configuration

    Returns:
        List of PatternObservation objects
    """
    witness = ObsidianPatternWitness(config)
    result = witness.observe(vault_path)
    return result.observations
