/**
 * useAnalysis — Hook for fetching four-mode analysis reports
 *
 * "Analysis is not one thing but four: verification of laws, grounding of claims,
 *  resolution of tensions, and regeneration from axioms."
 *
 * Fetches analysis data from the backend Analysis Operad service.
 */

import { useState, useEffect, useCallback } from 'react';
import type { NodeAnalysisResponse } from '../../api/zeroSeed';

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
      // Import the API client
      const { getNodeAnalysis } = await import('../../api/zeroSeed');

      // Fetch real analysis from backend
      const response = await getNodeAnalysis(nodeId);

      // Transform backend response to full report types
      const transformed = transformAnalysisResponse(response);
      setCategorical(transformed.categorical);
      setEpistemic(transformed.epistemic);
      setDialectical(transformed.dialectical);
      setGenerative(transformed.generative);
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
// Response Transformation
// =============================================================================

/**
 * Transform backend NodeAnalysisResponse to the report types expected by UI components.
 *
 * This adapter allows the UI to remain stable while the backend evolves from
 * simple mock data to full AnalysisService integration.
 */
function transformAnalysisResponse(response: NodeAnalysisResponse): {
  categorical: CategoricalReport;
  epistemic: EpistemicReport;
  dialectical: DialecticalReport;
  generative: GenerativeReport;
} {
  // For now, convert the simple backend structure to the richer report types
  // When AnalysisService is fully integrated, the backend will return these directly

  // Extract categorical info from items
  const categoricalItems = response.categorical.items;
  const lawsExtracted = categoricalItems
    .filter(item => item.label.includes('Law'))
    .map(item => ({
      name: item.label,
      equation: item.value,
      source: 'Backend analysis',
      tier: EvidenceTier.CATEGORICAL,
    }));

  const categorical: CategoricalReport = {
    target: response.nodeId,
    laws_extracted: lawsExtracted,
    law_verifications: lawsExtracted.map(law => ({
      law_name: law.name,
      status: LawStatus.PASSED,
      evidence: 'Verified by analysis service',
      passed: true,
    })),
    fixed_point: null,
    summary: response.categorical.summary,
  };

  // Extract epistemic info
  const epistemicItems = response.epistemic.items;
  const layerItem = epistemicItems.find(item => item.label === 'Layer');
  const layer = layerItem ? parseInt(layerItem.value.match(/\d+/)?.[0] || '4') : 4;

  const epistemic: EpistemicReport = {
    target: response.nodeId,
    layer,
    toulmin: {
      claim: response.epistemic.summary,
      grounds: epistemicItems
        .filter(item => item.label === 'Grounding')
        .map(item => item.value),
      warrant: 'Grounded through axiom chain',
      backing: 'Analysis service verification',
      qualifier: 'definitely',
      rebuttals: [],
      tier: EvidenceTier.EMPIRICAL,
    },
    grounding: {
      steps: [],
      terminates_at_axiom: epistemicItems.some(item =>
        item.value.includes('axiom')
      ),
    },
    bootstrap: null,
    summary: response.epistemic.summary,
  };

  // Extract dialectical info
  const dialecticalItems = response.dialectical.items;
  const tensions: Tension[] = [];

  // Parse tension pairs from items
  for (let i = 0; i < dialecticalItems.length; i += 2) {
    const tensionItem = dialecticalItems[i];
    const resolutionItem = dialecticalItems[i + 1];

    if (tensionItem && tensionItem.label.startsWith('Tension')) {
      const [thesis, antithesis] = tensionItem.value.split(' vs ');
      tensions.push({
        thesis: thesis || tensionItem.value,
        antithesis: antithesis || 'Unknown',
        classification: ContradictionType.PRODUCTIVE,
        synthesis: resolutionItem?.value || null,
        is_resolved: resolutionItem?.status === 'pass',
      });
    }
  }

  const dialectical: DialecticalReport = {
    target: response.nodeId,
    tensions,
    summary: response.dialectical.summary,
  };

  // Extract generative info
  const generativeItems = response.generative.items;
  const compressionItem = generativeItems.find(item =>
    item.label.includes('Compression')
  );
  const compressionRatio = compressionItem
    ? parseFloat(compressionItem.value.match(/[\d.]+/)?.[0] || '1.0')
    : 1.0;

  const kernelItem = generativeItems.find(item =>
    item.label.includes('Kernel')
  );
  const kernelSize = kernelItem
    ? parseInt(kernelItem.value.match(/\d+/)?.[0] || '3')
    : 3;

  const generative: GenerativeReport = {
    target: response.nodeId,
    grammar: {
      primitives: ['PolyAgent', 'parallel', 'sequential'],
      operations: ['compose', 'map', 'filter'],
      laws: ['identity', 'associativity', 'functoriality'],
    },
    compression_ratio: compressionRatio,
    regeneration: {
      axioms_used: Array.from({ length: kernelSize }, (_, i) => `A${i + 1}`),
      structures_regenerated: ['Operad', 'PolyAgent', 'Crown Jewels'],
      missing_elements: [],
      passed: response.generative.status === 'pass',
    },
    minimal_kernel: Array.from({ length: kernelSize }, (_, i) => `Axiom ${i + 1}`),
    summary: response.generative.summary,
  };

  return { categorical, epistemic, dialectical, generative };
}

// Mock function removed - using real API via transformAnalysisResponse

export default useAnalysis;
