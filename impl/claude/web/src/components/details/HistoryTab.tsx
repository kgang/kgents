/**
 * HistoryTab: Trace timeline for citizen events.
 *
 * Shows chronological history of citizen actions and state changes.
 */

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

export interface HistoryTabProps {
  citizenId: string;
  expanded?: boolean;
}

// Mock history data (in production, fetch from API)
interface HistoryEvent {
  id: string;
  timestamp: Date;
  type: EventType;
  description: string;
  details?: Record<string, unknown>;
}

type EventType = 'action' | 'transition' | 'interaction' | 'evolution' | 'coalition';
type TimeFilter = 'all' | '1h' | '24h' | '7d';

export function HistoryTab({ citizenId, expanded = false }: HistoryTabProps) {
  const [events, setEvents] = useState<HistoryEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<TimeFilter>('all');
  const [typeFilters, setTypeFilters] = useState<Set<EventType>>(new Set(['action', 'transition', 'interaction', 'evolution', 'coalition']));

  // Load history (mock for now)
  useEffect(() => {
    setLoading(true);
    // Simulate API call
    const mockEvents = generateMockHistory(citizenId, 50);
    setTimeout(() => {
      setEvents(mockEvents);
      setLoading(false);
    }, 300);
  }, [citizenId]);

  // Filter events
  const filteredEvents = events.filter((event) => {
    // Type filter
    if (!typeFilters.has(event.type)) return false;

    // Time filter
    if (filter !== 'all') {
      const now = new Date();
      const hours = filter === '1h' ? 1 : filter === '24h' ? 24 : 168;
      const cutoff = new Date(now.getTime() - hours * 60 * 60 * 1000);
      if (event.timestamp < cutoff) return false;
    }

    return true;
  });

  // Group by date
  const groupedEvents = groupEventsByDate(filteredEvents);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="animate-pulse text-gray-500">Loading history...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <TimeFilterSelector value={filter} onChange={setFilter} />
        <TypeFilterSelector value={typeFilters} onChange={setTypeFilters} />
      </div>

      {/* Stats */}
      <div className="flex gap-4 text-xs text-gray-500">
        <span>{filteredEvents.length} events</span>
        <span>·</span>
        <span>{Object.keys(groupedEvents).length} days</span>
      </div>

      {/* Timeline */}
      <div className={cn('overflow-y-auto', expanded ? 'max-h-[500px]' : 'max-h-[300px]')}>
        {Object.keys(groupedEvents).length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <span className="text-4xl block mb-4">📜</span>
            <p>No events match your filters.</p>
          </div>
        ) : (
          <Timeline groups={groupedEvents} expanded={expanded} />
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Filters
// =============================================================================

function TimeFilterSelector({
  value,
  onChange,
}: {
  value: TimeFilter;
  onChange: (v: TimeFilter) => void;
}) {
  const options: TimeFilter[] = ['all', '1h', '24h', '7d'];

  return (
    <div className="flex gap-1 bg-town-surface/30 rounded-lg p-1">
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onChange(opt)}
          className={cn(
            'px-2 py-1 text-xs font-medium rounded transition-colors',
            value === opt ? 'bg-town-highlight text-white' : 'text-gray-400 hover:text-white'
          )}
        >
          {opt === 'all' ? 'All' : opt}
        </button>
      ))}
    </div>
  );
}

function TypeFilterSelector({
  value,
  onChange,
}: {
  value: Set<EventType>;
  onChange: (v: Set<EventType>) => void;
}) {
  const types: { id: EventType; icon: string; label: string }[] = [
    { id: 'action', icon: '⚡', label: 'Actions' },
    { id: 'transition', icon: '🔄', label: 'Transitions' },
    { id: 'interaction', icon: '💬', label: 'Interactions' },
    { id: 'evolution', icon: '✨', label: 'Evolution' },
    { id: 'coalition', icon: '🤝', label: 'Coalition' },
  ];

  const toggle = (type: EventType) => {
    const next = new Set(value);
    if (next.has(type)) {
      next.delete(type);
    } else {
      next.add(type);
    }
    onChange(next);
  };

  return (
    <div className="flex gap-1">
      {types.map(({ id, icon, label }) => (
        <button
          key={id}
          onClick={() => toggle(id)}
          className={cn(
            'px-2 py-1 text-xs rounded transition-colors',
            value.has(id)
              ? 'bg-town-accent/50 text-white'
              : 'text-gray-500 hover:text-gray-300'
          )}
          title={label}
        >
          {icon}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Timeline
// =============================================================================

interface TimelineProps {
  groups: Record<string, HistoryEvent[]>;
  expanded?: boolean;
}

function Timeline({ groups, expanded }: TimelineProps) {
  const sortedDates = Object.keys(groups).sort((a, b) => b.localeCompare(a));

  return (
    <div className="space-y-6">
      {sortedDates.map((date) => (
        <div key={date}>
          {/* Date header */}
          <div className="sticky top-0 bg-town-bg/90 backdrop-blur py-2 z-10">
            <span className="text-xs font-medium text-gray-400 bg-town-surface/50 px-2 py-1 rounded">
              {formatDateHeader(date)}
            </span>
          </div>

          {/* Events */}
          <div className="ml-4 border-l-2 border-town-accent/20 pl-4 space-y-4 mt-2">
            {groups[date].map((event, i) => (
              <EventCard key={event.id} event={event} isLast={i === groups[date].length - 1} expanded={expanded} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

interface EventCardProps {
  event: HistoryEvent;
  isLast: boolean;
  expanded?: boolean;
}

function EventCard({ event, expanded: _expanded }: EventCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const config = getEventConfig(event.type);

  return (
    <div className="relative">
      {/* Timeline dot */}
      <div
        className={cn(
          'absolute -left-[21px] w-3 h-3 rounded-full border-2 border-town-bg',
          config.dotColor
        )}
      />

      {/* Event content */}
      <div
        className={cn(
          'bg-town-surface/20 rounded-lg p-3 hover:bg-town-surface/30 transition-colors cursor-pointer',
          showDetails && 'ring-1 ring-town-accent/30'
        )}
        onClick={() => setShowDetails(!showDetails)}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <span>{config.icon}</span>
            <span className="text-sm">{event.description}</span>
          </div>
          <span className="text-xs text-gray-500">{formatTime(event.timestamp)}</span>
        </div>

        {/* Details (expanded) */}
        {showDetails && event.details && (
          <div className="mt-3 pt-3 border-t border-town-accent/20">
            <pre className="text-xs text-gray-400 overflow-x-auto">
              {JSON.stringify(event.details, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getEventConfig(type: EventType): { icon: string; dotColor: string } {
  switch (type) {
    case 'action':
      return { icon: '⚡', dotColor: 'bg-yellow-500' };
    case 'transition':
      return { icon: '🔄', dotColor: 'bg-blue-500' };
    case 'interaction':
      return { icon: '💬', dotColor: 'bg-green-500' };
    case 'evolution':
      return { icon: '✨', dotColor: 'bg-purple-500' };
    case 'coalition':
      return { icon: '🤝', dotColor: 'bg-pink-500' };
    default:
      return { icon: '•', dotColor: 'bg-gray-500' };
  }
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatDateHeader(dateStr: string): string {
  const date = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (dateStr === today.toISOString().split('T')[0]) return 'Today';
  if (dateStr === yesterday.toISOString().split('T')[0]) return 'Yesterday';
  return date.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
}

function groupEventsByDate(events: HistoryEvent[]): Record<string, HistoryEvent[]> {
  const groups: Record<string, HistoryEvent[]> = {};

  for (const event of events) {
    const dateKey = event.timestamp.toISOString().split('T')[0];
    if (!groups[dateKey]) {
      groups[dateKey] = [];
    }
    groups[dateKey].push(event);
  }

  return groups;
}

function generateMockHistory(citizenId: string, count: number): HistoryEvent[] {
  const types: EventType[] = ['action', 'transition', 'interaction', 'evolution', 'coalition'];
  const actions = [
    'Completed a task',
    'Started working on project',
    'Took a break',
    'Reflected on progress',
    'Made a decision',
  ];
  const transitions = [
    'Transitioned to WORKING phase',
    'Entered SOCIALIZING phase',
    'Began REFLECTING period',
    'Started RESTING',
    'Returned to IDLE',
  ];
  const interactions = [
    'Chatted with another citizen',
    'Collaborated on a task',
    'Shared knowledge',
    'Received assistance',
    'Gave feedback',
  ];
  const evolutions = [
    'Eigenvector shift detected',
    'Capability increased',
    'New skill unlocked',
    'Pattern adaptation',
    'Memory consolidated',
  ];
  const coalitions = [
    'Joined coalition',
    'Left coalition',
    'Coalition strength changed',
    'New connection formed',
    'Bridge citizen status',
  ];

  const events: HistoryEvent[] = [];
  const now = new Date();

  for (let i = 0; i < count; i++) {
    const type = types[Math.floor(Math.random() * types.length)];
    const timestamp = new Date(now.getTime() - i * 30 * 60 * 1000 - Math.random() * 60 * 60 * 1000);

    let descriptions: string[];
    switch (type) {
      case 'action':
        descriptions = actions;
        break;
      case 'transition':
        descriptions = transitions;
        break;
      case 'interaction':
        descriptions = interactions;
        break;
      case 'evolution':
        descriptions = evolutions;
        break;
      case 'coalition':
        descriptions = coalitions;
        break;
    }

    events.push({
      id: `${citizenId}-${i}`,
      timestamp,
      type,
      description: descriptions[Math.floor(Math.random() * descriptions.length)],
      details: Math.random() > 0.5 ? { entropy_delta: Math.random() * 0.1, tick: 100 - i } : undefined,
    });
  }

  return events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
}

export default HistoryTab;
