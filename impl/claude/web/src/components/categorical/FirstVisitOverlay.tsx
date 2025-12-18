/**
 * FirstVisitOverlay: Welcome modal for first-time users.
 *
 * Shows per-jewel introduction with option to dismiss permanently.
 * Uses localStorage to track which jewels have been introduced.
 *
 * @see plans/park-town-design-overhaul.md
 */

import { useState, useEffect } from 'react';
import { X, Sparkles, Users, Theater, ArrowRight } from 'lucide-react';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

export type JewelType = 'town' | 'park' | 'forge' | 'coalition' | 'brain' | 'gardener' | 'gestalt';

export interface FirstVisitOverlayProps {
  /** Which jewel this is for */
  jewel: JewelType;
  /** Children to highlight (optional) */
  children?: React.ReactNode;
  /** Custom content override */
  customContent?: React.ReactNode;
  /** Callback when "Show me how" is clicked */
  onShowTutorial?: () => void;
  /** Callback when dismissed */
  onDismiss?: () => void;
  /** Force show even if previously dismissed (for testing) */
  forceShow?: boolean;
}

// =============================================================================
// Configuration
// =============================================================================

const STORAGE_KEY_PREFIX = 'kgents_first_visit_';

interface JewelConfig {
  title: string;
  subtitle: string;
  description: string;
  icon: typeof Sparkles;
  color: string;
  gradient: string;
  features: string[];
}

const JEWEL_CONFIGS: Record<JewelType, JewelConfig> = {
  town: {
    title: 'Welcome to Agent Town',
    subtitle: 'A living simulation of polynomial agents',
    description:
      'Each citizen follows a state machine with 5 phases. Watch them interact, form relationships, and respect the Right to Rest.',
    icon: Users,
    color: '#8b5cf6',
    gradient: 'from-purple-500/20 to-pink-500/20',
    features: [
      'Citizens with 5-phase lifecycles',
      'Operad-defined interactions',
      'Coalition formation',
      'Real-time streaming',
    ],
  },
  park: {
    title: 'Welcome to Punchdrunk Park',
    subtitle: 'Where the director is invisible',
    description:
      'Practice crisis response with serendipity injection. The director orchestrates experiences while respecting consent boundaries.',
    icon: Theater,
    color: '#f59e0b',
    gradient: 'from-amber-500/20 to-red-500/20',
    features: [
      'Crisis phase state machine',
      'Compliance timers',
      'Consent debt tracking',
      'Mask-based affordances',
    ],
  },
  forge: {
    title: 'Welcome to the Forge',
    subtitle: 'The fishbowl where spectators collaborate',
    description:
      'Watch and influence creative sessions in real-time. Your participation shapes the outcome through earned actions.',
    icon: Sparkles,
    color: '#ec4899',
    gradient: 'from-pink-500/20 to-purple-500/20',
    features: [
      'Exquisite corpse mode',
      'Spectator economy',
      'Real-time collaboration',
      'AI-human synthesis',
    ],
  },
  coalition: {
    title: 'Welcome to Coalition Forge',
    subtitle: 'Workshop where agents collaborate visibly',
    description:
      'Form coalitions, vote on missions, and accomplish goals through collective action. Every voice matters.',
    icon: Users,
    color: '#3b82f6',
    gradient: 'from-blue-500/20 to-cyan-500/20',
    features: [
      'Coalition formation',
      'Voting mechanism',
      'Mission assignments',
      'Quorum laws',
    ],
  },
  brain: {
    title: 'Welcome to Holographic Brain',
    subtitle: 'A spatial cathedral of memory',
    description:
      'Navigate your knowledge in 3D space. Memories form constellations of meaning, connected by association.',
    icon: Sparkles,
    color: '#06b6d4',
    gradient: 'from-cyan-500/20 to-blue-500/20',
    features: [
      'Spatial memory layout',
      '3D navigation',
      'Crystal formation',
      'Semantic connections',
    ],
  },
  gardener: {
    title: 'Welcome to The Gardener',
    subtitle: 'Cultivation practice for ideas',
    description:
      'Tend to your projects through seasons of growth. Plant seeds, nurture sprouts, and harvest the fruits of your work.',
    icon: Sparkles,
    color: '#22c55e',
    gradient: 'from-green-500/20 to-teal-500/20',
    features: [
      'Seasonal project lifecycle',
      'Garden gestures',
      'Plot management',
      'Entropy budgets',
    ],
  },
  gestalt: {
    title: 'Welcome to Gestalt Visualizer',
    subtitle: 'Living garden where code breathes',
    description:
      'Visualize your codebase as a living system. Watch dependencies flow and understand architecture at a glance.',
    icon: Sparkles,
    color: '#6366f1',
    gradient: 'from-indigo-500/20 to-purple-500/20',
    features: [
      'Architecture visualization',
      'Dependency graphs',
      'Live code metrics',
      'OTEL integration',
    ],
  },
};

// =============================================================================
// Hooks
// =============================================================================

function useFirstVisit(jewel: JewelType, forceShow?: boolean) {
  const [hasVisited, setHasVisited] = useState<boolean | null>(null);

  useEffect(() => {
    if (forceShow) {
      setHasVisited(false);
      return;
    }

    const key = `${STORAGE_KEY_PREFIX}${jewel}`;
    const visited = localStorage.getItem(key) === 'true';
    setHasVisited(visited);
  }, [jewel, forceShow]);

  const markVisited = () => {
    const key = `${STORAGE_KEY_PREFIX}${jewel}`;
    localStorage.setItem(key, 'true');
    setHasVisited(true);
  };

  return { hasVisited, markVisited };
}

/** Hook to reset first visit state (for testing) */
export function useResetFirstVisit() {
  return (jewel?: JewelType) => {
    if (jewel) {
      localStorage.removeItem(`${STORAGE_KEY_PREFIX}${jewel}`);
    } else {
      // Reset all
      Object.keys(JEWEL_CONFIGS).forEach((j) => {
        localStorage.removeItem(`${STORAGE_KEY_PREFIX}${j}`);
      });
    }
  };
}

// =============================================================================
// Component
// =============================================================================

export function FirstVisitOverlay({
  jewel,
  children,
  customContent,
  onShowTutorial,
  onDismiss,
  forceShow,
}: FirstVisitOverlayProps) {
  const { hasVisited, markVisited } = useFirstVisit(jewel, forceShow);
  const config = JEWEL_CONFIGS[jewel];
  const Icon = config.icon;

  const handleDismiss = () => {
    markVisited();
    onDismiss?.();
  };

  const handleShowTutorial = () => {
    markVisited();
    onShowTutorial?.();
  };

  // Still loading or already visited
  if (hasVisited === null || hasVisited) {
    return <>{children}</>;
  }

  return (
    <>
      {children}

      {/* Overlay backdrop */}
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
        {/* Modal */}
        <div
          className={cn(
            'relative max-w-lg w-full mx-4 rounded-2xl overflow-hidden',
            'bg-gradient-to-br',
            config.gradient,
            'border border-white/10 shadow-2xl',
            'animate-in zoom-in-95 duration-300'
          )}
        >
          {/* Close button */}
          <button
            onClick={handleDismiss}
            className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5 text-white/80" />
          </button>

          {/* Content */}
          <div className="p-8">
            {customContent ?? (
              <>
                {/* Icon */}
                <div
                  className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6"
                  style={{ backgroundColor: `${config.color}30` }}
                >
                  <Icon className="w-8 h-8" style={{ color: config.color }} />
                </div>

                {/* Title */}
                <h2 className="text-2xl font-bold text-white mb-2">{config.title}</h2>
                <p className="text-lg text-gray-300 mb-4">{config.subtitle}</p>

                {/* Description */}
                <p className="text-gray-400 mb-6">{config.description}</p>

                {/* Features */}
                <div className="grid grid-cols-2 gap-3 mb-8">
                  {config.features.map((feature, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-2 text-sm text-gray-300"
                    >
                      <div
                        className="w-1.5 h-1.5 rounded-full"
                        style={{ backgroundColor: config.color }}
                      />
                      {feature}
                    </div>
                  ))}
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    onClick={handleDismiss}
                    className="flex-1 px-4 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-medium transition-colors"
                  >
                    Got it
                  </button>
                  {onShowTutorial && (
                    <button
                      onClick={handleShowTutorial}
                      className="flex-1 px-4 py-3 rounded-xl text-white font-medium transition-colors flex items-center justify-center gap-2"
                      style={{ backgroundColor: config.color }}
                    >
                      Show me how
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

export default FirstVisitOverlay;
