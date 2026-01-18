# UX Flow: Genesis (First-Time User)

> *"Genesis is self-description, not interrogation."*

**Status**: Active Plan
**Date**: 2026-01-17
**Spec**: genesis-clean-slate.md
**Principles**: Generative, Tasteful, Joy-Inducing

---

## The Problem We're Solving

Traditional onboarding:
```
Welcome! → Tell us about yourself → What do you do? → Configure preferences → Empty dashboard
```

This is **extractive**. The user provides value before receiving any. The blank dashboard is paralysis.

---

## The Genesis Alternative

```
Welcome! → Here's the Constitutional Graph → Explore layers → Trace derivations → When ready, extend
```

The system **gives first**. The user explores a pre-populated, self-describing structure. Their first action is curiosity, not data entry.

---

## The Flow

### Phase 0: Landing (0-3 seconds)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                                 kgents                                          │
│                                                                                 │
│                    The system already knows itself.                             │
│                    Your job is to explore—and then extend.                      │
│                                                                                 │
│                         [Enter the Garden ↓]                                    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Design Notes**:
- One button. One action. No "Sign up" or "Learn more."
- Button text is invitational, not transactional
- Background: subtle Constitutional Graph animation (nodes gently breathing)

### Phase 1: Zero Seed Reveal (3-30 seconds)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ L0: ZERO SEED                                        The irreducible axioms    │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│   ◉ A1: Entity           "There exist things"                      [→]         │
│   ◉ A2: Morphism         "Things relate"                           [→]         │
│   ◉ A3: Mirror Test      "We judge by reflection"                  [→]         │
│   ◉ G: Galois Ground     "Axioms are fixed points"                 [→]         │
│                                                                                 │
│   These four axioms are the irreducible foundation.                             │
│   Everything else derives from them.                                            │
│                                                                                 │
│   ────────────────────────────────────────────────────────────────────────────  │
│   Layer: L0 ━━━━━━━━━━━━━━━━━━ L1 ─────────── L2 ─────────── L3                 │
│                                                                                 │
│   [↓ Explore L1: Minimal Kernel]                                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Interaction**:
- Click any axiom → K-Block panel slides in with full content
- Layer bar shows position in derivation hierarchy
- Axiom nodes glow warm (LIVING_EARTH palette)

### Phase 2: Axiom Deep Dive (30-90 seconds)

When user clicks an axiom (e.g., A3: Mirror Test):

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ ← L0                                                                    AXIOM  │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ A3: Mirror Test                                                                 │
│ ═══════════════                                                                 │
│                                                                                 │
│ > "We judge by reflection."                                                     │
│                                                                                 │
│ The irreducible claim that Kent's somatic response (the "disgust veto")         │
│ is the ultimate arbiter. This cannot be algorithmized—it is the oracle          │
│ that grounds all judgment.                                                      │
│                                                                                 │
│ "Does this feel true for you on your best day?"                                 │
│                                                                                 │
│ ────────────────────────────────────────────────────────────────────────────    │
│                                                                                 │
│ DERIVES TO:                                                                     │
│ ┌─────────────────────────────────────────────────────────────────────────┐     │
│ │ L1: Judge       "Verdict generation"                           [→]     │     │
│ │ L2: TASTEFUL    "Judge applied to aesthetics"                  [→]     │     │
│ │ L2: ETHICAL     "Judge applied to harm"                        [→]     │     │
│ │ L2: JOY_INDUCING "Judge applied to affect"                     [→]     │     │
│ └─────────────────────────────────────────────────────────────────────────┘     │
│                                                                                 │
│ Galois Loss: L = 0.000 (definitional: human oracle IS ground truth)             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Key Insights Revealed**:
- Axioms have no proof (they ARE the proof)
- Derivation edges are visible and clickable
- User can trace forward (what derives from this?) or backward (what does this derive from?)

### Phase 3: Layer Traversal (90 seconds - 3 minutes)

User presses [↓ Explore L1] or clicks a derived K-Block:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ L1: MINIMAL KERNEL                                     Operational primitives   │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│   ◉ Compose      "Sequential combination: (f >> g)(x) = g(f(x))"       [→]     │
│   ◉ Judge        "Verdict generation: Claim → Verdict"                 [→]     │
│   ◉ Ground       "Factual seed: Query → grounded facts"                [→]     │
│   ◉ Id           "Identity: f >> Id = f = Id >> f"                     [→]     │
│   ◉ Contradict   "Antithesis: Thesis → Antithesis"                     [→]     │
│   ◉ Sublate      "Synthesis: (Thesis, Antithesis) → Synthesis"         [→]     │
│   ◉ Fix          "Fixed-point: Fix(f) = x where f(x) = x"              [→]     │
│                                                                                 │
│   The operational forms of the axioms. Compose + Judge + Ground are             │
│   the irreducible operations; Id, Contradict, Sublate, Fix derive from them.   │
│                                                                                 │
│   ────────────────────────────────────────────────────────────────────────────  │
│   Layer: L0 ─────────── L1 ━━━━━━━━━━━━━━━━━━ L2 ─────────── L3                 │
│                                                                                 │
│   [↑ Back to L0]  [↓ Explore L2: Principles]                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 4: Pattern Recognition (3-5 minutes)

By L2 (Principles), user begins to see the pattern:

```
"Oh, TASTEFUL is just Judge applied to aesthetics."
"COMPOSABLE is Compose + Id with verified laws."
"Everything traces back to those four axioms."
```

This is the **aha moment**. The system reveals its own structure.

### Phase 5: First Extension (5+ minutes)

When ready, user creates their first personal K-Block:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ YOUR FIRST DECLARATION                                                          │
│ ─────────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
│ The Constitutional Graph is the foundation.                                     │
│ Now add YOUR first axiom.                                                       │
│                                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                                                                             │ │
│ │  Build software that feels alive                                            │ │
│ │  ▌                                                                          │ │
│ │                                                                             │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│ Derives from: [A1: Entity ✓] [A3: Mirror ✓] [+ Add derivation]                  │
│                                                                                 │
│ ────────────────────────────────────────────────────────────────────────────    │
│                                                                                 │
│ Does this feel true for you on your best day?                                   │
│                                                                                 │
│ [Accept as L1 Axiom]    [Reframe]    [Think More]                               │
│                                                                                 │
│ This will become a personal axiom in YOUR graph.                                │
│ It needs no proof—only your acceptance.                                         │
│ Galois Loss: L = 0.000 (you are the oracle)                                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**The Mirror Test Integration**:
- User's first declaration becomes L1 axiom
- No proof required—Mirror Test IS the proof
- Derivation edges link to Constitutional foundation
- First witness mark: `km "First declaration" --tag genesis`

---

## Implementation Notes

### Component Structure

```tsx
// pages/GenesisPage.tsx
export function GenesisPage() {
  const [phase, setPhase] = useState<'landing' | 'explore' | 'extend'>('landing');
  const [currentLayer, setCurrentLayer] = useState(0);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  return (
    <div className="genesis-page">
      {phase === 'landing' && <GenesisLanding onEnter={() => setPhase('explore')} />}
      {phase === 'explore' && (
        <ConstitutionalExplorer
          layer={currentLayer}
          selectedNode={selectedNode}
          onNavigate={setSelectedNode}
          onLayerChange={setCurrentLayer}
          onReadyToExtend={() => setPhase('extend')}
        />
      )}
      {phase === 'extend' && <FirstDeclaration onComplete={handleComplete} />}
    </div>
  );
}
```

### Data Requirements

1. **Pre-seeded Constitutional Graph**: 22 K-Blocks at `/api/genesis/constitution`
2. **Layer navigation**: `GET /api/genesis/layer/{n}`
3. **K-Block detail**: `GET /api/genesis/node/{id}`
4. **First extension**: `POST /api/genesis/extend`

### Witnessing

Every Genesis interaction is witnessed:
- `genesis.enter` — User enters the garden
- `genesis.explore.layer` — User navigates to a layer
- `genesis.explore.node` — User inspects a K-Block
- `genesis.extend` — User creates first declaration

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to first layer navigation | < 10 seconds |
| Time to pattern recognition | < 3 minutes |
| Time to first extension | < 5 minutes |
| Completion rate (landing → first extension) | > 60% |

---

## Next Steps

1. Implement `GenesisPage` component
2. Seed Constitutional Graph in backend
3. Wire up witness events
4. Design LIVING_EARTH color application
5. Add breathing animations for axiom nodes

---

*"The system illuminates, not enforces."*
