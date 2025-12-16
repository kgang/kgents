---
path: plans/core-apps/the-gardener
status: complete
progress: 100
last_touched: 2025-12-16
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/core-apps-synthesis
  - plans/agentese-universal-protocol
session_notes: |
  INAUGURATED as 7th Crown Jewel per Kent's directive.
  Theme: "The interface where I speak with the system itself to evolve and grow"
  Core insight: N-Phase compiler + AGENTESE ontology = autopoietic development substrate

  2025-12-16: PRODUCTION-READY. All 8 phases complete.
  - Spec: spec/protocols/gardener-logos.md
  - Foundation: protocols/gardener_logos/ (163+ tests)
  - Tending Calculus: 6 verbs (observe, prune, graft, water, rotate, wait)
  - Seasons: DORMANT, SPROUTING, BLOOMING, HARVEST, COMPOSTING
  - Auto-Inducer: Phase transition signifiers
  - Persistence: GardenStore with CRUD + history
  - API: REST endpoints for gardens and plots
  - Web UI: Garden.tsx with Cymatics visualization
  - CLI: Full garden command suite
spec: spec/protocols/gardener-logos.md
implementation_plan: plans/gardener-logos-enactment.md
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.05
  returned: 0.0
---

# The Gardener: Autopoietic Development Interface

> *"The form that generates forms. The garden that tends itself."*
>
> *"An autopoietic system produces and reproduces its own elements as well as its own structures."* — Maturana & Varela

**Crown Jewel #7** | **Meta-Framework Stress**: N-Phase (Autopoiesis)

---

## I. Vision

The Gardener is the **interface through which Kent speaks with kgents to evolve kgents itself**. It is not merely a CLI—it is an **autopoietic development substrate** where:

1. **All development activity flows through AGENTESE paths**
2. **The N-Phase compiler orchestrates multi-session, multi-agent work**
3. **The system proposes its own improvements** (sympoiesis: "making-with")
4. **Kent's Claude Code sessions become first-class forest citizens**

This is **the end of using external tools**. Every request—from "what's the weather" to "implement the Coalition Forge API"—routes through kgents infrastructure, making every interaction a learning opportunity.

---

## II. Philosophical Foundation

### 2.1 Autopoiesis in Software

Maturana and Varela defined autopoiesis as a system that:
- **Produces its own components** (self-creation)
- **Maintains its own organization** (self-preservation)
- **Defines its own boundaries** (self-delimitation)

The Gardener instantiates this for software development:

| Biological Autopoiesis | The Gardener Analog |
|------------------------|---------------------|
| Cell produces proteins | N-Phase generates prompts/plans |
| Membrane defines boundary | AGENTESE contexts define scope |
| Metabolism maintains structure | Forest Protocol maintains coherence |
| Reproduction via division | Fork/branch creates new project lines |

### 2.2 From Autopoiesis to Sympoiesis

Donna Haraway critiques pure autopoiesis: *"Nothing makes itself."* She proposes **sympoiesis**: "making-with."

The Gardener embraces this:
- Kent proposes intent
- System proposes structure (via LLM + N-Phase templates)
- Kent refines
- System implements
- Both evolve together

**The Gardener is not Kent's tool. It is Kent's collaborator.**

### 2.3 The Verb-First Mandate

Per AGENTESE spec §1:

> *"The noun is a lie. There is only the rate of change."*

The Gardener eliminates the conceptual gap between "thinking about development" and "doing development":

```
OLD: "I should update the forest" → open editor → find file → edit
NEW: kg forest.evolve → system proposes changes → Kent approves
```

---

## III. AGENTESE-First Architecture

### 3.1 The CLI as AGENTESE Interpreter

**Current state**: CLI commands map loosely to AGENTESE paths.
**Target state**: CLI IS the AGENTESE REPL.

```bash
# Current (imperative commands)
kg nphase compile project.yaml
kg forest status
kg soul dialogue

# Target (AGENTESE paths directly)
kg concept.nphase.compile --target project.yaml
kg self.forest.manifest
kg self.soul.dialogue

# Or even shorter (slash shortcuts preserved)
kg /nphase → concept.nphase.manifest
kg /forest → self.forest.manifest
kg /soul → self.soul.dialogue
```

### 3.2 Context-Command Mapping

Every CLI command maps to an AGENTESE path:

| AGENTESE Path | CLI Command | Meaning |
|---------------|-------------|---------|
| `self.forest.manifest` | `kg forest` | Show forest health |
| `self.forest.evolve` | `kg forest evolve` | Propose forest changes |
| `self.soul.dialogue` | `kg soul` | Dialogue with K-gent |
| `concept.nphase.compile` | `kg nphase compile` | Compile N-Phase prompt |
| `concept.plan.create` | `kg plan new` | Create new plan |
| `world.code.manifest` | `kg code` | Show codebase state |
| `world.town.manifest` | `kg town` | Show Town status |
| `void.entropy.sip` | `kg surprise-me` | Draw serendipitous tangent |
| `time.trace.witness` | `kg trace` | Show execution history |

### 3.3 The Message Bus as AGENTESE Substrate

All internal communication flows through AGENTESE paths:

```python
# Old: Direct function calls
result = compiler.compile_from_yaml_file(path)

# New: AGENTESE message bus
result = await logos.invoke(
    "concept.nphase.compile",
    developer_umwelt,
    target=path
)
```

**Benefits**:
- Observability: Every action has a trace
- Permissioning: Affordances respected
- Composability: Actions compose via `>>`
- Auditability: All actions logged to forest

---

## IV. N-Phase as the Autopoietic Engine

### 4.1 Session as Living Entity

An N-Phase session is not a passive data structure—it is a **polynomial agent**:

```python
class GardenerSession(PolyAgent[SessionState, Intent, Artifact]):
    """
    A development session that maintains its own state.

    Positions: SENSE | ACT | REFLECT
    Directions: Intent (what Kent wants)
    Emissions: Artifact (code, docs, plans)
    """

    async def sense(self, intent: Intent) -> SessionState:
        """Gather context via AGENTESE paths."""
        forest = await logos.invoke("self.forest.manifest", self.umwelt)
        codebase = await logos.invoke("world.code.manifest", self.umwelt)
        memory = await logos.invoke("self.memory.manifest", self.umwelt)
        return SessionState(forest, codebase, memory, intent)

    async def act(self, state: SessionState) -> Artifact:
        """Execute phase-appropriate action."""
        phase = detect_phase(state)
        template = await logos.invoke(
            f"concept.nphase.template.{phase}",
            self.umwelt
        )
        return await self.execute_template(template, state)

    async def reflect(self, artifact: Artifact) -> SessionState:
        """Update forest, memory, meta.md."""
        await logos.invoke("self.forest.update", self.umwelt, artifact=artifact)
        await logos.invoke("self.memory.engram", self.umwelt, artifact=artifact)
        await logos.invoke("self.meta.append", self.umwelt, learning=artifact.learnings)
        return self.state.evolve(artifact)
```

### 4.2 The Session Store as Holographic Memory

Sessions persist and interconnect:

```python
# Create session for feature
session = await logos.invoke(
    "concept.gardener.session.create",
    umwelt,
    name="Coalition Forge API",
    plan="plans/core-apps/coalition-forge.md"
)

# Resume across Claude Code sessions
session = await logos.invoke(
    "concept.gardener.session.resume",
    umwelt,
    session_id="coalition-forge-api-2025-12-15"
)

# Query across all sessions
history = await logos.invoke(
    "time.sessions.witness",
    umwelt,
    filter={"plan": "coalition-forge"}
)
```

### 4.3 N-Phase → AGENTESE Path Mapping

Every N-Phase phase has an AGENTESE path:

| Phase | AGENTESE Path | System Action |
|-------|---------------|---------------|
| PLAN | `concept.nphase.plan` | Generate plan structure |
| RESEARCH | `concept.nphase.research` | Gather codebase context |
| DEVELOP | `concept.nphase.develop` | Draft implementation |
| STRATEGIZE | `concept.nphase.strategize` | Sequence waves |
| CROSS-SYNERGIZE | `concept.nphase.synergize` | Find cross-tree opportunities |
| IMPLEMENT | `concept.nphase.implement` | Write code |
| QA | `concept.nphase.qa` | Review + refactor |
| TEST | `concept.nphase.test` | Write + run tests |
| EDUCATE | `concept.nphase.educate` | Update docs + skills |
| MEASURE | `concept.nphase.measure` | Emit metrics |
| REFLECT | `concept.nphase.reflect` | Update meta.md |

---

## V. The Gardener Experience

### 5.1 User Journey: "Implement Coalition Forge API"

```
DAY 1: Kent's Intent
──────────────────────────────────────────────────────────────
Kent: "kg I want to implement the Coalition Forge API"

Gardener: [SENSE phase]
  ├── Reading self.forest.manifest → Coalition Forge at 0%
  ├── Reading world.code.manifest → Found agents/town/workshop.py
  ├── Reading self.memory.manifest → Prior session: "coalition architecture"
  └── Proposing session: "Coalition Forge API Implementation"

Gardener: [PLAN phase]
  Here's my proposed plan:

  1. Define ForgeTask interface (agents/forge/task.py)
  2. Implement CoalitionFormation algorithm (agents/forge/formation.py)
  3. Create 5 task templates (agents/forge/templates/)
  4. Wire REST endpoints (protocols/api/forge.py)
  5. Add reactive widgets (agents/i/reactive/forge/)

  Shall I proceed? [y/n/refine]

Kent: "y"

Gardener: [Advancing to RESEARCH]
  Session saved: coalition-forge-api-2025-12-15
  Next: `kg /continue` to resume

──────────────────────────────────────────────────────────────
DAY 2: Resume
──────────────────────────────────────────────────────────────
Kent: "kg /continue"

Gardener: [Resuming session: coalition-forge-api-2025-12-15]
  Phase: RESEARCH

  I've analyzed the codebase:
  ├── TownOperad at agents/town/operad.py (can reuse)
  ├── WorkshopFlux at agents/town/workshop.py (can extend)
  ├── Similar pattern in agents/atelier/ (learn from)

  File map updated. Ready for DEVELOP?

Kent: "proceed"

Gardener: [DEVELOP phase]
  Drafting ForgeTask interface...
  [Shows code diff]

  Shall I implement? [y/n/refine]

[... continues through phases ...]
```

### 5.2 Proactive Suggestions

The Gardener doesn't wait—it proposes:

```
Kent: "kg"

Gardener: Good morning. Here's what I notice:

  1. Coalition Forge session paused at IMPLEMENT
     → `kg /continue` to resume

  2. 3 tests failing in agents/atelier/
     → `kg /flinch` for analysis

  3. _forest.md is 2 days stale
     → `kg self.forest.evolve` to refresh

  4. void.entropy suggests: "Consider adding consent debt visualization to Gestalt"
     → `kg /explore` for details
```

### 5.3 Weather, Email, and Beyond

The Gardener handles ALL requests by routing to appropriate agents:

```
Kent: "kg what's the weather in SF"

Gardener: [Routing to world.weather.manifest]
  Currently 58°F, partly cloudy.

  (Note: This used world.weather.manifest with OpenWeatherMap MCP)

Kent: "kg summarize my unread emails"

Gardener: [Routing to world.email.manifest]
  3 unread:
  1. [GitHub] PR review requested on kgents/impl
  2. [Stripe] Monthly invoice
  3. [Newsletter] AI news digest

  (Note: This used world.email.manifest with Gmail MCP)
```

---

## VI. Technical Architecture

### 6.1 Core Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           THE GARDENER STACK                                 │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      INTERFACE LAYER                                   │ │
│  │   kg CLI  ←→  AGENTESE REPL  ←→  Web UI  ←→  Claude Code Hook         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    LOGOS (AGENTESE Resolver)                           │ │
│  │   Parse path → Check affordances → Route to handler → Return result    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                    SESSION MANAGER (N-Phase)                           │ │
│  │   Create → Advance → Checkpoint → Resume → Complete                    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                         │
│  ┌────────────┬───────────────────┴───────────────────┬───────────────────┐ │
│  │            │                                       │                   │ │
│  ▼            ▼                                       ▼                   ▼ │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │
│  │ Forest │ │ Memory │ │ Code   │ │ Town   │ │ Soul   │ │ Entropy│        │
│  │ self.  │ │ self.  │ │ world. │ │ world. │ │ self.  │ │ void.  │        │
│  │ forest │ │ memory │ │ code   │ │ town   │ │ soul   │ │ entropy│        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      PERSISTENCE LAYER                                 │ │
│  │   SessionStore  │  ForestFiles  │  M-gent  │  Traces  │  Metrics       │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 New AGENTESE Paths

| Path | Handler | Purpose |
|------|---------|---------|
| `concept.gardener.session.create` | `GardenerSession.create` | Start new session |
| `concept.gardener.session.resume` | `GardenerSession.resume` | Resume existing |
| `concept.gardener.session.advance` | `GardenerSession.advance` | Move to next phase |
| `concept.gardener.propose` | `GardenerProposer.propose` | Suggest next action |
| `concept.gardener.route` | `GardenerRouter.route` | Route natural language to path |
| `self.forest.evolve` | `ForestEvolver.evolve` | Propose forest changes |
| `self.meta.append` | `MetaAppender.append` | Add learning to meta.md |
| `world.code.implement` | `CodeImplementer.implement` | Write code to files |
| `world.external.*` | `MCPBridge.invoke` | Route to external MCP servers |

### 6.3 Claude Code Integration

The Gardener hooks into Claude Code sessions:

```python
# .claude/hooks/pre-prompt.py
async def pre_prompt_hook(context: HookContext) -> str:
    """Inject Gardener context before every prompt."""
    session = await logos.invoke(
        "concept.gardener.session.active",
        context.umwelt
    )

    if session:
        return f"""
[GARDENER SESSION: {session.name}]
Phase: {session.current_phase}
Plan: {session.plan_path}
Last action: {session.last_action}
"""
    return ""

# .claude/hooks/post-response.py
async def post_response_hook(context: HookContext, response: str) -> None:
    """Learn from Claude Code session."""
    await logos.invoke(
        "concept.gardener.learn",
        context.umwelt,
        response=response,
        intent=context.user_message
    )
```

---

## VII. Implementation Phases

### Phase 1: AGENTESE-First CLI Refactor

```
Deliverables:
├── Refactor hollow.py to route through Logos
├── Map all existing commands to AGENTESE paths
├── Add `kg <path>` syntax for direct AGENTESE invocation
├── Preserve slash shortcuts as aliases
└── Wire observability (traces for all invocations)

Exit Criteria:
├── [ ] All 50+ CLI commands route through Logos
├── [ ] Direct path syntax works: `kg self.forest.manifest`
├── [ ] Shortcuts preserved: `kg /forest` → `kg self.forest.manifest`
├── [ ] All invocations emit OTEL spans
```

### Phase 2: Session Manager

```
Deliverables:
├── GardenerSession polynomial agent
├── Persistent session storage (SQLite + JSON)
├── Session resume across Claude Code sessions
├── Phase detection from conversation context
└── Session linking to forest plans

Exit Criteria:
├── [ ] Sessions persist across CLI invocations
├── [ ] Resume works: `kg /continue`
├── [ ] Sessions link to plan files
├── [ ] Phase transitions update forest
```

### Phase 3: Proactive Proposer

```
Deliverables:
├── GardenerProposer agent
├── LLM-powered intent → path routing
├── Proactive suggestion on bare `kg` command
├── Entropy-driven serendipitous suggestions
└── Claude Code hook integration

Exit Criteria:
├── [ ] Bare `kg` shows actionable suggestions
├── [ ] Natural language routes to paths
├── [ ] void.sip injects creative tangents
├── [ ] Claude Code sessions auto-resume Gardener sessions
```

### Phase 4: Universal Routing

```
Deliverables:
├── MCP bridge for external services
├── world.weather.*, world.email.*, etc.
├── Fallback LLM for unknown paths
├── Usage-based path crystallization
└── Custom path definition syntax

Exit Criteria:
├── [ ] Weather/email/calendar work via MCP
├── [ ] Unknown paths fallback to LLM with context
├── [ ] High-use custom paths get permanent handlers
├── [ ] Kent's daily workflow runs 100% through Gardener
```

---

## VIII. Success Metrics

### 8.1 Adoption Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| % of Kent's development via Gardener | 100% | Full autopoiesis |
| Sessions created/week | 10+ | Active development |
| Session completion rate | >80% | Useful, not abandoned |
| Average phases/session | 6+ | Deep work, not shallow |

### 8.2 Quality Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| CLI → AGENTESE coverage | 100% | Full ontology alignment |
| Session resume success | >95% | Reliable persistence |
| Proactive suggestion acceptance | >50% | Useful suggestions |
| Forest sync latency | <1s | Feels instantaneous |

### 8.3 Joy Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| "Surprise me" invocations/week | 5+ | Entropy is valued |
| Session naming creativity | High variance | Personal expression |
| Gardener personality emergence | Measurable | K-gent infusion |

---

## IX. Relationship to Other Jewels

| Jewel | Gardener Relationship |
|-------|----------------------|
| **Atelier** | Gardener sessions can spawn Atelier creation streams |
| **Coalition Forge** | Gardener can delegate to agent coalitions |
| **Holographic Brain** | Gardener sessions become brain crystals |
| **Punchdrunk Park** | Gardener can INHABIT scenarios for testing |
| **Domain Simulation** | Gardener can run domain sims for validation |
| **Gestalt** | Gardener uses Gestalt for codebase visualization |

---

## X. Open Questions

1. **Session granularity**: One session per plan? Per feature? Per day?
2. **Multi-user**: Can Gardener sessions have multiple contributors?
3. **Conflict resolution**: What if forest changes conflict mid-session?
4. **LLM fallback**: How much latency is acceptable for routing?
5. **Privacy**: Which paths should never route externally?
6. **Consent**: How does Gardener respect agent consent in proposals?

---

## XI. References

### Research Sources

- [Autopoiesis - Wikipedia](https://en.wikipedia.org/wiki/Autopoiesis)
- [Understanding Autopoiesis - Mannaz](https://www.mannaz.com/en/articles/coaching-assessment/understanding-autopoiesis-life-systems-and-self-organization/)
- [Self-Evolving Software Systems - ACM](https://dl.acm.org/doi/10.1145/288408.288416)
- [Building Evolutionary Architectures - O'Reilly](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/ch01.html)
- [Command Line Interface Guidelines](https://clig.dev/)

### Internal References

- `spec/protocols/agentese.md` — AGENTESE specification
- `impl/claude/protocols/nphase/` — N-Phase implementation
- `impl/claude/protocols/cli/` — Current CLI implementation
- `docs/skills/plan-file.md` — Forest Protocol conventions

---

## UX Research: Reference Flows

### Proven Patterns from AI-Powered CLI Tools

#### 1. GitHub Copilot CLI (2025)
**Source**: [GitHub Copilot CLI 101](https://github.blog/ai-and-ml/github-copilot-cli-101-how-to-use-github-copilot-from-the-command-line/)

GitHub's Copilot CLI sets the standard for AI-powered terminal experiences:

| Copilot CLI Pattern | Gardener Adaptation |
|--------------------|---------------------|
| **Natural language → command** | `kg <natural language>` → AGENTESE path |
| **Interactive mode** (back-and-forth refinement) | `kg` (bare command) → conversational session |
| **Programmatic mode** (one-off prompts) | `kg -p "task description"` → immediate execution |
| **GitHub context awareness** | Forest + Memory awareness |

**Key Insight**: "Copilot CLI brings AI-powered coding assistance directly to your command line...through natural language conversations." The Gardener must feel like **talking to the system**, not commanding it.

#### 2. Warp Terminal AI Features
**Source**: [Warp AI Features](https://www.infralovers.com/blog/2024-05-19-unlocking-new-possibilities-with-ai-powered-terminal-integration/)

Warp's AI integration provides UX patterns for error recovery and context:

| Warp Pattern | Gardener Application |
|--------------|---------------------|
| **AI command suggestions** (on error) | `GardenerRecovery` — suggest fixes on failure |
| **History-aware completions** | `SessionContext` — suggestions from recent actions |
| **Visual command blocks** | `PhaseBlocks` — visually distinct N-Phase stages |
| **Collaboration features** | `SessionSharing` — share gardener sessions |

**Key Insight**: "AI can suggest commands from the history of the last commands." Gardener should learn from **your patterns**, not just generic patterns.

#### 3. Fig (now Amazon Q) Autocomplete
**Source**: [Fig Autocomplete Architecture](https://github.com/withfig/autocomplete)

Fig's declarative autocomplete provides patterns for intelligent suggestions:

| Fig Pattern | Gardener Application |
|-------------|---------------------|
| **Completion specs** (declarative schemas) | `PathSpecs` — AGENTESE paths as completion sources |
| **Context-aware suggestions** | `PhaseAwareSuggestions` — suggest based on N-Phase stage |
| **Real-time inline descriptions** | `AffordanceDescriptions` — show what each path does |
| **500+ CLI tool support** | `UniversalRouting` — anything flows through Gardener |

**Key Insight**: "Cognitive load of remembering sub-commands, flags, file paths is real." Gardener should **eliminate recall**—it should know what you probably want next.

---

## Precise User Flows

### Flow 1: Morning Start ("The Dawn Protocol")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Kent opens terminal, first command of the day                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. BARE COMMAND (0 seconds)                                                 │
│     ├── Kent types: kg                                                       │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🌱 GARDENER                            Good morning, Kent   │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  ACTIVE SESSION:                                            │     │
│     │   │  ├── Coalition Forge API — paused at IMPLEMENT (45%)        │     │
│     │   │  └── `kg /continue` to resume                               │     │
│     │   │                                                             │     │
│     │   │  FOREST STATUS:                                             │     │
│     │   │  ├── _forest.md last updated: 2 days ago ⚠️                │     │
│     │   │  └── `kg self.forest.evolve` to refresh                     │     │
│     │   │                                                             │     │
│     │   │  NOTICES:                                                   │     │
│     │   │  ├── 2 tests failing in agents/atelier/                     │     │
│     │   │  │   └── `kg /flinch` for analysis                          │     │
│     │   │  ├── PR #147 has new comments                               │     │
│     │   │  │   └── `kg world.github.pr.147.manifest`                  │     │
│     │   │  └── void.entropy suggests: "Try the Exquisite mode today"  │     │
│     │   │      └── `kg void.entropy.sip` for details                  │     │
│     │   │                                                             │     │
│     │   │  What would you like to do?                                 │     │
│     │   │  > _                                                        │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Gardener proactively surfaces relevant context                       │
│                                                                              │
│  2. NATURAL LANGUAGE INPUT                                                   │
│     ├── Kent types: "continue with the coalition API"                       │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🔄 Routing: "continue with the coalition API"               │     │
│     │   │     → concept.gardener.session.resume                       │     │
│     │   │     → Session: coalition-forge-api-2025-12-14               │     │
│     │   │                                                             │     │
│     │   │  Resuming session...                                        │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Gardener routes to appropriate AGENTESE path                         │
│                                                                              │
│  3. SESSION CONTEXT RESTORED                                                 │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  SESSION: Coalition Forge API                               │     │
│     │   │  Phase: IMPLEMENT (step 3 of 5)                             │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  CONTEXT RESTORED:                                          │     │
│     │   │  ├── You were working on: CoalitionFormation class         │     │
│     │   │  ├── Last file edited: agents/forge/formation.py:127       │     │
│     │   │  └── Last decision: "Use eigenvector similarity for match"  │     │
│     │   │                                                             │     │
│     │   │  NEXT STEP:                                                 │     │
│     │   │  Implement the `match_specialists` method                   │     │
│     │   │                                                             │     │
│     │   │  Want me to:                                                │     │
│     │   │  [1] Draft the implementation                               │     │
│     │   │  [2] Show the interface again                               │     │
│     │   │  [3] Something else?                                        │     │
│     │   │                                                             │     │
│     │   │  > _                                                        │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Full context from previous session available                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: New Task ("The Intent to Plan")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Kent wants to start something new                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. EXPRESS INTENT                                                           │
│     ├── Kent types: kg I want to add consent visualization to Gestalt       │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🔄 Routing: "add consent visualization to Gestalt"          │     │
│     │   │     → concept.gardener.session.create                       │     │
│     │   │     → Plan: plans/core-apps/gestalt-architecture-visualizer │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Gardener recognizes this needs a new session                         │
│                                                                              │
│  2. SENSE PHASE (automatic)                                                  │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  [SENSE] Gathering context...                               │     │
│     │   │                                                             │     │
│     │   │  ├── Reading self.forest.manifest                           │     │
│     │   │  │   └── Found: Gestalt at 5% progress                      │     │
│     │   │  ├── Reading world.code.manifest                            │     │
│     │   │  │   └── Found: agents/i/reactive/, protocols/agentese/     │     │
│     │   │  ├── Reading self.memory.manifest                           │     │
│     │   │  │   └── Found: "consent debt" crystal from last month      │     │
│     │   │  └── Reading concept.consent.manifest                       │     │
│     │   │      └── Found: ConsentLedger in agents/town/               │     │
│     │   │                                                             │     │
│     │   │  Context gathered in 2.3s                                   │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Gardener autonomously gathers relevant context                       │
│                                                                              │
│  3. PLAN PROPOSAL                                                            │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  [PLAN] Here's my proposed approach:                        │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  TASK: Add consent visualization to Gestalt                 │     │
│     │   │                                                             │     │
│     │   │  STEPS:                                                     │     │
│     │   │  1. Extend ArchitectureGraph with consent edge metadata     │     │
│     │   │  2. Add ConsentLayer to visualization engine                │     │
│     │   │  3. Create consent debt color gradient (green→red)          │     │
│     │   │  4. Wire to live AGENTESE traces for real-time updates     │     │
│     │   │  5. Add tooltip showing consent ledger history              │     │
│     │   │                                                             │     │
│     │   │  ESTIMATED: 3-4 N-Phase sessions                            │     │
│     │   │                                                             │     │
│     │   │  RELATED:                                                   │     │
│     │   │  • ConsentLedger at agents/town/consent.py (reuse)         │     │
│     │   │  • Reactive signals at agents/i/reactive/ (reuse)          │     │
│     │   │                                                             │     │
│     │   │  [Approve] [Refine] [Ask questions]                         │     │
│     │   │  > _                                                        │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Gardener proposes structured plan based on context                   │
│                                                                              │
│  4. APPROVAL AND SESSION START                                               │
│     ├── Kent types: approve                                                  │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  ✓ Session created: gestalt-consent-viz-2025-12-15          │     │
│     │   │  ✓ Plan linked to: plans/core-apps/gestalt-architecture-vis │     │
│     │   │  ✓ Forest updated: new branch added                         │     │
│     │   │                                                             │     │
│     │   │  Moving to RESEARCH phase...                                │     │
│     │   │                                                             │     │
│     │   │  I'm now analyzing the existing consent code.               │     │
│     │   │  This will take ~30 seconds.                                │     │
│     │   │                                                             │     │
│     │   │  [Continue] or `kg /pause` to save and exit                 │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Session persists even if Kent closes the terminal                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 3: External Routing ("The Universal Interface")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Kent uses Gardener for non-development tasks                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. WEATHER QUERY                                                            │
│     ├── Kent types: kg what's the weather in SF                             │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🔄 Routing: "what's the weather in SF"                      │     │
│     │   │     → world.weather.manifest                                │     │
│     │   │     → MCP: openweathermap                                   │     │
│     │   │                                                             │     │
│     │   │  Currently 58°F in San Francisco                            │     │
│     │   │  Partly cloudy, 65% humidity                                │     │
│     │   │  Wind: 12 mph from the west                                 │     │
│     │   │                                                             │     │
│     │   │  (via world.weather.manifest → OpenWeatherMap MCP)          │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── External services accessed via AGENTESE paths                        │
│                                                                              │
│  2. EMAIL SUMMARY                                                            │
│     ├── Kent types: kg summarize my unread emails                           │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🔄 Routing: "summarize my unread emails"                    │     │
│     │   │     → world.email.unread.manifest                           │     │
│     │   │     → MCP: gmail                                            │     │
│     │   │                                                             │     │
│     │   │  3 unread emails:                                           │     │
│     │   │                                                             │     │
│     │   │  1. [GitHub] PR #147 review requested                       │     │
│     │   │     From: maya@team.com                                     │     │
│     │   │     "Ready for review on the Coalition Forge PR"            │     │
│     │   │                                                             │     │
│     │   │  2. [Stripe] Monthly invoice                                │     │
│     │   │     Amount: $127.50                                         │     │
│     │   │     Status: Paid                                            │     │
│     │   │                                                             │     │
│     │   │  3. [AI Weekly] Newsletter digest                           │     │
│     │   │     Topics: Claude updates, GPT-5, Agent frameworks         │     │
│     │   │                                                             │     │
│     │   │  (via world.email.unread.manifest → Gmail MCP)              │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Everything routes through Gardener—no external tools needed          │
│                                                                              │
│  3. CALENDAR CHECK                                                           │
│     ├── Kent types: kg what meetings do I have today                        │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🔄 Routing: "what meetings do I have today"                 │     │
│     │   │     → time.calendar.today.manifest                          │     │
│     │   │     → MCP: google-calendar                                  │     │
│     │   │                                                             │     │
│     │   │  Today's schedule:                                          │     │
│     │   │                                                             │     │
│     │   │  10:00 AM  Team standup (30 min)                           │     │
│     │   │  2:00 PM   Design review: Atelier UX (1 hr)                │     │
│     │   │  4:30 PM   1:1 with Maya (30 min)                          │     │
│     │   │                                                             │     │
│     │   │  3 hrs 30 min of focus time available before standup       │     │
│     │   │                                                             │     │
│     │   │  (via time.calendar.today.manifest → Google Calendar MCP)   │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Time context integrated with AGENTESE ontology                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 4: Serendipity ("The Void Sip")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Kent invokes the accursed share for creative inspiration            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. INVOKE ENTROPY                                                           │
│     ├── Kent types: kg void.entropy.sip                                     │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🌀 VOID.ENTROPY.SIP                                        │     │
│     │   │                                                             │     │
│     │   │  Drawing from the accursed share...                         │     │
│     │   │                                                             │     │
│     │   │  ┌───────────────────────────────────────────────────────┐ │     │
│     │   │  │                                                       │ │     │
│     │   │  │  "What if coalition formation used pheromone trails   │ │     │
│     │   │  │  like ant colonies? Agents leave traces that attract │ │     │
│     │   │  │  others with compatible eigenvectors..."              │ │     │
│     │   │  │                                                       │ │     │
│     │   │  │  This connects:                                       │ │     │
│     │   │  │  • Your recent work on Coalition Forge                │ │     │
│     │   │  │  • The stigmergy patterns in M-gent                   │ │     │
│     │   │  │  • A paper you saved 2 months ago about swarm AI      │ │     │
│     │   │  │                                                       │ │     │
│     │   │  └───────────────────────────────────────────────────────┘ │     │
│     │   │                                                             │     │
│     │   │  [Explore this] [Another sip] [Tithe gratitude]            │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Void draws from memory, forest, and creative chaos                   │
│                                                                              │
│  2. EXPLORE THE TANGENT                                                      │
│     ├── Kent types: explore this                                             │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🌀 EXPLORING: Stigmergic Coalition Formation               │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  Here's how this could work:                                │     │
│     │   │                                                             │     │
│     │   │  1. When agents complete tasks, they deposit "traces"       │     │
│     │   │     on the paths they took                                  │     │
│     │   │                                                             │     │
│     │   │  2. Traces carry eigenvector signatures                     │     │
│     │   │                                                             │     │
│     │   │  3. Compatible agents naturally gravitate toward            │     │
│     │   │     traces with similar signatures                          │     │
│     │   │                                                             │     │
│     │   │  4. Coalitions form emergently, not by explicit matching    │     │
│     │   │                                                             │     │
│     │   │  Related crystal from your brain:                           │     │
│     │   │  └── "Swarm Intelligence in Multi-Agent Systems" (saved    │     │
│     │   │      Oct 2025, last accessed: never)                        │     │
│     │   │                                                             │     │
│     │   │  Want me to:                                                │     │
│     │   │  [1] Create a plan to prototype this                        │     │
│     │   │  [2] Add as a future idea to Coalition Forge                │     │
│     │   │  [3] Just bookmark for later                                │     │
│     │   │                                                             │     │
│     │   │  > _                                                        │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Creative tangents can become real work items                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Interaction Micropatterns

### Path Autocomplete

```
As Kent types, Gardener provides intelligent completion:

kg self.for█
           │
           ▼
┌─────────────────────────────────────────┐
│ COMPLETIONS:                            │
│                                         │
│ self.forest.manifest    Show forest     │
│ self.forest.evolve      Propose changes │
│ self.forest.prune       Clean up        │
│                                         │
│ Press TAB to complete, ↑↓ to navigate  │
└─────────────────────────────────────────┘
```

### Session Checkpoint Indicator

```
During active sessions, visual indicator shows state:

┌─────────────────────────────────────────────────────────────────┐
│ 🌱 coalition-forge-api │ IMPLEMENT │ ████████░░ 80% │ 23:45   │
└─────────────────────────────────────────────────────────────────┘
  │                        │           │                 │
  │                        │           │                 └── Time in session
  │                        │           └── Progress in phase
  │                        └── Current N-Phase stage
  └── Session name (green = active, yellow = paused)
```

---

### UX Research Sources

- [GitHub Copilot CLI 101](https://github.blog/ai-and-ml/github-copilot-cli-101-how-to-use-github-copilot-from-the-command-line/) — AI-powered CLI patterns
- [GitHub Copilot CLI Repository](https://github.com/github/copilot-cli) — Agentic CLI architecture
- [Warp AI Integration](https://www.infralovers.com/blog/2024-05-19-unlocking-new-possibilities-with-ai-powered-terminal-integration/) — AI-powered terminal UX
- [Fig Autocomplete](https://github.com/withfig/autocomplete) — Declarative completion patterns
- [Command Line Interface Guidelines](https://clig.dev/) — CLI UX best practices

---

*"The garden tends itself, but only because we planted it together."*

*Last updated: 2025-12-15*
