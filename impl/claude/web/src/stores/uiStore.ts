import { create } from 'zustand';

// =============================================================================
// Types
// =============================================================================

type ModalType = 'upgrade' | 'checkout' | 'inhabit-consent' | 'error' | null;

interface UIState {
  // Panels
  isCitizenPanelOpen: boolean;
  isEventFeedOpen: boolean;

  // Modals
  activeModal: ModalType;
  modalData: Record<string, unknown>;

  // Notifications
  notifications: Notification[];

  // Loading states
  isLoading: boolean;
  loadingMessage: string | null;

  // Actions
  openCitizenPanel: () => void;
  closeCitizenPanel: () => void;
  toggleCitizenPanel: () => void;
  openEventFeed: () => void;
  closeEventFeed: () => void;
  toggleEventFeed: () => void;
  openModal: (type: ModalType, data?: Record<string, unknown>) => void;
  closeModal: () => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  setLoading: (loading: boolean, message?: string) => void;
}

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  duration?: number;
}

// =============================================================================
// Store
// =============================================================================

export const useUIStore = create<UIState>((set) => ({
  // Initial state
  isCitizenPanelOpen: false,
  isEventFeedOpen: true,
  activeModal: null,
  modalData: {},
  notifications: [],
  isLoading: false,
  loadingMessage: null,

  // Panel actions
  openCitizenPanel: () => set({ isCitizenPanelOpen: true }),
  closeCitizenPanel: () => set({ isCitizenPanelOpen: false }),
  toggleCitizenPanel: () => set((state) => ({ isCitizenPanelOpen: !state.isCitizenPanelOpen })),

  openEventFeed: () => set({ isEventFeedOpen: true }),
  closeEventFeed: () => set({ isEventFeedOpen: false }),
  toggleEventFeed: () => set((state) => ({ isEventFeedOpen: !state.isEventFeedOpen })),

  // Modal actions
  openModal: (type, data = {}) => set({ activeModal: type, modalData: data }),
  closeModal: () => set({ activeModal: null, modalData: {} }),

  // Notification actions
  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        { ...notification, id: crypto.randomUUID() },
      ],
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),

  // Loading actions
  setLoading: (loading, message) =>
    set({ isLoading: loading, loadingMessage: message ?? null }),
}));

// =============================================================================
// Notification helpers
// =============================================================================

export function showSuccess(title: string, message?: string) {
  useUIStore.getState().addNotification({
    type: 'success',
    title,
    message,
    duration: 3000,
  });
}

export function showError(title: string, message?: string) {
  useUIStore.getState().addNotification({
    type: 'error',
    title,
    message,
    duration: 5000,
  });
}

export function showInfo(title: string, message?: string) {
  useUIStore.getState().addNotification({
    type: 'info',
    title,
    message,
    duration: 3000,
  });
}
