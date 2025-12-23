"""
Validation Crown Jewel: Evidence-Based Decision Making.

The Validation service provides:
- Proposition: Atomic measurable claims
- Gate: Decision checkpoints
- Initiative: Bodies of work with validation criteria
- Phase: Stages within phased initiatives

Philosophy:
    "If you can't measure it, you can't claim it."
    "The proof IS the decision. The validation IS the witness."

See: spec/validation/schema.md
See: plans/validation-framework-implementation.md
"""

from .engine import (
    ValidationEngine,
)
from .runner import (
    check_gate,
    check_proposition,
)
from .schema import (
    # Results
    Blocker,
    # Enums
    Direction,
    # Core primitives
    Gate,
    GateCondition,
    GateResult,
    Initiative,
    InitiativeStatus,
    MetricType,
    Phase,
    Proposition,
    PropositionResult,
    ValidationRun,
)
from .store import (
    ValidationStore,
    ValidationStoreError,
    get_validation_store,
    reset_validation_store,
    set_validation_store,
)

__all__ = [
    # Enums
    "Direction",
    "GateCondition",
    "MetricType",
    # Core primitives
    "Gate",
    "Initiative",
    "Phase",
    "Proposition",
    # Results
    "Blocker",
    "GateResult",
    "InitiativeStatus",
    "PropositionResult",
    "ValidationRun",
    # Engine
    "ValidationEngine",
    # Runner
    "check_gate",
    "check_proposition",
    # Store
    "ValidationStore",
    "ValidationStoreError",
    "get_validation_store",
    "reset_validation_store",
    "set_validation_store",
]
