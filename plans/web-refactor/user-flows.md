---
path: plans/web-refactor/user-flows
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables: [web-refactor/polish-and-delight]
parent: plans/web-refactor/webapp-refactor-master
requires: [web-refactor/elastic-primitives, web-refactor/interaction-patterns]
session_notes: |
  Four core flows: create, chat, details, orchestrate.
  Each completable in ≤3 clicks. Consumer to professional UX.
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
entropy:
  planned: 0.08
  spent: 0.0
  returned: 0.0
---

# User Flows

> *"Shockingly delightful consumer, prosumer, and professional experience."*

## The Four Core Flows

| Flow | Consumer Need | Prosumer Need | Professional Need |
|------|---------------|---------------|-------------------|
| **Create** | Quick agent from template | Customize archetype | Full parameter control |
| **Chat** | Natural conversation | Access to agent internals | Multi-agent dialogue |
| **Details** | At-a-glance status | Deep metrics | Full state inspection |
| **Orchestrate** | Watch simulation | Build simple pipelines | Complex composition |

---

## Flow 1: Create Agent

### Current State
- API-only creation
- No visual interface

### Target Experience

**Consumer**: "I want an explorer agent"
1. Click "New Agent" → Opens creation modal
2. Select archetype from visual palette (Scout, Sage, Spark, Steady, Sync)
3. Name agent → Done

**Prosumer**: "I want a cautious explorer"
1. Click "New Agent" → Opens creation modal
2. Select archetype → Shows customization panel
3. Adjust eigenvector sliders (warmth, curiosity, trust)
4. Review preview → Create

**Professional**: "I want a specific polynomial configuration"
1. Click "New Agent" → Opens creation modal
2. Toggle "Advanced Mode"
3. Edit JSON/YAML directly or use form fields
4. Validate against polynomial schema
5. Create

### Components

```typescript
interface AgentCreationWizardProps {
  mode: 'simple' | 'custom' | 'advanced';
  onModeChange: (mode: 'simple' | 'custom' | 'advanced') => void;
  onComplete: (config: AgentConfig) => void;
  onCancel: () => void;
}

// Step components
function ArchetypePalette({ selected, onSelect }: {...}) { ... }
function EigenvectorSliders({ values, onChange }: {...}) { ... }
function AgentPreview({ config }: {...}) { ... }
function AdvancedEditor({ config, onChange, errors }: {...}) { ... }
```

### Archetype Palette

Visual cards with personality:

| Archetype | Emoji | Description | Eigenvector Bias |
|-----------|-------|-------------|------------------|
| **Scout** | 🔍 | Curious explorer, finds opportunities | High curiosity |
| **Sage** | 🧙 | Thoughtful planner, designs solutions | High trust |
| **Spark** | ✨ | Creative builder, rapid prototyping | High warmth |
| **Steady** | ⚓ | Reliable refiner, quality focus | Balanced |
| **Sync** | 🔗 | Integrator, connects systems | High trust |

---

## Flow 2: Chat with Agent

### Current State
- INHABIT mode exists but requires navigation
- Full-page takeover

### Target Experience

**Consumer**: "I want to talk to this agent"
1. Click agent → Details panel opens
2. Click "Chat" button → Chat drawer slides in
3. Type message → Get response

**Prosumer**: "I want to see the agent's thinking"
1. Open chat drawer
2. Toggle "Show Inner Voice"
3. See agent's internal monologue alongside responses

**Professional**: "I want multi-agent dialogue"
1. Open chat drawer
2. Click "Add Participant" → Select another agent
3. Facilitate dialogue between agents
4. Inject own messages as moderator

### Components

```typescript
interface ChatDrawerProps {
  agent: CitizenCardJSON;
  mode: 'simple' | 'detailed' | 'multi-agent';
  participants: CitizenCardJSON[];
  onAddParticipant: () => void;
  onRemoveParticipant: (id: string) => void;
  onSendMessage: (message: string, to?: string) => void;
  onClose: () => void;
}

interface ChatMessageProps {
  message: {
    id: string;
    from: string;
    content: string;
    timestamp: Date;
    innerVoice?: string;
    alignment?: number;
  };
  showInnerVoice: boolean;
}
```

### Chat Drawer Layout

```
┌──────────────────────────────────┐
│ 🎭 Chat with Scout          [X] │
├──────────────────────────────────┤
│ ┌─────────────────────────────┐  │
│ │ Scout: Hello! What shall we │  │
│ │ explore today?              │  │
│ │ [Inner: Eager to help]      │  │
│ └─────────────────────────────┘  │
│                                  │
│ ┌─────────────────────────────┐  │
│ │ You: Let's look at the      │  │
│ │ market trends.              │  │
│ └─────────────────────────────┘  │
│                                  │
│ ┌─────────────────────────────┐  │
│ │ Scout: Great idea! I notice │  │
│ │ activity near the plaza...  │  │
│ │ [Inner: This aligns well]   │  │
│ └─────────────────────────────┘  │
├──────────────────────────────────┤
│ [Type a message...]      [Send] │
│ [ ] Show Inner Voice   [INHABIT]│
└──────────────────────────────────┘
```

---

## Flow 3: View Agent Details

### Current State
- CitizenPanel in sidebar
- Limited information

### Target Experience

**Consumer**: "I want to see what this agent is doing"
1. Click agent → Card expands in place OR sidebar opens
2. See phase, activity sparkline, current mood

**Prosumer**: "I want to see metrics over time"
1. Click agent → Details panel
2. Click "Metrics" tab
3. See charts: activity history, eigenvector drift, relationship graph

**Professional**: "I want full state inspection"
1. Click agent → Details panel
2. Click "State" tab
3. See full polynomial state, memory contents, trace history
4. Export state as JSON

### Components

```typescript
interface AgentDetailsProps {
  agent: CitizenCardJSON;
  mode: 'compact' | 'expanded' | 'full';
  onModeChange: (mode: 'compact' | 'expanded' | 'full') => void;
  onClose: () => void;
}

// Tab components
function OverviewTab({ agent }: {...}) { ... }
function MetricsTab({ agent, timeRange }: {...}) { ... }
function RelationshipsTab({ agent, citizens }: {...}) { ... }
function StateTab({ agent, onExport }: {...}) { ... }
function HistoryTab({ agent, events }: {...}) { ... }
```

### Detail Levels

**Compact** (hover card):
```
┌────────────────────┐
│ 🔍 Scout           │
│ EXPLORING • 🟢     │
│ ▁▃▅▇▅▃ activity    │
└────────────────────┘
```

**Expanded** (sidebar):
```
┌──────────────────────────┐
│ 🔍 Scout          [chat] │
├──────────────────────────┤
│ Phase: EXPLORING         │
│ Mood: Curious            │
│ Region: Plaza            │
│                          │
│ ╭──────────────────────╮ │
│ │ ▁▃▅▇▅▃▂▁▃▅ Activity  │ │
│ ╰──────────────────────╯ │
│                          │
│ Eigenvectors:            │
│ Warmth:   ██████░░ 75%   │
│ Curiosity:████████ 95%   │
│ Trust:    █████░░░ 60%   │
├──────────────────────────┤
│ [Overview][Metrics][...] │
└──────────────────────────┘
```

**Full** (modal):
- All tabs available
- Full-width charts
- JSON state viewer
- Trace timeline

---

## Flow 4: Orchestrate Agents

### Current State
- Watch Town simulation
- Workshop for guided tasks

### Target Experience

**Consumer**: "I want to watch agents work together"
1. Click "Play" → Simulation runs
2. Watch agents interact on mesa
3. See events in feed

**Prosumer**: "I want to direct the simulation"
1. Open pipeline canvas
2. Drag agents into sequence
3. Click "Run" → Watch execution
4. Adjust and iterate

**Professional**: "I want complex multi-phase orchestration"
1. Open pipeline canvas (full-screen)
2. Build multi-branch pipeline
3. Add conditions and loops
4. Save pipeline as reusable template
5. Execute with monitoring

### Components

```typescript
interface OrchestrationCanvasProps {
  mode: 'watch' | 'build' | 'execute';
  pipeline?: Pipeline;
  onPipelineChange: (pipeline: Pipeline) => void;
  onExecute: () => void;
  onSave: (name: string) => void;
  onLoadTemplate: (id: string) => void;
}

interface ExecutionMonitorProps {
  pipeline: Pipeline;
  execution: {
    status: 'idle' | 'running' | 'complete' | 'error';
    currentNodeId: string | null;
    results: Map<string, unknown>;
    errors: Map<string, Error>;
  };
}
```

### Pipeline Templates

Pre-built pipelines for common patterns:

| Template | Description | Nodes |
|----------|-------------|-------|
| **Exploration** | Find then analyze | Scout >> Sage |
| **Build** | Design then implement | Sage >> Spark >> Steady |
| **Full Cycle** | Complete workshop flow | Scout >> Sage >> Spark >> Steady >> Sync |
| **Parallel Research** | Multiple explorers | Scout // Scout >> Sage |

---

## Navigation Architecture

### Route Structure

```
/                    → Landing
/town/demo           → Create demo town
/town/:id            → Town view (observe mode)
/town/:id/build      → Town view (build mode)
/town/:id/history    → Town view (historical mode)
/town/:id/inhabit/:citizenId → INHABIT mode
/workshop            → Workshop view
/workshop/pipeline/:id → Pipeline editor
/dashboard           → User dashboard
```

### Global Navigation

Always visible:
- Logo (→ home)
- Town switcher (if multiple)
- Mode indicator (observe/build/history)
- User menu

Context-sensitive:
- Back to town (from INHABIT)
- Save pipeline (in build mode)
- Exit history (in historical mode)

---

## Responsive Behavior

### Breakpoints

| Breakpoint | Layout | Panels |
|------------|--------|--------|
| <640px (mobile) | Stacked | Full-screen modals |
| 640-1024px (tablet) | Hybrid | Collapsible sidebar |
| >1024px (desktop) | Multi-column | Persistent sidebar |

### Mobile-Specific Flows

1. **Create**: Full-screen wizard
2. **Chat**: Full-screen drawer from bottom
3. **Details**: Bottom sheet, swipe up for full
4. **Orchestrate**: Simplified, no pipeline canvas (watch only)

---

## Implementation Tasks

### Phase 1: Create Flow
- [ ] Design AgentCreationWizard
- [ ] Implement ArchetypePalette
- [ ] Implement EigenvectorSliders
- [ ] Implement AgentPreview
- [ ] Implement AdvancedEditor
- [ ] Wire to API

### Phase 2: Chat Flow
- [ ] Design ChatDrawer component
- [ ] Implement ChatMessage component
- [ ] Implement multi-agent mode
- [ ] Add inner voice toggle
- [ ] Connect to existing INHABIT API

### Phase 3: Details Flow
- [ ] Design AgentDetails component
- [ ] Implement Overview tab
- [ ] Implement Metrics tab
- [ ] Implement Relationships tab
- [ ] Implement State tab
- [ ] Add export functionality

### Phase 4: Orchestrate Flow
- [ ] Design OrchestrationCanvas
- [ ] Implement ExecutionMonitor
- [ ] Create pipeline templates
- [ ] Add save/load functionality

---

## Success Metrics

1. **3-Click Test**: All flows completable in ≤3 primary actions
2. **Time to Create**: <30s for consumer, <2min for prosumer
3. **Chat Engagement**: >60% of users try chat within first session
4. **Pipeline Completion**: >40% of prosumers build a custom pipeline
5. **Mobile Usability**: 100% core flows work on mobile

---

*"Shockingly delightful" means the UI anticipates needs before they're expressed.*
