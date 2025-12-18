---
domain: self
holon: f
polynomial:
  positions:
    - dormant
    - streaming
    - branching
    - converging
    - draining
    - collapsed
  transition: flow_transition
  directions: flow_directions
operad:
  extends: AGENT_OPERAD
  operations:
    # Universal Flow Operations
    start:
      arity: 1
      signature: "Agent[A,B] -> Flow[A] -> Flow[B]"
      description: "Start a flow from an agent and input source"
    stop:
      arity: 0
      signature: "Flow[_] -> ()"
      description: "Stop a running flow"
    perturb:
      arity: 1
      signature: "(Flow[A], A) -> B"
      description: "Inject input into a streaming flow"
    # Chat Operations
    turn:
      arity: 1
      signature: "Message -> Response"
      description: "Execute one conversation turn"
    summarize:
      arity: 1
      signature: "Context -> CompressedContext"
      description: "Compress context window"
    inject_context:
      arity: 1
      signature: "Context -> Flow[_]"
      description: "Inject context into flow"
    # Research Operations
    research_branch:
      arity: 1
      signature: "Hypothesis -> [Hypothesis]"
      description: "Generate alternative hypotheses"
    merge:
      arity: 2
      signature: "(Hypothesis, Hypothesis) -> Synthesis"
      description: "Combine hypotheses into synthesis"
    prune:
      arity: 1
      signature: "[Hypothesis] -> [Hypothesis]"
      description: "Eliminate low-promise hypotheses"
    evaluate:
      arity: 1
      signature: "Hypothesis -> Score"
      description: "Score a hypothesis"
    # Collaboration Operations
    post:
      arity: 1
      signature: "Contribution -> Blackboard"
      description: "Post contribution to blackboard"
    read:
      arity: 1
      signature: "Query -> [Contribution]"
      description: "Read contributions from blackboard"
    vote:
      arity: 2
      signature: "(Proposal, Agents) -> Decision"
      description: "Vote on a proposal"
    moderate:
      arity: 1
      signature: "[Contribution] -> Resolution"
      description: "Moderate conflict"
  laws:
    start_identity: "start(Id) = Id_Flow"
    start_composition: "start(f >> g) = start(f) >> start(g)"
    perturbation_integrity: "perturb(flowing, x) = inject_priority(x)"
    branch_merge: "merge(branch(h)) >= essence(h)"
    prune_idempotent: "prune(prune(hs)) = prune(hs)"
    post_read: "read(all, post(c, board)) = [c] ++ read(all, board)"
    consensus_threshold: "vote(p, agents) = decide if votes >= threshold"
agentese:
  path: self.flow
  aspects:
    - manifest
    - modalities
    - chat
    - research
    - collab
    - configure
---

# F-gent (Flow Agent) Specification

> *"Flow is the unifying abstraction. Chat, research, and collaboration are modalities of the same substrate."*

The F-gent Crown Jewel provides a unified flow abstraction for chat, research, and collaboration modalities. All three share the same polynomial state machine with modality-specific operations.

## Categorical Structure

### Polynomial (FlowPolynomial)

Flows exist in 6 lifecycle phases:

| Position | Description | Valid Transitions |
|----------|-------------|-------------------|
| DORMANT | Created, not started | -> STREAMING |
| STREAMING | Processing continuous input | -> BRANCHING, CONVERGING, DRAINING |
| BRANCHING | Exploring alternatives (research) | -> STREAMING, CONVERGING |
| CONVERGING | Merging branches/consensus | -> STREAMING, COLLAPSED |
| DRAINING | Flushing remaining output | -> COLLAPSED |
| COLLAPSED | Terminal state | Terminal (can RESET) |

**Key Property**: All modalities share this structure. The difference is which operations are valid in each phase.

### Operad (FLOW_OPERAD)

The operad defines the grammar of valid flow operations:

**Universal**: `start`, `stop`, `perturb`
**Chat**: `turn`, `summarize`, `inject_context`
**Research**: `research_branch`, `merge`, `prune`, `evaluate`
**Collaboration**: `post`, `read`, `vote`, `moderate`

**Laws**:
- `start_identity`: Starting with identity agent yields identity flow
- `start_composition`: Start distributes over composition
- `perturbation_integrity`: Perturbation injects with priority
- `branch_merge`: Merging branches preserves semantic essence
- `prune_idempotent`: Pruning is idempotent
- `post_read`: Posted contributions are immediately readable
- `consensus_threshold`: Consensus requires threshold agreement

## Modalities

### Chat Modality

Conversational flow with context management. Primarily stays in STREAMING with summarization for context window management.

### Research Modality

Hypothesis exploration and synthesis. Uses STREAMING -> BRANCHING -> CONVERGING cycles for systematic exploration.

### Collaboration Modality

Multi-agent consensus building. STREAMING with blackboard for contributions, CONVERGING for voting and decisions.

## AGENTESE Interface

```
self.flow.manifest     - Flow service status
self.flow.modalities   - List available modalities
self.flow.chat.*       - Chat operations (delegates to self.chat)
self.flow.research.*   - Research operations
self.flow.collab.*     - Collaboration operations
self.flow.configure    - Configure default modality
```

## Implementation

- **Polynomial**: `impl/claude/agents/f/polynomial.py`
- **Operad**: `impl/claude/agents/f/operad.py`
- **Node**: `impl/claude/services/f/node.py`
- **Chat Service**: `impl/claude/services/chat/` (chat modality persistence)

---

*Canonical spec derived from implementation reflection. Last verified: 2025-12-18*
