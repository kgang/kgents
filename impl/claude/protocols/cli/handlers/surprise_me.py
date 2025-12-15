"""
Surprise Me Handler: Random creative prompt generator.

Draws from the Accursed Share (void.entropy) to generate unexpected
prompts for creative exploration.

Usage:
    kgents surprise-me                # Random prompt
    kgents surprise-me --domain code  # Domain-specific
    kgents surprise-me --weird        # Extra weird

AGENTESE Path: void.serendipity.prompt
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# =============================================================================
# Creative Prompts by Domain
# =============================================================================

PROMPTS = {
    "general": [
        "What would this look like if time ran backwards?",
        "How would an alien civilization solve this?",
        "What if the constraints became the features?",
        "What would a child do with this?",
        "How would this work at 1000x scale?",
        "What's the opposite of what you're trying to do?",
        "What would make this beautiful?",
        "If this were a dance, what kind would it be?",
        "What would a historian say about this in 100 years?",
        "What would you do if failure was impossible?",
        "How would nature solve this problem?",
        "What would this look like as a game?",
        "What if you had to explain this to your grandmother?",
        "What's the most elegant version of this?",
        "What would you do with infinite resources?",
    ],
    "code": [
        "What if every function had to fit in a tweet?",
        "How would you build this without any conditionals?",
        "What if state was forbidden?",
        "How would this work in a distributed system of millions?",
        "What if the compiler could write code too?",
        "How would you test this with only one test?",
        "What if errors were features?",
        "How would biological systems implement this?",
        "What if you had to make this work offline?",
        "What would this look like in 10 years?",
    ],
    "design": [
        "What if this had no visual hierarchy?",
        "How would a blind person experience this?",
        "What if every element was alive?",
        "How would you design this for zero attention span?",
        "What if sound was the primary medium?",
        "How would this work in zero gravity?",
        "What if the design changed based on emotion?",
        "How would you make this feel warm?",
        "What if every interaction was a surprise?",
        "How would you design this for a 5-year-old?",
    ],
    "writing": [
        "What if you could only use questions?",
        "How would you write this as a recipe?",
        "What if every sentence had to rhyme?",
        "How would you tell this story backwards?",
        "What if you wrote from the antagonist's perspective?",
        "How would you write this with no verbs?",
        "What if silence was the protagonist?",
        "How would you write this as a love letter?",
        "What if the reader was the main character?",
        "How would you compress this to haiku?",
    ],
    "weird": [
        "What if gravity only affected emotions?",
        "How would this work if consciousness was liquid?",
        "What if memories could be tasted?",
        "How would you implement this using only dreams?",
        "What if time was a texture you could feel?",
        "How would this look painted by a volcano?",
        "What if silence had mass?",
        "How would you build this from forgotten things?",
        "What if the solution was asking the right wrong question?",
        "How would this work if causality was optional?",
        "What if you could only use tools that didn't exist yet?",
        "How would a ghost approach this problem?",
    ],
}

DOMAINS = list(PROMPTS.keys())


@dataclass
class CreativePrompt:
    """A creative prompt from the Accursed Share."""

    prompt: str
    domain: str
    weirdness: float  # 0.0 = normal, 1.0 = very weird
    entropy_spent: float

    def to_dict(self) -> "dict[str, Any]":
        """Convert to JSON-serializable dict."""
        return {
            "prompt": self.prompt,
            "domain": self.domain,
            "weirdness": self.weirdness,
            "entropy_spent": self.entropy_spent,
        }


def _select_prompt(domain: str = "general", weird: bool = False) -> CreativePrompt:
    """
    Select a random prompt, drawing from entropy.
    """
    # Calculate weirdness
    weirdness = 0.3 if not weird else 0.8

    # Select domain
    if weird:
        domain = "weird"
    elif domain not in PROMPTS:
        domain = "general"

    # Mix in weird prompts based on weirdness
    pool = list(PROMPTS[domain])
    if weird and domain != "weird":
        pool.extend(PROMPTS["weird"][:5])  # Add some weird ones

    # Select prompt
    prompt_text = random.choice(pool)

    # Calculate entropy spent (symbolic)
    entropy_spent = random.uniform(0.01, 0.03)

    return CreativePrompt(
        prompt=prompt_text,
        domain=domain,
        weirdness=weirdness,
        entropy_spent=entropy_spent,
    )


def _emit_output(
    human: str,
    semantic: "dict[str, Any] | CreativePrompt",
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = semantic.to_dict() if isinstance(semantic, CreativePrompt) else semantic
        ctx.emit_semantic(data)


def _print_help() -> None:
    """Print help for surprise-me command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --domain <type>     Domain: general, code, design, writing, weird")
    print("  --weird             Extra weird prompts (from the deep void)")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print("  kgents surprise-me               # Random prompt")
    print("  kgents surprise-me --domain code # Code-focused")
    print("  kgents surprise-me --weird       # From the deep void")
    print()
    print("ABOUT THE ACCURSED SHARE:")
    print("  Surplus must be spent. This command draws from void.entropy")
    print("  to generate unexpected creative prompts.")
    print()
    print("PIPELINE USAGE:")
    print("  In REPL: void.serendipity.prompt >> concept.creativity.expand")
    print("  (Generate random seed, then expand it)")


def cmd_surprise_me(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Random creative prompt generator.

    AGENTESE Path: void.serendipity.prompt

    Draws from entropy to generate unexpected prompts for exploration.

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("surprise-me", args)
        except ImportError:
            pass

    # Parse flags
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    json_mode = "--json" in args
    weird_mode = "--weird" in args

    # Parse domain
    domain = "general"
    for i, arg in enumerate(args):
        if arg == "--domain" and i + 1 < len(args):
            domain = args[i + 1].lower()
            if domain not in DOMAINS:
                print(f"[SURPRISE-ME] Unknown domain: {domain}")
                print(f"  Available: {', '.join(DOMAINS)}")
                return 1

    # Generate prompt
    result = _select_prompt(domain=domain, weird=weird_mode)

    # Output
    if json_mode:
        import json

        print(json.dumps(result.to_dict(), indent=2))
    else:
        # Beautiful output
        print()
        emoji = "🎲" if not weird_mode else "🌀"
        print(f"  {emoji} \033[1;35m{result.prompt}\033[0m")
        print()
        print(
            f"\033[90m  Domain: {result.domain} | Entropy spent: {result.entropy_spent:.3f}\033[0m"
        )
        print()

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(result.to_dict())

    return 0
