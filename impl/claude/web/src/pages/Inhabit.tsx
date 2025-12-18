/**
 * Inhabit: Citizen inhabitation view.
 *
 * Allows users to "inhabit" a citizen and interact with the town through their perspective.
 * Uses ElasticContainer for inhabitant view with ElasticCard patterns.
 *
 * Layout:
 * - Desktop (>1024px): Citizen focus | Interaction panels (resizable)
 * - Tablet (768-1024px): Citizen focus | Panels (collapsible)
 * - Mobile (<768px): Full citizen focus + floating actions
 *
 * Session 8: Elastic UI Refactor
 * @see plans/web-refactor/elastic-primitives.md
 * @see plans/web-refactor/elastic-audit-report.md
 */

import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ElasticSplit,
  ElasticContainer,
  ElasticCard,
  ElasticPlaceholder,
  useWindowLayout,
} from '@/components/elastic';
import { PersonalityLoading } from '@/components/joy';
import { getArchetypeColor, getEmptyState, TOOLTIPS } from '@/constants';
import type { CitizenManifest, InhabitStatus, InhabitActionResult, Eigenvectors } from '@/api/types';

type Density = 'compact' | 'comfortable' | 'spacious';

export default function Inhabit() {
  const { citizenId } = useParams<{ citizenId: string }>();
  const navigate = useNavigate();
  const { density, isMobile, isDesktop } = useWindowLayout();

  // State
  // Note: setCitizen, setInhabitStatus, setActionResult will be used once API is integrated
  const [citizen, _setCitizen] = useState<CitizenManifest | null>(null);
  const [inhabitStatus, _setInhabitStatus] = useState<InhabitStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionResult, _setActionResult] = useState<InhabitActionResult | null>(null);

  // Silence unused variable warnings until API integration
  void _setCitizen;
  void _setInhabitStatus;
  void _setActionResult;

  // Load citizen data
  useEffect(() => {
    if (!citizenId) return;

    const loadCitizen = async () => {
      setIsLoading(true);
      setError(null);

      // Simulated load - would use API
      await new Promise((resolve) => setTimeout(resolve, 500));

      // For now, show empty state
      setIsLoading(false);
    };

    loadCitizen();
  }, [citizenId]);

  const hasData = citizen !== null;

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Inhabit Header */}
      <InhabitHeader
        citizenName={citizen?.name}
        citizenId={citizenId}
        status={inhabitStatus}
        onExit={() => navigate(-1)}
      />

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <ElasticSplit
          direction="horizontal"
          defaultRatio={0.65}
          collapseAt={768}
          collapsePriority="secondary"
          minPaneSize={isMobile ? 200 : 280}
          resizable={isDesktop}
          primary={
            /* Citizen Focus Panel */
            <ElasticContainer
              layout="stack"
              overflow="scroll"
              padding={{ sm: 'var(--elastic-gap-sm)', md: 'var(--elastic-gap-lg)' }}
              className="h-full bg-town-bg"
            >
              {isLoading && (
                <div className="h-full flex items-center justify-center" style={{ minHeight: isMobile ? '300px' : '400px' }}>
                  <PersonalityLoading jewel="coalition" action="inhabit" />
                </div>
              )}

              {error && (
                <ElasticPlaceholder
                  for="agent"
                  state="error"
                  error={error}
                  onRetry={() => {
                    setIsLoading(true);
                    setError(null);
                  }}
                />
              )}

              {!isLoading && !error && !hasData && (
                <EmptyInhabit citizenId={citizenId} density={density} />
              )}

              {!isLoading && !error && hasData && citizen && (
                <CitizenFocusView
                  citizen={citizen}
                  status={inhabitStatus}
                  actionResult={actionResult}
                  density={density}
                  onAction={(action) => {
                    // TODO: implement action
                    console.log('Action:', action);
                  }}
                />
              )}
            </ElasticContainer>
          }
          secondary={
            /* Interaction & Status Panel */
            <ElasticContainer
              layout="stack"
              direction="vertical"
              gap={isMobile ? 'var(--elastic-gap-sm)' : 'var(--elastic-gap-md)'}
              padding={isMobile ? 'var(--elastic-gap-sm)' : 'var(--elastic-gap-md)'}
              overflow="scroll"
              className="h-full bg-town-surface/30 border-l border-town-accent/30"
            >
              {/* Status Card */}
              <StatusPanel status={inhabitStatus} density={density} />

              {/* Actions Panel */}
              <ActionsPanel
                onAction={(action) => {
                  console.log('Action:', action);
                }}
                disabled={!inhabitStatus}
                density={density}
              />

              {/* Consent & Debt Panel */}
              {inhabitStatus && <ConsentPanel consent={inhabitStatus.consent} density={density} />}
            </ElasticContainer>
          }
        />
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface InhabitHeaderProps {
  citizenName?: string;
  citizenId?: string;
  status: InhabitStatus | null;
  onExit: () => void;
}

function InhabitHeader({ citizenName, citizenId, status, onExit }: InhabitHeaderProps) {
  return (
    <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={onExit}
            className="text-gray-400 hover:text-white transition-colors"
          >
            &larr; Exit
          </button>
          <div className="h-6 w-px bg-town-accent/30" />
          <h1 className="font-semibold">
            {citizenName ? `Inhabiting: ${citizenName}` : `Citizen ${citizenId || 'Unknown'}`}
          </h1>
          {status && (
            <span className="text-sm text-gray-400">
              {Math.floor(status.time_remaining / 60)}m remaining
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {status?.expired && (
            <span className="px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs font-medium">
              Session Expired
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

interface EmptyInhabitProps {
  citizenId?: string;
  density: Density;
}

function EmptyInhabit({ citizenId, density }: EmptyInhabitProps) {
  const isCompact = density === 'compact';
  // Use semantic empty state messages
  const emptyState = getEmptyState('noCitizens');

  return (
    <div className={`h-full flex flex-col items-center justify-center text-center ${isCompact ? 'p-4' : 'p-8'}`}>
      <span className={`${isCompact ? 'text-4xl mb-2' : 'text-6xl mb-4'}`}>👤</span>
      <h2 className={`font-medium text-white ${isCompact ? 'text-lg mb-1' : 'text-xl mb-2'}`}>
        {citizenId ? 'Ready to Inhabit' : emptyState.title}
      </h2>
      <p className={`text-gray-400 max-w-md ${isCompact ? 'text-xs mb-4' : 'mb-6'}`}>
        {citizenId
          ? `Connect with citizen ${citizenId} to see the town through their eyes.`
          : emptyState.description}
      </p>
      <Link
        to="/town/demo"
        className={`bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors ${
          isCompact ? 'px-3 py-1.5 text-sm' : 'px-4 py-2'
        }`}
      >
        {citizenId ? 'Begin Inhabitation' : emptyState.action || 'Browse Town'}
      </Link>
    </div>
  );
}

interface CitizenFocusViewProps {
  citizen: CitizenManifest;
  status: InhabitStatus | null;
  actionResult: InhabitActionResult | null;
  density: Density;
  onAction: (action: string) => void;
}

function CitizenFocusView({
  citizen,
  status: _status,
  actionResult,
  density,
  onAction: _onAction,
}: CitizenFocusViewProps) {
  // Note: _status and _onAction will be used for action handling
  void _status;
  void _onAction;
  const archetypeColor = getArchetypeColor(citizen.archetype || '');
  const isCompact = density === 'compact';
  void isCompact; // Will be used for density-aware styling

  return (
    <div className="space-y-6">
      {/* Main Citizen Card */}
      <ElasticCard
        priority={10}
        minContent="summary"
        shrinkBehavior="stack"
        icon={<span className="text-4xl">🧑</span>}
        title={citizen.name}
        summary={`${citizen.archetype || 'Unknown'} · ${citizen.region}`}
        className="bg-town-surface/50"
      >
        <div className="space-y-4 mt-4">
          {/* Phase indicator */}
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Phase:</span>
            <span
              className="px-2 py-0.5 rounded text-xs font-medium"
              style={{ backgroundColor: archetypeColor + '30', color: archetypeColor }}
            >
              {citizen.phase}
            </span>
          </div>

          {/* Mood */}
          {citizen.mood && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-400">Mood:</span>
              <span className="text-sm text-white">{citizen.mood}</span>
            </div>
          )}

          {/* Cosmotechnics */}
          {citizen.cosmotechnics && (
            <div>
              <span className="text-sm text-gray-400 block mb-1">Cosmotechnics:</span>
              <p className="text-sm text-gray-300 italic">{citizen.cosmotechnics}</p>
            </div>
          )}

          {/* Metaphor */}
          {citizen.metaphor && (
            <div>
              <span className="text-sm text-gray-400 block mb-1">Metaphor:</span>
              <p className="text-sm text-gray-300">{citizen.metaphor}</p>
            </div>
          )}
        </div>
      </ElasticCard>

      {/* Eigenvectors */}
      {citizen.eigenvectors && (
        <ElasticCard
          priority={5}
          minContent="title"
          shrinkBehavior="collapse"
          title="Eigenvectors"
          className="bg-town-surface/50"
        >
          <EigenvectorGrid eigenvectors={citizen.eigenvectors} />
        </ElasticCard>
      )}

      {/* Relationships */}
      {citizen.relationships && Object.keys(citizen.relationships).length > 0 && (
        <ElasticCard
          priority={5}
          minContent="title"
          shrinkBehavior="collapse"
          title="Relationships"
          className="bg-town-surface/50"
        >
          <RelationshipsList relationships={citizen.relationships} />
        </ElasticCard>
      )}

      {/* Action Result */}
      {actionResult && (
        <div
          className={`p-4 rounded-lg ${
            actionResult.success
              ? 'bg-green-500/10 border border-green-500/30'
              : 'bg-red-500/10 border border-red-500/30'
          }`}
        >
          <p className={actionResult.success ? 'text-green-400' : 'text-red-400'}>
            {actionResult.message}
          </p>
        </div>
      )}
    </div>
  );
}

interface EigenvectorGridProps {
  eigenvectors: Eigenvectors;
}

function EigenvectorGrid({ eigenvectors }: EigenvectorGridProps) {
  const entries = Object.entries(eigenvectors);

  return (
    <div className="grid grid-cols-2 gap-2 mt-3">
      {entries.map(([key, value]) => (
        <div key={key} className="text-sm">
          <div className="flex justify-between mb-1">
            <span className="text-gray-400 capitalize">{key}</span>
            <span className="text-gray-300 font-mono">{(value * 100).toFixed(0)}%</span>
          </div>
          <div className="w-full h-1.5 bg-town-bg rounded-full">
            <div
              className="h-full rounded-full bg-town-highlight transition-all"
              style={{ width: `${value * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

interface RelationshipsListProps {
  relationships: Record<string, number>;
}

function RelationshipsList({ relationships }: RelationshipsListProps) {
  const entries = Object.entries(relationships).sort((a, b) => b[1] - a[1]);

  return (
    <div className="space-y-2 mt-3">
      {entries.slice(0, 5).map(([name, strength]) => (
        <div key={name} className="flex items-center justify-between text-sm">
          <span className="text-gray-300">{name}</span>
          <span
            className={`font-mono ${
              strength > 0.5 ? 'text-green-400' : strength > 0 ? 'text-gray-400' : 'text-red-400'
            }`}
          >
            {(strength * 100).toFixed(0)}%
          </span>
        </div>
      ))}
    </div>
  );
}

interface StatusPanelProps {
  status: InhabitStatus | null;
  density: Density;
}

function StatusPanel({ status, density }: StatusPanelProps) {
  const isCompact = density === 'compact';

  if (!status) {
    const emptyState = getEmptyState('noSessions');
    return (
      <div className={`rounded-lg bg-town-surface/50 border border-town-accent/30 ${isCompact ? 'p-3' : 'p-4'}`}>
        <h3 className={`font-medium text-gray-300 ${isCompact ? 'text-xs mb-1' : 'text-sm mb-2'}`}>Session Status</h3>
        <p className={`text-gray-500 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>{emptyState.description}</p>
      </div>
    );
  }

  return (
    <div className={`rounded-lg bg-town-surface/50 border border-town-accent/30 ${isCompact ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-medium text-gray-300 ${isCompact ? 'text-xs mb-2' : 'text-sm mb-3'}`}>Session Status</h3>
      <div className={`${isCompact ? 'space-y-1 text-xs' : 'space-y-2 text-sm'}`}>
        <div className="flex justify-between">
          <span className="text-gray-400">Tier</span>
          <span className="text-gray-300">{status.tier}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Time Left</span>
          <span className="text-gray-300">{Math.floor(status.time_remaining / 60)}m</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Actions</span>
          <span className="text-gray-300">{status.actions_count}</span>
        </div>
      </div>
    </div>
  );
}

interface ActionsPanelProps {
  onAction: (action: string) => void;
  disabled: boolean;
  density: Density;
}

function ActionsPanel({ onAction, disabled, density }: ActionsPanelProps) {
  const isCompact = density === 'compact';

  const actions = [
    { id: 'speak', label: 'Speak', icon: '💬' },
    { id: 'move', label: 'Move', icon: '🚶' },
    { id: 'interact', label: 'Interact', icon: '🤝' },
    { id: 'observe', label: 'Observe', icon: '👁️' },
  ];

  return (
    <div className={`rounded-lg bg-town-surface/50 border border-town-accent/30 ${isCompact ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-medium text-gray-300 ${isCompact ? 'text-xs mb-2' : 'text-sm mb-3'}`}>Actions</h3>
      <div className={`grid grid-cols-2 ${isCompact ? 'gap-1.5' : 'gap-2'}`}>
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction(action.id)}
            disabled={disabled}
            className={`rounded-lg bg-town-bg/50 hover:bg-town-accent/30 transition-colors flex flex-col items-center disabled:opacity-50 disabled:cursor-not-allowed ${
              isCompact ? 'p-2 gap-0.5' : 'p-3 gap-1 text-sm'
            }`}
          >
            <span className={isCompact ? 'text-base' : 'text-lg'}>{action.icon}</span>
            <span className={`text-gray-300 ${isCompact ? 'text-[10px]' : ''}`}>{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

interface ConsentPanelProps {
  consent: InhabitStatus['consent'];
  density: Density;
}

function ConsentPanel({ consent, density }: ConsentPanelProps) {
  const isCompact = density === 'compact';

  return (
    <div className={`rounded-lg bg-town-surface/50 border border-town-accent/30 ${isCompact ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-medium text-gray-300 ${isCompact ? 'text-xs mb-2' : 'text-sm mb-3'}`}>Consent Status</h3>
      <div className={`${isCompact ? 'space-y-1 text-xs' : 'space-y-2 text-sm'}`}>
        <div className="flex justify-between">
          <span className="text-gray-400">Debt</span>
          <span
            className={consent.debt > 50 ? 'text-yellow-400' : 'text-gray-300'}
            title={TOOLTIPS.consentDebt(consent.debt / 100)}
          >
            {consent.debt}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Status</span>
          <span className="text-gray-300">{consent.status}</span>
        </div>
        {consent.at_rupture && (
          <div className={`rounded bg-red-500/10 text-red-400 mt-2 ${isCompact ? 'p-1.5 text-[10px]' : 'p-2 text-xs'}`}>
            At rupture threshold! Further actions may damage the relationship.
          </div>
        )}
      </div>
    </div>
  );
}
