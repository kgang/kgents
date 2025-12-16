---
path: plans/core-apps/atelier-experience
status: active
progress: 0
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - monetization/token-economy
  - plans/festivals-framework
session_notes: |
  Stub plan created from core-apps-synthesis.
  Extends existing Tiny Atelier (128 tests) to full platform.
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
  planned: 0.10
  spent: 0.0
  returned: 0.0
---

# Atelier Experience Platform

> *"Live creation mode where builders work in a fishbowl visible to spectators."*

**Master Plan**: `plans/core-apps-synthesis.md` (Section 2.1)
**Existing Infrastructure**: `agents/atelier/` (128 tests, streaming-first)

---

## Overview

| Aspect | Detail |
|--------|--------|
| **Frame** | Creative workshop with spectator economy |
| **Core Mechanic** | Builders stream creation; spectators bid on directions |
| **Revenue** | Token economy (attention → tokens → influence) |
| **Status** | 128 tests, streaming-first architecture complete |

---

## What This Plan Covers

### Absorbs These Original Ideas

| Idea | Source | Integration |
|------|--------|-------------|
| The Atelier | `art-creativity-ideas.md` | Core concept |
| Exquisite Cadaver | `art-creativity-ideas.md` | Visibility mode |
| Memory Theatre | `art-creativity-ideas.md` | Performance mode |
| Dreaming Garden | `art-creativity-ideas.md` | Persistence layer |
| Builder Workshop Runtime | `money-maximizing-ideas.md` | Live component generation |
| LiveOps Festivals | `money-maximizing-ideas.md` | Seasonal events |

---

## Experience Modes

| Mode | Description | Implementation Status |
|------|-------------|----------------------|
| **Open Studio** | Builders create, spectators watch | Pending |
| **Exquisite Mode** | Constrained visibility handoffs | Pending |
| **Memory Mode** | Citizens perform crystallized memories | Pending |
| **Garden Mode** | Artifacts grow as persistent flora | Pending |
| **Masked Mode** | Builders wear persona masks | Pending |
| **Festival Mode** | Timed seasonal events | Pending |

---

## Technical Foundation

```python
# Already built
from agents.atelier import (
    AtelierSession,      # Live creation session
    StreamingArtisan,    # Builder with SSE output
    Gallery,             # Artifact display
    Exhibition,          # Curated collections
)

# To build
from agents.atelier import (
    SpectatorPool,       # Token economy
    BidQueue,            # Constraint injection
    VisibilityMask,      # Exquisite mode
    GardenPersistence,   # Dreaming Garden
    FestivalScheduler,   # LiveOps events
)
```

---

## Implementation Phases

### Phase 1: Spectator Economy (Q1 2025)

**Goal**: Enable spectators to influence creation through token economy

- [ ] Implement `TokenPool` for spectator economy
- [ ] Add token accrual based on watch time
- [ ] Create `BidQueue` for constraint injection
- [ ] Wire bids to Flux perturbation API
- [ ] Build spectator leaderboard widget
- [ ] Add tier-based token rates (FREE/PRO/ENTERPRISE)

**Success Criteria**: Spectators can spend tokens to inject constraints

### Phase 2: Experience Modes (Q2 2025)

**Goal**: Multiple creation paradigms

- [ ] Implement `VisibilityMask` for Exquisite Cadaver mode
- [ ] Create edge-extraction for handoff views
- [ ] Wire Memory Theatre to M-gent crystals
- [ ] Build performance rendering for memories
- [ ] Implement Garden persistence layer
- [ ] Add flora morphology based on artifact metadata

**Success Criteria**: All 5 modes functional

### Phase 3: Social Features (Q3 2025)

**Goal**: Community and discovery

- [ ] Coalition-based watching groups
- [ ] Builder subscription system
- [ ] Artifact marketplace (purchase/license)
- [ ] Social sharing and embedding
- [ ] Discovery algorithms

**Success Criteria**: Users can follow builders, buy artifacts

### Phase 4: Festivals (Q4 2025)

**Goal**: Seasonal revenue spikes

- [ ] Festival calendar framework
- [ ] Themed constraint packs
- [ ] Limited-time modes
- [ ] Sponsored stages
- [ ] Achievement system

**Success Criteria**: First festival generates 3x normal revenue

---

## Revenue Model

```python
TOKEN_RATES = {
    LicenseTier.FREE: 1.0,        # 1 token per minute watched
    LicenseTier.PRO: 2.5,         # 2.5x earning rate
    LicenseTier.ENTERPRISE: 5.0,  # 5x earning rate + bonus pool
}

SPECTATOR_COSTS = {
    "inject_constraint": 10,
    "request_direction": 5,
    "boost_builder": 3,
    "acquire_artifact": 50,
}
```

---

## Open Questions

1. **Token liquidity**: Can tokens be traded between users?
2. **Builder compensation**: How do builders earn from spectator tokens?
3. **Artifact ownership**: NFT-style ownership or usage rights?
4. **Moderation**: How to handle inappropriate constraints?
5. **Festival timing**: How often? Seasonal themes?
6. **Cross-platform**: Embed in other sites?

---

## Dependencies

| System | Usage |
|--------|-------|
| `agents/atelier/` | Core (already built) |
| `agents/town/workshop.py` | Builder archetypes |
| `agents/i/reactive/` | Widget composition |
| `protocols/billing/` | Token transactions |
| `agents/m/` | Memory Theatre integration |

---

## UX Research: Reference Flows

### Proven Patterns from Live Streaming Platforms

#### 1. Twitch Channel Points & Bits Economy
**Source**: [Twitch Platform Economy Research](https://www.tandfonline.com/doi/full/10.1080/1369118X.2024.2331766)

Twitch's dual-currency system provides the template for Atelier's spectator economy:

| Twitch Mechanic | Atelier Adaptation |
|-----------------|-------------------|
| **Channel Points** (non-monetary, earned by watching) | `WatchTokens` - accrue passively during streams |
| **Bits** (real-money, purchasable) | `InfluenceTokens` - paid currency for premium actions |
| **Hype Train** (collective momentum) | `MomentumMeter` - collective audience energy amplifies effects |
| **Predictions** (viewers bet on outcomes) | `DirectionBids` - spectators bid on creative paths |

**Key Insight**: Twitch's 2025 updates allow new creators to access monetization immediately. Atelier should follow: **no gates to participation**.

#### 2. Figma's Multiplayer Design UX
**Source**: [Figma Multiplayer Technology](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)

Figma's collaborative canvas offers critical patterns:

| Figma Pattern | Atelier Application |
|---------------|---------------------|
| **Cursor tracking** (see others' focus) | `SpectatorCursors` - optional view of where viewers are looking |
| **Comments in context** | `ContextualBids` - spectator inputs appear near relevant canvas areas |
| **Live edits, no save button** | `StreamingArtifact` - all creation is immediately visible |
| **Plugin ecosystem** | `ConstraintPacks` - community-created constraint bundles |

**Key Insight**: Figma's 40% faster design cycles come from eliminating friction. Atelier should feel like **no barrier between thought and creation**.

#### 3. Twitch 2025 Interactive Features
**Source**: [Twitch 2025 New Features](https://www.valueyournetwork.com/en/twitch-in-2025-new-features-will-change-everything/)

- **Reactions with Bits**: Viewers highlight moments → maps to `SpotlightAction`
- **Power-ups**: Custom interaction elements → maps to `CreatorConstraints`
- **Stream Together + shared chat**: Multi-builder modes → maps to `ExquisiteMode`

---

## Precise User Flows

### Flow 1: First-Time Spectator ("The Curious Visitor")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: User lands on Atelier homepage                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. DISCOVER (0-10 seconds)                                                  │
│     ├── Hero: Live creation stream auto-playing (muted)                      │
│     ├── Overlay: "Watch [Builder] create [Artifact] — 47 spectators"         │
│     └── CTA: [Enter Studio] [Browse Galleries]                               │
│                                                                              │
│  2. WATCH (10 seconds - 2 minutes)                                           │
│     ├── User clicks [Enter Studio]                                           │
│     ├── Full-screen stream view                                              │
│     ├── Sidebar: Live chat (collapsed by default)                            │
│     ├── Bottom bar: Token balance (starts at 0), [Bid] button grayed         │
│     └── After 30s: Toast "You've earned 1 WatchToken 🎉"                     │
│                                                                              │
│  3. ENGAGE (2-5 minutes)                                                     │
│     ├── Token balance visible: "3 WatchTokens"                               │
│     ├── [Bid] button activates                                               │
│     ├── User taps [Bid] → Constraint picker appears:                         │
│     │   ├── "Suggest a color" (1 token)                                      │
│     │   ├── "Suggest a direction" (3 tokens)                                 │
│     │   └── "Challenge the builder" (5 tokens)                               │
│     ├── User selects → Constraint injected into stream                       │
│     └── Builder acknowledges: "[Username] wants more blue 💙"                │
│                                                                              │
│  4. RETURN (exit → re-entry)                                                 │
│     ├── Session ends                                                         │
│     ├── Email/notification: "[Builder] finished! See the artifact"          │
│     ├── User returns → Gallery view of completed artifact                    │
│     └── CTA: [Follow Builder] [Acquire Artifact] [Watch Replay]              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: First-Time Builder ("The Hesitant Creator")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ENTRY: User clicks [Become a Builder]                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. ONBOARDING (0-60 seconds)                                                │
│     ├── Modal: "What do you create?"                                         │
│     │   ├── [ ] Code      [ ] Visual Art    [ ] Writing                      │
│     │   ├── [ ] Music     [ ] 3D Models     [ ] Other                        │
│     ├── Selection → Tool palette pre-configured                              │
│     └── "You can change this anytime. Let's start simple."                   │
│                                                                              │
│  2. PRIVATE PRACTICE (1-5 minutes)                                           │
│     ├── "Practice Mode" (not live, no spectators)                            │
│     ├── Canvas + minimal tools visible                                       │
│     ├── Simulated spectator bids appear (AI-generated)                       │
│     │   └── "A spectator suggests: 'Add more contrast'"                      │
│     ├── User practices responding or ignoring                                │
│     └── Toast: "Ready to go live? [Start Stream]"                            │
│                                                                              │
│  3. FIRST STREAM (5-15 minutes)                                              │
│     ├── User clicks [Start Stream]                                           │
│     ├── Visibility options:                                                  │
│     │   ├── 🔒 Private (invite-only link)                                    │
│     │   ├── 👥 Friends (followers only)                                      │
│     │   └── 🌍 Public (discoverable)                                         │
│     ├── Default: 🔒 Private (reduces pressure)                               │
│     ├── First spectator joins → Celebration confetti                         │
│     └── Stream ends → Summary: "5 bids received, 12 tokens earned"           │
│                                                                              │
│  4. ARTIFACT COMPLETION                                                      │
│     ├── [Finalize Artifact] button                                           │
│     ├── Naming + description modal                                           │
│     ├── Options: [Add to Gallery] [Keep Private] [Sell/License]              │
│     └── Gallery placement → notification to spectators who contributed       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 3: Exquisite Cadaver Mode ("The Handoff Dance")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ SETUP: Host creates Exquisite Cadaver session                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. CONFIGURATION                                                            │
│     ├── Host sets parameters:                                                │
│     │   ├── Participants: 3-8 builders                                       │
│     │   ├── Round time: 5/10/15 minutes                                      │
│     │   ├── Visibility: Edge-only (see only last 10% of previous work)       │
│     │   └── Theme (optional): "Metamorphosis"                                │
│     ├── Invites sent → Builders join waiting room                            │
│     └── Spectators can join to watch the full evolving piece                 │
│                                                                              │
│  2. ROUND 1: Builder A                                                       │
│     ├── Builder A sees: Empty canvas + theme prompt                          │
│     ├── Spectators see: Full canvas                                          │
│     ├── Timer: 10:00 → counting down                                         │
│     ├── Builder A creates first section                                      │
│     └── Timer ends → "Your turn is complete. Passing to Builder B..."        │
│                                                                              │
│  3. ROUND 2: Builder B                                                       │
│     ├── Builder B sees: Only the rightmost 10% of Builder A's work           │
│     │   └── Visual: Fog/blur covering 90%, clear edge visible                │
│     ├── Builder B continues from the visible edge                            │
│     ├── Spectators see: Full canvas (A + B sections)                         │
│     └── Timer ends → Handoff to Builder C                                    │
│                                                                              │
│  4. REVELATION                                                               │
│     ├── All rounds complete                                                  │
│     ├── Dramatic reveal: Fog lifts, full piece visible to ALL               │
│     ├── Builders react in live video call (optional)                         │
│     ├── Artifact saved to Gallery with contributor credits                   │
│     └── Spectators who bid get "Witness" badge on artifact                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Flow 4: Festival Mode ("The Seasonal Surge")

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONTEXT: "Metamorphosis Festival" — 72-hour themed event                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. PRE-LAUNCH (1 week before)                                               │
│     ├── Homepage takeover: Festival announcement                             │
│     ├── Builders opt-in → Special badge on profile                           │
│     ├── Constraint Pack revealed: "Metamorphosis" themed prompts             │
│     └── Early-bird spectator tokens purchasable at discount                  │
│                                                                              │
│  2. DAY 1: OPENING CEREMONY                                                  │
│     ├── Curated builder spotlight streams                                    │
│     ├── Leaderboard appears: "Top Contributors"                              │
│     ├── Community challenges unlock:                                         │
│     │   └── "Collective bid 1000 tokens → unlock Secret Theme"               │
│     └── First artifacts enter Festival Gallery                               │
│                                                                              │
│  3. DAYS 2-3: MOMENTUM                                                       │
│     ├── Hourly highlights: "Stream of the Hour"                              │
│     ├── Cross-pollination: Builders can "remix" each other's artifacts       │
│     ├── Spectator achievements unlock:                                       │
│     │   ├── "Watch 10 streams" → Festival Badge                              │
│     │   ├── "Bid 50 tokens" → Influence Ring                                 │
│     │   └── "Participate in Exquisite Cadaver" → Collaborator Crown          │
│     └── Real-time festival stats displayed                                   │
│                                                                              │
│  4. CLOSING: AWARDS                                                          │
│     ├── Community voting on artifacts                                        │
│     ├── Categories: Most Collaborative, Most Surprising, Crowd Favorite      │
│     ├── Winners announced in closing stream                                  │
│     ├── Festival artifacts become "vintage" (permanent badge)                │
│     └── Wrap-up email: "You contributed to 23 artifacts 🎉"                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Interaction Micropatterns

### Spectator Bid Injection

```
[Spectator clicks BID]
    │
    ▼
┌──────────────────────────────┐
│ What should [Builder] try?   │
├──────────────────────────────┤
│ 💭 Suggest direction    (1)  │  ← Natural language input
│ 🎨 Suggest color        (1)  │  ← Color picker
│ 🔥 Challenge            (5)  │  ← Predefined challenge cards
│ ⚡ Boost current path   (2)  │  ← Reinforce what's happening
└──────────────────────────────┘
    │
    ▼
[Bid appears in Builder's stream with soft animation]
    │
    ▼
[Builder can: Accept ✓ | Acknowledge 👋 | Ignore ×]
    │
    ▼
[Spectator sees outcome + 1.5x token refund if accepted]
```

### Builder Response Flow

```
[Bid arrives]
    │
    ▼
┌─────────────────────────────────────────┐
│ 💡 [Username] suggests: "More contrast" │
│                                         │
│    [Accept] [Acknowledge] [Later]       │
└─────────────────────────────────────────┘
    │
    ├── [Accept] → Constraint becomes visible commitment
    │              → Spectator notification: "Accepted! 🎉"
    │              → +Reputation for builder
    │
    ├── [Acknowledge] → "Thanks! I'll consider it"
    │                 → Spectator gets half token refund
    │
    └── [Later] → Bid queued in sidebar
                → No notification to spectator
```

---

## References

- Master plan: `plans/core-apps-synthesis.md` §2.1
- Original idea: `brainstorming/2025-12-15-art-creativity-ideas.md`
- Existing code: `impl/claude/agents/atelier/`

### UX Research Sources

- [Twitch Platform Economy Research](https://www.tandfonline.com/doi/full/10.1080/1369118X.2024.2331766) — Capital flow and friction in spectator economies
- [Twitch 2025 Features](https://www.valueyournetwork.com/en/twitch-in-2025-new-features-will-change-everything/) — Interactive features roadmap
- [Figma Multiplayer Technology](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/) — Real-time collaboration patterns
- [Figma 2025 Updates](https://www.c-sharpcorner.com/article/figma-2025-updates-a-game-changer-for-design-and-collaboration/) — AI and collaboration features
- [Twitch UI/UX Case Study](https://medium.com/design-bootcamp/chat-is-this-real-ui-ux-analysis-on-twitch-mobile-app-8f6e1af7ca9c) — Mobile interaction patterns

---

*Last updated: 2025-12-15*
