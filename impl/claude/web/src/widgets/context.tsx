/**
 * Widget context for passing render functions down the tree.
 *
 * This avoids circular dependency between layout components and WidgetRenderer.
 */

import React, { createContext, useContext } from 'react';
import type { WidgetJSON } from '@/reactive/types';

export interface WidgetRenderFunc {
  (props: {
    widget: WidgetJSON;
    onSelect?: (id: string) => void;
    selectedId?: string | null;
    className?: string;
  }): React.ReactNode;
}

interface WidgetContextValue {
  renderWidget: WidgetRenderFunc;
}

const WidgetContext = createContext<WidgetContextValue | null>(null);

/**
 * Hook to get the widget render function from context.
 * Returns null if no provider is present (for direct component usage).
 */
export function useWidgetRenderOptional(): WidgetRenderFunc | null {
  const ctx = useContext(WidgetContext);
  return ctx?.renderWidget ?? null;
}

/**
 * Hook to get the widget render function from context.
 * Throws if no provider is present.
 */
export function useWidgetRender(): WidgetRenderFunc {
  const ctx = useContext(WidgetContext);
  if (!ctx) {
    throw new Error('useWidgetRender must be used within a WidgetProvider');
  }
  return ctx.renderWidget;
}

export interface WidgetProviderProps {
  renderWidget: WidgetRenderFunc;
  children: React.ReactNode;
}

export function WidgetProvider({ renderWidget, children }: WidgetProviderProps) {
  return (
    <WidgetContext.Provider value={{ renderWidget }}>
      {children}
    </WidgetContext.Provider>
  );
}
