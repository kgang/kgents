/**
 * SpecPlantCard: A spec rendered as a plant in the garden.
 *
 * Visual properties derived from evidence:
 * - Height: Taller = more evidence
 * - Health: blooming → seedling based on confidence
 * - Pulse: Heartbeat tied to confidence
 *
 * Living Earth Palette from constants/livingEarth.ts
 *
 * @see spec/protocols/witness-assurance-surface.md
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import type { SpecPlant, PlantHealth } from '@/api/witness';
import { EvidenceLadder } from './EvidenceLadder';
import { PulseDot } from './ConfidencePulse';

// =============================================================================
// Constants
// =============================================================================

const HEALTH_COLORS: Record<PlantHealth, { stem: string; leaf: string; glow: string }> = {
  blooming: { stem: '#10B981', leaf: '#34D399', glow: '#6EE7B7' }, // Green - thriving
  healthy: { stem: '#84CC16', leaf: '#A3E635', glow: '#BEF264' }, // Lime - healthy
  wilting: { stem: '#F59E0B', leaf: '#FBBF24', glow: '#FCD34D' }, // Amber - stressed
  dead: { stem: '#6B7280', leaf: '#9CA3AF', glow: '#D1D5DB' }, // Gray - dead
  seedling: { stem: '#8B5CF6', leaf: '#A78BFA', glow: '#C4B5FD' }, // Purple - new
};

const HEALTH_LABELS: Record<PlantHealth, string> = {
  blooming: '🌻', // Sunflower
  healthy: '🌱', // Seedling
  wilting: '🍂', // Fallen leaf
  dead: '🍃', // Leaf fluttering
  seedling: '🌱', // Seedling
};

// =============================================================================
// Types
// =============================================================================

export interface SpecPlantCardProps {
  /** The spec plant data */
  plant: SpecPlant;
  /** Whether the card is selected */
  isSelected?: boolean;
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

export function SpecPlantCard({
  plant,
  isSelected = false,
  onClick,
  density = 'comfortable',
  className = '',
}: SpecPlantCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [showLadder, setShowLadder] = useState(false);

  const colors = HEALTH_COLORS[plant.health];
  const healthEmoji = HEALTH_LABELS[plant.health];

  // Height determines card prominence
  const heightMultiplier = 1 + (plant.height / 10) * 0.3; // 1.0 to 1.3

  // Breathing animation for healthy plants
  const breatheVariants = {
    idle: { scale: 1 },
    hover: {
      scale: 1.02 * heightMultiplier,
      transition: { duration: 0.3, ease: 'easeOut' as const },
    },
  };

  // Compact mode: minimal display
  if (density === 'compact') {
    return (
      <motion.div
        className={`flex items-center gap-2 px-2 py-1 rounded cursor-pointer ${className}`}
        style={{
          backgroundColor: isSelected ? `${colors.stem}20` : 'transparent',
          borderLeft: `3px solid ${colors.stem}`,
        }}
        onClick={onClick}
        whileHover={{ backgroundColor: `${colors.stem}10` }}
      >
        <PulseDot confidence={plant.confidence} size={6} />
        <span className="text-sm truncate flex-1 text-gray-200">{plant.name}</span>
        <span className="text-xs text-gray-500">{healthEmoji}</span>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={`rounded-lg border cursor-pointer select-none overflow-hidden ${className}`}
      style={{
        backgroundColor: '#1C1C1E',
        borderColor: isSelected ? colors.stem : isHovered ? colors.leaf : '#2C2C2E',
        minHeight: density === 'spacious' ? 160 : 120,
      }}
      variants={breatheVariants}
      initial="idle"
      animate={isHovered ? 'hover' : 'idle'}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      role="article"
      aria-label={`Spec: ${plant.name}`}
    >
      {/* Header */}
      <div
        className="px-3 py-2 flex items-center justify-between"
        style={{ backgroundColor: `${colors.stem}15` }}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{healthEmoji}</span>
          <PulseDot confidence={plant.confidence} />
        </div>
        <span
          className="text-xs font-mono px-2 py-0.5 rounded"
          style={{ backgroundColor: `${colors.stem}30`, color: colors.leaf }}
        >
          {(plant.confidence * 100).toFixed(0)}%
        </span>
      </div>

      {/* Content */}
      <div className="px-3 py-2">
        {/* Name */}
        <h3 className="text-sm font-medium text-gray-100 mb-1 line-clamp-2">{plant.name}</h3>

        {/* Path */}
        <p className="text-xs text-gray-500 truncate mb-2" title={plant.path}>
          {plant.path}
        </p>

        {/* Status badge */}
        <div className="flex items-center gap-2 mb-2">
          <span
            className="text-xs px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: `${colors.stem}20`,
              color: colors.leaf,
              border: `1px solid ${colors.stem}40`,
            }}
          >
            {plant.status.replace('_', ' ')}
          </span>
          {plant.mark_count > 0 && (
            <span className="text-xs text-gray-500">
              {plant.mark_count} mark{plant.mark_count !== 1 ? 's' : ''}
            </span>
          )}
          {plant.test_count > 0 && (
            <span className="text-xs text-gray-500">
              {plant.test_count} test{plant.test_count !== 1 ? 's' : ''}
            </span>
          )}
        </div>

        {/* Evidence ladder (toggle) */}
        {density === 'spacious' && (
          <>
            <button
              className="text-xs text-gray-500 hover:text-gray-300 mb-2"
              onClick={(e) => {
                e.stopPropagation();
                setShowLadder(!showLadder);
              }}
            >
              {showLadder ? 'Hide ladder' : 'Show evidence ladder'}
            </button>

            {showLadder && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-2"
              >
                <EvidenceLadder ladder={plant.evidence_levels} mode="compact" />
              </motion.div>
            )}
          </>
        )}
      </div>

      {/* Height indicator (bottom bar) */}
      <div
        className="h-1"
        style={{
          backgroundColor: colors.stem,
          width: `${Math.min(100, plant.height * 10)}%`,
          opacity: 0.6,
        }}
      />
    </motion.div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default SpecPlantCard;
