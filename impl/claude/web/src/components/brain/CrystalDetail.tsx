/**
 * CrystalDetail - Crystal Detail View with Observer Switching
 *
 * Shows detailed information about a Brain crystal, with different
 * views based on the current observer perspective.
 *
 * Wave 1: Hero Path Polish
 * Foundation 1: Observer-Dependent Perception
 *
 * @see plans/crown-jewels-enlightened.md
 */

import { useMemo } from 'react';
import type { TopologyNode } from '../../api/types';
import { ObserverSwitcher, DEFAULT_OBSERVERS } from '../path';
import { Breathe, PopOnMount } from '../joy';

// =============================================================================
// Types
// =============================================================================

export interface CrystalDetailProps {
  /** The crystal node to display */
  crystal: TopologyNode;
  /** Close callback */
  onClose: () => void;
  /** Current observer */
  observer: string;
  /** Observer change callback */
  onObserverChange: (observer: string) => void;
  /** Size variant */
  variant?: 'panel' | 'modal';
}

// =============================================================================
// Observer View Renderers
// =============================================================================

/**
 * Render crystal content based on observer perspective.
 *
 * This is the core of observer-dependent perception:
 * same crystal, different views based on who is looking.
 */
function renderObserverView(
  crystal: TopologyNode,
  observer: string
): { title: string; content: string; badges: string[] } {
  const content = crystal.content_preview || 'No content captured';

  switch (observer) {
    case 'technical':
      return {
        title: 'Technical Summary',
        content: content,
        badges: ['Raw', 'Detailed', 'Code-centric'],
      };

    case 'casual':
      // Simplified, conversational version
      return {
        title: 'Quick Summary',
        content: content.length > 100 ? `${content.slice(0, 100)}...` : content,
        badges: ['Simple', 'TL;DR'],
      };

    case 'security': {
      // Security-focused view
      const securityConcerns = [];
      if (content.toLowerCase().includes('password'))
        securityConcerns.push('⚠️ Contains password reference');
      if (content.toLowerCase().includes('api key'))
        securityConcerns.push('⚠️ Contains API key reference');
      if (content.toLowerCase().includes('secret'))
        securityConcerns.push('⚠️ Contains secret reference');

      return {
        title: 'Security Analysis',
        content:
          securityConcerns.length > 0
            ? `${content}\n\n--- Security Notes ---\n${securityConcerns.join('\n')}`
            : `${content}\n\n✓ No obvious security concerns detected`,
        badges: securityConcerns.length > 0 ? ['⚠️ Review Required'] : ['✓ Clear'],
      };
    }

    case 'creative':
      // Metaphorical interpretation
      return {
        title: 'Creative Interpretation',
        content: `"${content}"\n\n—This memory crystal holds a thought-fragment, a neuron of the holographic mind, waiting to be connected to others...`,
        badges: ['Metaphor', 'Poetic'],
      };

    default:
      return {
        title: 'Crystal Content',
        content,
        badges: [],
      };
  }
}

// =============================================================================
// Subcomponents
// =============================================================================

interface StatBadgeProps {
  label: string;
  value: string | number;
  color?: string;
}

function StatBadge({ label, value, color = 'cyan' }: StatBadgeProps) {
  const colorClasses: Record<string, string> = {
    cyan: 'bg-cyan-900/50 text-cyan-300 border-cyan-700/50',
    green: 'bg-green-900/50 text-green-300 border-green-700/50',
    yellow: 'bg-yellow-900/50 text-yellow-300 border-yellow-700/50',
    purple: 'bg-purple-900/50 text-purple-300 border-purple-700/50',
    red: 'bg-red-900/50 text-red-300 border-red-700/50',
  };

  return (
    <div className={`px-2 py-1 rounded border ${colorClasses[color]} text-xs`}>
      <span className="text-gray-400">{label}:</span> <span className="font-semibold">{value}</span>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function CrystalDetail({
  crystal,
  onClose,
  observer,
  onObserverChange,
  variant = 'panel',
}: CrystalDetailProps) {
  // Generate observer-specific view
  const view = useMemo(() => renderObserverView(crystal, observer), [crystal, observer]);

  // Format age
  const ageDisplay = useMemo(() => {
    const seconds = crystal.age_seconds;
    if (seconds < 60) return `${Math.round(seconds)}s ago`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.round(seconds / 3600)}h ago`;
    return `${Math.round(seconds / 86400)}d ago`;
  }, [crystal.age_seconds]);

  // Resolution color
  const resolutionColor = useMemo(() => {
    if (crystal.resolution > 0.8) return 'green';
    if (crystal.resolution > 0.5) return 'yellow';
    return 'red';
  }, [crystal.resolution]);

  const containerClass =
    variant === 'modal'
      ? 'fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm'
      : 'h-full';

  const panelClass =
    variant === 'modal'
      ? 'bg-gray-800 rounded-xl shadow-xl max-w-lg w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col'
      : 'bg-gray-800 h-full flex flex-col overflow-hidden';

  return (
    <div className={containerClass} onClick={variant === 'modal' ? onClose : undefined}>
      <PopOnMount scale={1.02} duration={200}>
        <div className={panelClass} onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="p-4 border-b border-gray-700 bg-gray-800/90">
            <div className="flex justify-between items-start gap-2 mb-3">
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-semibold text-white truncate flex items-center gap-2">
                  {crystal.is_hot && (
                    <Breathe intensity={0.4} speed="fast">
                      <span title="Hot crystal - frequently accessed">🔥</span>
                    </Breathe>
                  )}
                  <span>{crystal.label}</span>
                </h3>
                <p className="text-xs text-gray-400 font-mono truncate" title={crystal.id}>
                  {crystal.id}
                </p>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-white text-xl p-1 -mr-1 -mt-1 rounded hover:bg-gray-700 transition-colors flex-shrink-0"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            {/* Stats */}
            <div className="flex flex-wrap gap-2">
              <StatBadge
                label="Resolution"
                value={`${Math.round(crystal.resolution * 100)}%`}
                color={resolutionColor}
              />
              <StatBadge label="Accesses" value={crystal.access_count} color="purple" />
              <StatBadge label="Age" value={ageDisplay} color="cyan" />
              {crystal.is_hot && <StatBadge label="Status" value="Hot" color="yellow" />}
            </div>
          </div>

          {/* Observer Switcher - fixed height to prevent layout shift on hover */}
          <div className="px-4 py-3 border-b border-gray-700 bg-gray-800/50 min-h-[72px]">
            <ObserverSwitcher
              current={observer}
              available={DEFAULT_OBSERVERS.brain}
              onChange={onObserverChange}
              variant="pills"
              size="sm"
            />
          </div>

          {/* Content - Observer Dependent */}
          <div className="flex-1 overflow-y-auto p-4">
            <h4 className="text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
              {view.title}
              {view.badges.map((badge) => (
                <span
                  key={badge}
                  className="px-1.5 py-0.5 bg-gray-700 text-gray-300 text-[10px] rounded"
                >
                  {badge}
                </span>
              ))}
            </h4>
            <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                {view.content}
              </pre>
            </div>

            {/* Path Trace - shows the AGENTESE path */}
            <div className="mt-4 text-xs text-gray-500">
              <span className="font-mono text-cyan-400">
                self.memory.crystal[{crystal.id}].manifest
              </span>
              <span className="mx-2">•</span>
              <span>Observer: {observer}</span>
            </div>
          </div>

          {/* Actions */}
          <div className="p-3 border-t border-gray-700 bg-gray-800/90 flex gap-2">
            <button
              onClick={() => {
                /* TODO: Implement ghost surfacing from this crystal */
              }}
              className="flex-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm font-medium transition-colors"
            >
              🔮 Surface Related
            </button>
            <button
              onClick={onClose}
              className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </PopOnMount>
    </div>
  );
}

export default CrystalDetail;
