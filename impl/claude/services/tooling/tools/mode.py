"""
Mode Tools: Plan ↔ Execute Modal Transitions.

Phase 3 of U-gent Tooling: Orchestration tools for workflow coordination.

Mode tools manage the agent's operational mode:
- EXECUTE_MODE: Normal operation, tools can be invoked freely
- PLAN_MODE: Exploration/design phase, writes are restricted

Key insight from Claude Code:
- EnterPlanMode: Agent signals "I'm exploring, let me design an approach"
- ExitPlanMode: Agent signals "Ready to implement" — REQUIRES user approval

The asymmetry is intentional:
- Entering plan mode is low-risk (just exploring)
- Exiting plan mode gates implementation (user confirms approach)

State Machine:
    EXECUTE ──EnterPlanMode──> PLAN
    PLAN ──ExitPlanMode(approved)──> EXECUTE
    PLAN ──ExitPlanMode(not approved)──> PLAN (stays)

See: plans/ugent-tooling-phase3-handoff.md
See: docs/skills/crown-jewel-patterns.md (Pattern 1: Container Owns Workflow)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from ..base import Tool, ToolCategory, ToolError
from ..contracts import (
    EnterPlanModeRequest,
    EnterPlanModeResponse,
    ExitPlanModeRequest,
    ExitPlanModeResponse,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Mode State Machine
# =============================================================================


class AgentMode(Enum):
    """
    Agent operational mode.

    EXECUTE: Normal operation, all tools available
    PLAN: Design/exploration phase, agent is planning approach
    """

    EXECUTE = "execute"
    PLAN = "plan"


# =============================================================================
# Session-Scoped Mode State
# =============================================================================


@dataclass
class ModeState:
    """
    Session-scoped mode state.

    Tracks current mode and provides transition logic.
    """

    current_mode: AgentMode = AgentMode.EXECUTE
    plan_file_path: str | None = None  # Optional plan file for reference
    pending_approval: bool = False  # True if waiting for user approval

    def can_enter_plan(self) -> bool:
        """Check if can transition to plan mode."""
        return self.current_mode == AgentMode.EXECUTE

    def can_exit_plan(self) -> bool:
        """Check if can transition to execute mode."""
        return self.current_mode == AgentMode.PLAN

    def enter_plan(self, plan_file: str | None = None) -> None:
        """Transition to plan mode."""
        if not self.can_enter_plan():
            raise ToolError(
                f"Cannot enter plan mode: already in {self.current_mode.value} mode",
                "mode.enter_plan",
            )
        self.current_mode = AgentMode.PLAN
        self.plan_file_path = plan_file
        self.pending_approval = False

    def request_exit_plan(self) -> None:
        """Request transition to execute mode (pending approval)."""
        if not self.can_exit_plan():
            raise ToolError(
                f"Cannot exit plan mode: currently in {self.current_mode.value} mode",
                "mode.exit_plan",
            )
        self.pending_approval = True

    def approve_exit(self) -> None:
        """Approve transition to execute mode."""
        if not self.pending_approval:
            raise ToolError(
                "No pending approval request",
                "mode.exit_plan",
            )
        self.current_mode = AgentMode.EXECUTE
        self.pending_approval = False
        self.plan_file_path = None

    def reject_exit(self) -> None:
        """Reject transition (stay in plan mode)."""
        self.pending_approval = False


# Singleton for session scope
_mode_state: ModeState | None = None


def get_mode_state() -> ModeState:
    """Get or create the session mode state."""
    global _mode_state
    if _mode_state is None:
        _mode_state = ModeState()
    return _mode_state


def reset_mode_state() -> None:
    """Reset the mode state (for testing)."""
    global _mode_state
    _mode_state = None


def set_mode_state(state: ModeState) -> None:
    """Inject a mode state (for testing)."""
    global _mode_state
    _mode_state = state


# =============================================================================
# Approval Handler (Pluggable)
# =============================================================================

# Type for approval callback
ApprovalCallback = Callable[[ExitPlanModeRequest], bool]


def _default_approval_handler(request: ExitPlanModeRequest) -> bool:
    """
    Default approval handler (always requires approval).

    In production, this would:
    1. Present the plan to the user
    2. Wait for user confirmation
    3. Return True/False based on user response

    For testing, inject a custom handler.
    """
    # Default: approval is pending (needs explicit approval)
    return False


_approval_handler: ApprovalCallback = _default_approval_handler


def set_approval_handler(handler: ApprovalCallback) -> None:
    """Set the approval handler (for testing or production wiring)."""
    global _approval_handler
    _approval_handler = handler


def reset_approval_handler() -> None:
    """Reset to default approval handler."""
    global _approval_handler
    _approval_handler = _default_approval_handler


# =============================================================================
# EnterPlanModeTool
# =============================================================================


@dataclass
class EnterPlanModeTool(Tool[EnterPlanModeRequest, EnterPlanModeResponse]):
    """
    Transition from execute mode to plan mode.

    Plan mode signals the agent is exploring/designing an approach.
    No user approval required (low-risk operation).

    Trust Level: L0 (mode transition)
    Effects: BLOCKS (changes agent behavior)
    """

    _state: ModeState | None = None

    def __post_init__(self) -> None:
        if self._state is None:
            self._state = get_mode_state()

    @property
    def name(self) -> str:
        return "mode.enter_plan"

    @property
    def description(self) -> str:
        return "Enter plan mode to design implementation approach"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def trust_required(self) -> int:
        return 0  # L0 - Mode transition

    async def invoke(self, request: EnterPlanModeRequest) -> EnterPlanModeResponse:
        """
        Enter plan mode.

        Args:
            request: EnterPlanModeRequest (no args needed)

        Returns:
            EnterPlanModeResponse with success status

        Raises:
            ToolError: If already in plan mode
        """
        assert self._state is not None

        try:
            self._state.enter_plan()
            logger.debug("Entered plan mode")

            return EnterPlanModeResponse(
                success=True,
                message="Entered plan mode. Explore the codebase and design your approach.",
            )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(str(e), self.name) from e


# =============================================================================
# ExitPlanModeTool
# =============================================================================


@dataclass
class ExitPlanModeTool(Tool[ExitPlanModeRequest, ExitPlanModeResponse]):
    """
    Transition from plan mode to execute mode.

    REQUIRES user approval before implementation begins.
    This is the key gating mechanism for safe agent operation.

    Trust Level: L0 (mode transition)
    Effects: BLOCKS (waits for approval)
    """

    _state: ModeState | None = None

    def __post_init__(self) -> None:
        if self._state is None:
            self._state = get_mode_state()

    @property
    def name(self) -> str:
        return "mode.exit_plan"

    @property
    def description(self) -> str:
        return "Exit plan mode and request approval to implement"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def trust_required(self) -> int:
        return 0  # L0 - Mode transition

    async def invoke(self, request: ExitPlanModeRequest) -> ExitPlanModeResponse:
        """
        Request to exit plan mode.

        This checks with the approval handler (user confirmation).
        If approved, transitions to execute mode.
        If not approved, stays in plan mode.

        Args:
            request: ExitPlanModeRequest with optional swarm config

        Returns:
            ExitPlanModeResponse with approval status

        Raises:
            ToolError: If not in plan mode
        """
        assert self._state is not None

        try:
            # Request exit (validates we're in plan mode)
            self._state.request_exit_plan()

            # Check approval via handler
            approved = _approval_handler(request)

            if approved:
                self._state.approve_exit()
                logger.debug(
                    f"Exited plan mode (approved). "
                    f"launch_swarm={request.launch_swarm}, "
                    f"teammate_count={request.teammate_count}"
                )

                message = "Plan approved. Ready to implement."
                if request.launch_swarm:
                    message = (
                        f"Plan approved. Launching swarm with {request.teammate_count} teammates."
                    )

                return ExitPlanModeResponse(
                    success=True,
                    approved=True,
                    message=message,
                )
            else:
                self._state.reject_exit()
                logger.debug("Exit plan mode rejected (pending approval)")

                return ExitPlanModeResponse(
                    success=True,
                    approved=False,
                    message="Awaiting user approval. Please review the plan.",
                )

        except ToolError:
            raise
        except Exception as e:
            raise ToolError(str(e), self.name) from e


# =============================================================================
# Convenience: Query Mode
# =============================================================================


@dataclass
class ModeQueryRequest:
    """Request for querying current mode."""

    pass


@dataclass
class ModeQueryResponse:
    """Response with current mode state."""

    mode: str
    pending_approval: bool
    plan_file_path: str | None


@dataclass
class ModeQueryTool(Tool[ModeQueryRequest, ModeQueryResponse]):
    """
    Query current mode state.

    Useful for UI to show current mode and pending approvals.

    Trust Level: L0 (read-only)
    """

    _state: ModeState | None = None

    def __post_init__(self) -> None:
        if self._state is None:
            self._state = get_mode_state()

    @property
    def name(self) -> str:
        return "mode.query"

    @property
    def description(self) -> str:
        return "Query current agent mode"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def trust_required(self) -> int:
        return 0

    async def invoke(self, request: ModeQueryRequest) -> ModeQueryResponse:
        assert self._state is not None

        return ModeQueryResponse(
            mode=self._state.current_mode.value,
            pending_approval=self._state.pending_approval,
            plan_file_path=self._state.plan_file_path,
        )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # State
    "AgentMode",
    "ModeState",
    "get_mode_state",
    "reset_mode_state",
    "set_mode_state",
    # Approval
    "ApprovalCallback",
    "set_approval_handler",
    "reset_approval_handler",
    # Tools
    "EnterPlanModeTool",
    "ExitPlanModeTool",
    "ModeQueryTool",
    "ModeQueryRequest",
    "ModeQueryResponse",
]
