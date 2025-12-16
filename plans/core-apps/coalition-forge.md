---
path: plans/core-apps/coalition-forge
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - monetization/task-credits
  - plans/enterprise-workflows
session_notes: |
  Stub plan created from core-apps-synthesis.
  Low lift, high demo value - proves visible dynamics.
phase_ledger:
  PLAN: touched
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
---

# Coalition Forge

> *"A no-code tool for assembling agent coalitions that accomplish real tasks."*

**Master Plan**: `plans/core-apps-synthesis.md` (Section 2.2)
**Existing Infrastructure**: `agents/town/workshop.py`, `agents/operad/`

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Frame** | Task completion with visible collaboration |
| **Core Mechanic** | Select task → watch coalition form → get output |
| **Revenue** | Per-task credits + enterprise SLAs |
| **Status** | 85% infrastructure ready |

---

## What This Plan Covers

### Absorbs These Original Ideas

| Idea | Source | Integration |
|------|--------|-------------|
| Coalition Forge | `project-proposals.md` | Core concept |
| Agent Town Marketplace | `project-proposals.md` | Citizen selection UI |
| Research Guilds | `money-maximizing-ideas.md` | Task templates |
| Personality Marketplace | `money-maximizing-ideas.md` | Citizen library |

---

## Task Templates

| Task Type | Coalition Shape | Output Format | Credits |
|-----------|-----------------|---------------|---------|
| **Research Report** | Scout + Sage + 2 specialists | Markdown | 50 |
| **Code Review** | Steady + Sync + domain expert | PR comments | 30 |
| **Content Creation** | Spark + Sage + audience-tuned | Multi-format | 40 |
| **Decision Analysis** | Full archetype set | Pros/cons matrix | 75 |
| **Competitive Intel** | Scout + 3 specialists | Briefing doc | 100 |

---

## User Journey

```
1. User selects task type
   └── System suggests coalition composition

2. User reviews/modifies suggested citizens
   └── Eigenvector compatibility shown

3. Coalition forms (visible)
   └── Watch negotiation in real-time

4. Task executes (streamed)
   └── See handoffs, see dialogue

5. Output delivered + replay available
   └── Can rerun with different coalition
```

---

## Technical Foundation

```python
# Already built
from agents.town import (
    Citizen, TownEnvironment, TownFlux,
    TOWN_OPERAD, CoalitionDetector,
)
from agents.town.workshop import (
    WorkshopEnvironment, WorkshopFlux,
    BuilderArchetype,
)
from agents.operad import AGENT_OPERAD, Operation
from agents.sheaf import TownSheaf

# To build
from agents.forge import (
    ForgeTask,           # Task interface
    CoalitionBuilder,    # Formation algorithm
    TaskExecutor,        # Orchestration
    OutputRenderer,      # Format conversion
    ReplayEngine,        # Scrubber
)
```

---

## Implementation Phases

### Phase 1: Core Task Loop (Q1 2025)

**Goal**: Basic task submission → coalition → output

- [ ] Define `ForgeTask` interface with input/output typing
- [ ] Implement coalition formation algorithm
- [ ] Create 5 task templates (research, review, content, decision, intel)
- [ ] Build basic execution orchestration
- [ ] Wire output delivery

**Success Criteria**: User can submit task and get output

### Phase 2: Visibility Layer (Q1-Q2 2025)

**Goal**: Watch agents work together

- [ ] Coalition formation visualization (who joins, why)
- [ ] Dialogue streaming (see conversations)
- [ ] Handoff animations
- [ ] Progress indicators
- [ ] Replay scrubber

**Success Criteria**: User can watch entire process

### Phase 3: Customization (Q2 2025)

**Goal**: Bring your own citizens and tasks

- [ ] Custom citizen import (eigenvector tuning)
- [ ] Task template builder
- [ ] Coalition presets (save favorite combos)
- [ ] Parameter override UI
- [ ] Enterprise workflow definitions

**Success Criteria**: Power users can customize everything

### Phase 4: Marketplace (Q3 2025)

**Goal**: Ecosystem and monetization

- [ ] Task template marketplace
- [ ] Citizen rental system
- [ ] Coalition recipes sharing
- [ ] Revenue sharing model
- [ ] Rating system

**Success Criteria**: Users buy/sell task templates

---

## Revenue Model

```python
TASK_CREDITS = {
    "research_report": 50,
    "code_review": 30,
    "content_creation": 40,
    "decision_analysis": 75,
    "competitive_intel": 100,
}

SUBSCRIPTION_TIERS = {
    LicenseTier.FREE: {
        "credits": 100,
        "tasks": ["research_report"],
        "custom_citizens": False,
    },
    LicenseTier.PRO: {
        "credits": 500,
        "tasks": "all",
        "custom_citizens": True,
        "priority": True,
    },
    LicenseTier.ENTERPRISE: {
        "credits": "unlimited",
        "custom_tasks": True,
        "sla": "99.9%",
    },
}
```

---

## Open Questions

1. **Quality assurance**: How to handle task failures?
2. **Replay value**: Can users rerun with tweaks?
3. **Custom citizens**: What eigenvector constraints?
4. **Task chaining**: Can output of one feed into another?
5. **Human-in-the-loop**: When does user intervene?
6. **Billing granularity**: Per-task or per-minute?

---

## AGENTESE v3 Integration

> *"Coalition formation is composition. Composition is AGENTESE."*

### Path Registry

| AGENTESE Path | Aspect | Handler | Effects |
|---------------|--------|---------|---------|
| `concept.task.manifest` | manifest | Show task template schema | — |
| `concept.task[type].manifest` | manifest | Show specific template | — |
| `?concept.task.*` | query | Search available templates | — |
| `world.coalition.form` | define | Create coalition for task | `SPAWN_AGENTS`, `DEBIT_CREDITS` |
| `world.coalition[id].manifest` | manifest | Watch coalition work | — |
| `world.coalition[id].dialogue.witness` | witness | Stream dialogue history | — |
| `world.coalition[id].subscribe` | witness | Real-time updates | — |
| `world.coalition[id].inject` | refine | Add constraint mid-task | `NOTIFY_CITIZENS` |
| `time.task[id].witness` | witness | Replay task execution | — |
| `self.credits.manifest` | manifest | My credit balance | — |

### Observer-Dependent Perception

```python
# User sees simplified progress + output
await logos("world.coalition[id].manifest", user_umwelt)
# → TaskProgress(status, estimated_time, preview)

# Power user sees full coalition dynamics
await logos("world.coalition[id].manifest", power_user_umwelt)
# → CoalitionView(agents, handoffs, dialogue, eigenvector_compatibility)

# Enterprise admin sees all team tasks + analytics
await logos("?world.coalition.*", admin_umwelt, limit=100)
# → [TaskSummary(id, status, owner, credits_used)]
```

### Subscription Patterns

```python
# Subscribe to coalition dialogue (for live viewing)
sub = await logos.subscribe(
    "world.coalition[*].dialogue",
    delivery=DeliveryMode.AT_LEAST_ONCE,
    buffer_size=500
)

# Subscribe to task completions (for notifications)
complete_sub = await logos.subscribe(
    "world.coalition[*].complete",
    delivery=DeliveryMode.AT_LEAST_ONCE
)
```

### CLI Shortcuts

```yaml
# .kgents/shortcuts.yaml additions
forge: world.coalition.manifest
task: concept.task.manifest
tasks: "?concept.task.*"
coalitions: "?world.coalition.*"
credits: self.credits.manifest
```

### Pipeline Composition (Operad-Native)

```python
# Task composition using >> operator
# Each stage maps to Operad operations
research_pipeline = (
    path("concept.task.research_report")
    >> path("world.coalition.form")
    >> path("world.coalition[*].manifest")
)

# Complex task: research → analyze → document
complex_task = AspectPipeline(
    path("concept.task.research"),
    path("concept.task.analyze"),
    path("concept.task.document"),
    fail_fast=True
)
```

### Eigenvector Compatibility via AGENTESE

```python
# Query citizens by eigenvector compatibility
compatible = await logos(
    "?world.citizen.*",
    user_umwelt,
    filter={"eigenvector.creativity": ">0.7", "eigenvector.analytical": ">0.5"}
)

# Form coalition with specific citizens
coalition = await logos(
    "world.coalition.form",
    user_umwelt,
    citizens=compatible[:5],
    task="concept.task.research_report"
)
```

---

## Dependencies

| System | Usage |
|--------|-------|
| `agents/town/` | Coalition formation |
| `agents/town/workshop.py` | Builder archetypes |
| `agents/operad/` | Composition grammar |
| `agents/sheaf/` | Output coherence |
| `protocols/billing/` | Credit system |
| `protocols/agentese/` | Path-based interaction (v3) |

---

## Differentiator

**Not just task completion—visible process.**

> "Kids on a playground" energy: watch them figure it out together.
> Coalition dynamics are the product, not just the task output.

---

## UX Research: Reference Flows

### Proven Patterns from No-Code Workflow Builders

#### 1. Zapier's AI-First Onboarding
**Source**: [Zapier Automation Review 2025](https://thedigitalprojectmanager.com/tools/zapier-review/)

Zapier's natural language workflow creation is the gold standard:

| Zapier Pattern | Coalition Forge Adaptation |
|----------------|---------------------------|
| **"Describe what you want"** → AI generates Zap | **"Describe your task"** → AI suggests coalition |
| **8,000+ app integrations** | **Citizen library** with eigenvector-tagged specialists |
| **Visual step-by-step preview** | **Coalition preview** showing who does what |
| **Test before activate** | **Dry run mode** — watch agents discuss without executing |

**Key Insight**: Zapier's Copilot removes "initial confusion" for beginners. Coalition Forge must do the same: **natural language in, visible process out**.

#### 2. Make's Visual Flowchart Builder
**Source**: [Zapier vs Make Comparison](https://www.nocode.mba/articles/zapier-vs-make)

Make's flowchart approach offers advantages for complex orchestrations:

| Make Pattern | Coalition Forge Application |
|--------------|----------------------------|
| **Visual flowchart** (see entire process at a glance) | **Coalition topology view** — see who talks to whom |
| **Branching paths** | **Conditional handoffs** — if Scout finds X, route to Specialist Y |
| **Error handling built-in** | **Recovery strategies** — if agent fails, fallback options visible |
| **Module library** | **Citizen library** — browse by archetype, eigenvector, or skill |

**Key Insight**: Make's visual representation helps users understand complex flows. Coalition Forge should show **the coalition as a living diagram**.

#### 3. No-Code Automation Trends (2024-2025)
**Source**: [No-Code AI Workflow Tools Guide](https://www.vellum.ai/blog/no-code-ai-workflow-automation-tools-guide)

- **84% of organizations** already use low/no-code tools
- **AI-enabled workflows** growing from 3% to 25% by end of 2025
- Key components: drag-and-drop builders, ready-made integrations, conditional logic

---

## Precise User Flows

### Flow 1: First Task ("The Quick Win")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: User lands on Coalition Forge homepage                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. DESCRIBE TASK (0-30 seconds)                                             │
│     ├── Hero input: "What do you need done?"                                 │
│     ├── Placeholder: "Research competitors for my SaaS product..."          │
│     ├── User types: "Research the top 5 project management tools"           │
│     └── [Form Coalition] button activates                                    │
│                                                                              │
│  2. COALITION PREVIEW (30-60 seconds)                                        │
│     ├── AI analyzes task → suggests coalition:                               │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────┐         │
│     │   │        SUGGESTED COALITION                               │         │
│     │   │                                                          │         │
│     │   │   🔍 Scout        →  🧙 Sage       →  📝 Scribe         │         │
│     │   │   (Research)         (Analyze)        (Document)         │         │
│     │   │                                                          │         │
│     │   │   Estimated: 15 credits | ~3 minutes                     │         │
│     │   └─────────────────────────────────────────────────────────┘         │
│     │                                                                        │
│     ├── Expandable: Click citizen → see eigenvectors, past performance      │
│     └── [Start Task] [Customize Coalition] [Save as Template]               │
│                                                                              │
│  3. WATCH EXECUTION (2-5 minutes)                                            │
│     ├── Real-time dialogue stream:                                           │
│     │   ├── Scout: "I found 5 tools. Analyzing Asana first..."              │
│     │   ├── Sage: "Asana's strength is timeline view. Weakness is..."       │
│     │   └── Scribe: "Documenting. Current section: Asana Overview"          │
│     ├── Progress bar with agent avatars                                      │
│     ├── Handoff animations (Scout → Sage glow effect)                        │
│     └── [Pause] [Speed Up (2x)] [Add Constraint] visible                    │
│                                                                              │
│  4. RECEIVE OUTPUT                                                           │
│     ├── Task complete notification                                           │
│     ├── Output rendered: Markdown report                                     │
│     ├── Options: [Download] [Copy] [Share] [Edit]                            │
│     ├── Replay available: [Watch Again]                                      │
│     └── Credits deducted: "45 credits remaining"                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: Custom Coalition ("The Power User")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: User clicks [Build Custom Coalition]                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SELECT CITIZENS (1-3 minutes)                                            │
│     ├── Citizen Library view:                                                │
│     │                                                                        │
│     │   ┌────────────────────────────────────────────────────────────┐      │
│     │   │  CITIZEN LIBRARY                    [Search] [Filter ▼]    │      │
│     │   ├────────────────────────────────────────────────────────────┤      │
│     │   │                                                            │      │
│     │   │  🔍 SCOUT          ⚡ SPARK          🧙 SAGE              │      │
│     │   │  Research,         Creativity,       Analysis,            │      │
│     │   │  Investigation     Ideation          Synthesis            │      │
│     │   │  [+Add]            [+Add]            [+Add]               │      │
│     │   │                                                            │      │
│     │   │  🤝 SYNC           🏔️ STEADY        📝 SCRIBE            │      │
│     │   │  Coordination,     Reliability,      Documentation,       │      │
│     │   │  Facilitation      Persistence       Formatting           │      │
│     │   │  [+Add]            [+Add]            [+Add]               │      │
│     │   │                                                            │      │
│     │   └────────────────────────────────────────────────────────────┘      │
│     │                                                                        │
│     ├── Drag citizens to Coalition Canvas                                    │
│     └── Eigenvector compatibility meter updates in real-time                 │
│                                                                              │
│  2. DEFINE HANDOFFS                                                          │
│     ├── Coalition Canvas (visual editor):                                    │
│     │                                                                        │
│     │   ┌──────────────────────────────────────────────────────────┐        │
│     │   │                                                          │        │
│     │   │    🔍 Scout ──────► 🧙 Sage                              │        │
│     │   │         │              │                                 │        │
│     │   │         │              ▼                                 │        │
│     │   │         └─────► ⚡ Spark ───► 📝 Scribe                  │        │
│     │   │                                                          │        │
│     │   └──────────────────────────────────────────────────────────┘        │
│     │                                                                        │
│     ├── Click connection → configure trigger condition                       │
│     ├── "When Scout finds > 5 items, also send to Spark"                    │
│     └── Branch conditions visible on connections                             │
│                                                                              │
│  3. TEST RUN                                                                 │
│     ├── [Dry Run] → Agents discuss but don't execute real actions           │
│     ├── Sample output preview                                                │
│     └── "This coalition would cost ~25 credits. Proceed?"                   │
│                                                                              │
│  4. SAVE & REUSE                                                             │
│     ├── [Save as Template] → naming modal                                    │
│     ├── Template added to personal library                                   │
│     └── Optional: [Publish to Marketplace]                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 3: Enterprise Workflow ("The Team Standard")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Team lead creates standard workflow for recurring task              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. CREATE WORKFLOW DEFINITION                                               │
│     ├── Admin panel: [Create New Workflow]                                   │
│     ├── Define inputs:                                                       │
│     │   ├── {{company_name}} - text input                                   │
│     │   ├── {{report_depth}} - dropdown: Quick/Standard/Deep                │
│     │   └── {{notify_channel}} - Slack channel picker                       │
│     ├── Build coalition with variables                                       │
│     └── Set approval requirements: "Requires manager review if > 100 creds" │
│                                                                              │
│  2. ASSIGN TO TEAM                                                           │
│     ├── Workflow published to team library                                   │
│     ├── Permissions: Who can run? Who can edit?                              │
│     ├── Budget allocation: "This workflow draws from Project X budget"      │
│     └── Notifications: Slack/email when workflow completes                   │
│                                                                              │
│  3. TEAM MEMBER USAGE                                                        │
│     ├── Team member opens workflow library                                   │
│     ├── Sees: "Competitive Analysis" [Run]                                   │
│     ├── Fills in required inputs                                             │
│     ├── [Submit] → workflow queues                                           │
│     └── Notification: "Your analysis is ready for review"                    │
│                                                                              │
│  4. ANALYTICS & ITERATION                                                    │
│     ├── Dashboard shows:                                                     │
│     │   ├── Runs this month: 47                                              │
│     │   ├── Avg completion time: 4.2 min                                     │
│     │   ├── Credit spend: 1,200                                              │
│     │   └── Success rate: 94%                                                │
│     ├── Failed runs traceable → click to see agent dialogue                  │
│     └── [Optimize] suggests coalition improvements                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 4: Watching Coalition Dynamics ("The Learning Moment")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: User watching a complex task with visible agent collaboration       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  VIEW: Split-pane interface                                                  │
│                                                                              │
│  ┌─────────────────────────────────┬─────────────────────────────────────┐  │
│  │                                 │                                     │  │
│  │    COALITION MAP               │    DIALOGUE STREAM                  │  │
│  │                                 │                                     │  │
│  │    🔍 ──────► 🧙               │    [Scout]: "Found 7 competitors.   │  │
│  │     ↓ (active)   ↓              │    Prioritizing by market share."  │  │
│  │    ⚡ ◄────── 📝               │                                     │  │
│  │                                 │    [Sage]: "I'll analyze the top   │  │
│  │    Legend:                      │    3 first. Scout, send details    │  │
│  │    ─► Active handoff           │    on Asana."                       │  │
│  │    ··· Waiting                  │                                     │  │
│  │    ▓▓▓ Completed               │    [Scout → Sage]: Sending Asana   │  │
│  │                                 │    profile (47 data points)        │  │
│  │                                 │                                     │  │
│  └─────────────────────────────────┴─────────────────────────────────────┘  │
│                                                                              │
│  CONTROLS:                                                                   │
│  [▶ Play/Pause] [◀◀ Rewind] [1x ▼ Speed] [📍 Bookmark] [💬 Comment]        │
│                                                                              │
│  INSIGHTS PANEL (collapsed by default):                                      │
│  ├── "Scout made 3 API calls (Google, LinkedIn, Crunchbase)"                │
│  ├── "Sage spent 45 tokens on analysis"                                      │
│  └── "Total dialogue: 127 messages"                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Interaction Micropatterns

### Coalition Suggestion Algorithm Display

```
[User describes task]
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 🤖 Analyzing your task...                                       │
│                                                                  │
│ Detected needs:                                                  │
│   ✓ Research (confidence: 92%)                                   │
│   ✓ Analysis (confidence: 87%)                                   │
│   ✓ Documentation (confidence: 79%)                              │
│   ○ Creativity (confidence: 34%) — not included                  │
│                                                                  │
│ Suggested coalition matches 94% of similar successful tasks     │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
[User can override any suggestion with one click]
```

### Eigenvector Compatibility Visualization

```
When user adds citizen to coalition:

┌─────────────────────────────────────────────────────────────┐
│ COMPATIBILITY CHECK                                          │
│                                                              │
│ 🔍 Scout + 🧙 Sage                                          │
│                                                              │
│ Creativity    ████░░░░░░ 40%     ████████░░ 80%             │
│ Analytical    ██████████ 100%    ██████████ 100%   ✓ Match  │
│ Social        ██░░░░░░░░ 20%     ████░░░░░░ 40%             │
│                                                              │
│ Overall compatibility: 87% ✓ Good pairing                   │
└─────────────────────────────────────────────────────────────┘
```

---

## References

- Master plan: `plans/core-apps-synthesis.md` §2.2
- Original idea: `brainstorming/2025-12-15-project-proposals.md`
- Existing code: `impl/claude/agents/town/workshop.py`

### UX Research Sources

- [Zapier Automation Review 2025](https://thedigitalprojectmanager.com/tools/zapier-review/) — AI-first workflow creation
- [Zapier vs Make Comparison](https://www.nocode.mba/articles/zapier-vs-make) — Visual builder patterns
- [No-Code AI Workflow Tools Guide](https://www.vellum.ai/blog/no-code-ai-workflow-automation-tools-guide) — Market trends 2024-2025
- [Zapier No-Code Automation Guide](https://zapier.com/blog/no-code-automation/) — Core builder components
- [Zapier Interfaces Guide](https://zapier.com/blog/zapier-interfaces-guide/) — No-code app patterns

---

*Last updated: 2025-12-15*
