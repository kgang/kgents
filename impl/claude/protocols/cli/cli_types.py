"""
CLI Protocol Types - Core abstractions for the command surface.

Implements the output contracts, error classification, and configuration
patterns from spec/protocols/cli.md.

Category Theory:
  The CLI is a functor: Intent -> (Parse >> Route >> Execute >> Format) -> Result
  Commands are morphisms in the Intent category.
  Results are objects in the Output category with structured levels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Generic, TypeVar

T = TypeVar("T")


# =============================================================================
# Output Enums
# =============================================================================


class OutputFormat(Enum):
    """
    Output format selection from spec/protocols/cli.md.

    Maps to the Output Hierarchy levels:
    - code: Level 0 (exit code only)
    - value: Level 1 (single value)
    - json: Level 2 (structured record)
    - jsonl: Level 3 (streaming records)
    - rich: Level 4 (human-formatted)
    - markdown: Level 4 (markdown report)
    """

    CODE = "code"  # Level 0: Exit code only
    VALUE = "value"  # Level 1: Single value
    JSON = "json"  # Level 2: Structured JSON
    JSONL = "jsonl"  # Level 3: Streaming JSONL
    RICH = "rich"  # Level 4: Rich human output (default for TTY)
    MARKDOWN = "markdown"  # Level 4: Markdown report


class OutputLevel(Enum):
    """Output hierarchy level from spec."""

    EXIT_CODE = 0  # Exit code only
    SCALAR = 1  # Single value
    RECORD = 2  # Structured JSON
    STREAM = 3  # JSONL stream
    RICH = 4  # Human-formatted


class BudgetLevel(Enum):
    """
    Entropy budget levels from spec/protocols/cli.md.

    Controls resource expenditure for operations.
    """

    MINIMAL = "minimal"  # Avoid LLM calls where possible
    LOW = "low"  # Prefer cached/local operations
    MEDIUM = "medium"  # Balanced (default)
    HIGH = "high"  # Allow expensive operations
    UNLIMITED = "unlimited"  # No restrictions (use with care)

    @property
    def max_llm_calls(self) -> int:
        """Maximum LLM calls allowed at this budget level."""
        return {
            BudgetLevel.MINIMAL: 0,
            BudgetLevel.LOW: 1,
            BudgetLevel.MEDIUM: 5,
            BudgetLevel.HIGH: 20,
            BudgetLevel.UNLIMITED: 1000,
        }[self]

    @property
    def max_tokens(self) -> int:
        """Maximum tokens allowed at this budget level."""
        return {
            BudgetLevel.MINIMAL: 0,
            BudgetLevel.LOW: 4000,
            BudgetLevel.MEDIUM: 20000,
            BudgetLevel.HIGH: 100000,
            BudgetLevel.UNLIMITED: 1000000,
        }[self]


class PersonaMode(Enum):
    """
    K-gent personality lifting from spec/protocols/cli.md.

    Controls tone and style of output.
    """

    WARM = "warm"  # Friendly, encouraging
    CLINICAL = "clinical"  # Precise, technical
    PLAYFUL = "playful"  # Witty, exploratory
    MINIMAL = "minimal"  # No personality modification


class ErrorSeverity(Enum):
    """
    Error severity levels from spec/protocols/cli.md.

    Maps to exit code ranges.
    """

    SUCCESS = 0  # Operation completed (exit 0)
    WARNING = 1  # Completed with concerns (exit 0, stderr)
    DEGRADED = 2  # Partial success (exit 1-9)
    FAILURE = 3  # Operation failed (exit 10-99)
    FATAL = 4  # System-level failure (exit 100-127)

    @property
    def exit_code_range(self) -> tuple[int, int]:
        """Exit code range for this severity."""
        return {
            ErrorSeverity.SUCCESS: (0, 0),
            ErrorSeverity.WARNING: (0, 0),
            ErrorSeverity.DEGRADED: (1, 9),
            ErrorSeverity.FAILURE: (10, 99),
            ErrorSeverity.FATAL: (100, 127),
        }[self]


class ErrorRecoverability(Enum):
    """
    Error recoverability from spec/protocols/cli.md.

    Guides user action on error.
    """

    TRANSIENT = "transient"  # Retry may succeed
    PERMANENT = "permanent"  # Input is invalid
    RESOURCE = "resource"  # Budget/quota exceeded
    ETHICAL = "ethical"  # Violates constraints


# =============================================================================
# Core Types
# =============================================================================


@dataclass(frozen=True)
class ErrorInfo:
    """
    Structured error information from spec/protocols/cli.md.

    Provides actionable error context.
    """

    error_type: ErrorRecoverability
    severity: ErrorSeverity
    code: str  # e.g., "PARSE_SCHEMA_MISMATCH"
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    suggestions: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON output."""
        return {
            "error": {
                "type": self.error_type.value,
                "severity": self.severity.value,
                "code": self.code,
                "message": self.message,
                "details": self.details,
                "suggestions": list(self.suggestions),
            }
        }

    @property
    def exit_code(self) -> int:
        """Compute exit code from severity."""
        low, high = self.severity.exit_code_range
        return low if low == high else (low + high) // 2


@dataclass(frozen=True)
class BudgetStatus:
    """
    Entropy budget tracking.

    From spec: Every command respects entropy budgets.
    """

    level: BudgetLevel
    tokens_used: int = 0
    tokens_limit: int = 0
    llm_calls_used: int = 0
    llm_calls_limit: int = 0
    entropy_spent: float = 0.0

    @classmethod
    def from_level(cls, level: BudgetLevel) -> BudgetStatus:
        """Create budget status from level."""
        return cls(
            level=level,
            tokens_limit=level.max_tokens,
            llm_calls_limit=level.max_llm_calls,
        )

    def can_afford(self, estimated_tokens: int = 0, llm_calls: int = 0) -> bool:
        """Check if operation is within budget."""
        if self.level == BudgetLevel.UNLIMITED:
            return True
        tokens_ok = (self.tokens_used + estimated_tokens) <= self.tokens_limit
        calls_ok = (self.llm_calls_used + llm_calls) <= self.llm_calls_limit
        return tokens_ok and calls_ok

    def spend(self, tokens: int = 0, llm_calls: int = 0) -> BudgetStatus:
        """Return new budget with spent resources."""
        return BudgetStatus(
            level=self.level,
            tokens_used=self.tokens_used + tokens,
            tokens_limit=self.tokens_limit,
            llm_calls_used=self.llm_calls_used + llm_calls,
            llm_calls_limit=self.llm_calls_limit,
            entropy_spent=self.entropy_spent + (tokens / max(1, self.tokens_limit)),
        )


@dataclass(frozen=True)
class OutputEnvelope(Generic[T]):
    """
    The envelope pattern from spec/protocols/cli.md.

    Rich outputs include metadata envelope wrapping the result.
    """

    result: T
    version: str = "1.0"
    timestamp: datetime = field(default_factory=datetime.now)
    agent: str = ""
    duration_ms: int = 0
    tokens_used: int = 0
    entropy_spent: float = 0.0
    diagnostics: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON output."""
        result_dict = (
            self.result if isinstance(self.result, dict) else {"value": self.result}
        )
        return {
            "envelope": {
                "version": self.version,
                "timestamp": self.timestamp.isoformat(),
                "agent": self.agent,
                "duration_ms": self.duration_ms,
                "cost": {
                    "tokens": self.tokens_used,
                    "entropy_spent": self.entropy_spent,
                },
            },
            "result": result_dict,
            "diagnostics": list(self.diagnostics),
        }


@dataclass
class CommandResult(Generic[T]):
    """
    Result of a CLI command execution.

    Wraps success/failure with structured context.
    """

    success: bool
    output: T | None = None
    error: ErrorInfo | None = None
    exit_code: int = 0
    duration_ms: int = 0
    budget_status: BudgetStatus | None = None

    @classmethod
    def ok(
        cls, output: T, duration_ms: int = 0, budget: BudgetStatus | None = None
    ) -> CommandResult[T]:
        """Create successful result."""
        return cls(
            success=True,
            output=output,
            exit_code=0,
            duration_ms=duration_ms,
            budget_status=budget,
        )

    @classmethod
    def fail(cls, error: ErrorInfo, duration_ms: int = 0) -> CommandResult[T]:
        """Create failure result."""
        return cls(
            success=False,
            error=error,
            exit_code=error.exit_code,
            duration_ms=duration_ms,
        )

    def to_envelope(self, agent: str = "") -> OutputEnvelope[T | dict]:
        """Wrap result in output envelope."""
        if self.success and self.output is not None:
            return OutputEnvelope(
                result=self.output,
                agent=agent,
                duration_ms=self.duration_ms,
                tokens_used=self.budget_status.tokens_used if self.budget_status else 0,
                entropy_spent=self.budget_status.entropy_spent
                if self.budget_status
                else 0.0,
            )
        elif self.error:
            return OutputEnvelope(
                result=self.error.to_dict(),
                agent=agent,
                duration_ms=self.duration_ms,
            )
        else:
            return OutputEnvelope(result={}, agent=agent)


# =============================================================================
# CLI Context
# =============================================================================


@dataclass
class CLIContext:
    """
    Execution context for CLI commands.

    Threading state through command execution.
    """

    # Output configuration
    output_format: OutputFormat = OutputFormat.RICH
    persona: PersonaMode = PersonaMode.MINIMAL

    # Budget management
    budget: BudgetStatus = field(
        default_factory=lambda: BudgetStatus.from_level(BudgetLevel.MEDIUM)
    )

    # Privacy
    sanctuary_paths: tuple[Path, ...] = ()

    # Session (D-gent integration)
    session_id: str | None = None

    # Provenance
    operation_id: str = ""
    parent_operation_id: str | None = None

    # Timestamps
    started_at: datetime = field(default_factory=datetime.now)

    # Metrics visibility (for trust-building, default on)
    show_metrics: bool = True

    def is_tty(self) -> bool:
        """Check if output is a TTY (for rich format default)."""
        import sys

        return sys.stdout.isatty()

    def effective_format(self) -> OutputFormat:
        """Get effective output format (TTY-aware)."""
        if self.output_format == OutputFormat.RICH and not self.is_tty():
            return OutputFormat.JSON
        return self.output_format

    def is_sanctuary(self, path: Path) -> bool:
        """Check if path is in sanctuary (privacy-protected)."""
        path = path.resolve()
        for sanctuary in self.sanctuary_paths:
            try:
                path.relative_to(sanctuary.resolve())
                return True
            except ValueError:
                continue
        return False

    def with_budget(self, level: BudgetLevel) -> CLIContext:
        """Return new context with different budget level."""
        return CLIContext(
            output_format=self.output_format,
            persona=self.persona,
            budget=BudgetStatus.from_level(level),
            sanctuary_paths=self.sanctuary_paths,
            session_id=self.session_id,
            operation_id=self.operation_id,
            parent_operation_id=self.parent_operation_id,
            started_at=self.started_at,
        )


# =============================================================================
# Output Formatting
# =============================================================================


def format_output(
    result: CommandResult[Any],
    ctx: CLIContext,
    agent_name: str = "kgents",
) -> str:
    """
    Format command result according to output format.

    Implements the output hierarchy from spec.
    """
    import json

    fmt = ctx.effective_format()

    if fmt == OutputFormat.CODE:
        # Level 0: Exit code only (no output)
        return ""

    elif fmt == OutputFormat.VALUE:
        # Level 1: Single value
        if result.success and result.output is not None:
            return str(result.output)
        elif result.error:
            return f"Error: {result.error.message}"
        return ""

    elif fmt == OutputFormat.JSON:
        # Level 2: Structured JSON
        envelope = result.to_envelope(agent_name)
        return json.dumps(envelope.to_dict(), indent=2, default=str)

    elif fmt == OutputFormat.JSONL:
        # Level 3: JSONL (single line)
        envelope = result.to_envelope(agent_name)
        return json.dumps(envelope.to_dict(), default=str)

    elif fmt == OutputFormat.MARKDOWN:
        # Level 4: Markdown report
        return _format_markdown(result, agent_name)

    else:  # OutputFormat.RICH
        # Level 4: Rich human output
        return _format_rich(result, ctx, agent_name)


def _format_rich(result: CommandResult[Any], ctx: CLIContext, agent: str) -> str:
    """Format as rich human-readable output."""
    lines = []

    # Header box
    if result.success:
        lines.append(f"--- {agent} ---")
    else:
        lines.append(f"--- {agent} (error) ---")

    # Main content
    if result.success and result.output is not None:
        if isinstance(result.output, dict):
            for key, value in result.output.items():
                lines.append(f"  {key}: {value}")
        elif isinstance(result.output, str):
            lines.append(result.output)
        else:
            lines.append(str(result.output))
    elif result.error:
        lines.append(f"Error [{result.error.code}]: {result.error.message}")
        if result.error.suggestions:
            lines.append("")
            lines.append("Suggestions:")
            for suggestion in result.error.suggestions:
                lines.append(f"  - {suggestion}")

    # Footer with metrics (for trust-building, default on)
    if ctx.show_metrics:
        lines.append("")
        lines.append(_format_metrics_line(result, ctx))

    return "\n".join(lines)


def _format_metrics_line(result: CommandResult[Any], ctx: CLIContext) -> str:
    """Format metrics footer line for transparency."""
    parts = []

    # Tokens
    tokens = result.budget_status.tokens_used if result.budget_status else 0
    parts.append(f"tokens: {tokens}")

    # LLM calls
    llm_calls = result.budget_status.llm_calls_used if result.budget_status else 0
    parts.append(f"llm: {llm_calls}")

    # Duration
    parts.append(f"time: {result.duration_ms}ms")

    # Budget level
    parts.append(f"budget: {ctx.budget.level.value}")

    return f"[{' | '.join(parts)}]"


def format_metrics(result: CommandResult[Any], ctx: CLIContext) -> str:
    """
    Get metrics line for appending to custom output.

    Use this when a command has custom rendering but still wants metrics.
    Returns empty string if metrics are disabled.
    """
    if not ctx.show_metrics:
        return ""
    return "\n" + _format_metrics_line(result, ctx)


def with_metrics(output: str, result: CommandResult[Any], ctx: CLIContext) -> str:
    """
    Wrap custom output with metrics footer.

    Convenience function for commands with custom render() methods.
    """
    if not ctx.show_metrics:
        return output
    return output + "\n\n" + _format_metrics_line(result, ctx)


def _format_markdown(result: CommandResult[Any], agent: str) -> str:
    """Format as markdown report."""
    lines = [f"# {agent} Report", ""]

    if result.success and result.output is not None:
        lines.append("## Result")
        lines.append("")
        if isinstance(result.output, dict):
            for key, value in result.output.items():
                lines.append(f"- **{key}**: {value}")
        else:
            lines.append(str(result.output))
    elif result.error:
        lines.append("## Error")
        lines.append("")
        lines.append(f"**Code**: `{result.error.code}`")
        lines.append(f"**Message**: {result.error.message}")
        if result.error.suggestions:
            lines.append("")
            lines.append("### Suggestions")
            for suggestion in result.error.suggestions:
                lines.append(f"- {suggestion}")

    lines.append("")
    lines.append("---")
    lines.append(f"*Duration: {result.duration_ms}ms*")

    return "\n".join(lines)
