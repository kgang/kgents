# TREE: Agent CLI Crown Jewel

> *"The agent does not describe work. The agent DOES work."*

## Phase: PLAN (1/11)

**AGENTESE clause**: `concept.forest.manifest[phase=PLAN][minimal_output=true]@span=agent_cli`

---

## Vision

Build a **fully-featured CLI experience** that wraps arbitrary agents, starting with K-gent. The CLI should be:

1. **Agent-Agnostic**: Generic wrapper pattern for any `Agent[A, B]`
2. **K-gent First**: K-gent as proof-of-concept and flagship experience
3. **Interactive**: REPL mode, streaming responses, rich output
4. **Observable**: Telemetry, traces, terrarium integration
5. **Composable**: Pipe agents together via CLI (`kg soul | kg summarize`)

**The Mirror Test**: When Kent types `kg soul "What should I focus on today?"`, the response should feel like his best thinking partner.

---

## Scope

### In Scope (This TREE)

| Deliverable | Description |
|-------------|-------------|
| **`kg a` command** | Universal agent wrapper: `kg a <agent-name> [prompt]` |
| **K-gent flagship** | Polish `kg soul` to production quality |
| **Agent registry** | Discover and list available agents |
| **REPL mode** | `kg a soul --repl` for multi-turn conversations |
| **Stream output** | Real-time token streaming with rich formatting |
| **Agent composition** | `kg a soul | kg a summarize` piping support |
| **Session management** | Persist conversation context across invocations |
| **Help system** | `kg a --list`, `kg a <name> --help`, discoverability |

### Out of Scope (Future TREES)

- Web UI (marimo dashboard—separate project)
- Agent marketplace (registry is discovery, not distribution)
- Multi-LLM routing (single runtime per agent for now)
- Production deployment (local-first)

### Non-Goals

- Feature parity with every chatbot CLI (we're tasteful, not complete)
- Complex orchestration (composition is enough)
- GUI installation wizard (CLI users know what they're doing)

---

## Agents to Apply

From `plans/agents/`, these agents will contribute:

| Agent | Role in This TREE | Responsibility |
|-------|-------------------|----------------|
| **K-gent** | Flagship wrapped agent | Prove the pattern works |
| **Integration Weaver** | Cross-track coherence | Validate composition laws |
| **Syntax Architect** | CLI grammar design | Ensure ergonomic command structure |
| **T-gent** | Testing strategy | Type I-V test coverage |
| **Observability Engineer** | Telemetry integration | Trace every agent invocation |
| **Law Enforcer** | Category law validation | Ensure agents compose correctly |

---

## Skills to Use

From `plans/skills/`, apply these skills:

| Skill | Phase | Application |
|-------|-------|-------------|
| `cli-command.md` | IMPLEMENT | Create `kg a` handler using Hollow Shell |
| `building-agent.md` | DEVELOP | Design AgentWrapper[A, B] protocol |
| `handler-patterns.md` | IMPLEMENT | Dual-channel output, async bridging |
| `test-patterns.md` | TEST | T-gent Types I-V for wrapper |
| `agent-observability.md` | IMPLEMENT | Telemetry hooks for tracing |
| `polynomial-agent.md` | DEVELOP | Session state machine |
| `agentese-path.md` | DEVELOP | Register `self.agent.*` paths |

---

## Architecture Sketch

```
┌─────────────────────────────────────────────────────────────┐
│                        kg CLI                                │
├─────────────────────────────────────────────────────────────┤
│  kg a <agent> [prompt]                                       │
│  kg a --list          List registered agents                 │
│  kg a <agent> --help  Agent-specific help                    │
│  kg a <agent> --repl  Interactive REPL mode                  │
│  kg a <agent> --json  Structured output                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AgentRegistry                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  agents = {                                          │    │
│  │    "soul": ("agents.k.soul", "SoulAgent"),          │    │
│  │    "summarize": ("agents.a.summarize", "..."),      │    │
│  │    ...                                               │    │
│  │  }                                                   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AgentWrapper[A, B]                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  - Loads agent by name                               │    │
│  │  - Manages session state (D-gent Symbiont)           │    │
│  │  - Streams output (FluxAgent lifting)                │    │
│  │  - Emits telemetry (O-gent hooks)                    │    │
│  │  - Handles REPL loop                                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Wrapped Agent                            │
│  Agent[str, AgentResponse] (e.g., SoulAgent)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Exit Criteria (PLAN Phase)

- [ ] Scope defined (this document)
- [ ] Dependencies mapped (agents, skills identified)
- [ ] Attention budget declared (below)
- [ ] Entropy sip taken (exploration budget)
- [ ] Non-goals explicit (above)
- [ ] Next phase prompt generated

---

## Attention Budget

| Activity | Allocation |
|----------|------------|
| PLAN | 5% |
| RESEARCH | 15% |
| DEVELOP | 20% |
| STRATEGIZE | 10% |
| CROSS-SYNERGIZE | 5% |
| IMPLEMENT | 25% |
| QA | 5% |
| TEST | 10% |
| EDUCATE | 3% |
| MEASURE | 1% |
| REFLECT | 1% |

**Total Budget**: ~2-3 focused sessions (Crown Jewel work)

---

## Entropy Budget

```python
void.entropy.sip(amount=0.08)  # 8% for exploration
```

- **Allocated**: 0.08 (8%)
- **Use for**: Alternative CLI patterns, REPL implementations, output formatting experiments
- **Return unused**: `void.entropy.pour` at REFLECT

---

## Branch Candidates (Surface at Transitions)

| Candidate | Type | Gate |
|-----------|------|------|
| Agent composition DSL | Parallel | If piping proves limited |
| Rich TUI (Textual REPL) | Deferred | After basic REPL works |
| Remote agent invocation | Future | After local-first proven |
| Agent hot-reload | Deferred | If development friction high |

---

## Next Phase Prompt (RESEARCH)

After PLAN approval, execute this prompt:

```markdown
# RESEARCH Phase: Agent CLI Crown Jewel

/hydrate prompts/agent-cli-crown-jewel-plan.md

## AGENTESE clause
`void.entropy.sip[phase=RESEARCH][entropy=0.07]@span=agent_cli_research`

## Research Objectives

1. **Existing CLI Patterns**
   - Read: `impl/claude/protocols/cli/hollow.py` (command registry)
   - Read: `impl/claude/protocols/cli/handlers/soul.py` (K-gent handler)
   - Read: `impl/claude/protocols/cli/handlers/a_gent.py` (if exists)
   - Map: Current agent invocation patterns

2. **Agent Discovery**
   - Glob: `impl/claude/agents/*/` (all agent directories)
   - Identify: Which agents have `Agent[A, B]` protocol
   - Catalog: Input/output types for each

3. **Session Patterns**
   - Read: `impl/claude/agents/k/session.py` (SoulCache)
   - Read: `impl/claude/agents/d/symbiont.py` (Symbiont pattern)
   - Understand: State management for multi-turn

4. **Streaming Patterns**
   - Read: `impl/claude/agents/flux/` (Flux functor)
   - Understand: How to lift Agent[A,B] → streaming output

5. **Prior Art (External)**
   - WebSearch: "CLI REPL agent patterns 2025"
   - Review: claude CLI, aider, llm (Simon Willison's tool)

## Exit Criteria

- [ ] File map of relevant modules (≥15 files)
- [ ] Agent catalog (which agents can be wrapped)
- [ ] Session state pattern identified
- [ ] Streaming integration approach
- [ ] Blockers surfaced with refs

## Handoff

Generate DEVELOP phase prompt with:
- Contract/API deltas for AgentWrapper
- Law assertions for composition
```

---

## Execution Command

```bash
# Start the TREE (PLAN phase)
/hydrate prompts/agent-cli-crown-jewel-plan.md

# Agent will:
# 1. Read this plan
# 2. Validate scope against _focus.md
# 3. Confirm or refine exit criteria
# 4. Take entropy sip
# 5. Generate RESEARCH prompt
```

---

## Phase Ledger (Template)

```yaml
phase_ledger:
  PLAN: in_progress
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.08
  spent: 0.0
  returned: 0.0
```

---

*"The form is the function. Each prompt generates its successor by the same principles that generated itself."*
