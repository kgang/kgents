/**
 * GameKernelEditor - Displays and edits the 4 axioms + derived values
 *
 * "The kernel is the constitutional foundation. Every mechanic derives from here."
 *
 * Left panel in Create Mode. Shows:
 * - A1-A4 axioms as expandable cards
 * - Derived values with their lineage
 * - Health indicator for the overall kernel
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState } from 'react';
import { Shield, Target, TrendingUp, Layers, ChevronDown, ChevronRight, Zap } from 'lucide-react';
import type { GameKernel, Axiom, GameValue } from './types';

// =============================================================================
// Types
// =============================================================================

export interface GameKernelEditorProps {
  /** The game kernel to display/edit */
  kernel: GameKernel;
  /** Called when an axiom is selected for detail view */
  onAxiomSelect: (axiomId: string) => void;
  /** Called when a value is selected */
  onValueSelect?: (valueId: string) => void;
  /** Currently selected axiom ID */
  selectedAxiomId?: string | null;
  /** Whether editing is enabled */
  editable?: boolean;
}

// =============================================================================
// Axiom Icons
// =============================================================================

const AXIOM_ICONS: Record<string, typeof Shield> = {
  A1: Target, // Agency - choices hit their mark
  A2: Shield, // Attribution - clear cause/effect
  A3: TrendingUp, // Mastery - skill rewards
  A4: Layers, // Composition - clean layering
};

const AXIOM_COLORS: Record<string, string> = {
  A1: '#c4a77d', // Amber - agency glows
  A2: '#6b8b6b', // Sage - attribution grounds
  A3: '#8b7355', // Earth - mastery builds
  A4: '#a39890', // Steel - composition structures
};

// =============================================================================
// Subcomponents
// =============================================================================

interface AxiomCardProps {
  axiom: Axiom;
  isSelected: boolean;
  isExpanded: boolean;
  onSelect: () => void;
  onToggleExpand: () => void;
}

const AxiomCard = memo(function AxiomCard({
  axiom,
  isSelected,
  isExpanded,
  onSelect,
  onToggleExpand,
}: AxiomCardProps) {
  const Icon = AXIOM_ICONS[axiom.id] || Shield;
  const color = AXIOM_COLORS[axiom.id] || '#c4a77d';

  return (
    <div
      className={`kernel-axiom ${isSelected ? 'kernel-axiom--selected' : ''}`}
      style={{ '--axiom-color': color } as React.CSSProperties}
    >
      <button className="kernel-axiom__header" onClick={onSelect}>
        <div className="kernel-axiom__icon">
          <Icon size={14} />
        </div>
        <div className="kernel-axiom__info">
          <span className="kernel-axiom__id">{axiom.id}</span>
          <span className="kernel-axiom__name">{axiom.name}</span>
        </div>
        <div className="kernel-axiom__confidence">
          <span
            className="kernel-axiom__confidence-bar"
            style={{ width: `${axiom.confidence * 100}%` }}
          />
          <span className="kernel-axiom__confidence-value">
            {Math.round(axiom.confidence * 100)}%
          </span>
        </div>
        <button
          className="kernel-axiom__expand"
          onClick={(e) => {
            e.stopPropagation();
            onToggleExpand();
          }}
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
        >
          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </button>
      </button>

      {isExpanded && (
        <div className="kernel-axiom__body">
          <p className="kernel-axiom__statement">{axiom.statement}</p>
          <p className="kernel-axiom__description">{axiom.description}</p>
          {axiom.evidence.length > 0 && (
            <div className="kernel-axiom__evidence">
              <span className="kernel-axiom__evidence-label">Evidence:</span>
              <ul className="kernel-axiom__evidence-list">
                {axiom.evidence.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
});

interface ValueCardProps {
  value: GameValue;
  isSelected: boolean;
  onSelect: () => void;
  axiomNames: Record<string, string>;
}

const ValueCard = memo(function ValueCard({
  value,
  isSelected,
  onSelect,
  axiomNames,
}: ValueCardProps) {
  return (
    <button
      className={`kernel-value ${isSelected ? 'kernel-value--selected' : ''}`}
      onClick={onSelect}
    >
      <div className="kernel-value__header">
        <span className="kernel-value__id">{value.id}</span>
        <span className="kernel-value__name">{value.name}</span>
        <span className="kernel-value__strength">{Math.round(value.strength * 100)}%</span>
      </div>
      <p className="kernel-value__description">{value.description}</p>
      <div className="kernel-value__derivation">
        <span className="kernel-value__derivation-label">From:</span>
        {value.derivedFrom.map((axiomId) => (
          <span
            key={axiomId}
            className="kernel-value__axiom-badge"
            style={{ borderColor: AXIOM_COLORS[axiomId] }}
          >
            {axiomId}: {axiomNames[axiomId] || axiomId}
          </span>
        ))}
      </div>
    </button>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const GameKernelEditor = memo(function GameKernelEditor({
  kernel,
  onAxiomSelect,
  onValueSelect,
  selectedAxiomId,
  editable: _editable = false,
}: GameKernelEditorProps) {
  const [expandedAxioms, setExpandedAxioms] = useState<Set<string>>(new Set());
  const [selectedValueId, setSelectedValueId] = useState<string | null>(null);

  const axioms: Axiom[] = [kernel.agency, kernel.attribution, kernel.mastery, kernel.composition];

  const axiomNames: Record<string, string> = {
    A1: kernel.agency.name,
    A2: kernel.attribution.name,
    A3: kernel.mastery.name,
    A4: kernel.composition.name,
  };

  const toggleExpand = (axiomId: string) => {
    setExpandedAxioms((prev) => {
      const next = new Set(prev);
      if (next.has(axiomId)) {
        next.delete(axiomId);
      } else {
        next.add(axiomId);
      }
      return next;
    });
  };

  const handleValueSelect = (valueId: string) => {
    setSelectedValueId(valueId);
    onValueSelect?.(valueId);
  };

  return (
    <div className="game-kernel-editor">
      {/* Header */}
      <div className="game-kernel-editor__header">
        <Zap size={14} className="game-kernel-editor__icon" />
        <span className="game-kernel-editor__title">GameKernel</span>
        <span className="game-kernel-editor__health">
          <span
            className="game-kernel-editor__health-bar"
            style={{ width: `${kernel.health * 100}%` }}
          />
          <span className="game-kernel-editor__health-value">
            {Math.round(kernel.health * 100)}%
          </span>
        </span>
      </div>

      {/* Axioms Section */}
      <div className="game-kernel-editor__section">
        <div className="game-kernel-editor__section-header">
          <span className="game-kernel-editor__section-title">Axioms</span>
          <span className="game-kernel-editor__section-count">4</span>
        </div>
        <div className="game-kernel-editor__axioms">
          {axioms.map((axiom) => (
            <AxiomCard
              key={axiom.id}
              axiom={axiom}
              isSelected={selectedAxiomId === axiom.id}
              isExpanded={expandedAxioms.has(axiom.id)}
              onSelect={() => onAxiomSelect(axiom.id)}
              onToggleExpand={() => toggleExpand(axiom.id)}
            />
          ))}
        </div>
      </div>

      {/* Values Section */}
      <div className="game-kernel-editor__section">
        <div className="game-kernel-editor__section-header">
          <span className="game-kernel-editor__section-title">Values</span>
          <span className="game-kernel-editor__section-count">{kernel.values.length}</span>
        </div>
        <div className="game-kernel-editor__values">
          {kernel.values.map((value) => (
            <ValueCard
              key={value.id}
              value={value}
              isSelected={selectedValueId === value.id}
              onSelect={() => handleValueSelect(value.id)}
              axiomNames={axiomNames}
            />
          ))}
        </div>
      </div>

      {/* Last Updated */}
      <div className="game-kernel-editor__footer">
        <span className="game-kernel-editor__updated">
          Updated: {kernel.updatedAt.toLocaleDateString()}
        </span>
      </div>
    </div>
  );
});

export default GameKernelEditor;
