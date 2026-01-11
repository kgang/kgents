"""
Document Director REST API: Full lifecycle document management.

Provides:
- POST /api/director/upload              - Upload document, trigger analysis
- GET  /api/director/summary             - Aggregate stats (replaces ledger)
- GET  /api/director/documents           - List documents with status + filters
- GET  /api/director/:path               - Get document detail + analysis
- GET  /api/director/:path/preview       - Rendered preview (read-only)
- POST /api/director/:path/analyze       - Re-trigger analysis
- POST /api/director/:path/prompt        - Generate execution prompt
- POST /api/director/:path/capture       - Capture execution results
- GET  /api/director/:path/evidence      - Get evidence for document
- POST /api/director/:path/evidence      - Add evidence link
- POST /api/director/:path/deprecate     - Mark document deprecated

Query Parameters (GET /documents):
- status: Filter by status
- prefix: Filter by path prefix
- needs_evidence: Filter to docs without implementations/tests
- has_placeholders: Filter to docs with unresolved placeholders
- min_claims: Filter by minimum claim count

Philosophy:
    "Specs become code. Code becomes evidence. Evidence feeds back to specs."
    Upload → Analyze → Generate → Execute → Capture → Verify
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    HTTPException = None  # type: ignore[assignment, misc]

try:
    from pydantic import BaseModel, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore[assignment, misc]
    Field = lambda *args, **kwargs: None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================


def map_analysis_to_document_status(
    analysis_status: str | None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """
    Map AnalysisStatus values to DocumentStatus values.

    AnalysisStatus: pending, analyzing, analyzed, failed, stale
    DocumentStatus: uploaded, processing, ready, executed, stale, failed, ghost

    Special case: If metadata contains is_placeholder=True, return "ghost"
    regardless of analysis status.
    """
    # Check for ghost/placeholder documents first
    if metadata and metadata.get("is_placeholder", False):
        return "ghost"

    if not analysis_status:
        return "uploaded"

    status_map = {
        "pending": "uploaded",
        "analyzing": "processing",
        "analyzed": "ready",
        "failed": "failed",
        "stale": "stale",
    }
    return status_map.get(analysis_status, "uploaded")


# =============================================================================
# Pydantic Models
# =============================================================================


class DocumentStatus(str):
    """Document lifecycle status."""

    UPLOADED = "uploaded"  # Ingested, not yet analyzed
    PROCESSING = "processing"  # Analysis in progress
    READY = "ready"  # Full write access enabled
    EXECUTED = "executed"  # Code generation captured
    STALE = "stale"  # Content changed, re-analysis needed
    FAILED = "failed"  # Analysis failed
    GHOST = "ghost"  # Placeholder created from reference, awaiting real content


class UploadRequest(BaseModel):
    """Request to upload a document."""

    path: str = Field(..., description="Target path for the document")
    content: str = Field(..., description="Document content")
    source: str = Field(default="upload", description="Source identifier")
    auto_analyze: bool = Field(default=True, description="Trigger analysis immediately")


class UploadResponse(BaseModel):
    """Response from document upload."""

    path: str
    version: int
    status: str
    ingest_mark_id: str
    analysis_queued: bool
    message: str = ""


class DocumentListEntry(BaseModel):
    """Single document in list."""

    path: str
    title: str
    status: str
    version: int
    word_count: int | None = None
    claim_count: int | None = None
    impl_count: int | None = None
    test_count: int | None = None
    placeholder_count: int | None = None
    uploaded_at: str | None = None
    analyzed_at: str | None = None


class DocumentListResponse(BaseModel):
    """Response with list of documents."""

    success: bool
    total: int
    offset: int
    limit: int
    documents: list[DocumentListEntry]
    summary: dict[str, Any] | None = None


class AnticipatedImplementation(BaseModel):
    """Anticipated implementation from spec."""

    path: str
    type: str  # "anticipated" | "deferred" | "proof_of_concept"
    context: str
    spec_line: int | None = None
    owner: str | None = None
    phase: str | None = None
    resolved: bool = False


class DocumentDetailResponse(BaseModel):
    """Detailed document view."""

    success: bool
    path: str
    title: str
    status: str
    version: int
    content: str
    content_hash: str

    # Analysis results (from overlay)
    word_count: int | None = None
    heading_count: int | None = None
    claims: list[dict[str, Any]] = []
    discovered_refs: list[str] = []
    implementations: list[str] = []
    tests: list[str] = []
    spec_refs: list[str] = []

    # Anticipated implementations
    anticipated: list[AnticipatedImplementation] = []
    placeholder_paths: list[str] = []

    # Metadata
    uploaded_at: str | None = None
    analyzed_at: str | None = None
    analysis_mark_id: str | None = None
    error: str | None = None

    # Extra context (e.g., Zero Seed K-Block metadata)
    extra: dict[str, Any] | None = None


class PreviewResponse(BaseModel):
    """Rendered preview (read-only)."""

    success: bool
    path: str
    title: str
    rendered_html: str
    status: str


class AnalyzeRequest(BaseModel):
    """Request to trigger/re-trigger analysis."""

    force: bool = Field(default=False, description="Force re-analysis even if fresh")
    deep: bool = Field(default=False, description="Deep analysis with extended extraction")


class AnalyzeResponse(BaseModel):
    """Response from analysis trigger."""

    success: bool
    path: str
    status: str
    message: str
    analysis_mark_id: str | None = None
    queued: bool = False


class PromptRequest(BaseModel):
    """Request to generate execution prompt."""

    include_context: bool = Field(default=True, description="Include full spec context")
    include_tests: bool = Field(default=True, description="Request test generation")
    temperature: float = Field(default=0.0, ge=0.0, le=1.0, description="LLM temperature")


class PromptResponse(BaseModel):
    """Generated execution prompt."""

    success: bool
    spec_path: str
    prompt_text: str  # Formatted for Claude Code
    targets: list[str]  # Paths to generate
    context: dict[str, Any]
    mark_id: str  # L-2 PROMPT witness mark
    message: str = ""


class CaptureRequest(BaseModel):
    """Request to capture execution results."""

    prompt_mark_id: str = Field(..., description="Mark ID of the prompt that generated this")
    generated_files: dict[str, str] = Field(..., description="path → content")
    test_results: dict[str, Any] | None = Field(default=None, description="Test execution results")
    model: str = Field(default="claude-opus-4", description="Model used for generation")
    temperature: float = Field(default=0.0, description="Temperature used")


class CaptureResponse(BaseModel):
    """Response from execution capture."""

    success: bool
    spec_path: str
    captured_count: int
    resolved_placeholders: list[str]
    evidence_marks: list[str]  # Mark IDs created
    test_marks: list[str] = []  # L1 TEST marks if tests passed
    message: str = ""


class EvidenceEntry(BaseModel):
    """Single evidence entry."""

    mark_id: str
    file_path: str
    evidence_type: str  # "impl" | "test" | "generated" | "usage"
    action: str
    reasoning: str | None
    timestamp: str
    exists: bool  # Whether file still exists
    tags: list[str] = []


class EvidenceResponse(BaseModel):
    """Response with evidence for document."""

    success: bool
    spec_path: str
    total_evidence: int
    by_type: dict[str, int]  # type → count
    entries: list[EvidenceEntry]


class EvidenceAddRequest(BaseModel):
    """Request to add evidence link."""

    evidence_path: str = Field(..., description="Path to implementation/test file")
    evidence_type: str = Field(
        default="implementation", description="Type: implementation, test, or usage"
    )
    reasoning: str | None = Field(default=None, description="Why this is evidence")


class EvidenceAddResponse(BaseModel):
    """Response from adding evidence."""

    success: bool
    spec_path: str
    evidence_path: str
    evidence_type: str
    mark_id: str
    message: str = ""


class DeprecateRequest(BaseModel):
    """Request to deprecate a document."""

    reason: str = Field(..., description="Reason for deprecation")


class DeprecateResponse(BaseModel):
    """Response from deprecating a document."""

    success: bool
    path: str
    status: str
    mark_id: str
    message: str = ""


class DeleteResponse(BaseModel):
    """Response from deleting a document."""

    success: bool
    path: str
    mark_id: str
    message: str = ""


class RenameRequest(BaseModel):
    """Request to rename a document."""

    new_path: str = Field(..., description="New path for the document")


class RenameResponse(BaseModel):
    """Response from renaming a document."""

    success: bool
    old_path: str
    new_path: str
    mark_id: str
    message: str = ""


class SummaryResponse(BaseModel):
    """Summary statistics for all documents."""

    success: bool
    total: int
    by_status: dict[str, int]
    recent_uploads: list[DocumentListEntry]


class ParseRequest(BaseModel):
    """Request to parse document content."""

    content: str = Field(..., description="Document content to parse")
    layout_mode: str = Field(
        default="COMFORTABLE", description="Layout mode: COMPACT, COMFORTABLE, SPACIOUS"
    )


class ParseResponse(BaseModel):
    """Response from parsing document."""

    success: bool
    scene_graph: dict[str, Any]
    sections: list[dict[str, Any]]
    section_hashes: dict[int, str]
    token_count: int
    message: str = ""


# =============================================================================
# Background Analysis Helper
# =============================================================================


async def _run_analysis(path: str, store: "Any") -> None:
    """
    Background task to run deep analysis after upload.

    Flow:
    1. Emit analysis.started event
    2. Run DocumentDirector.analyze_deep()
    3. On success: Set status to ANALYZED, emit analysis.complete
    4. On failure: Set status to FAILED, emit analysis.failed

    Args:
        path: Document path to analyze
        store: SovereignStore instance
    """
    from services.director.director import DocumentDirector
    from services.director.types import DocumentTopics
    from services.sovereign.analysis import AnalysisState, AnalysisStatus
    from services.witness.bus import get_synergy_bus

    try:
        # Get bus for events
        bus = get_synergy_bus()

        # Emit started event
        await bus.publish(
            DocumentTopics.ANALYSIS_STARTED,
            {"path": path, "timestamp": datetime.now(UTC).isoformat()},
        )

        # Get witness persistence
        from services.providers import get_witness_persistence

        witness = await get_witness_persistence()

        # Run deep analysis
        director = DocumentDirector(store, witness, bus)
        crystal = await director.analyze_deep(path, author="auto-analysis")

        # Set status to ANALYZED
        await store.set_analysis_state(
            path,
            AnalysisState(
                status=AnalysisStatus.ANALYZED,
                completed_at=datetime.now(UTC).isoformat(),
                analysis_mark_id=None,  # Mark is in crystal if needed
            ),
        )

        # Emit complete event
        await bus.publish(
            DocumentTopics.ANALYSIS_COMPLETE,
            {
                "path": path,
                "claim_count": len(crystal.claims),
                "anticipated_count": len(crystal.anticipated),
                "placeholder_count": len(crystal.placeholder_paths),
                "status": "ready",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        logger.info(
            f"Auto-analysis complete for {path}: "
            f"{len(crystal.claims)} claims, {len(crystal.anticipated)} anticipated"
        )

    except Exception as e:
        logger.error(f"Auto-analysis failed for {path}: {e}", exc_info=True)

        # Set status to FAILED
        from services.sovereign.analysis import AnalysisState, AnalysisStatus

        await store.set_analysis_state(
            path,
            AnalysisState(
                status=AnalysisStatus.FAILED,
                error=str(e),
            ),
        )

        # Emit failed event
        try:
            from services.director.types import DocumentTopics
            from services.witness.bus import get_synergy_bus

            bus = get_synergy_bus()
            await bus.publish(
                DocumentTopics.ANALYSIS_FAILED,
                {
                    "path": path,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )
        except Exception as bus_error:
            logger.error(f"Failed to emit analysis.failed event: {bus_error}")


async def _get_genesis_file_as_document(path: str) -> "DocumentDetailResponse":
    """
    Load a genesis file and return as DocumentDetailResponse.

    Handles paths like: spec/genesis/L0/entity.md

    Genesis files are sovereign territory - they exist as real .md files
    with YAML frontmatter containing metadata. K-Blocks serve as rich indexes.
    """
    from pathlib import Path as PathLib

    from services.genesis.path_resolver import GenesisPathResolver
    from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage

    # Determine project root (impl/claude relative to this file)
    project_root = PathLib(__file__).parent.parent.parent

    # Convert to absolute path
    absolute_path = project_root / path

    if not absolute_path.exists():
        raise HTTPException(status_code=404, detail=f"Genesis file not found: {path}")

    # Read file content
    content = absolute_path.read_text(encoding="utf-8")

    # Parse frontmatter if present
    metadata: dict = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            import yaml

            try:
                metadata = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()
            except yaml.YAMLError:
                pass  # Proceed with empty metadata

    # Try to get K-Block for additional info
    kblock_id = GenesisPathResolver.file_to_kblock_id(path)
    kblock = None
    if kblock_id:
        try:
            storage = await get_postgres_zero_seed_storage()
            kblock = await storage.get_node(kblock_id)
        except Exception:
            pass  # K-Block lookup is optional

    # Extract info from metadata or K-Block
    layer = metadata.get("layer") or (kblock.zero_seed_layer if kblock else None) or 0
    layer_name = metadata.get("layer_name") or (kblock.zero_seed_kind if kblock else None) or "genesis"
    title = metadata.get("title") or (kblock.path.split(".")[-1] if kblock and kblock.path else path)
    galois_loss = metadata.get("galois_loss") or 0.0
    confidence = metadata.get("confidence") or (kblock.confidence if kblock else 1.0)
    derives_from = metadata.get("derives_from") or (kblock.lineage if kblock else [])
    tags = metadata.get("tags") or []

    # Get file stats
    stat = absolute_path.stat()

    return DocumentDetailResponse(
        success=True,
        path=path,
        title=title,
        status=DocumentStatus.READY,  # Genesis files are foundational
        version=1,
        content=content,  # Include frontmatter for transparency
        content_hash=str(hash(content))[:16],
        word_count=len(body.split()),
        heading_count=body.count("#"),
        claims=[],
        discovered_refs=[],
        implementations=[],
        tests=[],
        spec_refs=[],
        anticipated=[],
        placeholder_paths=[],
        uploaded_at=None,  # Genesis files are system-created
        analyzed_at=None,
        analysis_mark_id=None,
        error=None,
        extra={
            "genesis": True,
            "genesis_id": kblock_id,
            "layer": layer,
            "layer_name": layer_name,
            "galois_loss": galois_loss,
            "confidence": confidence,
            "derives_from": derives_from,
            "tags": tags,
            "file_size": stat.st_size,
            "modified_at": stat.st_mtime,
        },
    )


async def _get_kblock_as_document(path: str) -> "DocumentDetailResponse":
    """
    Convert a Zero Seed K-Block to DocumentDetailResponse format.

    Handles paths like: zero-seed/axioms/kb_xxx, zero-seed/values/kb_xxx
    """
    from services.k_block.postgres_zero_seed_storage import get_postgres_zero_seed_storage

    # Extract K-Block ID from path (last segment)
    parts = path.split("/")
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail=f"Invalid Zero Seed path: {path}")

    kblock_id = parts[-1]
    if not kblock_id.startswith("kb_"):
        raise HTTPException(status_code=400, detail=f"Invalid K-Block ID: {kblock_id}")

    # Get K-Block from storage
    storage = await get_postgres_zero_seed_storage()
    kblock = await storage.get_node(kblock_id)

    if not kblock:
        raise HTTPException(status_code=404, detail=f"K-Block not found: {kblock_id}")

    # Map layer to Zero Seed kind
    layer_kinds = {
        1: "axiom",
        2: "value",
        3: "goal",
        4: "spec",
        5: "action",
        6: "reflection",
        7: "representation",
    }
    kind = layer_kinds.get(kblock.zero_seed_layer or 0, "node")

    # Build response in DocumentDetailResponse format
    return DocumentDetailResponse(
        success=True,
        path=path,
        title=kblock.path.split(".")[-1] if kblock.path else kblock_id,
        status=DocumentStatus.READY,  # K-Blocks are foundational
        version=1,
        content=kblock.content,
        content_hash=kblock.content_hash if hasattr(kblock, "content_hash") else "",
        word_count=len(kblock.content.split()) if kblock.content else 0,
        heading_count=kblock.content.count("#") if kblock.content else 0,
        claims=[],  # K-Blocks don't have claims in the spec sense
        discovered_refs=[],
        implementations=[],
        tests=[],
        spec_refs=[],
        anticipated=[],
        placeholder_paths=[],
        uploaded_at=kblock.created_at.isoformat() if hasattr(kblock, "created_at") else None,
        analyzed_at=None,
        analysis_mark_id=None,
        error=None,
        # Add extra context for Zero Seed
        extra={
            "zero_seed": True,
            "layer": kblock.zero_seed_layer,
            "kind": kind,
            "confidence": kblock.confidence if hasattr(kblock, "confidence") else 1.0,
            "lineage": kblock.lineage if hasattr(kblock, "lineage") else [],
            "has_proof": kblock.has_proof if hasattr(kblock, "has_proof") else False,
        },
    )


# =============================================================================
# Router Factory
# =============================================================================


def create_director_router() -> APIRouter | None:
    """Create the Document Director API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, director routes disabled")
        return None

    router = APIRouter(prefix="/api/director", tags=["director"])

    # =========================================================================
    # Document Parsing Routes
    # =========================================================================

    @router.post("/parse", response_model=ParseResponse)
    async def parse_document(request: ParseRequest) -> ParseResponse:
        """
        Parse document content into SceneGraph with section detection.

        This is Phase 2 of the Document Proxy system (AD-015).
        Returns:
        - SceneGraph for rendering
        - Sections with byte ranges and hashes
        - Section hash map for incremental re-parsing

        See: spec/protocols/document-proxy.md
        """
        from protocols.agentese.projection.scene import LayoutMode
        from protocols.agentese.projection.tokens_to_scene import (
            detect_sections,
            markdown_to_scene_graph,
        )

        # Map layout mode string to enum
        layout_mode_map = {
            "COMPACT": LayoutMode.COMPACT,
            "COMFORTABLE": LayoutMode.COMFORTABLE,
            "SPACIOUS": LayoutMode.SPACIOUS,
        }
        layout_mode = layout_mode_map.get(request.layout_mode, LayoutMode.COMFORTABLE)

        # Detect sections
        sections = detect_sections(request.content)

        # Parse to SceneGraph
        scene_graph = await markdown_to_scene_graph(
            request.content,
            observer=None,
            layout_mode=layout_mode,
        )

        # Build section hash map
        section_hashes = {section.index: section.section_hash for section in sections}

        # Count tokens (nodes in scene graph)
        token_count = len(scene_graph.nodes)

        return ParseResponse(
            success=True,
            scene_graph=scene_graph.to_dict(),
            sections=[section.to_dict() for section in sections],
            section_hashes=section_hashes,
            token_count=token_count,
            message=f"Parsed {len(sections)} sections, {token_count} tokens",
        )

    # =========================================================================
    # Document Lifecycle Routes
    # =========================================================================

    @router.post("/upload", response_model=UploadResponse)
    async def upload_document(request: UploadRequest) -> UploadResponse:
        """
        Upload document and trigger analysis.

        Workflow:
        1. Ingest document into sovereign store
        2. Create birth witness mark
        3. Set status to PROCESSING (if auto_analyze=True)
        4. Spawn background task to run deep analysis
        5. Analysis emits events: started → complete/failed
        """
        from services.providers import get_sovereign_store
        from services.sovereign.ingest import Ingestor
        from services.sovereign.types import IngestEvent

        store = await get_sovereign_store()

        # Create ingest event
        event = IngestEvent.from_content(
            content=request.content.encode("utf-8"),
            claimed_path=request.path,
            source=request.source,
        )

        # Ingest
        ingestor = Ingestor(store, witness=None)
        result = await ingestor.ingest(event, author="api")

        # Set initial status and spawn analysis
        from services.sovereign.analysis import AnalysisState, AnalysisStatus

        analysis_queued = False
        status_value = "pending"

        if request.auto_analyze:
            # Set status to ANALYZING (processing)
            await store.set_analysis_state(
                request.path,
                AnalysisState(
                    status=AnalysisStatus.ANALYZING,
                    started_at=datetime.now(UTC).isoformat(),
                ),
            )

            # Spawn background analysis task
            asyncio.create_task(_run_analysis(request.path, store))
            analysis_queued = True
            status_value = "processing"
        else:
            # Set status to PENDING (awaiting manual trigger)
            await store.set_analysis_state(
                request.path,
                AnalysisState(
                    status=AnalysisStatus.PENDING,
                    started_at=None,
                ),
            )

        return UploadResponse(
            path=result.path,
            version=result.version,
            status=status_value,
            ingest_mark_id=result.ingest_mark_id,
            analysis_queued=analysis_queued,
            message="Document uploaded successfully",
        )

    @router.get("/summary", response_model=SummaryResponse)
    async def get_summary() -> SummaryResponse:
        """
        Get aggregate statistics for all documents.

        Replaces Living Spec Ledger summary functionality.

        Returns:
        - Total document count
        - Breakdown by status (uploaded, processing, ready, executed, stale, failed)
        - Recent uploads (last 10)
        """
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()
        all_paths = await store.list_all()

        # Compute status breakdown
        by_status: dict[str, int] = {
            "uploaded": 0,
            "processing": 0,
            "ready": 0,
            "executed": 0,
            "stale": 0,
            "failed": 0,
            "ghost": 0,
        }

        # Track recent uploads for later sorting
        recent_docs: list[tuple[str, str | None]] = []  # (path, created_at)

        for path in all_paths:
            state = await store.get_analysis_state(path)
            entity = await store.get_current(path)

            # Map AnalysisStatus to DocumentStatus (check is_placeholder metadata)
            analysis_status = state.status.value if state else None
            metadata = entity.metadata if entity else None
            doc_status = map_analysis_to_document_status(analysis_status, metadata)

            if doc_status in by_status:
                by_status[doc_status] += 1

            # Track for recent uploads
            if entity:
                created_at = entity.metadata.get("created_at")
                recent_docs.append((path, created_at))

        # Sort by created_at and take most recent 10
        recent_docs.sort(key=lambda x: x[1] or "", reverse=True)
        recent_paths = [path for path, _ in recent_docs[:10]]

        # Build detailed entries for recent uploads
        recent_uploads = []
        for path in recent_paths:
            entity = await store.get_current(path)
            if not entity:
                continue

            state = await store.get_analysis_state(path)
            overlay = await store.get_overlay(path, "analysis")

            doc_status = map_analysis_to_document_status(
                state.status.value if state else None,
                entity.metadata,
            )

            recent_uploads.append(
                DocumentListEntry(
                    path=path,
                    title=overlay.get("title", path) if overlay else path,
                    status=doc_status,
                    version=entity.version,
                    word_count=overlay.get("word_count") if overlay else None,
                    claim_count=len(overlay.get("claims", [])) if overlay else None,
                    impl_count=len(overlay.get("implementations", [])) if overlay else None,
                    test_count=len(overlay.get("tests", [])) if overlay else None,
                    placeholder_count=len(overlay.get("placeholder_paths", []))
                    if overlay
                    else None,
                    uploaded_at=entity.metadata.get("created_at"),
                    analyzed_at=overlay.get("analyzed_at") if overlay else None,
                )
            )

        return SummaryResponse(
            success=True,
            total=len(all_paths),
            by_status=by_status,
            recent_uploads=recent_uploads,
        )

    @router.get("/documents", response_model=DocumentListResponse)
    async def list_documents(
        status: str | None = Query(default=None, description="Filter by status"),
        prefix: str = Query(default="", description="Filter by path prefix"),
        needs_evidence: bool = Query(
            default=False, description="Filter to documents without implementations/tests"
        ),
        has_placeholders: bool = Query(
            default=False, description="Filter to documents with unresolved placeholders"
        ),
        min_claims: int | None = Query(
            default=None, ge=0, description="Filter by minimum claim count"
        ),
        sort_by: str = Query(default="path", description="Sort field"),
        limit: int = Query(default=100, ge=1, le=500, description="Max results"),
        offset: int = Query(default=0, ge=0, description="Pagination offset"),
    ) -> DocumentListResponse:
        """
        List all documents with status.

        Shows documents from sovereign store with analysis state.
        """
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()
        all_paths = await store.list_all()

        # Filter by prefix
        if prefix:
            all_paths = [p for p in all_paths if p.startswith(prefix)]

        # Apply filters - need to check overlay data
        filtered = []
        for path in all_paths:
            state = await store.get_analysis_state(path)
            overlay = await store.get_overlay(path, "analysis")
            entity = await store.get_current(path)

            # Filter by status (map DocumentStatus to AnalysisStatus for comparison)
            if status:
                analysis_status = state.status.value if state else None
                metadata = entity.metadata if entity else None
                doc_status = map_analysis_to_document_status(analysis_status, metadata)
                if doc_status != status:
                    continue

            # Filter by needs_evidence (no implementations or tests)
            if needs_evidence and overlay:
                impls = overlay.get("implementations", [])
                tests = overlay.get("tests", [])
                if impls or tests:
                    continue

            # Filter by has_placeholders
            if has_placeholders and overlay:
                placeholders = overlay.get("placeholder_paths", [])
                if not placeholders:
                    continue

            # Filter by min_claims
            if min_claims is not None and overlay:
                claims = overlay.get("claims", [])
                if len(claims) < min_claims:
                    continue

            filtered.append(path)

        all_paths = filtered

        # Pagination
        total = len(all_paths)
        paths = all_paths[offset : offset + limit]

        # Build document entries
        documents = []
        for path in paths:
            entity = await store.get_current(path)
            if not entity:
                continue

            state = await store.get_analysis_state(path)
            overlay = await store.get_overlay(path, "analysis")

            doc_status = map_analysis_to_document_status(
                state.status.value if state else None,
                entity.metadata,
            )

            documents.append(
                DocumentListEntry(
                    path=path,
                    title=overlay.get("title", path) if overlay else path,
                    status=doc_status,
                    version=entity.version,
                    word_count=overlay.get("word_count") if overlay else None,
                    claim_count=len(overlay.get("claims", [])) if overlay else None,
                    impl_count=len(overlay.get("implementations", [])) if overlay else None,
                    test_count=len(overlay.get("tests", [])) if overlay else None,
                    placeholder_count=len(overlay.get("placeholder_paths", []))
                    if overlay
                    else None,
                    uploaded_at=entity.metadata.get("created_at"),
                    analyzed_at=overlay.get("analyzed_at") if overlay else None,
                )
            )

        # Build summary
        summary = {
            "total": total,
            "by_status": {},  # TODO: Compute status breakdown
        }

        return DocumentListResponse(
            success=True,
            total=total,
            offset=offset,
            limit=limit,
            documents=documents,
            summary=summary,
        )

    @router.get("/documents/{path:path}", response_model=DocumentDetailResponse)
    async def get_document_detail(path: str) -> DocumentDetailResponse:
        """
        Get document detail with full analysis.

        Returns content, analysis results, and evidence.
        For genesis files, reads from spec/genesis/ directory.
        For Zero Seed K-Block paths, delegates to K-Blocks API.
        """
        from services.providers import get_sovereign_store

        # Handle genesis file paths (spec/genesis/L0/entity.md, etc.)
        if path.startswith("spec/genesis/"):
            return await _get_genesis_file_as_document(path)

        # Handle Zero Seed K-Block paths (zero-seed/axioms/kb_xxx, zero-seed/values/kb_xxx, etc.)
        if path.startswith("zero-seed/"):
            return await _get_kblock_as_document(path)

        store = await get_sovereign_store()

        # Get entity
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Get analysis state
        state = await store.get_analysis_state(path)
        doc_status = map_analysis_to_document_status(
            state.status.value if state else None,
            entity.metadata,
        )

        # Get analysis overlay
        overlay = await store.get_overlay(path, "analysis")

        # Build anticipated implementations
        anticipated = []
        if overlay and "anticipated" in overlay:
            for ant in overlay["anticipated"]:
                anticipated.append(
                    AnticipatedImplementation(
                        path=ant["path"],
                        type=ant.get("type", "anticipated"),
                        context=ant.get("context", ""),
                        spec_line=ant.get("spec_line"),
                        owner=ant.get("owner"),
                        phase=ant.get("phase"),
                        resolved=ant.get("resolved", False),
                    )
                )

        return DocumentDetailResponse(
            success=True,
            path=path,
            title=overlay.get("title", path) if overlay else path,
            status=doc_status,
            version=entity.version,
            content=entity.content_text,
            content_hash=entity.content_hash,
            word_count=overlay.get("word_count") if overlay else None,
            heading_count=overlay.get("heading_count") if overlay else None,
            claims=overlay.get("claims", []) if overlay else [],
            discovered_refs=overlay.get("discovered_refs", []) if overlay else [],
            implementations=overlay.get("implementations", []) if overlay else [],
            tests=overlay.get("tests", []) if overlay else [],
            spec_refs=overlay.get("spec_refs", []) if overlay else [],
            anticipated=anticipated,
            placeholder_paths=overlay.get("placeholder_paths", []) if overlay else [],
            uploaded_at=entity.metadata.get("created_at"),
            analyzed_at=overlay.get("analyzed_at") if overlay else None,
            analysis_mark_id=state.analysis_mark_id if state else None,
            error=state.error if state else None,
        )

    @router.get("/documents/{path:path}/preview", response_model=PreviewResponse)
    async def preview_document(path: str) -> PreviewResponse:
        """
        Get rendered preview of document (read-only).

        Returns HTML-rendered content for display without edit access.
        """
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()

        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # TODO: Implement markdown → HTML rendering
        # For now, return raw content
        rendered_html = f"<pre>{entity.content_text}</pre>"

        state = await store.get_analysis_state(path)
        doc_status = map_analysis_to_document_status(
            state.status.value if state else None,
            entity.metadata,
        )

        overlay = await store.get_overlay(path, "analysis")
        title = overlay.get("title", path) if overlay else path

        return PreviewResponse(
            success=True,
            path=path,
            title=title,
            rendered_html=rendered_html,
            status=doc_status,
        )

    @router.post("/documents/{path:path}/analyze", response_model=AnalyzeResponse)
    async def analyze_document(path: str, request: AnalyzeRequest) -> AnalyzeResponse:
        """
        Trigger or re-trigger analysis for a document.

        Workflow:
        1. Update status to PROCESSING
        2. Run analysis (extract claims, refs, etc)
        3. Store results in overlay
        4. Update status to READY or FAILED
        5. Create analysis witness mark
        """
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()

        # Verify document exists
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Check if already analyzed and force not set
        state = await store.get_analysis_state(path)
        if state and state.status.value == "analyzed" and not request.force:
            return AnalyzeResponse(
                success=True,
                path=path,
                status="analyzed",
                message="Document already analyzed. Use force=true to re-analyze.",
                analysis_mark_id=state.analysis_mark_id,
                queued=False,
            )

        # TODO: Implement async analysis queue
        # For now, return queued status
        from services.sovereign.analysis import AnalysisState, AnalysisStatus

        await store.set_analysis_state(
            path,
            AnalysisState(
                status=AnalysisStatus.ANALYZING,
                started_at=None,  # TODO: Set timestamp
            ),
        )

        return AnalyzeResponse(
            success=True,
            path=path,
            status="processing",
            message="Analysis queued successfully",
            queued=True,
        )

    # =========================================================================
    # Code Generation Routes
    # =========================================================================

    @router.post("/documents/{path:path}/prompt", response_model=PromptResponse)
    async def generate_prompt(path: str, request: PromptRequest) -> PromptResponse:
        """
        Generate execution prompt for Claude Code.

        Creates a formatted prompt with:
        - Full spec content
        - Extracted claims
        - Anticipated implementations
        - Existing context
        - Test requirements
        """
        from services.providers import get_sovereign_store, get_witness_persistence

        store = await get_sovereign_store()
        witness = await get_witness_persistence()

        # Get document
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Get analysis
        overlay = await store.get_overlay(path, "analysis")
        if not overlay:
            raise HTTPException(
                status_code=400, detail="Document not analyzed. Run analysis first."
            )

        # Extract targets
        targets = []
        targets.extend(overlay.get("placeholder_paths", []))
        for ant in overlay.get("anticipated", []):
            if not ant.get("resolved", False):
                targets.append(ant["path"])

        # Build context
        context = {
            "claims": overlay.get("claims", []),
            "existing_refs": overlay.get("implementations", []),
            "tests": overlay.get("tests", []),
        }

        # Format prompt
        prompt_text = f"""Implement the following specification:

# Specification: {path}

{entity.content_text}

## Implementation Targets

Generate code for the following paths:
{chr(10).join(f"- {t}" for t in targets)}

## Context

Claims from spec:
{len(context["claims"])} claims extracted

Existing implementations:
{chr(10).join(f"- {r}" for r in context.get("existing_refs", []))}

## Requirements

1. Follow the spec's assertions and constraints exactly
2. Use the existing codebase patterns
{"3. Create tests for each implementation" if request.include_tests else ""}
4. Document any deviations with reasoning
"""

        # Create L-2 PROMPT witness mark
        mark = await witness.save_mark(
            action=f"Generated prompt for: {path}",
            reasoning=f"Targeting {len(targets)} implementations",
            tags=["prompt", f"spec:{path}", "codegen"],
            author="director",
        )

        return PromptResponse(
            success=True,
            spec_path=path,
            prompt_text=prompt_text,
            targets=targets,
            context=context,
            mark_id=mark.mark_id,
            message="Prompt generated successfully",
        )

    @router.post("/documents/{path:path}/capture", response_model=CaptureResponse)
    async def capture_execution(path: str, request: CaptureRequest) -> CaptureResponse:
        """
        Capture execution results back into system.

        Workflow:
        1. Ingest generated files
        2. Resolve placeholders
        3. Create evidence marks (L-1 TRACE)
        4. Create test marks if tests passed (L1 TEST)
        5. Link all marks to prompt mark (genealogy)
        """
        from services.providers import get_sovereign_store, get_witness_persistence
        from services.sovereign.ingest import Ingestor
        from services.sovereign.types import IngestEvent

        store = await get_sovereign_store()
        witness = await get_witness_persistence()

        # Verify spec exists
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Ingest generated files
        ingestor = Ingestor(store, witness=witness)
        captured_count = 0
        resolved_placeholders = []
        evidence_marks = []
        test_marks = []

        for file_path, content in request.generated_files.items():
            # Ingest
            event = IngestEvent.from_content(
                content=content.encode("utf-8"),
                claimed_path=file_path,
                source="codegen",
            )
            result = await ingestor.ingest(event, author="director")
            captured_count += 1

            # Create L-1 TRACE evidence mark
            trace_mark = await witness.save_mark(
                action=f"Generated: {file_path}",
                reasoning=f"From spec {path} via Claude Code (model={request.model}, temp={request.temperature}, prompt={request.prompt_mark_id})",
                tags=[
                    f"spec:{path}",
                    "evidence:generated",
                    f"file:{file_path}",
                    "codegen",
                ],
                author="director",
            )
            evidence_marks.append(trace_mark.mark_id)

            # Check if this resolves a placeholder
            overlay = await store.get_overlay(path, "analysis")
            if overlay:
                placeholders = overlay.get("placeholder_paths", [])
                if file_path in placeholders:
                    resolved_placeholders.append(file_path)
                    # TODO: Update overlay to mark as resolved

            # Create L1 TEST mark if tests passed
            if request.test_results:
                test_result = request.test_results.get(file_path)
                if test_result and test_result.get("passed", False):
                    test_mark = await witness.save_mark(
                        action=f"Tests passed: {file_path}",
                        reasoning=f"Generated code passes {test_result.get('count', 0)} tests",
                        tags=[
                            f"spec:{path}",
                            "evidence:test",
                            "evidence:pass",
                            f"file:{file_path}",
                        ],
                        author="director",
                    )
                    test_marks.append(test_mark.mark_id)

        return CaptureResponse(
            success=True,
            spec_path=path,
            captured_count=captured_count,
            resolved_placeholders=resolved_placeholders,
            evidence_marks=evidence_marks,
            test_marks=test_marks,
            message=f"Captured {captured_count} files successfully",
        )

    # =========================================================================
    # Evidence Routes
    # =========================================================================

    @router.get("/documents/{path:path}/evidence", response_model=EvidenceResponse)
    async def get_evidence(path: str) -> EvidenceResponse:
        """
        Get evidence for a document.

        Returns all witness marks that link to this document.
        """
        from pathlib import Path as PathLib

        from services.providers import get_sovereign_store, get_witness_persistence

        store = await get_sovereign_store()
        witness = await get_witness_persistence()

        # Verify document exists
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Query witness marks for this spec
        # TODO: Add proper tag-based querying to witness system
        # For now, return empty
        entries: list[EvidenceEntry] = []
        by_type: dict[str, int] = {
            "impl": 0,
            "test": 0,
            "generated": 0,
            "usage": 0,
        }

        return EvidenceResponse(
            success=True,
            spec_path=path,
            total_evidence=len(entries),
            by_type=by_type,
            entries=entries,
        )

    @router.post("/documents/{path:path}/evidence", response_model=EvidenceAddResponse)
    async def add_evidence(path: str, request: EvidenceAddRequest) -> EvidenceAddResponse:
        """
        Add evidence link to a document.

        Creates a witness mark linking implementation/test to spec.
        """
        from services.providers import get_sovereign_store, get_witness_persistence

        store = await get_sovereign_store()
        witness = await get_witness_persistence()

        # Verify spec exists
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Create evidence mark
        mark = await witness.save_mark(
            action=f"Evidence added: {request.evidence_path}",
            reasoning=request.reasoning or f"Links {request.evidence_type} to {path}",
            tags=[
                f"spec:{path}",
                f"evidence:{request.evidence_type}",
                f"file:{request.evidence_path}",
            ],
            author="director",
        )

        return EvidenceAddResponse(
            success=True,
            spec_path=path,
            evidence_path=request.evidence_path,
            evidence_type=request.evidence_type,
            mark_id=mark.mark_id,
            message="Evidence link created successfully",
        )

    # =========================================================================
    # Document Lifecycle Management Routes
    # =========================================================================

    @router.post("/documents/{path:path}/deprecate", response_model=DeprecateResponse)
    async def deprecate_document(path: str, request: DeprecateRequest) -> DeprecateResponse:
        """
        Mark a document as deprecated (stale).

        Workflow:
        1. Update status to STALE
        2. Create witness mark with deprecation reason
        3. Document becomes read-only until re-analysis

        Use this when:
        - Spec is outdated and needs revision
        - Implementation has diverged from spec
        - Document superseded by newer version
        """
        from services.providers import get_sovereign_store, get_witness_persistence
        from services.sovereign.analysis import AnalysisState, AnalysisStatus

        store = await get_sovereign_store()
        witness = await get_witness_persistence()

        # Verify document exists
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Get current state
        state = await store.get_analysis_state(path)
        current_status = state.status.value if state else "unknown"

        # Update status to STALE
        new_state = AnalysisState(
            status=AnalysisStatus.STALE,
            started_at=None,
            completed_at=None,
            error=f"Deprecated: {request.reason}",
        )

        # Preserve existing analysis data if present
        if state:
            new_state.discovered_refs = state.discovered_refs
            new_state.placeholder_paths = state.placeholder_paths
            new_state.analysis_mark_id = state.analysis_mark_id

        await store.set_analysis_state(path, new_state)

        # Create deprecation witness mark
        mark = await witness.save_mark(
            action=f"Deprecated: {path}",
            reasoning=request.reason,
            tags=[
                "deprecation",
                f"spec:{path}",
                f"previous_status:{current_status}",
            ],
            author="director",
        )

        return DeprecateResponse(
            success=True,
            path=path,
            status="stale",
            mark_id=mark.mark_id,
            message=f"Document marked as deprecated: {request.reason}",
        )

    @router.delete("/documents/{path:path}", response_model=DeleteResponse)
    async def delete_document(path: str) -> DeleteResponse:
        """
        Delete a document permanently.

        Workflow:
        1. Verify document exists
        2. Create witness mark recording deletion
        3. Remove from sovereign store
        4. Clean up analysis state and overlays

        WARNING: This is destructive and cannot be undone.
        """
        from services.providers import get_sovereign_store, get_witness_persistence

        store = await get_sovereign_store()
        witness = await get_witness_persistence()

        # Verify document exists
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Delete from store using the full delete method
        # This will:
        # 1. Create witness mark BEFORE deletion
        # 2. Remove the entity and all versions
        # 3. Remove analysis state and overlays
        # 4. Handle any references (with safety checks)
        delete_result = await store.delete(
            path=path,
            check_references=False,  # Director allows deleting documents with references
            force=True,  # Force deletion
            witness=witness,
            author="director",
        )

        if not delete_result.success:
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {path}")

        return DeleteResponse(
            success=True,
            path=path,
            mark_id=delete_result.mark_id or "",
            message=f"Document deleted: {path}",
        )

    @router.put("/documents/{path:path}/rename", response_model=RenameResponse)
    async def rename_document(path: str, request: RenameRequest) -> RenameResponse:
        """
        Rename a document.

        Workflow:
        1. Verify source document exists
        2. Verify target path doesn't exist
        3. Copy entity to new path
        4. Copy analysis state and overlays
        5. Create witness mark
        6. Delete old path

        This maintains version history at the new path.
        """
        from services.providers import get_sovereign_store, get_witness_persistence

        store = await get_sovereign_store()
        witness = await get_witness_persistence()

        # Verify source exists
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Verify target doesn't exist
        target_exists = await store.get_current(request.new_path)
        if target_exists:
            raise HTTPException(
                status_code=409, detail=f"Target path already exists: {request.new_path}"
            )

        # Get analysis state and overlay
        state = await store.get_analysis_state(path)
        overlay = await store.get_overlay(path, "analysis")

        # Create witness mark
        mark = await witness.save_mark(
            action=f"Renamed: {path} → {request.new_path}",
            reasoning=f"Document renamed from {path} to {request.new_path}",
            tags=[
                "rename",
                f"old:{path}",
                f"new:{request.new_path}",
            ],
            author="director",
        )

        # TODO: Add proper rename method to SovereignStore
        # For now, we would:
        # 1. Store content at new path
        # 2. Copy analysis state
        # 3. Copy overlays
        # 4. Delete old path
        # await store.rename(path, request.new_path)

        # Placeholder implementation - store at new path
        from services.sovereign.ingest import Ingestor
        from services.sovereign.types import IngestEvent

        event = IngestEvent.from_content(
            content=entity.content,
            claimed_path=request.new_path,
            source="rename",
        )
        ingestor = Ingestor(store, witness=witness)
        await ingestor.ingest(event, author="director")

        # Copy analysis state if it exists
        if state:
            await store.set_analysis_state(request.new_path, state)

        # Copy overlay if it exists
        if overlay:
            await store.store_overlay(request.new_path, "analysis", overlay)

        return RenameResponse(
            success=True,
            old_path=path,
            new_path=request.new_path,
            mark_id=mark.mark_id,
            message=f"Document renamed: {path} → {request.new_path}",
        )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_director_router",
    "DocumentStatus",
    "SummaryResponse",
    "DeprecateRequest",
    "DeprecateResponse",
    "DeleteResponse",
    "RenameRequest",
    "RenameResponse",
]
