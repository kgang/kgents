/**
 * NodeDetailPanel: Slide-in panel showing node details and aspects.
 *
 * CLI v7 Phase 5: Collaborative Canvas.
 *
 * Voice Anchor:
 * "Tasteful > feature-complete"
 *
 * Shows:
 * - Node path and description
 * - Available aspects (manifest, witness, refine, etc.)
 * - Context explanation (teaching mode)
 * - Recent invocations (if any)
 *
 * Design:
 * - Slides in from right edge
 * - Closes on outside click or escape
 * - Information-dense but not overwhelming
 *
 * @see protocols/agentese/aspects.py - Aspect taxonomy
 */

import { useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Play, Book, Info, ChevronRight } from 'lucide-react';
import type { CanvasNode } from './AgentCanvas';

// =============================================================================
// Types
// =============================================================================

export interface NodeDetailPanelProps {
  /** The selected node (null = panel closed) */
  node: CanvasNode | null;
  /** Close callback */
  onClose: () => void;
  /** Invoke an aspect callback */
  onInvoke?: (path: string, aspect: string) => void;
  /** Whether teaching mode is enabled */
  teachingMode?: boolean;
  /** Extra CSS classes */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

/** Common aspects available on most nodes */
const COMMON_ASPECTS = ['manifest', 'witness', 'refine', 'sip', 'tithe'] as const;

/** Aspect descriptions for teaching mode */
const ASPECT_DESCRIPTIONS: Record<string, string> = {
  manifest: 'Create or reveal the essential nature',
  witness: 'Observe and record state changes',
  refine: 'Improve or evolve toward ideal form',
  sip: 'Sample a small portion (preview)',
  tithe: 'Contribute to the collective (Accursed Share)',
  lens: 'Apply a filter or perspective',
  define: 'Establish formal boundaries and properties',
};

/** Context explanations for AGENTESE five contexts */
const CONTEXT_EXPLANATIONS: Record<string, { title: string; description: string; color: string }> = {
  world: {
    title: 'The External',
    description: 'Entities, environments, and tools that exist outside the agent. This is where the agent interacts with reality.',
    color: 'blue',
  },
  self: {
    title: 'The Internal',
    description: 'Memory, capability, and state within the agent. This is where introspection and self-awareness live.',
    color: 'violet',
  },
  concept: {
    title: 'The Abstract',
    description: 'Platonic forms, definitions, and logical structures. Ideas that exist independently of instantiation.',
    color: 'emerald',
  },
  void: {
    title: 'The Accursed Share',
    description: 'Entropy, serendipity, and gratitude. The part that must be spent without return. Embrace randomness.',
    color: 'gray',
  },
  time: {
    title: 'The Temporal',
    description: 'Traces, forecasts, and schedules. How the past informs the present and shapes the future.',
    color: 'amber',
  },
};

// =============================================================================
// Helper Components
// =============================================================================

interface AspectButtonProps {
  aspect: string;
  description?: string;
  onInvoke: () => void;
  teachingMode: boolean;
}

function AspectButton({ aspect, description, onInvoke, teachingMode }: AspectButtonProps) {
  return (
    <button
      onClick={onInvoke}
      className="group flex items-start gap-2 w-full px-3 py-2 rounded-lg bg-gray-800/50 hover:bg-gray-800 border border-gray-700/50 hover:border-gray-600 transition-all text-left"
    >
      <Play className="w-3 h-3 mt-1 text-gray-500 group-hover:text-green-400 transition-colors" />
      <div className="flex-1 min-w-0">
        <div className="text-sm font-medium text-gray-200 group-hover:text-white">
          {aspect}
        </div>
        {teachingMode && description && (
          <div className="text-[10px] text-gray-500 mt-0.5 line-clamp-2">
            {description}
          </div>
        )}
      </div>
      <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors opacity-0 group-hover:opacity-100" />
    </button>
  );
}

interface TeachingCalloutProps {
  context: string;
  children?: React.ReactNode;
}

function TeachingCallout({ context, children }: TeachingCalloutProps) {
  const info = CONTEXT_EXPLANATIONS[context];
  if (!info) return null;

  const colorClasses: Record<string, string> = {
    blue: 'border-blue-500/30 bg-blue-500/5',
    violet: 'border-violet-500/30 bg-violet-500/5',
    emerald: 'border-emerald-500/30 bg-emerald-500/5',
    gray: 'border-gray-500/30 bg-gray-500/5',
    amber: 'border-amber-500/30 bg-amber-500/5',
  };

  return (
    <div
      className={`rounded-lg border p-3 ${colorClasses[info.color] || colorClasses.gray}`}
    >
      <div className="flex items-center gap-1.5 mb-1">
        <Book className="w-3 h-3 text-gray-400" />
        <span className="text-xs font-medium text-gray-300">{info.title}</span>
      </div>
      <p className="text-[11px] text-gray-400 leading-relaxed">
        {info.description}
      </p>
      {children && (
        <div className="mt-2 pt-2 border-t border-gray-700/50 text-[11px] text-gray-500">
          {children}
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function NodeDetailPanel({
  node,
  onClose,
  onInvoke,
  teachingMode = false,
  className = '',
}: NodeDetailPanelProps) {
  // Close on Escape key
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Handle aspect invocation
  const handleInvoke = useCallback(
    (aspect: string) => {
      if (node && onInvoke) {
        onInvoke(node.path, aspect);
      }
    },
    [node, onInvoke]
  );

  return (
    <AnimatePresence>
      {node && (
        <>
          {/* Backdrop (click to close) */}
          <motion.div
            className="fixed inset-0 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Panel */}
          <motion.aside
            className={`
              fixed right-0 top-0 bottom-0 z-50
              w-80 bg-gray-900 border-l border-gray-800
              flex flex-col shadow-xl shadow-black/50
              ${className}
            `}
            initial={{ x: '100%', opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: '100%', opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          >
            {/* Header */}
            <div className="flex-shrink-0 flex items-start justify-between p-4 border-b border-gray-800">
              <div className="min-w-0 flex-1">
                <h2 className="font-medium text-white truncate">{node.label}</h2>
                <code className="text-xs text-blue-400 font-mono">{node.path}</code>
              </div>
              <button
                onClick={onClose}
                className="ml-2 p-1 rounded hover:bg-gray-800 text-gray-500 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* Description */}
              {node.description && (
                <p className="text-sm text-gray-400">{node.description}</p>
              )}

              {/* Context badge */}
              <div className="flex items-center gap-2">
                <span
                  className={`
                    px-2 py-0.5 rounded-full text-[10px] font-medium uppercase
                    ${node.context === 'world' ? 'bg-blue-500/20 text-blue-400' : ''}
                    ${node.context === 'self' ? 'bg-violet-500/20 text-violet-400' : ''}
                    ${node.context === 'concept' ? 'bg-emerald-500/20 text-emerald-400' : ''}
                    ${node.context === 'void' ? 'bg-gray-500/20 text-gray-400' : ''}
                    ${node.context === 'time' ? 'bg-amber-500/20 text-amber-400' : ''}
                  `}
                >
                  {node.context}
                </span>
                <span className="text-[10px] text-gray-600">
                  depth {node.path.split('.').length}
                </span>
              </div>

              {/* Aspects section */}
              <div>
                <h3 className="text-xs font-medium text-gray-500 uppercase mb-2 flex items-center gap-1">
                  <Play className="w-3 h-3" />
                  Aspects
                </h3>
                <div className="space-y-1.5">
                  {COMMON_ASPECTS.map((aspect) => (
                    <AspectButton
                      key={aspect}
                      aspect={aspect}
                      description={ASPECT_DESCRIPTIONS[aspect]}
                      onInvoke={() => handleInvoke(aspect)}
                      teachingMode={teachingMode}
                    />
                  ))}
                </div>
              </div>

              {/* Teaching mode callout */}
              {teachingMode && (
                <div>
                  <h3 className="text-xs font-medium text-gray-500 uppercase mb-2 flex items-center gap-1">
                    <Info className="w-3 h-3" />
                    About This Context
                  </h3>
                  <TeachingCallout context={node.context}>
                    <p>
                      This node is at path <code className="text-blue-400">{node.path}</code>.
                      Invoke an aspect above to interact with it.
                    </p>
                  </TeachingCallout>
                </div>
              )}

              {/* Node hierarchy */}
              {node.parent && (
                <div>
                  <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">
                    Hierarchy
                  </h3>
                  <div className="text-xs text-gray-400 font-mono">
                    <span className="text-gray-600">{node.parent}</span>
                    <span className="text-gray-700 mx-1">→</span>
                    <span className="text-white">{node.label}</span>
                  </div>
                </div>
              )}

              {/* Children (if expanded) */}
              {node.children && node.children.length > 0 && (
                <div>
                  <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">
                    Children ({node.children.length})
                  </h3>
                  <div className="flex flex-wrap gap-1">
                    {node.children.slice(0, 8).map((childId) => (
                      <span
                        key={childId}
                        className="px-1.5 py-0.5 rounded bg-gray-800 text-[10px] text-gray-400 font-mono"
                      >
                        {childId.split('.').pop()}
                      </span>
                    ))}
                    {node.children.length > 8 && (
                      <span className="px-1.5 py-0.5 text-[10px] text-gray-600">
                        +{node.children.length - 8} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex-shrink-0 p-4 border-t border-gray-800 bg-gray-900/50">
              <p className="text-[10px] text-gray-600 text-center">
                Press <kbd className="px-1 py-0.5 bg-gray-800 rounded text-gray-400">Esc</kbd> to close
              </p>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default NodeDetailPanel;
