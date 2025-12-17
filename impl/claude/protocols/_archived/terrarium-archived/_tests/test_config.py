"""Tests for TerrariumConfig."""

import pytest
from protocols.terrarium.config import TerrariumConfig


class TestTerrariumConfigDefaults:
    """Default configuration values."""

    def test_default_values(self) -> None:
        """Config has sensible defaults."""
        config = TerrariumConfig()

        assert config.host == "0.0.0.0"
        assert config.port == 8080
        assert config.mirror_history_size == 100
        assert config.perturb_auth_required is True

    def test_custom_values(self) -> None:
        """Config accepts custom values."""
        config = TerrariumConfig(
            host="127.0.0.1",
            port=9000,
            mirror_history_size=500,
        )

        assert config.host == "127.0.0.1"
        assert config.port == 9000
        assert config.mirror_history_size == 500


class TestTerrariumConfigValidation:
    """Configuration validation."""

    def test_invalid_history_size(self) -> None:
        """mirror_history_size must be >= 1."""
        with pytest.raises(ValueError, match="mirror_history_size"):
            TerrariumConfig(mirror_history_size=0)

    def test_invalid_rate_limit(self) -> None:
        """perturb_rate_limit must be > 0."""
        with pytest.raises(ValueError, match="perturb_rate_limit"):
            TerrariumConfig(perturb_rate_limit=0)

        with pytest.raises(ValueError, match="perturb_rate_limit"):
            TerrariumConfig(perturb_rate_limit=-1)

    def test_invalid_max_lag(self) -> None:
        """observer_max_lag must be >= 1."""
        with pytest.raises(ValueError, match="observer_max_lag"):
            TerrariumConfig(observer_max_lag=0)
