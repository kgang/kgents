# Inbound Sovereignty — Multi-Session Implementation Plan

> *"We don't reference. We possess."*

**Source Spec**: `spec/protocols/inbound-sovereignty.md`
**Decision**: `fuse-dc6a2453` (2025-12-22)
**Status**: SESSION 1+2 COMPLETE

---

## Progress Tracker

| Session | Status | Tests | Notes |
|---------|--------|-------|-------|
| S1: Sovereign Store | ✅ COMPLETE | 43 | types, store, versions, overlay |
| S2: Ingest Protocol | ✅ COMPLETE | 27 | edge extraction, witness marks |
| S3: Sync Protocol | PENDING | — | — |
| S4: Bootstrap | PENDING | — | — |
| S5: Export + AGENTESE | PENDING | — | — |
| S6: WitnessedGraph | PENDING | — | — |
| S7: Integration | PENDING | — | — |

**Mark**: `mark-e34` — Session 1+2 complete, 70 tests passing

---

## 🎯 GROUNDING IN KENT'S INTENT

*"The Mirror Test: Does K-gent feel like me on my best day?"*
*"Tasteful > feature-complete; Joy-inducing > merely functional"*
*"The proof IS the decision. The mark IS the witness."*

---

## The Problem (Crystal Clear)

**Current pain**: Every time kgents starts, it scans 4000+ files. Results evaporate. External changes break us. Data "escapes" without witnessing.

**The insight**: Hot analysis is violence. We should possess, not reference.

---

## Existing Infrastructure to Leverage

| Component | Location | What We Use |
|-----------|----------|-------------|
| **Mark** | `services/witness/mark.py` | Immutable witness primitives (Law 1-3) |
| **WitnessPersistence** | `services/witness/persistence.py` | Dual-track storage (SQL + D-gent) |
| **SpecParser** | `protocols/specgraph/parser.py` | Edge discovery from markdown |
| **D-gent** | `agents/d/` | Content-addressable storage |
| **TableAdapter** | `agents/d/` | SQL table abstraction |

---

## Session Plan

### Session 1: Sovereign Store Foundation (3-4 hours)
**Goal**: Core data structures and storage primitives

#### Deliverables:
1. **`impl/claude/services/sovereign/`** — New Crown Jewel service directory
2. **`sovereign/types.py`** — Core types:
   - `IngestEvent`: Document crossing the membrane
   - `SovereignEntity`: Versioned copy with overlay
   - `SyncResult`: Sync operation result
   - `Diff`: Comparison result
3. **`sovereign/store.py`** — `SovereignStore` class:
   - `store_version()` → Store content, return version number
   - `get_current()` → Get latest version
   - `store_overlay()` → Store annotations/edges in overlay
   - `get_overlay()` → Get overlay data
   - `list_all()` → List all sovereign entities
   - `diff_with_source()` → Compare with external content
4. **`sovereign/_tests/test_store.py`** — 20+ tests

#### Storage Layout:
```
.kgents/sovereign/
├── spec/
│   └── protocols/
│       └── k-block.md/
│           ├── v1/
│           │   ├── content.md
│           │   └── meta.json
│           ├── current -> v1/
│           └── overlay/
└── impl/
    └── claude/
        └── services/
            └── witness/
                └── crystal.py/
```

#### Key Decisions:
- File-based storage (`.kgents/sovereign/`) for visibility + git compatibility
- Symlinks for `current` version → easy to see what's active
- Versioned directories (`v1/`, `v2/`) → full history
- Overlay separate from content → our modifications don't touch original

---

### Session 2: Ingest Protocol (3-4 hours)
**Goal**: Document ingestion with witness marks

#### Deliverables:
1. **`sovereign/ingest.py`** — Core ingest logic:
   - `ingest()` → Main entry point (witness + copy + extract + store)
   - `extract_edges()` → Use SpecParser for markdown, AST for Python
   - `_create_birth_mark()` → Witness the arrival
   - `_create_edge_marks()` → Witness each discovered edge
2. **`sovereign/persistence.py`** — SQL models + persistence
3. **`sovereign/_tests/test_ingest.py`** — 25+ tests

#### The Ingest Flow:
```python
async def ingest(event: IngestEvent) -> IngestedEntity:
    # 1. Create birth certificate (Mark)
    birth_mark = await witness.mark(
        action="entity.ingest",
        target=event.claimed_path,
        evidence={...},
    )

    # 2. Store sovereign copy
    version = await sovereign.store_version(...)

    # 3. Extract edges AT INGEST TIME
    edges = extract_edges(event.content, event.claimed_path)

    # 4. Store edges as witness marks
    edge_marks = await _create_edge_marks(edges, parent=birth_mark.id)

    # 5. Store derived data in overlay
    await sovereign.store_overlay(path, "edges", {"edges": [...]})

    return IngestedEntity(...)
```

#### Laws Enforced:
- Law 0: No Entity Without Copy
- Law 1: No Entity Without Witness
- Law 2: No Edge Without Witness

---

### Session 3: Sync Protocol (2-3 hours)
**Goal**: Receive-only sync with change detection

#### Deliverables:
1. **`sovereign/sync.py`** — Sync logic:
   - `sync_inbound()` → Receive notification, decide accept/reject
   - `should_accept()` → Policy-based decision
   - `GitSyncProvider` — Watch git for changes
2. **`sovereign/watcher.py`** — File system watcher (optional, for daemon mode)
3. **`sovereign/_tests/test_sync.py`** — 15+ tests

#### The Sync Philosophy:
```python
# We don't poll. We receive.
async def sync_inbound(notification: ChangeNotification) -> SyncResult:
    # 1. Witness the notification (even if we reject)
    mark = await witness.mark(
        action="sync.notification_received",
        target=notification.path,
        evidence={...},
    )

    # 2. Decide: accept or reject?
    if should_accept(notification):
        # Re-ingest (creates new witness trail)
        return await ingest(...)
    else:
        # Witness the rejection
        await witness.mark(action="sync.rejected", parent=mark.id)
        return SyncResult.REJECTED
```

---

### Session 4: Bootstrap Migration (3-4 hours)
**Goal**: One-time ingestion of existing codebase

#### Deliverables:
1. **`sovereign/bootstrap.py`** — One-time migration:
   - `bootstrap_from_filesystem()` → Convert existing files
   - `install_file_watchers()` → Set up for ongoing sync
   - Progress reporting (this will take a while for 4000+ files)
2. **CLI command**: `kg sovereign bootstrap [--path spec/] [--dry-run]`
3. **`sovereign/_tests/test_bootstrap.py`** — Integration tests

#### Bootstrap UX:
```bash
# Dry run first
kg sovereign bootstrap --dry-run
# → Would ingest 4,127 files
# → Estimated edges: 12,340
# → Estimated time: 8 minutes

# Actually run
kg sovereign bootstrap
# → Ingesting... [████████████████████░░░░] 80%
# → 3,301/4,127 files
# → 9,876 edges discovered
```

---

### Session 5: Export Protocol + AGENTESE Integration (3-4 hours)
**Goal**: Explicit export and AGENTESE node registration

#### Deliverables:
1. **`sovereign/export.py`** — Export logic:
   - `export()` → Explicit export with witness mark
   - `ExportPolicy` — Pre-authorized export rules
   - `ExportReceipt` — Proof of export
2. **`sovereign/node.py`** — AGENTESE node:
   - `@node("concept.sovereign")` registration
   - `ingest` aspect → Ingest a document
   - `query` aspect → Query sovereign copy
   - `sync` aspect → Trigger sync
   - `export` aspect → Export with consent
3. **`sovereign/_tests/test_export.py`** — 15+ tests

#### Export Philosophy:
```python
# Nothing leaves without consent
async def export(
    path: str,
    destination: str,
    reason: str,
    authorized_by: str,
) -> ExportReceipt:
    # 1. Witness the export decision
    mark = await witness.mark(
        action="entity.export",
        target=path,
        evidence={"destination": destination, "reason": reason, ...},
    )

    # 2. Perform the export
    await send_to_destination(entity.content, destination)

    # 3. Return receipt
    return ExportReceipt(mark_id=mark.id, ...)
```

---

### Session 6: WitnessedGraph + SpecGraph Migration (4-5 hours)
**Goal**: Replace hot scanning with witness trail queries

#### Deliverables:
1. **`sovereign/graph.py`** — `WitnessedGraph` class:
   - `get_edges()` → Query witness marks, not file scan
   - `get_all_edges()` → Fast DB query
   - `get_entity()` → Entity with full provenance
2. **Update `protocols/specgraph/`** to use WitnessedGraph
3. **Performance test**: Prove <100ms for all-edge query
4. **`sovereign/_tests/test_graph.py`** — 20+ tests

#### The Key Insight:
```python
# OLD (never again)
edges = scan_filesystem_for_edges()  # 4000 files, 30 seconds

# NEW (instant)
edges = await witnessed_graph.get_all_edges()  # DB query, 10ms
```

---

### Session 7: Membrane Integration + Polish (3-4 hours)
**Goal**: Wire into existing UX, CLI commands, tests

#### Deliverables:
1. **CLI commands**:
   - `kg sovereign status` → Show sovereign store stats
   - `kg sovereign ingest <path>` → Manual ingest
   - `kg sovereign diff <path>` → Compare with source
   - `kg sovereign export <path> <destination>` → Explicit export
2. **Membrane integration**: FocusPane can show sovereign entity with overlay
3. **K-Block integration**: K-Block commit triggers sovereign ingest
4. **Final integration tests**: 40+ tests

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Bootstrap time (4K files) | < 10 minutes |
| All-edges query | < 100ms |
| Ingest single file | < 50ms |
| Test coverage | > 90% |
| Laws verified | All 5 |

---

## Laws Verification

Each session should verify applicable laws:

| Law | Description | Session |
|-----|-------------|---------|
| Law 0 | No Entity Without Copy | S1-S4 |
| Law 1 | No Entity Without Witness | S2-S4 |
| Law 2 | No Edge Without Witness | S2 |
| Law 3 | No Export Without Witness | S5 |
| Law 4 | Sync is Ingest | S3 |

---

## Risk Mitigation

1. **4000+ files ingestion**: Session 4 includes dry-run + progress. If too slow, batch async.
2. **Edge extraction accuracy**: Session 2 uses proven SpecParser + extends for Python AST.
3. **Storage growth**: Versioned copies could grow large. Consider compaction strategy (future work).
4. **Git integration complexity**: Session 3 can be simple (polling) initially, hooks later.

---

## Dependencies

- Session 2 depends on Session 1 (types + store)
- Session 3 depends on Session 2 (ingest flow)
- Session 4 depends on Session 2, 3 (full ingest + sync)
- Session 5 depends on Session 2 (ingest types)
- Session 6 depends on Session 2, 4 (ingested data exists)
- Session 7 depends on all (integration)

**Critical Path**: S1 → S2 → S4 → S6 (can parallelize S3, S5 after S2)

---

## Estimated Total

**7 sessions × ~3.5 hours average = ~24 hours of focused work**

Could compress to 5 sessions if willing to have longer sessions and less polish.

---

*"The file is a lie. There is only the witnessed entity."*

---

*Filed: 2025-12-22*
*Ready for Session 1*
