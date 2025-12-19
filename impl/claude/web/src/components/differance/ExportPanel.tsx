/**
 * ExportPanel — Export & Share for Differance DevEx
 *
 * Export traces and sessions in various formats.
 * "Generative, Not Archival": Export should answer "What should I do next?"
 *
 * Features:
 * - JSON export (machine-readable, for replay)
 * - Markdown export (human-readable, ADR-style)
 * - Shareable "why?" snapshots (single trace explanation)
 * - Session summary export (decision timeline)
 *
 * Design Principles (from differance-devex-enlightenment.md):
 * - Trace-as-documentation: Institutional knowledge preservation
 * - Shareability: Easy to share with colleagues
 * - Living Earth aesthetic
 *
 * @see spec/protocols/differance.md
 * @see plans/differance-devex-enlightenment.md - Phase 7E
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Download,
  FileJson,
  FileText,
  Share2,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Clock,
  GitBranch,
  Flag,
  ExternalLink,
} from 'lucide-react';
import { EARTH, GREEN, GLOW } from '@/constants/livingEarth';
import type { RecordingSession } from './RecordingControls';
import type { WhyResponse, AtResponse, TracePreview } from '@/hooks/useDifferanceQuery';

// =============================================================================
// Types
// =============================================================================

export type ExportFormat = 'json' | 'markdown' | 'adr';

export interface ExportPanelProps {
  /** Session to export (if any) */
  session?: RecordingSession | null;
  /** Selected trace to export (if any) */
  selectedTrace?: AtResponse | null;
  /** Why response for the selected trace */
  whyResponse?: WhyResponse | null;
  /** Recent traces to include in export */
  recentTraces?: TracePreview[];
  /** Callback when export is initiated */
  onExport?: (format: ExportFormat, content: string) => void;
  /** Compact mode */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

export interface ExportedSession {
  version: '1.0';
  exported_at: string;
  session: {
    id: string;
    name: string;
    start_time: string;
    end_time?: string;
    duration_seconds: number;
    trace_count: number;
    ghost_count: number;
    decision_markers: Array<{
      id: string;
      timestamp: string;
      label: string;
    }>;
  };
  traces?: TracePreview[];
}

export interface ExportedTrace {
  version: '1.0';
  exported_at: string;
  trace: AtResponse;
  why?: WhyResponse;
}

// =============================================================================
// Export Generators
// =============================================================================

function generateSessionJson(session: RecordingSession, traces?: TracePreview[]): string {
  const exportData: ExportedSession = {
    version: '1.0',
    exported_at: new Date().toISOString(),
    session: {
      id: session.id,
      name: session.name,
      start_time: session.startTime.toISOString(),
      end_time: session.endTime?.toISOString(),
      duration_seconds: Math.floor(
        ((session.endTime?.getTime() || Date.now()) - session.startTime.getTime()) / 1000
      ),
      trace_count: session.traceCount,
      ghost_count: session.ghostCount,
      decision_markers: session.decisionMarkers.map((m) => ({
        id: m.id,
        timestamp: m.timestamp.toISOString(),
        label: m.label,
      })),
    },
    traces,
  };

  return JSON.stringify(exportData, null, 2);
}

function generateTraceJson(trace: AtResponse, why?: WhyResponse): string {
  const exportData: ExportedTrace = {
    version: '1.0',
    exported_at: new Date().toISOString(),
    trace,
    why,
  };

  return JSON.stringify(exportData, null, 2);
}

function generateSessionMarkdown(session: RecordingSession, traces?: TracePreview[]): string {
  const duration = formatDuration(session.startTime, session.endTime || new Date());

  let md = `# Session: ${session.name}\n\n`;
  md += `**Recorded**: ${session.startTime.toLocaleString()}\n`;
  md += `**Duration**: ${duration}\n`;
  md += `**Traces**: ${session.traceCount} | **Ghosts**: ${session.ghostCount}\n\n`;

  // Decision markers
  if (session.decisionMarkers.length > 0) {
    md += `## Decision Points\n\n`;
    session.decisionMarkers.forEach((marker, i) => {
      const elapsed = formatDuration(session.startTime, marker.timestamp);
      md += `${i + 1}. **${marker.label}** (at ${elapsed})\n`;
    });
    md += '\n';
  }

  // Traces summary
  if (traces && traces.length > 0) {
    md += `## Trace Timeline\n\n`;
    md += `| Time | Operation | Context | Ghosts |\n`;
    md += `|------|-----------|---------|--------|\n`;
    traces.forEach((t) => {
      const time = new Date(t.timestamp).toLocaleTimeString();
      md += `| ${time} | \`${t.operation}\` | ${t.context || '-'} | ${t.ghost_count} |\n`;
    });
    md += '\n';
  }

  md += `---\n`;
  md += `*Exported from kgents Differance Engine*\n`;

  return md;
}

function generateTraceMarkdown(trace: AtResponse, why?: WhyResponse): string {
  let md = `# Trace: ${trace.operation}\n\n`;
  md += `**ID**: \`${trace.trace_id}\`\n`;
  md += `**Time**: ${new Date(trace.timestamp).toLocaleString()}\n`;
  md += `**Context**: ${trace.context || 'No context recorded'}\n\n`;

  // Inputs
  if (trace.inputs.length > 0) {
    md += `## Inputs\n\n`;
    trace.inputs.forEach((input) => {
      md += `- \`${input}\`\n`;
    });
    md += '\n';
  }

  // Output
  md += `## Output\n\n`;
  md += `\`\`\`json\n${JSON.stringify(trace.output, null, 2)}\n\`\`\`\n\n`;

  // Why explanation
  if (why?.summary) {
    md += `## Why This Path?\n\n`;
    md += `> ${why.summary}\n\n`;
    md += `- Decisions made: ${why.decisions_made}\n`;
    md += `- Alternatives considered: ${why.alternatives_considered}\n\n`;
  }

  // Alternatives (ghosts)
  if (trace.alternatives.length > 0) {
    md += `## Roads Not Taken\n\n`;
    trace.alternatives.forEach((alt, i) => {
      md += `### ${i + 1}. ${alt.operation}\n`;
      md += `- **Reason rejected**: ${alt.reason}\n`;
      md += `- **Explorable**: ${alt.could_revisit ? 'Yes' : 'No'}\n`;
      if (alt.inputs.length > 0) {
        md += `- **Inputs**: ${alt.inputs.join(', ')}\n`;
      }
      md += '\n';
    });
  }

  md += `---\n`;
  md += `*Exported from kgents Differance Engine*\n`;

  return md;
}

function generateAdr(trace: AtResponse, why?: WhyResponse): string {
  const date = new Date().toISOString().split('T')[0];
  const title = trace.operation.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  let adr = `# ADR: ${title}\n\n`;
  adr += `**Date**: ${date}\n`;
  adr += `**Status**: Recorded\n`;
  adr += `**Context**: ${trace.context || 'System decision during operation'}\n\n`;

  adr += `## Decision\n\n`;
  adr += `The system chose to execute \`${trace.operation}\` with inputs:\n`;
  trace.inputs.forEach((input) => {
    adr += `- \`${input}\`\n`;
  });
  adr += '\n';

  if (why?.summary) {
    adr += `## Rationale\n\n`;
    adr += `${why.summary}\n\n`;
  }

  if (trace.alternatives.length > 0) {
    adr += `## Alternatives Considered\n\n`;
    trace.alternatives.forEach((alt, i) => {
      adr += `### ${i + 1}. ${alt.operation}\n`;
      adr += `**Rejected because**: ${alt.reason}\n\n`;
    });
  }

  adr += `## Consequences\n\n`;
  adr += `**Output**: \n\`\`\`json\n${JSON.stringify(trace.output, null, 2)}\n\`\`\`\n\n`;

  adr += `---\n`;
  adr += `*Auto-generated from Differance trace \`${trace.trace_id}\`*\n`;

  return adr;
}

// =============================================================================
// Helper Functions
// =============================================================================

function formatDuration(start: Date, end: Date): string {
  const diffMs = end.getTime() - start.getTime();
  const seconds = Math.floor(diffMs / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
}

async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

function downloadFile(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// =============================================================================
// Export Button
// =============================================================================

interface ExportButtonProps {
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  compact?: boolean;
}

function ExportButton({ label, icon, onClick, compact }: ExportButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors hover:brightness-110 ${
        compact ? 'text-xs' : 'text-sm'
      }`}
      style={{
        backgroundColor: `${GREEN.sage}20`,
        color: GREEN.sprout,
        border: `1px solid ${GREEN.sage}40`,
      }}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function ExportPanel({
  session,
  selectedTrace,
  whyResponse,
  recentTraces,
  onExport,
  compact = false,
  className = '',
}: ExportPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const hasSession = !!session;
  const hasTrace = !!selectedTrace;
  const hasContent = hasSession || hasTrace;

  const handleExportSessionJson = useCallback(() => {
    if (!session) return;
    const content = generateSessionJson(session, recentTraces);
    downloadFile(content, `session-${session.id}.json`, 'application/json');
    onExport?.('json', content);
  }, [session, recentTraces, onExport]);

  const handleExportSessionMarkdown = useCallback(() => {
    if (!session) return;
    const content = generateSessionMarkdown(session, recentTraces);
    downloadFile(content, `session-${session.id}.md`, 'text/markdown');
    onExport?.('markdown', content);
  }, [session, recentTraces, onExport]);

  const handleExportTraceJson = useCallback(() => {
    if (!selectedTrace) return;
    const content = generateTraceJson(selectedTrace, whyResponse ?? undefined);
    downloadFile(content, `trace-${selectedTrace.trace_id}.json`, 'application/json');
    onExport?.('json', content);
  }, [selectedTrace, whyResponse, onExport]);

  const handleExportTraceMarkdown = useCallback(() => {
    if (!selectedTrace) return;
    const content = generateTraceMarkdown(selectedTrace, whyResponse ?? undefined);
    downloadFile(content, `trace-${selectedTrace.trace_id}.md`, 'text/markdown');
    onExport?.('markdown', content);
  }, [selectedTrace, whyResponse, onExport]);

  const handleExportAdr = useCallback(() => {
    if (!selectedTrace) return;
    const content = generateAdr(selectedTrace, whyResponse ?? undefined);
    downloadFile(content, `adr-${selectedTrace.operation}.md`, 'text/markdown');
    onExport?.('adr', content);
  }, [selectedTrace, whyResponse, onExport]);

  const handleCopyWhySnapshot = useCallback(async () => {
    if (!whyResponse?.summary) return;

    const snapshot = `**Why did ${selectedTrace?.operation || 'this'} happen?**\n\n${whyResponse.summary}\n\nDecisions: ${whyResponse.decisions_made} | Alternatives: ${whyResponse.alternatives_considered}`;

    const success = await copyToClipboard(snapshot);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [selectedTrace, whyResponse]);

  if (!hasContent) {
    return (
      <div
        className={`rounded-xl p-4 text-center ${className}`}
        style={{ backgroundColor: `${EARTH.bark}40`, border: `1px solid ${EARTH.wood}` }}
      >
        <Download className="w-6 h-6 mx-auto mb-2" style={{ color: EARTH.clay }} />
        <p className="text-xs" style={{ color: EARTH.sand }}>
          Record a session or select a trace to export
        </p>
      </div>
    );
  }

  return (
    <div
      className={`rounded-xl overflow-hidden ${className}`}
      style={{
        backgroundColor: EARTH.soil,
        border: `1px solid ${EARTH.wood}`,
      }}
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full flex items-center justify-between ${compact ? 'px-3 py-2' : 'px-4 py-3'}`}
        style={{ backgroundColor: `${EARTH.bark}80` }}
      >
        <div className="flex items-center gap-2">
          <Download className={compact ? 'w-4 h-4' : 'w-5 h-5'} style={{ color: GREEN.sprout }} />
          <span
            className={`font-medium ${compact ? 'text-xs' : 'text-sm'}`}
            style={{ color: GLOW.lantern }}
          >
            Export & Share
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4" style={{ color: EARTH.sand }} />
        ) : (
          <ChevronDown className="w-4 h-4" style={{ color: EARTH.sand }} />
        )}
      </button>

      {/* Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div
              className={compact ? 'p-3' : 'p-4'}
              style={{ borderTop: `1px solid ${EARTH.wood}40` }}
            >
              {/* Session exports */}
              {hasSession && session && (
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="w-4 h-4" style={{ color: EARTH.clay }} />
                    <span className="text-xs font-medium" style={{ color: EARTH.sand }}>
                      Session: {session.name}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <ExportButton
                      label="JSON"
                      icon={<FileJson className="w-4 h-4" />}
                      onClick={handleExportSessionJson}
                      compact={compact}
                    />
                    <ExportButton
                      label="Markdown"
                      icon={<FileText className="w-4 h-4" />}
                      onClick={handleExportSessionMarkdown}
                      compact={compact}
                    />
                  </div>
                </div>
              )}

              {/* Trace exports */}
              {hasTrace && selectedTrace && (
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <GitBranch className="w-4 h-4" style={{ color: EARTH.clay }} />
                    <span className="text-xs font-medium" style={{ color: EARTH.sand }}>
                      Trace: {selectedTrace.operation}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <ExportButton
                      label="JSON"
                      icon={<FileJson className="w-4 h-4" />}
                      onClick={handleExportTraceJson}
                      compact={compact}
                    />
                    <ExportButton
                      label="Markdown"
                      icon={<FileText className="w-4 h-4" />}
                      onClick={handleExportTraceMarkdown}
                      compact={compact}
                    />
                    <ExportButton
                      label="ADR"
                      icon={<Flag className="w-4 h-4" />}
                      onClick={handleExportAdr}
                      compact={compact}
                    />
                  </div>
                </div>
              )}

              {/* Why snapshot (quick share) */}
              {whyResponse?.summary && (
                <div
                  className="rounded-lg p-3"
                  style={{
                    backgroundColor: `${GLOW.amber}10`,
                    border: `1px solid ${GLOW.amber}30`,
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-1.5">
                      <Share2 className="w-3.5 h-3.5" style={{ color: GLOW.amber }} />
                      <span className="text-xs font-medium" style={{ color: GLOW.amber }}>
                        Quick Share: "Why?"
                      </span>
                    </div>
                    <button
                      onClick={handleCopyWhySnapshot}
                      className="flex items-center gap-1 text-[10px] px-2 py-1 rounded transition-colors"
                      style={{
                        backgroundColor: copied ? `${GREEN.sage}30` : `${EARTH.bark}60`,
                        color: copied ? GREEN.sprout : EARTH.sand,
                      }}
                    >
                      {copied ? (
                        <>
                          <Check className="w-3 h-3" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-xs italic" style={{ color: GLOW.honey }}>
                    "{whyResponse.summary.slice(0, 150)}
                    {whyResponse.summary.length > 150 && '...'}"
                  </p>
                </div>
              )}

              {/* Export tip */}
              <div
                className="flex items-start gap-2 mt-3 px-2 py-1.5 rounded text-[10px]"
                style={{ backgroundColor: `${GREEN.moss}30`, color: GREEN.sprout }}
              >
                <ExternalLink className="w-3 h-3 flex-shrink-0 mt-0.5" />
                <span>
                  Tip: ADR format creates Architecture Decision Records — great for documenting why
                  certain paths were chosen.
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default ExportPanel;
