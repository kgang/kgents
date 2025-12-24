"""
Tests for PolicyTrace ↔ Mark bridge.

Verifies the translation layer between DP traces and Witness marks.
"""

from datetime import datetime, timezone

import pytest

from dp.witness.bridge import (
    mark_to_trace_entry,
    policy_trace_to_marks,
    trace_entry_to_mark,
)
from services.categorical.dp_bridge import PolicyTrace, TraceEntry


def test_trace_entry_to_mark_basic():
    """Test basic conversion from TraceEntry to Mark dict."""
    entry = TraceEntry(
        state_before="initial",
        action="do_something",
        state_after="final",
        value=0.85,
        rationale="This is optimal because X",
        timestamp=datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc),
    )

    mark_dict = trace_entry_to_mark(entry, origin="test_origin")

    # Verify structure
    assert mark_dict["origin"] == "test_origin"
    assert mark_dict["stimulus"]["kind"] == "state"
    assert mark_dict["stimulus"]["content"] == "initial"
    assert mark_dict["response"]["kind"] == "state"
    assert "do_something" in mark_dict["response"]["content"]
    assert "final" in mark_dict["response"]["content"]
    assert mark_dict["response"]["metadata"]["action"] == "do_something"
    assert mark_dict["response"]["metadata"]["value"] == 0.85

    # Verify proof structure
    proof = mark_dict["proof"]
    assert proof["warrant"] == "This is optimal because X"
    assert proof["claim"] == "Action 'do_something' is optimal"
    assert proof["qualifier"] == "almost certainly"  # 0.85 maps to "almost certainly"
    assert proof["tier"] == "CATEGORICAL"

    # Verify tags
    assert "dp" in mark_dict["tags"]
    assert "trace" in mark_dict["tags"]
    assert "optimal" in mark_dict["tags"]


def test_value_to_qualifier_mapping():
    """Test that value ranges map to correct qualifiers."""
    test_cases = [
        (0.95, "definitely"),
        (0.8, "almost certainly"),
        (0.6, "probably"),
        (0.4, "possibly"),
        (0.2, "unlikely"),
    ]

    for value, expected_qualifier in test_cases:
        entry = TraceEntry(
            state_before="s1",
            action="a",
            state_after="s2",
            value=value,
            rationale="test",
        )
        mark_dict = trace_entry_to_mark(entry)
        assert mark_dict["proof"]["qualifier"] == expected_qualifier


def test_policy_trace_to_marks():
    """Test conversion of full PolicyTrace to marks."""
    # Create a trace with multiple entries
    entry1 = TraceEntry(
        state_before="s0",
        action="a1",
        state_after="s1",
        value=0.9,
        rationale="Step 1",
    )
    entry2 = TraceEntry(
        state_before="s1",
        action="a2",
        state_after="s2",
        value=0.7,
        rationale="Step 2",
    )

    trace = PolicyTrace(value="s2", log=(entry1, entry2))

    marks = policy_trace_to_marks(trace, origin="test")

    assert len(marks) == 2
    assert marks[0]["response"]["metadata"]["action"] == "a1"
    assert marks[1]["response"]["metadata"]["action"] == "a2"
    assert marks[0]["proof"]["qualifier"] == "definitely"
    assert marks[1]["proof"]["qualifier"] == "almost certainly"


def test_mark_to_trace_entry_from_dict():
    """Test reverse conversion from mark dict to TraceEntry."""
    mark_dict = {
        "origin": "test",
        "stimulus": {"kind": "state", "content": "initial_state"},
        "response": {
            "kind": "state",
            "content": "action_name → final_state",
            "metadata": {
                "action": "action_name",
                "state": "final_state",
                "value": 0.75,
            },
        },
        "proof": {
            "warrant": "Test rationale",
            "qualifier": "almost certainly",
        },
        "metadata": {"rationale": "Test rationale"},
        "timestamp": "2025-12-24T12:00:00+00:00",
    }

    entry = mark_to_trace_entry(mark_dict)

    assert entry.state_before == "initial_state"
    assert entry.action == "action_name"
    assert entry.state_after == "final_state"
    assert entry.value == 0.75
    assert entry.rationale == "Test rationale"
    assert entry.timestamp == datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc)


def test_mark_to_trace_entry_parses_response_content():
    """Test that mark_to_trace_entry can parse action from response content."""
    mark_dict = {
        "stimulus": {"kind": "state", "content": "s1"},
        "response": {
            "kind": "state",
            "content": "move_forward → s2",
            "metadata": {},
        },
        "proof": {"qualifier": "probably"},
        "metadata": {},
    }

    entry = mark_to_trace_entry(mark_dict)

    assert entry.action == "move_forward"
    assert entry.state_after == "s2"
    assert entry.value == 0.6  # "probably" maps to 0.6


def test_round_trip_conversion():
    """Test that TraceEntry → Mark → TraceEntry preserves data."""
    original_entry = TraceEntry(
        state_before="start",
        action="execute",
        state_after="end",
        value=0.85,
        rationale="Because it's optimal",
        timestamp=datetime(2025, 12, 24, 12, 0, 0, tzinfo=timezone.utc),
    )

    # Convert to mark and back
    mark_dict = trace_entry_to_mark(original_entry)
    reconstructed_entry = mark_to_trace_entry(mark_dict)

    # Verify all fields preserved
    assert reconstructed_entry.state_before == original_entry.state_before
    assert reconstructed_entry.action == original_entry.action
    assert reconstructed_entry.state_after == original_entry.state_after
    assert reconstructed_entry.rationale == original_entry.rationale
    assert reconstructed_entry.timestamp == original_entry.timestamp

    # Value gets quantized through qualifier, so allow some tolerance
    assert abs(reconstructed_entry.value - original_entry.value) < 0.15


def test_mark_to_trace_entry_fallback_parsing():
    """Test that mark_to_trace_entry handles minimal mark data gracefully."""
    # Minimal mark with missing fields
    mark_dict = {
        "stimulus": {"content": "s1"},
        "response": {"content": "do_it → s2"},
        "metadata": {},
    }

    entry = mark_to_trace_entry(mark_dict)

    # Should parse from content
    assert entry.state_before == "s1"
    assert entry.action == "do_it"
    assert entry.state_after == "s2"
    # Should have defaults
    assert entry.value == 0.5  # Default from missing qualifier
