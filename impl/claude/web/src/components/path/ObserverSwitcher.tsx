/**
 * ObserverSwitcher - Wave 0 Foundation 2
 *
 * Core differentiator: same data, different views based on observer context.
 *
 * This component makes observer-dependent perception VISIBLE to users.
 * When viewing a Brain crystal or Gestalt analysis, users can switch
 * observers to see how the same underlying data looks from different
 * perspectives (technical, casual, security, creative, etc.)
 *
 * "There is no view from nowhere. Every perception is observer-dependent."
 *
 * @see spec/protocols/agentese.md - Observer concept
 * @see plans/crown-jewels-enlightened.md - Foundation 2
 */

import { useState, useCallback } from 'react';
import {
  useLayoutClaim,
  ReservedSlot,
  FadeTransition,
} from '@/components/layout-sheaf';

// =============================================================================
// Types
// =============================================================================

export interface Observer {
  id: string;
  label: string;
  description?: string;
  icon?: string;
}

export interface ObserverSwitcherProps {
  /** Currently active observer */
  current: string;
  /** Available observers to switch between */
  available: Observer[];
  /** Callback when observer changes */
  onChange: (observerId: string) => void;
  /** Visual variant */
  variant?: 'pills' | 'dropdown' | 'minimal';
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Additional CSS classes */
  className?: string;
  /** Whether the switcher is disabled */
  disabled?: boolean;
  /** Whether to show descriptions on hover */
  showDescriptions?: boolean;
}

// =============================================================================
// Default Observers
// =============================================================================

/**
 * Default observers for different jewels.
 * These are the common perspectives available across the Crown Jewels.
 */
export const DEFAULT_OBSERVERS: Record<string, Observer[]> = {
  brain: [
    {
      id: 'technical',
      label: 'Technical',
      description: 'Detailed technical summary with code references',
      icon: '',
    },
    {
      id: 'casual',
      label: 'Casual',
      description: 'Plain language summary for quick understanding',
      icon: '',
    },
    {
      id: 'security',
      label: 'Security',
      description: 'Security-focused view highlighting risks and concerns',
      icon: '',
    },
    {
      id: 'creative',
      label: 'Creative',
      description: 'Metaphorical and creative interpretation',
      icon: '',
    },
  ],
  gestalt: [
    {
      id: 'architect',
      label: 'Architect',
      description: 'High-level architecture view with patterns',
      icon: '',
    },
    {
      id: 'developer',
      label: 'Developer',
      description: 'Implementation-focused with dependencies',
      icon: '',
    },
    {
      id: 'reviewer',
      label: 'Reviewer',
      description: 'Code review perspective highlighting issues',
      icon: '',
    },
    {
      id: 'newcomer',
      label: 'Newcomer',
      description: 'Beginner-friendly overview of the codebase',
      icon: '',
    },
  ],
  gardener: [
    {
      id: 'strategic',
      label: 'Strategic',
      description: 'High-level planning and priorities',
      icon: '',
    },
    {
      id: 'tactical',
      label: 'Tactical',
      description: 'Day-to-day task management',
      icon: '',
    },
    {
      id: 'reflective',
      label: 'Reflective',
      description: 'Progress review and retrospective',
      icon: '',
    },
  ],
};

// =============================================================================
// Component
// =============================================================================

export function ObserverSwitcher({
  current,
  available,
  onChange,
  variant = 'pills',
  size = 'md',
  className = '',
  disabled = false,
  showDescriptions = true,
}: ObserverSwitcherProps) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  // Reserve 16px for description slot - prevents layout shift on hover
  useLayoutClaim('observer-description', 16, true);

  const handleChange = useCallback(
    (id: string) => {
      if (!disabled && id !== current) {
        onChange(id);
      }
    },
    [disabled, current, onChange]
  );

  // Size classes
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1.5',
    lg: 'text-base px-4 py-2',
  };

  // Render pills variant
  if (variant === 'pills') {
    return (
      <div className={`flex flex-col gap-1 ${className}`}>
        {/* Header */}
        <div className="flex items-center gap-2" data-testid="observer-header">
          <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-wide">
            Observer
          </span>
          {showDescriptions && (
            <ReservedSlot
              id="observer-description"
              className="flex-1 min-w-0"
              constraints={{ minHeight: 16, maxHeight: 16 }}
            >
              <FadeTransition show={!!hoveredId}>
                <span className="text-[10px] text-gray-400 truncate block">
                  {hoveredId && available.find((o) => o.id === hoveredId)?.description}
                </span>
              </FadeTransition>
            </ReservedSlot>
          )}
        </div>

        {/* Pills */}
        <div className="flex flex-wrap gap-1.5">
          {available.map((observer) => {
            const isActive = observer.id === current;
            return (
              <button
                key={observer.id}
                onClick={() => handleChange(observer.id)}
                onMouseEnter={() => setHoveredId(observer.id)}
                onMouseLeave={() => setHoveredId(null)}
                disabled={disabled}
                className={`
                  ${sizeClasses[size]}
                  rounded-full font-medium
                  transition-all duration-200
                  ${
                    isActive
                      ? 'bg-cyan-600 text-white shadow-md shadow-cyan-900/30'
                      : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600 hover:text-white'
                  }
                  ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                  flex items-center gap-1.5
                `}
                title={observer.description}
              >
                {observer.icon && <span>{observer.icon}</span>}
                <span>{observer.label}</span>
                {isActive && <span className="text-[10px]"></span>}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  // Render dropdown variant
  if (variant === 'dropdown') {
    return (
      <div className={`relative ${className}`}>
        <label className="text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-1 block">
          Observer
        </label>
        <select
          value={current}
          onChange={(e) => handleChange(e.target.value)}
          disabled={disabled}
          className={`
            ${sizeClasses[size]}
            bg-gray-700 text-white rounded border border-gray-600
            focus:outline-none focus:border-cyan-500
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            w-full
          `}
        >
          {available.map((observer) => (
            <option key={observer.id} value={observer.id}>
              {observer.icon} {observer.label}
            </option>
          ))}
        </select>
        {showDescriptions && (
          <p className="text-[10px] text-gray-400 mt-1">
            {available.find((o) => o.id === current)?.description}
          </p>
        )}
      </div>
    );
  }

  // Render minimal variant (just buttons, no label)
  return (
    <div className={`flex gap-1 ${className}`}>
      {available.map((observer) => {
        const isActive = observer.id === current;
        return (
          <button
            key={observer.id}
            onClick={() => handleChange(observer.id)}
            disabled={disabled}
            className={`
              ${sizeClasses[size]}
              rounded font-medium
              transition-colors duration-150
              ${
                isActive
                  ? 'bg-cyan-600/20 text-cyan-400 border border-cyan-500/50'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50 border border-transparent'
              }
              ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            `}
            title={observer.description}
          >
            {observer.icon || observer.label.charAt(0)}
          </button>
        );
      })}
    </div>
  );
}

// =============================================================================
// Compound Components
// =============================================================================

/**
 * PathTrace - Shows the AGENTESE path being invoked.
 *
 * Displays:
 * - The current AGENTESE path (e.g., self.memory.crystal[abc].manifest)
 * - The active observer
 * - Optional effects that may result
 */
export interface PathTraceProps {
  path: string;
  observer?: string;
  aspect?: string;
  effects?: string[];
  className?: string;
}

export function PathTrace({
  path,
  observer = 'default',
  aspect = 'manifest',
  effects = [],
  className = '',
}: PathTraceProps) {
  // Determine context color from path
  const context = path.split('.')[0];
  const contextColors: Record<string, string> = {
    self: 'text-cyan-400 border-cyan-500/30',
    world: 'text-green-400 border-green-500/30',
    concept: 'text-purple-400 border-purple-500/30',
    void: 'text-yellow-400 border-yellow-500/30',
    time: 'text-blue-400 border-blue-500/30',
  };
  const colorClass = contextColors[context] || 'text-gray-400 border-gray-500/30';

  return (
    <div
      className={`
        bg-gray-800/50 rounded-lg border px-3 py-2
        ${colorClass.split(' ')[1]}
        ${className}
      `}
    >
      {/* Path */}
      <div className="flex items-center gap-2 mb-1">
        <span className={`font-mono text-sm font-medium ${colorClass.split(' ')[0]}`}>
          {path}
        </span>
      </div>

      {/* Metadata line */}
      <div className="flex items-center gap-3 text-[10px] text-gray-500">
        <span>
          Aspect: <span className="text-gray-400">{aspect}</span>
        </span>
        {observer !== 'default' && (
          <span>
            Observer: <span className="text-gray-400">{observer}</span>
          </span>
        )}
        {effects.length > 0 && (
          <span>
            Effects: <span className="text-gray-400">{effects.join(', ')}</span>
          </span>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Hooks
// =============================================================================

/**
 * useObserverState - Manage observer state with persistence.
 *
 * Persists observer selection to localStorage so users don't have
 * to re-select their preferred observer on each visit.
 */
export function useObserverState(
  jewel: string,
  defaultObserver: string = 'technical'
): [string, (observer: string) => void] {
  const storageKey = `kgents.observer.${jewel}`;

  const [observer, setObserverState] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(storageKey) || defaultObserver;
    }
    return defaultObserver;
  });

  const setObserver = useCallback(
    (newObserver: string) => {
      setObserverState(newObserver);
      if (typeof window !== 'undefined') {
        localStorage.setItem(storageKey, newObserver);
      }
    },
    [storageKey]
  );

  return [observer, setObserver];
}

export default ObserverSwitcher;
