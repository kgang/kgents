# SaaS Soak Test Baseline

> Long-running stability validation for kgents SaaS infrastructure.

## Overview

Soak testing validates system stability over extended periods, detecting:
- Memory leaks
- Resource exhaustion
- Latency degradation
- Connection pool exhaustion
- Circuit breaker patterns

**Test Script:** `impl/claude/tests/load/saas-soak.js`

---

## Test Configurations

### Full Soak Test (Production Validation)

```bash
k6 run --vus 10 --duration 24h impl/claude/tests/load/saas-soak.js
```

| Parameter | Value |
|-----------|-------|
| Duration | 24 hours |
| Virtual Users | 10 constant |
| Endpoints | `/health/saas`, `/v1/agentese/resolve` |
| Request Rate | ~20 req/s sustained |

### Accelerated Soak Test (CI/Staging)

```bash
k6 run --vus 25 --duration 4h impl/claude/tests/load/saas-soak.js
```

| Parameter | Value |
|-----------|-------|
| Duration | 4 hours |
| Virtual Users | 25 constant |
| Endpoints | `/health/saas`, `/v1/agentese/resolve` |
| Request Rate | ~50 req/s sustained |

### Quick Validation (Development)

```bash
k6 run --vus 10 --duration 1h impl/claude/tests/load/saas-soak.js
```

---

## Thresholds

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Health p95 latency | < 200ms | Stricter than baseline for stability |
| Agentese p95 latency | < 300ms | Accounts for business logic |
| Error rate | < 0.1% | Near-zero tolerance for soak |
| Memory growth | < 10% over baseline | Detect leaks |

---

## Baseline Results

### Test Run: [DATE]

**Configuration:**
- Duration: ___ hours
- VUs: ___
- Environment: ___

**Results:**

| Metric | Value | Status |
|--------|-------|--------|
| Total Requests | ___ | — |
| Requests/sec | ___ | — |
| Error Rate | ___% | [ ] Pass |
| Health p95 | ___ ms | [ ] Pass |
| Health p99 | ___ ms | [ ] Pass |
| Agentese p95 | ___ ms | [ ] Pass |
| Circuit Breaker Activations | ___ | — |
| Memory Growth Indicator | ___x | [ ] Pass |

**Stability Analysis:**

- [ ] Latency remained stable throughout test
- [ ] No memory leak indicators (growth < 10%)
- [ ] Error rate stayed below threshold
- [ ] No circuit breaker issues

---

## Memory Leak Detection

The soak test tracks latency growth as a proxy for memory leaks:

```
Memory Growth Indicator = Current Latency / Baseline Latency
```

| Indicator | Interpretation |
|-----------|----------------|
| < 1.1x | Healthy (< 10% growth) |
| 1.1x - 1.5x | Warning (investigate) |
| > 1.5x | Critical (likely leak) |

### If Memory Leak Detected

1. **Identify the source:**
   ```bash
   # Check API memory in Prometheus/Grafana
   # Query: container_memory_usage_bytes{container="api"}
   ```

2. **Profile the application:**
   ```bash
   # Enable memory profiling
   kubectl exec -n kgents-triad deploy/kgent-api -- python -c "import tracemalloc; tracemalloc.start()"
   ```

3. **Common causes:**
   - Unclosed connections (NATS, Redis)
   - Growing caches without eviction
   - Event handler accumulation
   - Large request/response buffering

---

## Grafana Dashboard

### Recommended Panels for Soak Testing

1. **Memory Over Time**
   ```promql
   container_memory_usage_bytes{container="api", namespace="kgents-triad"}
   ```

2. **Latency Percentiles Over Time**
   ```promql
   histogram_quantile(0.95, rate(kgents_api_request_latency_seconds_bucket[5m]))
   ```

3. **Error Rate Over Time**
   ```promql
   rate(kgents_api_request_errors_total[5m])
   ```

4. **Circuit Breaker State**
   ```promql
   kgents_nats_circuit_state
   ```

---

## Running the Test

### Prerequisites

1. k6 installed: `brew install k6`
2. API running locally or accessible
3. Grafana/Prometheus available for monitoring

### Execute

```bash
# Set environment variables
export API_BASE_URL=http://localhost:8000
export SOAK_DURATION=4h
export SOAK_VUS=10

# Run test
k6 run impl/claude/tests/load/saas-soak.js

# Output saved to: soak-test-results.json
```

### Monitor During Test

```bash
# Watch API memory
kubectl top pods -n kgents-triad -l app.kubernetes.io/name=kgent-api --watch

# Watch circuit breaker
watch 'curl -s localhost:8000/health/saas | jq .nats'

# Watch k6 output
# (k6 will print progress and final summary)
```

---

## Historical Results

| Date | Duration | VUs | Error Rate | Health p95 | Memory Growth | Status |
|------|----------|-----|------------|------------|---------------|--------|
| ___ | ___ h | ___ | ___% | ___ ms | ___x | [ ] Pass |

---

## CI Integration

```yaml
# Example GitHub Actions job
soak-test:
  runs-on: ubuntu-latest
  timeout-minutes: 300  # 5 hours max
  steps:
    - uses: actions/checkout@v4
    - uses: grafana/k6-action@v0.3.0
      with:
        filename: impl/claude/tests/load/saas-soak.js
        flags: --vus 25 --duration 4h
      env:
        API_BASE_URL: ${{ secrets.STAGING_API_URL }}
    - uses: actions/upload-artifact@v3
      with:
        name: soak-test-results
        path: soak-test-results.json
```

---

## Next Steps

After successful soak test:
1. Record baseline in this document
2. Add memory trend panel to Grafana
3. Configure alert for memory growth > 20%
4. Schedule weekly soak tests in staging

---

*Last Updated: 2025-12-14 | Phase 9: Production Hardening*
