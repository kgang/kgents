---
path: docs/skills/user-flow-documentation
status: active
progress: 1.0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/core-apps-synthesis
session_notes: |
  Extracted from UX documentation work on core-apps plans.
  Provides templates and patterns for documenting user journeys.
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

# Skill: User Flow Documentation

> Document precise user flows with ASCII wireframes for implementation grounding.

**Difficulty**: Medium
**Prerequisites**: Understanding of the feature being documented
**Use Cases**: Plan files, spec files, design documents

---

## Overview

User flow documentation captures the complete interaction sequence between a user and system. Well-documented flows enable:

1. **Implementation grounding**: Developers know exactly what to build
2. **UX consistency**: Patterns carry across features
3. **Review efficiency**: Stakeholders can evaluate before code
4. **Test derivation**: Flows become acceptance test scripts

---

## Flow Documentation Structure

### 1. Flow Header

```markdown
### Flow N: Descriptive Name ("The Evocative Subtitle")
```

**Components**:
- **Flow number**: Sequential within document
- **Descriptive name**: What happens (e.g., "First Task")
- **Evocative subtitle**: The emotional/experiential core (e.g., "The Quick Win")

**Examples**:
```markdown
### Flow 1: First-Time Spectator ("The Curious Visitor")
### Flow 2: First-Time Builder ("The Hesitant Creator")
### Flow 3: Consent Negotiation ("The Refusal Moment")
### Flow 4: Morning Start ("The Dawn Protocol")
```

---

### 2. Context Block

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: What triggers this flow                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ OR                                                                           │
│ CONTEXT: What situation the user is in                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Use ENTRY for**: User-initiated flows (clicking, typing, navigating)
**Use CONTEXT for**: System-initiated or situational flows

---

### 3. Step Blocks

Each step follows this pattern:

```
│  N. STEP NAME (timing if relevant)                                           │
│     ├── Action or observation                                                │
│     ├── Another action                                                       │
│     │   └── Sub-detail if needed                                             │
│     └── Final action in step                                                 │
```

**Timing annotations**:
- `(0-10 seconds)` — User time in step
- `(T+15 minutes)` — Elapsed time from start
- `(background, 5-30 seconds)` — Async operation

---

### 4. Wireframe Blocks

ASCII wireframes show exact UI state:

```
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  TITLE BAR                              [Action] [Action2]  │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  Content area with description                              │     │
│     │   │                                                             │     │
│     │   │  • Bullet point                                             │     │
│     │   │  • Another point                                            │     │
│     │   │                                                             │     │
│     │   │  [Primary Button] [Secondary Button]                        │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
```

**Wireframe conventions**:
- `[Text]` — Clickable buttons/actions
- `│ ├── └──` — Tree structure for hierarchy
- `───────` — Horizontal dividers
- `█████░░░░░` — Progress bars (filled/empty)
- `> _` — Input cursor/prompt

---

### 5. Decision Points

Show branching with explicit labels:

```
│  3a. IF USER CHOOSES [Option A]                                              │
│     ├── What happens                                                         │
│     └── Outcome                                                              │
│                                                                              │
│  3b. IF USER CHOOSES [Option B]                                              │
│     ├── Different path                                                       │
│     └── Different outcome                                                    │
│                                                                              │
│  3c. IF USER CHOOSES [Option C]                                              │
│     ├── Third path                                                           │
│     └── Third outcome                                                        │
```

---

## Complete Flow Template

```markdown
### Flow N: Name ("Subtitle")

\`\`\`
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: Trigger description                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. FIRST STEP (timing)                                                      │
│     ├── First action                                                         │
│     ├── Second action                                                        │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  UI STATE                                                   │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  Content                                                    │     │
│     │   │                                                             │     │
│     │   │  [Action] [Action]                                          │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Closing observation                                                  │
│                                                                              │
│  2. SECOND STEP (timing)                                                     │
│     ├── Action                                                               │
│     └── Outcome                                                              │
│                                                                              │
│  3. DECISION POINT                                                           │
│     ├── User makes choice                                                    │
│                                                                              │
│  3a. IF [Choice A]                                                           │
│     ├── Path A actions                                                       │
│     └── Path A outcome                                                       │
│                                                                              │
│  3b. IF [Choice B]                                                           │
│     ├── Path B actions                                                       │
│     └── Path B outcome                                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
\`\`\`
```

---

## Interaction Micropatterns

For reusable UI components, document as micropatterns:

```markdown
### Pattern Name

\`\`\`
Description of when this pattern is used:

┌─────────────────────────────────────────────────────────────┐
│ COMPONENT TITLE                                              │
│                                                              │
│ Element 1:    ████████░░░░░░░░░░░░ 40%                      │
│ Element 2:    ██████████████░░░░░░ 70%                      │
│                                                              │
│ [Action] [Action] [Action]                                   │
└─────────────────────────────────────────────────────────────┘
\`\`\`
```

---

## Visual Vocabulary

### Progress Indicators

```
Empty:     ░░░░░░░░░░░░░░░░░░░░
Partial:   ████████░░░░░░░░░░░░ 40%
Full:      ████████████████████ 100%
Warning:   ██████░░░░░░░░░░░░░░ 30% ⚠️
```

### State Icons

```
Success:   ✅ ✓
Warning:   ⚠️
Error:     ✗ ❌
Info:      ℹ️ 💡
Active:    🟢 ████
Idle:      🟡 ░░░░
Thinking:  ∿∿∿∿
Loading:   🔄
```

### Arrows and Flow

```
Single:    →  ←  ↑  ↓
Double:    ⇒  ⇐  ⇑  ⇓
With data: ──⚡──►  (message with latency)
Branch:    ┬  ├  └
```

### Box Drawing

```
Corners:   ┌  ┐  └  ┘
Lines:     ─  │
Junctions: ┬  ┴  ├  ┤  ┼
```

---

## Flow Categories

### Entry Flows ("The First Time")
- **Purpose**: Onboarding, discovery
- **Key elements**: Minimal friction, immediate value, gradual reveal
- **Naming convention**: "First-Time [Role]", "The [Emotion] [Moment]"

### Core Loops ("The Daily")
- **Purpose**: Primary repeated action
- **Key elements**: Efficiency, keyboard shortcuts, muscle memory
- **Naming convention**: "[Action] Flow", "The [Ritual]"

### Edge Cases ("The Exception")
- **Purpose**: Error recovery, unusual situations
- **Key elements**: Clear guidance, recovery path, no dead ends
- **Naming convention**: "[Situation] Handling", "The [Challenge]"

### Advanced Flows ("The Power Move")
- **Purpose**: Expert features, customization
- **Key elements**: Depth without complexity, progressive disclosure
- **Naming convention**: "Custom [Feature]", "Advanced [Action]"

---

## Quality Checklist

Before finalizing a flow:

- [ ] **Entry is clear**: User knows how they got here
- [ ] **Steps are numbered**: Easy to reference in reviews
- [ ] **Timing is indicated**: Developers know expected latency
- [ ] **UI states are shown**: Visual at each major moment
- [ ] **Branches are explicit**: All paths documented
- [ ] **Outcomes are stated**: User knows what happened
- [ ] **Error cases exist**: What if something fails?
- [ ] **Feedback is visible**: User knows system received input

---

## Example: Complete Flow

```
### Flow 1: First Bid ("The Moment of Influence")

┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: Spectator has accumulated 3 WatchTokens                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. BID BUTTON ACTIVATES (passive, 0 seconds)                                │
│     ├── Token balance visible: "3 WatchTokens"                               │
│     ├── [Bid] button transitions from gray to colored                        │
│     └── Subtle pulse animation draws attention                               │
│                                                                              │
│  2. USER CLICKS BID (0-2 seconds)                                            │
│     ├── Constraint picker modal appears:                                     │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  What should [Builder] try?                                 │     │
│     │   ├─────────────────────────────────────────────────────────────┤     │
│     │   │                                                             │     │
│     │   │  💭 Suggest direction    (1 token)                          │     │
│     │   │  🎨 Suggest color        (1 token)                          │     │
│     │   │  🔥 Challenge            (5 tokens)  [disabled - need 5]    │     │
│     │   │  ⚡ Boost current        (2 tokens)                          │     │
│     │   │                                                             │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── Options costed > balance are disabled with tooltip                   │
│                                                                              │
│  3. USER SELECTS OPTION (2-10 seconds)                                       │
│     ├── User taps "Suggest color" (1 token)                                  │
│     ├── Color picker appears:                                                │
│     │                                                                        │
│     │   ┌─────────────────────────────────────────────────────────────┐     │
│     │   │  Pick a color to suggest:                                   │     │
│     │   │                                                             │     │
│     │   │  [🔴] [🟠] [🟡] [🟢] [🔵] [🟣] [⚫] [⚪]                     │     │
│     │   │                                                             │     │
│     │   │  Or type: [____________]                                    │     │
│     │   │                                                             │     │
│     │   │  [Cancel] [Send Suggestion]                                 │     │
│     │   └─────────────────────────────────────────────────────────────┘     │
│     │                                                                        │
│     └── User selects blue                                                    │
│                                                                              │
│  4. BID SUBMITTED (0-1 second)                                               │
│     ├── Modal closes                                                         │
│     ├── Token balance updates: "3 → 2 WatchTokens"                          │
│     ├── Toast: "Suggestion sent! 💙"                                        │
│     └── Bid appears in Builder's stream with animation                       │
│                                                                              │
│  5. BUILDER RESPONDS (5-60 seconds, async)                                   │
│     ├── Builder sees notification in their UI                                │
│                                                                              │
│  5a. IF BUILDER ACCEPTS                                                      │
│     ├── Spectator receives notification: "Accepted! 🎉"                     │
│     ├── Token refund: "+1.5 tokens (50% bonus)"                             │
│     └── Reputation increment for spectator                                   │
│                                                                              │
│  5b. IF BUILDER ACKNOWLEDGES (but doesn't commit)                            │
│     ├── Spectator sees: "Thanks! I'll consider it"                          │
│     └── Token refund: "+0.5 tokens (partial)"                               │
│                                                                              │
│  5c. IF BUILDER IGNORES (timeout after 60s)                                  │
│     ├── Bid fades from spectator's view                                      │
│     └── No refund, no notification                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Skills

- [ux-reference-patterns](ux-reference-patterns.md) — Cross-cutting UX patterns
- [plan-file](plan-file.md) — Forest Protocol plan file conventions
- [handler-patterns](handler-patterns.md) — CLI handler implementation

---

## Changelog

- 2025-12-15: Initial skill based on core-apps documentation work
