/**
 * TrailingSession - Graceful context ending component
 *
 * Displays crystallized session context with continuation affordances.
 * Implements spec §9.4b: Trailing Session Affordance
 *
 * @see spec/protocols/chat-web.md §9.4b
 */

import { motion, AnimatePresence } from 'framer-motion';
import { TIMING } from '@/constants';
import type { Turn, SessionCrystal } from './store';
import './TrailingSession.css';

// =============================================================================
// Types
// =============================================================================

export interface TrailingSessionProps {
  /** The crystallized session summary */
  crystal: SessionCrystal;

  /** Trailing turns (visible but not in context) */
  trailingTurns: Turn[];

  /** When the session was crystallized */
  crystallizedAt: string;

  /** Callback to re-activate session */
  onContinue?: () => void;

  /** Callback to start fresh session with crystal reference */
  onStartFresh?: () => void;

  /** Callback to view crystal in side panel */
  onViewCrystal?: () => void;

  /** Callback to dismiss trailing section */
  onDismiss?: () => void;

  /** Custom className */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * TrailingSession
 *
 * Shows crystallized session context below active conversation.
 * Users can continue, start fresh, or view the crystal summary.
 *
 * Philosophy: "Context ends gracefully, not abruptly."
 *
 * @example
 * ```tsx
 * <TrailingSession
 *   crystal={sessionCrystal}
 *   trailingTurns={oldTurns}
 *   crystallizedAt={crystallizedTimestamp}
 *   onContinue={handleContinue}
 *   onStartFresh={handleStartFresh}
 *   onViewCrystal={handleViewCrystal}
 * />
 * ```
 */
export function TrailingSession({
  crystal,
  trailingTurns,
  crystallizedAt,
  onContinue,
  onStartFresh,
  onViewCrystal,
  onDismiss,
  className = '',
}: TrailingSessionProps) {
  const timeAgo = getTimeAgo(crystallizedAt);

  return (
    <AnimatePresence>
      <motion.div
        className={`trailing-session ${className}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: TIMING.elaborate / 1000 }}
      >
        {/* Divider with context transition message */}
        <div className="trailing-divider">
          <div className="trailing-divider-line" />
          <span className="trailing-divider-text">
            Trailing (not in context) — crystallized {timeAgo}
          </span>
          <div className="trailing-divider-line" />
        </div>

        {/* Trailing turns (greyed out) */}
        <div className="trailing-turns">
          {trailingTurns.map((turn) => (
            <TrailingTurn key={turn.turn_number} turn={turn} />
          ))}
        </div>

        {/* Action buttons */}
        <div className="trailing-actions">
          <button
            className="trailing-action-button trailing-action-continue"
            onClick={onContinue}
            disabled={!onContinue}
          >
            <ContinueIcon />
            <span>Continue This Session</span>
          </button>

          <button
            className="trailing-action-button trailing-action-fresh"
            onClick={onStartFresh}
            disabled={!onStartFresh}
          >
            <FreshIcon />
            <span>Start Fresh</span>
          </button>

          <button
            className="trailing-action-button trailing-action-crystal"
            onClick={onViewCrystal}
            disabled={!onViewCrystal}
          >
            <CrystalIcon />
            <span>View Crystal</span>
          </button>

          {onDismiss && (
            <button
              className="trailing-action-button trailing-action-dismiss"
              onClick={onDismiss}
              aria-label="Dismiss trailing section"
            >
              <DismissIcon />
            </button>
          )}
        </div>

        {/* Quick crystal summary */}
        <div className="trailing-summary">
          <div className="trailing-summary-stat">
            <span className="trailing-summary-label">Turns:</span>
            <span className="trailing-summary-value">{crystal.turn_count}</span>
          </div>
          <div className="trailing-summary-stat">
            <span className="trailing-summary-label">Confidence:</span>
            <span className="trailing-summary-value">
              {Math.round(crystal.final_evidence.confidence * 100)}%
            </span>
          </div>
          {crystal.key_decisions.length > 0 && (
            <div className="trailing-summary-stat">
              <span className="trailing-summary-label">Decisions:</span>
              <span className="trailing-summary-value">
                {crystal.key_decisions.length}
              </span>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

// =============================================================================
// Trailing Turn Component
// =============================================================================

interface TrailingTurnProps {
  turn: Turn;
}

function TrailingTurn({ turn }: TrailingTurnProps) {
  return (
    <div className="trailing-turn">
      {/* User message */}
      <div className="trailing-turn-user">
        <span className="trailing-turn-icon">∴</span>
        <span className="trailing-turn-text">{turn.user_message.content}</span>
      </div>

      {/* Assistant response */}
      <div className="trailing-turn-assistant">
        <span className="trailing-turn-icon">∵</span>
        <span className="trailing-turn-text">{turn.assistant_response.content}</span>
      </div>
    </div>
  );
}

// =============================================================================
// Icons
// =============================================================================

function ContinueIcon() {
  return (
    <svg
      className="trailing-action-icon"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="9 18 15 12 9 6" />
    </svg>
  );
}

function FreshIcon() {
  return (
    <svg
      className="trailing-action-icon"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

function CrystalIcon() {
  return (
    <svg
      className="trailing-action-icon"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polygon points="12 2 2 7 12 12 22 7 12 2" />
      <polyline points="2 17 12 22 22 17" />
      <polyline points="2 12 12 17 22 12" />
    </svg>
  );
}

function DismissIcon() {
  return (
    <svg
      className="trailing-action-icon"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

// =============================================================================
// Utilities
// =============================================================================

/**
 * Convert timestamp to human-readable "time ago" string
 */
function getTimeAgo(timestamp: string): string {
  const now = new Date().getTime();
  const then = new Date(timestamp).getTime();
  const diffMs = now - then;

  const minutes = Math.floor(diffMs / 60000);
  const hours = Math.floor(diffMs / 3600000);
  const days = Math.floor(diffMs / 86400000);

  if (minutes < 1) return 'just now';
  if (minutes === 1) return '1 min ago';
  if (minutes < 60) return `${minutes} min ago`;
  if (hours === 1) return '1 hour ago';
  if (hours < 24) return `${hours} hours ago`;
  if (days === 1) return '1 day ago';
  return `${days} days ago`;
}

// =============================================================================
// Default Export
// =============================================================================

export default TrailingSession;
