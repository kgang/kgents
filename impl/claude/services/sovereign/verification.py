"""
Sovereign Verification: Guarantee Enforcement at Runtime.

> *"The proof IS the possession. The witness IS the guarantee."*

This module implements the verification protocol from spec/protocols/sovereign-data-guarantees.md.
It provides runtime checks for the Four Sovereign Laws:

    Law 0: No Entity Without Copy
    Law 1: No Entity Without Witness
    Law 2: No Edge Without Witness
    Theorem 1: Hash Integrity (content unchanged since ingest)

Each check returns a Check dataclass with:
- name: The check performed
- passed: Whether the check passed
- details: Additional context (errors, warnings, etc.)

Teaching:
    gotcha: This module doesn't fix violations, it only detects them.
            Violations indicate bugs in the ingest/analysis pipeline.

    gotcha: verify_integrity() checks a single entity.
            verify_all() checks the entire store (can be slow).

See: spec/protocols/sovereign-data-guarantees.md Section 9
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any

from .analysis import AnalysisStatus

logger = logging.getLogger(__name__)


# =============================================================================
# Verification Results
# =============================================================================


@dataclass
class Check:
    """
    Result of a single verification check.

    Fields:
        name: Check identifier (e.g., "content_exists", "witness_exists")
        passed: Whether the check passed
        details: Additional context (error messages, warnings, etc.)
    """

    name: str
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """
    Result of verifying all guarantees for an entity.

    Fields:
        path: Entity path verified
        checks: List of Check results
        all_passed: Whether all checks passed
        errors: List of error messages (for failed checks)
        warnings: List of warnings (for suspicious but not invalid states)
    """

    path: str
    checks: list[Check]
    all_passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "all_passed": self.all_passed,
            "checks": [
                {"name": c.name, "passed": c.passed, "details": c.details}
                for c in self.checks
            ],
            "errors": self.errors,
            "warnings": self.warnings,
            "passed_count": sum(1 for c in self.checks if c.passed),
            "failed_count": sum(1 for c in self.checks if not c.passed),
            "total_checks": len(self.checks),
        }


# =============================================================================
# Verification Functions
# =============================================================================


async def verify_integrity(
    store: Any,  # SovereignStore
    witness: Any,  # WitnessPersistence
    path: str,
) -> VerificationResult:
    """
    Verify all guarantees for a single entity.

    Performs these checks:
    1. Law 0 (content_exists): entity.content is not None
    2. Law 1 (witness_exists): can retrieve ingest mark via mark_id
    3. Theorem 1 (hash_integrity): recompute SHA256 and compare to stored
    4. Law 2 (edges_witnessed): if analyzed, analysis_mark_id exists

    Args:
        store: SovereignStore instance
        witness: WitnessPersistence instance
        path: Entity path to verify

    Returns:
        VerificationResult with all check results

    Example:
        >>> result = await verify_integrity(store, witness, "spec/protocols/k-block.md")
        >>> if not result.all_passed:
        ...     print(f"Violations detected: {result.errors}")
    """
    checks: list[Check] = []
    errors: list[str] = []
    warnings: list[str] = []

    # Get the entity
    entity = await store.get_current(path)

    if entity is None:
        # Entity doesn't exist - special case
        return VerificationResult(
            path=path,
            checks=[
                Check(
                    name="entity_exists",
                    passed=False,
                    details={"error": "Entity not found in store"},
                )
            ],
            all_passed=False,
            errors=[f"Entity not found: {path}"],
        )

    # =========================================================================
    # Law 0: Content Exists
    # =========================================================================

    content_exists = entity.content is not None and len(entity.content) > 0
    checks.append(
        Check(
            name="content_exists",
            passed=content_exists,
            details={
                "content_length": len(entity.content) if entity.content else 0,
            },
        )
    )

    if not content_exists:
        errors.append(f"Law 0 violation: No content for {path}")

    # =========================================================================
    # Law 1: Witness Exists
    # =========================================================================

    ingest_mark_id = entity.metadata.get("ingest_mark")
    witness_exists = False
    witness_details: dict[str, Any] = {}

    if ingest_mark_id:
        try:
            mark = await witness.get_mark(ingest_mark_id)
            witness_exists = mark is not None

            if mark:
                witness_details = {
                    "mark_id": mark.mark_id,
                    "action": mark.action,
                    "author": mark.author,
                    "timestamp": mark.timestamp.isoformat() if mark.timestamp else None,
                }
            else:
                witness_details = {"error": "Mark not found"}
                errors.append(f"Law 1 violation: Ingest mark not found: {ingest_mark_id}")

        except Exception as e:
            witness_details = {"error": str(e)}
            errors.append(f"Law 1 violation: Failed to retrieve mark: {e}")
    else:
        witness_details = {"error": "No ingest_mark in metadata"}
        errors.append(f"Law 1 violation: No ingest mark for {path}")

    checks.append(
        Check(
            name="witness_exists",
            passed=witness_exists,
            details=witness_details,
        )
    )

    # =========================================================================
    # Theorem 1: Hash Integrity
    # =========================================================================

    hash_integrity = False
    hash_details: dict[str, Any] = {}

    if entity.content:
        computed_hash = hashlib.sha256(entity.content).hexdigest()
        stored_hash = entity.metadata.get("content_hash") or entity.content_hash

        hash_integrity = computed_hash == stored_hash

        hash_details = {
            "computed_hash": computed_hash,
            "stored_hash": stored_hash,
            "match": hash_integrity,
        }

        if not hash_integrity:
            errors.append(
                f"Theorem 1 violation: Hash mismatch for {path} "
                f"(stored: {stored_hash[:8]}..., computed: {computed_hash[:8]}...)"
            )
    else:
        hash_details = {"error": "No content to hash"}
        warnings.append(f"Cannot verify hash integrity: No content for {path}")

    checks.append(
        Check(
            name="hash_integrity",
            passed=hash_integrity,
            details=hash_details,
        )
    )

    # =========================================================================
    # Law 2: Edges Witnessed (if analyzed)
    # =========================================================================

    is_analyzed = await store.is_analyzed(path)
    edges_witnessed = True  # Default: pass if not analyzed
    edges_details: dict[str, Any] = {"analyzed": is_analyzed}

    if is_analyzed:
        state = await store.get_analysis_state(path)

        if state:
            has_analysis_mark = state.analysis_mark_id is not None

            edges_details["status"] = state.status.value
            edges_details["analysis_mark_id"] = state.analysis_mark_id
            edges_details["discovered_refs"] = len(state.discovered_refs)

            # Check if analysis mark exists
            if has_analysis_mark:
                try:
                    analysis_mark = await witness.get_mark(state.analysis_mark_id)
                    edges_witnessed = analysis_mark is not None

                    if not analysis_mark:
                        errors.append(
                            f"Law 2 violation: Analysis mark not found: {state.analysis_mark_id}"
                        )
                        edges_details["error"] = "Analysis mark not found"
                except Exception as e:
                    edges_witnessed = False
                    errors.append(f"Law 2 violation: Failed to retrieve analysis mark: {e}")
                    edges_details["error"] = str(e)
            else:
                edges_witnessed = False
                errors.append(f"Law 2 violation: Analyzed entity missing analysis mark: {path}")
                edges_details["error"] = "No analysis_mark_id"
        else:
            edges_witnessed = False
            errors.append(f"Law 2 violation: Analyzed entity missing analysis state: {path}")
            edges_details["error"] = "No analysis state"

    checks.append(
        Check(
            name="edges_witnessed",
            passed=edges_witnessed,
            details=edges_details,
        )
    )

    # =========================================================================
    # Build Result
    # =========================================================================

    all_passed = all(c.passed for c in checks)

    return VerificationResult(
        path=path,
        checks=checks,
        all_passed=all_passed,
        errors=errors,
        warnings=warnings,
    )


async def verify_all(
    store: Any,  # SovereignStore
    witness: Any,  # WitnessPersistence
) -> dict[str, VerificationResult]:
    """
    Verify all entities in the sovereign store.

    This can be slow for large stores (O(n) entities × O(1) checks).

    Args:
        store: SovereignStore instance
        witness: WitnessPersistence instance

    Returns:
        Dictionary mapping path → VerificationResult
        Only includes entities with violations (failed checks)

    Example:
        >>> violations = await verify_all(store, witness)
        >>> if violations:
        ...     print(f"Found {len(violations)} entities with violations")
        ...     for path, result in violations.items():
        ...         print(f"  {path}: {result.errors}")
    """
    all_paths = await store.list_all()
    violations: dict[str, VerificationResult] = {}

    logger.info(f"Verifying {len(all_paths)} entities...")

    for path in all_paths:
        try:
            result = await verify_integrity(store, witness, path)

            if not result.all_passed:
                violations[path] = result

        except Exception as e:
            logger.error(f"Failed to verify {path}: {e}")
            violations[path] = VerificationResult(
                path=path,
                checks=[
                    Check(
                        name="verification_error",
                        passed=False,
                        details={"error": str(e)},
                    )
                ],
                all_passed=False,
                errors=[f"Verification failed: {e}"],
            )

    logger.info(
        f"Verification complete: {len(violations)} violations found "
        f"({len(all_paths) - len(violations)} entities passed)"
    )

    return violations


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "Check",
    "VerificationResult",
    "verify_integrity",
    "verify_all",
]
