"""
Dream Handler: LucidDreamer morning briefing.

DevEx V4 Phase 1 - Foundation Layer.

Usage:
    kgents dream          # Show morning briefing questions
    kgents dream --run    # Trigger a REM cycle (maintenance)
    kgents dream --answer # Interactive answer mode

Example output:
    [DREAMER] AWAKE | Cycles: 12 | Questions: 3

    Morning Briefing:
      1. [HIGH] Memory 'foo' has conflicting embeddings. Heal left or right?
      2. [MED]  Found 5 ghost memories. Auto-heal or review?
      3. [LOW]  Consider adding index on 'timestamp'?
"""

from __future__ import annotations

import asyncio
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def cmd_dream(args: list[str]) -> int:
    """
    Display LucidDreamer status and morning briefing.

    The Dreamer runs maintenance during "sleep" and accumulates
    questions for the morning briefing.
    """
    # Parse args
    run_mode = "--run" in args
    answer_mode = "--answer" in args
    help_mode = "--help" in args or "-h" in args

    if help_mode:
        print(__doc__)
        return 0

    # Get lifecycle state
    from protocols.cli.hollow import get_lifecycle_state

    state = get_lifecycle_state()

    if state is None:
        print("[DREAMER] ? DB-LESS | No dreaming without persistence")
        print("  Run 'kgents init' to initialize workspace.")
        return 0

    try:
        dreamer = _get_or_create_dreamer(state)

        if dreamer is None:
            print("[DREAMER] ? NOT INITIALIZED | Components missing")
            return 0

        if run_mode:
            return asyncio.run(_run_rem_cycle(dreamer))
        elif answer_mode:
            return _answer_questions(dreamer)
        else:
            return _show_briefing(dreamer)

    except ImportError as e:
        print(f"[DREAMER] ! DEGRADED | Missing component: {e}")
        return 1
    except Exception as e:
        print(f"[DREAMER] X ERROR | {e}")
        return 1


def _get_or_create_dreamer(state):
    """Get or create LucidDreamer from lifecycle state."""
    # Check if dreamer exists on state
    if hasattr(state, "dreamer") and state.dreamer is not None:
        return state.dreamer

    # Try to create from components
    synapse = getattr(state, "synapse", None)
    hippocampus = getattr(state, "hippocampus", None)

    if synapse is None or hippocampus is None:
        return None

    from protocols.cli.instance_db.dreamer import create_lucid_dreamer

    return create_lucid_dreamer(
        synapse=synapse,
        hippocampus=hippocampus,
        cortex=getattr(state, "cortex", None),
    )


def _show_briefing(dreamer) -> int:
    """Show morning briefing status."""
    from protocols.cli.instance_db.dreamer import DreamPhase

    # Header
    phase = dreamer.phase.value.upper()
    cycles = dreamer.dream_cycles_total
    questions = len(dreamer.morning_briefing)

    print(f"[DREAMER] {phase} | Cycles: {cycles} | Questions: {questions}")
    print()

    # Questions
    if not dreamer.morning_briefing:
        print("  No questions in morning briefing.")
        print("  Run 'kgents dream --run' to trigger maintenance cycle.")
    else:
        print("Morning Briefing:")
        for i, q in enumerate(
            sorted(dreamer.morning_briefing, key=lambda x: -x.priority), 1
        ):
            priority_label = _priority_label(q.priority)
            status = "[ANSWERED]" if q.answered else ""
            print(f"  {i}. [{priority_label}] {q.question_text} {status}")

    print()

    # Last dream info
    if dreamer.last_dream:
        print(f"Last dream: {dreamer.last_dream.started_at}")
        if dreamer.last_dream.interrupted:
            print(f"  (Interrupted: {dreamer.last_dream.interrupt_reason})")

    return 0


def _priority_label(priority: int) -> str:
    """Convert priority number to label."""
    if priority >= 80:
        return "HIGH"
    elif priority >= 50:
        return "MED"
    else:
        return "LOW"


async def _run_rem_cycle(dreamer) -> int:
    """Run a REM maintenance cycle."""
    print("[DREAMER] Entering REM cycle...")
    print("  (Ctrl+C to interrupt)")
    print()

    try:
        report = await dreamer.rem_cycle()

        print(f"[DREAMER] Cycle complete: {report.phase_reached.value}")
        print(f"  Chunks processed: {report.chunks_processed}/{report.total_chunks}")
        print(f"  Questions generated: {report.questions_generated}")

        if report.interrupted:
            print(f"  Interrupted: {report.interrupt_reason}")

        if report.errors:
            print(f"  Errors: {len(report.errors)}")
            for err in report.errors[:3]:
                print(f"    - {err}")

        return 0

    except KeyboardInterrupt:
        print("\n[DREAMER] Cycle interrupted by user")
        return 130


def _answer_questions(dreamer) -> int:
    """Interactive question answering."""
    questions = [q for q in dreamer.morning_briefing if not q.answered]

    if not questions:
        print("[DREAMER] No unanswered questions.")
        return 0

    print("[DREAMER] Morning Briefing - Interactive Mode")
    print("  Type answer or 'skip' to skip, 'quit' to exit")
    print()

    for q in sorted(questions, key=lambda x: -x.priority):
        priority_label = _priority_label(q.priority)
        print(f"[{priority_label}] {q.question_text}")

        if q.context:
            print(f"  Context: {q.context}")

        try:
            answer = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return 0

        if answer.lower() == "quit":
            break
        elif answer.lower() == "skip":
            continue
        else:
            dreamer.answer_question(q.question_id, answer)
            print("  Recorded.")

        print()

    answered = dreamer.clear_answered()
    print(f"[DREAMER] Processed {answered} answers.")

    return 0
