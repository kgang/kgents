"""
W-gent Core Interceptors: Production interceptors for the Middleware Bus.

Phase 1 Interceptors (from agent-cross-pollination-final-proposal.md):
- MeteringInterceptor: B-gent token economics (no bypass)
- SafetyInterceptor: J-gent entropy/reality gating
- TelemetryInterceptor: O-gent observation emission
- PersonaInterceptor: K-gent prior injection

These interceptors implement the "integration-by-field" architecture where
agents never call each other directly - all communication flows through
the bus with interceptors applied.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable

from .bus import (
    BaseInterceptor,
    BusMessage,
    InterceptorResult,
)


# ============================================================================
# Metering Interceptor (B-gent)
# ============================================================================


@dataclass
class TokenCost:
    """Token cost estimate for an operation."""

    input_tokens: int = 0
    output_tokens: int = 0
    compute_tokens: int = 0  # For compute-intensive operations

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens + self.compute_tokens


@runtime_checkable
class CostOracle(Protocol):
    """Protocol for estimating operation costs."""

    def estimate(self, msg: BusMessage[Any, Any]) -> TokenCost:
        """Estimate the cost of processing this message."""
        ...


@runtime_checkable
class Treasury(Protocol):
    """Protocol for token budget management."""

    def can_afford(self, agent_id: str, cost: TokenCost) -> bool:
        """Check if agent has sufficient budget."""
        ...

    def debit(self, agent_id: str, cost: TokenCost) -> bool:
        """Debit tokens from agent's budget. Returns True if successful."""
        ...

    def get_balance(self, agent_id: str) -> int:
        """Get current balance for agent."""
        ...


@dataclass
class InMemoryTreasury:
    """
    Simple in-memory treasury for testing.

    Production would integrate with B-gent's CentralBank.
    """

    balances: dict[str, int] = field(default_factory=dict)
    default_balance: int = 10000

    def can_afford(self, agent_id: str, cost: TokenCost) -> bool:
        balance = self.balances.get(agent_id, self.default_balance)
        return balance >= cost.total

    def debit(self, agent_id: str, cost: TokenCost) -> bool:
        if not self.can_afford(agent_id, cost):
            return False
        if agent_id not in self.balances:
            self.balances[agent_id] = self.default_balance
        self.balances[agent_id] -= cost.total
        return True

    def get_balance(self, agent_id: str) -> int:
        return self.balances.get(agent_id, self.default_balance)


@dataclass
class SimpleCostOracle:
    """
    Simple cost oracle using fixed costs per target.

    Production would integrate with B-gent's ComplexityOracle.
    """

    costs: dict[str, TokenCost] = field(default_factory=dict)
    default_cost: TokenCost = field(default_factory=lambda: TokenCost(100, 100, 0))

    def estimate(self, msg: BusMessage[Any, Any]) -> TokenCost:
        return self.costs.get(msg.target, self.default_cost)


class MeteringInterceptor(BaseInterceptor):
    """
    B-gent: Universal token metering.

    Key insight: The "bypass" isn't free—it costs *stability*.
    Agents that don't pay for metering get noisier results.

    Order: 100-199 (after safety, before telemetry)
    """

    def __init__(
        self,
        treasury: Treasury | None = None,
        oracle: CostOracle | None = None,
        scarcity_policy: str = "latency",  # "latency" | "entropy" | "block"
        scarcity_delay: float = 0.1,  # seconds
        name: str = "metering",
    ):
        super().__init__(name, order=100)
        self.treasury = treasury or InMemoryTreasury()
        self.oracle = oracle or SimpleCostOracle()
        self.scarcity_policy = scarcity_policy
        self.scarcity_delay = scarcity_delay
        self.deficit_log: list[dict[str, Any]] = []

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        # Estimate cost
        cost = self.oracle.estimate(msg)
        msg.set_context("token_cost", cost)

        # Check budget
        if not self.treasury.can_afford(msg.source, cost):
            # Inject artificial scarcity based on policy
            if self.scarcity_policy == "block":
                msg.block(
                    f"Insufficient tokens: need {cost.total}, have {self.treasury.get_balance(msg.source)}"
                )
            elif self.scarcity_policy == "latency":
                # Delay is handled after - just log deficit
                self.deficit_log.append(
                    {
                        "agent": msg.source,
                        "cost": cost.total,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "policy": "latency",
                    }
                )
                msg.set_context("token_deficit", True)
            # "entropy" policy is handled in after() by adding noise

        else:
            # Debit tokens
            self.treasury.debit(msg.source, cost)
            msg.set_context("token_deficit", False)

        return msg

    async def after(
        self, msg: BusMessage[Any, Any], result: Any
    ) -> InterceptorResult[Any]:
        cost = msg.get_context("token_cost")
        deficit = msg.get_context("token_deficit", False)

        metadata = {
            "token_cost": cost.total if cost else 0,
            "token_deficit": deficit,
        }

        # For entropy policy, we could inject noise here
        # (not implemented - would need type-specific noise injection)

        return InterceptorResult(
            value=result,
            metadata=metadata,
        )


# ============================================================================
# Safety Interceptor (J-gent)
# ============================================================================


@dataclass
class SafetyThresholds:
    """Safety thresholds for J-gent gating."""

    max_entropy: float = 0.8  # Maximum allowed randomness/creativity
    reality_threshold: float = 0.5  # Minimum grounding in reality
    max_depth: int = 10  # Maximum recursion depth


@runtime_checkable
class EntropyChecker(Protocol):
    """Protocol for checking message entropy/risk."""

    def check_entropy(self, msg: BusMessage[Any, Any]) -> float:
        """Return entropy score (0.0 = deterministic, 1.0 = chaotic)."""
        ...

    def check_reality(self, msg: BusMessage[Any, Any]) -> float:
        """Return reality grounding score (0.0 = hallucination, 1.0 = grounded)."""
        ...


@dataclass
class SimpleEntropyChecker:
    """
    Simple entropy checker using heuristics.

    Production would integrate with J-gent's RealityAnchor.
    """

    # Targets with higher entropy risk
    high_entropy_targets: set[str] = field(
        default_factory=lambda: {"psi", "creative", "mutate"}
    )

    def check_entropy(self, msg: BusMessage[Any, Any]) -> float:
        if msg.target in self.high_entropy_targets:
            return 0.7
        return 0.3

    def check_reality(self, msg: BusMessage[Any, Any]) -> float:
        # Default: assume grounded
        return 0.8


class SafetyInterceptor(BaseInterceptor):
    """
    J-gent: Entropy and reality gating.

    Blocks messages that would exceed safety thresholds.

    Order: 0-99 (first to run - security)
    """

    def __init__(
        self,
        thresholds: SafetyThresholds | None = None,
        checker: EntropyChecker | None = None,
        name: str = "safety",
    ):
        super().__init__(name, order=50)
        self.thresholds = thresholds or SafetyThresholds()
        self.checker = checker or SimpleEntropyChecker()
        self.blocked_count = 0
        self.recursion_depths: dict[str, int] = {}

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        # Check entropy
        entropy = self.checker.check_entropy(msg)
        msg.set_context("entropy_score", entropy)

        if entropy > self.thresholds.max_entropy:
            self.blocked_count += 1
            msg.block(
                f"Entropy too high: {entropy:.2f} > {self.thresholds.max_entropy:.2f}"
            )
            return msg

        # Check reality grounding
        reality = self.checker.check_reality(msg)
        msg.set_context("reality_score", reality)

        if reality < self.thresholds.reality_threshold:
            self.blocked_count += 1
            msg.block(
                f"Reality grounding too low: {reality:.2f} < {self.thresholds.reality_threshold:.2f}"
            )
            return msg

        # Track recursion depth
        chain_key = f"{msg.source}->{msg.target}"
        current_depth = self.recursion_depths.get(chain_key, 0)
        if current_depth >= self.thresholds.max_depth:
            self.blocked_count += 1
            msg.block(
                f"Recursion depth exceeded: {current_depth} >= {self.thresholds.max_depth}"
            )
            return msg

        self.recursion_depths[chain_key] = current_depth + 1

        return msg

    async def after(
        self, msg: BusMessage[Any, Any], result: Any
    ) -> InterceptorResult[Any]:
        # Decrement recursion depth
        chain_key = f"{msg.source}->{msg.target}"
        if chain_key in self.recursion_depths:
            self.recursion_depths[chain_key] = max(
                0, self.recursion_depths[chain_key] - 1
            )

        return InterceptorResult(
            value=result,
            metadata={
                "entropy_score": msg.get_context("entropy_score", 0.0),
                "reality_score": msg.get_context("reality_score", 1.0),
            },
        )


# ============================================================================
# Telemetry Interceptor (O-gent)
# ============================================================================


@dataclass
class Observation:
    """A single observation for telemetry."""

    timestamp: datetime
    source: str
    target: str
    message_id: str
    phase: str  # "before" | "after" | "blocked"
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class ObservationSink(Protocol):
    """Protocol for emitting observations."""

    def emit(self, observation: Observation) -> None:
        """Emit an observation to the telemetry system."""
        ...


@dataclass
class InMemoryObservationSink:
    """
    Simple in-memory observation sink.

    Production would integrate with O-gent's Observer hierarchy.
    """

    observations: list[Observation] = field(default_factory=list)
    max_observations: int = 1000

    def emit(self, observation: Observation) -> None:
        self.observations.append(observation)
        if len(self.observations) > self.max_observations:
            self.observations = self.observations[-self.max_observations :]


class TelemetryInterceptor(BaseInterceptor):
    """
    O-gent: Observation emission.

    Records all message flow for observability.

    Order: 200-299 (after safety and metering)
    """

    def __init__(
        self,
        sink: ObservationSink | None = None,
        name: str = "telemetry",
    ):
        super().__init__(name, order=200)
        self.sink = sink or InMemoryObservationSink()
        self._start_times: dict[str, datetime] = {}

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        # Record start time
        self._start_times[msg.message_id] = datetime.now(timezone.utc)

        # Emit before observation
        self.sink.emit(
            Observation(
                timestamp=datetime.now(timezone.utc),
                source=msg.source,
                target=msg.target,
                message_id=msg.message_id,
                phase="before",
                metadata={
                    "priority": msg.priority.name,
                    "blocked": msg.blocked,
                },
            )
        )

        return msg

    async def after(
        self, msg: BusMessage[Any, Any], result: Any
    ) -> InterceptorResult[Any]:
        # Calculate duration
        start = self._start_times.pop(msg.message_id, None)
        duration_ms = 0.0
        if start:
            duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        # Emit after observation
        self.sink.emit(
            Observation(
                timestamp=datetime.now(timezone.utc),
                source=msg.source,
                target=msg.target,
                message_id=msg.message_id,
                phase="after",
                duration_ms=duration_ms,
                metadata={
                    "result_type": type(result).__name__,
                },
            )
        )

        return InterceptorResult(
            value=result,
            metadata={"duration_ms": duration_ms},
        )


# ============================================================================
# Persona Interceptor (K-gent)
# ============================================================================


@dataclass
class PersonaPriors:
    """
    Personality as decision-making biases.

    These priors influence how agents make decisions, not just
    how they communicate. A "risk-averse" persona doesn't just
    *talk* carefully—it *decides* carefully.
    """

    # Economic priors (B-gent)
    discount_rate: float = 0.9  # Time preference (higher = more patient)
    loss_aversion: float = 2.0  # Prospect theory (higher = more averse)
    risk_tolerance: float = 0.5  # Variance acceptance (higher = more tolerant)

    # Safety priors (J-gent)
    entropy_tolerance: float = 0.5  # Creativity vs stability
    reality_threshold: float = 0.7  # Hallucination rejection

    # Communication style (still present, not primary)
    formality: float = 0.5  # 0.0 = casual, 1.0 = formal


class PersonaInterceptor(BaseInterceptor):
    """
    K-gent: Prior injection.

    Injects personality priors into decision-making agents.
    The persona is structural, not cosmetic.

    Order: 300-399 (after telemetry)
    """

    def __init__(
        self,
        priors: PersonaPriors | None = None,
        name: str = "persona",
    ):
        super().__init__(name, order=300)
        self.priors = priors or PersonaPriors()

    async def before(self, msg: BusMessage[Any, Any]) -> BusMessage[Any, Any]:
        # Inject priors into message context
        msg.set_context("persona_priors", self.priors)

        # Adjust safety thresholds based on persona
        current_entropy_threshold = msg.get_context("entropy_threshold")
        if current_entropy_threshold is None:
            # Set based on persona's entropy tolerance
            msg.set_context("entropy_threshold", self.priors.entropy_tolerance)

        # Inject risk profile for economic decisions
        msg.set_context(
            "risk_profile",
            {
                "discount_rate": self.priors.discount_rate,
                "loss_aversion": self.priors.loss_aversion,
                "risk_tolerance": self.priors.risk_tolerance,
            },
        )

        return msg

    async def after(
        self, msg: BusMessage[Any, Any], result: Any
    ) -> InterceptorResult[Any]:
        return InterceptorResult(
            value=result,
            metadata={
                "persona_applied": True,
                "formality": self.priors.formality,
            },
        )


# ============================================================================
# Factory Functions
# ============================================================================


def create_standard_interceptors(
    treasury: Treasury | None = None,
    oracle: CostOracle | None = None,
    thresholds: SafetyThresholds | None = None,
    priors: PersonaPriors | None = None,
) -> list[BaseInterceptor]:
    """
    Create the standard interceptor stack.

    Order:
    1. SafetyInterceptor (50) - Security first
    2. MeteringInterceptor (100) - Economics
    3. TelemetryInterceptor (200) - Observability
    4. PersonaInterceptor (300) - Prior injection

    Example:
        interceptors = create_standard_interceptors()
        bus = create_bus(*interceptors)
    """
    return [
        SafetyInterceptor(thresholds=thresholds),
        MeteringInterceptor(treasury=treasury, oracle=oracle),
        TelemetryInterceptor(),
        PersonaInterceptor(priors=priors),
    ]
