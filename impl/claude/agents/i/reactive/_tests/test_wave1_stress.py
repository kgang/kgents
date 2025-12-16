"""
Wave 1 Stress Tests: Property-based, stress, boundary, and concurrency tests.

Visionary UX Flows TEST Phase (N-Phase 8 of 11).
Tests Signal, Computed, Effect under heavy load and edge cases.
"""

from __future__ import annotations

import random
import time
from typing import Any

import pytest
from agents.i.reactive.signal import Computed, Effect, Signal, Snapshot
from hypothesis import given, settings
from hypothesis import strategies as st

# =============================================================================
# PROPERTY-BASED TESTS (Hypothesis)
# =============================================================================


class TestSignalProperties:
    """Property-based tests for Signal invariants."""

    @given(st.integers())
    def test_snapshot_restore_roundtrip(self, value: int) -> None:
        """Any value can be snapshot and restored."""
        sig = Signal.of(value)
        snap = sig.snapshot()
        sig.set(value + 1)
        sig.restore(snap)
        assert sig.value == value

    @given(
        st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1, max_size=50)
    )
    def test_generation_monotonic(self, values: list[int]) -> None:
        """Generation always increases on distinct value changes."""
        sig = Signal.of(values[0])
        prev_gen = sig.generation
        for v in values[1:]:
            if v != sig.value:
                sig.set(v)
                assert sig.generation > prev_gen
                prev_gen = sig.generation

    @given(st.integers())
    def test_set_same_value_no_generation_increase(self, value: int) -> None:
        """Setting same value does not increase generation."""
        sig = Signal.of(value)
        gen_before = sig.generation
        sig.set(value)  # Same value
        assert sig.generation == gen_before

    @given(st.text(min_size=0, max_size=100))
    def test_signal_text_values(self, text: str) -> None:
        """Signal works with arbitrary text values."""
        sig = Signal.of(text)
        assert sig.value == text
        snap = sig.snapshot()
        sig.set("changed")
        sig.restore(snap)
        assert sig.value == text

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_signal_float_values(self, value: float) -> None:
        """Signal works with float values."""
        sig = Signal.of(value)
        assert sig.value == value

    @given(st.lists(st.integers(), min_size=0, max_size=20))
    def test_signal_list_values(self, value: list[int]) -> None:
        """Signal works with list values (identity comparison)."""
        sig = Signal.of(value)
        assert sig.value == value

    @given(st.integers(min_value=1, max_value=10), st.integers())
    def test_multiple_snapshots_independent(self, count: int, initial: int) -> None:
        """Multiple snapshots from same signal are independent."""
        sig = Signal.of(initial)
        snapshots: list[Snapshot[int]] = []

        for i in range(count):
            sig.set(initial + i)
            snapshots.append(sig.snapshot())

        # All snapshots should have captured different values
        values = [snap.value for snap in snapshots]
        expected = [initial + i for i in range(count)]
        assert values == expected

    @given(st.integers(), st.integers())
    def test_snapshot_captures_generation(self, v1: int, v2: int) -> None:
        """Snapshot captures generation at time of capture."""
        sig = Signal.of(v1)
        gen1 = sig.generation
        snap1 = sig.snapshot()
        assert snap1.generation == gen1

        if v2 != v1:
            sig.set(v2)
            assert snap1.generation == gen1  # Unchanged
            assert sig.generation > gen1


class TestComputedProperties:
    """Property-based tests for Computed invariants."""

    @given(st.integers(min_value=-100, max_value=100))
    def test_computed_map_preserves_value(self, value: int) -> None:
        """Computed.map preserves function application."""
        sig = Signal.of(value)
        computed = sig.map(lambda x: x * 2)
        assert computed.value == value * 2

    @given(
        st.integers(min_value=-10, max_value=10),
        st.integers(min_value=-10, max_value=10),
    )
    def test_computed_multiple_sources(self, a: int, b: int) -> None:
        """Computed with multiple sources tracks both."""
        sig_a = Signal.of(a)
        sig_b = Signal.of(b)
        computed = Computed.of(
            compute=lambda: sig_a.value + sig_b.value,
            sources=[sig_a, sig_b],
        )
        assert computed.value == a + b


class TestEffectProperties:
    """Property-based tests for Effect invariants."""

    @given(st.integers(min_value=1, max_value=20))
    def test_effect_runs_exactly_once_per_dirty(self, n_changes: int) -> None:
        """Effect runs exactly once when dirty, not more."""
        sig = Signal.of(0)
        run_count = [0]

        def fx() -> None:
            run_count[0] += 1
            return None

        effect = Effect.of(fn=fx, sources=[sig])

        # Run once initially
        effect.run_if_dirty()
        assert run_count[0] == 1

        # Make dirty n_changes times, run after each
        for i in range(n_changes):
            sig.set(i + 1)
            effect.run_if_dirty()

        assert run_count[0] == n_changes + 1


# =============================================================================
# STRESS TESTS (High Iteration Counts)
# =============================================================================


class TestSignalStress:
    """Stress tests for Signal under load."""

    def test_signal_1000_snapshots(self) -> None:
        """Signal handles 1000 snapshots without degradation."""
        sig = Signal.of(0)
        snapshots: list[Snapshot[int]] = []

        for i in range(1000):
            sig.set(i)
            snapshots.append(sig.snapshot())

        # Restore 100 random snapshots
        sample = random.sample(snapshots, 100)
        for snap in sample:
            sig.restore(snap)
            assert sig.value == snap.value

    def test_signal_10000_updates(self) -> None:
        """Signal handles 10000 value updates."""
        sig = Signal.of(-1)  # Start with different value

        for i in range(10000):
            sig.set(i)

        assert sig.value == 9999
        assert sig.generation == 10000  # 10000 distinct values

    def test_signal_100_subscribers(self) -> None:
        """Signal handles 100 concurrent subscribers."""
        sig = Signal.of(0)
        results: list[list[int]] = [[] for _ in range(100)]

        # Add 100 subscribers
        unsubs = []
        for i in range(100):
            idx = i

            def callback(v: int, idx: int = idx) -> None:
                results[idx].append(v)

            unsubs.append(sig.subscribe(callback))

        # Update 50 times
        for j in range(1, 51):
            sig.set(j)

        # All subscribers should have received all updates
        for r in results:
            assert r == list(range(1, 51))

        # Cleanup
        for unsub in unsubs:
            unsub()

    def test_signal_rapid_snapshot_restore_cycles(self) -> None:
        """Signal handles rapid snapshot-restore cycles."""
        sig = Signal.of(0)

        for _ in range(1000):
            sig.set(sig.value + 1)
            snap = sig.snapshot()
            sig.set(sig.value + 100)
            sig.restore(snap)

        # Final value should be 1000 (1000 +1 operations, restored each time)
        assert sig.value == 1000

    def test_signal_subscriber_add_remove_stress(self) -> None:
        """Signal handles rapid subscriber add/remove."""
        sig = Signal.of(0)

        for _ in range(1000):
            unsub = sig.subscribe(lambda v: None)
            unsub()

        # Should work normally after stress
        received: list[int] = []
        sig.subscribe(lambda v: received.append(v))
        sig.set(42)
        assert received == [42]


class TestComputedStress:
    """Stress tests for Computed under load."""

    def test_computed_1000_recomputations(self) -> None:
        """Computed handles 1000 recomputations."""
        sig = Signal.of(0)
        computed = sig.map(lambda x: x * 2)

        for i in range(1000):
            sig.set(i)
            assert computed.value == i * 2

    def test_computed_deep_chain(self) -> None:
        """Computed handles deep chains of mappings."""
        sig = Signal.of(1)
        current: Computed[int] | Signal[int] = sig

        # Build chain of 50 maps
        for _ in range(50):
            if isinstance(current, Signal):
                current = current.map(lambda x: x + 1)
            else:
                current = current.map(lambda x: x + 1)

        # Final value should be 1 + 50 = 51
        assert current.value == 51

        # Update source
        sig.set(10)
        assert current.value == 60

    def test_computed_many_sources(self) -> None:
        """Computed handles many source signals."""
        signals = [Signal.of(i) for i in range(50)]
        computed = Computed.of(
            compute=lambda: sum(s.value for s in signals),
            sources=signals,
        )

        assert computed.value == sum(range(50))

        # Update one signal
        signals[25].set(1000)
        assert computed.value == sum(range(50)) - 25 + 1000


class TestEffectStress:
    """Stress tests for Effect under load."""

    def test_effect_1000_runs(self) -> None:
        """Effect handles 1000 runs with cleanup."""
        sig = Signal.of(0)
        run_count = [0]
        cleanup_count = [0]

        def fx() -> Any:
            run_count[0] += 1

            def cleanup() -> None:
                cleanup_count[0] += 1

            return cleanup

        effect = Effect.of(fn=fx, sources=[sig])

        for i in range(1000):
            sig.set(i)
            effect.run_if_dirty()

        assert run_count[0] == 1000
        assert cleanup_count[0] == 999  # First run has no prior cleanup

        effect.dispose()
        assert cleanup_count[0] == 1000  # Dispose calls final cleanup


@pytest.mark.skip(reason="ModalScope removed in data-architecture-rewrite")
class TestModalScopeStress:
    """Stress tests for ModalScope deep nesting."""

    def test_modal_scope_deep_nesting(self) -> None:
        """ModalScope handles 50-deep branch nesting."""
        from agents.d.modal_scope import ModalScope

        root = ModalScope.create_root()
        current = root

        for i in range(50):
            current = current.branch(f"level-{i}", budget=0.99)

        assert current.depth == 50
        assert ":level-49" in current.scope_id

    def test_modal_scope_many_siblings(self) -> None:
        """ModalScope handles many sibling branches."""
        from agents.d.modal_scope import ModalScope

        root = ModalScope.create_root()

        for i in range(100):
            root.branch(f"branch-{i}", budget=0.01)

        assert len(root.children) == 100

    def test_modal_scope_serialization_roundtrip_stress(self) -> None:
        """ModalScope serialization handles complex trees."""
        from agents.d.context_window import TurnRole
        from agents.d.modal_scope import ModalScope

        root = ModalScope.create_root()

        # Build a tree with depth and breadth
        for i in range(10):
            branch = root.branch(f"b{i}", budget=0.1)
            branch.window.append(TurnRole.ASSISTANT, f"Content {i}")
            for j in range(5):
                sub = branch.branch(f"sub{j}", budget=0.1)
                sub.window.append(TurnRole.ASSISTANT, f"Sub content {j}")

        # Serialize and restore
        data = root.to_dict()
        restored = ModalScope.from_dict(data)

        assert len(restored.children) == 10
        for child in restored.children:
            assert len(child.children) == 5


# =============================================================================
# BOUNDARY VALUE TESTS
# =============================================================================


class TestSignalBoundaries:
    """Boundary value tests for Signal."""

    def test_signal_empty_string(self) -> None:
        """Signal handles empty string."""
        sig = Signal.of("")
        assert sig.value == ""
        sig.set("x")
        sig.set("")
        assert sig.value == ""

    def test_signal_none_value(self) -> None:
        """Signal handles None value."""
        sig: Signal[int | None] = Signal.of(None)
        assert sig.value is None
        sig.set(42)
        sig.set(None)
        assert sig.value is None

    def test_signal_zero_generation(self) -> None:
        """New signal starts at generation 0."""
        sig = Signal.of(0)
        assert sig.generation == 0

    def test_signal_large_value(self) -> None:
        """Signal handles very large values."""
        big = 10**100
        sig = Signal.of(big)
        assert sig.value == big

    def test_signal_negative_value(self) -> None:
        """Signal handles negative values."""
        sig = Signal.of(-999)
        assert sig.value == -999


class TestEntropyBoundaries:
    """Boundary value tests for entropy functions."""

    @pytest.mark.parametrize("entropy", [0.0, 0.5, 1.0, 0.001, 0.999])
    def test_entropy_boundary_values(self, entropy: float) -> None:
        """entropy_to_distortion handles boundary values."""
        from agents.i.reactive.entropy import entropy_to_distortion

        distortion = entropy_to_distortion(entropy, seed=42, t=0.0)
        # All outputs should be finite floats
        assert isinstance(distortion.blur, float)
        assert isinstance(distortion.skew, float)
        assert isinstance(distortion.pulse, float)

    @pytest.mark.parametrize("entropy", [-0.5, -1.0, 1.5, 2.0, 100.0])
    def test_entropy_clamping(self, entropy: float) -> None:
        """Out-of-bounds entropy is clamped."""
        from agents.i.reactive.entropy import entropy_to_distortion

        distortion = entropy_to_distortion(entropy, seed=42, t=0.0)
        # Should not raise, values should be clamped
        assert distortion is not None

    @pytest.mark.parametrize("seed", [0, -1, 1, 2**31 - 1, 2**31])
    def test_entropy_seed_boundaries(self, seed: int) -> None:
        """entropy_to_distortion handles boundary seed values."""
        from agents.i.reactive.entropy import entropy_to_distortion

        distortion = entropy_to_distortion(0.5, seed=seed, t=0.0)
        assert distortion is not None

    @pytest.mark.parametrize("t", [0.0, 0.001, 1000.0, 1e10, -100.0])
    def test_entropy_time_boundaries(self, t: float) -> None:
        """entropy_to_distortion handles boundary time values."""
        from agents.i.reactive.entropy import entropy_to_distortion

        distortion = entropy_to_distortion(0.5, seed=42, t=t)
        assert distortion is not None


class TestTurnBoundaries:
    """Boundary value tests for Turn."""

    def test_turn_empty_content(self) -> None:
        """Turn handles empty content."""
        from protocols.api.turn import Turn

        turn = Turn(speaker="test", content="", timestamp=0.0)
        assert turn.to_cli() == "[test]: "

    def test_turn_empty_speaker(self) -> None:
        """Turn handles empty speaker."""
        from protocols.api.turn import Turn

        turn = Turn(speaker="", content="Hello", timestamp=0.0)
        assert turn.to_cli() == "[]: Hello"

    def test_turn_unicode_content(self) -> None:
        """Turn handles unicode/emoji content."""
        from protocols.api.turn import Turn

        turn = Turn(speaker="🤖", content="Hello 世界! 🌍", timestamp=0.0)
        cli = turn.to_cli()
        assert "🤖" in cli
        assert "世界" in cli
        assert "🌍" in cli

    def test_turn_very_long_content(self) -> None:
        """Turn handles very long content."""
        from protocols.api.turn import Turn

        long_content = "x" * 100000
        turn = Turn(speaker="user", content=long_content, timestamp=0.0)
        assert len(turn.content) == 100000
        assert turn.to_cli() == f"[user]: {long_content}"

    def test_turn_zero_timestamp(self) -> None:
        """Turn handles zero timestamp."""
        from protocols.api.turn import Turn

        turn = Turn(speaker="user", content="Hi", timestamp=0.0)
        assert turn.timestamp == 0.0

    def test_turn_negative_timestamp(self) -> None:
        """Turn handles negative timestamp."""
        from protocols.api.turn import Turn

        turn = Turn(speaker="user", content="Hi", timestamp=-1000.0)
        assert turn.timestamp == -1000.0

    def test_turn_large_timestamp(self) -> None:
        """Turn handles very large timestamp."""
        from protocols.api.turn import Turn

        turn = Turn(speaker="user", content="Hi", timestamp=1e15)
        assert turn.timestamp == 1e15


# =============================================================================
# PERFORMANCE BASELINE TESTS
# =============================================================================


class TestPerformanceBaselines:
    """Performance baseline tests to detect regressions."""

    def test_signal_snapshot_performance(self) -> None:
        """Signal snapshot/restore should be fast."""
        sig = Signal.of(0)

        start = time.perf_counter()
        for i in range(10000):
            sig.set(i)
            snap = sig.snapshot()
            sig.restore(snap)
        elapsed = time.perf_counter() - start

        # Should complete 10000 cycles in under 1 second
        assert elapsed < 1.0, f"Signal snapshot cycle too slow: {elapsed:.3f}s"

    def test_computed_recompute_performance(self) -> None:
        """Computed recomputation should be fast."""
        sig = Signal.of(0)
        computed = sig.map(lambda x: x * 2 + 1)

        start = time.perf_counter()
        for i in range(10000):
            sig.set(i)
            _ = computed.value
        elapsed = time.perf_counter() - start

        # Should complete 10000 recomputes in under 1 second
        assert elapsed < 1.0, f"Computed recompute too slow: {elapsed:.3f}s"

    def test_subscriber_notification_performance(self) -> None:
        """Subscriber notifications should be fast."""
        sig = Signal.of(-1)  # Start with different value
        count = [0]

        for _ in range(10):
            sig.subscribe(lambda v: count.__setitem__(0, count[0] + 1))

        start = time.perf_counter()
        for i in range(10000):
            sig.set(i)
        elapsed = time.perf_counter() - start

        # Should complete 10000 updates with 10 subscribers in under 1 second
        assert elapsed < 1.0, f"Subscriber notification too slow: {elapsed:.3f}s"
        assert count[0] == 100000  # 10 subscribers * 10000 updates

    @pytest.mark.skip(reason="ModalScope removed in data-architecture-rewrite")
    def test_modal_scope_branch_performance(self) -> None:
        """ModalScope branching should be fast."""
        pass


# =============================================================================
# COMPOSITION STRESS TESTS (Wave 2.1)
# =============================================================================


class TestCompositionStress:
    """Stress tests for >> and // composition operators."""

    def test_composition_deep_horizontal_chain(self) -> None:
        """Test deep >> chain (100 widgets)."""
        from agents.i.reactive.composable import ComposableWidget, HStack
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        widgets = [GlyphWidget(GlyphState(char=chr(65 + (i % 26)))) for i in range(100)]

        # Build chain via >> operator
        result: ComposableWidget = widgets[0]
        for w in widgets[1:]:
            result = result >> w

        assert isinstance(result, HStack)
        assert len(result.children) == 100

    def test_composition_deep_vertical_chain(self) -> None:
        """Test deep // chain (100 widgets)."""
        from agents.i.reactive.composable import ComposableWidget, VStack
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        widgets = [GlyphWidget(GlyphState(char=chr(65 + (i % 26)))) for i in range(100)]

        # Build chain via // operator
        result: ComposableWidget = widgets[0]
        for w in widgets[1:]:
            result = result // w

        assert isinstance(result, VStack)
        assert len(result.children) == 100

    def test_composition_mixed_deep_nesting(self) -> None:
        """Test mixed >> and // in deep nesting (50 levels)."""
        from agents.i.reactive.composable import ComposableWidget, HStack, VStack
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget

        # Build alternating pattern: (a >> b) // (c >> d) // ...
        result: ComposableWidget = GlyphWidget(GlyphState(char="A")) >> GlyphWidget(
            GlyphState(char="B")
        )

        for i in range(50):
            row = GlyphWidget(GlyphState(char=chr(65 + (i % 26)))) >> GlyphWidget(
                GlyphState(char=chr(97 + (i % 26)))
            )
            result = result // row

        assert isinstance(result, VStack)
        assert len(result.children) == 51  # Original + 50 rows

    def test_composition_render_performance(self) -> None:
        """Composition of 100 widgets renders in under 100ms."""
        from agents.i.reactive.composable import ComposableWidget
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
        from agents.i.reactive.widget import RenderTarget

        widgets = [GlyphWidget(GlyphState(char=chr(65 + (i % 26)))) for i in range(100)]

        result: ComposableWidget = widgets[0]
        for w in widgets[1:]:
            result = result >> w

        start = time.perf_counter()
        for _ in range(100):
            result.project(RenderTarget.CLI)
            result.project(RenderTarget.JSON)
        elapsed = time.perf_counter() - start

        # 200 renders (100 CLI + 100 JSON) should complete in under 1 second
        assert elapsed < 1.0, f"Composition render too slow: {elapsed:.3f}s"

    def test_composition_json_large_tree(self) -> None:
        """JSON projection of large composition tree."""
        from agents.i.reactive.composable import ComposableWidget, HStack, VStack
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
        from agents.i.reactive.widget import RenderTarget

        # Build 10x10 grid
        rows: list[ComposableWidget] = []
        for i in range(10):
            row: ComposableWidget = GlyphWidget(GlyphState(char=str(i)))
            for j in range(9):
                row = row >> GlyphWidget(GlyphState(char=str(j)))
            rows.append(row)

        grid: ComposableWidget = rows[0]
        for r in rows[1:]:
            grid = grid // r

        json_out = grid.project(RenderTarget.JSON)

        assert json_out["type"] == "vstack"
        assert len(json_out["children"]) == 10
        for child in json_out["children"]:
            assert child["type"] == "hstack"
            assert len(child["children"]) == 10


class TestPresetStress:
    """Stress tests for preset layout functions."""

    def test_metric_row_many_bars(self) -> None:
        """metric_row with 50 BarWidgets."""
        from agents.i.reactive.presets import metric_row
        from agents.i.reactive.primitives.bar import BarState, BarWidget
        from agents.i.reactive.widget import RenderTarget

        bars = [BarWidget(BarState(value=i / 50.0, label=f"B{i}")) for i in range(50)]
        result = metric_row(*bars)

        assert len(result.children) == 50

        # Should render without error
        cli = result.project(RenderTarget.CLI)
        assert len(cli) > 0

    def test_metric_stack_many_rows(self) -> None:
        """metric_stack with 50 metric_rows."""
        from agents.i.reactive.presets import metric_row, metric_stack
        from agents.i.reactive.primitives.bar import BarState, BarWidget
        from agents.i.reactive.widget import RenderTarget

        rows = [
            metric_row(
                BarWidget(BarState(value=0.3, label="A")),
                BarWidget(BarState(value=0.7, label="B")),
            )
            for _ in range(50)
        ]
        result = metric_stack(*rows)

        assert len(result.children) == 50

        # Should render without error
        cli = result.project(RenderTarget.CLI)
        lines = cli.split("\n")
        assert len(lines) >= 50

    def test_status_row_all_phases_performance(self) -> None:
        """status_row for all phases renders quickly."""
        from agents.i.reactive.presets import status_row
        from agents.i.reactive.widget import RenderTarget

        phases = [
            "PLAN",
            "RESEARCH",
            "DEVELOP",
            "STRATEGIZE",
            "CROSS-SYNERGIZE",
            "IMPLEMENT",
            "QA",
            "TEST",
            "EDUCATE",
            "MEASURE",
            "REFLECT",
        ]

        start = time.perf_counter()
        for _ in range(100):
            for phase in phases:
                row = status_row(phase, f"Working on {phase}", 0.5)
                row.project(RenderTarget.CLI)
        elapsed = time.perf_counter() - start

        # 1100 renders (100 iterations * 11 phases) should complete in under 1 second
        assert elapsed < 1.0, f"status_row render too slow: {elapsed:.3f}s"

    def test_dashboard_composition_stress(self) -> None:
        """Full dashboard layout under stress."""
        from agents.i.reactive.presets import (
            labeled,
            metric_row,
            metric_stack,
            panel,
            status_row,
        )
        from agents.i.reactive.primitives.bar import BarState, BarWidget
        from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
        from agents.i.reactive.widget import RenderTarget

        # Build complex dashboard 50 times
        start = time.perf_counter()
        for _ in range(50):
            header = GlyphWidget(GlyphState(char="═══ Agent Dashboard ═══"))

            statuses = metric_stack(
                status_row("SENSE", "Scanning", 0.9),
                status_row("ACT", "Processing", 0.5),
                status_row("REFLECT", "Complete", 1.0),
            )

            metrics = metric_row(
                labeled("CPU:", BarWidget(BarState(value=0.6, width=10))),
                labeled("MEM:", BarWidget(BarState(value=0.4, width=10))),
                labeled("IO:", BarWidget(BarState(value=0.8, width=10))),
            )

            dashboard = panel(header, metric_stack(statuses, metrics), gap=1)
            dashboard.project(RenderTarget.CLI)
            dashboard.project(RenderTarget.JSON)

        elapsed = time.perf_counter() - start

        # 100 renders (50 CLI + 50 JSON) of complex dashboard in under 2 seconds
        assert elapsed < 2.0, f"Dashboard composition too slow: {elapsed:.3f}s"
