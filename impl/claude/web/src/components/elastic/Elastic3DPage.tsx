/**
 * Elastic3DPage - Higher-Order Component for 3D Crown Jewel Pages
 *
 * Provides consistent patterns for pages that:
 * 1. Use Layout Projection Functor (density-parameterized layouts)
 * 2. Use canonical SceneLighting / SceneEffects
 * 3. Need mobile drawers and floating actions
 *
 * This HOC encapsulates:
 * - Illumination quality detection and QualitySelector
 * - Mobile-first layout with BottomDrawer pattern
 * - Desktop ElasticSplit layout
 * - Consistent header structure
 *
 * @example
 * ```tsx
 * function MyPage() {
 *   return (
 *     <Elastic3DPage
 *       title="My 3D Visualization"
 *       subtitle="Interactive demo"
 *       icon="🌐"
 *       canvas={<Canvas><MyScene quality={quality} density={density} /></Canvas>}
 *       sidebar={<MySidebar />}
 *       actions={[{ id: 'refresh', icon: '🔄', label: 'Refresh', onClick: ... }]}
 *       loading={loading}
 *       error={error}
 *       onRetry={handleRetry}
 *     />
 *   );
 * }
 * ```
 *
 * @see plans/_continuations/gestalt-live-elastic-upgrade.md
 * @see docs/skills/3d-lighting-patterns.md
 */

import type { ReactNode } from 'react';
import { Suspense } from 'react';
import { ErrorBoundary } from '../error/ErrorBoundary';
import {
  ElasticSplit,
  BottomDrawer,
  FloatingActions,
  useWindowLayout,
  PHYSICAL_CONSTRAINTS,
  type FloatingAction,
  type Density,
} from '../elastic';
import { QualitySelector } from '../three/QualitySelector';
import { useIlluminationQuality } from '../../hooks/useIlluminationQuality';
import type { IlluminationQuality } from '../../constants/lighting';

// =============================================================================
// Types
// =============================================================================

export interface Elastic3DPageProps {
  /** Page title displayed in header */
  title: string;

  /** Page subtitle (e.g., stats summary) */
  subtitle?: string;

  /** Page icon emoji */
  icon?: string;

  /**
   * The 3D canvas element. You are responsible for wrapping in Canvas and
   * passing illuminationQuality and density to your scene.
   */
  canvas: ReactNode;

  /**
   * Sidebar content for tablet/desktop. On mobile, this goes into a BottomDrawer.
   */
  sidebar?: ReactNode;

  /** Sidebar title for drawer mode */
  sidebarTitle?: string;

  /**
   * Floating actions for mobile. Also shown in header on desktop.
   */
  actions?: FloatingAction[];

  /** Header right-side content (additional controls) */
  headerRight?: ReactNode;

  /** Loading state */
  loading?: boolean;

  /** Error message */
  error?: string | null;

  /** Retry handler for error state */
  onRetry?: () => void;

  /** Optional health percentage (0-1) for status badge */
  healthPercent?: number;

  /** Show quality selector (default: true on desktop) */
  showQualitySelector?: boolean;

  /** Loading placeholder component */
  loadingFallback?: ReactNode;

  /** Error fallback component (overrides default) */
  errorFallback?: ReactNode;

  /** Overlays to position above the canvas */
  canvasOverlays?: ReactNode;

  /** Additional class names */
  className?: string;
}

export interface Elastic3DPageContext {
  /** Current density from layout */
  density: Density;
  /** Device type flags */
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  /** Illumination quality for 3D scenes */
  illuminationQuality: IlluminationQuality;
  /** Whether quality is auto-detected */
  isQualityAutoDetected: boolean;
  /** Override quality manually */
  overrideQuality: (quality: IlluminationQuality | null) => void;
  /** Whether shadows are enabled */
  shadowsEnabled: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const PANEL_COLLAPSE_BREAKPOINT = 768;

// =============================================================================
// Default Components
// =============================================================================

function DefaultLoading() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900">
      <div className="text-6xl mb-4 animate-pulse">🔄</div>
      <p className="text-gray-400 text-sm">Loading...</p>
    </div>
  );
}

interface DefaultErrorProps {
  error: string;
  onRetry?: () => void;
}

function DefaultError({ error, onRetry }: DefaultErrorProps) {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-gray-900 p-8">
      <div className="text-5xl mb-4">⚠️</div>
      <h3 className="text-lg font-semibold text-gray-300 mb-2">Something went wrong</h3>
      <p className="text-gray-500 text-sm text-center mb-4 max-w-md">{error}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium"
          style={{
            minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
            minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}

// =============================================================================
// Hook: useElastic3DPage
// =============================================================================

/**
 * Hook to get Elastic3DPage context values without using the full component.
 * Useful for pages that need custom layouts but want the standard hooks.
 */
export function useElastic3DPage(): Elastic3DPageContext {
  const { density, isMobile, isTablet, isDesktop } = useWindowLayout();
  const {
    quality: illuminationQuality,
    isAutoDetected: isQualityAutoDetected,
    override: overrideQuality,
  } = useIlluminationQuality();
  const shadowsEnabled = illuminationQuality !== 'minimal';

  return {
    density,
    isMobile,
    isTablet,
    isDesktop,
    illuminationQuality,
    isQualityAutoDetected,
    overrideQuality,
    shadowsEnabled,
  };
}

// =============================================================================
// Main Component
// =============================================================================

export function Elastic3DPage({
  title,
  subtitle,
  icon = '🌐',
  canvas,
  sidebar,
  sidebarTitle = 'Details',
  actions = [],
  headerRight,
  loading = false,
  error = null,
  onRetry,
  healthPercent,
  showQualitySelector = true,
  loadingFallback,
  errorFallback,
  canvasOverlays,
  className = '',
}: Elastic3DPageProps) {
  const {
    // density available via context if needed
    isMobile,
    isTablet,
    isDesktop,
    illuminationQuality,
    isQualityAutoDetected,
    overrideQuality,
  } = useElastic3DPage();

  // Drawer state for mobile
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  // Health badge color
  const healthColor =
    healthPercent !== undefined
      ? healthPercent >= 0.8
        ? '#22c55e'
        : '#ef4444'
      : undefined;

  // ==========================================================================
  // Loading state
  // ==========================================================================

  if (loading && !canvas) {
    return (
      <div className={`h-screen bg-gray-900 ${className}`}>
        {loadingFallback || <DefaultLoading />}
      </div>
    );
  }

  // ==========================================================================
  // Error state
  // ==========================================================================

  if (error && !canvas) {
    return (
      <div className={`h-screen bg-gray-900 ${className}`}>
        {errorFallback || <DefaultError error={error} onRetry={onRetry} />}
      </div>
    );
  }

  // ==========================================================================
  // Canvas with overlays
  // ==========================================================================

  const canvasWithOverlays = (
    <div className="h-full relative">
      <ErrorBoundary
        fallback={
          errorFallback || (
            <DefaultError error="Canvas error" onRetry={onRetry} />
          )
        }
      >
        <Suspense fallback={loadingFallback || <DefaultLoading />}>
          {canvas}
        </Suspense>
      </ErrorBoundary>
      {canvasOverlays}

      {/* Quality selector on desktop */}
      {showQualitySelector && !isMobile && (
        <div className="absolute bottom-3 left-3">
          <QualitySelector
            currentQuality={illuminationQuality}
            isAutoDetected={isQualityAutoDetected}
            onQualityChange={overrideQuality}
            compact
            className="backdrop-blur-sm shadow-lg"
          />
        </div>
      )}
    </div>
  );

  // ==========================================================================
  // Mobile Layout
  // ==========================================================================

  if (isMobile) {
    return (
      <div className={`h-screen flex flex-col bg-gray-900 text-white overflow-hidden ${className}`}>
        {/* Compact header */}
        <header className="flex-shrink-0 border-b border-gray-800 px-3 py-2 bg-gray-900 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">{icon}</span>
            <span className="font-semibold truncate">{title}</span>
            {healthPercent !== undefined && (
              <span
                className="text-xs font-bold px-1.5 py-0.5 rounded"
                style={{
                  backgroundColor: healthColor + '33',
                  color: healthColor,
                }}
              >
                {Math.round(healthPercent * 100)}%
              </span>
            )}
          </div>
          {headerRight}
        </header>

        {/* Main content */}
        <div className="flex-1 relative">{canvasWithOverlays}</div>

        {/* Floating actions */}
        {actions.length > 0 && (
          <FloatingActions
            actions={[
              ...actions,
              ...(sidebar
                ? [
                    {
                      id: '__sidebar',
                      icon: '📋',
                      label: sidebarTitle,
                      onClick: () => setDrawerOpen(!drawerOpen),
                      isActive: drawerOpen,
                    },
                  ]
                : []),
            ]}
            position="bottom-right"
          />
        )}

        {/* Sidebar drawer */}
        {sidebar && (
          <BottomDrawer
            isOpen={drawerOpen}
            onClose={() => setDrawerOpen(false)}
            title={sidebarTitle}
          >
            {sidebar}
          </BottomDrawer>
        )}
      </div>
    );
  }

  // ==========================================================================
  // Tablet/Desktop Layout
  // ==========================================================================

  return (
    <div className={`h-screen flex flex-col bg-gray-900 text-white overflow-hidden ${className}`}>
      {/* Header */}
      <header className="flex-shrink-0 border-b border-gray-800 px-4 py-3 bg-gray-900">
        <div className="flex justify-between items-center">
          <div>
            <h1 className={`font-bold flex items-center gap-2 ${isTablet ? 'text-lg' : 'text-xl'}`}>
              <span>{icon}</span>
              <span>{title}</span>
              {healthPercent !== undefined && (
                <span
                  className="text-sm font-normal px-2 py-0.5 rounded ml-2"
                  style={{
                    backgroundColor: healthColor + '33',
                    color: healthColor,
                  }}
                >
                  {Math.round(healthPercent * 100)}%
                </span>
              )}
            </h1>
            {subtitle && (
              <p className={`text-gray-400 mt-0.5 ${isTablet ? 'text-xs' : 'text-sm'}`}>
                {subtitle}
              </p>
            )}
          </div>

          <div className="flex items-center gap-2">
            {headerRight}
            {actions
              .filter((a) => a.variant === 'primary')
              .map((action) => (
                <button
                  key={action.id}
                  onClick={action.onClick}
                  disabled={action.disabled || action.loading}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2
                    ${
                      action.disabled || action.loading
                        ? 'bg-gray-700 cursor-not-allowed'
                        : 'bg-green-600 hover:bg-green-700'
                    }
                    ${isTablet ? 'text-xs' : 'text-sm'}
                  `}
                  style={{
                    minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
                    minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
                  }}
                >
                  {action.loading ? (
                    <span className="animate-spin">{action.icon}</span>
                  ) : (
                    <span>{action.icon}</span>
                  )}
                  {isDesktop && <span>{action.label}</span>}
                </button>
              ))}
          </div>
        </div>
      </header>

      {/* Main content with ElasticSplit */}
      <div className="flex-1 overflow-hidden">
        {sidebar ? (
          <ElasticSplit
            direction="horizontal"
            defaultRatio={isDesktop ? 0.75 : 0.65}
            collapseAt={PANEL_COLLAPSE_BREAKPOINT}
            collapsePriority="secondary"
            minPaneSize={isTablet ? 200 : 300}
            resizable={isDesktop}
            primary={canvasWithOverlays}
            secondary={
              <div className="h-full border-l border-gray-700 bg-gray-800 overflow-auto">
                {sidebar}
              </div>
            }
          />
        ) : (
          canvasWithOverlays
        )}
      </div>
    </div>
  );
}

// Need React import for useState
import * as React from 'react';

export default Elastic3DPage;
