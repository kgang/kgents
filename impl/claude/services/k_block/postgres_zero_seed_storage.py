"""
PostgreSQL-backed Zero Seed K-Block Storage.

This module provides an async PostgreSQL implementation of ZeroSeedStorage
that persists K-Blocks to the database using SQLAlchemy.

Philosophy:
    "Zero Seed nodes ARE K-Blocks. The derivation IS the lineage."
    "Persistence is not an afterthought—it's the foundation."

Storage pattern:
- Full K-Block data in 'kblocks' table (queryable metadata + content)
- Edges in both normalized table and JSONB for fast traversal
- Async operations throughout (no blocking I/O)

AGENTESE: services.k_block.postgres_zero_seed_storage
"""

from __future__ import annotations

import hashlib
import logging
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.kblock import KBlock as KBlockModel
from services.k_block.core.derivation import DerivationDAG
from services.k_block.core.kblock import KBlockId, generate_kblock_id
from services.k_block.layers.factories import create_kblock_for_layer

if TYPE_CHECKING:
    from services.k_block.core.kblock import KBlock

logger = logging.getLogger(__name__)


class PostgresZeroSeedStorage:
    """
    PostgreSQL-backed storage for Zero Seed nodes using K-Blocks.

    Manages:
    1. K-Block creation for Zero Seed nodes
    2. Derivation DAG tracking
    3. Async CRUD operations with PostgreSQL
    4. Lineage validation
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize PostgreSQL storage.

        Args:
            session_factory: SQLAlchemy async session factory
        """
        self._session_factory = session_factory
        self._kblocks: dict[str, KBlock] = {}  # In-memory cache
        self._dag = DerivationDAG()

    async def create_node(
        self,
        layer: int,
        title: str,
        content: str,
        lineage: list[str] | None = None,
        confidence: float | None = None,
        tags: list[str] | None = None,
        created_by: str = "system",
        kblock_id: KBlockId | None = None,  # Allow override for Zero Seed
    ) -> tuple[KBlock, str]:
        """
        Create a new Zero Seed node as a K-Block and persist to PostgreSQL.

        Args:
            layer: Zero Seed layer (0-7)
            title: Display title
            content: Markdown content
            lineage: Parent K-Block IDs
            confidence: Confidence score (0-1)
            tags: Tags for categorization
            created_by: Creator identifier

        Returns:
            Tuple of (created K-Block, node_id)

        Raises:
            ValueError: If layer invalid or lineage validation fails
        """
        lineage = lineage or []
        tags = tags or []

        # Generate K-Block ID (or use provided one for Zero Seed)
        if kblock_id is None:
            kblock_id = generate_kblock_id()

        # Create K-Block using layer factory
        kblock = create_kblock_for_layer(
            layer=layer,
            kblock_id=kblock_id,
            title=title,
            content=content,
            lineage=lineage,
            confidence=confidence,
            tags=tags,
            created_by=created_by,
        )

        # Store K-Block in memory cache
        node_id = str(kblock_id)
        self._kblocks[node_id] = kblock

        # Add to derivation DAG
        kind = getattr(kblock, "_kind", "unknown")
        self._dag.add_node(
            kblock_id=node_id,
            layer=layer,
            kind=kind,
            parent_ids=lineage,
        )

        # Persist to PostgreSQL
        await self._persist_kblock(kblock, created_by)

        logger.info(f"Created Zero Seed node: {node_id} (L{layer}, {kind}, lineage={len(lineage)})")

        return kblock, node_id

    async def _persist_kblock(self, kblock: KBlock, created_by: str) -> None:
        """
        Persist a K-Block to PostgreSQL.

        Args:
            kblock: K-Block to persist
            created_by: Creator identifier
        """
        async with self._session_factory() as session:
            # Compute content hash
            content_hash = hashlib.sha256(kblock.content.encode()).hexdigest()[:16]

            # Serialize edges
            incoming_edges = [edge.to_dict() for edge in kblock.incoming_edges]
            outgoing_edges = [edge.to_dict() for edge in kblock.outgoing_edges]

            # Extract Zero Seed metadata from K-Block (may be in _layer/_kind or zero_seed_layer/zero_seed_kind)
            zero_seed_layer = kblock.zero_seed_layer or getattr(kblock, "_layer", None)
            zero_seed_kind = kblock.zero_seed_kind or getattr(kblock, "_kind", None)

            # Create SQLAlchemy model
            db_kblock = KBlockModel(
                id=str(kblock.id),
                path=kblock.path,
                content=kblock.content,
                base_content=kblock.base_content,
                content_hash=content_hash,
                isolation=kblock.isolation.name,
                zero_seed_layer=zero_seed_layer,
                zero_seed_kind=zero_seed_kind,
                lineage=kblock.lineage,
                has_proof=kblock.has_proof,
                toulmin_proof=kblock.toulmin_proof,
                confidence=kblock.confidence,
                incoming_edges=incoming_edges,
                outgoing_edges=outgoing_edges,
                tags=getattr(kblock, "_tags", []),
                created_by=created_by,
                not_ingested=kblock.not_ingested,
                analysis_required=kblock.analysis_required,
            )

            session.add(db_kblock)
            await session.commit()

            logger.debug(
                f"Persisted K-Block {kblock.id} to PostgreSQL (L{zero_seed_layer}, {zero_seed_kind})"
            )

    def _deserialize_kblock(self, db_kblock: KBlockModel) -> KBlock:
        """
        Deserialize a SQLAlchemy KBlockModel to a KBlock domain object.

        Args:
            db_kblock: Database model to deserialize

        Returns:
            Deserialized K-Block
        """
        from services.k_block.core.edge import KBlockEdge
        from services.k_block.core.kblock import IsolationState, KBlock as KBlockClass

        return KBlockClass(
            id=KBlockId(db_kblock.id),
            path=db_kblock.path,
            content=db_kblock.content,
            base_content=db_kblock.base_content,
            isolation=IsolationState[db_kblock.isolation],
            created_at=db_kblock.created_at,
            modified_at=db_kblock.updated_at,
            zero_seed_layer=db_kblock.zero_seed_layer,
            zero_seed_kind=db_kblock.zero_seed_kind,
            lineage=db_kblock.lineage,
            has_proof=bool(db_kblock.has_proof),
            toulmin_proof=db_kblock.toulmin_proof,
            confidence=db_kblock.confidence,
            incoming_edges=[
                KBlockEdge.from_dict(edge_data) for edge_data in db_kblock.incoming_edges
            ],
            outgoing_edges=[
                KBlockEdge.from_dict(edge_data) for edge_data in db_kblock.outgoing_edges
            ],
            not_ingested=bool(db_kblock.not_ingested),
            analysis_required=bool(db_kblock.analysis_required),
        )

    async def get_node(self, node_id: str) -> KBlock | None:
        """
        Get a Zero Seed node by ID.

        First checks memory cache, then queries PostgreSQL if needed.

        Args:
            node_id: Node ID (K-Block ID)

        Returns:
            K-Block if found, None otherwise
        """
        # Check memory cache first
        if node_id in self._kblocks:
            return self._kblocks[node_id]

        # Query PostgreSQL
        async with self._session_factory() as session:
            stmt = select(KBlockModel).where(KBlockModel.id == node_id)
            result = await session.execute(stmt)
            db_kblock = result.scalar_one_or_none()

            if db_kblock is None:
                return None

            # Deserialize to K-Block
            kblock = self._deserialize_kblock(db_kblock)

            # Add to cache
            self._kblocks[node_id] = kblock
            return kblock

    async def update_node(
        self,
        node_id: str,
        title: str | None = None,
        content: str | None = None,
        confidence: float | None = None,
        tags: list[str] | None = None,
    ) -> KBlock | None:
        """
        Update a Zero Seed node.

        Args:
            node_id: Node ID to update
            title: Updated title
            content: Updated content
            confidence: Updated confidence
            tags: Updated tags

        Returns:
            Updated K-Block if found, None otherwise
        """
        # Get from cache or database
        kblock = await self.get_node(node_id)
        if not kblock:
            return None

        # Update in-memory K-Block
        if title is not None:
            kblock._title = title  # type: ignore[attr-defined]
        if content is not None:
            kblock.set_content(content)
        if confidence is not None:
            kblock.confidence = confidence
        if tags is not None:
            kblock.tags = tags
            kblock._tags = tags  # type: ignore[attr-defined]

        # Persist to PostgreSQL
        async with self._session_factory() as session:
            stmt = select(KBlockModel).where(KBlockModel.id == node_id)
            result = await session.execute(stmt)
            db_kblock = result.scalar_one_or_none()

            if db_kblock is not None:
                if content is not None:
                    db_kblock.content = content
                    db_kblock.content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                if confidence is not None:
                    db_kblock.confidence = confidence
                if tags is not None:
                    db_kblock.tags = tags

                await session.commit()

        logger.info(f"Updated Zero Seed node: {node_id}")
        return kblock

    async def delete_node(self, node_id: str) -> bool:
        """
        Delete a Zero Seed node.

        Args:
            node_id: Node ID to delete

        Returns:
            True if deleted, False if not found
        """
        # Remove from memory cache
        if node_id in self._kblocks:
            del self._kblocks[node_id]

        # Delete from PostgreSQL
        async with self._session_factory() as session:
            stmt = select(KBlockModel).where(KBlockModel.id == node_id)
            result = await session.execute(stmt)
            db_kblock = result.scalar_one_or_none()

            if db_kblock is None:
                return False

            await session.delete(db_kblock)
            await session.commit()

        logger.info(f"Deleted Zero Seed node: {node_id}")
        return True

    async def get_layer_nodes(self, layer: int) -> list[KBlock]:
        """
        Get all nodes in a specific layer.

        Args:
            layer: Layer number (0-7)

        Returns:
            List of K-Blocks in that layer
        """
        async with self._session_factory() as session:
            stmt = select(KBlockModel).where(KBlockModel.zero_seed_layer == layer)
            result = await session.execute(stmt)
            db_kblocks = result.scalars().all()

            kblocks = []
            for db_kblock in db_kblocks:
                # Check cache first
                node_id = db_kblock.id
                if node_id in self._kblocks:
                    kblocks.append(self._kblocks[node_id])
                    continue

                # Deserialize inline within the same session (don't call get_node!)
                kblock = self._deserialize_kblock(db_kblock)

                # Add to cache
                self._kblocks[node_id] = kblock
                kblocks.append(kblock)

            return kblocks

    def get_lineage(self, node_id: str) -> list[str]:
        """
        Get lineage (ancestors) of a node.

        Args:
            node_id: Node ID

        Returns:
            List of ancestor node IDs
        """
        return self._dag.get_lineage(node_id)

    def get_descendants(self, node_id: str) -> list[str]:
        """
        Get descendants of a node.

        Args:
            node_id: Node ID

        Returns:
            List of descendant node IDs
        """
        return self._dag.get_descendants(node_id)

    def is_grounded(self, node_id: str) -> bool:
        """
        Check if a node's lineage terminates at L1 axioms.

        Args:
            node_id: Node ID

        Returns:
            True if grounded in axioms, False otherwise
        """
        return self._dag.is_grounded(node_id)

    @property
    def dag(self) -> DerivationDAG:
        """Get the derivation DAG."""
        return self._dag

    def __len__(self) -> int:
        """Return number of stored nodes (memory cache)."""
        return len(self._kblocks)

    async def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        context: str | None = None,
        confidence: float = 1.0,
        mark_id: str | None = None,
    ) -> str:
        """
        Add an edge between two K-Blocks.

        Updates both:
        - Source K-Block's outgoing_edges
        - Target K-Block's incoming_edges

        Args:
            source_id: Source K-Block ID
            target_id: Target K-Block ID
            edge_type: Type of edge (derives_from, implements, tests, references, contradicts)
            context: Optional context/justification for the edge
            confidence: Confidence score [0.0, 1.0]
            mark_id: Optional witness mark ID

        Returns:
            The edge ID

        Raises:
            ValueError: If source or target K-Block not found
        """
        import uuid
        from datetime import datetime, timezone

        from services.k_block.core.edge import KBlockEdge

        # Generate edge ID
        edge_id = f"edge_{uuid.uuid4().hex[:12]}"

        # Create edge object
        edge = KBlockEdge(
            id=edge_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            context=context or f"Edge from {source_id[:8]} to {target_id[:8]}",
            confidence=confidence,
            mark_id=mark_id,
            created_at=datetime.now(timezone.utc),
        )

        async with self._session_factory() as session:
            # Get source K-Block
            stmt = select(KBlockModel).where(KBlockModel.id == source_id)
            result = await session.execute(stmt)
            source_db = result.scalar_one_or_none()

            if source_db is None:
                raise ValueError(f"Source K-Block not found: {source_id}")

            # Get target K-Block
            stmt = select(KBlockModel).where(KBlockModel.id == target_id)
            result = await session.execute(stmt)
            target_db = result.scalar_one_or_none()

            if target_db is None:
                raise ValueError(f"Target K-Block not found: {target_id}")

            # Update source's outgoing_edges
            outgoing = list(source_db.outgoing_edges or [])
            outgoing.append(edge.to_dict())
            source_db.outgoing_edges = outgoing

            # Update target's incoming_edges
            incoming = list(target_db.incoming_edges or [])
            incoming.append(edge.to_dict())
            target_db.incoming_edges = incoming

            await session.commit()

        # Update memory cache if cached
        if source_id in self._kblocks:
            self._kblocks[source_id].outgoing_edges.append(edge)
        if target_id in self._kblocks:
            self._kblocks[target_id].incoming_edges.append(edge)

        logger.info(f"Added edge {edge_id}: {source_id[:8]}... -> {target_id[:8]}... ({edge_type})")

        return edge_id


# Global storage instance (for backward compatibility)
_storage: PostgresZeroSeedStorage | None = None


async def get_postgres_zero_seed_storage() -> PostgresZeroSeedStorage:
    """
    Get global PostgreSQL Zero Seed storage instance.

    Creates the storage with session factory from bootstrap.
    """
    global _storage
    if _storage is None:
        from services.providers import get_session_factory

        session_factory = await get_session_factory()
        _storage = PostgresZeroSeedStorage(session_factory)
    return _storage


def reset_postgres_zero_seed_storage() -> None:
    """Reset global storage (for testing)."""
    global _storage
    _storage = None


__all__ = [
    "PostgresZeroSeedStorage",
    "get_postgres_zero_seed_storage",
    "reset_postgres_zero_seed_storage",
]
