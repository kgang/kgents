"""
Ingest Protocol: Document ingestion with witness marks.

> *"Every document that enters is witnessed. Every edge discovered is marked."*

This module implements the core ingest flow:

    IngestEvent ──► ingest() ──► IngestedEntity
                      │
                      ├─► birth_mark (witness arrival)
                      ├─► sovereign.store_version() (store copy)
                      ├─► extract_edges() (discover edges)
                      ├─► edge_marks[] (witness each edge)
                      └─► sovereign.store_overlay() (store derived data)

Laws Enforced:
    Law 0: No Entity Without Copy — store_version() runs before anything else
    Law 1: No Entity Without Witness — birth_mark created immediately
    Law 2: No Edge Without Witness — every edge gets its own mark

Teaching:
    gotcha: Edge extraction happens AT INGEST TIME, not on query.
            This is the key insight—we compute once, store forever.

    gotcha: All marks link to the birth mark via parent relationship.
            This creates a proper causal DAG for tracing.

See: spec/protocols/inbound-sovereignty.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from protocols.specgraph.parser import SpecParser
from protocols.specgraph.types import SpecEdge

from .store import SovereignStore
from .types import IngestedEntity, IngestEvent

if TYPE_CHECKING:
    from services.witness.persistence import MarkResult, WitnessPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Edge Extraction
# =============================================================================


@dataclass
class DiscoveredEdge:
    """An edge discovered during ingestion."""

    edge_type: str  # "references", "implements", "tests", "extends", "heritage"
    target: str  # What the edge points to
    line_number: int  # Where in the source
    context: str  # Surrounding text


def extract_edges(content: bytes, path: str) -> list[DiscoveredEdge]:
    """
    Extract edges from content.

    Uses SpecParser for markdown, could extend to Python AST for .py files.

    Args:
        content: The content bytes
        path: The path (used to determine parser)

    Returns:
        List of discovered edges
    """
    edges: list[DiscoveredEdge] = []

    # Determine file type
    suffix = Path(path).suffix.lower()

    if suffix in (".md", ".markdown"):
        edges = _extract_markdown_edges(content, path)
    elif suffix == ".py":
        edges = _extract_python_edges(content, path)
    # Could add more extractors: .ts, .tsx, .json, etc.

    return edges


def _extract_markdown_edges(content: bytes, path: str) -> list[DiscoveredEdge]:
    """Extract edges from markdown content using SpecParser."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning(f"Could not decode {path} as UTF-8")
        return []

    parser = SpecParser()
    result = parser.parse_content(path, text)

    return [
        DiscoveredEdge(
            edge_type=edge.edge_type.name.lower(),
            target=edge.target,
            line_number=edge.line_number or 0,  # Default to 0 if not known
            context=edge.context or "",
        )
        for edge in result.edges
    ]


def _extract_python_edges(content: bytes, path: str) -> list[DiscoveredEdge]:
    """
    Extract edges from Python content.

    Currently uses basic regex patterns. Could be extended with AST analysis.
    """
    edges: list[DiscoveredEdge] = []

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return []

    lines = text.split("\n")

    import re

    # Pattern for import statements
    import_pattern = re.compile(r"^(?:from\s+(\S+)\s+import|import\s+(\S+))")

    # Pattern for AGENTESE paths in docstrings/comments
    agentese_pattern = re.compile(r"((?:world|self|concept|void|time)\.[a-z][a-z0-9_.]*)")

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Check for imports
        import_match = import_pattern.match(stripped)
        if import_match:
            module = import_match.group(1) or import_match.group(2)
            if module:
                edges.append(
                    DiscoveredEdge(
                        edge_type="references",
                        target=module,
                        line_number=line_num,
                        context=stripped[:100],
                    )
                )

        # Check for AGENTESE paths
        for match in agentese_pattern.finditer(line):
            edges.append(
                DiscoveredEdge(
                    edge_type="references",
                    target=match.group(1),
                    line_number=line_num,
                    context=stripped[:100],
                )
            )

    return edges


# =============================================================================
# Ingestor
# =============================================================================


class Ingestor:
    """
    Core ingestion logic.

    Composes:
    - SovereignStore: For storing sovereign copies
    - WitnessPersistence: For creating witness marks

    Example:
        >>> ingestor = Ingestor(store, witness)
        >>> result = await ingestor.ingest(event)
        >>> print(f"Ingested v{result.version} with {result.edge_count} edges")
    """

    def __init__(
        self,
        store: SovereignStore,
        witness: "WitnessPersistence | None" = None,
    ) -> None:
        """
        Initialize the ingestor.

        Args:
            store: The sovereign store
            witness: Optional witness persistence (for marks)
        """
        self.store = store
        self.witness = witness

    async def ingest(
        self,
        event: IngestEvent,
        author: str = "system",
    ) -> IngestedEntity:
        """
        Ingest a document.

        The full ingestion flow:
        1. Create birth certificate (witness mark)
        2. Store sovereign copy
        3. Extract edges at ingest time
        4. Create edge marks (witness each discovery)
        5. Store derived data in overlay

        Args:
            event: The ingest event
            author: Who is ingesting (for witness marks)

        Returns:
            IngestedEntity with all mark references
        """
        logger.debug(f"Ingesting {event.claimed_path} from {event.source}")

        # 1. Create birth certificate (Law 1: No Entity Without Witness)
        birth_mark_id = await self._create_birth_mark(event, author)

        # 2. Store sovereign copy (Law 0: No Entity Without Copy)
        version = await self.store.store_version(
            path=event.claimed_path,
            content=event.content,
            ingest_mark=birth_mark_id,
            metadata={
                "source": event.source,
                "content_hash": event.content_hash,
                "source_timestamp": event.source_timestamp.isoformat()
                if event.source_timestamp
                else None,
                "source_author": event.source_author,
            },
        )

        # 3. Extract edges AT INGEST TIME (key insight!)
        edges = extract_edges(event.content, event.claimed_path)
        logger.debug(f"Discovered {len(edges)} edges in {event.claimed_path}")

        # 4. Create edge marks (Law 2: No Edge Without Witness)
        edge_mark_ids = await self._create_edge_marks(
            event.claimed_path,
            edges,
            parent_mark_id=birth_mark_id,
            author=author,
        )

        # 5. Store derived data in overlay
        # Note: If no witness, edge_mark_ids may be empty — we still store edges
        edge_data = []
        for i, e in enumerate(edges):
            mark_id = edge_mark_ids[i] if i < len(edge_mark_ids) else None
            edge_data.append(
                {
                    "type": e.edge_type,
                    "target": e.target,
                    "line": e.line_number,
                    "context": e.context,
                    "mark_id": mark_id,
                }
            )

        await self.store.store_overlay(
            event.claimed_path,
            "edges",
            {
                "edges": edge_data,
                "count": len(edges),
                "ingest_mark": birth_mark_id,
            },
        )

        # Get the full entity
        entity = await self.store.get_current(event.claimed_path)

        return IngestedEntity(
            path=event.claimed_path,
            version=version,
            ingest_mark_id=birth_mark_id,
            edge_mark_ids=edge_mark_ids,
            entity=entity,
        )

    async def _create_birth_mark(
        self,
        event: IngestEvent,
        author: str,
    ) -> str:
        """
        Create the birth certificate mark for an ingest.

        Returns a mark ID (or placeholder if no witness).
        """
        if self.witness is None:
            # No witness available — return placeholder
            import uuid

            return f"unwitnessed-{uuid.uuid4().hex[:12]}"

        result = await self.witness.save_mark(
            action=f"entity.ingest: {event.claimed_path}",
            reasoning=f"Document crossed the membrane from {event.source}",
            principles=["composable"],  # Ingest enables composition
            tags=[
                "ingest",
                f"source:{event.source.split(':')[0]}",  # e.g., "source:git"
            ],
            author=author,
        )

        return result.mark_id

    async def _create_edge_marks(
        self,
        path: str,
        edges: list[DiscoveredEdge],
        parent_mark_id: str,
        author: str,
    ) -> list[str]:
        """
        Create witness marks for each discovered edge.

        All edge marks link to the birth mark as parent.
        """
        if self.witness is None or not edges:
            return []

        mark_ids = []

        for edge in edges:
            result = await self.witness.save_mark(
                action=f"edge.discovered: {edge.edge_type} → {edge.target}",
                reasoning=f"Line {edge.line_number}: {edge.context[:50]}",
                tags=[
                    "edge",
                    f"edge:{edge.edge_type}",
                    f"spec:{path}",
                ],
                author=author,
                parent_mark_id=parent_mark_id,
            )
            mark_ids.append(result.mark_id)

        return mark_ids

    async def reingest(
        self,
        path: str,
        new_content: bytes,
        source: str = "sync",
        author: str = "system",
    ) -> IngestedEntity:
        """
        Re-ingest an entity with new content.

        This is called during sync when we accept a change.
        Creates a new version with its own witness trail.

        Args:
            path: The entity path
            new_content: The new content
            source: Where it came from
            author: Who is ingesting

        Returns:
            IngestedEntity with new version
        """
        import hashlib

        event = IngestEvent(
            source=f"reingest:{source}",
            content_hash=hashlib.sha256(new_content).hexdigest(),
            content=new_content,
            claimed_path=path,
        )

        return await self.ingest(event, author=author)


# =============================================================================
# Convenience Functions
# =============================================================================


async def ingest_file(
    file_path: Path,
    store: SovereignStore,
    witness: "WitnessPersistence | None" = None,
    source: str = "file",
    author: str = "system",
) -> IngestedEntity:
    """
    Ingest a file from the filesystem.

    Convenience function that creates an IngestEvent from a file.

    Args:
        file_path: Path to the file
        store: The sovereign store
        witness: Optional witness persistence
        source: Source identifier
        author: Who is ingesting

    Returns:
        IngestedEntity
    """
    event = IngestEvent.from_file(file_path, source=source)
    ingestor = Ingestor(store, witness)
    return await ingestor.ingest(event, author=author)


async def ingest_content(
    content: bytes | str,
    claimed_path: str,
    store: SovereignStore,
    witness: "WitnessPersistence | None" = None,
    source: str = "memory",
    author: str = "system",
) -> IngestedEntity:
    """
    Ingest content directly.

    Convenience function for in-memory content.

    Args:
        content: The content (bytes or str)
        claimed_path: Where it should live
        store: The sovereign store
        witness: Optional witness persistence
        source: Source identifier
        author: Who is ingesting

    Returns:
        IngestedEntity
    """
    event = IngestEvent.from_content(content, claimed_path, source=source)
    ingestor = Ingestor(store, witness)
    return await ingestor.ingest(event, author=author)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core
    "Ingestor",
    "DiscoveredEdge",
    "extract_edges",
    # Convenience
    "ingest_file",
    "ingest_content",
]
