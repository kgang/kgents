"""
Yes-And Handler: Improv-style idea expansion.

Based on the improv technique "Yes, and..." - accept an idea and build on it.
Never block, always expand.

Usage:
    kgents yes-and "What if agents could dream?"
    kgents yes-and --rounds 3 "Semantic memory as garden"
    kgents yes-and --persona playful "Code review as jazz"

AGENTESE Path: concept.creativity.expand
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Expansion Templates (for graceful degradation when LLM unavailable)
# =============================================================================

EXPANSION_PATTERNS = [
    "Yes, and {idea}... what if we took that further and considered {extension}?",
    "Building on {idea}... imagine combining this with {mashup}",
    "I love {idea}! And what if {twist}?",
    "Yes! And the deeper implication is {implication}",
    "{idea}—yes! And in a different context: {recontextualization}",
]

EXTENSIONS = [
    "the opposite extreme",
    "a completely different scale",
    "an unexpected medium",
    "a parallel in nature",
    "the historical precedent",
    "the future evolution",
    "the meta-level version",
    "the embodied experience",
]

MASHUPS = [
    "jazz improvisation",
    "gardening",
    "architecture",
    "cooking",
    "theater",
    "sports",
    "weather patterns",
    "children's games",
]

TWISTS = [
    "it was temporal instead of spatial",
    "the constraints became features",
    "we inverted the hierarchy",
    "it worked backwards",
    "the audience became creators",
    "errors were celebrated",
]

PERSONA_STYLES = {
    "playful": "with delight and whimsy",
    "philosophical": "exploring deeper meaning",
    "practical": "with actionable next steps",
    "provocative": "challenging assumptions",
    "warm": "with encouragement and support",
}


@dataclass
class YesAndResponse:
    """Response containing expanded ideas."""

    original: str
    expansions: list[str]
    rounds: int
    persona: str | None

    def to_dict(self) -> "dict[str, Any]":
        """Convert to JSON-serializable dict."""
        return {
            "original": self.original,
            "expansions": self.expansions,
            "rounds": self.rounds,
            "persona": self.persona,
            "count": len(self.expansions),
        }


def _generate_expansion(idea: str) -> str:
    """Generate a single expansion using templates."""
    pattern = random.choice(EXPANSION_PATTERNS)

    # Fill in template
    expansion = pattern.format(
        idea=idea[:50] + "..." if len(idea) > 50 else idea,
        extension=random.choice(EXTENSIONS),
        mashup=random.choice(MASHUPS),
        twist=random.choice(TWISTS),
        implication=f"the relationship between {random.choice(EXTENSIONS)} and the original",
        recontextualization=f"applied to {random.choice(MASHUPS)}",
    )

    return expansion


def _select_expansions(
    idea: str, rounds: int = 3, persona: str | None = None
) -> list[str]:
    """Generate multiple expansions using templates."""
    expansions = []
    for _ in range(rounds):
        expansion = _generate_expansion(idea)
        if persona and persona in PERSONA_STYLES:
            expansion += f" ({PERSONA_STYLES[persona]})"
        expansions.append(expansion)
    return expansions


async def _generate_with_llm(
    idea: str, rounds: int, persona: str | None
) -> YesAndResponse | None:
    """
    Generate expansions using LLM (if available).

    Returns None if LLM unavailable.
    """
    try:
        from agents.a.creativity import CreativityCoach, CreativityInput, CreativityMode
        from runtime.openrouter import OpenRouterRuntime

        coach = CreativityCoach(response_count=rounds)
        runtime = OpenRouterRuntime()

        input_data = CreativityInput(
            seed=idea,
            mode=CreativityMode.EXPAND,
            context=f"Use 'Yes, and...' improv technique to expand: {idea}",
        )

        result = await runtime.execute(coach, input_data)
        return YesAndResponse(
            original=idea,
            expansions=result.output.responses,
            rounds=rounds,
            persona=persona,
        )
    except ImportError:
        return None
    except Exception:
        return None


def _emit_output(
    human: str,
    semantic: "dict[str, Any] | YesAndResponse",
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = semantic.to_dict() if isinstance(semantic, YesAndResponse) else semantic
        ctx.emit_semantic(data)


def _print_help() -> None:
    """Print help for yes-and command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --rounds <n>        Number of expansions (default: 3)")
    print(
        "  --persona <type>    Style: playful, philosophical, practical, provocative, warm"
    )
    print("  --llm               Use LLM for generation (costs tokens)")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kgents yes-and "What if tests could dream?"')
    print('  kgents yes-and --rounds 5 "Code as poetry"')
    print('  kgents yes-and --persona playful "Debugging as archaeology"')
    print()
    print("ABOUT YES-AND:")
    print("  From improv theater: accept and build, never block.")
    print("  'Yes, and...' keeps possibility space open.")
    print()
    print("PIPELINE USAGE:")
    print("  In REPL: void.serendipity.prompt >> concept.creativity.expand")
    print("  (Generate random seed, then expand it)")


def cmd_yes_and(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Improv-style idea expansion: "Yes, and..."

    AGENTESE Path: concept.creativity.expand

    Never blocks, always expands. Accept the idea and build on it.

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("yes-and", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args
    use_llm = "--llm" in args

    # Parse rounds
    rounds = 3
    for i, arg in enumerate(args):
        if arg == "--rounds" and i + 1 < len(args):
            try:
                rounds = int(args[i + 1])
                rounds = max(1, min(rounds, 10))  # Clamp to 1-10
            except ValueError:
                print("[YES-AND] Invalid rounds value")
                return 1

    # Parse persona
    persona = None
    for i, arg in enumerate(args):
        if arg == "--persona" and i + 1 < len(args):
            persona = args[i + 1].lower()
            if persona not in PERSONA_STYLES:
                print(f"[YES-AND] Unknown persona: {persona}")
                print(f"  Available: {', '.join(PERSONA_STYLES.keys())}")
                return 1

    # Extract idea (everything not a flag)
    idea_parts = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg.startswith("-"):
            if arg in ("--rounds", "--persona"):
                skip_next = True
            continue
        idea_parts.append(arg)

    idea = " ".join(idea_parts)

    if not idea:
        print("[YES-AND] What idea would you like to expand?")
        print('  Example: kgents yes-and "What if agents could dream?"')
        return 1

    # Generate expansions
    if use_llm:
        result = asyncio.run(_generate_with_llm(idea, rounds, persona))
        if result is None:
            print("[YES-AND] LLM unavailable, using templates")
            expansions = _select_expansions(idea, rounds, persona)
            result = YesAndResponse(
                original=idea, expansions=expansions, rounds=rounds, persona=persona
            )
    else:
        expansions = _select_expansions(idea, rounds, persona)
        result = YesAndResponse(
            original=idea, expansions=expansions, rounds=rounds, persona=persona
        )

    # Output
    if json_mode:
        import json

        print(json.dumps(result.to_dict(), indent=2))
    else:
        print()
        print(f"\033[1;32mYes, and...\033[0m {idea}")
        print()
        for i, expansion in enumerate(result.expansions, 1):
            print(f"  \033[33m{i}.\033[0m {expansion}")
        print()
        if persona:
            print(f"\033[90m  Persona: {persona}\033[0m")
            print()

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(result.to_dict())

    return 0
