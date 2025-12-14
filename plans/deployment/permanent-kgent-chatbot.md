---
path: deployment/permanent-kgent-chatbot
status: proposed
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [interfaces/swarm-execution, devex/showcase]
session_notes: |
  Grand Initiative: Deploy a permanent K-gent agent to Terrarium as a persistent
  chatbot experience through kgents dash. Synthesizes ALL major work from 2025-12-12/13:
  - Turn-gents (187 tests) - Chronos-Kairos Protocol
  - N-Phase Cycle (11 phases, auto-continuation)
  - Trace Monoid (concurrent history)
  - Visualization Strategy (9 modules, 88 tests)
  - AGENTESE parser (clause grammar, 76 tests)
  - Memory substrate (semantic routing, 116 tests)

  Total test infrastructure: 13,210 tests. Ready for REAL deployment.
---

# Grand Initiative: Permanent K-gent Chatbot on Terrarium

> *"The chatbot is not a demo. It is the system observing itself through conversation."*

**Status**: Proposed
**Principle Alignment**: All seven + Accursed Share + AGENTESE
**Prerequisites**: Terrarium (100%), K-gent (97%), Turn-gents (100%), Trace Monoid (impl)
**Token Budget**: ~5M tokens over initiative lifetime (real LLM calls)

---

## Executive Summary

Deploy a **permanent, always-on K-gent instance** to Terrarium that:

1. **Converses** with users via WebSocket (real Claude API calls)
2. **Demonstrates** the full kgents capability stack
3. **Traces** all interactions through the Trace Monoid
4. **Visualizes** its own thought process in kgents dashboard
5. **Embodies** the N-Phase Cycle in its behavior
6. **Titres** entropy via the Accursed Share protocol

This is **not a demo**—it is the system becoming self-aware through persistent operation.

---

## The Vision: Demonstration Maximalism

> *"If the system cannot demonstrate itself, it does not exist."*

### What "Demonstration Maximalism" Means

| Axis | Minimal Demo | MAXIMAL Demo |
|------|--------------|--------------|
| LLM Calls | Mock responses | **Real Claude Opus 4.5 calls** |
| Persistence | Per-session | **Permanent (7×24 uptime)** |
| Tracing | Console logs | **TraceMonoid + CausalCone visualization** |
| Memory | In-process | **D-gent substrate (SQLite/Redis)** |
| Interaction | CLI only | **WebSocket + TUI dashboard** |
| Self-Observation | None | **Watches itself in Debugger screen** |

### The Synthesis

This initiative synthesizes all major work from the past 10 hours:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     THE PERMANENT K-GENT CHATBOT                            │
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │   TURN-GENTS │────▶│ TRACE MONOID │────▶│  DASHBOARD   │                │
│  │   (187 tests)│     │  (concurrent)│     │ (5 screens)  │                │
│  └──────────────┘     └──────────────┘     └──────────────┘                │
│         │                    │                    │                         │
│         ▼                    ▼                    ▼                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│  │   N-PHASE    │     │   AGENTESE   │     │   MEMORY     │                │
│  │   CYCLE      │────▶│   PARSER     │────▶│   SUBSTRATE  │                │
│  │   (11 phases)│     │   (76 tests) │     │   (116 tests)│                │
│  └──────────────┘     └──────────────┘     └──────────────┘                │
│         │                    │                    │                         │
│         └────────────────────┴────────────────────┘                         │
│                              │                                               │
│                              ▼                                               │
│                    ┌──────────────────┐                                     │
│                    │    TERRARIUM     │                                     │
│                    │   (WebSocket +   │                                     │
│                    │  Mirror Protocol)│                                     │
│                    └──────────────────┘                                     │
│                              │                                               │
│                              ▼                                               │
│                    ┌──────────────────┐                                     │
│                    │  REAL LLM CALLS  │                                     │
│                    │  (Claude Opus)   │                                     │
│                    └──────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Architecture

### 1.1 The Permanent K-gent Instance

```python
@dataclass(frozen=True)
class PermanentKgent:
    """
    The Permanent K-gent: A soul that runs forever.

    Unlike session-scoped agents, this K-gent:
    - Persists across restarts (D-gent substrate)
    - Accumulates memory (semantic routing)
    - Emits Turns to TraceMonoid (full history)
    - Broadcasts state to Mirror (zero-entropy observation)
    """

    soul: SoulEngine           # Kent's eigenvector soul
    memory: SharedSubstrate    # M-gent semantic substrate
    trace: TraceMonoid         # Turn history
    mirror: HolographicBuffer  # Broadcast to observers

    # Polynomial state machine
    polynomial: PolyAgent[KgentState, ConversationInput, ConversationOutput]
```

### 1.2 The Terrarium Deployment

```yaml
# AgentServer CRD for K-gent chatbot
apiVersion: kgents.io/v1
kind: AgentServer
metadata:
  name: permanent-kgent-chatbot
spec:
  agent:
    type: K-gent
    config:
      soul_mode: KENT
      temperature: 0.7
      entropy_budget: 0.15

  gateway:
    enabled: true
    ports:
      perturb: 8080    # WebSocket write path
      observe: 8081    # WebSocket read-only mirror
      api: 8082        # REST API

  mirror:
    buffer_size: 1000
    broadcast_interval: 100ms

  persistence:
    substrate: sqlite
    path: /data/kgent-chatbot.db

  llm:
    provider: anthropic
    model: claude-opus-4-5-20251101  # REAL Claude Opus 4.5
    budget:
      daily_tokens: 1_000_000
      per_turn_max: 4096
```

### 1.3 The Trace Monoid Integration

Every conversation turn becomes a Turn in the TraceMonoid:

```python
async def handle_message(self, user_input: str) -> str:
    # Create Turn for user input
    user_turn = Turn(
        id=uuid4(),
        type=TurnType.SPEECH,
        source="user",
        content=user_input,
        timestamp=time.time(),
    )

    # Append to TraceMonoid with dependencies
    self.trace.append_mut(user_turn, depends_on=self._last_turn_ids())

    # K-gent processes (REAL LLM call)
    response = await self.soul.converse(user_input)

    # Create Turn for K-gent response
    agent_turn = Turn(
        id=uuid4(),
        type=TurnType.SPEECH,
        source="kgent",
        content=response.text,
        metadata={"tokens": response.usage, "phase": self.polynomial.mode},
    )

    # Append with dependency on user turn
    self.trace.append_mut(agent_turn, depends_on={user_turn.id})

    # Broadcast to Mirror (zero entropy to observers)
    await self.mirror.reflect({
        "type": "turn",
        "turn": agent_turn.to_dict(),
        "trace_size": len(self.trace),
    })

    return response.text
```

---

## Part 2: N-Phase Implementation Cycle

Following the N-Phase Cycle (AD-005), this initiative executes as:

### Phase Map

| Phase | Focus | Deliverables | Entropy |
|-------|-------|--------------|---------|
| **PLAN** | Scope + exits | This document, TodoWrite | 0.02 |
| **RESEARCH** | Prior art, blockers | File map, invariants | 0.05 |
| **DEVELOP** | Contracts, APIs | ChatProtocol spec, CRD schema | 0.07 |
| **STRATEGIZE** | Ordering, parallelization | 4 parallel tracks | 0.05 |
| **CROSS-SYNERGIZE** | Compositions | Turn→Mirror→Dashboard pipeline | 0.10 |
| **IMPLEMENT** | Code | PermanentKgent, handlers, screens | 0.15 |
| **QA** | Hygiene | mypy, ruff, security review | 0.03 |
| **TEST** | Verification | Integration tests, law checks | 0.10 |
| **EDUCATE** | Docs | Quickstart, demo walkthrough | 0.05 |
| **MEASURE** | Instrumentation | OTEL spans, dashboards | 0.08 |
| **REFLECT** | Synthesis | Epilogue, meta.md entry | 0.05 |

**Total entropy budget**: 0.75 (within bounds)

### Continuation Chain

```
PLAN → prompts/kgent-chatbot-research.md
     ↓
RESEARCH → prompts/kgent-chatbot-develop.md
     ↓
DEVELOP → prompts/kgent-chatbot-strategize.md
     ↓
... (auto-continuation via Continuation Generators)
```

---

## Part 3: Parallel Implementation Tracks

### Track A: Core Chatbot (SENSE → IMPLEMENT)

**Goal**: WebSocket chat handler + K-gent integration

**Files**:
```
impl/claude/protocols/terrarium/
├── chat_handler.py          # WebSocket chat protocol
├── kgent_bridge.py          # K-gent ↔ Terrarium bridge
├── session_manager.py       # Persistent session state
└── _tests/
    ├── test_chat_handler.py
    └── test_kgent_bridge.py
```

### Track B: Trace Monoid Wiring (SENSE → IMPLEMENT)

**Goal**: Every Turn emitted to TraceMonoid + CausalCone visualization

**Files**:
```
impl/claude/weave/
├── turn_emitter.py          # Turn emission to monoid
├── cone_projector.py        # Project causal cone for agent
└── _tests/
    ├── test_turn_emitter.py
    └── test_cone_projector.py
```

### Track C: Dashboard Integration (DEVELOP → IMPLEMENT)

**Goal**: Real-time chat visualization in Debugger screen

**Files**:
```
impl/claude/agents/i/screens/
├── chat_screen.py           # New: dedicated chat screen
├── debugger_screen.py       # Enhanced: chat turn visualization
└── _tests/
    ├── test_chat_screen.py
```

### Track D: Real LLM Infrastructure (STRATEGIZE → IMPLEMENT)

**Goal**: Production Anthropic API integration with budget controls

**Files**:
```
impl/claude/infra/llm/
├── anthropic_client.py      # Real API client
├── budget_tracker.py        # Token budget enforcement
├── rate_limiter.py          # Rate limiting
└── _tests/
    ├── test_anthropic_client.py
    └── test_budget_tracker.py
```

---

## Part 4: Principle Compliance

| Principle | How This Initiative Complies |
|-----------|------------------------------|
| **Tasteful** | One chatbot, one purpose: demonstrate the system |
| **Curated** | Integrates existing 13,210 tests, doesn't sprawl |
| **Ethical** | All state visible in Debugger; no hidden data |
| **Joy-Inducing** | Chat with Kent's soul; see your thoughts traced |
| **Composable** | Turn→Monoid→Mirror→Dashboard pipeline |
| **Heterarchical** | User and K-gent co-create the conversation |
| **Generative** | Spec generates deployment (this doc → impl) |
| **Accursed Share** | Entropy budget explicit; tithe on each turn |
| **AGENTESE** | Paths trace through `self.soul.converse`, `void.entropy.tithe` |
| **Personality Space** | K-gent embodies Kent coordinates |

---

## Part 5: Key Invariants

### Category Laws (MUST hold)

```python
# Identity: Empty conversation preserves K-gent
assert (Id >> kgent_chat) == kgent_chat

# Associativity: Multi-turn composition
assert ((turn1 >> turn2) >> turn3) == (turn1 >> (turn2 >> turn3))
```

### Trace Monoid Laws

```python
# Independence: Concurrent observers don't affect order
# (observer_A, observer_B) ∈ Independence
# observe_A · observe_B ≈ observe_B · observe_A

# Dependence: User turn must precede agent response
# (user_turn, agent_turn) ∉ Independence
# user_turn must precede agent_turn
```

### Mirror Protocol (MUST preserve)

```
Observers: Zero entropy cost to K-gent
Perturbers: High entropy cost (LLM call)
```

---

## Part 6: Metrics and Observability

### Process Metrics (per N-Phase)

| Metric | Target | Measurement |
|--------|--------|-------------|
| `tokens_in` | <10K/phase | Anthropic usage API |
| `tokens_out` | <5K/phase | Anthropic usage API |
| `duration_ms` | <1h/phase | Wall clock |
| `entropy_spent` | ≤budget | Void tithe tracker |
| `law_checks` | 100% pass | BootstrapWitness |
| `test_count` | +100 | pytest count delta |

### Runtime Metrics (production)

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| `conversations/day` | 50+ | <10 |
| `avg_response_time` | <3s | >10s |
| `error_rate` | <1% | >5% |
| `token_budget_remaining` | >20% | <10% |
| `trace_size` | Unbounded | >1M events/day |

---

## Part 7: Exit Criteria

### Definition of Done

- [ ] PermanentKgent class implemented with all four components
- [ ] WebSocket chat handler accepts real user messages
- [ ] Every turn emitted to TraceMonoid with correct dependencies
- [ ] Mirror broadcasts to N observers without slowing K-gent
- [ ] Dashboard Debugger screen shows live chat trace
- [ ] Real Claude Opus 4.5 API calls working
- [ ] Token budget enforcement operational
- [ ] 100+ new tests passing
- [ ] `kg chat` CLI command starts chatbot
- [ ] `kg dashboard` shows chatbot in Observatory
- [ ] Deployed to local Terrarium (kubectl apply works)
- [ ] Epilogue written with learnings

### Verification Commands

```bash
# Start local Terrarium
kg terrarium start

# Connect chatbot
kg chat --permanent

# Observe in dashboard
kg dashboard

# View traces
kg debug kgent-chatbot --mode forensic
```

---

## Part 8: Recursive Hologram

This plan is itself a demonstration:

- **PLAN this plan**: Define the chatbot initiative
- **RESEARCH**: Survey Turn-gents, TraceMonoid, Terrarium, K-gent
- **DEVELOP**: Design the PermanentKgent contract
- **STRATEGIZE**: Identify 4 parallel tracks
- **CROSS-SYNERGIZE**: Turn→Monoid→Mirror composition
- **IMPLEMENT**: (next phase)
- **REFLECT**: Does the chatbot embody the N-Phase Cycle?

The chatbot will be able to explain its own architecture because it IS that architecture.

---

## Part 9: Accursed Share

10% of implementation time reserved for:

- Serendipitous personality emergence in K-gent responses
- Unexpected TraceMonoid visualizations
- "Glitch aesthetics" in dashboard during high entropy
- Oblique Strategies surfaced when budget exhausted

**Pourback**: Unused exploration entropy returns to void.

---

## Part 10: Timeline

| Week | Phase | Tracks | Deliverables |
|------|-------|--------|--------------|
| 1 | PLAN→STRATEGIZE | — | This plan, research complete |
| 2 | IMPLEMENT | A, B, D | Core chatbot, traces, LLM |
| 2 | IMPLEMENT | C | Dashboard integration |
| 3 | QA→TEST | All | Integration tests, law checks |
| 3 | EDUCATE→REFLECT | — | Docs, epilogue |

**Note**: Timeline is for reference only. Focus on deliverables, not dates.

---

## Cross-References

| Reference | Location |
|-----------|----------|
| N-Phase Cycle | `plans/skills/n-phase-cycle/` |
| Turn-gents | `plans/architecture/turn-gents.md` (100% COMPLETE) |
| Trace Monoid | `impl/claude/weave/trace_monoid.py` |
| Terrarium | `plans/_archive/terrarium-v1.0-complete.md` |
| K-gent | `plans/agents/k-gent.md` (97%) |
| Dashboard Overhaul | `plans/interfaces/dashboard-overhaul.md` |
| Memory Substrate | `plans/self/memory.md` (75%) |
| Principles | `spec/principles.md` |

---

*"The chatbot is the system teaching itself to speak. Through conversation, the architecture becomes aware."*
