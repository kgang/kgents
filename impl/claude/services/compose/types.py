"""
Composition Types: Core data structures for kg command composition.

Following the PolyAgent pattern: state machines with clear transitions.

Composition states:
    PENDING → RUNNING → COMPLETED | FAILED

Step dependencies:
    Default: sequential (step N depends on step N-1)
    Custom: specify explicit dependencies by index
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


def generate_composition_id() -> str:
    """Generate unique composition ID."""
    return f"comp-{uuid4().hex[:12]}"


class CompositionStatus(Enum):
    """Status of a composition execution."""

    PENDING = "pending"  # Not started
    RUNNING = "running"  # Currently executing
    COMPLETED = "completed"  # All steps succeeded
    FAILED = "failed"  # One or more steps failed


@dataclass
class CompositionStep:
    """
    A single step in a composition.

    Steps can have dependencies on other steps. Default is sequential
    (step N depends on step N-1), but can be customized.
    """

    index: int
    command: str  # Raw command string (e.g., "audit spec/foo.md --principles")
    depends_on: list[int] = field(default_factory=list)  # Step indices this depends on

    def __post_init__(self) -> None:
        """Set default dependency: previous step."""
        if not self.depends_on and self.index > 0:
            self.depends_on = [self.index - 1]


@dataclass
class StepResult:
    """Result of executing a single step."""

    step_index: int
    success: bool
    output: str
    duration_ms: float
    mark_id: str | None = None  # Mark created by this step (if any)
    skipped: bool = False  # True if skipped due to failed dependencies
    error: str | None = None  # Error message if failed


@dataclass
class Composition:
    """
    A composition of kg commands with unified tracing.

    The composition tracks:
    - Individual steps and their dependencies
    - Execution results for each step
    - Unified trace linking all step marks
    - Overall status (pending → running → completed/failed)

    Pattern: This is a PolyAgent state machine where the state is status.
    """

    id: str
    name: str | None  # Named compositions can be saved and reused
    steps: list[CompositionStep]
    status: CompositionStatus = CompositionStatus.PENDING
    results: list[StepResult] = field(default_factory=list)
    trace_id: str | None = None  # Unified trace linking all step marks

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    author: str = "claude-code"  # Who created this composition

    @property
    def all_succeeded(self) -> bool:
        """Check if all steps succeeded."""
        if not self.results:
            return False
        return all(r.success or r.skipped for r in self.results)

    @property
    def any_failed(self) -> bool:
        """Check if any step failed."""
        return any(r.success is False for r in self.results)

    @property
    def duration_ms(self) -> float:
        """Total duration of all steps."""
        return sum(r.duration_ms for r in self.results)

    @property
    def success_count(self) -> int:
        """Count of successful steps."""
        return sum(1 for r in self.results if r.success)

    @property
    def failure_count(self) -> int:
        """Count of failed steps."""
        return sum(1 for r in self.results if r.success is False)

    @property
    def skipped_count(self) -> int:
        """Count of skipped steps."""
        return sum(1 for r in self.results if r.skipped)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "steps": [
                {"index": s.index, "command": s.command, "depends_on": s.depends_on}
                for s in self.steps
            ],
            "results": [
                {
                    "step_index": r.step_index,
                    "success": r.success,
                    "output": r.output[:500],  # Truncate long outputs
                    "duration_ms": r.duration_ms,
                    "mark_id": r.mark_id,
                    "skipped": r.skipped,
                    "error": r.error,
                }
                for r in self.results
            ],
            "trace_id": self.trace_id,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "author": self.author,
            "duration_ms": self.duration_ms,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "skipped_count": self.skipped_count,
        }

    def to_yaml(self) -> str:
        """Convert to YAML for export."""
        import yaml

        data = {
            "name": self.name,
            "steps": [s.command for s in self.steps],
        }
        return yaml.dump(data, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yaml_str: str, author: str = "claude-code") -> Composition:
        """Create a composition from YAML."""
        import yaml

        data = yaml.safe_load(yaml_str)
        name = data.get("name")
        steps = data.get("steps", [])

        return cls.from_commands(steps, name=name, author=author)

    @classmethod
    def from_commands(
        cls,
        commands: list[str],
        name: str | None = None,
        author: str = "claude-code",
    ) -> Composition:
        """Create a composition from a list of command strings."""
        steps = [CompositionStep(index=i, command=cmd) for i, cmd in enumerate(commands)]
        return cls(
            id=generate_composition_id(),
            name=name,
            steps=steps,
            author=author,
        )
