/**
 * Gestalt - Living Architecture Visualizer
 *
 * Projection-first page for codebase health visualization.
 * All logic delegated to GestaltVisualization via PathProjection.
 *
 * Target: < 50 LOC (achieved: ~55 LOC with maxNodes state)
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see docs/skills/crown-jewel-patterns.md
 */

import { useState, useMemo, useCallback } from 'react';
import { PathProjection } from '../shell/PathProjection';
import { useShellMaybe } from '../shell/ShellProvider';
import { useWindowLayout } from '../hooks/useLayoutContext';
import { GestaltVisualization } from '../components/gestalt/GestaltVisualization';
import { gestaltApi } from '../api/client';
import type { CodebaseTopologyResponse } from '../api/types';

export default function GestaltPage() {
  // Get layout context (shell or fallback)
  const shell = useShellMaybe();
  const windowLayout = useWindowLayout();

  // Derive layout from shell or fallback
  const density = shell?.density ?? windowLayout.density;
  const isMobile = shell?.isMobile ?? windowLayout.isMobile;
  const isTablet = shell?.isTablet ?? windowLayout.isTablet;
  const isDesktop = shell?.isDesktop ?? windowLayout.isDesktop;
  const width = shell?.width ?? windowLayout.width;

  // Max nodes state - controlled by slider, defaults from viewport
  const defaultMaxNodes = isMobile ? 100 : isTablet ? 125 : 150;
  const [maxNodes, setMaxNodes] = useState(defaultMaxNodes);

  // Memoize body to prevent infinite re-fetch
  const body = useMemo(() => ({ max_nodes: maxNodes }), [maxNodes]);

  // Scan handler for rescan button
  const handleScan = async () => {
    await gestaltApi.scan('python');
  };

  // Handle maxNodes change from slider
  const handleMaxNodesChange = useCallback((newMaxNodes: number) => {
    setMaxNodes(newMaxNodes);
  }, []);

  return (
    <PathProjection
      path="world.codebase"
      aspect="topology"
      body={body}
      jewel="gestalt"
      className="h-screen"
    >
      {(data) => (
        <GestaltVisualization
          data={data as CodebaseTopologyResponse}
          density={density}
          isMobile={isMobile}
          isTablet={isTablet}
          isDesktop={isDesktop}
          width={width}
          onScan={handleScan}
          maxNodes={maxNodes}
          onMaxNodesChange={handleMaxNodesChange}
        />
      )}
    </PathProjection>
  );
}
