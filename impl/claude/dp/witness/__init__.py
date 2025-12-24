"""
Witness integration: PolicyTrace ↔ Mark bridge.

This module bridges the DP world (PolicyTrace) to the Witness world (Mark).
Every DP step emits a TraceEntry. Every TraceEntry can be witnessed as a Mark.

The proof IS the decision. The mark IS the witness.

bridge.py - Translation functions:
          - trace_entry_to_mark: Convert TraceEntry to Mark dict
          - policy_trace_to_marks: Convert full PolicyTrace to Mark dicts
          - mark_to_trace_entry: Reverse conversion from Mark to TraceEntry
"""

from dp.witness.bridge import (
    mark_to_trace_entry,
    policy_trace_to_marks,
    trace_entry_to_mark,
)

__all__ = [
    "trace_entry_to_mark",
    "policy_trace_to_marks",
    "mark_to_trace_entry",
]
