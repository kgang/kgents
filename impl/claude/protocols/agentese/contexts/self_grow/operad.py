"""
self.grow GROWTH_OPERAD

The compositional grammar for growth operations.

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


# === Operad Operations ===


@dataclass(frozen=True)
class OperadOperation:
    """
    An operation in the growth operad.

    Each operation has:
    - name: Operation identifier
    - arity: Number of inputs
    - input_types: Tuple of input type names
    - output_type: Output type name
    - entropy_cost: Cost in entropy budget
    """

    name: str
    arity: int
    input_types: tuple[str, ...]
    output_type: str
    entropy_cost: float

    def compose(self, *others: "OperadOperation") -> "ComposedOperation":
        """Compose this operation with others."""
        return ComposedOperation(operations=(self, *others))


@dataclass(frozen=True)
class ComposedOperation:
    """A composition of operad operations."""

    operations: tuple[OperadOperation, ...]

    @property
    def name(self) -> str:
        return " >> ".join(op.name for op in self.operations)

    @property
    def total_entropy_cost(self) -> float:
        return sum(op.entropy_cost for op in self.operations)

    def input_type(self) -> str:
        """First operation's input type."""
        return self.operations[0].input_types[0] if self.operations else "()"

    def output_type(self) -> str:
        """Last operation's output type."""
        return self.operations[-1].output_type if self.operations else "()"


# === GROWTH_OPERAD Operations ===


RECOGNIZE = OperadOperation(
    name="recognize",
    arity=0,
    input_types=(),
    output_type="GapRecognition",
    entropy_cost=0.25,
)

PROPOSE = OperadOperation(
    name="propose",
    arity=1,
    input_types=("GapRecognition",),
    output_type="HolonProposal",
    entropy_cost=0.15,
)

VALIDATE = OperadOperation(
    name="validate",
    arity=1,
    input_types=("HolonProposal",),
    output_type="ValidationResult",
    entropy_cost=0.10,
)

GERMINATE = OperadOperation(
    name="germinate",
    arity=2,
    input_types=("HolonProposal", "ValidationResult"),
    output_type="GerminatingHolon",
    entropy_cost=0.10,
)

PROMOTE = OperadOperation(
    name="promote",
    arity=1,
    input_types=("GerminatingHolon",),
    output_type="PromotionResult",
    entropy_cost=0.05,
)

ROLLBACK = OperadOperation(
    name="rollback",
    arity=1,
    input_types=("RollbackToken",),
    output_type="RollbackResult",
    entropy_cost=0.02,
)

PRUNE = OperadOperation(
    name="prune",
    arity=1,
    input_types=("GerminatingHolon",),
    output_type="CompostEntry",
    entropy_cost=0.02,
)


@dataclass
class GrowthOperad:
    """
    The GROWTH_OPERAD: compositional grammar for growth operations.

    Provides:
    - Operation composition with type checking
    - Law verification
    - Budget tracking
    """

    # All operations
    operations: dict[str, OperadOperation] = field(default_factory=dict)

    # Composed pipelines
    pipelines: dict[str, ComposedOperation] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Register standard operations
        self.operations = {
            "recognize": RECOGNIZE,
            "propose": PROPOSE,
            "validate": VALIDATE,
            "germinate": GERMINATE,
            "promote": PROMOTE,
            "rollback": ROLLBACK,
            "prune": PRUNE,
        }

        # Register standard pipelines
        self.pipelines = {
            "discovery": ComposedOperation((RECOGNIZE, PROPOSE)),
            "full_pipeline": ComposedOperation((RECOGNIZE, PROPOSE, VALIDATE)),
            "lifecycle": ComposedOperation((GERMINATE, PROMOTE)),
        }

    def get_operation(self, name: str) -> OperadOperation | None:
        """Get an operation by name."""
        return self.operations.get(name)

    def compose(self, *names: str) -> ComposedOperation:
        """
        Compose operations by name with type checking.

        Raises ValueError if composition is invalid.
        """
        ops = []
        for name in names:
            op = self.operations.get(name)
            if op is None:
                raise ValueError(f"Unknown operation: {name}")
            ops.append(op)

        # Type check composition
        for i in range(len(ops) - 1):
            current_output = ops[i].output_type
            next_input = ops[i + 1].input_types[0] if ops[i + 1].input_types else "()"

            if current_output != next_input:
                raise ValueError(
                    f"Type mismatch in composition: "
                    f"{ops[i].name} outputs {current_output}, "
                    f"but {ops[i + 1].name} expects {next_input}"
                )

        return ComposedOperation(tuple(ops))

    def can_afford(self, budget: GrowthBudget, *names: str) -> bool:
        """Check if budget can afford a composition."""
        try:
            composed = self.compose(*names)
            return budget.remaining >= composed.total_entropy_cost
        except ValueError:
            return False


# === Laws ===


def check_budget_invariant(
    budget: GrowthBudget,
    operations: list[str],
    operad: GrowthOperad,
) -> tuple[bool, str]:
    """
    Law 1: BUDGET_INVARIANT

    Each operation costs entropy; total must not exceed budget.
    """
    try:
        composed = operad.compose(*operations)
        if budget.remaining >= composed.total_entropy_cost:
            return (
                True,
                f"Budget sufficient: {budget.remaining} >= {composed.total_entropy_cost}",
            )
        else:
            return (
                False,
                f"Budget exhausted: {budget.remaining} < {composed.total_entropy_cost}",
            )
    except ValueError as e:
        return False, str(e)


def check_validation_gate(validation: ValidationResult) -> tuple[bool, str]:
    """
    Law 2: VALIDATION_GATE

    germinate requires validate.passed = True.
    """
    if validation.passed:
        return True, "Validation passed"
    else:
        return False, f"Validation failed with blockers: {validation.blockers}"


def check_approval_gate(
    holon: GerminatingHolon | None,
    approver_archetype: str,
) -> tuple[bool, str]:
    """
    Law 3: APPROVAL_GATE

    promote requires staged + (approve OR gardener).
    """
    if holon is None:
        return False, "Holon not staged"

    if holon.promoted_at is not None:
        return True, "Already approved"

    if approver_archetype in ("admin", "gardener"):
        return True, f"Archetype '{approver_archetype}' can approve/skip"

    return False, f"Archetype '{approver_archetype}' cannot approve"


def check_rollback_window(token: RollbackToken) -> tuple[bool, str]:
    """
    Law 4: ROLLBACK_WINDOW

    rollback only valid within expiry window.
    """
    if token.is_expired:
        return False, f"Rollback window expired at {token.expires_at.isoformat()}"
    else:
        return True, f"Rollback valid until {token.expires_at.isoformat()}"


def check_composability(
    operad: GrowthOperad,
    *operations: str,
) -> tuple[bool, str]:
    """
    Law 5: COMPOSABILITY

    Operations must type-check to compose.
    """
    try:
        composed = operad.compose(*operations)
        return True, f"Composition valid: {composed.name}"
    except ValueError as e:
        return False, str(e)


# === Global Operad Instance ===


GROWTH_OPERAD = GrowthOperad()


# === Tests (for operad laws) ===


def test_law_budget_invariant() -> bool:
    """Test Law 1: BUDGET_INVARIANT."""
    budget = GrowthBudget()
    budget.remaining = 0.5  # Limited budget

    # Should succeed with enough budget
    ok, _ = check_budget_invariant(budget, ["recognize", "propose"], GROWTH_OPERAD)
    if not ok:
        return False

    # Should fail with exhausted budget
    budget.remaining = 0.1
    ok, _ = check_budget_invariant(budget, ["recognize", "propose"], GROWTH_OPERAD)
    if ok:  # Should have failed
        return False

    return True


def test_law_validation_gate() -> bool:
    """Test Law 2: VALIDATION_GATE."""
    # Should pass when validation passes
    passing = ValidationResult(passed=True)
    ok, _ = check_validation_gate(passing)
    if not ok:
        return False

    # Should fail when validation fails
    failing = ValidationResult(passed=False, blockers=["test"])
    ok, _ = check_validation_gate(failing)
    if ok:  # Should have failed
        return False

    return True


def test_law_composability() -> bool:
    """Test Law 5: COMPOSABILITY."""
    # Valid composition
    ok, _ = check_composability(GROWTH_OPERAD, "recognize", "propose", "validate")
    if not ok:
        return False

    # Invalid composition (type mismatch)
    ok, _ = check_composability(GROWTH_OPERAD, "recognize", "validate")  # Skip propose
    if ok:  # Should have failed
        return False

    return True


def run_all_law_tests() -> dict[str, bool]:
    """Run all operad law tests."""
    return {
        "BUDGET_INVARIANT": test_law_budget_invariant(),
        "VALIDATION_GATE": test_law_validation_gate(),
        "COMPOSABILITY": test_law_composability(),
    }
