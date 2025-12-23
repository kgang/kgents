# Living Spec Ledger — Continuation Prompt

> **For**: Next Claude session
> **From**: Session 2025-12-22
> **Status**: Phase 2 (Evidence-as-Marks) implemented, UI update pending

---

## Ground Truth

Run `/hydrate` first to load full context, then read this file.

```bash
# Verify current state
cd impl/claude && uv run pytest services/living_spec/_tests/ -q  # 28 tests
cd impl/claude/web && npm run typecheck  # Should be clean
```

---

## The Accounting Metaphor (CRITICAL)

Kent established this framing — **do not deviate**:

```
Specs = Assets          → Claims that can accrue evidence
Evidence = Transactions → Implementations, tests, usage that prove specs
Contradictions = Liabilities → Conflicts that drain value
Harmonies = Compound Interest → Reinforcements that multiply value
Orphans = Dead Weight   → Specs with no evidence, candidates for deprecation
```

**Key Quote**: *"Upload spec → Parse → Accumulate evidence → Brilliant executions. If proofs valid, supported. If not used, dead."*

---

## What's Done (Phase 1)

### Backend (`impl/claude/services/living_spec/`)

| File | Purpose |
|------|---------|
| `analyzer.py` | Corpus scanner — extracts claims, finds evidence, identifies relationships |
| `ledger_node.py` | AGENTESE node — `self.spec.scan`, `ledger`, `get`, `orphans`, `contradictions`, `harmonies`, `deprecate`, `evidence_add` |
| `contracts.py` | Type contracts for spec records, claims, evidence |
| `monad.py` | SpecM monad for compositional operations |
| `polynomial.py` | PolyAgent state machine for spec lifecycle |
| `sheaf.py` | Sheaf coherence for cross-spec consistency |
| `tokens/` | Spec token types (portals, principles, etc.) |

### REST API (`impl/claude/protocols/api/spec_ledger.py`)

```
POST /api/spec/scan           → Scan corpus
GET  /api/spec/ledger         → Get ledger summary + specs
GET  /api/spec/detail?path=   → Single spec detail
GET  /api/spec/orphans        → List orphan specs
GET  /api/spec/contradictions → List conflicts
GET  /api/spec/harmonies      → List reinforcements
POST /api/spec/deprecate      → Mark specs deprecated
POST /api/spec/evidence/add   → Link evidence to spec (NEW)
```

### Witness Integration (`impl/claude/services/witness/bus.py`)

Added topics:
- `SPEC_SCANNED` — Corpus scan completed
- `SPEC_DEPRECATED` — Spec marked deprecated
- `SPEC_EVIDENCE_ADDED` — Evidence linked (transaction)
- `SPEC_CONTRADICTION_FOUND` — Conflict detected
- `SPEC_ORPHAN_DETECTED` — Orphan identified

### Frontend (`impl/claude/web/src/`)

| Component | Location |
|-----------|----------|
| API client | `api/specLedger.ts` |
| State hook | `membrane/useLivingSpec.ts` |
| Dashboard | `membrane/views/LedgerDashboard.tsx` |
| Table | `membrane/views/SpecTable.tsx` |
| Detail | `membrane/views/SpecLedgerDetail.tsx` |
| Page | `pages/SpecLedgerPage.tsx` |

### Current Metrics

```
Total specs:      198
Active:           164
Orphans:           80 (40%)
Deprecated:        23
Archived:          11
Total claims:     255
Contradictions:     0 (needs better detection)
Harmonies:        329
```

---

## What Was Done (Phase 2: Evidence-as-Marks)

**Radical transformation**: Evidence is no longer a separate concept. **Evidence IS witness marks with specific tags.**

### 1. Unified Evidence Model (COMPLETE)

Instead of a separate `spec_evidence` table, evidence uses the existing witness mark system:

```python
# Evidence = Marks with evidence tags
tags = [
    "spec:principles.md",      # Which spec this is evidence for
    "evidence:impl",           # Type: impl, test, usage
    "file:path/to/impl.py",    # The evidence file
]
```

See: `spec/protocols/living-spec-evidence.md`

### 2. Backend Implementation (COMPLETE)

**Added to `WitnessMark` model** (`models/witness.py`):
- `tags` column (JSON array with GIN index)
- Evidence tag taxonomy in docstring

**Added to `WitnessPersistence`** (`services/witness/persistence.py`):
- `get_evidence_for_spec(spec_path, evidence_type)` — Query evidence by spec
- `get_specs_with_evidence()` — All specs with evidence
- `count_evidence_by_spec()` — Counts by spec and type
- `save_mark(... tags=...)` — Store tags with marks

**Added to `LedgerNode`** (`services/living_spec/ledger_node.py`):
- `evidence_add()` now creates a witness mark (not just event)
- `evidence_query()` — Query evidence from witness marks
- `evidence_verify()` — Check if evidence files exist
- `evidence_summary()` — Counts across all specs

### 3. What Remains (UI Only)

Add to `SpecLedgerDetail.tsx`:
- "Add Evidence" modal with file picker
- "Verify Evidence" button that runs checks
- Evidence status indicators (valid/stale/broken)
- Show evidence marks in detail view

---

## Phase 3: Contradiction Detection

Current state: 0 contradictions detected (too naive).

### Improvement Approach

1. **Claim Extraction Enhancement**
   - Parse markdown more deeply (not just headers)
   - Extract assertions from bullet points
   - Identify constraints vs definitions

2. **Semantic Similarity**
   - Use embeddings to find similar claims across specs
   - Flag claims that are similar but not identical (tension)

3. **Explicit Contradiction Rules**
   ```python
   # Example rules
   CONTRADICTION_PATTERNS = [
       # Same subject, different predicates
       (r"(\w+) should (\w+)", r"\1 should not \2"),
       # Conflicting numbers
       (r"max (\d+)", r"min (\d+)"),  # if min > max
   ]
   ```

---

## Key Patterns to Follow

### 1. Symmetric Harness

Every UI action must map to an AGENTESE call that agents can also use:

```typescript
// UI button click
onClick={() => addEvidence(specPath, evidencePath, 'implementation')}

// Same call an agent would make
await logos.invoke("self.spec.evidence.add", observer, {
  spec_path: specPath,
  evidence_path: evidencePath,
  evidence_type: "implementation"
})
```

### 2. Witness Everything

Mutations emit witness events:

```python
async def some_mutation(self, ...) -> dict[str, Any]:
    # ... do the thing ...

    # Emit witness event
    _, topics = _get_witness_bus()
    if topics:
        await _emit_witness_event(topics.SPEC_SOMETHING, {
            "action": "something",
            "details": ...,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
```

### 3. Categorical Foundations

Living Spec follows the standard kgents pattern:

```
PolyAgent → Operad → Sheaf
   ↓          ↓        ↓
State      Grammar   Coherence
machine    of ops    across views
```

See `polynomial.py`, `sheaf.py` for implementations.

---

## Gotchas

1. **Analyzer runs in thread pool** — `ensure_scanned()` uses `run_in_executor` to not block async. Don't add async calls inside `analyze_spec_corpus()`.

2. **Cache has 5-minute TTL** — `LedgerCache.is_fresh()` returns cached data if < 5 min old. Use `scan(force=True)` to refresh.

3. **Orphan detection is path-based** — A spec is an orphan if no other files reference its path. This misses semantic references.

4. **WitnessBus is optional** — `_get_witness_bus()` returns `(None, None)` if not available. Always check before emitting.

5. **TypeScript types need manual sync** — `api/specLedger.ts` types must match `protocols/api/spec_ledger.py` Pydantic models.

---

## Files to Read First

```
spec/protocols/living-spec-ui-strategy.md  — Full UI strategy doc
impl/claude/services/living_spec/ledger_node.py  — Main AGENTESE node
impl/claude/services/living_spec/analyzer.py  — Corpus analysis logic
impl/claude/web/src/api/specLedger.ts  — Frontend API client
```

---

## Verification Commands

```bash
# Backend tests
cd impl/claude && uv run pytest services/living_spec/_tests/ -q

# Frontend compile
cd impl/claude/web && npm run typecheck

# Test evidence endpoint
curl -X POST http://localhost:8000/api/spec/evidence/add \
  -H "Content-Type: application/json" \
  -d '{"spec_path": "k-block.md", "evidence_path": "services/k_block/core/kblock.py", "evidence_type": "implementation"}'

# Test scan endpoint
curl -X POST http://localhost:8000/api/spec/scan \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

---

## Success Metrics (from strategy doc)

| Metric | Current | Target |
|--------|---------|--------|
| Orphan rate | 40% | < 20% |
| Contradiction count | 0 | 0 hard, < 10 soft |
| Evidence coverage | ~30% | > 80% |
| Agent action parity | ~80% | 100% |

---

## The North Star

*"The proof IS the decision. The mark IS the witness."*

Every spec should be:
1. **Proven** by evidence (implementations, tests)
2. **Witnessed** by the system (transactions recorded)
3. **Accountable** (orphans triaged, contradictions resolved)

---

**Filed**: 2025-12-22
**Next Session**: Phase 2 — Evidence Tracking
