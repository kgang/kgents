/**
 * AGENTESE-as-Route Projection System
 *
 * The URL IS the API call. This module provides:
 * - UniversalProjection: Catches all AGENTESE paths and renders appropriate components
 * - DynamicProjection: Resolves response types to components
 * - Registry: Maps types and patterns to projection components
 *
 * @see spec/protocols/agentese-as-route.md
 */

// Main components
export { UniversalProjection, useProjectionContext } from './UniversalProjection';
export { ProjectionLoading } from './ProjectionLoading';
export { ProjectionError } from './ProjectionError';
export { ConceptHomeProjection } from './ConceptHomeProjection';

// Registry functions and components
export {
  resolveProjection,
  registerTypeProjection,
  registerPathProjection,
  getRegisteredPatterns,
  getRegisteredTypes,
  GenericProjection, // Re-export for explicit JSON viewing
} from './registry';

// Types
export type {
  ProjectionContext,
  ProjectionProps,
  ProjectionComponent,
  ProjectionRegistration,
  ProjectionLoadingProps,
  ProjectionErrorProps,
  UniversalProjectionOptions,
} from './types';
