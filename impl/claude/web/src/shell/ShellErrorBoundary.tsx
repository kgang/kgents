/**
 * ShellErrorBoundary - Graceful Degradation for Shell Components
 *
 * Catches errors in shell components and provides recovery options.
 * Each critical shell layer (ObserverDrawer, NavigationTree, Terminal)
 * should be wrapped to prevent cascading failures.
 *
 * @see spec/protocols/os-shell.md
 *
 * @example
 * ```tsx
 * <ShellErrorBoundary layer="navigation" onError={logToSentry}>
 *   <NavigationTree />
 * </ShellErrorBoundary>
 * ```
 */

import { Component, type ReactNode, type ErrorInfo } from 'react';
import { AlertTriangle, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';

// =============================================================================
// Types
// =============================================================================

export type ShellLayer = 'observer' | 'navigation' | 'terminal' | 'projection' | 'shell';

export interface ShellErrorBoundaryProps {
  /** Which shell layer this boundary protects */
  layer: ShellLayer;
  /** Child components to render */
  children: ReactNode;
  /** Callback when error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo, layer: ShellLayer) => void;
  /** Custom fallback component */
  fallback?: ReactNode;
  /** Whether to show detailed error info (dev mode) */
  showDetails?: boolean;
}

interface ShellErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showStack: boolean;
  retryCount: number;
}

// =============================================================================
// Constants
// =============================================================================

const LAYER_INFO: Record<ShellLayer, { label: string; recoveryHint: string }> = {
  observer: {
    label: 'Observer Drawer',
    recoveryHint: 'Observer context is unavailable. Some features may not work correctly.',
  },
  navigation: {
    label: 'Navigation Tree',
    recoveryHint: 'Navigation is unavailable. Use direct URLs or the terminal instead.',
  },
  terminal: {
    label: 'Terminal',
    recoveryHint: 'Terminal is unavailable. Try refreshing or using the navigation tree.',
  },
  projection: {
    label: 'Content Projection',
    recoveryHint: 'Content failed to load. Try refreshing or navigating to a different page.',
  },
  shell: {
    label: 'Application Shell',
    recoveryHint: 'The application encountered an error. Please refresh the page.',
  },
};

const MAX_RETRIES = 3;

// =============================================================================
// Component
// =============================================================================

/**
 * Error boundary for shell components with recovery options.
 *
 * Features:
 * - Catches render errors in child components
 * - Provides layer-specific error messages
 * - Supports retry with exponential backoff awareness
 * - Shows stack traces in development
 * - Calls optional error callback for logging
 */
export class ShellErrorBoundary extends Component<
  ShellErrorBoundaryProps,
  ShellErrorBoundaryState
> {
  constructor(props: ShellErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showStack: false,
      retryCount: 0,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ShellErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    const { layer, onError } = this.props;

    // Update state with error info
    this.setState({ errorInfo });

    // Call error callback if provided
    if (onError) {
      onError(error, errorInfo, layer);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error(`[ShellErrorBoundary:${layer}]`, error, errorInfo);
    }
  }

  handleRetry = (): void => {
    const { retryCount } = this.state;

    if (retryCount < MAX_RETRIES) {
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: retryCount + 1,
      });
    }
  };

  handleToggleStack = (): void => {
    this.setState((prev) => ({ showStack: !prev.showStack }));
  };

  render(): ReactNode {
    const { children, layer, fallback, showDetails = process.env.NODE_ENV === 'development' } = this.props;
    const { hasError, error, errorInfo, showStack, retryCount } = this.state;

    if (!hasError) {
      return children;
    }

    // Use custom fallback if provided
    if (fallback) {
      return fallback;
    }

    const layerInfo = LAYER_INFO[layer];
    const canRetry = retryCount < MAX_RETRIES;

    // Render error UI
    return (
      <div
        className="flex flex-col items-center justify-center p-4 bg-gray-800/50 border border-red-500/30 rounded-lg m-2"
        role="alert"
        aria-live="assertive"
      >
        {/* Icon and title */}
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          <span className="text-sm font-medium text-red-400">
            {layerInfo.label} Error
          </span>
        </div>

        {/* Recovery hint */}
        <p className="text-xs text-gray-400 text-center mb-3 max-w-xs">
          {layerInfo.recoveryHint}
        </p>

        {/* Retry button */}
        {canRetry && (
          <button
            onClick={this.handleRetry}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-gray-200 text-xs rounded transition-colors mb-2"
          >
            <RefreshCw className="w-3 h-3" />
            Retry ({MAX_RETRIES - retryCount} left)
          </button>
        )}

        {/* Show details toggle (dev mode) */}
        {showDetails && error && (
          <div className="w-full max-w-md mt-2">
            <button
              onClick={this.handleToggleStack}
              className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-400 transition-colors"
            >
              {showStack ? (
                <ChevronUp className="w-3 h-3" />
              ) : (
                <ChevronDown className="w-3 h-3" />
              )}
              {showStack ? 'Hide' : 'Show'} Details
            </button>

            {showStack && (
              <div className="mt-2 p-2 bg-gray-900 rounded text-xs font-mono overflow-auto max-h-32">
                <p className="text-red-400 mb-1">{error.message}</p>
                {errorInfo?.componentStack && (
                  <pre className="text-gray-500 whitespace-pre-wrap text-[10px]">
                    {errorInfo.componentStack}
                  </pre>
                )}
              </div>
            )}
          </div>
        )}

        {/* Retry exhausted message */}
        {!canRetry && (
          <p className="text-xs text-gray-500 mt-2">
            Maximum retries reached. Please refresh the page.
          </p>
        )}
      </div>
    );
  }
}

// =============================================================================
// Convenience Wrappers
// =============================================================================

/**
 * Pre-configured boundary for ObserverDrawer.
 */
export function ObserverErrorBoundary({
  children,
  onError,
}: {
  children: ReactNode;
  onError?: ShellErrorBoundaryProps['onError'];
}) {
  return (
    <ShellErrorBoundary layer="observer" onError={onError}>
      {children}
    </ShellErrorBoundary>
  );
}

/**
 * Pre-configured boundary for NavigationTree.
 */
export function NavigationErrorBoundary({
  children,
  onError,
}: {
  children: ReactNode;
  onError?: ShellErrorBoundaryProps['onError'];
}) {
  return (
    <ShellErrorBoundary layer="navigation" onError={onError}>
      {children}
    </ShellErrorBoundary>
  );
}

/**
 * Pre-configured boundary for Terminal.
 */
export function TerminalErrorBoundary({
  children,
  onError,
}: {
  children: ReactNode;
  onError?: ShellErrorBoundaryProps['onError'];
}) {
  return (
    <ShellErrorBoundary layer="terminal" onError={onError}>
      {children}
    </ShellErrorBoundary>
  );
}

/**
 * Pre-configured boundary for PathProjection content.
 */
export function ProjectionErrorBoundary({
  children,
  onError,
}: {
  children: ReactNode;
  onError?: ShellErrorBoundaryProps['onError'];
}) {
  return (
    <ShellErrorBoundary layer="projection" onError={onError}>
      {children}
    </ShellErrorBoundary>
  );
}

export default ShellErrorBoundary;
