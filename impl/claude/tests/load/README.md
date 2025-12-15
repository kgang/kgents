# Load Testing

Load tests for kgents SaaS infrastructure using k6.

## Prerequisites

Install k6:
```bash
brew install k6  # macOS
# or
docker pull grafana/k6  # Docker
```

## Tests

### saas-health.js

Tests the `/health/saas` endpoint for baseline throughput.

**Target Metrics:**
- Throughput: 100 req/s sustained
- Latency p95: < 500ms
- Latency p99: < 1000ms
- Error Rate: < 1%

**Usage:**
```bash
# Baseline test (50 VUs, 5 minutes)
k6 run saas-health.js

# Custom VUs and duration
k6 run --vus 100 --duration 10m saas-health.js

# With custom API URL
API_BASE_URL=https://api.kgents.io k6 run saas-health.js

# Docker
docker run -i grafana/k6 run - < saas-health.js
```

## Scenarios

| Scenario | VUs | Duration | Target |
|----------|-----|----------|--------|
| Baseline | 50 | 5m | Establish baseline |
| Stress | 100 | 10m | Find limits |
| Soak | 25 | 1h | Memory leaks |

## Results

Results are written to `load-test-results.json` after each run.

## CI Integration

Add to GitHub Actions:
```yaml
- name: Run load tests
  uses: grafana/k6-action@v0.2.0
  with:
    filename: impl/claude/tests/load/saas-health.js
    flags: --vus 50 --duration 2m
```
