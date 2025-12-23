"""
Spec Ledger REST API: Frontend endpoints for spec management.

Provides:
- POST /api/spec/scan     - Scan corpus
- GET  /api/spec/ledger   - Get ledger summary and specs
- GET  /api/spec/detail   - Get single spec detail
- GET  /api/spec/orphans  - List orphan specs
- GET  /api/spec/contradictions - List contradictions
- GET  /api/spec/harmonies - List harmonies
- POST /api/spec/deprecate - Deprecate specs

Philosophy:
    "Spec = Asset. Evidence = Transactions."
    "If proofs valid, supported. If not used, dead."
"""

from __future__ import annotations

import logging
from typing import Any, Optional

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class ScanRequest(BaseModel):
    """Request body for scanning."""

    force: bool = Field(default=False, description="Force rescan even if cache is fresh")


class ScanResponse(BaseModel):
    """Response from scan."""

    success: bool
    message: str
    summary: dict[str, Any]


class LedgerSummary(BaseModel):
    """Summary statistics."""

    total_specs: int
    active: int
    orphans: int
    deprecated: int
    archived: int
    total_claims: int
    contradictions: int
    harmonies: int


class SpecEntry(BaseModel):
    """Single spec in ledger."""

    path: str
    title: str
    status: str
    claim_count: int
    impl_count: int
    test_count: int
    ref_count: int
    word_count: int


class LedgerResponse(BaseModel):
    """Full ledger response."""

    success: bool
    total: int
    offset: int
    limit: int
    summary: LedgerSummary
    specs: list[SpecEntry]
    orphan_paths: list[str]
    deprecated_paths: list[str]


class ClaimDetail(BaseModel):
    """Single claim."""

    type: str
    subject: str
    predicate: str
    line: int


class HarmonyDetail(BaseModel):
    """Single harmony."""

    spec: str
    relationship: str
    strength: float


class ContradictionDetail(BaseModel):
    """Single contradiction."""

    spec: str
    conflict_type: str
    severity: str


class SpecDetailResponse(BaseModel):
    """Detailed spec view."""

    success: bool
    path: str
    title: str
    status: str
    claims: list[ClaimDetail]
    implementations: list[str]
    tests: list[str]
    references: list[str]
    harmonies: list[HarmonyDetail]
    contradictions: list[ContradictionDetail]
    word_count: int
    heading_count: int


class OrphanEntry(BaseModel):
    """Single orphan."""

    path: str
    title: str
    claim_count: int
    word_count: int


class OrphansResponse(BaseModel):
    """Orphans list response."""

    success: bool
    total: int
    orphans: list[OrphanEntry]


class ContradictionEntry(BaseModel):
    """Single contradiction entry."""

    spec_a: str
    spec_b: str
    conflict_type: str
    severity: str
    claim_a: dict[str, Any]
    claim_b: dict[str, Any]


class ContradictionsResponse(BaseModel):
    """Contradictions list response."""

    success: bool
    total: int
    contradictions: list[ContradictionEntry]


class HarmonyEntry(BaseModel):
    """Single harmony entry."""

    spec_a: str
    spec_b: str
    relationship: str
    strength: float


class HarmoniesResponse(BaseModel):
    """Harmonies list response."""

    success: bool
    total: int
    harmonies: list[HarmonyEntry]


class EvidenceAddRequest(BaseModel):
    """Request to add evidence to a spec."""

    spec_path: str = Field(..., description="Spec path to link evidence to")
    evidence_path: str = Field(..., description="Path to implementation/test file")
    evidence_type: str = Field(
        default="implementation", description="Type: implementation, test, or usage"
    )


class EvidenceAddResponse(BaseModel):
    """Response from adding evidence."""

    success: bool
    message: str
    spec_path: str
    evidence_path: str
    evidence_type: str
    evidence_exists: bool
    was_orphan: bool
    is_first_evidence: bool
    timestamp: str
    mark_id: str | None = None
    note: str | None = None


class EvidenceMark(BaseModel):
    """Single evidence mark from witness system."""

    mark_id: str
    action: str
    reasoning: str | None
    author: str
    timestamp: str | None
    tags: list[str]


class EvidenceByType(BaseModel):
    """Evidence grouped by type."""

    impl: list[EvidenceMark]
    test: list[EvidenceMark]
    usage: list[EvidenceMark]


class EvidenceQueryResponse(BaseModel):
    """Response from evidence query."""

    success: bool
    spec_path: str
    total_evidence: int
    by_type: EvidenceByType
    marks: list[EvidenceMark]


class EvidenceVerifyResult(BaseModel):
    """Single evidence verification result."""

    mark_id: str
    file_path: str
    evidence_type: str | None
    status: str
    exists: bool


class EvidenceVerifyResponse(BaseModel):
    """Response from evidence verification."""

    success: bool
    spec_path: str
    total: int
    valid: int
    stale: int
    broken: int
    results: list[EvidenceVerifyResult]


class EvidenceSummaryResponse(BaseModel):
    """Response from evidence summary."""

    success: bool
    total_specs_with_evidence: int
    total_impl: int
    total_test: int
    total_usage: int
    by_spec: dict[str, dict[str, int]]


class DeprecateRequest(BaseModel):
    """Request to deprecate specs."""

    paths: list[str] = Field(..., description="Spec paths to deprecate")
    reason: str = Field(..., description="Reason for deprecation")


class DeprecateResponse(BaseModel):
    """Response from deprecation."""

    success: bool
    message: str
    paths: list[str]
    reason: str
    note: str | None = None


# =============================================================================
# Router Factory
# =============================================================================


class DataNotComputedResponse(BaseModel):
    """Response when proxy handle data hasn't been computed yet (AD-015)."""

    success: bool = False
    needs_scan: bool = True
    message: str = "Spec analysis not available. Click 'Scan' to generate proxy handles."
    hint: str = "AD-015: Analysis is explicit. Run scan to compute."


def create_spec_ledger_router() -> Optional["APIRouter"]:
    """
    Create FastAPI router for spec ledger endpoints.

    Returns:
        APIRouter or None if FastAPI not installed
    """
    if not HAS_FASTAPI:
        logger.warning("FastAPI not installed, spec ledger router not available")
        return None

    router = APIRouter(prefix="/api/spec", tags=["spec-ledger"])

    # Import ledger node
    try:
        from services.living_spec.ledger_node import (
            NoProxyHandleError,  # AD-015: Unified exception from proxy service
            get_ledger_node,
        )
    except ImportError as e:
        logger.error(f"Could not import ledger node: {e}")
        return None

    @router.post("/scan", response_model=ScanResponse)
    async def scan_corpus(request: ScanRequest) -> ScanResponse:
        """
        Scan spec corpus and populate ledger.

        Extracts claims, finds evidence, identifies relationships.
        """
        node = get_ledger_node()
        result = await node.scan(force=request.force)

        return ScanResponse(
            success=result["success"],
            message=result["message"],
            summary=result["summary"],
        )

    @router.get("/ledger", response_model=LedgerResponse | DataNotComputedResponse)
    async def get_ledger(
        status: Optional[str] = Query(None, description="Filter by status"),
        sort_by: str = Query("path", description="Sort field"),
        limit: int = Query(100, ge=1, le=500, description="Max results"),
        offset: int = Query(0, ge=0, description="Pagination offset"),
    ) -> LedgerResponse | DataNotComputedResponse:
        """
        Get ledger summary and spec list.

        Returns summary statistics and paginated spec list.
        AD-015: Returns needs_scan=true if no proxy handle data exists.
        """
        node = get_ledger_node()
        try:
            result = await node.ledger(
                status_filter=status,
                sort_by=sort_by,
                limit=limit,
                offset=offset,
            )
        except NoProxyHandleError:
            # AD-015: Data not computed yet, return helpful response
            return DataNotComputedResponse()

        return LedgerResponse(
            success=result["success"],
            total=result["total"],
            offset=result["offset"],
            limit=result["limit"],
            summary=LedgerSummary(**result["summary"]),
            specs=[SpecEntry(**s) for s in result["specs"]],
            orphan_paths=result["orphan_paths"],
            deprecated_paths=result["deprecated_paths"],
        )

    @router.get("/detail", response_model=SpecDetailResponse)
    async def get_spec_detail(
        path: str = Query(..., description="Spec path"),
    ) -> SpecDetailResponse:
        """
        Get detailed view of single spec.

        Includes claims, evidence, and relationships.
        """
        node = get_ledger_node()
        result = await node.get(path)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Spec not found"))

        return SpecDetailResponse(
            success=True,
            path=result["path"],
            title=result["title"],
            status=result["status"],
            claims=[ClaimDetail(**c) for c in result["claims"]],
            implementations=result["implementations"],
            tests=result["tests"],
            references=result["references"],
            harmonies=[HarmonyDetail(**h) for h in result["harmonies"]],
            contradictions=[ContradictionDetail(**c) for c in result["contradictions"]],
            word_count=result["word_count"],
            heading_count=result["heading_count"],
        )

    @router.get("/orphans", response_model=OrphansResponse)
    async def get_orphans(
        limit: int = Query(100, ge=1, le=500, description="Max results"),
    ) -> OrphansResponse:
        """
        List specs without evidence.

        Returns specs that have no implementations, tests, or references.
        """
        node = get_ledger_node()
        result = await node.orphans(limit=limit)

        return OrphansResponse(
            success=result["success"],
            total=result["total"],
            orphans=[OrphanEntry(**o) for o in result["orphans"]],
        )

    @router.get("/contradictions", response_model=ContradictionsResponse)
    async def get_contradictions() -> ContradictionsResponse:
        """
        List conflicting specs.

        Returns pairs of specs with conflicting claims.
        """
        node = get_ledger_node()
        result = await node.contradictions()

        return ContradictionsResponse(
            success=result["success"],
            total=result["total"],
            contradictions=[ContradictionEntry(**c) for c in result["contradictions"]],
        )

    @router.get("/harmonies", response_model=HarmoniesResponse | DataNotComputedResponse)
    async def get_harmonies(
        limit: int = Query(50, ge=1, le=200, description="Max results"),
    ) -> HarmoniesResponse | DataNotComputedResponse:
        """
        List reinforcing relationships.

        Returns specs that reference or extend each other.
        AD-015: Returns needs_scan=true if no proxy handle data exists.
        """
        node = get_ledger_node()
        try:
            result = await node.harmonies(limit=limit)
        except NoProxyHandleError:
            # AD-015: Data not computed yet, return helpful response
            return DataNotComputedResponse()

        return HarmoniesResponse(
            success=result["success"],
            total=result["total"],
            harmonies=[HarmonyEntry(**h) for h in result["harmonies"]],
        )

    @router.post("/evidence/add", response_model=EvidenceAddResponse)
    async def add_evidence(request: EvidenceAddRequest) -> EvidenceAddResponse:
        """
        Link evidence (implementation/test) to a spec.

        This is an accounting transaction — creates a witness mark with evidence tags.
        """
        node = get_ledger_node()
        result = await node.evidence_add(
            spec_path=request.spec_path,
            evidence_path=request.evidence_path,
            evidence_type=request.evidence_type,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400, detail=result.get("error", "Failed to add evidence")
            )

        return EvidenceAddResponse(
            success=result["success"],
            message=result["message"],
            spec_path=result["spec_path"],
            evidence_path=result["evidence_path"],
            evidence_type=result["evidence_type"],
            evidence_exists=result["evidence_exists"],
            was_orphan=result["was_orphan"],
            is_first_evidence=result["is_first_evidence"],
            timestamp=result["timestamp"],
            mark_id=result.get("mark_id"),
            note=result.get("note"),
        )

    @router.get("/evidence/query", response_model=EvidenceQueryResponse)
    async def query_evidence(
        path: str = Query(..., description="Spec path to query evidence for"),
        evidence_type: Optional[str] = Query(None, description="Filter by type: impl, test, usage"),
        limit: int = Query(50, ge=1, le=200, description="Max results"),
    ) -> EvidenceQueryResponse:
        """
        Query evidence for a spec from the witness mark system.

        Returns declared evidence (explicit links) from witness marks.
        """
        node = get_ledger_node()
        result = await node.evidence_query(
            spec_path=path,
            evidence_type=evidence_type,
            limit=limit,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400, detail=result.get("error", "Failed to query evidence")
            )

        return EvidenceQueryResponse(
            success=result["success"],
            spec_path=result["spec_path"],
            total_evidence=result["total_evidence"],
            by_type=EvidenceByType(
                impl=[EvidenceMark(**m) for m in result["by_type"]["impl"]],
                test=[EvidenceMark(**m) for m in result["by_type"]["test"]],
                usage=[EvidenceMark(**m) for m in result["by_type"]["usage"]],
            ),
            marks=[EvidenceMark(**m) for m in result["marks"]],
        )

    @router.post("/evidence/verify", response_model=EvidenceVerifyResponse)
    async def verify_evidence(
        path: str = Query(..., description="Spec path to verify evidence for"),
    ) -> EvidenceVerifyResponse:
        """
        Verify all evidence for a spec is still valid.

        Checks if evidence files still exist on disk.
        """
        node = get_ledger_node()
        result = await node.evidence_verify(spec_path=path)

        if not result["success"]:
            raise HTTPException(
                status_code=400, detail=result.get("error", "Failed to verify evidence")
            )

        return EvidenceVerifyResponse(
            success=result["success"],
            spec_path=result["spec_path"],
            total=result["total"],
            valid=result["valid"],
            stale=result["stale"],
            broken=result["broken"],
            results=[EvidenceVerifyResult(**r) for r in result["results"]],
        )

    @router.get("/evidence/summary", response_model=EvidenceSummaryResponse)
    async def get_evidence_summary() -> EvidenceSummaryResponse:
        """
        Get summary of evidence across all specs.

        Returns counts by spec and evidence type.
        """
        node = get_ledger_node()
        result = await node.evidence_summary()

        if not result["success"]:
            raise HTTPException(
                status_code=400, detail=result.get("error", "Failed to get evidence summary")
            )

        return EvidenceSummaryResponse(
            success=result["success"],
            total_specs_with_evidence=result["total_specs_with_evidence"],
            total_impl=result["total_impl"],
            total_test=result["total_test"],
            total_usage=result["total_usage"],
            by_spec=result["by_spec"],
        )

    @router.post("/deprecate", response_model=DeprecateResponse)
    async def deprecate_specs(request: DeprecateRequest) -> DeprecateResponse:
        """
        Mark specs as deprecated.

        Adds deprecation notice to spec files.
        """
        node = get_ledger_node()
        result = await node.deprecate(paths=request.paths, reason=request.reason)

        return DeprecateResponse(
            success=result["success"],
            message=result["message"],
            paths=result["paths"],
            reason=result["reason"],
            note=result.get("note"),
        )

    return router
