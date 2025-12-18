/**
 * useTeachingMode - Global teaching mode toggle with localStorage persistence.
 *
 * When teaching mode is ON:
 * - Polynomial state machines visible in panels
 * - Operad operations shown with arity badges
 * - Teaching callouts appear with icon
 * - Trace panel shows categorical interpretation
 *
 * When teaching mode is OFF:
 * - Clean, minimal interface
 * - Operations without categorical explanation
 * - Suitable for experienced users
 *
 * @see plans/park-town-design-overhaul.md - Phase 4: Teaching Layer
 */

import { useState, useEffect, useCallback, createContext, useContext, type ReactNode } from 'react';

// =============================================================================
// Constants
// =============================================================================

const STORAGE_KEY = 'kgents_teaching_mode';
const DEFAULT_TEACHING_MODE = true;

// =============================================================================
// Types
// =============================================================================

export interface TeachingModeState {
  /** Whether teaching mode is enabled */
  enabled: boolean;
  /** Toggle teaching mode on/off */
  toggle: () => void;
  /** Set teaching mode explicitly */
  setEnabled: (enabled: boolean) => void;
  /** Whether state has loaded from localStorage */
  isLoaded: boolean;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for managing teaching mode state with localStorage persistence.
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { enabled, toggle } = useTeachingMode();
 *
 *   return (
 *     <div>
 *       <button onClick={toggle}>
 *         Teaching: {enabled ? 'ON' : 'OFF'}
 *       </button>
 *       {enabled && <TeachingCallout>...</TeachingCallout>}
 *     </div>
 *   );
 * }
 * ```
 */
export function useTeachingMode(): TeachingModeState {
  const [enabled, setEnabledState] = useState<boolean>(DEFAULT_TEACHING_MODE);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored !== null) {
        setEnabledState(stored === 'true');
      }
    } catch {
      // localStorage not available (SSR or privacy mode)
      console.warn('localStorage not available for teaching mode');
    }
    setIsLoaded(true);
  }, []);

  // Persist to localStorage when changed
  const setEnabled = useCallback((value: boolean) => {
    setEnabledState(value);
    try {
      localStorage.setItem(STORAGE_KEY, String(value));
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  const toggle = useCallback(() => {
    setEnabled(!enabled);
  }, [enabled, setEnabled]);

  return { enabled, toggle, setEnabled, isLoaded };
}

// =============================================================================
// Context (for app-wide access without prop drilling)
// =============================================================================

const TeachingModeContext = createContext<TeachingModeState | null>(null);

export interface TeachingModeProviderProps {
  children: ReactNode;
  /** Optional default value override */
  defaultEnabled?: boolean;
}

/**
 * Provider component for app-wide teaching mode access.
 *
 * Wrap your app or layout in this provider to enable useTeachingModeContext().
 *
 * @example
 * ```tsx
 * function App() {
 *   return (
 *     <TeachingModeProvider>
 *       <MyApp />
 *     </TeachingModeProvider>
 *   );
 * }
 * ```
 */
export function TeachingModeProvider({ children, defaultEnabled }: TeachingModeProviderProps) {
  const state = useTeachingMode();

  // Apply default override on first load
  useEffect(() => {
    if (defaultEnabled !== undefined && !state.isLoaded) {
      // Only apply default if no stored value exists
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === null) {
        state.setEnabled(defaultEnabled);
      }
    }
  }, [defaultEnabled, state.isLoaded, state.setEnabled]);

  return <TeachingModeContext.Provider value={state}>{children}</TeachingModeContext.Provider>;
}

/**
 * Access teaching mode state from context.
 *
 * Must be used within a TeachingModeProvider.
 *
 * @throws Error if used outside provider
 */
export function useTeachingModeContext(): TeachingModeState {
  const context = useContext(TeachingModeContext);
  if (!context) {
    throw new Error('useTeachingModeContext must be used within a TeachingModeProvider');
  }
  return context;
}

/**
 * Safe version that returns default state if no provider exists.
 * Useful for components that may be rendered outside the provider.
 */
export function useTeachingModeSafe(): TeachingModeState {
  const context = useContext(TeachingModeContext);
  const fallback = useTeachingMode();
  return context ?? fallback;
}

// =============================================================================
// Utility Components
// =============================================================================

export interface TeachingToggleProps {
  /** Custom className */
  className?: string;
  /** Compact mode (icon only) */
  compact?: boolean;
  /** Label override */
  label?: string;
}

/**
 * Pre-built toggle button for teaching mode.
 *
 * @example
 * ```tsx
 * <TeachingToggle />
 * <TeachingToggle compact />
 * <TeachingToggle label="Show Hints" />
 * ```
 */
export function TeachingToggle({ className = '', compact = false, label }: TeachingToggleProps) {
  const { enabled, toggle, isLoaded } = useTeachingModeSafe();

  if (!isLoaded) {
    return null; // Prevent hydration mismatch
  }

  if (compact) {
    return (
      <button
        onClick={toggle}
        className={`p-2 rounded-lg transition-colors ${
          enabled
            ? 'bg-blue-500/20 text-blue-400'
            : 'bg-gray-700/50 text-gray-500 hover:text-gray-300'
        } ${className}`}
        title={`Teaching Mode: ${enabled ? 'ON' : 'OFF'}`}
        aria-label={`Teaching Mode: ${enabled ? 'ON' : 'OFF'}`}
      >
        <svg
          className="w-5 h-5"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path d="M12 6.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z" />
          <path d="M12 6.5V21.5" />
          <path d="M8 12.5h8" />
          <path d="M8 16.5h8" />
        </svg>
      </button>
    );
  }

  return (
    <button
      onClick={toggle}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
        enabled
          ? 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
          : 'bg-gray-700/50 text-gray-400 hover:text-gray-200 hover:bg-gray-700'
      } ${className}`}
    >
      {/* Lightbulb icon */}
      <svg
        className="w-4 h-4"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path d="M9 18h6" />
        <path d="M10 22h4" />
        <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14" />
      </svg>
      <span className="text-sm font-medium">
        {label ?? (enabled ? 'Teaching ON' : 'Teaching OFF')}
      </span>
    </button>
  );
}

/**
 * Conditional wrapper that only renders children when teaching mode is enabled.
 *
 * @example
 * ```tsx
 * <WhenTeaching>
 *   <TeachingCallout>This only shows when teaching mode is ON</TeachingCallout>
 * </WhenTeaching>
 * ```
 */
export function WhenTeaching({ children }: { children: ReactNode }) {
  const { enabled, isLoaded } = useTeachingModeSafe();

  if (!isLoaded || !enabled) {
    return null;
  }

  return <>{children}</>;
}

/**
 * Conditional wrapper that only renders children when teaching mode is disabled.
 *
 * @example
 * ```tsx
 * <WhenNotTeaching>
 *   <span>Clean mode</span>
 * </WhenNotTeaching>
 * ```
 */
export function WhenNotTeaching({ children }: { children: ReactNode }) {
  const { enabled, isLoaded } = useTeachingModeSafe();

  if (!isLoaded || enabled) {
    return null;
  }

  return <>{children}</>;
}

export default useTeachingMode;
