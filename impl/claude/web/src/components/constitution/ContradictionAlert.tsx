/**
 * ContradictionAlert - Conflict between axioms display.
 *
 * Shows contradictions as opportunities for synthesis, not problems.
 * Links to dialectical fusion for resolution.
 *
 * Philosophy:
 *   "Contradiction handling feels like opportunity, not problem."
 *   "Contradictions are invitations to deeper understanding."
 *
 * @see components/constitution/PersonalConstitutionBuilder.tsx
 * @see services/zero_seed/axiom_discovery_pipeline.py
 */

import { motion } from 'framer-motion';
import type { ContradictionPair, ContradictionSeverity } from './types';
import { getSeverityLabel } from './types';
import { TIMING, GLOW } from '@/constants';
import './ContradictionAlert.css';

// =============================================================================
// Types
// =============================================================================

export interface ContradictionAlertProps {
  /** The contradiction to display */
  contradiction: ContradictionPair;

  /** Whether this alert is expanded */
  isExpanded?: boolean;

  /** Callback when expanded state changes */
  onExpandedChange?: (expanded: boolean) => void;

  /** Callback to initiate dialectical fusion */
  onFuse?: (contradiction: ContradictionPair) => void;

  /** Callback to dismiss this contradiction */
  onDismiss?: (contradiction: ContradictionPair) => void;

  /** Custom className */
  className?: string;

  /** Index for staggered animations */
  index?: number;
}

// =============================================================================
// Constants
// =============================================================================

const SEVERITY_COLORS: Record<ContradictionSeverity, string> = {
  weak: GLOW.honey,
  moderate: GLOW.amber,
  strong: GLOW.copper,
  irreconcilable: '#ef4444', // Red for truly irreconcilable
};

const SEVERITY_MESSAGES: Record<ContradictionSeverity, string> = {
  weak: 'These axioms have a subtle tension. They may coexist with care.',
  moderate: 'These axioms conflict in some contexts. Consider when each applies.',
  strong: 'These axioms strongly contradict. One may need to yield to the other.',
  irreconcilable: 'These axioms cannot both be true. A choice must be made.',
};

const OPPORTUNITY_MESSAGES: Record<ContradictionSeverity, string> = {
  weak: 'This tension might reveal nuance in your values.',
  moderate: 'This conflict invites you to explore boundary conditions.',
  strong: 'This contradiction offers an opportunity for synthesis.',
  irreconcilable: 'This opposition demands a principled choice.',
};

// =============================================================================
// Sub-components
// =============================================================================

interface SeverityIconProps {
  severity: ContradictionSeverity;
}

function SeverityIcon({ severity }: SeverityIconProps) {
  const color = SEVERITY_COLORS[severity];

  // Different icons for different severities
  if (severity === 'weak') {
    return (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <circle cx="10" cy="10" r="8" stroke={color} strokeWidth="1.5" />
        <path d="M10 6v4" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="10" cy="13" r="1" fill={color} />
      </svg>
    );
  }

  if (severity === 'moderate') {
    return (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 2L18 17H2L10 2Z" stroke={color} strokeWidth="1.5" strokeLinejoin="round" />
        <path d="M10 7v4" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="10" cy="14" r="1" fill={color} />
      </svg>
    );
  }

  if (severity === 'strong') {
    return (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path
          d="M10 2L18 17H2L10 2Z"
          fill={`${color}20`}
          stroke={color}
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        <path d="M10 7v4" stroke={color} strokeWidth="2" strokeLinecap="round" />
        <circle cx="10" cy="14" r="1.5" fill={color} />
      </svg>
    );
  }

  // Irreconcilable
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="8" fill={`${color}20`} stroke={color} strokeWidth="2" />
      <path d="M7 7l6 6M13 7l-6 6" stroke={color} strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

interface LossDiagramProps {
  lossA: number;
  lossB: number;
  lossCombined: number;
}

function LossDiagram({ lossA, lossB, lossCombined }: LossDiagramProps) {
  const expected = lossA + lossB;
  const excess = lossCombined - expected;

  return (
    <div className="loss-diagram">
      <div className="loss-item">
        <span className="loss-label">A alone</span>
        <span className="loss-value">{lossA.toFixed(3)}</span>
      </div>
      <span className="loss-operator">+</span>
      <div className="loss-item">
        <span className="loss-label">B alone</span>
        <span className="loss-value">{lossB.toFixed(3)}</span>
      </div>
      <span className="loss-operator">=</span>
      <div className="loss-item expected">
        <span className="loss-label">Expected</span>
        <span className="loss-value">{expected.toFixed(3)}</span>
      </div>
      <span className="loss-operator">but</span>
      <div className="loss-item combined">
        <span className="loss-label">Combined</span>
        <span className="loss-value">{lossCombined.toFixed(3)}</span>
      </div>
      <span className="loss-operator">excess:</span>
      <div className="loss-item excess">
        <span className="loss-value excess-value">+{excess.toFixed(3)}</span>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ContradictionAlert({
  contradiction,
  isExpanded = false,
  onExpandedChange,
  onFuse,
  onDismiss,
  className = '',
  index = 0,
}: ContradictionAlertProps) {
  const { axiomA, axiomB, lossA, lossB, lossCombined, strength, type, synthesisHint } =
    contradiction;

  const severityColor = SEVERITY_COLORS[type];

  // Animation variants
  const variants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { delay: index * 0.1, duration: TIMING.standard / 1000 },
    },
  };

  return (
    <motion.article
      className={`contradiction-alert severity-${type} ${isExpanded ? 'expanded' : ''} ${className}`}
      variants={variants}
      initial="hidden"
      animate="visible"
      style={
        {
          '--severity-color': severityColor,
        } as React.CSSProperties
      }
    >
      {/* Header */}
      <header className="contradiction-header">
        <div className="contradiction-icon">
          <SeverityIcon severity={type} />
        </div>
        <div className="contradiction-title">
          <span className="severity-label">{getSeverityLabel(type)}</span>
          <span className="contradiction-subtitle">Tension Detected</span>
        </div>
        <span className="strength-badge" title={`Super-additive excess: ${strength.toFixed(3)}`}>
          {(strength * 100).toFixed(0)}%
        </span>
      </header>

      {/* Axiom Pair */}
      <div className="axiom-pair">
        <div className="axiom-a">
          <span className="axiom-marker">A</span>
          <p className="axiom-content">{axiomA}</p>
        </div>
        <div className="versus">
          <span>vs</span>
        </div>
        <div className="axiom-b">
          <span className="axiom-marker">B</span>
          <p className="axiom-content">{axiomB}</p>
        </div>
      </div>

      {/* Severity Message */}
      <p className="severity-message">{SEVERITY_MESSAGES[type]}</p>

      {/* Expanded Content */}
      {isExpanded && (
        <motion.div
          className="contradiction-details"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          transition={{ duration: TIMING.quick / 1000 }}
        >
          {/* Loss Diagram */}
          <div className="loss-section">
            <h4 className="section-title">Why these conflict</h4>
            <p className="section-desc">
              When combined, these axioms lose more meaning than they would individually. This
              super-additive loss signals semantic interference.
            </p>
            <LossDiagram lossA={lossA} lossB={lossB} lossCombined={lossCombined} />
          </div>

          {/* Synthesis Hint */}
          {synthesisHint && (
            <div className="synthesis-section">
              <h4 className="section-title">Possible Synthesis</h4>
              <p className="synthesis-hint">{synthesisHint}</p>
            </div>
          )}

          {/* Opportunity Message */}
          <div className="opportunity-section">
            <p className="opportunity-message">{OPPORTUNITY_MESSAGES[type]}</p>
          </div>
        </motion.div>
      )}

      {/* Actions */}
      <footer className="contradiction-actions">
        <button className="action-btn secondary" onClick={() => onExpandedChange?.(!isExpanded)}>
          {isExpanded ? 'Less' : 'Details'}
        </button>
        {onDismiss && (
          <button className="action-btn dismiss" onClick={() => onDismiss(contradiction)}>
            Acknowledge
          </button>
        )}
        {onFuse && (
          <button className="action-btn fuse" onClick={() => onFuse(contradiction)}>
            Attempt Synthesis
          </button>
        )}
      </footer>
    </motion.article>
  );
}

export default ContradictionAlert;
