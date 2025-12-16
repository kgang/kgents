/**
 * DraggableAgent: Agent card with drag functionality.
 *
 * Wraps a citizen card to make it draggable. Supports multiple drag handle
 * modes: the entire card, just an icon, or a dedicated grip handle.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { forwardRef, type ReactNode } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';

import { cn, getArchetypeColor, getPhaseColor } from '@/lib/utils';
import { ElasticCard } from '@/components/elastic';
import type { CitizenCardJSON } from '@/reactive/types';
import type { AgentDragData } from './types';

// =============================================================================
// Types
// =============================================================================

export type DragHandleMode = 'card' | 'icon' | 'grip';

export interface DraggableAgentProps {
  /** Citizen data to display and drag */
  citizen: CitizenCardJSON;

  /** Which part acts as the drag handle */
  dragHandle?: DragHandleMode;

  /** Source zone identifier (for drop validation) */
  sourceZone?: string;

  /** Whether the agent is currently selected */
  isSelected?: boolean;

  /** Click handler (when not dragging) */
  onClick?: (citizen: CitizenCardJSON) => void;

  /** Custom content to render inside the card */
  children?: ReactNode;

  /** Additional class names */
  className?: string;

  /** Disable dragging */
  disabled?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export const DraggableAgent = forwardRef<HTMLDivElement, DraggableAgentProps>(function DraggableAgent(
  {
    citizen,
    dragHandle = 'grip',
    sourceZone = 'mesa',
    isSelected = false,
    onClick,
    children,
    className,
    disabled = false,
  },
  ref
) {
  // Set up draggable
  const dragData: AgentDragData = {
    type: 'agent',
    id: citizen.citizen_id,
    sourceZone,
    payload: citizen,
  };

  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: citizen.citizen_id,
    data: dragData,
    disabled,
  });

  // Compute transform style
  const style = transform
    ? {
        transform: CSS.Translate.toString(transform),
      }
    : undefined;

  // Determine what gets the drag listeners
  const cardListeners = dragHandle === 'card' ? listeners : undefined;
  const cardAttributes = dragHandle === 'card' ? attributes : undefined;

  const archetypeColor = getArchetypeColor(citizen.archetype);
  const phaseColor = getPhaseColor(citizen.phase);

  return (
    <ElasticCard
      ref={(node) => {
        setNodeRef(node);
        if (typeof ref === 'function') ref(node);
        else if (ref) ref.current = node;
      }}
      draggable={!disabled}
      isSelected={isSelected}
      onClick={onClick ? () => onClick(citizen) : undefined}
      className={cn(
        'transition-all duration-150',
        isDragging && 'opacity-50 scale-95',
        disabled && 'opacity-60 cursor-not-allowed',
        className
      )}
      style={style}
      {...cardAttributes}
      {...cardListeners}
    >
      <div className="flex items-center gap-3">
        {/* Grip handle */}
        {dragHandle === 'grip' && !disabled && (
          <div
            className="flex-shrink-0 cursor-grab active:cursor-grabbing text-gray-500 hover:text-gray-300"
            {...listeners}
            {...attributes}
          >
            <GripIcon />
          </div>
        )}

        {/* Archetype icon (draggable if mode is 'icon') */}
        <div
          className={cn(
            'flex-shrink-0 text-2xl',
            dragHandle === 'icon' && !disabled && 'cursor-grab active:cursor-grabbing'
          )}
          {...(dragHandle === 'icon' ? { ...listeners, ...attributes } : {})}
        >
          {getArchetypeIcon(citizen.archetype)}
        </div>

        {/* Name and info */}
        <div className="flex-1 min-w-0">
          <div className="font-semibold truncate">{citizen.name}</div>
          <div className="flex items-center gap-2 text-xs">
            <span className={archetypeColor}>{citizen.archetype}</span>
            <span className="text-gray-500">·</span>
            <span className={phaseColor}>{citizen.phase}</span>
          </div>
        </div>

        {/* Capability indicator */}
        <div className="flex-shrink-0">
          <div
            className="w-8 h-8 rounded-full border-2 border-town-accent/30 flex items-center justify-center text-xs font-mono"
            title={`Capability: ${(citizen.capability * 100).toFixed(0)}%`}
          >
            {Math.round(citizen.capability * 100)}
          </div>
        </div>
      </div>

      {/* Custom content */}
      {children}
    </ElasticCard>
  );
});

// =============================================================================
// Icons
// =============================================================================

function GripIcon() {
  return (
    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
      <path d="M7 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" />
    </svg>
  );
}

function getArchetypeIcon(archetype: string): string {
  const icons: Record<string, string> = {
    Scout: '🔭',
    Sage: '📚',
    Spark: '✨',
    Steady: '🏔️',
    Sync: '🔗',
  };
  return icons[archetype] || '👤';
}

export default DraggableAgent;
