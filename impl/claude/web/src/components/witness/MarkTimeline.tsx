/**
 * MarkTimeline: Chronological display of witness marks.
 *
 * Displays marks grouped by day or session with:
 * - Day/session separators
 * - Virtualized list for performance
 * - Loading states with skeleton
 * - Empty state handling
 *
 * "The marks accumulate like leaves in autumn."
 *
 * @see plans/witness-fusion-ux-design.md
 */

import { useMemo, useCallback, useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MarkCard, type MarkDensity } from './MarkCard';
import type { Mark } from '@/api/witness';
import { groupMarksByDay, groupMarksBySession } from '@/api/witness';

// =============================================================================
// Living Earth Palette
// =============================================================================

const LIVING_EARTH = {
  soil: '#2D1B14',
  soilLight: '#3D2B24',
  wood: '#6B4E3D',
  woodLight: '#8B6E5D',
  copper: '#C08552',
  honey: '#E8C4A0',
  lantern: '#F5E6D3',
} as const;

// =============================================================================
// Types
// =============================================================================

export type GroupBy = 'day' | 'session' | 'none';

export interface MarkTimelineProps {
  /** Marks to display (sorted by timestamp descending) */
  marks: Mark[];

  /** How to group marks */
  groupBy?: GroupBy;

  /** Display density for mark cards */
  density?: MarkDensity;

  /** Loading state */
  isLoading?: boolean;

  /** Error message */
  error?: string | null;

  /** Callback when a mark is retracted */
  onRetract?: (markId: string) => void;

  /** Callback when a mark is selected */
  onSelect?: (mark: Mark) => void;

  /** Currently selected mark ID */
  selectedMarkId?: string | null;

  /** Height for virtualization (if not set, uses container height) */
  height?: number | string;

  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Sub-components
// =============================================================================

interface DaySeparatorProps {
  date: string;
  count: number;
}

function DaySeparator({ date, count }: DaySeparatorProps) {
  const today = new Date().toLocaleDateString();
  const yesterday = new Date(Date.now() - 86400000).toLocaleDateString();

  let label = date;
  if (date === today) {
    label = 'Today';
  } else if (date === yesterday) {
    label = 'Yesterday';
  }

  return (
    <div
      className="flex items-center gap-3 py-3 px-2"
      data-testid="day-separator"
    >
      <div
        className="flex-1 h-px"
        style={{ backgroundColor: LIVING_EARTH.wood }}
      />
      <span
        className="text-sm font-medium"
        style={{ color: LIVING_EARTH.honey }}
      >
        {label}
      </span>
      <span
        className="text-xs px-2 py-0.5 rounded-full"
        style={{
          backgroundColor: `${LIVING_EARTH.copper}20`,
          color: LIVING_EARTH.copper,
        }}
      >
        {count} {count === 1 ? 'mark' : 'marks'}
      </span>
      <div
        className="flex-1 h-px"
        style={{ backgroundColor: LIVING_EARTH.wood }}
      />
    </div>
  );
}

interface SessionSeparatorProps {
  sessionId: string;
  count: number;
}

function SessionSeparator({ sessionId, count }: SessionSeparatorProps) {
  const shortId = sessionId.slice(0, 8);

  return (
    <div
      className="flex items-center gap-3 py-2 px-2"
      data-testid="session-separator"
    >
      <span
        className="text-xs"
        style={{ color: LIVING_EARTH.wood }}
      >
        Session {shortId}...
      </span>
      <span
        className="text-xs"
        style={{ color: LIVING_EARTH.woodLight }}
      >
        ({count} marks)
      </span>
    </div>
  );
}

function LoadingSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-2 p-2" data-testid="loading-skeleton">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          className="rounded-lg p-3"
          style={{ backgroundColor: LIVING_EARTH.soilLight }}
          animate={{
            opacity: [0.5, 0.8, 0.5],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: i * 0.1,
          }}
        >
          <div className="flex items-center gap-2 mb-2">
            <div
              className="w-12 h-3 rounded"
              style={{ backgroundColor: LIVING_EARTH.wood }}
            />
            <div
              className="w-5 h-5 rounded-full"
              style={{ backgroundColor: LIVING_EARTH.wood }}
            />
          </div>
          <div
            className="w-3/4 h-4 rounded"
            style={{ backgroundColor: LIVING_EARTH.wood }}
          />
        </motion.div>
      ))}
    </div>
  );
}

function EmptyState() {
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-12 px-4 text-center"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      data-testid="empty-state"
    >
      <span className="text-4xl mb-4">🍂</span>
      <h3
        className="text-lg font-medium mb-2"
        style={{ color: LIVING_EARTH.lantern }}
      >
        No marks yet
      </h3>
      <p
        className="text-sm max-w-xs"
        style={{ color: LIVING_EARTH.woodLight }}
      >
        Every action leaves a mark. Start witnessing your decisions with{' '}
        <code className="px-1 rounded" style={{ backgroundColor: LIVING_EARTH.soil }}>
          km "your action"
        </code>
      </p>
    </motion.div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-12 px-4 text-center"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      data-testid="error-state"
    >
      <span className="text-4xl mb-4">\u26A0\uFE0F</span>
      <h3
        className="text-lg font-medium mb-2"
        style={{ color: LIVING_EARTH.copper }}
      >
        Something went wrong
      </h3>
      <p
        className="text-sm max-w-xs"
        style={{ color: LIVING_EARTH.woodLight }}
      >
        {message}
      </p>
    </motion.div>
  );
}

// =============================================================================
// Virtualization Hook (Simple Implementation)
// =============================================================================

interface VirtualItem {
  index: number;
  start: number;
  size: number;
}

function useVirtualList(
  itemCount: number,
  itemHeight: number,
  containerRef: React.RefObject<HTMLDivElement | null>,
  overscan: number = 3
) {
  const [scrollTop, setScrollTop] = useState(0);
  const [containerHeight, setContainerHeight] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      setScrollTop(container.scrollTop);
    };

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setContainerHeight(entry.contentRect.height);
      }
    });

    container.addEventListener('scroll', handleScroll, { passive: true });
    observer.observe(container);

    return () => {
      container.removeEventListener('scroll', handleScroll);
      observer.disconnect();
    };
  }, [containerRef]);

  const virtualItems = useMemo(() => {
    if (containerHeight === 0 || itemCount === 0) return [];

    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      itemCount,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );

    const items: VirtualItem[] = [];
    for (let i = startIndex; i < endIndex; i++) {
      items.push({
        index: i,
        start: i * itemHeight,
        size: itemHeight,
      });
    }

    return items;
  }, [scrollTop, containerHeight, itemCount, itemHeight, overscan]);

  const totalSize = itemCount * itemHeight;

  return { virtualItems, totalSize };
}

// =============================================================================
// Main Component
// =============================================================================

export function MarkTimeline({
  marks,
  groupBy = 'day',
  density = 'comfortable',
  isLoading = false,
  error = null,
  onRetract,
  onSelect,
  selectedMarkId,
  height,
  className = '',
}: MarkTimelineProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  // Estimate item height based on density
  const estimatedItemHeight = useMemo(() => {
    switch (density) {
      case 'compact':
        return 40;
      case 'comfortable':
        return 72;
      case 'spacious':
        return 120;
      default:
        return 72;
    }
  }, [density]);

  // Group marks
  const groupedItems = useMemo(() => {
    if (groupBy === 'none') {
      return marks.map((mark) => ({ type: 'mark' as const, mark }));
    }

    const groups =
      groupBy === 'day' ? groupMarksByDay(marks) : groupMarksBySession(marks);

    const items: Array<
      | { type: 'day'; date: string; count: number }
      | { type: 'session'; sessionId: string; count: number }
      | { type: 'mark'; mark: Mark }
    > = [];

    for (const [key, groupMarks] of groups) {
      if (groupBy === 'day') {
        items.push({ type: 'day', date: key, count: groupMarks.length });
      } else {
        items.push({ type: 'session', sessionId: key, count: groupMarks.length });
      }
      for (const mark of groupMarks) {
        items.push({ type: 'mark', mark });
      }
    }

    return items;
  }, [marks, groupBy]);

  // Simple virtualization (disabled for now - can enable for large lists)
  // TODO: Re-enable virtualization when needed for performance
  const _shouldVirtualize = marks.length > 100;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { virtualItems: _virtualItems, totalSize: _totalSize } = useVirtualList(
    _shouldVirtualize ? groupedItems.length : 0,
    estimatedItemHeight,
    containerRef
  );

  // Handle mark click
  const handleMarkClick = useCallback(
    (mark: Mark) => {
      onSelect?.(mark);
    },
    [onSelect]
  );

  // Render states
  if (isLoading) {
    return <LoadingSkeleton count={5} />;
  }

  if (error) {
    return <ErrorState message={error} />;
  }

  if (marks.length === 0) {
    return <EmptyState />;
  }

  // Render items (non-virtualized for simplicity)
  const renderItems = () => {
    return groupedItems.map((item, index) => {
      if (item.type === 'day') {
        return (
          <DaySeparator key={`day-${item.date}`} date={item.date} count={item.count} />
        );
      }
      if (item.type === 'session') {
        return (
          <SessionSeparator
            key={`session-${item.sessionId}`}
            sessionId={item.sessionId}
            count={item.count}
          />
        );
      }
      return (
        <motion.div
          key={item.mark.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ delay: index * 0.02 }}
        >
          <MarkCard
            mark={item.mark}
            density={density}
            onRetract={onRetract}
            onClick={() => handleMarkClick(item.mark)}
            isSelected={selectedMarkId === item.mark.id}
          />
        </motion.div>
      );
    });
  };

  return (
    <div
      ref={containerRef}
      className={`overflow-y-auto ${className}`}
      style={{
        height: height || '100%',
        backgroundColor: LIVING_EARTH.soil,
      }}
      data-testid="mark-timeline"
      data-group-by={groupBy}
    >
      <AnimatePresence mode="popLayout">
        <div className="space-y-2 p-2">{renderItems()}</div>
      </AnimatePresence>
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export { DaySeparator, SessionSeparator, LoadingSkeleton, EmptyState, ErrorState };
export default MarkTimeline;
