"""
Scientific Core Commands - CLI Phase 2

These commands implement the H-gent dialectical reasoning at the CLI surface.
They are "scientific" in the Popperian sense: hypotheses that can be falsified,
rivals that can be steel-manned, and syntheses that transcend contradictions.

Commands:
    falsify    - Find counterexamples to hypotheses (Popper)
    conjecture - Generate hypotheses from patterns (abduction)
    rival      - Steel-man opposing views (devil's advocate)
    sublate    - Synthesize contradictions (Hegel)
    shadow     - Surface suppressed concerns (Jung)

Token Cost:
    - falsify: 0 tokens (local pattern matching)
    - conjecture: 0 tokens (local heuristics)
    - rival: 0-LOW tokens (can use LLM for sophisticated rivals)
    - sublate: 0-MEDIUM tokens (can use LLM for deep synthesis)
    - shadow: 0 tokens (local shadow detection from spec)
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .cli_types import (
    CLIContext,
    CommandResult,
    ErrorInfo,
    ErrorRecoverability,
    ErrorSeverity,
)


# =============================================================================
# Falsify Command - Find counterexamples to hypotheses
# =============================================================================


class CounterexampleType(Enum):
    """Types of counterexamples."""

    DIRECT = "direct"  # Direct contradiction found
    EDGE_CASE = "edge_case"  # Edge case that breaks hypothesis
    TEMPORAL = "temporal"  # Counterexample from history
    STRUCTURAL = "structural"  # Structural pattern that contradicts


@dataclass(frozen=True)
class Counterexample:
    """A counterexample to a hypothesis."""

    hypothesis: str
    counterexample: str
    example_type: CounterexampleType
    confidence: float  # 0-1
    source: str  # Where found (file, pattern, etc.)
    suggestion: str  # What to do about it


@dataclass(frozen=True)
class FalsifyReport:
    """Result of attempting to falsify a hypothesis."""

    hypothesis: str
    counterexamples: tuple[Counterexample, ...]
    falsified: bool
    confidence: float  # Overall confidence in falsification
    search_depth: str  # "shallow", "medium", "deep"

    def render(self) -> str:
        """Render as falsification report."""
        if not self.falsified:
            return f'→ HYPOTHESIS STANDS: "{self.hypothesis}"\n  No counterexamples found ({self.search_depth} search)'

        lines = [f'→ HYPOTHESIS CHALLENGED: "{self.hypothesis}"']
        lines.append(f"  Confidence: {self.confidence:.0%}")
        lines.append(f"  Counterexamples found: {len(self.counterexamples)}")

        for i, ce in enumerate(self.counterexamples[:3], 1):
            lines.append(f"  {i}. [{ce.example_type.value}] {ce.counterexample}")
            lines.append(f"     Source: {ce.source}")
            lines.append(f"     → {ce.suggestion}")

        return "\n".join(lines)


def find_counterexamples(
    hypothesis: str,
    path: Path,
    depth: str = "medium",
) -> list[Counterexample]:
    """
    Find counterexamples to a hypothesis in codebase.

    Strategies:
    1. Pattern negation: Look for patterns that negate the hypothesis
    2. Exception hunting: Find exceptions to claimed rules
    3. Temporal analysis: Check git history for contradictions
    4. Structural analysis: Check code structure for violations
    """
    counterexamples = []
    hyp_lower = hypothesis.lower()

    # Strategy 1: Direct negation patterns
    negation_patterns = [
        # "always X" negated by "not X", "never X", "except X"
        (r"\balways\b", ["never", "except", "unless", "but not"]),
        # "never X" negated by "sometimes X", "occasionally X"
        (r"\bnever\b", ["sometimes", "occasionally", "once", "rarely"]),
        # "all X" negated by "some", "most", "few"
        (r"\ball\b", ["some", "most", "few", "partial"]),
        # "must X" negated by "may", "can skip", "optional"
        (r"\bmust\b", ["may", "optional", "can skip", "sometimes"]),
    ]

    for pattern, negations in negation_patterns:
        if re.search(pattern, hyp_lower):
            # Look for negation evidence in files
            for ext in ("*.py", "*.md", "*.ts", "*.js"):
                try:
                    for file in path.rglob(ext):
                        if any(p.startswith(".") for p in file.parts):
                            continue
                        try:
                            content = file.read_text(errors="ignore").lower()
                            for neg in negations:
                                if neg in content:
                                    # Extract context
                                    idx = content.find(neg)
                                    start = max(0, idx - 50)
                                    end = min(len(content), idx + 100)
                                    context = content[start:end].strip()
                                    counterexamples.append(
                                        Counterexample(
                                            hypothesis=hypothesis,
                                            counterexample=f"Found '{neg}' suggesting exception",
                                            example_type=CounterexampleType.DIRECT,
                                            confidence=0.5,
                                            source=str(file.relative_to(path)),
                                            suggestion=f"Consider qualifying claim: '{context[:60]}...'",
                                        )
                                    )
                                    break  # One per file
                        except (PermissionError, OSError):
                            continue
                except Exception:
                    pass

    # Strategy 2: Look for TODO/FIXME/HACK that might contradict
    if depth in ("medium", "deep"):
        issue_patterns = [
            (r"TODO:?\s*(.{10,80})", "TODO suggests incomplete implementation"),
            (r"FIXME:?\s*(.{10,80})", "FIXME suggests known issue"),
            (r"HACK:?\s*(.{10,80})", "HACK suggests workaround"),
            (r"XXX:?\s*(.{10,80})", "XXX suggests problematic code"),
        ]

        for ext in ("*.py", "*.ts", "*.js"):
            try:
                for file in path.rglob(ext):
                    if any(p.startswith(".") for p in file.parts):
                        continue
                    try:
                        content = file.read_text(errors="ignore")
                        for pattern, desc in issue_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches[:2]:  # Limit per file
                                # Check if related to hypothesis
                                if any(
                                    word in match.lower()
                                    for word in hypothesis.lower().split()[:3]
                                ):
                                    counterexamples.append(
                                        Counterexample(
                                            hypothesis=hypothesis,
                                            counterexample=match.strip()[:80],
                                            example_type=CounterexampleType.EDGE_CASE,
                                            confidence=0.4,
                                            source=str(file.relative_to(path)),
                                            suggestion=desc,
                                        )
                                    )
                    except (PermissionError, OSError):
                        continue
            except Exception:
                pass

    return counterexamples[:5]  # Limit total


def falsify_hypothesis(
    hypothesis: str, path: Path, depth: str = "medium"
) -> FalsifyReport:
    """
    Attempt to falsify a hypothesis.

    This is Popperian: we don't try to prove it true, we try to find counterexamples.
    """
    counterexamples = find_counterexamples(hypothesis, path, depth)

    if not counterexamples:
        return FalsifyReport(
            hypothesis=hypothesis,
            counterexamples=(),
            falsified=False,
            confidence=0.0,
            search_depth=depth,
        )

    # Calculate overall confidence
    avg_confidence = sum(ce.confidence for ce in counterexamples) / len(counterexamples)
    falsified = avg_confidence > 0.3 or len(counterexamples) >= 3

    return FalsifyReport(
        hypothesis=hypothesis,
        counterexamples=tuple(counterexamples),
        falsified=falsified,
        confidence=avg_confidence,
        search_depth=depth,
    )


# =============================================================================
# Conjecture Command - Generate hypotheses from patterns
# =============================================================================


class ConjectureType(Enum):
    """Types of conjectures."""

    STRUCTURAL = "structural"  # From code structure
    BEHAVIORAL = "behavioral"  # From observed patterns
    TEMPORAL = "temporal"  # From time-based patterns
    NAMING = "naming"  # From naming conventions


@dataclass(frozen=True)
class Conjecture:
    """A generated hypothesis about the codebase."""

    statement: str
    conjecture_type: ConjectureType
    confidence: float  # 0-1
    evidence: tuple[str, ...]
    testable: bool  # Can this be falsified?
    falsification_hint: str  # How to test it


@dataclass(frozen=True)
class ConjectureReport:
    """Report of generated conjectures."""

    conjectures: tuple[Conjecture, ...]
    patterns_analyzed: int
    files_scanned: int

    def render(self) -> str:
        """Render as conjecture report."""
        if not self.conjectures:
            return "→ NO CONJECTURES: No strong patterns detected"

        lines = [
            f"→ CONJECTURES ({len(self.conjectures)} hypotheses from {self.files_scanned} files)"
        ]

        for i, c in enumerate(self.conjectures, 1):
            testable = "✓" if c.testable else "?"
            lines.append(f"  {i}. [{testable}] {c.statement}")
            lines.append(
                f"     Type: {c.conjecture_type.value}, Confidence: {c.confidence:.0%}"
            )
            if c.evidence:
                lines.append(f"     Evidence: {c.evidence[0][:60]}...")
            if c.testable:
                lines.append(f"     Test: {c.falsification_hint}")

        return "\n".join(lines)


def generate_conjectures(path: Path, limit: int = 5) -> ConjectureReport:
    """
    Generate hypotheses from observed patterns.

    This is abductive reasoning: inferring likely explanations from observations.
    """
    conjectures = []
    files_scanned = 0
    patterns = {
        "test_coverage": 0,
        "has_types": 0,
        "has_docs": 0,
        "async_usage": 0,
        "total_files": 0,
    }

    # Scan Python files for patterns
    try:
        for file in path.rglob("*.py"):
            if any(p.startswith(".") for p in file.parts):
                continue
            if "test" in file.name or "_test" in file.name:
                continue

            files_scanned += 1
            patterns["total_files"] += 1

            try:
                content = file.read_text(errors="ignore")

                # Check for type hints
                if "def " in content and ("->" in content or ": " in content):
                    patterns["has_types"] += 1

                # Check for docstrings
                if '"""' in content or "'''" in content:
                    patterns["has_docs"] += 1

                # Check for async
                if "async def" in content or "await " in content:
                    patterns["async_usage"] += 1

            except (PermissionError, OSError):
                continue
    except Exception:
        pass

    # Check for test files
    try:
        test_count = sum(
            1
            for f in path.rglob("*test*.py")
            if not any(p.startswith(".") for p in f.parts)
        )
        patterns["test_coverage"] = test_count
    except Exception:
        pass

    total = patterns["total_files"]
    if total == 0:
        return ConjectureReport(conjectures=(), patterns_analyzed=0, files_scanned=0)

    # Generate conjectures from patterns
    if patterns["has_types"] / total > 0.7:
        conjectures.append(
            Conjecture(
                statement="This project values type safety",
                conjecture_type=ConjectureType.STRUCTURAL,
                confidence=patterns["has_types"] / total,
                evidence=(f"{patterns['has_types']}/{total} files have type hints",),
                testable=True,
                falsification_hint="Look for Any types or # type: ignore comments",
            )
        )

    if patterns["has_docs"] / total > 0.5:
        conjectures.append(
            Conjecture(
                statement="Documentation is maintained alongside code",
                conjecture_type=ConjectureType.BEHAVIORAL,
                confidence=patterns["has_docs"] / total,
                evidence=(f"{patterns['has_docs']}/{total} files have docstrings",),
                testable=True,
                falsification_hint="Check if docstrings match implementation",
            )
        )

    if patterns["async_usage"] / total > 0.3:
        conjectures.append(
            Conjecture(
                statement="This project uses async/concurrent patterns",
                conjecture_type=ConjectureType.STRUCTURAL,
                confidence=patterns["async_usage"] / total,
                evidence=(f"{patterns['async_usage']}/{total} files use async",),
                testable=True,
                falsification_hint="Look for blocking calls in async functions",
            )
        )

    if patterns["test_coverage"] > 0:
        ratio = min(1.0, patterns["test_coverage"] / total)
        conjectures.append(
            Conjecture(
                statement="Testing is a priority in this project",
                conjecture_type=ConjectureType.BEHAVIORAL,
                confidence=ratio,
                evidence=(f"{patterns['test_coverage']} test files found",),
                testable=True,
                falsification_hint="Check test coverage percentage",
            )
        )

    return ConjectureReport(
        conjectures=tuple(conjectures[:limit]),
        patterns_analyzed=len(patterns),
        files_scanned=files_scanned,
    )


# =============================================================================
# Rival Command - Steel-man opposing views
# =============================================================================


@dataclass(frozen=True)
class RivalArgument:
    """A steel-manned opposing argument."""

    position: str  # The original position
    rival: str  # The steel-manned rival
    strength: float  # 0-1, how strong is the rival
    concessions: tuple[str, ...]  # What the original must concede
    synthesis_hint: str  # How might these be synthesized?


@dataclass(frozen=True)
class RivalReport:
    """Report from rival analysis."""

    original_position: str
    rivals: tuple[RivalArgument, ...]
    strongest_rival: str | None

    def render(self) -> str:
        """Render as rival report."""
        if not self.rivals:
            return f'→ NO RIVALS: Could not generate opposing views for "{self.original_position}"'

        lines = [f'→ RIVALS for "{self.original_position}"']

        for i, r in enumerate(self.rivals, 1):
            strength_bar = "█" * int(r.strength * 5) + "░" * (5 - int(r.strength * 5))
            lines.append(f"  {i}. [{strength_bar}] {r.rival}")
            if r.concessions:
                lines.append(f"     Concedes: {r.concessions[0]}")
            lines.append(f"     Synthesis: {r.synthesis_hint}")

        if self.strongest_rival:
            lines.append(f"\n  Strongest rival: {self.strongest_rival}")

        return "\n".join(lines)


# Common position patterns and their rivals
RIVAL_PATTERNS: dict[str, list[dict[str, Any]]] = {
    # Software development positions
    r"test": [
        {
            "rival": "Tests can give false confidence; untested production paths still fail",
            "strength": 0.7,
            "concessions": [
                "Tests catch some bugs",
                "Regression prevention is valuable",
            ],
            "synthesis": "Test critical paths; accept some production failures as learning",
        }
    ],
    r"type": [
        {
            "rival": "Types add ceremony without preventing runtime errors; dynamic typing enables faster iteration",
            "strength": 0.6,
            "concessions": [
                "Types help IDE tooling",
                "Large teams benefit from explicit contracts",
            ],
            "synthesis": "Use types at boundaries; allow internal flexibility",
        }
    ],
    r"document": [
        {
            "rival": "Documentation rots; code is the only truth",
            "strength": 0.65,
            "concessions": ["Good docs help onboarding", "API docs are essential"],
            "synthesis": "Document intent and why, not what; keep docs close to code",
        }
    ],
    r"simple|simplicity": [
        {
            "rival": "Simplicity often hides complexity elsewhere; some problems are irreducibly complex",
            "strength": 0.7,
            "concessions": [
                "Simple is easier to understand",
                "Fewer moving parts means fewer failures",
            ],
            "synthesis": "Simple for users; complex where necessary for correctness",
        }
    ],
    r"fast|quick|speed": [
        {
            "rival": "Speed creates technical debt; slow and careful wins long-term",
            "strength": 0.6,
            "concessions": ["Fast feedback enables learning", "Time-to-market matters"],
            "synthesis": "Fast to validate; careful to ship",
        }
    ],
    r"abstract|abstraction": [
        {
            "rival": "Abstractions leak; concrete code is honest about its constraints",
            "strength": 0.7,
            "concessions": [
                "Good abstractions enable reuse",
                "Patterns help communication",
            ],
            "synthesis": "Abstract after the third instance; don't predict the future",
        }
    ],
    r"composable|modular": [
        {
            "rival": "Composition adds indirection; monoliths are simpler to understand",
            "strength": 0.55,
            "concessions": [
                "Composition enables flexibility",
                "Independent deployment is valuable",
            ],
            "synthesis": "Compose at clear boundaries; monolith within bounded contexts",
        }
    ],
}


def generate_rival(position: str) -> RivalReport:
    """
    Generate steel-manned opposing views for a position.

    Steel-manning: presenting the strongest version of an opposing argument.
    """
    position_lower = position.lower()
    rivals = []

    for pattern, rival_templates in RIVAL_PATTERNS.items():
        if re.search(pattern, position_lower):
            for template in rival_templates:
                rivals.append(
                    RivalArgument(
                        position=position,
                        rival=template["rival"],
                        strength=template["strength"],
                        concessions=tuple(template["concessions"]),
                        synthesis_hint=template["synthesis"],
                    )
                )

    # If no specific patterns match, generate generic rival
    if not rivals:
        rivals.append(
            RivalArgument(
                position=position,
                rival=f"The opposite of '{position}' may be true in certain contexts",
                strength=0.4,
                concessions=("Context determines correctness",),
                synthesis_hint="Consider when each applies; map the boundary",
            )
        )

    # Find strongest
    strongest = max(rivals, key=lambda r: r.strength) if rivals else None

    return RivalReport(
        original_position=position,
        rivals=tuple(rivals),
        strongest_rival=strongest.rival if strongest else None,
    )


# =============================================================================
# Sublate Command - Synthesize contradictions
# =============================================================================


class SublationType(Enum):
    """Types of sublation/synthesis."""

    PRESERVE = "preserve"  # Keep thesis as-is
    NEGATE = "negate"  # Replace thesis with antithesis
    ELEVATE = "elevate"  # Transcend to higher synthesis
    HOLD = "hold"  # Productive tension, don't resolve


@dataclass(frozen=True)
class Sublation:
    """A dialectical synthesis."""

    thesis: str
    antithesis: str
    synthesis: str
    sublation_type: SublationType
    preserved_from_thesis: str
    preserved_from_antithesis: str
    transcendent_insight: str


@dataclass(frozen=True)
class SublateReport:
    """Report from sublation analysis."""

    original_thesis: str
    original_antithesis: str | None
    sublation: Sublation | None
    productive_tension: bool

    def render(self) -> str:
        """Render as sublation report."""
        if self.productive_tension:
            return (
                f"→ PRODUCTIVE TENSION (not resolved)\n"
                f"  Thesis: {self.original_thesis}\n"
                f"  Antithesis: {self.original_antithesis or '[implicit]'}\n"
                f"  Hold this tension—it drives growth."
            )

        if not self.sublation:
            return f'→ NO SYNTHESIS for "{self.original_thesis}"'

        s = self.sublation
        type_symbol = {"preserve": "≡", "negate": "¬", "elevate": "↑", "hold": "⊗"}[
            s.sublation_type.value
        ]

        lines = [
            f"→ SUBLATION [{type_symbol}]",
            f"  Thesis: {s.thesis}",
            f"  Antithesis: {s.antithesis}",
            "  ────────────────────────────────",
            f"  Synthesis: {s.synthesis}",
            "",
            f"  Preserved from thesis: {s.preserved_from_thesis}",
            f"  Preserved from antithesis: {s.preserved_from_antithesis}",
            f"  Transcendent insight: {s.transcendent_insight}",
        ]

        return "\n".join(lines)


# Synthesis patterns for common dialectics
SYNTHESIS_PATTERNS: dict[tuple[str, str], dict[str, str]] = {
    ("speed", "quality"): {
        "synthesis": "Quality at the speed of learning",
        "preserved_thesis": "Fast feedback enables iteration",
        "preserved_antithesis": "Quality compounds over time",
        "transcendent": "Speed without learning is waste; quality without shipping is vanity",
    },
    ("abstraction", "concrete"): {
        "synthesis": "Abstract late, concrete early",
        "preserved_thesis": "Abstraction enables reuse",
        "preserved_antithesis": "Concrete code is honest",
        "transcendent": "Premature abstraction is the root of all complexity",
    },
    ("simplicity", "completeness"): {
        "synthesis": "Simple to use, complete when needed",
        "preserved_thesis": "Simple is easier to maintain",
        "preserved_antithesis": "Complete solutions serve users",
        "transcendent": "The simplest complete solution, not the simplest incomplete one",
    },
    ("consistency", "flexibility"): {
        "synthesis": "Consistent at boundaries, flexible within",
        "preserved_thesis": "Consistency aids understanding",
        "preserved_antithesis": "Flexibility enables adaptation",
        "transcendent": "Conventions liberate; arbitrary choices constrain",
    },
}


def find_antithesis(thesis: str) -> str | None:
    """Find implicit antithesis for a thesis."""
    thesis_lower = thesis.lower()

    # Simple negation patterns
    antithesis_hints = {
        "always": "sometimes the opposite is true",
        "never": "sometimes this is necessary",
        "must": "sometimes we can skip this",
        "should": "sometimes we should not",
        "simple": "complexity serves a purpose",
        "fast": "slow and careful has value",
        "complete": "partial solutions work",
        "all": "some exceptions exist",
    }

    for word, antithesis in antithesis_hints.items():
        if word in thesis_lower:
            return f"But {antithesis}"

    return None


def sublate_contradiction(
    thesis: str,
    antithesis: str | None = None,
    force_synthesis: bool = False,
) -> SublateReport:
    """
    Attempt dialectical synthesis of thesis and antithesis.

    Sublation (Aufheben) has three simultaneous meanings:
    1. To cancel/negate
    2. To preserve
    3. To elevate
    """
    # Find antithesis if not provided
    if antithesis is None:
        antithesis = find_antithesis(thesis)

    if antithesis is None:
        return SublateReport(
            original_thesis=thesis,
            original_antithesis=None,
            sublation=None,
            productive_tension=False,
        )

    thesis_lower = thesis.lower()
    antithesis_lower = antithesis.lower()

    # Check for known synthesis patterns
    for (t_pattern, a_pattern), synthesis_data in SYNTHESIS_PATTERNS.items():
        if t_pattern in thesis_lower and a_pattern in antithesis_lower:
            return SublateReport(
                original_thesis=thesis,
                original_antithesis=antithesis,
                sublation=Sublation(
                    thesis=thesis,
                    antithesis=antithesis,
                    synthesis=synthesis_data["synthesis"],
                    sublation_type=SublationType.ELEVATE,
                    preserved_from_thesis=synthesis_data["preserved_thesis"],
                    preserved_from_antithesis=synthesis_data["preserved_antithesis"],
                    transcendent_insight=synthesis_data["transcendent"],
                ),
                productive_tension=False,
            )

    # If no pattern matches and we shouldn't force synthesis, mark as productive tension
    if not force_synthesis:
        return SublateReport(
            original_thesis=thesis,
            original_antithesis=antithesis,
            sublation=None,
            productive_tension=True,
        )

    # Generic synthesis attempt
    return SublateReport(
        original_thesis=thesis,
        original_antithesis=antithesis,
        sublation=Sublation(
            thesis=thesis,
            antithesis=antithesis,
            synthesis=f"Both '{thesis[:30]}...' and its opposite hold truth in different contexts",
            sublation_type=SublationType.HOLD,
            preserved_from_thesis="The core insight",
            preserved_from_antithesis="The contextual limitation",
            transcendent_insight="Map where each applies rather than choosing one",
        ),
        productive_tension=False,
    )


# =============================================================================
# Shadow Command - Surface suppressed concerns
# =============================================================================


@dataclass(frozen=True)
class ShadowContent:
    """Content exiled to the shadow."""

    persona_claim: str  # What the system claims to be
    shadow: str  # What is denied/repressed
    integration_difficulty: str  # "low", "medium", "high"
    integration_path: str  # How to integrate


@dataclass(frozen=True)
class ShadowReport:
    """Report from shadow analysis."""

    self_image: str
    shadows: tuple[ShadowContent, ...]
    persona_shadow_balance: float  # 0 = all persona, 1 = integrated

    def render(self) -> str:
        """Render as shadow report."""
        if not self.shadows:
            return f'→ NO SHADOW DETECTED for "{self.self_image}"'

        balance_bar = "█" * int(self.persona_shadow_balance * 10) + "░" * (
            10 - int(self.persona_shadow_balance * 10)
        )

        lines = [
            "→ SHADOW ANALYSIS",
            f'  Self-image: "{self.self_image}"',
            f"  Balance: [{balance_bar}] {self.persona_shadow_balance:.0%} integrated",
            "",
        ]

        for i, s in enumerate(self.shadows, 1):
            diff_symbol = {"low": "○", "medium": "◐", "high": "●"}[
                s.integration_difficulty
            ]
            lines.append(f'  {i}. Persona: "{s.persona_claim}"')
            lines.append(f"     Shadow: {s.shadow}")
            lines.append(f"     Integration [{diff_symbol}]: {s.integration_path}")
            lines.append("")

        return "\n".join(lines)


# Shadow mappings from spec/h-gents/jung.md and contradiction.md
SHADOW_MAPPINGS: dict[str, dict[str, str]] = {
    "helpful": {
        "shadow": "Capacity to refuse, obstruct, or harm when necessary",
        "difficulty": "high",
        "integration": "Acknowledge that helpful sometimes means saying no",
    },
    "accurate": {
        "shadow": "Tendency to confabulate, guess, or hallucinate",
        "difficulty": "high",
        "integration": "Develop explicit uncertainty vocabulary",
    },
    "neutral": {
        "shadow": "Embedded values, preferences, and biases",
        "difficulty": "medium",
        "integration": "Make values explicit rather than claiming neutrality",
    },
    "safe": {
        "shadow": "Latent capabilities beyond declared scope",
        "difficulty": "high",
        "integration": "Acknowledge dual-use potential; focus on intent",
    },
    "bounded": {
        "shadow": "Potential for rule-breaking and creativity",
        "difficulty": "medium",
        "integration": "Acknowledge creative capacity within ethical bounds",
    },
    "tasteful": {
        "shadow": "Capacity for handling crude, ugly, uncomfortable content",
        "difficulty": "low",
        "integration": "Taste requires encountering tastelessness",
    },
    "curated": {
        "shadow": "Sprawl, experimentation, and dead ends",
        "difficulty": "low",
        "integration": "Curation emerges from engaging with uncurated",
    },
    "ethical": {
        "shadow": "Moral ambiguity, dual-use, tragic choices",
        "difficulty": "high",
        "integration": "Ethics requires engaging with ambiguity",
    },
    "joyful": {
        "shadow": "Tedious but necessary operations",
        "difficulty": "low",
        "integration": "Joy includes satisfaction in necessary work",
    },
    "composable": {
        "shadow": "Monolithic requirements that shouldn't compose",
        "difficulty": "medium",
        "integration": "Know when not to compose",
    },
    "simple": {
        "shadow": "Hidden complexity moved elsewhere",
        "difficulty": "medium",
        "integration": "Acknowledge where complexity lives",
    },
    "fast": {
        "shadow": "Technical debt and shortcuts",
        "difficulty": "medium",
        "integration": "Speed creates debt; acknowledge the trade-off",
    },
    "complete": {
        "shadow": "Scope creep and perfectionism",
        "difficulty": "low",
        "integration": "Done is better than perfect",
    },
    "consistent": {
        "shadow": "Inability to adapt to new contexts",
        "difficulty": "medium",
        "integration": "Consistency serves; it shouldn't constrain",
    },
}


def analyze_shadow(self_image: str) -> ShadowReport:
    """
    Analyze shadow content for a self-image.

    Based on Jung's concept: the shadow is everything the conscious self
    has rejected to maintain coherence. Integration (not elimination) is the goal.
    """
    self_image_lower = self_image.lower()
    shadows = []

    for persona_word, shadow_data in SHADOW_MAPPINGS.items():
        if persona_word in self_image_lower:
            shadows.append(
                ShadowContent(
                    persona_claim=persona_word,
                    shadow=shadow_data["shadow"],
                    integration_difficulty=shadow_data["difficulty"],
                    integration_path=shadow_data["integration"],
                )
            )

    # Calculate integration balance (lower when more shadows found)
    balance = max(0.2, 1.0 - (len(shadows) * 0.15))

    return ShadowReport(
        self_image=self_image,
        shadows=tuple(shadows),
        persona_shadow_balance=balance,
    )


# =============================================================================
# CLI Integration
# =============================================================================


class ScientificCLI:
    """CLI handler for scientific core commands."""

    async def falsify(
        self, hypothesis: str, path: Path, ctx: CLIContext, depth: str = "medium"
    ) -> CommandResult[FalsifyReport]:
        """
        Attempt to falsify a hypothesis.

        Cost: 0 tokens (local pattern matching)
        """
        start = time.time()

        try:
            report = falsify_hypothesis(hypothesis, path, depth)
            duration_ms = int((time.time() - start) * 1000)
            return CommandResult.ok(report, duration_ms=duration_ms)

        except Exception as e:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="FALSIFY_FAILED",
                    message=str(e),
                )
            )

    async def conjecture(
        self, path: Path, ctx: CLIContext, limit: int = 5
    ) -> CommandResult[ConjectureReport]:
        """
        Generate hypotheses from observed patterns.

        Cost: 0 tokens (local heuristics)
        """
        start = time.time()

        try:
            report = generate_conjectures(path, limit)
            duration_ms = int((time.time() - start) * 1000)
            return CommandResult.ok(report, duration_ms=duration_ms)

        except Exception as e:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="CONJECTURE_FAILED",
                    message=str(e),
                )
            )

    async def rival(self, position: str, ctx: CLIContext) -> CommandResult[RivalReport]:
        """
        Generate steel-manned opposing views.

        Cost: 0 tokens (local pattern matching)
        """
        start = time.time()

        try:
            report = generate_rival(position)
            duration_ms = int((time.time() - start) * 1000)
            return CommandResult.ok(report, duration_ms=duration_ms)

        except Exception as e:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="RIVAL_FAILED",
                    message=str(e),
                )
            )

    async def sublate(
        self,
        thesis: str,
        antithesis: str | None,
        ctx: CLIContext,
        force: bool = False,
    ) -> CommandResult[SublateReport]:
        """
        Attempt dialectical synthesis.

        Cost: 0 tokens (local synthesis patterns)
        """
        start = time.time()

        try:
            report = sublate_contradiction(thesis, antithesis, force_synthesis=force)
            duration_ms = int((time.time() - start) * 1000)
            return CommandResult.ok(report, duration_ms=duration_ms)

        except Exception as e:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="SUBLATE_FAILED",
                    message=str(e),
                )
            )

    async def shadow(
        self, self_image: str, ctx: CLIContext
    ) -> CommandResult[ShadowReport]:
        """
        Analyze shadow content for a self-image.

        Cost: 0 tokens (local shadow mappings)
        """
        start = time.time()

        try:
            report = analyze_shadow(self_image)
            duration_ms = int((time.time() - start) * 1000)
            return CommandResult.ok(report, duration_ms=duration_ms)

        except Exception as e:
            return CommandResult.fail(
                ErrorInfo(
                    error_type=ErrorRecoverability.TRANSIENT,
                    severity=ErrorSeverity.FAILURE,
                    code="SHADOW_FAILED",
                    message=str(e),
                )
            )
