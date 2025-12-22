# UX Design: Witness + Fusion Experience

> *"The workshop breathes. The arena listens. Every action leaves a mark."*

**Status:** 📐 Design Specification (Agent-as-Witness complete — ready for UX impl)
**Priority:** MEDIUM (ready for implementation)
**Date:** 2025-12-21
**Implements:** Agent-as-Witness + Symmetric Supersession Phase 0
**Creative Heritage:** Crown Jewels Genesis Moodboard, Punchdrunk Theater, Alive Workshop

---

## I. Design Philosophy

### The Core Metaphor: The Living Arena

The Witness + Fusion system is a **living arena** where:
- **Marks** are leaves falling—each action leaves a trace that accumulates
- **Proposals** are seeds that grow into positions
- **Challenges** are vines that connect and test proposals
- **Synthesis** blooms at the bottom, where gravity pulls toward resolution
- **The Disgust Veto** is a thunderclap—instant, visceral, unmistakable

### Ontological Foundation

**The Witness is in the World, not the Self.**

```
self.*   = Kent's inner world (preferences, memories, capabilities)
world.*  = Agents Kent interacts with (witness, gestalt, town)
```

The Witness observes Kent from the world. It wears a mask too (Punchdrunk). This is not metaphor—it's architecture. `world.witness` is an agent that:
- Observes Kent's actions
- Records marks on Kent's behalf
- Can be consulted by Kent
- Has its own perspective (observer-dependent)

### Aesthetic Alignment

From the Crown Jewels Genesis Moodboard:

| Principle | Application |
|-----------|-------------|
| **Everything Breathes** | Proposals pulse gently; the arena has ambient animation |
| **Growing Transitions** | New elements grow from seed to full size (300-500ms) |
| **Unfurling Panels** | Dialogs open like leaves, not mechanical slides |
| **Flowing Data** | Challenges flow downward like water toward synthesis |
| **Living Earth Palette** | Warm earth tones for grounding; Ghibli glow for synthesis |

### Interaction Model

From Punchdrunk Theater (Sleep No More):
- **Immersive Inhabit**: User is a participant, not an observer
- **Spectator-as-Actor**: Kent doesn't watch the dialectic—Kent IS in the dialectic
- **The Mask**: Kent's identity is preserved even as he becomes part of the system
- **The Witness Wears a Mask Too**: It observes from outside, with its own perspective

---

## II. CLI Experience

### Command Structure

All commands are AGENTESE paths projected to CLI. The Witness lives at `world.witness.*`:

```bash
# Witness Commands (via km shortcut)
km "Refactored DI container"                                # Quick mark (minimum friction)
km "Chose PostgreSQL" -w "Scaling needs"                    # With reasoning
km "Adopted Crown Jewel pattern" -p composable,generative   # With principles

# Full AGENTESE paths (equivalent)
kg world.witness.mark "Refactored DI container"
kg world.witness.recent                                     # Recent marks
kg world.witness.recent --limit 20                          # More marks
kg world.witness.get mark-20251221-143025-a1b2c3d4         # Specific mark
kg world.witness.session                                    # Current session marks
kg world.witness.retract mark-abc123 -w "Typo, meant X"    # Retract (not delete)

# Fusion Commands
kg world.fusion.propose "Use LangChain" --agent kent -w "Scale"
kg world.fusion.propose "Build kgents" --agent claude -w "Novel"
kg world.fusion.fuse prop-a1b2 prop-c3d4 --synthesis "Build kernel, validate"

kg world.dialectic.arena                                    # View active dialectics
kg world.dialectic.trace fuse-a1b2c3d4                     # View dialectic trace

# The Veto (sacred, requires typed confirmation)
kg world.fusion.veto fuse-a1b2c3d4                         # Prompts for confirmation
```

### The `km` Command: Maximum Ergonomics

The most common action—leaving a mark—gets a dedicated command:

```bash
# Absolute minimum friction
$ km "Decided to use async/await"
✓ mark-a1b2c3d4 [session:current]

# With reasoning (-w = why)
$ km "Refactored DI" -w "Enable Crown Jewel pattern"
✓ mark-e5f6g7h8
  ↳ Enable Crown Jewel pattern

# With principles (-p)
$ km "Chose composition over inheritance" -p composable
✓ mark-i9j0k1l2 [composable]

# Full form (rarely needed)
$ km "Major architecture decision" -w "Enables X, Y, Z" -p tasteful,generative --agent kent
```

**Why `km` instead of `kg mark`?**
- Common operations deserve short commands (Unix philosophy)
- `km` = "kgents mark" — memorable mnemonic
- Two keystrokes vs seven: friction matters for frequent actions

### `km` vs `kg decide`: Complementary Tools

| Command | Purpose | Dialectic | Example |
|---------|---------|-----------|---------|
| `km` | Atomic observations | No | "Refactored the DI container" |
| `kg decide` | Decisions with reasoning | Optional | "Chose PostgreSQL over SQLite because scaling" |

**When to use `km`:**
- Recording what happened (not why)
- Quick notes during work
- Observations without justification required

**When to use `kg decide`:**
- Recording a choice between options
- When Kent and Claude had different views
- When the reasoning matters for the future

Both create marks in `world.witness`. `kg decide` additionally uses `world.fusion` for dialectical structure.

### Auto Session Context

Marks automatically capture session context:

```python
# When running inside Claude Code or kg session:
mark.session_id = current_session()  # Auto-populated
mark.timestamp = now()               # Auto-populated
mark.author = inferred_agent()       # "kent" in CLI, "claude" in Claude Code
```

This enables:
```bash
$ kg world.witness.session           # "What did I mark this session?"
$ kg world.witness.today             # "What did I mark today?"
```

### Retract (Not Delete) Marks

Marks are immutable, but humans make typos:

```bash
$ kg world.witness.retract mark-abc123 -w "Typo, meant async not sync"
✓ Retracted: mark-abc123
  ↳ Original preserved, semantically superseded
```

Creates a new mark: `Mark(action="RETRACTED: original", reasoning="Typo...")`. The original persists (immutability law) but is marked as superseded.

### Interactive Dialectic Mode (Phase 1)

> **Note**: The interactive TUI is deferred to Phase 1. Phase 0 uses simple commands.

For Phase 0, use sequential commands:

```bash
# Create proposals
$ kg world.fusion.propose "Use LangChain" --agent kent -w "Scale, resources"
✓ prop-a1b2c3d4

$ kg world.fusion.propose "Build kgents" --agent claude -w "Novel contribution"
✓ prop-e5f6g7h8

# Fuse with manual synthesis
$ kg world.fusion.fuse prop-a1b2 prop-e5f6 \
    --synthesis "Build minimal kernel, validate, then decide" \
    -w "Avoids both risks"
✓ fuse-i9j0k1l2 [SYNTHESIZED]
  ↳ All steps recorded as marks

# Check the fusion
$ kg world.dialectic.trace fuse-i9j0k1l2
```

**Phase 1** will add the full interactive TUI with visual arena, flowing challenges, and real-time synthesis.

### The Disgust Veto (CLI)

The veto must feel **sacred and visceral**. It requires **intentional friction**:

```bash
$ kg world.fusion.veto fuse-x1y2z3

╔══════════════════════════════════════════════════════════════════════════╗
║                              ⚡ VETO ⚡                                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  You are about to apply the DISGUST VETO.                                ║
║                                                                           ║
║  This is the ethical floor. It cannot be argued away.                    ║
║  The synthesis will be rejected.                                         ║
║                                                                           ║
║  To confirm, type exactly: I feel disgust                                ║
║  > _                                                                     ║
║                                                                           ║
╚══════════════════════════════════════════════════════════════════════════╝

> I feel disgust

Why? (describe the somatic signal): Feels like selling out. Visceral wrongness.

╔══════════════════════════════════════════════════════════════════════════╗
║                           VETO APPLIED                                    ║
║                                                                           ║
║  The synthesis has been rejected.                                        ║
║  Signal: "I feel disgust"                                                ║
║  Reason: "Feels like selling out. Visceral wrongness."                   ║
║                                                                           ║
║  Recorded as mark with [ethical] principle.                              ║
║                                                                           ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Why require typing "I feel disgust"?**
- **Deliberate friction**: Prevents accidental veto
- **Self-awareness**: Kent acknowledges the somatic signal explicitly
- **Recorded truth**: The literal phrase becomes part of the mark
- **Honors the body**: Disgust is phenomenological, not argumentative

### CLI Output Density

Following the Elastic UI Patterns, CLI output adapts to terminal width:

| Width | Mark Display |
|-------|--------------|
| <60 cols | `✓ mark-...a1b2` |
| <100 cols | `✓ Mark: "Refactored DI" (mark-...a1b2)` |
| ≥100 cols | Full display with reasoning and principles |

---

## III. Web Frontend Experience

### Layout: The Dialectical Arena (Vertical-First)

**Design Decision**: Vertical layout by default. Horizontal is Spacious-mode upgrade only.

**Why vertical?**
- Horizontal feels adversarial (face-to-face confrontation)
- Vertical feels like conversation (flowing toward resolution)
- Synthesis at bottom = gravity pulls toward resolution
- Better for mobile-first responsive design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  kgents                          [Witness] [Fusion] [Arena]        🌱 Kent  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                       DIALECTICAL ARENA                              │   │
│   │                                                                      │   │
│   │   ╭─────────────────────────────────────────────────────────────╮   │   │
│   │   │                      PROPOSAL A                              │   │   │
│   │   │  🧑 kent                                                     │   │   │
│   │   │  "Use LangChain"                                             │   │   │
│   │   │  ↳ Scale, resources, production validation                  │   │   │
│   │   ╰─────────────────────────────────────────────────────────────╯   │   │
│   │                              ↓                                       │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │  CHALLENGES (flowing down)                                   │   │   │
│   │   │  ─────────────────────────────────────────────────────────  │   │   │
│   │   │  [claude → A] "Feature sprawl violates Tasteful..."         │   │   │
│   │   │  [kent → B] "Philosophy doesn't ship..."                    │   │   │
│   │   │  + Add Challenge                                             │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                              ↓                                       │   │
│   │   ╭─────────────────────────────────────────────────────────────╮   │   │
│   │   │                      PROPOSAL B                              │   │   │
│   │   │  🤖 claude                                                   │   │   │
│   │   │  "Build kgents"                                              │   │   │
│   │   │  ↳ Novel contribution, aligned with soul                    │   │   │
│   │   ╰─────────────────────────────────────────────────────────────╯   │   │
│   │                              ↓                                       │   │
│   │   ╭─────────────────────────────────────────────────────────────╮   │   │
│   │   │                      SYNTHESIS                               │   │   │
│   │   │  ● ● ●  (forming... breathing animation)                    │   │   │
│   │   │                                                              │   │   │
│   │   │  "Build minimal kernel, validate, then decide"              │   │   │
│   │   ╰─────────────────────────────────────────────────────────────╯   │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌────────────────────────────────────┐  ┌────────────────────────────┐   │
│   │  WITNESS TRACE                      │  │      ⚡ VETO ⚡            │   │
│   │  ════════════════════════════════  │  │                            │   │
│   │  [14:30] kent proposed...           │  │  Type "I feel disgust"    │   │
│   │  [14:30] claude proposed...         │  │  to apply veto            │   │
│   │  [14:31] claude challenged...       │  │                            │   │
│   └────────────────────────────────────┘  └────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Spacious mode (≥1024px)**: Can optionally show horizontal layout with proposals side-by-side and synthesis in center. But vertical remains the default for its conversational feel.

### Component Hierarchy

```
ArenaPage/
├── ArenaHeader                 # Title, navigation, user badge
├── DialecticalArena/           # Main arena visualization
│   ├── ProposalCard            # Agent's proposal (grows from seed)
│   │   ├── AgentBadge          # kent/claude/k-gent icon
│   │   ├── ProposalContent     # The proposal text
│   │   ├── ReasoningPanel      # Expandable reasoning
│   │   └── PrincipleChips      # Which principles support this
│   ├── ChallengeFlow           # Animated vines between proposals
│   │   └── ChallengeParticle   # Individual challenge flowing
│   └── SynthesisOrb            # Center synthesis (breathing animation)
│       ├── SynthesisContent    # What emerged
│       └── StatusIndicator     # forming/synthesized/vetoed
├── ChallengeStream/            # Left panel: challenge history
│   ├── ChallengeCard           # Individual challenge
│   └── AddChallengeForm        # Input for new challenge
├── VetoPanel/                  # Right panel: the sacred veto
│   ├── VetoButton              # Big, red, unmistakable
│   └── VetoConfirmDialog       # Requires reason
└── WitnessTrace/               # Bottom: marks from this dialectic
    └── MarkTimeline            # Chronological marks
```

### Animation Specifications

Following "Everything Breathes":

| Element | Animation | Timing |
|---------|-----------|--------|
| **ProposalCard** | Idle: subtle scale pulse (1.0 → 1.02 → 1.0) | 3s ease-in-out loop |
| **ProposalCard** | Entry: grow from seed (0 → 1 scale) | 400ms cubic-bezier(0.34, 1.56, 0.64, 1) |
| **ChallengeFlow** | Particles flow along bezier curve | 2s linear loop |
| **SynthesisOrb** | Forming: ripple effect | 1s ease-out loop |
| **SynthesisOrb** | Synthesized: gentle glow pulse | 4s ease-in-out loop |
| **VetoButton** | Hover: subtle shake | 150ms |
| **VetoButton** | Active: thunderclap flash | 200ms |

### Color Application

From Living Earth palette:

| Element | Color | Hex |
|---------|-------|-----|
| **Arena background** | Soil (dark) | #2D1B14 |
| **ProposalCard (kent)** | Copper | #C08552 |
| **ProposalCard (claude)** | Sage | #4A6B4A |
| **ChallengeFlow** | Amber glow | #D4A574 |
| **SynthesisOrb (forming)** | Honey | #E8C4A0 |
| **SynthesisOrb (synthesized)** | Lantern (bright) | #F5E6D3 |
| **VetoButton** | Urgent (red-brown) | #8B4513 |
| **WitnessTrace** | Wood | #6B4E3D |

### Responsive Behavior (Elastic UI)

| Density | Arena Layout | Challenge Stream | Veto Panel |
|---------|--------------|------------------|------------|
| **Compact** (<768px) | Vertical stack | Bottom drawer | Floating button |
| **Comfortable** (768-1023px) | Horizontal, collapsed sidebar | Collapsible panel | Side panel |
| **Spacious** (≥1024px) | Full layout | Always visible | Always visible |

### Mobile Experience

```
╔═════════════════════════════════════╗
║  DIALECTICAL ARENA          ≡       ║
╠═════════════════════════════════════╣
║                                     ║
║   ╭─────────────────────────────╮   ║
║   │       PROPOSAL A            │   ║
║   │                             │   ║
║   │  "Use LangChain"            │   ║
║   │   🧑 kent                   │   ║
║   ╰─────────────────────────────╯   ║
║                 ↕                   ║
║   ╭─────────────────────────────╮   ║
║   │       PROPOSAL B            │   ║
║   │                             │   ║
║   │  "Build kgents"             │   ║
║   │   🤖 claude                 │   ║
║   ╰─────────────────────────────╯   ║
║                 ↓                   ║
║   ╭─────────────────────────────╮   ║
║   │       SYNTHESIS             │   ║
║   │       ● ● ●                 │   ║
║   ╰─────────────────────────────╯   ║
║                                     ║
╠═════════════════════════════════════╣
║  [Challenge] [Synthesize]  [⚡VETO] ║
╚═════════════════════════════════════╝
        ▲
        │ Swipe up for Challenge Stream
        │
╔═════════════════════════════════════╗
║         CHALLENGE STREAM            ║
╠═════════════════════════════════════╣
║                                     ║
║  [claude → A]                       ║
║  "Feature sprawl violates..."       ║
║                                     ║
║  [kent → B]                         ║
║  "Philosophy doesn't ship..."       ║
║                                     ║
║  + Add Challenge                    ║
║                                     ║
╚═════════════════════════════════════╝
```

---

## IV. Witness Dashboard

A dedicated view for exploring marks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  kgents                          [Witness] [Fusion] [Arena]        🌱 Kent  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  WITNESS: THE GARDEN OF MARKS                                        │   │
│   │                                                                      │   │
│   │  Today                                                               │   │
│   │  ══════════════════════════════════════════════════════════════════ │   │
│   │                                                                      │   │
│   │  🍂 14:32  "Synthesis: Build minimal kernel, validate"              │   │
│   │            Principles: [tasteful] [generative]                      │   │
│   │            Author: system                                            │   │
│   │                                                                      │   │
│   │  🍂 14:31  "Challenge: Philosophy doesn't ship"                     │   │
│   │            Author: kent                                              │   │
│   │                                                                      │   │
│   │  🍂 14:30  "Proposal: Build kgents"                                 │   │
│   │            Reasoning: Novel contribution, aligned with soul         │   │
│   │            Principles: [tasteful] [generative] [joy-inducing]       │   │
│   │            Author: claude                                            │   │
│   │                                                                      │   │
│   │  🍂 14:30  "Proposal: Use LangChain"                                │   │
│   │            Reasoning: Scale, resources, production validation       │   │
│   │            Author: kent                                              │   │
│   │                                                                      │   │
│   │  Yesterday                                                           │   │
│   │  ══════════════════════════════════════════════════════════════════ │   │
│   │                                                                      │   │
│   │  🍂 23:45  "Completed Crown Jewel Cleanup"                          │   │
│   │            Principles: [curated]                                     │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌──────────────────────────────────┐  ┌───────────────────────────────┐   │
│   │  QUICK MARK                      │  │  FILTERS                      │   │
│   │                                  │  │                               │   │
│   │  Action: _____________________   │  │  Author: [All ▼]              │   │
│   │  Why:    _____________________   │  │  Principle: [All ▼]          │   │
│   │                                  │  │  Date: [This week ▼]         │   │
│   │  [Create Mark]                   │  │                               │   │
│   └──────────────────────────────────┘  └───────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## V. Teaching Mode Integration

Following Dense Teacher from Crown Jewels:

```
╔══════════════════════════════════════════════════════════════════════════╗
║  TEACHING MODE: ON                                                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  ╭──────────────────────────────────────────────────────────────────────╮ ║
║  │  💡 SYMMETRIC SUPERSESSION                                           │ ║
║  │  ════════════════════════════════════════════════════════════════   │ ║
║  │                                                                      │ ║
║  │  Kent and Claude are SYMMETRIC AGENTS.                              │ ║
║  │  Both can propose. Both can challenge. Both can be superseded.      │ ║
║  │                                                                      │ ║
║  │  The system can supersede Kent's decision when:                     │ ║
║  │  1. Proofs are valid                                                │ ║
║  │  2. Arguments are sound                                             │ ║
║  │  3. Evidence is sufficient                                          │ ║
║  │  4. No DISGUST VETO                                                 │ ║
║  │                                                                      │ ║
║  │  The Disgust Veto is the ethical floor. It cannot be argued away.   │ ║
║  │                                                                      │ ║
║  │  See: brainstorming/2025-12-21-symmetric-supersession.md            │ ║
║  ╰──────────────────────────────────────────────────────────────────────╯ ║
║                                                                           ║
║  ╭──────────────────────────────────────────────────────────────────────╮ ║
║  │  💡 WITNESS MARKS                                                    │ ║
║  │  ════════════════════════════════════════════════════════════════   │ ║
║  │                                                                      │ ║
║  │  Every action in this dialectic leaves a MARK.                      │ ║
║  │  Marks are immutable. They are the proof.                           │ ║
║  │                                                                      │ ║
║  │  Mark = { action, reasoning?, principles[], author, timestamp }     │ ║
║  │                                                                      │ ║
║  │  See: brainstorming/2025-12-21-agent-as-witness.md                  │ ║
║  ╰──────────────────────────────────────────────────────────────────────╯ ║
║                                                                           ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## VI. Component Inventory

### New Primitives Needed

| Primitive | Purpose | Location |
|-----------|---------|----------|
| `ProposalCard` | Display agent proposal with breathing animation | `components/fusion/` |
| `ChallengeFlow` | Animated vine between proposals | `components/fusion/` |
| `SynthesisOrb` | Center synthesis visualization | `components/fusion/` |
| `VetoButton` | Sacred veto trigger | `components/fusion/` |
| `VetoConfirmDialog` | Requires reason for veto | `components/fusion/` |
| `MarkCard` | Display individual mark | `components/witness/` |
| `MarkTimeline` | Chronological mark display | `components/witness/` |
| `QuickMarkForm` | Minimal friction mark creation | `components/witness/` |
| `DialecticalArena` | Main arena layout | `components/fusion/` |
| `AgentBadge` | Kent/Claude/K-gent identifier | `components/shared/` |

### Reusing Existing Primitives

| Primitive | From | Use In |
|-----------|------|--------|
| `ElasticSplit` | `elastic/` | Arena layout |
| `BottomDrawer` | `elastic/` | Mobile challenge stream |
| `FloatingActions` | `elastic/` | Mobile FABs |
| `TeachingCallout` | `categorical/` | Teaching mode panels |
| `TracePanel` | `categorical/` | Witness trace display |
| `StateIndicator` | `categorical/` | Synthesis status |

---

## VII. AGENTESE Integration

### Ontological Placement

All witness/fusion nodes live in `world.*` because they are agents observing Kent from outside:

```
world.witness.*     The Witness agent (observes, records marks)
world.fusion.*      The Fusion agent (facilitates dialectic)
world.dialectic.*   The Dialectic inspector (views arena state)
```

### Node Registration

```python
# world.witness.* nodes
@node(path="world.witness", ...)
class WitnessNode:
    async def mark(...) -> MarkResponse
    async def recent(...) -> RecentResponse
    async def get(...) -> MarkResponse | None
    async def session(...) -> SessionResponse      # Current session marks
    async def retract(...) -> MarkResponse         # Retract a mark

# world.fusion.* nodes
@node(path="world.fusion", ...)
class FusionNode:
    async def propose(...) -> ProposeResponse
    async def fuse(...) -> FusionResponse
    async def veto(...) -> FusionResponse          # Typed confirmation required

# world.dialectic.* nodes
@node(path="world.dialectic", ...)
class DialecticNode:
    async def arena(...) -> ArenaResponse
    async def trace(...) -> TraceResponse
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/witness/mark` | POST | Create mark |
| `/api/witness/recent` | GET | Recent marks |
| `/api/witness/marks/{id}` | GET | Specific mark |
| `/api/fusion/propose` | POST | Create proposal |
| `/api/fusion/fuse` | POST | Run fusion |
| `/api/fusion/veto` | POST | Apply veto |
| `/api/dialectic/arena` | GET | Arena state |
| `/api/dialectic/trace/{id}` | GET | Fusion trace |

### React Hooks

```typescript
// Witness hooks
const { mark, recentMarks, isLoading } = useWitness();
const marks = useMarks({ limit: 20, author: 'kent' });

// Fusion hooks
const { propose, fuse, veto, arenaState } = useFusion();
const { challenges, addChallenge } = useDialectic(fusionId);

// Combined hook for arena page
const {
  proposalA, proposalB,
  challenges,
  synthesis,
  addChallenge,
  attemptSynthesis,
  applyVeto,
} = useDialecticalArena(fusionId);
```

---

## VIII. Implementation Phases

### Phase 0.1: CLI Marks (1 session)

- [ ] Implement `km` command (standalone binary or alias)
- [ ] Register `world.witness` AGENTESE node
- [ ] Implement `world.witness.mark`, `.recent`, `.session`, `.retract`
- [ ] CLI output formatting with density awareness
- [ ] Auto session context detection

### Phase 0.2: CLI Dialectic (1 session)

> Note: `kg decide` already exists. This phase refines it.

- [ ] Update `kg decide` to use `world.fusion.*` paths
- [ ] Implement typed veto confirmation ("I feel disgust")
- [ ] Connect `kg decide` to `world.witness` for mark creation
- [ ] Add `kg world.dialectic.trace` for viewing fusion history

### Phase 0.3: Web Witness (1 session)

- [ ] `MarkCard` component
- [ ] `MarkTimeline` component
- [ ] `QuickMarkForm` component
- [ ] Witness dashboard page

### Phase 0.4: Web Arena (1-2 sessions)

- [ ] `ProposalCard` with placeholder breathing animation
- [ ] `ChallengeFlow` (placeholder: static display, animation in Phase 1)
- [ ] `SynthesisOrb` with forming/synthesized states
- [ ] `VetoButton` and `VetoConfirmDialog` (typed confirmation)
- [ ] `DialecticalArena` vertical layout
- [ ] Responsive behavior (Elastic UI)

### Phase 0.5: Integration (1 session)

- [ ] Connect arena to witness (marks recorded)
- [ ] Teaching mode callouts
- [ ] Mobile optimization
- [ ] End-to-end test: run the kgents dialectic in the UI

### Phase 1: Interactive TUI (future)

- [ ] Full interactive `kg fuse --interactive` TUI
- [ ] Real-time challenge/synthesis flow
- [ ] Breathing animations (production quality)
- [ ] Horizontal layout option for Spacious mode

---

## IX. Success Metrics

| Metric | Target |
|--------|--------|
| Time to create mark (CLI) | <3 seconds |
| Time to create mark (Web) | <5 seconds |
| Dialectic completion (happy path) | <5 minutes |
| Veto response time | <1 second (instant feel) |
| Teaching mode comprehension | User understands symmetric supersession |
| Joy-inducing? | Kent smiles while using it |

---

## X. Coaching Kent: Effective Mark Usage

> *"An agent is a thing that justifies its behavior."*

### The Habit to Build

**Goal**: Kent marks naturally, without thinking about it. Marks become as automatic as git commits.

### When to Mark (Quick Reference)

| Trigger | Example Mark |
|---------|--------------|
| Made a choice | `km "Chose async over sync" -w "Non-blocking required"` |
| Finished something | `km "Completed DI refactor"` |
| Hit a wall | `km "Stuck on OAuth flow" -w "Callback URL confusion"` |
| Had an insight | `km "Realized: marks ARE the API"` |
| Changed direction | `km "Abandoned WebSocket approach" -w "SSE simpler"` |
| Disagreed with Claude | Use `kg decide` for dialectic |

### The Two-Second Rule

If it takes more than 2 seconds to decide whether to mark, just mark it. The cost of over-marking is low (clutter, easily filtered). The cost of under-marking is high (lost reasoning, forgotten context).

### Mark Hygiene

**Good marks:**
```bash
km "Chose PostgreSQL over SQLite" -w "Need concurrent writes"
km "Refactored Brain service to Crown Jewel pattern"
km "Bug: session not persisting across restarts"
```

**Less useful marks:**
```bash
km "Did stuff"           # Too vague
km "Fixed it"            # What? Why?
km "Working on things"   # Marks are for decisions/events, not status
```

### Building the Habit: First Week Protocol

**Day 1-2**: Mark at least 5 things. Quantity over quality.

**Day 3-4**: Review marks with `kg world.witness.today`. Notice patterns.

**Day 5-7**: Start using `-w` (why) on significant marks. Notice which marks were actually useful.

**Week 2+**: Marks become automatic. Adjust frequency based on what's useful.

### When Claude Should Prompt for Marks

Claude should gently prompt Kent to mark when:
1. Kent makes a decision after discussion
2. Kent says "let's go with..." or "I think we should..."
3. A significant piece of work completes
4. Kent expresses uncertainty or frustration (valuable to trace)

Example Claude prompt:
> "That's an interesting decision. Want me to mark it? `km 'Chose X over Y' -w 'Reasoning'`"

### The Payoff

After 2-4 weeks of consistent marking:
- `kg world.witness.session` shows the story of each work session
- Patterns emerge (when do you get stuck? what decisions recur?)
- Future Kent thanks past Kent for the context
- Claude can reference marks for continuity

### Anti-Pattern: Performative Marking

Marks are for Kent, not for an audience. Don't mark to "look productive" or "document for others." Mark because it helps you think, remember, and trace.

*"The mark is the proof. The proof is the mark."*

---

## XI. Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| Mechanical animations | Organic, breathing animations |
| Heavy confirmation dialogs | Quick actions with undo |
| Hidden veto | Prominent, sacred veto |
| Separate witness and fusion | Integrated—dialectic creates marks |
| Desktop-only design | Mobile-first with progressive enhancement |
| Teaching mode as afterthought | Teaching mode as core feature |

---

*"The arena breathes. The marks accumulate. The synthesis blooms. The veto thunders."*

---

**Filed:** 2025-12-21
**Refined:** 2025-12-21 (world.witness paths, km command, vertical-first, coaching)
**Implements:** Agent-as-Witness + Symmetric Supersession UX
**Status:** Ready for implementation

### Refinement Summary (2025-12-21)

1. **`world.witness`** not `time.witness` — The Witness is an agent in the world, observing Kent
2. **`km` shortcut** — Maximum ergonomics for frequent marking
3. **Vertical-first arena** — Conversation flowing toward synthesis, not adversarial face-off
4. **Interactive TUI deferred** — Phase 0 uses simple commands; Phase 1 adds TUI
5. **Typed veto confirmation** — "I feel disgust" as intentional friction
6. **Retract mechanism** — Semantic supersession, not deletion (immutability preserved)
7. **`km` vs `kg decide`** — Complementary tools for observations vs decisions
8. **Coaching section** — Guide Kent to build the marking habit
