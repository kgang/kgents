/**
 * ActivePilot - Center panel showing current endeavor in progress
 *
 * Displays:
 * - Active pilot info
 * - Mark input for witnessing
 * - Live mark stream
 * - Progress toward crystal
 */

import { memo, useState, useCallback, useRef } from 'react';
import { Play, Pause, RotateCcw, Plus, Clock, Gem, Layers, X, Send } from 'lucide-react';

import type { ActivePilotProps, WitnessMark, MarkContext, CustomPilot } from './actualize-types';
import { TIER_CONFIG } from './actualize-types';

// =============================================================================
// Mark Input
// =============================================================================

interface MarkInputProps {
  onMark: (action: string, context: MarkContext) => void;
  pilotName: string;
}

const MarkInput = memo(function MarkInput({ onMark, pilotName }: MarkInputProps) {
  const [value, setValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback(() => {
    if (value.trim()) {
      onMark(value.trim(), {
        metadata: { source: 'active-pilot' },
      });
      setValue('');
      inputRef.current?.focus();
    }
  }, [value, onMark]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className="active-pilot__mark-input">
      <input
        ref={inputRef}
        type="text"
        className="active-pilot__mark-field"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={`Witness a mark for ${pilotName}...`}
      />
      <button className="active-pilot__mark-submit" onClick={handleSubmit} disabled={!value.trim()}>
        <Send size={14} />
      </button>
    </div>
  );
});

// =============================================================================
// Mark Stream
// =============================================================================

interface MarkStreamProps {
  marks: WitnessMark[];
}

const MarkStream = memo(function MarkStream({ marks }: MarkStreamProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  if (marks.length === 0) {
    return (
      <div className="active-pilot__marks-empty">
        <Gem size={24} />
        <span>No marks yet. Start witnessing your journey.</span>
      </div>
    );
  }

  return (
    <div className="active-pilot__marks">
      {marks
        .slice()
        .reverse()
        .map((mark) => (
          <div key={mark.id} className="active-pilot__mark">
            <div className="active-pilot__mark-time">
              <Clock size={10} />
              {formatTime(mark.timestamp)}
            </div>
            <div className="active-pilot__mark-action">{mark.action}</div>
            {mark.context.derivationLink && (
              <div className="active-pilot__mark-derivation">
                Linked to: {mark.context.derivationLink}
              </div>
            )}
          </div>
        ))}
    </div>
  );
});

// =============================================================================
// Crystal Progress
// =============================================================================

interface CrystalProgressProps {
  markCount: number;
  threshold: number;
}

const CrystalProgress = memo(function CrystalProgress({
  markCount,
  threshold,
}: CrystalProgressProps) {
  const progress = Math.min((markCount / threshold) * 100, 100);
  const isReady = markCount >= threshold;

  return (
    <div className="active-pilot__crystal">
      <div className="active-pilot__crystal-header">
        <Gem size={14} />
        <span>Crystal Progress</span>
        <span className="active-pilot__crystal-count">
          {markCount}/{threshold}
        </span>
      </div>
      <div className="active-pilot__crystal-bar">
        <div
          className={`active-pilot__crystal-fill ${isReady ? 'active-pilot__crystal-fill--ready' : ''}`}
          style={{ width: `${progress}%` }}
        />
      </div>
      {isReady && (
        <button className="active-pilot__crystal-btn">
          <Gem size={14} />
          Crystallize
        </button>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const ActivePilot = memo(function ActivePilot({
  pilot,
  marks,
  onMark,
  onDeactivate,
}: ActivePilotProps) {
  const [isPaused, setIsPaused] = useState(false);
  const tierConfig = TIER_CONFIG[pilot.tier];
  const isCustom = 'isCustom' in pilot && pilot.isCustom;
  const customPilot = isCustom ? (pilot as CustomPilot) : null;

  // Crystal threshold (configurable, default 5 marks)
  const crystalThreshold = 5;

  return (
    <div className="active-pilot">
      {/* Header */}
      <div className="active-pilot__header">
        <div className="active-pilot__info">
          <div className="active-pilot__name">
            <Layers size={16} style={{ color: pilot.color || tierConfig.color }} />
            <span>{pilot.displayName}</span>
          </div>
          <div className="active-pilot__tier" style={{ color: tierConfig.color }}>
            {tierConfig.label}
            {isCustom && ' (Custom)'}
          </div>
        </div>

        <div className="active-pilot__controls">
          <button
            className={`active-pilot__control-btn ${isPaused ? 'active-pilot__control-btn--paused' : ''}`}
            onClick={() => setIsPaused(!isPaused)}
            title={isPaused ? 'Resume' : 'Pause'}
          >
            {isPaused ? <Play size={14} /> : <Pause size={14} />}
          </button>
          <button
            className="active-pilot__control-btn"
            onClick={() => onDeactivate()}
            title="Deactivate"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Personality Tag */}
      <div className="active-pilot__personality">&quot;{pilot.personalityTag}&quot;</div>

      {/* Custom Axioms (if custom pilot) */}
      {customPilot && (
        <div className="active-pilot__axioms">
          <div className="active-pilot__axioms-header">Your Axioms</div>
          <div className="active-pilot__axiom">
            <span className="active-pilot__axiom-label">Success:</span>
            <span>{customPilot.axioms.A1_success}</span>
          </div>
          <div className="active-pilot__axiom">
            <span className="active-pilot__axiom-label">Feeling:</span>
            <span>{customPilot.axioms.A2_feeling}</span>
          </div>
          <div className="active-pilot__axiom">
            <span className="active-pilot__axiom-label">Non-negotiable:</span>
            <span>{customPilot.axioms.A3_nonnegotiable}</span>
          </div>
          <div className="active-pilot__axiom">
            <span className="active-pilot__axiom-label">Validation:</span>
            <span>{customPilot.axioms.A4_validation}</span>
          </div>
        </div>
      )}

      {/* Mark Input */}
      {!isPaused && <MarkInput onMark={onMark} pilotName={pilot.displayName} />}

      {/* Crystal Progress */}
      <CrystalProgress markCount={marks.length} threshold={crystalThreshold} />

      {/* Mark Stream */}
      <div className="active-pilot__stream">
        <div className="active-pilot__stream-header">
          <Clock size={14} />
          <span>Mark Stream</span>
          <span className="active-pilot__stream-count">{marks.length}</span>
        </div>
        <MarkStream marks={marks} />
      </div>

      {/* Quick Actions */}
      <div className="active-pilot__quick">
        <button className="active-pilot__quick-btn" title="Add Quick Mark">
          <Plus size={14} />
          Quick Mark
        </button>
        <button className="active-pilot__quick-btn" title="Reset Session">
          <RotateCcw size={14} />
          Reset
        </button>
      </div>
    </div>
  );
});

export default ActivePilot;
