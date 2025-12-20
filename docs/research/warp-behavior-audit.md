# WARP Behavior Audit: Primitive Classification

> *"The block is the atom."* — Core WARP Insight

**Date**: 2025-12-20
**Status**: ✅ **IMPLEMENTED** — All 9 primitives live in `impl/claude/services/witness/`
**Purpose**: Classify each WARP → kgents mapping as ADAPT, EVOLVE, or INVENT

---

## Classification Legend

| Category | Definition | Example |
|----------|------------|---------|
| **ADAPT** | Direct mapping with minimal changes | WARP Block → TraceNode (structure preserved) |
| **EVOLVE** | Enhanced with category theory (laws, composition) | WARP Tasks → IntentTree (typed, lawful edges) |
| **INVENT** | kgents-native, inspired but fundamentally different | VoiceGate (WARP has NL detection; kgents has Anti-Sausage) |

---

## Primitive Classification Table

| Primitive | WARP Source | Category | Constitutional Principle | Voice Anchor |
|-----------|-------------|----------|--------------------------|--------------|
| **TraceNode** | Block | ADAPT | Composable (single output), Generative (spec-first) | *"Every action is a TraceNode"* |
| **Walk** | Conversation | EVOLVE | Heterarchical (no fixed structure), Generative (Forest-bound) | *"The persona is a garden, not a museum"* |
| **Ritual** | Agent Mode | EVOLVE | Ethical (explicit gates), Composable (N-Phase phases) | *"Tasteful > feature-complete"* |
| **Offering** | Context Attachments | EVOLVE | Ethical (priced context), Curated (explicit handles) | *"Depth over breadth"* |
| **IntentTree** | Task List | EVOLVE | Composable (typed graph), Generative (dependencies as edges) | *"The Mirror Test"* |
| **Covenant** | Profiles/Permissions | INVENT | Ethical (negotiated, not assumed), Joy-Inducing (visible) | *"Daring, bold, creative, opinionated"* |
| **Terrace** | Drive | ADAPT | Curated (versioned layers), Heterarchical (multiple terraces) | *"Tasteful > feature-complete"* |
| **VoiceGate** | NL Detection | INVENT | Ethical (Anti-Sausage enforcement), Tasteful (voice preservation) | *"Daring, bold, creative, opinionated but not gaudy"* |
| **TerrariumView** | Panes | EVOLVE | Composable (functor composition), Heterarchical (multi-surface) | *"Joy-inducing > merely functional"* |

---

## Detailed Analysis

### TraceNode (ADAPT)

**WARP Behavior**: Block is the atomic unit — command + output + metadata.

**kgents Adaptation**:
- Preserves: command/output/metadata structure
- Adds: `umwelt` (observer context), `links` (causal edges), `phase` (N-Phase position)
- Preserves: immutability, append-only semantics

**Why ADAPT**: The core insight (block as atom) is correct. We just add categorical metadata.

```python
# WARP-compatible fields
origin: JewelOrAgent   # Who emitted it
stimulus: Stimulus     # The command/prompt
response: Response     # The output/diff

# kgents additions
umwelt: UmweltSnapshot # Observer context (new)
links: list[TraceLink] # Causal edges (new)
phase: NPhase | None   # N-Phase position (new)
```

---

### Walk (EVOLVE)

**WARP Behavior**: Conversation is an ordered sequence of blocks with context.

**kgents Evolution**:
- Preserves: ordered trace sequence, context accumulation
- Evolves: bound to Forest plan files (not freeform)
- Evolves: N-Phase position tracking (grammar-constrained transitions)
- Evolves: participant Umwelts (not just "context")

**Why EVOLVE**: WARP conversations are freeform. kgents Walks have structure (Forest binding, N-Phase grammar).

```python
# WARP-compatible
trace_nodes: list[TraceNodeId]  # Ordered history

# kgents evolution
root_plan: PlanPath    # Forest binding (law: must exist in Forest)
phase: NPhase          # Grammar-constrained (law: follows N-Phase DAG)
participants: list[ParticipantId]  # Umwelt-aware
```

---

### Ritual (EVOLVE)

**WARP Behavior**: Agent Mode is a multi-step loop with human approvals.

**kgents Evolution**:
- Preserves: multi-step workflow, approval gates
- Evolves: phases are state machines (N-Phase compatible)
- Evolves: guards emit TraceNodes (visible, auditable)
- Evolves: Covenant binding (permissions explicit, not profile-implicit)

**Why EVOLVE**: WARP approvals are ad-hoc. kgents Rituals are lawful state machines with explicit Covenants.

**Constitutional Alignment**: Pattern 9 (Phase Ordering) from `crown-jewel-patterns.md`.

---

### Offering (EVOLVE)

**WARP Behavior**: Context attachments are files, URLs, blocks, knowledge items.

**kgents Evolution**:
- Preserves: handle-based context access
- Evolves: explicit budgets (capital, entropy, tokens, time)
- Evolves: contracts per handle (read/write caps)
- Evolves: expiration semantics

**Why EVOLVE**: WARP attachments are "use as needed." kgents Offerings are priced contracts.

**Constitutional Alignment**: Principle 3 (Ethical) — explicit pricing prevents hidden costs.

---

### IntentTree (EVOLVE)

**WARP Behavior**: Task list is freeform decomposition of work.

**kgents Evolution**:
- Preserves: decomposition into subtasks
- Evolves: typed nodes (EXPLORE, DESIGN, IMPLEMENT, REFINE, VERIFY, ARCHIVE)
- Evolves: typed edges with capability requirements
- Evolves: status tracking (PENDING, ACTIVE, COMPLETE, BLOCKED)

**Why EVOLVE**: WARP tasks are strings. kgents Intents are typed nodes in a graph with lawful edges.

**Constitutional Alignment**: Principle 7 (Generative) — spec is compression.

---

### Covenant (INVENT)

**WARP Behavior**: Profiles grant tool access and autonomy levels.

**kgents Invention**:
- Fundamentally different: permissions are **negotiated**, not granted by profile
- New: review gates (human or K-gent approval)
- New: degradation tiers (graceful fallback under stress)
- New: amendment history (traceable permission changes)

**Why INVENT**: WARP profiles are static grants. kgents Covenants are dynamic contracts that evolve.

**Constitutional Alignment**: Principle 3 (Ethical) — human agency preserved through negotiation.

---

### Terrace (ADAPT)

**WARP Behavior**: Drive is shared knowledge with reusable content.

**kgents Adaptation**:
- Preserves: curated content, reusable flows
- Adds: versioning (explicit version field)
- Adds: canonical traces (TraceNodes as exemplars)
- Adds: curator attribution

**Why ADAPT**: Drive and Terrace serve the same purpose. kgents adds versioning and categorization.

---

### VoiceGate (INVENT)

**WARP Behavior**: NL detection distinguishes commands from natural language; denylists block harmful prompts.

**kgents Invention**:
- Fundamentally different: Anti-Sausage protocol preserves Kent's voice, not just safety
- New: Voice anchors (phrases to preserve)
- New: Transform action (not just block—can suggest alternatives)
- New: Semantic pattern matching (not just regex denylists)

**Why INVENT**: WARP detects command vs. NL for safety. kgents VoiceGate enforces aesthetic consistency.

**Voice Anchor**: *"Daring, bold, creative, opinionated but not gaudy"*

---

### TerrariumView (EVOLVE)

**WARP Behavior**: Panes are multiple surfaces in a workspace.

**kgents Evolution**:
- Preserves: multi-surface workspace
- Evolves: selection is a query (functor from data to view)
- Evolves: lens is a natural transformation (preserves structure)
- Evolves: projection target is parameterized (servo, cli, marimo)

**Why EVOLVE**: WARP panes are layout primitives. kgents TerrariumViews are categorical compositions.

**Constitutional Alignment**: Principle 5 (Composable) — views compose via functor laws.

---

## Summary

| Category | Count | Primitives | Implementation |
|----------|-------|------------|----------------|
| **ADAPT** | 2 | TraceNode, Terrace | `trace_node.py`, `terrace.py` |
| **EVOLVE** | 5 | Walk, Ritual, Offering, IntentTree, TerrariumView | `walk.py`, `ritual.py`, `offering.py`, `intent.py`, (TerrariumView in web/) |
| **INVENT** | 2 | Covenant, VoiceGate | `covenant.py`, `voice_gate.py` |

**Test Coverage**: 30+ test files in `services/witness/_tests/`

**Insight**: Most WARP primitives needed evolution (categorical enhancement), not invention. The two inventions (Covenant, VoiceGate) are where kgents diverges philosophically from WARP—not in mechanism, but in purpose.

---

## Anti-Sausage Check

- ❓ Did I classify generously (too many ADAPT)? **No — only 2 ADAPTs where structure truly matches.**
- ❓ Are voice anchors authentic? **Yes — quoted directly from `_focus.md`.**
- ❓ Is classification opinionated? **Yes — clear reasoning for each, no hedging.**

---

*"The noun is a lie. There is only the rate of change."*
