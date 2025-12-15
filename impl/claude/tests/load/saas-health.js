/**
 * k6 Load Test for kgents SaaS Health Endpoint
 * Phase 6: Launch Prep - Establish baseline throughput
 *
 * Target: 100 req/s sustained for 5 minutes
 *
 * Usage:
 *   k6 run --vus 50 --duration 5m saas-health.js
 *   k6 run --vus 100 --duration 10m saas-health.js  # stress test
 *
 * Environment:
 *   API_BASE_URL - Base URL for the API (default: http://localhost:8000)
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const healthCheckDuration = new Trend('health_check_duration');

// Configuration
export const options = {
    // Baseline test: 50 VUs for 5 minutes
    scenarios: {
        baseline: {
            executor: 'constant-vus',
            vus: 50,
            duration: '5m',
        },
    },
    thresholds: {
        // 95th percentile response time should be < 500ms
        http_req_duration: ['p(95)<500'],
        // 99th percentile should be < 1000ms
        'http_req_duration{scenario:baseline}': ['p(99)<1000'],
        // Error rate should be < 1%
        errors: ['rate<0.01'],
        // Health check specific threshold
        health_check_duration: ['p(95)<300'],
    },
};

const BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000';

export default function () {
    // Test /health/saas endpoint
    const healthRes = http.get(`${BASE_URL}/health/saas`, {
        tags: { name: 'health_saas' },
    });

    // Track custom metrics
    healthCheckDuration.add(healthRes.timings.duration);

    // Validate response
    const healthChecks = check(healthRes, {
        'status is 200': (r) => r.status === 200,
        'has status field': (r) => {
            const body = JSON.parse(r.body);
            return body.status !== undefined;
        },
        'status is ok or not_configured': (r) => {
            const body = JSON.parse(r.body);
            return ['ok', 'not_configured', 'degraded'].includes(body.status);
        },
        'response time < 500ms': (r) => r.timings.duration < 500,
    });

    errorRate.add(!healthChecks);

    // Small sleep to simulate realistic client behavior
    sleep(0.1);
}

// Lifecycle hooks for reporting
export function handleSummary(data) {
    const summary = {
        timestamp: new Date().toISOString(),
        duration_seconds: data.root_group.duration / 1000,
        total_requests: data.metrics.http_reqs.values.count,
        avg_req_per_second: data.metrics.http_reqs.values.rate,
        error_rate: data.metrics.errors?.values?.rate || 0,
        latency: {
            p50: data.metrics.http_req_duration.values['p(50)'],
            p95: data.metrics.http_req_duration.values['p(95)'],
            p99: data.metrics.http_req_duration.values['p(99)'],
            max: data.metrics.http_req_duration.values.max,
        },
        thresholds_passed: Object.values(data.metrics).every(
            (m) => !m.thresholds || Object.values(m.thresholds).every((t) => t.ok)
        ),
    };

    console.log('\n=== Load Test Summary ===');
    console.log(`Total Requests: ${summary.total_requests}`);
    console.log(`Requests/sec: ${summary.avg_req_per_second.toFixed(2)}`);
    console.log(`Error Rate: ${(summary.error_rate * 100).toFixed(2)}%`);
    console.log(`Latency p95: ${summary.latency.p95?.toFixed(2) || 'N/A'}ms`);
    console.log(`Latency p99: ${summary.latency.p99?.toFixed(2) || 'N/A'}ms`);
    console.log(`Thresholds Passed: ${summary.thresholds_passed ? 'YES' : 'NO'}`);

    return {
        'stdout': JSON.stringify(summary, null, 2) + '\n',
        'load-test-results.json': JSON.stringify(summary, null, 2),
    };
}
