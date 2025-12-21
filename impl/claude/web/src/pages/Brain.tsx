/**
 * Brain Page - Living Memory Cartography
 *
 * 2D Renaissance Phase 4 Complete (2025-12-18): Brain2D visualization.
 *
 * "Memory isn't a starfield. It's a living library where crystals
 * form, connect, and surface when needed."
 *
 * @see spec/protocols/2d-renaissance.md - Phase 4: Brain2D
 */

import { useState, useCallback } from 'react';
import { PathProjection } from '../shell/PathProjection';
import { Brain2D } from '../components/brain';
import type { SelfMemoryTopologyResponse } from '../api/types';

export default function BrainPage() {
  const [observer, setObserver] = useState('technical');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = useCallback(() => {
    setRefreshKey((k) => k + 1);
  }, []);

  return (
    <PathProjection<SelfMemoryTopologyResponse>
      key={refreshKey}
      path="self.memory"
      aspect="topology"
      jewel="brain"
      loadingAction="analyze"
      body={{ similarity_threshold: 0.3 }}
      className="flex-1 min-h-0 flex flex-col"
    >
      {(topology) => (
        <Brain2D
          topology={topology}
          observer={observer}
          onObserverChange={setObserver}
          onRefresh={handleRefresh}
        />
      )}
    </PathProjection>
  );
}
