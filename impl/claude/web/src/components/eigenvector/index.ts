/**
 * Eigenvector Components: Visualizing personality vectors.
 *
 * Two eigenvector systems:
 * 1. 7D Artisan Eigenvectors (warmth, curiosity, trust, creativity, patience, resilience, ambition)
 * 2. 6D Kent Eigenvectors (aesthetic, categorical, gratitude, heterarchy, generativity, joy)
 *
 * The 7D system is for artisan compatibility in the Forge.
 * The 6D system is Kent's soul coordinates for K-gent governance.
 */

// 7D Artisan Eigenvectors (for artisan personality)
export {
  EigenvectorRadar,
  EigenvectorBars,
  CompatibilityScore,
  type EigenvectorDimensions,
} from './EigenvectorRadar';

// 6D Kent Eigenvectors (for K-gent soul governance)
export {
  KentEigenvectorRadar,
  KentEigenvectorBars,
  KENT_EIGENVECTORS,
  type KentEigenvectorDimensions,
} from './KentEigenvectorRadar';
