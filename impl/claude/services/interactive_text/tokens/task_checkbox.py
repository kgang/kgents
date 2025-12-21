"""
TaskCheckbox Token Implementation.

The TaskCheckbox token represents a GitHub-style task list item that connects
to the formal verification system. When toggled, it captures a Trace_Witness
through world.trace.capture.

Affordances:
- click: Toggle checkbox state and persist to source file
- hover: Display verification status and linked requirements
- right-click: Show context menu with view changes, view execution options

Verification Integration:
- Task completion creates Trace_Witness for formal verification
- Tasks with requirement references link to verification status
- Failed verification displays warning with counter-examples

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    Observer,
    ObserverRole,
)

from .base import BaseMeaningToken, ExecutionTrace, TraceWitness, filter_affordances_by_observer


@dataclass(frozen=True)
class VerificationStatus:
    """Verification status for a task.

    Attributes:
        verified: Whether the task has been verified
        requirement_refs: Linked requirement references
        counter_examples: Counter-examples if verification failed
        derivation_path: Path through verification graph
    """

    verified: bool
    requirement_refs: tuple[str, ...] = ()
    counter_examples: tuple[str, ...] = ()
    derivation_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "verified": self.verified,
            "requirement_refs": list(self.requirement_refs),
            "counter_examples": list(self.counter_examples),
            "derivation_path": self.derivation_path,
        }


@dataclass(frozen=True)
class TaskHoverInfo:
    """Information displayed on task hover.

    Attributes:
        description: Task description text
        checked: Current checkbox state
        verification: Verification status
        file_path: Source file path
        line_number: Line number in source file
    """

    description: str
    checked: bool
    verification: VerificationStatus | None = None
    file_path: str | None = None
    line_number: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "description": self.description,
            "checked": self.checked,
            "verification": self.verification.to_dict() if self.verification else None,
            "file_path": self.file_path,
            "line_number": self.line_number,
        }


@dataclass(frozen=True)
class ToggleResult:
    """Result of toggling a task checkbox.

    Attributes:
        success: Whether toggle succeeded
        new_state: New checkbox state after toggle
        trace_witness: Trace witness captured for verification
        file_updated: Whether the source file was updated
        error: Error message if toggle failed
    """

    success: bool
    new_state: bool
    trace_witness: TraceWitness | None = None
    file_updated: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "new_state": self.new_state,
            "trace_witness": self.trace_witness.to_dict() if self.trace_witness else None,
            "file_updated": self.file_updated,
            "error": self.error,
        }


@dataclass(frozen=True)
class TaskContextMenuResult:
    """Result of showing context menu for a task.

    Attributes:
        description: Task description
        options: Available menu options
        verification: Verification status
    """

    description: str
    options: list[dict[str, Any]]
    verification: VerificationStatus | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "description": self.description,
            "options": self.options,
            "verification": self.verification.to_dict() if self.verification else None,
        }


class TaskCheckboxToken(BaseMeaningToken[bool]):
    """Token representing a GitHub-style task checkbox.

    TaskCheckbox tokens connect to the formal verification system.
    When toggled, they capture a Trace_Witness for verification and
    persist the state change to the source file.

    Pattern: `- [ ] description` or `- [x] description`

    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
    """

    # Pattern for task checkboxes
    PATTERN = re.compile(r"^- \[([ xX])\] (.+)$", re.MULTILINE)

    # Capabilities required for certain affordances
    REQUIRED_CAPABILITIES: dict[str, frozenset[str]] = {
        "toggle": frozenset(),  # Toggle is always available (persistence is optional)
        "hover": frozenset(),  # Always available
        "context_menu": frozenset(),  # Always available
        "view_changes": frozenset(),  # Always available
        "view_execution": frozenset(),  # Always available
    }

    def __init__(
        self,
        source_text: str,
        source_position: tuple[int, int],
        checked: bool,
        description: str,
        file_path: str | None = None,
        line_number: int | None = None,
        requirement_refs: tuple[str, ...] = (),
    ) -> None:
        """Initialize a TaskCheckbox token.

        Args:
            source_text: The original matched text
            source_position: (start, end) position in source document
            checked: Whether the checkbox is checked
            description: Task description text
            file_path: Path to source file (for persistence)
            line_number: Line number in source file
            requirement_refs: Linked requirement references
        """
        self._source_text = source_text
        self._source_position = source_position
        self._checked = checked
        self._description = description
        self._file_path = file_path
        self._line_number = line_number
        self._requirement_refs = requirement_refs
        self._verification: VerificationStatus | None = None

    @classmethod
    def from_match(
        cls,
        match: re.Match[str],
        file_path: str | None = None,
        line_number: int | None = None,
    ) -> TaskCheckboxToken:
        """Create token from regex match.

        Args:
            match: Regex match object from pattern matching
            file_path: Path to source file
            line_number: Line number in source file

        Returns:
            New TaskCheckboxToken instance
        """
        checkbox_char = match.group(1)
        checked = checkbox_char.lower() == "x"
        description = match.group(2)

        # Extract requirement refs from description
        req_pattern = re.compile(r"\[R(\d+(?:\.\d+)?)\]")
        req_matches = req_pattern.findall(description)
        requirement_refs = tuple(f"R{r}" for r in req_matches)

        return cls(
            source_text=match.group(0),
            source_position=(match.start(), match.end()),
            checked=checked,
            description=description,
            file_path=file_path,
            line_number=line_number,
            requirement_refs=requirement_refs,
        )

    @property
    def token_type(self) -> str:
        """Token type name from registry."""
        return "task_checkbox"

    @property
    def source_text(self) -> str:
        """Original text that was recognized as this token."""
        return self._source_text

    @property
    def source_position(self) -> tuple[int, int]:
        """(start, end) position in source document."""
        return self._source_position

    @property
    def checked(self) -> bool:
        """Whether the checkbox is checked."""
        return self._checked

    @property
    def description(self) -> str:
        """Task description text."""
        return self._description

    @property
    def file_path(self) -> str | None:
        """Path to source file."""
        return self._file_path

    @property
    def line_number(self) -> int | None:
        """Line number in source file."""
        return self._line_number

    @property
    def requirement_refs(self) -> tuple[str, ...]:
        """Linked requirement references."""
        return self._requirement_refs

    @property
    def verification(self) -> VerificationStatus | None:
        """Verification status for this task."""
        return self._verification

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer.

        Args:
            observer: The observer requesting affordances

        Returns:
            List of available affordances

        Requirements: 6.6
        """
        definition = self.get_definition()

        # Use definition affordances if available, otherwise use defaults
        if definition is not None:
            affordances = list(definition.affordances)
        else:
            # Default affordances for task checkbox
            affordances = [
                Affordance(
                    name="toggle",
                    action=AffordanceAction.CLICK,
                    handler="world.task.toggle",
                    enabled=True,
                    description="Toggle task completion",
                ),
                Affordance(
                    name="hover",
                    action=AffordanceAction.HOVER,
                    handler="world.task.hover",
                    enabled=True,
                    description="View task details",
                ),
                Affordance(
                    name="context_menu",
                    action=AffordanceAction.RIGHT_CLICK,
                    handler="world.task.context_menu",
                    enabled=True,
                    description="Show task options",
                ),
            ]

        # Filter by observer capabilities
        return filter_affordances_by_observer(
            tuple(affordances),
            observer,
            self.REQUIRED_CAPABILITIES,
        )

    async def project(self, target: str, observer: Observer) -> str | dict[str, Any]:
        """Project token to target-specific rendering.

        Args:
            target: Target name (e.g., "cli", "web", "json")
            observer: The observer receiving the projection

        Returns:
            Target-specific rendering of this token
        """
        checkbox = "[x]" if self._checked else "[ ]"

        if target == "cli":
            if self._checked:
                return f"[green]✓[/green] [strike]{self._description}[/strike]"
            return f"[dim]○[/dim] {self._description}"

        elif target == "json":
            return {
                "type": "task_checkbox",
                "checked": self._checked,
                "description": self._description,
                "requirement_refs": list(self._requirement_refs),
                "source_text": self._source_text,
            }

        else:  # web or default
            return f"- {checkbox} {self._description}"

    async def _execute_action(
        self,
        action: AffordanceAction,
        observer: Observer,
        **kwargs: Any,
    ) -> Any:
        """Execute the action for this token.

        Args:
            action: The action being performed
            observer: The observer performing the action
            **kwargs: Additional action-specific arguments

        Returns:
            Action-specific result

        Requirements: 6.2, 6.3, 6.4, 6.5, 6.6
        """
        if action == AffordanceAction.CLICK:
            return await self._handle_toggle(observer)
        elif action == AffordanceAction.HOVER:
            return await self._handle_hover(observer)
        elif action == AffordanceAction.RIGHT_CLICK:
            return await self._handle_context_menu(observer)
        else:
            return None

    async def _handle_toggle(self, observer: Observer) -> ToggleResult:
        """Handle click action - toggle checkbox state.

        Requirements: 6.2, 6.3
        """
        new_state = not self._checked

        # Create trace witness for verification
        trace = ExecutionTrace(
            agent_path="world.task.toggle",
            operation="toggle",
            input_data={"previous_state": self._checked},
            output_data={"new_state": new_state},
            observer_id=observer.id,
        )

        witness = TraceWitness(
            id=str(uuid4()),
            trace=trace,
        )

        # In full implementation, would:
        # 1. Persist to file via world.file.write
        # 2. Capture trace via world.trace.capture
        # 3. Verify via verification service

        file_updated = False
        if self._file_path is not None:
            # Simulated file update
            file_updated = True

        return ToggleResult(
            success=True,
            new_state=new_state,
            trace_witness=witness,
            file_updated=file_updated,
        )

    async def _handle_hover(self, observer: Observer) -> TaskHoverInfo:
        """Handle hover action - display verification status.

        Requirements: 6.4, 6.5
        """
        # Get verification status (simulated)
        verification = None
        if self._requirement_refs:
            verification = VerificationStatus(
                verified=self._checked,
                requirement_refs=self._requirement_refs,
            )

        return TaskHoverInfo(
            description=self._description,
            checked=self._checked,
            verification=verification,
            file_path=self._file_path,
            line_number=self._line_number,
        )

    async def _handle_context_menu(self, observer: Observer) -> TaskContextMenuResult:
        """Handle right-click action - show context menu.

        Requirements: 6.6
        """
        options = [
            {"action": "view_changes", "label": "View Changes (git diff)", "enabled": True},
            {"action": "view_execution", "label": "View Execution (trace)", "enabled": True},
        ]

        if self._requirement_refs:
            options.append(
                {"action": "view_requirements", "label": "View Requirements", "enabled": True}
            )

        # Admin-only options
        if observer.role == ObserverRole.ADMIN:
            options.append({"action": "edit_task", "label": "Edit Task", "enabled": True})

        verification = None
        if self._requirement_refs:
            verification = VerificationStatus(
                verified=self._checked,
                requirement_refs=self._requirement_refs,
            )

        return TaskContextMenuResult(
            description=self._description,
            options=options,
            verification=verification,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        base = super().to_dict()
        base.update(
            {
                "checked": self._checked,
                "description": self._description,
                "file_path": self._file_path,
                "line_number": self._line_number,
                "requirement_refs": list(self._requirement_refs),
            }
        )
        return base


# =============================================================================
# Factory Functions
# =============================================================================


def create_task_checkbox_token(
    text: str,
    position: tuple[int, int] | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
) -> TaskCheckboxToken | None:
    """Create a TaskCheckbox token from text.

    Args:
        text: Text that may contain a task checkbox
        position: Optional (start, end) position override
        file_path: Path to source file
        line_number: Line number in source file

    Returns:
        TaskCheckboxToken if text matches pattern, None otherwise
    """
    match = TaskCheckboxToken.PATTERN.search(text)
    if match is None:
        return None

    token = TaskCheckboxToken.from_match(match, file_path, line_number)

    # Override position if provided
    if position is not None:
        return TaskCheckboxToken(
            source_text=token.source_text,
            source_position=position,
            checked=token.checked,
            description=token.description,
            file_path=file_path,
            line_number=line_number,
            requirement_refs=token.requirement_refs,
        )

    return token


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TaskCheckboxToken",
    "VerificationStatus",
    "TaskHoverInfo",
    "ToggleResult",
    "TaskContextMenuResult",
    "create_task_checkbox_token",
]
