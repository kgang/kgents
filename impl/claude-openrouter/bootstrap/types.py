"""
Bootstrap Types - Core type definitions for kgents bootstrap agents.

These types form the foundation for the 7 irreducible agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, TypeVar, Optional, Union

# Type variables for generic agent types
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type
C = TypeVar("C")  # Third type for composition
E = TypeVar("E")  # Error type


# Algebraic sum type for results
@dataclass(frozen=True)
class Ok(Generic[A]):
    """Success variant of Result."""
    value: A
    
    def is_ok(self) -> bool:
        return True
    
    def is_err(self) -> bool:
        return False


@dataclass(frozen=True)
class Err(Generic[E]):
    """Error variant of Result."""
    error: E
    
    def is_ok(self) -> bool:
        return False
    
    def is_err(self) -> bool:
        return True


# Result sum type: Ok[A] | Err[E]
Result = Union[Ok[A], Err[E]]


def match_result(
    result: Result[A, E],
    on_ok: Callable[[A], B],
    on_err: Callable[[E], B]
) -> B:
    """
    Exhaustive pattern matching on Result.
    
    Forces handling of both Ok and Err cases.
    """
    if isinstance(result, Ok):
        return on_ok(result.value)
    elif isinstance(result, Err):
        return on_err(result.error)
    else:
        # Exhaustiveness check - should never reach here
        raise TypeError(f"Invalid Result variant: {type(result)}")


class Agent(ABC, Generic[A, B]):
    """
    Base agent interface.

    An agent is a morphism in the kgents category:
    - Has typed input and output
    - Is composable with other agents
    - Can operate in functional mode (invoke) or autonomous mode (loop)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier."""
        pass

    @abstractmethod
    async def invoke(self, input: A) -> B:
        """
        Functional mode: input → transform → output.

        This is the primary operation. All agents must implement this.
        """
        pass

    def __rshift__(self, other: "Agent[B, C]") -> "Agent[A, C]":
        """
        Composition operator: self >> other.

        Creates a new agent that applies self, then other.
        Enables: Pipeline = A >> B >> C
        """
        from .compose import compose
        return compose(self, other)

    def __repr__(self) -> str:
        return f"<Agent:{self.name}>"


@dataclass
class FixConfig:
    """Configuration for Fix agent iteration."""
    max_iterations: int = 10
    min_iterations: int = 1
    should_continue: Callable[[Any], bool] = lambda _: True


class Fix(Agent[A, B], Generic[A, B]):
    """
    Fix-point agent for iteration and retry patterns.
    
    Applies an agent repeatedly until convergence or limit reached.
    This is the canonical pattern for self-improvement loops.
    
    Example:
        improve = Fix(refine_agent, max_iterations=5)
        result = await improve.invoke(draft)
    """
    
    def __init__(
        self,
        agent: Agent[A, A],
        config: FixConfig = FixConfig()
    ):
        self._agent = agent
        self._config = config
    
    @property
    def name(self) -> str:
        return f"Fix({self._agent.name})"
    
    async def invoke(self, input: A) -> B:
        """
        Apply agent repeatedly until convergence.
        
        Returns final output after iteration limit or early termination.
        """
        current = input
        
        for i in range(self._config.max_iterations):
            current = await self._agent.invoke(current)
            
            if i >= self._config.min_iterations - 1:
                if not self._config.should_continue(current):
                    break
        
        return current  # type: ignore


# Verdict types for Judge
class VerdictType(Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"


@dataclass
class Verdict:
    """
    Result of Judge evaluating an agent against principles.
    """
    type: VerdictType
    reasons: list[str] = field(default_factory=list)
    revisions: Optional[list[str]] = None  # Suggestions if REVISE

    @classmethod
    def accept(cls, reasons: list[str] | None = None) -> "Verdict":
        return cls(VerdictType.ACCEPT, reasons or [])

    @classmethod
    def reject(cls, reasons: list[str]) -> "Verdict":
        return cls(VerdictType.REJECT, reasons)

    @classmethod
    def revise(cls, reasons: list[str], revisions: list[str]) -> "Verdict":
        return cls(VerdictType.REVISE, reasons, revisions)


# Tension types for Contradict
class TensionMode(Enum):
    LOGICAL = "logical"       # A and ¬A
    PRAGMATIC = "pragmatic"   # A recommends X, B recommends ¬X
    AXIOLOGICAL = "axiological"  # Serves value V vs ¬V
    TEMPORAL = "temporal"     # Past-self vs present-self


@dataclass
class Tension:
    """
    A contradiction detected between two outputs.
    """
    mode: TensionMode
    thesis: Any
    antithesis: Any
    description: str
    severity: float = 0.5  # 0.0 = minor, 1.0 = critical

    def __repr__(self) -> str:
        return f"Tension({self.mode.value}: {self.description})"


# Resolution types for Sublate
class ResolutionType(Enum):
    PRESERVE = "preserve"  # Keep both as valid in different contexts
    NEGATE = "negate"      # One is wrong
    ELEVATE = "elevate"    # Synthesize to higher level
    HOLD = "hold"          # Too soon to resolve


@dataclass
class Synthesis:
    """
    Result of Sublate resolving a tension.
    """
    resolution_type: ResolutionType
    result: Any
    explanation: str
    preserved: list[Any] = field(default_factory=list)
    negated: list[Any] = field(default_factory=list)


@dataclass
class HoldTension:
    """
    Explicit decision to not resolve a tension yet.
    """
    tension: Tension
    reason: str
    revisit_conditions: list[str] = field(default_factory=list)


# Ground types
@dataclass
class PersonaSeed:
    """Core identity and preferences from Ground."""
    name: str
    roles: list[str]
    preferences: dict[str, Any]
    patterns: dict[str, list[str]]
    values: list[str]
    dislikes: list[str]


@dataclass
class WorldSeed:
    """Environmental context from Ground."""
    date: str
    context: dict[str, Any]
    active_projects: list[dict[str, Any]]


@dataclass
class Facts:
    """
    The output of Ground - irreducible facts about person and world.
    """
    persona: PersonaSeed
    world: WorldSeed
    history: dict[str, Any] = field(default_factory=dict)


# Principles for Judge
@dataclass
class Principle:
    """A single principle from the 7 core principles."""
    name: str
    question: str
    check: Callable[[Agent], bool]


@dataclass
class Principles:
    """The complete set of evaluation criteria for Judge."""
    tasteful: Principle
    curated: Principle
    ethical: Principle
    joy_inducing: Principle
    composable: Principle
    heterarchical: Principle
    generative: Principle

    def all(self) -> list[Principle]:
        return [
            self.tasteful,
            self.curated,
            self.ethical,
            self.joy_inducing,
            self.composable,
            self.heterarchical,
            self.generative,
        ]
