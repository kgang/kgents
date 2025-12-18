/**
 * Atelier Page - Tiny Atelier Creative Workshop
 *
 * PROJECTION-FIRST REFACTOR (OS Shell Phase: refactor-atelier)
 *
 * This page follows the projection-first pattern from spec/protocols/os-shell.md:
 * - Page is a thin wrapper (<50 LOC target)
 * - Business logic lives in AtelierVisualization component
 * - Data fetching delegated to PathProjection
 * - Shell context provides density and observer
 *
 * Before refactor: 415 lines
 * After refactor: ~45 lines (target: <50 LOC)
 *
 * Theme: Orisinal.com aesthetic - whimsical, minimal, melancholic but hopeful.
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see components/atelier/AtelierVisualization.tsx - All visualization logic
 * @see shell/PathProjection.tsx - AGENTESE path projection
 */

import { PathProjection } from '../shell/PathProjection';
import { useShellMaybe } from '../shell/ShellProvider';
import { useWindowLayout } from '../hooks/useLayoutContext';
import { AtelierVisualization } from '../components/atelier';
import type { AtelierStatusData } from '../components/atelier';

/**
 * Atelier Page - Projection-First Implementation
 *
 * Fetches status from world.atelier path and delegates
 * all rendering to AtelierVisualization component.
 */
export default function AtelierPage() {
  // Get layout context (shell or fallback)
  const shell = useShellMaybe();
  const windowLayout = useWindowLayout();

  // Derive layout from shell or fallback
  const density = shell?.density ?? windowLayout.density;
  const isMobile = shell?.isMobile ?? windowLayout.isMobile;
  const isTablet = shell?.isTablet ?? windowLayout.isTablet;
  const isDesktop = shell?.isDesktop ?? windowLayout.isDesktop;

  return (
    <PathProjection
      path="world.atelier"
      aspect="manifest"
      jewel="atelier"
      loadingAction="prepare"
      className="min-h-screen"
    >
      {(data, { refetch }) => (
        <AtelierVisualization
          status={data as AtelierStatusData}
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
// BEFORE (415 lines):
// - All data fetching logic in page
// - All layout logic in page
// - All form state in page
// - All navigation state in page
// - Mobile/tablet/desktop branching in page
//
// AFTER (55 lines):
// - PathProjection handles fetching and loading/error states
// - AtelierVisualization contains all visualization and control logic
// - Page is pure delegation
//
// Key changes:
// - Header uses Lucide Palette icon instead of no icon (follows no-emoji policy)
// - Density-adaptive styles applied in visualization component
// - Streaming logic preserved in AtelierVisualization
//
// Backup available at: Atelier.tsx.backup
// =============================================================================
