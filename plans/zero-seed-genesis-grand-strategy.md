# THE GRAND STRATEGY: Zero Seed Genesis

> **DEPRECATED**: This document has been superseded by `plans/zero-seed-strategy-unified.md`.
> Please refer to the unified document for the authoritative Zero Seed strategy.
> This file is retained for historical reference only.

---

> *"The act of declaring, capturing, and auditing your decisions is itself a radical act of self-transformation."*

**Version**: 1.0 — The Sanctification
**Date**: 2025-12-25
**Status**: DEPRECATED - See `plans/zero-seed-strategy-unified.md`
**Author**: Kent Gang + Claude (Anthropic)
**Context**: This plan emerged from a deep brainstorming session exploring the unification of Galois, Zero-Seed, and K-Block architectures into a coherent whole.

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

This plan defines a **radical reimagining** of kgents as a self-justifying, self-auditing, infinitely tolerant knowledge garden where:

1. **Genesis is visible** — The Zero Seed is not hidden; users watch it spawn
2. **Everything is a K-Block** — Files, decisions, goals, axioms — all first-class
3. **The feed is the interface** — Chronological truth, filterable by lens
4. **Uploads are portals** — External content enters through sovereign staging
5. **Layers are normative but porous** — Structure helps, but heterarchy is allowed
6. **Incoherence is tolerated** — Declaring > coherence; the system metabolizes mess
7. **Justification IS agency** — No hidden decisions; every edge has a trace

**The radical act**: Not *building* a coherent system, but *declaring your intent* and watching coherence emerge (or not).

---

## Prerequisites for Executing Agent

Before implementing, the executing agent MUST read and understand:

| Document | Location | Why Essential |
|----------|----------|---------------|
| **Constitution** | `spec/principles/CONSTITUTION.md` | The 7+7 principles that ground all decisions |
| **Zero Seed Protocol** | `spec/protocols/zero-seed.md` | The canonical v3.0 Galois-native spec |
| **K-Block Spec** | `spec/protocols/k-block.md` | Transactional hyperdimensional editing |
| **Galois Theory** | `spec/theory/galois-modularization.md` | Loss as universal coherence metric |
| **Agent-DP** | `spec/theory/agent-dp.md` | Problem-solution co-emergence |
| **NOW.md** | `NOW.md` | Current system state and context |

---

## Part I: The Five Pillars

These are the **architectural pillars** that define the system:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE FIVE PILLARS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. FEED AS PRIMITIVE                                                       │
│     The chronological truth stream. Algorithmic. Principles-aligned.        │
│     Users create feedback systems WITH the feed.                            │
│                                                                             │
│  2. K-BLOCK AS INCIDENTAL ESSENTIAL                                         │
│     Theoretically decouple-able. Pragmatically indispensable.               │
│     The surface for organizing IDEAS on linear media.                       │
│                                                                             │
│  3. SOVEREIGN UPLOADS                                                       │
│     External content enters through staging.                                │
│     Analysis + connection on deliberate integration.                        │
│                                                                             │
│  4. HETERARCHICAL TOLERANCE                                                 │
│     Cross-layer edges allowed. Incoherence tolerated.                       │
│     System adapts to user, not user to system.                              │
│                                                                             │
│  5. CONTRADICTION AS FEATURE                                                │
│     Surface. Interrogate. Transform.                                        │
│     Fail-fast epistemology. Always in flux.                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part II: Design Laws (Immutable)

These laws are **immutable** and must be respected by all implementations.

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

    One could remove K-Blocks and kgents would still function.
    But the UX/DevEx transformation is so radical that
    pragmatically: K-Blocks IS kgents, kgents NEEDS K-Blocks.

    The primitive underneath is the trace.
    K-Blocks are syntactic sugar over traces.
    But sugar that makes the medicine go down.
    """

    immutable = True
    layer = 2  # Value level (not axiom — could be replaced)
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
    layer = 1  # Axiom level — core to identity
```

---

## Part III: The Genesis Protocol

### 3.1 Zero Seed Definition

```python
@dataclass(frozen=True)
class ZeroSeed:
    """
    The unwriteable genesis K-Block.

    Not truly immutable — append-only evolution is possible.
    But evolution is DIFFICULT by design.
    Any change to Zero Seed requires:
    1. Dialectical synthesis proposal
    2. Galois loss verification (must not increase system loss)
    3. Witness trail with full justification

    Zero Seed is the FIRST entry in the infinite feed.
    Everything else derives from it.
    """

    id: str = "zero-seed-genesis"
    created_at: datetime = EPOCH  # t=0
    kind: Literal["SYSTEM"] = "SYSTEM"
    layer: int = 0  # Below L1 — the ground of grounds
    galois_loss: float = 0.000  # Perfect self-coherence

    axioms: tuple[Axiom, ...] = (
        Axiom(id="A1", statement="Everything is a node", loss=0.002),
        Axiom(id="A2", statement="Everything composes", loss=0.003),
        Axiom(id="G", statement="Loss measures truth", loss=0.000),
    )

    design_laws: tuple[DesignLaw, ...] = (
        FeedIsPrimitive,
        KBlockIncidentalEssential,
        LinearAdaptation,
        ContradictionSurfacing,
    )

    @property
    def can_evolve(self) -> bool:
        """Evolution is possible but governed."""
        return True

    @property
    def evolution_difficulty(self) -> str:
        """Honest answer: we don't know yet."""
        return "UNKNOWN — designed to be difficult"
```

### 3.2 The Bootstrap Script

```bash
#!/bin/bash
# reset-world.sh — Total system reset for development/testing

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  KGENTS GENESIS PROTOCOL                                          ║"
echo "║  This will destroy all user data and rebuild from Zero Seed.      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

read -p "Are you sure? Type 'genesis' to confirm: " confirm
if [ "$confirm" != "genesis" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Phase 1: Destroying old cosmos..."
docker compose down -v
rm -rf ./data/cosmos/*
rm -rf ./data/uploads/*
rm -rf ./data/user/*

echo "Phase 2: Rebuilding containers..."
docker compose build --no-cache
docker compose up -d

echo "Phase 3: Waiting for services..."
sleep 5

echo "Phase 4: Seeding Zero Seed..."
curl -X POST http://localhost:8000/api/genesis/seed \
  -H "Content-Type: application/json" \
  -d '{
    "axioms": ["A1", "A2", "G"],
    "design_laws": ["FeedIsPrimitive", "KBlockIncidentalEssential", "LinearAdaptation", "ContradictionSurfacing"]
  }'

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  GENESIS COMPLETE                                                 ║"
echo "║                                                                   ║"
echo "║  Zero Seed created at t=0                                         ║"
echo "║  The infinite feed has begun.                                     ║"
echo "║                                                                   ║"
echo "║  Visit http://localhost:3000 to witness.                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
```

---

## Part IV: The Feed Architecture

### 4.1 Feed as UI Primitive

```typescript
// Feed is a PRIMITIVE, not a component
// Like Text, View, Button — Feed is foundational

interface Feed {
  id: string;
  name: string;

  // What enters this feed
  sources: FeedSource[];

  // How it's filtered
  filters: FeedFilter[];

  // How it's ranked (algorithmic)
  ranking: FeedRanking;

  // The user's feedback loop WITH this feed
  feedback: FeedFeedback;
}

interface FeedSource {
  type: 'all' | 'layer' | 'author' | 'tag' | 'custom';
  value: string | number | ((kblock: KBlock) => boolean);
}

interface FeedFilter {
  field: 'layer' | 'loss' | 'author' | 'principle' | 'time' | 'custom';
  operator: 'eq' | 'lt' | 'gt' | 'between' | 'contains';
  value: any;
}

interface FeedRanking {
  // Attention model: what has the user engaged with?
  attention_weight: number;

  // Principles alignment: how well does this match user's declared values?
  principles_weight: number;

  // Recency: newer = higher
  recency_weight: number;

  // Loss: lower loss = higher rank (more coherent)
  coherence_weight: number;

  // Custom scoring function
  custom?: (kblock: KBlock, user: User) => number;
}

interface FeedFeedback {
  // The user creates feedback systems WITH the feed
  // This is recursive and powerful

  on_view: (kblock: KBlock) => void;      // Track attention
  on_engage: (kblock: KBlock) => void;    // Track interaction
  on_dismiss: (kblock: KBlock) => void;   // Learn preferences
  on_contradict: (kblock: KBlock) => void; // Surface conflicts
}
```

### 4.2 Default Feeds

```typescript
const DEFAULT_FEEDS: Feed[] = [
  {
    id: 'cosmos',
    name: 'The Cosmos',
    description: 'Everything, in order of creation',
    sources: [{ type: 'all' }],
    filters: [],
    ranking: { recency_weight: 1.0, attention_weight: 0, principles_weight: 0, coherence_weight: 0 },
  },
  {
    id: 'coherent',
    name: 'Most Coherent',
    description: 'Lowest loss first — your most solid beliefs',
    sources: [{ type: 'all' }],
    filters: [],
    ranking: { coherence_weight: 1.0, recency_weight: 0.1 },
  },
  {
    id: 'contradictions',
    name: 'Contradictions',
    description: 'Where your beliefs conflict — opportunity for synthesis',
    sources: [{ type: 'all' }],
    filters: [{ field: 'custom', operator: 'eq', value: 'has_contradiction_edge' }],
    ranking: { coherence_weight: -1.0 },  // Highest loss first
  },
  {
    id: 'axioms',
    name: 'Your Axioms',
    description: 'L1-L2 — the bedrock you stand on',
    sources: [{ type: 'layer', value: [1, 2] }],
    filters: [],
    ranking: { coherence_weight: 1.0 },
  },
  {
    id: 'handwavy',
    name: 'Hand-Wavy Goals',
    description: 'High loss declarations waiting to cohere',
    sources: [{ type: 'layer', value: 3 }],
    filters: [{ field: 'loss', operator: 'gt', value: 0.5 }],
    ranking: { recency_weight: 1.0 },
  },
];
```

### 4.3 Feed-Feedback Loop

```typescript
// Users create feedback systems WITH the feed
// This is the recursive power

class FeedFeedbackSystem {
  constructor(private feed: Feed, private user: User) {}

  // When user views a K-Block, learn from it
  async onView(kblock: KBlock): Promise<void> {
    await this.recordAttention(kblock, 'view');
    await this.updatePrinciplesModel(kblock);
  }

  // When user engages (edits, comments, links), strengthen
  async onEngage(kblock: KBlock): Promise<void> {
    await this.recordAttention(kblock, 'engage');
    await this.boostSimilar(kblock);
  }

  // When user dismisses, learn negative preference
  async onDismiss(kblock: KBlock): Promise<void> {
    await this.recordAttention(kblock, 'dismiss');
    await this.suppressSimilar(kblock);
  }

  // When contradiction detected, surface it
  async onContradiction(kblock: KBlock, other: KBlock): Promise<void> {
    // Create a SYNTHESIS prompt
    const synthesis = await this.promptSynthesis(kblock, other);

    // Add to contradictions feed automatically
    await this.contradictionsFeed.add(synthesis);

    // Witness the detection
    await witness.mark({
      action: 'contradiction_detected',
      kblocks: [kblock.id, other.id],
      galois_loss: await galois.superAdditiveLoss(kblock, other),
    });
  }

  // The user can CREATE new feeds based on their feedback
  async createPersonalFeed(name: string, criteria: FeedCriteria): Promise<Feed> {
    // This is the recursive part — feeds creating feeds
    const feed = {
      id: `user-${this.user.id}-${name}`,
      name,
      sources: criteria.sources,
      filters: criteria.filters,
      ranking: {
        ...DEFAULT_RANKING,
        custom: (kb) => this.personalScore(kb, criteria),
      },
    };

    await this.saveFeed(feed);
    return feed;
  }
}
```

---

## Part V: The File Explorer + Sovereign Uploads

### 5.1 Directory Structure (Real)

```
/                           # Root of user's kgents space
├── uploads/                # SOVEREIGN STAGING (unmapped)
│   └── [incoming files]    # Await integration
│
├── spec/                   # SPECIFICATIONS (L3-L4)
│   ├── agents/             # Agent specifications
│   ├── protocols/          # Protocol specifications
│   └── principles/         # Principle specifications
│
├── impl/                   # IMPLEMENTATION (L5)
│   └── [code files]        # Mapped to K-Blocks
│
├── docs/                   # DOCUMENTATION (L6-L7)
│   ├── skills/             # How-to guides
│   └── theory/             # Theoretical foundations
│
└── .kgents/                # SYSTEM (hidden)
    ├── cosmos.db           # Append-only log
    ├── feeds/              # User's feed configurations
    └── zero-seed.json      # Genesis (readonly)
```

### 5.2 Upload Integration Protocol

```python
class UploadIntegrationProtocol:
    """
    When a file is moved from uploads/ to a proper folder,
    it is ANALYZED and TOTALLY CONNECTED with the system.
    """

    async def integrate(
        self,
        source: Path,  # uploads/my-doc.md
        destination: Path,  # spec/protocols/my-doc.md
    ) -> IntegrationResult:
        """Full integration on move."""

        # 1. Create witness mark for the integration
        mark = await witness.mark(
            action="upload_integration",
            source=str(source),
            destination=str(destination),
            timestamp=now(),
        )

        # 2. Analyze content for layer assignment
        content = await read(source)
        layer = await galois.assign_layer(content)
        loss = await galois.compute_loss(content)

        # 3. Create K-Block (one doc = one K-Block heuristic)
        kblock = await kblock_service.create(
            path=destination,
            content=content,
            layer=layer,
            galois_loss=loss,
            created_via=mark.id,
        )

        # 4. Discover edges (what does this relate to?)
        edges = await self.discover_edges(kblock)
        for edge in edges:
            await kblock_service.add_edge(kblock.id, edge)

        # 5. Attach portal tokens (kgents native links)
        tokens = await self.extract_portal_tokens(content)
        for token in tokens:
            await portal_service.attach(kblock.id, token)

        # 6. Identify concepts (axioms, constructs)
        concepts = await self.identify_concepts(content)
        for concept in concepts:
            await concept_service.link(kblock.id, concept)

        # 7. Check for contradictions with existing content
        contradictions = await galois.find_contradictions(kblock)
        if contradictions:
            await self.surface_contradictions(kblock, contradictions)

        # 8. Move file to destination
        await move(source, destination)

        # 9. Add to cosmos feed
        await cosmos_feed.append(kblock)

        return IntegrationResult(
            kblock=kblock,
            mark=mark,
            edges=edges,
            tokens=tokens,
            concepts=concepts,
            contradictions=contradictions,
        )
```

### 5.3 Automatic K-Block Splitting

```python
class KBlockSplittingHeuristics:
    """
    Decide when one doc should become multiple K-Blocks.
    """

    async def analyze_for_splitting(self, kblock: KBlock) -> SplitRecommendation:
        """
        Heuristics for splitting:
        1. Multiple distinct concepts (headings at same level)
        2. Internal contradiction (super-additive loss)
        3. Size threshold (> 5000 tokens)
        4. Layer mixing (L3 goals mixed with L5 implementations)
        """

        reasons = []

        # Check for multiple top-level concepts
        sections = self.extract_sections(kblock.content)
        if len(sections) > 3:
            reasons.append(SplitReason(
                type="multiple_concepts",
                description=f"Document has {len(sections)} distinct sections",
                confidence=0.7,
            ))

        # Check for internal contradiction
        internal_loss = await galois.internal_contradiction(kblock)
        if internal_loss > 0.4:
            reasons.append(SplitReason(
                type="internal_contradiction",
                description=f"Sections contradict each other (loss: {internal_loss:.2f})",
                confidence=0.9,
            ))

        # Check for layer mixing
        section_layers = [await galois.assign_layer(s) for s in sections]
        if len(set(section_layers)) > 2:
            reasons.append(SplitReason(
                type="layer_mixing",
                description=f"Sections span layers {set(section_layers)}",
                confidence=0.6,
            ))

        if not reasons:
            return SplitRecommendation(should_split=False, reasons=[])

        # Generate split plan
        split_plan = await self.generate_split_plan(kblock, reasons)

        return SplitRecommendation(
            should_split=True,
            reasons=reasons,
            plan=split_plan,
            # User decides — we don't force
            requires_user_approval=True,
        )
```

---

## Part VI: First Time User Experience

### 6.1 Research: FTUE Trends 2024-2025

Based on current trends in onboarding:

| Trend | Example | Our Application |
|-------|---------|-----------------|
| **Progressive Disclosure** | Notion, Linear | Show Zero Seed first, reveal complexity gradually |
| **Empty State as Teaching** | Figma, Miro | Genesis as educational experience |
| **Action-First** | Vercel, Railway | "What do you want to build?" immediately |
| **Personalization Early** | Spotify, TikTok | Ask about values/goals in first 30 seconds |
| **Show, Don't Tell** | Loom, Arcade | Watch the feed populate in real-time |
| **Delight Moments** | Slack, Discord | Celebrate first K-Block creation |

### 6.2 The kgents FTUE: "Witness Genesis"

```
PHASE 1: GENESIS (0-30 seconds)
───────────────────────────────────────────────────────────────────────────

╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║                           W E L C O M E                                  ║
║                                                                          ║
║                    You are witnessing Genesis.                           ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝

[Feed begins populating in real-time]

┌──────────────────────────────────────────────────────────────────────────┐
│  t=0  │ ZERO SEED                                                        │
│       │ The ground of grounds.                                           │
│       │ ○ L0 · System · Loss: 0.000                                      │
├──────────────────────────────────────────────────────────────────────────┤
│  t=1  │ AXIOM: Everything is a node                                      │
│       │ A1 — The first truth.                                            │
│       │ ○ L1 · Axiom · Loss: 0.002                                       │
├──────────────────────────────────────────────────────────────────────────┤
│  t=2  │ AXIOM: Everything composes                                       │
│       │ A2 — The second truth.                                           │
│       │ ○ L1 · Axiom · Loss: 0.003                                       │
├──────────────────────────────────────────────────────────────────────────┤
│  t=3  │ GROUND: Loss measures truth                                      │
│       │ G — The Galois foundation.                                       │
│       │ ○ L1 · Ground · Loss: 0.000                                      │
└──────────────────────────────────────────────────────────────────────────┘

                    The system is now self-aware.

                    [ Continue → ]


PHASE 2: FIRST QUESTION (30-60 seconds)
───────────────────────────────────────────────────────────────────────────

╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║         What matters most to you right now?                              ║
║                                                                          ║
║         (This becomes your first personal axiom)                         ║
║                                                                          ║
║    ┌──────────────────────────────────────────────────────────────┐      ║
║    │                                                              │      ║
║    │  > Building something specific                               │      ║
║    │                                                              │      ║
║    └──────────────────────────────────────────────────────────────┘      ║
║                                                                          ║
║    Examples:                                                             ║
║    • "I want to build a personal knowledge base"                         ║
║    • "I believe in open source"                                          ║
║    • "I'm exploring what I believe"                                      ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝


PHASE 3: FIRST K-BLOCK (60-90 seconds)
───────────────────────────────────────────────────────────────────────────

[User types: "I want to build a personal knowledge base"]

╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║    Your first K-Block is being created...                                ║
║                                                                          ║
║    ┌──────────────────────────────────────────────────────────────┐      ║
║    │  GOAL: Build a personal knowledge base                       │      ║
║    │                                                              │      ║
║    │  Layer: L3 (Goal)                                            │      ║
║    │  Loss: 0.42 — A bit hand-wavy, and that's okay!              │      ║
║    │                                                              │      ║
║    │  Justification: "This is what matters to me"                 │      ║
║    │                                                              │      ║
║    └──────────────────────────────────────────────────────────────┘      ║
║                                                                          ║
║    ✨ You've made your first declaration.                                 ║
║       The system will help you make it more coherent over time.          ║
║                                                                          ║
║                    [ Enter kgents → ]                                    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝


PHASE 4: THE STUDIO (90+ seconds)
───────────────────────────────────────────────────────────────────────────

[User enters the Hypergraph Studio]

┌────────────────┬────────────────────────────────────────────────────────┐
│ FILE EXPLORER  │                                                        │
│                │                    FEED: The Cosmos                     │
│ ▼ uploads/     │                                                        │
│   (empty)      │  ┌──────────────────────────────────────────────────┐  │
│                │  │  t=4  │ YOUR GOAL                                 │  │
│ ▼ spec/        │  │       │ Build a personal knowledge base           │  │
│   (empty)      │  │       │ ○ L3 · Goal · Loss: 0.42                  │  │
│                │  └──────────────────────────────────────────────────┘  │
│ ▼ impl/        │                                                        │
│   (empty)      │  ┌──────────────────────────────────────────────────┐  │
│                │  │  t=3  │ GROUND: Loss measures truth               │  │
│ ▼ docs/        │  │       │ The Galois foundation                     │  │
│   (empty)      │  │       │ ○ L1 · Ground · Loss: 0.000               │  │
│                │  └──────────────────────────────────────────────────┘  │
│                │                                                        │
│ [Drop files    │            [scroll for more...]                        │
│  to upload]    │                                                        │
└────────────────┴────────────────────────────────────────────────────────┘

                    HINT: Drag files into uploads/ to begin.
                    The system will help you organize them.
```

### 6.3 Joy Moments

| Moment | Trigger | Delight |
|--------|---------|---------|
| Genesis witnessed | First load | "The system is now self-aware" |
| First K-Block | User types first goal | Subtle animation, celebratory copy |
| First upload | File dropped | "Your knowledge is entering the cosmos" |
| First integration | File moved from uploads | Show edges discovered |
| First contradiction | System detects conflict | Frame as opportunity, not error |
| First synthesis | User resolves contradiction | "You've grown" |

---

## Part VII: Heterarchical Tolerance

### 7.1 Cross-Layer Edge Rules

```python
class HeterarchicalEdgePolicy:
    """
    Cross-layer edges are ALLOWED by default.
    Justification is ENCOURAGED but not REQUIRED.

    Linear design philosophy: adapt to user, don't force behavior.
    """

    STRICT_EDGES = {
        # These MUST have justification (categorical requirement)
        EdgeKind.CONTRADICTS: True,
        EdgeKind.SUPERSEDES: True,
    }

    SUGGESTED_EDGES = {
        # These SHOULD have justification (flagged if missing)
        EdgeKind.GROUNDS: True,      # L1 → L2 (why does this value derive from that axiom?)
        EdgeKind.JUSTIFIES: True,    # L2 → L3 (why does this goal follow from that value?)
    }

    OPTIONAL_EDGES = {
        # These MAY have justification (not flagged)
        EdgeKind.IMPLEMENTS: False,  # L4 → L5 (obvious connection)
        EdgeKind.EXTENDS: False,     # Same layer refinement
        EdgeKind.DERIVES_FROM: False,
    }

    async def validate_edge(self, edge: ZeroEdge) -> EdgeValidation:
        """Validate but don't block."""

        is_cross_layer = abs(edge.source.layer - edge.target.layer) > 1

        if edge.kind in self.STRICT_EDGES:
            if not edge.justification:
                return EdgeValidation(
                    valid=False,  # Actually blocked
                    reason="Contradiction/supersession edges require justification",
                )

        if is_cross_layer:
            # Cross-layer is allowed but surfaced
            loss = await galois.edge_loss(edge)

            return EdgeValidation(
                valid=True,  # Allowed
                flagged=True,  # But surfaced
                loss=loss,
                suggestion=f"This connects L{edge.source.layer} to L{edge.target.layer}. "
                          f"Consider adding justification for clarity.",
            )

        return EdgeValidation(valid=True, flagged=False)
```

### 7.2 Nonsense Quarantine

```python
class NonsenseQuarantine:
    """
    User may add arbitrary nonsense.
    Nonsense does not spread.
    Performance unaffected.

    Strategy: Quarantine, don't reject.
    """

    LOSS_THRESHOLD = 0.85  # Above this = likely nonsense

    async def evaluate(self, kblock: KBlock) -> QuarantineDecision:
        """Evaluate whether to quarantine."""

        loss = kblock.galois_loss

        if loss < 0.5:
            return QuarantineDecision(quarantine=False, reason="Coherent")

        if loss < self.LOSS_THRESHOLD:
            return QuarantineDecision(
                quarantine=False,
                reason="Hand-wavy but tolerable",
                suggestion="Consider adding more detail to increase coherence",
            )

        # High loss — quarantine
        return QuarantineDecision(
            quarantine=True,
            reason=f"Very high loss ({loss:.2f}) — quarantined for review",
            effects=[
                "Will not affect system-wide rankings",
                "Will not propagate to recommendations",
                "Still visible in your personal feeds",
                "Can be refined to exit quarantine",
            ],
        )

    async def on_quarantine(self, kblock: KBlock) -> None:
        """What happens when quarantined."""

        # Add to quarantine feed (user can still see it)
        await feeds.quarantine.add(kblock)

        # Remove from system-wide indexes
        await system_index.exclude(kblock.id)

        # Create witness mark
        await witness.mark(
            action="quarantine",
            kblock_id=kblock.id,
            reason="High Galois loss",
            reversible=True,
        )

        # Notify user (gently)
        await notify.gentle(
            "This K-Block has been quarantined due to high incoherence. "
            "It's still yours — you can refine it or leave it be."
        )
```

---

## Part VIII: Contradiction Engine

### 8.1 Contradiction Detection

```python
class ContradictionEngine:
    """
    ONE OF THE MOST IMPORTANT PARTS of the system.

    Surface, interrogate, systematically interact with
    personal beliefs, values, and contradictions.
    """

    async def detect_contradictions(self, kblock: KBlock) -> list[Contradiction]:
        """Find all contradictions involving this K-Block."""

        contradictions = []

        # Check against all existing K-Blocks
        existing = await cosmos.all_kblocks()

        for other in existing:
            if other.id == kblock.id:
                continue

            # Super-additive loss = contradiction
            loss_combined = await galois.combined_loss(kblock, other)
            loss_sum = kblock.galois_loss + other.galois_loss

            strength = loss_combined - loss_sum

            if strength > 0.1:  # τ threshold
                contradictions.append(Contradiction(
                    kblock_a=kblock,
                    kblock_b=other,
                    strength=strength,
                    type=self.classify_contradiction(strength),
                ))

        return contradictions

    def classify_contradiction(self, strength: float) -> ContradictionType:
        """Classify by strength."""
        if strength < 0.2:
            return ContradictionType.APPARENT  # Likely different scopes
        elif strength < 0.4:
            return ContradictionType.PRODUCTIVE  # Could drive synthesis
        elif strength < 0.6:
            return ContradictionType.TENSION  # Real conflict, needs attention
        else:
            return ContradictionType.FUNDAMENTAL  # Deep inconsistency

    async def surface(self, contradiction: Contradiction) -> None:
        """Surface contradiction to user."""

        # Create contradiction K-Block (meta!)
        contradiction_kblock = await kblock_service.create(
            kind="CONTRADICTION",
            content=f"""
# Contradiction Detected

## Statement A (from {contradiction.kblock_a.title})
{contradiction.kblock_a.summary}

## Statement B (from {contradiction.kblock_b.title})
{contradiction.kblock_b.summary}

## Analysis
- Strength: {contradiction.strength:.2f}
- Type: {contradiction.type.value}

## Options
1. **Synthesize**: Find a higher truth that resolves both
2. **Scope**: Clarify that these apply in different contexts
3. **Choose**: Decide which you actually believe
4. **Tolerate**: Accept the contradiction as productive tension
            """,
            layer=6,  # Reflection layer
            galois_loss=contradiction.strength,
        )

        # Add to contradictions feed
        await feeds.contradictions.add(contradiction_kblock)

        # Add edges
        await kblock_service.add_edge(
            source=contradiction_kblock.id,
            target=contradiction.kblock_a.id,
            kind=EdgeKind.ANALYZES,
        )
        await kblock_service.add_edge(
            source=contradiction_kblock.id,
            target=contradiction.kblock_b.id,
            kind=EdgeKind.ANALYZES,
        )

        # Witness
        await witness.mark(
            action="contradiction_surfaced",
            contradiction_id=contradiction_kblock.id,
            strength=contradiction.strength,
        )
```

### 8.2 Contradiction Resolution UI

```
╔══════════════════════════════════════════════════════════════════════════╗
║  CONTRADICTION DETECTED                                                   ║
║                                                                          ║
║  You said:                                                               ║
║  ┌────────────────────────────────────────────────────────────────┐      ║
║  │  "I believe in composition — everything should compose"        │      ║
║  │  (Your Axiom, L1, Loss: 0.003)                                 │      ║
║  └────────────────────────────────────────────────────────────────┘      ║
║                                                                          ║
║  But also:                                                               ║
║  ┌────────────────────────────────────────────────────────────────┐      ║
║  │  "Some things are atomic and shouldn't be decomposed"          │      ║
║  │  (Your Value, L2, Loss: 0.15)                                  │      ║
║  └────────────────────────────────────────────────────────────────┘      ║
║                                                                          ║
║  Contradiction strength: 0.34 (Productive Tension)                       ║
║                                                                          ║
║  This is INFORMATION, not JUDGMENT.                                      ║
║  Your beliefs are allowed to be in flux.                                 ║
║                                                                          ║
║  Options:                                                                ║
║                                                                          ║
║  [ Synthesize ]  Find a higher truth                                     ║
║  [ Scope ]       "These apply in different contexts"                     ║
║  [ Choose ]      Decide which I actually believe                         ║
║  [ Tolerate ]    Keep both — productive tension is valuable              ║
║  [ Ignore ]      I'll think about this later                             ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Part IX: Implementation Roadmap

### Phase 0: Bootstrap Infrastructure (1 week)

```
DELIVERABLES:
├── reset-world.sh                    # Complete system reset
├── docker-compose.genesis.yml        # Genesis-specific compose
├── impl/claude/protocols/api/genesis.py  # Genesis API endpoints
├── impl/claude/services/zero_seed/seed.py  # Seeding logic
└── tests/
    └── test_genesis.py               # Genesis flow tests

SUCCESS CRITERIA:
✓ `./reset-world.sh` completes in < 60 seconds
✓ Zero Seed appears in cosmos at t=0
✓ Axioms A1, A2, G appear at t=1, t=2, t=3
✓ Design Laws stored and queryable
```

### Phase 1: Feed Primitive (2 weeks)

```
DELIVERABLES:
├── impl/claude/services/feed/
│   ├── core.py                       # Feed primitive
│   ├── ranking.py                    # Algorithmic ranking
│   ├── feedback.py                   # Feedback loop system
│   └── defaults.py                   # Default feeds
├── impl/claude/web/src/primitives/Feed/
│   ├── Feed.tsx                      # Feed component
│   ├── FeedItem.tsx                  # K-Block in feed
│   ├── FeedFilters.tsx               # Filter UI
│   └── useFeedFeedback.ts            # Feedback hook
└── spec/primitives/feed.md           # Feed specification

SUCCESS CRITERIA:
✓ 5 default feeds functional
✓ User can create custom feeds
✓ Attention tracking works
✓ Principles alignment scoring works
```

### Phase 2: File Explorer + Uploads (2 weeks)

```
DELIVERABLES:
├── impl/claude/services/sovereign/
│   ├── uploads.py                    # Upload staging
│   ├── integration.py                # Integration protocol
│   └── splitting.py                  # K-Block splitting
├── impl/claude/web/src/components/FileExplorer/
│   ├── FileExplorer.tsx              # Real file explorer
│   ├── UploadZone.tsx                # Drag-drop zone
│   └── IntegrationDialog.tsx         # Integration confirmation
└── spec/protocols/sovereign-uploads.md

SUCCESS CRITERIA:
✓ File explorer shows real directories
✓ Drag-drop into uploads/ works
✓ Moving from uploads/ triggers integration
✓ K-Block splitting suggestions appear
```

### Phase 3: FTUE (1 week)

```
DELIVERABLES:
├── impl/claude/web/src/pages/Genesis/
│   ├── GenesisPage.tsx               # Genesis witness
│   ├── FirstQuestion.tsx             # First K-Block creation
│   └── WelcomeToStudio.tsx           # Studio onboarding
├── impl/claude/protocols/api/onboarding.py
└── spec/ux/ftue.md

SUCCESS CRITERIA:
✓ Genesis visible and delightful
✓ First K-Block created < 90 seconds
✓ User enters studio with context
✓ Joy moments implemented
```

### Phase 4: Contradiction Engine (2 weeks)

```
DELIVERABLES:
├── impl/claude/services/contradiction/
│   ├── detection.py                  # Contradiction detection
│   ├── classification.py             # Strength classification
│   ├── resolution.py                 # Resolution options
│   └── ui.py                         # UI generation
├── impl/claude/web/src/components/Contradiction/
│   ├── ContradictionCard.tsx         # Contradiction display
│   └── ResolutionDialog.tsx          # Resolution UI
└── spec/protocols/contradiction.md

SUCCESS CRITERIA:
✓ Contradictions detected automatically
✓ Surfaced in dedicated feed
✓ Resolution options functional
✓ Synthesis creates new K-Blocks
```

### Phase 5: Heterarchical Tolerance (1 week)

```
DELIVERABLES:
├── impl/claude/services/edge/
│   ├── policy.py                     # Edge validation policy
│   └── quarantine.py                 # Nonsense quarantine
├── impl/claude/services/galois/
│   └── cross_layer.py                # Cross-layer loss computation
└── spec/protocols/heterarchy.md

SUCCESS CRITERIA:
✓ Cross-layer edges allowed
✓ Justification encouraged not required
✓ Quarantine works without blocking
✓ Performance unaffected by nonsense
```

---

## Part X: The Grand Equation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                        THE GRAND EQUATION                                   │
│                                                                             │
│   kgents = ZeroSeed × Feed × KBlock × Heterarchy × Contradiction            │
│                                                                             │
│   where:                                                                    │
│                                                                             │
│   ZeroSeed     = Genesis + Axioms + DesignLaws                              │
│   Feed         = Time × Attention × Principles × Coherence                   │
│   KBlock       = Trace × Surface × Justification                            │
│   Heterarchy   = CrossLayer + Tolerance + Adaptation                         │
│   Contradiction = Detection × Surfacing × Resolution × Growth               │
│                                                                             │
│   And the fundamental law:                                                  │
│                                                                             │
│   Agency(X) = ∫ Justification(X) dt                                         │
│                                                                             │
│   An agent is the integral of its justifications over time.                 │
│   The more you justify, the more you ARE.                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part XI: Orchestration Guide for Executing Agent

### How to Execute This Plan

1. **Read Prerequisites First** — Ensure full understanding of Constitution, Zero-Seed, K-Block, and Galois specs before starting.

2. **Execute Phases Sequentially** — Each phase builds on the previous. Don't skip.

3. **Use Sub-Agents for Parallel Work** — Within each phase, identify independent tasks and spawn sub-agents:
   - Backend sub-agent for Python services
   - Frontend sub-agent for React components
   - Spec sub-agent for documentation

4. **Verify Success Criteria** — Each phase has explicit success criteria. Don't proceed until met.

5. **Witness Your Decisions** — Every architectural choice should be marked. This plan is itself a demonstration of the system.

### Sub-Agent Spawn Pattern

```python
# Example orchestration for Phase 1
async def execute_phase_1():
    # Spawn parallel sub-agents
    backend_agent = await spawn_agent(
        type="general-purpose",
        prompt="""
        Implement the Feed primitive backend:
        - Create impl/claude/services/feed/core.py
        - Create impl/claude/services/feed/ranking.py
        - Create impl/claude/services/feed/feedback.py
        - Create impl/claude/services/feed/defaults.py

        Follow the specifications in this plan exactly.
        Ensure all code is type-hinted and tested.
        """,
    )

    frontend_agent = await spawn_agent(
        type="general-purpose",
        prompt="""
        Implement the Feed primitive frontend:
        - Create impl/claude/web/src/primitives/Feed/Feed.tsx
        - Create impl/claude/web/src/primitives/Feed/FeedItem.tsx
        - Create impl/claude/web/src/primitives/Feed/FeedFilters.tsx
        - Create impl/claude/web/src/primitives/Feed/useFeedFeedback.ts

        Follow the TypeScript interfaces in this plan exactly.
        Ensure responsive design and STARK BIOME styling.
        """,
    )

    # Wait for both
    await gather(backend_agent, frontend_agent)

    # Verify success criteria
    await verify_phase_1_criteria()
```

### Key Decisions to Make During Execution

| Decision Point | Options | Guidance |
|----------------|---------|----------|
| Database schema for feeds | Postgres JSON vs. separate tables | JSON for flexibility initially |
| Feed ranking algorithm | Simple weighted sum vs. ML model | Start simple, iterate |
| Contradiction threshold | 0.1 vs. higher/lower | Start at 0.1, tune based on usage |
| K-Block splitting trigger | Automatic vs. manual | Suggest, don't force (Linear philosophy) |
| FTUE animation style | Subtle vs. dramatic | Dramatic for Genesis, subtle thereafter |

---

## Closing

> *"The act of declaring, capturing, and auditing your decisions is itself a radical act of self-transformation."*

This is not a product specification. This is a **manifesto for self-aware software**.

The user doesn't use kgents. The user **becomes** through kgents.

Every K-Block is a declaration. Every edge is a justification. Every contradiction is an opportunity.

The system tolerates your mess. The system adapts to your will. The system shows you what is.

And in showing you, it invites you to become more than you were.

**Genesis awaits.**

---

*"The seed IS the garden."*

---

## Part XII: Post-Implementation Learnings (2025-12-25)

> *Added after 6-phase implementation QA by parallel exploration agents*

### 12.1 Implementation Status Summary

| Phase | Component | Completion | Notes |
|-------|-----------|------------|-------|
| 0 | Bootstrap Infrastructure | 85% | PostgreSQL persistence needs wiring |
| 1 | Feed Primitive | 85% | UI complete, AGENTESE wiring needed |
| 2 | File Explorer | 70% | 4/9 integration steps are TODO |
| 3 | FTUE | 95% | Flow complete, backend call needed |
| 4 | Contradiction Engine | 95% | Missing API endpoints |
| 5 | Heterarchical Tolerance | **100%** | All 38 tests passing ✅ |

### 12.2 Key Discoveries

#### Discovery 1: UI-First Implementation Pattern

The implementation naturally followed a **UI-first** pattern where:
1. React components were built with mock data
2. Python services were built with correct algorithms
3. The gap is **wiring** (AGENTESE calls, persistence)

**Implication**: Future phases should explicitly plan for wiring work.

#### Discovery 2: Ranking Weights (Empirical)

The Feed ranking algorithm uses these weights:

```python
RANKING_WEIGHTS = {
    'attention': 0.4,    # User behavior is primary signal
    'principles': 0.3,   # Alignment with 7 design principles
    'recency': 0.2,      # Freshness matters for feed
    'coherence': 0.1,    # Low-loss items get small boost
}
```

These emerged from implementation and should be documented as canonical.

#### Discovery 3: Integration Protocol Sync/Async

The 9-step integration protocol needs explicit sync/async marking:

| Step | Name | Type | Duration |
|------|------|------|----------|
| 1 | validate_sovereignty | Sync | <10ms |
| 2 | check_layer_affinity | Sync | <50ms |
| 3 | propose_edges | Sync | <100ms |
| 4 | integrate_into_cosmos | **Async** | Variable |
| 5 | witness_integration | **Async** | <50ms |
| 6 | check_galois_coherence | **Async** | Variable |
| 7-9 | cleanup | Sync | <50ms |

#### Discovery 4: Contradiction Threshold (τ)

The super-additive detection uses τ = 0.1:

```
L(A ∪ B) > L(A) + L(B) + τ
where τ = 0.1
```

This allows small noise while catching genuine contradictions.

### 12.3 TypeScript Gotchas Fixed

| File | Issue | Fix |
|------|-------|-----|
| WelcomeToStudio.tsx:83 | Unicode curly quote | Use double quotes |
| Feed.tsx:267 | Type narrowing | Add type assertion |
| FileExplorer.tsx | Unused import | Remove |

### 12.4 Reference Implementation

**Phase 5 (Heterarchical Tolerance)** is the gold standard:
- All 38 tests passing
- Complete spec at `spec/protocols/heterarchy.md`
- Clean edge policy levels (STRICT/SUGGESTED/OPTIONAL)
- Nonsense quarantine with 0.85 threshold

Other phases should follow this completion pattern.

### 12.5 Remaining Work (Prioritized)

1. **Wire PostgreSQL persistence** for K-Block creation (Phase 0)
2. **Wire Feed to AGENTESE** queries (Phase 1)
3. **Complete integration steps** 4-6, 9 (Phase 2)
4. **Add contradiction API endpoints** (Phase 4)
5. **Integration tests** across all phases

---

**Document Metadata**
- **Created**: 2025-12-25
- **Authors**: Kent Gang, Claude (Anthropic)
- **Status**: IMPLEMENTED (85% average completion)
- **Supersedes**: Previous witness architecture plans
- **Total Estimated Duration**: 9 weeks
- **Priority**: CRITICAL — This is the new foundation

---

## Cross-References

- `spec/protocols/zero-seed.md` — Canonical Zero Seed v3.0
- `spec/protocols/k-block.md` — K-Block specification
- `spec/theory/galois-modularization.md` — Galois loss theory
- `spec/theory/agent-dp.md` — Agent as Dynamic Programming
- `spec/principles/CONSTITUTION.md` — The 7+7 principles
- `NOW.md` — Current system state
