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

import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

import { DirectorDashboard } from '../components/DirectorDashboard';

// =============================================================================
// Component
// =============================================================================

export function DirectorPage() {
  const navigate = useNavigate();

  // Navigate to editor with document path
  const handleSelectDocument = useCallback(
    (path: string) => {
      navigate(`/editor/${path}`);
    },
    [navigate]
  );

  // Handle upload action (could open a modal or navigate)
  const handleUpload = useCallback(() => {
    // TODO: Implement upload modal or navigate to upload page
    console.info('[DirectorPage] Upload requested');
  }, []);

  return (
    <div style={{ height: '100%', width: '100%', overflow: 'hidden' }}>
      <DirectorDashboard
        onSelectDocument={handleSelectDocument}
        onUpload={handleUpload}
      />
    </div>
  );
}

export default DirectorPage;
