# Unified Chat Protocol v5.0

> *"Conversation is structured time-travel through possibility space."*
>
> *"Chat = FlowPolynomial ∘ ValueAgent ∘ PolicyTrace ∘ K-Block ∘ Evidence"*
>
> *"The proof IS the decision. The mark IS the witness. The chat IS the flow."*

**Status:** Specification v5.0 (Unified Architecture)
**Date:** 2025-12-25
**Consolidates:** chat.md (v3.0), chat-web.md (v4.1b), f-gents/chat.md
**Principles:** Composable, Generative, Ethical, Joy-Inducing, Heterarchical
**Grounding:** Zero Seed L3, ValueAgent Framework, FlowPolynomial

---

## This Spec's Own Proof

```yaml
proof:
  data: |
    - FlowPolynomial provides unified state machine for all flow modalities
    - ValueAgent framework provides Constitutional reward (7 principles)
    - K-Block provides verified transactional semantics (fork/merge/rewind)
    - ASHC provides Bayesian evidence accumulation
    - chat.md (v3.0) provides solid PolyAgent foundation
    - chat-web.md (v4.1b) provides branching algebra, evidence, tool transparency

  warrant: |
    By composing FlowPolynomial (state machine) with ValueAgent (constitutional reward)
    with PolicyTrace (decision witness) with K-Block (transactions) with Evidence
    (Bayesian stopping), we get a chat protocol that is:
    - Categorically well-founded (FlowPolynomial laws)
    - Constitutionally evaluated (7-principle reward)
    - Fully witnessed (every turn is a Mark)
    - Transactionally safe (K-Block isolation)
    - Evidence-driven (Bayesian confidence)

  claim: |
    The Unified Chat Protocol v5.0 provides a principled composition of
    F-gent flow substrate, ValueAgent constitutional evaluation, and
    existing K-Block/Evidence infrastructure into a single coherent system.

  backing: |
    - FlowPolynomial identity/associativity (agents/f/ tests)
    - ValueAgent reward composition (agents/dp/ design)
    - K-Block monad laws (services/chat/session.py)
    - ASHC evidence laws (276 tests)

  qualifier: probably

  rebuttals:
    - rebuttal: "FlowPolynomial adds complexity without benefit"
      falsification: "IF flow abstraction causes >10% latency increase, simplify"
      metric: "kg metrics chat.turn_latency_with_flow"
    - rebuttal: "Constitutional reward is too abstract"
      falsification: "IF reward scores don't correlate with user satisfaction, recalibrate"
      metric: "kg metrics chat.constitutional_satisfaction_correlation"
    - rebuttal: "Unification is premature"
      falsification: "IF maintainers prefer separate specs, revert to Option A (two specs)"
      metric: "kg survey spec_preference"

  tier: EMPIRICAL
  principles: [composable, generative, ethical, heterarchical, joy-inducing]
```

---

## The Core Insight: Chat as Composed Agent

Chat is not a standalone system. It is a **composition** of five categorical constructs:

```
ChatSession = FlowPolynomial[ChatState, ChatEvent, ChatOutput]
            ∘ ValueAgent[Constitution]
            ∘ PolicyTrace[Mark]
            ∘ K-Block[checkpoint/rewind/fork/merge]
            ∘ Evidence[BetaPrior]
```

This reads:

1. **FlowPolynomial**: Chat is a polynomial functor with mode-dependent inputs
2. **ValueAgent**: Every turn is evaluated against the 7 Constitutional principles
3. **PolicyTrace**: Every decision leaves a witnessed Mark (Witness Walk)
4. **K-Block**: Chat supports transactional operations (fork/merge/rewind)
5. **Evidence**: Bayesian confidence accumulates per turn

---

## Part I: Categorical Foundation

### 1.1 Chat as FlowPolynomial Instantiation

Chat is an instantiation of the F-gent flow substrate:

```python
from agents.f import FlowPolynomial, FlowState

CHAT_POLYNOMIAL = FlowPolynomial(
    name="chat",
    positions=frozenset([
        FlowState.DORMANT,     # Session created, not started
        FlowState.STREAMING,   # Active conversation
        FlowState.BRANCHING,   # Fork operation in progress
        FlowState.CONVERGING,  # Merge operation in progress
        FlowState.DRAINING,    # Session ending, flushing output
        FlowState.COLLAPSED,   # Terminal state
    ]),
    directions=chat_directions,   # State → valid inputs
    transition=chat_transition,   # (State, Input) → (State, Output)
)

def chat_directions(state: FlowState) -> frozenset[str]:
    """Valid inputs for each chat state."""
    match state:
        case FlowState.DORMANT:
            return frozenset(["start", "configure"])
        case FlowState.STREAMING:
            return frozenset(["message", "fork", "rewind", "checkpoint", "stop"])
        case FlowState.BRANCHING:
            return frozenset(["confirm_fork", "cancel_fork"])
        case FlowState.CONVERGING:
            return frozenset(["confirm_merge", "cancel_merge"])
        case FlowState.DRAINING:
            return frozenset(["flush", "crystallize"])
        case FlowState.COLLAPSED:
            return frozenset(["reset", "harvest"])
```

**Why FlowPolynomial**:

1. **Mode-dependent inputs**: Different states accept different inputs (the polynomial insight)
2. **Shared infrastructure**: Same FlowPolynomial powers Research and Collaboration flows
3. **Continuous execution**: Flux semantics for streaming responses
4. **Perturbation safety**: Messages injected during streaming are queued, not dropped

### 1.2 Chat as ValueAgent

Every chat turn is evaluated by Constitutional reward:

```python
from agents.dp import ValueAgent, Constitution

CHAT_VALUE_AGENT = ValueAgent(
    name="chat",
    states=CHAT_POLYNOMIAL.positions,
    actions=lambda s: CHAT_POLYNOMIAL.directions(s),
    transition=lambda s, a: CHAT_POLYNOMIAL.transition(s, a)[0],
    reward=constitutional_reward,  # R(s, a, s') → PrincipleScore
    gamma=0.99,
)

def constitutional_reward(
    state: FlowState,
    action: ChatAction,
    next_state: FlowState,
) -> PrincipleScore:
    """Evaluate chat action against the 7 Constitutional principles."""
    return PrincipleScore(
        tasteful=measure_tasteful(action),       # Is this justified?
        curated=measure_curated(action),         # Is this intentional?
        ethical=measure_ethical(action),         # Does this respect human agency?
        joy_inducing=measure_joy(action),        # Does this delight?
        composable=measure_composable(action),   # Does this compose cleanly?
        heterarchical=measure_heterarchical(action),  # Is this flux-ready?
        generative=measure_generative(action),   # Is this compressive?
    )

# Weights for constitutional evaluation
CONSTITUTION_WEIGHTS = {
    Principle.ETHICAL: 2.0,        # Safety first
    Principle.COMPOSABLE: 1.5,     # Architecture second
    Principle.JOY_INDUCING: 1.2,   # Kent's aesthetic
    # Others default to 1.0
}
```

**Why ValueAgent**:

1. **Principled evaluation**: Every action has explicit justification
2. **Bellman optimality**: Composition preserves optimality (sheaf gluing)
3. **Self-improvement**: PolicyTrace enables learning from past decisions
4. **Explainability**: Constitutional scores explain "why" decisions were made

### 1.3 Chat as PolicyTrace (Witness Walk)

Every turn is a witnessed Mark in the PolicyTrace:

```python
from agents.o import Mark, PolicyTrace

class ChatMark(Mark):
    """Witness mark for a chat turn."""
    turn_number: int
    user_message: str
    assistant_response: str
    tools_used: list[str]
    constitutional_scores: PrincipleScore
    evidence: ChatEvidence
    reasoning: str  # Why this response was generated

# The chat session IS a PolicyTrace
ChatSession = PolicyTrace[ChatMark]
```

**Why PolicyTrace**:

1. **Auditability**: Every decision is witnessed with reasoning
2. **Reproducibility**: PolicyTrace can be replayed
3. **Learning**: Past marks inform future decisions
4. **Composition**: Marks from different sessions can be merged

### 1.4 Composition Formula (The Core Equation)

```
Chat = F-gent ∘ ValueAgent ∘ PolicyTrace ∘ K-Block ∘ Evidence

Where:
- F-gent provides: FlowPolynomial state machine, Flux streaming
- ValueAgent provides: Constitutional reward, Bellman optimality
- PolicyTrace provides: Witness Walk, decision tracing
- K-Block provides: fork/merge/rewind transactions
- Evidence provides: Bayesian stopping, confidence scores
```

**Composition Laws**:

| Law | Statement | Verification |
|-----|-----------|--------------|
| **Identity** | `Id >> Chat ≡ Chat ≡ Chat >> Id` | FlowPolynomial identity |
| **Associativity** | `(A >> B) >> C ≡ A >> (B >> C)` | ValueAgent composition |
| **Fork-Merge** | `merge(fork(s)) ≡ s` | K-Block tests |
| **Evidence Join** | `join(e1, e2) = join(e2, e1)` | ASHC commutativity |

---

## Part II: State Machine

### 2.1 Unified State Enumeration

Resolving the state drift between chat.md (6 states) and chat-web.md (5 states):

```python
class ChatState(Enum):
    """Unified chat states derived from FlowState."""

    # From FlowState (shared with Research/Collaboration)
    DORMANT = "dormant"       # Created, not started
    STREAMING = "streaming"   # Active conversation (replaces READY + PROCESSING)
    BRANCHING = "branching"   # Fork operation
    CONVERGING = "converging" # Merge operation
    DRAINING = "draining"     # Session ending
    COLLAPSED = "collapsed"   # Terminal

    # Chat-specific substates (within STREAMING)
    # These are MODES, not separate states
    @property
    def is_awaiting_tool(self) -> bool:
        """Tool execution pending (substate of STREAMING)."""
        return self._metadata.get("awaiting_tool", False)

    @property
    def is_compressing(self) -> bool:
        """Context compression active (substate of STREAMING)."""
        return self._metadata.get("compressing", False)
```

**Resolution**: AWAITING_TOOL and COMPRESSING from chat.md become **metadata flags** on STREAMING, not separate states. This preserves FlowPolynomial compatibility while retaining chat-specific semantics.

### 2.2 State Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UNIFIED CHAT STATE MACHINE                            │
│                        (FlowPolynomial-derived)                              │
│                                                                              │
│                        ┌──────────────┐                                     │
│                        │   DORMANT    │◄──────────────────────┐             │
│                        └──────────────┘                       │             │
│                               │                               │             │
│                          start()                          reset()           │
│                               ▼                               │             │
│         fork()         ┌──────────────┐         merge()      │             │
│     ┌─────────────────►│  STREAMING   │◄────────────────┐    │             │
│     │                  └──────────────┘                 │    │             │
│     │                         │                         │    │             │
│     │           ┌─────────────┼─────────────┐          │    │             │
│     │           │             │             │          │    │             │
│     │      fork()          stop()      merge()         │    │             │
│     │           ▼             │             ▼          │    │             │
│ ┌──────────────┐             │      ┌──────────────┐   │    │             │
│ │  BRANCHING   │─────────────┘      │  CONVERGING  │───┘    │             │
│ └──────────────┘ confirm            └──────────────┘        │             │
│                               │                              │             │
│                          stop()                              │             │
│                               ▼                              │             │
│                        ┌──────────────┐                      │             │
│                        │   DRAINING   │──────────────────────┤             │
│                        └──────────────┘                      │             │
│                               │                              │             │
│                       crystallize()                          │             │
│                               ▼                              │             │
│                        ┌──────────────┐                      │             │
│                        │  COLLAPSED   │──────────────────────┘             │
│                        └──────────────┘                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Mode-Dependent Inputs

```python
def directions(state: ChatState) -> frozenset[ChatAction]:
    """Valid actions for each state (polynomial directions)."""
    match state:
        case ChatState.DORMANT:
            return frozenset([
                ChatAction.START,
                ChatAction.CONFIGURE,
                ChatAction.DELETE,
            ])
        case ChatState.STREAMING:
            return frozenset([
                ChatAction.MESSAGE,
                ChatAction.FORK,
                ChatAction.CHECKPOINT,
                ChatAction.REWIND,
                ChatAction.STOP,
                ChatAction.INJECT_CONTEXT,  # @mentions
            ])
        case ChatState.BRANCHING:
            return frozenset([
                ChatAction.CONFIRM_FORK,
                ChatAction.CANCEL_FORK,
            ])
        case ChatState.CONVERGING:
            return frozenset([
                ChatAction.CONFIRM_MERGE,
                ChatAction.CANCEL_MERGE,
                ChatAction.RESOLVE_CONFLICT,
            ])
        case ChatState.DRAINING:
            return frozenset([
                ChatAction.FLUSH,
                ChatAction.CRYSTALLIZE,
            ])
        case ChatState.COLLAPSED:
            return frozenset([
                ChatAction.RESET,
                ChatAction.HARVEST,
            ])
```

---

## Part III: Context Management

### 3.1 WorkingContext Functor

Context projection is a **functor** from Session to ContextWindow:

```python
WorkingContext : Session → ContextWindow

# Functor Laws
1. Identity:    WorkingContext(id) = id
2. Composition: WorkingContext(f ∘ g) = WorkingContext(f) ∘ WorkingContext(g)
```

### 3.2 LinearityMap (Preservation Tags)

```python
class LinearityTag(Enum):
    REQUIRED = "required"      # Never drop (system prompt, key facts)
    PRESERVED = "preserved"    # Prefer to keep (recent turns)
    DROPPABLE = "droppable"    # Safe to summarize (routine responses)
```

### 3.3 Galois Compression

Compression forms a Galois connection:

```
compress : Session → ContextWindow
expand   : ContextWindow → SessionProjection

Laws:
  1. expand(compress(s)).provenance ⊆ s  (unit)
  2. compress(expand(w)).provenance ⊆ w  (counit)
  3. L(compressed) ≤ L(original) + ε     (bounded loss)
```

### 3.4 Compression Strategy

```python
class ContextConfig:
    window_size: int = 200_000           # Claude Opus 4.5
    compress_at: float = 0.80            # 160k tokens
    resume_at: float = 0.70              # Hysteresis
    galois_tolerance: float = 0.05       # Semantic loss bound
    strategy: Literal["sliding", "summarize", "galois"] = "galois"
```

---

## Part IV: Evidence & Stopping

### 4.1 Bayesian Evidence (ASHC-Inspired)

```python
@dataclass
class ChatEvidence:
    """Bayesian evidence per turn."""
    prior: BetaPrior                    # Before this turn
    posterior: BetaPrior                # After this turn
    tools_succeeded: int
    tools_failed: int
    user_signals: list[UserSignal]      # Corrections, reactions
    ashc_equivalence: float | None      # If spec edited

    @property
    def confidence(self) -> float:
        """P(goal_achieved) under posterior."""
        return self.posterior.mean()

    @property
    def should_stop(self) -> bool:
        """Stopping criterion: P(success > 0.5) ≥ 0.95"""
        return self.posterior.prob_success_above(0.5) >= 0.95

    def update(self, turn_succeeded: bool) -> ChatEvidence:
        """Bayesian update."""
        if turn_succeeded:
            new_prior = BetaPrior(self.prior.alpha + 1, self.prior.beta)
        else:
            new_prior = BetaPrior(self.prior.alpha, self.prior.beta + 1)
        return replace(self, prior=self.posterior, posterior=new_prior)
```

### 4.2 Constitutional Reward Integration

Evidence accumulation is linked to Constitutional reward:

```python
def compute_turn_reward(
    turn: Turn,
    evidence: ChatEvidence,
) -> PrincipleScore:
    """Combine evidence with constitutional evaluation."""

    # Base constitutional scores
    constitutional = constitutional_reward(
        turn.pre_state,
        turn.action,
        turn.post_state,
    )

    # Weight by evidence confidence
    confidence_weight = evidence.confidence

    # Ethical principle gets extra weight when mutations occur
    if turn.has_mutations:
        constitutional.ethical *= 1.5  # Mutations must be acknowledged

    return constitutional.weighted_by(confidence_weight)
```

---

## Part V: Branching Algebra (K-Block)

### 5.1 HARNESS_OPERAD Instance

```python
CHAT_BRANCHING = HARNESS_OPERAD.instantiate(
    carrier=ChatSession,
    operations={
        "fork": Arity(1, 2),       # Session → (Session, Session)
        "merge": Arity(2, 1),      # Session × Session → Session
        "checkpoint": Arity(1, 1), # Session → Session (with saved state)
        "rewind": Arity(1, 1),     # Session → Session (to checkpoint)
        "diff": Arity(2, 1),       # Session × Session → Diff
    },
    laws=[
        Law("fork_merge_id", "merge(fork(s)) ≡ s"),
        Law("merge_assoc", "merge(merge(a, b), c) ≡ merge(a, merge(b, c))"),
        Law("checkpoint_id", "rewind(checkpoint(s)) ≡ s"),
        Law("diff_sym", "diff(a, b).invert() ≡ diff(b, a)"),
    ],
)
```

### 5.2 Evidence in Branching

Evidence is **linear** during branching:

```python
def fork_evidence(evidence: ChatEvidence) -> tuple[ChatEvidence, ChatEvidence]:
    """Split evidence linearly (not copy)."""
    # Each branch gets half the observations
    left_alpha = evidence.prior.alpha // 2 + 1
    right_alpha = evidence.prior.alpha - left_alpha + 1

    return (
        ChatEvidence(prior=BetaPrior(left_alpha, evidence.prior.beta)),
        ChatEvidence(prior=BetaPrior(right_alpha, evidence.prior.beta)),
    )

def merge_evidence(e1: ChatEvidence, e2: ChatEvidence) -> ChatEvidence:
    """Join evidence via lattice."""
    return ChatEvidence(
        prior=BetaPrior(
            alpha=e1.prior.alpha + e2.prior.alpha - 1,
            beta=e1.prior.beta + e2.prior.beta - 1,
        )
    )
```

### 5.3 Cognitive Limit

```python
MAX_BRANCHES = 3  # Hard constraint for cognitive load
```

---

## Part VI: Tool Transparency (Ethical)

### 6.1 Asymmetric Design

```
READ operations:  Silent (non-destructive)
MUTATION operations: Acknowledgment required
DESTRUCTIVE operations: Approval required
```

### 6.2 Three Transparency Modes

| Level | Reads | Mutations | Destructive |
|-------|-------|-----------|-------------|
| **Minimal** | Silent | Acknowledgment | Approval |
| **Approval** | Silent | Approval | Approval |
| **Detailed** | Toast | Full panel | Full panel |

### 6.3 Mutation Acknowledgment

```python
@dataclass
class MutationAcknowledgment:
    mutation_id: str
    acknowledged_at: datetime
    mode: Literal["click", "keyboard", "timeout_accept"]
```

---

## Part VII: AGENTESE Integration

### 7.1 Chat Affordances

```
<node_path>.chat.*
├── send[message="..."]      # Send message (MUTATION)
├── stream[message="..."]    # Streaming response
├── history                  # Get turn history
├── context                  # Current context window
├── evidence                 # Bayesian state
├── fork[name="..."]         # Create branch
├── merge[other_id="..."]    # Merge sessions
├── rewind[turns=n]          # Undo turns
├── checkpoint               # Save state
└── crystallize              # End and save
```

### 7.2 Observer-Dependent Behavior

```python
def select_model(observer: Observer) -> MorpheusConfig:
    match observer.archetype:
        case "developer":
            return MorpheusConfig(model="claude-sonnet-4", temperature=0.7)
        case "guest":
            return MorpheusConfig(model="claude-haiku", temperature=0.5)
        case "system":
            return MorpheusConfig(model="claude-opus-4", temperature=0.3)
```

---

## Part VIII: Implementation Architecture

### 8.1 The Metaphysical Fullstack Position

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   ChatPanel │ CLI │ API │ marimo                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     self.chat.send[message="..."]                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node("*.chat") with ChatSession                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/chat/ - ChatSession, Evidence, Context  │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        HARNESS_OPERAD (fork/merge) + FLOW_OPERAD        │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      CHAT_POLYNOMIAL (FlowPolynomial instantiation)   │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. VALUE AGENT           CHAT_VALUE_AGENT (Constitutional reward)         │
├─────────────────────────────────────────────────────────────────────────────┤
│  0. PERSISTENCE LAYER     D-gent: sessions, crystals, evidence             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Backend Structure

```
impl/claude/
├── agents/f/                    # FlowPolynomial (shared)
│   ├── flow.py
│   ├── polynomial.py
│   └── modalities/chat.py       # CHAT_POLYNOMIAL
├── agents/dp/                   # ValueAgent (shared)
│   └── value_agent.py           # Constitutional reward
├── services/chat/               # Chat Crown Jewel
│   ├── session.py               # ChatSession (uses CHAT_POLYNOMIAL)
│   ├── context.py               # WorkingContext functor
│   ├── evidence.py              # ChatEvidence (Bayesian)
│   ├── branching.py             # K-Block operations
│   ├── witness.py               # ChatMark creation
│   └── reward.py                # Constitutional scoring
└── protocols/agentese/chat/     # AGENTESE node
    └── node.py                  # @node("*.chat")
```

### 8.3 Frontend Structure

```
impl/claude/web/src/
├── constructions/ChatSession/   # Main construction
│   ├── ChatSession.tsx
│   ├── ChatSession.css
│   └── index.ts
├── primitives/Conversation/     # Reusable primitive
│   ├── Conversation.tsx
│   └── types.ts
├── components/chat/             # Chat-specific components
│   ├── ChatPanel.tsx
│   ├── BranchTree.tsx
│   ├── ContextIndicator.tsx
│   └── ActionPanel.tsx
└── hooks/
    ├── useChatStore.ts          # Zustand store
    └── useBranching.ts          # Branch operations
```

---

## Part IX: Future Features Roadmap

### Near-Term (Q1 2025)

1. **Branching UI**: Tree visualization, diff view, merge resolution
2. **Evidence Dashboard**: Bayesian confidence, ASHC results
3. **Context Pressure**: Real-time token usage, compression warnings
4. **Constitutional Radar**: 7-principle visualization per turn

### Medium-Term (Q2-Q3 2025)

4. **Research Flow Integration**: Branch into tree-of-thought, synthesize back
5. **Collaboration Flow Integration**: Multi-agent chat, blackboard pattern
6. **Meta-DP Self-Improvement**: Learn from PolicyTrace, improve policies

### Long-Term Vision

7. **Zero Seed Extraction**: Auto-extract L3-L7 nodes from conversation
8. **Crystallization First-Class**: Every session becomes queryable crystal
9. **Crystal-to-Crystal Composition**: Semantic search, crystal merging

---

## Part X: Migration Path

### From chat.md + chat-web.md → chat-unified.md

| Old | New | Change |
|-----|-----|--------|
| 6 states (chat.md) | 6 FlowStates + metadata | AWAITING_TOOL, COMPRESSING → flags |
| ChatKBlock pattern | FlowPolynomial + K-Block | Explicit polynomial composition |
| No ValueAgent | Constitutional reward | Every turn scored |
| Ad-hoc evidence | PolicyTrace | Witness Walk integration |
| Separate specs | This unified spec | Single source of truth |

### Implementation Changes

1. **ChatSession imports from agents/f/**: `from agents.f import CHAT_POLYNOMIAL`
2. **Evidence links to Constitutional reward**: Each turn has `PrincipleScore`
3. **PolicyTrace emitted**: Every turn creates a `ChatMark`
4. **Frontend uses new types**: `ConstitutionalScores` in ChatSession props

---

## Appendix A: Grounding Chain

```
L1 (Axioms): Entity, Morphism, Galois Ground
    Source: spec/protocols/zero-seed.md
         │
         │ grounds
         ▼
L2 (Values): Mirror Test + Composability + Ethical Transparency
    Source: CONSTITUTION.md, spec/principles.md
         │
         │ justifies
         ▼
L3 (Goal): Conversational Coherence
    Source: spec/protocols/zero-seed.md §3.3
         │
         │ specifies
         ▼
L4 (Spec): This Document
    Unified Chat Protocol v5.0
```

---

## Appendix B: F-gent Modality Registration

This spec defines Chat as the first F-gent modality:

```python
# In spec/f-gents/instantiations.md (to be created)

FLOW_MODALITIES = {
    "chat": {
        "polynomial": CHAT_POLYNOMIAL,
        "value_agent": CHAT_VALUE_AGENT,
        "spec": "spec/protocols/chat-unified.md",
    },
    "research": {
        "polynomial": RESEARCH_POLYNOMIAL,
        "value_agent": RESEARCH_VALUE_AGENT,
        "spec": "spec/f-gents/research.md",
    },
    "collaboration": {
        "polynomial": COLLABORATION_POLYNOMIAL,
        "value_agent": COLLABORATION_VALUE_AGENT,
        "spec": "spec/f-gents/collaboration.md",
    },
}
```

---

## Appendix C: Test Verification

```python
# tests/test_chat_unified.py

def test_chat_is_flow_polynomial():
    """Chat polynomial satisfies FlowPolynomial laws."""
    from agents.f import verify_polynomial_laws
    assert verify_polynomial_laws(CHAT_POLYNOMIAL)

def test_chat_value_agent_composition():
    """ValueAgent composition preserves optimality."""
    from agents.dp import verify_bellman
    assert verify_bellman(CHAT_VALUE_AGENT)

def test_chat_policy_trace():
    """Every turn creates a witnessed Mark."""
    session = ChatSession.create()
    session.send("Hello")
    assert len(session.policy_trace.marks) == 1

def test_constitutional_reward_coverage():
    """All 7 principles scored per turn."""
    turn = create_test_turn()
    score = constitutional_reward(turn)
    assert all(p in score for p in Principle)
```

---

*"The proof IS the decision. The mark IS the witness. The chat IS the flow."*

*Last updated: 2025-12-25*
*Version: 5.0 (Unified Architecture)*
