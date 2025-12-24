"""
Provenance Chain Retrieval: Implementation of Theorem 2.

> *"The proof IS the possession. The witness IS the guarantee."*

This module implements Theorem 2 from spec/protocols/sovereign-data-guarantees.md:

    For any entity e, we can reconstruct the complete history:
    who created it, when, from where, and all modifications.

The proof shows: Chain: current → v_n → v_{n-1} → ... → v_1 → ingest_mark

Provenance chain structure:
1. Get all versions from SovereignStore (v1, v2, v3, ...)
2. For each version, get its ingest mark from metadata
3. For each mark, follow parent_mark_id chain to birth
4. Build ProvenanceChain from birth to current

Teaching:
    gotcha: Marks can have parent_mark_id, creating causal chains.
            Ingest marks are typically roots (no parent).
            Modification marks reference their ingest parent.

    gotcha: Version metadata contains ingest_mark but not analysis marks.
            Analysis marks link to entities via tags (spec:{path}).

See: spec/protocols/sovereign-data-guarantees.md → Theorem 2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .store import SovereignStore

# =============================================================================
# Provenance Data Structures
# =============================================================================


@dataclass
class ProvenanceStep:
    """
    One step in the provenance chain.

    Represents either:
    - A version transition (ingest or sync creating new version)
    - A mark in the causal chain (parent marks)

    Fields:
        version: Version number (None for pure mark steps)
        mark_id: The witness mark ID (None if no mark found)
        timestamp: When this step occurred
        action: What happened ("ingest", "sync", "modification", etc.)
        author: Who did it (None if unknown)
        metadata: Additional context (source, reasoning, principles, tags)
    """

    version: int | None
    mark_id: str | None
    timestamp: str
    action: str
    author: str | None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "mark_id": self.mark_id,
            "timestamp": self.timestamp,
            "action": self.action,
            "author": self.author,
            "metadata": self.metadata,
        }


@dataclass
class ProvenanceChain:
    """
    Complete provenance for an entity.

    The chain reconstructs the full history from birth (first ingest)
    to current state, following Law 1 (No Entity Without Witness).

    Fields:
        path: The entity path
        steps: List of ProvenanceStep from birth to current
        birth_mark_id: The original ingest mark (if found)
        current_version: Current version number
        total_versions: Total number of versions

    Example:
        >>> chain = await get_provenance_chain(store, witness, "spec/k-block.md")
        >>> assert chain.is_complete  # Has birth mark
        >>> for step in chain.steps:
        ...     print(f"v{step.version}: {step.action} by {step.author}")
    """

    path: str
    steps: list[ProvenanceStep] = field(default_factory=list)
    birth_mark_id: str | None = None
    current_version: int | None = None
    total_versions: int = 0

    @property
    def is_complete(self) -> bool:
        """
        Chain is complete if it ends at a birth mark.

        By Law 1, every entity must have an ingest mark.
        If we can't find it, the chain is incomplete (data loss).
        """
        return self.birth_mark_id is not None

    @property
    def modification_count(self) -> int:
        """Number of modifications (versions after v1)."""
        return max(0, self.total_versions - 1)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "steps": [step.to_dict() for step in self.steps],
            "birth_mark_id": self.birth_mark_id,
            "current_version": self.current_version,
            "total_versions": self.total_versions,
            "is_complete": self.is_complete,
            "modification_count": self.modification_count,
        }


# =============================================================================
# Provenance Chain Retrieval
# =============================================================================


async def get_provenance_chain(
    store: SovereignStore,
    witness: Any | None,  # WitnessPersistence, optional
    path: str,
) -> ProvenanceChain:
    """
    Reconstruct full provenance chain for an entity.

    Implementation of Theorem 2: Provenance Guarantee.

    Algorithm:
    1. Get all versions from store (ascending order)
    2. For each version, extract ingest mark from metadata
    3. Build step for each version
    4. If witness available, follow parent_mark_id chain
    5. Return ProvenanceChain from birth to current

    Args:
        store: SovereignStore instance
        witness: WitnessPersistence instance (optional for mark ancestry)
        path: Entity path to trace

    Returns:
        ProvenanceChain with complete history

    Raises:
        ValueError: If entity doesn't exist

    Example:
        >>> chain = await get_provenance_chain(store, witness, "spec/k-block.md")
        >>> assert chain.is_complete
        >>> print(f"Entity created at {chain.steps[0].timestamp}")
    """
    # Check entity exists
    if not await store.exists(path):
        raise ValueError(f"Entity not found: {path}")

    # Get all versions
    versions = await store.list_versions(path)
    if not versions:
        raise ValueError(f"Entity exists but has no versions: {path}")

    chain = ProvenanceChain(
        path=path,
        current_version=max(versions) if versions else None,
        total_versions=len(versions),
    )

    # Build steps for each version (chronological order)
    for version in sorted(versions):
        entity = await store.get_version(path, version)
        if not entity:
            continue

        # Extract metadata
        metadata = entity.metadata
        mark_id = metadata.get("ingest_mark")
        timestamp = metadata.get("ingested_at", "")
        source = metadata.get("source", "unknown")

        # Determine action type
        if version == 1:
            action = "ingest"
        elif metadata.get("renamed_from"):
            action = f"rename from {metadata['renamed_from']}"
        else:
            action = "sync"

        # Create step
        step = ProvenanceStep(
            version=version,
            mark_id=mark_id,
            timestamp=timestamp,
            action=action,
            author=metadata.get("source_author"),
            metadata={
                "source": source,
                "content_hash": metadata.get("content_hash"),
            },
        )

        chain.steps.append(step)

        # Track birth mark (first version's mark)
        if version == 1 and mark_id:
            chain.birth_mark_id = mark_id

    # If witness available and we have a birth mark, get mark ancestry
    if witness and chain.birth_mark_id:
        try:
            # Get ancestry from birth mark to root
            mark_ancestry = await witness.get_mark_ancestry(chain.birth_mark_id)

            # Add parent marks as steps (if any beyond the ingest mark itself)
            for mark_result in mark_ancestry[1:]:  # Skip first (already added)
                parent_step = ProvenanceStep(
                    version=None,  # Not a version transition
                    mark_id=mark_result.mark_id,
                    timestamp=mark_result.timestamp.isoformat(),
                    action=mark_result.action,
                    author=mark_result.author,
                    metadata={
                        "reasoning": mark_result.reasoning,
                        "principles": mark_result.principles,
                        "tags": mark_result.tags,
                    },
                )
                # Insert at beginning (ancestry goes newest to oldest)
                chain.steps.insert(0, parent_step)

        except Exception as e:
            # Graceful degradation if witness unavailable
            # Chain is still valid from store metadata alone
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Could not retrieve mark ancestry for {path}: {e}")

    return chain


async def get_provenance_summary(
    store: SovereignStore,
    witness: Any | None,
    path: str,
) -> dict[str, Any]:
    """
    Get a summary of provenance without full chain details.

    Lightweight alternative to get_provenance_chain for dashboards.

    Args:
        store: SovereignStore instance
        witness: WitnessPersistence instance (optional)
        path: Entity path

    Returns:
        Summary dict with key provenance facts

    Example:
        >>> summary = await get_provenance_summary(store, witness, "spec/k-block.md")
        >>> print(f"Created: {summary['created_at']}")
        >>> print(f"Versions: {summary['version_count']}")
    """
    chain = await get_provenance_chain(store, witness, path)

    # Extract key facts
    first_step = chain.steps[0] if chain.steps else None
    last_step = chain.steps[-1] if chain.steps else None

    return {
        "path": path,
        "created_at": first_step.timestamp if first_step else None,
        "created_by": first_step.author if first_step else None,
        "last_modified_at": last_step.timestamp if last_step else None,
        "version_count": chain.total_versions,
        "modification_count": chain.modification_count,
        "birth_mark_id": chain.birth_mark_id,
        "is_complete": chain.is_complete,
    }


async def verify_provenance_integrity(
    store: SovereignStore,
    witness: Any | None,
    path: str,
) -> dict[str, Any]:
    """
    Verify provenance guarantees for an entity.

    Checks:
    1. Entity has at least one version (Law 0)
    2. Entity has birth mark (Law 1)
    3. All versions have ingest marks
    4. Marks are retrievable (if witness available)
    5. Version sequence is valid (no gaps)

    Args:
        store: SovereignStore instance
        witness: WitnessPersistence instance (optional)
        path: Entity path to verify

    Returns:
        Verification result dict with checks and violations

    Example:
        >>> result = await verify_provenance_integrity(store, witness, "spec/k-block.md")
        >>> assert result["valid"]
        >>> if not result["valid"]:
        ...     print(f"Violations: {result['violations']}")
    """
    violations = []
    checks = []

    try:
        chain = await get_provenance_chain(store, witness, path)

        # Check: Has versions (Law 0)
        if chain.total_versions == 0:
            violations.append("No versions found (Law 0 violation)")
        checks.append({
            "check": "has_versions",
            "passed": chain.total_versions > 0,
            "detail": f"{chain.total_versions} versions",
        })

        # Check: Has birth mark (Law 1)
        if not chain.birth_mark_id:
            violations.append("No birth mark found (Law 1 violation)")
        checks.append({
            "check": "has_birth_mark",
            "passed": chain.birth_mark_id is not None,
            "detail": f"birth_mark={chain.birth_mark_id}",
        })

        # Check: All versions have marks
        missing_marks = [
            step.version for step in chain.steps if step.version and not step.mark_id
        ]
        if missing_marks:
            violations.append(
                f"Versions without marks: {missing_marks} (Law 1 violation)"
            )
        checks.append({
            "check": "all_versions_have_marks",
            "passed": len(missing_marks) == 0,
            "detail": f"{len(missing_marks)} missing",
        })

        # Check: Version sequence is valid
        versions = [step.version for step in chain.steps if step.version]
        expected = list(range(1, len(versions) + 1))
        if sorted(versions) != expected:
            violations.append(f"Invalid version sequence: {versions} != {expected}")
        checks.append({
            "check": "valid_version_sequence",
            "passed": sorted(versions) == expected,
            "detail": f"versions={versions}",
        })

        # Check: Birth mark is retrievable (if witness available)
        if witness and chain.birth_mark_id:
            try:
                mark = await witness.get_mark(chain.birth_mark_id)
                if not mark:
                    violations.append(f"Birth mark not found: {chain.birth_mark_id}")
                checks.append({
                    "check": "birth_mark_retrievable",
                    "passed": mark is not None,
                    "detail": f"mark_id={chain.birth_mark_id}",
                })
            except Exception as e:
                violations.append(f"Error retrieving birth mark: {e}")
                checks.append({
                    "check": "birth_mark_retrievable",
                    "passed": False,
                    "detail": str(e),
                })

        return {
            "path": path,
            "valid": len(violations) == 0,
            "violations": violations,
            "checks": checks,
            "provenance_complete": chain.is_complete,
        }

    except ValueError as e:
        return {
            "path": path,
            "valid": False,
            "violations": [str(e)],
            "checks": [],
            "provenance_complete": False,
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ProvenanceStep",
    "ProvenanceChain",
    "get_provenance_chain",
    "get_provenance_summary",
    "verify_provenance_integrity",
]
