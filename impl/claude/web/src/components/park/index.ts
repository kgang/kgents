/**
 * Park components - Punchdrunk Park crisis practice UI.
 *
 * Wave 3: Web UI for crisis scenarios.
 *
 * Architecture:
 * - ParkVisualization: Main visualization (projection-first target)
 * - TimerDisplay/Grid: Timer countdown visuals
 * - PhaseTransition/Indicator: Crisis phase state machine
 * - MaskSelector/CurrentMaskBadge: Dialogue mask selection
 * - ConsentMeter: Consent debt and force mechanics
 */

// Main visualization (for projection-first pages)
export { ParkVisualization } from './ParkVisualization';

// Timer components
export { TimerDisplay, TimerGrid } from './TimerDisplay';

// Phase components
export { PhaseTransition, PhaseIndicator } from './PhaseTransition';

// Mask components
export { MaskSelector, CurrentMaskBadge } from './MaskSelector';

// Consent/force components
export { ConsentMeter } from './ConsentMeter';
