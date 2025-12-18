---
path: plans/autopoietic-consolidation
status: active
progress: 5
last_touched: 2025-12-17
touched_by: claude-opus-4-5
blocking: []
enables: [all-crown-jewels]
session_notes: |
  Initial PLAN phase complete. Spec written for multi-session deep audit
  to consolidate kgents into unified substrate achieving autopoiesis.
  2025-12-17: Enhanced with ANNIHILATION MANDATE—aggressive culling of
  everything except categorical foundation and principles.
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.07
  spent: 0.02
  returned: 0.0
---

# Autopoietic System Consolidation

> *"The system that cannot describe itself cannot improve itself."*
> *"Everything except the Ground can be rebuilt better."*

---

## Purpose

Design and execute a **multi-session deep audit** that consolidates kgents from 17+ disparate systems into a **unified substrate** where:

1. Building an agent = building a metaphysical app
2. Every agent can be chatted with, projected to web, or sold as SaaS
3. Systems and patterns are **discoverable via AGENTESE paths**, not tribal knowledge
4. The system achieves **autopoiesis**—self-interfacing and self-production

---

## The Annihilation Mandate

> *"The phoenix requires ash. Aggressive culling enables rebirth."*

### The Two Invariants (NEVER DELETE)

| Invariant | Location | Why Sacred |
|-----------|----------|------------|
| **Categorical Foundation** | `spec/c-gents/`, `impl/claude/agents/{poly,operad,sheaf}/` | The mathematical ground truth |
| **Principles + Personality** | `spec/principles.md` | Kent's voice, values, and design philosophy |

**Everything else is fair game for annihilation.**

### Mandate 1: Aggressive Spec/Impl Culling

Any spec or implementation meeting these criteria **SHALL be deleted, not refactored**:

| Criterion | Threshold | Action |
|-----------|-----------|--------|
| **Bloat ratio** | Impl > 4× spec size | Delete impl, regenerate from spec |
| **Spec rot** | Impl diverged >50% from spec | Delete both, write fresh spec |
| **Orphan impl** | No corresponding spec | Delete impl |
| **Dead spec** | No impl for >30 days | Archive spec |
| **Complexity smell** | >500 LoC without operad structure | Delete, rebuild with operads |
| **Test desert** | <30% coverage, no property tests | Delete, rebuild test-first |

**The Regeneration Principle**: If it can be rebuilt better in 2 hours with the new foundation, delete it now.

### Mandate 2: Aggressive Documentation Archiving

| Type | Archive If | Target |
|------|-----------|--------|
| **Plans** | >14 days since last touch, <80% complete | `plans/_archived/` |
| **Docs** | Describes deleted system | `docs/_archived/` |
| **Skills** | Duplicates another skill, or targets deleted system | `docs/skills/_archived/` |
| **Prompts** | References archived agents | `prompts/_archived/` |
| **ADRs** | Superseded by newer AD | Archive in principles.md footnote |

**Archive format**: `{filename}.archived-{date}.md`

### Mandate 3: The Culling Audit

Each audit session SHALL include a culling phase:

```bash
# The Culling Checklist (run every session)
1. Identify 3 files that could be deleted
2. For each: "Can this be rebuilt better with categorical foundation?"
3. If yes: delete immediately, don't "save for later"
4. If no: document why in this plan's SACRED section
```

### The SACRED Section

Files explicitly protected from culling (justify each):

| File | Justification |
|------|---------------|
| `spec/principles.md` | Core identity—Kent's voice |
| `spec/c-gents/*.md` | Mathematical foundation |
| `impl/claude/agents/poly/core.py` | PolyAgent implementation |
| `impl/claude/agents/operad/core.py` | Operad implementation |
| `impl/claude/agents/sheaf/core.py` | Sheaf implementation |
| `plans/meta.md` | Distilled learnings (compression) |
| `CLAUDE.md` | Session context (regenerated) |

**To add to SACRED**: Requires explicit justification in a session note.

---

## The Core Insight

**The infrastructure exists. The problem is not capability—it is coherence.**

kgents has:
- PolyAgent/Operad/Sheaf categorical foundation
- AGENTESE verb-first ontology with 559 tests
- 7 Crown Jewels as services
- Projection Protocol for multi-target rendering
- N-Phase lifecycle for human-agent collaboration
- AD-009 (Metaphysical Fullstack Agent) defining the stack

What's missing:
- **Single entry point** that proves the unified vision works
- **Discoverable wiring** so agents self-interface
- **Template that generates all three modes** (chat, web, SaaS)

---

## Formal Definition (The Audit as N-Phase Cycle)

This audit is itself an 11-phase cycle, but **meta-applied**: each phase audits the system rather than building features.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AUDIT PHASES (N-Phase Meta-Application)                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PLAN            Define audit scope: which files, which patterns            │
│      ↓                                                                      │
│  RESEARCH        Inventory: impl/, docs/, spec/ cross-references            │
│      ↓                                                                      │
│  DEVELOP         Map: actual wiring vs. ideal AD-009 stack                  │
│      ↓                                                                      │
│  STRATEGIZE      Prioritize: which consolidations unlock autopoiesis        │
│      ↓                                                                      │
│  CROSS-SYNERGIZE Identify: Crown Jewel interdependencies                    │
│      ↓                                                                      │
│  IMPLEMENT       Execute: per-session consolidation tasks                   │
│      ↓                                                                      │
│  QA              Verify: AGENTESE paths resolve correctly                   │
│      ↓                                                                      │
│  TEST            Automated: conformance suite proves consolidation          │
│      ↓                                                                      │
│  EDUCATE         Document: update systems-reference.md + skills             │
│      ↓                                                                      │
│  MEASURE         Metrics: path discoverability, test coverage, LoC          │
│      ↓                                                                      │
│  REFLECT         Distill: what patterns emerged? update meta.md             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part I: PLAN Phase (Complete)

### 1.1 Key Questions to Resolve

| Question | Why It Matters |
|----------|----------------|
| What is the "reference agent"? | Need ONE agent that demonstrates all three modes (chat, web, SaaS) |
| Which systems are redundant? | Terrarium archived, but are there others? |
| What is the minimal AGENTESE surface? | 58 paths across 7 jewels—is this discoverable? |
| Where does TableAdapter belong? | AD-009 says services/, but current code mixed |
| How does autopoiesis manifest? | `kg self.system.manifest` should describe the system |
| **What can be annihilated?** | Most systems; identify categorical survivors |

### 1.2 Research Targets (Session 2)

| Target | Files to Audit | Purpose |
|--------|----------------|---------|
| **AGENTESE Wiring** | `protocols/agentese/`, `services/*/node.py` | Map all registered nodes |
| **Projection Gaps** | `agents/i/reactive/`, `protocols/projection/` | What projects where? |
| **Service Consistency** | `services/*/persistence.py`, `services/*/node.py` | Do all jewels follow AD-009? |
| **Crown Jewel Readiness** | `services/{brain,town,park,atelier,gestalt,gardener,morpheus}/` | Test density, AGENTESE coverage |
| **Categorical Foundation** | `agents/{poly,operad,sheaf}/` | Used vs. declared |
| **Spec-Impl Drift** | Compare `spec/protocols/*.md` to `impl/claude/protocols/` | What's specified but not built? |
| **ANNIHILATION CANDIDATES** | All of `impl/`, `spec/`, `docs/`, `plans/` | Apply culling criteria |

### 1.3 Creative Angles

**Category-Theoretic Lens:**
- The system IS an agent (meta-agent)
- `self.system.*` path should exist
- **Autopoiesis = `self.system.manifest` >> `self.system.evolve` >> `self.system.manifest`** (identity modulo improvement)

**Holonic Lens:**
- System → Jewel → Service → Node → Aspect
- Each level is both whole and part
- Audit must respect this hierarchy

**Puppet Lens:**
- The "kgents as OS" metaphor (OS Shell)
- Can we hot-swap to "kgents as City" (Town) or "kgents as Garden" (Gardener)?
- Puppet isomorphism should validate

**Accursed Share:**
- What got archived that shouldn't have?
- What exists that should be archived?
- Where is the creative chaos being suppressed?

---

## Part II: Session Plan (Revised with Annihilation)

### Session 1: Foundation Verification ✓
- [x] Read principles.md
- [x] Read n-phase-cycle.md
- [x] Read systems-reference.md
- [x] Read projection.md
- [x] Read agentese.md
- [x] Read meta.md learnings
- [x] Write this spec
- [x] Add Annihilation Mandate

### Session 2: The Great Inventory + First Culling
**Purpose**: Know what exists, then kill what doesn't deserve to.

**Inventory Phase** (2 hours):
- Enumerate all `@logos.node()` registrations
- Map path → service → persistence
- Count LoC for each system in impl/
- List all plans with last-touched dates
- List all docs with reference targets

**Culling Phase** (1 hour):
- Apply Mandate 1 criteria to every impl/ directory
- Apply Mandate 2 criteria to every plan
- **Deliverable**: `ANNIHILATION_REPORT.md` with:
  - Files to delete (with justification)
  - Files to archive (with justification)
  - Survivors and why
- **Execute**: Delete/archive immediately

### Session 3: Spec Purge + Minimal Core
**Purpose**: Reduce spec/ to the generative minimum.

**Audit**:
- For each spec file: Does an impl exist? Is impl faithful?
- For each spec: Is it < 400 LoC? (spec-hygiene.md principle)
- For each spec: Does it reference categorical foundation?

**Culling**:
- Archive specs with no impl
- Archive specs that don't use PolyAgent/Operad/Sheaf concepts
- Merge duplicate specs into single authoritative version
- **Deliverable**: `spec/` reduced by ≥40%

### Session 4: Crown Jewel Triage
**Purpose**: Which jewels survive? Which are rebuilt?

For each jewel, score:
| Criterion | Weight |
|-----------|--------|
| Uses PolyAgent | 3 |
| Uses Operad | 3 |
| Has Sheaf coherence | 2 |
| AGENTESE node exists | 2 |
| Test coverage >50% | 2 |
| <500 LoC | 1 |

**Decision Table**:
| Score | Decision |
|-------|----------|
| ≥10 | Keep, polish |
| 6-9 | Rebuild from spec |
| <6 | **ANNIHILATE**, rebuild from scratch |

- **Deliverable**: Jewel survival matrix

### Session 5: Reference Agent (Reborn)
- Pick surviving jewel with highest score (likely Town or Brain)
- If needed, rebuild from scratch using categorical foundation
- Prove: chat, web, SaaS all work
- **Deliverable**: Working reference agent (≤500 LoC)

### Session 6: Cascading Rebuild
- Apply reference agent pattern to next 2 surviving jewels
- Delete old implementations after new ones work
- Update CLAUDE.md to reflect reduced system
- **Deliverable**: 3 working jewels, everything else archived

### Session 7: Autopoiesis from Ash
- Implement `self.system.*` paths on the reduced system
- System describes its own (smaller, cleaner) architecture
- Prove: `kg self.system.manifest` shows the new structure
- **Deliverable**: Self-describing phoenix system

---

## Part III: AGENTESE Integration

### New Paths to Implement

```
self.system.manifest      # What is kgents? (projection)
self.system.audit         # What needs fixing? (perception)
self.system.evolve        # Apply consolidation (mutation)
self.system.witness       # History of changes (N-gent)
```

### Composition with Existing Agents

The audit uses existing agents:
- **N-Phase**: This document follows the cycle
- **Gardener-Logos**: Tends the spec garden
- **M-gent**: Records learnings in meta.md crystals
- **F-gent**: Chat interface for audit sessions

### Laws That Must Hold

| Law | Requirement |
|-----|-------------|
| **Identity** | `self.system.manifest` returns same structure before/after audit |
| **Associativity** | Audit sessions can be reordered (with dependency respect) |
| **Composability** | Each audit deliverable can be used independently |

---

## Part IV: Risks and Tensions

| Risk | Mitigation |
|------|------------|
| **Scope creep** | Strict 7-session cap; further work becomes new plan |
| **Breaking changes** | Each session produces reversible PR |
| **Losing learnings** | Update meta.md after each session |
| **Paralysis by analysis** | Session 5 forces implementation |
| **Autopoiesis as buzzword** | Define operationally: system invokes itself successfully |

---

## Part V: Anti-Patterns

**What this audit is NOT:**

| Anti-Pattern | Why Wrong |
|--------------|-----------|
| ~~Complete rewrite~~ | ~~Infrastructure exists; consolidate, don't replace~~ **REVISED**: Complete rewrite IS valid if the foundation survives |
| **More new systems** | Goal is fewer systems, not more |
| **Documentation-only** | Session 5 forces implementation |
| **Single-session** | Multi-session is the point; context preservation |
| **Feature work disguised as audit** | Audit audits; features come after |
| **"Save it for later"** | If it deserves deletion, delete NOW |
| **Refactoring bloat** | Don't polish—annihilate and rebuild |
| **Sentimental preservation** | Attachment to code is the enemy of quality |
| **Premature archiving** | Archive only after replacement works |

### The Psychology of Annihilation

**Why we hesitate to delete:**
- "Someone might need it" → If they do, rebuild it better
- "It took effort to create" → Sunk cost fallacy
- "It mostly works" → Mostly isn't good enough
- "The tests pass" → Tests can be wrong

**Why deletion is virtuous:**
- Every line deleted is a line that can't break
- Every system removed is cognitive load lifted
- The foundation (PolyAgent/Operad/Sheaf) is the only true asset
- Everything else is derived—and derivation is cheap with good tools

**The Litmus Test:**
> "If I had to explain this to a new contributor, would I be proud or embarrassed?"
>
> If embarrassed: **annihilate.**

---

## Part VI: Success Criteria

### Exit Criteria for Full Audit

**Quantitative (Revised for Annihilation):**
- ~~All 7 Crown Jewels follow AD-009 stack~~ **≤5 Crown Jewels survive**, all following AD-009
- `self.system.manifest` returns valid projection
- ~~AGENTESE path coverage ≥ 80% of services~~ **100% coverage of surviving services**
- systems-reference.md accurately describes the **reduced** system
- **impl/ reduced by ≥50% LoC**
- **spec/ reduced by ≥40% files**
- **plans/ reduced to ≤10 active plans**
- **docs/ reduced by ≥30% files** (archived, not lost)

**Qualitative:**
- New contributor can find correct system in <2 minutes
- Building new agent follows template
- Chat/Web/SaaS modes work from single definition
- **"The codebase is smaller than it was"**
- **"I could explain the whole system in 10 minutes"**
- **"Everything uses PolyAgent/Operad/Sheaf"**

### The Phoenix Metric

```
Autopoiesis Score = (Categorical primitives used) / (Total systems)

Target: ≥0.9 (90% of surviving code uses the foundation)
```

**Current estimate**: ~0.3 (too many systems don't use the foundation)
**Target after annihilation**: ≥0.9

---

## Auto-Continuation

```markdown
⟿[RESEARCH]
/hydrate
handles: scope=system_consolidation; chunks=[agentese_surface, projection_gaps, jewel_consistency, reference_agent, consolidation, autopoiesis]; exit=self_describing_system; ledger={PLAN:touched}; entropy=0.07
mission: audit impl/claude/protocols/agentese/ for all @logos.node() registrations; cross-reference with services/*/node.py; produce surface map
actions: parallel Grep("@logos.node", impl/), Read(services/*/node.py); produce docs/audit/agentese-surface.md
exit: surface map complete; continue to DEVELOP for gap analysis
```

---

## The Annihilation Creed

> *"The sculptor does not add clay; the sculptor removes what is not the statue."*
>
> *"The foundation remains. Everything else is kindling for the phoenix."*
>
> *"If you can rebuild it better in 2 hours, delete it in 2 seconds."*

**The form that generates forms is itself a form. The audit that enables autopoiesis is itself autopoietic.**

**What survives the annihilation IS the system.**
