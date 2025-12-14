"""
Dialogue commands: reflect, advise, challenge, explore.

These are the core dialogue modes for K-gent Soul.
Each mode offers a different perspective on the user's prompt.
"""

from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING, Any

from protocols.cli.shared import InvocationContext, OutputFormatter, StreamingHandler
from protocols.cli.shared.output import format_dialogue_header

if TYPE_CHECKING:
    pass


async def execute_dialogue(
    mode_name: str,
    prompt: str | None,
    ctx: InvocationContext,
    soul: Any,
) -> int:
    """
    Execute a dialogue command (reflect, advise, challenge, explore).

    Args:
        mode_name: The dialogue mode (reflect, advise, challenge, explore)
        prompt: User prompt (None for interactive mode)
        ctx: Invocation context
        soul: KgentSoul instance

    Returns:
        Exit code (0 for success)
    """
    from agents.k import BudgetTier, DialogueMode

    # Map mode string to DialogueMode
    mode_map = {
        "reflect": DialogueMode.REFLECT,
        "advise": DialogueMode.ADVISE,
        "challenge": DialogueMode.CHALLENGE,
        "explore": DialogueMode.EXPLORE,
    }

    dialogue_mode = mode_map.get(mode_name.lower())
    if dialogue_mode is None:
        output = OutputFormatter(ctx)
        output.emit_error(f"Unknown mode: {mode_name}")
        return 1

    # Map budget string to BudgetTier
    budget_map = {
        "whisper": BudgetTier.WHISPER,
        "dialogue": BudgetTier.DIALOGUE,
        "deep": BudgetTier.DEEP,
    }
    budget_tier = budget_map.get(ctx.budget, BudgetTier.DIALOGUE)

    # If no prompt but in pipe mode, read from stdin
    if prompt is None and ctx.pipe_mode:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        if not prompt:
            import json

            print(
                json.dumps({"type": "error", "message": "No input on stdin"}),
                flush=True,
            )
            return 1

    # If no prompt, enter interactive mode
    if prompt is None:
        return await _handle_interactive(soul, dialogue_mode, budget_tier, ctx)

    # Single dialogue turn (with streaming if --stream or --pipe flag)
    if ctx.is_streaming:
        return await _handle_streaming(soul, dialogue_mode, prompt, budget_tier, ctx)

    return await _handle_single(soul, dialogue_mode, prompt, budget_tier, ctx)


async def _handle_single(
    soul: Any,
    mode: Any,  # DialogueMode
    prompt: str,
    budget: Any,  # BudgetTier
    ctx: InvocationContext,
) -> int:
    """Handle a single dialogue turn (non-streaming)."""
    output = OutputFormatter(ctx)
    response = await soul.dialogue(prompt, mode=mode, budget=budget)

    semantic = {
        "mode": response.mode.value,
        "response": response.response,
        "budget_tier": response.budget_tier.value,
        "tokens_used": response.tokens_used,
        "was_template": response.was_template,
        "referenced_preferences": response.referenced_preferences,
        "referenced_patterns": response.referenced_patterns,
    }

    if ctx.json_mode:
        import json

        output.emit(json.dumps(semantic, indent=2), semantic)
    else:
        # Human-friendly output
        header = format_dialogue_header(response.mode.value)
        lines = [header, "", response.response]

        if response.referenced_preferences:
            lines.append("")
            lines.append(
                f"  Principles: {', '.join(response.referenced_preferences[:2])}"
            )

        if response.tokens_used > 0 and not response.was_template:
            lines.append(f"  [{response.tokens_used} tokens]")

        output.emit("\n".join(lines), semantic)

    return 0


async def _handle_streaming(
    soul: Any,
    mode: Any,  # DialogueMode
    prompt: str,
    budget: Any,  # BudgetTier
    ctx: InvocationContext,
) -> int:
    """Handle streaming dialogue."""
    handler = StreamingHandler(ctx)
    result = await handler.stream_dialogue(soul, mode, prompt, budget)
    return 0 if not result.cancelled else 130  # 130 = SIGINT


async def _handle_interactive(
    soul: Any,
    mode: Any,  # DialogueMode
    budget: Any,  # BudgetTier
    ctx: InvocationContext,
) -> int:
    """Handle interactive dialogue mode."""
    output = OutputFormatter(ctx)

    # Enter mode and show a starter
    entry_message = soul.enter_mode(mode)
    starter = soul.get_starter(mode)

    semantic = {
        "mode": mode.value,
        "entry_message": entry_message,
        "starter": starter,
    }

    if ctx.json_mode:
        import json

        output.emit(json.dumps(semantic, indent=2), semantic)
    else:
        lines = [
            f"[SOUL] {entry_message}",
            "",
            f'Try: "{starter}"',
            "",
            "Enter your prompt (or 'q' to quit):",
        ]
        output.emit("\n".join(lines), semantic)

        # Interactive loop
        try:
            while True:
                try:
                    user_input = input(f"\n[{mode.value}] > ").strip()
                except (KeyboardInterrupt, EOFError):
                    print("\n[SOUL] Goodbye.")
                    return 0

                if user_input.lower() in ("q", "quit", "exit", "bye"):
                    print("[SOUL] Until next time. The patterns will be here.")
                    return 0

                if not user_input:
                    continue

                # Process dialogue
                response = await soul.dialogue(user_input, mode=mode, budget=budget)
                print(f"\n{response.response}")

                if response.referenced_preferences:
                    print(
                        f"\n  Principles: {', '.join(response.referenced_preferences[:2])}"
                    )

        except Exception as e:
            print(f"[SOUL] Error: {e}")
            return 1

    return 0
