/**
 * VoiceCheckIndicator - Anti-Sausage score display.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Displays the Anti-Sausage voice check score with:
 * - Letter grade (A-D)
 * - Progress bar
 * - Breathing animation for high scores
 * - Violation summary on hover
 *
 * @example
 * <VoiceCheckIndicator score={0.85} />
 * <VoiceCheckIndicator text="Some text to check" />
 */

import React, { useState } from 'react';
import { Breathe } from '../joy/Breathe';
import { useVoiceGate, type VoiceViolation } from '../../hooks/useVoiceGate';

// =============================================================================
// Types
// =============================================================================

export interface VoiceCheckIndicatorProps {
  /** Text to check (optional, for real-time checking) */
  text?: string;
  /** Pre-computed score (0-1) */
  score?: number;
  /** Pre-computed violations */
  violations?: VoiceViolation[];
  /** Pre-computed anchors */
  anchors?: string[];
  /** Compact mode (just grade) */
  compact?: boolean;
  /** Show details on hover */
  showDetails?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

function getGrade(score: number): string {
  if (score >= 0.9) return 'A';
  if (score >= 0.8) return 'A-';
  if (score >= 0.7) return 'B';
  if (score >= 0.6) return 'B-';
  if (score >= 0.5) return 'C';
  return 'D';
}

function getColor(score: number): { text: string; bg: string; bar: string } {
  if (score >= 0.9) {
    return { text: 'text-green-400', bg: 'bg-green-900/30', bar: 'bg-green-500' };
  }
  if (score >= 0.7) {
    return { text: 'text-yellow-400', bg: 'bg-yellow-900/30', bar: 'bg-yellow-500' };
  }
  if (score >= 0.5) {
    return { text: 'text-orange-400', bg: 'bg-orange-900/30', bar: 'bg-orange-500' };
  }
  return { text: 'text-red-400', bg: 'bg-red-900/30', bar: 'bg-red-500' };
}

// =============================================================================
// Component
// =============================================================================

export function VoiceCheckIndicator({
  text,
  score: propScore,
  violations: propViolations,
  anchors: propAnchors,
  compact = false,
  showDetails = true,
  className = '',
}: VoiceCheckIndicatorProps): React.ReactElement {
  const [isHovered, setIsHovered] = useState(false);

  // Use hook for real-time checking if text provided
  const {
    score: hookScore,
    violations: hookViolations,
    anchors: hookAnchors,
    isChecking,
  } = useVoiceGate(text, { enabled: !!text });

  // Use props or hook values
  const score = propScore ?? hookScore;
  const violations = propViolations ?? hookViolations;
  const anchors = propAnchors ?? hookAnchors;

  const grade = getGrade(score);
  const colors = getColor(score);
  const shouldBreathe = score >= 0.9;

  // Compact mode: just the grade badge
  if (compact) {
    const content = (
      <span
        className={`
          voice-indicator-compact inline-flex items-center justify-center
          w-6 h-6 rounded-full font-medium text-xs
          ${colors.bg} ${colors.text}
          ${className}
        `}
        title={`Anti-Sausage: ${(score * 100).toFixed(0)}%`}
      >
        {isChecking ? '...' : grade}
      </span>
    );

    return shouldBreathe ? (
      <Breathe intensity={0.2} speed="slow">
        {content}
      </Breathe>
    ) : (
      content
    );
  }

  // Full mode
  const content = (
    <div
      className={`
        voice-indicator inline-flex items-center gap-2 px-3 py-1.5 rounded-full
        ${colors.bg} border border-current/30
        ${className}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Grade */}
      <span className={`font-medium ${colors.text}`}>{isChecking ? '...' : grade}</span>

      {/* Progress bar */}
      <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${colors.bar}`}
          style={{ width: `${score * 100}%` }}
        />
      </div>

      {/* Score percentage */}
      <span className="text-xs text-gray-400">{(score * 100).toFixed(0)}%</span>

      {/* Details popover */}
      {showDetails && isHovered && (violations.length > 0 || anchors.length > 0) && (
        <div className="absolute top-full left-0 mt-2 z-50">
          <VoiceDetailsPopover violations={violations} anchors={anchors} />
        </div>
      )}
    </div>
  );

  return (
    <div className="relative">
      {shouldBreathe ? (
        <Breathe intensity={0.2} speed="slow">
          {content}
        </Breathe>
      ) : (
        content
      )}
    </div>
  );
}

// =============================================================================
// Details Popover
// =============================================================================

interface VoiceDetailsPopoverProps {
  violations: VoiceViolation[];
  anchors: string[];
}

function VoiceDetailsPopover({
  violations,
  anchors,
}: VoiceDetailsPopoverProps): React.ReactElement {
  return (
    <div className="voice-details bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-3 min-w-64 max-w-80">
      {/* Violations */}
      {violations.length > 0 && (
        <div className="mb-3">
          <h4 className="text-xs font-medium text-red-400 mb-1">
            Violations ({violations.length})
          </h4>
          <ul className="space-y-1">
            {violations.slice(0, 3).map((v, i) => (
              <li key={i} className="text-xs">
                <span className="text-gray-300">"{v.match}"</span>
                {v.suggestion && <span className="text-gray-500 block ml-2">→ {v.suggestion}</span>}
              </li>
            ))}
            {violations.length > 3 && (
              <li className="text-xs text-gray-500">+{violations.length - 3} more...</li>
            )}
          </ul>
        </div>
      )}

      {/* Anchors */}
      {anchors.length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-green-400 mb-1">Anchors ({anchors.length})</h4>
          <ul className="space-y-1">
            {anchors.slice(0, 3).map((anchor, i) => (
              <li key={i} className="text-xs text-gray-300">
                ✓ {anchor}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default VoiceCheckIndicator;
