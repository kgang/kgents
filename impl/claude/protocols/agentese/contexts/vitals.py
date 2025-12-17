"""
AGENTESE Vitals Context - self.vitals.*

Infrastructure health metrics for the Database Triad.

self.vitals.* provides semantic health signals:
- self.vitals.triad - Complete Database Triad health (TriadHealth)
- self.vitals.synapse - CDC pipeline metrics (SynapseMetrics)
- self.vitals.durability - Postgres health (DurabilitySignal)
- self.vitals.reflex - Redis health (ReflexSignal)
- self.vitals.resonance - Qdrant health (ResonanceSignal)
- self.vitals.circuit - Circuit breaker status

The key metric: coherency_with_truth
This tells you if the derived views (Qdrant) are in sync with truth (Postgres).

AGENTESE: self.vitals.*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..node import BaseLogosNode, BasicRendering, Renderable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# ===========================================================================
# Global State (Singletons for infrastructure metrics)
# ===========================================================================

# These will be wired by the infrastructure at startup
_synapse_metrics: Any = None
_cdc_lag_tracker: Any = None
_semantic_collector: Any = None
_circuit_breaker: Any = None


def set_synapse_metrics(metrics: Any) -> None:
    """Wire Synapse metrics singleton."""
    global _synapse_metrics
    _synapse_metrics = metrics


def set_cdc_lag_tracker(tracker: Any) -> None:
    """Wire CDC lag tracker singleton."""
    global _cdc_lag_tracker
    _cdc_lag_tracker = tracker


def set_semantic_collector(collector: Any) -> None:
    """Wire semantic metrics collector singleton."""
    global _semantic_collector
    _semantic_collector = collector


def set_circuit_breaker(breaker: Any) -> None:
    """Wire circuit breaker singleton."""
    global _circuit_breaker
    _circuit_breaker = breaker


def get_synapse_metrics() -> Any:
    """Get Synapse metrics singleton (creates if needed)."""
    global _synapse_metrics
    if _synapse_metrics is None:
        try:
            from agents.flux.synapse import SynapseMetrics

            _synapse_metrics = SynapseMetrics()
        except ImportError:
            return None
    return _synapse_metrics


def get_cdc_lag_tracker() -> Any:
    """Get CDC lag tracker singleton (creates if needed)."""
    global _cdc_lag_tracker
    if _cdc_lag_tracker is None:
        try:
            from agents.flux.synapse import CDCLagTracker

            _cdc_lag_tracker = CDCLagTracker()
        except ImportError:
            return None
    return _cdc_lag_tracker


def get_semantic_collector() -> Any:
    """Get semantic metrics collector singleton."""
    global _semantic_collector
    if _semantic_collector is None:
        try:
            from agents.flux.semantic_metrics import SemanticMetricsCollector

            tracker = get_cdc_lag_tracker()
            _semantic_collector = SemanticMetricsCollector(cdc_lag_tracker=tracker)
        except ImportError:
            return None
    return _semantic_collector


def get_circuit_breaker() -> Any:
    """Get circuit breaker singleton."""
    return _circuit_breaker


# ===========================================================================
# Affordances
# ===========================================================================

VITALS_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "triad": ("manifest", "is_coherent", "can_persist", "can_recall", "can_associate"),
    "synapse": ("manifest", "prometheus", "reset"),
    "durability": ("manifest", "update"),
    "reflex": ("manifest", "update"),
    "resonance": ("manifest", "update", "coherency"),
    "circuit": ("manifest", "open", "close", "reset"),
}


# ===========================================================================
# Triad Health Node
# ===========================================================================


@dataclass
class TriadHealthNode(BaseLogosNode):
    """
    self.vitals.triad - Complete Database Triad health.

    The holistic view of infrastructure health:
    - Durability (Postgres): Is the truth safe?
    - Reflex (Redis): How fast can I think?
    - Resonance (Qdrant): Can I remember similar things?

    The KEY metric is overall_health and is_coherent.
    """

    _handle: str = "self.vitals.triad"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return VITALS_AFFORDANCES["triad"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Get complete triad health."""
        collector = get_semantic_collector()
        if collector is None:
            return BasicRendering(
                summary="Triad Health (Not Configured)",
                content="SemanticMetricsCollector not available",
                metadata={"error": "collector_not_available"},
            )

        health = collector.collect()
        if health is None:
            return BasicRendering(
                summary="Triad Health (Incomplete)",
                content="Not all component pulses have been recorded",
                metadata={"error": "incomplete_pulses"},
            )

        return BasicRendering(
            summary=f"Triad Health: {health.overall_health.value.upper()}",
            content=(
                f"Overall: {health.overall_health.value}\n"
                f"Coherent: {health.is_coherent}\n"
                f"Can Persist: {health.can_persist}\n"
                f"Can Recall: {health.can_recall}\n"
                f"Can Associate: {health.can_associate}"
            ),
            metadata=health.to_dict(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        collector = get_semantic_collector()
        health = collector.collect() if collector else None

        match aspect:
            case "is_coherent":
                return health.is_coherent if health else False
            case "can_persist":
                return health.can_persist if health else False
            case "can_recall":
                return health.can_recall if health else False
            case "can_associate":
                return health.can_associate if health else False
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# ===========================================================================
# Synapse Metrics Node
# ===========================================================================


@dataclass
class SynapseMetricsNode(BaseLogosNode):
    """
    self.vitals.synapse - CDC pipeline metrics.

    Provides visibility into the Synapse processor:
    - Events processed/failed/retried
    - Average and max sync lag
    - DLQ size
    - Circuit breaker state
    """

    _handle: str = "self.vitals.synapse"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return VITALS_AFFORDANCES["synapse"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Get Synapse metrics."""
        metrics = get_synapse_metrics()
        if metrics is None:
            return BasicRendering(
                summary="Synapse Metrics (Not Configured)",
                content="SynapseMetrics not available",
                metadata={"error": "metrics_not_available"},
            )

        return BasicRendering(
            summary=f"Synapse: {metrics.events_processed} processed, {metrics.events_failed} failed",
            content=(
                f"Processed: {metrics.events_processed}\n"
                f"Failed: {metrics.events_failed}\n"
                f"Retried: {metrics.events_retried}\n"
                f"In DLQ: {metrics.events_in_dlq}\n"
                f"Avg Lag: {metrics.avg_sync_lag_ms:.1f}ms\n"
                f"Max Lag: {metrics.max_sync_lag_ms:.1f}ms\n"
                f"Circuit: {metrics.circuit_state}"
            ),
            metadata=metrics.to_dict(),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        metrics = get_synapse_metrics()

        match aspect:
            case "prometheus":
                return metrics.to_prometheus() if metrics else ""
            case "reset":
                # Reset metrics (for testing)
                if metrics:
                    metrics.events_processed = 0
                    metrics.events_failed = 0
                    metrics.events_retried = 0
                    metrics.events_in_dlq = 0
                    metrics._lag_samples.clear()
                return {"status": "reset"}
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# ===========================================================================
# Resonance Node (Key: coherency_with_truth)
# ===========================================================================


@dataclass
class ResonanceVitalsNode(BaseLogosNode):
    """
    self.vitals.resonance - Qdrant health with coherency.

    The coherency_with_truth metric is THE KEY:
    - 1.0 = Perfect sync with Postgres
    - 0.0 = 5+ seconds behind (critical)

    coherency = 1 - (cdc_lag_ms / 5000)
    """

    _handle: str = "self.vitals.resonance"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return VITALS_AFFORDANCES["resonance"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Get resonance signal with coherency."""
        collector = get_semantic_collector()
        if collector is None:
            return BasicRendering(
                summary="Resonance (Not Configured)",
                content="SemanticMetricsCollector not available",
            )

        health = collector.collect()
        if health is None or health.resonance is None:
            # Try to compute from lag tracker alone
            tracker = get_cdc_lag_tracker()
            if tracker:
                coherency = max(0.0, 1.0 - (tracker.avg_lag_ms / 5000))
                return BasicRendering(
                    summary=f"Resonance: {coherency:.0%} coherent",
                    content=f"Coherency with truth: {coherency:.2f}\nAvg lag: {tracker.avg_lag_ms:.0f}ms",
                    metadata={
                        "coherency_with_truth": coherency,
                        "avg_lag_ms": tracker.avg_lag_ms,
                    },
                )
            return BasicRendering(
                summary="Resonance (No Data)",
                content="No resonance data available",
            )

        resonance = health.resonance
        return BasicRendering(
            summary=f"Resonance: {resonance.health.value.upper()} ({resonance.coherency_with_truth:.0%} coherent)",
            content=(
                f"Health: {resonance.health.value}\n"
                f"Coherency with truth: {resonance.coherency_with_truth:.2f}\n"
                f"Search responsiveness: {resonance.search_responsiveness:.2f}\n"
                f"Associative capacity: {resonance.associative_capacity:.2f}"
            ),
            metadata={
                "health": resonance.health.value,
                "coherency_with_truth": resonance.coherency_with_truth,
                "search_responsiveness": resonance.search_responsiveness,
                "associative_capacity": resonance.associative_capacity,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        match aspect:
            case "coherency":
                tracker = get_cdc_lag_tracker()
                if tracker:
                    return max(0.0, 1.0 - (tracker.avg_lag_ms / 5000))
                return 1.0  # Assume perfect if no tracker
            case "update":
                # Update Qdrant pulse
                collector = get_semantic_collector()
                if collector and "pulse" in kwargs:
                    collector.update_qdrant(kwargs["pulse"])
                    return {"status": "updated"}
                return {"error": "collector or pulse not available"}
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# ===========================================================================
# Circuit Breaker Node
# ===========================================================================


@dataclass
class CircuitBreakerNode(BaseLogosNode):
    """
    self.vitals.circuit - Circuit breaker status.

    When the circuit opens, Qdrant operations fail fast.
    This protects against cascade failures.
    """

    _handle: str = "self.vitals.circuit"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return VITALS_AFFORDANCES["circuit"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Get circuit breaker status."""
        breaker = get_circuit_breaker()
        if breaker is None:
            return BasicRendering(
                summary="Circuit Breaker (Not Configured)",
                content="No circuit breaker configured",
                metadata={"state": "not_configured"},
            )

        stats = breaker.stats()
        return BasicRendering(
            summary=f"Circuit: {stats['state'].upper()}",
            content=(
                f"State: {stats['state']}\n"
                f"Failures: {stats['failure_count']}\n"
                f"Time in state: {stats['time_in_state']:.1f}s\n"
                f"Time until retry: {stats['time_until_retry']:.1f}s"
            ),
            metadata=stats,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        breaker = get_circuit_breaker()

        match aspect:
            case "open":
                if breaker:
                    breaker.force_open()
                    return {"status": "opened"}
                return {"error": "no circuit breaker"}
            case "close":
                if breaker:
                    breaker.force_close()
                    return {"status": "closed"}
                return {"error": "no circuit breaker"}
            case "reset":
                if breaker:
                    breaker.reset()
                    return {"status": "reset"}
                return {"error": "no circuit breaker"}
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# ===========================================================================
# Vitals Context Resolver
# ===========================================================================


@dataclass
class VitalsContextResolver:
    """
    Resolver for self.vitals.* context.

    Routes to appropriate vitals node based on path.
    """

    _triad: TriadHealthNode | None = None
    _synapse: SynapseMetricsNode | None = None
    _resonance: ResonanceVitalsNode | None = None
    _circuit: CircuitBreakerNode | None = None

    def __post_init__(self) -> None:
        """Initialize singleton nodes."""
        self._triad = TriadHealthNode()
        self._synapse = SynapseMetricsNode()
        self._resonance = ResonanceVitalsNode()
        self._circuit = CircuitBreakerNode()

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a self.vitals.* path to a node.

        Args:
            holon: The vitals component (triad, synapse, resonance, circuit, durability, reflex)
            rest: Additional path components

        Returns:
            Resolved node
        """
        match holon:
            case "triad":
                return self._triad or TriadHealthNode()
            case "synapse":
                return self._synapse or SynapseMetricsNode()
            case "resonance":
                return self._resonance or ResonanceVitalsNode()
            case "circuit":
                return self._circuit or CircuitBreakerNode()
            case "durability":
                # TODO: Add DurabilityVitalsNode
                return GenericVitalsNode("durability")
            case "reflex":
                # TODO: Add ReflexVitalsNode
                return GenericVitalsNode("reflex")
            case _:
                return GenericVitalsNode(holon)


@dataclass
class GenericVitalsNode(BaseLogosNode):
    """Fallback node for undefined vitals paths."""

    holon: str
    _handle: str = ""

    def __post_init__(self) -> None:
        self._handle = f"self.vitals.{self.holon}"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("manifest",)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        return BasicRendering(
            summary=f"Vitals: {self.holon}",
            content=f"Generic vitals node for {self.holon}",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        return {"holon": self.holon, "aspect": aspect, "kwargs": kwargs}


# ===========================================================================
# Factory
# ===========================================================================


def create_vitals_resolver() -> VitalsContextResolver:
    """Create a VitalsContextResolver."""
    resolver = VitalsContextResolver()
    resolver.__post_init__()
    return resolver
