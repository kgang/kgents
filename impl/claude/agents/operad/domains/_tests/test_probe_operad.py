"""
Tests for ProbeOperad: Verification probe composition grammar.

This verifies that ProbeOperad correctly implements:
- Sequential composition (p >> q)
- Parallel composition (p || q)
- Conditional composition (pred ? p : q)
- Fixed-point composition (iterate until convergence)
- Witnessed composition (trace emission)
- Operad laws (associativity, identity, trace preservation)
"""

import asyncio
from typing import Any

import pytest

from agents.operad.domains.probe import (
    ASSOCIATIVITY_LAW,
    IDENTITY_LAW,
    NullProbe,
    PROBE_OPERAD,
    ProbeProtocol,
    SequentialProbe,
    TRACE_PRESERVATION_LAW,
)
from services.categorical.dp_bridge import PolicyTrace
from services.probe.types import ProbeResult, ProbeStatus, ProbeType


# =============================================================================
# Test Probes
# =============================================================================


class AlwaysPassProbe:
    """Test probe that always passes."""

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        result = ProbeResult(
            name="always_pass",
            probe_type=ProbeType.IDENTITY,
            status=ProbeStatus.PASSED,
            details="Always passes",
            duration_ms=1.0,
        )
        return PolicyTrace.pure(result)


class AlwaysFailProbe:
    """Test probe that always fails."""

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        result = ProbeResult(
            name="always_fail",
            probe_type=ProbeType.IDENTITY,
            status=ProbeStatus.FAILED,
            details="Always fails",
            duration_ms=1.0,
        )
        return PolicyTrace.pure(result)


class CounterProbe:
    """Test probe that increments a counter."""

    def __init__(self, name: str = "counter"):
        self.name = name
        self.count = 0

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        self.count += 1
        result = ProbeResult(
            name=f"{self.name}_{self.count}",
            probe_type=ProbeType.IDENTITY,
            status=ProbeStatus.PASSED,
            details=f"Count: {self.count}",
            duration_ms=1.0,
        )
        return PolicyTrace.pure(result)


# =============================================================================
# Tests
# =============================================================================


def test_probe_operad_exists():
    """PROBE_OPERAD should be created and registered."""
    assert PROBE_OPERAD is not None
    assert PROBE_OPERAD.name == "ProbeOperad"


def test_probe_operad_has_operations():
    """PROBE_OPERAD should have 5 operations."""
    ops = list(PROBE_OPERAD.operations.keys())
    assert "seq" in ops
    assert "par" in ops
    assert "branch" in ops
    assert "fix" in ops
    assert "witness" in ops
    assert len(ops) == 5


def test_probe_operad_has_laws():
    """PROBE_OPERAD should have 3 laws."""
    laws = [law.name for law in PROBE_OPERAD.laws]
    assert "associativity" in laws
    assert "identity" in laws
    assert "trace_preservation" in laws
    assert len(laws) == 3


@pytest.mark.asyncio
async def test_sequential_composition():
    """Sequential composition should run left then right."""
    left = CounterProbe("left")
    right = CounterProbe("right")
    seq = SequentialProbe(left, right)

    result = await seq.verify("test", {})

    assert result.value.status == ProbeStatus.PASSED
    assert left.count == 1
    assert right.count == 1
    assert "left_1 >> right_1" in result.value.name


@pytest.mark.asyncio
async def test_sequential_fails_if_either_fails():
    """Sequential composition should fail if either probe fails."""
    # Left fails
    seq1 = SequentialProbe(AlwaysFailProbe(), AlwaysPassProbe())
    result1 = await seq1.verify("test", {})
    assert result1.value.failed

    # Right fails
    seq2 = SequentialProbe(AlwaysPassProbe(), AlwaysFailProbe())
    result2 = await seq2.verify("test", {})
    assert result2.value.failed


@pytest.mark.asyncio
async def test_parallel_composition():
    """Parallel composition should run both probes."""
    from agents.operad.domains.probe import ParallelProbe

    left = CounterProbe("left")
    right = CounterProbe("right")
    par = ParallelProbe(left, right)

    result = await par.verify("test", {})

    assert result.value.status == ProbeStatus.PASSED
    assert left.count == 1
    assert right.count == 1


@pytest.mark.asyncio
async def test_parallel_takes_best_result():
    """Parallel composition should take the better result."""
    from agents.operad.domains.probe import ParallelProbe

    # Both pass - should pass
    par1 = ParallelProbe(AlwaysPassProbe(), AlwaysPassProbe())
    result1 = await par1.verify("test", {})
    assert result1.value.passed

    # One passes, one fails - should pass
    par2 = ParallelProbe(AlwaysPassProbe(), AlwaysFailProbe())
    result2 = await par2.verify("test", {})
    assert result2.value.passed

    # Both fail - should fail
    par3 = ParallelProbe(AlwaysFailProbe(), AlwaysFailProbe())
    result3 = await par3.verify("test", {})
    assert result3.value.failed


@pytest.mark.asyncio
async def test_branch_composition():
    """Branch composition should choose branch based on predicate."""
    from agents.operad.domains.probe import BranchProbe

    # Predicate passes -> take true branch
    true_counter = CounterProbe("true")
    false_counter = CounterProbe("false")
    branch1 = BranchProbe(
        predicate=AlwaysPassProbe(),
        if_true=true_counter,
        if_false=false_counter,
    )
    result1 = await branch1.verify("test", {})
    assert "true-branch" in result1.value.name or "true-branch" in result1.value.details
    assert true_counter.count == 1
    assert false_counter.count == 0

    # Predicate fails -> take false branch
    true_counter2 = CounterProbe("true")
    false_counter2 = CounterProbe("false")
    branch2 = BranchProbe(
        predicate=AlwaysFailProbe(),
        if_true=true_counter2,
        if_false=false_counter2,
    )
    result2 = await branch2.verify("test", {})
    assert "false-branch" in result2.value.name or "false-branch" in result2.value.details
    assert true_counter2.count == 0
    assert false_counter2.count == 1


@pytest.mark.asyncio
async def test_witnessed_composition():
    """Witnessed composition should add trace entries."""
    from agents.operad.domains.probe import WitnessedProbe

    inner = AlwaysPassProbe()
    witnessed = WitnessedProbe(inner)

    result = await witnessed.verify("test", {})

    # Should have trace entry
    assert len(result.log) > 0
    assert result.value.passed


@pytest.mark.asyncio
async def test_null_probe_is_identity():
    """Null probe should always pass and do nothing."""
    null = NullProbe()
    result = await null.verify("test", {})

    assert result.value.passed
    assert result.value.name == "null"
    assert result.value.duration_ms == 0.0


def test_associativity_law():
    """Associativity law should verify structurally."""
    p = AlwaysPassProbe()
    q = AlwaysPassProbe()
    r = AlwaysPassProbe()

    verification = ASSOCIATIVITY_LAW.verify(p, q, r)

    # Should pass or be structural
    assert verification.passed or verification.status.name == "STRUCTURAL"


def test_identity_law():
    """Identity law should verify null probe."""
    p = AlwaysPassProbe()

    verification = IDENTITY_LAW.verify(p)

    # Should pass or be structural
    assert verification.passed or verification.status.name == "STRUCTURAL"


def test_trace_preservation_law():
    """Trace preservation law should verify witnessing."""
    p = AlwaysPassProbe()
    q = AlwaysPassProbe()

    verification = TRACE_PRESERVATION_LAW.verify(p, q)

    # Should pass or be structural
    assert verification.passed or verification.status.name == "STRUCTURAL"


@pytest.mark.asyncio
async def test_bellman_semantics_sequential():
    """Sequential composition should use Bellman value propagation."""
    # V(p >> q) = V(p) + γ·V(q)
    # Duration is our proxy for value here
    left = AlwaysPassProbe()
    right = AlwaysPassProbe()
    seq = SequentialProbe(left, right, gamma=0.99)

    result = await seq.verify("test", {})

    # Combined duration should be sum of both
    assert result.value.duration_ms >= 2.0  # Both probes contribute


@pytest.mark.asyncio
async def test_trace_accumulation():
    """Traces should accumulate through composition (Writer monad)."""
    from agents.operad.domains.probe import WitnessedProbe

    # Create witnessed probes
    p = WitnessedProbe(AlwaysPassProbe())
    q = WitnessedProbe(AlwaysPassProbe())

    # Compose sequentially
    seq = SequentialProbe(p, q)
    result = await seq.verify("test", {})

    # Should have entries from both
    assert len(result.log) >= 2


@pytest.mark.asyncio
async def test_fixed_point_convergence():
    """Fixed-point composition should iterate until convergence."""
    from agents.operad.domains.probe import FixedPointProbe

    # Probe that passes immediately
    body = AlwaysPassProbe()
    fix = FixedPointProbe(body, max_iterations=5)

    result = await fix.verify("test", {})

    # Should converge (status stabilizes)
    assert "Converged" in result.value.details or result.value.passed


def test_operad_compose_method():
    """PROBE_OPERAD.compose() should create composed probes."""
    p = AlwaysPassProbe()
    q = AlwaysPassProbe()

    # Test seq composition via operad
    composed = PROBE_OPERAD.compose("seq", p, q)
    assert isinstance(composed, SequentialProbe)


def test_operad_verify_all_laws():
    """PROBE_OPERAD should be able to verify all its laws."""
    p = AlwaysPassProbe()
    q = AlwaysPassProbe()
    r = AlwaysPassProbe()

    # This should not raise
    results = PROBE_OPERAD.verify_all_laws(p, q, r)
    assert len(results) == 3
