/**
 * WASM Survivors - Crystal View
 *
 * Post-run proof display showing the crystallized witness trace.
 * Implements DD-1: Invisible Witness - marks are invisible until this view.
 * Implements DD-3: Crystal as Proof - compressed, shareable run summary.
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import { useState, useCallback } from 'react';
import type {
  GameCrystal,
  CrystalSegment,
  GamePrincipleWeights,
  Ghost,
} from '@kgents/shared-primitives';
import { COLORS } from '../systems/juice';

// =============================================================================
// Types
// =============================================================================

interface CrystalViewProps {
  crystal: GameCrystal;
  ghosts: Ghost[];
  onClose: () => void;
  onPlayAgain: () => void;
}

// =============================================================================
// Component
// =============================================================================

export function CrystalView({
  crystal,
  ghosts,
  onClose,
  onPlayAgain,
}: CrystalViewProps) {
  const [activeTab, setActiveTab] = useState<'journey' | 'ghosts' | 'share'>('journey');
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(crystal.shareableText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [crystal.shareableText]);

  return (
    <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 overflow-y-auto py-8">
      <div className="max-w-2xl w-full mx-4 bg-gray-900 rounded-xl border border-gray-700 shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-gray-700 text-center">
          <div className="text-4xl mb-2">*</div>
          <h1
            className="text-2xl font-bold mb-2"
            style={{ color: COLORS.xp }}
          >
            {crystal.title}
          </h1>
          <p className="text-gray-400">{crystal.claim}</p>
        </div>

        {/* Stats Bar */}
        <div className="grid grid-cols-4 gap-4 p-4 bg-gray-800/50 border-b border-gray-700">
          <StatBox
            label="Wave"
            value={crystal.waveReached.toString()}
            color={COLORS.player}
          />
          <StatBox
            label="Duration"
            value={formatDuration(crystal.duration)}
            color={COLORS.health}
          />
          <StatBox
            label="Pivots"
            value={crystal.pivotMoments.toString()}
            color={COLORS.crisis}
          />
          <StatBox
            label="Ghosts"
            value={crystal.ghostCount.toString()}
            color={COLORS.ghost}
          />
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-700">
          <TabButton
            active={activeTab === 'journey'}
            onClick={() => setActiveTab('journey')}
          >
            Journey
          </TabButton>
          <TabButton
            active={activeTab === 'ghosts'}
            onClick={() => setActiveTab('ghosts')}
          >
            Ghosts ({ghosts.length})
          </TabButton>
          <TabButton
            active={activeTab === 'share'}
            onClick={() => setActiveTab('share')}
          >
            Share
          </TabButton>
        </div>

        {/* Tab Content */}
        <div className="p-6 max-h-80 overflow-y-auto">
          {activeTab === 'journey' && (
            <JourneyTab
              segments={crystal.segments}
              weights={crystal.finalWeights}
            />
          )}
          {activeTab === 'ghosts' && <GhostsTab ghosts={ghosts} />}
          {activeTab === 'share' && (
            <ShareTab
              crystal={crystal}
              onCopy={handleCopy}
              copied={copied}
            />
          )}
        </div>

        {/* Actions */}
        <div className="p-4 border-t border-gray-700 flex gap-3">
          <button
            onClick={onPlayAgain}
            className="flex-1 py-3 rounded-lg font-medium transition-colors"
            style={{ backgroundColor: COLORS.player, color: '#000' }}
          >
            Play Again
          </button>
          <button
            onClick={onClose}
            className="px-6 py-3 rounded-lg font-medium bg-gray-700 text-white hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function StatBox({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="text-center">
      <div className="text-2xl font-bold" style={{ color }}>
        {value}
      </div>
      <div className="text-xs text-gray-500 uppercase">{label}</div>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 py-3 text-sm font-medium transition-colors ${
        active
          ? 'text-white border-b-2 border-yellow-400'
          : 'text-gray-500 hover:text-gray-300'
      }`}
    >
      {children}
    </button>
  );
}

function JourneyTab({
  segments,
  weights,
}: {
  segments: CrystalSegment[];
  weights: GamePrincipleWeights;
}) {
  return (
    <div className="space-y-6">
      {/* Narrative segments */}
      <div className="space-y-4">
        {segments.map((segment, index) => (
          <div key={index} className="relative pl-6 border-l-2 border-gray-700">
            <div
              className="absolute left-[-5px] top-0 w-2 h-2 rounded-full"
              style={{ backgroundColor: getEmotionColor(segment.emotion) }}
            />
            <div className="text-sm text-gray-500 mb-1">
              Waves {segment.waves[0]}-{segment.waves[1]} | {segment.emotion}
            </div>
            <div className="text-gray-300">{segment.narrative}</div>
            {segment.keyMoments.length > 0 && (
              <div className="mt-2 text-xs text-gray-500">
                Key moments: {segment.keyMoments.slice(0, 2).join(' | ')}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Playstyle weights */}
      <div className="pt-4 border-t border-gray-700">
        <h3 className="text-sm font-medium text-gray-400 mb-3">
          Playstyle Signature
        </h3>
        <div className="space-y-2">
          {Object.entries(weights).map(([key, value]) => (
            <div key={key} className="flex items-center gap-3">
              <span className="text-gray-400 text-sm w-24 capitalize">{key}</span>
              <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${value * 100}%`,
                    backgroundColor: getWeightColor(key),
                  }}
                />
              </div>
              <span className="text-gray-500 text-xs w-12 text-right">
                {Math.round(value * 100)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function GhostsTab({ ghosts }: { ghosts: Ghost[] }) {
  if (ghosts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <div className="text-4xl mb-2" style={{ color: COLORS.ghost }}>
          -
        </div>
        <p>No decision points recorded in this run.</p>
        <p className="text-sm mt-2">
          Ghosts appear when you make upgrade choices.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p
        className="text-sm italic mb-4"
        style={{ color: COLORS.ghost }}
      >
        "Every path holds its own wisdom. These alternatives were equally valid."
      </p>

      {ghosts.map((ghost, index) => (
        <div
          key={index}
          className="p-4 rounded-lg bg-gray-800/50 border border-gray-700"
        >
          <div className="flex items-start justify-between mb-2">
            <span className="text-gray-400 text-sm">
              Decision at Wave {ghost.context.wave}
            </span>
            <span
              className="text-xs px-2 py-1 rounded"
              style={{
                backgroundColor: `${COLORS.ghost}22`,
                color: COLORS.ghost,
              }}
            >
              Drift: {Math.round(ghost.projectedDrift * 100)}%
            </span>
          </div>

          <div className="flex items-center gap-2 mb-2">
            <span className="text-green-400">Chose:</span>
            <span className="text-white font-medium">
              {formatUpgradeName(ghost.chosen)}
            </span>
          </div>

          <div className="flex items-start gap-2">
            <span style={{ color: COLORS.ghost }}>Alternatives:</span>
            <span className="text-gray-400">
              {ghost.unchosen.map(formatUpgradeName).join(', ')}
            </span>
          </div>

          <div className="mt-2 text-xs text-gray-600">
            Context: {ghost.context.health}/{ghost.context.maxHealth} HP |{' '}
            {ghost.context.upgrades.length} upgrades
          </div>
        </div>
      ))}
    </div>
  );
}

function ShareTab({
  crystal,
  onCopy,
  copied,
}: {
  crystal: GameCrystal;
  onCopy: () => void;
  copied: boolean;
}) {
  return (
    <div className="space-y-6">
      {/* Shareable text */}
      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-2">
          Share Your Run
        </h3>
        <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
          <p className="text-gray-300">{crystal.shareableText}</p>
        </div>
        <button
          onClick={onCopy}
          className={`mt-2 w-full py-2 rounded-lg text-sm font-medium transition-colors ${
            copied
              ? 'bg-green-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          {copied ? 'Copied!' : 'Copy to Clipboard'}
        </button>
      </div>

      {/* Proof hash */}
      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-2">Proof Hash</h3>
        <div className="flex items-center gap-2">
          <code className="flex-1 p-3 bg-gray-800 rounded-lg text-gray-400 text-sm font-mono">
            {crystal.shareableHash}
          </code>
        </div>
        <p className="text-xs text-gray-600 mt-2">
          This hash uniquely identifies your run and can be used to verify your
          achievement.
        </p>
      </div>

      {/* Quick stats for sharing */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
        <div className="text-center p-3 bg-gray-800 rounded-lg">
          <div
            className="text-xl font-bold"
            style={{ color: COLORS.player }}
          >
            Wave {crystal.waveReached}
          </div>
          <div className="text-xs text-gray-500">Reached</div>
        </div>
        <div className="text-center p-3 bg-gray-800 rounded-lg">
          <div className="text-xl font-bold" style={{ color: COLORS.xp }}>
            {formatDuration(crystal.duration)}
          </div>
          <div className="text-xs text-gray-500">Duration</div>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function formatUpgradeName(id: string): string {
  const names: Record<string, string> = {
    damage_up: 'Power Strike',
    attack_speed_up: 'Rapid Fire',
    move_speed_up: 'Swift Steps',
    health_up: 'Vitality',
    attack_range_up: 'Long Reach',
  };
  return names[id] || id.replace(/_/g, ' ');
}

function getEmotionColor(emotion: CrystalSegment['emotion']): string {
  const colors: Record<string, string> = {
    hope: COLORS.health,
    flow: COLORS.player,
    crisis: COLORS.crisis,
    triumph: COLORS.xp,
    grief: COLORS.ghost,
  };
  return colors[emotion] || COLORS.ghost;
}

function getWeightColor(key: string): string {
  const colors: Record<string, string> = {
    aggression: '#FF6B6B',
    defense: COLORS.health,
    mobility: COLORS.player,
    precision: '#9B59B6',
    synergy: COLORS.xp,
  };
  return colors[key] || COLORS.ghost;
}

export default CrystalView;
