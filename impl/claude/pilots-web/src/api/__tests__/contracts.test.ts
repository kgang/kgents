/**
 * Contract Coherence Tests
 *
 * Verifies frontend expectations match shared contract definitions.
 * This is the frontend half of Contract Coherence Law (L6).
 *
 * Run: npm test -- --testPathPattern=contracts
 *
 * @see pilots/CONTRACT_COHERENCE.md
 * @see pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md (QA-5/6/7)
 */

import { describe, test, expect } from 'vitest';
import {
  TRAIL_RESPONSE_INVARIANTS,
  CAPTURE_RESPONSE_INVARIANTS,
  normalizeTrailResponse,
  isTrailResponse,
  type TrailResponse,
  type CaptureResponse,
} from '@kgents/shared-primitives';

describe('TrailResponse Contract', () => {
  test('invariants hold for valid response', () => {
    const response: TrailResponse = {
      marks: [
        {
          mark_id: 'mark-001',
          content: 'Started working on the Daily Lab pilot',
          tags: ['eureka'],
          timestamp: '2025-12-26T10:00:00Z',
        },
      ],
      gaps: [
        {
          start: '2025-12-26T10:00:00Z',
          end: '2025-12-26T12:00:00Z',
          duration_minutes: 120,
        },
      ],
      date: '2025-12-26',
    };

    for (const [name, check] of Object.entries(TRAIL_RESPONSE_INVARIANTS)) {
      expect(check(response), `Invariant failed: ${name}`).toBe(true);
    }
  });

  test('invariants hold for empty response', () => {
    const response: TrailResponse = {
      marks: [],
      gaps: [],
      date: '2025-12-26',
    };

    for (const [name, check] of Object.entries(TRAIL_RESPONSE_INVARIANTS)) {
      expect(check(response), `Invariant failed: ${name}`).toBe(true);
    }
  });

  test('isTrailResponse correctly identifies valid response', () => {
    const valid = {
      marks: [],
      gaps: [],
      date: '2025-12-26',
    };

    expect(isTrailResponse(valid)).toBe(true);
  });

  test('isTrailResponse rejects invalid response', () => {
    const invalid = {
      marks: [],
      // Missing gaps array
      date: '2025-12-26',
    };

    expect(isTrailResponse(invalid)).toBe(false);
  });

  test('defensive handling for malformed response (gap_minutes instead of gaps)', () => {
    // Simulate backend returning wrong shape (the original bug)
    const malformed = {
      marks: [],
      gap_minutes: 120, // Wrong! Should be gaps: []
      date: '2025-12-26',
    };

    // Frontend should handle gracefully via normalizeTrailResponse
    const normalized = normalizeTrailResponse(malformed);

    expect(Array.isArray(normalized.gaps)).toBe(true);
    expect(normalized.gaps.length).toBe(0); // Empty array, not undefined
  });

  test('normalizeTrailResponse preserves valid data', () => {
    const valid: TrailResponse = {
      marks: [
        {
          mark_id: 'mark-001',
          content: 'Test mark',
          tags: [],
          timestamp: '2025-12-26T10:00:00Z',
        },
      ],
      gaps: [
        {
          start: '2025-12-26T10:00:00Z',
          end: '2025-12-26T11:00:00Z',
          duration_minutes: 60,
        },
      ],
      date: '2025-12-26',
      total: 1,
      position: 1,
    };

    const normalized = normalizeTrailResponse(valid);

    expect(normalized.marks).toEqual(valid.marks);
    expect(normalized.gaps).toEqual(valid.gaps);
    expect(normalized.date).toBe(valid.date);
    expect(normalized.total).toBe(valid.total);
    expect(normalized.position).toBe(valid.position);
  });

  test('normalizeTrailResponse handles empty object', () => {
    // The function expects at least an object-like value
    // null/undefined should be caught before calling normalize
    expect(normalizeTrailResponse({}).gaps).toEqual([]);
    expect(normalizeTrailResponse({}).marks).toEqual([]);
  });
});

describe('CaptureResponse Contract', () => {
  test('invariants hold for valid response', () => {
    const response: CaptureResponse = {
      mark_id: 'mark-001',
      content: 'Captured a moment',
      tag: 'joy',
      timestamp: '2025-12-26T10:00:00Z',
      warmth_response: 'Captured. Joy is noted.',
    };

    for (const [name, check] of Object.entries(CAPTURE_RESPONSE_INVARIANTS)) {
      expect(check(response), `Invariant failed: ${name}`).toBe(true);
    }
  });

  test('invariants hold for response without tag', () => {
    const response: CaptureResponse = {
      mark_id: 'mark-002',
      content: 'Quick thought',
      tag: null,
      timestamp: '2025-12-26T10:05:00Z',
      warmth_response: 'Captured.',
    };

    for (const [name, check] of Object.entries(CAPTURE_RESPONSE_INVARIANTS)) {
      expect(check(response), `Invariant failed: ${name}`).toBe(true);
    }
  });
});

describe('Contract Coherence', () => {
  test('all required types are exported from shared-primitives', () => {
    // This test ensures we import from shared-primitives, not local definitions
    // If this compiles, the contract is coherent on the frontend side
    const testTypes = {
      TRAIL_RESPONSE_INVARIANTS,
      CAPTURE_RESPONSE_INVARIANTS,
      normalizeTrailResponse,
      isTrailResponse,
    };

    // All should be defined
    for (const [name, value] of Object.entries(testTypes)) {
      expect(value, `${name} should be defined`).toBeDefined();
    }
  });

  test('TrailResponse has required fields', () => {
    // TypeScript compile-time check - if this compiles, contract is correct
    const response: TrailResponse = {
      marks: [],
      gaps: [], // MUST be array, not scalar
      date: '2025-12-26',
    };

    // Runtime check
    expect(response.marks).toBeDefined();
    expect(response.gaps).toBeDefined();
    expect(response.date).toBeDefined();
    expect(Array.isArray(response.marks)).toBe(true);
    expect(Array.isArray(response.gaps)).toBe(true);
  });
});
