---
path: warp-servo/phase0-research
status: complete
progress: 100
last_touched: 2025-12-20
touched_by: claude-opus-4-5
blocking: []
enables: [warp-servo/phase1-core-primitives, warp-servo/phase2-servo-integration]
session_notes: |
  2025-12-20: Research complete. 4 deliverables created:
  - docs/research/servo-embedding-2025.md (GO decision)
  - docs/research/rust-core-strategy.md (Hybrid approach)
  - docs/research/warp-behavior-audit.md (2 ADAPT, 5 EVOLVE, 2 INVENT)
  - docs/research/existing-leverage.md (70% leverage, 30% build)
  Parallel agent execution used for research chunks.
  Chunk 5 (SpecGraph) deferred - primitives implemented directly.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
entropy:
  planned: 0.1
  spent: 0.08
  returned: 0.0
---

# Phase 0: WARP + Servo Research & Foundation

> *"Daring, bold, creative, opinionated but not gaudy"* — The Mirror Test

**AGENTESE Context**: Foundation for `time.*`, `self.*`, `concept.*` primitives
**Status**: Dormant (0 tests)
**Principles**: Generative (spec-first), Tasteful (curated primitives), Composable (category laws)
**Cross-refs**: `spec/protocols/warp-primitives.md`, `spec/protocols/servo-substrate.md`

---

## Core Insight

Before implementing, we must **ground in research**:
1. Servo embedding API maturity (Tauri prototype status)
2. Rust FFI strategy (PyO3 vs pure-Rust service)
3. WARP behavior audit (what we're adapting vs inventing)
4. Existing kgents systems to leverage (Witness, Brain, Gardener)

---

## Chunks

### Chunk 1: Servo Embedding Research (2-3 hours)

**Goal**: Determine Servo embedding viability and timeline.

**Tasks**:
- [x] Review [Servo 2025 Roadmap](https://servo.org/blog/)
- [x] Audit [Tauri embedding prototype](https://servo.org/blog/2024/01/19/embedding-update/)
- [x] Document embedding API surface (window creation, navigation, multi-webview)
- [x] Identify blockers for kgents integration
- [x] Write research summary: `docs/research/servo-embedding-2025.md`

**Exit Criteria**: ✅ GO decision — Servo via Verso + Tauri is production-viable for 2025.

---

### Chunk 2: Rust Core Strategy (2-3 hours)

**Goal**: Define Rust integration strategy for categorical kernel.

**Tasks**:
- [x] Evaluate PyO3 maturity for PolyAgent/Operad types
- [x] Prototype: Can we verify operad laws in Rust and expose to Python?
- [x] Document trade-offs: Rust crate vs pure-Python with performance paths
- [x] Identify which components benefit most from Rust:
  - TraceNode ledger (append-only, immutable)
  - Operad law checking (performance-critical)
  - Covenant/Offering enforcement (security-critical)
- [x] Write strategy doc: `docs/research/rust-core-strategy.md`

**Exit Criteria**: ✅ Hybrid approach — Rust for laws/ledger/covenant, Python for orchestration.

---

### Chunk 3: WARP Behavior Audit (2 hours)

**Goal**: Document exactly which WARP behaviors we're adapting.

**Tasks**:
- [x] Review `brainstorming/warp-primitives-for-kgents.md` mapping table
- [x] For each WARP primitive, classify:
  - ADAPT (directly map to kgents)
  - EVOLVE (enhance with category theory)
  - INVENT (kgents-native, WARP-inspired)
- [x] Document Voice Anchors for each primitive (Anti-Sausage check)
- [x] Write audit: `docs/research/warp-behavior-audit.md`

**Exit Criteria**: ✅ Classification complete — 2 ADAPT, 5 EVOLVE, 2 INVENT.

---

### Chunk 4: Existing System Leverage (2 hours)

**Goal**: Identify what existing kgents systems to leverage vs build new.

**Tasks**:
- [x] Audit Witness system for TraceNode compatibility
- [x] Audit Brain/Terrace for knowledge layer reuse
- [x] Audit Gardener for Walk/Ritual patterns
- [x] Audit CLI v7 for Conductor → Ritual mapping
- [x] Document leverage points and gaps
- [x] Write leverage doc: `docs/research/existing-leverage.md`

**Exit Criteria**: ✅ 70% leverage, 30% build-new. Witness/Gardener/Brain reusable.

---

### Chunk 5: SpecGraph Nodes (1-2 hours)

**Goal**: Register spec entries for all WARP primitives.

**Tasks**:
- [ ] Add SpecGraph frontmatter to `spec/protocols/warp-primitives.md`
- [ ] Add SpecGraph frontmatter to `spec/protocols/servo-substrate.md`
- [ ] Run SpecGraph compile → verify no drift
- [ ] Create stub impl files for drift-check

**Exit Criteria**: SpecGraph recognizes all new primitives.

---

## N-Phase Position

This plan covers phases:
- **PLAN**: ✅ Complete (this document)
- **RESEARCH**: The primary deliverable of Phase 0
- **DEVELOP**: Stub creation for SpecGraph

Subsequent phases (STRATEGIZE → IMPLEMENT) are in Phase 1+.

---

## Anti-Sausage Check

**Verified 2025-12-20**:
- ✅ Did research preserve Kent's voice? Yes — all deliverables quote anchors directly.
- ✅ Is the Servo decision daring? Yes — GO decision, not hedging.
- ✅ Does Rust strategy align with categorical foundation? Yes — laws/ledger/covenant in Rust.
- ✅ Are WARP adaptations opinionated, not kitchen-sink? Yes — 2 ADAPT, 5 EVOLVE, 2 INVENT (not "all the same").

---

## Cross-References

- **Spec**: `spec/protocols/warp-primitives.md`, `spec/protocols/servo-substrate.md`
- **Brainstorm**: `brainstorming/2025-12-20-servo-browser-engine-integration.md`
- **Skills**: `docs/skills/metaphysical-fullstack.md`, `docs/skills/projection-target.md`
- **Constitution**: `spec/principles/CONSTITUTION.md`

---

*"The persona is a garden, not a museum."*
