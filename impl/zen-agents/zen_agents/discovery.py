"""
Discovery Agents

Agents for discovering existing sessions and reconciling state:
    - TmuxDiscovery: Discover running tmux sessions with zen prefix
    - SessionReconcile: Match known sessions against discovered tmux sessions
    - ClaudeSessionDiscovery: Find Claude Code session files in a directory
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from bootstrap import Agent
from .types import Session, TmuxSession, SessionState
from .tmux.query import TmuxList


# =============================================================================
# INPUT/OUTPUT TYPES
# =============================================================================

@dataclass
class DiscoveryInput:
    """Input for TmuxDiscovery agent."""
    prefix: str = "zen-"
    socket_path: str | None = None


@dataclass
class ReconcileInput:
    """Input for SessionReconcile agent."""
    known_sessions: dict[str, Session]
    tmux_sessions: list[TmuxSession]


@dataclass
class ReconcileResult:
    """Result of session reconciliation."""
    matched: list[tuple[Session, TmuxSession]]  # Sessions with matching tmux
    orphaned: list[TmuxSession]  # tmux sessions with no known session
    missing: list[Session]  # known sessions with no tmux


@dataclass
class ClaudeSessionInfo:
    """Information about an existing Claude Code session."""
    session_id: str
    project_path: Path  # The working directory this session was in
    modified_at: datetime
    file_path: Path  # Path to the session file


# =============================================================================
# DISCOVERY AGENTS
# =============================================================================

class TmuxDiscovery(Agent[DiscoveryInput, list[TmuxSession]]):
    """
    Discover running tmux sessions with zen prefix.

    Type signature: TmuxDiscovery: DiscoveryInput → [TmuxSession]

    Uses the existing TmuxList agent from zen_agents/tmux/query.py
    and filters to sessions with the configured prefix (default "zen-").
    """

    def __init__(self, prefix: str = "zen-", socket_path: str | None = None):
        self._default_prefix = prefix
        self._default_socket_path = socket_path

    @property
    def name(self) -> str:
        return "TmuxDiscovery"

    @property
    def genus(self) -> str:
        return "zen/discovery"

    @property
    def purpose(self) -> str:
        return "Discover running tmux sessions with zen prefix"

    async def invoke(self, input: DiscoveryInput | None = None) -> list[TmuxSession]:
        """
        Discover tmux sessions with the configured prefix.

        Args:
            input: Optional discovery config (prefix, socket_path)

        Returns:
            List of tmux sessions matching the prefix
        """
        # Use input params or defaults
        prefix = input.prefix if input else self._default_prefix
        socket_path = input.socket_path if input else self._default_socket_path

        # Create TmuxList agent with the prefix filter
        tmux_list = TmuxList(socket_path=socket_path, prefix=prefix)

        try:
            # Invoke the agent (it handles prefix filtering internally)
            sessions = await tmux_list.invoke()
            return sessions
        except Exception:
            # Handle errors gracefully - return empty list
            return []


class SessionReconcile(Agent[ReconcileInput, ReconcileResult]):
    """
    Match known sessions against discovered tmux sessions.

    Type signature: SessionReconcile: ReconcileInput → ReconcileResult

    Input: (known_sessions: dict[str, Session], tmux_sessions: list[TmuxSession])
    Output: ReconcileResult with:
        - matched: Sessions with matching tmux
        - orphaned: tmux sessions with no known session
        - missing: known sessions with no tmux
    """

    @property
    def name(self) -> str:
        return "SessionReconcile"

    @property
    def genus(self) -> str:
        return "zen/discovery"

    @property
    def purpose(self) -> str:
        return "Match known sessions against discovered tmux sessions"

    async def invoke(self, input: ReconcileInput) -> ReconcileResult:
        """
        Reconcile known sessions with discovered tmux sessions.

        Args:
            input: ReconcileInput with known_sessions and tmux_sessions

        Returns:
            ReconcileResult with matched, orphaned, and missing sessions
        """
        matched: list[tuple[Session, TmuxSession]] = []
        orphaned: list[TmuxSession] = []
        missing: list[Session] = []

        # Build lookup maps (use id, which is the actual tmux session name)
        tmux_by_id = {ts.id: ts for ts in input.tmux_sessions}
        known_by_id = {}

        # Index known sessions by their tmux id (if they have tmux)
        for session in input.known_sessions.values():
            if session.tmux:
                known_by_id[session.tmux.id] = session

        # Find matches and missing
        for session in input.known_sessions.values():
            if session.tmux and session.tmux.id in tmux_by_id:
                # Session has matching tmux
                matched.append((session, tmux_by_id[session.tmux.id]))
            elif session.state in {SessionState.RUNNING, SessionState.PAUSED}:
                # Session should be running but has no tmux
                missing.append(session)

        # Find orphaned tmux sessions
        for tmux_session in input.tmux_sessions:
            if tmux_session.id not in known_by_id:
                orphaned.append(tmux_session)

        return ReconcileResult(
            matched=matched,
            orphaned=orphaned,
            missing=missing,
        )


class ClaudeSessionDiscovery(Agent[Path, list[ClaudeSessionInfo]]):
    """
    Find Claude Code session files in a directory.

    Type signature: ClaudeSessionDiscovery: Path → [ClaudeSessionInfo]

    Claude Code stores sessions in ~/.claude/projects/{project_hash}/sessions/

    This is for the "resume session" feature.
    """

    CLAUDE_DIR = Path.home() / ".claude"
    PROJECTS_DIR = CLAUDE_DIR / "projects"

    @property
    def name(self) -> str:
        return "ClaudeSessionDiscovery"

    @property
    def genus(self) -> str:
        return "zen/discovery"

    @property
    def purpose(self) -> str:
        return "Find Claude Code session files in a directory"

    async def invoke(self, project_path: Path | None = None) -> list[ClaudeSessionInfo]:
        """
        List Claude sessions for a specific project or all projects.

        Args:
            project_path: Specific project path to filter by (None = all)

        Returns:
            List of ClaudeSessionInfo sorted by modification time (newest first)
        """
        if not self.PROJECTS_DIR.exists():
            return []

        sessions = []

        try:
            # Filter by specific project or list all
            if project_path:
                project_name = self._path_to_claude_project_name(project_path)
                project_dirs = [self.PROJECTS_DIR / project_name]
            else:
                project_dirs = [
                    d for d in self.PROJECTS_DIR.iterdir()
                    if d.is_dir()
                ]

            for project_dir in project_dirs:
                if not project_dir.exists():
                    continue

                # Get session files (UUIDs, not agent-* files)
                session_files = [
                    f for f in project_dir.glob("*.jsonl")
                    if not f.name.startswith("agent-")
                    and self._is_valid_uuid(f.stem)
                ]

                for session_file in session_files:
                    try:
                        stat = session_file.stat()
                        sessions.append(ClaudeSessionInfo(
                            session_id=session_file.stem,
                            project_path=self._claude_project_name_to_path(project_dir.name),
                            modified_at=datetime.fromtimestamp(stat.st_mtime),
                            file_path=session_file,
                        ))
                    except (OSError, ValueError):
                        continue

            # Sort by modification time (newest first)
            sessions.sort(key=lambda s: s.modified_at, reverse=True)
            return sessions

        except Exception:
            # Handle file/tmux errors gracefully
            return []

    def _path_to_claude_project_name(self, path: Path) -> str:
        """
        Convert a path to Claude's project directory name format.

        Claude stores projects with both / and _ replaced by -,
        e.g., /Users/kentgang/git/agent_services -> -Users-kentgang-git-agent-services
        """
        # Resolve and make absolute
        path = path.resolve()
        # Replace both / and _ with -
        return str(path).replace("/", "-").replace("_", "-")

    def _claude_project_name_to_path(self, name: str) -> Path:
        """
        Convert Claude's project directory name back to a path.

        Claude stores paths with both / and _ replaced by -.
        Dashes in original paths are preserved as dashes.
        We need to try various combinations to find the actual path.
        """
        # Remove leading dash
        if name.startswith("-"):
            name = name[1:]

        # Simple case: just replace - with /
        simple_path = Path("/" + name.replace("-", "/"))
        if simple_path.exists():
            return simple_path

        # Try intelligent reconstruction by checking each segment
        segments = name.split("-")
        reconstructed = self._reconstruct_path_greedy(segments)
        if reconstructed and reconstructed.exists():
            return reconstructed

        # Fallback to simple conversion
        return simple_path

    def _reconstruct_path_greedy(self, segments: list[str]) -> Path | None:
        """
        Greedily reconstruct a path from dash-separated segments.

        For each dash position, tries:
        1. Treat as path separator (/) - commit current segment as directory
        2. Treat as underscore (_) - extend current segment
        3. Treat as dash (-) - extend current segment with original dash

        Uses filesystem existence checks to determine the correct interpretation.
        """
        if not segments:
            return None

        # Build path one segment at a time, always checking filesystem
        current_path = ""
        current_segment = segments[0]

        for i in range(1, len(segments)):
            seg = segments[i]

            # Try treating dash as slash (new path segment)
            test_slash = current_path + "/" + current_segment if current_path else "/" + current_segment
            slash_test_path = Path(test_slash)

            if slash_test_path.exists() and slash_test_path.is_dir():
                # Current segment forms a valid directory, commit it
                current_path = test_slash
                current_segment = seg
            else:
                # Prefer underscore (keep segment growing)
                current_segment = current_segment + "_" + seg

        # Add the final segment and try underscore/dash variants
        base_path = current_path if current_path else ""

        # Try the final segment as-is (with underscores from our reconstruction)
        final_underscore = base_path + "/" + current_segment
        if Path(final_underscore).exists():
            return Path(final_underscore)

        # Try with remaining dashes converted to original dashes
        # This handles cases like zen-portal
        final_path = self._try_final_segment_variants(base_path, current_segment)
        return final_path or Path(final_underscore)

    def _try_final_segment_variants(self, base_path: str, segment: str) -> Path | None:
        """
        Try different interpretations of underscores in final segment.

        Some underscores might need to be dashes (like zen-portal).
        """
        # If there are underscores, try converting some to dashes
        if "_" in segment:
            # Try all-dash variant
            dash_variant = segment.replace("_", "-")
            test_path = base_path + "/" + dash_variant
            if Path(test_path).exists():
                return Path(test_path)

            # For each underscore position, try dash
            parts = segment.split("_")
            for i in range(len(parts) - 1):
                # Try dash at position i
                variant = "_".join(parts[:i+1]) + "-" + "_".join(parts[i+1:])
                test_path = base_path + "/" + variant
                if Path(test_path).exists():
                    return Path(test_path)

        return None

    def _is_valid_uuid(self, s: str) -> bool:
        """Check if string is a valid UUID format."""
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(s))


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

tmux_discovery = TmuxDiscovery()
session_reconcile = SessionReconcile()
claude_session_discovery = ClaudeSessionDiscovery()
