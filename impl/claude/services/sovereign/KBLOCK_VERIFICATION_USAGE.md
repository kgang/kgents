# K-Block Isolation Verification: Usage Guide

This guide shows how to use the K-Block isolation verification functions to ensure Theorem 3 guarantees hold.

## Quick Start

```python
from services.k_block.core.harness import get_harness
from services.providers import get_sovereign_store
from services.sovereign import verify_kblock_isolation, verify_all_kblocks

# Get dependencies
harness = get_harness()
store = await get_sovereign_store()

# Verify a single K-Block
kblock = harness.get_block(kblock_id)
check = await verify_kblock_isolation(kblock, store)

if not check.is_isolated:
    print(f"VIOLATION: {check.details}")
else:
    print(f"OK: {check.state} - {check.details}")
```

## Use Cases

### 1. Pre-Save Verification

Before committing a K-Block, verify it's not in CONFLICTING state:

```python
async def safe_save(kblock: KBlock) -> SaveResult:
    """Save with pre-verification."""
    store = await get_sovereign_store()
    check = await verify_kblock_isolation(kblock, store)

    if not check.is_isolated:
        return SaveResult.err(kblock.path, f"Isolation violation: {check.details}")

    if check.state == "CONFLICTING":
        return SaveResult.err(kblock.path, "Resolve conflicts before saving")

    return await harness.save(kblock)
```

### 2. Detect Multiple Editors

Check if multiple K-Blocks are editing the same entity:

```python
from services.sovereign import detect_conflicting_editors

harness = get_harness()
all_blocks = harness.list_blocks()

conflicts = await detect_conflicting_editors(all_blocks)

for path, editors in conflicts.items():
    if len(editors) > 1:
        print(f"WARNING: {len(editors)} editors on {path}")
        print(f"  K-Blocks: {', '.join(editors)}")
```

### 3. Batch Verification

Verify all active K-Blocks at once:

```python
from services.sovereign import verify_all_kblocks

harness = get_harness()
store = await get_sovereign_store()

checks = await verify_all_kblocks(harness.list_blocks(), store)

# Find violations
violations = [c for c in checks if not c.is_isolated]

if violations:
    print(f"Found {len(violations)} isolation violations:")
    for v in violations:
        print(f"  - K-Block {v.kblock_id}: {v.details}")
```

### 4. Stale K-Block Detection

Find K-Blocks that need refresh (upstream changed):

```python
checks = await verify_all_kblocks(harness.list_blocks(), store)

stale_blocks = [c for c in checks if c.state in ("STALE", "CONFLICTING")]

for stale in stale_blocks:
    print(f"K-Block {stale.kblock_id} needs refresh:")
    print(f"  Base hash: {stale.base_hash}")
    print(f"  Sovereign hash: {stale.sovereign_hash}")
```

## Verification Fields

The `KBlockIsolationCheck` result contains:

```python
@dataclass
class KBlockIsolationCheck:
    kblock_id: str                # K-Block identifier
    state: str                    # PRISTINE, DIRTY, STALE, CONFLICTING, ENTANGLED
    is_isolated: bool             # True if isolation guarantees hold
    conflict_with: list[str]      # Other K-Block IDs editing same entity
    details: str                  # Human-readable explanation
    content_hash: str             # Hash of current K-Block content
    base_hash: str                # Hash of base content (at creation)
    sovereign_hash: str | None    # Hash from sovereign store
```

## State Interpretations

### PRISTINE
- **Meaning**: No local changes
- **Check**: `content_hash == base_hash`
- **Action**: None needed, K-Block matches source

### DIRTY
- **Meaning**: Local changes not yet committed
- **Check**: `content_hash != base_hash`
- **Action**: Save or discard when ready

### STALE
- **Meaning**: Upstream changed since K-Block creation
- **Check**: `base_hash != sovereign_hash`
- **Action**: Refresh from sovereign or resolve manually

### CONFLICTING
- **Meaning**: Both local and upstream changes
- **Check**: `content != base` AND `base != sovereign`
- **Action**: Manual merge required before save

### ENTANGLED
- **Meaning**: Linked to another K-Block
- **Check**: `entangled_with` is set
- **Action**: Special rules apply, see K-Block spec

## Common Patterns

### Pre-commit Hook

```python
async def verify_before_commit(kblock: KBlock) -> tuple[bool, str]:
    """Verify K-Block before commit."""
    store = await get_sovereign_store()
    check = await verify_kblock_isolation(kblock, store)

    if not check.is_isolated:
        return False, f"Isolation violation: {check.details}"

    if check.state == "CONFLICTING":
        return False, "Cannot commit CONFLICTING K-Block. Resolve conflicts first."

    if check.state == "ENTANGLED":
        return False, "Cannot commit ENTANGLED K-Block individually."

    return True, "OK to commit"
```

### Periodic Health Check

```python
async def health_check_kblocks():
    """Periodic verification of all K-Blocks."""
    harness = get_harness()
    store = await get_sovereign_store()

    checks = await verify_all_kblocks(harness.list_blocks(), store)

    stats = {
        "total": len(checks),
        "violations": sum(1 for c in checks if not c.is_isolated),
        "stale": sum(1 for c in checks if c.state == "STALE"),
        "conflicting": sum(1 for c in checks if c.state == "CONFLICTING"),
    }

    return stats
```

## Teaching Notes

### Gotcha: Isolation is Runtime, Not Static

K-Block state can change when:
1. Another K-Block commits to the same path → STALE
2. `set_content()` modifies content → DIRTY
3. Multiple K-Blocks created for same path → conflict potential

Run verification at key points:
- Before save (ensure valid state)
- After save (verify dependents marked STALE)
- Periodically (detect stale K-Blocks)

### Gotcha: Multiple Editors ≠ Violation

Having multiple K-Blocks on the same path is NOT a violation of Theorem 3.

Theorem 3 guarantees that edits in K-Block b₁ don't affect K-Block b₂ until commit.
When b₁ commits, b₂ **should** transition to STALE. This is correct behavior.

### Gotcha: CONFLICTING Requires Manual Resolution

`harness.save()` will reject CONFLICTING K-Blocks. User must:

1. **Rebase**: Discard local changes, refresh from sovereign
2. **Force Save**: Override upstream changes (data loss risk)
3. **Manual Merge**: Combine both changesets

There's no automatic merge for K-Block conflicts.

## See Also

- `spec/protocols/sovereign-data-guarantees.md` - Theorem 3 formal proof
- `spec/protocols/k-block.md` - K-Block specification
- `services/k_block/core/kblock.py` - K-Block implementation
- `services/sovereign/store.py` - Sovereign store (source of truth)
