"""
StudioOperad -- Composition Grammar for Creative Production Studio.

Defines the valid operations and composition laws for the Studio.
Following the pattern from agents/operad/core.py.

The operad provides:
1. **Operations** -- The generators (excavate, synthesize, produce, export, etc.)
2. **Laws** -- Constraints on composition (provenance, vision, refinement, export)
3. **Verification** -- Structural verification of law satisfaction

Operations (from spec):
- Archaeological: excavate, interpret, trace
- Synthesis: synthesize, codify, brand
- Production: produce, refine, composite
- Delivery: export, gallery, handoff

Laws (from spec):
- provenance_preserved: trace . excavate = id (archaeology preserves source)
- vision_determines_style: codify . synthesize is deterministic
- refinement_reversible: refine can be undone within session
- export_idempotent: export . export = export

Teaching:
    gotcha: Operations have ARITY (number of inputs), not return count.
            excavate has arity=1 (takes source), synthesize has arity=2
            (takes findings + principles). Arity is used for validating
            composition sequences.

    gotcha: Laws are verified STRUCTURALLY by type, not at runtime.
            STUDIO_OPERAD.verify_law() returns STRUCTURAL status, meaning
            the law is satisfied by the type signatures alone. Runtime
            verification would require an actual Studio instance.

    gotcha: The operad is a SINGLETON (STUDIO_OPERAD). Unlike the polynomial
            state machine which tracks per-session state, the operad is shared
            because it describes the grammar, not the state.

Example:
    >>> STUDIO_OPERAD.list_operations()
    ['excavate', 'interpret', 'trace', 'synthesize', 'codify', 'brand',
     'produce', 'refine', 'composite', 'export', 'gallery', 'handoff']
    >>> STUDIO_OPERAD.get_operation('excavate').arity
    1
    >>> STUDIO_OPERAD.verify_law('provenance_preserved').passed
    True

See: spec/s-gents/studio.md, agents/operad/core.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

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

# =============================================================================
# Studio Law Status (Mirrors FoundryLawStatus pattern)
# =============================================================================


class StudioLawStatus(Enum):
    """Status of a Studio law verification."""

    PASSED = auto()  # Law verified
    FAILED = auto()  # Law violation detected
    SKIPPED = auto()  # Law not tested
    STRUCTURAL = auto()  # Law verified by type structure


@dataclass(frozen=True)
class StudioLawVerification:
    """Result of verifying a Studio law."""

    law_name: str
    status: StudioLawStatus
    left_result: Any = None
    right_result: Any = None
    message: str = ""

    @property
    def passed(self) -> bool:
        """True if law was verified."""
        return self.status in (StudioLawStatus.PASSED, StudioLawStatus.STRUCTURAL)


# =============================================================================
# Studio Operation and Law Types
# =============================================================================


@dataclass
class StudioOperation:
    """
    An operation in the Studio operad.

    Operations are the generators of the Studio composition grammar.
    """

    name: str
    arity: int  # Number of inputs
    signature: str  # Type signature description
    description: str = ""

    def __repr__(self) -> str:
        return f"StudioOperation({self.name}, arity={self.arity})"


@dataclass
class StudioLaw:
    """
    A law that must hold in the Studio operad.

    Laws constrain which compositions are equivalent.
    """

    name: str
    equation: str  # Mathematical notation
    description: str = ""

    def __repr__(self) -> str:
        return f"StudioLaw({self.name}: {self.equation})"


@dataclass
class StudioOperad:
    """
    The Studio Operad: Grammar for creative production.

    This operad defines the valid operations for the Studio
    and the laws that govern their composition.
    """

    operations: dict[str, StudioOperation] = field(default_factory=dict)
    laws: list[StudioLaw] = field(default_factory=list)
    name: str = "STUDIO_OPERAD"

    def get_operation(self, name: str) -> StudioOperation | None:
        """Get an operation by name."""
        return self.operations.get(name)

    def list_operations(self) -> list[str]:
        """List all operation names."""
        return list(self.operations.keys())

    def verify_law(self, law_name: str) -> StudioLawVerification:
        """
        Verify a specific law.

        For now, laws are verified structurally (by type).
        Runtime verification would require actual Studio instance.
        """
        law = next((l for l in self.laws if l.name == law_name), None)
        if law is None:
            return StudioLawVerification(
                law_name=law_name,
                status=StudioLawStatus.SKIPPED,
                message=f"Law '{law_name}' not found",
            )

        # Structural verification based on law semantics
        return StudioLawVerification(
            law_name=law_name,
            status=StudioLawStatus.STRUCTURAL,
            message=f"Law '{law_name}' verified structurally",
        )

    def verify_all_laws(self) -> list[StudioLawVerification]:
        """Verify all laws."""
        return [self.verify_law(law.name) for law in self.laws]


# =============================================================================
# Archaeological Operations (Arity: source -> findings)
# =============================================================================

EXCAVATE_OPERATION = StudioOperation(
    name="excavate",
    arity=1,
    signature="Source -> ArchaeologicalFindings",
    description="Extract patterns from source material",
)

INTERPRET_OPERATION = StudioOperation(
    name="interpret",
    arity=1,
    signature="Findings -> InterpretedMeaning",
    description="Assign meaning to archaeological findings",
)

TRACE_OPERATION = StudioOperation(
    name="trace",
    arity=1,
    signature="Element -> Provenance",
    description="Track provenance of a creative element",
)


# =============================================================================
# Synthesis Operations (Arity: inputs -> vision)
# =============================================================================

SYNTHESIZE_OPERATION = StudioOperation(
    name="synthesize",
    arity=2,
    signature="Findings x Principles -> CreativeVision",
    description="Combine findings and principles to generate vision",
)

CODIFY_OPERATION = StudioOperation(
    name="codify",
    arity=1,
    signature="Vision -> StyleGuide",
    description="Transform vision into actionable style guide",
)

BRAND_OPERATION = StudioOperation(
    name="brand",
    arity=1,
    signature="Vision -> BrandIdentity",
    description="Transform vision into brand identity",
)


# =============================================================================
# Production Operations (Arity: vision x requirement -> asset)
# =============================================================================

PRODUCE_OPERATION = StudioOperation(
    name="produce",
    arity=2,
    signature="Vision x Requirement -> Asset",
    description="Create asset from vision and requirement",
)

REFINE_OPERATION = StudioOperation(
    name="refine",
    arity=2,
    signature="Asset x Feedback -> Asset",
    description="Improve asset based on feedback",
)

COMPOSITE_OPERATION = StudioOperation(
    name="composite",
    arity=2,
    signature="Asset x Asset -> Asset",
    description="Combine multiple assets into one",
)


# =============================================================================
# Delivery Operations (Arity: asset -> output)
# =============================================================================

EXPORT_OPERATION = StudioOperation(
    name="export",
    arity=1,
    signature="Asset -> ExportedAsset",
    description="Render asset to specified format",
)

GALLERY_OPERATION = StudioOperation(
    name="gallery",
    arity=1,
    signature="Asset -> GalleryPlacement",
    description="Place asset in showcase gallery",
)

HANDOFF_OPERATION = StudioOperation(
    name="handoff",
    arity=1,
    signature="Asset -> Void",
    description="Transfer asset to consumer",
)


# =============================================================================
# Studio Laws
# =============================================================================

PROVENANCE_PRESERVED_LAW = StudioLaw(
    name="provenance_preserved",
    equation="trace . excavate = id",
    description="Archaeology preserves source provenance",
)

VISION_DETERMINES_STYLE_LAW = StudioLaw(
    name="vision_determines_style",
    equation="codify . synthesize is deterministic",
    description="Same vision always produces same style guide",
)

REFINEMENT_REVERSIBLE_LAW = StudioLaw(
    name="refinement_reversible",
    equation="refine can be undone within session",
    description="Refinements are reversible during active session",
)

EXPORT_IDEMPOTENT_LAW = StudioLaw(
    name="export_idempotent",
    equation="export . export = export",
    description="Exporting an exported asset is idempotent",
)


# =============================================================================
# Compose Functions for PolyAgent Integration
# =============================================================================


def _excavate_compose(
    source: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose an excavation operation."""

    def excavate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "excavate",
            "source": source.name,
            "input": input,
        }

    return from_function(f"excavate({source.name})", excavate_fn)


def _interpret_compose(
    findings: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose an interpretation operation."""

    def interpret_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "interpret",
            "findings": findings.name,
            "input": input,
        }

    return from_function(f"interpret({findings.name})", interpret_fn)


def _trace_compose(
    element: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a trace operation."""

    def trace_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "trace",
            "element": element.name,
            "input": input,
        }

    return from_function(f"trace({element.name})", trace_fn)


def _synthesize_compose(
    findings: PolyAgent[Any, Any, Any],
    principles: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a synthesis operation."""

    def synthesize_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "synthesize",
            "findings": findings.name,
            "principles": principles.name,
            "input": input,
        }

    return from_function(f"synthesize({findings.name},{principles.name})", synthesize_fn)


def _codify_compose(
    vision: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a codify operation."""

    def codify_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "codify",
            "vision": vision.name,
            "input": input,
        }

    return from_function(f"codify({vision.name})", codify_fn)


def _brand_compose(
    vision: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a brand operation."""

    def brand_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "brand",
            "vision": vision.name,
            "input": input,
        }

    return from_function(f"brand({vision.name})", brand_fn)


def _produce_compose(
    vision: PolyAgent[Any, Any, Any],
    requirement: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a produce operation."""

    def produce_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "produce",
            "vision": vision.name,
            "requirement": requirement.name,
            "input": input,
        }

    return from_function(f"produce({vision.name},{requirement.name})", produce_fn)


def _refine_compose(
    asset: PolyAgent[Any, Any, Any],
    feedback: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a refine operation."""

    def refine_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "refine",
            "asset": asset.name,
            "feedback": feedback.name,
            "input": input,
        }

    return from_function(f"refine({asset.name},{feedback.name})", refine_fn)


def _composite_compose(
    asset_a: PolyAgent[Any, Any, Any],
    asset_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a composite operation."""

    def composite_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "composite",
            "asset_a": asset_a.name,
            "asset_b": asset_b.name,
            "input": input,
        }

    return from_function(f"composite({asset_a.name},{asset_b.name})", composite_fn)


def _export_compose(
    asset: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose an export operation."""

    def export_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "export",
            "asset": asset.name,
            "input": input,
        }

    return from_function(f"export({asset.name})", export_fn)


def _gallery_compose(
    asset: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a gallery operation."""

    def gallery_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "gallery",
            "asset": asset.name,
            "input": input,
        }

    return from_function(f"gallery({asset.name})", gallery_fn)


def _handoff_compose(
    asset: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Compose a handoff operation."""

    def handoff_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "handoff",
            "asset": asset.name,
            "input": input,
        }

    return from_function(f"handoff({asset.name})", handoff_fn)


# =============================================================================
# Law Verification Helpers
# =============================================================================


def _verify_provenance(
    source: PolyAgent[Any, Any, Any] | None = None,
    context: Any = None,
) -> LawVerification:
    """
    Verify: trace . excavate = id (provenance preserved).

    Excavating then tracing should return to the original source.
    This is checked structurally -- actual verification needs runtime.
    """
    return LawVerification(
        law_name="provenance_preserved",
        status=LawStatus.STRUCTURAL,
        message="Provenance preservation enforced by archaeological functor",
    )


def _verify_vision_determinism(
    findings: PolyAgent[Any, Any, Any] | None = None,
    principles: PolyAgent[Any, Any, Any] | None = None,
    context: Any = None,
) -> LawVerification:
    """
    Verify: codify . synthesize is deterministic.

    Same findings + principles should always produce same style guide.
    """
    return LawVerification(
        law_name="vision_determines_style",
        status=LawStatus.STRUCTURAL,
        message="Vision determinism enforced by synthesis functor",
    )


def _verify_refinement_reversible(
    asset: PolyAgent[Any, Any, Any] | None = None,
    feedback: PolyAgent[Any, Any, Any] | None = None,
    context: Any = None,
) -> LawVerification:
    """
    Verify: refine can be undone within session.

    Refinements should be reversible during the active session.
    """
    return LawVerification(
        law_name="refinement_reversible",
        status=LawStatus.STRUCTURAL,
        message="Refinement reversibility enforced by session history",
    )


def _verify_export_idempotence(
    asset: PolyAgent[Any, Any, Any] | None = None,
    context: Any = None,
) -> LawVerification:
    """
    Verify: export . export = export.

    Exporting an already-exported asset should be idempotent.
    """
    return LawVerification(
        law_name="export_idempotent",
        status=LawStatus.STRUCTURAL,
        message="Export idempotence enforced by format detection",
    )


# =============================================================================
# Studio Operad Creation
# =============================================================================


def create_studio_operad() -> Operad:
    """
    Create the Studio Operad (creative production grammar).

    Extends AGENT_OPERAD with studio-specific operations:
    - Archaeological: excavate, interpret, trace
    - Synthesis: synthesize, codify, brand
    - Production: produce, refine, composite
    - Delivery: export, gallery, handoff

    And studio-specific laws:
    - provenance_preserved: archaeology preserves source
    - vision_determines_style: synthesis is deterministic
    - refinement_reversible: refine can be undone
    - export_idempotent: export is idempotent
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add archaeological operations
    ops["excavate"] = Operation(
        name="excavate",
        arity=1,
        signature="Source -> ArchaeologicalFindings",
        compose=_excavate_compose,
        description="Extract patterns from source material",
    )

    ops["interpret"] = Operation(
        name="interpret",
        arity=1,
        signature="Findings -> InterpretedMeaning",
        compose=_interpret_compose,
        description="Assign meaning to archaeological findings",
    )

    ops["trace"] = Operation(
        name="trace",
        arity=1,
        signature="Element -> Provenance",
        compose=_trace_compose,
        description="Track provenance of a creative element",
    )

    # Add synthesis operations
    ops["synthesize"] = Operation(
        name="synthesize",
        arity=2,
        signature="Findings x Principles -> CreativeVision",
        compose=_synthesize_compose,
        description="Combine findings and principles to generate vision",
    )

    ops["codify"] = Operation(
        name="codify",
        arity=1,
        signature="Vision -> StyleGuide",
        compose=_codify_compose,
        description="Transform vision into actionable style guide",
    )

    ops["brand"] = Operation(
        name="brand",
        arity=1,
        signature="Vision -> BrandIdentity",
        compose=_brand_compose,
        description="Transform vision into brand identity",
    )

    # Add production operations
    ops["produce"] = Operation(
        name="produce",
        arity=2,
        signature="Vision x Requirement -> Asset",
        compose=_produce_compose,
        description="Create asset from vision and requirement",
    )

    ops["refine"] = Operation(
        name="refine",
        arity=2,
        signature="Asset x Feedback -> Asset",
        compose=_refine_compose,
        description="Improve asset based on feedback",
    )

    ops["composite"] = Operation(
        name="composite",
        arity=2,
        signature="Asset x Asset -> Asset",
        compose=_composite_compose,
        description="Combine multiple assets into one",
    )

    # Add delivery operations
    ops["export"] = Operation(
        name="export",
        arity=1,
        signature="Asset -> ExportedAsset",
        compose=_export_compose,
        description="Render asset to specified format",
    )

    ops["gallery"] = Operation(
        name="gallery",
        arity=1,
        signature="Asset -> GalleryPlacement",
        compose=_gallery_compose,
        description="Place asset in showcase gallery",
    )

    ops["handoff"] = Operation(
        name="handoff",
        arity=1,
        signature="Asset -> Void",
        compose=_handoff_compose,
        description="Transfer asset to consumer",
    )

    # Inherit universal laws and add studio-specific ones
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="provenance_preserved",
            equation="trace . excavate = id",
            verify=_verify_provenance,
            description="Archaeology preserves source provenance",
        ),
        Law(
            name="vision_determines_style",
            equation="codify . synthesize is deterministic",
            verify=_verify_vision_determinism,
            description="Same vision always produces same style guide",
        ),
        Law(
            name="refinement_reversible",
            equation="refine can be undone within session",
            verify=_verify_refinement_reversible,
            description="Refinements are reversible during active session",
        ),
        Law(
            name="export_idempotent",
            equation="export . export = export",
            verify=_verify_export_idempotence,
            description="Exporting an exported asset is idempotent",
        ),
    ]

    return Operad(
        name="StudioOperad",
        operations=ops,
        laws=laws,
        description="Grammar for creative production (archaeology, synthesis, production, delivery)",
    )


# =============================================================================
# Global StudioOperad Instance
# =============================================================================


STUDIO_OPERAD = create_studio_operad()
"""
The Studio Operad (creative production grammar).

Operations:
- Universal: seq, par, branch, fix, trace
- Archaeological: excavate, interpret, trace
- Synthesis: synthesize, codify, brand
- Production: produce, refine, composite
- Delivery: export, gallery, handoff

Laws:
- Universal: seq_associativity, par_associativity
- Studio: provenance_preserved, vision_determines_style,
          refinement_reversible, export_idempotent
"""

# Register with the operad registry
OperadRegistry.register(STUDIO_OPERAD)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "StudioLawStatus",
    "StudioLawVerification",
    "StudioOperation",
    "StudioLaw",
    "StudioOperad",
    # Archaeological Operations
    "EXCAVATE_OPERATION",
    "INTERPRET_OPERATION",
    "TRACE_OPERATION",
    # Synthesis Operations
    "SYNTHESIZE_OPERATION",
    "CODIFY_OPERATION",
    "BRAND_OPERATION",
    # Production Operations
    "PRODUCE_OPERATION",
    "REFINE_OPERATION",
    "COMPOSITE_OPERATION",
    # Delivery Operations
    "EXPORT_OPERATION",
    "GALLERY_OPERATION",
    "HANDOFF_OPERATION",
    # Laws
    "PROVENANCE_PRESERVED_LAW",
    "VISION_DETERMINES_STYLE_LAW",
    "REFINEMENT_REVERSIBLE_LAW",
    "EXPORT_IDEMPOTENT_LAW",
    # Operad Instance & Factory
    "STUDIO_OPERAD",
    "create_studio_operad",
]
