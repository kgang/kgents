"""
PolicyTrace ↔ Mark bridge: Decisions are traces, traces are decisions.

This module bridges the DP world (PolicyTrace) to the Witness world (Mark).
Every DP step emits a TraceEntry. Every TraceEntry can be witnessed as a Mark.

The proof IS the decision. The mark IS the witness.

Key Mappings:
    TraceEntry.action       ↔ Mark.action (in response content)
    TraceEntry.state_before ↔ Mark.stimulus (stringified)
    TraceEntry.state_after  ↔ Mark.response (stringified)
    TraceEntry.value        ↔ Mark.proof.qualifier (mapped to confidence language)
    TraceEntry.rationale    ↔ Mark.proof.warrant (reasoning)
    TraceEntry.timestamp    ↔ Mark.timestamp

Philosophy:
    This is a translation layer, not a new abstraction. It converts between
    two views of the same underlying reality: decisions as DP traces and
    decisions as witnessed marks.

See: services/categorical/dp_bridge.py
See: services/witness/mark.py
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from services.categorical.dp_bridge import PolicyTrace, TraceEntry
from services.witness.mark import (
    EvidenceTier,
    Mark,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
)

# =============================================================================
# TraceEntry → Mark Conversion
# =============================================================================


def _value_to_qualifier(value: float) -> str:
    """
    Map a numeric value to a confidence qualifier.

    Value ranges:
        >= 0.9: "definitely"
        >= 0.7: "almost certainly"
        >= 0.5: "probably"
        >= 0.3: "possibly"
        <  0.3: "unlikely"
    """
    if value >= 0.9:
        return "definitely"
    elif value >= 0.7:
        return "almost certainly"
    elif value >= 0.5:
        return "probably"
    elif value >= 0.3:
        return "possibly"
    else:
        return "unlikely"


def _qualifier_to_value(qualifier: str) -> float:
    """
    Reverse mapping: confidence qualifier to numeric value.

    Returns the midpoint of each range.
    """
    qualifier_lower = qualifier.lower().strip()
    if qualifier_lower == "definitely":
        return 0.95
    elif qualifier_lower == "almost certainly":
        return 0.8
    elif qualifier_lower == "probably":
        return 0.6
    elif qualifier_lower == "possibly":
        return 0.4
    elif qualifier_lower == "unlikely":
        return 0.2
    else:
        # Default to neutral
        return 0.5


def trace_entry_to_mark(entry: TraceEntry, origin: str = "dp_bridge") -> dict[str, Any]:
    """
    Convert a TraceEntry to a Mark-compatible dictionary.

    This returns a dict instead of a Mark directly to avoid coupling to
    the full Mark constructor signature and to allow flexible deserialization.

    Args:
        entry: The TraceEntry to convert
        origin: Origin identifier (default: "dp_bridge")

    Returns:
        Dictionary with Mark-compatible structure
    """
    # Build stimulus from state_before
    stimulus_data = {
        "kind": "state",
        "content": str(entry.state_before),
        "source": "dp_solver",
        "metadata": {"state": entry.state_before},
    }

    # Build response from state_after and action
    response_data = {
        "kind": "state",
        "content": f"{entry.action} → {entry.state_after}",
        "success": True,
        "metadata": {
            "action": entry.action,
            "state": entry.state_after,
            "value": entry.value,
        },
    }

    # Build proof from rationale and value
    proof_data = {
        "data": f"State transition: {entry.state_before} → {entry.state_after}",
        "warrant": entry.rationale or "DP optimal policy step",
        "claim": f"Action '{entry.action}' is optimal",
        "qualifier": _value_to_qualifier(entry.value),
        "tier": EvidenceTier.CATEGORICAL.name,  # DP solutions are mathematical
        "backing": f"Bellman optimality (value={entry.value:.3f})",
        "rebuttals": [],
        "principles": [],
    }

    # Build the mark dict
    return {
        "origin": origin,
        "stimulus": stimulus_data,
        "response": response_data,
        "proof": proof_data,
        "timestamp": entry.timestamp.isoformat(),
        "umwelt": UmweltSnapshot.system().to_dict(),
        "tags": ("dp", "trace", "optimal"),
        "metadata": {
            "value": entry.value,
            "rationale": entry.rationale,
        },
    }


def policy_trace_to_marks(trace: PolicyTrace[Any], origin: str = "dp_bridge") -> list[dict[str, Any]]:
    """
    Convert a full PolicyTrace to a list of Mark-compatible dictionaries.

    Each TraceEntry in the PolicyTrace becomes one Mark.

    Args:
        trace: The PolicyTrace to convert
        origin: Origin identifier for all marks

    Returns:
        List of Mark-compatible dictionaries, one per trace entry
    """
    return [trace_entry_to_mark(entry, origin=origin) for entry in trace.log]


# =============================================================================
# Mark → TraceEntry Conversion
# =============================================================================


def mark_to_trace_entry(mark: Mark | dict[str, Any]) -> TraceEntry:
    """
    Convert a Mark (or mark dict) back to a TraceEntry.

    This is the reverse conversion, reconstructing the DP trace from witness data.

    Args:
        mark: Either a Mark object or a mark-compatible dict

    Returns:
        TraceEntry reconstructed from the mark

    Raises:
        ValueError: If the mark doesn't have the required structure
    """
    # Handle both Mark objects and dicts
    if not isinstance(mark, dict):
        # If it's a Mark object, access attributes directly
        stimulus_content = mark.stimulus.content if hasattr(mark, "stimulus") else ""
        response_content = mark.response.content if hasattr(mark, "response") else ""
        response_metadata = mark.response.metadata if hasattr(mark, "response") else {}
        proof_qualifier = mark.proof.qualifier if mark.proof else "probably"
        proof_warrant = mark.proof.warrant if mark.proof else ""
        timestamp = mark.timestamp if hasattr(mark, "timestamp") else datetime.now(timezone.utc)

        # Extract action from response metadata or parse from content
        action = response_metadata.get("action", "")
        if not action and " → " in response_content:
            # Parse "action → state" format
            action = response_content.split(" → ")[0].strip()

        # Extract states
        state_before = stimulus_content
        state_after = response_metadata.get("state", "")
        if not state_after and " → " in response_content:
            state_after = response_content.split(" → ", 1)[1].strip()

        # Extract value
        value = response_metadata.get("value", 0.0)
        if value == 0.0 and proof_qualifier:
            value = _qualifier_to_value(proof_qualifier)

        return TraceEntry(
            state_before=state_before,
            action=action,
            state_after=state_after,
            value=value,
            rationale=proof_warrant,
            timestamp=timestamp,
        )

    # Handle dict format
    stimulus = mark.get("stimulus", {})
    response = mark.get("response", {})
    proof = mark.get("proof", {})
    metadata = mark.get("metadata", {})

    # Extract fields
    state_before = stimulus.get("content", "")
    response_content = response.get("content", "")
    response_metadata = response.get("metadata", {})

    # Extract action
    action = response_metadata.get("action", "")
    if not action and " → " in response_content:
        action = response_content.split(" → ")[0].strip()

    # Extract state_after
    state_after = response_metadata.get("state", "")
    if not state_after and " → " in response_content:
        state_after = response_content.split(" → ", 1)[1].strip()

    # Extract value
    value = response_metadata.get("value") or metadata.get("value")
    if value is None:
        # No explicit value, try to get from qualifier
        qualifier = proof.get("qualifier")
        if qualifier:
            value = _qualifier_to_value(qualifier)
        else:
            # No value and no qualifier, use default
            value = 0.5

    # Extract rationale
    rationale = metadata.get("rationale") or proof.get("warrant", "")

    # Extract timestamp
    timestamp_str = mark.get("timestamp")
    if timestamp_str:
        if isinstance(timestamp_str, str):
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = timestamp_str
    else:
        timestamp = datetime.now(timezone.utc)

    return TraceEntry(
        state_before=state_before,
        action=action,
        state_after=state_after,
        value=value,
        rationale=rationale,
        timestamp=timestamp,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "trace_entry_to_mark",
    "policy_trace_to_marks",
    "mark_to_trace_entry",
]
