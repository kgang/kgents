"""
F-gent Service: Flow agent service layer.

The F-gent (Flow agent) provides chat, research, and collaboration modalities
as a unified flow abstraction.

Crown Jewel Components:
- Polynomial: FlowPhase (agents/f/polynomial.py)
- Operad: FLOW_OPERAD (agents/f/operad.py)
- Node: FlowNode at self.flow (services/f/node.py)

Related:
- Chat modality uses services/chat/ for persistence and session management
- The self.flow node delegates to self.chat for chat operations

See: spec/f-gents/README.md
"""

from .node import FlowNode

__all__ = ["FlowNode"]
