import { loadStripe, Stripe } from '@stripe/stripe-js';

// Stripe publishable key from environment
const STRIPE_PUBLISHABLE_KEY = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY;

// Singleton promise for Stripe instance
let stripePromise: Promise<Stripe | null> | null = null;

/**
 * Get the Stripe.js instance.
 * Uses singleton pattern to avoid reloading Stripe on every component mount.
 */
export function getStripe(): Promise<Stripe | null> {
  if (!stripePromise) {
    if (!STRIPE_PUBLISHABLE_KEY) {
      console.warn('[Stripe] Missing VITE_STRIPE_PUBLISHABLE_KEY env var');
      stripePromise = Promise.resolve(null);
    } else {
      stripePromise = loadStripe(STRIPE_PUBLISHABLE_KEY);
    }
  }
  return stripePromise;
}

/**
 * Redirect to Stripe Checkout.
 * @param sessionId - The Checkout Session ID from the backend
 */
export async function redirectToCheckout(sessionId: string): Promise<void> {
  const stripe = await getStripe();
  if (!stripe) {
    throw new Error('Stripe not initialized');
  }

  const { error } = await stripe.redirectToCheckout({ sessionId });
  if (error) {
    console.error('[Stripe] Checkout redirect error:', error);
    throw error;
  }
}

// Subscription tiers
export const SUBSCRIPTION_PRODUCTS = {
  RESIDENT: 'price_resident_monthly',
  CITIZEN: 'price_citizen_monthly',
  FOUNDER: 'price_founder_yearly',
} as const;

// Credit pack products
export const CREDIT_PRODUCTS = {
  SMALL: { priceId: 'price_credits_100', credits: 100, amount: 499 },
  MEDIUM: { priceId: 'price_credits_500', credits: 500, amount: 1999 },
  LARGE: { priceId: 'price_credits_2000', credits: 2000, amount: 4999 },
} as const;

export type CreditPack = keyof typeof CREDIT_PRODUCTS;
