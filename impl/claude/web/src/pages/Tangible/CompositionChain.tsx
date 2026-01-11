/**
 * CompositionChain - Right panel visualizing Mark -> Trace -> Crystal pipeline
 *
 * Shows:
 * - Current trace with marks
 * - Crystallized insights
 * - Derivation links to principles
 * - Cross-pilot composition
 */

import { memo } from 'react';
import {
  Gem,
  GitBranch,
  Link2,
  Clock,
  ChevronRight,
  Sparkles,
  Layers,
  ArrowRight,
} from 'lucide-react';

import type {
  CompositionChainProps,
  WitnessTrace,
  Crystal,
  DerivationLink,
} from './actualize-types';

// =============================================================================
// Pipeline Stage
// =============================================================================

interface PipelineStageProps {
  stage: 'mark' | 'trace' | 'crystal';
  count: number;
  isActive: boolean;
}

const STAGE_CONFIG = {
  mark: { icon: GitBranch, label: 'Marks', color: '#3b82f6' },
  trace: { icon: Layers, label: 'Trace', color: '#f59e0b' },
  crystal: { icon: Gem, label: 'Crystal', color: '#c4a77d' },
};

const PipelineStage = memo(function PipelineStage({ stage, count, isActive }: PipelineStageProps) {
  const config = STAGE_CONFIG[stage];
  const Icon = config.icon;

  return (
    <div
      className={`composition-chain__stage ${isActive ? 'composition-chain__stage--active' : ''}`}
      style={{ '--stage-color': config.color } as React.CSSProperties}
    >
      <Icon size={14} />
      <span className="composition-chain__stage-label">{config.label}</span>
      <span className="composition-chain__stage-count">{count}</span>
    </div>
  );
});

// =============================================================================
// Pipeline Visualization
// =============================================================================

interface PipelineVisualizationProps {
  markCount: number;
  traceActive: boolean;
  crystalCount: number;
}

const PipelineVisualization = memo(function PipelineVisualization({
  markCount,
  traceActive,
  crystalCount,
}: PipelineVisualizationProps) {
  return (
    <div className="composition-chain__pipeline">
      <div className="composition-chain__pipeline-header">
        <Sparkles size={14} />
        <span>Composition Pipeline</span>
      </div>
      <div className="composition-chain__pipeline-stages">
        <PipelineStage stage="mark" count={markCount} isActive={markCount > 0} />
        <ArrowRight size={12} className="composition-chain__pipeline-arrow" />
        <PipelineStage stage="trace" count={traceActive ? 1 : 0} isActive={traceActive} />
        <ArrowRight size={12} className="composition-chain__pipeline-arrow" />
        <PipelineStage stage="crystal" count={crystalCount} isActive={crystalCount > 0} />
      </div>
    </div>
  );
});

// =============================================================================
// Derivation Links
// =============================================================================

interface DerivationLinksProps {
  links: DerivationLink[];
}

const DerivationLinks = memo(function DerivationLinks({ links }: DerivationLinksProps) {
  if (links.length === 0) {
    return (
      <div className="composition-chain__derivation-empty">
        <Link2 size={16} />
        <span>No derivation links yet</span>
      </div>
    );
  }

  return (
    <div className="composition-chain__derivation-list">
      {links.map((link, index) => (
        <div key={index} className="composition-chain__derivation-link">
          <div className="composition-chain__derivation-source">
            <ChevronRight size={10} />
            {link.sourceId}
          </div>
          <div className="composition-chain__derivation-target">
            <Link2 size={10} />
            {link.targetPrinciple}
          </div>
          <div
            className="composition-chain__derivation-strength"
            style={{ '--strength': link.strength } as React.CSSProperties}
          >
            {Math.round(link.strength * 100)}%
          </div>
        </div>
      ))}
    </div>
  );
});

// =============================================================================
// Crystal List
// =============================================================================

interface CrystalListProps {
  crystals: Crystal[];
}

const CrystalList = memo(function CrystalList({ crystals }: CrystalListProps) {
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  if (crystals.length === 0) {
    return (
      <div className="composition-chain__crystals-empty">
        <Gem size={24} />
        <span>No crystals crystallized yet</span>
        <span className="composition-chain__crystals-hint">
          Keep witnessing marks to form crystals
        </span>
      </div>
    );
  }

  return (
    <div className="composition-chain__crystals-list">
      {crystals.map((crystal) => (
        <div key={crystal.id} className="composition-chain__crystal">
          <div className="composition-chain__crystal-header">
            <Gem size={12} />
            <span className="composition-chain__crystal-title">{crystal.title}</span>
          </div>
          <div className="composition-chain__crystal-insight">{crystal.insight}</div>
          <div className="composition-chain__crystal-meta">
            <span className="composition-chain__crystal-date">
              <Clock size={10} />
              {formatDate(crystal.createdAt)}
            </span>
            {crystal.axiomReference && (
              <span className="composition-chain__crystal-axiom">
                <Link2 size={10} />
                {crystal.axiomReference}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
});

// =============================================================================
// Trace View
// =============================================================================

interface TraceViewProps {
  trace: WitnessTrace | null;
}

const TraceView = memo(function TraceView({ trace }: TraceViewProps) {
  if (!trace) {
    return (
      <div className="composition-chain__trace-empty">
        <Layers size={20} />
        <span>No active trace</span>
        <span className="composition-chain__trace-hint">
          Select a pilot and start witnessing to create a trace
        </span>
      </div>
    );
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="composition-chain__trace">
      <div className="composition-chain__trace-header">
        <Layers size={14} />
        <span className="composition-chain__trace-pilot">{trace.pilotName}</span>
        <span className="composition-chain__trace-time">Started {formatTime(trace.createdAt)}</span>
      </div>
      <div className="composition-chain__trace-marks">
        {trace.marks.slice(-5).map((mark) => (
          <div key={mark.id} className="composition-chain__trace-mark">
            <span className="composition-chain__trace-mark-time">{formatTime(mark.timestamp)}</span>
            <span className="composition-chain__trace-mark-action">{mark.action}</span>
          </div>
        ))}
        {trace.marks.length > 5 && (
          <div className="composition-chain__trace-more">+{trace.marks.length - 5} more marks</div>
        )}
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const CompositionChain = memo(function CompositionChain({
  trace,
  crystals,
  derivationLinks,
  onCrystallize,
}: CompositionChainProps) {
  const markCount = trace?.marks.length || 0;

  return (
    <div className="composition-chain">
      <div className="composition-chain__header">
        <GitBranch size={14} />
        <span className="composition-chain__title">Composition</span>
      </div>

      {/* Pipeline Visualization */}
      <PipelineVisualization
        markCount={markCount}
        traceActive={!!trace}
        crystalCount={crystals.length}
      />

      {/* Current Trace */}
      <div className="composition-chain__section">
        <div className="composition-chain__section-header">
          <Layers size={12} />
          <span>Active Trace</span>
        </div>
        <TraceView trace={trace} />
      </div>

      {/* Derivation Links */}
      <div className="composition-chain__section">
        <div className="composition-chain__section-header">
          <Link2 size={12} />
          <span>Derivations</span>
          <span className="composition-chain__section-count">{derivationLinks.length}</span>
        </div>
        <DerivationLinks links={derivationLinks} />
      </div>

      {/* Crystals */}
      <div className="composition-chain__section">
        <div className="composition-chain__section-header">
          <Gem size={12} />
          <span>Crystals</span>
          <span className="composition-chain__section-count">{crystals.length}</span>
        </div>
        <CrystalList crystals={crystals} />
      </div>

      {/* Crystallize Action */}
      {markCount >= 5 && onCrystallize && (
        <button className="composition-chain__crystallize-btn" onClick={onCrystallize}>
          <Gem size={14} />
          Crystallize Current Trace
        </button>
      )}
    </div>
  );
});

export default CompositionChain;
