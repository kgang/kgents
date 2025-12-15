import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock the API client and stripe redirect first
vi.mock('@/api/client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

vi.mock('@/lib/stripe', () => ({
  SUBSCRIPTION_PRODUCTS: {
    RESIDENT: 'price_resident_monthly',
    CITIZEN: 'price_citizen_monthly',
    FOUNDER: 'price_founder_yearly',
  },
  CREDIT_PRODUCTS: {
    SMALL: { priceId: 'price_credits_100', credits: 100, amount: 499 },
    MEDIUM: { priceId: 'price_credits_500', credits: 500, amount: 1999 },
    LARGE: { priceId: 'price_credits_2000', credits: 2000, amount: 4999 },
  },
  redirectToCheckout: vi.fn(),
}));

// Import after mocking
import { apiClient } from '@/api/client';
import { redirectToCheckout } from '@/lib/stripe';
import {
  createSubscriptionCheckout,
  createCreditCheckout,
  getSubscriptionStatus,
  getCreditBalance,
  getUsageHistory,
  verifyCheckoutSession,
} from '@/api/payments';

describe('payments API', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock window.location.origin
    Object.defineProperty(window, 'location', {
      value: { origin: 'http://localhost:3000' },
      writable: true,
    });
  });

  describe('createSubscriptionCheckout', () => {
    it('should call API with correct parameters', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { session_id: 'cs_123' } });
      vi.mocked(redirectToCheckout).mockResolvedValueOnce(undefined);

      await createSubscriptionCheckout('CITIZEN', 'user-123');

      expect(apiClient.post).toHaveBeenCalledWith('/api/checkout/subscription', {
        user_id: 'user-123',
        price_id: 'price_citizen_monthly',
        tier: 'CITIZEN',
        success_url: 'http://localhost:3000/checkout/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url: 'http://localhost:3000/dashboard?checkout=canceled',
      });
    });

    it('should redirect to Stripe checkout', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { session_id: 'cs_123' } });
      vi.mocked(redirectToCheckout).mockResolvedValueOnce(undefined);

      await createSubscriptionCheckout('RESIDENT', 'user-123');

      expect(redirectToCheckout).toHaveBeenCalledWith('cs_123');
    });

    it('should throw for invalid tier', async () => {
      await expect(
        createSubscriptionCheckout('INVALID' as any, 'user-123')
      ).rejects.toThrow('Unknown subscription tier: INVALID');
    });

    it('should handle RESIDENT tier', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { session_id: 'cs_123' } });
      vi.mocked(redirectToCheckout).mockResolvedValueOnce(undefined);

      await createSubscriptionCheckout('RESIDENT', 'user-123');

      expect(apiClient.post).toHaveBeenCalledWith('/api/checkout/subscription', expect.objectContaining({
        price_id: 'price_resident_monthly',
        tier: 'RESIDENT',
      }));
    });

    it('should handle FOUNDER tier', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { session_id: 'cs_123' } });
      vi.mocked(redirectToCheckout).mockResolvedValueOnce(undefined);

      await createSubscriptionCheckout('FOUNDER', 'user-123');

      expect(apiClient.post).toHaveBeenCalledWith('/api/checkout/subscription', expect.objectContaining({
        price_id: 'price_founder_yearly',
        tier: 'FOUNDER',
      }));
    });
  });

  describe('createCreditCheckout', () => {
    it('should call API with correct parameters', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { session_id: 'cs_123' } });
      vi.mocked(redirectToCheckout).mockResolvedValueOnce(undefined);

      await createCreditCheckout('MEDIUM', 'user-123');

      expect(apiClient.post).toHaveBeenCalledWith('/api/checkout/credits', {
        user_id: 'user-123',
        price_id: 'price_credits_500',
        credits: 500,
        success_url: 'http://localhost:3000/checkout/success?session_id={CHECKOUT_SESSION_ID}&credits=500',
        cancel_url: 'http://localhost:3000/dashboard?checkout=canceled',
      });
    });

    it('should redirect to Stripe checkout', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { session_id: 'cs_456' } });
      vi.mocked(redirectToCheckout).mockResolvedValueOnce(undefined);

      await createCreditCheckout('SMALL', 'user-123');

      expect(redirectToCheckout).toHaveBeenCalledWith('cs_456');
    });

    it('should throw for invalid pack', async () => {
      await expect(
        createCreditCheckout('INVALID' as any, 'user-123')
      ).rejects.toThrow('Unknown credit pack: INVALID');
    });

    it('should include credits in success URL', async () => {
      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: { session_id: 'cs_123' } });
      vi.mocked(redirectToCheckout).mockResolvedValueOnce(undefined);

      await createCreditCheckout('LARGE', 'user-123');

      expect(apiClient.post).toHaveBeenCalledWith('/api/checkout/credits', expect.objectContaining({
        success_url: expect.stringContaining('credits=2000'),
      }));
    });
  });

  describe('getSubscriptionStatus', () => {
    it('should fetch subscription status', async () => {
      const mockResponse = {
        tier: 'CITIZEN',
        status: 'active',
        current_period_end: '2024-02-01T00:00:00Z',
        cancel_at_period_end: false,
      };
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

      const result = await getSubscriptionStatus('user-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/subscription/user-123');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getCreditBalance', () => {
    it('should fetch credit balance', async () => {
      const mockResponse = {
        credits: 500,
        lifetime_credits: 2000,
      };
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

      const result = await getCreditBalance('user-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/credits/user-123');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getUsageHistory', () => {
    it('should fetch usage history with default period', async () => {
      const mockResponse = {
        actions: [
          { action_type: 'lod3', count: 10, total_cost: 100 },
        ],
        total_credits_used: 100,
        period_start: '2024-01-01',
        period_end: '2024-01-31',
      };
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

      const result = await getUsageHistory('user-123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/usage/user-123?period_days=30');
      expect(result).toEqual(mockResponse);
    });

    it('should fetch usage history with custom period', async () => {
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: {} });

      await getUsageHistory('user-123', 7);

      expect(apiClient.get).toHaveBeenCalledWith('/api/usage/user-123?period_days=7');
    });
  });

  describe('verifyCheckoutSession', () => {
    it('should verify subscription checkout', async () => {
      const mockResponse = {
        success: true,
        type: 'subscription',
        tier: 'CITIZEN',
      };
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

      const result = await verifyCheckoutSession('cs_123');

      expect(apiClient.get).toHaveBeenCalledWith('/api/checkout/verify/cs_123');
      expect(result).toEqual(mockResponse);
    });

    it('should verify credit checkout', async () => {
      const mockResponse = {
        success: true,
        type: 'credits',
        credits: 500,
      };
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

      const result = await verifyCheckoutSession('cs_456');

      expect(result.type).toBe('credits');
      expect(result.credits).toBe(500);
    });

    it('should return failure for invalid session', async () => {
      const mockResponse = {
        success: false,
        type: 'subscription',
      };
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockResponse });

      const result = await verifyCheckoutSession('invalid');

      expect(result.success).toBe(false);
    });
  });
});
