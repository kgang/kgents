import { useWorkshopStore } from '@/stores/workshopStore';
import { BUILDER_COLORS, BUILDER_ICONS } from '@/api/types';
import type { BuilderArchetype, WorkshopEventType } from '@/api/types';
import { cn } from '@/lib/utils';

/**
 * ArtifactFeed displays workshop events and artifacts in a scrollable feed.
 */
export function ArtifactFeed() {
  const { events, artifacts } = useWorkshopStore();

  return (
    <div className="h-[calc(100%-40px)] overflow-y-auto p-2 space-y-1 text-xs">
      {events.length === 0 && artifacts.length === 0 ? (
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
      )}
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
  const color = builder
    ? BUILDER_COLORS[builder as BuilderArchetype] || '#6b7280'
    : '#6b7280';
  const builderIcon = builder
    ? BUILDER_ICONS[builder as BuilderArchetype] || '👤'
    : '';

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
        {dialogue && (
          <p className="text-purple-300 italic mt-1">"{dialogue}"</p>
        )}
      </div>
    </div>
  );
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

export default ArtifactFeed;
