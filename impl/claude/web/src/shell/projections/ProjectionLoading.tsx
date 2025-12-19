/**
 * ProjectionLoading - Loading state for AGENTESE projections
 *
 * Shows a contextual loading indicator while fetching AGENTESE data.
 * Uses Living Earth aesthetic with path-aware messaging.
 *
 * @see spec/protocols/agentese-as-route.md
 */

import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import type { ProjectionLoadingProps } from './types';
import { formatPathLabel, getHolon } from '@/utils/parseAgentesePath';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';

/**
 * Context-aware loading messages
 */
const LOADING_MESSAGES: Record<string, string> = {
  world: 'Exploring the world...',
  self: 'Reflecting inward...',
  concept: 'Contemplating abstractions...',
  void: 'Embracing entropy...',
  time: 'Tracing temporal threads...',
};

/**
 * Holon-specific loading messages
 */
const HOLON_MESSAGES: Record<string, string> = {
  town: 'Gathering citizens...',
  memory: 'Surfacing memories...',
  gardener: 'Tending the garden...',
  forge: 'Heating the forge...',
  differance: 'Following the ghosts...',
  coalition: 'Assembling the coalition...',
  park: 'Opening the park...',
  codebase: 'Analyzing architecture...',
};

export function ProjectionLoading({ path, aspect }: ProjectionLoadingProps) {
  const { shouldAnimate } = useMotionPreferences();
  const context = path.split('.')[0];
  const holon = getHolon(path);
  const label = formatPathLabel(path);

  // Get contextual message
  const message =
    (holon && HOLON_MESSAGES[holon]) || LOADING_MESSAGES[context] || 'Invoking AGENTESE...';

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] p-8">
      {/* Breathing loader */}
      <motion.div
        className="relative"
        animate={
          shouldAnimate
            ? {
                scale: [1, 1.1, 1],
                opacity: [0.7, 1, 0.7],
              }
            : {}
        }
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        <Loader2 className="w-12 h-12 text-accent-sage animate-spin" />
      </motion.div>

      {/* Path info */}
      <div className="mt-6 text-center">
        <p className="text-lg text-content-primary">{message}</p>
        <code className="mt-2 block text-sm text-content-tertiary font-mono">
          {path}
          {aspect !== 'manifest' && `:${aspect}`}
        </code>
      </div>

      {/* Entity label */}
      {label && (
        <motion.p
          className="mt-4 text-sm text-content-secondary"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          Loading {label}...
        </motion.p>
      )}
    </div>
  );
}

export default ProjectionLoading;
