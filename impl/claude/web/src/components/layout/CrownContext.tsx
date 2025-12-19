/**
 * CrownContext - Active Crown State Display
 *
 * Shows the current session context in the nav header:
 * - Active Gardener session phase
 * - Recent Brain crystals count
 * - Active Park mask (if any)
 * - Current AGENTESE path
 *
 * This makes the Crown feel unified - users see cross-jewel state.
 *
 * Wave 4: Connected to real API data from Brain and Gardener.
 */

import { useState, useEffect, useCallback } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { JEWEL_INFO, type Jewel } from '../synergy/types';
import { brainApi, gardenerApi } from '../../api/client';

/**
 * Map AGENTESE paths to jewels for display.
 * The URL IS the AGENTESE path - no translation needed.
 */
const PATH_TO_JEWEL: Record<string, Jewel> = {
  '/self.memory': 'brain',
  '/world.codebase': 'gestalt',
  '/world.gestalt.live': 'gestalt',
  '/concept.gardener': 'gardener',
  '/self.garden': 'gardener',
  '/world.forge': 'forge',
  '/world.town': 'coalition',
  '/world.domain': 'coalition',
  '/world.park': 'park',
  '/time.differance': 'gestalt',
};

/**
 * Map paths to display AGENTESE context.
 */
const PATH_TO_AGENTESE: Record<string, string> = {
  '/self.memory': 'self.memory.*',
  '/world.codebase': 'world.codebase.*',
  '/world.gestalt.live': 'world.gestalt.live.*',
  '/concept.gardener': 'concept.gardener.*',
  '/self.garden': 'self.garden.*',
  '/world.forge': 'world.forge.*',
  '/world.town': 'world.town.*',
  '/world.domain': 'world.domain.*',
  '/world.park': 'world.park.*',
  '/time.differance': 'time.differance.*',
};

interface CrownState {
  /** Current gardener session phase (if active) */
  gardenerPhase?: string;
  /** Number of brain crystals */
  crystalCount?: number;
  /** Currently worn park mask (if any) */
  activeMask?: string;
  /** Active Gardener season */
  season?: string;
  /** Whether data is loading */
  loading?: boolean;
}

/**
 * Get jewel from AGENTESE pathname.
 */
function getJewelFromPath(pathname: string): Jewel | undefined {
  // Check for exact match first
  if (PATH_TO_JEWEL[pathname]) {
    return PATH_TO_JEWEL[pathname];
  }

  // Check for prefix match (e.g., /self.memory.capture matches /self.memory)
  for (const [path, jewel] of Object.entries(PATH_TO_JEWEL)) {
    if (pathname.startsWith(path)) {
      return jewel;
    }
  }

  return undefined;
}

/**
 * Get AGENTESE display path from pathname.
 */
function getAgentesePath(pathname: string): string | undefined {
  // Check for exact match first
  if (PATH_TO_AGENTESE[pathname]) {
    return PATH_TO_AGENTESE[pathname];
  }

  // Check for prefix match
  for (const [path, agentese] of Object.entries(PATH_TO_AGENTESE)) {
    if (pathname.startsWith(path)) {
      return agentese;
    }
  }

  return undefined;
}

/**
 * Crown context display component.
 * Wave 4: Connected to real API data.
 */
export function CrownContext() {
  const location = useLocation();
  const [state, setState] = useState<CrownState>({ loading: true });

  // Determine current jewel from route
  const currentJewel = getJewelFromPath(location.pathname);
  const agentesePath = getAgentesePath(location.pathname);
  const jewelInfo = currentJewel ? JEWEL_INFO[currentJewel] : undefined;

  // Fetch crown state from multiple APIs
  const fetchCrownState = useCallback(async () => {
    try {
      // Fetch Brain and Garden state in parallel
      const [brainRes, gardenRes] = await Promise.allSettled([
        brainApi.getStatus(),
        gardenerApi.getGarden(),
      ]);

      const newState: CrownState = { loading: false };

      // Brain crystal count
      if (brainRes.status === 'fulfilled' && brainRes.value) {
        newState.crystalCount = brainRes.value.concept_count;
      }

      // Garden season and session
      if (gardenRes.status === 'fulfilled' && gardenRes.value) {
        const garden = gardenRes.value;
        newState.season = garden.season;

        // Check if there's an active Gardener session
        if (garden.session_id) {
          // Could fetch session phase here if needed
          newState.gardenerPhase = 'active';
        }
      }

      setState(newState);
    } catch (error) {
      console.debug('CrownContext: API not available', error);
      setState({ loading: false });
    }
  }, []);

  // Fetch on mount and periodically
  useEffect(() => {
    fetchCrownState();

    // Refresh every 30 seconds to keep state current
    const interval = setInterval(fetchCrownState, 30000);
    return () => clearInterval(interval);
  }, [fetchCrownState]);

  // Don't show if not on a jewel page
  if (!currentJewel || !jewelInfo) {
    return null;
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="flex items-center gap-3 text-xs"
      >
        {/* Current jewel indicator with AGENTESE path */}
        <div className="flex items-center gap-1.5">
          <span className="text-base" title={jewelInfo.name}>
            {jewelInfo.icon}
          </span>
          {agentesePath && (
            <code className={`font-mono ${jewelInfo.color} opacity-70`}>{agentesePath}</code>
          )}
        </div>

        {/* Divider */}
        {(state.gardenerPhase || state.crystalCount || state.activeMask || state.season) && (
          <span className="text-gray-600">│</span>
        )}

        {/* Gardener phase */}
        {state.gardenerPhase && (
          <Link
            to="/concept.gardener"
            className="flex items-center gap-1 text-green-400/70 hover:text-green-400 transition-colors"
            title="Active Gardener Session"
          >
            <span>🌱</span>
            <span>{state.gardenerPhase}</span>
          </Link>
        )}

        {/* Season indicator */}
        {state.season && (
          <Link
            to="/self.garden"
            className="flex items-center gap-1 text-green-400/70 hover:text-green-400 transition-colors"
            title="Current Season"
          >
            <span>🌿</span>
            <span>{state.season}</span>
          </Link>
        )}

        {/* Crystal count */}
        {state.crystalCount !== undefined && state.crystalCount > 0 && (
          <Link
            to="/self.memory"
            className="flex items-center gap-1 text-purple-400/70 hover:text-purple-400 transition-colors"
            title="Brain Crystals"
          >
            <span>💎</span>
            <span>{state.crystalCount}</span>
          </Link>
        )}

        {/* Active mask */}
        {state.activeMask && (
          <Link
            to="/world.park"
            className="flex items-center gap-1 text-pink-400/70 hover:text-pink-400 transition-colors"
            title="Active Park Mask"
          >
            <span>🎭</span>
            <span>{state.activeMask}</span>
          </Link>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

/**
 * Compact crown breadcrumb showing jewel hierarchy.
 */
export function CrownBreadcrumb() {
  const location = useLocation();
  const currentJewel = getJewelFromPath(location.pathname);

  if (!currentJewel) return null;

  const jewelInfo = JEWEL_INFO[currentJewel];

  return (
    <div className="flex items-center gap-2 text-xs text-gray-500">
      <Link to="/" className="hover:text-gray-300 transition-colors">
        Crown
      </Link>
      <span>/</span>
      <span className={`flex items-center gap-1 ${jewelInfo.color}`}>
        <span>{jewelInfo.icon}</span>
        <span>{jewelInfo.name}</span>
      </span>
    </div>
  );
}
