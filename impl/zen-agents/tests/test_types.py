"""Tests for zen-agents types"""

import pytest
from datetime import datetime

from zen_agents.types import (
    SessionConfig,
    SessionType,
    SessionState,
    Session,
    TmuxSession,
    SessionVerdict,
)


class TestSessionConfig:
    def test_create_config(self):
        config = SessionConfig(
            name="my-session",
            session_type=SessionType.CLAUDE,
        )
        assert config.name == "my-session"
        assert config.session_type == SessionType.CLAUDE
        assert config.working_dir is None
        assert config.env == {}
        assert config.tags == []

    def test_config_with_all_fields(self):
        config = SessionConfig(
            name="test",
            session_type=SessionType.SHELL,
            working_dir="/home/user",
            command="bash",
            env={"FOO": "bar"},
            model="claude-opus",
            system_prompt="Be helpful",
            max_tokens=1000,
            tags=["dev", "test"],
            priority=5,
        )
        assert config.working_dir == "/home/user"
        assert config.env == {"FOO": "bar"}
        assert config.model == "claude-opus"
        assert config.priority == 5


class TestSession:
    def test_create_session(self, sample_config):
        session = Session(
            id="test-123",
            config=sample_config,
            state=SessionState.CREATING,
        )
        assert session.id == "test-123"
        assert session.state == SessionState.CREATING
        assert session.tmux is None
        assert session.is_alive()

    def test_is_alive(self, sample_config):
        for state, expected in [
            (SessionState.CREATING, True),
            (SessionState.RUNNING, True),
            (SessionState.PAUSED, True),
            (SessionState.COMPLETED, False),
            (SessionState.FAILED, False),
            (SessionState.UNKNOWN, False),
        ]:
            session = Session(id="test", config=sample_config, state=state)
            assert session.is_alive() == expected, f"State {state} should be alive={expected}"


class TestSessionVerdict:
    def test_accept(self):
        verdict = SessionVerdict.accept()
        assert verdict.valid is True
        assert verdict.issues == []

    def test_reject(self):
        verdict = SessionVerdict.reject("Invalid name", "Missing directory")
        assert verdict.valid is False
        assert "Invalid name" in verdict.issues
        assert "Missing directory" in verdict.issues


class TestTmuxSession:
    def test_create_tmux_session(self):
        tmux = TmuxSession(
            id="zen-test",
            name="test",
            pane_id="zen-test:0.0",
            created_at=datetime.now(),
        )
        assert tmux.id == "zen-test"
        assert tmux.is_attached is False
