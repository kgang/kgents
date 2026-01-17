/**
 * Axiom Discovery API Client
 *
 * Frontend client for the Axiom Discovery Pipeline via AGENTESE.
 *
 * Endpoints:
 * - POST /agentese/self/axiom/discover - Discover axioms from decision history
 * - POST /agentese/self/axiom/validate - Validate a potential axiom
 * - GET /agentese/self/axiom/contradictions - Detect contradictions
 *
 * Philosophy:
 *   "Kent discovers his personal axioms. The system shows him:
 *    'You've made 147 decisions this month. Here are the 3 principles
 *     you never violated - your L0 axioms.' He didn't write them; he *discovered* them."
 *
 * @see services/zero_seed/axiom_discovery_pipeline.py
 * @see components/constitution/PersonalConstitutionBuilder.tsx
 */

import type {
  AxiomCandidate,
  AxiomDiscoveryResult,
  ContradictionPair,
  DiscoverAxiomsRequest,
  ValidateAxiomResponse,
  DiscoveryProgress,
} from '../components/constitution/types';
import { getContradictionSeverity } from '../components/constitution/types';

// =============================================================================
// API Configuration
// =============================================================================

const API_BASE = '/agentese';

/**
 * Helper to make AGENTESE POST requests.
 */
async function agentesePost<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}/${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`AGENTESE error: ${response.status} - ${error}`);
  }

  const envelope = await response.json();

  // Unwrap AGENTESE envelope
  if (envelope.error) {
    throw new Error(envelope.error);
  }

  return envelope.result;
}

/**
 * Helper to make AGENTESE GET requests.
 * Currently unused but kept for future endpoints.
 */
async function _agenteseGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}/${path}`, {
    method: 'GET',
    headers: {
      Accept: 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`AGENTESE error: ${response.status} - ${error}`);
  }

  const envelope = await response.json();

  // Unwrap AGENTESE envelope
  if (envelope.error) {
    throw new Error(envelope.error);
  }

  return envelope.result;
}

// =============================================================================
// API Functions
// =============================================================================

/**
 * Discover personal axioms from decision history.
 *
 * Runs the full axiom discovery pipeline:
 * 1. Surfaces decisions from past N days
 * 2. Extracts recurring patterns
 * 3. Computes Galois loss for each pattern
 * 4. Identifies fixed points (L < 0.05)
 * 5. Detects contradictions
 *
 * @param options - Discovery options
 * @returns Discovery result with candidates and contradictions
 */
export async function discoverAxioms(
  options: DiscoverAxiomsRequest = {}
): Promise<AxiomDiscoveryResult> {
  const { days = 30, maxCandidates = 10, minPatternOccurrences = 5 } = options;

  const rawResult = await agentesePost<{
    candidates: Array<{
      content: string;
      loss: number;
      stability: number;
      evidence: string[];
      source_pattern: string;
      confidence: number;
      frequency: number;
      first_seen: string;
      last_seen: string;
      is_axiom: boolean;
      stability_score: number;
    }>;
    total_decisions_analyzed: number;
    time_window_days: number;
    contradictions_detected: Array<{
      axiom_a: string;
      axiom_b: string;
      loss_a: number;
      loss_b: number;
      loss_combined: number;
      strength: number;
      type: string;
      synthesis_hint: string | null;
    }>;
    patterns_found: number;
    axioms_discovered: number;
    duration_ms: number;
    user_id: string | null;
    top_axioms: Array<{
      content: string;
      loss: number;
      stability: number;
      evidence: string[];
      source_pattern: string;
      confidence: number;
      frequency: number;
      first_seen: string;
      last_seen: string;
      is_axiom: boolean;
      stability_score: number;
    }>;
    has_contradictions: boolean;
  }>('self/axiom/discover', {
    days,
    max_candidates: maxCandidates,
    min_pattern_occurrences: minPatternOccurrences,
  });

  // Transform snake_case to camelCase
  return {
    candidates: rawResult.candidates.map(transformCandidate),
    totalDecisionsAnalyzed: rawResult.total_decisions_analyzed,
    timeWindowDays: rawResult.time_window_days,
    contradictionsDetected: rawResult.contradictions_detected.map(transformContradiction),
    patternsFound: rawResult.patterns_found,
    axiomsDiscovered: rawResult.axioms_discovered,
    durationMs: rawResult.duration_ms,
    userId: rawResult.user_id,
    topAxioms: rawResult.top_axioms.map(transformCandidate),
    hasContradictions: rawResult.has_contradictions,
  };
}

/**
 * Validate if user-provided content qualifies as an axiom.
 *
 * @param content - The potential axiom to validate
 * @returns Validation result with loss and stability
 */
export async function validateAxiom(content: string): Promise<ValidateAxiomResponse> {
  const rawResult = await agentesePost<{
    is_axiom: boolean;
    loss: number;
    stability: number;
    candidate: {
      content: string;
      loss: number;
      stability: number;
      evidence: string[];
      source_pattern: string;
      confidence: number;
      frequency: number;
      first_seen: string;
      last_seen: string;
      is_axiom: boolean;
      stability_score: number;
    };
  }>('self/axiom/validate', { content });

  return {
    isAxiom: rawResult.is_axiom,
    loss: rawResult.loss,
    stability: rawResult.stability,
    candidate: transformCandidate(rawResult.candidate),
  };
}

/**
 * Detect contradictions between a set of axiom contents.
 *
 * @param contents - Array of axiom contents to check for contradictions
 * @returns Array of detected contradiction pairs
 */
export async function detectContradictions(contents: string[]): Promise<ContradictionPair[]> {
  const rawResult = await agentesePost<
    Array<{
      axiom_a: string;
      axiom_b: string;
      loss_a: number;
      loss_b: number;
      loss_combined: number;
      strength: number;
      type: string;
      synthesis_hint: string | null;
    }>
  >('self/axiom/contradictions', { contents });

  return rawResult.map(transformContradiction);
}

// =============================================================================
// Transform Functions
// =============================================================================

/**
 * Transform a raw candidate from API to typed AxiomCandidate.
 */
function transformCandidate(raw: {
  content: string;
  loss: number;
  stability: number;
  evidence: string[];
  source_pattern: string;
  confidence: number;
  frequency: number;
  first_seen: string;
  last_seen: string;
  is_axiom: boolean;
  stability_score: number;
}): AxiomCandidate {
  return {
    content: raw.content,
    loss: raw.loss,
    stability: raw.stability,
    evidence: raw.evidence,
    sourcePattern: raw.source_pattern,
    confidence: raw.confidence,
    frequency: raw.frequency,
    firstSeen: raw.first_seen,
    lastSeen: raw.last_seen,
    isAxiom: raw.is_axiom,
    stabilityScore: raw.stability_score,
  };
}

/**
 * Transform a raw contradiction from API to typed ContradictionPair.
 */
function transformContradiction(raw: {
  axiom_a: string;
  axiom_b: string;
  loss_a: number;
  loss_b: number;
  loss_combined: number;
  strength: number;
  type: string;
  synthesis_hint: string | null;
}): ContradictionPair {
  return {
    axiomA: raw.axiom_a,
    axiomB: raw.axiom_b,
    lossA: raw.loss_a,
    lossB: raw.loss_b,
    lossCombined: raw.loss_combined,
    strength: raw.strength,
    type: getContradictionSeverity(raw.strength),
    synthesisHint: raw.synthesis_hint,
  };
}

// =============================================================================
// Streaming Discovery (for progress updates)
// =============================================================================

/**
 * Progress callback type for streaming discovery.
 */
export type ProgressCallback = (progress: DiscoveryProgress) => void;

/**
 * Discover axioms with streaming progress updates.
 *
 * Uses Server-Sent Events to provide real-time progress during discovery.
 *
 * @param options - Discovery options
 * @param onProgress - Callback for progress updates
 * @returns Final discovery result
 */
export async function discoverAxiomsWithProgress(
  options: DiscoverAxiomsRequest = {},
  onProgress: ProgressCallback
): Promise<AxiomDiscoveryResult> {
  const { days = 30, maxCandidates = 10, minPatternOccurrences = 5 } = options;

  return new Promise((resolve, reject) => {
    // Build query params
    const params = new URLSearchParams({
      days: String(days),
      max_candidates: String(maxCandidates),
      min_pattern_occurrences: String(minPatternOccurrences),
    });

    const eventSource = new EventSource(`${API_BASE}/self/axiom/discover/stream?${params}`);

    let result: AxiomDiscoveryResult | null = null;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'progress') {
          onProgress({
            stage: data.stage,
            message: data.message,
            percent: data.percent,
            decisionsAnalyzed: data.decisions_analyzed || 0,
            patternsFound: data.patterns_found || 0,
          });
        } else if (data.type === 'complete') {
          result = {
            candidates: (data.result.candidates || []).map(transformCandidate),
            totalDecisionsAnalyzed: data.result.total_decisions_analyzed,
            timeWindowDays: data.result.time_window_days,
            contradictionsDetected: (data.result.contradictions_detected || []).map(
              transformContradiction
            ),
            patternsFound: data.result.patterns_found,
            axiomsDiscovered: data.result.axioms_discovered,
            durationMs: data.result.duration_ms,
            userId: data.result.user_id,
            topAxioms: (data.result.top_axioms || []).map(transformCandidate),
            hasContradictions: data.result.has_contradictions,
          };
          eventSource.close();
          resolve(result);
        } else if (data.type === 'error') {
          eventSource.close();
          reject(new Error(data.message));
        }
      } catch (e) {
        console.error('Failed to parse SSE data:', e);
      }
    };

    eventSource.onerror = (_error) => {
      eventSource.close();
      reject(new Error('Discovery stream failed'));
    };
  });
}

// =============================================================================
// Mock Data (for development)
// =============================================================================

/**
 * Generate mock discovery result for development/testing.
 */
export function getMockDiscoveryResult(): AxiomDiscoveryResult {
  const mockCandidates: AxiomCandidate[] = [
    {
      content: 'Prioritize depth over breadth',
      loss: 0.03,
      stability: 0.02,
      evidence: ['mark_001', 'mark_042', 'mark_089', 'mark_123'],
      sourcePattern: 'depth over breadth',
      confidence: 0.92,
      frequency: 23,
      firstSeen: '2024-01-15T10:30:00Z',
      lastSeen: '2024-02-10T14:20:00Z',
      isAxiom: true,
      stabilityScore: 0.95,
    },
    {
      content: 'Taste over features',
      loss: 0.04,
      stability: 0.03,
      evidence: ['mark_007', 'mark_055', 'mark_098'],
      sourcePattern: 'tasteful > feature-complete',
      confidence: 0.88,
      frequency: 18,
      firstSeen: '2024-01-20T09:15:00Z',
      lastSeen: '2024-02-08T16:45:00Z',
      isAxiom: true,
      stabilityScore: 0.92,
    },
    {
      content: 'Evidence over intuition',
      loss: 0.08,
      stability: 0.05,
      evidence: ['mark_012', 'mark_034', 'mark_067', 'mark_101', 'mark_145'],
      sourcePattern: 'evidence-driven',
      confidence: 0.78,
      frequency: 31,
      firstSeen: '2024-01-10T11:00:00Z',
      lastSeen: '2024-02-12T10:30:00Z',
      isAxiom: false,
      stabilityScore: 0.85,
    },
    {
      content: 'Joy in the process',
      loss: 0.15,
      stability: 0.08,
      evidence: ['mark_023', 'mark_056'],
      sourcePattern: 'joy-inducing',
      confidence: 0.65,
      frequency: 12,
      firstSeen: '2024-01-25T13:30:00Z',
      lastSeen: '2024-02-05T09:00:00Z',
      isAxiom: false,
      stabilityScore: 0.72,
    },
    {
      content: 'Composability enables evolution',
      loss: 0.22,
      stability: 0.12,
      evidence: ['mark_045', 'mark_078', 'mark_112'],
      sourcePattern: 'composable agents',
      confidence: 0.55,
      frequency: 9,
      firstSeen: '2024-01-18T16:00:00Z',
      lastSeen: '2024-02-01T11:15:00Z',
      isAxiom: false,
      stabilityScore: 0.62,
    },
  ];

  const mockContradictions: ContradictionPair[] = [
    {
      axiomA: 'Prioritize depth over breadth',
      axiomB: 'Composability enables evolution',
      lossA: 0.03,
      lossB: 0.22,
      lossCombined: 0.42,
      strength: 0.17,
      type: 'moderate',
      synthesisHint:
        'Consider: "Deep composability" - compose deeply understood components rather than broad shallow ones.',
    },
  ];

  return {
    candidates: mockCandidates,
    totalDecisionsAnalyzed: 147,
    timeWindowDays: 30,
    contradictionsDetected: mockContradictions,
    patternsFound: 42,
    axiomsDiscovered: 2,
    durationMs: 1234,
    userId: null,
    topAxioms: mockCandidates.filter((c) => c.isAxiom),
    hasContradictions: true,
  };
}
