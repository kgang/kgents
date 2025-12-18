/**
 * Forge Page - The Metaphysical Forge
 *
 * PROJECTION-FIRST IMPLEMENTATION
 *
 * This page follows the projection-first pattern from spec/protocols/os-shell.md:
 * - Page is a thin wrapper (<50 LOC target)
 * - Business logic lives in ForgeVisualization component
 * - Data fetching delegated to PathProjection
 * - Shell context provides density and observer
 *
 * The Forge is where Kent builds. No spectators. Just the work.
 *
 * @see spec/protocols/metaphysical-forge.md
 * @see components/forge/ForgeVisualization.tsx - All visualization logic
 * @see shell/PathProjection.tsx - AGENTESE path projection
 */

import { PathProjection } from '../shell/PathProjection';
import { useShellMaybe } from '../shell/ShellProvider';
import { useWindowLayout } from '../hooks/useLayoutContext';
import { ForgeVisualization } from '../components/forge';
import type { ForgeStatusData } from '../components/forge';

/**
 * Forge Page - Projection-First Implementation
 *
 * Fetches status from world.forge path and delegates
 * all rendering to ForgeVisualization component.
 */
export default function ForgePage() {
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
      path="world.forge"
      aspect="manifest"
      jewel="forge"
      loadingAction="prepare"
      className="min-h-screen"
    >
      {(data, { refetch }) => (
        <ForgeVisualization
          status={data as ForgeStatusData}
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
