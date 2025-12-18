"""Tests for Signal[T], Computed[T], and Effect reactive primitives."""

from __future__ import annotations

import pytest

from agents.i.reactive.signal import Computed, Effect, Signal


class TestSignal:
    """Tests for Signal[T] reactive primitive."""

    def test_signal_of_creates_with_value(self) -> None:
        """Signal.of() creates signal with initial value."""
        signal = Signal.of(42)
        assert signal.value == 42

    def test_signal_of_with_string(self) -> None:
        """Signal.of() works with string values."""
        signal = Signal.of("hello")
        assert signal.value == "hello"

    def test_signal_set_updates_value(self) -> None:
        """Signal.set() updates the value."""
        signal = Signal.of(0)
        signal.set(10)
        assert signal.value == 10

    def test_signal_set_notifies_subscribers(self) -> None:
        """Subscribers are called when value changes."""
        signal = Signal.of(0)
        received: list[int] = []
        signal.subscribe(lambda v: received.append(v))

        signal.set(1)
        signal.set(2)
        signal.set(3)

        assert received == [1, 2, 3]

    def test_signal_no_notify_same_value(self) -> None:
        """No notification if value unchanged."""
        signal = Signal.of(5)
        received: list[int] = []
        signal.subscribe(lambda v: received.append(v))

        signal.set(5)  # Same value
        signal.set(5)  # Same again

        assert received == []  # No notifications

    def test_signal_update_applies_function(self) -> None:
        """Signal.update() applies function to current value."""
        signal = Signal.of(10)
        signal.update(lambda x: x * 2)
        assert signal.value == 20

    def test_signal_update_notifies_on_change(self) -> None:
        """Signal.update() notifies subscribers if value changes."""
        signal = Signal.of(5)
        received: list[int] = []
        signal.subscribe(lambda v: received.append(v))

        signal.update(lambda x: x + 1)
        assert received == [6]

    def test_signal_unsubscribe(self) -> None:
        """Unsubscribe function removes subscriber."""
        signal = Signal.of(0)
        received: list[int] = []
        unsub = signal.subscribe(lambda v: received.append(v))

        signal.set(1)  # Should notify
        unsub()  # Unsubscribe
        signal.set(2)  # Should NOT notify

        assert received == [1]

    def test_signal_multiple_subscribers(self) -> None:
        """Multiple subscribers all receive notifications."""
        signal = Signal.of(0)
        received_a: list[int] = []
        received_b: list[int] = []

        signal.subscribe(lambda v: received_a.append(v))
        signal.subscribe(lambda v: received_b.append(v))

        signal.set(42)

        assert received_a == [42]
        assert received_b == [42]

    def test_signal_map_creates_computed(self) -> None:
        """Signal.map() creates a Computed with transformed value."""
        signal = Signal.of(5)
        doubled = signal.map(lambda x: x * 2)

        assert isinstance(doubled, Computed)
        assert doubled.value == 10

    def test_signal_map_updates_on_change(self) -> None:
        """Mapped Computed updates when source signal changes."""
        signal = Signal.of(3)
        squared = signal.map(lambda x: x**2)

        assert squared.value == 9
        signal.set(4)
        assert squared.value == 16


class TestComputed:
    """Tests for Computed[T] derived state."""

    def test_computed_of_creates_with_computation(self) -> None:
        """Computed.of() creates computed value."""
        computed = Computed.of(compute=lambda: 2 + 2)
        assert computed.value == 4

    def test_computed_lazy_evaluation(self) -> None:
        """Computed is lazy - only computes when accessed."""
        call_count = [0]

        def expensive():
            call_count[0] += 1
            return 42

        computed = Computed.of(compute=expensive)
        assert call_count[0] == 0  # Not computed yet

        _ = computed.value  # First access
        assert call_count[0] == 1

        _ = computed.value  # Second access (cached)
        assert call_count[0] == 1  # Still 1, no recompute

    def test_computed_invalidates_on_source_change(self) -> None:
        """Computed invalidates when source signal changes."""
        source = Signal.of(10)
        computed = Computed.of(compute=lambda: source.value * 2, sources=[source])

        assert computed.value == 20

        source.set(15)
        assert computed.value == 30

    def test_computed_multiple_sources(self) -> None:
        """Computed with multiple source signals."""
        a = Signal.of(3)
        b = Signal.of(4)
        computed = Computed.of(
            compute=lambda: a.value + b.value,
            sources=[a, b],
        )

        assert computed.value == 7

        a.set(10)
        assert computed.value == 14

        b.set(20)
        assert computed.value == 30

    def test_computed_dispose_unsubscribes(self) -> None:
        """Computed.dispose() removes all subscriptions."""
        source = Signal.of(5)
        computed = Computed.of(compute=lambda: source.value, sources=[source])

        _ = computed.value  # Access to compute
        computed.dispose()

        # After dispose, should have no subscribers
        assert len(source._subscribers) == 0

    def test_computed_map_chains(self) -> None:
        """Computed.map() creates chained computation."""
        source = Signal.of(2)
        step1 = source.map(lambda x: x * 3)
        step2 = step1.map(lambda x: x + 1)

        assert step1.value == 6
        assert step2.value == 7


class TestEffect:
    """Tests for Effect side-effect container."""

    def test_effect_of_creates_effect(self) -> None:
        """Effect.of() creates effect."""
        ran = [False]

        def side_effect():
            ran[0] = True
            return None

        effect = Effect.of(fn=side_effect)
        assert not ran[0]  # Not run yet

        effect.run()
        assert ran[0]

    def test_effect_marks_dirty_on_source_change(self) -> None:
        """Effect is marked dirty when source changes."""
        source = Signal.of(0)
        effect = Effect.of(fn=lambda: None, sources=[source])

        effect.run()  # Clear dirty flag
        assert not effect.dirty

        source.set(1)
        assert effect.dirty

    def test_effect_run_if_dirty_only_when_dirty(self) -> None:
        """Effect.run_if_dirty() only runs when dirty."""
        run_count = [0]

        def side_effect():
            run_count[0] += 1
            return None

        source = Signal.of(0)
        effect = Effect.of(fn=side_effect, sources=[source])

        effect.run_if_dirty()
        assert run_count[0] == 1

        effect.run_if_dirty()  # Already ran, not dirty
        assert run_count[0] == 1

        source.set(1)  # Makes it dirty
        effect.run_if_dirty()
        assert run_count[0] == 2

    def test_effect_cleanup_called_on_rerun(self) -> None:
        """Cleanup function is called before rerun."""
        cleanup_count = [0]
        run_count = [0]

        def side_effect():
            run_count[0] += 1

            def cleanup():
                cleanup_count[0] += 1

            return cleanup

        effect = Effect.of(fn=side_effect)

        effect.run()
        assert run_count[0] == 1
        assert cleanup_count[0] == 0

        effect.run()  # Cleanup called, then new run
        assert run_count[0] == 2
        assert cleanup_count[0] == 1

    def test_effect_dispose_calls_cleanup(self) -> None:
        """Effect.dispose() calls cleanup and unsubscribes."""
        cleanup_count = [0]
        source = Signal.of(0)

        def side_effect():
            def cleanup():
                cleanup_count[0] += 1

            return cleanup

        effect = Effect.of(fn=side_effect, sources=[source])
        effect.run()

        effect.dispose()
        assert cleanup_count[0] == 1
        assert len(source._subscribers) == 0

    def test_effect_no_cleanup_if_none_returned(self) -> None:
        """No error if effect returns None for cleanup."""
        effect = Effect.of(fn=lambda: None)
        effect.run()
        effect.run()  # Should not error
        effect.dispose()  # Should not error


class TestIntegration:
    """Integration tests for reactive primitives working together."""

    def test_signal_computed_effect_chain(self) -> None:
        """Full chain: Signal -> Computed -> Effect."""
        source = Signal.of(10)
        computed = source.map(lambda x: x * 2)
        log: list[int] = []

        def log_effect():
            log.append(computed.value)
            return None

        effect = Effect.of(fn=log_effect, sources=[source])

        effect.run()
        assert log == [20]

        source.set(25)
        effect.run_if_dirty()
        assert log == [20, 50]

    def test_diamond_dependency(self) -> None:
        """Diamond dependency pattern works correctly."""
        #       source
        #       /    \
        #   left    right
        #       \    /
        #       bottom

        source = Signal.of(1)
        left = source.map(lambda x: x * 2)
        right = source.map(lambda x: x + 10)

        # Can't directly make Computed depend on Computed,
        # but we can compose the computations
        bottom = Computed.of(
            compute=lambda: left.value + right.value,
            sources=[source],
        )

        assert bottom.value == 13  # (1*2) + (1+10) = 2 + 11 = 13

        source.set(5)
        assert bottom.value == 25  # (5*2) + (5+10) = 10 + 15 = 25
