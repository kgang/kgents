/**
 * StreamPathProjection - SSE-Based Projection Wrapper
 *
 * A variant of PathProjection designed for SSE streaming pages.
 * While PathProjection does one-time AGENTESE gateway fetches,
 * StreamPathProjection handles continuous SSE event streams.
 *
 * Use Cases:
 * - Agent Town (live simulation updates)
 * - Live dashboards requiring real-time updates
 * - Any page needing SSE-based data flow
 *
 * Key Differences from PathProjection:
 * - No gateway fetch - data comes from SSE stream
 * - Requires loader hook for initial setup
 * - Requires stream hook for continuous updates
 * - Handles connect/disconnect lifecycle
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see PathProjection.tsx - For gateway-based projections
 *
 * @example
 * ```tsx
 * // Minimal SSE projection-first page (< 50 LOC target)
 * export default function TownPage() {
 *   const { townId } = useParams<{ townId: string }>();
 *   return (
 *     <StreamPathProjection
 *       jewel="coalition"
 *       loader={useTownLoader(townId)}
 *       stream={useTownStreamWidget}
 *     >
 *       {(stream, { density }) => (
 *         <TownVisualization {...stream} density={density} />
 *       )}
 *     </StreamPathProjection>
 *   );
 * }
 * ```
 */

import {
  type ReactNode,
  type CSSProperties,
} from 'react';
import { useShellMaybe } from './ShellProvider';
import { useWindowLayout } from '../hooks';
import { PersonalityLoading } from '@/components/joy/PersonalityLoading';
import { EmpathyError } from '@/components/joy/EmpathyError';
import type { Density, CrownJewel } from './types';
import type { ColonyDashboardJSON } from '../reactive/types';
import type { TownEvent } from '../api/types';

// =============================================================================
// Types
// =============================================================================

/**
 * Loader result - provides entity ID and loading state.
 */
export interface LoaderResult {
  /** The resolved entity ID (null if loading/error) */
  townId: string | null;
  /** Whether loading is in progress */
  loading: boolean;
  /** Error message if loading failed */
  error: string | null;
}

/**
 * Stream result - provides streaming data and controls.
 */
export interface StreamResult {
  /** Dashboard state from SSE */
  dashboard: ColonyDashboardJSON | null;
  /** Events from SSE */
  events: TownEvent[];
  /** Whether connected to SSE */
  isConnected: boolean;
  /** Whether simulation is playing */
  isPlaying: boolean;
  /** Connect to stream */
  connect: () => void;
  /** Disconnect from stream */
  disconnect: () => void;
}

/**
 * Context provided to stream projection children.
 */
export interface StreamProjectionContext {
  /** Current layout density */
  density: Density;
  /** Mobile viewport (<768px) */
  isMobile: boolean;
  /** Tablet viewport (768-1024px) */
  isTablet: boolean;
  /** Desktop viewport (>1024px) */
  isDesktop: boolean;
  /** Entity ID (townId, etc.) */
  entityId: string;
}

/**
 * Props for StreamPathProjection component.
 */
export interface StreamPathProjectionProps {
  /** Which Crown Jewel this projection belongs to */
  jewel: CrownJewel;
  /** Loader result from hook like useTownLoader */
  loader: LoaderResult;
  /** Stream result from hook like useTownStreamWidget */
  stream: StreamResult;
  /** Render function receiving stream data and context */
  children: (stream: StreamResult, context: StreamProjectionContext) => ReactNode;
  /** Container className */
  className?: string;
  /** Container style */
  style?: CSSProperties;
  /** Action label for not found error */
  notFoundAction?: string;
  /** Handler for not found action */
  onNotFoundAction?: () => void;
}

// =============================================================================
// Component
// =============================================================================

/**
 * StreamPathProjection - SSE-Based Projection Wrapper.
 *
 * Provides the same projection-first pattern as PathProjection,
 * but for SSE streaming data instead of gateway fetches.
 *
 * Target: Pages using StreamPathProjection should be < 50 LOC.
 */
export function StreamPathProjection({
  jewel,
  loader,
  stream,
  children,
  className = '',
  style,
  notFoundAction = 'Go Back',
  onNotFoundAction,
}: StreamPathProjectionProps) {
  // Use shell context if available, otherwise fallback to window layout
  const shell = useShellMaybe();
  const layout = useWindowLayout();

  // Derive layout from shell or window
  const density = shell?.density ?? layout.density;
  const isMobile = shell?.isMobile ?? layout.isMobile;
  const isTablet = shell?.isTablet ?? layout.isTablet;
  const isDesktop = shell?.isDesktop ?? layout.isDesktop;

  // Loading state
  if (loader.loading || !loader.townId) {
    return (
      <div
        className={`h-screen flex items-center justify-center bg-violet-950 ${className}`}
        style={style}
      >
        <PersonalityLoading jewel={jewel} size="lg" />
      </div>
    );
  }

  // Error state
  if (loader.error) {
    return (
      <div
        className={`h-screen flex items-center justify-center bg-violet-950 ${className}`}
        style={style}
      >
        <EmpathyError
          type="notfound"
          title="Not Found"
          subtitle={loader.error}
          action={notFoundAction}
          onAction={onNotFoundAction ?? (() => window.history.back())}
        />
      </div>
    );
  }

  // Build context
  const context: StreamProjectionContext = {
    density,
    isMobile,
    isTablet,
    isDesktop,
    entityId: loader.townId,
  };

  // Render children with stream and context
  return (
    <div className={className} style={style}>
      {children(stream, context)}
    </div>
  );
}

export default StreamPathProjection;
