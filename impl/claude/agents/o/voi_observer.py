"""
O-gent VoI Integration: Economically Self-Aware Observation

This module bridges O-gent with B-gent's VoI (Value of Information) economics.
It ensures that observation itself is economically justified.

The Heisenberg Constraint:
While O-gents aspire to be invisible, semantic observation (LLM-as-Judge)
consumes energy (tokens). O-gents must optimize the Value of Information.

Key Principles:
1. Each observation must justify its cost
2. High-risk agents get more observation budget
3. Observation depth adapts to available budget
4. VoI = E[Value with Info] - E[Value without Info]

Integration Points:
- B-gent VoI economics (voi_economics.py)
- Adaptive observation scheduling
- Budget-aware observation depth selection
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional

from .observer import (
    Agent,
    BaseObserver,
    CompositeObserver,
    EntropyEvent,
    ObservationContext,
    ObservationResult,
    ObservationStatus,
    Observer,
)
from .telemetry import TelemetryObserver
from .semantic import SemanticObserver, DriftDetector
from .axiological import AxiologicalObserver

# Import B-gent VoI types
try:
    from ..b.voi_economics import (
        ObservationDepth,
        FindingType,
        ObservationFinding,
        EpistemicCapital,
        VoILedger,
        VoIOptimizer,
        AdaptiveObserver as BgentAdaptiveObserver,
        UnifiedValueAccounting,
        VoIReceipt,
        create_voi_ledger,
        create_voi_optimizer,
    )
    from ..b.metered_functor import Gas
    from ..b.value_ledger import ValueLedger

    HAS_VOI = True
except ImportError:
    HAS_VOI = False

    # Stub types for standalone use
    class ObservationDepth(Enum):
        TELEMETRY_ONLY = "telemetry_only"
        SEMANTIC_SPOT = "semantic_spot"
        SEMANTIC_FULL = "semantic_full"
        AXIOLOGICAL = "axiological"

    class FindingType(Enum):
        ANOMALY_DETECTED = "anomaly_detected"
        HEALTH_CONFIRMED = "health_confirmed"
        FALSE_POSITIVE = "false_positive"
        INCONCLUSIVE = "inconclusive"


# =============================================================================
# VoI-Aware Types
# =============================================================================


@dataclass
class VoIObservationConfig:
    """Configuration for VoI-aware observation."""

    # Budget constraints
    max_observation_fraction: float = 0.10  # Max 10% of total budget
    min_rovi: float = 1.0  # Minimum acceptable RoVI

    # Depth costs (in tokens)
    depth_costs: dict[str, int] = field(
        default_factory=lambda: {
            "telemetry_only": 10,
            "semantic_spot": 500,
            "semantic_full": 2000,
            "axiological": 1000,
        }
    )

    # Priority weights
    risk_weight: float = 0.4
    consequence_weight: float = 0.3
    observability_weight: float = 0.3


@dataclass
class VoIObservationResult:
    """Result of a VoI-aware observation."""

    finding: "ObservationFinding | Any"
    depth_used: ObservationDepth
    gas_consumed: float
    voi: float  # Calculated Value of Information
    budget_remaining: float
    was_skipped: bool = False
    skip_reason: str | None = None


@dataclass
class VoIBudgetAllocation:
    """Budget allocation for an agent."""

    agent_id: str
    tokens_allocated: int
    priority: float
    recommended_depth: ObservationDepth
    reliability: float
    observability: float


# =============================================================================
# VoI-Aware Observer
# =============================================================================


class VoIAwareObserver(BaseObserver):
    """
    An O-gent observer that optimizes its own observation economics.

    Key principle: Each observation must justify its cost.

    This observer:
    1. Checks if observation is worth the cost before observing
    2. Selects observation depth based on budget
    3. Tracks VoI metrics for optimization
    4. Adapts observation frequency to priority
    """

    def __init__(
        self,
        observer_id: str = "voi_aware",
        config: VoIObservationConfig | None = None,
        voi_ledger: Any | None = None,
        voi_optimizer: Any | None = None,
    ):
        """
        Initialize VoI-aware observer.

        Args:
            observer_id: Unique identifier
            config: VoI configuration
            voi_ledger: B-gent VoILedger instance
            voi_optimizer: B-gent VoIOptimizer instance
        """
        super().__init__(observer_id=observer_id)
        self.config = config or VoIObservationConfig()

        # B-gent integration
        self._voi_ledger = voi_ledger
        self._voi_optimizer = voi_optimizer

        # Internal state
        self._budgets: dict[str, float] = {}  # agent_id -> remaining budget
        self._last_observation: dict[str, datetime] = {}
        self._observation_history: list[VoIObservationResult] = []

        # Sub-observers for different depths
        self._telemetry = TelemetryObserver(observer_id=f"{observer_id}_telemetry")
        self._semantic: SemanticObserver | None = None
        self._axiological: AxiologicalObserver | None = None

    def set_budget(self, agent_id: str, tokens: float) -> None:
        """Set observation budget for an agent."""
        self._budgets[agent_id] = tokens

    def get_remaining_budget(self, agent_id: str) -> float:
        """Get remaining observation budget."""
        return self._budgets.get(agent_id, 0.0)

    def should_observe(self, agent_id: str) -> tuple[bool, str | None]:
        """
        VoI-aware decision: Is observation worth it?

        Returns (should_observe, reason_if_not)
        """
        # Check budget
        budget = self.get_remaining_budget(agent_id)
        min_cost = self.config.depth_costs["telemetry_only"]

        if budget < min_cost:
            return False, "Insufficient budget"

        # Check recency (avoid redundant observation)
        last = self._last_observation.get(agent_id)
        if last:
            # Simple cooldown: 5 seconds minimum between observations
            if (datetime.now() - last).total_seconds() < 5:
                return False, "Recent observation exists"

        # If we have VoI optimizer, use its priority calculation
        if self._voi_optimizer:
            priority = self._voi_optimizer.compute_observation_priority(agent_id)
            if priority < 0.1:
                return False, "Priority too low"

        return True, None

    def select_depth(self, agent_id: str) -> ObservationDepth:
        """Select observation depth based on budget."""
        budget = self.get_remaining_budget(agent_id)

        # Order from deepest to shallowest
        depth_order = [
            (ObservationDepth.SEMANTIC_FULL, self.config.depth_costs["semantic_full"]),
            (ObservationDepth.AXIOLOGICAL, self.config.depth_costs["axiological"]),
            (ObservationDepth.SEMANTIC_SPOT, self.config.depth_costs["semantic_spot"]),
            (
                ObservationDepth.TELEMETRY_ONLY,
                self.config.depth_costs["telemetry_only"],
            ),
        ]

        for depth, cost in depth_order:
            if cost <= budget:
                return depth

        return ObservationDepth.TELEMETRY_ONLY

    async def observe_with_budget(
        self,
        agent: Agent[Any, Any],
        input_data: Any,
        result: Any,
        duration_ms: float,
    ) -> VoIObservationResult:
        """
        Perform observation within VoI constraints.
        """
        agent_id = getattr(agent, "id", str(id(agent)))
        agent_name = getattr(agent, "name", type(agent).__name__)

        # Check if observation is worthwhile
        should_observe, skip_reason = self.should_observe(agent_id)

        if not should_observe:
            return VoIObservationResult(
                finding=None,
                depth_used=ObservationDepth.TELEMETRY_ONLY,
                gas_consumed=0.0,
                voi=0.0,
                budget_remaining=self.get_remaining_budget(agent_id),
                was_skipped=True,
                skip_reason=skip_reason,
            )

        # Select depth based on budget
        depth = self.select_depth(agent_id)
        gas_cost = float(self.config.depth_costs[depth.value])

        # Create observation context
        ctx = ObservationContext(
            agent_id=agent_id,
            agent_name=agent_name,
            input_data=input_data,
            metadata={"depth": depth.value, "voi_aware": True},
        )

        # Execute observation at selected depth
        finding = await self._execute_observation(ctx, result, duration_ms, depth)

        # Calculate VoI
        voi = self._calculate_voi(finding)

        # Deduct budget
        self._budgets[agent_id] = max(0, self._budgets.get(agent_id, 0) - gas_cost)

        # Update last observation time
        self._last_observation[agent_id] = datetime.now()

        # Log to VoI ledger if available
        if self._voi_ledger and HAS_VOI:
            self._voi_ledger.log_observation(
                observer_id=self.observer_id,
                target_id=agent_id,
                gas_consumed=Gas(tokens=int(gas_cost), time_ms=0),
                finding=finding,
                depth=depth,
            )

        # Create result
        result = VoIObservationResult(
            finding=finding,
            depth_used=depth,
            gas_consumed=gas_cost,
            voi=voi,
            budget_remaining=self.get_remaining_budget(agent_id),
        )

        self._observation_history.append(result)
        return result

    async def _execute_observation(
        self,
        ctx: ObservationContext,
        result: Any,
        duration_ms: float,
        depth: ObservationDepth,
    ) -> Any:
        """Execute observation at the selected depth."""
        if depth == ObservationDepth.TELEMETRY_ONLY:
            # Just telemetry
            obs_result = await self._telemetry.post_invoke(ctx, result, duration_ms)
            return self._create_finding(FindingType.HEALTH_CONFIRMED, obs_result)

        elif depth == ObservationDepth.SEMANTIC_SPOT:
            # Sample semantic check
            if self._semantic is None:
                self._semantic = SemanticObserver()
            obs_result = await self._semantic.post_invoke(ctx, result, duration_ms)

            # Check for drift
            if obs_result.entropy_detected:
                return self._create_finding(FindingType.ANOMALY_DETECTED, obs_result)
            return self._create_finding(FindingType.HEALTH_CONFIRMED, obs_result)

        elif depth == ObservationDepth.SEMANTIC_FULL:
            # Full semantic analysis
            if self._semantic is None:
                self._semantic = SemanticObserver()
            obs_result = await self._semantic.post_invoke(ctx, result, duration_ms)

            if obs_result.entropy_detected:
                return self._create_finding(FindingType.ANOMALY_DETECTED, obs_result)
            return self._create_finding(FindingType.HEALTH_CONFIRMED, obs_result)

        elif depth == ObservationDepth.AXIOLOGICAL:
            # Economic audit
            if self._axiological is None:
                self._axiological = AxiologicalObserver()
            obs_result = await self._axiological.post_invoke(ctx, result, duration_ms)

            if obs_result.entropy_detected:
                return self._create_finding(FindingType.ANOMALY_DETECTED, obs_result)
            return self._create_finding(FindingType.HEALTH_CONFIRMED, obs_result)

        return self._create_finding(FindingType.INCONCLUSIVE, None)

    def _create_finding(
        self,
        finding_type: FindingType,
        obs_result: ObservationResult | None,
    ) -> Any:
        """Create an observation finding."""
        if HAS_VOI:
            return ObservationFinding(
                type=finding_type,
                confidence=0.8 if obs_result else 0.5,
                anomaly=obs_result.error if obs_result and obs_result.error else None,
                details=obs_result.telemetry if obs_result else {},
            )

        # Simple dict if B-gent not available
        return {
            "type": finding_type.value,
            "confidence": 0.8 if obs_result else 0.5,
            "anomaly": obs_result.error if obs_result and obs_result.error else None,
        }

    def _calculate_voi(self, finding: Any) -> float:
        """Calculate Value of Information for a finding."""
        if finding is None:
            return 0.0

        # Get finding type
        if hasattr(finding, "type"):
            finding_type = finding.type
        elif isinstance(finding, dict):
            finding_type_str = finding.get("type", "inconclusive")
            finding_type = FindingType(finding_type_str)
        else:
            return 0.0

        # Calculate VoI based on type
        if finding_type == FindingType.ANOMALY_DETECTED:
            # Anomaly detection has high value
            return 100.0  # Estimated disaster prevention value
        elif finding_type == FindingType.HEALTH_CONFIRMED:
            # Confirmation has modest value
            return 0.1
        elif finding_type == FindingType.FALSE_POSITIVE:
            # False positives have negative value
            return -0.5

        return 0.0

    def get_stats(self) -> dict[str, Any]:
        """Get observer statistics."""
        total_gas = sum(r.gas_consumed for r in self._observation_history)
        total_voi = sum(r.voi for r in self._observation_history)
        skipped = sum(1 for r in self._observation_history if r.was_skipped)

        return {
            "observer_id": self.observer_id,
            "total_observations": len(self._observation_history),
            "skipped_observations": skipped,
            "total_gas_consumed": total_gas,
            "total_voi_generated": total_voi,
            "rovi": total_voi / total_gas if total_gas > 0 else 0.0,
            "budget_utilization": {
                agent_id: {
                    "remaining": budget,
                }
                for agent_id, budget in self._budgets.items()
            },
        }

    def clear(self) -> None:
        """Clear observation history."""
        super().clear()
        self._observation_history.clear()


# =============================================================================
# Panopticon: Unified Observer Dashboard
# =============================================================================


@dataclass
class PanopticonStatus:
    """Status of the Panopticon (unified observation view)."""

    # Overall status
    status: str = "HOMEOSTATIC"  # HOMEOSTATIC, DEGRADED, CRITICAL
    uptime_seconds: float = 0.0

    # Dimension X: Telemetry
    ops_per_second: float = 0.0
    latency_p95_ms: float = 0.0
    error_rate: float = 0.0

    # Dimension Y: Semantics
    drift_score: float = 0.0
    knots_intact_pct: float = 100.0
    hallucinations_caught: int = 0

    # Dimension Z: Economics
    system_gdp: float = 0.0
    burn_rate: float = 0.0
    net_roc: float = 0.0
    top_performer: str | None = None
    cash_burner: str | None = None

    # Bootstrap
    identity_laws_hold: bool = True
    composition_laws_hold: bool = True
    kernel_integrity: bool = True

    # Alerts
    alerts: list[str] = field(default_factory=list)

    # VoI
    observation_rovi: float = 0.0
    observation_budget_used: float = 0.0


class Panopticon:
    """
    The O-gent aggregates the three dimensions into a single view of reality.

    This is the unified dashboard for system proprioception.
    """

    def __init__(
        self,
        telemetry: TelemetryObserver | None = None,
        semantic: SemanticObserver | None = None,
        axiological: AxiologicalObserver | None = None,
        voi_observer: VoIAwareObserver | None = None,
    ):
        self.telemetry = telemetry or TelemetryObserver()
        self.semantic = semantic
        self.axiological = axiological
        self.voi_observer = voi_observer
        self._start_time = datetime.now()
        self._alerts: list[str] = []

    def add_alert(self, message: str) -> None:
        """Add an alert."""
        self._alerts.append(message)
        # Keep last 10 alerts
        self._alerts = self._alerts[-10:]

    def get_status(self) -> PanopticonStatus:
        """Get current panopticon status."""
        uptime = (datetime.now() - self._start_time).total_seconds()

        status = PanopticonStatus(
            uptime_seconds=uptime,
            alerts=list(self._alerts),
        )

        # Telemetry (Dimension X)
        # Simplified - in production, aggregate from telemetry observer
        status.error_rate = 0.01
        status.latency_p95_ms = 230.0

        # Semantics (Dimension Y)
        if self.semantic:
            avg_drift = self.semantic.drift_detector.get_average_drift("system")
            status.drift_score = avg_drift

        # Economics (Dimension Z)
        if self.axiological:
            health = self.axiological.get_health_report()
            status.system_gdp = health.system_gdp
            status.burn_rate = health.total_gas_burned
            status.net_roc = health.system_roc

            if health.agent_rankings:
                status.top_performer = health.agent_rankings[0].agent_id
                # Find worst performer
                worst = min(health.agent_rankings, key=lambda r: r.roc)
                if worst.roc < 0.5:
                    status.cash_burner = worst.agent_id

        # VoI
        if self.voi_observer:
            stats = self.voi_observer.get_stats()
            status.observation_rovi = stats["rovi"]

        # Determine overall status
        if status.error_rate > 0.1 or status.net_roc < 0.5:
            status.status = "CRITICAL"
        elif status.drift_score > 0.3 or status.net_roc < 1.0:
            status.status = "DEGRADED"
        else:
            status.status = "HOMEOSTATIC"

        return status

    def render_dashboard(self) -> str:
        """Render ASCII dashboard."""
        status = self.get_status()

        lines = [
            "=" * 70,
            f" [O] SYSTEM PROPRIOCEPTION - {status.status}",
            "=" * 70,
            "",
            f"  TIME: T+{int(status.uptime_seconds)}s",
            "",
            "  ┌─ [X] TELEMETRY ───────────┐  ┌─ [Y] SEMANTICS ──────────────┐",
            f"  │ LATENCY: {status.latency_p95_ms:.0f}ms (p95)     │  │ DRIFT: {status.drift_score:.2f}                    │",
            f"  │ ERR: {status.error_rate:.2%}               │  │ KNOTS: {status.knots_intact_pct:.1f}% Intact          │",
            "  └────────────────────────────┘  └───────────────────────────────┘",
            "",
            "  ┌─ [Z] AXIOLOGY (ECONOMICS) ─────────────────────────────────────┐",
            f"  │ SYSTEM GDP: ${status.system_gdp:.2f} (Impact Generated)                    │",
            f"  │ BURN RATE:  ${status.burn_rate:.2f} (Tokens Consumed)                      │",
            f"  │ NET ROC:    {status.net_roc:.1f}x {'(Healthy)' if status.net_roc >= 1.0 else '(WARNING)'}                                │",
        ]

        if status.top_performer:
            lines.append(
                f"  │ TOP PERFORMER: [{status.top_performer}]                                   │"
            )
        if status.cash_burner:
            lines.append(
                f"  │ CASH BURNER:   [{status.cash_burner}] -> [UNDER AUDIT]               │"
            )

        lines.extend(
            [
                "  └─────────────────────────────────────────────────────────────────┘",
                "",
            ]
        )

        if status.alerts:
            lines.append(
                "  ┌─ ALERTS ─────────────────────────────────────────────────────────┐"
            )
            for alert in status.alerts[-5:]:
                lines.append(f"  │ {alert[:60]}│")
            lines.append(
                "  └─────────────────────────────────────────────────────────────────┘"
            )

        lines.append("=" * 70)

        return "\n".join(lines)


# =============================================================================
# Factory Functions
# =============================================================================


def create_voi_aware_observer(
    observer_id: str = "voi_aware",
    config: VoIObservationConfig | None = None,
) -> VoIAwareObserver:
    """Create a VoI-aware observer."""
    return VoIAwareObserver(observer_id=observer_id, config=config)


def create_panopticon(
    telemetry: TelemetryObserver | None = None,
    semantic: SemanticObserver | None = None,
    axiological: AxiologicalObserver | None = None,
    voi_observer: VoIAwareObserver | None = None,
) -> Panopticon:
    """Create a Panopticon dashboard."""
    return Panopticon(
        telemetry=telemetry,
        semantic=semantic,
        axiological=axiological,
        voi_observer=voi_observer,
    )


def create_full_observer_stack(
    observer_id: str = "full",
) -> tuple[CompositeObserver, Panopticon]:
    """
    Create a complete observer stack with all three dimensions + VoI.

    Returns:
        (CompositeObserver, Panopticon)
    """
    telemetry = TelemetryObserver(observer_id=f"{observer_id}_telemetry")
    semantic = SemanticObserver(observer_id=f"{observer_id}_semantic")
    axiological = AxiologicalObserver(observer_id=f"{observer_id}_axiological")
    voi = VoIAwareObserver(observer_id=f"{observer_id}_voi")

    # Composite observer for unified observation
    composite = CompositeObserver([telemetry, semantic, axiological])

    # Panopticon for dashboard
    panopticon = Panopticon(
        telemetry=telemetry,
        semantic=semantic,
        axiological=axiological,
        voi_observer=voi,
    )

    return composite, panopticon
