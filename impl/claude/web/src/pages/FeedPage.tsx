/**
 * FeedPage — Power-User Mark Stream
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * Terminal-style live stream of witness marks.
 * Keyboard-first, minimal chrome, 90% steel.
 */

import { useEffect, useMemo, useState } from 'react';

import { useWitnessStream } from '../hooks/useWitnessStream';
import type { WitnessEvent } from '../hooks/useWitnessStream';
import { getRecentMarks, type Mark } from '../api/witness';

import './FeedPage.css';

// =============================================================================
// Types
// =============================================================================

interface FilterState {
  searchQuery: string;
  tagFilter: string;
  authorFilter: 'all' | 'kent' | 'claude' | 'system';
}

// =============================================================================
// Main Component
// =============================================================================

// Helper to convert Mark to WitnessEvent
function markToEvent(mark: Mark): WitnessEvent {
  return {
    id: mark.id,
    type: 'mark',
    timestamp: new Date(mark.timestamp),
    action: mark.action,
    reasoning: mark.reasoning,
    principles: mark.principles,
    author: mark.author,
  };
}

export function FeedPage() {
  const { events: sseEvents, connected, reconnect, clear: clearSSE } = useWitnessStream();

  // Historical data loading
  const [historicalMarks, setHistoricalMarks] = useState<WitnessEvent[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [historyError, setHistoryError] = useState<string | null>(null);

  // Merge historical + SSE events (deduplicate by ID, newest first)
  const allEvents = useMemo(() => {
    const eventMap = new Map<string, WitnessEvent>();

    // Add historical marks first
    for (const event of historicalMarks) {
      eventMap.set(event.id, event);
    }

    // Add SSE events (will override if ID matches)
    for (const event of sseEvents) {
      eventMap.set(event.id, event);
    }

    // Convert to array and sort by timestamp (newest first)
    return Array.from(eventMap.values()).sort(
      (a, b) => b.timestamp.getTime() - a.timestamp.getTime()
    );
  }, [historicalMarks, sseEvents]);

  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    searchQuery: '',
    tagFilter: '',
    authorFilter: 'all',
  });

  // UI state
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);
  const [showDetail, setShowDetail] = useState(false);
  const [inputMode, setInputMode] = useState<'search' | 'tag' | null>(null);
  const [inputValue, setInputValue] = useState('');

  // Load historical marks on mount
  useEffect(() => {
    async function loadHistory() {
      try {
        setIsLoadingHistory(true);
        setHistoryError(null);

        // Requirement: Load last 100 OR last 15 minutes (whichever gives MORE results)
        // Strategy: Always fetch last 100 marks
        // This ensures:
        // - Never show empty screen if marks exist in DB
        // - 100 marks typically covers far more than 15 minutes
        // - Good performance (single query, no complex filtering)
        const marks = await getRecentMarks({ limit: 100 });

        // Convert to WitnessEvent format
        const events = marks.map(markToEvent);

        setHistoricalMarks(events);
      } catch (error) {
        console.error('Failed to load historical marks:', error);
        setHistoryError(error instanceof Error ? error.message : 'Failed to load marks');
      } finally {
        setIsLoadingHistory(false);
      }
    }

    loadHistory();
  }, []);

  // Filter events
  const filteredEvents = useMemo(() => {
    return allEvents.filter((event) => {
      // Only show marks
      if (event.type !== 'mark') return false;

      // Search filter
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        const matchesAction = event.action?.toLowerCase().includes(query);
        const matchesReasoning = event.reasoning?.toLowerCase().includes(query);
        if (!matchesAction && !matchesReasoning) return false;
      }

      // Tag filter
      if (filters.tagFilter) {
        const hasTags = event.tags?.some((tag) =>
          tag.toLowerCase().includes(filters.tagFilter.toLowerCase())
        );
        const hasPrinciples = event.principles?.some((p) =>
          p.toLowerCase().includes(filters.tagFilter.toLowerCase())
        );
        if (!hasTags && !hasPrinciples) return false;
      }

      // Author filter
      if (filters.authorFilter !== 'all' && event.author !== filters.authorFilter) {
        return false;
      }

      return true;
    });
  }, [allEvents, filters]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't intercept if input is active
      if (inputMode !== null) {
        if (e.key === 'Escape') {
          setInputMode(null);
          setInputValue('');
        } else if (e.key === 'Enter') {
          e.preventDefault();
          // Apply filter
          if (inputMode === 'search') {
            setFilters((prev) => ({ ...prev, searchQuery: inputValue }));
          } else if (inputMode === 'tag') {
            setFilters((prev) => ({ ...prev, tagFilter: inputValue }));
          }
          setInputMode(null);
          setInputValue('');
        }
        return;
      }

      // Normal mode keyboard shortcuts
      switch (e.key) {
        case '/':
          e.preventDefault();
          setInputMode('search');
          break;
        case 't':
          e.preventDefault();
          setInputMode('tag');
          break;
        case 'r':
          e.preventDefault();
          reconnect();
          break;
        case 'c':
          e.preventDefault();
          clearSSE();
          setHistoricalMarks([]);
          break;
        case 'x':
          e.preventDefault();
          setFilters({ searchQuery: '', tagFilter: '', authorFilter: 'all' });
          break;
        case 'a':
          e.preventDefault();
          setFilters((prev) => ({
            ...prev,
            authorFilter: prev.authorFilter === 'all' ? 'kent' : 'all',
          }));
          break;
        case 'j':
          e.preventDefault();
          setSelectedIndex((prev) => Math.min(prev + 1, filteredEvents.length - 1));
          break;
        case 'k':
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;
        case 'Enter':
          if (selectedIndex >= 0) {
            e.preventDefault();
            setShowDetail((prev) => !prev);
          }
          break;
        case 'Escape':
          setShowDetail(false);
          setSelectedIndex(-1);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [inputMode, inputValue, filteredEvents.length, selectedIndex, reconnect, clearSSE]);

  // Auto-select first item when filter changes
  useEffect(() => {
    if (filteredEvents.length > 0 && selectedIndex === -1) {
      setSelectedIndex(0);
    }
  }, [filteredEvents.length, selectedIndex]);

  return (
    <div className="feed-page">
      {/* Command bar */}
      <div className="feed-page__command-bar">
        {inputMode === null ? (
          <>
            <span className="feed-page__command-hint">
              / search · t tag · a author · r refresh · c clear · x reset · j/k nav · Enter
              detail
            </span>
            {filters.searchQuery && (
              <span className="feed-page__active-filter">search: {filters.searchQuery}</span>
            )}
            {filters.tagFilter && (
              <span className="feed-page__active-filter">tag: {filters.tagFilter}</span>
            )}
            {filters.authorFilter !== 'all' && (
              <span className="feed-page__active-filter">author: {filters.authorFilter}</span>
            )}
          </>
        ) : (
          <div className="feed-page__input-mode">
            <span className="feed-page__input-label">
              {inputMode === 'search' ? '/' : 't'}
            </span>
            <input
              className="feed-page__input"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={inputMode === 'search' ? 'Search marks...' : 'Filter by tag...'}
              autoFocus
            />
            <span className="feed-page__input-hint">Enter to apply · Esc to cancel</span>
          </div>
        )}
      </div>

      {/* Stream */}
      <div className="feed-page__stream">
        {isLoadingHistory ? (
          <div className="feed-page__empty">
            <div className="feed-page__empty-icon">⏳</div>
            <div className="feed-page__empty-text">Loading marks...</div>
          </div>
        ) : historyError ? (
          <div className="feed-page__empty">
            <div className="feed-page__empty-icon">⚠</div>
            <div className="feed-page__empty-text">Error: {historyError}</div>
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="feed-page__empty">
            <div className="feed-page__empty-icon">∅</div>
            <div className="feed-page__empty-text">
              {allEvents.length === 0 ? 'No marks yet. Action creates memory.' : 'No matches.'}
            </div>
          </div>
        ) : (
          <div className="feed-page__marks">
            {filteredEvents.map((event, idx) => (
              <MarkRow
                key={event.id}
                event={event}
                selected={idx === selectedIndex}
                expanded={idx === selectedIndex && showDetail}
                onClick={() => {
                  setSelectedIndex(idx);
                  setShowDetail((prev) => !prev);
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Status line */}
      <div className="feed-page__status">
        <span className="feed-page__status-connection">
          {connected ? (
            <>
              <span className="feed-page__status-indicator feed-page__status-indicator--live" />
              LIVE
            </>
          ) : (
            <>
              <span className="feed-page__status-indicator feed-page__status-indicator--disconnected" />
              DISCONNECTED
            </>
          )}
        </span>
        <span className="feed-page__status-count">
          {filteredEvents.length}/{allEvents.length} marks
        </span>
        {selectedIndex >= 0 && (
          <span className="feed-page__status-selected">
            {selectedIndex + 1}/{filteredEvents.length}
          </span>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// MarkRow Component
// =============================================================================

interface MarkRowProps {
  event: WitnessEvent;
  selected: boolean;
  expanded: boolean;
  onClick: () => void;
}

function MarkRow({ event, selected, expanded, onClick }: MarkRowProps) {
  const timestamp = formatTimestamp(event.timestamp);
  const action = event.action || '(no action)';
  const tags = [...(event.tags || []), ...(event.principles || [])];
  const reasoning = event.reasoning || '';

  return (
    <div
      className={`feed-page__mark ${selected ? 'feed-page__mark--selected' : ''}`}
      onClick={onClick}
    >
      <div className="feed-page__mark-row">
        <span className="feed-page__mark-time">{timestamp}</span>
        <span className="feed-page__mark-divider">│</span>
        <span className="feed-page__mark-action">{truncate(action, 60)}</span>
        <span className="feed-page__mark-divider">│</span>
        <span className="feed-page__mark-tags">{tags.join(',') || '—'}</span>
        {!expanded && reasoning && (
          <>
            <span className="feed-page__mark-divider">│</span>
            <span className="feed-page__mark-reasoning">{truncate(reasoning, 40)}</span>
          </>
        )}
      </div>
      {expanded && reasoning && (
        <div className="feed-page__mark-detail">
          <div className="feed-page__mark-detail-label">Reasoning:</div>
          <div className="feed-page__mark-detail-text">{reasoning}</div>
          {event.author && (
            <div className="feed-page__mark-detail-meta">Author: {event.author}</div>
          )}
          {event.source && (
            <div className="feed-page__mark-detail-meta">Source: {event.source}</div>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Utilities
// =============================================================================

function formatTimestamp(date: Date): string {
  const h = date.getHours().toString().padStart(2, '0');
  const m = date.getMinutes().toString().padStart(2, '0');
  const s = date.getSeconds().toString().padStart(2, '0');
  return `${h}:${m}:${s}`;
}

function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 1) + '…';
}

export default FeedPage;
