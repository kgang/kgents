---
path: plans/meta/chromatic-engine-master-prompt
status: active
progress: 0
priority: 10.0
importance: crown_jewel
last_touched: 2025-12-15
touched_by: gpt-5-codex
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
entropy:
  planned: 0.10
  spent: 0.09
  returned: 0.01
---

# Master Prompt — Chromatic Engine (Polyfunctor Scene Graph)

> *"Render perspectives as pigments; compose functors as passes."*

## Handles
- hydrate=HYDRATE.md
- n_phase=docs/skills/n-phase-cycle/README.md
- chromatic_design=plans/meta/chromatic-engine-design.md
- compiler_research=plans/meta/_research/nphase-prompt-compiler-research.md
- compiler_develop=plans/meta/_research/nphase-prompt-compiler-develop.md
- principles=spec/principles.md
- functor_guide=docs/functor-field-guide.md
- categorical=docs/categorical-foundations.md
- impl_root=impl/claude
- agents=impl/claude/agents
- protocols=impl/claude/protocols

## Mission
Ground the Chromatic Engine metaphor in kgents: treat the polyfunctor graph as a scene graph, colors as perspectives (hue/worldview, saturation/assertiveness, value/risk appetite, opacity/override), and blend modes as dialectic interactions. Execute as a Crown Jewel (full 11-phase) while honoring functor/category laws, AGENTESE, and the minimal-output principle.

## Core Context (synthesized)
- N-Phase scaffolding: each phase is a render pass with minimal artifact requirements and associativity law (`n_phase:55-79`).
- Principles enforce tasteful/curated palettes and composability; identity/associativity are non-negotiable (`principles:71-92`).
- Functor laws (identity + composition) = shader/material invariants; lift/unlift symmetry required (`functor_guide:153-173`; `categorical:131-155`).
- LogosProfunctor bridges AGENTESE intent to implementation—use as scene graph resolver (`impl_root/poly/profunctor.py:48-190`).
- Prompt Compiler prior art: YAML frontmatter parsing, frozen dataclass schemas, hardcoded templates, concept resolver hook; reuse for Chromatic registry and templates (`compiler_research`, `compiler_develop`).
- Chromatic design note: chroma channels, dialectic blend modes, render loop mapping per phase, entropy↔GPU budget, material library keyed by principles (`chromatic_design`).

## Chroma/Pass Model (refined)
- Channels: hue(worldview) • saturation(assertiveness) • value(risk appetite) • opacity(override) • blend(dialectic mode).
- Blend modes: add (constructive), multiply (constraint), screen (guardrails), overlay (context-weighted), difference (conflict surfacing), mask (governance gate).
- Phase→Pass: PLAN vertex/mask; RESEARCH geometry*multiply with evidence; DEVELOP material/overlay with persona shader; STRATEGIZE queue/add; IMPLEMENT fragment/screen; QA+TEST post/difference; MEASURE exposure/add-decay; REFLECT tone-map/mask on debt.
- Budget: entropy ≤0.10 per phase; tie to GPU/quality; halt on exhaustion.

## Contracts (must hold)
- Naturality under shader swap: `L(S ∘ f) = L(S) ∘ L(f)` for any lift stack `L` and persona shader `S`.
- Monoidal pass composition: passes associative with identity clear; mirrors phase laws.
- Lift/unlift symmetry: every capability lift registers unlift.
- Palette curation: materials constrained by Tasteful/Curated; reject out-of-gamut hues.
- Dialectic invariants: commutative blends (add/multiply) only when lawful; ordered blends explicit.
- Minimal output: one logical artifact per pass; compose at pipeline level.

## Interfaces (targets)
- `concept.chromatic.registry`: persona/shader registry keyed by AGENTESE path; `compile_shader(persona, hue, saturation, value, opacity) -> Shader`.
- `concept.chromatic.materials`: principles-bound material library with default blends per phase.
- `concept.chromatic.scene`: scene graph builder mapping phase artifacts to nodes via Logos resolver.
- `concept.chromatic.pipeline`: render loop hooks (pre/main/post) + dialectic stack; emits auto-inducer signifiers.
- `concept.chromatic.chaos`: chaos/LOD controls `dial(entropy) -> quality_level`.
- `concept.chromatic.metrics`: exposure meter linking entropy spend to GPU budget; report debt.

## Worked Thread (canonical flow)
1) PLAN: scope → vertex buffers; opacity high; emit `plan.vertex`.
2) RESEARCH: citations → geometry; `multiply` evidence textures.
3) DEVELOP: apply persona shader; enforce functor laws; output `develop.material`.
4) STRATEGIZE: order queue; resolve associativity; blend `add`.
5) IMPLEMENT: fragment through material stack; `screen` guardrails.
6) QA/TEST: `difference` vs expected; on fail emit `⟂[QA:blocked]`.
7) MEASURE: exposure histogram; decay; budget check.
8) REFLECT: tone-map into learnings; emit continuation + branch candidates.

## Crown Jewel Execution (11-phase skeleton)
- PLAN: scope, non-goals, entropy sip; decide palette bounds.
- RESEARCH: map prior art; cite AGENTESE/Logos/functor precedents; identify blockers.
- DEVELOP: assert contracts; finalize chroma model + interfaces; law checks.
- STRATEGIZE: sequence registry/material/pipeline/chaos; branch classification.
- CROSS-SYNERGIZE: align with AGENTESE, Prompt Compiler, auto-inducer; name compositions.
- IMPLEMENT: scaffold modules in `impl_root` (concept.chromatic.*) respecting lifts/unlifts.
- QA: lint/type placeholders; verify law stubs.
- TEST: add exemplar prompts/contracts; minimal golden-path tests or risk note.
- EDUCATE: doc snippet + usage note referencing handles.
- MEASURE: metric hook for budget/exposure; timebox debt.
- REFLECT: learnings + next-loop seeds; emit auto-inducer.

## Branching Guidance
- Parallel: registry vs materials can proceed concurrently; pipeline integration after.
- Blocking: none known; if chaos/LOD unclear, stub and mark deferred.
- Deferred: GPU-budget adapter; full shader DSL.

## Auto-Inducer Block
⟿[PLAN]
/hydrate
handles: hydrate=HYDRATE.md; n_phase=docs/skills/n-phase-cycle/README.md; chromatic_design=plans/meta/chromatic-engine-design.md; compiler_research=plans/meta/_research/nphase-prompt-compiler-research.md; compiler_develop=plans/meta/_research/nphase-prompt-compiler-develop.md; principles=spec/principles.md; functor_guide=docs/functor-field-guide.md; categorical=docs/categorical-foundations.md; impl_root=impl/claude; agents=impl/claude/agents; protocols=impl/claude/protocols
ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched}
entropy: spend=0.09/0.10
mission: run Crown Jewel loop using this master prompt to deliver registry/material/pipeline stubs and contracts.
exit: plan→research continuation generated with updated ledger + entropy.
