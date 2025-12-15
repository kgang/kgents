import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useUIStore, showSuccess, showError, showInfo } from '@/stores/uiStore';

// Mock crypto.randomUUID
vi.stubGlobal('crypto', {
  randomUUID: vi.fn(() => 'test-uuid-' + Math.random().toString(36).slice(2)),
});

describe('uiStore', () => {
  beforeEach(() => {
    // Reset store state
    useUIStore.setState({
      isCitizenPanelOpen: false,
      isEventFeedOpen: true,
      activeModal: null,
      modalData: {},
      notifications: [],
      isLoading: false,
      loadingMessage: null,
    });
  });

  describe('panels', () => {
    it('should open citizen panel', () => {
      useUIStore.getState().openCitizenPanel();
      expect(useUIStore.getState().isCitizenPanelOpen).toBe(true);
    });

    it('should close citizen panel', () => {
      useUIStore.getState().openCitizenPanel();
      useUIStore.getState().closeCitizenPanel();
      expect(useUIStore.getState().isCitizenPanelOpen).toBe(false);
    });

    it('should toggle citizen panel', () => {
      expect(useUIStore.getState().isCitizenPanelOpen).toBe(false);
      useUIStore.getState().toggleCitizenPanel();
      expect(useUIStore.getState().isCitizenPanelOpen).toBe(true);
      useUIStore.getState().toggleCitizenPanel();
      expect(useUIStore.getState().isCitizenPanelOpen).toBe(false);
    });

    it('should open event feed', () => {
      useUIStore.getState().closeEventFeed();
      useUIStore.getState().openEventFeed();
      expect(useUIStore.getState().isEventFeedOpen).toBe(true);
    });

    it('should close event feed', () => {
      useUIStore.getState().closeEventFeed();
      expect(useUIStore.getState().isEventFeedOpen).toBe(false);
    });

    it('should toggle event feed', () => {
      expect(useUIStore.getState().isEventFeedOpen).toBe(true);
      useUIStore.getState().toggleEventFeed();
      expect(useUIStore.getState().isEventFeedOpen).toBe(false);
      useUIStore.getState().toggleEventFeed();
      expect(useUIStore.getState().isEventFeedOpen).toBe(true);
    });
  });

  describe('modals', () => {
    it('should open modal with type', () => {
      useUIStore.getState().openModal('upgrade');
      expect(useUIStore.getState().activeModal).toBe('upgrade');
    });

    it('should open modal with data', () => {
      useUIStore.getState().openModal('upgrade', { requiredCredits: 100 });
      expect(useUIStore.getState().activeModal).toBe('upgrade');
      expect(useUIStore.getState().modalData).toEqual({ requiredCredits: 100 });
    });

    it('should close modal and clear data', () => {
      useUIStore.getState().openModal('upgrade', { test: true });
      useUIStore.getState().closeModal();
      expect(useUIStore.getState().activeModal).toBeNull();
      expect(useUIStore.getState().modalData).toEqual({});
    });

    it('should handle all modal types', () => {
      const modalTypes = ['upgrade', 'checkout', 'inhabit-consent', 'error'] as const;

      modalTypes.forEach((type) => {
        useUIStore.getState().openModal(type);
        expect(useUIStore.getState().activeModal).toBe(type);
        useUIStore.getState().closeModal();
      });
    });
  });

  describe('notifications', () => {
    it('should add notification', () => {
      useUIStore.getState().addNotification({
        type: 'info',
        title: 'Test',
        message: 'Test message',
      });

      const notifications = useUIStore.getState().notifications;
      expect(notifications).toHaveLength(1);
      expect(notifications[0].title).toBe('Test');
      expect(notifications[0].type).toBe('info');
    });

    it('should generate unique id for notifications', () => {
      useUIStore.getState().addNotification({ type: 'info', title: 'Test 1' });
      useUIStore.getState().addNotification({ type: 'info', title: 'Test 2' });

      const notifications = useUIStore.getState().notifications;
      expect(notifications[0].id).not.toBe(notifications[1].id);
    });

    it('should remove notification by id', () => {
      useUIStore.getState().addNotification({ type: 'info', title: 'Test' });
      const notificationId = useUIStore.getState().notifications[0].id;

      useUIStore.getState().removeNotification(notificationId);
      expect(useUIStore.getState().notifications).toHaveLength(0);
    });

    it('should preserve other notifications when removing one', () => {
      useUIStore.getState().addNotification({ type: 'info', title: 'Test 1' });
      useUIStore.getState().addNotification({ type: 'success', title: 'Test 2' });

      const firstId = useUIStore.getState().notifications[0].id;
      useUIStore.getState().removeNotification(firstId);

      expect(useUIStore.getState().notifications).toHaveLength(1);
      expect(useUIStore.getState().notifications[0].title).toBe('Test 2');
    });
  });

  describe('loading state', () => {
    it('should set loading state', () => {
      useUIStore.getState().setLoading(true);
      expect(useUIStore.getState().isLoading).toBe(true);
    });

    it('should set loading with message', () => {
      useUIStore.getState().setLoading(true, 'Loading data...');
      expect(useUIStore.getState().isLoading).toBe(true);
      expect(useUIStore.getState().loadingMessage).toBe('Loading data...');
    });

    it('should clear loading message when false', () => {
      useUIStore.getState().setLoading(true, 'Loading...');
      useUIStore.getState().setLoading(false);
      expect(useUIStore.getState().isLoading).toBe(false);
      expect(useUIStore.getState().loadingMessage).toBeNull();
    });
  });

  describe('notification helpers', () => {
    it('showSuccess should add success notification', () => {
      showSuccess('Success!', 'Operation completed');

      const notifications = useUIStore.getState().notifications;
      expect(notifications).toHaveLength(1);
      expect(notifications[0].type).toBe('success');
      expect(notifications[0].title).toBe('Success!');
      expect(notifications[0].duration).toBe(3000);
    });

    it('showError should add error notification', () => {
      showError('Error!', 'Something went wrong');

      const notifications = useUIStore.getState().notifications;
      expect(notifications).toHaveLength(1);
      expect(notifications[0].type).toBe('error');
      expect(notifications[0].title).toBe('Error!');
      expect(notifications[0].duration).toBe(5000);
    });

    it('showInfo should add info notification', () => {
      showInfo('Info', 'Just FYI');

      const notifications = useUIStore.getState().notifications;
      expect(notifications).toHaveLength(1);
      expect(notifications[0].type).toBe('info');
      expect(notifications[0].title).toBe('Info');
      expect(notifications[0].duration).toBe(3000);
    });
  });
});
