---
path: plans/meta/chromatic-engine-design
status: active
progress: 55
last_touched: 2025-12-15
touched_by: gpt-5-codex
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: pending
entropy:
  planned: 0.10
  spent: 0.08
  returned: 0.02
---

# Chromatic Engine — Polyfunctor Scene Graph

> *"Perspectives are pigments; composition is the render loop."*

## Scope
- Goal: Reframe polyfunctor graph as scene graph where colors encode perspectives and blend modes express dialectics.
- Non-goals: Shipping runtime code; new math. Keep within existing AGENTESE + functor laws.
- Exit: Contracts + interfaces + branch candidates for implementation; ≤200 lines; entropy sip recorded.

## Research (file map + parallels)
- N-phase hologram and minimal artifacts give phase-to-pass scaffolding (`docs/skills/n-phase-cycle/README.md:55-79`).
- Categorical laws mandate identity/associativity for all agents—our render passes must preserve them (`spec/principles.md:71-92`).
- Functor laws (identity + composition) define shader/material invariants and lift/unlift symmetry (`docs/functor-field-guide.md:153-173`).
- Functor stack ordering (D→K→O→Flux) is our canonical material stack (`docs/categorical-foundations.md:148-155`).
- Profunctor Logos bridges intent to implementation—acts as scene graph resolver (`impl/claude/poly/profunctor.py:48-190`).

Blockers: None; open question—how to represent chaos/LOD knobs without breaking minimal output.

Opportunities:
- Use AGENTESE paths as scene nodes; profunctor lift as draw-call compiler.
- Map entropy budget to GPU budget; reuse auto-inducer signifiers for pass scheduling.
- Encode principles as material library to enforce tasteful/curated palettes (`spec/principles.md:7-34`).

## Chroma Model
- Channels: `hue(worldview)`, `saturation(assertiveness)`, `value(risk appetite)`, `opacity(override power)`, `blend(dialectic mode)`.
- Blend modes (dialectic): `add` (constructive superposition), `multiply` (constraint intersection), `screen` (safety-first brightening), `overlay` (context-weighted), `difference` (conflict surfacing), `mask` (gate by governance).
- Palette sources: personas (K-gent eigenvectors), principles (Tasteful/Curated, etc.), phase cues (SENSE warm, ACT neutral, REFLECT cool).

## Engine Diagram (textual)
- Geometry (phase intent) ↔ N-phase stage ↔ Category law ↔ Blend mode
  - PLAN vertex buffer ↔ SENSE/PLAN ↔ Identity seed ↔ `mask` (only allow scoped vertices)
  - RESEARCH geometry pass ↔ SENSE/RESEARCH ↔ Natural transformation (source→evidence) ↔ `multiply` (constraint by evidence)
  - DEVELOP material compile ↔ SENSE/DEVELOP ↔ Functor composition law ↔ `overlay` (persona influence on logic)
  - STRATEGIZE render queue ↔ SENSE/STRATEGIZE ↔ Associativity (pass ordering) ↔ `add` (compose options)
  - IMPLEMENT fragment ↔ ACT/IMPLEMENT ↔ Identity preservation ↔ `screen` (guardrails keep luminance)
  - QA/TEST post effects ↔ ACT/QA+TEST ↔ Idempotence of lifts ↔ `difference` (error surfacing)
  - MEASURE exposure ↔ REFLECT/MEASURE ↔ Monoidal accumulation ↔ `add` with decay
  - REFLECT tone-map ↔ REFLECT/REFLECT ↔ Fixed-point check ↔ `mask` on debt

## Contracts (must-hold)
- **Naturality under shader swap**: For any functor lift stack `L` and persona shader `S`, `L(S ∘ f) = L(S) ∘ L(f)`; shaders cannot break composition (`docs/functor-field-guide.md:153-163`).
- **Monoidal pass composition**: Render passes compose associatively and have identity clear pass; mirrors phase laws (`docs/skills/n-phase-cycle/README.md:55-58`).
- **Lift/unlift symmetry**: Every capability lift registers an unlift path so post-processing can re-enter base category (`docs/categorical-foundations.md:131-144`).
- **Palette curation**: Material library constrained by principles; reject hues outside tasteful/curated bounds (`spec/principles.md:7-34`).
- **Entropy↔GPU budget**: Each phase draws ≤0.10 entropy; exceeding budget halts pipeline (`docs/skills/n-phase-cycle/README.md:92-98`).
- **Dialectic invariants**: Blend mode choices must be commutative where declared (e.g., add/multiply) and explicitly ordered where not (overlay).

## Interfaces/Stubs (implementation targets)
- `concept.chromatic.registry`: shader/persona registry; keyed by AGENTESE path; exposes `compile_shader(persona, hue, saturation, value, opacity) -> Shader`.
- `concept.chromatic.materials`: material library binding principles to shader params; enforces palette curation + default blend per phase.
- `concept.chromatic.scene`: scene graph builder mapping phase artifacts to nodes; integrates LogosProfunctor bridge as resolver.
- `concept.chromatic.pipeline`: render loop hooks (pre-pass, main, post) aligned to phases; exposes `dialectic_stack` for blend scheduling.
- `concept.chromatic.chaos`: chaos/LOD controls; interface `dial(turn_entropy) -> quality_level`; defaults pulled from entropy ledger.
- `concept.chromatic.metrics`: exposure meter tying entropy spend to GPU budget; emits auto-inducer signifiers for continuation.

## Worked Example (phase traversal)
- PLAN vertex: scope defines geometry buffers; hue = worldview (e.g., operator vs user), opacity high to lock scope; outputs scene node `plan.vertex`.
- RESEARCH geometry: ingest citations; blend `multiply` to constrain vertices; outputs `research.mesh` + evidence textures.
- DEVELOP material compile: apply persona shader `S_kent`; enforce functor laws; output `develop.material` with governance mask.
- IMPLEMENT fragment: run nucleus code through material stack; `screen` blend to avoid clipping; outputs `implement.color`.
- QA/TEST post: `difference` blend with expected outputs; fails bubble as `⟂[QA:blocked]`.
- MEASURE exposure: accumulate metrics as histogram; adjust value channel to avoid burnout.
- REFLECT tone map: compress luminance into learnings; emit continuation handles + branch candidates.

## Branch Candidates
- Blocking: None.
- Parallel: `concept.chromatic.registry` vs `materials` can develop concurrently; integration needed at pipeline stage.
- Deferred: Chaos/LOD adapter to GPU budget; can stub with fixed entropy→quality mapping.

## Continuation (auto-inducer)
⟿[STRATEGIZE]
/hydrate
handles: hydrate=HYDRATE.md; n_phase=docs/skills/n-phase-cycle/README.md; chromatic=plans/meta/_research/nphase-prompt-compiler-develop.md; principles=spec/principles.md; functor_guide=docs/functor-field-guide.md; categorical=docs/categorical-foundations.md; impl_root=impl/claude; agents=impl/claude/agents; protocols=impl/claude/protocols
ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched}
entropy: spend=0.08/0.10
mission: sequence implementation tracks for registry/materials/pipeline + choose branch order.
exit: strategy sketch + branch plan.
