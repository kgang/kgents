"""
Flow Engine Types - Core types for the Flowfile system.

Flowfiles are the composition backbone:
- YAML-based pipeline definitions
- Jinja2 templated variables
- Debug snapshots for TUI inspection
- Step-by-step execution with dependency resolution

From docs/cli-integration-plan.md Part 4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# =============================================================================
# Status Enums
# =============================================================================


class FlowStatus(Enum):
    """Overall flow execution status."""

    PENDING = "pending"  # Not started
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"  # Failed with error
    CANCELLED = "cancelled"  # User cancelled
    PAUSED = "paused"  # Paused (for debugging)


class StepStatus(Enum):
    """Individual step execution status."""

    PENDING = "pending"  # Not started
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"  # Failed with error
    SKIPPED = "skipped"  # Skipped (condition not met)
    WAITING = "waiting"  # Waiting for dependency


# =============================================================================
# Flowfile Components
# =============================================================================


@dataclass(frozen=True)
class FlowVariable:
    """
    A templated variable in a flowfile.

    Variables use Jinja2 syntax with defaults:
        strictness: "{{ strictness | default('high') }}"
    """

    name: str
    expression: str  # Jinja2 expression
    default: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "expression": self.expression,
            "default": self.default,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowVariable:
        return cls(
            name=data["name"],
            expression=data["expression"],
            default=data.get("default"),
        )


@dataclass(frozen=True)
class FlowInput:
    """
    Input schema for a flowfile.

    Defines expected input type and constraints.
    """

    type: str = "any"  # "file", "text", "json", "any"
    extensions: tuple[str, ...] = ()  # For file type: [".py", ".js"]
    schema: str | None = None  # JSON Schema path for validation
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"type": self.type}
        if self.extensions:
            result["extensions"] = list(self.extensions)
        if self.schema:
            result["schema"] = self.schema
        result["required"] = self.required
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowInput:
        return cls(
            type=data.get("type", "any"),
            extensions=tuple(data.get("extensions", [])),
            schema=data.get("schema"),
            required=data.get("required", True),
        )


@dataclass(frozen=True)
class FlowOutput:
    """
    Output handling configuration for a flowfile.
    """

    format: str = "rich"  # "rich", "json", "yaml", "markdown"
    save_to: str | None = None  # Directory path for artifacts

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"format": self.format}
        if self.save_to:
            result["save_to"] = self.save_to
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowOutput:
        return cls(
            format=data.get("format", "rich"),
            save_to=data.get("save_to"),
        )


@dataclass(frozen=True)
class FlowHooks:
    """
    Pre/post hooks for flowfile execution.
    """

    pre: str | None = None  # Shell command or script path
    post: str | None = None  # Shell command or script path

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.pre:
            result["pre"] = self.pre
        if self.post:
            result["post"] = self.post
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowHooks:
        return cls(
            pre=data.get("pre"),
            post=data.get("post"),
        )


@dataclass(frozen=True)
class FlowErrorHandling:
    """
    Error handling configuration for flowfile execution.
    """

    strategy: str = "halt"  # "halt", "continue", "retry"
    max_retries: int = 3
    notify: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy,
            "max_retries": self.max_retries,
            "notify": self.notify,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowErrorHandling:
        return cls(
            strategy=data.get("strategy", "halt"),
            max_retries=data.get("max_retries", 3),
            notify=data.get("notify", False),
        )


@dataclass
class FlowStep:
    """
    A single step in a flowfile pipeline.

    Steps are the atomic units of composition:
    - Each step has an ID, genus, and operation
    - Input can come from previous steps via "from:step_id"
    - Conditional execution via "condition" expression
    - Debug snapshots via "debug: true"
    """

    id: str
    genus: str  # Agent genus: "P-gent", "J-gent", "Bootstrap", etc.
    operation: str  # Operation name: "extract", "judge", "compile", etc.

    # Input handling
    input: str | None = None  # "from:step_id" or literal
    args: dict[str, Any] = field(default_factory=dict)

    # Execution control
    condition: str | None = None  # Jinja2 condition expression
    on_error: str = "halt"  # "halt", "continue", "skip"
    timeout_ms: int | None = None

    # Debugging
    debug: bool = False  # Enable debug snapshot
    snapshot: bool = False  # Alias for debug

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "genus": self.genus,
            "operation": self.operation,
        }
        if self.input:
            result["input"] = self.input
        if self.args:
            result["args"] = self.args
        if self.condition:
            result["condition"] = self.condition
        if self.on_error != "halt":
            result["on_error"] = self.on_error
        if self.timeout_ms:
            result["timeout_ms"] = self.timeout_ms
        if self.debug or self.snapshot:
            result["debug"] = True
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FlowStep:
        return cls(
            id=data["id"],
            genus=data["genus"],
            operation=data["operation"],
            input=data.get("input"),
            args=data.get("args", {}),
            condition=data.get("condition"),
            on_error=data.get("on_error", "halt"),
            timeout_ms=data.get("timeout_ms"),
            debug=data.get("debug", False) or data.get("snapshot", False),
            snapshot=data.get("snapshot", False),
        )


@dataclass
class Flowfile:
    """
    A complete flowfile definition.

    This is the YAML-serializable representation of a composition pipeline.

    Example:
        version: "1.0"
        name: "Code Review Pipeline"
        description: "Parse, judge, and refine code"

        input:
          type: file
          extensions: [.py, .js, .ts]

        variables:
          strictness: "{{ strictness | default('high') }}"

        steps:
          - id: parse
            genus: P-gent
            operation: extract
          - id: judge
            genus: Bootstrap
            operation: judge
            input: "from:parse"
    """

    # Metadata
    version: str = "1.0"
    name: str = ""
    description: str = ""

    # Schema
    input: FlowInput = field(default_factory=FlowInput)
    output: FlowOutput = field(default_factory=FlowOutput)

    # Variables (Jinja2 templated)
    variables: dict[str, str] = field(default_factory=dict)

    # Pipeline
    steps: list[FlowStep] = field(default_factory=list)

    # Lifecycle
    hooks: FlowHooks = field(default_factory=FlowHooks)
    on_error: FlowErrorHandling = field(default_factory=FlowErrorHandling)

    # Source info (set during parsing)
    source_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "version": self.version,
            "name": self.name,
        }
        if self.description:
            result["description"] = self.description
        result["input"] = self.input.to_dict()
        result["output"] = self.output.to_dict()
        if self.variables:
            result["variables"] = self.variables
        result["steps"] = [step.to_dict() for step in self.steps]
        hooks_dict = self.hooks.to_dict()
        if hooks_dict:
            result["hooks"] = hooks_dict
        result["on_error"] = self.on_error.to_dict()
        return result

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], source_path: str | None = None
    ) -> Flowfile:
        # Parse input
        input_data = data.get("input", {})
        if isinstance(input_data, str):
            input_config = FlowInput(type=input_data)
        else:
            input_config = FlowInput.from_dict(input_data)

        # Parse output
        output_data = data.get("output", {})
        if isinstance(output_data, str):
            output_config = FlowOutput(format=output_data)
        else:
            output_config = FlowOutput.from_dict(output_data)

        # Parse steps
        steps = [FlowStep.from_dict(step_data) for step_data in data.get("steps", [])]

        # Parse hooks
        hooks_data = data.get("hooks", {})
        hooks = FlowHooks.from_dict(hooks_data)

        # Parse error handling
        error_data = data.get("on_error", {})
        if isinstance(error_data, str):
            error_handling = FlowErrorHandling(strategy=error_data)
        else:
            error_handling = FlowErrorHandling.from_dict(error_data)

        return cls(
            version=data.get("version", "1.0"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            input=input_config,
            output=output_config,
            variables=data.get("variables", {}),
            steps=steps,
            hooks=hooks,
            on_error=error_handling,
            source_path=source_path,
        )


# =============================================================================
# Execution Results
# =============================================================================


@dataclass
class StepResult:
    """
    Result of executing a single flow step.
    """

    step_id: str
    status: StepStatus

    # Output
    output: Any = None

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Debug
    snapshot_path: str | None = None

    # Error info
    error: str | None = None
    error_type: str | None = None

    @property
    def duration_ms(self) -> float | None:
        """Execution duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "step_id": self.step_id,
            "status": self.status.value,
        }
        if self.output is not None:
            result["output"] = self.output
        if self.started_at:
            result["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            result["completed_at"] = self.completed_at.isoformat()
        if self.duration_ms is not None:
            result["duration_ms"] = self.duration_ms
        if self.snapshot_path:
            result["snapshot_path"] = self.snapshot_path
        if self.error:
            result["error"] = self.error
            result["error_type"] = self.error_type
        return result


@dataclass
class FlowResult:
    """
    Result of executing a complete flowfile.
    """

    flow_name: str
    status: FlowStatus

    # Step results
    step_results: list[StepResult] = field(default_factory=list)

    # Final output
    output: Any = None

    # Timing
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Error info
    error: str | None = None
    failed_step: str | None = None

    @property
    def duration_ms(self) -> float | None:
        """Total execution duration in milliseconds."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None

    @property
    def completed_steps(self) -> int:
        """Number of successfully completed steps."""
        return sum(1 for r in self.step_results if r.status == StepStatus.COMPLETED)

    @property
    def total_steps(self) -> int:
        """Total number of steps."""
        return len(self.step_results)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "flow_name": self.flow_name,
            "status": self.status.value,
            "step_results": [r.to_dict() for r in self.step_results],
        }
        if self.output is not None:
            result["output"] = self.output
        if self.started_at:
            result["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            result["completed_at"] = self.completed_at.isoformat()
        if self.duration_ms is not None:
            result["duration_ms"] = self.duration_ms
        if self.error:
            result["error"] = self.error
            result["failed_step"] = self.failed_step
        result["completed_steps"] = self.completed_steps
        result["total_steps"] = self.total_steps
        return result


# =============================================================================
# Errors
# =============================================================================


class FlowError(Exception):
    """Base error for flow operations."""

    pass


class FlowValidationError(FlowError):
    """Error validating a flowfile."""

    def __init__(self, message: str, field: str | None = None, line: int | None = None):
        super().__init__(message)
        self.field = field
        self.line = line


class FlowExecutionError(FlowError):
    """Error executing a flowfile."""

    def __init__(
        self, message: str, step_id: str | None = None, cause: Exception | None = None
    ):
        super().__init__(message)
        self.step_id = step_id
        self.cause = cause
