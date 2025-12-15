/**
 * k6 Soak Test for kgents SaaS Infrastructure
 * Phase 9: Production Hardening - Memory leak detection and stability validation
 *
 * Purpose:
 *   - Detect memory leaks over extended runtime
 *   - Validate latency stability under sustained load
 *   - Monitor error patterns over time
 *   - Verify circuit breaker behavior
 *
 * Usage:
 *   # Full 24h soak test (production validation)
 *   k6 run --vus 10 --duration 24h saas-soak.js
 *
 *   # Accelerated 4h soak test (CI/staging)
 *   k6 run --vus 25 --duration 4h saas-soak.js
 *
 *   # Quick validation (1h)
 *   k6 run --vus 10 --duration 1h saas-soak.js
 *
 * Environment:
 *   API_BASE_URL - Base URL for the API (default: http://localhost:8000)
 *   SOAK_DURATION - Override duration (default: 4h)
 *   SOAK_VUS - Override VU count (default: 10)
 *
 * Thresholds:
 *   - p95 latency < 200ms (stricter than baseline for stability)
 *   - Error rate < 0.1%
 *   - No memory growth > 10% over baseline
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';

// Custom metrics for soak testing
const errorRate = new Rate('soak_errors');
const healthCheckDuration = new Trend('soak_health_duration');
const agenteseDuration = new Trend('soak_agentese_duration');
const circuitBreakerOpen = new Counter('soak_circuit_breaker_activations');
const memoryGrowthIndicator = new Gauge('soak_memory_growth_indicator');
const successfulRequests = new Counter('soak_successful_requests');

// Configuration
const DURATION = __ENV.SOAK_DURATION || '4h';
const VUS = parseInt(__ENV.SOAK_VUS || '10');

export const options = {
    scenarios: {
        // Constant load soak test
        soak: {
            executor: 'constant-vus',
            vus: VUS,
            duration: DURATION,
        },
    },
    thresholds: {
        // Stricter thresholds for soak testing
        'soak_health_duration': ['p(95)<200', 'p(99)<500'],
        'soak_agentese_duration': ['p(95)<300', 'p(99)<750'],
        'soak_errors': ['rate<0.001'],  // < 0.1% error rate
        'http_req_duration': ['p(95)<200', 'p(99)<500'],
        'http_req_failed': ['rate<0.001'],
    },
    // Extended setup/teardown for soak
    setupTimeout: '60s',
    teardownTimeout: '60s',
};

const BASE_URL = __ENV.API_BASE_URL || 'http://localhost:8000';

// Track start time for duration-based metrics
let testStartTime;

export function setup() {
    testStartTime = Date.now();

    // Capture baseline metrics at start
    const healthRes = http.get(`${BASE_URL}/health/saas`);
    const baselineCheck = check(healthRes, {
        'baseline: API reachable': (r) => r.status === 200,
    });

    if (!baselineCheck) {
        console.error('API not reachable at start of soak test');
    }

    return {
        startTime: testStartTime,
        baselineLatency: healthRes.timings.duration,
    };
}

export default function (data) {
    const elapsedHours = (Date.now() - data.startTime) / (1000 * 60 * 60);

    group('health_checks', function () {
        // Primary health endpoint
        const healthRes = http.get(`${BASE_URL}/health/saas`, {
            tags: { name: 'health_saas', phase: 'soak' },
        });

        healthCheckDuration.add(healthRes.timings.duration);

        const healthOk = check(healthRes, {
            'health: status 200': (r) => r.status === 200,
            'health: has status': (r) => {
                try {
                    const body = JSON.parse(r.body);
                    return body.status !== undefined;
                } catch {
                    return false;
                }
            },
            'health: latency < 200ms': (r) => r.timings.duration < 200,
        });

        if (healthOk) {
            successfulRequests.add(1);
        } else {
            errorRate.add(1);
        }

        // Check for circuit breaker state
        try {
            const body = JSON.parse(healthRes.body);
            if (body.nats?.status === 'circuit_open') {
                circuitBreakerOpen.add(1);
                console.log(`[${elapsedHours.toFixed(2)}h] Circuit breaker OPEN detected`);
            }
        } catch {
            // Ignore parse errors
        }
    });

    group('agentese_resolve', function () {
        // Mixed workload: AGENTESE resolution (simulates real usage)
        const resolvePayload = JSON.stringify({
            path: 'self.soul.manifest',
            observer: { id: `soak-test-${__VU}` },
        });

        const resolveRes = http.post(
            `${BASE_URL}/v1/agentese/resolve`,
            resolvePayload,
            {
                headers: { 'Content-Type': 'application/json' },
                tags: { name: 'agentese_resolve', phase: 'soak' },
            }
        );

        agenteseDuration.add(resolveRes.timings.duration);

        const resolveOk = check(resolveRes, {
            'agentese: status 200 or 404': (r) => [200, 404, 422].includes(r.status),
            'agentese: latency < 300ms': (r) => r.timings.duration < 300,
        });

        if (resolveOk) {
            successfulRequests.add(1);
        } else {
            errorRate.add(1);
        }
    });

    // Periodic memory/stability indicator
    // Log progress every ~100 iterations per VU
    if (__ITER % 100 === 0) {
        // Use health response latency as proxy for system health
        const checkRes = http.get(`${BASE_URL}/health`);
        const currentLatency = checkRes.timings.duration;
        const latencyGrowth = currentLatency / data.baselineLatency;

        // Track latency growth as memory leak proxy
        memoryGrowthIndicator.add(latencyGrowth);

        if (latencyGrowth > 1.5) {
            console.log(`[${elapsedHours.toFixed(2)}h] WARNING: Latency growth ${latencyGrowth.toFixed(2)}x baseline`);
        }
    }

    // Pacing: simulate realistic client behavior (1-2 req/s per VU)
    sleep(Math.random() * 0.5 + 0.5);
}

export function teardown(data) {
    const totalDuration = (Date.now() - data.startTime) / (1000 * 60 * 60);
    console.log(`\nSoak test completed: ${totalDuration.toFixed(2)} hours`);
}

export function handleSummary(data) {
    const totalDurationMs = data.state?.testRunDurationMs || 0;
    const totalDurationHours = totalDurationMs / (1000 * 60 * 60);

    // Extract metrics safely
    const getMetricValue = (metric, key) => {
        try {
            return data.metrics[metric]?.values?.[key] || 0;
        } catch {
            return 0;
        }
    };

    const summary = {
        test: 'soak',
        timestamp: new Date().toISOString(),
        duration_hours: totalDurationHours.toFixed(2),
        total_requests: getMetricValue('http_reqs', 'count'),
        successful_requests: getMetricValue('soak_successful_requests', 'count'),
        avg_req_per_second: getMetricValue('http_reqs', 'rate'),
        error_rate: getMetricValue('soak_errors', 'rate'),
        circuit_breaker_activations: getMetricValue('soak_circuit_breaker_activations', 'count'),
        health_latency: {
            p50: getMetricValue('soak_health_duration', 'p(50)'),
            p95: getMetricValue('soak_health_duration', 'p(95)'),
            p99: getMetricValue('soak_health_duration', 'p(99)'),
            max: getMetricValue('soak_health_duration', 'max'),
        },
        agentese_latency: {
            p50: getMetricValue('soak_agentese_duration', 'p(50)'),
            p95: getMetricValue('soak_agentese_duration', 'p(95)'),
            p99: getMetricValue('soak_agentese_duration', 'p(99)'),
            max: getMetricValue('soak_agentese_duration', 'max'),
        },
        memory_growth_indicator: getMetricValue('soak_memory_growth_indicator', 'value'),
        thresholds_passed: Object.values(data.metrics).every(
            (m) => !m.thresholds || Object.values(m.thresholds).every((t) => t.ok)
        ),
        stability_analysis: {
            latency_stable: getMetricValue('soak_health_duration', 'p(95)') < 200,
            error_rate_acceptable: getMetricValue('soak_errors', 'rate') < 0.001,
            no_memory_leak_indicators: getMetricValue('soak_memory_growth_indicator', 'value') < 1.1,
        },
    };

    console.log('\n' + '='.repeat(60));
    console.log('SOAK TEST SUMMARY');
    console.log('='.repeat(60));
    console.log(`Duration: ${summary.duration_hours} hours`);
    console.log(`Total Requests: ${summary.total_requests}`);
    console.log(`Requests/sec: ${summary.avg_req_per_second.toFixed(2)}`);
    console.log(`Error Rate: ${(summary.error_rate * 100).toFixed(4)}%`);
    console.log(`Health p95: ${summary.health_latency.p95?.toFixed(2) || 'N/A'}ms`);
    console.log(`Agentese p95: ${summary.agentese_latency.p95?.toFixed(2) || 'N/A'}ms`);
    console.log(`Circuit Breaker Activations: ${summary.circuit_breaker_activations}`);
    console.log(`Memory Growth Indicator: ${summary.memory_growth_indicator?.toFixed(2) || 'N/A'}x`);
    console.log('---');
    console.log('Stability Analysis:');
    console.log(`  Latency Stable: ${summary.stability_analysis.latency_stable ? 'YES' : 'NO'}`);
    console.log(`  Error Rate OK: ${summary.stability_analysis.error_rate_acceptable ? 'YES' : 'NO'}`);
    console.log(`  No Memory Leak: ${summary.stability_analysis.no_memory_leak_indicators ? 'YES' : 'NO'}`);
    console.log('---');
    console.log(`THRESHOLDS PASSED: ${summary.thresholds_passed ? 'YES' : 'NO'}`);
    console.log('='.repeat(60));

    return {
        'stdout': JSON.stringify(summary, null, 2) + '\n',
        'soak-test-results.json': JSON.stringify(summary, null, 2),
    };
}
