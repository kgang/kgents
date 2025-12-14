"""
Dialogue commands for A-gent.

Handles direct dialogue with dialogue-capable agents like KgentSoul.
Supports both single-turn and REPL modes.
"""

from __future__ import annotations

import importlib
import sys
from typing import TYPE_CHECKING, Any

from . import DIALOGUE_AGENTS, _emit_output

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def resolve_dialogue_agent(name: str) -> Any | None:
    """
    Resolve agent name to a dialogue-capable agent instance.

    Returns:
        Instantiated agent if found and dialogue-capable, None otherwise.
    """
    if name not in DIALOGUE_AGENTS:
        return None

    try:
        module_path, class_name = DIALOGUE_AGENTS[name].rsplit(":", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)

        # Instantiate: SoulSession needs no args, KgentSoul needs no args
        if class_name == "SoulSession":
            # SoulSession.get() returns singleton
            return cls.get()
        else:
            return cls()
    except (ImportError, AttributeError) as e:
        # Graceful degradation: log but don't crash
        print(f"[A] Warning: Could not load {name}: {e}", file=sys.stderr)
        return None


async def execute_dialogue(
    agent_name: str,
    prompt: str | None,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle direct dialogue with an agent.

    If prompt is None, enters REPL mode.
    Otherwise, performs a single dialogue turn.
    """
    agent = resolve_dialogue_agent(agent_name)
    if agent is None:
        _emit_output(
            f"[A] Unknown dialogue agent: {agent_name}\n"
            f"    Available: {', '.join(DIALOGUE_AGENTS.keys())}",
            {"error": "unknown_agent", "available": list(DIALOGUE_AGENTS.keys())},
            ctx,
        )
        return 1

    if prompt is None:
        # Enter REPL mode
        return await _execute_repl(agent, agent_name, json_mode, ctx)

    # Single dialogue turn
    try:
        if hasattr(agent, "dialogue"):
            output = await agent.dialogue(prompt)
            response = output.response if hasattr(output, "response") else str(output)
            mode = getattr(output, "mode", None)
            mode_str = mode.value if mode else "dialogue"
        else:
            # Fallback to invoke() for generic agents
            output = await agent.invoke(prompt)
            response = str(output)
            mode_str = "invoke"

        if json_mode:
            import json

            result = {
                "agent": agent_name,
                "input": prompt,
                "response": response,
                "mode": mode_str,
            }
            _emit_output(json.dumps(result, indent=2), result, ctx)
        else:
            _emit_output(response, {"agent": agent_name, "response": response}, ctx)

        return 0

    except Exception as e:
        _emit_output(
            f"[A] Dialogue error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _execute_repl(
    agent: Any,
    agent_name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """
    Interactive REPL for dialogue with an agent.

    Commands:
        q, quit, exit  - Exit REPL
        /mode <mode>   - Change dialogue mode (reflect, advise, challenge, explore)
        /status        - Show agent status
    """
    _emit_output(
        f"[A] {agent_name} REPL\n"
        f"    Commands: q (quit), /mode <mode>, /status\n"
        f"    Type your message and press Enter.",
        {"repl": True, "agent": agent_name},
        ctx,
    )

    current_mode = None  # Will use agent's default

    while True:
        try:
            user_input = input(f"[{agent_name}] > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n[A] Goodbye.")
            return 0

        if not user_input:
            continue

        # Handle REPL commands
        if user_input.lower() in ("q", "quit", "exit"):
            print("[A] Goodbye.")
            return 0

        if user_input.startswith("/mode "):
            mode_arg = user_input[6:].strip().lower()
            try:
                from agents.k.persona import DialogueMode

                current_mode = DialogueMode(mode_arg)
                print(f"[A] Mode set to: {current_mode.value}")
            except (ImportError, ValueError):
                print(f"[A] Unknown mode: {mode_arg}")
                print("    Available: reflect, advise, challenge, explore")
            continue

        if user_input == "/status":
            if hasattr(agent, "_state"):
                state = agent._state
                print(f"[A] Agent: {agent_name}")
                if hasattr(state, "active_mode"):
                    print(f"    Mode: {state.active_mode.value}")
                if hasattr(state, "turns"):
                    print(f"    Turns: {state.turns}")
            else:
                print(f"[A] Agent: {agent_name} (no state available)")
            continue

        # Dialogue turn
        try:
            if hasattr(agent, "dialogue"):
                if current_mode:
                    output = await agent.dialogue(user_input, mode=current_mode)
                else:
                    output = await agent.dialogue(user_input)
                response = (
                    output.response if hasattr(output, "response") else str(output)
                )
            else:
                output = await agent.invoke(user_input)
                response = str(output)

            if json_mode:
                import json

                print(json.dumps({"response": response}, indent=2))
            else:
                print(response)
                print()

        except Exception as e:
            print(f"[A] Error: {e}")

    return 0
