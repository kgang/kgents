"""
J-gent AgentFactory Integration: JIT Agents as Bootstrap Agents.

This module bridges the gap between JIT-compiled code and the bootstrap Agent[A, B]
system. JIT agents are ephemeral, runtime-generated agents that must:
1. Pass safety validation (JITSafetyJudge)
2. Execute in sandboxed environments
3. Compose seamlessly with other agents via >>

Key Types:
- JITAgentMeta: Extended metadata for JIT-compiled agents
- JITAgentWrapper: Makes JIT code behave as Agent[A, B]

Primary Functions:
- create_agent_from_source: AgentSource → Agent[A, B]
- compile_and_instantiate: Intent → Agent (full pipeline)

Security Model:
- Every invoke() re-executes in sandbox (no cached code)
- ArchitectConstraints travel with the agent
- Stability score tracked for monitoring

See spec/j-gents/jit.md and HYDRATE.md for full specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from agents.a.skeleton import (
    AgentBehavior,
    AgentIdentity,
    AgentInterface,
    AgentMeta,
)
from bootstrap.types import Agent

from .chaosmonger import StabilityConfig, analyze_stability
from .meta_architect import (
    AgentSource,
    ArchitectConstraints,
    ArchitectInput,
    MetaArchitect,
    jit_safety_judge,
)
from .sandbox import SandboxConfig, execute_in_sandbox

# Type variables for agent generics
A = TypeVar("A")
B = TypeVar("B")


@dataclass(frozen=True)
class JITAgentMeta:
    """
    Extended metadata for JIT-compiled agents.

    Carries the full provenance of a JIT agent:
    - source: Original generated source code
    - constraints: Safety constraints used during generation
    - stability_score: Chaosmonger stability score (0.0-1.0)
    - sandbox_config: Execution configuration

    This enables full traceability and reproducibility of JIT agents.
    """

    source: AgentSource
    constraints: ArchitectConstraints
    stability_score: float
    sandbox_config: SandboxConfig = field(default_factory=SandboxConfig)


class JITAgentWrapper(Agent[A, B], Generic[A, B]):
    """
    Wrapper that makes JIT-compiled code behave as Agent[A, B].

    Properties:
    - name → class_name from source
    - meta → AgentMeta with JIT identity
    - jit_meta → JITAgentMeta for JIT-specific introspection
    - invoke() → Re-executes in sandbox for security
    - >> → Composition works via inherited Agent behavior

    Security: Every invoke() call re-compiles and executes in sandbox.
    This prevents any cached code from bypassing safety checks.

    Example:
        source = await compile_agent("Parse JSON logs")
        agent = await create_agent_from_source(source, ArchitectConstraints())

        # Use as normal agent
        result = await agent.invoke('{"level": "error"}')

        # Compose with other agents
        pipeline = agent >> format_agent >> store_agent
    """

    def __init__(
        self,
        meta: AgentMeta,
        jit_meta: JITAgentMeta,
        method_name: str = "invoke",
    ):
        """
        Initialize JIT agent wrapper.

        Args:
            meta: Standard AgentMeta for introspection
            jit_meta: JIT-specific metadata (source, constraints, etc.)
            method_name: Method to call on JIT agent (default: "invoke")
        """
        self._meta = meta
        self._jit_meta = jit_meta
        self._method_name = method_name

    @property
    def name(self) -> str:
        """Agent name from source class name."""
        return str(self._meta.identity.name)

    @property
    def meta(self) -> AgentMeta:
        """Standard AgentMeta for introspection."""
        return self._meta

    @property
    def jit_meta(self) -> JITAgentMeta:
        """JIT-specific metadata for provenance tracking."""
        return self._jit_meta

    async def invoke(self, input: A) -> B:
        """
        Execute JIT agent in sandbox.

        Security: Always re-executes in sandbox. Never uses cached code.
        This ensures every invocation goes through safety checks.

        Args:
            input: Input to pass to JIT agent

        Returns:
            Output from JIT agent

        Raises:
            RuntimeError: If sandbox execution fails
        """
        result = await execute_in_sandbox(
            source=self._jit_meta.source,
            method_name=self._method_name,
            args=(input,),
            config=self._jit_meta.sandbox_config,
        )

        if not result.success:
            raise RuntimeError(f"JIT execution failed: {result.error}")

        return result.output  # type: ignore[no-any-return]


def _build_agent_meta(
    source: AgentSource,
    constraints: ArchitectConstraints,
) -> AgentMeta:
    """
    Build AgentMeta from AgentSource.

    Maps JIT generation artifacts to standard agent metadata.
    """
    return AgentMeta(
        identity=AgentIdentity(
            name=source.class_name,
            genus="j",  # J-gent genus
            version="ephemeral",  # JIT agents are ephemeral
            purpose=source.description,
        ),
        interface=AgentInterface(
            input_type=Any,  # JIT agents have dynamic types
            input_description=f"Input to {source.class_name}",
            output_type=Any,
            output_description=f"Output from {source.class_name}",
        ),
        behavior=AgentBehavior(
            description=source.description,
            guarantees=[
                f"Complexity: {source.complexity}",
                f"Imports: {', '.join(sorted(source.imports))}",
            ],
            constraints=[
                f"Entropy budget: {constraints.entropy_budget}",
                f"Max complexity: {constraints.max_cyclomatic_complexity}",
            ],
        ),
    )


async def create_agent_from_source(
    source: AgentSource,
    constraints: ArchitectConstraints | None = None,
    validate: bool = True,
    sandbox_config: SandboxConfig | None = None,
) -> Agent[Any, Any]:
    """
    Create Agent[A, B] from AgentSource.

    Pipeline:
    1. Validate via JITSafetyJudge (if enabled)
    2. Compute stability score via Chaosmonger
    3. Build AgentMeta from source metadata
    4. Build JITAgentMeta with full provenance
    5. Return JITAgentWrapper

    Args:
        source: Generated agent source code
        constraints: Safety constraints (defaults to ArchitectConstraints())
        validate: Whether to run JITSafetyJudge validation
        sandbox_config: Sandbox configuration (defaults to SandboxConfig())

    Returns:
        Agent[Any, Any] that wraps JIT-compiled code

    Raises:
        ValueError: If validation fails

    Example:
        source = await compile_agent("Parse JSON logs")
        agent = await create_agent_from_source(source)

        result = await agent.invoke('{"level": "error"}')
    """
    constraints = constraints or ArchitectConstraints()
    sandbox_config = sandbox_config or SandboxConfig()

    # Step 1: Validate via JITSafetyJudge
    if validate:
        verdict = await jit_safety_judge.evaluate_source(source, constraints)
        if verdict.type.value == "reject":
            reasons = verdict.reasoning if verdict.reasoning else "Unknown"
            raise ValueError(f"JIT source rejected: {reasons}")

    # Step 2: Compute stability score from Chaosmonger analysis
    stability_result = analyze_stability(
        source_code=source.source,
        entropy_budget=constraints.entropy_budget,
        config=StabilityConfig(
            max_cyclomatic_complexity=constraints.max_cyclomatic_complexity,
            max_branching_factor=constraints.max_branching_factor,
            allowed_imports=constraints.allowed_imports,
        ),
    )
    # Compute stability score from metrics (1.0 = fully stable, 0.0 = unstable)
    # Use a simple heuristic based on is_stable and metrics
    if stability_result.is_stable:
        # Base score of 0.8 for stable, adjust based on complexity
        complexity_ratio = source.complexity / constraints.max_cyclomatic_complexity
        stability_score = max(0.5, 1.0 - (complexity_ratio * 0.3))
    else:
        # Unstable agents get low scores based on violation count
        stability_score = max(0.0, 0.4 - (len(stability_result.violations) * 0.1))

    # Step 3: Build AgentMeta
    meta = _build_agent_meta(source, constraints)

    # Step 4: Build JITAgentMeta
    jit_meta = JITAgentMeta(
        source=source,
        constraints=constraints,
        stability_score=stability_score,
        sandbox_config=sandbox_config,
    )

    # Step 5: Return wrapper
    return JITAgentWrapper(meta=meta, jit_meta=jit_meta)


async def compile_and_instantiate(
    intent: str,
    context: dict[str, Any] | None = None,
    constraints: ArchitectConstraints | None = None,
    validate: bool = True,
    sandbox_config: SandboxConfig | None = None,
) -> Agent[Any, Any]:
    """
    Full pipeline: Intent → Agent.

    Convenience function that runs the complete JIT compilation pipeline:
    1. MetaArchitect generates source from intent
    2. create_agent_from_source validates and wraps

    Args:
        intent: Natural language description of agent purpose
        context: Optional context (examples, formats, etc.)
        constraints: Safety constraints
        validate: Whether to validate source
        sandbox_config: Sandbox configuration

    Returns:
        Agent[Any, Any] ready for use

    Example:
        agent = await compile_and_instantiate(
            "Parse JSON logs and extract errors",
            context={"sample": '{"level": "error"}'}
        )
        result = await agent.invoke('{"level": "error", "msg": "oops"}')
    """
    constraints = constraints or ArchitectConstraints()

    # Step 1: Generate source via MetaArchitect
    architect = MetaArchitect()
    architect_input = ArchitectInput(
        intent=intent,
        context=context or {},
        constraints=constraints,
    )
    source = await architect.invoke(architect_input)

    # Step 2: Create agent from source
    return await create_agent_from_source(
        source=source,
        constraints=constraints,
        validate=validate,
        sandbox_config=sandbox_config,
    )


# Convenience function for introspection
def get_jit_meta(agent: Agent[Any, Any]) -> JITAgentMeta | None:
    """
    Extract JITAgentMeta from a JIT agent if present.

    Args:
        agent: Any agent

    Returns:
        JITAgentMeta if agent is a JITAgentWrapper, None otherwise
    """
    if isinstance(agent, JITAgentWrapper):
        return agent.jit_meta
    return None


def is_jit_agent(agent: Agent[Any, Any]) -> bool:
    """
    Check if an agent is a JIT-compiled agent.

    Args:
        agent: Any agent

    Returns:
        True if agent is a JITAgentWrapper
    """
    return isinstance(agent, JITAgentWrapper)


# Exports
__all__ = [
    # Types
    "JITAgentMeta",
    "JITAgentWrapper",
    # Primary functions
    "create_agent_from_source",
    "compile_and_instantiate",
    # Utility functions
    "get_jit_meta",
    "is_jit_agent",
]
