/**
 * Gallery components for Projection Component Gallery.
 *
 * Heavy interactive components (PolynomialPlayground, OperadWiring, TownLive)
 * are available in two forms:
 * - Direct imports: For when the component is definitely needed
 * - Lazy imports: For code splitting when components may not render
 *
 * @see plans/park-town-design-overhaul.md - Phase 5.2 Performance
 */

import { lazy } from 'react';

export { PilotCard } from './PilotCard';
export { ProjectionView } from './ProjectionView';
export { CategoryFilter } from './CategoryFilter';
export { OverrideControls } from './OverrideControls';

// Flagship Interactive Pilots (Gallery V2) - Direct exports
export { PolynomialPlayground } from './PolynomialPlayground';
export { OperadWiring } from './OperadWiring';
export { TownLive } from './TownLive';

// =============================================================================
// Lazy-loaded versions for code splitting
// Use these with React.Suspense for optimal bundle splitting
// =============================================================================

/**
 * Lazy-loaded PolynomialPlayground for code splitting.
 *
 * @example
 * ```tsx
 * import { LazyPolynomialPlayground } from '@/components/projection/gallery';
 *
 * <Suspense fallback={<Spinner />}>
 *   <LazyPolynomialPlayground />
 * </Suspense>
 * ```
 */
export const LazyPolynomialPlayground = lazy(() =>
  import('./PolynomialPlayground').then((mod) => ({ default: mod.PolynomialPlayground }))
);

/**
 * Lazy-loaded OperadWiring for code splitting.
 */
export const LazyOperadWiring = lazy(() =>
  import('./OperadWiring').then((mod) => ({ default: mod.OperadWiring }))
);

/**
 * Lazy-loaded TownLive for code splitting.
 */
export const LazyTownLive = lazy(() =>
  import('./TownLive').then((mod) => ({ default: mod.TownLive }))
);
