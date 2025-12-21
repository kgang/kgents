/**
 * Gestalt - Living Architecture Visualizer
 *
 * 2D Renaissance Phase 3 (2025-12-18): Full Gestalt2D implementation.
 *
 * Shows codebase architecture health as a living garden of layer cards,
 * with breathing animations when healthy, violations highlighted.
 *
 * @see spec/protocols/2d-renaissance.md - Phase 3: Gestalt2D
 */

import { useMemo } from 'react';
import { PathProjection } from '../shell/PathProjection';
import type { WorldCodebaseTopologyResponse } from '../api/types';
import { Gestalt2D } from '../components/gestalt';

export default function GestaltPage() {
  const body = useMemo(() => ({ max_nodes: 150 }), []);

  return (
    <PathProjection
      path="world.codebase"
      aspect="topology"
      body={body}
      jewel="gestalt"
      className="flex-1 min-h-0 flex flex-col"
    >
      {(data) => <Gestalt2D topology={data as WorldCodebaseTopologyResponse} />}
    </PathProjection>
  );
}
