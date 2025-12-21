Execute Phase 4: Lemma Database

## Summary: Phase 3 Complete 🎉

Phase 3: LLM Proof Search is now complete.

### What Was Built

**Files Created:**
- `impl/claude/services/ashc/search.py` — ProofSearcher with:
  - `search(obligation)` → Quick (10) → Medium (50) → Deep (200) phases
  - Failed tactics tracking (stigmergic anti-pheromone)
  - Heritage hints (polynomial, composition, identity patterns)
- `impl/claude/services/ashc/_tests/test_search.py` — 39 new tests

**Test Results:** 128 passed, 10 skipped (Dafny integration)

### Exit Criteria ✅
- [x] LLM prompt generation is deterministic
- [x] Budget management respects phase limits
- [x] Failed tactics inform future attempts
- [x] Proof extraction handles various LLM output formats
- [x] Temperature is configurable via ProofSearchConfig

---

## Next: Phase 4 — Lemma Database

> *"Agents leave proofs as traces. Future agents follow the proven paths."*

### Relevant Files

**Read these first:**
- `plans/proof-generation-implementation.md` — Phase 4 spec (lines 1021-1216)
- `impl/claude/services/ashc/search.py` — LemmaDatabase protocol to implement
- `impl/claude/services/ashc/contracts.py` — VerifiedLemma contract

**Reference for D-gent persistence:**
- `spec/agents/d-gent.md` — StorageProvider patterns
- `impl/claude/agents/d/persistence.py` — Existing D-gent implementation

### Stigmergic Design (from Spec)

The lemma database is a **stigmergic surface** (§13):
- **Pheromone = usage_count**: More-used lemmas rank higher
- **Decay = relevance scoring**: Old unused lemmas fade
- **Reinforcement = composition**: Lemmas built on other lemmas strengthen the base

### Deliverables for Phase 4

Create `impl/claude/services/ashc/lemma_db.py` with:

1. **LemmaDatabase** class (replaces InMemoryLemmaDatabase):
   - SQLite persistence via D-gent StorageProvider
   - `add(lemma: VerifiedLemma)` — store with embedding placeholder
   - `get(id: LemmaId)` — retrieve by ID
   - `find_related(property, limit)` — stigmergic ranking
   - `record_usage(id)` — increment usage count
   - `dependency_graph()` — return lemma dependency DAG

2. **Schema** (two tables):
   - `lemmas`: id, statement, proof, checker, obligation_id, usage_count, verified_at, embedding
   - `lemma_dependencies`: lemma_id, depends_on

3. **SynergyBus Integration**:
   - `wire_lemma_events(bus, lemma_db)` — cross-service sharing
   - Emit `lemma.available` when new lemma verified

### Exit Criteria (Phase 4)

- [ ] Lemma persistence survives process restart
- [ ] Stigmergic ranking (usage × recency) works correctly
- [ ] Dependency graph is queryable
- [ ] SynergyBus integration allows cross-service lemma sharing

### Design Decision

| Question | Answer |
|----------|--------|
| SQLite vs Postgres? | **SQLite** for now (local-first, simpler) |
| Embeddings now or later? | **Later** — placeholder column, keyword matching first |
| Async or sync DB? | **Async** — aiosqlite for consistency with codebase |
