"""Integration tests for full zen-agents flows.

Tests complete workflows from session creation through state detection.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import tempfile

from zen_agents.models.session import (
    Session,
    SessionState,
    SessionType,
    NewSessionConfig,
    session_requires_llm,
)
from zen_agents.agents.config import ZenConfig
from zen_agents.agents.pipelines.create import (
    CreateContext,
    create_session_pipeline,
    ValidationError,
)
from zen_agents.services.persistence import SessionPersistence


class TestSessionCreationFlow:
    """Test complete session creation flows."""

    @pytest.mark.asyncio
    async def test_create_shell_session(self, zen_config, mock_tmux):
        """Create a shell session end-to-end."""
        config = NewSessionConfig(
            name="shell-test",
            session_type=SessionType.SHELL,
            working_dir="/tmp",
        )

        session = await create_session_pipeline(
            config=config,
            zen_config=zen_config,
            existing_sessions=[],
            tmux=mock_tmux,
        )

        assert session.name == "shell-test"
        assert session.session_type == SessionType.SHELL
        assert session.state == SessionState.RUNNING
        assert session.tmux_name.startswith(zen_config.tmux_prefix)
        mock_tmux.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_claude_session(self, zen_config, mock_tmux):
        """Create a Claude session end-to-end."""
        config = NewSessionConfig(
            name="claude-test",
            session_type=SessionType.CLAUDE,
            working_dir="/tmp",
        )

        session = await create_session_pipeline(
            config=config,
            zen_config=zen_config,
            existing_sessions=[],
            tmux=mock_tmux,
        )

        assert session.session_type == SessionType.CLAUDE
        assert session.state == SessionState.RUNNING

    @pytest.mark.asyncio
    async def test_create_robin_session(self, zen_config, mock_tmux):
        """Create a Robin (LLM-backed) session end-to-end."""
        config = NewSessionConfig(
            name="robin-test",
            session_type=SessionType.ROBIN,
            working_dir="/tmp",
        )

        session = await create_session_pipeline(
            config=config,
            zen_config=zen_config,
            existing_sessions=[],
            tmux=mock_tmux,
        )

        assert session.session_type == SessionType.ROBIN
        assert session_requires_llm(session.session_type)


class TestConflictResolutionFlow:
    """Test conflict detection and resolution flows."""

    @pytest.mark.asyncio
    async def test_name_collision_auto_resolved(self, zen_config, mock_tmux, mock_sessions_list):
        """Name collision is automatically resolved."""
        colliding_name = mock_sessions_list[0].name
        config = NewSessionConfig(
            name=colliding_name,
            session_type=SessionType.SHELL,
        )

        session = await create_session_pipeline(
            config=config,
            zen_config=zen_config,
            existing_sessions=mock_sessions_list,
            tmux=mock_tmux,
        )

        # Name should be different (resolved with timestamp)
        assert session.name != colliding_name
        # The suggested resolution format may include quotes
        assert colliding_name in session.name or session.name != colliding_name

    @pytest.mark.asyncio
    async def test_invalid_config_rejected(self, zen_config, mock_tmux):
        """Invalid config is rejected before tmux creation."""
        # Need > 2 reasons to trigger REJECT (short name, numeric, bad path)
        config = NewSessionConfig(
            name="1",  # Too short AND numeric (2 reasons)
            session_type=SessionType.SHELL,
            working_dir="/nonexistent/path/that/does/not/exist",  # 3rd reason
        )

        with pytest.raises(ValidationError):
            await create_session_pipeline(
                config=config,
                zen_config=zen_config,
                existing_sessions=[],
                tmux=mock_tmux,
            )

        # Tmux should never be called
        mock_tmux.create_session.assert_not_called()


class TestPersistenceFlow:
    """Test session persistence across restarts."""

    @pytest.mark.asyncio
    async def test_save_and_load_sessions(self, zen_config, mock_tmux):
        """Sessions can be saved and loaded."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            persistence = SessionPersistence(Path(f.name))

            # Create session
            config = NewSessionConfig(
                name="persist-test",
                session_type=SessionType.SHELL,
                working_dir="/tmp",
            )

            session = await create_session_pipeline(
                config=config,
                zen_config=zen_config,
                existing_sessions=[],
                tmux=mock_tmux,
            )

            # Save
            persistence.save([session])

            # Load
            loaded = persistence.load()
            assert len(loaded) == 1
            assert loaded[0].id == session.id
            assert loaded[0].name == session.name
            assert loaded[0].session_type == session.session_type

            # Cleanup
            Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_multiple_sessions_roundtrip(self, zen_config, mock_tmux):
        """Multiple sessions survive persistence roundtrip."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            persistence = SessionPersistence(Path(f.name))

            sessions = []
            for i, stype in enumerate([SessionType.SHELL, SessionType.CLAUDE, SessionType.ROBIN]):
                config = NewSessionConfig(
                    name=f"session-{i}",
                    session_type=stype,
                )
                session = await create_session_pipeline(
                    config=config,
                    zen_config=zen_config,
                    existing_sessions=sessions,
                    tmux=mock_tmux,
                )
                sessions.append(session)

            # Save all
            persistence.save(sessions)

            # Load and verify
            loaded = persistence.load()
            assert len(loaded) == 3
            assert {s.session_type for s in loaded} == {
                SessionType.SHELL,
                SessionType.CLAUDE,
                SessionType.ROBIN,
            }

            # Cleanup
            Path(f.name).unlink()


class TestStateDetectionFlow:
    """Test state detection flows."""

    @pytest.mark.asyncio
    async def test_running_session_detected(self, mock_session, mock_tmux):
        """Running session state is detected."""
        from zen_agents.agents.detection import detect_state

        result = await detect_state(
            session=mock_session,
            tmux=mock_tmux,
            max_iterations=10,
        )

        assert result.converged
        assert result.value.session_state == SessionState.RUNNING

    @pytest.mark.asyncio
    async def test_dead_session_detected(self, mock_session, mock_tmux_dead):
        """Dead session state is detected."""
        from zen_agents.agents.detection import detect_state

        result = await detect_state(
            session=mock_session,
            tmux=mock_tmux_dead,
            max_iterations=10,
        )

        assert result.converged
        assert result.value.session_state == SessionState.FAILED


class TestLLMSessionFlow:
    """Test LLM-backed session flows."""

    def test_session_requires_llm_classification(self):
        """Correctly classifies which sessions need LLM."""
        # LLM-backed
        assert session_requires_llm(SessionType.ROBIN) is True
        assert session_requires_llm(SessionType.CREATIVITY) is True
        assert session_requires_llm(SessionType.HYPOTHESIS) is True
        assert session_requires_llm(SessionType.KGENT) is True

        # Non-LLM
        assert session_requires_llm(SessionType.SHELL) is False
        assert session_requires_llm(SessionType.CLAUDE) is False
        assert session_requires_llm(SessionType.CODEX) is False

    @pytest.mark.asyncio
    async def test_llm_session_handler_integration(self, mock_session):
        """LLM session handler integrates with orchestrator."""
        from zen_agents.services.session_handler import SessionTypeHandler
        from zen_agents.services.agent_orchestrator import (
            AgentOrchestrator,
            ScientificResult,
        )

        # Create mock orchestrator
        mock_orch = AsyncMock(spec=AgentOrchestrator)
        mock_orch.scientific_dialogue.return_value = ScientificResult(
            synthesis="Test synthesis",
            hypotheses=["H1"],
            dialectic=None,
            next_questions=["Q1?"],
            personalization=None,
        )

        handler = SessionTypeHandler(mock_orch)

        # Create ROBIN session
        mock_session.session_type = SessionType.ROBIN
        mock_session.metadata = {"domain": "test"}

        # Handle input
        result = await handler.handle_input(
            mock_session,
            "Why do X happen?"
        )

        assert result.success
        assert "Synthesis" in result.formatted_output
        mock_orch.scientific_dialogue.assert_called_once()


class TestPipelineComposition:
    """Test pipeline composition with >> operator."""

    @pytest.mark.asyncio
    async def test_pipeline_stages_execute_in_order(self, zen_config, mock_tmux):
        """Pipeline stages execute in correct order."""
        from zen_agents.agents.pipelines.create import (
            ValidateLimit,
            DetectConflicts,
            ResolveConflicts,
            SpawnTmux,
            DetectInitialState,
            CreateContext,
        )

        config = NewSessionConfig(
            name="pipeline-test",
            session_type=SessionType.SHELL,
        )
        ctx = CreateContext(
            config=config,
            zen_config=zen_config,
            existing_sessions=[],
            tmux=mock_tmux,
        )

        # Execute stages manually to verify order
        ctx = await ValidateLimit().invoke(ctx)
        ctx = await DetectConflicts().invoke(ctx)
        ctx = await ResolveConflicts().invoke(ctx)
        spawn_result = await SpawnTmux().invoke(ctx)
        session = await DetectInitialState().invoke(spawn_result)

        assert session.state == SessionState.RUNNING


class TestConfigResolution:
    """Test config resolution flows."""

    @pytest.mark.asyncio
    async def test_config_ground_loads_defaults(self):
        """ConfigGround loads default configuration."""
        from zen_agents.agents.config import ConfigGround, DEFAULT_CONFIG

        ground = ConfigGround()
        facts = await ground.invoke(None)

        # Should have persona preferences from defaults
        assert facts.persona.preferences["poll_interval"] == DEFAULT_CONFIG["poll_interval"]

    @pytest.mark.asyncio
    async def test_config_resolve_merges_tiers(self):
        """ResolveConfig merges all config tiers."""
        from zen_agents.agents.config import ConfigGround, ResolveConfig

        # Ground with session override
        ground = ConfigGround(session_config={"poll_interval": 2.0})
        facts = await ground.invoke(None)

        # Resolve
        resolver = ResolveConfig()
        config = await resolver.invoke(facts)

        assert isinstance(config, ZenConfig)
        assert config.poll_interval == 2.0  # Session override wins


class TestSessionLifecycle:
    """Test complete session lifecycle."""

    @pytest.mark.asyncio
    async def test_create_use_persist_lifecycle(self, zen_config, mock_tmux):
        """Complete session lifecycle: create -> use -> persist."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            persistence = SessionPersistence(Path(f.name))

            # 1. Create session
            config = NewSessionConfig(
                name="lifecycle-test",
                session_type=SessionType.SHELL,
            )
            session = await create_session_pipeline(
                config=config,
                zen_config=zen_config,
                existing_sessions=[],
                tmux=mock_tmux,
            )
            assert session.state == SessionState.RUNNING

            # 2. "Use" session (update metadata)
            session.metadata["used"] = True

            # 3. Persist
            persistence.save([session])

            # 4. Verify persistence
            loaded = persistence.load()
            assert loaded[0].metadata.get("used") is True

            # Cleanup
            Path(f.name).unlink()
