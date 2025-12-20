/**
 * Web Vitals reporting for performance monitoring.
 *
 * Tracks Core Web Vitals:
 * - LCP (Largest Contentful Paint) - loading performance
 * - FID (First Input Delay) - interactivity
 * - CLS (Cumulative Layout Shift) - visual stability
 * - FCP (First Contentful Paint) - perceived load speed
 * - TTFB (Time to First Byte) - server response time
 *
 * Usage:
 *   // In main.tsx
 *   import { reportWebVitals } from '@/lib/reportWebVitals';
 *   reportWebVitals(console.log);
 *
 *   // Or send to analytics:
 *   reportWebVitals((metric) => {
 *     analytics.track('web-vital', {
 *       name: metric.name,
 *       value: metric.value,
 *       rating: metric.rating,
 *     });
 *   });
 */

import { onCLS, onFCP, onINP, onLCP, onTTFB, type Metric } from 'web-vitals';

export type WebVitalMetric = Metric;

export interface WebVitalReport {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
}

// Target thresholds (matching Phase 4 plan)
export const WEB_VITAL_TARGETS = {
  FCP: 1500, // <1.5s
  LCP: 2500, // <2.5s
  INP: 200, // <200ms (replaced FID)
  CLS: 0.1, // <0.1
  TTFB: 800, // <800ms
} as const;

export function reportWebVitals(onReport: (metric: WebVitalReport) => void): void {
  const handler = (metric: Metric) => {
    onReport({
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
      id: metric.id,
    });
  };

  onCLS(handler);
  onFCP(handler);
  onINP(handler);
  onLCP(handler);
  onTTFB(handler);
}

// Development helper: log to console with color coding
export function reportWebVitalsToConsole(): void {
  reportWebVitals((metric) => {
    const target = WEB_VITAL_TARGETS[metric.name as keyof typeof WEB_VITAL_TARGETS];
    const status =
      metric.rating === 'good'
        ? '\u2705'
        : metric.rating === 'needs-improvement'
          ? '\u26A0\uFE0F'
          : '\u274C';
    const color =
      metric.rating === 'good'
        ? 'color: green'
        : metric.rating === 'needs-improvement'
          ? 'color: orange'
          : 'color: red';

    console.log(
      `%c${status} ${metric.name}: ${metric.value.toFixed(2)}${target ? ` (target: ${target})` : ''} [${metric.rating}]`,
      color
    );
  });
}

export default reportWebVitals;
