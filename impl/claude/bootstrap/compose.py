"""
Compose (∘) - The agent-that-makes-agents.

Type: (Agent, Agent) → Agent
Law: Compose(f, g) = g ∘ f

Takes two agents and yields their sequential composition.

Why irreducible: Composition IS the fundamental operation.
What it grounds: All agent pipelines. The C-gents category.
"""

from typing import Awaitable, Callable, Optional, TypeVar

from .types import Agent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


class ComposedAgent(Agent[A, C]):
    """
    A composed agent: the result of first >> second.

    Applies first, then second. Type-safe pipeline.
    """

    def __init__(self, first: Agent[A, B], second: Agent[B, C]):
        self._first = first
        self._second = second
        self._name = f"({first.name} >> {second.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> C:
        """Apply first agent, then second agent."""
        intermediate = await self._first.invoke(input)
        return await self._second.invoke(intermediate)

    def __repr__(self) -> str:
        return self._name


class FixComposedAgent(Agent[A, B]):
    """
    Agent composed with Fix-pattern iteration.

    Applies: input -> agent -> check -> (retry if needed) -> output

    Enables patterns like:
        Create >> Judge >> retry until accept
        Transform >> Validate >> retry until valid

    Type: A -> (A -> B) -> (B -> bool) -> B
    """

    def __init__(
        self,
        agent: Agent[A, B],
        refine: Agent[tuple[A, B], A],
        should_retry: Callable[[B], Awaitable[bool]],
        max_iterations: int = 10,
    ):
        """
        Create iterative composition with retry logic.

        agent: The main agent to apply
        refine: Agent that produces new input from (original, failed_output)
        should_retry: Async predicate - True means retry
        max_iterations: Maximum retry attempts
        """
        self._agent = agent
        self._refine = refine
        self._should_retry = should_retry
        self._max_iterations = max_iterations
        self._name = f"Fix({agent.name})"

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: A) -> B:
        """Apply agent iteratively until should_retry returns False."""
        current_input = input
        
        for iteration in range(self._max_iterations):
            output = await self._agent.invoke(current_input)
            
            if not await self._should_retry(output):
                return output  # Success
            
            if iteration < self._max_iterations - 1:
                # Refine input based on failed output
                current_input = await self._refine.invoke((input, output))
        
        # Max iterations reached - return last output
        return output
    
    def __repr__(self) -> str:
        return self._name


def compose(first: Agent[A, B], second: Agent[B, C]) -> Agent[A, C]:
    """
    Compose two agents into a pipeline.

    The fundamental operation. Creates an agent that:
    1. Applies `first` to input
    2. Applies `second` to the result

    Laws:
    - Associativity: (f >> g) >> h == f >> (g >> h)
    - Identity: Id >> f == f, f >> Id == f

    Usage:
        pipeline = compose(validate, transform)
        # or via operator:
        pipeline = validate >> transform

    Example:
        Pipeline = Judge(config) >> Create(config) >> Spawn(session)
    """
    return ComposedAgent(first, second)


def fix_compose(
    agent: Agent[A, B],
    refine: Agent[tuple[A, B], A],
    should_retry: Callable[[B], Awaitable[bool]],
    max_iterations: int = 10,
) -> Agent[A, B]:
    """
    Compose agent with Fix-pattern retry logic.
    
    Creates an agent that iteratively applies:
        1. Run agent on current input
        2. Check output with should_retry
        3. If retry needed, refine input and loop
        4. If accepted, return output
    
    This demonstrates how procedural composition enables functional
    recursion schemes: the Fix pattern composes WITH agents.
    
    Usage:
        # Retry pattern: generate until judge accepts
        generator = Create(config)
        refiner = Revise(config)  # Takes (original, rejected) -> revised
        checker = lambda output: judge.invoke(output).type == REJECT
        
        stable_generator = fix_compose(
            agent=generator,
            refine=refiner,
            should_retry=checker,
            max_iterations=5
        )
        
        # Now: stable_generator will retry up to 5 times
        result = await stable_generator.invoke(spec)
    
    This is Fix specialized for agent pipelines. Compare with Fix agent:
        Fix: iterate (A -> A) until fixed point
        FixCompose: iterate (A -> B) until predicate accepts
    """
    return FixComposedAgent(agent, refine, should_retry, max_iterations)


# Idiom: Compose, Don't Concatenate
#
# If a function does A then B then C, it should BE `A >> B >> C`.
#
# Benefits:
# - Each step is testable in isolation
# - Clear data flow between steps
# - Steps are replaceable/mockable
# - Debugging: "which step failed?"
#
# Anti-pattern: 130-line methods mixing validation, I/O, state, errors.

# Idiom: Fix Composes With Agents
#
# Iteration patterns (retry, polling, refinement) should use Fix composition:
#   fix_compose(agent, refiner, predicate) instead of while loops
#
# Benefits:
# - Declarative: "retry until predicate" vs imperative loops
# - Composable: Fix-composed agents are still agents
# - Traceable: Iteration count and history available
# - Testable: Mock predicates and refiners
#
# Example: Generate >> Judge >> Retry
#   stable = fix_compose(generate, revise, is_rejected)
#   result = await stable.invoke(spec)
