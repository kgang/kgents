/**
 * useVoiceGate - Hook for Anti-Sausage voice checking.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * Provides:
 * - Real-time text checking against voice rules
 * - Anti-Sausage score calculation
 * - Violation and anchor tracking
 *
 * @example
 * const { score, violations, anchors } = useVoiceGate(text);
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface VoiceViolation {
  match: string;
  category: string;
  action: string;
  reason: string;
  suggestion?: string;
  context?: string;
}

export interface VoiceCheckResult {
  passed: boolean;
  blocking_count: number;
  warning_count: number;
  anchors_referenced: string[];
  violations: VoiceViolation[];
  warnings: VoiceViolation[];
  checked_at: string;
}

export interface VoiceReportResult {
  text_length: number;
  passed: boolean;
  summary: {
    blocking: number;
    warnings: number;
    anchors: number;
  };
  violations: VoiceViolation[];
  anchors_found: string[];
  anti_sausage_score: number;
}

export interface UseVoiceGateOptions {
  /** Enable checking (default: true) */
  enabled?: boolean;
  /** Debounce delay in ms (default: 300) */
  debounceMs?: number;
  /** Use strict mode (default: false) */
  strict?: boolean;
}

export interface UseVoiceGateReturn {
  /** Check result */
  result: VoiceCheckResult | null;
  /** Report with score */
  report: VoiceReportResult | null;
  /** Anti-Sausage score (0-1) */
  score: number;
  /** Whether text passed the check */
  passed: boolean;
  /** Blocking violations */
  violations: VoiceViolation[];
  /** Warning violations */
  warnings: VoiceViolation[];
  /** Anchors referenced in text */
  anchors: string[];
  /** Loading state */
  isChecking: boolean;
  /** Error message */
  error: string | null;
  /** Manually trigger check */
  check: (text: string) => Promise<void>;
  /** Get detailed report */
  getReport: (text: string) => Promise<VoiceReportResult | null>;
}

// =============================================================================
// Constants
// =============================================================================

const API_BASE = import.meta.env.VITE_API_URL || '';

// =============================================================================
// Hook Implementation
// =============================================================================

export function useVoiceGate(text?: string, options: UseVoiceGateOptions = {}): UseVoiceGateReturn {
  const { enabled = true, debounceMs = 300, strict = false } = options;

  // State
  const [result, setResult] = useState<VoiceCheckResult | null>(null);
  const [report, setReport] = useState<VoiceReportResult | null>(null);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs
  const debounceRef = useRef<number | null>(null);
  const mountedRef = useRef(true);

  // Derived state
  const score = report?.anti_sausage_score ?? 1.0;
  const passed = result?.passed ?? true;
  const violations = result?.violations ?? [];
  const warnings = result?.warnings ?? [];
  const anchors = result?.anchors_referenced ?? [];

  // ==========================================================================
  // Check Function
  // ==========================================================================

  const check = useCallback(
    async (textToCheck: string): Promise<void> => {
      if (!textToCheck.trim()) {
        setResult(null);
        setReport(null);
        return;
      }

      setIsChecking(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE}/agentese/self/voice/gate/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: textToCheck, strict }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        if (mountedRef.current && data.result) {
          setResult(data.result as VoiceCheckResult);
        }
      } catch (e) {
        const message = e instanceof Error ? e.message : 'Check failed';
        if (mountedRef.current) {
          setError(message);
        }
        console.error('[useVoiceGate] Check error:', e);
      } finally {
        if (mountedRef.current) {
          setIsChecking(false);
        }
      }
    },
    [strict]
  );

  // ==========================================================================
  // Report Function
  // ==========================================================================

  const getReport = useCallback(async (textToReport: string): Promise<VoiceReportResult | null> => {
    if (!textToReport.trim()) {
      return null;
    }

    setIsChecking(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/agentese/self/voice/gate/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToReport }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      if (mountedRef.current && data.result) {
        const reportResult = data.result as VoiceReportResult;
        setReport(reportResult);
        return reportResult;
      }

      return null;
    } catch (e) {
      const message = e instanceof Error ? e.message : 'Report failed';
      if (mountedRef.current) {
        setError(message);
      }
      console.error('[useVoiceGate] Report error:', e);
      return null;
    } finally {
      if (mountedRef.current) {
        setIsChecking(false);
      }
    }
  }, []);

  // ==========================================================================
  // Auto-check when text changes
  // ==========================================================================

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
      if (debounceRef.current !== null) {
        window.clearTimeout(debounceRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (!enabled || !text) {
      return;
    }

    // Clear previous timeout
    if (debounceRef.current !== null) {
      window.clearTimeout(debounceRef.current);
    }

    // Debounce check
    debounceRef.current = window.setTimeout(() => {
      check(text);
    }, debounceMs);

    return () => {
      if (debounceRef.current !== null) {
        window.clearTimeout(debounceRef.current);
      }
    };
  }, [text, enabled, debounceMs, check]);

  return {
    result,
    report,
    score,
    passed,
    violations,
    warnings,
    anchors,
    isChecking,
    error,
    check,
    getReport,
  };
}

export default useVoiceGate;
