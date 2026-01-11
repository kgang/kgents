/**
 * GenesisView - Special View for Constitutional Genesis
 *
 * Shows the constitutional genesis moment:
 * - The 22 original Constitutional K-Blocks
 * - Why each was chosen
 * - The minimal kernel derivation
 * - The "Day Four" moment
 *
 * STARK BIOME: 90% steel, 10% earned amber glow.
 */

import { memo, useState } from 'react';
import { X, Sparkles, FileText, ChevronDown, ChevronRight, Layers } from 'lucide-react';

import { HISTORY_LAYER_COLORS, HISTORY_LAYER_NAMES } from './types';

// =============================================================================
// Types
// =============================================================================

interface GenesisViewProps {
  onClose: () => void;
}

interface GenesisKBlock {
  id: string;
  title: string;
  layer: number;
  description: string;
  reasoning: string;
  derivedFrom?: string[];
}

// =============================================================================
// Mock Genesis Data - The 22 Original K-Blocks
// =============================================================================

const GENESIS_KBLOCKS: GenesisKBlock[] = [
  // Layer 0: Irreducibles (5)
  {
    id: 'composable',
    title: 'COMPOSABLE',
    layer: 0,
    description: 'Agents are morphisms in a category. They compose via >> operator.',
    reasoning: 'Foundation of all agent interaction. Without composability, no system.',
  },
  {
    id: 'ethical',
    title: 'ETHICAL',
    layer: 0,
    description: 'Agents augment human capability, never replace judgment.',
    reasoning: 'The red line. Agents serve humans, not the reverse.',
  },
  {
    id: 'tasteful',
    title: 'TASTEFUL',
    layer: 0,
    description: 'Each agent serves a clear, justified purpose.',
    reasoning: 'Prevents bloat. Every feature must earn its place.',
  },
  {
    id: 'curated',
    title: 'CURATED',
    layer: 0,
    description: 'Intentional selection over exhaustive cataloging.',
    reasoning: 'Quality over quantity. Depth over breadth.',
  },
  {
    id: 'generative',
    title: 'GENERATIVE',
    layer: 0,
    description: 'Spec is compression. The constitution generates the system.',
    reasoning: 'The spec IS the implementation, in a more economical form.',
  },

  // Layer 1: Primitives (6)
  {
    id: 'heterarchical',
    title: 'HETERARCHICAL',
    layer: 1,
    description: 'Agents exist in flux, not fixed hierarchy.',
    reasoning: 'Rigid hierarchies break. Heterarchies adapt.',
    derivedFrom: ['composable'],
  },
  {
    id: 'witnessable',
    title: 'WITNESSABLE',
    layer: 1,
    description: 'Every significant action leaves a trace.',
    reasoning: 'Accountability requires visibility. No dark corners.',
    derivedFrom: ['ethical'],
  },
  {
    id: 'joy-inducing',
    title: 'JOY_INDUCING',
    layer: 1,
    description: 'Delight in interaction is a requirement, not a bonus.',
    reasoning: "The Anti-Sausage Protocol: Kent's voice preserved.",
    derivedFrom: ['tasteful'],
  },
  {
    id: 'minimal',
    title: 'MINIMAL',
    layer: 1,
    description: 'Minimal viable trace. Minimal viable output.',
    reasoning: 'LLM context is precious. Every token must earn its place.',
    derivedFrom: ['composable', 'tasteful'],
  },
  {
    id: 'polynomial',
    title: 'POLYNOMIAL',
    layer: 1,
    description: 'State machines with mode-dependent inputs.',
    reasoning: 'PolyAgent[S,A,B] > Agent[A,B]. Modes are powerful.',
    derivedFrom: ['composable'],
  },
  {
    id: 'dialectical',
    title: 'DIALECTICAL',
    layer: 1,
    description: 'Thesis, antithesis, synthesis. Contradiction is productive.',
    reasoning: 'Kent and Claude disagree. That disagreement creates.',
    derivedFrom: ['ethical', 'curated'],
  },

  // Layer 2: Derived (6)
  {
    id: 'agentese',
    title: 'AGENTESE',
    layer: 2,
    description: 'The verb-first ontology. world.*, self.*, concept.*, void.*, time.*',
    reasoning: 'The noun is a lie. There is only the rate of change.',
    derivedFrom: ['composable', 'heterarchical'],
  },
  {
    id: 'witness-protocol',
    title: 'Witness Protocol',
    layer: 2,
    description: 'Mark, Crystal, Decision Fusion. The witnessing system.',
    reasoning: 'Decisions without traces are reflexes. With traces, agency.',
    derivedFrom: ['witnessable', 'dialectical'],
  },
  {
    id: 'polyagent-spec',
    title: 'PolyAgent Spec',
    layer: 2,
    description: 'Formal specification of polynomial state machines.',
    reasoning: 'Abstract once, instantiate everywhere. Towns, Games, UIs.',
    derivedFrom: ['polynomial'],
  },
  {
    id: 'operad-grammar',
    title: 'Operad Grammar',
    layer: 2,
    description: 'Composition laws. Valid operations. Associativity.',
    reasoning: 'Operads define grammar; algebras apply grammar to systems.',
    derivedFrom: ['composable', 'polynomial'],
  },
  {
    id: 'sheaf-coherence',
    title: 'Sheaf Coherence',
    layer: 2,
    description: 'Local views glue into global consistency.',
    reasoning: 'Sheaf gluing = emergence. Compatible locals to global.',
    derivedFrom: ['heterarchical'],
  },
  {
    id: 'galois-connection',
    title: 'Galois Connection',
    layer: 2,
    description: 'Adjunctions between layers. Loss measurement.',
    reasoning: 'What is lost in derivation? The Galois loss tracks it.',
    derivedFrom: ['generative'],
  },

  // Layer 3: Architecture (5)
  {
    id: 'crown-jewels',
    title: 'Crown Jewels',
    layer: 3,
    description: 'Brain, Town, Witness, Atelier, Liminal. The five jewels.',
    reasoning: 'Post-extinction focus. These five, nothing more.',
    derivedFrom: ['curated', 'minimal'],
  },
  {
    id: 'metaphysical-fullstack',
    title: 'Metaphysical Fullstack',
    layer: 3,
    description: '7 layers from persistence to projection.',
    reasoning: 'Every agent is fullstack. No partial definitions.',
    derivedFrom: ['agentese', 'polyagent-spec'],
  },
  {
    id: 'data-buses',
    title: 'Data Buses',
    layer: 3,
    description: 'DataBus, SynergyBus, EventBus. Event-driven architecture.',
    reasoning: 'Timer loops create zombies. Events create life.',
    derivedFrom: ['heterarchical', 'composable'],
  },
  {
    id: 'elastic-ui',
    title: 'Elastic UI',
    layer: 3,
    description: 'Compact/Comfortable/Spacious. Density-aware rendering.',
    reasoning: 'One component, many surfaces. Project everywhere.',
    derivedFrom: ['joy-inducing', 'minimal'],
  },
  {
    id: 'di-container',
    title: 'DI Container',
    layer: 3,
    description: 'Dependency injection with fail-fast semantics.',
    reasoning: 'Required deps fail at import. Optional deps gracefully skip.',
    derivedFrom: ['composable', 'minimal'],
  },
];

// =============================================================================
// K-Block Card Component
// =============================================================================

interface KBlockCardProps {
  kblock: GenesisKBlock;
  isExpanded: boolean;
  onToggle: () => void;
}

const KBlockCard = memo(function KBlockCard({ kblock, isExpanded, onToggle }: KBlockCardProps) {
  const layerColor = HISTORY_LAYER_COLORS[kblock.layer as keyof typeof HISTORY_LAYER_COLORS];
  const layerName = HISTORY_LAYER_NAMES[kblock.layer as keyof typeof HISTORY_LAYER_NAMES];

  return (
    <div
      className={`genesis-kblock ${isExpanded ? 'genesis-kblock--expanded' : ''}`}
      style={{ '--layer-color': layerColor } as React.CSSProperties}
    >
      <button className="genesis-kblock__header" onClick={onToggle}>
        <div className="genesis-kblock__layer">
          <span className="genesis-kblock__layer-num">L{kblock.layer}</span>
          <span className="genesis-kblock__layer-name">{layerName}</span>
        </div>
        <span className="genesis-kblock__title">{kblock.title}</span>
        {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </button>

      {isExpanded && (
        <div className="genesis-kblock__content">
          <p className="genesis-kblock__description">{kblock.description}</p>
          <div className="genesis-kblock__reasoning">
            <span className="genesis-kblock__reasoning-label">Why?</span>
            <p>{kblock.reasoning}</p>
          </div>
          {kblock.derivedFrom && kblock.derivedFrom.length > 0 && (
            <div className="genesis-kblock__derivation">
              <span className="genesis-kblock__derivation-label">Derived from:</span>
              <div className="genesis-kblock__derivation-links">
                {kblock.derivedFrom.map((id) => (
                  <span key={id} className="genesis-kblock__derivation-link">
                    {id}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const GenesisView = memo(function GenesisView({ onClose }: GenesisViewProps) {
  const [expandedBlocks, setExpandedBlocks] = useState<Set<string>>(new Set());

  const toggleBlock = (id: string) => {
    setExpandedBlocks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const expandAll = () => {
    setExpandedBlocks(new Set(GENESIS_KBLOCKS.map((k) => k.id)));
  };

  const collapseAll = () => {
    setExpandedBlocks(new Set());
  };

  // Group by layer
  const kblocksByLayer = GENESIS_KBLOCKS.reduce(
    (acc, kblock) => {
      if (!acc[kblock.layer]) acc[kblock.layer] = [];
      acc[kblock.layer].push(kblock);
      return acc;
    },
    {} as Record<number, GenesisKBlock[]>
  );

  return (
    <div className="genesis-view">
      {/* Header */}
      <div className="genesis-view__header">
        <div className="genesis-view__title-area">
          <Sparkles size={18} className="genesis-view__icon" />
          <h2 className="genesis-view__title">Constitutional Genesis</h2>
        </div>
        <button className="genesis-view__close" onClick={onClose} aria-label="Close genesis view">
          <X size={16} />
        </button>
      </div>

      {/* Day Four Quote */}
      <div className="genesis-view__quote">
        <blockquote>
          "Day Four: The constitution emerged from first principles. 22 K-Blocks form the minimal
          kernel from which all else derives."
        </blockquote>
        <cite>— Kent, October 2025</cite>
      </div>

      {/* Controls */}
      <div className="genesis-view__controls">
        <button className="genesis-view__control-btn" onClick={expandAll}>
          Expand All
        </button>
        <button className="genesis-view__control-btn" onClick={collapseAll}>
          Collapse All
        </button>
        <span className="genesis-view__count">
          <FileText size={12} />
          {GENESIS_KBLOCKS.length} K-Blocks
        </span>
      </div>

      {/* K-Blocks by Layer */}
      <div className="genesis-view__layers">
        {[0, 1, 2, 3].map((layer) => {
          const layerBlocks = kblocksByLayer[layer] || [];
          if (layerBlocks.length === 0) return null;

          const layerColor = HISTORY_LAYER_COLORS[layer as keyof typeof HISTORY_LAYER_COLORS];
          const layerName = HISTORY_LAYER_NAMES[layer as keyof typeof HISTORY_LAYER_NAMES];

          return (
            <div key={layer} className="genesis-view__layer">
              <div
                className="genesis-view__layer-header"
                style={{ '--layer-color': layerColor } as React.CSSProperties}
              >
                <Layers size={14} />
                <span className="genesis-view__layer-badge">L{layer}</span>
                <span className="genesis-view__layer-name">{layerName}</span>
                <span className="genesis-view__layer-count">{layerBlocks.length}</span>
              </div>
              <div className="genesis-view__layer-blocks">
                {layerBlocks.map((kblock) => (
                  <KBlockCard
                    key={kblock.id}
                    kblock={kblock}
                    isExpanded={expandedBlocks.has(kblock.id)}
                    onToggle={() => toggleBlock(kblock.id)}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Derivation Summary */}
      <div className="genesis-view__summary">
        <h3>The Minimal Kernel</h3>
        <p>
          These 22 K-Blocks form the <em>minimal kernel</em> of the kgents constitution. Every
          feature, every agent, every line of code derives from this foundation.
        </p>
        <p>
          L0 irreducibles cannot be derived further. L1-L3 show explicit derivation chains. The
          Galois connection measures information preserved across layers.
        </p>
      </div>
    </div>
  );
});
