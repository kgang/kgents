import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { verifyCheckoutSession } from '@/api/payments';
import { useUserStore } from '@/stores/userStore';
import type { SubscriptionTier } from '@/api/types';

type VerificationState = 'loading' | 'success' | 'error';

interface VerificationResult {
  type: 'subscription' | 'credits';
  tier?: SubscriptionTier;
  credits?: number;
}

export default function CheckoutSuccess() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const creditsParam = searchParams.get('credits');

  const [state, setState] = useState<VerificationState>('loading');
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const { setTier, addCredits } = useUserStore();

  useEffect(() => {
    async function verifySession() {
      if (!sessionId) {
        setState('error');
        setErrorMessage('Missing session ID');
        return;
      }

      try {
        const verification = await verifyCheckoutSession(sessionId);

        if (verification.success) {
          setResult({
            type: verification.type,
            tier: verification.tier,
            credits: verification.credits,
          });

          // Update user state based on purchase type
          if (verification.type === 'subscription' && verification.tier) {
            setTier(verification.tier);
          } else if (verification.type === 'credits' && verification.credits) {
            addCredits(verification.credits);
          }

          setState('success');

          // Redirect to dashboard after delay
          setTimeout(() => {
            navigate('/dashboard');
          }, 4000);
        } else {
          setState('error');
          setErrorMessage('Payment verification failed');
        }
      } catch (err) {
        console.error('Verification error:', err);
        setState('error');
        setErrorMessage('Could not verify payment. Please contact support if you were charged.');

        // Fallback: if credits param exists, assume credit purchase succeeded
        if (creditsParam) {
          const credits = parseInt(creditsParam, 10);
          if (!isNaN(credits)) {
            addCredits(credits);
            setResult({ type: 'credits', credits });
            setState('success');
            setTimeout(() => navigate('/dashboard'), 4000);
          }
        }
      }
    }

    verifySession();
  }, [sessionId, creditsParam, navigate, setTier, addCredits]);

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center">
      <div className="text-center max-w-md px-4">
        {state === 'loading' && (
          <>
            <div className="text-6xl mb-6 animate-pulse">...</div>
            <h1 className="text-2xl font-bold mb-4">Verifying Payment</h1>
            <p className="text-gray-400">Please wait while we confirm your purchase...</p>
          </>
        )}

        {state === 'success' && (
          <>
            <div className="text-6xl mb-6">🎉</div>
            <h1 className="text-3xl font-bold mb-4">Payment Successful!</h1>

            {result?.type === 'subscription' && result.tier && (
              <div className="mb-6">
                <p className="text-lg text-gray-300 mb-2">
                  Welcome to <span className="text-town-highlight font-semibold">{result.tier}</span>!
                </p>
                <p className="text-gray-400">
                  Your subscription is now active. Enjoy your enhanced access to Agent Town.
                </p>
              </div>
            )}

            {result?.type === 'credits' && result.credits && (
              <div className="mb-6">
                <p className="text-lg text-gray-300 mb-2">
                  <span className="text-town-highlight font-semibold">{result.credits}</span> credits added!
                </p>
                <p className="text-gray-400">
                  Your credits are ready to use. Explore deeper levels of the simulation.
                </p>
              </div>
            )}

            <p className="text-sm text-gray-500 mb-4">Redirecting to dashboard...</p>
            <Link
              to="/dashboard"
              className="text-town-highlight hover:underline"
            >
              Go to Dashboard Now
            </Link>
          </>
        )}

        {state === 'error' && (
          <>
            <div className="text-6xl mb-6">⚠️</div>
            <h1 className="text-2xl font-bold mb-4 text-red-400">Verification Issue</h1>
            <p className="text-gray-400 mb-6">
              {errorMessage}
            </p>
            <div className="space-y-3">
              <Link
                to="/dashboard"
                className="block w-full py-2 px-4 bg-town-accent hover:bg-town-accent/80 rounded-lg font-medium transition-colors"
              >
                Go to Dashboard
              </Link>
              <p className="text-sm text-gray-500">
                If you were charged and don't see your purchase, please{' '}
                <a href="mailto:support@agenttown.dev" className="text-town-highlight hover:underline">
                  contact support
                </a>
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
