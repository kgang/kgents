/**
 * HypergraphEditorPage — Membrane Editor
 *
 * "The file is a lie. There is only the graph."
 *
 * URL Routing:
 * - /editor — Show FileExplorer
 * - /editor/<spec-path> — Open directly to this path
 */

import { useCallback, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

import { HypergraphEditor, FileExplorer, normalizePath, useFileUpload } from '../hypergraph';
import { useRecentFiles } from '../hypergraph/useRecentFiles';

import './HypergraphEditorPage.css';

export function HypergraphEditorPage() {
  const { '*': rawPath } = useParams();
  const navigate = useNavigate();

  // Get path from URL
  const initialPath = rawPath ? normalizePath(rawPath) : null;
  const [currentPath, setCurrentPath] = useState<string | null>(initialPath);

  // Recent files management
  const { recentFiles, addRecentFile } = useRecentFiles();

  // File upload logic
  const { loadNode, handleUploadFile } = useFileUpload({
    onFileReady: (path: string) => {
      const normalized = normalizePath(path);
      setCurrentPath(normalized);
      addRecentFile(normalized);
      navigate(`/editor/${normalized}`);
    },
  });

  // Sync path with URL
  useEffect(() => {
    const normalized = rawPath ? normalizePath(rawPath) : null;
    if (normalized !== currentPath) {
      setCurrentPath(normalized);
    }
  }, [rawPath, currentPath]);

  // Handle file selection from explorer
  const handleOpenFile = useCallback(
    (path: string) => {
      const normalized = normalizePath(path);
      setCurrentPath(normalized);
      addRecentFile(normalized);
      navigate(`/editor/${normalized}`);
    },
    [navigate, addRecentFile]
  );

  return (
    <div className="hypergraph-editor-page">
      {currentPath ? (
        <HypergraphEditor
          initialPath={currentPath}
          onNavigate={handleOpenFile}
          loadNode={loadNode}
        />
      ) : (
        <FileExplorer
          onOpenFile={handleOpenFile}
          onUploadFile={handleUploadFile}
          recentFiles={recentFiles}
        />
      )}
    </div>
  );
}
