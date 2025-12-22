/**
 * OrphanWeedCard: An artifact without prompt lineage.
 *
 * From spec:
 *   "Orphans are weeds to tend, not shame to conceal."
 *   "Orphan Visibility Law: Orphans are ALWAYS visible."
 *
 * Orphans render at garden edges, always visible, styled as "weeds to tend."
 *
 * @see spec/protocols/witness-assurance-surface.md
 */

import { motion } from 'framer-motion';
import type { OrphanWeed } from '@/api/witness';

// =============================================================================
// Constants
// =============================================================================

const WEED_COLORS = {
  stem: '#DC2626', // Red
  leaf: '#F87171', // Light red
  glow: '#FCA5A5', // Very light red
};

// =============================================================================
// Types
// =============================================================================

export interface OrphanWeedCardProps {
  /** The orphan weed data */
  orphan: OrphanWeed;
  /** Click handler */
  onClick?: () => void;
  /** Display density */
  density?: 'compact' | 'comfortable' | 'spacious';
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Main Component
// =============================================================================

export function OrphanWeedCard({
  orphan,
  onClick,
  density = 'comfortable',
  className = '',
}: OrphanWeedCardProps) {
  const createdAt = new Date(orphan.created_at);
  const timeStr = createdAt.toLocaleDateString([], {
    month: 'short',
    day: 'numeric',
  });

  // Compact mode
  if (density === 'compact') {
    return (
      <motion.div
        className={`flex items-center gap-2 px-2 py-1 rounded cursor-pointer ${className}`}
        style={{
          backgroundColor: `${WEED_COLORS.stem}10`,
          borderLeft: `3px solid ${WEED_COLORS.stem}`,
        }}
        onClick={onClick}
        whileHover={{ backgroundColor: `${WEED_COLORS.stem}20` }}
      >
        <span className="text-red-400">🌿</span> {/* Herb emoji (weed) */}
        <span className="text-sm truncate flex-1 text-red-300">{orphan.path}</span>
        <span className="text-xs text-red-500">{orphan.artifact_type}</span>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={`rounded-lg border cursor-pointer select-none overflow-hidden ${className}`}
      style={{
        backgroundColor: '#1C1C1E',
        borderColor: `${WEED_COLORS.stem}50`,
      }}
      whileHover={{ borderColor: WEED_COLORS.stem }}
      onClick={onClick}
      role="article"
      aria-label={`Orphan: ${orphan.path}`}
    >
      {/* Header with warning style */}
      <div
        className="px-3 py-2 flex items-center justify-between"
        style={{ backgroundColor: `${WEED_COLORS.stem}15` }}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">🌿</span> {/* Herb emoji */}
          <span className="text-xs text-red-400 font-medium">Orphan</span>
        </div>
        <span className="text-xs text-red-500">{timeStr}</span>
      </div>

      {/* Content */}
      <div className="px-3 py-2">
        {/* Path */}
        <p className="text-sm text-red-300 truncate mb-1" title={orphan.path}>
          {orphan.path}
        </p>

        {/* Type badge */}
        <div className="flex items-center gap-2 mb-2">
          <span
            className="text-xs px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: `${WEED_COLORS.stem}20`,
              color: WEED_COLORS.leaf,
              border: `1px solid ${WEED_COLORS.stem}40`,
            }}
          >
            {orphan.artifact_type}
          </span>
        </div>

        {/* Suggested prompt */}
        {orphan.suggested_prompt && density === 'spacious' && (
          <div className="mt-2 p-2 rounded bg-steel-carbon">
            <p className="text-xs text-steel-zinc mb-1">Suggested prompt:</p>
            <p className="text-sm text-steel-zinc italic">
              &ldquo;{orphan.suggested_prompt}&rdquo;
            </p>
          </div>
        )}

        {/* Action hint */}
        <p className="text-xs text-steel-zinc mt-2">🌱 Click to tend this weed (add lineage)</p>
      </div>
    </motion.div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default OrphanWeedCard;
