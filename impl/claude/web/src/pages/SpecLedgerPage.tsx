/**
 * SpecLedgerPage — The Accounting View of Specifications
 *
 * Three views, one ledger:
 * - Dashboard: Assets vs Liabilities overview
 * - Table: All specs in accounting-style rows
 * - Detail: Deep dive into single spec
 *
 * Philosophy:
 *   "Every spec is an asset or a liability."
 *   "Evidence is the only currency that matters."
 */

import { useState, useCallback } from 'react';

import { LedgerDashboard } from '../membrane/views/LedgerDashboard';
import { SpecTable } from '../membrane/views/SpecTable';
import { SpecLedgerDetail } from '../membrane/views/SpecLedgerDetail';

import './SpecLedgerPage.css';

// =============================================================================
// Types
// =============================================================================

type LedgerView = 'dashboard' | 'table' | 'detail';

// =============================================================================
// Component
// =============================================================================

export function SpecLedgerPage() {
  const [view, setView] = useState<LedgerView>('dashboard');
  const [selectedSpecPath, setSelectedSpecPath] = useState<string | null>(null);

  // Navigate to spec detail
  const handleSelectSpec = useCallback((path: string) => {
    setSelectedSpecPath(path);
    setView('detail');
  }, []);

  // Navigate back from detail
  const handleCloseDetail = useCallback(() => {
    setSelectedSpecPath(null);
    setView('table');
  }, []);

  // Navigate to table view
  const handleViewTable = useCallback(() => {
    setView('table');
  }, []);

  return (
    <div className="spec-ledger-page">
      {/* Navigation Tabs */}
      <nav className="spec-ledger-page__nav">
        <button
          className={`spec-ledger-page__tab ${view === 'dashboard' ? 'spec-ledger-page__tab--active' : ''}`}
          onClick={() => setView('dashboard')}
        >
          Dashboard
        </button>
        <button
          className={`spec-ledger-page__tab ${view === 'table' ? 'spec-ledger-page__tab--active' : ''}`}
          onClick={handleViewTable}
        >
          All Specs
        </button>
        {selectedSpecPath && (
          <button
            className={`spec-ledger-page__tab ${view === 'detail' ? 'spec-ledger-page__tab--active' : ''}`}
            onClick={() => setView('detail')}
          >
            Detail
          </button>
        )}

        <div className="spec-ledger-page__nav-spacer" />

        <span className="spec-ledger-page__title">SPEC LEDGER</span>
      </nav>

      {/* View Content */}
      <div className="spec-ledger-page__content">
        {view === 'dashboard' && <LedgerDashboard onNavigateToSpec={handleSelectSpec} />}
        {view === 'table' && <SpecTable onSelectSpec={handleSelectSpec} />}
        {view === 'detail' && selectedSpecPath && (
          <SpecLedgerDetail
            path={selectedSpecPath}
            onNavigateToSpec={handleSelectSpec}
            onClose={handleCloseDetail}
          />
        )}
      </div>
    </div>
  );
}

export default SpecLedgerPage;
