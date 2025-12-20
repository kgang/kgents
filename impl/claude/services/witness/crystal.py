"""
ExperienceCrystal: The Atomic Unit of Witnessed Experience.

The Experience Crystal transforms ephemeral work events into durable,
navigable memory. Unlike raw Thought streams, crystals have:
- Semantic handles (topics, entities, mood) for retrieval
- Narrative synthesis (what happened, what it means)
- Topological grounding (where in the codebase)
- Temporal bounds (when it began and ended)

The Insight (from brainstorming/2025-12-19-the-witness-and-the-muse.md):
    "Experience Crystallization—the transformation of ephemeral events
     into durable, navigable memory."

Philosophy:
    A crystal is not a log. A log records what happened.
    A crystal captures what it meant.

See: plans/witness-muse-implementation.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from .polynomial import Thought

# =============================================================================
# MoodVector: Affective Signature
# =============================================================================


@dataclass(frozen=True)
class MoodVector:
    """
    Seven-dimensional affective signature of a work session.

    Each dimension is a float in [0, 1]:
    - warmth: Cold/clinical ↔ Warm/engaging (connection)
    - weight: Light/playful ↔ Heavy/serious (gravity)
    - tempo: Slow/deliberate ↔ Fast/urgent (pace)
    - texture: Smooth/flowing ↔ Rough/struggling (friction)
    - brightness: Dim/frustrated ↔ Bright/joyful (affect)
    - saturation: Muted/routine ↔ Vivid/intense (engagement)
    - complexity: Simple/focused ↔ Complex/branching (scope)

    The Insight: Qualia space enables cross-modal retrieval.
    "Find sessions that felt like this one" → vector similarity.

    Example:
        >>> mood = MoodVector.from_thoughts(thoughts)
        >>> mood.brightness  # 0.8 if lots of success markers
        >>> mood.similarity(other_mood)  # Cosine similarity
    """

    warmth: float = 0.5
    weight: float = 0.5
    tempo: float = 0.5
    texture: float = 0.5
    brightness: float = 0.5
    saturation: float = 0.5
    complexity: float = 0.5

    def __post_init__(self) -> None:
        """Validate all dimensions are in [0, 1]."""
        for dim in (
            "warmth",
            "weight",
            "tempo",
            "texture",
            "brightness",
            "saturation",
            "complexity",
        ):
            value = getattr(self, dim)
            if not 0.0 <= value <= 1.0:
                object.__setattr__(self, dim, max(0.0, min(1.0, value)))

    @classmethod
    def neutral(cls) -> MoodVector:
        """Return a neutral mood (all 0.5)."""
        return cls()

    @classmethod
    def from_thoughts(cls, thoughts: list[Thought]) -> MoodVector:
        """
        Derive mood from a thought stream.

        Signal aggregation (Pattern 4 from crown-jewel-patterns.md):
        Multiple weak signals → affective signature.
        """
        if not thoughts:
            return cls.neutral()

        # Count signal markers - check both content AND tags
        total = len(thoughts)
        failures = sum(
            1
            for t in thoughts
            if "fail" in t.content.lower()
            or "error" in t.content.lower()
            or "failure" in str(t.tags).lower()
        )
        successes = sum(
            1
            for t in thoughts
            if "pass" in t.content.lower()
            or "success" in t.content.lower()
            or "success" in str(t.tags).lower()
        )
        commits = sum(
            1 for t in thoughts if "commit" in str(t.tags).lower() or "commit" in t.content.lower()
        )
        tests = sum(1 for t in thoughts if "test" in str(t.tags).lower())

        # Derive dimensions from signals
        brightness = 0.5 + 0.3 * ((successes - failures) / max(total, 1))
        brightness = max(0.0, min(1.0, brightness))

        # Tempo from event density (events per minute if we have timestamps)
        tempo = min(1.0, total / 50)  # Normalize to 50 events = full tempo

        # Weight from test/commit ratio (more tests = heavier/more serious)
        weight = 0.3 + 0.4 * (tests / max(total, 1))

        # Complexity from unique sources
        sources = set(t.source for t in thoughts)
        complexity = min(1.0, len(sources) / 5)  # 5 sources = full complexity

        # Saturation from activity level
        saturation = min(1.0, total / 30)  # 30 events = full saturation

        # Texture from failure ratio (more failures = rougher)
        texture = 0.5 + 0.3 * (failures / max(total, 1))
        texture = max(0.0, min(1.0, texture))

        # Warmth from commits (personal investment)
        warmth = 0.4 + 0.4 * (commits / max(total, 1))

        return cls(
            warmth=warmth,
            weight=weight,
            tempo=tempo,
            texture=texture,
            brightness=brightness,
            saturation=saturation,
            complexity=complexity,
        )

    def similarity(self, other: MoodVector) -> float:
        """
        Cosine similarity to another mood vector.

        Returns float in [-1, 1] (usually [0, 1] for positive values).
        Special case: Two zero vectors are considered identical (similarity 1.0).
        """
        import math

        a = [
            self.warmth,
            self.weight,
            self.tempo,
            self.texture,
            self.brightness,
            self.saturation,
            self.complexity,
        ]
        b = [
            other.warmth,
            other.weight,
            other.tempo,
            other.texture,
            other.brightness,
            other.saturation,
            other.complexity,
        ]

        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))

        # Edge case: zero vectors are identical
        if mag_a == 0 and mag_b == 0:
            return 1.0
        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot / (mag_a * mag_b)

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary for serialization."""
        return {
            "warmth": self.warmth,
            "weight": self.weight,
            "tempo": self.tempo,
            "texture": self.texture,
            "brightness": self.brightness,
            "saturation": self.saturation,
            "complexity": self.complexity,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> MoodVector:
        """Create from dictionary."""
        return cls(
            warmth=data.get("warmth", 0.5),
            weight=data.get("weight", 0.5),
            tempo=data.get("tempo", 0.5),
            texture=data.get("texture", 0.5),
            brightness=data.get("brightness", 0.5),
            saturation=data.get("saturation", 0.5),
            complexity=data.get("complexity", 0.5),
        )

    @property
    def dominant_quality(self) -> str:
        """Return the most prominent quality."""
        dims = {
            "warmth": self.warmth,
            "weight": self.weight,
            "tempo": self.tempo,
            "texture": self.texture,
            "brightness": self.brightness,
            "saturation": self.saturation,
            "complexity": self.complexity,
        }
        # Find furthest from neutral (0.5)
        return max(dims.keys(), key=lambda k: abs(dims[k] - 0.5))


# =============================================================================
# TopologySnapshot: Codebase Position
# =============================================================================


@dataclass(frozen=True)
class TopologySnapshot:
    """
    Snapshot of codebase topology at crystallization time.

    Captures:
    - Primary path: Where most activity happened
    - Heat map: Relative activity by path
    - Dependencies: Files touched together

    The Insight: Code has geography. Sessions have territory.
    """

    primary_path: str = "."
    heat: dict[str, float] = field(default_factory=dict)  # path → activity level [0, 1]
    dependencies: frozenset[tuple[str, str]] = field(
        default_factory=frozenset
    )  # (path_a, path_b) touched together

    @classmethod
    def from_thoughts(cls, thoughts: list[Thought]) -> TopologySnapshot:
        """
        Derive topology from thought stream.

        Extracts paths from file events and builds heat map.
        """
        path_counts: dict[str, int] = {}
        dependency_pairs: set[tuple[str, str]] = set()

        # Extract paths from file-related thoughts
        for thought in thoughts:
            # Look for file paths in content
            if thought.source == "filesystem" or "file" in str(thought.tags).lower():
                # Simple heuristic: content often has "path: /foo/bar" or "Edited: foo.py"
                content = thought.content
                # Try to extract path-like strings
                words = content.split()
                for word in words:
                    if (
                        "/" in word
                        or word.endswith(".py")
                        or word.endswith(".ts")
                        or word.endswith(".tsx")
                    ):
                        clean = word.strip("():,")
                        if clean:
                            path_counts[clean] = path_counts.get(clean, 0) + 1

        if not path_counts:
            return cls()

        # Normalize to heat map
        max_count = max(path_counts.values())
        heat = {path: count / max_count for path, count in path_counts.items()}

        # Primary path is most active
        primary = max(path_counts.keys(), key=lambda p: path_counts[p])

        # Dependencies: paths appearing in same thought
        # (Simplified—would need more sophisticated analysis for real deps)
        paths = list(path_counts.keys())
        for i, p1 in enumerate(paths):
            for p2 in paths[i + 1 :]:
                if path_counts[p1] > 0 and path_counts[p2] > 0:
                    dependency_pairs.add((min(p1, p2), max(p1, p2)))

        return cls(
            primary_path=primary,
            heat=heat,
            dependencies=frozenset(dependency_pairs),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "primary_path": self.primary_path,
            "heat": self.heat,
            "dependencies": list(self.dependencies),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TopologySnapshot:
        """Create from dictionary."""
        deps = data.get("dependencies", [])
        return cls(
            primary_path=data.get("primary_path", "."),
            heat=data.get("heat", {}),
            dependencies=frozenset(tuple(d) for d in deps if len(d) == 2),
        )


# =============================================================================
# Narrative: Synthesized Meaning
# =============================================================================


@dataclass(frozen=True)
class Narrative:
    """
    Synthesized narrative from a work session.

    Created via K-gent LLM integration (or fallback template).
    """

    summary: str  # 1-2 sentence summary
    themes: tuple[str, ...] = ()  # Major themes detected
    highlights: tuple[str, ...] = ()  # Key moments worth remembering
    dramatic_question: str = ""  # What was at stake?

    @classmethod
    def template_fallback(cls, thoughts: list[Thought]) -> Narrative:
        """
        Template fallback when LLM unavailable.

        Graceful degradation (from meta.md):
        "Template fallbacks make CLI commands work without LLM"
        """
        if not thoughts:
            return cls(summary="Empty session—no activity recorded.")

        # Extract unique sources
        sources = sorted(set(t.source for t in thoughts))
        sources_str = ", ".join(sources)

        # Count by tag categories
        tags_flat = [tag for t in thoughts for tag in t.tags]
        tag_summary = ""
        if tags_flat:
            from collections import Counter

            top_tags = Counter(tags_flat).most_common(3)
            tag_summary = ", ".join(f"{tag}" for tag, _ in top_tags)

        summary = f"Session with {len(thoughts)} observations from {sources_str}."
        if tag_summary:
            summary += f" Primary activity: {tag_summary}."

        # Themes from most common tags
        themes = tuple(tag for tag, _ in Counter(tags_flat).most_common(3)) if tags_flat else ()

        # Highlights from first/last thoughts
        highlights: tuple[str, ...] = ()
        if thoughts:
            first = thoughts[0].content[:50]
            last = thoughts[-1].content[:50]
            highlights = (f"Started: {first}", f"Ended: {last}")

        return cls(
            summary=summary,
            themes=themes,
            highlights=highlights,
            dramatic_question="What work was accomplished?",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "summary": self.summary,
            "themes": list(self.themes),
            "highlights": list(self.highlights),
            "dramatic_question": self.dramatic_question,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Narrative:
        """Create from dictionary."""
        return cls(
            summary=data.get("summary", ""),
            themes=tuple(data.get("themes", [])),
            highlights=tuple(data.get("highlights", [])),
            dramatic_question=data.get("dramatic_question", ""),
        )


# =============================================================================
# ExperienceCrystal: The Atomic Memory Unit
# =============================================================================


@dataclass(frozen=True)
class ExperienceCrystal:
    """
    The atomic unit of The Witness's memory.

    Unlike D-gent's generic storage, ExperienceCrystals are
    structured for retrieval, reflection, and cross-session learning.

    A crystal captures:
    - WHAT happened (timeline of thoughts)
    - WHAT it means (narrative synthesis)
    - WHERE it happened (topology)
    - HOW it felt (mood vector)
    - WHEN it crystallized

    Example:
        >>> crystal = ExperienceCrystal.from_thoughts(thoughts, session_id="abc")
        >>> crystal.mood.brightness  # Was it a good session?
        >>> crystal.topics  # What was worked on?
        >>> crystal.as_memory()  # Project to D-gent for storage
    """

    # Identity
    crystal_id: str = field(default_factory=lambda: f"crystal-{uuid4().hex[:12]}")
    session_id: str = ""

    # Timeline
    thoughts: tuple[Thought, ...] = ()
    markers: tuple[str, ...] = ()  # User-defined significant moments
    started_at: datetime | None = None
    ended_at: datetime | None = None

    # Synthesis
    narrative: Narrative = field(default_factory=lambda: Narrative(summary=""))
    topology: TopologySnapshot = field(default_factory=TopologySnapshot)
    mood: MoodVector = field(default_factory=MoodVector.neutral)

    # Semantic handles for retrieval
    topics: frozenset[str] = field(default_factory=frozenset)
    entities: frozenset[str] = field(default_factory=frozenset)

    # Metrics
    complexity: float = 0.0  # Session complexity score [0, 1]
    crystallized_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_thoughts(
        cls,
        thoughts: list[Thought],
        session_id: str = "",
        markers: list[str] | None = None,
        narrative: Narrative | None = None,
    ) -> ExperienceCrystal:
        """
        Create crystal from thought stream.

        This is the primary crystallization path. K-gent narrative
        synthesis is async and may be provided separately.
        """
        if not thoughts:
            return cls(
                session_id=session_id,
                narrative=narrative or Narrative(summary="Empty crystal—no thoughts."),
                markers=tuple(markers or []),
            )

        # Derive components
        mood = MoodVector.from_thoughts(thoughts)
        topology = TopologySnapshot.from_thoughts(thoughts)
        narrative_final = narrative or Narrative.template_fallback(thoughts)

        # Extract topics from tags and sources
        all_tags: set[str] = set()
        all_sources: set[str] = set()
        for thought in thoughts:
            all_tags.update(thought.tags)
            all_sources.add(thought.source)
        topics = frozenset(all_tags | all_sources)

        # Extract entities (simplified—files mentioned)
        entities_set: set[str] = set()
        for thought in thoughts:
            for word in thought.content.split():
                if word.endswith(".py") or word.endswith(".ts") or word.endswith(".tsx"):
                    entities_set.add(word.strip("():,"))
        entities = frozenset(entities_set)

        # Timestamps
        started_at = thoughts[0].timestamp if thoughts else None
        ended_at = thoughts[-1].timestamp if thoughts else None

        # Complexity from mood
        complexity = mood.complexity

        return cls(
            session_id=session_id,
            thoughts=tuple(thoughts),
            markers=tuple(markers or []),
            started_at=started_at,
            ended_at=ended_at,
            narrative=narrative_final,
            topology=topology,
            mood=mood,
            topics=topics,
            entities=entities,
            complexity=complexity,
        )

    def as_memory(self) -> dict[str, Any]:
        """
        Project into D-gent-compatible format for long-term storage.

        Returns a dict ready for DgentEntry creation.
        """
        return {
            "key": f"witness:crystal:{self.crystal_id}",
            "value": self.to_json(),
            "metadata": {
                "type": "experience_crystal",
                "session_id": self.session_id,
                "topics": list(self.topics),
                "entities": list(self.entities),
                "mood": self.mood.to_dict(),
                "complexity": self.complexity,
                "crystallized_at": self.crystallized_at.isoformat(),
            },
        }

    def to_json(self) -> dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "crystal_id": self.crystal_id,
            "session_id": self.session_id,
            "thoughts": [
                {
                    "content": t.content,
                    "source": t.source,
                    "tags": list(t.tags),
                    "timestamp": t.timestamp.isoformat() if t.timestamp else None,
                }
                for t in self.thoughts
            ],
            "markers": list(self.markers),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "narrative": self.narrative.to_dict(),
            "topology": self.topology.to_dict(),
            "mood": self.mood.to_dict(),
            "topics": list(self.topics),
            "entities": list(self.entities),
            "complexity": self.complexity,
            "crystallized_at": self.crystallized_at.isoformat(),
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ExperienceCrystal:
        """Create from JSON dictionary."""
        from datetime import datetime

        thoughts = [
            Thought(
                content=t["content"],
                source=t["source"],
                tags=tuple(t.get("tags", [])),
                timestamp=datetime.fromisoformat(t["timestamp"])
                if t.get("timestamp")
                else datetime.now(),
            )
            for t in data.get("thoughts", [])
        ]

        started_at = datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None
        ended_at = datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None
        crystallized_at = (
            datetime.fromisoformat(data["crystallized_at"])
            if data.get("crystallized_at")
            else datetime.now()
        )

        return cls(
            crystal_id=data.get("crystal_id", f"crystal-{uuid4().hex[:12]}"),
            session_id=data.get("session_id", ""),
            thoughts=tuple(thoughts),
            markers=tuple(data.get("markers", [])),
            started_at=started_at,
            ended_at=ended_at,
            narrative=Narrative.from_dict(data.get("narrative", {})),
            topology=TopologySnapshot.from_dict(data.get("topology", {})),
            mood=MoodVector.from_dict(data.get("mood", {})),
            topics=frozenset(data.get("topics", [])),
            entities=frozenset(data.get("entities", [])),
            complexity=data.get("complexity", 0.0),
            crystallized_at=crystallized_at,
        )

    @property
    def duration_minutes(self) -> float | None:
        """Duration of the crystallized session in minutes."""
        if self.started_at and self.ended_at:
            return (self.ended_at - self.started_at).total_seconds() / 60
        return None

    @property
    def thought_count(self) -> int:
        """Number of thoughts in this crystal."""
        return len(self.thoughts)

    def __repr__(self) -> str:
        duration = self.duration_minutes
        duration_str = f"{duration:.1f}min" if duration else "?"
        return (
            f"ExperienceCrystal("
            f"id={self.crystal_id[:8]}..., "
            f"thoughts={self.thought_count}, "
            f"duration={duration_str}, "
            f"mood={self.mood.dominant_quality})"
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ExperienceCrystal",
    "MoodVector",
    "TopologySnapshot",
    "Narrative",
]
