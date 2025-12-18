/**
 * ParkScenario - Projection-first page for Punchdrunk Park.
 *
 * Target: < 50 LOC (achieved: ~25 LOC)
 *
 * This page delegates all business logic and visualization to ParkVisualization.
 * It only handles the PathProjection wrapper for AGENTESE integration.
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 */

import { PathProjection } from '@/shell/PathProjection';
import { ParkVisualization } from '@/components/park/ParkVisualization';
import type { ParkStatusResponse } from '@/api/types';

export default function ParkScenario() {
  return (
    <PathProjection<ParkStatusResponse>
      path="world.park"
      aspect="manifest"
      jewel="park"
      loadingAction="connect"
    >
      {(data, { density }) => (
        <ParkVisualization data={data} density={density} />
      )}
    </PathProjection>
  );
}
