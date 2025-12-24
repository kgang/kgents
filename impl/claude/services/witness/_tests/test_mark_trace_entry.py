"""
Test Mark <-> TraceEntry conversion for DP-native integration.

This module tests the bidirectional conversion between:
- Witness Mark (execution artifacts)
- TraceEntry (DP solution traces)

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Every DP step can be a Mark. Every Mark can be a trace entry.
"""

from datetime import datetime, timezone

import pytest

from services.categorical.dp_bridge import TraceEntry
from services.witness.mark import (
    EvidenceTier,
    Mark,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
)


class TestMarkToTraceEntry:
    """Test Mark -> TraceEntry conversion."""

    def test_basic_conversion(self):
        """Test basic mark converts to trace entry."""
        mark = Mark(
            origin="test",
            stimulus=Stimulus(kind="prompt", content="state_A", source="user"),
            response=Response(
                kind="action",
                content="do_something",
                metadata={"state": "state_B"},
            ),
        )

        entry = mark.to_trace_entry()

        assert entry.state_before == "state_A"
        assert entry.action == "do_something"
        assert entry.state_after == "state_B"
        assert entry.value == 0.5  # default when no proof
        assert entry.rationale == ""

    def test_with_proof(self):
        """Test mark with proof converts correctly."""
        proof = Proof.empirical(
            data="Tests pass",
            warrant="Passing tests indicate correctness",
            claim="This works",
        )

        mark = Mark(
            origin="test",
            stimulus=Stimulus(kind="prompt", content="initial", source="user"),
            response=Response(kind="text", content="implemented"),
            proof=proof,
        )

        entry = mark.to_trace_entry()

        assert entry.value == 0.9  # "almost certainly"
        assert entry.rationale == "Passing tests indicate correctness"

    def test_qualifier_to_value_mapping(self):
        """Test all qualifiers map to correct values."""
        test_cases = [
            ("definitely", 1.0),
            ("almost certainly", 0.9),
            ("probably", 0.7),
            ("arguably", 0.5),
            ("possibly", 0.3),
            ("personally", 0.8),
        ]

        for qualifier, expected_value in test_cases:
            proof = Proof(
                data="test",
                warrant="test",
                claim="test",
                qualifier=qualifier,
            )
            mark = Mark(
                origin="test",
                stimulus=Stimulus(kind="test", content="a", source="test"),
                response=Response(kind="test", content="b"),
                proof=proof,
            )

            entry = mark.to_trace_entry()
            assert entry.value == expected_value, f"Failed for qualifier '{qualifier}'"

    def test_timestamp_utc_conversion(self):
        """Test timestamp is converted to UTC if needed."""
        # Naive timestamp
        naive_time = datetime(2025, 1, 1, 12, 0, 0)
        mark = Mark(
            origin="test",
            stimulus=Stimulus(kind="test", content="a", source="test"),
            response=Response(kind="test", content="b"),
            timestamp=naive_time,
        )

        entry = mark.to_trace_entry()
        assert entry.timestamp.tzinfo == timezone.utc

        # Already UTC timestamp
        utc_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mark2 = Mark(
            origin="test",
            stimulus=Stimulus(kind="test", content="a", source="test"),
            response=Response(kind="test", content="b"),
            timestamp=utc_time,
        )

        entry2 = mark2.to_trace_entry()
        assert entry2.timestamp == utc_time


class TestTraceEntryToMark:
    """Test TraceEntry -> Mark conversion."""

    def test_basic_conversion(self):
        """Test basic trace entry converts to mark."""
        entry = TraceEntry(
            state_before="A",
            action="move_to_B",
            state_after="B",
            value=0.8,
            rationale="This is optimal",
        )

        mark = Mark.from_trace_entry(entry)

        assert mark.stimulus.content == "A"
        assert mark.response.content == "move_to_B"
        assert mark.response.metadata["state"] == "B"
        assert mark.response.metadata["value"] == 0.8
        assert mark.origin == "dp_bridge"
        assert "dp_trace" in mark.tags

    def test_with_rationale_creates_proof(self):
        """Test entry with rationale creates proof."""
        entry = TraceEntry(
            state_before="A",
            action="optimal_move",
            state_after="B",
            value=0.95,
            rationale="Bellman optimality",
        )

        mark = Mark.from_trace_entry(entry)

        assert mark.proof is not None
        assert mark.proof.warrant == "Bellman optimality"
        assert mark.proof.claim == "optimal_move"
        assert mark.proof.qualifier == "definitely"  # value 0.95 -> definitely
        assert mark.proof.tier == EvidenceTier.CATEGORICAL

    def test_value_to_qualifier_mapping(self):
        """Test value ranges map to correct qualifiers."""
        test_cases = [
            (1.0, "definitely"),
            (0.95, "definitely"),
            (0.9, "almost certainly"),
            (0.8, "probably"),
            (0.7, "probably"),
            (0.5, "arguably"),
            (0.3, "possibly"),
            (0.1, "possibly"),
        ]

        for value, expected_qualifier in test_cases:
            entry = TraceEntry(
                state_before="A",
                action="test",
                state_after="B",
                value=value,
                rationale="test rationale",
            )

            mark = Mark.from_trace_entry(entry)
            assert (
                mark.proof.qualifier == expected_qualifier
            ), f"Failed for value {value}"

    def test_custom_origin_and_umwelt(self):
        """Test can specify custom origin and umwelt."""
        entry = TraceEntry(
            state_before="A",
            action="test",
            state_after="B",
            value=0.8,
        )

        custom_umwelt = UmweltSnapshot.witness(trust_level=2)
        mark = Mark.from_trace_entry(entry, origin="custom_dp", umwelt=custom_umwelt)

        assert mark.origin == "custom_dp"
        assert mark.umwelt == custom_umwelt


class TestRoundTrip:
    """Test round-trip conversions."""

    def test_mark_to_entry_to_mark(self):
        """Test Mark -> TraceEntry -> Mark preserves core data."""
        original_mark = Mark(
            origin="test",
            stimulus=Stimulus(kind="test", content="state_A", source="test"),
            response=Response(
                kind="action", content="action_1", metadata={"state": "state_B"}
            ),
            proof=Proof.empirical(
                data="test data",
                warrant="test warrant",
                claim="test claim",
            ),
        )

        # Mark -> TraceEntry
        entry = original_mark.to_trace_entry()

        # TraceEntry -> Mark
        reconstructed_mark = Mark.from_trace_entry(entry, origin="test")

        # Core data should be preserved
        assert reconstructed_mark.stimulus.content == original_mark.stimulus.content
        assert reconstructed_mark.response.content == original_mark.response.content
        assert (
            reconstructed_mark.response.metadata["state"]
            == original_mark.response.metadata["state"]
        )
        assert reconstructed_mark.proof.warrant == original_mark.proof.warrant

    def test_entry_to_mark_to_entry(self):
        """
        Test TraceEntry -> Mark -> TraceEntry preserves core data.

        Note: Value precision is lost due to continuous->discrete->continuous mapping.
        0.85 -> "almost certainly" -> 0.9 (this is expected behavior).
        """
        original_entry = TraceEntry(
            state_before="init",
            action="transform",
            state_after="final",
            value=0.85,
            rationale="optimal choice",
        )

        # TraceEntry -> Mark
        mark = Mark.from_trace_entry(original_entry)

        # Mark -> TraceEntry
        reconstructed_entry = mark.to_trace_entry()

        # Core data should be preserved
        assert reconstructed_entry.state_before == original_entry.state_before
        assert reconstructed_entry.action == original_entry.action
        assert reconstructed_entry.state_after == original_entry.state_after
        # Value precision is quantized: 0.85 -> "almost certainly" -> 0.9
        assert reconstructed_entry.value == 0.9
        assert reconstructed_entry.rationale == original_entry.rationale
