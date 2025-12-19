/**
 * CommissionPanel - Intent submission and commission management.
 *
 * The heart of the Forge UI - where Kent describes what he wants to build
 * and watches the artisans work.
 *
 * Features:
 * - Intent textarea for describing the agent to build
 * - Commission list with status indicators
 * - Commission detail view with artisan progress
 * - Intervention controls (pause, resume, cancel)
 *
 * "The Forge is where Kent builds with Kent."
 *
 * @see services/forge/commission.py
 * @see spec/protocols/metaphysical-forge.md
 */

import { useState, useCallback, FormEvent } from 'react';
import {
  Hammer,
  Play,
  Pause,
  X,
  ChevronRight,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
} from 'lucide-react';
import {
  useCommissions,
  useCreateCommission,
  useStartCommission,
  useAdvanceCommission,
  usePauseCommission,
  useResumeCommission,
  useCancelCommission,
  type Commission,
  type CommissionStatus,
} from '@/hooks/useForgeQuery';
import { cn } from '@/lib/utils';

// =============================================================================
// Types
// =============================================================================

interface CommissionPanelProps {
  /** Compact mode for sidebar */
  compact?: boolean;
  /** Callback when a commission is selected */
  onSelect?: (commission: Commission) => void;
  /** Currently selected commission ID */
  selectedId?: string;
  /** Additional class names */
  className?: string;
}

// =============================================================================
// Status Display Helpers
// =============================================================================

const STATUS_CONFIG: Record<
  CommissionStatus,
  { icon: typeof CheckCircle2; color: string; label: string }
> = {
  pending: { icon: Clock, color: 'text-stone-400', label: 'Pending' },
  designing: { icon: Loader2, color: 'text-blue-500', label: 'Designing' },
  implementing: { icon: Loader2, color: 'text-blue-500', label: 'Implementing' },
  exposing: { icon: Loader2, color: 'text-blue-500', label: 'Exposing' },
  projecting: { icon: Loader2, color: 'text-blue-500', label: 'Projecting' },
  securing: { icon: Loader2, color: 'text-blue-500', label: 'Securing' },
  verifying: { icon: Loader2, color: 'text-blue-500', label: 'Verifying' },
  reviewing: { icon: Loader2, color: 'text-amber-500', label: 'Reviewing' },
  complete: { icon: CheckCircle2, color: 'text-green-500', label: 'Complete' },
  rejected: { icon: XCircle, color: 'text-red-500', label: 'Rejected' },
  failed: { icon: XCircle, color: 'text-red-500', label: 'Failed' },
};

const ARTISAN_ORDER = ['kgent', 'architect', 'smith', 'herald', 'projector', 'sentinel', 'witness'];

const ARTISAN_LABELS: Record<string, string> = {
  kgent: 'K-gent',
  architect: 'Architect',
  smith: 'Smith',
  herald: 'Herald',
  projector: 'Projector',
  sentinel: 'Sentinel',
  witness: 'Witness',
};

// =============================================================================
// CommissionPanel Component
// =============================================================================

export function CommissionPanel({
  compact = false,
  onSelect,
  selectedId,
  className = '',
}: CommissionPanelProps) {
  const [intent, setIntent] = useState('');
  const [name, setName] = useState('');

  // Queries and mutations
  const { data: commissionsData, isLoading, refetch } = useCommissions();
  const createCommission = useCreateCommission();
  const startCommission = useStartCommission();
  const advanceCommission = useAdvanceCommission();
  const pauseCommission = usePauseCommission();
  const resumeCommission = useResumeCommission();
  const cancelCommission = useCancelCommission();

  const commissions = commissionsData?.commissions ?? [];

  // Create new commission
  const handleCreate = useCallback(
    async (e: FormEvent) => {
      e.preventDefault();
      if (!intent.trim()) return;

      try {
        const result = await createCommission.mutateAsync({
          intent: intent.trim(),
          name: name.trim() || undefined,
        });
        setIntent('');
        setName('');
        refetch();

        // Auto-start the commission
        if (result?.id) {
          await startCommission.mutateAsync({ commission_id: result.id });
          refetch();
        }
      } catch {
        // Error handled by mutation state
      }
    },
    [intent, name, createCommission, startCommission, refetch]
  );

  // Advance commission to next stage
  const handleAdvance = useCallback(
    async (commissionId: string) => {
      try {
        await advanceCommission.mutateAsync({ commission_id: commissionId });
        refetch();
      } catch {
        // Error handled by mutation state
      }
    },
    [advanceCommission, refetch]
  );

  // Toggle pause/resume
  const handleTogglePause = useCallback(
    async (commission: Commission) => {
      try {
        if (commission.paused) {
          await resumeCommission.mutateAsync({ commission_id: commission.id });
        } else {
          await pauseCommission.mutateAsync({ commission_id: commission.id });
        }
        refetch();
      } catch {
        // Error handled by mutation state
      }
    },
    [pauseCommission, resumeCommission, refetch]
  );

  // Cancel commission
  const handleCancel = useCallback(
    async (commissionId: string) => {
      try {
        await cancelCommission.mutateAsync({ commission_id: commissionId });
        refetch();
      } catch {
        // Error handled by mutation state
      }
    },
    [cancelCommission, refetch]
  );

  return (
    <div className={cn('flex flex-col', className)}>
      {/* Create Commission Form */}
      <form onSubmit={handleCreate} className="p-4 border-b border-stone-200 bg-white">
        <div className="flex items-center gap-2 mb-3">
          <Hammer className="w-5 h-5 text-amber-500" />
          <h2 className="font-medium text-stone-800">New Commission</h2>
        </div>

        {!compact && (
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Agent name (optional)"
            className="w-full px-3 py-2 mb-2 text-sm border border-stone-200 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-200"
          />
        )}

        <textarea
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          placeholder="Describe the agent you want to build..."
          rows={compact ? 2 : 3}
          className="w-full px-3 py-2 text-sm border border-stone-200 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-amber-200"
        />

        <button
          type="submit"
          disabled={!intent.trim() || createCommission.isPending}
          className={cn(
            'mt-2 w-full px-4 py-2 text-sm font-medium rounded-md transition-colors',
            'bg-amber-500 text-white hover:bg-amber-600',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {createCommission.isPending ? (
            <span className="flex items-center justify-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              Creating...
            </span>
          ) : (
            'Forge Agent'
          )}
        </button>
      </form>

      {/* Commission List */}
      <div className="flex-1 overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 bg-stone-50 border-b border-stone-200">
          <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">
            Commissions ({commissions.length})
          </span>
          <button
            onClick={() => refetch()}
            className="p-1 text-stone-400 hover:text-stone-600 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', isLoading && 'animate-spin')} />
          </button>
        </div>

        {/* Empty State */}
        {commissions.length === 0 && !isLoading && (
          <div className="p-8 text-center">
            <p className="text-sm text-stone-400">No commissions yet</p>
            <p className="mt-1 text-xs text-stone-300">Describe what you want to build above</p>
          </div>
        )}

        {/* Commission Items */}
        {commissions.map((commission) => (
          <CommissionItem
            key={commission.id}
            commission={commission}
            isSelected={commission.id === selectedId}
            compact={compact}
            onSelect={onSelect}
            onAdvance={handleAdvance}
            onTogglePause={handleTogglePause}
            onCancel={handleCancel}
            isAdvancing={advanceCommission.isPending}
          />
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// CommissionItem Component
// =============================================================================

interface CommissionItemProps {
  commission: Commission;
  isSelected: boolean;
  compact: boolean;
  onSelect?: (commission: Commission) => void;
  onAdvance: (id: string) => void;
  onTogglePause: (commission: Commission) => void;
  onCancel: (id: string) => void;
  isAdvancing: boolean;
}

function CommissionItem({
  commission,
  isSelected,
  compact,
  onSelect,
  onAdvance,
  onTogglePause,
  onCancel,
  isAdvancing,
}: CommissionItemProps) {
  const statusConfig = STATUS_CONFIG[commission.status];
  const StatusIcon = statusConfig.icon;

  const isActive = !['complete', 'rejected', 'failed'].includes(commission.status);
  const canAdvance = isActive && !commission.paused && commission.status !== 'pending';

  return (
    <div
      className={cn(
        'border-b border-stone-100 transition-colors',
        isSelected ? 'bg-amber-50' : 'bg-white hover:bg-stone-50',
        onSelect && 'cursor-pointer'
      )}
      onClick={() => onSelect?.(commission)}
    >
      {/* Main Info */}
      <div className="px-4 py-3">
        <div className="flex items-start gap-3">
          {/* Status Icon */}
          <StatusIcon
            className={cn(
              'w-4 h-4 mt-0.5 flex-shrink-0',
              statusConfig.color,
              statusConfig.icon === Loader2 && 'animate-spin'
            )}
          />

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-stone-800 text-sm truncate">
                {commission.name || commission.id.slice(-8)}
              </span>
              {commission.paused && (
                <span className="px-1.5 py-0.5 text-[10px] bg-yellow-100 text-yellow-700 rounded">
                  Paused
                </span>
              )}
            </div>

            {!compact && (
              <p className="mt-0.5 text-xs text-stone-500 line-clamp-2">{commission.intent}</p>
            )}

            {/* Status Label */}
            <span className="text-[10px] text-stone-400 uppercase tracking-wide">
              {statusConfig.label}
            </span>
          </div>

          {/* Action Buttons */}
          {isActive && !compact && (
            <div className="flex items-center gap-1">
              {/* Pause/Resume */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onTogglePause(commission);
                }}
                className="p-1.5 text-stone-400 hover:text-stone-600 transition-colors"
                title={commission.paused ? 'Resume' : 'Pause'}
              >
                {commission.paused ? (
                  <Play className="w-3.5 h-3.5" />
                ) : (
                  <Pause className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Advance */}
              {canAdvance && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onAdvance(commission.id);
                  }}
                  disabled={isAdvancing}
                  className="p-1.5 text-amber-500 hover:text-amber-600 transition-colors disabled:opacity-50"
                  title="Advance to next stage"
                >
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              )}

              {/* Cancel */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onCancel(commission.id);
                }}
                className="p-1.5 text-stone-400 hover:text-red-500 transition-colors"
                title="Cancel"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Artisan Progress (expanded view) */}
      {!compact && isSelected && <ArtisanProgress commission={commission} />}
    </div>
  );
}

// =============================================================================
// ArtisanProgress Component
// =============================================================================

interface ArtisanProgressProps {
  commission: Commission;
}

function ArtisanProgress({ commission }: ArtisanProgressProps) {
  return (
    <div className="px-4 pb-3 bg-stone-50">
      <div className="text-xs font-medium text-stone-500 mb-2">Artisan Progress</div>
      <div className="space-y-1">
        {ARTISAN_ORDER.map((artisan) => {
          const output = commission.artisan_outputs[artisan];
          const status = output?.status || 'pending';

          const statusIcon = {
            pending: <Clock className="w-3 h-3 text-stone-300" />,
            working: <Loader2 className="w-3 h-3 text-blue-500 animate-spin" />,
            complete: <CheckCircle2 className="w-3 h-3 text-green-500" />,
            failed: <XCircle className="w-3 h-3 text-red-500" />,
            skipped: <Clock className="w-3 h-3 text-stone-300" />,
          }[status] || <Clock className="w-3 h-3 text-stone-300" />;

          return (
            <div key={artisan} className="flex items-center gap-2 text-xs">
              {statusIcon}
              <span
                className={cn(
                  'flex-1',
                  status === 'complete' ? 'text-stone-700' : 'text-stone-400'
                )}
              >
                {ARTISAN_LABELS[artisan] || artisan}
              </span>
              {output?.annotation && (
                <span className="text-[10px] text-stone-400 truncate max-w-[120px]">
                  {output.annotation}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Soul Annotation */}
      {commission.soul_annotation && (
        <div className="mt-3 p-2 bg-amber-50 rounded text-xs text-amber-800">
          <span className="font-medium">K-gent:</span> {commission.soul_annotation}
        </div>
      )}
    </div>
  );
}

export default CommissionPanel;
