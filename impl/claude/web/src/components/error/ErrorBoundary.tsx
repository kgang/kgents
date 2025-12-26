/**
 * ErrorBoundary: Catches render errors in React component tree.
 *
 * Neutral error messaging — clear and direct.
 * Supports reset on route changes via resetKeys prop.
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
import { AlertCircle } from 'lucide-react';

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
 * Error boundary that catches render errors and displays a neutral fallback.
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

      // Neutral error UI — Lucide icon, not emoji
      return (
        <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-gray-900">
          <div className="max-w-md w-full text-center p-8">
            <div className="flex justify-center mb-4">
              <AlertCircle className="w-16 h-16 text-gray-500" strokeWidth={1.5} />
            </div>
            <h2 className="text-xl font-semibold mb-2 text-white">Component Error</h2>
            <p className="text-gray-400 mb-6">{this.state.error?.message || 'An error occurred'}</p>
            <button
              onClick={this.reset}
              className="px-6 py-2 rounded-lg font-medium transition-colors text-white"
              style={{
                background: 'var(--color-life-sage)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--color-life-mint)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'var(--color-life-sage)';
              }}
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
