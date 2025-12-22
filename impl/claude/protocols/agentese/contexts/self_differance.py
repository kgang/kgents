"""
AGENTESE Différance Self Context.

self.differance.* paths for navigating the spec/impl graph.

The self-knowing system: understanding why decisions were made.

AGENTESE Paths:
- self.differance.why       - "Why did this happen?"
- self.differance.navigate  - Browse spec/impl graph
- self.differance.concretize - Spec -> Impl (traced)
- self.differance.abstract   - Impl -> Spec (reverse)

See: spec/protocols/differance.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import AspectCategory, aspect
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from agents.differance import DifferanceStore, TraceMonoid
    from bootstrap.umwelt import Umwelt


# === Affordances ===

SELF_DIFFERANCE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "why",
    "navigate",
    "concretize",
    "abstract",
)


# === SelfDifferanceNode ===


@node("self.differance", description="Spec/Impl navigation and explainability")
@dataclass
class SelfDifferanceNode(BaseLogosNode):
    """
    self.differance - The self-knowing system.

    Navigate between specifications and implementations,
    understanding the lineage of decisions.

    AGENTESE paths:
    - self.differance.manifest    # View navigation state
    - self.differance.why         # "Why did this happen?" (delegates to time.differance)
    - self.differance.navigate    # Browse spec/impl graph
    - self.differance.concretize  # Spec -> Impl (traced)
    - self.differance.abstract    # Impl -> Spec (reverse)
    """

    _handle: str = "self.differance"

    # Integration with time.differance for heritage queries
    _time_differance_node: Any = None

    # Track current navigation position
    _current_spec: str | None = None
    _current_impl: str | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Self differance affordances."""
        return SELF_DIFFERANCE_AFFORDANCES

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View spec/impl navigation state",
    )
    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View current navigation state."""
        return BasicRendering(
            summary="Différance Navigation",
            content=(
                "Self-knowing system for spec/impl traversal. "
                "Use 'why' to understand decision lineage, "
                "'navigate' to browse the graph."
            ),
            metadata={
                "current_spec": self._current_spec,
                "current_impl": self._current_impl,
                "route": "/differance/navigate",
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle self differance aspects."""
        match aspect:
            case "why":
                return await self._why(observer, **kwargs)
            case "navigate":
                return await self._navigate(observer, **kwargs)
            case "concretize":
                return await self._concretize(observer, **kwargs)
            case "abstract":
                return await self._abstract(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _why(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        "Why did this happen?" - Explain a decision.

        AGENTESE: self.differance.why

        This delegates to time.differance.why but provides
        a self-context framing.

        Args:
            output_id: ID of the output to explain
            format: Output format - "summary", "full", "cli"

        Returns:
            Explanation of why this output exists
        """
        output_id = kwargs.get("output_id") or kwargs.get("id")
        if not output_id:
            return {
                "error": "output_id (or 'id') is required",
                "aspect": "why",
                "usage": "self.differance.why(output_id='trace_xyz')",
            }

        # Delegate to time.differance.why if available
        if self._time_differance_node:
            result: dict[str, Any] = await self._time_differance_node._why(observer, **kwargs)
            # Add self-context framing
            if "error" not in result:
                result["context"] = "self"
                result["interpretation"] = (
                    f"I made {result.get('decisions_made', 0)} decisions "
                    f"to produce this output, considering "
                    f"{result.get('alternatives_considered', 0)} alternatives."
                )
            return result

        # Fallback without time.differance integration
        return {
            "output_id": output_id,
            "context": "self",
            "status": "limited",
            "note": "Full 'why' requires time.differance integration. "
            "Connect via set_time_differance_node().",
        }

    async def _navigate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Browse spec/impl graph.

        AGENTESE: self.differance.navigate

        Args:
            target: Target to navigate to (spec path or impl path)
            direction: "up" (to spec), "down" (to impl), or "lateral"

        Returns:
            Navigation result with related specs/impls
        """
        target = kwargs.get("target")
        direction = kwargs.get("direction", "lateral")

        if not target:
            # Return current position and available moves
            return {
                "current_spec": self._current_spec,
                "current_impl": self._current_impl,
                "available_directions": ["up", "down", "lateral"],
                "usage": "self.differance.navigate(target='spec/path', direction='down')",
            }

        # Update navigation position
        if target.startswith("spec/"):
            self._current_spec = target
            return {
                "navigated_to": target,
                "type": "spec",
                "direction": direction,
                "related_impls": self._find_related_impls(target),
            }
        elif target.startswith("impl/"):
            self._current_impl = target
            return {
                "navigated_to": target,
                "type": "impl",
                "direction": direction,
                "related_specs": self._find_related_specs(target),
            }
        else:
            return {
                "target": target,
                "error": "Target should start with 'spec/' or 'impl/'",
                "aspect": "navigate",
            }

    async def _concretize(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Spec -> Impl (traced).

        AGENTESE: self.differance.concretize

        This represents the fundamental différance operation:
        making a specification concrete while recording the
        decisions made and alternatives considered.

        Args:
            spec_path: Path to the specification
            strategy: Concretization strategy (default: "direct")

        Returns:
            Concretization result with trace
        """
        spec_path = kwargs.get("spec_path")
        if not spec_path:
            return {
                "error": "spec_path is required",
                "aspect": "concretize",
                "usage": "self.differance.concretize(spec_path='spec/agents/brain.md')",
            }

        strategy = kwargs.get("strategy", "direct")

        # For now, concretization is declarative (actual implementation would
        # invoke the appropriate generators/transformers)
        return {
            "spec_path": spec_path,
            "strategy": strategy,
            "status": "planned",
            "trace_id": None,  # Would be generated on actual concretization
            "note": (
                "Concretization creates a traced transformation from spec to impl. "
                "The trace records what decisions were made and what alternatives "
                "were considered. Use time.differance.heritage to see the result."
            ),
        }

    async def _abstract(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Impl -> Spec (reverse).

        AGENTESE: self.differance.abstract

        The reverse of concretize: extract a specification
        from an implementation.

        Args:
            impl_path: Path to the implementation
            style: Abstraction style (default: "essence")

        Returns:
            Abstraction result
        """
        impl_path = kwargs.get("impl_path")
        if not impl_path:
            return {
                "error": "impl_path is required",
                "aspect": "abstract",
                "usage": "self.differance.abstract(impl_path='impl/claude/agents/brain/')",
            }

        style = kwargs.get("style", "essence")

        return {
            "impl_path": impl_path,
            "style": style,
            "status": "planned",
            "note": (
                "Abstraction extracts the essential specification from "
                "an implementation. This is the reverse of concretize."
            ),
        }

    # === Helper Methods ===

    def _find_related_impls(self, spec_path: str) -> list[str]:
        """Find implementations related to a spec."""
        # Pattern: spec/X/Y.md -> impl/claude/X/
        if spec_path.startswith("spec/"):
            impl_base = spec_path.replace("spec/", "impl/claude/")
            impl_base = impl_base.rsplit(".", 1)[0]  # Remove .md
            return [impl_base + "/"]
        return []

    def _find_related_specs(self, impl_path: str) -> list[str]:
        """Find specs related to an implementation."""
        # Pattern: impl/claude/X/ -> spec/X/
        if impl_path.startswith("impl/claude/"):
            spec_base = impl_path.replace("impl/claude/", "spec/")
            # Remove trailing slash and add .md
            spec_base = spec_base.rstrip("/")
            return [spec_base + ".md"]
        return []

    def set_time_differance_node(self, node: Any) -> None:
        """Set the time.differance node for delegation."""
        self._time_differance_node = node


# === Factory Functions ===

_self_differance_node: SelfDifferanceNode | None = None


def get_self_differance_node() -> SelfDifferanceNode:
    """Get the singleton SelfDifferanceNode."""
    global _self_differance_node
    if _self_differance_node is None:
        _self_differance_node = SelfDifferanceNode()
    return _self_differance_node


def set_self_differance_node(node: SelfDifferanceNode | None) -> None:
    """Set or clear the singleton SelfDifferanceNode."""
    global _self_differance_node
    _self_differance_node = node


def create_self_differance_node(
    time_differance_node: Any = None,
) -> SelfDifferanceNode:
    """
    Create a SelfDifferanceNode with optional integration.

    Args:
        time_differance_node: DifferanceMark for heritage queries

    Returns:
        Configured SelfDifferanceNode
    """
    node = SelfDifferanceNode()
    if time_differance_node:
        node.set_time_differance_node(time_differance_node)
    return node


__all__ = [
    # Affordances
    "SELF_DIFFERANCE_AFFORDANCES",
    # Nodes
    "SelfDifferanceNode",
    # Factories
    "get_self_differance_node",
    "set_self_differance_node",
    "create_self_differance_node",
]
