"""
Gestalt Primitives: Widgets for architecture visualization and governance.

The Gestalt Architecture Visualizer (Jewel #6) needs widgets for:
- TopologyGraph: System topology visualization (agents, services, connections)
- GovernanceTable: Agent governance state table (permissions, consent, status)

These widgets integrate with the Projection Component Library for unified
rendering across CLI, TUI, marimo, and JSON surfaces.
"""

from agents.i.reactive.primitives.gestalt.governance import (
    GovernanceEntry,
    GovernanceTableState,
    GovernanceTableWidget,
)
from agents.i.reactive.primitives.gestalt.topology import (
    TopologyEdge,
    TopologyGraphState,
    TopologyGraphWidget,
    TopologyNode,
)

__all__ = [
    # Topology
    "TopologyGraphWidget",
    "TopologyGraphState",
    "TopologyNode",
    "TopologyEdge",
    # Governance
    "GovernanceTableWidget",
    "GovernanceTableState",
    "GovernanceEntry",
]
