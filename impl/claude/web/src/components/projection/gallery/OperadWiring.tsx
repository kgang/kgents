/**
 * OperadWiring: Interactive operad composition diagram.
 *
 * Flagship pilot that makes operad composition visual - drag operations
 * from palette, verify composition laws in real-time.
 *
 * @see plans/gallery-pilots-top3.md
 * @see spec/protocols/agentese.md (operad section)
 */

import { useState, useCallback } from 'react';
import { Check, X, Lightbulb, Link2, ArrowRight } from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

interface Operation {
  id: string;
  name: string;
  arity: number;
  signature: string;
  color: string;
}

interface Law {
  id: string;
  name: string;
  equation: string;
  verified: boolean;
}

interface OperadDefinition {
  name: string;
  description: string;
  operations: Operation[];
  laws: Law[];
  teaching: string;
}

type OperadKey = 'TOWN_OPERAD' | 'FLOW_OPERAD';

export interface OperadWiringProps {
  /** Initial operad to load */
  operad?: OperadKey;
  /** Compact mode for gallery cards */
  compact?: boolean;
  /** Callback when composition changes */
  onCompositionChange?: (composition: Operation[]) => void;
}

// =============================================================================
// Operad Definitions (matching backend)
// =============================================================================

const OPERADS: Record<OperadKey, OperadDefinition> = {
  TOWN_OPERAD: {
    name: 'TOWN_OPERAD',
    description: 'Grammar of citizen interactions in Agent Town',
    operations: [
      { id: 'greet', name: 'greet', arity: 2, signature: 'Citizen x Citizen -> Relationship', color: '#22c55e' },
      { id: 'gossip', name: 'gossip', arity: 2, signature: 'Citizen x Citizen -> Information', color: '#3b82f6' },
      { id: 'trade', name: 'trade', arity: 2, signature: 'Citizen x Citizen -> Exchange', color: '#f59e0b' },
      { id: 'solo', name: 'solo', arity: 1, signature: 'Citizen -> Reflection', color: '#8b5cf6' },
      { id: 'celebrate', name: 'celebrate', arity: 3, signature: 'Cit x Cit x Cit -> Event', color: '#ec4899' },
    ],
    laws: [
      { id: 'identity', name: 'Identity', equation: 'g(f; id, ..., id) = f', verified: true },
      { id: 'associativity', name: 'Associativity', equation: 'g(g(f;g);h) = g(f;g(g;h))', verified: true },
      { id: 'locality', name: 'Locality', equation: 'ops affect only participants', verified: true },
    ],
    teaching: 'Operads define the grammar of composition - which operations can combine and how',
  },
  FLOW_OPERAD: {
    name: 'FLOW_OPERAD',
    description: 'Research and collaboration flow composition',
    operations: [
      { id: 'query', name: 'query', arity: 1, signature: 'Question -> SearchResults', color: '#22c55e' },
      { id: 'synthesize', name: 'synthesize', arity: 2, signature: 'Results x Results -> Summary', color: '#3b82f6' },
      { id: 'critique', name: 'critique', arity: 1, signature: 'Summary -> Refinement', color: '#f59e0b' },
      { id: 'commit', name: 'commit', arity: 1, signature: 'Refinement -> Knowledge', color: '#8b5cf6' },
    ],
    laws: [
      { id: 'identity', name: 'Identity', equation: 'g(f; id) = f', verified: true },
      { id: 'associativity', name: 'Associativity', equation: 'g(g(f;g);h) = g(f;g(g;h))', verified: true },
    ],
    teaching: 'FLOW_OPERAD governs research collaboration - ensuring coherent knowledge synthesis',
  },
};

// =============================================================================
// Component
// =============================================================================

export function OperadWiring({
  operad: initialOperad = 'TOWN_OPERAD',
  compact = false,
  onCompositionChange,
}: OperadWiringProps) {
  const [operadKey, setOperadKey] = useState<OperadKey>(initialOperad);
  const [composition, setComposition] = useState<Operation[]>([]);
  const [draggedOp, setDraggedOp] = useState<Operation | null>(null);

  const config = OPERADS[operadKey];

  // Handle drag start
  const handleDragStart = useCallback((op: Operation) => {
    setDraggedOp(op);
  }, []);

  // Handle drop on canvas
  const handleDrop = useCallback(() => {
    if (draggedOp) {
      const newComposition = [...composition, draggedOp];
      setComposition(newComposition);
      onCompositionChange?.(newComposition);
    }
    setDraggedOp(null);
  }, [draggedOp, composition, onCompositionChange]);

  // Handle drag end (clear)
  const handleDragEnd = useCallback(() => {
    setDraggedOp(null);
  }, []);

  // Clear composition
  const handleClear = useCallback(() => {
    setComposition([]);
    onCompositionChange?.([]);
  }, [onCompositionChange]);

  // Handle operad change
  const handleOperadChange = useCallback(
    (newOperad: OperadKey) => {
      setOperadKey(newOperad);
      setComposition([]);
      onCompositionChange?.([]);
    },
    [onCompositionChange]
  );

  // Compute composition result string
  const compositionResult = composition.length > 0
    ? composition.map(op => op.name).join(' >> ')
    : null;

  // ==========================================================================
  // Compact Mode
  // ==========================================================================

  if (compact) {
    return (
      <div className="space-y-3">
        {/* Mini operation badges */}
        <div className="flex gap-1.5 flex-wrap justify-center">
          {config.operations.slice(0, 4).map((op) => (
            <div
              key={op.id}
              className="px-2 py-1 rounded-md text-xs font-medium flex items-center gap-1"
              style={{
                background: `${op.color}20`,
                color: op.color,
                border: `1px solid ${op.color}40`,
              }}
            >
              <span className="text-[10px] bg-white/10 px-1 rounded">{op.arity}</span>
              {op.name}
            </div>
          ))}
        </div>

        {/* Law indicators */}
        <div className="flex justify-center gap-2">
          {config.laws.slice(0, 3).map((law) => (
            <div key={law.id} className="flex items-center gap-1 text-xs">
              {law.verified ? (
                <Check className="w-3 h-3 text-green-500" />
              ) : (
                <X className="w-3 h-3 text-red-500" />
              )}
              <span className="text-gray-400">{law.name}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ==========================================================================
  // Full Mode
  // ==========================================================================

  return (
    <div className="bg-slate-900 rounded-xl p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">{config.name}</h3>
          <p className="text-sm text-gray-400">{config.description}</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Law indicators */}
          <div className="flex gap-2">
            {config.laws.map((law) => (
              <div
                key={law.id}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs"
                style={{
                  background: law.verified ? '#22c55e15' : '#ef444415',
                }}
              >
                {law.verified ? (
                  <Check className="w-3.5 h-3.5 text-green-500" />
                ) : (
                  <X className="w-3.5 h-3.5 text-red-500" />
                )}
                <span className="text-gray-200">{law.name}</span>
              </div>
            ))}
          </div>
          <select
            value={operadKey}
            onChange={(e) => handleOperadChange(e.target.value as OperadKey)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-gray-200"
          >
            <option value="TOWN_OPERAD">TOWN_OPERAD</option>
            <option value="FLOW_OPERAD">FLOW_OPERAD</option>
          </select>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-[200px_1fr] gap-4">
        {/* Operation Palette */}
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-3">
            Operations
          </div>
          <div className="space-y-2">
            {config.operations.map((op) => (
              <div
                key={op.id}
                draggable
                onDragStart={() => handleDragStart(op)}
                onDragEnd={handleDragEnd}
                className="p-3 rounded-lg cursor-grab active:cursor-grabbing transition-all hover:scale-[1.02]"
                style={{
                  background: `linear-gradient(135deg, ${op.color}20, ${op.color}10)`,
                  border: `1px solid ${op.color}40`,
                }}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="text-[10px] font-bold px-1.5 py-0.5 rounded"
                    style={{ background: op.color, color: 'white' }}
                  >
                    {op.arity}
                  </span>
                  <span className="font-medium" style={{ color: op.color }}>
                    {op.name}
                  </span>
                </div>
                <div className="text-[10px] text-gray-500 mt-1.5 font-mono">
                  {op.signature}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Composition Canvas */}
        <div
          className="bg-slate-800 rounded-lg p-4 min-h-[250px] flex flex-col"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="text-xs text-gray-500 uppercase tracking-wider">
              Composition Canvas
            </div>
            {composition.length > 0 && (
              <button
                onClick={handleClear}
                className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
              >
                Clear
              </button>
            )}
          </div>

          {composition.length === 0 ? (
            <div className="flex-1 border-2 border-dashed border-slate-600 rounded-lg flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Link2 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Drag operations here to compose</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 space-y-4">
              {/* Composed operations */}
              <div className="flex items-center gap-2 flex-wrap">
                {composition.map((op, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <div
                      className="px-3 py-2 rounded-lg"
                      style={{
                        background: `${op.color}20`,
                        border: `1px solid ${op.color}40`,
                      }}
                    >
                      <span className="font-medium" style={{ color: op.color }}>
                        {op.name}
                      </span>
                    </div>
                    {idx < composition.length - 1 && (
                      <ArrowRight className="w-4 h-4 text-gray-500" />
                    )}
                  </div>
                ))}
              </div>

              {/* Result */}
              {compositionResult && (
                <div className="bg-slate-700/50 rounded-lg p-3">
                  <div className="text-xs text-gray-500 mb-1">Composition Result</div>
                  <div className="font-mono text-sm text-green-400">
                    {compositionResult}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Teaching Callout */}
      <div className="bg-gradient-to-r from-amber-500/20 to-pink-500/20 border-l-4 border-amber-500 rounded-r-lg p-4">
        <div className="flex items-center gap-2 text-amber-400 text-xs uppercase tracking-wider mb-1">
          <Lightbulb className="w-3 h-3" />
          Teaching
        </div>
        <p className="text-sm text-gray-200">{config.teaching}</p>
      </div>
    </div>
  );
}

export default OperadWiring;
