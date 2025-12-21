/**
 * Test Providers - Deterministic Context for Frontend Tests
 *
 * PRINCIPLE: Components that consume context must be testable with injected context.
 * This is a category-theoretic insight: if `render: Context -> ReactNode` is a functor,
 * then test fixtures must provide the full domain, not rely on environmental state.
 *
 * PATTERN: Test Context Injection
 * - Tests should be deterministic, not dependent on mocked globals or DOM timing
 * - Context is explicitly provided, making test intent clear
 * - Composable with other providers (ShellProvider, etc.)
 *
 * @see docs/skills/test-patterns.md
 * @see plans/meta.md - "Context-dependent components need test-aware providers"
 */

import type { ReactNode } from 'react';
import type { LayoutContext } from '@/reactive/types';
import { LayoutContextProvider } from '@/hooks/useLayoutContext';

// =============================================================================
// Layout Context Testing
// =============================================================================

/**
 * Default layout context for tests - spacious desktop viewport
 *
 * Uses concrete values (not CSS variables) for predictability in tests.
 * Matches the "comfortable" scenario where all content levels render fully.
 */
export const DEFAULT_TEST_LAYOUT_CONTEXT: LayoutContext = {
  availableWidth: 1280,
  availableHeight: 800,
  depth: 0,
  parentLayout: 'stack',
  isConstrained: false,
  density: 'spacious',
};

/**
 * Constrained layout context - simulates mobile/icon-only view
 */
export const CONSTRAINED_TEST_LAYOUT_CONTEXT: LayoutContext = {
  availableWidth: 320,
  availableHeight: 568,
  depth: 0,
  parentLayout: 'stack',
  isConstrained: true,
  density: 'compact',
};

/**
 * Comfortable layout context - tablet viewport
 */
export const COMFORTABLE_TEST_LAYOUT_CONTEXT: LayoutContext = {
  availableWidth: 768,
  availableHeight: 1024,
  depth: 0,
  parentLayout: 'stack',
  isConstrained: false,
  density: 'comfortable',
};

export interface TestLayoutProviderProps {
  children: ReactNode;
  /** Override specific context values */
  context?: Partial<LayoutContext>;
  /** Use a preset context (overridden by context prop) */
  preset?: 'spacious' | 'comfortable' | 'compact';
}

/**
 * TestLayoutProvider: Provides controlled layout context for testing
 *
 * USAGE:
 * ```tsx
 * // Default spacious context (most common - full content renders)
 * render(
 *   <TestLayoutProvider>
 *     <CitizenCard {...props} />
 *   </TestLayoutProvider>
 * );
 *
 * // Test constrained behavior
 * render(
 *   <TestLayoutProvider preset="compact">
 *     <CitizenCard {...props} />
 *   </TestLayoutProvider>
 * );
 *
 * // Custom context for edge cases
 * render(
 *   <TestLayoutProvider context={{ availableWidth: 150, isConstrained: true }}>
 *     <CitizenCard {...props} />
 *   </TestLayoutProvider>
 * );
 * ```
 */
export function TestLayoutProvider({
  children,
  context,
  preset = 'spacious',
}: TestLayoutProviderProps) {
  // Select base context from preset
  const baseContext =
    preset === 'compact'
      ? CONSTRAINED_TEST_LAYOUT_CONTEXT
      : preset === 'comfortable'
        ? COMFORTABLE_TEST_LAYOUT_CONTEXT
        : DEFAULT_TEST_LAYOUT_CONTEXT;

  // Merge with overrides
  const fullContext: LayoutContext = {
    ...baseContext,
    ...context,
  };

  // LayoutContextProvider is a React Context, use .Provider
  return (
    <LayoutContextProvider.Provider value={fullContext}>
      {children}
    </LayoutContextProvider.Provider>
  );
}

// =============================================================================
// Composite Test Wrappers
// =============================================================================

/**
 * AllProviders: Wraps component with all necessary providers for integration tests
 *
 * Use this when testing components that need multiple contexts.
 * For unit tests, prefer the specific provider (TestLayoutProvider, etc.)
 */
export function AllProviders({
  children,
  layoutContext,
}: {
  children: ReactNode;
  layoutContext?: Partial<LayoutContext>;
}) {
  return <TestLayoutProvider context={layoutContext}>{children}</TestLayoutProvider>;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Create a custom render function with default providers
 *
 * USAGE in test file:
 * ```tsx
 * import { render } from '@testing-library/react';
 * import { withTestProviders } from '../utils/testProviders';
 *
 * const customRender = withTestProviders(render);
 *
 * // All renders now have layout context
 * customRender(<CitizenCard {...props} />);
 * ```
 */
export function withTestProviders<T extends typeof import('@testing-library/react').render>(
  renderFn: T
): T {
  const wrappedRender = ((ui: Parameters<T>[0], options?: Parameters<T>[1]) =>
    renderFn(ui, {
      wrapper: ({ children }: { children: ReactNode }) => (
        <TestLayoutProvider>{children}</TestLayoutProvider>
      ),
      ...options,
    })) as T;
  return wrappedRender;
}

export default TestLayoutProvider;
