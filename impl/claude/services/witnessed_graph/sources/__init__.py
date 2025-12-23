"""
WitnessedGraph Sources: Adapters for each edge source.

Each source adapts its native types to HyperEdge:
- SovereignSource: DiscoveredEdge → HyperEdge
- WitnessSource: Mark tags → HyperEdge
- SpecLedgerSource: Harmony/Contradiction → HyperEdge
"""

from .sovereign_source import SovereignSource
from .spec_ledger_source import SpecLedgerSource
from .witness_source import WitnessSource

__all__ = [
    "SovereignSource",
    "WitnessSource",
    "SpecLedgerSource",
]
