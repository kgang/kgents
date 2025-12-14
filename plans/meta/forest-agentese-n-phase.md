---
path: meta/forest-agentese
status: active
progress: 35
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: [plans/_forest.md, plans/_status.md]
session_notes: |
  Added forest handle appendix + single-hop schema (agentese-path). Documented dry-run adapter mapping in DEVELOP skill and forest metrics/lookback hooks in process-metrics. README now carries forest handle quickstart.
---

# Plan: Forest Meta-System (AGENTESE × N-Phase)

> *"To read is to invoke. The forest is a verb."*

**AGENTESE Context**: `concept.forest.*` (planning grammar), `self.forest.*` (maintenance agents), `time.forest.witness` (epilogues), `void.accursed-share.sip` (exploration rotation)  
**Principles**: Tasteful, Composable, Heterarchical, Accursed Share, Transparent Infrastructure  
**Cross-refs**: `spec/protocols/agentese.md`, `plans/principles.md`, `plans/skills/n-phase-cycle/*` (implementation hooks deferred)

---

## Core Insight
The plan system itself is an agent: AGENTESE handles should surface plan manifests/traces and accept mutations as lawful morphisms. For this pass, all work stays inside `plans/` (skills, headers, prompts); wiring into the `kgents` codebase is deferred. Agent-to-agent coherence is prioritized over developer comfort (85/15 weighting); developer experience may be marginally worse if it simplifies agent messaging. The N-phase cycle governs self-renewal: PLAN→…→REFLECT with embedded lookbacks and process metrics.

---

## Current State (RESEARCH snapshot)
- Forest CLI (`kgents forest`) parses plan headers and renders `_forest.md`; AGENTESE path exposure is pending and **out of scope** for this cycle.
- N-phase skills exist but are not bound to planning artifacts; lookbacks happen ad hoc.
- Accursed Share rotation is implied (dormant plans) but not addressable as a first-class handle.
- Agent comms friction: humans rely on CLI; agents lack a clear, minimal manifest+affordance grammar for peer-to-peer invocation.

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
- **Heterarchical routing**: Any agent can originate `concept.forest.*`; no central orchestrator—messages carry observer role + affordance.  
- **Tasteful/Curated**: Limit handle surface to manifest, witness, refine, sip, define; anything else becomes slop for Accursed Share rotation.  
- **Joy-Inducing**: Allow light persona tags in epilogue streams so peers can mirror tone; humans read secondary.  
- **Generative**: Document operad-like rewrites (manifest → refine → witness) so regeneration of adapters is mechanical once allowed.  
- **Ethical**: Observer role gates mutation; defaults to read-only for guests.  
- **Accursed Share**: Permit 5–10% entropy in `void.forest.sip` selection to keep dormant plans in circulation.
