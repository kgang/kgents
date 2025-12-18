"""
AGENTESE Design Context Resolver

Design Language System integration with AGENTESE.

Provides paths for the three orthogonal design functors:
- concept.design.layout.*    Layout composition grammar
- concept.design.content.*   Content degradation grammar
- concept.design.motion.*    Animation composition grammar
- concept.design.operad.*    Unified design operad

The core insight: UI = Layout[D] ∘ Content[D] ∘ Motion[M]

These three dimensions compose orthogonally. This context exposes
the design operads from agents/design/ via AGENTESE paths.

Phase 4 of the Design Language Consolidation plan.
See: plans/design-language-consolidation.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Affordances
# =============================================================================

DESIGN_AFFORDANCES: dict[str, tuple[str, ...]] = {
    # concept.design.layout.* affordances
    "layout": ("manifest", "compose", "operations", "laws", "verify"),
    # concept.design.content.* affordances
    "content": ("manifest", "degrade", "operations", "laws", "verify"),
    # concept.design.motion.* affordances
    "motion": ("manifest", "apply", "operations", "laws", "verify"),
    # concept.design.operad.* affordances
    "operad": ("manifest", "operations", "laws", "verify", "naturality"),
    # Generic design affordances
    "default": ("manifest", "operations", "laws"),
}


# =============================================================================
# Layout Node - concept.design.layout.*
# =============================================================================


@node(
    "concept.design.layout",
    description="Layout composition grammar - split, stack, drawer, float",
)
@dataclass
class LayoutDesignNode(BaseLogosNode):
    """
    concept.design.layout - Layout composition grammar.

    Provides access to LAYOUT_OPERAD operations:
    - split: Two-pane layout with collapse behavior
    - stack: Vertical/horizontal stack
    - drawer: Collapsible drawer pattern
    - float: Floating action buttons

    Laws:
    - split(a, drawer(t, b)) ≅ drawer(t, split(a, b)) at compact density
    """

    _handle: str = "concept.design.layout"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return DESIGN_AFFORDANCES["layout"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Manifest layout operad summary."""
        from agents.design import LAYOUT_OPERAD

        return BasicRendering(
            summary=f"Layout Operad: {LAYOUT_OPERAD.name}",
            content=(
                f"Operad: {LAYOUT_OPERAD.name}\n"
                f"Operations: {', '.join(LAYOUT_OPERAD.operations.keys())}\n"
                f"Laws: {len(LAYOUT_OPERAD.laws)}\n"
                f"Description: {LAYOUT_OPERAD.description}"
            ),
            metadata={
                "name": LAYOUT_OPERAD.name,
                "operations": list(LAYOUT_OPERAD.operations.keys()),
                "law_count": len(LAYOUT_OPERAD.laws),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle layout aspect invocations."""
        from agents.design import LAYOUT_OPERAD

        match aspect:
            case "operations":
                return {
                    name: {
                        "arity": op.arity,
                        "signature": op.signature,
                        "description": op.description,
                    }
                    for name, op in LAYOUT_OPERAD.operations.items()
                }

            case "laws":
                return [
                    {
                        "name": law.name,
                        "equation": law.equation,
                        "description": law.description,
                    }
                    for law in LAYOUT_OPERAD.laws
                ]

            case "verify":
                results = []
                for law in LAYOUT_OPERAD.laws:
                    verification = law.verify()
                    results.append(
                        {
                            "law": law.name,
                            "status": verification.status.name.lower(),  # "passed", "structural", etc.
                            "passed": verification.passed,  # True if PASSED or STRUCTURAL
                            "message": verification.message,
                        }
                    )
                return results

            case "compose":
                op_name = kwargs.get("operation")
                if op_name and op_name in LAYOUT_OPERAD.operations:
                    op = LAYOUT_OPERAD.operations[op_name]
                    return {
                        "operation": op_name,
                        "arity": op.arity,
                        "signature": op.signature,
                        "compose_available": op.compose is not None,
                    }
                return {"error": f"Unknown operation: {op_name}"}

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# Content Node - concept.design.content.*
# =============================================================================


@node(
    "concept.design.content",
    description="Content degradation grammar - degrade based on space",
)
@dataclass
class ContentDesignNode(BaseLogosNode):
    """
    concept.design.content - Content degradation grammar.

    Provides access to CONTENT_OPERAD operations:
    - degrade: Reduce content to fit space
    - compose: Combine widget content

    Laws:
    - degrade(x, icon) ⊆ degrade(x, title) ⊆ degrade(x, summary) ⊆ degrade(x, full)
    - compose(degrade(a, L), degrade(b, L)) = degrade(compose(a, b), L)
    """

    _handle: str = "concept.design.content"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return DESIGN_AFFORDANCES["content"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Manifest content operad summary."""
        from agents.design import CONTENT_OPERAD

        return BasicRendering(
            summary=f"Content Operad: {CONTENT_OPERAD.name}",
            content=(
                f"Operad: {CONTENT_OPERAD.name}\n"
                f"Operations: {', '.join(CONTENT_OPERAD.operations.keys())}\n"
                f"Laws: {len(CONTENT_OPERAD.laws)}\n"
                f"Description: {CONTENT_OPERAD.description}"
            ),
            metadata={
                "name": CONTENT_OPERAD.name,
                "operations": list(CONTENT_OPERAD.operations.keys()),
                "law_count": len(CONTENT_OPERAD.laws),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle content aspect invocations."""
        from agents.design import CONTENT_OPERAD, ContentLevel

        match aspect:
            case "operations":
                return {
                    name: {
                        "arity": op.arity,
                        "signature": op.signature,
                        "description": op.description,
                    }
                    for name, op in CONTENT_OPERAD.operations.items()
                }

            case "laws":
                return [
                    {
                        "name": law.name,
                        "equation": law.equation,
                        "description": law.description,
                    }
                    for law in CONTENT_OPERAD.laws
                ]

            case "verify":
                results = []
                for law in CONTENT_OPERAD.laws:
                    verification = law.verify()
                    results.append(
                        {
                            "law": law.name,
                            "status": verification.status.name.lower(),
                            "passed": verification.passed,
                            "message": verification.message,
                        }
                    )
                return results

            case "degrade":
                # Return content level information
                level_name = kwargs.get("level", "full")
                try:
                    level = ContentLevel[level_name.upper()]
                    return {
                        "level": level.value,
                        "includes": [
                            l.value for l in ContentLevel if level.includes(l)
                        ],
                    }
                except KeyError:
                    return {
                        "error": f"Unknown level: {level_name}",
                        "valid_levels": [l.value for l in ContentLevel],
                    }

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# Motion Node - concept.design.motion.*
# =============================================================================


@node(
    "concept.design.motion",
    description="Animation composition grammar - breathe, pop, shake, shimmer",
)
@dataclass
class MotionDesignNode(BaseLogosNode):
    """
    concept.design.motion - Animation composition grammar.

    Provides access to MOTION_OPERAD operations:
    - identity: No animation
    - breathe: Gentle pulse
    - pop: Scale bounce
    - shake: Horizontal vibration
    - shimmer: Highlight sweep
    - chain: Sequential animation
    - parallel: Simultaneous animation

    Laws:
    - chain(identity, m) = m = chain(m, identity)
    - !shouldAnimate => all operations = identity
    """

    _handle: str = "concept.design.motion"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return DESIGN_AFFORDANCES["motion"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Manifest motion operad summary."""
        from agents.design import MOTION_OPERAD

        return BasicRendering(
            summary=f"Motion Operad: {MOTION_OPERAD.name}",
            content=(
                f"Operad: {MOTION_OPERAD.name}\n"
                f"Operations: {', '.join(MOTION_OPERAD.operations.keys())}\n"
                f"Laws: {len(MOTION_OPERAD.laws)}\n"
                f"Description: {MOTION_OPERAD.description}"
            ),
            metadata={
                "name": MOTION_OPERAD.name,
                "operations": list(MOTION_OPERAD.operations.keys()),
                "law_count": len(MOTION_OPERAD.laws),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle motion aspect invocations."""
        from agents.design import MOTION_OPERAD, MotionType

        match aspect:
            case "operations":
                return {
                    name: {
                        "arity": op.arity,
                        "signature": op.signature,
                        "description": op.description,
                    }
                    for name, op in MOTION_OPERAD.operations.items()
                }

            case "laws":
                return [
                    {
                        "name": law.name,
                        "equation": law.equation,
                        "description": law.description,
                    }
                    for law in MOTION_OPERAD.laws
                ]

            case "verify":
                results = []
                for law in MOTION_OPERAD.laws:
                    verification = law.verify()
                    results.append(
                        {
                            "law": law.name,
                            "status": verification.status.name.lower(),
                            "passed": verification.passed,
                            "message": verification.message,
                        }
                    )
                return results

            case "apply":
                # Return motion type information
                motion_name = kwargs.get("motion", "identity")
                try:
                    motion = MotionType[motion_name.upper()]
                    return {
                        "motion": motion.value,
                        "is_identity": motion == MotionType.IDENTITY,
                    }
                except KeyError:
                    return {
                        "error": f"Unknown motion: {motion_name}",
                        "valid_motions": [m.value for m in MotionType],
                    }

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# Operad Node - concept.design.operad.*
# =============================================================================


@node(
    "concept.design.operad",
    description="Unified design operad - Layout x Content x Motion",
)
@dataclass
class DesignOperadNode(BaseLogosNode):
    """
    concept.design.operad - Unified design operad.

    Combines all three sub-operads with the naturality law:
        Layout[D] ∘ Content[D] ∘ Motion[M] is natural

    This means UI = structure × content × motion, and these compose orthogonally.
    """

    _handle: str = "concept.design.operad"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return DESIGN_AFFORDANCES["operad"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Manifest unified design operad summary."""
        from agents.design import DESIGN_OPERAD

        return BasicRendering(
            summary=f"Design Operad: {DESIGN_OPERAD.name}",
            content=(
                f"Operad: {DESIGN_OPERAD.name}\n"
                f"Operations: {len(DESIGN_OPERAD.operations)}\n"
                f"Laws: {len(DESIGN_OPERAD.laws)}\n"
                f"Description: {DESIGN_OPERAD.description}\n\n"
                f"Core Insight: UI = Layout[D] ∘ Content[D] ∘ Motion[M]"
            ),
            metadata={
                "name": DESIGN_OPERAD.name,
                "operation_count": len(DESIGN_OPERAD.operations),
                "law_count": len(DESIGN_OPERAD.laws),
                "sub_operads": ["LAYOUT", "CONTENT", "MOTION"],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle design operad aspect invocations."""
        from agents.design import DESIGN_OPERAD

        match aspect:
            case "operations":
                return {
                    name: {
                        "arity": op.arity,
                        "signature": op.signature,
                        "description": op.description,
                    }
                    for name, op in DESIGN_OPERAD.operations.items()
                }

            case "laws":
                return [
                    {
                        "name": law.name,
                        "equation": law.equation,
                        "description": law.description,
                    }
                    for law in DESIGN_OPERAD.laws
                ]

            case "verify":
                results = []
                for law in DESIGN_OPERAD.laws:
                    verification = law.verify()
                    results.append(
                        {
                            "law": law.name,
                            "status": verification.status.name.lower(),
                            "passed": verification.passed,  # True if PASSED or STRUCTURAL
                            "message": verification.message,
                        }
                    )
                all_passed = all(r["passed"] for r in results)
                return {
                    "all_passed": all_passed,
                    "results": results,
                }

            case "naturality":
                # Check the naturality law specifically
                naturality_law = next(
                    (
                        law
                        for law in DESIGN_OPERAD.laws
                        if law.name == "composition_natural"
                    ),
                    None,
                )
                if naturality_law:
                    verification = naturality_law.verify()
                    return {
                        "law": naturality_law.name,
                        "equation": naturality_law.equation,
                        "status": verification.status.name.lower(),
                        "passed": verification.passed,
                        "message": verification.message,
                    }
                return {"error": "Naturality law not found"}

            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# Design Context Node - concept.design.*
# =============================================================================


@node(
    "concept.design",
    description="Design Language System - UI composition via operads",
)
@dataclass
class DesignContextNode(BaseLogosNode):
    """
    concept.design - Design Language System root.

    Routes to sub-nodes:
    - concept.design.layout.*  → LayoutDesignNode
    - concept.design.content.* → ContentDesignNode
    - concept.design.motion.*  → MotionDesignNode
    - concept.design.operad.*  → DesignOperadNode
    """

    _handle: str = "concept.design"
    layout_node: LayoutDesignNode = field(default_factory=LayoutDesignNode)
    content_node: ContentDesignNode = field(default_factory=ContentDesignNode)
    motion_node: MotionDesignNode = field(default_factory=MotionDesignNode)
    operad_node: DesignOperadNode = field(default_factory=DesignOperadNode)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return DESIGN_AFFORDANCES["default"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Manifest design language overview."""
        return BasicRendering(
            summary="Design Language System",
            content=(
                "UI = Layout[D] ∘ Content[D] ∘ Motion[M]\n\n"
                "Three orthogonal dimensions:\n"
                "- Layout: split, stack, drawer, float\n"
                "- Content: degrade, compose\n"
                "- Motion: breathe, pop, shake, shimmer, chain, parallel\n\n"
                "Paths:\n"
                "- concept.design.layout.*\n"
                "- concept.design.content.*\n"
                "- concept.design.motion.*\n"
                "- concept.design.operad.*"
            ),
            metadata={
                "dimensions": ["layout", "content", "motion"],
                "operad": "DESIGN_OPERAD",
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route to sub-nodes based on aspect."""
        match aspect:
            case "layout":
                return await self.layout_node.manifest(observer)
            case "content":
                return await self.content_node.manifest(observer)
            case "motion":
                return await self.motion_node.manifest(observer)
            case "operad":
                return await self.operad_node.manifest(observer)
            case "operations":
                from agents.design import DESIGN_OPERAD

                return list(DESIGN_OPERAD.operations.keys())
            case "laws":
                from agents.design import DESIGN_OPERAD

                return [law.name for law in DESIGN_OPERAD.laws]
            case _:
                msg = f"Unknown aspect: {aspect}"
                raise ValueError(msg)


# =============================================================================
# Resolver and Factory
# =============================================================================


@dataclass
class DesignContextResolver:
    """
    Resolver for design context paths.

    Handles:
    - concept.design (root)
    - concept.design.layout.*
    - concept.design.content.*
    - concept.design.motion.*
    - concept.design.operad.*
    """

    design_node: DesignContextNode = field(default_factory=DesignContextNode)

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode | None:
        """Resolve a design path to its node."""
        if not rest:
            return self.design_node

        sub_path = rest[0]
        match sub_path:
            case "layout":
                return self.design_node.layout_node
            case "content":
                return self.design_node.content_node
            case "motion":
                return self.design_node.motion_node
            case "operad":
                return self.design_node.operad_node
            case _:
                return self.design_node


def create_design_resolver() -> DesignContextResolver:
    """Create a design context resolver."""
    return DesignContextResolver()


def create_design_node() -> DesignContextNode:
    """Create a design context node."""
    return DesignContextNode()


# =============================================================================
# Path Registry (for crown_jewels.py documentation)
# =============================================================================

DESIGN_PATHS: dict[str, str] = {
    "concept.design.manifest": "Design Language System overview",
    "concept.design.layout.manifest": "Layout operad state",
    "concept.design.layout.operations": "Layout operations (split, stack, drawer, float)",
    "concept.design.layout.laws": "Layout composition laws",
    "concept.design.layout.verify": "Verify layout laws",
    "concept.design.layout.compose": "Apply layout operation",
    "concept.design.content.manifest": "Content operad state",
    "concept.design.content.operations": "Content operations (degrade, compose)",
    "concept.design.content.laws": "Content degradation laws",
    "concept.design.content.verify": "Verify content laws",
    "concept.design.content.degrade": "Apply content degradation",
    "concept.design.motion.manifest": "Motion operad state",
    "concept.design.motion.operations": "Motion operations (breathe, pop, shake, shimmer, chain, parallel)",
    "concept.design.motion.laws": "Motion composition laws",
    "concept.design.motion.verify": "Verify motion laws",
    "concept.design.motion.apply": "Apply motion primitive",
    "concept.design.operad.manifest": "Unified design operad",
    "concept.design.operad.operations": "All design operations",
    "concept.design.operad.laws": "All design laws (including naturality)",
    "concept.design.operad.verify": "Verify all design laws",
    "concept.design.operad.naturality": "Check Layout ∘ Content ∘ Motion naturality",
}


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Affordances
    "DESIGN_AFFORDANCES",
    # Nodes
    "LayoutDesignNode",
    "ContentDesignNode",
    "MotionDesignNode",
    "DesignOperadNode",
    "DesignContextNode",
    # Resolver
    "DesignContextResolver",
    # Factories
    "create_design_resolver",
    "create_design_node",
    # Path Registry
    "DESIGN_PATHS",
]
