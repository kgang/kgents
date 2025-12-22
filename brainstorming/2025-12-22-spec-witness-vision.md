# Spec Witness: The Living Accountability Graph

> *"Marks are the atomic unit of agency. Witness is the substrate beneath all other jewels."*

**Date:** 2025-12-22
**Status:** Brainstorming — Anti-Sausage Interview Synthesis
**Participants:** Kent + Claude
**Heritage:** Agent-as-Witness, Symmetric Supersession, Bloomberg Terminal, Research Paper Margins

---

## I. The Genesis: Anti-Sausage Interview

This document emerged from a structured interview to recover creative vision that had been diluted through rushed implementation. The handoff flagged: *"implementation rushed, vision diluted."*

### The Questions That Revealed the Vision

| Question | Kent's Answer | Insight Extracted |
|----------|---------------|-------------------|
| What makes Witness the exemplar? | "Marks are the atomic unit of agency — Witness is the substrate beneath all other jewels" | Witness is foundational, not a feature |
| How do Portal Node, Interactive Text, Meaning Tokens relate? | "Witness is both player and system. We could think of all of kgents through witness" | Witness is self-referential: observes AND is observed |
| What's missing from current dashboard? | "More density of information and durable proof. Evidence of usage and incorporation into ASHC" | Joy comes from proof-of-life, not animations |
| What density model? | "Bloomberg terminal and research paper margin notes" | Dense, every-pixel-earns-its-place |
| How should ASHC integrate? | "Decisions from kg decide should be obligations. Marks become substrate evidence for claims/warrants" | Toulmin structure: Claim → Warrant → Evidence |
| What's the minimum lovable version? | "An enumeration of all specs broken into upstream principles/evidence and downstream accountability/implementation/correctness proofs" | The Spec Witness |

### The Core Reframe

The original Witness dashboard vision was about *aesthetics* — breathing animations, earth tones, organic transitions. Kent redirected to *proof-of-life* — dense information showing that witnessing actually matters.

**Before:** "Does it feel like a garden?"
**After:** "Does it show that the garden is growing?"

---

## II. The Vision: Spec Witness

### The One-Sentence Summary

**A Bloomberg-terminal-density view showing every spec in the codebase, with upstream lineage (principles, marks, decisions) and downstream accountability (implementations, tests, ASHC proofs).**

### The Visual Mental Model

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ SPEC WITNESS                                                      │▓▓▓░░ 73%│
│ "The proof IS the decision. The mark IS the witness."                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ╔═══════════════════════════════════════════════════════════════════════════╗ │
│  ║ AD-002: Polynomial Generalization                               WITNESSED ║ │
│  ╠═══════════════════════════════════════════════════════════════════════════╣ │
│  ║                                                                           ║ │
│  ║  ┌─ UPSTREAM ──────────────────────┐ ┌─ DOWNSTREAM ─────────────────────┐ ║ │
│  ║  │                                 │ │                                  │ ║ │
│  ║  │ PRINCIPLES                      │ │ IMPLEMENTATIONS                  │ ║ │
│  ║  │ ┌────────┐ ┌──────────────┐    │ │  ✓ agents/poly/agent.py         │ ║ │
│  ║  │ │ P5     │ │ P6           │    │ │  ✓ agents/poly/operad.py        │ ║ │
│  ║  │ │Compose │ │Heterarchical │    │ │  ✓ agents/poly/sheaf.py         │ ║ │
│  ║  │ └────────┘ └──────────────┘    │ │                                  │ ║ │
│  ║  │                                 │ │ TESTS                            │ ║ │
│  ║  │ EVIDENCE (marks)                │ │  ✓ 47 passing                    │ ║ │
│  ║  │ ┌─────────────────────────────┐ │ │                                  │ ║ │
│  ║  │ │ mark-a1b2: "Kent wanted     │ │ │ ASHC PROOFS                      │ ║ │
│  ║  │ │ mode-dependent behavior..." │ │ │  ✓ Identity law (Lean4 #7f2a)   │ ║ │
│  ║  │ │                             │ │ │  ✓ Associativity (Lean4 #8b3c)  │ ║ │
│  ║  │ │ mark-c3d4: "Claude showed   │ │ │  ⏳ Composition (in progress)   │ ║ │
│  ║  │ │ polynomial functors..."     │ │ │                                  │ ║ │
│  ║  │ └─────────────────────────────┘ │ │                                  │ ║ │
│  ║  │                                 │ │                                  │ ║ │
│  ║  │ DECISIONS (kg decide)           │ │ OBLIGATIONS                      │ ║ │
│  ║  │ ┌─────────────────────────────┐ │ │  ✓ All category laws verified   │ ║ │
│  ║  │ │ decide-e5f6: "Use poly      │ │ │  ✓ Discharged by test evidence  │ ║ │
│  ║  │ │ over simple Agent[A,B]"     │ │ │                                  │ ║ │
│  ║  │ └─────────────────────────────┘ │ │                                  │ ║ │
│  ║  └─────────────────────────────────┘ └──────────────────────────────────┘ ║ │
│  ╚═══════════════════════════════════════════════════════════════════════════╝ │
│                                                                                 │
│  [+ 12 more specs...]                                                           │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  13 specs │ 7 witnessed │ 4 open │ 2 in-progress │ 89% accountability          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### The Philosophical Foundation

**Witness as Substrate:**
```
         ┌─────────────────────────────────────────┐
         │     Brain  Town  Atelier  Liminal  ...  │  ← Crown Jewels
         └─────────────────────────────────────────┘
                           │
                    emit marks, query marks
                           │
         ┌─────────────────────────────────────────┐
         │              W I T N E S S              │  ← The Ground
         │   (substrate of all agent behavior)     │
         └─────────────────────────────────────────┘
```

**Witness as Player-and-System:**
```
Witness observes Brain → emits mark
Witness observes itself observing → emits meta-mark
Witness IS the system AND plays within it
(heterarchical, self-referential, but not solipsistic)
```

---

## III. The Toulmin Structure

Kent's key insight: *"Decisions from kg decide should be obligations. Marks become substrate evidence to create claims or warrants."*

This maps directly to Toulmin argumentation:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           TOULMIN STRUCTURE                                      │
│                                                                                  │
│  CLAIM: "AD-002 (Polynomial Generalization) is correctly implemented"           │
│                                                                                  │
│  WARRANT: "The category laws hold for PolyAgent composition"                    │
│     └── (sourced from spec/principles.md §5 Composable)                         │
│                                                                                  │
│  EVIDENCE:                                                                       │
│     ├── mark-a1b2: Kent's original need for mode-dependent behavior             │
│     ├── mark-c3d4: Claude's proof that polynomial functors solve this           │
│     ├── decide-e5f6: Joint decision to adopt polynomial approach                │
│     ├── test results: 47 tests passing in agents/poly/_tests/                   │
│     └── ASHC proof: Identity and associativity verified in Lean4                │
│                                                                                  │
│  QUALIFIER: "with confidence 0.95"                                              │
│     └── (computed from evidence diversity + proof strength)                      │
│                                                                                  │
│  REBUTTAL CONDITIONS:                                                           │
│     └── "Unless composition law fails under new edge case"                      │
│     └── "Unless ASHC proof is found to have soundness gap"                      │
│                                                                                  │
│  DISCHARGE STATUS: WITNESSED (all evidence present, proofs verified)            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### The Three Levels of Durable Proof

Kent validated all three forms:

| Level | Description | Example |
|-------|-------------|---------|
| **Causal Chain** | mark → decision → code → tests | mark-a1b2 → decide-e5f6 → agent.py → test_poly_laws |
| **Formal Verification** | ASHC proofs that reference marks | Lean4 proof #7f2a citing decide-e5f6 as obligation source |
| **Aggregated Patterns** | This kind of mark tends to lead to this outcome | "Polynomial decisions have 100% test success rate" |

---

## IV. The Density Model

### Bloomberg Terminal

Kent said: *"Bloomberg terminal"* — this means:

- **Every pixel earns its place**: No decorative whitespace
- **Information-dense**: Multiple data points visible at once
- **Scannable**: Patterns visible at a glance
- **Drill-down capable**: Click for more detail, but overview is useful standalone
- **Real-time**: Status updates as marks and proofs arrive

### Research Paper Margin Notes

Kent said: *"Research paper margin notes"* — this means:

- **Primary content in center**: The spec itself
- **Annotations in margins**: Upstream/downstream as side panels
- **Hypertext links**: Principle badges, mark references, file paths are all clickable
- **Layered detail**: Hover for preview, click for full content

### The Hybrid Model

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                                                                               │
│  ┌── MARGIN ──┐  ┌────────────── PRIMARY ──────────────┐  ┌── MARGIN ──┐    │
│  │            │  │                                      │  │            │    │
│  │ UPSTREAM   │  │  AD-002: Polynomial Generalization   │  │ DOWNSTREAM │    │
│  │            │  │                                      │  │            │    │
│  │ Principles │  │  "Agents SHOULD generalize from      │  │ Impl files │    │
│  │ [P5] [P6]  │  │   Agent[A,B] to PolyAgent[S,A,B]    │  │ Test count │    │
│  │            │  │   where state-dependent behavior     │  │ Proof IDs  │    │
│  │ Evidence   │  │   is required."                      │  │            │    │
│  │ mark-a1b2  │  │                                      │  │ Status     │    │
│  │ mark-c3d4  │  │  [Full spec text expandable...]      │  │ WITNESSED  │    │
│  │            │  │                                      │  │            │    │
│  └────────────┘  └──────────────────────────────────────┘  └────────────┘    │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## V. The Hypergraph Model

### Typed Hypergraph via Meaning Tokens

Kent said: *"Incorporate new meaning tokens and links to implement the spirit of a hypergraph like a hypertext document."*

The existing POCs provide the building blocks:

| POC | Contribution |
|-----|--------------|
| `InteractiveTextGallery` | MeaningTokenRenderer, principle badges, AGENTESE portals |
| `Portal Page` | Tree exploration, file path navigation, collaboration events |
| `Trail Page` | Evidence strength badges, step reasoning, force-directed graph |

### Token Types for Spec Witness

```typescript
// Principle reference badge
{
  token_type: 'principle_ref',
  token_data: { principle_number: 5, name: 'Composable' },
  affordances: [{ name: 'expand', action: 'click', handler: 'show_principle' }]
}

// Mark reference
{
  token_type: 'mark_ref',
  token_data: { mark_id: 'mark-a1b2c3d4', action: 'Kent wanted mode-dependent...' },
  affordances: [{ name: 'preview', action: 'hover' }, { name: 'navigate', action: 'click' }]
}

// Decision reference
{
  token_type: 'decision_ref',
  token_data: { fusion_id: 'decide-e5f6', synthesis: 'Use polynomial...' },
  affordances: [{ name: 'expand', action: 'click', handler: 'show_dialectic' }]
}

// Implementation file reference
{
  token_type: 'file_ref',
  token_data: { path: 'agents/poly/agent.py', status: 'implemented' },
  affordances: [{ name: 'open', action: 'click', handler: 'open_portal' }]
}

// ASHC proof reference
{
  token_type: 'proof_ref',
  token_data: { proof_id: 'lean4-7f2a', law: 'identity', status: 'verified' },
  affordances: [{ name: 'expand', action: 'click', handler: 'show_proof' }]
}

// Obligation status
{
  token_type: 'obligation_status',
  token_data: { status: 'witnessed' | 'open' | 'in_progress', confidence: 0.95 },
  affordances: []  // Display only
}
```

### The Hypergraph Structure

```
         ┌──────────────────┐
         │    SPEC NODE     │
         │    (AD-002)      │
         └────────┬─────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌───────┐    ┌────────┐    ┌────────┐
│ P5    │    │ P6     │    │mark-a1b│
│Compose│    │Heterar.│    │        │
└───────┘    └────────┘    └────────┘
                               │
                               ▼
                          ┌────────┐
                          │decide- │
                          │e5f6    │
                          └────┬───┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
    ┌────────┐            ┌────────┐            ┌────────┐
    │agent.py│            │47 tests│            │Lean4   │
    │        │            │passing │            │proof   │
    └────────┘            └────────┘            └────────┘
```

---

## VI. Building Blocks from Existing POCs

### From Trail Page (`/_/trail`)

**Reusable:**
- `TrailGraph` component (force-directed visualization)
- `ReasoningPanel` (step-by-step traces)
- `BudgetRing` (progress indicator)
- `getEvidenceColor()` function (strength → color mapping)
- Evidence strength computation

**Adapt for Spec Witness:**
- Trail steps → Spec upstream/downstream nodes
- Evidence strength → Obligation confidence
- Reasoning panel → Principle/mark annotations

### From Portal Page (`/_/portal`)

**Reusable:**
- `PortalTree` component (hierarchical exploration)
- `TrailPanel` (session trail tracking)
- `TrailIndicator` (step count + strength badge)
- Collaboration events tracking

**Adapt for Spec Witness:**
- File tree → Spec tree organized by context (agents/, protocols/, services/)
- Trail panel → Evidence trail for selected spec
- Collaboration events → Mark/decision events

### From InteractiveText Gallery (`/_/interactive-text`)

**Reusable:**
- `MeaningTokenRenderer` (universal token display)
- `AGENTESEPortal` (clickable path tokens)
- `BadgeToken` (principle/requirement badges)
- `PilotContainer` (demo card layout)
- Density comparison pattern

**Adapt for Spec Witness:**
- Principle badges → Upstream principle references
- AGENTESE portals → File path links
- Badge tokens → Obligation status indicators

---

## VII. Implementation Phases

### Phase 1: Data Layer — Spec Enumeration

**Goal:** Parse all specs and build the graph.

**Tasks:**
1. Create `SpecExtractor` class that parses `spec/**/*.md`
2. Extract from each spec:
   - Title and summary
   - Principles referenced (by pattern matching `[P1]`, `Tasteful`, etc.)
   - Laws declared (by pattern matching `| Law |`, `Identity`, `Associativity`)
   - File paths mentioned (by pattern matching `impl/`, `agents/`, etc.)
3. Build `SpecGraph` data structure:
   ```python
   @dataclass
   class SpecNode:
       id: str  # e.g., "AD-002"
       title: str
       summary: str
       upstream: UpstreamLinks
       downstream: DownstreamLinks
       obligation_status: ObligationStatus

   @dataclass
   class UpstreamLinks:
       principles: list[PrincipleRef]
       marks: list[MarkRef]  # From Witness database
       decisions: list[DecisionRef]  # From kg decide records

   @dataclass
   class DownstreamLinks:
       implementations: list[FileRef]
       tests: list[TestRef]
       proofs: list[ProofRef]  # From ASHC database
   ```
4. Create API endpoint: `GET /api/witness/specs` → SpecGraph

**Deliverable:** `services/witness/spec_graph.py` + API endpoint

### Phase 2: Witness Integration — Substrate Connection

**Goal:** Connect specs to marks, decisions, and ASHC proofs.

**Tasks:**
1. Query Witness database for marks that reference specs:
   ```python
   async def find_marks_for_spec(spec_id: str) -> list[Mark]:
       return await witness.query(
           tags=["decision", "architecture"],
           grep=spec_id
       )
   ```
2. Query `kg decide` records that reference specs:
   ```python
   async def find_decisions_for_spec(spec_id: str) -> list[Fusion]:
       return await fusion.query(synthesis__contains=spec_id)
   ```
3. Query ASHC obligation database:
   ```python
   async def find_proofs_for_spec(spec_id: str) -> list[Proof]:
       return await ashc.query_obligations(source_spec=spec_id)
   ```
4. Compute obligation status:
   ```python
   def compute_obligation_status(spec: SpecNode) -> ObligationStatus:
       if all(proof.verified for proof in spec.downstream.proofs):
           return WITNESSED
       elif any(proof.in_progress for proof in spec.downstream.proofs):
           return IN_PROGRESS
       else:
           return OPEN
   ```

**Deliverable:** Witness integration in `services/witness/spec_bridge.py`

### Phase 3: Dense UI — Projection Layer

**Goal:** Bloomberg-style spec cards with margin annotations.

**Tasks:**
1. Create `SpecCard` component:
   ```typescript
   interface SpecCardProps {
     spec: SpecNode;
     density: 'compact' | 'comfortable' | 'spacious';
     onPrincipleClick: (p: PrincipleRef) => void;
     onMarkClick: (m: MarkRef) => void;
     onFileClick: (f: FileRef) => void;
     onProofClick: (p: ProofRef) => void;
   }
   ```
2. Create `UpstreamMargin` component:
   - Principle badges (using `BadgeToken` from InteractiveText)
   - Mark references (using new `MarkRefToken`)
   - Decision references (using new `DecisionRefToken`)
3. Create `DownstreamMargin` component:
   - File references (using `AGENTESEPortal` pattern)
   - Test count badge
   - Proof status badges
4. Create `ObligationIndicator` component:
   - WITNESSED: Green checkmark + confidence percentage
   - IN_PROGRESS: Yellow spinner
   - OPEN: Red open circle + missing evidence list
5. Create `SpecWitnessPage` component:
   - Header with summary stats
   - Filterable spec list
   - Detail panel for selected spec

**Deliverable:** `web/src/pages/SpecWitness.tsx` + components

### Phase 4: Hypergraph View — Visual Graph

**Goal:** Force-directed graph showing spec relationships.

**Tasks:**
1. Adapt `TrailGraph` for spec relationships
2. Node types:
   - Spec nodes (AD decisions)
   - Principle nodes
   - Mark nodes
   - Implementation file nodes
   - Proof nodes
3. Edge types:
   - `embodies`: Spec → Principle
   - `evidenced_by`: Spec → Mark
   - `decided_by`: Spec → Decision
   - `implemented_in`: Spec → File
   - `verified_by`: Spec → Proof
4. Layout:
   - Principles at top (upstream)
   - Specs in middle
   - Implementations at bottom (downstream)
5. Interactions:
   - Click node → Show detail panel
   - Hover node → Highlight connected nodes
   - Filter by principle/status

**Deliverable:** `web/src/components/witness/SpecGraph.tsx`

### Phase 5: Integration & Polish

**Goal:** Wire everything together, SSE streaming, mobile.

**Tasks:**
1. SSE streaming for real-time mark/proof updates
2. Mobile responsive layout (density adaptation)
3. Keyboard navigation (j/k for spec list)
4. Teaching mode callouts (explain Toulmin, explain obligation)
5. Integration tests
6. Performance optimization (virtualized list for many specs)

**Deliverable:** Production-ready Spec Witness page

---

## VIII. Open Questions

### Architectural

1. **Where does SpecExtractor live?**
   - Option A: `services/witness/spec_extractor.py` (Witness owns all accountability)
   - Option B: `services/archaeology/spec_extractor.py` (Archaeology owns codebase analysis)
   - **Lean toward A** — Witness is the substrate

2. **How do we detect mark→spec connections?**
   - Option A: Explicit tagging (`km "..." --spec AD-002`)
   - Option B: Pattern matching in mark content
   - Option C: LLM classification
   - **Start with B**, add A for precision

3. **What's the ASHC integration point?**
   - Need to query obligation database
   - Need to subscribe to proof completion events
   - **Depends on ASHC Phase 5 status** — may need stubs initially

### UX

4. **Default view: List or Graph?**
   - List is more Bloomberg (scannable)
   - Graph shows relationships better
   - **Start with List**, add Graph as toggle

5. **How much spec content to show inline?**
   - Just title + summary?
   - Full spec text expandable?
   - **Summary inline, full text in detail panel**

6. **Mobile experience?**
   - Bloomberg doesn't work on mobile
   - Need a different density mode
   - **Card stack for compact, list for comfortable**

### Scope

7. **Which specs to include?**
   - All `spec/**/*.md`?
   - Only AD decisions?
   - Only specs with implementations?
   - **Start with AD decisions**, expand to all specs

8. **What counts as "witnessed"?**
   - Just marks exist?
   - Tests pass?
   - ASHC proof verified?
   - **Tiered: marks = partial, tests = substantial, proof = full**

---

## IX. The Mirror Test

Before implementation, ask:

> *"Does this feel like Kent on his best day?"*
> *"Is it daring, bold, creative — or did I make it safe?"*
> *"Would Kent smile while using this?"*

The vision here is **daring**: We're building a system that watches itself, proves itself, and makes that proof visible. This is not a dashboard — it's a **living accountability graph**.

The density model is **bold**: Bloomberg terminal density in a world of whitespace-heavy UIs. Every pixel earns its place.

The substrate concept is **creative**: Witness isn't a feature — it's the ground everything else stands on. The metaphysics is operationalized.

---

## X. Next Steps

1. **Kent to review** this brainstorming doc
2. **Clarify open questions** (especially ASHC integration point)
3. **Prioritize phases** (which delivers value fastest?)
4. **Begin Phase 1** — Spec enumeration is foundational

---

*"The proof IS the decision. The mark IS the witness."*

---

**Filed:** 2025-12-22
**Anti-Sausage Status:** Vision recovered. Dense, proof-oriented, substrate-as-foundation.
**Heritage:** Agent-as-Witness spec, Symmetric Supersession articles, Bloomberg Terminal, Toulmin argumentation
