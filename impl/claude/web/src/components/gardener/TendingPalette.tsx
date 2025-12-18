/**
 * TendingPalette - Tending Action Buttons
 *
 * Quick action buttons for garden tending gestures.
 * Desktop: Contextual buttons inline
 * Mobile: FloatingActions at bottom
 *
 * @see spec/protocols/2d-renaissance.md - Section 3.4E
 * @see docs/creative/visual-system.md - Uses Lucide icons
 */

import { useState } from 'react';
import {
  Eye,
  Droplet,
  GitBranch,
  Scissors,
  RotateCcw,
  Clock,
  History,
  type LucideIcon,
} from 'lucide-react';
import type { TendingVerb } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface TendingPaletteProps {
  /** Target path for tending actions */
  target: string;
  /** Callback when action is selected */
  onTend?: (verb: TendingVerb, target: string, reasoning?: string) => void;
  /** Callback to open gesture stream */
  onOpenGestures?: () => void;
  /** Display as floating actions (mobile) */
  floating?: boolean;
  /** Display inline (within detail panel) */
  inline?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Verb Configuration
// =============================================================================

const VERBS: {
  verb: TendingVerb;
  Icon: LucideIcon;
  label: string;
  description: string;
  color: string;
  bgColor: string;
}[] = [
  {
    verb: 'OBSERVE',
    Icon: Eye,
    label: 'Observe',
    description: 'Perceive without changing',
    color: '#06B6D4',
    bgColor: '#06B6D420',
  },
  {
    verb: 'WATER',
    Icon: Droplet,
    label: 'Water',
    description: 'Nurture via TextGRAD',
    color: '#8BAB8B',
    bgColor: '#8BAB8B20',
  },
  {
    verb: 'GRAFT',
    Icon: GitBranch,
    label: 'Graft',
    description: 'Add something new',
    color: '#4A6B4A',
    bgColor: '#4A6B4A20',
  },
  {
    verb: 'PRUNE',
    Icon: Scissors,
    label: 'Prune',
    description: 'Remove what no longer serves',
    color: '#C08552',
    bgColor: '#C0855220',
  },
  {
    verb: 'ROTATE',
    Icon: RotateCcw,
    label: 'Rotate',
    description: 'Change perspective',
    color: '#D4A574',
    bgColor: '#D4A57420',
  },
  {
    verb: 'WAIT',
    Icon: Clock,
    label: 'Wait',
    description: 'Allow time to pass',
    color: '#6B4E3D',
    bgColor: '#6B4E3D20',
  },
];

// =============================================================================
// Main Component
// =============================================================================

export function TendingPalette({
  target,
  onTend,
  onOpenGestures,
  floating = false,
  inline = false,
  className = '',
}: TendingPaletteProps) {
  const [expanded, setExpanded] = useState(false);

  // Floating mode: FAB cluster at bottom-right
  if (floating) {
    return (
      <div className={`fixed bottom-4 right-4 z-40 ${className}`}>
        {/* Expanded actions */}
        {expanded && (
          <div className="absolute bottom-14 right-0 flex flex-col gap-2 mb-2">
            {VERBS.map(({ verb, Icon, label, color, bgColor }) => (
              <button
                key={verb}
                onClick={() => {
                  onTend?.(verb, target);
                  setExpanded(false);
                }}
                className="w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-110"
                style={{ backgroundColor: bgColor, border: `2px solid ${color}` }}
                title={label}
              >
                <Icon className="w-5 h-5" style={{ color }} />
              </button>
            ))}

            {/* Gesture history button */}
            {onOpenGestures && (
              <button
                onClick={() => {
                  onOpenGestures();
                  setExpanded(false);
                }}
                className="w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-110 bg-[#4A3728] border-2 border-[#6B4E3D]"
                title="Gesture Stream"
              >
                <History className="w-5 h-5 text-[#AB9080]" />
              </button>
            )}
          </div>
        )}

        {/* Main FAB */}
        <button
          onClick={() => setExpanded(!expanded)}
          className={`
            w-14 h-14 rounded-full flex items-center justify-center shadow-xl
            transition-all duration-300
            ${expanded ? 'rotate-45 bg-[#C08552]' : 'bg-[#4A6B4A]'}
          `}
        >
          <svg
            className="w-6 h-6 text-[#F5E6D3]"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d={expanded ? 'M6 18L18 6M6 6l12 12' : 'M12 6v6m0 0v6m0-6h6m-6 0H6'}
            />
          </svg>
        </button>
      </div>
    );
  }

  // Inline mode: compact grid within detail panel
  if (inline) {
    return (
      <div className={className}>
        <h4 className="text-xs font-semibold text-[#6B4E3D] mb-2">Tend this plot</h4>
        <div className="grid grid-cols-3 gap-2">
          {VERBS.map(({ verb, Icon, label, color, bgColor }) => (
            <button
              key={verb}
              onClick={() => onTend?.(verb, target)}
              className="flex flex-col items-center gap-1 p-2 rounded-lg transition-colors hover:brightness-110"
              style={{ backgroundColor: bgColor }}
            >
              <Icon className="w-4 h-4" style={{ color }} />
              <span className="text-[10px]" style={{ color }}>
                {label}
              </span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  // Default: full palette with descriptions
  return (
    <div className={`bg-[#4A3728]/30 rounded-lg p-4 ${className}`}>
      <h3 className="text-xs font-semibold text-[#AB9080] uppercase tracking-wide mb-3">
        Tending Palette
      </h3>

      <div className="space-y-2">
        {VERBS.map(({ verb, Icon, label, description, color, bgColor }) => (
          <button
            key={verb}
            onClick={() => onTend?.(verb, target)}
            className="w-full flex items-center gap-3 p-3 rounded-lg transition-all hover:scale-[1.02] hover:brightness-110"
            style={{ backgroundColor: bgColor }}
          >
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: `${color}30` }}
            >
              <Icon className="w-5 h-5" style={{ color }} />
            </div>
            <div className="text-left">
              <p className="font-medium text-sm" style={{ color }}>
                {label}
              </p>
              <p className="text-xs text-[#6B4E3D]">{description}</p>
            </div>
          </button>
        ))}
      </div>

      {/* Target indicator */}
      <div className="mt-3 pt-3 border-t border-[#4A3728]">
        <p className="text-xs text-[#6B4E3D]">
          Target:{' '}
          <code className="text-[#8BAB8B] bg-[#1A2E1A] px-1.5 py-0.5 rounded">{target}</code>
        </p>
      </div>
    </div>
  );
}

export default TendingPalette;
