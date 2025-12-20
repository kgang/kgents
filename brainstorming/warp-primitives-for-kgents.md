# Warp -> kgents: Primitive Mapping v2 (WARP-Heavy)

This is a second iteration of the Warp -> kgents primitive mapping. It tightens alignment with the Constitution and spec/principles, and explicitly wires WARP-inspired primitives into CLI v7, AGENTESE node evolution, SpecGraph, the N-Phase compiler, Forest Protocol, and the Anti-Sausage protocol.

---

## 0. Constitutional Alignment (Non-Negotiable)

Every primitive and mapping below must satisfy the seven immutable principles in `spec/principles/CONSTITUTION.md`:

- Tasteful: each new primitive earns existence, no kitchen-sink nodes
- Curated: fewer, sharper primitives over sprawling taxonomies
- Ethical: explicit human gates and visible provenance
- Joy-Inducing: interactions feel alive, not bureaucratic
- Composable: single-output agents, clean I/O contracts
- Heterarchical: no permanent boss agent; roles are contextual
- Generative: spec compresses implementation; SpecGraph enforces drift checks

This doc uses WARP as inspiration but remains kgents-native in style.

---

## 1. WARP Primitives -> kgents Primitives (Mapping Table)

| WARP primitive | WARP behavior | kgents primitive | kgents anchor | Notes |
| --- | --- | --- | --- | --- |
| Block | command + output + metadata | TraceNode | `time.trace.node.*`, `witness.event.*` | Trace-first history and context handles |
| Conversation | ordered blocks + context | Walk | `time.walk.*` + Forest plans | Long-lived work stream tied to plans |
| Agent Mode | multi-step loop with approvals | Ritual | `self.ritual.*` + Curator + Sentinel | Workflow engine with gates and covenants |
| Context attachments | files, URLs, blocks, knowledge | Offering | `concept.offering.*` | Context becomes priced and contractual |
| Task list | decomposed tasks | IntentTree | `concept.intent.*` + `time.intent.*` | Typed intent graph with dependencies |
| Profiles & permissions | tool access + autonomy | Covenant | `self.covenant.*` | Permissions negotiated, not assumed |
| Drive | shared knowledge | Terrace | `brain.terrace.*` | Curated, versioned knowledge layers |
| NL detection + denylists | safety for command vs NL | VoiceGate | `self.voice.gate.*` | Anti-sausage enforcement point |
| Panes | multi-surface workspace | TerrariumView | `world.terrarium.view.*` | Multiple projections over same substrate |

---

## 2. Core Primitives (Rewritten for v2)

### 2.1 TraceNode (WARP Block -> time.trace)

WARP makes a block the atomic unit. kgents must do the same, but under Witness + Time.

- `time.trace.node.{id}` stores the execution artifact
- `witness.event.{id}` stores the observation context

Minimum fields (spec-level):

- origin: jewel or agent that emitted it
- stimulus: prompt, command, or event
- response: output, diff, or state transition
- umwelt: observer capabilities at emission time
- links: causal edges (plan -> node, node -> node)

TraceNodes become the default context handle for AGENTESE, N-Phase, and CLI v7.

### 2.2 Walk (WARP Conversation -> time.walk)

WARP conversation = a durable work stream. In kgents, this is a Forest Walk.

- `time.walk.{id}` links TraceNodes to Forest plans
- The Walk is the unit of replay, summarization, and learning

Fields:

- goal: `concept.intent.{id}`
- root_plan: `plans/*.md` leaf
- trace_nodes: ordered list of TraceNode IDs
- participants: agents + umwelts
- phase: current N-Phase position

### 2.3 Ritual (WARP Agent Mode -> self.ritual)

Ritual is a Curator-orchestrated workflow with explicit gates.

- `self.ritual.{id}` is the runtime workflow object
- Rituals compile from IntentTrees + Offerings + Covenants

Ritual components:

- intent: `concept.intent.{id}`
- phases: a typed state machine (N-Phase compatible)
- guards: Sentinel checks at each boundary
- tools: registered agent capabilities

Rituals are WARP Agent Mode but with category laws and covenant negotiation.

### 2.4 Offering (WARP Context Attachments -> concept.offering)

Context should be explicitly priced and scoped.

- `concept.offering.{id}` is a set of handles, budgets, and contracts
- Every AGENTESE invocation should reference an Offering

Offering fields:

- handles: `brain.*`, `world.file.*`, `plans.*`, `time.trace.*`
- budget: capital, entropy, token constraints
- contracts: read/write caps by agent or jewel

### 2.5 IntentTree (WARP Task List -> concept.intent)

Typed intent nodes replace freeform tasks.

- `concept.intent.{id}` describes a typed goal
- `time.intent.{id}` captures temporal state (in-progress, done)

Intent types:

- EXPLORE, DESIGN, IMPLEMENT, REFINE, VERIFY, ARCHIVE

Edges carry dependencies and capability requirements (Umwelt v2).

### 2.6 Covenant (WARP Profiles -> self.covenant)

Permissions are negotiated, not implicit.

- `self.covenant.{id}` defines permitted handles and review gates
- Sentinels can amend a Covenant (temporary privileges)

Fields:

- allowed_handles: path patterns
- budget: capital ceilings
- review_gates: human or K-gent approval checkpoints
- degradation_tiers: fallback permissions under stress

### 2.7 Terrace (WARP Drive -> brain.terrace)

Terrace is a curated, versioned knowledge layer.

- `brain.terrace.{id}` stores reusable flows and reference content
- Terraces host Ritual templates, IntentTrees, and canonical TraceNodes

### 2.8 VoiceGate (WARP NL detection -> self.voice.gate)

WARP distinguishes command vs NL. kgents must detect voice drift.

- `self.voice.gate.{id}` enforces Anti-Sausage constraints
- Used at AGENTESE entrypoints and CLI v7 prompt parsing

### 2.9 TerrariumView (WARP Panes -> world.terrarium.view)

Multiple projections over the same substrate.

- `world.terrarium.view.{id}` defines a configured projection
- Each view is a functor: selection + lens + projection target

---

## 3. Meta-Planning Systems (SpecGraph + N-Phase + Forest + Anti-Sausage)

This is where WARP becomes kgents-native. The primitives above are not just runtime objects; they are planning objects.

Relevant spec anchors: `spec/principles.md` AD-005 (N-Phase self-similar lifecycle) and AD-006 (Unified Categorical Foundation).

### 3.1 SpecGraph (Spec -> Impl -> Drift)

SpecGraph makes primitives generative and auditable.

- Every primitive listed above should have a SpecGraph node
- Reflect, compile, and drift-check are mandatory
- Primitive definitions are spec-first; implementations derive from spec

SpecGraph loop:

- Compile: `spec/*` -> `impl/claude/*`
- Reflect: `impl/claude/*` -> spec summary
- Drift: report divergence, generate stubs if gaps appear

### 3.2 N-Phase Compiler

The N-Phase compiler is the process engine for these primitives.

- Plan files and Ritual templates compile into N-Phase prompts
- Walks and IntentTrees carry phase state
- TraceNodes record phase transitions

N-Phase is not a rigid sequence; it is the lifecycle grammar for Rituals.

### 3.3 Forest Protocol

Forest is the persistent planning substrate.

- Every major primitive change should create or update a Forest plan file
- Walks anchor to these plan leaves
- Forest files remain the durable coordination layer across sessions

### 3.4 Anti-Sausage Protocol

Anti-Sausage is the voice firewall.

- All WARP-inspired additions must pass the Anti-Sausage check
- VoiceGate enforces this at runtime
- CLI v7 UI text and system prompts must remain opinionated and kent-voice

---

## 4. CLI v7 Integration (Concrete Wiring)

CLI v7 is the immediate beneficiary. WARP primitives map directly into its architecture.

### 4.1 TraceNodes in the Conversation Window

- The Conversation Window becomes a TraceNode feed, not just text history
- Context preview is a projection of TraceNodes + Offerings
- Summarizer emits TraceNodes with provenance, not freeform text

### 4.2 Rituals in the Conductor

- Conductor orchestrates Rituals, not ad-hoc flows
- Each CLI v7 session corresponds to a Walk
- File I/O actions are Ritual steps with Covenant and VoiceGate checks

### 4.3 Presence as TerrariumView

- The Collaborative Canvas becomes a TerrariumView over TraceNodes
- Agent cursors point to active TraceNodes and IntentTree nodes

### 4.4 IntentTrees for Task Decomposition

- CLI v7 uses IntentTrees instead of flat task lists
- Each Intent leaf maps to a Ritual step
- Intent -> TraceNode -> Walk = full provenance chain

### 4.5 Drive -> Terrace

- CLI v7 "Drive" equivalent is a curated Terrace
- The Terrace is the default Offering source for a Walk

---

## 5. AGENTESE Node Improvements (Deep Integration)

These are the concrete node additions and upgrades implied by this mapping.

### 5.1 New or Expanded AGENTESE Paths

- `time.trace.node.*` and `time.trace.walk.*` (TraceNode and Walk APIs)
- `self.ritual.*` (Ritual lifecycle, phases, guards)
- `concept.offering.*` (context bundle creation and scope)
- `concept.intent.*` + `time.intent.*` (typed intent graphs with state)
- `self.covenant.*` (permission negotiation and gates)
- `brain.terrace.*` (Drive-like knowledge layers)
- `self.voice.gate.*` (Anti-Sausage enforcement)
- `world.terrarium.view.*` (multi-surface projections)

### 5.2 Node-Level Improvements (Tied to Ongoing Work)

- Align these new nodes with the AGENTESE node overhaul patterns
- Register paths through the router consolidation plan
- Add contracts for all new aspects and emit Witness events for every mutation
- Ensure all nodes are SpecGraph-backed and drift-checked
- Support CLI v7 Conductor and REPL integration for every new path

### 5.3 Spec-First Deliverables

For each new node:

- Add spec entries with YAML frontmatter for SpecGraph
- Implement minimal, composable aspects (one output per call)
- Add tests that verify identity/associativity laws where applicable

---

## 6. N-Phase Implementation Arc (CLI v7 + AGENTESE)

This is a concrete N-Phase skeleton for the WARP integration.

- PLAN: create Forest plan files for TraceNode, Walk, Ritual, Offering, VoiceGate
- RESEARCH: audit WARP behaviors and CLI v7 constraints
- DEVELOP: draft SpecGraph nodes and AGENTESE path contracts
- STRATEGIZE: map nodes to CLI v7 Conductor + Conversation Window
- CROSS-SYNERGIZE: align with Witness, Brain, Gardener, Town
- IMPLEMENT: wire nodes, add minimal storage, emit TraceNodes
- QA: verify read-before-edit and covenant gates
- TEST: SpecGraph drift check, node contract tests, CLI v7 flow tests
- EDUCATE: update skills and CLI v7 docs
- MEASURE: track trace coverage, ritual completion, voice-gate hits
- REFLECT: Anti-Sausage check and constitution review

The Forest Protocol is the storage layer for this arc. The N-Phase compiler is the execution layer.

---

## 7. Anti-Sausage Check (WARP-Heavy Edition)

- Did I smooth anything that should stay sharp? No. This remains a trace-first, spec-first system.
- Did I add words or tone Kent would not use? Avoided filler; kept category and ontology language.
- Did I water down the category laws or heterarchy? No. They are explicit and enforced.
- Is this still daring? Yes. It commits to WARP-grade ergonomics without losing kgents identity.

---

## 8. Next Iteration Targets (Optional)

- Draft SpecGraph nodes for TraceNode, Walk, Ritual, Offering
- Add CLI v7 view pilots for TraceNode playback and Walk timelines
- Add a VoiceGate prototype that reads the Anti-Sausage checklist
- Convert one CLI v7 flow into a Ritual with a Covenant and Offerings
