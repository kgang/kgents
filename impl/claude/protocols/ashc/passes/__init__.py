"""
ASHC Pass Operad: Categorical Transform Engine

Passes are morphisms. The compiler is a category.

The Pass Operad treats compiler passes as morphisms with verified laws.
Bootstrap agents become the canonical passes, and composition is the
primary operation.

Example:
    from protocols.ashc.passes import PASS_OPERAD, GroundPass, JudgePass

    # Compose passes
    pipeline = ground >> judge >> fix

    # Verify laws hold
    result = await PASS_OPERAD.verify_laws(pipeline)
    assert result.all_passed

    # Run pipeline
    ir = await pipeline.invoke(None)
    print(ir.witnesses)  # Full audit trail
"""

from .bootstrap import (
    ContradictPass,
    FixPass,
    GroundPass,
    IdentityPass,
    JudgePass,
    SublatePass,
)
from .composition import ComposedPass
from .core import (
    CompositionLaw,
    LawResult,
    PassProtocol,
    ProofCarryingIR,
    VerificationGraph,
)
from .operad import (
    PASS_OPERAD,
    PassOperad,
    PassOperation,
    render_law_verification,
    render_operad_manifest,
)

__all__ = [
    # Core types
    "PassProtocol",
    "ProofCarryingIR",
    "VerificationGraph",
    "LawResult",
    "CompositionLaw",
    # Bootstrap passes
    "IdentityPass",
    "GroundPass",
    "JudgePass",
    "ContradictPass",
    "SublatePass",
    "FixPass",
    # Composition
    "ComposedPass",
    # Operad
    "PassOperad",
    "PassOperation",
    "PASS_OPERAD",
    # Rendering
    "render_operad_manifest",
    "render_law_verification",
]
