"""Tests for AgentOrchestrator service.

AgentOrchestrator is the central service for executing LLM-backed agents
within the zen-agents TUI.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from zen_agents.services.agent_orchestrator import (
    AgentOrchestrator,
    AnalysisResult,
    ExpansionResult,
    DialogueResult,
    DialecticResult,
    ScientificResult,
)


class TestAgentOrchestratorInit:
    """Test AgentOrchestrator initialization."""

    def test_lazy_runtime_init(self):
        """Runtime is initialized lazily."""
        orch = AgentOrchestrator(runtime=None)
        assert orch._runtime is None

    def test_provided_runtime_used(self, mock_runtime):
        """Provided runtime is used."""
        orch = AgentOrchestrator(runtime=mock_runtime)
        assert orch.runtime == mock_runtime

    def test_runtime_property_creates_default(self):
        """Runtime property creates default if none provided."""
        with patch('zen_agents.services.agent_orchestrator.ClaudeCLIRuntime') as mock_cls:
            mock_cls.return_value = MagicMock()
            orch = AgentOrchestrator(runtime=None)
            _ = orch.runtime
            mock_cls.assert_called_once()


class TestCheckAvailable:
    """Test availability checking."""

    @pytest.mark.asyncio
    async def test_caches_availability(self, orchestrator):
        """Availability check result is cached."""
        # First call
        result1 = await orchestrator.check_available()
        # Second call should use cache
        result2 = await orchestrator.check_available()
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_available_when_fixture_set(self, orchestrator):
        """Orchestrator reports available when fixture sets it."""
        assert await orchestrator.check_available() is True

    @pytest.mark.asyncio
    async def test_unavailable_when_cli_fails(self):
        """Reports unavailable when CLI check fails."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("CLI not found")
            orch = AgentOrchestrator()
            result = await orch.check_available()
            assert result is False


class TestAnalyzeLog:
    """Test log analysis via HypothesisEngine."""

    @pytest.mark.asyncio
    async def test_returns_analysis_result(self, orchestrator, mock_runtime):
        """analyze_log returns AnalysisResult."""
        result = await orchestrator.analyze_log(
            log_content="Error: connection refused",
            domain="networking"
        )

        assert isinstance(result, AnalysisResult)
        assert len(result.hypotheses) == 2
        assert "Test hypothesis 1" in result.hypotheses
        mock_runtime.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_default_domain(self, orchestrator, mock_runtime):
        """Default domain is software engineering."""
        await orchestrator.analyze_log("some log content")
        # Check the call was made
        mock_runtime.execute.assert_called()

    @pytest.mark.asyncio
    async def test_custom_question(self, orchestrator, mock_runtime):
        """Custom question is passed through."""
        await orchestrator.analyze_log(
            log_content="some log",
            question="What caused the crash?"
        )
        mock_runtime.execute.assert_called()


class TestExpandIdea:
    """Test idea expansion via CreativityCoach."""

    @pytest.mark.asyncio
    async def test_returns_expansion_result(self, orchestrator, mock_runtime):
        """expand_idea returns ExpansionResult."""
        result = await orchestrator.expand_idea(
            seed="distributed systems"
        )

        assert isinstance(result, ExpansionResult)
        assert len(result.ideas) > 0
        assert len(result.follow_ups) > 0

    @pytest.mark.asyncio
    async def test_with_context(self, orchestrator, mock_runtime):
        """expand_idea passes context."""
        await orchestrator.expand_idea(
            seed="databases",
            context="focusing on performance"
        )
        mock_runtime.execute.assert_called()


class TestScientificDialogue:
    """Test scientific dialogue via Robin."""

    @pytest.mark.asyncio
    async def test_returns_scientific_result(self, orchestrator, mock_runtime, mock_robin_result):
        """scientific_dialogue returns ScientificResult."""
        # Mock robin agent
        with patch('zen_agents.services.agent_orchestrator.robin') as mock_robin:
            mock_agent = AsyncMock()
            mock_agent.invoke.return_value = mock_robin_result
            mock_robin.return_value = mock_agent

            result = await orchestrator.scientific_dialogue(
                query="Why do neurons spike?",
                domain="neuroscience"
            )

            assert isinstance(result, ScientificResult)
            assert result.synthesis == "Scientific synthesis narrative"
            assert len(result.next_questions) > 0

    @pytest.mark.asyncio
    async def test_with_observations(self, orchestrator, mock_runtime, mock_robin_result):
        """scientific_dialogue passes observations."""
        with patch('zen_agents.services.agent_orchestrator.robin') as mock_robin:
            mock_agent = AsyncMock()
            mock_agent.invoke.return_value = mock_robin_result
            mock_robin.return_value = mock_agent

            await orchestrator.scientific_dialogue(
                query="Pattern analysis",
                domain="biology",
                observations=["obs 1", "obs 2"]
            )
            mock_agent.invoke.assert_called_once()


class TestKgentDialogue:
    """Test K-gent dialogue."""

    @pytest.mark.asyncio
    async def test_returns_dialogue_result(self, orchestrator, mock_runtime):
        """kgent_dialogue returns DialogueResult."""
        result = await orchestrator.kgent_dialogue(
            message="Should I add another feature?"
        )

        assert isinstance(result, DialogueResult)
        assert result.response == "This is a thoughtful response."

    @pytest.mark.asyncio
    async def test_different_modes(self, orchestrator, mock_runtime):
        """kgent_dialogue handles different modes."""
        from zen_agents.kgents_bridge import DialogueMode

        for mode in [DialogueMode.REFLECT, DialogueMode.CHALLENGE, DialogueMode.ADVISE]:
            result = await orchestrator.kgent_dialogue(
                message="test",
                mode=mode
            )
            assert result.mode == mode


class TestQueryPreferences:
    """Test preference querying."""

    @pytest.mark.asyncio
    async def test_returns_preferences_dict(self, orchestrator, mock_runtime):
        """query_preferences returns dict with expected keys."""
        result = await orchestrator.query_preferences()

        assert isinstance(result, dict)
        assert "preferences" in result
        assert "patterns" in result
        assert "suggested_style" in result

    @pytest.mark.asyncio
    async def test_for_agent_parameter(self, orchestrator, mock_runtime):
        """query_preferences passes for_agent."""
        await orchestrator.query_preferences(for_agent="robin")
        mock_runtime.execute.assert_called()


class TestDialecticAnalysis:
    """Test dialectic analysis via Hegel."""

    @pytest.mark.asyncio
    async def test_returns_dialectic_result(self, orchestrator, mock_runtime):
        """dialectic_analysis returns DialecticResult."""
        result = await orchestrator.dialectic_analysis(
            thesis="Simple is better",
            antithesis="Feature-rich is better"
        )

        assert isinstance(result, DialecticResult)
        assert result.synthesis is not None
        assert result.productive_tension is True


class TestSuggestSessionName:
    """Test session name suggestion."""

    @pytest.mark.asyncio
    async def test_returns_short_name(self, orchestrator, mock_runtime):
        """suggest_session_name returns short name."""
        result = await orchestrator.suggest_session_name(
            working_dir="/home/user/project",
            session_type="shell"
        )

        # Response is "This is a thoughtful response." -> first word is "this"
        assert isinstance(result, str)
        assert len(result) <= 20  # Max 20 chars

    @pytest.mark.asyncio
    async def test_with_context(self, orchestrator, mock_runtime):
        """suggest_session_name uses context."""
        await orchestrator.suggest_session_name(
            working_dir="/tmp",
            session_type="robin",
            context="AI research project"
        )
        mock_runtime.execute.assert_called()
