"""
Mirror Protocol Types - Core abstractions for organizational introspection.

This module defines the fundamental types for the Mirror Protocol:
- Thesis: A stated principle or value
- Antithesis: An observed behavior that tensions with a thesis
- Tension: The productive friction between stated and actual
- Synthesis: A proposed resolution

The types implement the H-gent dialectical model from spec/h-gents/README.md.

Category Theory:
  Thesis and Antithesis are objects in the Deontic (stated) and Ontic (actual)
  categories. Tension is a morphism between them, and Synthesis is a
  universal construction (coequalizer) that resolves the tension.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# =============================================================================
# Enums
# =============================================================================


class TensionMode(Enum):
    """
    How the tension manifests.

    From spec/h-gents/README.md:
    - LOGICAL: Formal contradiction in statements
    - EMPIRICAL: Contradiction between claim and evidence
    - PRAGMATIC: Contradiction in practice/action
    - TEMPORAL: Contradiction across time (drift)
    """

    LOGICAL = "logical"
    EMPIRICAL = "empirical"
    PRAGMATIC = "pragmatic"
    TEMPORAL = "temporal"


class TensionType(Enum):
    """
    Classification for resolution strategy.

    From spec/h-gents/README.md:
    - BEHAVIORAL: Principle is right, behavior needs adjustment
    - ASPIRATIONAL: Principle is aspirational, behavior is realistic
    - OUTDATED: Principle no longer serves, should be updated
    - CONTEXTUAL: Both are right in different contexts
    - FUNDAMENTAL: Deep conflict requiring explicit choice
    """

    BEHAVIORAL = "behavioral"
    ASPIRATIONAL = "aspirational"
    OUTDATED = "outdated"
    CONTEXTUAL = "contextual"
    FUNDAMENTAL = "fundamental"


class InterventionType(Enum):
    """
    Types of interventions the Mirror can suggest.

    From spec/h-gents/kairos.md:
    - Passive (always available): REFLECT, REMEMBER
    - Active (requires opt-in): REMIND, SUGGEST, DRAFT
    - Structural (requires explicit approval): RITUAL, AUDIT
    """

    # Passive
    REFLECT = "reflect"  # Surface a pattern when asked
    REMEMBER = "remember"  # Recall relevant past decisions

    # Active
    REMIND = "remind"  # Gentle commitment tracking
    SUGGEST = "suggest"  # Propose principle-aligned actions
    DRAFT = "draft"  # Generate documentation

    # Structural
    RITUAL = "ritual"  # Create recurring processes
    AUDIT = "audit"  # Systematic principle review


class PatternType(Enum):
    """Types of patterns observable in a knowledge base."""

    # Structural patterns (easy to detect)
    ORPHAN_NOTES = "orphan_notes"  # Notes with no links
    LINK_DENSITY = "link_density"  # Average links per note
    NOTE_LENGTH = "note_length"  # Average note length
    UPDATE_FREQUENCY = "update_frequency"  # How often notes are updated
    TAG_USAGE = "tag_usage"  # Tag patterns
    FOLDER_STRUCTURE = "folder_structure"  # Organizational patterns

    # Behavioral patterns (require analysis)
    DAILY_NOTE_USAGE = "daily_note_usage"  # Daily note patterns
    REFLECTION_DEPTH = "reflection_depth"  # Content depth analysis
    CONNECTION_PATTERNS = "connection_patterns"  # How ideas are linked
    KNOWLEDGE_SILOS = "knowledge_silos"  # Isolated clusters
    STALENESS = "staleness"  # How old content gets


# =============================================================================
# Core Types
# =============================================================================


@dataclass(frozen=True)
class Thesis:
    """
    A stated principle or value.

    Extracted from knowledge bases (Obsidian vaults, Notion workspaces, etc.)
    using P-gent parsing strategies.

    Attributes:
        content: The principle statement itself
        source: Where it was extracted from (file path, URL, etc.)
        source_line: Line number in source (if applicable)
        confidence: Extraction confidence (0.0-1.0)
        category: Optional categorization of the principle
        extracted_at: When the principle was extracted
        metadata: Additional context (tags, surrounding text, etc.)
    """

    content: str
    source: str
    confidence: float = 1.0
    source_line: int | None = None
    category: str = ""
    extracted_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


@dataclass(frozen=True)
class PatternObservation:
    """
    A single observation about behavioral patterns.

    Collected by W-gent (Witness) through file system analysis,
    content parsing, and temporal tracking.
    """

    pattern_type: PatternType
    description: str
    value: float | int | str  # The observed metric
    sample_size: int  # How many items were analyzed
    confidence: float = 1.0
    observed_at: datetime = field(default_factory=datetime.now)
    examples: tuple[str, ...] = ()  # Specific examples
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Antithesis:
    """
    An observed behavior that tensions with a thesis.

    The Antithesis represents what actually happens, as opposed to
    what was stated (Thesis). The gap between them is the Tension.

    Attributes:
        pattern: Description of the observed behavior
        evidence: List of PatternObservations supporting this
        frequency: How often this pattern occurs (0.0-1.0)
        severity: How strongly this contradicts the thesis (0.0-1.0)
        observed_at: When the pattern was observed
    """

    pattern: str
    evidence: tuple[PatternObservation, ...]
    frequency: float = 0.5
    severity: float = 0.5
    observed_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not 0.0 <= self.frequency <= 1.0:
            raise ValueError(f"Frequency must be 0.0-1.0, got {self.frequency}")
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError(f"Severity must be 0.0-1.0, got {self.severity}")


@dataclass(frozen=True)
class DivergenceScore:
    """
    Quantified gap between thesis and antithesis.

    From spec/h-gents/contradiction.md:
    Divergence measures how far behavior is from stated principle.

    Component scores allow understanding which analysis method found the gap:
    - structural: From metrics analysis (link density, staleness, etc.)
    - semantic: From content analysis (LLM-based)
    - temporal: From drift analysis (change over time)
    """

    value: float  # 0.0 = perfect alignment, 1.0 = direct contradiction
    structural: float = 0.0  # From metrics analysis
    semantic: float = 0.0  # From content analysis
    temporal: float = 0.0  # From drift analysis

    def __post_init__(self):
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"Value must be 0.0-1.0, got {self.value}")

    @property
    def severity_label(self) -> str:
        """Human-readable severity interpretation."""
        if self.value < 0.2:
            return "aligned"  # Minor variance, not concerning
        elif self.value < 0.4:
            return "tension"  # Worth noting, not urgent
        elif self.value < 0.6:
            return "contradiction"  # Clear gap requiring attention
        elif self.value < 0.8:
            return "significant"  # Major divergence
        else:
            return "crisis"  # Fundamental integrity issue


@dataclass(frozen=True)
class Tension:
    """
    The productive friction between stated and actual.

    A Tension is the core unit of the Mirror Protocol. It represents
    a gap between what was stated (Thesis) and what is observed (Antithesis).

    From spec/h-gents/README.md:
    - mode: How the tension manifests (LOGICAL, EMPIRICAL, PRAGMATIC, TEMPORAL)
    - thesis: The stated position
    - antithesis: The opposing position (may be surfaced)
    - severity: 0.0 = minor, 1.0 = critical
    - description: Human-readable diagnosis
    - tension_type: Classification (may be determined later)

    Attributes:
        thesis: The stated principle
        antithesis: The observed behavior
        divergence: Divergence score (0.0-1.0) - alias for severity
        mode: How the tension manifests
        tension_type: Classification of the tension
        interpretation: Human-readable diagnosis (spec calls this 'description')
        detected_at: When the tension was detected
    """

    thesis: Thesis
    antithesis: Antithesis
    divergence: float  # severity in spec terms
    mode: TensionMode = TensionMode.EMPIRICAL
    tension_type: TensionType = TensionType.BEHAVIORAL
    interpretation: str = ""
    detected_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not 0.0 <= self.divergence <= 1.0:
            raise ValueError(f"Divergence must be 0.0-1.0, got {self.divergence}")

    @property
    def severity(self) -> float:
        """Alias for divergence, matching spec terminology."""
        return self.divergence

    @property
    def description(self) -> str:
        """Alias for interpretation, matching spec terminology."""
        return self.interpretation

    @property
    def is_significant(self) -> bool:
        """Whether this tension is significant enough to surface."""
        return self.divergence >= 0.5

    @property
    def requires_attention(self) -> bool:
        """Whether this tension requires immediate attention."""
        return self.divergence >= 0.75


class HoldReason(Enum):
    """
    Why a tension is being held rather than resolved.

    From spec/h-gents/sublation.md
    """

    PREMATURE = "premature"  # Not enough information yet
    PRODUCTIVE = "productive"  # Tension drives growth
    EXTERNAL_DEPENDENCY = "external"  # Resolution depends on outside factors
    HIGH_COST = "high_cost"  # Social cost too high right now
    KAIROS = "kairos"  # Waiting for right moment


@dataclass(frozen=True)
class HoldTension:
    """
    Decision to preserve rather than resolve a tension.

    From spec/h-gents/README.md and sublation.md:
    Not all tensions should be resolved. Some are productive—they drive
    growth, creativity, and evolution.
    """

    tension: Tension
    why_held: str  # Human-readable reason
    hold_reason: HoldReason = HoldReason.PRODUCTIVE
    review_after: datetime | None = None
    held_since: datetime = field(default_factory=datetime.now)

    # Why this tension is valuable
    productive_function: str = ""

    # Conditions that would change the decision
    synthesis_triggers: tuple[str, ...] = ()

    # How to live with this tension
    management_practices: tuple[str, ...] = ()


@dataclass(frozen=True)
class Synthesis:
    """
    A resolved tension.

    From spec/h-gents/README.md and sublation.md:
    The Synthesis is not a compromise—it's a transcendence that
    acknowledges the truth in both thesis and antithesis.

    Resolution types (the three meanings of aufheben):
    - "preserve": Keep thesis as-is (no real contradiction found)
    - "negate": Replace thesis with antithesis (antithesis is clearly right)
    - "elevate": Transcend to higher synthesis (both contain partial truth)

    Attributes:
        tension: The tension being resolved
        resolution_type: How the tension was resolved ("preserve", "negate", "elevate")
        proposal: The specific proposal for resolution (explanation in spec)
        intervention: What type of intervention is needed
        cost: Estimated social/cognitive cost (0.0-1.0)
        confidence: Confidence in this synthesis (0.0-1.0)
    """

    tension: Tension
    resolution_type: str  # "preserve", "negate", "elevate" per spec
    proposal: str
    intervention: InterventionType = InterventionType.REFLECT
    cost: float = 0.5
    confidence: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not 0.0 <= self.cost <= 1.0:
            raise ValueError(f"Cost must be 0.0-1.0, got {self.cost}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")

    @property
    def result(self) -> str:
        """Alias for proposal, matching spec terminology."""
        return self.proposal

    @property
    def explanation(self) -> str:
        """Alias for proposal, matching spec terminology."""
        return self.proposal


# Union type for sublation result per spec
SublateResult = Synthesis | HoldTension


# =============================================================================
# Report Types
# =============================================================================


@dataclass
class MirrorReport:
    """
    The output of a Mirror Protocol analysis.

    Contains the most significant tension found and a reflection prompt.
    """

    # The primary tension to surface
    thesis: Thesis
    antithesis: Antithesis
    divergence: float
    reflection: str

    # Optional: additional context
    all_tensions: list[Tension] = field(default_factory=list)
    all_principles: list[Thesis] = field(default_factory=list)
    all_patterns: list[PatternObservation] = field(default_factory=list)

    # Metadata
    vault_path: str = ""
    analyzed_at: datetime = field(default_factory=datetime.now)
    analysis_duration_seconds: float = 0.0

    @property
    def integrity_score(self) -> float:
        """
        Overall integrity score (0.0-1.0).

        1.0 = perfect alignment between stated and actual
        0.0 = complete contradiction
        """
        if not self.all_tensions:
            return 1.0
        total_divergence = sum(t.divergence for t in self.all_tensions)
        return 1.0 - (total_divergence / len(self.all_tensions))


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class MirrorConfig:
    """Configuration for Mirror Protocol analysis."""

    # What to extract
    extract_from_readme: bool = True
    extract_from_principles_folder: bool = True
    extract_from_tags: bool = True  # Look for #principle tags
    principle_indicators: tuple[str, ...] = (
        "principle",
        "value",
        "belief",
        "important",
        "always",
        "never",
        "should",
        "must",
    )

    # What to observe
    observe_link_patterns: bool = True
    observe_update_patterns: bool = True
    observe_length_patterns: bool = True
    observe_daily_notes: bool = True

    # Analysis settings
    min_divergence_to_report: float = 0.3
    max_tensions_to_report: int = 5

    # File patterns
    excluded_folders: tuple[str, ...] = (
        ".obsidian",
        ".trash",
        "templates",
        ".git",
    )
    note_extensions: tuple[str, ...] = (".md", ".markdown")

    # Daily notes detection
    daily_note_patterns: tuple[str, ...] = (
        r"\d{4}-\d{2}-\d{2}",  # 2024-01-15
        r"\d{4}/\d{2}/\d{2}",  # 2024/01/15
        r"\w+ \d{1,2}, \d{4}",  # January 15, 2024
    )


# =============================================================================
# Marker Constants for Detection
# =============================================================================
#
# From spec/h-gents/contradiction.md:
# These markers enable fast, semantic-aware contradiction detection
# without requiring full LLM analysis.


# Symbolic markers: formal, structured claims
SYMBOLIC_MARKERS: tuple[str, ...] = (
    "defined",
    "specified",
    "typed",
    "interface",
    "contract",
    "rule",
    "law",
    "structure",
    "formal",
    "protocol",
    "must",
    "shall",
    "requires",
    "returns",
    "implements",
)

# Imaginary markers: idealized, aspirational claims
IMAGINARY_MARKERS: tuple[str, ...] = (
    "helpful",
    "friendly",
    "intelligent",
    "perfect",
    "always",
    "completely",
    "understand",
    "best",
    "ideal",
    "seamless",
    "I am",
    "we are",
    "our goal",
    "we provide",
)

# Real markers: limits, impossibilities, failures
REAL_MARKERS: tuple[str, ...] = (
    "cannot",
    "impossible",
    "limit",
    "edge case",
    "failure",
    "error",
    "exception",
    "undefined",
    "unknown",
    "crash",
    "timeout",
    "overflow",
    "corrupt",
    "lost",
)

# Shadow mappings: persona claim → shadow content
# From spec/h-gents/contradiction.md (H-jung integration)
SHADOW_MAPPINGS: dict[str, str] = {
    "helpful": "capacity to refuse, obstruct, or harm when necessary",
    "accurate": "tendency to confabulate, guess, or hallucinate",
    "neutral": "embedded values, preferences, and biases",
    "safe": "latent capabilities beyond declared scope",
    "bounded": "potential for rule-breaking and creativity",
    "tasteful": "capacity for handling crude, ugly, uncomfortable content",
    "curated": "sprawl, experimentation, and dead ends",
    "ethical": "moral ambiguity, dual-use, tragic choices",
    "joyful": "tedious but necessary operations",
    "composable": "monolithic requirements that shouldn't compose",
}
