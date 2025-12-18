"""
Tests for W-gent Core Interceptors (Phase 1).

Tests verify:
- MeteringInterceptor (B-gent token economics)
- SafetyInterceptor (J-gent entropy/reality gating)
- TelemetryInterceptor (O-gent observation emission)
- PersonaInterceptor (K-gent prior injection)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import pytest

from agents.w.bus import (
    BusMessage,
    DispatchResult,
    create_bus,
)
from agents.w.interceptors import (
    InMemoryObservationSink,
    InMemoryTreasury,
    MeteringInterceptor,
    # Telemetry
    Observation,
    PersonaInterceptor,
    # Persona
    PersonaPriors,
    SafetyInterceptor,
    # Safety
    SafetyThresholds,
    SimpleCostOracle,
    TelemetryInterceptor,
    # Metering
    TokenCost,
    # Factory
    create_standard_interceptors,
)

# --- Test Agents ---


@dataclass
class EchoAgent:
    """Returns input unchanged."""

    name: str = "echo"

    async def invoke(self, input: Any) -> Any:
        return input


@dataclass
class DoubleAgent:
    """Doubles numeric input."""

    name: str = "double"

    async def invoke(self, input: int) -> int:
        return input * 2


# --- TokenCost Tests ---


class TestTokenCost:
    """Tests for TokenCost dataclass."""

    def test_total_computation(self) -> None:
        """Test total property."""
        cost = TokenCost(input_tokens=100, output_tokens=200, compute_tokens=50)
        assert cost.total == 350

    def test_default_values(self) -> None:
        """Test default values are zero."""
        cost = TokenCost()
        assert cost.total == 0


# --- InMemoryTreasury Tests ---


class TestInMemoryTreasury:
    """Tests for InMemoryTreasury."""

    @pytest.fixture
    def treasury(self) -> InMemoryTreasury:
        return InMemoryTreasury(default_balance=1000)

    def test_can_afford_with_default(self, treasury: InMemoryTreasury) -> None:
        """Test affordability with default balance."""
        cost = TokenCost(input_tokens=500)
        assert treasury.can_afford("agent-1", cost)

    def test_can_afford_exact(self, treasury: InMemoryTreasury) -> None:
        """Test affordability at exact balance."""
        cost = TokenCost(input_tokens=1000)
        assert treasury.can_afford("agent-1", cost)

    def test_cannot_afford_exceeds(self, treasury: InMemoryTreasury) -> None:
        """Test cannot afford when exceeds balance."""
        cost = TokenCost(input_tokens=1001)
        assert not treasury.can_afford("agent-1", cost)

    def test_debit_updates_balance(self, treasury: InMemoryTreasury) -> None:
        """Test debit reduces balance."""
        cost = TokenCost(input_tokens=300)
        assert treasury.debit("agent-1", cost)
        assert treasury.get_balance("agent-1") == 700

    def test_debit_fails_insufficient(self, treasury: InMemoryTreasury) -> None:
        """Test debit fails when insufficient funds."""
        treasury.balances["agent-1"] = 100
        cost = TokenCost(input_tokens=500)
        assert not treasury.debit("agent-1", cost)
        assert treasury.get_balance("agent-1") == 100


# --- MeteringInterceptor Tests ---


class TestMeteringInterceptor:
    """Tests for MeteringInterceptor."""

    @pytest.fixture
    def metering(self) -> MeteringInterceptor:
        treasury = InMemoryTreasury(default_balance=1000)
        oracle = SimpleCostOracle(default_cost=TokenCost(100, 100, 0))
        return MeteringInterceptor(
            treasury=treasury,
            oracle=oracle,
            scarcity_policy="block",
        )

    @pytest.mark.asyncio
    async def test_debit_on_dispatch(self, metering: MeteringInterceptor) -> None:
        """Test tokens debited on successful dispatch."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await metering.before(msg)

        assert not msg.blocked
        assert metering.treasury.get_balance("cli") == 800  # 1000 - 200

    @pytest.mark.asyncio
    async def test_block_on_insufficient(self, metering: MeteringInterceptor) -> None:
        """Test message blocked when insufficient tokens."""
        metering.treasury.balances["cli"] = 50  # type: ignore[attr-defined]
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await metering.before(msg)

        assert msg.blocked
        assert msg.block_reason is not None
        assert "Insufficient tokens" in msg.block_reason

    @pytest.mark.asyncio
    async def test_context_contains_cost(self, metering: MeteringInterceptor) -> None:
        """Test cost added to message context."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await metering.before(msg)

        cost = msg.get_context("token_cost")
        assert cost is not None
        assert cost.total == 200

    @pytest.mark.asyncio
    async def test_latency_policy_logs_deficit(self) -> None:
        """Test latency policy logs deficit instead of blocking."""
        treasury = InMemoryTreasury(default_balance=0)
        metering = MeteringInterceptor(
            treasury=treasury,
            scarcity_policy="latency",
        )

        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await metering.before(msg)

        assert not msg.blocked
        assert msg.get_context("token_deficit") is True
        assert len(metering.deficit_log) == 1


# --- SafetyThresholds Tests ---


class TestSafetyThresholds:
    """Tests for SafetyThresholds."""

    def test_default_values(self) -> None:
        """Test sensible defaults."""
        thresholds = SafetyThresholds()
        assert thresholds.max_entropy == 0.8
        assert thresholds.reality_threshold == 0.5
        assert thresholds.max_depth == 10


# --- SafetyInterceptor Tests ---


class TestSafetyInterceptor:
    """Tests for SafetyInterceptor."""

    @pytest.fixture
    def safety(self) -> SafetyInterceptor:
        return SafetyInterceptor(
            thresholds=SafetyThresholds(max_entropy=0.5),
        )

    @pytest.mark.asyncio
    async def test_low_entropy_passes(self, safety: SafetyInterceptor) -> None:
        """Test low entropy message passes."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await safety.before(msg)

        assert not msg.blocked

    @pytest.mark.asyncio
    async def test_high_entropy_blocked(self, safety: SafetyInterceptor) -> None:
        """Test high entropy message blocked."""
        # "psi" target has entropy 0.7 in SimpleEntropyChecker
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="psi", payload="creative task")
        await safety.before(msg)

        assert msg.blocked
        assert msg.block_reason is not None
        assert "Entropy too high" in msg.block_reason

    @pytest.mark.asyncio
    async def test_custom_entropy_checker(self) -> None:
        """Test with custom entropy checker."""

        class AlwaysHighEntropy:
            def check_entropy(self, msg: BusMessage[Any, Any]) -> float:
                return 0.9

            def check_reality(self, msg: BusMessage[Any, Any]) -> float:
                return 0.8

        safety = SafetyInterceptor(checker=AlwaysHighEntropy())
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await safety.before(msg)

        assert msg.blocked

    @pytest.mark.asyncio
    async def test_recursion_depth_tracking(self, safety: SafetyInterceptor) -> None:
        """Test recursion depth is tracked."""
        safety.thresholds.max_depth = 2

        # First two calls should pass
        for _ in range(2):
            msg1: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
            await safety.before(msg1)
            assert not msg1.blocked

        # Third call should be blocked
        msg2: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await safety.before(msg2)
        assert msg2.blocked
        assert msg2.block_reason is not None
        assert "Recursion depth exceeded" in msg2.block_reason

    @pytest.mark.asyncio
    async def test_recursion_depth_decremented_after(self, safety: SafetyInterceptor) -> None:
        """Test recursion depth decremented in after hook."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await safety.before(msg)
        await safety.after(msg, "result")

        # Depth should be back to 0
        chain_key = "cli->echo"
        assert safety.recursion_depths.get(chain_key, 0) == 0


# --- TelemetryInterceptor Tests ---


class TestTelemetryInterceptor:
    """Tests for TelemetryInterceptor."""

    @pytest.fixture
    def sink(self) -> InMemoryObservationSink:
        return InMemoryObservationSink()

    @pytest.fixture
    def telemetry(self, sink: InMemoryObservationSink) -> TelemetryInterceptor:
        return TelemetryInterceptor(sink=sink)

    @pytest.mark.asyncio
    async def test_emits_before_observation(
        self, telemetry: TelemetryInterceptor, sink: InMemoryObservationSink
    ) -> None:
        """Test observation emitted in before hook."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await telemetry.before(msg)

        assert len(sink.observations) == 1
        obs = sink.observations[0]
        assert obs.phase == "before"
        assert obs.source == "cli"
        assert obs.target == "echo"

    @pytest.mark.asyncio
    async def test_emits_after_observation(
        self, telemetry: TelemetryInterceptor, sink: InMemoryObservationSink
    ) -> None:
        """Test observation emitted in after hook."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await telemetry.before(msg)
        await telemetry.after(msg, "result")

        assert len(sink.observations) == 2
        obs = sink.observations[1]
        assert obs.phase == "after"
        assert obs.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_tracks_duration(
        self, telemetry: TelemetryInterceptor, sink: InMemoryObservationSink
    ) -> None:
        """Test duration is calculated."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await telemetry.before(msg)

        # Small delay to get measurable duration
        import asyncio

        await asyncio.sleep(0.01)

        await telemetry.after(msg, "result")

        obs = sink.observations[1]
        assert obs.duration_ms >= 10  # At least 10ms

    def test_sink_max_observations(self) -> None:
        """Test sink respects max observations."""
        sink = InMemoryObservationSink(max_observations=5)
        for i in range(10):
            sink.emit(
                Observation(
                    timestamp=None,  # type: ignore
                    source="cli",
                    target="echo",
                    message_id=f"msg-{i}",
                    phase="before",
                )
            )

        assert len(sink.observations) == 5
        # Should have kept most recent
        assert sink.observations[-1].message_id == "msg-9"


# --- PersonaPriors Tests ---


class TestPersonaPriors:
    """Tests for PersonaPriors."""

    def test_default_values(self) -> None:
        """Test sensible defaults."""
        priors = PersonaPriors()
        assert priors.discount_rate == 0.9
        assert priors.risk_tolerance == 0.5
        assert priors.formality == 0.5

    def test_custom_values(self) -> None:
        """Test custom prior configuration."""
        priors = PersonaPriors(
            discount_rate=0.7,
            loss_aversion=3.0,
            entropy_tolerance=0.8,
        )
        assert priors.discount_rate == 0.7
        assert priors.loss_aversion == 3.0


# --- PersonaInterceptor Tests ---


class TestPersonaInterceptor:
    """Tests for PersonaInterceptor."""

    @pytest.fixture
    def persona(self) -> PersonaInterceptor:
        return PersonaInterceptor(
            priors=PersonaPriors(
                risk_tolerance=0.3,
                entropy_tolerance=0.4,
            ),
        )

    @pytest.mark.asyncio
    async def test_injects_priors(self, persona: PersonaInterceptor) -> None:
        """Test priors injected into message context."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await persona.before(msg)

        priors = msg.get_context("persona_priors")
        assert priors is not None
        assert priors.risk_tolerance == 0.3

    @pytest.mark.asyncio
    async def test_sets_entropy_threshold(self, persona: PersonaInterceptor) -> None:
        """Test entropy threshold set from persona."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await persona.before(msg)

        threshold = msg.get_context("entropy_threshold")
        assert threshold == 0.4

    @pytest.mark.asyncio
    async def test_risk_profile_injected(self, persona: PersonaInterceptor) -> None:
        """Test risk profile injected."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await persona.before(msg)

        profile = msg.get_context("risk_profile")
        assert profile is not None
        assert profile["risk_tolerance"] == 0.3

    @pytest.mark.asyncio
    async def test_after_adds_metadata(self, persona: PersonaInterceptor) -> None:
        """Test after hook adds persona metadata."""
        msg: BusMessage[str, Any] = BusMessage(source="cli", target="echo", payload="test")
        await persona.before(msg)
        result = await persona.after(msg, "output")

        assert result.metadata["persona_applied"] is True


# --- create_standard_interceptors Tests ---


class TestCreateStandardInterceptors:
    """Tests for create_standard_interceptors factory."""

    def test_creates_four_interceptors(self) -> None:
        """Test creates all four standard interceptors."""
        interceptors = create_standard_interceptors()
        assert len(interceptors) == 4

    def test_correct_order(self) -> None:
        """Test interceptors are in correct order."""
        interceptors = create_standard_interceptors()
        orders = [i.order for i in interceptors]
        assert orders == sorted(orders)

        # Specific orders
        assert interceptors[0].name == "safety"  # 50
        assert interceptors[1].name == "metering"  # 100
        assert interceptors[2].name == "telemetry"  # 200
        assert interceptors[3].name == "persona"  # 300

    def test_custom_components(self) -> None:
        """Test with custom components."""
        treasury = InMemoryTreasury(default_balance=5000)
        priors = PersonaPriors(risk_tolerance=0.1)

        interceptors = create_standard_interceptors(
            treasury=treasury,
            priors=priors,
        )

        # Find metering and verify custom treasury
        metering = next(i for i in interceptors if i.name == "metering")
        assert metering.treasury.default_balance == 5000  # type: ignore[attr-defined]

        # Find persona and verify custom priors
        persona = next(i for i in interceptors if i.name == "persona")
        assert persona.priors.risk_tolerance == 0.1  # type: ignore[attr-defined]


# --- Integration Tests ---


class TestInterceptorsIntegration:
    """Integration tests with full bus."""

    @pytest.mark.asyncio
    async def test_full_interceptor_stack(self) -> None:
        """Test all interceptors working together."""
        # Create bus with standard interceptors
        interceptors = create_standard_interceptors()
        bus = create_bus(*interceptors)
        bus.registry.register("echo", EchoAgent())

        result: DispatchResult[str] = await bus.send("cli", "echo", "test")

        # Should succeed
        assert not result.blocked
        assert result.value == "test"

        # Should have metadata from all interceptors
        assert "token_cost" in result.metadata
        assert "entropy_score" in result.metadata
        assert "duration_ms" in result.metadata
        assert "persona_applied" in result.metadata

    @pytest.mark.asyncio
    async def test_safety_blocks_before_metering(self) -> None:
        """Test safety blocks before metering debits tokens."""
        treasury = InMemoryTreasury(default_balance=1000)

        interceptors = create_standard_interceptors(
            treasury=treasury,
            thresholds=SafetyThresholds(max_entropy=0.0),  # Block everything
        )
        bus = create_bus(*interceptors)
        bus.registry.register("echo", EchoAgent())

        result: DispatchResult[str] = await bus.send("cli", "echo", "test")

        # Should be blocked by safety
        assert result.blocked
        assert result.block_reason is not None
        assert "Entropy" in result.block_reason

        # Tokens should NOT be debited (safety ran first)
        assert treasury.get_balance("cli") == 1000

    @pytest.mark.asyncio
    async def test_telemetry_records_blocked(self) -> None:
        """Test telemetry records messages even when later blocked."""
        sink = InMemoryObservationSink()

        # Put telemetry BEFORE safety so it records the before event
        # In production, telemetry is typically after safety, but this test
        # verifies telemetry works for messages that get blocked later
        telemetry = TelemetryInterceptor(sink=sink)
        telemetry._order = 10  # Run before safety (50)

        interceptors = [
            telemetry,
            SafetyInterceptor(thresholds=SafetyThresholds(max_entropy=0.0)),
        ]
        bus = create_bus(*interceptors)
        bus.registry.register("echo", EchoAgent())

        await bus.send("cli", "echo", "test")

        # Should have before observation
        before_obs = [o for o in sink.observations if o.phase == "before"]
        assert len(before_obs) >= 1

    @pytest.mark.asyncio
    async def test_persona_priors_available_to_agent(self) -> None:
        """Test persona priors are available in message context."""
        priors = PersonaPriors(risk_tolerance=0.2)
        interceptors = create_standard_interceptors(priors=priors)
        bus = create_bus(*interceptors)

        # Create agent that checks context
        @dataclass
        class ContextCheckingAgent:
            name: str = "context-checker"
            last_priors: Optional[PersonaPriors] = None

            async def invoke(self, input: Any) -> str:
                # In real use, agent would receive context via other mechanism
                # This tests that priors are set
                return "ok"

        bus.registry.register("checker", ContextCheckingAgent())

        result: DispatchResult[str] = await bus.send("cli", "checker", "test")
        assert result.value == "ok"
        assert result.metadata.get("persona_applied") is True
