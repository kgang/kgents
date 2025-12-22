"""
Tests for DisgustVeto: The Absolute Veto Mechanism.

Tests the phenomenological disgust veto that Kent can apply.
"""

from datetime import datetime

import pytest

from services.fusion.types import Synthesis
from services.fusion.veto import (
    DisgustSignal,
    DisgustVeto,
    VetoSource,
)


class TestDigustSignal:
    """Test DisgustSignal dataclass."""

    def test_high_intensity_is_veto(self):
        """High intensity triggers veto."""
        signal = DisgustSignal(
            timestamp=datetime.utcnow(),
            source=VetoSource.EXPLICIT,
            reason="Visceral wrongness",
            intensity=1.0,
        )

        assert signal.is_veto is True
        assert signal.is_warning is False

    def test_medium_intensity_is_warning(self):
        """Medium intensity is warning, not veto."""
        signal = DisgustSignal(
            timestamp=datetime.utcnow(),
            source=VetoSource.EXPLICIT,
            reason="Some discomfort",
            intensity=0.5,
        )

        assert signal.is_veto is False
        assert signal.is_warning is True

    def test_low_intensity_is_neither(self):
        """Low intensity is neither veto nor warning."""
        signal = DisgustSignal(
            timestamp=datetime.utcnow(),
            source=VetoSource.EXPLICIT,
            reason="Mild concern",
            intensity=0.2,
        )

        assert signal.is_veto is False
        assert signal.is_warning is False

    def test_threshold_boundary(self):
        """Intensity exactly at threshold triggers veto."""
        threshold = 0.7
        signal = DisgustSignal(
            timestamp=datetime.utcnow(),
            source=VetoSource.EXPLICIT,
            reason="At threshold",
            intensity=threshold,
            veto_threshold=threshold,
        )

        assert signal.is_veto is True


class TestDigustVeto:
    """Test DisgustVeto mechanism."""

    def test_explicit_veto(self):
        """explicit_veto creates high-intensity signal."""
        veto = DisgustVeto()
        signal = veto.explicit_veto("This feels fundamentally wrong")

        assert signal.is_veto is True
        assert signal.source == VetoSource.EXPLICIT
        assert signal.reason == "This feels fundamentally wrong"
        assert signal.intensity == 1.0

    def test_explicit_veto_with_intensity(self):
        """explicit_veto respects intensity parameter."""
        veto = DisgustVeto()
        signal = veto.explicit_veto("Moderate concern", intensity=0.8)

        assert signal.is_veto is True
        assert signal.intensity == 0.8

    def test_warning(self):
        """warning creates below-threshold signal."""
        veto = DisgustVeto()
        signal = veto.warning("I have reservations")

        assert signal.is_veto is False
        assert signal.is_warning is True
        assert signal.intensity < 0.7

    def test_intensity_clamped(self):
        """Intensity is clamped to [0, 1]."""
        veto = DisgustVeto()

        # Above 1.0
        signal = veto.explicit_veto("Too high", intensity=1.5)
        assert signal.intensity == 1.0

        # Below 0.0
        signal = veto.explicit_veto("Too low", intensity=-0.5)
        assert signal.intensity == 0.0

    @pytest.mark.asyncio
    async def test_check_without_callback(self):
        """check returns None without callback (assumes no disgust)."""
        veto = DisgustVeto()
        synthesis = Synthesis(content="Test", reasoning="Test")

        signal = await veto.check(synthesis)

        assert signal is None

    @pytest.mark.asyncio
    async def test_check_with_callback_no_disgust(self):
        """check returns None when callback returns False."""
        veto = DisgustVeto()
        synthesis = Synthesis(content="Test", reasoning="Test")

        async def no_disgust(s):
            return False

        signal = await veto.check(synthesis, callback=no_disgust)

        assert signal is None

    @pytest.mark.asyncio
    async def test_check_with_callback_disgust(self):
        """check returns signal when callback returns True."""
        veto = DisgustVeto()
        synthesis = Synthesis(content="Test", reasoning="Test")

        async def feels_disgust(s):
            return True

        signal = await veto.check(synthesis, callback=feels_disgust)

        assert signal is not None
        assert signal.is_veto is True
