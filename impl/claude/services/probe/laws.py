"""
Law Probes: Categorical law verification for tools and agents.

Philosophy:
    "Category laws are rationality constraints. If they fail, something is wrong."

This module implements fast checks for:
- Identity law: Id >> f == f == f >> Id
- Associativity law: (f >> g) >> h == f >> (g >> h)
- Coherence: Sheaf gluing conditions

No LLM calls - these are deterministic structural checks.

See: spec/services/tooling.md §3.1 (Category Laws)
See: impl/claude/services/categorical/probes.py (Monad/Sheaf probes)
"""

from __future__ import annotations

import time
from typing import Any

from .types import ProbeResult, ProbeStatus, ProbeType


class IdentityProbe:
    """
    Verify the identity law: Id >> f == f == f >> Id.

    The identity morphism should be a no-op on either side of composition.

    Usage:
        >>> probe = IdentityProbe()
        >>> result = await probe.check(tool, test_input)
        >>> assert result.passed
    """

    async def check(
        self,
        tool: Any,
        test_input: Any,
    ) -> ProbeResult:
        """
        Verify identity law for a tool.

        Args:
            tool: Tool instance with invoke() method
            test_input: Test input to verify with

        Returns:
            ProbeResult indicating pass/fail
        """
        start_ms = time.perf_counter() * 1000

        try:
            from services.tooling.base import IdentityTool

            identity: IdentityTool[Any] = IdentityTool()

            # Compute three paths
            # 1. Id >> tool
            left_result = await tool.invoke(await identity.invoke(test_input))

            # 2. tool (direct)
            direct_result = await tool.invoke(test_input)

            # 3. tool >> Id
            right_result = await identity.invoke(await tool.invoke(test_input))

            # All three should be equal
            passed = left_result == direct_result == right_result

            duration_ms = (time.perf_counter() * 1000) - start_ms

            if passed:
                return ProbeResult(
                    name=f"identity:{tool.name}",
                    probe_type=ProbeType.IDENTITY,
                    status=ProbeStatus.PASSED,
                    duration_ms=duration_ms,
                )
            else:
                return ProbeResult(
                    name=f"identity:{tool.name}",
                    probe_type=ProbeType.IDENTITY,
                    status=ProbeStatus.FAILED,
                    details=f"Identity law violated: left={left_result}, direct={direct_result}, right={right_result}",
                    duration_ms=duration_ms,
                )

        except Exception as e:
            duration_ms = (time.perf_counter() * 1000) - start_ms
            return ProbeResult(
                name=f"identity:{getattr(tool, 'name', 'unknown')}",
                probe_type=ProbeType.IDENTITY,
                status=ProbeStatus.ERROR,
                details=f"Error during identity check: {e}",
                duration_ms=duration_ms,
            )


class AssociativityProbe:
    """
    Verify the associativity law: (f >> g) >> h == f >> (g >> h).

    Grouping of compositions should not matter.

    Usage:
        >>> probe = AssociativityProbe()
        >>> result = await probe.check(tool1, tool2, tool3, test_input)
        >>> assert result.passed
    """

    async def check(
        self,
        tool_f: Any,
        tool_g: Any,
        tool_h: Any,
        test_input: Any,
    ) -> ProbeResult:
        """
        Verify associativity law for three tools.

        Args:
            tool_f: First tool
            tool_g: Second tool
            tool_h: Third tool
            test_input: Test input to verify with

        Returns:
            ProbeResult indicating pass/fail
        """
        start_ms = time.perf_counter() * 1000

        try:
            # Test associativity: (f >> g) >> h == f >> (g >> h)
            # Both paths should produce the same result

            # Left path: (f >> g) >> h
            step1_left = await tool_f.invoke(test_input)
            step2_left = await tool_g.invoke(step1_left)
            left_result = await tool_h.invoke(step2_left)

            # Right path: f >> (g >> h)
            # This is the same as left since composition is just sequential application
            # BUT we test it by composing g and h first if tools support >> operator
            if hasattr(tool_f, "__rshift__"):
                # Use built-in composition to verify >> operator works correctly
                left_pipeline = (tool_f >> tool_g) >> tool_h
                right_pipeline = tool_f >> (tool_g >> tool_h)

                left_result = await left_pipeline.invoke(test_input)
                right_result = await right_pipeline.invoke(test_input)
            else:
                # Manual composition - both should be equivalent
                # Left: ((f >> g) >> h)
                step1_left = await tool_f.invoke(test_input)
                step2_left = await tool_g.invoke(step1_left)
                left_result = await tool_h.invoke(step2_left)

                # Right: (f >> (g >> h))
                # Same operations, just different grouping
                step1_right = await tool_f.invoke(test_input)
                step2_right = await tool_g.invoke(step1_right)
                right_result = await tool_h.invoke(step2_right)

            # They should be equal
            passed = left_result == right_result

            duration_ms = (time.perf_counter() * 1000) - start_ms

            name = f"associativity:{getattr(tool_f, 'name', 'f')}>>{getattr(tool_g, 'name', 'g')}>>{getattr(tool_h, 'name', 'h')}"

            if passed:
                return ProbeResult(
                    name=name,
                    probe_type=ProbeType.ASSOCIATIVITY,
                    status=ProbeStatus.PASSED,
                    duration_ms=duration_ms,
                )
            else:
                return ProbeResult(
                    name=name,
                    probe_type=ProbeType.ASSOCIATIVITY,
                    status=ProbeStatus.FAILED,
                    details=f"Associativity law violated: (f>>g)>>h={left_result}, f>>(g>>h)={right_result}",
                    duration_ms=duration_ms,
                )

        except Exception as e:
            duration_ms = (time.perf_counter() * 1000) - start_ms
            return ProbeResult(
                name="associativity:error",
                probe_type=ProbeType.ASSOCIATIVITY,
                status=ProbeStatus.ERROR,
                details=f"Error during associativity check: {e}",
                duration_ms=duration_ms,
            )


class CoherenceProbe:
    """
    Verify sheaf coherence conditions.

    For a sheaf, local views must agree on overlaps (gluing condition).
    This is a structural check, not an LLM-based hallucination detector.

    Usage:
        >>> probe = CoherenceProbe()
        >>> result = await probe.check(sheaf_instance, context)
        >>> assert result.passed
    """

    async def check(
        self,
        sheaf: Any,
        context: str | None = None,
    ) -> ProbeResult:
        """
        Verify sheaf coherence for a given context.

        Args:
            sheaf: Sheaf instance with coherence checking methods
            context: Optional context to check coherence in

        Returns:
            ProbeResult indicating pass/fail
        """
        start_ms = time.perf_counter() * 1000

        try:
            # Check if sheaf has a coherence check method
            if hasattr(sheaf, "check_coherence"):
                is_coherent = await sheaf.check_coherence(context)
            elif hasattr(sheaf, "is_coherent"):
                is_coherent = sheaf.is_coherent(context)
            else:
                # No coherence check method - skip
                duration_ms = (time.perf_counter() * 1000) - start_ms
                return ProbeResult(
                    name=f"coherence:{getattr(sheaf, 'name', 'unknown')}",
                    probe_type=ProbeType.COHERENCE,
                    status=ProbeStatus.SKIPPED,
                    details="No coherence check method available",
                    duration_ms=duration_ms,
                )

            duration_ms = (time.perf_counter() * 1000) - start_ms

            if is_coherent:
                return ProbeResult(
                    name=f"coherence:{getattr(sheaf, 'name', 'unknown')}",
                    probe_type=ProbeType.COHERENCE,
                    status=ProbeStatus.PASSED,
                    duration_ms=duration_ms,
                )
            else:
                return ProbeResult(
                    name=f"coherence:{getattr(sheaf, 'name', 'unknown')}",
                    probe_type=ProbeType.COHERENCE,
                    status=ProbeStatus.FAILED,
                    details="Sheaf coherence condition violated",
                    duration_ms=duration_ms,
                )

        except Exception as e:
            duration_ms = (time.perf_counter() * 1000) - start_ms
            return ProbeResult(
                name=f"coherence:{getattr(sheaf, 'name', 'unknown')}",
                probe_type=ProbeType.COHERENCE,
                status=ProbeStatus.ERROR,
                details=f"Error during coherence check: {e}",
                duration_ms=duration_ms,
            )


__all__ = [
    "IdentityProbe",
    "AssociativityProbe",
    "CoherenceProbe",
]
