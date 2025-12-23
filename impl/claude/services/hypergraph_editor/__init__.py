"""
Hypergraph Editor Service - Crown Jewel for typed-hypergraph editing.

The editor is a modal interface to the typed-hypergraph, where:
- Every cursor position is a node focus
- Every selection is a subgraph
- Every edit is a morphism
- Navigation is edge traversal, not path construction

See: spec/surfaces/hypergraph-editor.md
"""

from .contracts import (
    AffordancesRequest,
    AffordancesResponse,
    CommandRequest,
    CommandResponse,
    EditorStateResponse,
    FocusRequest,
    FocusResponse,
    ModeRequest,
    ModeResponse,
    NavigateRequest,
    NavigateResponse,
    SelectionRequest,
    SelectionResponse,
)
from .node import EditorNode
from .service import HypergraphEditorService

__all__ = [
    # Service
    "HypergraphEditorService",
    # Node
    "EditorNode",
    # Contracts
    "EditorStateResponse",
    "NavigateRequest",
    "NavigateResponse",
    "FocusRequest",
    "FocusResponse",
    "ModeRequest",
    "ModeResponse",
    "CommandRequest",
    "CommandResponse",
    "AffordancesRequest",
    "AffordancesResponse",
    "SelectionRequest",
    "SelectionResponse",
]
