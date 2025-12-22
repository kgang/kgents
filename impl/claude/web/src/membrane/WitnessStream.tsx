/**
 * WitnessStream — Real-time stream of decisions, marks, crystallizations
 *
 * Shows you're being heard. Every action leaves a trace.
 *
 * "The proof IS the decision."
 */

import { Breathe } from '../components/joy/Breathe';

import { useWitnessStream } from './useWitnessStream';
import { WitnessEvent } from './WitnessEvent';

import './WitnessStream.css';

// =============================================================================
// Component
// =============================================================================

export function WitnessStream() {
  const { events, connected, reconnect, clear } = useWitnessStream();

  return (
    <div className="witness-stream">
      <header className="witness-stream__header">
        <div className="witness-stream__title-row">
          <Breathe intensity={connected ? 0.3 : 0} speed="slow">
            <h3 className="witness-stream__title">Witness</h3>
          </Breathe>
          <span
            className={`witness-stream__status ${connected ? 'witness-stream__status--connected' : 'witness-stream__status--disconnected'}`}
            title={connected ? 'Connected' : 'Disconnected'}
          />
        </div>

        <div className="witness-stream__actions">
          {!connected && (
            <button className="witness-stream__action" onClick={reconnect} title="Reconnect">
              Reconnect
            </button>
          )}
          {events.length > 0 && (
            <button
              className="witness-stream__action witness-stream__action--subtle"
              onClick={clear}
              title="Clear"
            >
              Clear
            </button>
          )}
        </div>
      </header>

      <div className="witness-stream__events">
        {events.length === 0 ? (
          <div className="witness-stream__empty">
            <p>No events yet</p>
            <p className="witness-stream__hint">Decisions will appear here as they happen</p>
          </div>
        ) : (
          events.map((event) => <WitnessEvent key={event.id} event={event} />)
        )}
      </div>
    </div>
  );
}
