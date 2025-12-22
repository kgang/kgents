/**
 * Witness Garden Components
 *
 * Phase 6: Witness Assurance Surface
 *
 * Components for the living garden visualization where specs grow as plants,
 * evidence accumulates as soil depth, and orphans appear as weeds to tend.
 *
 * "Trust is not a badge—it's a living organism."
 *
 * @see spec/protocols/witness-assurance-surface.md
 */

export { EvidenceLadder, type EvidenceLadderProps } from './EvidenceLadder';
export {
  ConfidencePulse,
  PulseDot,
  type ConfidencePulseProps,
  type PulseDotProps,
} from './ConfidencePulse';
export { SpecPlantCard, type SpecPlantCardProps } from './SpecPlantCard';
export { OrphanWeedCard, type OrphanWeedCardProps } from './OrphanWeedCard';
export { GardenScene, type GardenSceneProps } from './GardenScene';
