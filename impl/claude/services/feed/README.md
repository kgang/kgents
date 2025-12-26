# Feed Crown Jewel

**"The feed is not a view of data. The feed IS the primary interface."**

The Feed service provides algorithmic ranking and filtering of K-Blocks based on attention, principles alignment, recency, and coherence (Galois loss).

## Status: Phase 1 Complete

This is the **backend primitive** implementation for Zero Seed Genesis Grand Strategy Phase 1.

- ✅ Core primitives (Feed, FeedSource, FeedFilter, FeedRanking, FeedFeedback)
- ✅ Algorithmic ranking (attention + principles + recency + coherence)
- ✅ Feedback loop system (AttentionTracker, FeedbackSystem)
- ✅ 5 default feeds (cosmos, coherent, contradictions, axioms, handwavy)
- ✅ Tests for core functionality
- ⏳ K-Block integration (layer works, loss/author/tags TODO)
- ⏳ AGENTESE node registration
- ⏳ Frontend UI components

## Architecture

```
Feed Service
├── core.py         - Feed, FeedSource, FeedFilter, FeedRanking, FeedFeedback
├── ranking.py      - Algorithmic scoring (4 dimensions)
├── feedback.py     - User interaction tracking
├── defaults.py     - 5 canonical feeds
└── _tests/         - Test suite
```

## Core Concepts

### Feed

A filtered, ranked stream of K-Blocks.

```python
@dataclass
class Feed:
    id: str
    name: str
    description: str
    sources: tuple[FeedSource, ...]      # What enters
    filters: tuple[FeedFilter, ...]      # How to filter
    ranking: FeedRanking                 # How to rank
    feedback: FeedFeedback | None        # User interaction callbacks
```

### FeedSource

Defines where K-Blocks enter a feed:

- `all`: Everything (cosmos)
- `layer`: Filter by Zero Seed layer (1-7)
- `author`: Filter by author ID (TODO)
- `tag`: Filter by tag (TODO)
- `custom`: Custom predicate function

### FeedFilter

Filters K-Blocks by field and operator:

- Fields: `layer`, `loss`, `author`, `principle`, `time`, `custom`
- Operators: `eq`, `lt`, `gt`, `between`, `contains`

### FeedRanking

Weighted combination of 4 scoring dimensions:

1. **Attention**: User engagement patterns (views, edits, dismissals)
2. **Principles**: Alignment with user's declared values
3. **Recency**: Temporal freshness (exponential decay)
4. **Coherence**: Galois loss (low loss = high quality)

```python
@dataclass
class FeedRanking:
    attention_weight: float = 0.0
    principles_weight: float = 0.0
    recency_weight: float = 1.0
    coherence_weight: float = 0.0
    custom: Callable[[KBlock, User], float] | None = None
```

### FeedFeedback

User interaction callbacks for personalization:

```python
@dataclass
class FeedFeedback:
    on_view: Callable[[KBlock], None] | None
    on_engage: Callable[[KBlock], None] | None
    on_dismiss: Callable[[KBlock], None] | None
    on_contradict: Callable[[KBlock, KBlock], None] | None
```

## The 5 Default Feeds

### 1. Cosmos (`cosmos`)

Everything, in chronological order. The raw truth stream.

```python
COSMOS_FEED = Feed(
    id="cosmos",
    sources=(FeedSource(type="all"),),
    ranking=FeedRanking(recency_weight=1.0),
)
```

### 2. Coherent (`coherent`)

Lowest loss first — your most solid beliefs.

```python
COHERENT_FEED = Feed(
    id="coherent",
    sources=(FeedSource(type="all"),),
    ranking=FeedRanking(
        coherence_weight=1.0,
        recency_weight=0.1,
    ),
)
```

### 3. Contradictions (`contradictions`)

Where your beliefs conflict — opportunity for synthesis.

```python
CONTRADICTIONS_FEED = Feed(
    id="contradictions",
    filters=(
        FeedFilter(field="custom", value=lambda kb: has_contradiction_edge(kb)),
    ),
    ranking=FeedRanking(coherence_weight=-1.0),  # Highest loss first
)
```

### 4. Axioms (`axioms`)

L1-L2 only — the bedrock you stand on.

```python
AXIOMS_FEED = Feed(
    id="axioms",
    sources=(FeedSource(type="layer", value=(1, 2)),),
    ranking=FeedRanking(coherence_weight=1.0),
)
```

### 5. Handwavy (`handwavy`)

High loss L3 declarations waiting to cohere.

```python
HANDWAVY_FEED = Feed(
    id="handwavy",
    sources=(FeedSource(type="layer", value=3),),
    filters=(FeedFilter(field="loss", operator="gt", value=0.5),),
    ranking=FeedRanking(recency_weight=1.0),
)
```

## Usage Example

```python
from services.feed import (
    Feed,
    FeedSource,
    FeedFilter,
    FeedRanking,
    get_default_feed,
    rank_kblocks,
)

# Get a default feed
cosmos = get_default_feed("cosmos")

# Create a custom feed
my_feed = Feed(
    id="my-feed",
    name="My Custom Feed",
    sources=(FeedSource(type="layer", value=(3, 4)),),
    filters=(
        FeedFilter(field="layer", operator="gt", value=2),
    ),
    ranking=FeedRanking(
        attention_weight=0.5,
        recency_weight=0.3,
        coherence_weight=0.2,
    ),
)

# Filter K-Blocks
kblocks = [...]  # List of K-Blocks
filtered = [kb for kb in kblocks if my_feed.should_include(kb)]

# Rank K-Blocks
user = ...  # User object
ranked = await rank_kblocks(
    filtered,
    user=user,
    attention_weight=my_feed.ranking.attention_weight,
    recency_weight=my_feed.ranking.recency_weight,
    coherence_weight=my_feed.ranking.coherence_weight,
)

# Get top 50
top_50 = [kb for kb, score in ranked[:50]]
```

## Feedback Loop

```python
from services.feed import FeedbackSystem

# Create feedback system
feedback = FeedbackSystem()

# Track user interactions
await feedback.on_view(user_id="alice", kblock=kb)
await feedback.on_engage(user_id="alice", kblock=kb, action_type="edit")
await feedback.on_dismiss(user_id="alice", kblock=kb)

# Get attention score
score = await feedback.attention_tracker.get_attention_score("alice", kb.id)
```

## K-Block Integration Status

The Feed service integrates with K-Block via:

- ✅ `zero_seed_layer` (1-7) - Layer filtering works
- ⏳ `galois_loss` - Not yet stored on K-Block (defaults to 0.0)
- ⏳ `created_by` - Not yet on K-Block
- ⏳ `tags` - Not yet on K-Block
- ✅ `created_at` - Timestamp filtering works
- ✅ `toulmin_proof` - Proof principles filtering works
- ⏳ `edges` - Contradiction edge detection (placeholder)

## TODOs

### Phase 2: K-Block Schema Updates

1. Add `galois_loss` field to K-Block
2. Add `created_by` field to K-Block
3. Add `tags` field to K-Block
4. Finalize edge storage for contradiction detection

### Phase 3: AGENTESE Integration

1. Create `@node("self.feed")` for AGENTESE
2. Implement paths:
   - `self.feed.cosmos` - Get cosmos feed
   - `self.feed.coherent` - Get coherent feed
   - `self.feed.contradictions` - Get contradictions
   - `self.feed.axioms` - Get axioms
   - `self.feed.handwavy` - Get handwavy goals
   - `self.feed.custom` - Create custom feed

### Phase 4: Frontend UI

1. Feed component (React)
2. K-Block card with density modes (Compact/Comfortable/Spacious)
3. Infinite scroll with lazy loading
4. Feed switcher
5. Custom feed builder

### Phase 5: Persistence

1. Store user feeds in database
2. Persist attention tracking
3. Persist custom feeds

## Philosophy

From the Zero Seed Genesis Grand Strategy:

> "A feed without filters is the raw cosmos.
>  A feed with filters is a perspective.
>  Multiple feeds = multiple selves."

The feed is a primitive, not a component. Like Text, View, Button — Feed is foundational.

## References

- [Zero Seed Genesis Grand Strategy](../../../plans/zero-seed-genesis-grand-strategy.md) (Part IV)
- [K-Block Crown Jewel](../k_block/)
- [Zero Seed Crown Jewel](../zero_seed/)
