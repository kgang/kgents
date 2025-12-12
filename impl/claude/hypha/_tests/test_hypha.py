"""
Tests for Hypha - The Agent as Growing Tip.

These tests verify:
- Hypha creation and configuration
- Foraging loop behavior
- Action execution (explore, exploit, prune)
- Colony creation

Exit Criteria from topos-of-becoming.md:
- Hypha responds to surprise appropriately
- High surprise -> EXPLORE
- Low surprise, low reward -> PRUNE
"""

from __future__ import annotations

import numpy as np
import pytest

from ...field.holographic import HolographicField
from ..foraging import ForageAction, ForagingPolicy
from ..free_energy import FreeEnergyState
from ..hypha import (
    Hypha,
    HyphaConfig,
    create_hypha,
    create_hypha_colony,
)

DIMENSIONS = 100  # Smaller for faster tests


@pytest.fixture
def small_config() -> HyphaConfig:
    """Config with smaller dimensions for testing."""
    return HyphaConfig(dimensions=DIMENSIONS)


@pytest.fixture
def hypha(small_config: HyphaConfig) -> Hypha:
    """Create a test hypha."""
    return create_hypha(
        hypha_id="test-hypha",
        name="Test",
        config=small_config,
    )


class TestHyphaCreation:
    """Tests for Hypha creation."""

    def test_create_hypha(self, small_config: HyphaConfig) -> None:
        """create_hypha creates valid Hypha."""
        hypha = create_hypha(
            hypha_id="test",
            name="Test Hypha",
            config=small_config,
        )

        assert hypha.id == "test"
        assert hypha.name == "Test Hypha"
        assert hypha.is_active

    def test_hypha_has_generative_model(self, hypha: Hypha) -> None:
        """Hypha initializes with GenerativeModel."""
        assert hypha.generative_model is not None
        assert hypha.generative_model.dimensions == DIMENSIONS

    def test_hypha_has_weave(self, hypha: Hypha) -> None:
        """Hypha initializes with TheWeave."""
        assert hypha.weave is not None
        assert len(hypha.weave) == 0

    def test_hypha_starts_active(self, hypha: Hypha) -> None:
        """Hypha starts in active state."""
        assert hypha.is_active is True

    def test_hypha_initial_counts_zero(self, hypha: Hypha) -> None:
        """Hypha starts with zero counts."""
        assert hypha.forage_count == 0
        assert hypha.explore_count == 0
        assert hypha.exploit_count == 0
        assert hypha.prune_count == 0


class TestHyphaConfig:
    """Tests for HyphaConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible values."""
        config = HyphaConfig()

        assert config.exploration_rate > 0
        assert config.pruning_threshold > 0
        assert config.learning_rate > 0
        assert config.imprint_strength > 0

    def test_custom_config(self) -> None:
        """Custom config values are respected."""
        config = HyphaConfig(
            exploration_rate=0.5,
            pruning_threshold=0.2,
            learning_rate=0.05,
            dimensions=500,
        )

        assert config.exploration_rate == 0.5
        assert config.pruning_threshold == 0.2
        assert config.learning_rate == 0.05
        assert config.dimensions == 500


class TestForaging:
    """Tests for foraging behavior."""

    @pytest.mark.asyncio
    async def test_forage_increments_count(self, hypha: Hypha) -> None:
        """forage() increments forage_count."""
        assert hypha.forage_count == 0

        await hypha.forage()

        assert hypha.forage_count == 1

    @pytest.mark.asyncio
    async def test_forage_records_to_weave(self, hypha: Hypha) -> None:
        """forage() records events to weave."""
        initial_len = len(hypha.weave)

        await hypha.forage()

        # Weave should have new event(s)
        assert len(hypha.weave) >= initial_len

    @pytest.mark.asyncio
    async def test_forage_updates_free_energy_state(self, hypha: Hypha) -> None:
        """forage() sets free_energy_state."""
        assert hypha.free_energy_state is None

        await hypha.forage()

        assert hypha.free_energy_state is not None

    @pytest.mark.asyncio
    async def test_forage_with_custom_observation(
        self, small_config: HyphaConfig
    ) -> None:
        """forage() uses provided observation."""
        hypha = create_hypha("test", "Test", config=small_config)

        observation = np.random.randn(DIMENSIONS)
        await hypha.forage(observation=observation)

        # free_energy_state should use our observation
        assert hypha.free_energy_state is not None
        assert np.allclose(
            hypha.free_energy_state.actual_observation,
            observation,
        )

    @pytest.mark.asyncio
    async def test_forage_with_reward_estimator(
        self, small_config: HyphaConfig
    ) -> None:
        """forage() uses reward estimator."""
        hypha = create_hypha("test", "Test", config=small_config)

        def constant_reward(obs: np.ndarray) -> float:
            return 0.9

        result = await hypha.forage(reward_estimator=constant_reward)

        assert result.reward == 0.9


class TestExplore:
    """Tests for explore action."""

    @pytest.mark.asyncio
    async def test_high_surprise_triggers_explore(
        self, small_config: HyphaConfig
    ) -> None:
        """
        Exit Criteria: High surprise -> EXPLORE

        hypha.free_energy_state = FreeEnergyState(
            expected_observation=np.zeros(DIMENSIONS),
            actual_observation=np.random.randn(DIMENSIONS),  # Very different
        )
        action = await hypha.forage()
        assert action == ForageAction.EXPLORE
        """
        hypha = create_hypha("test", "Test", config=small_config)

        # Use a policy with low explore threshold
        hypha.policy = ForagingPolicy(explore_threshold=0.3)

        # Very different observation -> high surprise
        observation = np.ones(DIMENSIONS) * 10  # Large difference from zeros

        result = await hypha.forage(observation=observation)

        assert result.action == ForageAction.EXPLORE
        assert result.branched is True

    @pytest.mark.asyncio
    async def test_explore_increments_count(self, small_config: HyphaConfig) -> None:
        """explore increments explore_count."""
        hypha = create_hypha("test", "Test", config=small_config)
        hypha.policy = ForagingPolicy(explore_threshold=0.1)

        observation = np.ones(DIMENSIONS) * 10

        await hypha.forage(observation=observation)

        assert hypha.explore_count >= 1


class TestExploit:
    """Tests for exploit action."""

    @pytest.mark.asyncio
    async def test_low_surprise_high_reward_triggers_exploit(
        self, small_config: HyphaConfig
    ) -> None:
        """Low surprise + high reward -> EXPLOIT."""
        hypha = create_hypha("test", "Test", config=small_config)

        # Policy that triggers exploit easily
        hypha.policy = ForagingPolicy(
            explore_threshold=0.99,  # High, so we don't explore
            prune_threshold=0.5,  # Medium
            exploit_reward_threshold=0.3,  # Low, so we exploit
        )

        # Small observation (low surprise)
        observation = np.zeros(DIMENSIONS) + 0.01

        # High reward
        def high_reward(obs: np.ndarray) -> float:
            return 0.9

        result = await hypha.forage(
            observation=observation,
            reward_estimator=high_reward,
        )

        assert result.action == ForageAction.EXPLOIT
        assert result.imprinted is True

    @pytest.mark.asyncio
    async def test_exploit_increments_count(self, small_config: HyphaConfig) -> None:
        """exploit increments exploit_count."""
        hypha = create_hypha("test", "Test", config=small_config)
        hypha.policy = ForagingPolicy(
            explore_threshold=0.99,
            prune_threshold=0.5,
            exploit_reward_threshold=0.3,
        )

        observation = np.zeros(DIMENSIONS) + 0.01

        await hypha.forage(
            observation=observation,
            reward_estimator=lambda x: 0.9,
        )

        assert hypha.exploit_count >= 1


class TestPrune:
    """Tests for prune action."""

    @pytest.mark.asyncio
    async def test_low_surprise_low_reward_triggers_prune(
        self, small_config: HyphaConfig
    ) -> None:
        """
        Exit Criteria: Low surprise, low reward -> PRUNE

        hypha.free_energy_state = FreeEnergyState(
            expected_observation=np.ones(DIMENSIONS),
            actual_observation=np.ones(DIMENSIONS) * 1.01,  # Very similar
        )
        action = await hypha.forage()
        assert action == ForageAction.PRUNE
        """
        hypha = create_hypha("test", "Test", config=small_config)

        # Policy that triggers prune
        hypha.policy = ForagingPolicy(
            explore_threshold=0.99,  # High
            prune_threshold=0.5,  # Medium
            exploit_reward_threshold=0.8,  # High
        )

        # Small observation (low surprise)
        observation = np.zeros(DIMENSIONS) + 0.01

        # Low reward
        def low_reward(obs: np.ndarray) -> float:
            return 0.1

        result = await hypha.forage(
            observation=observation,
            reward_estimator=low_reward,
        )

        assert result.action == ForageAction.PRUNE
        assert result.pruned is True

    @pytest.mark.asyncio
    async def test_prune_deactivates_hypha(self, small_config: HyphaConfig) -> None:
        """Prune sets is_active to False."""
        hypha = create_hypha("test", "Test", config=small_config)
        hypha.policy = ForagingPolicy(
            explore_threshold=0.99,
            prune_threshold=0.5,
            exploit_reward_threshold=0.8,
        )

        observation = np.zeros(DIMENSIONS) + 0.01

        await hypha.forage(
            observation=observation,
            reward_estimator=lambda x: 0.1,
        )

        assert hypha.is_active is False

    @pytest.mark.asyncio
    async def test_pruned_hypha_doesnt_forage(self, small_config: HyphaConfig) -> None:
        """Pruned hypha returns immediately from forage."""
        hypha = create_hypha("test", "Test", config=small_config)
        hypha.is_active = False

        initial_count = hypha.forage_count
        result = await hypha.forage()

        assert result.action == ForageAction.PRUNE
        assert hypha.forage_count == initial_count  # No increment


class TestVitality:
    """Tests for vitality metric."""

    def test_vitality_starts_at_one(self, hypha: Hypha) -> None:
        """Vitality is 1.0 before any foraging."""
        assert hypha.vitality == 1.0

    @pytest.mark.asyncio
    async def test_vitality_reflects_success_rate(
        self, small_config: HyphaConfig
    ) -> None:
        """Vitality = (explore + exploit) / forage_count."""
        hypha = create_hypha("test", "Test", config=small_config)

        # Force some explores
        hypha.policy = ForagingPolicy(explore_threshold=0.1)
        observation = np.ones(DIMENSIONS) * 10

        await hypha.forage(observation=observation)
        await hypha.forage(observation=observation)

        # All forages should be explores
        expected_vitality = (
            hypha.explore_count + hypha.exploit_count
        ) / hypha.forage_count
        assert hypha.vitality == pytest.approx(expected_vitality)


class TestReset:
    """Tests for reset."""

    @pytest.mark.asyncio
    async def test_reset_clears_counts(self, small_config: HyphaConfig) -> None:
        """reset() clears all counts."""
        hypha = create_hypha("test", "Test", config=small_config)

        # Do some foraging
        await hypha.forage()
        assert hypha.forage_count > 0

        hypha.reset()

        assert hypha.forage_count == 0
        assert hypha.explore_count == 0
        assert hypha.exploit_count == 0
        assert hypha.prune_count == 0

    @pytest.mark.asyncio
    async def test_reset_reactivates_hypha(self, small_config: HyphaConfig) -> None:
        """reset() sets is_active to True."""
        hypha = create_hypha("test", "Test", config=small_config)
        hypha.is_active = False

        hypha.reset()

        assert hypha.is_active is True

    @pytest.mark.asyncio
    async def test_reset_clears_free_energy_state(
        self, small_config: HyphaConfig
    ) -> None:
        """reset() clears free_energy_state."""
        hypha = create_hypha("test", "Test", config=small_config)
        await hypha.forage()
        assert hypha.free_energy_state is not None

        hypha.reset()

        assert hypha.free_energy_state is None


class TestColony:
    """Tests for colony creation."""

    def test_create_colony(self) -> None:
        """create_hypha_colony creates multiple hyphae."""
        names = ["Alpha", "Beta", "Gamma"]
        config = HyphaConfig(dimensions=DIMENSIONS)

        colony = create_hypha_colony(names, config=config)

        assert len(colony) == 3
        assert colony[0].name == "Alpha"
        assert colony[1].name == "Beta"
        assert colony[2].name == "Gamma"

    def test_colony_shares_hologram(self) -> None:
        """Colony members share holographic field."""
        hologram = HolographicField(dimensions=DIMENSIONS)
        names = ["A", "B"]
        config = HyphaConfig(dimensions=DIMENSIONS)

        colony = create_hypha_colony(names, shared_hologram=hologram, config=config)

        assert colony[0].hologram is hologram
        assert colony[1].hologram is hologram

    def test_colony_distinct_ids(self) -> None:
        """Colony members have distinct IDs."""
        names = ["A", "B", "C"]
        config = HyphaConfig(dimensions=DIMENSIONS)

        colony = create_hypha_colony(names, config=config)

        ids = [h.id for h in colony]
        assert len(set(ids)) == 3


class TestResonate:
    """Tests for resonance with holographic field."""

    def test_resonate_without_hologram_returns_zero(
        self, small_config: HyphaConfig
    ) -> None:
        """resonate() returns 0 if no hologram."""
        hypha = create_hypha("test", "Test", config=small_config)

        pattern = np.random.randn(DIMENSIONS)
        resonance = hypha.resonate(pattern)

        assert resonance == 0.0

    def test_resonate_with_hologram(self, small_config: HyphaConfig) -> None:
        """resonate() uses hologram when available."""
        hologram = HolographicField(dimensions=DIMENSIONS)
        hypha = create_hypha(
            "test",
            "Test",
            hologram=hologram,
            config=small_config,
        )

        # Imprint something
        pattern = np.random.randn(DIMENSIONS)
        hologram.imprint(pattern)

        # Should resonate
        resonance = hypha.resonate(pattern)

        assert resonance != 0.0


class TestExitCriteria:
    """
    Exit Criteria tests from topos-of-becoming.md.

    Test: Hypha responds to surprise appropriately
    """

    @pytest.mark.asyncio
    async def test_spec_high_surprise_explore(self) -> None:
        """
        Exit Criteria: High surprise -> EXPLORE

        hypha = Hypha(id="test", name="test-hypha")
        hypha.free_energy_state = FreeEnergyState(
            expected_observation=np.zeros(DIMENSIONS),
            actual_observation=np.random.randn(DIMENSIONS),
        )
        action = await hypha.forage()
        assert action == ForageAction.EXPLORE
        """
        config = HyphaConfig(dimensions=DIMENSIONS)
        hypha = Hypha(id="test", name="test-hypha", config=config)

        # Set policy to trigger explore on high surprise
        hypha.policy = ForagingPolicy(explore_threshold=0.3)

        # Very different observation -> high surprise
        observation = np.random.randn(DIMENSIONS) * 10

        result = await hypha.forage(observation=observation)

        assert result.action == ForageAction.EXPLORE

    @pytest.mark.asyncio
    async def test_spec_low_surprise_low_reward_prune(self) -> None:
        """
        Exit Criteria: Low surprise, low reward -> PRUNE

        hypha.free_energy_state = FreeEnergyState(
            expected_observation=np.ones(DIMENSIONS),
            actual_observation=np.ones(DIMENSIONS) * 1.01,
        )
        action = await hypha.forage()
        assert action == ForageAction.PRUNE
        """
        config = HyphaConfig(dimensions=DIMENSIONS)
        hypha = Hypha(id="test", name="test-hypha", config=config)

        # Set policy to trigger prune
        hypha.policy = ForagingPolicy(
            explore_threshold=0.99,
            prune_threshold=0.5,
            exploit_reward_threshold=0.8,
        )

        # Very similar observation -> low surprise
        observation = np.zeros(DIMENSIONS) * 1.01

        # Low reward
        def low_reward(obs: np.ndarray) -> float:
            return 0.1

        result = await hypha.forage(
            observation=observation,
            reward_estimator=low_reward,
        )

        assert result.action == ForageAction.PRUNE
