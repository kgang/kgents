"""
kgents Bootstrap Types

Core type definitions for the 7 irreducible bootstrap agents.
These types form the category-theoretic foundation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, TypeVar, Awaitable
from datetime import datetime

# =============================================================================
# TYPE VARIABLES
# =============================================================================

I = TypeVar('I')  # Input type
O = TypeVar('O')  # Output type
A = TypeVar('A')  # Generic type
B = TypeVar('B')
C = TypeVar('C')

# =============================================================================
# AGENT PRIMITIVES
# =============================================================================

class Agent(ABC, Generic[I, O]):
    """
    An Agent is a morphism: Input → Output
    Agents form a category with composition and identity.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier"""
        pass

    @property
    @abstractmethod
    def genus(self) -> str:
        """Which letter category (bootstrap, a, b, c, etc.)"""
        pass

    @property
    @abstractmethod
    def purpose(self) -> str:
        """One-sentence description of why this agent exists"""
        pass

    @abstractmethod
    async def invoke(self, input: I) -> O:
        """The agent's core transformation"""
        pass

    def __repr__(self) -> str:
        return f"<Agent:{self.name} ({self.genus})>"


# =============================================================================
# VERDICT (Judge output)
# =============================================================================

class VerdictStatus(Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"


@dataclass(frozen=True)
class Verdict:
    status: VerdictStatus
    reason: str | None = None
    suggestion: str | None = None

    @classmethod
    def accept(cls) -> 'Verdict':
        return cls(status=VerdictStatus.ACCEPT)

    @classmethod
    def reject(cls, reason: str) -> 'Verdict':
        return cls(status=VerdictStatus.REJECT, reason=reason)

    @classmethod
    def revise(cls, suggestion: str) -> 'Verdict':
        return cls(status=VerdictStatus.REVISE, suggestion=suggestion)


# =============================================================================
# PRINCIPLES (Judge criteria)
# =============================================================================

class Principle(Enum):
    TASTEFUL = "tasteful"
    CURATED = "curated"
    ETHICAL = "ethical"
    JOY_INDUCING = "joy-inducing"
    COMPOSABLE = "composable"
    HETERARCHICAL = "heterarchical"


PRINCIPLE_QUESTIONS = {
    Principle.TASTEFUL: "Does this agent have a clear, justified purpose?",
    Principle.CURATED: "Does this add unique value, or does something similar exist?",
    Principle.ETHICAL: "Does this respect human agency and privacy?",
    Principle.JOY_INDUCING: "Would I enjoy interacting with this?",
    Principle.COMPOSABLE: "Can this work with other agents?",
    Principle.HETERARCHICAL: "Can this agent both lead and follow? Does it avoid fixed hierarchy?",
}


# =============================================================================
# TENSION (Contradict output)
# =============================================================================

class TensionMode(Enum):
    LOGICAL = "logical"        # A and ¬A
    PRAGMATIC = "pragmatic"    # A recommends X, B recommends ¬X
    AXIOLOGICAL = "axiological"  # Serves value V vs serves ¬V
    TEMPORAL = "temporal"      # Past-self said X, present-self says ¬X


@dataclass(frozen=True)
class Tension:
    mode: TensionMode
    thesis: Any
    antithesis: Any
    description: str


# =============================================================================
# SYNTHESIS (Sublate output)
# =============================================================================

@dataclass(frozen=True)
class Synthesis:
    """Result of successful sublation"""
    preserved: tuple[Any, ...]
    negated: tuple[Any, ...]
    synthesis: Any


@dataclass(frozen=True)
class HoldTension:
    """Result when tension should not yet be resolved"""
    reason: str
    tension: Tension


SynthesisResult = Synthesis | HoldTension


# =============================================================================
# GROUND (Persona seed)
# =============================================================================

@dataclass
class CommunicationPrefs:
    style: str
    length: str
    formality: str


@dataclass
class AestheticsPrefs:
    design: str
    prose: str


@dataclass
class Preferences:
    communication: CommunicationPrefs
    aesthetics: AestheticsPrefs
    values: list[str]
    dislikes: list[str]


@dataclass
class Patterns:
    thinking: list[str]
    decision_making: list[str]
    communication: list[str]


@dataclass
class Project:
    name: str
    status: str
    goals: list[str]


@dataclass
class Context:
    current_focus: str
    recent_interests: list[str]
    active_projects: list[Project]


@dataclass
class Identity:
    name: str
    roles: list[str]


@dataclass
class PersonaState:
    identity: Identity
    preferences: Preferences
    patterns: Patterns
    context: Context
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WorldState:
    date: str
    runtime: str


@dataclass
class GroundState:
    persona: PersonaState
    world: WorldState


# =============================================================================
# FIX (Fixed-point iteration)
# =============================================================================

@dataclass
class FixResult(Generic[A]):
    value: A
    iterations: int
    stable: bool


@dataclass
class FixConfig:
    max_iterations: int = 100
    equality_check: Callable[[Any, Any], bool] | None = None
