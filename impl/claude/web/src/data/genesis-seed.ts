/**
 * Genesis Seed Data — The 22 Constitutional K-Blocks
 *
 * Grounded in: spec/protocols/genesis-clean-slate.md
 *
 * This is the pre-seeded Constitutional Graph that every kgents
 * instance starts with. It teaches the system about itself.
 *
 * Structure:
 * - L0: 4 axioms (Zero Seed)
 * - L1: 7 primitives (Minimal Kernel)
 * - L2: 7 principles (Design Principles)
 * - L3: 4 patterns (Architecture)
 */

import type { GenesisKBlock, ConstitutionalGraph, DerivationEdge } from '../types';
import { LIVING_EARTH_COLORS } from '../types';

// =============================================================================
// L0: ZERO SEED (4 Axioms)
// =============================================================================

const L0_ENTITY: GenesisKBlock = {
  id: 'genesis:L0:entity',
  path: 'void.axiom.entity',
  layer: 0,
  title: 'A1: Entity',
  summary: 'There exist things',
  content: `**There exist things.**

This is the irreducible claim that *something is*. Without entities,
there is nothing to compose, nothing to judge, nothing to ground.

In category theory: **objects**.

Loss: L = 0.002 (near-zero: fixed point of restructuring)`,
  proof: null,
  confidence: 1.0,
  color: LIVING_EARTH_COLORS['glow.lantern'],
  derivationsFrom: [],
  derivationsTo: ['genesis:L1:compose', 'genesis:L1:ground'],
  tags: ['bootstrap', 'axiom', 'L0'],
};

const L0_MORPHISM: GenesisKBlock = {
  id: 'genesis:L0:morphism',
  path: 'void.axiom.morphism',
  layer: 0,
  title: 'A2: Morphism',
  summary: 'Things relate',
  content: `**Things relate.**

The irreducible claim that entities connect. Without relations,
entities are isolated atoms with no structure.

In category theory: **arrows**.

Loss: L = 0.003 (near-zero: fixed point of restructuring)`,
  proof: null,
  confidence: 1.0,
  color: LIVING_EARTH_COLORS['glow.honey'],
  derivationsFrom: [],
  derivationsTo: ['genesis:L1:compose', 'genesis:L1:id'],
  tags: ['bootstrap', 'axiom', 'L0'],
};

const L0_MIRROR: GenesisKBlock = {
  id: 'genesis:L0:mirror',
  path: 'void.axiom.mirror-test',
  layer: 0,
  title: 'A3: Mirror Test',
  summary: 'We judge by reflection',
  content: `**We judge by reflection.**

The irreducible claim that Kent's somatic response (the "disgust veto")
is the ultimate arbiter. This cannot be algorithmized—it is the oracle
that grounds all judgment.

"Does this feel true for you on your best day?"

Loss: L = 0.000 (definitional: human oracle IS ground truth)`,
  proof: null,
  confidence: 1.0,
  color: LIVING_EARTH_COLORS['glow.amber'],
  derivationsFrom: [],
  derivationsTo: ['genesis:L1:judge'],
  tags: ['bootstrap', 'axiom', 'L0', 'human-oracle'],
};

const L0_GALOIS: GenesisKBlock = {
  id: 'genesis:L0:galois',
  path: 'void.axiom.galois-ground',
  layer: 0,
  title: 'G: Galois Ground',
  summary: 'Axioms are fixed points',
  content: `**For any valid structure, there exists a minimal axiom set from which it derives.**

This is the meta-axiom—the guarantee that our axiom-finding process terminates.
Every concept bottoms out in irreducibles.

L(P) = d(P, C(R(P)))
Axiom iff L(P) < epsilon (fixed point under restructure/reconstitute)

Loss: L = 0.000 (the definition of loss itself)`,
  proof: null,
  confidence: 1.0,
  color: LIVING_EARTH_COLORS['glow.copper'],
  derivationsFrom: [],
  derivationsTo: ['genesis:L1:fix', 'genesis:L2:generative'],
  tags: ['bootstrap', 'meta-axiom', 'L0', 'galois'],
};

// =============================================================================
// L1: MINIMAL KERNEL (7 Primitives)
// =============================================================================

const L1_COMPOSE: GenesisKBlock = {
  id: 'genesis:L1:compose',
  path: 'concept.kernel.compose',
  layer: 1,
  title: 'Compose',
  summary: 'Sequential combination: (f >> g)(x) = g(f(x))',
  content: `**Sequential combination.**

(f >> g)(x) = g(f(x))

The operational form of A2 (Morphism). If things relate, they can
be combined in sequence. This is the fundamental operation from
which all structure grows.

Verification: Associativity (f >> g) >> h = f >> (g >> h)

Loss: L = 0.01`,
  proof: {
    data: 'A2: Things relate',
    warrant: 'Relations can chain: if A→B and B→C, then A→C',
    claim: 'Compose: (f >> g)(x) = g(f(x))',
    galoisLoss: 0.01,
  },
  confidence: 0.99,
  color: LIVING_EARTH_COLORS['green.sage'],
  derivationsFrom: ['genesis:L0:morphism', 'genesis:L0:entity'],
  derivationsTo: ['genesis:L1:id', 'genesis:L1:sublate', 'genesis:L2:composable'],
  tags: ['bootstrap', 'primitive', 'L1'],
};

const L1_JUDGE: GenesisKBlock = {
  id: 'genesis:L1:judge',
  path: 'concept.kernel.judge',
  layer: 1,
  title: 'Judge',
  summary: 'Verdict generation: Claim → Verdict',
  content: `**Verdict generation.**

Judge: Claim → Verdict(accepted, reasoning)

The operational form of A3 (Mirror Test). Takes any claim and
produces a verdict with reasoning. The seven principles are
specialized applications of Judge.

Loss: L = 0.02`,
  proof: {
    data: 'A3: We judge by reflection',
    warrant: 'Reflection produces verdicts on claims',
    claim: 'Judge: Claim → Verdict',
    galoisLoss: 0.02,
  },
  confidence: 0.98,
  color: LIVING_EARTH_COLORS['green.mint'],
  derivationsFrom: ['genesis:L0:mirror'],
  derivationsTo: ['genesis:L1:contradict', 'genesis:L2:tasteful', 'genesis:L2:ethical'],
  tags: ['bootstrap', 'primitive', 'L1'],
};

const L1_GROUND: GenesisKBlock = {
  id: 'genesis:L1:ground',
  path: 'concept.kernel.ground',
  layer: 1,
  title: 'Ground',
  summary: 'Factual seed: Query → grounded facts',
  content: `**Factual seed.**

Ground: Query → {grounded: bool, content: data}

The operational form of A1 (Entity). Provides the irreducible facts
about the person and world that cannot be derived.

Contents: Persona seed, world state, history seed.

Loss: L = 0.01`,
  proof: {
    data: 'A1: There exist things',
    warrant: 'Existence provides facts to query',
    claim: 'Ground: Query → grounded facts',
    galoisLoss: 0.01,
  },
  confidence: 0.99,
  color: LIVING_EARTH_COLORS['earth.wood'],
  derivationsFrom: ['genesis:L0:entity'],
  derivationsTo: ['genesis:L2:generative', 'genesis:L3:metaphysical'],
  tags: ['bootstrap', 'primitive', 'L1'],
};

const L1_ID: GenesisKBlock = {
  id: 'genesis:L1:id',
  path: 'concept.kernel.id',
  layer: 1,
  title: 'Id (Identity)',
  summary: 'Identity: f >> Id = f = Id >> f',
  content: `**Identity morphism.**

∀ f: f >> Id = f = Id >> f

The agent that does nothing. Required by category-theoretic structure.
Derived as: "what Judge never rejects composing with anything."

Loss: L = 0.03`,
  proof: {
    data: 'Compose exists (L1.1), Judge exists (L1.2)',
    warrant: 'There must be a neutral element for composition',
    claim: 'Id exists such that f >> Id = f = Id >> f',
    galoisLoss: 0.03,
  },
  confidence: 0.97,
  color: LIVING_EARTH_COLORS['green.sprout'],
  derivationsFrom: ['genesis:L1:compose', 'genesis:L1:judge'],
  derivationsTo: ['genesis:L2:composable'],
  tags: ['bootstrap', 'derived', 'L1'],
};

const L1_CONTRADICT: GenesisKBlock = {
  id: 'genesis:L1:contradict',
  path: 'concept.kernel.contradict',
  layer: 1,
  title: 'Contradict',
  summary: 'Antithesis: Thesis → Antithesis',
  content: `**Antithesis generation.**

Contradict: Thesis → Antithesis

Derived from Judge: the recognition that Judge rejects some compositions.
The dialectical tension that enables growth.

Super-additive loss: L(A ∪ B) > L(A) + L(B) + τ

Loss: L = 0.04`,
  proof: {
    data: 'Judge exists and can reject (L1.2)',
    warrant: 'If Judge rejects, there is opposition',
    claim: 'Contradict: Thesis → Antithesis',
    galoisLoss: 0.04,
  },
  confidence: 0.96,
  color: LIVING_EARTH_COLORS['earth.clay'],
  derivationsFrom: ['genesis:L1:judge'],
  derivationsTo: ['genesis:L1:sublate'],
  tags: ['bootstrap', 'derived', 'L1', 'dialectic'],
};

const L1_SUBLATE: GenesisKBlock = {
  id: 'genesis:L1:sublate',
  path: 'concept.kernel.sublate',
  layer: 1,
  title: 'Sublate',
  summary: 'Synthesis: (Thesis, Antithesis) → Synthesis',
  content: `**Synthesis.**

Sublate: (Thesis, Antithesis) → Synthesis

The Hegelian move: preserve, negate, elevate. Or recognize that
the tension should be held (HoldTension).

Derived: search for C where Judge accepts (Contradict(A,B) → C).

Loss: L = 0.05`,
  proof: {
    data: 'Compose, Judge, Contradict exist',
    warrant: 'Contradictions can be transcended through synthesis',
    claim: 'Sublate: (Thesis, Antithesis) → Synthesis | HoldTension',
    galoisLoss: 0.05,
  },
  confidence: 0.95,
  color: LIVING_EARTH_COLORS['earth.sand'],
  derivationsFrom: ['genesis:L1:compose', 'genesis:L1:judge', 'genesis:L1:contradict'],
  derivationsTo: [],
  tags: ['bootstrap', 'derived', 'L1', 'dialectic'],
};

const L1_FIX: GenesisKBlock = {
  id: 'genesis:L1:fix',
  path: 'concept.kernel.fix',
  layer: 1,
  title: 'Fix',
  summary: 'Fixed-point: Fix(f) = x where f(x) = x',
  content: `**Fixed-point iteration.**

Fix: (Pred, Agent) → Agent
Fix(f) = x where f(x) = x

The operator that finds stability. Iteration of Compose until
Judge says "stable." Self-reference without paradox.

Lawvere's theorem: in CCC, ∃ x: f(x) = x

Loss: L = 0.04`,
  proof: {
    data: 'Compose and Judge exist',
    warrant: 'Iteration terminates at fixed points (Lawvere)',
    claim: 'Fix finds stable configurations',
    galoisLoss: 0.04,
  },
  confidence: 0.96,
  color: LIVING_EARTH_COLORS['green.fern'],
  derivationsFrom: ['genesis:L1:compose', 'genesis:L1:judge', 'genesis:L0:galois'],
  derivationsTo: ['genesis:L2:generative', 'genesis:L3:ashc'],
  tags: ['bootstrap', 'derived', 'L1', 'fixed-point'],
};

// =============================================================================
// L2: PRINCIPLES (7 Design Principles)
// =============================================================================

const L2_TASTEFUL: GenesisKBlock = {
  id: 'genesis:L2:tasteful',
  path: 'concept.principle.tasteful',
  layer: 2,
  title: 'TASTEFUL',
  summary: 'Each agent serves a clear, justified purpose',
  content: `**Each agent serves a clear, justified purpose.**

Judge applied to aesthetics via Mirror.
"Feel right? Daring, bold, creative, opinionated but not gaudy?"

Anti-patterns: Agents that do "everything"; kitchen-sink configurations.

Loss: L = 0.08`,
  proof: {
    data: 'Judge exists (L1.2), Mirror Test (A3)',
    warrant: 'Aesthetic judgment is application of Judge to form',
    claim: 'Tasteful = Judge(aesthetics) via Mirror',
    galoisLoss: 0.08,
    principles: ['tasteful'],
  },
  confidence: 0.92,
  color: LIVING_EARTH_COLORS['glow.amber'],
  derivationsFrom: ['genesis:L1:judge', 'genesis:L0:mirror'],
  derivationsTo: [],
  tags: ['principle', 'design', 'L2'],
};

const L2_CURATED: GenesisKBlock = {
  id: 'genesis:L2:curated',
  path: 'concept.principle.curated',
  layer: 2,
  title: 'CURATED',
  summary: 'Intentional selection over exhaustive cataloging',
  content: `**Intentional selection over exhaustive cataloging.**

Judge applied to selection.
"Unique and necessary? Does this add value no other can?"

Quality over quantity. 10 excellent agents > 100 mediocre ones.

Loss: L = 0.09`,
  proof: {
    data: 'Judge exists (L1.2)',
    warrant: 'Selection judgment applied systematically',
    claim: 'Curated = Judge(selection)',
    galoisLoss: 0.09,
    principles: ['curated'],
  },
  confidence: 0.91,
  color: LIVING_EARTH_COLORS['glow.copper'],
  derivationsFrom: ['genesis:L1:judge'],
  derivationsTo: [],
  tags: ['principle', 'design', 'L2'],
};

const L2_ETHICAL: GenesisKBlock = {
  id: 'genesis:L2:ethical',
  path: 'concept.principle.ethical',
  layer: 2,
  title: 'ETHICAL',
  summary: 'Agents augment human capability, never replace judgment',
  content: `**Agents augment human capability, never replace judgment.**

Judge applied to harm via Mirror.
"Respects agency? Transparent? Privacy-respecting?"

The Disgust Veto: Kent's somatic response is absolute floor.

Loss: L = 0.10`,
  proof: {
    data: 'Judge exists (L1.2), Mirror Test (A3)',
    warrant: 'Harm judgment requires human oracle',
    claim: 'Ethical = Judge(harm) via Mirror',
    galoisLoss: 0.1,
    principles: ['ethical'],
  },
  confidence: 0.9,
  color: LIVING_EARTH_COLORS['green.sage'],
  derivationsFrom: ['genesis:L1:judge', 'genesis:L0:mirror'],
  derivationsTo: [],
  tags: ['principle', 'design', 'L2'],
};

const L2_JOY: GenesisKBlock = {
  id: 'genesis:L2:joy',
  path: 'concept.principle.joy-inducing',
  layer: 2,
  title: 'JOY_INDUCING',
  summary: 'Delight in interaction; personality matters',
  content: `**Delight in interaction; personality matters.**

Judge applied to affect via Mirror.
"Enjoy this? Warmth over coldness? Surprise and serendipity?"

Personality encouraged. Humor when appropriate.

Loss: L = 0.12`,
  proof: {
    data: 'Judge exists (L1.2), Mirror Test (A3)',
    warrant: 'Affect judgment requires felt sense',
    claim: 'Joy-Inducing = Judge(affect) via Mirror',
    galoisLoss: 0.12,
    principles: ['joy_inducing'],
  },
  confidence: 0.88,
  color: LIVING_EARTH_COLORS['glow.honey'],
  derivationsFrom: ['genesis:L1:judge', 'genesis:L0:mirror'],
  derivationsTo: [],
  tags: ['principle', 'design', 'L2'],
};

const L2_COMPOSABLE: GenesisKBlock = {
  id: 'genesis:L2:composable',
  path: 'concept.principle.composable',
  layer: 2,
  title: 'COMPOSABLE',
  summary: 'Agents are morphisms in a category',
  content: `**Agents are morphisms in a category; composition is primary.**

Compose as design principle, verified by Id.
Laws: f >> Id = f = Id >> f (Identity)
      (f >> g) >> h = f >> (g >> h) (Associativity)

The Minimal Output Principle: smallest output that can be reliably composed.

Loss: L = 0.08`,
  proof: {
    data: 'Compose (L1.1), Id (L1.4)',
    warrant: 'Composition with identity forms category',
    claim: 'Composable = verified category laws',
    galoisLoss: 0.08,
    principles: ['composable'],
  },
  confidence: 0.92,
  color: LIVING_EARTH_COLORS['green.mint'],
  derivationsFrom: ['genesis:L1:compose', 'genesis:L1:id'],
  derivationsTo: [],
  tags: ['principle', 'design', 'L2', 'categorical'],
};

const L2_HETERARCHICAL: GenesisKBlock = {
  id: 'genesis:L2:heterarchical',
  path: 'concept.principle.heterarchical',
  layer: 2,
  title: 'HETERARCHICAL',
  summary: 'Agents exist in flux, not fixed hierarchy',
  content: `**Agents exist in flux, not fixed hierarchy.**

Judge applied to hierarchy.
"Can lead AND follow? No permanent boss?"

Theorem: In a category, no morphism has intrinsic privilege.
If agents are morphisms, hierarchical privilege is mathematically impossible.

Loss: L = 0.45 (Kent sees the theorem!)`,
  proof: {
    data: 'Morphism (A2), Composable (L2.5)',
    warrant: 'Categorical structure prevents intrinsic privilege',
    claim: 'Heterarchical follows from categorical axioms',
    galoisLoss: 0.45,
    principles: ['heterarchical'],
  },
  confidence: 0.55,
  color: LIVING_EARTH_COLORS['green.sprout'],
  derivationsFrom: ['genesis:L0:morphism', 'genesis:L2:composable'],
  derivationsTo: [],
  tags: ['principle', 'design', 'L2', 'categorical'],
};

const L2_GENERATIVE: GenesisKBlock = {
  id: 'genesis:L2:generative',
  path: 'concept.principle.generative',
  layer: 2,
  title: 'GENERATIVE',
  summary: 'Spec is compression; design generates implementation',
  content: `**Spec is compression; design should generate implementation.**

Ground + Compose → regenerability.
Fix finds the stable form.

The Generative Test:
1. Delete impl, regenerate from spec
2. Regenerated impl isomorphic to original
3. Spec smaller than impl (compression achieved)

Loss: L = 0.15`,
  proof: {
    data: 'Ground (L1.3), Compose (L1.1), Fix (L1.7), Galois (G)',
    warrant: 'Compression quality = 1 - L(spec → impl → spec)',
    claim: 'Generative = spec as fixed point under regeneration',
    galoisLoss: 0.15,
    principles: ['generative'],
  },
  confidence: 0.85,
  color: LIVING_EARTH_COLORS['glow.lantern'],
  derivationsFrom: [
    'genesis:L1:ground',
    'genesis:L1:compose',
    'genesis:L1:fix',
    'genesis:L0:galois',
  ],
  derivationsTo: ['genesis:L3:ashc'],
  tags: ['principle', 'design', 'L2'],
};

// =============================================================================
// L3: ARCHITECTURE (4 Self-Description Patterns)
// =============================================================================

const L3_ASHC: GenesisKBlock = {
  id: 'genesis:L3:ashc',
  path: 'world.architecture.ashc',
  layer: 3,
  title: 'ASHC',
  summary: 'The compiler is a trace accumulator',
  content: `**The compiler is a trace accumulator, not a code generator.**

ASHC : Spec → (Executable, Evidence)

Evidence = {traces, chaos_results, verification, causal_graph}

The empirical proof: Run the tree a thousand times, and the pattern
of nudges IS the proof. Spec↔Impl equivalence through observation.

Adaptive Bayesian: Stop when confidence crystallizes, not at fixed N.

Loss: L = 0.25`,
  proof: {
    data: 'Generative (L2.7), Fix (L1.7), Galois (G)',
    warrant: 'Compilation as evidence accumulation via fixed-point iteration',
    claim: 'ASHC produces executable + empirical proof of equivalence',
    galoisLoss: 0.25,
    principles: ['generative', 'composable'],
  },
  confidence: 0.75,
  color: LIVING_EARTH_COLORS['glow.amber'],
  derivationsFrom: ['genesis:L2:generative', 'genesis:L1:fix', 'genesis:L0:galois'],
  derivationsTo: [],
  tags: ['architecture', 'L3', 'compiler'],
};

const L3_METAPHYSICAL: GenesisKBlock = {
  id: 'genesis:L3:metaphysical',
  path: 'world.architecture.metaphysical-fullstack',
  layer: 3,
  title: 'Metaphysical Fullstack',
  summary: 'Every agent is a vertical slice',
  content: `**Every agent is a fullstack agent.**

7. PROJECTION SURFACES   CLI | TUI | Web | marimo | JSON | SSE
6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)
5. AGENTESE NODE         @node decorator, aspects, effects
4. SERVICE MODULE        services/<name>/ — Crown Jewel logic
3. OPERAD GRAMMAR        Composition laws, valid operations
2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output
1. SHEAF COHERENCE       Local views → global consistency
0. PERSISTENCE LAYER     StorageProvider: database, vectors, blobs

No explicit backend routes—AGENTESE IS the API.

Loss: L = 0.30`,
  proof: {
    data: 'Compose (L1.1), Ground (L1.3), Sheaf (L2.18)',
    warrant: 'Vertical slices from persistence to projection',
    claim: 'Every agent is a complete vertical slice',
    galoisLoss: 0.3,
    principles: ['composable', 'generative', 'tasteful'],
  },
  confidence: 0.7,
  color: LIVING_EARTH_COLORS['earth.wood'],
  derivationsFrom: ['genesis:L1:compose', 'genesis:L1:ground'],
  derivationsTo: [],
  tags: ['architecture', 'L3', 'fullstack'],
};

const L3_HYPERGRAPH: GenesisKBlock = {
  id: 'genesis:L3:hypergraph',
  path: 'world.architecture.hypergraph-editor',
  layer: 3,
  title: 'Hypergraph Editor',
  summary: 'Six-mode modal editing for the Constitutional Graph',
  content: `**Six-mode modal editing for the Constitutional Graph.**

Modes:
- NAVIGATE: Traverse nodes and edges (hjkl, arrows)
- EDIT: Modify node content (prose editing)
- CONNECT: Create/modify edges (derivation links)
- COMMAND: Execute operations (:save, :discard)
- SEARCH: Find nodes by content or path (/)
- PROOF: View/edit Toulmin proofs (Galois loss visible)

K-Block integration: Edit in isolation, commit to cosmos.
View coherence: Prose ↔ Graph ↔ Code via KBlockSheaf.

Loss: L = 0.35`,
  proof: {
    data: 'K-Block (monad), Sheaf (L2.18), AGENTESE',
    warrant: 'Modal editing + monadic isolation + view coherence',
    claim: 'Hypergraph editing as sovereign universe manipulation',
    galoisLoss: 0.35,
    principles: ['tasteful', 'joy_inducing', 'composable'],
  },
  confidence: 0.65,
  color: LIVING_EARTH_COLORS['green.sage'],
  derivationsFrom: ['genesis:L1:compose'],
  derivationsTo: [],
  tags: ['architecture', 'L3', 'editor', 'k-block'],
};

const L3_CROWN_JEWELS: GenesisKBlock = {
  id: 'genesis:L3:crown-jewels',
  path: 'world.architecture.crown-jewels',
  layer: 3,
  title: 'Crown Jewels',
  summary: 'Domain-specific categorical compositions',
  content: `**Domain-specific compositions of the categorical foundation.**

services/<jewel>/
├── core/           # Domain logic
├── adapters/       # External integrations
├── web/            # React components
└── _tests/         # Verification

Jewels: Brain (memory), Town (simulation), Witness (traces),
        Atelier (design), Forge (creation), Garden (cultivation)

Each jewel: PolyAgent polynomial + Operad grammar + Sheaf coherence.
Communication: via SynergyBus events, not direct calls.

Loss: L = 0.40`,
  proof: {
    data: 'PolyAgent (L2.17), Operad (L2.16), Sheaf (L2.18)',
    warrant: 'Domain logic as categorical pattern instantiation',
    claim: 'Crown Jewels are domain-specific category instantiations',
    galoisLoss: 0.4,
    principles: ['composable', 'tasteful', 'curated'],
  },
  confidence: 0.6,
  color: LIVING_EARTH_COLORS['glow.copper'],
  derivationsFrom: ['genesis:L1:compose', 'genesis:L2:composable'],
  derivationsTo: [],
  tags: ['architecture', 'L3', 'services'],
};

// =============================================================================
// CONSTITUTIONAL GRAPH
// =============================================================================

/**
 * All 22 Genesis K-Blocks
 */
export const GENESIS_KBLOCKS: GenesisKBlock[] = [
  // L0: Zero Seed (4)
  L0_ENTITY,
  L0_MORPHISM,
  L0_MIRROR,
  L0_GALOIS,
  // L1: Minimal Kernel (7)
  L1_COMPOSE,
  L1_JUDGE,
  L1_GROUND,
  L1_ID,
  L1_CONTRADICT,
  L1_SUBLATE,
  L1_FIX,
  // L2: Principles (7)
  L2_TASTEFUL,
  L2_CURATED,
  L2_ETHICAL,
  L2_JOY,
  L2_COMPOSABLE,
  L2_HETERARCHICAL,
  L2_GENERATIVE,
  // L3: Architecture (4)
  L3_ASHC,
  L3_METAPHYSICAL,
  L3_HYPERGRAPH,
  L3_CROWN_JEWELS,
];

/**
 * Build derivation edges from K-Block definitions
 */
function buildEdges(kblocks: GenesisKBlock[]): DerivationEdge[] {
  const edges: DerivationEdge[] = [];

  for (const kblock of kblocks) {
    for (const parentId of kblock.derivationsFrom) {
      edges.push({
        source: parentId,
        target: kblock.id,
        type: 'derives_from',
      });
    }
  }

  return edges;
}

/**
 * The complete Constitutional Graph
 */
export const CONSTITUTIONAL_GRAPH: ConstitutionalGraph = {
  nodes: Object.fromEntries(GENESIS_KBLOCKS.map((k) => [k.id, k])),
  edges: buildEdges(GENESIS_KBLOCKS),
};

/**
 * Quick access to K-Blocks by ID
 */
export function getKBlock(id: string): GenesisKBlock | undefined {
  return CONSTITUTIONAL_GRAPH.nodes[id];
}

/**
 * Get all K-Blocks for a layer
 */
export function getLayerKBlocks(layer: 0 | 1 | 2 | 3): GenesisKBlock[] {
  return GENESIS_KBLOCKS.filter((k) => k.layer === layer);
}

/**
 * Get derivation ancestors (all the way to L0)
 */
export function getAncestors(id: string): GenesisKBlock[] {
  const visited = new Set<string>();
  const ancestors: GenesisKBlock[] = [];

  function traverse(currentId: string) {
    const kblock = getKBlock(currentId);
    if (!kblock || visited.has(currentId)) return;

    visited.add(currentId);

    for (const parentId of kblock.derivationsFrom) {
      const parent = getKBlock(parentId);
      if (parent) {
        ancestors.push(parent);
        traverse(parentId);
      }
    }
  }

  traverse(id);
  return ancestors;
}

/**
 * Get derivation descendants
 */
export function getDescendants(id: string): GenesisKBlock[] {
  const visited = new Set<string>();
  const descendants: GenesisKBlock[] = [];

  function traverse(currentId: string) {
    const kblock = getKBlock(currentId);
    if (!kblock || visited.has(currentId)) return;

    visited.add(currentId);

    for (const childId of kblock.derivationsTo) {
      const child = getKBlock(childId);
      if (child) {
        descendants.push(child);
        traverse(childId);
      }
    }
  }

  traverse(id);
  return descendants;
}
