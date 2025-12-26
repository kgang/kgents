# Constitutional Decision OS (Factory Vision)

**Status:** Vision Draft
**User:** Kent (single-user founder mode)
**Purpose:** Autonomous factory for digital products and SaaS, grounded in Constitutional, witnessed decisions.

---

## Persona and Profile (Evidence-Based)

This vision is adapted to Kent's demonstrated intent, voice, and working style, with evidence from the repo and git history.

**Voice anchors (direct quotes):**
- "Daring, bold, creative, opinionated but not gaudy" (CLAUDE.md)
- "Tasteful > feature-complete" (CLAUDE.md)
- "The persona is a garden, not a museum" (CLAUDE.md, README.md)
- "The Mirror Test: Does K-gent feel like me on my best day?" (CLAUDE.md, NOW.md)

**Evidence of behavior and preference:**
- The repo emphasizes *compression over sprawl* (spec/principles.md; spec-hygiene and spec-template skills).
- Strong bias toward deletion and simplification (git history shows large refactors and aggressive cleanup).
- Theory-first, UI-visible systems (NOW.md: theory-to-UI mapping; ValueCompass and Telescope primitives).
- The system is explicitly a metatheory for agents that justify their behavior (README.md).

**Git history signals (selected commit themes):**
- "refactor: Remove Forge API and related modules (~4,500 LOC)"
- "chore: Aggressive working docs cleanup (~200 files, 56K lines)"
- "refactor: K-gent & test cleanup (-2,452 LOC)"
These demonstrate a consistent preference for principled reduction and structural clarity.

**Persona summary:**
Kent values daring compression, explicit justification, and aesthetic coherence. The system must feel like a high-agency instrument, not a tool zoo. The factory must be autonomous yet accountable, bold yet tasteful, and always capable of passing the Mirror Test.

---

## Product Spec

### Problem / Job-to-be-Done
- Building digital products and SaaS requires sustained judgment, coherent decisions, and disciplined execution.
- Traditional agent frameworks automate tasks but do not justify decisions or preserve long-term coherence.
- Kent needs a single-user, autonomous factory that can generate, test, and ship products without drifting into slop.

### Audience
- **Primary user:** Kent (single founder, taste-driven, theory-first).
- **Secondary beneficiaries:** Future collaborators and clients who inherit the decision trail and system outputs.

### Value Proposition
A constitutional, witnessed decision engine that:
- Produces products via justifiable, composable decisions.
- Preserves agency and taste as a first-class constraint.
- Turns theory into a practical, repeatable factory loop.

### Core Insight
**A product factory is not a scheduler; it is a proof system.**
Every output (spec, code, UI, launch) must be a witnessed decision trace scored by constitutional value.

---

## System Overview (Factory Architecture)

### The Four Pillars
1. **Zero-Seed (Epistemic Kernel)**
   - Establishes the minimum axiom set that every product must derive from.
   - Prevents drift by forcing all product ideas through a fixed epistemic holarchy.

2. **K-Blocks (Sovereign Editing Worlds)**
   - Every product change occurs inside a transactional universe.
   - Only committed outputs enter the cosmos, preventing half-baked states from leaking.

3. **PolyAgent (Mode-Dependent Workflows)**
   - The factory is a state machine, not a chain.
   - Each phase exposes different affordances and inputs, avoiding orchestration rigidity.

4. **ValueAgent (Constitutional Reward)**
   - Every decision is scored against the seven principles.
   - The highest-value policy wins; the lowest-value path is discarded.

### Witness Integration (Decision Proof)
- Every action leaves a Mark.
- Every product becomes a PolicyTrace.
- Every outcome is justifiable, replayable, and auditable.

---

## Workflow: The Factory Loop

### 1) Seed
- Start from Zero-Seed axioms.
- A product idea must be derived, not invented.

### 2) Compose
- Compose agents into a product blueprint: Idea -> Spec -> Design -> Build -> Launch.
- Each step is a PolyAgent position with state-specific directions.

### 3) Prove
- ValueAgent evaluates decisions against constitutional reward.
- If the proof is weak, the system re-enters Compose.

### 4) Commit
- K-Block commits only when decision value and witness proof exceed thresholds.
- The cosmos receives a coherent, justified output.

### 5) Iterate
- Witness marks become training data for future products.
- The factory improves without losing its personality.

---

## PolyAgent State Model (Factory Positions)

**Positions (suggested):**
- `seed` -> `frame` -> `prototype` -> `validate` -> `ship` -> `learn`

**Key behavior:**
- Each position exposes different inputs and agent affordances.
- The factory does not accept development actions while in `seed` or `frame`.
- The factory does not allow shipping actions without Witness proof.

---

## Decision Objects (Canonical Data Model)

- **K-Block:** Transactional scope for product decisions.
- **ZeroNode:** Epistemic anchor for each product concept.
- **ValueCompass:** 7-principle radar for constitutional reward.
- **PolicyTrace:** DP-native trace of decisions and rewards.
- **Mark:** Unit of evidence; the only record that matters.

---

## Interface Primitives (User-Facing)

- **Telescope:** Navigate the product derivation graph.
- **Trail:** See the proof chain and compression ratios.
- **Witness:** Inspect evidence and justification confidence.
- **ValueCompass:** Visualize constitutional alignment.
- **Conversation:** Active dialog with factory state and decisions.

These primitives map directly to theory, ensuring the interface is not ornamental but semantic.

---

## Economic Model (Value Capture)

### Primary Value
- Continuous product creation with reduced decision friction.
- The factory is a compounding asset: each product improves the next.

### Product Outputs
- SaaS offerings generated as discrete K-Block worlds.
- Each product has an explicit proof chain and governance trace.

### Competitive Differentiation
- Not "automation," but "justified generation."
- Products are born from constitutional proofs, not opportunistic hacks.

---

## Constraints (Principles as Laws)

- **Tasteful:** Every product must justify existence.
- **Curated:** Fewer launches, higher impact.
- **Ethical:** No products that manipulate or deceive.
- **Joy-Inducing:** Each product should feel alive and collaborative.
- **Composable:** Each output is a single, composable result.
- **Heterarchical:** No permanent orchestrator.
- **Generative:** Specs must regenerate implementations.

---

## Failure Modes and Safeguards

**Failure Mode:** Automation drift (products become generic or opportunistic).
- **Safeguard:** ValueAgent reward gates; Mirror Test enforcement.

**Failure Mode:** Orchestration hierarchy ossifies.
- **Safeguard:** PolyAgent mode-dependent behavior; heterarchical enforcement.

**Failure Mode:** Decision opacity.
- **Safeguard:** Witness marks are mandatory for any commit.

---

## Why This Is Daring

- It replaces project management with epistemic proof.
- It treats product creation as a witnessed, constitutional process.
- It makes Kent's taste the ultimate constraint, not a subjective afterthought.

This is not a chatbot. It is a factory that *proves* its outputs.

---

## Immediate Artifacts (Non-Roadmap)

- A single master K-Block for the factory itself.
- A zero-seed path for each product lineage.
- A ValueAgent policy trace for every launch.

---

## The Mirror Test

"Does this factory feel like me on my best day?"
If not, it does not ship.
