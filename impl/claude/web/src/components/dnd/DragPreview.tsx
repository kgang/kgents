/**
 * DragPreview: Visual feedback during drag operations.
 *
 * Renders a preview of the item being dragged. The preview adapts to
 * the type of item (agent, pipeline node, etc.) and provides visual
 * feedback about the drag state.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { cn, getArchetypeColor } from '@/lib/utils';
import type { DragData, AgentDragData, PipelineNodeDragData } from './types';
import { isAgentDragData, isPipelineNodeDragData } from './types';

// =============================================================================
// Types
// =============================================================================

export interface DragPreviewProps {
  /** Data of the item being dragged */
  data: DragData;

  /** Additional class names */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export function DragPreview({ data, className }: DragPreviewProps) {
  // Render based on drag item type
  if (isAgentDragData(data)) {
    return <AgentPreview data={data} className={className} />;
  }

  if (isPipelineNodeDragData(data)) {
    return <PipelineNodePreview data={data} className={className} />;
  }

  // Generic preview fallback
  return (
    <div
      className={cn(
        'px-3 py-2 rounded-lg bg-town-surface border border-town-accent/50',
        'shadow-lg opacity-90 pointer-events-none',
        className
      )}
    >
      <span className="text-sm text-gray-300">Dragging item...</span>
    </div>
  );
}

// =============================================================================
// Specialized Previews
// =============================================================================

interface AgentPreviewProps {
  data: AgentDragData;
  className?: string;
}

function AgentPreview({ data, className }: AgentPreviewProps) {
  const citizen = data.payload;
  const archetypeColor = getArchetypeColor(citizen.archetype);

  return (
    <div
      className={cn(
        'px-4 py-3 rounded-lg bg-town-surface border-2',
        'shadow-xl opacity-95 pointer-events-none',
        'min-w-[180px] max-w-[250px]',
        archetypeColor.includes('text-') ? archetypeColor.replace('text-', 'border-') : 'border-town-highlight',
        className
      )}
    >
      <div className="flex items-center gap-3">
        {/* Archetype icon */}
        <div className="text-2xl">
          {getArchetypeIcon(citizen.archetype)}
        </div>

        {/* Name and archetype */}
        <div className="min-w-0">
          <div className="font-semibold truncate">{citizen.name}</div>
          <div className={cn('text-xs', archetypeColor)}>{citizen.archetype}</div>
        </div>
      </div>

      {/* Dragging indicator */}
      <div className="mt-2 flex items-center gap-1.5 text-xs text-gray-400">
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path d="M7 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4z" />
        </svg>
        <span>Drop to add to pipeline</span>
      </div>
    </div>
  );
}

interface PipelineNodePreviewProps {
  data: PipelineNodeDragData;
  className?: string;
}

function PipelineNodePreview({ data, className }: PipelineNodePreviewProps) {
  const node = data.payload;

  return (
    <div
      className={cn(
        'px-4 py-3 rounded-lg bg-town-surface border border-town-accent/50',
        'shadow-xl opacity-95 pointer-events-none',
        'min-w-[150px]',
        className
      )}
    >
      <div className="flex items-center gap-2">
        {/* Node type icon */}
        <div className="text-lg">{getNodeTypeIcon(node.type)}</div>

        {/* Node info */}
        <div className="min-w-0">
          <div className="font-medium text-sm capitalize">{node.type}</div>
          <div className="text-xs text-gray-400 truncate">{node.id}</div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

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

function getNodeTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    agent: '🤖',
    operation: '⚙️',
    input: '📥',
    output: '📤',
  };
  return icons[type] || '📦';
}

export default DragPreview;
