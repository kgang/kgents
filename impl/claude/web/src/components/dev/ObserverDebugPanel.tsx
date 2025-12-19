/**
 * ObserverDebugPanel - Developer Tool for Observer Consistency Auditing
 *
 * Phase 8 of AGENTESE Node Overhaul: Observer Consistency Audit
 *
 * Shows what the current observer sees differently than other archetypes:
 * - Affordances available to current vs other archetypes
 * - Eigenvector influence on soul (when in developer mode)
 * - Visibility differences across archetypes
 *
 * Toggle: Ctrl+Shift+O (dev mode only)
 *
 * The observer gradation principle:
 *   Observer (minimal) → Umwelt (full)
 *   Different observers see different realities.
 *
 * @see plans/agentese-node-overhaul-strategy.md (Phase 8)
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Eye,
  Shield,
  User,
  Lock,
  Unlock,
  Code,
  Bug,
  ChevronDown,
  ChevronUp,
  X,
} from 'lucide-react';
import { useShell } from '../../shell/ShellProvider';
import type { ObserverArchetype, Capability } from '../../shell/types';
import { GLASS_EFFECT, Z_INDEX_LAYERS } from '../elastic';

// =============================================================================
// Types
// =============================================================================

interface ObserverDelta {
  archetype: ObserverArchetype;
  extraAffordances: string[]; // What this archetype has that current doesn't
  missingAffordances: string[]; // What current has that this doesn't
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Known archetype gradations by node.
 *
 * These define what each node SHOULD vary by observer.
 * Phase 8 Deliverable: Document expected gradations.
 */
const NODE_GRADATIONS: Record<
  string,
  {
    description: string;
    archetypes: Record<string, string[]>;
  }
> = {
  'self.soul': {
    description: 'Soul eigenvector influence varies by archetype',
    archetypes: {
      developer: ['introspection', 'witness', 'eigenvector.inspect', 'eigenvector.adjust'],
      architect: ['introspection', 'witness', 'eigenvector.inspect'],
      operator: ['witness', 'health'],
      reviewer: ['witness'],
      newcomer: ['witness'],
      guest: [],
    },
  },
  'world.park': {
    description: 'Park visibility: admin sees all, tourist sees subset',
    archetypes: {
      developer: ['manifest', 'session.list', 'session.detail', 'director.ops', 'mask.manage'],
      operator: ['manifest', 'session.list', 'session.detail', 'director.ops'],
      architect: ['manifest', 'session.list', 'session.detail'],
      newcomer: ['manifest', 'session.list'],
      guest: ['manifest'],
    },
  },
  'concept.gardener': {
    description: 'Gardener polynomial visibility for developers',
    archetypes: {
      developer: [
        'manifest',
        'garden.manifest',
        'polynomial.inspect',
        'polynomial.step',
        'session.trace',
      ],
      architect: ['manifest', 'garden.manifest', 'polynomial.inspect'],
      operator: ['manifest', 'garden.manifest'],
      newcomer: ['manifest'],
      guest: [],
    },
  },
  'world.forge': {
    description: 'Forge artifact visibility varies by role',
    archetypes: {
      developer: [
        'manifest',
        'workshop.*',
        'artisan.*',
        'exhibition.*',
        'gallery.*',
        'tokens.*',
        'festival.*',
      ],
      curator: ['manifest', 'workshop.create', 'workshop.end', 'exhibition.*', 'gallery.add'],
      artisan: ['manifest', 'workshop.join', 'contribute', 'festival.enter'],
      spectator: ['manifest', 'workshop.list', 'exhibition.view', 'gallery.list', 'bid.submit'],
      guest: ['manifest', 'gallery.list'],
    },
  },
  'self.memory': {
    description: 'Memory crystal access varies by capability',
    archetypes: {
      developer: ['manifest', 'crystal.*', 'cartography.*', 'stigmergy.*'],
      architect: ['manifest', 'crystal.list', 'cartography.manifest'],
      operator: ['manifest', 'crystal.list'],
      newcomer: ['manifest'],
      guest: [],
    },
  },
};

const ALL_ARCHETYPES: ObserverArchetype[] = [
  'developer',
  'architect',
  'operator',
  'reviewer',
  'newcomer',
  'guest',
  'technical',
  'casual',
  'security',
  'creative',
  'strategic',
  'tactical',
  'reflective',
];

// =============================================================================
// Subcomponents
// =============================================================================

/** Single node gradation card */
function NodeGradationCard({
  nodePath,
  gradation,
  currentArchetype,
  isExpanded,
  onToggle,
}: {
  nodePath: string;
  gradation: { description: string; archetypes: Record<string, string[]> };
  currentArchetype: ObserverArchetype;
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const currentAffordances = gradation.archetypes[currentArchetype] || [];
  const allAffordances = new Set(Object.values(gradation.archetypes).flat());
  const hasAccess = currentAffordances.length > 0;
  const hasFullAccess = currentAffordances.length === allAffordances.size;

  return (
    <div className="border border-gray-700/50 rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={onToggle}
        className={`
          w-full flex items-center justify-between px-3 py-2
          hover:bg-gray-700/30 transition-colors
          ${hasFullAccess ? 'bg-green-900/20' : hasAccess ? 'bg-amber-900/20' : 'bg-red-900/20'}
        `}
      >
        <div className="flex items-center gap-2">
          {hasFullAccess ? (
            <Unlock className="w-4 h-4 text-green-400" />
          ) : hasAccess ? (
            <Shield className="w-4 h-4 text-amber-400" />
          ) : (
            <Lock className="w-4 h-4 text-red-400" />
          )}
          <span className="font-mono text-sm text-cyan-400">{nodePath}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">
            {currentAffordances.length}/{allAffordances.size}
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          )}
        </div>
      </button>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-3 py-2 border-t border-gray-700/50 space-y-2">
              <p className="text-xs text-gray-400">{gradation.description}</p>

              {/* Current archetype affordances */}
              <div>
                <label className="text-xs text-gray-500 block mb-1">
                  Your affordances ({currentArchetype}):
                </label>
                <div className="flex flex-wrap gap-1">
                  {currentAffordances.length > 0 ? (
                    currentAffordances.map((aff) => (
                      <span
                        key={aff}
                        className="text-xs px-1.5 py-0.5 rounded bg-green-900/40 text-green-400 font-mono"
                      >
                        {aff}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-red-400">No access</span>
                  )}
                </div>
              </div>

              {/* What you're missing */}
              {currentAffordances.length < allAffordances.size && (
                <div>
                  <label className="text-xs text-gray-500 block mb-1">
                    Requires higher privilege:
                  </label>
                  <div className="flex flex-wrap gap-1">
                    {Array.from(allAffordances)
                      .filter((aff) => !currentAffordances.includes(aff))
                      .map((aff) => (
                        <span
                          key={aff}
                          className="text-xs px-1.5 py-0.5 rounded bg-red-900/30 text-red-400/70 font-mono"
                        >
                          {aff}
                        </span>
                      ))}
                  </div>
                </div>
              )}

              {/* Archetype comparison */}
              <div>
                <label className="text-xs text-gray-500 block mb-1">By archetype:</label>
                <div className="grid grid-cols-2 gap-1 text-xs">
                  {Object.entries(gradation.archetypes).map(([arch, affs]) => (
                    <div
                      key={arch}
                      className={`
                        flex items-center justify-between px-2 py-0.5 rounded
                        ${arch === currentArchetype ? 'bg-cyan-900/40 text-cyan-400' : 'text-gray-400'}
                      `}
                    >
                      <span>{arch}</span>
                      <span className="font-mono">{affs.length}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/** Observer comparison widget */
function ObserverComparison({
  currentArchetype,
  capabilities,
}: {
  currentArchetype: ObserverArchetype;
  capabilities: Set<Capability>;
}) {
  const capArray = Array.from(capabilities);

  // Calculate what each archetype would see differently
  const deltas: ObserverDelta[] = ALL_ARCHETYPES.filter((arch) => arch !== currentArchetype)
    .slice(0, 5) // Show top 5 most different
    .map((arch) => {
      // This is a simplified comparison - in reality we'd query each node
      const extra: string[] = [];
      const missing: string[] = [];

      Object.entries(NODE_GRADATIONS).forEach(([, gradation]) => {
        const currentAffs = gradation.archetypes[currentArchetype] || [];
        const otherAffs = gradation.archetypes[arch] || [];

        otherAffs.forEach((aff) => {
          if (!currentAffs.includes(aff)) extra.push(aff);
        });
        currentAffs.forEach((aff) => {
          if (!otherAffs.includes(aff)) missing.push(aff);
        });
      });

      return { archetype: arch, extraAffordances: extra, missingAffordances: missing };
    })
    .sort(
      (a, b) =>
        b.extraAffordances.length +
        b.missingAffordances.length -
        (a.extraAffordances.length + a.missingAffordances.length)
    );

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-sm text-gray-300">
        <User className="w-4 h-4" />
        <span>
          Current: <strong className="text-cyan-400">{currentArchetype}</strong>
        </span>
      </div>

      <div className="flex flex-wrap gap-1">
        {capArray.map((cap) => (
          <span key={cap} className="text-xs px-1.5 py-0.5 rounded bg-gray-700/50 text-gray-300">
            {cap}
          </span>
        ))}
      </div>

      {/* Delta comparison */}
      <div className="mt-3 space-y-1">
        <label className="text-xs text-gray-500">Switching would change access:</label>
        {deltas.slice(0, 3).map((delta) => (
          <div
            key={delta.archetype}
            className="flex items-center justify-between text-xs px-2 py-1 rounded bg-gray-700/30"
          >
            <span className="text-gray-300">{delta.archetype}</span>
            <div className="flex items-center gap-2">
              {delta.extraAffordances.length > 0 && (
                <span className="text-green-400">+{delta.extraAffordances.length}</span>
              )}
              {delta.missingAffordances.length > 0 && (
                <span className="text-red-400">-{delta.missingAffordances.length}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export interface ObserverDebugPanelProps {
  /** Force visibility (bypasses dev mode check) */
  forceVisible?: boolean;
}

/**
 * ObserverDebugPanel - Shows observer-dependent visibility for debugging.
 *
 * Only visible in development mode. Toggle with Ctrl+Shift+O.
 *
 * @example
 * ```tsx
 * // Auto-enabled in dev mode
 * <ObserverDebugPanel />
 *
 * // Force visible for testing
 * <ObserverDebugPanel forceVisible />
 * ```
 */
export function ObserverDebugPanel({ forceVisible = false }: ObserverDebugPanelProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const { observer } = useShell();

  // Only show in dev mode (or when forced)
  const isDev = import.meta.env.DEV || forceVisible;

  // Toggle visibility with Ctrl+Shift+O
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'O') {
      e.preventDefault();
      setIsVisible((v) => !v);
    }
  }, []);

  useEffect(() => {
    if (!isDev) return;
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isDev, handleKeyDown]);

  // Toggle node expansion
  const toggleNode = useCallback((nodePath: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(nodePath)) {
        next.delete(nodePath);
      } else {
        next.add(nodePath);
      }
      return next;
    });
  }, []);

  if (!isDev || !isVisible) {
    return null;
  }

  const glassStyles = GLASS_EFFECT.standard;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className={`
        fixed right-4 top-16 w-80
        ${glassStyles.background} ${glassStyles.blur}
        border border-gray-700/50 rounded-lg shadow-xl
        overflow-hidden
      `}
      style={{ zIndex: Z_INDEX_LAYERS.modal + 10 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-gray-700/50 bg-violet-900/20">
        <div className="flex items-center gap-2">
          <Bug className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-semibold text-white">Observer Debug</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 font-mono">Ctrl+Shift+O</span>
          <button onClick={() => setIsVisible(false)} className="p-1 hover:bg-gray-700/50 rounded">
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-3 space-y-4 max-h-[60vh] overflow-auto">
        {/* Current observer */}
        <ObserverComparison
          currentArchetype={observer.archetype}
          capabilities={observer.capabilities}
        />

        {/* Node gradations */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Code className="w-4 h-4 text-gray-400" />
            <label className="text-xs text-gray-500 uppercase tracking-wide">Node Gradations</label>
          </div>

          {Object.entries(NODE_GRADATIONS).map(([nodePath, gradation]) => (
            <NodeGradationCard
              key={nodePath}
              nodePath={nodePath}
              gradation={gradation}
              currentArchetype={observer.archetype}
              isExpanded={expandedNodes.has(nodePath)}
              onToggle={() => toggleNode(nodePath)}
            />
          ))}
        </div>

        {/* Legend */}
        <div className="border-t border-gray-700/50 pt-2 space-y-1">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Unlock className="w-3 h-3 text-green-400" />
            <span>Full access</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Shield className="w-3 h-3 text-amber-400" />
            <span>Partial access</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Lock className="w-3 h-3 text-red-400" />
            <span>No access</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-gray-700/50 bg-gray-800/50">
        <p className="text-xs text-gray-500">
          <Eye className="w-3 h-3 inline mr-1" />
          Observer gradation: <em>different archetypes see different realities</em>
        </p>
      </div>
    </motion.div>
  );
}

export default ObserverDebugPanel;
