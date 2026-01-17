/**
 * Dialectic Components - FusionCeremony Module
 *
 * "Make disagreement beautiful. Create a UI where Kent and Claude can synthesize."
 *
 * From the Constitution (Article VI):
 * "The goal is not Kent's decisions or AI's decisions.
 *  The goal is fused decisions better than either alone."
 *
 * Components:
 * - FusionCeremony: The main dialectical synthesis UI
 * - ThesisPanel: Kent's position input
 * - AntithesisPanel: Claude's counter-position input
 * - SynthesisPanel: The fusion result display
 * - CoconeVisualization: Abstract categorical cocone visualization
 *
 * @see docs/theory/17-dialectic.md
 */

// Main component
export { FusionCeremony, default as FusionCeremonyDefault } from './FusionCeremony';

// Supporting components
export { ThesisPanel } from './ThesisPanel';
export { AntithesisPanel } from './AntithesisPanel';
export { SynthesisPanel } from './SynthesisPanel';
export { CoconeVisualization } from './CoconeVisualization';

// Types
export type {
  CeremonyPhase,
  CeremonyState,
  ThesisPanelProps,
  AntithesisPanelProps,
  SynthesisPanelProps,
  CoconeVisualizationProps,
  FusionCeremonyProps,
  CoconeAnimationState,
  ExportFormat,
  ExportData,
} from './types';

export { INITIAL_CEREMONY_STATE } from './types';
