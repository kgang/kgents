/**
 * PolicyTraceView — Timeline visualization of DP solution traces
 *
 * Shows the policy trace as a vertical timeline:
 * - Each entry = (state_before → action → state_after, value)
 * - Color-coded by value (high = green, low = red)
 * - Expandable rationale on click
 *
 * "The trace IS the proof. The mark IS the witness."
 */

import { useState } from 'react';
import type { PolicyTrace, TraceEntry } from './types';
import './PolicyTraceView.css';

// =============================================================================
// Types
// =============================================================================

export interface PolicyTraceViewProps {
  /** Policy trace to visualize */
  trace: PolicyTrace | null;
  /** Compact mode */
  compact?: boolean;
  /** Max entries to show (default: all) */
  maxEntries?: number;
  /** Show cumulative value */
  showCumulative?: boolean;
}

// =============================================================================
// Helpers
// =============================================================================

function formatValue(value: number): string {
  return value.toFixed(3);
}

function getValueColor(value: number): string {
  // Normalize assuming values are roughly in [0, 1] range
  if (value >= 0.8) return 'var(--health-healthy)';
  if (value >= 0.6) return 'var(--health-degraded)';
  if (value >= 0.4) return 'var(--health-warning)';
  return 'var(--health-critical)';
}

function formatTimestamp(ts: string): string {
  try {
    const date = new Date(ts);
    return date.toLocaleTimeString(undefined, {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return ts;
  }
}

function stringifyState(state: unknown): string {
  if (typeof state === 'string') return state;
  if (typeof state === 'number') return String(state);
  if (state === null || state === undefined) return '—';
  return JSON.stringify(state);
}

// =============================================================================
// TraceEntryItem Component
// =============================================================================

interface TraceEntryItemProps {
  entry: TraceEntry;
  index: number;
  compact: boolean;
  cumulativeValue?: number;
}

function TraceEntryItem({ entry, index, compact, cumulativeValue }: TraceEntryItemProps) {
  const [expanded, setExpanded] = useState(false);

  const valueColor = getValueColor(entry.value);

  return (
    <div
      className="policy-trace-entry"
      data-compact={compact}
      onClick={() => setExpanded(!expanded)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          setExpanded(!expanded);
        }
      }}
    >
      {/* Index */}
      <div className="policy-trace-entry__index">{index}</div>

      {/* Timeline connector */}
      <div className="policy-trace-entry__timeline">
        <div className="policy-trace-entry__dot" style={{ backgroundColor: valueColor }} />
        <div className="policy-trace-entry__line" />
      </div>

      {/* Content */}
      <div className="policy-trace-entry__content">
        {/* Header: action + value */}
        <div className="policy-trace-entry__header">
          <span className="policy-trace-entry__action">{entry.action}</span>
          <span className="policy-trace-entry__value" style={{ color: valueColor }}>
            v={formatValue(entry.value)}
          </span>
        </div>

        {/* State transition */}
        {!compact && (
          <div className="policy-trace-entry__states">
            <span className="policy-trace-entry__state">
              {stringifyState(entry.state_before)}
            </span>
            <span className="policy-trace-entry__arrow">→</span>
            <span className="policy-trace-entry__state">
              {stringifyState(entry.state_after)}
            </span>
          </div>
        )}

        {/* Metadata */}
        <div className="policy-trace-entry__meta">
          <span className="policy-trace-entry__timestamp">
            {formatTimestamp(entry.timestamp)}
          </span>
          {cumulativeValue !== undefined && (
            <span className="policy-trace-entry__cumulative">
              Σ={formatValue(cumulativeValue)}
            </span>
          )}
        </div>

        {/* Rationale (expandable) */}
        {expanded && entry.rationale && (
          <div className="policy-trace-entry__rationale">
            <div className="policy-trace-entry__rationale-label">Rationale:</div>
            <div className="policy-trace-entry__rationale-text">{entry.rationale}</div>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function PolicyTraceView({
  trace,
  compact = false,
  maxEntries,
  showCumulative = true,
}: PolicyTraceViewProps) {
  if (!trace || trace.log.length === 0) {
    return (
      <div className="policy-trace-view policy-trace-view--empty">
        <div className="policy-trace-view__placeholder">
          <span>No trace entries</span>
        </div>
      </div>
    );
  }

  const entries = maxEntries ? trace.log.slice(0, maxEntries) : trace.log;
  const hasMore = maxEntries && trace.log.length > maxEntries;

  // Calculate cumulative values
  let cumulative = 0;
  const entriesWithCumulative = entries.map((entry) => {
    cumulative += entry.value;
    return { entry, cumulative };
  });

  return (
    <div className="policy-trace-view" data-compact={compact}>
      {/* Header */}
      <div className="policy-trace-view__header">
        <h3 className="policy-trace-view__title">Policy Trace</h3>
        <div className="policy-trace-view__stats">
          <span>{trace.log.length} steps</span>
          {trace.total_value !== undefined && (
            <span className="policy-trace-view__total">
              Total: {formatValue(trace.total_value)}
            </span>
          )}
        </div>
      </div>

      {/* Trace timeline */}
      <div className="policy-trace-view__timeline">
        {entriesWithCumulative.map(({ entry, cumulative: cumulativeValue }, i) => (
          <TraceEntryItem
            key={i}
            entry={entry}
            index={i}
            compact={compact}
            cumulativeValue={showCumulative ? cumulativeValue : undefined}
          />
        ))}

        {hasMore && (
          <div className="policy-trace-view__more">
            + {trace.log.length - entries.length} more entries
          </div>
        )}
      </div>
    </div>
  );
}
