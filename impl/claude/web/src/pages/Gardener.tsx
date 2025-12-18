/**
 * Gardener Page - Projection-First Implementation
 *
 * The Gardener is the meta-jewel for development sessions, visualizing
 * polynomial state machines for the SENSE → ACT → REFLECT cycle.
 *
 * This is a projection-first page per OS Shell spec:
 * - Page delegates to PathProjection for data fetching
 * - Visualization component handles all rendering logic
 * - Target: < 50 LOC (excluding mock data)
 *
 * @see spec/protocols/os-shell.md - Projection-First Rendering
 * @see docs/creative/visual-system.md - No Emoji Policy (uses Lucide icons)
 */

import { useState, useCallback, useMemo } from 'react';
import { Leaf } from 'lucide-react';
import { useShell } from '@/shell';
import { GardenerVisualization } from '@/components/gardener';
import { Breathe } from '@/components/joy';
import type { GardenerPhase } from '@/api/types/_generated/concept-gardener';
import type { GardenerSessionState } from '@/api/types';

// =============================================================================
// Mock Data (REMOVE when API is ready - will use PathProjection instead)
// =============================================================================
const createMockSession = (phase: GardenerPhase): GardenerSessionState => ({
  session_id: 'mock-session-001',
  name: 'Wave 1 Hero Path Implementation',
  phase,
  plan_path: 'plans/crown-jewels-enlightened.md',
  intent: { description: 'Implement Hero Path jewels with foundation support', priority: 'high' },
  artifacts_count: phase === 'SENSE' ? 0 : phase === 'ACT' ? 3 : 5,
  learnings_count: phase === 'REFLECT' ? 2 : 0,
  sense_count: 1,
  act_count: phase === 'SENSE' ? 0 : 1,
  reflect_count: phase === 'REFLECT' ? 1 : 0,
});

// =============================================================================
// Page Component (30 LOC - meets <50 LOC target)
// =============================================================================
export default function GardenerPage() {
  const { density, isMobile } = useShell();
  const [phase, setPhase] = useState<GardenerPhase>('SENSE');
  const session = useMemo(() => createMockSession(phase), [phase]);
  const handlePhaseChange = useCallback((p: GardenerPhase) => setPhase(p), []);

  return (
    <div className="h-screen flex flex-col bg-gray-900 text-white overflow-hidden">
      <header className="flex-shrink-0 border-b border-gray-800 px-4 py-3">
        <h1 className={`font-bold flex items-center gap-2 ${isMobile ? 'text-lg' : 'text-xl'}`}>
          <Leaf className="w-5 h-5 text-lime-400" />
          <span>The Gardener</span>
          <Breathe intensity={0.3} speed="slow"><span className="text-lime-400">●</span></Breathe>
        </h1>
        <p className={`text-gray-400 mt-0.5 ${isMobile ? 'text-xs' : 'text-sm'}`}>{session.name}</p>
      </header>
      <div className="flex-1 overflow-y-auto p-4">
        <GardenerVisualization session={session} density={density} onPhaseChange={handlePhaseChange} />
      </div>
    </div>
  );
}
