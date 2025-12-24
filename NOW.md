# NOW: The Living Document

> *"What's happening right now?"*

**Last Updated**: 2025-12-24 (Morning)
**Session**: Archival + Fresh Start

---

## FIRST: Get Task-Relevant Gotchas

```bash
kg docs hydrate "<your task>"
```

This surfaces critical gotchas, likely files, and voice anchors for YOUR specific task.
Don't skip this—the gotchas you don't read are the bugs you will write.

---

## The Greater Arc: Burn → Build → Harden → Ship

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: THE EXTINCTION (Dec 21)                                          │
│  67K lines archived. Town, Park, Gestalt, Coalition, Muse, Gardener gone.  │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 2: THE REBUILDING (Dec 21-22)                                       │
│  • Hypergraph Emacs: Six-mode modal editor for conceptual navigation       │
│  • WitnessedGraph: Evidence-carrying edges with visual confidence          │
│  • Inbound Sovereignty: External data ingestion with witnessing            │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 3: THE HARDENING (Dec 22-23)                                        │
│  • Dead Code Audit: ~14K more lines removed                                │
│  • AD-015/016: Fail-fast AGENTESE + ProxyHandleStore unification           │
│  • Validation Framework: 92 tests, witness-integrated                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  PHASE 4: THEORY CRYSTALLIZATION (Dec 23) ← YOU ARE HERE                   │
│  • 10-chapter monograph: "Categorical Foundations of Machine Reasoning"    │
│  • Derivation DAG: CONSTITUTION as axiomatic root, confidence navigation   │
│  • kgents 2.0 roadmap: CategoricalAgent + CPRM + SBM (15-week plan)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Current Focus

**CRYSTALLIZATION**: Theory meets implementation. The monograph is the map.

*"The proof IS the decision. The mark IS the witness."*

---

## What Happened Today (Dec 23)

### Major Deliverables

| Deliverable | Impact | Evidence |
|-------------|--------|----------|
| **🆕 Categorical Probes** | Phase 1 foundation for kgents 2.0 | `services/categorical/` — 41 tests |
| **Theory Monograph** | 10 chapters on categorical machine reasoning | `docs/theory/` — complete first draft |
| **Derivation DAG Phase 1-2** | CONSTITUTION as root, confidence navigation | 255+ tests, gD/gc keybindings |
| **Validation Framework** | Witness-integrated validation engine | 92 tests, `services/validation/` |
| **Proxy Handle Store** | Composite key support, event-driven invalidation | 70 tests, reactive staleness |
| **Inbound Sovereignty** | Content access requires explicit witnessing | AD-015 enforcement live |

### Categorical Probes Service (NEW)

Built complete infrastructure for testing kgents 2.0's core hypothesis:

```
services/categorical/
├── __init__.py         # Crown Jewel exports
├── probes.py           # MonadProbe + SheafDetector + CategoricalProbeRunner
├── study.py            # CorrelationStudy for Phase 1 gate validation
└── _tests/             # 41 tests (all passing)

protocols/agentese/contexts/
└── concept_categorical.py  # AGENTESE paths for categorical probes
```

**Key Components:**
- `MonadProbe`: Tests identity and associativity laws on LLM reasoning
- `SheafDetector`: Detects coherence violations (hallucinations)
- `CorrelationStudy`: Runs statistical correlation between laws and accuracy
- AGENTESE: `concept.categorical.{manifest,monad,sheaf,probe,study,status}`

**Phase 1 Gate Criteria (Enhanced 2025-12-23):**
| Metric | Threshold | Status |
|--------|-----------|--------|
| Monad identity correlation | r > 0.3 (CI lower bound) | ⏳ Pending study |
| Sheaf coherence correlation | r > 0.4 (CI lower bound) | ⏳ Pending study |
| Combined AUC | > 0.7 | ⏳ Pending study |
| **Beats random baseline** | Δ > 0.15 | ⏳ Pending study |
| **Permutation p-value** | p < 0.01 | ⏳ Pending study |

**Methodology Enhancements Added:**
- Bootstrap 95% CIs (lower bound must exceed threshold)
- Permutation tests for exact p-values (no normality assumption)
- Baseline comparisons (random, length, confidence heuristics)
- Hybrid sheaf detection (symbolic pre-filter → LLM)
- Automatic step extraction for associativity testing

### Today's Commits

| Commit | What | Arc |
|--------|------|-----|
| `49ebe16d` | Formatting + composite keys in ValidationEngine | HARDENING |
| `796e51ee` | Composite key support to ProxyHandleStore | HARDENING |
| `517df49e` | Enforce inbound sovereignty for content access | HARDENING |
| `32c61e1c` | **Categorical theory foundations + exploration plans** | THEORY |
| `b6c3b8f6` | Edge evidence querying via concept.derivation.edges | BUILDING |
| `c99c7a69` | Witnessed validation framework (Sessions 1+2 fused) | BUILDING |
| `234ab4f9` | Edge-aware witness integration (Phase 3C) | BUILDING |
| `db6aa302` | AppShell navigation + BrainPage memory explorer | BUILDING |

### Uncommitted Work

- New validation initiative YAMLs (`atelier.yaml`, `liminal.yaml`)
- Minor mypy.ini tweaks
- Garden.py formatting

---

## The Theory Monograph: "Categorical Foundations"

A 10-chapter work crystallizing the mathematical foundations:

```
Chapter 0: Overture — Why categories? The vision.
Chapter 1: Preliminaries — Categories, functors, natural transformations
Chapter 2: Reasoning as Morphism — Inference steps as arrows
Chapter 3: Monadic Reasoning — Effects, context, chain-of-thought
Chapter 4: Operadic Reasoning — Multi-input composition, proof trees
Chapter 5: Sheaf Coherence — Local-to-global belief consistency
Chapter 6: Neural Substrate — Attention, circuits, geometry
Chapter 7: Neurosymbolic Bridge — Categorical meets neural
Chapter 8: kgents Instantiation — Theory made code
Chapter 9: Open Problems — The frontier
```

**Status**: First draft complete. Ready for iteration.

**Why it matters**: This isn't just documentation—it's the **generative spec** for kgents 2.0. The four-phase plan (Foundations → Integration → Architecture → Synthesis) derives from this theory.

---

## Active Plans (8 remain — 90% archived Dec 24)

| Plan | Status | Notes |
|------|--------|-------|
| `_focus.md` | 🔒 HUMAN | Kent's intent (never archive) |
| `categorical-reinvention-phase1-foundations.md` | **EXECUTING** | Probes built ✅, study pending |
| `categorical-reinvention-phase2-integration.md` | NEXT | CPRM training |
| `categorical-reinvention-phase3-architecture.md` | FUTURE | SBM implementation |
| `categorical-reinvention-phase4-synthesis.md` | FUTURE | Ship kgents 2.0 |
| `ui-rebuild-from-first-principles.md` | ACTIVE | Fresh UI arc |
| `meta.md` | REFERENCE | Plan guidelines |
| `README.md` | INDEX | Plan navigation |

**Archived Dec 24**: 19 plans + 9 root docs → `_archive/2025-12-24-*/`
- All witness-* plans (completed)
- All derivation/validation plans (captured in commits)
- All SYNTHESIS/stark-biome/hypergraph-emacs (completed)
- LAW3, PHASE_2_2, HANDOFF docs (superseded by NOW.md)

---

## Crown Jewel Status (Post-Crystallization)

| Jewel | Status | Tests | Latest |
|-------|--------|-------|--------|
| **Brain** | 100% | 200+ | AppShell + BrainPage |
| **Witness** | 98% | 678+ | WitnessedGraph, edge evidence |
| **Validation** | NEW | 92 | Witnessed proposition checking |
| **Categorical** | NEW | 41 | MonadProbe + SheafDetector |
| **Atelier** | 75% | — | Design forge |
| **Liminal** | 50% | — | Transition protocols |

---

## The kgents 2.0 Roadmap

```
Phase 1: Foundations (3 weeks) — Probes that measure law satisfaction
Phase 2: Integration (4 weeks) — CPRM that scores reasoning steps
Phase 3: Architecture (5 weeks) — SBM that retains bindings
Phase 4: Synthesis (3 weeks) — Ship CategoricalAgent + pipeline

Total: 15 weeks from theory to product
```

Key deliverables:
- `CategoricalAgent[S, A, B]` with categorical guarantees
- `SharpBindingModule` for discrete variable tracking
- `CPRM` (Categorical Process Reward Model) for step verification
- AGENTESE paths: `concept.reasoning.solve`, `self.binding.state`

---

## Session Entry Points

**Continue current arc**:
```bash
# Derivation DAG Phase 3 — WitnessedDerivation
cat plans/derivation-dag-integration.md | head -80

# Validation CLI + AGENTESE
cat plans/validation-framework-implementation.md
```

**Quick wins (< 3 hrs)**:
```bash
# Dawn Phase 4 — j/k nav, copy confirmation
cat plans/dawn-phase-4-kickoff.md

# Stark Biome enforcement — ESLint rule
cat plans/stark-biome-enforcement.md
```

**Major arc (multi-session)**:
```bash
# Categorical Phase 1 — Foundation experiments
cat plans/categorical-reinvention-phase1-foundations.md

# kgents 2.0 — Full synthesis
cat plans/categorical-reinvention-phase4-synthesis.md
```

---

## Verification

```bash
# Backend quality gate
cd impl/claude && uv run pytest -q && uv run mypy . 2>&1 | tail -5

# Frontend quality gate
cd impl/claude/web && npm run typecheck && npm run lint 2>&1 | tail -5

# Theory monograph
ls docs/theory/*.md | wc -l  # Should be 11 files
```

---

## What's Different After Today

1. **Theory is crystallized** — The monograph provides intellectual foundation
2. **Derivation DAG is live** — CONSTITUTION as root, confidence visible
3. **Validation is witnessed** — Every check emits marks with Toulmin structure
4. **Proxy handles are reactive** — Event-driven staleness, not just TTL
5. **kgents 2.0 has a roadmap** — 15 weeks from theory to product

*"Daring, bold, creative, opinionated but not gaudy."*

---

*"The proof IS the decision. The mark IS the witness."*
