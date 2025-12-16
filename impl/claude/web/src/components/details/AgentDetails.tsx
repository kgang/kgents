/**
 * AgentDetails: Tabbed container for deep citizen inspection.
 *
 * Supports three modes:
 * - compact: Hover preview with minimal info
 * - expanded: Sidebar panel with tabs
 * - full: Modal overlay with full visualization
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { townApi } from '@/api/client';
import { useUserStore, selectCanInhabit } from '@/stores/userStore';
import { ElasticCard } from '@/components/elastic';
import { LODGate } from '@/components/paywall/LODGate';
import { cn, getArchetypeColor, getPhaseColor } from '@/lib/utils';
import { OverviewTab } from './OverviewTab';
import { MetricsTab } from './MetricsTab';
import { RelationshipsTab } from './RelationshipsTab';
import { StateTab } from './StateTab';
import { HistoryTab } from './HistoryTab';
import { ExportButton } from './ExportButton';
import type { CitizenCardJSON } from '@/reactive/types';
import type { CitizenManifest } from '@/api/types';

export type DetailLevel = 'compact' | 'expanded' | 'full';
export type DetailsTab = 'overview' | 'metrics' | 'relationships' | 'state' | 'history';

export interface AgentDetailsProps {
  /** Citizen data from widget stream */
  citizen: CitizenCardJSON;
  /** Town ID for API calls */
  townId: string;
  /** Detail level to render */
  level: DetailLevel;
  /** Currently active tab (expanded/full modes) */
  activeTab?: DetailsTab;
  /** Tab change handler */
  onTabChange?: (tab: DetailsTab) => void;
  /** Close handler */
  onClose?: () => void;
  /** Level change handler (e.g., hover -> click -> modal) */
  onLevelChange?: (level: DetailLevel) => void;
  /** Additional class names */
  className?: string;
}

const TAB_CONFIG: { id: DetailsTab; label: string; icon: string; minLOD: number }[] = [
  { id: 'overview', label: 'Overview', icon: '📊', minLOD: 0 },
  { id: 'metrics', label: 'Metrics', icon: '📈', minLOD: 3 },
  { id: 'relationships', label: 'Relations', icon: '🤝', minLOD: 3 },
  { id: 'state', label: 'State', icon: '💾', minLOD: 4 },
  { id: 'history', label: 'History', icon: '📜', minLOD: 4 },
];

export function AgentDetails({
  citizen,
  townId,
  level,
  activeTab = 'overview',
  onTabChange,
  onClose,
  onLevelChange,
  className,
}: AgentDetailsProps) {
  const { userId, tier } = useUserStore();
  const canInhabit = useUserStore(selectCanInhabit());
  const [manifest, setManifest] = useState<CitizenManifest | null>(null);
  const [currentLOD, setCurrentLOD] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch manifest when citizen/LOD changes
  useEffect(() => {
    const fetchManifest = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await townApi.getCitizen(townId, citizen.name, currentLOD, userId || 'anonymous');
        setManifest(res.data.citizen);
      } catch (err) {
        console.error('Failed to fetch citizen:', err);
        setError('Failed to load details');
      } finally {
        setLoading(false);
      }
    };

    fetchManifest();
  }, [citizen.name, townId, currentLOD, userId]);

  // Upgrade LOD when switching to tabs that need it
  const handleTabChange = (tab: DetailsTab) => {
    const tabConfig = TAB_CONFIG.find((t) => t.id === tab);
    if (tabConfig && tabConfig.minLOD > currentLOD) {
      setCurrentLOD(tabConfig.minLOD);
    }
    onTabChange?.(tab);
  };

  // Compact: Hover card
  if (level === 'compact') {
    return (
      <CompactView
        citizen={citizen}
        onClick={() => onLevelChange?.('expanded')}
        className={className}
      />
    );
  }

  // Expanded/Full: Tabbed view
  return (
    <div
      className={cn(
        'flex flex-col bg-town-surface/50 rounded-lg border border-town-accent/30',
        level === 'full' && 'fixed inset-4 z-50 shadow-2xl',
        className
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-town-accent/20">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{getArchetypeEmoji(citizen.archetype)}</span>
          <div>
            <h2 className="text-lg font-bold">{citizen.name}</h2>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <span className={getArchetypeColor(citizen.archetype)}>{citizen.archetype}</span>
              <span>·</span>
              <span className={getPhaseColor(citizen.phase)}>{citizen.phase}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {level === 'expanded' && (
            <button
              onClick={() => onLevelChange?.('full')}
              className="p-2 hover:bg-town-accent/20 rounded transition-colors"
              title="Expand to full view"
            >
              ⛶
            </button>
          )}
          {level === 'full' && (
            <button
              onClick={() => onLevelChange?.('expanded')}
              className="p-2 hover:bg-town-accent/20 rounded transition-colors"
              title="Collapse to sidebar"
            >
              ⛶
            </button>
          )}
          <button
            onClick={onClose}
            className="p-2 hover:bg-town-accent/20 rounded transition-colors"
            title="Close"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-town-accent/20">
        {TAB_CONFIG.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabChange(tab.id)}
            className={cn(
              'flex-1 px-3 py-2 text-sm font-medium transition-colors',
              'hover:bg-town-accent/10',
              activeTab === tab.id
                ? 'border-b-2 border-town-highlight text-white'
                : 'text-gray-400'
            )}
          >
            <span className="mr-1">{tab.icon}</span>
            {level === 'full' && tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-pulse text-gray-500">Loading...</div>
          </div>
        ) : error ? (
          <div className="text-center text-red-400 py-8">
            <p>{error}</p>
            <button
              onClick={() => setCurrentLOD(0)}
              className="mt-2 text-sm text-gray-400 hover:text-white"
            >
              Reset to LOD 0
            </button>
          </div>
        ) : (
          <TabContent
            tab={activeTab}
            citizen={citizen}
            manifest={manifest}
            currentLOD={currentLOD}
            onUnlockLOD={setCurrentLOD}
            tier={tier}
            level={level}
          />
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-town-accent/20 flex items-center justify-between">
        <ExportButton citizen={citizen} manifest={manifest} />
        {canInhabit && (
          <Link
            to={`/town/${townId}/inhabit/${citizen.citizen_id}`}
            className="px-4 py-2 bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors"
          >
            🎭 INHABIT
          </Link>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Compact View (Hover Card)
// =============================================================================

interface CompactViewProps {
  citizen: CitizenCardJSON;
  onClick?: () => void;
  className?: string;
}

function CompactView({ citizen, onClick, className }: CompactViewProps) {
  return (
    <ElasticCard
      onClick={onClick}
      priority={2}
      className={cn('cursor-pointer hover:border-town-highlight/50 transition-colors', className)}
    >
      <div className="flex items-center gap-3">
        <span className="text-xl">{getArchetypeEmoji(citizen.archetype)}</span>
        <div className="flex-1 min-w-0">
          <div className="font-medium truncate">{citizen.name}</div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span className={getPhaseColor(citizen.phase)}>{citizen.phase}</span>
            <span>·</span>
            <span>{citizen.region}</span>
          </div>
        </div>
        {/* Mini sparkline placeholder */}
        <div className="w-16 h-4">
          <MiniSparkline values={[0.5, 0.6, 0.55, 0.7, 0.65, 0.8, citizen.capability]} />
        </div>
      </div>
    </ElasticCard>
  );
}

// =============================================================================
// Tab Content Router
// =============================================================================

interface TabContentProps {
  tab: DetailsTab;
  citizen: CitizenCardJSON;
  manifest: CitizenManifest | null;
  currentLOD: number;
  onUnlockLOD: (lod: number) => void;
  tier: string;
  level: DetailLevel;
}

function TabContent({ tab, citizen, manifest, currentLOD, onUnlockLOD, tier: _tier, level }: TabContentProps) {
  const tabConfig = TAB_CONFIG.find((t) => t.id === tab);

  // Check if tab requires higher LOD
  if (tabConfig && tabConfig.minLOD > currentLOD) {
    return (
      <LODGate level={tabConfig.minLOD} onUnlock={() => onUnlockLOD(tabConfig.minLOD)}>
        <div className="text-center py-8 text-gray-500">
          Unlock LOD {tabConfig.minLOD} to view {tabConfig.label}
        </div>
      </LODGate>
    );
  }

  switch (tab) {
    case 'overview':
      return <OverviewTab citizen={citizen} manifest={manifest} expanded={level === 'full'} />;
    case 'metrics':
      return <MetricsTab citizen={citizen} manifest={manifest} expanded={level === 'full'} />;
    case 'relationships':
      return <RelationshipsTab citizen={citizen} manifest={manifest} expanded={level === 'full'} />;
    case 'state':
      return <StateTab citizen={citizen} manifest={manifest} expanded={level === 'full'} />;
    case 'history':
      return <HistoryTab citizenId={citizen.citizen_id} expanded={level === 'full'} />;
    default:
      return null;
  }
}

// =============================================================================
// Helpers
// =============================================================================

function getArchetypeEmoji(archetype: string): string {
  switch (archetype) {
    case 'Builder':
      return '🔨';
    case 'Trader':
      return '💼';
    case 'Healer':
      return '💚';
    case 'Scholar':
      return '📚';
    case 'Watcher':
      return '👁️';
    case 'Scout':
      return '🔍';
    case 'Sage':
      return '🧙';
    case 'Spark':
      return '✨';
    case 'Steady':
      return '⚓';
    case 'Sync':
      return '🔗';
    default:
      return '👤';
  }
}

function MiniSparkline({ values }: { values: number[] }) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const height = 16;
  const width = 64;
  const step = width / (values.length - 1);

  const points = values
    .map((v, i) => {
      const x = i * step;
      const y = height - ((v - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');

  return (
    <svg width={width} height={height} className="text-town-highlight">
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default AgentDetails;
