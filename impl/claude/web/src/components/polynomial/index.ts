/**
 * Polynomial Visualization Components
 *
 * Foundation 3: Visible Polynomial State
 *
 * These components visualize polynomial agent state machines, making
 * the categorical structure visible to users.
 *
 * @example
 * ```tsx
 * import { PolynomialDiagram, usePolynomialState, createGardenerVisualization } from '@/components/polynomial';
 *
 * const gardenerViz = createGardenerVisualization(session);
 * const { visualization, transition } = usePolynomialState({ initial: gardenerViz });
 *
 * <PolynomialDiagram
 *   visualization={visualization}
 *   onTransition={transition}
 *   layout="linear"
 * />
 * ```
 */

// Components
export { PolynomialDiagram } from './PolynomialDiagram';
export type { PolynomialDiagramProps, PolynomialLayout } from './PolynomialDiagram';

export { PolynomialNode } from './PolynomialNode';
export type { PolynomialNodeProps } from './PolynomialNode';

// Hooks
export { usePolynomialState } from './usePolynomialState';
export type { PolynomialStateOptions, PolynomialStateReturn } from './usePolynomialState';

// Utility functions for creating visualizations
export {
  createGardenerVisualization,
  createNPhaseVisualization,
  createCitizenVisualization,
  createGenericVisualization,
} from './visualizations';
export type { GenericPolynomialConfig } from './visualizations';
