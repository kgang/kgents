"""
AGENTESE World Context Resolver

The External: entities, environments, tools, resources in flux.

world.* handles resolve to external entities that can be:
- Registered in L-gent (known entities)
- Generated from spec via J-gent JIT (generative)
- Created via define affordance (autopoiesis)

Principle Alignment: Heterarchical (resources in flux)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

from ..node import (
    BaseLogosNode,
    BasicRendering,
    BlueprintRendering,
    EconomicRendering,
    PoeticRendering,
    Renderable,
)
from ..renderings import (
    AdminRendering,
    DeveloperRendering,
    ScientificRendering,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Archetype-Specific Affordances ===

WORLD_ARCHETYPE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "architect": ("renovate", "measure", "blueprint", "demolish", "design"),
    "poet": ("describe", "metaphorize", "inhabit", "contemplate"),
    "economist": ("appraise", "forecast", "compare", "trade"),
    "inhabitant": ("enter", "exit", "furnish", "repair", "use"),
    "scientist": ("analyze", "measure", "experiment", "hypothesize"),
    "developer": ("build", "deploy", "debug", "test", "refactor"),
    "admin": ("configure", "monitor", "audit", "provision"),
    "default": (),
}


# === World Node ===


@dataclass
class WorldNode(BaseLogosNode):
    """
    A node in the world.* context.

    Represents an external entity that can be perceived differently
    by different observers (the Polymorphic Principle).

    Examples:
        world.house - A physical structure
        world.server - A compute resource
        world.document - A file or text
        world.project - A codebase
    """

    _handle: str
    name: str = ""
    description: str = ""
    entity_type: str = "generic"
    state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Integration points (protocols)
    _registry: Any = None  # L-gent registry for related entities
    _narrator: Any = None  # N-gent for history/witness

    def __post_init__(self) -> None:
        if not self.name:
            # Extract name from handle (e.g., "world.house" -> "house")
            self.name = self._handle.split(".")[-1] if "." in self._handle else self._handle

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances for world entities."""
        base_extra = ("define", "relate", "transform")
        archetype_extra = WORLD_ARCHETYPE_AFFORDANCES.get(archetype, ())
        return base_extra + archetype_extra

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Collapse to observer-appropriate representation.

        The projection IS the aesthetic (Principle #4: Joy-Inducing).
        Uses StandardRenderingFactory for polymorphic rendering.
        """
        meta = self._umwelt_to_meta(observer)

        match meta.archetype:
            case "architect":
                return BlueprintRendering(
                    dimensions=self.state.get("dimensions", {}),
                    materials=tuple(self.state.get("materials", [])),
                    structural_analysis=self._compute_structure(),
                )
            case "poet":
                return PoeticRendering(
                    description=self._generate_poetic_description(),
                    metaphors=tuple(self.state.get("metaphors", [])),
                    mood=self.state.get("mood", "contemplative"),
                )
            case "economist":
                return EconomicRendering(
                    market_value=self.state.get("value", 0.0),
                    comparable_sales=tuple(self.state.get("comparables", [])),
                    appreciation_forecast=self.state.get("forecast", {}),
                )
            case "scientist":
                return ScientificRendering(
                    entity=self.name,
                    measurements=self.state.get("measurements", {}),
                    observations=tuple(self.state.get("observations", [])),
                    hypotheses=tuple(self.state.get("hypotheses", [])),
                    confidence=self.state.get("confidence", 0.5),
                )
            case "developer":
                return DeveloperRendering(
                    entity=self.name,
                    language=self.state.get("language", ""),
                    dependencies=tuple(self.state.get("dependencies", [])),
                    structure=self.state.get("structure", {}),
                    build_status=self.state.get("build_status", "unknown"),
                    test_coverage=self.state.get("test_coverage", 0.0),
                    issues=tuple(self.state.get("issues", [])),
                )
            case "admin":
                return AdminRendering(
                    entity=self.name,
                    status=self.state.get("status", "unknown"),
                    health=self.state.get("health", 1.0),
                    metrics=self.state.get("metrics", {}),
                    config=self.state.get("config", {}),
                    alerts=tuple(self.state.get("alerts", [])),
                )
            case _:
                return BasicRendering(
                    summary=f"{self.entity_type.title()}: {self.name}",
                    content=self.description or f"A {self.entity_type} in the world.",
                    metadata={"entity_type": self.entity_type, **self.metadata},
                )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle domain-specific aspects for world entities."""
        match aspect:
            case "witness":
                return await self._get_history(observer)
            case "define":
                return await self._define_child(observer, **kwargs)
            case "relate":
                return await self._find_relations(observer, **kwargs)
            case "transform":
                return await self._transform(observer, **kwargs)
            case "describe" | "metaphorize" | "contemplate":
                return await self._poetic_aspect(aspect, observer, **kwargs)
            case "analyze" | "measure" | "experiment":
                return await self._scientific_aspect(aspect, observer, **kwargs)
            case "build" | "deploy" | "debug" | "test" | "refactor":
                return await self._developer_aspect(aspect, observer, **kwargs)
            case _:
                return await self._generic_aspect(aspect, observer, **kwargs)

    def _compute_structure(self) -> dict[str, Any]:
        """Compute structural analysis for architects."""
        return {
            "load_bearing": self.state.get("load_bearing", []),
            "stress_points": self.state.get("stress_points", []),
            "integrity": self.state.get("integrity", 1.0),
        }

    def _generate_poetic_description(self) -> str:
        """Generate poetic description of the entity."""
        base = self.description or f"A {self.entity_type}"
        return f"{base}—a presence in the world, waiting to be observed."

    async def _get_history(self, observer: "Umwelt[Any, Any]") -> dict[str, Any]:
        """Get temporal trace via N-gent if available."""
        if self._narrator:
            try:
                return cast(dict[str, Any], await self._narrator.get_trace(self.handle))
            except Exception:
                pass
        return {
            "handle": self.handle,
            "history": [],
            "note": "N-gent not connected—history unavailable",
        }

    async def _define_child(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> "WorldNode":
        """Create a child entity via autopoiesis."""
        name = kwargs.get("name", "unnamed")
        spec = kwargs.get("spec", "")
        entity_type = kwargs.get("entity_type", "generic")

        child_handle = f"{self.handle}.{name}"
        child = WorldNode(
            _handle=child_handle,
            name=name,
            description=spec,
            entity_type=entity_type,
        )

        # Register if registry available
        if self._registry:
            await self._registry.register(child_handle, child)

        return child

    async def _find_relations(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[str]:
        """Find related entities via L-gent if available."""
        if self._registry:
            try:
                prefix = self.handle.rsplit(".", 1)[0]
                return cast(list[str], self._registry.list_handles(prefix))
            except Exception:
                pass
        return []

    async def _transform(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Transform the entity's state."""
        changes = kwargs.get("changes", {})
        self.state.update(changes)
        return {"transformed": True, "changes": changes}

    async def _poetic_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> str:
        """Handle poetic aspects (describe, metaphorize, contemplate)."""
        match aspect:
            case "describe":
                return self._generate_poetic_description()
            case "metaphorize":
                context = kwargs.get("context", "existence")
                return f"{self.name} is like {context}—both present and becoming."
            case "contemplate":
                return f"In contemplating {self.name}, one finds... presence."
            case _:
                return f"The {aspect} of {self.name} eludes description."

    async def _scientific_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle scientific aspects (analyze, measure, experiment)."""
        match aspect:
            case "analyze":
                return {
                    "entity": self.name,
                    "type": self.entity_type,
                    "state_keys": list(self.state.keys()),
                    "metadata_keys": list(self.metadata.keys()),
                }
            case "measure":
                metric = kwargs.get("metric", "size")
                return {
                    "entity": self.name,
                    "metric": metric,
                    "value": self.state.get(metric, "unmeasured"),
                }
            case "experiment":
                hypothesis = kwargs.get("hypothesis", "")
                return {
                    "entity": self.name,
                    "hypothesis": hypothesis,
                    "result": "pending",
                    "note": "Full experimentation requires B-gent integration",
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _developer_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle developer aspects (build, deploy, debug, test, refactor)."""
        return {
            "entity": self.name,
            "aspect": aspect,
            "status": "acknowledged",
            "note": f"Full {aspect} capability requires integration with build system",
        }

    async def _generic_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Handle generic/unknown aspects."""
        return {
            "entity": self.name,
            "aspect": aspect,
            "kwargs": kwargs,
            "note": "Generic aspect handler—consider extending WorldNode",
        }


# === Purgatory Node ===


PURGATORY_AFFORDANCES: tuple[str, ...] = (
    "list",
    "resolve",
    "cancel",
    "inspect",
    "void_expired",
)


@dataclass
class PurgatoryNode(BaseLogosNode):
    """
    world.purgatory - Global semaphore management.

    Provides admin-level access to the Purgatory:
    - list: List all pending semaphores
    - resolve: Resolve a pending semaphore with human input
    - cancel: Cancel a pending semaphore
    - inspect: Get detailed info about a semaphore
    - void_expired: Void all expired semaphores

    Access Control:
    The PurgatoryNode is intended for admin/human use, not agent use.
    Agents should use self.semaphore.* for their own semaphores.

    AGENTESE: world.purgatory.*
    """

    _handle: str = "world.purgatory"

    # Integration points
    _purgatory: Any = None  # Purgatory instance for token storage

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Purgatory affordances - admin only."""
        # Admin/developer archetypes get full access
        if archetype in ("admin", "developer", "architect"):
            return PURGATORY_AFFORDANCES
        # Other archetypes get read-only access
        return ("list", "inspect")

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """View purgatory status."""
        pending = await self._get_pending_list(observer)
        return BasicRendering(
            summary="Purgatory Status",
            content=f"Pending semaphores: {len(pending)}",
            metadata={
                "pending_count": len(pending),
                "semaphore_ids": [t.get("id") for t in pending],
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle purgatory-specific aspects."""
        match aspect:
            case "list":
                return await self._get_pending_list(observer, **kwargs)
            case "resolve":
                return await self._resolve_token(observer, **kwargs)
            case "cancel":
                return await self._cancel_token(observer, **kwargs)
            case "inspect":
                return await self._inspect_token(observer, **kwargs)
            case "void_expired":
                return await self._void_expired(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _get_pending_list(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        List all pending semaphores.

        Returns list of token summaries for admin review.
        """
        if self._purgatory is None:
            return []

        try:
            tokens = self._purgatory.list_pending()
            return [
                {
                    "id": t.id,
                    "reason": t.reason.value if hasattr(t.reason, "value") else str(t.reason),
                    "prompt": t.prompt,
                    "options": t.options,
                    "severity": t.severity,
                    "deadline": t.deadline.isoformat() if t.deadline else None,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "escalation": t.escalation,
                }
                for t in tokens
            ]
        except Exception:
            return []

    async def _resolve_token(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Resolve a pending semaphore with human input.

        Args:
            token_id: The semaphore token ID
            human_input: The human's response/decision

        Returns:
            Dict with status and reentry context info
        """
        token_id = kwargs.get("token_id")
        human_input = kwargs.get("human_input")

        if not token_id:
            return {"error": "token_id required"}
        if human_input is None:
            return {"error": "human_input required"}

        if self._purgatory is None:
            return {"error": "Purgatory not configured"}

        try:
            reentry = await self._purgatory.resolve(token_id, human_input)
            if reentry is None:
                return {
                    "error": "Token not found or not pending",
                    "token_id": token_id,
                }
            return {
                "status": "resolved",
                "token_id": token_id,
                "has_reentry": True,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _cancel_token(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Cancel a pending semaphore.

        Args:
            token_id: The semaphore token ID

        Returns:
            Dict with status
        """
        token_id = kwargs.get("token_id")

        if not token_id:
            return {"error": "token_id required"}

        if self._purgatory is None:
            return {"error": "Purgatory not configured"}

        try:
            success = await self._purgatory.cancel(token_id)
            if success:
                return {"status": "cancelled", "token_id": token_id}
            return {
                "error": "Token not found or not pending",
                "token_id": token_id,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _inspect_token(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Get detailed info about a semaphore.

        Args:
            token_id: The semaphore token ID

        Returns:
            Detailed token info
        """
        token_id = kwargs.get("token_id")

        if not token_id:
            return {"error": "token_id required"}

        if self._purgatory is None:
            return {"error": "Purgatory not configured"}

        try:
            token = self._purgatory.get(token_id)
            if token is None:
                return {"error": "Token not found", "token_id": token_id}

            return {
                "token_id": token.id,
                "status": (
                    "resolved"
                    if token.is_resolved
                    else "cancelled"
                    if token.is_cancelled
                    else "voided"
                    if token.is_voided
                    else "pending"
                ),
                "reason": token.reason.value
                if hasattr(token.reason, "value")
                else str(token.reason),
                "prompt": token.prompt,
                "options": token.options,
                "severity": token.severity,
                "deadline": token.deadline.isoformat() if token.deadline else None,
                "escalation": token.escalation,
                "created_at": token.created_at.isoformat() if token.created_at else None,
                "resolved_at": token.resolved_at.isoformat() if token.resolved_at else None,
                "cancelled_at": token.cancelled_at.isoformat() if token.cancelled_at else None,
                "voided_at": token.voided_at.isoformat() if token.voided_at else None,
            }
        except Exception as e:
            return {"error": str(e)}

    async def _void_expired(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Void all expired semaphores.

        Returns:
            Dict with count of voided tokens
        """
        if self._purgatory is None:
            return {"error": "Purgatory not configured"}

        try:
            voided = await self._purgatory.void_expired()
            return {
                "status": "completed",
                "voided_count": len(voided),
                "voided_ids": [t.id for t in voided],
            }
        except Exception as e:
            return {"error": str(e)}


# === World Context Resolver ===


@dataclass
class WorldContextResolver:
    """
    Resolver for world.* context.

    Resolution strategy:
    1. Check for special nodes (purgatory)
    2. Check registry (known entities)
    3. Check spec/ for JIT generation
    4. Create placeholder node (for exploration)
    """

    registry: Any = None  # L-gent registry
    narrator: Any = None  # N-gent for traces
    purgatory: Any = None  # Purgatory for semaphores

    # Cache of resolved nodes
    _cache: dict[str, BaseLogosNode] = field(default_factory=dict)

    # Singleton nodes for special world entities
    _purgatory_node: PurgatoryNode | None = None

    def __post_init__(self) -> None:
        """Initialize singleton nodes."""
        self._purgatory_node = PurgatoryNode(_purgatory=self.purgatory)

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a world.* path to a node.

        Args:
            holon: The entity name (e.g., "house" from "world.house")
            rest: Additional path components

        Returns:
            Resolved node (WorldNode or PurgatoryNode)
        """
        handle = f"world.{holon}"

        # Check cache
        if handle in self._cache:
            return self._cache[handle]

        # Special case: world.purgatory
        if holon == "purgatory":
            node = self._purgatory_node or PurgatoryNode()
            self._cache[handle] = node
            return node

        # Check registry if available
        if self.registry:
            try:
                entry = self.registry.get(handle)
                if entry:
                    world_node = self._hydrate_from_registry(entry, handle)
                    self._cache[handle] = world_node
                    return world_node
            except Exception:
                pass

        # Create placeholder node for exploration
        world_node = WorldNode(
            _handle=handle,
            name=holon,
            entity_type="world_entity",
            _registry=self.registry,
            _narrator=self.narrator,
        )
        self._cache[handle] = world_node
        return world_node

    def _hydrate_from_registry(self, entry: Any, handle: str) -> WorldNode:
        """Hydrate a WorldNode from a registry entry."""
        return WorldNode(
            _handle=handle,
            name=getattr(entry, "name", handle.split(".")[-1]),
            description=getattr(entry, "description", ""),
            entity_type=getattr(entry, "entity_type", "world_entity"),
            state=getattr(entry, "state", {}),
            metadata=getattr(entry, "metadata", {}),
            _registry=self.registry,
            _narrator=self.narrator,
        )

    def register(self, handle: str, node: WorldNode) -> None:
        """Register a node in the cache."""
        self._cache[handle] = node

    def list_handles(self, prefix: str = "world.") -> list[str]:
        """List cached handles."""
        return [h for h in self._cache if h.startswith(prefix)]


# === Factory Functions ===


def create_world_resolver(
    registry: Any = None,
    narrator: Any = None,
    purgatory: Any = None,
) -> WorldContextResolver:
    """Create a WorldContextResolver with optional integrations."""
    resolver = WorldContextResolver(registry=registry, narrator=narrator, purgatory=purgatory)
    resolver.__post_init__()  # Initialize singleton nodes
    return resolver


def create_world_node(
    name: str,
    description: str = "",
    entity_type: str = "generic",
    state: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> WorldNode:
    """Create a WorldNode with standard configuration."""
    return WorldNode(
        _handle=f"world.{name}",
        name=name,
        description=description,
        entity_type=entity_type,
        state=state or {},
        metadata=metadata or {},
    )


__all__ = [
    # Constants
    "WORLD_ARCHETYPE_AFFORDANCES",
    "PURGATORY_AFFORDANCES",
    # Nodes
    "WorldNode",
    "PurgatoryNode",
    # Resolver
    "WorldContextResolver",
    # Factories
    "create_world_resolver",
    "create_world_node",
]
