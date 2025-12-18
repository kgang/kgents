/**
 * ObserverSelector: Switch between observer umwelts.
 *
 * Implements AGENTESE observer-dependent rendering. Different observers
 * see different affordances from the same entities.
 *
 * @see plans/park-town-design-overhaul.md (Journey 14)
 * @see spec/protocols/agentese.md
 */

import { useState, useCallback } from 'react';
import { Eye, Building2, Feather, LineChart, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import { TeachingCallout, TEACHING_MESSAGES } from '@/components/categorical/TeachingCallout';

// =============================================================================
// Types
// =============================================================================

export type ObserverUmwelt = 'default' | 'architect' | 'poet' | 'economist';

export interface ObserverConfig {
  id: ObserverUmwelt;
  label: string;
  description: string;
  icon: typeof Eye;
  color: string;
  /** What this observer perceives in the town */
  perceives: string[];
  /** Mesa rendering hints */
  mesaOverlay: 'none' | 'relationships' | 'coalitions' | 'economy';
}

export interface ObserverSelectorProps {
  /** Current selected observer */
  value: ObserverUmwelt;
  /** Callback when observer changes */
  onChange: (observer: ObserverUmwelt) => void;
  /** Compact mode for header */
  compact?: boolean;
  /** Show teaching callout */
  showTeaching?: boolean;
  /** Additional className */
  className?: string;
}

// =============================================================================
// Configuration
// =============================================================================

export const OBSERVERS: Record<ObserverUmwelt, ObserverConfig> = {
  default: {
    id: 'default',
    label: 'Default',
    description: 'Standard view',
    icon: Eye,
    color: '#64748b',
    perceives: ['Citizens', 'Regions', 'Phases'],
    mesaOverlay: 'none',
  },
  architect: {
    id: 'architect',
    label: 'Architect',
    description: 'System structure',
    icon: Building2,
    color: '#3b82f6',
    perceives: ['Relationship graphs', 'Coalition boundaries', 'System health'],
    mesaOverlay: 'relationships',
  },
  poet: {
    id: 'poet',
    label: 'Poet',
    description: 'Narrative flow',
    icon: Feather,
    color: '#8b5cf6',
    perceives: ['Story arcs', 'Metaphors', 'Emotional currents'],
    mesaOverlay: 'none',
  },
  economist: {
    id: 'economist',
    label: 'Economist',
    description: 'Resource flows',
    icon: LineChart,
    color: '#22c55e',
    perceives: ['Trade networks', 'Value creation', 'Capability markets'],
    mesaOverlay: 'economy',
  },
};

// =============================================================================
// Component
// =============================================================================

export function ObserverSelector({
  value,
  onChange,
  compact = false,
  showTeaching = false,
  className,
}: ObserverSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const currentObserver = OBSERVERS[value];
  const Icon = currentObserver.icon;

  const handleSelect = useCallback(
    (observer: ObserverUmwelt) => {
      onChange(observer);
      setIsOpen(false);
    },
    [onChange]
  );

  if (compact) {
    // Compact dropdown for header
    return (
      <div className={cn('relative', className)}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium transition-colors',
            'bg-gray-800/50 hover:bg-gray-700/50 border border-gray-700'
          )}
          style={{ color: currentObserver.color }}
        >
          <Icon className="w-3.5 h-3.5" />
          <span>{currentObserver.label}</span>
          <ChevronDown className={cn('w-3 h-3 transition-transform', isOpen && 'rotate-180')} />
        </button>

        {isOpen && (
          <>
            {/* Backdrop */}
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />

            {/* Dropdown */}
            <div className="absolute right-0 top-full mt-1 z-50 w-48 py-1 rounded-lg bg-gray-800 border border-gray-700 shadow-xl">
              {Object.values(OBSERVERS).map((obs) => {
                const ObsIcon = obs.icon;
                const isSelected = obs.id === value;
                return (
                  <button
                    key={obs.id}
                    onClick={() => handleSelect(obs.id)}
                    className={cn(
                      'w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors',
                      isSelected ? 'bg-gray-700/50' : 'hover:bg-gray-700/30'
                    )}
                  >
                    <ObsIcon className="w-4 h-4" style={{ color: obs.color }} />
                    <div className="text-left">
                      <div className="font-medium" style={{ color: isSelected ? obs.color : '#fff' }}>
                        {obs.label}
                      </div>
                      <div className="text-xs text-gray-500">{obs.description}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </>
        )}
      </div>
    );
  }

  // Full panel view
  return (
    <div className={cn('space-y-3', className)}>
      <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
        Observer Umwelt
      </div>

      <div className="grid grid-cols-2 gap-2">
        {Object.values(OBSERVERS).map((obs) => {
          const ObsIcon = obs.icon;
          const isSelected = obs.id === value;
          return (
            <button
              key={obs.id}
              onClick={() => onChange(obs.id)}
              className={cn(
                'flex flex-col items-center gap-1.5 p-3 rounded-lg text-center transition-all',
                isSelected
                  ? 'bg-gray-700/50 ring-2 ring-offset-1 ring-offset-gray-900'
                  : 'bg-gray-800/50 hover:bg-gray-700/30'
              )}
              style={{
                borderColor: isSelected ? obs.color : 'transparent',
                // Ring color set via CSS custom property
                '--tw-ring-color': isSelected ? obs.color : undefined,
              } as React.CSSProperties}
            >
              <ObsIcon className="w-5 h-5" style={{ color: obs.color }} />
              <span className="text-sm font-medium" style={{ color: isSelected ? obs.color : '#fff' }}>
                {obs.label}
              </span>
              <span className="text-xs text-gray-500">{obs.description}</span>
            </button>
          );
        })}
      </div>

      {/* What this observer perceives */}
      <div className="bg-gray-800/30 rounded-lg p-3">
        <div className="text-xs text-gray-500 mb-2">
          <Icon className="w-3 h-3 inline mr-1" style={{ color: currentObserver.color }} />
          {currentObserver.label} perceives:
        </div>
        <div className="flex flex-wrap gap-1.5">
          {currentObserver.perceives.map((item) => (
            <span
              key={item}
              className="px-2 py-0.5 text-xs rounded-full"
              style={{
                backgroundColor: `${currentObserver.color}20`,
                color: currentObserver.color,
                border: `1px solid ${currentObserver.color}40`,
              }}
            >
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* Teaching callout */}
      {showTeaching && (
        <TeachingCallout category="insight" compact>
          {TEACHING_MESSAGES.observer_dependent}
        </TeachingCallout>
      )}
    </div>
  );
}

export default ObserverSelector;
