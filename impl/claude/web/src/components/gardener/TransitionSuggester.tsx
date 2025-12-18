/**
 * TransitionSuggester - Auto-Inducer Banner
 *
 * Suggests season transitions based on garden state signals.
 * Can be dismissed (4h cooldown per spec).
 *
 * @see spec/protocols/2d-renaissance.md
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { Sparkles, X, Check, ChevronRight } from 'lucide-react';
import { getSeasonIcon } from '@/constants';
import type { TransitionSuggestionJSON } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface TransitionSuggesterProps {
  /** Transition suggestion from Auto-Inducer */
  suggestion: TransitionSuggestionJSON;
  /** Accept transition callback */
  onAccept: () => void;
  /** Dismiss transition callback */
  onDismiss: () => void;
  /** Loading state */
  isLoading?: boolean;
  /** Compact mode */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Main Component
// =============================================================================

export function TransitionSuggester({
  suggestion,
  onAccept,
  onDismiss,
  isLoading = false,
  compact = false,
  className = '',
}: TransitionSuggesterProps) {
  const FromIcon = getSeasonIcon(suggestion.from_season);
  const ToIcon = getSeasonIcon(suggestion.to_season);
  const confidence = Math.round(suggestion.confidence * 100);

  // Compact mode: single line
  if (compact) {
    return (
      <div
        className={`
          flex items-center justify-between gap-2 px-3 py-2 rounded-lg
          bg-[#D4A574]/20 border border-[#D4A574]/40
          ${className}
        `}
      >
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <Sparkles className="w-4 h-4 text-[#D4A574] flex-shrink-0" />
          <span className="text-xs text-[#F5E6D3] truncate">
            {suggestion.from_season} → {suggestion.to_season}
          </span>
          <span className="text-[10px] text-[#D4A574]">{confidence}%</span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={onAccept}
            disabled={isLoading}
            className="p-1.5 rounded bg-[#4A6B4A] text-[#F5E6D3] hover:brightness-110 disabled:opacity-50"
          >
            <Check className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onDismiss}
            disabled={isLoading}
            className="p-1.5 rounded bg-[#6B4E3D] text-[#AB9080] hover:brightness-110 disabled:opacity-50"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    );
  }

  // Full mode: detailed banner
  return (
    <div
      className={`
        rounded-lg border overflow-hidden
        bg-gradient-to-r from-[#D4A574]/10 to-[#8B5A2B]/10
        border-[#D4A574]/40
        ${className}
      `}
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2 bg-[#D4A574]/20 border-b border-[#D4A574]/20">
        <Sparkles className="w-4 h-4 text-[#D4A574]" />
        <span className="text-xs font-medium text-[#D4A574] uppercase tracking-wide">
          Auto-Inducer Suggestion
        </span>
        <span className="ml-auto text-xs text-[#AB9080]">{confidence}% confidence</span>
      </div>

      {/* Body */}
      <div className="p-4">
        {/* Transition visualization */}
        <div className="flex items-center justify-center gap-4 mb-4">
          <SeasonPill season={suggestion.from_season} Icon={FromIcon} active={false} />
          <ChevronRight className="w-6 h-6 text-[#D4A574]" />
          <SeasonPill season={suggestion.to_season} Icon={ToIcon} active={true} />
        </div>

        {/* Reason */}
        <p className="text-sm text-[#AB9080] text-center mb-4">{suggestion.reason}</p>

        {/* Signals summary */}
        <div className="grid grid-cols-3 gap-2 mb-4 text-center">
          <SignalBadge
            label="Gestures"
            value={suggestion.signals.gesture_frequency.toFixed(1)}
            unit="/hr"
          />
          <SignalBadge
            label="Diversity"
            value={(suggestion.signals.gesture_diversity * 100).toFixed(0)}
            unit="%"
          />
          <SignalBadge
            label="Entropy"
            value={(suggestion.signals.entropy_spent_ratio * 100).toFixed(0)}
            unit="%"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={onAccept}
            disabled={isLoading}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-[#4A6B4A] text-[#F5E6D3] font-medium hover:brightness-110 disabled:opacity-50 transition-all"
          >
            <Check className="w-4 h-4" />
            Accept Transition
          </button>
          <button
            onClick={onDismiss}
            disabled={isLoading}
            className="px-4 py-2 rounded-lg bg-[#4A3728] text-[#AB9080] hover:brightness-110 disabled:opacity-50 transition-all"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Cooldown note */}
        <p className="text-[10px] text-[#6B4E3D] text-center mt-2">
          Dismissing applies 4h cooldown before next suggestion
        </p>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface SeasonPillProps {
  season: string;
  Icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
  active: boolean;
}

function SeasonPill({ season, Icon, active }: SeasonPillProps) {
  return (
    <div
      className={`
        flex items-center gap-2 px-3 py-2 rounded-lg
        ${active ? 'bg-[#4A6B4A]/30 ring-2 ring-[#8BAB8B]' : 'bg-[#4A3728]/30'}
      `}
    >
      <Icon className="w-5 h-5" style={{ color: active ? '#8BAB8B' : '#6B4E3D' }} />
      <span className={`text-sm font-medium ${active ? 'text-[#8BAB8B]' : 'text-[#6B4E3D]'}`}>
        {season}
      </span>
    </div>
  );
}

interface SignalBadgeProps {
  label: string;
  value: string;
  unit: string;
}

function SignalBadge({ label, value, unit }: SignalBadgeProps) {
  return (
    <div className="bg-[#4A3728]/30 rounded px-2 py-1">
      <div className="text-xs text-[#6B4E3D]">{label}</div>
      <div className="text-sm text-[#AB9080]">
        {value}
        <span className="text-[10px] text-[#6B4E3D]">{unit}</span>
      </div>
    </div>
  );
}

export default TransitionSuggester;
