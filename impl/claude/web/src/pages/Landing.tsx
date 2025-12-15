import { useState } from 'react';
import { Link } from 'react-router-dom';
import { DemoPreview } from '@/components/landing/DemoPreview';
import { createSubscriptionCheckout } from '@/api/payments';
import { useUserStore } from '@/stores/userStore';
import type { SubscriptionTier } from '@/api/types';

const FEATURES = [
  {
    title: 'OBSERVE',
    emoji: '👁️',
    description: 'Watch lives unfold. Citizens form relationships, coalitions, and memories.',
  },
  {
    title: 'INHABIT',
    emoji: '🎭',
    description: 'Become them. Step into a citizen\'s perspective and guide their choices.',
  },
  {
    title: 'BRANCH',
    emoji: '🌿',
    description: 'Fork reality. Create alternate timelines and explore what-if scenarios.',
  },
];

const PRICING = [
  {
    tier: 'TOURIST',
    price: 'FREE',
    description: 'Watch the demo',
    features: ['LOD 0-1 access', 'Demo town only', 'No INHABIT'],
    cta: 'Try Demo',
    highlighted: false,
  },
  {
    tier: 'RESIDENT',
    price: '$9.99/mo',
    description: 'Start your journey',
    features: ['LOD 0-3 access', '50 LOD3 actions/mo', 'Basic INHABIT', '1 town'],
    cta: 'Get Started',
    highlighted: false,
  },
  {
    tier: 'CITIZEN',
    price: '$29.99/mo',
    description: 'Full experience',
    features: ['LOD 0-4 access', '20 LOD4 actions/mo', 'Full INHABIT + Force', '5 towns', '3 branches/mo'],
    cta: 'Subscribe',
    highlighted: true,
  },
  {
    tier: 'FOUNDER',
    price: '$99.99/mo',
    description: 'Unlimited access',
    features: ['LOD 0-5 access', 'Unlimited actions', 'Unlimited INHABIT', 'Unlimited towns', 'API access'],
    cta: 'Join Founders',
    highlighted: false,
  },
];

export default function Landing() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { userId, isAuthenticated } = useUserStore();

  const handleSubscribe = async (tier: string) => {
    if (tier === 'TOURIST') return;

    // Require authentication for paid tiers
    if (!isAuthenticated || !userId) {
      setError('Please sign in to subscribe. Create an account in the dashboard.');
      return;
    }

    setLoading(tier);
    setError(null);
    try {
      await createSubscriptionCheckout(tier as Exclude<SubscriptionTier, 'TOURIST'>, userId);
      // User will be redirected to Stripe Checkout
    } catch (err) {
      console.error('Checkout error:', err);
      setError('Failed to start checkout. Please try again.');
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-town-bg">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-town-accent/20 to-transparent" />
        <div className="max-w-7xl mx-auto px-4 py-20 relative">
          <div className="text-center mb-12">
            <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Agent Town
            </h1>
            <p className="text-xl md:text-2xl text-gray-400 mb-8">
              Civilizations that dream
            </p>
            <div className="flex justify-center gap-4">
              <Link
                to="/town/demo"
                className="px-8 py-3 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-semibold text-lg transition-colors"
              >
                Watch the Demo
              </Link>
              <a
                href="#pricing"
                className="px-8 py-3 bg-town-surface hover:bg-town-accent border border-town-accent rounded-lg font-semibold text-lg transition-colors"
              >
                View Pricing
              </a>
            </div>
          </div>

          {/* Live Demo Preview */}
          <div className="max-w-4xl mx-auto">
            <DemoPreview />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 border-t border-town-accent/30">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Three Ways to Experience</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="bg-town-surface/30 rounded-xl p-8 border border-town-accent/20 hover:border-town-accent/50 transition-colors"
              >
                <div className="text-5xl mb-4">{feature.emoji}</div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 border-t border-town-accent/30">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-4">Choose Your Path</h2>
          <p className="text-gray-400 text-center mb-12">Start free, upgrade when ready</p>

          {error && (
            <div className="max-w-md mx-auto mb-8 p-4 bg-red-900/30 border border-red-500/30 rounded-lg text-red-300 text-center">
              {error}
            </div>
          )}

          <div className="grid md:grid-cols-4 gap-6">
            {PRICING.map((plan) => {
              const isLoading = loading === plan.tier;
              return (
                <div
                  key={plan.tier}
                  className={`rounded-xl p-6 border ${
                    plan.highlighted
                      ? 'bg-town-highlight/10 border-town-highlight'
                      : 'bg-town-surface/30 border-town-accent/20'
                  }`}
                >
                  {plan.highlighted && (
                    <div className="text-xs font-semibold text-town-highlight mb-2">MOST POPULAR</div>
                  )}
                  <h3 className="text-lg font-semibold">{plan.tier}</h3>
                  <div className="text-3xl font-bold my-3">{plan.price}</div>
                  <p className="text-sm text-gray-400 mb-4">{plan.description}</p>
                  <ul className="space-y-2 mb-6">
                    {plan.features.map((feature, i) => (
                      <li key={i} className="text-sm text-gray-300 flex items-center gap-2">
                        <span className="text-green-500">✓</span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                  {plan.tier === 'TOURIST' ? (
                    <Link
                      to="/town/demo"
                      className={`block w-full py-2 rounded-lg font-medium text-center transition-colors bg-town-accent hover:bg-town-accent/80`}
                    >
                      {plan.cta}
                    </Link>
                  ) : (
                    <button
                      onClick={() => handleSubscribe(plan.tier)}
                      disabled={loading !== null}
                      className={`w-full py-2 rounded-lg font-medium transition-colors ${
                        loading !== null
                          ? 'bg-gray-600 cursor-not-allowed'
                          : plan.highlighted
                          ? 'bg-town-highlight hover:bg-town-highlight/80'
                          : 'bg-town-accent hover:bg-town-accent/80'
                      }`}
                    >
                      {isLoading ? 'Processing...' : plan.cta}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-town-accent/30">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500">
          <p>Agent Town - Civilizations that dream</p>
          <p className="text-sm mt-2">Built with kgents</p>
        </div>
      </footer>
    </div>
  );
}
