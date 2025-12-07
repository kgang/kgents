"""
SessionDetect Agent (Fix-based State Detection)

Detect: Session → SessionState
Detect(session) = Fix(poll_state)(session.state)

Uses the Fix bootstrap agent to iterate until session state stabilizes.
This is the key insight from the research plan:
    "Polling is Fix: Session state detection via polling is a fixed-point search"

The detection process:
    1. Capture current tmux output
    2. Parse for state indicators (completion markers, errors, prompts)
    3. Compare with previous state
    4. Iterate until stable (Fix finds fixed point)
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Awaitable

from bootstrap import Agent, fix, FixResult, FixConfig
from ..types import (
    Session,
    SessionState,
)


@dataclass
class DetectionResult:
    """Result of state detection"""
    state: SessionState
    confidence: float  # 0.0 - 1.0
    indicators: list[str]  # What led to this conclusion
    iterations: int  # How many Fix iterations


# State detection patterns (would be configurable)
COMPLETION_PATTERNS = [
    "Task completed",
    "Done!",
    "finished",
    "exited with code 0",
    ">>> ",  # Python REPL prompt
    "$ ",    # Shell prompt returned
]

ERROR_PATTERNS = [
    "error:",
    "Error:",
    "FAILED",
    "exception",
    "traceback",
    "exited with code 1",
]

RUNNING_PATTERNS = [
    "Processing",
    "Working",
    "...",
    "Loading",
]


class SessionDetect(Agent[Session, DetectionResult]):
    """
    Fix-based session state detection.

    Type signature: SessionDetect: Session → DetectionResult

    Uses Fix to iterate until state stabilizes:
        - Poll tmux output
        - Parse for state indicators
        - Compare with previous reading
        - Stop when state is stable

    This is the "polling as fixed-point" insight from the research plan.
    """

    def __init__(
        self,
        max_iterations: int = 10,
        poll_interval_ms: int = 500,
    ):
        self._max_iterations = max_iterations
        self._poll_interval_ms = poll_interval_ms

    @property
    def name(self) -> str:
        return "SessionDetect"

    @property
    def genus(self) -> str:
        return "zen/session"

    @property
    def purpose(self) -> str:
        return "Detect session state through Fix-based polling"

    async def invoke(self, session: Session) -> DetectionResult:
        """
        Detect the current state of a session.

        Uses Fix to iterate until state stabilizes.
        """
        # If no tmux session, can't detect state
        if not session.tmux:
            return DetectionResult(
                state=session.state,
                confidence=1.0,
                indicators=["No tmux session attached"],
                iterations=0,
            )

        # Initial state estimate
        initial_estimate = DetectionState(
            state=session.state,
            confidence=0.0,
            indicators=[],
            output_snapshot="",
        )

        # Define the transform for Fix
        async def poll_and_detect(current: 'DetectionState') -> 'DetectionState':
            # Capture tmux output (would shell out in real impl)
            output = await self._capture_output(session)

            # Parse output for state indicators
            new_state, confidence, indicators = self._parse_output(output)

            return DetectionState(
                state=new_state,
                confidence=confidence,
                indicators=indicators,
                output_snapshot=output[-500:] if output else "",  # Last 500 chars
            )

        # Custom equality: stable when same state with high confidence
        def is_stable(a: 'DetectionState', b: 'DetectionState') -> bool:
            return (
                a.state == b.state and
                b.confidence >= 0.8 and
                abs(a.confidence - b.confidence) < 0.1
            )

        # Run Fix to find stable state
        result: FixResult[DetectionState] = await fix(
            transform=poll_and_detect,
            initial=initial_estimate,
            max_iterations=self._max_iterations,
            equality_check=is_stable,
        )

        return DetectionResult(
            state=result.value.state,
            confidence=result.value.confidence,
            indicators=result.value.indicators,
            iterations=result.iterations,
        )

    async def _capture_output(self, session: Session) -> str:
        """
        Capture recent tmux output.

        In real impl: tmux capture-pane -p -t {session.tmux.pane_id}
        """
        # Placeholder - would shell out to tmux
        # For now, return whatever output is cached in session
        return "\n".join(session.output_lines[-50:])

    def _parse_output(
        self,
        output: str
    ) -> tuple[SessionState, float, list[str]]:
        """
        Parse output for state indicators.

        Returns (state, confidence, indicators)
        """
        indicators: list[str] = []
        output_lower = output.lower()

        # Check for completion patterns
        completion_matches = [
            p for p in COMPLETION_PATTERNS
            if p.lower() in output_lower
        ]
        if completion_matches:
            indicators.extend([f"Completion: {m}" for m in completion_matches])

        # Check for error patterns
        error_matches = [
            p for p in ERROR_PATTERNS
            if p.lower() in output_lower
        ]
        if error_matches:
            indicators.extend([f"Error: {m}" for m in error_matches])

        # Check for running patterns
        running_matches = [
            p for p in RUNNING_PATTERNS
            if p.lower() in output_lower
        ]
        if running_matches:
            indicators.extend([f"Running: {m}" for m in running_matches])

        # Determine state from indicators
        if error_matches:
            confidence = min(1.0, 0.5 + 0.1 * len(error_matches))
            return SessionState.FAILED, confidence, indicators

        if completion_matches and not running_matches:
            confidence = min(1.0, 0.6 + 0.1 * len(completion_matches))
            return SessionState.COMPLETED, confidence, indicators

        if running_matches:
            confidence = min(1.0, 0.4 + 0.1 * len(running_matches))
            return SessionState.RUNNING, confidence, indicators

        # No clear indicators - stay running but low confidence
        return SessionState.RUNNING, 0.3, ["No clear indicators"]


@dataclass
class DetectionState:
    """Internal state for Fix iteration"""
    state: SessionState
    confidence: float
    indicators: list[str]
    output_snapshot: str


# Singleton instance
detect_state = SessionDetect()
