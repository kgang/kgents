"""
Agent Genera Type Definitions

Shared types for A, B, C, H, K agent implementations.
These types complement bootstrap/types.py with genus-specific structures.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


# =============================================================================
# K-GENT TYPES (Kent Simulacra)
# =============================================================================

class DialogueMode(Enum):
    """K-gent dialogue interaction modes"""
    REFLECT = "reflect"      # Mirror back thinking
    ADVISE = "advise"        # Offer aligned suggestions
    CHALLENGE = "challenge"  # Push back constructively
    EXPLORE = "explore"      # Help explore possibilities


class QueryAspect(Enum):
    """Aspects of persona that can be queried"""
    PREFERENCE = "preference"
    PATTERN = "pattern"
    CONTEXT = "context"
    ALL = "all"


class UpdateOperation(Enum):
    """Operations for persona updates"""
    ADD = "add"
    MODIFY = "modify"
    REMOVE = "remove"


@dataclass
class PersonaQuery:
    """Query K-gent's persona"""
    aspect: QueryAspect
    topic: str | None = None
    for_agent: str | None = None  # Which agent is asking


@dataclass
class PersonaUpdate:
    """Update K-gent's persona"""
    aspect: QueryAspect
    operation: UpdateOperation
    content: Any
    reason: str | None = None


@dataclass
class Dialogue:
    """Engage in dialogue with K-gent"""
    message: str
    mode: DialogueMode


# Union type for K-gent input
KgentInput = PersonaQuery | PersonaUpdate | Dialogue


@dataclass
class QueryResponse:
    """Response to a persona query"""
    preferences: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    suggested_style: list[str] = field(default_factory=list)


@dataclass
class UpdateConfirmation:
    """Confirmation of persona update"""
    success: bool
    aspect_updated: str
    new_value: Any | None = None


@dataclass
class DialogueResponse:
    """Response to dialogue"""
    response: str
    mode_used: DialogueMode
    follow_ups: list[str] = field(default_factory=list)


# Union type for K-gent output
KgentOutput = QueryResponse | UpdateConfirmation | DialogueResponse


# =============================================================================
# H-GENT TYPES (Dialectic Introspection)
# =============================================================================

# H-hegel types
@dataclass
class HegelInput:
    """Input to H-hegel agent"""
    thesis: Any
    antithesis: Any | None = None  # If None, H-hegel surfaces it
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class HegelOutput:
    """Output from H-hegel agent"""
    synthesis: Any | None = None
    sublation_notes: str = ""  # What was preserved, negated, elevated
    productive_tension: bool = False  # True if synthesis premature
    next_thesis: Any | None = None  # For recursive dialectic


# H-lacan types
class Register(Enum):
    """Lacan's three registers"""
    SYMBOLIC = "symbolic"
    IMAGINARY = "imaginary"
    REAL = "real"


class KnotStatus(Enum):
    """Status of the Borromean knot"""
    STABLE = "stable"
    LOOSENING = "loosening"
    UNKNOTTED = "unknotted"


@dataclass
class RegisterLocation:
    """Location in the three registers (each 0.0-1.0)"""
    symbolic: float
    imaginary: float
    real_proximity: float


@dataclass
class Slippage:
    """A register slippage (claiming one, actually another)"""
    claimed: Register
    actual: Register
    evidence: str


@dataclass
class LacanInput:
    """Input to H-lacan agent"""
    output: Any  # Agent output to examine
    context: dict[str, Any] = field(default_factory=dict)
    focus: Register | Literal["all"] = "all"


@dataclass
class LacanOutput:
    """Output from H-lacan agent"""
    register_location: RegisterLocation
    gaps: list[str]  # What cannot be represented
    slippages: list[Slippage]
    knot_status: KnotStatus


# H-jung types
class IntegrationDifficulty(Enum):
    """Difficulty of integrating shadow content"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ShadowContent:
    """Shadow content item"""
    content: str
    exclusion_reason: str
    integration_difficulty: IntegrationDifficulty


@dataclass
class Projection:
    """A shadow projection"""
    shadow_content: str
    projected_onto: str
    evidence: str


@dataclass
class IntegrationPath:
    """Path to integrate shadow content"""
    shadow_content: str
    integration_method: str
    risks: list[str]


@dataclass
class JungInput:
    """Input to H-jung agent"""
    system_self_image: str
    declared_capabilities: list[str]
    declared_limitations: list[str]
    behavioral_patterns: list[Any] = field(default_factory=list)


@dataclass
class JungOutput:
    """Output from H-jung agent"""
    shadow_inventory: list[ShadowContent]
    projections: list[Projection]
    integration_paths: list[IntegrationPath]
    persona_shadow_balance: float  # 0 = all persona, 1 = integrated


# =============================================================================
# A-GENT TYPES (Creativity Coach)
# =============================================================================

class CreativityMode(Enum):
    """Creativity Coach interaction modes"""
    EXPAND = "expand"        # Generate related concepts
    CONNECT = "connect"      # Link to unrelated domains
    CONSTRAIN = "constrain"  # Add productive limitations
    QUESTION = "question"    # Ask generative questions


class CreativityPersona(Enum):
    """Optional persona flavors"""
    PLAYFUL = "playful"
    PHILOSOPHICAL = "philosophical"
    PRACTICAL = "practical"
    PROVOCATIVE = "provocative"
    WARM = "warm"


@dataclass
class CreativityInput:
    """Input to Creativity Coach"""
    seed: str  # The idea or starting point
    mode: CreativityMode
    context: str | None = None  # Optional background
    response_count: int = 3
    temperature: float = 0.8  # Creativity variance (0.0-1.0)
    persona: CreativityPersona | None = None


@dataclass
class CreativityOutput:
    """Output from Creativity Coach"""
    responses: list[str]
    mode_used: CreativityMode
    follow_ups: list[str]


# =============================================================================
# B-GENT TYPES (Hypothesis Engine)
# =============================================================================

class Novelty(Enum):
    """Hypothesis novelty level"""
    INCREMENTAL = "incremental"
    EXPLORATORY = "exploratory"
    PARADIGM_SHIFTING = "paradigm_shifting"


@dataclass
class Hypothesis:
    """A scientific hypothesis"""
    statement: str
    confidence: float  # 0.0-1.0 epistemic confidence
    novelty: Novelty
    falsifiable_by: list[str]  # What would disprove this
    supporting_observations: list[int]  # Indices into input observations
    assumptions: list[str]  # Unstated assumptions


@dataclass
class HypothesisInput:
    """Input to Hypothesis Engine"""
    observations: list[str]  # Raw observations or data summaries
    domain: str  # Scientific domain
    question: str | None = None  # Optional guiding research question
    constraints: list[str] = field(default_factory=list)  # Known constraints


@dataclass
class HypothesisOutput:
    """Output from Hypothesis Engine"""
    hypotheses: list[Hypothesis]
    reasoning_chain: list[str]  # How hypotheses were derived
    suggested_tests: list[str]  # Ways to test the hypotheses
