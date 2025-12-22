/**
 * ObserverDrawer - Top-Fixed Observer Context Panel
 *
 * The Observer Drawer shows who is observing and their context.
 * It is always present, never hidden, and affects all projections.
 *
 * States:
 * - Collapsed (40px): Summary view with archetype, capabilities, tier
 * - Expanded (280px): Full umwelt, recent traces, controls
 *
 * Per os-shell.md:
 * - Always present, never hidden
 * - Collapsed by default, expand on click
 * - Changes to observer immediately affect all projections
 * - Shows recent traces for devex visibility
 *
 * Sheaf condition: nav.top = observer.bottom
 * NavigationTree reads observerDrawerExpanded via context to set topOffset.
 *
 * @see spec/protocols/os-shell.md
 * @see docs/creative/visual-system.md
 * @see docs/skills/elastic-ui-patterns.md (Fixed Top Panel Pattern)
 */

import { useCallback, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  ChevronDown,
  ChevronUp,
  User,
  Shield,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Settings,
  RotateCcw,
  Download,
} from 'lucide-react';
import { useShell } from './ShellProvider';
import type { Trace, ObserverArchetype, Capability } from './types';
import { useMotionPreferences } from '../components/joy/useMotionPreferences';
import { GLASS_EFFECT, Z_INDEX_LAYERS, TOP_PANEL_HEIGHTS } from '../components/elastic';

// =============================================================================
// Types
// =============================================================================

export interface ObserverDrawerProps {
  /** Default expanded state (default: false) */
  defaultExpanded?: boolean;
  /** Show recent traces (default: true) */
  showTraces?: boolean;
  /** Maximum traces to show (default: 5) */
  traceLimit?: number;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

/** Archetype display names and descriptions */
const ARCHETYPE_INFO: Record<ObserverArchetype, { label: string; description: string }> = {
  developer: { label: 'Developer', description: 'Building and debugging' },
  architect: { label: 'Architect', description: 'Designing systems' },
  operator: { label: 'Operator', description: 'Running and monitoring' },
  reviewer: { label: 'Reviewer', description: 'Evaluating quality' },
  newcomer: { label: 'Newcomer', description: 'Learning the system' },
  guest: { label: 'Guest', description: 'Limited access' },
  technical: { label: 'Technical', description: 'Deep technical focus' },
  casual: { label: 'Casual', description: 'Light exploration' },
  security: { label: 'Security', description: 'Audit and compliance' },
  creative: { label: 'Creative', description: 'Artistic exploration' },
  strategic: { label: 'Strategic', description: 'High-level planning' },
  tactical: { label: 'Tactical', description: 'Immediate action' },
  reflective: { label: 'Reflective', description: 'Deep contemplation' },
};

/** Capability display info */
const CAPABILITY_INFO: Record<Capability, { label: string; color: string }> = {
  read: { label: 'Read', color: 'text-cyan-400' },
  write: { label: 'Write', color: 'text-green-400' },
  admin: { label: 'Admin', color: 'text-amber-400' },
  stream: { label: 'Stream', color: 'text-violet-400' },
  delete: { label: 'Delete', color: 'text-red-400' },
};

// =============================================================================
// Subcomponents
// =============================================================================

/** Collapsed summary content - rendered inside the clickable button area */
function CollapsedContent({
  archetype,
  capabilities,
}: {
  archetype: ObserverArchetype;
  capabilities: Set<Capability>;
}) {
  const archetypeInfo = ARCHETYPE_INFO[archetype];
  const capArray = Array.from(capabilities);

  return (
    <div className="flex items-center gap-4 px-4">
      {/* Observer icon and archetype */}
      <div className="flex items-center gap-2">
        <User className="w-4 h-4 text-steel-zinc" />
        <span className="text-sm font-medium text-white">{archetypeInfo.label}</span>
      </div>

      {/* Capabilities badges */}
      <div className="flex items-center gap-1">
        {capArray.map((cap) => (
          <span
            key={cap}
            className={`text-xs px-1.5 py-0.5 rounded bg-steel-slate/50 ${CAPABILITY_INFO[cap].color}`}
          >
            {CAPABILITY_INFO[cap].label}
          </span>
        ))}
      </div>
    </div>
  );
}

/** Trace status icon */
function TraceStatusIcon({ status }: { status: Trace['status'] }) {
  switch (status) {
    case 'success':
      return <CheckCircle className="w-3 h-3 text-green-400" />;
    case 'error':
      return <XCircle className="w-3 h-3 text-red-400" />;
    case 'refused':
      return <AlertCircle className="w-3 h-3 text-amber-400" />;
    case 'pending':
      return <Clock className="w-3 h-3 text-steel-zinc animate-pulse" />;
    default:
      return null;
  }
}

/** Format trace timestamp */
function formatTime(date: Date): string {
  return date.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

/** Format duration */
function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

/** Recent traces table */
function TracesTable({ traces, limit }: { traces: Trace[]; limit: number }) {
  const displayTraces = traces.slice(0, limit);

  if (displayTraces.length === 0) {
    return <div className="text-center py-4 text-steel-zinc text-sm">No recent traces</div>;
  }

  return (
    <div className="overflow-auto max-h-24">
      <table className="w-full text-xs">
        <thead className="text-steel-zinc border-b border-steel-gunmetal/50">
          <tr>
            <th className="text-left py-1 px-2 font-medium">Time</th>
            <th className="text-left py-1 px-2 font-medium">Path</th>
            <th className="text-right py-1 px-2 font-medium">Duration</th>
            <th className="text-center py-1 px-2 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          {displayTraces.map((trace) => (
            <tr
              key={trace.id}
              className="border-b border-steel-gunmetal/30 hover:bg-steel-slate/20"
            >
              <td className="py-1 px-2 text-steel-zinc font-mono">{formatTime(trace.timestamp)}</td>
              <td className="py-1 px-2 text-cyan-400 font-mono truncate max-w-48">
                {trace.path}.{trace.aspect}
              </td>
              <td className="py-1 px-2 text-right text-steel-zinc font-mono">
                {formatDuration(trace.duration)}
              </td>
              <td className="py-1 px-2 text-center">
                <TraceStatusIcon status={trace.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Archetype selector */
function ArchetypeSelector({
  current,
  onChange,
}: {
  current: ObserverArchetype;
  onChange: (archetype: ObserverArchetype) => void;
}) {
  return (
    <select
      value={current}
      onChange={(e) => onChange(e.target.value as ObserverArchetype)}
      className="bg-steel-slate text-white text-sm rounded px-2 py-1 border border-steel-gunmetal focus:border-cyan-500 focus:outline-none"
    >
      {Object.entries(ARCHETYPE_INFO).map(([key, { label }]) => (
        <option key={key} value={key}>
          {label}
        </option>
      ))}
    </select>
  );
}

/** Expanded view content */
function ExpandedContent({
  observer,
  traces,
  traceLimit,
  onArchetypeChange,
  onClearTraces,
  onCollapse,
}: {
  observer: {
    archetype: ObserverArchetype;
    capabilities: Set<Capability>;
    sessionId: string;
    userId?: string;
    tenantId?: string;
    intent?: string;
  };
  traces: Trace[];
  traceLimit: number;
  onArchetypeChange: (archetype: ObserverArchetype) => void;
  onClearTraces: () => void;
  onCollapse: () => void;
}) {
  const archetypeInfo = ARCHETYPE_INFO[observer.archetype];
  const capArray = Array.from(observer.capabilities);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-steel-gunmetal/50 shrink-0">
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-cyan-400" />
          <span className="text-sm font-semibold text-white">Observer Umwelt</span>
        </div>
        <button
          onClick={onCollapse}
          className="p-1 hover:bg-steel-slate rounded transition-colors"
          aria-label="Collapse observer drawer"
        >
          <ChevronUp className="w-4 h-4 text-steel-zinc" />
        </button>
      </div>

      {/* Content grid */}
      <div className="px-4 py-3 grid grid-cols-2 gap-4 flex-1 overflow-auto">
        {/* Left column: Observer info */}
        <div className="space-y-3">
          {/* Archetype */}
          <div>
            <label className="text-xs text-steel-zinc block mb-1">Archetype</label>
            <ArchetypeSelector current={observer.archetype} onChange={onArchetypeChange} />
            <p className="text-xs text-steel-zinc mt-1">{archetypeInfo.description}</p>
          </div>

          {/* Session info */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <label className="text-steel-zinc block">Session</label>
              <span className="text-steel-zinc font-mono">{observer.sessionId.slice(0, 12)}</span>
            </div>
            {observer.tenantId && (
              <div>
                <label className="text-steel-zinc block">Tenant</label>
                <span className="text-steel-zinc font-mono">{observer.tenantId}</span>
              </div>
            )}
          </div>

          {/* Capabilities */}
          <div>
            <label className="text-xs text-steel-zinc block mb-1">Capabilities</label>
            <div className="flex flex-wrap gap-1">
              {capArray.map((cap) => (
                <span
                  key={cap}
                  className={`text-xs px-2 py-0.5 rounded-full bg-steel-slate/70 ${CAPABILITY_INFO[cap].color}`}
                >
                  {CAPABILITY_INFO[cap].label}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Right column: Intent and Traces */}
        <div className="space-y-3">
          {/* Intent */}
          {observer.intent && (
            <div>
              <label className="text-xs text-steel-zinc block mb-1">Intent</label>
              <p className="text-sm text-steel-zinc">{observer.intent}</p>
            </div>
          )}

          {/* Recent traces */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs text-steel-zinc">Recent Traces</label>
              <button
                onClick={onClearTraces}
                className="text-xs text-steel-zinc hover:text-steel-zinc flex items-center gap-1"
                title="Clear traces"
              >
                <RotateCcw className="w-3 h-3" />
                Clear
              </button>
            </div>
            <TracesTable traces={traces} limit={traceLimit} />
          </div>
        </div>
      </div>

      {/* Footer actions */}
      <div className="px-4 py-2 border-t border-steel-gunmetal/50 flex items-center gap-2 shrink-0">
        <button className="text-xs px-2 py-1 bg-steel-slate hover:bg-steel-gunmetal rounded text-steel-zinc flex items-center gap-1 transition-colors">
          <Settings className="w-3 h-3" />
          Edit Observer
        </button>
        <button className="text-xs px-2 py-1 bg-steel-slate hover:bg-steel-gunmetal rounded text-steel-zinc flex items-center gap-1 transition-colors">
          <Download className="w-3 h-3" />
          Export Session
        </button>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Observer Drawer - Top-fixed collapsible panel showing observer context.
 *
 * Uses a single animated container to prevent double-collapse jank.
 * The height transition is controlled by framer-motion while content
 * fades in/out without waiting for exit animations.
 *
 * @example
 * ```tsx
 * // In Shell layout
 * <ObserverDrawer />
 *
 * // With custom options
 * <ObserverDrawer
 *   defaultExpanded={false}
 *   showTraces={true}
 *   traceLimit={5}
 * />
 * ```
 */
export function ObserverDrawer({
  defaultExpanded = false,
  showTraces = true,
  traceLimit = 5,
  className = '',
}: ObserverDrawerProps) {
  const {
    observer,
    setArchetype,
    traces,
    clearTraces,
    observerDrawerExpanded,
    setObserverDrawerExpanded,
    density,
    // Use animated height from shell context (temporal coherence)
    observerHeight,
    isAnimating,
  } = useShell();
  const { shouldAnimate } = useMotionPreferences();

  // Use shell state
  const isExpanded = observerDrawerExpanded;
  const setExpanded = setObserverDrawerExpanded;

  // Track if we've initialized from defaultExpanded
  const hasInitialized = useRef(false);

  // Initialize from defaultExpanded if shell state is false (once)
  useEffect(() => {
    if (!hasInitialized.current && defaultExpanded && !observerDrawerExpanded) {
      setObserverDrawerExpanded(true);
      hasInitialized.current = true;
    }
  }, [defaultExpanded, observerDrawerExpanded, setObserverDrawerExpanded]);

  const handleExpand = useCallback(() => setExpanded(true), [setExpanded]);
  const handleCollapse = useCallback(() => setExpanded(false), [setExpanded]);

  // Use animated height from context (coordinated with other shell elements)
  const currentHeight = observerHeight;

  // Glass effect from elastic primitives
  const glassStyles = GLASS_EFFECT.standard;

  // Compact density: Mobile layout with modal expansion
  if (density === 'compact') {
    return (
      <div
        className={`fixed top-0 left-0 right-0 ${className}`}
        style={{ zIndex: Z_INDEX_LAYERS.modal }}
      >
        {/* Always-visible collapsed bar */}
        <button
          onClick={handleExpand}
          className={`
            w-full h-10 flex items-center justify-between
            ${glassStyles.background} ${glassStyles.blur}
            border-b border-steel-gunmetal/50
            hover:bg-steel-slate/30 transition-colors
          `}
          aria-label="Expand observer drawer"
        >
          <CollapsedContent archetype={observer.archetype} capabilities={observer.capabilities} />
          <div className="px-3">
            <ChevronDown className="w-4 h-4 text-steel-zinc" />
          </div>
        </button>

        {/* Expanded modal overlay */}
        {isExpanded && (
          <>
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/50 -z-10" onClick={handleCollapse} />
            {/* Expanded content */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: shouldAnimate ? 0.2 : 0 }}
              className={`
                absolute top-10 left-0 right-0
                ${glassStyles.background} ${glassStyles.blur}
                border-b border-steel-gunmetal/50 shadow-xl
              `}
              style={{ height: TOP_PANEL_HEIGHTS.expanded - TOP_PANEL_HEIGHTS.collapsed }}
            >
              <ExpandedContent
                observer={observer}
                traces={showTraces ? traces : []}
                traceLimit={traceLimit}
                onArchetypeChange={setArchetype}
                onClearTraces={clearTraces}
                onCollapse={handleCollapse}
              />
            </motion.div>
          </>
        )}
      </div>
    );
  }

  // Desktop/tablet: Use coordinated height from shell context
  // Animation is now controlled by useShellAnimation hook for temporal coherence
  // with NavigationTree and Terminal
  return (
    <div
      className={`
        fixed top-0 left-0 right-0
        ${glassStyles.background} ${glassStyles.blur}
        border-b border-steel-gunmetal/50
        overflow-hidden
        ${className}
      `}
      style={{
        zIndex: Z_INDEX_LAYERS.panel,
        height: currentHeight,
        // Disable CSS transition when JS is animating
        transition: isAnimating ? 'none' : 'height 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
    >
      {isExpanded ? (
        <ExpandedContent
          observer={observer}
          traces={showTraces ? traces : []}
          traceLimit={traceLimit}
          onArchetypeChange={setArchetype}
          onClearTraces={clearTraces}
          onCollapse={handleCollapse}
        />
      ) : (
        <button
          onClick={handleExpand}
          className="w-full h-full flex items-center justify-between hover:bg-steel-slate/30 transition-colors"
          aria-label="Expand observer drawer"
        >
          <CollapsedContent archetype={observer.archetype} capabilities={observer.capabilities} />
          <div className="px-3 h-10 flex items-center">
            <ChevronDown className="w-4 h-4 text-steel-zinc" />
          </div>
        </button>
      )}
    </div>
  );
}

export default ObserverDrawer;
