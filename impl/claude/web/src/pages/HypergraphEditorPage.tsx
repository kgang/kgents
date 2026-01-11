/**
 * HypergraphEditorPage — Workspace Container
 *
 * "The Hypergraph Editor IS the app. Everything else is a sidebar."
 *
 * UX Transformation (2025-12-25):
 * - Three-panel layout: Files (left) | Editor (center) | Chat (right)
 * - Ctrl+B: Toggle files sidebar
 * - Ctrl+J: Toggle chat sidebar
 *
 * URL Routing:
 * - /world.document — FileExplorer in left sidebar, no document open
 * - /world.document/<path> — Editor with document
 *
 * Zero Seed Integration:
 * - After Genesis, location.state.showZeroSeed triggers foundation panel
 * - Displays A1, A2, G axioms with derivation edges
 *
 * Re-render Isolation (2025-01-10):
 * - NavigationProvider stores path in a ref, not state
 * - Only HypergraphEditor subscribes to path changes (re-renders on navigate)
 * - Sidebars don't re-render when navigating between K-Blocks
 * - KBlockExplorer uses useNavigate() for dispatch, useSelectedId() for highlight
 *
 * @see docs/UX-LAWS.md
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { normalizePath, isValidFilePath, useFileUpload, ZeroSeedFoundation } from '../hypergraph';
import { isRawKBlockId, kblockIdToGenesisPath } from '../hypergraph/kblockToGraphNode';
import { NavigationProvider } from '../hooks/useNavigationState';
import { Workspace } from '../constructions/Workspace';
import './HypergraphEditorPage.css';

// =============================================================================
// Types
// =============================================================================

interface ZeroSeedContext {
  userAxiomId: string;
  userDeclaration?: string;
  layer: number;
  loss: number;
}

interface LocationState {
  highlightKBlock?: string;
  showZeroSeed?: boolean;
  zeroSeedContext?: ZeroSeedContext;
}

export function HypergraphEditorPage() {
  const { '*': rawPath } = useParams();
  const routerNavigate = useNavigate();
  const location = useLocation();

  // Extract Zero Seed context from location state (passed from Genesis)
  const locationState = location.state as LocationState | null;
  const [showZeroSeed, setShowZeroSeed] = useState<boolean>(locationState?.showZeroSeed ?? false);
  const zeroSeedContext = locationState?.zeroSeedContext;

  const normalizedRawPath = rawPath ? normalizePath(rawPath) : null;
  const initialPath =
    normalizedRawPath && isValidFilePath(normalizedRawPath) ? normalizedRawPath : null;

  // Validate path and redirect if invalid
  useEffect(() => {
    if (normalizedRawPath && !isValidFilePath(normalizedRawPath)) {
      console.warn('[HypergraphEditorPage] Invalid path, redirecting:', normalizedRawPath);
      routerNavigate('/world.document', { replace: true });
    }
  }, [normalizedRawPath, routerNavigate]);

  // Track the current path in a ref for URL sync (doesn't cause re-renders)
  const currentPathRef = useRef<string | null>(initialPath);

  // Handle navigation from Zero Seed Foundation panel
  const handleZeroSeedNavigate = useCallback(
    (nodeId: string) => {
      console.info('[HypergraphEditorPage] Zero Seed navigate:', nodeId);
      if (nodeId === zeroSeedContext?.userAxiomId) {
        setShowZeroSeed(false);
      }
    },
    [zeroSeedContext?.userAxiomId]
  );

  // Close Zero Seed panel
  const handleCloseZeroSeed = useCallback(() => {
    setShowZeroSeed(false);
    routerNavigate(location.pathname, { replace: true, state: null });
  }, [routerNavigate, location.pathname]);

  /**
   * Handle navigation callback from NavigationProvider.
   * Updates the browser URL when navigation occurs.
   */
  const handleNavigate = useCallback(
    (path: string) => {
      let normalized = normalizePath(path);

      // Convert raw K-Block IDs to file paths for cleaner URLs
      if (isRawKBlockId(normalized)) {
        const filePath = kblockIdToGenesisPath(normalized);
        if (filePath) {
          normalized = filePath;
        }
      }

      currentPathRef.current = normalized;
      routerNavigate(`/world.document/${normalized}`);
    },
    [routerNavigate]
  );

  /**
   * Handle internal navigation (edge clicks, derivation navigation).
   * Updates URL silently without triggering React Router navigation.
   */
  const handleInternalNavigate = useCallback((path: string) => {
    let normalized = normalizePath(path);

    if (isRawKBlockId(normalized)) {
      const filePath = kblockIdToGenesisPath(normalized);
      if (filePath) {
        normalized = filePath;
      }
    }

    currentPathRef.current = normalized;
    const newUrl = `/world.document/${normalized}`;
    window.history.replaceState(null, '', newUrl);
  }, []);

  return (
    <div className="hypergraph-editor-page">
      <NavigationProvider
        initialPath={initialPath}
        onNavigate={handleNavigate}
        onInternalNavigate={handleInternalNavigate}
      >
        <Workspace />
      </NavigationProvider>

      {/* Zero Seed Foundation Panel (shown after Genesis) */}
      {zeroSeedContext && (
        <ZeroSeedFoundation
          userAxiomId={zeroSeedContext.userAxiomId}
          userDeclaration={zeroSeedContext.userDeclaration}
          layer={zeroSeedContext.layer}
          loss={zeroSeedContext.loss}
          isVisible={showZeroSeed}
          onNavigate={handleZeroSeedNavigate}
          onClose={handleCloseZeroSeed}
        />
      )}
    </div>
  );
}
