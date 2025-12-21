/**
 * CrownJewelsSection - Quick access shortcuts to Crown Jewels
 *
 * Provides expandable shortcuts to the main Crown Jewel services.
 * Persists expansion state to localStorage independently.
 *
 * @see NavigationTree.tsx
 * @see constants/jewels.ts
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, type LucideIcon } from 'lucide-react';
import { Brain, Network, Palette, Users, Theater } from 'lucide-react';
import { getJewelColor, type JewelName } from '@/constants/jewels';

// =============================================================================
// Types
// =============================================================================

interface CrownJewel {
  name: JewelName;
  label: string;
  path: string;
  icon: LucideIcon;
  children?: Array<{ label: string; path: string }>;
}

export interface CrownJewelsSectionProps {
  currentPath: string;
  onNavigate: (path: string) => void;
}

// =============================================================================
// Constants
// =============================================================================

const STORAGE_KEY_EXPANDED_JEWELS = 'kgents:navtree:expandedJewels';

/**
 * Crown Jewel shortcuts - navigate via AGENTESE path.
 *
 * IMPORTANT: All paths MUST be registered in the AGENTESE registry.
 * The registry (@node decorator) is the single source of truth.
 */
const CROWN_JEWELS: CrownJewel[] = [
  { name: 'brain', label: 'Brain', path: 'self.memory', icon: Brain },
  { name: 'gestalt', label: 'Gestalt', path: 'world.codebase', icon: Network },
  { name: 'forge', label: 'Forge', path: 'world.forge', icon: Palette },
  {
    name: 'coalition',
    label: 'Coalition',
    path: 'world.town',
    icon: Users,
    children: [
      { label: 'Overview', path: 'world.town' },
      { label: 'Citizens', path: 'world.town.citizen' },
      { label: 'Coalitions', path: 'world.town.coalition' },
      { label: 'Inhabit', path: 'world.town.inhabit' },
    ],
  },
  { name: 'park', label: 'Park', path: 'world.park', icon: Theater },
];

// =============================================================================
// Component
// =============================================================================

export function CrownJewelsSection({ currentPath, onNavigate }: CrownJewelsSectionProps) {
  // Track expanded jewels - persisted to localStorage
  const [expandedJewels, setExpandedJewels] = useState<Set<string>>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY_EXPANDED_JEWELS);
      if (stored) {
        return new Set(JSON.parse(stored));
      }
    } catch {
      // Ignore parse errors
    }
    return new Set();
  });

  // Persist expandedJewels to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_EXPANDED_JEWELS, JSON.stringify([...expandedJewels]));
    } catch {
      // Ignore storage errors
    }
  }, [expandedJewels]);

  const toggleJewel = (name: string) => {
    setExpandedJewels((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  };

  return (
    <div className="border-t border-gray-700/50 pt-3">
      <h3 className="px-3 mb-2 text-xs font-medium text-gray-500 uppercase tracking-wider">
        Crown Jewels
      </h3>
      <div className="space-y-0.5">
        {CROWN_JEWELS.map((jewel) => {
          const isActive = currentPath === jewel.path || currentPath.startsWith(`${jewel.path}.`);
          const isExpanded = expandedJewels.has(jewel.name);
          const hasChildren = jewel.children && jewel.children.length > 0;
          const color = getJewelColor(jewel.name);
          const Icon = jewel.icon;

          return (
            <div key={jewel.name}>
              <button
                onClick={() => {
                  if (hasChildren) {
                    toggleJewel(jewel.name);
                  } else {
                    onNavigate(jewel.path);
                  }
                }}
                className={`
                  w-full flex items-center gap-2 px-3 py-1.5 text-sm
                  hover:bg-gray-700/50 transition-colors rounded-md
                  ${isActive ? 'bg-gray-700/70' : ''}
                `}
              >
                {hasChildren && (
                  <motion.span
                    animate={{ rotate: isExpanded ? 90 : 0 }}
                    transition={{ duration: 0.15 }}
                    className="flex-shrink-0"
                  >
                    <ChevronRight className="w-3 h-3 text-gray-500" />
                  </motion.span>
                )}
                <Icon className="w-4 h-4" style={{ color: color.primary }} />
                <span className={isActive ? 'text-white' : 'text-gray-300'}>{jewel.label}</span>
                <span className="ml-auto text-xs text-gray-500 font-mono">{jewel.path}</span>
              </button>

              {/* Children */}
              <AnimatePresence>
                {hasChildren && isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    className="overflow-hidden"
                  >
                    {jewel.children?.map((child) => {
                      const childActive =
                        currentPath === child.path || currentPath.startsWith(`${child.path}.`);

                      return (
                        <button
                          key={child.path}
                          onClick={() => onNavigate(child.path)}
                          className={`
                            w-full flex items-center gap-2 pl-10 pr-3 py-1 text-sm
                            hover:bg-gray-700/30 transition-colors rounded-md
                            ${childActive ? 'bg-gray-700/50 text-white' : 'text-gray-400'}
                          `}
                        >
                          <span>{child.label}</span>
                          <span className="ml-auto text-xs text-gray-600 font-mono">
                            {child.path.split('.').pop()}
                          </span>
                        </button>
                      );
                    })}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default CrownJewelsSection;
