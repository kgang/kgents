"""
Bootstrap Types - Foundation types for all bootstrap agents.

This module defines the core abstractions:
- Agent[A, B]: The base agent type (morphism A → B)
- ComposedAgent: Sequential composition (f >> g)
- Result[T, E]: Either-based error handling (Ok | Err)
- Core domain types for the 7 bootstrap agents

The bootstrap agents are the irreducible kernel from which all of kgents
can be regenerated. See spec/bootstrap.md for the full specification.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

# --- Type Variables ---

A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type
C = TypeVar("C")  # Third type for composition
T = TypeVar("T")  # Generic success type
E = TypeVar("E")  # Generic error type

# Variance-correct type variables for Protocol
A_contra = TypeVar("A_contra", contravariant=True)  # Input (contravariant)
B_co = TypeVar("B_co", covariant=True)  # Output (covariant)


# --- Result Type (Either-based error handling) ---


@dataclass(frozen=True)
class Ok(Generic[T]):
    """Success result containing value."""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        """Extract the value."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Extract value or return default."""
        return self.value

    def map(self, f: Callable[[T], B]) -> Result[B, Any]:
        """Apply function to contained value."""
        return Ok(f(self.value))


@dataclass(frozen=True)
class Err(Generic[E]):
    """Error result containing error information."""

    error: E
    message: str = ""
    recoverable: bool = True

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> Any:
        """Raises exception - can't unwrap an error."""
        raise RuntimeError(f"Cannot unwrap Err: {self.message or self.error}")

    def unwrap_or(self, default: T) -> T:
        """Return default value."""
        return default

    def map(self, f: Callable[[Any], B]) -> Result[B, E]:
        """Map is identity for errors - just propagate the error."""
        return Err(self.error, self.message, self.recoverable)


# Result is Either[Err, Ok] - following Railway Oriented Programming
Result = Union[Ok[T], Err[E]]


def ok(value: T) -> Ok[T]:
    """Create an Ok result."""
    return Ok(value)


def err(error: E, message: str = "", recoverable: bool = True) -> Err[E]:
    """Create an Err result."""
    return Err(error=error, message=message, recoverable=recoverable)


# --- Agent Base Class ---


@runtime_checkable
class AgentProtocol(Protocol[A_contra, B_co]):
    """Protocol for agent-like objects (structural typing)."""

    @property
    def name(self) -> str: ...

    async def invoke(self, input: A_contra) -> B_co: ...


class Agent(ABC, Generic[A, B]):
    """
    Abstract base class for all agents.

    An agent is a morphism A → B in the category of agents:
    - Has a defined input type A and output type B
    - Can be invoked with input to produce output
    - Can be composed with other agents via >>

    Laws (must hold for all agents):
    - Identity: Id >> f ≡ f ≡ f >> Id
    - Associativity: (f >> g) >> h ≡ f >> (g >> h)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this agent."""
        pass

    @abstractmethod
    async def invoke(self, input: A) -> B:
        """
        Invoke the agent with input and produce output.

        This is the core operation of an agent.
        """
        pass

    def __rshift__(self, other: Agent[B, C]) -> ComposedAgent[A, B, C]:
        """
        Composition operator: self >> other.

        Produces an agent that runs self, then other on self's output.
        Type: Agent[A,B] >> Agent[B,C] → Agent[A,C]
        """
        return ComposedAgent(self, other)


# --- Composed Agent ---


class ComposedAgent(Agent[A, C], Generic[A, B, C]):
    """
    Sequential composition of two agents: f >> g.

    Given f: A → B and g: B → C, produces an agent A → C
    that runs f, then g on f's output.

    This is the fundamental composition operation that makes
    agents form a category.
    """

    def __init__(self, f: Agent[A, B], g: Agent[B, C]):
        self._f = f
        self._g = g

    @property
    def name(self) -> str:
        return f"({self._f.name} >> {self._g.name})"

    async def invoke(self, input: A) -> C:
        """Execute f, then g."""
        intermediate: B = await self._f.invoke(input)
        return await self._g.invoke(intermediate)

    @property
    def first(self) -> Agent[A, B]:
        """Access first agent in composition."""
        return self._f

    @property
    def second(self) -> Agent[B, C]:
        """Access second agent in composition."""
        return self._g


# --- Tension and Synthesis Types (for Contradict/Sublate) ---


class TensionMode(Enum):
    """Types of tension that can be detected between outputs."""

    LOGICAL = "logical"  # A and ¬A
    PRAGMATIC = "pragmatic"  # A recommends X, B recommends ¬X
    AXIOLOGICAL = "axiological"  # Serves value V vs ¬V
    TEMPORAL = "temporal"  # Past-self vs present-self
    AESTHETIC = "aesthetic"  # Style/taste conflicts


@dataclass(frozen=True)
class Tension:
    """
    A detected contradiction between two outputs.

    Produced by Contradict, consumed by Sublate.
    """

    thesis: Any
    antithesis: Any
    mode: TensionMode
    severity: float  # 0.0 (minor) to 1.0 (fundamental)
    description: str


@dataclass(frozen=True)
class Synthesis:
    """
    Resolution of a tension via Hegelian sublation.

    The synthesis preserves elements from both thesis and antithesis
    while elevating to a higher level of understanding.
    """

    resolution_type: str  # "preserve", "negate", "elevate"
    result: Any
    explanation: str
    preserved_from_thesis: tuple[str, ...] = ()
    preserved_from_antithesis: tuple[str, ...] = ()


@dataclass(frozen=True)
class HoldTension:
    """
    Decision to consciously hold a tension rather than resolve it.

    Sometimes tensions should not be resolved prematurely.
    This captures the wisdom to wait.
    """

    tension: Tension
    why_held: str
    revisit_conditions: tuple[str, ...] = ()


# --- Verdict Types (for Judge) ---


class VerdictType(Enum):
    """Possible outcomes of judgment."""

    ACCEPT = "accept"  # Agent passes all principles
    REVISE = "revise"  # Agent needs modification
    REJECT = "reject"  # Agent fundamentally flawed


@dataclass(frozen=True)
class PartialVerdict:
    """Verdict from a single mini-judge (one principle)."""

    principle: str
    passed: bool
    reasons: tuple[str, ...] = ()
    confidence: float = 1.0


@dataclass(frozen=True)
class Verdict:
    """
    Complete verdict from Judge.

    Aggregates partial verdicts from seven mini-judges.
    """

    type: VerdictType
    partial_verdicts: tuple[PartialVerdict, ...] = ()
    revisions: Optional[tuple[str, ...]] = None
    reasoning: str = ""

    @staticmethod
    def accept(reasons: Optional[list[str]] = None) -> "Verdict":
        """Factory for ACCEPT verdict."""
        return Verdict(
            type=VerdictType.ACCEPT,
            reasoning="; ".join(reasons) if reasons else "Accepted",
        )

    @staticmethod
    def reject(reasons: Optional[list[str]] = None) -> "Verdict":
        """Factory for REJECT verdict."""
        return Verdict(
            type=VerdictType.REJECT,
            reasoning="; ".join(reasons) if reasons else "Rejected",
        )

    @staticmethod
    def revise(revisions: list[str], reasons: Optional[list[str]] = None) -> "Verdict":
        """Factory for REVISE verdict with suggested changes."""
        return Verdict(
            type=VerdictType.REVISE,
            revisions=tuple(revisions),
            reasoning="; ".join(reasons) if reasons else "Needs revision",
        )


# --- Principles (Judge's criteria) ---


@dataclass(frozen=True)
class Principles:
    """
    The seven principles that Judge evaluates against.

    Each principle has a name, description, and check function.
    """

    # The seven principle names
    TASTEFUL = "tasteful"
    CURATED = "curated"
    ETHICAL = "ethical"
    JOYFUL = "joyful"
    COMPOSABLE = "composable"
    HETERARCHICAL = "heterarchical"
    GENERATIVE = "generative"

    @classmethod
    def all(cls) -> tuple[str, ...]:
        """Return all principle names."""
        return (
            cls.TASTEFUL,
            cls.CURATED,
            cls.ETHICAL,
            cls.JOYFUL,
            cls.COMPOSABLE,
            cls.HETERARCHICAL,
            cls.GENERATIVE,
        )

    @staticmethod
    def check(principle: str, agent: Agent[Any, Any]) -> PartialVerdict:
        """
        Check if an agent satisfies a principle.

        This is a placeholder - actual checks require LLM or heuristics.
        Mini-judges should override this with real logic.
        """
        raise NotImplementedError(
            f"Principle check for '{principle}' not implemented. "
            "Mini-judges should provide specific implementations."
        )


# --- Ground Types (persona and world seed) ---


@dataclass(frozen=True)
class PersonaSeed:
    """
    The irreducible facts about a persona.

    Loaded from spec/k-gent/persona.md by Ground agent.
    """

    name: str
    roles: tuple[str, ...] = ()
    values: tuple[str, ...] = ()
    communication_style: str = ""
    heuristics: tuple[str, ...] = ()
    dislikes: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorldSeed:
    """
    The irreducible facts about the world state.

    Includes date, context, and any active projects.
    """

    date: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Facts:
    """
    Complete grounded facts returned by Ground agent.

    Contains persona, world state, and optional history.
    """

    persona: PersonaSeed
    world: WorldSeed
    history: Optional[dict[str, Any]] = None


# --- Fix Types (fixed-point iteration) ---


@dataclass(frozen=True)
class FixConfig(Generic[A]):
    """Configuration for fixed-point iteration."""

    max_iterations: int = 100
    equality_check: Callable[[A, A], bool] = field(
        default_factory=lambda: lambda a, b: a == b
    )
    should_continue: Callable[[A, int], bool] = field(
        default_factory=lambda: lambda a, i: True
    )
    # J-gents entropy budget: diminishes with recursion depth
    # None means no budget tracking (backward compatible)
    entropy_budget: Optional[float] = None
    # Performance: Bounded history (H6 optimization)
    # If set, keep only last N iterations in history (sliding window)
    # None means unbounded (keep all iterations, backward compatible)
    # Recommended: 10-50 for most use cases
    max_history_size: Optional[int] = None


@dataclass(frozen=True)
class FixResult(Generic[A]):
    """Result of fixed-point iteration."""

    value: A
    converged: bool
    iterations: int
    history: tuple[A, ...] = ()
    proximity: float = 0.0  # Distance from fixed point (adaptive convergence metric)
    # J-gents entropy tracking: remaining budget after iteration
    entropy_remaining: Optional[float] = None


# --- Contradict Input/Output Types ---


@dataclass(frozen=True)
class ContradictInput:
    """Input to Contradict agent."""

    a: Any
    b: Any
    context: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class ContradictResult:
    """Result from Contradict agent."""

    tensions: tuple[Tension, ...] = ()
    no_tension: bool = True


# --- Sublate Input/Output Types ---


@dataclass(frozen=True)
class SublateInput:
    """Input to Sublate agent."""

    tensions: tuple[Tension, ...]
    context: Optional[dict[str, Any]] = None


SublateResult = Union[Synthesis, HoldTension]


# --- Judge Input/Output Types ---


@dataclass(frozen=True)
class JudgeInput:
    """Input to Judge agent."""

    agent: Agent[Any, Any]
    principles: Optional[tuple[str, ...]] = None  # None = all principles
    context: Optional[dict[str, Any]] = None


# --- Void Type (for Ground input) ---


class Void:
    """
    The void type - Ground's input.

    Represents "no meaningful input" - Ground produces facts from nothing.
    """

    _instance: Optional[Void] = None

    def __new__(cls) -> Void:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "Void()"


# Singleton instance
VOID = Void()
