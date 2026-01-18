import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  resetKeys?: unknown[];
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary - Required React infrastructure.
 * Catches errors in child components and displays fallback.
 */
export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  public componentDidUpdate(prevProps: Props) {
    if (this.state.hasError && prevProps.resetKeys !== this.props.resetKeys) {
      this.setState({ hasError: false, error: null });
    }
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0a0a0c] text-[#8a8a94] p-4 font-mono text-[12px]">
          <h1 className="text-[#c4a77d] text-[14px] mb-2">Error</h1>
          <pre className="text-[#5a5a64] text-[10px] overflow-auto">
            {this.state.error?.message}
          </pre>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4 px-2 py-1 border border-[#28282f] hover:border-[#3a3a44]"
          >
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
