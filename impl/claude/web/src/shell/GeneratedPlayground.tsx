/**
 * GeneratedPlayground - Inline REPL for Standard/Minimal Tier Habitats
 *
 * A standalone AGENTESE invocation interface for paths without custom
 * visualizations. Provides aspect buttons, output display, and JSON viewing.
 *
 * "The AGENTESE REPL IS the default playground."
 * — AD-010: The Habitat Guarantee
 *
 * @see spec/principles.md - AD-010: The Habitat Guarantee
 * @see plans/concept-home-implementation.md
 */

import { useState, useCallback, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Copy, Check, ChevronDown, ChevronUp, Terminal, Sparkles } from 'lucide-react';
import { apiClient } from '@/api/client';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { GhostPanel, type Ghost } from './GhostPanel';
import { ExplorationBreadcrumb, type BreadcrumbItem } from './ExplorationBreadcrumb';

// =============================================================================
// Breathing Animation Variants
// =============================================================================

/**
 * Breathing animation for active elements.
 * "Active elements (currently invoking, streaming) use a subtle breathing animation"
 * — AD-010: The Habitat Guarantee
 */
const breatheVariants = {
  idle: { scale: 1, opacity: 1 },
  breathing: {
    scale: [1, 1.02, 1],
    opacity: [0.9, 1, 0.9],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut' as const,
    },
  },
};

/**
 * Micro-teaching hints for aspects.
 * These help users understand what each aspect does.
 */
const ASPECT_HINTS: Record<string, string> = {
  manifest: 'Manifest reveals the current state—like asking "what are you right now?"',
  witness: 'Witness observes without changing—pure perception of the entity.',
  lens: 'Lens applies a perspective filter to what you see.',
  refine: 'Refine improves or evolves the entity based on feedback.',
  capture: 'Capture stores this moment in memory (Brain).',
  nurture: 'Nurture helps something grow toward its potential.',
  sip: 'Sip draws a small amount from the entropy reservoir.',
  tithe: 'Tithe returns surplus to the void—the gift economy.',
  greet: 'Greet initiates a connection with this entity.',
  dialogue: 'Dialogue opens a conversational exchange.',
  polynomial: 'Polynomial shows the state machine—positions and directions.',
  transition: 'Transition moves between states in the polynomial.',
  affordances: 'Affordances lists what actions are available to you.',
};

function getAspectHint(aspect: string): string {
  return ASPECT_HINTS[aspect] || `${aspect} — an aspect of this path`;
}

// =============================================================================
// Types
// =============================================================================

export interface GeneratedPlaygroundProps {
  /** AGENTESE path to explore */
  path: string;
  /** Available aspects to invoke */
  aspects: string[];
  /** Pre-seeded example invocations */
  examples?: string[];
  /** Optional initial aspect to highlight */
  initialAspect?: string;
  /** Additional CSS classes */
  className?: string;
}

interface InvocationResult {
  aspect: string;
  result: unknown;
  error?: string;
  duration: number;
  timestamp: Date;
}

// =============================================================================
// Constants
// =============================================================================

/** Default aspect if none provided */
const DEFAULT_ASPECT = 'manifest';

/** Aspect button colors by category */
const ASPECT_COLORS: Record<string, string> = {
  // Perception aspects
  manifest: 'bg-emerald-800/50 hover:bg-emerald-700/60 text-emerald-200',
  witness: 'bg-blue-800/50 hover:bg-blue-700/60 text-blue-200',
  lens: 'bg-cyan-800/50 hover:bg-cyan-700/60 text-cyan-200',
  // Action aspects
  refine: 'bg-amber-800/50 hover:bg-amber-700/60 text-amber-200',
  capture: 'bg-orange-800/50 hover:bg-orange-700/60 text-orange-200',
  nurture: 'bg-green-800/50 hover:bg-green-700/60 text-green-200',
  // Entropy aspects
  sip: 'bg-pink-800/50 hover:bg-pink-700/60 text-pink-200',
  tithe: 'bg-purple-800/50 hover:bg-purple-700/60 text-purple-200',
  // Default
  default: 'bg-gray-700/50 hover:bg-gray-600/60 text-gray-200',
};

// =============================================================================
// Component
// =============================================================================

/**
 * GeneratedPlayground provides an interactive REPL for any AGENTESE path.
 *
 * Features:
 * - Aspect buttons for one-click invocation
 * - Output display with JSON formatting
 * - Copy to clipboard
 * - Loading state with spinner
 * - Error display with retry
 *
 * @example
 * ```tsx
 * <GeneratedPlayground
 *   path="world.town.citizen"
 *   aspects={['manifest', 'greet', 'gossip']}
 * />
 * ```
 */
export const GeneratedPlayground = memo(function GeneratedPlayground({
  path,
  aspects,
  examples = [],
  initialAspect,
  className = '',
}: GeneratedPlaygroundProps) {
  const { shouldAnimate } = useMotionPreferences();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InvocationResult | null>(null);
  const [expanded, setExpanded] = useState(true);
  const [copied, setCopied] = useState(false);
  const [ghosts, setGhosts] = useState<Ghost[]>([]);
  const [trail, setTrail] = useState<BreadcrumbItem[]>([]);

  // Ensure we have at least 'manifest' aspect
  const availableAspects = aspects.length > 0 ? aspects : [DEFAULT_ASPECT];

  /**
   * Invoke an aspect on the path.
   */
  const invokeAspect = useCallback(
    async (aspect: string) => {
      setLoading(true);
      setResult(null);
      setGhosts([]); // Clear previous ghosts

      const start = Date.now();

      try {
        // Build the AGENTESE route
        const route = `/agentese/${path.replace(/\./g, '/')}/${aspect}`;

        // POST for actions, GET for manifest/witness
        const isQuery = ['manifest', 'witness', 'lens'].includes(aspect);
        const response = isQuery
          ? await apiClient.get(route)
          : await apiClient.post(route, {});

        setResult({
          aspect,
          result: response.data?.result ?? response.data,
          duration: Date.now() - start,
          timestamp: new Date(),
        });

        // Add to trail (max 5 items)
        setTrail((prev) => {
          const newItem: BreadcrumbItem = {
            path,
            aspect,
            timestamp: Date.now(),
          };
          const updated = [...prev, newItem];
          return updated.slice(-5); // Keep only last 5
        });

        // Fetch alternatives (ghosts) after successful invocation
        try {
          const altRoute = `/agentese/${path.replace(/\./g, '/')}/alternatives`;
          const altResponse = await apiClient.post(altRoute, { invoked_aspect: aspect });
          const alternatives = altResponse.data?.result ?? altResponse.data;

          if (Array.isArray(alternatives)) {
            setGhosts(alternatives);
          }
        } catch (altError) {
          // Silently fail - alternatives are optional
          console.debug('Could not fetch alternatives:', altError);
        }
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        setResult({
          aspect,
          result: null,
          error: errorMsg,
          duration: Date.now() - start,
          timestamp: new Date(),
        });
      } finally {
        setLoading(false);
      }
    },
    [path]
  );

  /**
   * Copy result to clipboard.
   */
  const copyResult = useCallback(async () => {
    if (!result) return;

    const text = result.error
      ? `Error: ${result.error}`
      : JSON.stringify(result.result, null, 2);

    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [result]);

  /**
   * Handle ghost click - invoke the alternative aspect.
   */
  const handleGhostClick = useCallback(
    (aspect: string) => {
      invokeAspect(aspect);
    },
    [invokeAspect]
  );

  /**
   * Handle breadcrumb navigation.
   */
  const handleNavigate = useCallback(
    (item: BreadcrumbItem) => {
      invokeAspect(item.aspect);
    },
    [invokeAspect]
  );

  /**
   * Get button color for an aspect.
   */
  const getAspectColor = (aspect: string): string => {
    return ASPECT_COLORS[aspect] ?? ASPECT_COLORS.default;
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="border-b border-gray-700/50">
        <div className="flex items-center justify-between px-4 py-2">
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Terminal className="w-4 h-4" />
            <span className="font-mono">{path}</span>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 hover:bg-gray-700 rounded transition-colors"
            aria-label={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? (
              <ChevronUp className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            )}
          </button>
        </div>
        {/* Exploration Breadcrumb */}
        {trail.length > 0 && (
          <div className="px-4 pb-2">
            <ExplorationBreadcrumb trail={trail} onNavigate={handleNavigate} />
          </div>
        )}
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: shouldAnimate ? 0.2 : 0 }}
            className="flex-1 overflow-hidden"
          >
            {/* Aspect Buttons */}
            <div className="p-3 border-b border-gray-700/50">
              <div className="text-xs text-gray-500 mb-2">Aspects</div>
              <div className="flex flex-wrap gap-2">
                {availableAspects.map((aspect) => (
                  <button
                    key={aspect}
                    onClick={() => invokeAspect(aspect)}
                    disabled={loading}
                    className={`
                      px-3 py-1.5 rounded-md text-sm font-medium
                      transition-colors disabled:opacity-50 disabled:cursor-not-allowed
                      flex items-center gap-1.5
                      ${getAspectColor(aspect)}
                      ${initialAspect === aspect ? 'ring-2 ring-white/30' : ''}
                    `}
                  >
                    <Play className="w-3 h-3" />
                    {aspect}
                  </button>
                ))}
              </div>

              {/* Examples */}
              {examples.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-700/30">
                  <div className="text-xs text-gray-500 mb-2">Examples</div>
                  <div className="flex flex-wrap gap-2">
                    {examples.map((example, i) => (
                      <button
                        key={i}
                        onClick={() => {
                          const [, aspect] = example.split('.').slice(-1);
                          invokeAspect(aspect || DEFAULT_ASPECT);
                        }}
                        className="px-2 py-1 text-xs bg-gray-800 hover:bg-gray-700 rounded text-gray-300 font-mono"
                      >
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Output Area */}
            <div className="flex-1 p-3 overflow-auto bg-gray-900/50 min-h-[200px]">
              {loading ? (
                <motion.div
                  className="flex flex-col items-center justify-center h-full gap-3"
                  variants={breatheVariants}
                  initial="idle"
                  animate={shouldAnimate ? 'breathing' : 'idle'}
                >
                  <motion.div
                    className="p-3 rounded-full bg-emerald-900/30"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                  >
                    <Sparkles className="w-6 h-6 text-emerald-400" />
                  </motion.div>
                  <p className="text-sm text-gray-400">Invoking...</p>
                </motion.div>
              ) : result ? (
                <div className="space-y-2">
                  {/* Result Header */}
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">
                      {result.aspect} • {result.duration}ms
                    </span>
                    <button
                      onClick={copyResult}
                      className="flex items-center gap-1 px-2 py-1 hover:bg-gray-700 rounded transition-colors"
                    >
                      {copied ? (
                        <>
                          <Check className="w-3 h-3 text-green-400" />
                          <span className="text-green-400">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3 text-gray-400" />
                          <span className="text-gray-400">Copy</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Result Content */}
                  {result.error ? (
                    <div className="p-3 bg-red-900/30 rounded-md border border-red-800/50">
                      <div className="text-red-400 text-sm font-medium">Error</div>
                      <div className="text-red-300 text-sm mt-1">{result.error}</div>
                      <button
                        onClick={() => invokeAspect(result.aspect)}
                        className="mt-2 px-2 py-1 text-xs bg-red-800/50 hover:bg-red-700/60 rounded text-red-200"
                      >
                        Retry
                      </button>
                    </div>
                  ) : (
                    <>
                      {/* Micro-teaching hint */}
                      <motion.div
                        initial={{ opacity: 0, y: -5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-3 px-3 py-2 bg-emerald-900/20 border border-emerald-800/30 rounded-md"
                      >
                        <div className="flex items-start gap-2">
                          <Sparkles className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-emerald-300/90">
                            {getAspectHint(result.aspect)}
                          </p>
                        </div>
                      </motion.div>

                      <pre className="p-3 bg-gray-800/50 rounded-md text-sm text-gray-300 overflow-x-auto font-mono">
                        {typeof result.result === 'string'
                          ? result.result
                          : JSON.stringify(result.result, null, 2)}
                      </pre>
                    </>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <Terminal className="w-8 h-8 mb-2 opacity-50" />
                  <p className="text-sm">Click an aspect to invoke</p>
                  <p className="text-xs mt-1 opacity-75">
                    Results will appear here
                  </p>
                </div>
              )}
            </div>

            {/* Ghost Panel - show alternatives after successful invocation */}
            {!loading && result && !result.error && ghosts.length > 0 && (
              <div className="px-3 pb-3">
                <GhostPanel alternatives={ghosts} onGhostClick={handleGhostClick} />
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
});

export default GeneratedPlayground;
