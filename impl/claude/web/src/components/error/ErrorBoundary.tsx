/**
 * ErrorBoundary: Catches render errors in React component tree.
 *
 * Supports reset on route changes via resetKeys prop.
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface ErrorBoundaryProps {
  /** Child components to render */
  children: ReactNode;
  /** Custom fallback UI (optional) */
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
    console.error('[ErrorBoundary] Caught error:', error);
    console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);
    this.props.onError?.(error, errorInfo);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps): void {
    if (this.state.hasError && this.props.resetKeys) {
      const hasKeyChanged = this.props.resetKeys.some(
        (key, index) => key !== prevProps.resetKeys?.[index]
      );
      if (hasKeyChanged) {
        this.reset();
      }
    }
  }

  reset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback !== undefined) {
        return this.props.fallback;
      }

      // Simple error UI
      return (
        <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
          <div className="max-w-md w-full text-center p-8">
            <div className="text-6xl mb-4">😵</div>
            <h2 className="text-xl font-semibold mb-2 text-red-400">Something went wrong</h2>
            <p className="text-gray-400 mb-6">{this.state.error?.message || 'Unknown error'}</p>
            <button
              onClick={this.reset}
              className="px-6 py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export { ErrorBoundary as default };
