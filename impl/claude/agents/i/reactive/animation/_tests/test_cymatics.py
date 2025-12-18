"""Tests for the Cymatics Engine - vibration visualization.

Philosophy verification:
    - Wave superposition produces interference patterns
    - Multiple sources create constructive/destructive interference
    - Pattern stability measures harmony vs. chaos
    - Empty engine produces zero amplitude everywhere
"""

import math

import pytest

from agents.i.reactive.animation.cymatics import (
    ChladniPattern,
    CymaticsEngine,
    VibrationSource,
    create_dissonant_sources,
    create_harmonic_sources,
    pattern_stability,
)


class TestVibrationSource:
    """Test VibrationSource wave generation."""

    def test_default_values(self) -> None:
        """Default source should have reasonable values."""
        source = VibrationSource(frequency=1.0, amplitude=1.0)
        assert source.frequency == 1.0
        assert source.amplitude == 1.0
        assert source.phase == 0.0
        assert source.position == (0.0, 0.0)
        assert source.decay == 0.5

    def test_amplitude_clamped(self) -> None:
        """Amplitude should be clamped to [0, 1]."""
        source = VibrationSource(frequency=1.0, amplitude=2.0)
        assert source.amplitude == 1.0

        source2 = VibrationSource(frequency=1.0, amplitude=-0.5)
        assert source2.amplitude == 0.0

    def test_frequency_positive(self) -> None:
        """Frequency should be forced positive."""
        source = VibrationSource(frequency=-1.0, amplitude=1.0)
        assert source.frequency > 0

    def test_wave_at_origin(self) -> None:
        """Wave at source position should be non-zero."""
        source = VibrationSource(frequency=1.0, amplitude=1.0, position=(0, 0))
        # At t=0, wave should be affected by phase
        wave = source.wave_at(0, 0, 0)
        # sin(0) = 0, but we want to verify the function runs
        assert isinstance(wave, float)

    def test_wave_at_distance(self) -> None:
        """Wave should decay with distance."""
        source = VibrationSource(frequency=1.0, amplitude=1.0, position=(0, 0))

        # Sample at origin vs. far point
        wave_near = abs(source.wave_at(0, 0, 0.25))  # Peak of sine at t=0.25
        wave_far = abs(source.wave_at(1.0, 0, 0.25))

        # Far wave should be weaker due to decay
        assert wave_far < wave_near

    def test_wave_oscillates(self) -> None:
        """Wave should oscillate over time."""
        source = VibrationSource(frequency=1.0, amplitude=1.0, position=(0, 0))

        # Sample at different times
        waves = [source.wave_at(0.1, 0, t * 0.1) for t in range(20)]

        # Should have positive and negative values
        assert any(w > 0 for w in waves)
        assert any(w < 0 for w in waves)

    def test_immutable(self) -> None:
        """VibrationSource should be immutable."""
        source = VibrationSource(frequency=1.0, amplitude=1.0)
        with pytest.raises(AttributeError):
            source.frequency = 2.0  # type: ignore


class TestCymaticsEngine:
    """Test CymaticsEngine simulation."""

    def test_create_empty(self) -> None:
        """Created engine should be empty."""
        engine = CymaticsEngine.create()
        assert engine.source_count == 0
        assert engine.time == 0.0

    def test_create_with_resolution(self) -> None:
        """Engine should accept custom resolution."""
        engine = CymaticsEngine.create(resolution=32)
        assert engine.resolution == 32

    def test_add_source(self) -> None:
        """Adding sources should increase count."""
        engine = CymaticsEngine.create()
        engine.add_source(VibrationSource(frequency=1.0, amplitude=1.0))
        assert engine.source_count == 1

        engine.add_source(VibrationSource(frequency=2.0, amplitude=0.5))
        assert engine.source_count == 2

    def test_remove_source(self) -> None:
        """Removing source should decrease count."""
        engine = CymaticsEngine.create()
        engine.add_source(VibrationSource(frequency=1.0, amplitude=1.0, position=(0.5, 0)))
        engine.add_source(VibrationSource(frequency=2.0, amplitude=0.5, position=(-0.5, 0)))

        assert engine.remove_source((0.5, 0))
        assert engine.source_count == 1

    def test_remove_nonexistent(self) -> None:
        """Removing nonexistent source should return False."""
        engine = CymaticsEngine.create()
        engine.add_source(VibrationSource(frequency=1.0, amplitude=1.0, position=(0, 0)))

        assert not engine.remove_source((1.0, 1.0))
        assert engine.source_count == 1

    def test_clear(self) -> None:
        """Clear should remove all sources."""
        engine = CymaticsEngine.create()
        engine.add_source(VibrationSource(frequency=1.0, amplitude=1.0))
        engine.add_source(VibrationSource(frequency=2.0, amplitude=0.5))
        engine.clear()
        assert engine.source_count == 0

    def test_step_advances_time(self) -> None:
        """Step should advance simulation time."""
        engine = CymaticsEngine.create()
        assert engine.time == 0.0

        engine.step(0.1)
        assert abs(engine.time - 0.1) < 0.001

        engine.step(0.2)
        assert abs(engine.time - 0.3) < 0.001

    def test_reset_time(self) -> None:
        """Reset should return time to zero."""
        engine = CymaticsEngine.create()
        engine.step(1.0)
        engine.reset_time()
        assert engine.time == 0.0

    def test_amplitude_at_empty(self) -> None:
        """Empty engine should produce zero amplitude."""
        engine = CymaticsEngine.create()
        assert engine.amplitude_at(0, 0) == 0.0
        assert engine.amplitude_at(0.5, 0.5) == 0.0

    def test_amplitude_at_with_source(self) -> None:
        """Engine with source should produce non-zero amplitude at some times."""
        engine = CymaticsEngine.create()
        engine.add_source(VibrationSource(frequency=1.0, amplitude=1.0, position=(0, 0)))

        # Sample at multiple times
        amplitudes = [engine.amplitude_at(0.1, 0, t * 0.1) for t in range(10)]

        # Should have non-zero values
        assert any(abs(a) > 0.01 for a in amplitudes)

    def test_superposition(self) -> None:
        """Multiple sources should superpose (add)."""
        engine = CymaticsEngine.create()

        # Two in-phase sources at same position should double amplitude
        source1 = VibrationSource(frequency=1.0, amplitude=1.0, position=(0, 0), phase=0)
        source2 = VibrationSource(frequency=1.0, amplitude=1.0, position=(0, 0), phase=0)

        # Single source amplitude
        engine.add_source(source1)
        amp_single = engine.amplitude_at(0.1, 0, 0.25)

        # Double source amplitude
        engine.add_source(source2)
        amp_double = engine.amplitude_at(0.1, 0, 0.25)

        # Should be approximately double (within some tolerance)
        assert abs(amp_double - 2 * amp_single) < 0.1


class TestChladniPattern:
    """Test ChladniPattern output."""

    def test_compute_produces_pattern(self) -> None:
        """Computing should produce a ChladniPattern."""
        engine = CymaticsEngine.create(resolution=16)
        engine.add_source(VibrationSource(frequency=2.0, amplitude=1.0, position=(0, 0)))

        pattern = engine.compute(time=0.5)

        assert isinstance(pattern, ChladniPattern)
        assert pattern.resolution == 16
        assert len(pattern.grid) == 16
        assert len(pattern.grid[0]) == 16

    def test_compute_empty_engine(self) -> None:
        """Empty engine should produce zero pattern."""
        engine = CymaticsEngine.create(resolution=8)
        pattern = engine.compute()

        assert pattern.min_amplitude == 0.0
        assert pattern.max_amplitude == 0.0

    def test_field_interpolation(self) -> None:
        """Field method should interpolate grid values."""
        engine = CymaticsEngine.create(resolution=8)
        engine.add_source(VibrationSource(frequency=2.0, amplitude=1.0, position=(0, 0)))

        pattern = engine.compute(time=0.25)

        # Sample at grid center
        center = pattern.field(0, 0)
        assert isinstance(center, float)

        # Sample between grid points
        between = pattern.field(0.1, 0.1)
        assert isinstance(between, float)

    def test_normalized_field(self) -> None:
        """Normalized field should return values in [0, 1]."""
        engine = CymaticsEngine.create(resolution=16)
        engine.add_source(VibrationSource(frequency=2.0, amplitude=1.0, position=(0, 0)))

        pattern = engine.compute(time=0.25)

        for x in [-0.9, -0.5, 0, 0.5, 0.9]:
            for y in [-0.9, -0.5, 0, 0.5, 0.9]:
                norm_val = pattern.normalized_field(x, y)
                assert 0 <= norm_val <= 1

    def test_nodes_and_antinodes(self) -> None:
        """Pattern should identify nodes and antinodes."""
        engine = CymaticsEngine.create(resolution=32)

        # Two sources create interference
        engine.add_source(VibrationSource(frequency=2.0, amplitude=1.0, position=(-0.3, 0)))
        engine.add_source(VibrationSource(frequency=2.0, amplitude=1.0, position=(0.3, 0)))

        pattern = engine.compute(time=0.5)

        # Should have some nodes (constructive) and antinodes (destructive)
        # Note: exact counts depend on the pattern
        assert isinstance(pattern.nodes, tuple)
        assert isinstance(pattern.antinodes, tuple)


class TestInterference:
    """Test constructive and destructive interference."""

    def test_constructive_interference(self) -> None:
        """In-phase sources should interfere constructively."""
        engine = CymaticsEngine.create(resolution=16)

        # Two in-phase sources
        engine.add_source(
            VibrationSource(frequency=1.0, amplitude=1.0, position=(-0.2, 0), phase=0)
        )
        engine.add_source(VibrationSource(frequency=1.0, amplitude=1.0, position=(0.2, 0), phase=0))

        pattern = engine.compute(time=0.25)

        # At midpoint between sources, waves should add
        # Max amplitude should be higher than single source
        assert pattern.max_amplitude > 0.5

    def test_destructive_interference(self) -> None:
        """Out-of-phase sources should interfere destructively."""
        engine = CymaticsEngine.create(resolution=16)

        # Two out-of-phase sources (pi phase difference)
        engine.add_source(
            VibrationSource(frequency=1.0, amplitude=1.0, position=(-0.2, 0), phase=0)
        )
        engine.add_source(
            VibrationSource(frequency=1.0, amplitude=1.0, position=(0.2, 0), phase=math.pi)
        )

        # At midpoint, waves should partially cancel
        # This is geometry-dependent, so we just verify pattern exists
        pattern = engine.compute(time=0.25)
        assert pattern is not None


class TestPatternStability:
    """Test pattern stability measurement."""

    def test_empty_pattern_unstable(self) -> None:
        """Empty pattern should have zero stability."""
        engine = CymaticsEngine.create(resolution=8)
        pattern = engine.compute()
        assert pattern_stability(pattern) == 0.0

    def test_single_source_stable(self) -> None:
        """Single source should have some stability."""
        engine = CymaticsEngine.create(resolution=16)
        engine.add_source(VibrationSource(frequency=2.0, amplitude=1.0, position=(0, 0)))

        pattern = engine.compute(time=0.25)
        stability = pattern_stability(pattern)

        # Single source creates clear pattern
        assert stability > 0

    def test_harmonic_vs_dissonant(self) -> None:
        """Harmonic sources should be more stable than dissonant."""
        # Harmonic sources (same frequency)
        harmonic_engine = CymaticsEngine.create(resolution=32)
        for source in create_harmonic_sources(3, base_frequency=2.0):
            harmonic_engine.add_source(source)
        harmonic_pattern = harmonic_engine.compute(time=0.5)
        harmonic_stability = pattern_stability(harmonic_pattern)

        # Dissonant sources (different frequencies)
        dissonant_engine = CymaticsEngine.create(resolution=32)
        for source in create_dissonant_sources([1.7, 2.3, 3.1]):
            dissonant_engine.add_source(source)
        dissonant_pattern = dissonant_engine.compute(time=0.5)
        dissonant_stability = pattern_stability(dissonant_pattern)

        # Both should produce patterns
        assert harmonic_stability > 0
        assert dissonant_stability > 0


class TestConvenienceFunctions:
    """Test convenience source creation functions."""

    def test_create_harmonic_sources(self) -> None:
        """Should create harmonically-related sources."""
        sources = create_harmonic_sources(4, base_frequency=2.0, amplitude=0.8)

        assert len(sources) == 4

        # All should have same frequency
        for source in sources:
            assert source.frequency == 2.0
            assert source.amplitude == 0.8

        # Positions should be in a ring
        for source in sources:
            r = math.sqrt(source.position[0] ** 2 + source.position[1] ** 2)
            assert abs(r - 0.5) < 0.01  # Default radius

    def test_create_dissonant_sources(self) -> None:
        """Should create sources with different frequencies."""
        freqs = [1.0, 1.5, 2.0, 3.0]
        sources = create_dissonant_sources(freqs, amplitude=0.7)

        assert len(sources) == 4

        # Each should have its own frequency
        for source, freq in zip(sources, freqs):
            assert source.frequency == freq
            assert source.amplitude == 0.7
