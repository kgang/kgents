"""
Tests for N-gent Bard: The Storyteller.

Tests cover:
- NarrativeGenre and Verbosity enums
- Perspective enum
- Chapter detection and structure
- NarrativeRequest filtering
- Narrative rendering (text, markdown, html)
- Bard.invoke() narrative generation
- ForensicBard.diagnose() crash analysis
- SimpleLLMProvider for testing
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from agents.n.bard import (
    Bard,
    Chapter,
    Diagnosis,
    ForensicBard,
    LLMProvider,
    Narrative,
    NarrativeGenre,
    NarrativeRequest,
    Perspective,
    SimpleLLMProvider,
    Verbosity,
    _truncate_dict,
)
from agents.n.types import Determinism, SemanticTrace

# =============================================================================
# Test Fixtures
# =============================================================================


def make_trace(
    trace_id: str = "trace-1",
    agent_id: str = "agent-1",
    agent_genus: str = "G",
    action: str = "INVOKE",
    timestamp: datetime | None = None,
    inputs: dict | None = None,
    outputs: dict | None = None,
    duration_ms: int = 100,
    gas_consumed: int = 50,
    determinism: Determinism = Determinism.PROBABILISTIC,
    parent_id: str | None = None,
) -> SemanticTrace:
    """Create a test SemanticTrace."""
    return SemanticTrace(
        trace_id=trace_id,
        parent_id=parent_id,
        timestamp=timestamp or datetime.now(),
        agent_id=agent_id,
        agent_genus=agent_genus,
        action=action,
        inputs=inputs or {"key": "value"},
        outputs=outputs or {"result": "success"},
        input_hash="abc123",
        input_snapshot=b"test",
        output_hash="def456",
        gas_consumed=gas_consumed,
        duration_ms=duration_ms,
        determinism=determinism,
    )


@pytest.fixture
def sample_traces() -> list[SemanticTrace]:
    """Create a sample list of traces for testing."""
    base_time = datetime(2024, 1, 15, 10, 0, 0)
    return [
        make_trace(
            trace_id="t1",
            agent_id="parser",
            agent_genus="G",
            action="PARSE",
            timestamp=base_time,
            inputs={"text": "hello world"},
            outputs={"tokens": ["hello", "world"]},
        ),
        make_trace(
            trace_id="t2",
            agent_id="parser",
            agent_genus="G",
            action="VALIDATE",
            timestamp=base_time + timedelta(seconds=1),
            inputs={"tokens": ["hello", "world"]},
            outputs={"valid": True},
        ),
        make_trace(
            trace_id="t3",
            agent_id="generator",
            agent_genus="J",
            action="GENERATE",
            timestamp=base_time + timedelta(seconds=2),
            inputs={"prompt": "greet user"},
            outputs={"text": "Hello, user!"},
        ),
    ]


@pytest.fixture
def error_trace() -> SemanticTrace:
    """Create an error trace for testing."""
    return make_trace(
        trace_id="err-1",
        agent_id="validator",
        agent_genus="G",
        action="ERROR",
        inputs={"data": "invalid"},
        outputs={"error": "Validation failed", "type": "ValueError"},
        determinism=Determinism.CHAOTIC,
    )


# =============================================================================
# Enum Tests
# =============================================================================


class TestNarrativeGenre:
    """Tests for NarrativeGenre enum."""

    def test_all_genres_defined(self):
        """All expected genres should be defined."""
        assert NarrativeGenre.TECHNICAL.value == "technical"
        assert NarrativeGenre.LITERARY.value == "literary"
        assert NarrativeGenre.NOIR.value == "noir"
        assert NarrativeGenre.SYSADMIN.value == "sysadmin"
        assert NarrativeGenre.MINIMAL.value == "minimal"
        assert NarrativeGenre.DETECTIVE.value == "detective"

    def test_genre_count(self):
        """Should have 6 genres."""
        assert len(NarrativeGenre) == 6


class TestVerbosity:
    """Tests for Verbosity enum."""

    def test_all_verbosity_levels(self):
        """All verbosity levels should be defined."""
        assert Verbosity.TERSE.value == "terse"
        assert Verbosity.NORMAL.value == "normal"
        assert Verbosity.VERBOSE.value == "verbose"

    def test_verbosity_count(self):
        """Should have 3 verbosity levels."""
        assert len(Verbosity) == 3


class TestPerspective:
    """Tests for Perspective enum."""

    def test_all_perspectives(self):
        """All perspectives should be defined."""
        assert Perspective.FIRST_PERSON.value == "first_person"
        assert Perspective.SECOND_PERSON.value == "second_person"
        assert Perspective.THIRD_PERSON.value == "third_person"

    def test_perspective_count(self):
        """Should have 3 perspectives."""
        assert len(Perspective) == 3


# =============================================================================
# Chapter Tests
# =============================================================================


class TestChapter:
    """Tests for Chapter dataclass."""

    def test_chapter_creation(self):
        """Can create a chapter with all fields."""
        chapter = Chapter(
            name="Chapter 1",
            start_trace_id="t1",
            end_trace_id="t5",
            theme="Processing",
            agents_involved=["agent-1", "agent-2"],
            trace_count=5,
            duration_ms=500,
        )

        assert chapter.name == "Chapter 1"
        assert chapter.start_trace_id == "t1"
        assert chapter.end_trace_id == "t5"
        assert chapter.theme == "Processing"
        assert chapter.agents_involved == ["agent-1", "agent-2"]
        assert chapter.trace_count == 5
        assert chapter.duration_ms == 500

    def test_chapter_defaults(self):
        """Chapter has sensible defaults."""
        chapter = Chapter(
            name="Ch 1",
            start_trace_id="s",
            end_trace_id="e",
            theme="Test",
            agents_involved=[],
        )

        assert chapter.trace_count == 0
        assert chapter.duration_ms == 0

    def test_chapter_converts_set_to_list(self):
        """Chapter.agents_involved converts set to list."""
        chapter = Chapter(
            name="Ch 1",
            start_trace_id="s",
            end_trace_id="e",
            theme="Test",
            agents_involved={"a", "b"},  # type: ignore
        )

        assert isinstance(chapter.agents_involved, list)
        assert set(chapter.agents_involved) == {"a", "b"}


# =============================================================================
# NarrativeRequest Tests
# =============================================================================


class TestNarrativeRequest:
    """Tests for NarrativeRequest dataclass."""

    def test_request_creation(self, sample_traces):
        """Can create a narrative request."""
        request = NarrativeRequest(
            traces=sample_traces,
            genre=NarrativeGenre.NOIR,
            perspective=Perspective.FIRST_PERSON,
            verbosity=Verbosity.VERBOSE,
        )

        assert request.traces == sample_traces
        assert request.genre == NarrativeGenre.NOIR
        assert request.perspective == Perspective.FIRST_PERSON
        assert request.verbosity == Verbosity.VERBOSE

    def test_request_defaults(self, sample_traces):
        """Request has sensible defaults."""
        request = NarrativeRequest(traces=sample_traces)

        assert request.genre == NarrativeGenre.TECHNICAL
        assert request.perspective == Perspective.THIRD_PERSON
        assert request.verbosity == Verbosity.NORMAL
        assert request.focus_agents is None
        assert request.filter_actions is None
        assert request.exclude_actions is None

    def test_filter_by_agent(self, sample_traces):
        """Can filter traces by agent."""
        request = NarrativeRequest(
            traces=sample_traces,
            focus_agents=["parser"],
        )

        filtered = request.filtered_traces()
        assert len(filtered) == 2
        assert all(t.agent_id == "parser" for t in filtered)

    def test_filter_by_action(self, sample_traces):
        """Can filter traces by action."""
        request = NarrativeRequest(
            traces=sample_traces,
            filter_actions=["GENERATE"],
        )

        filtered = request.filtered_traces()
        assert len(filtered) == 1
        assert filtered[0].action == "GENERATE"

    def test_exclude_actions(self, sample_traces):
        """Can exclude traces by action."""
        request = NarrativeRequest(
            traces=sample_traces,
            exclude_actions=["VALIDATE"],
        )

        filtered = request.filtered_traces()
        assert len(filtered) == 2
        assert all(t.action != "VALIDATE" for t in filtered)

    def test_combined_filters(self, sample_traces):
        """Can combine multiple filters."""
        request = NarrativeRequest(
            traces=sample_traces,
            focus_agents=["parser"],
            filter_actions=["PARSE", "VALIDATE"],
            exclude_actions=["VALIDATE"],
        )

        filtered = request.filtered_traces()
        assert len(filtered) == 1
        assert filtered[0].action == "PARSE"


# =============================================================================
# Narrative Tests
# =============================================================================


class TestNarrative:
    """Tests for Narrative dataclass."""

    def test_narrative_creation(self, sample_traces):
        """Can create a narrative."""
        chapters = [
            Chapter(
                name="Ch 1",
                start_trace_id="t1",
                end_trace_id="t3",
                theme="Processing",
                agents_involved=["parser", "generator"],
            )
        ]

        narrative = Narrative(
            text="Once upon a time...",
            genre=NarrativeGenre.LITERARY,
            traces_used=sample_traces,
            chapters=chapters,
            metadata={"title": "Test Story"},
        )

        assert narrative.text == "Once upon a time..."
        assert narrative.genre == NarrativeGenre.LITERARY
        assert len(narrative.traces_used) == 3
        assert len(narrative.chapters) == 1

    def test_narrative_title(self, sample_traces):
        """Narrative.title returns metadata title or default."""
        # With title
        n1 = Narrative(
            text="test",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=[],
            chapters=[],
            metadata={"title": "My Story"},
        )
        assert n1.title == "My Story"

        # Without title
        n2 = Narrative(
            text="test",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=[],
            chapters=[],
        )
        assert n2.title == "Untitled Narrative"

    def test_narrative_total_duration(self, sample_traces):
        """Narrative.total_duration_ms sums trace durations."""
        narrative = Narrative(
            text="test",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=sample_traces,
            chapters=[],
        )

        # Each sample trace has duration_ms=100
        assert narrative.total_duration_ms == 300

    def test_narrative_total_gas(self, sample_traces):
        """Narrative.total_gas sums gas consumed."""
        narrative = Narrative(
            text="test",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=sample_traces,
            chapters=[],
        )

        # Each sample trace has gas_consumed=50
        assert narrative.total_gas == 150

    def test_narrative_agent_count(self, sample_traces):
        """Narrative.agent_count returns unique agent count."""
        narrative = Narrative(
            text="test",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=sample_traces,
            chapters=[],
        )

        # Sample traces have 2 unique agents: parser, generator
        assert narrative.agent_count == 2

    def test_render_text(self, sample_traces):
        """Narrative.render('text') returns plain text."""
        narrative = Narrative(
            text="The story goes...",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=sample_traces,
            chapters=[],
        )

        assert narrative.render("text") == "The story goes..."

    def test_render_markdown(self, sample_traces):
        """Narrative.render('markdown') returns markdown."""
        chapters = [
            Chapter(
                name="Chapter 1",
                start_trace_id="t1",
                end_trace_id="t3",
                theme="Processing",
                agents_involved=["parser"],
            )
        ]

        narrative = Narrative(
            text="The story...",
            genre=NarrativeGenre.TECHNICAL,
            traces_used=sample_traces,
            chapters=chapters,
            metadata={"title": "Test"},
        )

        md = narrative.render("markdown")
        assert "# Test" in md
        assert "## Chapter 1" in md
        assert "*Theme: Processing" in md

    def test_render_html(self, sample_traces):
        """Narrative.render('html') returns HTML."""
        narrative = Narrative(
            text="The story...",
            genre=NarrativeGenre.LITERARY,
            traces_used=sample_traces,
            chapters=[],
            metadata={"title": "HTML Test"},
        )

        html = narrative.render("html")
        assert "<!DOCTYPE html>" in html
        assert "<title>HTML Test</title>" in html
        assert "Genre: literary" in html


# =============================================================================
# SimpleLLMProvider Tests
# =============================================================================


class TestSimpleLLMProvider:
    """Tests for SimpleLLMProvider."""

    @pytest.mark.asyncio
    async def test_default_response(self):
        """Provider generates default response."""
        provider = SimpleLLMProvider()
        response = await provider.generate("test prompt")

        assert "[Generated narrative from 1 call(s)]" in response
        assert provider.call_count == 1
        assert provider.last_prompt == "test prompt"

    @pytest.mark.asyncio
    async def test_custom_response(self):
        """Provider returns custom response."""
        provider = SimpleLLMProvider(response="Custom story")
        response = await provider.generate("test prompt")

        assert response == "Custom story"

    @pytest.mark.asyncio
    async def test_call_counting(self):
        """Provider tracks call count."""
        provider = SimpleLLMProvider()

        await provider.generate("prompt 1")
        await provider.generate("prompt 2")
        await provider.generate("prompt 3")

        assert provider.call_count == 3

    def test_llm_provider_protocol(self):
        """SimpleLLMProvider conforms to LLMProvider protocol."""
        provider = SimpleLLMProvider()
        assert isinstance(provider, LLMProvider)


# =============================================================================
# Bard Tests
# =============================================================================


class TestBard:
    """Tests for Bard storyteller agent."""

    @pytest.mark.asyncio
    async def test_invoke_empty_traces(self):
        """Bard handles empty trace list."""
        bard = Bard()
        request = NarrativeRequest(traces=[])

        narrative = await bard.invoke(request)

        assert narrative.text == "No events to narrate."
        assert len(narrative.traces_used) == 0
        assert len(narrative.chapters) == 0

    @pytest.mark.asyncio
    async def test_invoke_with_traces(self, sample_traces):
        """Bard generates narrative from traces."""
        llm = SimpleLLMProvider(response="A tale of parsing and generation.")
        bard = Bard(llm=llm)

        request = NarrativeRequest(traces=sample_traces)
        narrative = await bard.invoke(request)

        assert narrative.text == "A tale of parsing and generation."
        assert len(narrative.traces_used) == 3
        assert llm.call_count == 1

    @pytest.mark.asyncio
    async def test_invoke_respects_genre(self, sample_traces):
        """Bard includes genre in prompt."""
        llm = SimpleLLMProvider()
        bard = Bard(llm=llm)

        for genre in NarrativeGenre:
            request = NarrativeRequest(traces=sample_traces, genre=genre)
            narrative = await bard.invoke(request)

            assert narrative.genre == genre
            assert f"GENRE: {genre.value}" in llm.last_prompt

    @pytest.mark.asyncio
    async def test_invoke_respects_verbosity(self, sample_traces):
        """Bard includes verbosity in prompt."""
        llm = SimpleLLMProvider()
        bard = Bard(llm=llm)

        for verbosity in Verbosity:
            request = NarrativeRequest(traces=sample_traces, verbosity=verbosity)
            await bard.invoke(request)

            assert f"VERBOSITY: {verbosity.value}" in llm.last_prompt

    @pytest.mark.asyncio
    async def test_invoke_respects_perspective(self, sample_traces):
        """Bard includes perspective in prompt."""
        llm = SimpleLLMProvider()
        bard = Bard(llm=llm)

        for perspective in Perspective:
            request = NarrativeRequest(traces=sample_traces, perspective=perspective)
            await bard.invoke(request)

            assert f"PERSPECTIVE: {perspective.value}" in llm.last_prompt

    @pytest.mark.asyncio
    async def test_invoke_custom_prompt(self, sample_traces):
        """Bard includes custom prompt."""
        llm = SimpleLLMProvider()
        bard = Bard(llm=llm)

        request = NarrativeRequest(
            traces=sample_traces,
            custom_prompt="Focus on errors only.",
        )
        await bard.invoke(request)

        assert "Focus on errors only." in llm.last_prompt

    @pytest.mark.asyncio
    async def test_invoke_with_title(self, sample_traces):
        """Bard uses provided title."""
        bard = Bard()
        request = NarrativeRequest(traces=sample_traces, title="Custom Title")

        narrative = await bard.invoke(request)

        assert narrative.title == "Custom Title"

    @pytest.mark.asyncio
    async def test_invoke_generates_title(self, sample_traces):
        """Bard generates title from traces."""
        bard = Bard()
        request = NarrativeRequest(traces=sample_traces)

        narrative = await bard.invoke(request)

        # Should generate a title based on agents
        assert (
            "parser" in narrative.title.lower()
            or "generator" in narrative.title.lower()
        )

    def test_chapter_detection_agent_change(self):
        """Bard detects chapters on agent changes."""
        bard = Bard()
        base_time = datetime.now()

        traces = [
            make_trace(trace_id="t1", agent_id="a1", timestamp=base_time),
            make_trace(
                trace_id="t2", agent_id="a1", timestamp=base_time + timedelta(seconds=1)
            ),
            make_trace(
                trace_id="t3", agent_id="a2", timestamp=base_time + timedelta(seconds=2)
            ),  # New agent
            make_trace(
                trace_id="t4", agent_id="a2", timestamp=base_time + timedelta(seconds=3)
            ),
        ]

        chapters = bard._identify_chapters(traces)

        assert len(chapters) == 2
        assert "a1" in chapters[0].agents_involved
        assert "a2" in chapters[1].agents_involved

    def test_chapter_detection_temporal_gap(self):
        """Bard detects chapters on temporal gaps."""
        bard = Bard()
        base_time = datetime.now()

        traces = [
            make_trace(trace_id="t1", agent_id="a1", timestamp=base_time),
            make_trace(
                trace_id="t2",
                agent_id="a1",
                timestamp=base_time + timedelta(seconds=90),  # >60s gap
            ),
        ]

        chapters = bard._identify_chapters(traces)

        assert len(chapters) == 2

    def test_chapter_detection_error(self):
        """Bard detects chapters on error traces."""
        bard = Bard()
        base_time = datetime.now()

        traces = [
            make_trace(
                trace_id="t1", agent_id="a1", action="INVOKE", timestamp=base_time
            ),
            make_trace(
                trace_id="t2",
                agent_id="a1",
                action="ERROR",
                timestamp=base_time + timedelta(seconds=1),
            ),
            make_trace(
                trace_id="t3",
                agent_id="a1",
                action="INVOKE",
                timestamp=base_time + timedelta(seconds=2),
            ),
        ]

        chapters = bard._identify_chapters(traces)

        # Error should trigger new chapter
        assert len(chapters) >= 2

    def test_theme_inference(self):
        """Bard infers themes from actions."""
        bard = Bard()

        # Error theme
        error_traces = [make_trace(action="ERROR")]
        assert bard._infer_theme(error_traces) == "Error Handling"

        # Generation theme
        gen_traces = [make_trace(action="GENERATE")]
        assert bard._infer_theme(gen_traces) == "Generation"

        # Validation theme
        val_traces = [make_trace(action="VALIDATE")]
        assert bard._infer_theme(val_traces) == "Validation"

        # Decision theme
        dec_traces = [make_trace(action="DECIDE")]
        assert bard._infer_theme(dec_traces) == "Decision Making"

        # Default theme
        other_traces = [make_trace(action="OTHER")]
        assert bard._infer_theme(other_traces) == "Processing"

    def test_title_generation_single_agent(self):
        """Bard generates title for single agent."""
        bard = Bard()
        traces = [make_trace(agent_id="parser")]

        title = bard._generate_title(traces)
        assert "parser" in title.lower()

    def test_title_generation_multiple_agents(self):
        """Bard generates title for multiple agents."""
        bard = Bard()
        traces = [
            make_trace(agent_id="parser"),
            make_trace(agent_id="generator"),
        ]

        title = bard._generate_title(traces)
        assert "Collaboration" in title or "parser" in title.lower()

    def test_title_generation_many_agents(self):
        """Bard generates title for many agents."""
        bard = Bard()
        traces = [make_trace(agent_id=f"agent-{i}") for i in range(5)]

        title = bard._generate_title(traces)
        assert "5 agents" in title.lower()

    def test_format_crystals(self, sample_traces):
        """Bard formats crystals for prompt."""
        bard = Bard()
        formatted = bard._format_crystals(sample_traces)

        assert "Agent=parser" in formatted
        assert "Agent=generator" in formatted
        assert "Action=PARSE" in formatted
        assert "Action=GENERATE" in formatted


# =============================================================================
# ForensicBard Tests
# =============================================================================


class TestForensicBard:
    """Tests for ForensicBard crash analyst."""

    @pytest.mark.asyncio
    async def test_diagnose_basic(self, error_trace):
        """ForensicBard produces diagnosis."""
        llm = SimpleLLMProvider(
            response="Root cause: Invalid input data. The validator received malformed data."
        )
        forensic = ForensicBard(llm=llm)

        diagnosis = await forensic.diagnose(error_trace)

        assert isinstance(diagnosis, Diagnosis)
        assert diagnosis.failure_trace == error_trace
        assert (
            "Root cause" in diagnosis.probable_cause or "Invalid" in diagnosis.narrative
        )

    @pytest.mark.asyncio
    async def test_diagnose_with_context(self, error_trace, sample_traces):
        """ForensicBard uses context traces."""
        llm = SimpleLLMProvider()
        forensic = ForensicBard(llm=llm)

        diagnosis = await forensic.diagnose(
            error_trace,
            context_traces=sample_traces,
        )

        assert diagnosis.context_traces == sample_traces
        # Context should be in the prompt
        assert "parser" in llm.last_prompt.lower() or "CONTEXT" in llm.last_prompt

    @pytest.mark.asyncio
    async def test_diagnose_with_similar_failures(self, error_trace):
        """ForensicBard includes similar failures."""
        similar = [
            make_trace(
                trace_id="s1",
                action="ERROR",
                outputs={"error": "Similar error"},
            )
        ]
        llm = SimpleLLMProvider()
        forensic = ForensicBard(llm=llm)

        diagnosis = await forensic.diagnose(
            error_trace,
            similar_failures=similar,
        )

        assert diagnosis.similar_failures == similar
        assert "SIMILAR" in llm.last_prompt or "Similar error" in llm.last_prompt

    @pytest.mark.asyncio
    async def test_echo_command(self, error_trace):
        """Diagnosis includes echo command."""
        forensic = ForensicBard()
        diagnosis = await forensic.diagnose(error_trace)

        assert f"kgents echo {error_trace.trace_id}" == diagnosis.echo_command

    @pytest.mark.asyncio
    async def test_severity_critical_cascade(self):
        """Severity is critical for cascade failures."""
        forensic = ForensicBard()
        failure = make_trace(action="ERROR")
        context = [make_trace(action="ERROR") for _ in range(4)]

        diagnosis = await forensic.diagnose(failure, context_traces=context)

        assert diagnosis.severity == "critical"

    @pytest.mark.asyncio
    async def test_severity_high_chaotic(self):
        """Severity is high for chaotic failures."""
        forensic = ForensicBard()
        failure = make_trace(action="ERROR", determinism=Determinism.CHAOTIC)

        diagnosis = await forensic.diagnose(failure)

        assert diagnosis.severity == "high"

    @pytest.mark.asyncio
    async def test_severity_medium_slow(self):
        """Severity is medium for slow operations."""
        forensic = ForensicBard()
        failure = make_trace(
            action="ERROR",
            duration_ms=6000,  # >5000ms
            determinism=Determinism.DETERMINISTIC,
        )

        diagnosis = await forensic.diagnose(failure)

        assert diagnosis.severity == "medium"

    @pytest.mark.asyncio
    async def test_severity_low_default(self):
        """Default severity is low."""
        forensic = ForensicBard()
        failure = make_trace(
            action="ERROR",
            duration_ms=100,
            determinism=Determinism.DETERMINISTIC,
        )

        diagnosis = await forensic.diagnose(failure)

        assert diagnosis.severity == "low"

    def test_diagnosis_is_deterministic(self, error_trace):
        """Diagnosis.is_deterministic reflects trace determinism."""
        diag1 = Diagnosis(
            narrative="test",
            failure_trace=make_trace(determinism=Determinism.DETERMINISTIC),
            probable_cause="test",
            echo_command="test",
        )
        assert diag1.is_deterministic is True

        diag2 = Diagnosis(
            narrative="test",
            failure_trace=make_trace(determinism=Determinism.PROBABILISTIC),
            probable_cause="test",
            echo_command="test",
        )
        assert diag2.is_deterministic is False

    def test_diagnosis_agent_history(self, error_trace, sample_traces):
        """Diagnosis.agent_history returns agent sequence."""
        diag = Diagnosis(
            narrative="test",
            failure_trace=error_trace,
            probable_cause="test",
            echo_command="test",
            context_traces=sample_traces,
        )

        history = diag.agent_history
        assert history[-1] == error_trace.agent_id
        assert len(history) == len(sample_traces) + 1

    def test_extract_cause_root_cause(self):
        """ForensicBard extracts root cause from analysis."""
        forensic = ForensicBard()

        analysis = """Analysis of the failure:
The agent attempted to process data.
Root cause: Invalid configuration in the input handler.
This could be prevented by validation."""

        cause = forensic._extract_cause(analysis)
        assert "Invalid configuration" in cause

    def test_extract_cause_because(self):
        """ForensicBard extracts cause from 'because' statements."""
        forensic = ForensicBard()

        analysis = """The system failed because the memory limit was exceeded."""

        cause = forensic._extract_cause(analysis)
        assert "because" in cause.lower() or "memory" in cause.lower()

    def test_extract_cause_fallback(self):
        """ForensicBard falls back to first line."""
        forensic = ForensicBard()

        analysis = """Something went wrong here.
More details follow."""

        cause = forensic._extract_cause(analysis)
        assert "Something went wrong" in cause


# =============================================================================
# Utility Tests
# =============================================================================


class TestTruncateDict:
    """Tests for _truncate_dict utility."""

    def test_truncate_none(self):
        """Returns 'None' for None input."""
        assert _truncate_dict(None, 100) == "None"

    def test_truncate_short(self):
        """Returns full string for short dicts."""
        d = {"a": 1}
        result = _truncate_dict(d, 100)
        assert result == str(d)

    def test_truncate_long(self):
        """Truncates long dicts with ellipsis."""
        d = {"a": "x" * 100, "b": "y" * 100}
        result = _truncate_dict(d, 50)

        assert len(result) == 50
        assert result.endswith("...")


# =============================================================================
# Integration Tests
# =============================================================================


class TestBardIntegration:
    """Integration tests for Bard workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete Bard workflow from traces to narrative."""
        # Create a sequence of traces simulating an execution
        base_time = datetime.now()
        traces = [
            make_trace(
                trace_id="t1",
                agent_id="router",
                agent_genus="J",
                action="DECIDE",
                timestamp=base_time,
                inputs={"request": "/api/users"},
                outputs={"handler": "user_handler"},
            ),
            make_trace(
                trace_id="t2",
                agent_id="user_handler",
                agent_genus="G",
                action="LOOKUP",
                timestamp=base_time + timedelta(milliseconds=100),
                inputs={"id": 123},
                outputs={"user": {"name": "Alice"}},
            ),
            make_trace(
                trace_id="t3",
                agent_id="formatter",
                agent_genus="G",
                action="TRANSFORM",
                timestamp=base_time + timedelta(milliseconds=200),
                inputs={"user": {"name": "Alice"}},
                outputs={"json": '{"name":"Alice"}'},
            ),
        ]

        # Create bard with custom LLM
        llm = SimpleLLMProvider(
            response="""The router received a request for /api/users and decided to route it to the user handler.
The user handler looked up user 123 and found Alice.
The formatter transformed the user data into JSON format."""
        )
        bard = Bard(llm=llm)

        # Generate narrative
        request = NarrativeRequest(
            traces=traces,
            genre=NarrativeGenre.TECHNICAL,
            title="API Request Handling",
        )
        narrative = await bard.invoke(request)

        # Verify narrative
        assert narrative.title == "API Request Handling"
        assert len(narrative.traces_used) == 3
        assert "router" in narrative.text.lower()
        assert "Alice" in narrative.text

        # Verify markdown rendering
        md = narrative.render("markdown")
        assert "# API Request Handling" in md

    @pytest.mark.asyncio
    async def test_forensic_workflow(self):
        """Test ForensicBard crash analysis workflow."""
        base_time = datetime.now()

        # Context leading to failure
        context = [
            make_trace(
                trace_id="c1",
                agent_id="validator",
                action="VALIDATE",
                timestamp=base_time,
                inputs={"data": "good"},
                outputs={"valid": True},
            ),
            make_trace(
                trace_id="c2",
                agent_id="validator",
                action="VALIDATE",
                timestamp=base_time + timedelta(seconds=1),
                inputs={"data": "bad"},
                outputs={"valid": False},
            ),
        ]

        # The failure
        failure = make_trace(
            trace_id="f1",
            agent_id="processor",
            agent_genus="J",
            action="ERROR",
            timestamp=base_time + timedelta(seconds=2),
            inputs={"data": "bad"},
            outputs={"error": "Cannot process invalid data", "type": "ValueError"},
            determinism=Determinism.DETERMINISTIC,
        )

        # Diagnose
        llm = SimpleLLMProvider(
            response="""Root cause: The processor received data that was already flagged as invalid.
The validator correctly identified the bad data, but the processor was invoked anyway.
Prevention: Add a guard check before processing."""
        )
        forensic = ForensicBard(llm=llm)

        diagnosis = await forensic.diagnose(failure, context_traces=context)

        # Verify diagnosis
        assert "Root cause" in diagnosis.probable_cause
        assert diagnosis.failure_trace == failure
        assert len(diagnosis.context_traces) == 2
        assert diagnosis.echo_command == "kgents echo f1"
        assert diagnosis.is_deterministic is True


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_single_trace(self):
        """Bard handles single trace."""
        bard = Bard()
        traces = [make_trace()]

        request = NarrativeRequest(traces=traces)
        narrative = await bard.invoke(request)

        assert len(narrative.traces_used) == 1
        assert len(narrative.chapters) == 1

    @pytest.mark.asyncio
    async def test_all_filtered_out(self, sample_traces):
        """Bard handles all traces filtered out."""
        bard = Bard()
        request = NarrativeRequest(
            traces=sample_traces,
            focus_agents=["nonexistent"],
        )

        narrative = await bard.invoke(request)

        assert narrative.text == "No events to narrate."

    def test_empty_chapters(self):
        """Bard handles empty trace list for chapters."""
        bard = Bard()
        chapters = bard._identify_chapters([])

        assert chapters == []

    def test_large_input_truncation(self):
        """Large inputs are truncated in prompt."""
        bard = Bard()
        trace = make_trace(inputs={"large": "x" * 10000})

        formatted = bard._format_crystals([trace])
        # Should be truncated
        assert len(formatted) < 10000
