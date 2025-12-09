# EventStream Protocol: Temporal Observation

**Where static snapshots become flowing time.**

**Status:** Specification v1.0
**Depends On:** J-gents (reality classification), W-gents (witness), H-gents (dialectic)
**Part Of:** Mirror Protocol Phase 2
**Last Updated:** 2025-12-09

---

## Philosophy

> "You cannot step into the same codebase twice—for it is not the same codebase, and you are not the same developer."

The Mirror Protocol Phase 1 observes **snapshots**—static slices of reality frozen in time. But organizations are not static. They are **flows**—rivers of commits, evolving documents, drifting meanings.

EventStream abstracts the **temporal dimension**, allowing the Mirror to witness:
- **Change**: What shifted between observations?
- **Momentum**: What direction is meaning moving?
- **Conservation**: What principles are being preserved or violated?
- **Drift**: What semantic fields are leaking entropy?

---

## The Three Realities

Before processing any stream, we must classify its **nature** using J-gent reality classification:

```
┌────────────────────────────────────────────────────────────────┐
│                     REALITY TRICHOTOMY                         │
│                                                                │
│   DETERMINISTIC           PROBABILISTIC          CHAOTIC       │
│   ───────────────        ───────────────        ──────────     │
│                                                                │
│   Bounded                Decomposable           Unbounded      │
│   Single-step            Multi-step             Recursive      │
│   Predictable            Analyzable             Unstable       │
│                                                                │
│   Examples:              Examples:              Examples:      │
│   • File read            • Git history          • Live stream  │
│   • Directory list       • Parse log file       • Infinite gen │
│   • Fetch URL            • Analyze archive      • Cyclic deps  │
│                                                                │
│   Action:                Action:                Action:        │
│   Execute directly       Spawn sub-promises     Collapse to    │
│                          (lazy expansion)       Ground         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Reality Classification Algorithm

```python
def classify_stream_reality(stream: EventStream) -> Reality:
    """
    Classify the nature of a stream before processing.

    Returns:
        DETERMINISTIC: Bounded, single-pass processing
        PROBABILISTIC: Complex but decomposable
        CHAOTIC: Unbounded or unstable
    """
    # Check boundedness
    if not stream.is_bounded():
        return Reality.CHAOTIC

    # Estimate complexity
    est_size = stream.estimate_size()
    if est_size < DETERMINISTIC_THRESHOLD:
        return Reality.DETERMINISTIC

    # Check for cycles or recursion
    if stream.has_cycles():
        return Reality.CHAOTIC

    # Default: probabilistic (complex but manageable)
    return Reality.PROBABILISTIC
```

---

## The EventStream Protocol

A **protocol** (not a class)—implementations vary, interface is fixed.

### Core Interface

```python
from typing import Protocol, Iterator, AsyncIterator, TypeVar
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

T = TypeVar('T', covariant=True)

class Reality(Enum):
    """J-gent reality classification."""
    DETERMINISTIC = "deterministic"
    PROBABILISTIC = "probabilistic"
    CHAOTIC = "chaotic"

@dataclass(frozen=True)
class Event:
    """A discrete occurrence in time."""

    id: str                      # Unique identifier
    timestamp: datetime          # When it occurred
    actor: str | None           # Who/what caused it
    event_type: str             # Classification (commit, edit, create, etc.)
    data: dict                  # Event-specific payload
    metadata: dict              # Additional context

class EventStream(Protocol[T]):
    """
    Protocol for temporal event sources.

    Streams can be:
    - Pull-based (iterator) or push-based (async)
    - Bounded (finite) or unbounded (infinite)
    - Seekable (git history) or append-only (live log)
    """

    def classify_reality(self) -> Reality:
        """
        Classify the nature of this stream.

        Called before processing to determine strategy.
        """
        ...

    def is_bounded(self) -> bool:
        """Can we determine the stream will end?"""
        ...

    def estimate_size(self) -> int:
        """Approximate number of events (best effort)."""
        ...

    def has_cycles(self) -> bool:
        """Does this stream contain recursive/cyclic dependencies?"""
        ...

    def events(self,
               start: datetime | None = None,
               end: datetime | None = None,
               limit: int | None = None) -> Iterator[Event]:
        """
        Iterate events in temporal order.

        Args:
            start: Only events after this time
            end: Only events before this time
            limit: Maximum events to return
        """
        ...

    async def events_async(self,
                           start: datetime | None = None,
                           end: datetime | None = None,
                           limit: int | None = None) -> AsyncIterator[Event]:
        """Async variant for push-based streams."""
        ...

    def window(self, duration: timedelta) -> 'SlidingWindow':
        """
        Create a sliding window view of this stream.

        Returns a stream that processes events in overlapping windows.
        """
        ...

    def entropy_budget(self, depth: int = 0) -> float:
        """
        Calculate available entropy budget for processing.

        J-gent entropy budget: 1.0 / (depth + 1)
        """
        return 1.0 / (depth + 1)
```

### Sliding Window

```python
from datetime import timedelta

@dataclass(frozen=True)
class Window:
    """A temporal window of events."""

    start: datetime
    end: datetime
    events: tuple[Event, ...]

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    @property
    def event_count(self) -> int:
        return len(self.events)

class SlidingWindow:
    """
    A view of an event stream with overlapping windows.

    Example: 30-day windows, sliding by 7 days
    """

    def __init__(self,
                 stream: EventStream,
                 window_size: timedelta,
                 step_size: timedelta):
        self.stream = stream
        self.window_size = window_size
        self.step_size = step_size

    def windows(self) -> Iterator[Window]:
        """Iterate overlapping windows."""
        ...
```

---

## Concrete Implementations

### 1. GitStream: History as Event Stream

Git commit history is a **PROBABILISTIC** stream (bounded, analyzable, but complex).

```python
from dataclasses import dataclass
from git import Repo

@dataclass
class GitStream:
    """Git commit history as event stream."""

    repo_path: Path
    branch: str = "main"

    def classify_reality(self) -> Reality:
        """Git history is PROBABILISTIC."""
        return Reality.PROBABILISTIC

    def is_bounded(self) -> bool:
        """Git history is finite."""
        return True

    def estimate_size(self) -> int:
        """Count commits in branch."""
        repo = Repo(self.repo_path)
        return sum(1 for _ in repo.iter_commits(self.branch))

    def has_cycles(self) -> bool:
        """Git DAG has no cycles."""
        return False

    def events(self,
               start: datetime | None = None,
               end: datetime | None = None,
               limit: int | None = None) -> Iterator[Event]:
        """
        Iterate commits as events.

        Each commit becomes an Event with:
        - id: commit SHA
        - timestamp: commit timestamp
        - actor: author name
        - event_type: "commit"
        - data: {"message": ..., "diff": ..., "files": [...]}
        """
        repo = Repo(self.repo_path)
        commit_iter = repo.iter_commits(self.branch)

        count = 0
        for commit in commit_iter:
            # Filter by time
            commit_time = datetime.fromtimestamp(commit.committed_date)
            if start and commit_time < start:
                continue
            if end and commit_time > end:
                continue

            # Yield event
            yield Event(
                id=commit.hexsha,
                timestamp=commit_time,
                actor=commit.author.name,
                event_type="commit",
                data={
                    "message": commit.message,
                    "diff": commit.diff(commit.parents[0] if commit.parents else None),
                    "files": [item.a_path for item in commit.stats.files],
                    "stats": dict(commit.stats.files),
                },
                metadata={
                    "branch": self.branch,
                    "author_email": commit.author.email,
                    "committer": commit.committer.name,
                }
            )

            count += 1
            if limit and count >= limit:
                break
```

### 2. ObsidianStream: Vault Changes Over Time

Obsidian vault modifications tracked via git or filesystem timestamps.

```python
@dataclass
class ObsidianStream:
    """Obsidian vault changes as event stream."""

    vault_path: Path
    use_git: bool = True  # Use git history if available

    def classify_reality(self) -> Reality:
        """Obsidian stream is PROBABILISTIC."""
        return Reality.PROBABILISTIC

    def is_bounded(self) -> bool:
        """Vault history is finite."""
        return True

    def estimate_size(self) -> int:
        """Estimate events based on file count."""
        return sum(1 for _ in self.vault_path.rglob("*.md"))

    def events(self, **kwargs) -> Iterator[Event]:
        """
        Stream note creation/modification events.

        Events include:
        - note_created
        - note_modified
        - link_added
        - link_removed
        """
        if self.use_git and (self.vault_path / ".git").exists():
            # Use git history
            git_stream = GitStream(self.vault_path)
            for git_event in git_stream.events(**kwargs):
                # Transform git commits into note-level events
                for note_event in self._parse_note_events(git_event):
                    yield note_event
        else:
            # Use filesystem timestamps
            for note_path in sorted(self.vault_path.rglob("*.md")):
                stat = note_path.stat()
                yield Event(
                    id=str(note_path),
                    timestamp=datetime.fromtimestamp(stat.st_mtime),
                    actor=None,
                    event_type="note_modified",
                    data={"path": str(note_path), "size": stat.st_size},
                    metadata={"mtime": stat.st_mtime},
                )
```

### 3. FileSystemStream: Directory Changes

Watch filesystem for changes (can be **CHAOTIC** if unbounded).

```python
@dataclass
class FileSystemStream:
    """
    Filesystem changes as event stream.

    WARNING: Can be CHAOTIC if watching unbounded directories.
    """

    watch_path: Path
    patterns: list[str] = field(default_factory=lambda: ["**/*"])
    max_depth: int = 5

    def classify_reality(self) -> Reality:
        """
        Filesystem watching can be CHAOTIC.

        If watching root or very large directory, classify as CHAOTIC
        and collapse to Ground (refuse to process).
        """
        # Estimate directory depth
        if self.max_depth > 10:
            return Reality.CHAOTIC

        # Estimate file count
        try:
            file_count = sum(1 for _ in self.watch_path.rglob("*"))
            if file_count > 100_000:
                return Reality.CHAOTIC
        except OSError:
            return Reality.CHAOTIC

        return Reality.PROBABILISTIC

    def is_bounded(self) -> bool:
        """Filesystem snapshot is bounded, watching is not."""
        return False

    def events(self, **kwargs) -> Iterator[Event]:
        """
        One-time scan of current filesystem state.

        For continuous watching, use events_async().
        """
        for path in self.watch_path.rglob("*"):
            if path.is_file():
                stat = path.stat()
                yield Event(
                    id=str(path),
                    timestamp=datetime.fromtimestamp(stat.st_mtime),
                    actor=None,
                    event_type="file_exists",
                    data={"path": str(path), "size": stat.st_size},
                    metadata={"ctime": stat.st_ctime, "mtime": stat.st_mtime},
                )

    async def events_async(self, **kwargs) -> AsyncIterator[Event]:
        """
        Continuous filesystem watching (push-based).

        Uses inotify/FSEvents to watch for changes.
        WARNING: Can be unbounded. Respect entropy budget.
        """
        # Implementation uses watchdog library
        ...
```

---

## Integration with W-gents (Witness)

W-gents observe behavioral patterns. EventStreams provide temporal data.

### Temporal Witness

```python
from protocols.mirror.types import Antithesis, PatternType

class TemporalWitness:
    """
    W-gent that observes patterns across time windows.

    Compares behavior in different time periods to detect drift.
    """

    def __init__(self, stream: EventStream):
        self.stream = stream
        self.reality = stream.classify_reality()

    def observe_drift(self,
                      window_size: timedelta,
                      compare_periods: int = 2) -> list[Antithesis]:
        """
        Detect behavioral drift across time windows.

        Args:
            window_size: Size of each observation window (e.g., 30 days)
            compare_periods: How many periods to compare (2 = current vs previous)

        Returns:
            Antitheses describing detected drifts
        """
        # Refuse chaotic streams
        if self.reality == Reality.CHAOTIC:
            return [Antithesis(
                content="Stream is unbounded/chaotic",
                evidence=["Reality classification: CHAOTIC"],
                frequency=1.0,
                severity=1.0,
                pattern_type=PatternType.UNKNOWN,
            )]

        # Create sliding windows
        windowed = self.stream.window(window_size)
        windows = list(itertools.islice(windowed.windows(), compare_periods))

        if len(windows) < 2:
            return []  # Not enough data

        # Compare patterns between windows
        antitheses = []

        # Example: Compare commit frequency
        recent_window = windows[-1]
        previous_window = windows[-2]

        recent_rate = recent_window.event_count / recent_window.duration.days
        previous_rate = previous_window.event_count / previous_window.duration.days

        if abs(recent_rate - previous_rate) / previous_rate > 0.3:  # 30% change
            antitheses.append(Antithesis(
                content=f"Activity rate changed from {previous_rate:.1f} to {recent_rate:.1f} events/day",
                evidence=[
                    f"Period 1: {previous_window.event_count} events in {previous_window.duration.days} days",
                    f"Period 2: {recent_window.event_count} events in {recent_window.duration.days} days",
                ],
                frequency=recent_rate,
                severity=abs(recent_rate - previous_rate) / previous_rate,
                pattern_type=PatternType.UPDATE_FREQUENCY,
            ))

        return antitheses
```

---

## Semantic Momentum Tracking

The **semantic momentum** of a topic measures how its meaning changes over time.

### Theory

From Noether's theorem (conservation laws):

```
p⃗ = m · v⃗

Where:
  p⃗ = momentum vector
  m = mass (attention/influence weight)
  v⃗ = velocity (rate of semantic change)
```

A topic's meaning is **conserved** if its momentum remains constant. If momentum changes without explicit evolution (no new principles), we detect an **entropy leak**—meaning is drifting.

### Implementation

```python
import numpy as np
from sentence_transformers import SentenceTransformer

@dataclass(frozen=True)
class SemanticMomentum:
    """The motion of meaning through time."""

    topic: str
    mass: float              # Attention density (references/mentions)
    velocity: np.ndarray     # Embedding drift vector
    timestamp: datetime

    @property
    def momentum(self) -> np.ndarray:
        """p⃗ = m · v⃗"""
        return self.mass * self.velocity

    @property
    def magnitude(self) -> float:
        """||p⃗||"""
        return np.linalg.norm(self.momentum)

    def is_conserved(self, threshold: float = 0.1) -> bool:
        """
        Is momentum conserved (stable meaning)?

        Returns True if velocity magnitude < threshold.
        """
        return np.linalg.norm(self.velocity) < threshold

class SemanticMomentumTracker:
    """
    Track semantic momentum across event streams.

    Uses embeddings to measure how topic meanings drift over time.
    """

    def __init__(self,
                 model_name: str = "all-MiniLM-L6-v2",
                 window_size: timedelta = timedelta(days=30)):
        self.model = SentenceTransformer(model_name)
        self.window_size = window_size

    def track_topic(self,
                    stream: EventStream,
                    topic: str) -> list[SemanticMomentum]:
        """
        Track a topic's semantic momentum across time.

        Args:
            stream: Event stream to analyze
            topic: Topic keyword to track

        Returns:
            List of SemanticMomentum observations (one per window)
        """
        # Create sliding windows
        windowed = stream.window(self.window_size)

        momentum_history = []
        previous_embedding = None

        for window in windowed.windows():
            # Extract topic mentions in this window
            mentions = self._extract_topic_mentions(window, topic)

            if not mentions:
                continue

            # Calculate mass (attention in this window)
            mass = len(mentions)

            # Calculate average embedding for topic in this window
            embeddings = self.model.encode(mentions)
            avg_embedding = np.mean(embeddings, axis=0)

            # Calculate velocity (embedding drift since previous window)
            if previous_embedding is not None:
                velocity = avg_embedding - previous_embedding
            else:
                velocity = np.zeros_like(avg_embedding)

            # Record momentum
            momentum_history.append(SemanticMomentum(
                topic=topic,
                mass=mass,
                velocity=velocity,
                timestamp=window.end,
            ))

            previous_embedding = avg_embedding

        return momentum_history

    def detect_entropy_leaks(self,
                            momentum_history: list[SemanticMomentum],
                            threshold: float = 0.15) -> list[str]:
        """
        Detect entropy leaks (momentum violations).

        An entropy leak occurs when:
        1. Momentum is not conserved (high velocity)
        2. No explicit principle evolution explains the drift

        Args:
            momentum_history: Momentum observations over time
            threshold: Velocity magnitude threshold for conservation

        Returns:
            List of detected entropy leaks (descriptions)
        """
        leaks = []

        for i, momentum in enumerate(momentum_history):
            if not momentum.is_conserved(threshold):
                leaks.append(
                    f"Entropy leak at {momentum.timestamp}: "
                    f"Topic '{momentum.topic}' drifted with velocity {momentum.magnitude:.3f}"
                )

        return leaks

    def _extract_topic_mentions(self, window: Window, topic: str) -> list[str]:
        """Extract sentences/paragraphs mentioning the topic."""
        mentions = []
        for event in window.events:
            # Extract text from event data
            if "message" in event.data:
                text = event.data["message"]
                if topic.lower() in text.lower():
                    mentions.append(text)
        return mentions
```

---

## Entropy Budget Management

J-gents enforce **entropy budgets** to prevent runaway computation.

```python
from dataclasses import dataclass

@dataclass
class EntropyBudget:
    """
    Computational freedom budget for stream processing.

    Budget diminishes with recursion depth:
        budget(0) = 1.00  (full freedom)
        budget(1) = 0.50
        budget(2) = 0.33
        budget(3) = 0.25  (minimal freedom)
    """

    depth: int
    max_depth: int = 3

    @property
    def remaining(self) -> float:
        """Remaining entropy budget."""
        if self.depth >= self.max_depth:
            return 0.0
        return 1.0 / (self.depth + 1)

    def can_afford(self, cost: float) -> bool:
        """Can we afford this computation?"""
        return self.remaining >= cost

    def descend(self) -> 'EntropyBudget':
        """Create child budget (recursion)."""
        return EntropyBudget(
            depth=self.depth + 1,
            max_depth=self.max_depth,
        )

def process_stream_with_budget(stream: EventStream,
                               budget: EntropyBudget) -> list[Event]:
    """
    Process stream respecting entropy budget.

    Args:
        stream: Event stream to process
        budget: Available entropy budget

    Returns:
        Processed events (may be truncated if budget exhausted)
    """
    reality = stream.classify_reality()

    # CHAOTIC streams collapse to Ground
    if reality == Reality.CHAOTIC:
        print(f"Stream classified as CHAOTIC, collapsing to Ground")
        return []

    # DETERMINISTIC streams execute directly
    if reality == Reality.DETERMINISTIC:
        return list(stream.events(limit=100))  # Bounded limit

    # PROBABILISTIC streams require budget
    if not budget.can_afford(0.3):
        print(f"Insufficient entropy budget ({budget.remaining:.2f}), deferring")
        return []

    # Process with child budget
    child_budget = budget.descend()
    events = []

    for event in stream.events(limit=1000):
        if not child_budget.can_afford(0.01):
            print(f"Entropy budget exhausted at {len(events)} events")
            break
        events.append(event)

    return events
```

---

## Composability

EventStreams are **morphisms** in the category of temporal observations.

### Stream Composition

```python
class ComposedStream:
    """
    Compose multiple event streams into a single unified stream.

    Events are merged and sorted by timestamp.
    """

    def __init__(self, *streams: EventStream):
        self.streams = streams

    def classify_reality(self) -> Reality:
        """Composition inherits most chaotic reality."""
        realities = [s.classify_reality() for s in self.streams]
        if Reality.CHAOTIC in realities:
            return Reality.CHAOTIC
        if Reality.PROBABILISTIC in realities:
            return Reality.PROBABILISTIC
        return Reality.DETERMINISTIC

    def events(self, **kwargs) -> Iterator[Event]:
        """Merge events from all streams, sorted by timestamp."""
        import heapq

        # Create iterators for all streams
        iterators = [s.events(**kwargs) for s in self.streams]

        # Merge using heap (priority queue)
        for event in heapq.merge(*iterators, key=lambda e: e.timestamp):
            yield event
```

### Stream Transformations (Functors)

```python
class FilteredStream:
    """Filter events by predicate (functor)."""

    def __init__(self,
                 stream: EventStream,
                 predicate: Callable[[Event], bool]):
        self.stream = stream
        self.predicate = predicate

    def events(self, **kwargs) -> Iterator[Event]:
        for event in self.stream.events(**kwargs):
            if self.predicate(event):
                yield event

class MappedStream:
    """Transform events (functor)."""

    def __init__(self,
                 stream: EventStream,
                 transform: Callable[[Event], Event]):
        self.stream = stream
        self.transform = transform

    def events(self, **kwargs) -> Iterator[Event]:
        for event in self.stream.events(**kwargs):
            yield self.transform(event)
```

---

## Usage Examples

### Example 1: Track Git Commit Activity Drift

```python
# Create git stream
git_stream = GitStream(Path("~/projects/my-app"))

# Classify reality
print(f"Reality: {git_stream.classify_reality()}")  # PROBABILISTIC

# Create temporal witness
witness = TemporalWitness(git_stream)

# Detect drift over 30-day windows
antitheses = witness.observe_drift(
    window_size=timedelta(days=30),
    compare_periods=2,
)

for antithesis in antitheses:
    print(f"Drift detected: {antithesis.content}")
```

### Example 2: Track Semantic Momentum of "Auth"

```python
# Create git stream
git_stream = GitStream(Path("~/projects/my-app"))

# Create momentum tracker
tracker = SemanticMomentumTracker(window_size=timedelta(days=14))

# Track "authentication" topic
momentum_history = tracker.track_topic(git_stream, "authentication")

# Detect entropy leaks
leaks = tracker.detect_entropy_leaks(momentum_history, threshold=0.15)

for leak in leaks:
    print(f"⚠️  {leak}")
```

### Example 3: Compose Multiple Streams

```python
# Combine git history and filesystem changes
git_stream = GitStream(Path("~/projects/my-app"))
fs_stream = FileSystemStream(Path("~/projects/my-app/docs"))

# Compose
composed = ComposedStream(git_stream, fs_stream)

# Process with entropy budget
budget = EntropyBudget(depth=0, max_depth=3)
events = process_stream_with_budget(composed, budget)

print(f"Processed {len(events)} events")
```

---

## Design Principles Applied

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Clean protocol interface, clear purpose (temporal observation) |
| **Curated** | Three stream types cover 90% of cases; avoid proliferation |
| **Composable** | Streams compose (ComposedStream), transform (functors), window (SlidingWindow) |
| **Generative** | Protocol spec generates concrete implementations |
| **Heterarchical** | Streams can be pull (sync) or push (async), functional or autonomous |
| **J-gent Integration** | Reality classification, entropy budgets, lazy promises |

---

## Anti-Patterns

### What NOT to Do

1. **Unbounded Streams Without Classification**
   - Always classify reality before processing
   - Collapse CHAOTIC streams to Ground

2. **Eager Consumption**
   - Don't materialize entire stream upfront
   - Use lazy iteration (generators/iterators)

3. **Ignoring Entropy Budget**
   - Respect budget at every recursion level
   - Fail fast when budget exhausted

4. **Mixing Sync/Async Carelessly**
   - Choose one execution model per context
   - Don't block async loops with sync streams

5. **Over-Abstracting**
   - Three concrete implementations (Git, Obsidian, FileSystem) are enough
   - Don't create streams for every data source

---

## Future Extensions

### Phase 3 (Kairos Controller)

- **Cost Functions**: C(t) = (η·S + γ·L) / A for opportune moment detection
- **Intervention Timing**: Use stream momentum to determine when to surface tensions

### Phase 4 (Autopoietic Loop)

- **Sublation Loop**: Synthesis → new Thesis → new EventStream observation
- **Ergodicity Measurement**: Does the system explore its full state space?

---

## See Also

- [mirror.md](mirror.md) — Mirror Protocol overview
- [../j-gents/README.md](../j-gents/README.md) — J-gent reality classification
- [../j-gents/lazy.md](../j-gents/lazy.md) — Lazy promises and accountability
- [../j-gents/stability.md](../j-gents/stability.md) — Entropy budgets and Chaosmonger

---

*"Time is not a container we fill—it is a river we witness."*
