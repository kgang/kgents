"""Tests for animation combinators (Sequence, Parallel)."""

import pytest
from agents.i.reactive.animation.combinators import (
    CombinatorState,
    Parallel,
    Sequence,
    parallel,
    sequence,
)
from agents.i.reactive.animation.easing import Easing
from agents.i.reactive.animation.tween import (
    TransitionStatus,
    Tween,
    TweenConfig,
    tween,
)


class TestSequenceCreation:
    """Tests for Sequence creation."""

    def test_create_empty(self) -> None:
        """Create empty sequence."""
        seq = Sequence.of([])
        assert len(seq) == 0

    def test_create_with_animations(self) -> None:
        """Create sequence with animations."""
        animations = [
            tween(0.0, 100.0, duration_ms=100.0),
            tween(100.0, 50.0, duration_ms=100.0),
        ]
        seq = Sequence.of(animations)
        assert len(seq) == 2

    def test_convenience_function(self) -> None:
        """Use convenience sequence() function."""
        seq = sequence(
            tween(0.0, 100.0),
            tween(100.0, 50.0),
        )
        assert len(seq) == 2


class TestSequenceLifecycle:
    """Tests for Sequence lifecycle."""

    def test_start_begins_first_animation(self) -> None:
        """Start begins the first animation."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(100.0, 50.0, duration_ms=100.0)
        seq = sequence(tw1, tw2)

        seq.start()

        assert seq.state.value.status == TransitionStatus.RUNNING
        assert tw1.is_running
        assert not tw2.is_running

    def test_pause_pauses_current(self) -> None:
        """Pause pauses current animation."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        seq = sequence(tw1)
        seq.start()

        seq.pause()

        assert seq.state.value.status == TransitionStatus.PAUSED
        assert tw1.state.value.status == TransitionStatus.PAUSED

    def test_resume_resumes_current(self) -> None:
        """Resume resumes current animation."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        seq = sequence(tw1)
        seq.start()
        seq.pause()

        seq.resume()

        assert seq.state.value.status == TransitionStatus.RUNNING
        assert tw1.is_running

    def test_reset_resets_all(self) -> None:
        """Reset resets all animations."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(100.0, 50.0, duration_ms=100.0)
        seq = sequence(tw1, tw2)
        seq.start()
        seq.update(100.0)  # Complete first

        seq.reset()

        assert seq.state.value.status == TransitionStatus.PENDING
        assert tw1.state.value.status == TransitionStatus.PENDING
        assert tw2.state.value.status == TransitionStatus.PENDING


class TestSequenceUpdate:
    """Tests for Sequence.update()."""

    def test_update_advances_first(self) -> None:
        """Update advances first animation."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(100.0, 50.0, duration_ms=100.0)
        seq = sequence(tw1, tw2)
        seq.start()

        seq.update(50.0)

        assert seq.state.value.current_index == 0
        assert tw1.progress > 0

    def test_transitions_to_next(self) -> None:
        """Sequence transitions to next animation."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(100.0, 50.0, duration_ms=100.0)
        seq = sequence(tw1, tw2)
        seq.start()

        seq.update(100.0)  # Complete first

        assert seq.state.value.current_index == 1
        assert tw1.is_complete
        assert tw2.is_running

    def test_completes_when_all_done(self) -> None:
        """Sequence completes when all animations done."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(100.0, 50.0, duration_ms=100.0)
        seq = sequence(tw1, tw2)
        seq.start()

        seq.update(100.0)  # First done
        seq.update(100.0)  # Second done

        assert seq.is_complete

    def test_progress_calculated_correctly(self) -> None:
        """Progress reflects position in sequence."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(100.0, 50.0, duration_ms=100.0)
        seq = sequence(tw1, tw2)
        seq.start()

        seq.update(50.0)  # 50% through first
        # Progress = (0 + 0.5) / 2 = 0.25
        assert 0.2 <= seq.state.value.progress <= 0.3

        seq.update(50.0)  # First complete
        # Progress = (1) / 2 = 0.5
        assert 0.4 <= seq.state.value.progress <= 0.6


class TestSequenceValues:
    """Tests for Sequence value access."""

    def test_current_animation(self) -> None:
        """current_animation returns active animation."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(100.0, 50.0, duration_ms=100.0)
        seq = sequence(tw1, tw2)
        seq.start()

        assert seq.current_animation is tw1

        seq.update(100.0)
        assert seq.current_animation is tw2

    def test_current_value(self) -> None:
        """current_value returns current animation's value."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0, easing=Easing.LINEAR)
        seq = sequence(tw1)
        seq.start()
        seq.update(50.0)

        value = seq.current_value()
        assert value is not None
        assert 40 < value < 60


class TestSequenceCallback:
    """Tests for Sequence completion callback."""

    def test_on_complete_called(self) -> None:
        """on_complete called when sequence finishes."""
        completed = [False]

        def on_done(s: Sequence) -> None:
            completed[0] = True

        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        seq = Sequence.of([tw1], on_complete=on_done)
        seq.start()
        seq.update(100.0)

        assert completed[0] is True


class TestParallelCreation:
    """Tests for Parallel creation."""

    def test_create_empty(self) -> None:
        """Create empty parallel."""
        par = Parallel.of([])
        assert len(par) == 0

    def test_create_with_animations(self) -> None:
        """Create parallel with animations."""
        animations = [
            tween(0.0, 100.0, duration_ms=100.0),
            tween(0.0, 50.0, duration_ms=100.0),
        ]
        par = Parallel.of(animations)
        assert len(par) == 2

    def test_convenience_function(self) -> None:
        """Use convenience parallel() function."""
        par = parallel(
            tween(0.0, 100.0),
            tween(0.0, 50.0),
        )
        assert len(par) == 2


class TestParallelLifecycle:
    """Tests for Parallel lifecycle."""

    def test_start_begins_all_animations(self) -> None:
        """Start begins all animations simultaneously."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=100.0)
        par = parallel(tw1, tw2)

        par.start()

        assert par.state.value.status == TransitionStatus.RUNNING
        assert tw1.is_running
        assert tw2.is_running

    def test_pause_pauses_all(self) -> None:
        """Pause pauses all animations."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=100.0)
        par = parallel(tw1, tw2)
        par.start()

        par.pause()

        assert par.state.value.status == TransitionStatus.PAUSED
        assert tw1.state.value.status == TransitionStatus.PAUSED
        assert tw2.state.value.status == TransitionStatus.PAUSED

    def test_resume_resumes_all(self) -> None:
        """Resume resumes all animations."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=100.0)
        par = parallel(tw1, tw2)
        par.start()
        par.pause()

        par.resume()

        assert par.state.value.status == TransitionStatus.RUNNING
        assert tw1.is_running
        assert tw2.is_running

    def test_reset_resets_all(self) -> None:
        """Reset resets all animations."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=100.0)
        par = parallel(tw1, tw2)
        par.start()
        par.update(50.0)

        par.reset()

        assert par.state.value.status == TransitionStatus.PENDING
        assert tw1.state.value.status == TransitionStatus.PENDING
        assert tw2.state.value.status == TransitionStatus.PENDING


class TestParallelUpdate:
    """Tests for Parallel.update()."""

    def test_update_advances_all(self) -> None:
        """Update advances all animations."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=100.0)
        par = parallel(tw1, tw2)
        par.start()

        par.update(50.0)

        assert tw1.progress > 0
        assert tw2.progress > 0

    def test_completes_when_all_done(self) -> None:
        """Parallel completes when ALL animations done."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=200.0)  # Longer duration
        par = parallel(tw1, tw2)
        par.start()

        par.update(100.0)  # First done, second not
        assert not par.is_complete

        par.update(100.0)  # Both done
        assert par.is_complete

    def test_progress_is_average(self) -> None:
        """Progress is average of all animations."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=200.0)
        par = parallel(tw1, tw2)
        par.start()

        par.update(100.0)  # tw1: 100%, tw2: 50%
        # Average progress = (1.0 + 0.5) / 2 = 0.75
        assert 0.7 <= par.state.value.progress <= 0.8


class TestParallelValues:
    """Tests for Parallel value access."""

    def test_values_returns_all(self) -> None:
        """values() returns all current values."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=100.0)
        par = parallel(tw1, tw2)
        par.start()
        par.update(50.0)

        values = par.values()
        assert len(values) == 2
        assert all(v > 0 for v in values)

    def test_value_at_returns_specific(self) -> None:
        """value_at() returns specific animation's value."""
        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=100.0)
        par = parallel(tw1, tw2)
        par.start()
        par.update(50.0)

        v1 = par.value_at(0)
        v2 = par.value_at(1)
        assert v1 is not None
        assert v2 is not None
        # Different end values should give different results
        assert v1 > v2  # v1 targets 100, v2 targets 50

    def test_value_at_out_of_bounds(self) -> None:
        """value_at() returns None for out of bounds."""
        par = parallel(tween(0.0, 100.0))
        assert par.value_at(99) is None


class TestParallelCallback:
    """Tests for Parallel completion callback."""

    def test_on_complete_called(self) -> None:
        """on_complete called when all animations finish."""
        completed = [False]

        def on_done(p: Parallel) -> None:
            completed[0] = True

        tw1 = tween(0.0, 100.0, duration_ms=100.0)
        tw2 = tween(0.0, 50.0, duration_ms=100.0)
        par = Parallel.of([tw1, tw2], on_complete=on_done)
        par.start()
        par.update(100.0)

        assert completed[0] is True


class TestCombinatorComposition:
    """Tests for composing combinators."""

    def test_sequence_of_parallels(self) -> None:
        """Can sequence parallels."""
        par1 = parallel(
            tween(0.0, 100.0, duration_ms=50.0),
            tween(0.0, 50.0, duration_ms=50.0),
        )
        par2 = parallel(
            tween(100.0, 0.0, duration_ms=50.0),
            tween(50.0, 0.0, duration_ms=50.0),
        )

        # Note: This would require Sequence to accept AnimationCombinator
        # For now we just verify the parallels work independently
        par1.start()
        par1.update(50.0)
        assert par1.is_complete

    def test_empty_sequence_completes_immediately(self) -> None:
        """Empty sequence completes immediately when updated."""
        seq = sequence()
        seq.start()
        seq.update(16.67)  # One frame is enough
        assert seq.is_complete

    def test_empty_parallel_completes_immediately(self) -> None:
        """Empty parallel completes immediately."""
        par = parallel()
        par.start()
        par.update(0.0)
        assert par.is_complete
