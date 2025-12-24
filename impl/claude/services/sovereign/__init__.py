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
from .kblock_integration import (
    KBlockIsolationCheck,
    detect_conflicting_editors,
    verify_all_kblocks,
    verify_kblock_isolation,
)
from .listeners import on_kblock_saved, wire_sovereign_listeners
from .node import SovereignNode
from .provenance import (
    ProvenanceChain,
    ProvenanceStep,
    get_provenance_chain,
    get_provenance_summary,
    verify_provenance_integrity,
)
from .store import SovereignStore
from .types import (
    Annotation,
    AnnotationType,
    DeleteResult,
    Diff,
    DiffType,
    IngestedEntity,
    IngestEvent,
    SovereignEntity,
    SyncResult,
    SyncStatus,
)
from .verification import (
    Check,
    VerificationResult,
    verify_all,
    verify_integrity,
)
from .analysis_reactor import (
    AnalysisCrystal,
    AnalysisReactor,
    analyze_structural,
    analyze_with_claude,
    create_analysis_reactor,
    get_analysis_reactor,
    init_analysis_reactor,
    reset_analysis_reactor,
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
    "DeleteResult",
    # Store
    "SovereignStore",
    # Ingest
    "Ingestor",
    "DiscoveredEdge",
    "extract_edges",
    "ingest_file",
    "ingest_content",
    # Event listeners
    "on_kblock_saved",
    "wire_sovereign_listeners",
    # AGENTESE Node
    "SovereignNode",
    # Verification
    "Check",
    "VerificationResult",
    "verify_integrity",
    "verify_all",
    # K-Block Isolation Verification (Theorem 3)
    "KBlockIsolationCheck",
    "verify_kblock_isolation",
    "verify_all_kblocks",
    "detect_conflicting_editors",
    # Provenance Chain Retrieval (Theorem 2)
    "ProvenanceStep",
    "ProvenanceChain",
    "get_provenance_chain",
    "get_provenance_summary",
    "verify_provenance_integrity",
    # Analysis Reactor (Phase 2)
    "AnalysisCrystal",
    "AnalysisReactor",
    "analyze_structural",
    "analyze_with_claude",
    "create_analysis_reactor",
    "get_analysis_reactor",
    "init_analysis_reactor",
    "reset_analysis_reactor",
]
