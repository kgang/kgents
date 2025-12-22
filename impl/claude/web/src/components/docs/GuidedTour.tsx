/**
 * GuidedTour - First-load experience showing the five contexts.
 *
 * AD-010 Habitat Guarantee: No blank pages.
 *
 * This shows a beautiful overview of the AGENTESE universe,
 * with representative paths from each context that can be
 * clicked to start exploring.
 */

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Globe, User, BookOpen, Sparkles, Clock, ArrowRight, type LucideIcon } from 'lucide-react';
import type { PathMetadata } from './useAgenteseDiscovery';

// =============================================================================
// Types
// =============================================================================

interface GuidedTourProps {
  paths: string[];
  metadata: Record<string, PathMetadata>;
  onSelectPath: (path: string) => void;
}

interface ContextCard {
  key: string;
  label: string;
  tagline: string;
  icon: LucideIcon;
  color: string;
  bgColor: string;
  borderColor: string;
}

// =============================================================================
// Context Cards
// =============================================================================

const CONTEXTS: ContextCard[] = [
  {
    key: 'world',
    label: 'World',
    tagline: 'External entities and environments',
    icon: Globe,
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
  },
  {
    key: 'self',
    label: 'Self',
    tagline: 'Internal memory and capability',
    icon: User,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500/10',
    borderColor: 'border-cyan-500/30',
  },
  {
    key: 'concept',
    label: 'Concept',
    tagline: 'Abstract definitions and logic',
    icon: BookOpen,
    color: 'text-violet-400',
    bgColor: 'bg-violet-500/10',
    borderColor: 'border-violet-500/30',
  },
  {
    key: 'void',
    label: 'Void',
    tagline: 'The accursed share',
    icon: Sparkles,
    color: 'text-pink-400',
    bgColor: 'bg-pink-500/10',
    borderColor: 'border-pink-500/30',
  },
  {
    key: 'time',
    label: 'Time',
    tagline: 'Traces and schedules',
    icon: Clock,
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/10',
    borderColor: 'border-amber-500/30',
  },
];

// =============================================================================
// Component
// =============================================================================

export function GuidedTour({ paths, metadata, onSelectPath }: GuidedTourProps) {
  // Get representative paths for each context
  const contextPaths = useMemo(() => {
    const result: Record<string, string[]> = {};

    for (const context of CONTEXTS) {
      const contextPathList = paths.filter((p) => p.startsWith(`${context.key}.`)).slice(0, 3); // Max 3 per context
      result[context.key] = contextPathList;
    }

    return result;
  }, [paths]);

  return (
    <div className="h-full overflow-auto p-6">
      <motion.div
        className="max-w-4xl mx-auto"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* Header */}
        <div className="text-center mb-12">
          <motion.h1
            className="text-3xl font-bold text-white mb-4"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            Welcome to AGENTESE
          </motion.h1>
          <motion.p
            className="text-gray-400 text-lg max-w-2xl mx-auto"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            The universal protocol for agent-world interaction.
            <br />
            <span className="text-cyan-400 italic">
              "The noun is a lie. There is only the rate of change."
            </span>
          </motion.p>
        </div>

        {/* Context Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
          {CONTEXTS.map((context, i) => {
            const Icon = context.icon;
            const contextPathList = contextPaths[context.key] || [];

            return (
              <motion.div
                key={context.key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + i * 0.05 }}
                className={`
                  relative p-5 rounded-xl border ${context.borderColor}
                  ${context.bgColor} backdrop-blur-sm
                  hover:border-opacity-60 transition-all group
                `}
              >
                {/* Icon and label */}
                <div className="flex items-center gap-3 mb-3">
                  <div
                    className={`
                      w-10 h-10 rounded-lg flex items-center justify-center
                      ${context.bgColor} border ${context.borderColor}
                    `}
                  >
                    <Icon className={`w-5 h-5 ${context.color}`} />
                  </div>
                  <div>
                    <h3 className={`font-semibold ${context.color}`}>{context.label}</h3>
                    <p className="text-xs text-gray-500">{context.tagline}</p>
                  </div>
                </div>

                {/* Sample paths */}
                <div className="space-y-1">
                  {contextPathList.length > 0 ? (
                    contextPathList.map((path) => (
                      <button
                        key={path}
                        onClick={() => onSelectPath(path)}
                        className={`
                          w-full flex items-center gap-2 px-3 py-1.5 rounded-lg
                          text-sm text-left text-gray-300
                          hover:bg-white/5 transition-colors group/path
                        `}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${context.color.replace('text-', 'bg-')}`}
                        />
                        <span className="flex-1 truncate font-mono text-xs">{path}</span>
                        <ArrowRight className="w-3 h-3 text-gray-500 opacity-0 group-hover/path:opacity-100 transition-opacity" />
                      </button>
                    ))
                  ) : (
                    <p className="text-xs text-gray-600 italic px-3 py-2">No paths registered</p>
                  )}
                </div>

                {/* Count badge */}
                {contextPathList.length > 0 && (
                  <div className="absolute top-4 right-4">
                    <span className="px-2 py-0.5 text-xs rounded-full bg-gray-700/50 text-gray-400">
                      {paths.filter((p) => p.startsWith(`${context.key}.`)).length}
                    </span>
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Quick stats */}
        <motion.div
          className="flex items-center justify-center gap-8 text-sm text-gray-500"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <div>
            <span className="text-2xl font-bold text-cyan-400">{paths.length}</span>
            <span className="ml-2">registered paths</span>
          </div>
          <div className="w-px h-6 bg-gray-700" />
          <div>
            <span className="text-2xl font-bold text-green-400">
              {Object.values(metadata).reduce((acc, m) => acc + (m.aspects?.length || 0), 0)}
            </span>
            <span className="ml-2">total aspects</span>
          </div>
          <div className="w-px h-6 bg-gray-700" />
          <div>
            <span className="text-2xl font-bold text-violet-400">5</span>
            <span className="ml-2">contexts</span>
          </div>
        </motion.div>

        {/* Call to action */}
        <motion.div
          className="mt-12 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <p className="text-gray-500 text-sm">
            Select a path from the explorer to begin your journey
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}

export default GuidedTour;
