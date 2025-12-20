/**
 * GhostAspectDetail - Explorable locked aspects with capability pathway
 *
 * "The paths not taken are as important as the path taken."
 *
 * Ghost aspects shouldn't feel like dead ends—they should feel like
 * doorways to possibility. This component shows:
 * - What capability is required
 * - Which archetypes have that capability
 * - A "Preview As" button to temporarily elevate
 * - Optional schema preview if available
 *
 * @see plans/umwelt-v2-expansion.md (2C. Ghost Aspect Interaction)
 */

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Lock, Eye, ChevronRight, Sparkles } from 'lucide-react';
import type { Observer } from '../ObserverPicker';
import type { AspectMetadataEntry } from '../useAgenteseDiscovery';

// =============================================================================
// Types
// =============================================================================

interface GhostAspectDetailProps {
  /** The ghost aspect name */
  aspect: string;
  /** Path this aspect belongs to */
  path: string;
  /** Capability required for this aspect */
  requiredCapability: string;
  /** Current observer (for context) */
  observer: Observer;
  /** Per-aspect metadata if available */
  aspectMetadata?: AspectMetadataEntry;
  /** Schema preview if available */
  schemaPreview?: {
    request?: Record<string, unknown>;
    response?: Record<string, unknown>;
  };
  /** Callback when user wants to preview as different archetype */
  onPreviewAs?: (archetype: string) => void;
  /** Density mode */
  density: 'compact' | 'comfortable' | 'spacious';
}

// =============================================================================
// Archetype → Capability Mapping
// =============================================================================

/**
 * Which archetypes have which capabilities.
 * Used to show "Available to:" list.
 */
const ARCHETYPE_CAPABILITIES: Record<string, string[]> = {
  guest: ['read'],
  user: ['read', 'write'],
  developer: ['read', 'write', 'admin'],
  mayor: ['read', 'write', 'admin', 'govern'],
  coalition: ['read', 'write', 'collaborate'],
  void: ['read', 'void'],
};

/**
 * Find all archetypes that have a given capability.
 */
function getArchetypesWithCapability(capability: string): string[] {
  return Object.entries(ARCHETYPE_CAPABILITIES)
    .filter(([_, caps]) => caps.includes(capability))
    .map(([archetype]) => archetype);
}

/**
 * Human-readable capability descriptions.
 */
const CAPABILITY_DESCRIPTIONS: Record<string, string> = {
  read: 'View information and state',
  write: 'Create, update, or delete data',
  admin: 'System administration and diagnostics',
  govern: 'Town governance and policy decisions',
  collaborate: 'Multi-agent coordination',
  void: 'Entropy and serendipity access',
};

// =============================================================================
// Component
// =============================================================================

export function GhostAspectDetail({
  aspect,
  path,
  requiredCapability,
  observer,
  aspectMetadata,
  schemaPreview,
  onPreviewAs,
  density,
}: GhostAspectDetailProps) {
  // Find archetypes that can access this aspect
  const availableArchetypes = useMemo(
    () => getArchetypesWithCapability(requiredCapability),
    [requiredCapability]
  );

  // Filter out current observer's archetype (they don't have it)
  const suggestedArchetypes = useMemo(
    () => availableArchetypes.filter((a) => a !== observer.archetype),
    [availableArchetypes, observer.archetype]
  );

  // Compact mode: Just show lock icon and capability
  if (density === 'compact') {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-gray-800/50 rounded-lg">
        <Lock className="w-4 h-4 text-gray-500" />
        <span className="text-sm text-gray-400">Requires {requiredCapability}</span>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-800/70 rounded-lg border border-gray-700/50 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center gap-3 p-4 border-b border-gray-700/50">
        <div className="w-10 h-10 rounded-lg bg-gray-700/50 flex items-center justify-center">
          <Lock className="w-5 h-5 text-gray-400" />
        </div>
        <div className="flex-1">
          <div className="font-medium text-gray-300">{aspect}</div>
          <div className="text-xs text-gray-500">{path}</div>
        </div>
      </div>

      {/* Capability explanation */}
      <div className="p-4 space-y-4">
        <div>
          <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">
            Required Capability
          </div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-1 rounded bg-amber-500/20 text-amber-400 text-sm font-medium">
              {requiredCapability}
            </span>
            <span className="text-sm text-gray-400">
              {CAPABILITY_DESCRIPTIONS[requiredCapability] || 'Special access required'}
            </span>
          </div>
        </div>

        {/* Available to */}
        {suggestedArchetypes.length > 0 && (
          <div>
            <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
              Available to
            </div>
            <div className="flex flex-wrap gap-2">
              {suggestedArchetypes.map((archetype) => (
                <button
                  key={archetype}
                  onClick={() => onPreviewAs?.(archetype)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full
                             bg-gray-700/50 text-gray-300 text-sm
                             hover:bg-gray-600/50 transition-colors group"
                >
                  <span className="capitalize">{archetype}</span>
                  {onPreviewAs && (
                    <Eye className="w-3 h-3 text-gray-500 group-hover:text-cyan-400 transition-colors" />
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Preview As CTA (only in spacious mode with callback) */}
        {density === 'spacious' && onPreviewAs && suggestedArchetypes.length > 0 && (
          <div className="pt-2">
            <button
              onClick={() => onPreviewAs(suggestedArchetypes[0])}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg
                         bg-cyan-600/20 text-cyan-400 font-medium
                         hover:bg-cyan-600/30 transition-colors"
            >
              <Sparkles className="w-4 h-4" />
              <span>Preview as {suggestedArchetypes[0]}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
            <p className="text-xs text-gray-500 text-center mt-2">
              See what this aspect looks like with elevated access
            </p>
          </div>
        )}

        {/* Schema preview (spacious only) */}
        {density === 'spacious' && schemaPreview && (
          <div>
            <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
              Schema Preview
            </div>
            <pre className="text-xs text-gray-400 bg-gray-900/50 rounded-lg p-3 overflow-auto max-h-32">
              {JSON.stringify(schemaPreview, null, 2)}
            </pre>
          </div>
        )}

        {/* Aspect metadata (if available) */}
        {aspectMetadata?.description && (
          <div className="text-sm text-gray-400 italic">
            {aspectMetadata.description}
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default GhostAspectDetail;
