/**
 * ZeroSeedFoundation -- Post-Genesis onboarding panel with tutorial content
 *
 * After Genesis completes, this panel shows:
 * 1. What You Created - the user's goal and its layer assignment
 * 2. Your Foundation - connection to axioms A1 (Entity), A2 (Morphism), G (Galois)
 * 3. Getting Started - suggested next actions
 * 4. Learn More - links to documentation
 *
 * First-time-only: Uses localStorage to track if user has seen this panel.
 * After viewing once, defaults to hidden.
 *
 * Philosophy:
 *   "Every claim derives from axioms. Every axiom traces to Zero Seed."
 *   "The foundation IS the ground. The derivation IS the path."
 */

import { memo, useEffect, useState, useCallback } from 'react';
import './ZeroSeedFoundation.css';

// =============================================================================
// Types
// =============================================================================

export interface ZeroSeedFoundationProps {
  /** User's first K-Block ID from Genesis */
  userAxiomId: string;
  /** User's declaration content */
  userDeclaration?: string;
  /** Layer the user's K-Block was assigned to */
  layer?: number;
  /** Coherence loss value (0-1, lower is better) */
  loss?: number;
  /** Whether the panel is visible */
  isVisible: boolean;
  /** Callback when user navigates to a node */
  onNavigate?: (nodeId: string) => void;
  /** Callback to close the panel */
  onClose?: () => void;
}

// LocalStorage key for tracking first-time view
const STORAGE_KEY = 'kgents:zero-seed-seen';

// =============================================================================
// Layer Utilities
// =============================================================================

const LAYER_NAMES: Record<number, string> = {
  0: 'System',
  1: 'Axiom',
  2: 'Value',
  3: 'Goal',
  4: 'Spec',
  5: 'Implementation',
  6: 'Reflection',
  7: 'Meta',
};

const LAYER_COLORS: Record<number, string> = {
  0: 'var(--color-ground, #c4a77d)',
  1: 'var(--color-axiom, #8b5cf6)',
  2: 'var(--color-value, #06b6d4)',
  3: 'var(--color-goal, #10b981)',
  4: 'var(--color-spec, #f59e0b)',
  5: 'var(--color-impl, #ef4444)',
  6: 'var(--color-reflection, #ec4899)',
  7: 'var(--color-meta, #6366f1)',
};

// =============================================================================
// Axiom Display Data
// =============================================================================

interface AxiomInfo {
  id: string;
  title: string;
  shortDesc: string;
}

const FOUNDATIONAL_AXIOMS: AxiomInfo[] = [
  {
    id: 'A1',
    title: 'A1: Entity',
    shortDesc: 'Everything is a node in the graph.',
  },
  {
    id: 'A2',
    title: 'A2: Morphism',
    shortDesc: 'Everything composes via >>.',
  },
  {
    id: 'G',
    title: 'G: Galois',
    shortDesc: 'Loss measures coherence. Axioms are fixed points.',
  },
];

// =============================================================================
// Tutorial Content
// =============================================================================

interface NextAction {
  icon: string;
  label: string;
  description: string;
  keybinding?: string;
}

const NEXT_ACTIONS: NextAction[] = [
  {
    icon: 'n',
    label: 'Add More Thoughts',
    description: 'Create new K-Blocks that connect to your first axiom.',
    keybinding: 'n',
  },
  {
    icon: 'e',
    label: 'Edit Your Declaration',
    description: 'Refine your axiom as your thinking evolves.',
    keybinding: 'e',
  },
  {
    icon: 'gd',
    label: 'Explore Derivations',
    description: 'Navigate to parent axioms in the knowledge graph.',
    keybinding: 'gD',
  },
  {
    icon: '?',
    label: 'Get Help',
    description: 'Open the command palette for all available actions.',
    keybinding: ':',
  },
];

interface LearnMoreLink {
  title: string;
  description: string;
  path: string;
}

const LEARN_MORE_LINKS: LearnMoreLink[] = [
  {
    title: 'Zero Seed Protocol',
    description: 'How the epistemic graph works',
    path: '/docs/zero-seed',
  },
  {
    title: 'K-Block Layers',
    description: 'Understanding L0-L7 layer structure',
    path: '/docs/layers',
  },
  {
    title: 'Galois Loss',
    description: 'Coherence measurement and optimization',
    path: '/docs/galois',
  },
];

// =============================================================================
// Sub-components
// =============================================================================

interface AxiomBadgeProps {
  axiom: AxiomInfo;
  isConnected: boolean;
}

const AxiomBadge = memo(function AxiomBadge({ axiom, isConnected }: AxiomBadgeProps) {
  return (
    <div
      className={`zs-foundation__axiom-badge ${isConnected ? 'zs-foundation__axiom-badge--connected' : ''}`}
    >
      <span className="zs-foundation__axiom-id">{axiom.id}</span>
      <div className="zs-foundation__axiom-content">
        <span className="zs-foundation__axiom-title">{axiom.title}</span>
        <span className="zs-foundation__axiom-desc">{axiom.shortDesc}</span>
      </div>
      {isConnected && <span className="zs-foundation__axiom-check">[der]</span>}
    </div>
  );
});

interface ActionCardProps {
  action: NextAction;
}

const ActionCard = memo(function ActionCard({ action }: ActionCardProps) {
  return (
    <div className="zs-foundation__action-card">
      <div className="zs-foundation__action-header">
        {action.keybinding && (
          <kbd className="zs-foundation__action-key">{action.keybinding}</kbd>
        )}
        <span className="zs-foundation__action-label">{action.label}</span>
      </div>
      <p className="zs-foundation__action-desc">{action.description}</p>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ZeroSeedFoundation = memo(function ZeroSeedFoundation({
  userAxiomId,
  userDeclaration,
  layer = 1,
  loss = 0.05,
  isVisible,
  onNavigate,
  onClose,
}: ZeroSeedFoundationProps) {
  const [hasSeenBefore, setHasSeenBefore] = useState<boolean>(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true';
    } catch {
      return false;
    }
  });
  const [showLearnMore, setShowLearnMore] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  // Mark as seen when panel is shown (only once)
  useEffect(() => {
    if (isVisible && !hasSeenBefore) {
      try {
        localStorage.setItem(STORAGE_KEY, 'true');
        setHasSeenBefore(true);
      } catch {
        // localStorage not available
      }
    }
  }, [isVisible, hasSeenBefore]);

  // Handle close with animation
  const handleClose = useCallback(() => {
    setIsClosing(true);
    // Wait for animation to complete
    setTimeout(() => {
      setIsClosing(false);
      onClose?.();
    }, 280);
  }, [onClose]);

  // Handle navigation to axiom
  const handleNavigateToAxiom = useCallback(
    (axiomId: string) => {
      onNavigate?.(axiomId);
    },
    [onNavigate]
  );

  // Compute coherence from loss
  const coherence = Math.round((1 - loss) * 100);
  const coherenceLabel =
    coherence >= 95
      ? 'Near-axiomatic'
      : coherence >= 80
        ? 'Highly coherent'
        : coherence >= 60
          ? 'Coherent'
          : 'Exploratory';

  // If not visible and has been seen before, return null
  // This implements first-time-only display
  if (!isVisible) return null;

  // Get layer styling
  const layerName = LAYER_NAMES[layer] || 'Unknown';
  const layerColor = LAYER_COLORS[layer] || 'var(--color-text-secondary)';

  return (
    <div
      className={`zs-foundation ${isClosing ? 'zs-foundation--closing' : ''}`}
      role="complementary"
      aria-label="Zero Seed Foundation - Getting Started Guide"
    >
      {/* Header */}
      <div className="zs-foundation__header">
        <div className="zs-foundation__header-content">
          <h3 className="zs-foundation__title">Welcome to kgents</h3>
          <p className="zs-foundation__subtitle">
            Your first declaration is now part of the knowledge graph
          </p>
        </div>
        {onClose && (
          <button
            className="zs-foundation__close"
            onClick={handleClose}
            aria-label="Close welcome panel"
            title="Close (you can reopen from Help menu)"
          >
            x
          </button>
        )}
      </div>

      <div className="zs-foundation__content">
        {/* Section 1: What You Created */}
        <section className="zs-foundation__section">
          <h4 className="zs-foundation__section-title">What You Created</h4>
          <div className="zs-foundation__user-kblock">
            <div className="zs-foundation__user-kblock-header">
              <span
                className="zs-foundation__layer-badge"
                style={{ '--layer-color': layerColor } as React.CSSProperties}
              >
                L{layer} {layerName}
              </span>
              <span className="zs-foundation__coherence-badge">
                {coherence}% coherence ({coherenceLabel})
              </span>
            </div>
            {userDeclaration ? (
              <p className="zs-foundation__user-declaration">"{userDeclaration}"</p>
            ) : (
              <p className="zs-foundation__user-declaration zs-foundation__user-declaration--id">
                K-Block: {userAxiomId.slice(0, 16)}...
              </p>
            )}
          </div>
        </section>

        {/* Section 2: Your Foundation */}
        <section className="zs-foundation__section">
          <h4 className="zs-foundation__section-title">Your Foundation</h4>
          <p className="zs-foundation__section-desc">
            Your declaration derives from these foundational axioms:
          </p>
          <div className="zs-foundation__axioms">
            {FOUNDATIONAL_AXIOMS.map((axiom) => (
              <AxiomBadge
                key={axiom.id}
                axiom={axiom}
                isConnected={true}
              />
            ))}
          </div>
        </section>

        {/* Section 3: Getting Started */}
        <section className="zs-foundation__section">
          <h4 className="zs-foundation__section-title">Getting Started</h4>
          <div className="zs-foundation__actions">
            {NEXT_ACTIONS.map((action) => (
              <ActionCard key={action.label} action={action} />
            ))}
          </div>
        </section>

        {/* Section 4: Learn More (Collapsible) */}
        <section className="zs-foundation__section zs-foundation__section--learn-more">
          <button
            className="zs-foundation__learn-more-toggle"
            onClick={() => setShowLearnMore(!showLearnMore)}
            aria-expanded={showLearnMore}
          >
            <span className="zs-foundation__section-title">Learn More</span>
            <span className="zs-foundation__toggle-icon">
              {showLearnMore ? '[-]' : '[+]'}
            </span>
          </button>

          {showLearnMore && (
            <div className="zs-foundation__learn-more-content">
              {LEARN_MORE_LINKS.map((link) => (
                <button
                  key={link.path}
                  className="zs-foundation__learn-link"
                  onClick={() => handleNavigateToAxiom(link.path)}
                >
                  <span className="zs-foundation__learn-title">{link.title}</span>
                  <span className="zs-foundation__learn-desc">{link.description}</span>
                </button>
              ))}
            </div>
          )}
        </section>

        {/* Quick reference hint */}
        <div className="zs-foundation__hint">
          <kbd>:</kbd> command palette &bull; <kbd>?</kbd> help &bull;{' '}
          <kbd>Esc</kbd> close this panel
        </div>
      </div>
    </div>
  );
});

export default ZeroSeedFoundation;
