/**
 * Park components - Punchdrunk Park crisis practice UI.
 *
 * Wave 3: Web UI for crisis scenarios.
 * Phase 3: Enhanced with categorical polynomial visualizations.
 *
 * Architecture:
 * - ParkVisualization: Main visualization (projection-first target)
 * - TimerDisplay/Grid: Timer countdown visuals (legacy)
 * - TimerMachine/Grid: Timer with polynomial state machine (Phase 3)
 * - PhaseTransition/Indicator: Crisis phase state machine (legacy)
 * - PhaseVisualization: Enhanced phase with polynomial viz (Phase 3)
 * - MaskSelector/CurrentMaskBadge: Dialogue mask selection (legacy)
 * - MaskCardEnhanced/Grid: Masks with affordances preview (Phase 3)
 * - ConsentMeter: Consent debt and force mechanics (legacy)
 * - ConsentDebtMachine: Debt as polynomial phases (Phase 3)
 * - ParkTracePanel: N-gent witness for park events (Phase 3)
 *
 * @see plans/park-town-design-overhaul.md (Phase 3: Park Enhancement)
 */

// Main visualization (for projection-first pages)
export { ParkVisualization } from './ParkVisualization';

// Timer components (legacy)
export { TimerDisplay, TimerGrid } from './TimerDisplay';

// Timer components (Phase 3 - with polynomial state machine)
export { TimerMachine, TimerMachineGrid } from './TimerMachine';

// Phase components (legacy)
export { PhaseTransition, PhaseIndicator } from './PhaseTransition';

// Phase components (Phase 3 - with polynomial visualization)
export { PhaseVisualization } from './PhaseVisualization';

// Mask components (legacy)
export { MaskSelector, CurrentMaskBadge } from './MaskSelector';

// Mask components (Phase 3 - with affordances preview)
export { MaskCardEnhanced, MaskGridEnhanced } from './MaskCardEnhanced';

// Consent/force components (legacy)
export { ConsentMeter } from './ConsentMeter';

// Consent/force components (Phase 3 - with polynomial phases)
export { ConsentDebtMachine } from './ConsentDebtMachine';

// Trace panel (Phase 3 - N-gent witness)
export { ParkTracePanel } from './ParkTracePanel';
