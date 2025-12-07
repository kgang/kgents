"""Tests for runtime/llm_agents/"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from runtime.llm_agents import LLMJudge, LLMSublate, LLMContradict
from runtime.messages import CompletionResult, TokenUsage
from runtime.config import RuntimeConfig, AuthMethod

from bootstrap.types import Principle, Verdict, VerdictStatus, Tension, TensionMode
from bootstrap.judge import JudgeInput
from bootstrap.contradict import ContradictInput


class MockClient:
    """Mock LLM client for testing"""

    def __init__(self, response: str):
        self.response = response
        self._config = RuntimeConfig(auth_method=AuthMethod.CLI)
        self.complete = AsyncMock(return_value=CompletionResult(
            content=response,
            model="mock-model",
            usage=TokenUsage(10, 20),
        ))


class MockCache:
    """Mock cache that always misses"""

    def get(self, *args, **kwargs):
        return None

    def set(self, *args, **kwargs):
        pass


class MockTracker:
    """Mock usage tracker"""

    def track(self, *args, **kwargs):
        pass


class TestLLMJudge:
    @pytest.mark.asyncio
    async def test_accept_verdict(self):
        client = MockClient('{"status": "accept"}')
        judge = LLMJudge(client=client, cache=MockCache(), tracker=MockTracker())

        input = JudgeInput(subject="test subject", principles=[Principle.TASTEFUL])
        result = await judge.invoke(input)

        assert result.overall.status == VerdictStatus.ACCEPT

    @pytest.mark.asyncio
    async def test_reject_verdict(self):
        client = MockClient('{"status": "reject", "reason": "Not tasteful"}')
        judge = LLMJudge(client=client, cache=MockCache(), tracker=MockTracker())

        input = JudgeInput(subject="test subject", principles=[Principle.TASTEFUL])
        result = await judge.invoke(input)

        assert result.overall.status == VerdictStatus.REJECT
        assert "tasteful" in result.overall.reason.lower()

    @pytest.mark.asyncio
    async def test_revise_verdict(self):
        client = MockClient('{"status": "revise", "suggestion": "Add more personality"}')
        judge = LLMJudge(client=client, cache=MockCache(), tracker=MockTracker())

        input = JudgeInput(subject="test subject", principles=[Principle.JOY_INDUCING])
        result = await judge.invoke(input)

        assert result.overall.status == VerdictStatus.REVISE

    @pytest.mark.asyncio
    async def test_parse_markdown_json(self):
        # LLM might return JSON in markdown code block
        client = MockClient('```json\n{"status": "accept"}\n```')
        judge = LLMJudge(client=client, cache=MockCache(), tracker=MockTracker())

        input = JudgeInput(subject="test", principles=[Principle.COMPOSABLE])
        result = await judge.invoke(input)

        assert result.overall.status == VerdictStatus.ACCEPT


class TestLLMSublate:
    @pytest.mark.asyncio
    async def test_synthesize(self):
        response = '''{
            "action": "synthesize",
            "preserved": ["thesis value", "antithesis value"],
            "negated": ["what we reject"],
            "synthesis": {
                "resolution": "unified understanding",
                "elevated_understanding": "new insight"
            }
        }'''
        client = MockClient(response)
        sublate = LLMSublate(client=client, cache=MockCache(), tracker=MockTracker())

        tension = Tension(
            mode=TensionMode.LOGICAL,
            thesis="A is true",
            antithesis="A is false",
            description="Direct contradiction"
        )

        result = await sublate.invoke(tension)

        from bootstrap.types import Synthesis
        assert isinstance(result, Synthesis)
        assert len(result.preserved) == 2
        assert "unified understanding" in result.synthesis["resolution"]

    @pytest.mark.asyncio
    async def test_hold_tension(self):
        response = '{"action": "hold", "reason": "Need more information"}'
        client = MockClient(response)
        sublate = LLMSublate(client=client, cache=MockCache(), tracker=MockTracker())

        tension = Tension(
            mode=TensionMode.PRAGMATIC,
            thesis="Do X",
            antithesis="Do Y",
            description="Conflicting recommendations"
        )

        result = await sublate.invoke(tension)

        from bootstrap.types import HoldTension
        assert isinstance(result, HoldTension)
        assert "more information" in result.reason.lower()


class TestLLMContradict:
    @pytest.mark.asyncio
    async def test_detect_tension(self):
        response = '''{
            "tension_found": true,
            "mode": "logical",
            "description": "Direct negation"
        }'''
        client = MockClient(response)
        contradict = LLMContradict(client=client, cache=MockCache(), tracker=MockTracker())

        input = ContradictInput(thesis="X is good", antithesis="X is bad")
        result = await contradict.invoke(input)

        assert result is not None
        assert result.mode == TensionMode.LOGICAL
        assert "negation" in result.description.lower()

    @pytest.mark.asyncio
    async def test_no_tension(self):
        response = '{"tension_found": false, "reason": "Compatible statements"}'
        client = MockClient(response)
        contradict = LLMContradict(client=client, cache=MockCache(), tracker=MockTracker())

        input = ContradictInput(thesis="I like apples", antithesis="I like oranges")
        result = await contradict.invoke(input)

        assert result is None

    @pytest.mark.asyncio
    async def test_identical_inputs(self):
        client = MockClient('should not be called')
        contradict = LLMContradict(client=client, cache=MockCache(), tracker=MockTracker())

        input = ContradictInput(thesis="same", antithesis="same")
        result = await contradict.invoke(input)

        # Should return None without calling the LLM
        assert result is None
        client.complete.assert_not_called()
