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
R = TypeVar("R")  # Refinement data type


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

    Decoupled refinement: analyzer (B -> R) extracts failure info,
    transformer ((A, R) -> A) applies corrections to input.

    This enables reusable analyzers across different agent types.
    """

    def __init__(
        self,
        agent: Agent[A, B],
        analyze: Agent[B, R],
        transform: Agent[tuple[A, R], A],
        should_retry: Callable[[B], Awaitable[bool]],
        max_iterations: int = 10,
    ):
        """
        Create iterative composition with decoupled refinement.

        agent: The main agent to apply
        analyze: Extract refinement data from failed output (B -> R)
        transform: Apply refinement to input ((A, R) -> A)
        should_retry: Async predicate - True means retry
        max_iterations: Maximum retry attempts
        """
        self._agent = agent
        self._analyze = analyze
        self._transform = transform
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
                # Analyze failure, then transform input
                refinement = await self._analyze.invoke(output)
                current_input = await self._transform.invoke((input, refinement))
        
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
    analyze: Agent[B, R],
    transform: Agent[tuple[A, R], A],
    should_retry: Callable[[B], Awaitable[bool]],
    max_iterations: int = 10,
) -> Agent[A, B]:
    """
    Compose agent with Fix-pattern retry logic using decoupled refinement.
    
    Splits refinement into two morphisms:
    - analyze: B -> R (extract failure information)
    - transform: (A, R) -> A (apply corrections to input)
    
    This separation enables:
    1. Reusable analyzers across different agent types
    2. Pure failure analysis (B -> R) independent of input type
    3. Explicit refinement data structures (R)
    
    Usage:
        # Decoupled retry: analyzer is reusable
        generator = Create(config)
        
        # Analyzer: extract what's wrong (pure, reusable)
        error_analyzer = ExtractErrors()  # JudgmentResult -> ErrorList
        
        # Transformer: apply corrections to specific input type
        prompt_fixer = FixPrompt()  # (Prompt, ErrorList) -> Prompt
        
        # Checker: predicate for retry
        checker = lambda output: output.verdict == REJECT
        
        stable_generator = fix_compose(
            agent=generator,
            analyze=error_analyzer,
            transform=prompt_fixer,
            should_retry=checker,
            max_iterations=5
        )
        
        # Now: error_analyzer can be reused with different generators
        result = await stable_generator.invoke(spec)
    
    Compare with monolithic refiner (A, B) -> A:
    - Monolithic: couples failure analysis to input reconstruction
    - Decoupled: analyzer (B -> R) reusable, transformer (A, R -> A) specific
    """
    return FixComposedAgent(agent, analyze, transform, should_retry, max_iterations)


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
#   fix_compose(agent, analyzer, transformer, predicate) instead of while loops
#
# Benefits:
# - Declarative: "retry until predicate" vs imperative loops
# - Composable: Fix-composed agents are still agents
# - Traceable: Iteration count and history available
# - Testable: Mock predicates, analyzers, and transformers
# - Reusable: Analyzers (B -> R) work across agent types
#
# Example: Generate >> Judge >> Retry
#   stable = fix_compose(generate, extract_errors, fix_prompt, is_rejected)
#   result = await stable.invoke(spec)