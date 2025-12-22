"""
Trail Protocol: First-class knowledge artifacts with concurrent co-exploration.

This module implements the Trail Protocol from spec/protocols/trail-protocol.md.

A Trail is NOT:
- Browser history (log of URLs visited)
- Breadcrumb (linear back-stack)
- Session recording (replay only)

A Trail IS:
- Shareable, forkable, mergeable artifact of understanding
- Evidence that grounds claims in observable exploration
- Living document that multiple explorers navigate simultaneously

Architecture:
    - models.py: SQLAlchemy models for Postgres persistence
    - storage.py: TrailStorageAdapter for D-gent integration
    - file_persistence.py: Lightweight file-based storage (Phase 3)
    - concurrent.py: Fork/merge and real-time sync (Phase 10)
    - semantic/: Embedding and LLM resolution (Phase 9)

Teaching:
    gotcha: Trails persist to Postgres—they are NOT ephemeral.
            Every trail is durable evidence that can be shared and replayed.

    gotcha: Trail steps are immutable once persisted.
            Annotations can be added, but steps are append-only.

    gotcha: For quick local saves, use file_persistence (saves to ~/.kgents/trails/).
            For production/durable storage, use TrailStorageAdapter (Postgres).
            (Evidence: test_file_persistence.py)

Usage:
    # Postgres (production)
    from protocols.trail import TrailStorageAdapter
    storage = TrailStorageAdapter(postgres_backend)
    await storage.save_trail(trail)

    # File-based (quick local saves)
    from protocols.trail import save_trail, load_trail, list_trails
    result = await save_trail(trail, "My Investigation")
    loaded = await load_trail(result.trail_id)

Spec Reference: spec/protocols/trail-protocol.md
"""

from models.trail import (
    # SQLAlchemy models (Row suffix to avoid collision with exploration types)
    TrailRow,
    TrailStepRow,
    TrailAnnotationRow,
    TrailForkRow,
    TrailEvidenceRow,
    TrailCommitmentRow,
)
from .storage import TrailStorageAdapter

# Phase 3: File-based persistence
from .file_persistence import (
    TRAIL_DIR,
    TrailSaveResult,
    TrailLoadResult,
    TrailListEntry,
    save_trail,
    load_trail,
    list_trails,
    delete_trail,
    sanitize_trail_name,
    generate_trail_id,
)

__all__ = [
    # SQLAlchemy models (re-exported from models.trail)
    "TrailRow",
    "TrailStepRow",
    "TrailAnnotationRow",
    "TrailForkRow",
    "TrailEvidenceRow",
    "TrailCommitmentRow",
    # Postgres Storage
    "TrailStorageAdapter",
    # File-based Storage (Phase 3)
    "TRAIL_DIR",
    "TrailSaveResult",
    "TrailLoadResult",
    "TrailListEntry",
    "save_trail",
    "load_trail",
    "list_trails",
    "delete_trail",
    "sanitize_trail_name",
    "generate_trail_id",
]
