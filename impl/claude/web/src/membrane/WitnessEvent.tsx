/**
 * WitnessEvent — Single event in the witness stream
 *
 * Renders marks, thoughts, crystals with appropriate styling.
 * Uses Joy primitives for entry animation.
 */

import { GrowingContainer } from '../components/genesis/GrowingContainer';

import type { WitnessEvent as WitnessEventData } from './useWitnessStream';

// Simple relative time formatter (native, no date-fns dependency)
function formatTimeAgo(date: Date): string {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

import './WitnessEvent.css';

// =============================================================================
// Component
// =============================================================================

interface WitnessEventProps {
  event: WitnessEventData;
}

export function WitnessEvent({ event }: WitnessEventProps) {
  const timeAgo = formatTimeAgo(event.timestamp);

  return (
    <GrowingContainer>
      <div className={`witness-event witness-event--${event.type}`}>
        <div className="witness-event__header">
          <span className="witness-event__type">{getTypeLabel(event.type)}</span>
          <span className="witness-event__time">{timeAgo}</span>
        </div>

        <div className="witness-event__content">{renderContent(event)}</div>

        {event.principles && event.principles.length > 0 && (
          <div className="witness-event__principles">
            {event.principles.map((p) => (
              <span key={p} className="witness-event__principle">
                {p}
              </span>
            ))}
          </div>
        )}
      </div>
    </GrowingContainer>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getTypeLabel(type: WitnessEventData['type']): string {
  switch (type) {
    case 'mark':
      return 'Mark';
    case 'thought':
      return 'Thought';
    case 'crystal':
      return 'Crystal';
    case 'connected':
      return 'Connected';
    case 'heartbeat':
      return 'Heartbeat';
    default:
      return 'Event';
  }
}

function renderContent(event: WitnessEventData): React.ReactNode {
  switch (event.type) {
    case 'mark':
      return (
        <>
          {event.action && <div className="witness-event__action">{event.action}</div>}
          {event.reasoning && <div className="witness-event__reasoning">{event.reasoning}</div>}
          {event.author && <div className="witness-event__author">— {event.author}</div>}
        </>
      );

    case 'thought':
      return (
        <>
          {event.content && <div className="witness-event__thought">{event.content}</div>}
          {event.source && <div className="witness-event__source">from {event.source}</div>}
        </>
      );

    case 'crystal':
      return (
        <>
          {event.insight && <div className="witness-event__insight">{event.insight}</div>}
          {event.level && <div className="witness-event__level">Level: {event.level}</div>}
        </>
      );

    case 'connected':
      return <div className="witness-event__connected">Stream connected</div>;

    default:
      return event.content || 'Unknown event';
  }
}
