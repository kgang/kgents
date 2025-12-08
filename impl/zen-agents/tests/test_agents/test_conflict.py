"""Tests for conflict detection and resolution (Contradict/Sublate patterns).

SessionContradict detects conflicts before session creation.
ConflictSublate resolves them or surfaces them for user decision.
"""

import pytest
from datetime import datetime

from zen_agents.models.session import (
    Session,
    SessionState,
    SessionType,
    NewSessionConfig,
)
from zen_agents.agents.conflict import (
    SessionConflict,
    ConflictInput,
    SessionContradict,
    ConflictSublate,
    NameCollisionResolver,
    MAX_SESSIONS,
)
from bootstrap import TensionMode, HoldTension, Synthesis


class TestSessionContradict:
    """Test SessionContradict conflict detection."""

    @pytest.mark.asyncio
    async def test_no_conflict_when_name_unique(self, mock_sessions_list):
        """No conflict when session name is unique."""
        config = NewSessionConfig(
            name="unique-name",
            session_type=SessionType.SHELL,
        )
        contradict = SessionContradict()
        result = await contradict.invoke(ConflictInput(
            config=config,
            existing_sessions=mock_sessions_list,
        ))
        assert result is None

    @pytest.mark.asyncio
    async def test_name_collision_detected(self, mock_sessions_list):
        """Detects name collision with existing session."""
        config = NewSessionConfig(
            name="alpha",  # Same as first session in list
            session_type=SessionType.SHELL,
        )
        contradict = SessionContradict()
        result = await contradict.invoke(ConflictInput(
            config=config,
            existing_sessions=mock_sessions_list,
        ))
        assert result is not None
        assert result.conflict_type == "NAME_COLLISION"
        assert "already exists" in result.description

    @pytest.mark.asyncio
    async def test_limit_exceeded_detected(self):
        """Detects when session limit is exceeded."""
        from uuid import uuid4

        # Create MAX_SESSIONS sessions
        sessions = [
            Session(
                id=uuid4(),
                name=f"session-{i}",
                session_type=SessionType.SHELL,
                state=SessionState.RUNNING,
                tmux_name=f"zen-{i}",
            )
            for i in range(MAX_SESSIONS)
        ]

        config = NewSessionConfig(
            name="one-more",
            session_type=SessionType.SHELL,
        )
        contradict = SessionContradict()
        result = await contradict.invoke(ConflictInput(
            config=config,
            existing_sessions=sessions,
        ))
        assert result is not None
        assert result.conflict_type == "LIMIT_EXCEEDED"
        assert str(MAX_SESSIONS) in result.description

    @pytest.mark.asyncio
    async def test_worktree_conflict_detected(self):
        """Detects worktree conflict (same dir + type + running)."""
        from uuid import uuid4

        existing = Session(
            id=uuid4(),
            name="existing",
            session_type=SessionType.CLAUDE,
            state=SessionState.RUNNING,
            tmux_name="zen-existing",
            working_dir="/path/to/project",
        )

        config = NewSessionConfig(
            name="new-session",
            session_type=SessionType.CLAUDE,  # Same type
            working_dir="/path/to/project",  # Same dir
        )

        contradict = SessionContradict()
        result = await contradict.invoke(ConflictInput(
            config=config,
            existing_sessions=[existing],
        ))
        assert result is not None
        assert result.conflict_type == "WORKTREE_CONFLICT"
        assert "already running" in result.description

    @pytest.mark.asyncio
    async def test_worktree_no_conflict_different_type(self):
        """No worktree conflict when types differ."""
        from uuid import uuid4

        existing = Session(
            id=uuid4(),
            name="existing",
            session_type=SessionType.SHELL,  # Different type
            state=SessionState.RUNNING,
            tmux_name="zen-existing",
            working_dir="/path/to/project",
        )

        config = NewSessionConfig(
            name="new-session",
            session_type=SessionType.CLAUDE,
            working_dir="/path/to/project",
        )

        contradict = SessionContradict()
        result = await contradict.invoke(ConflictInput(
            config=config,
            existing_sessions=[existing],
        ))
        assert result is None

    @pytest.mark.asyncio
    async def test_worktree_no_conflict_session_not_running(self):
        """No worktree conflict when existing session not running."""
        from uuid import uuid4

        existing = Session(
            id=uuid4(),
            name="existing",
            session_type=SessionType.CLAUDE,
            state=SessionState.COMPLETED,  # Not running
            tmux_name="zen-existing",
            working_dir="/path/to/project",
        )

        config = NewSessionConfig(
            name="new-session",
            session_type=SessionType.CLAUDE,
            working_dir="/path/to/project",
        )

        contradict = SessionContradict()
        result = await contradict.invoke(ConflictInput(
            config=config,
            existing_sessions=[existing],
        ))
        assert result is None

    def test_contradict_name(self):
        """SessionContradict has correct name."""
        assert SessionContradict().name == "SessionContradict"


class TestConflictSublate:
    """Test ConflictSublate resolution."""

    @pytest.mark.asyncio
    async def test_name_collision_auto_resolved(self):
        """Name collision is auto-resolved with timestamp."""
        conflict = SessionConflict(
            mode=TensionMode.PRAGMATIC,
            thesis="test-session",
            antithesis=["test-session"],
            description="Session 'test-session' already exists",
            conflict_type="NAME_COLLISION",
            suggested_resolution="test-session-123456",
        )

        sublate = ConflictSublate()
        result = await sublate.invoke(conflict)

        assert isinstance(result, Synthesis)
        assert result.result == "test-session-123456"
        assert "collision" in result.explanation.lower()

    @pytest.mark.asyncio
    async def test_limit_exceeded_held(self):
        """Limit exceeded conflict is held for user decision."""
        conflict = SessionConflict(
            mode=TensionMode.PRAGMATIC,
            thesis="new-session",
            antithesis="Current count: 10",
            description="Session limit (10) reached",
            conflict_type="LIMIT_EXCEEDED",
            suggested_resolution="Kill existing sessions",
        )

        sublate = ConflictSublate()
        result = await sublate.invoke(conflict)

        assert isinstance(result, HoldTension)
        assert "limit" in result.reason.lower()
        assert len(result.revisit_conditions) > 0

    @pytest.mark.asyncio
    async def test_worktree_conflict_held(self):
        """Worktree conflict is held for user decision."""
        conflict = SessionConflict(
            mode=TensionMode.PRAGMATIC,
            thesis="new-session",
            antithesis="existing-session",
            description="Session already running in directory",
            conflict_type="WORKTREE_CONFLICT",
            suggested_resolution="Attach to existing",
        )

        sublate = ConflictSublate()
        result = await sublate.invoke(conflict)

        assert isinstance(result, HoldTension)
        assert "already running" in result.reason.lower()

    def test_sublate_name(self):
        """ConflictSublate has correct name."""
        assert ConflictSublate().name == "ConflictSublate"


class TestNameCollisionResolver:
    """Test NameCollisionResolver agent."""

    @pytest.mark.asyncio
    async def test_no_change_when_unique(self):
        """Config unchanged when name is unique."""
        config = NewSessionConfig(
            name="unique",
            session_type=SessionType.SHELL,
        )
        resolver = NameCollisionResolver(existing_names={"alpha", "beta"})
        result = await resolver.invoke(config)
        assert result.name == "unique"

    @pytest.mark.asyncio
    async def test_appends_timestamp_on_collision(self):
        """Appends timestamp when name collides."""
        config = NewSessionConfig(
            name="alpha",
            session_type=SessionType.SHELL,
        )
        resolver = NameCollisionResolver(existing_names={"alpha", "beta"})
        result = await resolver.invoke(config)
        assert result.name.startswith("alpha-")
        assert result.name != "alpha"
        # Other fields preserved
        assert result.session_type == config.session_type

    def test_resolver_name(self):
        """NameCollisionResolver has correct name."""
        resolver = NameCollisionResolver(existing_names=set())
        assert resolver.name == "NameCollisionResolver"
