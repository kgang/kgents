/**
 * Zero Seed Personal Governance Lab
 *
 * "Your axioms are not what you think they are. Galois loss reveals them."
 *
 * This pilot treats value articulation as archaeology, not construction.
 * You're not creating values - you're discovering what was already there,
 * then choosing whether to keep it.
 *
 * Design Philosophy (from PROTO_SPEC):
 * - QA-1: Value discovery feels like recognition, not invention
 * - QA-2: Amendment process feels ceremonial but not burdensome
 * - QA-3: Contradiction surfacing feels clarifying, not judgmental
 * - QA-4: After a month, produces a shareable personal constitution
 * - QA-5: System never tells you what to value
 *
 * Anti-Patterns Avoided:
 * - NO value imposition (prescribing what to believe)
 * - NO coherence worship (optimizing Galois score)
 * - NO amendment theater (bureaucratic ritual)
 * - NO contradiction shame (feeling bad about conflicts)
 * - NO philosophical gatekeeping (only for "philosophers")
 *
 * Joy Dimension: SURPRISE ("Oh, that's what I actually believe")
 *
 * @see pilots/zero-seed-personal-governance-lab/PROTO_SPEC.md
 */

import { useState, useEffect, useCallback } from 'react';
import type {
  DiscoveredAxiom,
  Constitution,
  ConstitutionContradiction,
  DiscoveryReport,
} from '@kgents/shared-primitives';
import { LIVING_EARTH, useWindowLayout } from '@kgents/shared-primitives';
import { DiscoveryWizard } from './components/DiscoveryWizard';
import { ConstitutionView } from './components/ConstitutionView';
import { ContradictionExplorer } from './components/ContradictionExplorer';
import {
  discoverAxiomsFromText,
  validateAxiom,
  getConstitution,
  addAxiomToConstitution,
  retireAxiom,
  detectContradictions,
  ZeroSeedApiError,
} from '@/api/zero-seed';

// =============================================================================
// Types
// =============================================================================

type ViewMode = 'discovery' | 'constitution' | 'contradictions';

interface ZeroSeedLabState {
  /** Discovered axioms from latest discovery run */
  discoveredAxioms: DiscoveredAxiom[];
  /** Latest discovery report with stats */
  discoveryReport?: DiscoveryReport;
  /** Current personal constitution */
  constitution?: Constitution;
  /** Detected contradictions */
  contradictions: ConstitutionContradiction[];
  /** Currently selected axiom for detail view */
  selectedAxiom?: DiscoveredAxiom;
  /** Active view mode */
  viewMode: ViewMode;
  /** Loading states */
  isDiscovering: boolean;
  isValidating: boolean;
  isLoadingConstitution: boolean;
  /** Error message if any */
  error?: string;
}

// =============================================================================
// Density-aware Sizing
// =============================================================================

const SIZES = {
  compact: {
    gap: 'gap-3',
    padding: 'p-3',
    maxWidth: 'max-w-lg',
    headerText: 'text-lg',
    navGap: 'gap-2',
  },
  comfortable: {
    gap: 'gap-4',
    padding: 'p-4',
    maxWidth: 'max-w-2xl',
    headerText: 'text-xl',
    navGap: 'gap-3',
  },
  spacious: {
    gap: 'gap-6',
    padding: 'p-6',
    maxWidth: 'max-w-3xl',
    headerText: 'text-2xl',
    navGap: 'gap-4',
  },
} as const;

// =============================================================================
// Component
// =============================================================================

/**
 * ZeroSeedLabPilot
 *
 * Main pilot page for Zero Seed Personal Governance Lab.
 * Manages state and API interactions for value discovery,
 * constitution building, and contradiction exploration.
 *
 * @example
 * // In router:
 * <Route path="/pilots/zero-seed" element={<ZeroSeedLabPilot />} />
 */
export function ZeroSeedLabPilot() {
  const { density } = useWindowLayout();
  const sizes = SIZES[density];

  const [state, setState] = useState<ZeroSeedLabState>({
    discoveredAxioms: [],
    contradictions: [],
    viewMode: 'discovery',
    isDiscovering: false,
    isValidating: false,
    isLoadingConstitution: false,
  });

  // Load constitution on mount
  useEffect(() => {
    const loadConstitution = async () => {
      setState((prev) => ({ ...prev, isLoadingConstitution: true, error: undefined }));

      try {
        const constitution = await getConstitution();
        setState((prev) => ({
          ...prev,
          constitution,
          isLoadingConstitution: false,
        }));
      } catch (error) {
        // Don't show error for new users without constitution
        if (error instanceof ZeroSeedApiError && error.status === 404) {
          setState((prev) => ({ ...prev, isLoadingConstitution: false }));
        } else {
          const message =
            error instanceof ZeroSeedApiError
              ? error.detail
              : error instanceof Error
                ? error.message
                : 'Failed to load constitution';

          setState((prev) => ({
            ...prev,
            isLoadingConstitution: false,
            error: message,
          }));
        }
      }
    };

    loadConstitution();
  }, []);

  // Handle axiom discovery from corpus
  const handleDiscover = useCallback(async (corpus: string) => {
    setState((prev) => ({
      ...prev,
      isDiscovering: true,
      error: undefined,
      discoveredAxioms: [],
    }));

    try {
      // Split corpus into meaningful chunks (paragraphs, sentences, etc.)
      const texts = corpus
        .split(/\n\n+/)
        .map((t) => t.trim())
        .filter((t) => t.length > 10);

      if (texts.length === 0) {
        throw new Error('Please provide more text to analyze (at least a few sentences)');
      }

      const report = await discoverAxiomsFromText(texts, { minOccurrences: 1 });

      setState((prev) => ({
        ...prev,
        discoveredAxioms: report.discovered_axioms,
        discoveryReport: report,
        isDiscovering: false,
      }));
    } catch (error) {
      const message =
        error instanceof ZeroSeedApiError
          ? error.detail
          : error instanceof Error
            ? error.message
            : 'Discovery failed';

      setState((prev) => ({
        ...prev,
        isDiscovering: false,
        error: message,
      }));
    }
  }, []);

  // Handle adding axiom to constitution
  const handleAddToConstitution = useCallback(
    async (axiom: DiscoveredAxiom) => {
      setState((prev) => ({ ...prev, isValidating: true, error: undefined }));

      try {
        const updated = await addAxiomToConstitution(axiom, {
          check_contradictions: true,
        });

        // Remove from discovered list
        setState((prev) => ({
          ...prev,
          constitution: updated,
          discoveredAxioms: prev.discoveredAxioms.filter(
            (a) => a.content !== axiom.content
          ),
          isValidating: false,
        }));
      } catch (error) {
        const message =
          error instanceof ZeroSeedApiError
            ? error.detail
            : error instanceof Error
              ? error.message
              : 'Failed to add axiom';

        setState((prev) => ({
          ...prev,
          isValidating: false,
          error: message,
        }));
      }
    },
    []
  );

  // Handle validating a custom axiom
  const handleValidateCustom = useCallback(async (content: string) => {
    setState((prev) => ({ ...prev, isValidating: true, error: undefined }));

    try {
      const result = await validateAxiom(content);

      if (result.is_axiom) {
        // Create a discovered axiom from the validation result
        const axiom: DiscoveredAxiom = {
          content,
          loss: result.loss,
          stability: result.stability,
          iterations: result.iterations,
          confidence: 1 - result.loss,
          source_decisions: [],
        };

        // Add to discovered axioms
        setState((prev) => ({
          ...prev,
          discoveredAxioms: [axiom, ...prev.discoveredAxioms],
          isValidating: false,
        }));
      } else {
        setState((prev) => ({
          ...prev,
          isValidating: false,
          error: `This doesn't quite qualify as an axiom yet (loss: ${(result.loss * 100).toFixed(1)}%). Try making it more fundamental.`,
        }));
      }
    } catch (error) {
      const message =
        error instanceof ZeroSeedApiError
          ? error.detail
          : error instanceof Error
            ? error.message
            : 'Validation failed';

      setState((prev) => ({
        ...prev,
        isValidating: false,
        error: message,
      }));
    }
  }, []);

  // Handle retiring an axiom
  const handleRetire = useCallback(
    async (axiomId: string, reason: string) => {
      try {
        const updated = await retireAxiom({ axiom_id: axiomId, reason });
        setState((prev) => ({
          ...prev,
          constitution: updated,
        }));
      } catch (error) {
        const message =
          error instanceof ZeroSeedApiError
            ? error.detail
            : error instanceof Error
              ? error.message
              : 'Failed to retire axiom';

        setState((prev) => ({ ...prev, error: message }));
      }
    },
    []
  );

  // Handle detecting contradictions
  const handleDetectContradictions = useCallback(async () => {
    try {
      const report = await detectContradictions();
      setState((prev) => ({
        ...prev,
        contradictions: report.contradictions,
        viewMode: 'contradictions',
      }));
    } catch (error) {
      const message =
        error instanceof ZeroSeedApiError
          ? error.detail
          : error instanceof Error
            ? error.message
            : 'Failed to detect contradictions';

      setState((prev) => ({ ...prev, error: message }));
    }
  }, []);

  // Handle view mode change
  const handleViewChange = useCallback((mode: ViewMode) => {
    setState((prev) => ({ ...prev, viewMode: mode, error: undefined }));
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setState((prev) => ({ ...prev, error: undefined }));
  }, []);

  return (
    <div
      className={`zero-seed-lab mx-auto ${sizes.maxWidth} ${sizes.padding}`}
      style={{ minHeight: '100vh', background: LIVING_EARTH.bark }}
    >
      {/* Header */}
      <header className="mb-6">
        <h1
          className={`${sizes.headerText} font-semibold`}
          style={{ color: LIVING_EARTH.lantern }}
        >
          Personal Governance Lab
        </h1>
        <p
          className="text-sm mt-1 opacity-70"
          style={{ color: LIVING_EARTH.sand }}
        >
          Discover what you actually believe, not what you think you believe.
        </p>
      </header>

      {/* Navigation Tabs */}
      <nav className={`flex ${sizes.navGap} mb-6`}>
        <NavTab
          active={state.viewMode === 'discovery'}
          onClick={() => handleViewChange('discovery')}
          label="Discover"
          description="Surface your axioms"
        />
        <NavTab
          active={state.viewMode === 'constitution'}
          onClick={() => handleViewChange('constitution')}
          label="Constitution"
          description={
            state.constitution
              ? `${state.constitution.active_count} axioms`
              : 'Your values'
          }
        />
        <NavTab
          active={state.viewMode === 'contradictions'}
          onClick={() => handleViewChange('contradictions')}
          label="Tensions"
          description={
            state.contradictions.length > 0
              ? `${state.contradictions.length} found`
              : 'Explore conflicts'
          }
        />
      </nav>

      {/* Error display */}
      {state.error && (
        <div
          className={`${sizes.padding} rounded-lg mb-4 flex justify-between items-start`}
          style={{
            background: `${LIVING_EARTH.rust}22`,
            border: `1px solid ${LIVING_EARTH.rust}44`,
          }}
        >
          <p style={{ color: LIVING_EARTH.rust }}>{state.error}</p>
          <button
            onClick={clearError}
            className="ml-4 opacity-60 hover:opacity-100"
            style={{ color: LIVING_EARTH.rust }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <main className={`flex flex-col ${sizes.gap}`}>
        {state.viewMode === 'discovery' && (
          <DiscoveryWizard
            discoveredAxioms={state.discoveredAxioms}
            discoveryReport={state.discoveryReport}
            isDiscovering={state.isDiscovering}
            isValidating={state.isValidating}
            onDiscover={handleDiscover}
            onValidateCustom={handleValidateCustom}
            onAddToConstitution={handleAddToConstitution}
            onSelectAxiom={(axiom) =>
              setState((prev) => ({ ...prev, selectedAxiom: axiom }))
            }
          />
        )}

        {state.viewMode === 'constitution' && (
          <ConstitutionView
            constitution={state.constitution}
            isLoading={state.isLoadingConstitution}
            onRetireAxiom={handleRetire}
            onDetectContradictions={handleDetectContradictions}
          />
        )}

        {state.viewMode === 'contradictions' && (
          <ContradictionExplorer
            contradictions={state.contradictions}
            constitution={state.constitution}
            onDetect={handleDetectContradictions}
          />
        )}
      </main>

      {/* Footer */}
      <footer
        className="mt-12 pt-6 border-t"
        style={{ borderColor: `${LIVING_EARTH.sage}22` }}
      >
        <p
          className="text-xs text-center opacity-40"
          style={{ color: LIVING_EARTH.sand }}
        >
          Zero Seed Personal Governance Lab - Know thyself, computationally.
        </p>
      </footer>
    </div>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

interface NavTabProps {
  active: boolean;
  onClick: () => void;
  label: string;
  description: string;
}

function NavTab({ active, onClick, label, description }: NavTabProps) {
  return (
    <button
      onClick={onClick}
      className={`
        flex-1 rounded-lg px-4 py-3 text-left transition-all duration-150
        ${active ? 'ring-2' : 'opacity-60 hover:opacity-80'}
      `}
      style={{
        background: active ? `${LIVING_EARTH.sage}22` : 'transparent',
        borderColor: active ? LIVING_EARTH.sage : 'transparent',
        // Use CSS custom property for ring color since ringColor is not a valid CSS property
        ['--tw-ring-color' as string]: active ? LIVING_EARTH.sage : undefined,
      }}
    >
      <span
        className="block font-medium"
        style={{ color: active ? LIVING_EARTH.lantern : LIVING_EARTH.sand }}
      >
        {label}
      </span>
      <span
        className="block text-xs mt-0.5"
        style={{ color: LIVING_EARTH.sand }}
      >
        {description}
      </span>
    </button>
  );
}

export default ZeroSeedLabPilot;
