/**
 * PipelineNode: Individual node in the pipeline canvas.
 *
 * Renders a node with input/output ports. Supports different node types
 * (agent, operation, input, output) with appropriate styling.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { forwardRef, type MouseEvent } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';

import { cn, getArchetypeColor } from '@/lib/utils';
import type { PipelineNodeData, Port } from '@/components/dnd';
import type { CitizenCardJSON } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface PipelineNodeProps {
  /** Node data */
  node: PipelineNodeData;

  /** Whether the node is selected */
  isSelected?: boolean;

  /** Called when node is clicked */
  onClick?: (e: MouseEvent<HTMLDivElement>) => void;

  /** Called when a port is clicked (for connection) */
  onPortClick?: (port: Port, isInput: boolean) => void;

  /** Additional class names */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export const PipelineNode = forwardRef<HTMLDivElement, PipelineNodeProps>(function PipelineNode(
  { node, isSelected = false, onClick, onPortClick, className },
  ref
) {
  // Make the node draggable within the canvas
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `pipeline-node-${node.id}`,
    data: {
      type: 'pipeline-node',
      id: node.id,
      sourceZone: 'canvas',
      payload: node,
    },
  });

  // Combine refs
  const setRefs = (element: HTMLDivElement | null) => {
    setNodeRef(element);
    if (typeof ref === 'function') ref(element);
    else if (ref) ref.current = element;
  };

  // Position style
  const style = {
    position: 'absolute' as const,
    left: node.position.x,
    top: node.position.y,
    transform: transform ? CSS.Translate.toString(transform) : undefined,
  };

  return (
    <div
      ref={setRefs}
      style={style}
      onClick={onClick}
      className={cn(
        'pipeline-node',
        'rounded-lg border-2 bg-town-surface shadow-lg',
        'min-w-[150px] transition-all duration-150',
        isSelected && 'border-town-highlight ring-2 ring-town-highlight/30',
        !isSelected && 'border-town-accent/50',
        isDragging && 'opacity-70 scale-105 z-50',
        className
      )}
      {...attributes}
      {...listeners}
    >
      {/* Header */}
      <NodeHeader node={node} />

      {/* Ports */}
      <div className="flex justify-between px-1 py-2">
        {/* Input ports */}
        <div className="flex flex-col gap-1">
          {node.ports.inputs.map((port) => (
            <PortHandle
              key={port.id}
              port={port}
              isInput
              onClick={() => onPortClick?.(port, true)}
            />
          ))}
        </div>

        {/* Output ports */}
        <div className="flex flex-col gap-1">
          {node.ports.outputs.map((port) => (
            <PortHandle
              key={port.id}
              port={port}
              isInput={false}
              onClick={() => onPortClick?.(port, false)}
            />
          ))}
        </div>
      </div>
    </div>
  );
});

// =============================================================================
// Sub-components
// =============================================================================

interface NodeHeaderProps {
  node: PipelineNodeData;
}

function NodeHeader({ node }: NodeHeaderProps) {
  // Render based on node type
  switch (node.type) {
    case 'agent': {
      const citizen = node.data as CitizenCardJSON;
      const archetypeColor = getArchetypeColor(citizen.archetype);
      return (
        <div className="px-3 py-2 border-b border-town-accent/30">
          <div className="flex items-center gap-2">
            <span className="text-lg">{getArchetypeIcon(citizen.archetype)}</span>
            <div className="min-w-0">
              <div className="font-semibold truncate text-sm">{citizen.name}</div>
              <div className={cn('text-xs', archetypeColor)}>{citizen.archetype}</div>
            </div>
          </div>
        </div>
      );
    }

    case 'operation':
      return (
        <div className="px-3 py-2 border-b border-town-accent/30 bg-purple-500/10">
          <div className="flex items-center gap-2">
            <span className="text-lg">⚙️</span>
            <span className="font-medium text-sm text-purple-300">Operation</span>
          </div>
        </div>
      );

    case 'input':
      return (
        <div className="px-3 py-2 border-b border-town-accent/30 bg-green-500/10">
          <div className="flex items-center gap-2">
            <span className="text-lg">📥</span>
            <span className="font-medium text-sm text-green-300">Input</span>
          </div>
        </div>
      );

    case 'output':
      return (
        <div className="px-3 py-2 border-b border-town-accent/30 bg-blue-500/10">
          <div className="flex items-center gap-2">
            <span className="text-lg">📤</span>
            <span className="font-medium text-sm text-blue-300">Output</span>
          </div>
        </div>
      );

    default:
      return (
        <div className="px-3 py-2 border-b border-town-accent/30">
          <span className="font-medium text-sm text-gray-400">Node</span>
        </div>
      );
  }
}

interface PortHandleProps {
  port: Port;
  isInput: boolean;
  onClick?: () => void;
}

function PortHandle({ port, isInput, onClick }: PortHandleProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors',
        'hover:bg-town-accent/20',
        isInput ? 'flex-row' : 'flex-row-reverse'
      )}
      title={`${port.label} (${port.type})`}
    >
      {/* Port dot */}
      <div
        className={cn(
          'w-2.5 h-2.5 rounded-full border-2',
          port.connected ? 'bg-town-highlight border-town-highlight' : 'bg-transparent border-town-accent',
          isInput ? '-ml-3' : '-mr-3'
        )}
      />
      <span className="text-gray-400">{port.label}</span>
    </button>
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

export default PipelineNode;
