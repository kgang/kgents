/**
 * Projection System Types
 *
 * Types for the AGENTESE-as-Route projection system.
 *
 * @see spec/protocols/agentese-as-route.md
 */

import type { ComponentType } from 'react';
import type { AgenteseContext } from '@/utils/parseAgentesePath';

/**
 * Context passed to all projection components
 */
export interface ProjectionContext {
  /** Full AGENTESE path (e.g., "world.town.citizen.kent_001") */
  path: string;
  /** Context (world, self, concept, void, time) */
  context: AgenteseContext | null;
  /** Invoked aspect (e.g., "manifest", "polynomial") */
  aspect: string;
  /** Query parameters */
  params: Record<string, string>;
  /** Response data from AGENTESE */
  response: unknown;
  /** Response type name (from contracts) */
  responseType: string;
}

/**
 * Props for projection components
 */
export interface ProjectionProps {
  context: ProjectionContext;
}

/**
 * A projection component renders an AGENTESE response
 */
export type ProjectionComponent = ComponentType<ProjectionProps>;

/**
 * Registration entry in the projection registry
 */
export interface ProjectionRegistration {
  /** Component to render */
  component: ProjectionComponent;
  /** Optional description */
  description?: string;
  /** Optional priority (higher = more specific) */
  priority?: number;
}

/**
 * Props for loading state projection
 */
export interface ProjectionLoadingProps {
  path: string;
  aspect: string;
}

/**
 * Props for error state projection
 */
export interface ProjectionErrorProps {
  path: string;
  aspect: string;
  error: Error;
  /** Similar paths for recovery suggestions */
  similarPaths?: string[];
}

/**
 * Options for the UniversalProjection component
 */
export interface UniversalProjectionOptions {
  /** Custom loading component */
  loadingComponent?: ComponentType<ProjectionLoadingProps>;
  /** Custom error component */
  errorComponent?: ComponentType<ProjectionErrorProps>;
  /** Skip fetching (for testing) */
  skip?: boolean;
}
