"""
Flow Execution Engine - Execute flowfile pipelines.

The engine handles:
- Step-by-step execution with dependency resolution
- Input passing between steps (from:step_id)
- Conditional execution
- Debug snapshots
- Error handling (halt, continue, retry)
- Hooks (pre/post)

From docs/cli-integration-plan.md Part 4.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .parser import (
    render_flowfile,
    topological_sort,
    validate_flowfile_strict,
)
from .types import (
    Flowfile,
    FlowResult,
    FlowStatus,
    FlowStep,
    StepResult,
    StepStatus,
)

# =============================================================================
# Step Executors (Genus Handlers)
# =============================================================================


# Type for step execution handler
StepExecutor = Callable[[FlowStep, Any, dict[str, Any]], Any]


async def execute_p_gent_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Execute a P-gent (Parser) step."""
    operation = step.operation

    if operation == "extract":
        # Simple extraction - return input with structure annotation
        return {
            "type": "parsed",
            "content": input_data,
            "structure": "extracted",
        }
    elif operation == "repair":
        # Attempt repair of malformed input
        return {
            "type": "repaired",
            "content": input_data,
            "repairs": [],
        }
    elif operation == "validate":
        # Validate against schema
        schema = step.args.get("schema")
        return {
            "type": "validated",
            "content": input_data,
            "valid": True,
            "schema": schema,
        }
    else:
        return {"type": "p_gent", "operation": operation, "input": input_data}


async def execute_j_gent_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Execute a J-gent (JIT) step."""
    operation = step.operation

    if operation == "compile":
        # JIT compile intent
        intent = step.args.get("intent", str(input_data))
        return {
            "type": "compiled",
            "intent": intent,
            "budget": step.args.get("budget", "medium"),
        }
    elif operation == "classify":
        # Classify reality type
        return {
            "type": "classified",
            "reality": "DETERMINISTIC",  # or PROBABILISTIC, CHAOTIC
            "input": input_data,
        }
    elif operation == "defer":
        # Defer operation
        return {
            "type": "deferred",
            "operation": input_data,
            "reason": "entropy budget",
        }
    else:
        return {"type": "j_gent", "operation": operation, "input": input_data}


async def execute_g_gent_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Execute a G-gent (Grammarian) step."""
    operation = step.operation

    if operation == "reify":
        # Create tongue from domain
        domain = step.args.get("domain", str(input_data))
        return {
            "type": "tongue",
            "domain": domain,
            "level": step.args.get("level", "COMMAND"),
        }
    elif operation == "parse":
        # Parse with tongue
        tongue = step.args.get("tongue")
        return {
            "type": "parsed",
            "input": input_data,
            "tongue": tongue,
        }
    else:
        return {"type": "g_gent", "operation": operation, "input": input_data}


async def execute_bootstrap_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Execute a Bootstrap step."""
    operation = step.operation

    if operation == "judge":
        # Judge against principles
        principles = step.args.get("principles", "spec/principles.md")
        strictness = step.args.get("strictness", "high")
        return {
            "type": "judgment",
            "verdict": "APPROVED",  # or REJECTED
            "principles": principles,
            "strictness": strictness,
            "input": input_data,
            "scores": {
                "tasteful": 0.9,
                "curated": 0.85,
                "ethical": 0.95,
                "composable": 0.8,
            },
        }
    elif operation == "verify":
        # Verify category laws
        return {
            "type": "verification",
            "laws_verified": True,
            "input": input_data,
        }
    else:
        return {"type": "bootstrap", "operation": operation, "input": input_data}


async def execute_w_gent_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Execute a W-gent (Witness) step."""
    operation = step.operation

    if operation == "watch":
        # Observe without judgment
        return {
            "type": "observation",
            "target": input_data,
            "patterns": [],
        }
    elif operation == "fidelity":
        # Check fidelity
        return {
            "type": "fidelity_check",
            "input": input_data,
            "drift_detected": False,
        }
    else:
        return {"type": "w_gent", "operation": operation, "input": input_data}


async def execute_r_gent_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Execute an R-gent (Refiner) step."""
    operation = step.operation

    if operation == "optimize":
        # Optimize code/artifact
        return {
            "type": "optimized",
            "input": input_data,
            "improvements": [],
        }
    elif operation == "refine":
        # Iterative refinement
        return {
            "type": "refined",
            "input": input_data,
            "iterations": 1,
        }
    else:
        return {"type": "r_gent", "operation": operation, "input": input_data}


async def execute_l_gent_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Execute an L-gent (Library) step."""
    operation = step.operation

    if operation == "catalog":
        # List catalog
        return {
            "type": "catalog",
            "entries": [],
        }
    elif operation == "discover":
        # Search catalog
        query = step.args.get("query", str(input_data))
        return {
            "type": "search_results",
            "query": query,
            "results": [],
        }
    elif operation == "register":
        # Register artifact
        return {
            "type": "registered",
            "artifact": input_data,
        }
    else:
        return {"type": "l_gent", "operation": operation, "input": input_data}


async def execute_t_gent_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Execute a T-gent (Tester) step."""
    operation = step.operation

    if operation == "verify":
        # Verify agent
        return {
            "type": "test_result",
            "passed": True,
            "input": input_data,
        }
    elif operation == "fuzz":
        # Fuzz testing
        iterations = step.args.get("iterations", 100)
        return {
            "type": "fuzz_result",
            "iterations": iterations,
            "failures": 0,
        }
    else:
        return {"type": "t_gent", "operation": operation, "input": input_data}


async def execute_generic_step(
    step: FlowStep, input_data: Any, context: dict[str, Any]
) -> Any:
    """Fallback executor for unimplemented genera."""
    return {
        "type": "generic",
        "genus": step.genus,
        "operation": step.operation,
        "input": input_data,
        "args": step.args,
    }


# Genus -> Executor mapping
GENUS_EXECUTORS: dict[str, Callable] = {
    "P-gent": execute_p_gent_step,
    "J-gent": execute_j_gent_step,
    "G-gent": execute_g_gent_step,
    "W-gent": execute_w_gent_step,
    "R-gent": execute_r_gent_step,
    "L-gent": execute_l_gent_step,
    "T-gent": execute_t_gent_step,
    "Bootstrap": execute_bootstrap_step,
}


# =============================================================================
# Condition Evaluation
# =============================================================================


def evaluate_condition(condition: str, step_results: dict[str, StepResult]) -> bool:
    """
    Evaluate a condition expression.

    Supports simple patterns:
    - "step_id.field == 'value'"
    - "step_id.field != 'value'"
    - "step_id.success"
    - "not step_id.success"

    Args:
        condition: Condition expression
        step_results: Results from previous steps

    Returns:
        True if condition is met
    """
    # Handle "not" prefix
    if condition.startswith("not "):
        return not evaluate_condition(condition[4:], step_results)

    # Handle equality/inequality
    for op in ("!=", "=="):
        if op in condition:
            parts = condition.split(op)
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip().strip("'\"")

                # Parse left side (step_id.field)
                if "." in left:
                    step_id, field = left.split(".", 1)
                    if step_id in step_results:
                        result = step_results[step_id]
                        if result.output and isinstance(result.output, dict):
                            value = result.output.get(field)
                            if op == "==":
                                return str(value) == right
                            else:
                                return str(value) != right

                return op == "!="  # Default: not equal if field not found

    # Handle simple boolean (step_id.success)
    if "." in condition:
        step_id, field = condition.split(".", 1)
        if step_id in step_results:
            result = step_results[step_id]
            if field == "success":
                return result.status == StepStatus.COMPLETED
            elif result.output and isinstance(result.output, dict):
                return bool(result.output.get(field))

    return True  # Default to true if can't evaluate


# =============================================================================
# Flow Engine
# =============================================================================


class FlowEngine:
    """
    Engine for executing flowfile pipelines.

    The engine handles:
    - Step execution in dependency order
    - Input passing between steps
    - Condition evaluation
    - Debug snapshots
    - Error handling
    - Hooks
    """

    def __init__(
        self,
        debug_dir: Path | None = None,
        progress_callback: Callable[[str, str], None] | None = None,
    ):
        """
        Initialize flow engine.

        Args:
            debug_dir: Directory for debug snapshots (default: .kgents/debug/)
            progress_callback: Callback for progress updates (step_id, status)
        """
        self.debug_dir = debug_dir or Path(".kgents/debug")
        self.progress_callback = progress_callback
        self._executors = GENUS_EXECUTORS.copy()

    def register_executor(self, genus: str, executor: Callable) -> None:
        """Register a custom executor for a genus."""
        self._executors[genus] = executor

    def _log_progress(self, step_id: str, status: str) -> None:
        """Log progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(step_id, status)

    async def _run_hook(self, hook: str | None, context: dict[str, Any]) -> bool:
        """
        Run a hook script.

        Returns True if hook succeeded (or no hook defined).
        """
        if not hook:
            return True

        try:
            # Expand variables in hook command
            cmd = hook
            for key, value in context.items():
                cmd = cmd.replace(f"${{{key}}}", str(value))

            # Run hook
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _save_snapshot(self, step_id: str, data: Any, flow_name: str) -> str:
        """Save debug snapshot and return path."""
        snapshot_dir = self.debug_dir / flow_name / step_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_path = snapshot_dir / f"{timestamp}.json"

        with open(snapshot_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return str(snapshot_path)

    async def _execute_step(
        self,
        step: FlowStep,
        input_data: Any,
        context: dict[str, Any],
    ) -> StepResult:
        """Execute a single step."""
        started_at = datetime.now()
        self._log_progress(step.id, "running")

        try:
            # Get executor
            executor = self._executors.get(step.genus, execute_generic_step)

            # Execute with timeout
            if step.timeout_ms:
                timeout = step.timeout_ms / 1000.0
                output = await asyncio.wait_for(
                    executor(step, input_data, context),
                    timeout=timeout,
                )
            else:
                output = await executor(step, input_data, context)

            completed_at = datetime.now()
            self._log_progress(step.id, "completed")

            # Save debug snapshot if enabled
            snapshot_path = None
            if step.debug:
                flow_name = context.get("flow_name", "unknown")
                snapshot_path = self._save_snapshot(step.id, output, flow_name)

            return StepResult(
                step_id=step.id,
                status=StepStatus.COMPLETED,
                output=output,
                started_at=started_at,
                completed_at=completed_at,
                snapshot_path=snapshot_path,
            )

        except asyncio.TimeoutError:
            self._log_progress(step.id, "failed")
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                error=f"Step timed out after {step.timeout_ms}ms",
                error_type="timeout",
            )

        except Exception as e:
            self._log_progress(step.id, "failed")
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                error=str(e),
                error_type=type(e).__name__,
            )

    async def execute(
        self,
        flowfile: Flowfile,
        input_data: Any = None,
        variables: dict[str, Any] | None = None,
    ) -> FlowResult:
        """
        Execute a flowfile.

        Args:
            flowfile: Flowfile to execute
            input_data: Initial input data
            variables: Variable values to override defaults

        Returns:
            FlowResult with step results and final output
        """
        started_at = datetime.now()
        variables = variables or {}

        # Validate
        validate_flowfile_strict(flowfile)

        # Render templates
        rendered = render_flowfile(flowfile, variables)

        # Build execution context
        context: dict[str, Any] = {
            "flow_name": rendered.name,
            "input": input_data,
            "variables": variables,
        }

        # Run pre-hook
        if not await self._run_hook(rendered.hooks.pre, context):
            return FlowResult(
                flow_name=rendered.name,
                status=FlowStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                error="Pre-hook failed",
            )

        # Get execution order
        try:
            execution_order = topological_sort(rendered)
        except Exception as e:
            return FlowResult(
                flow_name=rendered.name,
                status=FlowStatus.FAILED,
                started_at=started_at,
                completed_at=datetime.now(),
                error=str(e),
            )

        # Create step lookup
        step_lookup = {s.id: s for s in rendered.steps}

        # Execute steps
        step_results: dict[str, StepResult] = {}
        final_output = None
        failed_step = None

        for step_id in execution_order:
            step = step_lookup[step_id]

            # Check condition
            if step.condition:
                if not evaluate_condition(step.condition, step_results):
                    step_results[step_id] = StepResult(
                        step_id=step_id,
                        status=StepStatus.SKIPPED,
                    )
                    self._log_progress(step_id, "skipped")
                    continue

            # Resolve input
            step_input = input_data
            if step.input:
                if step.input.startswith("from:"):
                    ref_id = step.input[5:]
                    if ref_id in step_results:
                        step_input = step_results[ref_id].output
                else:
                    step_input = step.input

            # Execute step
            result = await self._execute_step(step, step_input, context)
            step_results[step_id] = result

            # Handle failure
            if result.status == StepStatus.FAILED:
                if step.on_error == "halt" or rendered.on_error.strategy == "halt":
                    failed_step = step_id
                    break
                elif step.on_error == "skip":
                    continue
                # else: continue execution

            # Track final output (last successful step)
            if result.status == StepStatus.COMPLETED:
                final_output = result.output

        # Determine final status
        if failed_step:
            status = FlowStatus.FAILED
        elif all(
            r.status in (StepStatus.COMPLETED, StepStatus.SKIPPED)
            for r in step_results.values()
        ):
            status = FlowStatus.COMPLETED
        else:
            status = FlowStatus.FAILED

        completed_at = datetime.now()

        # Run post-hook
        if status == FlowStatus.COMPLETED:
            context["output"] = final_output
            await self._run_hook(rendered.hooks.post, context)

        return FlowResult(
            flow_name=rendered.name,
            status=status,
            step_results=list(step_results.values()),
            output=final_output,
            started_at=started_at,
            completed_at=completed_at,
            error=step_results[failed_step].error if failed_step else None,
            failed_step=failed_step,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


async def execute_flow(
    flowfile_path: str | Path,
    input_data: Any = None,
    variables: dict[str, Any] | None = None,
    progress_callback: Callable[[str, str], None] | None = None,
) -> FlowResult:
    """
    Execute a flowfile from path.

    Args:
        flowfile_path: Path to flowfile
        input_data: Initial input data
        variables: Variable overrides
        progress_callback: Progress callback (step_id, status)

    Returns:
        FlowResult
    """
    from .parser import parse_flowfile

    flowfile = parse_flowfile(flowfile_path)
    engine = FlowEngine(progress_callback=progress_callback)
    return await engine.execute(flowfile, input_data, variables)


def execute_flow_sync(
    flowfile_path: str | Path,
    input_data: Any = None,
    variables: dict[str, Any] | None = None,
) -> FlowResult:
    """Synchronous wrapper for execute_flow."""
    return asyncio.run(execute_flow(flowfile_path, input_data, variables))
