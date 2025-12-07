"""
Session Tick Pipeline

Per-tick state update using Fix-based detection.

Pipeline: Session → Session (with updated state)

This demonstrates the research plan's insight:
    "Polling is Fix: Session state detection via polling is a fixed-point search"

The tick pipeline:
    1. Capture current output
    2. Detect state (Fix-based iteration)
    3. Handle state transitions
    4. Update ground state

In zenportal: This is StateRefresher.refresh()
In zen-agents: Explicit composition with Fix as the core operator.
"""

import sys
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "claude-openrouter"))

from bootstrap import Agent, contradict, sublate, Tension, TensionMode
from zen_agents.types import (
    Session,
    SessionState,
)
from zen_agents.ground import ZenGround, zen_ground
from zen_agents.session.detect import SessionDetect, detect_state, DetectionResult
from zen_agents.tmux.capture import TmuxCapture, capture_output, CaptureInput
from zen_agents.tmux.query import TmuxExists, session_exists


@dataclass
class TickResult:
    """Result of a tick"""
    session: Session
    state_changed: bool
    old_state: SessionState
    new_state: SessionState
    detection: DetectionResult | None
    output_lines: list[str]


class SessionTickPipeline(Agent[Session, TickResult]):
    """
    Per-tick session state update.

    Type signature: SessionTickPipeline: Session → TickResult

    This pipeline runs on every refresh cycle (500ms in zenportal).
    It uses Fix-based detection to find stable state.

    Key insight: The "polling loop" IS a fixed-point search.
    We iterate (poll) until state stabilizes.
    """

    def __init__(
        self,
        ground: ZenGround | None = None,
        capture: TmuxCapture | None = None,
        detect: SessionDetect | None = None,
        exists: TmuxExists | None = None,
        grace_period_seconds: float = 5.0,
    ):
        self._ground = ground or zen_ground
        self._capture = capture or capture_output
        self._detect = detect or detect_state
        self._exists = exists or session_exists
        self._grace_period = grace_period_seconds

    @property
    def name(self) -> str:
        return "SessionTickPipeline"

    @property
    def genus(self) -> str:
        return "zen/pipeline"

    @property
    def purpose(self) -> str:
        return "Per-tick state update with Fix-based detection"

    async def invoke(self, session: Session) -> TickResult:
        """
        Execute one tick of state update.

        Steps:
            1. Skip if not RUNNING
            2. Check tmux session exists
            3. Check grace period (after revival)
            4. Capture output
            5. Detect state (Fix-based)
            6. Handle state transition
        """
        old_state = session.state
        output_lines: list[str] = []

        # Step 1: Skip non-running sessions
        if session.state != SessionState.RUNNING:
            return TickResult(
                session=session,
                state_changed=False,
                old_state=old_state,
                new_state=session.state,
                detection=None,
                output_lines=[],
            )

        # Step 2: Check tmux session exists
        if session.tmux:
            exists = await self._exists.invoke(session.tmux.id)
            if not exists:
                # Session died without us knowing
                updated = replace(
                    session,
                    state=SessionState.COMPLETED,
                    completed_at=datetime.now(),
                )
                self._ground.update_session(updated)
                return TickResult(
                    session=updated,
                    state_changed=True,
                    old_state=old_state,
                    new_state=SessionState.COMPLETED,
                    detection=None,
                    output_lines=[],
                )

        # Step 3: Grace period check
        if self._in_grace_period(session):
            return TickResult(
                session=session,
                state_changed=False,
                old_state=old_state,
                new_state=session.state,
                detection=None,
                output_lines=[],
            )

        # Step 4: Capture output
        if session.tmux:
            capture_result = await self._capture.invoke(CaptureInput(
                session=session.tmux,
                lines=100,
            ))
            output_lines = capture_result.lines

            # Check if pane is dead
            if capture_result.is_dead:
                new_state = (
                    SessionState.COMPLETED
                    if capture_result.exit_code == 0
                    else SessionState.FAILED
                )
                error = (
                    None if capture_result.exit_code == 0
                    else f"Exit code: {capture_result.exit_code}"
                )

                updated = replace(
                    session,
                    state=new_state,
                    completed_at=datetime.now(),
                    output_lines=output_lines,
                    error=error,
                )
                self._ground.update_session(updated)
                return TickResult(
                    session=updated,
                    state_changed=True,
                    old_state=old_state,
                    new_state=new_state,
                    detection=None,
                    output_lines=output_lines,
                )

        # Step 5: Detect state (Fix-based)
        updated_session = replace(session, output_lines=output_lines)
        detection = await self._detect.invoke(updated_session)

        # Step 6: Handle state transition
        new_state = detection.state
        state_changed = new_state != old_state

        if state_changed:
            updated_session = replace(
                updated_session,
                state=new_state,
                completed_at=datetime.now() if new_state in {
                    SessionState.COMPLETED, SessionState.FAILED
                } else None,
            )

        self._ground.update_session(updated_session)

        return TickResult(
            session=updated_session,
            state_changed=state_changed,
            old_state=old_state,
            new_state=new_state,
            detection=detection,
            output_lines=output_lines,
        )

    def _in_grace_period(self, session: Session) -> bool:
        """Check if session is in post-revival grace period."""
        # Would check session.revived_at in real impl
        return False


# Singleton instance
session_tick = SessionTickPipeline()
