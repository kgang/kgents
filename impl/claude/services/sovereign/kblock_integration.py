"""
K-Block Isolation Verification: Theorem 3 from sovereign-data-guarantees.md

> *"Edits in K-Block b₁ do not affect K-Block b₂ until commit."*

This module provides verification that K-Block isolation guarantees hold:

1. PRISTINE: no uncommitted changes
2. DIRTY: changes exist but not committed (isolated)
3. STALE: underlying version changed (needs resync)
4. CONFLICTING: multiple K-Blocks editing same entity

Theorem 3 (Isolation Guarantee):
    ∀ K-Blocks b₁, b₂ editing the same entity:
        edits in b₁ do not affect b₂ until harness.save(b₁)

See: spec/protocols/sovereign-data-guarantees.md (Section 3, Theorem 3)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.k_block.core.kblock import KBlock

    from .store import SovereignStore


# =============================================================================
# Verification Result Types
# =============================================================================


@dataclass
class KBlockIsolationCheck:
    """
    Result of K-Block isolation verification.

    This verifies Theorem 3: Isolation Guarantee.

    Attributes:
        kblock_id: The K-Block identifier
        state: The isolation state (PRISTINE, DIRTY, STALE, CONFLICTING, ENTANGLED)
        is_isolated: Whether isolation guarantees hold
        conflict_with: Other K-Block IDs if conflicting (multiple editors)
        details: Human-readable explanation
        content_hash: Hash of current K-Block content
        base_hash: Hash of base content (at creation)
        sovereign_hash: Hash from sovereign store (source of truth)
    """

    kblock_id: str
    state: str  # PRISTINE, DIRTY, STALE, CONFLICTING, ENTANGLED
    is_isolated: bool
    conflict_with: list[str]  # Other K-Block IDs editing same entity
    details: str
    content_hash: str
    base_hash: str
    sovereign_hash: str | None = None


# =============================================================================
# Verification Functions
# =============================================================================


async def verify_kblock_isolation(
    kblock: "KBlock",
    store: "SovereignStore",
    all_blocks: list["KBlock"] | None = None,
) -> KBlockIsolationCheck:
    """
    Verify that K-Block maintains isolation guarantees (Theorem 3).

    Checks:
    1. PRISTINE: content == base_content (no local changes)
    2. DIRTY: content != base_content (isolated changes, not committed)
    3. STALE: sovereign version changed since K-Block creation
    4. CONFLICTING: STALE + DIRTY (both local and upstream changes)
    5. ENTANGLED: linked to another K-Block (special state)

    The verification ensures:
    - Local edits stay isolated until commit
    - Multiple K-Blocks editing same entity are detected
    - Stale state detected when upstream changes

    Args:
        kblock: The K-Block to verify
        store: Sovereign store (source of truth for committed content)
        all_blocks: Optional list of all active K-Blocks (for conflict detection)

    Returns:
        KBlockIsolationCheck with verification results

    Example:
        >>> check = await verify_kblock_isolation(kblock, store)
        >>> if not check.is_isolated:
        ...     print(f"Isolation violation: {check.details}")
    """
    from services.k_block.core.kblock import IsolationState

    # Compute content hashes
    content_hash = hashlib.sha256(kblock.content.encode()).hexdigest()[:16]
    base_hash = hashlib.sha256(kblock.base_content.encode()).hexdigest()[:16]

    # Get sovereign version (source of truth)
    sovereign_entity = await store.get_current(kblock.path)
    sovereign_hash = None
    if sovereign_entity:
        sovereign_hash = hashlib.sha256(sovereign_entity.content).hexdigest()[:16]

    # Detect conflicts with other K-Blocks
    conflict_with: list[str] = []
    if all_blocks:
        for other in all_blocks:
            if other.id != kblock.id and other.path == kblock.path:
                conflict_with.append(str(other.id))

    # Verify isolation state consistency
    state_name = kblock.isolation.name
    is_isolated = True
    details = ""

    if kblock.isolation == IsolationState.PRISTINE:
        # PRISTINE: no local changes
        if content_hash != base_hash:
            is_isolated = False
            details = "VIOLATION: PRISTINE but content != base_content"
        else:
            details = "OK: No uncommitted changes. Isolation guaranteed."

    elif kblock.isolation == IsolationState.DIRTY:
        # DIRTY: local changes exist, not committed
        if content_hash == base_hash:
            is_isolated = False
            details = "VIOLATION: DIRTY but content == base_content"
        else:
            details = (
                f"OK: Local changes isolated. {len(conflict_with)} other editors on same path."
            )
            if conflict_with:
                details += f" (Conflicts with: {', '.join(conflict_with[:3])})"

    elif kblock.isolation == IsolationState.STALE:
        # STALE: upstream changed since creation
        if sovereign_hash is None:
            details = "WARNING: STALE but no sovereign version exists"
        elif base_hash == sovereign_hash:
            is_isolated = False
            details = "VIOLATION: STALE but base_hash == sovereign_hash (not actually stale)"
        else:
            details = f"OK: Upstream changed. Base={base_hash}, Sovereign={sovereign_hash}."

    elif kblock.isolation == IsolationState.CONFLICTING:
        # CONFLICTING: both local and upstream changes
        has_local_changes = content_hash != base_hash
        has_upstream_changes = sovereign_hash is not None and base_hash != sovereign_hash

        if not has_local_changes:
            is_isolated = False
            details = "VIOLATION: CONFLICTING but no local changes"
        elif not has_upstream_changes:
            is_isolated = False
            details = "VIOLATION: CONFLICTING but no upstream changes"
        else:
            details = (
                f"OK: Conflict detected. Local changes + upstream changes. "
                f"Base={base_hash}, Content={content_hash}, Sovereign={sovereign_hash}."
            )

    elif kblock.isolation == IsolationState.ENTANGLED:
        # ENTANGLED: linked to another K-Block
        if kblock.entangled_with is None:
            is_isolated = False
            details = "VIOLATION: ENTANGLED but entangled_with is None"
        else:
            details = f"OK: Entangled with {kblock.entangled_with}. Special isolation rules apply."

    else:
        is_isolated = False
        details = f"UNKNOWN STATE: {kblock.isolation}"

    return KBlockIsolationCheck(
        kblock_id=str(kblock.id),
        state=state_name,
        is_isolated=is_isolated,
        conflict_with=conflict_with,
        details=details,
        content_hash=content_hash,
        base_hash=base_hash,
        sovereign_hash=sovereign_hash,
    )


async def verify_all_kblocks(
    blocks: list["KBlock"],
    store: "SovereignStore",
) -> list[KBlockIsolationCheck]:
    """
    Verify isolation for all active K-Blocks.

    This detects:
    - Multiple K-Blocks editing same entity (conflict potential)
    - State inconsistencies (DIRTY but no changes, etc.)
    - Stale K-Blocks (upstream changed)

    Args:
        blocks: All active K-Blocks
        store: Sovereign store

    Returns:
        List of verification results, one per K-Block

    Example:
        >>> harness = get_harness()
        >>> store = await get_sovereign_store()
        >>> checks = await verify_all_kblocks(harness.list_blocks(), store)
        >>> violations = [c for c in checks if not c.is_isolated]
        >>> if violations:
        ...     print(f"Found {len(violations)} isolation violations")
    """
    results = []

    for block in blocks:
        check = await verify_kblock_isolation(block, store, all_blocks=blocks)
        results.append(check)

    return results


async def detect_conflicting_editors(
    blocks: list["KBlock"],
) -> dict[str, list[str]]:
    """
    Detect multiple K-Blocks editing the same entity.

    This is a precondition check for potential conflicts.
    Theorem 3 guarantees isolation, but multiple editors on the same
    path will create a CONFLICTING state when one commits.

    Args:
        blocks: All active K-Blocks

    Returns:
        Dict mapping path → list of K-Block IDs editing that path

    Example:
        >>> harness = get_harness()
        >>> conflicts = await detect_conflicting_editors(harness.list_blocks())
        >>> for path, editors in conflicts.items():
        ...     if len(editors) > 1:
        ...         print(f"WARNING: {len(editors)} editors on {path}")
    """
    path_to_blocks: dict[str, list[str]] = {}

    for block in blocks:
        if block.path not in path_to_blocks:
            path_to_blocks[block.path] = []
        path_to_blocks[block.path].append(str(block.id))

    # Filter to only paths with multiple editors
    return {path: editors for path, editors in path_to_blocks.items() if len(editors) > 1}


# =============================================================================
# Teaching Notes
# =============================================================================

"""
Gotcha: K-Block isolation is a RUNTIME property, not a static one.

    The state can change when:
    1. harness.save(other_block) commits to same path → STALE
    2. block.set_content(...) modifies content → DIRTY
    3. harness.create(path) when already editing → conflict potential

    Verification should run:
    - Before save (ensure no CONFLICTING state)
    - After save (verify dependents marked STALE)
    - Periodically (detect stale K-Blocks)

Gotcha: Multiple K-Blocks on same path is NOT a violation.

    Isolation guarantees that edits in b₁ don't affect b₂ until commit.
    When b₁ commits, b₂ should transition to STALE.
    This is correct behavior, not a bug.

Gotcha: CONFLICTING state requires user resolution.

    harness.save() will reject CONFLICTING K-Blocks.
    User must either:
    1. Rebase onto sovereign version (discard local changes)
    2. Force save (override upstream changes)
    3. Manual merge (combine both changes)

Gotcha: Sovereign store is source of truth for "committed" content.

    K-Block.base_content is a snapshot at creation time.
    Sovereign store has the CURRENT committed version.
    If base_hash != sovereign_hash, the K-Block is STALE.
"""


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "KBlockIsolationCheck",
    "verify_kblock_isolation",
    "verify_all_kblocks",
    "detect_conflicting_editors",
]
