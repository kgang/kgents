"""
Tests for AGENTESE Phase 8: Natural Language → AGENTESE Adapter

Tests the translation from natural language to AGENTESE paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from ..adapter import (
    LLM_TRANSLATION_EXAMPLES,
    TRANSLATION_PATTERNS,
    AgentesAdapter,
    LLMTranslator,
    PatternTranslator,
    TranslationError,
    TranslationResult,
    build_translation_prompt,
    create_adapter,
    create_pattern_translator,
)
from ..integration import GgentIntegration

# =============================================================================
# Test Fixtures
# =============================================================================


@dataclass
class MockDNA:
    """Mock DNA for testing."""

    name: str = "test_agent"
    archetype: str = "architect"
    capabilities: tuple[str, ...] = ()


@dataclass
class MockUmwelt:
    """Mock Umwelt for testing."""

    dna: MockDNA = field(default_factory=MockDNA)
    state: Any = None
    gravity: tuple = ()


class MockLLM:
    """Mock LLM for testing."""

    def __init__(self, responses: dict[str, str] | None = None):
        self._responses = responses or {}
        self._calls: list[str] = []

    async def complete(self, prompt: str) -> str:
        self._calls.append(prompt)
        # Check for specific input patterns
        for key, response in self._responses.items():
            if key in prompt:
                return response
        # Default response
        return "world.unknown.manifest"


class MockLogos:
    """Mock WiredLogos for testing."""

    def __init__(self):
        self._invocations: list[tuple[str, Any, dict]] = []
        self._results: dict[str, Any] = {}

    async def invoke(self, path: str, observer: Any, **kwargs: Any) -> Any:
        self._invocations.append((path, observer, kwargs))
        return self._results.get(path, {"path": path, "status": "invoked"})


@pytest.fixture
def mock_umwelt() -> MockUmwelt:
    """Create a mock Umwelt."""
    return MockUmwelt()


@pytest.fixture
def pattern_translator() -> PatternTranslator:
    """Create a pattern translator."""
    return PatternTranslator()


@pytest.fixture
def mock_llm() -> MockLLM:
    """Create a mock LLM with some responses."""
    return MockLLM(
        {
            "check database health": "world.database.manifest",
            "analyze user behavior": "world.users.manifest",
        }
    )


@pytest.fixture
def llm_translator(mock_llm: MockLLM) -> LLMTranslator:
    """Create an LLM translator."""
    return LLMTranslator(llm=mock_llm)


@pytest.fixture
def mock_logos() -> MockLogos:
    """Create a mock Logos."""
    return MockLogos()


@pytest.fixture
def adapter(mock_logos: MockLogos, mock_llm: MockLLM) -> AgentesAdapter:
    """Create a full adapter."""
    return AgentesAdapter(
        logos=mock_logos,
        llm_translator=LLMTranslator(llm=mock_llm),
    )


@pytest.fixture
def adapter_no_llm(mock_logos: MockLogos) -> AgentesAdapter:
    """Create an adapter without LLM."""
    return AgentesAdapter(
        logos=mock_logos,
        use_llm_fallback=False,
    )


# =============================================================================
# Test TranslationResult
# =============================================================================


class TestTranslationResult:
    """Tests for TranslationResult dataclass."""

    def test_basic_result(self) -> None:
        """Test creating a basic translation result."""
        result = TranslationResult(
            path="world.house.manifest",
            confidence=0.9,
            source="pattern",
            original_input="show me the house",
        )
        assert result.path == "world.house.manifest"
        assert result.confidence == 0.9
        assert result.source == "pattern"

    def test_result_with_entities(self) -> None:
        """Test result with extracted entities."""
        result = TranslationResult(
            path="world.house.manifest",
            confidence=0.9,
            source="pattern",
            original_input="show me the house",
            matched_pattern=r"^show\s+(me\s+)?(?:the\s+)?(\w+)$",
            extracted_entities={"entity": "house"},
        )
        assert result.extracted_entities["entity"] == "house"

    def test_result_is_frozen(self) -> None:
        """Test that TranslationResult is immutable."""
        result = TranslationResult(
            path="world.house.manifest",
            confidence=0.9,
            source="pattern",
            original_input="test",
        )
        with pytest.raises(AttributeError):
            result.path = "different.path"


# =============================================================================
# Test TranslationError
# =============================================================================


class TestTranslationError:
    """Tests for TranslationError."""

    def test_error_message(self) -> None:
        """Test error message formatting."""
        error = TranslationError(
            input="blorp the florp",
            reason="No matching pattern",
            suggestions=["Try: 'show me the <entity>'"],
        )
        msg = str(error)
        assert "blorp the florp" in msg
        assert "No matching pattern" in msg
        assert "show me the <entity>" in msg

    def test_error_with_no_suggestions(self) -> None:
        """Test error without suggestions."""
        error = TranslationError(
            input="test",
            reason="Failed",
        )
        msg = str(error)
        assert "Failed" in msg
        assert "AGENTESE directly" in msg  # Always suggests direct usage


# =============================================================================
# Test PatternTranslator
# =============================================================================


class TestPatternTranslator:
    """Tests for pattern-based translation."""

    # === Perception Patterns ===

    def test_show_me_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'show me the X' pattern."""
        result = pattern_translator.translate("show me the house")
        assert result is not None
        assert result.path == "world.house.manifest"
        assert result.confidence >= 0.85

    def test_get_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'get X' pattern."""
        result = pattern_translator.translate("get the status")
        assert result is not None
        assert result.path == "world.status.manifest"

    def test_view_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'view X' pattern."""
        result = pattern_translator.translate("view the project")
        assert result is not None
        assert result.path == "world.project.manifest"

    def test_what_is_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'what is X' pattern."""
        result = pattern_translator.translate("what is the garden?")
        assert result is not None
        assert result.path == "world.garden.manifest"

    def test_describe_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'describe X' pattern."""
        result = pattern_translator.translate("describe the library")
        assert result is not None
        assert result.path == "world.library.manifest"

    # === History Patterns ===

    def test_what_happened_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'what happened to X' pattern."""
        result = pattern_translator.translate("what happened to the house?")
        assert result is not None
        assert result.path == "world.house.witness"

    def test_history_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'history of X' pattern."""
        result = pattern_translator.translate("history of the project")
        assert result is not None
        assert result.path == "world.project.witness"

    def test_trace_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'trace' pattern."""
        result = pattern_translator.translate("trace the logs")
        assert result is not None
        assert result.path == "time.trace.witness"

    def test_show_logs_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'show logs' pattern."""
        result = pattern_translator.translate("show me the logs")
        assert result is not None
        assert result.path == "time.trace.witness"

    # === Memory Patterns ===

    def test_memory_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'show memory' pattern."""
        result = pattern_translator.translate("show my memory")
        assert result is not None
        assert result.path == "self.memory.manifest"

    def test_dream_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'dream' pattern."""
        result = pattern_translator.translate("dream")
        assert result is not None
        assert result.path == "self.memory.consolidate"

    def test_sort_thoughts_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'sort my thoughts' pattern."""
        result = pattern_translator.translate("sort my thoughts")
        assert result is not None
        assert result.path == "self.memory.consolidate"

    def test_capabilities_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'what can I do' pattern."""
        result = pattern_translator.translate("what can I do?")
        assert result is not None
        assert result.path == "self.capabilities.affordances"

    # === Concept Patterns ===

    def test_think_about_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'think about X' pattern."""
        result = pattern_translator.translate("think about justice")
        assert result is not None
        assert result.path == "concept.justice.refine"

    def test_refine_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'refine X' pattern."""
        result = pattern_translator.translate("refine fairness")
        assert result is not None
        assert result.path == "concept.fairness.refine"

    def test_challenge_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'challenge X' pattern."""
        result = pattern_translator.translate("challenge the idea of freedom")
        assert result is not None
        assert result.path == "concept.freedom.refine"

    def test_define_concept_pattern(
        self, pattern_translator: PatternTranslator
    ) -> None:
        """Test 'define X' pattern."""
        result = pattern_translator.translate("define love")
        assert result is not None
        assert result.path == "concept.love.define"

    # === Entropy Patterns ===

    def test_random_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'give me randomness' pattern."""
        result = pattern_translator.translate("give me some randomness")
        assert result is not None
        assert result.path == "void.entropy.sip"

    def test_sip_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'sip from void' pattern."""
        result = pattern_translator.translate("sip from the void")
        assert result is not None
        assert result.path == "void.entropy.sip"

    def test_surprise_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'surprise me' pattern."""
        result = pattern_translator.translate("surprise me")
        assert result is not None
        assert result.path == "void.serendipity.sip"

    def test_tithe_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'tithe' pattern."""
        result = pattern_translator.translate("tithe")
        assert result is not None
        assert result.path == "void.gratitude.tithe"

    def test_thanks_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'thanks' pattern."""
        result = pattern_translator.translate("thanks")
        assert result is not None
        assert result.path == "void.gratitude.thank"

    # === Temporal Patterns ===

    def test_forecast_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'forecast' pattern."""
        result = pattern_translator.translate("forecast the weather")
        assert result is not None
        assert result.path == "time.future.forecast"

    def test_predict_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'predict' pattern."""
        result = pattern_translator.translate("predict the future")
        assert result is not None
        assert result.path == "time.future.forecast"

    def test_schedule_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'schedule' pattern."""
        result = pattern_translator.translate("schedule a meeting")
        assert result is not None
        assert result.path == "time.schedule.defer"

    # === Server/System Patterns ===

    def test_server_status_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'server status' pattern."""
        result = pattern_translator.translate("get server status")
        assert result is not None
        assert result.path == "world.server.manifest"

    def test_system_health_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'system health' pattern."""
        result = pattern_translator.translate("check system health")
        assert result is not None
        assert result.path == "world.system.manifest"

    # === Creation Patterns ===

    def test_create_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'create X' pattern."""
        result = pattern_translator.translate("create a new garden")
        assert result is not None
        assert result.path == "world.garden.define"

    def test_add_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test 'add X' pattern."""
        result = pattern_translator.translate("add a user")
        assert result is not None
        assert result.path == "world.user.define"

    # === Edge Cases ===

    def test_no_match_returns_none(self, pattern_translator: PatternTranslator) -> None:
        """Test that non-matching input returns None."""
        result = pattern_translator.translate("blorp the florp")
        assert result is None

    def test_case_insensitive(self, pattern_translator: PatternTranslator) -> None:
        """Test that patterns are case insensitive."""
        result = pattern_translator.translate("SHOW ME THE HOUSE")
        assert result is not None
        assert result.path == "world.house.manifest"

    def test_whitespace_handling(self, pattern_translator: PatternTranslator) -> None:
        """Test that whitespace is handled."""
        result = pattern_translator.translate("  show me the house  ")
        assert result is not None
        assert result.path == "world.house.manifest"

    def test_add_custom_pattern(self, pattern_translator: PatternTranslator) -> None:
        """Test adding a custom pattern."""
        pattern_translator.add_pattern(
            r"^flip\s+(\w+)$",
            "world.{entity}.flip",
            "flip",
            0.9,
        )
        result = pattern_translator.translate("flip pancake")
        assert result is not None
        assert result.path == "world.pancake.flip"


# =============================================================================
# Test LLMTranslator
# =============================================================================


class TestLLMTranslator:
    """Tests for LLM-based translation."""

    @pytest.mark.asyncio
    async def test_basic_translation(
        self, llm_translator: LLMTranslator, mock_llm: MockLLM
    ):
        """Test basic LLM translation."""
        mock_llm._responses["test query"] = "world.test.manifest"
        result = await llm_translator.translate("test query")
        assert result is not None
        assert result.path == "world.test.manifest"
        assert result.source == "llm"
        assert result.confidence == 0.7  # LLM confidence

    @pytest.mark.asyncio
    async def test_no_llm_returns_none(self) -> None:
        """Test that missing LLM returns None."""
        translator = LLMTranslator(llm=None)
        result = await translator.translate("test")
        assert result is None

    @pytest.mark.asyncio
    async def test_invalid_path_returns_none(self, mock_llm: MockLLM) -> None:
        """Test that invalid LLM output returns None."""
        mock_llm._responses["bad query"] = "invalid path without dots"
        translator = LLMTranslator(llm=mock_llm)
        result = await translator.translate("bad query")
        assert result is None

    @pytest.mark.asyncio
    async def test_llm_receives_prompt(
        self, llm_translator: LLMTranslator, mock_llm: MockLLM
    ):
        """Test that LLM receives properly formatted prompt."""
        await llm_translator.translate("test input")
        assert len(mock_llm._calls) == 1
        prompt = mock_llm._calls[0]
        assert "AGENTESE" in prompt
        assert "test input" in prompt

    def test_add_example(self, llm_translator: LLMTranslator) -> None:
        """Test adding training examples."""
        initial_count = len(llm_translator.examples)
        llm_translator.add_example("flip pancake", "world.pancake.flip")
        assert len(llm_translator.examples) == initial_count + 1


# =============================================================================
# Test AgentesAdapter
# =============================================================================


class TestAgentesAdapter:
    """Tests for the unified adapter."""

    @pytest.mark.asyncio
    async def test_pattern_translation_first(self, adapter: AgentesAdapter) -> None:
        """Test that pattern translation is tried first."""
        result = await adapter.translate("show me the house")
        assert result.source == "pattern"
        assert result.path == "world.house.manifest"

    @pytest.mark.asyncio
    async def test_llm_fallback(
        self, adapter: AgentesAdapter, mock_llm: MockLLM
    ) -> None:
        """Test that LLM is used when patterns fail."""
        mock_llm._responses["complex query"] = "world.complex.manifest"
        result = await adapter.translate("complex query that doesn't match patterns")
        # Should fall back to LLM which returns default
        assert result.source in ("llm", "pattern")

    @pytest.mark.asyncio
    async def test_direct_agentese_passthrough(self, adapter: AgentesAdapter) -> None:
        """Test that valid AGENTESE passes through."""
        result = await adapter.translate("world.house.manifest")
        assert result.source == "direct"
        assert result.path == "world.house.manifest"
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_translation_error_on_failure(
        self, adapter_no_llm: AgentesAdapter
    ) -> None:
        """Test that TranslationError is raised when all translators fail."""
        with pytest.raises(TranslationError) as exc_info:
            await adapter_no_llm.translate("blorp the florp completely")
        assert "blorp the florp" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_error_has_suggestions(self, adapter_no_llm: AgentesAdapter) -> None:
        """Test that TranslationError has helpful suggestions."""
        with pytest.raises(TranslationError) as exc_info:
            await adapter_no_llm.translate("blorp the florp utterly")
        error = exc_info.value
        assert len(error.suggestions) > 0

    @pytest.mark.asyncio
    async def test_execute_translates_and_invokes(
        self,
        adapter: AgentesAdapter,
        mock_logos: MockLogos,
        mock_umwelt: MockUmwelt,
    ):
        """Test that execute translates and invokes."""
        result = await adapter.execute("show me the house", mock_umwelt)
        assert len(mock_logos._invocations) == 1
        path, observer, kwargs = mock_logos._invocations[0]
        assert path == "world.house.manifest"
        assert observer is mock_umwelt

    @pytest.mark.asyncio
    async def test_execute_with_direct_path(
        self,
        adapter: AgentesAdapter,
        mock_logos: MockLogos,
        mock_umwelt: MockUmwelt,
    ):
        """Test that execute works with direct AGENTESE paths."""
        result = await adapter.execute("concept.justice.refine", mock_umwelt)
        path, _, _ = mock_logos._invocations[0]
        assert path == "concept.justice.refine"

    @pytest.mark.asyncio
    async def test_min_confidence_filter(self, adapter: AgentesAdapter) -> None:
        """Test that low confidence results are filtered."""
        adapter.min_confidence = 0.99  # Very high threshold
        with pytest.raises(TranslationError):
            await adapter.translate("show me the house")  # 0.9 confidence

    @pytest.mark.asyncio
    async def test_llm_disabled(self, adapter_no_llm: AgentesAdapter) -> None:
        """Test adapter without LLM fallback."""
        # Pattern match should still work
        result = await adapter_no_llm.translate("show me the house")
        assert result.source == "pattern"

        # Non-matching should fail (no LLM fallback)
        with pytest.raises(TranslationError):
            await adapter_no_llm.translate("unique query no pattern")


# =============================================================================
# Test Factory Functions
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_adapter_basic(self) -> None:
        """Test creating basic adapter."""
        adapter = create_adapter()
        assert isinstance(adapter, AgentesAdapter)
        assert adapter.logos is None  # Not set

    def test_create_adapter_with_logos(self, mock_logos: MockLogos) -> None:
        """Test creating adapter with logos."""
        adapter = create_adapter(logos=mock_logos)
        assert adapter.logos is mock_logos

    def test_create_adapter_with_llm(self, mock_llm: MockLLM) -> None:
        """Test creating adapter with LLM."""
        adapter = create_adapter(llm=mock_llm)
        assert adapter.llm_translator.llm is mock_llm

    def test_create_adapter_with_config(self) -> None:
        """Test creating adapter with configuration."""
        adapter = create_adapter(
            min_confidence=0.8,
            use_llm_fallback=False,
        )
        assert adapter.min_confidence == 0.8
        assert adapter.use_llm_fallback is False

    def test_create_pattern_translator_basic(self) -> None:
        """Test creating basic pattern translator."""
        translator = create_pattern_translator()
        assert isinstance(translator, PatternTranslator)
        assert len(translator.patterns) == len(TRANSLATION_PATTERNS)

    def test_create_pattern_translator_with_extra(self) -> None:
        """Test creating translator with extra patterns."""
        translator = create_pattern_translator(
            extra_patterns=[
                (r"^flip\s+(\w+)$", "world.{entity}.flip", "flip", 0.9),
            ]
        )
        assert len(translator.patterns) == len(TRANSLATION_PATTERNS) + 1


# =============================================================================
# Test Prompt Building
# =============================================================================


class TestPromptBuilding:
    """Tests for LLM prompt construction."""

    def test_prompt_contains_contexts(self) -> None:
        """Test that prompt explains contexts."""
        prompt = build_translation_prompt("test input")
        assert "world" in prompt
        assert "self" in prompt
        assert "concept" in prompt
        assert "void" in prompt
        assert "time" in prompt

    def test_prompt_contains_examples(self) -> None:
        """Test that prompt contains examples."""
        prompt = build_translation_prompt("test input")
        assert "show me the house" in prompt or "world.house.manifest" in prompt

    def test_prompt_contains_input(self) -> None:
        """Test that prompt contains the input."""
        prompt = build_translation_prompt("my specific query")
        assert "my specific query" in prompt

    def test_prompt_with_context(self) -> None:
        """Test prompt with additional context."""
        prompt = build_translation_prompt(
            "test input",
            context={"previous_path": "world.house.manifest"},
        )
        assert "previous_path" in prompt or "world.house.manifest" in prompt

    def test_prompt_limits_examples(self) -> None:
        """Test that examples are limited."""
        many_examples = [(f"input{i}", f"path{i}.manifest") for i in range(50)]
        prompt = build_translation_prompt("test", examples=many_examples)
        # Should only include first 15
        assert "input14" in prompt or "path14" in prompt
        assert "input20" not in prompt


# =============================================================================
# Test Constants
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_patterns_are_valid_regex(self) -> None:
        """Test that all patterns compile."""
        for pattern, template, aspect, confidence in TRANSLATION_PATTERNS:
            assert hasattr(pattern, "match")  # Is compiled regex

    def test_patterns_have_valid_templates(self) -> None:
        """Test that templates are valid AGENTESE."""
        validator = GgentIntegration()
        for pattern, template, aspect, confidence in TRANSLATION_PATTERNS:
            # Templates with {entity} need substitution
            test_template = template.replace("{entity}", "test")
            is_valid, error = validator.validate_path(test_template)
            assert is_valid, f"Invalid template: {template} -> {error}"

    def test_examples_are_valid_agentese(self) -> None:
        """Test that all examples have valid AGENTESE paths."""
        validator = GgentIntegration()
        for nl, agentese in LLM_TRANSLATION_EXAMPLES:
            is_valid, error = validator.validate_path(agentese)
            assert is_valid, f"Invalid example path: {agentese} -> {error}"

    def test_patterns_cover_all_contexts(self) -> None:
        """Test that patterns exist for all five contexts."""
        contexts_found = set()
        for pattern, template, aspect, confidence in TRANSLATION_PATTERNS:
            test_template = template.replace("{entity}", "test")
            context = test_template.split(".")[0]
            contexts_found.add(context)

        expected = {"world", "self", "concept", "void", "time"}
        assert contexts_found == expected, (
            f"Missing contexts: {expected - contexts_found}"
        )


# =============================================================================
# Test Integration Scenarios
# =============================================================================


class TestIntegrationScenarios:
    """Tests for real-world usage scenarios."""

    @pytest.mark.asyncio
    async def test_developer_workflow(
        self, adapter: AgentesAdapter, mock_umwelt: MockUmwelt
    ):
        """Test typical developer queries."""
        # Check status
        result = await adapter.translate("get server status")
        assert result.path == "world.server.manifest"

        # View logs
        result = await adapter.translate("show me the logs")
        assert "witness" in result.path

        # Create something
        result = await adapter.translate("create a new service")
        assert "define" in result.path

    @pytest.mark.asyncio
    async def test_philosopher_workflow(
        self, adapter: AgentesAdapter, mock_umwelt: MockUmwelt
    ):
        """Test philosophical queries."""
        # Refine concepts
        result = await adapter.translate("think harder about justice")
        assert result.path == "concept.justice.refine"

        # Define new concept
        result = await adapter.translate("define beauty")
        assert result.path == "concept.beauty.define"

    @pytest.mark.asyncio
    async def test_entropy_workflow(
        self, adapter: AgentesAdapter, mock_umwelt: MockUmwelt
    ):
        """Test entropy/accursed share queries."""
        # Get randomness
        result = await adapter.translate("give me something random")
        assert result.path == "void.entropy.sip"

        # Express gratitude
        result = await adapter.translate("thank you")
        assert result.path == "void.gratitude.thank"

        # Tithe
        result = await adapter.translate("tithe")
        assert result.path == "void.gratitude.tithe"

    @pytest.mark.asyncio
    async def test_memory_workflow(
        self, adapter: AgentesAdapter, mock_umwelt: MockUmwelt
    ):
        """Test memory-related queries."""
        # View memory
        result = await adapter.translate("show my memory")
        assert result.path == "self.memory.manifest"

        # Consolidate
        result = await adapter.translate("dream")
        assert result.path == "self.memory.consolidate"

        # Check capabilities
        result = await adapter.translate("what can I do?")
        assert result.path == "self.capabilities.affordances"
