/**
 * ConceptHomeProjection - The Universal Habitat Fallback
 *
 * When no specific projection is registered for an AGENTESE path,
 * this component provides a rich exploration experience with:
 * - Reference Panel (metadata, aspects, effects)
 * - Generated Playground (aspect invocation)
 * - Context-aware styling
 * - Warm, cultivating copy for minimal-tier paths
 *
 * This replaces GenericProjection as the default fallback, ensuring
 * every path has a home (AD-010: The Habitat Guarantee).
 *
 * @see spec/protocols/concept-home.md
 * @see spec/principles.md - AD-010
 */

import { memo, useMemo, useCallback, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sprout, ArrowRight, Terminal, BookOpen, Zap, GitBranch } from 'lucide-react';
import type { ProjectionProps } from './types';
import { ContextBadge } from '../ContextBadge';
import { GeneratedPlayground } from '../GeneratedPlayground';
import { ExamplesPanel } from '../ExamplesPanel';
import type { NodeExample } from '../ExamplesPanel';
import { MiniPolynomial } from '@/components/polynomial/MiniPolynomial';
import { formatPathLabel } from '@/utils/parseAgentesePath';
import type { AGENTESEContext } from '@/lib/habitat';
import { useHabitat } from '@/hooks/useHabitat';
import { apiClient } from '@/api/client';

// =============================================================================
// Types
// =============================================================================

type HabitatTier = 'minimal' | 'standard';

interface HabitatMetadata {
  path: string;
  context: AGENTESEContext;
  tier: HabitatTier;
  description: string | null;
  aspects: string[];
  effects: string[];
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Extract metadata from AGENTESE response for habitat rendering.
 *
 * The response may contain node metadata (description, aspects, effects)
 * or it may just be raw data. We extract what we can.
 */
function extractHabitatMetadata(
  path: string,
  context: string,
  response: unknown
): HabitatMetadata {
  // Try to extract from response if it's a manifest
  let description: string | null = null;
  let aspects: string[] = ['manifest'];
  let effects: string[] = [];

  if (response && typeof response === 'object') {
    const r = response as Record<string, unknown>;

    // Check for description in various forms
    if (typeof r.description === 'string') {
      description = r.description;
    } else if (typeof r.doc === 'string') {
      description = r.doc;
    }

    // Check for aspects
    if (Array.isArray(r.aspects)) {
      aspects = r.aspects.filter((a): a is string => typeof a === 'string');
    } else if (Array.isArray(r.affordances)) {
      aspects = r.affordances.filter((a): a is string => typeof a === 'string');
    }

    // Check for effects
    if (Array.isArray(r.effects)) {
      effects = r.effects.filter((e): e is string => typeof e === 'string');
    }
  }

  // Determine tier
  const tier: HabitatTier = description && aspects.length > 1 ? 'standard' : 'minimal';

  return {
    path,
    context: (['world', 'self', 'concept', 'void', 'time'].includes(context)
      ? context
      : 'world') as AGENTESEContext,
    tier,
    description,
    aspects,
    effects,
  };
}

// =============================================================================
// Sub-components
// =============================================================================

/**
 * Reference Panel - Shows path metadata in a sidebar
 */
const ReferencePanel = memo(function ReferencePanel({
  metadata,
  examples,
  onExampleClick,
  onAspectInvoke,
}: {
  metadata: HabitatMetadata;
  examples: NodeExample[];
  onExampleClick: (example: NodeExample) => void;
  onAspectInvoke: (aspect: string) => void;
}) {
  // Fetch polynomial structure if 'polynomial' aspect is available
  const [polynomial, setPolynomial] = useState<{
    positions: string[];
    current: string;
    directions: Record<string, string[]>;
  } | null>(null);

  useEffect(() => {
    if (metadata.aspects.includes('polynomial')) {
      const fetchPolynomial = async () => {
        try {
          const route = `/agentese/${metadata.path.replace(/\./g, '/')}/polynomial`;
          const response = await apiClient.get(route);
          if (response.data?.result) {
            setPolynomial(response.data.result);
          } else if (response.data?.positions) {
            setPolynomial(response.data);
          }
        } catch (error) {
          console.warn('Failed to fetch polynomial:', error);
        }
      };
      fetchPolynomial();
    }
  }, [metadata.path, metadata.aspects]);

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-gray-800/50 rounded-lg border border-gray-700/50 overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-700/50">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-gray-100 font-mono">
              {formatPathLabel(metadata.path)}
            </h2>
            <code className="text-xs text-gray-500 mt-1 block">
              {metadata.path}
            </code>
          </div>
          <ContextBadge context={metadata.context} size="md" showLabel />
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Description */}
        {metadata.description && (
          <div>
            <div className="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wide mb-2">
              <BookOpen className="w-3 h-3" />
              Description
            </div>
            <p className="text-sm text-gray-300 leading-relaxed">
              {metadata.description}
            </p>
          </div>
        )}

        {/* Examples (Habitat 2.0) */}
        {examples.length > 0 && (
          <div>
            <ExamplesPanel examples={examples} onExampleClick={onExampleClick} />
          </div>
        )}

        {/* Aspects - Clickable to navigate */}
        <div>
          <div className="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wide mb-2">
            <Zap className="w-3 h-3" />
            Aspects
          </div>
          <div className="flex flex-wrap gap-2">
            {metadata.aspects.map((aspect) => (
              <button
                key={aspect}
                onClick={() => onAspectInvoke(aspect)}
                className="px-2 py-1 text-xs font-mono bg-gray-700/50 rounded text-gray-300 hover:bg-gray-600/50 hover:text-white transition-colors cursor-pointer"
              >
                {aspect}
              </button>
            ))}
          </div>
        </div>

        {/* Effects */}
        {metadata.effects.length > 0 && (
          <div>
            <div className="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wide mb-2">
              <Terminal className="w-3 h-3" />
              Effects
            </div>
            <ul className="text-sm text-amber-300/80 space-y-1">
              {metadata.effects.map((effect) => (
                <li key={effect} className="flex items-start gap-2">
                  <ArrowRight className="w-3 h-3 mt-1 flex-shrink-0" />
                  <span>{effect}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Polynomial (Mini Polynomial - AD-002) */}
        {polynomial && (
          <div>
            <div className="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wide mb-2">
              <GitBranch className="w-3 h-3" />
              Polynomial Structure
            </div>
            <div className="bg-gray-900/30 rounded p-3">
              <MiniPolynomial
                positions={polynomial.positions}
                current={polynomial.current}
                directions={polynomial.directions}
                onTransitionClick={(_position, direction) => onAspectInvoke(direction)}
              />
            </div>
          </div>
        )}

        {/* Tier Badge */}
        <div className="pt-3 mt-3 border-t border-gray-700/30">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Tier</span>
            <span
              className={`
              px-2 py-0.5 rounded-full font-medium
              ${metadata.tier === 'standard'
                ? 'bg-blue-900/50 text-blue-300'
                : 'bg-gray-700/50 text-gray-400'
              }
            `}
            >
              {metadata.tier}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
});

/**
 * Header for minimal-tier paths
 */
const MinimalHeader = memo(function MinimalHeader({
  metadata,
}: {
  metadata: HabitatMetadata;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-start gap-4"
    >
      <div className="p-3 bg-gray-800/50 rounded-lg">
        <Sprout className="w-8 h-8 text-gray-400" />
      </div>
      <div>
        <div className="flex items-center gap-3 mb-1">
          <ContextBadge context={metadata.context} size="md" showLabel />
          <h1 className="text-xl font-semibold text-gray-100 font-mono">
            {formatPathLabel(metadata.path)}
          </h1>
        </div>
        <p className="text-gray-400">Explore this AGENTESE node</p>
        <code className="text-xs text-gray-500 mt-1 block">{metadata.path}</code>
      </div>
    </motion.div>
  );
});

/**
 * Header for standard-tier paths
 */
const StandardHeader = memo(function StandardHeader({
  metadata,
}: {
  metadata: HabitatMetadata;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-start justify-between gap-4"
    >
      <div>
        <div className="flex items-center gap-3 mb-2">
          <ContextBadge context={metadata.context} size="lg" showLabel />
          <h1 className="text-2xl font-bold text-gray-100">
            {formatPathLabel(metadata.path)}
          </h1>
        </div>
        <code className="text-sm text-gray-500 font-mono">{metadata.path}</code>
        {metadata.description && (
          <p className="text-gray-400 max-w-xl mt-2">{metadata.description}</p>
        )}
      </div>
    </motion.div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

/**
 * ConceptHomeProjection - Universal habitat for AGENTESE paths
 *
 * This is the fallback projection for paths without custom visualizations.
 * It provides a consistent, explorable experience with:
 * - Path header with context badge
 * - Reference panel with metadata
 * - Interactive playground for aspect invocation
 * - Pre-seeded examples (Habitat 2.0)
 *
 * @example
 * // Automatically used for unregistered paths via resolveProjection()
 * // Or manually:
 * <ConceptHomeProjection context={projectionContext} />
 */
export const ConceptHomeProjection = memo(function ConceptHomeProjection({
  context,
}: ProjectionProps) {
  const { path, context: agentContext, response } = context;
  const navigate = useNavigate();

  // Get habitat info from discovery endpoint (includes aspects, examples)
  const { habitat } = useHabitat(path);

  // Extract habitat metadata from response, but prefer discovery aspects
  // The manifest response may not include aspects, but discovery always does
  const metadata = useMemo(() => {
    const base = extractHabitatMetadata(path, agentContext ?? 'world', response);
    return {
      ...base,
      // Prefer aspects from discovery endpoint over response extraction
      aspects: habitat?.aspects && habitat.aspects.length > 0
        ? habitat.aspects
        : base.aspects,
      // Also use description from discovery if response didn't have one
      description: base.description ?? habitat?.description ?? null,
    };
  }, [path, agentContext, response, habitat]);

  // Get examples from discovery (Habitat 2.0)
  const examples = habitat?.examples ?? [];

  // Handle example click - navigate to AGENTESE URL with aspect and kwargs
  const handleExampleClick = useCallback(
    (example: NodeExample) => {
      // Build URL: /{path}:{aspect}?{kwargs}
      const params = new URLSearchParams();
      for (const [key, value] of Object.entries(example.kwargs)) {
        params.set(key, String(value));
      }

      const url = `/${path}:${example.aspect}${params.toString() ? `?${params.toString()}` : ''}`;
      navigate(url);
    },
    [path, navigate]
  );

  // Handle aspect invocation from polynomial (Mini Polynomial)
  const handleAspectInvoke = useCallback(
    (aspect: string) => {
      const url = `/${path}:${aspect}`;
      navigate(url);
    },
    [path, navigate]
  );

  return (
    <div className="h-full overflow-auto bg-surface-canvas">
      <div className="max-w-5xl mx-auto p-6 space-y-6">
        {/* Header */}
        {metadata.tier === 'minimal' ? (
          <MinimalHeader metadata={metadata} />
        ) : (
          <StandardHeader metadata={metadata} />
        )}

        {/* Main content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Reference Panel */}
          <div className="lg:col-span-1">
            <ReferencePanel
              metadata={metadata}
              examples={examples}
              onExampleClick={handleExampleClick}
              onAspectInvoke={handleAspectInvoke}
            />
          </div>

          {/* Right: Playground */}
          <div className="lg:col-span-2">
            <div className="bg-gray-800/50 rounded-lg border border-gray-700/50 overflow-hidden h-full min-h-[400px]">
              <GeneratedPlayground
                path={metadata.path}
                aspects={metadata.aspects}
                initialAspect={metadata.aspects[0]}
                className="h-full"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
});

export default ConceptHomeProjection;
