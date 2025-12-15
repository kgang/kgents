/**
 * Widget Context: Theme and interaction context for reactive widgets.
 *
 * Provides:
 * - Theme configuration (colors, fonts, animations)
 * - Global interaction handlers
 * - Selection state management
 */

import { createContext, useContext, useCallback, useState, useMemo, ReactNode } from 'react';

// =============================================================================
// Theme Types
// =============================================================================

export interface WidgetTheme {
  /** Color palette */
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    background: string;
    surface: string;
    text: string;
    textMuted: string;
    border: string;
  };
  /** Font family for widget text */
  fontFamily: string;
  /** Monospace font for glyphs and bars */
  fontMono: string;
  /** Base spacing unit in pixels */
  spacing: number;
  /** Border radius in pixels */
  borderRadius: number;
  /** Enable animations */
  animationsEnabled: boolean;
}

export const defaultTheme: WidgetTheme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#6366f1',
    success: '#22c55e',
    warning: '#f59e0b',
    error: '#ef4444',
    background: '#ffffff',
    surface: '#f3f4f6',
    text: '#111827',
    textMuted: '#6b7280',
    border: '#e5e7eb',
  },
  fontFamily: 'system-ui, -apple-system, sans-serif',
  fontMono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
  spacing: 8,
  borderRadius: 8,
  animationsEnabled: true,
};

export const darkTheme: WidgetTheme = {
  colors: {
    primary: '#60a5fa',
    secondary: '#818cf8',
    success: '#4ade80',
    warning: '#fbbf24',
    error: '#f87171',
    background: '#111827',
    surface: '#1f2937',
    text: '#f9fafb',
    textMuted: '#9ca3af',
    border: '#374151',
  },
  fontFamily: 'system-ui, -apple-system, sans-serif',
  fontMono: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
  spacing: 8,
  borderRadius: 8,
  animationsEnabled: true,
};

// =============================================================================
// Context Types
// =============================================================================

export interface WidgetContextValue {
  /** Current theme */
  theme: WidgetTheme;
  /** Set theme */
  setTheme: (theme: WidgetTheme) => void;
  /** Currently selected widget ID */
  selectedId: string | null;
  /** Set selected widget ID */
  setSelectedId: (id: string | null) => void;
  /** Handle widget selection */
  onSelect: (id: string) => void;
  /** Clear selection */
  clearSelection: () => void;
}

// =============================================================================
// Context
// =============================================================================

const WidgetContext = createContext<WidgetContextValue | null>(null);

// =============================================================================
// Provider
// =============================================================================

export interface WidgetProviderProps {
  children: ReactNode;
  /** Initial theme (default: defaultTheme) */
  initialTheme?: WidgetTheme;
  /** Initial selected ID */
  initialSelectedId?: string | null;
  /** External selection handler */
  onSelectionChange?: (id: string | null) => void;
}

export function WidgetProvider({
  children,
  initialTheme = defaultTheme,
  initialSelectedId = null,
  onSelectionChange,
}: WidgetProviderProps) {
  const [theme, setTheme] = useState<WidgetTheme>(initialTheme);
  const [selectedId, setSelectedIdInternal] = useState<string | null>(initialSelectedId);

  const setSelectedId = useCallback(
    (id: string | null) => {
      setSelectedIdInternal(id);
      onSelectionChange?.(id);
    },
    [onSelectionChange]
  );

  const onSelect = useCallback(
    (id: string) => {
      // Toggle selection if clicking same item
      setSelectedId(selectedId === id ? null : id);
    },
    [selectedId, setSelectedId]
  );

  const clearSelection = useCallback(() => {
    setSelectedId(null);
  }, [setSelectedId]);

  const value = useMemo<WidgetContextValue>(
    () => ({
      theme,
      setTheme,
      selectedId,
      setSelectedId,
      onSelect,
      clearSelection,
    }),
    [theme, selectedId, setSelectedId, onSelect, clearSelection]
  );

  return <WidgetContext.Provider value={value}>{children}</WidgetContext.Provider>;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook to access widget context.
 *
 * @throws if used outside WidgetProvider
 */
export function useWidgetContext(): WidgetContextValue {
  const context = useContext(WidgetContext);
  if (!context) {
    throw new Error('useWidgetContext must be used within a WidgetProvider');
  }
  return context;
}

/**
 * Hook to access just the theme (safe outside provider).
 * Returns default theme if no provider.
 */
export function useWidgetTheme(): WidgetTheme {
  const context = useContext(WidgetContext);
  return context?.theme ?? defaultTheme;
}

// =============================================================================
// CSS Custom Properties
// =============================================================================

/**
 * Generate CSS custom properties from theme.
 * Use with style={{ ...themeToCSS(theme) }}
 */
export function themeToCSS(theme: WidgetTheme): Record<string, string> {
  return {
    '--kgents-primary': theme.colors.primary,
    '--kgents-secondary': theme.colors.secondary,
    '--kgents-success': theme.colors.success,
    '--kgents-warning': theme.colors.warning,
    '--kgents-error': theme.colors.error,
    '--kgents-bg': theme.colors.background,
    '--kgents-surface': theme.colors.surface,
    '--kgents-text': theme.colors.text,
    '--kgents-text-muted': theme.colors.textMuted,
    '--kgents-border': theme.colors.border,
    '--kgents-font': theme.fontFamily,
    '--kgents-font-mono': theme.fontMono,
    '--kgents-spacing': `${theme.spacing}px`,
    '--kgents-radius': `${theme.borderRadius}px`,
  };
}

// =============================================================================
// Exports
// =============================================================================

export { WidgetContext };
