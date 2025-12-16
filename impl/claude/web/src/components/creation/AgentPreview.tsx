/**
 * AgentPreview: Live preview of agent configuration before creation.
 *
 * Shows name, archetype, eigenvectors, and predicted personality traits.
 */

import { cn } from '@/lib/utils';
import { ElasticCard } from '@/components/elastic';
import type { Archetype, Eigenvectors } from '@/api/types';

export interface AgentPreviewProps {
  config: {
    name: string;
    archetype: Archetype | null;
    eigenvectors: Partial<Eigenvectors>;
    region?: string;
  };
  onEdit?: () => void;
  className?: string;
}

const ARCHETYPE_CONFIG: Record<
  Archetype,
  { icon: string; color: string; description: string }
> = {
  Builder: { icon: '🔨', color: 'text-amber-400', description: 'Creates and constructs' },
  Trader: { icon: '💼', color: 'text-emerald-400', description: 'Connects and exchanges' },
  Healer: { icon: '💚', color: 'text-green-400', description: 'Nurtures and restores' },
  Scholar: { icon: '📚', color: 'text-blue-400', description: 'Learns and teaches' },
  Watcher: { icon: '👁️', color: 'text-purple-400', description: 'Observes and protects' },
};

export function AgentPreview({ config, onEdit, className }: AgentPreviewProps) {
  const archetypeConfig = config.archetype ? ARCHETYPE_CONFIG[config.archetype] : null;
  const eigenvectors = config.eigenvectors as Eigenvectors;

  // Predict personality traits based on eigenvectors
  const traits = predictTraits(eigenvectors);

  return (
    <div className={cn('space-y-6', className)}>
      {/* Main Preview Card */}
      <ElasticCard className="relative overflow-hidden">
        {/* Background gradient based on archetype */}
        {archetypeConfig && (
          <div
            className="absolute inset-0 opacity-10"
            style={{
              background: `radial-gradient(circle at 30% 30%, ${getArchetypeHex(config.archetype!)}, transparent 70%)`,
            }}
          />
        )}

        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 rounded-full bg-town-surface/50 flex items-center justify-center text-3xl">
              {archetypeConfig?.icon || '👤'}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold">{config.name || 'Unnamed Citizen'}</h2>
              {archetypeConfig && (
                <p className={cn('text-sm', archetypeConfig.color)}>
                  {config.archetype} · {archetypeConfig.description}
                </p>
              )}
            </div>
            {onEdit && (
              <button
                onClick={onEdit}
                className="px-3 py-1 text-sm bg-town-surface/50 hover:bg-town-accent/30 rounded-lg transition-colors"
              >
                ✏️ Edit
              </button>
            )}
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <StatBox
              label="Starting Phase"
              value="IDLE"
              icon="🔄"
              description="Will begin in idle phase"
            />
            <StatBox
              label="Region"
              value={config.region || 'Auto-assigned'}
              icon="📍"
              description="Location in town"
            />
          </div>

          {/* Eigenvector Summary */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
              Personality Profile
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(eigenvectors).slice(0, 6).map(([key, value]) => (
                <EigenvectorBar key={key} label={key} value={value as number} />
              ))}
            </div>
          </div>

          {/* Predicted Traits */}
          <div>
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
              Predicted Traits
            </h3>
            <div className="flex flex-wrap gap-2">
              {traits.map((trait) => (
                <span
                  key={trait}
                  className="px-3 py-1 text-sm bg-town-highlight/20 text-town-highlight rounded-full"
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>
        </div>
      </ElasticCard>

      {/* Preview Notes */}
      <div className="bg-town-surface/20 rounded-lg p-4 border border-town-accent/20">
        <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
          <span>💡</span>
          <span>What happens next?</span>
        </h3>
        <ul className="text-sm text-gray-400 space-y-1">
          <li>• Citizen will spawn in the town with these characteristics</li>
          <li>• Initial phase will be IDLE, transitioning based on town activity</li>
          <li>• Eigenvectors will drift slightly over time through interactions</li>
          <li>• You can INHABIT this citizen to experience their perspective</li>
        </ul>
      </div>

      {/* Simulation Preview */}
      <SimulationPreview config={config} />
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface StatBoxProps {
  label: string;
  value: string;
  icon: string;
  description: string;
}

function StatBox({ label, value, icon, description }: StatBoxProps) {
  return (
    <div className="bg-town-surface/30 rounded-lg p-3" title={description}>
      <div className="flex items-center gap-2 text-gray-400 text-xs mb-1">
        <span>{icon}</span>
        <span>{label}</span>
      </div>
      <div className="font-semibold">{value}</div>
    </div>
  );
}

function EigenvectorBar({ label, value }: { label: string; value: number }) {
  const colors: Record<string, string> = {
    warmth: 'bg-red-500',
    curiosity: 'bg-yellow-500',
    trust: 'bg-green-500',
    creativity: 'bg-purple-500',
    patience: 'bg-blue-500',
    resilience: 'bg-orange-500',
    ambition: 'bg-pink-500',
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-gray-400 w-16 capitalize">{label}</span>
      <div className="flex-1 h-1.5 bg-town-surface rounded-full overflow-hidden">
        <div
          className={cn('h-full transition-all', colors[label] || 'bg-gray-500')}
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="text-xs text-gray-500 w-8 text-right">{value.toFixed(2)}</span>
    </div>
  );
}

function SimulationPreview({ config }: { config: AgentPreviewProps['config'] }) {
  // Generate a simple predicted behavior based on eigenvectors
  const behaviors = predictBehaviors(config.eigenvectors as Eigenvectors);

  return (
    <ElasticCard className="bg-gradient-to-br from-town-surface/30 to-transparent">
      <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
        Predicted Behaviors
      </h3>
      <div className="space-y-3">
        {behaviors.map((behavior, i) => (
          <div key={i} className="flex items-start gap-3">
            <span className="text-lg">{behavior.icon}</span>
            <div>
              <div className="font-medium text-sm">{behavior.action}</div>
              <div className="text-xs text-gray-500">{behavior.likelihood}</div>
            </div>
          </div>
        ))}
      </div>
    </ElasticCard>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getArchetypeHex(archetype: Archetype): string {
  const colors: Record<Archetype, string> = {
    Builder: '#f59e0b',
    Trader: '#10b981',
    Healer: '#22c55e',
    Scholar: '#3b82f6',
    Watcher: '#a855f7',
  };
  return colors[archetype];
}

function predictTraits(eigenvectors: Eigenvectors): string[] {
  const traits: string[] = [];

  if (eigenvectors.warmth > 0.7) traits.push('Warm-hearted');
  if (eigenvectors.warmth < 0.3) traits.push('Reserved');

  if (eigenvectors.curiosity > 0.7) traits.push('Inquisitive');
  if (eigenvectors.curiosity < 0.3) traits.push('Focused');

  if (eigenvectors.trust > 0.7) traits.push('Open');
  if (eigenvectors.trust < 0.3) traits.push('Cautious');

  if (eigenvectors.creativity > 0.7) traits.push('Inventive');
  if (eigenvectors.creativity < 0.3) traits.push('Methodical');

  if (eigenvectors.patience > 0.7) traits.push('Patient');
  if (eigenvectors.patience < 0.3) traits.push('Eager');

  if (eigenvectors.resilience > 0.7) traits.push('Resilient');
  if (eigenvectors.resilience < 0.3) traits.push('Sensitive');

  if (eigenvectors.ambition > 0.7) traits.push('Driven');
  if (eigenvectors.ambition < 0.3) traits.push('Content');

  // Ensure we have at least 3 traits
  if (traits.length < 3) {
    if (eigenvectors.warmth >= 0.5 && !traits.includes('Warm-hearted'))
      traits.push('Friendly');
    if (eigenvectors.curiosity >= 0.5 && !traits.includes('Inquisitive'))
      traits.push('Curious');
    if (eigenvectors.resilience >= 0.5 && !traits.includes('Resilient'))
      traits.push('Steady');
  }

  return traits.slice(0, 5);
}

function predictBehaviors(
  eigenvectors: Eigenvectors
): { icon: string; action: string; likelihood: string }[] {
  const behaviors: { icon: string; action: string; likelihood: string }[] = [];

  if (eigenvectors.curiosity > 0.6) {
    behaviors.push({
      icon: '🔍',
      action: 'Explores new areas frequently',
      likelihood: 'Very likely',
    });
  }

  if (eigenvectors.warmth > 0.6 && eigenvectors.trust > 0.5) {
    behaviors.push({
      icon: '💬',
      action: 'Initiates conversations with others',
      likelihood: 'Likely',
    });
  }

  if (eigenvectors.creativity > 0.6) {
    behaviors.push({
      icon: '💡',
      action: 'Proposes novel solutions',
      likelihood: 'Likely',
    });
  }

  if (eigenvectors.patience > 0.6 && eigenvectors.resilience > 0.5) {
    behaviors.push({
      icon: '⏳',
      action: 'Persists through difficult tasks',
      likelihood: 'Very likely',
    });
  }

  if (eigenvectors.ambition > 0.7) {
    behaviors.push({
      icon: '🎯',
      action: 'Takes on challenging goals',
      likelihood: 'Very likely',
    });
  }

  // Default behaviors
  if (behaviors.length < 3) {
    behaviors.push({
      icon: '🔄',
      action: 'Follows daily routines',
      likelihood: 'Moderate',
    });
  }

  return behaviors.slice(0, 4);
}

export default AgentPreview;
