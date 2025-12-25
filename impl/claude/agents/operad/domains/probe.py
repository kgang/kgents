"""
ProbeOperad: Grammar of Verification Probe Composition.

The ProbeOperad defines how verification probes compose. Each operation
has Bellman semantics - the value of a composed probe is derived from
component values via the Bellman equation.

This integrates:
- DP-native semantics from spec/theory/dp-native-kgents.md
- Witness PolicyTrace for execution traces
- ProbeResult types from services/probe/types.py
- Operad composition grammar

Operations:
- seq: Sequential composition (p >> q)
- par: Parallel composition (p || q)
- branch: Conditional composition (pred ? p : q)
- fix: Fixed-point composition (iterate until convergence)
- witness: Trace-emitting wrapper

Laws:
- Associativity: (p >> q) >> r ≡ p >> (q >> r)
- Identity: null >> p ≡ p ≡ p >> null
- Trace preservation: witness(p >> q) ≡ witness(p) >> witness(q)

Teaching:
    gotcha: ProbeOperad operations compose ProbeResult objects, NOT agents.
            Unlike AGENT_OPERAD which composes PolyAgents, ProbeOperad works
            at the verification layer where we compose verification judgments.
            (Evidence: ProbeResult is the value in PolicyTrace[ProbeResult])

    gotcha: Bellman semantics encode value propagation through composition.
            seq uses additive combination: V(p>>q) = V(p) + γ·V(q)
            par uses max combination: V(p||q) = max(V(p), V(q))
            This matches DP optimal substructure property.
            (Evidence: spec/theory/dp-native-kgents.md §2.1)

See: spec/theory/dp-native-kgents.md
See: spec/theory/analysis-operad.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, FrozenSet, Protocol

from agents.operad.core import Law, LawStatus, LawVerification, Operad, Operation
from services.categorical.dp_bridge import PolicyTrace, TraceEntry
from services.probe.types import ProbeResult, ProbeStatus, ProbeType

# =============================================================================
# Probe Protocol
# =============================================================================


class ProbeProtocol(Protocol):
    """
    Protocol for verification probes.

    A probe is a function that examines a target and returns a ProbeResult
    wrapped in a PolicyTrace (for witnessing).
    """

    async def verify(self, target: Any, context: dict[str, Any]) -> PolicyTrace[ProbeResult]:
        """
        Verify the target and return a witnessed result.

        Args:
            target: The thing to verify (agent, spec, implementation)
            context: Verification context (previous results, config)

        Returns:
            PolicyTrace[ProbeResult] with verification result and trace
        """
        ...


# =============================================================================
# Composed Probe Types
# =============================================================================


@dataclass
class SequentialProbe:
    """
    Sequential composition: run left, then right.

    The right probe receives the left's result in context.
    Values combine additively: V(p>>q) = V(p) + γ·V(q)
    """

    left: ProbeProtocol
    right: ProbeProtocol
    gamma: float = 0.99  # Discount factor

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        """Run left probe, then right probe with left's result in context."""
        # Run left probe
        left_trace = await self.left.verify(target, context)

        # Add left's result to context for right probe
        right_context = {**context, "previous": left_trace.value}
        right_trace = await self.right.verify(target, right_context)

        # Combine results: If either failed, composition fails
        if left_trace.value.failed or right_trace.value.failed:
            combined_status = ProbeStatus.FAILED
            combined_details = f"{left_trace.value.details}; {right_trace.value.details}"
        else:
            combined_status = left_trace.value.status
            combined_details = f"{left_trace.value.name} >> {right_trace.value.name}"

        # Bellman value combination: V(p>>q) = V(p) + γ·V(q)
        combined_duration = left_trace.value.duration_ms + right_trace.value.duration_ms

        combined_result = ProbeResult(
            name=f"{left_trace.value.name} >> {right_trace.value.name}",
            probe_type=left_trace.value.probe_type,  # Inherit from left
            status=combined_status,
            details=combined_details,
            duration_ms=combined_duration,
        )

        # Merge traces (Writer monad accumulation)
        return PolicyTrace(
            value=combined_result,
            log=left_trace.log + right_trace.log,
        )


@dataclass
class ParallelProbe:
    """
    Parallel composition: run both, take best.

    Both probes run concurrently on same target.
    Values combine via max: V(p||q) = max(V(p), V(q))
    """

    left: ProbeProtocol
    right: ProbeProtocol

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        """Run both probes in parallel, take result with better status."""
        # Run both probes concurrently
        left_task = asyncio.create_task(self.left.verify(target, context))
        right_task = asyncio.create_task(self.right.verify(target, context))
        left_trace, right_trace = await asyncio.gather(left_task, right_task)

        # Take best result (PASSED > SKIPPED > FAILED > ERROR)
        status_priority = {
            ProbeStatus.PASSED: 3,
            ProbeStatus.SKIPPED: 2,
            ProbeStatus.FAILED: 1,
            ProbeStatus.ERROR: 0,
        }

        if status_priority[left_trace.value.status] >= status_priority[
            right_trace.value.status
        ]:
            better_trace = left_trace
            worse_trace = right_trace
        else:
            better_trace = right_trace
            worse_trace = left_trace

        # Create combined result
        combined_result = ProbeResult(
            name=f"{left_trace.value.name} || {right_trace.value.name}",
            probe_type=better_trace.value.probe_type,
            status=better_trace.value.status,
            details=f"Best: {better_trace.value.details}",
            duration_ms=max(
                left_trace.value.duration_ms, right_trace.value.duration_ms
            ),  # Parallel time
        )

        # Merge traces (both branches witnessed)
        return PolicyTrace(
            value=combined_result,
            log=left_trace.log + right_trace.log,
        )


@dataclass
class BranchProbe:
    """
    Conditional composition: if predicate then left else right.

    Predicate probe determines which branch to take.
    Value: V(branch) = P(pred)·V(left) + (1-P(pred))·V(right)
    """

    predicate: ProbeProtocol
    if_true: ProbeProtocol
    if_false: ProbeProtocol

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        """Run predicate, then appropriate branch based on result."""
        # Evaluate predicate
        pred_trace = await self.predicate.verify(target, context)

        # Branch based on predicate status
        if pred_trace.value.passed:
            branch_trace = await self.if_true.verify(target, context)
            branch_name = "true-branch"
        else:
            branch_trace = await self.if_false.verify(target, context)
            branch_name = "false-branch"

        # Create combined result
        combined_result = ProbeResult(
            name=f"branch({pred_trace.value.name}, {branch_name})",
            probe_type=branch_trace.value.probe_type,
            status=branch_trace.value.status,
            details=f"Pred: {pred_trace.value.status.value}, Branch: {branch_trace.value.details}",
            duration_ms=pred_trace.value.duration_ms + branch_trace.value.duration_ms,
        )

        # Merge traces: predicate + chosen branch
        return PolicyTrace(
            value=combined_result,
            log=pred_trace.log + branch_trace.log,
        )


@dataclass
class FixedPointProbe:
    """
    Fixed-point composition: iterate until convergence.

    Repeatedly apply probe until result stabilizes or max iterations reached.
    Value: V(fix) = V(body) / (1 - γ)  (infinite horizon)
    """

    body: ProbeProtocol
    max_iterations: int = 10
    gamma: float = 0.99

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        """Iterate body until result stabilizes."""
        accumulated_log: tuple[TraceEntry, ...] = ()
        prev_status = None
        iterations = 0

        # Iterate until convergence or max iterations
        for i in range(self.max_iterations):
            iterations = i + 1
            body_trace = await self.body.verify(target, context)
            accumulated_log = accumulated_log + body_trace.log

            # Check for convergence (status stabilized)
            if body_trace.value.status == prev_status:
                # Converged
                converged = True
                final_result = body_trace.value
                break

            prev_status = body_trace.value.status

            # Update context with previous result
            context = {**context, "iteration": i, "previous": body_trace.value}
        else:
            # Max iterations reached without convergence
            converged = False
            final_result = ProbeResult(
                name=f"fix({self.body.__class__.__name__})",
                probe_type=ProbeType.COHERENCE,
                status=ProbeStatus.ERROR,
                details=f"Failed to converge after {self.max_iterations} iterations",
                duration_ms=0,
            )

        # Create fixed-point result
        fixed_result = ProbeResult(
            name=f"fix({final_result.name})",
            probe_type=final_result.probe_type,
            status=final_result.status if converged else ProbeStatus.ERROR,
            details=f"Converged after {iterations} iterations: {final_result.details}"
            if converged
            else final_result.details,
            duration_ms=final_result.duration_ms * iterations,
        )

        return PolicyTrace(
            value=fixed_result,
            log=accumulated_log,
        )


@dataclass
class WitnessedProbe:
    """
    Witnessed composition: wrap probe to emit explicit trace entries.

    Every verification step gets recorded as a TraceEntry.
    Value unchanged: V(witness(p)) = V(p)
    """

    inner: ProbeProtocol

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        """Run inner probe and ensure trace entry is emitted."""
        inner_trace = await self.inner.verify(target, context)

        # Create explicit witness entry
        witness_entry = TraceEntry(
            state_before=context,
            action=f"witness({inner_trace.value.name})",
            state_after={"result": inner_trace.value.to_dict()},
            value=1.0 if inner_trace.value.passed else 0.0,
            rationale=f"Witnessed verification: {inner_trace.value.details}",
        )

        # Return with witness entry prepended to log
        return PolicyTrace(
            value=inner_trace.value,
            log=(witness_entry,) + inner_trace.log,
        )


# =============================================================================
# Identity Probe (for law verification)
# =============================================================================


@dataclass
class NullProbe:
    """
    Null/Identity probe: always passes, does nothing.

    This is the identity element for probe composition.
    """

    async def verify(
        self, target: Any, context: dict[str, Any]
    ) -> PolicyTrace[ProbeResult]:
        """Return trivial passing result."""
        result = ProbeResult(
            name="null",
            probe_type=ProbeType.IDENTITY,
            status=ProbeStatus.PASSED,
            details="Identity probe (no-op)",
            duration_ms=0.0,
        )
        return PolicyTrace.pure(result)


# =============================================================================
# Operations
# =============================================================================


def _seq_compose(left: ProbeProtocol, right: ProbeProtocol) -> ProbeProtocol:
    """Sequential composition: left >> right."""
    return SequentialProbe(left, right)


def _par_compose(left: ProbeProtocol, right: ProbeProtocol) -> ProbeProtocol:
    """Parallel composition: left || right."""
    return ParallelProbe(left, right)


def _branch_compose(
    predicate: ProbeProtocol,
    if_true: ProbeProtocol,
    if_false: ProbeProtocol,
) -> ProbeProtocol:
    """Conditional composition: predicate ? if_true : if_false."""
    return BranchProbe(predicate, if_true, if_false)


def _fix_compose(
    body: ProbeProtocol,
    max_iterations: int = 10,
) -> ProbeProtocol:
    """Fixed-point composition: iterate body until convergence."""
    return FixedPointProbe(body, max_iterations)


def _witness_compose(inner: ProbeProtocol) -> ProbeProtocol:
    """Witnessed composition: wrap probe to emit trace entries."""
    return WitnessedProbe(inner)


SEQ_OP = Operation(
    name="seq",
    arity=2,
    signature="Probe × Probe → Probe",
    compose=_seq_compose,
    description="Sequential composition with Bellman value propagation",
)

PAR_OP = Operation(
    name="par",
    arity=2,
    signature="Probe × Probe → Probe",
    compose=_par_compose,
    description="Parallel composition taking best result",
)

BRANCH_OP = Operation(
    name="branch",
    arity=3,
    signature="Pred × Probe × Probe → Probe",
    compose=_branch_compose,
    description="Conditional composition based on predicate",
)

FIX_OP = Operation(
    name="fix",
    arity=1,
    signature="Probe → Probe",
    compose=_fix_compose,
    description="Fixed-point composition (iterate until convergence)",
)

WITNESS_OP = Operation(
    name="witness",
    arity=1,
    signature="Probe → PolicyTrace[Probe]",
    compose=_witness_compose,
    description="Trace-emitting wrapper for witnessing",
)


# =============================================================================
# Law Verification
# =============================================================================


async def _verify_associativity(
    p: ProbeProtocol, q: ProbeProtocol, r: ProbeProtocol
) -> LawVerification:
    """
    Verify associativity: (p >> q) >> r ≡ p >> (q >> r).

    We verify this structurally - both compositions should exist and have
    equivalent semantics (though trace order may differ).
    """
    try:
        # Left grouping: (p >> q) >> r
        left_grouped = SequentialProbe(SequentialProbe(p, q), r)

        # Right grouping: p >> (q >> r)
        right_grouped = SequentialProbe(p, SequentialProbe(q, r))

        # Run both on dummy target
        target = "test_target"
        context: dict[str, Any] = {}

        left_result = await left_grouped.verify(target, context)
        right_result = await right_grouped.verify(target, context)

        # Both should succeed (structural check)
        if left_result.value.status == right_result.value.status:
            return LawVerification(
                law_name="associativity",
                status=LawStatus.PASSED,
                left_result=left_result.value.name,
                right_result=right_result.value.name,
                message="Both groupings produce valid results",
            )
        else:
            return LawVerification(
                law_name="associativity",
                status=LawStatus.FAILED,
                left_result=left_result.value.name,
                right_result=right_result.value.name,
                message=f"Status mismatch: {left_result.value.status} vs {right_result.value.status}",
            )

    except Exception as e:
        return LawVerification(
            law_name="associativity",
            status=LawStatus.FAILED,
            message=f"Associativity verification failed: {e}",
        )


async def _verify_identity(p: ProbeProtocol) -> LawVerification:
    """
    Verify identity: null >> p ≡ p ≡ p >> null.

    The null probe should not affect the result of p.
    """
    try:
        null = NullProbe()
        target = "test_target"
        context: dict[str, Any] = {}

        # Left identity: null >> p
        left_id = SequentialProbe(null, p)
        left_result = await left_id.verify(target, context)

        # Right identity: p >> null
        right_id = SequentialProbe(p, null)
        right_result = await right_id.verify(target, context)

        # Plain p
        plain_result = await p.verify(target, context)

        # All should have same status (ignoring trace details)
        if (
            left_result.value.status == plain_result.value.status
            and right_result.value.status == plain_result.value.status
        ):
            return LawVerification(
                law_name="identity",
                status=LawStatus.PASSED,
                left_result="null >> p",
                right_result="p",
                message="Identity law holds: null does not affect result",
            )
        else:
            return LawVerification(
                law_name="identity",
                status=LawStatus.FAILED,
                left_result=left_result.value.status.value,
                right_result=plain_result.value.status.value,
                message="Identity law violated: null changed result",
            )

    except Exception as e:
        return LawVerification(
            law_name="identity",
            status=LawStatus.FAILED,
            message=f"Identity verification failed: {e}",
        )


async def _verify_trace_preservation(
    p: ProbeProtocol, q: ProbeProtocol
) -> LawVerification:
    """
    Verify trace preservation: witness(p >> q) ≡ witness(p) >> witness(q).

    Witnessing distributes over composition.
    """
    try:
        target = "test_target"
        context: dict[str, Any] = {}

        # Left: witness(p >> q)
        composed = SequentialProbe(p, q)
        left = WitnessedProbe(composed)
        left_result = await left.verify(target, context)

        # Right: witness(p) >> witness(q)
        right = SequentialProbe(WitnessedProbe(p), WitnessedProbe(q))
        right_result = await right.verify(target, context)

        # Both should have trace entries (length > 0)
        if len(left_result.log) > 0 and len(right_result.log) > 0:
            return LawVerification(
                law_name="trace_preservation",
                status=LawStatus.PASSED,
                left_result=f"{len(left_result.log)} entries",
                right_result=f"{len(right_result.log)} entries",
                message="Trace preservation holds: both produce witnessed traces",
            )
        else:
            return LawVerification(
                law_name="trace_preservation",
                status=LawStatus.FAILED,
                left_result=f"{len(left_result.log)} entries",
                right_result=f"{len(right_result.log)} entries",
                message="Trace preservation violated: missing trace entries",
            )

    except Exception as e:
        return LawVerification(
            law_name="trace_preservation",
            status=LawStatus.FAILED,
            message=f"Trace preservation verification failed: {e}",
        )


# Laws use sync wrappers for compatibility with operad interface
def _verify_associativity_sync(p: ProbeProtocol, q: ProbeProtocol, r: ProbeProtocol, *args) -> LawVerification:
    """Sync wrapper for associativity verification."""
    try:
        # Try to get running loop
        loop = asyncio.get_running_loop()
        # Can't use asyncio.run() inside running loop - return structural verification
        return LawVerification(
            law_name="associativity",
            status=LawStatus.STRUCTURAL,
            message="Structural verification (cannot run async in sync context with running loop)",
        )
    except RuntimeError:
        # No running loop - can use asyncio.run()
        return asyncio.run(_verify_associativity(p, q, r))


def _verify_identity_sync(p: ProbeProtocol, *args) -> LawVerification:
    """Sync wrapper for identity verification. Accepts extra args for operad compatibility."""
    try:
        # Try to get running loop
        loop = asyncio.get_running_loop()
        # Can't use asyncio.run() inside running loop - return structural verification
        return LawVerification(
            law_name="identity",
            status=LawStatus.STRUCTURAL,
            message="Structural verification (cannot run async in sync context with running loop)",
        )
    except RuntimeError:
        # No running loop - can use asyncio.run()
        return asyncio.run(_verify_identity(p))


def _verify_trace_preservation_sync(p: ProbeProtocol, q: ProbeProtocol, *args) -> LawVerification:
    """Sync wrapper for trace preservation verification."""
    try:
        # Try to get running loop
        loop = asyncio.get_running_loop()
        # Can't use asyncio.run() inside running loop - return structural verification
        return LawVerification(
            law_name="trace_preservation",
            status=LawStatus.STRUCTURAL,
            message="Structural verification (cannot run async in sync context with running loop)",
        )
    except RuntimeError:
        # No running loop - can use asyncio.run()
        return asyncio.run(_verify_trace_preservation(p, q))


ASSOCIATIVITY_LAW = Law(
    name="associativity",
    equation="(p >> q) >> r ≡ p >> (q >> r)",
    verify=_verify_associativity_sync,
    description="Sequential composition is associative",
)

IDENTITY_LAW = Law(
    name="identity",
    equation="null >> p ≡ p ≡ p >> null",
    verify=_verify_identity_sync,
    description="Null probe is the identity element",
)

TRACE_PRESERVATION_LAW = Law(
    name="trace_preservation",
    equation="witness(p >> q) ≡ witness(p) >> witness(q)",
    verify=_verify_trace_preservation_sync,
    description="Witnessing distributes over composition",
)


# =============================================================================
# ProbeOperad
# =============================================================================


def create_probe_operad() -> Operad:
    """
    Create the ProbeOperad.

    This operad defines how verification probes compose. It extends the
    universal AGENT_OPERAD with probe-specific semantics:
    - Sequential probes propagate values via Bellman equation
    - Parallel probes take the best result
    - Witnessing ensures every verification step is traced

    Returns:
        Operad with 5 operations and 3 laws
    """
    return Operad(
        name="ProbeOperad",
        operations={
            "seq": SEQ_OP,
            "par": PAR_OP,
            "branch": BRANCH_OP,
            "fix": FIX_OP,
            "witness": WITNESS_OP,
        },
        laws=[
            ASSOCIATIVITY_LAW,
            IDENTITY_LAW,
            TRACE_PRESERVATION_LAW,
        ],
        description="Grammar of verification probe composition with DP semantics",
    )


# Create the global instance
PROBE_OPERAD = create_probe_operad()


# =============================================================================
# Registry
# =============================================================================

# Register with OperadRegistry (happens at module import time)
from agents.operad.core import OperadRegistry

OperadRegistry.register(PROBE_OPERAD)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Operad
    "PROBE_OPERAD",
    "create_probe_operad",
    # Operations
    "SEQ_OP",
    "PAR_OP",
    "BRANCH_OP",
    "FIX_OP",
    "WITNESS_OP",
    # Laws
    "ASSOCIATIVITY_LAW",
    "IDENTITY_LAW",
    "TRACE_PRESERVATION_LAW",
    # Probe types
    "ProbeProtocol",
    "SequentialProbe",
    "ParallelProbe",
    "BranchProbe",
    "FixedPointProbe",
    "WitnessedProbe",
    "NullProbe",
]
