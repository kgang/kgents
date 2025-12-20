/**
 * TerraceCard - Knowledge entry card for Terrace (curated knowledge).
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Displays a single Terrace knowledge entry with:
 * - Topic title
 * - Content preview
 * - Version and age metadata
 * - Confidence meter
 * - Tags
 * - Action buttons for history and evolve
 *
 * Uses ElasticCard for priority-aware responsive behavior.
 *
 * @example
 * <TerraceCard
 *   topic="React Hooks Best Practices"
 *   content="Use useMemo for expensive calculations..."
 *   version={3}
 *   confidence={0.9}
 *   tags={['react', 'hooks']}
 *   ageDays={5}
 *   onEvolve={() => setEditing(true)}
 * />
 */

import React from 'react';
import { Layers } from 'lucide-react';
import { ElasticCard } from '../elastic/ElasticCard';
import { Breathe } from '../joy/Breathe';

// =============================================================================
// Types
// =============================================================================

export interface TerraceCardProps {
  /** Knowledge topic */
  topic: string;
  /** Knowledge content */
  content: string;
  /** Version number */
  version: number;
  /** Confidence score (0-1) */
  confidence: number;
  /** Associated tags */
  tags: string[];
  /** Age in days */
  ageDays: number;
  /** Status of this entry */
  status?: 'CURRENT' | 'SUPERSEDED';
  /** Callback when user wants to evolve this entry */
  onEvolve?: () => void;
  /** Callback when user wants to see history */
  onShowHistory?: () => void;
  /** Callback when card is clicked */
  onClick?: () => void;
  /** Whether card is selected */
  isSelected?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * ConfidenceMeter - Visual representation of confidence level.
 */
function ConfidenceMeter({ value }: { value: number }): React.ReactElement {
  const percentage = Math.round(value * 100);
  const color =
    value >= 0.9
      ? 'bg-green-500'
      : value >= 0.7
        ? 'bg-yellow-500'
        : value >= 0.5
          ? 'bg-orange-500'
          : 'bg-red-500';

  return (
    <div className="flex items-center gap-1.5" title={`Confidence: ${percentage}%`}>
      <div className="w-12 h-1.5 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-xs text-gray-500">{percentage}%</span>
    </div>
  );
}

/**
 * Format age for display.
 */
function formatAge(days: number): string {
  if (days < 1) return 'today';
  if (days === 1) return '1d ago';
  if (days < 7) return `${Math.round(days)}d ago`;
  if (days < 30) return `${Math.round(days / 7)}w ago`;
  if (days < 365) return `${Math.round(days / 30)}mo ago`;
  return `${Math.round(days / 365)}y ago`;
}

// =============================================================================
// Component
// =============================================================================

export function TerraceCard({
  topic,
  content,
  version,
  confidence,
  tags,
  ageDays,
  status = 'CURRENT',
  onEvolve,
  onShowHistory,
  onClick,
  isSelected = false,
  className = '',
}: TerraceCardProps): React.ReactElement {
  // High confidence entries get the breathing animation
  const isHighConfidence = confidence >= 0.9;
  const isSuperseded = status === 'SUPERSEDED';

  // Truncate content for summary
  const summary = content.length > 100 ? content.slice(0, 100) + '...' : content;

  const card = (
    <ElasticCard
      priority={confidence * 10}
      title={topic}
      summary={summary}
      icon={<Layers className={`w-4 h-4 ${isSuperseded ? 'text-gray-500' : 'text-cyan-400'}`} />}
      onClick={onClick}
      isSelected={isSelected}
      className={`${isSuperseded ? 'opacity-60' : ''} ${className}`}
    >
      {/* Metadata row */}
      <div className="flex items-center gap-2 text-xs text-gray-400">
        <span className="font-mono">v{version}</span>
        <span className="text-gray-600">·</span>
        <span>{formatAge(ageDays)}</span>
        <span className="text-gray-600">·</span>
        <ConfidenceMeter value={confidence} />
      </div>

      {/* Tags */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {tags.slice(0, 3).map((tag) => (
            <span key={tag} className="px-1.5 py-0.5 bg-gray-700 rounded text-xs text-gray-300">
              {tag}
            </span>
          ))}
          {tags.length > 3 && (
            <span className="px-1.5 py-0.5 text-xs text-gray-500">+{tags.length - 3}</span>
          )}
        </div>
      )}

      {/* Status indicator for superseded entries */}
      {isSuperseded && (
        <div className="mt-2 text-xs text-yellow-500/70 italic">Superseded by newer version</div>
      )}

      {/* Action buttons */}
      {(onShowHistory || onEvolve) && (
        <div className="flex gap-3 mt-3 pt-2 border-t border-gray-700/50">
          {onShowHistory && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onShowHistory();
              }}
              className="text-xs text-gray-400 hover:text-white transition-colors"
            >
              History
            </button>
          )}
          {onEvolve && !isSuperseded && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEvolve();
              }}
              className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
            >
              Evolve
            </button>
          )}
        </div>
      )}
    </ElasticCard>
  );

  // Wrap high confidence cards in breathing animation
  return isHighConfidence && !isSuperseded ? (
    <Breathe intensity={0.15} speed="slow">
      {card}
    </Breathe>
  ) : (
    card
  );
}

// =============================================================================
// Exports
// =============================================================================

export default TerraceCard;
