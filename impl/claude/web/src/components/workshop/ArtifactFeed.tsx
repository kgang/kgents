import { useState } from 'react';
import { useWorkshopStore } from '@/stores/workshopStore';
import { BUILDER_COLORS, BUILDER_ICONS } from '@/api/types';
import type { BuilderArchetype, WorkshopEventType, WorkshopArtifact } from '@/api/types';
import { cn } from '@/lib/utils';

/**
 * ArtifactFeed displays workshop events and artifacts in a scrollable feed.
 * Now with tabs for Events/Artifacts and expandable artifact detail.
 */
export function ArtifactFeed() {
  const { events, artifacts } = useWorkshopStore();
  const [activeTab, setActiveTab] = useState<'events' | 'artifacts'>('events');
  const [expandedArtifact, setExpandedArtifact] = useState<string | null>(null);

  return (
    <div className="h-[calc(100%-40px)] flex flex-col">
      {/* Tab Bar */}
      <div className="flex border-b border-town-accent/30 text-xs">
        <button
          onClick={() => setActiveTab('events')}
          className={cn(
            'flex-1 px-3 py-1.5 transition-colors',
            activeTab === 'events'
              ? 'bg-town-accent/20 text-white border-b-2 border-town-highlight'
              : 'text-gray-400 hover:bg-town-accent/10'
          )}
        >
          Events ({events.length})
        </button>
        <button
          onClick={() => setActiveTab('artifacts')}
          className={cn(
            'flex-1 px-3 py-1.5 transition-colors',
            activeTab === 'artifacts'
              ? 'bg-town-accent/20 text-white border-b-2 border-town-highlight'
              : 'text-gray-400 hover:bg-town-accent/10'
          )}
        >
          Artifacts ({artifacts.length})
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1 text-xs">
        {activeTab === 'events' ? (
          events.length === 0 ? (
            <div className="text-center text-gray-500 py-4">
              <p>No events yet</p>
              <p className="mt-1">Assign a task to start</p>
            </div>
          ) : (
            events.slice(0, 50).map((event, index) => (
              <EventItem
                key={`${event.timestamp}-${index}`}
                type={event.type}
                builder={event.builder}
                message={event.message}
                phase={event.phase}
                dialogue={event.metadata.dialogue as string | undefined}
              />
            ))
          )
        ) : artifacts.length === 0 ? (
          <div className="text-center text-gray-500 py-4">
            <p>No artifacts yet</p>
            <p className="mt-1">Builders produce artifacts as they work</p>
          </div>
        ) : (
          artifacts.map((artifact) => (
            <ArtifactItem
              key={artifact.id}
              artifact={artifact}
              isExpanded={expandedArtifact === artifact.id}
              onToggle={() =>
                setExpandedArtifact(expandedArtifact === artifact.id ? null : artifact.id)
              }
            />
          ))
        )}
      </div>
    </div>
  );
}

interface EventItemProps {
  type: WorkshopEventType;
  builder: string | null;
  message: string;
  phase: string;
  dialogue?: string;
}

function EventItem({ type, builder, message, phase, dialogue }: EventItemProps) {
  const icon = getEventIcon(type);
  const color = builder ? BUILDER_COLORS[builder as BuilderArchetype] || '#6b7280' : '#6b7280';
  const builderIcon = builder ? BUILDER_ICONS[builder as BuilderArchetype] || '👤' : '';

  return (
    <div
      className={cn(
        'flex items-start gap-2 px-2 py-1 rounded',
        type === 'TASK_COMPLETED' && 'bg-emerald-900/20',
        type === 'HANDOFF' && 'bg-pink-900/20',
        type === 'ERROR' && 'bg-red-900/20'
      )}
    >
      {/* Event Icon */}
      <span className="text-base shrink-0">{icon}</span>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Builder & Phase */}
        {builder && (
          <div className="flex items-center gap-1 text-gray-400">
            <span>{builderIcon}</span>
            <span style={{ color }}>{builder}</span>
            <span className="text-gray-600">• {phase}</span>
          </div>
        )}

        {/* Message */}
        <p className="text-gray-300 truncate">{message}</p>

        {/* Dialogue (if present) */}
        {dialogue && <p className="text-purple-300 italic mt-1">"{dialogue}"</p>}
      </div>
    </div>
  );
}

interface ArtifactItemProps {
  artifact: WorkshopArtifact;
  isExpanded: boolean;
  onToggle: () => void;
}

function ArtifactItem({ artifact, isExpanded, onToggle }: ArtifactItemProps) {
  const color = BUILDER_COLORS[artifact.builder as BuilderArchetype] || '#6b7280';
  const builderIcon = BUILDER_ICONS[artifact.builder as BuilderArchetype] || '📦';

  // Format content for display
  const contentPreview = formatArtifactContent(artifact.content, false);
  const contentFull = formatArtifactContent(artifact.content, true);

  return (
    <div
      className={cn(
        'rounded border border-town-accent/30 overflow-hidden transition-all',
        isExpanded ? 'bg-town-surface/50' : 'bg-town-surface/20 hover:bg-town-surface/30'
      )}
    >
      {/* Header - always visible */}
      <button onClick={onToggle} className="w-full px-3 py-2 flex items-center gap-2 text-left">
        <span className="text-lg">{builderIcon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span style={{ color }} className="font-medium">
              {artifact.builder}
            </span>
            <span className="text-gray-500">•</span>
            <span className={getPhaseTextColor(artifact.phase)}>{artifact.phase}</span>
          </div>
          {!isExpanded && (
            <p className="text-gray-400 truncate text-xs mt-0.5">{contentPreview}</p>
          )}
        </div>
        <span className="text-gray-500 text-xs">{isExpanded ? '▼' : '▶'}</span>
      </button>

      {/* Expanded content */}
      {isExpanded && (
        <div className="px-3 pb-3 border-t border-town-accent/20">
          <div className="mt-2 bg-town-bg/50 rounded p-2 font-mono text-xs text-gray-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
            {contentFull}
          </div>
          <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
            <span>ID: {artifact.id.slice(0, 8)}...</span>
            <span>•</span>
            <span>{new Date(artifact.created_at).toLocaleTimeString()}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function formatArtifactContent(content: unknown, full: boolean): string {
  if (content === null || content === undefined) {
    return 'No content';
  }

  if (typeof content === 'string') {
    return full ? content : content.slice(0, 80) + (content.length > 80 ? '...' : '');
  }

  if (typeof content === 'object') {
    const json = JSON.stringify(content, null, full ? 2 : 0);
    return full ? json : json.slice(0, 80) + (json.length > 80 ? '...' : '');
  }

  return String(content);
}

function getEventIcon(type: WorkshopEventType): string {
  switch (type) {
    case 'TASK_ASSIGNED':
      return '📋';
    case 'PLAN_CREATED':
      return '📝';
    case 'PHASE_STARTED':
      return '▶️';
    case 'PHASE_COMPLETED':
      return '✅';
    case 'HANDOFF':
      return '🤝';
    case 'ARTIFACT_PRODUCED':
      return '📦';
    case 'USER_QUERY':
      return '❓';
    case 'USER_RESPONSE':
      return '💬';
    case 'TASK_COMPLETED':
      return '🎉';
    case 'ERROR':
      return '⚠️';
    default:
      return '•';
  }
}

function getPhaseTextColor(phase: string): string {
  switch (phase) {
    case 'EXPLORING':
      return 'text-green-400';
    case 'DESIGNING':
      return 'text-purple-400';
    case 'PROTOTYPING':
      return 'text-amber-400';
    case 'REFINING':
      return 'text-blue-400';
    case 'INTEGRATING':
      return 'text-pink-400';
    default:
      return 'text-gray-400';
  }
}

export default ArtifactFeed;
