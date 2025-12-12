"""
Hypnagogia: The Dream Cycle.

K-gent Phase 4: Background refinement through dream processing.

Hypnagogia is the state between waking and sleeping where patterns consolidate
and insights emerge. The HypnagogicCycle processes accumulated interactions
and refines the soul's understanding:

1. Review recent interactions (from dialogue history)
2. Identify recurring patterns
3. Promote strong patterns (SEED -> TREE)
4. Adjust eigenvector confidence based on evidence
5. Compost stale patterns

Philosophy:
    "Sleep consolidates memory. Dreams consolidate meaning."

Architecture:
    HypnagogicCycle → pattern extraction → eigenvector updates → DreamReport

Usage:
    from agents.k.hypnagogia import HypnagogicCycle, HypnagogicConfig

    cycle = HypnagogicCycle()
    report = await cycle.dream(soul)
    print(f"Patterns found: {len(report.patterns_discovered)}")
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from .llm import LLMClient
    from .soul import KgentSoul


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class HypnagogicConfig:
    """Configuration for dream cycles."""

    # When to dream (default: 3 AM local)
    dream_hour: int = 3
    dream_minute: int = 0

    # What to process
    max_interactions_per_dream: int = 100
    min_interactions_for_dream: int = 10

    # Pattern thresholds
    seed_to_tree_threshold: int = 5  # Occurrences before promotion
    tree_pruning_days: int = 30  # Days before tree becomes compost

    # Eigenvector adjustment
    confidence_delta_per_evidence: float = 0.01  # Max change per evidence
    max_confidence_change: float = 0.05  # Max change per dream cycle

    # LLM usage
    use_llm_for_patterns: bool = True
    pattern_extraction_temperature: float = 0.3


# =============================================================================
# Pattern Types
# =============================================================================


class PatternMaturity(str, Enum):
    """Maturity levels for discovered patterns."""

    SEED = "seed"  # Newly discovered, unvalidated
    SAPLING = "sapling"  # Seen twice, growing
    TREE = "tree"  # Established, high confidence
    COMPOST = "compost"  # Stale, ready for recycling


@dataclass
class Pattern:
    """A pattern discovered during dream processing."""

    content: str  # The pattern itself
    occurrences: int = 1
    maturity: PatternMaturity = PatternMaturity.SEED
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: list[str] = field(default_factory=list)
    eigenvector_affinities: dict[str, float] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Generate stable ID for pattern."""
        return hashlib.md5(self.content.encode()).hexdigest()[:12]

    @property
    def age_days(self) -> float:
        """Age of pattern in days."""
        delta = datetime.now(timezone.utc) - self.first_seen
        return delta.total_seconds() / 86400

    @property
    def staleness_days(self) -> float:
        """Days since last seen."""
        delta = datetime.now(timezone.utc) - self.last_seen
        return delta.total_seconds() / 86400

    def promote(self) -> "Pattern":
        """Promote pattern to next maturity level."""
        promotions = {
            PatternMaturity.SEED: PatternMaturity.SAPLING,
            PatternMaturity.SAPLING: PatternMaturity.TREE,
            PatternMaturity.TREE: PatternMaturity.TREE,  # Already max
            PatternMaturity.COMPOST: PatternMaturity.COMPOST,  # Cannot promote
        }
        return Pattern(
            content=self.content,
            occurrences=self.occurrences,
            maturity=promotions[self.maturity],
            first_seen=self.first_seen,
            last_seen=self.last_seen,
            evidence=self.evidence.copy(),
            eigenvector_affinities=self.eigenvector_affinities.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "occurrences": self.occurrences,
            "maturity": self.maturity.value,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "evidence": self.evidence,
            "eigenvector_affinities": self.eigenvector_affinities,
        }


# =============================================================================
# Eigenvector Delta
# =============================================================================


@dataclass
class EigenvectorDelta:
    """Changes to eigenvector confidence from dream processing."""

    eigenvector: str  # Name of eigenvector (aesthetic, categorical, etc.)
    old_confidence: float
    new_confidence: float
    evidence: list[str]  # What patterns supported this change
    reasoning: str

    @property
    def delta(self) -> float:
        """The change in confidence."""
        return self.new_confidence - self.old_confidence

    @property
    def direction(self) -> str:
        """Human-readable direction."""
        if self.delta > 0.001:
            return "increased"
        elif self.delta < -0.001:
            return "decreased"
        return "unchanged"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "eigenvector": self.eigenvector,
            "old_confidence": self.old_confidence,
            "new_confidence": self.new_confidence,
            "delta": self.delta,
            "direction": self.direction,
            "evidence": self.evidence,
            "reasoning": self.reasoning,
        }


# =============================================================================
# Dream Report
# =============================================================================


@dataclass
class DreamReport:
    """Report from a dream cycle."""

    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interactions_processed: int = 0
    patterns_discovered: list[Pattern] = field(default_factory=list)
    patterns_promoted: list[Pattern] = field(default_factory=list)
    patterns_composted: list[Pattern] = field(default_factory=list)
    eigenvector_deltas: list[EigenvectorDelta] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    was_dry_run: bool = False

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Dream Report ({self.timestamp.strftime('%Y-%m-%d %H:%M UTC')})",
            f"  Interactions processed: {self.interactions_processed}",
            f"  Patterns discovered: {len(self.patterns_discovered)}",
            f"  Patterns promoted: {len(self.patterns_promoted)}",
            f"  Patterns composted: {len(self.patterns_composted)}",
        ]

        if self.eigenvector_deltas:
            lines.append("  Eigenvector changes:")
            for delta in self.eigenvector_deltas:
                lines.append(
                    f"    {delta.eigenvector}: {delta.direction} "
                    f"({delta.old_confidence:.2%} -> {delta.new_confidence:.2%})"
                )

        if self.insights:
            lines.append("  Insights:")
            for insight in self.insights[:3]:
                lines.append(f"    - {insight}")

        if self.was_dry_run:
            lines.append("  [DRY RUN - no changes applied]")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "interactions_processed": self.interactions_processed,
            "patterns_discovered": [p.to_dict() for p in self.patterns_discovered],
            "patterns_promoted": [p.to_dict() for p in self.patterns_promoted],
            "patterns_composted": [p.to_dict() for p in self.patterns_composted],
            "eigenvector_deltas": [d.to_dict() for d in self.eigenvector_deltas],
            "insights": self.insights,
            "was_dry_run": self.was_dry_run,
        }


# =============================================================================
# Interaction Record (for pattern extraction)
# =============================================================================


@dataclass
class Interaction:
    """A recorded interaction for dream processing."""

    timestamp: datetime
    message: str
    response: str
    mode: str
    tokens_used: int = 0

    def to_text(self) -> str:
        """Convert to text for pattern extraction."""
        return f"[{self.mode}] User: {self.message}\nK-gent: {self.response}"


# =============================================================================
# The Dream Cycle
# =============================================================================


class HypnagogicCycle:
    """
    The dream cycle - background refinement of patterns.

    During hypnagogia:
    1. Review recent interactions (from dialogue history)
    2. Identify recurring patterns
    3. Promote strong patterns to TREEs
    4. Adjust eigenvector confidence based on evidence
    5. Compost stale patterns

    The cycle can be triggered:
    - Manually via `kgents soul dream`
    - Scheduled via cortex daemon at 3 AM
    - On interaction threshold (every N interactions)
    """

    def __init__(
        self,
        config: Optional[HypnagogicConfig] = None,
        llm: Optional["LLMClient"] = None,
    ) -> None:
        """Initialize hypnagogic cycle.

        Args:
            config: Dream configuration
            llm: Optional LLM client for pattern extraction
        """
        self._config = config or HypnagogicConfig()
        self._llm = llm

        # Pattern store (in-memory for now, could be persisted)
        self._patterns: dict[str, Pattern] = {}

        # Interaction buffer
        self._interactions: list[Interaction] = []

        # Dream history
        self._dream_history: list[DreamReport] = []

    @property
    def config(self) -> HypnagogicConfig:
        """Get configuration."""
        return self._config

    @property
    def patterns(self) -> dict[str, Pattern]:
        """Get all patterns."""
        return self._patterns.copy()

    @property
    def interactions_buffered(self) -> int:
        """Number of interactions in buffer."""
        return len(self._interactions)

    @property
    def last_dream(self) -> Optional[DreamReport]:
        """Most recent dream report."""
        return self._dream_history[-1] if self._dream_history else None

    # ─────────────────────────────────────────────────────────────────────────
    # Recording Interactions
    # ─────────────────────────────────────────────────────────────────────────

    def record_interaction(
        self,
        message: str,
        response: str,
        mode: str,
        tokens_used: int = 0,
    ) -> None:
        """
        Record an interaction for dream processing.

        Args:
            message: User's message
            response: K-gent's response
            mode: Dialogue mode (reflect, advise, challenge, explore)
            tokens_used: Tokens used for this interaction
        """
        interaction = Interaction(
            timestamp=datetime.now(timezone.utc),
            message=message,
            response=response,
            mode=mode,
            tokens_used=tokens_used,
        )
        self._interactions.append(interaction)

        # Cap buffer size
        if len(self._interactions) > self._config.max_interactions_per_dream * 2:
            self._interactions = self._interactions[
                -self._config.max_interactions_per_dream :
            ]

    def clear_interactions(self) -> int:
        """Clear interaction buffer, return count cleared."""
        count = len(self._interactions)
        self._interactions.clear()
        return count

    # ─────────────────────────────────────────────────────────────────────────
    # The Dream
    # ─────────────────────────────────────────────────────────────────────────

    async def dream(
        self,
        soul: "KgentSoul",
        dry_run: bool = False,
    ) -> DreamReport:
        """
        Execute a dream cycle.

        Args:
            soul: The KgentSoul to process
            dry_run: If True, don't apply changes

        Returns:
            DreamReport with results
        """
        report = DreamReport(was_dry_run=dry_run)

        # Get interactions to process
        interactions = self._interactions[: self._config.max_interactions_per_dream]
        report.interactions_processed = len(interactions)

        # Skip if not enough interactions
        if len(interactions) < self._config.min_interactions_for_dream:
            report.insights.append(
                f"Insufficient interactions ({len(interactions)} < "
                f"{self._config.min_interactions_for_dream}). Waiting..."
            )
            return report

        # Phase 1: Extract patterns
        new_patterns = await self.extract_patterns(interactions)
        report.patterns_discovered = new_patterns

        # Phase 2: Update pattern store and track promotions
        for pattern in new_patterns:
            existing = self._patterns.get(pattern.id)
            if existing:
                # Update existing pattern
                existing.occurrences += 1
                existing.last_seen = datetime.now(timezone.utc)
                existing.evidence.extend(pattern.evidence)

                # Check for promotion
                if (
                    existing.maturity == PatternMaturity.SEED
                    and existing.occurrences >= 2
                ):
                    promoted = existing.promote()
                    if not dry_run:
                        self._patterns[pattern.id] = promoted
                    report.patterns_promoted.append(promoted)
                elif (
                    existing.maturity == PatternMaturity.SAPLING
                    and existing.occurrences >= self._config.seed_to_tree_threshold
                ):
                    promoted = existing.promote()
                    if not dry_run:
                        self._patterns[pattern.id] = promoted
                    report.patterns_promoted.append(promoted)
                elif not dry_run:
                    self._patterns[pattern.id] = existing
            else:
                # New pattern
                if not dry_run:
                    self._patterns[pattern.id] = pattern

        # Phase 3: Compost stale patterns
        stale_ids: list[str] = []
        for pid, pattern in self._patterns.items():
            if pattern.staleness_days > self._config.tree_pruning_days:
                stale_ids.append(pid)
                composted = Pattern(
                    content=pattern.content,
                    occurrences=pattern.occurrences,
                    maturity=PatternMaturity.COMPOST,
                    first_seen=pattern.first_seen,
                    last_seen=pattern.last_seen,
                    evidence=pattern.evidence,
                    eigenvector_affinities=pattern.eigenvector_affinities,
                )
                report.patterns_composted.append(composted)

        if not dry_run:
            for pid in stale_ids:
                del self._patterns[pid]

        # Phase 4: Update eigenvector confidence
        deltas = await self.update_eigenvectors(new_patterns, soul)
        report.eigenvector_deltas = deltas

        # Apply eigenvector changes (if not dry run)
        if not dry_run and deltas:
            self._apply_eigenvector_changes(soul, deltas)

        # Phase 5: Generate insights
        report.insights = self._generate_insights(report)

        # Clear processed interactions
        if not dry_run:
            self._interactions = self._interactions[report.interactions_processed :]
            self._dream_history.append(report)

        return report

    # ─────────────────────────────────────────────────────────────────────────
    # Pattern Extraction
    # ─────────────────────────────────────────────────────────────────────────

    async def extract_patterns(
        self,
        interactions: list[Interaction],
    ) -> list[Pattern]:
        """
        Extract patterns from recent interactions.

        Uses heuristics first, then LLM for deeper analysis if available.

        Args:
            interactions: List of interactions to analyze

        Returns:
            List of discovered patterns
        """
        patterns: list[Pattern] = []

        # Phase 1: Heuristic extraction
        patterns.extend(self._extract_patterns_heuristic(interactions))

        # Phase 2: LLM extraction (if available and enabled)
        if self._llm and self._config.use_llm_for_patterns:
            llm_patterns = await self._extract_patterns_llm(interactions)
            patterns.extend(llm_patterns)

        # Deduplicate by content similarity
        seen_contents: set[str] = set()
        unique_patterns: list[Pattern] = []
        for pattern in patterns:
            normalized = pattern.content.lower().strip()
            if normalized not in seen_contents:
                seen_contents.add(normalized)
                unique_patterns.append(pattern)

        return unique_patterns

    def _extract_patterns_heuristic(
        self,
        interactions: list[Interaction],
    ) -> list[Pattern]:
        """Extract patterns using heuristics."""
        patterns: list[Pattern] = []

        # Count mode frequencies
        mode_counts: dict[str, int] = {}
        for interaction in interactions:
            mode_counts[interaction.mode] = mode_counts.get(interaction.mode, 0) + 1

        # Pattern: Dominant mode
        if mode_counts:
            dominant_mode = max(mode_counts, key=lambda m: mode_counts[m])
            ratio = mode_counts[dominant_mode] / len(interactions)
            if ratio > 0.5:
                patterns.append(
                    Pattern(
                        content=f"Preference for {dominant_mode} mode ({ratio:.0%})",
                        evidence=[
                            f"{mode_counts[dominant_mode]} of {len(interactions)} interactions"
                        ],
                        eigenvector_affinities=self._mode_to_eigenvector(dominant_mode),
                    )
                )

        # Pattern: Common words in messages
        word_counts: dict[str, int] = {}
        for interaction in interactions:
            words = re.findall(r"\b\w{4,}\b", interaction.message.lower())
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1

        # Find recurring themes (words appearing in > 20% of interactions)
        threshold = max(2, len(interactions) // 5)
        for word, count in word_counts.items():
            if count >= threshold:
                # Skip common words
                if word in {
                    "this",
                    "that",
                    "what",
                    "have",
                    "with",
                    "from",
                    "your",
                    "about",
                }:
                    continue
                patterns.append(
                    Pattern(
                        content=f"Recurring theme: '{word}'",
                        evidence=[f"Appeared {count} times"],
                    )
                )

        # Pattern: Question types
        question_count = sum(1 for i in interactions if "?" in i.message)
        if question_count > len(interactions) * 0.6:
            patterns.append(
                Pattern(
                    content="High inquiry rate (many questions)",
                    evidence=[
                        f"{question_count} of {len(interactions)} were questions"
                    ],
                    eigenvector_affinities={"categorical": 0.6},
                )
            )

        return patterns

    async def _extract_patterns_llm(
        self,
        interactions: list[Interaction],
    ) -> list[Pattern]:
        """Extract patterns using LLM analysis."""
        if not self._llm:
            return []

        # Build prompt
        interaction_text = "\n---\n".join(
            i.to_text()
            for i in interactions[:20]  # Limit for context
        )

        system_prompt = """You are analyzing K-gent dialogue interactions to identify patterns.

Look for:
1. Recurring themes or topics
2. Behavioral patterns (modes, question types)
3. Emotional patterns (feelings expressed)
4. Growth patterns (changes over time)
5. Tension patterns (conflicting desires)

Output each pattern on a new line prefixed with "PATTERN: "
Include confidence (0.0-1.0) in parentheses.

Example:
PATTERN: User often seeks validation before major decisions (0.8)
PATTERN: Tendency toward over-engineering (0.6)
"""

        user_prompt = f"""Analyze these K-gent interactions and identify patterns:

{interaction_text}

What patterns do you notice?"""

        try:
            response = await self._llm.generate(
                system=system_prompt,
                user=user_prompt,
                temperature=self._config.pattern_extraction_temperature,
                max_tokens=500,
            )

            # Parse response
            patterns: list[Pattern] = []
            for line in response.text.split("\n"):
                if line.strip().upper().startswith("PATTERN:"):
                    content = line.split(":", 1)[1].strip()
                    # Extract confidence if present
                    confidence_match = re.search(r"\((\d*\.?\d+)\)", content)
                    if confidence_match:
                        confidence = float(confidence_match.group(1))
                        content = re.sub(r"\s*\(\d*\.?\d+\)\s*", "", content)
                    else:
                        confidence = 0.5

                    patterns.append(
                        Pattern(
                            content=content,
                            evidence=[f"LLM analysis (confidence: {confidence:.2f})"],
                        )
                    )

            return patterns

        except Exception:
            # LLM failure is non-fatal
            return []

    def _mode_to_eigenvector(self, mode: str) -> dict[str, float]:
        """Map dialogue mode to eigenvector affinities."""
        affinities: dict[str, dict[str, float]] = {
            "reflect": {"categorical": 0.7, "aesthetic": 0.5},
            "advise": {"gratitude": 0.6, "joy": 0.5},
            "challenge": {"heterarchy": 0.7, "generativity": 0.6},
            "explore": {"categorical": 0.8, "joy": 0.6},
        }
        return affinities.get(mode, {})

    # ─────────────────────────────────────────────────────────────────────────
    # Eigenvector Updates
    # ─────────────────────────────────────────────────────────────────────────

    async def update_eigenvectors(
        self,
        patterns: list[Pattern],
        soul: "KgentSoul",
    ) -> list[EigenvectorDelta]:
        """
        Adjust eigenvector confidence based on discovered patterns.

        Args:
            patterns: Patterns discovered in this cycle
            soul: The KgentSoul to update

        Returns:
            List of eigenvector deltas
        """
        deltas: list[EigenvectorDelta] = []

        # Aggregate affinities from patterns
        eigenvector_evidence: dict[str, list[str]] = {}
        eigenvector_signals: dict[str, float] = {}

        for pattern in patterns:
            for eigen, affinity in pattern.eigenvector_affinities.items():
                if eigen not in eigenvector_signals:
                    eigenvector_signals[eigen] = 0.0
                    eigenvector_evidence[eigen] = []
                eigenvector_signals[eigen] += affinity
                eigenvector_evidence[eigen].append(pattern.content)

        # Get current eigenvectors
        current = soul.eigenvectors

        # Calculate deltas for each eigenvector with evidence
        for eigen_name, signal in eigenvector_signals.items():
            # Get current confidence
            eigen_obj = getattr(current, eigen_name, None)
            if eigen_obj is None:
                continue

            old_confidence = eigen_obj.confidence

            # Calculate new confidence
            # More evidence = larger potential change
            evidence_count = len(eigenvector_evidence[eigen_name])
            potential_delta = (
                signal
                * self._config.confidence_delta_per_evidence
                * min(evidence_count, 5)  # Cap evidence impact
            )

            # Clamp to max change
            actual_delta = max(
                -self._config.max_confidence_change,
                min(self._config.max_confidence_change, potential_delta),
            )

            new_confidence = max(0.0, min(1.0, old_confidence + actual_delta))

            if abs(new_confidence - old_confidence) > 0.001:
                deltas.append(
                    EigenvectorDelta(
                        eigenvector=eigen_name,
                        old_confidence=old_confidence,
                        new_confidence=new_confidence,
                        evidence=eigenvector_evidence[eigen_name],
                        reasoning=f"Based on {evidence_count} pattern(s) with affinity signal {signal:.2f}",
                    )
                )

        return deltas

    def _apply_eigenvector_changes(
        self,
        soul: "KgentSoul",
        deltas: list[EigenvectorDelta],
    ) -> None:
        """
        Apply eigenvector confidence changes to the soul.

        Note: This modifies the eigenvector objects in place.
        """
        for delta in deltas:
            eigen_obj = getattr(soul.eigenvectors, delta.eigenvector, None)
            if eigen_obj is not None:
                # EigenvectorCoordinate is a dataclass, we need to create a new one
                # But since KentEigenvectors uses field(default_factory=...), the
                # eigenvector objects are mutable. We can update confidence directly.
                object.__setattr__(eigen_obj, "confidence", delta.new_confidence)

    # ─────────────────────────────────────────────────────────────────────────
    # Insight Generation
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_insights(self, report: DreamReport) -> list[str]:
        """Generate human-readable insights from dream report."""
        insights: list[str] = []

        # Insight: Pattern promotions
        if report.patterns_promoted:
            for pattern in report.patterns_promoted:
                insights.append(
                    f"Pattern strengthened: '{pattern.content}' "
                    f"(now {pattern.maturity.value})"
                )

        # Insight: Eigenvector changes
        for delta in report.eigenvector_deltas:
            if delta.delta > 0.01:
                insights.append(
                    f"Growing confidence in {delta.eigenvector} "
                    f"({delta.old_confidence:.0%} -> {delta.new_confidence:.0%})"
                )
            elif delta.delta < -0.01:
                insights.append(
                    f"Questioning {delta.eigenvector} "
                    f"({delta.old_confidence:.0%} -> {delta.new_confidence:.0%})"
                )

        # Insight: Pattern composting
        if report.patterns_composted:
            insights.append(
                f"Released {len(report.patterns_composted)} stale pattern(s) to compost"
            )

        # Insight: Pattern discovery rate
        if report.interactions_processed > 0:
            rate = len(report.patterns_discovered) / report.interactions_processed
            if rate > 0.2:
                insights.append("High pattern density - many recurring themes")
            elif rate < 0.05:
                insights.append("Low pattern density - diverse interactions")

        return insights

    # ─────────────────────────────────────────────────────────────────────────
    # Status & Scheduling
    # ─────────────────────────────────────────────────────────────────────────

    def status(self) -> dict[str, Any]:
        """Get current hypnagogia status."""
        return {
            "interactions_buffered": self.interactions_buffered,
            "patterns_stored": len(self._patterns),
            "patterns_by_maturity": {
                m.value: sum(1 for p in self._patterns.values() if p.maturity == m)
                for m in PatternMaturity
            },
            "dreams_completed": len(self._dream_history),
            "last_dream": self.last_dream.timestamp.isoformat()
            if self.last_dream
            else None,
            "config": {
                "min_interactions": self._config.min_interactions_for_dream,
                "max_interactions": self._config.max_interactions_per_dream,
                "dream_time": f"{self._config.dream_hour:02d}:{self._config.dream_minute:02d}",
            },
        }

    def should_dream(self) -> bool:
        """Check if conditions are met for dreaming."""
        # Check interaction threshold
        if self.interactions_buffered >= self._config.min_interactions_for_dream:
            return True

        # Check scheduled time
        now = datetime.now()
        if (
            now.hour == self._config.dream_hour
            and now.minute >= self._config.dream_minute
        ):
            # Only dream once per hour
            if self.last_dream:
                since_last = datetime.now(timezone.utc) - self.last_dream.timestamp
                if since_last < timedelta(hours=1):
                    return False
            return True

        return False


# =============================================================================
# Factory Functions
# =============================================================================


def create_hypnagogic_cycle(
    config: Optional[HypnagogicConfig] = None,
    llm: Optional["LLMClient"] = None,
) -> HypnagogicCycle:
    """Create a HypnagogicCycle instance."""
    return HypnagogicCycle(config=config, llm=llm)


# Module-level singleton for CLI
_hypnagogia_instance: Optional[HypnagogicCycle] = None


def get_hypnagogia() -> HypnagogicCycle:
    """Get or create the global hypnagogia instance."""
    global _hypnagogia_instance
    if _hypnagogia_instance is None:
        _hypnagogia_instance = HypnagogicCycle()
    return _hypnagogia_instance


def set_hypnagogia(cycle: HypnagogicCycle) -> None:
    """Set the global hypnagogia instance."""
    global _hypnagogia_instance
    _hypnagogia_instance = cycle


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Configuration
    "HypnagogicConfig",
    # Types
    "PatternMaturity",
    "Pattern",
    "EigenvectorDelta",
    "DreamReport",
    "Interaction",
    # The Cycle
    "HypnagogicCycle",
    # Factories
    "create_hypnagogic_cycle",
    "get_hypnagogia",
    "set_hypnagogia",
]
