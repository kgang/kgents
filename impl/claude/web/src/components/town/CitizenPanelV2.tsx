/**
 * CitizenPanelV2: Props-based citizen detail panel.
 *
 * Receives citizen from props instead of reading from Zustand.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useUserStore, selectCanInhabit } from '@/stores/userStore';
import { townApi } from '@/api/client';
import { LODGate } from '@/components/paywall/LODGate';
import { cn, getArchetypeColor, getPhaseColor } from '@/lib/utils';
import type { CitizenCardJSON } from '@/reactive/types';
import type { CitizenManifest } from '@/api/types';

interface CitizenPanelV2Props {
  citizen: CitizenCardJSON;
  townId: string;
  onClose: () => void;
}

export function CitizenPanelV2({ citizen, townId, onClose }: CitizenPanelV2Props) {
  const { userId, tier } = useUserStore();
  const canInhabit = useUserStore(selectCanInhabit());
  const [manifest, setManifest] = useState<CitizenManifest | null>(null);
  const [currentLOD, setCurrentLOD] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch citizen manifest when citizen or LOD changes
  useEffect(() => {
    const fetchManifest = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await townApi.getCitizen(
          townId,
          citizen.name,
          currentLOD,
          userId || 'anonymous'
        );
        setManifest(res.data.citizen);
      } catch (err) {
        console.error('Failed to fetch citizen:', err);
        setError('Failed to load citizen details');
      } finally {
        setLoading(false);
      }
    };

    fetchManifest();
  }, [citizen.name, townId, currentLOD, userId]);

  if (loading) {
    return (
      <div className="p-6 text-center text-gray-400">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center text-red-400">
        <p>{error}</p>
        <button
          onClick={() => setCurrentLOD(0)}
          className="mt-2 text-sm text-gray-400 hover:text-white"
        >
          Reset to LOD 0
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4 overflow-y-auto h-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">{citizen.name}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-white">
          ✕
        </button>
      </div>

      {/* LOD 0: Silhouette - Always visible */}
      <LODSection level={0} title="Silhouette" icon="👤">
        <div className="space-y-2 text-sm">
          <InfoRow label="Region" value={citizen.region} />
          <InfoRow
            label="Phase"
            value={citizen.phase}
            valueClass={getPhaseColor(citizen.phase)}
          />
          <InfoRow label="N-Phase" value={citizen.nphase} />
        </div>
      </LODSection>

      {/* LOD 1: Posture - Always visible for paid tiers */}
      <LODSection level={1} title="Posture" icon="🧍">
        <div className="space-y-2 text-sm">
          <InfoRow
            label="Archetype"
            value={citizen.archetype}
            valueClass={getArchetypeColor(citizen.archetype)}
          />
          <InfoRow label="Mood" value={citizen.mood} />
        </div>
      </LODSection>

      {/* LOD 2: Dialogue - Always visible for paid tiers */}
      <LODSection level={2} title="Dialogue" icon="💬">
        {manifest?.cosmotechnics && (
          <div className="space-y-2 text-sm">
            <InfoRow label="Cosmotechnics" value={manifest.cosmotechnics} />
            {manifest?.metaphor && (
              <p className="italic text-gray-300 mt-2">"{manifest.metaphor}"</p>
            )}
          </div>
        )}
      </LODSection>

      {/* LOD 3: Memory - Gated */}
      <LODGate level={3} onUnlock={() => setCurrentLOD(3)}>
        <LODSection level={3} title="Memory" icon="🧠">
          <div className="space-y-3">
            {/* Display eigenvectors from CitizenCardJSON */}
            <div>
              <h4 className="font-medium text-sm mb-2">Eigenvectors</h4>
              <EigenvectorBar label="Warmth" value={citizen.eigenvectors.warmth} color="bg-red-500" />
              <EigenvectorBar label="Curiosity" value={citizen.eigenvectors.curiosity} color="bg-yellow-500" />
              <EigenvectorBar label="Trust" value={citizen.eigenvectors.trust} color="bg-green-500" />
            </div>
            {/* Full eigenvectors from manifest if available */}
            {manifest?.eigenvectors && (
              <div className="mt-2">
                <EigenvectorBar label="Creativity" value={manifest.eigenvectors.creativity} color="bg-purple-500" />
                <EigenvectorBar label="Patience" value={manifest.eigenvectors.patience} color="bg-blue-500" />
                <EigenvectorBar label="Resilience" value={manifest.eigenvectors.resilience} color="bg-orange-500" />
                <EigenvectorBar label="Ambition" value={manifest.eigenvectors.ambition} color="bg-pink-500" />
              </div>
            )}
            {manifest?.relationships && Object.keys(manifest.relationships).length > 0 && (
              <>
                <h4 className="font-medium text-sm mt-4">Relationships</h4>
                <RelationshipList relationships={manifest.relationships} />
              </>
            )}
          </div>
        </LODSection>
      </LODGate>

      {/* LOD 4: Psyche - Gated */}
      <LODGate level={4} onUnlock={() => setCurrentLOD(4)}>
        <LODSection level={4} title="Psyche" icon="✨">
          <div className="space-y-2 text-sm">
            <InfoRow
              label="Capability"
              value={`${(citizen.capability * 100).toFixed(0)}%`}
            />
            <InfoRow
              label="Entropy"
              value={citizen.entropy.toFixed(3)}
            />
            {manifest?.accursed_surplus !== undefined && (
              <InfoRow
                label="Accursed Surplus"
                value={manifest.accursed_surplus.toFixed(3)}
              />
            )}
            {manifest?.id && <InfoRow label="ID" value={manifest.id} mono />}
          </div>
        </LODSection>
      </LODGate>

      {/* LOD 5: Abyss - Gated */}
      <LODGate level={5} onUnlock={() => setCurrentLOD(5)}>
        <LODSection level={5} title="Abyss" icon="🌀">
          {manifest?.opacity && (
            <div className="bg-purple-900/30 p-4 rounded-lg border border-purple-500/20">
              <p className="italic text-purple-300">"{manifest.opacity.statement}"</p>
              <p className="mt-3 text-sm text-gray-400">{manifest.opacity.message}</p>
            </div>
          )}
        </LODSection>
      </LODGate>

      {/* Actions */}
      <div className="pt-4 border-t border-town-accent/30 space-y-2">
        {canInhabit && townId && (
          <Link
            to={`/town/${townId}/inhabit/${citizen.citizen_id}`}
            className="block w-full py-2 px-4 bg-town-highlight hover:bg-town-highlight/80 rounded-lg text-center font-medium transition-colors"
          >
            🎭 INHABIT {citizen.name}
          </Link>
        )}
        {tier === 'TOURIST' && (
          <p className="text-xs text-center text-gray-500">
            Upgrade to RESIDENT to unlock INHABIT mode
          </p>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface LODSectionProps {
  level: number;
  title: string;
  icon: string;
  children: React.ReactNode;
}

function LODSection({ level, title, icon, children }: LODSectionProps) {
  return (
    <div className="bg-town-surface/30 rounded-lg p-4 border border-town-accent/20">
      <div className="flex items-center gap-2 mb-3">
        <span>{icon}</span>
        <h3 className="font-medium">
          {title}
          <span className="text-xs text-gray-500 ml-2">LOD {level}</span>
        </h3>
      </div>
      {children}
    </div>
  );
}

interface InfoRowProps {
  label: string;
  value: string | number;
  valueClass?: string;
  mono?: boolean;
}

function InfoRow({ label, value, valueClass, mono }: InfoRowProps) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-400">{label}</span>
      <span className={cn(valueClass, mono && 'font-mono text-xs')}>{value}</span>
    </div>
  );
}

interface EigenvectorBarProps {
  label: string;
  value: number;
  color: string;
}

function EigenvectorBar({ label, value, color }: EigenvectorBarProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400 w-20">{label}</span>
      <div className="flex-1 h-2 bg-town-surface rounded-full overflow-hidden">
        <div
          className={cn('h-full transition-all', color)}
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="text-xs text-gray-500 w-8">{value.toFixed(2)}</span>
    </div>
  );
}

interface RelationshipListProps {
  relationships: Record<string, number>;
}

function RelationshipList({ relationships }: RelationshipListProps) {
  const sorted = Object.entries(relationships).sort(([, a], [, b]) => b - a);

  return (
    <div className="space-y-1">
      {sorted.slice(0, 5).map(([name, value]) => (
        <div key={name} className="flex items-center justify-between text-sm">
          <span className="text-gray-300">{name}</span>
          <span
            className={cn(
              'font-mono text-xs',
              value > 0 ? 'text-green-400' : value < 0 ? 'text-red-400' : 'text-gray-500'
            )}
          >
            {value > 0 ? '+' : ''}
            {value.toFixed(2)}
          </span>
        </div>
      ))}
      {sorted.length > 5 && (
        <p className="text-xs text-gray-500">+{sorted.length - 5} more</p>
      )}
    </div>
  );
}

export default CitizenPanelV2;
