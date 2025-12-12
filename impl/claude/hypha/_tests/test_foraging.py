"""
Tests for Foraging - Action Selection Based on Free Energy.

These tests verify:
- ForageAction enum
- ForagingPolicy action selection
- ForagingResult tracking
"""

from __future__ import annotations

import numpy as np
import pytest

from ..foraging import (
    DEFAULT_POLICY,
    ForageAction,
    ForagingPolicy,
    ForagingResult,
    select_forage_action,
)
from ..free_energy import FreeEnergyState

DIMENSIONS = 100  # Smaller for faster tests


def make_state(surprise_level: float) -> FreeEnergyState:
    """
    Create a FreeEnergyState with approximately the given surprise level.

    Args:
        surprise_level: Desired normalized surprise (0-1)

    Returns:
        FreeEnergyState

    Note: normalized_surprise = 1 / (1 + exp(-pred_error + 1))
    With 100 dims, pred_error = sqrt(100) * magnitude = 10 * magnitude
    So for norm_surprise ~0.1, need pred_error ~0 (magnitude ~0)
    For norm_surprise ~0.5, need pred_error ~1 (magnitude ~0.1)
    For norm_surprise ~0.9, need pred_error ~3.2 (magnitude ~0.32)
    """
    expected = np.zeros(DIMENSIONS)

    # Invert the sigmoid: pred_error = 1 - ln(1/norm_surprise - 1)
    # pred_error = 10 * magnitude, so magnitude = pred_error / 10
    if surprise_level >= 0.999:
        magnitude = 100.0
    elif surprise_level <= 0.001:
        magnitude = 0.0
    else:
        # Invert sigmoid
        pred_error = 1.0 - np.log(1.0 / surprise_level - 1.0)
        pred_error = max(0.0, pred_error)
        # pred_error = sqrt(DIMENSIONS) * magnitude
        magnitude = pred_error / np.sqrt(DIMENSIONS)

    actual = np.ones(DIMENSIONS) * magnitude

    return FreeEnergyState(
        expected_observation=expected,
        actual_observation=actual,
    )


class TestForageAction:
    """Tests for ForageAction enum."""

    def test_all_actions_exist(self) -> None:
        """All expected actions exist."""
        assert ForageAction.EXPLORE
        assert ForageAction.EXPLOIT
        assert ForageAction.PRUNE
        assert ForageAction.WAIT

    def test_actions_are_distinct(self) -> None:
        """All actions have distinct values."""
        actions = [
            ForageAction.EXPLORE,
            ForageAction.EXPLOIT,
            ForageAction.PRUNE,
            ForageAction.WAIT,
        ]
        assert len(set(actions)) == 4


class TestForagingPolicy:
    """Tests for ForagingPolicy."""

    def test_default_thresholds(self) -> None:
        """Default policy has sensible thresholds."""
        policy = ForagingPolicy()

        assert 0 < policy.explore_threshold < 1
        assert 0 < policy.prune_threshold < 1
        assert 0 < policy.exploit_reward_threshold < 1

    def test_high_surprise_triggers_explore(self) -> None:
        """High surprise (> explore_threshold) triggers EXPLORE."""
        policy = ForagingPolicy(explore_threshold=0.5)

        # Create high-surprise state
        state = make_state(0.8)  # Above threshold

        action = policy.select_action(state, reward=0.0)

        assert action == ForageAction.EXPLORE

    def test_low_surprise_high_reward_triggers_exploit(self) -> None:
        """Low surprise + high reward triggers EXPLOIT."""
        policy = ForagingPolicy(
            prune_threshold=0.3,
            exploit_reward_threshold=0.4,
        )

        # Create low-surprise state
        state = make_state(0.1)  # Below prune_threshold

        action = policy.select_action(state, reward=0.6)  # Above exploit threshold

        assert action == ForageAction.EXPLOIT

    def test_low_surprise_low_reward_triggers_prune(self) -> None:
        """Low surprise + low reward triggers PRUNE."""
        policy = ForagingPolicy(
            prune_threshold=0.3,
            exploit_reward_threshold=0.5,
        )

        # Create low-surprise state
        state = make_state(0.1)  # Below prune_threshold

        action = policy.select_action(state, reward=0.2)  # Below exploit threshold

        assert action == ForageAction.PRUNE

    def test_moderate_surprise_triggers_wait(self) -> None:
        """Moderate surprise triggers WAIT."""
        policy = ForagingPolicy(
            explore_threshold=0.7,
            prune_threshold=0.2,
        )

        # Create moderate-surprise state
        state = make_state(0.4)  # Between thresholds

        action = policy.select_action(state, reward=0.5)

        assert action == ForageAction.WAIT

    def test_custom_thresholds(self) -> None:
        """Custom thresholds work correctly."""
        policy = ForagingPolicy(
            explore_threshold=0.9,  # Very high
            prune_threshold=0.1,  # Very low
            exploit_reward_threshold=0.8,  # High
        )

        # With these thresholds, most states should WAIT
        state = make_state(0.5)
        action = policy.select_action(state, reward=0.5)

        assert action == ForageAction.WAIT


class TestForagingResult:
    """Tests for ForagingResult."""

    def test_free_energy_delta_computed(self) -> None:
        """free_energy_delta is after - before."""
        result = ForagingResult(
            action=ForageAction.EXPLORE,
            free_energy_before=10.0,
            free_energy_after=8.0,
            surprise=0.5,
            reward=0.3,
        )

        assert result.free_energy_delta == pytest.approx(-2.0)

    def test_free_energy_delta_none_when_no_after(self) -> None:
        """free_energy_delta is None when free_energy_after is None."""
        result = ForagingResult(
            action=ForageAction.PRUNE,
            free_energy_before=10.0,
            free_energy_after=None,
            surprise=0.5,
            reward=0.3,
        )

        assert result.free_energy_delta is None

    def test_improved_true_when_delta_negative(self) -> None:
        """improved is True when free energy decreased."""
        result = ForagingResult(
            action=ForageAction.EXPLORE,
            free_energy_before=10.0,
            free_energy_after=8.0,
            surprise=0.5,
            reward=0.3,
        )

        assert result.improved is True

    def test_improved_false_when_delta_positive(self) -> None:
        """improved is False when free energy increased."""
        result = ForagingResult(
            action=ForageAction.EXPLORE,
            free_energy_before=8.0,
            free_energy_after=10.0,
            surprise=0.5,
            reward=0.3,
        )

        assert result.improved is False

    def test_improved_false_when_no_after(self) -> None:
        """improved is False when no free_energy_after."""
        result = ForagingResult(
            action=ForageAction.PRUNE,
            free_energy_before=10.0,
            free_energy_after=None,
            surprise=0.5,
            reward=0.3,
        )

        assert result.improved is False

    def test_flags_track_actions(self) -> None:
        """imprinted, branched, pruned flags work."""
        result_branch = ForagingResult(
            action=ForageAction.EXPLORE,
            free_energy_before=0,
            free_energy_after=None,
            surprise=0,
            reward=0,
            branched=True,
        )
        assert result_branch.branched

        result_imprint = ForagingResult(
            action=ForageAction.EXPLOIT,
            free_energy_before=0,
            free_energy_after=None,
            surprise=0,
            reward=0,
            imprinted=True,
        )
        assert result_imprint.imprinted

        result_prune = ForagingResult(
            action=ForageAction.PRUNE,
            free_energy_before=0,
            free_energy_after=None,
            surprise=0,
            reward=0,
            pruned=True,
        )
        assert result_prune.pruned


class TestSelectForageAction:
    """Tests for select_forage_action convenience function."""

    def test_uses_default_policy(self) -> None:
        """select_forage_action uses DEFAULT_POLICY when none provided."""
        state = make_state(0.8)  # High surprise

        action = select_forage_action(state, reward=0.0)

        # Should match DEFAULT_POLICY behavior
        expected = DEFAULT_POLICY.select_action(state, reward=0.0)
        assert action == expected

    def test_uses_custom_policy(self) -> None:
        """select_forage_action uses provided policy."""
        policy = ForagingPolicy(explore_threshold=0.99)  # Very high

        state = make_state(0.8)  # Would normally explore

        action = select_forage_action(state, reward=0.0, policy=policy)

        # With high explore_threshold, should not explore
        assert action != ForageAction.EXPLORE


class TestDefaultPolicy:
    """Tests for DEFAULT_POLICY."""

    def test_default_policy_is_foraging_policy(self) -> None:
        """DEFAULT_POLICY is a ForagingPolicy instance."""
        assert isinstance(DEFAULT_POLICY, ForagingPolicy)

    def test_default_policy_has_sensible_defaults(self) -> None:
        """DEFAULT_POLICY has reasonable default thresholds."""
        # Explore threshold should be moderately high
        assert DEFAULT_POLICY.explore_threshold >= 0.5

        # Prune threshold should be low
        assert DEFAULT_POLICY.prune_threshold <= 0.5

        # Exploit reward threshold should be moderate
        assert 0.3 <= DEFAULT_POLICY.exploit_reward_threshold <= 0.7
