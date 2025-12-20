"""
WhatIf Handler: Generate alternative approaches to problems.

K-gent WhatIf is a Pro Crown Jewel that uses the K-gent Soul in EXPLORE mode
to generate N alternative approaches to any problem, categorized by reality type.

Usage:
    kgents whatif "I'm stuck on architecture"
    kgents whatif "How should I structure this feature?" --n 5
    kgents whatif "React vs Vue" --json

WhatIf explores the possibility space and returns structured alternatives with:
- title: Short name for the approach
- description: What this approach entails
- reality_type: optimistic/pessimistic/realistic
- confidence: How viable this approach is (0.0-1.0)

This is Pro-only because it requires multiple LLM calls to generate diverse alternatives.
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for whatif command."""
    print(__doc__)
    print()
    print("OPTIONS:")
    print("  --n N               Number of alternatives to generate (default: 3)")
    print("  --json              Output as JSON")
    print("  --help, -h          Show this help")
    print()
    print("EXAMPLES:")
    print('  kgents whatif "How should I handle errors?"')
    print('  kgents whatif "Database design choices" --n 5')
    print('  kgents whatif "Architecture pattern" --json')


def cmd_whatif(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    K-gent WhatIf: Generate alternative approaches.

    Usage:
        kgents whatif "problem description" [--n N] [--json]

    Returns:
        0 on success, 1 on error
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("whatif", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args
    n_alternatives = 3

    # Parse --n flag
    for i, arg in enumerate(args):
        if arg == "--n" and i + 1 < len(args):
            try:
                n_alternatives = int(args[i + 1])
                n_alternatives = max(1, min(10, n_alternatives))  # Clamp 1-10
            except ValueError:
                pass

    # Extract prompt (everything that's not a flag)
    prompt_parts: list[str] = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg in ("--n", "--limit"):
            skip_next = True
            continue
        if arg.startswith("-"):
            continue
        prompt_parts.append(arg)

    if not prompt_parts:
        _emit_output(
            "[WHATIF] X Error: No problem description provided\n"
            'Usage: kgents whatif "problem description"',
            {"error": "No problem description provided"},
            ctx,
        )
        return 1

    prompt = " ".join(prompt_parts)

    # Run async handler
    return asyncio.run(_async_whatif(prompt, n_alternatives, json_mode, ctx))


async def _async_whatif(
    prompt: str,
    n: int,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of whatif command."""
    try:
        from agents.k import DialogueMode, KgentSoul

        # Get soul instance
        soul = _get_soul()

        # Generate alternatives using EXPLORE mode
        alternatives = await _generate_alternatives(soul, prompt, n)

        # Output
        semantic = {
            "command": "whatif",
            "prompt": prompt,
            "n": n,
            "alternatives": alternatives,
        }

        if json_mode:
            _emit_output(json.dumps(semantic, indent=2), semantic, ctx)
        else:
            # Human-friendly output
            lines = [
                f"[WHATIF] {n} alternatives for: {prompt}",
                "",
            ]

            # Group by reality type
            by_type: dict[str, list[dict[str, Any]]] = {
                "optimistic": [],
                "realistic": [],
                "pessimistic": [],
            }

            for alt in alternatives:
                reality_type = alt.get("reality_type", "realistic")
                by_type[reality_type].append(alt)

            # Display grouped
            type_icons = {
                "optimistic": "✨",
                "realistic": "⚖️",
                "pessimistic": "⚠️",
            }

            for reality_type in ["optimistic", "realistic", "pessimistic"]:
                if by_type[reality_type]:
                    icon = type_icons[reality_type]
                    lines.append(f"{icon} {reality_type.upper()}")
                    lines.append("")

                    for alt in by_type[reality_type]:
                        confidence = alt.get("confidence", 0.5)
                        lines.append(f"  • {alt['title']} (confidence: {confidence:.1f})")
                        lines.append(f"    {alt['description']}")
                        lines.append("")

            _emit_output("\n".join(lines), semantic, ctx)

        return 0

    except ImportError as e:
        _emit_output(
            f"[WHATIF] X K-gent module not available: {e}",
            {"error": f"K-gent module not available: {e}"},
            ctx,
        )
        return 1
    except Exception as e:
        _emit_output(
            f"[WHATIF] X Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _generate_alternatives(
    soul: Any,
    prompt: str,
    n: int,
) -> list[dict[str, Any]]:
    """
    Generate N alternative approaches using K-gent EXPLORE mode.

    Uses a specialized prompt to generate diverse alternatives.
    """
    from agents.k import BudgetTier, DialogueMode

    # Craft a prompt that encourages diverse thinking
    whatif_prompt = f"""I'm facing this challenge: {prompt}

Generate {n} alternative approaches to this problem. For each alternative:
1. Give it a short title (3-5 words)
2. Describe the approach in 1-2 sentences
3. Classify it as optimistic/realistic/pessimistic
4. Rate your confidence in its viability (0.0 to 1.0)

Explore the full spectrum - from safe to radical, from minimal to maximal.

Format as JSON:
[
  {{
    "title": "...",
    "description": "...",
    "reality_type": "optimistic|realistic|pessimistic",
    "confidence": 0.8
  }}
]
"""

    # Use EXPLORE mode with DIALOGUE tier
    response = await soul.dialogue(
        whatif_prompt,
        mode=DialogueMode.EXPLORE,
        budget=BudgetTier.DIALOGUE,
    )

    # Parse the response
    alternatives = _parse_alternatives(response.response, n)

    return alternatives


def _parse_alternatives(response: str, n: int) -> list[dict[str, Any]]:
    """
    Parse alternatives from K-gent response.

    Tries to extract JSON array from response. Falls back to text parsing.
    """
    # Try to extract JSON from response
    import re

    # Look for JSON array
    json_match = re.search(r"\[[\s\S]*?\]", response)
    if json_match:
        try:
            alternatives = json.loads(json_match.group(0))
            if isinstance(alternatives, list):
                # Validate and clean
                cleaned = []
                for alt in alternatives[:n]:
                    if isinstance(alt, dict):
                        cleaned.append(
                            {
                                "title": str(alt.get("title", "Unknown approach")),
                                "description": str(alt.get("description", "No description")),
                                "reality_type": str(alt.get("reality_type", "realistic")).lower(),
                                "confidence": float(alt.get("confidence", 0.5)),
                            }
                        )
                return cleaned
        except (json.JSONDecodeError, ValueError):
            pass

    # Fallback: parse as text with numbered items
    alternatives = []
    lines = response.split("\n")

    current_alt: dict[str, Any] | None = None
    for line in lines:
        line = line.strip()

        # Look for numbered items (1., 2., etc.)
        number_match = re.match(r"(\d+)\.\s*(.+)", line)
        if number_match:
            if current_alt:
                alternatives.append(current_alt)

            title = number_match.group(2)
            current_alt = {
                "title": title[:50],  # Truncate
                "description": "",
                "reality_type": "realistic",
                "confidence": 0.5,
            }
        elif current_alt and line and not line.startswith("#"):
            # Accumulate description
            if current_alt["description"]:
                current_alt["description"] += " "
            current_alt["description"] += line

    if current_alt:
        alternatives.append(current_alt)

    # Ensure we have at least one alternative
    if not alternatives:
        alternatives = [
            {
                "title": "Direct approach",
                "description": response[:200],
                "reality_type": "realistic",
                "confidence": 0.5,
            }
        ]

    return alternatives[:n]


# Module-level soul instance (singleton for CLI session)
_soul_instance: Any = None


def _get_soul() -> Any:
    """
    Get or create the K-gent Soul instance.

    Resolution order:
    1. Try to get from lifecycle state (shared across CLI session)
    2. Fall back to module-level singleton (in-memory)
    """
    from agents.k import KgentSoul

    global _soul_instance

    # Try to get from lifecycle state first
    try:
        from protocols.cli.hollow import get_lifecycle_state

        lifecycle_state = get_lifecycle_state()
        if lifecycle_state is not None:
            soul = getattr(lifecycle_state, "soul", None)
            if soul is not None:
                return soul
    except ImportError:
        pass

    # Fall back to module-level singleton
    if _soul_instance is None:
        _soul_instance = KgentSoul()
    return _soul_instance


def set_soul(soul: Any) -> None:
    """Set the module-level soul instance."""
    global _soul_instance
    _soul_instance = soul


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    This is the key integration point with the Reflector Protocol:
    - Human output goes to stdout (for humans)
    - Semantic output goes to FD3 (for agents consuming our output)
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
