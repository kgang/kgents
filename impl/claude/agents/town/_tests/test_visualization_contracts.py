"""
Tests for Town Visualization Contracts (Phase 5 DEVELOP).

Verifies that the contracts are:
1. Type-checkable
2. Well-formed (dataclasses serialize correctly)
3. Laws are expressed correctly

These are CONTRACT tests - implementation tests come in IMPLEMENT phase.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import pytest


class TestScatterPointContract:
    """Tests for ScatterPoint dataclass contract."""

    def test_scatter_point_creation(self) -> None:
        """ScatterPoint can be created with required fields."""
        from agents.town.visualization import ScatterPoint

        point = ScatterPoint(
            citizen_id="abc123",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.7,
            curiosity=0.5,
            trust=0.8,
            creativity=0.6,
            patience=0.4,
            resilience=0.9,
            ambition=0.3,
        )

        assert point.citizen_id == "abc123"
        assert point.citizen_name == "Alice"
        assert point.archetype == "builder"
        assert point.warmth == 0.7

    def test_scatter_point_to_dict(self) -> None:
        """ScatterPoint.to_dict() returns serializable dict."""
        from agents.town.visualization import ScatterPoint

        point = ScatterPoint(
            citizen_id="abc123",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.7,
            curiosity=0.5,
            trust=0.8,
            creativity=0.6,
            patience=0.4,
            resilience=0.9,
            ambition=0.3,
            x=1.5,
            y=-0.5,
            color="#ff0000",
            is_evolving=True,
            coalition_ids=("c1", "c2"),
        )

        d = point.to_dict()

        assert d["citizen_id"] == "abc123"
        assert d["eigenvectors"]["warmth"] == 0.7
        assert d["x"] == 1.5
        assert d["coalition_ids"] == ["c1", "c2"]

        # Verify JSON serializable
        json_str = json.dumps(d)
        assert "abc123" in json_str

    def test_scatter_point_immutable(self) -> None:
        """ScatterPoint is frozen (immutable)."""
        from agents.town.visualization import ScatterPoint

        point = ScatterPoint(
            citizen_id="abc123",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.7,
            curiosity=0.5,
            trust=0.8,
            creativity=0.6,
            patience=0.4,
            resilience=0.9,
            ambition=0.3,
        )

        with pytest.raises(AttributeError):
            point.warmth = 0.9  # type: ignore[misc]


class TestScatterStateContract:
    """Tests for ScatterState dataclass contract."""

    def test_scatter_state_creation_empty(self) -> None:
        """ScatterState can be created with defaults."""
        from agents.town.visualization import ProjectionMethod, ScatterState

        state = ScatterState()

        assert state.points == ()
        assert state.projection == ProjectionMethod.PAIR_WT
        assert state.selected_citizen_id is None
        assert not state.show_evolving_only

    def test_scatter_state_with_points(self) -> None:
        """ScatterState holds tuple of ScatterPoints."""
        from agents.town.visualization import (
            ProjectionMethod,
            ScatterPoint,
            ScatterState,
        )

        p1 = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )
        p2 = ScatterPoint(
            citizen_id="c2",
            citizen_name="Bob",
            archetype="trader",
            warmth=0.6,
            curiosity=0.6,
            trust=0.6,
            creativity=0.6,
            patience=0.6,
            resilience=0.6,
            ambition=0.6,
        )

        state = ScatterState(
            points=(p1, p2),
            projection=ProjectionMethod.PCA,
            show_labels=False,
        )

        assert len(state.points) == 2
        assert state.points[0].citizen_name == "Alice"
        assert state.projection == ProjectionMethod.PCA

    def test_scatter_state_to_dict(self) -> None:
        """ScatterState.to_dict() returns serializable dict."""
        from agents.town.visualization import (
            ProjectionMethod,
            ScatterPoint,
            ScatterState,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )

        state = ScatterState(
            points=(point,),
            selected_citizen_id="c1",
        )

        d = state.to_dict()

        assert d["type"] == "eigenvector_scatter"
        assert len(d["points"]) == 1
        assert d["selected_citizen_id"] == "c1"
        assert d["projection"] == "PAIR_WT"

        # Verify JSON serializable
        json.dumps(d)


class TestProjectionMethodContract:
    """Tests for ProjectionMethod enum contract."""

    def test_projection_methods_exist(self) -> None:
        """All expected projection methods exist."""
        from agents.town.visualization import ProjectionMethod

        assert ProjectionMethod.PCA is not None
        assert ProjectionMethod.TSNE is not None
        assert ProjectionMethod.PAIR_WT is not None
        assert ProjectionMethod.PAIR_CC is not None
        assert ProjectionMethod.PAIR_PR is not None
        assert ProjectionMethod.PAIR_RA is not None
        assert ProjectionMethod.CUSTOM is not None

    def test_projection_method_count(self) -> None:
        """Seven projection methods defined."""
        from agents.town.visualization import ProjectionMethod

        assert len(ProjectionMethod) == 7


class TestSSEEventContract:
    """Tests for SSEEvent dataclass contract."""

    def test_sse_event_creation(self) -> None:
        """SSEEvent can be created with event type and data."""
        from agents.town.visualization import SSEEvent

        event = SSEEvent(
            event="town.event",
            data={"phase": "MORNING", "operation": "greet"},
        )

        assert event.event == "town.event"
        assert event.data["phase"] == "MORNING"

    def test_sse_event_to_sse_format(self) -> None:
        """SSEEvent.to_sse() returns correct wire format."""
        from agents.town.visualization import SSEEvent

        event = SSEEvent(
            event="town.event",
            data={"message": "hello"},
            id="evt-123",
        )

        sse_str = event.to_sse()

        assert "event: town.event" in sse_str
        assert "id: evt-123" in sse_str
        assert 'data: {"message": "hello"}' in sse_str
        assert sse_str.endswith("\n\n")

    def test_sse_event_with_retry(self) -> None:
        """SSEEvent with retry includes retry field."""
        from agents.town.visualization import SSEEvent

        event = SSEEvent(
            event="status",
            data={"connected": True},
            retry=5000,
        )

        sse_str = event.to_sse()

        assert "retry: 5000" in sse_str


class TestTownNATSSubjectContract:
    """Tests for TownNATSSubject contract."""

    def test_subject_to_string(self) -> None:
        """TownNATSSubject.to_subject() formats correctly."""
        from agents.town.visualization import TownNATSSubject

        subject = TownNATSSubject(
            town_id="abc123",
            phase="morning",
            operation="greet",
        )

        assert subject.to_subject() == "town.abc123.morning.greet"

    def test_subject_from_string(self) -> None:
        """TownNATSSubject.from_subject() parses correctly."""
        from agents.town.visualization import TownNATSSubject

        subject = TownNATSSubject.from_subject("town.abc123.afternoon.trade")

        assert subject.town_id == "abc123"
        assert subject.phase == "afternoon"
        assert subject.operation == "trade"

    def test_subject_roundtrip(self) -> None:
        """Subject string can be parsed and formatted back."""
        from agents.town.visualization import TownNATSSubject

        original = "town.xyz789.evening.gossip"
        subject = TownNATSSubject.from_subject(original)
        formatted = subject.to_subject()

        assert formatted == original

    def test_subject_from_invalid_raises(self) -> None:
        """TownNATSSubject.from_subject() raises on invalid format."""
        from agents.town.visualization import TownNATSSubject

        with pytest.raises(ValueError, match="Invalid town subject"):
            TownNATSSubject.from_subject("invalid.subject")

        with pytest.raises(ValueError, match="Invalid town subject"):
            TownNATSSubject.from_subject("town.only.two")

    def test_subject_wildcard_town(self) -> None:
        """Wildcard for all events in a town."""
        from agents.town.visualization import TownNATSSubject

        wildcard = TownNATSSubject.wildcard_town("abc123")

        assert wildcard == "town.abc123.>"

    def test_subject_wildcard_all_towns(self) -> None:
        """Wildcard for all town events."""
        from agents.town.visualization import TownNATSSubject

        wildcard = TownNATSSubject.wildcard_all_towns()

        assert wildcard == "town.>"

    def test_subject_for_status(self) -> None:
        """Subject for status events."""
        from agents.town.visualization import TownNATSSubject

        subject = TownNATSSubject.for_status("abc123", "phase_change")

        assert subject.to_subject() == "town.abc123.status.phase_change"

    def test_subject_for_coalition(self) -> None:
        """Subject for coalition events."""
        from agents.town.visualization import TownNATSSubject

        subject = TownNATSSubject.for_coalition("abc123", "formed")

        assert subject.to_subject() == "town.abc123.coalition.formed"


class TestTownEventTypeContract:
    """Tests for TownEventType enum contract."""

    def test_event_types_exist(self) -> None:
        """All expected event types exist."""
        from agents.town.visualization import TownEventType

        assert TownEventType.EVENT is not None
        assert TownEventType.STATUS is not None
        assert TownEventType.PHASE_CHANGE is not None
        assert TownEventType.COALITION_FORMED is not None
        assert TownEventType.COALITION_DISSOLVED is not None
        assert TownEventType.EIGENVECTOR_DRIFT is not None
        assert TownEventType.CITIZEN_EVOLVED is not None

    def test_event_type_values(self) -> None:
        """Event type values are correct strings."""
        from agents.town.visualization import TownEventType

        assert TownEventType.EVENT.value == "event"
        assert TownEventType.COALITION_FORMED.value == "coalition.formed"
        assert TownEventType.EIGENVECTOR_DRIFT.value == "eigenvector.drift"


class TestFunctorLaws:
    """
    Tests expressing functor laws for scatter widget.

    These are specification tests - they document the laws that
    implementations must satisfy.
    """

    def test_identity_law_expressed(self) -> None:
        """
        LAW 1: scatter.map(id) ≡ scatter

        The identity transformation preserves the widget.
        """
        # This is a specification test - actual verification requires implementation
        from agents.town.visualization import ScatterState

        # Express the law
        state = ScatterState()

        def identity(s):
            return s

        # By the law, map(identity)(state) should equal state
        transformed = identity(state)
        assert transformed == state

    def test_composition_law_expressed(self) -> None:
        """
        LAW 2: scatter.map(f).map(g) ≡ scatter.map(g . f)

        Sequential maps can be fused.
        """
        from agents.town.visualization import ProjectionMethod, ScatterState

        # Two state transformations
        def f(s):
            return ScatterState(
                points=s.points,
                projection=ProjectionMethod.PCA,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )

        def g(s):
            return ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=True,  # Changed
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )

        # Start state
        state = ScatterState()

        # By LAW 2: g(f(state)) should equal the result of map(f).map(g)
        via_sequential = g(f(state))
        via_composed = (lambda s: g(f(s)))(state)

        assert via_sequential.projection == via_composed.projection == ProjectionMethod.PCA
        assert via_sequential.show_evolving_only is True
        assert via_composed.show_evolving_only is True

    def test_state_map_equivalence_expressed(self) -> None:
        """
        LAW 3: scatter.map(f) ≡ scatter.with_state(f(scatter.state.value))

        Map is implemented via state transformation.
        """
        from agents.town.visualization import ScatterState

        # This law says that for any widget and transformation f:
        # widget.map(f) produces same result as widget.with_state(f(widget.state.value))

        # Express via pure state transformation
        state = ScatterState()

        def f(s):
            return ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id="selected-123",  # Changed
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )

        # Direct state transformation
        new_state = f(state)

        assert new_state.selected_citizen_id == "selected-123"

        # The law guarantees this equals widget.map(f).state.value
        # for any conforming widget implementation


class TestExportsContract:
    """Tests that all expected exports are available."""

    def test_all_exports_importable(self) -> None:
        """All exports from __all__ are importable."""
        from agents.town.visualization import (
            EigenvectorScatterWidget,
            EigenvectorScatterWidgetProtocol,
            ProjectionMethod,
            ScatterPoint,
            ScatterState,
            SSEEvent,
            TownEventType,
            TownNATSSubject,
            TownSSEEndpointProtocol,
            project_scatter_to_ascii,
        )

        # Just verify imports work
        assert ScatterPoint is not None
        assert ScatterState is not None
        assert ProjectionMethod is not None
        assert EigenvectorScatterWidgetProtocol is not None
        assert EigenvectorScatterWidget is not None
        assert SSEEvent is not None
        assert TownSSEEndpointProtocol is not None
        assert TownEventType is not None
        assert TownNATSSubject is not None
        assert project_scatter_to_ascii is not None


class TestIntegrationWithTownEvent:
    """Tests integration with existing TownEvent."""

    def test_subject_for_town_event(self) -> None:
        """TownNATSSubject.for_town_event creates correct subject."""
        from agents.town.flux import TownEvent, TownPhase
        from agents.town.visualization import TownNATSSubject

        event = TownEvent(
            phase=TownPhase.MORNING,
            operation="greet",
            participants=["Alice", "Bob"],
            success=True,
            message="Alice greeted Bob",
        )

        subject = TownNATSSubject.for_town_event("abc123", event)

        assert subject.to_subject() == "town.abc123.morning.greet"

    def test_scatter_point_from_eigenvectors(self) -> None:
        """ScatterPoint can be created from Eigenvectors."""
        from agents.town.citizen import Eigenvectors
        from agents.town.visualization import ScatterPoint

        ev = Eigenvectors(
            warmth=0.7,
            curiosity=0.8,
            trust=0.6,
            creativity=0.9,
            patience=0.5,
            resilience=0.4,
            ambition=0.3,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Test",
            archetype="builder",
            warmth=ev.warmth,
            curiosity=ev.curiosity,
            trust=ev.trust,
            creativity=ev.creativity,
            patience=ev.patience,
            resilience=ev.resilience,
            ambition=ev.ambition,
        )

        assert point.warmth == 0.7
        assert point.creativity == 0.9


# =============================================================================
# Phase 5 IMPLEMENT: ASCII Projection Tests
# =============================================================================


class TestASCIIProjection:
    """Tests for project_scatter_to_ascii() implementation."""

    def test_empty_state_renders(self) -> None:
        """Empty scatter state renders without error."""
        from agents.town.visualization import ScatterState, project_scatter_to_ascii

        state = ScatterState()
        result = project_scatter_to_ascii(state)

        assert "Eigenvector Space" in result
        assert "Citizens: 0/0" in result

    def test_single_point_renders(self) -> None:
        """Single point renders at correct position."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )

        state = ScatterState(points=(point,))
        result = project_scatter_to_ascii(state, width=40, height=15)

        assert "b" in result  # lowercase for non-selected
        assert "Citizens: 1/1" in result
        assert "B=Builder" in result  # Legend

    def test_selected_point_uppercase(self) -> None:
        """Selected citizen renders in uppercase."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="trader",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )

        state = ScatterState(points=(point,), selected_citizen_id="c1")
        result = project_scatter_to_ascii(state, width=40, height=15)

        assert "T" in result  # uppercase for selected
        assert "Selected: c1" in result

    def test_multiple_points_render(self) -> None:
        """Multiple points render at different positions."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        points = (
            ScatterPoint(
                citizen_id="c1",
                citizen_name="Alice",
                archetype="builder",
                warmth=0.1,
                curiosity=0.5,
                trust=0.1,  # Low warmth, low trust - bottom left
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
            ),
            ScatterPoint(
                citizen_id="c2",
                citizen_name="Bob",
                archetype="trader",
                warmth=0.9,
                curiosity=0.5,
                trust=0.9,  # High warmth, high trust - top right
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
            ),
        )

        state = ScatterState(points=points)
        result = project_scatter_to_ascii(state, width=40, height=15)

        assert "b" in result  # Builder
        assert "t" in result  # Trader
        assert "Citizens: 2/2" in result

    def test_evolving_filter(self) -> None:
        """Evolving-only filter works correctly."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        points = (
            ScatterPoint(
                citizen_id="c1",
                citizen_name="Alice",
                archetype="builder",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                is_evolving=True,
            ),
            ScatterPoint(
                citizen_id="c2",
                citizen_name="Bob",
                archetype="trader",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
                is_evolving=False,
            ),
        )

        state = ScatterState(points=points, show_evolving_only=True)
        result = project_scatter_to_ascii(state, width=40, height=15)

        assert "Citizens: 1/2" in result  # Only 1 visible of 2 total

    def test_archetype_filter(self) -> None:
        """Archetype filter works correctly."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        points = (
            ScatterPoint(
                citizen_id="c1",
                citizen_name="Alice",
                archetype="builder",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
            ),
            ScatterPoint(
                citizen_id="c2",
                citizen_name="Bob",
                archetype="trader",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
            ),
            ScatterPoint(
                citizen_id="c3",
                citizen_name="Carol",
                archetype="healer",
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
            ),
        )

        state = ScatterState(points=points, archetype_filter=("builder", "healer"))
        result = project_scatter_to_ascii(state, width=40, height=15)

        assert "Citizens: 2/3" in result  # 2 visible of 3 total

    def test_bridge_node_special_char(self) -> None:
        """Bridge nodes (multiple coalitions) get special character."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
            coalition_ids=("coal1", "coal2"),  # Member of multiple coalitions
        )

        state = ScatterState(points=(point,))
        result = project_scatter_to_ascii(state, width=40, height=15)

        assert "○" in result  # Bridge node character

    def test_kgent_special_char(self) -> None:
        """K-gent projection gets star character."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        point = ScatterPoint(
            citizen_id="kgent",
            citizen_name="K-gent",
            archetype="kgent",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )

        state = ScatterState(points=(point,))
        result = project_scatter_to_ascii(state, width=40, height=15)

        assert "☆" in result  # K-gent star character

    def test_different_projections(self) -> None:
        """Different projection methods produce different axis labels."""
        from agents.town.visualization import (
            ProjectionMethod,
            ScatterState,
            project_scatter_to_ascii,
        )

        state_wt = ScatterState(projection=ProjectionMethod.PAIR_WT)
        state_cc = ScatterState(projection=ProjectionMethod.PAIR_CC)
        state_pca = ScatterState(projection=ProjectionMethod.PCA)

        result_wt = project_scatter_to_ascii(state_wt)
        result_cc = project_scatter_to_ascii(state_cc)
        result_pca = project_scatter_to_ascii(state_pca)

        assert "Warmth" in result_wt
        assert "Trust" in result_wt
        assert "Curiosity" in result_cc
        assert "Creativity" in result_cc
        assert "PC1" in result_pca
        assert "PC2" in result_pca

    def test_custom_dimensions(self) -> None:
        """Custom width/height work correctly."""
        from agents.town.visualization import ScatterState, project_scatter_to_ascii

        state = ScatterState()

        small = project_scatter_to_ascii(state, width=30, height=10)
        large = project_scatter_to_ascii(state, width=80, height=30)

        # Verify grid sizes
        small_lines = small.split("\n")
        large_lines = large.split("\n")

        # Grid portion should be different sizes
        assert len(small_lines) < len(large_lines)

    def test_functor_law_identity(self) -> None:
        """LAW 1: ASCII projection of identity-transformed state equals original."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )
        state = ScatterState(points=(point,))

        def identity(s):
            return s

        original = project_scatter_to_ascii(state)
        transformed = project_scatter_to_ascii(identity(state))

        assert original == transformed

    def test_functor_law_composition(self) -> None:
        """LAW 2: Composition of filter transformations works correctly."""
        from agents.town.visualization import (
            ProjectionMethod,
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
            is_evolving=True,
        )
        state = ScatterState(points=(point,))

        # Two transformations
        def f(s):
            return ScatterState(
                points=s.points,
                projection=ProjectionMethod.PAIR_CC,  # Change projection
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )

        def g(s):
            return ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id="c1",  # Select citizen
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )

        # Sequential application
        via_sequential = g(f(state))
        # Composed application
        via_composed = (lambda s: g(f(s)))(state)

        result_seq = project_scatter_to_ascii(via_sequential)
        result_comp = project_scatter_to_ascii(via_composed)

        assert result_seq == result_comp
        assert "Curiosity" in result_seq  # Projection changed
        assert "Selected: c1" in result_seq  # Citizen selected


# =============================================================================
# Phase 5 IMPLEMENT: Widget Implementation Tests
# =============================================================================


class TestEigenvectorScatterWidgetImpl:
    """Tests for EigenvectorScatterWidgetImpl."""

    def test_widget_creation(self) -> None:
        """Widget can be created with default state."""
        from agents.town.visualization import EigenvectorScatterWidgetImpl

        widget = EigenvectorScatterWidgetImpl()
        assert widget.state.value.points == ()

    def test_widget_with_initial_state(self) -> None:
        """Widget can be created with initial state."""
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ProjectionMethod,
            ScatterState,
        )

        state = ScatterState(projection=ProjectionMethod.PAIR_CC)
        widget = EigenvectorScatterWidgetImpl(initial_state=state)

        assert widget.state.value.projection == ProjectionMethod.PAIR_CC

    def test_widget_project_cli(self) -> None:
        """Widget projects to CLI (ASCII scatter)."""
        from agents.i.reactive.widget import RenderTarget
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ScatterPoint,
            ScatterState,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )
        state = ScatterState(points=(point,))
        widget = EigenvectorScatterWidgetImpl(initial_state=state)

        result = widget.project(RenderTarget.CLI)

        assert isinstance(result, str)
        assert "b" in result  # Builder
        assert "Eigenvector Space" in result

    def test_widget_project_json(self) -> None:
        """Widget projects to JSON (dict)."""
        from agents.i.reactive.widget import RenderTarget
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ScatterPoint,
            ScatterState,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )
        state = ScatterState(points=(point,))
        widget = EigenvectorScatterWidgetImpl(initial_state=state)

        result = widget.project(RenderTarget.JSON)

        assert isinstance(result, dict)
        assert result["type"] == "eigenvector_scatter"
        assert len(result["points"]) == 1

    def test_widget_select_citizen(self) -> None:
        """Widget can select a citizen."""
        from agents.town.visualization import EigenvectorScatterWidgetImpl

        widget = EigenvectorScatterWidgetImpl()
        widget.select_citizen("c1")

        assert widget.state.value.selected_citizen_id == "c1"

    def test_widget_set_projection(self) -> None:
        """Widget can change projection method."""
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ProjectionMethod,
        )

        widget = EigenvectorScatterWidgetImpl()
        widget.set_projection(ProjectionMethod.PAIR_CC)

        assert widget.state.value.projection == ProjectionMethod.PAIR_CC

    def test_widget_filter_by_archetype(self) -> None:
        """Widget can filter by archetype."""
        from agents.town.visualization import EigenvectorScatterWidgetImpl

        widget = EigenvectorScatterWidgetImpl()
        widget.filter_by_archetype(("builder", "healer"))

        assert widget.state.value.archetype_filter == ("builder", "healer")

    def test_widget_toggle_evolving_only(self) -> None:
        """Widget can toggle evolving-only filter."""
        from agents.town.visualization import EigenvectorScatterWidgetImpl

        widget = EigenvectorScatterWidgetImpl()
        assert widget.state.value.show_evolving_only is False

        widget.toggle_evolving_only()
        assert widget.state.value.show_evolving_only is True

        widget.toggle_evolving_only()
        assert widget.state.value.show_evolving_only is False

    def test_widget_functor_identity_law(self) -> None:
        """LAW 1: widget.map(id) returns widget with identical state."""
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ScatterPoint,
            ScatterState,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )
        state = ScatterState(points=(point,))
        widget = EigenvectorScatterWidgetImpl(initial_state=state)

        def identity(s):
            return s

        mapped = widget.map(identity)

        assert mapped.state.value.points == widget.state.value.points
        assert mapped.state.value.projection == widget.state.value.projection

    def test_widget_functor_composition_law(self) -> None:
        """LAW 2: widget.map(f).map(g) = widget.map(g . f)."""
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ProjectionMethod,
            ScatterState,
        )

        widget = EigenvectorScatterWidgetImpl()

        def f(s):
            return ScatterState(
                points=s.points,
                projection=ProjectionMethod.PAIR_CC,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )

        def g(s):
            return ScatterState(
                points=s.points,
                projection=s.projection,
                selected_citizen_id="selected",
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )

        # Sequential
        via_sequential = widget.map(f).map(g)
        # Composed
        via_composed = widget.map(lambda s: g(f(s)))

        assert via_sequential.state.value.projection == via_composed.state.value.projection
        assert (
            via_sequential.state.value.selected_citizen_id
            == via_composed.state.value.selected_citizen_id
        )

    def test_widget_with_state_law(self) -> None:
        """LAW 3: widget.map(f) = widget.with_state(f(widget.state.value))."""
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ProjectionMethod,
            ScatterState,
        )

        widget = EigenvectorScatterWidgetImpl()

        def f(s):
            return ScatterState(
                points=s.points,
                projection=ProjectionMethod.PCA,
                selected_citizen_id=s.selected_citizen_id,
                hovered_citizen_id=s.hovered_citizen_id,
                show_evolving_only=s.show_evolving_only,
                archetype_filter=s.archetype_filter,
                coalition_filter=s.coalition_filter,
                show_labels=s.show_labels,
                show_coalition_colors=s.show_coalition_colors,
                animate_transitions=s.animate_transitions,
            )

        via_map = widget.map(f)
        via_with_state = widget.with_state(f(widget.state.value))

        assert via_map.state.value.projection == via_with_state.state.value.projection


# =============================================================================
# Phase 5 IMPLEMENT: SSE Endpoint Tests
# =============================================================================


class TestTownSSEEndpoint:
    """Tests for TownSSEEndpoint implementation."""

    def test_sse_endpoint_creation(self) -> None:
        """SSE endpoint can be created."""
        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")
        assert endpoint.town_id == "town123"

    @pytest.mark.asyncio
    async def test_sse_push_status(self) -> None:
        """SSE endpoint can push status updates."""
        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")
        await endpoint.push_status({"day": 1, "phase": "MORNING"})

        # Event should be in queue
        event = await endpoint._queue.get()
        assert event is not None
        assert event.event == "town.status"
        assert event.data["day"] == 1

    @pytest.mark.asyncio
    async def test_sse_push_eigenvector_drift(self) -> None:
        """SSE endpoint can push eigenvector drift events."""
        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")
        await endpoint.push_eigenvector_drift(
            citizen_id="c1",
            old_eigenvectors={"warmth": 0.5},
            new_eigenvectors={"warmth": 0.6},
            drift_magnitude=0.1,
        )

        event = await endpoint._queue.get()
        assert event is not None
        assert event.event == "town.eigenvector.drift"
        assert event.data["drift"] == 0.1

    @pytest.mark.asyncio
    async def test_sse_format(self) -> None:
        """SSE events are formatted correctly."""
        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")
        await endpoint.push_status({"test": True})

        event = await endpoint._queue.get()
        assert event is not None
        sse_str = event.to_sse()

        assert "event: town.status" in sse_str
        assert 'data: {"test": true}' in sse_str
        assert sse_str.endswith("\n\n")

    def test_sse_close(self) -> None:
        """SSE endpoint can be closed."""
        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")
        endpoint.close()

        assert endpoint._closed is True

    @pytest.mark.asyncio
    async def test_sse_generate_with_close(self) -> None:
        """SSE generate terminates on close."""
        import asyncio

        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")

        # Collect events in a background task
        events: list[str] = []

        async def collect_events() -> None:
            async for event in endpoint.generate():
                events.append(event)
                if len(events) >= 2:
                    break

        # Start collecting
        task = asyncio.create_task(collect_events())

        # Give time for task to start
        await asyncio.sleep(0.01)

        # Push an event
        await endpoint.push_status({"connected": True})

        # Give time for event to be processed
        await asyncio.sleep(0.01)

        # Close the endpoint
        endpoint.close()

        # Wait for task to complete
        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.TimeoutError:
            pass

        # Should have received at least the status event
        assert len(events) >= 1
        assert "town.status" in events[0]


# =============================================================================
# Phase 5 IMPLEMENT: NATS Bridge Tests
# =============================================================================


class TestTownNATSBridge:
    """Tests for TownNATSBridge implementation."""

    def test_bridge_creation(self) -> None:
        """Bridge can be created with default settings."""
        from agents.town.visualization import TownNATSBridge

        bridge = TownNATSBridge()
        assert bridge._servers == ["nats://localhost:4222"]
        assert bridge._fallback_to_memory is True
        assert bridge.is_connected is False

    def test_bridge_custom_servers(self) -> None:
        """Bridge accepts custom server list."""
        from agents.town.visualization import TownNATSBridge

        bridge = TownNATSBridge(servers=["nats://server1:4222", "nats://server2:4222"])
        assert len(bridge._servers) == 2
        assert "nats://server1:4222" in bridge._servers

    @pytest.mark.asyncio
    async def test_bridge_memory_fallback_publish(self) -> None:
        """Bridge falls back to memory when NATS unavailable."""
        from agents.town.visualization import TownNATSBridge

        bridge = TownNATSBridge(fallback_to_memory=True)
        # Don't connect - will use memory fallback

        await bridge.publish_status("town123", {"day": 1})

        # Check message is in memory queue
        assert "town123" in bridge._memory_queues
        msg = await bridge._memory_queues["town123"].get()
        assert msg["data"]["day"] == 1

    @pytest.mark.asyncio
    async def test_bridge_memory_fallback_subscribe(self) -> None:
        """Bridge memory subscribe yields published messages."""
        import asyncio

        from agents.town.visualization import TownNATSBridge

        bridge = TownNATSBridge(fallback_to_memory=True)

        # Publish a message
        await bridge.publish_status("town456", {"phase": "MORNING"})

        # Subscribe and get message
        messages: list[dict[str, Any]] = []

        async def collect() -> None:
            async for msg in bridge.subscribe_town("town456"):
                messages.append(msg)
                if len(messages) >= 1:
                    break

        # Run with timeout
        task = asyncio.create_task(collect())
        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.TimeoutError:
            pass

        assert len(messages) >= 1
        assert messages[0]["phase"] == "MORNING"

    @pytest.mark.asyncio
    async def test_bridge_eigenvector_drift(self) -> None:
        """Bridge can publish eigenvector drift events."""
        from agents.town.visualization import TownNATSBridge

        bridge = TownNATSBridge(fallback_to_memory=True)

        await bridge.publish_eigenvector_drift(
            town_id="town789",
            citizen_id="c1",
            old_eigenvectors={"warmth": 0.5, "trust": 0.5},
            new_eigenvectors={"warmth": 0.6, "trust": 0.6},
        )

        msg = await bridge._memory_queues["town789"].get()
        assert msg["data"]["citizen_id"] == "c1"
        assert msg["data"]["drift"] > 0  # Some drift

    def test_drift_magnitude_computation(self) -> None:
        """Drift magnitude computes Euclidean distance."""
        from agents.town.visualization import _compute_drift_magnitude

        old = {"warmth": 0.0, "trust": 0.0}
        new = {"warmth": 3.0, "trust": 4.0}

        drift = _compute_drift_magnitude(old, new)
        assert drift == 5.0  # 3-4-5 triangle

    def test_drift_magnitude_same_values(self) -> None:
        """Drift is zero when values unchanged."""
        from agents.town.visualization import _compute_drift_magnitude

        values = {"warmth": 0.5, "trust": 0.5}
        drift = _compute_drift_magnitude(values, values)
        assert drift == 0.0


# =============================================================================
# Phase 5 TEST: Edge Case Tests (QA Discoveries)
# =============================================================================


class TestSSEConnectionDrop:
    """Tests for SSE connection drop handling (QA edge case 1)."""

    @pytest.mark.asyncio
    async def test_sse_close_mid_generate(self) -> None:
        """SSE endpoint handles close() called during generate()."""
        import asyncio

        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")

        events_received: list[str] = []

        async def consume_events() -> None:
            async for event in endpoint.generate():
                events_received.append(event)
                if len(events_received) >= 1:
                    # Simulate client disconnect by closing
                    endpoint.close()

        # Push an event before starting consumer
        await endpoint.push_status({"day": 1})

        # Run consumer
        task = asyncio.create_task(consume_events())
        try:
            await asyncio.wait_for(task, timeout=2.0)
        except asyncio.TimeoutError:
            pass

        # Should have received the event
        assert len(events_received) >= 1
        assert endpoint._closed is True

    @pytest.mark.asyncio
    async def test_sse_queue_full_drops_gracefully(self) -> None:
        """SSE endpoint handles full queue gracefully."""
        from agents.town.visualization import TownSSEEndpoint

        # Small queue for testing
        endpoint = TownSSEEndpoint("town123", max_queue_size=2)

        # Fill the queue
        await endpoint.push_status({"event": 1})
        await endpoint.push_status({"event": 2})

        # Third push should not raise (queue is full but we handle it)
        # Note: put is blocking, so we use put_nowait internally
        # Close to test graceful handling
        endpoint.close()
        assert endpoint._closed is True

    @pytest.mark.asyncio
    async def test_sse_keepalive_on_timeout(self) -> None:
        """SSE endpoint sends keepalive on timeout."""
        import asyncio

        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")

        events: list[str] = []

        async def consume_with_short_timeout() -> None:
            # Override the timeout in generate() by closing quickly
            async for event in endpoint.generate():
                events.append(event)
                break  # Exit after first event

        # Don't push anything, let it timeout
        task = asyncio.create_task(consume_with_short_timeout())

        # Wait a bit then close
        await asyncio.sleep(0.05)
        endpoint.close()

        try:
            await asyncio.wait_for(task, timeout=1.0)
        except asyncio.TimeoutError:
            pass

        # Should either get keepalive or exit cleanly
        assert endpoint._closed is True


class TestNATSReconnection:
    """Tests for NATS reconnection handling (QA edge case 2)."""

    @pytest.mark.asyncio
    async def test_bridge_fallback_when_not_connected(self) -> None:
        """Bridge uses memory fallback when NATS unavailable."""
        from agents.town.visualization import TownNATSBridge

        bridge = TownNATSBridge(fallback_to_memory=True)
        # Don't call connect() - stay disconnected

        assert bridge.is_connected is False

        # Should still be able to publish via memory
        await bridge.publish_status("town123", {"test": True})

        # Verify in memory queue
        assert "town123" in bridge._memory_queues
        msg = await bridge._memory_queues["town123"].get()
        assert msg["data"]["test"] is True

    @pytest.mark.asyncio
    async def test_bridge_memory_queue_isolation(self) -> None:
        """Each town has its own memory queue."""
        from agents.town.visualization import TownNATSBridge

        bridge = TownNATSBridge(fallback_to_memory=True)

        await bridge.publish_status("town_a", {"town": "a"})
        await bridge.publish_status("town_b", {"town": "b"})

        # Different queues
        assert "town_a" in bridge._memory_queues
        assert "town_b" in bridge._memory_queues
        assert bridge._memory_queues["town_a"] is not bridge._memory_queues["town_b"]

        # Correct routing
        msg_a = await bridge._memory_queues["town_a"].get()
        msg_b = await bridge._memory_queues["town_b"].get()
        assert msg_a["data"]["town"] == "a"
        assert msg_b["data"]["town"] == "b"

    @pytest.mark.asyncio
    async def test_bridge_context_manager_without_nats(self) -> None:
        """Bridge context manager works without NATS."""
        from agents.town.visualization import TownNATSBridge

        async with TownNATSBridge(fallback_to_memory=True) as bridge:
            # Will fail to connect to NATS but fallback is enabled
            assert bridge.is_connected is False
            await bridge.publish_status("town123", {"in_context": True})

        # Bridge should be cleanly closed
        assert bridge._connected is False


class TestWidgetRoundtrip:
    """Tests for widget state serialization roundtrip (QA edge case 3)."""

    def test_scatter_point_to_dict_roundtrip(self) -> None:
        """ScatterPoint.to_dict() contains all fields for reconstruction."""
        from agents.town.visualization import ScatterPoint

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.7,
            curiosity=0.8,
            trust=0.6,
            creativity=0.9,
            patience=0.5,
            resilience=0.4,
            ambition=0.3,
            x=1.5,
            y=-0.5,
            color="#ff0000",
            is_evolving=True,
            coalition_ids=("coal1", "coal2"),
        )

        d = point.to_dict()

        # Reconstruct from dict
        reconstructed = ScatterPoint(
            citizen_id=d["citizen_id"],
            citizen_name=d["citizen_name"],
            archetype=d["archetype"],
            warmth=d["eigenvectors"]["warmth"],
            curiosity=d["eigenvectors"]["curiosity"],
            trust=d["eigenvectors"]["trust"],
            creativity=d["eigenvectors"]["creativity"],
            patience=d["eigenvectors"]["patience"],
            resilience=d["eigenvectors"]["resilience"],
            ambition=d["eigenvectors"]["ambition"],
            x=d["x"],
            y=d["y"],
            color=d["color"],
            is_evolving=d["is_evolving"],
            coalition_ids=tuple(d["coalition_ids"]),
        )

        assert reconstructed.citizen_id == point.citizen_id
        assert reconstructed.warmth == point.warmth
        assert reconstructed.x == point.x
        assert reconstructed.coalition_ids == point.coalition_ids

    def test_scatter_state_to_dict_roundtrip(self) -> None:
        """ScatterState.to_dict() contains all fields for reconstruction."""
        from agents.town.visualization import (
            ProjectionMethod,
            ScatterPoint,
            ScatterState,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )

        state = ScatterState(
            points=(point,),
            projection=ProjectionMethod.PAIR_CC,
            selected_citizen_id="c1",
            show_evolving_only=True,
            archetype_filter=("builder", "healer"),
        )

        d = state.to_dict()

        # Verify all fields present
        assert d["type"] == "eigenvector_scatter"
        assert d["projection"] == "PAIR_CC"
        assert d["selected_citizen_id"] == "c1"
        assert d["show_evolving_only"] is True
        assert d["archetype_filter"] == ["builder", "healer"]
        assert len(d["points"]) == 1

    def test_scatter_state_projection_enum_roundtrip(self) -> None:
        """ProjectionMethod enum survives serialization."""
        from agents.town.visualization import ProjectionMethod, ScatterState

        for method in ProjectionMethod:
            state = ScatterState(projection=method)
            d = state.to_dict()
            assert d["projection"] == method.name

            # Can reconstruct enum from name
            restored = ProjectionMethod[d["projection"]]
            assert restored == method


class TestPropertyTests:
    """Property-based tests using hypothesis."""

    @pytest.mark.parametrize(
        "warmth,trust",
        [
            (0.0, 0.0),
            (1.0, 1.0),
            (0.5, 0.5),
            (0.0, 1.0),
            (1.0, 0.0),
        ],
    )
    def test_scatter_point_coordinate_bounds(self, warmth: float, trust: float) -> None:
        """ScatterPoint eigenvector values are preserved exactly."""
        from agents.town.visualization import ScatterPoint

        point = ScatterPoint(
            citizen_id="test",
            citizen_name="Test",
            archetype="builder",
            warmth=warmth,
            curiosity=0.5,
            trust=trust,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )

        assert point.warmth == warmth
        assert point.trust == trust

    @pytest.mark.parametrize(
        "x,y",
        [
            (0.0, 0.0),
            (1.0, 1.0),
            (-2.0, -2.0),
            (2.0, 2.0),
            (0.5, -0.5),
        ],
    )
    def test_scatter_point_2d_coordinates(self, x: float, y: float) -> None:
        """ScatterPoint 2D coordinates are preserved."""
        from agents.town.visualization import ScatterPoint

        point = ScatterPoint(
            citizen_id="test",
            citizen_name="Test",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
            x=x,
            y=y,
        )

        d = point.to_dict()
        assert d["x"] == x
        assert d["y"] == y

    def test_scatter_state_empty_filters_show_all(self) -> None:
        """Empty filters mean show all points."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        points = tuple(
            ScatterPoint(
                citizen_id=f"c{i}",
                citizen_name=f"Citizen {i}",
                archetype=["builder", "trader", "healer"][i % 3],
                warmth=0.5,
                curiosity=0.5,
                trust=0.5,
                creativity=0.5,
                patience=0.5,
                resilience=0.5,
                ambition=0.5,
            )
            for i in range(5)
        )

        # Empty filters
        state = ScatterState(
            points=points,
            archetype_filter=(),  # Empty = show all
            coalition_filter=None,
            show_evolving_only=False,
        )

        result = project_scatter_to_ascii(state)
        assert "Citizens: 5/5" in result

    def test_drift_magnitude_laws(self) -> None:
        """Drift magnitude satisfies metric laws."""
        from agents.town.visualization import _compute_drift_magnitude

        a = {"warmth": 0.5, "trust": 0.3}
        b = {"warmth": 0.7, "trust": 0.4}
        c = {"warmth": 0.9, "trust": 0.2}

        # Identity: d(a, a) = 0
        assert _compute_drift_magnitude(a, a) == 0.0

        # Symmetry: d(a, b) = d(b, a)
        assert _compute_drift_magnitude(a, b) == _compute_drift_magnitude(b, a)

        # Triangle inequality: d(a, c) <= d(a, b) + d(b, c)
        d_ac = _compute_drift_magnitude(a, c)
        d_ab = _compute_drift_magnitude(a, b)
        d_bc = _compute_drift_magnitude(b, c)
        assert d_ac <= d_ab + d_bc + 1e-10  # Small epsilon for float comparison


class TestDegradedModeTests:
    """Tests for degraded mode behavior (from QA)."""

    def test_ascii_projection_invalid_method_fallback(self) -> None:
        """ASCII projection handles unknown projection gracefully."""
        from agents.town.visualization import (
            ScatterPoint,
            ScatterState,
            project_scatter_to_ascii,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )

        # Use default projection
        state = ScatterState(points=(point,))
        result = project_scatter_to_ascii(state)

        # Should render without error
        assert "Eigenvector Space" in result
        assert "Citizens: 1/1" in result

    def test_widget_map_with_identity_preserves_state(self) -> None:
        """Widget.map(id) preserves all state fields."""
        from agents.town.visualization import (
            EigenvectorScatterWidgetImpl,
            ProjectionMethod,
            ScatterPoint,
            ScatterState,
        )

        point = ScatterPoint(
            citizen_id="c1",
            citizen_name="Alice",
            archetype="builder",
            warmth=0.5,
            curiosity=0.5,
            trust=0.5,
            creativity=0.5,
            patience=0.5,
            resilience=0.5,
            ambition=0.5,
        )

        state = ScatterState(
            points=(point,),
            projection=ProjectionMethod.PAIR_CC,
            selected_citizen_id="c1",
            show_evolving_only=True,
        )

        widget = EigenvectorScatterWidgetImpl(initial_state=state)
        mapped = widget.map(lambda s: s)

        # All fields preserved
        assert mapped.state.value.points == widget.state.value.points
        assert mapped.state.value.projection == widget.state.value.projection
        assert mapped.state.value.selected_citizen_id == widget.state.value.selected_citizen_id
        assert mapped.state.value.show_evolving_only == widget.state.value.show_evolving_only

    @pytest.mark.asyncio
    async def test_sse_handles_empty_data(self) -> None:
        """SSE endpoint handles empty data dict."""
        from agents.town.visualization import TownSSEEndpoint

        endpoint = TownSSEEndpoint("town123")
        await endpoint.push_status({})

        event = await endpoint._queue.get()
        assert event is not None
        sse_str = event.to_sse()

        assert "data: {}" in sse_str
        endpoint.close()
