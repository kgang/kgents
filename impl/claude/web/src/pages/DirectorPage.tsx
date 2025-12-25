/**
 * DirectorPage — Documents (Living Document Canvas)
 *
 * The canonical documents viewer for kgents.
 * No batch "Scan Corpus" — documents auto-analyze on upload.
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
// Component
// =============================================================================

export function DirectorPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Navigate to editor with document path
  const handleSelectDocument = useCallback(
    (path: string) => {
      navigate(`/world.document/${path}`);
    },
    [navigate]
  );

  // Handle file selection from input
  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    console.info('[DirectorPage] File selected:', file.name, `(${file.size} bytes)`);

    try {
      // Read file content
      const content = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => resolve(event.target?.result as string);
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsText(file);
      });

      // Upload to sovereign store
      const uploadPath = `uploads/${file.name}`;
      const result = await sovereignApi.ingest({
        path: uploadPath,
        content,
        source: 'director-upload',
      });

      console.info(
        '[DirectorPage] Upload successful:',
        result.path,
        `v${result.version}`,
        `(${result.edge_count} edges, mark: ${result.ingest_mark_id})`
      );

      // Navigate to editor to view the uploaded document
      navigate(`/world.document/${result.path}`);
    } catch (err) {
      console.error('[DirectorPage] Upload failed:', err);
      // TODO: Show error notification to user
    } finally {
      // Reset file input so the same file can be uploaded again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  }, [navigate]);

  // Trigger file input click
  const handleUpload = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className="full-height">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
        accept=".md,.txt,.py,.ts,.tsx,.js,.jsx,.json,.yaml,.yml"
      />

      <DirectorDashboard
        onSelectDocument={handleSelectDocument}
        onUpload={handleUpload}
      />
    </div>
  );
}

export default DirectorPage;
