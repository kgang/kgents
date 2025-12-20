"""
Tests for Task Tools: Session-Scoped Task State Management.

Covers:
- TodoListTool: Listing and filtering tasks
- TodoCreateTool: Creating tasks with constraint validation
- TodoUpdateTool: Updating status with single in_progress enforcement
- TaskStore: Session-scoped storage mechanics

Key constraint tested: Only ONE task can be in_progress at a time.

See: services/tooling/tools/task.py
"""

from __future__ import annotations

import pytest

from services.tooling.base import ToolCategory, ToolError
from services.tooling.contracts import (
    TodoCreateRequest,
    TodoItem,
    TodoListRequest,
    TodoUpdateRequest,
)
from services.tooling.tools.task import (
    TaskStatus,
    TaskStore,
    TodoCreateTool,
    TodoListTool,
    TodoTool,
    TodoUpdateTool,
    get_task_store,
    reset_task_store,
    set_task_store,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def task_store() -> TaskStore:
    """Fresh task store for each test."""
    store = TaskStore()
    set_task_store(store)
    yield store
    reset_task_store()


@pytest.fixture
def list_tool(task_store: TaskStore) -> TodoListTool:
    """TodoListTool with fresh store."""
    return TodoListTool(_store=task_store)


@pytest.fixture
def create_tool(task_store: TaskStore) -> TodoCreateTool:
    """TodoCreateTool with fresh store."""
    return TodoCreateTool(_store=task_store)


@pytest.fixture
def update_tool(task_store: TaskStore) -> TodoUpdateTool:
    """TodoUpdateTool with fresh store."""
    return TodoUpdateTool(_store=task_store)


# =============================================================================
# TaskStatus Tests
# =============================================================================


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_from_string_valid(self) -> None:
        """Valid status strings parse correctly."""
        assert TaskStatus.from_string("pending") == TaskStatus.PENDING
        assert TaskStatus.from_string("in_progress") == TaskStatus.IN_PROGRESS
        assert TaskStatus.from_string("completed") == TaskStatus.COMPLETED

    def test_from_string_case_insensitive(self) -> None:
        """Status parsing is case-insensitive."""
        assert TaskStatus.from_string("PENDING") == TaskStatus.PENDING
        assert TaskStatus.from_string("In_Progress") == TaskStatus.IN_PROGRESS
        assert TaskStatus.from_string("COMPLETED") == TaskStatus.COMPLETED

    def test_from_string_invalid(self) -> None:
        """Invalid status strings raise ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            TaskStatus.from_string("unknown")


# =============================================================================
# TaskStore Tests
# =============================================================================


class TestTaskStore:
    """Tests for TaskStore session storage."""

    def test_empty_store(self, task_store: TaskStore) -> None:
        """Fresh store is empty."""
        assert len(task_store.tasks) == 0
        assert task_store.get_in_progress_count() == 0
        assert task_store.get_in_progress_index() is None

    def test_in_progress_tracking(self, task_store: TaskStore) -> None:
        """Store tracks in_progress task correctly."""
        task_store.tasks = [
            TodoItem(content="Task 1", status="pending", active_form="Doing task 1"),
            TodoItem(content="Task 2", status="in_progress", active_form="Doing task 2"),
            TodoItem(content="Task 3", status="completed", active_form="Doing task 3"),
        ]

        assert task_store.get_in_progress_count() == 1
        assert task_store.get_in_progress_index() == 1

    def test_validate_single_in_progress_allows_non_in_progress(
        self, task_store: TaskStore
    ) -> None:
        """Validation passes for pending/completed transitions."""
        task_store.tasks = [
            TodoItem(content="Current", status="in_progress", active_form="Doing"),
        ]

        # Should not raise
        task_store.validate_single_in_progress("pending")
        task_store.validate_single_in_progress("completed")

    def test_validate_single_in_progress_blocks_duplicate(self, task_store: TaskStore) -> None:
        """Validation blocks second in_progress."""
        task_store.tasks = [
            TodoItem(content="Current", status="in_progress", active_form="Doing"),
            TodoItem(content="Another", status="pending", active_form="Doing another"),
        ]

        with pytest.raises(ToolError, match="already in_progress"):
            task_store.validate_single_in_progress("in_progress")

    def test_validate_single_in_progress_allows_same_task(self, task_store: TaskStore) -> None:
        """Validation allows same task to stay in_progress."""
        task_store.tasks = [
            TodoItem(content="Current", status="in_progress", active_form="Doing"),
        ]

        # Should not raise when updating the same task
        task_store.validate_single_in_progress("in_progress", skip_index=0)

    def test_clear(self, task_store: TaskStore) -> None:
        """Clear removes all tasks."""
        task_store.tasks = [
            TodoItem(content="Task", status="pending", active_form="Doing"),
        ]
        task_store.clear()
        assert len(task_store.tasks) == 0


# =============================================================================
# TodoListTool Tests
# =============================================================================


class TestTodoListTool:
    """Tests for TodoListTool."""

    def test_properties(self, list_tool: TodoListTool) -> None:
        """Tool has correct properties."""
        assert list_tool.name == "task.list"
        assert list_tool.category == ToolCategory.ORCHESTRATION
        assert list_tool.trust_required == 0  # L0 read-only

    async def test_list_empty(self, list_tool: TodoListTool) -> None:
        """Empty store returns empty list."""
        response = await list_tool.invoke(TodoListRequest())
        assert response.todos == []
        assert response.count == 0

    async def test_list_all(self, list_tool: TodoListTool, task_store: TaskStore) -> None:
        """List returns all tasks without filter."""
        task_store.tasks = [
            TodoItem(content="Task 1", status="pending", active_form="Doing 1"),
            TodoItem(content="Task 2", status="in_progress", active_form="Doing 2"),
            TodoItem(content="Task 3", status="completed", active_form="Doing 3"),
        ]

        response = await list_tool.invoke(TodoListRequest())
        assert response.count == 3
        assert len(response.todos) == 3

    async def test_list_with_filter(self, list_tool: TodoListTool, task_store: TaskStore) -> None:
        """List filters by status."""
        task_store.tasks = [
            TodoItem(content="Task 1", status="pending", active_form="Doing 1"),
            TodoItem(content="Task 2", status="in_progress", active_form="Doing 2"),
            TodoItem(content="Task 3", status="completed", active_form="Doing 3"),
        ]

        # Filter by pending
        response = await list_tool.invoke(TodoListRequest(status_filter="pending"))
        assert response.count == 1
        assert response.todos[0].content == "Task 1"

        # Filter by in_progress
        response = await list_tool.invoke(TodoListRequest(status_filter="in_progress"))
        assert response.count == 1
        assert response.todos[0].content == "Task 2"

    async def test_list_invalid_filter(self, list_tool: TodoListTool) -> None:
        """Invalid filter raises ToolError."""
        with pytest.raises(ToolError, match="Invalid status"):
            await list_tool.invoke(TodoListRequest(status_filter="invalid"))


# =============================================================================
# TodoCreateTool Tests
# =============================================================================


class TestTodoCreateTool:
    """Tests for TodoCreateTool."""

    def test_properties(self, create_tool: TodoCreateTool) -> None:
        """Tool has correct properties."""
        assert create_tool.name == "task.create"
        assert create_tool.category == ToolCategory.ORCHESTRATION
        assert create_tool.trust_required == 0

    async def test_create_tasks(self, create_tool: TodoCreateTool, task_store: TaskStore) -> None:
        """Creating tasks populates the store."""
        todos = [
            TodoItem(content="Task 1", status="pending", active_form="Doing 1"),
            TodoItem(content="Task 2", status="pending", active_form="Doing 2"),
        ]

        response = await create_tool.invoke(TodoCreateRequest(todos=todos))

        assert response.success
        assert response.count == 2
        assert len(task_store.tasks) == 2

    async def test_create_replaces_existing(
        self, create_tool: TodoCreateTool, task_store: TaskStore
    ) -> None:
        """Creating tasks replaces existing list."""
        task_store.tasks = [
            TodoItem(content="Old", status="pending", active_form="Doing old"),
        ]

        todos = [
            TodoItem(content="New", status="pending", active_form="Doing new"),
        ]

        response = await create_tool.invoke(TodoCreateRequest(todos=todos))

        assert response.success
        assert len(task_store.tasks) == 1
        assert task_store.tasks[0].content == "New"

    async def test_create_allows_one_in_progress(
        self, create_tool: TodoCreateTool, task_store: TaskStore
    ) -> None:
        """Creating with one in_progress is allowed."""
        todos = [
            TodoItem(content="Pending", status="pending", active_form="Doing pending"),
            TodoItem(content="Active", status="in_progress", active_form="Doing active"),
        ]

        response = await create_tool.invoke(TodoCreateRequest(todos=todos))

        assert response.success
        assert task_store.get_in_progress_count() == 1

    async def test_create_blocks_multiple_in_progress(self, create_tool: TodoCreateTool) -> None:
        """Creating with multiple in_progress is blocked."""
        todos = [
            TodoItem(content="Active 1", status="in_progress", active_form="Doing 1"),
            TodoItem(content="Active 2", status="in_progress", active_form="Doing 2"),
        ]

        with pytest.raises(ToolError, match="Multiple in_progress"):
            await create_tool.invoke(TodoCreateRequest(todos=todos))

    async def test_create_invalid_status(self, create_tool: TodoCreateTool) -> None:
        """Creating with invalid status raises error."""
        todos = [
            TodoItem(content="Bad", status="invalid", active_form="Doing bad"),
        ]

        with pytest.raises(ToolError, match="Invalid status"):
            await create_tool.invoke(TodoCreateRequest(todos=todos))


# =============================================================================
# TodoUpdateTool Tests
# =============================================================================


class TestTodoUpdateTool:
    """Tests for TodoUpdateTool."""

    def test_properties(self, update_tool: TodoUpdateTool) -> None:
        """Tool has correct properties."""
        assert update_tool.name == "task.update"
        assert update_tool.category == ToolCategory.ORCHESTRATION
        assert update_tool.trust_required == 0

    async def test_update_status(self, update_tool: TodoUpdateTool, task_store: TaskStore) -> None:
        """Updating status works correctly."""
        task_store.tasks = [
            TodoItem(content="Task", status="pending", active_form="Doing task"),
        ]

        response = await update_tool.invoke(TodoUpdateRequest(index=0, status="in_progress"))

        assert response.success
        assert response.todo is not None
        assert response.todo.status == "in_progress"
        assert task_store.tasks[0].status == "in_progress"

    async def test_update_preserves_content(
        self, update_tool: TodoUpdateTool, task_store: TaskStore
    ) -> None:
        """Update preserves content and active_form."""
        task_store.tasks = [
            TodoItem(content="My Task", status="pending", active_form="Doing my task"),
        ]

        response = await update_tool.invoke(TodoUpdateRequest(index=0, status="completed"))

        assert response.todo is not None
        assert response.todo.content == "My Task"
        assert response.todo.active_form == "Doing my task"
        assert response.todo.status == "completed"

    async def test_update_index_out_of_range(
        self, update_tool: TodoUpdateTool, task_store: TaskStore
    ) -> None:
        """Update with out-of-range index raises error."""
        task_store.tasks = [
            TodoItem(content="Task", status="pending", active_form="Doing"),
        ]

        with pytest.raises(ToolError, match="out of range"):
            await update_tool.invoke(TodoUpdateRequest(index=5, status="completed"))

        with pytest.raises(ToolError, match="out of range"):
            await update_tool.invoke(TodoUpdateRequest(index=-1, status="completed"))

    async def test_update_invalid_status(
        self, update_tool: TodoUpdateTool, task_store: TaskStore
    ) -> None:
        """Update with invalid status raises error."""
        task_store.tasks = [
            TodoItem(content="Task", status="pending", active_form="Doing"),
        ]

        with pytest.raises(ToolError, match="Invalid status"):
            await update_tool.invoke(TodoUpdateRequest(index=0, status="invalid"))

    async def test_update_blocks_second_in_progress(
        self, update_tool: TodoUpdateTool, task_store: TaskStore
    ) -> None:
        """Cannot set second task to in_progress."""
        task_store.tasks = [
            TodoItem(content="Active", status="in_progress", active_form="Doing 1"),
            TodoItem(content="Pending", status="pending", active_form="Doing 2"),
        ]

        with pytest.raises(ToolError, match="already in_progress"):
            await update_tool.invoke(TodoUpdateRequest(index=1, status="in_progress"))

    async def test_update_allows_completing_in_progress(
        self, update_tool: TodoUpdateTool, task_store: TaskStore
    ) -> None:
        """Can complete an in_progress task."""
        task_store.tasks = [
            TodoItem(content="Active", status="in_progress", active_form="Doing"),
        ]

        response = await update_tool.invoke(TodoUpdateRequest(index=0, status="completed"))

        assert response.success
        assert task_store.tasks[0].status == "completed"

    async def test_update_allows_new_in_progress_after_complete(
        self, update_tool: TodoUpdateTool, task_store: TaskStore
    ) -> None:
        """After completing task, can start new one."""
        task_store.tasks = [
            TodoItem(content="First", status="in_progress", active_form="Doing 1"),
            TodoItem(content="Second", status="pending", active_form="Doing 2"),
        ]

        # Complete first
        await update_tool.invoke(TodoUpdateRequest(index=0, status="completed"))

        # Now can start second
        response = await update_tool.invoke(TodoUpdateRequest(index=1, status="in_progress"))

        assert response.success
        assert task_store.tasks[1].status == "in_progress"


# =============================================================================
# TodoTool (Alias) Tests
# =============================================================================


class TestTodoTool:
    """Tests for TodoTool convenience alias."""

    async def test_is_list_alias(self, task_store: TaskStore) -> None:
        """TodoTool behaves as TodoListTool alias."""
        tool = TodoTool()
        set_task_store(task_store)

        task_store.tasks = [
            TodoItem(content="Task", status="pending", active_form="Doing"),
        ]

        response = await tool.invoke(TodoListRequest())
        assert response.count == 1


# =============================================================================
# Composition Tests
# =============================================================================


class TestTaskToolComposition:
    """Tests for task tool categorical composition."""

    async def test_compose_with_identity(self, list_tool: TodoListTool) -> None:
        """Task tool composes with identity."""
        from services.tooling.base import IdentityTool

        # Id >> TodoListTool (type mismatch expected, but structure works)
        pipeline = IdentityTool[TodoListRequest]() >> list_tool

        assert " >> " in pipeline.name

    async def test_category_properties(self, list_tool: TodoListTool) -> None:
        """All task tools have correct category."""
        assert list_tool.category == ToolCategory.ORCHESTRATION


# =============================================================================
# Integration Tests
# =============================================================================


class TestTaskToolIntegration:
    """Integration tests for task tool workflow."""

    async def test_full_workflow(self, task_store: TaskStore) -> None:
        """Complete workflow: create → start → complete → start next."""
        create_tool = TodoCreateTool(_store=task_store)
        update_tool = TodoUpdateTool(_store=task_store)
        list_tool = TodoListTool(_store=task_store)

        # Create tasks
        await create_tool.invoke(
            TodoCreateRequest(
                todos=[
                    TodoItem(content="Task 1", status="pending", active_form="Doing 1"),
                    TodoItem(content="Task 2", status="pending", active_form="Doing 2"),
                ]
            )
        )

        # Start first task
        await update_tool.invoke(TodoUpdateRequest(index=0, status="in_progress"))

        # Verify state
        response = await list_tool.invoke(TodoListRequest(status_filter="in_progress"))
        assert response.count == 1
        assert response.todos[0].content == "Task 1"

        # Complete first, start second
        await update_tool.invoke(TodoUpdateRequest(index=0, status="completed"))
        await update_tool.invoke(TodoUpdateRequest(index=1, status="in_progress"))

        # Verify final state
        response = await list_tool.invoke(TodoListRequest())
        assert response.todos[0].status == "completed"
        assert response.todos[1].status == "in_progress"
