/**
 * ExecutionMonitor: Live status display during pipeline execution.
 *
 * Shows:
 * - Overall progress
 * - Per-node status
 * - Execution time
 * - Error details
 */

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

export type NodeExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

export interface NodeExecution {
  nodeId: string;
  status: NodeExecutionStatus;
  startedAt?: Date;
  completedAt?: Date;
  result?: unknown;
  error?: string;
}

export interface ExecutionStatus {
  pipelineId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  nodes: NodeExecution[];
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
}

/** Simplified node info for display in the monitor */
export interface MonitorNodeInfo {
  id: string;
  label: string;
}

export interface ExecutionMonitorProps {
  status: ExecutionStatus;
  nodes: MonitorNodeInfo[];
  onClose?: () => void;
  className?: string;
}

export function ExecutionMonitor({
  status,
  nodes,
  onClose,
  className,
}: ExecutionMonitorProps) {
  const [elapsed, setElapsed] = useState(0);

  // Update elapsed time
  useEffect(() => {
    if (status.status !== 'running' || !status.startedAt) return;

    const interval = setInterval(() => {
      setElapsed(Date.now() - status.startedAt!.getTime());
    }, 100);

    return () => clearInterval(interval);
  }, [status.status, status.startedAt]);

  // Calculate progress
  const completedCount = status.nodes.filter(
    (n) => n.status === 'completed' || n.status === 'failed'
  ).length;
  const progress = (completedCount / status.nodes.length) * 100;

  // Get status display
  const statusConfig = getStatusConfig(status.status);

  return (
    <div
      className={cn(
        'w-80 border-l border-town-accent/30 bg-town-surface/30 flex flex-col',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-town-accent/20">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold">Execution</h3>
          {onClose && status.status !== 'running' && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-town-accent/20 rounded transition-colors"
            >
              ✕
            </button>
          )}
        </div>

        {/* Status badge */}
        <div className="flex items-center gap-2">
          <div
            className={cn(
              'px-2 py-1 rounded text-xs font-medium',
              statusConfig.bgColor,
              statusConfig.textColor
            )}
          >
            {statusConfig.icon} {statusConfig.label}
          </div>
          {status.status === 'running' && (
            <span className="text-xs text-gray-400">
              {formatElapsed(elapsed)}
            </span>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="px-4 py-3 border-b border-town-accent/20">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
          <span>Progress</span>
          <span>
            {completedCount}/{status.nodes.length}
          </span>
        </div>
        <div className="h-2 bg-town-surface rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full transition-all duration-300',
              status.status === 'failed'
                ? 'bg-red-500'
                : status.status === 'completed'
                  ? 'bg-green-500'
                  : 'bg-town-highlight'
            )}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Node list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {status.nodes.map((nodeExec) => {
          const node = nodes.find((n) => n.id === nodeExec.nodeId);
          return (
            <NodeExecutionCard
              key={nodeExec.nodeId}
              execution={nodeExec}
              node={node}
            />
          );
        })}
      </div>

      {/* Error display */}
      {status.error && (
        <div className="p-4 border-t border-red-500/20 bg-red-500/10">
          <h4 className="text-sm font-medium text-red-400 mb-1">Error</h4>
          <p className="text-xs text-red-300">{status.error}</p>
        </div>
      )}

      {/* Summary (completed) */}
      {status.status === 'completed' && (
        <div className="p-4 border-t border-town-accent/20">
          <h4 className="text-sm font-medium mb-2">Summary</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <SummaryStat
              label="Duration"
              value={formatDuration(status.startedAt, status.completedAt)}
            />
            <SummaryStat label="Nodes" value={`${completedCount} completed`} />
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface NodeExecutionCardProps {
  execution: NodeExecution;
  node?: MonitorNodeInfo;
}

function NodeExecutionCard({ execution, node }: NodeExecutionCardProps) {
  const statusConfig = getNodeStatusConfig(execution.status);

  return (
    <div
      className={cn(
        'p-3 rounded-lg border transition-all',
        execution.status === 'running' && 'ring-2 ring-town-highlight/50',
        statusConfig.borderColor,
        'bg-town-surface/30'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={statusConfig.textColor}>{statusConfig.icon}</span>
          <span className="font-medium text-sm">{node?.label || execution.nodeId}</span>
        </div>
        <span className={cn('text-xs', statusConfig.textColor)}>
          {statusConfig.label}
        </span>
      </div>

      {/* Duration for completed nodes */}
      {execution.completedAt && execution.startedAt && (
        <div className="mt-1 text-xs text-gray-500">
          {formatDuration(execution.startedAt, execution.completedAt)}
        </div>
      )}

      {/* Error */}
      {execution.error && (
        <div className="mt-2 text-xs text-red-400 bg-red-500/10 p-2 rounded">
          {execution.error}
        </div>
      )}

      {/* Running animation */}
      {execution.status === 'running' && (
        <div className="mt-2 flex gap-1">
          <div className="w-2 h-2 rounded-full bg-town-highlight animate-pulse" />
          <div
            className="w-2 h-2 rounded-full bg-town-highlight animate-pulse"
            style={{ animationDelay: '0.2s' }}
          />
          <div
            className="w-2 h-2 rounded-full bg-town-highlight animate-pulse"
            style={{ animationDelay: '0.4s' }}
          />
        </div>
      )}
    </div>
  );
}

interface SummaryStatProps {
  label: string;
  value: string;
}

function SummaryStat({ label, value }: SummaryStatProps) {
  return (
    <div className="bg-town-surface/30 rounded p-2">
      <div className="text-gray-500">{label}</div>
      <div className="font-medium">{value}</div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getStatusConfig(status: ExecutionStatus['status']) {
  switch (status) {
    case 'pending':
      return {
        icon: '⏳',
        label: 'Pending',
        bgColor: 'bg-gray-500/20',
        textColor: 'text-gray-400',
      };
    case 'running':
      return {
        icon: '⚡',
        label: 'Running',
        bgColor: 'bg-amber-500/20',
        textColor: 'text-amber-400',
      };
    case 'completed':
      return {
        icon: '✓',
        label: 'Completed',
        bgColor: 'bg-green-500/20',
        textColor: 'text-green-400',
      };
    case 'failed':
      return {
        icon: '✗',
        label: 'Failed',
        bgColor: 'bg-red-500/20',
        textColor: 'text-red-400',
      };
  }
}

function getNodeStatusConfig(status: NodeExecutionStatus) {
  switch (status) {
    case 'pending':
      return {
        icon: '○',
        label: 'Pending',
        textColor: 'text-gray-500',
        borderColor: 'border-gray-500/30',
      };
    case 'running':
      return {
        icon: '◉',
        label: 'Running',
        textColor: 'text-amber-400',
        borderColor: 'border-amber-500/50',
      };
    case 'completed':
      return {
        icon: '✓',
        label: 'Done',
        textColor: 'text-green-400',
        borderColor: 'border-green-500/30',
      };
    case 'failed':
      return {
        icon: '✗',
        label: 'Failed',
        textColor: 'text-red-400',
        borderColor: 'border-red-500/50',
      };
    case 'skipped':
      return {
        icon: '⊘',
        label: 'Skipped',
        textColor: 'text-gray-500',
        borderColor: 'border-gray-500/30',
      };
  }
}

function formatElapsed(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function formatDuration(start?: Date, end?: Date): string {
  if (!start || !end) return '-';
  const ms = end.getTime() - start.getTime();
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

export default ExecutionMonitor;
