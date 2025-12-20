"""
Tests for Mode Tools: Plan ↔ Execute Modal Transitions.

Covers:
- EnterPlanModeTool: Transition to plan mode
- ExitPlanModeTool: Transition to execute mode with approval
- ModeState: Session state mechanics
- Approval gating: User confirmation required for exit

Key constraint tested: ExitPlanMode REQUIRES approval.

See: services/tooling/tools/mode.py
"""

from __future__ import annotations

import pytest

from services.tooling.base import ToolCategory, ToolError
from services.tooling.contracts import (
    EnterPlanModeRequest,
    ExitPlanModeRequest,
)
from services.tooling.tools.mode import (
    AgentMode,
    EnterPlanModeTool,
    ExitPlanModeTool,
    ModeQueryRequest,
    ModeQueryTool,
    ModeState,
    get_mode_state,
    reset_approval_handler,
    reset_mode_state,
    set_approval_handler,
    set_mode_state,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mode_state() -> ModeState:
    """Fresh mode state for each test."""
    state = ModeState()
    set_mode_state(state)
    yield state
    reset_mode_state()
    reset_approval_handler()


@pytest.fixture
def enter_tool(mode_state: ModeState) -> EnterPlanModeTool:
    """EnterPlanModeTool with fresh state."""
    return EnterPlanModeTool(_state=mode_state)


@pytest.fixture
def exit_tool(mode_state: ModeState) -> ExitPlanModeTool:
    """ExitPlanModeTool with fresh state."""
    return ExitPlanModeTool(_state=mode_state)


@pytest.fixture
def query_tool(mode_state: ModeState) -> ModeQueryTool:
    """ModeQueryTool with fresh state."""
    return ModeQueryTool(_state=mode_state)


# =============================================================================
# AgentMode Tests
# =============================================================================


class TestAgentMode:
    """Tests for AgentMode enum."""

    def test_values(self) -> None:
        """Mode values are correct."""
        assert AgentMode.EXECUTE.value == "execute"
        assert AgentMode.PLAN.value == "plan"


# =============================================================================
# ModeState Tests
# =============================================================================


class TestModeState:
    """Tests for ModeState session storage."""

    def test_initial_state(self, mode_state: ModeState) -> None:
        """Initial state is execute mode."""
        assert mode_state.current_mode == AgentMode.EXECUTE
        assert mode_state.pending_approval is False
        assert mode_state.plan_file_path is None

    def test_can_enter_plan_from_execute(self, mode_state: ModeState) -> None:
        """Can enter plan mode from execute mode."""
        assert mode_state.can_enter_plan() is True

    def test_cannot_enter_plan_from_plan(self, mode_state: ModeState) -> None:
        """Cannot enter plan mode when already in plan mode."""
        mode_state.current_mode = AgentMode.PLAN
        assert mode_state.can_enter_plan() is False

    def test_can_exit_plan_from_plan(self, mode_state: ModeState) -> None:
        """Can exit plan mode from plan mode."""
        mode_state.current_mode = AgentMode.PLAN
        assert mode_state.can_exit_plan() is True

    def test_cannot_exit_plan_from_execute(self, mode_state: ModeState) -> None:
        """Cannot exit plan mode when already in execute mode."""
        assert mode_state.can_exit_plan() is False

    def test_enter_plan_transition(self, mode_state: ModeState) -> None:
        """Enter plan transitions state correctly."""
        mode_state.enter_plan(plan_file="/path/to/plan.md")

        assert mode_state.current_mode == AgentMode.PLAN
        assert mode_state.plan_file_path == "/path/to/plan.md"
        assert mode_state.pending_approval is False

    def test_enter_plan_from_plan_raises(self, mode_state: ModeState) -> None:
        """Cannot enter plan from plan mode."""
        mode_state.current_mode = AgentMode.PLAN

        with pytest.raises(ToolError, match="already in plan"):
            mode_state.enter_plan()

    def test_request_exit_plan(self, mode_state: ModeState) -> None:
        """Requesting exit sets pending approval."""
        mode_state.current_mode = AgentMode.PLAN
        mode_state.request_exit_plan()

        assert mode_state.pending_approval is True
        assert mode_state.current_mode == AgentMode.PLAN  # Still in plan

    def test_request_exit_from_execute_raises(self, mode_state: ModeState) -> None:
        """Cannot request exit from execute mode."""
        with pytest.raises(ToolError, match="currently in execute"):
            mode_state.request_exit_plan()

    def test_approve_exit(self, mode_state: ModeState) -> None:
        """Approving exit transitions to execute mode."""
        mode_state.current_mode = AgentMode.PLAN
        mode_state.request_exit_plan()
        mode_state.approve_exit()

        assert mode_state.current_mode == AgentMode.EXECUTE
        assert mode_state.pending_approval is False

    def test_approve_without_pending_raises(self, mode_state: ModeState) -> None:
        """Cannot approve without pending request."""
        mode_state.current_mode = AgentMode.PLAN

        with pytest.raises(ToolError, match="No pending approval"):
            mode_state.approve_exit()

    def test_reject_exit(self, mode_state: ModeState) -> None:
        """Rejecting exit clears pending and stays in plan."""
        mode_state.current_mode = AgentMode.PLAN
        mode_state.request_exit_plan()
        mode_state.reject_exit()

        assert mode_state.current_mode == AgentMode.PLAN
        assert mode_state.pending_approval is False


# =============================================================================
# EnterPlanModeTool Tests
# =============================================================================


class TestEnterPlanModeTool:
    """Tests for EnterPlanModeTool."""

    def test_properties(self, enter_tool: EnterPlanModeTool) -> None:
        """Tool has correct properties."""
        assert enter_tool.name == "mode.enter_plan"
        assert enter_tool.category == ToolCategory.ORCHESTRATION
        assert enter_tool.trust_required == 0

    async def test_enter_plan_success(
        self, enter_tool: EnterPlanModeTool, mode_state: ModeState
    ) -> None:
        """Successfully entering plan mode."""
        response = await enter_tool.invoke(EnterPlanModeRequest())

        assert response.success is True
        assert "plan mode" in response.message.lower()
        assert mode_state.current_mode == AgentMode.PLAN

    async def test_enter_plan_from_plan_fails(
        self, enter_tool: EnterPlanModeTool, mode_state: ModeState
    ) -> None:
        """Entering plan from plan mode fails."""
        mode_state.current_mode = AgentMode.PLAN

        with pytest.raises(ToolError, match="already in plan"):
            await enter_tool.invoke(EnterPlanModeRequest())


# =============================================================================
# ExitPlanModeTool Tests
# =============================================================================


class TestExitPlanModeTool:
    """Tests for ExitPlanModeTool."""

    def test_properties(self, exit_tool: ExitPlanModeTool) -> None:
        """Tool has correct properties."""
        assert exit_tool.name == "mode.exit_plan"
        assert exit_tool.category == ToolCategory.ORCHESTRATION
        assert exit_tool.trust_required == 0

    async def test_exit_not_in_plan_fails(
        self, exit_tool: ExitPlanModeTool, mode_state: ModeState
    ) -> None:
        """Exiting when not in plan mode fails."""
        assert mode_state.current_mode == AgentMode.EXECUTE

        with pytest.raises(ToolError, match="currently in execute"):
            await exit_tool.invoke(ExitPlanModeRequest())

    async def test_exit_default_not_approved(
        self, exit_tool: ExitPlanModeTool, mode_state: ModeState
    ) -> None:
        """Default handler does not approve (requires explicit approval)."""
        mode_state.current_mode = AgentMode.PLAN

        response = await exit_tool.invoke(ExitPlanModeRequest())

        assert response.success is True
        assert response.approved is False
        assert "awaiting" in response.message.lower()
        assert mode_state.current_mode == AgentMode.PLAN  # Still in plan

    async def test_exit_with_approval(
        self, exit_tool: ExitPlanModeTool, mode_state: ModeState
    ) -> None:
        """Exit with approval handler returning True."""
        mode_state.current_mode = AgentMode.PLAN

        # Set handler that auto-approves
        set_approval_handler(lambda _: True)

        response = await exit_tool.invoke(ExitPlanModeRequest())

        assert response.success is True
        assert response.approved is True
        assert "approved" in response.message.lower()
        assert mode_state.current_mode == AgentMode.EXECUTE

    async def test_exit_with_swarm(
        self, exit_tool: ExitPlanModeTool, mode_state: ModeState
    ) -> None:
        """Exit with swarm launch option."""
        mode_state.current_mode = AgentMode.PLAN
        set_approval_handler(lambda _: True)

        response = await exit_tool.invoke(ExitPlanModeRequest(launch_swarm=True, teammate_count=3))

        assert response.success is True
        assert response.approved is True
        assert "swarm" in response.message.lower()
        assert "3" in response.message

    async def test_exit_rejected_stays_in_plan(
        self, exit_tool: ExitPlanModeTool, mode_state: ModeState
    ) -> None:
        """Rejected exit keeps agent in plan mode."""
        mode_state.current_mode = AgentMode.PLAN
        set_approval_handler(lambda _: False)

        response = await exit_tool.invoke(ExitPlanModeRequest())

        assert response.approved is False
        assert mode_state.current_mode == AgentMode.PLAN


# =============================================================================
# ModeQueryTool Tests
# =============================================================================


class TestModeQueryTool:
    """Tests for ModeQueryTool."""

    def test_properties(self, query_tool: ModeQueryTool) -> None:
        """Tool has correct properties."""
        assert query_tool.name == "mode.query"
        assert query_tool.category == ToolCategory.ORCHESTRATION
        assert query_tool.trust_required == 0

    async def test_query_execute_mode(
        self, query_tool: ModeQueryTool, mode_state: ModeState
    ) -> None:
        """Query returns execute mode state."""
        response = await query_tool.invoke(ModeQueryRequest())

        assert response.mode == "execute"
        assert response.pending_approval is False
        assert response.plan_file_path is None

    async def test_query_plan_mode(self, query_tool: ModeQueryTool, mode_state: ModeState) -> None:
        """Query returns plan mode state."""
        mode_state.enter_plan(plan_file="/my/plan.md")

        response = await query_tool.invoke(ModeQueryRequest())

        assert response.mode == "plan"
        assert response.pending_approval is False
        assert response.plan_file_path == "/my/plan.md"

    async def test_query_pending_approval(
        self, query_tool: ModeQueryTool, mode_state: ModeState
    ) -> None:
        """Query shows pending approval state."""
        mode_state.current_mode = AgentMode.PLAN
        mode_state.request_exit_plan()

        response = await query_tool.invoke(ModeQueryRequest())

        assert response.mode == "plan"
        assert response.pending_approval is True


# =============================================================================
# Approval Handler Tests
# =============================================================================


class TestApprovalHandler:
    """Tests for pluggable approval handler."""

    async def test_custom_handler(self, mode_state: ModeState) -> None:
        """Custom approval handler is called."""
        calls: list[ExitPlanModeRequest] = []

        def custom_handler(request: ExitPlanModeRequest) -> bool:
            calls.append(request)
            return request.launch_swarm  # Approve only if launching swarm

        set_approval_handler(custom_handler)
        mode_state.current_mode = AgentMode.PLAN
        exit_tool = ExitPlanModeTool(_state=mode_state)

        # Without swarm: rejected
        response = await exit_tool.invoke(ExitPlanModeRequest(launch_swarm=False))
        assert response.approved is False

        # With swarm: approved (need to re-enter plan mode first)
        mode_state.current_mode = AgentMode.PLAN
        response = await exit_tool.invoke(ExitPlanModeRequest(launch_swarm=True))
        assert response.approved is True

        assert len(calls) == 2


# =============================================================================
# Composition Tests
# =============================================================================


class TestModeToolComposition:
    """Tests for mode tool categorical composition."""

    async def test_compose_with_identity(self, enter_tool: EnterPlanModeTool) -> None:
        """Mode tool composes with identity."""
        from services.tooling.base import IdentityTool

        pipeline = IdentityTool[EnterPlanModeRequest]() >> enter_tool
        assert " >> " in pipeline.name


# =============================================================================
# Integration Tests
# =============================================================================


class TestModeToolIntegration:
    """Integration tests for mode tool workflow."""

    async def test_full_workflow(self, mode_state: ModeState) -> None:
        """Complete workflow: execute → plan → (rejected) → plan → (approved) → execute."""
        enter_tool = EnterPlanModeTool(_state=mode_state)
        exit_tool = ExitPlanModeTool(_state=mode_state)
        query_tool = ModeQueryTool(_state=mode_state)

        # Start in execute
        query = await query_tool.invoke(ModeQueryRequest())
        assert query.mode == "execute"

        # Enter plan mode
        await enter_tool.invoke(EnterPlanModeRequest())
        query = await query_tool.invoke(ModeQueryRequest())
        assert query.mode == "plan"

        # Try to exit (rejected by default)
        response = await exit_tool.invoke(ExitPlanModeRequest())
        assert response.approved is False
        query = await query_tool.invoke(ModeQueryRequest())
        assert query.mode == "plan"

        # Set approval and try again
        set_approval_handler(lambda _: True)
        response = await exit_tool.invoke(ExitPlanModeRequest())
        assert response.approved is True
        query = await query_tool.invoke(ModeQueryRequest())
        assert query.mode == "execute"
