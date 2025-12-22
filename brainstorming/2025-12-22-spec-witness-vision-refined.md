# Spec Witness: Assurance-Case Graph for kgents

> *"The proof IS the decision. The mark IS the witness."*

**Date:** 2025-12-22
**Status:** Brainstorming — Repo-Aware Rewrite
**Purpose:** Transform the existing Spec Witness vision into a repo-grounded, radically higher-fidelity plan for accountability.

---

## 0. Why This Rewrite Exists (Critical Audit Summary)

The original vision is strong, but it drifts away from what the repo already *has*. It reinvents graphs that already exist (Typed-Hypergraph, Trail), and it leaves the evidence system underspecified (marks vs decisions vs trace witnesses vs tests vs ASHC). This rewrite re-centers on the actual kgents substrate, then upgrades it into a true **assurance-case system** rather than a pretty dashboard.

### Repo Realities We Must Align With

- **Witness already exists** as a Crown Jewel with marks, lineage, crystallization, and a persistent event stream (`spec/services/witness.md`, `spec/protocols/witness-crystallization.md`).
- **Typed-Hypergraph already defines evidence edges** (`spec/protocols/typed-hypergraph.md`). Creating a separate SpecGraph duplicates the substrate.
- **Trail Protocol already models provenance & exploration** with Trail → Witness bridges (`spec/protocols/trail-protocol.md`).
- **TraceWitness is the real runtime proof primitive** used across verification and metatheory (`spec/services/verification.md`, `spec/protocols/metatheory.md`).
- **ASHC evidence economics exists** and should *set the confidence model*, not a new bespoke one (`docs/reference/ashc-compiler/ashc-compiler.md`).

### Hard Critiques of the Original Doc

- **Brittle extraction**: pattern-matching specs for principles/laws will fail. The repo already has typed hyperedges for `implements`, `supports`, `evidence`, etc.
- **Evidence conflation**: marks are not proofs, and tests are not proofs. The system needs explicit levels and escalation rules.
- **No provenance vocabulary**: The model needs stable types: *Entity, Activity, Agent* (see PROV-O) rather than ad-hoc terms.
- **UI-first drift**: A Bloomberg aesthetic without a hard accountability core is still decorative. The value is in **formal, queryable assurance cases**.

---

## 1. New Thesis: Spec Witness = Assurance Case Graph

Spec Witness is not a dashboard. It is a **living assurance case** for every spec: a structured argument that the spec is implemented and correct, grounded in trace witnesses, tests, marks, and proofs.

This aligns with established structures:

- **Toulmin**: Claim → Warrant → Evidence → Qualifier → Rebuttal
  - https://en.wikipedia.org/wiki/Toulmin_model_of_argument
- **GSN (Goal Structuring Notation)**: Goal → Strategy → Solution + Context/Assumptions
  - https://en.wikipedia.org/wiki/Goal_structuring_notation
- **IBIS**: Issue → Position → Argument (to capture decisions + alternatives)
  - https://en.wikipedia.org/wiki/Issue-based_information_system
- **PROV-O**: Entity / Activity / Agent for provenance
  - https://www.w3.org/TR/prov-o/
- **Data-Ink Ratio** (Tufte): density without chartjunk
  - https://en.wikipedia.org/wiki/Data-ink_ratio

**Translation into kgents**:

- **Goal/Claim** = Spec is correct and grounded
- **Strategy/Warrant** = Principles or laws that justify the spec
- **Solution/Evidence** = TraceWitness, tests, marks, decisions, proofs
- **Context/Assumptions** = Spec dependencies, known gaps, rebuttals
- **IBIS Issue** = The decision that created the spec (kg decide)

Spec Witness is therefore a **structured argument graph**, not just a set of links.

---

## 2. The Evidence Ladder (Non-Negotiable)

Evidence is stratified. Each level *unlocks the next*.

| Level | Name | Source | Meaning | Minimum Data |
|------:|------|--------|---------|--------------|
| L-1 | Trace Witness | Runtime trace capture | Actual behavior observed | `TraceWitness` with inputs/outputs |
| L0 | Mark | Human attention | Why it matters | `km` mark with tags + lineage |
| L1 | Test | Automated claim check | Repeatable evidence | Test run + artifact hash |
| L2 | Proof | Formal obligation discharge | Law verified | ASHC/Lean proof id |
| L3 | Economic Bet | Credibility stake | Confidence calibration | ASHC bet + settlement |

**Rule**: A spec cannot be "WITNESSED" without at least one L-1 TraceWitness or L1 test tied to the exact implementation artifact.

---

## 3. The Unified Provenance Model (PROV-O aligned)

Instead of bespoke node types, use a **minimal provenance core** that maps to existing protocols:

```text
Entity:  Spec, ImplementationFile, TestArtifact, ProofArtifact, Crystal
Activity: Decision, TestRun, TraceCapture, Crystallize, Compile
Agent:  HumanObserver, LLM, ToolingAgent, Service
```

### Standard Edges (reuse Typed-Hypergraph semantics)

- `implements` (ImplementationFile → Spec)
- `supports` (Evidence → Claim)
- `refutes` (Evidence → Claim)
- `derived_from` (Crystal → Mark/Trace)
- `generated_by` (Artifact → Activity)
- `attributed_to` (Activity → Agent)
- `depends_on` (Spec → Spec)

This is how we avoid a parallel graph. The **Typed-Hypergraph is the graph**.

---

## 4. Spec Witness Projection (What the UI Actually Shows)

### The Primary Surface: Assurance Ledger

A dense ledger is more honest than a fancy graph. Each row is a spec. Each column is evidence.

```
SPEC ID   TITLE                      L-1  L0  L1  L2  L3   STATUS  REBUTTALS
AD-002    Polynomial Generalization   2   7   47  2   1    WITNS   1
AD-003    Generative Operads          0   3   12  0   0    OPEN    4
...
```

- L-1: TraceWitness count
- L0: Mark count (lineage-aware)
- L1: Tests passing, with hashes
- L2: Proofs verified
- L3: Bets settled

**Row click** expands into a *structured argument view* (Toulmin + GSN), not a simple detail pane.

### Secondary Surface: Argument Graph

A directed graph *only after* the ledger, used for deep inspection:

```
[Claim] Spec AD-002 correct
  |--[Warrant] P5 Composable
  |--[Evidence] 47 tests passing
  |--[Evidence] TraceWitness #8f2a
  |--[Rebuttal] Edge case: async composition
```

### Tertiary Surface: Temporal Compression

Use Witness crystals as a **context summary** for a spec over time:

- A spec with 40 marks and 0 crystals is *noisy* and not understood.
- A spec with 3 crystals and 1 trace witness is *under-tested*.

---

## 5. The Spec Witness Engine (No New Graphs)

### 5.1 Data Sources (Already in Repo)

- Specs: `spec/**/*.md`
- Witness: marks, lineage, crystals (`services/witness/`)
- Trails: `services/witness/trail_bridge.py`
- Tests: test runs + artifacts (`impl/claude/.../_tests`)
- ASHC: proofs + bets (`docs/reference/ashc-compiler/ashc-compiler.md`)
- Typed-Hypergraph: path traversal + edges (`spec/protocols/typed-hypergraph.md`)

### 5.2 The Minimal Indexer (Replace SpecExtractor)

Instead of parsing Markdown, **index from hyperedges**:

1. `spec_node = ContextNode("world.spec.AD-002")`
2. Traverse `implements`, `tests`, `evidence`, `supports`, `refutes`
3. Join to Witness (marks, traces) via shared identifiers + tags

This makes the spec graph a **projection of the hypergraph**, not a parallel system.

---

## 6. Critical Decisions (Make Them Now)

### 6.1 Definition of "WITNESSED"

**Proposal**: A spec is WITNESSED only if it has:

- ≥1 L-1 TraceWitness OR ≥1 L1 test artifact
- ≥1 mark *or* decision referencing the spec
- ≥1 downstream implementation file linked via `implements`

If any of these are missing, status is **OPEN** or **IN PROGRESS**.

### 6.2 Evidence Integrity

All evidence items must be **content-addressed** (hash or ID). Otherwise, we cannot trust it.

### 6.3 Rebuttal Discipline

Every spec must allow rebuttals. A spec with no rebuttals is suspect. We need a standard place for:

- Known gaps
- Edge cases
- Unverified claims

---

## 7. Why This Is Radically Better

- **No parallel graph**: We leverage the Typed-Hypergraph, Trail, and Witness infrastructure already implemented.
- **Formal assurance case**: The system becomes inspectable and defendable, not just pretty.
- **Evidence economy**: Confidence is computed from ASHC evidence tiers and bets.
- **Temporal compression**: Crystals are first-class, reducing mark spam.
- **Repo fidelity**: Aligns with existing Crown Jewel architecture and protocols.

---

## 8. Implementation Path (Tight, Realistic, Non-Decorative)

### Phase 0 — Define the Evidence Ladder (1 day)

- Add `spec/protocols/spec-witness.md` (canonical definition)
- Document evidence tiers + required fields

### Phase 1 — Hypergraph Projection (2–3 days)

- Implement `services/witness/spec_projection.py`
- Build `SpecEvidenceIndex` using typed-hypergraph edges
- Output: JSON ledger

### Phase 2 — Assurance Ledger UI (3–5 days)

- Simple dense table (no graph yet)
- Filters: status, missing evidence, rebuttals

### Phase 3 — Argument View (2–4 days)

- Toulmin/GSN structured view on row expand
- Rebuttals and missing evidence highlighted

### Phase 4 — Economic Confidence (Optional)

- Integrate ASHC bets and settlement stats

---

## 9. Open Questions (Only the Hard Ones)

1. **Spec identifiers**: Do all specs have stable IDs? If not, who owns normalization?
2. **TraceWitness routing**: How do we tie runtime trace to a spec? Tagging? static mapping?
3. **Evidence loss**: What happens if a test artifact hash goes missing? Do we demote status?
4. **Rebuttal lifecycle**: Who owns rebuttals and how do they expire?

---

## 10. The Mirror Test (Updated)

> *Does this make the system more honest, or just more impressive?*

If the ledger shows an uncomfortable gap, that is success. The goal is not to look green; it is to show the truth of the system.

---

**Filed:** 2025-12-22
**Heritage:** Agent-as-Witness, Typed-Hypergraph, Trail Protocol, Toulmin, GSN, PROV-O, IBIS, Tufte
