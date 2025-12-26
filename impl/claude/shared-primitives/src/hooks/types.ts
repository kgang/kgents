/**
 * Layout Context Types
 */

export interface LayoutContext {
  availableWidth: number;
  availableHeight: number;
  depth: number;
  parentLayout: 'stack' | 'flow' | 'grid';
  isConstrained: boolean;
  density: 'compact' | 'comfortable' | 'spacious';
}
