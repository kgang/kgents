/**
 * PhaseTimeline: N-Phase transition timeline visualization.
 *
 * Wave 5: N-Phase Native Integration
 * ===================================
 *
 * Shows N-Phase transitions over time in a horizontal timeline.
 * Each phase gets a track, with transitions marked at tick points.
 *
 * Design:
 * ```
 * UNDERSTAND ════════════╗
 *                        ║ tick 15
 * ACT ═══════════════════╬════════════╗
 *                                     ║ tick 28
 * REFLECT ════════════════════════════╩═══════ ●
 *                                            current
 * ```
 *
 * Features:
 * - Horizontal timeline with phase tracks
 * - Transition markers with tick numbers
 * - Current position indicator
 * - Click to see transition details
 * - Responsive scaling based on container width
 */

import { useState, useMemo, useRef } from 'react';
import type { NPhaseType, NPhaseTransitionEvent, NPhaseState } from '@/api/types';
import { NPHASE_CONFIG } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

interface PhaseTimelineProps {
  /** N-Phase state from useNPhaseStream */
  nphase: NPhaseState | null;
  /** Current tick (for position indicator) */
  currentTick?: number;
  /** Height of the timeline */
  height?: number;
  /** Additional CSS classes */
  className?: string;
  /** Callback when transition is clicked */
  onTransitionClick?: (transition: NPhaseTransitionEvent) => void;
}

interface TransitionMarker {
  transition: NPhaseTransitionEvent;
  x: number; // percentage position
  y1: number; // start y position
  y2: number; // end y position
}

// =============================================================================
// Constants
// =============================================================================

const PHASES: NPhaseType[] = ['UNDERSTAND', 'ACT', 'REFLECT'];
const PHASE_INDEX: Record<NPhaseType, number> = {
  UNDERSTAND: 0,
  ACT: 1,
  REFLECT: 2,
};
const TRACK_HEIGHT = 24;
const TRACK_GAP = 8;

// =============================================================================
// Component
// =============================================================================

export function PhaseTimeline({
  nphase,
  currentTick = 0,
  height: _height = 120, // Reserved for future responsive scaling
  className = '',
  onTransitionClick,
}: PhaseTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedTransition, setSelectedTransition] = useState<NPhaseTransitionEvent | null>(null);

  // Reserved for future responsive scaling
  void _height;

  // Calculate timeline data
  const { segments, markers, maxTick } = useMemo(() => {
    if (!nphase || !nphase.enabled || nphase.transitions.length === 0) {
      return {
        segments: [] as Array<{ phase: NPhaseType; startTick: number; endTick: number }>,
        markers: [] as TransitionMarker[],
        maxTick: Math.max(currentTick, 1),
      };
    }

    const transitions = nphase.transitions;
    const maxT = Math.max(currentTick, ...transitions.map((t) => t.tick), 1);

    // Build phase segments
    const segs: Array<{ phase: NPhaseType; startTick: number; endTick: number }> = [];
    let currentPhase: NPhaseType = transitions[0]?.from_phase || 'UNDERSTAND';
    let startTick = 0;

    for (const t of transitions) {
      // Close previous segment
      segs.push({ phase: currentPhase, startTick, endTick: t.tick });
      // Start new segment
      currentPhase = t.to_phase;
      startTick = t.tick;
    }
    // Add final segment to current tick
    segs.push({ phase: currentPhase, startTick, endTick: maxT });

    // Build markers
    const marks: TransitionMarker[] = transitions.map((t) => {
      const fromY = PHASE_INDEX[t.from_phase];
      const toY = PHASE_INDEX[t.to_phase];
      return {
        transition: t,
        x: (t.tick / maxT) * 100,
        y1: fromY * (TRACK_HEIGHT + TRACK_GAP) + TRACK_HEIGHT / 2,
        y2: toY * (TRACK_HEIGHT + TRACK_GAP) + TRACK_HEIGHT / 2,
      };
    });

    return { segments: segs, markers: marks, maxTick: maxT };
  }, [nphase, currentTick]);

  // Handle transition click
  const handleMarkerClick = (marker: TransitionMarker) => {
    setSelectedTransition(marker.transition);
    onTransitionClick?.(marker.transition);
  };

  // Not enabled or no transitions
  if (!nphase || !nphase.enabled) {
    return (
      <div className={`text-gray-500 text-sm text-center py-4 ${className}`}>
        N-Phase tracking not enabled
      </div>
    );
  }

  if (nphase.transitions.length === 0) {
    return (
      <div className={`text-gray-500 text-sm text-center py-4 ${className}`}>
        No phase transitions yet
      </div>
    );
  }

  const totalHeight = PHASES.length * (TRACK_HEIGHT + TRACK_GAP) - TRACK_GAP;

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      {/* Phase Labels */}
      <div className="absolute left-0 top-0 w-20 text-xs">
        {PHASES.map((phase, index) => (
          <div
            key={phase}
            className="flex items-center h-6 gap-1"
            style={{
              marginTop: index > 0 ? TRACK_GAP : 0,
              color: NPHASE_CONFIG.colors[phase],
            }}
          >
            <span>{NPHASE_CONFIG.icons[phase]}</span>
            <span className="hidden sm:inline truncate">{phase}</span>
          </div>
        ))}
      </div>

      {/* Timeline Area */}
      <div className="ml-20 relative" style={{ height: totalHeight }}>
        {/* Track backgrounds */}
        {PHASES.map((phase, index) => (
          <div
            key={phase}
            className="absolute left-0 right-0 rounded-full opacity-20"
            style={{
              top: index * (TRACK_HEIGHT + TRACK_GAP),
              height: TRACK_HEIGHT,
              backgroundColor: NPHASE_CONFIG.colors[phase],
            }}
          />
        ))}

        {/* Phase segments */}
        {segments.map((seg, i) => {
          const phaseIndex = PHASE_INDEX[seg.phase];
          const startX = (seg.startTick / maxTick) * 100;
          const width = ((seg.endTick - seg.startTick) / maxTick) * 100;
          const color = NPHASE_CONFIG.colors[seg.phase];

          return (
            <div
              key={`${seg.phase}-${i}`}
              className="absolute rounded-full transition-all duration-300"
              style={{
                top: phaseIndex * (TRACK_HEIGHT + TRACK_GAP) + 4,
                left: `${startX}%`,
                width: `${width}%`,
                height: TRACK_HEIGHT - 8,
                backgroundColor: color,
                boxShadow: `0 0 8px ${color}40`,
              }}
            />
          );
        })}

        {/* Transition markers */}
        <svg
          className="absolute inset-0 pointer-events-none"
          style={{ width: '100%', height: totalHeight }}
        >
          {markers.map((marker, i) => {
            const isSelected = selectedTransition === marker.transition;
            const strokeColor = isSelected ? '#fff' : '#888';

            return (
              <g
                key={i}
                className="cursor-pointer pointer-events-auto"
                onClick={() => handleMarkerClick(marker)}
              >
                {/* Vertical connector line */}
                <line
                  x1={`${marker.x}%`}
                  y1={marker.y1}
                  x2={`${marker.x}%`}
                  y2={marker.y2}
                  stroke={strokeColor}
                  strokeWidth={isSelected ? 2 : 1}
                  strokeDasharray={isSelected ? 'none' : '4,2'}
                />
                {/* Marker dot */}
                <circle
                  cx={`${marker.x}%`}
                  cy={(marker.y1 + marker.y2) / 2}
                  r={isSelected ? 6 : 4}
                  fill={isSelected ? '#fff' : '#666'}
                  stroke={NPHASE_CONFIG.colors[marker.transition.to_phase]}
                  strokeWidth={2}
                />
              </g>
            );
          })}
        </svg>

        {/* Current position indicator */}
        {currentTick > 0 && (
          <div
            className="absolute top-0 w-0.5 bg-white/60 z-10"
            style={{
              left: `${(currentTick / maxTick) * 100}%`,
              height: totalHeight,
            }}
          >
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 text-[10px] text-white/60">
              {currentTick}
            </div>
          </div>
        )}
      </div>

      {/* Selected Transition Details */}
      {selectedTransition && (
        <div className="mt-3 p-2 bg-gray-800/80 rounded text-xs border border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span style={{ color: NPHASE_CONFIG.colors[selectedTransition.from_phase] }}>
                {NPHASE_CONFIG.icons[selectedTransition.from_phase]} {selectedTransition.from_phase}
              </span>
              <span className="text-gray-500">→</span>
              <span style={{ color: NPHASE_CONFIG.colors[selectedTransition.to_phase] }}>
                {NPHASE_CONFIG.icons[selectedTransition.to_phase]} {selectedTransition.to_phase}
              </span>
            </div>
            <button
              onClick={() => setSelectedTransition(null)}
              className="text-gray-500 hover:text-gray-300"
            >
              ×
            </button>
          </div>
          <div className="mt-1 text-gray-400 flex gap-4">
            <span>Tick: {selectedTransition.tick}</span>
            <span>Cycle: {selectedTransition.cycle_count}</span>
            <span className="truncate">Trigger: {selectedTransition.trigger}</span>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Mini Timeline (for headers)
// =============================================================================

/**
 * PhaseTimelineMini: Compact inline timeline indicator.
 *
 * Shows a simple progress bar with phase colors.
 */
export function PhaseTimelineMini({
  nphase,
  className = '',
}: Pick<PhaseTimelineProps, 'nphase' | 'className'>) {
  if (!nphase || !nphase.enabled || nphase.transitions.length === 0) {
    return null;
  }

  // Calculate phase percentages based on transitions
  const phasePercentages = useMemo(() => {
    const transitions = nphase.transitions;
    if (transitions.length === 0) return [100, 0, 0];

    const maxTick = Math.max(...transitions.map((t) => t.tick), 1);
    const percents = [0, 0, 0];

    let prevTick = 0;
    let prevPhase: NPhaseType = transitions[0]?.from_phase || 'UNDERSTAND';

    for (const t of transitions) {
      const duration = t.tick - prevTick;
      percents[PHASE_INDEX[prevPhase]] += duration;
      prevTick = t.tick;
      prevPhase = t.to_phase;
    }
    // Add remaining time
    percents[PHASE_INDEX[prevPhase]] += maxTick - prevTick;

    // Convert to percentages
    const total = percents.reduce((a, b) => a + b, 0);
    return percents.map((p) => (p / total) * 100);
  }, [nphase]);

  return (
    <div className={`flex h-1.5 rounded-full overflow-hidden ${className}`}>
      {PHASES.map((phase, i) => (
        <div
          key={phase}
          style={{
            width: `${phasePercentages[i]}%`,
            backgroundColor: NPHASE_CONFIG.colors[phase],
          }}
          title={`${phase}: ${phasePercentages[i].toFixed(0)}%`}
        />
      ))}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default PhaseTimeline;
