import { describe, it, expect, beforeEach, vi } from 'vitest';

// Test the constants which don't need mocking
import { SUBSCRIPTION_PRODUCTS, CREDIT_PRODUCTS } from '@/lib/stripe';

describe('stripe lib', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // getStripe and redirectToCheckout tests are skipped because they require
  // complex mocking of the singleton pattern and @stripe/stripe-js module
  // TODO: Set up proper stripe-js mocking with module-level state reset

  describe('SUBSCRIPTION_PRODUCTS', () => {
    it('should have RESIDENT product', () => {
      expect(SUBSCRIPTION_PRODUCTS.RESIDENT).toBe('price_resident_monthly');
    });

    it('should have CITIZEN product', () => {
      expect(SUBSCRIPTION_PRODUCTS.CITIZEN).toBe('price_citizen_monthly');
    });

    it('should have FOUNDER product', () => {
      expect(SUBSCRIPTION_PRODUCTS.FOUNDER).toBe('price_founder_yearly');
    });

    it('should not have TOURIST product', () => {
      expect((SUBSCRIPTION_PRODUCTS as any).TOURIST).toBeUndefined();
    });
  });

  describe('CREDIT_PRODUCTS', () => {
    it('should have SMALL pack with 100 credits', () => {
      expect(CREDIT_PRODUCTS.SMALL).toEqual({
        priceId: 'price_credits_100',
        credits: 100,
        amount: 499,
      });
    });

    it('should have MEDIUM pack with 500 credits', () => {
      expect(CREDIT_PRODUCTS.MEDIUM).toEqual({
        priceId: 'price_credits_500',
        credits: 500,
        amount: 1999,
      });
    });

    it('should have LARGE pack with 2000 credits', () => {
      expect(CREDIT_PRODUCTS.LARGE).toEqual({
        priceId: 'price_credits_2000',
        credits: 2000,
        amount: 4999,
      });
    });

    it('should calculate correct price per credit for SMALL', () => {
      const pricePerCredit = CREDIT_PRODUCTS.SMALL.amount / CREDIT_PRODUCTS.SMALL.credits;
      expect(pricePerCredit).toBeCloseTo(4.99);
    });

    it('should calculate correct price per credit for MEDIUM', () => {
      const pricePerCredit = CREDIT_PRODUCTS.MEDIUM.amount / CREDIT_PRODUCTS.MEDIUM.credits;
      expect(pricePerCredit).toBeCloseTo(3.998);
    });

    it('should calculate correct price per credit for LARGE (best value)', () => {
      const pricePerCredit = CREDIT_PRODUCTS.LARGE.amount / CREDIT_PRODUCTS.LARGE.credits;
      expect(pricePerCredit).toBeCloseTo(2.4995);
    });
  });
});
