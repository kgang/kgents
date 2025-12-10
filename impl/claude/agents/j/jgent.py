"""
JGent: Just-in-Time Agent Coordinator

The main coordinator that orchestrates J-gents operations:
1. Classifies reality (DETERMINISTIC, PROBABILISTIC, CHAOTIC)
2. Manages lazy promise trees
3. Invokes MetaArchitect for JIT compilation when needed
4. Enforces entropy budgets
5. Collapses to Ground on instability

Morphism: JGentInput → T (where T is the ground type)

Philosophy:
> "Determine the nature of reality; compile the mind to match it; collapse to safety."

See spec/j-gents/ for the full specification.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Optional, TypeVar

from bootstrap.dna import JGentDNA
from bootstrap.types import Agent

from .chaosmonger import StabilityConfig, analyze_stability
from .meta_architect import (
    ArchitectConstraints,
    ArchitectInput,
    MetaArchitect,
)
from .promise import Promise, PromiseMetrics, collect_metrics
from .reality import ClassificationInput, Reality, RealityClassifier
from .sandbox import SandboxConfig, execute_in_sandbox

T = TypeVar("T")

logger = logging.getLogger(__name__)


# --- Configuration ---


@dataclass(frozen=True)
class JGentConfig(JGentDNA):
    """
    Configuration for JGent coordinator.

    Extends JGentDNA to add runtime-specific configuration.
    DNA provides: max_depth, entropy_budget, decay_factor
    Config adds: stability checking, sandbox settings
    """

    # Override defaults from JGentDNA
    max_depth: int = 3  # Maximum recursion depth
    entropy_budget: float = 1.0  # Initial entropy (from JGentDNA)
    decay_factor: float = 0.5  # Budget decay per depth (from JGentDNA)

    # Derived threshold (collapse when budget falls below)
    entropy_threshold: float = 0.1

    # Runtime configuration (not DNA)
    chaosmonger_enabled: bool = True  # Run stability checks
    test_generation_enabled: bool = True  # Generate accountability tests
    sandbox_timeout: float = 30.0  # Execution timeout in seconds

    # Stability constraints
    max_cyclomatic_complexity: int = 20
    max_branching_factor: int = 5
    allowed_imports: frozenset[str] = field(
        default_factory=lambda: frozenset(
            {"re", "json", "dataclasses", "typing", "datetime", "math"}
        )
    )

    @classmethod
    def from_dna(cls, dna: JGentDNA, **runtime_config) -> "JGentConfig":
        """
        Create config from DNA with runtime overrides.

        Example:
            dna = JGentDNA.germinate(max_depth=5)
            config = JGentConfig.from_dna(dna, sandbox_timeout=60.0)
        """
        return cls.germinate(
            max_depth=dna.max_depth,
            entropy_budget=dna.entropy_budget,
            decay_factor=dna.decay_factor,
            exploration_budget=dna.exploration_budget,
            **runtime_config,
        )


@dataclass(frozen=True)
class JGentInput(Generic[T]):
    """Input to JGent coordinator."""

    intent: str  # What needs to be done
    ground: T  # Fallback value on failure (the "golden parachute")
    context: dict[str, Any] = field(default_factory=dict)  # Available context


@dataclass(frozen=True)
class JGentResult(Generic[T]):
    """Result from JGent coordinator."""

    value: T  # The computed or ground value
    success: bool  # True if computation succeeded
    collapsed: bool  # True if fell back to ground
    collapse_reason: Optional[str] = None
    promise_metrics: Optional[PromiseMetrics] = None
    jit_compiled: bool = False  # True if JIT compilation was used


# --- Test Generation ---


@dataclass(frozen=True)
class GeneratedTest:
    """A test generated for backward accountability."""

    description: str
    test_fn: Callable[[Any], bool]
    confidence: float  # 0.0-1.0


def generate_test_for_intent(intent: str, result: Any) -> GeneratedTest:
    """
    Generate a validation test for a result based on intent.

    This is a simplified heuristic-based implementation.
    Production version would use LLM to generate contextual tests.

    Args:
        intent: What was promised
        result: What was produced

    Returns:
        GeneratedTest with validation function
    """
    intent_lower = intent.lower()

    # Parse intents: result should be parseable/valid
    if any(kw in intent_lower for kw in ["parse", "extract", "tokenize"]):
        return GeneratedTest(
            description=f"Result from '{intent}' should be non-None and valid",
            test_fn=lambda r: r is not None,
            confidence=0.7,
        )

    # Find/search intents: result should be list or None
    if any(kw in intent_lower for kw in ["find", "search", "filter", "select"]):
        return GeneratedTest(
            description=f"Result from '{intent}' should be list or None",
            test_fn=lambda r: r is None or isinstance(r, (list, tuple)),
            confidence=0.6,
        )

    # Validate intents: result should be bool or have 'valid' attribute
    if any(kw in intent_lower for kw in ["validate", "check", "verify"]):
        return GeneratedTest(
            description=f"Result from '{intent}' should indicate validity",
            test_fn=lambda r: isinstance(r, bool) or hasattr(r, "valid"),
            confidence=0.8,
        )

    # Transform intents: result should be non-None
    if any(kw in intent_lower for kw in ["transform", "convert", "map"]):
        return GeneratedTest(
            description=f"Result from '{intent}' should be transformed value",
            test_fn=lambda r: r is not None,
            confidence=0.5,
        )

    # Default: result exists and is not an exception
    return GeneratedTest(
        description=f"Result from '{intent}' should exist",
        test_fn=lambda r: not isinstance(r, Exception),
        confidence=0.4,
    )


# --- JGent Coordinator ---


class JGent(Agent[JGentInput[T], JGentResult[T]], Generic[T]):
    """
    Just-in-Time Agent Coordinator.

    Orchestrates the full J-gents pipeline:
    1. Reality Classification - determine task nature
    2. Promise Tree - build lazy computation structure
    3. JIT Compilation - generate agents on demand
    4. Test-Driven Reality - validate results
    5. Ground Collapse - safe fallback on failure

    The coordinator is derivable from bootstrap agents:
    JGent = RealityClassifier >> (Decomposer | MetaArchitect) >> TestGenerator >> Ground

    Type: JGentInput[T] → JGentResult[T]
    """

    def __init__(
        self,
        config: JGentConfig = JGentConfig(),
        depth: int = 0,
        parent: Optional[JGent[Any]] = None,
    ):
        """
        Initialize JGent coordinator.

        Args:
            config: Configuration for this coordinator
            depth: Current recursion depth (affects entropy budget)
            parent: Parent JGent if this is a child (for tree structure)
        """
        self._config = config
        self._depth = depth
        self._parent = parent
        self._classifier = RealityClassifier()
        self._architect = MetaArchitect()

    @property
    def name(self) -> str:
        return f"JGent[depth={self._depth}]"

    @property
    def entropy_budget(self) -> float:
        """
        Compute entropy budget based on depth.

        Uses DNA decay_factor: budget = initial * (decay_factor ^ depth)
        This gives geometric decay instead of linear.
        """
        return self._config.entropy_budget * (self._config.decay_factor**self._depth)

    @property
    def config(self) -> JGentConfig:
        """Access configuration."""
        return self._config

    async def invoke(self, input: JGentInput[T]) -> JGentResult[T]:
        """
        Execute the J-gents pipeline.

        Pipeline:
        1. Check entropy budget (collapse if exhausted)
        2. Classify reality (DETERMINISTIC, PROBABILISTIC, CHAOTIC)
        3. Based on classification:
           - DETERMINISTIC: Execute directly
           - PROBABILISTIC: Decompose and/or JIT compile
           - CHAOTIC: Collapse to Ground
        4. Validate result with generated test
        5. Return result or collapse to Ground

        Args:
            input: JGentInput with intent, ground, and context

        Returns:
            JGentResult with value, success status, and metrics
        """
        # Create root promise
        root_promise: Promise[T] = Promise(
            intent=input.intent,
            ground=input.ground,
            context=input.context,
            depth=self._depth,
        )

        try:
            # Step 1: Check entropy budget
            if self.entropy_budget < self._config.entropy_threshold:
                return self._collapse(
                    root_promise,
                    f"Entropy budget ({self.entropy_budget:.2f}) below threshold ({self._config.entropy_threshold})",
                )

            # Step 2: Classify reality
            classification = await self._classifier.invoke(
                ClassificationInput(
                    intent=input.intent,
                    context=input.context,
                    entropy_budget=self.entropy_budget,
                )
            )

            logger.debug(
                f"JGent[{self._depth}] classified '{input.intent[:50]}...' as {classification.reality.value} "
                f"(confidence={classification.confidence:.2f})"
            )

            # Step 3: Handle based on reality type
            match classification.reality:
                case Reality.DETERMINISTIC:
                    result = await self._execute_deterministic(root_promise, input)
                case Reality.PROBABILISTIC:
                    result = await self._execute_probabilistic(root_promise, input)
                case Reality.CHAOTIC:
                    return self._collapse(root_promise, classification.reasoning)

            # Step 4: Validate with generated test (if enabled)
            if self._config.test_generation_enabled and result.success:
                test = generate_test_for_intent(input.intent, result.value)
                if not test.test_fn(result.value):
                    logger.warning(
                        f"JGent[{self._depth}] test failed: {test.description}"
                    )
                    return self._collapse(
                        root_promise,
                        f"Accountability test failed: {test.description}",
                    )

            # Collect metrics
            metrics = collect_metrics(root_promise)

            return JGentResult(
                value=result.value,
                success=result.success,
                collapsed=result.collapsed,
                collapse_reason=result.collapse_reason,
                promise_metrics=metrics,
                jit_compiled=result.jit_compiled,
            )

        except Exception as e:
            logger.exception(f"JGent[{self._depth}] unexpected error: {e}")
            return self._collapse(root_promise, f"Unexpected error: {e}")

    async def _execute_deterministic(
        self, promise: Promise[T], input: JGentInput[T]
    ) -> JGentResult[T]:
        """
        Execute a DETERMINISTIC task directly.

        For now, this returns a placeholder. In production, this would:
        - Look up existing tools/agents that match the intent
        - Execute the matching tool
        - Return the result

        Args:
            promise: The promise tracking this execution
            input: Original JGent input

        Returns:
            JGentResult with computed value
        """
        promise.mark_resolving()

        # TODO: Implement tool lookup and execution
        # For now, we simulate by returning the ground value
        # with a note that this is a placeholder

        # In real implementation, this would:
        # 1. Match intent to available tools (file read, API call, etc.)
        # 2. Execute the tool
        # 3. Return the result

        logger.debug(
            f"JGent[{self._depth}] DETERMINISTIC: returning ground (placeholder)"
        )

        promise.mark_resolved(input.ground)

        return JGentResult(
            value=input.ground,
            success=True,
            collapsed=False,
            jit_compiled=False,
        )

    async def _execute_probabilistic(
        self, promise: Promise[T], input: JGentInput[T]
    ) -> JGentResult[T]:
        """
        Execute a PROBABILISTIC task via decomposition or JIT compilation.

        Steps:
        1. Check if existing agent can handle this
        2. If not, JIT compile a new agent
        3. Execute in sandbox
        4. Validate result

        Args:
            promise: The promise tracking this execution
            input: Original JGent input

        Returns:
            JGentResult with computed value
        """
        promise.mark_resolving()

        # Check depth limit
        if self._depth >= self._config.max_depth:
            return self._collapse(
                promise,
                f"Max depth ({self._config.max_depth}) reached",
            )

        # Try to JIT compile an agent for this task
        try:
            # Generate agent source
            architect_input = ArchitectInput(
                intent=input.intent,
                context=input.context,
                constraints=ArchitectConstraints(
                    entropy_budget=self.entropy_budget,
                    max_cyclomatic_complexity=self._config.max_cyclomatic_complexity,
                    max_branching_factor=self._config.max_branching_factor,
                    allowed_imports=self._config.allowed_imports,
                ),
            )

            source = await self._architect.invoke(architect_input)

            # Stability check (if enabled)
            if self._config.chaosmonger_enabled:
                stability = analyze_stability(
                    source_code=source.source,
                    entropy_budget=self.entropy_budget,
                    config=StabilityConfig(
                        max_cyclomatic_complexity=self._config.max_cyclomatic_complexity,
                        max_branching_factor=self._config.max_branching_factor,
                        allowed_imports=self._config.allowed_imports,
                    ),
                )

                if not stability.is_stable:
                    return self._collapse(
                        promise,
                        f"Chaosmonger rejected: {', '.join(stability.violations)}",
                    )

            # Execute in sandbox
            sandbox_config = SandboxConfig(
                timeout_seconds=self._config.sandbox_timeout,
                allowed_imports=self._config.allowed_imports,
                chaosmonger_check=False,  # Already checked above
            )

            # Determine method to call based on agent pattern
            method_name = self._get_method_for_class(source.class_name)

            # For now, we don't have real input data to pass
            # In production, context would contain the actual data
            test_input = input.context.get("input_data", "")

            result = await execute_in_sandbox(
                source=source,
                method_name=method_name,
                args=(test_input,),
                config=sandbox_config,
            )

            if result.success:
                promise.mark_resolved(result.output)
                return JGentResult(
                    value=result.output,
                    success=True,
                    collapsed=False,
                    jit_compiled=True,
                )
            else:
                return self._collapse(
                    promise,
                    f"Sandbox execution failed: {result.error}",
                )

        except Exception as e:
            return self._collapse(promise, f"JIT compilation failed: {e}")

    def _get_method_for_class(self, class_name: str) -> str:
        """
        Determine the method to call based on class name pattern.

        Args:
            class_name: The JIT-compiled class name

        Returns:
            Method name to invoke
        """
        class_lower = class_name.lower()

        if "parser" in class_lower:
            return "parse"
        elif "filter" in class_lower:
            return "filter"
        elif "transformer" in class_lower:
            return "transform"
        elif "analyzer" in class_lower:
            return "analyze"
        elif "validator" in class_lower:
            return "validate"
        else:
            return "invoke"

    def _collapse(self, promise: Promise[T], reason: str) -> JGentResult[T]:
        """
        Collapse to Ground (the golden parachute).

        Args:
            promise: The promise to collapse
            reason: Why we're collapsing

        Returns:
            JGentResult with ground value and collapse info
        """
        logger.info(f"JGent[{self._depth}] collapsing to Ground: {reason}")

        promise.mark_collapsed(reason)
        metrics = collect_metrics(promise)

        return JGentResult(
            value=promise.ground,
            success=False,
            collapsed=True,
            collapse_reason=reason,
            promise_metrics=metrics,
            jit_compiled=False,
        )

    def spawn_child(self) -> JGent[Any]:
        """
        Spawn a child JGent with incremented depth.

        Returns:
            New JGent with depth+1 and reduced entropy budget
        """
        return JGent(
            config=self._config,
            depth=self._depth + 1,
            parent=self,
        )


# --- Convenience Functions ---


async def jgent(
    intent: str,
    ground: T,
    context: Optional[dict[str, Any]] = None,
    config: Optional[JGentConfig] = None,
) -> JGentResult[T]:
    """
    Convenience function to run a J-gent task.

    Args:
        intent: What needs to be done
        ground: Fallback value on failure
        context: Optional context dictionary
        config: Optional JGent configuration

    Returns:
        JGentResult with value and execution info

    Example:
        >>> result = await jgent(
        ...     intent="Parse JSON config file",
        ...     ground={},  # Empty dict as fallback
        ...     context={"input_data": '{"key": "value"}'},
        ... )
        >>> print(result.value)
    """
    coordinator = JGent(config=config or JGentConfig())
    return await coordinator.invoke(
        JGentInput(
            intent=intent,
            ground=ground,
            context=context or {},
        )
    )


def jgent_sync(
    intent: str,
    ground: T,
    context: Optional[dict[str, Any]] = None,
    config: Optional[JGentConfig] = None,
) -> JGentResult[T]:
    """
    Synchronous version of jgent for non-async contexts.

    Args:
        intent: What needs to be done
        ground: Fallback value on failure
        context: Optional context dictionary
        config: Optional JGent configuration

    Returns:
        JGentResult with value and execution info
    """
    return asyncio.run(jgent(intent, ground, context, config))
