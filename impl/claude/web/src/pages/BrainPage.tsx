/**
 * BrainPage — Spatial Cathedral of Memory
 *
 * "The file is a lie. There is only the graph."
 *
 * Unified data explorer for ALL kgents data constructs:
 * - Marks (witnessed behavior)
 * - Crystals (crystallized knowledge)
 * - Trails (exploration journeys)
 * - Evidence (formal verification)
 * - Teaching (ancestral wisdom)
 * - Lemmas (ASHC experiments)
 *
 * Architecture: Unified stream + slide-in drawer
 */

import { useCallback, useMemo, useState } from 'react';

import {
  useBrainStream,
  useBrainPoll,
  UnifiedEventCard,
  StreamFiltersBar,
  ConnectionStatus,
  DetailPreview,
} from '../brain';
import type { UnifiedEvent, StreamFilters } from '../brain';

import './BrainPage.css';

// =============================================================================
// Types
// =============================================================================

interface BrainPageState {
  selectedEvent: UnifiedEvent | null;
  drawerOpen: boolean;
  searchQuery: string;
}

// =============================================================================
// Main Component
// =============================================================================

export function BrainPage() {
  // Local UI state
  const [state, setState] = useState<BrainPageState>({
    selectedEvent: null,
    drawerOpen: false,
    searchQuery: '',
  });

  // Stream filters state
  const [filters, setFilters] = useState<StreamFilters>({ types: [] });

  // Stream connection (try SSE first, fallback to polling)
  const stream = useBrainStream({
    filters,
    maxEvents: 100,
    onEvent: (event) => {
      // Could trigger notifications here for important events
      console.debug('[Brain] New event:', event.type, event.title);
    },
  });

  // Fallback to polling if SSE not available
  const poll = useBrainPoll({
    filters,
    pollInterval: 5000,
    maxEvents: 50,
  });

  // Merge events: poll provides historical data, stream provides real-time updates
  // SSE only receives NEW events, so we need poll for initial load
  const mergedEvents = useMemo(() => {
    // Combine stream (real-time) and poll (historical) events
    const allEvents = [...stream.events, ...poll.events];

    // Deduplicate by ID (stream events take priority as they're newer)
    const seen = new Set<string>();
    const unique = allEvents.filter((e) => {
      if (seen.has(e.id)) return false;
      seen.add(e.id);
      return true;
    });

    // Sort by timestamp descending (newest first)
    return unique.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [stream.events, poll.events]);

  const events = mergedEvents;
  const loading = !poll.connected; // Poll is the source of truth for initial load

  // Handle event selection
  const handleEventClick = useCallback((event: UnifiedEvent) => {
    setState((prev) => ({
      ...prev,
      selectedEvent: event,
      drawerOpen: true,
    }));
  }, []);

  // Handle drawer close
  const handleDrawerClose = useCallback(() => {
    setState((prev) => ({
      ...prev,
      drawerOpen: false,
    }));
  }, []);

  // Handle filter changes
  const handleFiltersChange = useCallback(
    (newFilters: StreamFilters) => {
      setFilters(newFilters);
      stream.setFilters(newFilters);
      poll.setFilters(newFilters); // Also update poll hook for filtering to work
    },
    [stream, poll]
  );

  // Handle search
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setState((prev) => ({ ...prev, searchQuery: e.target.value }));
  }, []);

  const handleSearchSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      // Update filters with search query
      const newFilters: StreamFilters = {
        ...filters,
        searchQuery: state.searchQuery || undefined,
      };
      setFilters(newFilters);
      stream.setFilters(newFilters);
    },
    [filters, stream, state.searchQuery]
  );

  // Handle serendipity (random surface)
  const handleSerendipity = useCallback(() => {
    // TODO: Implement random entity surfacing via self.explorer.surface
    console.debug('[Brain] Serendipity requested');
  }, []);

  // Filter events by search query (client-side for now)
  const filteredEvents = state.searchQuery
    ? events.filter(
        (e) =>
          e.title.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
          e.summary.toLowerCase().includes(state.searchQuery.toLowerCase())
      )
    : events;

  return (
    <div className="brain-page">
      {/* Header */}
      <header className="brain-page__header">
        <div className="brain-page__header-main">
          <h1 className="brain-page__title">
            Brain <span className="brain-page__subtitle">— spatial cathedral of memory</span>
          </h1>
        </div>

        <ConnectionStatus
          connected={stream.connected}
          reconnecting={stream.reconnecting}
          reconnectAttempts={stream.reconnectAttempts}
          error={stream.error?.message ?? null}
          onReconnect={stream.reconnect}
          variant="inline"
        />
      </header>

      {/* Search + Filters */}
      <section className="brain-page__controls">
        <form className="brain-page__search-form" onSubmit={handleSearchSubmit}>
          <input
            type="text"
            className="brain-page__search-input"
            placeholder="Search across all entities..."
            value={state.searchQuery}
            onChange={handleSearchChange}
          />
          <button type="submit" className="brain-page__search-btn" title="Search">
            🔍
          </button>
          <button
            type="button"
            className="brain-page__serendipity-btn"
            onClick={handleSerendipity}
            title="Surface serendipitous memory (The Accursed Share)"
          >
            🎲
          </button>
        </form>

        <StreamFiltersBar filters={filters} onChange={handleFiltersChange} disabled={loading} />
      </section>

      {/* Main Content: Stream + Drawer */}
      <div
        className={`brain-page__content ${state.drawerOpen ? 'brain-page__content--drawer-open' : ''}`}
      >
        {/* Event Stream */}
        <section className="brain-page__stream">
          {loading ? (
            <div className="brain-page__loading">
              <span className="brain-page__loading-icon">🧠</span>
              <span>Loading memories...</span>
            </div>
          ) : filteredEvents.length > 0 ? (
            <div className="brain-page__event-list">
              {filteredEvents.map((event) => (
                <UnifiedEventCard
                  key={event.id}
                  event={event}
                  onClick={() => handleEventClick(event)}
                  selected={state.selectedEvent?.id === event.id}
                />
              ))}
            </div>
          ) : (
            <div className="brain-page__empty">
              <span className="brain-page__empty-icon">🌌</span>
              <p className="brain-page__empty-title">
                {state.searchQuery
                  ? 'No entities match your search'
                  : 'Memory crystallizes through action'}
              </p>
              <p className="brain-page__empty-hint">
                {state.searchQuery ? 'Try different terms or clear filters' : 'Your first mark awaits'}
              </p>
            </div>
          )}
        </section>

        {/* Detail Drawer */}
        {state.drawerOpen && state.selectedEvent && (
          <aside className="brain-page__drawer">
            <div className="brain-page__drawer-header">
              <h2 className="brain-page__drawer-title">{state.selectedEvent.title}</h2>
              <button
                className="brain-page__drawer-close"
                onClick={handleDrawerClose}
                aria-label="Close drawer"
              >
                ×
              </button>
            </div>

            <div className="brain-page__drawer-content">
              {/* Type-specific detail view will go here in Phase 2 */}
              <DetailPreview event={state.selectedEvent} />
            </div>
          </aside>
        )}
      </div>

      {/* Error Toast */}
      {stream.error && !stream.reconnecting && (
        <div className="brain-page__error">
          <span>{stream.error.message}</span>
          <button onClick={stream.reconnect}>Retry</button>
        </div>
      )}
    </div>
  );
}

export default BrainPage;
