"""
Tests for the ASHC Bridge: Derivation ↔ ASHC Evidence integration.

Phase 2 of the Derivation Framework tests.

These tests verify:
1. extract_principle_evidence() correctly maps ASHC results to principles
2. update_derivation_from_ashc() updates derivations with ASHC evidence
3. merge_principle_draws() correctly combines evidence
4. sync_from_principle_registry() bridges causal penalty credibility
5. lemma_strengthens_derivation() adds categorical evidence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

import pytest

from ..ashc_bridge import (
    _classify_lemma_to_principle,
    _classify_test_name,
    extract_principle_evidence,
    lemma_strengthens_derivation,
    merge_principle_draws,
    sync_from_principle_registry,
    sync_to_principle_registry,
    update_derivation_from_ashc,
)
from ..registry import DerivationRegistry
from ..types import (
    Derivation,
    DerivationTier,
    EvidenceType,
    PrincipleDraw,
)

# =============================================================================
# Test Fixtures: Minimal ASHC Types for Testing
# =============================================================================


@dataclass(frozen=True)
class MockTestReport:
    """Minimal TestReport for testing."""

    passed: int = 10
    failed: int = 0
    total: int = 10
    success: bool = True


@dataclass(frozen=True)
class MockTypeReport:
    """Minimal TypeReport for testing."""

    passed: bool = True
    errors: int = 0


@dataclass(frozen=True)
class MockLintReport:
    """Minimal LintReport for testing."""

    passed: bool = True
    errors: int = 0


@dataclass(frozen=True)
class MockRun:
    """Minimal Run for testing."""

    run_id: str = field(default_factory=lambda: str(uuid4()))
    test_results: MockTestReport = field(default_factory=MockTestReport)
    type_results: MockTypeReport = field(default_factory=MockTypeReport)
    lint_results: MockLintReport = field(default_factory=MockLintReport)
    prompt_used: str = ""
    implementation: str = ""
    verification_score: float = 1.0

    @property
    def passed(self) -> bool:
        return self.test_results.success and self.type_results.passed and self.lint_results.passed


@dataclass(frozen=True)
class MockEvidence:
    """Minimal Evidence for testing."""

    runs: tuple[MockRun, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def equivalence_score(self) -> float:
        if not self.runs:
            return 0.0
        return sum(1 for r in self.runs if r.passed) / len(self.runs)


@dataclass(frozen=True)
class MockASHCOutput:
    """Minimal ASHCOutput for testing."""

    evidence: MockEvidence = field(default_factory=MockEvidence)
    executable: str = ""
    spec_hash: str = ""


@dataclass(frozen=True)
class MockAdaptiveRunResult:
    """Minimal AdaptiveRunResult for testing."""

    run_id: str = field(default_factory=lambda: str(uuid4()))
    success: bool = True


@dataclass(frozen=True)
class MockBetaPrior:
    """Minimal BetaPrior for testing."""

    alpha: float = 10.0
    beta: float = 2.0

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)


@dataclass(frozen=True)
class MockStoppingConfig:
    """Minimal StoppingConfig for testing."""

    n_diff: int = 2
    max_samples: int = 20


class MockStoppingDecision:
    """Enum-like for testing."""

    STOP_SUCCESS = "stop_success"


@dataclass(frozen=True)
class MockAdaptiveEvidence:
    """Minimal AdaptiveEvidence for testing."""

    runs: tuple[MockAdaptiveRunResult, ...] = ()
    posterior: MockBetaPrior = field(default_factory=MockBetaPrior)
    decision: str = "stop_success"
    config: MockStoppingConfig = field(default_factory=MockStoppingConfig)

    @property
    def sample_count(self) -> int:
        return len(self.runs)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.runs if r.success)

    @property
    def posterior_mean(self) -> float:
        return self.posterior.mean

    @property
    def is_success(self) -> bool:
        return self.decision == "stop_success"


# =============================================================================
# Test: Test Name Classification
# =============================================================================


class TestClassifyTestName:
    """Tests for _classify_test_name helper."""

    def test_composition_patterns(self) -> None:
        """Composition-related test names map to Composable."""
        assert _classify_test_name("test_composition_laws") == "Composable"
        assert _classify_test_name("test_associativity") == "Composable"
        assert _classify_test_name("test_identity_preservation") == "Composable"
        assert _classify_test_name("test_pipeline_execution") == "Composable"

    def test_heterarchy_patterns(self) -> None:
        """Mode-switching test names map to Heterarchical."""
        assert _classify_test_name("test_mode_switching") == "Heterarchical"
        assert _classify_test_name("test_dual_mode_operation") == "Heterarchical"
        assert _classify_test_name("test_autonomous_behavior") == "Heterarchical"

    def test_generative_patterns(self) -> None:
        """Regeneration test names map to Generative."""
        assert _classify_test_name("test_regeneration") == "Generative"
        assert _classify_test_name("test_spec_to_impl") == "Generative"
        assert _classify_test_name("test_compression") == "Generative"

    def test_curated_patterns(self) -> None:
        """Curation test names map to Curated."""
        assert _classify_test_name("test_deduplication") == "Curated"
        assert _classify_test_name("test_curation") == "Curated"
        assert _classify_test_name("test_quality_selection") == "Curated"

    def test_unknown_patterns(self) -> None:
        """Unknown patterns return None."""
        assert _classify_test_name("test_foobar") is None
        assert _classify_test_name("random_test") is None


# =============================================================================
# Test: Extract Principle Evidence
# =============================================================================


class TestExtractPrincipleEvidence:
    """Tests for extract_principle_evidence function."""

    def test_empty_evidence(self) -> None:
        """Empty evidence returns empty draws."""
        evidence = MockEvidence(runs=())
        draws = extract_principle_evidence(evidence)
        assert draws == ()

    def test_all_passing_runs(self) -> None:
        """Passing runs generate Composable and Tasteful evidence."""
        runs = tuple(MockRun() for _ in range(5))
        evidence = MockEvidence(runs=runs)

        draws = extract_principle_evidence(evidence)

        # Should have evidence for Composable (from tests/types) and Tasteful (from lint)
        principles = {d.principle for d in draws}
        assert "Composable" in principles
        assert "Tasteful" in principles

    def test_draw_strength_proportional(self) -> None:
        """Draw strength reflects pass rate."""
        # All passing
        all_pass = MockEvidence(runs=tuple(MockRun() for _ in range(5)))
        draws_pass = extract_principle_evidence(all_pass)
        composable_pass = next(d for d in draws_pass if d.principle == "Composable")

        # Partial passing (50%)
        mixed_runs = (
            MockRun(test_results=MockTestReport(success=True)),
            MockRun(test_results=MockTestReport(success=False, passed=0, failed=10)),
        )
        partial = MockEvidence(runs=mixed_runs)
        draws_partial = extract_principle_evidence(partial)
        composable_partial = next(d for d in draws_partial if d.principle == "Composable")

        # All passing should have higher strength
        assert composable_pass.draw_strength >= composable_partial.draw_strength

    def test_evidence_type_is_empirical(self) -> None:
        """All extracted evidence is EMPIRICAL, not CATEGORICAL."""
        runs = tuple(MockRun() for _ in range(5))
        evidence = MockEvidence(runs=runs)

        draws = extract_principle_evidence(evidence)

        for draw in draws:
            assert draw.evidence_type == EvidenceType.EMPIRICAL

    def test_draw_strength_capped(self) -> None:
        """Draw strength is capped below 1.0 for empirical evidence."""
        runs = tuple(MockRun() for _ in range(100))  # Many perfect runs
        evidence = MockEvidence(runs=runs)

        draws = extract_principle_evidence(evidence)

        for draw in draws:
            assert draw.draw_strength < 1.0  # Never reaches categorical certainty

    def test_ashc_output_wrapper(self) -> None:
        """ASHCOutput wrapper is handled correctly."""
        runs = tuple(MockRun() for _ in range(3))
        evidence = MockEvidence(runs=runs)
        output = MockASHCOutput(evidence=evidence)

        draws = extract_principle_evidence(output)

        assert len(draws) > 0
        assert all(d.evidence_type == EvidenceType.EMPIRICAL for d in draws)

    def test_adaptive_evidence(self) -> None:
        """AdaptiveEvidence with Bayesian posterior is handled."""
        runs = tuple(MockAdaptiveRunResult(success=True) for _ in range(5))
        adaptive = MockAdaptiveEvidence(
            runs=runs,
            posterior=MockBetaPrior(alpha=15.0, beta=2.0),  # ~88% posterior
        )

        draws = extract_principle_evidence(adaptive)

        # Should have Composable from successful runs
        principles = {d.principle for d in draws}
        assert "Composable" in principles


# =============================================================================
# Test: Merge Principle Draws
# =============================================================================


class TestMergePrincipleDraws:
    """Tests for merge_principle_draws function."""

    def test_new_principle_added(self) -> None:
        """New principles are simply added."""
        existing = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.8,
                evidence_type=EvidenceType.EMPIRICAL,
            ),
        )
        new = (
            PrincipleDraw(
                principle="Tasteful",
                draw_strength=0.7,
                evidence_type=EvidenceType.EMPIRICAL,
            ),
        )

        merged = merge_principle_draws(existing, new)

        assert len(merged) == 2
        principles = {d.principle for d in merged}
        assert principles == {"Composable", "Tasteful"}

    def test_categorical_never_demoted(self) -> None:
        """Categorical evidence is never replaced by empirical."""
        existing = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=1.0,
                evidence_type=EvidenceType.CATEGORICAL,
                evidence_sources=("formal-proof",),
            ),
        )
        new = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.5,  # Lower strength
                evidence_type=EvidenceType.EMPIRICAL,
            ),
        )

        merged = merge_principle_draws(existing, new)

        assert len(merged) == 1
        assert merged[0].evidence_type == EvidenceType.CATEGORICAL
        assert merged[0].draw_strength == 1.0

    def test_empirical_upgraded_to_categorical(self) -> None:
        """Empirical evidence can be upgraded to categorical."""
        existing = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.8,
                evidence_type=EvidenceType.EMPIRICAL,
            ),
        )
        new = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=1.0,
                evidence_type=EvidenceType.CATEGORICAL,
                evidence_sources=("new-proof",),
            ),
        )

        merged = merge_principle_draws(existing, new)

        assert len(merged) == 1
        assert merged[0].evidence_type == EvidenceType.CATEGORICAL
        assert merged[0].draw_strength == 1.0

    def test_empirical_weighted_average(self) -> None:
        """Two empirical draws merge with weighted average."""
        existing = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.6,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=("old",),
            ),
        )
        new = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.9,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=("new",),
            ),
        )

        merged = merge_principle_draws(existing, new)

        assert len(merged) == 1
        # 60% new (0.9) + 40% old (0.6) = 0.54 + 0.24 = 0.78
        assert 0.75 <= merged[0].draw_strength <= 0.80

    def test_evidence_sources_merged(self) -> None:
        """Evidence sources are combined and deduped."""
        existing = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.8,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=("a", "b"),
            ),
        )
        new = (
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.8,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=("b", "c"),  # b is duplicate
            ),
        )

        merged = merge_principle_draws(existing, new)

        # New sources come first, then old, deduped
        sources = merged[0].evidence_sources
        assert "b" in sources
        assert "c" in sources
        assert "a" in sources
        # b should appear only once
        assert sources.count("b") == 1 or len([s for s in sources if s == "b"]) == 1


# =============================================================================
# Test: Update Derivation from ASHC
# =============================================================================


class TestUpdateDerivationFromASHC:
    """Tests for update_derivation_from_ashc function."""

    @pytest.fixture
    def registry(self) -> DerivationRegistry:
        """Create a fresh registry with a derived agent."""
        reg = DerivationRegistry()
        reg.register(
            agent_name="TestAgent",
            derives_from=("Compose",),
            principle_draws=(),
            tier=DerivationTier.FUNCTOR,
        )
        return reg

    @pytest.mark.asyncio
    async def test_updates_empirical_confidence(self, registry: DerivationRegistry) -> None:
        """ASHC evidence updates empirical confidence."""
        runs = tuple(MockRun() for _ in range(5))
        evidence = MockEvidence(runs=runs)
        output = MockASHCOutput(evidence=evidence)

        before = registry.get("TestAgent")
        assert before is not None
        assert before.empirical_confidence == 0.0

        await update_derivation_from_ashc(registry, "TestAgent", output)

        after = registry.get("TestAgent")
        assert after is not None
        assert after.empirical_confidence > 0.0

    @pytest.mark.asyncio
    async def test_adds_principle_draws(self, registry: DerivationRegistry) -> None:
        """ASHC evidence adds principle draws."""
        runs = tuple(MockRun() for _ in range(5))
        evidence = MockEvidence(runs=runs)
        output = MockASHCOutput(evidence=evidence)

        before = registry.get("TestAgent")
        assert before is not None
        assert len(before.principle_draws) == 0

        await update_derivation_from_ashc(registry, "TestAgent", output)

        after = registry.get("TestAgent")
        assert after is not None
        assert len(after.principle_draws) > 0

    @pytest.mark.asyncio
    async def test_unknown_agent_raises(self, registry: DerivationRegistry) -> None:
        """Updating unknown agent raises KeyError."""
        output = MockASHCOutput()

        with pytest.raises(KeyError, match="UnknownAgent"):
            await update_derivation_from_ashc(registry, "UnknownAgent", output)

    @pytest.mark.asyncio
    async def test_adaptive_evidence_uses_posterior(self, registry: DerivationRegistry) -> None:
        """AdaptiveEvidence uses posterior mean for confidence."""
        runs = tuple(MockAdaptiveRunResult(success=True) for _ in range(5))
        adaptive = MockAdaptiveEvidence(
            runs=runs,
            posterior=MockBetaPrior(alpha=15.0, beta=2.0),
        )

        await update_derivation_from_ashc(registry, "TestAgent", adaptive)

        after = registry.get("TestAgent")
        assert after is not None
        # Posterior mean ~0.88, should be reflected in empirical_confidence
        assert after.empirical_confidence > 0.8


# =============================================================================
# Test: Sync with PrincipleRegistry
# =============================================================================


@dataclass
class MockPrincipleCredibility:
    """Mock PrincipleCredibility for testing."""

    principle_id: str
    credibility: float = 1.0
    times_cited: int = 0
    times_blamed: int = 0

    def cite(self) -> None:
        self.times_cited += 1

    def reward(self, weight: float = 0.01) -> None:
        self.credibility = min(1.0, self.credibility + weight)

    @property
    def is_discredited(self) -> bool:
        return self.credibility <= 0.0

    @property
    def is_predictive(self) -> bool:
        return self.times_cited >= 5 and self.times_blamed / max(1, self.times_cited) < 0.2


@dataclass
class MockPrincipleRegistry:
    """Mock PrincipleRegistry for testing."""

    principles: dict[str, MockPrincipleCredibility] = field(default_factory=dict)

    def get_or_create(self, principle_id: str) -> MockPrincipleCredibility:
        if principle_id not in self.principles:
            self.principles[principle_id] = MockPrincipleCredibility(principle_id)
        return self.principles[principle_id]

    def effective_weight(self, principle_id: str) -> float:
        if principle_id not in self.principles:
            return 1.0
        return self.principles[principle_id].credibility

    def cite_all(self, principle_ids: tuple[str, ...]) -> None:
        for pid in principle_ids:
            self.get_or_create(pid).cite()

    def apply_reward(self, principle_ids: tuple[str, ...], weight: float = 0.01) -> None:
        for pid in principle_ids:
            self.get_or_create(pid).reward(weight)


class TestSyncFromPrincipleRegistry:
    """Tests for sync_from_principle_registry function."""

    def test_discredited_principle_capped(self) -> None:
        """Discredited principles have draw strength capped."""
        derivation = Derivation(
            agent_name="Test",
            tier=DerivationTier.FUNCTOR,
            principle_draws=(
                PrincipleDraw(
                    principle="BadPrinciple",
                    draw_strength=0.9,
                    evidence_type=EvidenceType.EMPIRICAL,
                ),
            ),
        )

        registry = MockPrincipleRegistry()
        registry.principles["BadPrinciple"] = MockPrincipleCredibility(
            "BadPrinciple",
            credibility=0.0,  # Discredited
        )

        updated = sync_from_principle_registry(derivation, registry)

        assert updated.principle_draws[0].draw_strength <= 0.3

    def test_predictive_principle_boosted(self) -> None:
        """Predictive principles get a small boost."""
        derivation = Derivation(
            agent_name="Test",
            tier=DerivationTier.FUNCTOR,
            principle_draws=(
                PrincipleDraw(
                    principle="GoodPrinciple",
                    draw_strength=0.8,
                    evidence_type=EvidenceType.EMPIRICAL,
                ),
            ),
        )

        registry = MockPrincipleRegistry()
        good = MockPrincipleCredibility("GoodPrinciple", credibility=1.0, times_cited=10)
        registry.principles["GoodPrinciple"] = good

        updated = sync_from_principle_registry(derivation, registry)

        # 10% boost: 0.8 * 1.1 = 0.88
        assert updated.principle_draws[0].draw_strength >= 0.85

    def test_normal_credibility_modulation(self) -> None:
        """Normal principles are modulated by credibility."""
        derivation = Derivation(
            agent_name="Test",
            tier=DerivationTier.FUNCTOR,
            principle_draws=(
                PrincipleDraw(
                    principle="NormalPrinciple",
                    draw_strength=0.8,
                    evidence_type=EvidenceType.EMPIRICAL,
                ),
            ),
        )

        registry = MockPrincipleRegistry()
        registry.principles["NormalPrinciple"] = MockPrincipleCredibility(
            "NormalPrinciple", credibility=0.5
        )

        updated = sync_from_principle_registry(derivation, registry)

        # 0.8 * 0.5 = 0.4
        assert abs(updated.principle_draws[0].draw_strength - 0.4) < 0.01


class TestSyncToPrincipleRegistry:
    """Tests for sync_to_principle_registry function."""

    def test_cites_all_principles(self) -> None:
        """All principles in derivation are cited."""
        derivation = Derivation(
            agent_name="Test",
            tier=DerivationTier.FUNCTOR,
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.8,
                    evidence_type=EvidenceType.EMPIRICAL,
                ),
                PrincipleDraw(
                    principle="Tasteful",
                    draw_strength=0.7,
                    evidence_type=EvidenceType.EMPIRICAL,
                ),
            ),
        )

        registry = MockPrincipleRegistry()

        sync_to_principle_registry(derivation, registry, success=True)

        assert registry.principles["Composable"].times_cited == 1
        assert registry.principles["Tasteful"].times_cited == 1

    def test_success_rewards_principles(self) -> None:
        """Success increases principle credibility."""
        derivation = Derivation(
            agent_name="Test",
            tier=DerivationTier.FUNCTOR,
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.8,
                    evidence_type=EvidenceType.EMPIRICAL,
                ),
            ),
        )

        registry = MockPrincipleRegistry()
        registry.principles["Composable"] = MockPrincipleCredibility("Composable", credibility=0.9)

        sync_to_principle_registry(derivation, registry, success=True)

        # Should increase slightly
        assert registry.principles["Composable"].credibility > 0.9


# =============================================================================
# Test: Lemma Strengthens Derivation
# =============================================================================


class TestLemmaStrengthensDerivation:
    """Tests for lemma_strengthens_derivation function."""

    @pytest.fixture
    def registry(self) -> DerivationRegistry:
        """Create a fresh registry with a derived agent."""
        reg = DerivationRegistry()
        reg.register(
            agent_name="TestAgent",
            derives_from=("Compose",),
            principle_draws=(),
            tier=DerivationTier.FUNCTOR,
        )
        return reg

    @pytest.mark.asyncio
    async def test_adds_categorical_draw(self, registry: DerivationRegistry) -> None:
        """Verified lemma adds categorical principle draw."""
        before = registry.get("TestAgent")
        assert before is not None
        assert len(before.principle_draws) == 0

        await lemma_strengthens_derivation(
            registry,
            lemma_id="lemma_001",
            lemma_statement="forall x. id(x) = x (identity law)",
            agent_name="TestAgent",
        )

        after = registry.get("TestAgent")
        assert after is not None
        assert len(after.principle_draws) == 1
        assert after.principle_draws[0].evidence_type == EvidenceType.CATEGORICAL
        assert after.principle_draws[0].draw_strength == 1.0

    @pytest.mark.asyncio
    async def test_categorical_replaces_empirical(self, registry: DerivationRegistry) -> None:
        """Categorical evidence replaces empirical for same principle."""
        # First add empirical evidence
        existing = registry.get("TestAgent")
        updated = existing.with_principle_draws(
            (
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.7,
                    evidence_type=EvidenceType.EMPIRICAL,
                ),
            )
        )
        registry._derivations["TestAgent"] = updated

        # Now add categorical
        await lemma_strengthens_derivation(
            registry,
            lemma_id="lemma_002",
            lemma_statement="associativity proof",
            agent_name="TestAgent",
        )

        after = registry.get("TestAgent")
        composable = next(d for d in after.principle_draws if d.principle == "Composable")
        assert composable.evidence_type == EvidenceType.CATEGORICAL
        assert composable.draw_strength == 1.0

    @pytest.mark.asyncio
    async def test_unknown_lemma_no_op(self, registry: DerivationRegistry) -> None:
        """Unknown lemma type doesn't add evidence."""
        before = registry.get("TestAgent")
        assert len(before.principle_draws) == 0

        await lemma_strengthens_derivation(
            registry,
            lemma_id="lemma_003",
            lemma_statement="some random statement about foobar",
            agent_name="TestAgent",
        )

        after = registry.get("TestAgent")
        assert len(after.principle_draws) == 0


class TestClassifyLemmaToPrinciple:
    """Tests for _classify_lemma_to_principle helper."""

    def test_composable_lemmas(self) -> None:
        """Composition-related lemmas map to Composable."""
        assert _classify_lemma_to_principle("associativity law") == "Composable"
        assert _classify_lemma_to_principle("identity morphism") == "Composable"
        assert _classify_lemma_to_principle("composition is closed") == "Composable"

    def test_heterarchical_lemmas(self) -> None:
        """Mode-related lemmas map to Heterarchical."""
        assert _classify_lemma_to_principle("heterarchy property") == "Heterarchical"
        assert _classify_lemma_to_principle("mode switching preserves state") == "Heterarchical"
        assert _classify_lemma_to_principle("flux invariant") == "Heterarchical"

    def test_generative_lemmas(self) -> None:
        """Generation-related lemmas map to Generative."""
        assert _classify_lemma_to_principle("generative compression") == "Generative"
        assert _classify_lemma_to_principle("derivation is sound") == "Generative"

    def test_unknown_lemmas(self) -> None:
        """Unknown lemma types return None."""
        assert _classify_lemma_to_principle("foo bar baz") is None
        assert _classify_lemma_to_principle("random statement") is None
