"""Tests for FluxConfig dataclass."""

import pytest

from agents.flux.config import FluxConfig


class TestFluxConfigDefaults:
    """Test FluxConfig default values."""

    def test_default_entropy_budget(self):
        config = FluxConfig()
        assert config.entropy_budget == 1.0

    def test_default_entropy_decay(self):
        config = FluxConfig()
        assert config.entropy_decay == 0.01

    def test_default_max_events(self):
        config = FluxConfig()
        assert config.max_events is None

    def test_default_buffer_size(self):
        config = FluxConfig()
        assert config.buffer_size == 100

    def test_default_drop_policy(self):
        config = FluxConfig()
        assert config.drop_policy == "block"

    def test_default_feedback_fraction(self):
        config = FluxConfig()
        assert config.feedback_fraction == 0.0

    def test_default_feedback_transform(self):
        config = FluxConfig()
        assert config.feedback_transform is None

    def test_default_emit_pheromones(self):
        config = FluxConfig()
        assert config.emit_pheromones is True

    def test_default_trace_enabled(self):
        config = FluxConfig()
        assert config.trace_enabled is True

    def test_default_agent_id(self):
        config = FluxConfig()
        assert config.agent_id is None


class TestFluxConfigValidation:
    """Test FluxConfig validation."""

    def test_invalid_entropy_budget_zero(self):
        with pytest.raises(ValueError, match="entropy_budget"):
            FluxConfig(entropy_budget=0)

    def test_invalid_entropy_budget_negative(self):
        with pytest.raises(ValueError, match="entropy_budget"):
            FluxConfig(entropy_budget=-1)

    def test_invalid_entropy_decay_negative(self):
        with pytest.raises(ValueError, match="entropy_decay"):
            FluxConfig(entropy_decay=-0.01)

    def test_valid_entropy_decay_zero(self):
        # Zero decay is valid (infinite entropy)
        config = FluxConfig(entropy_decay=0.0)
        assert config.entropy_decay == 0.0

    def test_invalid_buffer_size_zero(self):
        with pytest.raises(ValueError, match="buffer_size"):
            FluxConfig(buffer_size=0)

    def test_invalid_buffer_size_negative(self):
        with pytest.raises(ValueError, match="buffer_size"):
            FluxConfig(buffer_size=-10)

    def test_invalid_drop_policy(self):
        with pytest.raises(ValueError, match="drop_policy"):
            FluxConfig(drop_policy="invalid")

    def test_valid_drop_policies(self):
        for policy in ["block", "drop_oldest", "drop_newest"]:
            config = FluxConfig(drop_policy=policy)
            assert config.drop_policy == policy

    def test_invalid_feedback_fraction_negative(self):
        with pytest.raises(ValueError, match="feedback_fraction"):
            FluxConfig(feedback_fraction=-0.1)

    def test_invalid_feedback_fraction_over_one(self):
        with pytest.raises(ValueError, match="feedback_fraction"):
            FluxConfig(feedback_fraction=1.1)

    def test_valid_feedback_fraction_boundaries(self):
        config_zero = FluxConfig(feedback_fraction=0.0)
        assert config_zero.feedback_fraction == 0.0

        config_one = FluxConfig(feedback_fraction=1.0)
        assert config_one.feedback_fraction == 1.0

    def test_invalid_max_events_zero(self):
        with pytest.raises(ValueError, match="max_events"):
            FluxConfig(max_events=0)

    def test_invalid_max_events_negative(self):
        with pytest.raises(ValueError, match="max_events"):
            FluxConfig(max_events=-1)


class TestFluxConfigImmutability:
    """Test FluxConfig is frozen/immutable."""

    def test_cannot_modify_entropy_budget(self):
        config = FluxConfig()
        with pytest.raises(Exception):  # FrozenInstanceError
            config.entropy_budget = 2.0  # type: ignore[misc]

    def test_cannot_modify_drop_policy(self):
        config = FluxConfig()
        with pytest.raises(Exception):
            config.drop_policy = "drop_oldest"  # type: ignore[misc]


class TestFluxConfigWithMethods:
    """Test FluxConfig with_* builder methods."""

    def test_with_entropy_budget(self):
        original = FluxConfig()
        modified = original.with_entropy(budget=2.0)

        assert original.entropy_budget == 1.0  # Unchanged
        assert modified.entropy_budget == 2.0

    def test_with_entropy_decay(self):
        original = FluxConfig()
        modified = original.with_entropy(decay=0.05)

        assert original.entropy_decay == 0.01
        assert modified.entropy_decay == 0.05

    def test_with_entropy_max_events(self):
        original = FluxConfig()
        modified = original.with_entropy(max_events=500)

        assert original.max_events is None
        assert modified.max_events == 500

    def test_with_backpressure_buffer_size(self):
        original = FluxConfig()
        modified = original.with_backpressure(buffer_size=50)

        assert original.buffer_size == 100
        assert modified.buffer_size == 50

    def test_with_backpressure_drop_policy(self):
        original = FluxConfig()
        modified = original.with_backpressure(drop_policy="drop_oldest")

        assert original.drop_policy == "block"
        assert modified.drop_policy == "drop_oldest"

    def test_with_feedback_fraction(self):
        original = FluxConfig()
        modified = original.with_feedback(fraction=0.5)

        assert original.feedback_fraction == 0.0
        assert modified.feedback_fraction == 0.5

    def test_with_feedback_transform(self):
        def transform(x: int) -> str:
            return str(x)

        original = FluxConfig()
        modified = original.with_feedback(transform=transform)

        assert original.feedback_transform is None
        assert modified.feedback_transform is transform

    def test_with_feedback_preserves_other_fields(self):
        original = FluxConfig(entropy_budget=5.0, buffer_size=50)
        modified = original.with_feedback(fraction=0.3)

        assert modified.entropy_budget == 5.0
        assert modified.buffer_size == 50


class TestFluxConfigFactoryMethods:
    """Test FluxConfig factory class methods."""

    def test_infinite_config(self):
        config = FluxConfig.infinite()
        assert config.entropy_budget == float("inf")
        assert config.entropy_decay == 0.0

    def test_bounded_config(self):
        config = FluxConfig.bounded(max_events=1000)
        assert config.max_events == 1000
        assert config.entropy_budget == float("inf")
        assert config.entropy_decay == 0.0

    def test_ouroboric_config_default(self):
        config = FluxConfig.ouroboric()
        assert config.feedback_fraction == 0.5

    def test_ouroboric_config_custom(self):
        config = FluxConfig.ouroboric(feedback_fraction=0.3)
        assert config.feedback_fraction == 0.3


class TestFluxConfigCustomValues:
    """Test FluxConfig with custom values."""

    def test_all_custom_values(self):
        def transform(x: int) -> int:
            return x

        config = FluxConfig(
            entropy_budget=10.0,
            entropy_decay=0.1,
            max_events=100,
            buffer_size=50,
            drop_policy="drop_oldest",
            feedback_fraction=0.5,
            feedback_transform=transform,
            feedback_queue_size=25,
            emit_pheromones=False,
            trace_enabled=False,
            agent_id="custom-id",
            perturbation_timeout=5.0,
            perturbation_priority=50,
        )

        assert config.entropy_budget == 10.0
        assert config.entropy_decay == 0.1
        assert config.max_events == 100
        assert config.buffer_size == 50
        assert config.drop_policy == "drop_oldest"
        assert config.feedback_fraction == 0.5
        assert config.feedback_transform is transform
        assert config.feedback_queue_size == 25
        assert config.emit_pheromones is False
        assert config.trace_enabled is False
        assert config.agent_id == "custom-id"
        assert config.perturbation_timeout == 5.0
        assert config.perturbation_priority == 50
