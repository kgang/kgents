/**
 * useDirector — Document Director capabilities for any surface
 *
 * Provides state management and actions for interacting with the Document Director system.
 * Supports both document-specific operations (when path provided) and global metrics.
 *
 * Philosophy:
 *   "Upload → Analyze → Generate → Execute → Capture → Verify"
 */

import { useCallback, useEffect, useState } from 'react';
import {
  analyzeDocument,
  captureExecution,
  generatePrompt,
  getDocument,
  getMetrics,
  type AnalysisCrystal,
  type AnalyzeResponse,
  type CaptureRequest,
  type CaptureResponse,
  type DocumentDetail,
  type DocumentStatus,
  type EvidenceMark,
  type ExecutionPrompt,
  type MetricsSummary,
} from '../api/director';

// =============================================================================
// Types
// =============================================================================

export interface UseDirectorOptions {
  /** Path to track a specific document */
  path?: string;
  /** Auto-fetch document status when path changes (default: true) */
  autoFetch?: boolean;
}

export interface UseDirectorResult {
  // Document-specific state (when path provided)
  status: DocumentStatus | null;
  analysis: AnalysisCrystal | null;
  evidenceMarks: EvidenceMark[];
  uploadedAt: string | null;
  analyzedAt: string | null;

  // Global metrics
  metrics: MetricsSummary | null;

  // Actions
  analyze: (path: string, force?: boolean) => Promise<AnalyzeResponse>;
  generatePrompt: (path: string) => Promise<ExecutionPrompt>;
  capture: (request: CaptureRequest) => Promise<CaptureResponse>;
  refresh: () => Promise<void>;
  refreshMetrics: () => Promise<void>;

  // State
  loading: boolean;
  metricsLoading: boolean;
  error: Error | null;
}

// =============================================================================
// Hook
// =============================================================================

export function useDirector(options: UseDirectorOptions = {}): UseDirectorResult {
  const { path, autoFetch = true } = options;

  // Document-specific state
  const [status, setStatus] = useState<DocumentStatus | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisCrystal | null>(null);
  const [evidenceMarks, setEvidenceMarks] = useState<EvidenceMark[]>([]);
  const [uploadedAt, setUploadedAt] = useState<string | null>(null);
  const [analyzedAt, setAnalyzedAt] = useState<string | null>(null);

  // Global metrics
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);

  // Loading and error state
  const [loading, setLoading] = useState(false);
  const [metricsLoading, setMetricsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  /**
   * Fetch document detail when path is provided.
   */
  const fetchDocument = useCallback(async (documentPath: string) => {
    setLoading(true);
    setError(null);

    try {
      const detail: DocumentDetail = await getDocument(documentPath);

      setStatus(detail.status);
      setAnalysis(detail.analysis);
      setEvidenceMarks(detail.evidence_marks || []);
      setUploadedAt(detail.uploaded_at);
      setAnalyzedAt(detail.analyzed_at);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      console.error('Failed to fetch document:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch global metrics.
   */
  const fetchMetrics = useCallback(async () => {
    setMetricsLoading(true);

    try {
      const metricsData = await getMetrics();
      setMetrics(metricsData);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      console.error('Failed to fetch metrics:', error);
      // Don't set error state for metrics failures (non-critical)
    } finally {
      setMetricsLoading(false);
    }
  }, []);

  /**
   * Analyze a document (trigger or re-trigger analysis).
   */
  const analyze = useCallback(
    async (analyzePath: string, force = false): Promise<AnalyzeResponse> => {
      setLoading(true);
      setError(null);

      try {
        const response = await analyzeDocument(analyzePath, force);

        // Update local state if analyzing the current document
        if (path === analyzePath) {
          setStatus(response.analysis.status as DocumentStatus);
          setAnalysis(response.analysis);
          setAnalyzedAt(response.analysis.analyzed_at);
        }

        return response;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [path]
  );

  /**
   * Generate execution prompt for a document.
   */
  const generatePromptAction = useCallback(
    async (promptPath: string): Promise<ExecutionPrompt> => {
      setLoading(true);
      setError(null);

      try {
        const prompt = await generatePrompt(promptPath);
        return prompt;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  /**
   * Capture execution results.
   */
  const capture = useCallback(
    async (request: CaptureRequest): Promise<CaptureResponse> => {
      setLoading(true);
      setError(null);

      try {
        const response = await captureExecution(request);

        // Refresh document state if capturing for current document
        if (path === request.spec_path) {
          await fetchDocument(request.spec_path);
        }

        return response;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [path, fetchDocument]
  );

  /**
   * Refresh document state.
   */
  const refresh = useCallback(async () => {
    if (path) {
      await fetchDocument(path);
    }
  }, [path, fetchDocument]);

  /**
   * Refresh metrics state.
   */
  const refreshMetrics = useCallback(async () => {
    await fetchMetrics();
  }, [fetchMetrics]);

  /**
   * Auto-fetch document when path changes.
   */
  useEffect(() => {
    if (path && autoFetch) {
      fetchDocument(path);
    }
  }, [path, autoFetch, fetchDocument]);

  /**
   * Fetch metrics on mount.
   */
  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return {
    // Document-specific state
    status,
    analysis,
    evidenceMarks,
    uploadedAt,
    analyzedAt,

    // Global metrics
    metrics,

    // Actions
    analyze,
    generatePrompt: generatePromptAction,
    capture,
    refresh,
    refreshMetrics,

    // State
    loading,
    metricsLoading,
    error,
  };
}
