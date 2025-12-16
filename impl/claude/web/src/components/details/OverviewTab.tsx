/**
 * OverviewTab: Phase, mood, and activity summary.
 *
 * Quick glance at citizen state with sparkline visualization.
 */

import { cn, getPhaseColor, getArchetypeColor } from '@/lib/utils';
import type { CitizenCardJSON, CitizenEigenvectors } from '@/reactive/types';
import type { CitizenManifest } from '@/api/types';

type EigenvectorKey = keyof CitizenEigenvectors;

export interface OverviewTabProps {
  citizen: CitizenCardJSON;
  manifest: CitizenManifest | null;
  expanded?: boolean;
}

export function OverviewTab({ citizen, manifest, expanded = false }: OverviewTabProps) {
  return (
    <div className="space-y-6">
      {/* Current State */}
      <Section title="Current State">
        <div className={cn('grid gap-4', expanded ? 'grid-cols-3' : 'grid-cols-2')}>
          <StatCard
            label="Phase"
            value={citizen.phase}
            valueClass={getPhaseColor(citizen.phase)}
            icon="🔄"
          />
          <StatCard
            label="Archetype"
            value={citizen.archetype}
            valueClass={getArchetypeColor(citizen.archetype)}
            icon="🎭"
          />
          <StatCard label="Region" value={citizen.region} icon="📍" />
          {citizen.nphase && (
            <StatCard label="N-Phase" value={citizen.nphase} icon="🌀" />
          )}
          <StatCard
            label="Capability"
            value={`${(citizen.capability * 100).toFixed(0)}%`}
            icon="💪"
          />
          <StatCard
            label="Entropy"
            value={citizen.entropy.toFixed(3)}
            icon="🎲"
          />
        </div>
      </Section>

      {/* Mood & Metaphor (LOD 2) */}
      {manifest?.mood && (
        <Section title="Mood">
          <div className="flex items-center gap-3">
            <MoodIndicator mood={manifest.mood} />
            <span className="font-medium">{manifest.mood}</span>
          </div>
          {manifest.metaphor && (
            <p className="mt-3 italic text-gray-300 bg-town-surface/30 p-3 rounded-lg">
              "{manifest.metaphor}"
            </p>
          )}
        </Section>
      )}

      {/* Activity Sparkline */}
      <Section title="Activity">
        <ActivitySparkline citizen={citizen} expanded={expanded} />
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <span>Past activity</span>
          <span>Now</span>
        </div>
      </Section>

      {/* Eigenvector Preview (LOD 3) */}
      {citizen.eigenvectors && (
        <Section title="Eigenvectors">
          <EigenvectorPreview eigenvectors={citizen.eigenvectors} expanded={expanded} />
        </Section>
      )}

      {/* Cosmotechnics (LOD 2) */}
      {manifest?.cosmotechnics && (
        <Section title="Cosmotechnics">
          <div className="bg-purple-900/20 p-3 rounded-lg border border-purple-500/20">
            <span className="font-medium text-purple-300">{manifest.cosmotechnics}</span>
          </div>
        </Section>
      )}
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
        {title}
      </h3>
      {children}
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
  valueClass?: string;
  icon?: string;
}

function StatCard({ label, value, valueClass, icon }: StatCardProps) {
  return (
    <div className="bg-town-surface/30 rounded-lg p-3 border border-town-accent/20">
      <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
        {icon && <span>{icon}</span>}
        <span>{label}</span>
      </div>
      <div className={cn('font-semibold', valueClass)}>{value}</div>
    </div>
  );
}

function MoodIndicator({ mood }: { mood: string }) {
  const getMoodEmoji = (m: string) => {
    const lower = m.toLowerCase();
    if (lower.includes('happy') || lower.includes('joy')) return '😊';
    if (lower.includes('content') || lower.includes('calm')) return '😌';
    if (lower.includes('curious') || lower.includes('interested')) return '🤔';
    if (lower.includes('excited') || lower.includes('energetic')) return '🤩';
    if (lower.includes('tired') || lower.includes('weary')) return '😴';
    if (lower.includes('sad') || lower.includes('melancholy')) return '😢';
    if (lower.includes('anxious') || lower.includes('worried')) return '😰';
    if (lower.includes('angry') || lower.includes('frustrated')) return '😤';
    return '😐';
  };

  return <span className="text-2xl">{getMoodEmoji(mood)}</span>;
}

interface ActivitySparklineProps {
  citizen: CitizenCardJSON;
  expanded?: boolean;
}

function ActivitySparkline({ citizen, expanded }: ActivitySparklineProps) {
  // Generate synthetic activity data based on entropy/capability
  // In production, this would come from actual event history
  const generateActivity = () => {
    const points = expanded ? 24 : 12;
    const base = citizen.capability;
    const variance = citizen.entropy * 0.3;
    return Array.from({ length: points }, (_, i) => {
      const noise = (Math.sin(i * 0.5) + Math.cos(i * 0.3)) * variance;
      return Math.max(0, Math.min(1, base + noise * (i / points)));
    });
  };

  const values = generateActivity();
  const height = expanded ? 80 : 48;
  const width = '100%';
  const padding = 4;

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const points = values
    .map((v, i) => {
      const x = padding + (i / (values.length - 1)) * (100 - padding * 2);
      const y = height - padding - ((v - min) / range) * (height - padding * 2);
      return `${x}%,${y}`;
    })
    .join(' ');

  // Fill area path
  const areaPath = `M ${padding}%,${height - padding} ${points.split(' ').map(p => `L ${p}`).join(' ')} L ${100 - padding}%,${height - padding} Z`;

  return (
    <svg width={width} height={height} className="rounded-lg bg-town-surface/20">
      {/* Grid lines */}
      {[0.25, 0.5, 0.75].map((y) => (
        <line
          key={y}
          x1={`${padding}%`}
          y1={height * y}
          x2={`${100 - padding}%`}
          y2={height * y}
          stroke="currentColor"
          strokeOpacity="0.1"
        />
      ))}
      {/* Area fill */}
      <path d={areaPath} fill="url(#activityGradient)" opacity="0.3" />
      {/* Line */}
      <polyline
        points={points}
        fill="none"
        stroke="var(--town-highlight, #60a5fa)"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Current point */}
      {values.length > 0 && (
        <circle
          cx={`${100 - padding}%`}
          cy={height - padding - ((values[values.length - 1] - min) / range) * (height - padding * 2)}
          r="4"
          fill="var(--town-highlight, #60a5fa)"
        />
      )}
      {/* Gradient definition */}
      <defs>
        <linearGradient id="activityGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--town-highlight, #60a5fa)" stopOpacity="0.4" />
          <stop offset="100%" stopColor="var(--town-highlight, #60a5fa)" stopOpacity="0" />
        </linearGradient>
      </defs>
    </svg>
  );
}

interface EigenvectorPreviewProps {
  eigenvectors: CitizenEigenvectors;
  expanded?: boolean;
}

function EigenvectorPreview({ eigenvectors, expanded }: EigenvectorPreviewProps) {
  const vectors: { key: EigenvectorKey; label: string; color: string }[] = [
    { key: 'warmth', label: 'Warmth', color: 'bg-red-500' },
    { key: 'curiosity', label: 'Curiosity', color: 'bg-yellow-500' },
    { key: 'trust', label: 'Trust', color: 'bg-green-500' },
  ];

  const displayVectors = expanded ? vectors : vectors.slice(0, 4);

  return (
    <div className="space-y-2">
      {displayVectors.map(({ key, label, color }) => {
        const value = eigenvectors[key];
        return (
          <div key={key} className="flex items-center gap-2">
            <span className="text-xs text-gray-400 w-20">{label}</span>
            <div className="flex-1 h-2 bg-town-surface rounded-full overflow-hidden">
              <div
                className={cn('h-full transition-all duration-500', color)}
                style={{ width: `${value * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 w-10 text-right">{value.toFixed(2)}</span>
          </div>
        );
      })}
      {!expanded && vectors.length > 3 && (
        <p className="text-xs text-gray-500 mt-1">+{vectors.length - 3} more</p>
      )}
    </div>
  );
}

export default OverviewTab;
