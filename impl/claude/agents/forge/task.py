"""
ForgeTask: Typed Task Interface for Coalition Forge.

A ForgeTask defines what needs to be done, who should do it,
and how the output should be formatted. Tasks are the contracts
that coalitions fulfill.

Design Principle (from Morton):
    The task is not a specification—it is a coordination protocol.
    It tells agents how to relate to each other.

Key Types:
    - ForgeTask: Protocol defining task interface
    - TaskTemplate: Reusable task definitions with coalition shapes
    - OutputFormat: What form the deliverable takes
    - CoalitionShape: Which archetypes are required

See: plans/core-apps/coalition-forge.md
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, ClassVar, Protocol, TypeVar, runtime_checkable
from uuid import uuid4

# =============================================================================
# Output Formats
# =============================================================================


class OutputFormat(Enum):
    """
    Format of task deliverables.

    Each format implies different rendering and quality expectations.
    """

    MARKDOWN = auto()  # Structured markdown document
    PR_COMMENTS = auto()  # GitHub PR-style inline comments
    MATRIX = auto()  # Pros/cons or comparison matrix
    BRIEFING = auto()  # Executive briefing document
    MULTI_FORMAT = auto()  # Multiple formats (user chooses)
    JSON = auto()  # Structured JSON data
    CODE = auto()  # Source code output
    SLIDES = auto()  # Presentation slides


# =============================================================================
# Handoff Pattern
# =============================================================================


class HandoffPattern(Enum):
    """
    How work flows between agents in a coalition.

    SEQUENTIAL: A → B → C (strict order)
    PARALLEL: A || B || C → Merge (concurrent then merge)
    HUB_AND_SPOKE: Hub ↔ Spokes (coordinator mediates)
    ITERATIVE: A ↔ B (back and forth until convergence)
    PIPELINE: A >> B >> C (streaming pipeline)
    """

    SEQUENTIAL = auto()
    PARALLEL = auto()
    HUB_AND_SPOKE = auto()
    ITERATIVE = auto()
    PIPELINE = auto()


# =============================================================================
# Coalition Shape
# =============================================================================


@dataclass(frozen=True)
class CoalitionShape:
    """
    Defines which builder archetypes are needed for a task.

    The shape is not just a list—it encodes coordination structure:
    - required: Must have these archetypes
    - lead: Who coordinates (defaults to first required)
    - pattern: How they hand off work
    - min_eigenvector: Minimum capability thresholds

    Example:
        research_shape = CoalitionShape(
            required=("Scout", "Sage"),
            optional=("Spark",),
            lead="Scout",
            pattern=HandoffPattern.SEQUENTIAL,
        )
    """

    required: tuple[str, ...]  # Required archetype names
    optional: tuple[str, ...] = ()  # Optional archetypes
    lead: str | None = None  # Coordinating archetype
    pattern: HandoffPattern = HandoffPattern.SEQUENTIAL
    min_eigenvector: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate shape configuration."""
        if not self.required:
            raise ValueError("Coalition must have at least one required archetype")

    @property
    def effective_lead(self) -> str:
        """Get the lead archetype (defaults to first required)."""
        return self.lead or self.required[0]

    @property
    def all_archetypes(self) -> tuple[str, ...]:
        """Get all archetypes (required + optional)."""
        return self.required + self.optional

    @property
    def min_size(self) -> int:
        """Minimum coalition size (required only)."""
        return len(self.required)

    @property
    def max_size(self) -> int:
        """Maximum coalition size (required + optional)."""
        return len(self.required) + len(self.optional)

    def validate_coalition(self, archetypes: tuple[str, ...]) -> tuple[bool, str]:
        """
        Check if a coalition meets this shape's requirements.

        Returns:
            (is_valid, error_message)
        """
        missing = set(self.required) - set(archetypes)
        if missing:
            return False, f"Missing required archetypes: {missing}"

        # Check eigenvector thresholds would happen at runtime
        # when we have actual builder instances
        return True, ""


# =============================================================================
# Task Input/Output Types
# =============================================================================


@dataclass(frozen=True)
class TaskInput:
    """
    Input specification for a task.

    Captures what the user provides to initiate the task.
    """

    description: str  # Natural language task description
    context: dict[str, Any] = field(default_factory=dict)  # Additional context
    constraints: tuple[str, ...] = ()  # User-specified constraints
    preferences: dict[str, Any] = field(default_factory=dict)  # User preferences

    # Optional structured fields
    target: str | None = None  # Target entity (repo, company, etc.)
    scope: str | None = None  # Scope limit (e.g., "last 30 days")
    depth: str = "standard"  # "quick", "standard", "deep"


@dataclass
class TaskOutput:
    """
    Output produced by a completed task.

    Captures the deliverable and metadata about execution.
    """

    content: Any  # The actual output
    format: OutputFormat  # How it's formatted
    summary: str = ""  # Brief summary
    artifacts: list[dict[str, Any]] = field(
        default_factory=list
    )  # Additional artifacts

    # Execution metadata
    coalition_used: tuple[str, ...] = ()  # Which archetypes participated
    handoffs: int = 0  # Number of handoffs
    duration_seconds: float = 0.0
    credits_spent: int = 0

    # Quality signals
    confidence: float = 0.0  # 0.0-1.0 confidence score
    coverage: float = 0.0  # 0.0-1.0 coverage of requested scope
    warnings: tuple[str, ...] = ()  # Any warnings or caveats


# =============================================================================
# ForgeTask Protocol
# =============================================================================


InputT = TypeVar("InputT", bound=TaskInput, contravariant=True)
OutputT = TypeVar("OutputT", bound=TaskOutput, covariant=True)


@runtime_checkable
class ForgeTask(Protocol[InputT, OutputT]):
    """
    Protocol defining the interface for executable tasks.

    A ForgeTask is the contract between user intent and coalition action.
    It specifies:
    - What input is expected
    - What output will be produced
    - What coalition shape is required
    - What it costs

    From the spec (coalition-forge.md):
        "ForgeTask Protocol: input typing, output format, credit cost, coalition shape"

    Example Implementation:
        @dataclass
        class ResearchReportTask:
            template_id: str = "research_report"
            base_credits: int = 50
            output_format: OutputFormat = OutputFormat.MARKDOWN
            coalition_shape: CoalitionShape = RESEARCH_SHAPE

            async def execute(
                self,
                input: TaskInput,
                coalition: Coalition,
            ) -> TaskOutput:
                ...
    """

    # Class-level configuration
    template_id: ClassVar[str]  # Unique template identifier
    name: ClassVar[str]  # Human-readable name
    description: ClassVar[str]  # What this task does
    base_credits: ClassVar[int]  # Base credit cost
    output_format: ClassVar[OutputFormat]  # Output format
    coalition_shape: ClassVar[CoalitionShape]  # Required coalition

    @abstractmethod
    async def execute(
        self,
        input: InputT,
        coalition: Any,  # Coalition instance (forward ref)
    ) -> OutputT:
        """
        Execute the task with the given coalition.

        Args:
            input: Task input specification
            coalition: The coalition of builders

        Returns:
            Task output with deliverable and metadata
        """
        ...

    @abstractmethod
    def estimate_credits(self, input: InputT) -> int:
        """
        Estimate credit cost for this input.

        Args:
            input: Task input specification

        Returns:
            Estimated credits (may vary from actual)
        """
        ...

    @abstractmethod
    def validate_input(self, input: InputT) -> tuple[bool, list[str]]:
        """
        Validate input before execution.

        Returns:
            (is_valid, list of error messages)
        """
        ...

    @abstractmethod
    def suggest_coalition(self, input: InputT) -> CoalitionShape:
        """
        Suggest optimal coalition shape for this input.

        May adjust the base coalition_shape based on input characteristics.
        """
        ...


# =============================================================================
# Task Instance (Runtime)
# =============================================================================


@dataclass
class ForgeTaskInstance:
    """
    A specific instance of a task ready for execution.

    While TaskTemplate defines the blueprint, ForgeTaskInstance is
    the actual task being executed with specific input.
    """

    id: str
    template_id: str
    input: TaskInput
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, running, completed, failed
    output: TaskOutput | None = None
    error: str | None = None

    # Execution tracking
    started_at: datetime | None = None
    completed_at: datetime | None = None
    coalition_id: str | None = None

    @classmethod
    def create(cls, template_id: str, input: TaskInput) -> ForgeTaskInstance:
        """Factory for creating task instances."""
        return cls(
            id=str(uuid4())[:8],
            template_id=template_id,
            input=input,
        )

    @property
    def duration_seconds(self) -> float:
        """Execution duration in seconds."""
        if self.started_at is None:
            return 0.0
        end = self.completed_at or datetime.now()
        return (end - self.started_at).total_seconds()

    def start(self, coalition_id: str) -> None:
        """Mark task as started."""
        self.status = "running"
        self.started_at = datetime.now()
        self.coalition_id = coalition_id

    def complete(self, output: TaskOutput) -> None:
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()
        self.output = output

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.status = "failed"
        self.completed_at = datetime.now()
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "template_id": self.template_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "duration_seconds": self.duration_seconds,
            "coalition_id": self.coalition_id,
            "error": self.error,
        }


# =============================================================================
# Credit Calculation
# =============================================================================


def calculate_credits(
    base_credits: int,
    input: TaskInput,
    coalition_shape: CoalitionShape,
) -> int:
    """
    Calculate estimated credits for a task.

    Factors:
    - Base credits (from template)
    - Input depth modifier
    - Coalition size modifier
    - Context complexity
    """
    credits = base_credits

    # Depth modifier
    depth_modifiers = {
        "quick": 0.5,
        "standard": 1.0,
        "deep": 2.0,
    }
    credits = int(credits * depth_modifiers.get(input.depth, 1.0))

    # Coalition size modifier (more agents = more credits)
    size = len(coalition_shape.required) + len(coalition_shape.optional) // 2
    if size > 3:
        credits = int(credits * (1 + (size - 3) * 0.1))

    # Context complexity (more context = more processing)
    if len(input.context) > 5:
        credits = int(credits * 1.1)

    return credits


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "OutputFormat",
    "HandoffPattern",
    # Data classes
    "CoalitionShape",
    "TaskInput",
    "TaskOutput",
    "ForgeTaskInstance",
    # Protocol
    "ForgeTask",
    # Utilities
    "calculate_credits",
]
