/**
 * Analysis Components
 *
 * Four-mode analysis visualization for the Analysis Operad.
 *
 * Export Structure:
 * - AnalysisQuadrant: Main 2x2 grid component
 * - Individual panels: CategoricalPanel, EpistemicPanel, etc.
 * - Hook: useAnalysis
 * - Types: All analysis report types
 */

export { AnalysisQuadrant } from './AnalysisQuadrant';
export { CategoricalPanel } from './CategoricalPanel';
export { EpistemicPanel } from './EpistemicPanel';
export { DialecticalPanel } from './DialecticalPanel';
export { GenerativePanel } from './GenerativePanel';

export { useAnalysis } from './useAnalysis';
export type {
  CategoricalReport,
  EpistemicReport,
  DialecticalReport,
  GenerativeReport,
  FullAnalysisReport,
  LawExtraction,
  LawVerification,
  FixedPointAnalysis,
  ToulminStructure,
  GroundingChain,
  BootstrapAnalysis,
  Tension,
  OperadGrammar,
  RegenerationTest,
  UseAnalysisResult,
  ContradictionType,
  EvidenceTier,
  LawStatus,
} from './useAnalysis';
