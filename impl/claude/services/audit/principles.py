"""
Principle Scoring: Evaluate specs against 7 constitutional principles.

Each principle has a scoring function that analyzes spec content and
structure to produce a score in [0, 1].

Scoring philosophy:
- 0.0-0.3: Violation (principle clearly not followed)
- 0.4-0.6: Partial (some adherence but significant gaps)
- 0.7-0.9: Strong (principle well followed)
- 1.0: Perfect (exemplary adherence)

See: spec/principles.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .types import PrincipleScores


def _load_spec(spec_path: Path) -> str:
    """Load spec file content with explicit UTF-8 encoding."""
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")

    try:
        return spec_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(
            f"Failed to read spec file (encoding issue): {spec_path}\n"
            f"Error: {e}\n"
            f"Hint: Ensure the file is UTF-8 encoded."
        ) from e
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied reading spec file: {spec_path}"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Unexpected error reading spec file: {spec_path}\n"
            f"Error: {e}"
        ) from e


def _count_sections(content: str) -> int:
    """Count markdown sections (## headings)."""
    return content.count("\n## ") + (1 if content.startswith("## ") else 0)


def _has_section(content: str, *keywords: str) -> bool:
    """Check if spec has a section containing any of the keywords."""
    lines = content.lower().split("\n")
    for line in lines:
        if line.startswith("##") and any(kw in line for kw in keywords):
            return True
    return False


def _score_tasteful(content: str) -> float:
    """
    Score TASTEFUL principle (0-1).

    Indicators of tasteful design:
    - Clear purpose statement
    - Justification for existence
    - Limited scope (not "kitchen sink")
    - Aesthetic considerations mentioned
    """
    score = 0.4  # Base score

    # Has clear purpose/overview section
    if _has_section(content, "purpose", "overview", "vision"):
        score += 0.2

    # Has justification ("why" section)
    if _has_section(content, "why", "rationale", "motivation"):
        score += 0.2

    # Not too broad (reasonable section count)
    section_count = _count_sections(content)
    if 3 <= section_count <= 12:
        score += 0.1
    elif section_count > 20:
        score -= 0.2  # Feature creep indicator

    # Mentions "tasteful" or aesthetic concerns
    if any(kw in content.lower() for kw in ["tasteful", "aesthetic", "elegant", "simple"]):
        score += 0.1

    return min(1.0, max(0.0, score))


def _score_curated(content: str) -> float:
    """
    Score CURATED principle (0-1).

    Indicators of curation:
    - Explicit choices made (not exhaustive listing)
    - Quality over quantity mentioned
    - Evolution strategy present
    - Heritage citations (builds on existing work)
    """
    score = 0.4  # Base score

    # Has examples but not exhaustive
    example_count = content.lower().count("example")
    if 1 <= example_count <= 5:
        score += 0.2
    elif example_count > 10:
        score -= 0.1  # Exhaustive enumeration

    # Mentions selection/curation
    if any(kw in content.lower() for kw in ["curated", "intentional", "selected", "chosen"]):
        score += 0.2

    # Has heritage citations
    if "heritage" in content.lower() or "citation" in content.lower():
        score += 0.1

    # Has evolution/versioning strategy
    if _has_section(content, "evolution", "migration", "deprecation"):
        score += 0.1

    return min(1.0, max(0.0, score))


def _score_ethical(content: str) -> float:
    """
    Score ETHICAL principle (0-1).

    Indicators of ethical design:
    - Transparency mentioned
    - Privacy considerations
    - Human agency preserved
    - No deception
    """
    score = 0.5  # Base score (neutral)

    # Explicitly mentions ethics/transparency
    if any(kw in content.lower() for kw in ["transparent", "privacy", "ethical", "human agency"]):
        score += 0.3

    # Has privacy/data section
    if _has_section(content, "privacy", "data", "security"):
        score += 0.1

    # Mentions limitations/uncertainty
    if any(kw in content.lower() for kw in ["limitation", "uncertainty", "disclaimer"]):
        score += 0.1

    return min(1.0, max(0.0, score))


def _score_joy_inducing(content: str) -> float:
    """
    Score JOY-INDUCING principle (0-1).

    Indicators of joy:
    - Personality/warmth in writing
    - Examples are engaging
    - Mentions delight/joy/fun
    - Has emoji or expressive language
    """
    score = 0.4  # Base score

    # Has engaging language
    if any(kw in content.lower() for kw in ["delight", "joy", "fun", "playful", "engaging"]):
        score += 0.2

    # Has emoji (personality)
    if any(c in content for c in "🎯🔮💎✨🎭"):
        score += 0.2

    # Has conversational tone
    if any(phrase in content.lower() for phrase in ["you can", "we'll", "let's", "imagine"]):
        score += 0.1

    # Has examples that tell stories
    if "example:" in content.lower() and len(content.split("example:")) >= 2:
        score += 0.1

    return min(1.0, max(0.0, score))


def _score_composable(content: str) -> float:
    """
    Score COMPOSABLE principle (0-1).

    Indicators of composability:
    - Category laws mentioned (identity, associativity)
    - Clear input/output types
    - Mentions composition (>>, ∘)
    - Single outputs (not arrays)
    """
    score = 0.3  # Lower base (composability is technical)

    # Mentions category laws
    if any(kw in content.lower() for kw in ["identity", "associativity", "composition law"]):
        score += 0.3

    # Has type signatures
    if any(kw in content for kw in ["->", "→", ":", "Agent["]):
        score += 0.2

    # Mentions composition operators
    if any(op in content for op in [">>", "∘", "compose"]):
        score += 0.2

    # Has interface/contract section
    if _has_section(content, "interface", "contract", "signature", "type"):
        score += 0.1

    # Warns against arrays/multiple outputs
    if "single output" in content.lower() or "not array" in content.lower():
        score += 0.2

    return min(1.0, max(0.0, score))


def _score_heterarchical(content: str) -> float:
    """
    Score HETERARCHICAL principle (0-1).

    Indicators of heterarchy:
    - Mentions dual loop (autonomous + functional)
    - Flux/dynamic allocation
    - No fixed hierarchy
    - Agent can both lead and follow
    """
    score = 0.5  # Base score (neutral)

    # Mentions dual loop pattern
    if any(kw in content.lower() for kw in ["dual loop", "autonomous", "functional mode"]):
        score += 0.2

    # Mentions flux/dynamics
    if any(kw in content.lower() for kw in ["flux", "dynamic", "heterarch"]):
        score += 0.2

    # Avoids fixed hierarchy language
    if not any(kw in content.lower() for kw in ["orchestrator", "master", "boss", "manager"]):
        score += 0.1

    return min(1.0, max(0.0, score))


def _score_generative(content: str) -> float:
    """
    Score GENERATIVE principle (0-1).

    Indicators of generativity:
    - Spec is concise (compression)
    - Implementation can be derived
    - Has grammar/rules not instances
    - Mentions "generate" or "derive"
    """
    score = 0.4  # Base score

    # Mentions generation/derivation
    if any(kw in content.lower() for kw in ["generate", "derive", "compile", "compression"]):
        score += 0.2

    # Has grammar/operad section
    if _has_section(content, "grammar", "operad", "rules", "laws"):
        score += 0.2

    # Concise (not overly long)
    line_count = len(content.split("\n"))
    if line_count < 300:
        score += 0.1
    elif line_count > 1000:
        score -= 0.2  # Too verbose

    # Mentions regenerability
    if "regenera" in content.lower() or "reconstruct" in content.lower():
        score += 0.1

    return min(1.0, max(0.0, score))


def score_principles(spec_path: Path) -> PrincipleScores:
    """
    Score a spec against all 7 constitutional principles.

    Args:
        spec_path: Path to spec markdown file

    Returns:
        PrincipleScores with scores in [0, 1] for each principle

    Raises:
        FileNotFoundError: If spec file doesn't exist
    """
    content = _load_spec(spec_path)

    return PrincipleScores(
        tasteful=_score_tasteful(content),
        curated=_score_curated(content),
        ethical=_score_ethical(content),
        joy_inducing=_score_joy_inducing(content),
        composable=_score_composable(content),
        heterarchical=_score_heterarchical(content),
        generative=_score_generative(content),
    )


async def score_principles_async(spec_path: Path) -> PrincipleScores:
    """Async version of score_principles (currently just wraps sync version)."""
    return score_principles(spec_path)
