"""
Attention State Detection - Infer user's cognitive availability from activity.

Detects attention state from filesystem and git activity patterns to determine
when it's appropriate to surface tensions.

From spec/protocols/kairos.md:
  A(t) = base_budget × context_multiplier × temporal_factor

States:
- DEEP_WORK (0.1): User deeply focused, minimal interruptions
- ACTIVE (0.5): Working but interruptible
- TRANSITIONING (0.8): Between tasks, good moment
- IDLE (1.0): No active work, optimal moment
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path


class AttentionState(Enum):
    """
    User's current attention availability.

    Values represent the context multiplier for attention budget:
    - DEEP_WORK: 0.1 (emergencies only)
    - ACTIVE: 0.5 (working but interruptible)
    - TRANSITIONING: 0.8 (between tasks)
    - IDLE: 1.0 (optimal moment)
    """

    DEEP_WORK = 0.1
    ACTIVE = 0.5
    TRANSITIONING = 0.8
    IDLE = 1.0


@dataclass
class KairosContext:
    """
    Current state for timing decisions.

    Captures all relevant context about user attention and system state
    at a specific moment in time.
    """

    timestamp: datetime
    attention_state: AttentionState
    attention_budget: float  # A(t), final computed budget
    cognitive_load: float  # L(t), 0.0-1.0 estimated from activity
    recent_interventions: int  # Count of recent surfacings
    last_activity_age: float  # Minutes since last filesystem/git activity

    # Additional context for decision making
    last_commit_age: float | None = None  # Minutes since last git commit
    last_file_mod_age: float | None = None  # Minutes since last file modification
    active_files_count: int = 0  # Number of recently modified files


class AttentionDetector:
    """
    Detects user attention state from filesystem and git activity.

    Uses heuristics to infer cognitive availability:
    - Recent git commits → ACTIVE or DEEP_WORK
    - File modifications → ACTIVE
    - Long idle periods → TRANSITIONING or IDLE
    - Multiple rapid changes → DEEP_WORK (in flow)
    """

    def __init__(
        self,
        base_budget: float = 1.0,
        deep_work_threshold: timedelta = timedelta(minutes=5),
        active_threshold: timedelta = timedelta(minutes=15),
        transitioning_threshold: timedelta = timedelta(minutes=30),
    ):
        """
        Initialize attention detector.

        Args:
            base_budget: User's default attention capacity (0.0-1.0)
            deep_work_threshold: Max idle time to consider deep work
            active_threshold: Max idle time to consider active
            transitioning_threshold: Max idle time to consider transitioning
        """
        self.base_budget = base_budget
        self.deep_work_threshold = deep_work_threshold
        self.active_threshold = active_threshold
        self.transitioning_threshold = transitioning_threshold

    def detect_attention_state(
        self,
        workspace_path: Path,
        recent_interventions: int = 0,
    ) -> KairosContext:
        """
        Detect current attention state from workspace activity.

        Args:
            workspace_path: Path to workspace/repository to monitor
            recent_interventions: Count of recent tension surfacings

        Returns:
            KairosContext with detected state and computed budget
        """
        now = datetime.now()

        # Collect activity signals
        last_commit_age = self._get_last_commit_age(workspace_path)
        last_file_mod_age = self._get_last_file_modification_age(workspace_path)
        active_files = self._get_recently_active_files(workspace_path)

        # Determine attention state
        last_activity_age = min(
            filter(
                lambda x: x is not None,
                [last_commit_age, last_file_mod_age],
            ),
            default=float("inf"),
        )

        attention_state = self._classify_attention_state(
            last_activity_age, active_files
        )

        # Compute cognitive load (more files = higher load)
        cognitive_load = self._estimate_cognitive_load(active_files, last_activity_age)

        # Compute final attention budget
        context_multiplier = attention_state.value
        temporal_factor = self._compute_temporal_factor(now)
        attention_budget = self.base_budget * context_multiplier * temporal_factor

        return KairosContext(
            timestamp=now,
            attention_state=attention_state,
            attention_budget=attention_budget,
            cognitive_load=cognitive_load,
            recent_interventions=recent_interventions,
            last_activity_age=last_activity_age,
            last_commit_age=last_commit_age,
            last_file_mod_age=last_file_mod_age,
            active_files_count=len(active_files),
        )

    def _classify_attention_state(
        self, last_activity_age: float, active_files: list[Path]
    ) -> AttentionState:
        """
        Classify attention state based on activity patterns.

        Heuristics:
        - Very recent activity + multiple files → DEEP_WORK (in flow)
        - Recent activity → ACTIVE
        - Moderate idle time → TRANSITIONING
        - Long idle time → IDLE
        """
        deep_work_minutes = self.deep_work_threshold.total_seconds() / 60
        active_minutes = self.active_threshold.total_seconds() / 60
        transition_minutes = self.transitioning_threshold.total_seconds() / 60

        # Multiple files being worked on suggests deep work
        if last_activity_age < deep_work_minutes and len(active_files) >= 3:
            return AttentionState.DEEP_WORK

        # Recent activity
        if last_activity_age < active_minutes:
            return AttentionState.ACTIVE

        # Moderate idle
        if last_activity_age < transition_minutes:
            return AttentionState.TRANSITIONING

        # Long idle
        return AttentionState.IDLE

    def _estimate_cognitive_load(
        self, active_files: list[Path], last_activity_age: float
    ) -> float:
        """
        Estimate cognitive load from activity patterns.

        Returns value 0.0-1.0:
        - More active files = higher load
        - Recent activity = higher load
        - Long idle = lower load
        """
        # File count component (normalized to 0-0.5)
        file_load = min(len(active_files) / 10.0, 0.5)

        # Recency component (normalized to 0-0.5)
        # Recent activity suggests mental context still loaded
        if last_activity_age < 5:
            recency_load = 0.5
        elif last_activity_age < 15:
            recency_load = 0.3
        elif last_activity_age < 30:
            recency_load = 0.1
        else:
            recency_load = 0.0

        return file_load + recency_load

    def _compute_temporal_factor(self, timestamp: datetime) -> float:
        """
        Compute time-of-day attention factor.

        Simple heuristic:
        - Peak hours (9am-5pm): 1.0
        - Morning/evening (7-9am, 5-9pm): 0.8
        - Late night (9pm-1am): 0.6
        - Deep night (1-7am): 0.3
        """
        hour = timestamp.hour

        if 9 <= hour < 17:  # Peak work hours
            return 1.0
        elif 7 <= hour < 9 or 17 <= hour < 21:  # Transition periods
            return 0.8
        elif 21 <= hour < 24 or 0 <= hour < 1:  # Late night
            return 0.6
        else:  # Deep night
            return 0.3

    def _get_last_commit_age(self, workspace_path: Path) -> float | None:
        """
        Get minutes since last git commit.

        Returns None if not a git repo or error occurs.
        """
        try:
            result = subprocess.run(
                ["git", "-C", str(workspace_path), "log", "-1", "--format=%ct"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                commit_timestamp = int(result.stdout.strip())
                commit_time = datetime.fromtimestamp(commit_timestamp)
                delta = datetime.now() - commit_time
                return delta.total_seconds() / 60
        except (subprocess.SubprocessError, ValueError):
            pass
        return None

    def _get_last_file_modification_age(self, workspace_path: Path) -> float | None:
        """
        Get minutes since last file modification in workspace.

        Scans common development files (.py, .md, .txt, etc.).
        Returns None if no files found or error occurs.
        """
        try:
            # Look for recently modified files
            extensions = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
            latest_mtime = 0.0

            for ext in extensions:
                for file_path in workspace_path.rglob(f"*{ext}"):
                    # Skip hidden, venv, node_modules, etc.
                    if any(part.startswith(".") for part in file_path.parts):
                        continue
                    if "venv" in file_path.parts or "node_modules" in file_path.parts:
                        continue

                    try:
                        mtime = file_path.stat().st_mtime
                        latest_mtime = max(latest_mtime, mtime)
                    except OSError:
                        continue

            if latest_mtime > 0:
                mod_time = datetime.fromtimestamp(latest_mtime)
                delta = datetime.now() - mod_time
                return delta.total_seconds() / 60

        except Exception:
            pass
        return None

    def _get_recently_active_files(
        self, workspace_path: Path, window_minutes: int = 15
    ) -> list[Path]:
        """
        Get list of files modified in last N minutes.

        Used to estimate how many files user is actively working on.
        """
        active_files = []
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        cutoff_timestamp = cutoff.timestamp()

        try:
            extensions = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml"}

            for ext in extensions:
                for file_path in workspace_path.rglob(f"*{ext}"):
                    # Skip hidden, venv, etc.
                    if any(part.startswith(".") for part in file_path.parts):
                        continue
                    if "venv" in file_path.parts or "node_modules" in file_path.parts:
                        continue

                    try:
                        if file_path.stat().st_mtime >= cutoff_timestamp:
                            active_files.append(file_path)
                    except OSError:
                        continue

        except Exception:
            pass

        return active_files
