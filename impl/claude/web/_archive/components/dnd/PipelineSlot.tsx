/**
 * PipelineSlot: Drop zone for pipeline composition.
 *
 * A designated area where agents can be dropped to add them to a pipeline.
 * Provides visual feedback when items are dragged over and validates
 * accepted item types.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { type ReactNode } from 'react';
import { useDroppable } from '@dnd-kit/core';

import { cn } from '@/lib/utils';
import type { DragItemType, DragData } from './types';

// =============================================================================
// Types
// =============================================================================

export interface PipelineSlotProps {
  /** Unique identifier for this slot */
  slotId: string;

  /** Types of items this slot accepts */
  accepts: DragItemType[];

  /** Called when a valid item is dropped */
  onDrop?: (data: DragData) => void;

  /** Position index in the pipeline (for ordering) */
  index?: number;

  /** Whether this is an insertion point between nodes */
  isInsertionPoint?: boolean;

  /** Content to show when slot is empty */
  placeholder?: string;

  /** Content to show when slot is filled */
  children?: ReactNode;

  /** Additional class names */
  className?: string;

  /** Whether the slot is disabled */
  disabled?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export function PipelineSlot({
  slotId,
  accepts,
  onDrop,
  index,
  isInsertionPoint = false,
  placeholder = 'Drop agent here',
  children,
  className,
  disabled = false,
}: PipelineSlotProps) {
  const { isOver, setNodeRef, active } = useDroppable({
    id: slotId,
    data: { accepts, index, onDrop },
    disabled,
  });

  // Check if the currently dragged item is acceptable
  const activeData = active?.data.current as DragData | undefined;
  const canAccept = activeData && accepts.includes(activeData.type);
  const isValidDrop = isOver && canAccept;

  // Render insertion point (thin line between nodes)
  if (isInsertionPoint) {
    return (
      <div
        ref={setNodeRef}
        className={cn(
          'h-2 w-full transition-all duration-150',
          'flex items-center justify-center',
          canAccept && !isOver && 'bg-town-accent/20',
          isValidDrop && 'h-8 bg-town-highlight/30 border-2 border-dashed border-town-highlight',
          className
        )}
      >
        {isValidDrop && (
          <span className="text-xs text-town-highlight">Insert here</span>
        )}
      </div>
    );
  }

  // Render standard slot
  return (
    <div
      ref={setNodeRef}
      className={cn(
        // Base styles
        'rounded-lg border-2 border-dashed transition-all duration-200',
        'min-h-[100px] flex items-center justify-center',

        // Default state
        !isOver && !canAccept && 'border-town-accent/30 bg-town-surface/20',

        // Dragging compatible item
        canAccept && !isOver && 'border-town-accent/50 bg-town-accent/10',

        // Hovering with valid item
        isValidDrop && 'border-town-highlight bg-town-highlight/10 scale-[1.02]',

        // Hovering with invalid item
        isOver && !canAccept && 'border-red-500/50 bg-red-500/10',

        // Disabled state
        disabled && 'opacity-50 cursor-not-allowed',

        // Custom classes
        className
      )}
      data-slot-id={slotId}
      data-accepts={accepts.join(',')}
      data-index={index}
    >
      {children || (
        <div className="text-center p-4">
          {isValidDrop ? (
            <div className="text-town-highlight">
              <DropIcon className="w-8 h-8 mx-auto mb-2" />
              <span className="text-sm font-medium">Release to add</span>
            </div>
          ) : isOver && !canAccept ? (
            <div className="text-red-400">
              <BlockIcon className="w-8 h-8 mx-auto mb-2" />
              <span className="text-sm">Cannot drop here</span>
            </div>
          ) : (
            <div className="text-gray-500">
              <PlusIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <span className="text-sm">{placeholder}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Icons
// =============================================================================

function PlusIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  );
}

function DropIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M19 14l-7 7m0 0l-7-7m7 7V3"
      />
    </svg>
  );
}

function BlockIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
      />
    </svg>
  );
}

export default PipelineSlot;
