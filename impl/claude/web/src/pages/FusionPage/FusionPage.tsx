/**
 * FusionPage - Dialectical Synthesis Interface
 *
 * "Make disagreement beautiful. Create a UI where Kent and Claude can synthesize."
 *
 * From the Constitution (Article VI):
 * "The goal is not Kent's decisions or AI's decisions.
 *  The goal is fused decisions better than either alone."
 *
 * AGENTESE Paths:
 * - self.dialectic     - The dialectic state
 * - world.fusion       - Kent + Claude synthesis interface
 *
 * Features:
 * - Full-page FusionCeremony wrapper
 * - URL parameter support for initial topic
 * - AGENTESE context integration
 *
 * @see docs/theory/17-dialectic.md
 * @see spec/protocols/fusion-ceremony.md
 */

import { useSearchParams } from 'react-router-dom';
import { FusionCeremony } from '@/components/dialectic';
import type { AgentesePath } from '@/router/AgentesePath';
import type { CeremonyState } from '@/components/dialectic';
import './FusionPage.css';

// =============================================================================
// Types
// =============================================================================

export interface FusionPageProps {
  /** Optional AGENTESE context for navigation integration */
  agenteseContext?: AgentesePath;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * FusionPage - Full-page dialectical synthesis experience.
 *
 * Wraps FusionCeremony with page-level concerns:
 * - URL parameter extraction (topic)
 * - AGENTESE path context
 * - Page-level layout and navigation
 *
 * @example
 * // Direct usage
 * <FusionPage />
 *
 * @example
 * // With AGENTESE context (from router)
 * <FusionPage agenteseContext={parsedPath} />
 *
 * @example
 * // URL with topic: /self.dialectic?topic=architecture
 * // Automatically pre-fills the topic field
 */
export function FusionPage({ agenteseContext }: FusionPageProps) {
  const [searchParams] = useSearchParams();

  // Extract optional URL parameters
  const initialTopic = searchParams.get('topic') || '';
  const initialKentView = searchParams.get('kent') || '';
  const initialClaudeView = searchParams.get('claude') || '';

  /**
   * Handle fusion completion.
   * Could be used for analytics, navigation, or state persistence.
   */
  const handleFusionComplete = (state: CeremonyState) => {
    // Log for now; could integrate with witness system
    console.info('[FusionPage] Fusion complete:', {
      fusionId: state.fusionId,
      result: state.result,
      topic: state.topic,
      agenteseContext: agenteseContext?.fullPath,
    });
  };

  return (
    <div className="fusion-page">
      {/* Page Header */}
      <header className="fusion-page__header">
        <div className="fusion-page__header-content">
          <h1 className="fusion-page__title">Dialectical Synthesis</h1>
          <p className="fusion-page__subtitle">
            Kent + Claude fusion. Not compromise, but Aufhebung.
          </p>
          {agenteseContext && (
            <div className="fusion-page__context">
              <span className="fusion-page__context-label">Context:</span>
              <code className="fusion-page__context-path">{agenteseContext.fullPath}</code>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="fusion-page__main">
        <FusionCeremony
          initialTopic={initialTopic}
          initialKentView={initialKentView}
          initialClaudeView={initialClaudeView}
          onFusionComplete={handleFusionComplete}
          className="fusion-page__ceremony"
        />
      </main>

      {/* Page Footer */}
      <footer className="fusion-page__footer">
        <p className="fusion-page__quote">
          "The goal is not Kent's decisions or AI's decisions. The goal is fused decisions better
          than either alone."
        </p>
        <p className="fusion-page__attribution">— Constitution, Article VI</p>
      </footer>
    </div>
  );
}

export default FusionPage;
