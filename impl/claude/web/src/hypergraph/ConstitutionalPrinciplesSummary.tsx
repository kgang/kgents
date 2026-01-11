/**
 * Constitutional Principles Summary Panel
 *
 * Displays the 7 constitutional principles with K-Block counts,
 * enabling navigation and filtering by principle grounding.
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import { memo, useState, useCallback } from 'react';
import './ConstitutionalPrinciplesSummary.css';

// LIVING_EARTH palette colors for each principle
export const PRINCIPLE_COLORS = {
  TASTEFUL: '#8ba98b', // sage
  CURATED: '#c4a77d', // honey
  ETHICAL: '#4a6b4a', // forest
  JOY_INDUCING: '#d4b88c', // sand
  COMPOSABLE: '#6b8b6b', // mint
  HETERARCHICAL: '#8bab8b', // sage light
  GENERATIVE: '#e5c99d', // lantern
} as const;

export type ConstitutionalPrincipleId = keyof typeof PRINCIPLE_COLORS;

export interface ConstitutionalPrinciple {
  id: string;
  name: string;
  kblockCount: number;
  color: string;
}

export interface ConstitutionalPrinciplesSummaryProps {
  principles: ConstitutionalPrinciple[];
  totalGrounded: number;
  totalOrphan: number;
  selectedPrincipleId?: string;
  onPrincipleClick?: (principleId: string) => void;
  onViewOrphans?: () => void;
  className?: string;
}

export const ConstitutionalPrinciplesSummary = memo(function ConstitutionalPrinciplesSummary({
  principles,
  totalGrounded,
  totalOrphan,
  selectedPrincipleId,
  onPrincipleClick,
  onViewOrphans,
  className = '',
}: ConstitutionalPrinciplesSummaryProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleToggleCollapse = useCallback(() => {
    setIsCollapsed((prev) => !prev);
  }, []);

  const handlePrincipleClick = useCallback(
    (principleId: string) => {
      onPrincipleClick?.(principleId);
    },
    [onPrincipleClick]
  );

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent, principleId: string) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        handlePrincipleClick(principleId);
      }
    },
    [handlePrincipleClick]
  );

  const handleOrphansKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        onViewOrphans?.();
      }
    },
    [onViewOrphans]
  );

  const totalKBlocks = totalGrounded + totalOrphan;
  const groundedPercentage =
    totalKBlocks > 0 ? Math.round((totalGrounded / totalKBlocks) * 100) : 0;

  return (
    <div
      className={`constitutional-summary ${isCollapsed ? 'constitutional-summary--collapsed' : ''} ${className}`}
      role="region"
      aria-label="Constitutional Principles"
    >
      {/* Header */}
      <div className="constitutional-summary__header">
        <button
          className="constitutional-summary__toggle"
          onClick={handleToggleCollapse}
          aria-expanded={!isCollapsed}
          aria-label={isCollapsed ? 'Expand principles' : 'Collapse principles'}
        >
          <span className="constitutional-summary__chevron">{isCollapsed ? '▸' : '▾'}</span>
        </button>
        <span className="constitutional-summary__title">CONSTITUTIONAL PRINCIPLES</span>
        <span className="constitutional-summary__count">{totalGrounded}</span>
      </div>

      {/* Content (collapsible) */}
      {!isCollapsed && (
        <>
          {/* Principles List */}
          <div className="constitutional-summary__list">
            {principles.map((principle) => (
              <div
                key={principle.id}
                className={`constitutional-summary__principle ${
                  selectedPrincipleId === principle.id
                    ? 'constitutional-summary__principle--selected'
                    : ''
                }`}
                style={{ '--principle-color': principle.color } as React.CSSProperties}
                onClick={() => handlePrincipleClick(principle.id)}
                onKeyDown={(e) => handleKeyDown(e, principle.id)}
                tabIndex={0}
                role="button"
                aria-pressed={selectedPrincipleId === principle.id}
              >
                <span className="constitutional-summary__icon">◈</span>
                <span className="constitutional-summary__name">{principle.name}</span>
                <span className="constitutional-summary__badge">{principle.kblockCount}</span>
              </div>
            ))}
          </div>

          {/* Footer with totals */}
          <div className="constitutional-summary__footer">
            <div className="constitutional-summary__stats">
              <span className="constitutional-summary__stat constitutional-summary__stat--grounded">
                <span className="constitutional-summary__stat-label">Grounded</span>
                <span className="constitutional-summary__stat-value">{totalGrounded}</span>
              </span>
              <span className="constitutional-summary__stat-separator">|</span>
              <span
                className={`constitutional-summary__stat constitutional-summary__stat--orphan ${
                  totalOrphan > 0 ? 'constitutional-summary__stat--clickable' : ''
                }`}
                onClick={totalOrphan > 0 ? onViewOrphans : undefined}
                onKeyDown={totalOrphan > 0 ? handleOrphansKeyDown : undefined}
                tabIndex={totalOrphan > 0 ? 0 : undefined}
                role={totalOrphan > 0 ? 'button' : undefined}
                aria-label={totalOrphan > 0 ? `View ${totalOrphan} orphan K-Blocks` : undefined}
              >
                <span className="constitutional-summary__stat-label">Orphan</span>
                <span className="constitutional-summary__stat-value">{totalOrphan}</span>
              </span>
            </div>
            <div className="constitutional-summary__progress">
              <div
                className="constitutional-summary__progress-bar"
                style={{ width: `${groundedPercentage}%` }}
                aria-valuenow={groundedPercentage}
                aria-valuemin={0}
                aria-valuemax={100}
                role="progressbar"
                aria-label={`${groundedPercentage}% grounded`}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
});

export type { ConstitutionalPrinciplesSummaryProps as ConstitutionalSummaryProps };
