"""
Storage Services: Unified XDG-compliant storage for kgents.

This package provides centralized storage management for all file-based
operations in kgents, following XDG Base Directory specifications.

Usage:
    from services.storage import get_storage_provider

    provider = get_storage_provider()
    uploads_dir = provider.paths.uploads
    provider.ensure_all_dirs()

See: spec/agents/d-gent.md, spec/protocols/storage-unified.md
"""

from .provider import (
    StoragePaths,
    StorageProvider,
    get_cosmos_dir,
    get_exports_dir,
    get_kgents_cache_root,
    get_kgents_config_root,
    get_kgents_data_root,
    get_kgents_state_root,
    get_storage_provider,
    get_uploads_dir,
    get_vectors_dir,
    get_witness_dir,
    reset_storage_provider,
)

__all__ = [
    # Core
    "StorageProvider",
    "StoragePaths",
    "get_storage_provider",
    "reset_storage_provider",
    # XDG Roots
    "get_kgents_data_root",
    "get_kgents_config_root",
    "get_kgents_cache_root",
    "get_kgents_state_root",
    # Convenience
    "get_uploads_dir",
    "get_cosmos_dir",
    "get_exports_dir",
    "get_witness_dir",
    "get_vectors_dir",
]
