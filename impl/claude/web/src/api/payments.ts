import { apiClient } from './client';
import { redirectToCheckout, SUBSCRIPTION_PRODUCTS, CREDIT_PRODUCTS, CreditPack } from '@/lib/stripe';
import type { SubscriptionTier } from './types';

// =============================================================================
// Types
// =============================================================================

interface CheckoutSessionResponse {
  session_id: string;
  url: string;
}

interface SubscriptionStatusResponse {
  tier: SubscriptionTier;
  status: 'active' | 'past_due' | 'canceled' | 'trialing' | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
}

interface CreditBalanceResponse {
  credits: number;
  lifetime_credits: number;
}

interface UsageResponse {
  actions: {
    action_type: string;
    count: number;
    total_cost: number;
  }[];
  total_credits_used: number;
  period_start: string;
  period_end: string;
}

// =============================================================================
// Subscription Checkout
// =============================================================================

/**
 * Create a subscription checkout session and redirect to Stripe.
 */
export async function createSubscriptionCheckout(
  tier: Exclude<SubscriptionTier, 'TOURIST'>,
  userId: string
): Promise<void> {
  const priceId = SUBSCRIPTION_PRODUCTS[tier];
  if (!priceId) {
    throw new Error(`Unknown subscription tier: ${tier}`);
  }

  const response = await apiClient.post<CheckoutSessionResponse>('/api/checkout/subscription', {
    user_id: userId,
    price_id: priceId,
    tier,
    success_url: `${window.location.origin}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${window.location.origin}/dashboard?checkout=canceled`,
  });

  await redirectToCheckout(response.data.session_id);
}

/**
 * Create a customer portal session for subscription management.
 */
export async function createPortalSession(userId: string): Promise<string> {
  const response = await apiClient.post<{ url: string }>('/api/checkout/portal', {
    user_id: userId,
    return_url: `${window.location.origin}/dashboard`,
  });
  return response.data.url;
}

// =============================================================================
// Credit Purchases
// =============================================================================

/**
 * Create a credit pack checkout session and redirect to Stripe.
 */
export async function createCreditCheckout(
  pack: CreditPack,
  userId: string
): Promise<void> {
  const product = CREDIT_PRODUCTS[pack];
  if (!product) {
    throw new Error(`Unknown credit pack: ${pack}`);
  }

  const response = await apiClient.post<CheckoutSessionResponse>('/api/checkout/credits', {
    user_id: userId,
    price_id: product.priceId,
    credits: product.credits,
    success_url: `${window.location.origin}/checkout/success?session_id={CHECKOUT_SESSION_ID}&credits=${product.credits}`,
    cancel_url: `${window.location.origin}/dashboard?checkout=canceled`,
  });

  await redirectToCheckout(response.data.session_id);
}

// =============================================================================
// Status Queries
// =============================================================================

/**
 * Get the user's current subscription status.
 */
export async function getSubscriptionStatus(userId: string): Promise<SubscriptionStatusResponse> {
  const response = await apiClient.get<SubscriptionStatusResponse>(`/api/subscription/${userId}`);
  return response.data;
}

/**
 * Get the user's credit balance.
 */
export async function getCreditBalance(userId: string): Promise<CreditBalanceResponse> {
  const response = await apiClient.get<CreditBalanceResponse>(`/api/credits/${userId}`);
  return response.data;
}

/**
 * Get the user's usage history.
 */
export async function getUsageHistory(
  userId: string,
  periodDays: number = 30
): Promise<UsageResponse> {
  const response = await apiClient.get<UsageResponse>(`/api/usage/${userId}?period_days=${periodDays}`);
  return response.data;
}

// =============================================================================
// Webhook Verification (for backend use - included for completeness)
// =============================================================================

/**
 * Verify a checkout session was successful.
 * Called after redirect from Stripe Checkout.
 */
export async function verifyCheckoutSession(sessionId: string): Promise<{
  success: boolean;
  type: 'subscription' | 'credits';
  tier?: SubscriptionTier;
  credits?: number;
}> {
  const response = await apiClient.get<{
    success: boolean;
    type: 'subscription' | 'credits';
    tier?: SubscriptionTier;
    credits?: number;
  }>(`/api/checkout/verify/${sessionId}`);
  return response.data;
}
