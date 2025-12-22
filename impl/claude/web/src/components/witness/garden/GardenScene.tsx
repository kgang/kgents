/**
 * GardenScene: The complete Witness Assurance Surface visualization.
 *
 * This is the main container that renders:
 * - SpecPlant cards for each spec file
 * - OrphanWeed cards for artifacts without lineage
 * - Lens switcher (Audit/Author/Trust)
 * - Overall health indicator
 *
 * From spec: "The UI IS the trust surface. Every pixel grows or wilts."
 *
 * @see spec/protocols/witness-assurance-surface.md
 */

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { GardenScene as GardenSceneType, AccountabilityLens, SpecPlant } from '@/api/witness';
import { SpecPlantCard } from './SpecPlantCard';
import { OrphanWeedCard } from './OrphanWeedCard';
import { ConfidencePulse } from './ConfidencePulse';

// =============================================================================
// Constants
// =============================================================================

const LENS_CONFIG: Record<AccountabilityLens, { label: string; icon: string; key: string }> = {
  audit: { label: 'Audit', icon: '🔍', key: 'A' }, // Magnifying glass
  author: { label: 'Author', icon: '📝', key: 'U' }, // Memo
  trust: { label: 'Trust', icon: '💚', key: 'T' }, // Green heart
};

// =============================================================================
// Types
// =============================================================================

export interface GardenSceneProps {
  /** The garden scene data */
  scene: GardenSceneType;
  /** Current lens */
  lens: AccountabilityLens;
  /** Callback when lens changes */
  onLensChange?: (lens: AccountabilityLens) => void;
  /** Callback when a plant is selected */
  onPlantSelect?: (plant: SpecPlant) => void;
  /** Currently selected plant path */
  selectedPlantPath?: string;
  /** Display density */
  density?: 'compact' | 'comfortable' | 'spacious';
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Sub-components
// =============================================================================

interface LensSwitcherProps {
  currentLens: AccountabilityLens;
  onChange: (lens: AccountabilityLens) => void;
}

function LensSwitcher({ currentLens, onChange }: LensSwitcherProps) {
  return (
    <div className="flex items-center gap-1 p-1 rounded-lg bg-gray-800">
      {(['audit', 'author', 'trust'] as AccountabilityLens[]).map((lens) => {
        const config = LENS_CONFIG[lens];
        const isActive = lens === currentLens;

        return (
          <button
            key={lens}
            className={`
              flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm
              transition-all duration-200
              ${isActive ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-gray-200'}
            `}
            onClick={() => onChange(lens)}
            title={`${config.label} (${config.key})`}
          >
            <span>{config.icon}</span>
            <span className="hidden sm:inline">{config.label}</span>
          </button>
        );
      })}
    </div>
  );
}

interface HealthHeaderProps {
  scene: GardenSceneType;
}

function HealthHeader({ scene }: HealthHeaderProps) {
  const healthPercent = Math.round(scene.overall_health * 100);
  const healthColor =
    healthPercent >= 80
      ? '#10B981' // Green
      : healthPercent >= 50
        ? '#F59E0B' // Amber
        : '#EF4444'; // Red

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <ConfidencePulse
          pulse={{
            confidence: scene.overall_health,
            previous_confidence: null,
            pulse_rate:
              scene.overall_health < 0.3
                ? 0
                : scene.overall_health < 0.6
                  ? 0.5
                  : scene.overall_health < 0.9
                    ? 1.0
                    : 1.5,
            delta_direction: 'stable',
          }}
          size="md"
        />
        <div>
          <h2 className="text-lg font-semibold text-white">Witness Garden</h2>
          <p className="text-xs text-gray-400">
            {scene.total_specs} specs | {scene.witnessed_count} witnessed | {scene.orphan_count}{' '}
            orphans
          </p>
        </div>
      </div>

      <div className="text-right">
        <p className="text-2xl font-bold" style={{ color: healthColor }}>
          {healthPercent}%
        </p>
        <p className="text-xs text-gray-500">Overall Health</p>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function GardenScene({
  scene,
  lens,
  onLensChange,
  onPlantSelect,
  selectedPlantPath,
  density = 'comfortable',
  className = '',
}: GardenSceneProps) {
  const [sortBy, setSortBy] = useState<'name' | 'confidence' | 'recent'>('confidence');

  // Sort plants based on current sort mode
  const sortedPlants = useMemo(() => {
    const plants = [...scene.specs];

    switch (sortBy) {
      case 'name':
        return plants.sort((a, b) => a.name.localeCompare(b.name));
      case 'confidence':
        return plants.sort((a, b) => b.confidence - a.confidence);
      case 'recent':
        return plants.sort((a, b) => {
          const aTime = a.last_evidence_at ? new Date(a.last_evidence_at).getTime() : 0;
          const bTime = b.last_evidence_at ? new Date(b.last_evidence_at).getTime() : 0;
          return bTime - aTime;
        });
      default:
        return plants;
    }
  }, [scene.specs, sortBy]);

  // Grid configuration based on density
  const gridClass =
    density === 'compact'
      ? 'grid-cols-1'
      : density === 'comfortable'
        ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'
        : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4';

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-700 bg-gray-900">
        <HealthHeader scene={scene} />

        {/* Controls */}
        <div className="flex items-center justify-between mt-4">
          {onLensChange && <LensSwitcher currentLens={lens} onChange={onLensChange} />}

          {/* Sort options */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500">Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'name' | 'confidence' | 'recent')}
              className="text-xs bg-gray-800 text-gray-300 rounded px-2 py-1 border border-gray-700"
            >
              <option value="confidence">By confidence</option>
              <option value="name">By name</option>
              <option value="recent">By recent</option>
            </select>
          </div>
        </div>
      </div>

      {/* Garden content */}
      <div className="flex-1 overflow-auto p-4">
        {/* Spec plants grid */}
        <div className={`grid ${gridClass} gap-4`}>
          <AnimatePresence mode="popLayout">
            {sortedPlants.map((plant, index) => (
              <motion.div
                key={plant.path}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.02 }}
              >
                <SpecPlantCard
                  plant={plant}
                  isSelected={plant.path === selectedPlantPath}
                  onClick={() => onPlantSelect?.(plant)}
                  density={density}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Orphans section (always visible per spec) */}
        {scene.orphans.length > 0 && (
          <div className="mt-8">
            <h3 className="text-sm font-medium text-red-400 mb-3 flex items-center gap-2">
              <span>🌿</span> Weeds to Tend ({scene.orphans.length})
            </h3>
            <div className={`grid ${gridClass} gap-4`}>
              {scene.orphans.map((orphan, index) => (
                <motion.div
                  key={orphan.path}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.02 }}
                >
                  <OrphanWeedCard orphan={orphan} density={density} />
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Empty state */}
        {scene.specs.length === 0 && scene.orphans.length === 0 && (
          <div className="flex flex-col items-center justify-center h-64 text-steel-zinc">
            <span className="text-4xl mb-4">🌱</span>
            <p className="text-lg">No specs found</p>
            <p className="text-sm mt-2">Add spec files to spec/ to start growing your garden</p>
          </div>
        )}
      </div>

      {/* Footer with timestamp */}
      <div className="flex-shrink-0 px-4 py-2 border-t border-steel-carbon text-xs text-steel-zinc">
        Generated: {new Date(scene.generated_at).toLocaleString()}
      </div>
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default GardenScene;
