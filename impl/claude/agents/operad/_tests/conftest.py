"""
Operad test fixtures.

Registry population is handled by impl/claude/conftest.py:
  _ensure_global_registries_populated()

That session-scoped fixture runs at session start for ALL tests,
ensuring OperadRegistry is fully populated before any tests run.

Canary tests: See test_xdist_registry_canary.py in this directory.
"""

from __future__ import annotations

# No local fixtures needed - root conftest.py handles registry population.
