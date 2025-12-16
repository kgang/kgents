/**
 * Tests for ErrorBoundary component.
 *
 * @see src/components/error/ErrorBoundary.tsx
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import type { ReactElement } from 'react';
import { ErrorBoundary } from '@/components/error/ErrorBoundary';

// Component that throws an error
function ThrowingComponent({ shouldThrow = true }: { shouldThrow?: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error message');
  }
  return <div>Content rendered successfully</div>;
}

// Component that throws with custom message
function ThrowingWithMessage({ message }: { message: string }): ReactElement {
  throw new Error(message);
}

describe('ErrorBoundary', () => {
  // Suppress console.error during tests (ErrorBoundary logs errors)
  const originalConsoleError = console.error;

  beforeEach(() => {
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  describe('normal rendering', () => {
    it('should render children when no error', () => {
      render(
        <ErrorBoundary>
          <div>Hello World</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('Hello World')).toBeInTheDocument();
    });

    it('should render multiple children', () => {
      render(
        <ErrorBoundary>
          <div>First</div>
          <div>Second</div>
        </ErrorBoundary>
      );

      expect(screen.getByText('First')).toBeInTheDocument();
      expect(screen.getByText('Second')).toBeInTheDocument();
    });
  });

  describe('error catching', () => {
    it('should catch render errors and show fallback', () => {
      render(
        <ErrorBoundary>
          <ThrowingComponent />
        </ErrorBoundary>
      );

      // Should show error message from ElasticPlaceholder
      expect(screen.getByText('Test error message')).toBeInTheDocument();
      // Should show retry button
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    it('should display error message in fallback', () => {
      render(
        <ErrorBoundary>
          <ThrowingWithMessage message="Custom error text" />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom error text')).toBeInTheDocument();
    });

    it('should show default message when error has no message', () => {
      const BadComponent = () => {
        throw new Error('');
      };

      render(
        <ErrorBoundary>
          <BadComponent />
        </ErrorBoundary>
      );

      // ElasticPlaceholder shows "Something went wrong" for empty messages
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });
  });

  describe('onError callback', () => {
    it('should call onError callback when error is caught', () => {
      const onError = vi.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowingComponent />
        </ErrorBoundary>
      );

      expect(onError).toHaveBeenCalledTimes(1);
      expect(onError).toHaveBeenCalledWith(
        expect.any(Error),
        expect.objectContaining({
          componentStack: expect.any(String),
        })
      );
    });

    it('should pass error object to onError', () => {
      const onError = vi.fn();

      render(
        <ErrorBoundary onError={onError}>
          <ThrowingWithMessage message="Specific error" />
        </ErrorBoundary>
      );

      const [error] = onError.mock.calls[0];
      expect(error.message).toBe('Specific error');
    });
  });

  describe('custom fallback', () => {
    it('should render custom fallback when provided', () => {
      render(
        <ErrorBoundary fallback={<div>Custom Error UI</div>}>
          <ThrowingComponent />
        </ErrorBoundary>
      );

      expect(screen.getByText('Custom Error UI')).toBeInTheDocument();
      // Should NOT show default ElasticPlaceholder
      expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument();
    });

    it('should allow null fallback', () => {
      render(
        <ErrorBoundary fallback={null}>
          <ThrowingComponent />
        </ErrorBoundary>
      );

      // Nothing should be rendered
      expect(screen.queryByText('Test error message')).not.toBeInTheDocument();
    });
  });

  describe('reset functionality', () => {
    it('should reset and retry when Try Again is clicked', () => {
      const { rerender } = render(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
      );

      // Should show error
      expect(screen.getByText('Test error message')).toBeInTheDocument();

      // Rerender with non-throwing component to simulate fix
      rerender(
        <ErrorBoundary>
          <ThrowingComponent shouldThrow={false} />
        </ErrorBoundary>
      );

      // Click retry
      fireEvent.click(screen.getByRole('button', { name: /try again/i }));

      // Should now show content
      expect(screen.getByText('Content rendered successfully')).toBeInTheDocument();
    });
  });

  describe('resetKeys', () => {
    it('should reset when resetKeys change', () => {
      const { rerender } = render(
        <ErrorBoundary resetKeys={['/page1']}>
          <ThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
      );

      // Should show error
      expect(screen.getByText('Test error message')).toBeInTheDocument();

      // Change resetKeys (simulating route change) and fix component
      rerender(
        <ErrorBoundary resetKeys={['/page2']}>
          <ThrowingComponent shouldThrow={false} />
        </ErrorBoundary>
      );

      // Should auto-reset and show content
      expect(screen.getByText('Content rendered successfully')).toBeInTheDocument();
    });

    it('should not reset when resetKeys are the same', () => {
      const { rerender } = render(
        <ErrorBoundary resetKeys={['/page1']}>
          <ThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
      );

      // Should show error
      expect(screen.getByText('Test error message')).toBeInTheDocument();

      // Rerender with same keys but different child props
      rerender(
        <ErrorBoundary resetKeys={['/page1']}>
          <div>New content</div>
        </ErrorBoundary>
      );

      // Should still show error (keys didn't change)
      expect(screen.getByText('Test error message')).toBeInTheDocument();
    });

    it('should handle multiple resetKeys', () => {
      const { rerender } = render(
        <ErrorBoundary resetKeys={['key1', 'key2']}>
          <ThrowingComponent shouldThrow={true} />
        </ErrorBoundary>
      );

      expect(screen.getByText('Test error message')).toBeInTheDocument();

      // Change only one key
      rerender(
        <ErrorBoundary resetKeys={['key1', 'key3']}>
          <ThrowingComponent shouldThrow={false} />
        </ErrorBoundary>
      );

      // Should reset because key2 changed to key3
      expect(screen.getByText('Content rendered successfully')).toBeInTheDocument();
    });
  });

  describe('console logging', () => {
    it('should log error to console', () => {
      render(
        <ErrorBoundary>
          <ThrowingComponent />
        </ErrorBoundary>
      );

      expect(console.error).toHaveBeenCalled();
    });
  });
});
