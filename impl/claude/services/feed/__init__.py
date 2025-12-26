"""
Feed Crown Jewel: Algorithmic K-Block Discovery.

"The feed is not a view of data. The feed IS the primary interface."

The Feed service provides algorithmic ranking and filtering of K-Blocks
based on attention, principles alignment, recency, and coherence (Galois loss).

AGENTESE Paths (via @node("self.feed")):
- self.feed.manifest  - Feed health status
- self.feed.cosmos    - All K-Blocks (unfiltered)
- self.feed.coherent  - Low-loss items (< 0.2 loss)
- self.feed.contradictions - Flagged pairs with conflicts

Key Concepts:
- Feed: A filtered, ranked stream of K-Blocks
- FeedRanking: Weighted combination of attention, principles, recency, coherence
- FeedFeedback: User interaction tracking for personalization
- Default Feeds: Cosmos, Coherent, Contradictions, Axioms, Handwavy

Philosophy:
    A feed without filters is the raw cosmos.
    A feed with filters is a perspective.
    Multiple feeds = multiple selves.

See: plans/zero-seed-genesis-grand-strategy.md (Part IV)
See: docs/skills/metaphysical-fullstack.md
"""

from .core import (
    Feed,
    FeedFilter,
    FeedRanking,
    FeedSource,
    FeedFeedback,
)
from .defaults import (
    COSMOS_FEED,
    COHERENT_FEED,
    CONTRADICTIONS_FEED,
    AXIOMS_FEED,
    HANDWAVY_FEED,
    DEFAULT_FEEDS,
    get_default_feed,
)
from .ranking import (
    AttentionScore,
    CoherenceScore,
    PrinciplesScore,
    RecencyScore,
    compute_feed_score,
    rank_kblocks,
)
from .feedback import (
    FeedbackAction,
    FeedbackEvent,
    FeedbackSystem,
    AttentionTracker,
    AttentionTrackerProtocol,
    InMemoryAttentionTracker,
    PersistentAttentionTracker,
)
from .config import (
    FeedConfig,
    get_feed_config,
    reset_feed_config,
    DEFAULT_CONFIG,
)
from .node import FeedNode

__all__ = [
    # AGENTESE Node
    "FeedNode",
    # Core types
    "Feed",
    "FeedFilter",
    "FeedRanking",
    "FeedSource",
    "FeedFeedback",
    # Defaults
    "COSMOS_FEED",
    "COHERENT_FEED",
    "CONTRADICTIONS_FEED",
    "AXIOMS_FEED",
    "HANDWAVY_FEED",
    "DEFAULT_FEEDS",
    "get_default_feed",
    # Ranking
    "AttentionScore",
    "CoherenceScore",
    "PrinciplesScore",
    "RecencyScore",
    "compute_feed_score",
    "rank_kblocks",
    # Feedback
    "FeedbackAction",
    "FeedbackEvent",
    "FeedbackSystem",
    "AttentionTracker",
    "AttentionTrackerProtocol",
    "InMemoryAttentionTracker",
    "PersistentAttentionTracker",
    # Config
    "FeedConfig",
    "get_feed_config",
    "reset_feed_config",
    "DEFAULT_CONFIG",
]
