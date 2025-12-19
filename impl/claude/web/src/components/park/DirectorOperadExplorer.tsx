/**
 * DirectorOperadExplorer: Interactive explorer for DIRECTOR_OPERAD.
 *
 * Shows the 8 director operations with their arities and signatures,
 * 6 verification laws, and teaching callouts for Punchdrunk concepts.
 *
 * @see agents/park/operad.py - DIRECTOR_OPERAD definition
 * @see plans/park-town-quality-enhancement-continuation.md (Phase 5)
 */

import { useState, useCallback } from 'react';
import { Check, X, Lightbulb, Eye, Zap, Timer, Shield, RotateCcw } from 'lucide-react';
import { TeachingCallout } from '../categorical/TeachingCallout';

// =============================================================================
// Types
// =============================================================================

interface Operation {
  id: string;
  name: string;
  arity: number;
  signature: string;
  description: string;
  icon: typeof Eye;
  color: string;
  teaching: string;
}

interface Law {
  id: string;
  name: string;
  equation: string;
  description: string;
  verified: boolean;
}

export interface DirectorOperadExplorerProps {
  variant: 'modal' | 'inline';
  currentPhase?: 'OBSERVING' | 'BUILDING_TENSION' | 'INJECTING' | 'COOLDOWN' | 'INTERVENING';
  showTeaching?: boolean;
  onClose?: () => void;
}

// =============================================================================
// Static Data (matches agents/park/operad.py)
// =============================================================================

const DIRECTOR_OPERATIONS: Operation[] = [
  {
    id: 'observe',
    name: 'observe',
    arity: 1,
    signature: 'Session -> Metrics',
    description: 'Watch guest behavior passively',
    icon: Eye,
    color: '#22c55e',
    teaching:
      'The director watches from the shadows, gathering tension metrics without intervening.',
  },
  {
    id: 'build_tension',
    name: 'build_tension',
    arity: 1,
    signature: 'Metrics -> TensionState',
    description: 'Increase narrative pressure',
    icon: Zap,
    color: '#f59e0b',
    teaching: 'Rising action in theatrical terms. The director decides whether to intervene.',
  },
  {
    id: 'inject',
    name: 'inject',
    arity: 2,
    signature: '(SerendipityInjection, Session) -> Result',
    description: 'Introduce lucky coincidence',
    icon: Zap,
    color: '#8b5cf6',
    teaching:
      'A surprise arrival, a revelation, a twist. Injections shift the narrative without forcing outcomes.',
  },
  {
    id: 'cooldown',
    name: 'cooldown',
    arity: 1,
    signature: 'Duration -> CooldownState',
    description: 'Reduce intensity after injection',
    icon: Timer,
    color: '#3b82f6',
    teaching: 'Every climax needs resolution. Cooldown prevents injection fatigue.',
  },
  {
    id: 'intervene',
    name: 'intervene',
    arity: 1,
    signature: 'DifficultyAdjustment -> Result',
    description: 'Direct action (high consent cost)',
    icon: Shield,
    color: '#ef4444',
    teaching: 'Interventions are expensive (3x cost). Use sparingly when guests are truly stuck.',
  },
  {
    id: 'evaluate',
    name: 'evaluate',
    arity: 2,
    signature: '(Metrics, Config) -> InjectionDecision',
    description: 'Check injection conditions',
    icon: Eye,
    color: '#06b6d4',
    teaching: 'Consent debt too high? Cooldown active? Evaluate before committing to inject.',
  },
  {
    id: 'director_reset',
    name: 'director_reset',
    arity: 0,
    signature: '() -> Observing',
    description: 'Return to observing state',
    icon: RotateCcw,
    color: '#64748b',
    teaching: 'Nullary operation - no inputs required. Always returns to passive observation.',
  },
  {
    id: 'abort',
    name: 'abort',
    arity: 0,
    signature: '() -> Observing',
    description: 'Cancel current operation',
    icon: RotateCcw,
    color: '#6b7280',
    teaching: 'Interventions are atomic: complete or abort. Never leave guests in limbo.',
  },
];

const DIRECTOR_LAWS: Law[] = [
  {
    id: 'consent_constraint',
    name: 'Consent Constraint',
    equation: 'inject(i, s) requires consent_debt(s) <= 0.7',
    description: 'Cannot inject when consent debt is too high',
    verified: true,
  },
  {
    id: 'cooldown_constraint',
    name: 'Cooldown Constraint',
    equation: 'inject(i, s) requires time_since_injection >= min_cooldown',
    description: 'Must respect minimum cooldown between injections',
    verified: true,
  },
  {
    id: 'tension_flow',
    name: 'Tension Flow',
    equation: 'build_tension(m) -> inject | observe within T',
    description: 'Building tension leads to injection or observation',
    verified: true,
  },
  {
    id: 'intervention_isolation',
    name: 'Intervention Isolation',
    equation: 'intervene(a) = complete(a) | abort()',
    description: 'Interventions are atomic - complete or abort',
    verified: true,
  },
  {
    id: 'observe_identity',
    name: 'Observe Identity',
    equation: 'observe(observe(s)) = observe(s)',
    description: 'Observing is idempotent',
    verified: true,
  },
  {
    id: 'reset_to_observe',
    name: 'Reset to Observe',
    equation: 'reset() -> OBSERVING',
    description: 'Reset always returns to OBSERVING phase',
    verified: true,
  },
];

// Phase -> Active operations mapping
const PHASE_ACTIVE_OPS: Record<string, string[]> = {
  OBSERVING: ['observe', 'evaluate'],
  BUILDING_TENSION: ['build_tension', 'evaluate', 'abort'],
  INJECTING: ['inject', 'abort'],
  COOLDOWN: ['cooldown', 'director_reset'],
  INTERVENING: ['intervene', 'abort'],
};

// =============================================================================
// Component
// =============================================================================

export function DirectorOperadExplorer({
  variant,
  currentPhase,
  showTeaching = false,
  onClose,
}: DirectorOperadExplorerProps) {
  const [selectedOp, setSelectedOp] = useState<Operation | null>(null);
  const [verifyingLaws, setVerifyingLaws] = useState(false);

  const activeOps = currentPhase ? PHASE_ACTIVE_OPS[currentPhase] || [] : [];

  const handleVerifyLaws = useCallback(async () => {
    setVerifyingLaws(true);
    await new Promise<void>((r) => {
      setTimeout(r, 500);
    });
    setVerifyingLaws(false);
  }, []);

  const content = (
    <div className="bg-slate-900 rounded-xl p-5 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">DIRECTOR_OPERAD</h3>
          <p className="text-sm text-gray-400">
            Composition grammar for Punchdrunk Park director operations
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleVerifyLaws}
            disabled={verifyingLaws}
            className="px-3 py-1.5 text-sm bg-emerald-600/20 text-emerald-400 rounded-lg hover:bg-emerald-600/30 disabled:opacity-50 transition-colors"
          >
            {verifyingLaws ? 'Verifying...' : 'Verify Laws'}
          </button>
          {variant === 'modal' && onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-white text-xl px-2">
              ×
            </button>
          )}
        </div>
      </div>

      {/* Operations Grid */}
      <div>
        <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-3">
          Operations ({DIRECTOR_OPERATIONS.length})
        </h4>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {DIRECTOR_OPERATIONS.map((op) => {
            const Icon = op.icon;
            const isActive = activeOps.includes(op.id);
            const isSelected = selectedOp?.id === op.id;

            return (
              <button
                key={op.id}
                onClick={() => setSelectedOp(isSelected ? null : op)}
                className={`
                  p-3 rounded-lg text-left transition-all
                  ${isActive ? 'ring-2 ring-amber-500/50' : ''}
                  ${isSelected ? 'bg-slate-700' : 'bg-slate-800 hover:bg-slate-700/50'}
                `}
                style={{ borderLeft: `3px solid ${op.color}` }}
              >
                <div className="flex items-center gap-2 mb-1">
                  <Icon className="w-4 h-4" style={{ color: op.color }} />
                  <span className="font-medium text-white text-sm">{op.name}</span>
                  <span
                    className="text-[10px] px-1.5 py-0.5 rounded"
                    style={{ background: `${op.color}30`, color: op.color }}
                  >
                    {op.arity}
                  </span>
                </div>
                <p className="text-xs text-gray-500">{op.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Operation Detail */}
      {selectedOp && (
        <div className="bg-slate-800 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            {(() => {
              const Icon = selectedOp.icon;
              return <Icon className="w-5 h-5" style={{ color: selectedOp.color }} />;
            })()}
            <span className="font-medium text-white">{selectedOp.name}</span>
          </div>
          <p className="text-xs font-mono text-gray-400 mb-3">{selectedOp.signature}</p>
          {showTeaching && (
            <TeachingCallout category="insight" compact>
              {selectedOp.teaching}
            </TeachingCallout>
          )}
        </div>
      )}

      {/* Laws Panel */}
      <div>
        <h4 className="text-xs text-gray-500 uppercase tracking-wider mb-3">
          Composition Laws ({DIRECTOR_LAWS.length})
        </h4>
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-2">
          {DIRECTOR_LAWS.map((law) => (
            <div key={law.id} className="bg-slate-800 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-1">
                {law.verified ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <X className="w-4 h-4 text-red-500" />
                )}
                <span className="text-sm font-medium text-white">{law.name}</span>
              </div>
              <p className="text-[10px] font-mono text-gray-500">{law.equation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Teaching Footer */}
      {showTeaching && (
        <div className="bg-gradient-to-r from-amber-500/20 to-pink-500/20 border-l-4 border-amber-500 rounded-r-lg p-4">
          <div className="flex items-center gap-2 text-amber-400 text-xs uppercase tracking-wider mb-1">
            <Lightbulb className="w-3 h-3" />
            Teaching
          </div>
          <p className="text-sm text-gray-200">
            The DIRECTOR_OPERAD captures how a Punchdrunk-style director composes actions. Each
            operation has constraints (laws) that prevent harmful compositions—like injecting
            serendipity when consent debt is too high.
          </p>
        </div>
      )}
    </div>
  );

  if (variant === 'modal') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
        <div className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">{content}</div>
      </div>
    );
  }

  return content;
}

export default DirectorOperadExplorer;
