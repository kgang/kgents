"""
Types for the Principles Crown Jewel.

Dataclasses for principle projection, validation, and healing.
These types are the foundation for concept.principles node aspects.

See: spec/principles/node.md for the authoritative specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# === Stance Enum ===


class Stance(Enum):
    """
    The Four Stances for principle consumption.

    Drawing from the Greek rhetorical tradition:
    - Genesis: Becoming - which principles apply?
    - Poiesis: Making - how do I build according to principles?
    - Krisis: Judgment - does this embody the principles?
    - Therapeia: Healing - which principle was violated?

    See: spec/principles/consumption.md
    """

    GENESIS = "genesis"
    POIESIS = "poiesis"
    KRISIS = "krisis"
    THERAPEIA = "therapeia"

    @property
    def greek_root(self) -> str:
        """The Greek word this stance derives from."""
        return {
            Stance.GENESIS: "genesis (becoming)",
            Stance.POIESIS: "poiesis (making)",
            Stance.KRISIS: "krisis (judgment)",
            Stance.THERAPEIA: "therapeia (healing)",
        }[self]

    @property
    def motion(self) -> str:
        """The type of motion this stance represents."""
        return {
            Stance.GENESIS: "Emergence",
            Stance.POIESIS: "Construction",
            Stance.KRISIS: "Evaluation",
            Stance.THERAPEIA: "Restoration",
        }[self]

    @property
    def question(self) -> str:
        """The central question of this stance."""
        return {
            Stance.GENESIS: "What am I creating and why?",
            Stance.POIESIS: "How do I build this right?",
            Stance.KRISIS: "Does this embody the principles?",
            Stance.THERAPEIA: "What went wrong and how do I fix it?",
        }[self]


# === Stance Slices ===

# Map of stance to principle files to load
STANCE_SLICES: dict[Stance, tuple[str, ...]] = {
    Stance.GENESIS: (
        "CONSTITUTION.md",
        "meta.md",
    ),
    Stance.POIESIS: (
        "CONSTITUTION.md",
        "operational.md",
    ),
    Stance.KRISIS: (
        "CONSTITUTION.md",
    ),
    Stance.THERAPEIA: (
        "CONSTITUTION.md",
        "puppets.md",
        "operational.md",
    ),
}


# === Principle Definition ===


@dataclass(frozen=True)
class Principle:
    """
    A single principle from the constitution.

    Each of the seven immutable principles has:
    - number: 1-7
    - name: The principle name (e.g., "Tasteful")
    - tagline: The short description
    - content: The full content including anti-patterns
    - question: The question to ask when applying this principle
    - anti_patterns: Common violations
    """

    number: int
    name: str
    tagline: str
    content: str
    question: str
    anti_patterns: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "number": self.number,
            "name": self.name,
            "tagline": self.tagline,
            "content": self.content,
            "question": self.question,
            "anti_patterns": list(self.anti_patterns),
        }


# === The Seven Principles ===

THE_SEVEN_PRINCIPLES: tuple[Principle, ...] = (
    Principle(
        number=1,
        name="Tasteful",
        tagline="Each agent serves a clear, justified purpose.",
        content="",  # Will be loaded from file
        question="Does this agent have a clear, justified purpose?",
        anti_patterns=(
            "Agents that do 'everything'",
            "kitchen-sink configurations",
            "agents added 'just in case'",
        ),
    ),
    Principle(
        number=2,
        name="Curated",
        tagline="Intentional selection over exhaustive cataloging.",
        content="",
        question="Does this add unique value, or does something similar exist?",
        anti_patterns=(
            "'Awesome list' sprawl",
            "duplicative agents with slight variations",
            "legacy agents kept for nostalgia",
        ),
    ),
    Principle(
        number=3,
        name="Ethical",
        tagline="Agents augment human capability, never replace judgment.",
        content="",
        question="Does this respect human agency and privacy?",
        anti_patterns=(
            "Agents that claim certainty they don't have",
            "hidden data collection",
            "agents that manipulate rather than assist",
            "'trust me' without explanation",
        ),
    ),
    Principle(
        number=4,
        name="Joy-Inducing",
        tagline="Delight in interaction; personality matters.",
        content="",
        question="Would I enjoy interacting with this?",
        anti_patterns=(
            "Robotic, lifeless responses",
            "needless formality",
            "agents that feel like forms to fill out",
        ),
    ),
    Principle(
        number=5,
        name="Composable",
        tagline="Agents are morphisms in a category; composition is primary.",
        content="",
        question="Can this work with other agents? Does it return single outputs?",
        anti_patterns=(
            "Monolithic agents that can't be broken apart",
            "agents with hidden state that prevents composition",
            "'god agents' that must be used alone",
            "LLM agents that return arrays instead of single outputs",
        ),
    ),
    Principle(
        number=6,
        name="Heterarchical",
        tagline="Agents exist in flux, not fixed hierarchy; autonomy and composability coexist.",
        content="",
        question="Can this agent both lead and follow?",
        anti_patterns=(
            "Permanent orchestrator/worker relationships",
            "agents that can only be called, never run autonomously",
            "fixed resource budgets that prevent dynamic reallocation",
            "'chain of command' that prevents peer-to-peer interaction",
        ),
    ),
    Principle(
        number=7,
        name="Generative",
        tagline="Spec is compression; design should generate implementation.",
        content="",
        question="Could this be regenerated from spec? Is the design compressed?",
        anti_patterns=(
            "Specs that merely describe existing code",
            "implementations that diverge from spec (spec rot)",
            "designs that require extensive prose to explain",
        ),
    ),
)

# Map from principle name to number
PRINCIPLE_NAMES: dict[str, int] = {p.name.lower(): p.number for p in THE_SEVEN_PRINCIPLES}
PRINCIPLE_NUMBERS: dict[int, str] = {p.number: p.name for p in THE_SEVEN_PRINCIPLES}

# The Seven Questions (for Krisis stance)
THE_SEVEN_QUESTIONS: tuple[str, ...] = tuple(p.question for p in THE_SEVEN_PRINCIPLES)


# === Renderings ===


@dataclass(frozen=True)
class PrincipleProjection:
    """
    Stance-aware projection of principles.

    The manifest aspect returns this, containing:
    - stance: The detected or specified stance
    - slices: Which principle files were loaded
    - content: The combined content
    """

    stance: Stance
    slices: tuple[str, ...]
    content: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "stance": self.stance.value,
            "slices": list(self.slices),
            "content": self.content,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        lines = [
            f"Stance: {self.stance.value.upper()} ({self.stance.motion})",
            f"Question: {self.stance.question}",
            f"Reading: {', '.join(self.slices)}",
            "",
            self.content,
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class ConstitutionRendering:
    """
    The seven immutable principles rendered.

    The constitution aspect returns this.
    """

    content: str
    principles: tuple[Principle, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "principles": [p.to_dict() for p in self.principles],
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        return self.content


@dataclass(frozen=True)
class MetaPrincipleRendering:
    """
    Meta-principles (Accursed Share, AGENTESE, Personality Space).

    The meta aspect returns this.
    """

    content: str
    section: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "section": self.section,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        if self.section:
            return f"## {self.section}\n\n{self.content}"
        return self.content


@dataclass(frozen=True)
class OperationalRendering:
    """
    Tactical implementation guidance.

    The operational aspect returns this.
    """

    content: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {"content": self.content}

    def to_text(self) -> str:
        """Convert to human-readable text."""
        return self.content


@dataclass(frozen=True)
class ADRendering:
    """
    Architectural decision rendering.

    The ad aspect returns this for one or more ADs.
    """

    ad_id: int | None
    category: str | None
    content: str
    ads: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "ad_id": self.ad_id,
            "category": self.category,
            "content": self.content,
            "ads": list(self.ads),
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        return self.content


# === Check Types ===


@dataclass(frozen=True)
class PrincipleCheck:
    """
    Result of checking a single principle against a target.
    """

    principle: int
    name: str
    question: str
    passed: bool
    citation: str
    anti_patterns: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "principle": self.principle,
            "name": self.name,
            "question": self.question,
            "passed": self.passed,
            "citation": self.citation,
            "anti_patterns": list(self.anti_patterns),
        }


@dataclass(frozen=True)
class CheckResult:
    """
    Full result of checking a target against all principles.

    The check aspect returns this.
    """

    target: str
    passed: bool
    checks: tuple[PrincipleCheck, ...]
    stance: Stance = Stance.KRISIS

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "target": self.target,
            "passed": self.passed,
            "checks": [c.to_dict() for c in self.checks],
            "stance": self.stance.value,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        lines = [
            f"Target: {self.target}",
            f"Result: {'PASSED' if self.passed else 'FAILED'}",
            "",
        ]
        for check in self.checks:
            icon = "OK" if check.passed else "XX"
            lines.append(f"[{icon}] {check.principle}. {check.name}")
            lines.append(f"    {check.question}")
            if not check.passed:
                lines.append(f"    Citation: {check.citation}")
                if check.anti_patterns:
                    lines.append(f"    Anti-patterns: {', '.join(check.anti_patterns)}")
            lines.append("")
        return "\n".join(lines)


# === Healing Types ===


@dataclass(frozen=True)
class HealingPrescription:
    """
    Prescription for healing a principle violation.

    The heal aspect returns this.
    """

    principle: int
    principle_name: str
    anti_patterns: tuple[str, ...]
    matched_pattern: str | None
    puppets: tuple[str, ...]
    related_ads: tuple[int, ...]
    path: tuple[str, ...]
    stance: Stance = Stance.THERAPEIA

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "principle": self.principle,
            "principle_name": self.principle_name,
            "anti_patterns": list(self.anti_patterns),
            "matched_pattern": self.matched_pattern,
            "puppets": list(self.puppets),
            "related_ads": list(self.related_ads),
            "path": list(self.path),
            "stance": self.stance.value,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        lines = [
            f"Healing Prescription for: {self.principle}. {self.principle_name}",
            "",
            "Anti-patterns:",
        ]
        for ap in self.anti_patterns:
            marker = " *" if ap == self.matched_pattern else "  "
            lines.append(f"{marker} {ap}")
        lines.append("")
        lines.append("Healing Path:")
        for i, step in enumerate(self.path, 1):
            lines.append(f"  {i}. {step}")
        if self.related_ads:
            lines.append("")
            lines.append(f"Related ADs: {', '.join(f'AD-{n:03d}' for n in self.related_ads)}")
        return "\n".join(lines)


# === Teaching Types ===


@dataclass(frozen=True)
class TeachingContent:
    """
    Teaching content for a principle.

    The teach aspect returns this.
    """

    principle: int | None
    principle_name: str | None
    depth: str  # "overview", "examples", "exercises"
    content: str
    examples: tuple[str, ...] = ()
    exercises: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "principle": self.principle,
            "principle_name": self.principle_name,
            "depth": self.depth,
            "content": self.content,
            "examples": list(self.examples),
            "exercises": list(self.exercises),
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        lines = [self.content]
        if self.examples:
            lines.append("\nExamples:")
            for ex in self.examples:
                lines.append(f"  - {ex}")
        if self.exercises:
            lines.append("\nExercises:")
            for ex in self.exercises:
                lines.append(f"  - {ex}")
        return "\n".join(lines)


# === AD Task Mapping ===

# Map of task patterns to relevant ADs (for Poiesis stance)
AD_TASK_MAPPING: dict[str, tuple[int, ...]] = {
    "adding-agent": (2, 3, 6),  # AD-002, AD-003, AD-006
    "agentese": (9, 10, 11, 12),  # AD-009, AD-010, AD-011, AD-012
    "state-machine": (2, 13),  # AD-002, AD-013
    "memory": (1, 6),  # AD-001, AD-006
    "persistence": (1, 6),  # AD-001, AD-006
    "ui": (9, 12),  # AD-009, AD-012
    "projection": (9, 12),  # AD-009, AD-012
    "form": (13,),  # AD-013
}

# Map of principle to related ADs (for Therapeia stance)
PRINCIPLE_AD_MAPPING: dict[int, tuple[int, ...]] = {
    1: (3, 8),  # Tasteful: Generative Over Enumerative, Simplifying Isomorphisms
    2: (3,),  # Curated: Generative Over Enumerative
    3: (),  # Ethical: (no specific ADs yet)
    4: (4,),  # Joy-Inducing: Pre-Computed Richness
    5: (1, 2, 6),  # Composable: Universal Functor, Polynomial, Unified Categorical
    6: (2, 6),  # Heterarchical: Polynomial, Unified Categorical
    7: (3, 5),  # Generative: Generative Over Enumerative, Self-Similar Lifecycle
}


# === Exports ===

__all__ = [
    # Enums
    "Stance",
    # Constants
    "STANCE_SLICES",
    "THE_SEVEN_PRINCIPLES",
    "THE_SEVEN_QUESTIONS",
    "PRINCIPLE_NAMES",
    "PRINCIPLE_NUMBERS",
    "AD_TASK_MAPPING",
    "PRINCIPLE_AD_MAPPING",
    # Core types
    "Principle",
    # Renderings
    "PrincipleProjection",
    "ConstitutionRendering",
    "MetaPrincipleRendering",
    "OperationalRendering",
    "ADRendering",
    # Check types
    "PrincipleCheck",
    "CheckResult",
    # Healing types
    "HealingPrescription",
    # Teaching types
    "TeachingContent",
]
