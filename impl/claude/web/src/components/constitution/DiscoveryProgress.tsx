/**
 * DiscoveryProgress - Analysis progress indicator for axiom discovery.
 *
 * Shows the pipeline stages with warmth:
 * - "Surfacing your decisions..."
 * - "Finding recurring patterns..."
 * - "Computing stability..."
 * - "Detecting contradictions..."
 *
 * Philosophy:
 *   "I noticed some patterns worth keeping."
 *   Discovery should feel like self-reflection, not data mining.
 *
 * @see stores/personalConstitutionStore.ts
 */

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import type { DiscoveryProgress as DiscoveryProgressType } from './types';
import { GLOW, GREEN, EARTH } from '@/constants';
import './DiscoveryProgress.css';

// =============================================================================
// Types
// =============================================================================

export interface DiscoveryProgressProps {
  /** Current progress state */
  progress: DiscoveryProgressType | null;

  /** Whether discovery is in progress */
  isDiscovering: boolean;

  /** Error message if discovery failed */
  error?: string | null;

  /** Callback to retry discovery */
  onRetry?: () => void;

  /** Custom className */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const STAGE_MESSAGES: Record<DiscoveryProgressType['stage'], string> = {
  surfacing: 'Surfacing your decisions...',
  extracting: 'Finding recurring patterns...',
  computing: 'Computing stability of each pattern...',
  detecting: 'Detecting potential contradictions...',
  complete: 'Discovery complete',
};

const STAGE_ORDER: DiscoveryProgressType['stage'][] = [
  'surfacing',
  'extracting',
  'computing',
  'detecting',
  'complete',
];

// =============================================================================
// Sub-components
// =============================================================================

interface StageIndicatorProps {
  currentStage: DiscoveryProgressType['stage'];
  index: number;
}

function StageIndicator({ currentStage, index }: StageIndicatorProps) {
  const currentIndex = STAGE_ORDER.indexOf(currentStage);
  const isComplete = index < currentIndex;
  const isCurrent = index === currentIndex;

  return (
    <div
      className={`stage-indicator ${isComplete ? 'complete' : ''} ${isCurrent ? 'current' : ''}`}
    >
      <motion.div
        className="stage-dot"
        animate={{
          scale: isCurrent ? [1, 1.2, 1] : 1,
          backgroundColor: isComplete ? GREEN.mint : isCurrent ? GLOW.amber : `${EARTH.clay}60`,
        }}
        transition={
          isCurrent ? { repeat: Infinity, duration: 1.5, ease: 'easeInOut' } : { duration: 0.3 }
        }
      />
      {index < STAGE_ORDER.length - 1 && (
        <div
          className="stage-connector"
          style={{
            backgroundColor: isComplete ? GREEN.mint : `${EARTH.clay}40`,
          }}
        />
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function DiscoveryProgress({
  progress,
  isDiscovering,
  error,
  onRetry,
  className = '',
}: DiscoveryProgressProps) {
  const stage = progress?.stage ?? 'surfacing';
  const percent = progress?.percent ?? 0;

  // Warm message based on stage
  const message = useMemo(() => {
    if (error) return 'Something went wrong during discovery.';
    if (!isDiscovering && !progress) return 'Ready to discover your axioms.';
    return progress?.message ?? STAGE_MESSAGES[stage];
  }, [error, isDiscovering, progress, stage]);

  // Stats display
  const stats = useMemo(() => {
    if (!progress) return null;
    return {
      decisions: progress.decisionsAnalyzed,
      patterns: progress.patternsFound,
    };
  }, [progress]);

  if (!isDiscovering && !progress && !error) {
    return null;
  }

  return (
    <div className={`discovery-progress ${error ? 'has-error' : ''} ${className}`}>
      {/* Stage Timeline */}
      {!error && (
        <div className="stage-timeline">
          {STAGE_ORDER.slice(0, -1).map((s, i) => (
            <StageIndicator key={s} currentStage={stage} index={i} />
          ))}
        </div>
      )}

      {/* Progress Bar */}
      <div className="progress-bar-container">
        <motion.div
          className="progress-bar-fill"
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
          style={{
            backgroundColor: error ? GLOW.copper : GREEN.sage,
          }}
        />
      </div>

      {/* Message */}
      <motion.p
        className="progress-message"
        key={message}
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {message}
      </motion.p>

      {/* Stats */}
      {stats && !error && (
        <div className="progress-stats">
          <span className="stat">
            <span className="stat-value">{stats.decisions}</span>
            <span className="stat-label">decisions analyzed</span>
          </span>
          {stats.patterns > 0 && (
            <span className="stat">
              <span className="stat-value">{stats.patterns}</span>
              <span className="stat-label">patterns found</span>
            </span>
          )}
        </div>
      )}

      {/* Error Actions */}
      {error && onRetry && (
        <div className="error-actions">
          <p className="error-detail">{error}</p>
          <button className="retry-btn" onClick={onRetry}>
            Try Again
          </button>
        </div>
      )}

      {/* Loading Spinner (for indeterminate states) */}
      {isDiscovering && percent === 0 && (
        <motion.div
          className="loading-spinner"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke={`${EARTH.clay}40`} strokeWidth="2" />
            <path
              d="M12 2a10 10 0 0 1 10 10"
              stroke={GLOW.amber}
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        </motion.div>
      )}
    </div>
  );
}

export default DiscoveryProgress;
