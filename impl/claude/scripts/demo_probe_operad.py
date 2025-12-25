#!/usr/bin/env python3
"""
Demo: ProbeOperad in Action

This script demonstrates the ProbeOperad's five operations and three laws
with concrete examples. Run this to verify the implementation works.

Usage:
    uv run python scripts/demo_probe_operad.py
"""

import asyncio
from typing import Any

from agents.operad import PROBE_OPERAD
from agents.operad.domains.probe import (
    BranchProbe,
    FixedPointProbe,
    NullProbe,
    ParallelProbe,
    SequentialProbe,
    WitnessedProbe,
)
from services.categorical.dp_bridge import PolicyTrace
from services.probe.types import ProbeResult, ProbeStatus, ProbeType


# =============================================================================
# Example Probes
# =============================================================================


class SimpleProbe:
    """A simple probe that always passes."""

    def __init__(self, name: str, duration_ms: float = 1.0):
        self.name = name
        self.duration_ms = duration_ms

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        result = ProbeResult(
            name=self.name,
            probe_type=ProbeType.IDENTITY,
            status=ProbeStatus.PASSED,
            details=f"Simple probe '{self.name}' passed",
            duration_ms=self.duration_ms,
        )
        return PolicyTrace.pure(result)


class ConditionalProbe:
    """A probe that passes if the target has a certain property."""

    def __init__(self, property_name: str):
        self.property_name = property_name

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        has_property = hasattr(target, self.property_name)
        result = ProbeResult(
            name=f"check_{self.property_name}",
            probe_type=ProbeType.IDENTITY,
            status=ProbeStatus.PASSED if has_property else ProbeStatus.FAILED,
            details=f"Property '{self.property_name}' {'found' if has_property else 'not found'}",
            duration_ms=0.5,
        )
        return PolicyTrace.pure(result)


class CountingProbe:
    """A probe that counts how many times it's been called."""

    def __init__(self, name: str):
        self.name = name
        self.count = 0

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        self.count += 1
        result = ProbeResult(
            name=f"{self.name}_call_{self.count}",
            probe_type=ProbeType.IDENTITY,
            status=ProbeStatus.PASSED,
            details=f"Call #{self.count}",
            duration_ms=0.1,
        )
        return PolicyTrace.pure(result)


# =============================================================================
# Demonstrations
# =============================================================================


async def demo_sequential():
    """Demo: Sequential composition (p >> q)."""
    print("=" * 70)
    print("DEMO 1: Sequential Composition (p >> q)")
    print("=" * 70)

    p = SimpleProbe("first_check", 10.0)
    q = SimpleProbe("second_check", 20.0)
    composed = SequentialProbe(p, q)

    result = await composed.verify("target", {})

    print(f"Result: {result.value.name}")
    print(f"Status: {result.value.status.value}")
    print(f"Duration: {result.value.duration_ms}ms (10 + 20 = 30)")
    print(f"Trace entries: {len(result.log)}")
    print()


async def demo_parallel():
    """Demo: Parallel composition (p || q)."""
    print("=" * 70)
    print("DEMO 2: Parallel Composition (p || q)")
    print("=" * 70)

    fast = SimpleProbe("fast_check", 5.0)
    slow = SimpleProbe("thorough_check", 50.0)
    composed = ParallelProbe(fast, slow)

    result = await composed.verify("target", {})

    print(f"Result: {result.value.name}")
    print(f"Status: {result.value.status.value}")
    print(f"Duration: {result.value.duration_ms}ms (max(5, 50) = 50)")
    print(f"Both probes ran concurrently")
    print()


async def demo_branch():
    """Demo: Branch composition (pred ? p : q)."""
    print("=" * 70)
    print("DEMO 3: Branch Composition (pred ? p : q)")
    print("=" * 70)

    # Create a target with a 'complex' property
    class SimpleTarget:
        complex = False

    class ComplexTarget:
        complex = True

    predicate = ConditionalProbe("complex")
    simple_check = SimpleProbe("simple_verification")
    complex_check = SimpleProbe("thorough_verification")
    branch = BranchProbe(predicate, complex_check, simple_check)

    # Test with simple target
    simple_target = SimpleTarget()
    result1 = await branch.verify(simple_target, {})
    print(f"Simple target: {result1.value.details}")

    # Test with complex target
    complex_target = ComplexTarget()
    result2 = await branch.verify(complex_target, {})
    print(f"Complex target: {result2.value.details}")
    print()


async def demo_fixed_point():
    """Demo: Fixed-point composition (iterate until convergence)."""
    print("=" * 70)
    print("DEMO 4: Fixed-Point Composition (iterate until convergence)")
    print("=" * 70)

    counter = CountingProbe("refinement")
    fix = FixedPointProbe(counter, max_iterations=5)

    result = await fix.verify("target", {})

    print(f"Result: {result.value.name}")
    print(f"Iterations: {counter.count}")
    print(f"Converged: {'Converged' in result.value.details}")
    print()


async def demo_witnessed():
    """Demo: Witnessed composition (trace emission)."""
    print("=" * 70)
    print("DEMO 5: Witnessed Composition (trace emission)")
    print("=" * 70)

    inner = SimpleProbe("important_check")
    witnessed = WitnessedProbe(inner)

    result = await witnessed.verify("target", {})

    print(f"Result: {result.value.name}")
    print(f"Trace entries: {len(result.log)}")
    print(f"First entry: {result.log[0].action if result.log else 'None'}")
    print()


async def demo_laws():
    """Demo: Operad laws verification."""
    print("=" * 70)
    print("DEMO 6: Operad Laws Verification")
    print("=" * 70)

    p = SimpleProbe("p")
    q = SimpleProbe("q")
    r = SimpleProbe("r")

    # Verify all laws
    results = PROBE_OPERAD.verify_all_laws(p, q, r)

    for result in results:
        status_symbol = "✓" if result.passed else "✗"
        print(f"{status_symbol} {result.law_name}: {result.status.value}")

    print()


async def demo_operad_compose():
    """Demo: Using PROBE_OPERAD.compose()."""
    print("=" * 70)
    print("DEMO 7: Using PROBE_OPERAD.compose()")
    print("=" * 70)

    p = SimpleProbe("check_a")
    q = SimpleProbe("check_b")

    # Compose via operad
    composed = PROBE_OPERAD.compose("seq", p, q)

    result = await composed.verify("target", {})

    print(f"Composed via operad: {result.value.name}")
    print(f"Status: {result.value.status.value}")
    print()


async def demo_complex_composition():
    """Demo: Complex multi-level composition."""
    print("=" * 70)
    print("DEMO 8: Complex Multi-Level Composition")
    print("=" * 70)

    # Build a complex verification pipeline:
    # ((p || q) >> r) with witnessing

    p = SimpleProbe("fast_syntax_check", 5.0)
    q = SimpleProbe("thorough_syntax_check", 20.0)
    r = SimpleProbe("semantic_check", 15.0)

    # Parallel: try both syntax checks
    syntax = ParallelProbe(p, q)

    # Sequential: syntax then semantics
    full_check = SequentialProbe(syntax, r)

    # Witnessed: ensure tracing
    witnessed = WitnessedProbe(full_check)

    result = await witnessed.verify("code", {})

    print(f"Complex pipeline result:")
    print(f"  Name: {result.value.name}")
    print(f"  Status: {result.value.status.value}")
    print(f"  Duration: {result.value.duration_ms}ms")
    print(f"  Trace entries: {len(result.log)}")
    print()


# =============================================================================
# Main
# =============================================================================


async def main():
    """Run all demonstrations."""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║           ProbeOperad Demonstration Suite                         ║")
    print("║                                                                    ║")
    print("║  Showcasing the five operations and three laws                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

    # Run demos
    await demo_sequential()
    await demo_parallel()
    await demo_branch()
    await demo_fixed_point()
    await demo_witnessed()
    await demo_laws()
    await demo_operad_compose()
    await demo_complex_composition()

    print("=" * 70)
    print("All demonstrations complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
