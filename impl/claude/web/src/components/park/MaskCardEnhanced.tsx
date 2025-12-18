/**
 * MaskCardEnhanced: Mask card with affordances preview and debt cost.
 *
 * Phase 3 of park-town-design-overhaul: Enhances MaskCard to show
 * affordances, restrictions, and debt cost at a glance.
 *
 * Features:
 * - Visual affordance grid showing what the mask enables
 * - Restrictions list
 * - Debt cost indicator
 * - Eigenvector transform radar (from MaskSelector)
 * - AGENTESE observer-dependent teaching
 *
 * @see plans/park-town-design-overhaul.md (Journey 8: Mask Selection)
 * @see spec/park/masks.md (mask specification)
 */

import { useState, useMemo } from 'react';
import { Theater, Check, Lock, Unlock, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ParkMaskInfo, ParkMaskArchetype, ParkEigenvectorTransform } from '@/api/types';
import { PARK_MASK_CONFIG, PARK_EIGENVECTOR_CONFIG } from '@/api/types';
import { TeachingCallout, TEACHING_MESSAGES } from '@/components/categorical/TeachingCallout';
import { getMaskArchetypeIcon } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export interface MaskCardEnhancedProps {
  mask: ParkMaskInfo;
  isActive: boolean;
  onSelect: () => void;
  disabled?: boolean;
  showAffordances?: boolean;
  showRadar?: boolean;
  showDebtCost?: boolean;
  compact?: boolean;
  className?: string;
}

export interface MaskGridEnhancedProps {
  masks: ParkMaskInfo[];
  currentMask: ParkMaskInfo | null;
  onDon: (maskName: string) => void;
  onDoff: () => void;
  disabled?: boolean;
  showAffordances?: boolean;
  showTeaching?: boolean;
  compact?: boolean;
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Estimate debt cost based on mask archetype.
 * More powerful masks have higher debt costs.
 */
function estimateDebtCost(archetype: ParkMaskArchetype): number {
  const costs: Record<ParkMaskArchetype, number> = {
    TRICKSTER: 0.06,
    DREAMER: 0.04,
    SKEPTIC: 0.05,
    ARCHITECT: 0.08,
    CHILD: 0.03,
    SAGE: 0.04,
    WARRIOR: 0.10,
    HEALER: 0.05,
  };
  return costs[archetype] ?? 0.05;
}

/**
 * Categorize affordances for display.
 */
function categorizeAffordances(abilities: string[]): { primary: string[]; secondary: string[] } {
  const primary = abilities.slice(0, 3);
  const secondary = abilities.slice(3);
  return { primary, secondary };
}

// =============================================================================
// Sub-components
// =============================================================================

interface MiniRadarProps {
  transform: ParkEigenvectorTransform;
  size?: number;
  className?: string;
}

function MiniRadar({ transform, size = 80, className = '' }: MiniRadarProps) {
  const center = size / 2;
  const radius = (size / 2) * 0.7;
  const dimensions = Object.keys(PARK_EIGENVECTOR_CONFIG) as Array<keyof ParkEigenvectorTransform>;

  const points = useMemo(() => {
    return dimensions.map((key, index) => {
      const angle = (Math.PI * 2 * index) / dimensions.length - Math.PI / 2;
      const value = Math.max(0, Math.min(1, 0.5 + transform[key]));
      const x = center + radius * value * Math.cos(angle);
      const y = center + radius * value * Math.sin(angle);
      return { x, y, key, value: transform[key] };
    });
  }, [transform, center, radius, dimensions]);

  const path =
    points.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ') + ' Z';

  return (
    <svg width={size} height={size} className={className} viewBox={`0 0 ${size} ${size}`}>
      {/* Background circles */}
      {[0.5, 1.0].map((ringValue) => (
        <circle
          key={ringValue}
          cx={center}
          cy={center}
          r={radius * ringValue}
          fill="none"
          stroke="#374151"
          strokeWidth={1}
          opacity={0.3}
        />
      ))}

      {/* Transform polygon */}
      <path d={path} fill="#a855f7" fillOpacity={0.3} stroke="#a855f7" strokeWidth={1.5} />

      {/* Data points */}
      {points.map(({ x, y, key, value }) => (
        <circle
          key={key}
          cx={x}
          cy={y}
          r={3}
          fill={value > 0 ? '#22c55e' : value < 0 ? '#ef4444' : '#6b7280'}
        />
      ))}
    </svg>
  );
}

interface AffordanceGridProps {
  abilities: string[];
  restrictions: string[];
  compact?: boolean;
}

function AffordanceGrid({ abilities, restrictions, compact = false }: AffordanceGridProps) {
  const { primary, secondary } = categorizeAffordances(abilities);

  return (
    <div className={cn('space-y-2', compact && 'space-y-1')}>
      {/* Primary affordances */}
      <div className="flex flex-wrap gap-1">
        {primary.map((ability) => (
          <span
            key={ability}
            className={cn(
              'inline-flex items-center gap-1 rounded-full bg-green-900/30 text-green-400 border border-green-500/30',
              compact ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
            )}
          >
            <Unlock className={compact ? 'w-2 h-2' : 'w-3 h-3'} />
            {ability}
          </span>
        ))}
      </div>

      {/* Secondary affordances (if not compact) */}
      {!compact && secondary.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {secondary.map((ability) => (
            <span
              key={ability}
              className="text-[10px] px-1.5 py-0.5 bg-green-900/20 text-green-500 rounded"
            >
              {ability}
            </span>
          ))}
        </div>
      )}

      {/* Restrictions */}
      {restrictions.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {restrictions.slice(0, compact ? 2 : 4).map((restriction) => (
            <span
              key={restriction}
              className={cn(
                'inline-flex items-center gap-1 rounded-full bg-red-900/30 text-red-400 border border-red-500/30',
                compact ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
              )}
            >
              <Lock className={compact ? 'w-2 h-2' : 'w-3 h-3'} />
              {restriction}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

interface DebtCostBadgeProps {
  cost: number;
  compact?: boolean;
}

function DebtCostBadge({ cost, compact = false }: DebtCostBadgeProps) {
  const percent = Math.round(cost * 100);
  const severity = cost <= 0.04 ? 'low' : cost <= 0.07 ? 'medium' : 'high';

  const colors = {
    low: 'text-green-400 bg-green-900/20 border-green-500/30',
    medium: 'text-amber-400 bg-amber-900/20 border-amber-500/30',
    high: 'text-red-400 bg-red-900/20 border-red-500/30',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full border',
        colors[severity],
        compact ? 'px-1.5 py-0.5 text-[10px]' : 'px-2 py-0.5 text-xs'
      )}
    >
      <Zap className={compact ? 'w-2 h-2' : 'w-3 h-3'} />+{percent}%
    </span>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function MaskCardEnhanced({
  mask,
  isActive,
  onSelect,
  disabled = false,
  showAffordances = true,
  showRadar = false,
  showDebtCost = true,
  compact = false,
  className = '',
}: MaskCardEnhancedProps) {
  const [expanded, setExpanded] = useState(false);
  const config = PARK_MASK_CONFIG[mask.archetype as ParkMaskArchetype];
  const MaskIcon = getMaskArchetypeIcon(mask.archetype);
  const debtCost = estimateDebtCost(mask.archetype as ParkMaskArchetype);

  if (compact) {
    return (
      <button
        onClick={onSelect}
        disabled={disabled}
        className={cn(
          'flex items-center gap-2 p-2 rounded-lg transition-all w-full text-left',
          isActive
            ? 'bg-amber-900/40 border-2 border-amber-500'
            : 'bg-gray-800/50 border border-gray-700 hover:border-gray-500',
          disabled && 'opacity-50 cursor-not-allowed',
          className
        )}
      >
        <div
          className="p-1.5 rounded-lg flex-shrink-0"
          style={{ backgroundColor: `${config?.color || '#6b7280'}22` }}
        >
          <MaskIcon className="w-5 h-5" style={{ color: config?.color || '#6b7280' }} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-gray-200 truncate">{mask.name}</p>
          <p className="text-[10px] text-gray-500 truncate">{mask.description}</p>
        </div>
        {showDebtCost && <DebtCostBadge cost={debtCost} compact />}
        {isActive && <Check className="w-4 h-4 text-amber-500" />}
      </button>
    );
  }

  return (
    <div
      className={cn(
        'relative rounded-xl transition-all duration-300',
        isActive
          ? 'bg-amber-900/30 border-2 border-amber-500 shadow-lg shadow-amber-500/20'
          : 'bg-gray-800/50 border border-gray-700 hover:border-gray-500',
        className
      )}
    >
      {/* Header - clickable to expand */}
      <div
        className="p-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setExpanded(!expanded);
          }
        }}
      >
        <div className="flex items-start gap-3">
          {/* Icon */}
          <div
            className="p-2.5 rounded-xl flex-shrink-0"
            style={{ backgroundColor: `${config?.color || '#6b7280'}22` }}
          >
            <MaskIcon className="w-7 h-7" style={{ color: config?.color || '#6b7280' }} />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <p className="text-sm font-semibold text-gray-200">{mask.name}</p>
              {showDebtCost && <DebtCostBadge cost={debtCost} />}
            </div>
            <p className="text-xs text-gray-500 mb-1">{mask.archetype}</p>
            <p className="text-xs text-gray-400">{mask.description}</p>
          </div>
        </div>

        {/* Affordances preview */}
        {showAffordances && (
          <div className="mt-3">
            <AffordanceGrid
              abilities={mask.special_abilities}
              restrictions={mask.restrictions}
            />
          </div>
        )}

        {/* Action button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect();
          }}
          disabled={disabled}
          className={cn(
            'mt-4 w-full py-2 text-sm font-medium rounded-lg transition-colors',
            isActive
              ? 'bg-amber-600 hover:bg-amber-700 text-white'
              : 'bg-gray-700 hover:bg-gray-600 text-gray-200',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          {isActive ? 'Doff Mask' : 'Don Mask'}
        </button>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-gray-700 p-4 space-y-4">
          {/* Radar */}
          {showRadar && (
            <div className="flex justify-center">
              <MiniRadar transform={mask.transform} size={100} />
            </div>
          )}

          {/* Transform deltas */}
          <div>
            <p className="text-xs text-gray-500 mb-2">Eigenvector Transform</p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(mask.transform)
                .filter(([_, value]) => value !== 0)
                .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
                .map(([key, value]) => {
                  const config = PARK_EIGENVECTOR_CONFIG[key];
                  const isPositive = value > 0;
                  return (
                    <div key={key} className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">{config?.label || key}</span>
                      <span className={isPositive ? 'text-green-400' : 'text-red-400'}>
                        {isPositive ? '+' : ''}
                        {Math.round(value * 100)}%
                      </span>
                    </div>
                  );
                })}
            </div>
          </div>

          {/* Flavor text */}
          {mask.flavor_text && (
            <p className="text-xs text-gray-500 italic border-l-2 border-gray-600 pl-3">
              "{mask.flavor_text}"
            </p>
          )}
        </div>
      )}

      {/* Active indicator */}
      {isActive && (
        <div className="absolute -top-2 -right-2 w-6 h-6 bg-amber-500 rounded-full flex items-center justify-center shadow-lg">
          <Check className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Grid Component
// =============================================================================

export function MaskGridEnhanced({
  masks,
  currentMask,
  onDon,
  onDoff,
  disabled = false,
  showAffordances = true,
  showTeaching = true,
  compact = false,
  className = '',
}: MaskGridEnhancedProps) {
  const handleSelect = (mask: ParkMaskInfo) => {
    if (currentMask?.name === mask.name) {
      onDoff();
    } else {
      if (currentMask) {
        onDoff();
      }
      onDon(mask.name.toLowerCase().replace('the ', ''));
    }
  };

  if (masks.length === 0) {
    return (
      <div className={cn('text-center py-8 text-gray-500', className)}>
        <Theater className="w-10 h-10 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No masks available</p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div
        className={cn(
          'grid gap-3',
          compact ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-2'
        )}
      >
        {masks.map((mask) => (
          <MaskCardEnhanced
            key={mask.name}
            mask={mask}
            isActive={currentMask?.name === mask.name}
            onSelect={() => handleSelect(mask)}
            disabled={disabled}
            showAffordances={showAffordances}
            showDebtCost={!compact}
            compact={compact}
          />
        ))}
      </div>

      {/* Teaching callout */}
      {showTeaching && !compact && (
        <TeachingCallout category="conceptual" compact>
          {TEACHING_MESSAGES.observer_dependent}
        </TeachingCallout>
      )}
    </div>
  );
}

export default MaskCardEnhanced;
