"""
State Refresher - Fix-based polling service.

Continuously monitors session states using Fix-based iteration.
No while-True loops. All iteration is Fix.

IDIOM: Polling is Fix
> Any iteration pattern is a fixed-point search.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

import sys
sys.path.insert(0, str(__file__).rsplit("/impl/", 1)[0] + "/impl/claude-openrouter")

from bootstrap import fix, FixResult

if TYPE_CHECKING:
    from .session_manager import SessionManager
    from .tmux import TmuxService
    from ..models import Session, SessionState


@dataclass
class RefreshState:
    """State for the refresh fixed-point iteration."""
    last_check: float  # Timestamp of last check
    sessions_checked: int
    states_changed: int
    is_running: bool

    @classmethod
    def initial(cls) -> "RefreshState":
        import time
        return cls(
            last_check=time.time(),
            sessions_checked=0,
            states_changed=0,
            is_running=True,
        )


class StateRefresher:
    """
    Service that periodically refreshes session states.

    Uses Fix internally for each polling cycle.
    The outer loop is also conceptually a Fix operation
    that never converges (continuous monitoring).
    """

    def __init__(
        self,
        manager: "SessionManager",
        poll_interval: float = 1.0,
    ):
        self._manager = manager
        self._poll_interval = poll_interval
        self._running = False
        self._task: Optional[asyncio.Task] = None

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self) -> None:
        """Start the state refresher."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._refresh_loop())

    async def stop(self) -> None:
        """Stop the state refresher."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _refresh_loop(self) -> None:
        """
        The main refresh loop.

        This is conceptually an infinite Fix that never converges,
        continuously polling for state changes.
        """
        while self._running:
            try:
                await self._refresh_once()
                await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error but continue
                await asyncio.sleep(self._poll_interval)

    async def _refresh_once(self) -> RefreshState:
        """
        One refresh iteration.

        This is the transform function for Fix.
        """
        import time
        from ..models import SessionState
        from ..agents.detection import detect_state

        sessions = self._manager.sessions
        states_changed = 0

        for session in sessions:
            # Only check running sessions
            if session.state != SessionState.RUNNING:
                continue

            # Detect current state using Fix
            result = await detect_state(
                session=session,
                tmux=self._manager.tmux,
                max_iterations=5,  # Quick check
            )

            if result.converged:
                new_state = result.value.session_state
                if new_state != session.state:
                    await self._manager.update_session_state(
                        session.id,
                        new_state,
                        result.value.exit_code,
                    )
                    states_changed += 1

        return RefreshState(
            last_check=time.time(),
            sessions_checked=len(sessions),
            states_changed=states_changed,
            is_running=self._running,
        )

    async def refresh_session(self, session: "Session") -> "Session":
        """
        Refresh a single session's state immediately.

        Returns the session with updated state.
        """
        from ..models import SessionState
        from ..agents.detection import detect_state

        result = await detect_state(
            session=session,
            tmux=self._manager.tmux,
            max_iterations=10,
        )

        if result.converged and result.value.session_state != session.state:
            updated = await self._manager.update_session_state(
                session.id,
                result.value.session_state,
                result.value.exit_code,
            )
            return updated or session

        return session


class SingleSessionMonitor:
    """
    Monitor a single session until it completes or fails.

    This is Fix applied to a single session for focused monitoring.
    """

    def __init__(
        self,
        session: "Session",
        tmux: "TmuxService",
        on_state_change: Optional[callable] = None,
    ):
        self._session = session
        self._tmux = tmux
        self._on_state_change = on_state_change

    async def monitor(
        self,
        max_iterations: int = 1000,
        poll_interval: float = 1.0,
    ) -> FixResult:
        """
        Monitor session until terminal state.

        Uses Fix to poll until session is no longer RUNNING.
        """
        from ..agents.detection import DetectionState, StateDetector
        from ..models import SessionState

        @dataclass
        class MonitorState:
            detection: DetectionState
            iteration: int

        async def monitor_once(state: MonitorState) -> MonitorState:
            await asyncio.sleep(poll_interval)

            detector = StateDetector()
            detection = await detector.invoke((self._session, self._tmux))

            # Callback on state change
            if (
                self._on_state_change
                and detection.session_state != state.detection.session_state
            ):
                await self._on_state_change(detection.session_state)

            return MonitorState(
                detection=detection,
                iteration=state.iteration + 1,
            )

        initial = MonitorState(
            detection=DetectionState.initial(),
            iteration=0,
        )

        return await fix(
            transform=monitor_once,
            initial=initial,
            equality_check=lambda a, b: (
                b.detection.session_state != SessionState.RUNNING
                and b.detection.confidence >= 0.8
            ),
            max_iterations=max_iterations,
        )
