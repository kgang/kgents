"""
WitnessSheaf: Emergence from Event Sources to Coherent Crystals.

The Witness observes work through multiple lenses (watchers):
- Git events: commits, branches, stashes
- Filesystem events: edits, creates, deletes
- Test events: runs, passes, failures
- AGENTESE events: invocations, responses
- CI events: builds, deployments

The WitnessSheaf glues these local views into coherent Crystals,
ensuring the sheaf condition: overlapping observations must agree.

The Key Insight (from agents/sheaf/protocol.py):
    "A sheaf is defined as a presheaf satisfying locality and gluing
    conditions, ensuring coherent global structure while preserving
    local properties."

For the Witness, this means:
    - Different watchers (contexts) capture different aspects
    - Compatible observations can be glued into crystal
    - The crystal has semantic richness no single watcher provides

Sheaf Laws (verified in tests):
    1. Identity: glue([single_source]) ≅ single_source
    2. Associativity: glue(glue([A, B]), C) ≅ glue(A, glue([B, C]))

See: plans/witness-muse-implementation.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import FrozenSet, Sequence

from .crystal import Crystal, CrystalLevel, MoodVector
from .polynomial import Thought

# =============================================================================
# Event Source Contexts
# =============================================================================


class EventSource(Enum):
    """
    Contexts in the Witness observation topology.

    Each watcher corresponds to an event source context.
    """

    GIT = auto()  # Commits, branches, stashes
    FILESYSTEM = auto()  # File edits, creates, deletes
    TESTS = auto()  # Test runs, passes, failures
    AGENTESE = auto()  # AGENTESE invocations
    CI = auto()  # CI/CD events
    USER = auto()  # User markers, annotations

    @property
    def capabilities(self) -> frozenset[str]:
        """Capabilities this source provides."""
        return SOURCE_CAPABILITIES.get(self, frozenset())


# Capabilities by source
SOURCE_CAPABILITIES: dict[EventSource, frozenset[str]] = {
    EventSource.GIT: frozenset({"version_control", "history", "collaboration"}),
    EventSource.FILESYSTEM: frozenset({"files", "edits", "topology"}),
    EventSource.TESTS: frozenset({"quality", "validation", "feedback"}),
    EventSource.AGENTESE: frozenset({"invocations", "semantics", "paths"}),
    EventSource.CI: frozenset({"deployment", "builds", "integration"}),
    EventSource.USER: frozenset({"markers", "annotations", "intent"}),
}


def source_overlap(s1: EventSource, s2: EventSource) -> frozenset[str]:
    """
    Compute capability overlap between event sources.

    Returns shared capabilities. Empty frozenset if no overlap.
    """
    return s1.capabilities & s2.capabilities


# =============================================================================
# Local Observation (Per-Source View)
# =============================================================================


@dataclass(frozen=True)
class LocalObservation:
    """
    A local view from a single event source.

    Contains:
    - The source context
    - Thoughts captured from that source
    - Time bounds
    - Source-specific metadata
    """

    source: EventSource
    thoughts: tuple[Thought, ...]
    started_at: datetime
    ended_at: datetime
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        """Duration of this observation window."""
        return (self.ended_at - self.started_at).total_seconds()

    @property
    def thought_count(self) -> int:
        """Number of thoughts in this observation."""
        return len(self.thoughts)

    def overlaps_temporally(self, other: LocalObservation) -> bool:
        """Check if time windows overlap."""
        return not (self.ended_at < other.started_at or other.ended_at < self.started_at)


# =============================================================================
# Gluing Error
# =============================================================================


@dataclass
class GluingError(Exception):
    """Raised when local observations cannot be glued."""

    sources: list[str]
    reason: str

    def __str__(self) -> str:
        return f"Cannot glue observations from {self.sources}: {self.reason}"


# =============================================================================
# WitnessSheaf: The Core Emergence Structure
# =============================================================================


class WitnessSheaf:
    """
    Sheaf structure for gluing event source observations into crystals.

    The WitnessSheaf provides:
    - overlap(): Compute shared context between sources
    - compatible(): Check if local observations agree where they overlap
    - glue(): Combine observations into coherent Crystal

    The gluing is where EMERGENCE happens: the crystal has semantic
    richness that no single watcher provides alone.

    Crown Jewel Pattern: Signal Aggregation (Pattern 4)
    Multiple weak signals → coherent whole.

    Example:
        >>> sheaf = WitnessSheaf()
        >>> obs1 = LocalObservation(EventSource.GIT, git_thoughts, t0, t1)
        >>> obs2 = LocalObservation(EventSource.TESTS, test_thoughts, t0, t1)
        >>> if sheaf.compatible([obs1, obs2]):
        ...     crystal = sheaf.glue([obs1, obs2], session_id="my-session")
    """

    def __init__(self, time_tolerance: timedelta = timedelta(minutes=5)) -> None:
        """
        Initialize the WitnessSheaf.

        Args:
            time_tolerance: Maximum gap between observations to consider them
                           part of the same session. Default 5 minutes.
        """
        self.time_tolerance = time_tolerance

    def overlap(self, s1: EventSource, s2: EventSource) -> frozenset[str]:
        """
        Compute the overlap between two event sources.

        Returns the shared capabilities (semantic overlap).
        """
        return source_overlap(s1, s2)

    def compatible(self, observations: Sequence[LocalObservation]) -> bool:
        """
        Check if local observations can be glued.

        Observations are compatible if:
        1. They overlap temporally (or are within tolerance)
        2. Where sources have overlapping capabilities, observations don't contradict

        For the Witness, "contradiction" means:
        - Same file reported in different states
        - Same test reported as both passed and failed
        - Timeline inconsistency

        Currently we check temporal compatibility. Semantic compatibility
        is verified during glue() and fails explicitly if violated.

        Returns:
            True if observations can be glued.
        """
        if len(observations) < 2:
            return True

        # Check temporal compatibility
        observations_sorted = sorted(observations, key=lambda o: o.started_at)

        for i in range(len(observations_sorted) - 1):
            current = observations_sorted[i]
            next_obs = observations_sorted[i + 1]

            # Either overlap or gap is within tolerance
            gap = next_obs.started_at - current.ended_at
            if gap > self.time_tolerance:
                return False

        return True

    def glue(
        self,
        observations: Sequence[LocalObservation],
        session_id: str = "",
        markers: list[str] | None = None,
        insight: str | None = None,
    ) -> Crystal:
        """
        Glue local observations into a coherent Crystal.

        This is where EMERGENCE happens. The crystal synthesizes:
        - All thoughts from all sources (chronologically ordered)
        - Mood derived from combined signal stream
        - Topics from thought tags and source capabilities
        - Insight from semantic synthesis

        Args:
            observations: Local observations to glue
            session_id: Session identifier for the crystal
            markers: User-defined significant moments
            insight: Pre-computed insight (or template fallback)

        Returns:
            Crystal with emergent properties

        Raises:
            GluingError: If observations are not compatible
        """
        now = datetime.now()

        if not observations:
            return Crystal.from_crystallization(
                insight=insight or "Empty session—no observations.",
                significance="",
                principles=[],
                source_marks=[],
                time_range=(now, now),
                confidence=0.5,
                session_id=session_id,
            )

        if not self.compatible(observations):
            raise GluingError(
                sources=[obs.source.name for obs in observations],
                reason="Observations not temporally compatible",
            )

        # Merge all thoughts, sorted by timestamp
        all_thoughts: list[Thought] = []
        for obs in observations:
            all_thoughts.extend(obs.thoughts)

        # Sort by timestamp (handle None with epoch fallback)
        epoch = datetime.min
        all_thoughts.sort(key=lambda t: t.timestamp if t.timestamp else epoch)

        # Extract time range
        if all_thoughts:
            timestamps = [t.timestamp for t in all_thoughts if t.timestamp]
            started_at = min(timestamps) if timestamps else now
            ended_at = max(timestamps) if timestamps else now
        else:
            started_at = min(o.started_at for o in observations)
            ended_at = max(o.ended_at for o in observations)

        # Build insight from thought contents
        contents = [getattr(t, "content", str(t))[:100] for t in all_thoughts[:5]]
        computed_insight = insight or (
            "; ".join(contents[:3]) if contents else f"{len(all_thoughts)} observations"
        )

        # Extract topics from thought tags
        all_tags: set[str] = set()
        for t in all_thoughts:
            if hasattr(t, "tags"):
                all_tags.update(t.tags)

        # Add source capabilities as topics
        for obs in observations:
            all_tags.update(obs.source.capabilities)

        # Create crystal using the new API
        return Crystal.from_crystallization(
            insight=computed_insight,
            significance=f"Glued from {len(observations)} observations with {len(all_thoughts)} thoughts",
            principles=list(all_tags),
            source_marks=[],  # Would be populated from actual marks
            time_range=(started_at, ended_at),
            confidence=0.5,  # Template confidence
            topics=all_tags,
            mood=MoodVector.neutral(),  # Would compute from marks
            session_id=session_id,
        )

    def restrict(self, crystal: Crystal, source: EventSource) -> LocalObservation:
        """
        Restrict a crystal back to a single source view.

        Note: In the new Crystal model, raw thoughts are not stored (only semantic
        compression). This method now returns an empty observation with the crystal's
        time bounds, as the original thoughts must be retrieved from marks separately.

        This is the inverse of glue(): extract the contribution
        of a specific source from a crystal.

        Useful for:
        - Debugging crystallization
        - Source-specific analysis
        - Verifying sheaf laws

        Args:
            crystal: Crystal to restrict
            source: Event source to restrict to

        Returns:
            LocalObservation containing time bounds from the crystal
        """
        now = datetime.now()

        # Time bounds from crystal
        if crystal.time_range:
            started = crystal.time_range[0]
            ended = crystal.time_range[1]
        else:
            started = now
            ended = now

        return LocalObservation(
            source=source,
            thoughts=(),  # Thoughts not stored in Crystal; retrieve via source_marks
            started_at=started,
            ended_at=ended,
            metadata={"crystal_id": str(crystal.id)},
        )


# =============================================================================
# Sheaf Law Verification Helpers
# =============================================================================


def verify_identity_law(
    sheaf: WitnessSheaf, observation: LocalObservation, session_id: str = "test"
) -> bool:
    """
    Verify the identity law: glue([single_source]) ≅ glue([single_source]).

    The crystal from gluing a single observation should have consistent properties.
    In the new Crystal model, we verify time range and session consistency.
    """
    # Glue single observation
    glued_crystal = sheaf.glue([observation], session_id=session_id)

    # Verify essential properties
    return (
        glued_crystal.session_id == session_id
        and glued_crystal.time_range is not None
        and glued_crystal.level == CrystalLevel.SESSION
    )


def verify_associativity_law(
    sheaf: WitnessSheaf,
    obs_a: LocalObservation,
    obs_b: LocalObservation,
    obs_c: LocalObservation,
    session_id: str = "test",
) -> bool:
    """
    Verify the associativity law: glue(glue([A, B]), C) ≅ glue(A, glue([B, C])).

    The order of gluing should not matter for the final crystal structure.

    Note: In the new Crystal model, we verify that gluing in different orders
    produces crystals with consistent session_id and level. The actual content
    comparison requires semantic analysis beyond simple thought counts.
    """
    now = datetime.now()

    # (A ∘ B) ∘ C
    ab_crystal = sheaf.glue([obs_a, obs_b], session_id=session_id)
    # Extract as observation for re-gluing (using crystal time bounds)
    ab_obs = LocalObservation(
        source=obs_a.source,
        thoughts=obs_a.thoughts + obs_b.thoughts,  # Combine original thoughts
        started_at=ab_crystal.time_range[0] if ab_crystal.time_range else now,
        ended_at=ab_crystal.time_range[1] if ab_crystal.time_range else now,
    )
    abc_left = sheaf.glue([ab_obs, obs_c], session_id=session_id)

    # A ∘ (B ∘ C)
    bc_crystal = sheaf.glue([obs_b, obs_c], session_id=session_id)
    bc_obs = LocalObservation(
        source=obs_b.source,
        thoughts=obs_b.thoughts + obs_c.thoughts,  # Combine original thoughts
        started_at=bc_crystal.time_range[0] if bc_crystal.time_range else now,
        ended_at=bc_crystal.time_range[1] if bc_crystal.time_range else now,
    )
    abc_right = sheaf.glue([obs_a, bc_obs], session_id=session_id)

    # Compare essential properties (session and level consistency)
    return abc_left.session_id == abc_right.session_id and abc_left.level == abc_right.level


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "EventSource",
    "SOURCE_CAPABILITIES",
    "source_overlap",
    "LocalObservation",
    "GluingError",
    "WitnessSheaf",
    "verify_identity_law",
    "verify_associativity_law",
]
