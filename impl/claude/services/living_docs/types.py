"""
Living Docs Core Types

The 5 core types from spec/protocols/living-docs.md:
- DocNode: Atomic documentation primitive
- TeachingMoment: A gotcha with provenance
- LivingDocsObserver: Who's reading determines what they see
- Surface: Projected output for an observer
- Verification: Round-trip verification result
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal


class Tier(Enum):
    """
    Extraction tier determines extraction depth.

    Match effort to importance - not every function needs full extraction.
    """

    MINIMAL = "minimal"  # Private helpers: signature only
    STANDARD = "standard"  # Public API: signature + summary + examples
    RICH = "rich"  # Crown Jewels: full teaching moments + verification


@dataclass(frozen=True)
class TeachingMoment:
    """
    A gotcha with provenance. The killer feature.

    Teaching moments live in docstrings, not wikis.
    Each has traceable evidence back to the test that validates it.

    Teaching:
        gotcha: Always include evidence when creating TeachingMoments.
                (Evidence: test_types.py::test_teaching_moment_evidence)
    """

    insight: str
    severity: Literal["info", "warning", "critical"]
    evidence: str | None = None  # test_file.py::test_name
    commit: str | None = None  # Git SHA where learned

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "insight": self.insight,
            "severity": self.severity,
            "evidence": self.evidence,
            "commit": self.commit,
        }


@dataclass(frozen=True)
class DocNode:
    """
    Atomic documentation primitive extracted from source.

    A DocNode captures everything knowable about a symbol from:
    - Its signature (static analysis)
    - Its docstring (human-written)
    - Its tests (evidence)
    - Its git history (provenance)
    - Its AGENTESE path (navigation)

    Teaching:
        gotcha: agentese_path is extracted from "AGENTESE: <path>" in docstrings.
                Not all symbols have AGENTESE paths—only exposed nodes do.
                (Evidence: test_extractor.py::test_agentese_path_extraction)

        gotcha: related_symbols should be kept small (max 5).
                Too many cross-references makes navigation confusing.
                (Evidence: test_types.py::test_related_symbols_limit)
    """

    symbol: str  # Function/class name
    signature: str  # Type signature
    summary: str  # First line of docstring
    examples: tuple[str, ...] = ()  # From doctest or Example: sections
    teaching: tuple[TeachingMoment, ...] = ()
    evidence: tuple[str, ...] = ()  # Test refs that verify behavior
    tier: Tier = Tier.STANDARD
    module: str = ""  # Module path (e.g., "services.brain.persistence")
    agentese_path: str | None = None  # e.g., "self.memory.capture"
    related_symbols: tuple[str, ...] = ()  # Cross-references to related docs

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "signature": self.signature,
            "summary": self.summary,
            "examples": list(self.examples),
            "teaching": [t.to_dict() for t in self.teaching],
            "evidence": list(self.evidence),
            "tier": self.tier.value,
            "module": self.module,
            "agentese_path": self.agentese_path,
            "related_symbols": list(self.related_symbols),
        }

    def to_text(self) -> str:
        """
        Convert to human-readable text.

        Format varies by tier:
        - MINIMAL: Just signature
        - STANDARD: Signature + summary + examples
        - RICH: Full content with teaching moments + AGENTESE path
        """
        lines: list[str] = []

        # Always include signature
        lines.append(f"## {self.symbol}")
        lines.append(f"```python\n{self.signature}\n```")

        # RICH includes AGENTESE path if available
        if self.agentese_path:
            lines.append(f"\n**AGENTESE**: `{self.agentese_path}`")

        if self.tier == Tier.MINIMAL:
            return "\n".join(lines)

        # STANDARD and RICH include summary
        if self.summary:
            lines.append(f"\n{self.summary}")

        # STANDARD and RICH include examples
        if self.examples:
            lines.append("\n**Examples:**")
            for example in self.examples:
                lines.append(f"```python\n{example}\n```")

        if self.tier == Tier.STANDARD:
            return "\n".join(lines)

        # RICH includes teaching moments
        if self.teaching:
            lines.append("\n**Gotchas:**")
            for moment in self.teaching:
                severity_icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}.get(
                    moment.severity, "•"
                )
                lines.append(f"- {severity_icon} {moment.insight}")
                if moment.evidence:
                    lines.append(f"  - Evidence: `{moment.evidence}`")

        return "\n".join(lines)


@dataclass(frozen=True)
class LivingDocsObserver:
    """
    Who's reading determines what they see.

    The same DocNode projects differently based on:
    - kind: human (narrative), agent (structured), ide (tooltip)
    - density: compact, comfortable, spacious (for humans)
    """

    kind: Literal["human", "agent", "ide"]
    density: Literal["compact", "comfortable", "spacious"] = "comfortable"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "kind": self.kind,
            "density": self.density,
        }


@dataclass(frozen=True)
class Surface:
    """
    Projected output for an observer.

    The result of applying the projection functor:
        project(DocNode, Observer) -> Surface
    """

    content: str
    format: Literal["markdown", "structured", "tooltip"]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "format": self.format,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class Verification:
    """
    Round-trip verification result.

    Answers: "If you can't regenerate impl from docs, docs don't capture essence."
    """

    equivalent: bool
    score: float  # 0.0-1.0 semantic similarity
    missing: tuple[str, ...] = ()  # What docs don't capture

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "equivalent": self.equivalent,
            "score": self.score,
            "missing": list(self.missing),
        }

    @property
    def compression_adequate(self) -> bool:
        """Check if docs adequately compress implementation."""
        return self.score > 0.8 and len(self.missing) == 0
