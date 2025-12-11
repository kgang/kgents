"""
AGENTESE Phase 3: Polymorphic Affordances

Observer-dependent affordance filtering with Umwelt integration.

The key insight: the same handle yields different affordances depending
on who grasps it. This is the Polymorphic Principle in action.

Example:
    # Architect sees: [manifest, witness, renovate, measure, blueprint, demolish]
    # Poet sees: [manifest, witness, describe, metaphorize, inhabit]
    # Default sees: [manifest, witness, affordances]

This module provides:
- AffordanceRegistry: Central registry of archetype → affordances mappings
- AffordanceMatcher: Pattern-based affordance resolution
- ArchetypeDNA: DNA type for archetype-based agent configuration
- UmweltAdapter: Extract affordance-relevant info from Umwelt
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from .node import AgentMeta


# === Aspect Categories ===


class AspectCategory(Enum):
    """
    Categories of aspects from the AGENTESE spec (Part IV, §4.2).

    Each category has different access patterns and side effects.
    """

    PERCEPTION = auto()  # manifest, witness, sense, map (read-only)
    MUTATION = auto()  # transform, renovate, evolve, repair (state-changing)
    COMPOSITION = auto()  # compose, merge, split, relate, lens (category laws)
    INTROSPECTION = auto()  # affordances, constraints, lineage (meta)
    GENERATION = auto()  # define, spawn, fork, dream (autopoiesis)
    ENTROPY = auto()  # sip, pour, tithe, thank (Accursed Share)


# === Aspect Definition ===


@dataclass(frozen=True)
class Aspect:
    """
    Definition of a standard AGENTESE aspect.

    Aspects are the "verbs" in AGENTESE grammar. Each aspect
    has a category, optional archetype requirements, and
    documentation.
    """

    name: str
    category: AspectCategory
    description: str = ""
    requires_archetype: tuple[str, ...] = ()  # Empty = available to all
    side_effects: bool = False  # Whether invocation changes state


# === Standard Aspects Registry ===

# Core aspects available to all observers (from spec §2.3)
CORE_ASPECTS = (
    Aspect("manifest", AspectCategory.PERCEPTION, "Collapse to observer's view"),
    Aspect("witness", AspectCategory.PERCEPTION, "Show history via N-gent"),
    Aspect("affordances", AspectCategory.INTROSPECTION, "List available verbs"),
)

# Aspect taxonomy (from spec Part IV, §4.2)
STANDARD_ASPECTS: dict[str, Aspect] = {
    # Perception
    "manifest": Aspect("manifest", AspectCategory.PERCEPTION, "Collapse to perception"),
    "witness": Aspect("witness", AspectCategory.PERCEPTION, "Show me history"),
    "sense": Aspect("sense", AspectCategory.PERCEPTION, "Raw perception"),
    "map": Aspect("map", AspectCategory.PERCEPTION, "Spatial view"),
    # Mutation
    "transform": Aspect(
        "transform", AspectCategory.MUTATION, "Change state", side_effects=True
    ),
    "renovate": Aspect(
        "renovate",
        AspectCategory.MUTATION,
        "Architectural change",
        requires_archetype=("architect",),
        side_effects=True,
    ),
    "evolve": Aspect(
        "evolve", AspectCategory.MUTATION, "Evolutionary change", side_effects=True
    ),
    "repair": Aspect(
        "repair", AspectCategory.MUTATION, "Fix damage", side_effects=True
    ),
    # Composition
    "compose": Aspect("compose", AspectCategory.COMPOSITION, "Combine entities"),
    "merge": Aspect("merge", AspectCategory.COMPOSITION, "Merge entities"),
    "split": Aspect("split", AspectCategory.COMPOSITION, "Divide entity"),
    "relate": Aspect("relate", AspectCategory.COMPOSITION, "Find connections"),
    "lens": Aspect("lens", AspectCategory.COMPOSITION, "Get composable agent"),
    # Introspection
    "affordances": Aspect(
        "affordances", AspectCategory.INTROSPECTION, "What can I do?"
    ),
    "constraints": Aspect(
        "constraints", AspectCategory.INTROSPECTION, "What limits me?"
    ),
    "lineage": Aspect(
        "lineage", AspectCategory.INTROSPECTION, "Where did I come from?"
    ),
    # Generation
    "define": Aspect(
        "define", AspectCategory.GENERATION, "Create concept", side_effects=True
    ),
    "spawn": Aspect(
        "spawn", AspectCategory.GENERATION, "Create child", side_effects=True
    ),
    "fork": Aspect(
        "fork", AspectCategory.GENERATION, "Create variant", side_effects=True
    ),
    "dream": Aspect(
        "dream", AspectCategory.GENERATION, "Generate from void", side_effects=True
    ),
    # Entropy (void.* only)
    "sip": Aspect("sip", AspectCategory.ENTROPY, "Draw from entropy"),
    "pour": Aspect("pour", AspectCategory.ENTROPY, "Return entropy"),
    "tithe": Aspect("tithe", AspectCategory.ENTROPY, "Pay for order"),
    "thank": Aspect("thank", AspectCategory.ENTROPY, "Express gratitude"),
    # Concept-specific
    "refine": Aspect(
        "refine",
        AspectCategory.GENERATION,
        "Dialectical challenge",
        requires_archetype=("philosopher", "scientist"),
    ),
    "dialectic": Aspect(
        "dialectic",
        AspectCategory.GENERATION,
        "Thesis/antithesis/synthesis",
        requires_archetype=("philosopher",),
    ),
    "synthesize": Aspect(
        "synthesize",
        AspectCategory.GENERATION,
        "Combine concepts",
        requires_archetype=("philosopher", "scientist"),
    ),
    "critique": Aspect(
        "critique",
        AspectCategory.GENERATION,
        "Challenge definition",
        requires_archetype=("philosopher",),
    ),
    # Archetype-specific world aspects
    "measure": Aspect(
        "measure",
        AspectCategory.PERCEPTION,
        "Precise measurement",
        requires_archetype=("architect", "scientist"),
    ),
    "blueprint": Aspect(
        "blueprint",
        AspectCategory.PERCEPTION,
        "Technical drawing",
        requires_archetype=("architect",),
    ),
    "demolish": Aspect(
        "demolish",
        AspectCategory.MUTATION,
        "Destroy structure",
        requires_archetype=("architect",),
        side_effects=True,
    ),
    "design": Aspect(
        "design",
        AspectCategory.GENERATION,
        "Create design",
        requires_archetype=("architect",),
        side_effects=True,
    ),
    "describe": Aspect(
        "describe",
        AspectCategory.PERCEPTION,
        "Poetic description",
        requires_archetype=("poet",),
    ),
    "metaphorize": Aspect(
        "metaphorize",
        AspectCategory.GENERATION,
        "Create metaphor",
        requires_archetype=("poet",),
        side_effects=True,
    ),
    "inhabit": Aspect(
        "inhabit",
        AspectCategory.MUTATION,
        "Enter space",
        requires_archetype=("poet", "inhabitant"),
    ),
    "contemplate": Aspect(
        "contemplate",
        AspectCategory.PERCEPTION,
        "Deep observation",
        requires_archetype=("poet",),
    ),
    "appraise": Aspect(
        "appraise",
        AspectCategory.PERCEPTION,
        "Economic valuation",
        requires_archetype=("economist",),
    ),
    "forecast": Aspect(
        "forecast",
        AspectCategory.PERCEPTION,
        "Predict future",
        requires_archetype=("economist", "scientist"),
    ),
    "compare": Aspect(
        "compare",
        AspectCategory.PERCEPTION,
        "Comparative analysis",
        requires_archetype=("economist",),
    ),
    "trade": Aspect(
        "trade",
        AspectCategory.MUTATION,
        "Exchange value",
        requires_archetype=("economist",),
        side_effects=True,
    ),
    "analyze": Aspect(
        "analyze",
        AspectCategory.PERCEPTION,
        "Scientific analysis",
        requires_archetype=("scientist",),
    ),
    "experiment": Aspect(
        "experiment",
        AspectCategory.MUTATION,
        "Run experiment",
        requires_archetype=("scientist",),
        side_effects=True,
    ),
    "hypothesize": Aspect(
        "hypothesize",
        AspectCategory.GENERATION,
        "Form hypothesis",
        requires_archetype=("scientist",),
    ),
    "validate": Aspect(
        "validate",
        AspectCategory.MUTATION,
        "Test hypothesis",
        requires_archetype=("scientist",),
        side_effects=True,
    ),
    # Developer aspects
    "build": Aspect(
        "build",
        AspectCategory.MUTATION,
        "Build artifact",
        requires_archetype=("developer",),
        side_effects=True,
    ),
    "deploy": Aspect(
        "deploy",
        AspectCategory.MUTATION,
        "Deploy artifact",
        requires_archetype=("developer",),
        side_effects=True,
    ),
    "debug": Aspect(
        "debug",
        AspectCategory.PERCEPTION,
        "Debug issue",
        requires_archetype=("developer",),
    ),
    "test": Aspect(
        "test",
        AspectCategory.MUTATION,
        "Run tests",
        requires_archetype=("developer",),
        side_effects=True,
    ),
    "refactor": Aspect(
        "refactor",
        AspectCategory.MUTATION,
        "Restructure code",
        requires_archetype=("developer",),
        side_effects=True,
    ),
    # Admin aspects
    "configure": Aspect(
        "configure",
        AspectCategory.MUTATION,
        "Set configuration",
        requires_archetype=("admin",),
        side_effects=True,
    ),
    "monitor": Aspect(
        "monitor",
        AspectCategory.PERCEPTION,
        "Observe metrics",
        requires_archetype=("admin",),
    ),
    "audit": Aspect(
        "audit", AspectCategory.PERCEPTION, "Review logs", requires_archetype=("admin",)
    ),
    "provision": Aspect(
        "provision",
        AspectCategory.GENERATION,
        "Create resources",
        requires_archetype=("admin",),
        side_effects=True,
    ),
    # Memory aspects (self.*)
    "consolidate": Aspect(
        "consolidate",
        AspectCategory.MUTATION,
        "Hypnagogic cycle",
        side_effects=True,
    ),
    "prune": Aspect(
        "prune", AspectCategory.MUTATION, "Garbage collect", side_effects=True
    ),
    "checkpoint": Aspect(
        "checkpoint", AspectCategory.GENERATION, "Snapshot state", side_effects=True
    ),
    "recall": Aspect("recall", AspectCategory.PERCEPTION, "Retrieve memory"),
    "acquire": Aspect(
        "acquire", AspectCategory.MUTATION, "Gain capability", side_effects=True
    ),
    "release": Aspect(
        "release", AspectCategory.MUTATION, "Release capability", side_effects=True
    ),
    # Time aspects
    "project": Aspect("project", AspectCategory.PERCEPTION, "View past state"),
    "defer": Aspect(
        "defer", AspectCategory.GENERATION, "Schedule future action", side_effects=True
    ),
    "cancel": Aspect(
        "cancel", AspectCategory.MUTATION, "Cancel scheduled action", side_effects=True
    ),
    "query": Aspect("query", AspectCategory.PERCEPTION, "Query traces"),
    "simulate": Aspect("simulate", AspectCategory.GENERATION, "Run simulation"),
}


# === Archetype Affordance Mappings ===

# Standard archetype → additional affordances (beyond core)
ARCHETYPE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    # Technical archetypes
    "architect": (
        "renovate",
        "measure",
        "blueprint",
        "demolish",
        "design",
        "define",
        "relate",
    ),
    "developer": (
        "build",
        "deploy",
        "debug",
        "test",
        "refactor",
        "define",
    ),
    "scientist": (
        "analyze",
        "measure",
        "experiment",
        "hypothesize",
        "validate",
        "forecast",
        "refine",
    ),
    "admin": (
        "configure",
        "monitor",
        "audit",
        "provision",
    ),
    # Creative archetypes
    "poet": (
        "describe",
        "metaphorize",
        "inhabit",
        "contemplate",
    ),
    "philosopher": (
        "refine",
        "dialectic",
        "synthesize",
        "critique",
        "relate",
    ),
    # Economic archetypes
    "economist": (
        "appraise",
        "forecast",
        "compare",
        "trade",
    ),
    # User archetypes
    "inhabitant": (
        "inhabit",
        "repair",
        "transform",
    ),
    # Default (observe only)
    "default": (),
}


# === Affordance Registry ===


@dataclass
class AffordanceRegistry:
    """
    Central registry for archetype → affordances mappings.

    The registry:
    1. Stores standard archetype mappings
    2. Allows custom archetype registration
    3. Supports inheritance (archetypes can extend others)
    4. Provides affordance lookup with fallback

    Example:
        >>> registry = AffordanceRegistry()
        >>> registry.get_affordances("architect")
        ['manifest', 'witness', 'affordances', 'renovate', 'measure', ...]

        >>> registry.register("senior_architect", ("architect",), ("manage",))
        >>> registry.get_affordances("senior_architect")
        # Includes architect affordances + manage
    """

    # Archetype → additional affordances (beyond core)
    _archetypes: dict[str, tuple[str, ...]] = field(default_factory=dict)

    # Archetype inheritance (archetype → parent archetypes)
    _inheritance: dict[str, tuple[str, ...]] = field(default_factory=dict)

    # Core affordances available to all
    _core: tuple[str, ...] = ("manifest", "witness", "affordances")

    def __post_init__(self) -> None:
        """Initialize with standard archetypes."""
        for archetype, affordances in ARCHETYPE_AFFORDANCES.items():
            self._archetypes[archetype] = affordances

    def get_affordances(self, archetype: str) -> list[str]:
        """
        Get full affordance list for an archetype.

        Includes:
        1. Core affordances (all observers)
        2. Inherited affordances (from parent archetypes)
        3. Direct affordances (for this archetype)

        Args:
            archetype: The archetype name

        Returns:
            Complete list of available affordances
        """
        affordances = list(self._core)

        # Add inherited affordances
        for parent in self._inheritance.get(archetype, ()):
            parent_affordances = self._archetypes.get(parent, ())
            for aff in parent_affordances:
                if aff not in affordances:
                    affordances.append(aff)

        # Add direct affordances
        direct = self._archetypes.get(archetype, ())
        for aff in direct:
            if aff not in affordances:
                affordances.append(aff)

        return affordances

    def has_affordance(self, archetype: str, aspect: str) -> bool:
        """Check if an archetype has access to an aspect."""
        return aspect in self.get_affordances(archetype)

    def register(
        self,
        archetype: str,
        parents: tuple[str, ...] = (),
        additional: tuple[str, ...] = (),
    ) -> None:
        """
        Register a new archetype with inheritance.

        Args:
            archetype: New archetype name
            parents: Parent archetypes to inherit from
            additional: Additional affordances for this archetype
        """
        self._archetypes[archetype] = additional
        if parents:
            self._inheritance[archetype] = parents

    def extend(self, archetype: str, affordances: tuple[str, ...]) -> None:
        """
        Add affordances to an existing archetype.

        Args:
            archetype: Archetype to extend
            affordances: Additional affordances to add
        """
        existing = self._archetypes.get(archetype, ())
        self._archetypes[archetype] = existing + affordances

    def list_archetypes(self) -> list[str]:
        """List all registered archetypes."""
        return list(self._archetypes.keys())

    def get_aspect_info(self, aspect: str) -> Aspect | None:
        """Get full aspect information."""
        return STANDARD_ASPECTS.get(aspect)


# === Affordance Matcher ===


@runtime_checkable
class AffordanceMatcher(Protocol):
    """Protocol for affordance matchers."""

    def matches(self, archetype: str, aspect: str) -> bool:
        """Check if archetype can access aspect."""
        ...


@dataclass
class StandardAffordanceMatcher:
    """
    Standard affordance matcher using the registry.

    Matches based on archetype and aspect requirements.
    """

    registry: AffordanceRegistry = field(default_factory=AffordanceRegistry)

    def matches(self, archetype: str, aspect: str) -> bool:
        """Check if archetype can access aspect."""
        # Check registry first
        if self.registry.has_affordance(archetype, aspect):
            return True

        # Check aspect definition for archetype requirements
        aspect_info = STANDARD_ASPECTS.get(aspect)
        if aspect_info and not aspect_info.requires_archetype:
            return True  # Available to all

        return False


@dataclass
class CapabilityAffordanceMatcher:
    """
    Capability-based affordance matcher.

    Matches based on DNA capabilities in addition to archetype.
    """

    registry: AffordanceRegistry = field(default_factory=AffordanceRegistry)
    capability_grants: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def matches(
        self, archetype: str, aspect: str, capabilities: tuple[str, ...] = ()
    ) -> bool:
        """Check if archetype + capabilities can access aspect."""
        # Check archetype-based access
        if self.registry.has_affordance(archetype, aspect):
            return True

        # Check capability-based access
        for cap in capabilities:
            grants = self.capability_grants.get(cap, ())
            if aspect in grants:
                return True

        return False


# === Archetype DNA ===


@dataclass(frozen=True)
class ArchetypeDNA:
    """
    DNA type for archetype-based agent configuration.

    Provides:
    - archetype: Primary archetype for affordance filtering
    - capabilities: Additional capabilities that grant affordances
    - name: Agent identifier

    Example:
        >>> dna = ArchetypeDNA(
        ...     name="claude",
        ...     archetype="developer",
        ...     capabilities=("design", "test"),
        ... )
        >>> adapter = UmweltAdapter()
        >>> affordances = adapter.get_affordances(umwelt)
    """

    name: str = "agent"
    archetype: str = "default"
    capabilities: tuple[str, ...] = ()

    # Optional trait modifiers
    exploration_budget: float = 0.1  # Accursed Share allocation

    @classmethod
    def germinate(cls, **kwargs: Any) -> "ArchetypeDNA":
        """Create validated ArchetypeDNA."""
        archetype = kwargs.get("archetype", "default")
        if archetype not in ARCHETYPE_AFFORDANCES:
            # Allow unknown archetypes (custom extensions)
            pass
        return cls(**kwargs)


# === Umwelt Adapter ===


@dataclass
class UmweltAdapter:
    """
    Adapter for extracting affordance-relevant information from Umwelt.

    Bridges between the Umwelt protocol and the AffordanceRegistry.
    Handles various DNA types and extracts archetype information.

    Example:
        >>> adapter = UmweltAdapter()
        >>> meta = adapter.extract_meta(umwelt)
        >>> affordances = adapter.get_affordances(umwelt)
    """

    registry: AffordanceRegistry = field(default_factory=AffordanceRegistry)
    matcher: StandardAffordanceMatcher | None = None

    def __post_init__(self) -> None:
        if self.matcher is None:
            self.matcher = StandardAffordanceMatcher(self.registry)

    def extract_meta(self, umwelt: "Umwelt[Any, Any]") -> "AgentMeta":
        """
        Extract AgentMeta from Umwelt's DNA.

        Handles various DNA types and extracts the archetype.

        Args:
            umwelt: The Umwelt to extract from

        Returns:
            AgentMeta with archetype information
        """
        from .node import AgentMeta

        dna = umwelt.dna

        # Extract archetype from DNA
        name = getattr(dna, "name", "unknown")
        archetype = getattr(dna, "archetype", "default")
        capabilities = getattr(dna, "capabilities", ())

        return AgentMeta(name=name, archetype=archetype, capabilities=capabilities)

    def get_affordances(self, umwelt: "Umwelt[Any, Any]") -> list[str]:
        """
        Get full affordance list for an Umwelt.

        Args:
            umwelt: The Umwelt to get affordances for

        Returns:
            List of available affordances
        """
        meta = self.extract_meta(umwelt)
        return self.registry.get_affordances(meta.archetype)

    def can_invoke(self, umwelt: "Umwelt[Any, Any]", aspect: str) -> bool:
        """
        Check if the Umwelt's observer can invoke an aspect.

        Args:
            umwelt: The Umwelt to check
            aspect: The aspect to check

        Returns:
            True if the observer can invoke the aspect
        """
        meta = self.extract_meta(umwelt)
        assert self.matcher is not None
        return self.matcher.matches(meta.archetype, aspect)

    def filter_affordances(
        self,
        umwelt: "Umwelt[Any, Any]",
        available: list[str],
    ) -> list[str]:
        """
        Filter a list of affordances to those accessible by the observer.

        Args:
            umwelt: The Umwelt to filter for
            available: List of potentially available affordances

        Returns:
            Filtered list of accessible affordances
        """
        meta = self.extract_meta(umwelt)
        allowed = self.registry.get_affordances(meta.archetype)
        return [a for a in available if a in allowed]


# === Context-Specific Affordance Sets ===


@dataclass
class ContextAffordanceSet:
    """
    Affordance set for a specific context (world, self, concept, void, time).

    Each context has:
    - Base affordances available to all
    - Archetype-specific affordances
    - Holon-specific affordances (e.g., world.house has different affordances than world.document)
    """

    context: str
    base: tuple[str, ...] = ("manifest", "witness", "affordances")
    archetype_map: dict[str, tuple[str, ...]] = field(default_factory=dict)
    holon_map: dict[str, dict[str, tuple[str, ...]]] = field(default_factory=dict)

    def get_for_archetype(self, archetype: str, holon: str | None = None) -> list[str]:
        """
        Get affordances for an archetype in this context.

        Args:
            archetype: The archetype
            holon: Optional specific holon (e.g., "house" in "world.house")

        Returns:
            List of available affordances
        """
        result = list(self.base)

        # Add archetype-specific affordances
        archetype_affordances = self.archetype_map.get(archetype, ())
        result.extend(archetype_affordances)

        # Add holon-specific affordances if applicable
        if holon and holon in self.holon_map:
            holon_affordances = self.holon_map[holon].get(archetype, ())
            result.extend(holon_affordances)

        return list(dict.fromkeys(result))  # Remove duplicates, preserve order


# Pre-configured context affordance sets
WORLD_AFFORDANCE_SET = ContextAffordanceSet(
    context="world",
    base=("manifest", "witness", "affordances", "define", "relate", "transform"),
    archetype_map=ARCHETYPE_AFFORDANCES,
)

SELF_AFFORDANCE_SET = ContextAffordanceSet(
    context="self",
    base=("manifest", "witness", "affordances"),
    archetype_map={
        "default": ("consolidate", "prune", "checkpoint", "recall"),
    },
)

CONCEPT_AFFORDANCE_SET = ContextAffordanceSet(
    context="concept",
    base=("manifest", "witness", "affordances", "relate", "define"),
    archetype_map={
        "philosopher": ("refine", "dialectic", "synthesize", "critique"),
        "scientist": ("hypothesize", "validate", "refine"),
        "default": ("refine",),
    },
)

VOID_AFFORDANCE_SET = ContextAffordanceSet(
    context="void",
    base=("sip", "pour", "tithe", "thank", "witness"),
    archetype_map={},  # Void is available equally to all
)

TIME_AFFORDANCE_SET = ContextAffordanceSet(
    context="time",
    base=("manifest", "witness", "affordances"),
    archetype_map={
        "default": ("project", "defer", "cancel", "query", "simulate"),
    },
)


# === Factory Functions ===


def create_affordance_registry() -> AffordanceRegistry:
    """Create a standard affordance registry with all archetypes."""
    return AffordanceRegistry()


def create_umwelt_adapter(registry: AffordanceRegistry | None = None) -> UmweltAdapter:
    """Create a UmweltAdapter with optional custom registry."""
    if registry is None:
        registry = AffordanceRegistry()
    return UmweltAdapter(registry=registry)


def get_context_affordance_set(context: str) -> ContextAffordanceSet:
    """Get the pre-configured affordance set for a context."""
    sets = {
        "world": WORLD_AFFORDANCE_SET,
        "self": SELF_AFFORDANCE_SET,
        "concept": CONCEPT_AFFORDANCE_SET,
        "void": VOID_AFFORDANCE_SET,
        "time": TIME_AFFORDANCE_SET,
    }
    return sets.get(context, WORLD_AFFORDANCE_SET)


__all__ = [
    # Enums and types
    "AspectCategory",
    "Aspect",
    # Constants
    "CORE_ASPECTS",
    "STANDARD_ASPECTS",
    "ARCHETYPE_AFFORDANCES",
    # Registry
    "AffordanceRegistry",
    "create_affordance_registry",
    # Matcher
    "AffordanceMatcher",
    "StandardAffordanceMatcher",
    "CapabilityAffordanceMatcher",
    # DNA
    "ArchetypeDNA",
    # Adapter
    "UmweltAdapter",
    "create_umwelt_adapter",
    # Context sets
    "ContextAffordanceSet",
    "WORLD_AFFORDANCE_SET",
    "SELF_AFFORDANCE_SET",
    "CONCEPT_AFFORDANCE_SET",
    "VOID_AFFORDANCE_SET",
    "TIME_AFFORDANCE_SET",
    "get_context_affordance_set",
]
