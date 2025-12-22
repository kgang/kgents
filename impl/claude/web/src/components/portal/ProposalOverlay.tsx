/**
 * ProposalOverlay - Agent proposal visualization
 *
 * Phase 5C: Collaborative Editing
 *
 * Shows pending agent proposals as highlighted regions with:
 * - Original vs proposed content diff
 * - Accept/reject buttons
 * - Countdown timer with visual progress
 * - Auto-accept behavior when timer expires
 *
 * Design Philosophy:
 * "Inline, not modal" — Proposals appear as highlighted text regions,
 * not modal dialogs. The text shows what will change.
 *
 * @see spec/protocols/context-perception.md §6
 */

import { memo, useState, useEffect, useRef, useCallback } from 'react';
import { Check, X, Clock, Sparkles } from 'lucide-react';
import { Breathe } from '@/components/joy';
import type { Proposal } from '@/api/collaboration';

// =============================================================================
// Constants
// =============================================================================

/** Default auto-accept delay in milliseconds */
const DEFAULT_AUTO_ACCEPT_MS = 5000;

// =============================================================================
// Types
// =============================================================================

export interface ProposalOverlayProps {
  /** The proposal to display */
  proposal: Proposal;
  /** Called when user accepts */
  onAccept: (proposalId: string) => void;
  /** Called when user rejects */
  onReject: (proposalId: string) => void;
  /** Called when auto-accepted */
  onAutoAccept?: (proposalId: string) => void;
  /** Whether to show the diff */
  showDiff?: boolean;
  /** Custom class name */
  className?: string;
}

export interface ProposalListProps {
  /** List of proposals */
  proposals: Proposal[];
  /** Called when user accepts */
  onAccept: (proposalId: string) => void;
  /** Called when user rejects */
  onReject: (proposalId: string) => void;
  /** Called when auto-accepted */
  onAutoAccept?: (proposalId: string) => void;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Countdown Hook
// =============================================================================

function useCountdown(targetTime: string, onExpire?: () => void) {
  const [timeLeft, setTimeLeft] = useState<number>(() => {
    const target = new Date(targetTime).getTime();
    return Math.max(0, target - Date.now());
  });

  const expiredRef = useRef(false);

  useEffect(() => {
    const target = new Date(targetTime).getTime();

    const interval = setInterval(() => {
      const remaining = Math.max(0, target - Date.now());
      setTimeLeft(remaining);

      if (remaining === 0 && !expiredRef.current) {
        expiredRef.current = true;
        onExpire?.();
      }
    }, 100);

    return () => clearInterval(interval);
  }, [targetTime, onExpire]);

  return timeLeft;
}

// =============================================================================
// Progress Ring
// =============================================================================

interface ProgressRingProps {
  progress: number; // 0-1
  size?: number;
  strokeWidth?: number;
  className?: string;
}

const ProgressRing = memo(function ProgressRing({
  progress,
  size = 24,
  strokeWidth = 2,
  className = '',
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - progress * circumference;

  return (
    <svg
      width={size}
      height={size}
      className={`transform -rotate-90 ${className}`}
    >
      {/* Background circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        className="text-gray-700"
      />
      {/* Progress circle */}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        className={`transition-all duration-100 ${
          progress < 0.3 ? 'text-red-400' : progress < 0.6 ? 'text-yellow-400' : 'text-green-400'
        }`}
      />
    </svg>
  );
});

// =============================================================================
// Diff View
// =============================================================================

interface DiffViewProps {
  original: string;
  proposed: string;
  className?: string;
}

const DiffView = memo(function DiffView({
  original,
  proposed,
  className = '',
}: DiffViewProps) {
  // Simple line-by-line diff (basic implementation)
  const originalLines = original.split('\n');
  const proposedLines = proposed.split('\n');

  return (
    <div className={`font-mono text-xs ${className}`}>
      <div className="mb-2">
        <div className="text-red-400 opacity-70 line-through">
          {originalLines.slice(0, 3).map((line, i) => (
            <div key={`o-${i}`} className="truncate">
              - {line || '(empty)'}
            </div>
          ))}
          {originalLines.length > 3 && (
            <div className="text-gray-500">... +{originalLines.length - 3} more lines</div>
          )}
        </div>
      </div>
      <div>
        <div className="text-green-400">
          {proposedLines.slice(0, 3).map((line, i) => (
            <div key={`p-${i}`} className="truncate">
              + {line || '(empty)'}
            </div>
          ))}
          {proposedLines.length > 3 && (
            <div className="text-gray-500">... +{proposedLines.length - 3} more lines</div>
          )}
        </div>
      </div>
    </div>
  );
});

// =============================================================================
// Single Proposal Overlay
// =============================================================================

export const ProposalOverlay = memo(function ProposalOverlay({
  proposal,
  onAccept,
  onReject,
  onAutoAccept,
  showDiff = true,
  className = '',
}: ProposalOverlayProps) {
  // Countdown
  const handleExpire = useCallback(() => {
    onAutoAccept?.(proposal.id);
  }, [proposal.id, onAutoAccept]);

  const timeLeft = useCountdown(proposal.auto_accept_at, handleExpire);
  const progress = timeLeft / DEFAULT_AUTO_ACCEPT_MS;
  const secondsLeft = Math.ceil(timeLeft / 1000);

  // Handle accept
  const handleAccept = useCallback(() => {
    onAccept(proposal.id);
  }, [proposal.id, onAccept]);

  // Handle reject
  const handleReject = useCallback(() => {
    onReject(proposal.id);
  }, [proposal.id, onReject]);

  return (
    <Breathe intensity={0.15} speed="slow">
      <div
        className={`
          relative overflow-hidden rounded-lg border
          bg-gradient-to-r from-purple-950/40 to-indigo-950/40
          border-purple-500/30 shadow-lg shadow-purple-500/10
          ${className}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-3 py-2 border-b border-purple-500/20">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-purple-200">
              {proposal.agent_name}
            </span>
            <span className="text-xs text-gray-400">proposes:</span>
          </div>
          <div className="flex items-center gap-2">
            {/* Countdown */}
            <div className="flex items-center gap-1.5 text-xs text-gray-400">
              <ProgressRing progress={progress} size={16} strokeWidth={2} />
              <span>{secondsLeft}s</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-3">
          {/* Description */}
          <p className="text-sm text-gray-200 mb-2">{proposal.description}</p>

          {/* Location */}
          <div className="text-xs text-gray-500 mb-2">
            <Clock className="w-3 h-3 inline mr-1" />
            {proposal.location}
          </div>

          {/* Diff */}
          {showDiff && proposal.original && proposal.proposed && (
            <div className="bg-gray-900/50 rounded p-2 mb-3">
              <DiffView original={proposal.original} proposed={proposal.proposed} />
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleAccept}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md
                bg-green-600/80 hover:bg-green-600 text-white text-sm
                transition-colors"
            >
              <Check className="w-4 h-4" />
              Accept
            </button>
            <button
              onClick={handleReject}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md
                bg-red-600/40 hover:bg-red-600/60 text-red-200 text-sm
                border border-red-600/30 transition-colors"
            >
              <X className="w-4 h-4" />
              Reject
            </button>
            <span className="text-xs text-gray-500 ml-auto">
              Auto-accept in {secondsLeft}s
            </span>
          </div>
        </div>

        {/* Progress bar at bottom */}
        <div className="h-1 bg-gray-800">
          <div
            className={`h-full transition-all duration-100 ${
              progress < 0.3 ? 'bg-red-500' : progress < 0.6 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${progress * 100}%` }}
          />
        </div>
      </div>
    </Breathe>
  );
});

// =============================================================================
// Proposal List
// =============================================================================

export const ProposalList = memo(function ProposalList({
  proposals,
  onAccept,
  onReject,
  onAutoAccept,
  className = '',
}: ProposalListProps) {
  if (proposals.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {proposals.map((proposal) => (
        <ProposalOverlay
          key={proposal.id}
          proposal={proposal}
          onAccept={onAccept}
          onReject={onReject}
          onAutoAccept={onAutoAccept}
        />
      ))}
    </div>
  );
});

// =============================================================================
// Compact Proposal Badge (for inline use)
// =============================================================================

export interface ProposalBadgeProps {
  /** Number of pending proposals */
  count: number;
  /** Click handler */
  onClick?: () => void;
  /** Custom class name */
  className?: string;
}

export const ProposalBadge = memo(function ProposalBadge({
  count,
  onClick,
  className = '',
}: ProposalBadgeProps) {
  if (count === 0) {
    return null;
  }

  return (
    <Breathe intensity={0.2} speed="fast">
      <button
        onClick={onClick}
        className={`
          flex items-center gap-1.5 px-2 py-1 rounded-full
          bg-purple-600/30 border border-purple-500/40
          text-purple-200 text-xs font-medium
          hover:bg-purple-600/50 transition-colors
          ${className}
        `}
      >
        <Sparkles className="w-3 h-3" />
        {count} proposal{count !== 1 ? 's' : ''}
      </button>
    </Breathe>
  );
});

// =============================================================================
// Exports
// =============================================================================

export default ProposalOverlay;
