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
 * @see docs/UX-LAWS.md
 */

import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { normalizePath, isValidFilePath, useFileUpload } from '../hypergraph';
import { useRecentFiles } from '../hypergraph/useRecentFiles';
import { Workspace } from '../constructions/Workspace';
import './HypergraphEditorPage.css';

export function HypergraphEditorPage() {
  const { '*': rawPath } = useParams();
  const navigate = useNavigate();

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
    </div>
  );
}
