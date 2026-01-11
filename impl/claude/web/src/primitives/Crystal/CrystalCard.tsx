/**
 * CrystalCard — Single Crystal Display
 *
 * Displays a crystallized insight with:
 * - Level badge
 * - Insight (main content)
 * - Significance
 * - Confidence indicator
 * - Mood visualization
 * - Source count
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow
 */

import { memo, useState } from 'react';
import type { Crystal } from '../../types/crystal';
import { MoodIndicator } from './MoodIndicator';
import './CrystalCard.css';

// =============================================================================
// Types
// =============================================================================

interface CrystalCardProps {
  crystal: Crystal;
  onExpand?: (crystal: Crystal) => void;
  expandable?: boolean;
}

// =============================================================================
// Helpers
// =============================================================================

function getLevelColor(level: string): string {
  switch (level) {
    case 'SESSION':
      return 'var(--color-steel-300)';
    case 'DAY':
      return 'var(--color-life-sage)';
    case 'WEEK':
      return 'var(--color-glow-lichen)';
    case 'EPOCH':
      return 'var(--color-glow-amber)';
    default:
      return 'var(--text-muted)';
  }
}

function formatDate(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = diff / (1000 * 60 * 60);
  const days = diff / (1000 * 60 * 60 * 24);

  if (hours < 1) {
    return `${Math.floor(diff / (1000 * 60))}m ago`;
  } else if (hours < 24) {
    return `${Math.floor(hours)}h ago`;
  } else if (days < 7) {
    return `${Math.floor(days)}d ago`;
  }
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// =============================================================================
// Component
// =============================================================================

export const CrystalCard = memo(function CrystalCard({
  crystal,
  onExpand,
  expandable = true,
}: CrystalCardProps) {
  const [expanded, setExpanded] = useState(false);

  const handleToggleExpand = () => {
    if (!expandable) return;
    const newExpanded = !expanded;
    setExpanded(newExpanded);
    if (newExpanded && onExpand) {
      onExpand(crystal);
    }
  };

  const sourceCount = crystal.sourceMarkIds.length || crystal.sourceCrystalIds.length;
  const levelColor = getLevelColor(crystal.level);

  return (
    <div
      className={`crystal-card ${expanded ? 'crystal-card--expanded' : ''} ${
        expandable ? 'crystal-card--expandable' : ''
      }`}
      onClick={expandable ? handleToggleExpand : undefined}
    >
      {/* Header */}
      <div className="crystal-card__header">
        <span className="crystal-card__level-badge" style={{ color: levelColor }}>
          {crystal.level}
        </span>
        <span className="crystal-card__timestamp">{formatDate(crystal.crystallizedAt)}</span>
        <div className="crystal-card__confidence-ring">
          <svg width="20" height="20" viewBox="0 0 20 20">
            <circle
              cx="10"
              cy="10"
              r="8"
              fill="none"
              stroke="var(--color-steel-600)"
              strokeWidth="2"
            />
            <circle
              cx="10"
              cy="10"
              r="8"
              fill="none"
              stroke="var(--color-glow-spore)"
              strokeWidth="2"
              strokeDasharray={`${crystal.confidence * 50.26} 50.26`}
              strokeLinecap="round"
              transform="rotate(-90 10 10)"
            />
          </svg>
        </div>
      </div>

      {/* Insight (main content) */}
      <div className="crystal-card__insight">{crystal.insight}</div>

      {/* Significance */}
      {crystal.significance && (
        <div className="crystal-card__significance">{crystal.significance}</div>
      )}

      {/* Footer: Mood + Source count */}
      <div className="crystal-card__footer">
        <MoodIndicator mood={crystal.mood} size="small" variant="dots" />
        <span className="crystal-card__source-count">{sourceCount} sources</span>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="crystal-card__details">
          {/* Principles */}
          {crystal.principles.length > 0 && (
            <div className="crystal-card__principles">
              <span className="crystal-card__detail-label">Principles:</span>
              <div className="crystal-card__principle-tags">
                {crystal.principles.map((p) => (
                  <span key={p} className="crystal-card__principle-tag">
                    {p}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Topics */}
          {crystal.topics.length > 0 && (
            <div className="crystal-card__topics">
              <span className="crystal-card__detail-label">Topics:</span>
              <div className="crystal-card__topic-tags">
                {crystal.topics.map((t) => (
                  <span key={t} className="crystal-card__topic-tag">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Metrics */}
          <div className="crystal-card__metrics">
            <div className="crystal-card__metric">
              <span className="crystal-card__metric-label">Confidence:</span>
              <span className="crystal-card__metric-value">
                {(crystal.confidence * 100).toFixed(0)}%
              </span>
            </div>
            {crystal.compressionRatio && (
              <div className="crystal-card__metric">
                <span className="crystal-card__metric-label">Compression:</span>
                <span className="crystal-card__metric-value">
                  {crystal.compressionRatio.toFixed(1)}:1
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
});
