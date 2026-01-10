/**
 * FeedPage — The Stigmergic Surface
 *
 * "The feed is not a view of data. The feed IS the primary interface."
 *
 * Philosophy:
 *   Full-screen unified feed with K-Blocks AND Witness Marks interleaved.
 *   The cosmos of knowledge and decisions, navigable by coherence.
 *
 * STARK BIOME: 90% steel, 10% earned glow.
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Feed } from '../primitives/Feed';
import type { FeedFilter, FeedRanking, KBlock } from '../primitives/Feed/types';
import { useWitnessStream } from '../hooks/useWitnessStream';
import { getRecentMarks, type Mark } from '../api/witness';
import './FeedPage.css';

// =============================================================================
// Types
// =============================================================================

/** Page-level ranking options (mapped to FeedRanking) */
type PageRanking = 'chronological' | 'coherence' | 'principles';

/** Feed aspect options */
type FeedAspect = 'cosmos' | 'unified' | 'contradictions';

/** Maps page ranking to Feed ranking */
const RANKING_MAP: Record<PageRanking, FeedRanking> = {
  chronological: 'chronological',
  coherence: 'loss-ascending',
  principles: 'algorithmic',
};

// =============================================================================
// Utility: Check if recent (for breathing animation)
// =============================================================================

const RECENT_THRESHOLD_MS = 60 * 1000; // 60 seconds

function isRecent(timestamp: Date): boolean {
  return Date.now() - timestamp.getTime() < RECENT_THRESHOLD_MS;
}

// =============================================================================
// Main Component
// =============================================================================

export function FeedPage() {
  const navigate = useNavigate();
  const [ranking, setRanking] = useState<PageRanking>('chronological');
  const [feedAspect, setFeedAspect] = useState<FeedAspect>('unified');
  const [filters, setFilters] = useState<FeedFilter[]>([]);
  const [feedHeight, setFeedHeight] = useState(window.innerHeight - 120);

  // Selected mark for detail view
  const [selectedMark, setSelectedMark] = useState<Mark | null>(null);

  // Witness stream for real-time marks
  const { events: streamEvents, connected: witnessConnected } = useWitnessStream();

  // Initial marks loaded from API
  const [initialMarks, setInitialMarks] = useState<Mark[]>([]);
  const [marksLoading, setMarksLoading] = useState(true);

  // Fetch initial marks on mount
  useEffect(() => {
    async function fetchMarks() {
      try {
        const marks = await getRecentMarks({ today: true, limit: 50 });
        setInitialMarks(marks);
      } catch (error) {
        console.error('[FeedPage] Error fetching marks:', error);
      } finally {
        setMarksLoading(false);
      }
    }
    fetchMarks();
  }, []);

  // Merge stream events with initial marks, deduplicate by ID
  const allMarks = useMemo(() => {
    const markMap = new Map<string, Mark>();

    // Add initial marks
    for (const mark of initialMarks) {
      markMap.set(mark.id, mark);
    }

    // Add/update from stream events (only 'mark' type events)
    for (const event of streamEvents) {
      if (event.type === 'mark' && event.id) {
        // Convert WitnessEvent to Mark
        const mark: Mark = {
          id: event.id,
          action: event.action || '',
          reasoning: event.reasoning,
          principles: event.principles || [],
          author: (event.author as 'kent' | 'claude' | 'system') || 'system',
          timestamp: event.timestamp.toISOString(),
        };
        markMap.set(mark.id, mark);
      }
    }

    return Array.from(markMap.values());
  }, [initialMarks, streamEvents]);

  // Update feed height on resize
  useEffect(() => {
    const handleResize = () => {
      setFeedHeight(window.innerHeight - 120);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Navigate to editor for K-Block (or contradiction workspace for contradictions)
  const handleItemClick = useCallback(
    (kblock: KBlock) => {
      if (feedAspect === 'contradictions') {
        // Navigate to contradiction workspace
        navigate(`/world.contradiction/${kblock.id}`);
      } else {
        navigate(`/world.document/${kblock.id}`);
      }
    },
    [navigate, feedAspect]
  );

  // Handle mark click - show detail panel
  const handleMarkClick = useCallback((mark: Mark) => {
    setSelectedMark(mark);
  }, []);

  // Close detail panel
  const handleCloseDetail = useCallback(() => {
    setSelectedMark(null);
  }, []);

  // Handle contradiction click (log for now, could open modal)
  const handleContradiction = useCallback((a: KBlock, b: KBlock) => {
    console.info('[FeedPage] Contradiction detected:', a.id, '<->', b.id);
    // TODO: Open contradiction resolution modal
  }, []);

  // Update filters from child components
  const handleFiltersChange = useCallback((newFilters: FeedFilter[]) => {
    setFilters(newFilters);
  }, []);

  return (
    <div className="feed-page">
      <header className="feed-page__header">
        <div className="feed-page__title-section">
          <span className="feed-page__icon">Feed</span>
          <h1 className="feed-page__title">K-gents Feed</h1>
          {feedAspect === 'unified' && (
            <span
              className={`feed-page__witness-status ${witnessConnected ? 'feed-page__witness-status--connected' : ''}`}
              title={witnessConnected ? 'Witness stream connected' : 'Witness stream disconnected'}
            >
              {witnessConnected ? 'Live' : 'Offline'}
            </span>
          )}
        </div>
        <div className="feed-page__controls">
          <RankingSelector value={ranking} onChange={setRanking} />
          <FilterDropdown filters={filters} onChange={handleFiltersChange} />
        </div>
      </header>

      <nav className="feed-page__ranking-bar">
        <span className="feed-page__ranking-label">View:</span>
        <AspectPills value={feedAspect} onChange={setFeedAspect} />
        {feedAspect !== 'contradictions' && (
          <>
            <span className="feed-page__ranking-label feed-page__ranking-label--secondary">
              Ranking:
            </span>
            <RankingPills value={ranking} onChange={setRanking} />
          </>
        )}
      </nav>

      <main className="feed-page__main">
        {feedAspect === 'unified' ? (
          <UnifiedFeed
            marks={allMarks}
            marksLoading={marksLoading}
            onMarkClick={handleMarkClick}
            height={feedHeight}
          />
        ) : (
          <Feed
            feedId={feedAspect}
            initialRanking={RANKING_MAP[ranking]}
            initialFilters={filters}
            onItemClick={handleItemClick}
            onContradiction={handleContradiction}
            infiniteScroll={true}
            virtualized={true}
            height={feedHeight}
          />
        )}
      </main>

      {/* Mark Detail Panel (slide-in from right) */}
      {selectedMark && <MarkDetailPanel mark={selectedMark} onClose={handleCloseDetail} />}
    </div>
  );
}

// =============================================================================
// Mark Detail Panel (Full details on click)
// =============================================================================

interface MarkDetailPanelProps {
  mark: Mark;
  onClose: () => void;
}

function MarkDetailPanel({ mark, onClose }: MarkDetailPanelProps) {
  const timestamp = new Date(mark.timestamp);

  // Author color mapping
  const authorColors: Record<string, string> = {
    kent: '#6b8b6b', // mint (human)
    claude: '#c4a77d', // spore (AI)
    system: '#5a5a64', // steel (system)
  };

  return (
    <>
      {/* Backdrop */}
      <div className="mark-detail__backdrop" onClick={onClose} />

      {/* Panel */}
      <div className="mark-detail__panel">
        {/* Header */}
        <div className="mark-detail__header">
          <div className="mark-detail__header-left">
            <span className="mark-detail__icon">⊢</span>
            <span className="mark-detail__title">Witness Mark</span>
          </div>
          <button className="mark-detail__close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        {/* Meta row */}
        <div className="mark-detail__meta">
          <span
            className="mark-detail__author"
            style={{ color: authorColors[mark.author] || authorColors.system }}
          >
            {mark.author}
          </span>
          <span className="mark-detail__time">
            {timestamp.toLocaleString('en-US', {
              weekday: 'short',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>

        {/* Action */}
        <div className="mark-detail__section">
          <div className="mark-detail__label">Action</div>
          <div className="mark-detail__action">{mark.action}</div>
        </div>

        {/* Reasoning (full, not truncated) */}
        {mark.reasoning && (
          <div className="mark-detail__section">
            <div className="mark-detail__label">Reasoning</div>
            <div className="mark-detail__reasoning">{mark.reasoning}</div>
          </div>
        )}

        {/* Principles */}
        {mark.principles.length > 0 && (
          <div className="mark-detail__section">
            <div className="mark-detail__label">Principles</div>
            <div className="mark-detail__principles">
              {mark.principles.map((principle) => (
                <span key={principle} className="mark-detail__principle">
                  {principle}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* ID (for reference) */}
        <div className="mark-detail__section mark-detail__section--subtle">
          <div className="mark-detail__label">ID</div>
          <div className="mark-detail__id">{mark.id}</div>
        </div>
      </div>
    </>
  );
}

// =============================================================================
// Unified Feed Component (Marks + K-Blocks)
// =============================================================================

interface UnifiedFeedProps {
  marks: Mark[];
  marksLoading: boolean;
  onMarkClick: (mark: Mark) => void;
  height: number;
}

function UnifiedFeed({ marks, marksLoading, onMarkClick, height }: UnifiedFeedProps) {
  // Sort marks by timestamp descending (newest first)
  const sortedMarks = useMemo(() => {
    return [...marks].sort((a, b) => {
      const dateA = new Date(a.timestamp);
      const dateB = new Date(b.timestamp);
      return dateB.getTime() - dateA.getTime();
    });
  }, [marks]);

  if (marksLoading) {
    return (
      <div className="feed__loading" style={{ height }}>
        <div className="feed__loading-spinner" />
        <div className="feed__loading-text">Loading witness marks...</div>
      </div>
    );
  }

  if (sortedMarks.length === 0) {
    return (
      <div className="feed__empty" style={{ height }}>
        <div className="feed__empty-icon">witness</div>
        <div className="feed__empty-title">No witness marks today</div>
        <div className="feed__empty-message">
          Create marks with `km "action"` or through the witness UI.
        </div>
      </div>
    );
  }

  return (
    <div className="unified-feed" style={{ height, overflowY: 'auto' }}>
      <div className="unified-feed__items">
        {sortedMarks.map((mark) => (
          <MarkFeedItem key={mark.id} mark={mark} onClick={() => onMarkClick(mark)} />
        ))}
      </div>
      <div className="feed__end">
        <div className="feed__end-line" />
        <div className="feed__end-text">End of marks</div>
        <div className="feed__end-line" />
      </div>
    </div>
  );
}

// =============================================================================
// Mark Feed Item Component
// =============================================================================

interface MarkFeedItemProps {
  mark: Mark;
  onClick: () => void;
}

function MarkFeedItem({ mark, onClick }: MarkFeedItemProps) {
  const timestamp = new Date(mark.timestamp);
  const recent = isRecent(timestamp);
  const formattedTime = formatTimestamp(timestamp);

  // Truncate reasoning for preview
  const reasoningPreview = mark.reasoning
    ? mark.reasoning.length > 120
      ? mark.reasoning.substring(0, 120) + '...'
      : mark.reasoning
    : null;

  // Author color mapping
  const authorColors: Record<string, string> = {
    kent: '#6b8b6b', // mint (human)
    claude: '#c4a77d', // spore (AI)
    system: '#5a5a64', // steel (system)
  };

  return (
    <div
      className={`mark-feed-item ${recent ? 'mark-feed-item--recent breathe-subtle' : ''}`}
      onClick={onClick}
    >
      {/* Left gutter - mark icon */}
      <div className="mark-feed-item__icon" title="Witness Mark">
        ⊢
      </div>

      {/* Main content */}
      <div className="mark-feed-item__content">
        {/* Header row */}
        <div className="mark-feed-item__header">
          <span
            className="mark-feed-item__author"
            style={{ color: authorColors[mark.author] || authorColors.system }}
          >
            {mark.author}
          </span>
          <span className="mark-feed-item__time" title={timestamp.toISOString()}>
            {formattedTime}
          </span>
        </div>

        {/* Action (main text) */}
        <div className="mark-feed-item__action">{mark.action}</div>

        {/* Reasoning preview */}
        {reasoningPreview && <div className="mark-feed-item__reasoning">{reasoningPreview}</div>}

        {/* Principles tags */}
        {mark.principles.length > 0 && (
          <div className="mark-feed-item__principles">
            {mark.principles.slice(0, 4).map((principle) => (
              <span key={principle} className="mark-feed-item__principle">
                {principle}
              </span>
            ))}
            {mark.principles.length > 4 && (
              <span className="mark-feed-item__principle mark-feed-item__principle--more">
                +{mark.principles.length - 4}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Right indicator - recent badge */}
      {recent && (
        <div className="mark-feed-item__recent-badge" title="Recent (< 60s)">
          ●
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Utility: Format timestamp
// =============================================================================

function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  // Less than 1 minute
  if (diff < 60 * 1000) {
    return 'just now';
  }

  // Less than 1 hour
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes}m ago`;
  }

  // Less than 1 day
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}h ago`;
  }

  // More than 1 day - show full date
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// =============================================================================
// Ranking Selector (Compact Dropdown)
// =============================================================================

interface RankingSelectorProps {
  value: PageRanking;
  onChange: (ranking: PageRanking) => void;
}

function RankingSelector({ value, onChange }: RankingSelectorProps) {
  return (
    <select
      className="feed-page__ranking-select"
      value={value}
      onChange={(e) => onChange(e.target.value as PageRanking)}
      aria-label="Sort feed"
    >
      <option value="chronological">Recent</option>
      <option value="coherence">Grounded</option>
      <option value="principles">Principled</option>
    </select>
  );
}

// =============================================================================
// Aspect Pills (Feed Source Toggle)
// =============================================================================

interface AspectPillsProps {
  value: FeedAspect;
  onChange: (aspect: FeedAspect) => void;
}

function AspectPills({ value, onChange }: AspectPillsProps) {
  const options: { id: FeedAspect; label: string; icon: string }[] = [
    { id: 'unified', label: 'Unified', icon: '' },
    { id: 'cosmos', label: 'K-Blocks', icon: '' },
    { id: 'contradictions', label: 'Contradictions', icon: '' },
  ];

  return (
    <div className="aspect-pills" role="tablist" aria-label="Feed aspect">
      {options.map((opt) => (
        <button
          key={opt.id}
          role="tab"
          aria-selected={value === opt.id}
          className={`aspect-pills__btn ${value === opt.id ? 'aspect-pills__btn--active' : ''} ${opt.id === 'contradictions' ? 'aspect-pills__btn--contradiction' : ''} ${opt.id === 'unified' ? 'aspect-pills__btn--unified' : ''}`}
          onClick={() => onChange(opt.id)}
        >
          <span className="aspect-pills__icon">{opt.icon}</span>
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Ranking Pills (Visible in Ranking Bar)
// =============================================================================

interface RankingPillsProps {
  value: PageRanking;
  onChange: (ranking: PageRanking) => void;
}

function RankingPills({ value, onChange }: RankingPillsProps) {
  const options: { id: PageRanking; label: string }[] = [
    { id: 'chronological', label: 'Chronological' },
    { id: 'coherence', label: 'By Coherence' },
    { id: 'principles', label: 'By Principles' },
  ];

  return (
    <div className="ranking-pills" role="tablist" aria-label="Feed ranking">
      {options.map((opt) => (
        <button
          key={opt.id}
          role="tab"
          aria-selected={value === opt.id}
          className={`ranking-pills__btn ${value === opt.id ? 'ranking-pills__btn--active' : ''}`}
          onClick={() => onChange(opt.id)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

// =============================================================================
// Filter Dropdown
// =============================================================================

interface FilterDropdownProps {
  filters: FeedFilter[];
  onChange: (filters: FeedFilter[]) => void;
}

function FilterDropdown({ filters, onChange }: FilterDropdownProps) {
  const [open, setOpen] = useState(false);

  // Quick filter presets
  const addLayerFilter = (layer: number) => {
    const layerNames: Record<number, string> = {
      0: 'Ground',
      1: 'Axiom',
      2: 'Principle',
      3: 'Capability',
      4: 'Domain',
      5: 'Service',
      6: 'Implementation',
    };
    const newFilter: FeedFilter = {
      type: 'layer',
      value: layer,
      label: `L${layer}: ${layerNames[layer] || 'Unknown'}`,
      active: true,
    };
    onChange([...filters, newFilter]);
    setOpen(false);
  };

  const addLossFilter = (min: number, max: number, label: string) => {
    const newFilter: FeedFilter = {
      type: 'loss-range',
      value: [min, max],
      label,
      active: true,
    };
    onChange([...filters, newFilter]);
    setOpen(false);
  };

  const clearFilters = () => {
    onChange([]);
    setOpen(false);
  };

  const activeCount = filters.filter((f) => f.active).length;

  return (
    <div className="filter-dropdown">
      <button
        className="filter-dropdown__trigger"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-haspopup="menu"
      >
        <span className="filter-dropdown__icon">Filters</span>
        {activeCount > 0 && <span className="filter-dropdown__badge">{activeCount}</span>}
        <span className="filter-dropdown__chevron">{open ? '...' : '...'}</span>
      </button>

      {open && (
        <div className="filter-dropdown__menu" role="menu">
          <div className="filter-dropdown__section">
            <div className="filter-dropdown__section-title">By Layer</div>
            <div className="filter-dropdown__options">
              {[0, 1, 2, 3, 4, 5, 6].map((layer) => (
                <button
                  key={layer}
                  className="filter-dropdown__option"
                  onClick={() => addLayerFilter(layer)}
                  role="menuitem"
                >
                  L{layer}
                </button>
              ))}
            </div>
          </div>

          <div className="filter-dropdown__section">
            <div className="filter-dropdown__section-title">By Loss</div>
            <div className="filter-dropdown__options">
              <button
                className="filter-dropdown__option filter-dropdown__option--grounded"
                onClick={() => addLossFilter(0, 0.2, 'Grounded (0-20%)')}
                role="menuitem"
              >
                Grounded
              </button>
              <button
                className="filter-dropdown__option filter-dropdown__option--exploratory"
                onClick={() => addLossFilter(0.2, 0.5, 'Exploratory (20-50%)')}
                role="menuitem"
              >
                Exploratory
              </button>
              <button
                className="filter-dropdown__option filter-dropdown__option--frontier"
                onClick={() => addLossFilter(0.5, 1.0, 'Frontier (50-100%)')}
                role="menuitem"
              >
                Frontier
              </button>
            </div>
          </div>

          {filters.length > 0 && (
            <div className="filter-dropdown__section">
              <button className="filter-dropdown__clear" onClick={clearFilters} role="menuitem">
                Clear All Filters
              </button>
            </div>
          )}

          {/* Active filters */}
          {filters.length > 0 && (
            <div className="filter-dropdown__active">
              <div className="filter-dropdown__section-title">Active</div>
              <div className="filter-dropdown__active-list">
                {filters.map((filter, i) => (
                  <span
                    key={i}
                    className={`filter-dropdown__chip ${filter.active ? 'filter-dropdown__chip--active' : ''}`}
                    onClick={() => {
                      const updated = [...filters];
                      updated[i] = { ...updated[i], active: !updated[i].active };
                      onChange(updated);
                    }}
                  >
                    {filter.label}
                    <button
                      className="filter-dropdown__chip-remove"
                      onClick={(e) => {
                        e.stopPropagation();
                        onChange(filters.filter((_, idx) => idx !== i));
                      }}
                      aria-label={`Remove ${filter.label} filter`}
                    >
                      x
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FeedPage;
