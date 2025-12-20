"""
Task Tools: Session-Scoped Task State Management.

Phase 3 of U-gent Tooling: Orchestration tools for workflow coordination.

TodoTool manages task state with key constraints:
- Session-scoped: tasks live only within the current session
- Single in_progress: exactly ONE task can be in_progress at a time
- Two forms: content (imperative "Run tests"), activeForm (continuous "Running tests")

This aligns with Claude Code's TodoWrite tool behavior where:
- Tasks track multi-step work
- Status transitions are explicit
- Only one task "in flight" at a time

Category Laws (verified):
    Identity: Id >> TodoTool == TodoTool == TodoTool >> Id
    Associativity: (f >> g) >> h == f >> (g >> h)

See: plans/ugent-tooling-phase3-handoff.md
See: docs/skills/crown-jewel-patterns.md (Pattern 1: Container Owns Workflow)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..base import Tool, ToolCategory, ToolError
from ..contracts import (
    TodoCreateRequest,
    TodoCreateResponse,
    TodoItem,
    TodoListRequest,
    TodoListResponse,
    TodoUpdateRequest,
    TodoUpdateResponse,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Task State Machine
# =============================================================================


class TaskStatus(Enum):
    """
    Task status states.

    State machine:
        PENDING ──start──> IN_PROGRESS ──complete──> COMPLETED
                              │
                              └──abandon──> PENDING (reset)
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    @classmethod
    def from_string(cls, value: str) -> "TaskStatus":
        """Parse status from string (case-insensitive)."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Invalid status: {value}. Must be: pending, in_progress, completed")


# =============================================================================
# Session-Scoped Task Store
# =============================================================================


@dataclass
class TaskStore:
    """
    Session-scoped task storage.

    Key invariant: At most ONE task can be in_progress at any time.

    This is a session-local store (not shared across sessions).
    For persistence across sessions, integrate with DataBus.
    """

    tasks: list[TodoItem] = field(default_factory=list)

    def get_in_progress_count(self) -> int:
        """Count tasks currently in_progress."""
        return sum(1 for t in self.tasks if t.status == TaskStatus.IN_PROGRESS.value)

    def get_in_progress_index(self) -> int | None:
        """Get index of in_progress task, or None if none."""
        for i, task in enumerate(self.tasks):
            if task.status == TaskStatus.IN_PROGRESS.value:
                return i
        return None

    def validate_single_in_progress(self, new_status: str, skip_index: int | None = None) -> None:
        """
        Validate that setting new_status won't violate single in_progress constraint.

        Raises:
            ToolError: If constraint would be violated
        """
        if new_status != TaskStatus.IN_PROGRESS.value:
            return  # Only in_progress transitions need validation

        for i, task in enumerate(self.tasks):
            if skip_index is not None and i == skip_index:
                continue  # Skip the task being updated
            if task.status == TaskStatus.IN_PROGRESS.value:
                raise ToolError(
                    f"Cannot set task to in_progress: task {i} ('{task.content}') is already in_progress. "
                    f"Complete or abandon the current task first.",
                    "task.update",
                )

    def clear(self) -> None:
        """Clear all tasks (for session reset)."""
        self.tasks.clear()


# Singleton for session scope (can be replaced via DI for testing)
_task_store: TaskStore | None = None


def get_task_store() -> TaskStore:
    """Get or create the session task store."""
    global _task_store
    if _task_store is None:
        _task_store = TaskStore()
    return _task_store


def reset_task_store() -> None:
    """Reset the task store (for testing)."""
    global _task_store
    _task_store = None


def set_task_store(store: TaskStore) -> None:
    """Inject a task store (for testing)."""
    global _task_store
    _task_store = store


# =============================================================================
# TodoListTool: Read Tasks
# =============================================================================


@dataclass
class TodoListTool(Tool[TodoListRequest, TodoListResponse]):
    """
    List current tasks with optional status filter.

    Trust Level: L0 (read-only)
    Effects: None (pure query)
    Cacheable: False (live state)
    """

    _store: TaskStore | None = None

    def __post_init__(self) -> None:
        if self._store is None:
            self._store = get_task_store()

    @property
    def name(self) -> str:
        return "task.list"

    @property
    def description(self) -> str:
        return "List current tasks with optional status filter"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def trust_required(self) -> int:
        return 0  # L0 - Read-only

    async def invoke(self, request: TodoListRequest) -> TodoListResponse:
        """
        List tasks, optionally filtered by status.

        Args:
            request: TodoListRequest with optional status_filter

        Returns:
            TodoListResponse with tasks and count
        """
        assert self._store is not None

        tasks = self._store.tasks

        # Apply status filter if provided
        if request.status_filter:
            try:
                target_status = TaskStatus.from_string(request.status_filter)
                tasks = [t for t in tasks if t.status == target_status.value]
            except ValueError as e:
                raise ToolError(str(e), self.name) from e

        return TodoListResponse(
            todos=list(tasks),  # Copy to prevent mutation
            count=len(tasks),
        )


# =============================================================================
# TodoCreateTool: Create Tasks
# =============================================================================


@dataclass
class TodoCreateTool(Tool[TodoCreateRequest, TodoCreateResponse]):
    """
    Create new tasks from a todo list.

    Enforces single in_progress constraint:
    - If input contains multiple in_progress tasks, raises error
    - If store already has in_progress and input adds another, raises error

    Trust Level: L0 (orchestration metadata)
    Effects: None (session state, not filesystem)
    """

    _store: TaskStore | None = None

    def __post_init__(self) -> None:
        if self._store is None:
            self._store = get_task_store()

    @property
    def name(self) -> str:
        return "task.create"

    @property
    def description(self) -> str:
        return "Create new tasks (replaces existing list)"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def trust_required(self) -> int:
        return 0  # L0 - Orchestration metadata

    async def invoke(self, request: TodoCreateRequest) -> TodoCreateResponse:
        """
        Create tasks, replacing the current list.

        Validates:
        - All statuses are valid
        - At most one task is in_progress

        Args:
            request: TodoCreateRequest with list of TodoItems

        Returns:
            TodoCreateResponse with success and count
        """
        assert self._store is not None

        # Validate statuses
        in_progress_count = 0
        for i, todo in enumerate(request.todos):
            try:
                status = TaskStatus.from_string(todo.status)
                if status == TaskStatus.IN_PROGRESS:
                    in_progress_count += 1
                    if in_progress_count > 1:
                        raise ToolError(
                            f"Multiple in_progress tasks detected. Task {i} ('{todo.content}') "
                            f"would be the {in_progress_count}th in_progress task. "
                            f"Only ONE task can be in_progress at a time.",
                            self.name,
                        )
            except ValueError as e:
                raise ToolError(f"Task {i}: {e}", self.name) from e

        # Replace task list
        self._store.tasks = list(request.todos)  # Copy to own

        logger.debug(f"Created {len(request.todos)} tasks")

        return TodoCreateResponse(
            success=True,
            count=len(request.todos),
        )


# =============================================================================
# TodoUpdateTool: Update Task Status
# =============================================================================


@dataclass
class TodoUpdateTool(Tool[TodoUpdateRequest, TodoUpdateResponse]):
    """
    Update a task's status by index.

    Enforces single in_progress constraint:
    - Transition to in_progress fails if another task is already in_progress

    Trust Level: L0 (orchestration metadata)
    Effects: None (session state, not filesystem)
    """

    _store: TaskStore | None = None

    def __post_init__(self) -> None:
        if self._store is None:
            self._store = get_task_store()

    @property
    def name(self) -> str:
        return "task.update"

    @property
    def description(self) -> str:
        return "Update task status by index"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def trust_required(self) -> int:
        return 0  # L0 - Orchestration metadata

    async def invoke(self, request: TodoUpdateRequest) -> TodoUpdateResponse:
        """
        Update a task's status.

        Args:
            request: TodoUpdateRequest with index and new status

        Returns:
            TodoUpdateResponse with success and updated task

        Raises:
            ToolError: If index out of range, invalid status, or constraint violation
        """
        assert self._store is not None

        # Validate index
        if request.index < 0 or request.index >= len(self._store.tasks):
            raise ToolError(
                f"Task index {request.index} out of range. "
                f"Valid indices: 0-{len(self._store.tasks) - 1}",
                self.name,
            )

        # Validate status
        try:
            new_status = TaskStatus.from_string(request.status)
        except ValueError as e:
            raise ToolError(str(e), self.name) from e

        # Validate single in_progress constraint
        self._store.validate_single_in_progress(
            new_status.value,
            skip_index=request.index,
        )

        # Update the task
        old_task = self._store.tasks[request.index]
        updated_task = TodoItem(
            content=old_task.content,
            status=new_status.value,
            active_form=old_task.active_form,
        )
        self._store.tasks[request.index] = updated_task

        logger.debug(f"Updated task {request.index}: {old_task.status} → {new_status.value}")

        return TodoUpdateResponse(
            success=True,
            todo=updated_task,
        )


# =============================================================================
# Convenience: Combined TodoTool
# =============================================================================


@dataclass
class TodoTool(Tool[TodoListRequest, TodoListResponse]):
    """
    Convenience alias for TodoListTool.

    For full CRUD, use:
    - TodoListTool: List tasks
    - TodoCreateTool: Create/replace tasks
    - TodoUpdateTool: Update task status
    """

    _delegate: TodoListTool | None = None

    def __post_init__(self) -> None:
        if self._delegate is None:
            self._delegate = TodoListTool()

    @property
    def name(self) -> str:
        return "task.list"

    @property
    def description(self) -> str:
        return "List current tasks (alias for TodoListTool)"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def trust_required(self) -> int:
        return 0

    async def invoke(self, request: TodoListRequest) -> TodoListResponse:
        assert self._delegate is not None
        return await self._delegate.invoke(request)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # State
    "TaskStatus",
    "TaskStore",
    "get_task_store",
    "reset_task_store",
    "set_task_store",
    # Tools
    "TodoListTool",
    "TodoCreateTool",
    "TodoUpdateTool",
    "TodoTool",
]
