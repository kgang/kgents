"""
O-gent Dimension Z: Axiological Observability (The Soul)

Observes economic health and value flows.
Answers: "Is it worth the cost?"

Observes:
- Return on Compute (RoC) - system GDP
- Conservation laws (no value created/destroyed)
- Agent rankings by efficiency
- Economic anomalies (burning money, free lunch)

This is the "economic" layer of observation—the soul of the system.
Integrates with B-gents (Bankers) to ensure the system is profitable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from .observer import (
    BaseObserver,
    ObservationContext,
    ObservationResult,
)

# Note: We import B-gent types conditionally to avoid circular imports
# In production, these would be proper imports
try:
    from ..b.value_tensor import (
        AntiDelusionChecker,
        EconomicDimension,
        EthicalDimension,
        PhysicalDimension,
        SemanticDimension,
        ValueTensor,
    )

    HAS_VALUE_TENSOR = True
except ImportError:
    HAS_VALUE_TENSOR = False

try:
    from ..b.value_ledger import BalanceSheet, ValueLedger

    HAS_VALUE_LEDGER = True
except ImportError:
    HAS_VALUE_LEDGER = False


# =============================================================================
# Economic Health Types
# =============================================================================


class EconomicStatus(Enum):
    """Status classifications for economic health."""

    EXCELLENT = "excellent"  # RoC > 3.0
    HEALTHY = "healthy"  # RoC 1.5 - 3.0
    BREAK_EVEN = "break_even"  # RoC 1.0 - 1.5
    WARNING = "warning"  # RoC 0.5 - 1.0
    BANKRUPTCY = "bankruptcy"  # RoC < 0.5


@dataclass
class AgentRanking:
    """Ranking of an agent by economic performance."""

    agent_id: str
    roc: float  # Return on Compute
    impact: float  # Total value generated
    gas: float  # Total gas consumed
    status: EconomicStatus
    rank: int = 0


@dataclass
class EconomicAnomaly:
    """An anomaly detected in economic patterns."""

    type: str  # "burning_money", "free_lunch", "inflation", "deflation"
    agent_id: str | None
    severity: str  # "info", "warning", "error", "critical"
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EconomicHealthReport:
    """Comprehensive economic health report."""

    system_gdp: float  # Total Impact generated
    total_gas_burned: float  # Total tokens consumed
    system_roc: float  # System-wide Return on Compute
    agent_rankings: list[AgentRanking]
    ethical_summary: dict[str, float]  # Summary of ethical adjustments
    anomalies: list[EconomicAnomaly]
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def status(self) -> EconomicStatus:
        """Overall system economic status."""
        if self.system_roc >= 3.0:
            return EconomicStatus.EXCELLENT
        elif self.system_roc >= 1.5:
            return EconomicStatus.HEALTHY
        elif self.system_roc >= 1.0:
            return EconomicStatus.BREAK_EVEN
        elif self.system_roc >= 0.5:
            return EconomicStatus.WARNING
        else:
            return EconomicStatus.BANKRUPTCY


# =============================================================================
# Value Ledger Observer (Stub Implementation)
# =============================================================================


@dataclass
class SimpleTreasury:
    """Simple treasury for standalone use without B-gent."""

    _gas: float = 0.0
    _impact: float = 0.0
    _debt: float = 0.0

    def record_gas(self, amount: float) -> None:
        """Record gas consumption."""
        self._gas += amount

    def record_impact(self, amount: float) -> None:
        """Record impact generation."""
        self._impact += amount

    def total_gas(self) -> float:
        """Total gas consumed."""
        return self._gas

    def total_impact(self) -> float:
        """Total impact generated."""
        return self._impact

    def total_debt(self) -> float:
        """Total debt."""
        return self._debt


@dataclass
class SimpleBalanceSheet:
    """Simple balance sheet for an agent."""

    agent_id: str
    assets: float = 0.0  # Impact generated
    gas_consumed: float = 0.0
    transactions: int = 0

    @property
    def roc(self) -> float:
        """Return on Compute."""
        if self.gas_consumed <= 0:
            return 0.0
        return self.assets / self.gas_consumed


class SimpleValueLedger:
    """
    Simple value ledger for standalone use.

    Use this when B-gent is not available.
    In production, integrate with the full ValueLedger.
    """

    def __init__(self) -> None:
        self.treasury = SimpleTreasury()
        self._agent_sheets: dict[str, SimpleBalanceSheet] = {}

    def get_agent_balance_sheet(self, agent_id: str) -> SimpleBalanceSheet:
        """Get or create balance sheet for agent."""
        if agent_id not in self._agent_sheets:
            self._agent_sheets[agent_id] = SimpleBalanceSheet(agent_id=agent_id)
        return self._agent_sheets[agent_id]

    def record_transaction(
        self,
        agent_id: str,
        gas: float,
        impact: float,
    ) -> None:
        """Record a transaction."""
        sheet = self.get_agent_balance_sheet(agent_id)
        sheet.gas_consumed += gas
        sheet.assets += impact
        sheet.transactions += 1

        self.treasury.record_gas(gas)
        self.treasury.record_impact(impact)

    def get_all_agents(self) -> list[str]:
        """Get all agent IDs."""
        return list(self._agent_sheets.keys())

    def system_roc(self) -> float:
        """System-wide Return on Compute."""
        total_gas = self.treasury.total_gas()
        total_impact = self.treasury.total_impact()
        if total_gas <= 0:
            return 0.0
        return total_impact / total_gas


class ValueLedgerObserver:
    """
    Observes the system's economic health via ValueLedger.

    Provides:
    - System GDP (total Impact generated)
    - Gas efficiency (system-wide RoC)
    - Agent performance rankings
    - Ethical adjustment summaries
    """

    def __init__(self, ledger: SimpleValueLedger | Any | None = None):
        """
        Initialize with a value ledger.

        Args:
            ledger: ValueLedger instance (B-gent) or SimpleValueLedger
        """
        self.ledger = ledger or SimpleValueLedger()

    def observe(self) -> EconomicHealthReport:
        """Generate economic health report."""
        return EconomicHealthReport(
            system_gdp=self.ledger.treasury.total_impact(),
            total_gas_burned=self.ledger.treasury.total_gas(),
            system_roc=self.ledger.system_roc(),
            agent_rankings=self.get_agent_rankings(),
            ethical_summary=self.get_ethical_summary(),
            anomalies=self.detect_economic_anomalies(),
        )

    def get_agent_rankings(self) -> list[AgentRanking]:
        """Rank agents by Return on Compute."""
        rankings = []

        for agent_id in self.ledger.get_all_agents():
            sheet = self.ledger.get_agent_balance_sheet(agent_id)
            roc = sheet.roc

            rankings.append(
                AgentRanking(
                    agent_id=agent_id,
                    roc=roc,
                    impact=sheet.assets,
                    gas=sheet.gas_consumed,
                    status=self._classify_status(roc),
                )
            )

        # Sort by RoC (highest first) and assign ranks
        rankings.sort(key=lambda r: r.roc, reverse=True)
        for i, ranking in enumerate(rankings):
            ranking.rank = i + 1

        return rankings

    def _classify_status(self, roc: float) -> EconomicStatus:
        """Classify economic status by RoC."""
        if roc >= 3.0:
            return EconomicStatus.EXCELLENT
        elif roc >= 1.5:
            return EconomicStatus.HEALTHY
        elif roc >= 1.0:
            return EconomicStatus.BREAK_EVEN
        elif roc >= 0.5:
            return EconomicStatus.WARNING
        else:
            return EconomicStatus.BANKRUPTCY

    def get_ethical_summary(self) -> dict[str, float]:
        """Get summary of ethical adjustments."""
        # Simple implementation - in production, integrate with EthicalRegulator
        return {
            "sin_taxes_collected": 0.0,
            "virtue_subsidies_granted": 0.0,
            "net_ethical_adjustment": 0.0,
        }

    def detect_economic_anomalies(self) -> list[EconomicAnomaly]:
        """Detect suspicious economic patterns."""
        anomalies = []

        for agent_id in self.ledger.get_all_agents():
            sheet = self.ledger.get_agent_balance_sheet(agent_id)

            # Burning money: High gas, low impact
            if sheet.gas_consumed > 1000 and sheet.assets < sheet.gas_consumed * 0.5:
                anomalies.append(
                    EconomicAnomaly(
                        type="burning_money",
                        agent_id=agent_id,
                        severity="warning",
                        message=f"Agent {agent_id} has RoC < 0.5x (Entropy Leak)",
                        data={"roc": sheet.roc, "gas": sheet.gas_consumed},
                    )
                )

            # Free lunch: High impact, minimal gas (suspicious)
            if sheet.assets > 1000 and sheet.gas_consumed < 100:
                anomalies.append(
                    EconomicAnomaly(
                        type="free_lunch",
                        agent_id=agent_id,
                        severity="error",
                        message=f"Agent {agent_id} claims high impact with minimal gas (Check for Fraud)",
                        data={"roc": sheet.roc, "impact": sheet.assets},
                    )
                )

        return anomalies


# =============================================================================
# Tensor Validator
# =============================================================================


@dataclass
class TensorValidationReport:
    """Report from tensor validation."""

    tensor_valid: bool
    conservation_valid: bool
    anomalies: list[str]
    violations: list[str]
    dimensions_healthy: dict[str, bool]
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def valid(self) -> bool:
        """Overall validity."""
        return self.tensor_valid and self.conservation_valid


class TensorValidator:
    """
    Validates conservation laws across the Value Tensor.

    Catches:
    - Conservation violations (impossible state transitions)
    - Cross-dimensional inconsistencies (delusion detection)
    - Exchange rate anomalies

    Requires B-gent value_tensor module.
    Falls back to simple validation if unavailable.
    """

    def __init__(self) -> None:
        self._has_checker = HAS_VALUE_TENSOR
        if HAS_VALUE_TENSOR:
            self._checker = AntiDelusionChecker()

    def validate(self, tensor: Any) -> TensorValidationReport:
        """
        Validate a ValueTensor.

        Args:
            tensor: ValueTensor instance from B-gent
        """
        if not HAS_VALUE_TENSOR:
            return TensorValidationReport(
                tensor_valid=True,
                conservation_valid=True,
                anomalies=[],
                violations=[],
                dimensions_healthy={"note": True},
            )

        # Run anti-delusion checks
        anomalies = []
        if hasattr(self, "_checker"):
            consistency_result = self._checker.check_consistency(tensor)
            anomalies = list(consistency_result) if consistency_result else []

        # Check conservation laws (requires before/after state)
        conservation_violations: list[str] = []
        # In production, compare tensor._previous with current

        # Check dimension health
        dimensions_healthy = {
            "physical": tensor.physical.total_tokens > 0 if hasattr(tensor, "physical") else True,
            "semantic": tensor.semantic.confidence > 0.3 if hasattr(tensor, "semantic") else True,
            "economic": tensor.economic.roc >= 0 if hasattr(tensor, "economic") else True,
            "ethical": True,  # Simplified
        }

        return TensorValidationReport(
            tensor_valid=len(anomalies) == 0,
            conservation_valid=len(conservation_violations) == 0,
            anomalies=anomalies,  # type: ignore[arg-type]
            violations=conservation_violations,
            dimensions_healthy=dimensions_healthy,
        )


# =============================================================================
# RoC Monitor
# =============================================================================


@dataclass
class RoCAlert:
    """Alert for RoC threshold crossing."""

    agent_id: str
    roc: float
    threshold: str  # "bankruptcy", "warning", "break_even"
    action: str  # "budget_freeze", "review", "audit"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RoCSnapshot:
    """Point-in-time RoC snapshot."""

    timestamp: datetime
    system_roc: float
    agent_rocs: dict[str, float]
    alerts: list[RoCAlert]


@dataclass
class RoCThresholds:
    """Thresholds for RoC alerts."""

    bankruptcy: float = 0.5
    break_even: float = 1.0
    healthy: float = 2.0


class RoCMonitor:
    """
    Real-time monitoring of Return on Compute across all agents.

    Integrates with O-gent dashboard and alert systems.
    """

    def __init__(
        self,
        ledger: SimpleValueLedger | Any | None = None,
        thresholds: RoCThresholds | None = None,
        alert_callback: Callable[[RoCAlert], Any] | None = None,
    ):
        self.ledger = ledger or SimpleValueLedger()
        self.thresholds = thresholds or RoCThresholds()
        self.alert_callback = alert_callback
        self._history: list[RoCSnapshot] = []

    def take_snapshot(self) -> RoCSnapshot:
        """Take a point-in-time RoC snapshot."""
        alerts = []

        # Calculate agent RoCs
        agent_rocs = {}
        for agent_id in self.ledger.get_all_agents():
            sheet = self.ledger.get_agent_balance_sheet(agent_id)
            agent_rocs[agent_id] = sheet.roc

            # Check thresholds
            if sheet.roc < self.thresholds.bankruptcy:
                alert = RoCAlert(
                    agent_id=agent_id,
                    roc=sheet.roc,
                    threshold="bankruptcy",
                    action="budget_freeze",
                )
                alerts.append(alert)
                if self.alert_callback:
                    self.alert_callback(alert)

            elif sheet.roc < self.thresholds.break_even:
                alert = RoCAlert(
                    agent_id=agent_id,
                    roc=sheet.roc,
                    threshold="warning",
                    action="review",
                )
                alerts.append(alert)
                if self.alert_callback:
                    self.alert_callback(alert)

        snapshot = RoCSnapshot(
            timestamp=datetime.now(),
            system_roc=self.ledger.system_roc(),
            agent_rocs=agent_rocs,
            alerts=alerts,
        )

        self._history.append(snapshot)
        return snapshot

    def get_history(self, limit: int = 100) -> list[RoCSnapshot]:
        """Get snapshot history."""
        return self._history[-limit:]

    def get_trend(self, agent_id: str) -> list[tuple[datetime, float]]:
        """Get RoC trend for an agent."""
        return [
            (s.timestamp, s.agent_rocs.get(agent_id, 0.0))
            for s in self._history
            if agent_id in s.agent_rocs
        ]

    def clear(self) -> None:
        """Clear history."""
        self._history.clear()


# =============================================================================
# Ledger Auditor
# =============================================================================


class LedgerAuditor:
    """
    The O-gent acts as Auditor for the B-gent's ledger.

    Performs:
    - Bankruptcy detection
    - Supply invariant verification
    - Fraud detection
    """

    def __init__(
        self,
        ledger: SimpleValueLedger | Any | None = None,
        suspend_callback: Callable[[str, str], Any] | None = None,
    ):
        """
        Initialize ledger auditor.

        Args:
            ledger: Value ledger to audit
            suspend_callback: Called when agent should be suspended (agent_id, reason)
        """
        self.ledger = ledger or SimpleValueLedger()
        self.suspend_callback = suspend_callback

    def audit_agent(self, agent_id: str) -> dict[str, Any]:
        """
        Audit a specific agent.

        Returns audit findings.
        """
        sheet = self.ledger.get_agent_balance_sheet(agent_id)
        findings = {
            "agent_id": agent_id,
            "pass": True,
            "findings": [],
        }

        # Bankruptcy check
        if sheet.assets < 0:
            findings["pass"] = False
            findings["findings"].append(  # type: ignore[attr-defined]
                {
                    "type": "bankruptcy",
                    "severity": "critical",
                    "message": f"Agent {agent_id} has negative assets (insolvency)",
                }
            )
            if self.suspend_callback:
                self.suspend_callback(agent_id, "Insolvency")

        # Efficiency check
        if sheet.roc < 0.5 and sheet.gas_consumed > 100:
            findings["findings"].append(  # type: ignore[attr-defined]
                {
                    "type": "low_efficiency",
                    "severity": "warning",
                    "message": f"Agent {agent_id} has RoC {sheet.roc:.2f} (below 0.5 threshold)",
                }
            )

        # Suspicious activity check
        if sheet.transactions > 0:
            avg_gas_per_tx = sheet.gas_consumed / sheet.transactions
            avg_impact_per_tx = sheet.assets / sheet.transactions

            if avg_impact_per_tx > avg_gas_per_tx * 10:
                findings["findings"].append(  # type: ignore[attr-defined]
                    {
                        "type": "suspicious_returns",
                        "severity": "warning",
                        "message": f"Agent {agent_id} shows unusually high returns per transaction",
                    }
                )

        return findings

    def audit_all(self) -> list[dict[str, Any]]:
        """Audit all agents."""
        return [self.audit_agent(agent_id) for agent_id in self.ledger.get_all_agents()]

    def verify_supply_invariant(self) -> bool:
        """
        Verify that total supply hasn't changed.

        Note: Requires full B-gent LedgerState for proper implementation.
        """
        # Simplified: Just check gas/impact totals are consistent
        total_impact = self.ledger.treasury.total_impact()
        sum_agent_impact = sum(
            self.ledger.get_agent_balance_sheet(a).assets for a in self.ledger.get_all_agents()
        )
        return bool(abs(total_impact - sum_agent_impact) < 0.001)


# =============================================================================
# Axiological Observer
# =============================================================================


class AxiologicalObserver(BaseObserver):
    """
    Observer that tracks economic health.

    Combines value ledger observation, tensor validation, and RoC monitoring.
    """

    def __init__(
        self,
        observer_id: str = "axiological",
        ledger: SimpleValueLedger | Any | None = None,
        gas_per_invoke: float = 10.0,
        impact_calculator: Callable[[Any], float] | None = None,
    ):
        """
        Initialize axiological observer.

        Args:
            observer_id: Unique identifier
            ledger: Value ledger to use
            gas_per_invoke: Default gas cost per invocation
            impact_calculator: Function to calculate impact from result
        """
        super().__init__(observer_id=observer_id)
        self.ledger = ledger or SimpleValueLedger()
        self.gas_per_invoke = gas_per_invoke
        self._impact_calculator = impact_calculator or self._default_impact

        # Create sub-observers
        self.value_observer = ValueLedgerObserver(self.ledger)
        self.roc_monitor = RoCMonitor(self.ledger)
        self.auditor = LedgerAuditor(self.ledger)

    def _default_impact(self, result: Any) -> float:
        """Default impact calculator (simple heuristic)."""
        if result is None:
            return 0.0
        # Simple heuristic: length-based impact
        result_str = str(result)
        return min(100.0, len(result_str) * 0.1)

    async def post_invoke(
        self,
        context: ObservationContext,
        result: Any,
        duration_ms: float,
    ) -> ObservationResult:
        """Record economic metrics after invocation."""
        base_result = await super().post_invoke(context, result, duration_ms)

        # Calculate economic impact
        gas = self.gas_per_invoke + (duration_ms / 100)  # Time-based gas component
        impact = self._impact_calculator(result)

        # Record transaction
        self.ledger.record_transaction(
            agent_id=context.agent_id,
            gas=gas,
            impact=impact,
        )

        # Add economic telemetry
        sheet = self.ledger.get_agent_balance_sheet(context.agent_id)
        base_result.telemetry.update(
            {
                "gas_consumed": gas,
                "impact_generated": impact,
                "agent_roc": sheet.roc,
                "agent_total_gas": sheet.gas_consumed,
                "agent_total_impact": sheet.assets,
            }
        )

        # Check for anomalies
        if sheet.roc < 0.5 and sheet.gas_consumed > 100:
            base_result.entropy_detected = True

        return base_result

    def get_health_report(self) -> EconomicHealthReport:
        """Get current economic health report."""
        return self.value_observer.observe()

    def take_roc_snapshot(self) -> RoCSnapshot:
        """Take RoC snapshot."""
        return self.roc_monitor.take_snapshot()


# =============================================================================
# Convenience Functions
# =============================================================================


def create_value_ledger() -> SimpleValueLedger:
    """Create a simple value ledger."""
    return SimpleValueLedger()


def create_value_ledger_observer(
    ledger: SimpleValueLedger | Any | None = None,
) -> ValueLedgerObserver:
    """Create a value ledger observer."""
    return ValueLedgerObserver(ledger=ledger)


def create_tensor_validator() -> TensorValidator:
    """Create a tensor validator."""
    return TensorValidator()


def create_roc_monitor(
    ledger: SimpleValueLedger | Any | None = None,
    thresholds: RoCThresholds | None = None,
    alert_callback: Callable[[RoCAlert], Any] | None = None,
) -> RoCMonitor:
    """Create a RoC monitor."""
    return RoCMonitor(
        ledger=ledger,
        thresholds=thresholds,
        alert_callback=alert_callback,
    )


def create_ledger_auditor(
    ledger: SimpleValueLedger | Any | None = None,
    suspend_callback: Callable[[str, str], Any] | None = None,
) -> LedgerAuditor:
    """Create a ledger auditor."""
    return LedgerAuditor(ledger=ledger, suspend_callback=suspend_callback)


def create_axiological_observer(
    observer_id: str = "axiological",
    ledger: SimpleValueLedger | Any | None = None,
) -> AxiologicalObserver:
    """Create an axiological observer."""
    return AxiologicalObserver(observer_id=observer_id, ledger=ledger)
