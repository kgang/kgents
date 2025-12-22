/**
 * EvidenceBadge - Display computed evidence strength
 *
 * Phase 5D: Integration
 *
 * Shows evidence strength as a badge with:
 * - Color-coded strength indicator (weak → definitive)
 * - Tooltip with metrics breakdown (uses Portal to escape overflow containers)
 * - Optional animation for strong/definitive evidence
 *
 * Design Philosophy:
 * "Evidence strength is computed, not set" — The badge shows derived
 * strength from trail characteristics, not manually chosen values.
 *
 * @see spec/protocols/context-perception.md §6
 * @see plans/context-perception-phase5.md §5.D4
 */

import { memo, useMemo, useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Shield, ShieldCheck, ShieldAlert, ShieldQuestion } from 'lucide-react';
import { Breathe } from '@/components/joy';
import type { EvidenceStrength, TrailEvidence } from '@/api/trail';

// =============================================================================
// Constants
// =============================================================================

/**
 * Evidence strength configuration.
 */
const EVIDENCE_CONFIG: Record<
  EvidenceStrength,
  {
    label: string;
    color: string;
    bgColor: string;
    borderColor: string;
    icon: typeof Shield;
    breathe: boolean;
  }
> = {
  weak: {
    label: 'Weak',
    color: 'text-gray-400',
    bgColor: 'bg-gray-800/50',
    borderColor: 'border-gray-700',
    icon: ShieldQuestion,
    breathe: false,
  },
  moderate: {
    label: 'Moderate',
    color: 'text-amber-400',
    bgColor: 'bg-amber-950/30',
    borderColor: 'border-amber-800/50',
    icon: ShieldAlert,
    breathe: false,
  },
  strong: {
    label: 'Strong',
    color: 'text-blue-400',
    bgColor: 'bg-blue-950/30',
    borderColor: 'border-blue-800/50',
    icon: ShieldCheck,
    breathe: true,
  },
  definitive: {
    label: 'Definitive',
    color: 'text-green-400',
    bgColor: 'bg-green-950/30',
    borderColor: 'border-green-800/50',
    icon: ShieldCheck,
    breathe: true,
  },
};

// =============================================================================
// Types
// =============================================================================

export interface EvidenceBadgeProps {
  /** Evidence strength level */
  strength: EvidenceStrength;
  /** Optional full evidence data for tooltip */
  evidence?: TrailEvidence;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Show label text */
  showLabel?: boolean;
  /** Custom class name */
  className?: string;
}


// =============================================================================
// Evidence Tooltip
// =============================================================================

/**
 * Portal-based tooltip that escapes overflow: hidden containers.
 * Renders directly to document.body with calculated position.
 */
interface TooltipPortalProps {
  evidence: TrailEvidence;
  anchorRef: React.RefObject<HTMLDivElement>;
  isVisible: boolean;
}

const TooltipPortal = memo(function TooltipPortal({
  evidence,
  anchorRef,
  isVisible,
}: TooltipPortalProps) {
  const config = EVIDENCE_CONFIG[evidence.evidence_strength];
  const [position, setPosition] = useState({ top: 0, left: 0 });

  // Calculate position relative to anchor element
  useEffect(() => {
    if (isVisible && anchorRef.current) {
      const rect = anchorRef.current.getBoundingClientRect();
      setPosition({
        top: rect.top - 8, // Above the element with gap
        left: rect.left + rect.width / 2, // Centered
      });
    }
  }, [isVisible, anchorRef]);

  if (!isVisible) return null;

  const tooltipContent = (
    <div
      className="fixed z-[9999] w-48 p-3 rounded-lg shadow-xl
        bg-gray-900 border border-gray-700
        text-xs text-gray-300
        animate-in fade-in duration-200"
      style={{
        top: position.top,
        left: position.left,
        transform: 'translate(-50%, -100%)',
      }}
    >
      {/* Header */}
      <div className={`font-medium mb-2 ${config.color}`}>
        Evidence: {config.label}
      </div>

      {/* Metrics */}
      <div className="space-y-1.5">
        <div className="flex justify-between">
          <span className="text-gray-500">Steps taken:</span>
          <span className="text-gray-200">{evidence.step_count}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Unique paths:</span>
          <span className="text-gray-200">{evidence.unique_paths}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">Edge types:</span>
          <span className="text-gray-200">{evidence.unique_edges}</span>
        </div>
      </div>

      {/* Thresholds hint */}
      <div className="mt-2 pt-2 border-t border-gray-700 text-gray-500 text-[10px]">
        {evidence.evidence_strength === 'weak' && '3+ steps, 2+ paths → moderate'}
        {evidence.evidence_strength === 'moderate' && '5+ steps, 4+ paths → strong'}
        {evidence.evidence_strength === 'strong' && '10+ steps, 8+ paths → definitive'}
        {evidence.evidence_strength === 'definitive' && 'Maximum evidence level'}
      </div>

      {/* Arrow pointing down */}
      <div
        className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2
          bg-gray-900 border-r border-b border-gray-700 rotate-45"
      />
    </div>
  );

  // Render to document.body via Portal to escape any overflow:hidden containers
  return createPortal(tooltipContent, document.body);
});


// =============================================================================
// Evidence Badge
// =============================================================================

export const EvidenceBadge = memo(function EvidenceBadge({
  strength,
  evidence,
  size = 'md',
  showLabel = true,
  className = '',
}: EvidenceBadgeProps) {
  const config = EVIDENCE_CONFIG[strength];
  const Icon = config.icon;

  // Hover state for portal tooltip
  const [isHovered, setIsHovered] = useState(false);
  const badgeRef = useRef<HTMLDivElement>(null);

  // Size classes
  const sizeClasses = useMemo(() => {
    switch (size) {
      case 'sm':
        return {
          container: 'px-1.5 py-0.5 gap-1',
          icon: 'w-3 h-3',
          text: 'text-[10px]',
        };
      case 'lg':
        return {
          container: 'px-3 py-1.5 gap-2',
          icon: 'w-5 h-5',
          text: 'text-sm',
        };
      default:
        return {
          container: 'px-2 py-1 gap-1.5',
          icon: 'w-4 h-4',
          text: 'text-xs',
        };
    }
  }, [size]);

  const badge = (
    <div
      ref={badgeRef}
      className={`
        relative inline-flex items-center rounded-full
        border transition-colors cursor-pointer
        ${config.bgColor} ${config.borderColor}
        ${sizeClasses.container}
        ${className}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Icon className={`${sizeClasses.icon} ${config.color}`} />
      {showLabel && (
        <span className={`${sizeClasses.text} ${config.color} font-medium`}>
          {config.label}
        </span>
      )}

      {/* Portal-based tooltip that escapes overflow:hidden containers */}
      {evidence && (
        <TooltipPortal
          evidence={evidence}
          anchorRef={badgeRef}
          isVisible={isHovered}
        />
      )}
    </div>
  );

  // Wrap with Breathe for strong/definitive
  if (config.breathe) {
    return (
      <Breathe intensity={0.15} speed="slow">
        {badge}
      </Breathe>
    );
  }

  return badge;
});

// =============================================================================
// Evidence Progress Bar (for detailed view)
// =============================================================================

export interface EvidenceProgressProps {
  /** Full evidence data */
  evidence: TrailEvidence;
  /** Custom class name */
  className?: string;
}

export const EvidenceProgress = memo(function EvidenceProgress({
  evidence,
  className = '',
}: EvidenceProgressProps) {
  // Compute progress toward next level
  const progress = useMemo(() => {
    const { step_count, unique_paths, evidence_strength } = evidence;

    // Progress to next level (0-1)
    switch (evidence_strength) {
      case 'weak':
        // Need 3 steps, 2 paths for moderate
        return Math.min(1, (step_count / 3 + unique_paths / 2) / 2);
      case 'moderate':
        // Need 5 steps, 4 paths for strong
        return Math.min(1, (step_count / 5 + unique_paths / 4) / 2);
      case 'strong':
        // Need 10 steps, 8 paths for definitive
        return Math.min(1, (step_count / 10 + unique_paths / 8) / 2);
      case 'definitive':
        return 1;
      default:
        return 0;
    }
  }, [evidence]);

  const config = EVIDENCE_CONFIG[evidence.evidence_strength];
  const nextLevel =
    evidence.evidence_strength === 'weak'
      ? 'moderate'
      : evidence.evidence_strength === 'moderate'
        ? 'strong'
        : evidence.evidence_strength === 'strong'
          ? 'definitive'
          : null;

  return (
    <div className={`space-y-1 ${className}`}>
      <div className="flex items-center justify-between text-xs">
        <span className={config.color}>{config.label}</span>
        {nextLevel && (
          <span className="text-gray-500">
            {Math.round(progress * 100)}% to {nextLevel}
          </span>
        )}
      </div>
      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            evidence.evidence_strength === 'weak'
              ? 'bg-gray-500'
              : evidence.evidence_strength === 'moderate'
                ? 'bg-amber-500'
                : evidence.evidence_strength === 'strong'
                  ? 'bg-blue-500'
                  : 'bg-green-500'
          }`}
          style={{ width: `${progress * 100}%` }}
        />
      </div>
    </div>
  );
});

// =============================================================================
// Exports
// =============================================================================

export default EvidenceBadge;
