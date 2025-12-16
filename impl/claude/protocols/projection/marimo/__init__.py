"""
marimo Projection Adapters.

Maps projection widget vocabulary to marimo mo.ui.* components.
Enables consistent rendering in marimo notebooks.
"""

from protocols.projection.marimo.adapters import (
    MarimoAdapter,
    adapt_to_marimo,
    cached_badge_to_marimo,
    error_to_marimo,
    graph_to_marimo,
    progress_to_marimo,
    refusal_to_marimo,
    select_to_marimo,
    table_to_marimo,
    text_to_marimo,
)
from protocols.projection.marimo.stream import stream_to_marimo

__all__ = [
    "MarimoAdapter",
    "adapt_to_marimo",
    "text_to_marimo",
    "select_to_marimo",
    "progress_to_marimo",
    "table_to_marimo",
    "graph_to_marimo",
    "error_to_marimo",
    "refusal_to_marimo",
    "cached_badge_to_marimo",
    "stream_to_marimo",
]
