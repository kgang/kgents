# Morning Coffee ☕ — Developer Invigoration Ritual

> *"The musician doesn't start with the hardest passage. She tunes, breathes, plays a scale, feels the instrument respond."*

**Status**: Conceptual Design
**Created**: 2025-12-21
**Voice Anchor**: *"Flit in and out of flow like a musician or artist"*

---

## The Insight

Traditional dev rituals (standups, status checks, sprint planning) are **extractive** — they pull information FROM the developer. Morning Coffee is **generative** — it helps the developer BECOME ready for creative work.

Kent arrives having:
- Rested his aching eyes
- Dreamed, imagined, frolicked among non-CS concepts
- Reached a state of relative relaxation and authenticity

This liminal state is **precious**. Morning Coffee should:
1. **Honor** it (not immediately demand focus)
2. **Bridge** it (gentle transition, not jarring context switch)
3. **Capture** it (fresh voice, authentic reactions)
4. **Amplify** it (channel morning clarity into the day's work)

---

## The Four Movements

### Movement 1: The Garden View 🌱
*"What grew while I slept?"*

A **non-demanding** overview that lets Kent's eye wander:

```
┌─────────────────────────────────────────────────────────┐
│  Yesterday's Harvest                                     │
├─────────────────────────────────────────────────────────┤
│  ◉ 3 files changed → Brain persistence hardening        │
│  ◉ New test: test_semantic_consistency.py               │
│  ◉ UI: Gestalt2D now renders crystalline facets         │
│                                                          │
│  🌿 Growing:   Brain 100% → stable                      │
│  🌱 Sprouting: Gestalt 70% → crystalline rendering      │
│  🌰 Seeds:     ASHC compiler → L0 kernel designed       │
└─────────────────────────────────────────────────────────┘
```

**Implementation**: Pull from git diff, NOW.md percentages, and recent brainstorming files.

### Movement 2: The Conceptual Weather 🌤️
*"What's shifting in the atmosphere?"*

Not code changes — **conceptual movements**:

```
┌─────────────────────────────────────────────────────────┐
│  Conceptual Weather Report                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🔄 REFACTORING: S-gents → D-gents consolidation        │
│     The "stateful agent" abstraction is migrating...    │
│                                                          │
│  🌊 EMERGING: Failure-as-Evidence principle             │
│     "What you tried and rejected is information"        │
│                                                          │
│  🏗️ SCAFFOLDING: ASHC compiler architecture             │
│     L0 kernel → Pass operad → Bootstrap regeneration    │
│                                                          │
│  ⚡ TENSION: Depth vs. breadth in crown jewel work      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Implementation**: Parse recent plan files, detect "refactor", "consolidation", "emerging" patterns. Use the trace/graph visualizations to show conceptual topology.

### Movement 3: The Menu 🍳
*"What suits my taste this morning?"*

Present **challenge gradients** — Kent chooses valence and magnitude:

```
┌─────────────────────────────────────────────────────────┐
│  Today's Menu                                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🧘 GENTLE (warmup, low stakes)                         │
│     • Write a test for existing behavior                │
│     • Document a pattern you discovered yesterday       │
│     • Refine a UI detail that's been bugging you        │
│                                                          │
│  🎯 FOCUSED (clear objective, moderate depth)           │
│     • Wire ASHC L0 kernel to existing AST               │
│     • Complete Gestalt crystalline facet interaction    │
│     • Implement one ASHC pass                           │
│                                                          │
│  🔥 INTENSE (deep work, high cognitive load)            │
│     • Bootstrap regeneration: make spec regenerate impl │
│     • Solve the sheaf coherence visualization problem   │
│     • Design the voice capture feedback loop            │
│                                                          │
│  🎲 SERENDIPITOUS (follow curiosity)                    │
│     "What caught your eye in the garden view?"          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Key**: These aren't assigned tasks. They're **invitations**. Kent picks based on how he feels *right now*.

### Movement 4: The Fresh Capture 📝
*"What's Kent saying before the code takes over?"*

This is the **anti-sausage goldmine**. Before Kent dives into code, capture:

```
Morning Voice (2025-12-21):

Q: "What's on your mind that has nothing to do with code?"
A: [Kent's authentic morning thought]

Q: "Looking at the garden view, what catches your eye?"
A: [Fresh reaction, not filtered through implementation concerns]

Q: "What would make today feel like a good day?"
A: [Authentic success criteria]
```

**Why this matters**:
- Kent at 8am after rest ≠ Kent at 11pm after 6 hours of debugging
- Morning Kent is closer to the "vision holder"
- These captures become voice anchors for future anti-sausage checks

---

## Implementation Sketch

### Phase 1: CLI Ritual (Simple, Immediate)

```bash
kg morning-coffee
# or
kg coffee
```

Invokes a multi-step dialogue:
1. Display Garden View (non-interactive, just observation)
2. Display Conceptual Weather (same)
3. Present Menu (wait for selection)
4. Fresh Capture prompts (record responses)
5. Transition phrase: "Alright, let's begin. Your chosen path: [X]"

### Phase 2: Rich Visualization

Use existing infrastructure:
- **Trace system** → Show conceptual lineage ("this idea came from...")
- **Graph structure** → Visualize where today's work fits in the larger topology
- **Gestalt rendering** → Morning Coffee as a "crystalline moment" visualization

### Phase 3: Voice Loop Integration

Morning captures feed back into:
- Anti-sausage checks (is today's code consistent with morning Kent's voice?)
- K-gent personality (morning Kent is input to the "best day" persona)
- Long-term voice preservation (track how morning Kent evolves over months)

---

## Open Questions

1. **Timing**: Is this literally first thing, or after actual coffee?
2. **Duration**: 5 minutes? 15? Should feel unhurried but not lengthy
3. **Interruptibility**: Can Kent bail at any movement if inspiration strikes?
4. **Persistence**: Where do morning captures live? Private journal? HYDRATE.md?
5. **Periodicity**: Daily? Or "when Kent feels like it"?

---

## Connection to Existing Systems

| System | Morning Coffee Integration |
|--------|---------------------------|
| **NOW.md** | Garden View pulls from here |
| **ASHC** | Conceptual Weather shows compiler state |
| **K-gent** | Fresh Capture feeds personality |
| **Gestalt** | Visualization surface for conceptual weather |
| **Anti-Sausage** | Morning voice becomes reference anchor |

---

## The Deeper Pattern

Morning Coffee is an instance of a more general pattern:

**Liminal Transition Protocols** — rituals that honor state changes:
- Morning Coffee: Rest → Work
- `kg pause`: Deep Work → Break
- `kg evening`: Work → Rest
- `kg return`: Away → Back

Each transition is an opportunity to:
1. **Capture** the state being left
2. **Bridge** between states gracefully
3. **Prepare** the state being entered

---

## Voice Anchors for This Concept

*"Flit in and out of flow like a musician or artist"*
*"Fresh interactions at his relatively most relaxed and authentic"*
*"The valence and magnitude of challenge suited to my taste that instant"*
*"After he's had the night off to rest his literally aching eyes, imagine things, and frolick among concepts not computer science"*

---

## Next Steps

1. [ ] Prototype Garden View (parse git + NOW.md)
2. [ ] Prototype Conceptual Weather (parse plans/*.md)
3. [ ] Design Menu generation (difficulty gradients from TODO items)
4. [ ] Implement Fresh Capture storage
5. [ ] Wire to CLI: `kg coffee`

---

*"The morning mind knows things the afternoon mind has forgotten."*
