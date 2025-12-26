"""
Sovereign Integration: The protocol for moving files from uploads/ to proper folders.

> *"Integration is witness. Every file crossing the threshold is marked."*

This module implements the Integration Protocol from the Zero Seed Genesis Grand Strategy.
When a file moves from uploads/ to its destination, it undergoes full analysis and
integration into the kgents cosmos.

Integration Protocol (9 Steps):
    1. Create witness mark for the integration
    2. Analyze content for layer assignment (use Galois)
    3. Create K-Block (one doc = one K-Block heuristic)
    4. Discover edges (what does this relate to?)
    5. Attach portal tokens
    6. Identify concepts (axioms, constructs)
    7. Check for contradictions with existing content
    8. Move file to destination
    9. Add to cosmos feed

Philosophy:
    "Moving a file is not a file operation. It's an epistemological event.
     The file crosses from potential to actual, from unmapped to witnessed."

Laws:
    Law 1: Integration is never silent—always witnessed
    Law 2: Integration suggests, never forces—Linear philosophy
    Law 3: Integration is complete or it's not integration

See: plans/zero-seed-genesis-grand-strategy.md (Phase 2, Section 5.2)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Integration Types
# =============================================================================


@dataclass
class DiscoveredEdge:
    """
    An edge discovered during integration.

    Attributes:
        source_path: Path of the integrating file
        target_path: Path of the target (what it relates to)
        edge_type: Type of edge (references, implements, extends, etc.)
        confidence: Confidence score (0.0-1.0)
        context: Surrounding text that suggests this edge
    """

    source_path: str
    target_path: str
    edge_type: str
    confidence: float
    context: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_path": self.source_path,
            "target_path": self.target_path,
            "edge_type": self.edge_type,
            "confidence": self.confidence,
            "context": self.context,
        }


@dataclass
class PortalToken:
    """
    A portal token extracted from content.

    Portal tokens are kgents-native links: [[concept.entity]] or [[path/to/file.md]]

    Attributes:
        token: The raw token string (e.g., "concept.entity")
        token_type: Type of token ("concept" or "path")
        resolved_target: What this token resolves to
        line_number: Line number where token appears
    """

    token: str
    token_type: str  # "concept" | "path"
    resolved_target: str | None = None
    line_number: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "token": self.token,
            "token_type": self.token_type,
            "resolved_target": self.resolved_target,
            "line_number": self.line_number,
        }


@dataclass
class IdentifiedConcept:
    """
    A concept identified in the content.

    Concepts are axioms, constructs, principles, laws, etc.

    Attributes:
        name: Concept name
        concept_type: Type of concept ("axiom", "construct", "law", "principle")
        definition: Definition text
        layer: Layer assignment (1-7)
        galois_loss: Coherence score
    """

    name: str
    concept_type: str
    definition: str
    layer: int
    galois_loss: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "concept_type": self.concept_type,
            "definition": self.definition,
            "layer": self.layer,
            "galois_loss": self.galois_loss,
        }


@dataclass
class Contradiction:
    """
    A contradiction detected during integration.

    Attributes:
        new_content_hash: Hash of the new content
        existing_path: Path of existing content that contradicts
        strength: Contradiction strength (0.0-1.0)
        description: Human-readable description
        super_additive_loss: The super-additive loss (L(A+B) - (L(A) + L(B)))
    """

    new_content_hash: str
    existing_path: str
    strength: float
    description: str
    super_additive_loss: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "new_content_hash": self.new_content_hash,
            "existing_path": self.existing_path,
            "strength": self.strength,
            "description": self.description,
            "super_additive_loss": self.super_additive_loss,
        }


@dataclass
class IntegrationResult:
    """
    Result of integrating a file from uploads/.

    Attributes:
        source_path: Original path in uploads/
        destination_path: Final destination path
        kblock_id: ID of created K-Block (if applicable)
        witness_mark_id: ID of integration witness mark
        layer: Assigned layer (1-7)
        galois_loss: Coherence score
        edges: Discovered edges
        portal_tokens: Extracted portal tokens
        concepts: Identified concepts
        contradictions: Detected contradictions
        integrated_at: Timestamp of integration
        success: Whether integration succeeded
        error: Error message if failed
    """

    source_path: str
    destination_path: str
    kblock_id: str | None = None
    witness_mark_id: str | None = None
    layer: int | None = None
    galois_loss: float = 1.0
    edges: list[DiscoveredEdge] = field(default_factory=list)
    portal_tokens: list[PortalToken] = field(default_factory=list)
    concepts: list[IdentifiedConcept] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    integrated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_path": self.source_path,
            "destination_path": self.destination_path,
            "kblock_id": self.kblock_id,
            "witness_mark_id": self.witness_mark_id,
            "layer": self.layer,
            "galois_loss": self.galois_loss,
            "edges": [edge.to_dict() for edge in self.edges],
            "portal_tokens": [token.to_dict() for token in self.portal_tokens],
            "concepts": [concept.to_dict() for concept in self.concepts],
            "contradictions": [c.to_dict() for c in self.contradictions],
            "integrated_at": self.integrated_at.isoformat(),
            "success": self.success,
            "error": self.error,
        }


# =============================================================================
# Integration Service
# =============================================================================


class IntegrationService:
    """
    Service for integrating files from uploads/ into the kgents cosmos.

    Implements the 9-step Integration Protocol.
    """

    def __init__(
        self,
        uploads_root: Path,
        kgents_root: Path,
    ):
        """
        Initialize integration service.

        Args:
            uploads_root: Path to uploads/ directory
            kgents_root: Root path of kgents workspace
        """
        self.uploads_root = uploads_root
        self.kgents_root = kgents_root

    async def integrate(
        self, source_path: str, destination_path: str
    ) -> IntegrationResult:
        """
        Integrate a file from uploads/ to its destination.

        Executes all 9 steps of the Integration Protocol.

        Args:
            source_path: Relative path in uploads/ (e.g., "my-doc.md")
            destination_path: Destination path relative to kgents root (e.g., "spec/protocols/my-doc.md")

        Returns:
            IntegrationResult with all discovered information
        """
        result = IntegrationResult(
            source_path=source_path, destination_path=destination_path
        )

        try:
            # Read source content
            source_file = self.uploads_root / source_path
            if not source_file.exists():
                result.success = False
                result.error = f"Source file not found: {source_path}"
                return result

            content = source_file.read_bytes()

            # STEP 1: Create witness mark for the integration
            logger.info(f"Step 1: Creating witness mark for {source_path}")
            result.witness_mark_id = await self._create_witness_mark(
                source_path, destination_path, content
            )

            # STEP 2: Analyze content for layer assignment (use Galois)
            logger.info(f"Step 2: Analyzing content for layer assignment")
            result.layer, result.galois_loss = await self._assign_layer(content)

            # STEP 2b: Extract portal tokens (needed for K-Block creation)
            logger.info(f"Step 2b: Extracting portal tokens")
            result.portal_tokens = await self._extract_portal_tokens(content)

            # STEP 3: Create K-Block (one doc = one K-Block heuristic)
            logger.info(f"Step 3: Creating K-Block with portal tokens")
            result.kblock_id = await self._create_kblock(
                destination_path, content, result.layer, result.galois_loss,
                portal_tokens=result.portal_tokens
            )

            # STEP 4: Discover edges (what does this relate to?)
            logger.info(f"Step 4: Discovering edges")
            result.edges = await self._discover_edges(content, destination_path)

            # STEP 4b: Persist discovered edges
            logger.info(f"Step 4b: Persisting edges")
            await self._persist_edges(result.edges, result.witness_mark_id)

            # STEP 6: Identify concepts (axioms, constructs)
            logger.info(f"Step 6: Identifying concepts")
            result.concepts = await self._identify_concepts(content, result.layer)

            # STEP 7: Check for contradictions with existing content
            logger.info(f"Step 7: Checking for contradictions")
            result.contradictions = await self._find_contradictions(
                content, destination_path
            )

            # STEP 8: Move file to destination
            logger.info(f"Step 8: Moving file to {destination_path}")
            await self._move_file(source_file, self.kgents_root / destination_path)

            # STEP 9: Add to cosmos feed
            logger.info(f"Step 9: Adding to cosmos feed")
            await self._add_to_cosmos(result)

            logger.info(f"Integration complete: {source_path} -> {destination_path}")
            result.success = True

        except Exception as e:
            logger.error(f"Integration failed: {e}", exc_info=True)
            result.success = False
            result.error = str(e)

        return result

    async def _create_witness_mark(
        self, source_path: str, destination_path: str, content: bytes
    ) -> str:
        """
        Step 1: Create witness mark for the integration.

        Args:
            source_path: Source path in uploads/
            destination_path: Destination path
            content: File content

        Returns:
            Mark ID
        """
        from services.witness import (
            Mark,
            MarkStore,
            Response,
            Stimulus,
            UmweltSnapshot,
            get_mark_store,
        )

        # Create integration mark
        try:
            content_preview = content[:200].decode("utf-8", errors="ignore")
        except Exception:
            content_preview = f"<binary content, {len(content)} bytes>"

        mark = Mark(
            origin="sovereign",
            domain="system",
            stimulus=Stimulus(
                kind="file_upload",
                content=f"File uploaded: {source_path}",
                source="uploads",
                metadata={
                    "source_path": source_path,
                    "destination_path": destination_path,
                    "size_bytes": len(content),
                },
            ),
            response=Response(
                kind="integration",
                content=f"Integrating {source_path} -> {destination_path}",
                success=True,
                metadata={
                    "content_preview": content_preview,
                    "size_bytes": len(content),
                },
            ),
            umwelt=UmweltSnapshot.system(),
            tags=("file_integration", "sovereign", "uploads"),
        )

        # Persist mark
        store = get_mark_store()
        store.append(mark)

        logger.debug(f"Created witness mark: {mark.id}")
        return str(mark.id)

    async def _assign_layer(self, content: bytes) -> tuple[int, float]:
        """
        Step 2: Analyze content for layer assignment using Galois.

        Args:
            content: File content

        Returns:
            Tuple of (layer, galois_loss)
        """
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            # Binary file, default to implementation layer
            logger.debug("Binary content detected, assigning to L5 (implementation)")
            return 5, 0.6

        # Try to use Galois service for layer assignment
        try:
            from services.zero_seed.galois.galois_loss import (
                GaloisLossComputer,
                assign_layer_via_galois,
            )

            computer = GaloisLossComputer()
            assignment = await assign_layer_via_galois(text, computer)

            logger.debug(
                f"Galois assigned layer {assignment.layer} with loss {assignment.loss:.2f}"
            )
            logger.debug(f"Insight: {assignment.insight}")

            return assignment.layer, assignment.loss

        except ImportError:
            logger.warning("Galois service not available, using heuristic layer assignment")
        except Exception as e:
            logger.warning(f"Galois layer assignment failed: {e}, falling back to heuristics")

        # Fallback: Use simple heuristics based on content
        text_lower = text.lower()

        if "axiom" in text_lower or "principle" in text_lower:
            layer = 1  # L1: Axioms
            galois_loss = 0.1
        elif "value" in text_lower or "ethical" in text_lower:
            layer = 2  # L2: Values
            galois_loss = 0.15
        elif "goal" in text_lower or "objective" in text_lower:
            layer = 3  # L3: Goals
            galois_loss = 0.25
        elif "spec" in text_lower or "protocol" in text_lower:
            layer = 4  # L4: Specifications
            galois_loss = 0.35
        elif "impl" in text_lower or "implementation" in text_lower or "def " in text or "class " in text:
            layer = 5  # L5: Implementation
            galois_loss = 0.5
        elif "reflection" in text_lower or "retrospective" in text_lower:
            layer = 6  # L6: Reflection
            galois_loss = 0.65
        else:
            layer = 7  # L7: Representation/Documentation
            galois_loss = 0.7

        logger.debug(f"Heuristic assigned layer {layer} with estimated loss {galois_loss:.2f}")
        return layer, galois_loss

    async def _create_kblock(
        self,
        path: str,
        content: bytes,
        layer: int,
        galois_loss: float,
        portal_tokens: list[PortalToken] | None = None,
    ) -> str | None:
        """
        Step 3: Create K-Block (one doc = one K-Block heuristic).

        Args:
            path: Destination path
            content: File content
            layer: Assigned layer
            galois_loss: Coherence score
            portal_tokens: Optional portal tokens to attach

        Returns:
            K-Block ID if created, None otherwise
        """
        # Only create K-Blocks for markdown files
        if not path.endswith((".md", ".markdown")):
            logger.debug(f"Skipping K-Block creation for non-markdown file: {path}")
            return None

        try:
            from services.k_block.core.kblock import KBlock, generate_kblock_id

            # Decode content
            try:
                text_content = content.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning(f"Could not decode content as UTF-8: {path}")
                return None

            # Create K-Block
            kblock_id = generate_kblock_id()

            # Prepare tags from portal tokens
            tags = []
            if portal_tokens:
                # Add portal tokens as tags for searchability
                tags.extend([f"portal:{token.token}" for token in portal_tokens])

            kblock = KBlock(
                id=kblock_id,
                path=path,
                content=text_content,
                base_content=text_content,
                zero_seed_layer=layer,
                confidence=1.0 - galois_loss,  # Convert loss to confidence
                tags=tags,
            )

            # Store K-Block in a temporary registry for later persistence
            # This will be persisted in Step 9 when we add to cosmos
            if not hasattr(self, '_kblocks_pending'):
                self._kblocks_pending = {}
            self._kblocks_pending[str(kblock_id)] = kblock

            logger.debug(
                f"Created K-Block: {kblock_id} (layer={layer}, loss={galois_loss:.2f}, "
                f"portal_tokens={len(portal_tokens) if portal_tokens else 0})"
            )
            return str(kblock_id)

        except ImportError:
            logger.warning("K-Block service not available, using placeholder ID")
            import hashlib

            kblock_id = f"kblock-{hashlib.sha256(content).hexdigest()[:12]}"
            logger.debug(f"Created placeholder K-Block: {kblock_id}")
            return kblock_id

    async def _discover_edges(
        self, content: bytes, source_path: str
    ) -> list[DiscoveredEdge]:
        """
        Step 4: Discover edges (what does this relate to?).

        Now uses EdgeDiscoveryService for semantic edge detection beyond
        simple markdown links.

        Args:
            content: File content
            source_path: Source file path

        Returns:
            List of discovered edges
        """
        edges: list[DiscoveredEdge] = []

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            logger.debug("Cannot extract edges from binary file")
            return edges

        # Try to use EdgeDiscoveryService for enhanced discovery
        try:
            from services.k_block.core.edge_discovery import get_edge_discovery_service

            service = get_edge_discovery_service(self.kgents_root)

            # TODO: Build corpus from existing K-Blocks for semantic matching
            # For now, use simple discovery without corpus
            discovered = service.discover_edges(
                content=text,
                source_path=source_path,
                source_layer=None,  # Layer will be assigned in step 2
                corpus=None,  # No corpus yet
            )

            # Convert from edge_discovery.DiscoveredEdge to integration.DiscoveredEdge
            for edge in discovered:
                edges.append(
                    DiscoveredEdge(
                        source_path=edge.source_id,
                        target_path=edge.target_id,
                        edge_type=edge.kind.value,
                        confidence=edge.confidence,
                        context=edge.reasoning,
                    )
                )

            logger.debug(
                f"Discovered {len(edges)} edges using EdgeDiscoveryService "
                f"({len([e for e in discovered if e.kind.value in ('mentions', 'similar_to', 'contradicts')])} semantic)"
            )

        except ImportError:
            logger.warning("EdgeDiscoveryService not available, falling back to simple regex")

            # Fallback: Simple markdown link extraction (original logic)
            import re

            link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
            matches = re.findall(link_pattern, text)

            for link_text, link_target in matches:
                # Skip external URLs
                if link_target.startswith(("http://", "https://")):
                    continue

                edges.append(
                    DiscoveredEdge(
                        source_path=source_path,
                        target_path=link_target,
                        edge_type="references",
                        confidence=0.8,
                        context=link_text,
                    )
                )

            logger.debug(f"Discovered {len(edges)} edges (fallback mode)")

        return edges

    async def _extract_portal_tokens(self, content: bytes) -> list[PortalToken]:
        """
        Step 5: Extract portal tokens (kgents-native links).

        Args:
            content: File content

        Returns:
            List of portal tokens
        """
        tokens: list[PortalToken] = []

        try:
            text = content.decode("utf-8")

            # Simple regex for portal tokens: [[token]]
            import re

            token_pattern = r"\[\[([^\]]+)\]\]"
            matches = re.findall(token_pattern, text)

            for token in matches:
                # Determine token type
                if "." in token and not token.endswith(".md"):
                    token_type = "concept"  # e.g., [[concept.entity]]
                else:
                    token_type = "path"  # e.g., [[path/to/file.md]]

                tokens.append(
                    PortalToken(
                        token=token, token_type=token_type, resolved_target=None
                    )
                )

            logger.debug(f"Extracted {len(tokens)} portal tokens")

        except UnicodeDecodeError:
            logger.debug("Cannot extract portal tokens from binary file")

        return tokens

    async def _identify_concepts(
        self, content: bytes, layer: int
    ) -> list[IdentifiedConcept]:
        """
        Step 6: Identify concepts (axioms, constructs, principles, laws).

        Args:
            content: File content
            layer: Assigned layer

        Returns:
            List of identified concepts
        """
        concepts: list[IdentifiedConcept] = []

        try:
            text = content.decode("utf-8")

            # Simple heuristics for concept identification
            import re

            # Look for axiom definitions
            axiom_pattern = r"(?:^|\n)(?:##\s+)?(?:Axiom|AXIOM)\s+([A-Z0-9]+):?\s+(.+?)(?:\n|$)"
            for match in re.finditer(axiom_pattern, text, re.MULTILINE):
                name = match.group(1)
                definition = match.group(2)
                concepts.append(
                    IdentifiedConcept(
                        name=name,
                        concept_type="axiom",
                        definition=definition,
                        layer=1,  # Axioms are always L1
                        galois_loss=0.05,
                    )
                )

            # Look for law definitions
            law_pattern = r"(?:^|\n)(?:##\s+)?(?:Law|LAW)\s+(\d+):?\s+(.+?)(?:\n|$)"
            for match in re.finditer(law_pattern, text, re.MULTILINE):
                name = f"Law {match.group(1)}"
                definition = match.group(2)
                concepts.append(
                    IdentifiedConcept(
                        name=name,
                        concept_type="law",
                        definition=definition,
                        layer=layer,
                        galois_loss=0.1,
                    )
                )

            logger.debug(f"Identified {len(concepts)} concepts")

        except UnicodeDecodeError:
            logger.debug("Cannot identify concepts in binary file")

        return concepts

    async def _find_contradictions(
        self, content: bytes, path: str
    ) -> list[Contradiction]:
        """
        Step 7: Check for contradictions with existing content.

        Uses ContradictionDetector to find super-additive loss pairs between
        the new content and existing K-Blocks in the corpus.

        Philosophy:
            "Contradictions are not errors. They are invitations to grow."
            - Zero Seed Grand Strategy, Part II, LAW 4

        Args:
            content: File content
            path: Destination path

        Returns:
            List of detected contradictions (opportunities for growth)
        """
        contradictions: list[Contradiction] = []

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            logger.debug("Binary content, skipping contradiction detection")
            return contradictions

        # Create a temporary K-Block for the new content
        try:
            from services.contradiction.detection import ContradictionDetector
            from services.k_block.core.kblock import KBlock as KBlockClass, KBlockId
            from services.zero_seed.galois.galois_loss import GaloisLossComputer
            import hashlib

            # Create temporary K-Block for the new content
            content_hash = hashlib.sha256(content).hexdigest()[:16]
            new_kblock = KBlockClass(
                id=KBlockId(f"temp_{content_hash}"),
                path=path,
                content=text,
                base_content=text,
            )

            # Get Galois loss computer for semantic comparison
            galois = GaloisLossComputer()

            # Get existing K-Blocks from storage for comparison
            candidates = await self._get_corpus_candidates(path)

            if not candidates:
                logger.debug("No existing K-Blocks in corpus for contradiction detection")
                return contradictions

            # Use ContradictionDetector for super-additive loss analysis
            detector = ContradictionDetector()

            # Detect contradictions between new content and existing corpus
            # Note: GaloisLossComputer satisfies the duck-typed interface
            # expected by ContradictionDetector (has compute_loss method)
            detected_pairs = await detector.detect_all(
                kblock=new_kblock,
                candidates=candidates,
                galois=galois,  # type: ignore[arg-type]
            )

            # Convert ContradictionPairs to integration.Contradiction format
            for pair in detected_pairs:
                if pair.is_significant:
                    # Create human-readable description
                    existing_path = pair.kblock_b.path
                    description = self._generate_contradiction_description(
                        new_path=path,
                        existing_path=existing_path,
                        strength=pair.strength,
                    )

                    contradictions.append(
                        Contradiction(
                            new_content_hash=content_hash,
                            existing_path=existing_path,
                            strength=pair.strength,
                            description=description,
                            super_additive_loss=pair.strength,
                        )
                    )

                    logger.info(
                        f"Contradiction detected: {path} <-> {existing_path} "
                        f"(strength={pair.strength:.3f})"
                    )

            if contradictions:
                logger.info(
                    f"Found {len(contradictions)} contradiction(s) - these are "
                    f"opportunities for growth, not errors"
                )

        except ImportError as e:
            logger.debug(f"Contradiction detection services not available: {e}")
        except Exception as e:
            logger.warning(f"Contradiction detection failed: {e}")

        logger.debug(f"Found {len(contradictions)} contradictions")
        return contradictions

    async def _get_corpus_candidates(self, path: str) -> list[Any]:
        """
        Get K-Blocks from corpus for contradiction comparison.

        Strategy:
        1. First, get K-Blocks in the same directory (most likely to contradict)
        2. Then, get K-Blocks at the same layer (semantic similarity)
        3. Limit to a reasonable number for performance

        Args:
            path: Path of the new content

        Returns:
            List of candidate K-Blocks for comparison
        """
        from pathlib import Path as PathLib

        candidates = []
        MAX_CANDIDATES = 20  # Limit for performance

        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )
            from sqlalchemy import select
            from models.kblock import KBlock as KBlockModel

            storage = await get_postgres_zero_seed_storage()

            # Get directory path for related file filtering
            parent_dir = str(PathLib(path).parent)

            # Query candidates from PostgreSQL
            async with storage._session_factory() as session:
                # First priority: K-Blocks in the same directory
                stmt = (
                    select(KBlockModel)
                    .where(KBlockModel.path.like(f"{parent_dir}%"))
                    .limit(MAX_CANDIDATES // 2)
                )
                result = await session.execute(stmt)
                same_dir_kblocks = result.scalars().all()

                # Convert DB models to K-Block instances
                for db_kblock in same_dir_kblocks:
                    kblock = await storage.get_node(db_kblock.id)
                    if kblock:
                        candidates.append(kblock)

                # If we have room, add more candidates from same layer
                remaining = MAX_CANDIDATES - len(candidates)
                if remaining > 0:
                    # Get layer-related candidates (prefer axiomatic layers 1-3)
                    stmt = (
                        select(KBlockModel)
                        .where(KBlockModel.zero_seed_layer.in_([1, 2, 3]))
                        .where(~KBlockModel.path.like(f"{parent_dir}%"))  # Avoid duplicates
                        .limit(remaining)
                    )
                    result = await session.execute(stmt)
                    layer_kblocks = result.scalars().all()

                    for db_kblock in layer_kblocks:
                        kblock = await storage.get_node(db_kblock.id)
                        if kblock:
                            candidates.append(kblock)

            logger.debug(
                f"Found {len(candidates)} corpus candidates for contradiction detection "
                f"(same_dir: {len(same_dir_kblocks)}, layers: {len(candidates) - len(same_dir_kblocks)})"
            )

        except ImportError:
            logger.debug("PostgreSQL storage not available for corpus query")
        except Exception as e:
            logger.warning(f"Failed to query corpus candidates: {e}")

        return candidates

    def _generate_contradiction_description(
        self, new_path: str, existing_path: str, strength: float
    ) -> str:
        """
        Generate a human-readable description of a contradiction.

        The description is framed as an opportunity for growth, not an error.

        Args:
            new_path: Path of the new content
            existing_path: Path of the existing content
            strength: Contradiction strength

        Returns:
            Human-readable description
        """
        if strength >= 0.5:
            severity = "strong"
            suggestion = "consider reconciling or creating a synthesis"
        elif strength >= 0.3:
            severity = "moderate"
            suggestion = "review for potential conflicts"
        else:
            severity = "mild"
            suggestion = "may represent productive tension"

        return (
            f"A {severity} contradiction detected between '{new_path}' and "
            f"'{existing_path}'. This {suggestion}. "
            f"(Super-additive loss: {strength:.3f})"
        )

    async def _persist_edges(
        self, edges: list[DiscoveredEdge], witness_mark_id: str | None
    ) -> None:
        """
        Step 4b: Persist discovered edges to storage.

        Args:
            edges: Discovered edges to persist
            witness_mark_id: Witness mark ID linking this edge creation
        """
        if not edges:
            logger.debug("No edges to persist")
            return

        try:
            from services.providers import get_sovereign_store

            store = await get_sovereign_store()

            for edge in edges:
                # Persist edge to sovereign store
                edge_id = await store.add_edge(
                    from_path=edge.source_path,
                    to_path=edge.target_path,
                    edge_type=edge.edge_type,
                    mark_id=witness_mark_id,
                    context=edge.context,
                )
                logger.debug(
                    f"Persisted edge {edge_id}: {edge.source_path} --[{edge.edge_type}]--> {edge.target_path}"
                )

            logger.info(f"Persisted {len(edges)} edges to storage")

        except ImportError:
            logger.warning("Sovereign store not available, skipping edge persistence")
        except Exception as e:
            logger.warning(f"Failed to persist edges: {e}")

    async def _move_file(self, source: Path, destination: Path) -> None:
        """
        Step 8: Move file to destination.

        Args:
            source: Source path
            destination: Destination path
        """
        # Create parent directories if needed
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        source.rename(destination)
        logger.debug(f"Moved file: {source} -> {destination}")

    async def _add_to_cosmos(self, result: IntegrationResult) -> None:
        """
        Step 9: Add K-Block to cosmos feed and emit integration event.

        This step:
        1. Persists the K-Block to storage (if created)
        2. Commits content to cosmos
        3. Emits integration event to SynergyBus

        Args:
            result: Integration result
        """
        # Step 9a: Persist K-Block to storage
        if result.kblock_id and hasattr(self, '_kblocks_pending'):
            kblock = self._kblocks_pending.get(result.kblock_id)
            if kblock:
                try:
                    from services.k_block.postgres_zero_seed_storage import (
                        get_postgres_zero_seed_storage,
                    )

                    storage = await get_postgres_zero_seed_storage()

                    # Persist K-Block to PostgreSQL
                    await storage._persist_kblock(kblock, created_by="integration")

                    logger.info(
                        f"Persisted K-Block {result.kblock_id} to storage "
                        f"(L{result.layer}, {len(result.portal_tokens)} portal tokens)"
                    )

                    # Clean up pending K-Block
                    del self._kblocks_pending[result.kblock_id]

                except ImportError:
                    logger.warning("K-Block storage not available, skipping persistence")
                except Exception as e:
                    logger.warning(f"Failed to persist K-Block to storage: {e}")

        # Step 9b: Commit content to cosmos
        try:
            from services.k_block.core.cosmos import get_cosmos

            cosmos = get_cosmos()

            # Read the file content (it's been moved to destination already)
            destination_file = self.kgents_root / result.destination_path
            if destination_file.exists():
                file_content = destination_file.read_text(encoding="utf-8")

                # Commit to cosmos with witness mark
                version_id = await cosmos.commit(
                    path=result.destination_path,
                    content=file_content,
                    actor="integration",
                    reasoning=f"Integrated from {result.source_path}",
                    mark_id=result.witness_mark_id,
                )

                logger.info(
                    f"Committed {result.destination_path} to cosmos (version={version_id})"
                )

        except Exception as e:
            logger.warning(f"Failed to commit to cosmos: {e}")

        # Step 9c: Emit integration event to SynergyBus
        try:
            from protocols.synergy import Jewel, SynergyEvent, SynergyEventType, get_synergy_bus

            bus = get_synergy_bus()

            # Create integration event
            event = SynergyEvent(
                source_jewel=Jewel.DGENT,  # Sovereign is part of data layer
                target_jewel=Jewel.BRAIN,  # Notify Brain of new content
                event_type=SynergyEventType.DATA_STORED,  # Using existing event type
                source_id=result.kblock_id or result.destination_path,
                payload={
                    "source_path": result.source_path,
                    "destination_path": result.destination_path,
                    "kblock_id": result.kblock_id,
                    "witness_mark_id": result.witness_mark_id,
                    "layer": result.layer,
                    "galois_loss": result.galois_loss,
                    "edges": [edge.to_dict() for edge in result.edges],
                    "portal_tokens": [token.to_dict() for token in result.portal_tokens],
                    "concepts": [concept.to_dict() for concept in result.concepts],
                    "contradictions": [c.to_dict() for c in result.contradictions],
                    "integrated_at": result.integrated_at.isoformat(),
                },
            )

            # Emit event (non-blocking)
            await bus.emit(event)

            logger.debug(
                f"Emitted integration event: {result.destination_path} "
                f"(kblock={result.kblock_id}, layer={result.layer}, loss={result.galois_loss:.2f})"
            )

        except ImportError:
            logger.warning("SynergyBus not available, skipping event emission")
        except Exception as e:
            logger.warning(f"Failed to emit integration event: {e}")

        logger.debug(f"Added to cosmos: {result.destination_path}")


# =============================================================================
# Service Factory
# =============================================================================


_integration_service: IntegrationService | None = None


def get_integration_service(
    uploads_root: Path | None = None, kgents_root: Path | None = None
) -> IntegrationService:
    """
    Get or create the global IntegrationService.

    Args:
        uploads_root: Path to uploads/ directory (defaults to ./uploads)
        kgents_root: Root path of kgents workspace (defaults to cwd)

    Returns:
        IntegrationService singleton
    """
    global _integration_service

    if _integration_service is None:
        if uploads_root is None:
            uploads_root = Path.cwd() / "uploads"
        if kgents_root is None:
            kgents_root = Path.cwd()

        _integration_service = IntegrationService(uploads_root, kgents_root)

    return _integration_service


def reset_integration_service() -> None:
    """Reset the global IntegrationService (for testing)."""
    global _integration_service
    _integration_service = None
