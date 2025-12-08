"""Tests for TmuxService.

TmuxService wraps tmux operations as async functions.
These tests use mocks since actual tmux may not be available.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from zen_agents.services.tmux import TmuxService, TmuxConfig


@pytest.fixture
def tmux_service():
    """Create TmuxService with default config."""
    return TmuxService()


@pytest.fixture
def mock_subprocess():
    """Mock asyncio.create_subprocess_exec."""
    with patch('asyncio.create_subprocess_exec') as mock:
        process = AsyncMock()
        process.returncode = 0
        process.communicate.return_value = (b"output", b"")
        mock.return_value = process
        yield mock


class TestTmuxConfig:
    """Test TmuxConfig dataclass."""

    def test_default_values(self):
        """Default config has sensible values."""
        config = TmuxConfig()
        assert config.scrollback_lines == 50000
        assert config.default_shell == "/bin/bash"

    def test_custom_values(self):
        """Custom config values are used."""
        config = TmuxConfig(scrollback_lines=10000, default_shell="/bin/zsh")
        assert config.scrollback_lines == 10000
        assert config.default_shell == "/bin/zsh"


class TestRunTmux:
    """Test internal _run_tmux method."""

    @pytest.mark.asyncio
    async def test_runs_tmux_command(self, tmux_service, mock_subprocess):
        """Runs tmux with provided args."""
        await tmux_service._run_tmux("list-sessions")
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0]
        assert args[0] == "tmux"
        assert "list-sessions" in args

    @pytest.mark.asyncio
    async def test_returns_tuple(self, tmux_service, mock_subprocess):
        """Returns (returncode, stdout, stderr) tuple."""
        result = await tmux_service._run_tmux("list-sessions")
        assert isinstance(result, tuple)
        assert len(result) == 3
        code, stdout, stderr = result
        assert code == 0
        assert stdout == "output"

    @pytest.mark.asyncio
    async def test_handles_no_server(self, tmux_service, mock_subprocess):
        """Handles 'no server running' gracefully."""
        process = mock_subprocess.return_value
        process.returncode = 1
        process.communicate.return_value = (b"", b"no server running")

        result = await tmux_service._run_tmux("list-sessions")
        assert result[0] == 1


class TestCreateSession:
    """Test session creation."""

    @pytest.mark.asyncio
    async def test_creates_session(self, tmux_service, mock_subprocess):
        """Creates tmux session with name."""
        result = await tmux_service.create_session(name="test-session")
        assert result is True
        # Verify new-session was called
        call_args = mock_subprocess.call_args_list[0][0]
        assert "new-session" in call_args
        assert "-s" in call_args

    @pytest.mark.asyncio
    async def test_creates_with_working_dir(self, tmux_service, mock_subprocess):
        """Creates session with working directory."""
        await tmux_service.create_session(
            name="test",
            working_dir="/tmp/test"
        )
        call_args = mock_subprocess.call_args_list[0][0]
        assert "-c" in call_args
        assert "/tmp/test" in call_args

    @pytest.mark.asyncio
    async def test_creates_with_command(self, tmux_service, mock_subprocess):
        """Creates session with custom command."""
        await tmux_service.create_session(
            name="test",
            command="python script.py"
        )
        call_args = mock_subprocess.call_args_list[0][0]
        assert "python script.py" in call_args

    @pytest.mark.asyncio
    async def test_returns_false_on_failure(self, tmux_service, mock_subprocess):
        """Returns False when creation fails."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.create_session(name="test")
        assert result is False


class TestKillSession:
    """Test session killing."""

    @pytest.mark.asyncio
    async def test_kills_session(self, tmux_service, mock_subprocess):
        """Kills tmux session by name."""
        result = await tmux_service.kill_session(name="test-session")
        assert result is True
        call_args = mock_subprocess.call_args[0]
        assert "kill-session" in call_args
        assert "-t" in call_args
        assert "test-session" in call_args

    @pytest.mark.asyncio
    async def test_returns_false_on_failure(self, tmux_service, mock_subprocess):
        """Returns False when kill fails."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.kill_session(name="nonexistent")
        assert result is False


class TestSessionExists:
    """Test session existence checking."""

    @pytest.mark.asyncio
    async def test_returns_true_when_exists(self, tmux_service, mock_subprocess):
        """Returns True when session exists."""
        result = await tmux_service.session_exists(name="test")
        assert result is True
        call_args = mock_subprocess.call_args[0]
        assert "has-session" in call_args

    @pytest.mark.asyncio
    async def test_returns_false_when_not_exists(self, tmux_service, mock_subprocess):
        """Returns False when session doesn't exist."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.session_exists(name="nonexistent")
        assert result is False


class TestIsSessionAlive:
    """Test session aliveness checking."""

    @pytest.mark.asyncio
    async def test_returns_false_when_session_not_exists(self, tmux_service, mock_subprocess):
        """Returns False when session doesn't exist."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.is_session_alive(name="nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_checks_pane_pid(self, tmux_service, mock_subprocess):
        """Checks pane PID to determine aliveness."""
        # First call: has-session succeeds
        # Second call: list-panes returns PID
        mock_subprocess.return_value.communicate.side_effect = [
            (b"", b""),  # has-session
            (b"12345\n", b""),  # list-panes
        ]
        mock_subprocess.return_value.returncode = 0

        with patch('os.kill') as mock_kill:
            mock_kill.return_value = None  # Process exists
            result = await tmux_service.is_session_alive(name="test")
            # Should call os.kill(12345, 0) to check if alive
            mock_kill.assert_called()


class TestGetExitCode:
    """Test exit code retrieval."""

    @pytest.mark.asyncio
    async def test_returns_exit_code(self, tmux_service, mock_subprocess):
        """Returns exit code from pane."""
        mock_subprocess.return_value.communicate.return_value = (b"0\n", b"")
        result = await tmux_service.get_exit_code(name="test")
        assert result == 0

    @pytest.mark.asyncio
    async def test_returns_none_on_failure(self, tmux_service, mock_subprocess):
        """Returns None when can't get exit code."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.get_exit_code(name="test")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_for_non_numeric(self, tmux_service, mock_subprocess):
        """Returns None for non-numeric exit code."""
        mock_subprocess.return_value.communicate.return_value = (b"running\n", b"")
        result = await tmux_service.get_exit_code(name="test")
        assert result is None


class TestSendKeys:
    """Test sending keys to session."""

    @pytest.mark.asyncio
    async def test_sends_keys(self, tmux_service, mock_subprocess):
        """Sends keys to session."""
        result = await tmux_service.send_keys(
            name="test",
            keys="echo hello"
        )
        assert result is True
        call_args = mock_subprocess.call_args[0]
        assert "send-keys" in call_args
        assert "echo hello" in call_args

    @pytest.mark.asyncio
    async def test_sends_enter_by_default(self, tmux_service, mock_subprocess):
        """Sends Enter key by default."""
        await tmux_service.send_keys(name="test", keys="ls")
        call_args = mock_subprocess.call_args[0]
        assert "Enter" in call_args

    @pytest.mark.asyncio
    async def test_no_enter_when_disabled(self, tmux_service, mock_subprocess):
        """Doesn't send Enter when disabled."""
        await tmux_service.send_keys(name="test", keys="ls", enter=False)
        call_args = mock_subprocess.call_args[0]
        assert "Enter" not in call_args


class TestCapturePane:
    """Test pane content capture."""

    @pytest.mark.asyncio
    async def test_captures_pane(self, tmux_service, mock_subprocess):
        """Captures pane content."""
        mock_subprocess.return_value.communicate.return_value = (
            b"line1\nline2\nline3\n",
            b""
        )
        result = await tmux_service.capture_pane(name="test")
        assert "line1" in result
        assert "line2" in result

    @pytest.mark.asyncio
    async def test_returns_empty_on_failure(self, tmux_service, mock_subprocess):
        """Returns empty string on failure."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.capture_pane(name="nonexistent")
        assert result == ""


class TestListSessions:
    """Test session listing."""

    @pytest.mark.asyncio
    async def test_lists_sessions(self, tmux_service, mock_subprocess):
        """Lists all tmux sessions."""
        mock_subprocess.return_value.communicate.return_value = (
            b"session1\nsession2\nsession3\n",
            b""
        )
        result = await tmux_service.list_sessions()
        assert len(result) == 3
        assert "session1" in result
        assert "session2" in result

    @pytest.mark.asyncio
    async def test_returns_empty_on_failure(self, tmux_service, mock_subprocess):
        """Returns empty list on failure."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.list_sessions()
        assert result == []


class TestResurrectSession:
    """Test session resurrection."""

    @pytest.mark.asyncio
    async def test_resurrects_session(self, tmux_service, mock_subprocess):
        """Resurrects dead session."""
        result = await tmux_service.resurrect_session(name="test")
        assert result is True
        call_args = mock_subprocess.call_args[0]
        assert "respawn-pane" in call_args

    @pytest.mark.asyncio
    async def test_returns_false_on_failure(self, tmux_service, mock_subprocess):
        """Returns False when resurrection fails."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.resurrect_session(name="test")
        assert result is False


class TestAttachSession:
    """Test session attachment check."""

    @pytest.mark.asyncio
    async def test_returns_true_if_exists(self, tmux_service, mock_subprocess):
        """Returns True if session exists (ready for attach)."""
        result = await tmux_service.attach_session(name="test")
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_if_not_exists(self, tmux_service, mock_subprocess):
        """Returns False if session doesn't exist."""
        mock_subprocess.return_value.returncode = 1
        result = await tmux_service.attach_session(name="nonexistent")
        assert result is False
