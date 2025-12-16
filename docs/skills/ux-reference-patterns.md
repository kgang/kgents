---
path: docs/skills/ux-reference-patterns
status: active
progress: 1.0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/core-apps-synthesis
session_notes: |
  Extracted from UX research across all 7 Crown Jewel apps.
  Sources: Twitch, Figma, Zapier, Make, Obsidian, InfraNodus, Punchdrunk, AI Dungeon, etc.
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: complete
  CROSS-SYNERGIZE: complete
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: complete
  MEASURE: deferred
  REFLECT: complete
entropy:
  planned: 0.05
  spent: 0.05
  returned: 0.10
---

# Skill: UX Reference Patterns

> Cross-cutting UX patterns extracted from successful products, applicable to any kgents app.

**Difficulty**: Easy (reading), Medium (application)
**Prerequisites**: None
**Use Cases**: Designing new features, reviewing UX decisions, planning user flows

---

## Overview

This skill documents proven UX patterns from successful products, organized by concern. Each pattern is abstracted from specific implementations (Twitch, Figma, Obsidian, etc.) into reusable principles.

---

## 1. Spectator Economy Patterns

*Source: Twitch, Figma, YouTube*

### 1.1 Dual-Currency Systems

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Earned currency** | Watching time → passive tokens | Low barrier, rewards engagement |
| **Purchased currency** | Real money → premium actions | Monetization without gates |
| **Conversion ratio** | Never 1:1 between currencies | Prevents arbitrage, preserves value |

**kgents Application**: WatchTokens (passive) + InfluenceTokens (paid) in Atelier.

### 1.2 Collective Momentum

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Visible meter** | Energy bar fills with participation | Social proof drives action |
| **Unlock thresholds** | "1000 tokens unlock secret theme" | Gamification without competition |
| **Decay without activity** | Momentum drops if idle | Creates urgency |

**kgents Application**: MomentumMeter in Atelier's Festival Mode.

### 1.3 Spectator Influence Gradations

```
Minimal ────────────────────────────────────────────── Maximal
   │                                                      │
   Reactions          Suggestions         Bids         Force
   (free)             (1 token)           (5 tokens)   (expensive)
```

**Principle**: Cheap actions are plentiful; expensive actions are impactful.

---

## 2. Multiplayer Collaboration Patterns

*Source: Figma, Miro, Google Docs*

### 2.1 Cursor Awareness

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Visible cursors** | See where others are focused | Reduces collision, enables following |
| **Name labels** | "Maya is viewing..." | Social presence without chat |
| **Activity trails** | Fade paths showing recent movement | Shows intention |

**kgents Application**: SpectatorCursors in Atelier.

### 2.2 Real-Time Sync

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **No save button** | All changes auto-persist | Removes friction |
| **Conflict resolution** | Last-write-wins or CRDT | Predictable behavior |
| **Optimistic updates** | Show immediately, sync later | Feels instantaneous |

**Anti-pattern**: Requiring explicit "save" for collaborative content.

### 2.3 Comment-in-Context

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Anchored comments** | Comments attached to specific elements | Clear reference |
| **Thread collapse** | Resolve/collapse resolved threads | Reduces noise |
| **@mentions** | Notify specific collaborators | Directed attention |

---

## 3. No-Code Builder Patterns

*Source: Zapier, Make, Notion, Airtable*

### 3.1 Natural Language to Structure

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Describe → Generate** | "I want to..." → AI suggests structure | Eliminates blank page |
| **Show confidence** | "92% match to Research pattern" | Transparency builds trust |
| **Easy override** | One-click to modify suggestions | Maintains control |

**kgents Application**: Coalition Forge's "describe your task" flow.

### 3.2 Visual Flow Builders

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Node-based canvas** | Drag components, draw connections | Spatial reasoning |
| **Live preview** | See output as you build | Immediate feedback |
| **Dry run mode** | Test without execution | Safe experimentation |

**kgents Application**: Coalition topology view.

### 3.3 Template Libraries

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Curated starter templates** | "Competitive Research" template | Reduces cognitive load |
| **Community templates** | User-created, shareable | Network effects |
| **Clone-and-customize** | Start from existing, modify | Incremental learning |

---

## 4. Knowledge Graph Patterns

*Source: Obsidian, Notion, Roam Research, InfraNodus*

### 4.1 Semantic Zoom

| Level | Shows | Use Case |
|-------|-------|----------|
| **System** | All nodes, no detail | Orientation |
| **Container** | Major components | Navigation |
| **Component** | Internal structure | Exploration |
| **Code** | Implementation detail | Work |

**Principle**: Zoom = semantic depth, not just visual scale.

### 4.2 Decay Visualization

| State | Visual Treatment | Behavior |
|-------|------------------|----------|
| **Fresh** (< 1 week) | Full opacity, glow | Prominent |
| **Recent** (1-4 weeks) | 85% opacity | Normal |
| **Aging** (1-3 months) | 60% opacity, shrinking | Dimming |
| **Fading** (3+ months) | 30% opacity, ghost outline | Nearly gone |

**kgents Application**: Crystal decay in Holographic Brain.

### 4.3 Gap Detection

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Sparse region highlight** | Visual gap in topology | Shows what's missing |
| **Suggestion generation** | "You know X but lack Y foundation" | Actionable insight |
| **Proactive surfacing** | Ghost notifications | Prevents total loss |

---

## 5. Immersive Simulation Patterns

*Source: Punchdrunk (Sleep No More), AI Dungeon, Character.AI*

### 5.1 Observer → Participant Transition

| Phase | User State | System Affordances |
|-------|------------|-------------------|
| **Observer** | Masked, watching | Follow, react, no direct interaction |
| **Threshold** | Choosing to engage | Explicit consent moment |
| **Participant** | Unmasked, acting | Full interaction, consequences |

**kgents Application**: INHABIT mode in Punchdrunk Park.

### 5.2 Consent Mechanics

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Continuous consent [0,1]** | Debt meter, not binary | Nuanced relationships |
| **Refusal as feature** | Citizens can say no | Agency, not puppetry |
| **Expensive force** | 3x cost, limited uses | Meaningful choice |
| **Logged actions** | Audit trail | Accountability |

**Principle**: "Collaboration > control; refusal is core feature, not bug."

### 5.3 Memory Persistence

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Cross-session memory** | NPCs remember previous encounters | Continuity |
| **Eigenvector evolution** | Traits change based on interaction | Consequence |
| **Relationship tracking** | History of interactions per citizen | Depth |

---

## 6. Crisis Simulation Patterns

*Source: Immersive Labs, MIT Sloan, Conducttr*

### 6.1 Time Pressure

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Visible countdown** | "71:45:00 until GDPR deadline" | Creates stakes |
| **Escalation triggers** | Situation worsens if ignored | Consequence |
| **Real-time adaptability** | Injects change scenario mid-exercise | No playbook |

**kgents Application**: Domain Simulation drills.

### 6.2 Role-Based Views

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Information asymmetry** | Each role sees different data | Realistic constraint |
| **Handoff protocols** | Explicit transition between roles | Clear responsibility |
| **Facilitator override** | Admin can see/control everything | Safety valve |

### 6.3 Post-Exercise Analytics

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Timeline reconstruction** | "00:07 — Bob notified (4 min delay)" | Objective review |
| **Metric comparison** | "Target: 2 min, Actual: 4 min" | Gap identification |
| **Actionable recommendations** | "Next time: escalate faster" | Learning closure |

---

## 7. Architecture Visualization Patterns

*Source: Structurizr, C4 Model, CodeSee*

### 7.1 C4-Like Hierarchy

| Level | kgents Equivalent |
|-------|-------------------|
| System Context | TownView — all agents, external interfaces |
| Container | AgentView — individual agent architecture |
| Component | ProtocolView — AGENTESE contexts and nodes |
| Code | NodeView — affordances and handlers |

### 7.2 Live Diagramming

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Auto-generation** | Diagrams from running code | Always current |
| **Bidirectional sync** | Edit diagram ↔ edit code | Single source |
| **Change highlighting** | Show additions/removals since last version | Diff awareness |

### 7.3 Governance Dashboards

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Health scores** | Coupling, cohesion, drift metrics | Quick assessment |
| **Drift alerts** | "Undeclared dependency detected" | Proactive enforcement |
| **Actionable triage** | [Declare] [Suppress] [View Code] | One-click resolution |

---

## 8. CLI/Terminal Patterns

*Source: GitHub Copilot CLI, Warp, Fig/Amazon Q*

### 8.1 Natural Language Routing

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Describe → Command** | "what's the weather" → route | No syntax to learn |
| **Confidence display** | "Routing to world.weather.manifest" | Transparency |
| **Easy correction** | "No, I meant..." → retry | Forgiving |

**kgents Application**: The Gardener's natural language input.

### 8.2 Context-Aware Completion

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **History-aware** | Suggest from recent commands | Learns your patterns |
| **State-aware** | Suggest based on current phase | Relevant to moment |
| **Inline descriptions** | Show what each option does | Reduces lookup |

### 8.3 Session Persistence

| Pattern | Implementation | Why It Works |
|---------|----------------|--------------|
| **Named sessions** | "coalition-forge-api-2025-12-15" | Findable |
| **Resume anywhere** | `kg /continue` | Cross-terminal |
| **Checkpoint indicators** | Visual progress bar | Know where you are |

---

## Application Checklist

When designing a new feature, check against these patterns:

- [ ] **Spectator economy**: Does it have free/paid action tiers?
- [ ] **Collaboration**: Can multiple users work together?
- [ ] **No-code entry**: Can users start with natural language?
- [ ] **Semantic zoom**: Does detail increase with focus?
- [ ] **Consent mechanics**: Do agents have meaningful agency?
- [ ] **Time pressure**: Is there appropriate urgency?
- [ ] **Role-based views**: Do different users see different things?
- [ ] **Live sync**: Is state always current?
- [ ] **Post-action analytics**: Can users learn from what happened?
- [ ] **Session persistence**: Can work span multiple sessions?

---

## Related Skills

- [user-flow-documentation](user-flow-documentation.md) — How to document user flows
- [agent-town-inhabit](agent-town-inhabit.md) — INHABIT consent mechanics
- [reactive-primitives](reactive-primitives.md) — Signal/Computed for live sync

---

## Changelog

- 2025-12-15: Initial extraction from core-apps UX research
