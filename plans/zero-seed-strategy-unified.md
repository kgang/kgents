# Zero Seed Strategy: The Unified Vision

> *"The act of declaring, capturing, and auditing your decisions is itself a radical act of self-transformation."*

**Version**: 3.0 (Unified)
**Date**: 2025-12-25
**Status**: AUTHORITATIVE - Supersedes all previous strategy documents
**Supersedes**:
- `zero-seed-genesis-grand-strategy.md` (DEPRECATED)
- `zero-seed-creative-strategy.md` (DEPRECATED)
- `zero-seed-creative-strategy-v2.md` (DEPRECATED)

---

## Epigraph

```
From nothing, the seed.
From the seed, the axioms.
From the axioms, the layers.
From the layers, the contradictions.
From the contradictions, the self.

This is not a product.
This is a mirror that writes back.
```

---

## Executive Summary

This document defines the **complete Zero Seed Genesis strategy** for kgents - a self-justifying, self-auditing knowledge garden. It consolidates:

1. **Core Architecture** - The Five Pillars and Four Design Laws
2. **Observable Entities** - K-Blocks, Edges, Marks, and Crystals
3. **User Journeys** - Six complete flows from FTUE to meta-reflection
4. **Implementation Status** - Current state with verified percentages
5. **Validation Framework** - 30 testable design laws

**The Unified Insight**: Every user action produces a **Witness Trail** that is observable through three projections:
- **Hypergraph Editor** = Witness trail as graph navigation
- **Portal Tokens** = Witness trail as document expansion
- **Constitutional Chat** = Witness trail as dialogue history

These are NOT three separate systems. They are three **projections of the same morphism**.

---

## Table of Contents

1. [Part I: Core Architecture](#part-i-core-architecture)
2. [Part II: Observable Entities](#part-ii-observable-entities)
3. [Part III: User Journeys](#part-iii-user-journeys)
4. [Part IV: Implementation Status](#part-iv-implementation-status)
5. [Part V: Validation Framework](#part-v-validation-framework)

---

# Part I: Core Architecture

## 1.1 The Five Pillars

```
+---------------------------------------------------------------------------+
|                         THE FIVE PILLARS                                   |
+---------------------------------------------------------------------------+
|                                                                           |
|  1. FEED AS PRIMITIVE                                                     |
|     The chronological truth stream. Algorithmic. Principles-aligned.      |
|     Users create feedback systems WITH the feed.                          |
|                                                                           |
|  2. K-BLOCK AS INCIDENTAL ESSENTIAL                                       |
|     Theoretically decouple-able. Pragmatically indispensable.             |
|     The surface for organizing IDEAS on linear media.                     |
|                                                                           |
|  3. SOVEREIGN UPLOADS                                                     |
|     External content enters through staging.                              |
|     Analysis + connection on deliberate integration.                      |
|                                                                           |
|  4. HETERARCHICAL TOLERANCE                                               |
|     Cross-layer edges allowed. Incoherence tolerated.                     |
|     System adapts to user, not user to system.                            |
|                                                                           |
|  5. CONTRADICTION AS FEATURE                                              |
|     Surface. Interrogate. Transform.                                      |
|     Fail-fast epistemology. Always in flux.                               |
|                                                                           |
+---------------------------------------------------------------------------+
```

## 1.2 The Four Design Laws (Immutable)

### LAW 1: Feed Is Primitive

```python
@design_law
class FeedIsPrimitive:
    """
    The feed is not a view of data.
    The feed IS the primary interface.

    Feeds are:
    - Chronological truth streams
    - Filterable by lens (layer, loss, author, principle)
    - Algorithmic (attention + principles alignment)
    - Recursive (users create feedback systems with feeds)

    A feed without filters is the raw cosmos.
    A feed with filters is a perspective.
    Multiple feeds = multiple selves.
    """
    immutable = True
    layer = 1  # Axiom level
```

### LAW 2: K-Block Incidental Essential

```python
@design_law
class KBlockIncidentalEssential:
    """
    K-Blocks are theoretically decouple-able from kgents.
    K-Blocks are pragmatically essential to kgents.

    This tension is DESIGNED, not accidental.

    K-Blocks exist at the service/application layer.
    K-Blocks organize IDEAS and CONCEPTS.
    K-Blocks provide linear surfaces for collaboration.

    The primitive underneath is the trace.
    K-Blocks are syntactic sugar over traces.
    But sugar that makes the medicine go down.
    """
    immutable = True
    layer = 2  # Value level (not axiom - could be replaced)
```

### LAW 3: Linear Adaptation

```python
@design_law
class LinearAdaptation:
    """
    The system adapts to user wants and needs.
    The system does NOT change behavior against user will.

    Inspired by Linear design philosophy:
    - Product shapes to user, not user to product
    - Nonsense added by user does not spread
    - Performance unaffected by incoherent input
    - Common use cases prioritized for JOY

    The user may add arbitrary nonsense.
    The system metabolizes or quarantines it.
    Never punishes. Never lectures. Never blocks.
    """
    immutable = True
    layer = 2  # Value level
```

### LAW 4: Contradiction Surfacing

```python
@design_law
class ContradictionSurfacing:
    """
    Surfacing, interrogating, and systematically interacting
    with personal beliefs, values, and contradictions is
    ONE OF THE MOST IMPORTANT PARTS of the system.

    Approach: Fail-fast epistemology.

    The user should KNOW:
    - Evidence shows epistemological/ontological inconsistency
    - Level can be 0, can be huge, will definitely be in flux
    - This is INFORMATION, not JUDGMENT

    The system is a mirror.
    Mirrors don't tell you to change.
    Mirrors show you what is.
    """
    immutable = True
    layer = 1  # Axiom level - core to identity
```

## 1.3 The Hypergraph Observer Pattern (NEW)

The system is built around observable entities that emit events through a unified witness trail:

```
+------------------+     +------------------+     +------------------+
|    USER ACTION   | --> |   WITNESS MARK   | --> |    PROJECTION    |
+------------------+     +------------------+     +------------------+
                              |
                              v
+-----------------------------------------------------------------------+
|                         OBSERVABLE ENTITIES                            |
+-----------------------------------------------------------------------+
|                                                                       |
|  K-BLOCK        EDGE          MARK          CRYSTAL                   |
|  -------        ----          ----          -------                   |
|  id             source        id            id                        |
|  layer          target        action        compression_level         |
|  loss           kind          evidence      mood_vector               |
|  content        weight        timestamp     insight                   |
|  isolation      justification principles    parent_trace              |
|  derivation     witness_mark  score         galois_witness            |
|                                                                       |
+-----------------------------------------------------------------------+
                              |
                              v
+-----------------------------------------------------------------------+
|                         THREE PROJECTIONS                              |
+-----------------------------------------------------------------------+
|                                                                       |
|  HYPERGRAPH EDITOR    PORTAL TOKENS        CONSTITUTIONAL CHAT        |
|  -----------------    -------------        ------------------         |
|  Graph navigation     Document expansion   Dialogue history           |
|  Edge traversal       Semantic links       Decision archaeology       |
|  Loss gradient        Inline previews      Trace playback             |
|  Modal editing        Cure system          Synthesis suggestions      |
|                                                                       |
+-----------------------------------------------------------------------+
```

### Observable Event Types

| Entity | Event | Payload | Subscribers |
|--------|-------|---------|-------------|
| K-Block | `kblock.created` | id, layer, loss, content_hash | Feed, Graph, Timeline |
| K-Block | `kblock.modified` | id, delta, new_loss | Graph, Contradiction |
| K-Block | `kblock.committed` | id, witness_message | Trace, Crystal |
| Edge | `edge.created` | source, target, kind, weight | Graph, Coherence |
| Edge | `edge.justified` | id, justification | Trace, Proof |
| Edge | `edge.contradicted` | id, conflicting_edge | Contradiction |
| Mark | `mark.created` | id, action, evidence | Trail, Timeline |
| Mark | `mark.compressed` | mark_ids, crystal_id | Crystal, Archive |
| Crystal | `crystal.formed` | id, compression_level, insight | Memory, Search |

---

# Part II: Observable Entities

## 2.1 K-Blocks (L0-L7)

K-Blocks are the atomic units of the knowledge graph, organized into 8 layers:

| Layer | Name | Loss Range | Description | Example |
|-------|------|------------|-------------|---------|
| L0 | System | 0.000 | Zero Seed genesis | "Everything is a node" |
| L1 | Axiom | 0.001-0.010 | Self-evident truths | "Loss measures truth" |
| L2 | Value | 0.010-0.100 | Derived principles | "Composability over complexity" |
| L3 | Goal | 0.100-0.400 | Aspirational declarations | "Build a knowledge garden" |
| L4 | Spec | 0.200-0.500 | Specifications | "K-Block isolation protocol" |
| L5 | Impl | 0.300-0.600 | Implementations | "services/k_block/core.py" |
| L6 | Reflect | 0.400-0.700 | Meta-observations | "Contradiction detected" |
| L7 | Void | 0.500-1.000 | Serendipity, drafts | "What if we..." |

### K-Block Isolation States

```
PRISTINE -----> DIRTY -----> STALE
    |             |            |
    |             v            v
    |        CONFLICTING <-- ENTANGLED
    |             |
    +-------------+
          |
          v
      [COMMIT with Witness]
```

| State | Description | UI Indicator |
|-------|-------------|--------------|
| PRISTINE | No local changes | Solid border |
| DIRTY | Uncommitted changes | Dashed border |
| STALE | Remote changes pending | Amber glow |
| CONFLICTING | Merge required | Red pulse |
| ENTANGLED | Dependencies changed | Blue glow |

## 2.2 Edges (by Kind)

Edges are first-class citizens with their own properties and observability:

### Edge Kinds

| Kind | Direction | Required Fields | UI Symbol |
|------|-----------|-----------------|-----------|
| `GROUNDS` | L1 -> L2 | justification (required) | -- |
| `JUSTIFIES` | L2 -> L3 | justification (suggested) | --> |
| `IMPLEMENTS` | L4 -> L5 | - | ==> |
| `CONTRADICTS` | any -> any | justification (required), strength | <-> |
| `SUPERSEDES` | any -> any | justification (required) | >>> |
| `DERIVES_FROM` | any -> any | - | <- |
| `EXTENDS` | same layer | - | + |
| `ANALYZES` | L6 -> any | - | @ |

### Edge Policy Levels

```python
class EdgePolicyLevel:
    STRICT = {
        # MUST have justification - blocked without
        EdgeKind.CONTRADICTS,
        EdgeKind.SUPERSEDES,
    }
    SUGGESTED = {
        # SHOULD have justification - flagged without
        EdgeKind.GROUNDS,
        EdgeKind.JUSTIFIES,
    }
    OPTIONAL = {
        # MAY have justification - not flagged
        EdgeKind.IMPLEMENTS,
        EdgeKind.EXTENDS,
        EdgeKind.DERIVES_FROM,
        EdgeKind.ANALYZES,
    }
```

### Edge Discovery (NEW)

The system actively discovers potential edges based on:

1. **Semantic similarity** - Embedding distance < 0.3
2. **Layer proximity** - Adjacent layers have natural edge potential
3. **Contradiction detection** - Super-additive loss: `L(A+B) > L(A) + L(B) + 0.1`
4. **Citation analysis** - Portal tokens create implicit edges
5. **Co-modification** - Files edited together are likely related

```
Edge Discovery Pipeline:
+----------+     +-------------+     +---------------+     +-----------+
| New Node | --> | Embedding   | --> | Candidate     | --> | User      |
| Created  |     | Computation |     | Edges Found   |     | Approval  |
+----------+     +-------------+     +---------------+     +-----------+
                                           |
                                           v
                                   +---------------+
                                   | Edge Strength |
                                   | Computation   |
                                   +---------------+
```

## 2.3 Marks (by Tag)

Marks are the atoms of the witness trail:

### Mark Tags (7 Principles)

| Tag | Keystroke | Principle | Evidence Type |
|-----|-----------|-----------|---------------|
| `mE` | `gw mE` | Ethical | Action + reasoning |
| `mG` | `gw mG` | Generative | Created content |
| `mT` | `gw mT` | Tasteful | Aesthetic decision |
| `mF` | `gw mF` | joyFul | Delight moment |
| `mJ` | `gw mJ` | Judgmental | Evaluation + criteria |
| `mV` | `gw mV` | Visceral | Felt sense capture |
| `mC` | `gw mC` | Composable | Composition operation |

### Mark Structure

```typescript
interface Mark {
  id: string;
  action: string;           // What happened
  evidence: Evidence;       // Proof of the action
  timestamp: DateTime;      // When
  principles: PrincipleScore[];  // 7 scores (0-1)
  constitutional_score: number;  // Weighted sum (0-9.7)
  parent_trace?: TraceId;   // Optional trace linkage
  tags: MarkTag[];          // Categorical labels
}

interface Evidence {
  before?: Snapshot;        // State before action
  after?: Snapshot;         // State after action
  delta?: ContentDelta;     // What changed
  reasoning?: string;       // Why (optional)
  external_ref?: string;    // Link to external system
}
```

### Mark Archaeology (NEW)

Marks can be queried and explored through time:

```
Mark Archaeology Commands:
  :marks today           - All marks from today
  :marks @ethical        - Marks tagged ethical
  :marks "decision"      - Marks matching text
  :marks for:kb123       - Marks for specific K-Block
  :marks trace:tr456     - Marks in specific trace
  :marks --json          - Machine-readable output
```

## 2.4 Crystals (Hierarchy)

Crystals are compressed wisdom from accumulated marks:

### Compression Levels

| Level | Name | Marks Required | Retention |
|-------|------|----------------|-----------|
| 0 | DUST | 1-5 | Full detail |
| 1 | PEBBLE | 6-20 | Key moments |
| 2 | STONE | 21-100 | Patterns only |
| 3 | MOUNTAIN | 100+ | Distilled wisdom |

### Crystal Structure

```typescript
interface Crystal {
  id: string;
  compression_level: CompressionLevel;
  source_marks: MarkId[];      // What it compressed
  insight: string;             // Extracted wisdom
  mood_vector: number[];       // Aggregated emotional signature
  galois_witness: GaloisWitness;  // Coherence proof
  created_at: DateTime;
  parent_trace: TraceId;
}

interface GaloisWitness {
  loss_before: number;         // Pre-compression loss
  loss_after: number;          // Post-compression loss
  compression_ratio: number;   // How much was compressed
  information_preserved: number;  // 0-1 fidelity measure
}
```

---

# Part III: User Journeys

Six complete journeys with mode transitions, delight moments, and observable entities.

## Journey 1: FTUE - Witness Genesis (90 seconds)

**Trigger**: First-time user lands on kgents

### Flow

| Phase | Time | User Action | System Response | Observable Events |
|-------|------|-------------|-----------------|-------------------|
| Genesis Load | 0-3s | Lands on `/` | "kgents is initializing..." | - |
| Zero Seed Cascade | 3-15s | Watches | 8 axioms stream, loss gauges animate | `kblock.created` x8 |
| Ground Formation | 15-25s | Continues watching | L1 grounds derive, edges draw | `edge.created` x12 |
| Invitation | 25-30s | - | "What matters most?" input appears | - |
| First Declaration | 30-60s | Types first goal | K-Block materializes, L3 badge | `kblock.created`, `mark.created` |
| Studio Transition | 60-90s | Clicks "Continue" | Feed + Explorer, NORMAL mode | - |

### Mode Transitions
```
WITNESS (implied) --> NORMAL
```

### Delight Moments
- "The system is now self-aware" after Zero Seed
- Confetti burst on first K-Block
- uploads/ folder pulses amber

### Exit State
- Witnessed genesis
- Created first declaration
- Entered Studio with context

---

## Journey 2: Daily Capture (5 minutes)

**Trigger**: Returning user at morning

### Flow

| Phase | User Action | System Response | Observable Events |
|-------|-------------|-----------------|-------------------|
| Landing | Navigates to `/studio` | "Since last session" filter | - |
| Quick Scan | Scrolls with `j` | New items highlighted | - |
| INSERT Mode | Presses `i` | Mode: NORMAL -> INSERT | - |
| Rapid Declaration | Types 3 thoughts | K-Blocks materialize | `kblock.created` x3 |
| Quick Link | Presses `e` (EDGE) | Creates enabling edge | `edge.created` |
| Witness Commit | Presses `Esc`, `:w` | Auto-commit prompt | `kblock.committed` x3, `mark.created` |

### Mode Transitions
```
NORMAL --> INSERT --> EDGE --> NORMAL --> COMMAND --> NORMAL
```

### Observable Delta
- +3 K-Blocks
- +1 Edge
- +0.03 coherence
- 1 trace with 4 marks

---

## Journey 3: Edge Discovery (10 minutes) - NEW

**Trigger**: System notification "12 potential edges discovered"

### Flow

| Phase | User Action | System Response | Observable Events |
|-------|-------------|-----------------|-------------------|
| Navigate | Types `:edges pending` | Edge discovery panel opens | - |
| Batch Review | Scans candidates | Strength scores, justifications shown | - |
| Quick Accept | Clicks "Accept similar" | 8 edges with strength > 0.7 accepted | `edge.created` x8 |
| Manual Review | Reviews remaining 4 | Side-by-side comparison | - |
| Add Justification | Types justification | Edge promoted to JUSTIFIED | `edge.justified` |
| Reject False | Clicks "Dismiss" | Edge marked as dismissed | - |
| Coherence Update | Watches meter | Coherence: 0.76 -> 0.82 | `mark.created` |

### Mode Transitions
```
NORMAL --> COMMAND --> VISUAL --> NORMAL
```

### Observable Delta
- +9 edges (8 auto + 1 manual)
- 3 dismissed candidates
- +0.06 coherence
- 1 trace with justification marks

### New UI Component: Edge Discovery Panel

```
+-----------------------------------------------------------------------+
|  EDGE DISCOVERY                                        [Accept All 0.7+] |
+-----------------------------------------------------------------------+
| Source          | Target          | Kind      | Strength | Justify?  |
|-----------------|-----------------|-----------|----------|-----------|
| L2:Composability| L3:Modular goal | JUSTIFIES | 0.89     | [Add]     |
| L3:API spec     | L5:api.py       | IMPLEMENTS| 0.95     | -         |
| L2:Ethics       | L2:Joy          | CONTRADICTS| 0.34    | [Required]|
+-----------------------------------------------------------------------+
| Showing 12 candidates | Auto-accept threshold: 0.7 | [Dismiss All <0.3] |
+-----------------------------------------------------------------------+
```

---

## Journey 4: Mark Archaeology (15 minutes) - NEW

**Trigger**: User wants to understand how a decision evolved

### Flow

| Phase | User Action | System Response | Observable Events |
|-------|-------------|-----------------|-------------------|
| Select Node | Clicks K-Block | Context menu appears | - |
| View History | Clicks "Show marks" | Timeline opens | - |
| Expand Mark | Clicks first mark | Evidence panel shows before/after | - |
| Filter by Tag | Clicks `@ethical` | Only ethical marks shown | - |
| Trace Navigation | Clicks "View trace" | Full trace timeline | - |
| Crystal Preview | Scrolls to crystal | Compressed insight shown | - |
| Export | Clicks "Export journey" | Markdown + JSON download | `mark.created` (export) |

### Mode Transitions
```
NORMAL --> COMMAND --> WITNESS (read) --> NORMAL
```

### New UI Component: Mark Timeline

```
+-----------------------------------------------------------------------+
|  MARK ARCHAEOLOGY: "Use SSE instead of WebSocket"                      |
+-----------------------------------------------------------------------+
| TIME     | ACTION              | EVIDENCE                    | TAGS  |
|----------|---------------------|------------------------------|-------|
| 14:23    | Kent proposed       | "Bidirectional, familiar"   | @V    |
|          | WebSocket           | Score: 6.2/9.7              |       |
|----------|---------------------|------------------------------|-------|
| 14:25    | Claude proposed SSE | "Simpler, sufficient"       | @C @T |
|          |                     | Score: 8.1/9.7              |       |
|----------|---------------------|------------------------------|-------|
| 14:27    | Fusion: Use SSE     | SYNTHESIS: Unidirectional   | @E @G |
|          |                     | enough, simpler ops         |       |
|----------|---------------------|------------------------------|-------|
|          |                     |                              |       |
|  CRYSTAL | "SSE wins for simplicity when unidirectional flow suffices"  |
|          | Compression: PEBBLE | Mood: [Confident, Resolved]           |
+-----------------------------------------------------------------------+
```

---

## Journey 5: Contradiction Resolution (30 minutes)

**Trigger**: "3 unresolved contradictions detected" notification

### Flow

| Phase | User Action | System Response | Observable Events |
|-------|-------------|-----------------|-------------------|
| Navigate | Types `/contradictions` | Feed filters to 3 pairs | - |
| Select Pair | Clicks first pair | VISUAL mode: side-by-side | - |
| Analyze | Reviews both nodes | Strength indicator: 0.34 | - |
| Synthesize | Creates new principle | K-Block + auto-edges | `kblock.created`, `edge.created` x2 |
| Coherence | Watches update | 0.76 -> 0.81 | `mark.created` |
| Refine | Edits second K-Block | Loss 0.34 -> 0.19 | `kblock.modified` |
| Productive | Marks third as creative | Both get tension badge | `edge.justified` |
| Witness | Presses `gw` | Commit with celebration | `kblock.committed`, `crystal.formed` |

### Mode Transitions
```
NORMAL --> COMMAND --> VISUAL --> INSERT --> NORMAL --> WITNESS --> NORMAL
```

### Contradiction Types

| Type | Strength | Recommended Action |
|------|----------|-------------------|
| APPARENT | < 0.2 | Scope (different contexts) |
| PRODUCTIVE | 0.2-0.4 | Embrace (creative tension) |
| PROBLEMATIC | 0.4-0.6 | Synthesize (find higher truth) |
| GENUINE | > 0.6 | Choose (decide which to keep) |

---

## Journey 6: Meta Reflection (10 minutes)

**Trigger**: User wants to review 2-week journey

### Flow

| Phase | User Action | System Response | Observable Events |
|-------|-------------|-----------------|-------------------|
| Navigate | Types `/meta` | Coherence journey graph | - |
| Scrub Timeline | Hovers data points | Tooltips show commits | - |
| Layer Analysis | Clicks tab | Pie chart: 48% principles | - |
| Breakthrough | Clicks badge | Dec 21 insight expanded | - |
| Story | Clicks "Tell my story" | System narrates journey | `mark.created` |
| Export | Clicks export | Markdown + SVG download | - |
| Reflect | Types reflection | Saves as L6 meta-note | `kblock.created` |

### Mode Transitions
```
NORMAL (read-only exploration)
```

### Meta Dashboard Panels

```
+-----------------------------------------------------------------------+
|  META: Your Coherence Journey                            [2 weeks]     |
+-----------------------------------------------------------------------+
|                                                                       |
|  COHERENCE OVER TIME                                                  |
|  1.0 |                                          ----*                 |
|      |                              ----*------*                       |
|  0.8 |              ----*------*----                                   |
|      |  ----*------*                                                  |
|  0.6 |                                                                |
|      +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+    |
|        Dec 11  Dec 14  Dec 17  Dec 20  Dec 23                         |
|                                         ^                             |
|                                         BREAKTHROUGH                  |
+-----------------------------------------------------------------------+
|  LAYER DISTRIBUTION        |  RECENT CRYSTALS                        |
|  [L1] ####  12%            |  - "SSE over WS for simplicity"        |
|  [L2] ########  24%        |  - "Composition beats inheritance"     |
|  [L3] ######  18%          |  - "Joy is earned, not given"          |
|  [L4] ##########  30%      |                                         |
|  [L5] ####  12%            |  [View all 23 crystals]                 |
|  [L6] ##  4%               |                                         |
+-----------------------------------------------------------------------+
```

---

# Part IV: Implementation Status

Updated 2025-12-25 based on codebase exploration.

## 4.1 Backend Status

| System | Completion | Tests | Ready for UI? | Notes |
|--------|------------|-------|---------------|-------|
| **Zero Seed API** | 95% | 200+ | YES | PostgreSQL wiring needed |
| **K-Block Core** | 100% | 45+ | YES | All isolation states work |
| **Galois Loss** | 100% | 50+ | YES | Cache implemented |
| **Contradiction** | 100% | 40+ | YES | All 4 types classified |
| **Witness** | 98% | 678+ | YES | SSE ready |
| **Feed** | 90% | 30+ | PARTIAL | Needs K-Block metadata |
| **Brain** | 100% | 100+ | YES | Search + forage working |
| **Portal** | 95% | 50+ | YES | Cure system needs LLM |
| **Sovereign** | 85% | 40+ | YES | 4/9 integration steps TODO |
| **Heterarchy** | 100% | 38 | YES | All edge policies work |

## 4.2 Frontend Status

| Component | Completion | LOC | Needs |
|-----------|------------|-----|-------|
| **Hypergraph Editor** | 90% | 6,183 | Real data wiring |
| **Mode System (6 modes)** | 100% | 599 | - |
| **Feed** | 70% | 650 | API connection |
| **K-Block Editor** | 85% | 259 | Proof editing UI |
| **Witness UI** | 60% | 240 | Creation + timeline |
| **Edge Discovery** | 0% | - | NEW - needs building |
| **Mark Archaeology** | 0% | - | NEW - needs building |
| **Elastic Components** | 100% | 1,200+ | - |
| **Portal Tokens** | 90% | 300+ | Cure system |
| **Constitutional Radar** | 100% | 231 | Data connection |
| **SSE Streaming** | 80% | 200+ | Enable flags |

## 4.3 Gap Analysis

### Ready to Wire TODAY

| Frontend | Backend Endpoint | Status |
|----------|-----------------|--------|
| Feed | `/api/zero-seed/nodes` | Replace mock data |
| Witness creation | `/api/witness/marks` | Connect form |
| Decision stream | `/api/witness/fusion` | Enable polling |
| Brain search | `/api/agentese/self/memory/search` | Wire search bar |
| Contradiction feed | `/api/zero-seed/health` | Filter by contradictions |

### Needs Backend Work

| Feature | Missing | Priority |
|---------|---------|----------|
| Feed ranking | Attention tracking | HIGH |
| K-Block metadata | tags, created_by | HIGH |
| Real Galois loss | Mock returns 0.12-0.20 | MEDIUM |
| Portal curing | LLM integration | LOW |
| Edge Discovery panel | `/api/edges/candidates` | HIGH (NEW) |
| Mark timeline | `/api/marks/timeline` | HIGH (NEW) |

## 4.4 Implementation Phases (Revised)

### Phase 1: Core Loop (Week 1)
- [ ] Wire Feed to real API
- [ ] Enable Witness creation
- [ ] Connect EDGE mode to backend
- [ ] Add Edge Discovery endpoint

### Phase 2: Observability (Week 2)
- [ ] Build Edge Discovery panel
- [ ] Build Mark Archaeology timeline
- [ ] Enable SSE streaming
- [ ] Add real Galois loss computation

### Phase 3: Contradiction (Week 3)
- [ ] Contradiction feed filtering
- [ ] Resolution UI
- [ ] Synthesis K-Block creation
- [ ] Coherence delta animation

### Phase 4: Genesis (Week 4)
- [ ] Genesis streaming UI
- [ ] First declaration flow
- [ ] Studio tour hints

### Phase 5: Meta (Week 5)
- [ ] Coherence journey timeline
- [ ] Layer distribution analytics
- [ ] Export functionality
- [ ] Story narration

---

# Part V: Validation Framework

## 5.1 The 30 Design Laws

### Layout Laws (L-01 to L-05)

| ID | Name | Statement | Test |
|----|------|-----------|------|
| L-01 | Density-Content Isomorphism | Content detail maps to observer capacity | Spacious text > Compact text |
| L-02 | Three-Mode Preservation | Same affordances across all densities | Feature parity check |
| L-03 | Touch Target Invariance | >= 48px interactive elements on compact | Size assertion |
| L-04 | Tight Frame Breathing Content | Frame is steel, content glows | Color palette check |
| L-05 | Overlay Over Reflow | Navigation floats, doesn't push | Layout assertion |

### Navigation Laws (N-01 to N-05)

| ID | Name | Statement | Test |
|----|------|-----------|------|
| N-01 | Vim Primary Arrow Alias | j/k primary, arrows alias | Keybinding check |
| N-02 | Edge Traversal Not Directory | Navigate graph, not filesystem | Navigation test |
| N-03 | Mode Return to NORMAL | Escape always returns to NORMAL | Mode transition test |
| N-04 | Trail Is Semantic | Trail records edges, not positions | Trail content check |
| N-05 | Jump Stack Preservation | Jumps preserve return path | Stack depth test |

### Feedback Laws (F-01 to F-05)

| ID | Name | Statement | Test |
|----|------|-----------|------|
| F-01 | Multiple Channel Confirmation | 2+ channels for significant actions | Channel count check |
| F-02 | Contradiction as Information | Surface as info, not judgment | Tone analysis |
| F-03 | Tone Matches Observer | Archetype-aware messages | Persona mapping |
| F-04 | Earned Glow Not Decoration | Color on interaction, not default | Default state check |
| F-05 | Non-Blocking Notification | Status appears non-modally | Modal detection |

### Content Laws (C-01 to C-05)

| ID | Name | Statement | Test |
|----|------|-----------|------|
| C-01 | Five-Level Degradation | icon -> title -> summary -> detail -> full | Render level check |
| C-02 | Schema Single Source | Forms derive from Python contracts | Schema comparison |
| C-03 | Feed Is Primitive | Feed is first-class, not a view | Architecture check |
| C-04 | Portal Token Interactivity | Portals are interactive | Interaction test |
| C-05 | Witness Required for Commit | K-Block commits require witness | Commit flow test |

### Motion Laws (M-01 to M-05)

| ID | Name | Statement | Test |
|----|------|-----------|------|
| M-01 | Asymmetric Breathing | 4-7-8 timing, not symmetric | Animation timing check |
| M-02 | Stillness Then Life | Default still, animation earned | Default state check |
| M-03 | Mechanical Precision Organic Life | Mechanical for structure, organic for life | Animation style check |
| M-04 | Reduced Motion Respected | Respect prefers-reduced-motion | Media query check |
| M-05 | Animation Justification | Every animation has semantic reason | Documentation check |

### Coherence Laws (H-01 to H-05)

| ID | Name | Statement | Test |
|----|------|-----------|------|
| H-01 | Linear Adaptation | System adapts to user | Behavior consistency check |
| H-02 | Quarantine Not Block | High-loss quarantined, not rejected | Threshold behavior test |
| H-03 | Cross-Layer Edge Allowed | Distant layer edges allowed + flagged | Edge creation test |
| H-04 | K-Block Isolation | INSERT creates K-Block, changes isolated | Isolation state test |
| H-05 | AGENTESE Is API | Forms invoke AGENTESE, no REST routes | Route audit |

## 5.2 Verification Commands

```bash
# Run all design law tests
npm run test:design-laws

# Run specific category
npm run test:design-laws -- --category=layout

# Python backend coherence laws
cd impl/claude && uv run pytest -k test_coherence_law

# Full validation suite
kg compose --run "validate-spec"
```

## 5.3 Success Criteria

### Phase 1 Success (Core Loop)
- [ ] Feed shows real K-Blocks with loss values
- [ ] Witness marks created via UI
- [ ] Edges created via EDGE mode
- [ ] Edge Discovery shows >= 3 candidates

### Phase 2 Success (Observability)
- [ ] Edge Discovery panel accepts/rejects candidates
- [ ] Mark timeline shows history for any K-Block
- [ ] SSE events update UI in real-time
- [ ] Galois loss computes in < 100ms

### Phase 3 Success (Contradiction)
- [ ] Contradictions feed shows pairs with strength
- [ ] Resolution creates synthesis K-Block
- [ ] Coherence updates on resolution
- [ ] All 4 contradiction types handled

### Phase 4 Success (Genesis)
- [ ] Genesis streams 8 axioms in < 15s
- [ ] First K-Block created in < 60s
- [ ] Studio tour completes without confusion

### Phase 5 Success (Meta)
- [ ] Coherence timeline shows 2-week history
- [ ] Export produces valid Markdown + JSON
- [ ] Story narration feels personal

---

## The Grand Equation

```
+-----------------------------------------------------------------------------+
|                                                                             |
|                        THE GRAND EQUATION                                   |
|                                                                             |
|   kgents = ZeroSeed x Feed x KBlock x Heterarchy x Contradiction            |
|                                                                             |
|   where:                                                                    |
|                                                                             |
|   ZeroSeed     = Genesis + Axioms + DesignLaws                              |
|   Feed         = Time x Attention x Principles x Coherence                  |
|   KBlock       = Trace x Surface x Justification                            |
|   Heterarchy   = CrossLayer + Tolerance + Adaptation                        |
|   Contradiction = Detection x Surfacing x Resolution x Growth               |
|                                                                             |
|   And the fundamental law:                                                  |
|                                                                             |
|   Agency(X) = integral of Justification(X) dt                               |
|                                                                             |
|   An agent is the integral of its justifications over time.                 |
|   The more you justify, the more you ARE.                                   |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## Cross-References

| Document | Purpose |
|----------|---------|
| `spec/protocols/zero-seed.md` | Canonical Zero Seed v3.0 spec |
| `spec/protocols/k-block.md` | K-Block transactional spec |
| `spec/theory/galois-modularization.md` | Galois loss theory |
| `spec/principles/CONSTITUTION.md` | The 7+7 principles |
| `docs/skills/hypergraph-editor.md` | Editor usage guide |
| `NOW.md` | Current system state |

---

## Appendix: User Personas

Four distinct personas instantiate the kgents vision:

### Persona 1: Dr. Aisha Okonkwo - The Rigorous Skeptic
- **Archetype**: `developer` -> `creator`
- **Essence**: "Show me the proof, not the promise"
- **Coherence Tolerance**: Low (hates hand-wavy but respects void.*)
- **Primary Flows**: Proof construction, dialectic capture, coherence auditing

### Persona 2: Mx. River Castellanos - The Mycelial Thinker
- **Archetype**: `creator`
- **Essence**: "Let me tend the entanglement, not fight it"
- **Coherence Tolerance**: Maximum (thrives in void.*)
- **Primary Flows**: Hypnagogic capture, stigmergic discovery, serendipity

### Persona 3: Kenji Matsuda - The Craft Programmer
- **Archetype**: `developer`
- **Essence**: "Code should be legible like a theorem, executable like a blade"
- **Coherence Tolerance**: Moderate (types strict, runtime surprise)
- **Primary Flows**: Post-implementation audit, gotcha capture, CLI-native

### Persona 4: Lina Vasquez - The Executive Cartographer
- **Archetype**: `admin`
- **Essence**: "Show me the terrain so I can steer the ship"
- **Coherence Tolerance**: Low tolerance, high delegation
- **Primary Flows**: Strategic query, cross-team cartography, audit enforcement

---

*"The seed IS the garden."*

---

**Document Metadata**
- **Created**: 2025-12-25
- **Authors**: Kent Gang, Claude (Anthropic)
- **Status**: AUTHORITATIVE
- **Supersedes**: All previous strategy documents
- **Priority**: CRITICAL - This is the unified foundation
