# Memory-First Documentation Rollout

**Spec**: `spec/protocols/memory-first-docs.md`
**Status**: PHASE 1 COMPLETE
**Sessions**: 4-5 (estimated)

> *"Teaching moments don't die; they become ancestors."*

---

## Phase Overview

| Phase | Sessions | Deliverable | Dependency |
|-------|----------|-------------|------------|
| **1. Schema** | 1 | TeachingCrystal + ExtinctionEvent tables | None |
| **2. Crystallization** | 1 | Bootstrap current teaching → Brain | Phase 1 |
| **3. Extinction Protocol** | 1 | prepare_extinction() + record cleanup | Phase 2 |
| **4. Ghost Hydration** | 1-2 | hydrate_with_ghosts() + CLI | Phase 3 |

---

## Phase 1: Schema (Session 1)

**Goal**: Add Memory-First tables to Brain persistence.

### Tasks

1. **Add TeachingCrystal model** to `impl/claude/models/brain.py`:
   - Fields: id, insight, severity, evidence, source_module, source_symbol, source_commit, born_at, died_at, successor_module, successor_symbol, applies_to, crystal_id
   - Indexes: alive crystals, by module, by severity

2. **Add ExtinctionEvent model**:
   - Fields: id, reason, decision_doc, commit, deleted_paths, successor_map
   - Index: by creation date

3. **Add ExtinctionTeaching join table**:
   - Links extinction events to preserved teaching crystals

4. **Write tests** (~15):
   - Model validation
   - Index creation
   - Query patterns

### Exit Criteria

- [x] Models pass mypy
- [x] Tables created via SQLAlchemy
- [x] Basic CRUD operations tested (19 tests)
- [x] Schema documented in spec

**Session 1 Complete (2025-12-21)**:
- Added `TeachingCrystal`, `ExtinctionEvent`, `ExtinctionTeaching` to `models/brain.py`
- 19 tests covering CRUD, properties, queries, validation
- All brain tests (71) pass

---

## Phase 2: Crystallization (Session 2)

**Goal**: Persist existing teaching moments from Living Docs to Brain.

### Tasks

1. **Add crystallize_teaching() to BrainPersistence**:
   ```python
   async def crystallize_teaching(
       self,
       insight: str,
       severity: Literal["info", "warning", "critical"],
       evidence: str | None,
       source_module: str,
       source_symbol: str,
   ) -> TeachingCrystal:
       """Crystallize a teaching moment in Brain."""
   ```

2. **Create bootstrap script** `scripts/bootstrap_teaching_crystals.py`:
   - Iterate TeachingCollector.collect_all()
   - Crystallize each to Brain
   - Report statistics

3. **Wire to Living Docs extractor**:
   - On extraction, optionally crystallize to Brain
   - Add flag: `--crystallize` to `kg docs extract`

4. **Write tests** (~12):
   - Crystallization happy path
   - Duplicate detection
   - Bootstrap idempotency

### Exit Criteria

- [ ] All current teaching moments crystallized (~165)
- [ ] `kg docs extract --crystallize` works
- [ ] No duplicates on re-run
- [ ] Tests pass

---

## Phase 3: Extinction Protocol (Session 3)

**Goal**: Enable graceful deletion with wisdom preservation.

### Tasks

1. **Add prepare_extinction() to BrainPersistence**:
   ```python
   async def prepare_extinction(
       self,
       reason: str,
       decision_doc: str | None,
       commit: str,
       deleted_paths: list[str],
       successor_map: dict[str, str | None],
   ) -> ExtinctionEvent:
       """Prepare wisdom preservation before mass deletion."""
   ```

2. **Implement the Extinction Law**:
   - Find all teaching crystals with source_module in deleted_paths
   - Mark died_at = now()
   - Set successor_module from successor_map
   - Link to ExtinctionEvent

3. **Record 2025-12-21 Crown Jewel Cleanup retroactively**:
   ```python
   # Run once to capture the cleanup that just happened
   await brain.prepare_extinction(
       reason="Crown Jewel Cleanup - AD-009",
       decision_doc="plans/crown-jewel-cleanup.md",
       commit="<sha>",
       deleted_paths=[
           "services/town/", "services/park/", "services/gestalt/",
           "services/forge/", "services/chat/", "services/archaeology/",
           "services/coalition/", "services/muse/", "services/gardener/",
       ],
       successor_map={
           "town": None,  # Concept removed
           "park": None,  # Concept removed
           "gestalt": None,  # Concept removed
           "forge": None,  # Concept removed
           "chat": "brain.conversation",
           "archaeology": "living_docs.temporal",
           "coalition": None,
           "muse": None,
           "gardener": "ashc",
       },
   )
   ```

4. **Add CLI command**: `kg brain extinction prepare`

5. **Write tests** (~10):
   - Extinction event creation
   - Teaching crystal marking
   - Successor chain validation

### Exit Criteria

- [ ] Crown Jewel Cleanup recorded as ExtinctionEvent
- [ ] Teaching crystals from deleted code marked with died_at
- [ ] CLI command works
- [ ] Tests pass

---

## Phase 4: Ghost Hydration (Session 4-5)

**Goal**: Surface ancestral wisdom during hydration.

### Tasks

1. **Extend HydrationContext** with extinction awareness:
   ```python
   extinct_modules: list[str]
   ancestral_wisdom: list[TeachingCrystal]
   successor_map: dict[str, str]
   ```

2. **Add find_extinct_references() to BrainPersistence**:
   - Given keywords, check if any match extinct modules
   - Return ExtinctionEvents and their successor_maps

3. **Add load_ancestral_wisdom()**:
   - Given extinct modules, load their preserved TeachingCrystals
   - Filter by died_at IS NOT NULL

4. **Update Hydrator.hydrate_with_ghosts()**:
   - After normal hydration, check for extinct references
   - Load ancestral wisdom if found
   - Annotate context with successor mappings

5. **Update HydrationContext.to_markdown()** output:
   ```markdown
   ## Ancestral Wisdom (From Deleted Code)

   These modules no longer exist but their lessons persist:

   ### ⚰️ services.town.dialogue_service
   **Replaced by**: None (concept removed)

   - **DialogueService.process_turn**: Always validate turn order before...
   ```

6. **Add AGENTESE nodes**:
   - `void.extinct.list` → list extinction events
   - `void.extinct.wisdom(path)` → get ancestral teaching
   - `concept.docs.ancestors` → get all ancestral wisdom

7. **Write tests** (~15):
   - Ghost hydration with extinct modules
   - Successor mapping rendering
   - AGENTESE node registration

### Exit Criteria

- [ ] `kg docs hydrate "town dialogue"` surfaces ancestral wisdom
- [ ] AGENTESE nodes registered and functional
- [ ] Markdown output includes ghost section when relevant
- [ ] Tests pass

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Teaching crystals persisted | ~165 (current) + future |
| ExtinctionEvents recorded | 1 (Crown Jewel Cleanup) |
| Hydration shows ghosts when relevant | 100% |
| Tests added | ~52 total |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Schema migration complexity | Use clean slate approach (drop + recreate) |
| Bootstrap takes too long | Batch crystallization, show progress |
| Ghost hydration noise | Show only when task keywords match extinct modules |
| Successor chain cycles | DAG validation in prepare_extinction() |

---

## Notes

- **Clean slate OK**: No backwards compatibility required for DB
- **Teaching count**: Currently ~165 teaching moments extracted
- **Crown Jewel Cleanup**: Major extinction event that motivated this spec
- **Voice preservation**: This is a "Tasteful > feature-complete" implementation—simple first

---

*Plan created: 2025-12-21*
