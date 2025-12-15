"""
Constrain Handler: Generate productive constraints for creative work.

Constraints are not limitations—they are creative catalysts.
This command generates productive constraints that spark innovation.

Usage:
    kgents constrain "API design"
    kgents constrain "writing a novel" --count 5
    kgents constrain --persona provocative "team meeting"

AGENTESE Path: concept.creativity.constrain
"""

from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Constraint Templates (for graceful degradation when LLM unavailable)
# =============================================================================

CONSTRAINT_TEMPLATES = {
    "general": [
        "What if you had to complete this in half the time?",
        "What if you could only use 3 key elements?",
        "What if it had to work for someone with the opposite expertise?",
        "What if you had to explain it to a child?",
        "What if the primary tool you rely on was unavailable?",
        "What if it had to be reversible at any point?",
        "What if you had to do it in public?",
        "What if you had to make it work offline?",
        "What if the budget was 10x smaller?",
        "What if you had to teach someone else to do it simultaneously?",
    ],
    "code": [
        "What if you couldn't use any external dependencies?",
        "What if it had to run in under 100ms?",
        "What if all state had to be immutable?",
        "What if you couldn't use conditionals?",
        "What if it had to be fully composable?",
        "What if a junior developer had to maintain it?",
        "What if it had to work with 10x the data?",
        "What if you had to write tests first?",
    ],
    "design": [
        "What if it had to work in grayscale only?",
        "What if it had to be accessible to someone who is blind?",
        "What if it had to fit on a business card?",
        "What if it had to work on a 10-year-old device?",
        "What if it had to be understood in 3 seconds?",
        "What if it had to be beautiful without any images?",
    ],
    "writing": [
        "What if you had a strict word limit of 500 words?",
        "What if you couldn't use the word 'the'?",
        "What if every paragraph had to start with a question?",
        "What if it had to rhyme?",
        "What if you had to write it backwards?",
        "What if each sentence had to be shorter than the last?",
    ],
}

PERSONA_STYLES = {
    "playful": "with a sense of whimsy and delight",
    "provocative": "that challenges your deepest assumptions",
    "practical": "that you could implement today",
    "philosophical": "that questions the very nature of the task",
    "warm": "that feels like a gentle nudge from a friend",
}


@dataclass
class ConstraintResponse:
    """Response containing generated constraints."""

    topic: str
    constraints: list[str]
    persona: str | None

    def to_dict(self) -> "dict[str, Any]":
        """Convert to JSON-serializable dict."""
        return {
            "topic": self.topic,
            "constraints": self.constraints,
            "count": len(self.constraints),
            "persona": self.persona,
        }


def _select_constraints(
    topic: str, count: int = 3, persona: str | None = None
) -> list[str]:
    """
    Select constraints using templates.

    Attempts to match topic to domain, falls back to general.
    """
    # Detect domain from topic
    topic_lower = topic.lower()
    domain = "general"

    if any(kw in topic_lower for kw in ["code", "api", "function", "class", "program"]):
        domain = "code"
    elif any(kw in topic_lower for kw in ["design", "ui", "ux", "visual", "layout"]):
        domain = "design"
    elif any(
        kw in topic_lower for kw in ["write", "writing", "essay", "story", "blog"]
    ):
        domain = "writing"

    # Get pool of constraints
    pool = CONSTRAINT_TEMPLATES[domain] + CONSTRAINT_TEMPLATES["general"]

    # Shuffle and select
    random.shuffle(pool)
    selected = pool[:count]

    # Apply persona flavor if specified
    if persona and persona in PERSONA_STYLES:
        flavor = PERSONA_STYLES[persona]
        selected = [f"{c} ({flavor})" for c in selected]

    return selected


async def _generate_with_llm(
    topic: str, count: int, persona: str | None
) -> ConstraintResponse | None:
    """
    Generate constraints using LLM (if available).

    Returns None if LLM unavailable.
    """
    try:
        from agents.a.creativity import CreativityCoach, CreativityInput, CreativityMode
        from runtime.openrouter import OpenRouterRuntime

        coach = CreativityCoach(response_count=count)
        runtime = OpenRouterRuntime()

        input_data = CreativityInput(
            seed=topic,
            mode=CreativityMode.CONSTRAIN,
            context=f"Generate {count} productive constraints for: {topic}",
        )

        result = await runtime.execute(coach, input_data)
        return ConstraintResponse(
            topic=topic,
            constraints=result.output.responses,
            persona=persona,
        )
    except ImportError:
        return None
    except Exception:
        return None


def _emit_output(
    human: str,
    semantic: "dict[str, Any] | ConstraintResponse",
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = (
            semantic.to_dict() if isinstance(semantic, ConstraintResponse) else semantic
        )
        ctx.emit_semantic(data)


def _print_help() -> None:
    """Print help for constrain command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --count <n>         Number of constraints (default: 3)")
    print(
        "  --persona <type>    Style: playful, provocative, practical, philosophical, warm"
    )
    print("  --llm               Use LLM for generation (costs tokens)")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kgents constrain "API design"')
    print('  kgents constrain --count 5 "team meeting"')
    print('  kgents constrain --persona provocative "architecture review"')
    print()
    print("PIPELINE USAGE:")
    print("  In REPL: void.serendipity.prompt >> concept.creativity.constrain")
    print("  (Generate random seed, then constrain it)")


def cmd_constrain(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Generate productive constraints for a topic.

    AGENTESE Path: concept.creativity.constrain

    Constraints are creative catalysts, not limitations.

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("constrain", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args
    use_llm = "--llm" in args

    # Parse count
    count = 3
    for i, arg in enumerate(args):
        if arg == "--count" and i + 1 < len(args):
            try:
                count = int(args[i + 1])
            except ValueError:
                print("[CONSTRAIN] Invalid count value")
                return 1

    # Parse persona
    persona = None
    for i, arg in enumerate(args):
        if arg == "--persona" and i + 1 < len(args):
            persona = args[i + 1].lower()
            if persona not in PERSONA_STYLES:
                print(f"[CONSTRAIN] Unknown persona: {persona}")
                print(f"  Available: {', '.join(PERSONA_STYLES.keys())}")
                return 1

    # Extract topic (everything not a flag)
    topic_parts = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg.startswith("-"):
            if arg in ("--count", "--persona"):
                skip_next = True
            continue
        topic_parts.append(arg)

    topic = " ".join(topic_parts)

    if not topic:
        print("[CONSTRAIN] What would you like to constrain?")
        print('  Example: kgents constrain "API design"')
        return 1

    # Generate constraints
    if use_llm:
        result = asyncio.run(_generate_with_llm(topic, count, persona))
        if result is None:
            print("[CONSTRAIN] LLM unavailable, using templates")
            constraints = _select_constraints(topic, count, persona)
            result = ConstraintResponse(
                topic=topic, constraints=constraints, persona=persona
            )
    else:
        constraints = _select_constraints(topic, count, persona)
        result = ConstraintResponse(
            topic=topic, constraints=constraints, persona=persona
        )

    # Output
    if json_mode:
        import json

        print(json.dumps(result.to_dict(), indent=2))
    else:
        print()
        print(f"\033[1;36mConstraints for:\033[0m {topic}")
        print()
        for i, constraint in enumerate(result.constraints, 1):
            print(f"  \033[33m{i}.\033[0m {constraint}")
        print()
        if persona:
            print(f"\033[90m  Persona: {persona}\033[0m")
            print()

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(result.to_dict())

    return 0
