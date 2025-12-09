# HYDRATE.md - kgents Session Context

Hydrate context with this file. Keep it concise—focus on current state and recent work.

## Meta-Instructions for Maintaining This File

**WHEN ADDING NEW SESSIONS**:
- Add to "Current Session" section with date
- Move previous "Current Session" to "Recent Sessions"
- Keep only 3-4 most recent sessions in "Recent Sessions"
- Move older sessions to compressed Archive (use `<details>` tags)
- Update TL;DR with new status/commits

**AVOID**:
- ❌ Verbose session descriptions (keep to bullet points)
- ❌ Duplicating information already in git commits
- ❌ More than 5 recent sessions visible
- ❌ Detailed code snippets (reference files instead)
- ❌ Multiple paragraphs per session (use tables/lists)

**CLEANUP CHECKLIST** (run every 5-10 sessions):
1. Merge similar historical sessions in Archive
2. Verify TL;DR reflects actual latest commit
3. Remove sessions older than 2 weeks unless milestone
4. Compress Archive sections if >500 lines
5. Target: Keep file under 300 lines total

**PRINCIPLES**: Tasteful (concise), Curated (only essential), Generative (actionable next steps)

---

## TL;DR

**Status**: Uncommitted changes (CLI Integrations Phase 1)
**Branch**: `main`
**Latest Commit**: 599c928 - docs: Update HYDRATE.md for J-gents Phase 2 session
**Current State**:
  - CLI Integrations Phase 1: ✅ COMPLETE (4 daily companions)
  - G-gent Specification: ✅ SPEC COMPLETE (needs implementation)
  - Mirror Protocol Phase 1: ✅ COMPLETE (46 tests)
  - Mirror Protocol Phase 2: ✅ COMPLETE (EventStream implementations, 26 tests)
  - Mirror Protocol Phase 3 (Kairos): ✅ COMPLETE (controller, attention, salience, benefit, budget, watch)
  - CLI Publishing: ✅ COMPLETE (`kgents` command via pyproject.toml)
  - CLI Protocol: ✅ COMPLETE (59 passing tests)
  - Membrane Protocol v2.0: ✅ COMPLETE
  - Tests: 59 passing CLI + 22 Kairos + more

**Next Steps**:
1. CLI Integrations Phase 2 (Scientific Core: falsify, conjecture, rival, sublate, shadow)
2. Implement G-gent Phase 1 (Core Types + Tongue artifact)
3. Fix lint warnings (2 unused variables in igent_synergy.py, membrane_cli.py)

---

## Recent Sessions

### Session: CLI Integrations Phase 1 (2025-12-09)

**Status**: ✅ COMPLETE - Daily Companion Commands Implemented

**New Files Created**:
- `impl/claude/protocols/cli/companions.py` (~400 lines): Daily companion commands

**Commands Implemented** (Tier 1 - 0 tokens, local only):
- `kgents pulse`: 1-line project health (hypotheses pending, tensions held, flow phase)
- `kgents ground "<statement>"`: Parse statement, reflect structure, detect contradictions
- `kgents breathe`: Contemplative pause with gentle prompt
- `kgents entropy`: Show session chaos budget from git/file analysis

**Key Features**:
- FlowPhase detection (morning/afternoon/evening/night)
- Hypothesis detection from source file patterns (TODO, H:, What if)
- Tension detection from .kgents state and TENSION markers
- Activity level from git log timestamps (active/quiet/dormant)
- Ground parsing: action-target extraction, contradiction scoring, complexity scoring
- Entropy calculation: git diff stats + token usage + LLM calls

**Tests**: All 59 CLI tests pass

**Next**: Phase 2 (Scientific Core: falsify, conjecture, rival, sublate, shadow)

### Session: Kairos Controller Implementation (2025-12-09)

**Status**: ✅ COMPLETE - All core Kairos components implemented with 22 passing tests

**New Files Created** (~1400 lines):
- `impl/claude/protocols/mirror/kairos/` module structure:
  - `attention.py` (~280 lines): Attention state detection from filesystem/git activity
  - `salience.py` (~150 lines): Tension salience calculator with momentum & recency
  - `benefit.py` (~170 lines): Benefit function B(t) = A(t) × S(t) / (1 + L(t))
  - `budget.py` (~200 lines): EntropyBudget for rate limiting (4 levels)
  - `controller.py` (~320 lines): KairosController with state machine
  - `watch.py` (~145 lines): Autonomous watch mode loop
  - `_tests/test_kairos.py` (~580 lines): Comprehensive test suite

**Modified**:
- `impl/claude/protocols/mirror/types.py`: Added `id` property to Tension type

**Key Features**:
- Attention Detection: Infers user state from file/git activity (DEEP_WORK/ACTIVE/TRANSITIONING/IDLE)
- Salience Calculation: Tension urgency from severity × momentum × recency
- Benefit Function: Balances attention budget, salience, cognitive load
- Entropy Budget: 4 levels (LOW/MEDIUM/HIGH/UNLIMITED) prevent notification fatigue
- Controller: Full state machine (OBSERVING → EVALUATING → SURFACING/DEFERRING → COOLDOWN)
- Watch Mode: Async loop for autonomous observation

**Tests**: 22 passing (100% pass rate)

**Next**: CLI command integration (watch, timing, surface, history)

### Session: G-gent Specification (2025-12-09)

**Created**:
- `spec/g-gents/README.md` (~500 lines): G-gent (Grammarian) specification
  - DSL synthesis from domain intent + constraints
  - Three grammar levels: Schema (Pydantic), Command (Verb-Noun), Recursive (S-expr)
  - Tongue artifact: reified language with grammar, parser config, interpreter config
  - "Constraint is Liberation" principle: forbidden ops → grammatically impossible
- `spec/g-gents/grammar.md` (~400 lines): Grammar synthesis specification
  - Domain analysis → Grammar generation → Ambiguity verification
  - Constraint crystallization (structural, not runtime)
- `spec/g-gents/tongue.md` (~350 lines): Tongue artifact specification
  - Lifecycle: creation → registration → usage → evolution → deprecation
  - Serialization, validation, security considerations
- `spec/g-gents/integration.md` (~400 lines): Integration patterns
  - P-gent (parsing), J-gent (execution), F-gent (artifact interface)
  - L-gent (discovery), W-gent (inference), T-gent (fuzzing), H-gent (dialectic)
- `docs/g-gent_implementation_plan.md` (~500 lines): Implementation roadmap
  - 7 phases: Core Types → Synthesis → P/J/L/F Integration → Advanced

**Key Concepts**:
- G-gent fills gap between P-gent (parsing) and J-gent (execution)
- Solves Precision/Ambiguity Trade-off (NL too fuzzy, Code too rigid, DSL "Goldilocks")
- Functorial mapping: `G: (DomainContext, Constraints) → Tongue`
- Use cases: Safety Cage (no DELETE in grammar), Shorthand (token compression), UI Bridge, Contract Protocol

### Session: Kairos Phase 3 Spec + CLI Publishing (2025-12-09)

**Commit**: 1da5127 - feat(protocols): Add Kairos Phase 3 spec and CLI publishing

**Created**:
- `spec/protocols/kairos.md` (~500 lines): Opportune moment detection spec
  - Attention Budget, Tension Salience, Benefit Function B(t) = A(t)×S(t)/(1+L(t))
  - Entropy Budget, Kairos Controller state machine, Ethical safeguards
  - Watch mode: `kgents mirror watch --budget=medium`
- `impl/claude/protocols/cli/__main__.py`: Module entry point

**Modified**:
- `impl/claude/pyproject.toml`: Added protocols package + kgents console script
- CLI now installable: `kgents --help` and `python -m protocols.cli --help` both work

**Included**: EventStream Phase 2 (GitStream, TemporalWitness, SemanticMomentumTracker) + CLI Protocol (59 tests)

**Tests**: 63 passing, 22 skipped

### Session: EventStream Phase 2 Implementation (2025-12-09)

**New Files Created** (~700 lines):
- `impl/claude/protocols/mirror/streams/` - EventStream implementations
- GitStream, TemporalWitness, SemanticMomentumTracker
- 26 tests (4 baseline, 22 skipped for optional deps)

**Key Features**:
- J-gent reality classification (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
- Semantic momentum tracking (p⃗ = m · v⃗)
- Stream composition, drift detection, sliding windows

### Session: Protocol Spec Refinement (2025-12-09)

**Files Modified**:
- `spec/protocols/cli.md`: 735 → 526 lines (28% reduction)
- `spec/protocols/event_stream.md`: 951 → 747 lines (21% reduction)

**Principles Applied**: Tasteful, Curated, Ethical (explicit), Generative

### Session: CLI Protocol Implementation (2025-12-09)

**Files Created**:
- `impl/claude/protocols/cli/types.py` (~350 lines)
- `impl/claude/protocols/cli/mirror_cli.py` (~320 lines)
- `impl/claude/protocols/cli/membrane_cli.py` (~450 lines)
- `impl/claude/protocols/cli/igent_synergy.py` (~380 lines)
- `impl/claude/protocols/cli/main.py` (~400 lines)
- Tests: 59 passing

**Unlocked**: Mirror + Membrane protocols through command surface with I-gent synergy (StatusWhisper, SemanticGlint, GardenBridge)

### Session: EventStream Protocol Specification (2025-12-09)

**Created**: `spec/protocols/event_stream.md` (951 lines)
- J-gent reality classification (DETERMINISTIC/PROBABILISTIC/CHAOTIC)
- Three implementations: GitStream, ObsidianStream, FileSystemStream
- TemporalWitness (W-gent) for drift detection
- SemanticMomentumTracker (Noether's theorem: p⃗ = m · v⃗)
- EntropyBudget for recursion management
- Stream composition patterns

**Commit**: d4484fb
**Tests**: 63 passing

### Session: Mirror Protocol Phase 1 (2025-12-09)

**Files Created**:
- `impl/claude/protocols/mirror/types.py`: Core types (Thesis, Antithesis, Tension, Synthesis, MirrorReport)
- `impl/claude/protocols/mirror/obsidian/extractor.py`: P-gent principle extraction
- `impl/claude/protocols/mirror/obsidian/witness.py`: W-gent pattern observation
- `impl/claude/protocols/mirror/obsidian/tension.py`: H-gent tension detection
- Tests: 46 passing

**Status**: Phase 1 ✅ COMPLETE

---

## Project State Summary

### Completed Phases

| Phase | Status | Key Deliverables | Tests |
|-------|--------|-----------------|-------|
| **Mirror Phase 1** | ✅ | Obsidian extractor, tension detection | 46 |
| **Membrane Protocol** | ✅ | Topological perception layer | Integrated |
| **CLI Protocol** | ✅ | MirrorCLI, MembraneCLI, I-gent synergy | 59 |
| **EventStream Spec** | ✅ | Protocol + 3 implementations spec'd | N/A |

### Phase 2 Ready

**EventStream Implementation Path**:
1. Create `impl/claude/protocols/mirror/streams/` module
2. Implement EventStream protocol base classes
3. Implement GitStream (git-python)
4. Add TemporalWitness for drift detection
5. Add SemanticMomentumTracker (sentence-transformers)
6. Integrate with Mirror Protocol

### Key Architecture Decisions

- **Protocol-first**: Specs drive implementations (generative principle)
- **Composable**: All agents are morphisms; composition laws verified
- **Heterarchical**: Functional (invoke) and autonomous (loop) modes
- **J-gent safety**: Reality classification before execution, Ground collapse for chaos
- **I-gent synergy**: CLI includes perception layer (StatusWhisper, SemanticGlint)

---

## Archive: Historical Sessions (Compressed)

<details>
<summary>H-gent Spec Development (2025-12-09)</summary>

**Reconciliation**: Backpropagated impl insights to specs
- TensionMode enum, DialecticStep lineage
- Marker-based detection (SYMBOLIC/IMAGINARY/REAL)
- Errors-as-data pattern (LacanError)
- Composition pipelines (HegelLacan, LacanJung, FullIntrospection)
- CollectiveShadowAgent
- Updated archetypes: 6 → 8 (added Dialectician, Introspector)

**Files Modified**: h-gents/README.md, contradiction.md, sublation.md, composition.md (NEW), bootstrap.md, archetypes.md
</details>

<details>
<summary>Mirror Protocol Docs Synthesis (2025-12-09)</summary>

**Theoretical Additions**:
- Tri-Lattice System: 𝒟 (Deontic), 𝒪 (Ontic), 𝒯 (Tension)
- Semantic Momentum: p⃗ = m · v⃗
- Quantum Dialectic: |ψ⟩ = α|Hypocrisy⟩ + β|Aspiration⟩
- Thermodynamic Cost: C(t) = (η·S + γ·L) / A
- Entropy Budget: TrustEntropy for intervention gating

**Phase Restructure**: Organizational focus → Personal/research focus
</details>

<details>
<summary>Membrane Protocol v2.0 (2025-12-09)</summary>

**Created**: `spec/protocols/membrane.md` (~600 lines)
- Semantic Manifold: Curvature, Void (Ma), Flow, Dampening
- Pocket Cortex: Local perception state
- Grammar of Shape: 5 perception verbs (observe, sense, trace, touch, name)
- Integration with Mirror Protocol (complementary, not conflicting)

**Relationship**: Membrane = perception/interface layer, Mirror = dialectical engine
</details>

<details>
<summary>Foundation Work (Pre-2025-12-09)</summary>

**Major Milestones**:
- A-gents, B-gents, C-gents, K-gent, R-gents, T-gents specifications
- Bootstrap Protocol + BootstrapWitness (category law verification)
- Principles.md (7 principles + Accursed Share + Personality Space + Puppets)
- Archetypes (8 patterns: Observer, Parser, Composer, Refiner, Tester, Dialectician, Introspector, Witness)
- Infrastructure vs Composition pattern established
- zen-agents experiment (60% code reduction proof)

**Repository Structure**:
- `spec/`: Specification (implementation-agnostic)
- `impl/claude/`: Reference implementation (Claude Code + Open Router)
- Alphabetical taxonomy: A-Z agent genera
</details>

---

## Quick Reference

### Current Test Status
- **Total**: 168+ tests passing
- Mirror Protocol: 46 tests
- CLI Protocol: 59 tests
- EventStream: 63 tests (includes prior work)

### Key Files to Read
- `spec/principles.md`: 7 design principles
- `spec/protocols/mirror.md`: Mirror Protocol (dialectical introspection)
- `spec/protocols/membrane.md`: Membrane Protocol (topological perception)
- `spec/protocols/cli.md`: CLI meta-architecture
- `spec/protocols/event_stream.md`: EventStream Protocol (temporal observation)
- `spec/bootstrap.md`: Bootstrap Protocol (self-derivation)

### Branch Status
- **main**: Clean, all tests passing
- No uncommitted changes (per status at session start)

---

*Last Updated: 2025-12-09*
*Hydrate sessions should be concise—archive old work, focus on now.*
