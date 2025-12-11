"""
Persistence Extensions: Schema versioning, backup/restore, compression.

Enhanced persistence capabilities for PersistentAgent:
- Schema versioning with automatic migration
- Backup/restore utilities for crash recovery
- Compression strategies for large state

These extensions work with any DataAgent backend.
"""

import gzip
import json
import shutil
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Type,
    TypeVar,
)

from .errors import (
    StateCorruptionError,
    StateError,
    StorageError,
)
from .persistent import PersistentAgent

S = TypeVar("S")


# === Schema Versioning ===


class MigrationDirection(Enum):
    """Direction of schema migration."""

    UP = "up"  # Old → New
    DOWN = "down"  # New → Old (rollback)


@dataclass
class SchemaVersion:
    """
    Schema version information.

    Attributes:
        version: Semantic version string (e.g., "1.0.0")
        created_at: When this version was created
        description: Human-readable description of changes
    """

    version: str
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""

    def __lt__(self, other: "SchemaVersion") -> bool:
        """Compare versions for ordering."""
        return self._parse_version() < other._parse_version()

    def _parse_version(self) -> tuple:
        """Parse version string into comparable tuple."""
        parts = self.version.split(".")
        return tuple(int(p) if p.isdigit() else 0 for p in parts)


@dataclass
class Migration:
    """
    A single schema migration step.

    Attributes:
        from_version: Source version
        to_version: Target version
        up: Function to migrate data forward
        down: Function to migrate data backward (rollback)
    """

    from_version: str
    to_version: str
    up: Callable[[Dict[str, Any]], Dict[str, Any]]
    down: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None
    description: str = ""


class MigrationRegistry:
    """
    Registry of schema migrations.

    Manages a chain of migrations to evolve schema over time.
    """

    def __init__(self):
        self._migrations: Dict[str, Migration] = {}  # from_version → Migration

    def register(self, migration: Migration) -> None:
        """Register a migration."""
        self._migrations[migration.from_version] = migration

    def get_migration_path(self, from_version: str, to_version: str) -> List[Migration]:
        """
        Find the chain of migrations from one version to another.

        Args:
            from_version: Current version
            to_version: Target version

        Returns:
            Ordered list of migrations to apply

        Raises:
            StateError: If no migration path exists
        """
        path = []
        current = from_version

        while current != to_version:
            if current not in self._migrations:
                raise StateError(
                    f"No migration path from {from_version} to {to_version} "
                    f"(stuck at {current})"
                )

            migration = self._migrations[current]
            path.append(migration)
            current = migration.to_version

        return path


@dataclass
class VersionedState(Generic[S]):
    """
    Wrapper that includes schema version with state.

    Attributes:
        version: Schema version of the data
        data: The actual state data
        migrated_at: When this state was last migrated (if ever)
    """

    version: str
    data: S
    migrated_at: Optional[datetime] = None


class VersionedPersistentAgent(Generic[S]):
    """
    PersistentAgent with schema versioning support.

    Automatically migrates state when loading if schema version differs.

    Example:
        >>> # Define migrations
        >>> registry = MigrationRegistry()
        >>> registry.register(Migration(
        ...     from_version="1.0.0",
        ...     to_version="1.1.0",
        ...     up=lambda d: {**d, "new_field": "default"},
        ...     description="Add new_field"
        ... ))
        >>>
        >>> agent = VersionedPersistentAgent(
        ...     path=Path("state.json"),
        ...     schema=MyState,
        ...     current_version="1.1.0",
        ...     migrations=registry
        ... )
    """

    def __init__(
        self,
        path: Path | str,
        schema: Type[S],
        current_version: str,
        migrations: Optional[MigrationRegistry] = None,
        max_history: int = 100,
    ):
        self.path = Path(path)
        self.schema = schema
        self.current_version = current_version
        self.migrations = migrations or MigrationRegistry()
        self.max_history = max_history

        # Underlying agent (operates on VersionedState, not S directly)
        self._backend = PersistentAgent(
            path=self.path,
            schema=dict,  # Store as dict for migration flexibility
            max_history=max_history,
        )

    async def load(self) -> S:
        """
        Load state, migrating if necessary.

        Returns:
            Deserialized and migrated state

        Raises:
            StateNotFoundError: If file doesn't exist
            StateError: If migration fails
        """
        # Load raw data
        raw = await self._backend.load()

        # Extract version (default to "1.0.0" for legacy data)
        stored_version = raw.get("_version", "1.0.0")
        data = raw.get("_data", raw)  # Handle both versioned and legacy formats

        # Migrate if necessary
        if stored_version != self.current_version:
            data = await self._migrate(data, stored_version, self.current_version)

            # Save migrated data
            await self._save_raw(data, self.current_version)

        # Deserialize to schema type
        return self._deserialize(data)

    async def save(self, state: S) -> None:
        """
        Save state with current schema version.

        Args:
            state: State to persist
        """
        await self._save_raw(self._serialize(state), self.current_version)

    async def _save_raw(self, data: Dict[str, Any], version: str) -> None:
        """Save raw data with version wrapper."""
        versioned = {
            "_version": version,
            "_data": data,
            "_migrated_at": datetime.now().isoformat(),
        }
        await self._backend.save(versioned)

    async def _migrate(
        self, data: Dict[str, Any], from_version: str, to_version: str
    ) -> Dict[str, Any]:
        """
        Apply migrations to data.

        Args:
            data: Current data
            from_version: Current version
            to_version: Target version

        Returns:
            Migrated data
        """
        path = self.migrations.get_migration_path(from_version, to_version)

        for migration in path:
            try:
                data = migration.up(data)
            except Exception as e:
                raise StateError(
                    f"Migration {migration.from_version} → {migration.to_version} "
                    f"failed: {e}"
                )

        return data

    def _serialize(self, state: S) -> Dict[str, Any]:
        """Serialize state to dict."""
        if is_dataclass(state):
            return asdict(state)  # type: ignore
        return state  # type: ignore

    def _deserialize(self, data: Dict[str, Any]) -> S:
        """Deserialize dict to state type."""
        if is_dataclass(self.schema):
            return self.schema(**data)  # type: ignore
        return data  # type: ignore


# === Backup/Restore Utilities ===


@dataclass
class BackupMetadata:
    """
    Metadata for a backup file.

    Attributes:
        timestamp: When backup was created
        source_path: Original file path
        version: Schema version (if versioned)
        size_bytes: Backup file size
        checksum: Optional integrity checksum
    """

    timestamp: datetime
    source_path: str
    version: Optional[str] = None
    size_bytes: int = 0
    checksum: Optional[str] = None


class BackupManager:
    """
    Manages backup and restore operations for D-gents.

    Supports:
    - Manual and automatic backups
    - Backup rotation (keep N most recent)
    - Restore from specific backup
    - Backup verification

    Example:
        >>> manager = BackupManager(backup_dir=Path(".backups"))
        >>> agent = PersistentAgent(path=Path("state.json"), schema=MyState)
        >>>
        >>> # Create backup
        >>> backup = await manager.backup(agent)
        >>>
        >>> # Restore from backup
        >>> await manager.restore(agent, backup.timestamp)
    """

    def __init__(
        self,
        backup_dir: Path | str,
        max_backups: int = 10,
        backup_suffix: str = ".backup",
    ):
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_suffix = backup_suffix

        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    async def backup(
        self,
        agent: PersistentAgent[S],
        label: Optional[str] = None,
    ) -> BackupMetadata:
        """
        Create a backup of the agent's state.

        Args:
            agent: Agent to backup
            label: Optional label for the backup

        Returns:
            BackupMetadata with backup details

        Raises:
            StorageError: If backup fails
        """
        if not agent.path.exists():
            raise StorageError(f"Cannot backup: source file {agent.path} not found")

        timestamp = datetime.now()
        label_part = f"_{label}" if label else ""
        backup_name = (
            f"{agent.path.stem}"
            f"_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            f"{label_part}"
            f"{self.backup_suffix}"
        )
        backup_path = self.backup_dir / backup_name

        try:
            # Copy file
            shutil.copy2(agent.path, backup_path)

            # Get metadata
            size = backup_path.stat().st_size

            metadata = BackupMetadata(
                timestamp=timestamp,
                source_path=str(agent.path),
                size_bytes=size,
            )

            # Rotate old backups
            await self._rotate_backups(agent.path.stem)

            return metadata

        except Exception as e:
            raise StorageError(f"Backup failed: {e}")

    async def restore(
        self,
        agent: PersistentAgent[S],
        timestamp: Optional[datetime] = None,
        label: Optional[str] = None,
    ) -> bool:
        """
        Restore agent state from a backup.

        Args:
            agent: Agent to restore
            timestamp: Specific backup timestamp (uses latest if None)
            label: Optional label to filter backups

        Returns:
            True if restore succeeded

        Raises:
            StorageError: If restore fails
        """
        # Find backup to restore
        backups = await self.list_backups(agent.path.stem)

        if not backups:
            raise StorageError(f"No backups found for {agent.path.stem}")

        # Filter by label if specified
        if label:
            backups = [b for b in backups if label in str(b)]

        if timestamp:
            # Find specific backup
            target_str = timestamp.strftime("%Y%m%d_%H%M%S")
            matching = [b for b in backups if target_str in str(b)]
            if not matching:
                raise StorageError(f"No backup found for timestamp {timestamp}")
            backup_path = matching[0]
        else:
            # Use most recent
            backup_path = backups[0]

        try:
            # Restore file
            shutil.copy2(backup_path, agent.path)
            return True

        except Exception as e:
            raise StorageError(f"Restore failed: {e}")

    async def list_backups(self, source_stem: str) -> List[Path]:
        """
        List all backups for a source file.

        Args:
            source_stem: Stem of original file (without extension)

        Returns:
            List of backup paths, newest first
        """
        pattern = f"{source_stem}_*{self.backup_suffix}"
        backups = list(self.backup_dir.glob(pattern))

        # Sort by modification time, newest first
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        return backups

    async def _rotate_backups(self, source_stem: str) -> None:
        """Remove old backups beyond max_backups limit."""
        backups = await self.list_backups(source_stem)

        # Remove excess backups
        for old_backup in backups[self.max_backups :]:
            try:
                old_backup.unlink()
            except Exception:
                pass  # Ignore cleanup errors

    async def verify_backup(self, backup_path: Path) -> bool:
        """
        Verify backup file integrity.

        Args:
            backup_path: Path to backup file

        Returns:
            True if backup is valid JSON
        """
        try:
            with open(backup_path, "r") as f:
                json.load(f)
            return True
        except Exception:
            return False


# === Compression Strategies ===


class CompressionLevel(Enum):
    """Compression level presets."""

    NONE = 0
    FAST = 1
    DEFAULT = 6
    BEST = 9


@dataclass
class CompressionConfig:
    """
    Configuration for state compression.

    Attributes:
        level: Compression level (0-9)
        min_size_bytes: Only compress if state exceeds this size
        algorithm: Compression algorithm ("gzip", "lz4", "zstd")
    """

    level: CompressionLevel = CompressionLevel.DEFAULT
    min_size_bytes: int = 1024  # 1KB
    algorithm: str = "gzip"  # Only gzip supported in stdlib


class CompressedPersistentAgent(Generic[S]):
    """
    PersistentAgent with transparent compression.

    Automatically compresses state when saving if it exceeds min_size_bytes.
    Transparently decompresses when loading.

    Example:
        >>> agent = CompressedPersistentAgent(
        ...     path=Path("state.json"),
        ...     schema=MyState,
        ...     compression=CompressionConfig(
        ...         level=CompressionLevel.FAST,
        ...         min_size_bytes=1024
        ...     )
        ... )
    """

    def __init__(
        self,
        path: Path | str,
        schema: Type[S],
        compression: Optional[CompressionConfig] = None,
        max_history: int = 100,
    ):
        self.path = Path(path)
        self.schema = schema
        self.compression = compression or CompressionConfig()
        self.max_history = max_history

        # Compressed file uses .gz extension
        self._compressed_path = self.path.with_suffix(self.path.suffix + ".gz")

    async def load(self) -> S:
        """
        Load state, decompressing if necessary.

        Returns:
            Deserialized state

        Raises:
            StateNotFoundError: If file doesn't exist
            StateCorruptionError: If decompression or parsing fails
        """
        # Check for compressed file first
        if self._compressed_path.exists():
            return await self._load_compressed()
        elif self.path.exists():
            return await self._load_uncompressed()
        else:
            from .errors import StateNotFoundError

            raise StateNotFoundError(f"No state at {self.path}")

    async def save(self, state: S) -> None:
        """
        Save state, compressing if beneficial.

        Args:
            state: State to persist
        """
        # Serialize
        data = self._serialize(state)
        serialized = json.dumps(data, indent=2)
        size = len(serialized.encode("utf-8"))

        # Decide whether to compress
        if (
            self.compression.level != CompressionLevel.NONE
            and size >= self.compression.min_size_bytes
        ):
            await self._save_compressed(serialized)
            # Remove uncompressed version if it exists
            if self.path.exists():
                self.path.unlink()
        else:
            await self._save_uncompressed(serialized)
            # Remove compressed version if it exists
            if self._compressed_path.exists():
                self._compressed_path.unlink()

    async def _load_compressed(self) -> S:
        """Load and decompress gzipped state."""
        try:
            with gzip.open(self._compressed_path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            return self._deserialize(data)
        except Exception as e:
            raise StateCorruptionError(f"Failed to decompress state: {e}")

    async def _load_uncompressed(self) -> S:
        """Load uncompressed state."""
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
            return self._deserialize(data)
        except json.JSONDecodeError as e:
            raise StateCorruptionError(f"Invalid JSON: {e}")
        except Exception as e:
            from .errors import StorageError

            raise StorageError(f"Failed to load state: {e}")

    async def _save_compressed(self, serialized: str) -> None:
        """Save gzipped state."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write with temp file
        temp_path = self._compressed_path.with_suffix(".tmp")
        try:
            with gzip.open(
                temp_path,
                "wt",
                encoding="utf-8",
                compresslevel=self.compression.level.value,
            ) as f:
                f.write(serialized)
            temp_path.replace(self._compressed_path)
        except Exception as e:
            raise StorageError(f"Failed to save compressed state: {e}")

    async def _save_uncompressed(self, serialized: str) -> None:
        """Save uncompressed state."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write with temp file
        temp_path = self.path.with_suffix(".tmp")
        try:
            with open(temp_path, "w") as f:
                f.write(serialized)
            temp_path.replace(self.path)
        except Exception as e:
            raise StorageError(f"Failed to save state: {e}")

    def _serialize(self, state: S) -> Any:
        """Serialize state to JSON-compatible structure."""
        if is_dataclass(state):
            return asdict(state)  # type: ignore
        return state

    def _deserialize(self, data: Any) -> S:
        """Deserialize JSON data to state type."""
        if is_dataclass(self.schema):
            return self.schema(**data)  # type: ignore
        return data  # type: ignore

    async def get_compression_stats(self) -> Dict[str, Any]:
        """
        Get compression statistics.

        Returns:
            Dict with size comparisons and compression ratio
        """
        stats = {
            "is_compressed": self._compressed_path.exists(),
            "compressed_size": 0,
            "uncompressed_size": 0,
            "compression_ratio": 1.0,
        }

        if self._compressed_path.exists():
            stats["compressed_size"] = self._compressed_path.stat().st_size

            # Load and serialize to get uncompressed size
            try:
                state = await self._load_compressed()
                uncompressed = json.dumps(self._serialize(state))
                stats["uncompressed_size"] = len(uncompressed.encode("utf-8"))

                if stats["compressed_size"] > 0:
                    stats["compression_ratio"] = (
                        stats["uncompressed_size"] / stats["compressed_size"]
                    )
            except Exception:
                pass

        elif self.path.exists():
            stats["uncompressed_size"] = self.path.stat().st_size

        return stats


# === Convenience Functions ===


def create_versioned_agent(
    path: Path | str,
    schema: Type[S],
    version: str,
    migrations: Optional[List[Migration]] = None,
) -> VersionedPersistentAgent[S]:
    """
    Create a versioned persistent agent.

    Args:
        path: Path to state file
        schema: State type
        version: Current schema version
        migrations: Optional list of migrations to register

    Returns:
        VersionedPersistentAgent instance
    """
    registry = MigrationRegistry()
    for migration in migrations or []:
        registry.register(migration)

    return VersionedPersistentAgent(
        path=path,
        schema=schema,
        current_version=version,
        migrations=registry,
    )


def create_compressed_agent(
    path: Path | str,
    schema: Type[S],
    level: CompressionLevel = CompressionLevel.DEFAULT,
    min_size: int = 1024,
) -> CompressedPersistentAgent[S]:
    """
    Create a compressed persistent agent.

    Args:
        path: Path to state file
        schema: State type
        level: Compression level
        min_size: Minimum size in bytes to trigger compression

    Returns:
        CompressedPersistentAgent instance
    """
    return CompressedPersistentAgent(
        path=path,
        schema=schema,
        compression=CompressionConfig(level=level, min_size_bytes=min_size),
    )
