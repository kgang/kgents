# Session 3: Teaching Crystal Extinction

> Continuation prompt for Memory-First Documentation Phase 3

---

## Context

**Session 2 Complete**: Teaching crystallization now works. Gotchas extracted from docstrings can be persisted to Brain as `TeachingCrystal` records with full provenance.

**The Problem**: When code is deleted, teaching crystals currently remain "alive" even though their source is gone. We need to mark them as **extinct** (set `died_at`) while preserving the wisdom.

---

## Session 3 Objectives

1. **`record_extinction()`** in `BrainPersistence`
   - Create `ExtinctionEvent` with reason, commit, deleted_paths
   - Mark affected TeachingCrystals as extinct (set `died_at`)
   - Link via `ExtinctionTeaching` join table
   - Optionally record successor mappings

2. **Detect affected teaching**
   - Given deleted paths, find teaching crystals by `source_module`
   - Pattern matching: `services/town/` → `services.town.*`

3. **Extinction CLI** (`kg docs extinct`)
   - `--commit <sha>` for the deletion commit
   - `--reason <text>` for documentation
   - `--dry-run` to preview

4. **Tests** for extinction workflow

---

## Key Files

| File | Purpose |
|------|---------|
| `impl/claude/models/brain.py` | `TeachingCrystal`, `ExtinctionEvent`, `ExtinctionTeaching` models (Session 1) |
| `impl/claude/services/brain/persistence.py` | Add `record_extinction()` method |
| `impl/claude/services/living_docs/crystallizer.py` | May need `mark_extinct()` wrapper |
| `protocols/cli/handlers/docs.py` | Add `_handle_extinct()` |
| `spec/protocols/memory-first-docs.md` | Reference spec |

---

## Key Insights from Session 2

```python
# Deterministic ID pattern for deduplication
insight_hash = hashlib.sha256(insight.encode()).hexdigest()[:12]
teaching_id = f"teach-{module.replace('.', '-')}-{symbol.replace('.', '-')}-{insight_hash}"

# Query patterns already exist
await brain.get_teaching_by_module("services.town")  # Returns all town teaching
await brain.get_ancestral_wisdom()  # Returns extinct teaching

# Container resolution is async
resolved_brain = await container.resolve("brain_persistence")
```

---

## Proposed `record_extinction()` Signature

```python
async def record_extinction(
    self,
    reason: str,
    commit: str,
    deleted_paths: list[str],
    decision_doc: str | None = None,
    successor_map: dict[str, str | None] | None = None,
) -> ExtinctionResult:
    """
    Record a code extinction event.

    The Extinction Law: Teaching from deleted code marked died_at, NOT deleted.

    Args:
        reason: Why the code was deleted
        commit: Git commit SHA
        deleted_paths: List of deleted paths (e.g., ["services/town/"])
        decision_doc: Optional link to decision document
        successor_map: Optional {old_module: new_module} mapping

    Returns:
        ExtinctionResult with counts and affected teaching IDs
    """
```

---

## Exit Criteria

| Criterion | Requirement |
|-----------|-------------|
| `record_extinction()` works | ✅ Creates ExtinctionEvent, marks teaching extinct |
| Join table populated | ✅ ExtinctionTeaching links event to crystals |
| CLI command | ✅ `kg docs extinct` with dry-run |
| Tests pass | ✅ Extinction workflow covered |
| mypy passes | ✅ |

---

## Usage Example

```bash
# Preview what would be marked extinct
kg docs extinct --commit abc123 --reason "Crown Jewel Cleanup AD-009" \
    --path services/town/ --path services/park/ --dry-run

# Actually record extinction
kg docs extinct --commit abc123 --reason "Crown Jewel Cleanup AD-009" \
    --path services/town/ --path services/park/
```

---

*Session 2 completed 2025-12-21. Ready for Session 3.*
