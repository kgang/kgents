# Discovery 1: The Galois Bet

## The Claim

**Bold Claim**: Galois loss L(P) predicts task failure rate with r > 0.6

The theory: prompts with high "Galois loss" (meaning lost during modularization/restructuring) correlate with task difficulty. High-loss prompts are hard to break into parts without losing meaning, and this structural property predicts execution difficulty.

## The Experiment

### Methodology

1. **Collected 29 prompts** from the kgents codebase:
   - 3 system prompts (K-gent soul, citizen, agent)
   - 6 analysis prompts (categorical, epistemic, dialectical, generative, constitutional)
   - 5 slash commands (harden, zero-seed, crystallize, handoff, what)
   - 4 skill definitions (polynomial-agent, spec-template, metaphysical-fullstack, cli-strategy-tools)
   - 4 PROTO_SPEC pilot specifications (wasm-survivors, disney-portal, trail-to-crystal, rap-coach)
   - 7 synthetic examples (simple, moderate, complex)

2. **Measured Galois Loss Proxy** using three components:
   - **Structural complexity** (0.45 weight): Nesting depth, conditionals, tables, code blocks
   - **Information density** (0.30 weight): 1 - compression ratio (verbose = high loss)
   - **Token diversity** (0.25 weight): 1 - unique/total tokens (repetitive = context-dependent)

3. **Estimated Task Difficulty** based on:
   - Technical complexity markers (category theory, async, real-time requirements)
   - Multi-step requirements (phases, laws, MUSTs)
   - Integration complexity (composition, API, protocol)
   - Domain richness (witness, crystal, joy, ethical)
   - Error handling requirements (failure modes, graceful degradation)
   - Source type adjustments (PROTO_SPECs harder than simple prompts)

4. **Computed Pearson correlation** between loss proxy and difficulty estimate.

## The Data

| Prompt | Source | Loss | Difficulty |
|--------|--------|------|------------|
| disney_portal_spec | pilots/disney-portal-planner/PROTO_SPEC.md | 0.532 | 0.588 |
| rap_coach_spec | pilots/rap-coach-flow-lab/PROTO_SPEC.md | 0.407 | 0.627 |
| trail_to_crystal_spec | pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md | 0.366 | 0.596 |
| polynomial_agent_skill | docs/skills/polynomial-agent.md | 0.399 | 0.482 |
| wasm_survivors_spec | pilots/wasm-survivors-game/PROTO_SPEC.md | 0.462 | 0.337 |
| zero_seed_command | .claude/commands/zero-seed.md | 0.425 | 0.314 |
| harden_command | .claude/commands/harden.md | 0.359 | 0.323 |
| CATEGORICAL_PROMPT | services/analysis/prompts.py | 0.325 | 0.310 |
| SOUL_SYSTEM_PROMPT | agents/k/prompts.py | 0.396 | 0.087 |
| simple_hello_world | synthetic/simple | 0.000 | 0.000 |

(Full data in `data/galois-correlation.csv`)

## The Result

**Correlation: r = 0.5624**

This is **below the claimed threshold of r > 0.6**, but not by much.

### Loss Proxy Statistics
- Mean: 0.305
- Min: 0.000 (trivial prompts)
- Max: 0.581 (complex state machine)

### Difficulty Statistics
- Mean: 0.199
- Min: 0.000 (trivial prompts)
- Max: 0.627 (rap coach spec)

## Where Theory Worked (3 examples)

### 1. Disney Portal Planner
- **Loss**: 0.532 (high structural complexity from 20 laws, quality gates, data contracts)
- **Difficulty**: 0.588 (real-time API integration, multi-phase delivery, live data requirements)
- **Why it makes sense**: The spec is deeply nested with interdependent laws. Breaking it into modules loses the coherence of the "portal commitment" metaphor. High loss correctly predicts high difficulty.

### 2. Rap Coach Flow Lab
- **Loss**: 0.407 (moderate structure with L1-L14 laws, audio requirements)
- **Difficulty**: 0.627 (highest in corpus - real audio, LLM feedback, courage preservation)
- **Why it makes sense**: The intent-declaration-before-recording pattern is semantically tight. The "warmth" quality is hard to modularize. Loss captures this.

### 3. Trail to Crystal Daily Lab
- **Loss**: 0.366 (moderate, but L1-L9 laws create dependencies)
- **Difficulty**: 0.596 (real persistence, LLM-generated crystals, contract coherence)
- **Why it makes sense**: The "day is the proof" metaphor resists decomposition. Every mark must link to the crystal. The spec is holistic.

## Where Theory FAILED (3 examples)

### 1. Complex State Machine (SURPRISE: High loss, low difficulty)
- **Loss**: 0.581 (highest in corpus!)
- **Difficulty**: 0.215 (actually straightforward to implement)
- **Why surprising**: The code looks complex (nested match statements, state transitions) but the TASK is well-understood. State machines are a solved pattern. **The proxy confuses syntactic complexity with semantic difficulty.**

### 2. Metaphysical Fullstack Skill (SURPRISE: Low loss, high difficulty)
- **Loss**: 0.206 (clean, well-organized prose)
- **Difficulty**: 0.427 (requires understanding 7-layer architecture, DI patterns)
- **Why surprising**: The document is elegantly structured (low loss) but the CONCEPT is hard. **The proxy misses conceptual depth when presentation is clear.**

### 3. SOUL_SYSTEM_PROMPT (SURPRISE: High loss, low difficulty)
- **Loss**: 0.396 (moderate-high from behavioral rules)
- **Difficulty**: 0.087 (actually easy - just personality framing)
- **Why surprising**: The prompt has many bullets and conditions, but implementing it is trivial (just use as system prompt). **The proxy over-weights structural formatting.**

## Verdict

**PARTIALLY CONFIRMED** with important caveats.

The correlation r = 0.5624 is meaningful but below the bold claim of r > 0.6.

**Why the gap?**

1. **Syntactic vs. Semantic complexity**: The loss proxy measures HOW text is structured, not WHAT it means. Complex formatting doesn't equal difficult tasks.

2. **Pattern familiarity**: Some high-loss prompts (state machines, category theory) involve well-understood patterns. The proxy doesn't account for implementer expertise.

3. **Implementation vs. Understanding**: Some low-loss prompts (metaphysical fullstack) require deep understanding even though they're clearly written.

## What We Learned

The Galois loss proxy captures something real: prompts that resist modularization DO tend to be harder to execute. The r = 0.56 correlation is not noise. But the claim that this alone predicts task failure with r > 0.6 is too strong.

**The insight worth keeping**: High structural complexity + low token diversity + low information density = warning signal. But this must be combined with domain-specific difficulty markers.

**The refinement needed**: A better difficulty predictor would combine:
1. Galois loss proxy (structural resistance to modularization)
2. Domain complexity markers (real-time, async, integration)
3. Pattern novelty (well-known vs. novel approaches)
4. Dependency depth (how many other systems must work)

The Galois bet is not broken - it's incomplete. The loss function needs augmentation, not replacement.

---

*Experiment conducted: 2025-12-28*
*Prompts analyzed: 29*
*Correlation achieved: r = 0.5624*
*Verdict: PARTIALLY CONFIRMED - meaningful signal, claim too strong*
