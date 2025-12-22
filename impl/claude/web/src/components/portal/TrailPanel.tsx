/**
 * TrailPanel - Side panel showing exploration trail
 *
 * Phase 5D: Integration
 *
 * Shows the current exploration trail with:
 * - Step-by-step navigation history
 * - Evidence strength indicator
 * - Collaboration events (proposals accepted/rejected)
 * - Witness button to persist significant trails
 *
 * Design Philosophy:
 * "The trail IS evidence" — Every expansion, every annotation,
 * becomes part of the evidence chain that justifies decisions.
 *
 * @see spec/protocols/context-perception.md §6
 * @see plans/context-perception-phase5.md §3.4
 */

import { memo, useCallback, useMemo, useState } from 'react';
import {
  Footprints,
  ChevronRight,
  ChevronDown,
  Eye,
  MessageSquare,
  Check,
  X,
  GitFork,
  Save,
  Sparkles,
  Clock,
  FileCode,
} from 'lucide-react';
import { Breathe } from '@/components/joy';
import { EvidenceBadge, EvidenceProgress } from './EvidenceBadge';
import type { Trail, TrailStep, TrailEvidence, EvidenceStrength } from '@/api/trail';

// =============================================================================
// Types
// =============================================================================

/**
 * A collaboration event that happened during exploration.
 */
export interface CollaborationEvent {
  type: 'proposal_accepted' | 'proposal_rejected' | 'auto_accepted';
  proposalId: string;
  agentName: string;
  description: string;
  timestamp: string;
  /** Associated step index (if any) */
  stepIndex?: number;
}

export interface TrailPanelProps {
  /** Current trail data */
  trail: Trail | null;
  /** Evidence analysis */
  evidence: TrailEvidence | null;
  /** Collaboration events during this session */
  collaborationEvents?: CollaborationEvent[];
  /** Currently selected step */
  selectedStep: number | null;
  /** Callback when step is selected */
  onSelectStep?: (stepIndex: number) => void;
  /** Callback to witness the trail */
  onWitness?: () => Promise<void>;
  /** Callback to fork the trail */
  onFork?: (name: string, forkPoint?: number) => Promise<void>;
  /** Whether witnessing is in progress */
  isWitnessing?: boolean;
  /** Whether the panel is collapsed */
  collapsed?: boolean;
  /** Callback to toggle collapse */
  onToggleCollapse?: () => void;
  /** Custom class name */
  className?: string;
}

export interface TrailStepItemProps {
  /** The step data */
  step: TrailStep;
  /** Index in the trail */
  index: number;
  /** Whether this step is selected */
  isSelected: boolean;
  /** Whether this is the current (last) step */
  isCurrent: boolean;
  /** Annotation for this step */
  annotation?: string;
  /** Collaboration event at this step */
  collaborationEvent?: CollaborationEvent;
  /** Click handler */
  onClick: () => void;
}

// =============================================================================
// Trail Step Item
// =============================================================================

const TrailStepItem = memo(function TrailStepItem({
  step,
  index: _index,
  isSelected,
  isCurrent,
  annotation,
  collaborationEvent,
  onClick,
}: TrailStepItemProps) {
  // Note: _index available for debugging but not actively used in render
  // Format the path for display
  const displayPath = useMemo(() => {
    const parts = step.source_path.split('/');
    return parts.length > 2 ? `.../${parts.slice(-2).join('/')}` : step.source_path;
  }, [step.source_path]);

  // Edge type styling
  const edgeColor = useMemo(() => {
    if (!step.edge) return 'text-gray-500';
    switch (step.edge) {
      case 'imports':
        return 'text-cyan-400';
      case 'tests':
        return 'text-green-400';
      case 'spec':
        return 'text-purple-400';
      case 'callers':
        return 'text-amber-400';
      default:
        return 'text-blue-400';
    }
  }, [step.edge]);

  return (
    <div
      className={`
        relative pl-6 py-2 cursor-pointer transition-colors
        ${isSelected ? 'bg-blue-950/40 border-l-2 border-blue-500' : 'border-l-2 border-gray-700 hover:bg-gray-800/50'}
        ${isCurrent ? 'border-l-green-500' : ''}
      `}
      onClick={onClick}
    >
      {/* Step marker */}
      <div
        className={`
          absolute left-0 top-1/2 -translate-x-1/2 -translate-y-1/2
          w-3 h-3 rounded-full border-2
          ${isCurrent ? 'bg-green-500 border-green-400' : isSelected ? 'bg-blue-500 border-blue-400' : 'bg-gray-700 border-gray-600'}
        `}
      />

      {/* Step content */}
      <div className="space-y-1">
        {/* Edge type (if not start) */}
        {step.edge && (
          <div className={`text-[10px] font-medium ${edgeColor}`}>
            ──[{step.edge}]──▶
          </div>
        )}

        {/* Path */}
        <div className="flex items-center gap-1.5">
          <FileCode className="w-3 h-3 text-gray-500" />
          <span
            className={`text-xs font-mono truncate ${isSelected ? 'text-white' : 'text-gray-300'}`}
            title={step.source_path}
          >
            {displayPath}
          </span>
        </div>

        {/* Destinations count */}
        {step.destination_paths.length > 0 && (
          <div className="text-[10px] text-gray-500">
            → {step.destination_paths.length} target{step.destination_paths.length !== 1 ? 's' : ''}
          </div>
        )}

        {/* Annotation */}
        {annotation && (
          <div className="flex items-start gap-1 mt-1 p-1.5 bg-gray-800/50 rounded text-[10px] text-gray-400">
            <MessageSquare className="w-3 h-3 flex-shrink-0 mt-0.5" />
            <span>{annotation}</span>
          </div>
        )}

        {/* Collaboration event */}
        {collaborationEvent && (
          <div
            className={`
              flex items-center gap-1 mt-1 p-1.5 rounded text-[10px]
              ${collaborationEvent.type === 'proposal_accepted' ? 'bg-green-950/30 text-green-400' : ''}
              ${collaborationEvent.type === 'proposal_rejected' ? 'bg-red-950/30 text-red-400' : ''}
              ${collaborationEvent.type === 'auto_accepted' ? 'bg-purple-950/30 text-purple-400' : ''}
            `}
          >
            {collaborationEvent.type === 'proposal_accepted' && <Check className="w-3 h-3" />}
            {collaborationEvent.type === 'proposal_rejected' && <X className="w-3 h-3" />}
            {collaborationEvent.type === 'auto_accepted' && <Sparkles className="w-3 h-3" />}
            <span className="truncate">{collaborationEvent.description}</span>
          </div>
        )}

        {/* Loop warning */}
        {step.loop_status !== 'none' && (
          <div className="text-[10px] text-amber-400">⚠ Loop detected: {step.loop_status}</div>
        )}
      </div>
    </div>
  );
});

// =============================================================================
// Trail Panel Header
// =============================================================================

interface TrailPanelHeaderProps {
  trail: Trail | null;
  evidence: TrailEvidence | null;
  collapsed: boolean;
  onToggleCollapse: () => void;
  onWitness?: () => Promise<void>;
  isWitnessing: boolean;
}

const TrailPanelHeader = memo(function TrailPanelHeader({
  trail,
  evidence,
  collapsed,
  onToggleCollapse,
  onWitness,
  isWitnessing,
}: TrailPanelHeaderProps) {
  return (
    <div className="flex items-center justify-between px-3 py-2 border-b border-gray-800">
      <button
        onClick={onToggleCollapse}
        className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors"
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        <Footprints className="w-4 h-4" />
        <span className="text-sm font-medium">Trail</span>
        {trail && (
          <span className="text-xs text-gray-500">({trail.steps.length} steps)</span>
        )}
      </button>

      <div className="flex items-center gap-2">
        {/* Evidence badge */}
        {evidence && (
          <EvidenceBadge
            strength={evidence.evidence_strength}
            evidence={evidence}
            size="sm"
            showLabel={false}
          />
        )}

        {/* Witness button */}
        {onWitness && trail && trail.steps.length >= 3 && (
          <button
            onClick={onWitness}
            disabled={isWitnessing}
            className="p-1 rounded hover:bg-gray-700 transition-colors disabled:opacity-50"
            title="Witness this trail"
          >
            <Breathe intensity={isWitnessing ? 0.3 : 0} speed="fast">
              <Eye
                className={`w-4 h-4 ${isWitnessing ? 'text-purple-400' : 'text-gray-400 hover:text-purple-400'}`}
              />
            </Breathe>
          </button>
        )}
      </div>
    </div>
  );
});

// =============================================================================
// Trail Panel
// =============================================================================

export const TrailPanel = memo(function TrailPanel({
  trail,
  evidence,
  collaborationEvents = [],
  selectedStep,
  onSelectStep,
  onWitness,
  onFork,
  isWitnessing = false,
  collapsed: controlledCollapsed,
  onToggleCollapse,
  className = '',
}: TrailPanelProps) {
  // Internal collapsed state (if not controlled)
  const [internalCollapsed, setInternalCollapsed] = useState(false);
  const collapsed = controlledCollapsed ?? internalCollapsed;
  const handleToggleCollapse = onToggleCollapse ?? (() => setInternalCollapsed((c) => !c));

  // Fork dialog state
  const [showForkDialog, setShowForkDialog] = useState(false);
  const [forkName, setForkName] = useState('');

  // Map collaboration events to step indices
  const eventsByStep = useMemo(() => {
    const map = new Map<number, CollaborationEvent>();
    collaborationEvents.forEach((event) => {
      if (event.stepIndex !== undefined) {
        map.set(event.stepIndex, event);
      }
    });
    return map;
  }, [collaborationEvents]);

  // Handle step click
  const handleStepClick = useCallback(
    (index: number) => {
      onSelectStep?.(index);
    },
    [onSelectStep]
  );

  // Handle fork
  const handleFork = useCallback(async () => {
    if (forkName.trim() && onFork) {
      await onFork(forkName.trim(), selectedStep ?? undefined);
      setForkName('');
      setShowForkDialog(false);
    }
  }, [forkName, onFork, selectedStep]);

  // Empty state
  if (!trail || trail.steps.length === 0) {
    return (
      <div className={`bg-gray-900/50 border border-gray-800 rounded-lg ${className}`}>
        <TrailPanelHeader
          trail={null}
          evidence={null}
          collapsed={collapsed}
          onToggleCollapse={handleToggleCollapse}
          isWitnessing={false}
        />
        {!collapsed && (
          <div className="p-4 text-center text-gray-500 text-sm">
            <Footprints className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>No exploration trail yet.</p>
            <p className="text-xs mt-1">Expand portals to create a trail.</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`bg-gray-900/50 border border-gray-800 rounded-lg ${className}`}>
      {/* Header */}
      <TrailPanelHeader
        trail={trail}
        evidence={evidence}
        collapsed={collapsed}
        onToggleCollapse={handleToggleCollapse}
        onWitness={onWitness}
        isWitnessing={isWitnessing}
      />

      {/* Content (collapsible) */}
      {!collapsed && (
        <>
          {/* Evidence progress */}
          {evidence && (
            <div className="px-3 py-2 border-b border-gray-800">
              <EvidenceProgress evidence={evidence} />
            </div>
          )}

          {/* Trail name */}
          <div className="px-3 py-2 border-b border-gray-800 flex items-center justify-between">
            <span className="text-xs text-gray-400 truncate" title={trail.name}>
              {trail.name}
            </span>
            <div className="flex items-center gap-1">
              {/* Fork button */}
              {onFork && (
                <button
                  onClick={() => setShowForkDialog(true)}
                  className="p-1 rounded hover:bg-gray-700 transition-colors"
                  title="Fork trail"
                >
                  <GitFork className="w-3 h-3 text-gray-500 hover:text-gray-300" />
                </button>
              )}
              {/* Timestamp */}
              {trail.created_at && (
                <span className="text-[10px] text-gray-600 flex items-center gap-1">
                  <Clock className="w-2.5 h-2.5" />
                  {new Date(trail.created_at).toLocaleTimeString()}
                </span>
              )}
            </div>
          </div>

          {/* Steps list */}
          <div className="max-h-80 overflow-y-auto">
            {trail.steps.map((step, index) => (
              <TrailStepItem
                key={`${step.source_path}-${index}`}
                step={step}
                index={index}
                isSelected={selectedStep === index}
                isCurrent={index === trail.steps.length - 1}
                annotation={trail.annotations[index]}
                collaborationEvent={eventsByStep.get(index)}
                onClick={() => handleStepClick(index)}
              />
            ))}
          </div>

          {/* Collaboration events (outside steps) */}
          {collaborationEvents.filter((e) => e.stepIndex === undefined).length > 0 && (
            <div className="px-3 py-2 border-t border-gray-800">
              <div className="text-[10px] text-gray-500 mb-1.5">Session Activity</div>
              <div className="space-y-1">
                {collaborationEvents
                  .filter((e) => e.stepIndex === undefined)
                  .map((event, i) => (
                    <div
                      key={`event-${i}`}
                      className={`
                        flex items-center gap-1 p-1.5 rounded text-[10px]
                        ${event.type === 'proposal_accepted' ? 'bg-green-950/30 text-green-400' : ''}
                        ${event.type === 'proposal_rejected' ? 'bg-red-950/30 text-red-400' : ''}
                        ${event.type === 'auto_accepted' ? 'bg-purple-950/30 text-purple-400' : ''}
                      `}
                    >
                      <Sparkles className="w-3 h-3" />
                      <span className="truncate">{event.description}</span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Topics */}
          {trail.topics.length > 0 && (
            <div className="px-3 py-2 border-t border-gray-800">
              <div className="flex flex-wrap gap-1">
                {trail.topics.map((topic) => (
                  <span
                    key={topic}
                    className="px-1.5 py-0.5 text-[10px] bg-gray-800 text-gray-400 rounded"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Fork dialog */}
      {showForkDialog && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-4 w-64 shadow-xl">
            <h3 className="text-sm font-medium text-white mb-3">Fork Trail</h3>
            <input
              type="text"
              value={forkName}
              onChange={(e) => setForkName(e.target.value)}
              placeholder="Fork name..."
              className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              autoFocus
            />
            <div className="flex justify-end gap-2 mt-3">
              <button
                onClick={() => setShowForkDialog(false)}
                className="px-3 py-1.5 text-sm text-gray-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleFork}
                disabled={!forkName.trim()}
                className="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded disabled:opacity-50"
              >
                <Save className="w-3 h-3 inline mr-1" />
                Fork
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Compact Trail Indicator (for header/status bar)
// =============================================================================

export interface TrailIndicatorProps {
  /** Number of steps in trail */
  stepCount: number;
  /** Evidence strength */
  strength?: EvidenceStrength;
  /** Click handler */
  onClick?: () => void;
  /** Custom class name */
  className?: string;
}

export const TrailIndicator = memo(function TrailIndicator({
  stepCount,
  strength,
  onClick,
  className = '',
}: TrailIndicatorProps) {
  if (stepCount === 0) return null;

  return (
    <button
      onClick={onClick}
      className={`
        inline-flex items-center gap-1.5 px-2 py-1 rounded-full
        bg-gray-800/50 border border-gray-700
        text-gray-300 text-xs
        hover:bg-gray-700 transition-colors
        ${className}
      `}
    >
      <Footprints className="w-3 h-3" />
      <span>{stepCount} steps</span>
      {strength && strength !== 'weak' && (
        <EvidenceBadge strength={strength} size="sm" showLabel={false} />
      )}
    </button>
  );
});

// =============================================================================
// Exports
// =============================================================================

export default TrailPanel;
