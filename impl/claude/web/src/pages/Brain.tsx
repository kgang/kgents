/**
 * Brain Page - Holographic Memory Interface
 *
 * PROJECTION-FIRST REFACTOR (OS Shell Phase: refactor-brain)
 *
 * This page follows the projection-first pattern from spec/protocols/os-shell.md:
 * - Page is a thin wrapper (<50 LOC target)
 * - Business logic lives in BrainCanvas component
 * - Data fetching delegated to PathProjection
 * - Shell context provides density and observer
 *
 * Before refactor: 1114 lines
 * After refactor: ~30 lines (target: <50 LOC)
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see components/brain/BrainCanvas.tsx - All visualization logic
 * @see shell/PathProjection.tsx - AGENTESE path projection
 */

import { PathProjection } from '../shell/PathProjection';
import { BrainCanvas } from '../components/brain/BrainCanvas';
import type { BrainTopologyResponse } from '../api/types';

/**
 * Brain Page - Projection-First Implementation
 *
 * Fetches topology from self.memory path and delegates
 * all rendering to BrainCanvas component.
 */
export default function Brain() {
  return (
    <PathProjection<BrainTopologyResponse>
      path="self.memory"
      aspect="topology"
      jewel="brain"
      loadingAction="analyze"
      body={{ similarity_threshold: 0.3 }}
      className="h-screen"
    >
      {(topology, { density, refetch, isMobile, isTablet, isDesktop }) => (
        <BrainCanvas
          topology={topology}
          density={density}
          isMobile={isMobile}
          isTablet={isTablet}
          isDesktop={isDesktop}
          refetch={refetch}
        />
      )}
    </PathProjection>
  );
}

// =============================================================================
// Migration Notes
// =============================================================================
//
// BEFORE (1114 lines):
// - All data fetching logic in page
// - All layout logic in page
// - All form state in page
// - Mobile/tablet/desktop branching in page
//
// AFTER (45 lines):
// - PathProjection handles fetching and loading/error states
// - BrainCanvas contains all visualization and control logic
// - Page is pure delegation
//
// Backup available at: Brain.tsx.backup
// =============================================================================
