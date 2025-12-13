# Test Optimization Skill

> Pattern for profiling and optimizing test suite performance.

## Overview

The test optimization framework provides automatic test profiling, tier-based categorization, and optimization recommendations.

## Quick Start

```bash
# Run tests with profiling
pytest --profile-tests

# Run with recommendations
pytest --profile-tests --show-recommendations

# Generate standalone report
python -m testing.optimization.pytest_plugin
```

## Test Tiers

Tests are automatically categorized by execution time:

| Tier | Duration | Meaning |
|------|----------|---------|
| INSTANT | < 100ms | Unit tests, fast assertions |
| FAST | 100ms - 1s | Simple integration tests |
| MEDIUM | 1s - 5s | Database/network tests |
| SLOW | 5s - 30s | Full integration, E2E |
| EXPENSIVE | > 30s | Should be cached or mocked |

## Profile Storage

Profiles are stored in `.kgents/ghost/test_profiles.jsonl`:

```json
{"type": "profile", "test_id": "test_foo", "duration_ms": 500.0, "tier": "fast", ...}
```

## Dashboard Integration

View test health in the dashboard:

```python
from testing.optimization.dashboard import collect_test_health_metrics

metrics = await collect_test_health_metrics()
print(f"Total: {metrics.total_tests}, Status: {metrics.status_text}")
```

The `TestHealthPanel` widget can be added to any Textual dashboard.

## Recommendations

The framework generates recommendations for expensive tests:

1. **mark_slow** - Add `@pytest.mark.slow` to exclude from default runs
2. **cache_static_analysis** - Use module-scoped fixtures for trace analysis
3. **mock_expensive** - Mock external calls in expensive tests

## Framework Components

| Module | Purpose |
|--------|---------|
| `__init__.py` | Core types: TestTier, TestProfile, RefinementTracker |
| `pytest_plugin.py` | Pytest hook integration, `--profile-tests` CLI |
| `redundancy.py` | Coverage-based redundancy detection |
| `partition.py` | Operad-based test partitioning |
| `flux.py` | Self-improving TestOptimizationFlux agent |
| `dashboard.py` | TestHealthMetrics and panel for dashboard |

## Categorical Principle

> "Tests are the executable specification. A slow test suite is a spec that no one reads."

The framework models test optimization as a polynomial functor:

```
TestOptimizer: PolyAgent[OptimizationState, TestSuite, OptimizedSuite]
```

AGENTESE path: `self.test.optimization.witness`

## See Also

- `impl/claude/testing/optimization/` - Implementation
- `plans/skills/test-patterns.md` - General testing patterns
- `impl/claude/conftest.py` - Pytest configuration
