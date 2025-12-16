/**
 * ArchetypePalette: Visual cards for archetype selection.
 *
 * Shows Scout/Sage/Spark/Steady/Sync (Workshop) or
 * Builder/Trader/Healer/Scholar/Watcher (Town) archetypes.
 */

import { cn } from '@/lib/utils';
import { ElasticCard } from '@/components/elastic';
import type { Archetype } from '@/api/types';

export interface ArchetypePaletteProps {
  selected: Archetype | null;
  onSelect: (archetype: Archetype) => void;
  variant?: 'town' | 'workshop';
  className?: string;
}

interface ArchetypeConfig {
  id: Archetype;
  icon: string;
  name: string;
  description: string;
  traits: string[];
  color: string;
  bgColor: string;
}

const TOWN_ARCHETYPES: ArchetypeConfig[] = [
  {
    id: 'Builder',
    icon: '🔨',
    name: 'Builder',
    description: 'Creates and constructs. Patient craftsperson who builds lasting things.',
    traits: ['Creative', 'Patient', 'Resilient'],
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10 hover:bg-amber-500/20 border-amber-500/30',
  },
  {
    id: 'Trader',
    icon: '💼',
    name: 'Trader',
    description: 'Connects and exchanges. Social networker who facilitates relationships.',
    traits: ['Trustworthy', 'Ambitious', 'Warm'],
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500/10 hover:bg-emerald-500/20 border-emerald-500/30',
  },
  {
    id: 'Healer',
    icon: '💚',
    name: 'Healer',
    description: 'Nurtures and restores. Compassionate caretaker who supports others.',
    traits: ['Warm', 'Patient', 'Trusting'],
    color: 'text-green-400',
    bgColor: 'bg-green-500/10 hover:bg-green-500/20 border-green-500/30',
  },
  {
    id: 'Scholar',
    icon: '📚',
    name: 'Scholar',
    description: 'Learns and teaches. Curious mind who seeks and shares knowledge.',
    traits: ['Curious', 'Patient', 'Creative'],
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10 hover:bg-blue-500/20 border-blue-500/30',
  },
  {
    id: 'Watcher',
    icon: '👁️',
    name: 'Watcher',
    description: 'Observes and protects. Vigilant guardian who notices everything.',
    traits: ['Curious', 'Patient', 'Resilient'],
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10 hover:bg-purple-500/20 border-purple-500/30',
  },
];

// Workshop archetypes (for Builders Workshop)
const WORKSHOP_ARCHETYPES: ArchetypeConfig[] = [
  {
    id: 'Builder', // Maps to Scout in workshop context
    icon: '🔍',
    name: 'Scout',
    description: 'Explores possibilities. First to venture into unknown territory.',
    traits: ['Curious', 'Adventurous', 'Quick'],
    color: 'text-green-400',
    bgColor: 'bg-green-500/10 hover:bg-green-500/20 border-green-500/30',
  },
  {
    id: 'Scholar', // Maps to Sage
    icon: '🧙',
    name: 'Sage',
    description: 'Designs solutions. Deep thinker who plans before acting.',
    traits: ['Analytical', 'Thoughtful', 'Strategic'],
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/10 hover:bg-purple-500/20 border-purple-500/30',
  },
  {
    id: 'Trader', // Maps to Spark
    icon: '✨',
    name: 'Spark',
    description: 'Prototypes rapidly. Brings ideas to life with energy and speed.',
    traits: ['Energetic', 'Creative', 'Bold'],
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10 hover:bg-amber-500/20 border-amber-500/30',
  },
  {
    id: 'Healer', // Maps to Steady
    icon: '⚓',
    name: 'Steady',
    description: 'Refines and polishes. Ensures quality and consistency.',
    traits: ['Meticulous', 'Patient', 'Reliable'],
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10 hover:bg-blue-500/20 border-blue-500/30',
  },
  {
    id: 'Watcher', // Maps to Sync
    icon: '🔗',
    name: 'Sync',
    description: 'Integrates and connects. Brings everything together harmoniously.',
    traits: ['Collaborative', 'Organized', 'Diplomatic'],
    color: 'text-pink-400',
    bgColor: 'bg-pink-500/10 hover:bg-pink-500/20 border-pink-500/30',
  },
];

export function ArchetypePalette({
  selected,
  onSelect,
  variant = 'town',
  className,
}: ArchetypePaletteProps) {
  const archetypes = variant === 'workshop' ? WORKSHOP_ARCHETYPES : TOWN_ARCHETYPES;

  return (
    <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4', className)}>
      {archetypes.map((archetype) => (
        <ArchetypeCard
          key={archetype.id}
          config={archetype}
          isSelected={selected === archetype.id}
          onSelect={() => onSelect(archetype.id)}
        />
      ))}
    </div>
  );
}

// =============================================================================
// Archetype Card
// =============================================================================

interface ArchetypeCardProps {
  config: ArchetypeConfig;
  isSelected: boolean;
  onSelect: () => void;
}

function ArchetypeCard({ config, isSelected, onSelect }: ArchetypeCardProps) {
  return (
    <ElasticCard
      onClick={onSelect}
      isSelected={isSelected}
      priority={isSelected ? 3 : 2}
      className={cn(
        'transition-all duration-200 border-2',
        isSelected
          ? `ring-2 ring-offset-2 ring-offset-town-bg ${config.bgColor.replace('border-', 'ring-')}`
          : config.bgColor
      )}
    >
      {/* Icon and Name */}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-3xl">{config.icon}</span>
        <div>
          <h3 className={cn('text-lg font-bold', config.color)}>{config.name}</h3>
          {isSelected && (
            <span className="text-xs text-green-400">✓ Selected</span>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-300 mb-3">{config.description}</p>

      {/* Traits */}
      <div className="flex flex-wrap gap-2">
        {config.traits.map((trait) => (
          <span
            key={trait}
            className={cn(
              'text-xs px-2 py-1 rounded-full',
              'bg-town-surface/50 text-gray-400'
            )}
          >
            {trait}
          </span>
        ))}
      </div>
    </ElasticCard>
  );
}

export default ArchetypePalette;
