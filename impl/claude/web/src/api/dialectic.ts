/**
 * Dialectic API Client
 *
 * API client for the Dialectical Fusion system - Kent + Claude synthesis.
 *
 * "The goal is not Kent's decisions or AI's decisions.
 *  The goal is fused decisions better than either alone."
 *
 * AGENTESE Paths:
 * - self.dialectic.manifest   - Current dialectic state
 * - self.dialectic.thesis     - Propose Kent's position
 * - self.dialectic.antithesis - Generate Claude's counter-position
 * - self.dialectic.sublate    - Synthesize fusion (Aufhebung)
 * - self.dialectic.history    - View fusion history
 * - concept.fusion.manifest   - Fusion ontology
 * - concept.fusion.cocone     - The categorical cocone structure
 *
 * @see docs/theory/17-dialectic.md
 */

import { apiClient, unwrapAgentese, type AgenteseResponse } from './client';

// =============================================================================
// Types
// =============================================================================

/**
 * The holder of a position in dialectic.
 */
export type PositionHolder = 'kent' | 'claude';

/**
 * Possible fusion results.
 */
export type FusionResult = 'consensus' | 'synthesis' | 'kent' | 'claude' | 'deferred' | 'veto';

/**
 * A position in the dialectic (thesis or antithesis).
 */
export interface Position {
  content: string;
  reasoning: string;
  holder: PositionHolder;
  confidence?: number;
  evidence?: string[];
}

/**
 * The synthesis result from sublation.
 */
export interface Synthesis {
  content: string;
  reasoning: string;
  preservedFromKent: string;
  preservedFromClaude: string;
  transcends: string;
}

/**
 * A completed fusion.
 */
export interface Fusion {
  id: string;
  topic: string;
  thesis: Position;
  antithesis: Position;
  synthesis: Synthesis | null;
  result: FusionResult;
  reasoning: string;
  trustDelta: number;
  markId: string | null;
  createdAt: string;
}

/**
 * Dialectic manifest response.
 */
export interface DialecticManifest {
  totalFusions: number;
  recentTopic: string | null;
  trustTrajectory: string;
  cumulativeTrustDelta: number;
  fusionCounts: Record<FusionResult, number>;
}

/**
 * Constitution article.
 */
export interface ConstitutionArticle {
  number: string;
  name: string;
  description: string;
}

/**
 * Fusion ontology (the conceptual framework).
 */
export interface FusionOntology {
  constitutionArticles: ConstitutionArticle[];
  fusionResults: Array<{
    name: string;
    value: FusionResult;
    description: string;
  }>;
  trustDeltas: Record<FusionResult, number>;
  principleWeights: Record<string, number>;
}

/**
 * The categorical cocone structure.
 */
export interface CoconeStructure {
  description: string;
  formula: string;
  components: {
    apex: string;
    legs: string;
    universality: string;
  };
  philosophy: string;
}

/**
 * Request to propose a thesis (Kent's position).
 */
export interface ThesisRequest {
  topic: string;
  content: string;
  reasoning: string;
  confidence?: number;
  evidence?: string[];
}

/**
 * Request to propose antithesis (Claude's counter-position).
 */
export interface AntithesisRequest {
  topic: string;
  thesisContent: string;
  thesisReasoning: string;
  content: string;
  reasoning: string;
  confidence?: number;
  evidence?: string[];
}

/**
 * Request to synthesize (sublate) thesis and antithesis.
 */
export interface SublateRequest {
  topic: string;
  kentView: string;
  kentReasoning: string;
  claudeView: string;
  claudeReasoning: string;
}

/**
 * Response from sublation.
 */
export interface SublateResponse {
  fusionId: string;
  topic: string;
  result: FusionResult;
  reasoning: string;
  synthesis: Synthesis | null;
  trustDelta: number;
  markId: string | null;
}

/**
 * Fusion history response.
 */
export interface HistoryResponse {
  fusions: Fusion[];
  count: number;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Get the current dialectic status.
 *
 * @example
 * const manifest = await getDialecticManifest();
 * console.log(`Total fusions: ${manifest.totalFusions}`);
 */
export async function getDialecticManifest(): Promise<DialecticManifest> {
  const { data } = await apiClient.get<
    AgenteseResponse<{
      total_fusions: number;
      recent_topic: string | null;
      trust_trajectory: string;
      cumulative_trust_delta: number;
      fusion_counts: Record<string, number>;
    }>
  >('/agentese/self/dialectic/manifest');

  const result = unwrapAgentese({ data });

  return {
    totalFusions: result.total_fusions,
    recentTopic: result.recent_topic,
    trustTrajectory: result.trust_trajectory,
    cumulativeTrustDelta: result.cumulative_trust_delta,
    fusionCounts: result.fusion_counts as Record<FusionResult, number>,
  };
}

/**
 * Propose a thesis (Kent's position).
 *
 * @example
 * const thesis = await proposeThesis({
 *   topic: "Database choice",
 *   content: "Use PostgreSQL",
 *   reasoning: "Familiar, reliable, ACID-compliant",
 * });
 */
export async function proposeThesis(request: ThesisRequest): Promise<Position> {
  const { data } = await apiClient.post<
    AgenteseResponse<{
      topic: string;
      position: {
        content: string;
        reasoning: string;
        holder: string;
        confidence?: number;
        evidence?: string[];
      };
      holder: string;
    }>
  >('/agentese/self/dialectic/thesis', {
    topic: request.topic,
    content: request.content,
    reasoning: request.reasoning,
    confidence: request.confidence,
    evidence: request.evidence,
  });

  const result = unwrapAgentese({ data });

  return {
    content: result.position.content,
    reasoning: result.position.reasoning,
    holder: result.position.holder as PositionHolder,
    confidence: result.position.confidence,
    evidence: result.position.evidence,
  };
}

/**
 * Propose an antithesis (Claude's counter-position).
 *
 * @example
 * const antithesis = await proposeAntithesis({
 *   topic: "Database choice",
 *   thesisContent: "Use PostgreSQL",
 *   thesisReasoning: "Familiar, reliable",
 *   content: "Consider SQLite for simplicity",
 *   reasoning: "Simpler deployment, good enough for our scale",
 * });
 */
export async function proposeAntithesis(request: AntithesisRequest): Promise<{
  thesis: Position;
  antithesis: Position;
}> {
  const { data } = await apiClient.post<
    AgenteseResponse<{
      topic: string;
      thesis: {
        content: string;
        reasoning: string;
        holder: string;
      };
      antithesis: {
        content: string;
        reasoning: string;
        holder: string;
        confidence?: number;
        evidence?: string[];
      };
    }>
  >('/agentese/self/dialectic/antithesis', {
    topic: request.topic,
    thesis_content: request.thesisContent,
    thesis_reasoning: request.thesisReasoning,
    content: request.content,
    reasoning: request.reasoning,
    confidence: request.confidence,
    evidence: request.evidence,
  });

  const result = unwrapAgentese({ data });

  return {
    thesis: {
      content: result.thesis.content,
      reasoning: result.thesis.reasoning,
      holder: result.thesis.holder as PositionHolder,
    },
    antithesis: {
      content: result.antithesis.content,
      reasoning: result.antithesis.reasoning,
      holder: result.antithesis.holder as PositionHolder,
      confidence: result.antithesis.confidence,
      evidence: result.antithesis.evidence,
    },
  };
}

/**
 * Synthesize (sublate) thesis and antithesis into a fusion.
 *
 * This is the core dialectical operation - Aufhebung.
 *
 * @example
 * const synthesis = await sublate({
 *   topic: "Framework choice",
 *   kentView: "Use existing framework",
 *   kentReasoning: "Scale, resources, production-ready",
 *   claudeView: "Build novel system",
 *   claudeReasoning: "Joy-inducing, novel contribution",
 * });
 */
export async function sublate(request: SublateRequest): Promise<SublateResponse> {
  const { data } = await apiClient.post<
    AgenteseResponse<{
      fusion_id: string;
      topic: string;
      result: string;
      reasoning: string;
      synthesis: {
        content: string;
        reasoning: string;
        preserved_from_kent: string;
        preserved_from_claude: string;
        transcends: string;
      } | null;
      trust_delta: number;
      mark_id: string | null;
    }>
  >('/agentese/self/dialectic/sublate', {
    topic: request.topic,
    kent_view: request.kentView,
    kent_reasoning: request.kentReasoning,
    claude_view: request.claudeView,
    claude_reasoning: request.claudeReasoning,
  });

  const result = unwrapAgentese({ data });

  return {
    fusionId: result.fusion_id,
    topic: result.topic,
    result: result.result as FusionResult,
    reasoning: result.reasoning,
    synthesis: result.synthesis
      ? {
          content: result.synthesis.content,
          reasoning: result.synthesis.reasoning,
          preservedFromKent: result.synthesis.preserved_from_kent,
          preservedFromClaude: result.synthesis.preserved_from_claude,
          transcends: result.synthesis.transcends,
        }
      : null,
    trustDelta: result.trust_delta,
    markId: result.mark_id,
  };
}

/**
 * Get fusion history.
 *
 * @example
 * const history = await getFusionHistory({ topic: 'architecture', limit: 5 });
 */
export async function getFusionHistory(options?: {
  topic?: string;
  limit?: number;
}): Promise<HistoryResponse> {
  const params = new URLSearchParams();

  if (options?.topic) {
    params.set('topic', options.topic);
  }
  if (options?.limit) {
    params.set('limit', String(options.limit));
  }

  const query = params.toString();
  const url = `/agentese/self/dialectic/history${query ? `?${query}` : ''}`;

  const { data } = await apiClient.get<
    AgenteseResponse<{
      fusions: Array<{
        id: string;
        topic: string;
        thesis: { content: string; reasoning: string; holder: string };
        antithesis: { content: string; reasoning: string; holder: string };
        synthesis: {
          content: string;
          reasoning: string;
          preserved_from_kent: string;
          preserved_from_claude: string;
          transcends: string;
        } | null;
        result: string;
        reasoning: string;
        trust_delta: number;
        mark_id: string | null;
        created_at: string;
      }>;
      count: number;
    }>
  >(url);

  const result = unwrapAgentese({ data });

  return {
    fusions: result.fusions.map((f) => ({
      id: f.id,
      topic: f.topic,
      thesis: {
        content: f.thesis.content,
        reasoning: f.thesis.reasoning,
        holder: f.thesis.holder as PositionHolder,
      },
      antithesis: {
        content: f.antithesis.content,
        reasoning: f.antithesis.reasoning,
        holder: f.antithesis.holder as PositionHolder,
      },
      synthesis: f.synthesis
        ? {
            content: f.synthesis.content,
            reasoning: f.synthesis.reasoning,
            preservedFromKent: f.synthesis.preserved_from_kent,
            preservedFromClaude: f.synthesis.preserved_from_claude,
            transcends: f.synthesis.transcends,
          }
        : null,
      result: f.result as FusionResult,
      reasoning: f.reasoning,
      trustDelta: f.trust_delta,
      markId: f.mark_id,
      createdAt: f.created_at,
    })),
    count: result.count,
  };
}

/**
 * Get the fusion ontology (conceptual framework).
 *
 * @example
 * const ontology = await getFusionOntology();
 * console.log(ontology.constitutionArticles);
 */
export async function getFusionOntology(): Promise<FusionOntology> {
  const { data } = await apiClient.get<
    AgenteseResponse<{
      constitution_articles: Array<{
        number: string;
        name: string;
        description: string;
      }>;
      fusion_results: Array<{
        name: string;
        value: string;
        description: string;
      }>;
      trust_deltas: Record<string, number>;
      principle_weights: Record<string, number>;
    }>
  >('/agentese/concept/fusion/manifest');

  const result = unwrapAgentese({ data });

  return {
    constitutionArticles: result.constitution_articles,
    fusionResults: result.fusion_results.map((r) => ({
      name: r.name,
      value: r.value as FusionResult,
      description: r.description,
    })),
    trustDeltas: result.trust_deltas as Record<FusionResult, number>,
    principleWeights: result.principle_weights,
  };
}

/**
 * Get the categorical cocone structure.
 *
 * The cocone represents what synthesis achieves mathematically:
 * - Apex: The synthesis (tip of the cocone)
 * - Legs: Morphisms from thesis/antithesis to synthesis
 * - Universality: Any other synthesis factors through this one
 *
 * @example
 * const cocone = await getCoconeStructure();
 * console.log(cocone.philosophy);
 */
export async function getCoconeStructure(): Promise<CoconeStructure> {
  const { data } = await apiClient.get<
    AgenteseResponse<{
      description: string;
      formula: string;
      components: {
        apex: string;
        legs: string;
        universality: string;
      };
      philosophy: string;
    }>
  >('/agentese/concept/fusion/cocone');

  return unwrapAgentese({ data });
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Get a human-readable label for a fusion result.
 */
export function getFusionResultLabel(result: FusionResult): string {
  const labels: Record<FusionResult, string> = {
    consensus: 'Consensus',
    synthesis: 'Synthesis (Aufhebung)',
    kent: 'Kent Prevails',
    claude: 'Claude Prevails',
    deferred: 'Deferred',
    veto: 'Veto (Disgust)',
  };
  return labels[result];
}

/**
 * Get the icon/symbol for a fusion result.
 */
export function getFusionResultIcon(result: FusionResult): string {
  const icons: Record<FusionResult, string> = {
    consensus: '=',
    synthesis: '+',
    kent: 'K',
    claude: 'C',
    deferred: '?',
    veto: 'X',
  };
  return icons[result];
}

/**
 * Get the CSS class for a fusion result.
 */
export function getFusionResultClass(result: FusionResult): string {
  const classes: Record<FusionResult, string> = {
    consensus: 'fusion-result--consensus',
    synthesis: 'fusion-result--synthesis',
    kent: 'fusion-result--kent',
    claude: 'fusion-result--claude',
    deferred: 'fusion-result--deferred',
    veto: 'fusion-result--veto',
  };
  return classes[result];
}

/**
 * Format trust delta for display.
 */
export function formatTrustDelta(delta: number): string {
  if (delta > 0) return `+${delta.toFixed(2)}`;
  if (delta < 0) return delta.toFixed(2);
  return '0.00';
}

// =============================================================================
// Exports
// =============================================================================

export default {
  getDialecticManifest,
  proposeThesis,
  proposeAntithesis,
  sublate,
  getFusionHistory,
  getFusionOntology,
  getCoconeStructure,
  getFusionResultLabel,
  getFusionResultIcon,
  getFusionResultClass,
  formatTrustDelta,
};
