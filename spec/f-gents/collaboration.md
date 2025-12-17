# Collaboration Flow: Multi-Agent Blackboard

> *"No single agent has the full picture. The blackboard is where partial views become shared understanding."*

---

## Overview

Collaboration Flow is the F-gent modality for **multi-agent projects** using the blackboard pattern.

**Key characteristics**:
- Multiple agents contribute to shared state ("blackboard")
- Read/write access control per agent role
- Consensus mechanisms for conflict resolution
- Round-based or continuous contribution

This modality enables agents with different specializations to collaborate on complex problems.

---

## The Collaboration Polynomial

```python
COLLABORATION_POLYNOMIAL = FlowPolynomial(
    positions=frozenset([
        FlowState.DORMANT,      # Waiting for problem statement
        FlowState.STREAMING,    # Agents contributing
        FlowState.CONVERGING,   # Building consensus
        FlowState.COLLAPSED,    # Consensus reached or round limit
    ]),
    directions=lambda state: {
        FlowState.DORMANT: frozenset(["start", "configure", "add_agent"]),
        FlowState.STREAMING: frozenset(["post", "read", "vote", "stop"]),
        FlowState.CONVERGING: frozenset(["vote", "moderate", "decide"]),
        FlowState.COLLAPSED: frozenset(["harvest", "reset"]),
    }[state],
    transition=collaboration_transition,
)
```

---

## The Blackboard

The blackboard is shared state where agents post contributions.

```python
@dataclass
class Blackboard:
    """Shared state for multi-agent collaboration."""
    problem: str                        # Original problem statement
    contributions: list[Contribution]   # All posted contributions
    proposals: list[Proposal]           # Items requiring decision
    decisions: list[Decision]           # Resolved proposals
    current_round: int                  # Contribution round
    metadata: dict[str, Any]            # Arbitrary shared state

    def post(self, contribution: Contribution) -> None:
        """Add a contribution to the board."""
        self.contributions.append(contribution)

    def read(self, query: Query) -> list[Contribution]:
        """Read contributions matching query."""
        return [c for c in self.contributions if query.matches(c)]

    def propose(self, proposal: Proposal) -> None:
        """Submit something for group decision."""
        self.proposals.append(proposal)

    def decide(self, proposal_id: str, decision: Decision) -> None:
        """Record a decision on a proposal."""
        self.decisions.append(decision)
        # Remove from pending
        self.proposals = [p for p in self.proposals if p.id != proposal_id]
```

### Contribution

```python
@dataclass
class Contribution:
    """A single agent's contribution to the blackboard."""
    id: str
    agent_id: str                       # Who contributed
    agent_role: str                     # Their role (analyst, critic, etc.)
    content: str                        # The contribution text
    contribution_type: ContributionType # idea | critique | question | evidence | synthesis
    references: list[str]               # IDs of contributions this responds to
    confidence: float                   # Agent's confidence in this
    round: int                          # Which round
    timestamp: datetime

class ContributionType(Enum):
    IDEA = "idea"               # New proposal or approach
    CRITIQUE = "critique"       # Challenge to existing contribution
    QUESTION = "question"       # Request for clarification
    EVIDENCE = "evidence"       # Supporting or contradicting data
    SYNTHESIS = "synthesis"     # Combining multiple contributions
    DECISION = "decision"       # Final call on a topic
```

---

## Agent Roles

Collaboration Flow uses role-based agents:

```python
@dataclass
class AgentRole:
    """Definition of an agent's role in collaboration."""
    id: str
    name: str                           # Human-readable name
    description: str                    # What this role does
    permissions: set[Permission]        # What actions allowed
    priority: int                       # Order in round-robin
    specialization: str                 # Area of expertise

class Permission(Enum):
    READ_ALL = "read_all"               # Read any contribution
    READ_OWN = "read_own"               # Read only own contributions
    POST = "post"                       # Add contributions
    CRITIQUE = "critique"               # Challenge others
    PROPOSE = "propose"                 # Submit proposals
    VOTE = "vote"                       # Vote on proposals
    MODERATE = "moderate"               # Resolve conflicts
    DECIDE = "decide"                   # Make final decisions
```

### Standard Role Templates

| Role | Permissions | Purpose |
|------|-------------|---------|
| **Analyst** | READ_ALL, POST, PROPOSE | Generate ideas and analysis |
| **Critic** | READ_ALL, CRITIQUE, VOTE | Challenge and improve ideas |
| **Synthesizer** | READ_ALL, POST, DECIDE | Combine insights into conclusions |
| **Moderator** | READ_ALL, MODERATE, DECIDE | Resolve conflicts, guide process |
| **Observer** | READ_ALL | Watch without contributing |

---

## Contribution Order

How agents take turns contributing:

### Round Robin

```python
class RoundRobinOrder:
    """Each agent contributes once per round, in fixed order."""

    def __init__(self, agents: list[AgentRole]):
        self.agents = sorted(agents, key=lambda a: a.priority)
        self.current_index = 0

    def next_agent(self) -> AgentRole:
        agent = self.agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.agents)
        return agent

    def is_round_complete(self) -> bool:
        return self.current_index == 0
```

### Priority-Based

```python
class PriorityOrder:
    """Agents with pending high-priority contributions go first."""

    def __init__(self, agents: list[AgentRole]):
        self.agents = agents
        self.pending_priorities: dict[str, float] = {}

    def set_priority(self, agent_id: str, priority: float) -> None:
        self.pending_priorities[agent_id] = priority

    def next_agent(self) -> AgentRole:
        # Highest priority first
        sorted_agents = sorted(
            self.agents,
            key=lambda a: self.pending_priorities.get(a.id, 0),
            reverse=True,
        )
        return sorted_agents[0]
```

### Free-Form

```python
class FreeFormOrder:
    """Any agent can contribute at any time."""

    def __init__(self, agents: list[AgentRole]):
        self.agents = agents
        self.contribution_queue: asyncio.Queue[AgentRole] = asyncio.Queue()

    async def request_contribution(self, agent: AgentRole) -> None:
        await self.contribution_queue.put(agent)

    async def next_agent(self) -> AgentRole:
        return await self.contribution_queue.get()
```

---

## Consensus Mechanisms

When agents disagree, consensus is needed.

### Voting

```python
async def resolve_by_vote(
    self,
    proposal: Proposal,
    voters: list[AgentRole],
) -> Decision:
    """Resolve proposal via agent voting."""
    votes: dict[str, Vote] = {}

    for voter in voters:
        if Permission.VOTE in voter.permissions:
            vote = await self._get_vote(voter, proposal)
            votes[voter.id] = vote

    # Count votes
    approve_weight = sum(
        v.weight for v in votes.values() if v.choice == "approve"
    )
    reject_weight = sum(
        v.weight for v in votes.values() if v.choice == "reject"
    )
    total_weight = sum(v.weight for v in votes.values())

    if approve_weight / total_weight >= self.config.consensus_threshold:
        return Decision(
            proposal_id=proposal.id,
            outcome="approved",
            method="vote",
            evidence=votes,
        )
    else:
        return Decision(
            proposal_id=proposal.id,
            outcome="rejected",
            method="vote",
            evidence=votes,
        )
```

### Moderator Decision

```python
async def resolve_by_moderator(
    self,
    proposal: Proposal,
    context: list[Contribution],
) -> Decision:
    """Moderator agent makes final decision."""
    moderator = self._get_moderator()

    decision = await moderator.invoke(ModeratorInput(
        proposal=proposal,
        context=context,
        guidelines=self.config.moderation_guidelines,
    ))

    return Decision(
        proposal_id=proposal.id,
        outcome=decision.outcome,
        method="moderator",
        reasoning=decision.reasoning,
    )
```

### Timestamp (First Wins)

```python
async def resolve_by_timestamp(
    self,
    conflicting: list[Contribution],
) -> Contribution:
    """Earliest contribution wins conflicts."""
    return min(conflicting, key=lambda c: c.timestamp)
```

---

## Collaboration Protocol

### Phase 1: Problem Statement

```python
async def start(self, problem: str) -> None:
    """Initialize collaboration with problem statement."""
    self.blackboard = Blackboard(problem=problem)
    self._state = FlowState.STREAMING

    # Notify all agents
    for agent in self.agents:
        await agent.notify(NewProblemEvent(problem))
```

### Phase 2: Contribution Rounds

```python
async def run_round(self) -> AsyncIterator[Contribution]:
    """Execute one round of contributions."""
    self.blackboard.current_round += 1

    for agent in self.order.agents_for_round():
        # Agent reads board
        context = self.blackboard.read(agent.read_query())

        # Agent generates contribution
        contribution = await agent.invoke(ContributionRequest(
            problem=self.blackboard.problem,
            context=context,
            round=self.blackboard.current_round,
        ))

        if contribution:
            self.blackboard.post(contribution)
            yield contribution

            # Check for proposals
            if contribution.contribution_type == ContributionType.DECISION:
                await self._handle_proposal(contribution)
```

### Phase 3: Consensus Building

```python
async def build_consensus(self) -> AsyncIterator[Decision]:
    """Resolve pending proposals."""
    self._state = FlowState.CONVERGING

    for proposal in self.blackboard.proposals:
        decision = await self._resolve_proposal(proposal)
        self.blackboard.decide(proposal.id, decision)
        yield decision
```

### Phase 4: Harvest

```python
async def harvest(self) -> CollaborationResult:
    """Extract final result from blackboard."""
    return CollaborationResult(
        problem=self.blackboard.problem,
        decisions=self.blackboard.decisions,
        contributions=self.blackboard.contributions,
        rounds_completed=self.blackboard.current_round,
        final_synthesis=await self._synthesize_outcome(),
    )
```

---

## Configuration

```python
@dataclass
class CollaborationConfig:
    """Collaboration-specific configuration."""

    # Agents
    agents: list[AgentRole] = field(default_factory=list)
    moderator_id: str | None = None     # ID of moderator agent

    # Contribution
    contribution_order: ContributionOrder = ContributionOrder.ROUND_ROBIN
    max_contributions_per_round: int = 10
    round_limit: int = 10
    contribution_timeout: float = 30.0

    # Blackboard
    blackboard_capacity: int = 100      # Max contributions
    allow_references: bool = True       # Can contributions cite others?
    require_confidence: bool = True     # Must include confidence score?

    # Consensus
    consensus_threshold: float = 0.67   # 2/3 majority
    conflict_strategy: ConflictStrategy = ConflictStrategy.VOTE
    auto_propose_threshold: int = 3     # Auto-propose after N related contributions

    # Termination
    terminate_on_consensus: bool = True
    terminate_on_rounds: bool = True
    minimum_contributions: int = 3      # Min before allowing termination

    # Moderation
    moderation_guidelines: str | None = None
    escalation_threshold: int = 3       # Escalate to moderator after N failed votes
```

---

## Usage Examples

### Basic Multi-Agent Brainstorm

```python
from agents.f import Flow, FlowConfig

# Define agents
agents = [
    AgentRole(id="analyst", name="Analyst", permissions={Permission.READ_ALL, Permission.POST}),
    AgentRole(id="critic", name="Critic", permissions={Permission.READ_ALL, Permission.CRITIQUE}),
    AgentRole(id="synth", name="Synthesizer", permissions={Permission.READ_ALL, Permission.DECIDE}),
]

config = FlowConfig(
    modality="collaboration",
    agents=[a.id for a in agents],
    consensus_threshold=0.67,
)

collab = Flow.lift_multi(agent_pool, config)

async for contribution in collab.start(["How should we approach AI safety?"]):
    print(f"[{contribution.agent_role}] {contribution.content}")
```

### Design Review

```python
# Specialized roles for code review
agents = [
    AgentRole(id="author", permissions={Permission.READ_ALL, Permission.POST}),
    AgentRole(id="reviewer1", permissions={Permission.READ_ALL, Permission.CRITIQUE, Permission.VOTE}),
    AgentRole(id="reviewer2", permissions={Permission.READ_ALL, Permission.CRITIQUE, Permission.VOTE}),
    AgentRole(id="maintainer", permissions={Permission.READ_ALL, Permission.DECIDE}),
]

config = FlowConfig(
    modality="collaboration",
    contribution_order="round_robin",
    consensus_threshold=0.75,  # Need 3/4 approval
)
```

### Debate Format

```python
# Structured debate
agents = [
    AgentRole(id="pro", permissions={Permission.POST, Permission.READ_ALL}),
    AgentRole(id="con", permissions={Permission.POST, Permission.READ_ALL}),
    AgentRole(id="judge", permissions={Permission.READ_ALL, Permission.DECIDE}),
]

config = FlowConfig(
    modality="collaboration",
    round_limit=5,              # 5 rounds of debate
    contribution_order="round_robin",
)
```

---

## Metrics

| Metric | Description |
|--------|-------------|
| `contributions_total` | Total contributions posted |
| `contributions_per_agent` | Distribution across agents |
| `rounds_completed` | Number of full rounds |
| `proposals_made` | Total proposals submitted |
| `decisions_reached` | Proposals that reached consensus |
| `conflicts_resolved` | Disagreements successfully resolved |
| `consensus_rate` | Decisions / Proposals |
| `average_confidence` | Mean contribution confidence |

---

## Anti-Patterns

### 1. Single Agent Dominance

```python
# BAD: One agent does everything
agents = [AgentRole(id="god", permissions=all_permissions)]

# GOOD: Distributed roles
agents = [analyst, critic, synthesizer]  # Different strengths
```

### 2. No Conflict Resolution

```python
# BAD: Ignore disagreements
config = FlowConfig(conflict_strategy=None)
# Deadlocks forever

# GOOD: Clear resolution mechanism
config = FlowConfig(conflict_strategy="vote", consensus_threshold=0.67)
```

### 3. Infinite Rounds

```python
# BAD: No termination
config = FlowConfig(round_limit=None, terminate_on_consensus=False)
# Runs forever

# GOOD: Bounded exploration
config = FlowConfig(round_limit=10, terminate_on_consensus=True)
```

### 4. Echo Chamber

```python
# BAD: All agents agree always
agents = [clone_of_same_agent] * 5

# GOOD: Diverse perspectives
agents = [optimist, pessimist, pragmatist, expert, generalist]
```

---

## See Also

- `README.md` - F-gent overview
- `research.md` - Tree of thought (single-agent exploration)
- `spec/town/operad.md` - Agent Town uses similar patterns
- Pattern: "Blackboard Architecture" (Hayes-Roth, 1985)
