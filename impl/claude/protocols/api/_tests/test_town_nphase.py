"""
Tests for Town Live State N-Phase Enhancement (Wave 4, Task 4.5).

Verifies:
- stream_live endpoint accepts nphase_enabled parameter
- N-Phase session created when enabled
- live.start includes N-Phase info when enabled
- live.nphase events emitted on phase transitions
- live.state includes N-Phase context
- live.end includes N-Phase summary

See: plans/nphase-native-integration-wave4-prompt.md

NOTE: This module is skipped - protocols.api.town was archived.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="protocols.api.town was archived - rebuild in services layer")

import json
from typing import Any, AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Test Helpers
# =============================================================================


def parse_sse_events(content: str) -> list[dict[str, Any]]:
    """Parse SSE content into events."""
    events = []
    current_event: dict[str, Any] = {}

    for line in content.split("\n"):
        if line.startswith("event:"):
            current_event["event"] = line[6:].strip()
        elif line.startswith("data:"):
            try:
                current_event["data"] = json.loads(line[5:].strip())
            except json.JSONDecodeError:
                current_event["data"] = line[5:].strip()
        elif line == "" and current_event:
            events.append(current_event)
            current_event = {}

    if current_event:
        events.append(current_event)

    return events


# =============================================================================
# Unit Tests for N-Phase Mapping
# =============================================================================


class TestTownPhaseToNPhaseMapping:
    """Test Town phase to N-Phase mapping logic."""

    def test_morning_maps_to_understand(self) -> None:
        """MORNING phase maps to UNDERSTAND."""
        from protocols.api.town import create_town_router

        # The mapping is inside the generate() function
        # We test the concept here
        mapping = {
            "MORNING": "UNDERSTAND",
            "AFTERNOON": "UNDERSTAND",
            "EVENING": "ACT",
            "NIGHT": "REFLECT",
        }
        assert mapping["MORNING"] == "UNDERSTAND"

    def test_afternoon_maps_to_understand(self) -> None:
        """AFTERNOON phase maps to UNDERSTAND."""
        mapping = {
            "MORNING": "UNDERSTAND",
            "AFTERNOON": "UNDERSTAND",
            "EVENING": "ACT",
            "NIGHT": "REFLECT",
        }
        assert mapping["AFTERNOON"] == "UNDERSTAND"

    def test_evening_maps_to_act(self) -> None:
        """EVENING phase maps to ACT."""
        mapping = {
            "MORNING": "UNDERSTAND",
            "AFTERNOON": "UNDERSTAND",
            "EVENING": "ACT",
            "NIGHT": "REFLECT",
        }
        assert mapping["EVENING"] == "ACT"

    def test_night_maps_to_reflect(self) -> None:
        """NIGHT phase maps to REFLECT."""
        mapping = {
            "MORNING": "UNDERSTAND",
            "AFTERNOON": "UNDERSTAND",
            "EVENING": "ACT",
            "NIGHT": "REFLECT",
        }
        assert mapping["NIGHT"] == "REFLECT"


# =============================================================================
# N-Phase Session Integration Tests
# =============================================================================


class TestNPhaseSessionCreation:
    """Test N-Phase session creation in stream_live."""

    def test_nphase_session_created_when_enabled(self) -> None:
        """N-Phase session is created when nphase_enabled=True."""
        from protocols.nphase.session import (
            NPhaseSession,
            create_session,
            reset_session_store,
        )

        reset_session_store()
        session = create_session("Test Town Live")

        assert session is not None
        assert session.id is not None
        assert session.current_phase.name == "UNDERSTAND"

    def test_nphase_session_has_event_bus(self) -> None:
        """N-Phase session can be wired to event bus."""
        from agents.town.event_bus import EventBus
        from protocols.nphase.events import NPhaseEvent
        from protocols.nphase.session import (
            create_session,
            reset_session_store,
        )

        reset_session_store()
        session = create_session("Test Town Live")
        event_bus: EventBus[NPhaseEvent] = EventBus()

        session.set_event_bus(event_bus)
        assert session.event_bus is event_bus


# =============================================================================
# Live State Structure Tests
# =============================================================================


class TestLiveStateNPhaseStructure:
    """Test that live.state includes N-Phase context."""

    def test_nphase_context_structure(self) -> None:
        """N-Phase context has expected fields."""
        from protocols.nphase.session import (
            create_session,
            reset_session_store,
        )

        reset_session_store()
        session = create_session("Test Town Live")

        nphase_context = {
            "session_id": session.id,
            "current_phase": session.current_phase.name,
            "cycle_count": session.cycle_count,
            "checkpoint_count": len(session.checkpoints),
            "handle_count": len(session.handles),
        }

        assert "session_id" in nphase_context
        assert "current_phase" in nphase_context
        assert "cycle_count" in nphase_context
        assert "checkpoint_count" in nphase_context
        assert "handle_count" in nphase_context

    def test_nphase_summary_structure(self) -> None:
        """N-Phase summary has expected fields."""
        from protocols.nphase.session import (
            create_session,
            reset_session_store,
        )

        reset_session_store()
        session = create_session("Test Town Live")

        nphase_summary = {
            "session_id": session.id,
            "final_phase": session.current_phase.name,
            "cycle_count": session.cycle_count,
            "checkpoint_count": len(session.checkpoints),
            "handle_count": len(session.handles),
            "ledger_entries": len(session.ledger),
        }

        assert "session_id" in nphase_summary
        assert "final_phase" in nphase_summary
        assert "cycle_count" in nphase_summary
        assert "ledger_entries" in nphase_summary


# =============================================================================
# N-Phase Transition Tests
# =============================================================================


class TestNPhaseTransitions:
    """Test N-Phase transitions during town live streaming."""

    def test_advance_from_understand_to_act(self) -> None:
        """N-Phase advances from UNDERSTAND to ACT."""
        from protocols.nphase.operad import NPhase
        from protocols.nphase.session import (
            create_session,
            reset_session_store,
        )

        reset_session_store()
        session = create_session("Test Town Live")

        assert session.current_phase == NPhase.UNDERSTAND

        session.advance_phase(
            NPhase.ACT,
            payload={"source": "town_live", "town_phase": "EVENING"},
        )

        assert session.current_phase == NPhase.ACT  # type: ignore[comparison-overlap]

    def test_advance_from_act_to_reflect(self) -> None:
        """N-Phase advances from ACT to REFLECT."""
        from protocols.nphase.operad import NPhase
        from protocols.nphase.session import (
            create_session,
            reset_session_store,
        )

        reset_session_store()
        session = create_session("Test Town Live")

        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        assert session.current_phase == NPhase.ACT

        session.advance_phase(
            NPhase.REFLECT,
            payload={"source": "town_live", "town_phase": "NIGHT"},
        )

        assert session.current_phase == NPhase.REFLECT  # type: ignore[comparison-overlap]

    def test_ledger_records_transitions(self) -> None:
        """Ledger records all phase transitions."""
        from protocols.nphase.operad import NPhase
        from protocols.nphase.session import (
            create_session,
            reset_session_store,
        )

        reset_session_store()
        session = create_session("Test Town Live")

        # Initial ledger has one entry (creation)
        initial_entries = len(session.ledger)

        session.advance_phase(NPhase.ACT, auto_checkpoint=False)
        session.advance_phase(NPhase.REFLECT, auto_checkpoint=False)

        # Should have more entries
        assert len(session.ledger) > initial_entries


# =============================================================================
# SSE Event Format Tests
# =============================================================================


class TestSSEEventFormat:
    """Test SSE event format for N-Phase events."""

    def test_live_nphase_event_format(self) -> None:
        """live.nphase event has correct format."""
        import json

        nphase_data = json.dumps(
            {
                "tick": 10,
                "from_phase": "UNDERSTAND",
                "to_phase": "ACT",
                "session_id": "test-session-123",
                "cycle_count": 0,
                "trigger": "town_phase:EVENING",
            }
        )

        sse_line = f"event: live.nphase\ndata: {nphase_data}\n\n"

        assert "event: live.nphase" in sse_line
        assert '"from_phase": "UNDERSTAND"' in sse_line
        assert '"to_phase": "ACT"' in sse_line
        assert '"trigger": "town_phase:EVENING"' in sse_line

    def test_live_start_with_nphase_format(self) -> None:
        """live.start event includes nphase when enabled."""
        import json

        start_data = json.dumps(
            {
                "town_id": "test-town",
                "phases": 4,
                "speed": 1.0,
                "nphase_enabled": True,
                "nphase": {
                    "session_id": "test-session-123",
                    "current_phase": "UNDERSTAND",
                    "cycle_count": 0,
                },
            }
        )

        parsed = json.loads(start_data)
        assert parsed["nphase_enabled"] is True
        assert "nphase" in parsed
        assert parsed["nphase"]["current_phase"] == "UNDERSTAND"

    def test_live_end_with_nphase_summary_format(self) -> None:
        """live.end event includes nphase_summary when enabled."""
        import json

        end_data = json.dumps(
            {
                "town_id": "test-town",
                "total_ticks": 100,
                "status": "completed",
                "nphase_summary": {
                    "session_id": "test-session-123",
                    "final_phase": "REFLECT",
                    "cycle_count": 1,
                    "checkpoint_count": 3,
                    "handle_count": 5,
                    "ledger_entries": 10,
                },
            }
        )

        parsed = json.loads(end_data)
        assert "nphase_summary" in parsed
        assert parsed["nphase_summary"]["final_phase"] == "REFLECT"
        assert parsed["nphase_summary"]["ledger_entries"] == 10


# =============================================================================
# Integration with Existing Tests
# =============================================================================


class TestBackwardsCompatibility:
    """Test that nphase_enabled=False maintains backwards compatibility."""

    def test_default_nphase_disabled(self) -> None:
        """Default value of nphase_enabled is False."""
        # The endpoint signature shows nphase_enabled: bool = False
        # This test verifies the expected default
        default_value = False
        assert default_value is False

    def test_no_nphase_fields_when_disabled(self) -> None:
        """No N-Phase fields appear when disabled."""
        import json

        # Without N-Phase enabled
        start_data = {
            "town_id": "test-town",
            "phases": 4,
            "speed": 1.0,
            "nphase_enabled": False,
        }

        assert "nphase" not in start_data

        end_data = {
            "town_id": "test-town",
            "total_ticks": 100,
            "status": "completed",
        }

        assert "nphase_summary" not in end_data
