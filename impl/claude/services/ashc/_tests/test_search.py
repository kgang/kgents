"""
Tests for LLM Proof Search.

Phase 3 of the proof-generation implementation plan.

Test Categories:
1. ProofSearcher basic functionality
2. Budget management and phase progression
3. Prompt generation determinism
4. Failed tactics tracking
5. Code extraction from LLM responses
6. LemmaDatabase protocol and stub
7. Heritage hints

Heritage: "The LLM can hallucinate all it wants. The proof checker is the gatekeeper."
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock

from ..checker import CheckerResult, MockChecker, ProofChecker
from ..contracts import (
    LemmaId,
    ObligationId,
    ObligationSource,
    ProofAttempt,
    ProofAttemptId,
    ProofObligation,
    ProofSearchConfig,
    ProofSearchResult,
    ProofStatus,
    VerifiedLemma,
)
from ..search import (
    InMemoryLemmaDatabase,
    LemmaDatabase,
    ProofSearcher,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_obligation() -> ProofObligation:
    """Create a sample proof obligation for testing."""
    return ProofObligation(
        id=ObligationId("obl-test-001"),
        property="∀ x: int. x + 0 == x",
        source=ObligationSource.TEST,
        source_location="test_math.py:42",
        context=("Test: test_add_zero",),
    )


@pytest.fixture
def trivial_obligation() -> ProofObligation:
    """Create a trivially provable obligation."""
    return ProofObligation(
        id=ObligationId("obl-trivial-001"),
        property="∀ x: int. x == x",
        source=ObligationSource.TEST,
        source_location="test_identity.py:10",
    )


@pytest.fixture
def complex_obligation() -> ProofObligation:
    """Create a complex obligation that needs deep phase."""
    return ProofObligation(
        id=ObligationId("obl-complex-001"),
        property="∀ f, g, h. (f >> g) >> h == f >> (g >> h)",
        source=ObligationSource.COMPOSITION,
        source_location="test_composition.py:100",
        context=("Law: associativity of composition",),
    )


@pytest.fixture
def mock_gateway() -> MagicMock:
    """Create a mock MorpheusGateway."""
    gateway = MagicMock()

    # Create a mock response
    mock_choice = MagicMock()
    mock_choice.message.content = """```dafny
lemma Trivial()
    ensures forall x: int :: x == x
{
}
```"""

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    # Make complete return an awaitable
    async def mock_complete(*args: Any, **kwargs: Any) -> MagicMock:
        return mock_response

    gateway.complete = mock_complete
    return gateway


@pytest.fixture
def success_checker() -> MockChecker:
    """Create a mock checker that always succeeds."""
    return MockChecker(default_success=True, latency_ms=10)


@pytest.fixture
def failure_checker() -> MockChecker:
    """Create a mock checker that always fails."""
    return MockChecker(default_success=False, latency_ms=10)


@pytest.fixture
def conditional_checker() -> MockChecker:
    """Create a mock checker with conditional success."""
    checker = MockChecker(default_success=False, latency_ms=10)
    # Succeed on specific patterns
    checker.always_succeed_on(r"forall\s+x.*x\s*==\s*x")
    return checker


@pytest.fixture
def lemma_db() -> InMemoryLemmaDatabase:
    """Create an in-memory lemma database."""
    db = InMemoryLemmaDatabase()
    # Seed with some lemmas
    db.store(VerifiedLemma(
        id=LemmaId("lem-001"),
        statement="∀ x: int. x + 0 == x",
        proof="lemma AddZero() ensures forall x: int :: x + 0 == x {}",
        checker="mock",
        obligation_id=ObligationId("obl-seed-001"),
    ))
    return db


@pytest.fixture
def small_config() -> ProofSearchConfig:
    """Create a small budget config for fast testing."""
    return ProofSearchConfig(
        quick_budget=2,
        medium_budget=3,
        deep_budget=5,
        timeout_per_attempt_ms=1000,
        temperature=0.3,
    )


# =============================================================================
# Test: ProofSearcher Initialization
# =============================================================================


class TestProofSearcherInit:
    """Tests for ProofSearcher initialization."""

    def test_init_with_defaults(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Searcher initializes with default config and stub lemma DB."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        assert searcher.config.quick_budget == 10
        assert searcher.config.medium_budget == 50
        assert searcher.config.deep_budget == 200
        assert searcher.config.temperature == 0.3

    def test_init_with_custom_config(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        small_config: ProofSearchConfig,
    ) -> None:
        """Searcher respects custom configuration."""
        searcher = ProofSearcher(
            mock_gateway,
            success_checker,
            config=small_config,
        )

        assert searcher.config.quick_budget == 2
        assert searcher.config.medium_budget == 3
        assert searcher.config.deep_budget == 5

    def test_init_with_lemma_db(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        lemma_db: InMemoryLemmaDatabase,
    ) -> None:
        """Searcher accepts custom lemma database."""
        searcher = ProofSearcher(
            mock_gateway,
            success_checker,
            lemma_db=lemma_db,
        )

        # Can access the lemma DB through hints
        assert lemma_db.lemma_count == 1


# =============================================================================
# Test: Basic Search Functionality
# =============================================================================


class TestSearchBasic:
    """Tests for basic search functionality."""

    @pytest.mark.asyncio
    async def test_search_succeeds_quick_phase(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        trivial_obligation: ProofObligation,
        small_config: ProofSearchConfig,
    ) -> None:
        """Quick phase discharges trivial obligations."""
        searcher = ProofSearcher(
            mock_gateway,
            success_checker,
            config=small_config,
        )

        result = await searcher.search(trivial_obligation)

        assert result.succeeded
        assert result.lemma is not None
        assert result.budget_used <= small_config.quick_budget

    @pytest.mark.asyncio
    async def test_search_exhausts_budget(
        self,
        mock_gateway: MagicMock,
        failure_checker: MockChecker,
        sample_obligation: ProofObligation,
        small_config: ProofSearchConfig,
    ) -> None:
        """Search exhausts budget when all attempts fail."""
        searcher = ProofSearcher(
            mock_gateway,
            failure_checker,
            config=small_config,
        )

        result = await searcher.search(sample_obligation)

        assert not result.succeeded
        assert result.lemma is None
        assert result.budget_used == small_config.total_budget

    @pytest.mark.asyncio
    async def test_search_records_all_attempts(
        self,
        mock_gateway: MagicMock,
        failure_checker: MockChecker,
        sample_obligation: ProofObligation,
        small_config: ProofSearchConfig,
    ) -> None:
        """Search records all proof attempts."""
        searcher = ProofSearcher(
            mock_gateway,
            failure_checker,
            config=small_config,
        )

        result = await searcher.search(sample_obligation)

        assert len(result.attempts) == small_config.total_budget
        for attempt in result.attempts:
            assert attempt.obligation_id == sample_obligation.id
            assert attempt.result == ProofStatus.FAILED


# =============================================================================
# Test: Phase Progression
# =============================================================================


class TestPhaseProgression:
    """Tests for phase progression through Quick → Medium → Deep."""

    @pytest.mark.asyncio
    async def test_phases_use_correct_budgets(
        self,
        mock_gateway: MagicMock,
        failure_checker: MockChecker,
        sample_obligation: ProofObligation,
        small_config: ProofSearchConfig,
    ) -> None:
        """Phases consume correct budget amounts."""
        searcher = ProofSearcher(
            mock_gateway,
            failure_checker,
            config=small_config,
        )

        result = await searcher.search(sample_obligation)

        # Count attempts by phase (from attempt IDs)
        quick_attempts = [a for a in result.attempts if "quick" in a.id]
        medium_attempts = [a for a in result.attempts if "medium" in a.id]
        deep_attempts = [a for a in result.attempts if "deep" in a.id]

        assert len(quick_attempts) == small_config.quick_budget
        assert len(medium_attempts) == small_config.medium_budget
        assert len(deep_attempts) == small_config.deep_budget

    @pytest.mark.asyncio
    async def test_success_stops_phase_progression(
        self,
        mock_gateway: MagicMock,
        sample_obligation: ProofObligation,
        small_config: ProofSearchConfig,
    ) -> None:
        """Success in one phase stops progression to next."""
        # Create a checker that succeeds on third attempt
        checker = MockChecker(default_success=False, latency_ms=10)
        call_count = 0

        original_check = checker.check

        async def succeed_on_third(*args: Any, **kwargs: Any) -> CheckerResult:
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                return CheckerResult(success=True, duration_ms=10)
            return await original_check(*args, **kwargs)

        checker.check = succeed_on_third  # type: ignore

        searcher = ProofSearcher(
            mock_gateway,
            checker,
            config=small_config,
        )

        result = await searcher.search(sample_obligation)

        assert result.succeeded
        assert result.budget_used == 3  # Stopped after third attempt


# =============================================================================
# Test: Prompt Generation
# =============================================================================


class TestPromptGeneration:
    """Tests for _build_prompt determinism and structure."""

    def test_prompt_is_deterministic(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        sample_obligation: ProofObligation,
    ) -> None:
        """Same inputs produce same prompt."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        prompt1 = searcher._build_prompt(
            sample_obligation,
            tactics=("simp", "auto"),
            hints=("hint1",),
            failed_tactics={"blast"},
        )

        prompt2 = searcher._build_prompt(
            sample_obligation,
            tactics=("simp", "auto"),
            hints=("hint1",),
            failed_tactics={"blast"},
        )

        assert prompt1 == prompt2

    def test_prompt_includes_property(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        sample_obligation: ProofObligation,
    ) -> None:
        """Prompt includes the obligation property."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        prompt = searcher._build_prompt(
            sample_obligation,
            tactics=("simp",),
            hints=(),
            failed_tactics=set(),
        )

        assert sample_obligation.property in prompt
        assert sample_obligation.source_location in prompt

    def test_prompt_includes_tactics(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        sample_obligation: ProofObligation,
    ) -> None:
        """Prompt lists available tactics."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        prompt = searcher._build_prompt(
            sample_obligation,
            tactics=("simp", "auto", "blast"),
            hints=(),
            failed_tactics=set(),
        )

        assert "simp" in prompt
        assert "auto" in prompt
        assert "blast" in prompt

    def test_prompt_includes_hints(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        sample_obligation: ProofObligation,
    ) -> None:
        """Prompt includes hints when provided."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        prompt = searcher._build_prompt(
            sample_obligation,
            tactics=("simp",),
            hints=("Use induction", "Check base case"),
            failed_tactics=set(),
        )

        assert "Use induction" in prompt
        assert "Check base case" in prompt

    def test_prompt_includes_failed_tactics(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        sample_obligation: ProofObligation,
    ) -> None:
        """Prompt warns about failed tactics."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        prompt = searcher._build_prompt(
            sample_obligation,
            tactics=("simp", "blast"),
            hints=(),
            failed_tactics={"blast", "simp"},
        )

        assert "Avoid" in prompt
        assert "blast" in prompt
        assert "simp" in prompt

    def test_prompt_bounds_hints(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        sample_obligation: ProofObligation,
    ) -> None:
        """Prompt limits hints to prevent bloat."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        many_hints = tuple(f"hint{i}" for i in range(20))

        prompt = searcher._build_prompt(
            sample_obligation,
            tactics=("simp",),
            hints=many_hints,
            failed_tactics=set(),
        )

        # Should only include last 5 hints
        assert "hint19" in prompt
        assert "hint15" in prompt
        assert "hint0" not in prompt


# =============================================================================
# Test: Failed Tactics Tracking
# =============================================================================


class TestFailedTacticsTracking:
    """Tests for stigmergic anti-pheromone: tracking failed tactics."""

    @pytest.mark.asyncio
    async def test_failed_tactics_accumulate(
        self,
        mock_gateway: MagicMock,
        failure_checker: MockChecker,
        sample_obligation: ProofObligation,
        small_config: ProofSearchConfig,
    ) -> None:
        """Failed tactics accumulate across attempts."""
        searcher = ProofSearcher(
            mock_gateway,
            failure_checker,
            config=small_config,
        )

        result = await searcher.search(sample_obligation)

        # All attempts should contribute to failed tactics
        failed = result.tactics_that_failed
        assert len(failed) > 0

    @pytest.mark.asyncio
    async def test_failed_tactics_not_repeated(
        self,
        sample_obligation: ProofObligation,
        failure_checker: MockChecker,
        small_config: ProofSearchConfig,
    ) -> None:
        """Later prompts mention avoiding failed tactics."""
        prompts_captured: list[str] = []

        # Create a mock gateway that captures prompts
        mock_gateway = MagicMock()

        mock_choice = MagicMock()
        mock_choice.message.content = "lemma Test() ensures true {}"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        async def capture_complete(request: Any, **kwargs: Any) -> MagicMock:
            # Extract prompt from messages
            if hasattr(request, 'messages') and len(request.messages) > 1:
                prompts_captured.append(request.messages[1].content)
            return mock_response

        mock_gateway.complete = capture_complete

        searcher = ProofSearcher(
            mock_gateway,
            failure_checker,
            config=small_config,
        )

        await searcher.search(sample_obligation)

        # Later prompts should mention avoiding failed tactics
        if len(prompts_captured) >= 3:
            later_prompts = prompts_captured[2:]
            any_avoid = any("Avoid" in p for p in later_prompts)
            assert any_avoid, "Later prompts should mention avoiding failed tactics"


# =============================================================================
# Test: Code Extraction
# =============================================================================


class TestCodeExtraction:
    """Tests for _extract_code handling various LLM output formats."""

    def test_extract_dafny_code_block(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Extract code from ```dafny blocks."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        response = """Here's the proof:

```dafny
lemma AddZero()
    ensures forall x: int :: x + 0 == x
{
}
```

This proves the property."""

        code = searcher._extract_code(response)

        assert "lemma AddZero()" in code
        assert "ensures" in code
        assert "Here's the proof" not in code

    def test_extract_generic_code_block(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Extract code from generic ``` blocks."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        response = """```
lemma Test()
    ensures true
{
}
```"""

        code = searcher._extract_code(response)

        assert "lemma Test()" in code

    def test_extract_plain_code(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Extract code when no code blocks present."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        response = """lemma Plain()
    ensures forall x: int :: x == x
{
}"""

        code = searcher._extract_code(response)

        assert "lemma Plain()" in code

    def test_extract_code_with_prose(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Extract code ignoring leading prose."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        response = """I'll create a proof for you.
Here is my approach:

lemma Proof()
    ensures true
{
}"""

        code = searcher._extract_code(response)

        assert "lemma Proof()" in code
        assert "I'll create" not in code

    def test_extract_empty_response(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Handle empty LLM response gracefully."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        code = searcher._extract_code("")

        assert code == ""


# =============================================================================
# Test: InMemoryLemmaDatabase
# =============================================================================


class TestInMemoryLemmaDatabase:
    """Tests for the stub lemma database."""

    def test_empty_db_returns_empty(self) -> None:
        """Empty database returns no related lemmas."""
        db = InMemoryLemmaDatabase()

        related = db.find_related("∀ x. x == x")

        assert related == []

    def test_store_and_retrieve(self) -> None:
        """Stored lemmas can be retrieved."""
        db = InMemoryLemmaDatabase()
        lemma = VerifiedLemma(
            id=LemmaId("lem-001"),
            statement="∀ x: int. x + 0 == x",
            proof="lemma proof {}",
            checker="mock",
            obligation_id=ObligationId("obl-001"),
        )

        db.store(lemma)
        related = db.find_related("∀ x: int. x + 0 == x")

        assert len(related) == 1
        assert related[0].id == lemma.id

    def test_find_related_by_keywords(self) -> None:
        """Find related lemmas by keyword overlap."""
        db = InMemoryLemmaDatabase()

        # Store lemmas with different keywords
        db.store(VerifiedLemma(
            id=LemmaId("lem-add"),
            statement="∀ x: int. x + 0 == x",
            proof="",
            checker="mock",
            obligation_id=ObligationId("obl-1"),
        ))
        db.store(VerifiedLemma(
            id=LemmaId("lem-mul"),
            statement="∀ y: int. y * 1 == y",
            proof="",
            checker="mock",
            obligation_id=ObligationId("obl-2"),
        ))

        # Search for addition-related
        related = db.find_related("∀ x: int. x + 1 == x + 1")

        # Should find the addition lemma (has "x" and "int")
        assert len(related) >= 1
        assert any(l.id == LemmaId("lem-add") for l in related)

    def test_limit_respected(self) -> None:
        """Find related respects limit parameter."""
        db = InMemoryLemmaDatabase()

        # Store many lemmas
        for i in range(10):
            db.store(VerifiedLemma(
                id=LemmaId(f"lem-{i}"),
                statement=f"∀ x: int. x + {i} == x + {i}",
                proof="",
                checker="mock",
                obligation_id=ObligationId(f"obl-{i}"),
            ))

        related = db.find_related("∀ x: int. something", limit=3)

        assert len(related) <= 3

    def test_usage_count_affects_ranking(self) -> None:
        """More-used lemmas rank higher (stigmergic reinforcement)."""
        db = InMemoryLemmaDatabase()

        # Store two similar lemmas with different usage counts
        low_usage = VerifiedLemma(
            id=LemmaId("lem-low"),
            statement="∀ x: int. x == x",
            proof="",
            checker="mock",
            obligation_id=ObligationId("obl-1"),
            usage_count=1,
        )
        high_usage = VerifiedLemma(
            id=LemmaId("lem-high"),
            statement="∀ x: int. x == x",
            proof="",
            checker="mock",
            obligation_id=ObligationId("obl-2"),
            usage_count=100,
        )

        db.store(low_usage)
        db.store(high_usage)

        related = db.find_related("∀ x: int. x == x", limit=2)

        # High usage should be first
        assert related[0].id == LemmaId("lem-high")


# =============================================================================
# Test: Heritage Hints
# =============================================================================


class TestHeritageHints:
    """Tests for heritage hints from spec §10, §12."""

    def test_polynomial_pattern_hint(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Polynomial-related obligations get polynomial hints."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        obl = ProofObligation(
            id=ObligationId("obl-poly"),
            property="∀ p: Polynomial. p.degree >= 0",
            source=ObligationSource.TYPE,
            source_location="polynomial.py:10",
        )

        hints = searcher._heritage_hints(obl)

        assert any("polynomial" in h.lower() for h in hints)

    def test_composition_pattern_hint(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Composition obligations get associativity hints."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        obl = ProofObligation(
            id=ObligationId("obl-comp"),
            property="(f >> g) >> h == f >> (g >> h)",
            source=ObligationSource.COMPOSITION,
            source_location="pipeline.py:20",
        )

        hints = searcher._heritage_hints(obl)

        assert any("associativity" in h.lower() for h in hints)
        assert any(">>" in h for h in hints)

    def test_identity_pattern_hint(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Identity-related obligations get identity law hints."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        obl = ProofObligation(
            id=ObligationId("obl-id"),
            property="Identity >> f == f",
            source=ObligationSource.COMPOSITION,
            source_location="identity.py:5",
        )

        hints = searcher._heritage_hints(obl)

        assert any("identity" in h.lower() for h in hints)


# =============================================================================
# Test: Temperature Configuration
# =============================================================================


class TestTemperatureConfiguration:
    """Tests for temperature as hyper-parameter."""

    def test_temperature_in_config(self) -> None:
        """ProofSearchConfig includes temperature."""
        config = ProofSearchConfig()
        assert hasattr(config, "temperature")
        assert config.temperature == 0.3

    def test_temperature_configurable(self) -> None:
        """Temperature can be customized."""
        config = ProofSearchConfig(temperature=0.7)
        assert config.temperature == 0.7

    @pytest.mark.asyncio
    async def test_temperature_used_in_request(
        self,
        success_checker: MockChecker,
        sample_obligation: ProofObligation,
    ) -> None:
        """Temperature is passed to LLM request."""
        captured_temp: list[float] = []

        mock_gateway = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "lemma Test() ensures true {}"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        async def capture_complete(request: Any, **kwargs: Any) -> MagicMock:
            if hasattr(request, 'temperature'):
                captured_temp.append(request.temperature)
            return mock_response

        mock_gateway.complete = capture_complete

        config = ProofSearchConfig(
            quick_budget=1,
            medium_budget=0,
            deep_budget=0,
            temperature=0.5,
        )

        searcher = ProofSearcher(
            mock_gateway,
            success_checker,
            config=config,
        )

        await searcher.search(sample_obligation)

        assert 0.5 in captured_temp


# =============================================================================
# Test: Tactics Extraction
# =============================================================================


class TestTacticsExtraction:
    """Tests for extracting tactics from proof source."""

    def test_extract_basic_tactics(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Extract basic Dafny tactics."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        proof = """
lemma Test()
    requires x > 0
    ensures x >= 0
{
    assert x > 0;
}
"""

        tactics = searcher._extract_tactics(proof)

        assert "requires" in tactics
        assert "ensures" in tactics
        assert "assert" in tactics

    def test_extract_forall_exists(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
    ) -> None:
        """Extract quantifier tactics."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        proof = "forall x :: exists y :: x < y"

        tactics = searcher._extract_tactics(proof)

        assert "forall" in tactics
        assert "exists" in tactics


# =============================================================================
# Test: Result Properties
# =============================================================================


class TestResultProperties:
    """Tests for ProofSearchResult computed properties."""

    @pytest.mark.asyncio
    async def test_succeeded_property(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        trivial_obligation: ProofObligation,
        small_config: ProofSearchConfig,
    ) -> None:
        """succeeded property reflects lemma presence."""
        searcher = ProofSearcher(
            mock_gateway,
            success_checker,
            config=small_config,
        )

        result = await searcher.search(trivial_obligation)

        assert result.succeeded == (result.lemma is not None)

    @pytest.mark.asyncio
    async def test_budget_remaining_property(
        self,
        mock_gateway: MagicMock,
        failure_checker: MockChecker,
        sample_obligation: ProofObligation,
        small_config: ProofSearchConfig,
    ) -> None:
        """budget_remaining property is accurate."""
        searcher = ProofSearcher(
            mock_gateway,
            failure_checker,
            config=small_config,
        )

        result = await searcher.search(sample_obligation)

        assert result.budget_remaining == 0
        assert result.budget_used == result.budget_total


# =============================================================================
# Test: LemmaDatabase Protocol
# =============================================================================


class TestLemmaDatabaseProtocol:
    """Tests for LemmaDatabase protocol compliance."""

    def test_in_memory_implements_protocol(self) -> None:
        """InMemoryLemmaDatabase implements LemmaDatabase protocol."""
        db = InMemoryLemmaDatabase()

        # Protocol methods exist
        assert hasattr(db, "find_related")
        assert hasattr(db, "store")

        # Can be used as LemmaDatabase
        assert isinstance(db, LemmaDatabase)


# =============================================================================
# Test: Gather Hints
# =============================================================================


class TestGatherHints:
    """Tests for _gather_hints combining lemma DB and attempt analysis."""

    def test_gather_hints_from_lemma_db(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        lemma_db: InMemoryLemmaDatabase,
        sample_obligation: ProofObligation,
    ) -> None:
        """Hints include related lemmas from database."""
        searcher = ProofSearcher(
            mock_gateway,
            success_checker,
            lemma_db=lemma_db,
        )

        result = ProofSearchResult(obligation=sample_obligation)
        hints = searcher._gather_hints(sample_obligation, result)

        assert any("Related lemma" in h for h in hints)

    def test_gather_hints_from_errors(
        self,
        mock_gateway: MagicMock,
        success_checker: MockChecker,
        sample_obligation: ProofObligation,
    ) -> None:
        """Hints include patterns from checker error messages."""
        searcher = ProofSearcher(mock_gateway, success_checker)

        result = ProofSearchResult(obligation=sample_obligation)
        result.attempts.append(
            ProofAttempt(
                id=ProofAttemptId("att-001"),
                obligation_id=sample_obligation.id,
                proof_source="",
                checker="mock",
                result=ProofStatus.FAILED,
                checker_output="postcondition might not hold",
                duration_ms=10,
            )
        )

        hints = searcher._gather_hints(sample_obligation, result)

        assert any("Postcondition" in h for h in hints)
