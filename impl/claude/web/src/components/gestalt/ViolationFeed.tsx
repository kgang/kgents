/**
 * ViolationFeed - Streaming violation alerts
 *
 * Displays architecture violations with severity indicators and
 * source → target paths. Part of Gestalt2D 2D Renaissance.
 *
 * @see spec/protocols/2d-renaissance.md - §4.1 Gestalt2D
 */

import { useState, useMemo } from 'react';
import { AlertTriangle, ChevronDown, ChevronRight, ArrowRight, CheckCircle } from 'lucide-react';
import type { WorldCodebaseTopologyResponse } from '@/api/types';

// =============================================================================
// Types
// =============================================================================

type CodebaseLink = WorldCodebaseTopologyResponse['links'][number];

export interface ViolationFeedProps {
  /** All links from topology, violations will be filtered */
  violations: CodebaseLink[];
  /** Maximum violations to display */
  maxDisplay?: number;
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

const SEVERITY_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  critical: { color: '#EF4444', bg: '#7F1D1D', label: 'Critical' },
  high: { color: '#F97316', bg: '#7C2D12', label: 'High' },
  medium: { color: '#EAB308', bg: '#713F12', label: 'Medium' },
  low: { color: '#6B7280', bg: '#374151', label: 'Low' },
  unknown: { color: '#6B7280', bg: '#374151', label: 'Unknown' },
};

// =============================================================================
// Component
// =============================================================================

export function ViolationFeed({
  violations,
  maxDisplay = 10,
  compact = false,
  className = '',
}: ViolationFeedProps) {
  const [expanded, setExpanded] = useState(false);

  // Sort by severity (critical first)
  const sortedViolations = useMemo(() => {
    const severityOrder = ['critical', 'high', 'medium', 'low', 'unknown', null];
    return [...violations]
      .filter((l) => l.is_violation)
      .sort((a, b) => {
        const aIdx = severityOrder.indexOf(a.violation_severity);
        const bIdx = severityOrder.indexOf(b.violation_severity);
        return aIdx - bIdx;
      });
  }, [violations]);

  // Limit display
  const displayLimit = expanded
    ? sortedViolations.length
    : Math.min(maxDisplay, sortedViolations.length);
  const displayedViolations = sortedViolations.slice(0, displayLimit);
  const hasMore = sortedViolations.length > maxDisplay;

  // No violations - healthy state
  if (sortedViolations.length === 0) {
    return (
      <div
        className={`flex items-center gap-2 text-green-400 ${compact ? 'text-sm' : 'text-base'} ${className}`}
      >
        <CheckCircle className="w-4 h-4" />
        <span>No architecture violations detected</span>
      </div>
    );
  }

  return (
    <div className={`bg-[#2a2a2a] rounded-lg overflow-hidden border border-gray-700 ${className}`}>
      {/* Header */}
      <button
        onClick={() => setExpanded((prev) => !prev)}
        className="w-full flex items-center justify-between p-3 hover:bg-[#333] transition-colors"
      >
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <span className={`font-medium text-white ${compact ? 'text-sm' : 'text-base'}`}>
            Violations
          </span>
          <span className={`text-amber-400 ${compact ? 'text-xs' : 'text-sm'}`}>
            {sortedViolations.length}
          </span>
        </div>
        {hasMore &&
          (expanded ? (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-400" />
          ))}
      </button>

      {/* Violation List */}
      <div className="px-3 pb-3 space-y-2">
        {displayedViolations.map((violation, idx) => (
          <ViolationItem
            key={`${violation.source}-${violation.target}-${idx}`}
            violation={violation}
            compact={compact}
          />
        ))}

        {/* Show more button */}
        {hasMore && !expanded && (
          <button
            onClick={() => setExpanded(true)}
            className="w-full text-center text-sm text-gray-500 hover:text-gray-300 py-1"
          >
            Show {sortedViolations.length - maxDisplay} more violations
          </button>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Sub-Components
// =============================================================================

interface ViolationItemProps {
  violation: CodebaseLink;
  compact: boolean;
}

function ViolationItem({ violation, compact }: ViolationItemProps) {
  const severity = violation.violation_severity || 'unknown';
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.unknown;

  // Extract module names from full paths
  const sourceName = extractModuleName(violation.source);
  const targetName = extractModuleName(violation.target);

  return (
    <div
      className={`
        flex items-center gap-2 px-3 py-2 rounded-lg bg-[#333]
        border-l-2 transition-all hover:bg-[#3a3a3a]
        ${compact ? 'text-xs' : 'text-sm'}
      `}
      style={{ borderLeftColor: config.color }}
    >
      {/* Severity Badge */}
      {!compact && (
        <span
          className="text-[10px] font-medium px-1.5 py-0.5 rounded uppercase"
          style={{ color: config.color, backgroundColor: config.bg }}
        >
          {severity}
        </span>
      )}

      {/* Source → Target */}
      <div className="flex-1 flex items-center gap-1 overflow-hidden">
        <span className="text-amber-400 truncate" title={violation.source}>
          {sourceName}
        </span>
        <ArrowRight className="w-3 h-3 text-gray-500 flex-shrink-0" />
        <span className="text-amber-400 truncate" title={violation.target}>
          {targetName}
        </span>
      </div>

      {/* Import type */}
      <span className="text-gray-500 text-[10px] flex-shrink-0">{violation.import_type}</span>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function extractModuleName(fullPath: string): string {
  // Get last segment of dotted path
  const parts = fullPath.split('.');
  if (parts.length <= 2) return fullPath;
  return parts.slice(-2).join('.');
}

export default ViolationFeed;
