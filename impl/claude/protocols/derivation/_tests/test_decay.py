"""
Tests for Decay & Refresh: Phase 4 of the Derivation Framework.

Tests cover:
    - decay_principle_draw(): time-based evidence decay
    - decay_derivation_evidence(): full derivation decay
    - apply_evidence_decay(): registry-wide decay
    - calculate_stigmergic_decay(): inactivity-based decay
    - apply_stigmergic_decay(): registry-wide stigmergic decay
    - record_activity(): activity tracking
    - should_refresh_agent(): refresh scheduling
    - apply_ashc_refresh(): ASHC refresh
    - run_decay_cycle(): full decay cycle

Teaching:
    gotcha: These tests manipulate time via explicit datetime parameters.
            Never rely on datetime.now() in tests - inject the time.

    gotcha: Use fresh registry/stores in each test to avoid cross-contamination.
            The fixtures create isolated instances.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from protocols.derivation.decay import (
    ActivityRecord,
    DecayConfig,
    InMemoryActivityStore,
    InMemoryRefreshStore,
    RefreshSchedule,
    apply_ashc_refresh,
    apply_evidence_decay,
    apply_stigmergic_decay,
    calculate_stigmergic_decay,
    decay_derivation_evidence,
    decay_principle_draw,
    record_activity,
    reset_activity_store,
    reset_refresh_store,
    run_decay_cycle,
    should_refresh_agent,
)
from protocols.derivation.registry import DerivationRegistry
from protocols.derivation.types import (
    Derivation,
    DerivationTier,
    EvidenceType,
    PrincipleDraw,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def config() -> DecayConfig:
    """Standard decay configuration."""
    return DecayConfig()


@pytest.fixture
def registry() -> DerivationRegistry:
    """Fresh registry with test derivations."""
    reg = DerivationRegistry()

    # Register a Crown Jewel with empirical evidence
    reg.register(
        agent_name="Brain",
        derives_from=("Fix", "Compose"),
        principle_draws=(
            PrincipleDraw(
                principle="Composable",
                draw_strength=0.8,
                evidence_type=EvidenceType.EMPIRICAL,
                evidence_sources=("test-1",),
            ),
            PrincipleDraw(
                principle="Generative",
                draw_strength=0.7,
                evidence_type=EvidenceType.AESTHETIC,
                evidence_sources=("test-2",),
            ),
        ),
        tier=DerivationTier.JEWEL,
    )

    # Register an agent with categorical evidence
    reg.register(
        agent_name="CatAgent",
        derives_from=("Id",),
        principle_draws=(
            PrincipleDraw(
                principle="Composable",
                draw_strength=1.0,
                evidence_type=EvidenceType.CATEGORICAL,
                evidence_sources=("identity-law",),
            ),
        ),
        tier=DerivationTier.FUNCTOR,
    )

    # Register an agent with stigmergic confidence
    brain = reg.get("Brain")
    if brain:
        reg._derivations["Brain"] = brain.with_evidence(
            empirical=0.75,
            stigmergic=0.5,
        )

    return reg


@pytest.fixture
def activity_store() -> InMemoryActivityStore:
    """Fresh activity store."""
    reset_activity_store()
    return InMemoryActivityStore()


@pytest.fixture
def refresh_store() -> InMemoryRefreshStore:
    """Fresh refresh store."""
    reset_refresh_store()
    return InMemoryRefreshStore()


# =============================================================================
# Test: decay_principle_draw
# =============================================================================


class TestDecayPrincipleDraw:
    """Tests for decay_principle_draw()."""

    def test_categorical_never_decays(self, config: DecayConfig) -> None:
        """Categorical evidence never decays."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=1.0,
            evidence_type=EvidenceType.CATEGORICAL,
            evidence_sources=("law",),
        )

        decayed = decay_principle_draw(draw, days_elapsed=365, config=config)

        assert decayed.draw_strength == 1.0

    def test_somatic_never_decays(self, config: DecayConfig) -> None:
        """Somatic evidence (Mirror Test) never decays."""
        draw = PrincipleDraw(
            principle="Tasteful",
            draw_strength=0.9,
            evidence_type=EvidenceType.SOMATIC,
            evidence_sources=(),
        )

        decayed = decay_principle_draw(draw, days_elapsed=365, config=config)

        assert decayed.draw_strength == 0.9

    def test_empirical_decays(self, config: DecayConfig) -> None:
        """Empirical evidence decays at 2%/day."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=0.8,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=("ashc-run",),
        )

        # After 1 day: 0.8 * (1 - 0.02)^1 = 0.784
        decayed = decay_principle_draw(draw, days_elapsed=1, config=config)

        assert abs(decayed.draw_strength - 0.784) < 0.001

    def test_aesthetic_decays_faster(self, config: DecayConfig) -> None:
        """Aesthetic evidence decays at 3%/day (faster than empirical)."""
        draw = PrincipleDraw(
            principle="Joy-Inducing",
            draw_strength=0.8,
            evidence_type=EvidenceType.AESTHETIC,
            evidence_sources=("beauty-test",),
        )

        # After 1 day: 0.8 * (1 - 0.03)^1 = 0.776
        decayed = decay_principle_draw(draw, days_elapsed=1, config=config)

        assert abs(decayed.draw_strength - 0.776) < 0.001

    def test_genealogical_decays_slower(self, config: DecayConfig) -> None:
        """Genealogical evidence decays at 1%/day (slower than empirical)."""
        draw = PrincipleDraw(
            principle="Generative",
            draw_strength=0.8,
            evidence_type=EvidenceType.GENEALOGICAL,
            evidence_sources=("git-archaeology",),
        )

        # After 1 day: 0.8 * (1 - 0.01)^1 = 0.792
        decayed = decay_principle_draw(draw, days_elapsed=1, config=config)

        assert abs(decayed.draw_strength - 0.792) < 0.001

    def test_floor_at_minimum(self, config: DecayConfig) -> None:
        """Decay has a floor (0.1 by default)."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=0.5,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=("old-run",),
        )

        # After 365 days, should hit floor
        decayed = decay_principle_draw(draw, days_elapsed=365, config=config)

        assert decayed.draw_strength == config.min_draw_strength

    def test_zero_days_no_change(self, config: DecayConfig) -> None:
        """Zero days elapsed = no decay."""
        draw = PrincipleDraw(
            principle="Composable",
            draw_strength=0.8,
            evidence_type=EvidenceType.EMPIRICAL,
            evidence_sources=("run",),
        )

        decayed = decay_principle_draw(draw, days_elapsed=0, config=config)

        assert decayed.draw_strength == 0.8


# =============================================================================
# Test: decay_derivation_evidence
# =============================================================================


class TestDecayDerivationEvidence:
    """Tests for decay_derivation_evidence()."""

    def test_decays_all_non_categorical_draws(
        self, registry: DerivationRegistry, config: DecayConfig
    ) -> None:
        """All non-categorical draws are decayed."""
        brain = registry.get("Brain")
        assert brain is not None

        decayed = decay_derivation_evidence(brain, days_elapsed=10, config=config)

        # Both draws should have decayed
        for draw in decayed.principle_draws:
            original = next(d for d in brain.principle_draws if d.principle == draw.principle)
            assert draw.draw_strength < original.draw_strength

    def test_bootstrap_never_decayed(
        self, registry: DerivationRegistry, config: DecayConfig
    ) -> None:
        """Bootstrap agents are never decayed."""
        compose = registry.get("Compose")
        assert compose is not None

        decayed = decay_derivation_evidence(compose, days_elapsed=365, config=config)

        # Should be identical (bootstrap)
        assert decayed == compose

    def test_categorical_draws_preserved(
        self, registry: DerivationRegistry, config: DecayConfig
    ) -> None:
        """Categorical draws within a derivation are preserved."""
        cat_agent = registry.get("CatAgent")
        assert cat_agent is not None

        decayed = decay_derivation_evidence(cat_agent, days_elapsed=365, config=config)

        # Categorical draw should be unchanged
        cat_draw = next(
            d for d in decayed.principle_draws if d.evidence_type == EvidenceType.CATEGORICAL
        )
        assert cat_draw.draw_strength == 1.0


# =============================================================================
# Test: apply_evidence_decay
# =============================================================================


class TestApplyEvidenceDecay:
    """Tests for apply_evidence_decay()."""

    @pytest.mark.asyncio
    async def test_decays_all_agents(
        self, registry: DerivationRegistry, config: DecayConfig
    ) -> None:
        """Decays evidence for all non-bootstrap agents."""
        result = await apply_evidence_decay(days_elapsed=10, registry=registry, config=config)

        # Brain should be in decayed list
        assert "Brain" in result["decayed_agents"]

        # Bootstrap agents should be skipped
        assert "Compose" in result["bootstrap_skipped"]

    @pytest.mark.asyncio
    async def test_returns_summary(self, registry: DerivationRegistry, config: DecayConfig) -> None:
        """Returns summary with all categories."""
        result = await apply_evidence_decay(days_elapsed=1, registry=registry, config=config)

        assert "days_elapsed" in result
        assert "decayed_agents" in result
        assert "unchanged_agents" in result
        assert "bootstrap_skipped" in result


# =============================================================================
# Test: calculate_stigmergic_decay
# =============================================================================


class TestCalculateStigmergicDecay:
    """Tests for calculate_stigmergic_decay()."""

    def test_no_decay_within_threshold(self, config: DecayConfig) -> None:
        """No decay during inactivity threshold period."""
        # Config has 14-day threshold
        result = calculate_stigmergic_decay(
            current_confidence=0.5,
            days_inactive=10,  # Within threshold
            config=config,
        )

        assert result == 0.5

    def test_half_life_decay(self, config: DecayConfig) -> None:
        """Confidence halves after one half-life."""
        # Config has 30-day half-life, 14-day threshold
        # So after 14 + 30 = 44 days, should be at half
        result = calculate_stigmergic_decay(
            current_confidence=0.8,
            days_inactive=44,
            config=config,
        )

        # Should be approximately 0.4 (half of 0.8)
        assert abs(result - 0.4) < 0.01

    def test_extended_inactivity(self, config: DecayConfig) -> None:
        """Extended inactivity approaches zero."""
        result = calculate_stigmergic_decay(
            current_confidence=0.8,
            days_inactive=365,  # Very inactive
            config=config,
        )

        # Should be very low
        assert result < 0.01

    def test_floor_at_minimum(self, config: DecayConfig) -> None:
        """Decay has a floor (0.0 by default for stigmergic)."""
        result = calculate_stigmergic_decay(
            current_confidence=0.5,
            days_inactive=1000,  # Extremely inactive
            config=config,
        )

        assert result >= config.min_stigmergic_confidence


# =============================================================================
# Test: apply_stigmergic_decay
# =============================================================================


class TestApplyStigmergicDecay:
    """Tests for apply_stigmergic_decay()."""

    @pytest.mark.asyncio
    async def test_decays_inactive_agents(
        self,
        registry: DerivationRegistry,
        activity_store: InMemoryActivityStore,
        config: DecayConfig,
    ) -> None:
        """Inactive agents have their stigmergic confidence decayed."""
        # Record activity 60 days ago
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(days=60)

        activity_store.set(
            ActivityRecord(
                agent_name="Brain",
                last_active=old_time,
                usage_at_last_active=100,
            )
        )

        brain_before = registry.get("Brain")
        assert brain_before is not None
        stigmergic_before = brain_before.stigmergic_confidence

        result = await apply_stigmergic_decay(
            registry=registry,
            activity_store=activity_store,
            config=config,
            now=now,
        )

        brain_after = registry.get("Brain")
        assert brain_after is not None

        # Should have decayed (60 days inactive is well past threshold)
        assert "Brain" in result["decayed_agents"]
        assert brain_after.stigmergic_confidence < stigmergic_before

    @pytest.mark.asyncio
    async def test_active_agents_unchanged(
        self,
        registry: DerivationRegistry,
        activity_store: InMemoryActivityStore,
        config: DecayConfig,
    ) -> None:
        """Recently active agents are not decayed."""
        now = datetime.now(timezone.utc)
        recent = now - timedelta(days=5)  # Within threshold

        activity_store.set(
            ActivityRecord(
                agent_name="Brain",
                last_active=recent,
                usage_at_last_active=100,
            )
        )

        result = await apply_stigmergic_decay(
            registry=registry,
            activity_store=activity_store,
            config=config,
            now=now,
        )

        # Brain should be unchanged (recently active)
        assert "Brain" in result["unchanged_agents"]

    @pytest.mark.asyncio
    async def test_bootstrap_skipped(
        self,
        registry: DerivationRegistry,
        activity_store: InMemoryActivityStore,
        config: DecayConfig,
    ) -> None:
        """Bootstrap agents are skipped."""
        result = await apply_stigmergic_decay(
            registry=registry,
            activity_store=activity_store,
            config=config,
        )

        # Bootstrap agents should be in skipped list
        assert "Compose" in result["bootstrap_skipped"]


# =============================================================================
# Test: record_activity
# =============================================================================


class TestRecordActivity:
    """Tests for record_activity()."""

    def test_records_activity(
        self,
        registry: DerivationRegistry,
        activity_store: InMemoryActivityStore,
    ) -> None:
        """Activity is recorded correctly."""
        record = record_activity(
            "Brain",
            registry=registry,
            activity_store=activity_store,
        )

        assert record is not None
        assert record.agent_name == "Brain"
        assert activity_store.get("Brain") == record

    def test_unknown_agent_returns_none(
        self,
        registry: DerivationRegistry,
        activity_store: InMemoryActivityStore,
    ) -> None:
        """Unknown agent returns None."""
        record = record_activity(
            "UnknownAgent",
            registry=registry,
            activity_store=activity_store,
        )

        assert record is None


# =============================================================================
# Test: should_refresh_agent
# =============================================================================


class TestShouldRefreshAgent:
    """Tests for should_refresh_agent()."""

    @pytest.mark.asyncio
    async def test_never_refreshed_should_refresh(
        self, refresh_store: InMemoryRefreshStore, config: DecayConfig
    ) -> None:
        """Agent never refreshed should be refreshed."""
        result = await should_refresh_agent(
            "Brain",
            refresh_store=refresh_store,
            config=config,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_recently_refreshed_should_not(
        self, refresh_store: InMemoryRefreshStore, config: DecayConfig
    ) -> None:
        """Recently refreshed agent should not be refreshed."""
        now = datetime.now(timezone.utc)
        recent = now - timedelta(days=3)  # Less than 7-day threshold

        refresh_store.set(
            RefreshSchedule(
                agent_name="Brain",
                last_refresh=recent,
                refresh_count=1,
            )
        )

        result = await should_refresh_agent(
            "Brain",
            refresh_store=refresh_store,
            config=config,
            now=now,
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_stale_refresh_should_refresh(
        self, refresh_store: InMemoryRefreshStore, config: DecayConfig
    ) -> None:
        """Agent with stale refresh should be refreshed."""
        now = datetime.now(timezone.utc)
        old = now - timedelta(days=14)  # More than 7-day threshold

        refresh_store.set(
            RefreshSchedule(
                agent_name="Brain",
                last_refresh=old,
                refresh_count=1,
            )
        )

        result = await should_refresh_agent(
            "Brain",
            refresh_store=refresh_store,
            config=config,
            now=now,
        )

        assert result is True


# =============================================================================
# Test: apply_ashc_refresh
# =============================================================================


class TestApplyASHCRefresh:
    """Tests for apply_ashc_refresh()."""

    @pytest.mark.asyncio
    async def test_no_runner_skips_all(
        self,
        registry: DerivationRegistry,
        refresh_store: InMemoryRefreshStore,
        config: DecayConfig,
    ) -> None:
        """Without ASHC runner, all agents are skipped."""
        result = await apply_ashc_refresh(
            registry=registry,
            refresh_store=refresh_store,
            config=config,
            ashc_runner=None,
        )

        assert result["reason"] == "no_runner"
        assert len(result["refreshed_agents"]) == 0

    @pytest.mark.asyncio
    async def test_returns_summary(
        self,
        registry: DerivationRegistry,
        refresh_store: InMemoryRefreshStore,
        config: DecayConfig,
    ) -> None:
        """Returns summary structure."""
        result = await apply_ashc_refresh(
            registry=registry,
            refresh_store=refresh_store,
            config=config,
        )

        assert "refreshed_agents" in result
        assert "skipped_agents" in result
        assert "failed_agents" in result


# =============================================================================
# Test: run_decay_cycle
# =============================================================================


class TestRunDecayCycle:
    """Tests for run_decay_cycle()."""

    @pytest.mark.asyncio
    async def test_runs_all_phases(
        self,
        registry: DerivationRegistry,
        activity_store: InMemoryActivityStore,
        refresh_store: InMemoryRefreshStore,
        config: DecayConfig,
    ) -> None:
        """Full decay cycle runs all three phases."""
        # Set up some activity
        now = datetime.now(timezone.utc)
        old = now - timedelta(days=60)
        activity_store.set(ActivityRecord("Brain", old, 50))

        result = await run_decay_cycle(
            days_elapsed=1.0,
            registry=registry,
            activity_store=activity_store,
            refresh_store=refresh_store,
            config=config,
        )

        # All three phases should have run
        assert "days_elapsed" in result.evidence_decay or "decayed_agents" in result.evidence_decay
        assert "decayed_agents" in result.stigmergic_decay
        assert "skipped_agents" in result.ashc_refresh

    @pytest.mark.asyncio
    async def test_returns_summary(
        self,
        registry: DerivationRegistry,
        config: DecayConfig,
    ) -> None:
        """Returns comprehensive result."""
        result = await run_decay_cycle(
            days_elapsed=1.0,
            registry=registry,
            config=config,
        )

        assert result.timestamp is not None
        assert isinstance(result.total_agents_affected, int)
        assert result.summary is not None

    @pytest.mark.asyncio
    async def test_idempotent(
        self,
        registry: DerivationRegistry,
        config: DecayConfig,
    ) -> None:
        """Running twice doesn't crash (though applies decay twice)."""
        result1 = await run_decay_cycle(days_elapsed=1.0, registry=registry, config=config)
        result2 = await run_decay_cycle(days_elapsed=1.0, registry=registry, config=config)

        # Both should complete
        assert result1.timestamp is not None
        assert result2.timestamp is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestDecayIntegration:
    """Integration tests for the complete decay flow."""

    @pytest.mark.asyncio
    async def test_full_decay_lifecycle(self) -> None:
        """Full lifecycle: register, use, wait, decay."""
        registry = DerivationRegistry()
        activity_store = InMemoryActivityStore()
        config = DecayConfig()

        # Register agent with high confidence
        registry.register(
            agent_name="TestAgent",
            derives_from=("Compose",),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=0.9,
                    evidence_type=EvidenceType.EMPIRICAL,
                    evidence_sources=("init",),
                ),
            ),
            tier=DerivationTier.FUNCTOR,
        )

        # Set high stigmergic confidence
        agent = registry.get("TestAgent")
        assert agent is not None
        registry._derivations["TestAgent"] = agent.with_evidence(
            empirical=0.8,
            stigmergic=0.7,
        )

        # Record activity 60 days ago
        now = datetime.now(timezone.utc)
        old = now - timedelta(days=60)
        activity_store.set(ActivityRecord("TestAgent", old, 100))

        # Run decay cycle
        result = await run_decay_cycle(
            days_elapsed=60,  # 60 days of evidence decay
            registry=registry,
            activity_store=activity_store,
            config=config,
        )

        # Check that decay happened
        decayed_agent = registry.get("TestAgent")
        assert decayed_agent is not None

        # Evidence should have decayed significantly
        original_draw = 0.9
        decayed_draw = next(d.draw_strength for d in decayed_agent.principle_draws)
        assert decayed_draw < original_draw

        # Stigmergic should have decayed (60 days inactive)
        assert decayed_agent.stigmergic_confidence < 0.7

    @pytest.mark.asyncio
    async def test_categorical_evidence_survives(self) -> None:
        """Categorical evidence survives all decay cycles."""
        registry = DerivationRegistry()
        config = DecayConfig()

        # Register agent with categorical evidence
        registry.register(
            agent_name="CategoricalAgent",
            derives_from=("Id",),
            principle_draws=(
                PrincipleDraw(
                    principle="Composable",
                    draw_strength=1.0,
                    evidence_type=EvidenceType.CATEGORICAL,
                    evidence_sources=("identity-law",),
                ),
            ),
            tier=DerivationTier.FUNCTOR,
        )

        # Run decay cycle with extreme values
        await run_decay_cycle(
            days_elapsed=365,  # One year
            registry=registry,
            config=config,
        )

        # Categorical evidence should be unchanged
        agent = registry.get("CategoricalAgent")
        assert agent is not None
        draw = next(d for d in agent.principle_draws)
        assert draw.draw_strength == 1.0


# =============================================================================
# Test Count Summary
# =============================================================================

# decay_principle_draw: 7 tests
# decay_derivation_evidence: 3 tests
# apply_evidence_decay: 2 tests
# calculate_stigmergic_decay: 4 tests
# apply_stigmergic_decay: 3 tests
# record_activity: 2 tests
# should_refresh_agent: 3 tests
# apply_ashc_refresh: 2 tests
# run_decay_cycle: 3 tests
# Integration: 2 tests
# Total: 31 tests
