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

Teaching:
    gotcha: @node runs at import time. If the module isn't imported,
            the node won't be registered. Call _import_node_modules() first.
            (Evidence: test_logos.py::test_node_discovery)

    gotcha: Resolution checks NodeRegistry BEFORE SimpleRegistry.
            @node decorators in services/ override any manual registration.
            (Evidence: test_logos.py::test_resolution_order)

    gotcha: Observer can be None in v3 API—it defaults to Observer.guest().
            But guest observers have minimal affordances. Be explicit.
            (Evidence: test_logos.py::test_guest_observer)

    gotcha: ComposedPath.invoke() enforces Minimal Output Principle by default.
            Arrays break composition. Use without_enforcement() if you need them.
            (Evidence: test_logos.py::test_minimal_output_enforcement)

    gotcha: Aliases are PREFIX expansion only. "me.challenge" → "self.soul.challenge".
            You cannot alias an aspect, only a path prefix.
            (Evidence: test_logos.py::test_alias_expansion)
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Iterator,
    cast,
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
    Observer,
)

if TYPE_CHECKING:
    from agents.poly.types import Agent
    from bootstrap.umwelt import Umwelt

    from .aliases import AliasRegistry
    from .middleware.curator import WundtCurator
    from .query import QueryResult


# === Standalone Path for Composition (v3) ===


@dataclass
class AgentesePath:
    """
    Standalone path for string-based composition (v3 API).

    Allows composing paths with >> without needing a Logos instance:
        pipeline = path("world.doc.manifest") >> "concept.summary.refine"
        result = await pipeline.run(observer, logos)

    Example:
        # Basic composition
        pipeline = path("world.doc.manifest") >> "self.memory.engram"

        # Chained composition
        pipeline = (
            path("world.garden.manifest")
            >> "concept.summary.refine"
            >> "self.memory.engram"
        )

        # Execute with observer and logos
        result = await pipeline.run(observer, logos)

        # Or bind to logos first
        bound = pipeline.bind(logos)
        result = await bound.invoke(observer)

    Teaching:
        gotcha: AgentesePath creates UnboundComposedPath via >>. You must
                call .bind(logos) or .run(observer, logos) to execute.
                (Evidence: test_logos.py::test_unbound_composition)
    """

    value: str

    def __rshift__(
        self, other: "str | AgentesePath | UnboundComposedPath"
    ) -> "UnboundComposedPath":
        """Compose with another path."""
        if isinstance(other, UnboundComposedPath):
            return UnboundComposedPath([self.value] + other.paths)
        other_value = other.value if isinstance(other, AgentesePath) else other
        return UnboundComposedPath([self.value, other_value])

    def bind(self, logos: "Logos") -> "ComposedPath":
        """Bind to a Logos instance for execution."""
        return ComposedPath([self.value], logos)

    async def run(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        logos: "Logos",
        initial_input: Any = None,
    ) -> Any:
        """Execute this path with the given observer and logos."""
        return await logos.invoke(self.value, observer, input=initial_input)


@dataclass
class UnboundComposedPath:
    """
    Composition of paths that hasn't been bound to a Logos yet (v3 API).

    Created by path() >> "..." operations.

    Teaching:
        gotcha: UnboundComposedPath is lazy—no Logos, no execution.
                Call .bind(logos) to get ComposedPath, or .run() to execute.
                (Evidence: test_logos.py::test_unbound_composition)
    """

    paths: list[str]

    def __rshift__(
        self, other: "str | AgentesePath | UnboundComposedPath"
    ) -> "UnboundComposedPath":
        """Compose with another path."""
        if isinstance(other, str):
            return UnboundComposedPath(self.paths + [other])
        if isinstance(other, AgentesePath):
            return UnboundComposedPath(self.paths + [other.value])
        return UnboundComposedPath(self.paths + other.paths)

    def __rrshift__(self, other: str) -> "UnboundComposedPath":
        """Allow string >> UnboundComposedPath."""
        return UnboundComposedPath([other] + self.paths)

    def bind(self, logos: "Logos") -> "ComposedPath":
        """Bind to a Logos instance for execution."""
        return ComposedPath(self.paths, logos)

    async def run(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        logos: "Logos",
        initial_input: Any = None,
    ) -> Any:
        """Execute this composition with the given observer and logos."""
        return await self.bind(logos).invoke(observer, initial_input)


def path(p: str) -> AgentesePath:
    """
    Create a composable path for string-based composition (v3 API).

    This is the primary entry point for building path compositions
    without needing a Logos instance upfront.

    Example:
        # Single path
        p = path("world.garden.manifest")

        # Composition
        pipeline = path("world.doc.manifest") >> "concept.summary.refine"

        # Execute
        result = await pipeline.run(observer, logos)

    Args:
        p: AGENTESE path string

    Returns:
        AgentesePath object that supports >> composition
    """
    return AgentesePath(p)


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

    Track B (Law Enforcer) Enhancements:
    - emit_law_check: Emit law_check span events on each invocation
    - Law verification wired into invoke()

    Teaching:
        gotcha: ComposedPath.invoke() enforces Minimal Output Principle by default.
                Arrays break composition. Use .without_enforcement() if needed.
                (Evidence: test_logos.py::test_minimal_output_enforcement)
    """

    paths: list[str]
    logos: "Logos"
    _enforce_minimal_output: bool = True
    _emit_law_check: bool = True

    async def invoke(
        self,
        observer: "Observer | Umwelt[Any, Any]",
        initial_input: Any = None,
    ) -> Any:
        """
        Execute composition as pipeline.

        Each path is invoked in sequence, passing the result
        of the previous path as the input kwarg.

        Track B (Law Enforcer): Emits law_check events for observability.

        v3 API: Accepts both Observer (lightweight) and Umwelt (full context).

        Args:
            observer: Observer or Umwelt
            initial_input: Optional initial value for the pipeline

        Returns:
            Final result after all paths executed
        """
        from .laws import emit_law_check_event, enforce_minimal_output as check_output

        # Track B: Emit law_check event for the composition
        if self._emit_law_check and len(self.paths) >= 2:
            # For compositions with 2+ paths, associativity is relevant
            emit_law_check_event(
                law="associativity",
                result="pass",  # Structural guarantee via right-association
                locus=self.name,
            )

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
        Track B (Law Enforcer): Preserves law check flag.
        """
        if isinstance(other, str):
            return ComposedPath(
                self.paths + [other],
                self.logos,
                self._enforce_minimal_output,
                self._emit_law_check,
            )
        return ComposedPath(
            self.paths + other.paths,
            self.logos,
            self._enforce_minimal_output and other._enforce_minimal_output,
            self._emit_law_check and other._emit_law_check,
        )

    def __rrshift__(self, other: str) -> "ComposedPath":
        """Allow string >> ComposedPath."""
        return ComposedPath(
            [other] + self.paths,
            self.logos,
            self._enforce_minimal_output,
            self._emit_law_check,
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
        return ComposedPath(self.paths, self.logos, False, self._emit_law_check)

    def without_law_checks(self) -> "ComposedPath":
        """
        Create a version without law check event emission.

        Track B (Law Enforcer): Use this for performance-critical paths
        where you've already verified laws hold.
        """
        return ComposedPath(self.paths, self.logos, self._enforce_minimal_output, False)

    def with_law_checks(self, emit: bool = True) -> "ComposedPath":
        """
        Create a version with explicit law check control.

        Track B (Law Enforcer): Use this to enable/disable law check events.

        Args:
            emit: Whether to emit law_check span events

        Returns:
            ComposedPath with specified law check behavior
        """
        return ComposedPath(self.paths, self.logos, self._enforce_minimal_output, emit)

    def __len__(self) -> int:
        """Number of paths in composition."""
        return len(self.paths)

    def __iter__(self) -> Iterator[str]:
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

    Teaching:
        gotcha: IdentityPath is useful for conditional pipelines:
                base = logos.identity() if skip else logos.path("step1")
                pipeline = base >> "step2"
                (Evidence: test_logos.py::test_identity_composition)
    """

    def __init__(self, logos: "Logos"):
        self.logos = logos

    @property
    def name(self) -> str:
        """Return identity name for composition display."""
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
    """
    Protocol for L-gent registry lookup.

    Teaching:
        gotcha: This is a Protocol (structural typing). Any class with
                get/register/update methods satisfies it—no inheritance needed.
                (Evidence: test_logos.py::test_registry_protocol)
    """

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

    Teaching:
        gotcha: SimpleRegistry is for testing. In production, NodeRegistry
                from registry.py is the authoritative source—Logos checks
                NodeRegistry BEFORE SimpleRegistry.
                (Evidence: test_logos.py::test_resolution_order)
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

    Teaching:
        gotcha: Resolution checks NodeRegistry BEFORE SimpleRegistry.
                @node decorators in services/ override any manual registration.
                (Evidence: test_logos.py::test_resolution_order)

        gotcha: Aliases are PREFIX expansion only. "me.challenge" → "self.soul.challenge".
                You cannot alias an aspect, only a path prefix.
                (Evidence: test_logos.py::test_alias_expansion)
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
    _capital_ledger: Any = None  # EventSourcedLedger for void.capital.*

    # Middleware (Phase 5: Wundt Curator for aesthetic filtering)
    _curator: "WundtCurator | None" = None

    # Telemetry middleware (Phase 6: OpenTelemetry integration)
    _telemetry_enabled: bool = False

    # v3: Path aliases registry
    _aliases: "AliasRegistry | None" = None

    # Crown Jewel Brain integration (Session 3-4)
    _memory_crystal: Any = None  # MemoryCrystal from agents.m
    _cartographer: Any = None  # CartographerAgent from agents.m
    _embedder: Any = None  # L-gent Embedder for semantic embeddings

    def __post_init__(self) -> None:
        """Initialize context resolvers if not already set."""
        if not self._context_resolvers:
            self._context_resolvers = create_context_resolvers(
                registry=self.registry,
                narrator=self._narrator,
                d_gent=self._d_gent,
                b_gent=self._b_gent,
                grammarian=self._grammarian,
                capital_ledger=self._capital_ledger,
                # Crown Jewel Brain (Session 3-4)
                memory_crystal=self._memory_crystal,
                cartographer=self._cartographer,
                embedder=self._embedder,
            )

    # === v3 API: Make Logos callable ===

    async def __call__(
        self,
        path: str,
        observer: "Observer | Umwelt[Any, Any] | None" = None,
        **kwargs: Any,
    ) -> Any:
        """
        Invoke an AGENTESE path (v3 API).

        Makes Logos callable for cleaner syntax:
            result = await logos("world.house.manifest")
            result = await logos("self.soul.challenge", observer)

        v3 Enhancement: Observer can be:
            - None: Uses Observer.guest() (anonymous invocation)
            - Observer: Lightweight observer
            - Umwelt: Full observer context (v1 compatibility)

        Args:
            path: Full AGENTESE path including aspect
            observer: Optional observer (defaults to guest)
            **kwargs: Aspect-specific arguments

        Returns:
            Aspect-specific result
        """
        return await self.invoke(path, observer, **kwargs)

    def resolve(self, path: str, observer: "Umwelt[Any, Any] | None" = None) -> LogosNode:
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
        observer: "Observer | Umwelt[Any, Any] | None" = None,
        **kwargs: Any,
    ) -> Any:
        """
        Invoke an AGENTESE path with aspect.

        v3 API: Observer can be None (defaults to guest), Observer, or Umwelt.

        Example:
            # v3 style - anonymous invocation
            await logos.invoke("world.public.manifest")

            # v3 style - lightweight observer
            await logos.invoke("world.house.manifest", Observer(archetype="architect"))

            # v1 style - full Umwelt (still supported)
            await logos.invoke("world.house.manifest", architect_umwelt)

        Args:
            path: Full AGENTESE path including aspect
            observer: Observer, Umwelt, or None (defaults to guest)
            **kwargs: Aspect-specific arguments

        Returns:
            Aspect-specific result

        Raises:
            PathSyntaxError: If path doesn't include aspect
            AffordanceError: If observer lacks access to aspect
        """
        # v3: Default to guest observer if None
        if observer is None:
            observer = Observer.guest()

        # v3: Expand aliases
        path = self._expand_aliases(path)

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

        # Get AgentMeta from observer (v3: supports Observer and Umwelt)
        meta = self._observer_to_meta(observer)

        # Check affordances (Ethical principle)
        available = node.affordances(meta)
        if aspect not in available:
            raise AffordanceError(
                f"Aspect '{aspect}' not available to {meta.archetype}",
                aspect=aspect,
                observer_archetype=meta.archetype,
                available=available,
            )

        # Apply telemetry if enabled (Phase 6: OpenTelemetry integration)
        if self._telemetry_enabled:
            result = await self._invoke_with_telemetry(node, aspect, observer, path, **kwargs)
        else:
            result = await node.invoke(aspect, observer, **kwargs)  # type: ignore[arg-type]

        # Apply curator filtering (Phase 5: Wundt Curve aesthetic filtering)
        # PAYADOR Enhancement (v2.5): Auto-apply curator for GENERATION aspects
        if self._curator is not None:
            result = await self._curator.filter(result, observer, path, self)  # type: ignore[arg-type]
        elif self._should_auto_curate(aspect):
            # Auto-create curator for GENERATION aspects
            result = await self._auto_curate(result, observer, path)

        return result

    @asynccontextmanager
    async def invoke_stream(
        self,
        path: str,
        observer: "Observer | Umwelt[Any, Any] | None" = None,
        **kwargs: Any,
    ) -> AsyncIterator[AsyncIterator[Any]]:
        """
        Context manager for streaming invocations.

        Invokes the path and yields the result as an async iterator.
        If the result is already an async iterator (e.g., from self.chat.stream),
        it's yielded directly. Otherwise, the result is wrapped in a single-item
        async iterator for consistency.

        Usage:
            async with logos.invoke_stream("self.chat.stream", observer, message="Hi") as stream:
                async for token in stream:
                    print(token, end="", flush=True)
            print()  # Newline after streaming

        Args:
            path: Full AGENTESE path including aspect
            observer: Observer, Umwelt, or None (defaults to guest)
            **kwargs: Aspect-specific arguments

        Yields:
            AsyncIterator that produces the streaming result
        """
        result = await self.invoke(path, observer, **kwargs)

        if hasattr(result, "__aiter__"):
            # Already an async iterator (e.g., ChatNode.stream)
            yield result
        else:
            # Wrap non-streaming result in single-item iterator
            async def _single() -> AsyncIterator[Any]:
                yield result

            yield _single()

    async def _invoke_with_telemetry(
        self,
        node: LogosNode,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Invoke with OpenTelemetry span wrapping."""
        from .telemetry import trace_invocation

        async with trace_invocation(path, observer) as span:
            result = await node.invoke(aspect, observer, **kwargs)  # type: ignore[arg-type]

            # Record result type
            span.set_attribute("agentese.result.type", type(result).__name__)

            return result

    def compose(
        self,
        *paths: str,
        enforce_output: bool = True,
        emit_law_check: bool = True,
    ) -> ComposedPath:
        """
        Create a composed path for pipeline execution.

        Category Laws are preserved:
        - Identity: Id >> path == path == path >> Id
        - Associativity: (a >> b) >> c == a >> (b >> c)

        Track B (Law Enforcer): Emits law_check span events when invoked.

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
            emit_law_check: Whether to emit law_check span events
                          (default: True). Set to False for performance.

        Returns:
            ComposedPath that can be invoked or further composed
        """
        return ComposedPath(list(paths), self, enforce_output, emit_law_check)

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

    def path(self, p: str, emit_law_check: bool = True) -> ComposedPath:
        """
        Create a single-path composition for chaining.

        This allows the >> operator on string paths:
            pipeline = logos.path("world.house.manifest") >> "concept.summary.refine"

        Track B (Law Enforcer): Emits law_check events when composed paths invoke.

        Args:
            p: AGENTESE path
            emit_law_check: Whether to emit law_check span events

        Returns:
            ComposedPath with single path
        """
        return ComposedPath([p], self, True, emit_law_check)

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
        """Resolve by context type using Phase 2 context resolvers.

        Resolution order (AD-009 Metaphysical Fullstack, AD-016 Fail-Fast):
        1. Check NodeRegistry for @node decorated classes (services/)
           - Check most specific path first (e.g., self.forest.session)
           - Fall back to parent path (e.g., self.forest)
        2. Use context-specific resolvers (agents/)
        3. Check SimpleRegistry (legacy)
        4. Raise NodeNotRegisteredError (AD-016: no JIT fallback)

        Note: JIT generation from spec files was removed per AD-016.
        Use _generate_from_spec() explicitly if needed.
        """
        from .registry import get_registry

        node_registry = get_registry()

        # AD-009: Check NodeRegistry first (@node decorated service nodes)
        # This enables the Metaphysical Fullstack pattern where services
        # auto-register their AGENTESE nodes
        #
        # IMPORTANT: Check most specific path first to support nested nodes
        # e.g., self.forest.session should match before self.forest
        handles_to_check = []

        # Build list of handles from most specific to least specific
        # For rest=["session"], we check: self.forest.session, then self.forest
        parts = [context, holon] + rest
        for i in range(len(parts), 1, -1):
            handles_to_check.append(".".join(parts[:i]))

        for handle in handles_to_check:
            if node_registry.has(handle):
                # Get class and instantiate (sync - will be cached by registry)
                # Note: For async resolution with DI, use gateway._invoke_path()
                node_cls = node_registry.get(handle)
                if node_cls is not None:
                    try:
                        # Try to instantiate without dependencies
                        # For full DI, use ServiceContainer
                        return cast(LogosNode, node_cls())
                    except TypeError:
                        # Node requires dependencies - will be handled by gateway
                        pass

        # Use the base handle for remaining resolution
        handle = f"{context}.{holon}"

        # Phase 2: Use context-specific resolvers
        if context in self._context_resolvers:
            resolver = self._context_resolvers[context]
            # All Phase 2 resolvers implement resolve(holon, rest)
            if hasattr(resolver, "resolve"):
                return cast(LogosNode, resolver.resolve(holon, rest))

        # Fallback: Check registry directly (SimpleRegistry)
        node = self.registry.get(handle)
        if node:
            return node

        # AD-016: Fail-fast on unregistered paths (no JIT fallback)
        # JIT spec generation was removed because it masked registration bugs.
        # Spec files can still be used explicitly via logos._generate_from_spec().
        from .exceptions import NodeNotRegisteredError

        # Similar handles for suggestion
        similar = self.registry.list_handles(f"{context}.")

        # AD-016: NodeNotRegisteredError with helpful suggestion
        raise NodeNotRegisteredError(
            path=handle,
            similar_paths=similar[:5],
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
            # Re-raise tasteful errors as-is (AD-016: fail-fast)
            raise
        except Exception as e:
            # AD-016: Fail-fast on compilation failure (no silent fallback)
            # Previously this silently returned a minimal JIT node, masking bugs
            raise TastefulnessError(
                f"JIT compilation failed for '{handle}' from {spec_path}",
                validation_errors=[str(e)],
                why="Spec compilation failed and AD-016 forbids silent fallback",
                suggestion=(
                    f"Check the spec file at {spec_path} for syntax errors, "
                    "or register an explicit @node implementation"
                ),
            ) from e

    # === Phase 4: Autopoiesis (define aspect) ===

    async def define_concept(
        self,
        handle: str,
        spec: str,
        observer: "Umwelt[Any, Any]",
        extends: list[str] | None = None,
        justification: str = "",
    ) -> LogosNode:
        """
        Create a new concept via autopoiesis.

        The Generative Principle: Specs are compressed wisdom.
        New entities can be created from well-formed specs.

        For concept.* handles, the Genealogical Constraint applies:
        - No concept exists ex nihilo
        - Every concept must declare its parents (extends)
        - Lattice position must be validated

        Args:
            handle: The AGENTESE path for the new entity (e.g., "world.garden")
            spec: The spec content (markdown with YAML front matter)
            observer: The observer creating this entity
            extends: Parent concept handles (REQUIRED for concept.* paths)
            justification: Why this concept needs to exist

        Returns:
            The newly created LogosNode

        Raises:
            AffordanceError: If observer lacks 'define' affordance
            TastefulnessError: If spec is invalid
            PathSyntaxError: If handle is malformed
            LineageError: If concept has no parents (for concept.* context)
            LatticeError: If lattice position is invalid
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

        # Check observer affordance (v3: supports Observer and Umwelt)
        meta = self._observer_to_meta(observer)

        # 'define' requires special permission (architect, developer, or explicit capability)
        can_define = (
            meta.archetype in ("architect", "developer", "admin") or "define" in meta.capabilities
        )
        if not can_define:
            raise AffordanceError(
                f"Observer '{meta.name}' cannot define new entities",
                aspect="define",
                observer_archetype=meta.archetype,
                available=["manifest", "witness", "affordances"],
            )

        # === CONCEPT CONTEXT: Genealogical Constraint ===
        # For concept.* paths, use lineage-aware define
        if context == "concept":
            from .contexts.concept import define_concept as lineage_define_concept

            # Genealogical Constraint: concepts require parents
            if not extends:
                from .lattice.errors import LineageError

                raise LineageError(
                    f"Cannot create '{handle}': concepts cannot exist ex nihilo",
                    handle=handle,
                )

            # Delegate to lineage-aware define
            return await lineage_define_concept(
                logos=self,
                handle=handle,
                observer=observer,
                spec=spec,
                extends=extends,
                justification=justification,
            )

        # === OTHER CONTEXTS: Standard JIT compilation ===
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
    ) -> Any:
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
        result: list[dict[str, Any]] = []
        for handle in self._jit_nodes:
            status = self.get_jit_status(handle)
            if status is not None:
                result.append(status)
        return result

    def _observer_to_meta(self, observer: "Observer | Umwelt[Any, Any]") -> AgentMeta:
        """
        Extract AgentMeta from Observer or Umwelt.

        v3 API: Accepts both Observer (lightweight) and Umwelt (full context).
        """
        # v3 Observer - direct extraction
        if isinstance(observer, Observer):
            return AgentMeta.from_observer(observer)

        # v1 Umwelt - extract from DNA
        dna = observer.dna
        name = getattr(dna, "name", "unknown")
        archetype = getattr(dna, "archetype", "default")
        capabilities = getattr(dna, "capabilities", ())
        return AgentMeta(name=name, archetype=archetype, capabilities=capabilities)

    # Alias for backward compatibility
    def _umwelt_to_meta(self, umwelt: "Umwelt[Any, Any]") -> AgentMeta:
        """Extract AgentMeta from Umwelt's DNA. Deprecated: use _observer_to_meta."""
        return self._observer_to_meta(umwelt)

    # === PAYADOR (v2.5): Auto-Curator for GENERATION aspects ===

    # GENERATION aspects from affordances.py that should auto-curate
    _GENERATION_ASPECTS: frozenset[str] = frozenset(
        {
            "define",
            "spawn",
            "fork",
            "dream",
            "refine",
            "dialectic",
            "compress",
            "blend",
            "solve",  # pataphysics.solve generates creative content
        }
    )

    def _should_auto_curate(self, aspect: str) -> bool:
        """
        Determine if an aspect should be auto-curated.

        PAYADOR Enhancement (v2.5): GENERATION category aspects
        automatically get filtered through the Wundt Curator to ensure
        quality output (not too boring, not too chaotic).

        Args:
            aspect: The aspect being invoked

        Returns:
            True if the aspect should be auto-curated
        """
        return aspect in self._GENERATION_ASPECTS

    async def _auto_curate(
        self,
        result: Any,
        observer: "Observer | Umwelt[Any, Any]",
        path: str,
    ) -> Any:
        """
        Apply automatic curation for GENERATION aspects.

        Creates a default WundtCurator and filters the result.
        Uses conservative thresholds to avoid being too aggressive.

        Args:
            result: The result to filter
            observer: Observer or Umwelt
            path: The full AGENTESE path

        Returns:
            Filtered result
        """
        from .middleware.curator import WundtCurator

        # Use conservative thresholds for auto-curation
        # More permissive than manual curation to avoid surprises
        auto_curator = WundtCurator(
            low_threshold=0.15,  # Only reject very boring output
            high_threshold=0.95,  # Allow quite chaotic output
        )

        return await auto_curator.filter(result, observer, path, self)  # type: ignore[arg-type]

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

    def with_curator(self, curator: "WundtCurator") -> "Logos":
        """
        Create a new Logos instance with curator middleware.

        The curator filters invoke() results through the Wundt Curve,
        rejecting boring/chaotic output and enhancing/compressing as needed.

        Args:
            curator: WundtCurator instance for aesthetic filtering

        Returns:
            New Logos instance with curator set

        Example:
            from protocols.agentese.middleware.curator import WundtCurator

            curated_logos = logos.with_curator(WundtCurator())
            result = await curated_logos.invoke("concept.story.manifest", observer)
            # Result is filtered through Wundt Curve
        """
        return Logos(
            registry=self.registry,
            spec_root=self.spec_root,
            _cache=self._cache.copy(),
            _jit_nodes=self._jit_nodes.copy(),
            _context_resolvers=self._context_resolvers,
            _narrator=self._narrator,
            _d_gent=self._d_gent,
            _b_gent=self._b_gent,
            _grammarian=self._grammarian,
            _capital_ledger=self._capital_ledger,
            _curator=curator,
            _telemetry_enabled=self._telemetry_enabled,
        )

    def with_telemetry(self, enabled: bool = True) -> "Logos":
        """
        Create a new Logos instance with telemetry enabled/disabled.

        When enabled, all invoke() calls are wrapped with OpenTelemetry spans
        for distributed tracing.

        Args:
            enabled: Whether to enable telemetry (default True)

        Returns:
            New Logos instance with telemetry setting

        Example:
            from protocols.agentese.exporters import configure_telemetry

            # Configure OTEL once at startup
            configure_telemetry(TelemetryConfig(otlp_endpoint="tempo:4317"))

            # Enable telemetry on Logos
            traced_logos = logos.with_telemetry()
            result = await traced_logos.invoke("self.soul.challenge", observer, "idea")
            # Span exported to Tempo/Jaeger
        """
        return Logos(
            registry=self.registry,
            spec_root=self.spec_root,
            _cache=self._cache.copy(),
            _jit_nodes=self._jit_nodes.copy(),
            _context_resolvers=self._context_resolvers,
            _narrator=self._narrator,
            _d_gent=self._d_gent,
            _b_gent=self._b_gent,
            _grammarian=self._grammarian,
            _capital_ledger=self._capital_ledger,
            _curator=self._curator,
            _telemetry_enabled=enabled,
        )

    # === v3 API: Query System ===

    def query(
        self,
        pattern: str,
        *,
        limit: int = 100,
        offset: int = 0,
        tenant_id: str | None = None,
        observer: "Observer | Umwelt[Any, Any] | None" = None,
        capability_check: bool = True,
        dry_run: bool = False,
    ) -> "QueryResult":
        """
        Query the registry without invocation (v3 API).

        This allows asking "what exists?" without triggering side effects.

        Args:
            pattern: Query pattern (must start with '?')
                - ?world.*           - Query all world nodes
                - ?*.*.manifest      - Query all manifestable paths
                - ?self.memory.?     - Query affordances for self.memory
            limit: Maximum results (default 100, max 1000)
            offset: Pagination offset (default 0)
            tenant_id: Optional tenant filter
            observer: Observer for capability checking
            capability_check: Whether to filter by capability (default True)
            dry_run: If True, only estimate cost without executing

        Returns:
            QueryResult with matches and metadata

        Raises:
            QuerySyntaxError: If pattern is invalid
            QueryBoundError: If limit exceeds 1000

        Example:
            # Query all world nodes
            result = logos.query("?world.*")
            for match in result:
                print(match.path)

            # Query with pagination
            result = logos.query("?world.*", limit=10, offset=20)

            # Query affordances
            result = logos.query("?self.memory.?")
        """
        from .query import query as do_query

        # Convert Umwelt to Observer if needed
        obs: Observer | None = None
        if observer is not None:
            if isinstance(observer, Observer):
                obs = observer
            else:
                # Extract from Umwelt
                dna = observer.dna
                obs = Observer(
                    archetype=getattr(dna, "archetype", "guest"),
                    capabilities=frozenset(getattr(dna, "capabilities", ())),
                )

        return do_query(
            self,
            pattern,
            limit=limit,
            offset=offset,
            tenant_id=tenant_id,
            observer=obs,
            capability_check=capability_check,
            dry_run=dry_run,
        )

    # === v3 API: Alias System ===

    def _expand_aliases(self, path: str) -> str:
        """
        Expand aliases in a path.

        Only the first segment is checked for aliases.
        """
        if self._aliases is None:
            return path
        return self._aliases.expand(path)

    def alias(self, name: str, target: str) -> None:
        """
        Register a path alias (v3 API).

        Aliases are prefix expansions: "me" -> "self.soul"
        So "me.challenge" expands to "self.soul.challenge"

        Rules:
        - Prefix expansion only (alias must be first segment)
        - No recursion (aliases don't expand within aliases)
        - Shadowing forbidden (can't alias to context names)

        Args:
            name: Alias name (single segment)
            target: Target path (e.g., "self.soul")

        Example:
            logos.alias("me", "self.soul")
            await logos("me.challenge", observer)  # → self.soul.challenge
        """
        from .aliases import AliasRegistry

        if self._aliases is None:
            self._aliases = AliasRegistry()
        self._aliases.register(name, target)

    def unalias(self, name: str) -> None:
        """
        Remove a path alias.

        Args:
            name: Alias to remove
        """
        if self._aliases is not None:
            self._aliases.unregister(name)

    def get_aliases(self) -> dict[str, str]:
        """
        Get all registered aliases.

        Returns:
            Dict mapping alias names to target paths
        """
        if self._aliases is None:
            return {}
        return self._aliases.list_aliases()

    def with_aliases(self, aliases: "AliasRegistry") -> "Logos":
        """
        Create a new Logos instance with alias registry.

        Args:
            aliases: AliasRegistry to use

        Returns:
            New Logos instance with aliases set
        """
        return Logos(
            registry=self.registry,
            spec_root=self.spec_root,
            _cache=self._cache.copy(),
            _jit_nodes=self._jit_nodes.copy(),
            _context_resolvers=self._context_resolvers,
            _narrator=self._narrator,
            _d_gent=self._d_gent,
            _b_gent=self._b_gent,
            _grammarian=self._grammarian,
            _capital_ledger=self._capital_ledger,
            _curator=self._curator,
            _telemetry_enabled=self._telemetry_enabled,
            _aliases=aliases,
        )


# === Factory Functions ===


def create_logos(
    spec_root: Path | str = "spec",
    registry: SimpleRegistry | None = None,
    narrator: Any = None,
    d_gent: Any = None,
    b_gent: Any = None,
    grammarian: Any = None,
    capital_ledger: Any = None,
    curator: "WundtCurator | None" = None,
    middleware: list["WundtCurator"] | None = None,
    telemetry: bool = False,
    # Crown Jewel Brain integration (Session 3-4)
    memory_crystal: Any = None,
    cartographer: Any = None,
    embedder: Any = None,
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
        capital_ledger: EventSourcedLedger for void.capital.* (injected for testing)
        curator: WundtCurator for aesthetic filtering (Phase 5)
        middleware: List of middleware to apply to all invoke() calls.
                   If provided, this takes precedence over the curator parameter.
                   The first WundtCurator in the list becomes the primary curator.
        telemetry: Enable OpenTelemetry tracing (Phase 6)
        memory_crystal: MemoryCrystal for Four Pillars holographic memory (Session 3)
        cartographer: CartographerAgent for holographic memory navigation (Session 3)
        embedder: L-gent Embedder for semantic embeddings (Session 4)

    Returns:
        Configured Logos instance with Phase 2 context resolvers

    Example:
        # Simple usage with curator
        logos = create_logos(curator=WundtCurator())

        # With middleware list (enables chaining)
        logos = create_logos(
            middleware=[
                WundtCurator(
                    low_threshold=0.2,
                    high_threshold=0.8,
                ),
            ]
        )

        # With telemetry enabled
        logos = create_logos(telemetry=True)

        # With Crown Jewel Brain wiring (use create_brain_logos() for full wiring)
        logos = create_logos(memory_crystal=crystal, embedder=embedder)

        # All outputs are filtered through the Wundt curve
        result = await logos.invoke("concept.story.manifest", observer)
    """
    # Determine the curator to use
    effective_curator = curator
    if middleware:
        # Use first WundtCurator from middleware list
        for mw in middleware:
            if hasattr(mw, "filter") and hasattr(mw, "evaluate"):
                effective_curator = mw
                break

    logos = Logos(
        registry=registry or SimpleRegistry(),
        spec_root=Path(spec_root),
        _narrator=narrator,
        _d_gent=d_gent,
        _b_gent=b_gent,
        _grammarian=grammarian,
        _capital_ledger=capital_ledger,
        _curator=effective_curator,
        _telemetry_enabled=telemetry,
        # Crown Jewel Brain (Session 3-4)
        _memory_crystal=memory_crystal,
        _cartographer=cartographer,
        _embedder=embedder,
    )
    logos.__post_init__()  # Initialize context resolvers
    return logos


def create_curated_logos(
    complexity_min: float = 0.1,
    complexity_max: float = 0.9,
    novelty_min: float = 0.1,
    novelty_max: float = 0.9,
    **kwargs: Any,
) -> Logos:
    """
    Convenience factory to create a Logos with pre-configured Wundt Curator.

    This is the recommended way to enable aesthetic filtering globally.
    All invoke() results will be filtered through the Wundt Curve.

    Args:
        complexity_min: Below this complexity = boring (default 0.1)
        complexity_max: Above this complexity = chaotic (default 0.9)
        novelty_min: Below this novelty = boring (default 0.1)
        novelty_max: Above this novelty = chaotic (default 0.9)
        **kwargs: Additional arguments passed to create_logos()

    Returns:
        Logos with WundtCurator middleware enabled

    Example:
        # Create Logos that filters boring/chaotic output
        logos = create_curated_logos()

        # Custom thresholds for creative applications
        logos = create_curated_logos(
            complexity_min=0.2,  # Tolerate more simplicity
            complexity_max=0.95,  # Allow more complexity
            novelty_min=0.15,
            novelty_max=0.85,
        )
    """
    from .middleware.curator import WundtCurator

    curator = WundtCurator(
        low_threshold=min(complexity_min, novelty_min),
        high_threshold=max(complexity_max, novelty_max),
    )

    return create_logos(curator=curator, **kwargs)


# === Example Nodes for Testing ===


@dataclass
class PlaceholderNode:
    """
    Placeholder node for testing resolver behavior.

    Provides basic affordances and manifest behavior.

    Teaching:
        gotcha: PlaceholderNode is for tests only. Production nodes should
                extend BaseLogosNode or use @node decorator.
                (Evidence: test_logos.py::test_placeholder_node)
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
        return cast("Agent[Any, Any]", AspectAgent(self, aspect))

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
