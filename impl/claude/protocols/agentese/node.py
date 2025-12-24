"""
AGENTESE LogosNode Protocol

A node in the AGENTESE graph. Every node is a potential interaction,
not static data.

AGENTESE Principle: Nouns are frozen verbs.

Key invariants:
- LogosNode must be stateless (Symbiont pattern)
- State access via D-gent Lens only
- All methods require observer context (no view from nowhere)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Protocol,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from agents.poly.types import Agent
    from bootstrap.umwelt import Umwelt

# Type variables for generic types
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type
T_in = TypeVar("T_in", contravariant=True)
T_out = TypeVar("T_out", covariant=True)


# === Observer Base Class (v3) ===


@dataclass(frozen=True)
class Observer:
    """
    Lightweight observer for simple AGENTESE invocations (v3 API).

    The minimal observer context required for path invocation.
    Use this when you don't need full Umwelt context.

    AGENTESE v3 Principle: Observer gradations allow lightweight calls
    while preserving "no view from nowhere" semantics.

    Examples:
        # Simple invocation with default guest
        await logos("world.garden.manifest")

        # Developer observer
        await logos("self.forest.manifest", Observer(archetype="developer"))

        # With specific capabilities
        await logos("self.soul.challenge", Observer(
            archetype="developer",
            capabilities=frozenset({"define", "refine"})
        ))

    Factory methods:
        Observer.guest() - Anonymous guest observer
        Observer.test() - Test observer with all capabilities
        Observer.from_umwelt(umwelt) - Extract from full Umwelt

    Teaching:
        gotcha: Observer can be None in v3 API—Logos.invoke() defaults to
                Observer.guest(). But guest observers have minimal affordances.
                Be explicit about archetype for non-trivial operations.
                (Evidence: test_logos.py::test_guest_observer)

        gotcha: Observer is frozen (immutable). To change capabilities,
                create a new Observer instance. This enables safe sharing.
                (Evidence: test_node.py::test_observer_immutable)
    """

    archetype: str = "guest"
    capabilities: frozenset[str] = frozenset()

    @classmethod
    def guest(cls) -> "Observer":
        """Create anonymous guest observer."""
        return cls(archetype="guest", capabilities=frozenset())

    @classmethod
    def test(cls) -> "Observer":
        """Create test observer with broad capabilities."""
        return cls(
            archetype="developer",
            capabilities=frozenset({"define", "refine", "test", "debug"}),
        )

    @classmethod
    def from_archetype(cls, archetype: str) -> "Observer":
        """Create observer from archetype name."""
        return cls(archetype=archetype, capabilities=frozenset())

    @classmethod
    def from_umwelt(cls, umwelt: "Umwelt[Any, Any]") -> "Observer":
        """
        Extract Observer from a full Umwelt.

        Allows using Umwelt where Observer is expected.
        """
        dna = umwelt.dna
        archetype = getattr(dna, "archetype", "guest")
        caps = getattr(dna, "capabilities", ())
        return cls(
            archetype=archetype,
            capabilities=frozenset(caps) if not isinstance(caps, frozenset) else caps,
        )


# === Polynomial Manifest ===


@dataclass(frozen=True)
class PolynomialManifest:
    """
    The polynomial functor structure of an agent.

    This makes AD-002 (Polynomial Generalization) visible by exposing
    the state machine structure of any agent.

    Every agent has a polynomial functor P[S, A, B] where:
    - S is the set of positions (states)
    - For each position s in S, we have E(s) = directions available from s
    - A is the input type, B is the output type (not captured here)

    This type captures the S and E structure, making it visible and interactive.

    Teaching:
        gotcha: Default polynomial() returns single 'default' position with all
                affordances as directions. Override in PolyAgent subclasses
                (e.g., Gardener) to expose real state machine structure.
                (Evidence: test_node.py::test_polynomial_default)
    """

    positions: tuple[str, ...]  # S: set of positions (states)
    current: str  # Current position
    directions: Mapping[str, tuple[str, ...]]  # E(s): directions from each position

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "positions": list(self.positions),
            "current": self.current,
            "directions": {k: list(v) for k, v in self.directions.items()},
        }


# === Agent Metadata (v1 compatibility) ===


@dataclass(frozen=True)
class AgentMeta:
    """
    Metadata about an agent for affordance filtering.

    NOTE: v1 API - prefer Observer for new code.

    This is a lightweight view of the agent's identity, separate from
    the full Umwelt. Used by LogosNode.affordances() to determine
    what verbs are available.

    Teaching:
        gotcha: AgentMeta is the v1 affordance API. New code should use
                Observer directly—BaseLogosNode._umwelt_to_meta() bridges
                both for backward compatibility.
                (Evidence: test_node.py::test_agentmeta_to_observer)
    """

    name: str
    archetype: str = "default"
    capabilities: tuple[str, ...] = ()

    def to_observer(self) -> Observer:
        """Convert to v3 Observer."""
        return Observer(
            archetype=self.archetype,
            capabilities=frozenset(self.capabilities),
        )

    @classmethod
    def from_observer(cls, observer: Observer, name: str = "unknown") -> "AgentMeta":
        """Create from v3 Observer."""
        return cls(
            name=name,
            archetype=observer.archetype,
            capabilities=tuple(observer.capabilities),
        )


# === Renderable Protocol ===


@runtime_checkable
class Renderable(Protocol):
    """
    Protocol for objects that can be rendered to observers.

    The result of manifest() must be Renderable—can be converted
    to various output formats based on observer preference.

    Teaching:
        gotcha: Renderable is a Protocol (structural typing), not ABC.
                Any class with to_dict() and to_text() methods satisfies it.
                (Evidence: test_node.py::test_renderable_protocol)
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        ...

    def to_text(self) -> str:
        """Convert to human-readable text."""
        ...


# === Affordance Set ===


@dataclass(frozen=True)
class AffordanceSet:
    """
    Affordances available to a specific observer.

    The Umwelt Principle: Each agent inhabits its own
    world; there is no view from nowhere.

    Teaching:
        gotcha: AffordanceSet is observer-specific. Different observers
                get different verbs from the same node—this is intentional.
                (Evidence: test_node.py::test_affordance_polymorphism)
    """

    handle: str
    observer_archetype: str
    verbs: tuple[str, ...]
    state: dict[str, Any] = field(default_factory=dict)
    related: tuple[str, ...] = ()

    def __contains__(self, verb: str) -> bool:
        """Check if verb is in affordances."""
        return verb in self.verbs

    def __iter__(self) -> Iterator[str]:
        """Iterate over available verbs."""
        return iter(self.verbs)


# === LogosNode Protocol ===


@runtime_checkable
class LogosNode(Protocol):
    """
    A node in the AGENTESE graph.

    Every node is a potential interaction, not static data.
    Must be stateless (Symbiont pattern—state via D-gent Lens).

    AGENTESE Principle: Nouns are frozen verbs.

    Teaching:
        gotcha: LogosNode must be stateless. Any state access must go through
                D-gent Lens (dependency injection). This enables composition.
                (Evidence: test_node.py::test_logos_node_stateless)
    """

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        ...

    def affordances(self, observer: AgentMeta) -> list[str]:
        """
        What verbs are available to this observer?

        Enforces Principle #3: Ethical (Permissioning).
        The Polymorphic Principle: Different observers
        receive different affordances.

        Args:
            observer: Metadata about the requesting agent

        Returns:
            List of available aspect names
        """
        ...

    def lens(self, aspect: str) -> "Agent[Any, Any]":
        """
        Return the agent morphism for a specific aspect.

        Enforces Principle #5: Composable.
        The returned Agent can be composed with >> operator.

        Args:
            aspect: The verb to get a lens for

        Returns:
            Composable Agent morphism
        """
        ...

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Collapse the wave function into a representation.

        The Observation Principle: Perception is action.
        What is perceived depends on who perceives.

        Args:
            observer: The observer's projected world (Umwelt)

        Returns:
            Observer-appropriate representation
        """
        ...

    async def invoke(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Execute an affordance on this node.

        Args:
            aspect: The verb to invoke
            observer: The observer's projected world
            **kwargs: Aspect-specific arguments

        Returns:
            Aspect-specific result
        """
        ...


# === Base Implementation ===


class BaseLogosNode(ABC):
    """
    Abstract base class for LogosNode implementations.

    Provides common functionality while enforcing the protocol.
    Subclasses must implement:
    - handle (property)
    - _get_affordances_for_archetype()
    - manifest()
    - invoke()

    Teaching:
        gotcha: BaseLogosNode provides default implementations for help,
                alternatives, and polynomial aspects. Override polynomial()
                in PolyAgent subclasses to expose real state machine.
                (Evidence: test_node.py::test_base_logos_node_defaults)
    """

    @property
    @abstractmethod
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        pass

    # Standard affordances available to all archetypes
    # v3.1: Added "help" for self-documentation
    # v3.2: Added "alternatives" for Ghost Integration
    # v3.3: Added "polynomial" for Mini Polynomial (AD-002 visualization)
    _base_affordances: tuple[str, ...] = (
        "manifest",
        "witness",
        "affordances",
        "help",
        "alternatives",
        "polynomial",
    )

    # Aspect hints for Ghost Integration (v3.2)
    # Override in subclasses to provide domain-specific hints
    # ClassVar ensures dataclass subclasses treat this as class-level, not instance field
    ASPECT_HINTS: ClassVar[dict[str, str]] = {
        "manifest": "Collapse to observer's view—see the entity as it appears to you",
        "witness": "View historical traces—see what happened before",
        "affordances": "List available aspects—discover what you can do here",
        "help": "Get detailed help about this node and its aspects",
        "alternatives": "Show ghost alternatives—paths you could have taken",
        "lens": "Get a composable agent view for category-theoretic composition",
        "polynomial": "Show polynomial functor structure—visualize state machine",
    }

    def affordances(self, observer: AgentMeta) -> list[str]:
        """
        Return observer-specific affordances.

        Combines base affordances with archetype-specific ones.
        """
        base = list(self._base_affordances)
        extra = self._get_affordances_for_archetype(observer.archetype)
        return base + list(extra)

    @abstractmethod
    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Override in subclasses to provide polymorphic affordances.
        """
        pass

    def lens(self, aspect: str) -> "Agent[Any, Any]":
        """
        Return composable agent for aspect.

        Default implementation creates an AspectAgent wrapper.
        Override for custom aspect agents.
        """
        return AspectAgent(self, aspect)  # type: ignore[return-value]

    @abstractmethod
    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """Collapse to observer-appropriate representation."""
        pass

    async def invoke(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Execute an aspect on this node.

        Default implementation routes to _invoke_aspect().
        If constitutional=True in @node metadata, wraps with DP evaluation.
        """
        # Check if this node is constitutional
        from .registry import get_node_metadata

        meta = get_node_metadata(self.__class__)
        if meta and meta.constitutional:
            # Wrap invocation with constitutional evaluation
            return await self._invoke_constitutional(aspect, observer, **kwargs)

        # Standard invocation path
        return await self._invoke_standard(aspect, observer, **kwargs)

    async def _invoke_standard(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Standard invocation without constitutional evaluation."""
        if aspect == "manifest":
            return await self.manifest(observer, **kwargs)
        if aspect == "affordances":
            # Get AgentMeta from Umwelt's DNA
            meta = self._umwelt_to_meta(observer)
            return self.affordances(meta)
        if aspect == "help":
            # v3.1: Self-documentation aspect
            meta = self._umwelt_to_meta(observer)
            return self._generate_help(meta)
        if aspect == "alternatives":
            # v3.2: Ghost alternatives aspect
            invoked_aspect = kwargs.get("invoked_aspect")
            meta = self._umwelt_to_meta(observer)
            return self._get_alternatives(invoked_aspect, meta)
        if aspect == "polynomial":
            # v3.3: Polynomial functor structure (Mini Polynomial)
            return await self.polynomial(observer)
        return await self._invoke_aspect(aspect, observer, **kwargs)

    async def _invoke_constitutional(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Invoke aspect with constitutional evaluation.

        Captures state before/after, evaluates against Constitution,
        emits TraceEntry with principle scores.
        """
        from services.categorical import PolicyTrace, TraceEntry, ValueFunction, Principle

        # Capture state before (use hashable representation)
        state_before_str = f"{self.handle}:{aspect}:{sorted(kwargs.items())}"
        state_before = {
            "path": self.handle,
            "aspect": aspect,
            "kwargs": kwargs,
        }

        # Execute the aspect
        result = await self._invoke_standard(aspect, observer, **kwargs)

        # Capture state after
        state_after = {
            "path": self.handle,
            "aspect": aspect,
            "result": str(result)[:200],  # Truncate for brevity
        }

        # Evaluate against Constitution
        # Use hashable state representation for caching
        value_fn = self._get_value_function()
        score = value_fn.evaluate(
            agent_name=f"{self.handle}.{aspect}",
            state=state_before_str,  # Use string instead of dict for hashability
            action=aspect,
        )

        # Emit trace entry
        entry = TraceEntry(
            state_before=state_before,
            action=f"{self.handle}.{aspect}",
            state_after=state_after,
            value=score.total_score,
            rationale=f"Constitutional evaluation: {score.min_score:.2f} min, {score.total_score:.2f} avg",
        )

        # Log the trace entry (integrate with Witness in future)
        import logging
        logger = logging.getLogger("kgents.agentese.constitutional")
        logger.info(
            f"Constitutional invocation: {entry.action} -> "
            f"value={entry.value:.3f} (min={score.min_score:.3f})"
        )

        # For now, just return the result
        # TODO: Store trace in PolicyTrace and integrate with Witness
        return result

    def _get_value_function(self) -> "Any":
        """
        Get the ValueFunction for constitutional evaluation.

        Override in subclasses to provide custom principle evaluators.
        Default implementation uses neutral scoring.
        """
        from services.categorical import ValueFunction, Principle

        # Default: neutral scoring (0.5 for all principles)
        return ValueFunction()

    def _generate_help(self, observer: AgentMeta) -> str:
        """
        Generate self-documenting help for this node.

        v3.1: Every node can describe itself via the help aspect.
        Uses AspectMetadata for rich documentation when available.

        Args:
            observer: The observer requesting help

        Returns:
            Formatted help string showing path, affordances, and descriptions
        """
        from .affordances import STANDARD_ASPECTS

        # Get affordances for this observer
        affordances = self.affordances(observer)

        lines = [
            f"Path: {self.handle}",
            f"Observer: {observer.archetype}",
            "",
            "Affordances:",
        ]

        for aff in affordances:
            aspect_info = STANDARD_ASPECTS.get(aff)
            if aspect_info:
                desc = aspect_info.description
                cat = aspect_info.category.name
                lines.append(f"  {aff:20} [{cat:12}] {desc}")
                # Show examples if available
                if hasattr(aspect_info, "examples") and aspect_info.examples:
                    for ex in aspect_info.examples[:2]:
                        lines.append(f"    Example: {ex}")
                # Show related aspects if available
                if hasattr(aspect_info, "see_also") and aspect_info.see_also:
                    related = ", ".join(aspect_info.see_also[:3])
                    lines.append(f"    See also: {related}")
            else:
                lines.append(f"  {aff:20} (custom aspect)")

        return "\n".join(lines)

    def _get_alternatives(
        self,
        invoked_aspect: str | None,
        observer: AgentMeta,
    ) -> list[dict[str, Any]]:
        """
        Get ghost alternatives for this node.

        Returns sibling aspects that could have been invoked instead of
        the current aspect. Excludes the invoked aspect itself.

        v3.2: Ghost Integration for Différance visibility.

        Args:
            invoked_aspect: The aspect that was invoked (to exclude)
            observer: The observer requesting alternatives

        Returns:
            List of Ghost dictionaries with aspect, hint, and category
        """
        from .affordances import STANDARD_ASPECTS

        # Get all affordances for this observer
        all_affordances = self.affordances(observer)

        # Exclude the invoked aspect and the introspection aspects
        exclude = {"alternatives", "affordances", "help"}
        if invoked_aspect:
            exclude.add(invoked_aspect)

        ghosts: list[Ghost] = []
        for aspect in all_affordances:
            if aspect in exclude:
                continue

            # Get hint from class-level ASPECT_HINTS or affordances registry
            hint = self.ASPECT_HINTS.get(aspect)
            if not hint:
                aspect_info = STANDARD_ASPECTS.get(aspect)
                hint = aspect_info.description if aspect_info else f"Invoke {aspect}"

            # Get category
            aspect_info = STANDARD_ASPECTS.get(aspect)
            category = aspect_info.category.name if aspect_info else "UNKNOWN"

            ghosts.append(
                Ghost(
                    aspect=aspect,
                    hint=hint,
                    category=category,
                )
            )

        # Limit to 5 ghosts max (per requirements)
        ghosts = ghosts[:5]

        # Return as dictionaries for serialization
        return [g.to_dict() for g in ghosts]

    async def polynomial(self, observer: "Observer | Umwelt[Any, Any]") -> PolynomialManifest:
        """
        Return the polynomial functor structure of this agent.

        This makes AD-002 (Polynomial Generalization) visible by exposing
        the state machine as P[S, A, B] where S is positions and E(s) is
        directions available from each position.

        Default implementation: single 'default' position with all aspects
        as available directions. Override in subclasses for real state machines
        (e.g., Gardener with SENSE/ACT/REFLECT positions).

        Args:
            observer: The observer context (Observer or Umwelt)

        Returns:
            PolynomialManifest with positions, current, and directions
        """
        meta = (
            self._umwelt_to_meta(observer)
            if not isinstance(observer, Observer)
            else AgentMeta.from_observer(observer)
        )
        aspects = self.affordances(meta)
        return PolynomialManifest(
            positions=("default",),
            current="default",
            directions={"default": tuple(aspects)},
        )

    @abstractmethod
    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Invoke a non-standard aspect.

        Override in subclasses to handle domain-specific aspects.
        """
        pass

    def _umwelt_to_meta(self, observer: "Observer | Umwelt[Any, Any]") -> AgentMeta:
        """
        Extract AgentMeta from Observer or Umwelt.

        v3 API: Accepts both Observer (lightweight) and Umwelt (full context).
        """
        # v3 Observer - direct extraction
        if isinstance(observer, Observer):
            return AgentMeta.from_observer(observer)

        # v1 Umwelt - extract from DNA
        dna = observer.dna
        # Try to get archetype from DNA, fallback to defaults
        name = getattr(dna, "name", "unknown")
        archetype = getattr(dna, "archetype", "default")
        capabilities = getattr(dna, "capabilities", ())
        return AgentMeta(name=name, archetype=archetype, capabilities=capabilities)


# === JIT Node ===


@dataclass
class JITLogosNode:
    """
    A LogosNode generated at runtime from a spec.

    Created by J-gent JIT compilation when no implementation exists
    but a spec is found. Tracks usage for promotion decisions.

    Teaching:
        gotcha: JIT nodes track usage_count and success_rate for promotion.
                Use should_promote() to check if node is ready for permanent
                implementation in impl/.
                (Evidence: test_jit.py::test_jit_promotion_threshold)
    """

    handle: str
    source: str  # Generated Python source
    spec: str  # Original spec content
    usage_count: int = 0
    success_count: int = 0

    # Runtime-compiled module
    _module: Any = field(default=None, repr=False)
    _node: LogosNode | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Compile source on creation."""
        if self.source and not self._module:
            self._compile()

    def _compile(self) -> None:
        """Compile source to module and extract node."""
        # Note: Full implementation would use exec() with proper sandboxing
        # For now, this is a placeholder
        pass

    def affordances(self, observer: AgentMeta) -> list[str]:
        """Delegate to compiled node."""
        self.usage_count += 1
        if self._node:
            return self._node.affordances(observer)
        return ["manifest", "witness", "affordances"]

    def lens(self, aspect: str) -> "Agent[Any, Any]":
        """Delegate to compiled node."""
        if self._node:
            return self._node.lens(aspect)
        return AspectAgent(self, aspect)  # type: ignore[return-value]

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Delegate to compiled node."""
        self.usage_count += 1
        if self._node:
            return await self._node.manifest(observer)
        # Fallback: return spec as rendering
        return BasicRendering(
            summary=f"JIT node: {self.handle}",
            content=self.spec,
        )

    async def invoke(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Delegate to compiled node with usage tracking."""
        self.usage_count += 1
        try:
            if self._node:
                result = await self._node.invoke(aspect, observer, **kwargs)
            else:
                result = await self._fallback_invoke(aspect, observer, **kwargs)
            self.success_count += 1
            return result
        except Exception:
            raise

    async def _fallback_invoke(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Fallback invocation when module not compiled."""
        if aspect == "manifest":
            return await self.manifest(observer)
        raise NotImplementedError(
            f"JIT node {self.handle} has no compiled implementation for {aspect}"
        )

    @property
    def success_rate(self) -> float:
        """Success rate for promotion decisions."""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count

    def should_promote(self, threshold: int = 100, success_threshold: float = 0.8) -> bool:
        """Check if node should be promoted to permanent implementation."""
        return self.usage_count >= threshold and self.success_rate >= success_threshold


# === Ghost Alternative ===


@dataclass(frozen=True)
class Ghost:
    """
    An alternative aspect that could have been invoked.

    Represents a path not taken in the AGENTESE graph. These are the
    ghosts of Différance—aspects that were available but not chosen.

    Attributes:
        aspect: The aspect name (e.g., "witness", "refine")
        hint: Human-readable hint about what this aspect does
        category: Optional category for grouping (e.g., "PERCEPTION", "MUTATION")

    Teaching:
        gotcha: Ghosts are limited to 5 per invocation. BaseLogosNode._get_alternatives()
                truncates to prevent UI overload.
                (Evidence: test_node.py::test_ghost_limit)
    """

    aspect: str
    hint: str
    category: str = "UNKNOWN"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "aspect": self.aspect,
            "hint": self.hint,
            "category": self.category,
        }


# === Renderable Implementations ===


@dataclass(frozen=True)
class BasicRendering:
    """
    Simple rendering with summary and optional content.

    Teaching:
        gotcha: BasicRendering is the fallback for nodes without specialized
                rendering. Use BlueprintRendering/PoeticRendering/EconomicRendering
                for archetype-specific output.
                (Evidence: test_node.py::test_basic_rendering_fallback)
    """

    summary: str
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "summary": self.summary,
            "content": self.content,
            "metadata": self.metadata,
        }

    def to_text(self) -> str:
        """Convert to human-readable text format."""
        if self.content:
            return f"{self.summary}\n\n{self.content}"
        return self.summary


@dataclass(frozen=True)
class BlueprintRendering:
    """
    Technical rendering for architect archetypes.

    Teaching:
        gotcha: BlueprintRendering is returned when observer.archetype == "architect".
                Contains dimensions, materials, and structural analysis.
                (Evidence: test_node.py::test_archetype_rendering)
    """

    dimensions: dict[str, float] = field(default_factory=dict)
    materials: tuple[str, ...] = ()
    structural_analysis: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "type": "blueprint",
            "dimensions": self.dimensions,
            "materials": list(self.materials),
            "structural_analysis": self.structural_analysis,
        }

    def to_text(self) -> str:
        """Convert to human-readable text format."""
        lines = ["BLUEPRINT"]
        if self.dimensions:
            lines.append(f"Dimensions: {self.dimensions}")
        if self.materials:
            lines.append(f"Materials: {', '.join(self.materials)}")
        return "\n".join(lines)


@dataclass(frozen=True)
class PoeticRendering:
    """
    Aesthetic rendering for poet archetypes.

    Teaching:
        gotcha: PoeticRendering is returned when observer.archetype == "poet".
                Contains metaphors and mood for aesthetic interpretation.
                (Evidence: test_node.py::test_archetype_rendering)
    """

    description: str
    metaphors: tuple[str, ...] = ()
    mood: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "type": "poetic",
            "description": self.description,
            "metaphors": list(self.metaphors),
            "mood": self.mood,
        }

    def to_text(self) -> str:
        """Convert to human-readable text format."""
        lines = [self.description]
        if self.mood:
            lines.append(f"Mood: {self.mood}")
        if self.metaphors:
            lines.append("Metaphors: " + ", ".join(self.metaphors))
        return "\n".join(lines)


@dataclass(frozen=True)
class EconomicRendering:
    """
    Financial rendering for economist archetypes.

    Teaching:
        gotcha: EconomicRendering is returned when observer.archetype == "economist".
                Contains market value, comparable sales, and forecasts.
                (Evidence: test_node.py::test_archetype_rendering)
    """

    market_value: float = 0.0
    comparable_sales: tuple[dict[str, Any], ...] = ()
    appreciation_forecast: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "type": "economic",
            "market_value": self.market_value,
            "comparable_sales": list(self.comparable_sales),
            "appreciation_forecast": self.appreciation_forecast,
        }

    def to_text(self) -> str:
        """Convert to human-readable text format."""
        lines = [f"Market Value: ${self.market_value:,.2f}"]
        if self.appreciation_forecast:
            lines.append(f"Forecast: {self.appreciation_forecast}")
        return "\n".join(lines)


# === Aspect Agent Wrapper ===


@dataclass
class AspectAgent:
    """
    Wrapper that turns a LogosNode aspect into a composable Agent.

    Used by lens() to return Agent[Umwelt, Any] for composition.

    Teaching:
        gotcha: AspectAgent enables >> composition of node aspects.
                a.lens("manifest") >> b.lens("refine") composes.
                (Evidence: test_node.py::test_aspect_agent_composition)
    """

    node: LogosNode
    aspect: str

    @property
    def name(self) -> str:
        """Return the fully-qualified aspect path."""
        return f"{self.node.handle}.{self.aspect}"

    async def invoke(self, input: "Umwelt[Any, Any]") -> Any:
        """Invoke the aspect with the Umwelt as input."""
        return await self.node.invoke(self.aspect, input)

    def __rshift__(self, other: "Agent[Any, Any]") -> "ComposedAspectAgent":
        """Compose with another agent."""
        return ComposedAspectAgent(self, other)


@dataclass
class ComposedAspectAgent:
    """
    Composition of AspectAgent with another Agent.

    Teaching:
        gotcha: ComposedAspectAgent preserves associativity:
                (a >> b) >> c == a >> (b >> c). This is enforced by the
                flattening logic in __rshift__.
                (Evidence: test_node.py::test_composition_associativity)
    """

    first: AspectAgent
    second: "Agent[Any, Any]"

    @property
    def name(self) -> str:
        """Return the composition name showing the pipeline."""
        return f"({self.first.name} >> {self.second.name})"

    async def invoke(self, input: "Umwelt[Any, Any]") -> Any:
        """Execute first, then second."""
        intermediate = await self.first.invoke(input)
        return await self.second.invoke(intermediate)

    def __rshift__(self, other: "Agent[Any, Any]") -> "ComposedAspectAgent":
        """Compose with another agent."""
        # Flatten: (a >> b) >> c -> ComposedAspectAgent(a, b >> c)
        # This preserves associativity
        composed_second = ComposedAspectAgent(
            AspectAgent(
                node=_WrapperNode(self.second),
                aspect="invoke",
            ),
            other,
        )
        return ComposedAspectAgent(self.first, composed_second)  # type: ignore[arg-type]


# === Helper Types ===


@dataclass
class _WrapperNode:
    """Internal wrapper to make Agent work as LogosNode."""

    agent: "Agent[Any, Any]"

    @property
    def handle(self) -> str:
        """Return the agent's name as the AGENTESE handle."""
        return self.agent.name

    def affordances(self, observer: AgentMeta) -> list[str]:
        """Return minimal affordances for wrapped agents."""
        return ["invoke"]

    def lens(self, aspect: str) -> "Agent[Any, Any]":
        """Return the wrapped agent as a lens."""
        return self.agent

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """Return basic rendering for wrapped agents."""
        return BasicRendering(summary=f"Agent: {self.agent.name}")

    async def invoke(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Invoke the wrapped agent with observer as input."""
        return await self.agent.invoke(observer)
