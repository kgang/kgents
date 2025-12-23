"""
Living Spec Ledger AGENTESE Node: self.spec.ledger.*

Accounting-style interface for spec corpus management.

Aspects:
- self.spec.scan          - Scan corpus, extract claims, find evidence
- self.spec.ledger        - Get ledger summary (assets/liabilities)
- self.spec.get           - Get single spec detail
- self.spec.orphans       - List specs without evidence
- self.spec.contradictions - List conflicting specs
- self.spec.harmonies     - List reinforcing relationships
- self.spec.deprecate     - Mark specs as deprecated

Philosophy:
    "Spec = Asset. Evidence = Transactions. Contradictions = Liabilities."
    "If proofs valid, supported. If not used, dead."
    "The proof IS the decision. The mark IS the witness."

Integration:
    Every ledger mutation emits to WitnessBus.
    Connects Living Spec to Witness crown jewel.

AD-015 Migration (2025-12-23):
    Radical Unification: LedgerCache DELETED.
    All caching now via ProxyHandleStore singleton.
    Reactive invalidation via ProxyReactor.
    One truth. One store.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any

from services.proxy.exceptions import NoProxyHandleError
from services.proxy.store import get_proxy_handle_store
from services.proxy.types import SourceType

from .analyzer import (
    Contradiction,
    Harmony,
    LedgerReport,
    SpecRecord,
    SpecStatus,
    analyze_spec_corpus,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Default TTL for spec corpus analysis (5 minutes)
SPEC_CORPUS_TTL = timedelta(minutes=5)


# =============================================================================
# Witness Bus Integration
# =============================================================================


def _get_witness_bus() -> tuple[Any, Any]:
    """
    Get the witness synergy bus (optional dependency).

    Returns (None, None) if witness bus not available.
    This allows LedgerNode to work standalone for testing.
    """
    try:
        from services.witness.bus import WitnessTopics, get_synergy_bus

        return get_synergy_bus(), WitnessTopics
    except ImportError:
        logger.debug("Witness bus not available")
        return None, None


async def _emit_witness_event(topic: str, event: dict[str, Any]) -> None:
    """
    Emit an event to the witness bus.

    Silently no-ops if witness bus not available.
    """
    bus, _ = _get_witness_bus()
    if bus is not None:
        await bus.publish(topic, event)
        logger.debug(f"Emitted witness event: {topic}")


async def _get_witness_persistence() -> Any | None:
    """
    Get the WitnessPersistence instance.

    Returns None if witness persistence not available.
    This enables graceful degradation when running without full witness stack.
    """
    try:
        from services.providers import get_witness_persistence

        return await get_witness_persistence()
    except ImportError as e:
        logger.debug(f"Witness persistence not available: {e}")
        return None
    except Exception as e:
        logger.warning(f"Could not create witness persistence: {e}")
        return None


def get_spec_root() -> Path:
    """Get the spec root directory."""
    # Navigate up from this file to find spec/
    current = Path(__file__).resolve()
    for parent in current.parents:
        spec_dir = parent / "spec"
        if spec_dir.exists() and spec_dir.is_dir():
            return spec_dir
    raise FileNotFoundError("Could not find spec/ directory")


async def ensure_scanned() -> LedgerReport:
    """
    Get the pre-computed ledger report from ProxyHandleStore.

    AD-015 Radical Unification: All caching via ProxyHandleStore.
    No auto-compute. Fail fast if no handle exists.

    Raises:
        NoProxyHandleError: If no pre-computed data exists

    Returns:
        The LedgerReport from the proxy handle
    """
    store = get_proxy_handle_store()
    handle = await store.get_or_raise(SourceType.SPEC_CORPUS)

    # Handle data is the LedgerReport
    if handle.data is None:
        raise NoProxyHandleError(
            SourceType.SPEC_CORPUS,
            "Proxy handle exists but has no data. Use analyze_now() to compute.",
        )

    # Type cast since ProxyHandle is generic over Any
    report: LedgerReport = handle.data
    return report


async def analyze_now(force: bool = False) -> LedgerReport:
    """
    Explicitly analyze the spec corpus NOW via ProxyHandleStore.

    AD-015 Radical Unification: Computation is ALWAYS explicit.
    This method delegates to ProxyHandleStore.compute() which:
    - Checks for fresh handle (returns it unless force=True)
    - Coordinates concurrent computations (idempotent)
    - Emits events for transparency
    - Enables reactive invalidation

    Args:
        force: Force re-analysis even if cache is fresh

    Returns:
        The analyzed LedgerReport
    """
    store = get_proxy_handle_store()

    async def compute_fn() -> LedgerReport:
        """Compute spec corpus analysis in thread pool."""
        spec_root = get_spec_root()
        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(None, analyze_spec_corpus, spec_root)
        logger.info(f"Spec corpus analyzed: {len(report.specs)} specs")
        return report

    handle = await store.compute(
        source_type=SourceType.SPEC_CORPUS,
        compute_fn=compute_fn,
        force=force,
        ttl=SPEC_CORPUS_TTL,
        human_label="Spec corpus ledger analysis",
        computed_by="ledger_node.analyze_now",
    )

    return handle.data  # type: ignore


# =============================================================================
# Response Types
# =============================================================================


@dataclass
class LedgerSummary:
    """Summary of spec corpus health."""

    total_specs: int
    active: int
    orphans: int
    deprecated: int
    archived: int
    total_claims: int
    contradictions: int
    harmonies: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_specs": self.total_specs,
            "active": self.active,
            "orphans": self.orphans,
            "deprecated": self.deprecated,
            "archived": self.archived,
            "total_claims": self.total_claims,
            "contradictions": self.contradictions,
            "harmonies": self.harmonies,
        }


@dataclass
class SpecEntry:
    """Single spec in ledger table."""

    path: str
    title: str
    status: str
    claim_count: int
    impl_count: int
    test_count: int
    ref_count: int
    word_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "title": self.title,
            "status": self.status,
            "claim_count": self.claim_count,
            "impl_count": self.impl_count,
            "test_count": self.test_count,
            "ref_count": self.ref_count,
            "word_count": self.word_count,
        }


@dataclass
class LedgerResponse:
    """Full ledger response for API."""

    summary: LedgerSummary
    specs: list[SpecEntry]
    orphan_paths: list[str]
    deprecated_paths: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "specs": [s.to_dict() for s in self.specs],
            "orphan_paths": self.orphan_paths,
            "deprecated_paths": self.deprecated_paths,
        }


@dataclass
class SpecDetail:
    """Detailed view of single spec."""

    path: str
    title: str
    status: str
    claims: list[dict[str, Any]]
    implementations: list[str]
    tests: list[str]
    references: list[str]
    harmonies: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    word_count: int
    heading_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "title": self.title,
            "status": self.status,
            "claims": self.claims,
            "implementations": self.implementations,
            "tests": self.tests,
            "references": self.references,
            "harmonies": self.harmonies,
            "contradictions": self.contradictions,
            "word_count": self.word_count,
            "heading_count": self.heading_count,
        }


# =============================================================================
# AGENTESE Node
# =============================================================================


@dataclass
class LedgerNode:
    """
    AGENTESE node for spec ledger operations.

    Symmetric harness: agents can do everything Kent can do.
    """

    handle: str = "self.spec"

    async def scan(self, force: bool = False) -> dict[str, Any]:
        """
        Scan spec corpus and populate ledger.

        AD-015: This is an EXPLICIT analysis request. Unlike the old
        ensure_scanned(), this WILL compute analysis when called.

        Args:
            force: Force rescan even if cache is fresh

        Returns:
            Summary of scan results

        Emits:
            witness.spec.scanned — Summary of scan results
        """
        # AD-015: Use analyze_now() for explicit analysis
        report = await analyze_now(force=force)
        summary = report.summary()

        # Emit witness event
        _, topics = _get_witness_bus()
        if topics:
            await _emit_witness_event(
                topics.SPEC_SCANNED,
                {
                    "action": "scan",
                    "force": force,
                    "summary": summary,
                    "orphan_count": len(report.orphans),
                    "contradiction_count": len(report.contradictions),
                },
            )

        return {
            "success": True,
            "message": f"Scanned {summary['total_specs']} specs",
            "summary": summary,
        }

    async def ledger(
        self,
        status_filter: str | None = None,
        sort_by: str = "path",
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Get ledger summary and spec list.

        Args:
            status_filter: Filter by status (active, orphan, deprecated)
            sort_by: Sort field (path, claims, impl, status)
            limit: Max specs to return
            offset: Pagination offset

        Returns:
            LedgerResponse with summary and specs
        """
        report = await ensure_scanned()

        # Build summary
        summary_data = report.summary()
        summary = LedgerSummary(
            total_specs=summary_data["total_specs"],
            active=summary_data["active"],
            orphans=summary_data["orphans"],
            deprecated=summary_data["deprecated"],
            archived=summary_data["archived"],
            total_claims=summary_data["total_claims"],
            contradictions=summary_data["contradictions"],
            harmonies=summary_data["harmonies"],
        )

        # Convert specs to entries
        specs = report.specs

        # Filter by status
        if status_filter:
            status_upper = status_filter.upper()
            if status_upper == "ORPHAN":
                orphan_set = set(report.orphans)
                specs = [s for s in specs if s.path in orphan_set]
            elif status_upper == "DEPRECATED":
                specs = [s for s in specs if s.status == SpecStatus.DEPRECATED]
            elif status_upper == "ACTIVE":
                orphan_set = set(report.orphans)
                specs = [
                    s for s in specs if s.status == SpecStatus.ACTIVE and s.path not in orphan_set
                ]
            elif status_upper == "ARCHIVED":
                specs = [s for s in specs if s.status == SpecStatus.ARCHIVED]

        # Sort
        if sort_by == "claims":
            specs = sorted(specs, key=lambda s: len(s.claims), reverse=True)
        elif sort_by == "impl":
            specs = sorted(specs, key=lambda s: len(s.implementations), reverse=True)
        elif sort_by == "status":
            specs = sorted(specs, key=lambda s: s.status.name)
        else:  # path
            specs = sorted(specs, key=lambda s: s.path)

        # Paginate
        total = len(specs)
        specs = specs[offset : offset + limit]

        # Convert to entries
        orphan_set = set(report.orphans)
        entries = [
            SpecEntry(
                path=s.path,
                title=s.title,
                status="ORPHAN" if s.path in orphan_set else s.status.name,
                claim_count=len(s.claims),
                impl_count=len(s.implementations),
                test_count=len(s.tests),
                ref_count=len(s.references),
                word_count=s.word_count,
            )
            for s in specs
        ]

        response = LedgerResponse(
            summary=summary,
            specs=entries,
            orphan_paths=report.orphans[:50],  # Limit for response size
            deprecated_paths=report.deprecated[:50],
        )

        return {
            "success": True,
            "total": total,
            "offset": offset,
            "limit": limit,
            **response.to_dict(),
        }

    async def get(self, path: str) -> dict[str, Any]:
        """
        Get detailed view of single spec.

        Args:
            path: Spec path (relative to spec/)

        Returns:
            SpecDetail with claims, evidence, relationships
        """
        report = await ensure_scanned()

        # Find the spec
        spec = None
        for s in report.specs:
            if path in s.path or s.path.endswith(path):
                spec = s
                break

        if not spec:
            return {
                "success": False,
                "error": f"Spec not found: {path}",
            }

        # Find harmonies involving this spec
        harmonies = [
            {
                "spec": h.spec_b if h.spec_a == spec.path else h.spec_a,
                "relationship": h.relationship,
                "strength": h.strength,
            }
            for h in report.harmonies
            if h.spec_a == spec.path or h.spec_b == spec.path
        ]

        # Find contradictions involving this spec
        contradictions = [
            {
                "spec": c.spec_b if c.spec_a == spec.path else c.spec_a,
                "conflict_type": c.conflict_type,
                "severity": c.severity,
            }
            for c in report.contradictions
            if c.spec_a == spec.path or c.spec_b == spec.path
        ]

        # Determine status
        orphan_set = set(report.orphans)
        status = "ORPHAN" if spec.path in orphan_set else spec.status.name

        detail = SpecDetail(
            path=spec.path,
            title=spec.title,
            status=status,
            claims=[
                {
                    "type": c.claim_type.name,
                    "subject": c.subject,
                    "predicate": c.predicate,
                    "line": c.line_number,
                }
                for c in spec.claims
            ],
            implementations=spec.implementations,
            tests=spec.tests,
            references=spec.references,
            harmonies=harmonies[:20],
            contradictions=contradictions,
            word_count=spec.word_count,
            heading_count=spec.heading_count,
        )

        return {
            "success": True,
            **detail.to_dict(),
        }

    async def orphans(self, limit: int = 100) -> dict[str, Any]:
        """
        List specs without evidence.

        Returns:
            List of orphan spec paths with details
        """
        report = await ensure_scanned()

        orphan_details = []
        orphan_set = set(report.orphans)

        for spec in report.specs:
            if spec.path in orphan_set:
                orphan_details.append(
                    {
                        "path": spec.path,
                        "title": spec.title,
                        "claim_count": len(spec.claims),
                        "word_count": spec.word_count,
                    }
                )

        # Sort by word count (bigger specs = more important to triage)
        def get_word_count(x: dict[str, Any]) -> int:
            val = x.get("word_count", 0)
            return int(val) if isinstance(val, (int, float, str)) else 0

        orphan_details = sorted(orphan_details, key=get_word_count, reverse=True)

        return {
            "success": True,
            "total": len(orphan_details),
            "orphans": orphan_details[:limit],
        }

    async def contradictions(self) -> dict[str, Any]:
        """
        List conflicting specs.

        Returns:
            List of contradictions with details
        """
        report = await ensure_scanned()

        return {
            "success": True,
            "total": len(report.contradictions),
            "contradictions": [
                {
                    "spec_a": c.spec_a,
                    "spec_b": c.spec_b,
                    "conflict_type": c.conflict_type,
                    "severity": c.severity,
                    "claim_a": {
                        "type": c.claim_a.claim_type.name,
                        "text": c.claim_a.raw_text[:200],
                    },
                    "claim_b": {
                        "type": c.claim_b.claim_type.name,
                        "text": c.claim_b.raw_text[:200],
                    },
                }
                for c in report.contradictions[:50]
            ],
        }

    async def harmonies(self, limit: int = 50) -> dict[str, Any]:
        """
        List reinforcing relationships.

        Returns:
            List of harmonies
        """
        report = await ensure_scanned()

        # Sort by strength
        sorted_harmonies = sorted(report.harmonies, key=lambda h: h.strength, reverse=True)

        return {
            "success": True,
            "total": len(report.harmonies),
            "harmonies": [
                {
                    "spec_a": h.spec_a,
                    "spec_b": h.spec_b,
                    "relationship": h.relationship,
                    "strength": h.strength,
                }
                for h in sorted_harmonies[:limit]
            ],
        }

    async def evidence_add(
        self,
        spec_path: str,
        evidence_path: str,
        evidence_type: str = "implementation",
        author: str = "system",
        reasoning: str | None = None,
    ) -> dict[str, Any]:
        """
        Link evidence (implementation/test) to a spec.

        This is a TRANSACTION in the accounting sense:
        - Creates a DECLARATION MARK in the witness system
        - Emits SPEC_EVIDENCE_ADDED witness event
        - May transition spec from ORPHAN → ACTIVE if first evidence

        Unified Evidence-as-Marks:
            Evidence is stored as witness marks with specific tags:
            - spec:{path} — Links mark to a spec
            - evidence:{type} — Type of evidence (impl, test, usage)
            - file:{path} — The evidence file path

        Args:
            spec_path: Path to spec file (relative to spec/)
            evidence_path: Path to implementation/test file
            evidence_type: One of "implementation", "test", "usage"
            author: Who is declaring this evidence (default: "system")
            reasoning: Optional reasoning for why this is evidence

        Returns:
            Result of evidence linking (includes mark_id)

        Emits:
            witness.spec.evidence_added — Evidence transaction record
        """
        import time
        from pathlib import Path as P

        # Validate evidence type
        valid_types = {"implementation", "test", "usage"}
        if evidence_type not in valid_types:
            return {
                "success": False,
                "error": f"Invalid evidence_type: {evidence_type}. Must be one of {valid_types}",
            }

        # Map to short form for tags
        type_short = {"implementation": "impl", "test": "test", "usage": "usage"}[evidence_type]

        # Ensure we have scanned data
        report = await ensure_scanned()

        # Find the spec
        spec = None
        for s in report.specs:
            if spec_path in s.path or s.path.endswith(spec_path):
                spec = s
                break

        if not spec:
            return {
                "success": False,
                "error": f"Spec not found: {spec_path}",
            }

        # Check if evidence file exists (best effort)
        evidence_exists = P(evidence_path).exists()
        if not evidence_exists:
            # Try relative to impl/claude
            impl_root = P(__file__).resolve().parents[2]
            alt_path = impl_root / evidence_path.replace("impl/claude/", "")
            evidence_exists = alt_path.exists()

        # Determine if this is first evidence (orphan → active transition)
        orphan_set = set(report.orphans)
        was_orphan = spec.path in orphan_set
        is_first_evidence = was_orphan and (len(spec.implementations) == 0 and len(spec.tests) == 0)

        # Record the transaction timestamp
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Normalize spec path for tag
        spec_tag_path = spec.path.replace("spec/", "")

        # Create the declaration mark via witness persistence
        mark_id: str | None = None
        try:
            persistence = await _get_witness_persistence()
            if persistence:
                # Build evidence tags
                tags = [
                    f"spec:{spec_tag_path}",
                    f"evidence:{type_short}",
                    f"file:{evidence_path}",
                ]
                if is_first_evidence:
                    tags.append("first-evidence")

                # Create the mark
                mark_result = await persistence.save_mark(
                    action=f"Declared {evidence_type} evidence: {evidence_path} → {spec.path}",
                    reasoning=reasoning
                    or f"Links {evidence_path} as {evidence_type} for {spec.path}",
                    principles=["composable", "generative"],  # Evidence supports spec
                    tags=tags,
                    author=author,
                )
                mark_id = mark_result.mark_id
                logger.info(f"Evidence mark created: {mark_id}")
        except Exception as e:
            logger.warning(f"Could not create evidence mark: {e}")

        # Emit witness event (for cross-jewel awareness)
        _, topics = _get_witness_bus()
        if topics:
            await _emit_witness_event(
                topics.SPEC_EVIDENCE_ADDED,
                {
                    "action": "evidence_add",
                    "spec_path": spec.path,
                    "evidence_path": evidence_path,
                    "evidence_type": evidence_type,
                    "evidence_exists": evidence_exists,
                    "was_orphan": was_orphan,
                    "is_first_evidence": is_first_evidence,
                    "timestamp": timestamp,
                    "mark_id": mark_id,
                },
            )

        logger.info(f"Evidence linked: {evidence_path} → {spec.path} ({evidence_type})")

        return {
            "success": True,
            "message": f"Evidence linked to {spec.path}",
            "spec_path": spec.path,
            "evidence_path": evidence_path,
            "evidence_type": evidence_type,
            "evidence_exists": evidence_exists,
            "was_orphan": was_orphan,
            "is_first_evidence": is_first_evidence,
            "timestamp": timestamp,
            "mark_id": mark_id,
        }

    async def evidence_query(
        self,
        spec_path: str,
        evidence_type: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Query evidence for a spec from the witness mark system.

        Returns both declared evidence (explicit links) and emergent evidence
        (activity marks) for the spec.

        Args:
            spec_path: Path to spec file
            evidence_type: Filter by type ("impl", "test", "usage", or None for all)
            limit: Maximum evidence marks to return

        Returns:
            Evidence summary with marks
        """
        try:
            persistence = await _get_witness_persistence()
            if not persistence:
                return {
                    "success": False,
                    "error": "Witness persistence not available",
                }

            evidence = await persistence.get_evidence_for_spec(
                spec_path=spec_path,
                evidence_type=evidence_type,
                limit=limit,
            )

            # Group by evidence type
            by_type: dict[str, list[dict[str, Any]]] = {
                "impl": [],
                "test": [],
                "usage": [],
            }

            for mark in evidence:
                for tag in mark.tags:
                    if tag.startswith("evidence:"):
                        etype = tag[9:]
                        if etype in by_type:
                            by_type[etype].append(
                                {
                                    "mark_id": mark.mark_id,
                                    "action": mark.action,
                                    "reasoning": mark.reasoning,
                                    "author": mark.author,
                                    "timestamp": mark.timestamp.isoformat()
                                    if mark.timestamp
                                    else None,
                                    "tags": mark.tags,
                                }
                            )
                        break

            return {
                "success": True,
                "spec_path": spec_path,
                "total_evidence": len(evidence),
                "by_type": by_type,
                "marks": [
                    {
                        "mark_id": m.mark_id,
                        "action": m.action,
                        "author": m.author,
                        "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                        "tags": m.tags,
                    }
                    for m in evidence
                ],
            }

        except Exception as e:
            logger.error(f"Error querying evidence: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def evidence_verify(self, spec_path: str) -> dict[str, Any]:
        """
        Verify all evidence for a spec is still valid.

        Checks:
        - Files referenced in evidence marks still exist
        - Tests still pass (future: run tests)

        Args:
            spec_path: Path to spec file

        Returns:
            Verification result with status for each evidence item
        """
        from pathlib import Path as P

        try:
            persistence = await _get_witness_persistence()
            if not persistence:
                return {
                    "success": False,
                    "error": "Witness persistence not available",
                }

            evidence = await persistence.get_evidence_for_spec(spec_path)

            # Verify each evidence file exists
            verification_results = []
            valid_count = 0
            stale_count = 0
            broken_count = 0

            impl_root = P(__file__).resolve().parents[2]

            for mark in evidence:
                # Extract file path from tags
                file_path = None
                evidence_type = None
                for tag in mark.tags:
                    if tag.startswith("file:"):
                        file_path = tag[5:]
                    elif tag.startswith("evidence:"):
                        evidence_type = tag[9:]

                if not file_path:
                    continue

                # Check if file exists
                exists = P(file_path).exists()
                if not exists:
                    alt_path = impl_root / file_path.replace("impl/claude/", "")
                    exists = alt_path.exists()

                status = "valid" if exists else "broken"
                if status == "valid":
                    valid_count += 1
                else:
                    broken_count += 1

                verification_results.append(
                    {
                        "mark_id": mark.mark_id,
                        "file_path": file_path,
                        "evidence_type": evidence_type,
                        "status": status,
                        "exists": exists,
                    }
                )

            return {
                "success": True,
                "spec_path": spec_path,
                "total": len(verification_results),
                "valid": valid_count,
                "stale": stale_count,
                "broken": broken_count,
                "results": verification_results,
            }

        except Exception as e:
            logger.error(f"Error verifying evidence: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def evidence_summary(self) -> dict[str, Any]:
        """
        Get a summary of evidence across all specs.

        Returns counts of evidence by spec and type.
        """
        try:
            persistence = await _get_witness_persistence()
            if not persistence:
                return {
                    "success": False,
                    "error": "Witness persistence not available",
                }

            counts = await persistence.count_evidence_by_spec()

            # Calculate totals
            total_specs = len(counts)
            total_impl = sum(c["impl"] for c in counts.values())
            total_test = sum(c["test"] for c in counts.values())
            total_usage = sum(c["usage"] for c in counts.values())

            return {
                "success": True,
                "total_specs_with_evidence": total_specs,
                "total_impl": total_impl,
                "total_test": total_test,
                "total_usage": total_usage,
                "by_spec": counts,
            }

        except Exception as e:
            logger.error(f"Error getting evidence summary: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    async def deprecate(self, paths: list[str], reason: str) -> dict[str, Any]:
        """
        Mark specs as deprecated.

        Modifies spec files to add deprecation notice at top.

        Args:
            paths: List of spec paths to deprecate
            reason: Reason for deprecation

        Returns:
            Result of deprecation

        Emits:
            witness.spec.deprecated — For each deprecated spec
        """
        import time

        spec_root = get_spec_root()
        deprecated_paths: list[str] = []
        failed_paths: list[tuple[str, str]] = []

        deprecation_date = time.strftime("%Y-%m-%d")
        deprecation_notice = f"""---
> **⚠️ DEPRECATED** ({deprecation_date})
>
> {reason}
---

"""

        for path in paths:
            try:
                # Resolve path relative to spec root
                full_path = spec_root / path.replace("spec/", "")
                if not full_path.exists():
                    # Try without adjustment
                    full_path = Path(path)
                    if not full_path.exists():
                        failed_paths.append((path, "File not found"))
                        continue

                # Read current content
                content = full_path.read_text(encoding="utf-8")

                # Check if already deprecated
                if "**⚠️ DEPRECATED**" in content or "> **DEPRECATED**" in content:
                    failed_paths.append((path, "Already deprecated"))
                    continue

                # Prepend deprecation notice
                new_content = deprecation_notice + content
                full_path.write_text(new_content, encoding="utf-8")

                deprecated_paths.append(path)
                logger.info(f"Deprecated spec: {path}")

            except Exception as e:
                failed_paths.append((path, str(e)))
                logger.error(f"Failed to deprecate {path}: {e}")

        # Emit witness events for each deprecated spec
        _, topics = _get_witness_bus()
        if topics and deprecated_paths:
            await _emit_witness_event(
                topics.SPEC_DEPRECATED,
                {
                    "action": "deprecate",
                    "paths": deprecated_paths,
                    "reason": reason,
                    "date": deprecation_date,
                    "count": len(deprecated_paths),
                },
            )

        # Invalidate proxy handle since we modified files
        # This enables reactive staleness detection
        if deprecated_paths:
            store = get_proxy_handle_store()
            await store.invalidate(SourceType.SPEC_CORPUS)

        return {
            "success": len(deprecated_paths) > 0,
            "message": f"Deprecated {len(deprecated_paths)} of {len(paths)} specs",
            "paths": deprecated_paths,
            "reason": reason,
            "failed": [{"path": p, "error": e} for p, e in failed_paths],
        }


# =============================================================================
# Singleton
# =============================================================================

_ledger_node: LedgerNode | None = None


def get_ledger_node() -> LedgerNode:
    """Get or create the ledger node singleton."""
    global _ledger_node
    if _ledger_node is None:
        _ledger_node = LedgerNode()
    return _ledger_node


def reset_ledger_node() -> None:
    """Reset the ledger node and proxy store (for testing)."""
    global _ledger_node
    _ledger_node = None
    # Also reset the proxy store to clear spec corpus handle
    from services.proxy.store import reset_proxy_handle_store

    reset_proxy_handle_store()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core functions
    "ensure_scanned",
    "analyze_now",
    "get_spec_root",
    # Response types
    "LedgerSummary",
    "SpecEntry",
    "LedgerResponse",
    "SpecDetail",
    # AGENTESE Node
    "LedgerNode",
    "get_ledger_node",
    "reset_ledger_node",
    # Re-export for backward compatibility (use services.proxy.exceptions directly)
    "NoProxyHandleError",
]
