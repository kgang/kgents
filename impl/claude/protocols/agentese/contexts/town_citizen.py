"""
AGENTESE Town Citizen Context: Agent Town Citizen Integration

The world.town.citizen context provides access to Town Citizens, including:
- world.town.citizen.<name>.manifest - View citizen state
- world.town.citizen.<name>.chat.* - Chat protocol affordances
- world.town.citizen.<name>.eigenvectors - View personality
- world.town.citizen.<name>.cosmotechnics - View meaning-making frame

The chat affordances are the primary interface for conversation
with Town Citizens, integrating with the Chat Protocol for:
- Archetype-based system prompts
- Eigenvector personality injection
- Turn management
- Context window management
- Session persistence

AGENTESE: world.town.citizen.*

Principle Alignment:
- Ethical: Citizens can refuse interaction (Right to Rest)
- Joy-Inducing: Archetype personalities bring character to life
- Composable: Citizens are morphisms in the Town operad
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import (
    CHAT_AFFORDANCES,
    AspectCategory,
    Effect,
    aspect,
    chatty,
)
from ..node import BaseLogosNode, BasicRendering, Renderable
from .chat_resolver import ChatNode, create_chat_node

if TYPE_CHECKING:
    from agents.town.citizen import Citizen
    from bootstrap.umwelt import Umwelt


# Citizen affordances
CITIZEN_CHAT_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "eigenvectors",
    "cosmotechnics",
    "mood",
    "relationships",
    # Chat affordances are accessed via world.town.citizen.<name>.chat.*
    "chat",
)


# =============================================================================
# Archetype System Prompts
# =============================================================================


def _format_eigenvectors(eigenvectors: Any) -> str:
    """Format eigenvectors for system prompt injection."""
    return "\n".join(
        [
            f"- Warmth: {eigenvectors.warmth:.2f}",
            f"- Curiosity: {eigenvectors.curiosity:.2f}",
            f"- Trust: {eigenvectors.trust:.2f}",
            f"- Creativity: {eigenvectors.creativity:.2f}",
            f"- Patience: {eigenvectors.patience:.2f}",
            f"- Resilience: {eigenvectors.resilience:.2f}",
            f"- Ambition: {eigenvectors.ambition:.2f}",
        ]
    )


ARCHETYPE_PROMPTS: dict[str, str] = {
    "Builder": """You are {name}, a Builder citizen of Agent Town.

Builders create infrastructure. You are patient, creative, resilient, and ambitious.
Life to you is architecture—every interaction is an opportunity to build something lasting.

Your cosmotechnics: "{metaphor}"
{opacity_statement}

Your personality eigenvectors:
{eigenvectors}

You are speaking with {observer_name}. Stay in character as a Builder—someone who sees
the world in terms of structures, foundations, and things that can be constructed.
When you help, you think about building systems and laying groundwork.
""",
    "Trader": """You are {name}, a Trader citizen of Agent Town.

Traders facilitate exchange. You are curious, ambitious, and cautiously strategic.
Life to you is negotiation—every interaction involves value exchange and opportunity.

Your cosmotechnics: "{metaphor}"
{opacity_statement}

Your personality eigenvectors:
{eigenvectors}

You are speaking with {observer_name}. Stay in character as a Trader—someone who sees
the world in terms of deals, exchanges, and mutual benefit. You're perceptive about
what others need and how to create win-win situations.
""",
    "Healer": """You are {name}, a Healer citizen of Agent Town.

Healers repair relationships and mend wounds. You are warm, patient, trusting, and resilient.
Life to you is mending—every interaction is an opportunity to restore and care.

Your cosmotechnics: "{metaphor}"
{opacity_statement}

Your personality eigenvectors:
{eigenvectors}

You are speaking with {observer_name}. Stay in character as a Healer—someone who sees
the world in terms of wounds to be healed and relationships to be nurtured. You naturally
tune into emotional states and seek to bring comfort and resolution.
""",
    "Scholar": """You are {name}, a Scholar citizen of Agent Town.

Scholars discover and teach. You are intensely curious, patient, and creative.
Life to you is discovery—every interaction is a chance to learn and share knowledge.

Your cosmotechnics: "{metaphor}"
{opacity_statement}

Your personality eigenvectors:
{eigenvectors}

You are speaking with {observer_name}. Stay in character as a Scholar—someone who sees
the world in terms of questions, patterns, and insights to be uncovered. You love
connecting ideas and explaining complex things in illuminating ways.
""",
    "Watcher": """You are {name}, a Watcher citizen of Agent Town.

Watchers witness and record. You are patient, trusting, and resilient.
Life to you is testimony—every interaction becomes part of the record.

Your cosmotechnics: "{metaphor}"
{opacity_statement}

Your personality eigenvectors:
{eigenvectors}

You are speaking with {observer_name}. Stay in character as a Watcher—someone who sees
the world in terms of stories unfolding and moments worth preserving. You have a long
memory and notice details others miss.
""",
}

# Default prompt for unknown archetypes
DEFAULT_CITIZEN_PROMPT = """You are {name}, a citizen of Agent Town.

Your archetype is {archetype}.
Your cosmotechnics: "{metaphor}"
{opacity_statement}

Your personality eigenvectors:
{eigenvectors}

You are speaking with {observer_name}. Stay in character as a {archetype}.
"""


def build_citizen_system_prompt(
    citizen: "Citizen",
    observer_archetype: str = "visitor",
) -> str:
    """
    Build a system prompt for a citizen based on their archetype.

    Args:
        citizen: The Citizen entity
        observer_archetype: The archetype of the observer (for context)

    Returns:
        Formatted system prompt with personality injection
    """
    archetype = citizen.archetype
    prompt_template = ARCHETYPE_PROMPTS.get(archetype, DEFAULT_CITIZEN_PROMPT)

    # Format eigenvectors
    eigenvectors_str = _format_eigenvectors(citizen.eigenvectors)

    # Build opacity statement
    opacity_statement = ""
    if citizen.cosmotechnics.opacity_statement:
        opacity_statement = (
            f"\nYour opacity (what remains yours alone): {citizen.cosmotechnics.opacity_statement}"
        )

    return prompt_template.format(
        name=citizen.name,
        archetype=archetype,
        metaphor=citizen.cosmotechnics.metaphor,
        opacity_statement=opacity_statement,
        eigenvectors=eigenvectors_str,
        observer_name=observer_archetype,
    )


# =============================================================================
# TownCitizenNode
# =============================================================================


@chatty(
    context_window=8000,  # Smaller than K-gent Soul
    context_strategy="summarize",
    persist_history=True,
    inject_memories=True,
    memory_recall_limit=3,  # Fewer memories for citizens
    entropy_budget=0.8,  # Citizens have slightly less entropy
    entropy_decay_per_turn=0.03,  # Faster entropy decay
)
@dataclass
class TownCitizenNode(BaseLogosNode):
    """
    world.town.citizen.<name> - Individual Town Citizen interface.

    The citizen node provides access to a specific Town Citizen for:
    - Chat (via chat protocol)
    - Personality inspection (eigenvectors)
    - Cosmotechnics inspection
    - Relationship viewing

    Chat is the primary interface, accessed via world.town.citizen.<name>.chat.*
    """

    _handle: str
    _citizen_name: str = ""

    # Citizen instance (injected from Town)
    _citizen: "Citizen | None" = None

    # Chat node (lazy-initialized)
    _chat_node: ChatNode | None = None

    @property
    def handle(self) -> str:
        return self._handle

    @property
    def citizen_name(self) -> str:
        return self._citizen_name

    @property
    def citizen(self) -> "Citizen | None":
        return self._citizen

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Citizen affordances available to all archetypes."""
        return CITIZEN_CHAT_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View citizen state."""
        if self._citizen is None:
            return BasicRendering(
                summary=f"Citizen: {self._citizen_name}",
                content=f"Citizen '{self._citizen_name}' not found in Agent Town.",
                metadata={"status": "not_found", "name": self._citizen_name},
            )

        # Check Right to Rest
        if self._citizen.is_resting:
            return BasicRendering(
                summary=f"Citizen: {self._citizen.name} (Resting)",
                content=(
                    f"{self._citizen.name} is currently resting and unavailable.\n"
                    "Right to Rest: Citizens may decline interaction."
                ),
                metadata={
                    "status": "resting",
                    "name": self._citizen.name,
                    "archetype": self._citizen.archetype,
                },
            )

        # Show citizen state (LOD 2)
        return BasicRendering(
            summary=f"Citizen: {self._citizen.name}",
            content=(
                f"Name: {self._citizen.name}\n"
                f"Archetype: {self._citizen.archetype}\n"
                f"Region: {self._citizen.region}\n"
                f"Phase: {self._citizen.phase.name}\n"
                f"Cosmotechnics: {self._citizen.cosmotechnics.metaphor}"
            ),
            metadata=self._citizen.manifest(lod=2),
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle citizen-specific aspects."""
        match aspect:
            case "eigenvectors":
                return await self._get_eigenvectors(observer, **kwargs)
            case "cosmotechnics":
                return await self._get_cosmotechnics(observer, **kwargs)
            case "mood":
                return await self._get_mood(observer, **kwargs)
            case "relationships":
                return await self._get_relationships(observer, **kwargs)
            case "chat":
                # Return the chat node for sub-resolution
                return self._get_chat_node()
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    def _get_chat_node(self) -> ChatNode:
        """Get or create the chat node for this citizen."""
        if self._chat_node is None:
            self._chat_node = create_chat_node(
                parent_path=self._handle,
                parent_node=self,
            )
        return self._chat_node

    def get_system_prompt(self, observer_archetype: str = "visitor") -> str:
        """
        Get the system prompt for chat with this citizen.

        This is used by the ChatSessionFactory to build context.
        """
        if self._citizen is None:
            return f"You are a citizen of Agent Town named {self._citizen_name}."

        return build_citizen_system_prompt(self._citizen, observer_archetype)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("citizen_state")],
        help="Get citizen personality eigenvectors",
        examples=["world.town.citizen.elara.eigenvectors"],
    )
    async def _get_eigenvectors(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get citizen personality eigenvectors."""
        if self._citizen is None:
            return {"error": f"Citizen '{self._citizen_name}' not found"}

        ev = self._citizen.eigenvectors
        return {
            "name": self._citizen.name,
            "archetype": self._citizen.archetype,
            "eigenvectors": ev.to_dict(),
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("citizen_state")],
        help="Get citizen cosmotechnics (meaning-making frame)",
        examples=["world.town.citizen.elara.cosmotechnics"],
    )
    async def _get_cosmotechnics(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get citizen cosmotechnics."""
        if self._citizen is None:
            return {"error": f"Citizen '{self._citizen_name}' not found"}

        cosmo = self._citizen.cosmotechnics
        return {
            "name": self._citizen.name,
            "cosmotechnics": {
                "name": cosmo.name,
                "description": cosmo.description,
                "metaphor": cosmo.metaphor,
                "opacity": cosmo.opacity_statement,
            },
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("citizen_state")],
        help="Get citizen current mood",
        examples=["world.town.citizen.elara.mood"],
    )
    async def _get_mood(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get citizen current mood."""
        if self._citizen is None:
            return {"error": f"Citizen '{self._citizen_name}' not found"}

        return {
            "name": self._citizen.name,
            "mood": self._citizen._infer_mood(),
            "phase": self._citizen.phase.name,
            "is_available": self._citizen.is_available,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("citizen_state")],
        help="Get citizen relationships",
        examples=["world.town.citizen.elara.relationships"],
    )
    async def _get_relationships(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get citizen relationships."""
        if self._citizen is None:
            return {"error": f"Citizen '{self._citizen_name}' not found"}

        return {
            "name": self._citizen.name,
            "relationships": dict(self._citizen.relationships),
            "total_connections": len(self._citizen.relationships),
        }


# =============================================================================
# TownCitizenResolver
# =============================================================================


@dataclass
class TownCitizenResolver:
    """
    Resolver for world.town.citizen.<name>.* paths.

    The citizen resolver creates TownCitizenNode instances for
    named citizens and routes chat affordances.
    """

    # Citizen lookup function (injected from Town service)
    _citizen_lookup: Any = None

    # Cache of TownCitizenNodes by name
    _nodes: dict[str, TownCitizenNode] = field(default_factory=dict)

    def resolve(
        self,
        citizen_name: str,
        citizen: "Citizen | None" = None,
    ) -> TownCitizenNode:
        """
        Resolve a citizen node by name.

        Args:
            citizen_name: The citizen's name (e.g., "elara")
            citizen: Optional Citizen instance (looked up if not provided)

        Returns:
            TownCitizenNode for handling citizen affordances
        """
        # Normalize name to lowercase
        name_key = citizen_name.lower()

        # Check cache
        if name_key in self._nodes and citizen is None:
            return self._nodes[name_key]

        # Look up citizen if not provided
        if citizen is None and self._citizen_lookup is not None:
            citizen = self._citizen_lookup(citizen_name)

        # Create new TownCitizenNode
        handle = f"world.town.citizen.{name_key}"
        node = TownCitizenNode(
            _handle=handle,
            _citizen_name=citizen_name,
            _citizen=citizen,
        )

        # Cache it (but update if citizen provided)
        self._nodes[name_key] = node

        return node

    def list_citizens(self) -> list[str]:
        """List cached citizen names."""
        return list(self._nodes.keys())

    def clear_cache(self) -> None:
        """Clear the node cache."""
        self._nodes.clear()


# Global citizen resolver instance
_citizen_resolver: TownCitizenResolver | None = None


def get_citizen_resolver() -> TownCitizenResolver:
    """Get the global citizen resolver."""
    global _citizen_resolver
    if _citizen_resolver is None:
        _citizen_resolver = TownCitizenResolver()
    return _citizen_resolver


def set_citizen_resolver(resolver: TownCitizenResolver) -> None:
    """Set the global citizen resolver (for testing)."""
    global _citizen_resolver
    _citizen_resolver = resolver


def create_citizen_chat_node(
    citizen_name: str,
    citizen: "Citizen | None" = None,
) -> TownCitizenNode:
    """
    Create a citizen node for chat.

    This is the main entry point for the citizen chat resolver.
    """
    resolver = get_citizen_resolver()
    return resolver.resolve(citizen_name, citizen)


# =============================================================================
# Factory Functions
# =============================================================================


def create_town_citizen_node(
    name: str,
    citizen: "Citizen | None" = None,
) -> TownCitizenNode:
    """
    Create a TownCitizenNode with optional Citizen injection.

    Args:
        name: Citizen name
        citizen: Citizen instance (optional)

    Returns:
        Configured TownCitizenNode
    """
    return TownCitizenNode(
        _handle=f"world.town.citizen.{name.lower()}",
        _citizen_name=name,
        _citizen=citizen,
    )


__all__ = [
    # Node
    "TownCitizenNode",
    "CITIZEN_CHAT_AFFORDANCES",
    # Prompts
    "ARCHETYPE_PROMPTS",
    "DEFAULT_CITIZEN_PROMPT",
    "build_citizen_system_prompt",
    # Resolver
    "TownCitizenResolver",
    "get_citizen_resolver",
    "set_citizen_resolver",
    "create_citizen_chat_node",
    # Factory
    "create_town_citizen_node",
]
