"""
Gestalt Persistence: TableAdapter + D-gent integration for Gestalt Crown Jewel.

Owns domain semantics for Gestalt storage:
- WHEN to persist (topology creation, block updates, link changes)
- WHY to persist (code visualization + health tracking + evolution history)
- HOW to compose (TableAdapter for structure, D-gent for analysis content)

AGENTESE aspects exposed:
- manifest: Show codebase health
- topology.create: Create new topology view
- topology.scan: Scan repository for code structure
- block.health: Get block health metrics
- link.trace: Trace dependency chains

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol, TableAdapter
from models.gestalt import (
    CodeBlock,
    CodeLink,
    Topology,
    TopologySnapshot,
)

if TYPE_CHECKING:
    pass


@dataclass
class TopologyView:
    """View of a code topology."""

    id: str
    name: str
    description: str | None
    repo_path: str | None
    git_ref: str | None
    block_count: int
    link_count: int
    complexity_score: float | None
    created_at: str


@dataclass
class CodeBlockView:
    """View of a code block."""

    id: str
    topology_id: str
    name: str
    block_type: str
    file_path: str
    line_start: int | None
    line_end: int | None
    position: tuple[float, float, float]
    test_coverage: float | None
    complexity: float | None
    churn_rate: float | None
    created_at: str


@dataclass
class CodeLinkView:
    """View of a code link."""

    id: str
    topology_id: str
    source_block_id: str
    target_block_id: str
    link_type: str
    strength: float
    call_count: int | None
    notes: str | None


@dataclass
class GestaltStatus:
    """Gestalt health status."""

    total_topologies: int
    total_blocks: int
    total_links: int
    avg_complexity: float | None
    avg_coverage: float | None
    storage_backend: str


class GestaltPersistence:
    """
    Persistence layer for Gestalt Crown Jewel.

    Composes:
    - TableAdapter[Topology]: Topology metadata and structure
    - TableAdapter[CodeBlock]: Block positions and health metrics
    - D-gent: Analysis content, historical snapshots

    Domain Semantics:
    - Topologies are views of code structure
    - Blocks represent functions, classes, modules
    - Links capture dependencies and relationships
    - Health metrics drive "breathing" visualization

    Example:
        persistence = GestaltPersistence(
            topology_adapter=TableAdapter(Topology, session_factory),
            block_adapter=TableAdapter(CodeBlock, session_factory),
            dgent=dgent_router,
        )

        topology = await persistence.create_topology("My Project", repo_path="./")
        blocks = await persistence.scan_repository(topology.id, "./src")
    """

    def __init__(
        self,
        topology_adapter: TableAdapter[Topology],
        block_adapter: TableAdapter[CodeBlock],
        dgent: DgentProtocol,
    ) -> None:
        self.topologies = topology_adapter
        self.blocks = block_adapter
        self.dgent = dgent

    # =========================================================================
    # Topology Management
    # =========================================================================

    async def create_topology(
        self,
        name: str,
        description: str | None = None,
        repo_path: str | None = None,
        git_ref: str | None = None,
    ) -> TopologyView:
        """
        Create a new code topology.

        AGENTESE: self.gestalt.topology.create

        Args:
            name: Topology name
            description: Optional description
            repo_path: Path to repository root
            git_ref: Git branch or commit reference

        Returns:
            TopologyView of the created topology
        """
        topology_id = f"topology-{uuid.uuid4().hex[:12]}"

        async with self.topologies.session_factory() as session:
            topology = Topology(
                id=topology_id,
                name=name,
                description=description,
                repo_path=repo_path,
                git_ref=git_ref,
                layout={},
                viewport={"zoom": 1.0, "pan_x": 0.0, "pan_y": 0.0},
                block_count=0,
                link_count=0,
                complexity_score=None,
            )
            session.add(topology)
            await session.commit()

            return TopologyView(
                id=topology_id,
                name=name,
                description=description,
                repo_path=repo_path,
                git_ref=git_ref,
                block_count=0,
                link_count=0,
                complexity_score=None,
                created_at=topology.created_at.isoformat() if topology.created_at else "",
            )

    async def get_topology(self, topology_id: str) -> TopologyView | None:
        """Get a topology by ID."""
        async with self.topologies.session_factory() as session:
            topology = await session.get(Topology, topology_id)
            if topology is None:
                return None

            return self._topology_to_view(topology)

    async def list_topologies(self, limit: int = 20) -> list[TopologyView]:
        """List all topologies."""
        async with self.topologies.session_factory() as session:
            stmt = select(Topology).order_by(Topology.updated_at.desc()).limit(limit)
            result = await session.execute(stmt)
            topologies = result.scalars().all()

            return [self._topology_to_view(t) for t in topologies]

    async def delete_topology(self, topology_id: str) -> bool:
        """Delete a topology and all its blocks/links."""
        async with self.topologies.session_factory() as session:
            topology = await session.get(Topology, topology_id)
            if topology is None:
                return False

            await session.delete(topology)
            await session.commit()
            return True

    # =========================================================================
    # Code Block Management
    # =========================================================================

    async def add_block(
        self,
        topology_id: str,
        name: str,
        block_type: str,
        file_path: str,
        line_start: int | None = None,
        line_end: int | None = None,
        position: tuple[float, float, float] = (0.0, 0.0, 0.0),
        test_coverage: float | None = None,
        complexity: float | None = None,
        content_hash: str | None = None,
    ) -> CodeBlockView | None:
        """
        Add a code block to a topology.

        AGENTESE: self.gestalt.block.add

        Args:
            topology_id: Parent topology ID
            name: Block name (function/class/module name)
            block_type: Type ("function", "class", "module", "file")
            file_path: Path to source file
            line_start: Starting line number
            line_end: Ending line number
            position: 3D position (x, y, z)
            test_coverage: Coverage percentage (0-1)
            complexity: Cyclomatic complexity
            content_hash: Hash for change detection

        Returns:
            CodeBlockView or None if topology not found
        """
        async with self.blocks.session_factory() as session:
            # Verify topology exists
            topology = await session.get(Topology, topology_id)
            if topology is None:
                return None

            block_id = f"block-{uuid.uuid4().hex[:12]}"

            block = CodeBlock(
                id=block_id,
                topology_id=topology_id,
                name=name,
                block_type=block_type,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                x=position[0],
                y=position[1],
                z=position[2],
                test_coverage=test_coverage,
                complexity=complexity,
                churn_rate=None,
                content_hash=content_hash,
            )
            session.add(block)

            # Update topology block count
            topology.block_count += 1

            await session.commit()

            return CodeBlockView(
                id=block_id,
                topology_id=topology_id,
                name=name,
                block_type=block_type,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                position=position,
                test_coverage=test_coverage,
                complexity=complexity,
                churn_rate=None,
                created_at=block.created_at.isoformat() if block.created_at else "",
            )

    async def update_block_health(
        self,
        block_id: str,
        test_coverage: float | None = None,
        complexity: float | None = None,
        churn_rate: float | None = None,
    ) -> CodeBlockView | None:
        """
        Update block health metrics.

        AGENTESE: self.gestalt.block.health

        Args:
            block_id: Block to update
            test_coverage: New coverage value
            complexity: New complexity value
            churn_rate: New churn rate value

        Returns:
            Updated CodeBlockView or None
        """
        async with self.blocks.session_factory() as session:
            block = await session.get(CodeBlock, block_id)
            if block is None:
                return None

            if test_coverage is not None:
                block.test_coverage = test_coverage
            if complexity is not None:
                block.complexity = complexity
            if churn_rate is not None:
                block.churn_rate = churn_rate

            await session.commit()

            return self._block_to_view(block)

    async def update_block_position(
        self,
        block_id: str,
        x: float,
        y: float,
        z: float = 0.0,
    ) -> CodeBlockView | None:
        """Update block 3D position."""
        async with self.blocks.session_factory() as session:
            block = await session.get(CodeBlock, block_id)
            if block is None:
                return None

            block.x = x
            block.y = y
            block.z = z

            await session.commit()

            return self._block_to_view(block)

    async def get_block(self, block_id: str) -> CodeBlockView | None:
        """Get a block by ID."""
        async with self.blocks.session_factory() as session:
            block = await session.get(CodeBlock, block_id)
            if block is None:
                return None

            return self._block_to_view(block)

    async def list_blocks(
        self,
        topology_id: str,
        block_type: str | None = None,
        file_path: str | None = None,
        limit: int = 100,
    ) -> list[CodeBlockView]:
        """List blocks in a topology with optional filters."""
        async with self.blocks.session_factory() as session:
            stmt = select(CodeBlock).where(CodeBlock.topology_id == topology_id)

            if block_type:
                stmt = stmt.where(CodeBlock.block_type == block_type)
            if file_path:
                stmt = stmt.where(CodeBlock.file_path == file_path)

            stmt = stmt.order_by(CodeBlock.file_path, CodeBlock.line_start).limit(limit)
            result = await session.execute(stmt)
            blocks = result.scalars().all()

            return [self._block_to_view(b) for b in blocks]

    # =========================================================================
    # Code Link Management
    # =========================================================================

    async def add_link(
        self,
        topology_id: str,
        source_block_id: str,
        target_block_id: str,
        link_type: str,
        strength: float = 1.0,
        call_count: int | None = None,
        notes: str | None = None,
    ) -> CodeLinkView | None:
        """
        Add a link between code blocks.

        AGENTESE: self.gestalt.link.add

        Args:
            topology_id: Parent topology
            source_block_id: Source block
            target_block_id: Target block
            link_type: Type ("import", "call", "inherit", "data_flow")
            strength: Link strength (0-1)
            call_count: Number of calls (for call links)
            notes: Optional notes

        Returns:
            CodeLinkView or None if blocks not found
        """
        async with self.blocks.session_factory() as session:
            # Verify topology and blocks exist
            topology = await session.get(Topology, topology_id)
            source = await session.get(CodeBlock, source_block_id)
            target = await session.get(CodeBlock, target_block_id)

            if topology is None or source is None or target is None:
                return None

            link_id = f"link-{uuid.uuid4().hex[:12]}"

            link = CodeLink(
                id=link_id,
                topology_id=topology_id,
                source_block_id=source_block_id,
                target_block_id=target_block_id,
                link_type=link_type,
                strength=strength,
                call_count=call_count,
                notes=notes,
            )
            session.add(link)

            # Update topology link count
            topology.link_count += 1

            await session.commit()

            return CodeLinkView(
                id=link_id,
                topology_id=topology_id,
                source_block_id=source_block_id,
                target_block_id=target_block_id,
                link_type=link_type,
                strength=strength,
                call_count=call_count,
                notes=notes,
            )

    async def list_links(
        self,
        topology_id: str,
        link_type: str | None = None,
        block_id: str | None = None,
        limit: int = 200,
    ) -> list[CodeLinkView]:
        """
        List links with optional filters.

        Args:
            topology_id: Topology to query
            link_type: Filter by link type
            block_id: Filter by source or target block

        Returns:
            List of CodeLinkView
        """
        async with self.blocks.session_factory() as session:
            stmt = select(CodeLink).where(CodeLink.topology_id == topology_id)

            if link_type:
                stmt = stmt.where(CodeLink.link_type == link_type)
            if block_id:
                stmt = stmt.where(
                    (CodeLink.source_block_id == block_id) | (CodeLink.target_block_id == block_id)
                )

            stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            links = result.scalars().all()

            return [self._link_to_view(l) for l in links]

    async def trace_dependencies(
        self,
        block_id: str,
        direction: str = "both",
        max_depth: int = 3,
    ) -> list[CodeLinkView]:
        """
        Trace dependency chain from a block.

        AGENTESE: self.gestalt.link.trace

        Args:
            block_id: Starting block
            direction: "incoming", "outgoing", or "both"
            max_depth: Maximum traversal depth

        Returns:
            List of links in the dependency chain
        """
        async with self.blocks.session_factory() as session:
            block = await session.get(CodeBlock, block_id)
            if block is None:
                return []

            visited = set()
            all_links = []

            async def traverse(current_id: str, depth: int) -> None:
                if depth > max_depth or current_id in visited:
                    return
                visited.add(current_id)

                # Get links
                stmt = select(CodeLink)
                if direction == "incoming":
                    stmt = stmt.where(CodeLink.target_block_id == current_id)
                elif direction == "outgoing":
                    stmt = stmt.where(CodeLink.source_block_id == current_id)
                else:
                    stmt = stmt.where(
                        (CodeLink.source_block_id == current_id)
                        | (CodeLink.target_block_id == current_id)
                    )

                result = await session.execute(stmt)
                links = result.scalars().all()

                for link in links:
                    all_links.append(self._link_to_view(link))
                    # Traverse to connected block
                    next_id = (
                        link.target_block_id
                        if link.source_block_id == current_id
                        else link.source_block_id
                    )
                    await traverse(next_id, depth + 1)

            await traverse(block_id, 0)
            return all_links

    # =========================================================================
    # Snapshot Management
    # =========================================================================

    async def create_snapshot(
        self,
        topology_id: str,
        git_ref: str | None = None,
    ) -> str | None:
        """
        Create a snapshot of topology state.

        AGENTESE: self.gestalt.snapshot

        Enables viewing code evolution over time.

        Returns:
            Snapshot ID or None if topology not found
        """
        async with self.topologies.session_factory() as session:
            topology = await session.get(Topology, topology_id)
            if topology is None:
                return None

            snapshot_id = f"snapshot-{uuid.uuid4().hex[:12]}"

            # Collect current state
            blocks_stmt = select(CodeBlock).where(CodeBlock.topology_id == topology_id)
            blocks_result = await session.execute(blocks_stmt)
            blocks = blocks_result.scalars().all()

            links_stmt = select(CodeLink).where(CodeLink.topology_id == topology_id)
            links_result = await session.execute(links_stmt)
            links = links_result.scalars().all()

            state_json = {
                "blocks": [
                    {
                        "id": b.id,
                        "name": b.name,
                        "block_type": b.block_type,
                        "file_path": b.file_path,
                        "x": b.x,
                        "y": b.y,
                        "z": b.z,
                        "test_coverage": b.test_coverage,
                        "complexity": b.complexity,
                    }
                    for b in blocks
                ],
                "links": [
                    {
                        "id": l.id,
                        "source": l.source_block_id,
                        "target": l.target_block_id,
                        "type": l.link_type,
                        "strength": l.strength,
                    }
                    for l in links
                ],
            }

            snapshot = TopologySnapshot(
                id=snapshot_id,
                topology_id=topology_id,
                git_ref=git_ref,
                block_count=topology.block_count,
                link_count=topology.link_count,
                complexity_score=topology.complexity_score,
                state_json=state_json,
            )
            session.add(snapshot)
            await session.commit()

            return snapshot_id

    # =========================================================================
    # Health Status
    # =========================================================================

    async def manifest(self) -> GestaltStatus:
        """
        Get gestalt health status.

        AGENTESE: self.gestalt.manifest
        """
        async with self.topologies.session_factory() as session:
            # Count topologies
            topo_count_result = await session.execute(select(func.count()).select_from(Topology))
            total_topologies = topo_count_result.scalar() or 0

            # Count blocks
            block_count_result = await session.execute(select(func.count()).select_from(CodeBlock))
            total_blocks = block_count_result.scalar() or 0

            # Count links
            link_count_result = await session.execute(select(func.count()).select_from(CodeLink))
            total_links = link_count_result.scalar() or 0

            # Average complexity
            avg_complexity_result = await session.execute(
                select(func.avg(CodeBlock.complexity)).where(CodeBlock.complexity.isnot(None))
            )
            avg_complexity = avg_complexity_result.scalar()

            # Average coverage
            avg_coverage_result = await session.execute(
                select(func.avg(CodeBlock.test_coverage)).where(CodeBlock.test_coverage.isnot(None))
            )
            avg_coverage = avg_coverage_result.scalar()

        return GestaltStatus(
            total_topologies=total_topologies,
            total_blocks=total_blocks,
            total_links=total_links,
            avg_complexity=avg_complexity,
            avg_coverage=avg_coverage,
            storage_backend="postgres"
            if "postgres" in str(self.topologies.session_factory).lower()
            else "sqlite",
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _topology_to_view(self, topology: Topology) -> TopologyView:
        """Convert Topology model to TopologyView."""
        return TopologyView(
            id=topology.id,
            name=topology.name,
            description=topology.description,
            repo_path=topology.repo_path,
            git_ref=topology.git_ref,
            block_count=topology.block_count,
            link_count=topology.link_count,
            complexity_score=topology.complexity_score,
            created_at=topology.created_at.isoformat() if topology.created_at else "",
        )

    def _block_to_view(self, block: CodeBlock) -> CodeBlockView:
        """Convert CodeBlock model to CodeBlockView."""
        return CodeBlockView(
            id=block.id,
            topology_id=block.topology_id,
            name=block.name,
            block_type=block.block_type,
            file_path=block.file_path,
            line_start=block.line_start,
            line_end=block.line_end,
            position=(block.x, block.y, block.z),
            test_coverage=block.test_coverage,
            complexity=block.complexity,
            churn_rate=block.churn_rate,
            created_at=block.created_at.isoformat() if block.created_at else "",
        )

    def _link_to_view(self, link: CodeLink) -> CodeLinkView:
        """Convert CodeLink model to CodeLinkView."""
        return CodeLinkView(
            id=link.id,
            topology_id=link.topology_id,
            source_block_id=link.source_block_id,
            target_block_id=link.target_block_id,
            link_type=link.link_type,
            strength=link.strength,
            call_count=link.call_count,
            notes=link.notes,
        )


__all__ = [
    "GestaltPersistence",
    "TopologyView",
    "CodeBlockView",
    "CodeLinkView",
    "GestaltStatus",
]
