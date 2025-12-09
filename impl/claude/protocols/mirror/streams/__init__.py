"""EventStream protocol for temporal observation (Mirror Phase 2).

Provides abstractions for observing change across time.
"""

from .base import (
    Reality,
    Event,
    EventStream,
    Window,
    SlidingWindow,
    EntropyBudget,
    process_stream_with_budget,
)
from .git_stream import GitStream
from .composition import (
    ComposedStream,
    FilteredStream,
    MappedStream,
)
from .witness import TemporalWitness
from .momentum import SemanticMomentum, SemanticMomentumTracker

__all__ = [
    # Base protocol
    "Reality",
    "Event",
    "EventStream",
    "Window",
    "SlidingWindow",
    "EntropyBudget",
    "process_stream_with_budget",
    # Implementations
    "GitStream",
    # Composition
    "ComposedStream",
    "FilteredStream",
    "MappedStream",
    # Analysis
    "TemporalWitness",
    "SemanticMomentum",
    "SemanticMomentumTracker",
]
