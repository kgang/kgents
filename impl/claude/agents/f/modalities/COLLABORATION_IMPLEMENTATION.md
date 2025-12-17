# Collaboration Modality Implementation

**Status**: ✅ Complete (Phase 5)
**Date**: 2025-12-16
**Tests**: 24/24 passing

## Overview

This implementation provides the Collaboration modality for F-gent Flow, enabling multi-agent collaboration via the blackboard pattern.

## Files Created

### 1. `/impl/claude/agents/f/modalities/blackboard.py`

Core blackboard data structures:

- **`Contribution`**: A single agent's contribution to the blackboard
  - Tracks: id, agent_id, agent_role, content, type, references, confidence, round, timestamp
  - Supports 6 contribution types: IDEA, CRITIQUE, QUESTION, EVIDENCE, SYNTHESIS, DECISION

- **`Vote`**: A vote on a proposal
  - Tracks: voter_id, voter_role, proposal_id, choice, weight, reasoning

- **`Proposal`**: An item requiring group decision
  - Contains: id, contribution_id, title, description, proposed_by, votes

- **`Decision`**: A resolved proposal
  - Contains: proposal_id, outcome, method, evidence, reasoning

- **`Query`**: Filter for reading contributions
  - Supports filtering by: agent_id, agent_role, contribution_type, confidence, round, references, custom_filter

- **`AgentRole`**: Definition of an agent's role in collaboration
  - Contains: id, name, description, permissions, priority, specialization

- **`Blackboard`**: Shared state for multi-agent collaboration
  - Methods: `post()`, `read()`, `propose()`, `decide()`

### 2. `/impl/claude/agents/f/modalities/collaboration.py`

Collaboration flow implementation:

#### Contribution Ordering

- **`RoundRobinOrder`**: Fixed turn-taking order
  - Agents contribute in priority order
  - Cycles back after full round

- **`PriorityOrder`**: Dynamic priority-based ordering
  - Highest pending priority goes first
  - Supports runtime priority updates

- **`FreeFormOrder`**: Asynchronous contribution queue
  - Any agent can request contribution at any time
  - Uses `asyncio.Queue`

#### Consensus Mechanisms

- **`resolve_by_vote()`**: Democratic voting
  - Counts approve/reject votes by weight
  - Compares against consensus_threshold
  - Only agents with VOTE permission can vote

- **`resolve_by_moderator()`**: Moderator decision
  - Single moderator agent makes final call
  - Receives proposal + context + guidelines

- **`resolve_by_timestamp()`**: First-come-first-served
  - Earliest contribution wins conflicts

#### Main Class: `CollaborationFlow`

Wraps `FlowAgent` and implements collaboration-specific logic:

- **`start(problem)`**: Initialize blackboard with problem
- **`run_round()`**: Execute one contribution round
  - Agents read board (permission-checked)
  - Agents generate contributions
  - Posts to blackboard
  - Handles proposals
- **`build_consensus()`**: Resolve pending proposals
- **`harvest()`**: Extract final results

### 3. `/impl/claude/agents/f/_tests/test_collaboration.py`

Comprehensive test suite (24 tests):

#### Blackboard Tests (8 tests)
- Blackboard creation
- Post and read operations
- Query filtering by: agent_id, type, confidence, round
- Propose and decide workflow

#### Contribution Ordering Tests (6 tests)
- Round-robin creation and cycling
- Priority order respects dynamic priorities
- Free-form queue operations

#### Consensus Mechanism Tests (3 tests)
- Voting consensus (approved/rejected)
- Moderator decision
- Permission enforcement

#### Collaboration Flow Tests (7 tests)
- Start collaboration
- Run basic round
- Multiple agents
- Round limit enforcement
- Permission checking
- Contribution type handling
- Harvest results

## Key Features

### 1. Role-Based Permissions

Eight permission types:
- `READ_ALL`: Read any contribution
- `READ_OWN`: Read only own contributions
- `POST`: Add contributions
- `CRITIQUE`: Challenge others
- `PROPOSE`: Submit proposals
- `VOTE`: Vote on proposals
- `MODERATE`: Resolve conflicts
- `DECIDE`: Make final decisions

### 2. Contribution Types

Six contribution types:
- `IDEA`: New proposal or approach
- `CRITIQUE`: Challenge to existing contribution
- `QUESTION`: Request for clarification
- `EVIDENCE`: Supporting or contradicting data
- `SYNTHESIS`: Combining multiple contributions
- `DECISION`: Final call on a topic

### 3. Flexible Ordering

Three ordering strategies:
- Round-robin: Predictable, fair turn-taking
- Priority: Dynamic prioritization based on importance
- Free-form: Asynchronous, reactive contributions

### 4. Consensus Building

Three consensus strategies:
- Vote: Democratic decision-making with weighted votes
- Moderator: Single authority resolution
- Timestamp: First-come-first-served (simple)

## Configuration

Via `FlowConfig`:

```python
config = FlowConfig(
    modality="collaboration",

    # Agents
    agents=["analyst", "critic", "synthesizer"],
    moderator_id="moderator",

    # Contribution
    contribution_order="round_robin",  # or "priority" or "free"
    max_contributions_per_round=10,
    round_limit=10,
    contribution_timeout=30.0,

    # Blackboard
    blackboard_capacity=100,
    allow_references=True,
    require_confidence=True,

    # Consensus
    consensus_threshold=0.67,
    conflict_strategy="vote",  # or "moderator" or "timestamp"

    # Termination
    terminate_on_consensus=True,
    minimum_contributions=3,
)
```

## Usage Example

```python
from agents.f.config import FlowConfig
from agents.f.flow import Flow
from agents.f.modalities.blackboard import AgentRole
from agents.f.modalities.collaboration import CollaborationFlow
from agents.f.state import Permission

# Define roles
roles = [
    AgentRole(
        id="analyst",
        name="Analyst",
        permissions={Permission.READ_ALL, Permission.POST},
    ),
    AgentRole(
        id="critic",
        name="Critic",
        permissions={Permission.READ_ALL, Permission.CRITIQUE, Permission.VOTE},
    ),
]

# Create agents (your actual agent implementations)
agents = {
    "analyst": AnalystAgent(),
    "critic": CriticAgent(),
}

# Configure
config = FlowConfig(
    modality="collaboration",
    consensus_threshold=0.67,
)

# Create collaboration flow
flow_agent = Flow.lift_multi(agents, config)
collab = CollaborationFlow(flow_agent, agents, roles, config)

# Run collaboration
await collab.start("How should we solve problem X?")

# Execute rounds
async for contribution in collab.run_round():
    print(f"[{contribution.agent_role}] {contribution.content}")

# Build consensus
async for decision in collab.build_consensus():
    print(f"Decision: {decision.outcome}")

# Harvest results
result = await collab.harvest()
print(f"Final synthesis: {result.final_synthesis}")
```

## Integration with F-gent Architecture

### Polynomial Integration

Uses `COLLABORATION_POLYNOMIAL` from `polynomial.py`:

- **Positions**: DORMANT → STREAMING → CONVERGING → COLLAPSED
- **Directions**: State-dependent valid inputs
- **Transitions**: Collaboration-specific state changes

### State Machine

```
DORMANT ──start──> STREAMING
   ↑                  │
   │                  │ (stop)
   │                  ↓
COLLAPSED <──── CONVERGING
```

### Flow Agent Integration

- Wraps `FlowAgent` for collaboration-specific logic
- Uses `Flow.lift_multi()` for multi-agent setup
- Compatible with existing Flow infrastructure

## Test Results

All 24 tests passing:

```
test_blackboard_creation .......................... PASSED
test_post_contribution ............................ PASSED
test_read_all_contributions ....................... PASSED
test_read_with_query_agent_id ..................... PASSED
test_read_with_query_type ......................... PASSED
test_read_with_query_confidence ................... PASSED
test_read_with_query_round ........................ PASSED
test_propose_and_decide ........................... PASSED
test_round_robin_creation ......................... PASSED
test_round_robin_next_agent ....................... PASSED
test_priority_order_creation ...................... PASSED
test_priority_order_respects_priorities ........... PASSED
test_free_form_order_creation ..................... PASSED
test_free_form_order_queue ........................ PASSED
test_voting_consensus_approved .................... PASSED
test_voting_consensus_rejected .................... PASSED
test_moderator_decision ........................... PASSED
test_collaboration_start .......................... PASSED
test_run_round_basic .............................. PASSED
test_run_round_multiple_agents .................... PASSED
test_round_limit_enforcement ...................... PASSED
test_permissions_checking ......................... PASSED
test_contribution_type_handling ................... PASSED
test_harvest ...................................... PASSED
```

## Future Enhancements

Potential improvements for future iterations:

1. **LLM Integration**: Real agent implementations (currently mocked in tests)
2. **Metrics**: Track collaboration health, participation balance, consensus rate
3. **Advanced Queries**: Full-text search, semantic similarity
4. **Conflict Detection**: Automatic identification of contradicting contributions
5. **Dynamic Role Assignment**: Agents change roles based on context
6. **Nested Blackboards**: Hierarchical problem decomposition
7. **Contribution Pruning**: Remove low-value contributions after rounds
8. **Vote Delegation**: Agents can delegate voting to others

## Specification Compliance

This implementation faithfully follows `spec/f-gents/collaboration.md`:

- ✅ Blackboard data structures
- ✅ Agent roles with permissions
- ✅ Three contribution ordering strategies
- ✅ Three consensus mechanisms
- ✅ Full collaboration protocol (start → rounds → consensus → harvest)
- ✅ Configuration via FlowConfig
- ✅ Integration with Flow polynomial

## References

- **Spec**: `/spec/f-gents/collaboration.md`
- **Core Flow**: `/impl/claude/agents/f/flow.py`
- **Polynomial**: `/impl/claude/agents/f/polynomial.py`
- **State**: `/impl/claude/agents/f/state.py`
- **Config**: `/impl/claude/agents/f/config.py`
