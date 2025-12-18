/**
 * StreamingProgress: Real-time progress display during artisan work.
 *
 * Shows:
 * - Current status (contemplating, working, complete)
 * - Progress indicator
 * - Live fragment preview
 * - Event log
 */

// React import not needed for JSX in modern React
import type { AtelierEvent } from '@/api/forge';

interface StreamingProgressProps {
  /** Current status */
  status: 'idle' | 'contemplating' | 'working' | 'complete' | 'error';
  /** Progress (0-1) */
  progress: number;
  /** Current fragment being generated */
  currentFragment?: string;
  /** Error message if any */
  error?: string | null;
  /** All events received */
  events?: AtelierEvent[];
  /** Show event log */
  showEvents?: boolean;
}

const STATUS_CONFIG = {
  idle: {
    label: 'Ready',
    icon: '○',
    color: 'text-stone-400',
  },
  contemplating: {
    label: 'Contemplating...',
    icon: '◐',
    color: 'text-amber-500',
  },
  working: {
    label: 'Creating...',
    icon: '◑',
    color: 'text-amber-600',
  },
  complete: {
    label: 'Complete',
    icon: '●',
    color: 'text-green-500',
  },
  error: {
    label: 'Error',
    icon: '✗',
    color: 'text-red-500',
  },
};

export function StreamingProgress({
  status,
  progress,
  currentFragment,
  error,
  events = [],
  showEvents = false,
}: StreamingProgressProps) {
  const config = STATUS_CONFIG[status];

  return (
    <div className="space-y-4">
      {/* Status Header */}
      <div className="flex items-center gap-3">
        <span
          className={`text-2xl ${config.color} ${
            status === 'contemplating' || status === 'working' ? 'animate-spin' : ''
          }`}
        >
          {config.icon}
        </span>
        <span className={`font-medium ${config.color}`}>{config.label}</span>
      </div>

      {/* Progress Bar */}
      {(status === 'working' || status === 'complete') && (
        <div className="h-1 bg-stone-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-amber-400 transition-all duration-300"
            style={{ width: `${Math.min(progress * 100, 100)}%` }}
          />
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* Fragment Preview */}
      {currentFragment && status === 'working' && (
        <div className="p-4 rounded-lg bg-stone-50 border border-stone-200">
          <p className="text-stone-600 text-sm whitespace-pre-wrap font-mono">
            {currentFragment}
            <span className="animate-pulse text-amber-400">|</span>
          </p>
        </div>
      )}

      {/* Event Log */}
      {showEvents && events.length > 0 && (
        <div className="mt-4">
          <h4 className="text-xs font-medium text-stone-400 uppercase tracking-wide mb-2">
            Events
          </h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {events.map((event, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-stone-500 font-mono">
                <span className="text-stone-300">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
                <span className="text-stone-400">{event.event_type}</span>
                {event.message && <span className="text-stone-500 truncate">{event.message}</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default StreamingProgress;
