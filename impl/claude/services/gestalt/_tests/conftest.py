"""
Gestalt service test fixtures.

Registry population is handled by impl/claude/conftest.py:
  _ensure_global_registries_populated()

That session-scoped fixture runs at session start for ALL tests,
ensuring NodeRegistry (including world.codebase) is fully populated.
"""

from __future__ import annotations

# No local fixtures needed - root conftest.py handles registry population.
