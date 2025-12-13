"""
Dashboard Data Collectors: Real-time metrics aggregation for kgents dashboard.

Collects metrics from all subsystems:
- K-gent Soul state (garden patterns, mode, eigenvectors)
- Flux Metabolism (pressure, temperature, fever state)
- Database Triad health (durability, resonance, reflex)
- Recent event traces

The collectors are designed to be:
1. Non-blocking: Graceful degradation if services unavailable
2. Lightweight: Minimal overhead for dashboard refresh
3. Observable: Can be subscribed to for live updates

Usage:
    from agents.i.data.dashboard_collectors import (
        DashboardMetrics,
        collect_metrics,
        create_demo_metrics,
    )

    metrics = await collect_metrics()
    print(f"Pressure: {metrics.metabolism.pressure:.0%}")

AGENTESE: self.vitals.dashboard.manifest
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .trace_provider import CallTreeNode, TraceMetrics

logger = logging.getLogger(__name__)


# =============================================================================
# Metric Types
# =============================================================================


@dataclass
class KgentMetrics:
    """K-gent soul state metrics."""

    mode: str = "reflect"  # Active dialogue mode
    garden_patterns: int = 0  # Total patterns in PersonaGarden
    garden_trees: int = 0  # Established patterns (lifecycle: TREE)
    interactions_count: int = 0  # Session interaction count
    tokens_used: int = 0  # Session token usage
    last_dream: datetime | None = None  # Last hypnagogia run
    is_online: bool = True

    @property
    def dream_age_str(self) -> str:
        """Human-readable time since last dream."""
        if self.last_dream is None:
            return "never"
        delta = datetime.now(timezone.utc) - self.last_dream
        hours = delta.total_seconds() / 3600
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        else:
            return f"{int(hours / 24)}d ago"


@dataclass
class MetabolismMetrics:
    """Metabolic engine state metrics."""

    pressure: float = 0.0  # 0.0 - 1.0 (percentage of threshold)
    temperature: float = 0.0  # Token ratio (input/output)
    in_fever: bool = False  # Currently in fever state
    fever_count: int = 0  # Total fevers this session
    last_tithe: datetime | None = None  # Last entropy discharge
    is_online: bool = True

    @property
    def pressure_pct(self) -> int:
        """Pressure as integer percentage."""
        return int(self.pressure * 100)

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if self.in_fever:
            return "FEVER"
        elif self.pressure > 0.8:
            return "HOT"
        elif self.pressure > 0.5:
            return "WARM"
        else:
            return "COOL"


@dataclass
class TriadMetrics:
    """Database triad health metrics (PostgreSQL, Qdrant, Redis)."""

    durability: float = 0.0  # PostgreSQL health (0-1)
    resonance: float = 0.0  # Qdrant health (0-1)
    reflex: float = 0.0  # Redis health (0-1)
    cdc_lag_ms: float = 0.0  # CDC replication lag
    synapse_active: bool = False  # Synapse connection status
    outbox_pending: int = 0  # Pending outbox messages
    is_online: bool = True

    @property
    def overall(self) -> float:
        """Overall triad health (average)."""
        return (self.durability + self.resonance + self.reflex) / 3

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if self.overall >= 0.9:
            return "HEALTHY"
        elif self.overall >= 0.5:
            return "DEGRADED"
        else:
            return "CRITICAL"


@dataclass
class FluxMetrics:
    """Flux event processing metrics."""

    events_per_second: float = 0.0  # Throughput
    queue_depth: int = 0  # Pending events
    active_agents: int = 0  # Running flux agents
    total_events_processed: int = 0  # Session total
    error_rate: float = 0.0  # Error percentage
    is_online: bool = True

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if self.error_rate > 0.1:
            return "ERRORS"
        elif self.queue_depth > 100:
            return "BACKED UP"
        elif self.events_per_second > 0:
            return "FLOWING"
        else:
            return "IDLE"


@dataclass
class TraceEntry:
    """A single trace entry for the recent events panel."""

    timestamp: datetime
    path: str  # AGENTESE path (e.g., "self.soul.challenge")
    args: str = ""  # Arguments (e.g., "(singleton)")
    result: str = "OK"  # Result (e.g., "REJECT", "success")
    latency_ms: int = 0  # Execution time

    def render(self, show_timestamp: bool = True) -> str:
        """Render as display string."""
        ts = f"[{self.timestamp.strftime('%H:%M:%S')}] " if show_timestamp else ""
        args_str = f" {self.args}" if self.args else ""
        latency = f" [{self.latency_ms}ms]" if self.latency_ms > 0 else ""
        return f"{ts}{self.path}{args_str} → {self.result}{latency}"


@dataclass
class TraceAnalysisMetrics:
    """Metrics from static call graph analysis for dashboard display."""

    files_analyzed: int = 0
    definitions_found: int = 0
    calls_found: int = 0
    analysis_time_ms: int = 0
    is_online: bool = True

    # Hottest functions (by caller count)
    hottest_functions: list[dict[str, Any]] = field(default_factory=list)

    # Selected call trees for display
    call_trees: list[Any] = field(default_factory=list)  # CallTreeNode

    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if not self.is_online:
            return "UNAVAILABLE"
        if self.files_analyzed == 0:
            return "NOT ANALYZED"
        return f"{self.files_analyzed} files"


@dataclass
class DashboardMetrics:
    """Complete dashboard metrics bundle."""

    kgent: KgentMetrics = field(default_factory=KgentMetrics)
    metabolism: MetabolismMetrics = field(default_factory=MetabolismMetrics)
    triad: TriadMetrics = field(default_factory=TriadMetrics)
    flux: FluxMetrics = field(default_factory=FluxMetrics)
    traces: list[TraceEntry] = field(default_factory=list)
    trace_analysis: TraceAnalysisMetrics = field(default_factory=TraceAnalysisMetrics)
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def any_offline(self) -> bool:
        """Check if any subsystem is offline."""
        return not (
            self.kgent.is_online
            and self.metabolism.is_online
            and self.triad.is_online
            and self.flux.is_online
        )


# =============================================================================
# Collectors
# =============================================================================


async def collect_kgent_metrics() -> KgentMetrics:
    """
    Collect K-gent soul metrics.

    Returns empty metrics with is_online=False if unavailable.
    """
    try:
        from agents.k import KgentSoul
        from agents.k.garden import get_garden
        from agents.k.hypnagogia import get_hypnagogia

        # Get or create soul instance
        from protocols.cli.handlers.soul import _get_soul

        soul = _get_soul()
        state = soul.manifest()

        # Get garden stats
        garden = get_garden()
        stats = await garden.stats()

        # Get last dream time
        hypnagogia = get_hypnagogia()
        last_dream = getattr(hypnagogia, "last_dream", None) or getattr(
            hypnagogia, "_last_dream_time", None
        )

        return KgentMetrics(
            mode=state.active_mode.value,
            garden_patterns=stats.total_entries,
            garden_trees=stats.by_lifecycle.get("tree", 0),
            interactions_count=state.interactions_count,
            tokens_used=state.tokens_used_session,
            last_dream=last_dream,
            is_online=True,
        )

    except ImportError:
        logger.debug("K-gent not available for metrics collection")
        return KgentMetrics(is_online=False)
    except Exception as e:
        logger.warning(f"Failed to collect K-gent metrics: {e}")
        return KgentMetrics(is_online=False)


async def collect_metabolism_metrics() -> MetabolismMetrics:
    """
    Collect metabolic engine metrics.

    Returns empty metrics with is_online=False if unavailable.
    """
    try:
        from protocols.agentese.metabolism import get_metabolic_engine

        engine = get_metabolic_engine()

        # Get fever count from status or stats (varies by version)
        status = engine.status()
        fever_count = status.get("total_fevers", 0)

        return MetabolismMetrics(
            pressure=engine.pressure,
            temperature=engine.temperature,
            in_fever=engine.in_fever,
            fever_count=fever_count,
            is_online=True,
        )

    except ImportError:
        logger.debug("Metabolic engine not available for metrics collection")
        return MetabolismMetrics(is_online=False)
    except Exception as e:
        logger.warning(f"Failed to collect metabolism metrics: {e}")
        return MetabolismMetrics(is_online=False)


async def collect_triad_metrics() -> TriadMetrics:
    """
    Collect database triad health metrics.

    Returns empty metrics with is_online=False if unavailable.
    """
    try:
        # Try to get vitals from the triad health widget data
        from agents.i.widgets.triad_health import TriadHealth as TriadHealthData

        # For now, return a placeholder - real integration would pull from
        # actual database connections or a health check endpoint
        # This is graceful degradation: metrics are still displayable even if
        # the actual triad services are not running
        return TriadMetrics(
            durability=0.0,
            resonance=0.0,
            reflex=0.0,
            is_online=False,  # Until real services are wired
        )

    except ImportError:
        logger.debug("Triad health not available for metrics collection")
        return TriadMetrics(is_online=False)
    except Exception as e:
        logger.warning(f"Failed to collect triad metrics: {e}")
        return TriadMetrics(is_online=False)


async def collect_flux_metrics() -> FluxMetrics:
    """
    Collect flux event processing metrics.

    Returns empty metrics with is_online=False if unavailable.
    """
    try:
        from agents.flux.synapse import SynapseMetrics

        # Try to get metrics from synapse if available
        # For now, return placeholder - real integration would check running fluxes
        return FluxMetrics(
            events_per_second=0.0,
            queue_depth=0,
            active_agents=0,
            total_events_processed=0,
            error_rate=0.0,
            is_online=False,  # Until real synapse is wired
        )

    except ImportError:
        logger.debug("Flux synapse not available for metrics collection")
        return FluxMetrics(is_online=False)
    except Exception as e:
        logger.warning(f"Failed to collect flux metrics: {e}")
        return FluxMetrics(is_online=False)


async def collect_recent_traces(limit: int = 10) -> list[TraceEntry]:
    """
    Collect recent AGENTESE traces.

    Returns empty list if unavailable.
    """
    try:
        from protocols.agentese.logos import create_logos

        # For now, return empty - real integration would query logos history
        # Logos doesn't persist invocation history by default
        return []

    except ImportError:
        logger.debug("Logos not available for trace collection")
        return []
    except Exception as e:
        logger.warning(f"Failed to collect traces: {e}")
        return []


async def collect_trace_analysis(
    hot_function_targets: list[str] | None = None,
) -> TraceAnalysisMetrics:
    """
    Collect trace analysis metrics from TraceDataProvider.

    Args:
        hot_function_targets: Optional list of functions to build call trees for.
            If None, uses the hottest functions from static analysis.

    Returns TraceAnalysisMetrics with call graph data.
    """
    try:
        from .trace_provider import get_trace_provider

        provider = get_trace_provider()

        # Collect metrics (uses cached static analysis if available)
        metrics = await provider.collect_metrics(include_static=True)

        # Build call trees for hot functions
        call_trees = []
        targets = hot_function_targets or []

        # If no explicit targets, use hottest functions from analysis
        if not targets and metrics.static.hottest_functions:
            targets = [f["name"] for f in metrics.static.hottest_functions[:3]]

        for target in targets[:3]:  # Limit to 3 call trees
            tree = provider.build_call_tree(target, depth=2, direction="callers")
            if tree:
                call_trees.append(tree)

        return TraceAnalysisMetrics(
            files_analyzed=metrics.static.files_analyzed,
            definitions_found=metrics.static.definitions_found,
            calls_found=metrics.static.calls_found,
            analysis_time_ms=metrics.static.analysis_time_ms,
            is_online=metrics.static.is_available,
            hottest_functions=metrics.static.hottest_functions,
            call_trees=call_trees,
        )

    except ImportError:
        logger.debug("TraceDataProvider not available for trace analysis")
        return TraceAnalysisMetrics(is_online=False)
    except Exception as e:
        logger.warning(f"Failed to collect trace analysis: {e}")
        return TraceAnalysisMetrics(is_online=False)


async def collect_metrics() -> DashboardMetrics:
    """
    Collect all dashboard metrics in parallel.

    Non-blocking: returns empty metrics for unavailable subsystems.
    """
    # Run all collectors in parallel
    results = await asyncio.gather(
        collect_kgent_metrics(),
        collect_metabolism_metrics(),
        collect_triad_metrics(),
        collect_flux_metrics(),
        collect_recent_traces(),
        collect_trace_analysis(),
        return_exceptions=True,
    )

    # Handle any exceptions gracefully with type-safe extraction
    kgent: KgentMetrics = (
        results[0]
        if isinstance(results[0], KgentMetrics)
        else KgentMetrics(is_online=False)
    )
    metabolism: MetabolismMetrics = (
        results[1]
        if isinstance(results[1], MetabolismMetrics)
        else MetabolismMetrics(is_online=False)
    )
    triad: TriadMetrics = (
        results[2]
        if isinstance(results[2], TriadMetrics)
        else TriadMetrics(is_online=False)
    )
    flux: FluxMetrics = (
        results[3]
        if isinstance(results[3], FluxMetrics)
        else FluxMetrics(is_online=False)
    )
    traces: list[TraceEntry] = results[4] if isinstance(results[4], list) else []
    trace_analysis: TraceAnalysisMetrics = (
        results[5]
        if isinstance(results[5], TraceAnalysisMetrics)
        else TraceAnalysisMetrics(is_online=False)
    )

    return DashboardMetrics(
        kgent=kgent,
        metabolism=metabolism,
        triad=triad,
        flux=flux,
        traces=traces,
        trace_analysis=trace_analysis,
    )


# =============================================================================
# Demo / Mock Data
# =============================================================================


def create_demo_metrics() -> DashboardMetrics:
    """
    Create demo metrics for testing and showcase.

    This provides realistic-looking metrics without requiring
    actual services to be running.
    """
    import random

    now = datetime.now(timezone.utc)

    return DashboardMetrics(
        kgent=KgentMetrics(
            mode="dialogue",
            garden_patterns=12,
            garden_trees=5,
            interactions_count=127,
            tokens_used=45231,
            last_dream=datetime.now(timezone.utc).replace(hour=now.hour - 2),
            is_online=True,
        ),
        metabolism=MetabolismMetrics(
            pressure=0.42,
            temperature=0.72,
            in_fever=False,
            fever_count=2,
            is_online=True,
        ),
        triad=TriadMetrics(
            durability=0.95,
            resonance=0.88,
            reflex=0.92,
            cdc_lag_ms=127,
            synapse_active=True,
            outbox_pending=3,
            is_online=True,
        ),
        flux=FluxMetrics(
            events_per_second=2.5,
            queue_depth=7,
            active_agents=3,
            total_events_processed=1847,
            error_rate=0.02,
            is_online=True,
        ),
        traces=[
            TraceEntry(
                timestamp=now,
                path="self.soul.challenge",
                args='("singleton")',
                result="REJECT",
                latency_ms=23,
            ),
            TraceEntry(
                timestamp=now,
                path="world.cortex.invoke",
                args="(gpt-4)",
                result="success",
                latency_ms=1200,
            ),
            TraceEntry(
                timestamp=now,
                path="void.entropy.tithe",
                args="(0.1)",
                result="discharged",
                latency_ms=1,
            ),
        ],
        trace_analysis=TraceAnalysisMetrics(
            files_analyzed=2582,
            definitions_found=42189,
            calls_found=133421,
            analysis_time_ms=3880,
            is_online=True,
            hottest_functions=[
                {"name": "TraceRenderer.__init__", "callers": 1655},
                {"name": "CallVisitor.__init__", "callers": 1655},
                {"name": "StaticCallGraph.__init__", "callers": 1655},
            ],
            call_trees=[],  # Demo doesn't include call trees
        ),
    )


def create_random_metrics() -> DashboardMetrics:
    """Create randomized metrics for animated demos."""
    import random

    base = create_demo_metrics()

    # Randomize values slightly
    base.metabolism.pressure = min(
        1.0, max(0.0, base.metabolism.pressure + random.uniform(-0.05, 0.05))
    )
    base.metabolism.temperature = min(
        1.0, max(0.0, base.metabolism.temperature + random.uniform(-0.1, 0.1))
    )
    base.flux.events_per_second = max(
        0, base.flux.events_per_second + random.uniform(-0.5, 0.5)
    )
    base.flux.queue_depth = max(0, base.flux.queue_depth + random.randint(-2, 2))

    return base


# =============================================================================
# Observable Metrics (for live updates)
# =============================================================================


class MetricsObservable:
    """
    Observable wrapper for dashboard metrics.

    Allows subscribing to metric updates for live dashboard refresh.

    Usage:
        observable = MetricsObservable()
        observable.subscribe(lambda m: print(f"Pressure: {m.metabolism.pressure}"))
        await observable.start_collecting(interval=1.0)
    """

    def __init__(self) -> None:
        self._subscribers: list[Callable[[DashboardMetrics], None]] = []
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._latest: DashboardMetrics | None = None

    def subscribe(self, callback: Callable[[DashboardMetrics], None]) -> None:
        """Subscribe to metric updates."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[DashboardMetrics], None]) -> None:
        """Unsubscribe from metric updates."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    @property
    def latest(self) -> DashboardMetrics | None:
        """Get the latest collected metrics."""
        return self._latest

    async def start_collecting(
        self, interval: float = 1.0, demo_mode: bool = False
    ) -> None:
        """
        Start collecting metrics at the given interval.

        Args:
            interval: Seconds between collections
            demo_mode: Use demo metrics instead of real collection
        """
        if self._running:
            return

        self._running = True

        async def collect_loop() -> None:
            while self._running:
                try:
                    if demo_mode:
                        metrics = create_random_metrics()
                    else:
                        metrics = await collect_metrics()

                    self._latest = metrics

                    # Notify subscribers
                    for callback in self._subscribers:
                        try:
                            callback(metrics)
                        except Exception as e:
                            logger.warning(f"Metrics subscriber error: {e}")

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning(f"Metrics collection error: {e}")

                await asyncio.sleep(interval)

        self._task = asyncio.create_task(collect_loop())

    async def stop(self) -> None:
        """Stop collecting metrics."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Metric types
    "KgentMetrics",
    "MetabolismMetrics",
    "TriadMetrics",
    "FluxMetrics",
    "TraceEntry",
    "TraceAnalysisMetrics",
    "DashboardMetrics",
    # Collection functions
    "collect_metrics",
    "collect_kgent_metrics",
    "collect_metabolism_metrics",
    "collect_triad_metrics",
    "collect_flux_metrics",
    "collect_recent_traces",
    "collect_trace_analysis",
    # Demo data
    "create_demo_metrics",
    "create_random_metrics",
    # Observable
    "MetricsObservable",
]
