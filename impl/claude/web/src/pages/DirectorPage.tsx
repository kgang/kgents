/**
 * DirectorPage — Documents (Living Document Canvas)
 *
 * @deprecated This page is DEPRECATED as of 2025-12-25.
 * File browser functionality has been moved to a sidebar in the Hypergraph Editor.
 * Use /world.document and toggle the files sidebar with Ctrl+B (Cmd+B on Mac).
 *
 * This page is kept for backward compatibility during the grace period.
 * It will be removed in a future release.
 *
 * Philosophy:
 *   "The canvas breathes. Documents arrive, analyze, become ready."
 *   "This is not accounting. This is gardening."
 */

import { useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { DirectorDashboard } from '../components/DirectorDashboard';
import { sovereignApi } from '../api/client';

// =============================================================================
// Helpers
// =============================================================================

async function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => resolve(e.target?.result as string);
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

// =============================================================================
// Component
// =============================================================================

/**
 * @deprecated Use the Files sidebar in /world.document instead (Ctrl+B to toggle)
 */
export function DirectorPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Log deprecation warning on mount
  useEffect(() => {
    console.warn(
      '[DEPRECATED] DirectorPage is deprecated. ' +
        'File browser is now a sidebar in /world.document. Use Ctrl+B (Cmd+B on Mac) to toggle.'
    );
  }, []);

  const handleSelectDocument = useCallback(
    (path: string) => navigate(`/world.document/${path}`),
    [navigate]
  );

  const handleFileSelect = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      console.info('[DirectorPage] Uploading:', file.name, `(${file.size} bytes)`);

      try {
        const content = await readFileAsText(file);
        const result = await sovereignApi.ingest({
          path: `uploads/${file.name}`,
          content,
          source: 'director-upload',
        });

        console.info(
          '[DirectorPage] Upload success:',
          result.path,
          `v${result.version}`,
          `(${result.edge_count} edges, mark: ${result.ingest_mark_id})`
        );

        navigate(`/world.document/${result.path}`);
      } catch (err) {
        console.error('[DirectorPage] Upload failed:', err);
      } finally {
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      }
    },
    [navigate]
  );

  const handleUpload = useCallback(() => fileInputRef.current?.click(), []);

  return (
    <div className="full-height flex flex-col">
      {/* Deprecation Banner */}
      <div className="bg-amber-900/30 border-b border-amber-700/50 px-4 py-2 text-amber-200 text-sm flex-shrink-0">
        <strong>DEPRECATED:</strong> This page is deprecated. Files browser is now a sidebar in the{' '}
        <a href="/world.document" className="underline hover:text-amber-100">
          Hypergraph Editor
        </a>
        . Use <kbd className="px-1 py-0.5 bg-amber-800/50 rounded text-xs">Ctrl+B</kbd> to toggle.
      </div>

      <input
        ref={fileInputRef}
        type="file"
        hidden
        onChange={handleFileSelect}
        accept=".md,.txt,.py,.ts,.tsx,.js,.jsx,.json,.yaml,.yml"
      />
      <div className="flex-1 overflow-auto">
        <DirectorDashboard onSelectDocument={handleSelectDocument} onUpload={handleUpload} />
      </div>
    </div>
  );
}

export default DirectorPage;
