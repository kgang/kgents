"""
Sync Service - Explicit user-driven upload and sync of code artifacts.

Philosophy:
    "NOT magic. User decides what enters the Universe."

The SyncFlow service provides three explicit flows:
1. upload_file - Upload a single file to the Universe
2. sync_directory - Sync a directory tree
3. bootstrap_spec_impl_pair - Bootstrap spec+impl for QA

Kent's workflow: Insert trivial toy specs and implementations
to bootstrap and QA the full user journey.

Architecture:
    SyncFlow delegates to CodeService for parsing and storage.
    It provides the explicit user-facing API while CodeService
    handles the implementation details.

See: spec/protocols/zero-seed.md
"""

from .flow import (
    BootstrapResult,
    SyncFlow,
    SyncResult,
    UploadResult,
)

__all__ = [
    "SyncFlow",
    "UploadResult",
    "SyncResult",
    "BootstrapResult",
]
