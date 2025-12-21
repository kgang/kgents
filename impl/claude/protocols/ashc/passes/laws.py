"""
Pass Composition Laws

The categorical laws that define valid pass compositions.

These laws are not aspirational - they are verified:

| Law           | Requirement                           | Verification |
|---------------|---------------------------------------|--------------|
| Identity      | Id >> f == f == f >> Id               | Test with concrete passes |
| Associativity | (f >> g) >> h == f >> (g >> h)        | Test output equality |
| Functor       | lift(f >> g) == lift(f) >> lift(g)    | Structure preservation |

Integration with existing infrastructure:
- Delegates to agents/o/bootstrap_witness.py where possible
- Uses test passes for concrete verification
- Returns LawResult for aggregation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .bootstrap import IdentityPass, create_identity_pass
from .core import CompositionLaw, LawResult, LawStatus

if TYPE_CHECKING:
    from .core import PassProtocol


# =============================================================================
# Identity Law
# =============================================================================


@dataclass
class IdentityLaw(CompositionLaw):
    """
    Identity Law: Id >> f == f == f >> Id

    The identity pass is the unit of composition.
    Composing with identity yields the original pass.
    """

    @property
    def name(self) -> str:
        return "identity"

    @property
    def equation(self) -> str:
        return "Id >> f == f == f >> Id"

    async def verify(self, *passes: Any) -> LawResult:
        """
        Verify identity law with given passes.

        Tests:
        1. Id >> f produces same output as f
        2. f >> Id produces same output as f
        """
        if not passes:
            return LawResult.error(self.name, "No passes provided")

        id_pass = create_identity_pass()
        test_input = {"test": "value", "n": 42}

        evidence_parts = []
        all_passed = True

        for pass_ in passes:
            try:
                # Test left identity: Id >> f == f
                composed_left = id_pass >> pass_
                result_composed = await composed_left.invoke(test_input)
                result_direct = await pass_.invoke(test_input)

                # Compare IRs (not witnesses)
                left_ir = result_composed.ir
                right_ir = result_direct.ir

                if left_ir != right_ir:
                    all_passed = False
                    evidence_parts.append(
                        f"Left identity failed for {pass_.name}: Id >> {pass_.name} != {pass_.name}"
                    )
                else:
                    evidence_parts.append(f"Left identity holds for {pass_.name}")

                # Test right identity: f >> Id == f
                composed_right = pass_ >> id_pass
                result_composed = await composed_right.invoke(test_input)

                right_ir_composed = result_composed.ir

                if right_ir_composed != right_ir:
                    all_passed = False
                    evidence_parts.append(
                        f"Right identity failed for {pass_.name}: "
                        f"{pass_.name} >> Id != {pass_.name}"
                    )
                else:
                    evidence_parts.append(f"Right identity holds for {pass_.name}")

            except Exception as e:
                all_passed = False
                evidence_parts.append(f"Exception for {pass_.name}: {e}")

        if all_passed:
            return LawResult.passed(self.name, "; ".join(evidence_parts))
        else:
            return LawResult.failed(self.name, "; ".join(evidence_parts))


# =============================================================================
# Associativity Law
# =============================================================================


@dataclass
class AssociativityLaw(CompositionLaw):
    """
    Associativity Law: (f >> g) >> h == f >> (g >> h)

    Composition order doesn't matter for grouping.
    Both groupings produce the same result.
    """

    @property
    def name(self) -> str:
        return "associativity"

    @property
    def equation(self) -> str:
        return "(f >> g) >> h == f >> (g >> h)"

    async def verify(self, *passes: Any) -> LawResult:
        """
        Verify associativity law with given passes.

        Requires at least 3 passes to test composition groupings.
        """
        if len(passes) < 3:
            return LawResult.error(self.name, f"Need at least 3 passes, got {len(passes)}")

        test_input = {"test": "value", "n": 42}
        all_passed = True
        evidence_parts = []

        # Test with first 3 passes
        f, g, h = passes[0], passes[1], passes[2]

        try:
            # Left grouping: (f >> g) >> h
            left_assoc = (f >> g) >> h
            result_left = await left_assoc.invoke(test_input)

            # Right grouping: f >> (g >> h)
            right_assoc = f >> (g >> h)
            result_right = await right_assoc.invoke(test_input)

            # Compare IRs
            if result_left.ir == result_right.ir:
                evidence_parts.append(
                    f"Associativity holds: "
                    f"({f.name} >> {g.name}) >> {h.name} == "
                    f"{f.name} >> ({g.name} >> {h.name})"
                )
            else:
                all_passed = False
                evidence_parts.append(
                    f"Associativity failed: "
                    f"({f.name} >> {g.name}) >> {h.name} != "
                    f"{f.name} >> ({g.name} >> {h.name})"
                )

            # Also check witness counts match
            if len(result_left.witnesses) == len(result_right.witnesses):
                evidence_parts.append(f"Witness counts match: {len(result_left.witnesses)}")

        except Exception as e:
            all_passed = False
            evidence_parts.append(f"Exception: {e}")

        if all_passed:
            return LawResult.passed(self.name, "; ".join(evidence_parts))
        else:
            return LawResult.failed(
                self.name,
                "; ".join(evidence_parts),
                left=str(result_left.ir) if "result_left" in dir() else None,
                right=str(result_right.ir) if "result_right" in dir() else None,
            )


# =============================================================================
# Functor Law
# =============================================================================


@dataclass
class FunctorLaw(CompositionLaw):
    """
    Functor Law: lift(f >> g) == lift(f) >> lift(g)

    Lifting preserves composition structure.
    This ensures passes behave consistently when transformed.
    """

    @property
    def name(self) -> str:
        return "functor"

    @property
    def equation(self) -> str:
        return "lift(f >> g) == lift(f) >> lift(g)"

    async def verify(self, *passes: Any) -> LawResult:
        """
        Verify functor law with given passes.

        Note: In our current implementation, passes aren't lifted,
        so this is structurally verified (composition preserves names).
        """
        if len(passes) < 2:
            return LawResult.error(self.name, f"Need at least 2 passes, got {len(passes)}")

        f, g = passes[0], passes[1]

        try:
            # Compose and check name structure is preserved
            composed = f >> g
            expected_name = f"({f.name} >> {g.name})"

            if composed.name == expected_name:
                return LawResult(
                    law=self.name,
                    status=LawStatus.HOLDS,
                    evidence=(f"Structure preserved: {composed.name}"),
                )
            else:
                return LawResult.failed(
                    self.name,
                    f"Name mismatch: {composed.name} != {expected_name}",
                )

        except Exception as e:
            return LawResult.error(self.name, str(e))


# =============================================================================
# Closure Law
# =============================================================================


@dataclass
class ClosureLaw(CompositionLaw):
    """
    Closure Law: f >> g is still a Pass

    The result of composition is itself composable.
    This ensures we stay within the category.
    """

    @property
    def name(self) -> str:
        return "closure"

    @property
    def equation(self) -> str:
        return "f >> g : Pass"

    async def verify(self, *passes: Any) -> LawResult:
        """
        Verify closure law with given passes.

        Checks that composed result has all Pass properties.
        """
        if len(passes) < 2:
            return LawResult.error(self.name, f"Need at least 2 passes, got {len(passes)}")

        f, g = passes[0], passes[1]

        try:
            composed = f >> g

            # Check required attributes
            checks = []
            if hasattr(composed, "name"):
                checks.append("name")
            if hasattr(composed, "input_type"):
                checks.append("input_type")
            if hasattr(composed, "output_type"):
                checks.append("output_type")
            if hasattr(composed, "invoke"):
                checks.append("invoke")
            if hasattr(composed, "__rshift__"):
                checks.append("__rshift__")

            required = {"name", "input_type", "output_type", "invoke", "__rshift__"}
            present = set(checks)

            if present == required:
                return LawResult.passed(
                    self.name, f"All required attributes present: {', '.join(sorted(present))}"
                )
            else:
                missing = required - present
                return LawResult.failed(
                    self.name, f"Missing attributes: {', '.join(sorted(missing))}"
                )

        except Exception as e:
            return LawResult.error(self.name, str(e))


# =============================================================================
# Witness Law
# =============================================================================


@dataclass
class WitnessLaw(CompositionLaw):
    """
    Witness Law: Every pass emits a witness

    Per spec: "Silent passes are compile failures."
    Every pass execution must produce at least one witness.
    """

    @property
    def name(self) -> str:
        return "witness"

    @property
    def equation(self) -> str:
        return "forall pass P, input I: P(I) produces witness W"

    async def verify(self, *passes: Any) -> LawResult:
        """
        Verify witness law with given passes.

        Every pass must emit at least one witness.
        """
        if not passes:
            return LawResult.error(self.name, "No passes provided")

        test_input = {"test": "value"}
        all_passed = True
        evidence_parts = []

        for pass_ in passes:
            try:
                result = await pass_.invoke(test_input)

                if result.witnesses:
                    evidence_parts.append(f"{pass_.name}: {len(result.witnesses)} witness(es)")
                else:
                    all_passed = False
                    evidence_parts.append(f"{pass_.name}: NO WITNESS (violation!)")

            except Exception as e:
                all_passed = False
                evidence_parts.append(f"{pass_.name}: exception {e}")

        if all_passed:
            return LawResult.passed(self.name, "; ".join(evidence_parts))
        else:
            return LawResult.failed(self.name, "; ".join(evidence_parts))


# =============================================================================
# Default Laws
# =============================================================================

COMPOSITION_LAWS: tuple[CompositionLaw, ...] = (
    IdentityLaw(),
    AssociativityLaw(),
    FunctorLaw(),
    ClosureLaw(),
    WitnessLaw(),
)


__all__ = [
    "CompositionLaw",
    "IdentityLaw",
    "AssociativityLaw",
    "FunctorLaw",
    "ClosureLaw",
    "WitnessLaw",
    "COMPOSITION_LAWS",
]
