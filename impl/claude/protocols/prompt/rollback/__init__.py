"""
Rollback Registry: Full history with instant rollback capability.

Per taste decision: auto-change with rollback.
Every change is recorded. You can always go back.

This module provides:
- Checkpoint: Snapshot of prompt state at a point in time
- RollbackRegistry: Save, list, and restore checkpoints
- CheckpointStorage: Persistence backend

Category Law (must hold):
    rollback(checkpoint(p)) == p  # Invertibility
"""

from .checkpoint import Checkpoint, CheckpointId, CheckpointSummary
from .registry import RollbackRegistry, RollbackResult, get_default_registry
from .storage import CheckpointStorage, InMemoryCheckpointStorage, JSONCheckpointStorage

__all__ = [
    "Checkpoint",
    "CheckpointId",
    "CheckpointSummary",
    "RollbackRegistry",
    "RollbackResult",
    "get_default_registry",
    "CheckpointStorage",
    "JSONCheckpointStorage",
    "InMemoryCheckpointStorage",
]
