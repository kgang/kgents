/**
 * BrainPage — Memory exploration, context surfacing, health monitoring
 *
 * A comprehensive surface for the Brain Crown Jewel:
 * - Health dashboard showing captures, vectors, coherency
 * - Semantic search: "What do I know about X?"
 * - Recent memories browser
 * - Serendipitous surfacing (The Accursed Share)
 * - Navigation to Editor for source files
 *
 * "The proof IS the decision. The mark IS the witness."
 */

import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import brainApi, {
  type BrainStatusResponse,
  type SearchResult,
  type CaptureItem,
} from '../api/brain';

import './BrainPage.css';

// =============================================================================
// Sub-components
// =============================================================================

interface StatusCardProps {
  label: string;
  value: string | number;
  icon: string;
  highlight?: boolean;
}

function StatusCard({ label, value, icon, highlight }: StatusCardProps) {
  return (
    <div className={`brain-status-card ${highlight ? 'brain-status-card--highlight' : ''}`}>
      <span className="brain-status-card__icon">{icon}</span>
      <div className="brain-status-card__content">
        <span className="brain-status-card__value">{value}</span>
        <span className="brain-status-card__label">{label}</span>
      </div>
    </div>
  );
}

interface MemoryItemProps {
  item: SearchResult | CaptureItem;
  onClick: () => void;
  showSimilarity?: boolean;
}

function MemoryItem({ item, onClick, showSimilarity }: MemoryItemProps) {
  const similarity = 'similarity' in item ? item.similarity : undefined;
  const isStale = 'is_stale' in item ? item.is_stale : false;

  // Format date
  const date = new Date(item.captured_at);
  const timeAgo = formatTimeAgo(date);

  return (
    <button className="brain-memory-item" onClick={onClick} data-stale={isStale}>
      <div className="brain-memory-item__header">
        <code className="brain-memory-item__id">{item.concept_id.slice(0, 20)}...</code>
        <span className="brain-memory-item__time">{timeAgo}</span>
        {showSimilarity && similarity !== undefined && (
          <span className="brain-memory-item__similarity">{(similarity * 100).toFixed(0)}%</span>
        )}
        {isStale && <span className="brain-memory-item__stale">stale</span>}
      </div>
      <p className="brain-memory-item__content">{item.content}</p>
    </button>
  );
}

function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

// =============================================================================
// Main Component
// =============================================================================

// eslint-disable-next-line complexity
export function BrainPage() {
  const navigate = useNavigate();

  // State
  const [status, setStatus] = useState<BrainStatusResponse | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [recentCaptures, setRecentCaptures] = useState<CaptureItem[]>([]);
  const [surfacedMemory, setSurfacedMemory] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [surfacing, setSurfacing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'recent' | 'search'>('recent');

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        const [statusData, capturesData] = await Promise.all([
          brainApi.getStatus(),
          brainApi.listCaptures(30),
        ]);
        setStatus(statusData);
        setRecentCaptures(capturesData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load brain data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Handle search
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;

    setSearching(true);
    setActiveTab('search');
    setError(null);

    try {
      const results = await brainApi.search(searchQuery, 30);
      setSearchResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setSearching(false);
    }
  }, [searchQuery]);

  // Handle surface (serendipity)
  const handleSurface = useCallback(async () => {
    setSurfacing(true);
    setError(null);

    try {
      const memory = await brainApi.surface(searchQuery || undefined, 0.7);
      setSurfacedMemory(memory);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Surface failed');
    } finally {
      setSurfacing(false);
    }
  }, [searchQuery]);

  // Navigate to editor with memory context
  const handleMemoryClick = useCallback(
    (conceptId: string) => {
      // For now, just navigate to editor with a search param
      // In the future, this could open the source file if available
      navigate(`/editor?memory=${encodeURIComponent(conceptId)}`);
    },
    [navigate]
  );

  // Handle key press for search
  const handleKeyPress = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') {
        handleSearch();
      }
    },
    [handleSearch]
  );

  // Calculate health percentage
  const healthPercent = status ? Math.round(status.coherency_rate * 100) : 0;

  if (loading) {
    return (
      <div className="brain-page brain-page--loading">
        <div className="brain-page__loader">
          <span className="brain-page__loader-icon">🧠</span>
          <span>Loading brain...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="brain-page">
      {/* Header */}
      <header className="brain-page__header">
        <h1 className="brain-page__title">
          <span className="brain-page__title-icon">🧠</span>
          Brain
        </h1>
        <p className="brain-page__subtitle">Memory exploration • Context surfacing • Health</p>
      </header>

      {/* Status Dashboard */}
      {status && (
        <section className="brain-page__dashboard">
          <div className="brain-page__health">
            <div className="brain-page__health-bar">
              <div
                className="brain-page__health-fill"
                style={{ width: `${healthPercent}%` }}
                data-health={
                  healthPercent > 90 ? 'excellent' : healthPercent > 70 ? 'good' : 'warn'
                }
              />
            </div>
            <span className="brain-page__health-label">{healthPercent}% coherent</span>
          </div>

          <div className="brain-page__status-grid">
            <StatusCard icon="📦" label="Captures" value={status.total_captures} />
            <StatusCard icon="🔢" label="Vectors" value={status.vector_count} />
            <StatusCard
              icon={status.has_semantic ? '✨' : '🔤'}
              label="Mode"
              value={status.has_semantic ? 'Semantic' : 'Hash-based'}
              highlight={status.has_semantic}
            />
            <StatusCard icon="👻" label="Ghosts Healed" value={status.ghosts_healed} />
            <StatusCard
              icon={status.storage_backend === 'postgres' ? '🐘' : '📁'}
              label="Backend"
              value={status.storage_backend === 'postgres' ? 'PostgreSQL' : 'SQLite'}
            />
          </div>
        </section>
      )}

      {/* Search Bar */}
      <section className="brain-page__search">
        <div className="brain-page__search-bar">
          <input
            type="text"
            className="brain-page__search-input"
            placeholder="What do I know about..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button
            className="brain-page__search-btn"
            onClick={handleSearch}
            disabled={searching || !searchQuery.trim()}
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
          <button
            className="brain-page__surface-btn"
            onClick={handleSurface}
            disabled={surfacing}
            title="Surface a serendipitous memory"
          >
            {surfacing ? '...' : '🎲'}
          </button>
        </div>
      </section>

      {/* Surfaced Memory (Serendipity) */}
      {surfacedMemory && (
        <section className="brain-page__surfaced">
          <h3 className="brain-page__section-title">
            <span>🎲</span> Surfaced from the Void
          </h3>
          <MemoryItem
            item={surfacedMemory}
            onClick={() => handleMemoryClick(surfacedMemory.concept_id)}
            showSimilarity
          />
          <button className="brain-page__dismiss-btn" onClick={() => setSurfacedMemory(null)}>
            Dismiss
          </button>
        </section>
      )}

      {/* Tabs */}
      <div className="brain-page__tabs">
        <button
          className={`brain-page__tab ${activeTab === 'recent' ? 'brain-page__tab--active' : ''}`}
          onClick={() => setActiveTab('recent')}
        >
          Recent ({recentCaptures.length})
        </button>
        <button
          className={`brain-page__tab ${activeTab === 'search' ? 'brain-page__tab--active' : ''}`}
          onClick={() => setActiveTab('search')}
          disabled={searchResults.length === 0}
        >
          Search Results ({searchResults.length})
        </button>
      </div>

      {/* Memory List */}
      <section className="brain-page__memories">
        {activeTab === 'recent' ? (
          recentCaptures.length > 0 ? (
            <div className="brain-page__memory-list">
              {recentCaptures.map((capture) => (
                <MemoryItem
                  key={capture.concept_id}
                  item={capture}
                  onClick={() => handleMemoryClick(capture.concept_id)}
                />
              ))}
            </div>
          ) : (
            <div className="brain-page__empty">
              <p>No memories yet.</p>
              <p className="brain-page__empty-hint">
                Use <code>kg brain capture "..."</code> to store memories.
              </p>
            </div>
          )
        ) : searchResults.length > 0 ? (
          <div className="brain-page__memory-list">
            {searchResults.map((result) => (
              <MemoryItem
                key={result.concept_id}
                item={result}
                onClick={() => handleMemoryClick(result.concept_id)}
                showSimilarity
              />
            ))}
          </div>
        ) : (
          <div className="brain-page__empty">
            <p>No search results.</p>
            <p className="brain-page__empty-hint">Try a different query.</p>
          </div>
        )}
      </section>

      {/* Error Toast */}
      {error && (
        <div className="brain-page__error">
          <span>{error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
    </div>
  );
}

export default BrainPage;
