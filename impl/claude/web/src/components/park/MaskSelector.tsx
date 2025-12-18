/**
 * MaskSelector: Dialogue mask selection UI.
 *
 * Wave 3: Punchdrunk Park crisis practice.
 *
 * Features:
 * - 8 mask cards with archetype icons (Lucide)
 * - Eigenvector transform preview
 * - Don/doff controls
 * - Active mask indicator
 *
 * Per visual-system.md, kgents uses Lucide icons exclusively.
 */

import { useState, useMemo } from 'react';
import { Theater, Check } from 'lucide-react';
import type { ParkMaskInfo, ParkMaskArchetype, ParkEigenvectorTransform } from '../../api/types';
import { PARK_MASK_CONFIG, PARK_EIGENVECTOR_CONFIG } from '../../api/types';
import { STATE_COLORS, GRAYS, SEMANTIC_COLORS, getMaskArchetypeIcon } from '../../constants';

interface MaskSelectorProps {
  masks: ParkMaskInfo[];
  currentMask: ParkMaskInfo | null;
  onDon: (maskName: string) => void;
  onDoff: () => void;
  disabled?: boolean;
  compact?: boolean;
  className?: string;
}

/**
 * Eigenvector radar chart for mask transform preview.
 */
interface MaskRadarProps {
  transform: ParkEigenvectorTransform;
  size?: number;
  className?: string;
}

function MaskRadar({ transform, size = 120, className = '' }: MaskRadarProps) {
  const center = size / 2;
  const radius = (size / 2) * 0.75;
  const dimensions = Object.keys(PARK_EIGENVECTOR_CONFIG) as Array<keyof ParkEigenvectorTransform>;

  // Calculate points for the radar polygon
  const points = useMemo(() => {
    return dimensions.map((key, index) => {
      const angle = (Math.PI * 2 * index) / dimensions.length - Math.PI / 2;
      // Transform values are deltas, center at 0.5 + delta
      const value = Math.max(0, Math.min(1, 0.5 + transform[key]));
      const x = center + radius * value * Math.cos(angle);
      const y = center + radius * value * Math.sin(angle);
      return { x, y, key, value: transform[key] };
    });
  }, [transform, center, radius, dimensions]);

  // Generate path
  const path = points.map((p, i) =>
    i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`
  ).join(' ') + ' Z';

  // Baseline (0.5) path
  const baselinePoints = dimensions.map((_, index) => {
    const angle = (Math.PI * 2 * index) / dimensions.length - Math.PI / 2;
    const x = center + radius * 0.5 * Math.cos(angle);
    const y = center + radius * 0.5 * Math.sin(angle);
    return { x, y };
  });
  const baselinePath = baselinePoints.map((p, i) =>
    i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`
  ).join(' ') + ' Z';

  return (
    <svg width={size} height={size} className={className} viewBox={`0 0 ${size} ${size}`}>
      {/* Grid circles */}
      {[0.25, 0.5, 0.75, 1.0].map((ringValue) => (
        <circle
          key={ringValue}
          cx={center}
          cy={center}
          r={radius * ringValue}
          fill="none"
          stroke={GRAYS[700]}
          strokeWidth={1}
          opacity={0.3}
        />
      ))}

      {/* Axis lines */}
      {dimensions.map((_, index) => {
        const angle = (Math.PI * 2 * index) / dimensions.length - Math.PI / 2;
        const x2 = center + radius * Math.cos(angle);
        const y2 = center + radius * Math.sin(angle);
        return (
          <line
            key={index}
            x1={center}
            y1={center}
            x2={x2}
            y2={y2}
            stroke={GRAYS[700]}
            strokeWidth={1}
            opacity={0.3}
          />
        );
      })}

      {/* Baseline */}
      <path
        d={baselinePath}
        fill="none"
        stroke={GRAYS[500]}
        strokeWidth={1}
        strokeDasharray="2,2"
      />

      {/* Transform polygon */}
      <path
        d={path}
        fill={SEMANTIC_COLORS.creation}
        fillOpacity={0.3}
        stroke={SEMANTIC_COLORS.creation}
        strokeWidth={2}
      />

      {/* Data points with delta indicators */}
      {points.map(({ x, y, key, value }) => {
        void PARK_EIGENVECTOR_CONFIG[key]; // Access for future label rendering
        const isPositive = value > 0;
        const isNegative = value < 0;
        return (
          <g key={key}>
            <circle
              cx={x}
              cy={y}
              r={4}
              fill={isPositive ? STATE_COLORS.success : isNegative ? STATE_COLORS.error : GRAYS[500]}
              stroke="white"
              strokeWidth={1}
            />
          </g>
        );
      })}
    </svg>
  );
}

/**
 * Transform delta list.
 */
interface TransformDeltasProps {
  transform: ParkEigenvectorTransform;
  compact?: boolean;
  className?: string;
}

function TransformDeltas({ transform, compact = false, className = '' }: TransformDeltasProps) {
  const deltas = Object.entries(transform)
    .filter(([_, value]) => value !== 0)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));

  if (deltas.length === 0) {
    return <span className="text-gray-500 text-xs">No transform</span>;
  }

  if (compact) {
    const positive = deltas.filter(([_, v]) => v > 0).slice(0, 2);
    const negative = deltas.filter(([_, v]) => v < 0).slice(0, 2);

    return (
      <div className={`flex items-center gap-1 ${className}`}>
        {positive.map(([key, value]) => (
          <span key={key} className="text-green-400 text-xs">
            {PARK_EIGENVECTOR_CONFIG[key]?.label?.charAt(0)}+{Math.round(value * 100)}%
          </span>
        ))}
        {negative.map(([key, value]) => (
          <span key={key} className="text-red-400 text-xs">
            {PARK_EIGENVECTOR_CONFIG[key]?.label?.charAt(0)}{Math.round(value * 100)}%
          </span>
        ))}
      </div>
    );
  }

  return (
    <div className={`space-y-1 ${className}`}>
      {deltas.map(([key, value]) => {
        const config = PARK_EIGENVECTOR_CONFIG[key];
        const isPositive = value > 0;
        return (
          <div key={key} className="flex items-center justify-between text-xs">
            <span className="text-gray-400">{config?.label || key}</span>
            <span className={isPositive ? 'text-green-400' : 'text-red-400'}>
              {isPositive ? '+' : ''}{Math.round(value * 100)}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Single mask card.
 */
interface MaskCardProps {
  mask: ParkMaskInfo;
  isActive: boolean;
  onSelect: () => void;
  disabled?: boolean;
  compact?: boolean;
}

function MaskCard({ mask, isActive, onSelect, disabled, compact }: MaskCardProps) {
  const config = PARK_MASK_CONFIG[mask.archetype as ParkMaskArchetype];
  const [showDetails, setShowDetails] = useState(false);
  const MaskIcon = getMaskArchetypeIcon(mask.archetype);

  if (compact) {
    return (
      <button
        onClick={onSelect}
        disabled={disabled}
        className={`
          flex items-center gap-2 p-2 rounded-lg transition-all
          ${isActive
            ? 'bg-amber-900/40 border-2 border-amber-500'
            : 'bg-gray-800/50 border border-gray-700 hover:border-gray-500'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <MaskIcon className="w-5 h-5" style={{ color: config?.color || '#6b7280' }} />
        <div className="text-left">
          <p className="text-xs font-medium text-gray-200">{mask.name}</p>
          <p className="text-[10px] text-gray-500">{mask.description}</p>
        </div>
      </button>
    );
  }

  return (
    <div
      className={`
        relative rounded-lg transition-all cursor-pointer
        ${isActive
          ? 'bg-amber-900/30 border-2 border-amber-500 shadow-lg shadow-amber-500/20'
          : 'bg-gray-800/50 border border-gray-700 hover:border-gray-500'
        }
      `}
      onClick={() => setShowDetails(!showDetails)}
    >
      {/* Header */}
      <div className="p-3">
        <div className="flex items-center gap-2 mb-2">
          <div
            className="p-2 rounded-lg"
            style={{ backgroundColor: `${config?.color || '#6b7280'}22` }}
          >
            <MaskIcon className="w-6 h-6" style={{ color: config?.color || '#6b7280' }} />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-200">{mask.name}</p>
            <p className="text-xs text-gray-500">{mask.archetype}</p>
          </div>
        </div>

        {/* Description */}
        <p className="text-xs text-gray-400 mb-2">{mask.description}</p>

        {/* Compact deltas */}
        <TransformDeltas transform={mask.transform} compact />

        {/* Action button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onSelect();
          }}
          disabled={disabled}
          className={`
            mt-3 w-full py-1.5 text-xs font-medium rounded transition-colors
            ${isActive
              ? 'bg-amber-600 hover:bg-amber-700 text-white'
              : 'bg-gray-700 hover:bg-gray-600 text-gray-200'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          {isActive ? 'Doff Mask' : 'Don Mask'}
        </button>
      </div>

      {/* Expanded details */}
      {showDetails && (
        <div className="border-t border-gray-700 p-3">
          {/* Radar */}
          <div className="flex justify-center mb-3">
            <MaskRadar transform={mask.transform} size={100} />
          </div>

          {/* Full deltas */}
          <TransformDeltas transform={mask.transform} />

          {/* Abilities */}
          {mask.special_abilities.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-1">Abilities</p>
              <div className="flex flex-wrap gap-1">
                {mask.special_abilities.map((ability) => (
                  <span
                    key={ability}
                    className="text-[10px] px-1.5 py-0.5 bg-green-900/30 text-green-400 rounded"
                  >
                    {ability}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Restrictions */}
          {mask.restrictions.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-gray-500 mb-1">Restrictions</p>
              <div className="flex flex-wrap gap-1">
                {mask.restrictions.map((restriction) => (
                  <span
                    key={restriction}
                    className="text-[10px] px-1.5 py-0.5 bg-red-900/30 text-red-400 rounded"
                  >
                    {restriction}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Flavor text */}
          {mask.flavor_text && (
            <p className="mt-3 text-xs text-gray-500 italic">
              "{mask.flavor_text}"
            </p>
          )}
        </div>
      )}

      {/* Active indicator */}
      {isActive && (
        <div className="absolute -top-2 -right-2 w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center">
          <Check className="w-3 h-3 text-white" />
        </div>
      )}
    </div>
  );
}

export function MaskSelector({
  masks,
  currentMask,
  onDon,
  onDoff,
  disabled = false,
  compact = false,
  className = '',
}: MaskSelectorProps) {
  if (masks.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <Theater className="w-10 h-10 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No masks available</p>
      </div>
    );
  }

  const handleSelect = (mask: ParkMaskInfo) => {
    if (currentMask?.name === mask.name) {
      onDoff();
    } else {
      // Doff first if wearing another mask
      if (currentMask) {
        onDoff();
      }
      // Use lowercase name for API
      onDon(mask.name.toLowerCase().replace('the ', ''));
    }
  };

  if (compact) {
    return (
      <div className={`grid grid-cols-2 gap-2 ${className}`}>
        {masks.map((mask) => (
          <MaskCard
            key={mask.name}
            mask={mask}
            isActive={currentMask?.name === mask.name}
            onSelect={() => handleSelect(mask)}
            disabled={disabled}
            compact
          />
        ))}
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
      {masks.map((mask) => (
        <MaskCard
          key={mask.name}
          mask={mask}
          isActive={currentMask?.name === mask.name}
          onSelect={() => handleSelect(mask)}
          disabled={disabled}
        />
      ))}
    </div>
  );
}

/**
 * Current mask display badge.
 */
interface CurrentMaskBadgeProps {
  mask: ParkMaskInfo | null;
  onDoff?: () => void;
  className?: string;
}

export function CurrentMaskBadge({ mask, onDoff, className = '' }: CurrentMaskBadgeProps) {
  if (!mask) {
    return (
      <div className={`flex items-center gap-2 px-3 py-1.5 bg-gray-800/50 rounded-lg ${className}`}>
        <Theater className="w-5 h-5 opacity-50" />
        <span className="text-xs text-gray-500">No mask</span>
      </div>
    );
  }

  const config = PARK_MASK_CONFIG[mask.archetype as ParkMaskArchetype];
  const MaskIcon = getMaskArchetypeIcon(mask.archetype);

  return (
    <div
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded-lg
        ${className}
      `}
      style={{ backgroundColor: `${config?.color || '#6b7280'}22` }}
    >
      <MaskIcon className="w-5 h-5" style={{ color: config?.color || '#9ca3af' }} />
      <div>
        <p className="text-xs font-medium" style={{ color: config?.color || '#9ca3af' }}>
          {mask.name}
        </p>
        <p className="text-[10px] text-gray-500">{mask.description}</p>
      </div>
      {onDoff && (
        <button
          onClick={onDoff}
          className="ml-2 text-xs text-gray-400 hover:text-white"
        >
          ×
        </button>
      )}
    </div>
  );
}

export default MaskSelector;
