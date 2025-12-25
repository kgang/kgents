/**
 * SessionCrystal - Crystallized session summary view
 *
 * Displays compressed session summary with key decisions and artifacts.
 * Modal or side panel for quick reference.
 *
 * @see spec/protocols/chat-web.md §9.4
 */

import { motion, AnimatePresence } from 'framer-motion';
import { UnfurlPanel } from '@/components/joy';
import { LIVING_EARTH, TIMING } from '@/constants';
import type { SessionCrystal as SessionCrystalData } from './store';

// =============================================================================
// Types
// =============================================================================

export interface SessionCrystalProps {
  /** The crystallized session data */
  crystal: SessionCrystalData;

  /** Whether crystal panel is open */
  isOpen: boolean;

  /** Callback to close panel */
  onClose?: () => void;

  /** Display mode: modal or panel */
  mode?: 'modal' | 'panel';

  /** Custom className */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * SessionCrystal
 *
 * Displays a crystallized session summary for quick reference.
 * Can be shown as a modal or side panel.
 *
 * @example Modal mode:
 * ```tsx
 * <SessionCrystal
 *   crystal={sessionData}
 *   isOpen={showCrystal}
 *   onClose={() => setShowCrystal(false)}
 *   mode="modal"
 * />
 * ```
 *
 * @example Panel mode:
 * ```tsx
 * <SessionCrystal
 *   crystal={sessionData}
 *   isOpen={showPanel}
 *   onClose={() => setShowPanel(false)}
 *   mode="panel"
 * />
 * ```
 */
export function SessionCrystal({
  crystal,
  isOpen,
  onClose,
  mode = 'panel',
  className = '',
}: SessionCrystalProps) {
  if (mode === 'modal') {
    return <CrystalModal crystal={crystal} isOpen={isOpen} onClose={onClose} className={className} />;
  }

  return <CrystalPanel crystal={crystal} isOpen={isOpen} onClose={onClose} className={className} />;
}

// =============================================================================
// Modal Variant
// =============================================================================

function CrystalModal({
  crystal,
  isOpen,
  onClose,
  className = '',
}: SessionCrystalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal */}
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <motion.div
              className={`crystal-modal ${className}`}
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: TIMING.standard / 1000 }}
              style={{
                background: LIVING_EARTH.bark,
                border: `1px solid ${LIVING_EARTH.amber}`,
                borderRadius: 12,
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
                maxWidth: 600,
                maxHeight: '80vh',
                overflow: 'auto',
                width: '100%',
              }}
            >
              <CrystalContent crystal={crystal} onClose={onClose} />
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}

// =============================================================================
// Panel Variant
// =============================================================================

function CrystalPanel({
  crystal,
  isOpen,
  onClose,
  className = '',
}: SessionCrystalProps) {
  return (
    <UnfurlPanel
      isOpen={isOpen}
      direction="left"
      organicBorder
      accentColor={LIVING_EARTH.amber}
      className={`crystal-panel ${className}`}
      contentClassName="p-6"
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: 400,
        background: LIVING_EARTH.bark,
        boxShadow: '-4px 0 16px rgba(0, 0, 0, 0.3)',
        zIndex: 40,
      }}
    >
      <CrystalContent crystal={crystal} onClose={onClose} />
    </UnfurlPanel>
  );
}

// =============================================================================
// Crystal Content
// =============================================================================

interface CrystalContentProps {
  crystal: SessionCrystalData;
  onClose?: () => void;
}

function CrystalContent({ crystal, onClose }: CrystalContentProps) {
  const confidencePercent = Math.round(crystal.final_evidence.confidence * 100);
  const successRate =
    crystal.final_evidence.tools_succeeded /
    (crystal.final_evidence.tools_succeeded + crystal.final_evidence.tools_failed);

  return (
    <div className="crystal-content">
      {/* Header */}
      <div className="crystal-header">
        <div className="crystal-header-main">
          <CrystalIcon />
          <h2 className="crystal-title" style={{ color: LIVING_EARTH.lantern }}>
            {crystal.title}
          </h2>
        </div>
        {onClose && (
          <button
            className="crystal-close"
            onClick={onClose}
            aria-label="Close crystal view"
          >
            <CloseIcon />
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="crystal-stats">
        <CrystalStat label="Turns" value={crystal.turn_count.toString()} />
        <CrystalStat label="Confidence" value={`${confidencePercent}%`} />
        {crystal.final_evidence.tools_succeeded > 0 && (
          <CrystalStat
            label="Success Rate"
            value={`${Math.round(successRate * 100)}%`}
          />
        )}
      </div>

      {/* Summary */}
      <section className="crystal-section">
        <h3 className="crystal-section-title" style={{ color: LIVING_EARTH.sand }}>
          Summary
        </h3>
        <p className="crystal-summary" style={{ color: LIVING_EARTH.clay }}>
          {crystal.summary}
        </p>
      </section>

      {/* Key Decisions */}
      {crystal.key_decisions.length > 0 && (
        <section className="crystal-section">
          <h3 className="crystal-section-title" style={{ color: LIVING_EARTH.sand }}>
            Key Decisions
          </h3>
          <ul className="crystal-list">
            {crystal.key_decisions.map((decision, i) => (
              <li key={i} className="crystal-list-item" style={{ color: LIVING_EARTH.clay }}>
                {decision}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Artifacts */}
      {crystal.artifacts.length > 0 && (
        <section className="crystal-section">
          <h3 className="crystal-section-title" style={{ color: LIVING_EARTH.sand }}>
            Artifacts
          </h3>
          <ul className="crystal-list">
            {crystal.artifacts.map((artifact, i) => (
              <li key={i} className="crystal-artifact-item">
                <FileIcon />
                <span style={{ color: LIVING_EARTH.clay }}>{artifact}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Metadata */}
      <section className="crystal-metadata">
        <span className="crystal-metadata-label" style={{ color: LIVING_EARTH.sand }}>
          Created:
        </span>
        <span className="crystal-metadata-value" style={{ color: LIVING_EARTH.clay }}>
          {new Date(crystal.created_at).toLocaleString()}
        </span>
      </section>
    </div>
  );
}

// =============================================================================
// Crystal Stat Component
// =============================================================================

interface CrystalStatProps {
  label: string;
  value: string;
}

function CrystalStat({ label, value }: CrystalStatProps) {
  return (
    <div className="crystal-stat">
      <span className="crystal-stat-label" style={{ color: LIVING_EARTH.sand }}>
        {label}
      </span>
      <span className="crystal-stat-value" style={{ color: LIVING_EARTH.lantern }}>
        {value}
      </span>
    </div>
  );
}

// =============================================================================
// Icons
// =============================================================================

function CrystalIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke={LIVING_EARTH.amber}
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

function CloseIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke={LIVING_EARTH.clay}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function FileIcon() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke={LIVING_EARTH.sage}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
      <polyline points="13 2 13 9 20 9" />
    </svg>
  );
}

// =============================================================================
// Styles
// =============================================================================

const styles = `
.crystal-content {
  padding: 1.5rem;
}

.crystal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.crystal-header-main {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.crystal-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.crystal-close {
  padding: 0.5rem;
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.crystal-close:hover {
  background: rgba(255, 255, 255, 0.1);
}

.crystal-stats {
  display: flex;
  gap: 1.5rem;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.crystal-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.crystal-stat-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.crystal-stat-value {
  font-size: 1.25rem;
  font-weight: 700;
}

.crystal-section {
  margin-bottom: 1.5rem;
}

.crystal-section-title {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
}

.crystal-summary {
  line-height: 1.6;
  font-size: 0.9rem;
}

.crystal-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.crystal-list-item {
  padding-left: 1.25rem;
  position: relative;
  line-height: 1.5;
  font-size: 0.9rem;
}

.crystal-list-item::before {
  content: "→";
  position: absolute;
  left: 0;
  color: ${LIVING_EARTH.amber};
}

.crystal-artifact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  font-size: 0.875rem;
  font-family: monospace;
}

.crystal-metadata {
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.crystal-metadata-label {
  font-weight: 500;
}

@media (max-width: 640px) {
  .crystal-stats {
    flex-direction: column;
    gap: 1rem;
  }
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleElement = document.createElement('style');
  styleElement.textContent = styles;
  document.head.appendChild(styleElement);
}

// =============================================================================
// Default Export
// =============================================================================

export default SessionCrystal;
