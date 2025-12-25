/**
 * HypergraphEditorPage — Membrane Editor
 *
 * "The file is a lie. There is only the graph."
 *
 * URL Routing:
 * - /world.document — Show FileExplorer
 * - /world.document/<spec-path> — Open directly to this path
 */

import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { HypergraphEditor, FileExplorer, normalizePath, isValidFilePath, useFileUpload } from '../hypergraph';
import { useRecentFiles } from '../hypergraph/useRecentFiles';

import './HypergraphEditorPage.css';

export function HypergraphEditorPage() {
  const { '*': rawPath } = useParams();
  const navigate = useNavigate();

  // Get path from URL, but validate it first to prevent edge labels from causing infinite loops
  const normalizedRawPath = rawPath ? normalizePath(rawPath) : null;
  const initialPath = normalizedRawPath && isValidFilePath(normalizedRawPath) ? normalizedRawPath : null;

  // Log warning if an invalid path was in the URL
  useEffect(() => {
    if (normalizedRawPath && !isValidFilePath(normalizedRawPath)) {
      console.warn(
        '[HypergraphEditorPage] Invalid path in URL (edge label or malformed), redirecting to file explorer:',
        normalizedRawPath
      );
      // Redirect to base editor (file explorer) to prevent the bad URL from persisting
      navigate('/world.document', { replace: true });
    }
  }, [normalizedRawPath, navigate]);

  const [currentPath, setCurrentPath] = useState<string | null>(initialPath);

  // Recent files management
  const { recentFiles, addRecentFile, removeRecentFile, clearRecentFiles } = useRecentFiles();

  // File upload logic with error handling
  const { loadNode: rawLoadNode, handleUploadFile } = useFileUpload({
    onFileReady: (path: string) => {
      const normalized = normalizePath(path);
      setCurrentPath(normalized);
      addRecentFile(normalized);
      navigate(`/world.document/${normalized}`);
    },
  });

  // Wrap loadNode to handle errors and remove deleted files from recent
  const loadNode = useCallback(
    async (path: string) => {
      try {
        const node = await rawLoadNode(path);
        if (!node) {
          // File doesn't exist - remove from recent
          console.info('[HypergraphEditorPage] File not found, removing from recent:', path);
          removeRecentFile(path);
        }
        return node;
      } catch (error) {
        // Load error - likely file was deleted
        console.warn('[HypergraphEditorPage] Failed to load file, removing from recent:', path, error);
        removeRecentFile(path);
        return null;
      }
    },
    [rawLoadNode, removeRecentFile]
  );

  // Sync path with URL (only for valid paths)
  useEffect(() => {
    const normalized = rawPath ? normalizePath(rawPath) : null;
    // Only sync if it's a valid file path to prevent edge labels from causing issues
    if (normalized && isValidFilePath(normalized) && normalized !== currentPath) {
      setCurrentPath(normalized);
    } else if (!normalized && currentPath) {
      // URL cleared, clear current path
      setCurrentPath(null);
    }
  }, [rawPath, currentPath]);

  // Handle file selection from explorer
  const handleOpenFile = useCallback(
    (path: string) => {
      const normalized = normalizePath(path);
      setCurrentPath(normalized);
      addRecentFile(normalized);
      navigate(`/world.document/${normalized}`);
    },
    [navigate, addRecentFile]
  );

  // Handle Zero Seed navigation
  const handleZeroSeed = useCallback(
    (tab?: string) => {
      if (tab) {
        navigate(`/zero-seed?tab=${tab}`);
      } else {
        navigate('/zero-seed');
      }
    },
    [navigate]
  );

  return (
    <div className="hypergraph-editor-page">
      {currentPath ? (
        <HypergraphEditor
          initialPath={currentPath}
          onNavigate={handleOpenFile}
          loadNode={loadNode}
          onZeroSeed={handleZeroSeed}
        />
      ) : (
        <FileExplorer
          onOpenFile={handleOpenFile}
          onUploadFile={handleUploadFile}
          recentFiles={recentFiles}
          onClearRecent={clearRecentFiles}
        />
      )}
    </div>
  );
}
