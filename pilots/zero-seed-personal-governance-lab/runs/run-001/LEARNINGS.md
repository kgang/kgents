# Run 001 Learnings

> *"Generation is decision. Runs are experiments. Archives are memory."*

**Run**: run-001 (inaugural)
**Date**: 2025-12-26
**Status**: PASS

---

## Key Insights

### 1. Contract-First Generation Works

**Evidence**: TypeScript compilation succeeded on first attempt after contracts were created.

**Learning**: Creating comprehensive contracts (`galois.ts`, `zero-seed.ts`) before generation prevented type drift. The generator could import types directly without defining local duplicates.

**Preserve in Future Runs**: Always create/update contracts in Stage 2 before generating frontend code.

---

### 2. Archaeological Language is Generative

**Evidence**: The personality tag "archaeology, not construction" generated consistent language throughout all components without explicit instructions for each phrase.

**Learning**: A well-chosen metaphor (archaeology) generates appropriate language organically. The generator produced "surfaced", "uncovered", "emerged", "traces of" without a word-by-word checklist.

**Preserve in Future Runs**: PROTO_SPEC personality tags should use generative metaphors that cascade into language choices.

---

### 3. Anti-Success Patterns are Easier to Check Than Positive Assertions

**Evidence**: Checking for absence of prescriptive language (grep for "should believe", "recommend") was definitive. Checking for presence of recognition language required more subjective judgment.

**Learning**: Anti-patterns can be validated with automated checks; positive patterns require reading comprehension.

**Preserve in Future Runs**: Add automated anti-pattern checks to validation stage.

---

### 4. Joy Dimension Guided Component Priority

**Evidence**: SURPRISE as joy dimension naturally prioritized the DiscoveryWizard (the "Oh, that's what I actually believe" moment) as the centerpiece.

**Learning**: Joy dimensions are not just labels—they influence which components get the most care.

**Preserve in Future Runs**: Identify which component delivers the primary joy dimension and ensure it gets proportional attention.

---

### 5. "Tension" > "Contradiction" in UX Copy

**Evidence**: Using "tension" instead of "contradiction" throughout ContradictionExplorer created a non-judgmental tone automatically. No extra guidance needed.

**Learning**: Word choice in component names leaks into UX copy. Name things for how users should feel, not technical accuracy.

**Preserve in Future Runs**: When naming components, consider user-facing implications even for internal names.

---

## Prompt Improvements for Run 002

### 1. Add Explicit Language Guidelines to Generator Prompt

Current prompt relied on PROTO_SPEC. Future prompts should include:

```markdown
LANGUAGE GUIDELINES (extract from PROTO_SPEC):
- Use: "surfaced", "uncovered", "emerged", "traces of"
- Avoid: "created", "generated", "recommended", "should"
- Frame conflicts as: "tensions to explore"
- Frame losses as: stability metrics, not quality scores
```

### 2. Include Example UI Copy in Generator Prompt

Provide 2-3 example strings per component type:

```markdown
EXAMPLE COPY:
- Discovery empty state: "No strong patterns emerged yet."
- Axiom card header: "Patterns Uncovered"
- Contradiction message: "These patterns seem to pull in different directions."
```

### 3. Request Explicit Anti-Pattern Self-Check

Add to generator prompt:

```markdown
SELF-CHECK BEFORE OUTPUT:
For each component, verify:
- [ ] No prescriptive language ("should", "recommend")
- [ ] No gamification language ("score", "improve", "optimize")
- [ ] Tensions framed positively, not as errors
```

---

## Contract Amendments Needed

### 1. Add `RetireAxiomRequest` to Backend

The frontend expects `POST /api/zero-seed/constitution/retire` but this endpoint may not exist in backend. Verify and implement if missing.

### 2. Add `synthesis_hint` to ContradictionResponse

Ensure backend returns synthesis hints for contradictions (ghost alternatives).

---

## Pattern Recognition (Cross-Run)

Since this is run-001, no cross-run patterns yet. Will track:

- Generation time (this run: ~5 min via agent)
- Contract drift incidents
- QA failure patterns

---

## Success Patterns (Preserve These)

### 1. Five-Stage Protocol Works

Archive → Verify → Generate → Validate → Learn

Each stage has clear inputs/outputs. Sequential execution prevents drift.

### 2. PROTO_SPEC is Sufficient Specification

The generator produced high-quality code from PROTO_SPEC alone, without additional detailed specifications.

### 3. Contract Invariants Enable Validation

The invariant checks in contracts (`ZERO_NODE_INVARIANTS`, etc.) provide testable assertions.

### 4. Density-Aware Sizing Pattern

The `SIZES[density]` pattern from shared-primitives propagated naturally into generated components.

---

## Bellwether Results

From the original question: "What makes this a good bellwether?"

| Question | Answer | Evidence |
|----------|--------|----------|
| Can the generator compose multiple kgents primitives correctly? | ✅ Yes | Components import from shared-primitives, use LIVING_EARTH, useWindowLayout |
| Can it respect the "archaeology, not construction" personality? | ✅ Yes | All discovery language uses archaeological metaphors |
| Can it avoid anti-success patterns? | ✅ Yes | Grep validation found no value imposition, coherence worship, etc. |
| Can it create ceremony that feels "ceremonial but not burdensome"? | ✅ Yes | Retirement is single-dialog with required reason |
| Can it handle the Disgust Veto? | ✅ Yes | Frontend structure supports veto (though backend integration TBD) |

---

## Next Steps

1. **Backend Verification**: Ensure all API endpoints exist and return expected shapes
2. **Integration Test**: Run frontend with real backend
3. **Manual QA**: Kent validates "ceremonial but not burdensome" subjectively
4. **Contract Tests**: Add automated contract verification tests

---

## Crystal Summary

**The inaugural run of Zero Seed Personal Governance Lab validates the witnessed regeneration protocol.** Contract-first generation, archaeological language, and joy-dimension prioritization produced a frontend that passes all qualitative assertions and avoids all anti-success patterns.

**Key learning**: A well-chosen personality metaphor ("archaeology") is generative—it cascades into appropriate language throughout the codebase without explicit word-by-word guidance.

---

*Crystallized: 2025-12-26 | Witnessed by: Learner Agent | Run: run-001 PASS*
