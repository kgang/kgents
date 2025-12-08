"""Tests for pipeline composition.

CreateSessionPipeline uses >> composition: "Compose, Don't Concatenate".
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from zen_agents.models.session import NewSessionConfig, SessionType, SessionState, Session
from zen_agents.agents.config import ZenConfig
from zen_agents.agents.pipelines.create import (
    CreateContext,
    SpawnResult,
    ValidateConfig,
    ValidateLimit,
    DetectConflicts,
    ResolveConflicts,
    SpawnTmux,
    DetectInitialState,
    CreateSessionPipeline,
    create_session_pipeline,
    ValidationError,
    ConflictError,
)


class TestValidateConfig:
    """Test ValidateConfig pipeline stage."""

    @pytest.mark.asyncio
    async def test_valid_config_passes(self):
        """Valid config passes validation."""
        config = NewSessionConfig(
            name="test-session",
            session_type=SessionType.SHELL,
            working_dir="/tmp",
        )
        validator = ValidateConfig()
        result = await validator.invoke(config)
        assert result == config

    @pytest.mark.asyncio
    async def test_invalid_config_raises(self):
        """Invalid config raises ValidationError."""
        # Need > 2 reasons to trigger REJECT (short name, numeric, bad path)
        config = NewSessionConfig(
            name="1",  # Too short (reason 1) AND numeric (reason 2)
            session_type=SessionType.SHELL,
            working_dir="/nonexistent/path/that/does/not/exist",  # Invalid (reason 3)
        )
        validator = ValidateConfig()
        with pytest.raises(ValidationError):
            await validator.invoke(config)

    def test_validator_name(self):
        """ValidateConfig has correct name."""
        assert ValidateConfig().name == "ValidateConfig"


class TestValidateLimit:
    """Test ValidateLimit pipeline stage."""

    @pytest.mark.asyncio
    async def test_within_limit_passes(self, create_context):
        """Context within limit passes."""
        validator = ValidateLimit()
        result = await validator.invoke(create_context)
        assert result == create_context

    @pytest.mark.asyncio
    async def test_exceeds_limit_raises(self, create_context):
        """Exceeding limit raises ValidationError."""
        # Add sessions to exceed limit
        create_context.zen_config.max_sessions = 2
        create_context.existing_sessions = [MagicMock(), MagicMock(), MagicMock()]

        validator = ValidateLimit()
        with pytest.raises(ValidationError) as exc_info:
            await validator.invoke(create_context)
        assert "limit" in str(exc_info.value).lower()

    def test_validate_limit_name(self):
        """ValidateLimit has correct name."""
        assert ValidateLimit().name == "ValidateLimit"


class TestDetectConflicts:
    """Test DetectConflicts pipeline stage."""

    @pytest.mark.asyncio
    async def test_no_conflict_detected(self, create_context):
        """No conflict when name is unique."""
        create_context.config.name = "unique-name"
        detector = DetectConflicts()
        result = await detector.invoke(create_context)
        assert not hasattr(result, '_conflict') or result._conflict is None

    @pytest.mark.asyncio
    async def test_conflict_stored_in_context(self, create_context, mock_sessions_list):
        """Detected conflict is stored in context."""
        create_context.config.name = mock_sessions_list[0].name  # Collision
        create_context.existing_sessions = mock_sessions_list

        detector = DetectConflicts()
        result = await detector.invoke(create_context)
        assert hasattr(result, '_conflict')
        assert result._conflict is not None

    def test_detect_conflicts_name(self):
        """DetectConflicts has correct name."""
        assert DetectConflicts().name == "DetectConflicts"


class TestResolveConflicts:
    """Test ResolveConflicts pipeline stage."""

    @pytest.mark.asyncio
    async def test_no_conflict_passes_through(self, create_context):
        """Context without conflict passes through unchanged."""
        resolver = ResolveConflicts()
        result = await resolver.invoke(create_context)
        assert result.config.name == create_context.config.name

    @pytest.mark.asyncio
    async def test_name_collision_resolved(self, create_context, mock_sessions_list):
        """Name collision is auto-resolved."""
        create_context.config.name = mock_sessions_list[0].name
        create_context.existing_sessions = mock_sessions_list

        # Detect conflict first
        detector = DetectConflicts()
        ctx_with_conflict = await detector.invoke(create_context)

        # Resolve
        resolver = ResolveConflicts()
        result = await resolver.invoke(ctx_with_conflict)
        # Name should be modified
        assert result.config.name != mock_sessions_list[0].name

    def test_resolve_conflicts_name(self):
        """ResolveConflicts has correct name."""
        assert ResolveConflicts().name == "ResolveConflicts"


class TestSpawnTmux:
    """Test SpawnTmux pipeline stage."""

    @pytest.mark.asyncio
    async def test_spawns_session(self, create_context):
        """SpawnTmux creates session and returns SpawnResult."""
        spawner = SpawnTmux()
        result = await spawner.invoke(create_context)

        assert isinstance(result, SpawnResult)
        assert result.session is not None
        assert result.tmux == create_context.tmux
        assert result.session.name == create_context.config.name
        assert result.session.state == SessionState.RUNNING
        create_context.tmux.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_tmux_name_format(self, create_context):
        """Tmux name follows prefix-uuid format."""
        spawner = SpawnTmux()
        result = await spawner.invoke(create_context)

        assert result.session.tmux_name.startswith(create_context.zen_config.tmux_prefix)

    def test_spawn_tmux_name(self):
        """SpawnTmux has correct name."""
        assert SpawnTmux().name == "SpawnTmux"


class TestDetectInitialState:
    """Test DetectInitialState pipeline stage."""

    @pytest.mark.asyncio
    async def test_returns_session(self, mock_session, mock_tmux):
        """DetectInitialState returns session."""
        spawn_result = SpawnResult(session=mock_session, tmux=mock_tmux)

        detector = DetectInitialState()
        result = await detector.invoke(spawn_result)

        assert isinstance(result, Session)
        assert result.name == mock_session.name

    def test_detect_initial_state_name(self):
        """DetectInitialState has correct name."""
        assert DetectInitialState().name == "DetectInitialState"


class TestCreateSessionPipeline:
    """Test the composed CreateSessionPipeline."""

    def test_pipeline_composition(self):
        """Pipeline is properly composed with >> operator."""
        # The pipeline should be a composed agent
        assert CreateSessionPipeline is not None
        # It should have a name (from compose)
        assert hasattr(CreateSessionPipeline, 'name') or hasattr(CreateSessionPipeline, 'invoke')

    @pytest.mark.asyncio
    async def test_full_pipeline_execution(self, create_context):
        """Full pipeline creates a session."""
        result = await CreateSessionPipeline.invoke(create_context)

        assert isinstance(result, Session)
        assert result.state == SessionState.RUNNING


class TestCreateSessionPipelineFunction:
    """Test create_session_pipeline convenience function."""

    @pytest.mark.asyncio
    async def test_creates_session(self, mock_session_config, zen_config, mock_tmux):
        """create_session_pipeline creates a valid session."""
        result = await create_session_pipeline(
            config=mock_session_config,
            zen_config=zen_config,
            existing_sessions=[],
            tmux=mock_tmux,
        )

        assert isinstance(result, Session)
        assert result.name == mock_session_config.name
        assert result.session_type == mock_session_config.session_type

    @pytest.mark.asyncio
    async def test_validates_config_first(self, zen_config, mock_tmux):
        """Pipeline validates config before other stages."""
        # Need > 2 reasons to trigger REJECT (short name, numeric, bad path)
        invalid_config = NewSessionConfig(
            name="1",  # Too short AND numeric (2 reasons)
            session_type=SessionType.SHELL,
            working_dir="/nonexistent/path/that/does/not/exist",  # 3rd reason
        )

        with pytest.raises(ValidationError):
            await create_session_pipeline(
                config=invalid_config,
                zen_config=zen_config,
                existing_sessions=[],
                tmux=mock_tmux,
            )

    @pytest.mark.asyncio
    async def test_handles_name_collision(self, mock_session_config, zen_config, mock_sessions_list, mock_tmux):
        """Pipeline handles name collision by renaming."""
        mock_session_config.name = mock_sessions_list[0].name  # Collision

        result = await create_session_pipeline(
            config=mock_session_config,
            zen_config=zen_config,
            existing_sessions=mock_sessions_list,
            tmux=mock_tmux,
        )

        # Name should be different (resolved)
        assert result.name != mock_sessions_list[0].name
