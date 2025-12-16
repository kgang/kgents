/**
 * VirtualizedCitizenList: Efficient list rendering for large citizen counts.
 *
 * Uses @tanstack/react-virtual to only render visible items, enabling
 * smooth scrolling with 100+ citizens (memory and render performance).
 *
 * Performance targets:
 * - Memory: <50MB for 100 citizens (vs ~80MB without virtualization)
 * - Render: <16ms per frame during scroll
 */

import { useRef, memo } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { CitizenCard } from '@/widgets/cards/CitizenCard';
import type { CitizenCardJSON } from '@/reactive/types';

export interface VirtualizedCitizenListProps {
  citizens: CitizenCardJSON[];
  selectedCitizenId?: string | null;
  onSelectCitizen?: (id: string) => void;
  className?: string;
  /** Estimated row height in pixels */
  estimateSize?: number;
  /** Number of items to render outside viewport */
  overscan?: number;
}

export const VirtualizedCitizenList = memo(function VirtualizedCitizenList({
  citizens,
  selectedCitizenId,
  onSelectCitizen,
  className,
  estimateSize = 140,
  overscan = 5,
}: VirtualizedCitizenListProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: citizens.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimateSize,
    overscan,
  });

  const virtualItems = virtualizer.getVirtualItems();

  // Show count indicator for large lists
  const showCount = citizens.length > 20;

  return (
    <div className={className}>
      {showCount && (
        <div className="text-xs text-gray-500 px-2 py-1 border-b border-town-accent/30">
          {citizens.length} citizens
          {virtualItems.length < citizens.length && (
            <span className="text-gray-600"> (showing {virtualItems.length})</span>
          )}
        </div>
      )}

      <div
        ref={parentRef}
        className="h-full overflow-auto"
        style={{ contain: 'strict' }}
      >
        <div
          style={{
            height: `${virtualizer.getTotalSize()}px`,
            width: '100%',
            position: 'relative',
          }}
        >
          {virtualItems.map((virtualItem) => {
            const citizen = citizens[virtualItem.index];
            return (
              <div
                key={virtualItem.key}
                data-index={virtualItem.index}
                ref={virtualizer.measureElement}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  transform: `translateY(${virtualItem.start}px)`,
                }}
              >
                <div className="p-2">
                  <CitizenCard
                    {...citizen}
                    isSelected={citizen.citizen_id === selectedCitizenId}
                    onSelect={onSelectCitizen}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
});

export default VirtualizedCitizenList;
