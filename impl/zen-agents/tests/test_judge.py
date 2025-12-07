"""Tests for ZenJudge agent"""

import pytest
from zen_agents.types import SessionConfig, SessionType
from zen_agents.judge import ZenJudge, zen_judge


@pytest.mark.asyncio
class TestZenJudge:
    async def test_valid_config(self, empty_ground_state):
        judge = zen_judge.with_ground(empty_ground_state)
        config = SessionConfig(
            name="valid-session",
            session_type=SessionType.SHELL,
            working_dir="/tmp",
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is True
        assert verdict.issues == []

    async def test_invalid_name_spaces(self, empty_ground_state):
        judge = zen_judge.with_ground(empty_ground_state)
        config = SessionConfig(
            name="invalid name with spaces",
            session_type=SessionType.SHELL,
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is False
        assert any("Invalid name" in issue for issue in verdict.issues)

    async def test_invalid_name_special_chars(self, empty_ground_state):
        judge = zen_judge.with_ground(empty_ground_state)
        config = SessionConfig(
            name="bad!@#$%",
            session_type=SessionType.SHELL,
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is False

    async def test_empty_name(self, empty_ground_state):
        judge = zen_judge.with_ground(empty_ground_state)
        config = SessionConfig(
            name="",
            session_type=SessionType.SHELL,
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is False
        assert any("empty" in issue.lower() for issue in verdict.issues)

    async def test_name_too_long(self, empty_ground_state):
        judge = zen_judge.with_ground(empty_ground_state)
        config = SessionConfig(
            name="a" * 100,  # Way too long
            session_type=SessionType.SHELL,
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is False
        assert any("long" in issue.lower() for issue in verdict.issues)

    async def test_name_collision(self, sample_ground_state, sample_session):
        judge = zen_judge.with_ground(sample_ground_state)
        # Create config with same name as existing session
        config = SessionConfig(
            name=sample_session.config.name,
            session_type=SessionType.SHELL,
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is False
        assert any("exists" in issue.lower() for issue in verdict.issues)

    async def test_resource_limit(self, sample_ground_state, sample_config):
        # Set max_sessions to current count
        sample_ground_state.max_sessions = len(sample_ground_state.sessions)
        judge = zen_judge.with_ground(sample_ground_state)

        config = SessionConfig(
            name="new-session",
            session_type=SessionType.SHELL,
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is False
        assert any("max" in issue.lower() for issue in verdict.issues)

    async def test_nonexistent_working_dir(self, empty_ground_state):
        judge = zen_judge.with_ground(empty_ground_state)
        config = SessionConfig(
            name="test-session",
            session_type=SessionType.SHELL,
            working_dir="/nonexistent/path/that/should/not/exist",
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is False
        assert any("directory" in issue.lower() for issue in verdict.issues)

    async def test_dangerous_command(self, empty_ground_state):
        judge = zen_judge.with_ground(empty_ground_state)
        config = SessionConfig(
            name="test-session",
            session_type=SessionType.CUSTOM,
            command="rm -rf /",
        )
        verdict = await judge.invoke(config)
        assert verdict.valid is False
        assert any("dangerous" in issue.lower() for issue in verdict.issues)
