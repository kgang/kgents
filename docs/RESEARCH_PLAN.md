# Deep Research Plan: Rebuilding Zenportal with kgents

## Project Overview

**Goal:** Use the kgents reference implementation to imagine how an app could be built, then implement and assess it by recreating Zenportal.

**Hypothesis:** The kgents agent framework—with its composable, principled, heterarchical architecture—can serve as the foundation for building real applications. Zenportal is the test case.

---

## Phase 1: Understanding the Mapping

### 1.1 Zenportal Core Abstractions → kgents Primitives

| Zenportal Component | kgents Equivalent | Notes |
|---------------------|-------------------|-------|
| **SessionManager** | Compose + Fix | Orchestrates lifecycle; iterates until stable |
| **ConfigManager (3-tier)** | Ground + K-gent | Config cascade = persona grounding |
| **Session discovery** | Ground (world state) | Empirical facts about running sessions |
| **Service layer** | Agent genera (A, B, C) | Stateless, composable transforms |
| **UI Widgets** | Output schemas | Agents produce data; UI renders |
| **Modal system** | Input schemas | Structured prompts with validation |
| **Polling-based detection** | Fix (iteration) | Iterate until state stabilizes |
| **Command building** | Compose pipelines | Transform config → CLI command |
| **Grab mode (reorder)** | Contradict + Sublate | Surface tension, resolve order |
| **Zen AI integration** | K-gent + A-gent | Personalized creativity support |

### 1.2 Key Architectural Insights

1. **Services are Agents**: Zenportal's service layer (SessionManager, TmuxService, etc.) maps directly to agents with typed inputs/outputs
2. **Config is Ground**: The 3-tier config system (config > portal > session) mirrors Ground's persona/world structure
3. **Polling is Fix**: Session state detection via polling is a fixed-point search
4. **UI is Output**: Widgets render agent outputs; they don't contain logic
5. **Events are Composition**: The `SessionCreated`, `SessionStateChanged` events represent composed agent outputs flowing through the system

---

## Phase 2: Agent Architecture for Zenportal

### 2.1 Bootstrap Mapping

The irreducible kernel applies directly:

| Bootstrap Agent | Zenportal Role |
|-----------------|----------------|
| **Id** | Pass-through transforms (session → session) |
| **Compose** | Pipeline construction (config → command → session) |
| **Judge** | Validation (is this a valid session config?) |
| **Ground** | User preferences, system state, tmux facts |
| **Contradict** | Detect conflicts (same name, port clash, worktree conflict) |
| **Sublate** | Resolve conflicts (suggest alternative names, merge configs) |
| **Fix** | Iterate until session stable (polling → completion detection) |

### 2.2 Genus Mapping

| kgents Genus | Zenportal Function |
|--------------|-------------------|
| **A-gents** | Abstract session types (the "skeleton" of CLAUDE, CODEX, etc.) |
| **B-gents** | Discovery engine (find sessions, analyze patterns) |
| **C-gents** | Composition infrastructure (pipeline, config cascade) |
| **H-gents** | System introspection (why did this session fail?) |
| **K-gent** | User preferences, Zen AI personalization |

### 2.3 Proposed Agent Inventory

```
zen-agents/
├── bootstrap/                    # Re-use kgents bootstrap
│   └── (Id, Compose, Judge, Ground, Contradict, Sublate, Fix)
│
├── agents/
│   ├── session/                  # Session lifecycle agents
│   │   ├── create.py            # SessionInput → Session
│   │   ├── revive.py            # DeadSession → RunningSession
│   │   ├── pause.py             # Session → PausedSession
│   │   ├── kill.py              # Session → Killed
│   │   └── detect_state.py      # Session → SessionState (Fix-based)
│   │
│   ├── config/                   # Configuration agents
│   │   ├── resolve.py           # (config, portal, session) → ResolvedConfig
│   │   ├── validate.py          # Config → Verdict
│   │   └── merge.py             # (Config, Config) → Config
│   │
│   ├── tmux/                     # tmux interaction agents
│   │   ├── spawn.py             # Command → TmuxSession
│   │   ├── capture.py           # Session → OutputLines
│   │   ├── send_keys.py         # (Session, Keys) → Sent
│   │   └── list.py              # Void → [TmuxSession]
│   │
│   ├── worktree/                 # Git worktree agents
│   │   ├── create.py            # (Repo, Branch) → Worktree
│   │   ├── cleanup.py           # Worktree → Removed
│   │   └── list.py              # Repo → [Worktree]
│   │
│   ├── discovery/                # Session discovery agents
│   │   ├── find_claude.py       # Void → [ClaudeSession]
│   │   ├── find_tmux.py         # Void → [TmuxSession]
│   │   └── reconcile.py         # (Known, Found) → Reconciled
│   │
│   ├── command/                  # Command building agents
│   │   ├── claude.py            # Config → ClaudeCommand
│   │   ├── codex.py             # Config → CodexCommand
│   │   ├── gemini.py            # Config → GeminiCommand
│   │   ├── shell.py             # Config → ShellCommand
│   │   └── openrouter.py        # Config → OpenRouterCommand
│   │
│   ├── zen/                      # Zen AI agents
│   │   ├── prompt.py            # (Query, Context) → Response
│   │   ├── context.py           # Session → ContextSummary
│   │   └── mirror.py            # Thought → Reflection (K-gent)
│   │
│   └── proxy/                    # OpenRouter proxy agents
│       ├── validate.py          # ProxyConfig → Verdict
│       ├── health.py            # Proxy → HealthStatus
│       └── billing.py           # Usage → Cost
│
└── pipelines/                    # Composed agent pipelines
    ├── new_session.py           # Full session creation pipeline
    ├── session_tick.py          # Per-tick state update pipeline
    └── config_cascade.py        # 3-tier resolution pipeline
```

---

## Phase 3: Implementation Strategy

### 3.1 Phased Build

**Phase 3.1: Core Bootstrap Integration**
- Import kgents bootstrap agents directly
- Create ZenGround (extends Ground with Zenportal-specific state)
- Create ZenJudge (extends Judge with session validation principles)

**Phase 3.2: Session Agents**
- Implement session lifecycle agents (create, revive, pause, kill)
- Implement Fix-based state detection (polling as fixed-point)
- Test composition: `Compose(validate, create, spawn, detect)`

**Phase 3.3: Configuration Agents**
- Implement 3-tier cascade as composition
- Use Contradict to detect config conflicts
- Use Sublate to propose resolutions

**Phase 3.4: tmux Agents**
- Wrap TmuxService methods as agents
- Maintain async signatures
- Compose into pipelines

**Phase 3.5: Discovery Agents**
- Implement B-gent style discovery (observations → hypotheses)
- Reconciliation as dialectic (known vs. found → merged truth)

**Phase 3.6: Command Building Agents**
- One agent per session type
- All share composition interface
- Validate with Judge before execution

**Phase 3.7: Zen AI Integration**
- K-gent for personalization layer
- A-gent creativity coach for exploration
- H-hegel for surfacing decision tensions

**Phase 3.8: UI Layer**
- Textual widgets render agent outputs
- Widgets dispatch to agents, not services
- Event system remains, but carries agent outputs

### 3.2 Migration Strategy

Two approaches possible:

#### Option A: Greenfield (Recommended for Research)
Build from scratch using agents. Compare architecture, code volume, complexity.

**Pros:**
- Clean application of kgents principles
- No legacy constraints
- Clear comparison point

**Cons:**
- More work
- May miss edge cases original handles

#### Option B: Incremental Refactor
Replace Zenportal services one-by-one with agents.

**Pros:**
- Working system throughout
- Discovers integration friction

**Cons:**
- Hybrid state complicates analysis
- May not fully express agent architecture

**Recommendation:** Option A (Greenfield) for research validity. Build `zen-agents` as a separate implementation, then compare.

---

## Phase 4: Assessment Criteria

### 4.1 Quantitative Metrics

| Metric | Zenportal Original | Zen-Agents Target |
|--------|-------------------|-------------------|
| Lines of code | ~5,730 (services) | Measure |
| Number of files | ~40+ | Measure |
| Test coverage | >80% | Maintain |
| Cyclomatic complexity | Measure | Compare |
| Agent count | N/A | Count |
| Composition depth | N/A | Measure (max pipeline length) |

### 4.2 Qualitative Assessment

**Composability:**
- Can agents be reused in new contexts?
- Do pipelines feel natural?
- Is composition associative in practice?

**Tasteful:**
- Does each agent justify its existence?
- Is there redundancy?
- Is the system minimal?

**Curated:**
- Quality over quantity?
- Does every agent earn its place?

**Ethical:**
- Does the system preserve user agency?
- Is state transparent?

**Joy-Inducing:**
- Is working with the agent system pleasant?
- Does it have personality?

**Heterarchical:**
- Can agents switch between autonomous and functional modes?
- Is there fluid leadership?

### 4.3 Specific Test Cases

1. **Create a session**: Exercise full composition pipeline
2. **Detect session completion**: Test Fix iteration
3. **Resolve config conflict**: Test Contradict + Sublate
4. **Discover orphaned sessions**: Test discovery + reconciliation
5. **Zen AI query**: Test K-gent + A-gent composition
6. **Handle tmux failure**: Test error propagation through composition
7. **Reorder sessions**: Test Contradict (current order vs. desired)

---

## Phase 5: Research Questions

### 5.1 Primary Questions

1. **Does agent composition reduce complexity?**
   - Hypothesis: Explicit composition surfaces hidden dependencies
   - Measure: Coupling metrics, comprehensibility

2. **Does the bootstrap kernel generalize?**
   - Hypothesis: The 7 bootstrap agents suffice for any domain
   - Test: Are there operations that can't be expressed?

3. **Does heterarchy work in practice?**
   - Hypothesis: Agents can switch modes fluidly
   - Test: Same agent used both ways in real workflows

4. **Does Judge improve quality?**
   - Hypothesis: Explicit principles prevent feature creep
   - Test: Compare rejected designs to accepted ones

5. **Does K-gent personalization add value?**
   - Hypothesis: Ground-based personalization improves UX
   - Test: A/B compare with and without K-gent layer

### 5.2 Secondary Questions

- How deep should composition go? (Pipeline length limits)
- When should agents be split vs. combined?
- How to handle stateful operations in stateless agents?
- What's the overhead of agent infrastructure vs. direct code?

---

## Phase 6: Timeline Structure (No Dates)

### Milestone 1: Foundation
- [ ] Set up zen-agents project structure
- [ ] Import kgents bootstrap
- [ ] Create ZenGround with session-specific state
- [ ] Create ZenJudge with session validation principles

### Milestone 2: Core Agents
- [ ] Implement session lifecycle agents
- [ ] Implement config resolution pipeline
- [ ] Implement tmux wrapper agents
- [ ] Test Fix-based state detection

### Milestone 3: Discovery & Commands
- [ ] Implement discovery agents
- [ ] Implement command building agents
- [ ] Create reconciliation dialectic
- [ ] Test full create-to-completion flow

### Milestone 4: Zen AI
- [ ] Integrate K-gent for personalization
- [ ] Integrate A-gent for creativity
- [ ] Implement context summarization
- [ ] Test Zen prompt workflow

### Milestone 5: UI Layer
- [ ] Port Textual widgets to render agent outputs
- [ ] Implement event dispatch to agents
- [ ] Create main screen composition
- [ ] Test full UI workflow

### Milestone 6: Assessment
- [ ] Gather quantitative metrics
- [ ] Conduct qualitative assessment
- [ ] Document findings
- [ ] Write comparison report

---

## Appendix A: Zenportal Feature Inventory

Features to replicate (priority order):

1. **Must Have:**
   - Session lifecycle (create, pause, kill, revive)
   - tmux backend
   - Output capture and display
   - Session state detection
   - Basic config
   - Keyboard navigation

2. **Should Have:**
   - Git worktree isolation
   - 3-tier config cascade
   - Session discovery
   - Session reordering
   - Insert mode (send keys)

3. **Nice to Have:**
   - Zen AI integration
   - Proxy monitoring
   - Billing tracking
   - Token parsing
   - Sparkline visualization

4. **Defer:**
   - OpenRouter model selection
   - Full command palette
   - All session types (start with Claude + Shell)

---

## Appendix B: Key Files to Study

### Zenportal (~/git/zenportal)
- `services/session_manager.py` - Core orchestration (711 lines)
- `services/config.py` - 3-tier config (547 lines)
- `services/tmux.py` - tmux wrapper (279 lines)
- `services/discovery.py` - Session discovery (418 lines)
- `models/session.py` - Data structures
- `screens/main.py` - Main UI composition

### kgents (~/git/kgents)
- `impl/claude-openrouter/bootstrap/` - All 7 bootstrap agents
- `impl/claude-openrouter/agents/` - Genus implementations
- `spec/principles.md` - The 6 pillars
- `spec/bootstrap.md` - Irreducible kernel specification

---

## Appendix C: Open Questions for Kent

1. **Scope:** Full Zenportal feature parity, or subset?
2. **Integration:** Keep impl in kgents repo, or separate zen-agents repo?
3. **UI framework:** Still Textual, or explore alternatives?
4. **LLM backend:** Use mock implementations (like current kgents) or real LLM?
5. **Persistence:** File-based state or database?
6. **Testing:** Match Zenportal's pytest setup, or try different approach?

---

## Next Steps

1. Review this plan with Kent
2. Clarify scope and open questions
3. Begin Milestone 1 (Foundation)
4. Document findings continuously

---

*This research plan is itself a composition: Zenportal (thesis) + kgents (antithesis) → Zen-Agents (synthesis).*
