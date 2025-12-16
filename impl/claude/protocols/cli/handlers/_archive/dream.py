"""
Dream Handler: LucidDreamer morning briefing.

DevEx V4 Phase 1 - Foundation Layer.
Glass Terminal Integration: Uses GlassClient with 3-layer fallback.

Usage:
    kgents dream          # Show morning briefing questions
    kgents dream --brief  # Compact briefing format
    kgents dream --run    # Trigger a REM cycle (maintenance)
    kgents dream --answer # Interactive answer mode
    kgents dream --ghost  # Show cached dream state

Example output:
    [DREAMER] AWAKE | Cycles: 12 | Questions: 3

    Morning Briefing:
      1. [HIGH] Memory 'foo' has conflicting embeddings. Heal left or right?
      2. [MED]  Found 5 ghost memories. Auto-heal or review?
      3. [LOW]  Consider adding index on 'timestamp'?

Architecture:
    This handler is "hollowed" - it delegates to GlassClient which implements:
    1. Try gRPC call to Cortex daemon (live data)
    2. On gRPC failure, try local CortexServicer (in-process)
    3. On local failure, read from Ghost cache (last-known-good)
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from protocols.cli.glass import GlassResponse


def cmd_dream(args: list[str]) -> int:
    """
    Display LucidDreamer status and morning briefing.

    This is a "hollowed" handler - it delegates to GlassClient for the
    three-layer fallback strategy (gRPC → local → Ghost cache).
    """
    # Parse args
    run_mode = "--run" in args
    answer_mode = "--answer" in args
    brief_mode = "--brief" in args
    ghost_mode = "--ghost" in args
    help_mode = "--help" in args or "-h" in args

    if help_mode:
        print(__doc__)
        return 0

    # Ghost mode: show cached dream state
    if ghost_mode:
        return _show_ghost_dream_state()

    # Run async dream command
    return asyncio.run(
        _async_dream(
            run_mode=run_mode,
            answer_mode=answer_mode,
            brief_mode=brief_mode,
        )
    )


async def _async_dream(
    run_mode: bool = False,
    answer_mode: bool = False,
    brief_mode: bool = False,
) -> int:
    """
    Async implementation of dream command using GlassClient.

    Uses Invoke RPC with self.dreamer.* paths for dream operations.
    """
    from protocols.cli.glass import GlassResponse, get_glass_client

    client = get_glass_client()

    try:
        if run_mode:
            return await _run_rem_cycle_via_glass(client)
        elif answer_mode:
            return await _answer_questions_via_glass(client)
        else:
            return await _show_briefing_via_glass(client, brief_mode)

    except ConnectionError as e:
        print(f"[DREAMER] X OFFLINE | {e}")
        print("  Run 'kgents infra init' to start the Cortex daemon.")
        return 1

    except Exception as e:
        print(f"[DREAMER] X ERROR | {e}")
        return 1


async def _show_briefing_via_glass(client: Any, brief_mode: bool = False) -> int:
    """
    Show morning briefing via GlassClient.

    Uses Invoke RPC with path: self.dreamer.manifest
    """
    try:
        from protocols.proto.generated import InvokeRequest

        request: Any = InvokeRequest(
            path="self.dreamer.manifest",
            lens="optics.identity",
        )
    except ImportError:
        # Fallback: simple object
        class SimpleRequest:
            def __init__(self, path: str, lens: str):
                self.path = path
                self.lens = lens

        request = SimpleRequest(path="self.dreamer.manifest", lens="optics.identity")

    response: GlassResponse = await client.invoke(
        method="Invoke",
        request=request,
        ghost_key="dream",
        agentese_path="self.dreamer.manifest",
    )

    # Extract dream data from response
    dream_data = _extract_dream_data(response.data)

    if brief_mode:
        _print_brief_dream_status(dream_data, response.is_ghost)
    else:
        _print_full_dream_status(dream_data, response.is_ghost, response.ghost_age)

    return 0


async def _run_rem_cycle_via_glass(client: Any) -> int:
    """
    Run REM cycle via GlassClient.

    Note: Full bi-directional streaming not yet implemented.
    Uses Invoke RPC with path: self.dreamer.rem
    """
    print("[DREAMER] Entering REM cycle...")
    print("  (Ctrl+C to interrupt)")
    print()

    try:
        from protocols.proto.generated import InvokeRequest

        request: Any = InvokeRequest(
            path="self.dreamer.rem",
            lens="optics.identity",
        )
    except ImportError:

        class SimpleRequest:
            def __init__(self, path: str, lens: str):
                self.path = path
                self.lens = lens

        request = SimpleRequest(path="self.dreamer.rem", lens="optics.identity")

    try:
        response = await client.invoke(
            method="Invoke",
            request=request,
            ghost_key="dream_cycle",
            agentese_path="self.dreamer.rem",
        )

        result = _extract_invoke_result(response.data)

        if "error" in result:
            print(f"[DREAMER] ! DEGRADED | {result['error']}")
            return 1

        # Extract cycle results
        phase = result.get("phase_reached", "unknown")
        chunks = result.get("chunks_processed", 0)
        total = result.get("total_chunks", 0)
        questions = result.get("questions_generated", 0)
        interrupted = result.get("interrupted", False)
        errors = result.get("errors", [])

        print(f"[DREAMER] Cycle complete: {phase}")
        print(f"  Chunks processed: {chunks}/{total}")
        print(f"  Questions generated: {questions}")

        if interrupted:
            print(f"  Interrupted: {result.get('interrupt_reason', 'unknown')}")

        if errors:
            print(f"  Errors: {len(errors)}")
            for err in errors[:3]:
                print(f"    - {err}")

        return 0

    except KeyboardInterrupt:
        print("\n[DREAMER] Cycle interrupted by user")
        return 130


async def _answer_questions_via_glass(client: Any) -> int:
    """
    Interactive question answering via GlassClient.

    First fetches questions, then submits answers via Invoke.
    """
    # Get current briefing
    try:
        from protocols.proto.generated import InvokeRequest

        request: Any = InvokeRequest(
            path="self.dreamer.manifest", lens="optics.identity"
        )
    except ImportError:

        class SimpleRequestForManifest:
            def __init__(self, path: str, lens: str):
                self.path = path
                self.lens = lens

        request = SimpleRequestForManifest(
            path="self.dreamer.manifest", lens="optics.identity"
        )

    response = await client.invoke(
        method="Invoke",
        request=request,
        ghost_key="dream",
        agentese_path="self.dreamer.manifest",
    )

    dream_data = _extract_dream_data(response.data)
    questions = dream_data.get("questions", [])
    unanswered = [q for q in questions if not q.get("answered", False)]

    if not unanswered:
        print("[DREAMER] No unanswered questions.")
        return 0

    print("[DREAMER] Morning Briefing - Interactive Mode")
    print("  Type answer or 'skip' to skip, 'quit' to exit")
    print()

    answers = []
    for q in sorted(unanswered, key=lambda x: -x.get("priority", 0)):
        priority = q.get("priority", 0)
        priority_label = _priority_label(priority)
        print(f"[{priority_label}] {q.get('question_text', 'Unknown question')}")

        context = q.get("context")
        if context:
            print(f"  Context: {context}")

        try:
            answer = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if answer.lower() == "quit":
            break
        elif answer.lower() == "skip":
            continue
        else:
            answers.append(
                {
                    "question_id": q.get("question_id"),
                    "answer": answer,
                }
            )
            print("  Recorded.")

        print()

    # Submit answers if any
    if answers:
        try:
            from protocols.proto.generated import InvokeRequest

            answer_request: Any = InvokeRequest(
                path="self.dreamer.answer",
                lens="optics.identity",
                kwargs={"answers": json.dumps(answers)},
            )
        except ImportError:

            class SimpleRequestWithKwargs:
                def __init__(self, path: str, lens: str, kwargs: dict[str, Any]):
                    self.path = path
                    self.lens = lens
                    self.kwargs = kwargs

            answer_request = SimpleRequestWithKwargs(
                path="self.dreamer.answer",
                lens="optics.identity",
                kwargs={"answers": json.dumps(answers)},
            )

        await client.invoke(
            method="Invoke",
            request=answer_request,
            agentese_path="self.dreamer.answer",
        )

    print(f"[DREAMER] Processed {len(answers)} answers.")
    return 0


def _extract_dream_data(data: Any) -> dict[str, Any]:
    """Extract dream data from GlassResponse data."""
    if isinstance(data, dict):
        # Could be from Ghost cache or direct dict
        if "result" in data:
            return data["result"] if isinstance(data["result"], dict) else {}
        return data

    # Handle InvokeResponse
    if hasattr(data, "result_json"):
        try:
            parsed = json.loads(data.result_json)
            return parsed if isinstance(parsed, dict) else {}
        except (json.JSONDecodeError, TypeError):
            pass

    # Protobuf message
    if hasattr(data, "DESCRIPTOR"):
        try:
            from google.protobuf.json_format import MessageToDict

            return cast(
                dict[str, Any], MessageToDict(data, preserving_proto_field_name=True)
            )
        except ImportError:
            pass

    # Dataclass
    if hasattr(data, "to_dict"):
        result = data.to_dict()
        return result if isinstance(result, dict) else {}

    return {"raw": str(data)}


def _extract_invoke_result(data: Any) -> dict[str, Any]:
    """Extract result from InvokeResponse."""
    if isinstance(data, dict):
        if "result" in data:
            return data["result"] if isinstance(data["result"], dict) else data
        return data

    if hasattr(data, "result_json"):
        try:
            return cast(dict[str, Any], json.loads(data.result_json))
        except (json.JSONDecodeError, TypeError):
            pass

    return {"error": "Unable to parse result"}


def _print_brief_dream_status(
    dream_data: dict[str, Any], is_ghost: bool = False
) -> None:
    """Print compact dream status line."""
    prefix = "[GHOST]" if is_ghost else "[DREAMER]"

    phase = dream_data.get("phase", "unknown").upper()
    cycles = dream_data.get("total_cycles", 0)
    questions = len(dream_data.get("questions", []))

    print(f"{prefix} {phase} | Cycles: {cycles} | Questions: {questions}")


def _print_full_dream_status(
    dream_data: dict[str, Any],
    is_ghost: bool = False,
    ghost_age: Any = None,
) -> None:
    """Print full dream status with briefing."""
    prefix = "[GHOST]" if is_ghost else "[DREAMER]"

    phase = dream_data.get("phase", "unknown").upper()
    cycles = dream_data.get("total_cycles", 0)
    questions = dream_data.get("questions", [])

    # Header
    print(f"{prefix} {phase} | Cycles: {cycles} | Questions: {len(questions)}")

    if is_ghost and ghost_age:
        seconds = int(ghost_age.total_seconds())
        print(f"  (Cached data from {seconds}s ago)")

    print()

    # Questions
    if not questions:
        print("  No questions in morning briefing.")
        print("  Run 'kgents dream --run' to trigger maintenance cycle.")
    else:
        print("Morning Briefing:")
        sorted_questions = sorted(questions, key=lambda x: -x.get("priority", 0))
        for i, q in enumerate(sorted_questions, 1):
            priority = q.get("priority", 0)
            priority_label = _priority_label(priority)
            answered = "[ANSWERED]" if q.get("answered", False) else ""
            text = q.get("question_text", "Unknown question")
            print(f"  {i}. [{priority_label}] {text} {answered}")

    print()

    # Last dream info
    last_dream = dream_data.get("last_dream")
    if last_dream:
        print(f"Last dream: {last_dream.get('started_at', 'unknown')}")
        if last_dream.get("interrupted"):
            print(f"  (Interrupted: {last_dream.get('interrupt_reason', 'unknown')})")


def _priority_label(priority: int) -> str:
    """Convert priority number to label."""
    if priority >= 80:
        return "HIGH"
    elif priority >= 50:
        return "MED"
    else:
        return "LOW"


def _show_ghost_dream_state() -> int:
    """Show cached dream state for debugging."""
    try:
        from protocols.cli.glass import GHOST_DIR, GhostCache

        cache = GhostCache()
        data, age, timestamp = cache.read("dream")

        if data is None:
            print("[GHOST] No cached dream state available.")
            print("  Run 'kgents dream' to populate cache.")
            return 0

        # Format age
        age_str = "unknown"
        if age is not None:
            seconds = int(age.total_seconds())
            if seconds < 60:
                age_str = f"{seconds}s"
            elif seconds < 3600:
                age_str = f"{seconds // 60}m"
            else:
                age_str = f"{seconds // 3600}h"

        print(f"[GHOST] Cached dream state from {age_str} ago:")
        print()

        # Display cached data
        dream_data = _extract_dream_data(data)
        _print_full_dream_status(dream_data, is_ghost=True, ghost_age=age)

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to read Ghost cache: {e}")
        return 1
