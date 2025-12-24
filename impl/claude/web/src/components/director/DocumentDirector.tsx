/**
 * DocumentDirector - Main container component
 *
 * Tabs: Dashboard | Documents | (Detail when selected)
 *
 * Philosophy:
 *   "Upload → Analyze → Generate → Execute → Capture → Verify"
 */

import { useState } from 'react';

import { DirectorDashboard } from './DirectorDashboard';
import { DocumentTable } from './DocumentTable';
import { DocumentDetail } from './DocumentDetail';
import { analyzeDocument } from '../../api/director';

import './DocumentDirector.css';

// =============================================================================
// Types
// =============================================================================

type Tab = 'dashboard' | 'documents' | 'detail';

// =============================================================================
// Component
// =============================================================================

export function DocumentDirector() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [selectedPath, setSelectedPath] = useState<string | null>(null);

  // Handle document selection
  const handleSelectDocument = (path: string) => {
    setSelectedPath(path);
    setActiveTab('detail');
  };

  // Handle analyze action
  const handleAnalyzeDocument = async (path: string) => {
    try {
      await analyzeDocument(path, true);
      // Optionally navigate to detail view after analysis
      setSelectedPath(path);
      setActiveTab('detail');
    } catch (err) {
      console.error('Failed to analyze document:', err);
    }
  };

  // Handle generate prompt action
  const handleGeneratePrompt = (path: string) => {
    // Navigate to detail view where prompt generation happens
    setSelectedPath(path);
    setActiveTab('detail');
  };

  // Handle close detail
  const handleCloseDetail = () => {
    setSelectedPath(null);
    setActiveTab('documents');
  };

  // Handle navigate to documents
  const handleNavigateToDocuments = () => {
    setActiveTab('documents');
  };

  return (
    <div className="document-director">
      {/* Tab Bar */}
      <div className="document-director__tabs">
        <button
          className="document-director__tab"
          data-active={activeTab === 'dashboard'}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button
          className="document-director__tab"
          data-active={activeTab === 'documents'}
          onClick={() => setActiveTab('documents')}
        >
          Documents
        </button>
        {activeTab === 'detail' && selectedPath && (
          <button className="document-director__tab" data-active={true}>
            {selectedPath}
          </button>
        )}
      </div>

      {/* Content */}
      <div className="document-director__content">
        {activeTab === 'dashboard' && (
          <DirectorDashboard onNavigateToDocuments={handleNavigateToDocuments} />
        )}

        {activeTab === 'documents' && (
          <DocumentTable
            onSelectDocument={handleSelectDocument}
            onAnalyzeDocument={handleAnalyzeDocument}
            onGeneratePrompt={handleGeneratePrompt}
          />
        )}

        {activeTab === 'detail' && selectedPath && (
          <DocumentDetail path={selectedPath} onClose={handleCloseDetail} />
        )}
      </div>
    </div>
  );
}
