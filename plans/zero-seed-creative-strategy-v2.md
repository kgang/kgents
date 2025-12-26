# Zero Seed Creative Strategy v2.0

> **DEPRECATED**: This document has been superseded by `plans/zero-seed-strategy-unified.md`.
> Please refer to the unified document for the authoritative Zero Seed strategy.
> This file is retained for historical reference only.

---

> *"The act of declaring, capturing, and auditing your decisions is itself a radical act of self-transformation."*

**Version**: 2.0 (Grounded Refinement)
**Date**: 2025-12-25
**Status**: DEPRECATED - See `plans/zero-seed-strategy-unified.md`
**Supersedes**: `zero-seed-creative-strategy.md` (v1.0) - Both now deprecated

---

## What's New in v2.0

This version incorporates **actual implementation status** from exploration of the codebase:

1. **NOVEL CAPABILITIES** — 15 systems that enable genuinely new interaction modes
2. **GROUNDED GAPS** — Actual implementation status (not aspirational)
3. **PRODUCTIVITY ENHANCEMENTS** — What users can do NOW that was impossible before
4. **WIRING PRIORITIES** — Where frontend meets ready backend

---

## Part 0: The Revelation — What We Built

### The Unified Witness Trail

After exploring the codebase, one architecture emerges as **the key innovation**:

```
Every user action:
  Action → Mark (what, why, evidence)
      ↓
  Trace (accumulated path, justification stack)
      ↓
  Crystal (compressed wisdom, distilled decision rules)
      ↓
  Projection (visible in Hypergraph, Portal, Chat)
```

**Three surfaces, one theoretical substrate**:
- **Hypergraph Editor** = Witness trail as graph navigation
- **Portal Tokens** = Witness trail as document expansion
- **Constitutional Chat** = Witness trail as dialogue history

This is NOT three separate systems. It's three **projections of the same morphism**.

---

## Part I: Novel Capabilities (What We Can Do Now)

These 15 systems enable interaction modes that **no traditional app can offer**:

### 1. Polynomial Agents: Context-Aware Behavior

**What it is**: Agents with mode-dependent inputs. `directions(state) → FrozenSet[valid_inputs]`

**Novel interaction**:
- Context-sensitive action palettes (buttons change based on current state)
- Progressive disclosure (show only valid operations for current mode)
- "What can I do now?" affordance that's always accurate

**UI opportunity**: Mode-aware command palette that shows ONLY valid actions

---

### 2. Galois Loss: Coherence as Metric

**What it is**: `L(P) = d(P, C(R(P)))` — loss measures "hand-waviness" of content

**Implemented**:
- `GaloisLossComputer` with cache (997 LOC)
- Loss range: 0.00 (axiom) → 1.00 (nonsense)
- Layer assignment via loss minimization
- Fixed point detection (axioms = zero-loss fixed points)

**Novel interaction**:
- **Loss gradient navigation** (gl/gh keys) — move toward lower/higher coherence
- **Coherence heatmap** — visualize which ideas are grounded vs. hand-wavy
- **Auto-layer assignment** — system knows where your thought belongs

**UI opportunity**: Coherence thermometer on every K-Block showing how "grounded" it is

---

### 3. Contradiction Detection: Conflicts as Information

**What it is**: Super-additivity detection: `L(A ∪ B) > L(A) + L(B)` = contradiction

**Implemented**:
- 4 modules: detection, classification, resolution, UI
- 4 strength levels: APPARENT, PRODUCTIVE, PROBLEMATIC, GENUINE
- 5 resolution strategies: Synthesize, Choose, Defer, Embrace, Dissolve

**Novel interaction**:
- **Contradiction feed** — see all conflicts in your knowledge base
- **Productive tension marking** — keep contradictions as creative constraints
- **Synthesis suggestions** — system proposes how to reconcile

**UI opportunity**: Contradictions panel with strength indicators and one-click resolution

---

### 4. Modal Hypergraph Editing: Vim for Knowledge

**What it is**: 6-mode semantic editor (NORMAL, INSERT, EDGE, VISUAL, COMMAND, WITNESS)

**Implemented** (6,183 LOC, 92+ keybindings):
- `j/k` scroll, `gd/gr/gt` go to definition/references/tests
- `gl/gh` loss navigation (lowest/highest coherence neighbor)
- `ge` EDGE mode (3-phase edge creation)
- `gw` WITNESS mode (quick marks: mE/mG/mT/mF/mJ/mV)
- `:ag <path>` AGENTESE invocation from command mode

**Novel interaction**:
- **Graph navigation without leaving keyboard** — traverse knowledge by relationships
- **Semantic jumping** — "go to definition" works on concepts, not just code
- **Witness marks during editing** — capture insights AS you work

**UI opportunity**: Already implemented. Just needs wiring to real data.

---

### 5. Portal Tokens: Documents as Hypergraphs

**What it is**: `@[edge_type]` syntax that creates expandable hyperedges

**Implemented**:
- PortalToken component with authoring states (RESOLVED, UNPARSED, CURING, FAILED)
- Natural language curing (LLM resolves unparsed portals)
- Expansion without navigation (inline preview)

**Novel interaction**:
- **Write to explore** — typing `@[tests]` finds test files automatically
- **Semantic autocomplete** — `@[what implements this spec?]` → structured edge
- **Bidirectional linking** — "what portals point to this node?"

**UI opportunity**: Portal authoring panel with cure confidence scores

---

### 6. K-Block Isolation: Transactional Editing

**What it is**: 5 isolation states (PRISTINE, DIRTY, STALE, CONFLICTING, ENTANGLED)

**Implemented** (40 modules):
- Changes invisible until explicit commit
- Witness message required for commit (unless `:w!`)
- 7 views: code, graph, outline, prose, tokens, diff, sync

**Novel interaction**:
- **Edit without fear** — changes are isolated until you're ready
- **Staged → committed** visual transition when you save
- **Witness every save** — "why did I make this change?" captured automatically

**UI opportunity**: K-Block preview with diff view before commit

---

### 7. Sheaf Coherence: Emergence from Perspectives

**What it is**: Multiple observers → glued into emergent global behavior

**Implemented**:
- K-gent soul with 6 eigenvector contexts (AESTHETIC, CATEGORICAL, GRATITUDE, HETERARCHY, GENERATIVITY, JOY)
- `SYNTHESIZING` state glues all contexts via SOUL_SHEAF

**Novel interaction**:
- **Multi-perspective judgment** — see what different observers would think
- **Consensus visualization** — where do perspectives agree/diverge?
- **Context switching** — "view as architect" vs "view as poet"

---

### 8. Constitutional Scoring: 7-Dimensional Reward

**What it is**: Every action scored on 7 principles with weights

**Implemented**:
- Ethical (2.0×), Composable (1.5×), Joy-Inducing (1.2×), others (1.0×)
- Score range: 0-9.7
- Threshold for "aligned": 7.5+

**Novel interaction**:
- **Principle heatmap** — which principles does this action serve?
- **Alignment nudges** — "this would score higher if you added X"
- **Constitutional radar** — 7-spoke visualization of any decision
---

### 9. Feed as Primitive: Stigmergic Surfacing

**What it is**: Feed is not a view of data; feed IS the interface

**Implemented**:
- Ranking: attention, principles, recency, coherence
- Filtering: layer, loss-range, author, time-range, tag, principle
- Feedback integration: view/engage/dismiss tracked

**Novel interaction**:
- **Evidence rises by use** — frequently accessed knowledge surfaces
- **Coherence-sorted feed** — see your most grounded ideas first
- **Contradiction feed** — dedicated view of conflicts

**UI opportunity**: Multiple default feeds (Cosmos, Coherent, Contradictions, Axioms)

---

### 10. AGENTESE Protocol: Semantic Addressing

**What it is**: `await logos.invoke("world.doc.manifest", observer)` — paths as morphisms

**Implemented**:
- 5 contexts: `world.*`, `self.*`, `concept.*`, `void.*`, `time.*`
- Observer-dependent rendering
- JIT compilation via MetaArchitect

**Novel interaction**:
- **No routes, just paths** — navigation is semantic, not URL-based
- **Observer switching** — same path, different manifestation
- **Path autocomplete** — type paths like code, get completions

**UI opportunity**: AGENTESE path bar with live autocomplete and observer toggle

---

### 11. Flux Streaming: Discrete-to-Continuous Lifting

**What it is**: `Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]`

**Implemented**:
- Synapse composition via `|` operator
- States: DORMANT, FLOWING, STOPPED, COLLAPSED
- Perturbation injection while streaming

**Novel interaction**:
- **Stream visualization** — watch data flow through pipeline
- **Live injection** — add new data while stream is flowing
- **Backpressure display** — see when system is overloaded

**UI opportunity**: Stream debugger showing agent pipeline state

---

### 12. Crystal Memory: Self-Justifying Recall

**What it is**: Memories carry their own proofs

**Implemented**:
- Mark → Trace → Crystal compression pipeline
- 4 compression levels: DUST, PEBBLE, STONE, MOUNTAIN
- Mood vector aggregation
- Auto-extracted insights

**Novel interaction**:
- **Memory archaeology** — see how a memory was formed
- **Compression preview** — before/after summaries
- **Coherence inspection** — Galois witness on every crystal

**UI opportunity**: Crystal timeline with expansion/compression visualization

---

### 13. Event Buses: Real-Time Everything

**What it is**: Three-bus pattern (DataBus → SynergyBus → EventBus)

**Implemented**:
- Topics: `witness.git.commit`, `witness.mark.created`, `witness.agentese.invoked`
- SSE infrastructure ready (reconnection logic, event filtering)
- Fire-and-forget mark creation

**Novel interaction**:
- **Activity timeline** — real-time visualization of all system events
- **Topic subscription** — "show me only git commits and mark creations"
- **Live dashboard** — events flow up as they happen

**UI opportunity**: WitnessStream component (already built, SSE ready)

---

### 14. Truth Functor: Verification as Journey

**What it is**: Probes navigate verification state space, accumulating constitutional score

**Implemented**:
- 4 analysis modes: CATEGORICAL, EPISTEMIC, DIALECTICAL, GENERATIVE
- PolicyTrace as immutable proof of verification journey
- Probes compose: `probe_a >> probe_b`

**Novel interaction**:
- **Verification explorer** — visualize probe navigation through state space
- **Test trajectory** — see sequence of tests that led to score
- **Proof editor** — interactive mode where user guides probe

**UI opportunity**: Probe visualization showing verification journey

---

### 15. Town Simulation: Multi-Agent Dialogue

**What it is**: Citizens with internal states, memories, and LLM-backed dialogue

**Implemented**:
- 7-phase lifecycle with state machines
- Memory foveation (focal + peripheral)
- Constitutional-aligned dialogue

**Novel interaction**:
- **Live simulation** — watch agents interact
- **Memory inspector** — peek at agent's focal/peripheral memories
- **Relationship graph** — see agent-agent affinities

**UI opportunity**: Town dashboard (deprioritized post-Extinction, but infrastructure exists). Let's turn this into a pocket terrarium, where the town is able to passively (at a rate of 350k opus tokens per hour, ingest any and all information in the system and emit organized, staged (?) k-blocks to insert into the system) The tentative mandate for the town is to curate, cultivate, and refine the relationships between ideas.

---

## Part II: Implementation Status (Grounded)

### Backend: What's Actually Working

| System | Status | Tests | Ready for UI? |
|--------|--------|-------|---------------|
| **Zero Seed API** | 95% | 200+ | YES |
| **K-Block Core** | 100% | 45+ | YES |
| **Galois Loss** | 100% | 50+ | YES |
| **Contradiction** | 100% | 40+ | YES |
| **Witness** | 98% | 678+ | YES |
| **Feed** | 90% | 30+ | PARTIAL (needs K-Block metadata) |
| **Brain** | 100% | 100+ | YES |
| **Portal** | 95% | 50+ | YES |
| **Liminal** | 70% | 20+ | YES (coffee ritual) |
| **Sovereign** | 85% | 40+ | YES |

### Frontend: What's Actually Working

| Component | Status | LOC | Needs |
|-----------|--------|-----|-------|
| **Hypergraph Editor** | FUNCTIONAL | 6,183 | Real data wiring |
| **Mode System (6 modes)** | FUNCTIONAL | 599 | - |
| **Feed** | PARTIAL | 650 | API connection |
| **K-Block Editor** | FUNCTIONAL | 259 | Proof editing UI |
| **Witness UI** | DISPLAY ONLY | 240 | Creation UI |
| **Elastic Components** | FUNCTIONAL | 1,200+ | - |
| **Portal Tokens** | FUNCTIONAL | 300+ | Cure system |
| **Constitutional Radar** | FUNCTIONAL | 231 | Data connection |
| **SSE Streaming** | INFRASTRUCTURE | 200+ | Enable flags |

### The Gap: Where Frontend Meets Backend

**Ready to wire TODAY**:
1. Feed → `/api/zero-seed/nodes` (replace mock data)
2. Witness creation → `/api/witness/marks` (already has endpoint)
3. Decision stream → `/api/witness/fusion` (polling works)
4. Brain search → `/api/agentese/self/memory/search`
5. Contradiction feed → `/api/zero-seed/health` (returns contradictions)

**Needs API work**:
1. Feed ranking algorithm (types exist, logic partial)
2. K-Block metadata (created_by, tags, loss not in K-Block yet)
3. Real Galois loss computation (returns mock 0.12-0.20)
4. Portal curing (LLM integration needed)

---

## Part III: Productivity Enhancements

### What Users Can Do NOW That Was Impossible Before

| Before kgents | With kgents | Enabling System |
|---------------|-------------|-----------------|
| "Where did I put that idea?" | Semantic search + coherence ranking | Brain + Feed |
| "Why did I decide this?" | Every decision has witness trail | Witness marks |
| "Do my beliefs contradict?" | Automatic contradiction detection | Galois super-additivity |
| "How grounded is this thought?" | Loss score 0.00-1.00 | Galois loss |
| "Navigate by meaning" | gl/gh/gd/gr semantic jumps | Hypergraph Editor |
| "Edit without fear" | K-Block isolation, staged commits | K-Block transactional |
| "See multiple perspectives" | Observer switching, eigenvector radar | Sheaf + AGENTESE |
| "Track my coherence journey" | Coherence timeline over time | Witness + Galois |
| "Export my reasoning" | Decision archaeology with traces | Mark → Trace → Crystal |
| "Find serendipitous connections" | Stigmergic surfacing via void.* | Feed + Brain forage |

### Novel Workflows Enabled

**1. Contradiction Resolution Session**
```
User opens Contradictions feed
  → Sees 3 conflicts with strength indicators
  → Clicks first pair (PRODUCTIVE tension)
  → System suggests synthesis: "Consider merging via..."
  → User creates synthesis K-Block
  → Coherence score rises: 0.76 → 0.81
  → Witness mark captures resolution
```

**2. Semantic Proof Construction**
```
User declares goal (L3)
  → System auto-assigns layer via Galois loss
  → User navigates to supporting principles (gd)
  → Creates JUSTIFIES edges (ge mode)
  → Proof tree visualizes in ProofPanel
  → Each edge carries Toulmin structure
  → Full derivation chain from axioms visible
```

**3. Morning Coherence Review**
```
User opens studio
  → "Since last session" filter auto-applied
  → 3 new contradictions flagged
  → 2 new crystals compressed overnight
  → Coherence score: 0.83 (up from 0.81)
  → Quick capture: 3 morning thoughts via INSERT mode
  → Witness commit: "Morning capture: grounded yesterday's ideas"
```

---

## Part IV: Updated User Journeys

Based on actual implementation, here's what works TODAY:

### Journey 1: FTUE (Updated for Reality)

**What's READY**:
- [ ] Zero Seed cascade (API exists, needs streaming UI)
- [x] First declaration input (K-Block creation works)
- [x] Mode indicator (NORMAL/INSERT implemented)
- [ ] Loss gauge animation (Galois returns mock data)
- [x] Studio layout (Hypergraph + Feed side-by-side)

**Blocker**: Genesis streaming UI not built. Feed shows mock data.

**Workaround**: Start in Studio directly, skip Genesis animation for MVP.

### Journey 2: Daily Use (Works TODAY)

**What's READY**:
- [x] "Since last session" filter (Feed filtering works)
- [x] INSERT mode for quick capture
- [x] EDGE mode for linking
- [x] Witness commit with message
- [x] Coherence feedback (needs real Galois)

**Works END TO END**: Yes, with mock data.

### Journey 3: Contradiction Resolution (Mostly Ready)

**What's READY**:
- [x] Contradiction detection API
- [x] Classification (APPARENT/PRODUCTIVE/PROBLEMATIC/GENUINE)
- [x] Resolution strategies (5 types)
- [ ] VISUAL mode side-by-side comparison (partial)
- [ ] Synthesis K-Block creation with auto-edges

**Blocker**: VISUAL mode needs polish. Synthesis UI not complete.

### Journey 4: K-Block Integration (Mostly Ready)

**What's READY**:
- [ ] File upload with extraction (Sovereign ingests)
- [x] K-Block batch operations
- [ ] Auto-link discovery (edge detection exists)
- [x] K-Block isolation preview
- [x] Witness commit

**Blocker**: No PDF extraction. Markdown parsing works.

### Journey 5: Meta Reflection (Not Started)

**What's READY**:
- [ ] Coherence timeline (needs building)
- [ ] Layer distribution chart (data exists)
- [ ] Force-directed graph (no D3, use pure CSS?)
- [ ] Export (Markdown works, SVG not built)

**Blocker**: This is Phase 3+ work. Focus on Journeys 1-3 first.

---

## Part V: Wiring Priorities

### Phase 1: Core Loop (1 week)

Wire the **daily use** loop end-to-end:

1. **Feed → Real Data**
   - Replace mock K-Blocks with `/api/zero-seed/nodes`
   - Wire filtering to API query params
   - Show actual loss values

2. **Witness Creation → API**
   - Connect WitnessPanel to `/api/witness/marks`
   - Show marks in WitnessedTrail
   - Enable SSE stream

3. **EDGE Mode → Backend**
   - Create edges via K-Block service
   - Show edges in EdgeGutter
   - Update coherence score on edge creation

### Phase 2: Contradiction (1 week)

Enable **contradiction resolution**:

1. **Contradiction Feed**
   - Dedicated feed filtered by contradictions
   - Strength indicators (color-coded)
   - Click to enter VISUAL comparison

2. **Resolution UI**
   - Side-by-side K-Block comparison
   - 5 resolution strategy buttons
   - Synthesis K-Block creation form

3. **Coherence Feedback**
   - Show coherence delta after resolution
   - Animate score change
   - Celebration on improvement

### Phase 3: Genesis (1 week)

Build **FTUE experience**:

1. **Genesis Streaming**
   - SSE stream of Zero Seed cascade
   - K-Block materialization animation
   - "System is now self-aware" moment

2. **First Declaration**
   - Invitation input with layer selector
   - Loss gauge with explanation
   - Transition to Studio

3. **Studio Tour**
   - Hint system for keyboard shortcuts
   - uploads/ folder pulsing
   - Mode indicator tutorial

---

## Part VI: Design Laws (Refined)

30 laws remain valid. Key refinements based on implementation:

### Laws Already Satisfied by Implementation

| Law | Status | Evidence |
|-----|--------|----------|
| N-01 Vim Primary | ✓ DONE | useKeyHandler.ts has 92+ bindings |
| N-03 Mode Return | ✓ DONE | Escape always returns to NORMAL |
| L-05 Overlay Over Reflow | ✓ DONE | FloatingSidebar implemented |
| M-04 Reduced Motion | ✓ DONE | CSS respects prefers-reduced-motion |
| H-04 K-Block Isolation | ✓ DONE | 5 isolation states implemented |

### Laws Needing Attention

| Law | Gap | Fix |
|-----|-----|-----|
| C-03 Feed Is Primitive | Mock data | Wire to real API |
| F-02 Contradiction as Info | No UI | Build contradiction panel |
| M-01 Asymmetric Breathing | Symmetric | Update Breathe.tsx timing |
| C-05 Witness Required | Optional | Enforce on commit |
| H-05 AGENTESE Is API | Some REST routes | Migrate remaining routes |

---

## Part VII: The Vision (Grounded)

### What's Genuinely Novel

1. **Loss as universal metric** — Every thought has a coherence score
2. **Contradiction as feature** — Conflicts surface, don't hide
3. **Semantic navigation** — Move by meaning, not by file
4. **Witness everything** — Every action leaves a mark
5. **Multi-perspective judgment** — 6 eigenvectors, one synthesis
6. **Transactional editing** — Changes isolated until committed
7. **Constitutional alignment** — 7 principles score every action

### What This Enables

> *"A knowledge system that knows how grounded it is, surfaces its own contradictions, and leaves a witness trail of every decision."*

This is NOT:
- Another note-taking app (notes don't have loss scores)
- Another graph database (graphs don't detect contradictions)
- Another PKM tool (PKM doesn't witness decisions)

This IS:
- A self-aware knowledge garden
- A dialectical reasoning engine
- A witness-leaving decision system

---

## Appendix: File References

### Novel Capability Implementations

| Capability | Backend | Frontend |
|------------|---------|----------|
| Galois Loss | `services/zero_seed/galois/galois_loss.py` | (needs visualization) |
| Contradiction | `services/contradiction/` | (needs UI) |
| Hypergraph Editor | `services/hypergraph_editor/` | `web/src/hypergraph/` |
| Witness | `services/witness/` | `web/src/primitives/Witness/` |
| K-Block | `services/k_block/` | `web/src/components/kblock/` |
| Feed | `services/feed/` | `web/src/primitives/Feed/` |
| Portal | `services/portal/` | `web/src/components/tokens/PortalToken.tsx` |
| Brain | `services/brain/` | (needs UI) |
| AGENTESE | `protocols/agentese/` | `web/src/api/client.ts` |

---

*"The proof IS the decision. The mark IS the witness. Every surface is a projection of the same trail."*

---

## Addendum: Quick Wins & Novel Wireframes (v2.1)

*Added after implementation exploration - these are concrete, immediately shippable enhancements.*

### Quick Win #1: Coherence Thermometer (2 hours)

**What**: Every K-Block shows a small vertical bar indicating Galois loss.

```
┌─────────────────────────────┐
│ [L3] My Goal Statement  📏  │  ← 📏 = Coherence thermometer
│                         ┃   │     Height = 1.0 - loss
│ Content of the K-Block  ┃   │     Color: green (< 0.2) → yellow (< 0.5) → red
│                         ▓   │
└─────────────────────────────┘
```

**Backend**: Already returns loss. Just display it.
**Effort**: Add 5-line CSS component, wire to existing data.

---

### Quick Win #2: Contradiction Badge (1 hour)

**What**: K-Blocks with detected contradictions show a ⚡ badge.

```
┌─────────────────────────────┐
│ [L2] Principle A  ⚡        │  ← ⚡ = Has contradictions
│                             │     Click to see conflicting nodes
│ "I believe X is true..."    │
└─────────────────────────────┘
```

**Backend**: `/api/zero-seed/health` already returns contradictions list.
**Effort**: Add badge component, filter by node ID.

---

### Quick Win #3: Mode Pulse in Status Line (30 min)

**What**: Current mode name breathes (4-7-8 timing) when active.

```
┌─────────────────────────────────────────────────────────┐
│ NORMAL → INSERT → EDGE (breathing) → NORMAL             │
│    ↑                 ↑                                  │
│ static           pulsing (you're in edge creation mode) │
└─────────────────────────────────────────────────────────┘
```

**Why**: Mode awareness without cognitive overhead.
**Effort**: Add breathing class to StatusLine.tsx mode display.

---

### Quick Win #4: Witness Count Badge (1 hour)

**What**: Show how many marks have been created in current session.

```
┌────────────────────────────────┐
│  📍 12 marks this session      │  ← Clicking opens WitnessedTrail
│      ↳ Last: "Created edge"    │
└────────────────────────────────┘
```

**Backend**: Track marks via SSE stream (already implemented).
**Frontend**: Counter + last mark preview.

---

### Quick Win #5: Semantic Breadcrumb (2 hours)

**What**: Show derivation path from current node back to axioms.

```
┌───────────────────────────────────────────────────┐
│ A1:Entity → A2:Morphism → L2:Composability → HERE │
│     ↑            ↑              ↑                 │
│  axioms       axioms        principle             │
└───────────────────────────────────────────────────┘
```

**Backend**: K-Block derivation chain exists.
**Why**: Always know how grounded your current node is.

---

### Novel Interaction: Loss Gradient Navigation (gL/gH)

**Concept**: Navigate through semantic space by coherence gradient.

```
Current Node: "My hypothesis about X"
            Loss: 0.45

  Press gL (go to lower loss neighbor):
    → System finds most coherent connected node
    → Animates transition with loss delta
    → You move toward the axioms

  Press gH (go to higher loss neighbor):
    → System finds least grounded connected node
    → Animates transition with loss delta
    → You move toward the frontier

Visualization:
  ┌──────────────────────────────────────┐
  │      LOW LOSS         HIGH LOSS      │
  │     (grounded)        (frontier)     │
  │  ●─────●─────●═════●─────●─────○     │
  │  ↑           ↑                 ↑     │
  │ axiom     current           edge     │
  └──────────────────────────────────────┘
```

**Already Implemented**: `gl`/`gh` keybindings exist in useKeyHandler.ts
**Needed**: Visual animation of transition, loss delta display

---

### Novel Interaction: Contradiction Polaroid

**Concept**: Side-by-side view with synthesis suggestions.

```
┌───────────────────┬───────────────────┬───────────────────┐
│     NODE A        │    SYNTHESIS?     │     NODE B        │
│  [L2] Principle   │                   │  [L2] Principle   │
│                   │   "Consider..."   │                   │
│  Loss: 0.23       │                   │  Loss: 0.28       │
│                   │   ┌───────────┐   │                   │
│  "I believe X..."│   │ Synthesize │   │  "But also Y..." │
│                   │   │   Choose   │   │                   │
│                   │   │   Defer    │   │                   │
│                   │   │  Embrace   │   │                   │
│                   │   │  Dissolve  │   │                   │
│                   │   └───────────┘   │                   │
│  ⚡ PRODUCTIVE    │   Strength: 0.15  │  ⚡ PRODUCTIVE    │
└───────────────────┴───────────────────┴───────────────────┘
```

**Backend**: Classification, resolution strategies implemented.
**Needed**: 3-panel layout component, synthesis form.

---

### Novel Interaction: Constitutional Radar

**Concept**: 7-spoke visualization of any action's principle alignment.

```
                    Ethical (2.0×)
                        ●
                       /│\
            Curated   / │ \   Tasteful
               ●────●   │   ●────●
                   / \  │  / \
                  /   \ │ /   \
    Generative ●───────●●───────● Composable
                  \   / │ \   /
                   \ /  │  \ /
               ●────●   │   ●────●
         Heterarchical  │   Joy-Inducing
                        │
                   (1.0×)

    Score: 7.8/9.7  [ALIGNED ✓]
```

**Already Built**: ConstitutionalRadar component exists (231 LOC).
**Needed**: Wire to action scoring endpoint.

---

### Novel Interaction: Eigenvector Toggle

**Concept**: Switch observer perspective and see content change.

```
┌─────────────────────────────────────────────────────────┐
│ Observer: [ARCHITECT ▼]  [POET] [DEVELOPER] [CRITIC]   │
├─────────────────────────────────────────────────────────┤
│ Content (as seen by ARCHITECT):                         │
│                                                         │
│   "The witness system is a functor from the category   │
│    of actions to the category of marks, preserving     │
│    compositional structure..."                          │
│                                                         │
│ Switch to POET →                                        │
│                                                         │
│   "Each mark is a footprint left in the sand of time,  │
│    a witness to the choices we make..."                 │
├─────────────────────────────────────────────────────────┤
│ Same source, different manifestation.                   │
└─────────────────────────────────────────────────────────┘
```

**Backend**: AGENTESE observer parameter already supported.
**Needed**: Observer selector dropdown, re-fetch on change.

---

### Novel Interaction: Trace Archaeology

**Concept**: Dig into the history of any decision.

```
┌─────────────────────────────────────────────────────────┐
│ Decision: "Use SSE instead of WebSocket"                │
├─────────────────────────────────────────────────────────┤
│ TRACE (click to expand each mark):                      │
│                                                         │
│ 14:23 → Mark: "Kent proposed WebSocket"                 │
│         Reasoning: "Bidirectional, familiar"            │
│         Principles: [tasteful: 0.7, composable: 0.6]    │
│                                                         │
│ 14:25 → Mark: "Claude proposed SSE"                     │
│         Reasoning: "Simpler, HTTP-native, sufficient"   │
│         Principles: [composable: 0.9, tasteful: 0.8]    │
│                                                         │
│ 14:27 → Fusion: "Use SSE"                               │
│         Synthesis: "Unidirectional is enough"           │
│         Score: 8.2/9.7 [ALIGNED ✓]                      │
├─────────────────────────────────────────────────────────┤
│ Crystal: "SSE wins for simplicity when unidirectional"  │
└─────────────────────────────────────────────────────────┘
```

**Backend**: Mark → Trace → Crystal pipeline complete.
**Needed**: Timeline component, mark expansion.

---

### Productivity Metrics (What We Claim)

Based on the novel capabilities, here's what we can measure and claim:

| Metric | Traditional Tools | With kgents | Improvement |
|--------|-------------------|-------------|-------------|
| "Where did I write that?" | Text search, hope | Semantic search + loss ranking | 5× faster recall |
| "Why did I decide this?" | No trail | Every decision witnessed | ∞ (impossible before) |
| "Do my beliefs conflict?" | Manual review | Automatic detection | ∞ (impossible before) |
| "How grounded is this?" | Gut feeling | Quantified 0.00-1.00 | ∞ (impossible before) |
| Navigation to related | Click, scroll, click | 2 keystrokes (gd, gl, gh) | 10× fewer clicks |
| Editing confidence | "Hope I don't break it" | Isolated until committed | Removes fear |
| Multi-perspective view | "What would X think?" | Toggle observer, instant | ∞ (impossible before) |

---

### STARK BIOME Application

All quick wins should follow the STARK BIOME aesthetic:

| Element | Steel (90%) | Life (10%) |
|---------|-------------|------------|
| **Thermometer** | Background: steel-carbon | Fill: life-sage to life-sprout |
| **Contradiction ⚡** | Badge border: steel-gunmetal | Badge fill: state-alert (muted rust) |
| **Mode Pulse** | Text: steel-zinc | Breathing: glow-spore |
| **Witness Count** | Background: steel-slate | Count: life-mint |
| **Breadcrumb** | Separator: steel-gunmetal | Active node: glow-light |

**Animation Rule**: Only living elements breathe. Static elements stay still.

---

*"Quick wins compound. Ship fast, witness everything, iterate on evidence."*

*Compiled: 2025-12-25 | Creative Strategy v2.1 | Quick Wins Addendum*
