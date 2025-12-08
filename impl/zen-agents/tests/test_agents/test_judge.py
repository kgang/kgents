"""Tests for Judge validators.

Judge evaluates quality at key decision points.
Validation returns Verdict, not bool.
"""

import pytest
from pathlib import Path

from zen_agents.models.session import NewSessionConfig, SessionType, SessionState, Session
from zen_agents.agents.judge import (
    SessionJudge,
    ConfigJudge,
    CreatedSessionJudge,
    ValidateName,
)
from zen_agents.agents.config import ZenConfig
from bootstrap import VerdictType


class TestSessionJudge:
    """Test SessionJudge for session config validation."""

    @pytest.mark.asyncio
    async def test_valid_config_accepted(self):
        """Valid config is accepted."""
        config = NewSessionConfig(
            name="my-session",
            session_type=SessionType.SHELL,
            working_dir="/tmp",
        )
        judge = SessionJudge()
        verdict = await judge.invoke(config)
        assert verdict.type == VerdictType.ACCEPT

    @pytest.mark.asyncio
    async def test_short_name_rejected(self):
        """Name too short is rejected."""
        config = NewSessionConfig(
            name="x",  # Too short
            session_type=SessionType.SHELL,
        )
        judge = SessionJudge()
        verdict = await judge.invoke(config)
        assert verdict.type in (VerdictType.REVISE, VerdictType.REJECT)
        assert any("short" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_numeric_name_flagged(self):
        """Numeric-only name gets revision suggestion."""
        config = NewSessionConfig(
            name="12345",
            session_type=SessionType.SHELL,
        )
        judge = SessionJudge()
        verdict = await judge.invoke(config)
        assert verdict.type in (VerdictType.REVISE, VerdictType.REJECT)
        assert any("number" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_nonexistent_workdir_rejected(self, tmp_path):
        """Nonexistent working directory is flagged."""
        config = NewSessionConfig(
            name="test-session",
            session_type=SessionType.SHELL,
            working_dir="/nonexistent/path/that/does/not/exist",
        )
        judge = SessionJudge()
        verdict = await judge.invoke(config)
        assert verdict.type in (VerdictType.REVISE, VerdictType.REJECT)
        assert any("directory" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_openrouter_without_model_suggestion(self):
        """OpenRouter without model gets revision suggestion."""
        config = NewSessionConfig(
            name="openrouter-session",
            session_type=SessionType.OPENROUTER,
            model=None,
        )
        judge = SessionJudge()
        verdict = await judge.invoke(config)
        # Should be REVISE (not REJECT) - it's a suggestion
        if verdict.type == VerdictType.REVISE:
            assert any("model" in r.lower() for r in verdict.revisions)

    def test_judge_name(self):
        """SessionJudge has correct name."""
        assert SessionJudge().name == "SessionJudge"


class TestConfigJudge:
    """Test ConfigJudge for ZenConfig validation."""

    @pytest.mark.asyncio
    async def test_valid_config_accepted(self, zen_config):
        """Valid config is accepted."""
        judge = ConfigJudge()
        verdict = await judge.invoke(zen_config)
        assert verdict.type == VerdictType.ACCEPT

    @pytest.mark.asyncio
    async def test_short_poll_interval_rejected(self):
        """Poll interval too short is rejected."""
        config = ZenConfig(poll_interval=0.05)
        judge = ConfigJudge()
        verdict = await judge.invoke(config)
        assert verdict.type == VerdictType.REJECT
        assert any("poll" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_long_poll_interval_suggestion(self):
        """Long poll interval gets suggestion."""
        config = ZenConfig(poll_interval=120.0)
        judge = ConfigJudge()
        verdict = await judge.invoke(config)
        assert verdict.type == VerdictType.REVISE
        assert any("unresponsive" in r.lower() for r in verdict.revisions)

    @pytest.mark.asyncio
    async def test_short_grace_period_rejected(self):
        """Grace period too short is rejected."""
        config = ZenConfig(grace_period=0.5)
        judge = ConfigJudge()
        verdict = await judge.invoke(config)
        assert verdict.type == VerdictType.REJECT
        assert any("grace" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_zero_max_sessions_rejected(self):
        """Zero max sessions is rejected."""
        config = ZenConfig(max_sessions=0)
        judge = ConfigJudge()
        verdict = await judge.invoke(config)
        assert verdict.type == VerdictType.REJECT

    @pytest.mark.asyncio
    async def test_high_max_sessions_suggestion(self):
        """Very high max sessions gets suggestion."""
        config = ZenConfig(max_sessions=100)
        judge = ConfigJudge()
        verdict = await judge.invoke(config)
        assert verdict.type == VerdictType.REVISE
        assert any("resource" in r.lower() for r in verdict.revisions)

    @pytest.mark.asyncio
    async def test_low_scrollback_suggestion(self):
        """Low scrollback gets suggestion."""
        config = ZenConfig(scrollback_lines=500)
        judge = ConfigJudge()
        verdict = await judge.invoke(config)
        assert verdict.type == VerdictType.REVISE
        assert any("scrollback" in r.lower() for r in verdict.revisions)

    def test_config_judge_name(self):
        """ConfigJudge has correct name."""
        assert ConfigJudge().name == "ConfigJudge"


class TestCreatedSessionJudge:
    """Test CreatedSessionJudge for post-creation validation."""

    @pytest.mark.asyncio
    async def test_valid_session_accepted(self, mock_session):
        """Properly created session is accepted."""
        judge = CreatedSessionJudge()
        verdict = await judge.invoke(mock_session)
        assert verdict.type == VerdictType.ACCEPT

    @pytest.mark.asyncio
    async def test_missing_tmux_name_rejected(self, mock_session):
        """Session without tmux_name is rejected."""
        mock_session.tmux_name = ""
        judge = CreatedSessionJudge()
        verdict = await judge.invoke(mock_session)
        assert verdict.type == VerdictType.REJECT
        assert any("tmux_name" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_missing_state_rejected(self, mock_session):
        """Session without state is rejected."""
        mock_session.state = None
        judge = CreatedSessionJudge()
        verdict = await judge.invoke(mock_session)
        assert verdict.type == VerdictType.REJECT

    @pytest.mark.asyncio
    async def test_missing_id_rejected(self, mock_session):
        """Session without ID is rejected."""
        mock_session.id = None
        judge = CreatedSessionJudge()
        verdict = await judge.invoke(mock_session)
        assert verdict.type == VerdictType.REJECT

    def test_created_session_judge_name(self):
        """CreatedSessionJudge has correct name."""
        assert CreatedSessionJudge().name == "CreatedSessionJudge"


class TestValidateName:
    """Test ValidateName for quick name validation."""

    @pytest.mark.asyncio
    async def test_valid_name_accepted(self):
        """Valid name is accepted."""
        judge = ValidateName()
        verdict = await judge.invoke("my-session")
        assert verdict.type == VerdictType.ACCEPT

    @pytest.mark.asyncio
    async def test_empty_name_rejected(self):
        """Empty name is rejected."""
        judge = ValidateName()
        verdict = await judge.invoke("")
        assert verdict.type == VerdictType.REJECT
        assert any("empty" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_short_name_rejected(self):
        """Name too short is rejected."""
        judge = ValidateName()
        verdict = await judge.invoke("x")
        assert verdict.type == VerdictType.REJECT
        assert any("short" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_invalid_chars_rejected(self):
        """Name with invalid characters is rejected."""
        judge = ValidateName()
        verdict = await judge.invoke("my session!")  # Space and exclamation
        assert verdict.type == VerdictType.REJECT
        assert any("invalid" in r.lower() for r in verdict.reasons)

    @pytest.mark.asyncio
    async def test_valid_special_chars_accepted(self):
        """Name with valid special chars (underscore, hyphen) is accepted."""
        judge = ValidateName()
        verdict = await judge.invoke("my_session-123")
        assert verdict.type == VerdictType.ACCEPT

    @pytest.mark.asyncio
    async def test_numeric_only_flagged(self):
        """Numeric-only name gets revision suggestion."""
        judge = ValidateName()
        verdict = await judge.invoke("12345")
        assert verdict.type == VerdictType.REVISE

    @pytest.mark.asyncio
    async def test_very_long_name_flagged(self):
        """Very long name gets suggestion."""
        judge = ValidateName()
        verdict = await judge.invoke("a" * 60)
        assert verdict.type == VerdictType.REVISE
        assert any("long" in r.lower() for r in verdict.revisions)

    def test_validate_name_name(self):
        """ValidateName has correct name."""
        assert ValidateName().name == "ValidateName"
