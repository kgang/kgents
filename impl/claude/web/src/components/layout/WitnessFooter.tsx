/**
 * WitnessFooter — Compact always-on witness stream in footer
 *
 * Shows last 3 events in a single-line compact view.
 * Click to expand full WitnessStream panel.
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import { useState, useCallback, useMemo } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

import { useWitnessStream, type WitnessEvent } from '../../hooks/useWitnessStream';

import './WitnessFooter.css';

// =============================================================================
// Event Rendering
// =============================================================================

function getEventIcon(type: WitnessEvent['type']): string {
  switch (type) {
    case 'mark':
      return '📜';
    case 'kblock':
      return '✏️';
    case 'crystal':
      return '💎';
    case 'thought':
      return '💭';
    case 'trail':
      return '🔗';
    case 'spec':
      return '📋';
    case 'connected':
      return '🟢';
    default:
      return '•';
  }
}

// eslint-disable-next-line complexity
function getEventSummary(event: WitnessEvent): string {
  switch (event.type) {
    case 'mark':
      return event.action?.slice(0, 50) || 'Mark';
    case 'kblock':
      return `Edit: ${event.path?.split('/').pop() || 'file'}`;
    case 'crystal':
      return event.insight?.slice(0, 40) || 'Crystal';
    case 'thought':
      return event.content?.slice(0, 40) || 'Thought';
    case 'spec':
      return event.specAction === 'scan' ? 'Corpus scanned' : event.specAction || 'Spec';
    case 'connected':
      return 'Connected';
    default:
      return event.type;
  }
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

// =============================================================================
// Compact Event (single line)
// =============================================================================

interface CompactEventProps {
  event: WitnessEvent;
}

function CompactEvent({ event }: CompactEventProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 10 }}
      className="witness-footer__event"
      data-type={event.type}
    >
      <span className="witness-footer__event-icon">{getEventIcon(event.type)}</span>
      <span className="witness-footer__event-text">{getEventSummary(event)}</span>
      <span className="witness-footer__event-time">{formatTime(event.timestamp)}</span>
    </motion.div>
  );
}

// =============================================================================
// Expanded Event (full details)
// =============================================================================

interface ExpandedEventProps {
  event: WitnessEvent;
}

function ExpandedEvent({ event }: ExpandedEventProps) {
  // Show first 2 principles + "+N more" badge
  const visiblePrinciples = event.principles?.slice(0, 2) || [];
  const remainingCount = (event.principles?.length || 0) - visiblePrinciples.length;

  return (
    <div className="witness-footer__expanded-event" data-type={event.type}>
      <div className="witness-footer__expanded-header">
        <span className="witness-footer__event-icon">{getEventIcon(event.type)}</span>
        <span className="witness-footer__expanded-type">{event.type.toUpperCase()}</span>
        <span className="witness-footer__event-time">{formatTime(event.timestamp)}</span>
        {event.author && <span className="witness-footer__expanded-author">by {event.author}</span>}
      </div>
      <div className="witness-footer__expanded-content">
        {event.action && <p className="witness-footer__expanded-action">{event.action}</p>}
        {event.reasoning && <p className="witness-footer__expanded-reasoning">{event.reasoning}</p>}
        {event.principles && event.principles.length > 0 && (
          <div className="witness-footer__expanded-principles">
            {visiblePrinciples.map((p) => (
              <span key={p} className="witness-footer__principle-tag">
                {p}
              </span>
            ))}
            {remainingCount > 0 && (
              <span className="witness-footer__principle-tag witness-footer__principle-badge">
                +{remainingCount}
              </span>
            )}
          </div>
        )}
        {event.insight && <p className="witness-footer__expanded-insight">{event.insight}</p>}
        {event.path && (
          <p className="witness-footer__expanded-path">
            <code>{event.path}</code>
          </p>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function WitnessFooter() {
  const { events, connected, reconnect } = useWitnessStream();
  const [expanded, setExpanded] = useState(false);

  // Get last 3 events (excluding connected)
  const recentEvents = useMemo(
    () => events.filter((e) => e.type !== 'connected').slice(0, 3),
    [events]
  );

  // Get all events for expanded view
  const allEvents = useMemo(() => events.slice(0, 20), [events]);

  const toggleExpanded = useCallback(() => {
    setExpanded((prev) => !prev);
  }, []);

  return (
    <footer className="witness-footer" data-expanded={expanded}>
      {/* Compact bar */}
      <div className="witness-footer__bar" onClick={toggleExpanded}>
        {/* Connection indicator */}
        <div className="witness-footer__status" data-connected={connected}>
          <span className="witness-footer__status-dot" />
          <span className="witness-footer__status-label">
            {connected ? 'WITNESS' : 'RECONNECTING'}
          </span>
        </div>

        {/* Recent events */}
        <div className="witness-footer__events">
          <AnimatePresence mode="popLayout">
            {recentEvents.length > 0 ? (
              recentEvents.map((event) => <CompactEvent key={event.id} event={event} />)
            ) : (
              <span className="witness-footer__empty">No activity yet</span>
            )}
          </AnimatePresence>
        </div>

        {/* Expand toggle */}
        <button className="witness-footer__toggle" aria-label={expanded ? 'Collapse' : 'Expand'}>
          <span className="witness-footer__toggle-icon">{expanded ? '▼' : '▲'}</span>
        </button>
      </div>

      {/* Expanded panel */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="witness-footer__panel"
          >
            <div className="witness-footer__panel-header">
              <h3 className="witness-footer__panel-title">Witness Stream</h3>
              {!connected && (
                <button className="witness-footer__reconnect" onClick={reconnect}>
                  Reconnect
                </button>
              )}
            </div>
            <div className="witness-footer__panel-list">
              {allEvents.length > 0 ? (
                allEvents.map((event) => <ExpandedEvent key={event.id} event={event} />)
              ) : (
                <p className="witness-footer__panel-empty">
                  Awaiting first mark. Actions witnessed here.
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </footer>
  );
}
