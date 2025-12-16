import { useState } from 'react';
import { useUIStore } from '@/stores/uiStore';
import { useUserStore } from '@/stores/userStore';
import { createSubscriptionCheckout, createCreditCheckout } from '@/api/payments';
import { CREDIT_PRODUCTS, CreditPack } from '@/lib/stripe';
import { SUBSCRIPTION_TIERS, SubscriptionTier } from '@/api/types';

/**
 * Modal for upgrading subscription or purchasing credits.
 */
export function UpgradeModal() {
  const { activeModal, modalData, closeModal } = useUIStore();
  const { userId, tier } = useUserStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'credits' | 'subscription'>('credits');

  if (activeModal !== 'upgrade') {
    return null;
  }

  const requiredCredits = (modalData as { requiredCredits?: number }).requiredCredits || 0;
  const currentCredits = (modalData as { currentCredits?: number }).currentCredits || 0;

  const handleCreditPurchase = async (pack: CreditPack) => {
    if (!userId) {
      setError('Please sign in to purchase credits');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await createCreditCheckout(pack, userId);
    } catch (err) {
      console.error('Credit checkout error:', err);
      setError('Failed to start checkout. Please try again.');
      setLoading(false);
    }
  };

  const handleSubscriptionUpgrade = async (newTier: SubscriptionTier) => {
    if (!userId) {
      setError('Please sign in to upgrade');
      return;
    }

    if (newTier === 'TOURIST') {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await createSubscriptionCheckout(newTier, userId);
    } catch (err) {
      console.error('Subscription checkout error:', err);
      setError('Failed to start checkout. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      <div className="bg-town-surface border border-town-accent/30 rounded-xl w-full max-w-2xl mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-town-accent/30">
          <h2 className="text-xl font-bold">Unlock More</h2>
          <button
            onClick={closeModal}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Close"
          >
            &times;
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-town-accent/30">
          <button
            onClick={() => setTab('credits')}
            className={`flex-1 py-3 text-center font-medium transition-colors ${
              tab === 'credits'
                ? 'bg-town-accent/20 text-white border-b-2 border-town-highlight'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Buy Credits
          </button>
          <button
            onClick={() => setTab('subscription')}
            className={`flex-1 py-3 text-center font-medium transition-colors ${
              tab === 'subscription'
                ? 'bg-town-accent/20 text-white border-b-2 border-town-highlight'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Upgrade Tier
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-500/30 rounded-lg text-red-300 text-sm">
              {error}
            </div>
          )}

          {requiredCredits > currentCredits && (
            <div className="mb-4 p-3 bg-yellow-900/30 border border-yellow-500/30 rounded-lg text-yellow-300 text-sm">
              You need {requiredCredits - currentCredits} more credits to unlock this content.
            </div>
          )}

          {tab === 'credits' ? (
            <CreditPacksGrid
              onSelect={handleCreditPurchase}
              loading={loading}
              requiredCredits={requiredCredits}
              currentCredits={currentCredits}
            />
          ) : (
            <SubscriptionTiersGrid
              currentTier={tier}
              onSelect={handleSubscriptionUpgrade}
              loading={loading}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface CreditPacksGridProps {
  onSelect: (pack: CreditPack) => void;
  loading: boolean;
  requiredCredits: number;
  currentCredits: number;
}

function CreditPacksGrid({ onSelect, loading, requiredCredits, currentCredits }: CreditPacksGridProps) {
  const packs: { key: CreditPack; name: string; popular?: boolean }[] = [
    { key: 'SMALL', name: 'Starter' },
    { key: 'MEDIUM', name: 'Explorer', popular: true },
    { key: 'LARGE', name: 'Adventurer' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {packs.map(({ key, name, popular }) => {
        const product = CREDIT_PRODUCTS[key];
        const coversRequired = currentCredits + product.credits >= requiredCredits;

        return (
          <div
            key={key}
            className={`relative p-4 rounded-lg border transition-all ${
              popular
                ? 'border-town-highlight bg-town-highlight/10'
                : 'border-town-accent/30 bg-town-surface/30'
            } hover:border-town-highlight/50`}
          >
            {popular && (
              <span className="absolute -top-2 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-town-highlight text-xs font-medium rounded">
                Popular
              </span>
            )}

            <h3 className="font-semibold text-lg mt-2">{name}</h3>
            <p className="text-3xl font-bold mt-2">
              {product.credits}
              <span className="text-sm font-normal text-gray-400 ml-1">credits</span>
            </p>
            <p className="text-gray-400 mt-1">${(product.amount / 100).toFixed(2)}</p>

            {coversRequired && requiredCredits > currentCredits && (
              <p className="text-xs text-green-400 mt-2">Covers your needs</p>
            )}

            <button
              onClick={() => onSelect(key)}
              disabled={loading}
              className={`w-full mt-4 py-2 px-4 rounded-lg font-medium transition-colors ${
                loading
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-town-highlight hover:bg-town-highlight/80'
              }`}
            >
              {loading ? 'Processing...' : 'Buy Now'}
            </button>
          </div>
        );
      })}
    </div>
  );
}

interface SubscriptionTiersGridProps {
  currentTier: SubscriptionTier;
  onSelect: (tier: SubscriptionTier) => void;
  loading: boolean;
}

function SubscriptionTiersGrid({ currentTier, onSelect, loading }: SubscriptionTiersGridProps) {
  const tiers: { key: SubscriptionTier; recommended?: boolean }[] = [
    { key: 'RESIDENT' },
    { key: 'CITIZEN', recommended: true },
    { key: 'FOUNDER' },
  ];

  const tierOrder: Record<SubscriptionTier, number> = {
    TOURIST: 0,
    RESIDENT: 1,
    CITIZEN: 2,
    FOUNDER: 3,
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {tiers.map(({ key, recommended }) => {
        const tierInfo = SUBSCRIPTION_TIERS[key];
        const isCurrentTier = currentTier === key;
        const isDowngrade = tierOrder[key] < tierOrder[currentTier];

        return (
          <div
            key={key}
            className={`relative p-4 rounded-lg border transition-all ${
              recommended
                ? 'border-town-highlight bg-town-highlight/10'
                : 'border-town-accent/30 bg-town-surface/30'
            } hover:border-town-highlight/50`}
          >
            {recommended && (
              <span className="absolute -top-2 left-1/2 -translate-x-1/2 px-2 py-0.5 bg-town-highlight text-xs font-medium rounded">
                Recommended
              </span>
            )}

            <h3 className="font-semibold text-lg mt-2">{key}</h3>
            <p className="text-3xl font-bold mt-2">
              ${tierInfo.price}
              <span className="text-sm font-normal text-gray-400 ml-1">
                /{key === 'FOUNDER' ? 'year' : 'month'}
              </span>
            </p>

            <ul className="mt-4 space-y-2 text-sm text-gray-300">
              <li>LOD 0-{tierInfo.lod.at(-1)?.toString() || '2'} included</li>
              {tierInfo.inhabit && <li className="text-green-400">INHABIT mode ({tierInfo.inhabit})</li>}
              {tierInfo.branching && <li className="text-purple-400">BRANCH mode</li>}
            </ul>

            <button
              onClick={() => onSelect(key)}
              disabled={loading || isCurrentTier || isDowngrade}
              className={`w-full mt-4 py-2 px-4 rounded-lg font-medium transition-colors ${
                isCurrentTier
                  ? 'bg-gray-700 cursor-default text-gray-400'
                  : isDowngrade
                  ? 'bg-gray-700 cursor-not-allowed text-gray-500'
                  : loading
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-town-highlight hover:bg-town-highlight/80'
              }`}
            >
              {isCurrentTier ? 'Current Plan' : isDowngrade ? 'Downgrade N/A' : loading ? 'Processing...' : 'Upgrade'}
            </button>
          </div>
        );
      })}
    </div>
  );
}

export default UpgradeModal;
