/**
 * DerivationPortal: Expandable portal token for hypergraph navigation.
 *
 * Phase 5: Derivation Framework Visualization
 *
 * Implements the portal-token pattern from spec/protocols/portal-token.md:
 * - COLLAPSED: Shows agent name, tier badge, confidence bar
 * - EXPANDED: Shows derives_from/dependents counts, quick actions
 *
 * Used for navigating the derivation hypergraph:
 * - Click to expand/collapse
 * - Navigate to ancestors (derives_from)
 * - Navigate to descendants (dependents)
 *
 * @example
 * ```tsx
 * <DerivationPortal
 *   token={{ agent_name: "Flux", tier: "functor", confidence: 0.98, derives_from_count: 2, dependents_count: 5 }}
 *   expanded={false}
 *   onToggle={() => setExpanded(!expanded)}
 *   onNavigate={(edge) => navigate(`/derivation/${token.agent_name}?edge=${edge}`)}
 * />
 * ```
 */

import { motion, AnimatePresence } from 'framer-motion';
import type { DerivationPortalToken, DerivationTier } from '../../api/types';
import { DERIVATION_TIER_CONFIG } from '../../api/types';

// =============================================================================
// Types
// =============================================================================

export interface DerivationPortalProps {
  token: DerivationPortalToken;
  expanded?: boolean;
  onToggle?: () => void;
  onNavigate?: (edge: 'derives_from' | 'dependents') => void;
  onSelect?: () => void;
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

export function DerivationPortal({
  token,
  expanded = false,
  onToggle,
  onNavigate,
  onSelect,
  className = '',
}: DerivationPortalProps) {
  const config = DERIVATION_TIER_CONFIG[token.tier as DerivationTier] || {
    color: '#6b7280',
    icon: 'circle',
    ceiling: 1.0,
  };

  return (
    <motion.div
      className={`bg-gray-900 border border-gray-700 rounded-lg overflow-hidden ${className}`}
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      {/* Collapsed header (always visible) */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 p-3 hover:bg-gray-800 transition-colors"
      >
        {/* Expand/collapse chevron */}
        <motion.span
          className="text-gray-400"
          animate={{ rotate: expanded ? 90 : 0 }}
          transition={{ duration: 0.2 }}
        >
          ▶
        </motion.span>

        {/* Agent name */}
        <span className="font-medium text-white flex-1 text-left">
          {token.agent_name}
        </span>

        {/* Tier badge */}
        <span
          className="px-2 py-0.5 rounded text-xs font-medium"
          style={{
            backgroundColor: config.color + '20',
            color: config.color,
          }}
        >
          {token.tier}
        </span>

        {/* Confidence bar */}
        <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: config.color }}
            initial={{ width: 0 }}
            animate={{ width: `${token.confidence * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>

        {/* Confidence value */}
        <span className="text-xs font-mono text-gray-300 w-10 text-right">
          {Math.round(token.confidence * 100)}%
        </span>
      </button>

      {/* Expanded content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-gray-700"
          >
            <div className="p-3 space-y-3">
              {/* Connection counts */}
              <div className="flex gap-4 text-xs text-gray-400">
                {token.derives_from_count !== undefined && (
                  <span>
                    Ancestors: <strong className="text-white">{token.derives_from_count}</strong>
                  </span>
                )}
                {token.dependents_count !== undefined && (
                  <span>
                    Dependents: <strong className="text-white">{token.dependents_count}</strong>
                  </span>
                )}
              </div>

              {/* Navigation actions */}
              <div className="flex gap-2">
                {token.derives_from_count !== undefined && token.derives_from_count > 0 && (
                  <button
                    onClick={() => onNavigate?.('derives_from')}
                    className="flex-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-300 transition-colors"
                  >
                    ↑ View Ancestors
                  </button>
                )}
                {token.dependents_count !== undefined && token.dependents_count > 0 && (
                  <button
                    onClick={() => onNavigate?.('dependents')}
                    className="flex-1 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-300 transition-colors"
                  >
                    ↓ View Dependents
                  </button>
                )}
                {onSelect && (
                  <button
                    onClick={onSelect}
                    className="px-3 py-2 bg-blue-600 hover:bg-blue-500 rounded text-xs text-white transition-colors"
                  >
                    Details
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// =============================================================================
// Portal List Component
// =============================================================================

export interface DerivationPortalListProps {
  tokens: DerivationPortalToken[];
  expandedId?: string | null;
  onToggle?: (agentName: string) => void;
  onNavigate?: (agentName: string, edge: 'derives_from' | 'dependents') => void;
  onSelect?: (agentName: string) => void;
  className?: string;
}

export function DerivationPortalList({
  tokens,
  expandedId,
  onToggle,
  onNavigate,
  onSelect,
  className = '',
}: DerivationPortalListProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      <AnimatePresence mode="popLayout">
        {tokens.map((token) => (
          <DerivationPortal
            key={token.agent_name}
            token={token}
            expanded={expandedId === token.agent_name}
            onToggle={() => onToggle?.(token.agent_name)}
            onNavigate={(edge) => onNavigate?.(token.agent_name, edge)}
            onSelect={() => onSelect?.(token.agent_name)}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}

export default DerivationPortal;
