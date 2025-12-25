/**
 * WitnessFooter — Compact always-on witness stream in footer
 *
 * Shows last 3 events in a single-line compact view.
 * Click to expand full WitnessStream panel.
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import { useState, useCallback, useMemo, forwardRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';

import { useWitnessStream, type WitnessEvent } from '../../hooks/useWitnessStream';

import './WitnessFooter.css';

// =============================================================================
// Event Rendering
// =============================================================================

function getEventIcon(type: WitnessEvent['type']): string {
  switch (type) {
    case 'mark':
      return '⊢';
    case 'kblock':
      return '⎔';
    case 'crystal':
      return '◇';
    case 'thought':
      return '⟨⟩';
    case 'trail':
      return '∘';
    case 'spec':
      return '◈';
    case 'connected':
      return '●';
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

/**
 * CompactEvent — Single event in the footer bar
 *
 * Uses forwardRef because AnimatePresence with mode="popLayout"
 * needs to attach refs for layout measurements.
 */
const CompactEvent = forwardRef<HTMLDivElement, CompactEventProps>(function CompactEvent(
  { event },
  ref
) {
  return (
    <motion.div
      ref={ref}
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
});

// =============================================================================
// Log Entry (tail -f style)
// =============================================================================

interface LogEntryProps {
  event: WitnessEvent;
}

function formatTimeWithSeconds(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

function LogEntry({ event }: LogEntryProps) {
  const time = formatTimeWithSeconds(event.timestamp);
  const type = event.type.toUpperCase().padEnd(7);
  const author = event.author ? `[${event.author}]` : '';

  // Build the main content based on event type
  let content = '';
  let detail = '';

  switch (event.type) {
    case 'mark':
      content = event.action || 'mark';
      detail = event.reasoning || '';
      break;
    case 'kblock':
      content = event.path?.split('/').pop() || 'edit';
      detail = event.semanticDeltas?.length ? `${event.semanticDeltas.length} changes` : '';
      break;
    case 'crystal':
      content = event.insight || 'crystal';
      detail = event.level ? `L${event.level}` : '';
      break;
    case 'thought':
      content = event.content || 'thought';
      detail = event.source || '';
      break;
    case 'trail':
      content = event.path || 'trail';
      break;
    case 'spec':
      content = event.specAction || 'spec';
      detail = event.specPaths?.join(', ') || '';
      break;
    case 'connected':
      content = 'stream connected';
      break;
    default:
      content = event.type;
  }

  // Format principles as tags
  const tags = event.principles?.length
    ? event.principles.map(p => `#${p}`).join(' ')
    : '';

  return (
    <div className="witness-log__entry" data-type={event.type}>
      <span className="witness-log__time">{time}</span>
      <span className="witness-log__type">{type}</span>
      <span className="witness-log__author">{author}</span>
      <span className="witness-log__content">{content}</span>
      {detail && <span className="witness-log__detail">• {detail}</span>}
      {tags && <span className="witness-log__tags">{tags}</span>}
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
            <div className="witness-log">
              {allEvents.length > 0 ? (
                allEvents.map((event) => <LogEntry key={event.id} event={event} />)
              ) : (
                <div className="witness-log__empty">
                  Awaiting first mark...
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </footer>
  );
}
