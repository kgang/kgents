import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { SubscriptionTier } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

interface UserState {
  // Auth
  isAuthenticated: boolean;
  userId: string | null;
  email: string | null;
  apiKey: string | null;

  // Subscription
  tier: SubscriptionTier;
  credits: number;
  monthlyUsage: Record<string, number>;

  // Stripe
  stripeCustomerId: string | null;
  subscriptionId: string | null;
  subscriptionStatus: string | null;

  // Actions
  login: (userId: string, apiKey: string, tier?: SubscriptionTier) => void;
  logout: () => void;
  setTier: (tier: SubscriptionTier) => void;
  setCredits: (credits: number) => void;
  spendCredits: (amount: number) => boolean;
  addCredits: (amount: number) => void;
  recordAction: (action: string) => void;
  getMonthlyRemaining: (action: string, limit: number) => number;
  setStripeInfo: (customerId: string, subscriptionId?: string, status?: string) => void;
}

// =============================================================================
// Store
// =============================================================================

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      // Initial state
      isAuthenticated: false,
      userId: null,
      email: null,
      apiKey: null,
      tier: 'TOURIST',
      credits: 0,
      monthlyUsage: {},
      stripeCustomerId: null,
      subscriptionId: null,
      subscriptionStatus: null,

      login: (userId, apiKey, tier = 'TOURIST') => {
        localStorage.setItem('api_key', apiKey);
        set({
          isAuthenticated: true,
          userId,
          apiKey,
          tier,
        });
      },

      logout: () => {
        localStorage.removeItem('api_key');
        set({
          isAuthenticated: false,
          userId: null,
          email: null,
          apiKey: null,
          tier: 'TOURIST',
          credits: 0,
          monthlyUsage: {},
          stripeCustomerId: null,
          subscriptionId: null,
          subscriptionStatus: null,
        });
      },

      setTier: (tier) => set({ tier }),

      setCredits: (credits) => set({ credits }),

      spendCredits: (amount) => {
        const { credits } = get();
        if (credits >= amount) {
          set({ credits: credits - amount });
          return true;
        }
        return false;
      },

      addCredits: (amount) =>
        set((state) => ({ credits: state.credits + amount })),

      recordAction: (action) =>
        set((state) => ({
          monthlyUsage: {
            ...state.monthlyUsage,
            [action]: (state.monthlyUsage[action] || 0) + 1,
          },
        })),

      getMonthlyRemaining: (action, limit) => {
        const { monthlyUsage } = get();
        const used = monthlyUsage[action] || 0;
        return Math.max(0, limit - used);
      },

      setStripeInfo: (customerId, subscriptionId, status) =>
        set({
          stripeCustomerId: customerId,
          subscriptionId: subscriptionId || null,
          subscriptionStatus: status || null,
        }),
    }),
    {
      name: 'agent-town-user',
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        userId: state.userId,
        apiKey: state.apiKey,
        tier: state.tier,
        credits: state.credits,
        stripeCustomerId: state.stripeCustomerId,
        subscriptionId: state.subscriptionId,
      }),
    }
  )
);

// =============================================================================
// Selectors
// =============================================================================

export const selectCanAfford = (credits: number) => (state: UserState) =>
  state.credits >= credits;

export const selectIsLODIncluded = (lod: number) => (state: UserState) => {
  const lodByTier: Record<SubscriptionTier, number[]> = {
    TOURIST: [0, 1],
    RESIDENT: [0, 1, 2, 3],
    CITIZEN: [0, 1, 2, 3, 4],
    FOUNDER: [0, 1, 2, 3, 4, 5],
  };
  return lodByTier[state.tier]?.includes(lod) ?? false;
};

export const selectCanInhabit = () => (state: UserState) =>
  state.tier !== 'TOURIST';

export const selectCanForce = () => (state: UserState) =>
  state.tier === 'CITIZEN' || state.tier === 'FOUNDER';
