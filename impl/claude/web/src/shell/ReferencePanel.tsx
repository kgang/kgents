/**
 * ReferencePanel - Metadata Display for Standard Tier Habitats
 *
 * Shows path documentation, aspects, effects, and related paths.
 * Used alongside GeneratedPlayground for standard-tier paths.
 *
 * "Standard tier shows what can be done; the REPL lets you do it."
 * — AD-010: The Habitat Guarantee
 *
 * @see spec/principles.md - AD-010: The Habitat Guarantee
 * @see plans/concept-home-implementation.md
 */

import { memo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Info,
  Zap,
  AlertTriangle,
  ArrowRight,
  ExternalLink,
  Sparkles,
} from 'lucide-react';
import { ContextBadge } from './ContextBadge';
import { extractContext, getRouteForPath } from '@/lib/habitat';
import type { HabitatInfo } from '@/hooks/useHabitat';

// =============================================================================
// Types
// =============================================================================

export interface ReferencePanelProps {
  /** Habitat information for the path */
  habitat: HabitatInfo;
  /** Related paths to show as navigation links */
  relatedPaths?: string[];
  /** Additional CSS classes */
  className?: string;
}

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  empty?: boolean;
}

// =============================================================================
// Section Component
// =============================================================================

const Section = memo(function Section({
  title,
  icon,
  children,
  empty = false,
}: SectionProps) {
  if (empty) return null;

  return (
    <div className="py-3 border-b border-gray-700/30 last:border-b-0">
      <div className="flex items-center gap-2 text-xs text-gray-400 uppercase tracking-wide mb-2">
        {icon}
        {title}
      </div>
      {children}
    </div>
  );
});

// =============================================================================
// Component
// =============================================================================

/**
 * ReferencePanel displays structured metadata about an AGENTESE path.
 *
 * Sections:
 * - Description (if available)
 * - Aspects (invokable actions)
 * - Effects (declared side effects)
 * - Related Paths (navigation links)
 *
 * @example
 * ```tsx
 * <ReferencePanel
 *   habitat={habitat}
 *   relatedPaths={['world.town.coalition', 'world.town.simulation']}
 * />
 * ```
 */
export const ReferencePanel = memo(function ReferencePanel({
  habitat,
  relatedPaths = [],
  className = '',
}: ReferencePanelProps) {
  const {
    path,
    context,
    tier,
    description,
    aspects,
    effects,
  } = habitat;

  // Get parent path for "back" navigation
  const pathParts = path.split('.');
  const parentPath = pathParts.length > 1
    ? pathParts.slice(0, -1).join('.')
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-gray-800/50 rounded-lg border border-gray-700/50 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-700/50">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-gray-100 font-mono">
              {path}
            </h2>
            {parentPath && (
              <Link
                to={getRouteForPath(parentPath)}
                className="text-xs text-gray-500 hover:text-gray-400 flex items-center gap-1 mt-1"
              >
                <ArrowRight className="w-3 h-3 rotate-180" />
                {parentPath}
              </Link>
            )}
          </div>
          <ContextBadge context={context} size="md" showLabel />
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-1">
        {/* Description */}
        <Section
          title="Description"
          icon={<Info className="w-3 h-3" />}
          empty={!description}
        >
          <p className="text-sm text-gray-300 leading-relaxed">
            {description}
          </p>
        </Section>

        {/* Aspects */}
        <Section
          title="Aspects"
          icon={<Zap className="w-3 h-3" />}
          empty={aspects.length === 0}
        >
          <div className="flex flex-wrap gap-2">
            {aspects.map((aspect) => (
              <span
                key={aspect}
                className="px-2 py-1 text-xs font-mono bg-gray-700/50 rounded text-gray-300"
              >
                {aspect}
              </span>
            ))}
          </div>
        </Section>

        {/* Effects */}
        <Section
          title="Effects"
          icon={<AlertTriangle className="w-3 h-3" />}
          empty={effects.length === 0}
        >
          <ul className="text-sm text-amber-300/80 space-y-1">
            {effects.map((effect) => (
              <li key={effect} className="flex items-start gap-2">
                <Sparkles className="w-3 h-3 mt-1 flex-shrink-0" />
                <span>{effect}</span>
              </li>
            ))}
          </ul>
        </Section>

        {/* Related Paths */}
        <Section
          title="Related"
          icon={<ExternalLink className="w-3 h-3" />}
          empty={relatedPaths.length === 0}
        >
          <div className="flex flex-col gap-1">
            {relatedPaths.map((relatedPath) => (
              <Link
                key={relatedPath}
                to={getRouteForPath(relatedPath)}
                className="flex items-center gap-2 px-2 py-1.5 text-sm text-gray-400 hover:text-gray-200 hover:bg-gray-700/30 rounded transition-colors"
              >
                <ContextBadge
                  context={extractContext(relatedPath)}
                  size="sm"
                />
                <span className="font-mono">{relatedPath}</span>
              </Link>
            ))}
          </div>
        </Section>

        {/* Tier Badge */}
        <div className="pt-3 mt-3 border-t border-gray-700/30">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Tier</span>
            <span className={`
              px-2 py-0.5 rounded-full font-medium
              ${tier === 'rich' ? 'bg-emerald-900/50 text-emerald-300' :
                tier === 'standard' ? 'bg-blue-900/50 text-blue-300' :
                'bg-gray-700/50 text-gray-400'}
            `}>
              {tier}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
});

export default ReferencePanel;
