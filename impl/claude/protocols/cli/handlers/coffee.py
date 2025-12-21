# mypy: ignore-errors
"""
Coffee Handler: Rich CLI for the Morning Coffee liminal transition protocol.

Morning Coffee — Liminal transition protocol from rest to work.

The handler provides both:
1. Rich formatted output (default) — beautiful boxes and emoji
2. JSON output (--json flag) — for programmatic access

AGENTESE Path Mapping:
    kg coffee               -> time.coffee.manifest
    kg coffee --quick       -> time.coffee.garden + time.coffee.menu
    kg coffee garden        -> time.coffee.garden
    kg coffee weather       -> time.coffee.weather
    kg coffee menu          -> time.coffee.menu
    kg coffee capture       -> time.coffee.capture (interactive)
    kg coffee begin <item>  -> time.coffee.begin + transition
    kg coffee history       -> time.coffee.history

"The musician doesn't start with the hardest passage.
 She tunes, breathes, plays a scale."

See: spec/services/morning-coffee.md, docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# Path Routing
# =============================================================================


COFFEE_SUBCOMMAND_TO_PATH = {
    # Movements
    "garden": "time.coffee.garden",
    "weather": "time.coffee.weather",
    "menu": "time.coffee.menu",
    "capture": "time.coffee.capture",
    "begin": "time.coffee.begin",
    # History
    "history": "time.coffee.history",
    # Status
    "status": "time.coffee.manifest",
}

DEFAULT_PATH = "time.coffee.manifest"


# =============================================================================
# Async Helpers
# =============================================================================


def _run_async(coro: Any) -> Any:
    """Run an async coroutine synchronously."""
    try:
        asyncio.get_running_loop()
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)


# =============================================================================
# Service Access
# =============================================================================


def _get_service() -> Any:
    """Get the CoffeeService instance."""
    from services.liminal.coffee import get_coffee_service

    return get_coffee_service()


# =============================================================================
# Main Entry Point
# =============================================================================


def cmd_coffee(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Morning Coffee: Liminal transition from rest to work.

    This handler provides rich formatting for the ritual.
    For JSON output, use --json flag.
    """
    # Parse flags
    json_output = "--json" in args
    trace_mode = "--trace" in args

    # Clean args
    clean_args = [a for a in args if a not in ("--json", "--trace")]

    # Parse help flag
    if "--help" in clean_args or "-h" in clean_args:
        _print_help()
        return 0

    # Parse --quick flag (garden + menu shortcut)
    if "--quick" in clean_args:
        return _run_quick(json_output, trace_mode)

    # Parse --full flag (interactive ritual)
    if "--full" in clean_args:
        return cmd_coffee_full(clean_args, ctx)

    # Parse subcommand
    subcommand = _parse_subcommand(clean_args)

    if trace_mode:
        path = COFFEE_SUBCOMMAND_TO_PATH.get(subcommand, DEFAULT_PATH)
        print(f"[TRACE] Invoking: {path}")

    # Route to appropriate handler
    match subcommand:
        case "garden":
            return _run_garden(json_output)
        case "weather":
            return _run_weather(json_output)
        case "menu":
            return _run_menu(json_output)
        case "capture":
            return _run_capture(clean_args, json_output)
        case "begin":
            return _run_begin(clean_args, json_output)
        case "history":
            return _run_history(clean_args, json_output)
        case _:
            return _run_manifest(json_output)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "status"


# =============================================================================
# Movement Handlers
# =============================================================================


def _run_manifest(json_output: bool) -> int:
    """Show ritual manifest/status."""
    service = _get_service()
    data = service.manifest()

    if json_output:
        print(json.dumps(data, indent=2, default=str))
    else:
        from services.liminal.coffee.cli_formatting import format_manifest

        print(format_manifest(data))

    return 0


def _run_garden(json_output: bool) -> int:
    """Show garden view."""
    service = _get_service()

    async def _garden():
        return await service.garden()

    view = _run_async(_garden())
    data = view.to_dict()

    if json_output:
        print(json.dumps(data, indent=2, default=str))
    else:
        from services.liminal.coffee.cli_formatting import format_garden_view

        print(format_garden_view(data))

    return 0


def _run_weather(json_output: bool) -> int:
    """Show conceptual weather."""
    service = _get_service()

    async def _weather():
        return await service.weather()

    weather = _run_async(_weather())
    data = weather.to_dict()

    if json_output:
        print(json.dumps(data, indent=2, default=str))
    else:
        from services.liminal.coffee.cli_formatting import format_weather

        print(format_weather(data))

    return 0


def _run_menu(json_output: bool) -> int:
    """Show challenge menu."""
    service = _get_service()

    async def _menu():
        return await service.menu()

    menu = _run_async(_menu())
    data = menu.to_dict()

    if json_output:
        print(json.dumps(data, indent=2, default=str))
    else:
        from services.liminal.coffee.cli_formatting import format_menu

        print(format_menu(data))

    return 0


def _run_capture(args: list[str], json_output: bool) -> int:
    """Run interactive voice capture or accept inline args."""
    from datetime import date

    from services.liminal.coffee import MorningVoice
    from services.liminal.coffee.capture import CAPTURE_QUESTIONS

    service = _get_service()

    # Check for inline capture (non-interactive)
    # kg coffee capture --success "Ship the feature"
    success_idx = None
    for i, arg in enumerate(args):
        if arg == "--success" and i + 1 < len(args):
            success_idx = i + 1
            break

    if success_idx is not None:
        # Non-interactive capture
        success_criteria = args[success_idx]
        voice = MorningVoice(
            captured_date=date.today(),
            non_code_thought=None,
            eye_catch=None,
            success_criteria=success_criteria,
            raw_feeling=None,
            chosen_challenge=None,
        )

        async def _save():
            return await service.save_capture(voice)

        saved_path = _run_async(_save())

        if json_output:
            print(
                json.dumps(
                    {
                        "captured": True,
                        "voice": voice.to_dict(),
                        "saved_path": str(saved_path),
                    },
                    indent=2,
                    default=str,
                )
            )
        else:
            from services.liminal.coffee.cli_formatting import format_captured_voice

            print(
                format_captured_voice(
                    {
                        "voice": voice.to_dict(),
                        "saved_path": str(saved_path),
                    }
                )
            )
        return 0

    # Interactive capture
    if json_output:
        # Can't do interactive in JSON mode, return questions
        print(
            json.dumps(
                {
                    "questions": [
                        {
                            "key": q.key,
                            "prompt": q.prompt,
                            "placeholder": q.placeholder,
                            "required": q.required,
                        }
                        for q in CAPTURE_QUESTIONS
                    ],
                },
                indent=2,
            )
        )
        return 0

    # Interactive flow
    from services.liminal.coffee.cli_formatting import format_capture_questions

    print(format_capture_questions())
    print()

    answers: dict[str, str | None] = {}

    for q in CAPTURE_QUESTIONS:
        try:
            response = input(f"  {q.key}> ").strip()
            answers[q.key] = response if response else None
        except (KeyboardInterrupt, EOFError):
            print("\n\nCapture cancelled. The ritual honors your choice.")
            return 0

    # Build and save voice
    voice = MorningVoice(
        captured_date=date.today(),
        non_code_thought=answers.get("non_code_thought"),
        eye_catch=answers.get("eye_catch"),
        success_criteria=answers.get("success_criteria"),
        raw_feeling=answers.get("raw_feeling"),
        chosen_challenge=None,
    )

    async def _save():
        return await service.save_capture(voice)

    saved_path = _run_async(_save())

    from services.liminal.coffee.cli_formatting import format_captured_voice

    print()
    print(
        format_captured_voice(
            {
                "voice": voice.to_dict(),
                "saved_path": str(saved_path),
            }
        )
    )

    return 0


def _run_begin(args: list[str], json_output: bool) -> int:
    """
    Full morning start flow: Circadian context → Intent capture → Hydration → Ready.

    Phase 1.3 of Metabolic Development Protocol.

    Usage:
        kg coffee begin                # Full morning start flow
        kg coffee begin "ASHC L0"      # Skip capture, transition with chosen item
    """
    from datetime import date

    from services.liminal.coffee import (
        CircadianResonance,
        MorningVoice,
        get_circadian_resonance,
        load_recent_voices,
    )
    from services.liminal.coffee.cli_formatting import (
        format_circadian_context,
        format_hydration_context,
        format_transition,
    )
    from services.living_docs.hydrator import hydrate_context

    service = _get_service()
    resonance = get_circadian_resonance()

    # Check for selected item text (skip capture mode)
    item_text = None
    for arg in args:
        if not arg.startswith("-") and arg != "begin":
            item_text = arg
            break

    # 1. Load voice history and get circadian context
    voices = load_recent_voices(limit=30, store_path=service.voice_store_path)
    circadian_ctx = resonance.get_context(voices)

    if json_output:
        # JSON mode: return structured data
        result: dict[str, Any] = {
            "circadian": circadian_ctx.to_dict(),
            "chosen_item": {"label": item_text, "source": "manual"} if item_text else None,
            "hydration": None,
            "transitioned": True,
        }

        # If no chosen item, capture intent
        if not item_text:
            result["awaiting_intent"] = True
            result["prompt"] = "What brings you here today?"

        print(json.dumps(result, indent=2, default=str))
        return 0

    # 2. Display greeting with circadian context
    print("\n☕ Good morning\n")

    # Show circadian context if there's history
    if circadian_ctx.resonances or circadian_ctx.patterns or circadian_ctx.serendipity:
        print(format_circadian_context(circadian_ctx.to_dict()))
        print()

    # 3. If item_text provided, skip capture and transition
    if item_text:
        # Hydrate context for the provided intent
        hydration = hydrate_context(item_text)
        print(format_hydration_context(hydration.to_dict()))
        print()
        print(format_transition({"label": item_text, "source": "manual"}))
        return 0

    # 4. Interactive: Capture intent
    print("[What brings you here today?]")
    try:
        intent = input("> ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\n☕ The morning is still yours.\n")
        return 0

    if not intent:
        print("\n☀️ Ready. The morning is yours.\n")
        return 0

    # 5. Hydrate context based on intent
    print("\n✨ Intent captured. Hydrating context...\n")
    hydration = hydrate_context(intent)
    print(format_hydration_context(hydration.to_dict()))
    print()

    # 6. Optional: Save as today's voice
    print("Save this as today's voice? (Y/n)")
    try:
        save_choice = input("> ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        save_choice = "n"

    if save_choice != "n":
        voice = MorningVoice(
            captured_date=date.today(),
            non_code_thought=None,
            eye_catch=None,
            success_criteria=intent,
            raw_feeling=None,
            chosen_challenge=None,
        )

        async def _save():
            return await service.save_capture(voice)

        _run_async(_save())
        print("   Voice saved.\n")

    # 7. Transition
    print(format_transition({"label": intent, "source": "morning_start"}))
    print("\nContext compiled. Good morning, Kent.\n")

    return 0


def _run_history(args: list[str], json_output: bool) -> int:
    """Show voice capture history."""
    from datetime import date

    service = _get_service()

    # Parse --limit
    limit = 7
    for i, arg in enumerate(args):
        if arg == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass

    # Parse --date
    specific_date = None
    for i, arg in enumerate(args):
        if arg == "--date" and i + 1 < len(args):
            try:
                specific_date = date.fromisoformat(args[i + 1])
            except ValueError:
                pass

    if specific_date:
        voice = service.get_voice(specific_date)
        voices = [voice] if voice else []
    else:
        voices = service.get_recent_voices(limit=limit)

    # Extract patterns
    patterns = None
    if len(voices) >= 3:
        from services.liminal.coffee.capture import extract_voice_patterns

        patterns = extract_voice_patterns(voices)

    data = {
        "voices": [v.to_dict() for v in voices],
        "patterns": patterns,
    }

    if json_output:
        print(json.dumps(data, indent=2, default=str))
    else:
        from services.liminal.coffee.cli_formatting import format_history

        print(format_history(data))

    return 0


# =============================================================================
# Quick Mode (Garden + Menu)
# =============================================================================


def _run_quick(json_output: bool, trace_mode: bool) -> int:
    """Run quick ritual: garden + menu only."""
    service = _get_service()

    async def _quick():
        return await service.quick()

    garden, menu = _run_async(_quick())

    if trace_mode:
        print("[TRACE] time.coffee.garden + time.coffee.menu")

    if json_output:
        print(
            json.dumps(
                {
                    "garden": garden.to_dict(),
                    "menu": menu.to_dict(),
                },
                indent=2,
                default=str,
            )
        )
    else:
        from services.liminal.coffee.cli_formatting import (
            format_garden_view,
            format_menu,
        )

        print("☕ Morning Coffee — Quick View\n")
        print(format_garden_view(garden.to_dict()))
        print()
        print(format_menu(menu.to_dict()))

    return 0


# =============================================================================
# Full Ritual (Interactive)
# =============================================================================


def cmd_coffee_full(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Run the full interactive ritual.

    This is the "ritual as interface" mode — the complete experience.

    Usage: kg coffee --full
    """
    from services.liminal.coffee.cli_formatting import (
        format_garden_view,
        format_menu,
        format_movement_separator,
        format_ritual_start,
        format_transition,
        format_weather,
    )

    service = _get_service()

    print(format_ritual_start())

    try:
        # Movement 1: Garden
        print(format_movement_separator("Movement 1: Garden View"))

        async def _garden():
            return await service.garden()

        garden = _run_async(_garden())
        print(format_garden_view(garden.to_dict()))

        input("\nPress Enter to continue (or Ctrl+C to exit)...")

        # Movement 2: Weather
        print(format_movement_separator("Movement 2: Conceptual Weather"))

        async def _weather():
            return await service.weather()

        weather = _run_async(_weather())
        print(format_weather(weather.to_dict()))

        input("\nPress Enter to continue (or Ctrl+C to exit)...")

        # Movement 3: Menu
        print(format_movement_separator("Movement 3: Today's Menu"))

        async def _menu():
            return await service.menu(garden_view=garden, weather=weather)

        menu = _run_async(_menu())
        print(format_menu(menu.to_dict()))

        # Ask for selection
        print("\nEnter number, 's' for serendipitous, or press Enter to skip:")
        selection = input("> ").strip()

        chosen_item = None
        if selection:
            if selection.lower() == "s":
                chosen_item = {"label": "Following curiosity", "source": "serendipitous"}
            elif selection.isdigit():
                # Find the item by number
                item_num = 1
                for level in ["gentle", "focused", "intense"]:
                    for item in menu.to_dict().get(level, []):
                        if str(item_num) == selection:
                            chosen_item = item
                            break
                        item_num += 1
                    if chosen_item:
                        break

        # Movement 4: Capture (optional)
        print(format_movement_separator("Movement 4: Fresh Capture"))
        print("Record what's on your mind? (y/n)")
        do_capture = input("> ").strip().lower()

        if do_capture == "y":
            _run_capture([], json_output=False)

        # Transition
        print()
        print(format_transition(chosen_item))

    except KeyboardInterrupt:
        print("\n\n☕ Ritual paused. The morning is still yours.\n")
        return 0

    return 0


# =============================================================================
# Help
# =============================================================================


def _print_help() -> None:
    """Print coffee command help."""
    help_text = """
kg coffee - Morning Coffee (Liminal Transition Protocol)

"The musician doesn't start with the hardest passage.
 She tunes, breathes, plays a scale."

MOVEMENTS:
  kg coffee                       Show ritual status
  kg coffee garden                Movement 1: What grew while I slept?
  kg coffee weather               Movement 2: What's shifting in the atmosphere?
  kg coffee menu                  Movement 3: What suits my taste this morning?
  kg coffee capture               Movement 4: Fresh voice capture
  kg coffee begin [item]          Complete ritual, transition to work

QUICK MODE:
  kg coffee --quick               Garden + Menu only (skip Weather/Capture)

FULL RITUAL:
  kg coffee --full                Interactive guided ritual (all 4 movements)

VOICE CAPTURE:
  kg coffee capture               Interactive voice capture
  kg coffee capture --success "text"   Quick capture with success criteria

HISTORY:
  kg coffee history               View past voice captures
  kg coffee history --limit 7     Limit number of results
  kg coffee history --date 2025-01-15   View specific date

OPTIONS:
  --help, -h                      Show this help message
  --json                          Output as JSON
  --trace                         Show AGENTESE path being invoked

AGENTESE PATHS:
  time.coffee.manifest            Ritual status
  time.coffee.garden              Garden View (Movement 1)
  time.coffee.weather             Conceptual Weather (Movement 2)
  time.coffee.menu                Challenge Menu (Movement 3)
  time.coffee.capture             Voice Capture (Movement 4)
  time.coffee.begin               Transition to work
  time.coffee.history             Past voice captures

EXAMPLES:
  $ kg coffee                     # Check ritual status
  $ kg coffee --quick             # Fast start: garden + menu
  $ kg coffee garden              # Just view yesterday's changes
  $ kg coffee capture             # Record morning voice
  $ kg coffee begin "ASHC L0"     # Transition with chosen work

The ritual serves the human, not vice versa. Exit anytime.
"""
    print(help_text.strip())


# =============================================================================
# Exports
# =============================================================================


__all__ = ["cmd_coffee", "cmd_coffee_full"]
