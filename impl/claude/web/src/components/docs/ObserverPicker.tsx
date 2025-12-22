/**
 * ObserverPicker - Prominent observer selection that changes everything.
 *
 * "When you switch observer, the UI should feel different"
 *
 * This is NOT hidden in headers. It's THE primary control because in AGENTESE,
 * the observer determines what you can see and do.
 *
 * Now with Umwelt visualization: when you switch observers, a ripple
 * emanates from the picker, signaling "reality is shifting."
 *
 * @see plans/umwelt-visualization.md
 */

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Eye, User, Code, Shield, Crown, Users, Sparkles, ChevronDown, Check } from 'lucide-react';
import type { Density } from '@/hooks/useDesignPolynomial';
import { UmweltRipple, useUmweltSafe, getObserverColor } from './umwelt';

// =============================================================================
// Types
// =============================================================================

export interface Observer {
  archetype: string;
  capabilities: string[];
}

export interface ObserverPickerProps {
  observer: Observer;
  onChange: (observer: Observer) => void;
  density: Density;
}

// =============================================================================
// Observer Archetypes
// =============================================================================

interface ArchetypeInfo {
  id: string;
  label: string;
  description: string;
  icon: typeof Eye;
  color: string;
  bgColor: string;
  capabilities: string[];
}

const ARCHETYPES: ArchetypeInfo[] = [
  {
    id: 'guest',
    label: 'Guest',
    description: 'Read-only observer',
    icon: Eye,
    color: 'text-gray-400',
    bgColor: 'bg-gray-600/20',
    capabilities: ['read'],
  },
  {
    id: 'user',
    label: 'User',
    description: 'Standard user access',
    icon: User,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-600/20',
    capabilities: ['read', 'write'],
  },
  {
    id: 'developer',
    label: 'Developer',
    description: 'Full access + diagnostics',
    icon: Code,
    color: 'text-green-400',
    bgColor: 'bg-green-600/20',
    capabilities: ['read', 'write', 'admin'],
  },
  {
    id: 'mayor',
    label: 'Mayor',
    description: 'Town governance authority',
    icon: Crown,
    color: 'text-amber-400',
    bgColor: 'bg-amber-600/20',
    capabilities: ['read', 'write', 'admin', 'govern'],
  },
  {
    id: 'coalition',
    label: 'Coalition',
    description: 'Multi-agent collective',
    icon: Users,
    color: 'text-violet-400',
    bgColor: 'bg-violet-600/20',
    capabilities: ['read', 'write', 'collaborate'],
  },
  {
    id: 'void',
    label: 'Void Walker',
    description: 'Entropy & serendipity',
    icon: Sparkles,
    color: 'text-pink-400',
    bgColor: 'bg-pink-600/20',
    capabilities: ['read', 'void'],
  },
];

// =============================================================================
// Component
// =============================================================================

export function ObserverPicker({ observer, onChange, density }: ObserverPickerProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Get umwelt context (may be null if not wrapped in provider)
  const umwelt = useUmweltSafe();

  const currentArchetype = ARCHETYPES.find((a) => a.id === observer.archetype) || ARCHETYPES[2];
  const Icon = currentArchetype.icon;

  // Get observer color (from umwelt if available, else derive)
  const observerColor = umwelt?.observerColor ?? getObserverColor(observer.archetype);

  const handleSelect = useCallback(
    (archetype: ArchetypeInfo) => {
      onChange({
        archetype: archetype.id,
        capabilities: archetype.capabilities,
      });
      setIsOpen(false);
    },
    [onChange]
  );

  // Compact: Horizontal pill
  if (density === 'compact') {
    return (
      <div className="relative px-4 py-2 border-b border-gray-700 bg-gray-800/50">
        {/* Umwelt ripple for compact mode */}
        {umwelt && (
          <UmweltRipple isVisible={umwelt.showRipple} color={observerColor} className="z-0" />
        )}

        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`
            relative z-10 flex items-center gap-2 px-3 py-1.5 rounded-full
            ${currentArchetype.bgColor} ${currentArchetype.color}
            border border-current/30 transition-all
            active:scale-95
          `}
        >
          <Icon className="w-4 h-4" />
          <span className="text-sm font-medium">{currentArchetype.label}</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>

        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute top-full left-0 right-0 z-50 mt-2 mx-4 bg-gray-800 rounded-lg shadow-xl border border-gray-700 overflow-hidden"
            >
              {ARCHETYPES.map((archetype) => (
                <ArchetypeOption
                  key={archetype.id}
                  archetype={archetype}
                  isSelected={archetype.id === observer.archetype}
                  onSelect={() => handleSelect(archetype)}
                  compact
                />
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }

  // Comfortable/Spacious: Full bar with visible options
  return (
    <div
      className={`
        relative flex items-center gap-4 px-4 py-2 border-b border-gray-700
        bg-gradient-to-r from-gray-800/50 to-gray-900/50 overflow-hidden
      `}
      style={{
        // Observer color tints the header
        borderBottomColor: `color-mix(in srgb, ${observerColor} 30%, transparent)`,
        transition: 'border-color 100ms ease-out',
      }}
    >
      {/* Umwelt ripple for comfortable/spacious mode */}
      {umwelt && (
        <UmweltRipple isVisible={umwelt.showRipple} color={observerColor} className="z-0" />
      )}
      <div className="flex items-center gap-2">
        <Shield className="w-4 h-4 text-gray-500" />
        <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Observer</span>
      </div>

      <div className="flex items-center gap-1 flex-1">
        {ARCHETYPES.map((archetype) => {
          const ArchIcon = archetype.icon;
          const isSelected = archetype.id === observer.archetype;

          return (
            <button
              key={archetype.id}
              onClick={() => handleSelect(archetype)}
              title={archetype.description}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm
                transition-all duration-200
                ${
                  isSelected
                    ? `${archetype.bgColor} ${archetype.color} ring-1 ring-current/50`
                    : 'text-gray-500 hover:text-gray-300 hover:bg-gray-700/50'
                }
              `}
            >
              <ArchIcon className="w-4 h-4" />
              {density === 'spacious' && <span className="font-medium">{archetype.label}</span>}
            </button>
          );
        })}
      </div>

      {/* Current capabilities */}
      <div className="flex items-center gap-1">
        {observer.capabilities.map((cap) => (
          <span key={cap} className="px-2 py-0.5 text-xs rounded bg-gray-700/50 text-gray-400">
            {cap}
          </span>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Subcomponents
// =============================================================================

function ArchetypeOption({
  archetype,
  isSelected,
  onSelect,
  compact = false,
}: {
  archetype: ArchetypeInfo;
  isSelected: boolean;
  onSelect: () => void;
  compact?: boolean;
}) {
  const Icon = archetype.icon;

  return (
    <button
      onClick={onSelect}
      className={`
        w-full flex items-center gap-3 px-4 py-3 text-left
        transition-colors
        ${isSelected ? archetype.bgColor : 'hover:bg-gray-700/50'}
      `}
    >
      <Icon className={`w-5 h-5 ${archetype.color}`} />
      <div className="flex-1">
        <div className={`font-medium ${isSelected ? archetype.color : 'text-white'}`}>
          {archetype.label}
        </div>
        {!compact && <div className="text-xs text-gray-400">{archetype.description}</div>}
      </div>
      {isSelected && <Check className={`w-4 h-4 ${archetype.color}`} />}
    </button>
  );
}

export default ObserverPicker;
