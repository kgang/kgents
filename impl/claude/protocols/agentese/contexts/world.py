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
            self.name = (
                self._handle.split(".")[-1] if "." in self._handle else self._handle
            )

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances for world entities."""
        base_extra = ("define", "relate", "transform")
        archetype_extra = WORLD_ARCHETYPE_AFFORDANCES.get(archetype, ())
        return base_extra + archetype_extra

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
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


# === World Context Resolver ===


@dataclass
class WorldContextResolver:
    """
    Resolver for world.* context.

    Resolution strategy:
    1. Check registry (known entities)
    2. Check spec/ for JIT generation
    3. Create placeholder node (for exploration)
    """

    registry: Any = None  # L-gent registry
    narrator: Any = None  # N-gent for traces

    # Cache of resolved nodes
    _cache: dict[str, WorldNode] = field(default_factory=dict)

    def resolve(self, holon: str, rest: list[str]) -> WorldNode:
        """
        Resolve a world.* path to a WorldNode.

        Args:
            holon: The entity name (e.g., "house" from "world.house")
            rest: Additional path components

        Returns:
            Resolved WorldNode
        """
        handle = f"world.{holon}"

        # Check cache
        if handle in self._cache:
            return self._cache[handle]

        # Check registry if available
        if self.registry:
            try:
                entry = self.registry.get(handle)
                if entry:
                    node = self._hydrate_from_registry(entry, handle)
                    self._cache[handle] = node
                    return node
            except Exception:
                pass

        # Create placeholder node for exploration
        node = WorldNode(
            _handle=handle,
            name=holon,
            entity_type="world_entity",
            _registry=self.registry,
            _narrator=self.narrator,
        )
        self._cache[handle] = node
        return node

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
) -> WorldContextResolver:
    """Create a WorldContextResolver with optional integrations."""
    return WorldContextResolver(registry=registry, narrator=narrator)


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
