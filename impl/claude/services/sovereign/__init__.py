"""
Sovereign: The Inbound Sovereignty Crown Jewel.

> *"Data enters. Data is witnessed. Data never leaves without explicit consent."*

This service implements the Inbound Sovereignty Protocol (spec/protocols/inbound-sovereignty.md).

Core Philosophy:
    "We don't reference. We possess."

When a document enters kgents, we:
1. Keep an EXACT COPY under our control
2. WITNESS the arrival (create a Mark)
3. EXTRACT edges at ingest time (not later)
4. STORE edges as evidence (not recomputed)

Laws:
    Law 0: No Entity Without Copy
    Law 1: No Entity Without Witness
    Law 2: No Edge Without Witness
    Law 3: No Export Without Witness
    Law 4: Sync is Ingest

The Three Layers of an Entity:
    - OVERLAY (ours): annotations, corrections, derived data
    - SOVEREIGN COPY: exact bytes from source, versioned
    - WITNESS TRAIL: ingest mark, edge marks, sync marks

Heritage:
    - spec/protocols/witness-primitives.md
    - spec/protocols/k-block.md
    - spec/principles/constitution.md (Article IV: Disgust Veto)

See: spec/protocols/inbound-sovereignty.md
"""

from .ingest import (
    DiscoveredEdge,
    Ingestor,
    extract_edges,
    ingest_content,
    ingest_file,
)
from .store import SovereignStore
from .types import (
    Annotation,
    AnnotationType,
    Diff,
    DiffType,
    IngestedEntity,
    IngestEvent,
    SovereignEntity,
    SyncResult,
    SyncStatus,
)

__all__ = [
    # Core types
    "IngestEvent",
    "IngestedEntity",
    "SovereignEntity",
    "SyncResult",
    "SyncStatus",
    "Diff",
    "DiffType",
    "Annotation",
    "AnnotationType",
    # Store
    "SovereignStore",
    # Ingest
    "Ingestor",
    "DiscoveredEdge",
    "extract_edges",
    "ingest_file",
    "ingest_content",
]
