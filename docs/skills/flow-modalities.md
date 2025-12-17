---
path: docs/skills/flow-modalities
status: active
progress: 100
last_touched: 2025-12-16
touched_by: claude-opus-4-5
blocking: []
enables: []
session_notes: |
  Created for F-gent Flow modalities (Chat, Research, Collaboration).
  AGENTESE integration complete (self.flow.* paths).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: touched
  MEASURE: deferred
  REFLECT: touched
entropy:
  planned: 0.1
  spent: 0.08
  returned: 0.02
---

# Skill: F-gent Flow Modalities

> Chat, Research, and Collaboration substrates for continuous agent interaction.

**Difficulty**: Medium
**Prerequisites**: Understanding of `Agent[A, B]` protocol, AGENTESE basics
**Files Touched**: `agents/f/modalities/`, `protocols/agentese/contexts/self_flow.py`

---

## Overview

F-gent provides three **conversational modalities** for agent interaction:

| Modality | Purpose | Key Structure |
|----------|---------|---------------|
| **Chat** | Turn-based conversation with context management | `ChatFlow`, `Turn`, `SlidingContext` |
| **Research** | Tree of thought exploration | `ResearchFlow`, `HypothesisTree`, `Synthesis` |
| **Collaboration** | Multi-agent blackboard patterns | `CollaborationFlow`, `Blackboard`, `Contribution` |

**Note**: Flow modalities are distinct from `agents.flux` (streaming infrastructure).
- **Flow** = Conversational *modalities* (how agents converse)
- **Flux** = Stream *processing* (how agents consume events)

---

## AGENTESE Paths

Flow is wired into AGENTESE via `self.flow.*`:

```python
# Inspect flow state
await logos.invoke("self.flow.state", observer)         # → {"state": "dormant", ...}
await logos.invoke("self.flow.modality", observer)      # → "chat" | "research" | "collaboration" | "none"
await logos.invoke("self.flow.entropy", observer)       # → {"entropy": 1.0, ...}

# Start/stop flows
await logos.invoke("self.flow.start", observer, modality="chat")
await logos.invoke("self.flow.stop", observer)

# Modality-specific sub-paths
await logos.invoke("self.flow.chat.context", observer)  # → context window state
await logos.invoke("self.flow.chat.history", observer)  # → chat history
await logos.invoke("self.flow.research.tree", observer) # → hypothesis tree
await logos.invoke("self.flow.collaboration.board", observer)  # → blackboard
```

---

## Chat Modality

### Overview

Chat manages turn-based conversation with automatic context management:

```
User Message → Add to Context → Agent Process → Response → Turn Complete
                    ↓
            (Overflow) → Sliding/Summarizing Strategy
```

### Key Types

```python
from agents.f import ChatFlow, Turn, Message, SlidingContext, ChatConfig

@dataclass
class Turn:
    turn_number: int
    user_message: Message
    assistant_response: Message
    tokens_in: int
    tokens_out: int
    duration: float  # seconds

@dataclass
class Message:
    role: Literal["user", "assistant", "system"]
    content: str
    tokens: int | None = None
```

### Usage Pattern

```python
from agents.f import ChatFlow, ChatConfig

# Create chat flow with config
config = ChatConfig(
    context_window=128000,    # Max tokens in context
    context_strategy="sliding",  # sliding | summarize | forget
    max_turns=50,              # Max turns before reset
)

# The ChatFlow wraps an agent
chat = ChatFlow(agent=my_agent, config=config)

# Send messages and receive responses
response = await chat.send_message("Hello, how are you?")
print(response)  # Agent's response

# Stream tokens
async for token in chat.stream_response("Tell me a story"):
    print(token, end="", flush=True)

# Access history
history = chat.get_history()  # List[Turn]
metrics = chat.get_metrics()  # Turn counts, token usage
```

### Context Strategies

| Strategy | Behavior | When to Use |
|----------|----------|-------------|
| `sliding` | Drop oldest messages when full | General conversation |
| `summarize` | Compress old messages to summary | Long sessions |
| `forget` | Clear context each turn | Stateless interactions |

---

## Research Modality

### Overview

Research enables tree-of-thought exploration with hypothesis tracking:

```
Question → Root Hypothesis → Branches (Evidence) → Synthesis
              ↓
         Supporting    Refuting    Child Hypotheses
         Evidence      Evidence
```

### Key Types

```python
from agents.f.modalities.research import (
    ResearchFlow, HypothesisTree, Hypothesis,
    Evidence, Insight, Synthesis, HypothesisStatus
)

class HypothesisStatus(Enum):
    EXPLORING = "exploring"     # Under investigation
    SUPPORTED = "supported"     # Strong evidence for
    REFUTED = "refuted"         # Strong evidence against
    INCONCLUSIVE = "inconclusive"

@dataclass
class Hypothesis:
    id: str
    content: str
    status: HypothesisStatus
    confidence: float  # 0.0 - 1.0
    supporting_evidence: list[Evidence]
    refuting_evidence: list[Evidence]
    children: list[Hypothesis]
```

### Usage Pattern

```python
from agents.f.modalities.research import ResearchFlow, ResearchConfig

config = ResearchConfig(
    max_branches=5,   # Max hypotheses per node
    max_depth=3,      # Max tree depth
    convergence_threshold=0.8,  # When to synthesize
)

research = ResearchFlow(agent=my_agent, config=config)

# Start with a question
await research.ask("What causes climate change?")

# Explore hypotheses
branch = await research.branch("Greenhouse gases are the primary driver")
await research.support(branch.id, Evidence(content="CO2 correlates with temperature"))
await research.refute(branch.id, Evidence(content="But lag in ice core data..."))

# Get current tree
tree = research.tree
print(f"Root: {tree.root.content}")
print(f"Branches: {len(tree.branches)}")

# Synthesize insights
synthesis = await research.synthesize()
for insight in synthesis.insights:
    print(f"- {insight.content} (confidence: {insight.confidence})")
```

### AGENTESE Integration

```python
# Get hypothesis tree
await logos.invoke("self.flow.research.tree", observer)

# Create a new branch
await logos.invoke("self.flow.research.branch", observer, hypothesis="Solar activity is primary driver")

# Add evidence
await logos.invoke("self.flow.research.support", observer, hypothesis_id="h1", evidence="...")
await logos.invoke("self.flow.research.refute", observer, hypothesis_id="h1", evidence="...")

# Get synthesis
await logos.invoke("self.flow.research.synthesize", observer)
```

---

## Collaboration Modality

### Overview

Collaboration enables multi-agent coordination via a blackboard pattern:

```
Agent A → Contribution → Blackboard ← Query ← Agent B
            ↓
    Proposals → Voting → Decisions
```

### Key Types

```python
from agents.f.modalities.collaboration import (
    CollaborationFlow, Blackboard, Contribution,
    Vote, Proposal, Decision, AgentRole
)

class ContributionType(Enum):
    IDEA = "idea"
    QUESTION = "question"
    ANSWER = "answer"
    CRITIQUE = "critique"
    SYNTHESIS = "synthesis"

@dataclass
class Contribution:
    id: str
    agent_id: str
    content: str
    contribution_type: ContributionType
    confidence: float
    round: int
    timestamp: datetime
```

### Usage Pattern

```python
from agents.f.modalities.collaboration import CollaborationFlow, CollaborationConfig

config = CollaborationConfig(
    agent_ids=["planner", "critic", "implementer"],
    ordering="round_robin",  # round_robin | priority | free_form
    consensus_threshold=0.6,  # Vote threshold for decisions
)

collab = CollaborationFlow(agents=agent_dict, config=config)

# Post contributions
await collab.post(agent_id="planner", content="Let's build a cache layer", type="idea")
await collab.post(agent_id="critic", content="What about invalidation?", type="question")

# Create and vote on proposals
proposal = await collab.propose("Use LRU with 1hr TTL")
await collab.vote(proposal.id, agent_id="planner", vote="approve")
await collab.vote(proposal.id, agent_id="critic", vote="approve")
await collab.vote(proposal.id, agent_id="implementer", vote="abstain")

# Make decision
decision = await collab.decide(proposal.id)
print(f"Outcome: {decision.outcome}")  # approved | rejected | undecided
```

### Ordering Strategies

| Strategy | Behavior | When to Use |
|----------|----------|-------------|
| `round_robin` | Fixed rotation | Fair participation |
| `priority` | High priority agents first | Expert-led discussions |
| `free_form` | First-come, first-served | Dynamic brainstorming |

### AGENTESE Integration

```python
# Get blackboard state
await logos.invoke("self.flow.collaboration.board", observer)

# Post a contribution
await logos.invoke("self.flow.collaboration.post", observer, content="My idea", type="idea")

# Create and vote on proposals
await logos.invoke("self.flow.collaboration.propose", observer, content="My proposal")
await logos.invoke("self.flow.collaboration.vote", observer, proposal_id="p1", vote="approve")

# Get decision
await logos.invoke("self.flow.collaboration.decide", observer, proposal_id="p1")
```

---

## Verification

### Test Chat Flow

```bash
cd impl/claude
uv run pytest agents/f/_tests/test_chat.py -v --tb=short
```

### Test Research Flow

```bash
uv run pytest agents/f/_tests/test_research.py -v --tb=short
```

### Test Collaboration Flow

```bash
uv run pytest agents/f/_tests/test_collaboration.py -v --tb=short
```

### Test AGENTESE Integration

```bash
uv run pytest protocols/agentese/_tests/test_self_flow.py -v --tb=short
```

---

## Common Pitfalls

### 1. Using Flow without Flux

**Problem**: Trying to use Flow modalities without stream processing.

**Solution**: Flow provides conversation *patterns*, not streaming. Combine with Flux if you need event-driven processing:

```python
from agents.flux import Flux
from agents.f import ChatFlow

# Lift chat agent to flux for stream processing
flux_chat = Flux.lift(chat_agent)
```

### 2. Forgetting Agent Requirement

**Problem**: ChatFlow/ResearchFlow require an underlying agent.

```python
# Wrong - missing agent
chat = ChatFlow(config=ChatConfig())  # TypeError!

# Right - provide agent
chat = ChatFlow(agent=my_agent, config=ChatConfig())
```

### 3. Context Overflow

**Problem**: Context grows beyond window without handling.

**Solution**: Choose appropriate context strategy:

```python
config = ChatConfig(
    context_window=128000,
    context_strategy="summarize",  # Auto-compress when full
    summarization_threshold=0.8,   # Trigger at 80% capacity
)
```

---

## Related Skills

- [flux-agent.md](flux-agent.md) - Stream processing (different from Flow modalities)
- [polynomial-agent.md](polynomial-agent.md) - State-dependent agents (FLOW_POLYNOMIAL)
- [agentese-path.md](agentese-path.md) - Adding new AGENTESE paths

---

## Changelog

- 2025-12-16: Created with Chat, Research, Collaboration modalities
- 2025-12-16: Added AGENTESE `self.flow.*` integration
