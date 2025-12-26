/**
 * ThemeProvider
 *
 * Provides Living Earth color theme context to the application.
 * Supports dark mode (default) with potential light mode toggle.
 *
 * Living Earth Palette:
 * - bark: #1C1917 (deep earth background)
 * - lantern: #FAFAF9 (warm light text)
 * - sand: #A8A29E (muted secondary)
 * - clay: #78716C (subtle accents)
 * - sage: #A3E635 (growth, success)
 * - amber: #FBBF24 (warmth, action)
 * - rust: #C2410C (warning, attention)
 */

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';

// =============================================================================
// Types
// =============================================================================

export type ThemeMode = 'dark' | 'light';

export interface ThemeColors {
  bark: string;
  lantern: string;
  sand: string;
  clay: string;
  sage: string;
  amber: string;
  rust: string;
}

export interface ThemeContext {
  mode: ThemeMode;
  colors: ThemeColors;
  toggleMode: () => void;
  setMode: (mode: ThemeMode) => void;
}

// =============================================================================
// Constants
// =============================================================================

const DARK_COLORS: ThemeColors = {
  bark: '#1C1917',
  lantern: '#FAFAF9',
  sand: '#A8A29E',
  clay: '#78716C',
  sage: '#A3E635',
  amber: '#FBBF24',
  rust: '#C2410C',
};

const LIGHT_COLORS: ThemeColors = {
  bark: '#FAFAF9',
  lantern: '#1C1917',
  sand: '#57534E',
  clay: '#A8A29E',
  sage: '#65A30D',
  amber: '#D97706',
  rust: '#DC2626',
};

const STORAGE_KEY = 'kgents-theme-mode';

// =============================================================================
// Context
// =============================================================================

const ThemeContextReact = createContext<ThemeContext | null>(null);

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook to access theme context.
 * Must be used within a ThemeProvider.
 */
export function useTheme(): ThemeContext {
  const context = useContext(ThemeContextReact);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

// =============================================================================
// Provider Component
// =============================================================================

export interface ThemeProviderProps {
  children: ReactNode;
  defaultMode?: ThemeMode;
}

/**
 * ThemeProvider
 *
 * Wraps the application with theme context, providing Living Earth colors
 * and dark/light mode support.
 *
 * @example
 * ```tsx
 * <ThemeProvider defaultMode="dark">
 *   <App />
 * </ThemeProvider>
 * ```
 */
export function ThemeProvider({ children, defaultMode = 'dark' }: ThemeProviderProps) {
  // Initialize from localStorage or default
  const [mode, setModeState] = useState<ThemeMode>(() => {
    if (typeof window === 'undefined') return defaultMode;
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') return stored;
    // Check system preference
    if (window.matchMedia?.('(prefers-color-scheme: light)').matches) {
      return 'light';
    }
    return defaultMode;
  });

  const colors = mode === 'dark' ? DARK_COLORS : LIGHT_COLORS;

  const setMode = useCallback((newMode: ThemeMode) => {
    setModeState(newMode);
    localStorage.setItem(STORAGE_KEY, newMode);
  }, []);

  const toggleMode = useCallback(() => {
    setMode(mode === 'dark' ? 'light' : 'dark');
  }, [mode, setMode]);

  // Apply CSS custom properties to document
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--color-bark', colors.bark);
    root.style.setProperty('--color-lantern', colors.lantern);
    root.style.setProperty('--color-sand', colors.sand);
    root.style.setProperty('--color-clay', colors.clay);
    root.style.setProperty('--color-sage', colors.sage);
    root.style.setProperty('--color-amber', colors.amber);
    root.style.setProperty('--color-rust', colors.rust);

    // Set data attribute for potential CSS selectors
    root.setAttribute('data-theme', mode);
  }, [colors, mode]);

  // Listen for system preference changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
    const handleChange = (e: MediaQueryListEvent) => {
      // Only auto-switch if user hasn't explicitly set a preference
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        setModeState(e.matches ? 'light' : 'dark');
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const value: ThemeContext = {
    mode,
    colors,
    toggleMode,
    setMode,
  };

  return (
    <ThemeContextReact.Provider value={value}>
      {children}
    </ThemeContextReact.Provider>
  );
}

ThemeProvider.displayName = 'ThemeProvider';

export default ThemeProvider;
