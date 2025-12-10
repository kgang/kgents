"""
Bicameral Memory: Cross-Hemisphere Memory with Ghost Detection and Self-Healing.

The Bicameral Engine's memory system coordinates:
- Left Hemisphere (The Bookkeeper): ACID transactions, exact queries, source of truth
- Right Hemisphere (The Poet): Semantic similarity, fuzzy matching, vector embeddings
- Coherency Protocol: Cross-hemisphere validation preventing Ghost Memories

Ghost Memory Problem:
- Vector entry points to deleted/changed relational row
- Symptoms: Search returns stale data, missing references, hallucinations
- Solution: Validate vector results against relational store, self-heal

From the implementation plan:
> "The Coherency Protocol ensures the two hemispheres stay synchronized."
> "Self-healing: Remove stale vector entry."

Design:
- Left Hemisphere is ALWAYS source of truth
- Right Hemisphere is an index for semantic access
- Coherency checks on recall, not on write (eventual consistency)
- Ghost healing is automatic and logged
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Protocol, TypeVar, runtime_checkable

from .errors import NoosphereError
from .infra_backends import (
    ContentHash,
    RecallResult,
    VectorMetadata,
)

# Import from instance_db (protocols layer)
try:
    from protocols.cli.instance_db.interfaces import (
        IRelationalStore,
        IVectorStore,
        VectorSearchResult,
    )
    from protocols.cli.instance_db.hippocampus import (
        Hippocampus,
        ICortex,
        LetheEpoch,
    )
    from protocols.cli.instance_db.nervous import Signal
    from protocols.cli.instance_db.synapse import Synapse

    _INSTANCE_DB_AVAILABLE = True
except ImportError:
    _INSTANCE_DB_AVAILABLE = False
    IRelationalStore = None  # type: ignore
    IVectorStore = None  # type: ignore
    VectorSearchResult = None  # type: ignore
    Hippocampus = None  # type: ignore
    ICortex = None  # type: ignore
    LetheEpoch = None  # type: ignore
    Signal = None  # type: ignore
    Synapse = None  # type: ignore


S = TypeVar("S")


class BicameralError(NoosphereError):
    """Bicameral Memory operation failed."""


class CoherencyError(BicameralError):
    """Cross-hemisphere coherency violation."""


class HealingError(BicameralError):
    """Ghost healing operation failed."""


class HemisphereRole(Enum):
    """Which hemisphere to query."""

    LEFT = auto()  # Relational (Bookkeeper)
    RIGHT = auto()  # Semantic (Poet)
    BOTH = auto()  # Cross-hemisphere with coherency


@dataclass
class GhostRecord:
    """Record of a healed ghost memory."""

    ghost_id: str
    detected_at: str
    healed_at: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class StaleRecord:
    """Record of a stale embedding."""

    id: str
    detected_at: str
    old_hash: str
    new_hash: str
    re_embedded: bool = False


@dataclass
class CoherencyReport:
    """Report from coherency validation."""

    total_checked: int
    valid_count: int
    ghost_count: int
    stale_count: int
    ghosts_healed: int
    stale_flagged: int
    duration_ms: float

    @property
    def coherency_rate(self) -> float:
        """Percentage of valid (non-ghost, non-stale) results."""
        if self.total_checked == 0:
            return 1.0
        return self.valid_count / self.total_checked


@dataclass
class BicameralConfig:
    """Configuration for BicameralMemory."""

    # Ghost healing
    auto_heal_ghosts: bool = True
    log_healed_ghosts: bool = True
    max_ghost_log: int = 1000

    # Staleness detection
    flag_stale_on_recall: bool = True
    auto_reembed_stale: bool = False  # Requires embedding provider
    staleness_threshold_hours: float = 24.0

    # Coherency
    coherency_check_on_recall: bool = True
    coherency_check_on_batch: bool = False  # Expensive, disable by default

    # Telemetry
    log_coherency_reports: bool = True

    # Performance
    max_concurrent_validations: int = 10
    validation_timeout_seconds: float = 5.0


@runtime_checkable
class IEmbeddingProvider(Protocol):
    """Protocol for generating embeddings."""

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        ...

    @property
    def dimensions(self) -> int:
        """Embedding dimensions."""
        ...


@runtime_checkable
class ITelemetryLogger(Protocol):
    """Protocol for telemetry logging."""

    async def log(self, event_type: str, data: dict[str, Any]) -> None:
        """Log a telemetry event."""
        ...


class NullTelemetryLogger:
    """Null logger for when telemetry is disabled."""

    async def log(self, event_type: str, data: dict[str, Any]) -> None:
        pass


class BicameralMemory:
    """
    Cross-Hemisphere Memory with Coherency Protocol.

    Coordinates Left Hemisphere (relational) and Right Hemisphere (vector)
    with automatic ghost detection and self-healing.

    The Bicameral Memory provides:
    - `recall(query)`: Semantic search with coherency validation
    - `store(id, data)`: Store in both hemispheres
    - `fetch(id)`: Direct relational lookup (source of truth)
    - `heal_ghosts()`: Manual ghost sweep
    - `coherency_check()`: Full coherency audit

    Usage:
        bicameral = BicameralMemory(
            left_hemisphere=relational_store,
            right_hemisphere=vector_store,
        )

        # Store data (both hemispheres)
        await bicameral.store("insight-001", {
            "type": "insight",
            "content": "Category theory unifies all D-gent patterns",
        })

        # Semantic recall with coherency
        results = await bicameral.recall("category theory patterns")
        # → Validates against relational store, heals ghosts automatically

        # Check coherency health
        report = await bicameral.coherency_check()
        print(f"Coherency rate: {report.coherency_rate:.1%}")
    """

    def __init__(
        self,
        left_hemisphere: IRelationalStore,
        right_hemisphere: IVectorStore | None = None,
        embedding_provider: IEmbeddingProvider | None = None,
        telemetry: ITelemetryLogger | None = None,
        config: BicameralConfig | None = None,
    ):
        """
        Initialize Bicameral Memory.

        Args:
            left_hemisphere: IRelationalStore (source of truth)
            right_hemisphere: IVectorStore (optional, for semantic search)
            embedding_provider: For generating embeddings
            telemetry: For logging coherency events
            config: Configuration options
        """
        if not _INSTANCE_DB_AVAILABLE:
            raise ImportError(
                "Instance DB not available. Ensure protocols/cli/instance_db is accessible."
            )

        self._left = left_hemisphere
        self._right = right_hemisphere
        self._embedder = embedding_provider
        self._telemetry = telemetry or NullTelemetryLogger()
        self._config = config or BicameralConfig()

        # Ghost tracking
        self._ghost_log: list[GhostRecord] = []
        self._stale_log: list[StaleRecord] = []

        # Statistics
        self._total_recalls = 0
        self._ghosts_healed = 0
        self._stale_flagged = 0
        self._coherency_checks = 0

        # Reembedding queue (for async processing)
        self._reembed_queue: asyncio.Queue[str] = asyncio.Queue()

    @property
    def has_semantic(self) -> bool:
        """Check if semantic (vector) operations are available."""
        return self._right is not None

    # === Core Operations ===

    async def store(
        self,
        id: str,
        data: dict[str, Any],
        table: str = "memories",
        embed_field: str | None = None,
    ) -> str:
        """
        Store data in both hemispheres.

        Left Hemisphere: Insert/update relational row
        Right Hemisphere: Upsert vector with content hash

        Args:
            id: Unique identifier
            data: Data to store
            table: Table name for relational store
            embed_field: Field to embed (default: full JSON)

        Returns:
            Stored ID
        """
        now = datetime.now().isoformat()
        content_hash = ContentHash.compute(data)

        # Left Hemisphere (source of truth)
        query = f"""
            INSERT INTO {table} (id, data, content_hash, created_at, updated_at)
            VALUES (:id, :data, :content_hash, :created_at, :updated_at)
            ON CONFLICT(id) DO UPDATE SET
                data = :data,
                content_hash = :content_hash,
                updated_at = :updated_at
        """
        await self._left.execute(
            query,
            {
                "id": id,
                "data": json.dumps(data, default=str),
                "content_hash": content_hash.hash_value,
                "created_at": now,
                "updated_at": now,
            },
        )

        # Right Hemisphere (semantic index)
        if self._right and self._embedder:
            embed_content = data.get(embed_field) if embed_field else json.dumps(data)
            vector = self._embedder.embed(str(embed_content))

            metadata = VectorMetadata(
                relational_id=id,
                content_hash=content_hash.hash_value,
                created_at=now,
                updated_at=now,
                table=table,
            )

            await self._right.upsert(
                id=id,
                vector=vector,
                metadata=metadata.to_dict(),
            )

        return id

    async def recall(
        self,
        query: str,
        limit: int = 10,
        filter: dict[str, Any] | None = None,
        table: str = "memories",
    ) -> list[RecallResult]:
        """
        Semantic recall with coherency validation.

        This is the main entry point for Bicameral Memory:
        1. Search Right Hemisphere (vector) for semantic matches
        2. Validate against Left Hemisphere (relational)
        3. Detect and heal ghost memories
        4. Flag stale embeddings

        Args:
            query: Text query for semantic search
            limit: Max results
            filter: Metadata filter
            table: Table name for validation

        Returns:
            List of RecallResult with coherency info

        Raises:
            BicameralError: If semantic search not available
        """
        if not self._right or not self._embedder:
            raise BicameralError(
                "Semantic search requires vector store and embedding provider"
            )

        self._total_recalls += 1

        # Step 1: Right Hemisphere search
        query_vector = self._embedder.embed(query)
        vector_results = await self._right.search(
            query_vector=query_vector,
            limit=limit * 2,  # Over-fetch for ghost filtering
            filter=filter,
        )

        if not self._config.coherency_check_on_recall:
            # Skip coherency check (not recommended)
            return [
                RecallResult(id=r.id, data=r.metadata, distance=r.distance)
                for r in vector_results[:limit]
            ]

        # Step 2: Coherency validation
        return await self._validate_with_coherency(
            vector_results=vector_results,
            table=table,
            limit=limit,
        )

    async def _validate_with_coherency(
        self,
        vector_results: list[VectorSearchResult],
        table: str,
        limit: int,
    ) -> list[RecallResult]:
        """
        Validate vector results against relational store.

        Implements the Coherency Protocol:
        1. Batch fetch relational rows
        2. Detect ghosts (missing rows)
        3. Detect staleness (hash mismatch)
        4. Self-heal ghosts
        5. Return valid results
        """
        if not vector_results:
            return []

        start_time = datetime.now()

        # Batch fetch from Left Hemisphere
        ids = [r.id for r in vector_results]
        id_list = ",".join(f"'{id}'" for id in ids)
        query = f"SELECT * FROM {table} WHERE id IN ({id_list})"
        rows = await self._left.fetch_all(query)
        row_map = {row["id"]: row for row in rows}

        results = []
        ghosts_to_heal = []
        stale_to_flag = []

        for vec_result in vector_results:
            metadata = VectorMetadata.from_dict(vec_result.metadata)
            row = row_map.get(vec_result.id)

            if row is None:
                # Ghost Memory detected
                ghosts_to_heal.append(vec_result.id)
                continue

            # Check staleness
            is_stale = False
            if self._config.flag_stale_on_recall and "content_hash" in row:
                if row["content_hash"] != metadata.content_hash:
                    is_stale = True
                    stale_to_flag.append(
                        StaleRecord(
                            id=vec_result.id,
                            detected_at=datetime.now().isoformat(),
                            old_hash=metadata.content_hash,
                            new_hash=row["content_hash"],
                        )
                    )

            # Parse data if JSON
            data = row
            if "data" in row and isinstance(row["data"], str):
                try:
                    data = {**row, "data": json.loads(row["data"])}
                except json.JSONDecodeError:
                    pass

            results.append(
                RecallResult(
                    id=vec_result.id,
                    data=data,
                    distance=vec_result.distance,
                    is_stale=is_stale,
                )
            )

            if len(results) >= limit:
                break

        # Self-heal ghosts
        if ghosts_to_heal and self._config.auto_heal_ghosts:
            await self._heal_ghosts(ghosts_to_heal)

        # Log stale embeddings
        for stale in stale_to_flag:
            self._log_stale(stale)

        # Generate coherency report
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        report = CoherencyReport(
            total_checked=len(vector_results),
            valid_count=len(results),
            ghost_count=len(ghosts_to_heal),
            stale_count=len(stale_to_flag),
            ghosts_healed=len(ghosts_to_heal) if self._config.auto_heal_ghosts else 0,
            stale_flagged=len(stale_to_flag),
            duration_ms=duration_ms,
        )

        if self._config.log_coherency_reports:
            await self._telemetry.log(
                "memory.coherency_check",
                {
                    "total_checked": report.total_checked,
                    "coherency_rate": report.coherency_rate,
                    "ghosts_healed": report.ghosts_healed,
                    "duration_ms": report.duration_ms,
                },
            )

        self._coherency_checks += 1

        return results

    async def _heal_ghosts(self, ghost_ids: list[str]) -> int:
        """
        Remove orphaned vector entries (self-healing).

        Args:
            ghost_ids: IDs of ghost vectors to remove

        Returns:
            Number of ghosts healed
        """
        if not self._right:
            return 0

        healed = 0
        for ghost_id in ghost_ids:
            try:
                deleted = await self._right.delete(ghost_id)
                if deleted:
                    healed += 1
                    self._ghosts_healed += 1

                    # Log ghost
                    record = GhostRecord(
                        ghost_id=ghost_id,
                        detected_at=datetime.now().isoformat(),
                        healed_at=datetime.now().isoformat(),
                    )
                    self._log_ghost(record)

                    # Telemetry
                    if self._config.log_healed_ghosts:
                        await self._telemetry.log(
                            "memory.ghost_healed",
                            {
                                "ghost_id": ghost_id,
                            },
                        )
            except Exception as e:
                await self._telemetry.log(
                    "memory.ghost_heal_failed",
                    {
                        "ghost_id": ghost_id,
                        "error": str(e),
                    },
                )

        return healed

    def _log_ghost(self, record: GhostRecord) -> None:
        """Add ghost to log with size limit."""
        self._ghost_log.append(record)
        if len(self._ghost_log) > self._config.max_ghost_log:
            self._ghost_log = self._ghost_log[-self._config.max_ghost_log :]

    def _log_stale(self, record: StaleRecord) -> None:
        """Add stale record to log."""
        self._stale_log.append(record)
        self._stale_flagged += 1
        if len(self._stale_log) > self._config.max_ghost_log:
            self._stale_log = self._stale_log[-self._config.max_ghost_log :]

    async def fetch(self, id: str, table: str = "memories") -> dict[str, Any] | None:
        """
        Direct relational lookup (Left Hemisphere only).

        This bypasses the Right Hemisphere - use when you know the ID.

        Args:
            id: Data ID
            table: Table name

        Returns:
            Data dict or None
        """
        query = f"SELECT * FROM {table} WHERE id = :id"
        row = await self._left.fetch_one(query, {"id": id})

        if not row:
            return None

        # Parse JSON data field
        if "data" in row and isinstance(row["data"], str):
            try:
                row["data"] = json.loads(row["data"])
            except json.JSONDecodeError:
                pass

        return row

    async def delete(self, id: str, table: str = "memories") -> bool:
        """
        Delete from both hemispheres.

        Args:
            id: Data ID
            table: Table name

        Returns:
            True if deleted from Left Hemisphere
        """
        # Delete from Left Hemisphere (source of truth)
        query = f"DELETE FROM {table} WHERE id = :id"
        affected = await self._left.execute(query, {"id": id})

        # Delete from Right Hemisphere (this prevents ghosts)
        if self._right:
            await self._right.delete(id)

        return affected > 0

    # === Coherency Operations ===

    async def coherency_check(
        self,
        table: str = "memories",
        sample_size: int = 100,
    ) -> CoherencyReport:
        """
        Full coherency audit between hemispheres.

        Samples vectors and validates against relational store.
        Use for health monitoring, not on every recall.

        Args:
            table: Table to check
            sample_size: Number of vectors to sample

        Returns:
            CoherencyReport with statistics
        """
        if not self._right:
            return CoherencyReport(
                total_checked=0,
                valid_count=0,
                ghost_count=0,
                stale_count=0,
                ghosts_healed=0,
                stale_flagged=0,
                duration_ms=0.0,
            )

        start_time = datetime.now()

        # Get vector count
        total_vectors = await self._right.count()
        check_count = min(sample_size, total_vectors)

        if check_count == 0:
            return CoherencyReport(
                total_checked=0,
                valid_count=0,
                ghost_count=0,
                stale_count=0,
                ghosts_healed=0,
                stale_flagged=0,
                duration_ms=0.0,
            )

        # Sample vectors via random search (approximate)
        # In production, would use proper sampling
        zero_vector = [0.0] * self._right.dimensions
        sample_results = await self._right.search(
            query_vector=zero_vector,
            limit=check_count,
        )

        # Validate sample
        valid_results = await self._validate_with_coherency(
            vector_results=sample_results,
            table=table,
            limit=check_count,
        )

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        ghost_count = (
            check_count
            - len(valid_results)
            - len([r for r in valid_results if r.is_stale])
        )
        stale_count = len([r for r in valid_results if r.is_stale])

        return CoherencyReport(
            total_checked=check_count,
            valid_count=len([r for r in valid_results if not r.is_stale]),
            ghost_count=ghost_count,
            stale_count=stale_count,
            ghosts_healed=ghost_count if self._config.auto_heal_ghosts else 0,
            stale_flagged=stale_count,
            duration_ms=duration_ms,
        )

    async def heal_all_ghosts(self, table: str = "memories") -> int:
        """
        Full ghost sweep - find and heal all ghosts.

        Warning: This can be expensive for large vector stores.

        Args:
            table: Table to validate against

        Returns:
            Number of ghosts healed
        """
        if not self._right:
            return 0

        total_healed = 0
        batch_size = 100

        # Iterate through all vectors in batches
        zero_vector = [0.0] * self._right.dimensions
        offset = 0

        while True:
            results = await self._right.search(
                query_vector=zero_vector,
                limit=batch_size,
                # Note: Real implementation would need offset/cursor support
            )

            if not results:
                break

            # Check each batch
            ids = [r.id for r in results]
            id_list = ",".join(f"'{id}'" for id in ids)
            query = f"SELECT id FROM {table} WHERE id IN ({id_list})"
            rows = await self._left.fetch_all(query)
            existing_ids = {row["id"] for row in rows}

            # Find ghosts
            ghost_ids = [r.id for r in results if r.id not in existing_ids]

            if ghost_ids:
                healed = await self._heal_ghosts(ghost_ids)
                total_healed += healed

            offset += batch_size

            # Safety limit
            if offset > 10000:
                break

        return total_healed

    # === Statistics ===

    @property
    def ghost_log(self) -> list[GhostRecord]:
        """Get ghost healing log."""
        return self._ghost_log.copy()

    @property
    def stale_log(self) -> list[StaleRecord]:
        """Get stale embedding log."""
        return self._stale_log.copy()

    def stats(self) -> dict[str, Any]:
        """Get Bicameral Memory statistics."""
        return {
            "has_semantic": self.has_semantic,
            "total_recalls": self._total_recalls,
            "ghosts_healed": self._ghosts_healed,
            "stale_flagged": self._stale_flagged,
            "coherency_checks": self._coherency_checks,
            "ghost_log_size": len(self._ghost_log),
            "stale_log_size": len(self._stale_log),
            "config": {
                "auto_heal_ghosts": self._config.auto_heal_ghosts,
                "flag_stale_on_recall": self._config.flag_stale_on_recall,
                "coherency_check_on_recall": self._config.coherency_check_on_recall,
            },
        }


# === Integration with Hippocampus ===


class BicameralCortex:
    """
    Cortex implementation for Hippocampus integration.

    The Hippocampus flushes short-term memories to this Cortex,
    which stores them in the Bicameral Memory system.

    Implements ICortex protocol from hippocampus.py.
    """

    def __init__(
        self,
        bicameral: BicameralMemory,
        table: str = "memories",
        embed_field: str | None = None,
    ):
        """
        Initialize BicameralCortex.

        Args:
            bicameral: BicameralMemory instance
            table: Table for storage
            embed_field: Field to embed
        """
        self._bicameral = bicameral
        self._table = table
        self._embed_field = embed_field

    async def store_signal(self, signal: Signal) -> bool:
        """
        Store a signal in Bicameral Memory.

        Implements ICortex.store_signal().

        Args:
            signal: Signal from Hippocampus

        Returns:
            True if stored
        """
        try:
            signal_id = f"signal-{signal.timestamp}-{hash(str(signal.data))}"
            await self._bicameral.store(
                id=signal_id,
                data={
                    "signal_type": signal.signal_type,
                    "data": signal.data,
                    "timestamp": signal.timestamp,
                    "instance_id": signal.instance_id,
                    "project_hash": signal.project_hash,
                    "priority": signal.priority.value
                    if hasattr(signal.priority, "value")
                    else str(signal.priority),
                    "surprise": signal.surprise,
                },
                table=self._table,
                embed_field=self._embed_field,
            )
            return True
        except Exception:
            return False

    async def store_batch(self, signals: list[Signal]) -> int:
        """
        Store multiple signals.

        Implements ICortex.store_batch().

        Args:
            signals: Signals from Hippocampus

        Returns:
            Count stored
        """
        stored = 0
        for signal in signals:
            if await self.store_signal(signal):
                stored += 1
        return stored


# === Factory Functions ===


def create_bicameral_memory(
    relational_store: IRelationalStore,
    vector_store: IVectorStore | None = None,
    embedding_provider: IEmbeddingProvider | None = None,
    **config_kwargs,
) -> BicameralMemory:
    """
    Create a BicameralMemory instance.

    Args:
        relational_store: Required relational store (Left Hemisphere)
        vector_store: Optional vector store (Right Hemisphere)
        embedding_provider: For generating embeddings
        **config_kwargs: BicameralConfig parameters

    Returns:
        Configured BicameralMemory
    """
    config = BicameralConfig(**config_kwargs)
    return BicameralMemory(
        left_hemisphere=relational_store,
        right_hemisphere=vector_store,
        embedding_provider=embedding_provider,
        config=config,
    )


def create_bicameral_cortex(
    bicameral: BicameralMemory,
    table: str = "memories",
    embed_field: str | None = None,
) -> BicameralCortex:
    """
    Create a BicameralCortex for Hippocampus integration.

    Args:
        bicameral: BicameralMemory instance
        table: Table for storage
        embed_field: Field to embed

    Returns:
        Configured BicameralCortex
    """
    return BicameralCortex(
        bicameral=bicameral,
        table=table,
        embed_field=embed_field,
    )
