# Living Spec UI Strategy (Revised)

> *"Upload spec → Parse → Accumulate evidence → Brilliant executions"*
> *"If proofs valid, supported. If not used, dead."*

---

## Core Philosophy

The Living Spec UI is an **accounting ledger for specifications**:

1. **Spec = Asset** — Claims that can accrue evidence
2. **Evidence = Transactions** — Implementations, tests, usage that prove specs
3. **Contradictions = Liabilities** — Conflicts that drain value
4. **Harmonies = Compound Interest** — Reinforcements that multiply value
5. **Orphans = Dead Weight** — Specs with no evidence, candidates for deprecation

**Symmetric Harness**: The UI is the same interface agents use. Every Kent action is an AGENTESE call. Agents make identical calls.

```
LIVING SPEC UI = LEDGER × EVIDENCE × PROOF × SYMMETRIC_HARNESS
```

---

## Bootstrap Results (Current State)

```
Total specs:      198
Active:           165
Orphans:           86  ← 43% have NO evidence
Deprecated:        22
Archived:          11
Total claims:     255
Contradictions:     0  ← Need better detection
Harmonies:        313
```

**Key Finding**: 43% of specs are orphans. Either they need evidence or deprecation.

---

## UI Architecture

### Screen 1: Ledger Dashboard

The landing page shows the health of the spec corpus:

```
┌─────────────────────────────────────────────────────────────────┐
│  LIVING SPEC LEDGER                              [Scan Corpus]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── ASSETS ────────┐  ┌─── LIABILITIES ──────┐               │
│  │                   │  │                      │               │
│  │  198 Total Specs  │  │  86 Orphans          │               │
│  │  165 Active       │  │  22 Deprecated       │               │
│  │  255 Claims       │  │   0 Contradictions   │               │
│  │  313 Harmonies    │  │                      │               │
│  │                   │  │                      │               │
│  └───────────────────┘  └──────────────────────┘               │
│                                                                 │
│  ┌─── RECENT ACTIVITY ─────────────────────────────────────┐   │
│  │ 2m ago   spec/protocols/living-spec.md  +3 claims       │   │
│  │ 1h ago   spec/agents/d-gent.md          +1 impl         │   │
│  │ 3h ago   spec/services/witness.md       +2 tests        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 2: Spec Ledger (Table View)

Accounting-style table of all specs:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  SPEC LEDGER                                    Filter: [All ▼] [Search...] │
├──────────────────────────────────────────────────────────────────────────────┤
│  Path                          │ Status │ Claims │ Impl │ Tests │ Refs │    │
├────────────────────────────────┼────────┼────────┼──────┼───────┼──────┼────┤
│  spec/principles.md            │ ACTIVE │    28  │   3  │    0  │   12 │ ▶  │
│  spec/bootstrap.md             │ ACTIVE │    22  │   0  │    0  │    8 │ ▶  │
│  spec/protocols/k-block.md     │ ACTIVE │     3  │   2  │    3  │    5 │ ▶  │
│  spec/agents/d-gent.md         │ ORPHAN │     2  │   0  │    0  │    0 │ ⚠  │
│  spec/protocols/portal-token.md│ ACTIVE │     5  │   3  │    3  │    2 │ ▶  │
│  ...                           │        │        │      │       │      │    │
├──────────────────────────────────────────────────────────────────────────────┤
│  [Upload Spec]  [Scan Corpus]  [Export CSV]  [Deprecate Selected]           │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Columns**:
- **Status**: ACTIVE (green), ORPHAN (yellow), DEPRECATED (gray), CONFLICTING (red)
- **Claims**: Assertions extracted from spec
- **Impl**: Implementation files that reference this spec
- **Tests**: Test files that validate this spec
- **Refs**: Other specs that reference this one

### Screen 3: Spec Detail (Single Spec View)

Drill into one spec:

```
┌─────────────────────────────────────────────────────────────────┐
│  spec/protocols/k-block.md                          [Edit] [⋮] │
├─────────────────────────────────────────────────────────────────┤
│  Status: ACTIVE    Claims: 3    Evidence: 5    Harmonies: 8    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── CLAIMS ──────────────────────────────────────────────┐   │
│  │ ▸ ASSERTION: K-Block should provide monadic isolation   │   │
│  │   Evidence: services/k_block/core/kblock.py ✓           │   │
│  │             _tests/test_kblock.py ✓                     │   │
│  │                                                         │   │
│  │ ▸ ASSERTION: Cosmos should be append-only               │   │
│  │   Evidence: services/k_block/core/cosmos.py ✓           │   │
│  │                                                         │   │
│  │ ▸ CONSTRAINT: K-Block must not lose data                │   │
│  │   Evidence: [NONE] ⚠ Add evidence...                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─── EVIDENCE ────────────────────────────────────────────┐   │
│  │ Implementation:                                         │   │
│  │   • services/k_block/core/kblock.py                     │   │
│  │   • services/k_block/core/cosmos.py                     │   │
│  │                                                         │   │
│  │ Tests:                                                  │   │
│  │   • _tests/test_kblock.py (12 tests, 100% pass)         │   │
│  │   • _tests/test_cosmos.py (8 tests, 100% pass)          │   │
│  │                                                         │   │
│  │ [+ Add Evidence]  [Run Tests]  [Validate Claims]        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─── HARMONIES ───────────────────────────────────────────┐   │
│  │ ← spec/protocols/witness.md (references)                │   │
│  │ → spec/protocols/living-spec.md (extends)               │   │
│  │ ← spec/services/brain.md (uses)                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─── CONTRADICTIONS ──────────────────────────────────────┐   │
│  │ [None detected]                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 4: Contradictions View

Focus on conflicts:

```
┌─────────────────────────────────────────────────────────────────┐
│  CONTRADICTIONS                                         [Scan] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── HARD CONFLICTS (0) ──────────────────────────────────┐   │
│  │ [None detected]                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─── SOFT TENSIONS (3) ───────────────────────────────────┐   │
│  │                                                         │   │
│  │ ⚡ spec/agents/composition.md vs spec/agents/operads.md │   │
│  │   "Agents compose freely" vs "Composition follows laws" │   │
│  │   [View Both]  [Resolve]  [Mark as OK]                  │   │
│  │                                                         │   │
│  │ ⚡ spec/protocols/cli.md vs spec/protocols/cli-v7.md    │   │
│  │   Multiple CLI specs - which is canonical?              │   │
│  │   [View Both]  [Deprecate One]  [Merge]                 │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Screen 5: Orphans Triage

Mass action for specs without evidence:

```
┌─────────────────────────────────────────────────────────────────┐
│  ORPHANS (86 specs)                        [Deprecate All] [⋮] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ☐ spec/a-gents/alethic.md             0 claims, 0 refs        │
│  ☐ spec/agents/README.md               0 claims, 0 refs        │
│  ☐ spec/b-gents/README.md              0 claims, 0 refs        │
│  ☐ spec/g-gents/grammar.md             2 claims, 0 refs        │
│  ☐ spec/i-gents/meaning-token.md       1 claims, 0 refs        │
│  ...                                                            │
│                                                                 │
│  Selected: 0                                                    │
│  [Add Evidence to Selected]  [Deprecate Selected]  [Delete]    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Symmetric Harness: Agent Actions = Kent Actions

Every UI action maps to an AGENTESE call:

| Kent Action | AGENTESE Call | Agent Can Do? |
|-------------|---------------|---------------|
| Upload spec | `self.spec.upload(path, content)` | ✓ |
| Scan corpus | `self.spec.scan()` | ✓ |
| View ledger | `self.spec.ledger()` | ✓ |
| Add evidence | `self.spec.evidence.add(spec, impl)` | ✓ |
| Run tests | `self.spec.proof.run(spec)` | ✓ |
| Deprecate spec | `self.spec.deprecate(path, reason)` | ✓ |
| Resolve conflict | `self.spec.resolve(spec_a, spec_b, resolution)` | ✓ |
| Find contradictions | `self.spec.contradictions()` | ✓ |
| Find harmonies | `self.spec.harmonies()` | ✓ |
| Find orphans | `self.spec.orphans()` | ✓ |

**Implementation**: Every button click calls the same AGENTESE endpoint an agent would use.

---

## Data Model

### SpecLedger (Postgres table)

```sql
CREATE TABLE spec_ledger (
    id UUID PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    title TEXT,
    status TEXT DEFAULT 'active',  -- active, orphan, deprecated, archived
    content_hash TEXT,
    claim_count INT DEFAULT 0,
    impl_count INT DEFAULT 0,
    test_count INT DEFAULT 0,
    ref_count INT DEFAULT 0,
    last_scanned TIMESTAMP,
    last_modified TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE spec_claims (
    id UUID PRIMARY KEY,
    spec_id UUID REFERENCES spec_ledger(id),
    claim_type TEXT,  -- assertion, constraint, definition
    subject TEXT,
    predicate TEXT,
    line_number INT,
    raw_text TEXT
);

CREATE TABLE spec_evidence (
    id UUID PRIMARY KEY,
    spec_id UUID REFERENCES spec_ledger(id),
    evidence_type TEXT,  -- implementation, test, usage
    path TEXT,
    last_verified TIMESTAMP,
    status TEXT  -- valid, stale, broken
);

CREATE TABLE spec_relations (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES spec_ledger(id),
    target_id UUID REFERENCES spec_ledger(id),
    relation_type TEXT,  -- references, extends, contradicts, harmonizes
    strength FLOAT
);
```

---

## Phase Plan (Revised)

### Phase 1: Ledger Core (Week 1)

1. **Backend**:
   - `/api/spec/scan` — Scan corpus, populate ledger
   - `/api/spec/ledger` — Return ledger data
   - `/api/spec/detail/{path}` — Single spec detail

2. **Frontend**:
   - `LedgerDashboard` — Summary stats
   - `SpecTable` — Sortable, filterable table
   - `SpecDetail` — Single spec view

3. **AGENTESE**:
   - `self.spec.scan()` — Trigger scan
   - `self.spec.ledger()` — Get ledger
   - `self.spec.get(path)` — Get one spec

### Phase 2: Evidence Tracking (Week 2)

1. **Backend**:
   - `/api/spec/evidence/add` — Link impl/test to spec
   - `/api/spec/evidence/verify` — Check if evidence still valid
   - `/api/spec/proof/run` — Run tests for spec

2. **Frontend**:
   - Evidence panel in `SpecDetail`
   - "Add Evidence" modal
   - Test runner integration

3. **AGENTESE**:
   - `self.spec.evidence.add(spec, path, type)`
   - `self.spec.evidence.verify(spec)`
   - `self.spec.proof.run(spec)`

### Phase 3: Contradiction Detection (Week 2)

1. **Backend**:
   - Improve claim extraction (NLP?)
   - Cross-reference claims for conflicts
   - Semantic similarity for soft tensions

2. **Frontend**:
   - `ContradictionsView` — List conflicts
   - Side-by-side diff for resolution
   - "Mark as OK" for false positives

3. **AGENTESE**:
   - `self.spec.contradictions()`
   - `self.spec.resolve(a, b, resolution)`

### Phase 4: Orphan Triage (Week 3)

1. **Backend**:
   - Batch deprecation API
   - Usage tracking (what specs are actually accessed?)

2. **Frontend**:
   - `OrphansView` — Mass action UI
   - Bulk select/deprecate/delete

3. **AGENTESE**:
   - `self.spec.orphans()`
   - `self.spec.deprecate(paths[], reason)`

### Phase 5: Agent Symmetry (Week 3)

1. Ensure every UI action has AGENTESE equivalent
2. Add agent identity to all mutations (who made this change?)
3. Permission model: what can agents do vs Kent?

### Phase 6: Execution Proofs (Week 4)

1. **Backend**:
   - Link specs to test results
   - Track proof validity over time
   - Alert on broken proofs

2. **Frontend**:
   - Proof status indicators
   - "Run All Proofs" button
   - Proof history timeline

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Instead |
|--------------|---------|---------|
| Document viewer | Specs aren't documents, they're claims | Ledger with evidence |
| Read-only UI | Can't accumulate evidence | Every view has actions |
| Kent-only actions | Breaks symmetric harness | Every action = AGENTESE |
| Ignore orphans | Dead weight accumulates | Surface and triage |
| Manual evidence | Doesn't scale | Auto-detect from codebase |

---

## Success Metrics

| Metric | Target | Why |
|--------|--------|-----|
| Orphan rate | < 20% | Specs should have evidence |
| Contradiction count | 0 hard, < 10 soft | Corpus should be coherent |
| Evidence coverage | > 80% | Claims should be proven |
| Proof pass rate | 100% | All proofs should be valid |
| Agent action parity | 100% | Symmetric harness complete |

---

## Can I Do Everything Through This UI?

**Yes**. The UI supports:

| Process | UI Action |
|---------|-----------|
| Scan all specs | [Scan Corpus] button |
| View contradictions | Contradictions screen |
| View harmonies | Spec detail → Harmonies panel |
| Add evidence | Spec detail → [+ Add Evidence] |
| Run proofs | Spec detail → [Run Tests] |
| Deprecate orphans | Orphans screen → bulk select |
| Resolve conflicts | Contradictions → [Resolve] |
| Upload new spec | [Upload Spec] button |
| Edit spec | Spec detail → [Edit] |
| Track agent actions | Activity log shows all mutations |

**And agents can do all of this** via the same AGENTESE endpoints.

---

*"Upload spec → Parse → Accumulate evidence → Brilliant executions"*
*"If proofs valid, supported. If not used, dead."*

**Filed**: 2025-12-22
**Status**: Strategy — ready for Phase 1 implementation
