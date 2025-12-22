# mypy: ignore-errors
"""
AGENTESE Self Context Resolver

The Internal: memory, capability, state, agent boundaries.

self.* handles resolve to internal agent state and capabilities:
- self.memory - Agent's memory and recall
- self.capabilities - What the agent can do
- self.state - Current operational state
- self.identity - Agent's identity and DNA

Principle Alignment: Ethical (boundaries of agency)

Note: Named self_.py because 'self' is a Python reserved word.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# Import from submodules
from .self_bus import (
    BUS_AFFORDANCES,
    BusNode,
    create_bus_resolver,
)

# Data architecture rewrite (Phase 2)
from .self_data import (
    DATA_AFFORDANCES,
    DataNode,
    create_data_resolver,
)

# F-gent Flow integration (Phase 7)
from .self_flow import (
    FLOW_AFFORDANCES,
    ChatFlowNode,
    CollaborationFlowNode,
    FlowNode,
    ResearchFlowNode,
    create_flow_resolver,
)
from .self_grow import SelfGrowResolver, create_self_grow_resolver
from .self_judgment import CriticsLoop, Critique, RefinedArtifact
from .self_memory import (
    MEMORY_AFFORDANCES,
    MemoryCartographyNode,
    MemoryGhostNode,
    MemoryNode,
)
from .self_semaphore import SemaphoreNode

# Soul integration (Chat Protocol - Phase 2)
from .self_soul import (
    SOUL_AFFORDANCES,
    SOUL_CHAT_AFFORDANCES,
    SoulNode,
    create_soul_node,
)

# Autopoietic kernel interface (AD-009)
from .self_system import (
    SYSTEM_AFFORDANCES,
    SystemNode,
    create_system_node,
    get_system_node,
)

# V-gent Vector integration (Phase 7)
from .self_vector import (
    VECTOR_AFFORDANCES,
    VectorNode,
)
from .vitals import VitalsContextResolver, create_vitals_resolver

# Re-export for backwards compatibility
__all__ = [
    # Nodes
    "MemoryNode",
    "MemoryGhostNode",
    "MemoryCartographyNode",
    "CapabilitiesNode",
    "StateNode",
    "IdentityNode",
    "JudgmentNode",
    "SemaphoreNode",
    "DashboardNode",
    "GenericSelfNode",
    # Data architecture rewrite (Phase 2)
    "DataNode",
    "BusNode",
    "DATA_AFFORDANCES",
    "BUS_AFFORDANCES",
    "create_data_resolver",
    "create_bus_resolver",
    # F-gent Flow integration (Phase 7)
    "FlowNode",
    "ChatFlowNode",
    "ResearchFlowNode",
    "CollaborationFlowNode",
    "FLOW_AFFORDANCES",
    "create_flow_resolver",
    # V-gent Vector integration (Phase 7)
    "VectorNode",
    "VECTOR_AFFORDANCES",
    # Soul integration (Chat Protocol - Phase 2)
    "SoulNode",
    "SOUL_AFFORDANCES",
    "SOUL_CHAT_AFFORDANCES",
    "create_soul_node",
    # System (Autopoietic kernel - AD-009)
    "SystemNode",
    "SYSTEM_AFFORDANCES",
    "get_system_node",
    "create_system_node",
    # Resolver
    "SelfContextResolver",
    # Factory
    "create_self_resolver",
    # Judgment types
    "CriticsLoop",
    "Critique",
    "RefinedArtifact",
]


# === Self Affordances ===

SELF_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "memory": MEMORY_AFFORDANCES,
    "capabilities": ("list", "acquire", "release"),
    "state": ("checkpoint", "restore", "inspect"),
    "identity": ("reflect", "evolve"),
    "judgment": (
        "taste",
        "surprise",
        "expectations",
        "calibrate",
        "critique",
        "refine",
    ),
    "semaphore": ("pending", "yield", "status"),
    "vitals": ("triad", "synapse", "resonance", "circuit", "durability", "reflex"),
    "grow": (
        "recognize",
        "propose",
        "validate",
        "germinate",
        "nursery",
        "promote",
        "rollback",
        "prune",
        "budget",
    ),
    # Data architecture rewrite (Phase 2)
    "data": DATA_AFFORDANCES,
    "bus": BUS_AFFORDANCES,
    # F-gent Flow integration (Phase 7)
    "flow": FLOW_AFFORDANCES,
    # V-gent Vector integration (Phase 7)
    "vector": VECTOR_AFFORDANCES,
    # Soul integration (Chat Protocol - Phase 2)
    "soul": SOUL_CHAT_AFFORDANCES,
    # Autopoietic kernel (AD-009)
    "system": SYSTEM_AFFORDANCES,
}


# === Capabilities Node ===


@dataclass
class CapabilitiesNode(BaseLogosNode):
    """
    self.capabilities - What the agent can do.

    Provides introspection into agent capabilities.
    """

    _handle: str = "self.capabilities"
    _capabilities: set[str] = field(default_factory=set)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Capability introspection affordances."""
        return SELF_AFFORDANCES["capabilities"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """List current capabilities."""
        meta = self._umwelt_to_meta(observer)
        return BasicRendering(
            summary=f"Capabilities of {meta.name}",
            content="\n".join(sorted(self._capabilities))
            if self._capabilities
            else "No capabilities registered",
            metadata={
                "archetype": meta.archetype,
                "capability_count": len(self._capabilities),
                "capabilities": sorted(self._capabilities),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle capability aspects."""
        match aspect:
            case "list":
                return sorted(self._capabilities)
            case "acquire":
                capability = kwargs.get("capability")
                if capability:
                    self._capabilities.add(capability)
                    return {"acquired": capability, "total": len(self._capabilities)}
                return {"error": "capability required"}
            case "release":
                capability = kwargs.get("capability")
                if capability and capability in self._capabilities:
                    self._capabilities.discard(capability)
                    return {"released": capability, "total": len(self._capabilities)}
                return {"error": "capability not found"}
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === State Node ===


@dataclass
class StateNode(BaseLogosNode):
    """
    self.state - Current operational state.

    Provides state inspection and management.
    """

    _handle: str = "self.state"
    _state: dict[str, Any] = field(default_factory=dict)
    _snapshots: list[dict[str, Any]] = field(default_factory=list)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """State management affordances."""
        return SELF_AFFORDANCES["state"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Inspect current state."""
        return BasicRendering(
            summary="Agent State",
            content=f"State keys: {list(self._state.keys())}",
            metadata={
                "state": self._state,
                "snapshot_count": len(self._snapshots),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle state aspects."""
        match aspect:
            case "checkpoint":
                snapshot = {
                    "timestamp": datetime.now().isoformat(),
                    "state": dict(self._state),
                    "label": kwargs.get("label", f"snapshot_{len(self._snapshots)}"),
                }
                self._snapshots.append(snapshot)
                return snapshot
            case "restore":
                index = kwargs.get("index", -1)
                if self._snapshots:
                    snapshot = self._snapshots[index]
                    self._state = dict(snapshot["state"])
                    return {"restored": snapshot["label"]}
                return {"error": "no snapshots available"}
            case "inspect":
                key = kwargs.get("key")
                if key:
                    return self._state.get(key, {"not_found": key})
                return dict(self._state)
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Judgment Node ===


@dataclass
class JudgmentNode(BaseLogosNode):
    """
    self.judgment - Aesthetic judgment and taste.

    Provides access to the Wundt Curator for aesthetic filtering:
    - taste: Evaluate aesthetic quality (returns TasteScore)
    - surprise: Measure Bayesian surprise
    - expectations: View/set prior expectations
    - calibrate: Learn optimal thresholds from feedback
    - critique: SPECS-based evaluation (novelty, utility, surprise)
    - refine: Iterative refinement loop with critique feedback

    AGENTESE: self.judgment.*

    Principle Alignment:
    - Tasteful: Architectural quality filtering
    - Joy-Inducing: Interesting > Boring or Chaotic
    """

    _handle: str = "self.judgment"

    # Wundt Curator configuration
    _low_threshold: float = 0.1
    _high_threshold: float = 0.9
    _expectations: dict[str, Any] = field(default_factory=dict)

    # Critics Loop for SPECS-based evaluation
    _critics_loop: CriticsLoop | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Judgment affordances available to all archetypes."""
        return SELF_AFFORDANCES["judgment"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View current judgment configuration."""
        return BasicRendering(
            summary="Judgment Configuration",
            content=(
                f"Wundt Curve Thresholds:\n"
                f"  Boring threshold: < {self._low_threshold}\n"
                f"  Chaotic threshold: > {self._high_threshold}\n"
                f"  Expectations: {len(self._expectations)} priors set"
            ),
            metadata={
                "low_threshold": self._low_threshold,
                "high_threshold": self._high_threshold,
                "expectation_keys": list(self._expectations.keys()),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle judgment aspects."""
        match aspect:
            case "taste":
                return await self._evaluate_taste(observer, **kwargs)
            case "surprise":
                return await self._measure_surprise(observer, **kwargs)
            case "expectations":
                return self._manage_expectations(observer, **kwargs)
            case "calibrate":
                return self._calibrate(observer, **kwargs)
            case "critique":
                return await self._critique_artifact(observer, **kwargs)
            case "refine":
                return await self._refine_artifact(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _evaluate_taste(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Evaluate aesthetic taste via Wundt Curve.

        Args:
            content: The content to evaluate
            prior: Optional prior expectation (defaults to observer context)

        Returns:
            TasteScore-like dict with novelty, complexity, verdict
        """
        from ..middleware.curator import (
            TasteScore,
            structural_surprise,
        )

        content = kwargs.get("content")
        prior = kwargs.get("prior")

        if content is None:
            return {"error": "content required"}

        # Get prior from context if not provided
        if prior is None:
            prior = self._expectations.get("prior")
            # Also check observer context (using getattr for type safety)
            if prior is None:
                obs_context = getattr(observer, "context", {})
                if isinstance(obs_context, dict):
                    obs_expectations = obs_context.get("expectations", {})
                    if isinstance(obs_expectations, dict):
                        prior = obs_expectations.get("prior")

        # Compute surprise
        if prior is not None:
            content_str = str(content)
            prior_str = str(prior)
            novelty = structural_surprise(content_str, prior_str)
        else:
            novelty = 0.5  # Neutral when no prior

        # Create TasteScore
        score = TasteScore.from_novelty(
            novelty=novelty,
            complexity=0.5,  # Default complexity
            low_threshold=self._low_threshold,
            high_threshold=self._high_threshold,
        )

        return {
            "novelty": score.novelty,
            "complexity": score.complexity,
            "wundt_score": score.wundt_score,
            "verdict": score.verdict,
            "is_acceptable": score.is_acceptable,
        }

    async def _measure_surprise(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> float:
        """
        Measure Bayesian surprise between content and prior.

        Args:
            content: The content to measure
            prior: The expected content

        Returns:
            Surprise value between 0.0 and 1.0
        """
        from ..middleware.curator import structural_surprise

        content = kwargs.get("content")
        prior = kwargs.get("prior", self._expectations.get("prior"))

        if content is None:
            return 0.5  # Neutral

        if prior is None:
            return 0.5  # Neutral when no prior

        return structural_surprise(str(content), str(prior))

    def _manage_expectations(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        View or set prior expectations.

        Args:
            set_key: Key to set (if setting)
            set_value: Value to set (if setting)
            get_key: Key to get (if getting)
            clear: If True, clear all expectations

        Returns:
            Current expectations or operation result
        """
        if kwargs.get("clear"):
            self._expectations.clear()
            return {"status": "cleared", "expectations": {}}

        set_key = kwargs.get("set_key")
        set_value = kwargs.get("set_value")
        if set_key and set_value is not None:
            self._expectations[set_key] = set_value
            return {"status": "set", "key": set_key}

        get_key = kwargs.get("get_key")
        if get_key:
            return {"key": get_key, "value": self._expectations.get(get_key)}

        return {"expectations": dict(self._expectations)}

    def _calibrate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Calibrate thresholds from feedback.

        Args:
            low: New low threshold
            high: New high threshold
            feedback: List of (content, rating) tuples for learning

        Returns:
            Updated thresholds
        """
        low = kwargs.get("low")
        high = kwargs.get("high")

        if low is not None:
            self._low_threshold = max(0.0, min(low, 1.0))
        if high is not None:
            self._high_threshold = max(0.0, min(high, 1.0))

        # Ensure low < high
        if self._low_threshold >= self._high_threshold:
            self._high_threshold = min(self._low_threshold + 0.1, 1.0)

        return {
            "status": "calibrated",
            "low_threshold": self._low_threshold,
            "high_threshold": self._high_threshold,
        }

    def _get_or_create_loop(self) -> CriticsLoop:
        """Get or create the CriticsLoop instance."""
        if self._critics_loop is None:
            self._critics_loop = CriticsLoop()
        return self._critics_loop

    async def _critique_artifact(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        SPECS-based critique of an artifact.

        Args:
            artifact: The artifact to evaluate
            purpose: Optional purpose for utility assessment
            prior_work: Optional list of prior work for novelty comparison

        Returns:
            Critique result as dict (novelty, utility, surprise, overall, reasoning)
        """
        artifact = kwargs.get("artifact")
        if artifact is None:
            return {"error": "artifact required"}

        purpose = kwargs.get("purpose")
        prior_work = kwargs.get("prior_work")

        loop = self._get_or_create_loop()
        critique = await loop.critique(artifact, observer, purpose=purpose, prior_work=prior_work)
        return critique.to_dict()

    async def _refine_artifact(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Iterative refinement loop with critique feedback.

        Requires a Logos instance to be passed for generation.

        Args:
            logos: Logos instance for invocations
            generator_path: AGENTESE path for generation
            purpose: Optional purpose for utility assessment
            threshold: Optional threshold (default 0.7)
            max_iterations: Optional max iterations (default 3)
            **generator_kwargs: Additional args for the generator

        Returns:
            RefinedArtifact result as dict
        """
        logos = kwargs.get("logos")
        generator_path = kwargs.get("generator_path")

        if logos is None:
            return {"error": "logos required"}
        if generator_path is None:
            return {"error": "generator_path required"}

        purpose = kwargs.get("purpose")
        threshold = kwargs.get("threshold", 0.7)
        max_iterations = kwargs.get("max_iterations", 3)

        # Extract generator kwargs (remove our params)
        generator_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ("logos", "generator_path", "purpose", "threshold", "max_iterations")
        }

        loop = CriticsLoop(threshold=threshold, max_iterations=max_iterations)
        result = await loop.generate_with_trace(
            logos, observer, generator_path, purpose=purpose, **generator_kwargs
        )
        return result.to_dict()


# === Identity Node ===


@dataclass
class IdentityNode(BaseLogosNode):
    """
    self.identity - Agent's identity and DNA.

    Provides introspection into the agent's identity.
    """

    _handle: str = "self.identity"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Identity introspection affordances."""
        return SELF_AFFORDANCES["identity"]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View identity from observer's DNA."""
        meta = self._umwelt_to_meta(observer)
        dna = observer.dna

        return BasicRendering(
            summary=f"Identity: {meta.name}",
            content=f"Archetype: {meta.archetype}\nCapabilities: {meta.capabilities}",
            metadata={
                "name": meta.name,
                "archetype": meta.archetype,
                "capabilities": meta.capabilities,
                "dna_type": type(dna).__name__,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle identity aspects."""
        match aspect:
            case "reflect":
                meta = self._umwelt_to_meta(observer)
                return {
                    "name": meta.name,
                    "archetype": meta.archetype,
                    "capabilities": list(meta.capabilities),
                    "reflection": f"I am {meta.name}, a {meta.archetype}.",
                }
            case "evolve":
                # Evolution requires careful consideration
                return {
                    "status": "identity evolution requires deliberation",
                    "note": "Use concept.identity.refine for deep evolution",
                }
            case _:
                return {"aspect": aspect, "status": "not implemented"}


# === Dashboard Node ===


@dataclass
class DashboardNode(BaseLogosNode):
    """
    self.dashboard - Real-time TUI dashboard.

    Delegates to the CLI dashboard handler since the TUI
    doesn't fit the Logos render model (it takes over the terminal).

    AGENTESE: self.dashboard
              self.dashboard.manifest  (launches TUI)
              self.dashboard.demo      (launches TUI with demo data)
    """

    _handle: str = "self.dashboard"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("manifest", "demo")

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Launch the dashboard TUI."""
        from protocols.cli.handlers.dashboard import cmd_dashboard

        # Run the dashboard (this takes over the terminal)
        cmd_dashboard([], None)

        # Return a simple acknowledgment after dashboard exits
        return BasicRendering(
            summary="Dashboard",
            content="Dashboard session ended.",
            metadata={"status": "exited"},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle dashboard aspects."""
        from protocols.cli.handlers.dashboard import cmd_dashboard

        match aspect:
            case "demo":
                cmd_dashboard(["--demo"], None)
                return BasicRendering(
                    summary="Dashboard (Demo)",
                    content="Dashboard demo session ended.",
                    metadata={"status": "exited", "mode": "demo"},
                )
            case _:
                # Default to manifest behavior
                return await self.manifest(observer)


# === Generic Self Node ===


@dataclass
class GenericSelfNode(BaseLogosNode):
    """Fallback node for undefined self.* paths."""

    holon: str
    _handle: str = ""

    def __post_init__(self) -> None:
        self._handle = f"self.{self.holon}"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("inspect",)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        return BasicRendering(
            summary=f"Self: {self.holon}",
            content=f"Generic self node for {self.holon}",
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        return {"holon": self.holon, "aspect": aspect, "kwargs": kwargs}


# === Self Context Resolver ===


@dataclass
class SelfContextResolver:
    """
    Resolver for self.* context.

    The self context provides introspection into the agent's
    internal state, memory, capabilities, identity, judgment, and semaphores.
    """

    # D-gent integration for persistence
    _d_gent: Any = None
    # N-gent integration for tracing
    _n_gent: Any = None
    # Purgatory for semaphore integration
    _purgatory: Any = None
    # CrystallizationEngine for memory crystal operations
    _crystallization_engine: Any = None
    # Ghost cache path for offline capability
    _ghost_path: Path | None = None
    # Four Pillars integration (Phase 6)
    _memory_crystal: Any = None  # MemoryCrystal from agents.m
    _pheromone_field: Any = None  # PheromoneField from agents.m
    _inference_agent: Any = None  # ActiveInferenceAgent from agents.m
    _language_games: dict[str, Any] = field(default_factory=dict)

    # Substrate integration (Phase 5)
    _substrate: Any = None  # SharedSubstrate from agents.m
    _router: Any = None  # CategoricalRouter from agents.m
    _compactor: Any = None  # Compactor from agents.m

    # Crown Jewel Brain integration (Session 3)
    _cartographer: Any = None  # CartographerAgent from agents.m

    # L-gent embedder for semantic search (Session 4)
    _embedder: Any = None  # L-gent Embedder for semantic embeddings

    # Data architecture rewrite (Phase 2)
    _dgent_new: Any = None  # New simplified D-gent (DgentProtocol)
    _data_bus: Any = None  # DataBus for reactive events

    # F-gent Flow integration (Phase 7)
    _flow: FlowNode | None = None

    # V-gent Vector integration (Phase 7)
    _vgent: Any = None  # VgentProtocol from agents.v
    _vector: VectorNode | None = None

    # Soul integration (Chat Protocol - Phase 2)
    _kgent_soul: Any = None  # KgentSoul from agents.k
    _soul: SoulNode | None = None

    # Singleton nodes for self context
    _memory: MemoryNode | None = None
    _capabilities: CapabilitiesNode | None = None
    _state: StateNode | None = None
    _identity: IdentityNode | None = None
    _judgment: JudgmentNode | None = None
    _semaphore: SemaphoreNode | None = None
    # Data architecture rewrite (Phase 2)
    _data: DataNode | None = None
    _bus: BusNode | None = None
    # Vitals context resolver for self.vitals.*
    _vitals_resolver: VitalsContextResolver | None = None
    # Self-grow resolver for self.grow.*
    _grow_resolver: SelfGrowResolver | None = None

    def __post_init__(self) -> None:
        """Initialize singleton nodes."""
        # MemoryNode simplified in data-architecture-rewrite Phase 6
        self._memory = MemoryNode(
            _ghost_path=self._ghost_path,
            _embedder=self._embedder,
        )
        self._capabilities = CapabilitiesNode()
        self._state = StateNode()
        self._identity = IdentityNode()
        self._judgment = JudgmentNode()
        self._semaphore = SemaphoreNode(_purgatory=self._purgatory)
        # Data architecture rewrite (Phase 2)
        self._data = create_data_resolver(dgent=self._dgent_new)
        self._bus = create_bus_resolver(bus=self._data_bus)
        self._vitals_resolver = create_vitals_resolver()
        self._grow_resolver = create_self_grow_resolver()
        # F-gent Flow integration (Phase 7)
        self._flow = create_flow_resolver()
        # V-gent Vector integration (Phase 7)
        self._vector = VectorNode(_vgent=self._vgent)
        # Soul integration (Chat Protocol - Phase 2)
        self._soul = create_soul_node(soul=self._kgent_soul)

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a self.* path to a node.

        Args:
            holon: The self subsystem (memory, capabilities, state, identity, judgment, semaphore, vitals, dashboard)
            rest: Additional path components

        Returns:
            Resolved node

        Note:
            For vitals, rest contains the vitals component (triad, synapse, resonance, circuit).
            E.g., self.vitals.triad → holon="vitals", rest=["triad"]
        """
        match holon:
            case "memory":
                # Handle nested memory paths (Crown Jewel Brain)
                if rest:
                    sub_holon = rest[0]
                    memory_node = self._memory or MemoryNode()
                    if sub_holon == "ghost":
                        return MemoryGhostNode(_parent_memory=memory_node)
                    elif sub_holon == "cartography":
                        return MemoryCartographyNode(
                            _parent_memory=memory_node,
                        )
                    # Default: return memory node for other sub-paths
                return self._memory or MemoryNode()
            case "capabilities":
                return self._capabilities or CapabilitiesNode()
            case "state":
                return self._state or StateNode()
            case "identity":
                return self._identity or IdentityNode()
            case "judgment":
                return self._judgment or JudgmentNode()
            case "semaphore":
                return self._semaphore or SemaphoreNode()
            case "dashboard":
                # Delegate to CLI handler (TUI takes over terminal)
                return DashboardNode()
            case "vitals":
                # Delegate to vitals resolver
                if self._vitals_resolver is None:
                    self._vitals_resolver = create_vitals_resolver()
                if rest:
                    # self.vitals.triad → VitalsContextResolver.resolve("triad", [])
                    return self._vitals_resolver.resolve(rest[0], rest[1:])
                # self.vitals → Return triad health as default
                return self._vitals_resolver.resolve("triad", [])
            case "grow":
                # Delegate to self-grow resolver (autopoietic holon generator)
                if self._grow_resolver is None:
                    self._grow_resolver = create_self_grow_resolver()
                if rest:
                    # self.grow.recognize → SelfGrowResolver.resolve("recognize", [])
                    return self._grow_resolver.resolve(rest[0], rest[1:])
                # self.grow → Return recognize as default (gap discovery)
                return self._grow_resolver.resolve("recognize", [])
            # Data architecture rewrite (Phase 2)
            case "data":
                # self.data.* → DataNode for D-gent operations
                return self._data or DataNode()
            case "bus":
                # self.bus.* → BusNode for DataBus operations
                return self._bus or BusNode()
            # F-gent Flow integration (Phase 7)
            case "flow":
                # self.flow.* → FlowNode for chat/research/collaboration
                flow_node = self._flow or create_flow_resolver()
                if rest:
                    sub_holon = rest[0]
                    if sub_holon == "chat":
                        return ChatFlowNode(_parent_flow=flow_node)
                    elif sub_holon == "research":
                        return ResearchFlowNode(_parent_flow=flow_node)
                    elif sub_holon == "collaboration":
                        return CollaborationFlowNode(_parent_flow=flow_node)
                return flow_node
            # V-gent Vector integration (Phase 7)
            case "vector":
                # self.vector.* → VectorNode for vector operations
                return self._vector or VectorNode()
            # Soul integration (Chat Protocol - Phase 2)
            case "soul":
                # self.soul.* → SoulNode for K-gent dialogue
                return self._soul or create_soul_node()
            case _:
                # Generic self node for undefined holons
                return GenericSelfNode(holon)


# === Factory Functions ===


def create_self_resolver(
    d_gent: Any = None,
    n_gent: Any = None,
    purgatory: Any = None,
    crystallization_engine: Any = None,
    ghost_path: Path | None = None,
    # Four Pillars integration (Phase 6)
    memory_crystal: Any = None,
    pheromone_field: Any = None,
    inference_agent: Any = None,
    language_games: dict[str, Any] | None = None,
    # Substrate integration (Phase 5)
    substrate: Any = None,
    router: Any = None,
    compactor: Any = None,
    # Crown Jewel Brain integration (Session 3-4)
    cartographer: Any = None,
    embedder: Any = None,
    # Data architecture rewrite (Phase 2)
    dgent_new: Any = None,
    data_bus: Any = None,
    # V-gent Vector integration (Phase 7)
    vgent: Any = None,
    # Soul integration (Chat Protocol - Phase 2)
    kgent_soul: Any = None,
) -> SelfContextResolver:
    """
    Create a SelfContextResolver with optional integrations.

    Args:
        d_gent: D-gent for persistence (legacy)
        n_gent: N-gent for tracing
        purgatory: Purgatory for semaphore integration
        crystallization_engine: CrystallizationEngine for crystal operations
        ghost_path: Path for Ghost cache (defaults to ~/.kgents/ghost)
        memory_crystal: MemoryCrystal for Four Pillars holographic memory
        pheromone_field: PheromoneField for stigmergic coordination
        inference_agent: ActiveInferenceAgent for free energy-based retention
        language_games: Dict of language games for Wittgensteinian access
        substrate: SharedSubstrate for memory allocation and management
        router: CategoricalRouter for stigmergic task routing
        compactor: Compactor for graceful memory compaction
        cartographer: CartographerAgent for holographic memory navigation
        embedder: L-gent Embedder for semantic embeddings (Session 4)
        dgent_new: New simplified D-gent (DgentProtocol from data-architecture-rewrite)
        data_bus: DataBus for reactive data events
        vgent: V-gent backend (VgentProtocol from agents.v) for vector operations
        kgent_soul: KgentSoul from agents.k for soul dialogue

    Returns:
        Configured SelfContextResolver
    """
    resolver = SelfContextResolver()
    resolver._d_gent = d_gent
    resolver._n_gent = n_gent
    resolver._purgatory = purgatory
    resolver._crystallization_engine = crystallization_engine
    resolver._ghost_path = ghost_path
    # Four Pillars
    resolver._memory_crystal = memory_crystal
    resolver._pheromone_field = pheromone_field
    resolver._inference_agent = inference_agent
    resolver._language_games = language_games or {}
    # Substrate
    resolver._substrate = substrate
    resolver._router = router
    resolver._compactor = compactor
    # Crown Jewel Brain
    resolver._cartographer = cartographer
    resolver._embedder = embedder
    # Data architecture rewrite (Phase 2)
    resolver._dgent_new = dgent_new
    resolver._data_bus = data_bus
    # V-gent Vector integration (Phase 7)
    resolver._vgent = vgent
    # Soul integration (Chat Protocol - Phase 2)
    resolver._kgent_soul = kgent_soul
    resolver.__post_init__()  # Reinitialize with integrations
    return resolver
