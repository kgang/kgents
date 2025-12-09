"""
Watch Mode - Autonomous observation and opportune surfacing loop.

Continuously monitors workspace for tensions and surfaces them at
opportune moments based on Kairos timing logic.

From spec/protocols/kairos.md:
  kgents mirror watch ~/Vault --budget=medium

Flow:
  1. Observe new events (git commits, file changes)
  2. Detect tensions from drift
  3. Evaluate timing for each tension
  4. Surface if benefit > threshold AND budget available
  5. Defer otherwise
  6. Recharge + sleep
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

from .budget import BudgetLevel
from .controller import KairosController


async def watch_loop(
    workspace_path: Path,
    tension_detector: Callable,
    budget_level: BudgetLevel = BudgetLevel.MEDIUM,
    interval: timedelta = timedelta(minutes=10),
    on_surface: Callable | None = None,
    on_defer: Callable | None = None,
    verbose: bool = False,
):
    """
    Autonomous observation + opportune surfacing loop.

    Args:
        workspace_path: Path to workspace/repository to monitor
        tension_detector: Callable that detects tensions (from Mirror protocol)
        budget_level: Intervention rate limit
        interval: Observation interval
        on_surface: Callback when tension surfaced (tension, evaluation)
        on_defer: Callback when tension deferred (tension, reason)
        verbose: Print debug logs

    The tension_detector should have signature:
        async def detect_tensions(workspace_path: Path) -> list[Tension]
    """
    controller = KairosController(
        workspace_path=workspace_path,
        budget_level=budget_level,
    )

    if verbose:
        print(f"[Kairos] Starting watch mode: {budget_level.label}")
        print(f"[Kairos] Workspace: {workspace_path}")
        print(f"[Kairos] Interval: {interval}")

    iteration = 0

    while True:
        iteration += 1
        loop_start = datetime.now()

        if verbose:
            print(
                f"\n[Kairos] Observation cycle {iteration} - {loop_start.isoformat()}"
            )

        try:
            # 1. Detect tensions
            tensions = await tension_detector(workspace_path)

            if verbose:
                print(f"[Kairos] Detected {len(tensions)} tension(s)")

            # 2. Get current context
            context = controller.get_current_context()

            if verbose:
                print(
                    f"[Kairos] Attention: {context.attention_state.name} (budget={context.attention_budget:.2f})"
                )
                print(f"[Kairos] Cognitive load: {context.cognitive_load:.2f}")
                print(f"[Kairos] Budget status: {controller.budget.get_status()}")

            # 3. Evaluate each tension
            for tension in tensions:
                evaluation = controller.evaluate_timing(tension)

                if verbose:
                    print(
                        f"[Kairos] Tension {tension.id}: benefit={evaluation.benefit:.2f}, threshold={evaluation.threshold:.2f}"
                    )

                # 4. Surface or defer
                if evaluation.should_surface:
                    if controller.budget.can_intervene():
                        controller.surface_tension(tension, evaluation)

                        if verbose:
                            print(f"[Kairos] ✓ SURFACED: {tension.id}")

                        if on_surface:
                            await on_surface(tension, evaluation)
                    else:
                        controller.defer_tension(tension, reason="budget_exhausted")

                        if verbose:
                            print(
                                f"[Kairos] ✗ DEFERRED (budget exhausted): {tension.id}"
                            )

                        if on_defer:
                            await on_defer(tension, "budget_exhausted")
                else:
                    controller.defer_tension(tension, reason=evaluation.defer_reason)

                    if verbose:
                        print(
                            f"[Kairos] ✗ DEFERRED ({evaluation.defer_reason}): {tension.id}"
                        )

                    if on_defer:
                        await on_defer(tension, evaluation.defer_reason)

            # 5. Check deferred queue for retry-ready tensions
            next_deferred = controller.get_next_deferred()
            if next_deferred:
                tension, age = next_deferred

                if verbose:
                    print(
                        f"[Kairos] Re-evaluating deferred tension: {tension.id} (age={age:.1f}m)"
                    )

                # Re-evaluate
                evaluation = controller.evaluate_timing(tension)

                if evaluation.should_surface and controller.budget.can_intervene():
                    controller.surface_tension(tension, evaluation)

                    if verbose:
                        print(f"[Kairos] ✓ SURFACED (retry): {tension.id}")

                    if on_surface:
                        await on_surface(tension, evaluation)

            # 6. Recharge budget
            loop_duration = datetime.now() - loop_start
            controller.update_budget(loop_duration)

        except Exception as e:
            if verbose:
                print(f"[Kairos] Error in watch loop: {e}")
            # Continue on errors

        # 7. Sleep until next interval
        sleep_duration = interval.total_seconds()
        if verbose:
            print(f"[Kairos] Sleeping for {sleep_duration}s...")

        await asyncio.sleep(sleep_duration)


def run_watch_sync(
    workspace_path: Path,
    tension_detector: Callable,
    budget_level: BudgetLevel = BudgetLevel.MEDIUM,
    interval: timedelta = timedelta(minutes=10),
    on_surface: Callable | None = None,
    on_defer: Callable | None = None,
    verbose: bool = False,
):
    """
    Synchronous wrapper for watch_loop.

    Useful for CLI integration where asyncio event loop not already running.
    """
    asyncio.run(
        watch_loop(
            workspace_path=workspace_path,
            tension_detector=tension_detector,
            budget_level=budget_level,
            interval=interval,
            on_surface=on_surface,
            on_defer=on_defer,
            verbose=verbose,
        )
    )
