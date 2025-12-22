# Witness Assurance UI: The Trust Surface

> *"The proof IS the decision. The mark IS the witness. The UI IS the trust surface."*

**Status:** Ready for Implementation
**Priority:** High
**Estimated Effort:** 4-5 sessions
**Dependencies:** `witness-assurance-protocol.md` (parent), Living Earth palette, Joy primitives
**Heritage:** MarkCard, Breathe, Shimmer, Living Earth palette

---

## The Core Insight

**Trust is not a badge—it's a living organism.**

The UI should not *display* trust. It should *grow* trust. Every artifact has a genealogy—from the prompt that conceived it, through the marks that witnessed it, to the proof that validates it. The UI makes this genealogy *navigable* and *alive*.

Most audit UIs are spreadsheets with status icons. Ours is a garden where:
- Healthy specs bloom
- Contested specs wilt
- Orphans appear as weeds at the edges
- The overall health is immediately visible

*"The persona is a garden, not a museum."* — The Mirror Test

---

## Design Principles

### 1. Accountability Lenses (Not Density Modes)

Every app has compact/comfortable/spacious. That's about pixels. We have **accountability lenses**—about *who you are and what you need*:

| Lens | What It Shows | Who It's For | Keyboard |
|------|---------------|--------------|----------|
| **Audit** | Full evidence chain, all levels, rebuttals prominent | External reviewers | `A` |
| **Author** | My marks, my contributions, what needs attention | Contributors | `U` |
| **Trust** | Confidence only, green/yellow/red at a glance | Executives/stakeholders | `T` |

This is *opinionated*. It says: we know there are three kinds of observers, and we designed for each.

### 2. Orphans Are First-Class Citizens

Orphans (artifacts without prompt lineage) aren't shameful—they're *unwitnessed*. Instead of hiding them in a warning bar, we create **L-∞: Orphan** as a legitimate evidence level:

```
┌─────────────────────────────────────────────────────────────────┐
│  L3: Economic Bet  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  (gold, rare)   │
├─────────────────────────────────────────────────────────────────┤
│  L2: Formal Proof  ███████████████░░░░░░░░░░░░░  (purple glow)  │
├─────────────────────────────────────────────────────────────────┤
│  L1: Automated Test ██████████████████████░░░░░  (green solid)  │
├─────────────────────────────────────────────────────────────────┤
│  L0: Human Mark    ████████████████████████████  (copper pulse) │
├─────────────────────────────────────────────────────────────────┤
│  L-1: TraceWitness ████████████████████████████  (cyan trace)   │
├─────────────────────────────────────────────────────────────────┤
│  L-2: PromptAncestor████████████████████████████ (sage origin)  │
├─────────────────────────────────────────────────────────────────┤
│  L-∞: Orphan       ████████████████████████████  (red/unknown)  │
└─────────────────────────────────────────────────────────────────┘
```

The UI *invites completion*, not *punishes existence*.

### 3. Trust Pulses Like a Heartbeat

No floating particles. No confetti. **Trust has a heartbeat.**

| Confidence | Pulse Behavior |
|------------|----------------|
| 0.0–0.3 | Flatline (no pulse) |
| 0.3–0.6 | Slow pulse (awakening) |
| 0.6–0.9 | Steady pulse (alive) |
| 0.9–1.0 | Strong pulse (thriving) |
| On increase | Accelerates briefly, then settles |
| On decrease | Slows, becomes irregular |

This is more *alive* and less *decorative*. Kent's anchor: *"daring, bold, creative, opinionated but not gaudy."*

### 4. The Garden View (Primary Dashboard)

The dashboard is not a spreadsheet—it's a **living garden**:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        The Witness Garden                       [A][U][T]
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│    🌳                      🌿         🌱                               │
│   poly.md                operad.md   flux.md                          │
│   (tall, blooming)      (healthy)   (seedling)                        │
│                                                                        │
│         🥀                                      🌾🌾🌾                 │
│        sheaf.md                                (weeds: 3 orphans)     │
│        (wilting, contested)                                           │
│                                                                        │
│                                                                        │
│  ─── Ground (L-2) ────────────────────────────────────────────────── │
│  ─── Marks (L0) ──────────────────────────────────────────────────── │
│  ─── Tests (L1) ──────────────────────────────────────────────────── │
│  ─── Proofs (L2) ─────────────────────────────────────────────────── │
├────────────────────────────────────────────────────────────────────────┤
│  Orphan Weeds (3)                          [Link to Prompt] [Compost] │
└────────────────────────────────────────────────────────────────────────┘
```

- **Plant size** = evidence coverage (more evidence → taller)
- **Plant health** = confidence (high → green/blooming, low → brown/wilting)
- **Weeds** = orphans (red, at edges, invitation to tend)
- **Ground layers** = evidence strata (visible on hover)

This connects to Kent's metaphor: *"The persona is a garden, not a museum."*

---

## Component Specifications

### Phase 1: EvidencePulse Component

**File:** `impl/claude/web/src/components/witness/EvidencePulse.tsx`

The heartbeat of trust. Replaces `EvidenceBadge` with something alive.

```tsx
/**
 * EvidencePulse - A living heartbeat that shows trust health
 *
 * Confidence manifests as pulse rate. Not decorative—diagnostic.
 * Like checking a pulse to see if something is alive.
 */

export interface EvidencePulseProps {
  /** Current confidence (0.0-1.0) */
  confidence: number;
  /** Previous confidence for delta animation */
  previousConfidence?: number;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Show numeric value */
  showValue?: boolean;
  /** Click handler */
  onClick?: () => void;
}

// Pulse rate based on confidence
const getPulseConfig = (confidence: number) => {
  if (confidence < 0.3) return { rate: 0, color: LIVING_EARTH.soil };      // Flatline
  if (confidence < 0.6) return { rate: 0.5, color: LIVING_EARTH.honey };   // Awakening
  if (confidence < 0.9) return { rate: 1.0, color: LIVING_EARTH.sage };    // Alive
  return { rate: 1.5, color: LIVING_EARTH.copper };                         // Thriving
};
```

**Key behaviors:**
- Pulse via `Breathe` primitive with dynamic intensity
- Delta detection: if confidence increased, pulse *accelerates* for 2 seconds
- Delta detection: if confidence decreased, pulse becomes *irregular* (adds jitter)
- No animation at confidence < 0.3 (flatline is stillness, not animation)

---

### Phase 2: EvidenceLadder Component

**File:** `impl/claude/web/src/components/witness/EvidenceLadder.tsx`

Vertical visualization of the complete evidence stack, including L-∞ orphans.

```tsx
/**
 * EvidenceLadder - The complete evidence stack from L-∞ to L3
 *
 * Seven rungs: Orphan → Prompt → Trace → Mark → Test → Proof → Bet
 * Each rung has color, pulse, and count.
 */

export interface EvidenceLadderProps {
  levels: {
    orphan?: number;    // L-∞: Artifacts without lineage
    prompt?: number;    // L-2: PromptAncestor count
    trace?: number;     // L-1: TraceWitness count
    mark?: number;      // L0: Human marks
    test?: number;      // L1: Test artifacts
    proof?: number;     // L2: Formal proofs
    bet?: number;       // L3: Economic bets
  };
  status: SpecStatus;
  lens: 'audit' | 'author' | 'trust';
  onLevelClick?: (level: EvidenceLevel) => void;
}
```

**Colors (Living Earth palette extended):**

```ts
const EVIDENCE_COLORS = {
  orphan: '#991B1B',    // red-800 (needs attention)
  prompt: LIVING_EARTH.sage,      // sage (generative origin)
  trace: '#06B6D4',     // cyan-500 (runtime observation)
  mark: LIVING_EARTH.copper,      // copper (human attention)
  test: '#22C55E',      // green-500 (automation)
  proof: '#A855F7',     // purple-500 (formal)
  bet: '#F59E0B',       // amber-500 (economic)
} as const;
```

**Lens behaviors:**

| Lens | What's Visible | Animation |
|------|----------------|-----------|
| Audit | All 7 levels, counts, click to expand | `Shimmer` on processing levels |
| Author | My contributions highlighted, attention items pulsing | `Breathe` on items needing action |
| Trust | Collapsed to single bar with gradient | Static except on hover |

---

### Phase 3: ProvenanceTree Component

**File:** `impl/claude/web/src/components/witness/ProvenanceTree.tsx`

Navigate from artifact → prompt → decision → proof. Every line of code has a genealogy.

```tsx
/**
 * ProvenanceTree - Genealogy of an artifact
 *
 * Not a panel—a tree you can climb.
 * Click any node to see its parents or children.
 */

export interface ProvenanceTreeProps {
  /** Root artifact to show provenance for */
  rootPath: string;
  /** Provenance chain (loaded async) */
  chain: ProvenanceNode[];
  /** Loading state */
  loading?: boolean;
  /** Navigate to node */
  onNavigate?: (node: ProvenanceNode) => void;
  /** Current lens */
  lens: 'audit' | 'author' | 'trust';
}

interface ProvenanceNode {
  id: string;
  type: 'orphan' | 'prompt' | 'artifact' | 'mark' | 'crystal' | 'test' | 'proof';
  label: string;
  timestamp: string;
  confidence?: number;
  author: 'kent' | 'claude' | 'system';
  children?: ProvenanceNode[];
}
```

**Visual design:**
- Tree rendered horizontally (genealogy reads left → right, like time)
- AI-generated nodes: `Shimmer` effect (subtle, not flashy)
- Human nodes: solid presence (no shimmer)
- Each node shows: type icon + label + confidence pulse
- Click expands inline or navigates (lens-dependent)

**Mobile: Swipe-Based Provenance**

On mobile, the tree becomes a **card deck**:

```tsx
/**
 * Mobile: Provenance as swipeable cards
 *
 * Swipe left → parent node
 * Swipe right → children
 * Swipe up → add mark ("I witness this")
 * Swipe down → dismiss detail
 */
```

Gestures are first-class trust actions, not just navigation.

---

### Phase 4: SpecGarden Component

**File:** `impl/claude/web/src/components/witness/SpecGarden.tsx`

The primary dashboard. A living garden where specs grow.

```tsx
/**
 * SpecGarden - The assurance case as a living garden
 *
 * "The persona is a garden, not a museum."
 *
 * Specs are plants. Evidence is soil depth. Trust is health.
 */

export interface SpecGardenProps {
  specs: SpecPlant[];
  orphans: OrphanWeed[];
  lens: 'audit' | 'author' | 'trust';
  selectedSpec?: string;
  onSelectSpec?: (specPath: string) => void;
  onTendOrphan?: (orphanPath: string) => void;
}

interface SpecPlant {
  path: string;
  name: string;
  status: SpecStatus;
  confidence: number;
  evidenceLevels: EvidenceLevels;
  // Visual properties derived from evidence
  height: number;        // Taller = more evidence
  health: 'blooming' | 'healthy' | 'wilting' | 'dead';
  hasWeeds: boolean;     // Has orphan children
}

interface OrphanWeed {
  path: string;
  createdAt: string;
  suggestedPrompt?: string;  // If we can guess the origin
}
```

**Plant rendering:**

```tsx
function PlantGlyph({ plant }: { plant: SpecPlant }) {
  const glyphs = {
    blooming: '🌳',   // Tall tree with flowers
    healthy: '🌿',    // Green plant
    wilting: '🥀',    // Drooping flower
    dead: '🪵',       // Dead wood
  };

  return (
    <Breathe intensity={plant.confidence} disabled={plant.health === 'dead'}>
      <div
        className="flex flex-col items-center"
        style={{ height: `${20 + plant.height * 10}px` }}
      >
        <span className="text-2xl">{glyphs[plant.health]}</span>
        <span className="text-xs truncate max-w-[80px]">{plant.name}</span>
      </div>
    </Breathe>
  );
}
```

**Weeds rendering:**

```tsx
function WeedCluster({ orphans, onTend }: { orphans: OrphanWeed[], onTend: (path: string) => void }) {
  return (
    <div className="flex gap-1 opacity-70 hover:opacity-100 transition-opacity">
      {orphans.map(o => (
        <Breathe key={o.path} intensity={0.2} speed="slow">
          <button
            onClick={() => onTend(o.path)}
            className="text-lg hover:scale-110 transition-transform"
            title={`Orphan: ${o.path}`}
          >
            🌾
          </button>
        </Breathe>
      ))}
    </div>
  );
}
```

---

### Phase 5: WitnessAssurance Page

**File:** `impl/claude/web/src/pages/WitnessAssurance.tsx`

The complete dashboard integrating all components.

**Layout:**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  Witness Assurance                                      [Audit][Author][Trust]│
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                           SpecGarden                                         │
│                      (main visualization)                                    │
│                                                                              │
├──────────────────────────────────────────────────────────────────────────────┤
│  Selected: spec/agents/poly.md                                               │
│  ┌─────────────────────────────────┬────────────────────────────────────────┐│
│  │ EvidenceLadder                  │ ProvenanceTree                         ││
│  │                                 │                                        ││
│  │ L3 Bet: 0    ░░░░░░░░          │ prompt-abc123                          ││
│  │ L2 Proof: 2  █████░░░░         │ └─ agents/poly/core.py                 ││
│  │ L1 Test: 28  █████████         │    ├─ mark: "Polynomial is correct"    ││
│  │ L0 Mark: 5   █████░░░░         │    └─ test: test_polynomial_laws       ││
│  │ L-1 Trace: 12 ████████         │       └─ proof: poly-identity          ││
│  │ L-2 Prompt: 3 ███░░░░░         │                                        ││
│  │ L-∞ Orphan: 0 ░░░░░░░░         │                                        ││
│  └─────────────────────────────────┴────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────────────┤
│  EvidencePulse: ❤️ 0.87 (steady)                     [Add Mark] [Run Tests]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Mobile layout:**

- Single column: Garden → tap plant → full-screen detail
- Bottom drawer for provenance tree
- Floating action button for quick witness action
- Swipe gestures for provenance navigation

---

## Celebration Moments (Joy, Not Confetti)

### Milestone Toasts

```tsx
// In EvidencePulse.tsx or WitnessAssurance.tsx
useEffect(() => {
  if (previousStatus !== status) {
    if (status === 'witnessed') {
      toast({
        title: "Witnessed",
        message: `${specName} has earned full witness status`,
        variant: 'joy',
        icon: <span className="text-xl">🌳</span>,
      });
    } else if (previousConfidence < 0.5 && confidence >= 0.5) {
      toast({
        title: "Awakening",
        message: `${specName} is coming alive`,
        variant: 'subtle',
        icon: <span className="text-xl">🌱</span>,
      });
    }
  }
}, [status, confidence, previousStatus, previousConfidence, specName]);
```

### Orphan Resolution Celebration

When an orphan gets linked to a prompt:

```tsx
toast({
  title: "Tended",
  message: `${orphanPath} now has lineage`,
  variant: 'joy',
  icon: <span className="text-xl">🌻</span>,
});
```

---

## AGENTESE Integration

### New Paths

| Path | Returns | Component |
|------|---------|-----------|
| `self.witness.garden` | SpecGarden data | `SpecGarden.tsx` |
| `self.witness.ladder` | EvidenceLadder data | `EvidenceLadder.tsx` |
| `self.witness.provenance` | ProvenanceTree data | `ProvenanceTree.tsx` |
| `self.witness.orphans` | OrphanWeed[] | (part of garden) |
| `self.witness.pulse` | Confidence + delta | `EvidencePulse.tsx` |

### SSE Streaming for Live Updates

```python
@node("self.witness.garden")
class WitnessGardenNode(BaseLogosNode):
    """The spec garden as a living view."""

    aspects = ["manifest", "stream"]

    async def stream(self, observer: AgentMeta):
        """SSE stream of garden updates."""
        # Yields on: new mark, test result, proof completion, orphan change
        async for event in self._garden_events():
            yield {"type": event.type, "data": event.data}
```

---

## Implementation Phases

| Phase | Components | Sessions | Key Deliverable |
|-------|------------|----------|-----------------|
| **1** | `EvidencePulse.tsx` | 0.5 | Heartbeat visualization |
| **2** | `EvidenceLadder.tsx` + L-∞ | 0.5 | Complete evidence stack |
| **3** | `ProvenanceTree.tsx` + mobile | 1 | Navigable genealogy |
| **4** | `SpecGarden.tsx` | 1 | Garden visualization |
| **5** | `WitnessAssurance.tsx` + integration | 1.5 | Complete dashboard |

**Total:** 4.5 sessions

---

## Verification Checklist

**EvidencePulse:**
- [ ] Pulse rate varies with confidence
- [ ] Delta detection animates increase/decrease
- [ ] Flatline at confidence < 0.3
- [ ] Respects reduced motion preferences

**EvidenceLadder:**
- [ ] All 7 levels render (L-∞ to L3)
- [ ] Colors match Living Earth palette
- [ ] Lens switching works (Audit/Author/Trust)
- [ ] Click expands level detail

**ProvenanceTree:**
- [ ] Tree renders horizontally
- [ ] AI vs human distinction visible
- [ ] Navigation works
- [ ] Mobile swipe gestures work

**SpecGarden:**
- [ ] Plants render with correct height/health
- [ ] Weeds (orphans) visible at edges
- [ ] Selection syncs with detail panels
- [ ] Lens affects what's emphasized

**WitnessAssurance:**
- [ ] All panels coordinate
- [ ] SSE updates refresh garden
- [ ] Milestone toasts fire appropriately
- [ ] Mobile layout works

---

## Constitutional Alignment

| Article | How This UI Embodies It |
|---------|-------------------------|
| **I. Symmetric Agency** | Same plant representation for Kent's and Claude's marks |
| **IV. The Disgust Veto** | Wilting plants are visually distinct—problems aren't hidden |
| **V. Trust Accumulation** | Garden growth shows earned trust over time |
| **VI. Fusion as Goal** | Provenance shows human+AI contributions interleaved |
| **VII. Amendment** | The garden evolves—dead plants compost, new ones grow |

---

## The Mirror Test

> *"Does this make the assurance case understandable at a glance?"*

**Honest if:**
- A new contributor can see project health in 5 seconds (garden overview)
- Any artifact's genealogy is traceable in 3 clicks
- Low-fitness prompts are surfaced as wilting plants, not hidden
- Orphans are visible weeds, inviting tending
- Trust accumulation is visible as growth, not badges

**Impressive but dishonest if:**
- Garden animation distracts from real status
- Weeds are hidden by default
- Only blooming plants are shown
- The heartbeat is always strong regardless of actual confidence

---

## Anti-Sausage Check

Before implementing, verify:
- [ ] **Daring**: Garden metaphor is unconventional for audit UI
- [ ] **Bold**: Accountability lenses are opinionated, not generic
- [ ] **Creative**: Heartbeat pulse is novel for confidence display
- [ ] **Not gaudy**: No floating particles, no confetti—just organic life

---

*"The UI IS the trust surface. Every pixel grows or wilts."*

**Filed:** 2025-12-22
**Transformed:** From spreadsheet to garden
**Parent:** `plans/witness-assurance-protocol.md`
**Heritage:** MarkCard, Living Earth palette, Breathe, Shimmer, joy primitives
