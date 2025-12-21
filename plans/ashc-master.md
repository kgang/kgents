# ASHC Master Implementation Plan

> *"The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof."*

**Spec**: `spec/protocols/agentic-self-hosting-compiler.md`
**Phase**: IMPLEMENT (Phases 1-5 complete)
**Tests**: 408 passing (346 + 50 bootstrap regeneration + 12 integration)
**Session**: 2025-12-21

---

## Vision Grounding

🎯 **GROUNDING IN KENT'S INTENT:**

*"Daring, bold, creative, opinionated but not gaudy"*
*"The Mirror Test: Does K-gent feel like me on my best day?"*

ASHC is **not** a prompt generator. Writing prompts is easy—one shot is enough.

ASHC is a **trace accumulator** that gathers empirical evidence connecting spec to implementation. The "proof" that spec ↔ impl match is not mathematical—it's statistical, experimental, observed.

---

## The Failure We're Avoiding

**Evergreen Prompt System** (216 tests) solved the wrong problem. It over-engineered prompt generation with SoftSection, TextGRAD, rollback. But writing a good prompt is not hard.

**What IS hard:**
- Knowing if the agent will behave correctly in edge cases
- Verifying that spec matches what the agent actually does
- Building confidence that changes won't break things

These are **verification problems**, not generation problems.

---

## Core Architecture

```
Kent's Idea (Spec)
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│                    ASHC COMPILER                          │
│                                                          │
│  1. Generate N variations of the idea                    │
│  2. Run each through LLM → Implementation                │
│  3. Verify each with pytest, mypy, ruff                  │
│  4. Chaos test: compose variations combinatorially       │
│  5. Track causal relationships: nudge → outcome          │
│  6. Accumulate into evidence corpus                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
       │
       ▼
Agent Executable + Evidence Corpus
```

The Evidence Corpus is the "proof"—accumulated observation, not formal logic.

---

## Implementation Phases

### Phase 1: L0 Kernel + Pass Operad ✅ COMPLETE
**Effort**: ~7 sessions | **Status**: 47 tests

The minimal infrastructure:
- `L0Kernel` with primitives (compose, apply, match, emit, witness)
- Pass Operad with 6 bootstrap passes
- Composition laws verified
- ProofCarryingIR as the output type

See: `plans/ashc-l0-kernel.md`, `plans/ashc-pass-operad.md`

### Phase 2: Evidence Accumulation Engine ✅ COMPLETE
**Effort**: 1 session | **Status**: 103 tests passing

**The core of the new vision.** Built the machinery to:
- Run N variations of a spec
- Verify each with pytest/mypy/ruff
- Accumulate into Evidence corpus
- Compute equivalence scores

Key types (all implemented):
- `Run` — Single execution with test/type/lint results
- `Evidence` — Accumulated runs with `equivalence_score`
- `ASHCOutput` — Executable + Evidence + `is_verified`
- `EvidenceCompiler` — Main compilation loop

Key modules:
- `protocols/ashc/verify.py` — pytest/mypy/ruff runners
- `protocols/ashc/evidence.py` — Run, Evidence, EvidenceCompiler

### Phase 2.5: Adaptive Bayesian Evidence ✅ COMPLETE
**Effort**: 1 session | **Status**: 32 tests passing

**Major enhancement:** Instead of running fixed N variations, adaptively stop based on Bayesian confidence.

Key concepts implemented:
- **n_diff technique** — Stop when |successes - failures| ≥ n_diff margin
- **Beta-Binomial updating** — Conjugate prior: Beta(α,β) + data → Beta(α+s, β+f)
- **Confidence tiers** — TRIVIALLY_EASY, LIKELY_WORKS, UNCERTAIN, LIKELY_FAILS
- **LLM pre-verification** — Cheap prior from lightweight LLM estimate
- **Majority voting boost** — P(majority correct) for reliability amplification

Key types:
- `BetaPrior` — Beta distribution with Bayesian update
- `StoppingConfig` — n_diff, max_samples, confidence_threshold
- `StoppingState` — Tracks observations and stopping decision
- `AdaptiveCompiler` — Compile with adaptive stopping

Key module:
- `protocols/ashc/adaptive.py` — All adaptive Bayesian evidence types

Heritage: SPRT (Wald), BEACON (Bayesian LLM stopping), Evan Miller (sequential A/B)

### Phase 2.75: Economic Accountability ✅ COMPLETE
**Effort**: 1 session | **Status**: ~25 tests passing

**Skin in the game for ASHC decisions.** Added economic accountability:

Key types:
- `ASHCBet` — Wager on compilation outcome (confidence + stake)
- `ASHCCredibility` — Tracks accumulated credibility score
- `BetSettlement` — Resolution of a bet with payout logic
- `CausalPenalty` — Propagates blame to principles/evidence that caused failure
- `Adversary` — Implicit counterparty taking other side of bets

Key modules:
- `protocols/ashc/economy.py` — Betting and credibility tracking
- `protocols/ashc/adversary.py` — Adversarial accountability
- `protocols/ashc/causal_penalty.py` — Blame propagation to principles

Heritage: Prediction Markets, Skin in the Game (Taleb)

### Phase 3: Causal Graph Learning ✅ COMPLETE
**Effort**: 1 session | **Status**: 47 tests passing

**Vision Pivot**: Dropped Chaos Testing in favor of Causal Graph Learning. The Bayesian + Economic direction is about *efficient confidence*, not brute-force enumeration. Learning nudge → outcome relationships aligns with "the pattern of nudges IS the proof."

Key concepts implemented:
- **CausalEdge** — Tracked nudge → outcome relationship with confidence
- **CausalGraph** — Accumulated edges with prediction capability
- **CausalLearner** — Observes runs, builds causal graph
- **Similarity functions** — Find similar nudges for prediction
- **Causal Monotonicity Law** — Similar nudges should predict similar outcomes

Key module:
- `protocols/ashc/causal_graph.py` — All causal graph learning types

This complements Phase 2.75's causal_penalty.py:
- **causal_penalty**: "What caused this failure?" (retroactive blame)
- **causal_graph**: "What will this nudge do?" (proactive prediction)

### Phase 4: LLM Harness & Real Evidence ✅ COMPLETE
**Effort**: ~2 sessions | **Status**: 35 tests passing

**The missing piece**: All tests so far use deterministic functions. Real LLM calls produce real variation—only then can we test if Bayesian stopping actually saves tokens, build genuine causal graphs, and accumulate evidence that means something.

Key components (all implemented):
- **VoidHarness** — Isolated Claude CLI execution in temp directory (no CLAUDE.md context leakage)
- **TokenBudget** — Track and limit token usage across harness lifetime
- **compile_with_llm()** — Fixed-N compilation with real LLM evidence
- **adaptive_compile_with_llm()** — Bayesian stopping with real LLM
- **compile_with_nudges()** — For causal learning

See: `plans/_handoffs/ashc-phase4-llm-harness.md`

### Phase 5: Bootstrap Regeneration ✅ COMPLETE
**Effort**: ~2 sessions | **Status**: 50 tests passing

The ultimate self-hosting test: can ASHC regenerate its own bootstrap from specs?

Key components (all implemented):
- **SpecParser** — Parse `spec/bootstrap.md` into structured BootstrapAgentSpecs
- **IsomorphismChecker** — Verify behavioral equivalence between generated and installed
- **BootstrapRegenerator** — Full regeneration pipeline using VoidHarness
- **BehaviorComparison** — Multi-dimensional isomorphism scoring

See: `plans/ashc-phase5-bootstrap-regeneration.md`

### Phase 6: VoiceGate + Verification Tower (NEXT)
**Effort**: ~2-3 sessions | **Priority**: Medium

- VoiceGate: Trust-gated output (L0-L3)
- Verification Tower: Stack of verifiers (pytest → mypy → ruff → semantic)
- Evidence integration: Link VoiceGate decisions to causal graph

See: `plans/ashc-voice-verification.md`

---

## Quality Gates

| Checkpoint | Criteria | Verification |
|------------|----------|--------------|
| **Evidence Accumulation** | N runs produce Evidence | `len(output.evidence.runs) >= N` |
| **Verification Integration** | pytest/mypy/ruff run on each | All test reports populated |
| **Equivalence Score** | Computed from runs + causal | `score >= 0.8` for verified |
| **Causal Prediction** | Nudges predict outcomes | `|predicted - actual| < 0.1` |
| **Causal Monotonicity** | Similar nudges → similar outcomes | `graph.verify_causal_monotonicity()` |
| **Bootstrap Regeneration** | Self-hosting works | Generated ≅ Installed |

---

## Human Flow (Kent-Centered)

1. **Kent writes spec** in natural language with creative intent
2. **ASHC runs N variations** generating implementations
3. **ASHC verifies each** with pytest, mypy, ruff
4. **ASHC learns causal relationships** from nudge → outcome patterns
5. **ASHC accumulates evidence** into causal graph
6. **Kent reviews evidence**, not code
   - "95% pass rate across 100 variations"
   - "Stable under nudges: small changes don't break things"
   - "Causal insight: 'tasteful' correlates with +15% pass rate"
7. **Kent makes nudges** based on intuition + evidence
8. **Loop refines** until evidence is sufficient

**The lived effect:** Kent writes ideas, reviews evidence, makes nudges. The code is a byproduct.

---

## Technology Stack

The verification stack uses **the same tools we use**:

| Tool | What It Checks | ASHC Role |
|------|----------------|-----------|
| `pytest` | Behavior correctness | Primary evidence source |
| `mypy` | Type consistency | Structural soundness |
| `ruff` | Style/patterns | Compliance with conventions |
| `hypothesis` | Property-based | Chaos test generation |
| `git diff` | Change tracking | Nudge detection |

If these tools are good enough for us to verify our work, they're good enough for ASHC.

---

## Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Evidence runs per spec | ≥100 | Statistical significance |
| Equivalence score threshold | ≥0.8 | High confidence |
| Chaos pass rate | ≥0.95 | Stable under composition |
| Causal prediction accuracy | ≥0.9 | Nudges are predictable |
| Bootstrap regeneration | 100% equivalent | Self-hosting works |

---

## Anti-Patterns

- ❌ **One-shot compilation**: Running once and trusting the output. Evidence requires repetition.
- ❌ **Ignoring verification failures**: A failed test is data, not noise.
- ❌ **Manual code review**: The evidence corpus IS the review. Trust the process.
- ❌ **Formal proof obsession**: We're not doing Coq. We're doing science.
- ❌ **Prompt over-engineering**: Writing prompts is easy. Gathering evidence is hard.

---

## What We Keep from Phase 1

The Pass Operad infrastructure is still useful:
- **Passes as morphisms** — Structure for the generation step
- **ProofCarryingIR** — Each run produces witnesses
- **Composition laws** — Chaos testing exploits these

What changes:
- **Focus shifts** from generation to verification
- **Evidence** becomes the primary output, not just code
- **Causal tracking** is the new core insight

---

## Next Steps

1. Create `plans/ashc-evidence-engine.md` with Phase 2 detail
2. Implement Evidence, Run, ASHCOutput types
3. Wire pytest/mypy/ruff integration
4. Create the main compilation loop

---

*"We don't prove equivalence. We observe it."*

*"If you grow the tree a thousand times, the pattern of growth IS the proof."*
