"""Tests for SessionTypeHandler.

SessionTypeHandler routes session input to appropriate kgents agents.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from zen_agents.models.session import Session, SessionState, SessionType
from zen_agents.services.session_handler import (
    SessionTypeHandler,
    HandlerResult,
    create_handler,
)
from zen_agents.services.agent_orchestrator import (
    AnalysisResult,
    ExpansionResult,
    DialogueResult,
    ScientificResult,
)


@pytest.fixture
def mock_orchestrator():
    """Mock AgentOrchestrator for handler tests."""
    orch = AsyncMock()

    # Mock scientific_dialogue
    orch.scientific_dialogue.return_value = ScientificResult(
        synthesis="Test synthesis",
        hypotheses=["H1", "H2"],
        dialectic=None,
        next_questions=["Q1?"],
        personalization=None
    )

    # Mock expand_idea
    orch.expand_idea.return_value = ExpansionResult(
        ideas=["Idea 1", "Idea 2"],
        follow_ups=["Follow 1"]
    )

    # Mock analyze_log
    orch.analyze_log.return_value = AnalysisResult(
        hypotheses=["Hyp 1"],
        suggested_tests=["Test 1"],
        reasoning="Because..."
    )

    # Mock kgent_dialogue
    from zen_agents.kgents_bridge import DialogueMode
    orch.kgent_dialogue.return_value = DialogueResult(
        response="K-gent response",
        mode=DialogueMode.REFLECT
    )

    return orch


@pytest.fixture
def handler(mock_orchestrator):
    """SessionTypeHandler with mock orchestrator."""
    return SessionTypeHandler(mock_orchestrator)


@pytest.fixture
def robin_session():
    """Create a ROBIN session."""
    from uuid import uuid4
    return Session(
        id=uuid4(),
        name="robin-test",
        session_type=SessionType.ROBIN,
        state=SessionState.RUNNING,
        tmux_name="zen-robin-test",
        metadata={"domain": "neuroscience"}
    )


@pytest.fixture
def creativity_session():
    """Create a CREATIVITY session."""
    from uuid import uuid4
    return Session(
        id=uuid4(),
        name="creative-test",
        session_type=SessionType.CREATIVITY,
        state=SessionState.RUNNING,
        tmux_name="zen-creative-test",
    )


@pytest.fixture
def hypothesis_session():
    """Create a HYPOTHESIS session."""
    from uuid import uuid4
    return Session(
        id=uuid4(),
        name="hypo-test",
        session_type=SessionType.HYPOTHESIS,
        state=SessionState.RUNNING,
        tmux_name="zen-hypo-test",
        metadata={"domain": "biology"}
    )


@pytest.fixture
def kgent_session():
    """Create a KGENT session."""
    from uuid import uuid4
    return Session(
        id=uuid4(),
        name="kgent-test",
        session_type=SessionType.KGENT,
        state=SessionState.RUNNING,
        tmux_name="zen-kgent-test",
    )


@pytest.fixture
def shell_session():
    """Create a SHELL session (non-LLM)."""
    from uuid import uuid4
    return Session(
        id=uuid4(),
        name="shell-test",
        session_type=SessionType.SHELL,
        state=SessionState.RUNNING,
        tmux_name="zen-shell-test",
    )


class TestCanHandle:
    """Test can_handle method."""

    def test_can_handle_robin(self, handler, robin_session):
        """Can handle ROBIN sessions."""
        assert handler.can_handle(robin_session) is True

    def test_can_handle_creativity(self, handler, creativity_session):
        """Can handle CREATIVITY sessions."""
        assert handler.can_handle(creativity_session) is True

    def test_can_handle_hypothesis(self, handler, hypothesis_session):
        """Can handle HYPOTHESIS sessions."""
        assert handler.can_handle(hypothesis_session) is True

    def test_can_handle_kgent(self, handler, kgent_session):
        """Can handle KGENT sessions."""
        assert handler.can_handle(kgent_session) is True

    def test_cannot_handle_shell(self, handler, shell_session):
        """Cannot handle SHELL sessions (non-LLM)."""
        assert handler.can_handle(shell_session) is False


class TestHandleInput:
    """Test handle_input routing."""

    @pytest.mark.asyncio
    async def test_passthrough_for_shell(self, handler, shell_session):
        """Non-LLM sessions get passthrough."""
        result = await handler.handle_input(
            shell_session,
            "ls -la"
        )
        assert result.formatted_output == "ls -la"
        assert result.success is True
        assert result.raw_result is None

    @pytest.mark.asyncio
    async def test_routes_to_robin(self, handler, robin_session, mock_orchestrator):
        """ROBIN session routes to scientific_dialogue."""
        result = await handler.handle_input(
            robin_session,
            "Why do neurons spike?"
        )
        mock_orchestrator.scientific_dialogue.assert_called_once()
        assert result.success is True
        assert "Synthesis" in result.formatted_output

    @pytest.mark.asyncio
    async def test_routes_to_creativity(self, handler, creativity_session, mock_orchestrator):
        """CREATIVITY session routes to expand_idea."""
        result = await handler.handle_input(
            creativity_session,
            "distributed systems"
        )
        mock_orchestrator.expand_idea.assert_called_once()
        assert result.success is True
        assert "Idea" in result.formatted_output

    @pytest.mark.asyncio
    async def test_routes_to_hypothesis(self, handler, hypothesis_session, mock_orchestrator):
        """HYPOTHESIS session routes to analyze_log."""
        result = await handler.handle_input(
            hypothesis_session,
            "Error: connection refused"
        )
        mock_orchestrator.analyze_log.assert_called_once()
        assert result.success is True
        assert "Hypotheses" in result.formatted_output

    @pytest.mark.asyncio
    async def test_routes_to_kgent(self, handler, kgent_session, mock_orchestrator):
        """KGENT session routes to kgent_dialogue."""
        result = await handler.handle_input(
            kgent_session,
            "Should I add another feature?"
        )
        mock_orchestrator.kgent_dialogue.assert_called_once()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_error_handling(self, handler, robin_session, mock_orchestrator):
        """Errors are caught and returned in result."""
        mock_orchestrator.scientific_dialogue.side_effect = Exception("LLM error")

        result = await handler.handle_input(
            robin_session,
            "test query"
        )
        assert result.success is False
        assert "Error" in result.formatted_output
        assert result.error == "LLM error"


class TestRobinHandler:
    """Test Robin-specific handling."""

    @pytest.mark.asyncio
    async def test_uses_domain_from_metadata(self, handler, robin_session, mock_orchestrator):
        """Uses domain from session metadata."""
        await handler.handle_input(robin_session, "query")

        call_kwargs = mock_orchestrator.scientific_dialogue.call_args.kwargs
        assert call_kwargs["domain"] == "neuroscience"

    @pytest.mark.asyncio
    async def test_formats_hypotheses(self, handler, robin_session, mock_orchestrator):
        """Output includes formatted hypotheses."""
        result = await handler.handle_input(robin_session, "query")
        assert "H1" in result.formatted_output or "H2" in result.formatted_output

    @pytest.mark.asyncio
    async def test_formats_next_questions(self, handler, robin_session, mock_orchestrator):
        """Output includes next questions."""
        result = await handler.handle_input(robin_session, "query")
        assert "Q1?" in result.formatted_output


class TestCreativityHandler:
    """Test Creativity-specific handling."""

    @pytest.mark.asyncio
    async def test_default_expand_mode(self, handler, creativity_session, mock_orchestrator):
        """Default mode is EXPAND."""
        from zen_agents.kgents_bridge import CreativityMode

        await handler.handle_input(creativity_session, "an idea")
        call_kwargs = mock_orchestrator.expand_idea.call_args.kwargs
        assert call_kwargs["mode"] == CreativityMode.EXPAND

    @pytest.mark.asyncio
    async def test_connect_mode_prefix(self, handler, creativity_session, mock_orchestrator):
        """'/connect' prefix switches to CONNECT mode."""
        from zen_agents.kgents_bridge import CreativityMode

        await handler.handle_input(creativity_session, "/connect databases")
        call_kwargs = mock_orchestrator.expand_idea.call_args.kwargs
        assert call_kwargs["mode"] == CreativityMode.CONNECT
        assert call_kwargs["seed"] == "databases"

    @pytest.mark.asyncio
    async def test_constrain_mode_prefix(self, handler, creativity_session, mock_orchestrator):
        """'/constrain' prefix switches to CONSTRAIN mode."""
        from zen_agents.kgents_bridge import CreativityMode

        await handler.handle_input(creativity_session, "/constrain web apps")
        call_kwargs = mock_orchestrator.expand_idea.call_args.kwargs
        assert call_kwargs["mode"] == CreativityMode.CONSTRAIN

    @pytest.mark.asyncio
    async def test_question_mode_prefix(self, handler, creativity_session, mock_orchestrator):
        """'/question' prefix switches to QUESTION mode."""
        from zen_agents.kgents_bridge import CreativityMode

        await handler.handle_input(creativity_session, "/question microservices")
        call_kwargs = mock_orchestrator.expand_idea.call_args.kwargs
        assert call_kwargs["mode"] == CreativityMode.QUESTION


class TestKgentHandler:
    """Test K-gent-specific handling."""

    @pytest.mark.asyncio
    async def test_default_reflect_mode(self, handler, kgent_session, mock_orchestrator):
        """Default mode is REFLECT."""
        from zen_agents.kgents_bridge import DialogueMode

        await handler.handle_input(kgent_session, "thinking about X")
        call_args = mock_orchestrator.kgent_dialogue.call_args
        assert call_args.args[1] == DialogueMode.REFLECT

    @pytest.mark.asyncio
    async def test_challenge_mode_prefix(self, handler, kgent_session, mock_orchestrator):
        """'/challenge' prefix switches to CHALLENGE mode."""
        from zen_agents.kgents_bridge import DialogueMode

        await handler.handle_input(kgent_session, "/challenge this idea")
        call_args = mock_orchestrator.kgent_dialogue.call_args
        assert call_args.args[1] == DialogueMode.CHALLENGE
        assert call_args.args[0] == "this idea"

    @pytest.mark.asyncio
    async def test_advise_mode_prefix(self, handler, kgent_session, mock_orchestrator):
        """'/advise' prefix switches to ADVISE mode."""
        from zen_agents.kgents_bridge import DialogueMode

        await handler.handle_input(kgent_session, "/advise next steps")
        call_args = mock_orchestrator.kgent_dialogue.call_args
        assert call_args.args[1] == DialogueMode.ADVISE

    @pytest.mark.asyncio
    async def test_explore_mode_prefix(self, handler, kgent_session, mock_orchestrator):
        """'/explore' prefix switches to EXPLORE mode."""
        from zen_agents.kgents_bridge import DialogueMode

        await handler.handle_input(kgent_session, "/explore possibilities")
        call_args = mock_orchestrator.kgent_dialogue.call_args
        assert call_args.args[1] == DialogueMode.EXPLORE

    @pytest.mark.asyncio
    async def test_output_includes_mode_label(self, handler, kgent_session, mock_orchestrator):
        """Output includes mode label."""
        result = await handler.handle_input(kgent_session, "test")
        assert "[REFLECT]" in result.formatted_output


class TestCreateHandler:
    """Test create_handler convenience function."""

    def test_creates_with_default_orchestrator(self):
        """Creates handler with default orchestrator."""
        with patch('zen_agents.services.session_handler.AgentOrchestrator') as mock_cls:
            handler = create_handler()
            mock_cls.assert_called_once()
            assert isinstance(handler, SessionTypeHandler)

    def test_creates_with_provided_orchestrator(self, mock_orchestrator):
        """Creates handler with provided orchestrator."""
        handler = create_handler(mock_orchestrator)
        assert handler.orchestrator == mock_orchestrator
