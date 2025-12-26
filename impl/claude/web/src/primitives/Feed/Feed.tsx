/**
 * Feed Component
 *
 * "The feed is not a view of data. The feed IS the primary interface."
 *
 * A universal chronological truth stream with:
 * - Infinite scroll with virtualization
 * - Layer/loss/author/time filtering
 * - Algorithmic ranking (principles-aligned)
 * - Feedback system integration
 */

import { memo, useCallback, useEffect, useRef, useState } from 'react';
import type {
  FeedProps,
  KBlock,
  FeedFilter,
  FeedRanking,
} from './types';
import { FeedItem } from './FeedItem';
import { FeedFilters } from './FeedFilters';
import { useFeedFeedback } from './useFeedFeedback';
import { useSimpleToast } from '../../hooks/useSimpleToast';
import './Feed.css';

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_PAGE_SIZE = 20;
const SCROLL_THRESHOLD = 200; // px from bottom to trigger load

// =============================================================================
// Component
// =============================================================================

export const Feed = memo(function Feed({
  feedId,
  onItemClick,
  onContradiction,
  initialFilters = [],
  initialRanking = 'chronological',
  infiniteScroll = true,
  virtualized = true,
  height = 800,
  className = '',
}: FeedProps) {
  // Toast for contradiction notifications
  const { toast } = useSimpleToast();

  // Handler for when contradictions are found on a feed item
  const handleContradiction = useCallback(
    (kblockA: KBlock, kblockB: KBlock) => {
      // Call the parent handler if provided
      if (onContradiction) {
        onContradiction(kblockA, kblockB);
      }

      // Show toast notification
      toast.warning(
        'Contradiction detected',
        `Between "${kblockA.title}" and "${kblockB.title}"`,
        { duration: 5000 }
      );

      // Log for debugging in development
      if (import.meta.env.DEV) {
        console.log('[Feed] Contradiction detected:', {
          a: { id: kblockA.id, title: kblockA.title },
          b: { id: kblockB.id, title: kblockB.title },
        });
      }
    },
    [onContradiction, toast]
  );

  // State
  const [items, setItems] = useState<KBlock[]>([]);
  const [filters, setFilters] = useState<FeedFilter[]>(initialFilters);
  const [ranking, setRanking] = useState<FeedRanking>(initialRanking);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);

  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sentinelRef = useRef<HTMLDivElement>(null);

  // Feedback system
  const {
    onView,
    onEngage,
    onDismiss,
  } = useFeedFeedback();

  // Fetch items via AGENTESE (or API for contradictions)
  const fetchItems = useCallback(
    async (pageNum: number, reset: boolean = false) => {
      setLoading(true);

      try {
        // Handle contradictions feed separately (uses /api/contradictions)
        if (feedId === 'contradictions') {
          const response = await fetch(`/api/contradictions?limit=${DEFAULT_PAGE_SIZE}&offset=${pageNum * DEFAULT_PAGE_SIZE}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${await response.text()}`);
          }

          const data = await response.json();

          // Transform contradictions to K-Block-like format for display
          const fetchedItems: KBlock[] = (data.contradictions || []).map((c: any) => ({
            id: c.id,
            title: `${c.type}: ${c.k_block_a?.title || 'Thesis'} vs ${c.k_block_b?.title || 'Antithesis'}`,
            content: `**Thesis:** ${c.k_block_a?.content || ''}\n\n**Antithesis:** ${c.k_block_b?.content || ''}`,
            layer: 2, // Contradictions are value-layer concerns
            loss: c.severity,
            author: 'system',
            createdAt: new Date(c.detected_at),
            updatedAt: new Date(c.detected_at),
            tags: [c.type, c.suggested_strategy].filter(Boolean),
            principles: [],
            edgeCount: 2, // Always two K-Blocks involved
            preview: `${c.k_block_a?.content?.slice(0, 100) || ''} vs ${c.k_block_b?.content?.slice(0, 100) || ''}`,
          }));

          // Apply client-side filters
          const filtered = applyFilters(fetchedItems, filters);

          if (reset) {
            setItems(filtered);
          } else {
            setItems((prev) => [...prev, ...filtered]);
          }

          setHasMore(data.has_more || false);
          setLoading(false);
          return;
        }

        // AGENTESE call to get feed items
        const aspect = feedId === 'cosmos' ? 'cosmos' : feedId === 'coherent' ? 'coherent' : 'cosmos';
        const response = await fetch(`/agentese/self/feed/${aspect}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            offset: pageNum * DEFAULT_PAGE_SIZE,
            limit: DEFAULT_PAGE_SIZE,
            ranking: ranking,
            ...(aspect === 'coherent' && { max_loss: 0.2 }),
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }

        const data = await response.json();
        const result = data.result || data;

        if (result.error) {
          throw new Error(result.error);
        }

        // Transform backend items to frontend format
        const fetchedItems: KBlock[] = (result.items || []).map((item: any) => ({
          id: item.id,
          title: item.title,
          content: item.content,
          layer: item.layer,
          loss: item.loss,
          author: item.author,
          createdAt: new Date(item.createdAt),
          updatedAt: new Date(item.updatedAt),
          tags: item.tags || [],
          principles: item.principles || [],
          edgeCount: item.edgeCount || 0,
          preview: item.preview,
        }));

        // Apply client-side filters
        const filtered = applyFilters(fetchedItems, filters);

        // Update state
        if (reset) {
          setItems(filtered);
        } else {
          setItems((prev) => [...prev, ...filtered]);
        }

        // Check if there are more items
        setHasMore(result.has_more || false);
      } catch (error) {
        console.error('[Feed] Error fetching items:', error);
        // Fall back to empty state on error
        if (reset) {
          setItems([]);
        }
        setHasMore(false);
      } finally {
        setLoading(false);
      }
    },
    [feedId, filters, ranking]
  );

  // Load more items
  const loadMore = useCallback(() => {
    if (!loading && hasMore && infiniteScroll) {
      setPage((p) => p + 1);
    }
  }, [loading, hasMore, infiniteScroll]);

  // Initial load
  useEffect(() => {
    setPage(0);
    fetchItems(0, true);
  }, [feedId, filters, ranking]);

  // Load more when page changes
  useEffect(() => {
    if (page > 0) {
      fetchItems(page);
    }
  }, [page]);

  // Infinite scroll with Intersection Observer
  useEffect(() => {
    if (!infiniteScroll || !sentinelRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading && hasMore) {
          loadMore();
        }
      },
      { rootMargin: `${SCROLL_THRESHOLD}px` }
    );

    observerRef.current.observe(sentinelRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [infiniteScroll, loading, hasMore, loadMore]);

  // Item click handler
  const handleItemClick = useCallback(
    (kblock: KBlock) => {
      setExpandedId((prev) => (prev === kblock.id ? null : kblock.id));
      onEngage(kblock);
      onItemClick(kblock);
    },
    [onItemClick, onEngage]
  );

  // Filter change handler
  const handleFiltersChange = useCallback((newFilters: FeedFilter[]) => {
    setFilters(newFilters);
    setPage(0);
  }, []);

  // Ranking change handler
  const handleRankingChange = useCallback((newRanking: FeedRanking) => {
    setRanking(newRanking);
    setPage(0);
  }, []);

  // Create a contradiction click handler for each item
  const createContradictionClickHandler = useCallback(
    (currentKBlock: KBlock) => (contradictingKBlock: KBlock) => {
      handleContradiction(currentKBlock, contradictingKBlock);
    },
    [handleContradiction]
  );

  return (
    <div className={`feed ${className}`}>
      {/* Filters */}
      <FeedFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        ranking={ranking}
        onRankingChange={handleRankingChange}
      />

      {/* Feed items */}
      <div
        ref={containerRef}
        className="feed__container"
        style={virtualized ? { height: `${height}px` } : undefined}
      >
        {items.length === 0 && !loading ? (
          <div className="feed__empty">
            <div className="feed__empty-icon">📭</div>
            <div className="feed__empty-title">No items in feed</div>
            <div className="feed__empty-message">
              Try adjusting your filters or create some K-Blocks to see them here.
            </div>
          </div>
        ) : (
          <div className="feed__items">
            {items.map((kblock) => (
              <FeedItem
                key={kblock.id}
                kblock={kblock}
                isExpanded={expandedId === kblock.id}
                onClick={() => handleItemClick(kblock)}
                onView={() => onView(kblock)}
                onEngage={() => onEngage(kblock)}
                onDismiss={() => onDismiss(kblock)}
                onContradictionClick={createContradictionClickHandler(kblock)}
              />
            ))}

            {/* Loading indicator */}
            {loading && (
              <div className="feed__loading">
                <div className="feed__loading-spinner" />
                <div className="feed__loading-text">Loading...</div>
              </div>
            )}

            {/* Infinite scroll sentinel */}
            {infiniteScroll && hasMore && (
              <div ref={sentinelRef} className="feed__sentinel" />
            )}

            {/* End of feed */}
            {!hasMore && items.length > 0 && (
              <div className="feed__end">
                <div className="feed__end-line" />
                <div className="feed__end-text">End of feed</div>
                <div className="feed__end-line" />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Apply filters to K-Blocks.
 */
function applyFilters(items: KBlock[], filters: FeedFilter[]): KBlock[] {
  return items.filter((item) => {
    for (const filter of filters) {
      if (!filter.active) continue;

      switch (filter.type) {
        case 'layer':
          if (item.layer !== filter.value) return false;
          break;

        case 'loss-range':
          if (Array.isArray(filter.value)) {
            const [min, max] = filter.value as [number, number];
            if (item.loss < min || item.loss > max) return false;
          }
          break;

        case 'author':
          if (item.author !== filter.value) return false;
          break;

        case 'time-range':
          if (Array.isArray(filter.value)) {
            const [start, end] = filter.value as [Date, Date];
            const itemDate = new Date(item.createdAt);
            if (itemDate < start || itemDate > end) return false;
          }
          break;

        case 'tag':
          if (!item.tags.includes(filter.value as string)) return false;
          break;

        case 'principle':
          if (!item.principles.includes(filter.value as string)) return false;
          break;
      }
    }

    return true;
  });
}

// NOTE: Ranking is now handled by the backend in self.feed.cosmos and self.feed.coherent.
// Client-side ranking removed - backend is the source of truth.
