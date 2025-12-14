"""
Ghost Infrastructure - Living Filesystem with Real Data.

This module implements the "trust loop" integration strategy:
1. Collect real signals (git, flinches, tests, infra)
2. Project to .kgents/ghost/ files
3. Developer learns to glance at them
4. Trust grows through demonstrated accuracy

Design Principles:
- All data comes from real sources (no placeholders)
- Failures are visible, not hidden
- Updates are reliable (3-minute interval or on-demand)
- ClaudeCLIRuntime is the execution backbone when LLM is needed

Files Projected:
    health.status       - One-line status for IDE integration
    thought_stream.md   - System narrative (what's happening)
    tension_map.json    - Areas of concern
    context.json        - Current context summary
    flinch_summary.json - Test failure analysis

Key Classes:
    GhostCollector      - Base class for data collectors
    GitCollector        - Git status, branch, recent commits
    FlinchCollector     - Test failure patterns from JSONL
    InfraCollector      - K-Terrarium cluster status
    GhostDaemon         - Background projection loop
    CompositeHealth     - Aggregated health from all sources
"""

from __future__ import annotations

from .cache import (
    GLASS_CACHE_DIR,
    GlassCacheManager,
    clear_glass_cache,
    get_glass_cache,
    seed_glass_cache,
)
from .collectors import (
    CollectorResult,
    FlinchCollector,
    GhostCollector,
    GitCollector,
    InfraCollector,
    TraceGhostCollector,
    create_all_collectors,
)
from .daemon import GhostDaemon, create_ghost_daemon
from .health import CompositeHealth, HealthLevel, create_composite_health
from .lifecycle import (
    ExpirationEvent,
    LifecycleAwareCache,
    LifecycleCacheEntry,
    LifecycleStats,
    create_entry,
    create_from_allocation,
    get_lifecycle_cache,
    sync_allocation_to_cache,
)

__all__ = [
    # Collectors
    "GhostCollector",
    "GitCollector",
    "FlinchCollector",
    "InfraCollector",
    "TraceGhostCollector",
    "CollectorResult",
    "create_all_collectors",
    # Health
    "CompositeHealth",
    "HealthLevel",
    "create_composite_health",
    # Daemon
    "GhostDaemon",
    "create_ghost_daemon",
    # Glass Cache (CLI offline fallback)
    "GlassCacheManager",
    "get_glass_cache",
    "seed_glass_cache",
    "clear_glass_cache",
    "GLASS_CACHE_DIR",
    # Lifecycle-Aware Cache
    "LifecycleAwareCache",
    "LifecycleCacheEntry",
    "LifecycleStats",
    "ExpirationEvent",
    "get_lifecycle_cache",
    "create_entry",
    "create_from_allocation",
    "sync_allocation_to_cache",
]
