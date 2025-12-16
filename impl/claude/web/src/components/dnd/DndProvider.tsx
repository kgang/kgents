/**
 * DndProvider: Wraps app with drag-and-drop context.
 *
 * Provides the DnD context and collision detection strategy for the entire
 * application. Use this at the app root or around any region that needs
 * drag-and-drop functionality.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { useState, useCallback, type ReactNode } from 'react';
import {
  DndContext,
  DragOverlay,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
  type DragOverEvent,
} from '@dnd-kit/core';
import { sortableKeyboardCoordinates } from '@dnd-kit/sortable';

import type { DragData } from './types';
import { DragPreview } from './DragPreview';

// =============================================================================
// Types
// =============================================================================

export interface DndProviderProps {
  /** Child components */
  children: ReactNode;

  /** Callback when drag starts */
  onDragStart?: (data: DragData) => void;

  /** Callback when dragging over a zone */
  onDragOver?: (data: DragData, zoneId: string) => void;

  /** Callback when drag ends (drop or cancel) */
  onDragEnd?: (data: DragData | null, zoneId: string | null) => void;

  /** Custom collision detection strategy */
  collisionDetection?: typeof closestCenter;
}

// =============================================================================
// Component
// =============================================================================

export function DndProvider({
  children,
  onDragStart,
  onDragOver,
  onDragEnd,
  collisionDetection = closestCenter,
}: DndProviderProps) {
  // Track currently dragged item
  const [activeData, setActiveData] = useState<DragData | null>(null);

  // Configure sensors for mouse/touch and keyboard
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        // Require 8px movement to start drag (prevents accidental drags)
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Handle drag start
  const handleDragStart = useCallback(
    (event: DragStartEvent) => {
      const data = event.active.data.current as DragData | undefined;
      if (data) {
        setActiveData(data);
        onDragStart?.(data);
      }
    },
    [onDragStart]
  );

  // Handle drag over
  const handleDragOver = useCallback(
    (event: DragOverEvent) => {
      if (!activeData || !event.over) return;
      onDragOver?.(activeData, String(event.over.id));
    },
    [activeData, onDragOver]
  );

  // Handle drag end
  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const zoneId = event.over ? String(event.over.id) : null;
      onDragEnd?.(activeData, zoneId);
      setActiveData(null);
    },
    [activeData, onDragEnd]
  );

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={collisionDetection}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
    >
      {children}

      {/* Drag preview overlay */}
      <DragOverlay dropAnimation={null}>
        {activeData && <DragPreview data={activeData} />}
      </DragOverlay>
    </DndContext>
  );
}

export default DndProvider;
