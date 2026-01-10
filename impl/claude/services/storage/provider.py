"""
Unified Storage Provider: XDG-compliant storage abstraction.

> *"One root. Many branches. All paths coherent."*

This module provides a unified interface for all kgents file-based storage,
replacing scattered path logic with XDG-compliant directory management.

Philosophy:
    "PostgreSQL is the cortex. Files are the skeleton.
     The cortex holds state. The skeleton holds structure."

Storage Strategy:
    - PostgreSQL: Primary data store (state, relations, vectors)
    - Files: Staging, exports, backups, static assets

XDG Structure:
    ~/.kgents/                      # XDG_DATA_HOME/kgents
    ├── cosmos/                     # K-Block storage (main content)
    ├── uploads/                    # Sovereign staging area
    ├── vectors/                    # Vector export/backup
    ├── witness/                    # Witness marks (file backup)
    ├── exports/                    # User exports
    └── tmp/                        # Temporary files

    ~/.config/kgents/               # XDG_CONFIG_HOME/kgents
    ├── infrastructure.yaml         # Infrastructure config
    └── profiles/                   # Named profiles

    ~/.cache/kgents/                # XDG_CACHE_HOME/kgents
    ├── embeddings/                 # Cached embeddings
    └── http/                       # HTTP cache

Environment Variables:
    KGENTS_DATA_ROOT      - Override data root (default: ~/.kgents)
    KGENTS_CONFIG_ROOT    - Override config root (default: ~/.config/kgents)
    KGENTS_CACHE_ROOT     - Override cache root (default: ~/.cache/kgents)
    KGENTS_DATABASE_URL   - PostgreSQL connection (primary store)

See: spec/agents/d-gent.md, spec/protocols/storage-unified.md
"""

from __future__ import annotations

import hashlib
import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

logger = logging.getLogger(__name__)

# =============================================================================
# XDG Path Resolution
# =============================================================================

StorageType = Literal["data", "config", "cache", "state"]


def _get_xdg_base(storage_type: StorageType) -> Path:
    """
    Get XDG base directory for the given storage type.

    Args:
        storage_type: Type of storage ("data", "config", "cache", "state")

    Returns:
        XDG base directory path
    """
    home = Path.home()

    if storage_type == "data":
        env_var = "XDG_DATA_HOME"
        default = home / ".local" / "share"
    elif storage_type == "config":
        env_var = "XDG_CONFIG_HOME"
        default = home / ".config"
    elif storage_type == "cache":
        env_var = "XDG_CACHE_HOME"
        default = home / ".cache"
    elif storage_type == "state":
        env_var = "XDG_STATE_HOME"
        default = home / ".local" / "state"
    else:
        raise ValueError(f"Invalid storage type: {storage_type}")

    return Path(os.environ.get(env_var, default))


def get_kgents_data_root() -> Path:
    """
    Get kgents data root directory (XDG_DATA_HOME/kgents or ~/.kgents).

    This is the primary storage location for all kgents file-based data.

    Returns:
        Data root path

    Environment Variables:
        KGENTS_DATA_ROOT: Override data root (default: XDG_DATA_HOME/kgents)

    Teaching:
        gotcha: For backward compatibility, we support ~/.kgents as the default
                instead of ~/.local/share/kgents. This is more user-friendly
                and matches user expectations for a CLI tool.
    """
    if override := os.environ.get("KGENTS_DATA_ROOT"):
        return Path(override)

    # Default: ~/.kgents (more user-friendly than ~/.local/share/kgents)
    return Path.home() / ".kgents"


def get_kgents_config_root() -> Path:
    """
    Get kgents config root directory (XDG_CONFIG_HOME/kgents).

    Returns:
        Config root path

    Environment Variables:
        KGENTS_CONFIG_ROOT: Override config root
    """
    if override := os.environ.get("KGENTS_CONFIG_ROOT"):
        return Path(override)

    return _get_xdg_base("config") / "kgents"


def get_kgents_cache_root() -> Path:
    """
    Get kgents cache root directory (XDG_CACHE_HOME/kgents).

    Returns:
        Cache root path

    Environment Variables:
        KGENTS_CACHE_ROOT: Override cache root
    """
    if override := os.environ.get("KGENTS_CACHE_ROOT"):
        return Path(override)

    return _get_xdg_base("cache") / "kgents"


def get_kgents_state_root() -> Path:
    """
    Get kgents state root directory (XDG_STATE_HOME/kgents).

    Used for logs, runtime state, etc.

    Returns:
        State root path
    """
    return _get_xdg_base("state") / "kgents"


# =============================================================================
# Storage Provider
# =============================================================================


@dataclass(frozen=True)
class StoragePaths:
    """
    All kgents storage paths in one place.

    This is the single source of truth for file-based storage locations.
    """

    # Data paths (XDG_DATA_HOME/kgents or ~/.kgents)
    data_root: Path
    cosmos: Path  # K-Block storage
    uploads: Path  # Sovereign staging area
    vectors: Path  # Vector export/backup
    witness: Path  # Witness marks (file backup)
    exports: Path  # User exports
    tmp: Path  # Temporary files

    # Config paths (XDG_CONFIG_HOME/kgents)
    config_root: Path
    infrastructure_yaml: Path  # Infrastructure config
    profiles: Path  # Named profiles

    # Cache paths (XDG_CACHE_HOME/kgents)
    cache_root: Path
    embeddings_cache: Path  # Cached embeddings
    http_cache: Path  # HTTP cache

    # State paths (XDG_STATE_HOME/kgents)
    state_root: Path
    logs: Path  # Log files


class StorageProvider:
    """
    Unified storage provider for all kgents file operations.

    This class provides:
    - XDG-compliant path resolution
    - Directory creation/management
    - Path validation
    - Content hashing for deduplication

    Usage:
        >>> provider = StorageProvider()
        >>> uploads_dir = provider.paths.uploads
        >>> provider.ensure_dir(uploads_dir)
        >>> hash_val = provider.hash_file(uploads_dir / "doc.pdf")

    Teaching:
        gotcha: PostgreSQL is the PRIMARY store. Files are for staging,
                exports, and backups. Don't use files for primary state.

        gotcha: D-gent router already handles XDG compliance for its own
                backends (SQLite, JSONL). This provider is for higher-level
                services that need explicit file storage (uploads, exports).
    """

    def __init__(self, data_root: Path | None = None) -> None:
        """
        Initialize storage provider.

        Args:
            data_root: Override data root (default: from environment/XDG)
        """
        self._data_root = data_root or get_kgents_data_root()
        self._config_root = get_kgents_config_root()
        self._cache_root = get_kgents_cache_root()
        self._state_root = get_kgents_state_root()
        self._paths: StoragePaths | None = None

    @property
    def paths(self) -> StoragePaths:
        """
        Get all storage paths.

        Lazily constructs paths on first access.

        Returns:
            StoragePaths with all kgents storage locations
        """
        if self._paths is None:
            self._paths = StoragePaths(
                # Data
                data_root=self._data_root,
                cosmos=self._data_root / "cosmos",
                uploads=self._data_root / "uploads",
                vectors=self._data_root / "vectors",
                witness=self._data_root / "witness",
                exports=self._data_root / "exports",
                tmp=self._data_root / "tmp",
                # Config
                config_root=self._config_root,
                infrastructure_yaml=self._config_root / "infrastructure.yaml",
                profiles=self._config_root / "profiles",
                # Cache
                cache_root=self._cache_root,
                embeddings_cache=self._cache_root / "embeddings",
                http_cache=self._cache_root / "http",
                # State
                state_root=self._state_root,
                logs=self._state_root / "logs",
            )
        return self._paths

    def ensure_dir(self, path: Path) -> Path:
        """
        Ensure directory exists, creating it if necessary.

        Args:
            path: Directory path to ensure

        Returns:
            The same path (for chaining)

        Raises:
            OSError: If directory cannot be created
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    def ensure_all_dirs(self) -> None:
        """
        Ensure all standard kgents directories exist.

        Call this on application startup to initialize storage.
        """
        paths = self.paths

        # Data directories
        self.ensure_dir(paths.data_root)
        self.ensure_dir(paths.cosmos)
        self.ensure_dir(paths.uploads)
        self.ensure_dir(paths.vectors)
        self.ensure_dir(paths.witness)
        self.ensure_dir(paths.exports)
        self.ensure_dir(paths.tmp)

        # Config directories
        self.ensure_dir(paths.config_root)
        self.ensure_dir(paths.profiles)

        # Cache directories
        self.ensure_dir(paths.cache_root)
        self.ensure_dir(paths.embeddings_cache)
        self.ensure_dir(paths.http_cache)

        # State directories
        self.ensure_dir(paths.state_root)
        self.ensure_dir(paths.logs)

        logger.info(f"Storage directories initialized at {paths.data_root}")

    def validate_path(self, path: Path, *, allow_outside_root: bool = False) -> Path:
        """
        Validate that a path is safe to use.

        Args:
            path: Path to validate
            allow_outside_root: Allow paths outside kgents roots

        Returns:
            Resolved absolute path

        Raises:
            ValueError: If path is unsafe or outside allowed roots
        """
        resolved = path.resolve()

        # Check if path is inside any kgents root
        roots = [
            self.paths.data_root.resolve(),
            self.paths.config_root.resolve(),
            self.paths.cache_root.resolve(),
            self.paths.state_root.resolve(),
        ]
        in_root = any(resolved == root or root in resolved.parents for root in roots)

        if not in_root and not allow_outside_root:
            raise ValueError(
                f"Path {path} is outside kgents storage roots. "
                f"Use allow_outside_root=True to bypass this check."
            )

        return resolved

    def hash_file(self, path: Path, algorithm: str = "sha256") -> str:
        """
        Compute hash of file content.

        Args:
            path: Path to file
            algorithm: Hash algorithm (default: sha256)

        Returns:
            Hex digest of file content

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        h = hashlib.new(algorithm)
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def clear_cache(self) -> int:
        """
        Clear all cache directories.

        Returns:
            Number of files deleted
        """
        deleted = 0
        cache_root = self.paths.cache_root

        if cache_root.exists():
            for item in cache_root.rglob("*"):
                if item.is_file():
                    item.unlink()
                    deleted += 1

        logger.info(f"Cleared {deleted} cached files from {cache_root}")
        return deleted

    def clear_tmp(self) -> int:
        """
        Clear temporary directory.

        Returns:
            Number of files deleted
        """
        deleted = 0
        tmp_dir = self.paths.tmp

        if tmp_dir.exists():
            for item in tmp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    deleted += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    deleted += 1

        logger.info(f"Cleared {deleted} items from {tmp_dir}")
        return deleted

    def get_size_bytes(self, path: Path) -> int:
        """
        Get total size of a file or directory in bytes.

        Args:
            path: Path to measure

        Returns:
            Size in bytes
        """
        if path.is_file():
            return path.stat().st_size

        total = 0
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
        return total

    def format_size(self, size_bytes: int) -> str:
        """
        Format byte size as human-readable string.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        size: float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"


# =============================================================================
# Global Singleton
# =============================================================================

_provider: StorageProvider | None = None


def get_storage_provider(data_root: Path | None = None) -> StorageProvider:
    """
    Get or create the global StorageProvider.

    Args:
        data_root: Override data root (only used on first call)

    Returns:
        StorageProvider singleton
    """
    global _provider

    if _provider is None:
        _provider = StorageProvider(data_root=data_root)

    return _provider


def reset_storage_provider() -> None:
    """Reset the global StorageProvider (for testing)."""
    global _provider
    _provider = None


# =============================================================================
# Convenience Functions
# =============================================================================


def get_uploads_dir() -> Path:
    """Get uploads directory (sovereign staging area)."""
    return get_storage_provider().paths.uploads


def get_cosmos_dir() -> Path:
    """Get cosmos directory (K-Block storage)."""
    return get_storage_provider().paths.cosmos


def get_exports_dir() -> Path:
    """Get exports directory (user exports)."""
    return get_storage_provider().paths.exports


def get_witness_dir() -> Path:
    """Get witness directory (witness marks file backup)."""
    return get_storage_provider().paths.witness


def get_vectors_dir() -> Path:
    """Get vectors directory (vector export/backup)."""
    return get_storage_provider().paths.vectors


# =============================================================================
# Backward Compatibility
# =============================================================================

# These are for backward compatibility with existing code that uses
# hardcoded paths. New code should use get_storage_provider().paths.

DEFAULT_SOVEREIGN_ROOT: Final[Path] = get_kgents_data_root() / "sovereign"
DEFAULT_UPLOADS_ROOT: Final[Path] = get_uploads_dir()
DEFAULT_COSMOS_ROOT: Final[Path] = get_cosmos_dir()
