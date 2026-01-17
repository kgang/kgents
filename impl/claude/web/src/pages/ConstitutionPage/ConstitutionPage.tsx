/**
 * ConstitutionPage - Personal Axiom Discovery
 *
 * AGENTESE Path: self.constitution
 *
 * "The persona is a garden, not a museum."
 * "Kent discovers his personal axioms. He didn't write them; he *discovered* them."
 *
 * This page wraps the PersonalConstitutionBuilder component, providing
 * a full-page experience for axiom discovery and constitution building.
 *
 * Features:
 * - Axiom discovery from decision history
 * - Review and accept/reject candidates
 * - View and manage personal constitution
 * - Detect and resolve contradictions (tensions)
 *
 * @see components/constitution/PersonalConstitutionBuilder.tsx
 * @see stores/personalConstitutionStore.ts
 */

import { useEffect } from 'react';
import { PersonalConstitutionBuilder } from '@/components/constitution';
import { usePersonalConstitutionStore } from '@/stores/personalConstitutionStore';
import type { AgentesePath } from '@/router/AgentesePath';
import './ConstitutionPage.css';

// =============================================================================
// Types
// =============================================================================

export interface ConstitutionPageProps {
  /** AGENTESE context passed from router */
  agenteseContext?: AgentesePath;
}

// =============================================================================
// Component
// =============================================================================

export function ConstitutionPage({ agenteseContext }: ConstitutionPageProps) {
  // Access store for potential initialization or aspect-based section selection
  const { setActiveSection } = usePersonalConstitutionStore();

  // Handle AGENTESE aspect-based navigation
  // e.g., /self.constitution:review -> navigate to review section
  useEffect(() => {
    if (agenteseContext?.aspect) {
      const aspect = agenteseContext.aspect;
      // Map aspects to sections
      const aspectToSection: Record<
        string,
        'discover' | 'review' | 'constitution' | 'contradictions'
      > = {
        discover: 'discover',
        review: 'review',
        view: 'constitution',
        constitution: 'constitution',
        tensions: 'contradictions',
        contradictions: 'contradictions',
      };

      const section = aspectToSection[aspect];
      if (section) {
        setActiveSection(section);
      }
    }
  }, [agenteseContext?.aspect, setActiveSection]);

  return (
    <div className="constitution-page">
      {/* Page Header (supplements the builder's internal header) */}
      <header className="constitution-page-header">
        <div className="header-content">
          <div className="header-breadcrumb">
            <span className="context">self</span>
            <span className="separator">.</span>
            <span className="entity">constitution</span>
            {agenteseContext?.aspect && (
              <>
                <span className="separator">:</span>
                <span className="aspect">{agenteseContext.aspect}</span>
              </>
            )}
          </div>
          <p className="header-philosophy">"The persona is a garden, not a museum."</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="constitution-page-main">
        <PersonalConstitutionBuilder />
      </main>

      {/* Footer */}
      <footer className="constitution-page-footer">
        <p className="footer-quote">
          "You've made decisions this month. Here are the principles you never violated."
        </p>
      </footer>
    </div>
  );
}

export default ConstitutionPage;
