"""
Tests for K-Block isolation verification (Theorem 3).

These tests verify that the K-Block isolation guarantees hold:
- PRISTINE: no uncommitted changes
- DIRTY: changes exist but not committed (isolated)
- STALE: underlying version changed (needs resync)
- CONFLICTING: multiple K-Blocks editing same entity
"""

import hashlib

import pytest

from services.k_block.core.kblock import IsolationState, KBlock, generate_kblock_id
from services.sovereign.kblock_integration import (
    detect_conflicting_editors,
    verify_all_kblocks,
    verify_kblock_isolation,
)
from services.sovereign.store import SovereignStore


@pytest.fixture
def temp_store(tmp_path):
    """Create a temporary sovereign store."""
    return SovereignStore(root=tmp_path / "sovereign")


@pytest.fixture
def pristine_kblock():
    """Create a PRISTINE K-Block (no changes)."""
    return KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Test Content",
        base_content="# Test Content",
        isolation=IsolationState.PRISTINE,
    )


@pytest.fixture
def dirty_kblock():
    """Create a DIRTY K-Block (local changes)."""
    return KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Modified Content",
        base_content="# Test Content",
        isolation=IsolationState.DIRTY,
    )


@pytest.fixture
async def stale_kblock(temp_store):
    """Create a STALE K-Block (upstream changed)."""
    # First, ingest a version to sovereign store
    await temp_store.store_version(
        path="spec/test.md",
        content=b"# Upstream Content",
        ingest_mark="mark-upstream",
        metadata={"source": "git"},
    )

    # Create K-Block with old base_content
    return KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Old Content",
        base_content="# Old Content",
        isolation=IsolationState.STALE,
    )


# =============================================================================
# PRISTINE State Tests
# =============================================================================


@pytest.mark.asyncio
async def test_pristine_kblock_passes_verification(pristine_kblock, temp_store):
    """PRISTINE K-Block should pass isolation verification."""
    check = await verify_kblock_isolation(pristine_kblock, temp_store)

    assert check.is_isolated
    assert check.state == "PRISTINE"
    assert check.content_hash == check.base_hash
    assert "No uncommitted changes" in check.details


@pytest.mark.asyncio
async def test_pristine_with_changes_fails_verification(temp_store):
    """PRISTINE K-Block with content != base_content is a violation."""
    # Create K-Block marked PRISTINE but with changes (incorrect state)
    kblock = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Modified",
        base_content="# Original",
        isolation=IsolationState.PRISTINE,
    )

    check = await verify_kblock_isolation(kblock, temp_store)

    assert not check.is_isolated
    assert "VIOLATION" in check.details
    assert check.content_hash != check.base_hash


# =============================================================================
# DIRTY State Tests
# =============================================================================


@pytest.mark.asyncio
async def test_dirty_kblock_passes_verification(dirty_kblock, temp_store):
    """DIRTY K-Block with local changes should pass verification."""
    check = await verify_kblock_isolation(dirty_kblock, temp_store)

    assert check.is_isolated
    assert check.state == "DIRTY"
    assert check.content_hash != check.base_hash
    assert "Local changes isolated" in check.details


@pytest.mark.asyncio
async def test_dirty_without_changes_fails_verification(temp_store):
    """DIRTY K-Block without actual changes is a violation."""
    # Create K-Block marked DIRTY but no changes (incorrect state)
    kblock = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Same Content",
        base_content="# Same Content",
        isolation=IsolationState.DIRTY,
    )

    check = await verify_kblock_isolation(kblock, temp_store)

    assert not check.is_isolated
    assert "VIOLATION" in check.details
    assert check.content_hash == check.base_hash


# =============================================================================
# STALE State Tests
# =============================================================================


@pytest.mark.asyncio
async def test_stale_kblock_passes_verification(stale_kblock, temp_store):
    """STALE K-Block (upstream changed) should pass verification."""
    check = await verify_kblock_isolation(stale_kblock, temp_store)

    assert check.is_isolated
    assert check.state == "STALE"
    assert check.base_hash != check.sovereign_hash
    assert "Upstream changed" in check.details


@pytest.mark.asyncio
async def test_stale_with_matching_upstream_fails(temp_store):
    """STALE K-Block where base matches upstream is a violation."""
    # Ingest current version
    await temp_store.store_version(
        path="spec/test.md",
        content=b"# Content",
        ingest_mark="mark-1",
    )

    # Create K-Block marked STALE but base matches upstream (incorrect)
    kblock = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Content",
        base_content="# Content",
        isolation=IsolationState.STALE,
    )

    check = await verify_kblock_isolation(kblock, temp_store)

    assert not check.is_isolated
    assert "VIOLATION" in check.details


# =============================================================================
# CONFLICTING State Tests
# =============================================================================


@pytest.mark.asyncio
async def test_conflicting_kblock_passes_verification(temp_store):
    """CONFLICTING K-Block (local + upstream changes) should pass."""
    # Ingest upstream version
    await temp_store.store_version(
        path="spec/test.md",
        content=b"# Upstream Changes",
        ingest_mark="mark-1",
    )

    # Create K-Block with both local and upstream changes
    kblock = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Local Changes",
        base_content="# Original",
        isolation=IsolationState.CONFLICTING,
    )

    check = await verify_kblock_isolation(kblock, temp_store)

    assert check.is_isolated
    assert check.state == "CONFLICTING"
    assert "Conflict detected" in check.details
    assert check.content_hash != check.base_hash
    assert check.base_hash != check.sovereign_hash


@pytest.mark.asyncio
async def test_conflicting_without_local_changes_fails(temp_store):
    """CONFLICTING without local changes is a violation."""
    # Ingest upstream version
    await temp_store.store_version(
        path="spec/test.md",
        content=b"# Upstream",
        ingest_mark="mark-1",
    )

    # Create K-Block marked CONFLICTING but no local changes
    kblock = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Original",
        base_content="# Original",
        isolation=IsolationState.CONFLICTING,
    )

    check = await verify_kblock_isolation(kblock, temp_store)

    assert not check.is_isolated
    assert "VIOLATION" in check.details
    assert "no local changes" in check.details


# =============================================================================
# Multiple Editors (Conflict Detection)
# =============================================================================


@pytest.mark.asyncio
async def test_detect_conflicting_editors():
    """Multiple K-Blocks on same path should be detected."""
    kblock1 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Editor 1",
        base_content="# Original",
        isolation=IsolationState.DIRTY,
    )

    kblock2 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Editor 2",
        base_content="# Original",
        isolation=IsolationState.DIRTY,
    )

    kblock3 = KBlock(
        id=generate_kblock_id(),
        path="spec/other.md",
        content="# No conflict",
        base_content="# No conflict",
        isolation=IsolationState.PRISTINE,
    )

    conflicts = await detect_conflicting_editors([kblock1, kblock2, kblock3])

    assert "spec/test.md" in conflicts
    assert len(conflicts["spec/test.md"]) == 2
    assert str(kblock1.id) in conflicts["spec/test.md"]
    assert str(kblock2.id) in conflicts["spec/test.md"]
    assert "spec/other.md" not in conflicts


@pytest.mark.asyncio
async def test_verify_dirty_kblock_reports_conflicts(temp_store):
    """DIRTY K-Block should report other editors on same path."""
    kblock1 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Editor 1",
        base_content="# Original",
        isolation=IsolationState.DIRTY,
    )

    kblock2 = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Editor 2",
        base_content="# Original",
        isolation=IsolationState.DIRTY,
    )

    check = await verify_kblock_isolation(kblock1, temp_store, all_blocks=[kblock1, kblock2])

    assert check.is_isolated  # Still isolated (changes don't affect each other)
    assert len(check.conflict_with) == 1
    assert str(kblock2.id) in check.conflict_with
    assert "other editors" in check.details.lower()


# =============================================================================
# Batch Verification
# =============================================================================


@pytest.mark.asyncio
async def test_verify_all_kblocks(pristine_kblock, dirty_kblock, temp_store):
    """verify_all_kblocks should check all blocks."""
    blocks = [pristine_kblock, dirty_kblock]

    checks = await verify_all_kblocks(blocks, temp_store)

    assert len(checks) == 2
    assert all(check.is_isolated for check in checks)

    # Check states
    states = {check.state for check in checks}
    assert states == {"PRISTINE", "DIRTY"}


@pytest.mark.asyncio
async def test_verify_all_detects_violations(temp_store):
    """verify_all_kblocks should detect state violations."""
    # Create one valid, one invalid K-Block
    valid = KBlock(
        id=generate_kblock_id(),
        path="spec/valid.md",
        content="# Valid",
        base_content="# Valid",
        isolation=IsolationState.PRISTINE,
    )

    invalid = KBlock(
        id=generate_kblock_id(),
        path="spec/invalid.md",
        content="# Changed",
        base_content="# Original",
        isolation=IsolationState.PRISTINE,  # Wrong state!
    )

    checks = await verify_all_kblocks([valid, invalid], temp_store)

    assert len(checks) == 2

    # One should pass, one should fail
    violations = [c for c in checks if not c.is_isolated]
    assert len(violations) == 1
    assert violations[0].kblock_id == str(invalid.id)


# =============================================================================
# Edge Cases
# =============================================================================


@pytest.mark.asyncio
async def test_kblock_without_sovereign_version(temp_store):
    """K-Block for path not in sovereign store should handle gracefully."""
    kblock = KBlock(
        id=generate_kblock_id(),
        path="spec/not-ingested.md",
        content="# Content",
        base_content="# Content",
        isolation=IsolationState.PRISTINE,
    )

    check = await verify_kblock_isolation(kblock, temp_store)

    assert check.is_isolated
    assert check.sovereign_hash is None


@pytest.mark.asyncio
async def test_entangled_kblock(temp_store):
    """ENTANGLED K-Block should require entangled_with to be set."""
    # Valid entanglement
    kblock = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Content",
        base_content="# Content",
        isolation=IsolationState.ENTANGLED,
        entangled_with=generate_kblock_id(),
    )

    check = await verify_kblock_isolation(kblock, temp_store)

    assert check.is_isolated
    assert "Entangled with" in check.details


@pytest.mark.asyncio
async def test_entangled_without_target_fails(temp_store):
    """ENTANGLED K-Block without entangled_with is a violation."""
    kblock = KBlock(
        id=generate_kblock_id(),
        path="spec/test.md",
        content="# Content",
        base_content="# Content",
        isolation=IsolationState.ENTANGLED,
        entangled_with=None,  # Violation!
    )

    check = await verify_kblock_isolation(kblock, temp_store)

    assert not check.is_isolated
    assert "VIOLATION" in check.details
