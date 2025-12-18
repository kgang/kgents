/**
 * PolynomialPlayground: Interactive state machine visualization.
 *
 * Flagship pilot that makes PolyAgent[S, A, B] tangible through
 * visual state diagrams, input buttons, and transition traces.
 *
 * @see plans/gallery-pilots-top3.md
 * @see docs/skills/polynomial-agent.md
 */

import { useState, useCallback, useMemo } from 'react';
import { Play, RotateCcw, ChevronRight, Lightbulb } from 'lucide-react';

// Import shared presets from categorical module
import {
  PRESETS,
  type PresetKey,
  type PolynomialPreset,
  type Position,
  type Edge,
} from '@/components/categorical/presets';

// Re-export types for consumers
export type { PresetKey, PolynomialPreset, Position, Edge };

export interface PolynomialPlaygroundProps {
  /** Initial preset to load */
  preset?: PresetKey;
  /** Controlled current state */
  currentState?: string;
  /** Controlled trace */
  trace?: string[];
  /** Compact mode for gallery cards */
  compact?: boolean;
  /** Callback when state changes */
  onStateChange?: (state: string, trace: string[]) => void;
}

// =============================================================================
// Component
// =============================================================================

export function PolynomialPlayground({
  preset: initialPreset = 'traffic_light',
  currentState: controlledState,
  trace: controlledTrace,
  compact = false,
  onStateChange,
}: PolynomialPlaygroundProps) {
  // Local state for uncontrolled mode
  const [presetKey, setPresetKey] = useState<PresetKey>(initialPreset);
  const [localState, setLocalState] = useState<string>(() => PRESETS[initialPreset].positions[0].id);
  const [localTrace, setLocalTrace] = useState<string[]>([]);

  // Use controlled or local state
  const currentState = controlledState ?? localState;
  const trace = controlledTrace ?? localTrace;
  const config = PRESETS[presetKey];

  // Compute valid inputs for current state
  const validInputs = useMemo(() => {
    const inputs: string[] = [];
    for (const edge of config.edges) {
      if (edge.source === currentState) {
        inputs.push(edge.label);
      }
    }
    return [...new Set(inputs)];
  }, [config.edges, currentState]);

  // Handle input click (transition)
  const handleInput = useCallback(
    (input: string) => {
      // Find the edge for this input
      const edge = config.edges.find((e) => e.source === currentState && e.label === input);
      if (!edge) return;

      const newState = edge.target;
      const newTrace = [...trace, `${currentState} --${input}--> ${newState}`];

      if (onStateChange) {
        onStateChange(newState, newTrace);
      } else {
        setLocalState(newState);
        setLocalTrace(newTrace);
      }
    },
    [config.edges, currentState, trace, onStateChange]
  );

  // Handle reset
  const handleReset = useCallback(() => {
    const initialState = config.positions[0].id;
    if (onStateChange) {
      onStateChange(initialState, []);
    } else {
      setLocalState(initialState);
      setLocalTrace([]);
    }
  }, [config.positions, onStateChange]);

  // Handle preset change
  const handlePresetChange = useCallback(
    (newPreset: PresetKey) => {
      setPresetKey(newPreset);
      const newConfig = PRESETS[newPreset];
      const initialState = newConfig.positions[0].id;
      if (onStateChange) {
        onStateChange(initialState, []);
      } else {
        setLocalState(initialState);
        setLocalTrace([]);
      }
    },
    [onStateChange]
  );

  // ==========================================================================
  // Compact Mode (for gallery cards)
  // ==========================================================================

  if (compact) {
    return (
      <div className="space-y-3">
        {/* Mini state diagram */}
        <div className="flex gap-2 flex-wrap justify-center">
          {config.positions.map((pos) => {
            const isCurrent = pos.id === currentState;
            return (
              <div
                key={pos.id}
                className="text-center transition-all duration-300"
                style={{
                  opacity: isCurrent ? 1 : 0.5,
                  transform: isCurrent ? 'scale(1.1)' : 'scale(1)',
                }}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{
                    background: `${pos.color}30`,
                    border: `2px solid ${isCurrent ? pos.color : pos.color + '40'}`,
                    boxShadow: isCurrent ? `0 0 12px ${pos.color}60` : 'none',
                  }}
                >
                  {pos.label[0]}
                </div>
              </div>
            );
          })}
        </div>

        {/* Current state label */}
        <div className="text-center text-xs text-gray-400">
          Current:{' '}
          <span
            className="font-medium"
            style={{
              color: config.positions.find((p) => p.id === currentState)?.color || '#fff',
            }}
          >
            {currentState}
          </span>
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
        <select
          value={presetKey}
          onChange={(e) => handlePresetChange(e.target.value as PresetKey)}
          className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-gray-200"
        >
          <optgroup label="Gallery">
            <option value="traffic_light">Traffic Light</option>
            <option value="vending_machine">Vending Machine</option>
          </optgroup>
          <optgroup label="Town">
            <option value="citizen">Citizen</option>
          </optgroup>
          <optgroup label="Park">
            <option value="crisis_phase">Crisis Phase</option>
            <option value="timer_state">Timer State</option>
            <option value="consent_debt">Consent Debt</option>
            <option value="director">Director</option>
          </optgroup>
        </select>
      </div>

      {/* State Diagram */}
      <div className="bg-slate-800 rounded-lg p-6">
        <div className="flex gap-4 flex-wrap justify-center">
          {config.positions.map((pos, idx) => {
            const isCurrent = pos.id === currentState;
            return (
              <div key={pos.id} className="flex items-center gap-2">
                <div
                  className="relative p-4 rounded-xl text-center min-w-[80px] transition-all duration-300"
                  style={{
                    background: `linear-gradient(135deg, ${pos.color}20, ${pos.color}10)`,
                    border: `2px solid ${isCurrent ? pos.color : pos.color + '40'}`,
                    boxShadow: isCurrent ? `0 0 24px ${pos.color}50` : 'none',
                    transform: isCurrent ? 'scale(1.05)' : 'scale(1)',
                  }}
                >
                  {isCurrent && (
                    <div
                      className="absolute -top-2 -right-2 w-5 h-5 rounded-full flex items-center justify-center"
                      style={{ background: pos.color }}
                    >
                      <Play className="w-3 h-3 text-white" />
                    </div>
                  )}
                  <div className="font-semibold text-white" style={{ color: pos.color }}>
                    {pos.label}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{pos.description}</div>
                </div>
                {idx < config.positions.length - 1 && (
                  <ChevronRight className="w-4 h-4 text-gray-600" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Input Controls */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-400 min-w-[80px]">Inputs:</span>
        <div className="flex gap-2 flex-wrap">
          {validInputs.length > 0 ? (
            validInputs.map((input) => (
              <button
                key={input}
                onClick={() => handleInput(input)}
                className="px-4 py-2 rounded-lg text-sm font-medium bg-blue-600 hover:bg-blue-500 text-white transition-colors"
              >
                {input}
              </button>
            ))
          ) : (
            <span className="text-gray-500 text-sm italic">No valid inputs from this state</span>
          )}
        </div>
        <button
          onClick={handleReset}
          className="ml-auto px-3 py-2 rounded-lg text-sm bg-slate-700 hover:bg-slate-600 text-gray-300 transition-colors flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </button>
      </div>

      {/* Trace */}
      <div className="bg-slate-800 rounded-lg p-4">
        <div className="text-xs text-gray-500 uppercase tracking-wider mb-2">Trace</div>
        <div className="font-mono text-sm text-gray-300">
          {trace.length > 0 ? (
            trace.slice(-5).map((t, i) => (
              <div key={i} className="py-0.5">
                {t}
              </div>
            ))
          ) : (
            <span className="text-gray-500 italic">Click an input to begin</span>
          )}
        </div>
      </div>

      {/* Teaching Callout */}
      <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 border-l-4 border-purple-500 rounded-r-lg p-4">
        <div className="flex items-center gap-2 text-purple-400 text-xs uppercase tracking-wider mb-1">
          <Lightbulb className="w-3 h-3" />
          Teaching
        </div>
        <p className="text-sm text-gray-200">{config.teaching}</p>
      </div>
    </div>
  );
}

export default PolynomialPlayground;
