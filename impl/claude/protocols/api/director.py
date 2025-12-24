"""
Document Director REST API: Full lifecycle document management.

Provides:
- POST /api/director/upload         - Upload document, trigger analysis
- GET  /api/director/documents      - List documents with status
- GET  /api/director/:path          - Get document detail + analysis
- GET  /api/director/:path/preview  - Rendered preview (read-only)
- POST /api/director/:path/analyze  - Re-trigger analysis
- POST /api/director/:path/prompt   - Generate execution prompt
- POST /api/director/:path/capture  - Capture execution results
- GET  /api/director/:path/evidence - Get evidence for document
- POST /api/director/:path/evidence - Add evidence link

Philosophy:
    "Specs become code. Code becomes evidence. Evidence feeds back to specs."
    Upload → Analyze → Generate → Execute → Capture → Verify
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore

try:
    from pydantic import BaseModel, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore

logger = logging.getLogger(__name__)


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
    test_results: dict[str, Any] | None = Field(
        default=None, description="Test execution results"
    )
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


class ParseRequest(BaseModel):
    """Request to parse document content."""

    content: str = Field(..., description="Document content to parse")
    layout_mode: str = Field(default="COMFORTABLE", description="Layout mode: COMPACT, COMFORTABLE, SPACIOUS")


class ParseResponse(BaseModel):
    """Response from parsing document."""

    success: bool
    scene_graph: dict[str, Any]
    sections: list[dict[str, Any]]
    section_hashes: dict[int, str]
    token_count: int
    message: str = ""


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
        from protocols.agentese.projection.tokens_to_scene import (
            detect_sections,
            markdown_to_scene_graph,
        )
        from protocols.agentese.projection.scene import LayoutMode

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
        3. Set status to PENDING or PROCESSING
        4. Optionally queue for async analysis
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

        # Set initial status
        from services.sovereign.analysis import AnalysisState, AnalysisStatus

        status = AnalysisStatus.PENDING
        await store.set_analysis_state(
            request.path,
            AnalysisState(
                status=status,
                started_at=None,
            ),
        )

        # Queue for analysis if requested
        analysis_queued = False
        if request.auto_analyze:
            # TODO: When AnalysisQueue is implemented, enqueue here
            # For now, just set status
            analysis_queued = True

        return UploadResponse(
            path=result.path,
            version=result.version,
            status=status.value,
            ingest_mark_id=result.ingest_mark_id,
            analysis_queued=analysis_queued,
            message="Document uploaded successfully",
        )

    @router.get("/documents", response_model=DocumentListResponse)
    async def list_documents(
        status: str | None = Query(default=None, description="Filter by status"),
        prefix: str = Query(default="", description="Filter by path prefix"),
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

        # Filter by status
        if status:
            filtered = []
            for path in all_paths:
                state = await store.get_analysis_state(path)
                if state and state.status.value == status:
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

            doc_status = state.status.value if state else DocumentStatus.UPLOADED

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
        """
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()

        # Get entity
        entity = await store.get_current(path)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Document not found: {path}")

        # Get analysis state
        state = await store.get_analysis_state(path)
        doc_status = state.status.value if state else DocumentStatus.UPLOADED

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
        doc_status = state.status.value if state else DocumentStatus.UPLOADED

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
{len(context['claims'])} claims extracted

Existing implementations:
{chr(10).join(f"- {r}" for r in context.get('existing_refs', []))}

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

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_director_router",
    "DocumentStatus",
]
