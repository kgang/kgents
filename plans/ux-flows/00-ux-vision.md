# UX Flows: Vision

> *"The system illuminates, not enforces. The user discovers, not configures."*

**Status**: Active Plan
**Date**: 2026-01-17
**Grounded In**: genesis-clean-slate.md, k-block.md, severe-stark.md
**Voice Anchor**: "Daring, bold, creative, opinionated but not gaudy"

---

## The Meta-Goal

**kgents must represent itself within itself.**

The decision hierarchy, specs, and implementation of kgents should be fully navigable, annotatable, and traceable within the kgents product. This is not documentation—it's **self-description as first-class content**.

When a user opens kgents for the first time, they don't see an empty slate. They see **the Constitutional Graph**—22 K-Blocks that derive from 4 axioms. They can trace how TASTEFUL derives from Judge + Mirror. They can see how ASHC implements GENERATIVE. They can understand the system by exploring it.

---

## The Radical Insight

**Traditional apps**: Empty state → Configure → Use → (eventually) Understand
**kgents**: Already-understood → Explore → Extend → Witness

The system *already knows* what it is. Genesis reveals this knowledge. The user's first action is not "fill in the blank" but "traverse the graph."

---

## The Five UX Pillars

### 1. Genesis: Self-Revealing First Run
The system teaches itself to the user through the Constitutional Graph. No questionnaires. No preferences. Just: "Here's what exists. Here's why. Now extend it."

### 2. Ingest: Documents → K-Blocks
Upload any document. The system proposes K-Block decomposition: axioms, principles, links, implementations. User confirms or refines. Every annotation is witnessed.

### 3. Navigate: Constitutional Traversal
Move through derivation paths. See what derives from what. Click an axiom, see everything it grounds. Click an implementation, trace back to its axiom.

### 4. Annotate: Rich Semantic Linking
Mark any text as: axiom, principle, gotcha, implementation, derivation link. Create edges between K-Blocks. The graph grows as you annotate.

### 5. Witness: Every Decision Traced
Every action leaves a mark. Every navigation creates a trail. The system knows what you explored, what you decided, why you decided it.

---

## The Flow Sequence

```
1. GENESIS (01-genesis-flow.md)
   └── First run → Constitutional Graph → Layer exploration → First extension

2. INGEST (02-ingest-flow.md)
   └── Upload → K-Block proposal → Annotation → Derivation linking

3. WORKSPACE (03-workspace-flow.md)
   └── Navigation → K-Block editing → View switching → Save to cosmos

4. DOGFOODING (04-dogfood-flow.md)
   └── kgents specs in kgents → Decision traces → Implementation links
```

---

## Design Constraints

| Constraint | Rationale |
|------------|-----------|
| **No empty states** | Genesis provides the Constitutional Graph |
| **No configuration** | Preference is death; exploration is life |
| **Dense over sparse** | SEVERE STARK: Yahoo Japan density |
| **Traced over anonymous** | Every action is witnessed |
| **Derived over declared** | Show derivation, not just content |

---

## Success Criteria

1. **First-run to first-extension < 5 minutes**
   User can create their first personal K-Block within 5 minutes of opening kgents

2. **Upload to annotated < 10 minutes**
   Any document can be decomposed into K-Blocks within 10 minutes

3. **Any node to axiom < 3 clicks**
   From any K-Block, user can trace to its axiomatic foundation in ≤3 navigations

4. **100% traceability**
   Every user action leaves a witness mark

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why Harmful |
|--------------|-------------|
| Empty dashboard | Blank canvas paralysis |
| Setup wizard | Interrogation before value |
| Sparse layout | Wastes screen, hides structure |
| Unmarked actions | History evaporates |
| Orphan content | K-Blocks without derivation |

---

*"The garden knows itself. The user discovers alongside."*
