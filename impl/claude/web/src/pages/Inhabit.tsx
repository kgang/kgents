import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useUserStore, selectCanInhabit, selectCanForce } from '@/stores/userStore';
import { townApi } from '@/api/client';
import { useInhabitSession } from '@/hooks/useInhabitSession';

export default function Inhabit() {
  const { townId, citizenId } = useParams<{ townId: string; citizenId: string }>();
  const navigate = useNavigate();
  const { tier: _tier } = useUserStore();
  const canInhabit = useUserStore(selectCanInhabit());
  const canUseForce = useUserStore(selectCanForce());

  const [actionInput, setActionInput] = useState('');
  const [forceEnabled, setForceEnabled] = useState(false);
  const [citizenName, setCitizenName] = useState<string>(citizenId || '');

  // Fetch citizen name from API
  useEffect(() => {
    if (!townId || !citizenId) return;

    const fetchCitizenName = async () => {
      try {
        // Use the citizen ID to fetch the citizen manifest
        const res = await townApi.getCitizen(townId, citizenId, 0, 'anonymous');
        if (res.data.citizen?.name) {
          setCitizenName(res.data.citizen.name);
        }
      } catch {
        // Keep using citizenId as fallback
        console.warn('Could not fetch citizen name, using ID');
      }
    };

    fetchCitizenName();
  }, [townId, citizenId]);

  // INHABIT session hook
  const {
    status,
    isLoading,
    error,
    lastResponse: _lastResponse,
    history,
    start,
    submitAction,
    forceAction,
    apologize,
    end,
    timeRemaining,
    consentDebt,
    canForce,
    isRuptured,
    isExpired,
  } = useInhabitSession({
    townId: townId || '',
    citizenName,
    forceEnabled: forceEnabled && canUseForce,
    onSessionEnd: () => {
      navigate(`/town/${townId}`);
    },
    onRupture: () => {
      // Could show a notification here
      console.log('Relationship ruptured!');
    },
  });

  // Redirect if not allowed to INHABIT
  useEffect(() => {
    if (!canInhabit) {
      navigate(`/town/${townId}`);
    }
  }, [canInhabit, townId, navigate]);

  // Start session on mount
  useEffect(() => {
    if (citizenName && !status && !error) {
      start().catch(console.error);
    }
  }, [citizenName, status, error, start]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmitAction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!actionInput.trim() || isLoading) return;

    await submitAction(actionInput);
    setActionInput('');
  };

  const handleForce = async () => {
    if (!actionInput.trim() || isLoading || !canForce) return;

    await forceAction(actionInput);
    setActionInput('');
  };

  const handleApologize = async () => {
    if (isLoading) return;
    await apologize();
  };

  const handleExit = async () => {
    await end();
    navigate(`/town/${townId}`);
  };

  // Loading state
  if (!status && isLoading) {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
        <div className="text-center">
          <div className="animate-pulse text-4xl mb-4">🎭</div>
          <p className="text-gray-400">Connecting to {citizenName}...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !status) {
    return (
      <div className="h-[calc(100vh-64px)] flex items-center justify-center bg-town-bg">
        <div className="text-center">
          <div className="text-4xl mb-4">❌</div>
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => navigate(`/town/${townId}`)}
            className="px-4 py-2 bg-town-accent rounded-lg hover:bg-town-accent/80"
          >
            Return to Town
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col bg-town-bg">
      {/* INHABIT Header */}
      <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-2xl">🎭</span>
          <div>
            <h1 className="font-semibold">INHABIT: {citizenName}</h1>
            <p className="text-sm text-gray-400">{status?.consent.status || 'Connecting...'}</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          {/* Consent Debt Meter */}
          <div className="text-sm">
            <span className="text-gray-400">Consent Debt:</span>
            <div className="w-24 h-2 bg-town-surface rounded-full mt-1 overflow-hidden">
              <div
                className={`h-full transition-all ${
                  consentDebt < 0.5
                    ? 'bg-green-500'
                    : consentDebt < 0.8
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                }`}
                style={{ width: `${consentDebt * 100}%` }}
              />
            </div>
            {isRuptured && <p className="text-xs text-red-400 mt-1">RUPTURED</p>}
          </div>

          {/* Force Status */}
          {status?.force.enabled && (
            <div className="text-sm">
              <span className="text-gray-400">Forces:</span>
              <span className="ml-2 font-mono">
                {status.force.remaining}/{status.force.limit}
              </span>
            </div>
          )}

          {/* Session Timer */}
          <div className="text-sm">
            <span className="text-gray-400">Time:</span>
            <span className={`ml-2 font-mono ${timeRemaining < 60 ? 'text-red-500' : ''}`}>
              {formatTime(timeRemaining)}
            </span>
          </div>

          {/* Exit Button */}
          <button
            onClick={handleExit}
            className="px-4 py-1 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors"
          >
            Exit INHABIT
          </button>
        </div>
      </div>

      {/* Main INHABIT View */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-6 gap-6 overflow-y-auto">
        {/* Scene/Response History */}
        <div className="space-y-4 flex-1">
          {history.length === 0 && (
            <div className="bg-town-surface/30 rounded-xl p-6 border border-town-accent/20">
              <h2 className="text-sm text-gray-400 mb-2">SCENE</h2>
              <p className="text-lg leading-relaxed">
                You are now connected to {citizenName}'s perspective. What would you like to do?
              </p>
            </div>
          )}

          {history.map((response, i) => (
            <div key={i} className="space-y-3">
              {/* Response */}
              <div
                className={`bg-town-surface/30 rounded-xl p-6 border ${
                  response.type === 'enact'
                    ? 'border-green-500/30'
                    : response.type === 'resist'
                      ? 'border-red-500/30'
                      : response.type === 'negotiate'
                        ? 'border-yellow-500/30'
                        : 'border-town-accent/20'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span
                    className={`text-xs font-semibold ${
                      response.type === 'enact'
                        ? 'text-green-400'
                        : response.type === 'resist'
                          ? 'text-red-400'
                          : response.type === 'negotiate'
                            ? 'text-yellow-400'
                            : 'text-gray-400'
                    }`}
                  >
                    {response.type.toUpperCase()}
                  </span>
                  {response.alignment_score !== undefined && (
                    <span className="text-xs text-gray-500">
                      (alignment: {(response.alignment_score * 100).toFixed(0)}%)
                    </span>
                  )}
                </div>
                <p className="text-lg leading-relaxed">{response.message}</p>
                {response.suggested_rephrase && (
                  <p className="text-sm text-gray-400 mt-2 italic">
                    Suggestion: {response.suggested_rephrase}
                  </p>
                )}
              </div>

              {/* Inner Voice */}
              {response.inner_voice && (
                <div className="bg-town-surface/30 rounded-xl p-6 border border-purple-500/20">
                  <h2 className="text-sm text-purple-400 mb-2">INNER VOICE</h2>
                  <p className="text-lg italic text-gray-300">{response.inner_voice}</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Apologize button (when debt is high) */}
        {consentDebt > 0.3 && !isRuptured && (
          <button
            onClick={handleApologize}
            disabled={isLoading}
            className="px-4 py-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30 transition-colors disabled:opacity-50"
          >
            Apologize (reduce consent debt)
          </button>
        )}

        {/* Action Input */}
        {!isRuptured && !isExpired && (
          <form onSubmit={handleSubmitAction}>
            <div className="bg-town-surface/50 rounded-xl p-4 border border-town-accent/30">
              <label className="text-sm text-gray-400 block mb-2">What do you do?</label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={actionInput}
                  onChange={(e) => setActionInput(e.target.value)}
                  placeholder="describe your action..."
                  disabled={isLoading}
                  className="flex-1 bg-town-bg border border-town-accent/30 rounded-lg px-4 py-2 focus:outline-none focus:border-town-highlight disabled:opacity-50"
                />
                <button
                  type="submit"
                  disabled={isLoading || !actionInput.trim()}
                  className="px-6 py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors disabled:opacity-50"
                >
                  {isLoading ? '...' : 'Suggest'}
                </button>
                {canForce && status?.force.enabled && (
                  <button
                    type="button"
                    onClick={handleForce}
                    disabled={isLoading || !actionInput.trim() || !canForce}
                    className="px-6 py-2 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-lg font-medium transition-colors disabled:opacity-50"
                  >
                    Force
                  </button>
                )}
              </div>

              {/* Force toggle (for eligible tiers) */}
              {canUseForce && !status?.force.enabled && (
                <label className="flex items-center gap-2 mt-3 text-sm text-gray-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={forceEnabled}
                    onChange={(e) => setForceEnabled(e.target.checked)}
                    className="rounded border-town-accent/30"
                  />
                  Enable Advanced INHABIT (force mechanic)
                </label>
              )}

              {/* Suggestions */}
              <div className="flex gap-2 mt-3 flex-wrap">
                <span className="text-xs text-gray-500">Suggestions:</span>
                {[
                  'look around',
                  'greet nearby citizen',
                  'walk to market',
                  'reflect on the day',
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => setActionInput(suggestion)}
                    className="text-xs px-2 py-1 bg-town-accent/20 rounded hover:bg-town-accent/40 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </form>
        )}

        {/* Ruptured state */}
        {isRuptured && (
          <div className="bg-red-500/10 rounded-xl p-6 border border-red-500/30 text-center">
            <p className="text-red-400 text-lg">
              The relationship has ruptured. {citizenName} refuses all interaction.
            </p>
            <button
              onClick={handleExit}
              className="mt-4 px-6 py-2 bg-town-accent rounded-lg hover:bg-town-accent/80"
            >
              Return to Town
            </button>
          </div>
        )}

        {/* Expired state */}
        {isExpired && !isRuptured && (
          <div className="bg-yellow-500/10 rounded-xl p-6 border border-yellow-500/30 text-center">
            <p className="text-yellow-400 text-lg">
              Session time has expired. {citizenName} needs to rest.
            </p>
            <button
              onClick={handleExit}
              className="mt-4 px-6 py-2 bg-town-accent rounded-lg hover:bg-town-accent/80"
            >
              Return to Town
            </button>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="bg-red-500/10 rounded-lg p-3 border border-red-500/30">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}
