import { Link } from 'react-router-dom';
import { useState } from 'react';
import { useUserStore } from '@/stores/userStore';
import { useUIStore } from '@/stores/uiStore';
import { CREDIT_PACKS, SUBSCRIPTION_TIERS } from '@/api/types';
import { createPortalSession, createCreditCheckout } from '@/api/payments';
import { CreditPack } from '@/lib/stripe';

export default function Dashboard() {
  const { tier, credits, monthlyUsage, subscriptionStatus, userId } = useUserStore();
  const { openModal } = useUIStore();
  const [portalLoading, setPortalLoading] = useState(false);

  const handleManageSubscription = async () => {
    if (!userId) return;
    setPortalLoading(true);
    try {
      const url = await createPortalSession(userId);
      window.location.href = url;
    } catch (err) {
      console.error('Failed to open portal:', err);
      setPortalLoading(false);
    }
  };

  const handleUpgrade = () => {
    openModal('upgrade', { currentCredits: credits });
  };

  const handleBuyCredits = async (pack: CreditPack) => {
    if (!userId) return;
    try {
      await createCreditCheckout(pack, userId);
    } catch (err) {
      console.error('Failed to start checkout:', err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Subscription Card */}
        <div className="bg-town-surface/30 rounded-xl p-6 border border-town-accent/20">
          <h2 className="text-lg font-semibold mb-4">Subscription</h2>
          <div className="mb-4">
            <span className="text-2xl font-bold">{tier}</span>
            {subscriptionStatus && (
              <span className="ml-2 text-sm text-gray-400">({subscriptionStatus})</span>
            )}
          </div>
          <p className="text-sm text-gray-400 mb-4">
            {tier === 'TOURIST'
              ? 'Free tier - upgrade to unlock more features'
              : `$${SUBSCRIPTION_TIERS[tier].price}/month`}
          </p>
          {tier === 'TOURIST' ? (
            <button
              onClick={handleUpgrade}
              className="w-full py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors"
            >
              Upgrade Now
            </button>
          ) : (
            <button
              onClick={handleManageSubscription}
              disabled={portalLoading}
              className="w-full py-2 bg-town-accent/30 hover:bg-town-accent/50 rounded-lg text-sm transition-colors disabled:opacity-50"
            >
              {portalLoading ? 'Loading...' : 'Manage Subscription'}
            </button>
          )}
        </div>

        {/* Credits Card */}
        <div className="bg-town-surface/30 rounded-xl p-6 border border-town-accent/20">
          <h2 className="text-lg font-semibold mb-4">Credits</h2>
          <div className="mb-4">
            <span className="text-4xl font-bold">{credits}</span>
            <span className="text-gray-400 ml-2">credits</span>
          </div>
          <div className="space-y-2">
            {CREDIT_PACKS.map((pack, index) => {
              const packKey = ['SMALL', 'MEDIUM', 'LARGE'][index] as CreditPack;
              return (
                <button
                  key={pack.name}
                  onClick={() => handleBuyCredits(packKey)}
                  className="w-full py-2 px-3 bg-town-accent/20 hover:bg-town-accent/40 rounded-lg text-sm flex justify-between items-center transition-colors"
                >
                  <span>{pack.credits} credits</span>
                  <span className="text-gray-400">${pack.price_usd}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Usage Card */}
        <div className="bg-town-surface/30 rounded-xl p-6 border border-town-accent/20">
          <h2 className="text-lg font-semibold mb-4">This Month</h2>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">LOD 3 unlocks</span>
              <span>{monthlyUsage['lod3'] || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">LOD 4 unlocks</span>
              <span>{monthlyUsage['lod4'] || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">LOD 5 unlocks</span>
              <span>{monthlyUsage['lod5'] || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">INHABIT sessions</span>
              <span>{monthlyUsage['inhabit'] || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Branches created</span>
              <span>{monthlyUsage['branch'] || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Towns Section */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Your Towns</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {/* Demo Town Card */}
          <Link
            to="/town/demo"
            className="bg-town-surface/30 rounded-xl p-6 border border-town-accent/20 hover:border-town-accent/50 transition-colors"
          >
            <div className="text-3xl mb-3">🏘️</div>
            <h3 className="font-semibold">Demo Town</h3>
            <p className="text-sm text-gray-400 mt-1">7 citizens • Phase 4</p>
          </Link>

          {/* Create New Town */}
          {tier !== 'TOURIST' && (
            <button className="bg-town-surface/20 rounded-xl p-6 border border-dashed border-town-accent/30 hover:border-town-accent/50 transition-colors text-center">
              <div className="text-3xl mb-3">➕</div>
              <p className="text-gray-400">Create New Town</p>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
