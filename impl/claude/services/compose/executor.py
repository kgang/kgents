"""
Composition Executor: Execute kg command compositions with dependency resolution.

"Parallel where possible, sequential where necessary."

The executor:
1. Parses command strings into kg subcommands
2. Resolves dependencies (default: sequential)
3. Executes each step, capturing results
4. Links step marks to unified composition trace
5. Early exits on failure (unless continue_on_failure=True)

Pattern: Container-Owns-Workflow (Pattern 1 from crown-jewel-patterns.md)
    The executor owns the execution flow, coordinates with the trace,
    and delegates to individual command handlers.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 5)
"""

from __future__ import annotations

import asyncio
import shlex
from datetime import UTC, datetime
from typing import Any

from .trace import complete_composition_trace, record_step_execution, start_composition_trace
from .types import Composition, CompositionStatus, StepResult


class CompositionExecutor:
    """
    Execute compositions with dependency-aware scheduling.

    The executor manages:
    - Command parsing and dispatch
    - Dependency resolution
    - Trace management
    - Error handling and early exit
    """

    def __init__(
        self,
        continue_on_failure: bool = False,
        verbose: bool = False,
        timeout_seconds: float | None = None,
    ) -> None:
        """
        Initialize executor.

        Args:
            continue_on_failure: If True, continue executing after failures
            verbose: If True, print progress messages
            timeout_seconds: Timeout per step in seconds (None = no timeout)
        """
        self.continue_on_failure = continue_on_failure
        self.verbose = verbose
        self.timeout_seconds = timeout_seconds

    async def execute(self, composition: Composition) -> Composition:
        """
        Execute a composition, updating it with results.

        Returns the composition with updated status and results.
        """
        # Start trace
        trace = await start_composition_trace(composition)
        composition.status = CompositionStatus.RUNNING
        composition.started_at = datetime.now()

        try:
            # Execute each step in order (respecting dependencies)
            for step in composition.steps:
                # Check dependencies (unless continue_on_failure and using default sequential deps)
                # If continue_on_failure=True and step only depends on previous step,
                # we should run it anyway (that's what --continue means)
                should_check_deps = not (
                    self.continue_on_failure
                    and len(step.depends_on) == 1
                    and step.depends_on[0] == step.index - 1
                )

                if should_check_deps and not self._deps_satisfied(step.index, composition):
                    # Skip this step
                    result = StepResult(
                        step_index=step.index,
                        success=False,
                        output="",
                        duration_ms=0.0,
                        skipped=True,
                        error="Dependencies not satisfied",
                    )
                    composition.results.append(result)
                    await record_step_execution(trace, step.index, step.command, result)
                    continue

                # Execute the step
                if self.verbose:
                    print(f"[compose] Step {step.index}: {step.command}")

                # Apply timeout if configured
                if self.timeout_seconds:
                    try:
                        result = await asyncio.wait_for(
                            self._execute_step(step.command), timeout=self.timeout_seconds
                        )
                    except asyncio.TimeoutError:
                        result = StepResult(
                            step_index=step.index,
                            success=False,
                            output="",
                            duration_ms=self.timeout_seconds * 1000,
                            error=f"Step timed out after {self.timeout_seconds}s",
                        )
                else:
                    result = await self._execute_step(step.command)

                result.step_index = step.index
                composition.results.append(result)

                # Record in trace
                await record_step_execution(trace, step.index, step.command, result)

                if self.verbose:
                    status = "✓" if result.success else "✗"
                    print(f"[compose] {status} Step {step.index} ({result.duration_ms:.0f}ms)")

                # Early exit on failure
                if not result.success and not self.continue_on_failure:
                    if self.verbose:
                        print(f"[compose] Early exit on failure (step {step.index})")
                    break

            # Determine final status
            if composition.all_succeeded:
                composition.status = CompositionStatus.COMPLETED
            else:
                composition.status = CompositionStatus.FAILED

        except Exception as e:
            composition.status = CompositionStatus.FAILED
            # Record the exception as a failed step if no results yet
            if not composition.results:
                composition.results.append(
                    StepResult(
                        step_index=0,
                        success=False,
                        output="",
                        duration_ms=0.0,
                        error=f"Executor error: {e}",
                    )
                )

        finally:
            composition.completed_at = datetime.now()
            await complete_composition_trace(trace, composition)

        return composition

    def _deps_satisfied(self, step_index: int, composition: Composition) -> bool:
        """Check if all dependencies for a step are satisfied."""
        step = composition.steps[step_index]

        for dep_index in step.depends_on:
            # Check if dependency exists
            if dep_index >= len(composition.results):
                return False

            # Check if dependency succeeded
            dep_result = composition.results[dep_index]
            if not dep_result.success:
                return False

        return True

    async def _execute_step(self, command: str) -> StepResult:
        """
        Execute a single kg subcommand.

        Parses the command string and dispatches to the appropriate handler.
        """
        start_time = datetime.now(UTC)

        try:
            # Parse command
            parts = shlex.split(command)
            if not parts:
                return StepResult(
                    step_index=-1,
                    success=False,
                    output="",
                    duration_ms=0.0,
                    error="Empty command",
                )

            subcommand = parts[0]
            args = parts[1:]

            # Dispatch to handler
            output, success = await self._dispatch_command(subcommand, args)

            duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return StepResult(
                step_index=-1,  # Will be set by caller
                success=success,
                output=output,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
            return StepResult(
                step_index=-1,
                success=False,
                output="",
                duration_ms=duration_ms,
                error=str(e),
            )

    async def _dispatch_command(self, subcommand: str, args: list[str]) -> tuple[str, bool]:
        """
        Dispatch a kg subcommand to its handler.

        Returns (output, success).

        Calls the real command handlers from protocols.cli and captures their output.
        We run them in a thread pool to avoid event loop conflicts (since command
        handlers may call asyncio.run() internally).
        """
        import io
        import sys

        def _run_command() -> tuple[str, int]:
            """Run command in thread, capturing output."""
            old_stdout = sys.stdout
            sys.stdout = captured = io.StringIO()

            try:
                # Import and call command handler
                if subcommand == "audit":
                    from protocols.cli.commands.audit import cmd_audit
                    exit_code = cmd_audit(args)
                elif subcommand == "annotate":
                    from protocols.cli.handlers.annotate import cmd_annotate
                    exit_code = cmd_annotate(args)
                elif subcommand == "experiment":
                    from protocols.cli.commands.experiment import cmd_experiment
                    exit_code = cmd_experiment(args)
                elif subcommand == "probe":
                    from protocols.cli.handlers.probe_thin import cmd_probe
                    exit_code = cmd_probe(args)
                else:
                    return (f"Unknown subcommand: {subcommand}", 1)

                # Get captured output
                output = captured.getvalue()
                return (output, exit_code)

            finally:
                # Restore stdout
                sys.stdout = old_stdout

        # Run in thread pool to avoid event loop conflicts
        output, exit_code = await asyncio.to_thread(_run_command)
        success = exit_code == 0

        return (output, success)


async def execute_composition(
    composition: Composition,
    continue_on_failure: bool = False,
    verbose: bool = False,
    timeout_seconds: float | None = None,
) -> Composition:
    """
    Execute a composition with default executor.

    Convenience function for simple execution.
    """
    executor = CompositionExecutor(
        continue_on_failure=continue_on_failure,
        verbose=verbose,
        timeout_seconds=timeout_seconds,
    )
    return await executor.execute(composition)
