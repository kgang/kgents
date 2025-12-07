"""
pytest fixtures for zen-agents tests
"""

import pytest
import tempfile
from pathlib import Path

from zen_agents.types import (
    SessionConfig,
    SessionType,
    SessionState,
    Session,
    TmuxSession,
    ZenGroundState,
    ConfigLayer,
)
from zen_agents.ground import ZenGround
from datetime import datetime


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config():
    """Create a sample SessionConfig."""
    return SessionConfig(
        name="test-session",
        session_type=SessionType.SHELL,
        working_dir="/tmp",
        command="echo hello",
        tags=["test"],
    )


@pytest.fixture
def sample_session(sample_config):
    """Create a sample Session."""
    return Session(
        id="test-session-abc123",
        config=sample_config,
        state=SessionState.RUNNING,
        tmux=TmuxSession(
            id="zen-test-session-abc123",
            name="test-session",
            pane_id="zen-test-session-abc123:0.0",
            created_at=datetime.now(),
            is_attached=False,
        ),
        started_at=datetime.now(),
    )


@pytest.fixture
def sample_ground_state(sample_session):
    """Create a sample ZenGroundState."""
    return ZenGroundState(
        config_cascade=[
            ConfigLayer(name="global", values={"default_shell": "/bin/zsh"}),
        ],
        sessions={sample_session.id: sample_session},
        tmux_sessions=[sample_session.tmux] if sample_session.tmux else [],
        default_session_type=SessionType.CLAUDE,
        auto_discovery=True,
        max_sessions=10,
        last_updated=datetime.now(),
    )


@pytest.fixture
def empty_ground_state():
    """Create an empty ZenGroundState."""
    return ZenGroundState(
        config_cascade=[
            ConfigLayer(name="global", values={"default_shell": "/bin/zsh"}),
        ],
        sessions={},
        tmux_sessions=[],
        default_session_type=SessionType.CLAUDE,
        auto_discovery=True,
        max_sessions=10,
        last_updated=datetime.now(),
    )
