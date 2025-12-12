"""
AGENTESE Agent Discovery Context

The world.agent.* namespace for discovering and invoking agents.

This is a critical integration point that makes the kgents ecosystem
discoverable via AGENTESE paths:

    world.agent.list           → List all available agents
    world.agent.egent.manifest → Perceive E-gent capabilities
    world.agent.bgent.invoke   → Invoke B-gent
    world.agent.compose        → Compose multiple agents

Principle Alignment: Heterarchical (agents exist in flux, not hierarchy)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..exceptions import PathNotFoundError
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..renderings import AdminRendering, DeveloperRendering

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Agent Registry ===

# Known agent genuses and their metadata
AGENT_REGISTRY: dict[str, dict[str, Any]] = {
    "a": {
        "name": "A-gent",
        "theme": "Abstract architectures + Art/Creativity coaches",
        "status": "active",
        "description": "Handles abstract agent patterns and creative coaching",
    },
    "b": {
        "name": "B-gent",
        "theme": "Bio/Scientific discovery + Economics",
        "status": "active",
        "description": "Economics and scientific hypothesis management (Bank, Gas, Markets)",
    },
    "c": {
        "name": "C-gent",
        "theme": "Category Theory basis (composability)",
        "status": "active",
        "description": "Ensures category laws, composition, and morphism patterns",
    },
    "d": {
        "name": "D-gent",
        "theme": "Data Agents (state, memory, persistence)",
        "status": "active",
        "description": "Data persistence, memory, and state management",
    },
    "e": {
        "name": "E-gent",
        "theme": "Evolution (teleological thermodynamics)",
        "status": "active",
        "description": "Code evolution via mutations, phages, and thermodynamic selection",
        "tests": 353,
    },
    "f": {
        "name": "F-gent",
        "theme": "Forge (persistence layer)",
        "status": "active",
        "description": "Persistent storage and serialization",
    },
    "g": {
        "name": "G-gent",
        "theme": "Grammar (Grammarian)",
        "status": "active",
        "description": "Grammar validation, BNF generation, and syntactic constraints",
    },
    "h": {
        "name": "H-gent",
        "theme": "Hypothesis",
        "status": "active",
        "description": "Hypothesis generation and testing",
    },
    "i": {
        "name": "I-gent",
        "theme": "Introspection",
        "status": "active",
        "description": "Agent introspection and reflection",
    },
    "j": {
        "name": "J-gent",
        "theme": "JIT (Just-In-Time compilation)",
        "status": "active",
        "description": "MetaArchitect - generates code from specs",
    },
    "k": {
        "name": "K-gent",
        "theme": "Kent simulacra (interactive persona)",
        "status": "active",
        "description": "Personalization functor - navigates personality space",
    },
    "l": {
        "name": "L-gent",
        "theme": "Lattice/Library (semantic registry)",
        "status": "active",
        "description": "Semantic catalog, embeddings, and type lattice",
    },
    "m": {
        "name": "M-gent",
        "theme": "Memory/Map (holographic cartography)",
        "status": "active",
        "description": "HoloMap, pathfinding, context injection",
        "tests": 114,
    },
    "n": {
        "name": "N-gent",
        "theme": "Narrative (witness/trace)",
        "status": "active",
        "description": "Chronicles, traces, and narrative memory",
    },
    "o": {
        "name": "O-gent",
        "theme": "Observation (Panopticon)",
        "status": "active",
        "description": "Telemetry, observation, and monitoring",
    },
    "p": {
        "name": "P-gent",
        "theme": "Parser",
        "status": "active",
        "description": "Parsing and structural analysis",
    },
    "psi": {
        "name": "Ψ-gent",
        "theme": "Psychopomp (metaphor engine)",
        "status": "active",
        "description": "Metaphor-based problem solving and translation",
        "tests": 104,
    },
    "r": {
        "name": "R-gent",
        "theme": "Reflection",
        "status": "active",
        "description": "Self-reflection and meta-cognition",
    },
    "t": {
        "name": "T-gent",
        "theme": "Testing/Torture (Saboteurs)",
        "status": "active",
        "description": "Test generation and adversarial probing",
    },
    "q": {
        "name": "Q-gent",
        "theme": "Quartermaster (K8s disposable execution)",
        "status": "active",
        "description": "Disposable container execution via Kubernetes",
    },
    "u": {
        "name": "U-gent",
        "theme": "Utility (tool use, MCP integration)",
        "status": "active",
        "description": "Tool orchestration, MCP client, and utility execution",
    },
    "w": {
        "name": "W-gent",
        "theme": "Witness",
        "status": "active",
        "description": "Witnessing and verification",
    },
    "flux": {
        "name": "Flux",
        "theme": "Stream Transformer (Agent[A,B] → Agent[Flux[A], Flux[B]])",
        "status": "active",
        "description": "Event-driven stream processing, living pipelines, perturbation principle",
        "tests": 282,
    },
}


# === Agent Node ===


@dataclass
class AgentNode(BaseLogosNode):
    """
    A node representing an agent in the world.agent.* context.

    Provides AGENTESE access to agent metadata and capabilities:
    - manifest: View agent capabilities (polymorphic per observer)
    - witness: View agent history/usage
    - invoke: Invoke the agent
    - affordances: List what you can do with this agent
    """

    _handle: str
    agent_letter: str
    agent_info: dict[str, Any] = field(default_factory=dict)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances for agents."""
        base = ()  # Core affordances from BaseLogosNode
        match archetype:
            case "developer":
                return base + ("invoke", "compose", "debug", "test", "trace")
            case "admin":
                return base + ("invoke", "status", "metrics", "restart")
            case "architect":
                return base + ("invoke", "compose", "design", "refactor")
            case "scientist":
                return base + ("invoke", "experiment", "analyze")
            case _:
                return base + ("invoke",)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Manifest agent information based on observer's archetype.
        """
        meta = self._umwelt_to_meta(observer)
        info = self.agent_info

        match meta.archetype:
            case "developer":
                return DeveloperRendering(
                    entity=info.get("name", self.agent_letter),
                    language="python",
                    dependencies=(),
                    structure={
                        "location": f"impl/claude/agents/{self.agent_letter}/",
                        "theme": info.get("theme", ""),
                    },
                    build_status="active"
                    if info.get("status") == "active"
                    else "unknown",
                    test_coverage=0.0,
                    issues=(),
                )
            case "admin":
                return AdminRendering(
                    entity=info.get("name", self.agent_letter),
                    status=info.get("status", "unknown"),
                    health=1.0 if info.get("status") == "active" else 0.5,
                    metrics={"tests": info.get("tests", 0)},
                    config={},
                    alerts=(),
                )
            case _:
                return BasicRendering(
                    summary=f"{info.get('name', self.agent_letter)}: {info.get('theme', '')}",
                    content=info.get(
                        "description", "An agent in the kgents ecosystem."
                    ),
                    metadata={
                        "letter": self.agent_letter,
                        "status": info.get("status", "unknown"),
                    },
                )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle agent-specific aspects."""
        match aspect:
            case "invoke":
                return await self._invoke_agent(observer, **kwargs)
            case "compose":
                return await self._compose_with(observer, **kwargs)
            case "status":
                return self._get_status()
            case "metrics":
                return self._get_metrics()
            case "trace":
                return {"agent": self.agent_letter, "traces": []}
            case _:
                return {
                    "agent": self.agent_letter,
                    "aspect": aspect,
                    "note": f"Aspect '{aspect}' not fully implemented for agents",
                }

    async def _invoke_agent(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Invoke the underlying agent.

        This is a placeholder - actual invocation requires
        importing and instantiating the agent.
        """
        input_data = kwargs.get("input", {})
        return {
            "agent": self.agent_letter,
            "name": self.agent_info.get("name", ""),
            "status": "invocation_placeholder",
            "input": input_data,
            "note": (
                f"Full invocation requires direct import from agents.{self.agent_letter}. "
                "Use this path for discovery; use Python imports for execution."
            ),
        }

    async def _compose_with(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compose this agent with others."""
        others = kwargs.get("with", [])
        return {
            "composition": [self.agent_letter] + others,
            "note": "Composition via >> operator recommended",
            "example": f"agents.{self.agent_letter}.SomeAgent >> agents.{others[0] if others else 'X'}.OtherAgent",
        }

    def _get_status(self) -> dict[str, Any]:
        """Get agent status."""
        return {
            "agent": self.agent_letter,
            "name": self.agent_info.get("name", ""),
            "status": self.agent_info.get("status", "unknown"),
            "theme": self.agent_info.get("theme", ""),
        }

    def _get_metrics(self) -> dict[str, Any]:
        """Get agent metrics."""
        return {
            "agent": self.agent_letter,
            "tests": self.agent_info.get("tests", 0),
            "status": self.agent_info.get("status", "unknown"),
        }


# === Agent List Node ===


@dataclass
class AgentListNode(BaseLogosNode):
    """
    A node for world.agent.list - lists all available agents.
    """

    _handle: str = "world.agent"
    _registry: dict[str, dict[str, Any]] = field(default_factory=lambda: AGENT_REGISTRY)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return affordances for the agent list."""
        base = ()
        match archetype:
            case "developer" | "admin" | "architect":
                return base + ("list", "search", "compose")
            case _:
                return base + ("list",)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Manifest the list of all agents."""
        agents = []
        for letter, info in sorted(self._registry.items()):
            agents.append(f"• {info['name']} ({letter}): {info['theme']}")

        return BasicRendering(
            summary=f"kgents Agent Ecosystem ({len(self._registry)} agents)",
            content="\n".join(agents),
            metadata={
                "count": len(self._registry),
                "letters": list(self._registry.keys()),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle list-specific aspects."""
        match aspect:
            case "list":
                return self._list_agents(**kwargs)
            case "search":
                return self._search_agents(**kwargs)
            case "compose":
                return self._compose_agents(**kwargs)
            case _:
                return {"aspect": aspect, "agents": list(self._registry.keys())}

    def _list_agents(self, **kwargs: Any) -> list[dict[str, Any]]:
        """List all agents with their metadata."""
        status_filter = kwargs.get("status", None)
        agents = []
        for letter, info in sorted(self._registry.items()):
            if status_filter and info.get("status") != status_filter:
                continue
            agents.append(
                {
                    "letter": letter,
                    "name": info["name"],
                    "theme": info["theme"],
                    "status": info.get("status", "unknown"),
                    "handle": f"world.agent.{letter}",
                }
            )
        return agents

    def _search_agents(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Search agents by query."""
        query = kwargs.get("query", "").lower()
        results = []
        for letter, info in self._registry.items():
            searchable = (
                f"{info['name']} {info['theme']} {info.get('description', '')}".lower()
            )
            if query in searchable:
                results.append(
                    {
                        "letter": letter,
                        "name": info["name"],
                        "theme": info["theme"],
                        "handle": f"world.agent.{letter}",
                    }
                )
        return results

    def _compose_agents(self, **kwargs: Any) -> dict[str, Any]:
        """Return composition guidance for multiple agents."""
        agents = kwargs.get("agents", [])
        return {
            "agents": agents,
            "composition_pattern": " >> ".join(agents) if agents else "A >> B >> C",
            "note": "Use the >> operator to compose agents in pipelines",
        }


# === Agent Context Resolver ===


@dataclass
class AgentContextResolver:
    """
    Resolver for world.agent.* paths.

    Resolution strategy:
    1. world.agent → AgentListNode (for listing/searching)
    2. world.agent.{letter} → AgentNode (for specific agent)
    3. world.agent.{letter}.{aspect} → Invoke aspect

    Examples:
        world.agent.manifest        → List all agents
        world.agent.list            → List all agents
        world.agent.egent.manifest  → E-gent capabilities
        world.agent.bgent.invoke    → Invoke B-gent
    """

    _cache: dict[str, BaseLogosNode] = field(default_factory=dict)
    _registry: dict[str, dict[str, Any]] = field(default_factory=lambda: AGENT_REGISTRY)

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve world.agent.* paths.

        Args:
            holon: Either "agent" or the agent letter
            rest: Remaining path components

        Returns:
            AgentListNode for "agent" or AgentNode for specific agents
        """
        # If holon is "agent" and no rest, return the list node
        if holon == "agent" and not rest:
            if "world.agent" not in self._cache:
                self._cache["world.agent"] = AgentListNode(_registry=self._registry)
            return self._cache["world.agent"]

        # If holon is "agent" and rest has an agent letter
        if holon == "agent" and rest:
            agent_letter = rest[0]
            return self._resolve_agent(agent_letter)

        # Shouldn't reach here via normal resolution
        raise PathNotFoundError(
            "Invalid world.agent path. "
            "Try: world.agent.manifest or world.agent.{letter}.manifest"
        )

    def _resolve_agent(self, letter: str) -> AgentNode:
        """Resolve a specific agent by letter."""
        handle = f"world.agent.{letter}"

        if handle in self._cache:
            return self._cache[handle]  # type: ignore

        # Check if this is a known agent
        # Normalize: "egent" → "e", "bgent" → "b", etc.
        normalized = letter
        if letter.endswith("gent") and len(letter) > 4:
            normalized = letter[:-4]  # Remove "gent" suffix
        if normalized == "psi" or letter == "psigent" or letter == "ψ":
            normalized = "psi"

        if normalized not in self._registry:
            raise PathNotFoundError(
                f"Agent '{letter}' not found. "
                f"Available agents: {', '.join(sorted(self._registry.keys()))}. "
                f"Try: world.agent.manifest to list all agents."
            )

        info = self._registry[normalized]
        node = AgentNode(
            _handle=handle,
            agent_letter=normalized,
            agent_info=info,
        )
        self._cache[handle] = node
        return node

    def list_agents(self) -> list[str]:
        """List all available agent letters."""
        return sorted(self._registry.keys())


# === Factory Functions ===


def create_agent_resolver(
    registry: dict[str, dict[str, Any]] | None = None,
) -> AgentContextResolver:
    """Create an AgentContextResolver with optional custom registry."""
    return AgentContextResolver(_registry=registry or AGENT_REGISTRY)


def create_agent_node(letter: str) -> AgentNode:
    """Create an AgentNode for a specific agent letter."""
    info = AGENT_REGISTRY.get(letter, {"name": letter, "theme": "unknown"})
    return AgentNode(
        _handle=f"world.agent.{letter}",
        agent_letter=letter,
        agent_info=info,
    )
