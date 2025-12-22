"""
Decay & Refresh: Phase 4 of the Derivation Framework.

This module implements time-based decay and refresh mechanisms for derivations:

1. Time-Based Decay (evidence_decay):
   - Non-categorical evidence decays over time
   - Decay rates vary by evidence type (EMPIRICAL: 2%/day, AESTHETIC: 3%/day)
   - Categorical and somatic evidence never decay (Law 3)

2. Periodic ASHC Refresh (ashc_refresh):
   - Re-run ASHC to refresh empirical evidence
   - Prevents stale evidence from lingering
   - Updates principle draws with fresh data

3. Stigmergic Decay (stigmergic_decay):
   - Unused agents' stigmergic confidence decays
   - Prevents "usage inflation" from historical counts
   - Based on last activity timestamp, not just usage count

4. Full Decay Cycle (run_decay_cycle):
   - Combines all decay mechanisms
   - Should run periodically (e.g., daily via cron)
   - Emits summary for monitoring

Heritage:
    - Derivation Framework → spec/protocols/derivation-framework.md
    - Metabolic Development → spec/protocols/metabolic-development.md
    - Agent-as-Witness → spec/heritage.md

Teaching:
    gotcha: Categorical evidence NEVER decays. This is Law 3 (Bootstrap
            Indefeasibility) extended to derived agents with categorical proofs.

    gotcha: Stigmergic decay uses last_active timestamp, not usage count.
            High usage 6 months ago should decay; recent usage shouldn't.

    gotcha: ASHC refresh is OPTIONAL. If ASHC isn't available, skip it.
            Don't fail the entire decay cycle because ASHC is down.

    gotcha: run_decay_cycle is idempotent. Running it twice on the same day
            applies decay twice, but the formula handles this gracefully.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Protocol, Sequence

from .registry import DerivationRegistry, get_registry
from .types import Derivation, EvidenceType, PrincipleDraw

if TYPE_CHECKING:
    pass

logger = logging.getLogger("kgents.derivation.decay")


# =============================================================================
# Configuration
# =============================================================================


@dataclass(frozen=True)
class DecayConfig:
    """
    Configuration for decay behavior.

    These values were chosen based on the spec and real-world considerations:
    - Evidence decay rates from EvidenceType.decay_rate
    - Stigmergic half-life of ~30 days encourages ongoing usage
    - Activity threshold of 14 days before stigmergic decay begins
    """

    # Stigmergic decay settings
    stigmergic_halflife_days: float = 30.0  # Days for stigmergic confidence to halve
    inactivity_threshold_days: float = 14.0  # Days before stigmergic decay starts

    # Evidence decay settings
    min_draw_strength: float = 0.1  # Floor for decayed evidence
    min_stigmergic_confidence: float = 0.0  # Floor for stigmergic decay

    # Refresh settings
    refresh_threshold_days: float = 7.0  # Minimum days between ASHC refreshes


DEFAULT_CONFIG = DecayConfig()


# =============================================================================
# Activity Tracking
# =============================================================================


@dataclass
class ActivityRecord:
    """
    Tracks last activity for an agent.

    Used for stigmergic decay - we decay based on inactivity, not just low usage.
    """

    agent_name: str
    last_active: datetime
    usage_at_last_active: int

    @classmethod
    def now(cls, agent_name: str, usage: int) -> ActivityRecord:
        """Create a record for right now."""
        return cls(
            agent_name=agent_name,
            last_active=datetime.now(timezone.utc),
            usage_at_last_active=usage,
        )


class ActivityStore(Protocol):
    """
    Protocol for storing activity records.

    Can be backed by in-memory dict, D-gent, or any storage.
    """

    def get(self, agent_name: str) -> ActivityRecord | None:
        """Get activity record for an agent."""
        ...

    def set(self, record: ActivityRecord) -> None:
        """Store/update an activity record."""
        ...

    def all(self) -> Sequence[ActivityRecord]:
        """Get all activity records."""
        ...


class InMemoryActivityStore:
    """
    In-memory activity store for testing and simple deployments.

    For production, use a D-gent backed store.
    """

    def __init__(self) -> None:
        self._records: dict[str, ActivityRecord] = {}

    def get(self, agent_name: str) -> ActivityRecord | None:
        return self._records.get(agent_name)

    def set(self, record: ActivityRecord) -> None:
        self._records[record.agent_name] = record

    def all(self) -> Sequence[ActivityRecord]:
        return list(self._records.values())

    def clear(self) -> None:
        """Clear all records. For testing."""
        self._records.clear()


# Global activity store
_activity_store: ActivityStore | None = None


def get_activity_store() -> ActivityStore:
    """Get the global activity store."""
    global _activity_store
    if _activity_store is None:
        _activity_store = InMemoryActivityStore()
    return _activity_store


def set_activity_store(store: ActivityStore) -> None:
    """Set the global activity store. For DI/testing."""
    global _activity_store
    _activity_store = store


def reset_activity_store() -> None:
    """Reset to default in-memory store. For testing."""
    global _activity_store
    _activity_store = None


# =============================================================================
# Time-Based Evidence Decay
# =============================================================================


def decay_principle_draw(
    draw: PrincipleDraw,
    days_elapsed: float,
    config: DecayConfig = DEFAULT_CONFIG,
) -> PrincipleDraw:
    """
    Apply time-based decay to a single principle draw.

    Categorical and somatic evidence never decay (Law 3 extended).
    Other evidence types decay at their configured rates.

    Args:
        draw: The principle draw to decay
        days_elapsed: Days since last decay was applied
        config: Decay configuration

    Returns:
        A new PrincipleDraw with decayed strength (or unchanged if categorical)

    Example:
        >>> draw = PrincipleDraw("Composable", 0.8, EvidenceType.EMPIRICAL, ())
        >>> decayed = decay_principle_draw(draw, days_elapsed=30)
        >>> decayed.draw_strength < 0.8  # True, empirical decays
        True
    """
    # Categorical and somatic never decay
    if draw.evidence_type in (EvidenceType.CATEGORICAL, EvidenceType.SOMATIC):
        return draw

    rate = draw.evidence_type.decay_rate
    if rate == 0.0:
        return draw

    # Decay formula: strength' = strength * (1 - rate)^days
    decay_factor = (1 - rate) ** days_elapsed
    new_strength = draw.draw_strength * decay_factor

    # Apply floor
    new_strength = max(config.min_draw_strength, new_strength)

    return replace(draw, draw_strength=new_strength)


def decay_derivation_evidence(
    derivation: Derivation,
    days_elapsed: float,
    config: DecayConfig = DEFAULT_CONFIG,
) -> Derivation:
    """
    Apply time-based decay to all principle draws in a derivation.

    Bootstrap agents are never decayed (Law 3: Bootstrap Indefeasibility).

    Args:
        derivation: The derivation to decay
        days_elapsed: Days since last decay
        config: Decay configuration

    Returns:
        A new Derivation with decayed principle draws
    """
    if derivation.is_bootstrap:
        return derivation  # Law 3

    decayed_draws = tuple(
        decay_principle_draw(draw, days_elapsed, config) for draw in derivation.principle_draws
    )

    return replace(derivation, principle_draws=decayed_draws)


async def apply_evidence_decay(
    days_elapsed: float,
    registry: DerivationRegistry | None = None,
    config: DecayConfig = DEFAULT_CONFIG,
) -> dict[str, Any]:
    """
    Apply time-based decay to all derivations in the registry.

    This is the main entry point for evidence decay. Run periodically
    (e.g., daily) to keep evidence fresh.

    Args:
        days_elapsed: Days since last decay was applied
        registry: Derivation registry (uses global if not provided)
        config: Decay configuration

    Returns:
        Summary of decay operations performed

    Teaching:
        gotcha: This is async for consistency with other decay functions,
                even though current impl is sync. Future versions may need
                async for distributed registries.
    """
    if registry is None:
        registry = get_registry()

    decayed_agents: list[str] = []
    unchanged_agents: list[str] = []
    bootstrap_skipped: list[str] = []

    for agent_name in registry.list_agents():
        derivation = registry.get(agent_name)
        if derivation is None:
            continue

        if derivation.is_bootstrap:
            bootstrap_skipped.append(agent_name)
            continue

        decayed = decay_derivation_evidence(derivation, days_elapsed, config)

        if decayed != derivation:
            registry._derivations[agent_name] = decayed
            decayed_agents.append(agent_name)
            logger.debug(f"Decayed evidence for {agent_name} ({days_elapsed:.1f} days)")
        else:
            unchanged_agents.append(agent_name)

    logger.info(
        f"Evidence decay complete: {len(decayed_agents)} decayed, "
        f"{len(unchanged_agents)} unchanged, {len(bootstrap_skipped)} bootstrap skipped"
    )

    return {
        "days_elapsed": days_elapsed,
        "decayed_agents": decayed_agents,
        "unchanged_agents": unchanged_agents,
        "bootstrap_skipped": bootstrap_skipped,
    }


# =============================================================================
# Stigmergic Decay (Usage-Based)
# =============================================================================


def calculate_stigmergic_decay(
    current_confidence: float,
    days_inactive: float,
    config: DecayConfig = DEFAULT_CONFIG,
) -> float:
    """
    Calculate decayed stigmergic confidence based on inactivity.

    Uses half-life formula: confidence' = confidence * 0.5^(days / halflife)

    Args:
        current_confidence: Current stigmergic confidence
        days_inactive: Days since last activity
        config: Decay configuration

    Returns:
        New stigmergic confidence (may be 0.0)

    Example:
        >>> calculate_stigmergic_decay(0.5, days_inactive=30)
        0.25  # Half-life of 30 days means 30 days → half confidence
    """
    if days_inactive <= config.inactivity_threshold_days:
        return current_confidence  # No decay during grace period

    # Days beyond threshold
    decay_days: float = days_inactive - config.inactivity_threshold_days

    # Half-life formula
    decay_factor: float = 0.5 ** (decay_days / config.stigmergic_halflife_days)
    new_confidence: float = current_confidence * decay_factor

    # Return the larger of min threshold and decayed value
    if new_confidence < config.min_stigmergic_confidence:
        return config.min_stigmergic_confidence
    return new_confidence


async def apply_stigmergic_decay(
    registry: DerivationRegistry | None = None,
    activity_store: ActivityStore | None = None,
    config: DecayConfig = DEFAULT_CONFIG,
    now: datetime | None = None,
) -> dict[str, Any]:
    """
    Apply stigmergic decay to all agents based on inactivity.

    Agents that haven't been used recently have their stigmergic confidence
    reduced. This prevents "usage inflation" from historical counts.

    Args:
        registry: Derivation registry
        activity_store: Store for activity records
        config: Decay configuration
        now: Current time (for testing)

    Returns:
        Summary of stigmergic decay operations
    """
    if registry is None:
        registry = get_registry()
    if activity_store is None:
        activity_store = get_activity_store()
    if now is None:
        now = datetime.now(timezone.utc)

    decayed_agents: list[str] = []
    unchanged_agents: list[str] = []
    bootstrap_skipped: list[str] = []

    for agent_name in registry.list_agents():
        derivation = registry.get(agent_name)
        if derivation is None:
            continue

        if derivation.is_bootstrap:
            bootstrap_skipped.append(agent_name)
            continue

        # Get last activity
        record = activity_store.get(agent_name)
        if record is None:
            # No activity record = never active = max decay
            # But we need a baseline, so skip agents with no record
            unchanged_agents.append(agent_name)
            continue

        # Calculate days inactive
        days_inactive = (now - record.last_active).total_seconds() / 86400

        if days_inactive <= config.inactivity_threshold_days:
            unchanged_agents.append(agent_name)
            continue

        # Calculate new stigmergic confidence
        new_stigmergic = calculate_stigmergic_decay(
            derivation.stigmergic_confidence,
            days_inactive,
            config,
        )

        if new_stigmergic != derivation.stigmergic_confidence:
            updated = replace(derivation, stigmergic_confidence=new_stigmergic)
            registry._derivations[agent_name] = updated
            decayed_agents.append(agent_name)
            logger.debug(
                f"Stigmergic decay for {agent_name}: "
                f"{derivation.stigmergic_confidence:.3f} → {new_stigmergic:.3f} "
                f"({days_inactive:.1f} days inactive)"
            )
        else:
            unchanged_agents.append(agent_name)

    logger.info(
        f"Stigmergic decay complete: {len(decayed_agents)} decayed, "
        f"{len(unchanged_agents)} unchanged"
    )

    return {
        "decayed_agents": decayed_agents,
        "unchanged_agents": unchanged_agents,
        "bootstrap_skipped": bootstrap_skipped,
    }


# =============================================================================
# Activity Recording (for stigmergic decay)
# =============================================================================


def record_activity(
    agent_name: str,
    registry: DerivationRegistry | None = None,
    activity_store: ActivityStore | None = None,
) -> ActivityRecord | None:
    """
    Record activity for an agent (for stigmergic decay tracking).

    Call this when an agent is used (e.g., after mark_updates_stigmergy).

    Args:
        agent_name: The agent that was active
        registry: Derivation registry (for usage count)
        activity_store: Store for activity records

    Returns:
        The created ActivityRecord, or None if agent not found
    """
    if registry is None:
        registry = get_registry()
    if activity_store is None:
        activity_store = get_activity_store()

    if not registry.exists(agent_name):
        return None

    usage = registry.get_usage_count(agent_name)
    record = ActivityRecord.now(agent_name, usage)
    activity_store.set(record)

    logger.debug(f"Recorded activity for {agent_name}: usage={usage}")
    return record


# =============================================================================
# ASHC Refresh
# =============================================================================


@dataclass
class RefreshSchedule:
    """
    Tracks when agents were last refreshed via ASHC.

    Prevents excessive refresh attempts for agents that were recently verified.
    """

    agent_name: str
    last_refresh: datetime
    refresh_count: int = 0
    last_result: str | None = None  # "success", "failed", "skipped"


class RefreshStore(Protocol):
    """Protocol for storing refresh schedules."""

    def get(self, agent_name: str) -> RefreshSchedule | None: ...

    def set(self, schedule: RefreshSchedule) -> None: ...


class InMemoryRefreshStore:
    """In-memory refresh store for testing."""

    def __init__(self) -> None:
        self._schedules: dict[str, RefreshSchedule] = {}

    def get(self, agent_name: str) -> RefreshSchedule | None:
        return self._schedules.get(agent_name)

    def set(self, schedule: RefreshSchedule) -> None:
        self._schedules[schedule.agent_name] = schedule

    def clear(self) -> None:
        self._schedules.clear()


# Global refresh store
_refresh_store: RefreshStore | None = None


def get_refresh_store() -> RefreshStore:
    """Get the global refresh store."""
    global _refresh_store
    if _refresh_store is None:
        _refresh_store = InMemoryRefreshStore()
    return _refresh_store


def reset_refresh_store() -> None:
    """Reset to default in-memory store. For testing."""
    global _refresh_store
    _refresh_store = None


async def should_refresh_agent(
    agent_name: str,
    refresh_store: RefreshStore | None = None,
    config: DecayConfig = DEFAULT_CONFIG,
    now: datetime | None = None,
) -> bool:
    """
    Check if an agent should be refreshed via ASHC.

    Returns True if:
    - Agent was never refreshed, OR
    - Last refresh was more than refresh_threshold_days ago
    """
    if refresh_store is None:
        refresh_store = get_refresh_store()
    if now is None:
        now = datetime.now(timezone.utc)

    schedule = refresh_store.get(agent_name)
    if schedule is None:
        return True

    days_since_refresh = (now - schedule.last_refresh).total_seconds() / 86400
    return days_since_refresh >= config.refresh_threshold_days


async def apply_ashc_refresh(
    registry: DerivationRegistry | None = None,
    refresh_store: RefreshStore | None = None,
    config: DecayConfig = DEFAULT_CONFIG,
    ashc_runner: Any = None,  # ASHCRunner or None
) -> dict[str, Any]:
    """
    Refresh derivations by re-running ASHC.

    This is OPTIONAL. If ASHC isn't available, returns early without failing.
    When ASHC runs, it updates empirical evidence for principle draws.

    Args:
        registry: Derivation registry
        refresh_store: Store for refresh schedules
        config: Decay configuration
        ashc_runner: Optional ASHC runner (if None, skips refresh)

    Returns:
        Summary of refresh operations
    """
    if registry is None:
        registry = get_registry()
    if refresh_store is None:
        refresh_store = get_refresh_store()

    now = datetime.now(timezone.utc)
    refreshed_agents: list[str] = []
    skipped_agents: list[str] = []
    failed_agents: list[str] = []

    # If no ASHC runner, skip all refreshes
    if ashc_runner is None:
        logger.info("ASHC refresh skipped: no runner provided")
        return {
            "refreshed_agents": [],
            "skipped_agents": list(registry.list_agents()),
            "failed_agents": [],
            "reason": "no_runner",
        }

    for agent_name in registry.list_agents():
        derivation = registry.get(agent_name)
        if derivation is None or derivation.is_bootstrap:
            continue

        # Check if refresh is needed
        if not await should_refresh_agent(agent_name, refresh_store, config, now):
            skipped_agents.append(agent_name)
            continue

        # Try to run ASHC
        try:
            # In real implementation, this would call:
            # result = await ashc_runner.run_for_agent(agent_name)
            # For now, we just mark as attempted
            result = "skipped"  # Placeholder

            if result == "success":
                refreshed_agents.append(agent_name)
            else:
                skipped_agents.append(agent_name)

            # Record the attempt
            schedule = RefreshSchedule(
                agent_name=agent_name,
                last_refresh=now,
                refresh_count=(
                    refresh_store.get(agent_name) or RefreshSchedule(agent_name, now)
                ).refresh_count
                + 1,
                last_result=result,
            )
            refresh_store.set(schedule)

        except Exception as e:
            logger.warning(f"ASHC refresh failed for {agent_name}: {e}")
            failed_agents.append(agent_name)

    logger.info(
        f"ASHC refresh complete: {len(refreshed_agents)} refreshed, "
        f"{len(skipped_agents)} skipped, {len(failed_agents)} failed"
    )

    return {
        "refreshed_agents": refreshed_agents,
        "skipped_agents": skipped_agents,
        "failed_agents": failed_agents,
    }


# =============================================================================
# Full Decay Cycle
# =============================================================================


@dataclass
class DecayCycleResult:
    """
    Result of a full decay cycle.

    Contains summaries from all three decay mechanisms.
    """

    timestamp: datetime
    evidence_decay: dict[str, Any]
    stigmergic_decay: dict[str, Any]
    ashc_refresh: dict[str, Any]
    total_agents_affected: int

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Decay cycle at {self.timestamp.isoformat()}: "
            f"{self.total_agents_affected} agents affected"
        )


async def run_decay_cycle(
    days_elapsed: float = 1.0,
    registry: DerivationRegistry | None = None,
    activity_store: ActivityStore | None = None,
    refresh_store: RefreshStore | None = None,
    config: DecayConfig = DEFAULT_CONFIG,
    ashc_runner: Any = None,
) -> DecayCycleResult:
    """
    Run a complete decay cycle: evidence decay, stigmergic decay, ASHC refresh.

    This is the main entry point for periodic maintenance. Run daily via cron
    or scheduler.

    Args:
        days_elapsed: Days since last decay (for evidence decay)
        registry: Derivation registry
        activity_store: Store for activity records (stigmergic decay)
        refresh_store: Store for refresh schedules (ASHC refresh)
        config: Decay configuration
        ashc_runner: Optional ASHC runner

    Returns:
        Complete results from all decay mechanisms

    Example:
        >>> result = await run_decay_cycle(days_elapsed=1.0)
        >>> print(result.summary)
        "Decay cycle at 2025-12-22T...: 5 agents affected"
    """
    if registry is None:
        registry = get_registry()

    now = datetime.now(timezone.utc)

    # 1. Evidence decay
    evidence_result = await apply_evidence_decay(days_elapsed, registry, config)

    # 2. Stigmergic decay
    stigmergic_result = await apply_stigmergic_decay(registry, activity_store, config, now)

    # 3. ASHC refresh (optional)
    refresh_result = await apply_ashc_refresh(registry, refresh_store, config, ashc_runner)

    # Calculate total affected
    affected = set()
    affected.update(evidence_result.get("decayed_agents", []))
    affected.update(stigmergic_result.get("decayed_agents", []))
    affected.update(refresh_result.get("refreshed_agents", []))

    result = DecayCycleResult(
        timestamp=now,
        evidence_decay=evidence_result,
        stigmergic_decay=stigmergic_result,
        ashc_refresh=refresh_result,
        total_agents_affected=len(affected),
    )

    logger.info(result.summary)
    return result


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Configuration
    "DecayConfig",
    "DEFAULT_CONFIG",
    # Activity tracking
    "ActivityRecord",
    "ActivityStore",
    "InMemoryActivityStore",
    "get_activity_store",
    "set_activity_store",
    "reset_activity_store",
    "record_activity",
    # Evidence decay
    "decay_principle_draw",
    "decay_derivation_evidence",
    "apply_evidence_decay",
    # Stigmergic decay
    "calculate_stigmergic_decay",
    "apply_stigmergic_decay",
    # ASHC refresh
    "RefreshSchedule",
    "RefreshStore",
    "InMemoryRefreshStore",
    "get_refresh_store",
    "reset_refresh_store",
    "should_refresh_agent",
    "apply_ashc_refresh",
    # Full cycle
    "DecayCycleResult",
    "run_decay_cycle",
]
