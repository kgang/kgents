---
path: meta/forest-agentese
status: active
progress: 95
last_touched: 2025-12-14
touched_by: claude-opus-4-5
blocking: []
enables: [plans/_forest.md, plans/_status.md]
session_notes: |
  Week 3 IMPLEMENT (95%): Live wiring complete. ForestNode connected to real _forest.md parsing.
  - parse_forest_md() extracts Active/Dormant/Blocked/Complete trees from tables
  - manifest() returns real ForestManifest with tree counts and average progress
  - _sip() returns actual longest-dormant plan (string, not array)
  - Export registration in contexts/__init__.py (ForestNode, ParsedTree, parse_forest_md)
  - Test coverage: 20 tests in _tests/test_forest.py (all passing)
  - Affordance gating verified: guest/meta/ops roles work correctly
  - Rollback protocol verified: _refine() always returns rollback_token
  - Next: Week 4 (Witness + Epilogue Parsing) - implement _witness() to stream epilogues
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched  # reason: handle contracts + dry-run IO specs
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched  # reason: doc alignment to metrics/phase-accountability/meta-skill-operad
  IMPLEMENT: touched  # reason: ForestNode skeleton created (forest.py ~500 lines)
  QA: touched  # reason: mypy passes, header QA verified
  TEST: touched  # reason: 5 dry-run test cases documented
  EDUCATE: touched  # reason: handle usage snippets in agentese-path
  MEASURE: deferred  # reason: metrics spans deferred to impl phase
  REFLECT: touched
entropy:
  planned: 0.08
  spent: 0.06
  returned: 0.02
---

# Plan: Forest Meta-System (AGENTESE x N-Phase)

> *"To read is to invoke. The forest is a verb."*

**AGENTESE Context**: `concept.forest.*` (planning grammar), `self.forest.*` (maintenance agents), `time.forest.witness` (epilogues), `void.accursed-share.sip` (exploration rotation)  
**Principles**: Tasteful, Composable, Heterarchical, Accursed Share, Transparent Infrastructure  
**Cross-refs**: `spec/protocols/agentese.md`, `plans/principles.md`, `plans/skills/n-phase-cycle/*` (implementation hooks deferred)
**Entropy guard [phase=PLAN][entropy=0.07][minimal_output=true]:** Doc-only edits; sip from `void.entropy.sip` and pour unused at REFLECT; no auto-gen mutations.

---

## Scope & Exit (PLAN)
- **Goal**: Bind forest planning artifacts to AGENTESE handles with category-law guards and entropy accountability.  
- **Exit**: Scope + non-goals declared; observer gates (ops/meta/guest) stated; entropy band 0.05-0.10 logged per phase; Minimal Output promise noted.  
- **Non-goals**: No CLI/impl wiring, no new contexts, no array outputs, no live spans.  
- **Observer roles**: guest = manifest/witness (read-only); meta = manifest/refine/define (proposal); ops = apply/rollback, lint, promote. Law checks run on ops/meta mutation calls; guests never trigger mutation law checks.  
- **Attention budget**: 60/25/10/5 with 5% Accursed Share minimum (`void.entropy.sip[entropy=0.07]` at PLAN/RESEARCH; `void.entropy.pour` on REFLECT).

## Core Insight
The plan system itself is an agent: AGENTESE handles should surface plan manifests/traces and accept mutations as lawful morphisms. For this pass, all work stays inside `plans/` (skills, headers, prompts); wiring into the `kgents` codebase is deferred. Agent-to-agent coherence is prioritized over developer comfort (85/15 weighting); developer experience may be marginally worse if it simplifies agent messaging. The N-phase cycle governs self-renewal: PLAN->...->REFLECT with embedded lookbacks and process metrics.

---

## Current State (RESEARCH snapshot)
- Forest CLI (`kgents forest`) parses plan headers and renders `_forest.md`; AGENTESE path exposure is pending and **out of scope** for this cycle.
- N-phase skills exist but are not bound to planning artifacts; lookbacks happen ad hoc.
- Accursed Share rotation is implied (dormant plans) but not addressable as a first-class handle.
- Agent comms friction: humans rely on CLI; agents lack a clear, minimal manifest+affordance grammar for peer-to-peer invocation.
- Phase headers share `phase_ledger`/`entropy` keys but lack `[phase]/[law_check]/[entropy]` clauses and witness spans; `_forest.md` generation not instrumented with AGENTESE spans.

## N-Phase Continuation Orders (doc-only; forest spans)
- **PLAN**: `concept.forest.manifest[phase=PLAN][minimal_output=true]@span=forest_plan` → declare scope, non-goals, observer roles; draw `void.entropy.sip[entropy=0.07]`.  
- **RESEARCH**: `concept.forest.manifest[phase=RESEARCH]` to map headers/ledgers + deviations; sample epilogues via `time.forest.witness@span=forest_trace`.  
- **DEVELOP**: `concept.forest.refine[phase=DEVELOP][rollback=true][law_check=true]@span=forest_dev` → draft handle/IO/law notes; enforce Minimal Output; persist rollback token.  
- **STRATEGIZE**: Order rollout docs → skills → dry-run adapters; set observer gating matrix; budget entropy return.  
- **CROSS-SYNERGIZE**: Align with `process-metrics.md`, `phase-accountability.md`, `meta-skill-operad.md`; declare Accursed Share rotation `void.forest.sip`.  
- **IMPLEMENT**: Doc-only edits in `plans/skills/agentese-path.md` and n-phase skills/meta plan; no CLI/impl code.  
- **QA**: Headers ≤100 lines; `phase_ledger` + `entropy` present; clauses carry `[phase]`, `[entropy]`, `[law_check]`, `[rollback]`, `[minimal_output]`.  
- **TEST**: Dry-run = single renderable per handle, witness ordering stable, `concept.forest.refine` emits rollback token.  
- **EDUCATE**: Usage snippets + clause patterns live in skills/meta (agentese-path appendix, n-phase cycle quick-cards).  
- **MEASURE**: Desired spans `{phase,tokens_in/out,duration_ms,entropy,law_checks}` recorded (attachment deferred).  
- **REFLECT**: Log learnings/risks; `void.entropy.pour` unused; tithe if overdrawn.  

## Auto-Generation Contract (DEVELOP)
- **Source of truth**: `impl/claude/protocols/cli/handlers/forest.py#generate_forest_md` (invoked via `kgents forest update`). `_forest.md` remains fully auto-generated; no manual edits permitted.
- **Header ingestion**: Parser already reads YAML frontmatter; require `phase_ledger` + `entropy` keys per `phase-accountability.md` snippet to unblock ledger-aware metrics and keep plan reconciliation mechanical.
- **Branch/owner**: Doc-only changes stay on `main`; CLI work, if needed later, lands on branch `forest-autogen-contract` owned by `ops/meta` (current driver: gpt-5-codex).
- **Instrumentation hook (deferred)**: When ready to emit process metrics, wrap `generate_forest_md` with span `{phase: "FOREST", tokens_in/out, duration_ms, entropy, law_checks}` and record ledger presence as law check; no emission in this pass.

---

## N-Phase Reformation (OPERAD morphisms)
- **PLAN/RESEARCH**: Capture AGENTESE handles and affordances as **plan-only** grammar (`concept.forest.manifest`, `concept.forest.affordances`).  
- **DEVELOP**: Define handles as documented contracts (no code binding):  
  - `concept.forest.manifest` (read canopy + gaps from headers)  
  - `time.forest.witness` (epilogue stream contract)  
  - `concept.forest.refine` (propose mutations: add/refine/prune/fuse per `meta-skill-operad.md`)  
  - `void.forest.sip` (select dormant plan for Accursed Share)  
  - `self.forest.define` (JIT plan scaffold template)  
- **STRATEGIZE**: Stage rollout inside `plans/`: add prompts/skills and note future adapter hooks; leave `impl/` untouched.  
- **CROSS-SYNERGIZE**: Describe how forest handles compose with `re-metabolize` and process metrics; simplify to single-message morphisms (per Composable/Minimal Output) so agents can pass handles without aggregations; mark execution as deferred.  
- **IMPLEMENT**: Produce doc stubs (skills, quickstart, epilogue stream recipe) without modifying CLI or adapters; prefer agent-legible defaults over human niceties.  
- **QA/TEST**: Rely on lintable headers and self-consistency checks inside `plans/`; note pending law-check hooks for future code.  
- **EDUCATE**: README/skill snippets: how to call forest handles conceptually and where code hooks will land later.  
- **MEASURE**: Document desired spans/metrics schema for future wiring; do not emit yet.  
- **REFLECT/RE-METABOLIZE**: Monthly `lookback-revision` on forest metrics (documented); future automation deferred.

---

## Chunks (parallelizable)
- **C1: Handle Spec** (concept): Formalize Agentese handles + affordances + return types. Exit: draft in `plans/skills/agentese-path.md` appendix.  
- **C2: Adapter Spec (deferred code)** (self): Document how `forest_status`/`forest_update` would map to `concept.forest.*`; no code change. Exit: dry-run prompt ready.  
- **C3: Metrics/Lookbacks (doc)** (time/void): Describe process-metrics spans and lookback triggers; no emission yet. Exit: schema captured in plan.  
- **C4: Education** (concept): README/skill note + example prompts scoped to plans/. Exit: snippet runnable by agents conceptually.
- **C5: Agent Comms Simplification** (concept/self): Design a single-hop message schema (handle + affordances + observer role) that agents can forward without human mediation; include identity/associativity checks per `spec/principles.md`.

---

## Handle Contracts & Law Checks (DEVELOP)
- Contracts live in `plans/skills/agentese-path.md` (forest appendix): IO per handle, Minimal Output (single renderable/iterator), rollback token required for `concept.forest.refine`.  
- Category guards: identity via noop refinement; associativity via patch composition order; reject raw arrays; stream epilogues one at a time.  
- Clause deck: `[phase=PLAN|...|REFLECT]`, `[entropy=0.05-0.10]`, `[law_check=true]`, `[rollback=true]`, `[minimal_output=true]` with spans tagged per phase.  
- Yoneda: handle is view; observer role determines affordances (guest/meta/ops) without altering the handle string.

## Role Gates & Observer Matrix (STRATEGIZE)
- guest -> `concept.forest.manifest`, `time.forest.witness` (read-only; no law-check triggers).  
- meta -> + `concept.forest.refine`, `self.forest.define` (proposal only; `[law_check=true][rollback=true]` mandatory).  
- ops -> + apply/publish/lint; log law checks + entropy spend; spans use `forest_*` ids when wired.  
- Law checks run on mutation start/end; Minimal Output enforced for all roles.

## Rollout & Dry-Run Notes (IMPLEMENT/QA/TEST/MEASURE)
- Sequence: docs (this plan + skills) -> clause micro-prompts in `n-phase-cycle` skills -> dry-run adapter notes (no code) -> deferred CLI hooks.  
- Dry-run checklist (doc-only):  
  - `concept.forest.manifest[phase=PLAN][minimal_output=true]` returns single canopy renderable with ledger presence.  
  - `time.forest.witness[phase=REFLECT][law_check=true]@span=forest_trace` yields one epilogue per call, ordered by mtime.  
  - `concept.forest.refine[phase=DEVELOP][rollback=true]` emits rollback token + sympathetic status dict.  
  - `void.entropy.sip[phase=RESEARCH][entropy=0.07]` logs entropy spend; `void.entropy.pour` returns delta.  
- Measurement stub: desired spans `{phase,tokens_in/out,duration_ms,entropy,law_checks}` recorded, emission deferred.  
- QA guardrails: headers stay <=100 lines; `phase_ledger` + `entropy` keys present; clause examples include `[phase]`, `[entropy]`, `[law_check]`, `[rollback]`, `[minimal_output]`; spans/metrics labeled deferred.

## Cross-Synergy Hooks (CROSS-SYNERGIZE)
- N-phase skills updated with clause prompts (`n-phase-cycle/README.md`, `phase-accountability.md`, `process-metrics.md`) to keep phase ledger ingestion AGENTESE-aware.  
- Composition map: `concept.forest.manifest >> concept.forest.refine >> time.forest.witness` with `void.forest.sip` supplying dormant plan selection; tie to `meta-skill-operad.md` for patch fusion.  
- Accursed Share rotation: `void.forest.sip[entropy=0.07]` selects dormant plan; `void.entropy.pour` on REFLECT; tithe if overdrawn.  
- Liturgy morphism: align witness streams with `liturgy-morphism-nasi` law checks; law spans marked but wiring deferred.

---

## Dry-Run Prompts (Conceptual Verification)

These prompts test forest handle contracts without code. Execute mentally to verify expected behavior.

### Test 1: Forest Manifest (Guest Observer)
```
Invoke: concept.forest.manifest[phase=PLAN][minimal_output=true]@span=test_001
Observer: guest_umwelt (archetype=guest)
Expected: ForestManifest with:
  - canopy: list[PlanHandle] (handles, not raw content)
  - metrics: ForestMetrics (aggregate stats)
  - attention_suggestion: str (dormant plan recommendation)
Verify: No mutation affordances in response (guest is read-only)
Law Check: None required (read operation)
```

### Test 2: Epilogue Stream (Meta Observer)
```
Invoke: time.forest.witness[phase=REFLECT][law_check=true]@span=test_002
Observer: meta_umwelt (archetype=meta)
Input: since=7_days_ago
Expected: AsyncIterator[Epilogue] (NOT array)
  - Each yield: single Epilogue object
  - Epilogue contains: handle, timestamp, summary, learnings, phase
Verify: Stream yields one epilogue per iteration, ordered by mtime
Law Check: Identity (same invocation = same stream order)
```

### Test 3: Accursed Share Sip (Meta Observer)
```
Invoke: void.forest.sip[phase=RESEARCH][entropy=0.07]@span=test_003
Observer: meta_umwelt (archetype=meta)
Input: strategy="longest_dormant"
Expected: ForestSipResult with:
  - selected_plan: PlanHandle (single dormant plan)
  - rationale: str ("Selected because: N days untouched, M% complete")
  - entropy_spent: 0.07
  - entropy_remaining: float
Verify: Returns single selection, not array. Entropy accounting correct.
Law Check: Entropy budget enforced
```

### Test 4: Refine with Rollback (Ops Observer)
```
Invoke: concept.forest.refine[phase=DEVELOP][rollback=true][law_check=true]@span=test_004
Observer: ops_umwelt (archetype=ops)
Input:
  plan_handle: "agents/t-gent"
  mutation: ForestMutation(kind="update_progress", payload={"progress": 95})
Expected: ForestRefineResult with:
  - rollback_token: str (REQUIRED, non-empty)
  - preview: PlanManifest (shows new state)
  - law_check: LawCheckResult (identity/associativity verified)
  - applied: False (dry-run default)
Verify: Rollback token present. Law check passes. Not applied until ops confirms.
Law Check: Identity (noop mutation returns unchanged), Associativity (patch composition)
```

### Test 5: Guest Cannot Refine
```
Invoke: concept.forest.refine[phase=DEVELOP]@span=test_005
Observer: guest_umwelt (archetype=guest)
Expected: AffordanceError with:
  - aspect: "refine"
  - observer_archetype: "guest"
  - available: ["manifest", "witness"]
  - suggestion: "Use meta or ops archetype for mutations"
Verify: Sympathetic error message suggests which archetype could refine
Law Check: Affordance gating enforced
```

### Dry-Run Summary Table

| Test | Handle | Observer | Expected | Law Check |
|------|--------|----------|----------|-----------|
| 1 | concept.forest.manifest | guest | ForestManifest | N/A |
| 2 | time.forest.witness | meta | AsyncIterator[Epilogue] | Identity |
| 3 | void.forest.sip | meta | ForestSipResult | Entropy |
| 4 | concept.forest.refine | ops | ForestRefineResult + rollback_token | Identity + Assoc |
| 5 | concept.forest.refine | guest | AffordanceError | Gating |

---

## Continuation Prompts (handoff)
- **Adapter agent**:
  - "Implement `concept.forest.manifest` by wrapping `forest_status()`; return structured manifest with affordances per observer (ops=update/check/lint, meta=manifest/witness/refine, guest=manifest only). Defer until code wiring allowed."
  - "Expose `time.forest.witness` as stream over `plans/_epilogues/*.md` ordered by mtime; include observer filter hooks. Defer code; document contract now."
- **Metrics agent**:
  - "Instrument forest adapter with spans `{phase, tokens_in/out, duration_ms, entropy, law_checks, exploration_spend}` per `process-metrics.md`; write hotloadable dashboard spec."
  - "Add lookback trigger after `forest update` runs; emit counter of double-loop shifts found."
- **Doc agent**:
  - "Augment `plans/skills/agentese-path.md` with forest handle examples and law checks; keep <10 lines."
  - "Add quickstart snippet to `plans/README.md` referencing `concept.forest.manifest` without bloating file."

---

## Risks / Blockers
- Meta-bloat: keep additions terse; reuse existing skills instead of new ones.
- Identity/associativity for handles must be verified (no arrays; streams only).
- Observer permissions: must gate mutating affordances (`update`, `define`) by role.
- Developer friction: CLI ergonomics may regress; acceptable if agent messaging is simpler (explicit).

---

## Exit Criteria (cycle)
- Handles specified, adapter mapping documented (code deferred), and prompts ready for other agents.
- Metrics schema + lookback trigger defined in docs (no emission yet).
- Forest users can invoke AGENTESE handles conceptually (or dry-run) and know how to proceed.

---

## Agent-to-Agent Communication Notes (spec-aligned)
- **Minimal output / Composable**: Handles return one manifest/witness item per call; peers compose via pipelines, not aggregates.  
- **Heterarchical routing**: Any agent can originate `concept.forest.*`; no central orchestrator-messages carry observer role + affordance.  
- **Tasteful/Curated**: Limit handle surface to manifest, witness, refine, sip, define; anything else becomes slop for Accursed Share rotation.  
- **Joy-Inducing**: Allow light persona tags in epilogue streams so peers can mirror tone; humans read secondary.  
- **Generative**: Document operad-like rewrites (manifest -> refine -> witness) so regeneration of adapters is mechanical once allowed.  
- **Ethical**: Observer role gates mutation; defaults to read-only for guests.  
- **Accursed Share**: Permit 5-10% entropy in `void.forest.sip` selection to keep dormant plans in circulation.
