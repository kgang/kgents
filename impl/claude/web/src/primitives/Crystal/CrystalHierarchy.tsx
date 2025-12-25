/**
 * CrystalHierarchy — Crystal Tree Visualization
 *
 * Displays crystals in hierarchical levels:
 * SESSION → DAY → WEEK → EPOCH
 *
 * Features:
 * - Collapsible levels
 * - Click to expand/drill down
 * - Timeline or tree view
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow
 */

import { memo, useState } from 'react';
import type { Crystal, CrystalLevel } from '../../types/crystal';
import { CrystalCard } from './CrystalCard';
import './CrystalHierarchy.css';

// =============================================================================
// Types
// =============================================================================

interface CrystalHierarchyProps {
  crystals: Crystal[];
  onCrystalSelect?: (crystal: Crystal) => void;
  initialCollapsed?: CrystalLevel[];
  variant?: 'timeline' | 'tree';
}

// =============================================================================
// Helpers
// =============================================================================

const LEVEL_ORDER: CrystalLevel[] = ['SESSION', 'DAY', 'WEEK', 'EPOCH'];

function groupCrystalsByLevel(crystals: Crystal[]): Record<CrystalLevel, Crystal[]> {
  const grouped: Record<CrystalLevel, Crystal[]> = {
    SESSION: [],
    DAY: [],
    WEEK: [],
    EPOCH: [],
  };

  crystals.forEach((crystal) => {
    grouped[crystal.level].push(crystal);
  });

  // Sort each level by timestamp (newest first)
  Object.values(grouped).forEach((levelCrystals) => {
    levelCrystals.sort(
      (a, b) => new Date(b.crystallizedAt).getTime() - new Date(a.crystallizedAt).getTime()
    );
  });

  return grouped;
}

// =============================================================================
// Component
// =============================================================================

export const CrystalHierarchy = memo(function CrystalHierarchy({
  crystals,
  onCrystalSelect,
  initialCollapsed = [],
  variant = 'timeline',
}: CrystalHierarchyProps) {
  const [collapsed, setCollapsed] = useState<Set<CrystalLevel>>(
    new Set(initialCollapsed)
  );

  const grouped = groupCrystalsByLevel(crystals);

  const toggleLevel = (level: CrystalLevel) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(level)) {
        next.delete(level);
      } else {
        next.add(level);
      }
      return next;
    });
  };

  const handleCrystalExpand = (crystal: Crystal) => {
    if (onCrystalSelect) {
      onCrystalSelect(crystal);
    }
  };

  return (
    <div className={`crystal-hierarchy crystal-hierarchy--${variant}`}>
      {LEVEL_ORDER.map((level) => {
        const levelCrystals = grouped[level];
        const isCollapsed = collapsed.has(level);
        const isEmpty = levelCrystals.length === 0;

        return (
          <div key={level} className="crystal-hierarchy__level">
            {/* Level Header */}
            <div
              className={`crystal-hierarchy__level-header ${
                isEmpty ? 'crystal-hierarchy__level-header--empty' : ''
              }`}
              onClick={() => !isEmpty && toggleLevel(level)}
            >
              <span className="crystal-hierarchy__level-name">{level}</span>
              <span className="crystal-hierarchy__level-count">
                {levelCrystals.length}
              </span>
              {!isEmpty && (
                <span className="crystal-hierarchy__level-toggle">
                  {isCollapsed ? '▶' : '▼'}
                </span>
              )}
            </div>

            {/* Level Content */}
            {!isEmpty && !isCollapsed && (
              <div className="crystal-hierarchy__level-content">
                {levelCrystals.map((crystal) => (
                  <CrystalCard
                    key={crystal.id}
                    crystal={crystal}
                    onExpand={handleCrystalExpand}
                    expandable={true}
                  />
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* Empty state */}
      {crystals.length === 0 && (
        <div className="crystal-hierarchy__empty">
          <p>No crystals yet.</p>
          <p className="crystal-hierarchy__empty-hint">
            Use <code>:crystallize</code> to create your first crystal.
          </p>
        </div>
      )}
    </div>
  );
});
