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
 * @see docs/UX-LAWS.md
 */

import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { normalizePath, isValidFilePath, useFileUpload, ZeroSeedFoundation } from '../hypergraph';
import { useRecentFiles } from '../hypergraph/useRecentFiles';
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
  const navigate = useNavigate();
  const location = useLocation();

  // Extract Zero Seed context from location state (passed from Genesis)
  const locationState = location.state as LocationState | null;
  const [showZeroSeed, setShowZeroSeed] = useState<boolean>(
    locationState?.showZeroSeed ?? false
  );
  const zeroSeedContext = locationState?.zeroSeedContext;

  const normalizedRawPath = rawPath ? normalizePath(rawPath) : null;
  const initialPath = normalizedRawPath && isValidFilePath(normalizedRawPath) ? normalizedRawPath : null;

  // Validate path and redirect if invalid
  useEffect(() => {
    if (normalizedRawPath && !isValidFilePath(normalizedRawPath)) {
      console.warn('[HypergraphEditorPage] Invalid path, redirecting:', normalizedRawPath);
      navigate('/world.document', { replace: true });
    }
  }, [normalizedRawPath, navigate]);

  const [currentPath, setCurrentPath] = useState<string | null>(initialPath);
  const { recentFiles, addRecentFile, removeRecentFile, clearRecentFiles } = useRecentFiles();

  // Handle navigation from Zero Seed Foundation panel
  const handleZeroSeedNavigate = useCallback(
    (nodeId: string) => {
      // For foundational axioms (A1, A2, G), we might want to navigate to a special view
      // For now, just log and close the panel
      console.info('[HypergraphEditorPage] Zero Seed navigate:', nodeId);
      // If it's the user's axiom, navigate to it
      if (nodeId === zeroSeedContext?.userAxiomId) {
        // User's K-Block - navigate to it if we have a path
        // For now, just close the panel
        setShowZeroSeed(false);
      }
    },
    [zeroSeedContext?.userAxiomId]
  );

  // Close Zero Seed panel
  const handleCloseZeroSeed = useCallback(() => {
    setShowZeroSeed(false);
    // Clear location state to prevent panel from reappearing on refresh
    navigate(location.pathname, { replace: true, state: null });
  }, [navigate, location.pathname]);

  const handleFileReady = useCallback(
    (path: string) => {
      const normalized = normalizePath(path);
      setCurrentPath(normalized);
      addRecentFile(normalized);
      navigate(`/world.document/${normalized}`);
    },
    [addRecentFile, navigate]
  );

  const { loadNode: rawLoadNode, handleUploadFile } = useFileUpload({ onFileReady: handleFileReady });

  const loadNode = useCallback(
    async (path: string) => {
      try {
        const node = await rawLoadNode(path);
        if (!node) {
          console.info('[HypergraphEditorPage] File not found, removing from recent:', path);
          removeRecentFile(path);
        }
        return node;
      } catch (error) {
        console.warn('[HypergraphEditorPage] Load failed, removing from recent:', path, error);
        removeRecentFile(path);
        return null;
      }
    },
    [rawLoadNode, removeRecentFile]
  );

  // Sync path with URL
  useEffect(() => {
    const normalized = rawPath ? normalizePath(rawPath) : null;
    if (normalized && isValidFilePath(normalized) && normalized !== currentPath) {
      setCurrentPath(normalized);
    } else if (!normalized && currentPath) {
      setCurrentPath(null);
    }
  }, [rawPath, currentPath]);

  return (
    <div className="hypergraph-editor-page">
      <Workspace
        currentPath={currentPath}
        recentFiles={recentFiles}
        onNavigate={handleFileReady}
        onUploadFile={handleUploadFile}
        onClearRecent={clearRecentFiles}
        loadNode={loadNode}
      />

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
