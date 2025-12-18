/**
 * HealthBadge - Grade indicator with progress bar and breathing animation.
 *
 * Living Earth aesthetic: Healthy nodes breathe subtly, conveying vitality.
 * Violations show amber warning indicators.
 *
 * @see creative/crown-jewels-genesis-moodboard.md - Animation Philosophy
 */

import { memo } from 'react';
import { Breathe } from '@/components/joy';
import { HEALTH_GRADE_CONFIG } from '@/api/types';
import type { HealthBadgeProps } from './types';

// =============================================================================
// Component
// =============================================================================

/**
 * HealthBadge displays health grade with mini progress bar.
 * Breathes when healthy (A/A+, no violations).
 */
export const HealthBadge = memo(function HealthBadge({
  grade,
  score,
  hasViolation,
  breathing = false,
  compact = false,
}: HealthBadgeProps) {
  const config = HEALTH_GRADE_CONFIG[grade] || {
    color: '#6b7280',
    bgColor: 'bg-gray-500/20',
  };

  const isHealthy = (grade === 'A+' || grade === 'A') && !hasViolation;
  const shouldBreathe = breathing && isHealthy;

  const badge = (
    <div className="flex items-center gap-1">
      {/* Grade letter */}
      <span
        className={`font-bold ${compact ? 'text-[10px]' : 'text-xs'}`}
        style={{ color: config.color }}
      >
        {grade}
      </span>

      {/* Mini progress bar */}
      {!compact && (
        <div className="w-8 h-1 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-300"
            style={{
              width: `${Math.max(score * 100, 5)}%`,
              backgroundColor: config.color,
            }}
          />
        </div>
      )}

      {/* Compact: just show score percentage */}
      {compact && <span className="text-[9px] text-gray-500">{Math.round(score * 100)}%</span>}
    </div>
  );

  // Wrap with Breathe for healthy nodes
  if (shouldBreathe) {
    return (
      <Breathe intensity={0.2} speed="slow">
        {badge}
      </Breathe>
    );
  }

  return badge;
});

// =============================================================================
// Variants
// =============================================================================

/**
 * Large health badge for headers/summaries.
 */
export const HealthBadgeLarge = memo(function HealthBadgeLarge({
  grade,
  score,
  hasViolation,
}: Omit<HealthBadgeProps, 'compact' | 'breathing'>) {
  const config = HEALTH_GRADE_CONFIG[grade] || {
    color: '#6b7280',
    bgColor: 'bg-gray-500/20',
  };

  const isHealthy = (grade === 'A+' || grade === 'A') && !hasViolation;

  const badge = (
    <div className="flex items-center gap-2">
      <span className="text-2xl font-bold" style={{ color: config.color }}>
        {grade}
      </span>
      <div className="flex flex-col">
        <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-300"
            style={{
              width: `${Math.max(score * 100, 5)}%`,
              backgroundColor: config.color,
            }}
          />
        </div>
        <span className="text-[10px] text-gray-500 mt-0.5">{Math.round(score * 100)}% health</span>
      </div>
    </div>
  );

  if (isHealthy) {
    return (
      <Breathe intensity={0.3} speed="slow">
        {badge}
      </Breathe>
    );
  }

  return badge;
});

export default HealthBadge;
