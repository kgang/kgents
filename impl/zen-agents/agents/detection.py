"""
State Detection as Fix.

Polling is Fix. Replace `while True` loops with fixed-point iteration.

IDIOM: Polling is Fix
> Any iteration pattern is a fixed-point search.
"""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

import sys
sys.path.insert(0, str(__file__).rsplit("/impl/", 1)[0] + "/impl/claude-openrouter")

from bootstrap import Agent, fix, FixResult

if TYPE_CHECKING:
    from ..models import Session, SessionState
    from ..services.tmux import TmuxService


@dataclass
class DetectionState:
    """
    The state being detected through polling.

    This is the value that Fix iterates on until stable.
    """
    from ..models.session import SessionState

    session_state: SessionState
    confidence: float  # 0.0 to 1.0, increases with each consistent poll
    exit_code: Optional[int] = None
    error_message: Optional[str] = None

    def is_stable(self) -> bool:
        """Considered stable when confidence >= 0.8."""
        return self.confidence >= 0.8

    @classmethod
    def initial(cls) -> "DetectionState":
        """Initial state for detection."""
        from ..models.session import SessionState
        return cls(
            session_state=SessionState.RUNNING,
            confidence=0.0,
        )


class StateDetector(Agent[tuple["Session", "TmuxService"], DetectionState]):
    """
    Detect session state through a single poll.

    This is the transform function for Fix.
    Each invocation is one polling iteration.
    """

    @property
    def name(self) -> str:
        return "StateDetector"

    async def invoke(
        self, input: tuple["Session", "TmuxService"]
    ) -> DetectionState:
        """Poll once and return updated detection state."""
        from ..models.session import SessionState

        session, tmux = input

        # Check if tmux pane is still running
        is_alive = await tmux.is_session_alive(session.tmux_name)

        if not is_alive:
            # Session terminated - get exit code
            exit_code = await tmux.get_exit_code(session.tmux_name)

            if exit_code == 0:
                return DetectionState(
                    session_state=SessionState.COMPLETED,
                    confidence=1.0,
                    exit_code=exit_code,
                )
            else:
                return DetectionState(
                    session_state=SessionState.FAILED,
                    confidence=1.0,
                    exit_code=exit_code,
                    error_message=f"Process exited with code {exit_code}",
                )

        # Still running - increase confidence
        return DetectionState(
            session_state=SessionState.RUNNING,
            confidence=min(1.0, 0.2),  # Running confidence builds slowly
        )


async def detect_state(
    session: "Session",
    tmux: "TmuxService",
    max_iterations: int = 50,
) -> FixResult[DetectionState]:
    """
    Detect session state using Fix.

    Polls until state is stable (confidence >= 0.8) or max iterations.

    Usage:
        result = await detect_state(session, tmux_service)
        if result.converged:
            final_state = result.value.session_state
    """
    detector = StateDetector()

    async def poll_once(state: DetectionState) -> DetectionState:
        """One polling iteration - the transform for Fix."""
        new_state = await detector.invoke((session, tmux))

        # If state matches previous, increase confidence
        if new_state.session_state == state.session_state:
            return DetectionState(
                session_state=new_state.session_state,
                confidence=min(1.0, state.confidence + 0.2),
                exit_code=new_state.exit_code,
                error_message=new_state.error_message,
            )

        # State changed - reset confidence
        return new_state

    return await fix(
        transform=poll_once,
        initial=DetectionState.initial(),
        equality_check=lambda a, b: (
            a.session_state == b.session_state and b.confidence >= 0.8
        ),
        max_iterations=max_iterations,
    )
