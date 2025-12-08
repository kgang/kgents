"""Tests for SessionPersistence.

SessionPersistence saves and loads sessions across TUI restarts.
"""

import pytest
import json
from datetime import datetime
from uuid import uuid4
from pathlib import Path

from zen_agents.models.session import Session, SessionState, SessionType
from zen_agents.services.persistence import (
    SessionPersistence,
    DateTimeEncoder,
    CONFIG_DIR,
    SESSIONS_FILE,
)


class TestDateTimeEncoder:
    """Test custom JSON encoder."""

    def test_encodes_datetime(self):
        """Encodes datetime as ISO format."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = json.dumps({"date": dt}, cls=DateTimeEncoder)
        assert "2024-01-15T10:30:00" in result

    def test_encodes_uuid(self):
        """Encodes UUID as string."""
        uid = uuid4()
        result = json.dumps({"id": uid}, cls=DateTimeEncoder)
        assert str(uid) in result

    def test_encodes_session_state(self):
        """Encodes SessionState as value."""
        result = json.dumps({"state": SessionState.RUNNING}, cls=DateTimeEncoder)
        assert "running" in result

    def test_encodes_session_type(self):
        """Encodes SessionType as value."""
        result = json.dumps({"type": SessionType.CLAUDE}, cls=DateTimeEncoder)
        assert "claude" in result


class TestSessionPersistence:
    """Test SessionPersistence class."""

    def test_init_creates_directory(self, tmp_path):
        """Initializing creates parent directory."""
        sessions_file = tmp_path / "subdir" / "sessions.json"
        persistence = SessionPersistence(sessions_file)
        assert sessions_file.parent.exists()

    def test_default_path(self):
        """Default path is in ~/.config/zen-agents/."""
        persistence = SessionPersistence()
        assert persistence.sessions_file == SESSIONS_FILE
        assert "zen-agents" in str(persistence.sessions_file)


class TestSave:
    """Test saving sessions."""

    def test_save_empty_list(self, persistence, temp_sessions_file):
        """Saves empty list."""
        persistence.save([])
        assert temp_sessions_file.exists()
        data = json.loads(temp_sessions_file.read_text())
        assert data == []

    def test_save_single_session(self, persistence, temp_sessions_file, mock_session):
        """Saves single session."""
        persistence.save([mock_session])

        data = json.loads(temp_sessions_file.read_text())
        assert len(data) == 1
        assert data[0]["name"] == mock_session.name
        assert data[0]["session_type"] == mock_session.session_type.value
        assert data[0]["state"] == mock_session.state.value

    def test_save_multiple_sessions(self, persistence, temp_sessions_file):
        """Saves multiple sessions."""
        sessions = [
            Session(
                id=uuid4(),
                name=f"session-{i}",
                session_type=SessionType.SHELL,
                state=SessionState.RUNNING,
                tmux_name=f"zen-{i}",
            )
            for i in range(3)
        ]
        persistence.save(sessions)

        data = json.loads(temp_sessions_file.read_text())
        assert len(data) == 3

    def test_save_with_optional_fields(self, persistence, temp_sessions_file):
        """Saves optional fields when present."""
        session = Session(
            id=uuid4(),
            name="test",
            session_type=SessionType.SHELL,
            state=SessionState.FAILED,
            tmux_name="zen-test",
            exit_code=1,
            error_message="Process crashed",
            working_dir="/home/user/project",
            command="python script.py",
            metadata={"key": "value"},
        )
        persistence.save([session])

        data = json.loads(temp_sessions_file.read_text())
        assert data[0]["exit_code"] == 1
        assert data[0]["error_message"] == "Process crashed"
        assert data[0]["working_dir"] == "/home/user/project"
        assert data[0]["command"] == "python script.py"
        assert data[0]["metadata"] == {"key": "value"}

    def test_save_omits_none_optionals(self, persistence, temp_sessions_file, mock_session):
        """Omits optional fields when None."""
        mock_session.exit_code = None
        mock_session.error_message = None
        persistence.save([mock_session])

        data = json.loads(temp_sessions_file.read_text())
        assert "exit_code" not in data[0]
        assert "error_message" not in data[0]


class TestLoad:
    """Test loading sessions."""

    def test_load_nonexistent_file(self, persistence):
        """Returns empty list for nonexistent file."""
        result = persistence.load()
        assert result == []

    def test_load_empty_file(self, persistence, temp_sessions_file):
        """Returns empty list for empty JSON array."""
        temp_sessions_file.write_text("[]")
        result = persistence.load()
        assert result == []

    def test_load_single_session(self, persistence, temp_sessions_file, mock_session):
        """Loads single session."""
        persistence.save([mock_session])
        result = persistence.load()

        assert len(result) == 1
        assert result[0].name == mock_session.name
        assert result[0].session_type == mock_session.session_type
        assert result[0].state == mock_session.state
        assert result[0].id == mock_session.id

    def test_load_preserves_uuid(self, persistence, temp_sessions_file, mock_session):
        """Loaded session has same UUID."""
        persistence.save([mock_session])
        result = persistence.load()
        assert result[0].id == mock_session.id

    def test_load_preserves_timestamps(self, persistence, temp_sessions_file, mock_session):
        """Loaded session has preserved timestamps."""
        persistence.save([mock_session])
        result = persistence.load()
        # Datetime comparison (may have microsecond diff due to serialization)
        assert result[0].created_at.date() == mock_session.created_at.date()

    def test_load_with_optional_fields(self, persistence, temp_sessions_file):
        """Loads optional fields correctly."""
        session = Session(
            id=uuid4(),
            name="test",
            session_type=SessionType.SHELL,
            state=SessionState.FAILED,
            tmux_name="zen-test",
            exit_code=1,
            error_message="Crashed",
            metadata={"domain": "test"},
        )
        persistence.save([session])
        result = persistence.load()

        assert result[0].exit_code == 1
        assert result[0].error_message == "Crashed"
        assert result[0].metadata == {"domain": "test"}

    def test_load_corrupted_json_returns_empty(self, persistence, temp_sessions_file):
        """Returns empty list for corrupted JSON."""
        temp_sessions_file.write_text("not valid json {{{")
        result = persistence.load()
        assert result == []

    def test_load_missing_fields_returns_empty(self, persistence, temp_sessions_file):
        """Returns empty list when required fields missing."""
        temp_sessions_file.write_text('[{"name": "test"}]')  # Missing required fields
        result = persistence.load()
        assert result == []


class TestDelete:
    """Test deleting persistence file."""

    def test_delete_existing_file(self, persistence, temp_sessions_file, mock_session):
        """Deletes existing persistence file."""
        persistence.save([mock_session])
        assert temp_sessions_file.exists()

        persistence.delete()
        assert not temp_sessions_file.exists()

    def test_delete_nonexistent_file_safe(self, persistence, temp_sessions_file):
        """Deleting nonexistent file doesn't raise."""
        if temp_sessions_file.exists():
            temp_sessions_file.unlink()

        # Should not raise
        persistence.delete()


class TestExists:
    """Test existence checking."""

    def test_exists_returns_true(self, persistence, temp_sessions_file, mock_session):
        """exists() returns True when file exists."""
        persistence.save([mock_session])
        assert persistence.exists() is True

    def test_exists_returns_false(self, persistence, temp_sessions_file):
        """exists() returns False when file doesn't exist."""
        if temp_sessions_file.exists():
            temp_sessions_file.unlink()
        assert persistence.exists() is False


class TestRoundTrip:
    """Test save/load round-trip integrity."""

    def test_full_roundtrip(self, persistence, temp_sessions_file):
        """Full save/load preserves all data."""
        original = Session(
            id=uuid4(),
            name="roundtrip-test",
            session_type=SessionType.ROBIN,
            state=SessionState.RUNNING,
            tmux_name="zen-roundtrip",
            working_dir="/tmp/test",
            command="robin",
            metadata={"domain": "neuroscience", "observations": ["obs1", "obs2"]},
        )

        persistence.save([original])
        loaded = persistence.load()[0]

        assert loaded.id == original.id
        assert loaded.name == original.name
        assert loaded.session_type == original.session_type
        assert loaded.state == original.state
        assert loaded.tmux_name == original.tmux_name
        assert loaded.working_dir == original.working_dir
        assert loaded.command == original.command
        assert loaded.metadata == original.metadata
