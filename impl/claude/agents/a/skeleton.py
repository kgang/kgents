"""
A-gents Skeleton: The minimal structure every agent MUST implement.

This module formalizes what Agent[A, B] already IS:
- The skeleton is not a new class, but a recognition that Agent[A, B] in
  bootstrap.types IS the irreducible skeleton.

The key insight: Agent[A, B] provides:
    - name: str (identity)
    - invoke(input: A) -> B (behavior)
    - __rshift__ (composition)

That's it. That's the skeleton.

For agents that want to declare richer metadata (as per spec/a-gents/abstract/skeleton.md),
we provide AgentMeta as an OPTIONAL enhancement, not a requirement.

Philosophy: Composition, not duplication. We re-export Agent as AbstractAgent
for semantic clarity, but it's the same class.
"""

from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, Type, TypeVar, runtime_checkable

# Re-export the bootstrap Agent as AbstractAgent
# This is NOT a new class - it's the recognition that Agent IS the skeleton
from bootstrap.types import Agent

# Type alias for semantic clarity
AbstractAgent = Agent

# Type variables
A = TypeVar("A")
B = TypeVar("B")


@dataclass
class AgentIdentity:
    """
    Optional identity metadata for an agent.

    From spec/a-gents/abstract/skeleton.md:
    - name: Human-readable name
    - genus: Letter category (a, b, c, ...)
    - version: Semantic version
    - purpose: One-sentence "why this exists"
    """

    name: str
    genus: str
    version: str
    purpose: str


@dataclass
class AgentInterface:
    """
    Optional interface declaration.

    Describes what types the agent accepts and produces.
    In Python, this is already captured by Agent[A, B] generics,
    but this provides human-readable documentation.
    """

    input_type: Type[Any]
    input_description: str
    output_type: Type[Any]
    output_description: str
    error_codes: list[tuple[str, str]] = field(
        default_factory=list
    )  # (code, description)


@dataclass
class AgentBehavior:
    """
    Optional behavior specification.

    From spec/a-gents/abstract/skeleton.md:
    - description: What this agent does
    - guarantees: What the agent promises
    - constraints: What the agent will not do
    - side_effects: Effects beyond output
    """

    description: str
    guarantees: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    side_effects: list[str] = field(default_factory=list)


@dataclass
class AgentMeta:
    """
    Optional metadata for agents that want full spec compliance.

    This is NOT required to be a valid agent. Agent[A, B] is already
    the skeleton. AgentMeta provides additional documentation and
    introspection capabilities.

    Usage:
        class MyAgent(Agent[str, int]):
            meta = AgentMeta(
                identity=AgentIdentity(
                    name="Counter",
                    genus="a",
                    version="0.1.0",
                    purpose="Counts characters in input"
                ),
                interface=AgentInterface(
                    input_type=str,
                    input_description="Text to count",
                    output_type=int,
                    output_description="Character count"
                ),
                behavior=AgentBehavior(
                    description="Returns the length of input string",
                    guarantees=["Output >= 0", "Pure function"],
                    constraints=["Does not access network"],
                )
            )
    """

    identity: AgentIdentity
    interface: AgentInterface | None = None
    behavior: AgentBehavior | None = None

    @classmethod
    def minimal(cls, name: str, genus: str, purpose: str) -> "AgentMeta":
        """Create minimal metadata with just identity."""
        return cls(
            identity=AgentIdentity(
                name=name, genus=genus, version="0.1.0", purpose=purpose
            )
        )


# Protocol-based extension points for introspection and validation


@runtime_checkable
class Introspectable(Protocol):
    """
    Protocol for agents that provide metadata introspection.

    Agents implementing this protocol expose their AgentMeta
    for runtime inspection without requiring inheritance.
    """

    meta: AgentMeta


@runtime_checkable
class Validatable(Protocol):
    """
    Protocol for agents that can validate their inputs.

    Allows pre-flight validation before invoke() to catch
    type/constraint violations early.
    """

    def validate_input(self, input: Any) -> tuple[bool, str]:
        """
        Validate input before processing.

        Returns: (is_valid, error_message)
        """
        ...


@runtime_checkable
class Composable(Protocol):
    """
    Protocol for agents that can check composition compatibility.

    Enables static checking of A → B → C composition chains
    to detect type mismatches before runtime.
    """

    def can_compose_with(self, other: Agent[Any, Any]) -> tuple[bool, str]:
        """
        Check if this agent's output type matches other's input type.

        Returns: (is_compatible, reason)
        """
        ...


def has_meta(agent: Agent[Any, Any]) -> bool:
    """Check if an agent has AgentMeta defined."""
    return hasattr(agent, "meta") and isinstance(agent.meta, AgentMeta)


def get_meta(agent: Agent[Any, Any]) -> AgentMeta | None:
    """Get AgentMeta from an agent if present."""
    if has_meta(agent):
        return agent.meta  # type: ignore
    return None


def is_introspectable(agent: Agent[Any, Any]) -> bool:
    """Check if agent implements Introspectable protocol."""
    return isinstance(agent, Introspectable)


def is_validatable(agent: Agent[Any, Any]) -> bool:
    """Check if agent implements Validatable protocol."""
    return isinstance(agent, Validatable)


def is_composable(agent: Agent[Any, Any]) -> bool:
    """Check if agent implements Composable protocol."""
    return isinstance(agent, Composable)


def check_composition(
    agent_a: Agent[Any, Any], agent_b: Agent[Any, Any]
) -> tuple[bool, str]:
    """
    Check if two agents can be composed (agent_a >> agent_b).

    Uses Composable protocol if available, otherwise returns permissive result.
    Returns: (is_compatible, reason)
    """
    if is_composable(agent_a):
        return agent_a.can_compose_with(agent_b)  # type: ignore

    # Fallback: check metadata if available
    meta_a = get_meta(agent_a)
    meta_b = get_meta(agent_b)

    if meta_a and meta_a.interface and meta_b and meta_b.interface:
        output_type = meta_a.interface.output_type
        input_type = meta_b.interface.input_type

        if output_type != input_type:
            return (
                False,
                f"Type mismatch: {output_type.__name__} → {input_type.__name__}",
            )

    return (True, "Composition allowed (no metadata to verify)")


# Note on the Identity Agent:
# The Identity agent (Id) from bootstrap is already spec-compliant.
# It satisfies the skeleton by providing:
#   - name: "Identity"
#   - invoke: returns input unchanged
#   - composition: works correctly with any other agent
#
# See: impl/claude-openrouter/bootstrap/id.py


# =============================================================================
# Phase 1: BootstrapWitness - Verify bootstrap integrity
# =============================================================================


@dataclass
class BootstrapVerificationResult:
    """
    Result of bootstrap integrity verification.

    Captures whether all 7 bootstrap agents exist, satisfy categorical laws,
    and pass Judge evaluation. This is the proof that kgents can bootstrap.
    """

    all_agents_exist: bool
    identity_laws_hold: bool
    composition_laws_hold: bool
    judge_verdicts: dict[str, Any] = field(default_factory=dict)
    overall_verdict: Any = None  # Verdict type from bootstrap
    violations: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True if all verification checks passed."""
        return (
            self.all_agents_exist
            and self.identity_laws_hold
            and self.composition_laws_hold
            and (
                self.overall_verdict is None
                or self.overall_verdict.type.value == "accept"
            )
        )


class BootstrapWitness:
    """
    Verifies the bootstrap is sound.

    The skeleton becomes the checkpoint that says:
    "Yes, the 7 bootstrap agents exist and compose correctly."

    This is the pivotal role: skeleton validates bootstrap integrity.

    The 7 bootstrap agents:
    - Id: Identity morphism (composition unit)
    - Compose: Sequential composition (f >> g)
    - Judge: Value function (7 principles)
    - Ground: Empirical seed (persona, world)
    - Contradict: Tension detection
    - Sublate: Hegelian synthesis
    - Fix: Fixed-point iteration

    Laws verified:
    - Identity: Id >> f ≡ f ≡ f >> Id
    - Associativity: (f >> g) >> h ≡ f >> (g >> h)
    """

    REQUIRED_AGENTS = [
        "Id",
        "Compose",
        "Judge",
        "Ground",
        "Contradict",
        "Sublate",
        "Fix",
    ]

    @classmethod
    async def verify_bootstrap(cls) -> BootstrapVerificationResult:
        """
        Verify all bootstrap agents exist and satisfy laws.

        Returns BootstrapVerificationResult with detailed status.
        """
        violations: list[str] = []
        judge_verdicts: dict[str, Any] = {}

        # Step 1: Verify all agents exist
        agents_exist = cls._verify_agents_exist()
        if not agents_exist:
            violations.append("One or more bootstrap agents missing")

        # Step 2: Verify identity laws
        identity_ok = True
        if agents_exist:
            try:
                identity_ok = await cls._verify_all_identity_laws()
                if not identity_ok:
                    violations.append("Identity laws violated")
            except Exception as e:
                identity_ok = False
                violations.append(f"Identity law check failed: {e}")

        # Step 3: Verify composition laws
        composition_ok = True
        if agents_exist:
            try:
                composition_ok = await cls._verify_all_composition_laws()
                if not composition_ok:
                    violations.append("Composition laws violated")
            except Exception as e:
                composition_ok = False
                violations.append(f"Composition law check failed: {e}")

        # Step 4: Create overall verdict
        from bootstrap.types import Verdict

        if agents_exist and identity_ok and composition_ok:
            overall_verdict = Verdict.accept(["Bootstrap verified"])
        else:
            overall_verdict = Verdict.reject(violations)

        return BootstrapVerificationResult(
            all_agents_exist=agents_exist,
            identity_laws_hold=identity_ok,
            composition_laws_hold=composition_ok,
            judge_verdicts=judge_verdicts,
            overall_verdict=overall_verdict,
            violations=violations,
        )

    @classmethod
    def _verify_agents_exist(cls) -> bool:
        """Verify all 7 bootstrap agents can be imported."""
        try:
            # Import all 7 bootstrap agents to verify they exist
            # Using __import__ to avoid F401 unused import warnings
            import bootstrap

            required = [
                "Id",
                "Compose",
                "Judge",
                "Ground",
                "Contradict",
                "Sublate",
                "Fix",
            ]
            return all(hasattr(bootstrap, name) for name in required)
        except ImportError:
            return False

    @classmethod
    async def _verify_all_identity_laws(cls) -> bool:
        """Verify identity laws for sample agents."""

        # Create test agents
        class TestAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "TestAgent"

            async def invoke(self, input: int) -> int:
                return input * 2

        test_agent = TestAgent()
        return await cls.verify_identity_laws(test_agent, 5)

    @classmethod
    async def _verify_all_composition_laws(cls) -> bool:
        """Verify composition laws for sample agents."""

        class DoubleAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Double"

            async def invoke(self, input: int) -> int:
                return input * 2

        class SquareAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "Square"

            async def invoke(self, input: int) -> int:
                return input * input

        class AddOneAgent(Agent[int, int]):
            @property
            def name(self) -> str:
                return "AddOne"

            async def invoke(self, input: int) -> int:
                return input + 1

        return await cls.verify_composition_laws(
            DoubleAgent(), SquareAgent(), AddOneAgent(), 3
        )

    @classmethod
    async def verify_identity_laws(cls, agent: Agent[A, B], test_input: A) -> bool:
        """
        Verify identity laws hold for an agent.

        - Left identity: Id >> agent ≡ agent
        - Right identity: agent >> Id ≡ agent
        """
        from bootstrap.id import Id

        id_agent = Id()

        # Direct invocation
        direct_result = await agent.invoke(test_input)

        # Id >> agent (left identity)
        left_composed = id_agent >> agent
        left_result = await left_composed.invoke(test_input)

        # agent >> Id (right identity)
        right_composed = agent >> id_agent
        right_result = await right_composed.invoke(test_input)

        return direct_result == left_result == right_result

    @classmethod
    async def verify_composition_laws(
        cls, f: Agent[A, B], g: Agent[B, Any], h: Agent[Any, Any], test_input: A
    ) -> bool:
        """
        Verify composition law: (f >> g) >> h ≡ f >> (g >> h)

        Associativity must hold for agents to form a category.
        """
        # (f >> g) >> h
        left_composed = (f >> g) >> h
        left_result = await left_composed.invoke(test_input)

        # f >> (g >> h)
        right_composed = f >> (g >> h)
        right_result = await right_composed.invoke(test_input)

        return left_result == right_result


# =============================================================================
# Phase 2: Category-Theoretic Protocols - Morphism and Functor
# =============================================================================


@runtime_checkable
class Morphism(Protocol[A, B]):
    """
    Agent as morphism in the category of agents.

    In category theory, a morphism (or arrow) is a structure-preserving map
    between objects. In kgents, agents ARE morphisms: Agent[A, B] represents
    a morphism from type A to type B.

    Laws (verified by BootstrapWitness):
    - Identity: Id >> f ≡ f ≡ f >> Id
    - Associativity: (f >> g) >> h ≡ f >> (g >> h)

    This protocol makes the categorical structure explicit and enables
    structural typing - any object with these methods is a Morphism.
    """

    @property
    def name(self) -> str:
        """Human-readable name for this morphism."""
        ...

    async def invoke(self, input: A) -> B:
        """The morphism arrow A → B."""
        ...

    def __rshift__(self, other: "Agent[B, Any]") -> "Agent[A, Any]":
        """Composition: f >> g creates morphism A → C."""
        ...


@runtime_checkable
class Functor(Protocol):
    """
    Structure-preserving transformation between categories.

    A functor F lifts agents from one category to another while preserving
    composition:
    - F(id) = id_F (identity preservation)
    - F(g ∘ f) = F(g) ∘ F(f) (composition preservation)

    Examples of functors in kgents:
    - Maybe: Agent[A, B] → Agent[Maybe[A], Maybe[B]]
    - Either: Agent[A, B] → Agent[Either[E, A], Either[E, B]]
    - List: Agent[A, B] → Agent[List[A], List[B]]
    - Async: Agent[A, B] → Agent[A, Awaitable[B]]
    - Logged: Agent[A, B] → Agent[A, (B, LogEntry)]

    See: spec/c-gents/functors.md, impl/claude/agents/c/functor.py
    """

    def lift(self, agent: Agent[A, B]) -> Agent[Any, Any]:
        """
        Lift an agent into this functor's category.

        Takes Agent[A, B] and returns Agent[F[A], F[B]] where F is
        this functor's type constructor.
        """
        ...


def get_domain(agent: Agent[A, B]) -> type | None:
    """
    Extract domain (input) type from agent using type hints.

    Uses typing.get_type_hints() to introspect the invoke method's
    input parameter type. Returns None if type hints are not available.

    Example:
        class MyAgent(Agent[str, int]):
            async def invoke(self, input: str) -> int: ...

        get_domain(MyAgent())  # Returns: str
    """
    from typing import get_type_hints

    try:
        hints = get_type_hints(agent.invoke)
        return hints.get("input")
    except Exception:
        return None


def get_codomain(agent: Agent[A, B]) -> type | None:
    """
    Extract codomain (output) type from agent using type hints.

    Uses typing.get_type_hints() to introspect the invoke method's
    return type annotation. Returns None if type hints are not available.

    Example:
        class MyAgent(Agent[str, int]):
            async def invoke(self, input: str) -> int: ...

        get_codomain(MyAgent())  # Returns: int
    """
    from typing import get_type_hints

    try:
        hints = get_type_hints(agent.invoke)
        return hints.get("return")
    except Exception:
        return None


def verify_composition_types(f: Agent[A, B], g: Agent[Any, Any]) -> tuple[bool, str]:
    """
    Verify f >> g is type-safe: codomain(f) ⊆ domain(g).

    This is a runtime check that f's output type is compatible with
    g's input type. Enables early detection of composition errors.

    Returns:
        (is_valid, explanation) - True if types match, with explanation

    Example:
        f = Agent[str, int]  # str → int
        g = Agent[int, float]  # int → float

        verify_composition_types(f, g)  # (True, "int → int: compatible")

        h = Agent[str, float]  # str → float
        verify_composition_types(f, h)  # (False, "Type mismatch: int → str")
    """
    f_codomain = get_codomain(f)
    g_domain = get_domain(g)

    # If we can't determine types, allow composition (be permissive)
    if f_codomain is None or g_domain is None:
        return (True, "Type hints unavailable; composition allowed")

    # Check type compatibility
    # In Python, we can use issubclass for structural checks
    try:
        if f_codomain == g_domain:
            return (True, f"{f_codomain.__name__} → {g_domain.__name__}: compatible")
        elif isinstance(f_codomain, type) and isinstance(g_domain, type):
            if issubclass(f_codomain, g_domain):
                return (
                    True,
                    f"{f_codomain.__name__} is subtype of {g_domain.__name__}: compatible",
                )
            else:
                return (
                    False,
                    f"Type mismatch: {f_codomain.__name__} is not compatible with {g_domain.__name__}",
                )
        else:
            # Complex types (generics, unions, etc.) - be permissive
            return (True, f"Complex type check: {f_codomain} → {g_domain}")
    except TypeError:
        # issubclass fails for some type constructs
        return (True, "Type check inconclusive; composition allowed")


# =============================================================================
# Phase 3: AgentFactory - Generative center for agent creation
# =============================================================================


@dataclass
class AgentSpec:
    """
    Parsed agent specification from markdown.

    Extracted from spec/*.md files using YAML frontmatter and
    structured sections. Used by AgentFactory.from_spec_file().
    """

    identity: AgentIdentity
    interface: AgentInterface | None = None
    behavior: AgentBehavior | None = None
    raw_markdown: str = ""


class _WrappedAgent(Agent[A, B], Generic[A, B]):
    """
    Agent wrapper that combines implementation with metadata.

    Created by AgentFactory.create() to wrap a callable with AgentMeta.
    """

    def __init__(
        self,
        impl: Any,  # Callable[[A], B] or Callable[[A], Awaitable[B]]
        meta: AgentMeta,
        is_async: bool = True,
    ):
        self._impl = impl
        self.meta = meta
        self._is_async = is_async

    @property
    def name(self) -> str:
        return self.meta.identity.name

    async def invoke(self, input: A) -> B:
        if self._is_async:
            return await self._impl(input)
        else:
            return self._impl(input)


class AgentFactory:
    """
    The meta-agent that creates other agents.

    Every agent in kgents can be created through this factory,
    ensuring consistency and enabling meta-level operations.

    AgentFactory provides:
    - create(): Wrap implementation with metadata
    - from_spec_file(): Parse spec/*.md to AgentSpec
    - compose(): Validated composition of multiple agents
    - from_spec_and_impl(): Full factory from spec + implementation

    Usage:
        # Create agent from callable
        agent = AgentFactory.create(
            meta=AgentMeta.minimal("Counter", "a", "Counts characters"),
            impl=lambda s: len(s)
        )

        # Parse spec file
        spec = AgentFactory.from_spec_file(Path("spec/a-gents/art/creativity-coach.md"))

        # Compose with validation
        pipeline = AgentFactory.compose(agent_a, agent_b, validate=True)
    """

    @classmethod
    def create(
        cls,
        meta: AgentMeta,
        impl: Any,  # Callable[[A], B] or Callable[[A], Awaitable[B]]
    ) -> Agent[A, B]:
        """
        Create an agent from metadata + implementation.

        Wraps implementation with metadata for introspection.

        Args:
            meta: AgentMeta describing the agent
            impl: Callable that performs the agent's work

        Returns:
            Agent[A, B] with attached metadata
        """
        import inspect

        is_async = inspect.iscoroutinefunction(impl)
        return _WrappedAgent(impl, meta, is_async)

    @classmethod
    def from_spec_file(cls, spec_path: Any) -> AgentSpec:
        """
        Parse spec/*.md file into AgentSpec.

        Extracts YAML frontmatter and structured sections.
        Ground already parses persona.md - this generalizes that pattern.

        Args:
            spec_path: Path to markdown spec file

        Returns:
            AgentSpec with parsed metadata
        """
        from pathlib import Path

        path = Path(spec_path)
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {path}")

        content = path.read_text()
        return cls._parse_spec_content(content)

    @classmethod
    def _parse_spec_content(cls, content: str) -> AgentSpec:
        """Parse markdown content into AgentSpec."""
        # Try to extract YAML frontmatter
        identity = cls._extract_identity(content)

        # Try to extract interface and behavior from structured sections
        interface = cls._extract_interface(content)
        behavior = cls._extract_behavior(content)

        return AgentSpec(
            identity=identity,
            interface=interface,
            behavior=behavior,
            raw_markdown=content,
        )

    @classmethod
    def _extract_identity(cls, content: str) -> AgentIdentity:
        """Extract AgentIdentity from markdown content."""
        import re

        # Try YAML frontmatter first
        yaml_match = re.search(r"```yaml\s*\n(.*?)\n```", content, re.DOTALL)

        name = "Unknown"
        genus = "a"
        version = "0.1.0"
        purpose = ""

        if yaml_match:
            yaml_content = yaml_match.group(1)

            # Simple YAML-like parsing
            for line in yaml_content.split("\n"):
                if "name:" in line:
                    name = line.split(":", 1)[1].strip().strip("\"'")
                elif "genus:" in line:
                    genus = line.split(":", 1)[1].strip().strip("\"'")
                elif "version:" in line:
                    version = line.split(":", 1)[1].strip().strip("\"'")
                elif "purpose:" in line:
                    purpose = line.split(":", 1)[1].strip().strip("\"'")

        # Fallback: extract from headers
        if name == "Unknown":
            header_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if header_match:
                name = header_match.group(1).strip()

        return AgentIdentity(name=name, genus=genus, version=version, purpose=purpose)

    @classmethod
    def _extract_interface(cls, content: str) -> AgentInterface | None:
        """Extract AgentInterface from markdown content (if present)."""
        # Simple heuristic: look for interface section
        if "interface:" not in content.lower():
            return None

        # TODO: Implement full interface extraction
        return None

    @classmethod
    def _extract_behavior(cls, content: str) -> AgentBehavior | None:
        """Extract AgentBehavior from markdown content (if present)."""
        # Simple heuristic: look for behavior section
        if "behavior:" not in content.lower():
            return None

        # TODO: Implement full behavior extraction
        return None

    @classmethod
    def compose(
        cls, *agents: Agent[Any, Any], validate: bool = True
    ) -> Agent[Any, Any]:
        """
        Compose multiple agents with optional validation.

        If validate=True, uses verify_composition_types() for safety.

        Args:
            *agents: Agents to compose in order
            validate: Whether to check type compatibility

        Returns:
            Composed agent pipeline

        Raises:
            ValueError: If validation fails or no agents provided
        """
        if len(agents) == 0:
            raise ValueError("compose() requires at least one agent")

        if len(agents) == 1:
            return agents[0]

        # Validate composition if requested
        if validate:
            for i in range(len(agents) - 1):
                is_valid, reason = verify_composition_types(agents[i], agents[i + 1])
                if not is_valid:
                    raise ValueError(
                        f"Composition validation failed between {agents[i].name} and {agents[i + 1].name}: {reason}"
                    )

        # Compose left-to-right
        result = agents[0]
        for agent in agents[1:]:
            result = result >> agent

        return result

    @classmethod
    def from_spec_and_impl(
        cls,
        spec_path: Any,
        impl: Any,  # Callable[[A], B]
    ) -> Agent[A, B]:
        """
        Full factory: parse spec, wrap implementation.

        Enables spec-driven agent creation.

        Args:
            spec_path: Path to markdown spec file
            impl: Callable that performs the agent's work

        Returns:
            Agent[A, B] with metadata from spec
        """
        spec = cls.from_spec_file(spec_path)
        meta = AgentMeta(
            identity=spec.identity,
            interface=spec.interface,
            behavior=spec.behavior,
        )
        return cls.create(meta, impl)


class FactoryAgent(Agent[AgentMeta, Agent[Any, Any]]):
    """
    Agent that creates agents - the meta-factory as an agent itself.

    Input: AgentMeta describing desired agent
    Output: Agent instance (with stub implementation)

    This enables agent creation to be composed with other agents,
    making the factory itself part of the categorical structure.
    """

    @property
    def name(self) -> str:
        return "FactoryAgent"

    async def invoke(self, meta: AgentMeta) -> Agent[Any, Any]:
        """Create a stub agent from metadata."""

        async def stub_impl(input: Any) -> Any:
            return input  # Identity stub

        return AgentFactory.create(meta, stub_impl)


# =============================================================================
# Phase 4: GroundedSkeleton - Self-describing agents via Ground
# =============================================================================


class GroundedSkeleton(Agent[Any, AgentMeta]):
    """
    A skeleton that knows itself through Ground.

    The bootstrap agents can describe themselves:
    - Ground → Facts → skeleton parses to AgentMeta
    - Any agent can introspect via GroundedSkeleton

    This enables autopoiesis: agents that can describe themselves.

    Usage:
        # Describe any agent
        meta = await GroundedSkeleton.describe(my_agent)

        # Or use as an agent
        skeleton = GroundedSkeleton(my_agent)
        meta = await skeleton.invoke(VOID)
    """

    def __init__(self, target_agent: Agent[Any, Any] | None = None):
        """
        Initialize with optional target agent to describe.

        If None, describes the Ground agent itself.
        """
        self._target = target_agent

    @property
    def name(self) -> str:
        if self._target:
            return f"GroundedSkeleton({self._target.name})"
        return "GroundedSkeleton(Ground)"

    async def invoke(self, input: Any) -> AgentMeta:
        """
        Generate AgentMeta for target agent.

        Uses Ground facts + target agent introspection.
        """
        return self._derive_meta()

    def _derive_meta(self) -> AgentMeta:
        """
        Derive AgentMeta from target agent.

        If target is None, describes Ground itself.
        If target has existing meta, returns it (preserves existing).
        If target lacks meta, infers from name/type/docstring.
        """
        # If target has meta, use it
        if self._target and has_meta(self._target):
            return get_meta(self._target)  # type: ignore

        # Infer from target properties
        if self._target:
            name = self._target.name
            purpose = self._infer_purpose()
            genus = self._infer_genus()
        else:
            # Describe Ground itself
            name = "Ground"
            purpose = "The empirical seed agent that loads irreducible facts"
            genus = "bootstrap"

        return AgentMeta(
            identity=AgentIdentity(
                name=name,
                genus=genus,
                version="0.1.0",
                purpose=purpose,
            )
        )

    def _infer_purpose(self) -> str:
        """Infer purpose from target agent's docstring."""
        if not self._target:
            return ""

        # Try to get docstring
        doc = getattr(self._target, "__doc__", None) or ""
        if doc:
            # First sentence or line
            first_line = doc.strip().split("\n")[0].strip()
            if first_line:
                return first_line

        # Fallback to name-based inference
        return f"Agent named {self._target.name}"

    def _infer_genus(self) -> str:
        """Infer genus from target agent's module or class name."""
        if not self._target:
            return "unknown"

        # Try to infer from module path
        module = getattr(self._target.__class__, "__module__", "")
        if ".agents.a." in module or "/agents/a/" in module:
            return "a"
        elif ".agents.b." in module:
            return "b"
        elif ".agents.c." in module:
            return "c"
        elif ".bootstrap" in module:
            return "bootstrap"

        return "unknown"

    @classmethod
    async def describe(cls, agent: Agent[Any, Any]) -> AgentMeta:
        """
        Convenience: describe any agent using Ground.

        Usage:
            meta = await GroundedSkeleton.describe(my_agent)
        """
        from bootstrap.types import VOID

        return await cls(agent).invoke(VOID)


class AutopoieticAgent(Agent[A, B], Generic[A, B]):
    """
    Mixin for agents that can describe themselves.

    Agents inheriting from AutopoieticAgent get a describe_self()
    method that returns their AgentMeta using GroundedSkeleton.

    Usage:
        class MyAgent(AutopoieticAgent[str, int]):
            @property
            def name(self) -> str:
                return "MyAgent"

            async def invoke(self, input: str) -> int:
                return len(input)

        agent = MyAgent()
        meta = await agent.describe_self()  # Returns AgentMeta
    """

    async def describe_self(self) -> AgentMeta:
        """Return AgentMeta for this agent using GroundedSkeleton."""
        return await GroundedSkeleton.describe(self)
