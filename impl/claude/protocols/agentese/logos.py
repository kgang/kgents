"""
AGENTESE Logos Resolver

The bridge between String Theory and Agent Reality.

The Logos is a Functor that lifts string paths into Agent interactions:
    logos.resolve("world.house") -> LogosNode
    logos.lift("world.house.manifest") -> Agent[Umwelt, Renderable]
    logos.invoke("world.house.manifest", observer) -> Renderable

CRITICAL: There is no view from nowhere. All operations require an observer.

Phase 4 Additions:
    - JIT compilation from spec files via MetaArchitect
    - define_concept() for autopoiesis (creating new entities)
    - promote_concept() for graduating JIT nodes to permanent implementations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

from .contexts import (
    VALID_CONTEXTS,
    create_context_resolvers,
)
from .exceptions import (
    AffordanceError,
    ObserverRequiredError,
    PathNotFoundError,
    PathSyntaxError,
    TastefulnessError,
)
from .node import (
    AgentMeta,
    AspectAgent,
    BasicRendering,
    JITLogosNode,
    LogosNode,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from bootstrap.types import Agent


# === Composed Path ===


@dataclass
class ComposedPath:
    """
    A composition of AGENTESE paths.

    Category Laws preserved:
    - Identity: Id >> path == path == path >> Id
    - Associativity: (a >> b) >> c == a >> (b >> c)

    Phase 5 Enhancements:
    - enforce_minimal_output: Check returns are single logical units
    - verify_laws: Runtime category law verification
    - lift_all: Get all morphisms as composable agents
    """

    paths: list[str]
    logos: "Logos"
    _enforce_minimal_output: bool = True

    async def invoke(
        self,
        observer: "Umwelt[Any, Any]",
        initial_input: Any = None,
    ) -> Any:
        """
        Execute composition as pipeline.

        Each path is invoked in sequence, passing the result
        of the previous path as the input kwarg.

        Args:
            observer: The observer's Umwelt (REQUIRED)
            initial_input: Optional initial value for the pipeline

        Returns:
            Final result after all paths executed
        """
        from .laws import enforce_minimal_output as check_output

        current = initial_input
        for path in self.paths:
            current = await self.logos.invoke(path, observer, input=current)
            # Enforce Minimal Output Principle (Phase 5)
            if self._enforce_minimal_output:
                current = check_output(current, path)
        return current

    def __rshift__(self, other: "ComposedPath | str") -> "ComposedPath":
        """
        Compose with another path.

        Preserves associativity: (a >> b) >> c == a >> (b >> c)
        """
        if isinstance(other, str):
            return ComposedPath(
                self.paths + [other],
                self.logos,
                self._enforce_minimal_output,
            )
        return ComposedPath(
            self.paths + other.paths,
            self.logos,
            self._enforce_minimal_output and other._enforce_minimal_output,
        )

    def __rrshift__(self, other: str) -> "ComposedPath":
        """Allow string >> ComposedPath."""
        return ComposedPath(
            [other] + self.paths,
            self.logos,
            self._enforce_minimal_output,
        )

    @property
    def name(self) -> str:
        """Human-readable name for this composition."""
        return " >> ".join(self.paths)

    def lift_all(self) -> list["Agent[Any, Any]"]:
        """
        Get all paths as composable agents.

        Returns:
            List of Agent morphisms from lens()
        """
        return [self.logos.lift(path) for path in self.paths]

    def without_enforcement(self) -> "ComposedPath":
        """
        Create a version without Minimal Output Principle enforcement.

        Use with caution—this allows array returns which break composition.
        """
        return ComposedPath(self.paths, self.logos, False)

    def __len__(self) -> int:
        """Number of paths in composition."""
        return len(self.paths)

    def __iter__(self):
        """Iterate over paths."""
        return iter(self.paths)

    def __eq__(self, other: object) -> bool:
        """Equality based on paths."""
        if isinstance(other, ComposedPath):
            return self.paths == other.paths
        return False


# === Identity Path ===


class IdentityPath:
    """
    Identity morphism for AGENTESE paths.

    When composed with any path, returns the path unchanged:
    - Id >> path == path
    - path >> Id == path

    This is the unit element of path composition.
    """

    def __init__(self, logos: "Logos"):
        self.logos = logos

    @property
    def name(self) -> str:
        return "Id"

    async def invoke(
        self,
        observer: "Umwelt[Any, Any]",
        initial_input: Any = None,
    ) -> Any:
        """Identity returns input unchanged."""
        return initial_input

    def __rshift__(self, other: "ComposedPath | str") -> "ComposedPath":
        """Id >> path == path"""
        if isinstance(other, str):
            return ComposedPath([other], self.logos)
        return other

    def __rrshift__(self, other: "ComposedPath | str") -> "ComposedPath":
        """path >> Id == path"""
        if isinstance(other, str):
            return ComposedPath([other], self.logos)
        return other


# === Registry Protocol ===


class RegistryProtocol:
    """Protocol for L-gent registry lookup."""

    def get(self, handle: str) -> Any | None:
        """Get entry by handle, or None if not found."""
        ...

    async def register(self, entry: Any) -> None:
        """Register a new entry."""
        ...

    async def update(self, entry: Any) -> None:
        """Update an existing entry."""
        ...


# === Simple In-Memory Registry ===


@dataclass
class SimpleRegistry:
    """
    Simple in-memory registry for testing and bootstrapping.

    Will be replaced by L-gent integration in Phase 6.
    """

    _entries: dict[str, LogosNode] = field(default_factory=dict)

    def get(self, handle: str) -> LogosNode | None:
        """Get entry by handle."""
        return self._entries.get(handle)

    def register(self, handle: str, node: LogosNode) -> None:
        """Register a node."""
        self._entries[handle] = node

    def update(self, handle: str, node: LogosNode) -> None:
        """Update a node."""
        self._entries[handle] = node

    def list_handles(self, prefix: str = "") -> list[str]:
        """List all handles with optional prefix filter."""
        if not prefix:
            return list(self._entries.keys())
        return [h for h in self._entries if h.startswith(prefix)]


# === Logos Resolver ===


@dataclass
class Logos:
    """
    The bridge between String Theory and Agent Reality.

    The Logos is a Functor that lifts string paths into
    Agent interactions:

        logos.resolve("world.house") -> LogosNode
        logos.lift("world.house.manifest") -> Agent[Umwelt, Renderable]
        logos.invoke("world.house.manifest", observer) -> Renderable

    CRITICAL: There is no view from nowhere. All operations
    require an observer. `invoke()` without observer raises
    `ObserverRequiredError`.
    """

    registry: SimpleRegistry = field(default_factory=SimpleRegistry)
    spec_root: Path = field(default_factory=lambda: Path("spec"))

    # Path -> Node cache (lazy hydration)
    _cache: dict[str, LogosNode] = field(default_factory=dict)

    # JIT node registry (Phase 4: tracks nodes for promotion)
    _jit_nodes: dict[str, JITLogosNode] = field(default_factory=dict)

    # Context resolvers (Phase 2: Five Contexts)
    _context_resolvers: dict[str, Any] = field(default_factory=dict)

    # Integration points for context resolvers
    _narrator: Any = None  # N-gent for traces
    _d_gent: Any = None  # D-gent for persistence
    _b_gent: Any = None  # B-gent for budgeting
    _grammarian: Any = None  # G-gent for validation

    def __post_init__(self) -> None:
        """Initialize context resolvers if not already set."""
        if not self._context_resolvers:
            self._context_resolvers = create_context_resolvers(
                registry=self.registry,
                narrator=self._narrator,
                d_gent=self._d_gent,
                b_gent=self._b_gent,
                grammarian=self._grammarian,
            )

    def resolve(
        self, path: str, observer: "Umwelt[Any, Any] | None" = None
    ) -> LogosNode:
        """
        Resolve an AGENTESE path to a LogosNode.

        Resolution strategy:
        1. Check cache (already hydrated)
        2. Check registry (known entity)
        3. Check spec/ (generative definition—J-gent JIT)
        4. Raise PathNotFoundError with sympathetic message

        Args:
            path: AGENTESE path (e.g., "world.house")
            observer: Optional observer for affordance filtering

        Returns:
            Resolved LogosNode

        Raises:
            PathSyntaxError: If path is malformed
            PathNotFoundError: If path cannot be resolved
        """
        # Check cache
        if path in self._cache:
            return self._cache[path]

        # Parse path
        parts = path.split(".")
        if len(parts) < 2:
            raise PathSyntaxError(
                f"Path '{path}' incomplete",
                path=path,
                why="AGENTESE requires at least: <context>.<holon>",
            )

        context, holon = parts[0], parts[1]
        rest = parts[2:]

        # Validate context
        if context not in VALID_CONTEXTS:
            raise PathNotFoundError(
                f"Unknown context: '{context}'",
                path=path,
                available=list(VALID_CONTEXTS),
                why=f"'{context}' is not a valid AGENTESE context",
                suggestion="Valid contexts: world, self, concept, void, time",
            )

        # Resolve by context
        node = self._resolve_context(context, holon, rest)

        # Cache and return
        self._cache[path] = node
        return node

    def lift(self, path: str) -> "Agent[Any, Any]":
        """
        Convert a handle into a composable Agent.

        The returned agent can be composed with >> operator.

        Args:
            path: Full AGENTESE path including aspect

        Returns:
            Composable Agent morphism

        Raises:
            PathSyntaxError: If path doesn't include aspect
        """
        parts = path.split(".")
        if len(parts) < 3:
            raise PathSyntaxError(
                f"lift() requires aspect: {path}",
                path=path,
                why="lift() needs: <context>.<holon>.<aspect>",
                suggestion="Example: logos.lift('world.house.manifest')",
            )

        node_path = ".".join(parts[:-1])
        aspect = parts[-1]

        node = self.resolve(node_path)
        return node.lens(aspect)

    async def invoke(
        self,
        path: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Invoke an AGENTESE path with aspect.

        CRITICAL: Observer is REQUIRED. No view from nowhere.

        Example:
            logos.invoke("world.house.manifest", architect_umwelt)
            logos.invoke("concept.justice.refine", philosopher_umwelt)

        Args:
            path: Full AGENTESE path including aspect
            observer: The observer's Umwelt (REQUIRED)
            **kwargs: Aspect-specific arguments

        Returns:
            Aspect-specific result

        Raises:
            ObserverRequiredError: If observer is None
            PathSyntaxError: If path doesn't include aspect
            AffordanceError: If observer lacks access to aspect
        """
        if observer is None:
            raise ObserverRequiredError()

        parts = path.split(".")
        if len(parts) < 3:
            raise PathSyntaxError(
                f"Path must include aspect: '{path}'",
                path=path,
                why="invoke() needs: <context>.<holon>.<aspect>",
            )

        node_path = ".".join(parts[:-1])
        aspect = parts[-1]

        node = self.resolve(node_path)

        # Get AgentMeta from observer's DNA
        meta = self._umwelt_to_meta(observer)

        # Check affordances (Ethical principle)
        available = node.affordances(meta)
        if aspect not in available:
            raise AffordanceError(
                f"Aspect '{aspect}' not available to {meta.archetype}",
                aspect=aspect,
                observer_archetype=meta.archetype,
                available=available,
            )

        return await node.invoke(aspect, observer, **kwargs)

    def compose(self, *paths: str, enforce_output: bool = True) -> ComposedPath:
        """
        Create a composed path for pipeline execution.

        Category Laws are preserved:
        - Identity: Id >> path == path == path >> Id
        - Associativity: (a >> b) >> c == a >> (b >> c)

        Example:
            pipeline = logos.compose(
                "world.document.manifest",
                "concept.summary.refine",
                "self.memory.engram",
            )
            result = await pipeline.invoke(observer)

        Args:
            *paths: AGENTESE paths to compose
            enforce_output: Whether to enforce Minimal Output Principle
                          (default: True). Set to False to allow array returns.

        Returns:
            ComposedPath that can be invoked or further composed
        """
        return ComposedPath(list(paths), self, enforce_output)

    def identity(self) -> IdentityPath:
        """
        Get the identity morphism for path composition.

        The identity satisfies:
        - Id >> path == path
        - path >> Id == path

        Example:
            id = logos.identity()
            pipeline = id >> "world.house.manifest" >> "concept.summary.refine"
            # Equivalent to just composing the two paths

        Returns:
            IdentityPath instance
        """
        return IdentityPath(self)

    def path(self, p: str) -> ComposedPath:
        """
        Create a single-path composition for chaining.

        This allows the >> operator on string paths:
            pipeline = logos.path("world.house.manifest") >> "concept.summary.refine"

        Args:
            p: AGENTESE path

        Returns:
            ComposedPath with single path
        """
        return ComposedPath([p], self)

    def register(self, handle: str, node: LogosNode) -> None:
        """
        Register a node in the registry.

        Used for adding pre-built nodes or promoted JIT nodes.
        """
        self.registry.register(handle, node)
        # Also cache for fast lookup
        self._cache[handle] = node

    # === Internal Resolution Methods ===

    def _resolve_context(
        self,
        context: str,
        holon: str,
        rest: list[str],
    ) -> LogosNode:
        """Resolve by context type using Phase 2 context resolvers."""
        handle = f"{context}.{holon}"

        # Phase 2: Use context-specific resolvers
        if context in self._context_resolvers:
            resolver = self._context_resolvers[context]
            # All Phase 2 resolvers implement resolve(holon, rest)
            if hasattr(resolver, "resolve"):
                return resolver.resolve(holon, rest)

        # Fallback: Check registry directly
        node = self.registry.get(handle)
        if node:
            return node

        # Check spec for JIT generation
        spec_path = self.spec_root / context / f"{holon}.md"
        if spec_path.exists():
            return self._generate_from_spec(spec_path, handle)

        # Similar handles for suggestion
        similar = self.registry.list_handles(f"{context}.")

        # Sympathetic error
        raise PathNotFoundError(
            f"'{handle}' not found",
            path=handle,
            available=similar[:5],
            why=f"No implementation in registry, no spec at {spec_path}",
            suggestion=f"Create {spec_path} for auto-generation, or use {handle}.define",
        )

    def _generate_from_spec(self, spec_path: Path, handle: str) -> LogosNode:
        """
        Generate a LogosNode from a spec file via J-gent JIT.

        The Generative Principle: Specs are compressed wisdom.
        Implementations can be derived mechanically.

        Phase 4 Implementation:
        1. Parse spec file to extract affordances, manifest behavior
        2. Generate Python source via SpecCompiler
        3. Wrap in JITLogosNode with usage tracking
        """
        from .jit import JITCompiler

        compiler = JITCompiler(spec_root=self.spec_root)

        try:
            jit_node = compiler.compile_from_path(spec_path)
            # Track in JIT registry for potential promotion
            self._jit_nodes[handle] = jit_node
            return jit_node
        except TastefulnessError:
            # Re-raise tasteful errors as-is
            raise
        except Exception:
            # Fallback to minimal JIT node on compilation failure
            spec_content = spec_path.read_text()
            return JITLogosNode(
                handle=handle,
                source="",
                spec=spec_content,
            )

    # === Phase 4: Autopoiesis (define aspect) ===

    async def define_concept(
        self,
        handle: str,
        spec: str,
        observer: "Umwelt[Any, Any]",
    ) -> LogosNode:
        """
        Create a new concept via autopoiesis.

        The Generative Principle: Specs are compressed wisdom.
        New entities can be created from well-formed specs.

        Args:
            handle: The AGENTESE path for the new entity (e.g., "world.garden")
            spec: The spec content (markdown with YAML front matter)
            observer: The observer creating this entity

        Returns:
            The newly created LogosNode

        Raises:
            AffordanceError: If observer lacks 'define' affordance
            TastefulnessError: If spec is invalid
            PathSyntaxError: If handle is malformed
        """
        from .jit import JITCompiler

        # Validate handle syntax
        parts = handle.split(".")
        if len(parts) < 2:
            raise PathSyntaxError(
                f"Handle '{handle}' incomplete",
                path=handle,
                why="Handles must be: <context>.<entity>",
            )

        context = parts[0]
        if context not in VALID_CONTEXTS:
            raise PathSyntaxError(
                f"Invalid context: '{context}'",
                path=handle,
                why=f"'{context}' is not a valid AGENTESE context",
                suggestion="Valid contexts: world, self, concept, void, time",
            )

        # Check observer affordance
        meta = self._umwelt_to_meta(observer)

        # 'define' requires special permission (architect, developer, or explicit capability)
        can_define = (
            meta.archetype in ("architect", "developer", "admin")
            or "define" in meta.capabilities
        )
        if not can_define:
            raise AffordanceError(
                f"Observer '{meta.name}' cannot define new entities",
                aspect="define",
                observer_archetype=meta.archetype,
                available=["manifest", "witness", "affordances"],
            )

        # Validate spec via G-gent if available
        if self._grammarian is not None:
            # G-gent validation would go here
            pass

        # Compile spec
        compiler = JITCompiler(spec_root=self.spec_root)
        jit_node = compiler.compile_from_content(spec)

        # Override handle if spec has different one
        jit_node = JITLogosNode(
            handle=handle,
            source=jit_node.source,
            spec=spec,
        )

        # Register in cache and JIT registry
        self._cache[handle] = jit_node
        self._jit_nodes[handle] = jit_node

        # Register in main registry (as DRAFT status)
        self.registry.register(handle, jit_node)

        return jit_node

    async def promote_concept(
        self,
        handle: str,
        threshold: int = 100,
        success_threshold: float = 0.8,
    ) -> "PromotionResult":
        """
        Promote a JIT node to permanent implementation.

        A JIT node is promoted when:
        1. usage_count >= threshold
        2. success_rate >= success_threshold

        Promotion writes the source to impl/ and updates L-gent status.

        Args:
            handle: The AGENTESE path to promote
            threshold: Minimum usage count required
            success_threshold: Minimum success rate required

        Returns:
            PromotionResult with success status and details
        """
        from .jit import JITPromoter, PromotionResult

        # Check if handle exists as JIT node
        if handle not in self._jit_nodes:
            return PromotionResult(
                success=False,
                handle=handle,
                reason=f"'{handle}' is not a JIT node",
            )

        jit_node = self._jit_nodes[handle]

        # Promote
        promoter = JITPromoter(
            threshold=threshold,
            success_threshold=success_threshold,
        )
        result = promoter.promote(jit_node, self.registry)

        # Clear from JIT registry if promoted
        if result.success:
            del self._jit_nodes[handle]

        return result

    def get_jit_status(self, handle: str) -> dict[str, Any] | None:
        """
        Get JIT node status for a handle.

        Returns:
            Dict with usage_count, success_count, success_rate, should_promote
            or None if not a JIT node
        """
        if handle not in self._jit_nodes:
            return None

        node = self._jit_nodes[handle]
        return {
            "handle": handle,
            "usage_count": node.usage_count,
            "success_count": node.success_count,
            "success_rate": node.success_rate,
            "should_promote": node.should_promote(),
        }

    def list_jit_nodes(self) -> list[dict[str, Any]]:
        """List all JIT nodes with their status."""
        return [
            self.get_jit_status(handle)
            for handle in self._jit_nodes
            if self.get_jit_status(handle) is not None
        ]

    def _umwelt_to_meta(self, umwelt: "Umwelt[Any, Any]") -> AgentMeta:
        """Extract AgentMeta from Umwelt's DNA."""
        dna = umwelt.dna
        name = getattr(dna, "name", "unknown")
        archetype = getattr(dna, "archetype", "default")
        capabilities = getattr(dna, "capabilities", ())
        return AgentMeta(name=name, archetype=archetype, capabilities=capabilities)

    # === Convenience Methods ===

    def list_handles(self, context: str | None = None) -> list[str]:
        """List all registered handles, optionally filtered by context."""
        if context:
            return self.registry.list_handles(f"{context}.")
        return self.registry.list_handles()

    def is_resolved(self, path: str) -> bool:
        """Check if a path is already cached."""
        return path in self._cache

    def clear_cache(self) -> None:
        """Clear the resolution cache."""
        self._cache.clear()


# === Factory Functions ===


def create_logos(
    spec_root: Path | str = "spec",
    registry: SimpleRegistry | None = None,
    narrator: Any = None,
    d_gent: Any = None,
    b_gent: Any = None,
    grammarian: Any = None,
) -> Logos:
    """
    Create a Logos resolver with standard configuration.

    Args:
        spec_root: Path to spec directory for JIT generation
        registry: Optional pre-populated registry
        narrator: N-gent for narrative traces
        d_gent: D-gent for persistence and temporal projection
        b_gent: B-gent for budgeting and forecasting
        grammarian: G-gent for grammar validation

    Returns:
        Configured Logos instance with Phase 2 context resolvers
    """
    logos = Logos(
        registry=registry or SimpleRegistry(),
        spec_root=Path(spec_root),
        _narrator=narrator,
        _d_gent=d_gent,
        _b_gent=b_gent,
        _grammarian=grammarian,
    )
    logos.__post_init__()  # Initialize context resolvers
    return logos


# === Example Nodes for Testing ===


@dataclass
class PlaceholderNode:
    """
    Placeholder node for testing resolver behavior.

    Provides basic affordances and manifest behavior.
    """

    handle: str
    archetype_affordances: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def affordances(self, observer: AgentMeta) -> list[str]:
        """Return affordances based on archetype."""
        base = ["manifest", "witness", "affordances"]
        extra = self.archetype_affordances.get(observer.archetype, ())
        return base + list(extra)

    def lens(self, aspect: str) -> "Agent[Any, Any]":
        """Return aspect agent."""
        return AspectAgent(self, aspect)

    async def manifest(self, observer: "Umwelt[Any, Any]") -> BasicRendering:
        """Return basic rendering."""
        return BasicRendering(
            summary=f"Placeholder: {self.handle}",
            content="This is a placeholder node for testing.",
        )

    async def invoke(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Invoke aspect."""
        if aspect == "manifest":
            return await self.manifest(observer)
        if aspect == "affordances":
            meta = AgentMeta(
                name=getattr(observer.dna, "name", "unknown"),
                archetype=getattr(observer.dna, "archetype", "default"),
            )
            return self.affordances(meta)
        return {"aspect": aspect, "kwargs": kwargs}
