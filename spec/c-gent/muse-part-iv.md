# Creative Muse Protocol: Part IV — Hierarchical Works & Persistent Entities

> *"A TV show is not a file. An album is not 12 songs. These are worlds with inhabitants, rules, and recurring magic."*

**Status:** Active Extension
**Part of:** Creative Muse Protocol v2.0 (C-gent)
**Dependencies:** Main muse.md (The Co-Creative Engine)
**Relationship:** This part provides **data structures** that the co-creative engine **operates on**. The dialectic (amplify → select → contradict → defend) applies at every level of the hierarchy.

---

## Purpose

This section extends the Creative Muse Protocol to support **long-form, hierarchical creative works**—TV shows, album series, novel trilogies, video franchises—where **persistent entities** (characters, locations, formats, motifs) recur across episodes, and **creative coherence** must flow across structural boundaries.

**Why this matters for the co-creative engine**: The dialectic from muse.md (amplify → select → contradict → defend) happens at EVERY level. But without hierarchy, you'd iterate 50x on the whole show, losing the ability to focus. Hierarchy enables **focused iteration**: 30 iterations on a character, 50 iterations on a scene, 20 iterations on an episode structure—each operating within constraints inherited from above.

## Core Insight

**Hierarchical works are sheaves of sheaves**: Each level (series → season → episode → scene → beat) has its own VisionSheaf, and coherence flows **downward** (parent constraints propagate) while feedback flows **upward** (child discoveries inform parent). Persistent entities are the **invariants** that create identity across the hierarchy.

**The iteration principle at scale**: A breakthrough TV show isn't 50 iterations on "the show." It's:
- **50 iterations** on the series premise
- **30 iterations** on each major character
- **20 iterations** per season arc
- **15 iterations** per episode concept
- **50 iterations** per pivotal scene

Total: hundreds of micro-dialectics, each constrained by parent decisions, each potentially propagating breakthroughs upward.

---

## I. WorkHierarchy: Series as Sheaf Towers

### The Type

```python
@dataclass(frozen=True)
class Work:
    """A unit of creative output at any hierarchical level."""
    id: WorkId
    title: str
    kind: WorkKind          # SERIES, SEASON, EPISODE, SCENE, BEAT
    parent: WorkId | None   # None for root
    vision: CreativeVisionSheaf
    entities: frozenset[EntityRef]   # Characters, locations, etc.
    metadata: WorkMetadata  # Duration, genre, format constraints

class WorkKind(Enum):
    SERIES = "series"       # e.g., "Breaking Bad"
    SEASON = "season"       # e.g., "Season 3"
    EPISODE = "episode"     # e.g., "Ozymandias"
    SCENE = "scene"         # e.g., "Desert confrontation"
    BEAT = "beat"           # e.g., "Walt's phone call"

    # Non-episodic
    ALBUM = "album"
    TRACK = "track"
    MOVEMENT = "movement"

    # Novel
    SERIES_BOOK = "series_book"
    VOLUME = "volume"
    CHAPTER = "chapter"
    SECTION = "section"

@dataclass
class WorkHierarchy:
    """
    A tree of Works with sheaf coherence at each level.

    Laws:
    - Every child's vision MUST be compatible with parent's vision
    - Entity references resolve upward (characters defined at series level)
    - Feedback propagates upward (discoveries in episodes inform series)
    """
    root: Work
    children: dict[WorkId, WorkHierarchy]

    def find(self, work_id: WorkId) -> Work | None:
        """DFS search for work."""
        ...

    def check_coherence(self) -> CoherenceReport:
        """Verify vision compatibility down the tree."""
        ...

    def propagate_constraint(self, constraint: VisionConstraint) -> None:
        """Push constraint from parent to all descendants."""
        ...

    def bubble_feedback(self, work_id: WorkId, feedback: CreativeFeedback) -> None:
        """Pull insight from child up to ancestors."""
        ...
```

### Coherence Flow: Downward & Upward

```
                    SERIES
                   (Vision₀)
                   "Dark comedy, moral decay"
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    SEASON 1      SEASON 2      SEASON 3
    (Vision₁)     (Vision₂)     (Vision₃)
    "Setup"       "Descent"     "Reckoning"
        │             │             │
    ┌───┴───┐     ┌───┴───┐     ┌───┴───┐
    ▼       ▼     ▼       ▼     ▼       ▼
  EP 1    EP 2  EP 3    EP 4  EP 5    EP 6
  (V₁₁)   (V₁₂) (V₂₁)   (V₂₂) (V₃₁)   (V₃₂)

DOWNWARD (constraints):
  Series vision constraints → Season visions MUST satisfy
  Season constraints → Episode visions MUST satisfy

UPWARD (feedback):
  Episode insight (e.g., "Walt's pride is the real enemy")
    → Season 2 vision refines
    → Series vision sharpens
```

**Gluing Condition**: For any two siblings (e.g., Episode 3 and Episode 4 in Season 2), their visions must be compatible under the parent's (Season 2's) gluing map.

### Example: TV Show Hierarchy

```python
# Breaking Bad series
series = Work(
    id=WorkId("bb-series"),
    title="Breaking Bad",
    kind=WorkKind.SERIES,
    parent=None,
    vision=CreativeVisionSheaf(
        theme="Moral decay through pride",
        tone="Dark, tense, blackly comic",
        constraints=["Every action has consequences", "No redemption arcs"],
        aesthetic=AestheticVector(darkness=0.8, tension=0.9, humor=0.4),
    ),
    entities=frozenset({
        EntityRef("character:walter-white"),
        EntityRef("character:jesse-pinkman"),
        EntityRef("location:lab"),
        EntityRef("format:cold-open"),
    }),
)

season_3 = Work(
    id=WorkId("bb-s3"),
    title="Season 3",
    kind=WorkKind.SEASON,
    parent=WorkId("bb-series"),
    vision=CreativeVisionSheaf(
        theme="Consequences cascade—family fractures",
        tone="Bleaker, relationship focus",
        constraints=["Walt loses Skyler", "Gus appears untouchable"],
        aesthetic=AestheticVector(darkness=0.85, tension=0.95, humor=0.3),
    ),
    entities=frozenset({
        EntityRef("character:skyler-white"),
        EntityRef("character:gus-fring"),
    }),
)

episode_10 = Work(
    id=WorkId("bb-s3e10"),
    title="Fly",
    kind=WorkKind.EPISODE,
    parent=WorkId("bb-s3"),
    vision=CreativeVisionSheaf(
        theme="Obsession as symptom of guilt",
        tone="Bottle episode, introspective",
        constraints=["One location", "Character study over plot"],
        aesthetic=AestheticVector(darkness=0.6, tension=0.5, humor=0.5),
    ),
    entities=frozenset({
        EntityRef("location:lab"),
        EntityRef("motif:fly-as-guilt"),
    }),
)
```

**Coherence Check**:
- Episode 10's theme ("guilt") is compatible with Season 3's theme ("consequences")
- Episode 10's aesthetic is **softer** than Season 3—this is **allowed** (local variation within bounds)
- Episode 10 references `location:lab` defined at series level—**resolves upward**

### Iteration Budgets by Level

The co-creative engine (muse.md) operates at each level with different iteration counts. Higher levels need more iterations because decisions cascade.

```python
ITERATION_BUDGETS = {
    # TV/Video
    WorkKind.SERIES: {
        "premise": 50,           # 50 iterations to nail the core concept
        "tone_guide": 30,        # 30 iterations on aesthetic
        "world_rules": 20,       # 20 iterations on what's possible
    },
    WorkKind.SEASON: {
        "arc": 20,               # 20 iterations on season through-line
        "theme": 15,             # 15 iterations on seasonal theme
        "structure": 10,         # 10 iterations on episode order/pacing
    },
    WorkKind.EPISODE: {
        "concept": 15,           # 15 iterations on episode premise
        "a_story": 20,           # 20 iterations on main plot
        "b_story": 15,           # 15 iterations on subplot
        "cold_open": 30,         # 30 iterations—cold opens are key hooks
    },
    WorkKind.SCENE: {
        "pivotal": 50,           # 50 iterations on pivotal scenes
        "standard": 15,          # 15 iterations on standard scenes
        "transition": 5,         # 5 iterations on transitions
    },
    WorkKind.BEAT: {
        "dialogue": 20,          # 20 iterations per key line
        "action": 10,            # 10 iterations on blocking
    },

    # Music/Album
    WorkKind.ALBUM: {
        "concept": 50,           # 50 iterations on album vision
        "sequencing": 30,        # 30 iterations on track order
        "title": 100,            # 100 title options (per muse.md)
    },
    WorkKind.TRACK: {
        "hook": 200,             # 200 hook options (per muse.md)
        "verse": 50,             # 50 verse iterations
        "bridge": 30,            # 30 bridge iterations
        "arrangement": 20,       # 20 arrangement iterations
    },

    # Novel/Book
    WorkKind.SERIES_BOOK: {
        "premise": 50,           # 50 iterations on series concept
        "voice": 40,             # 40 iterations to crystallize voice
    },
    WorkKind.VOLUME: {
        "structure": 20,         # 20 iterations on book structure
        "arc": 25,               # 25 iterations on character arcs
    },
    WorkKind.CHAPTER: {
        "concept": 10,           # 10 iterations per chapter
        "opening": 30,           # 30 iterations on chapter hooks
        "closing": 20,           # 20 iterations on chapter endings
    },
}

def total_iterations_for_series(series: WorkHierarchy) -> int:
    """
    Calculate total iterations for a hierarchical work.

    A 5-season, 60-episode show with this budget:
    - Series level: ~100 iterations
    - Season level: 5 × 45 = 225 iterations
    - Episode level: 60 × 80 = 4,800 iterations
    - Scene level (avg 30 scenes/ep): 60 × 30 × 20 = 36,000 iterations
    - Beat level (avg 100 beats/ep): 60 × 100 × 15 = 90,000 iterations

    TOTAL: ~130,000+ iterations over series lifetime
    This is why AI amplification is necessary—no human has this bandwidth.
    """
    ...
```

**Key insight**: Each iteration is an amplify → select → contradict → defend cycle. Without AI, this takes forever. With AI, it takes hours per episode.

---

## II. Persistent Creative Entities

### The Type

```python
class CreativeEntity(Enum):
    CHARACTER = auto()      # People, personas
    LOCATION = auto()       # Recurring places
    FORMAT = auto()         # Structural templates (cold opens, sketches)
    MOTIF = auto()          # Musical themes, visual symbols
    CATCHPHRASE = auto()    # Recurring dialogue
    RITUAL = auto()         # Format rituals (intro sequence, sign-off)

@dataclass(frozen=True)
class EntityRef:
    """Reference to a persistent entity."""
    ref: str  # Format: "{type}:{id}" e.g., "character:walter-white"

    @property
    def entity_type(self) -> CreativeEntity:
        return CreativeEntity[self.ref.split(":")[0].upper()]

    @property
    def entity_id(self) -> str:
        return self.ref.split(":", 1)[1]

@dataclass
class PersistentEntity:
    """
    An entity that recurs across works in a hierarchy.

    Examples:
    - CHARACTER: Walter White (appears in 62 episodes)
    - LOCATION: The lab (appears in 34 episodes)
    - FORMAT: Cold open (structural template)
    - MOTIF: "Crystal Blue Persuasion" (musical theme)
    """
    ref: EntityRef
    name: str
    entity_type: CreativeEntity
    defined_at: WorkId               # Where first introduced
    attributes: dict[str, Any]       # Character traits, location details
    appearances: list[WorkId]        # Where entity appears
    evolution: list[EntitySnapshot]  # How entity changes over time

@dataclass(frozen=True)
class EntitySnapshot:
    """A version of an entity at a specific point in the hierarchy."""
    work_id: WorkId
    timestamp: datetime
    state: dict[str, Any]           # e.g., {"moral_alignment": "dark"}
    narrative_position: str         # e.g., "protagonist", "antagonist"
```

### Character Persistence

```python
walter_white = PersistentEntity(
    ref=EntityRef("character:walter-white"),
    name="Walter White",
    entity_type=CreativeEntity.CHARACTER,
    defined_at=WorkId("bb-s1e1"),
    attributes={
        "age": 50,
        "occupation": "Chemistry teacher → Meth cook",
        "arc": "Pride-driven moral decay",
        "signature": "Porkpie hat, tighty-whities",
    },
    appearances=[WorkId(f"bb-s{s}e{e}") for s in range(1, 6) for e in range(1, 14)],
    evolution=[
        EntitySnapshot(
            work_id=WorkId("bb-s1e1"),
            state={"moral_alignment": 0.7, "competence": 0.3, "desperation": 0.8},
            narrative_position="sympathetic protagonist",
        ),
        EntitySnapshot(
            work_id=WorkId("bb-s3e10"),
            state={"moral_alignment": 0.3, "competence": 0.8, "desperation": 0.9},
            narrative_position="morally compromised protagonist",
        ),
        EntitySnapshot(
            work_id=WorkId("bb-s5e16"),
            state={"moral_alignment": 0.1, "competence": 0.95, "desperation": 1.0},
            narrative_position="tragic antagonist",
        ),
    ],
)
```

**Key Insight**: Characters are **not static**. The entity tracks evolution across works, allowing the Muse to:
1. **Maintain continuity**: "Walt doesn't cry in public after Season 2"
2. **Detect drift**: "This feels like Season 1 Walt, but we're in Season 4"
3. **Suggest callbacks**: "Skyler's birthday—remember the awkward party?"

### Character Iteration Budgets

Character creation follows the co-creative engine but with specific iteration counts:

```python
CHARACTER_ITERATION_BUDGET = {
    "main_protagonist": {
        "core_concept": 100,      # 100 iterations on "who is this person?"
        "contradiction": 50,      # 50 iterations on surprising inversions
        "voice": 40,              # 40 iterations on how they speak
        "arc": 30,                # 30 iterations on transformation
        "signature": 20,          # 20 iterations on memorable quirks
    },
    "main_antagonist": {
        "core_concept": 80,       # Why they're compelling
        "justification": 60,      # 60 iterations on "why they think they're right"
        "voice": 30,
        "arc": 25,
    },
    "supporting": {
        "core_concept": 30,
        "voice": 15,
        "function": 10,           # What do they enable in the story?
    },
    "recurring": {
        "core_concept": 20,
        "memorable_trait": 30,    # One thing audience remembers
    },
}

# From muse.md: "Best characters = familiar archetype + surprising inversion"
# The "contradiction" iterations are where breakthroughs happen
```

### Location Persistence

```python
the_lab = PersistentEntity(
    ref=EntityRef("location:lab"),
    name="The Superlab",
    entity_type=CreativeEntity.LOCATION,
    defined_at=WorkId("bb-s3e1"),
    attributes={
        "feel": "Industrial, clinical, oppressive",
        "function": "Cook site, cage, symbol of pride",
        "lighting": "Fluorescent, harsh shadows",
    },
    appearances=[WorkId("bb-s3e1"), WorkId("bb-s3e10"), ...],
)
```

### Format Persistence

```python
cold_open = PersistentEntity(
    ref=EntityRef("format:cold-open"),
    name="Breaking Bad Cold Open",
    entity_type=CreativeEntity.FORMAT,
    defined_at=WorkId("bb-series"),
    attributes={
        "structure": "Flash-forward or mystery hook (2-4 min)",
        "tone": "Cryptic, visually striking",
        "transition": "Hard cut to title card",
        "frequency": "90% of episodes",
    },
)
```

**Format as Template**: Formats are **reusable structural patterns**. When creating Episode N, the Muse suggests: "You usually open with a cold open—here's a template."

### Motif Persistence

```python
blue_meth = PersistentEntity(
    ref=EntityRef("motif:blue-meth"),
    name="Blue Meth Motif",
    entity_type=CreativeEntity.MOTIF,
    defined_at=WorkId("bb-s1e1"),
    attributes={
        "visual": "Bright blue crystals",
        "symbolic": "Purity, pride, identity",
        "recurrence": "Product shots, color grading",
    },
)
```

---

## III. The Series Bible as VisionSheaf

### TV Show Bible Structure

A traditional TV show "bible" contains:
- **Premise**: What is this show about?
- **Tone Guide**: How should it feel?
- **Character Sheets**: Who are the recurring people?
- **World Rules**: What's possible? What's forbidden?
- **Format Notes**: Episode structure, recurring segments

**Insight**: This is exactly a VisionSheaf at the series level.

```python
class SeriesBible(CreativeVisionSheaf):
    """
    The authoritative vision for a TV series.

    Local sections:
    - character_sheets: PersistentEntity for each main character
    - world_rules: Constraints on what can happen
    - tone_guide: Aesthetic boundaries
    - format_template: Episode structure pattern

    Global section: Unified creative identity
    Gluing condition: All episodes must satisfy these constraints
    """
    def validate_episode(self, episode: Work) -> ValidationReport:
        """Check if episode respects bible."""
        violations = []

        # Check character consistency
        for entity_ref in episode.entities:
            if entity_ref.entity_type == CreativeEntity.CHARACTER:
                entity = self.resolve_entity(entity_ref)
                if not self._character_in_bounds(episode, entity):
                    violations.append(f"{entity.name} acts out of character")

        # Check tone compatibility
        if not self.compatible_aesthetic(episode.vision.aesthetic):
            violations.append("Tone violates series aesthetic")

        # Check format compliance
        if not self._follows_format(episode):
            violations.append("Episode structure deviates from format")

        return ValidationReport(valid=len(violations) == 0, violations=violations)
```

### Example: The Office (US) Bible

```python
the_office_bible = SeriesBible(
    theme="Mundane absurdity in workplace purgatory",
    tone="Mockumentary, cringe comedy, warm undercurrent",
    constraints=[
        "Characters look at camera (documentary awareness)",
        "No laugh track",
        "Talking heads break fourth wall",
        "Dwight and Jim antagonism is affectionate",
    ],
    aesthetic=AestheticVector(
        humor=0.9,
        warmth=0.6,
        absurdity=0.8,
        cringe=0.7,
    ),
    character_sheets={
        "michael-scott": PersistentEntity(...),  # Insecure, needs approval
        "jim-halpert": PersistentEntity(...),    # Prankster, documentarian
        "dwight-schrute": PersistentEntity(...), # Beet farmer, alpha wannabe
    },
    world_rules=[
        "Events happen in real-time (no time skips mid-episode)",
        "Documentary crew is always present",
        "Office is in Scranton, PA—Rust Belt realism",
    ],
    format_template=FormatEntity(
        cold_open="Self-contained gag (1-2 min)",
        act_structure="3 acts with talking heads",
        tag="Post-credits stinger",
    ),
)
```

**Usage**: When writing Episode 47, the Muse:
1. **Loads the bible** as the parent VisionSheaf
2. **Checks character actions** against entity evolution
3. **Suggests format elements**: "Cold open? Talking heads?"
4. **Validates tone**: "This feels too dark for The Office"

### Series Bible Iteration Budget

Creating a series bible is not a one-pass activity. Each component requires focused iteration:

```python
SERIES_BIBLE_BUDGET = {
    "premise": 50,                # The "what if" that drives everything
    "logline": 100,               # 100 iterations to nail 1-2 sentences
    "tone_guide": 30,             # How it feels
    "world_rules": 20,            # What's possible
    "format_template": 15,        # Episode structure

    "character_sheets": {
        "per_main": 150,          # Each main character gets 150 total iterations
        "per_recurring": 50,      # Recurring characters
    },

    "pilot_outline": 40,          # The pilot proves the series works
}

# Total for a series bible: ~500-800 iterations
# This takes 2-4 focused sessions with AI amplification
# Without AI: months of development. With AI: days.
```

---

## IV. Asset Library: Reusable Creative Atoms

### The Type

```python
@dataclass(frozen=True)
class CreativeAsset:
    """
    A reusable creative component.

    Examples:
    - Video: Intro sequence, b-roll footage, transition templates
    - Audio: Theme song, sound effects, musical stingers
    - Visual: Character designs, location concept art, color palettes
    - Text: Catchphrases, character voice samples, format templates
    """
    id: AssetId
    name: str
    asset_type: AssetType  # VIDEO, AUDIO, VISUAL, TEXT, TEMPLATE
    tags: frozenset[str]   # For retrieval
    provenance: AssetProvenance
    binary_ref: BlobRef | None   # For video/audio/images
    content: str | None          # For text/templates
    metadata: AssetMetadata

class AssetType(Enum):
    VIDEO = auto()      # Intro, b-roll, clips
    AUDIO = auto()      # Theme, SFX, stingers
    VISUAL = auto()     # Concept art, palettes
    TEXT = auto()       # Catchphrases, dialogue templates
    TEMPLATE = auto()   # Format templates, outlines

@dataclass(frozen=True)
class AssetProvenance:
    """Where did this asset come from?"""
    created_at: datetime
    created_for: WorkId          # First used in this work
    created_by: str              # Artist/creator
    tool_signature: str | None   # e.g., "flux-img/1.2" for generated images
    parent_asset: AssetId | None # If derived from another asset
```

### Asset Library

```python
class AssetLibrary:
    """
    Storage and retrieval for creative assets.

    Operations:
    - store(asset): Persist asset with provenance
    - retrieve(asset_id): Load asset
    - search(query, tags, asset_type): Find assets
    - tag(asset_id, tags): Add metadata
    - link(asset_id, work_id): Track usage
    """
    def __init__(self, storage: StorageProvider):
        self.storage = storage
        self.index: dict[AssetId, CreativeAsset] = {}
        self.tags_index: dict[str, set[AssetId]] = {}
        self.works_index: dict[WorkId, set[AssetId]] = {}

    async def search(
        self,
        query: str | None = None,
        tags: frozenset[str] | None = None,
        asset_type: AssetType | None = None,
    ) -> list[CreativeAsset]:
        """Find assets matching criteria."""
        candidates = set(self.index.keys())

        if tags:
            candidates &= self._assets_with_tags(tags)
        if asset_type:
            candidates &= self._assets_of_type(asset_type)
        if query:
            candidates &= self._fuzzy_match(query)

        return [self.index[aid] for aid in candidates]

    async def link_to_work(self, asset_id: AssetId, work_id: WorkId) -> None:
        """Track that this asset was used in this work."""
        self.works_index.setdefault(work_id, set()).add(asset_id)
```

### Example: YouTube Channel Assets

```python
# Intro sequence
intro = CreativeAsset(
    id=AssetId("intro-v2"),
    name="Channel Intro v2",
    asset_type=AssetType.VIDEO,
    tags=frozenset({"intro", "branding", "5sec"}),
    provenance=AssetProvenance(
        created_at=datetime(2024, 3, 15),
        created_for=WorkId("channel-rebrand"),
        created_by="motion-designer-alice",
        tool_signature="after-effects/2024",
    ),
    binary_ref=BlobRef("gs://assets/intro-v2.mp4"),
)

# B-roll library
city_broll = CreativeAsset(
    id=AssetId("broll-city-01"),
    name="City skyline (dusk)",
    asset_type=AssetType.VIDEO,
    tags=frozenset({"broll", "city", "dusk", "establishing"}),
    provenance=AssetProvenance(
        created_at=datetime(2024, 1, 10),
        created_for=WorkId("episode-07"),
        created_by="videographer-bob",
    ),
    binary_ref=BlobRef("gs://assets/city-broll-01.mp4"),
)

# Catchphrase template
catchphrase = CreativeAsset(
    id=AssetId("catchphrase-signoff"),
    name="Episode sign-off",
    asset_type=AssetType.TEXT,
    tags=frozenset({"catchphrase", "outro", "signature"}),
    content="And remember: Stay curious, stay kind, and I'll see you next time.",
    provenance=AssetProvenance(
        created_at=datetime(2023, 11, 1),
        created_for=WorkId("episode-01"),
        created_by="host",
    ),
)
```

**Muse Suggestion**: When creating Episode 47, the Muse searches:
```python
# Find intro assets
intros = await library.search(tags=frozenset({"intro"}))
# Suggest: "Use intro-v2 (your current branding)"

# Find b-roll for city scene
broll = await library.search(tags=frozenset({"broll", "city", "dusk"}))
# Suggest: "You have 3 city dusk clips—reuse city-broll-01?"
```

---

## V. Recurring Elements as Invariants

### Invariant Types

```python
class InvariantKind(Enum):
    THEME_SONG = "theme_song"           # Never changes
    INTRO_SEQUENCE = "intro_sequence"   # Same every episode
    CATCHPHRASE = "catchphrase"         # Signature line
    FORMAT_RITUAL = "format_ritual"     # Structural pattern
    VISUAL_MOTIF = "visual_motif"       # Recurring image/color

@dataclass(frozen=True)
class CreativeInvariant:
    """
    An element that MUST NOT change across works.

    These create identity and audience connection.
    """
    kind: InvariantKind
    asset_id: AssetId
    applies_to: frozenset[WorkId]  # Works that must use this
    rationale: str                  # Why is this fixed?

    def validate(self, work: Work) -> bool:
        """Check if work respects this invariant."""
        ...
```

### Examples

```python
# The Office theme song
theme = CreativeInvariant(
    kind=InvariantKind.THEME_SONG,
    asset_id=AssetId("the-office-theme"),
    applies_to=frozenset({WorkId("the-office-series")}),  # All descendants
    rationale="Instantly recognizable—audience connection point",
)

# Breaking Bad title card
title_card = CreativeInvariant(
    kind=InvariantKind.INTRO_SEQUENCE,
    asset_id=AssetId("bb-title-card"),
    applies_to=frozenset({WorkId("bb-series")}),
    rationale="Brand identity—green periodic table animation",
)

# "That's what she said" (The Office)
twss = CreativeInvariant(
    kind=InvariantKind.CATCHPHRASE,
    asset_id=AssetId("twss-catchphrase"),
    applies_to=frozenset({WorkId("the-office-series")}),
    rationale="Michael's signature—removes it, you lose character",
)

# Cold open format (Breaking Bad)
cold_open_ritual = CreativeInvariant(
    kind=InvariantKind.FORMAT_RITUAL,
    asset_id=AssetId("bb-cold-open-format"),
    applies_to=frozenset({WorkId("bb-series")}),
    rationale="Narrative hook—90% of episodes use this",
)
```

**Enforcement**:
```python
def validate_work(work: Work, invariants: list[CreativeInvariant]) -> ValidationReport:
    """Check if work respects required invariants."""
    violations = []

    for inv in invariants:
        if work.id in inv.applies_to or work.parent in inv.applies_to:
            if not inv.validate(work):
                violations.append(
                    f"Missing required {inv.kind}: {inv.rationale}"
                )

    return ValidationReport(valid=len(violations) == 0, violations=violations)
```

---

## VI. Integration with Co-Creative Engine

> *This section connects Part IV (hierarchical data structures) with muse.md (the co-creative engine). Hierarchy enables focused iteration; the engine provides the dialectic.*

### Hierarchical Context Injection

When working on Episode N of Season S:

```python
async def create_episode(
    hierarchy: WorkHierarchy,
    season_id: WorkId,
    episode_number: int,
) -> Work:
    """Create new episode with full hierarchical context."""

    # 1. Load parent contexts
    series = hierarchy.root
    season = hierarchy.find(season_id)

    # 2. Gather constraints
    constraints = [
        *series.vision.constraints,
        *season.vision.constraints,
    ]

    # 3. Resolve available entities
    entities = series.entities | season.entities

    # 4. Load invariants
    invariants = _load_invariants(series)

    # 5. Search asset library for suggestions
    suggested_assets = await asset_library.search(
        tags=frozenset({"episode", "intro", "outro"}),
    )

    # 6. Create episode with inherited context
    episode = Work(
        id=WorkId(f"{season_id}-e{episode_number}"),
        title=f"Episode {episode_number}",
        kind=WorkKind.EPISODE,
        parent=season_id,
        vision=CreativeVisionSheaf(
            theme="[To be defined]",
            tone=season.vision.tone,  # Inherit from season
            constraints=constraints,
            aesthetic=season.vision.aesthetic,
        ),
        entities=frozenset(),  # Start empty, add as needed
        metadata=WorkMetadata(
            duration_minutes=season.metadata.episode_length,
            format=invariants.get("format_ritual"),
        ),
    )

    return episode
```

### Feedback Propagation

When Episode N discovers an insight:

```python
async def bubble_feedback(
    hierarchy: WorkHierarchy,
    episode_id: WorkId,
    feedback: CreativeFeedback,
) -> None:
    """Propagate creative insight upward."""

    episode = hierarchy.find(episode_id)

    # Insight: "Walt's pride is the real theme, not survival"
    if feedback.kind == FeedbackKind.THEME_CLARIFICATION:
        season = hierarchy.find(episode.parent)

        # Update season theme
        season.vision.theme = refine_theme(
            current=season.vision.theme,
            insight=feedback.content,
        )

        # Propagate to series if significant
        if feedback.significance > 0.8:
            series = hierarchy.root
            series.vision.theme = refine_theme(
                current=series.vision.theme,
                insight=feedback.content,
            )
```

### The Iteration-Hierarchy Connection

The co-creative engine from muse.md operates at each level with different iteration budgets:

```python
async def iterate_at_level(
    work: Work,
    aspect: str,
    budget: int,
) -> Work:
    """
    Apply co-creative dialectic at one hierarchy level.

    From muse.md:
    1. AMPLIFY: Generate options
    2. SELECT: Kent picks
    3. CONTRADICT: Challenge selection
    4. DEFEND/PIVOT: Strengthen or discover

    Repeat until:
    - Budget exhausted, OR
    - Escape velocity reached (work has its own gravity)
    """
    iteration = 0
    current = work

    while iteration < budget:
        # Amplify (from muse.md AIRole.AMPLIFIER)
        options = await amplify(getattr(current, aspect), count=50)

        # Select (Kent's taste)
        selected = await kent_select(options)

        # Contradict (from muse.md AIRole.CONTRADICTOR)
        challenge = await contradict(selected, current.vision)

        # Defend or Pivot
        response = await kent_respond(challenge)
        current = apply_response(current, aspect, response)

        # Check escape velocity
        if has_escape_velocity(current, aspect):
            break

        iteration += 1

    return current

# Example: Developing a series premise with full budget
async def develop_series_premise(seed: str) -> Work:
    work = Work(kind=WorkKind.SERIES, vision=VisionSheaf(theme=seed))

    # 50 iterations on premise (from ITERATION_BUDGETS)
    work = await iterate_at_level(work, "theme", budget=50)

    # 30 iterations on tone
    work = await iterate_at_level(work, "tone", budget=30)

    # 20 iterations on world rules
    work = await iterate_at_level(work, "constraints", budget=20)

    return work
```

**Key Insight**: Hierarchy provides focus. Without hierarchy, you'd iterate on "the whole show"—too diffuse to reach escape velocity. With hierarchy, each level can achieve breakthrough independently, and breakthroughs propagate.

---

## VII. Laws

| # | Law | Description |
|---|-----|-------------|
| 1 | hierarchical_coherence | Child vision MUST be compatible with parent vision |
| 2 | entity_resolution | Entity refs resolve upward to first definition |
| 3 | invariant_preservation | Invariants MUST appear in all applicable works |
| 4 | feedback_flows_up | Creative insights propagate to ancestors |
| 5 | constraints_flow_down | Parent constraints apply to all descendants |
| 6 | asset_provenance | Every asset MUST track creation context |
| 7 | evolution_continuity | Entity snapshots MUST be temporally ordered |
| 8 | iteration_budget_honored | Each level gets its full iteration budget before moving down |
| 9 | escape_velocity_unlocks | Moving to child level requires parent escape velocity OR budget exhaustion |
| 10 | breakthrough_propagates | A breakthrough at child level triggers re-iteration at parent level |

---

## VIII. AGENTESE Integration

```python
# Hierarchical queries
await logos.invoke("self.muse.hierarchy.show", work_id="bb-s3e10")
# → Full ancestry: Series → Season 3 → Episode 10

await logos.invoke("self.muse.entities.list", work_id="bb-series")
# → All persistent entities defined at series level

await logos.invoke("self.muse.entities.evolution", entity_ref="character:walter-white")
# → Timeline of Walt's character evolution across 62 episodes

await logos.invoke("self.muse.bible.validate", episode_id="bb-s4e13")
# → Check if episode respects series bible

await logos.invoke("self.muse.assets.search", tags=["intro", "branding"])
# → Find reusable intro assets

await logos.invoke("self.muse.invariants.check", work_id="bb-s5e1")
# → Verify required invariants present
```

---

## IX. Anti-Patterns

**Hierarchy Anti-Patterns**:
- **Flat Structure for Hierarchical Works**: Treating a TV show as a list of files loses coherence
- **Character Inconsistency**: Walt acts like Season 1 Walt in Season 5—breaks belief
- **Ignoring Parent Constraints**: Episode violates series bible—audience notices
- **Asset Duplication**: Re-creating intro for every episode—wasted effort, inconsistent
- **No Provenance Tracking**: Can't remember where asset came from or why
- **Static Entities**: Characters don't evolve—they feel wooden, not alive

**Iteration Anti-Patterns** (integration with muse.md):
- **Premature Descent**: Moving to episode level before series bible reaches escape velocity—waste downstream iterations
- **Skipped Contradiction**: Accepting first good option without challenge—misses breakthroughs
- **Budget Starvation**: Giving 5 iterations to main character—not enough to find surprising inversion
- **Uniform Budgets**: Same iterations for pivotal scene and transition—misallocated effort
- **Ignored Propagation**: Child breakthrough not re-examined at parent level—orphaned insight

---

## X. Implementation Reference

```
impl/claude/services/muse/
├── hierarchy.py          # WorkHierarchy, Work, coherence checks
├── entities.py           # PersistentEntity, EntitySnapshot, evolution
├── bible.py              # SeriesBible, validation
├── assets.py             # AssetLibrary, search, provenance
├── invariants.py         # CreativeInvariant, enforcement
└── feedback.py           # Feedback propagation (up/down tree)
```

---

*"A show isn't episodes. A show is a world. The Muse remembers the world so you can focus on the story."*

---

## Relationship to Main Spec

This part provides **data structures** for hierarchical creative works. The main muse.md provides the **generative engine** (the dialectic).

**muse.md answers**: How does breakthrough work emerge?
**muse-part-iv.md answers**: How do you structure that process for long-form works?

They work together:
1. muse.md's `GenerationalShowEngine` (section 6.3) references `SeriesBible` defined here
2. The iteration budgets here operationalize muse.md's volume principle for hierarchical works
3. Entity persistence enables muse.md's `AIRole.MEMORY` to work across episodes

**Read both for TV/long-form work. Read only muse.md for standalone work.**

---

*Synthesized: 2025-01-11 | Updated: 2025-01-11 | Part IV of Creative Muse Protocol v2.0 | Hierarchical Works & Persistent Entities*
