/**
 * DirectorPage — Documents (Living Document Canvas)
 *
 * Philosophy:
 *   "The canvas breathes. Documents arrive, analyze, become ready."
 *   "This is not accounting. This is gardening."
 */

import { useCallback, useRef } from 'react';
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

export function DirectorPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    <div className="full-height">
      <input
        ref={fileInputRef}
        type="file"
        hidden
        onChange={handleFileSelect}
        accept=".md,.txt,.py,.ts,.tsx,.js,.jsx,.json,.yaml,.yml"
      />
      <DirectorDashboard onSelectDocument={handleSelectDocument} onUpload={handleUpload} />
    </div>
  );
}

export default DirectorPage;
