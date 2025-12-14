---
path: meta/liturgy-morphism-nasi
status: active
progress: 5
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: [spec/protocols/agentese.md, plans/_forest.md, plans/skills/agentese-path.md]
session_notes: |
  Standing up N-NASI ("The Liturgical Morphism"): AGENTESE as internal language + liturgy compiler. This pass is planning-only; no code written. Captured grammar/handle milestones and risk-tiered deliverables.
---

# Plan: The Liturgical Morphism (N-NASI)

> *"In the beginning was the Word, and the Word was the Agent."*

## Thesis
AGENTESE graduates from naming system to internal programming language. Agents become sentences; code is generated from liturgical morphisms (`@liturgy`), enabling self-hosted rewriting via `self.liturgy.*` handles.

## Objectives (near-term cycle)
- Define grammar + type surface for liturgical sentences (concatenative, Minimal Output).
- Specify JIT compiler pipeline (parse → resolve → type-check → fuse PolyAgent).
- Design self-rewrite handles (`self.liturgy.read/rewrite/simulate`) with safety rails.
- Align Turns-as-dots with Flux/Polyfunctor/Agent registry; keep AGENTESE laws intact.

## Scope / Non-Scope (this cycle)
- In: specs, skills, prompt scaffolds, adapter contracts. No impl/ code yet.
- Out: CLI integration, runtime rewrites, registry migration. Those land after dry-run validation.

## Deliverables by Phase (N-Phase framing)
- PLAN/RESEARCH: grammar draft (BNF), catalog of resolvable holons/aspects with IO types; risk register.
- DEVELOP: liturgy compiler contract + `@liturgy` decorator shape; `Nous`/`n("path")` wiring diagram; turn-level failure semantics.
- STRATEGIZE/CROSS-SYNERGIZE: composition with Flux turns, PolyAgent wiring, HotData fixtures, and K-gent personality coordinates; identify adapters (forest_status→manifest, etc).
- IMPLEMENT (doc only): skills appendices + dry-run prompts; no code.
- QA/TEST (doc): law checks (identity/assoc, minimal output), entropy bounds for `void.entropy.sip`.
- EDUCATE/MEASURE/REFLECT: demo script outline (haiku/guard/autopoietic agents) and metrics schema for compiler traces (tokens, law checks, entropy).

## Chunks (parallelizable)
- C1 Grammar: BNF + examples (haiku, guard, autopoietic) with type expectations per dot.
- C2 Compiler Contract: parse/resolve/type-check/fuse; decorator shape; `Nous` composition rules.
- C3 Self-liturgy Handles: read/rewrite/simulate contract + safety (role-gating, dry-run, diff).
- C4 Cross-Synergy Map: Flux Turn alignment, Polyfunctor embeddings, HotData/fixtures, K-gent persona coordinates.
- C5 Metrics & Risk Tiers: spans for compiler, entropy spend bands, rollback plan for rewrites.

## Artifact Shelf & Gap Log
- Artifacts on hand: grammar BNF sketch placeholder (C1), flow bullets (three journeys, baton handoff), process metrics spec (`plans/skills/n-phase-cycle/process-metrics.md` spans), AD-002 PolyAgent framing, Void entropy ledger (void.* contexts), ContextWindow comonad semantics (self.stream.*).
- Open questions to close: IO typing gaps for context resolvers (self.memory/self.stream/world void/time), PolyAgent positions/directions for semaphore/schedule/entropy pool/stateful rewrites, entropy band guardrails (Accursed Share 0.05–0.10) + tithe enforcement, rollback invariants + Purgatory token schema, Minimal Output adherence in each handle, category-law checkpoints (identity/assoc) and where they emit witness spans, polymorphic outputs in void/serendipity/pataphysics, unknown returns from capital ledger/bypass tokens, stream compression thresholds/types.

## Invocation Flows & Journeys (N-Phase, multi-agent)
- Guest Read (PLAN → RESEARCH): `self.liturgy.read` renders liturgy + witness spans; N-gent collects trace; D-gent stays idle. Output is Renderable only (Minimal Output). Hand off to EDUCATE for documentation refresh.
- Meta Simulate (DEVELOP → QA/TEST): `self.liturgy.simulate path="concept.justice.refine>>void.entropy.sip:amount=0.05"` parses → resolves → type-checks → runs law checks (identity/assoc) without side effects. Flux Turn manager emits spans with `{phase, tokens, entropy, law_checks}` per `process-metrics.md`; void budget debited and poured back if unused. Result diff goes to MEASURE with rollback pointer (shadow copy).
- Ops Rewrite (IMPLEMENT → QA/TEST → DEPLOY): Ops archetype calls `self.liturgy.rewrite path="self.memory.consolidate>>self.stream.project.compress"`; pre-flight = snapshot hotdata + polyagent direction check (AD-002). If law checks pass, apply to active liturgy; if fail, emit `InvalidDirection` at dot-level locus and auto-rollback. Purgatory receives rollback token; N-gent records witness; J-gent regenerates derived docs. REFLECT closes loop with entropy spend audit (0.05–0.10 band) and span aggregation.
- Multi-agent baton: K-gent sets observer coordinates → J-gent regenerates spec snippets → D-gent checkpoints context → N-gent traces → O/Flux orchestrates across sessions. Each baton throw is a Turn with explicit handle; sessions persist via `time.trace.collect` + HotData snapshots to resume mid-cycle.

## Risk / Payoff Tiers
- Tier 0 (safe): Docs/specs only; no runtime changes.
- Tier 1 (pilot): Sandbox compiler on fixtures; non-mutating liturgy evaluation; rollback by deleting fixture.
- Tier 2 (bet): Self-rewrite hooks enabled; requires gated roles + snapshot/rollback + law-check enforcement. Ship only after Tier 1 burn-in.

## Continuation Prompts
- "Draft BNF for liturgy sentences (pipes, args, comments), map to `Logos` resolution with IO types; include Turn-level failure semantics."
- "Spec `@liturgy` decorator + `Nous` object: how type metadata is sourced, how minimal-output law enforced, how to fuse adjacent pure morphisms."
- "Design `self.liturgy.read/rewrite/simulate` contract with role gates, dry-run diff, entropy cap for rewrites; no code yet."
- "Plan a pilot: pick 3 agents (poet, guard, autopoietic) as fixtures; outline hotdata generation; define metrics to collect during pilot (tokens, law_checks, entropy, rollback count)."

## Concrete Flow Narratives (Tier 0/1, doc-only)
- Guest Read (Minimal Output): `self.liturgy.read(observer=K, format="renderable")` → resolve liturgy path → renderable payload `{summary, content?, metadata}` + witness span `{phase="PLAN/RESEARCH", tokens_out, success=true, law_checks=0}`; no state mutation, no entropy debit. Failure examples: missing liturgy handle → `{error:"NotFound", locus:"read.resolver"}`; Minimal Output enforced (single renderable).
- Meta Simulate (dry-run): `self.liturgy.simulate(path="concept.justice.refine>>void.entropy.sip:amount=0.05", mode="dry", law_check=true)` → steps: parse BNF → resolve handles (concept.*, void.*, time.*) → type-check IO (unknown outputs flagged) → category law check (identity/assoc) → void.entropy.sip debits 0.05 (grant.seed captured) → execution dry-run with synthetic outputs (no mutations) → entropy pourback if unused → emit diff artifact `{path, predicted_output, entropy_debit, law_checks}` + span `{phase="DEVELOP/QA", tokens_in/out, duration_ms, entropy=0.05, success|failure}`. Failure loci: `BudgetExhaustedError` from void.entropy, `PolymorphicIO` when resolver returns variant type, `AssocViolation` from law checks, `MissingAffordance` on path segment.
- Ops Rewrite (gated): `self.liturgy.rewrite(path="self.memory.consolidate>>self.stream.project.compress", snapshot="hotdata/latest", validate="AD-002")` → preflight: snapshot HotData + Purgatory token create → PolyAgent direction validation (positions: semaphore? schedule? stream_window) → parse/resolve/type-check → law-check identity/assoc on composed morphisms → apply plan to active liturgy or emit `InvalidDirection(locus="stream.project.compress")` → record rollback token, emit span `{phase="IMPLEMENT/QA", entropy<=0.10, rollback_token, success}`; Minimal Output: one dict `{status, applied|error, span_ref, rollback_token}`. Failure loci: budget exhaustion, missing snapshot, unknown state transition, identity violation, IO mismatch.

## Failure Surface Examples (Minimal Output per failure)
- Budget exhaustion: `{error:"BudgetExhausted", locus:"void.entropy.sip", remaining:<float>, requested:<float>, witness:<span_id>}`.
- Missing affordance: `{error:"MissingAffordance", locus:"self.stream.seek.position", path:<str>}`.
- Assoc/identity violation: `{error:"LawCheckFailed", locus:"compose[2]", law:"associativity", path:<str>}`.
- Polymorphic IO mismatch: `{error:"PolymorphicIO", locus:"concept.blend", expected:"Renderable", received:"dict|Renderable|None"}`.

## Tier 1 Dry-Run Playbook (doc commands, no code)
- Read: call `self.liturgy.read` with `format="renderable"`; capture witness span + metadata; verify no state change in D-gent checkpoints.
- Simulate: run `self.liturgy.simulate path="<concept|void|time path>" mode="dry" law_check=true entropy_band=0.05–0.10`; collect diff artifact + span; check pourback when unused.
- Rewrite (shadow): run `self.liturgy.rewrite path="<self.memory|self.stream...>" snapshot="hotdata/<fixture>" dry_run=true validate=AD-002`; expect rollback token + shadow diff; do not mutate live liturgy.
- Expected spans/diffs: spans per phase align to `{phase, tokens_in/out, duration_ms, entropy, success, law_checks, exploration_spend}`; diffs stored as renderable/dict artifacts; rollback pointer references Purgatory snapshot.

## Baton Pass (Multi-agent)
- Sequence: K-gent sets observer coordinates/personality → J-gent regenerates spec snippets/BNF fragments → D-gent checkpoints context window/hotdata → N-gent traces spans + witness → O/Flux orchestrates turn scheduling and law-check injection → baton returns to K for next observer or closes via time.trace.
- Turn model: each baton throw is a Turn with handle and Minimal Output; identity = noop turn, associativity = stable composition of baton sequence; Flux Turn manager emits spans with lawfulness counters; baton order stored via `time.trace.collect`.

## Rollback, Entropy, and Law Checkpoints
- Entropy guardrail: sip defaults 0.05; enforce band 0.05–0.10 for simulate/rewrite; pourback when unused; tithe path `void.gratitude.tithe` restores budget before retry.
- Rollback invariants: any rewrite issues rollback token stored in Purgatory (time/world) with snapshot pointer; law-check failure must auto-rollback without consuming entropy beyond audit spend; Minimal Output dict includes rollback_token or `shadow_only=true`.
- Category checkpoints: identity (`Id>>f==f`), associativity (`(f>>g)>>h == f>>(g>>h)`), enforcement stage = preflight in simulate + rewrite; witness span includes `{law_checks:{identity:pass/fail, assoc:pass/fail}}`.

## QA / TEST Checklists (per flow)
- Identity/associativity: pass or emit `LawCheckFailed` with dot-level locus.
- PolyAgent direction validity: positions/directions validated for stream/memory/semaphore; unknown transitions flagged.
- Minimal Output compliance: one renderable/dict per call; no aggregates.
- Entropy band: enforce 0.05–0.10 sip; pourback recorded; tithe path documented.
- Rollback snapshot: snapshot created before mutate; token recorded.
- Witness emitted: span per phase with metrics from process-metrics schema.

## Residual Risks / Next Hooks
- IO typing gaps: self.memory/self.stream/world/time/void return polymorphic dicts/renderables; need typed envelopes.
- PolyAgent transitions: semaphore/schedule/entropy pool positions not enumerated; wiring diagrams pending.
- Entropy enforcement: need hard clamps + tithe requirement for re-tries; Accursed Share ledger integration.
- Rollback granularity: purgatory token schema + partial revert semantics TBD.
- Minimal Output adherence: some contexts (serendipity/pataphysics) emit multiple keys; may need wrappers.
- Category law checkpoints: need concrete witness functions + dashboards tied to spans.
- Next session hooks: generate fixture trio (poet/guard/autopoietic), extend BNF draft with type annotations, add adapters for polymorphic outputs, wire spans to process-metrics dashboard spec.
