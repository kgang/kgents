"""
Project Handler: H-jung Projection Analysis.

Based on Jungian psychology: We project disowned parts of ourselves
onto others. This command analyzes a statement to surface projections.

Usage:
    kgents project "They're so disorganized"
    kgents project --deep "I hate bureaucracy"
    kgents project --json "The codebase is a mess"

AGENTESE Path: void.shadow.project

When you criticize someone else strongly, ask: what does this reveal
about me?
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Projection Analysis Templates (for graceful degradation)
# =============================================================================

PROJECTION_PATTERNS = {
    "disorganized": {
        "shadow": "fear of your own chaos",
        "inquiry": "Where do you feel chaotic inside?",
        "integration": "Acknowledge that some disorder is creative",
    },
    "lazy": {
        "shadow": "repressed need for rest",
        "inquiry": "When did rest become shameful for you?",
        "integration": "Rest is not laziness—it's regeneration",
    },
    "arrogant": {
        "shadow": "suppressed confidence",
        "inquiry": "Where are you not allowing yourself to feel proud?",
        "integration": "Confidence is not arrogance when grounded",
    },
    "stupid": {
        "shadow": "fear of being wrong",
        "inquiry": "What would it mean if you were wrong?",
        "integration": "Being wrong is how we learn",
    },
    "messy": {
        "shadow": "perfectionism",
        "inquiry": "What does 'perfect' mean to you?",
        "integration": "Mess is part of creation",
    },
    "slow": {
        "shadow": "anxiety about productivity",
        "inquiry": "Who told you speed equals worth?",
        "integration": "Deliberation has value",
    },
    "selfish": {
        "shadow": "denied self-care",
        "inquiry": "When did taking care of yourself become wrong?",
        "integration": "Self-care enables care for others",
    },
    "aggressive": {
        "shadow": "suppressed anger",
        "inquiry": "What are you not allowing yourself to be angry about?",
        "integration": "Anger signals boundaries",
    },
}

# Generic fallback patterns
GENERIC_PATTERNS = [
    {
        "shadow": "something you've disowned in yourself",
        "inquiry": "What part of you does this remind you of?",
        "integration": "Consider what you're not seeing in yourself",
    },
    {
        "shadow": "a quality you've pushed away",
        "inquiry": "When did this quality become unacceptable?",
        "integration": "What you reject in others often lives in you",
    },
]


@dataclass
class ProjectionAnalysis:
    """Result of projection analysis."""

    original_statement: str
    shadow_content: str
    projected_onto: str
    self_inquiry: str
    integration_hint: str

    def to_dict(self) -> "dict[str, Any]":
        """Convert to JSON-serializable dict."""
        return {
            "original_statement": self.original_statement,
            "shadow_content": self.shadow_content,
            "projected_onto": self.projected_onto,
            "self_inquiry": self.self_inquiry,
            "integration_hint": self.integration_hint,
        }


def _analyze_projection(statement: str) -> ProjectionAnalysis:
    """
    Analyze a statement for projection patterns.

    Uses keyword matching with fallback to generic patterns.
    """
    statement_lower = statement.lower()

    # Find matching pattern
    matched = None
    projected_onto = "the target of your statement"

    for keyword, pattern in PROJECTION_PATTERNS.items():
        if keyword in statement_lower:
            matched = pattern
            # Try to extract target
            if "they" in statement_lower or "them" in statement_lower:
                projected_onto = "them"
            elif "it" in statement_lower:
                projected_onto = "the situation"
            break

    if matched is None:
        matched = random.choice(GENERIC_PATTERNS)

    return ProjectionAnalysis(
        original_statement=statement,
        shadow_content=matched["shadow"],
        projected_onto=projected_onto,
        self_inquiry=matched["inquiry"],
        integration_hint=matched["integration"],
    )


async def _analyze_with_llm(statement: str) -> ProjectionAnalysis | None:
    """
    Analyze projection using H-gent JungAgent (if available).

    Returns None if unavailable.
    """
    try:
        from agents.h.jung import JungAgent, JungInput

        # Build input - use statement as self-image context
        input_data = JungInput(
            system_self_image=f"Person who said: '{statement}'",
        )

        # Invoke JungAgent
        output = await JungAgent().invoke(input_data)

        # Extract first projection if available
        if output.projections:
            proj = output.projections[0]
            return ProjectionAnalysis(
                original_statement=statement,
                shadow_content=proj.shadow_content,
                projected_onto=proj.projected_onto,
                self_inquiry=f"Evidence: {proj.evidence}",
                integration_hint=(
                    output.integration_paths[0].integration_method
                    if output.integration_paths
                    else "Acknowledge and accept this part of yourself"
                ),
            )

        return None
    except ImportError:
        return None
    except Exception:
        return None


def _emit_output(
    human: str,
    semantic: "dict[str, Any] | ProjectionAnalysis",
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = (
            semantic.to_dict() if isinstance(semantic, ProjectionAnalysis) else semantic
        )
        ctx.emit_semantic(data)


def _print_help() -> None:
    """Print help for project command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --deep              Use LLM for deeper analysis (costs tokens)")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kgents project "They\'re so disorganized"')
    print('  kgents project --deep "I hate bureaucracy"')
    print('  kgents project "The codebase is a mess"')
    print()
    print("ABOUT PROJECTION:")
    print("  Projection is when we see in others what we won't see in ourselves.")
    print("  What irritates you about others often reveals something about you.")
    print("  This isn't blame—it's an invitation to self-knowledge.")
    print()
    print("PIPELINE USAGE:")
    print("  In REPL: self.soul.manifest >> void.shadow.project")
    print("  (Analyze what your soul state is projecting)")


def cmd_project(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    H-jung Projection Analysis: Where are you projecting?

    AGENTESE Path: void.shadow.project

    Analyzes a statement to surface what shadow content might be
    projected onto others.

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("project", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args
    use_llm = "--deep" in args

    # Extract statement (everything not a flag)
    statement_parts = []
    for arg in args:
        if arg.startswith("-"):
            continue
        statement_parts.append(arg)

    statement = " ".join(statement_parts)

    if not statement:
        print("[PROJECT] What statement would you like to analyze?")
        print('  Example: kgents project "They\'re so disorganized"')
        return 1

    if len(statement.split()) < 3:
        print("[PROJECT] Provide more context for meaningful analysis")
        print("  A sentence or phrase works best")
        return 1

    # Analyze projection
    if use_llm:
        result = asyncio.run(_analyze_with_llm(statement))
        if result is None:
            print("[PROJECT] LLM unavailable, using pattern matching")
            result = _analyze_projection(statement)
    else:
        result = _analyze_projection(statement)

    # Output
    if json_mode:
        import json

        print(json.dumps(result.to_dict(), indent=2))
    else:
        print()
        print(f'\033[90mYou said:\033[0m "{statement}"')
        print()
        print(f"\033[1;35mShadow content:\033[0m {result.shadow_content}")
        print(f"\033[1;36mProjected onto:\033[0m {result.projected_onto}")
        print()
        print(f"\033[33mSelf-inquiry:\033[0m {result.self_inquiry}")
        print()
        print(f"\033[32mIntegration hint:\033[0m {result.integration_hint}")
        print()

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(result.to_dict())

    return 0
