/**
 * useAnalysis — Hook for fetching four-mode analysis reports
 *
 * "Analysis is not one thing but four: verification of laws, grounding of claims,
 *  resolution of tensions, and regeneration from axioms."
 *
 * Fetches analysis data from the backend Analysis Operad service.
 */

import { useState, useEffect, useCallback } from 'react';

// =============================================================================
// Types (Mirror Python dataclasses from agents/operad/domains/analysis.py)
// =============================================================================

export enum ContradictionType {
  APPARENT = 'APPARENT',
  PRODUCTIVE = 'PRODUCTIVE',
  PROBLEMATIC = 'PROBLEMATIC',
  PARACONSISTENT = 'PARACONSISTENT',
}

export enum EvidenceTier {
  SOMATIC = 'SOMATIC',
  AESTHETIC = 'AESTHETIC',
  EMPIRICAL = 'EMPIRICAL',
  CATEGORICAL = 'CATEGORICAL',
  DERIVED = 'DERIVED',
}

export enum LawStatus {
  PASSED = 'PASSED',
  STRUCTURAL = 'STRUCTURAL',
  FAILED = 'FAILED',
  UNDECIDABLE = 'UNDECIDABLE',
}

export interface LawExtraction {
  name: string;
  equation: string;
  source: string;
  tier: EvidenceTier;
}

export interface LawVerification {
  law_name: string;
  status: LawStatus;
  evidence: string;
  passed: boolean;
}

export interface FixedPointAnalysis {
  is_self_referential: boolean;
  fixed_point_description: string;
  is_valid: boolean;
  implications: string[];
}

export interface CategoricalReport {
  target: string;
  laws_extracted: LawExtraction[];
  law_verifications: LawVerification[];
  fixed_point: FixedPointAnalysis | null;
  summary: string;
}

export interface ToulminStructure {
  claim: string;
  grounds: string[];
  warrant: string;
  backing: string;
  qualifier: string;
  rebuttals: string[];
  tier: EvidenceTier;
}

export interface GroundingChain {
  steps: Array<[number, string, string]>; // [layer, node, edge_type]
  terminates_at_axiom: boolean;
}

export interface BootstrapAnalysis {
  is_self_describing: boolean;
  layer_described: number;
  layer_occupied: number;
  is_valid: boolean;
  explanation: string;
}

export interface EpistemicReport {
  target: string;
  layer: number; // 1-7
  toulmin: ToulminStructure;
  grounding: GroundingChain;
  bootstrap: BootstrapAnalysis | null;
  summary: string;
}

export interface Tension {
  thesis: string;
  antithesis: string;
  classification: ContradictionType;
  synthesis: string | null;
  is_resolved: boolean;
}

export interface DialecticalReport {
  target: string;
  tensions: Tension[];
  summary: string;
}

export interface OperadGrammar {
  primitives: string[];
  operations: string[];
  laws: string[];
}

export interface RegenerationTest {
  axioms_used: string[];
  structures_regenerated: string[];
  missing_elements: string[];
  passed: boolean;
}

export interface GenerativeReport {
  target: string;
  grammar: OperadGrammar;
  compression_ratio: number;
  regeneration: RegenerationTest;
  minimal_kernel: string[];
  summary: string;
}

export interface FullAnalysisReport {
  target: string;
  categorical: CategoricalReport;
  epistemic: EpistemicReport;
  dialectical: DialecticalReport;
  generative: GenerativeReport;
  synthesis: string;
}

// =============================================================================
// Hook
// =============================================================================

export interface UseAnalysisResult {
  categorical: CategoricalReport | null;
  epistemic: EpistemicReport | null;
  dialectical: DialecticalReport | null;
  generative: GenerativeReport | null;
  loading: boolean;
  error: Error | null;
  refresh: () => void;
}

/**
 * Fetch four-mode analysis for a node.
 *
 * @param nodeId - The node ID to analyze (null to skip)
 * @returns Analysis reports, loading state, error, and refresh function
 *
 * @example
 * ```tsx
 * function AnalysisView({ nodeId }: { nodeId: string }) {
 *   const { categorical, epistemic, loading } = useAnalysis(nodeId);
 *
 *   if (loading) return <Skeleton />;
 *
 *   return (
 *     <AnalysisQuadrant
 *       categorical={categorical}
 *       epistemic={epistemic}
 *       dialectical={dialectical}
 *       generative={generative}
 *     />
 *   );
 * }
 * ```
 */
export function useAnalysis(nodeId: string | null): UseAnalysisResult {
  const [categorical, setCategorical] = useState<CategoricalReport | null>(null);
  const [epistemic, setEpistemic] = useState<EpistemicReport | null>(null);
  const [dialectical, setDialectical] = useState<DialecticalReport | null>(null);
  const [generative, setGenerative] = useState<GenerativeReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchAnalysis = useCallback(async () => {
    if (!nodeId) {
      setCategorical(null);
      setEpistemic(null);
      setDialectical(null);
      setGenerative(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // TODO: Replace with actual API endpoint when backend is ready
      // For now, use mock data
      const mockData = generateMockAnalysis(nodeId);

      setCategorical(mockData.categorical);
      setEpistemic(mockData.epistemic);
      setDialectical(mockData.dialectical);
      setGenerative(mockData.generative);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
      setCategorical(null);
      setEpistemic(null);
      setDialectical(null);
      setGenerative(null);
    } finally {
      setLoading(false);
    }
  }, [nodeId]);

  // Fetch on mount and when nodeId changes
  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  return {
    categorical,
    epistemic,
    dialectical,
    generative,
    loading,
    error,
    refresh: fetchAnalysis,
  };
}

// =============================================================================
// Mock Data Generator (TODO: Remove when backend ready)
// =============================================================================

function generateMockAnalysis(nodeId: string): {
  categorical: CategoricalReport;
  epistemic: EpistemicReport;
  dialectical: DialecticalReport;
  generative: GenerativeReport;
} {
  return {
    categorical: {
      target: nodeId,
      laws_extracted: [
        {
          name: 'Identity',
          equation: 'Id >> f = f = f >> Id',
          source: 'spec/agents/operad.md §2.1',
          tier: EvidenceTier.CATEGORICAL,
        },
        {
          name: 'Associativity',
          equation: '(f >> g) >> h = f >> (g >> h)',
          source: 'spec/agents/operad.md §2.1',
          tier: EvidenceTier.CATEGORICAL,
        },
      ],
      law_verifications: [
        {
          law_name: 'Identity',
          status: LawStatus.PASSED,
          evidence: 'Verified by construction in PolyAgent',
          passed: true,
        },
        {
          law_name: 'Associativity',
          status: LawStatus.PASSED,
          evidence: 'Holds for all composition chains',
          passed: true,
        },
      ],
      fixed_point: null,
      summary: 'All composition laws hold. No violations detected.',
    },
    epistemic: {
      target: nodeId,
      layer: 4,
      toulmin: {
        claim: 'This spec is sound',
        grounds: ['Axioms A1, V2', 'Goal G5'],
        warrant: 'Grounded in tested principles',
        backing: 'Empirical validation',
        qualifier: 'definitely',
        rebuttals: [],
        tier: EvidenceTier.EMPIRICAL,
      },
      grounding: {
        steps: [
          [4, 'spec/protocols/witness.md', 'DERIVES_FROM'],
          [2, 'V2: Joy-inducing', 'GROUNDS_IN'],
          [1, 'A1: Tasteful > feature-complete', 'AXIOM'],
        ],
        terminates_at_axiom: true,
      },
      bootstrap: null,
      summary: 'Grounded at L4 (Specification). Terminates at axiom A1.',
    },
    dialectical: {
      target: nodeId,
      tensions: [
        {
          thesis: 'Maximize expressiveness',
          antithesis: 'Minimize complexity',
          classification: ContradictionType.PRODUCTIVE,
          synthesis: 'Use compositional primitives (high expressiveness, low complexity)',
          is_resolved: true,
        },
        {
          thesis: 'Support all use cases',
          antithesis: 'Keep API surface minimal',
          classification: ContradictionType.PRODUCTIVE,
          synthesis: 'Provide composable operations, not enumerated features',
          is_resolved: true,
        },
      ],
      summary: '2 productive tensions identified. Both resolved via composition.',
    },
    generative: {
      target: nodeId,
      grammar: {
        primitives: ['PolyAgent', 'parallel', 'sequential'],
        operations: ['compose', 'map', 'filter'],
        laws: ['identity', 'associativity', 'functoriality'],
      },
      compression_ratio: 0.67,
      regeneration: {
        axioms_used: ['A1: Composability', 'V2: Joy-inducing', 'G5: Teaching mode'],
        structures_regenerated: ['Operad', 'PolyAgent', 'Crown Jewels'],
        missing_elements: [],
        passed: true,
      },
      minimal_kernel: ['Composability', 'Joy', 'Teaching'],
      summary: 'Regenerable from 3 axioms. Compression ratio: 0.67 (good).',
    },
  };
}

export default useAnalysis;
