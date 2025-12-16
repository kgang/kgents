/**
 * Tests for Toast and ToastContainer components.
 *
 * @see src/components/feedback/Toast.tsx
 * @see src/components/feedback/ToastContainer.tsx
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { Toast, type Notification } from '@/components/feedback/Toast';
import { ToastContainer } from '@/components/feedback/ToastContainer';
import { useUIStore } from '@/stores/uiStore';

// =============================================================================
// Toast Component Tests
// =============================================================================

describe('Toast', () => {
  const mockDismiss = vi.fn();

  const baseNotification: Notification = {
    id: 'test-1',
    type: 'info',
    title: 'Test Title',
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('rendering', () => {
    it('should render title', () => {
      render(<Toast notification={baseNotification} onDismiss={mockDismiss} />);
      expect(screen.getByText('Test Title')).toBeInTheDocument();
    });

    it('should render message when provided', () => {
      const notification: Notification = {
        ...baseNotification,
        message: 'Additional details',
      };
      render(<Toast notification={notification} onDismiss={mockDismiss} />);
      expect(screen.getByText('Additional details')).toBeInTheDocument();
    });

    it('should not render message when not provided', () => {
      render(<Toast notification={baseNotification} onDismiss={mockDismiss} />);
      expect(screen.queryByText('Additional details')).not.toBeInTheDocument();
    });

    it('should have alert role for accessibility', () => {
      render(<Toast notification={baseNotification} onDismiss={mockDismiss} />);
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });

  describe('notification types', () => {
    it.each([
      ['info', '💡'],
      ['success', '✅'],
      ['warning', '⚠️'],
      ['error', '🚫'],
    ] as const)('should show %s emoji for %s type', (type, emoji) => {
      const notification: Notification = { ...baseNotification, type };
      render(<Toast notification={notification} onDismiss={mockDismiss} />);
      expect(screen.getByText(emoji)).toBeInTheDocument();
    });
  });

  describe('dismiss functionality', () => {
    it('should call onDismiss when dismiss button clicked', () => {
      render(<Toast notification={baseNotification} onDismiss={mockDismiss} />);

      const dismissButton = screen.getByRole('button', { name: /dismiss/i });
      fireEvent.click(dismissButton);

      expect(mockDismiss).toHaveBeenCalledTimes(1);
    });

    it('should call onDismiss when Escape key pressed', () => {
      render(<Toast notification={baseNotification} onDismiss={mockDismiss} />);

      const alert = screen.getByRole('alert');
      fireEvent.keyDown(alert, { key: 'Escape' });

      expect(mockDismiss).toHaveBeenCalledTimes(1);
    });
  });

  describe('auto-dismiss', () => {
    it('should auto-dismiss after duration', () => {
      const notification: Notification = {
        ...baseNotification,
        duration: 3000,
      };
      render(<Toast notification={notification} onDismiss={mockDismiss} />);

      expect(mockDismiss).not.toHaveBeenCalled();

      act(() => {
        vi.advanceTimersByTime(3000);
      });

      expect(mockDismiss).toHaveBeenCalledTimes(1);
    });

    it('should not auto-dismiss when duration is 0', () => {
      const notification: Notification = {
        ...baseNotification,
        duration: 0,
      };
      render(<Toast notification={notification} onDismiss={mockDismiss} />);

      act(() => {
        vi.advanceTimersByTime(10000);
      });

      expect(mockDismiss).not.toHaveBeenCalled();
    });

    it('should not auto-dismiss when duration is undefined', () => {
      render(<Toast notification={baseNotification} onDismiss={mockDismiss} />);

      act(() => {
        vi.advanceTimersByTime(10000);
      });

      expect(mockDismiss).not.toHaveBeenCalled();
    });

    it('should clear timer on unmount', () => {
      const notification: Notification = {
        ...baseNotification,
        duration: 3000,
      };
      const { unmount } = render(
        <Toast notification={notification} onDismiss={mockDismiss} />
      );

      unmount();

      act(() => {
        vi.advanceTimersByTime(3000);
      });

      // Should not be called because component unmounted
      expect(mockDismiss).not.toHaveBeenCalled();
    });
  });
});

// =============================================================================
// ToastContainer Component Tests
// =============================================================================

describe('ToastContainer', () => {
  beforeEach(() => {
    // Reset store state
    useUIStore.setState({ notifications: [] });
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('rendering', () => {
    it('should render nothing when no notifications', () => {
      const { container } = render(<ToastContainer />);
      expect(container.firstChild).toBeNull();
    });

    it('should render notifications from store', () => {
      useUIStore.getState().addNotification({
        type: 'success',
        title: 'First notification',
      });
      useUIStore.getState().addNotification({
        type: 'error',
        title: 'Second notification',
      });

      render(<ToastContainer />);

      expect(screen.getByText('First notification')).toBeInTheDocument();
      expect(screen.getByText('Second notification')).toBeInTheDocument();
    });

    it('should have aria-live for accessibility', () => {
      useUIStore.getState().addNotification({
        type: 'info',
        title: 'Test',
      });

      render(<ToastContainer />);

      expect(screen.getByLabelText('Notifications')).toHaveAttribute(
        'aria-live',
        'polite'
      );
    });
  });

  describe('notification management', () => {
    it('should remove notification when dismissed', () => {
      useUIStore.getState().addNotification({
        type: 'info',
        title: 'Dismissable',
      });

      render(<ToastContainer />);
      expect(screen.getByText('Dismissable')).toBeInTheDocument();

      const dismissButton = screen.getByRole('button', { name: /dismiss/i });
      fireEvent.click(dismissButton);

      expect(screen.queryByText('Dismissable')).not.toBeInTheDocument();
    });

    it('should auto-remove notification after duration', () => {
      useUIStore.getState().addNotification({
        type: 'success',
        title: 'Auto-dismiss',
        duration: 3000,
      });

      render(<ToastContainer />);
      expect(screen.getByText('Auto-dismiss')).toBeInTheDocument();

      act(() => {
        vi.advanceTimersByTime(3000);
      });

      expect(screen.queryByText('Auto-dismiss')).not.toBeInTheDocument();
    });
  });

  describe('helper functions', () => {
    it('showSuccess should add success notification', async () => {
      const { showSuccess } = await import('@/stores/uiStore');
      showSuccess('Success!', 'It worked.');

      render(<ToastContainer />);

      expect(screen.getByText('Success!')).toBeInTheDocument();
      expect(screen.getByText('It worked.')).toBeInTheDocument();
      expect(screen.getByText('✅')).toBeInTheDocument();
    });

    it('showError should add error notification', async () => {
      const { showError } = await import('@/stores/uiStore');
      showError('Error!', 'Something broke.');

      render(<ToastContainer />);

      expect(screen.getByText('Error!')).toBeInTheDocument();
      expect(screen.getByText('Something broke.')).toBeInTheDocument();
      expect(screen.getByText('🚫')).toBeInTheDocument();
    });

    it('showInfo should add info notification', async () => {
      const { showInfo } = await import('@/stores/uiStore');
      showInfo('FYI', 'Just so you know.');

      render(<ToastContainer />);

      expect(screen.getByText('FYI')).toBeInTheDocument();
      expect(screen.getByText('Just so you know.')).toBeInTheDocument();
      expect(screen.getByText('💡')).toBeInTheDocument();
    });
  });
});
