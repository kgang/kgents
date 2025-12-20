/**
 * ContextGauge - Token Usage and Cost Visualization
 *
 * Shows AI metadata visibility in an elegant, information-dense format:
 * - Token usage with progress bar
 * - Session cost accumulator
 * - Current model indicator
 *
 * Follows elastic-ui-patterns.md: compact on mobile, full on desktop.
 *
 * @see spec/protocols/chat.md
 * @see services/chat/session.py - SessionBudget
 */

import { useState, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Coins, Database, Activity, ChevronRight, TrendingUp } from 'lucide-react';
import { useAgenteseMutation } from '@/hooks/useAgentesePath';
import { useShell } from '@/shell/ShellProvider';
import type { SelfChatMetricsResponse } from '@/api/types/_generated/self-chat';

// =============================================================================
// Types
// =============================================================================

export interface ContextGaugeProps {
  /** Session ID to fetch metrics for */
  sessionId: string | null;
  /** Tokens used in current context */
  tokensUsed?: number;
  /** Context window size */
  contextWindow?: number;
  /** Session cost in USD */
  sessionCost?: number;
  /** Refresh interval in ms (0 = no auto-refresh) */
  refreshInterval?: number;
  /** Visual variant */
  variant?: 'full' | 'compact' | 'minimal';
  /** Additional CSS classes */
  className?: string;
}

interface MetricsData {
  tokens_in: number;
  tokens_out: number;
  total_tokens: number;
  turn_count: number;
  estimated_cost_usd: number;
  context_utilization: number;
}

// =============================================================================
// Constants
// =============================================================================

// Default context windows by model (approx)
const MODEL_CONTEXT_WINDOWS: Record<string, number> = {
  'claude-3-haiku-20240307': 200000,
  'claude-sonnet-4-20250514': 200000,
  'claude-opus-4-20250514': 200000,
  default: 200000,
};

// Color thresholds for utilization
const UTILIZATION_COLORS = {
  low: 'bg-emerald-500', // < 50%
  medium: 'bg-cyan-500', // 50-80%
  high: 'bg-amber-500', // 80-95%
  critical: 'bg-red-500', // > 95%
};

function getUtilizationColor(ratio: number): string {
  if (ratio < 0.5) return UTILIZATION_COLORS.low;
  if (ratio < 0.8) return UTILIZATION_COLORS.medium;
  if (ratio < 0.95) return UTILIZATION_COLORS.high;
  return UTILIZATION_COLORS.critical;
}

// =============================================================================
// Helpers
// =============================================================================

function formatTokens(tokens: number): string {
  if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
  if (tokens >= 1000) return `${(tokens / 1000).toFixed(1)}k`;
  return tokens.toString();
}

function formatCost(cost: number): string {
  if (cost < 0.01) return '<$0.01';
  if (cost < 1) return `$${cost.toFixed(2)}`;
  return `$${cost.toFixed(2)}`;
}

// =============================================================================
// Component
// =============================================================================

export function ContextGauge({
  sessionId,
  tokensUsed: propTokensUsed,
  contextWindow = MODEL_CONTEXT_WINDOWS.default,
  sessionCost: propSessionCost,
  refreshInterval = 0,
  variant: propVariant,
  className = '',
}: ContextGaugeProps) {
  const { density } = useShell();
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  // Auto-select variant based on density if not specified
  const variant = propVariant || (density === 'compact' ? 'minimal' : 'full');

  // Fetch metrics
  const { mutate: fetchMetrics } = useAgenteseMutation<
    { session_id: string },
    SelfChatMetricsResponse
  >('self.chat:metrics');

  // Load metrics
  const loadMetrics = useCallback(async () => {
    if (!sessionId) return;
    const response = await fetchMetrics({ session_id: sessionId });
    if (response) {
      setMetrics({
        tokens_in: response.total_tokens ?? 0, // Simplify: total is what we show
        tokens_out: 0,
        total_tokens: response.total_tokens ?? 0,
        turn_count: response.total_turns ?? 0,
        estimated_cost_usd: 0, // Not in current metrics response, would need to add
        context_utilization: (response.total_tokens ?? 0) / contextWindow,
      });
    }
  }, [sessionId, fetchMetrics, contextWindow]);

  // Initial load and polling
  useEffect(() => {
    if (sessionId) {
      loadMetrics();
    }
  }, [sessionId, loadMetrics]);

  useEffect(() => {
    if (refreshInterval > 0 && sessionId) {
      const interval = setInterval(loadMetrics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, sessionId, loadMetrics]);

  // Use props if provided, otherwise use fetched metrics
  const tokensUsed = propTokensUsed ?? metrics?.total_tokens ?? 0;
  const sessionCost = propSessionCost ?? metrics?.estimated_cost_usd ?? 0;
  const utilization = tokensUsed / contextWindow;
  const utilizationPercent = Math.min(utilization * 100, 100);
  const utilizationColor = getUtilizationColor(utilization);

  // Minimal variant (icon + percentage only)
  if (variant === 'minimal') {
    return (
      <div className={`flex items-center gap-1.5 ${className}`}>
        <Database className="w-3.5 h-3.5 text-gray-500" />
        <span className="text-xs text-gray-400">{utilizationPercent.toFixed(0)}%</span>
        <div className="w-12 h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            className={`h-full ${utilizationColor} rounded-full`}
            initial={{ width: 0 }}
            animate={{ width: `${utilizationPercent}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>
    );
  }

  // Compact variant (single line, expandable)
  if (variant === 'compact') {
    return (
      <div className={`${className}`}>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-gray-400 hover:text-gray-200 transition-colors"
        >
          <Database className="w-3.5 h-3.5" />
          <span className="text-xs font-medium">{formatTokens(tokensUsed)}</span>
          <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className={`h-full ${utilizationColor} rounded-full`}
              initial={{ width: 0 }}
              animate={{ width: `${utilizationPercent}%` }}
            />
          </div>
          <ChevronRight
            className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
          />
        </button>

        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="mt-2 pl-5 space-y-1 text-xs text-gray-500"
          >
            <div className="flex justify-between">
              <span>Context</span>
              <span className="text-gray-400">
                {formatTokens(tokensUsed)} / {formatTokens(contextWindow)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Cost</span>
              <span className="text-gray-400">{formatCost(sessionCost)}</span>
            </div>
            {metrics?.turn_count && (
              <div className="flex justify-between">
                <span>Turns</span>
                <span className="text-gray-400">{metrics.turn_count}</span>
              </div>
            )}
          </motion.div>
        )}
      </div>
    );
  }

  // Full variant (detailed view)
  return (
    <div className={`space-y-3 ${className}`}>
      {/* Token usage bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500 flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5" />
            Context
          </span>
          <span className="text-gray-400">
            {formatTokens(tokensUsed)}{' '}
            <span className="text-gray-600">/ {formatTokens(contextWindow)}</span>
          </span>
        </div>
        <div className="h-2 bg-gray-700/50 rounded-full overflow-hidden">
          <motion.div
            className={`h-full ${utilizationColor} rounded-full`}
            initial={{ width: 0 }}
            animate={{ width: `${utilizationPercent}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-gray-600">
          <span>{utilizationPercent.toFixed(1)}% utilized</span>
          <span>{formatTokens(contextWindow - tokensUsed)} remaining</span>
        </div>
      </div>

      {/* Metrics row */}
      <div className="flex items-center gap-4 text-xs">
        {/* Session cost */}
        <div className="flex items-center gap-1.5 text-gray-400">
          <Coins className="w-3.5 h-3.5 text-amber-500/70" />
          <span>{formatCost(sessionCost)}</span>
        </div>

        {/* Turn count */}
        {metrics?.turn_count !== undefined && metrics.turn_count > 0 && (
          <div className="flex items-center gap-1.5 text-gray-400">
            <Activity className="w-3.5 h-3.5 text-cyan-500/70" />
            <span>{metrics.turn_count} turns</span>
          </div>
        )}

        {/* Avg tokens per turn */}
        {metrics?.turn_count && metrics.turn_count > 0 && (
          <div className="flex items-center gap-1.5 text-gray-400">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-500/70" />
            <span>~{formatTokens(Math.round(tokensUsed / metrics.turn_count))}/turn</span>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Teaching Mode Context Breakdown
// =============================================================================

export interface ContextBreakdownProps {
  /** Session ID */
  sessionId: string | null;
  /** Whether teaching mode is active */
  isTeachingMode?: boolean;
  /** Breakdown segments */
  segments?: {
    name: string;
    tokens: number;
    color: string;
    description: string;
  }[];
  /** Additional CSS classes */
  className?: string;
}

/**
 * ContextBreakdown - Shows detailed context composition when teaching mode is active.
 *
 * Visualizes how the context window is being used:
 * - System prompt (fixed overhead)
 * - Summary/history compression
 * - Working memory (recent turns)
 * - Available headroom
 *
 * This teaches users how context management works.
 *
 * Phase 2: Now fetches real data from self.chat:context AGENTESE endpoint.
 */
export function ContextBreakdown({
  sessionId,
  isTeachingMode = false,
  segments: propSegments,
  className = '',
}: ContextBreakdownProps) {
  const [breakdown, setBreakdown] = useState<{
    segments: { name: string; tokens: number; color: string; description: string }[];
    utilization: number;
    strategy: string;
    has_summary: boolean;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch context breakdown from AGENTESE
  const { mutate: fetchContext } = useAgenteseMutation<
    { session_id: string },
    {
      segments: { name: string; tokens: number; color: string; description: string }[];
      total_tokens: number;
      context_window: number;
      utilization: number;
      strategy: string;
      has_summary: boolean;
    }
  >('self.chat:context');

  // Load breakdown when teaching mode activates
  useEffect(() => {
    if (!isTeachingMode || !sessionId) {
      setBreakdown(null);
      return;
    }

    const loadBreakdown = async () => {
      setIsLoading(true);
      try {
        const response = await fetchContext({ session_id: sessionId });
        if (response) {
          setBreakdown({
            segments: response.segments,
            utilization: response.utilization,
            strategy: response.strategy,
            has_summary: response.has_summary,
          });
        }
      } catch {
        // Fallback to defaults on error
        setBreakdown(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadBreakdown();
  }, [sessionId, isTeachingMode, fetchContext]);

  // Default segments when API unavailable
  const defaultSegments = [
    {
      name: 'System',
      tokens: 2500,
      color: 'bg-violet-500',
      description: 'System prompt and personality',
    },
    {
      name: 'Summary',
      tokens: 1500,
      color: 'bg-blue-500',
      description: 'Compressed conversation history',
    },
    {
      name: 'Working',
      tokens: 4000,
      color: 'bg-cyan-500',
      description: 'Recent turns (full detail)',
    },
    {
      name: 'Available',
      tokens: 8000,
      color: 'bg-gray-700',
      description: 'Remaining context space',
    },
  ];

  // Priority: props > API response > defaults
  const displaySegments = propSegments || breakdown?.segments || defaultSegments;
  const totalTokens = displaySegments.reduce((sum, s) => sum + s.tokens, 0);
  const strategy = breakdown?.strategy || 'summarize';
  const hasSummary = breakdown?.has_summary || false;

  if (!isTeachingMode) {
    return null;
  }

  return (
    <div
      className={`space-y-2 p-3 bg-gray-800/50 rounded-lg border border-gray-700/50 ${className}`}
    >
      <div className="text-xs font-medium text-gray-400 flex items-center gap-2">
        <span className="text-purple-400">Teaching Mode</span>
        <span className="text-gray-600">|</span>
        <span>Context Composition</span>
        {isLoading && <span className="text-gray-500 animate-pulse">Loading...</span>}
        {!isLoading && breakdown && (
          <>
            <span className="text-gray-600">|</span>
            <span className="text-gray-500 capitalize">{strategy}</span>
            {hasSummary && <span className="text-blue-400 text-[10px]">• Summarized</span>}
          </>
        )}
      </div>

      {/* Stacked bar */}
      <div className="h-3 flex rounded-full overflow-hidden">
        {displaySegments.map((segment, i) => (
          <motion.div
            key={segment.name}
            className={`${segment.color} first:rounded-l-full last:rounded-r-full`}
            initial={{ width: 0 }}
            animate={{ width: `${(segment.tokens / totalTokens) * 100}%` }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
            title={`${segment.name}: ${formatTokens(segment.tokens)} tokens - ${segment.description}`}
          />
        ))}
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 gap-1 text-[10px]">
        {displaySegments.map((segment) => (
          <div key={segment.name} className="flex items-center gap-1.5" title={segment.description}>
            <div className={`w-2 h-2 rounded-full ${segment.color}`} />
            <span className="text-gray-400">
              {segment.name}: <span className="text-gray-500">{formatTokens(segment.tokens)}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ContextGauge;
