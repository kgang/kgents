/**
 * ErrorBoundary: Catches render errors in React component tree.
 *
 * Uses ElasticPlaceholder for consistent error display with personality.
 * Supports reset on route changes via resetKeys prop.
 *
 * @see plans/web-refactor/defensive-lifecycle.md
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
import { ElasticPlaceholder } from '@/components/elastic/ElasticPlaceholder';

// =============================================================================
// Types
// =============================================================================

export interface ErrorBoundaryProps {
  /** Child components to render */
  children: ReactNode;
  /** Custom fallback UI (optional, defaults to ElasticPlaceholder) */
  fallback?: ReactNode;
  /** Callback when error is caught (for logging/telemetry) */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** Reset boundary when any of these values change (e.g., route path) */
  resetKeys?: unknown[];
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

// =============================================================================
// Component
// =============================================================================

/**
 * Error boundary that catches render errors and displays a friendly fallback.
 *
 * @example
 * ```tsx
 * // Wrap at app level with route-based reset
 * <ErrorBoundary resetKeys={[location.pathname]}>
 *   <App />
 * </ErrorBoundary>
 *
 * // Wrap specific section with custom fallback
 * <ErrorBoundary fallback={<CustomError />}>
 *   <RiskyComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log to console for debugging
    console.error('[ErrorBoundary] Caught error:', error);
    console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);

    // Call optional error handler (for telemetry)
    this.props.onError?.(error, errorInfo);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps): void {
    // Reset error state when resetKeys change (e.g., on route change)
    if (this.state.hasError && this.props.resetKeys) {
      const hasKeyChanged = this.props.resetKeys.some(
        (key, index) => key !== prevProps.resetKeys?.[index]
      );
      if (hasKeyChanged) {
        this.reset();
      }
    }
  }

  /**
   * Reset the error boundary to try rendering children again.
   */
  reset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback !== undefined) {
        return this.props.fallback;
      }

      // Default: full-page error with ElasticPlaceholder
      return (
        <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
          <div className="max-w-md w-full">
            <ElasticPlaceholder
              state="error"
              error={this.state.error?.message || 'Something went wrong'}
              onRetry={this.reset}
            />
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// =============================================================================
// Hook for programmatic reset (optional)
// =============================================================================

/**
 * Context for accessing error boundary reset function.
 * Use with ErrorBoundaryProvider for nested reset capability.
 */
export { ErrorBoundary as default };
