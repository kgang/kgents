"""
Re-export PolicyTrace from dp_bridge for convenience.

This allows: from dp.core import PolicyTrace
Instead of:  from services.categorical.dp_bridge import PolicyTrace
"""

from services.categorical.dp_bridge import (
    PolicyTrace,
    Principle,
    PrincipleScore,
    TraceEntry,
)

__all__ = ["PolicyTrace", "TraceEntry", "Principle", "PrincipleScore"]
