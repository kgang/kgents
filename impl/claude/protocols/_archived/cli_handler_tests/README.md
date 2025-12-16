# Archived CLI Handler Tests

Tests for CLI handlers that were deprecated during the D-gent/M-gent architecture rewrite.

## Archived Tests (2025-12-16)

| Test File | Handler | Reason |
|-----------|---------|--------|
| `test_archetype.py` | archetype.py | Handler deleted (H-gent deprecation) |
| `test_collective_shadow.py` | collective_shadow.py | Handler deleted (H-gent deprecation) |
| `test_continuous.py` | continuous.py | Handler deleted (streaming replaced by Flux) |
| `test_gaps.py` | gaps.py | Handler deleted |
| `test_mirror.py` | mirror.py | Handler deleted (H-gent deprecation) |
| `test_shadow.py` | shadow.py | Handler deleted (H-gent deprecation) |

## Restoration

If handlers are restored, move corresponding tests back to:
`protocols/cli/handlers/_tests/`
