# S-gent: Creative Production Studio

> *"Art is not what you see, but what you make others see." — Degas*

**Version**: 1.0
**Status**: Draft
**Date**: 2025-12-28
**Supersedes**: `spec/protocols/metaphysical-forge.md` (never implemented), Atelier (extinct)
**Dependencies**: Foundry (JIT compilation), Witness (decision tracking), Brain (artifact storage)

---

## Abstract

The Creative Production Studio (S-gent) is a **two-functor pipeline** that transforms raw materials into creative and art assets. It absorbs and supersedes the defunct Atelier/Forge concepts, consolidating creative infrastructure into a single, tasteful system.

```
f(Principles, Archaeology) → (Vision, Strategy)
f(Vision | Strategy) → (Creative Assets | Art Assets)
```

**What was wrong with Atelier/Forge:**
- Atelier: "Fishbowl" spectator economy was backwards — Kent is the primary consumer
- Metaphysical Forge: 7-artisan vision was overengineered, never implemented
- Both lacked the archaeological phase — extracting creative vision from existing work

**What S-gent Studio provides:**
- Aesthetic Archaeology: Extracting creative vision from raw materials
- Vision Synthesis: Generating style guides, art direction, brand identity
- Asset Production: Creating sprites, audio, graphics, video, writing
- Quality Assurance: Tetrad-based quality measurement (Contrast, Arc, Voice, Floor)

---

## The Core Insight

> *"The studio is a two-functor pipeline: Archaeology extracts vision, Production synthesizes assets."*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  RAW MATERIAL              CREATIVE VISION              ASSETS             │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐        │
│  │ Specs       │          │ Style Guide │          │ Sprites     │        │
│  │ Code        │   ───▶   │ Art Direction│   ───▶  │ Audio       │        │
│  │ Screenshots │          │ Brand Identity│         │ Graphics    │        │
│  │ Inspiration │          │ Campaigns   │          │ Video       │        │
│  └─────────────┘          └─────────────┘          └─────────────┘        │
│                                                                            │
│     [Archaeology]            [Synthesis]             [Production]          │
│     AestheticFunctor         VisionFunctor           AssetFunctor          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part I: The Studio Stack (7 Layers)

Following AD-009 Metaphysical Fullstack:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   Assets (sprites, audio), Showcase (gallery)      │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     world.studio.* (archaeology, vision, production) │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node("world.studio") with creative aspects      │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/studio/ (Crown Jewel)                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        STUDIO_OPERAD (excavate, synthesize, produce)    │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      StudioPolynomial (5 phases)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Style coherence across domains                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  0. PERSISTENCE           Creative decisions, asset registry, gallery      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part II: Formal Definitions

### 2.1 StudioPolynomial

```python
class StudioPhase(Enum):
    ARCHAEOLOGY = auto()   # Excavating raw materials, extracting patterns
    SYNTHESIS = auto()     # Generating creative vision, style guide
    PRODUCTION = auto()    # Creating assets (sprites, audio, etc.)
    REVIEW = auto()        # Quality assurance, iteration
    DELIVERY = auto()      # Export, handoff, gallery placement

STUDIO_POLYNOMIAL = PolyAgent(
    name="StudioPolynomial",
    positions=frozenset(StudioPhase),
    _directions=studio_directions,
    _transition=studio_transition,
)

def studio_directions(phase: StudioPhase) -> FrozenSet[Type]:
    """Mode-dependent valid inputs."""
    match phase:
        case StudioPhase.ARCHAEOLOGY:
            return frozenset([ExcavateInput, SourceInput, FocusInput])
        case StudioPhase.SYNTHESIS:
            return frozenset([SynthesizeInput, PrincipleInput, VisionInput])
        case StudioPhase.PRODUCTION:
            return frozenset([ProduceInput, AssetTypeInput, StyleInput])
        case StudioPhase.REVIEW:
            return frozenset([ReviewInput, FeedbackInput, IterateInput])
        case StudioPhase.DELIVERY:
            return frozenset([ExportInput, GalleryInput, HandoffInput])
```

### 2.2 StudioOperad

```python
STUDIO_OPERAD = Operad(
    name="StudioOperad",
    operations={
        # Archaeological operations (arity: source → findings)
        "excavate": Operation(arity=1, description="Extract patterns from source"),
        "interpret": Operation(arity=1, description="Assign meaning to findings"),
        "trace": Operation(arity=1, description="Track provenance of element"),

        # Synthesis operations (arity: inputs → vision)
        "synthesize": Operation(arity=2, description="Combine findings + principles → vision"),
        "codify": Operation(arity=1, description="Vision → style guide"),
        "brand": Operation(arity=1, description="Vision → brand identity"),

        # Production operations (arity: vision × requirement → asset)
        "produce": Operation(arity=2, description="Create asset from vision + requirement"),
        "refine": Operation(arity=2, description="Improve asset with feedback"),
        "composite": Operation(arity=2, description="Combine assets"),

        # Delivery operations (arity: asset → output)
        "export": Operation(arity=1, description="Render asset to format"),
        "gallery": Operation(arity=1, description="Place in showcase"),
        "handoff": Operation(arity=1, description="Transfer to consumer"),
    },
    laws=[
        Law("provenance_preserved", "trace ∘ excavate = id (archaeology preserves source)"),
        Law("vision_determines_style", "codify ∘ synthesize is deterministic"),
        Law("refinement_reversible", "refine can be undone within session"),
        Law("export_idempotent", "export ∘ export = export"),
    ],
)
```

### 2.3 VisionSheaf

```python
@dataclass
class VisionSheaf:
    """
    Coherent creative vision across domains.

    Local sections: Style decisions per domain (color, typography, motion)
    Global section: Unified brand identity
    Gluing condition: Consistency across touchpoints
    """

    # Local sections (domain-specific)
    color_palette: ColorPalette
    typography: TypographySpec
    motion: MotionSpec
    iconography: IconographySpec
    tone_of_voice: ToneSpec

    # Global section (unified)
    brand_identity: BrandIdentity

    def glue(self) -> bool:
        """Verify consistency across domains."""
        return all([
            self.color_palette.primary in self.brand_identity.colors,
            self.typography.heading_font == self.brand_identity.primary_font,
            self.motion.timing_function == self.brand_identity.motion_curve,
        ])
```

---

## Part III: Asset Taxonomy

Derived from WASM Survivors archaeology (200+ requirements extracted):

### 3.1 Creative Assets (Strategic)

| Type | Description | AGENTESE Path | Example |
|------|-------------|---------------|---------|
| **Vision Document** | High-level creative direction | `world.studio.vision.manifest` | "Geometric arcade with biological undertones" |
| **Style Guide** | Concrete specifications | `world.studio.style.manifest` | Color palettes, typography, motion principles |
| **Art Requirements** | What needs to be created | `world.studio.requirements.manifest` | Sprite dimensions, animation states |
| **Campaign Strategy** | Marketing approach | `world.studio.campaign.manifest` | Launch sequence, messaging |
| **Brand Identity** | Core brand elements | `world.studio.brand.manifest` | Logo, voice, personality |

### 3.2 Art Assets (Tactical)

| Type | Specs | AGENTESE Path | Example |
|------|-------|---------------|---------|
| **Sprites** | PNG-24/32, power-of-2, 2px padding | `world.studio.assets.sprites` | `hornet_idle.png` (64x64) |
| **Animations** | Frame sequences, fps specified | `world.studio.assets.animations` | `hornet_attack` (6 frames, 16 fps) |
| **Audio** | OGG/MP3, 44.1kHz, -14 LUFS | `world.studio.assets.audio` | `sfx_bundle.ogg` |
| **Graphics** | Static visuals, any format | `world.studio.assets.graphics` | UI elements, icons |
| **Video** | MP4/WebM, any resolution | `world.studio.assets.video` | Trailers, cutscenes |
| **Writing** | Markdown/JSON, localized | `world.studio.assets.writing` | Flavor text, UI copy |

### 3.3 File Organization

```
assets/
├── creative/                    # Strategic assets
│   ├── vision/                  # Vision documents
│   ├── style/                   # Style guides
│   ├── requirements/            # Art requirements
│   ├── campaigns/               # Marketing strategies
│   └── brand/                   # Brand identity
│
├── art/                         # Tactical assets
│   ├── sprites/                 # Bitmap graphics
│   │   ├── player/
│   │   ├── enemies/
│   │   └── effects/
│   ├── animations/              # Animation data
│   ├── audio/                   # Sound files
│   │   ├── sfx/
│   │   └── music/
│   ├── graphics/                # Static visuals
│   ├── video/                   # Motion content
│   └── writing/                 # Text content
│
├── atlases/                     # Build output (packed)
└── data/                        # Metadata
    ├── atlas_map.json
    ├── animations.json
    └── color_palettes.json
```

---

## Part IV: The Three Functors

### 4.1 AestheticArchaeologyFunctor

```python
class AestheticArchaeologyFunctor:
    """
    Extracts creative vision from raw materials.

    Input: Raw materials (specs, code, screenshots, inspirations)
    Output: Archaeological findings (patterns, themes, constraints)
    """

    async def excavate(
        self,
        sources: list[Source],
        focus: ArchaeologyFocus,
    ) -> ArchaeologicalFindings:
        """
        Extract patterns from sources.

        Focus types:
        - VISUAL: Colors, shapes, composition
        - AUDIO: Soundscapes, rhythms, tones
        - NARRATIVE: Themes, arcs, characters
        - MECHANICAL: Interactions, feedback loops
        - EMOTIONAL: Feelings, moods, tensions
        """
        findings = []
        for source in sources:
            extracted = await self._extract_patterns(source, focus)
            findings.extend(extracted)

        return ArchaeologicalFindings(
            patterns=findings,
            provenance=self._build_provenance_graph(sources, findings),
        )

    async def interpret(
        self,
        findings: ArchaeologicalFindings,
        lens: InterpretationLens,
    ) -> InterpretedMeaning:
        """
        Assign meaning to findings.

        Lenses:
        - SEMIOTIC: Signs, symbols, signifiers
        - AESTHETIC: Beauty, taste, style
        - FUNCTIONAL: Purpose, utility, flow
        - EMOTIONAL: Affect, resonance, impact
        """
        ...
```

### 4.2 VisionSynthesisFunctor

```python
class VisionSynthesisFunctor:
    """
    Generates creative vision from findings + principles.

    Input: Archaeological findings + design principles
    Output: Creative vision (style guide, brand identity)
    """

    async def synthesize(
        self,
        findings: ArchaeologicalFindings,
        principles: list[DesignPrinciple],
    ) -> CreativeVision:
        """
        Combine findings with principles to generate vision.

        The vision is not just extraction — it's transformation.
        Findings are raw material; principles are the forge.
        """
        # Extract dominant patterns
        dominant = self._identify_dominant_patterns(findings)

        # Apply principles as constraints
        constrained = self._apply_principles(dominant, principles)

        # Synthesize into coherent vision
        vision = CreativeVision(
            core_insight=self._distill_insight(constrained),
            color_palette=self._derive_palette(constrained),
            typography=self._derive_typography(constrained),
            motion=self._derive_motion(constrained),
            tone=self._derive_tone(constrained),
        )

        return vision

    async def codify(self, vision: CreativeVision) -> StyleGuide:
        """Transform vision into actionable style guide."""
        ...

    async def brand(self, vision: CreativeVision) -> BrandIdentity:
        """Transform vision into brand identity."""
        ...
```

### 4.3 AssetProductionFunctor

```python
class AssetProductionFunctor:
    """
    Creates assets from vision + requirements.

    Input: Creative vision + asset requirements
    Output: Art assets (sprites, audio, graphics, etc.)
    """

    async def produce(
        self,
        vision: CreativeVision,
        requirement: AssetRequirement,
    ) -> Asset:
        """
        Create asset that embodies vision and fulfills requirement.

        The producer is opinionated — it doesn't just execute,
        it proposes unexpected but justified directions.
        """
        # Select production strategy based on asset type
        strategy = self._select_strategy(requirement.asset_type)

        # Generate asset with vision constraints
        asset = await strategy.generate(
            requirement=requirement,
            style_guide=vision.to_style_guide(),
        )

        # Validate against quality gates
        quality = await self._measure_quality(asset)
        if not quality.passes_floor():
            raise QualityFloorViolation(quality)

        return asset

    async def refine(
        self,
        asset: Asset,
        feedback: Feedback,
    ) -> Asset:
        """Improve asset based on feedback."""
        ...

    async def composite(
        self,
        assets: list[Asset],
        composition: CompositionSpec,
    ) -> Asset:
        """Combine multiple assets."""
        ...
```

---

## Part V: Quality Algebra

Instantiation of Experience Quality Operad for creative domain:

```python
STUDIO_QUALITY_ALGEBRA = QualityAlgebra(
    domain="creative_studio",
    description="Quality algebra for creative production",

    # Contrast: Variety within coherence
    contrast_dims=(
        ContrastDimension(
            name="expression",
            description="C1: Range of creative expression",
            measurement_hint="Track uniqueness vs. derivativeness",
        ),
        ContrastDimension(
            name="consistency",
            description="C2: Adherence to style guide",
            measurement_hint="Measure deviation from vision",
        ),
        ContrastDimension(
            name="surprise",
            description="C3: Unexpected but justified choices",
            measurement_hint="Track novel elements that still fit",
        ),
    ),

    # Arc: Creative process phases
    arc_phases=(
        PhaseDefinition(name="discovery", description="Finding the seed"),
        PhaseDefinition(name="exploration", description="Expanding possibilities"),
        PhaseDefinition(name="commitment", description="Narrowing to vision"),
        PhaseDefinition(name="execution", description="Producing assets"),
        PhaseDefinition(name="polish", description="Refining to completion"),
    ),

    # Voice: Three perspectives
    voices=(
        VoiceDefinition(
            name="adversarial",
            question="Is this technically correct?",
            checks=("format_valid", "dimensions_correct", "palette_compliant"),
        ),
        VoiceDefinition(
            name="creative",
            question="Is this interesting and novel?",
            checks=("not_derivative", "unexpected_element", "style_coherent"),
        ),
        VoiceDefinition(
            name="advocate",
            question="Would Kent be delighted?",
            checks=("joy_inducing", "tasteful", "on_brand"),
        ),
    ),

    # Floor: Non-negotiables
    floor_checks=(
        FloorCheckDefinition(
            name="provenance",
            threshold=1.0,
            description="F1: All elements have traceable source",
        ),
        FloorCheckDefinition(
            name="format_compliance",
            threshold=1.0,
            description="F2: Assets meet technical specifications",
        ),
        FloorCheckDefinition(
            name="style_coherence",
            threshold=0.8,
            description="F3: 80%+ alignment with style guide",
        ),
        FloorCheckDefinition(
            name="accessibility",
            threshold=1.0,
            description="F4: WCAG AA contrast ratios met",
        ),
    ),

    # Weights: Creative voice emphasized
    contrast_weight=0.25,
    arc_weight=0.25,
    voice_weight=0.50,
)
```

---

## Part VI: AGENTESE Integration

### 6.1 Path Structure

```python
STUDIO_PATHS = {
    # Archaeology context
    "world.studio.archaeology.excavate": {
        "aspect": "define",
        "description": "Extract patterns from sources",
        "effects": ["ARCHAEOLOGY_PERFORMED"],
        "contract": Contract(ExcavateRequest, ArchaeologicalFindings),
    },
    "world.studio.archaeology.interpret": {
        "aspect": "define",
        "description": "Assign meaning to findings",
        "effects": ["INTERPRETATION_GENERATED"],
        "contract": Contract(InterpretRequest, InterpretedMeaning),
    },

    # Vision context
    "world.studio.vision.manifest": {
        "aspect": "manifest",
        "description": "Current creative vision",
        "effects": [],
        "contract": Contract(None, CreativeVision),
    },
    "world.studio.vision.synthesize": {
        "aspect": "define",
        "description": "Generate vision from findings + principles",
        "effects": ["VISION_SYNTHESIZED"],
        "contract": Contract(SynthesizeRequest, CreativeVision),
    },
    "world.studio.vision.codify": {
        "aspect": "define",
        "description": "Transform vision to style guide",
        "effects": ["STYLE_GUIDE_CREATED"],
        "contract": Contract(VisionInput, StyleGuide),
    },

    # Production context
    "world.studio.production.brief": {
        "aspect": "manifest",
        "description": "Current production brief",
        "effects": [],
        "contract": Contract(None, ProductionBrief),
    },
    "world.studio.production.produce": {
        "aspect": "define",
        "description": "Create asset from requirement",
        "effects": ["ASSET_PRODUCED"],
        "contract": Contract(ProduceRequest, Asset),
    },
    "world.studio.production.refine": {
        "aspect": "define",
        "description": "Improve asset with feedback",
        "effects": ["ASSET_REFINED"],
        "contract": Contract(RefineRequest, Asset),
    },

    # Assets context
    "world.studio.assets.manifest": {
        "aspect": "manifest",
        "description": "Asset registry",
        "effects": [],
        "contract": Contract(None, AssetRegistry),
    },
    "world.studio.assets.export": {
        "aspect": "define",
        "description": "Export asset to format",
        "effects": ["ASSET_EXPORTED"],
        "contract": Contract(ExportRequest, ExportedAsset),
    },

    # Gallery context
    "world.studio.gallery.manifest": {
        "aspect": "manifest",
        "description": "Gallery contents",
        "effects": [],
        "contract": Contract(None, GalleryManifest),
    },
    "world.studio.gallery.place": {
        "aspect": "define",
        "description": "Place asset in gallery",
        "effects": ["GALLERY_UPDATED"],
        "contract": Contract(PlaceRequest, GalleryPlacement),
    },
}
```

### 6.2 Node Registration

```python
@node(
    "world.studio",
    description="Creative Production Studio",
    dependencies=("witness", "brain", "foundry"),
    contracts={
        "manifest": StudioManifestResponse,
        "archaeology.excavate": Contract(ExcavateRequest, ArchaeologicalFindings),
        "vision.synthesize": Contract(SynthesizeRequest, CreativeVision),
        "production.produce": Contract(ProduceRequest, Asset),
        "assets.export": Contract(ExportRequest, ExportedAsset),
        "gallery.place": Contract(PlaceRequest, GalleryPlacement),
    },
)
class StudioNode:
    """AGENTESE node for Creative Production Studio."""

    def __init__(
        self,
        witness: WitnessService,
        brain: BrainService,
        foundry: FoundryService,
    ):
        self.witness = witness
        self.brain = brain
        self.foundry = foundry
        self.studio = CreativeStudioService(witness, brain, foundry)

    async def manifest(self, observer: Umwelt) -> StudioManifestResponse:
        """Studio capabilities and status."""
        return await self.studio.manifest(observer)

    async def archaeology_excavate(
        self,
        request: ExcavateRequest,
        observer: Umwelt,
    ) -> ArchaeologicalFindings:
        """Extract patterns from sources."""
        return await self.studio.excavate(request, observer)

    # ... other handlers
```

---

## Part VII: Integration Points

### 7.1 Foundry Integration (JIT Tool Compilation)

```python
async def compile_creative_tool(
    self,
    intent: str,
    vision: CreativeVision,
) -> CompiledTool:
    """
    Use Foundry to JIT-compile creative tools.

    Example: "Create a sprite animator that follows our style guide"
    → Foundry classifies as PROBABILISTIC
    → Generates agent with style constraints
    → Projects to MARIMO for interactive use
    """
    return await self.foundry.forge(
        intent=intent,
        context={"style_guide": vision.to_style_guide()},
    )
```

### 7.2 Witness Integration (Decision Tracking)

```python
async def witness_creative_decision(
    self,
    decision: CreativeDecision,
) -> Mark:
    """
    Record creative decisions for provenance.

    Every color choice, composition decision, and style
    deviation is witnessed for future archaeology.
    """
    return await self.witness.mark(
        action=f"creative_decision:{decision.type}",
        reasoning=decision.rationale,
        context={
            "vision_id": decision.vision_id,
            "asset_id": decision.asset_id,
            "alternatives_considered": decision.alternatives,
        },
    )
```

### 7.3 Brain Integration (Artifact Storage)

```python
async def persist_asset(
    self,
    asset: Asset,
    gallery_placement: GalleryPlacement | None = None,
) -> StoredAsset:
    """
    Store asset in Brain's memory cathedral.

    Assets are automatically crystallized and made
    available for future archaeology.
    """
    crystal = await self.brain.capture(
        content=asset.to_dict(),
        tags=["creative", "asset", asset.asset_type],
    )

    return StoredAsset(
        asset=asset,
        crystal_id=crystal.id,
        gallery_placement=gallery_placement,
    )
```

---

## Part VIII: Example: WASM Survivors Art Pipeline

```python
async def wasm_survivors_pipeline():
    """
    Complete art pipeline for WASM Survivors.

    Demonstrates the full Studio workflow.
    """
    studio = CreativeStudioService()

    # Phase 1: Archaeology
    findings = await studio.excavate(
        sources=[
            Source("pilots/wasm-survivors-game/PROTO_SPEC.md"),
            Source("pilots/wasm-survivors-game/PROTO_SPEC_ENLIGHTENED.md"),
            Source("pilots/wasm-survivors-game/SYSTEM_REQUIREMENTS.md"),
        ],
        focus=ArchaeologyFocus.VISUAL,
    )
    # Yields: 280 sprite frames, 3 palettes, 50+ audio assets, etc.

    # Phase 2: Vision synthesis
    vision = await studio.synthesize(
        findings=findings,
        principles=[
            DesignPrinciple("Geometric arcade with biological undertones"),
            DesignPrinciple("High contrast: player (blue) vs enemies (red)"),
            DesignPrinciple("Earned animation: stillness by default"),
        ],
    )
    # Yields: Style guide with colors, animation specs, audio direction

    # Phase 3: Art requirements
    requirements = await studio.generate_requirements(
        vision=vision,
        domain="wasm_survivors",
    )
    # Yields: Detailed specs for each asset (dimensions, fps, etc.)

    # Phase 4: Production
    assets = []
    for req in requirements:
        asset = await studio.produce(
            vision=vision,
            requirement=req,
        )
        assets.append(asset)

    # Phase 5: Export
    bundle = await studio.export(
        assets=assets,
        format=ExportFormat.WEB,
        optimization=Optimization.AGGRESSIVE,
    )
    # Yields: Packed atlases, audio sprites, manifest

    return bundle
```

---

## Part IX: Anti-Patterns

| Anti-Pattern | Why Bad | Correct Pattern |
|--------------|---------|-----------------|
| **Art-first** | No strategy = inconsistent | Strategy → Art |
| **Single-pass** | No iteration = low quality | Ideate → Create → Review → Refine |
| **Implicit decisions** | Lost provenance | Witness every decision |
| **Asset sprawl** | No curation | Taxonomy + lifecycle |
| **Style drift** | Vision not enforced | VisionSheaf gluing condition |
| **Spectator economy** | Wrong audience | Kent-centric creation |
| **Seven artisans** | Overengineered | Single polynomial, multiple functors |

---

## Part X: Migration from Atelier/Forge

### 10.1 What's Absorbed

| From | Component | Into Studio |
|------|-----------|-------------|
| Atelier | Commission workflow | `world.studio.production.brief` |
| Atelier | Gallery | `world.studio.gallery.*` |
| Atelier | Artisan events | StudioPolynomial phases |
| Forge | K-gent governance | Quality voice (advocate) |
| Forge | Visual language (stone + amber) | STARK BIOME reference |
| Sprite Lab | Character creation | Asset production functor |
| Art Pipeline | Build tooling | Export operations |

### 10.2 What's Deprecated

| System | Reason | Alternative |
|--------|--------|-------------|
| Metaphysical Forge spec | Never implemented, overengineered | S-gent Studio |
| Atelier service | Extinct (2025-12-21) | S-gent Studio |
| Seven Artisans | Too complex | Single StudioPolynomial |
| Spectator economy | Wrong focus | Kent-centric |

### 10.3 What's Referenced (Not Absorbed)

| System | Relationship |
|--------|--------------|
| **Foundry** | Dependency: JIT tool compilation |
| **Witness** | Dependency: Decision tracking |
| **Brain** | Dependency: Artifact storage |
| **Workshop** | Sibling: Town collaborative building (different purpose) |
| **STARK BIOME** | Foundation: Design language |
| **Experience Quality** | Foundation: Quality measurement |

---

## Part XI: Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create `spec/s-gents/studio.md` (this document)
- [ ] Create `services/studio/` directory structure
- [ ] Implement StudioPolynomial
- [ ] Implement STUDIO_OPERAD
- [ ] Register in OperadRegistry

### Phase 2: Archaeology (Week 2)
- [ ] Implement AestheticArchaeologyFunctor
- [ ] Create extraction strategies per focus type
- [ ] Build provenance graph infrastructure
- [ ] Wire `world.studio.archaeology.*` paths

### Phase 3: Vision (Week 3)
- [ ] Implement VisionSynthesisFunctor
- [ ] Create VisionSheaf coherence checking
- [ ] Implement style guide generation
- [ ] Wire `world.studio.vision.*` paths

### Phase 4: Production (Week 4)
- [ ] Implement AssetProductionFunctor
- [ ] Create production strategies per asset type
- [ ] Implement quality measurement
- [ ] Wire `world.studio.production.*` paths

### Phase 5: Integration (Week 5)
- [ ] Foundry integration (JIT tools)
- [ ] Witness integration (decision tracking)
- [ ] Brain integration (artifact storage)
- [ ] Gallery UI implementation

---

## Cross-References

- `spec/principles.md` — Core design principles
- `spec/theory/experience-quality-operad.md` — Quality measurement foundation
- `spec/theory/domains/wasm-survivors-quality.md` — Domain instantiation example
- `spec/ui/procedural-vitality.md` — Animation patterns
- `spec/services/foundry.md` — JIT compilation dependency
- `docs/creative/stark-biome-moodboard.md` — Design language foundation
- `pilots/wasm-survivors-game/ART_PIPELINE.md` — Asset pipeline archaeology source

---

*"The proof IS the decision. The mark IS the witness. The asset IS the vision made manifest."*

**Filed**: 2025-12-28
**Status**: Draft — Ready for implementation
