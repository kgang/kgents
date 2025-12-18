"""
Flow AGENTESE Node: @node("self.flow")

The F-gent (Flow agent) unifies chat, research, and collaboration modalities
under a single polynomial state machine.

AGENTESE Paths:
- self.flow.manifest     - Flow service status
- self.flow.modalities   - List available modalities
- self.flow.chat.*       - Chat modality (delegates to self.chat)
- self.flow.research.*   - Research modality
- self.flow.collab.*     - Collaboration modality

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: docs/skills/metaphysical-fullstack.md
See: agents/f/polynomial.py for FlowPhase
See: agents/f/operad.py for FLOW_OPERAD
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === FlowNode Rendering ===


@dataclass(frozen=True)
class FlowManifestRendering:
    """Rendering for flow service status."""

    modalities: list[str]
    active_sessions: int
    default_modality: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "flow_manifest",
            "modalities": self.modalities,
            "active_sessions": self.active_sessions,
            "default_modality": self.default_modality,
        }

    def to_text(self) -> str:
        lines = [
            "Flow Service Status",
            "===================",
            f"Modalities: {', '.join(self.modalities)}",
            f"Active sessions: {self.active_sessions}",
            f"Default: {self.default_modality}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class ModalityRendering:
    """Rendering for modality information."""

    name: str
    description: str
    operations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "modality",
            "name": self.name,
            "description": self.description,
            "operations": self.operations,
        }

    def to_text(self) -> str:
        lines = [
            f"Modality: {self.name}",
            f"Description: {self.description}",
            f"Operations: {', '.join(self.operations)}",
        ]
        return "\n".join(lines)


# === FlowNode ===


@node(
    "self.flow",
    description="Flow agent - chat, research, and collaboration modalities",
)
class FlowNode(BaseLogosNode):
    """
    AGENTESE node for F-gent (Flow agent) Crown Jewel.

    Exposes the unified flow abstraction through the universal protocol.
    Chat operations delegate to self.chat, research and collaboration
    provide their own state machines.

    Example:
        # Via AGENTESE gateway
        GET /agentese/self/flow/manifest

        # Via Logos directly
        await logos.invoke("self.flow.manifest", observer)

        # Via CLI
        kgents flow manifest
    """

    def __init__(self) -> None:
        """Initialize FlowNode."""
        self._modalities = ["chat", "research", "collaboration"]
        self._default = "chat"

    @property
    def handle(self) -> str:
        return "self.flow"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        base = ("manifest", "modalities")
        if archetype in ("developer", "admin", "system"):
            return base + ("chat", "research", "collab", "configure")
        return base

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]") -> Renderable:
        """
        Manifest flow service status to observer.

        AGENTESE: self.flow.manifest
        """
        # TODO: Get actual session count from chat service
        return FlowManifestRendering(
            modalities=self._modalities,
            active_sessions=0,
            default_modality=self._default,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to appropriate handlers.

        Args:
            aspect: The aspect to invoke
            observer: The observer context
            **kwargs: Aspect-specific arguments
        """
        if aspect == "modalities":
            return {
                "modalities": [
                    {
                        "name": "chat",
                        "description": "Conversational flow with context management",
                        "operations": [
                            "start",
                            "stop",
                            "turn",
                            "summarize",
                            "inject_context",
                        ],
                    },
                    {
                        "name": "research",
                        "description": "Hypothesis exploration and synthesis",
                        "operations": [
                            "start",
                            "branch",
                            "merge",
                            "prune",
                            "evaluate",
                        ],
                    },
                    {
                        "name": "collaboration",
                        "description": "Multi-agent consensus building",
                        "operations": ["start", "post", "read", "vote", "moderate"],
                    },
                ]
            }

        elif aspect == "configure":
            new_default = kwargs.get("default_modality")
            if new_default and new_default in self._modalities:
                self._default = new_default
                return {"success": True, "default_modality": self._default}
            return {"error": f"Unknown modality: {new_default}"}

        elif aspect.startswith("chat."):
            # Delegate to self.chat
            return {
                "delegation": "self.chat",
                "aspect": aspect[5:],  # Remove "chat." prefix
                "message": "Use self.chat.* directly for chat operations",
            }

        elif aspect.startswith("research."):
            return {
                "message": "Research modality not yet implemented",
                "hint": "See agents/f/polynomial.py for RESEARCH_POLYNOMIAL",
            }

        elif aspect.startswith("collab."):
            return {
                "message": "Collaboration modality not yet implemented",
                "hint": "See agents/f/polynomial.py for COLLABORATION_POLYNOMIAL",
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}


# === Exports ===

__all__ = [
    "FlowNode",
    "FlowManifestRendering",
    "ModalityRendering",
]
