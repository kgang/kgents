---
path: plans/core-apps/punchdrunk-park
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - monetization/experience-tickets
  - plans/enterprise-training
  - plans/multiplayer-inhabit
session_notes: |
  Stub plan created from core-apps-synthesis.
  The "Westworld" vision - Kent's grandest strategy.
  INHABIT mode (91 tests) provides foundation.
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
  planned: 0.12
  spent: 0.0
  returned: 0.0
---

# Punchdrunk Park

> *"Westworld-like simulation where citizens can say no."*

**Master Plan**: `plans/core-apps-synthesis.md` (Section 2.4)
**Existing Infrastructure**: `agents/town/inhabit_session.py` (91 tests)

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Frame** | Narrative experiences with agent consent |
| **Core Mechanic** | INHABIT citizen → live story → consent dynamics |
| **Revenue** | Experience tickets + seasonal passes |
| **Status** | 80% ready (INHABIT mode complete) |

---

## The Punchdrunk Principle

> *"Collaboration > control. Citizen refusal is core feature, not bug."*

### Consent Mechanics

| Mechanic | Description |
|----------|-------------|
| **Consent Debt** | Continuous [0,1], not binary yes/no |
| **Force Mechanic** | 3x cost, 3/session limit, logged |
| **Alignment Threshold** | Citizens resist misaligned requests |
| **Negotiation** | Citizens can counter-propose |

---

## What This Plan Covers

### Absorbs These Original Ideas

| Idea | Source | Integration |
|------|--------|-------------|
| Punchdrunk Park | `project-proposals.md` | Core concept |
| Agent Academy | `project-proposals.md` | Learning mode |
| Learning Town | `self-education-productivity-ideas.md` | Education scenarios |
| Simulation Dojo | `self-education-productivity-ideas.md` | Practice mode |
| Dialogue Masks | `art-creativity-ideas.md` | Eigenvector game |

---

## Scenario Types

| Type | Description | Learning Value |
|------|-------------|----------------|
| **Mystery** | Something happened; investigate | Deduction, questioning |
| **Collaboration** | Shared goal, form coalitions | Teamwork, negotiation |
| **Conflict** | Competing factions | Strategy, persuasion |
| **Emergence** | No plot, pure simulation | Observation, adaptation |
| **Practice** | Skill-specific scenarios | Domain expertise |

---

## Holographic Metaphor Reification

The same Town manifests differently for different observers:

```python
# Same Town, different experiences
await logos.invoke("world.town.manifest", architect_umwelt)   # → Power structures
await logos.invoke("world.town.manifest", poet_umwelt)        # → Relationship webs
await logos.invoke("world.town.manifest", economist_umwelt)   # → Resource flows
await logos.invoke("world.town.manifest", child_umwelt)       # → Wonder and play
```

---

## Technical Foundation

```python
# Already built (91 tests)
from agents.town import (
    Citizen, TownEnvironment, TownFlux,
    CitizenPhase, TOWN_OPERAD,
)
from agents.town.inhabit_session import (
    InhabitSession,
    ConsentLedger,
    AlignmentCalculator,
)
from agents.k import soul, KgentFlux

# To build
from agents.park import (
    ScenarioTemplate,     # Scenario definitions
    DirectorAgent,        # Pacing and serendipity
    UmweltSelector,       # Observer perspective choice
    NarrativeExporter,    # Witness → story
    MultiplayerSession,   # Shared experiences
    SkillPolynomial,      # Learning tracking
)
```

---

## Implementation Phases

### Phase 1: Scenario Framework (Q1 2025)

**Goal**: Replayable narrative templates

- [ ] Create `ScenarioTemplate` schema
- [ ] Build 5 starter scenarios (1 per type)
- [ ] Implement basic INHABIT flow
- [ ] Wire K-gent feedback
- [ ] Add scenario replay

**Success Criteria**: User can complete a scenario

### Phase 2: Learning Mechanics (Q2 2025)

**Goal**: Track and improve skills

- [ ] Implement `SkillPolynomial` state machine
- [ ] Add adaptive difficulty
- [ ] Create progress persistence
- [ ] Build K-gent feedback analysis
- [ ] Replay with annotations

**Success Criteria**: User sees measurable improvement

### Phase 3: Social Features (Q2-Q3 2025)

**Goal**: Shared experiences

- [ ] Multiplayer INHABIT (same Town, different views)
- [ ] Scenario sharing
- [ ] Leaderboards (optional)
- [ ] Coalition watching mode (spectate others)
- [ ] Social proof mechanics

**Success Criteria**: Multiple users in same scenario

### Phase 4: Enterprise (Q3-Q4 2025)

**Goal**: Corporate training applications

- [ ] Scenario authoring tools
- [ ] Assessment framework
- [ ] Team analytics dashboard
- [ ] LMS integration (SCORM/xAPI)
- [ ] Custom branding

**Success Criteria**: Enterprise customer signs

---

## User Journey Example: Practice Scenario

```
Setup: Board Presentation Practice
├── User: "I need to practice defending Q4 strategy"
├── System spawns 5 board member agents
│   ├── Skeptical Sarah (CFO background)
│   ├── Technical Tom (CTO background)
│   ├── Political Paula (competitive focus)
│   ├── Supportive Sam (ally, needs talking points)
│   └── Quiet Quinn (silent, reveals concerns when prompted)
└── INHABIT: User enters as "CEO presenting"

Round 1: Initial Presentation
├── User presents (5 min)
├── Sarah challenges: "30% growth basis?"
├── Tom probes: "ML expertise hired?"
└── Quinn stays silent (missed opportunity)

Feedback: K-gent Analysis
├── "You got defensive with Sarah"
├── "You speak faster when challenged"
├── "Quinn had a concern—read the room"
└── Suggestion: "Try again? I'll increase difficulty"

Round 2+: Adaptive Difficulty
├── Sarah more aggressive
├── User practices new approach
├── Emergent: Quinn finally speaks
└── Skill: COMPETENT → PROFICIENT
```

---

## Revenue Model

```python
TICKETS = {
    "single_scenario": 5,
    "scenario_pack_5": 20,
    "day_pass": 15,
    "monthly_pass": 49,
    "season_pass": 149,
}

ENTERPRISE = {
    "team_training": "custom",
    "branded_scenarios": "custom",
    "assessment_mode": "custom",
    "dedicated_support": "included",
}
```

---

## Dialogue Masks Integration

From `art-creativity-ideas.md`:

```python
MASK_DECK = {
    "trickster": DialogueMask(
        name="The Trickster",
        eigenvector_transform=EigenvectorTransform(
            creativity_delta=+0.3,
            trust_delta=-0.2,
        ),
    ),
    "dreamer": DialogueMask(...),
    "skeptic": DialogueMask(...),
    "architect": DialogueMask(...),
    "child": DialogueMask(...),
}
```

Users can wear masks during scenarios, forcing novel behaviors.

---

## Open Questions

1. **Scenario authoring**: How do users/enterprises create scenarios?
2. **Multiplayer**: Can multiple users INHABIT same Town?
3. **Persistence**: Do characters remember across sessions?
4. **Assessment**: How to measure skill improvement objectively?
5. **Ethical boundaries**: What scenarios are off-limits?
6. **Mask mechanics**: When to offer mask options?
7. **Serendipity injection**: How much chaos is optimal?

---

## AGENTESE v3 Integration

> *"Collaboration > control. The verb-first ontology makes consent explicit."*

### Path Registry

| AGENTESE Path | Aspect | Handler | Effects |
|---------------|--------|---------|---------|
| `world.town.manifest` | manifest | Observer-dependent view | — |
| `world.town.scenario[id].manifest` | manifest | Scenario details | — |
| `world.town.scenario[id].inhabit` | define | Start INHABIT session | `SPAWN_SESSION`, `DEBIT_TICKET` |
| `world.town.inhabit[id].manifest` | manifest | Current session state | — |
| `world.town.inhabit[id].act` | define | Player action | `UPDATE_CONSENT_LEDGER` |
| `world.town.inhabit[id].dialogue` | witness | Dialogue history | — |
| `self.consent.manifest` | manifest | My consent debt | — |
| `self.consent.force` | define | Use force mechanic | `3X_COST`, `LOG_FORCE`, `UPDATE_DEBT` |
| `concept.mask.manifest` | manifest | Available masks | — |
| `concept.mask[name].don` | define | Wear mask | `TRANSFORM_EIGENVECTOR` |
| `void.entropy.inject` | sip | Serendipity injection | `MODIFY_SCENARIO` |
| `time.inhabit[id].witness` | witness | Session replay | — |
| `?world.town.scenario.*` | query | Search scenarios | — |

### Observer-Dependent Perception (Core Feature)

```python
# The same Town manifests differently for different observers
# This is THE Punchdrunk principle in action

# Architect sees power structures
await logos("world.town.manifest", architect_umwelt)
# → TownView(power_nodes, influence_edges, authority_hierarchy)

# Poet sees relationship webs
await logos("world.town.manifest", poet_umwelt)
# → TownView(emotional_bonds, trust_networks, metaphor_layers)

# Economist sees resource flows
await logos("world.town.manifest", economist_umwelt)
# → TownView(capital_distribution, transaction_history, wealth_gaps)

# Child sees wonder and play
await logos("world.town.manifest", child_umwelt)
# → TownView(play_spaces, friendly_faces, adventure_hooks)
```

### Consent Mechanics via AGENTESE

```python
# Force uses the 3x cost, logged mechanic
# This is NOT just an API call—it's an AGENTESE path with explicit effects
await logos(
    "self.consent.force",
    player_umwelt,
    target_citizen="sarah",
    request="approve the budget",
    effects=["3X_CONSENT_COST", "LOG_TO_AUDIT", "UPDATE_DEBT"]
)
# Returns: ForceResult(success=True, debt_remaining=0.4, forces_left=2)

# Consent debt is queryable
debt = await logos("self.consent.manifest", player_umwelt)
# → ConsentLedger(overall=0.6, per_citizen={"sarah": 0.2, "tom": 0.9, ...})
```

### Subscription Patterns

```python
# Live consent updates during INHABIT
consent_sub = await logos.subscribe(
    "world.town.inhabit[*].consent",
    delivery=DeliveryMode.AT_LEAST_ONCE
)

# Citizen dialogue stream
dialogue_sub = await logos.subscribe(
    "world.town.inhabit[id].dialogue",
    delivery=DeliveryMode.AT_LEAST_ONCE,
    buffer_size=1000
)

# Serendipity events (Director-injected surprises)
entropy_sub = await logos.subscribe(
    "void.entropy.inject",
    delivery=DeliveryMode.AT_MOST_ONCE
)
```

### CLI Shortcuts

```yaml
# .kgents/shortcuts.yaml additions
park: world.town.manifest
scenarios: "?world.town.scenario.*"
inhabit: world.town.scenario.inhabit
consent: self.consent.manifest
force: self.consent.force
masks: concept.mask.manifest
replay: time.inhabit.witness
```

### Pipeline Composition

```python
# Scenario selection → INHABIT → K-gent feedback
experience_pipeline = (
    path("world.town.scenario[id].manifest")
    >> path("world.town.scenario[id].inhabit")
    >> path("time.inhabit[id].witness")  # Replay available
    >> path("self.soul.feedback")        # K-gent analysis
)

# Mask application affects subsequent interactions
masked_session = (
    path("concept.mask[trickster].don")
    >> path("world.town.scenario[id].inhabit")
    # All dialogue now filtered through trickster eigenvectors
)
```

### Multiplayer via Shared Subscriptions

```python
# Two players in same scenario, different perspectives
# Both subscribe to same session, different views

# Player A (Detective)
detective_view = await logos(
    "world.town.inhabit[id].manifest",
    detective_umwelt
)
# → DetectiveView(evidence, suspects, access_level="security")

# Player B (Journalist)
journalist_view = await logos(
    "world.town.inhabit[id].manifest",
    journalist_umwelt
)
# → JournalistView(sources, leads, access_level="public")

# Convergence: when paths cross
convergence_sub = await logos.subscribe(
    "world.town.inhabit[id].convergence",
    delivery=DeliveryMode.AT_LEAST_ONCE
)
```

---

## Dependencies

| System | Usage |
|--------|-------|
| `agents/town/` | Simulation core |
| `agents/town/inhabit_session.py` | INHABIT mode (91 tests) |
| `agents/k/` | Dialogue + feedback |
| `protocols/agentese/` | Path-based interaction (v3) |
| `protocols/billing/` | Ticket system |

---

## Differentiator

**Citizens can say no.**

> The Punchdrunk principle: collaboration > control.
> Refusal is a feature, not a bug.
> Force mechanic is expensive and logged—consent matters.

This is not a puppet show. Citizens have eigenvectors, preferences, and autonomy. The drama emerges from authentic interaction, not scripted responses.

---

## UX Research: Reference Flows

### Proven Patterns from Immersive Experiences

#### 1. Punchdrunk's Sleep No More
**Source**: [Punchdrunk Handbook](https://worldxo.org/punchdrunk-handbook-immersive-pioneers-share-20-years-of-learnings/)

Sleep No More (2011-2025) is the foundational reference for immersive simulation design:

| Sleep No More Pattern | Punchdrunk Park Adaptation |
|-----------------------|----------------------------|
| **100 rooms, 5 floors** (open exploration) | `TownMap` — explorable districts, buildings, rooms |
| **Masks for audience** (anonymity + demarcation) | `ObserverMode` — watch without direct interaction |
| **Touch-real detail** (rummage in drawers) | `DeepInteraction` — every object has backstory |
| **Choose who to follow** | `CitizenFollow` — attach to any citizen's perspective |
| **Multi-sensory** (smell, temperature) | `AtmosphericLayer` — mood, tension, ambient cues |

**Key Insight**: "Masks help audience members loosen up, shake off inhibitions, and become more receptive to participation." INHABIT mode should feel like **removing the mask** — the moment you step from observer to participant.

#### 2. AI Dungeon's Narrative Memory
**Source**: [AI Dungeon Review 2025](https://www.aiapps.com/blog/ai-dungeon-review-2025-interactive-storytelling-with-artificial-intelligence/)

AI Dungeon's memory improvements directly inform Punchdrunk Park:

| AI Dungeon Pattern | Punchdrunk Park Application |
|-------------------|----------------------------|
| **Do/Say/Story/See** input modes | `ActionPalette` — distinct interaction verbs |
| **Memory layers** (persist across sessions) | `CitizenMemory` — NPCs remember past encounters |
| **SCORE system** (coherence, emotional consistency) | `NarrativeCoherence` — K-gent maintains story logic |
| **Community scenarios** | `ScenarioLibrary` — shareable scenario templates |

**Key Insight**: "Storylines now retain details across sessions—something earlier models struggled with." Citizens must **remember** the player's previous actions.

#### 3. Character.AI's Personality Persistence
**Source**: [AI Roleplay Guide 2025](https://aimojo.io/rise-of-ai-roleplay/)

Character.AI's personality-rich interactions inform citizen design:

| Character.AI Pattern | Punchdrunk Park Application |
|---------------------|----------------------------|
| **AI characters remember past interactions** | `EigenvectorPersistence` — traits evolve with interaction |
| **Community character creation** | `CitizenCustomization` — create/share citizen templates |
| **Natural, evolving dialogue** | `DynamicDialogue` — conversation shaped by consent debt |
| **Easy-to-use interface** | `QuickINHABIT` — one-click scenario entry |

**Key Insight**: "Focus on AI-driven character interactions...personality-rich conversations that feel natural and evolving." Citizens should feel like **individuals, not NPCs**.

#### 4. Consent and Ethical Design
**Source**: [AI Roleplay Ethics](https://aimojo.io/rise-of-ai-roleplay/)

Critical patterns for consent mechanics:

| Ethical Pattern | Punchdrunk Park Implementation |
|----------------|-------------------------------|
| **Explicit consent** | `ConsentLedger` — all interactions logged |
| **Age verification** | Platform-level verification |
| **Moderation tools** | `ScenarioGuardrails` — content filters |
| **User data protection** | Privacy-first, optional cloud |

---

## Precise User Flows

### Flow 1: First INHABIT ("The Threshold Crossing")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: User selects a scenario                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SCENARIO SELECTION (0-30 seconds)                                        │
│     ├── Scenario Library:                                                    │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  SCENARIO LIBRARY                         [Search] [New]    │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  🏢 BOARD PRESENTATION PRACTICE          ⏱ 15-30 min       │     │
│     │   │     Practice defending your strategy to skeptical execs    │     │
│     │   │     Citizens: 5 | Difficulty: Medium | [▶ Start]           │     │
│     │   │                                                             │     │
│     │   │  🔍 MYSTERY: THE MISSING ENGINEER        ⏱ 30-60 min       │     │
│     │   │     Someone vanished from the office. Investigate.          │     │
│     │   │     Citizens: 12 | Difficulty: Hard | [▶ Start]            │     │
│     │   │                                                             │     │
│     │   │  🤝 TEAM CONFLICT RESOLUTION             ⏱ 20-40 min       │     │
│     │   │     Two team members are at odds. Find common ground.       │     │
│     │   │     Citizens: 4 | Difficulty: Easy | [▶ Start]             │     │
│     │   │                                                             │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── User clicks [▶ Start] on Board Presentation                         │
│                                                                              │
│  2. ROLE ASSIGNMENT (10-30 seconds)                                          │
│     ├── "Who will you be?"                                                   │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────┐         │
│     │   │                                                         │         │
│     │   │   You are: CEO presenting Q4 strategy                   │         │
│     │   │                                                         │         │
│     │   │   Your goal: Defend the strategy, address concerns      │         │
│     │   │                                                         │         │
│     │   │   The board:                                            │         │
│     │   │   • 😤 Sarah (CFO) — Skeptical about costs              │         │
│     │   │   • 🤔 Tom (CTO) — Concerned about tech readiness       │         │
│     │   │   • 🗳️ Paula (Competitive) — Focused on rivals          │         │
│     │   │   • 😊 Sam (Ally) — Supportive but needs talking points │         │
│     │   │   • 😶 Quinn (Quiet) — Silent observer with hidden concerns │     │
│     │   │                                                         │         │
│     │   │   [I'm ready] [Customize my role]                       │         │
│     │   └─────────────────────────────────────────────────────────┘         │
│     │                                                                        │
│     └── User clicks [I'm ready]                                              │
│                                                                              │
│  3. THRESHOLD MOMENT (5 seconds)                                             │
│     ├── Screen transition: "Entering the boardroom..."                       │
│     ├── Ambient audio fades in (clock ticking, papers shuffling)            │
│     ├── Citizens are visible, waiting                                        │
│     └── First citizen speaks: "Thank you for joining us. Please begin."    │
│                                                                              │
│  4. INHABITATION (15-30 minutes)                                             │
│     ├── Interaction panel:                                                   │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  BOARDROOM                           Session: 00:04:23      │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  Sarah: "Your growth projections seem aggressive.          │     │
│     │   │          What's the basis for 30% increase?"               │     │
│     │   │                                                             │     │
│     │   │  ┌─────────────────────────────────────────────────────┐   │     │
│     │   │  │ Your response:                                       │   │     │
│     │   │  │ [Type your response...]                              │   │     │
│     │   │  │                                                       │   │     │
│     │   │  │ Quick actions: [Defer] [Challenge] [Ask for data]   │   │     │
│     │   │  └─────────────────────────────────────────────────────┘   │     │
│     │   │                                                             │     │
│     │   │  [💡 Hint] [⏸️ Pause] [🚪 Exit]                            │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Citizens respond dynamically, consent debt tracked                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: Consent Negotiation ("The Refusal Moment")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: User asks citizen to do something against their nature              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. THE REQUEST                                                              │
│     ├── User types: "Sarah, just approve the budget without questioning"    │
│     └── System evaluates against Sarah's eigenvectors                        │
│         ├── Sarah's traits: skeptical (0.9), analytical (0.8), direct (0.7) │
│         └── Request alignment: VERY LOW (0.15)                               │
│                                                                              │
│  2. THE REFUSAL                                                              │
│     ├── Sarah responds:                                                      │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────┐         │
│     │   │  Sarah: "I'm not going to rubber-stamp this. My job     │         │
│     │   │          is to scrutinize the numbers, not blindly      │         │
│     │   │          approve. If you want my support, show me       │         │
│     │   │          the data."                                     │         │
│     │   │                                                         │         │
│     │   │  ⚠️ CONSENT ALERT                                       │         │
│     │   │  This request conflicts with Sarah's core traits.       │         │
│     │   │                                                         │         │
│     │   │  Options:                                               │         │
│     │   │  • [Rephrase] Try a different approach                  │         │
│     │   │  • [Negotiate] Offer something in return                │         │
│     │   │  • [Force] Use force (costs 3x, limit 3/session)       │         │
│     │   │  • [Accept] Respect her position                        │         │
│     │   └─────────────────────────────────────────────────────────┘         │
│     │                                                                        │
│     └── Consent debt meter visible: ████████░░ (80%)                        │
│                                                                              │
│  3a. IF USER CHOOSES [Force]                                                 │
│     ├── Confirmation: "Force costs 3x consent. You have 2 forces remaining" │
│     ├── Sarah complies reluctantly:                                          │
│     │   "Fine. But I'm noting my objection in the minutes."                 │
│     ├── Consent debt drops: ██████░░░░ (60%)                                │
│     └── Session log notes: "FORCE used at 00:12:34"                         │
│                                                                              │
│  3b. IF USER CHOOSES [Negotiate]                                             │
│     ├── User types: "What if I show you the competitive analysis first?"    │
│     ├── Sarah: "That would help. Let me see the market data."              │
│     ├── Counter-proposal accepted                                            │
│     └── Consent debt stable: ████████░░ (80%)                               │
│                                                                              │
│  3c. IF USER CHOOSES [Accept]                                                │
│     ├── User types: "Fair enough. Let me walk you through the numbers."    │
│     ├── Sarah: "That's more like it. Show me the Q3 actuals first."        │
│     └── Consent debt increases: ████████░░ → █████████░ (90%)              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 3: K-gent Feedback ("The Learning Loop")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Session ends, K-gent provides analysis                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SESSION SUMMARY                                                          │
│     ├── Transition: "Session ending... Preparing feedback..."               │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  SESSION COMPLETE                          Duration: 23:47  │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  OUTCOME: Strategy approved with modifications              │     │
│     │   │                                                             │     │
│     │   │  YOUR PERFORMANCE:                                          │     │
│     │   │  ├── Persuasion:     ████████░░ 80%                        │     │
│     │   │  ├── Adaptability:   ██████████ 100%                       │     │
│     │   │  ├── Listening:      ██████░░░░ 60%                        │     │
│     │   │  └── Consent Used:   ████░░░░░░ 40% (1 force)              │     │
│     │   │                                                             │     │
│     │   │  [See Detailed Feedback] [Replay Key Moments] [Try Again]  │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── User clicks [See Detailed Feedback]                                  │
│                                                                              │
│  2. K-GENT ANALYSIS                                                          │
│     ├── K-gent appears (conversational, warm):                               │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  🧠 K-GENT FEEDBACK                                         │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  "You did well overall. A few observations:                │     │
│     │   │                                                             │     │
│     │   │  STRENGTH: When Sarah challenged the 30% growth,           │     │
│     │   │  you pivoted to showing historical data. Smart move.       │     │
│     │   │                                                             │     │
│     │   │  GROWTH AREA: You spoke faster when challenged.            │     │
│     │   │  At 12:34, your response was 2x faster than your          │     │
│     │   │  baseline. This can signal defensiveness.                  │     │
│     │   │                                                             │     │
│     │   │  MISSED OPPORTUNITY: Quinn was silent the whole            │     │
│     │   │  session. They had a concern about team capacity.          │     │
│     │   │  Next time, try directly addressing the quiet ones.        │     │
│     │   │                                                             │     │
│     │   │  Overall: COMPETENT → PROFICIENT                           │     │
│     │   │                                                             │     │
│     │   │  Want to try again with increased difficulty?"             │     │
│     │   │                                                             │     │
│     │   │  [Yes, harder] [Same level] [Different scenario] [Done]   │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Progress saved to skill polynomial                                   │
│                                                                              │
│  3. REPLAY KEY MOMENTS                                                       │
│     ├── User clicks [Replay Key Moments]                                     │
│     ├── Timeline scrubber with annotated moments:                            │
│     │   ├── 00:04:23 — "Sarah's first challenge" ⭐                         │
│     │   ├── 00:12:34 — "Force used" ⚠️                                      │
│     │   ├── 00:18:45 — "Paula's pivot" 💡                                   │
│     │   └── 00:22:12 — "Quinn's silence" ❓                                  │
│     └── Can replay any segment, see citizen internal states                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 4: Multiplayer INHABIT ("The Shared Stage")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: Two users in the same scenario, different perspectives             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. SESSION CREATION                                                         │
│     ├── User A creates multiplayer session:                                  │
│     │   "Mystery: The Missing Engineer" — 2-4 players                       │
│     ├── Invite link generated                                                │
│     └── User B joins via link                                                │
│                                                                              │
│  2. ROLE DISTRIBUTION                                                        │
│     ├── User A: Detective assigned to the case                               │
│     ├── User B: Journalist investigating the company                         │
│     ├── Both see same Town, different citizens trust them differently       │
│     └── Neither knows what the other has discovered                          │
│                                                                              │
│  3. PARALLEL EXPLORATION                                                     │
│     ├── User A (Detective):                                                  │
│     │   ├── Can access: Security logs, police contacts                       │
│     │   ├── Trusted by: Security team, HR                                    │
│     │   └── Distrusted by: Engineering team (they fear investigation)       │
│     │                                                                        │
│     ├── User B (Journalist):                                                 │
│     │   ├── Can access: Public records, social media                         │
│     │   ├── Trusted by: Disgruntled employees, whistleblowers               │
│     │   └── Distrusted by: Management (fear of bad press)                   │
│     │                                                                        │
│     └── Same Town, different affordances                                     │
│                                                                              │
│  4. CONVERGENCE MOMENT                                                       │
│     ├── At some point, both users discover overlapping information          │
│     ├── System notification: "Your paths may cross soon..."                 │
│     ├── Option to: [Meet in scenario] [Stay separate]                       │
│     └── If they meet: Both control their characters in same scene           │
│                                                                              │
│  5. COLLABORATIVE ENDING                                                     │
│     ├── Outcome depends on what both discovered                              │
│     ├── Shared debrief with K-gent                                           │
│     └── "Together you uncovered 87% of the story"                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Interaction Micropatterns

### Consent Debt Meter

```
The consent debt meter is always visible during INHABIT:

┌─────────────────────────────────────────────────────────────┐
│ CONSENT BALANCE                                              │
│                                                              │
│ Overall:  ████████░░░░░░░░░░░░ 40%   ⚠️ Low                 │
│                                                              │
│ By Citizen:                                                  │
│ Sarah:    ██░░░░░░░░ 20%  [Forced once, resistant]          │
│ Tom:      ██████████ 100% [Fully engaged]                   │
│ Paula:    ██████░░░░ 60%  [Cautious]                        │
│ Sam:      ████████░░ 80%  [Supportive]                      │
│ Quinn:    ████░░░░░░ 40%  [Unaddressed concerns]            │
│                                                              │
│ Forces remaining: 2/3                                        │
└─────────────────────────────────────────────────────────────┘
```

### Dialogue Mask Application

```
User selects mask during scenario setup:

┌─────────────────────────────────────────────────────────────┐
│ DIALOGUE MASKS                    (Optional challenge mode)  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Wear a mask to transform your approach:                     │
│                                                              │
│ 🎭 THE TRICKSTER                                             │
│    +30% creativity, -20% trust                              │
│    "Challenge conventions, expect resistance"               │
│                                                              │
│ 🌙 THE DREAMER                                               │
│    +25% vision, -15% practicality                           │
│    "Paint futures, ground them later"                       │
│                                                              │
│ 🔬 THE SKEPTIC                                               │
│    +35% analytical, -25% warmth                             │
│    "Question everything, alienate some"                     │
│                                                              │
│ [Select mask] [No mask (authentic)]                         │
└─────────────────────────────────────────────────────────────┘
```

---

## References

- Master plan: `plans/core-apps-synthesis.md` §2.4
- Original idea: `brainstorming/2025-12-15-project-proposals.md`
- INHABIT tests: `impl/claude/agents/town/_tests/test_inhabit*.py`
- Kent's wish: "Westworld-like simulation park" (`plans/_focus.md`)

### UX Research Sources

- [Punchdrunk Handbook](https://worldxo.org/punchdrunk-handbook-immersive-pioneers-share-20-years-of-learnings/) — 20 years of immersive theater learnings
- [Sleep No More MIT Project](https://www.media.mit.edu/projects/remote-theatrical-immersion-extending-sleep-no-more/overview/) — Digital extension research
- [AI Dungeon Review 2025](https://www.aiapps.com/blog/ai-dungeon-review-2025-interactive-storytelling-with-artificial-intelligence/) — Interactive storytelling patterns
- [AI Roleplay Guide 2025](https://aimojo.io/rise-of-ai-roleplay/) — Character interaction and consent ethics
- [Voices of VR: Sleep No More](https://voicesofvr.com/611-sleep-no-more-creative-producer-on-blurring-the-lines-of-reality-with-punchdrunks-immersive-theater/) — Blurring reality in immersive design

---

*Last updated: 2025-12-15*
