"""
self.grow GROWTH_OPERAD

The compositional grammar for growth operations.

Migrated to canonical operad pattern (Phase 1 Operad Unification).
Extends AGENT_OPERAD from agents.operad.core.

Operations:
- recognize: () → GapRecognition
- propose: GapRecognition → HolonProposal
- validate: HolonProposal → ValidationResult
- germinate: (HolonProposal, ValidationResult) → GerminatingHolon
- promote: GerminatingHolon → PromotionResult
- rollback: RollbackToken → RollbackResult
- prune: GerminatingHolon → CompostEntry

Laws:
1. BUDGET_INVARIANT: Each operation costs entropy; total must not exceed budget
2. VALIDATION_GATE: germinate requires validate.passed = True
3. APPROVAL_GATE: promote requires staged + (approve OR gardener)
4. ROLLBACK_WINDOW: rollback only valid within expiry window
5. COMPOSABILITY: recognize >> propose >> validate forms a pipeline
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent, from_function

from .schemas import (
    GapRecognition,
    GerminatingHolon,
    GrowthBudget,
    HolonProposal,
    PromotionResult,
    RollbackResult,
    RollbackToken,
    ValidationResult,
)

# Type variables for operad operations
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


# ============================================================================
# Operation Metadata (entropy costs, type info)
# ============================================================================


@dataclass(frozen=True)
class GrowthOperationMeta:
    """
    Metadata for growth operations.

    Tracks entropy cost and type signatures for budget management.
    """

    input_types: tuple[str, ...]
    output_type: str
    entropy_cost: float


# Operation metadata registry
GROWTH_OPERATION_META: dict[str, GrowthOperationMeta] = {
    "recognize": GrowthOperationMeta(
        input_types=(),
        output_type="GapRecognition",
        entropy_cost=0.25,
    ),
    "propose": GrowthOperationMeta(
        input_types=("GapRecognition",),
        output_type="HolonProposal",
        entropy_cost=0.15,
    ),
    "validate": GrowthOperationMeta(
        input_types=("HolonProposal",),
        output_type="ValidationResult",
        entropy_cost=0.10,
    ),
    "germinate": GrowthOperationMeta(
        input_types=("HolonProposal", "ValidationResult"),
        output_type="GerminatingHolon",
        entropy_cost=0.10,
    ),
    "promote": GrowthOperationMeta(
        input_types=("GerminatingHolon",),
        output_type="PromotionResult",
        entropy_cost=0.05,
    ),
    "rollback": GrowthOperationMeta(
        input_types=("RollbackToken",),
        output_type="RollbackResult",
        entropy_cost=0.02,
    ),
    "growth_prune": GrowthOperationMeta(
        input_types=("GerminatingHolon",),
        output_type="CompostEntry",
        entropy_cost=0.02,
    ),
}


def get_entropy_cost(*operation_names: str) -> float:
    """Calculate total entropy cost for a sequence of operations."""
    total = 0.0
    for name in operation_names:
        meta = GROWTH_OPERATION_META.get(name)
        if meta:
            total += meta.entropy_cost
    return total


# ============================================================================
# Growth-Specific Compose Functions
# ============================================================================


def _recognize_compose() -> PolyAgent[Any, Any, Any]:
    """Recognize gaps in the system."""

    def recognize_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "recognize",
            "input": input,
            "output_type": "GapRecognition",
            "entropy_cost": GROWTH_OPERATION_META["recognize"].entropy_cost,
        }

    return from_function("recognize()", recognize_fn)


def _propose_compose(
    gap: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Propose a holon from a gap recognition."""

    def propose_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "propose",
            "input": input,
            "output_type": "HolonProposal",
            "entropy_cost": GROWTH_OPERATION_META["propose"].entropy_cost,
        }

    return from_function("propose()", propose_fn)


def _validate_compose(
    proposal: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Validate a holon proposal."""

    def validate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "validate",
            "input": input,
            "output_type": "ValidationResult",
            "entropy_cost": GROWTH_OPERATION_META["validate"].entropy_cost,
        }

    return from_function("validate()", validate_fn)


def _germinate_compose(
    proposal: PolyAgent[Any, Any, Any],
    validation: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Germinate a validated proposal into a holon."""

    def germinate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "germinate",
            "proposal": proposal.name,
            "validation": validation.name,
            "input": input,
            "output_type": "GerminatingHolon",
            "entropy_cost": GROWTH_OPERATION_META["germinate"].entropy_cost,
        }

    return from_function(f"germinate({proposal.name},{validation.name})", germinate_fn)


def _promote_compose(
    holon: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Promote a germinating holon to permanent status."""

    def promote_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "promote",
            "input": input,
            "output_type": "PromotionResult",
            "entropy_cost": GROWTH_OPERATION_META["promote"].entropy_cost,
        }

    return from_function("promote()", promote_fn)


def _rollback_compose(
    token: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Rollback using a rollback token."""

    def rollback_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "rollback",
            "input": input,
            "output_type": "RollbackResult",
            "entropy_cost": GROWTH_OPERATION_META["rollback"].entropy_cost,
        }

    return from_function("rollback()", rollback_fn)


def _prune_compose(
    holon: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Prune a germinating holon to compost."""

    def prune_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "prune",
            "input": input,
            "output_type": "CompostEntry",
            "entropy_cost": GROWTH_OPERATION_META["growth_prune"].entropy_cost,
        }

    return from_function("growth_prune()", prune_fn)


# ============================================================================
# Law Verification Helpers
# ============================================================================


def _verify_budget_invariant(
    budget: GrowthBudget | Any = None,
    operations: list[str] | Any = None,
    *args: Any,
) -> LawVerification:
    """
    Law 1: BUDGET_INVARIANT

    Each operation costs entropy; total must not exceed budget.
    """
    # Type check: budget must be GrowthBudget, operations must be list of strings
    if not isinstance(budget, GrowthBudget):
        return LawVerification(
            law_name="budget_invariant",
            status=LawStatus.SKIPPED,
            message="Budget must be GrowthBudget type",
        )
    if not isinstance(operations, list):
        return LawVerification(
            law_name="budget_invariant",
            status=LawStatus.SKIPPED,
            message="Operations must be list of strings",
        )

    total_cost = get_entropy_cost(*operations)
    if budget.remaining >= total_cost:
        return LawVerification(
            law_name="budget_invariant",
            status=LawStatus.PASSED,
            left_result=budget.remaining,
            right_result=total_cost,
            message=f"Budget sufficient: {budget.remaining} >= {total_cost}",
        )
    else:
        return LawVerification(
            law_name="budget_invariant",
            status=LawStatus.FAILED,
            left_result=budget.remaining,
            right_result=total_cost,
            message=f"Budget exhausted: {budget.remaining} < {total_cost}",
        )


def _verify_validation_gate(
    validation: ValidationResult | Any = None,
    *args: Any,
) -> LawVerification:
    """
    Law 2: VALIDATION_GATE

    germinate requires validate.passed = True.
    """
    if not isinstance(validation, ValidationResult):
        return LawVerification(
            law_name="validation_gate",
            status=LawStatus.SKIPPED,
            message="ValidationResult type required",
        )

    if validation.passed:
        return LawVerification(
            law_name="validation_gate",
            status=LawStatus.PASSED,
            message="Validation passed",
        )
    else:
        return LawVerification(
            law_name="validation_gate",
            status=LawStatus.FAILED,
            message=f"Validation failed with blockers: {validation.blockers}",
        )


def _verify_approval_gate(
    holon: GerminatingHolon | Any = None,
    approver_archetype: str | Any = "",
    *args: Any,
) -> LawVerification:
    """
    Law 3: APPROVAL_GATE

    promote requires staged + (approve OR gardener).
    """
    if not isinstance(holon, GerminatingHolon):
        return LawVerification(
            law_name="approval_gate",
            status=LawStatus.SKIPPED,
            message="GerminatingHolon type required",
        )

    if holon.promoted_at is not None:
        return LawVerification(
            law_name="approval_gate",
            status=LawStatus.PASSED,
            message="Already approved",
        )

    if approver_archetype in ("admin", "gardener"):
        return LawVerification(
            law_name="approval_gate",
            status=LawStatus.PASSED,
            message=f"Archetype '{approver_archetype}' can approve/skip",
        )

    return LawVerification(
        law_name="approval_gate",
        status=LawStatus.FAILED,
        message=f"Archetype '{approver_archetype}' cannot approve",
    )


def _verify_rollback_window(
    token: RollbackToken | Any = None,
    *args: Any,
) -> LawVerification:
    """
    Law 4: ROLLBACK_WINDOW

    rollback only valid within expiry window.
    """
    if not isinstance(token, RollbackToken):
        return LawVerification(
            law_name="rollback_window",
            status=LawStatus.SKIPPED,
            message="RollbackToken type required",
        )

    if token.is_expired:
        return LawVerification(
            law_name="rollback_window",
            status=LawStatus.FAILED,
            message=f"Rollback window expired at {token.expires_at.isoformat()}",
        )
    else:
        return LawVerification(
            law_name="rollback_window",
            status=LawStatus.PASSED,
            message=f"Rollback valid until {token.expires_at.isoformat()}",
        )


def _verify_composability(*args: Any) -> LawVerification:
    """
    Law 5: COMPOSABILITY

    Operations must type-check to compose.
    recognize >> propose >> validate forms a valid pipeline.
    """
    # Check the standard pipeline types
    r_meta = GROWTH_OPERATION_META["recognize"]
    p_meta = GROWTH_OPERATION_META["propose"]
    v_meta = GROWTH_OPERATION_META["validate"]

    # recognize outputs GapRecognition, propose inputs GapRecognition
    if r_meta.output_type != p_meta.input_types[0]:
        return LawVerification(
            law_name="composability",
            status=LawStatus.FAILED,
            message=f"Type mismatch: recognize outputs {r_meta.output_type}, propose expects {p_meta.input_types[0]}",
        )

    # propose outputs HolonProposal, validate inputs HolonProposal
    if p_meta.output_type != v_meta.input_types[0]:
        return LawVerification(
            law_name="composability",
            status=LawStatus.FAILED,
            message=f"Type mismatch: propose outputs {p_meta.output_type}, validate expects {v_meta.input_types[0]}",
        )

    return LawVerification(
        law_name="composability",
        status=LawStatus.PASSED,
        message="Pipeline recognize >> propose >> validate is type-valid",
    )


# ============================================================================
# GROWTH_OPERAD Definition (extends AGENT_OPERAD)
# ============================================================================


def create_growth_operad() -> Operad:
    """
    Create the Growth Operad.

    Extends AGENT_OPERAD with growth-specific operations:
    - recognize: Identify gaps in the system
    - propose: Generate holon proposals
    - validate: Check proposal validity
    - germinate: Create germinating holon
    - promote: Elevate to permanent status
    - rollback: Undo recent changes
    - growth_prune: Send to compost
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # === Growth Operations ===
    ops["recognize"] = Operation(
        name="recognize",
        arity=0,
        signature="() → GapRecognition",
        compose=_recognize_compose,
        description="Identify gaps in the system (entropy: 0.25)",
    )
    ops["propose"] = Operation(
        name="propose",
        arity=1,
        signature="GapRecognition → HolonProposal",
        compose=_propose_compose,
        description="Generate holon proposal from gap (entropy: 0.15)",
    )
    ops["growth_validate"] = Operation(
        name="growth_validate",
        arity=1,
        signature="HolonProposal → ValidationResult",
        compose=_validate_compose,
        description="Check proposal validity (entropy: 0.10)",
    )
    ops["germinate"] = Operation(
        name="germinate",
        arity=2,
        signature="(HolonProposal, ValidationResult) → GerminatingHolon",
        compose=_germinate_compose,
        description="Create germinating holon (entropy: 0.10)",
    )
    ops["promote"] = Operation(
        name="promote",
        arity=1,
        signature="GerminatingHolon → PromotionResult",
        compose=_promote_compose,
        description="Elevate to permanent status (entropy: 0.05)",
    )
    ops["rollback"] = Operation(
        name="rollback",
        arity=1,
        signature="RollbackToken → RollbackResult",
        compose=_rollback_compose,
        description="Undo recent changes (entropy: 0.02)",
    )
    ops["growth_prune"] = Operation(
        name="growth_prune",
        arity=1,
        signature="GerminatingHolon → CompostEntry",
        compose=_prune_compose,
        description="Send to compost (entropy: 0.02)",
    )

    # Inherit universal laws and add growth-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="budget_invariant",
            equation="sum(entropy_cost(ops)) <= budget.remaining",
            verify=_verify_budget_invariant,
            description="Each operation costs entropy; total must not exceed budget",
        ),
        Law(
            name="validation_gate",
            equation="germinate(p, v) implies v.passed = True",
            verify=_verify_validation_gate,
            description="germinate requires validate.passed = True",
        ),
        Law(
            name="approval_gate",
            equation="promote(h) implies staged(h) AND (approved(h) OR gardener)",
            verify=_verify_approval_gate,
            description="promote requires staged + (approve OR gardener)",
        ),
        Law(
            name="rollback_window",
            equation="rollback(t) implies not expired(t)",
            verify=_verify_rollback_window,
            description="rollback only valid within expiry window",
        ),
        Law(
            name="composability",
            equation="recognize >> propose >> validate type-checks",
            verify=_verify_composability,
            description="Operations must type-check to compose",
        ),
    ]

    return Operad(
        name="GrowthOperad",
        operations=ops,
        laws=laws,
        description="Composition grammar for self.grow autopoiesis operations",
    )


# ============================================================================
# Global Instance
# ============================================================================


GROWTH_OPERAD = create_growth_operad()
"""
The Growth Operad.

Operations:
- Universal: seq, par, branch, fix, trace (from AGENT_OPERAD)
- Growth: recognize, propose, growth_validate, germinate, promote, rollback, growth_prune

Laws:
- Universal: seq_associativity, par_associativity
- Growth: budget_invariant, validation_gate, approval_gate, rollback_window, composability
"""

# Register with the operad registry
OperadRegistry.register(GROWTH_OPERAD)


# ============================================================================
# Composed Pipelines (convenience)
# ============================================================================


@dataclass(frozen=True)
class ComposedPipeline:
    """A named composition of operations with total entropy cost."""

    name: str
    operations: tuple[str, ...]

    @property
    def total_entropy_cost(self) -> float:
        return get_entropy_cost(*self.operations)

    def input_type(self) -> str:
        """First operation's input type."""
        if not self.operations:
            return "()"
        meta = GROWTH_OPERATION_META.get(self.operations[0])
        return meta.input_types[0] if meta and meta.input_types else "()"

    def output_type(self) -> str:
        """Last operation's output type."""
        if not self.operations:
            return "()"
        meta = GROWTH_OPERATION_META.get(self.operations[-1])
        return meta.output_type if meta else "()"


# Standard pipelines
DISCOVERY_PIPELINE = ComposedPipeline("discovery", ("recognize", "propose"))
FULL_PIPELINE = ComposedPipeline("full_pipeline", ("recognize", "propose", "validate"))
LIFECYCLE_PIPELINE = ComposedPipeline("lifecycle", ("germinate", "promote"))


# ============================================================================
# Budget Helpers
# ============================================================================


def can_afford(budget: GrowthBudget, *operation_names: str) -> bool:
    """Check if budget can afford a sequence of operations."""
    total = get_entropy_cost(*operation_names)
    return budget.remaining >= total


def compose_typed(*operation_names: str) -> ComposedPipeline | None:
    """
    Compose operations with type checking.

    Returns None if composition is invalid.
    """
    # Type check
    for i in range(len(operation_names) - 1):
        current = GROWTH_OPERATION_META.get(operation_names[i])
        next_op = GROWTH_OPERATION_META.get(operation_names[i + 1])

        if not current or not next_op:
            return None

        if not next_op.input_types:
            continue

        if current.output_type != next_op.input_types[0]:
            return None

    return ComposedPipeline(
        name=" >> ".join(operation_names),
        operations=tuple(operation_names),
    )


# ============================================================================
# Legacy Compatibility
# ============================================================================


# Legacy type aliases
OperadOperation = Operation
GrowthOperad = Operad


# Legacy law check functions (return tuple instead of LawVerification)
def check_budget_invariant(
    budget: GrowthBudget,
    operations: list[str],
    operad: Operad | None = None,
) -> tuple[bool, str]:
    """Legacy: Check BUDGET_INVARIANT law."""
    result = _verify_budget_invariant(budget, operations)
    return (result.passed, result.message)


def check_validation_gate(validation: ValidationResult) -> tuple[bool, str]:
    """Legacy: Check VALIDATION_GATE law."""
    result = _verify_validation_gate(validation)
    return (result.passed, result.message)


def check_approval_gate(
    holon: GerminatingHolon | None,
    approver_archetype: str,
) -> tuple[bool, str]:
    """Legacy: Check APPROVAL_GATE law."""
    result = _verify_approval_gate(holon, approver_archetype)
    return (result.passed, result.message)


def check_rollback_window(token: RollbackToken) -> tuple[bool, str]:
    """Legacy: Check ROLLBACK_WINDOW law."""
    result = _verify_rollback_window(token)
    return (result.passed, result.message)


def check_composability(
    operad: Operad | None = None,
    *operations: str,
) -> tuple[bool, str]:
    """Legacy: Check COMPOSABILITY law."""
    result = _verify_composability()
    return (result.passed, result.message)


def run_all_law_tests() -> dict[str, bool]:
    """Run all operad law tests (legacy)."""
    from .schemas import GrowthBudget, ValidationResult

    results = {}

    # Test budget invariant
    budget = GrowthBudget()
    budget.remaining = 0.5
    ok, _ = check_budget_invariant(budget, ["recognize", "propose"])
    results["BUDGET_INVARIANT"] = ok

    # Test validation gate
    passing = ValidationResult(passed=True)
    ok, _ = check_validation_gate(passing)
    results["VALIDATION_GATE"] = ok

    # Test composability
    ok, _ = check_composability(None, "recognize", "propose", "validate")
    results["COMPOSABILITY"] = ok

    return results


__all__ = [
    # Core types (re-exported)
    "Operation",
    "Law",
    "Operad",
    # Metadata
    "GrowthOperationMeta",
    "GROWTH_OPERATION_META",
    "get_entropy_cost",
    # Operad
    "GROWTH_OPERAD",
    "create_growth_operad",
    # Pipelines
    "ComposedPipeline",
    "DISCOVERY_PIPELINE",
    "FULL_PIPELINE",
    "LIFECYCLE_PIPELINE",
    # Helpers
    "can_afford",
    "compose_typed",
    # Legacy compatibility
    "OperadOperation",
    "GrowthOperad",
    "check_budget_invariant",
    "check_validation_gate",
    "check_approval_gate",
    "check_rollback_window",
    "check_composability",
    "run_all_law_tests",
]
