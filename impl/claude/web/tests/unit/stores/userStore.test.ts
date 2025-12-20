import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useUserStore, selectIsLODIncluded, selectCanInhabit, selectCanForce } from '@/stores/userStore';

// Mock localStorage before tests
const localStorageMock = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

describe('userStore', () => {
  beforeEach(() => {
    // Reset store state
    useUserStore.setState({
      userId: null,
      isAuthenticated: false,
      tier: 'TOURIST',
      credits: 100,
      monthlyUsage: {},
      subscriptionStatus: null,
    });
    vi.clearAllMocks();
  });

  describe('authentication', () => {
    it('should login user', () => {
      useUserStore.getState().login('user-123', 'api-key-123', 'RESIDENT');

      expect(useUserStore.getState().userId).toBe('user-123');
      expect(useUserStore.getState().isAuthenticated).toBe(true);
      expect(useUserStore.getState().tier).toBe('RESIDENT');
    });

    it('should login with default tier', () => {
      useUserStore.getState().login('user-123', 'api-key-123');
      expect(useUserStore.getState().tier).toBe('TOURIST');
    });

    it('should logout user', () => {
      useUserStore.getState().login('user-123', 'api-key-123', 'RESIDENT');
      useUserStore.getState().logout();

      expect(useUserStore.getState().userId).toBeNull();
      expect(useUserStore.getState().isAuthenticated).toBe(false);
      expect(useUserStore.getState().tier).toBe('TOURIST');
    });
  });

  describe('tier management', () => {
    it('should set tier', () => {
      useUserStore.getState().setTier('CITIZEN');
      expect(useUserStore.getState().tier).toBe('CITIZEN');
    });

    it('should handle all tiers', () => {
      const tiers = ['TOURIST', 'RESIDENT', 'CITIZEN', 'FOUNDER'] as const;

      tiers.forEach((tier) => {
        useUserStore.getState().setTier(tier);
        expect(useUserStore.getState().tier).toBe(tier);
      });
    });
  });

  describe('credits', () => {
    beforeEach(() => {
      useUserStore.getState().setCredits(100);
    });

    it('should set credits', () => {
      useUserStore.getState().setCredits(500);
      expect(useUserStore.getState().credits).toBe(500);
    });

    it('should add credits', () => {
      useUserStore.getState().addCredits(50);
      expect(useUserStore.getState().credits).toBe(150);
    });

    it('should spend credits successfully', () => {
      const success = useUserStore.getState().spendCredits(30);
      expect(success).toBe(true);
      expect(useUserStore.getState().credits).toBe(70);
    });

    it('should fail to spend more credits than available', () => {
      const success = useUserStore.getState().spendCredits(200);
      expect(success).toBe(false);
      expect(useUserStore.getState().credits).toBe(100);
    });

    it('should spend exact amount of credits', () => {
      const success = useUserStore.getState().spendCredits(100);
      expect(success).toBe(true);
      expect(useUserStore.getState().credits).toBe(0);
    });
  });

  describe('usage tracking', () => {
    it('should record action', () => {
      useUserStore.getState().recordAction('lod3');
      expect(useUserStore.getState().monthlyUsage.lod3).toBe(1);
    });

    it('should increment action count', () => {
      useUserStore.getState().recordAction('lod3');
      useUserStore.getState().recordAction('lod3');
      useUserStore.getState().recordAction('lod3');
      expect(useUserStore.getState().monthlyUsage.lod3).toBe(3);
    });

    it('should track multiple action types', () => {
      useUserStore.getState().recordAction('lod3');
      useUserStore.getState().recordAction('lod4');
      useUserStore.getState().recordAction('inhabit');

      expect(useUserStore.getState().monthlyUsage.lod3).toBe(1);
      expect(useUserStore.getState().monthlyUsage.lod4).toBe(1);
      expect(useUserStore.getState().monthlyUsage.inhabit).toBe(1);
    });
  });

  describe('stripe info', () => {
    it('should set stripe info', () => {
      useUserStore.getState().setStripeInfo('cus_123', 'sub_456', 'active');
      expect(useUserStore.getState().stripeCustomerId).toBe('cus_123');
      expect(useUserStore.getState().subscriptionId).toBe('sub_456');
      expect(useUserStore.getState().subscriptionStatus).toBe('active');
    });

    it('should set stripe customer without subscription', () => {
      useUserStore.getState().setStripeInfo('cus_123');
      expect(useUserStore.getState().stripeCustomerId).toBe('cus_123');
      expect(useUserStore.getState().subscriptionId).toBeNull();
    });
  });

  describe('selectors', () => {
    describe('selectIsLODIncluded', () => {
      it('should return true for LOD 0-1 for TOURIST', () => {
        useUserStore.getState().setTier('TOURIST');

        expect(selectIsLODIncluded(0)(useUserStore.getState())).toBe(true);
        expect(selectIsLODIncluded(1)(useUserStore.getState())).toBe(true);
        expect(selectIsLODIncluded(2)(useUserStore.getState())).toBe(false);
      });

      it('should return true for LOD 0-3 for RESIDENT', () => {
        useUserStore.getState().setTier('RESIDENT');

        expect(selectIsLODIncluded(2)(useUserStore.getState())).toBe(true);
        expect(selectIsLODIncluded(3)(useUserStore.getState())).toBe(true);
        expect(selectIsLODIncluded(4)(useUserStore.getState())).toBe(false);
      });

      it('should return true for LOD 0-4 for CITIZEN', () => {
        useUserStore.getState().setTier('CITIZEN');

        expect(selectIsLODIncluded(4)(useUserStore.getState())).toBe(true);
        expect(selectIsLODIncluded(5)(useUserStore.getState())).toBe(false);
      });

      it('should return true for LOD 0-5 for FOUNDER', () => {
        useUserStore.getState().setTier('FOUNDER');

        expect(selectIsLODIncluded(5)(useUserStore.getState())).toBe(true);
      });
    });

    describe('selectCanInhabit', () => {
      it('should return false for TOURIST', () => {
        useUserStore.getState().setTier('TOURIST');
        expect(selectCanInhabit()(useUserStore.getState())).toBe(false);
      });

      it('should return true for RESIDENT and above', () => {
        ['RESIDENT', 'CITIZEN', 'FOUNDER'].forEach((tier) => {
          useUserStore.getState().setTier(tier as any);
          expect(selectCanInhabit()(useUserStore.getState())).toBe(true);
        });
      });
    });

    describe('selectCanForce', () => {
      it('should return false for TOURIST and RESIDENT', () => {
        ['TOURIST', 'RESIDENT'].forEach((tier) => {
          useUserStore.getState().setTier(tier as any);
          expect(selectCanForce()(useUserStore.getState())).toBe(false);
        });
      });

      it('should return true for CITIZEN and FOUNDER', () => {
        ['CITIZEN', 'FOUNDER'].forEach((tier) => {
          useUserStore.getState().setTier(tier as any);
          expect(selectCanForce()(useUserStore.getState())).toBe(true);
        });
      });
    });
  });
});
