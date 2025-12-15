"""
Tension Handler: Surface unresolved tensions in context.

Identifies opposing forces, contradictions, and held tensions
that create creative pressure or cognitive dissonance.

Usage:
    kgents tension                    # Current project tensions
    kgents tension --system           # System-level tensions
    kgents tension --plans            # Plan file tensions
    kgents tension <path>             # Tensions in specific file

AGENTESE Path: self.soul.tension

Tensions are not bugs—they're features. They create generative pressure.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class TensionTemplate(TypedDict):
    """Type for tension template dict."""

    pole_a: str
    pole_b: str
    context: str
    severity: float


# =============================================================================
# Tension Detection Templates
# =============================================================================

COMMON_TENSIONS: list[TensionTemplate] = [
    {
        "pole_a": "Move fast",
        "pole_b": "Be thorough",
        "context": "Development velocity",
        "severity": 0.6,
    },
    {
        "pole_a": "Keep it simple",
        "pole_b": "Handle edge cases",
        "context": "Code complexity",
        "severity": 0.5,
    },
    {
        "pole_a": "Ship now",
        "pole_b": "Get it right",
        "context": "Release timing",
        "severity": 0.7,
    },
    {
        "pole_a": "Be consistent",
        "pole_b": "Be adaptive",
        "context": "System behavior",
        "severity": 0.4,
    },
    {
        "pole_a": "Automate everything",
        "pole_b": "Keep human judgment",
        "context": "Process design",
        "severity": 0.5,
    },
    {
        "pole_a": "Be principled",
        "pole_b": "Be pragmatic",
        "context": "Decision making",
        "severity": 0.6,
    },
    {
        "pole_a": "Document everything",
        "pole_b": "Let code speak",
        "context": "Documentation",
        "severity": 0.3,
    },
    {
        "pole_a": "Optimize performance",
        "pole_b": "Maintain readability",
        "context": "Code quality",
        "severity": 0.5,
    },
]

SYNTHESIS_HINTS = [
    "Hold both poles consciously—the tension itself is generative",
    "Look for a third option that transcends the binary",
    "Accept that this tension may never fully resolve",
    "Ask: which pole is more important in this specific context?",
    "The tension reveals what you value—lean into that",
    "Sometimes the answer is 'both, but at different times'",
    "Consider: what would synthesis look like here?",
]


@dataclass
class Tension:
    """A single tension between two poles."""

    pole_a: str
    pole_b: str
    context: str
    severity: float  # 0.0 = mild, 1.0 = critical
    held_since: str | None = None

    def to_dict(self) -> "dict[str, Any]":
        return {
            "pole_a": self.pole_a,
            "pole_b": self.pole_b,
            "context": self.context,
            "severity": self.severity,
            "held_since": self.held_since,
        }


@dataclass
class TensionReport:
    """Report of tensions in a context."""

    tensions: list[Tension] = field(default_factory=list)
    dominant_tension: Tension | None = None
    synthesis_hints: list[str] = field(default_factory=list)
    source: str = "general"

    def to_dict(self) -> "dict[str, Any]":
        return {
            "tensions": [t.to_dict() for t in self.tensions],
            "dominant_tension": self.dominant_tension.to_dict()
            if self.dominant_tension
            else None,
            "synthesis_hints": self.synthesis_hints,
            "source": self.source,
            "count": len(self.tensions),
        }

    def to_numeric_sequence(self) -> list[float]:
        """For sparkline composition: tension severities."""
        return [t.severity for t in self.tensions]


def _detect_tensions_from_text(text: str) -> list[Tension]:
    """
    Detect tensions in text by looking for contrastive patterns.
    """
    tensions = []

    # Simple heuristic: look for "but", "however", "versus", "vs", "or"
    text_lower = text.lower()

    contrastive_markers = ["but", "however", "although", "versus", " vs ", " or "]

    for marker in contrastive_markers:
        if marker in text_lower:
            # Found potential tension - use generic template
            import random

            template = random.choice(COMMON_TENSIONS)
            tensions.append(
                Tension(
                    pole_a=template["pole_a"],
                    pole_b=template["pole_b"],
                    context=f"Detected in text ({marker})",
                    severity=template["severity"],
                )
            )
            break

    return tensions


def _get_project_tensions() -> TensionReport:
    """
    Get tensions in the current project context.

    Uses common development tensions as baseline.
    """
    import random

    # Select 3-5 relevant tensions
    selected = random.sample(COMMON_TENSIONS, min(4, len(COMMON_TENSIONS)))

    tensions = [
        Tension(
            pole_a=t["pole_a"],
            pole_b=t["pole_b"],
            context=t["context"],
            severity=t["severity"],
        )
        for t in selected
    ]

    # Find dominant (highest severity)
    dominant = max(tensions, key=lambda t: t.severity) if tensions else None

    # Select synthesis hints
    hints = random.sample(SYNTHESIS_HINTS, min(2, len(SYNTHESIS_HINTS)))

    return TensionReport(
        tensions=tensions,
        dominant_tension=dominant,
        synthesis_hints=hints,
        source="project",
    )


def _get_file_tensions(path: str) -> TensionReport:
    """
    Analyze a specific file for tensions.
    """
    if not os.path.exists(path):
        return TensionReport(source=f"file:{path} (not found)")

    try:
        with open(path) as f:
            content = f.read()
    except Exception:
        return TensionReport(source=f"file:{path} (read error)")

    tensions = _detect_tensions_from_text(content)

    # If no tensions found, use generic
    if not tensions:
        import random

        template = random.choice(COMMON_TENSIONS)
        tensions.append(
            Tension(
                pole_a=template["pole_a"],
                pole_b=template["pole_b"],
                context="General development tension",
                severity=template["severity"],
            )
        )

    dominant = max(tensions, key=lambda t: t.severity) if tensions else None

    import random

    hints = random.sample(SYNTHESIS_HINTS, min(2, len(SYNTHESIS_HINTS)))

    return TensionReport(
        tensions=tensions,
        dominant_tension=dominant,
        synthesis_hints=hints,
        source=f"file:{path}",
    )


def _get_system_tensions() -> TensionReport:
    """
    Get system-level tensions (architecture, design decisions).
    """
    system_tensions = [
        Tension(
            pole_a="Centralized control",
            pole_b="Distributed autonomy",
            context="System architecture",
            severity=0.7,
        ),
        Tension(
            pole_a="Strong typing",
            pole_b="Dynamic flexibility",
            context="Type system",
            severity=0.5,
        ),
        Tension(
            pole_a="Explicit is better",
            pole_b="Convention over configuration",
            context="API design",
            severity=0.4,
        ),
    ]

    dominant = max(system_tensions, key=lambda t: t.severity)

    import random

    hints = random.sample(SYNTHESIS_HINTS, 2)

    return TensionReport(
        tensions=system_tensions,
        dominant_tension=dominant,
        synthesis_hints=hints,
        source="system",
    )


def _emit_output(
    human: str,
    semantic: "dict[str, Any] | TensionReport",
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = semantic.to_dict() if isinstance(semantic, TensionReport) else semantic
        ctx.emit_semantic(data)


def _severity_bar(severity: float) -> str:
    """Render severity as a visual bar."""
    filled = int(severity * 10)
    empty = 10 - filled

    if severity < 0.4:
        color = "\033[32m"  # Green
    elif severity < 0.7:
        color = "\033[33m"  # Yellow
    else:
        color = "\033[31m"  # Red

    return f"{color}{'█' * filled}{'░' * empty}\033[0m"


def _print_help() -> None:
    """Print help for tension command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --system            Show system-level tensions")
    print("  --plans             Analyze plan files for tensions")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents tension                    # Project tensions")
    print("  kgents tension --system           # Architecture tensions")
    print("  kgents tension plans/_focus.md    # Specific file")
    print()
    print("ABOUT TENSION:")
    print("  Tensions are not problems—they're generative pressure.")
    print("  Holding opposing forces consciously creates wisdom.")
    print("  The goal is not resolution but conscious holding.")
    print()
    print("PIPELINE USAGE:")
    print("  In REPL: self.soul.tension >> world.viz.sparkline")
    print("  (Visualize tension severity as sparkline)")


def cmd_tension(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    List unresolved tensions in the current context.

    AGENTESE Path: self.soul.tension

    Surfaces tensions between opposing forces. Tensions are generative.

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("tension", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args
    system_mode = "--system" in args
    plans_mode = "--plans" in args

    # Extract file path (everything not a flag)
    file_parts = []
    for arg in args:
        if arg.startswith("-"):
            continue
        file_parts.append(arg)

    file_path = " ".join(file_parts) if file_parts else None

    # Get tensions based on mode
    if system_mode:
        report = _get_system_tensions()
    elif file_path:
        report = _get_file_tensions(file_path)
    elif plans_mode:
        # Analyze plans directory
        report = _get_file_tensions("plans/_focus.md")
    else:
        report = _get_project_tensions()

    # Output
    if json_mode:
        import json

        print(json.dumps(report.to_dict(), indent=2))
    else:
        print()
        print(f"\033[1;36mTensions\033[0m ({report.source})")
        print()

        for i, tension in enumerate(report.tensions, 1):
            bar = _severity_bar(tension.severity)
            print(
                f"  {i}. \033[33m{tension.pole_a}\033[0m vs \033[33m{tension.pole_b}\033[0m"
            )
            print(f"     {tension.context}")
            print(f"     Severity: {bar} {tension.severity:.1f}")
            print()

        if report.dominant_tension:
            print(
                f"\033[1;31mDominant:\033[0m {report.dominant_tension.pole_a} vs {report.dominant_tension.pole_b}"
            )
            print()

        if report.synthesis_hints:
            print("\033[32mSynthesis hints:\033[0m")
            for hint in report.synthesis_hints:
                print(f"  • {hint}")
            print()

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(report.to_dict())

    return 0
