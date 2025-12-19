"""
AGENTESE Phase 6: Integration Layer

Wires AGENTESE into the existing kgents ecosystem:

1. Umwelt Integration - All invoke() calls receive observer Umwelt, DNA archetype determines affordances
2. Membrane Integration - Map CLI commands to AGENTESE paths
3. L-gent Integration - resolve() checks L-gent registry, define_concept() registers there
4. G-gent Integration - Create AGENTESE grammar with BNF for path syntax

Key Principle: Graceful Degradation
All integrations are optional. AGENTESE works standalone, but gains
capabilities when other agents are available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from .affordances import (
    AffordanceRegistry,
    ArchetypeDNA,
    UmweltAdapter,
    create_affordance_registry,
)
from .exceptions import (
    PathNotFoundError,
    PathSyntaxError,
)
from .node import AgentMeta, LogosNode

if TYPE_CHECKING:
    from agents.g.types import Tongue
    from agents.l.catalog import CatalogEntry, EntityType
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Part 1: Umwelt Integration
# =============================================================================


@dataclass
class UmweltIntegration:
    """
    Integration layer between AGENTESE and Umwelt protocol.

    The key insight: DNA archetype determines affordances.
    Every invoke() call requires an observer Umwelt, and the
    observer's DNA.archetype determines what aspects are available.

    Example:
        >>> integration = UmweltIntegration()
        >>> meta = integration.extract_meta(architect_umwelt)
        >>> meta.archetype
        'architect'
        >>> integration.get_affordances(architect_umwelt)
        ['manifest', 'witness', 'affordances', 'renovate', 'measure', 'blueprint', ...]
    """

    adapter: UmweltAdapter = field(default_factory=lambda: UmweltAdapter())
    registry: AffordanceRegistry = field(default_factory=create_affordance_registry)

    def extract_meta(self, umwelt: "Umwelt[Any, Any]") -> AgentMeta:
        """
        Extract AgentMeta from Umwelt's DNA.

        Handles various DNA types:
        - ArchetypeDNA (native AGENTESE DNA)
        - Any DNA with archetype/name/capabilities attributes
        - Falls back to 'default' archetype if not found
        """
        dna = umwelt.dna

        # Native ArchetypeDNA
        if isinstance(dna, ArchetypeDNA):
            return AgentMeta(
                name=dna.name,
                archetype=dna.archetype,
                capabilities=dna.capabilities,
            )

        # Duck-typed DNA
        name = getattr(dna, "name", "unknown")
        archetype = getattr(dna, "archetype", "default")
        capabilities = getattr(dna, "capabilities", ())

        return AgentMeta(name=name, archetype=archetype, capabilities=capabilities)

    def get_affordances(self, umwelt: "Umwelt[Any, Any]") -> list[str]:
        """
        Get full affordance list for an Umwelt observer.

        Returns affordances based on:
        1. Core affordances (all observers)
        2. Archetype-specific affordances
        3. Capability-based grants
        """
        return self.adapter.get_affordances(umwelt)

    def can_invoke(self, umwelt: "Umwelt[Any, Any]", aspect: str) -> bool:
        """Check if observer can invoke an aspect."""
        return self.adapter.can_invoke(umwelt, aspect)

    def create_observer_umwelt(
        self,
        archetype: str,
        name: str = "agent",
        capabilities: tuple[str, ...] = (),
        **extra_dna_fields: Any,
    ) -> "Umwelt[Any, ArchetypeDNA]":
        """
        Create a minimal Umwelt for AGENTESE observation.

        This is a convenience method for creating observers
        without the full Projector/DataAgent infrastructure.

        Args:
            archetype: Observer archetype (architect, poet, scientist, etc.)
            name: Observer name
            capabilities: Additional capabilities
            **extra_dna_fields: Extra fields for ArchetypeDNA

        Returns:
            Minimal Umwelt suitable for AGENTESE invocation
        """
        from agents.d.lens import identity_lens
        from bootstrap.umwelt import Umwelt

        dna = ArchetypeDNA(
            name=name,
            archetype=archetype,
            capabilities=capabilities,
            **extra_dna_fields,
        )

        return Umwelt(
            state=identity_lens(),
            dna=dna,
            gravity=(),
            _storage=None,  # No storage for minimal umwelt
        )


def create_umwelt_integration() -> UmweltIntegration:
    """Create a standard UmweltIntegration."""
    return UmweltIntegration()


# =============================================================================
# Part 2: Membrane Integration
# =============================================================================


# Membrane command → AGENTESE path mapping (from spec §9.2)
MEMBRANE_AGENTESE_MAP: dict[str, str] = {
    # Perception verbs
    "observe": "world.project.manifest",
    "sense": "world.project.sense",
    "map": "world.project.map",
    # Trace verb
    "trace": "time.trace.witness",  # Takes topic as arg
    # Memory verbs
    "dream": "self.memory.consolidate",
    "recall": "self.memory.manifest",
    "prune": "self.memory.prune",
    # Entropy verbs
    "sip": "void.entropy.sip",
    "tithe": "void.gratitude.tithe",
    # Gesture verbs (naming voids)
    "name": "concept.void.define",  # Creates new concept from named void
    # Generation verbs
    "define": "world.{entity}.define",  # Parameterized
    "spawn": "world.{entity}.spawn",
    # Temporal verbs
    "schedule": "time.schedule.defer",
    "forecast": "time.future.forecast",
}


@dataclass
class MembraneAgenteseBridge:
    """
    Bridge between Membrane CLI commands and AGENTESE paths.

    Translates the Membrane vocabulary (observe, sense, trace, dream)
    into AGENTESE invocations. This allows the CLI to be a thin
    wrapper around the AGENTESE protocol.

    Example:
        >>> bridge = MembraneAgenteseBridge(logos)
        >>> result = await bridge.execute("observe", observer)
        # Equivalent to: logos.invoke("world.project.manifest", observer)

        >>> result = await bridge.execute("trace", observer, topic="authentication")
        # Equivalent to: logos.invoke("time.trace.witness", observer, topic="authentication")
    """

    logos: Any  # Logos resolver (avoid circular import)
    command_map: dict[str, str] = field(default_factory=lambda: MEMBRANE_AGENTESE_MAP.copy())

    async def execute(
        self,
        command: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Execute a Membrane command via AGENTESE.

        Args:
            command: Membrane command (observe, sense, trace, etc.)
            observer: Observer Umwelt
            **kwargs: Command-specific arguments

        Returns:
            AGENTESE invocation result

        Raises:
            PathNotFoundError: If command doesn't map to AGENTESE
        """
        path = self._resolve_command(command, **kwargs)
        return await self.logos.invoke(path, observer, **kwargs)

    def _resolve_command(self, command: str, **kwargs: Any) -> str:
        """
        Resolve a Membrane command to AGENTESE path.

        Handles parameterized paths like "world.{entity}.define".
        """
        if command not in self.command_map:
            similar = [c for c in self.command_map if c.startswith(command[:2])]
            raise PathNotFoundError(
                f"Unknown Membrane command: '{command}'",
                path=command,
                available=similar[:5] if similar else list(self.command_map.keys())[:5],
                why="This command doesn't have an AGENTESE mapping",
                suggestion=f"Try one of: {', '.join(list(self.command_map.keys())[:5])}",
            )

        path = self.command_map[command]

        # Handle parameterized paths
        if "{entity}" in path:
            entity = kwargs.get("entity", "unknown")
            path = path.replace("{entity}", entity)

        return path

    def register_command(self, command: str, agentese_path: str) -> None:
        """Register a new command → AGENTESE mapping."""
        self.command_map[command] = agentese_path

    def list_commands(self) -> list[tuple[str, str]]:
        """List all registered command mappings."""
        return list(self.command_map.items())

    def get_path(self, command: str) -> str | None:
        """Get AGENTESE path for a command without executing."""
        return self.command_map.get(command)


def create_membrane_bridge(logos: Any) -> MembraneAgenteseBridge:
    """Create a Membrane-AGENTESE bridge."""
    return MembraneAgenteseBridge(logos=logos)


# =============================================================================
# Part 3: L-gent Integration
# =============================================================================


@runtime_checkable
class LgentRegistryProtocol(Protocol):
    """Protocol for L-gent registry integration."""

    async def get(self, entry_id: str) -> "CatalogEntry | None":
        """Get entry by ID."""
        ...

    async def register(self, entry: "CatalogEntry") -> None:
        """Register a new entry."""
        ...

    async def record_usage(
        self,
        entry_id: str,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """Record usage of an entry."""
        ...

    async def list_by_type(self, entity_type: "EntityType") -> list["CatalogEntry"]:
        """List entries by type."""
        ...


@dataclass
class LgentIntegration:
    """
    Integration layer between AGENTESE and L-gent registry.

    The key insight: L-gent provides semantic lookup for AGENTESE paths.
    When resolve() is called, it first checks L-gent for known entities.
    When define_concept() creates a new entity, it registers in L-gent.

    Example:
        >>> integration = LgentIntegration(registry)
        >>> # resolve() first checks L-gent
        >>> entry = await integration.lookup("world.house")
        >>> if entry:
        ...     # Found in L-gent, use its metadata
        ...     node = await integration.hydrate(entry)

        >>> # define_concept() registers in L-gent
        >>> await integration.register_node(jit_node, observer="architect")
    """

    registry: LgentRegistryProtocol | None = None
    _cache: dict[str, "CatalogEntry"] = field(default_factory=dict)

    async def lookup(self, handle: str) -> "CatalogEntry | None":
        """
        Look up an AGENTESE handle in L-gent registry.

        Args:
            handle: AGENTESE path (e.g., "world.house")

        Returns:
            CatalogEntry if found, None otherwise
        """
        if self.registry is None:
            return None

        # Check cache first
        if handle in self._cache:
            return self._cache[handle]

        entry = await self.registry.get(handle)
        if entry:
            self._cache[handle] = entry
        return entry

    async def register_node(
        self,
        node: LogosNode,
        observer: str = "unknown",
        description: str = "",
        keywords: list[str] | None = None,
        status: str = "draft",
    ) -> None:
        """
        Register a LogosNode in L-gent registry.

        Called by define_concept() to persist new entities.

        Args:
            node: The LogosNode to register
            observer: Creator identifier
            description: Node description
            keywords: Search keywords
            status: Initial status (draft, active)
        """
        if self.registry is None:
            return  # Graceful degradation: no-op without registry

        # Import L-gent types (only when needed)
        from agents.l.catalog import CatalogEntry, EntityType, Status

        entry = CatalogEntry(
            id=node.handle,
            entity_type=EntityType.AGENT,
            name=node.handle.split(".")[-1],
            version="1.0.0",
            description=description or f"AGENTESE node: {node.handle}",
            keywords=keywords or [node.handle.replace(".", " ")],
            author=observer,
            forged_by="agentese.define_concept",
            forged_from=getattr(node, "spec", None),
            status=Status(status),
        )

        await self.registry.register(entry)
        self._cache[node.handle] = entry

    async def record_invocation(
        self,
        handle: str,
        success: bool,
        error: str | None = None,
    ) -> None:
        """
        Record an invocation in L-gent usage metrics.

        Called after every invoke() to track usage patterns.
        """
        if self.registry is None:
            return

        try:
            await self.registry.record_usage(handle, success, error)
        except Exception:
            pass  # Graceful degradation: don't fail on metrics

    async def list_handles(self, context: str | None = None) -> list[str]:
        """
        List all registered AGENTESE handles.

        Args:
            context: Optional context filter (world, self, concept, void, time)

        Returns:
            List of handle strings
        """
        if self.registry is None:
            return []

        from agents.l.catalog import EntityType

        entries = await self.registry.list_by_type(EntityType.AGENT)
        handles = [e.id for e in entries if e.id.count(".") >= 1]

        if context:
            handles = [h for h in handles if h.startswith(f"{context}.")]

        return handles

    def clear_cache(self) -> None:
        """Clear the entry cache."""
        self._cache.clear()


def create_lgent_integration(
    registry: LgentRegistryProtocol | None = None,
) -> LgentIntegration:
    """
    Create L-gent integration.

    Args:
        registry: Optional L-gent registry. If None, integration
                 operates in graceful degradation mode.
    """
    return LgentIntegration(registry=registry)


# =============================================================================
# Part 4: G-gent Integration
# =============================================================================


# AGENTESE Grammar (BNF)
AGENTESE_BNF = """
PATH        ::= CONTEXT "." HOLON ("." ASPECT)?
CONTEXT     ::= "world" | "self" | "concept" | "void" | "time"
HOLON       ::= IDENTIFIER
ASPECT      ::= IDENTIFIER
IDENTIFIER  ::= [a-z][a-z0-9_]*

// Examples:
// world.house.manifest
// self.memory.consolidate
// concept.justice.refine
// void.entropy.sip
// time.trace.witness
"""

# AGENTESE Grammar Constraints (for G-gent validation)
AGENTESE_CONSTRAINTS = [
    "Only five contexts allowed: world, self, concept, void, time",
    "Paths must have at least context.holon",
    "Aspect is optional but required for invoke()",
    "Identifiers must be lowercase with underscores",
    "No numeric-only identifiers",
]

# Example inputs for G-gent grammar synthesis
AGENTESE_EXAMPLES = [
    "world.house.manifest",
    "world.library.define",
    "self.memory.consolidate",
    "self.capabilities.affordances",
    "concept.justice.refine",
    "concept.fairness.relate",
    "void.entropy.sip",
    "void.gratitude.tithe",
    "time.trace.witness",
    "time.future.forecast",
]


@dataclass
class GgentIntegration:
    """
    Integration layer between AGENTESE and G-gent grammar system.

    G-gent can:
    1. Generate the AGENTESE parser from the BNF
    2. Validate paths against the grammar
    3. Synthesize new DSLs that compose with AGENTESE

    Example:
        >>> integration = GgentIntegration(grammarian)
        >>> # Validate a path
        >>> is_valid = integration.validate_path("world.house.manifest")

        >>> # Create the AGENTESE Tongue
        >>> tongue = await integration.reify_agentese_tongue()
    """

    grammarian: Any | None = None  # G-gent instance
    _tongue: "Tongue | None" = None  # Cached AGENTESE tongue

    def validate_path(self, path: str) -> tuple[bool, str | None]:
        """
        Validate an AGENTESE path against the grammar.

        Uses structural validation (doesn't require G-gent).

        Args:
            path: Path to validate

        Returns:
            (is_valid, error_message)
        """
        parts = path.split(".")

        # Check minimum length
        if len(parts) < 2:
            return False, "Path must have at least context.holon"

        # Check context
        context = parts[0]
        valid_contexts = {"world", "self", "concept", "void", "time"}
        if context not in valid_contexts:
            return (
                False,
                f"Invalid context: '{context}'. Must be one of: {valid_contexts}",
            )

        # Check identifier format
        import re

        identifier_pattern = re.compile(r"^[a-z][a-z0-9_]*$")

        for i, part in enumerate(parts):
            if not identifier_pattern.match(part):
                position = ["context", "holon", "aspect"][min(i, 2)]
                return (
                    False,
                    f"Invalid {position}: '{part}'. Must be lowercase letters, numbers, underscores.",
                )

        return True, None

    def parse_path(self, path: str) -> dict[str, str | None]:
        """
        Parse an AGENTESE path into components.

        Args:
            path: Valid AGENTESE path

        Returns:
            Dict with context, holon, aspect (aspect may be None)

        Raises:
            PathSyntaxError: If path is invalid
        """
        is_valid, error = self.validate_path(path)
        if not is_valid:
            raise PathSyntaxError(
                f"Invalid AGENTESE path: {path}",
                path=path,
                why=error or "Path doesn't match grammar",
            )

        parts = path.split(".")
        return {
            "context": parts[0],
            "holon": parts[1],
            "aspect": parts[2] if len(parts) > 2 else None,
        }

    async def reify_agentese_tongue(self) -> "Tongue":
        """
        Create the AGENTESE Tongue via G-gent.

        The Tongue is a reified DSL that can parse and validate
        AGENTESE paths, with structural guarantees.

        Returns:
            AGENTESE Tongue artifact

        Raises:
            RuntimeError: If G-gent not available
        """
        if self._tongue is not None:
            return self._tongue

        if self.grammarian is None:
            raise RuntimeError(
                "G-gent not available. Cannot reify AGENTESE tongue. "
                "Use validate_path() for basic validation without G-gent."
            )

        from agents.g.types import GrammarLevel

        self._tongue = await self.grammarian.reify(
            domain="AGENTESE Path Syntax",
            constraints=AGENTESE_CONSTRAINTS,
            level=GrammarLevel.COMMAND,
            examples=AGENTESE_EXAMPLES,
            intent="Parse and validate AGENTESE paths",
            name="AgenteseTongue",
            version="2.0.0",
        )

        return self._tongue

    def get_bnf(self) -> str:
        """Get the AGENTESE BNF grammar."""
        return AGENTESE_BNF

    def get_constraints(self) -> list[str]:
        """Get the AGENTESE grammar constraints."""
        return AGENTESE_CONSTRAINTS.copy()

    def get_examples(self) -> list[str]:
        """Get example AGENTESE paths."""
        return AGENTESE_EXAMPLES.copy()


def create_ggent_integration(
    grammarian: Any | None = None,
) -> GgentIntegration:
    """
    Create G-gent integration.

    Args:
        grammarian: Optional G-gent instance. If None, basic
                   validation still works (graceful degradation).
    """
    return GgentIntegration(grammarian=grammarian)


# =============================================================================
# Part 5: Unified Integration Factory
# =============================================================================


@dataclass
class AgentesIntegrations:
    """
    Unified container for all AGENTESE integrations.

    Provides single point of access to:
    - Umwelt integration (observer handling)
    - Membrane integration (CLI bridging)
    - L-gent integration (registry/catalog)
    - G-gent integration (grammar/validation)

    Example:
        >>> integrations = create_agentese_integrations(
        ...     lgent_registry=registry,
        ...     grammarian=g_gent,
        ... )
        >>> # All integrations available
        >>> meta = integrations.umwelt.extract_meta(observer)
        >>> path = integrations.membrane.get_path("observe")
        >>> entry = await integrations.lgent.lookup("world.house")
        >>> is_valid = integrations.ggent.validate_path("world.house.manifest")
    """

    umwelt: UmweltIntegration = field(default_factory=create_umwelt_integration)
    membrane: MembraneAgenteseBridge | None = None
    lgent: LgentIntegration = field(default_factory=create_lgent_integration)
    ggent: GgentIntegration = field(default_factory=create_ggent_integration)

    def is_fully_integrated(self) -> bool:
        """Check if all integrations are available."""
        return (
            self.membrane is not None
            and self.lgent.registry is not None
            and self.ggent.grammarian is not None
        )

    def available_integrations(self) -> list[str]:
        """List which integrations are available."""
        available = ["umwelt"]  # Always available
        if self.membrane is not None:
            available.append("membrane")
        if self.lgent.registry is not None:
            available.append("lgent")
        if self.ggent.grammarian is not None:
            available.append("ggent")
        return available


def create_agentese_integrations(
    logos: Any | None = None,
    lgent_registry: LgentRegistryProtocol | None = None,
    grammarian: Any | None = None,
) -> AgentesIntegrations:
    """
    Create unified AGENTESE integrations.

    All parameters are optional. Missing integrations operate
    in graceful degradation mode.

    Args:
        logos: Logos resolver (for Membrane bridge)
        lgent_registry: L-gent registry (for catalog integration)
        grammarian: G-gent instance (for grammar validation)

    Returns:
        AgentesIntegrations with available components
    """
    return AgentesIntegrations(
        umwelt=create_umwelt_integration(),
        membrane=MembraneAgenteseBridge(logos=logos) if logos else None,
        lgent=create_lgent_integration(lgent_registry),
        ggent=create_ggent_integration(grammarian),
    )


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Umwelt Integration
    "UmweltIntegration",
    "create_umwelt_integration",
    # Membrane Integration
    "MEMBRANE_AGENTESE_MAP",
    "MembraneAgenteseBridge",
    "create_membrane_bridge",
    # L-gent Integration
    "LgentRegistryProtocol",
    "LgentIntegration",
    "create_lgent_integration",
    # G-gent Integration
    "AGENTESE_BNF",
    "AGENTESE_CONSTRAINTS",
    "AGENTESE_EXAMPLES",
    "GgentIntegration",
    "create_ggent_integration",
    # Unified Factory
    "AgentesIntegrations",
    "create_agentese_integrations",
]
