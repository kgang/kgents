"""
Why Handler: Recursive why until bedrock assumptions.

The Five Whys technique (Toyota) adapted for self-inquiry.
Keeps asking "why?" until reaching foundational assumptions.

Usage:
    kgents why "We need microservices"
    kgents why --depth 5 "Users want dark mode"
    kgents why --socratic "The tests should pass"

AGENTESE Path: self.soul.why

This is K-gent inquiry mode—dig deeper to find the real reason.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Why Chain Templates (for graceful degradation)
# =============================================================================

WHY_PROMPTS = [
    "Why is that important?",
    "What's the deeper reason?",
    "Why does that matter?",
    "What's driving that belief?",
    "Where does that assumption come from?",
    "What would happen if that weren't true?",
    "Why do you believe that?",
]

BEDROCK_PATTERNS = [
    "Because it's the right thing to do",
    "Because it aligns with our values",
    "Because that's what we're optimizing for",
    "Because the alternative is worse",
    "Because it serves the user",
    "Because it's elegant",
    "Because it's sustainable",
    "Because it's honest",
]


@dataclass
class WhyStep:
    """A single step in the why chain."""

    question: str
    answer: str
    depth: int

    def to_dict(self) -> "dict[str, Any]":
        return {"question": self.question, "answer": self.answer, "depth": self.depth}


@dataclass
class WhyChain:
    """Complete chain of why questions."""

    original: str
    chain: list[WhyStep] = field(default_factory=list)
    bedrock: str = ""
    max_depth: int = 5

    def to_dict(self) -> "dict[str, Any]":
        return {
            "original": self.original,
            "chain": [step.to_dict() for step in self.chain],
            "bedrock": self.bedrock,
            "depth_reached": len(self.chain),
            "max_depth": self.max_depth,
        }

    def to_numeric_sequence(self) -> list[float]:
        """For sparkline composition: depth progression."""
        return [float(i + 1) for i in range(len(self.chain))]


def _generate_why_chain(statement: str, depth: int = 5) -> WhyChain:
    """
    Generate a why chain using templates.

    Each step digs deeper into assumptions.
    """
    import random

    chain = WhyChain(original=statement, max_depth=depth)
    current_statement = statement

    for i in range(depth):
        # Generate question
        question = random.choice(WHY_PROMPTS)

        # Generate answer (in real LLM mode, this would be thoughtful)
        if i < depth - 1:
            # Intermediate answer - transforms the statement
            prefixes = [
                "Because",
                "In order to",
                "So that",
                "Because we believe",
            ]
            suffixes = [
                "is essential for success",
                "drives better outcomes",
                "aligns with our goals",
                "creates value",
                "is what users need",
            ]
            answer = (
                f"{random.choice(prefixes)} {current_statement.lower()} {random.choice(suffixes)}"
            )
        else:
            # Bedrock answer
            answer = random.choice(BEDROCK_PATTERNS)

        chain.chain.append(WhyStep(question=question, answer=answer, depth=i + 1))
        current_statement = answer

    chain.bedrock = chain.chain[-1].answer if chain.chain else statement
    return chain


async def _generate_with_llm(statement: str, depth: int, socratic: bool) -> WhyChain | None:
    """
    Generate why chain using K-gent soul (if available).

    Returns None if unavailable.
    """
    try:
        from agents.k.persona import DialogueMode
        from agents.k.soul import KgentSoul

        soul = KgentSoul(auto_llm=True)
        if not soul.has_llm:
            return None

        # Use soul's challenge mode to dig deeper
        chain = WhyChain(original=statement, max_depth=depth)
        current_statement = statement

        for i in range(depth):
            prompt = f"Why: {current_statement}"
            response = await soul.dialogue(prompt, mode=DialogueMode.CHALLENGE)

            question = "Why is that important?"
            answer = response.response[:200] if response.response else "..."

            chain.chain.append(WhyStep(question=question, answer=answer, depth=i + 1))
            current_statement = answer

            # Check for bedrock (answer stops changing meaningfully)
            if len(answer) < 50:
                break

        chain.bedrock = chain.chain[-1].answer if chain.chain else statement
        return chain

    except ImportError:
        return None
    except Exception:
        return None


def _emit_output(
    human: str,
    semantic: "dict[str, Any] | WhyChain",
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = semantic.to_dict() if isinstance(semantic, WhyChain) else semantic
        ctx.emit_semantic(data)


def _print_help() -> None:
    """Print help for why command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --depth <n>         Number of why iterations (default: 5, max: 10)")
    print("  --socratic          Use Socratic questioning style")
    print("  --llm               Use K-gent for deeper analysis (costs tokens)")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kgents why "We need microservices"')
    print('  kgents why --depth 7 "Users want dark mode"')
    print('  kgents why --llm "The tests should always pass"')
    print()
    print("ABOUT THE FIVE WHYS:")
    print("  Originated at Toyota for root cause analysis.")
    print("  Keep asking 'why' until you hit bedrock assumptions.")
    print("  Often reveals surprising foundations for beliefs.")
    print()
    print("PIPELINE USAGE:")
    print("  In REPL: self.soul.why >> world.viz.sparkline")
    print("  (Visualize how deep the inquiry went)")


@handler("why", is_async=False, needs_pty=True, tier=2, description="Recursive why inquiry")
def cmd_why(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Recursive why: Dig to bedrock assumptions.

    AGENTESE Path: self.soul.why

    Keeps asking "why?" until reaching foundational beliefs.

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("why", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args
    use_llm = "--llm" in args
    socratic = "--socratic" in args

    # Parse depth
    depth = 5
    for i, arg in enumerate(args):
        if arg == "--depth" and i + 1 < len(args):
            try:
                depth = int(args[i + 1])
                depth = max(1, min(depth, 10))  # Clamp to 1-10
            except ValueError:
                print("[WHY] Invalid depth value")
                return 1

    # Extract statement (everything not a flag)
    statement_parts = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg.startswith("-"):
            if arg == "--depth":
                skip_next = True
            continue
        statement_parts.append(arg)

    statement = " ".join(statement_parts)

    if not statement:
        print("[WHY] What statement would you like to examine?")
        print('  Example: kgents why "We need microservices"')
        return 1

    # Warn about deep inquiry
    if depth > 7:
        print("[WHY] Deep inquiry (depth > 7) may take time...")

    # Generate why chain
    if use_llm:
        result = asyncio.run(_generate_with_llm(statement, depth, socratic))
        if result is None:
            print("[WHY] LLM unavailable, using templates")
            result = _generate_why_chain(statement, depth)
    else:
        result = _generate_why_chain(statement, depth)

    # Output
    if json_mode:
        import json

        print(json.dumps(result.to_dict(), indent=2))
    else:
        print()
        print(f"\033[1;36mStarting point:\033[0m {statement}")
        print()

        for step in result.chain:
            indent = "  " * step.depth
            print(f"{indent}\033[33mWhy?\033[0m {step.question}")
            print(f"{indent}\033[90m→\033[0m {step.answer[:100]}...")
            print()

        print(f"\033[1;32mBedrock:\033[0m {result.bedrock}")
        print()
        print(f"\033[90mDepth reached: {len(result.chain)}/{result.max_depth}\033[0m")
        print()

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(result.to_dict())

    return 0
