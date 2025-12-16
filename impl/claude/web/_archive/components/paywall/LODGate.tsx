import { useState, ReactNode } from 'react';
import { useUserStore, selectIsLODIncluded } from '@/stores/userStore';
import { useUIStore } from '@/stores/uiStore';
import { LOD_COSTS } from '@/api/types';

interface LODGateProps {
  level: number;
  children: ReactNode;
  onUnlock?: () => void;
}

/**
 * LODGate component that gates content based on subscription tier and credits.
 *
 * - If LOD is included in user's tier, show content directly
 * - If user can afford credits, show unlock button
 * - Otherwise, show upgrade prompt
 */
export function LODGate({ level, children, onUnlock }: LODGateProps) {
  const { credits, spendCredits, recordAction } = useUserStore();
  const { openModal } = useUIStore();
  const [unlocked, setUnlocked] = useState(false);

  // Check if LOD is included in tier
  const isIncluded = useUserStore(selectIsLODIncluded(level));
  const cost = LOD_COSTS[level] || 0;

  // If included in tier or already unlocked, show content
  if (isIncluded || unlocked || cost === 0) {
    return <>{children}</>;
  }

  // Check if user can afford
  const canAfford = credits >= cost;

  const handleUnlock = () => {
    if (canAfford) {
      const success = spendCredits(cost);
      if (success) {
        recordAction(`lod${level}`);
        setUnlocked(true);
        onUnlock?.();
      }
    } else {
      // Open upgrade modal
      openModal('upgrade', { requiredCredits: cost, currentCredits: credits });
    }
  };

  return (
    <div className="relative">
      {/* Blurred preview */}
      <div className="lod-blur pointer-events-none opacity-50">{children}</div>

      {/* Overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 rounded-lg">
        <div className="text-center space-y-3 p-4">
          <div className="text-3xl">🔒</div>
          <p className="font-medium">LOD {level}</p>
          <p className="text-sm text-gray-400">{getLODDescription(level)}</p>
          <p className="text-sm">
            <span className="text-town-highlight">{cost}</span> credits
          </p>
          <button
            onClick={handleUnlock}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              canAfford
                ? 'bg-town-highlight hover:bg-town-highlight/80'
                : 'bg-town-accent hover:bg-town-accent/80'
            }`}
          >
            {canAfford ? `Unlock (${cost} credits)` : 'Get Credits'}
          </button>
          {!canAfford && (
            <p className="text-xs text-gray-500">
              You have {credits} credits
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function getLODDescription(level: number): string {
  switch (level) {
    case 3:
      return 'Memory - eigenvectors, relationships, N-Phase state';
    case 4:
      return 'Psyche - accursed surplus, deep internal state';
    case 5:
      return 'Abyss - the irreducible mystery';
    default:
      return '';
  }
}

export default LODGate;
