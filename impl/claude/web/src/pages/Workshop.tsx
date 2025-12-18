/**
 * Workshop: Builder agents working on tasks.
 *
 * Uses ElasticSplit for responsive layout:
 * - Builder canvas (primary) | Tool panels (secondary)
 * - Stacks vertically on mobile (collapseAt: 768px)
 *
 * Session 8: Elastic UI Refactor
 * @see plans/web-refactor/elastic-primitives.md
 * @see plans/web-refactor/elastic-audit-report.md
 */

import { useState } from 'react';
import {
  ElasticSplit,
  ElasticContainer,
  ElasticCard,
  ElasticPlaceholder,
  useWindowLayout,
} from '@/components/elastic';
import { PersonalityLoading } from '@/components/joy';
import { getBuilderColor, getEmptyState } from '@/constants';
import type {
  WorkshopStatus,
  WorkshopPhase,
  BuilderSummary,
  WorkshopArtifact,
} from '@/api/types';

type Density = 'compact' | 'comfortable' | 'spacious';

// =============================================================================
// Constants - Density-aware
// =============================================================================

/** Maximum artifacts shown by density */
const MAX_ARTIFACTS = {
  compact: 5,
  comfortable: 8,
  spacious: 10,
} as const;

/** Minimum grid item width by density */
const MIN_GRID_ITEM_WIDTH = {
  compact: 150,
  comfortable: 180,
  spacious: 200,
} as const;

/** Builder personality icons */
const BUILDER_ICONS_MAP: Record<string, string> = {
  Scout: '🔍',
  Sage: '📐',
  Spark: '💡',
  Steady: '🛠️',
  Sync: '🔄',
};

export default function Workshop() {
  // Layout context
  const { density, isMobile, isDesktop } = useWindowLayout();

  // Placeholder state - would come from API/streaming
  const [status] = useState<WorkshopStatus | null>(null);
  const [isLoading] = useState(false);
  const [error] = useState<string | null>(null);

  // Determine if we have data
  const hasData = status !== null;

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      {/* Workshop Header */}
      <WorkshopHeader
        phase={status?.phase || 'IDLE'}
        taskDescription={status?.active_task?.description}
        isRunning={status?.is_running || false}
      />

      {/* Main Content - ElasticSplit for canvas | sidebar */}
      <div className="flex-1 overflow-hidden">
        <ElasticSplit
          direction="horizontal"
          defaultRatio={0.7}
          collapseAt={768}
          collapsePriority="secondary"
          minPaneSize={isMobile ? 200 : 300}
          resizable={isDesktop}
          primary={
            /* Builder Canvas */
            <ElasticContainer
              layout="stack"
              overflow="scroll"
              padding={{ sm: 'var(--elastic-gap-sm)', md: 'var(--elastic-gap-md)' }}
              className="h-full bg-town-bg"
            >
              {isLoading && (
                <div className="h-full flex items-center justify-center" style={{ minHeight: isMobile ? '200px' : '300px' }}>
                  <PersonalityLoading jewel="forge" action="create" />
                </div>
              )}

              {error && (
                <ElasticPlaceholder
                  for="agent"
                  state="error"
                  error={error}
                  onRetry={() => {
                    /* TODO: retry logic */
                  }}
                />
              )}

              {!isLoading && !error && !hasData && (
                <EmptyWorkshop density={density} />
              )}

              {!isLoading && !error && hasData && status && (
                <BuilderCanvas builders={status.builders} artifacts={status.artifacts} density={density} />
              )}
            </ElasticContainer>
          }
          secondary={
            /* Tool Panels Sidebar */
            <ElasticContainer
              layout="stack"
              direction="vertical"
              overflow="scroll"
              padding={isMobile ? 'var(--elastic-gap-sm)' : 'var(--elastic-gap-md)'}
              className="h-full bg-town-surface/30 border-l border-town-accent/30"
            >
              {/* Builder Roster */}
              <BuilderRosterPanel builders={status?.builders || []} density={density} />

              {/* Artifacts List */}
              <ArtifactsPanel artifacts={status?.artifacts || []} density={density} />

              {/* Metrics */}
              {status?.metrics && <MetricsPanel metrics={status.metrics} density={density} />}
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

interface WorkshopHeaderProps {
  phase: WorkshopPhase;
  taskDescription?: string;
  isRunning: boolean;
}

function WorkshopHeader({ phase, taskDescription, isRunning }: WorkshopHeaderProps) {
  return (
    <div className="bg-town-surface/50 border-b border-town-accent/30 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="font-semibold text-lg">Workshop</h1>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <span
              className={`px-2 py-0.5 rounded text-xs font-medium ${
                isRunning ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
              }`}
            >
              {phase}
            </span>
            {taskDescription && (
              <>
                <span>·</span>
                <span className="truncate max-w-md">{taskDescription}</span>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            disabled={!isRunning}
            className="px-3 py-1.5 bg-town-accent/30 rounded text-sm hover:bg-town-accent/50 transition-colors disabled:opacity-50"
          >
            {isRunning ? 'Stop' : 'Start Task'}
          </button>
        </div>
      </div>
    </div>
  );
}

function EmptyWorkshop({ density }: { density: Density }) {
  const isCompact = density === 'compact';
  // Use semantic empty state - Workshop maps to Atelier's artisan vocabulary
  const emptyState = getEmptyState('noArtisans');

  return (
    <div className={`h-full flex flex-col items-center justify-center text-center ${isCompact ? 'p-4' : 'p-8'}`}>
      <span className={`${isCompact ? 'text-4xl mb-2' : 'text-6xl mb-4'}`}>🏗️</span>
      <h2 className={`font-medium text-white ${isCompact ? 'text-lg mb-1' : 'text-xl mb-2'}`}>{emptyState.title}</h2>
      <p className={`text-gray-400 max-w-md ${isCompact ? 'text-xs mb-4' : 'mb-6'}`}>
        {isCompact
          ? emptyState.description
          : `${emptyState.description} They'll collaborate through phases: Exploring, Designing, Prototyping, Refining, and Integrating.`}
      </p>
      <button className={`bg-town-highlight hover:bg-town-highlight/80 rounded-lg font-medium transition-colors ${
        isCompact ? 'px-3 py-1.5 text-sm' : 'px-4 py-2'
      }`}>
        {emptyState.action || 'Create Task'}
      </button>
    </div>
  );
}

interface BuilderCanvasProps {
  builders: BuilderSummary[];
  artifacts: WorkshopArtifact[];
  density: Density;
}

function BuilderCanvas({ builders, density }: BuilderCanvasProps) {
  const minItemWidth = MIN_GRID_ITEM_WIDTH[density];
  const isCompact = density === 'compact';

  return (
    <div className="h-full">
      <ElasticContainer layout="grid" gap={isCompact ? 'var(--elastic-gap-sm)' : 'var(--elastic-gap-md)'} minItemWidth={minItemWidth}>
        {builders.map((builder) => (
          <ElasticCard
            key={builder.archetype}
            priority={builder.is_active ? 10 : 5}
            minContent="title"
            shrinkBehavior="collapse"
            icon={<span className={isCompact ? 'text-lg' : 'text-2xl'}>{BUILDER_ICONS_MAP[builder.archetype]}</span>}
            title={builder.name}
            summary={`${builder.archetype} · ${builder.phase}`}
            isSelected={builder.is_active}
          >
            <div className={isCompact ? 'text-xs' : 'text-sm'}>
              <div
                className="w-full h-1 rounded-full mt-2"
                style={{ backgroundColor: getBuilderColor(builder.archetype) + '40' }}
              >
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: builder.is_active ? '60%' : '0%',
                    backgroundColor: getBuilderColor(builder.archetype),
                  }}
                />
              </div>
            </div>
          </ElasticCard>
        ))}
      </ElasticContainer>
    </div>
  );
}

interface BuilderRosterPanelProps {
  builders: BuilderSummary[];
  density: Density;
}

function BuilderRosterPanel({ builders, density }: BuilderRosterPanelProps) {
  const isCompact = density === 'compact';

  if (builders.length === 0) {
    const emptyState = getEmptyState('noArtisans');
    return (
      <div className={`rounded-lg bg-town-surface/50 border border-town-accent/30 ${isCompact ? 'p-3' : 'p-4'}`}>
        <h3 className={`font-medium text-gray-300 ${isCompact ? 'text-xs mb-1' : 'text-sm mb-2'}`}>Builders</h3>
        <p className={`text-gray-500 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>{emptyState.description}</p>
      </div>
    );
  }

  return (
    <div className={`rounded-lg bg-town-surface/50 border border-town-accent/30 ${isCompact ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-medium text-gray-300 ${isCompact ? 'text-xs mb-2' : 'text-sm mb-3'}`}>Builders</h3>
      <div className={isCompact ? 'space-y-1' : 'space-y-2'}>
        {builders.map((b) => (
          <div
            key={b.archetype}
            className={`flex items-center gap-2 ${isCompact ? 'text-xs' : 'text-sm'}`}
            style={{ color: b.is_active ? getBuilderColor(b.archetype) : undefined }}
          >
            <span className={isCompact ? 'text-sm' : ''}>{BUILDER_ICONS_MAP[b.archetype]}</span>
            <span className={b.is_active ? 'font-medium' : 'text-gray-400'}>{b.name}</span>
            {b.is_in_specialty && <span className={`text-yellow-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>★</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

interface ArtifactsPanelProps {
  artifacts: WorkshopArtifact[];
  density: Density;
}

function ArtifactsPanel({ artifacts, density }: ArtifactsPanelProps) {
  const maxArtifacts = MAX_ARTIFACTS[density];
  const isCompact = density === 'compact';

  return (
    <div className={`rounded-lg bg-town-surface/50 border border-town-accent/30 ${isCompact ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-medium text-gray-300 ${isCompact ? 'text-xs mb-2' : 'text-sm mb-3'}`}>
        Artifacts ({artifacts.length})
      </h3>
      {artifacts.length === 0 ? (
        <p className={`text-gray-500 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>{getEmptyState('noCreations').description}</p>
      ) : (
        <div className={`space-y-1 overflow-y-auto ${isCompact ? 'max-h-32' : 'max-h-48'}`}>
          {artifacts.slice(0, maxArtifacts).map((artifact) => (
            <div key={artifact.id} className={`rounded bg-town-bg/50 ${isCompact ? 'p-1.5 text-[10px]' : 'text-xs p-2'}`}>
              <div className="flex items-center justify-between">
                <span className="text-gray-300 font-mono">{artifact.phase}</span>
                <span className="text-gray-500">{artifact.builder}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

interface MetricsPanelProps {
  metrics: {
    total_steps: number;
    total_events: number;
    total_tokens: number;
    artifacts_produced: number;
    phases_completed: number;
    handoffs: number;
  };
  density: Density;
}

function MetricsPanel({ metrics, density }: MetricsPanelProps) {
  const isCompact = density === 'compact';

  return (
    <div className={`rounded-lg bg-town-surface/50 border border-town-accent/30 ${isCompact ? 'p-3' : 'p-4'}`}>
      <h3 className={`font-medium text-gray-300 ${isCompact ? 'text-xs mb-2' : 'text-sm mb-3'}`}>Metrics</h3>
      <div className={`grid grid-cols-2 ${isCompact ? 'gap-1 text-[10px]' : 'gap-2 text-xs'}`}>
        <MetricItem label="Steps" value={metrics.total_steps} isCompact={isCompact} />
        <MetricItem label="Events" value={metrics.total_events} isCompact={isCompact} />
        <MetricItem label="Tokens" value={metrics.total_tokens.toLocaleString()} isCompact={isCompact} />
        <MetricItem label="Artifacts" value={metrics.artifacts_produced} isCompact={isCompact} />
        <MetricItem label="Phases" value={metrics.phases_completed} isCompact={isCompact} />
        <MetricItem label="Handoffs" value={metrics.handoffs} isCompact={isCompact} />
      </div>
    </div>
  );
}

function MetricItem({ label, value, isCompact }: { label: string; value: string | number; isCompact?: boolean }) {
  return (
    <div className={`rounded bg-town-bg/50 ${isCompact ? 'p-1.5' : 'p-2'}`}>
      <div className="text-gray-500">{label}</div>
      <div className="font-mono text-gray-300">{value}</div>
    </div>
  );
}
