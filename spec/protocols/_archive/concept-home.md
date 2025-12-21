# Habitat Protocol (Projection Habitat)

> *"Every path deserves a home. The seam is where the protocol forgot to breathe."*

**Status:** Canonical Specification (Layer 1 Complete, Layers 2-3 Planned)
**Date:** 2025-12-18
**Prerequisites:** `projection.md`, `agentese.md`, `os-shell.md`, AD-009 (Metaphysical Fullstack)
**Implementation:**
- Layer 1: `impl/claude/web/src/shell/projections/ConceptHomeProjection.tsx` (✅ Complete)
- Layer 2: MiniPolynomial visualization (Planned)
- Layer 3: Ghost Integration (Planned)

**See also:** `plans/habitat-2.0.md`, `plans/ghost-integration.md`, `plans/mini-polynomial.md`, `plans/habitat-examples.md`

---

## Epigraph

> *"A LeetCode problem page is not just a problem. It's a context for understanding."*
>
> *"The REPL is not separate from the Concept Home. The REPL IS the default playground."*
>
> *"Arriving somewhere beats hitting a wall."*

---

## Part I: The Problem

The NavigationTree discovers AGENTESE paths via `/agentese/discover`. When a user clicks a path:

- **Crown Jewels** (Brain, Gestalt, Town, Park, Forge) → Rich pages with custom visualization
- **Lower-level nodes** (concept.*, void.*, primitive paths) → **Nothing**. Blank. 404 behavior.

This creates **seams**—holes in the application where exploration dead-ends. The user clicks, expecting to discover something, and finds a wall.

### Why This Violates Principles

| Principle | Violation |
|-----------|-----------|
| **Tasteful** | A blank page is untasteful. It signals "we didn't care about this." |
| **Joy-Inducing** | Dead-ends are the opposite of joy. Discovery should reward, not punish. |
| **Generative** | If the path exists in the registry, the experience should derive from it. |
| **Composable** | The projection functor should have a morphism for every registered path. |

---

## Part II: The Solution — AD-010: The Habitat Guarantee

### The Principle

> **Every registered AGENTESE path SHALL project into at least a minimal Habitat experience. No blank pages. No 404 behavior.**

A **Habitat** is a coherent, welcoming experience that makes exploration rewarding. It is the **minimum viable projection** for any AGENTESE path.

### The Categorical Formulation

```
Habitat : AGENTESENode → ProjectedExperience

For all registered paths p:
  Habitat(p) ≠ ∅
```

This is a **natural transformation** from the AGENTESE registry to the projection layer. Every node has an image; no node projects to nothing.

### The Affirmative Framing

**Not**: "No orphan paths" (negative)
**But**: "Every path has a home" (affirmative)

---

## Part II-A: Habitat 2.0 — The Three Enhancement Layers

**Version:** 2.0 (2025-12-18)
**Philosophy:** Bret Victor's Explorable Explanations — *"Every path is a place to think"*

The Habitat evolves beyond documentation into a **thinking environment** through three progressive enhancement layers:

### Formal Definition (Habitat 2.0)

```
Habitat : AGENTESENode → ProjectedExperience

For all registered nodes n:
  Habitat(n) = ReferencePanel(n) × Playground(n) × Teaching(n)

where:
  ReferencePanel(n) = n.metadata ∪ n.aspects ∪ MiniPolynomial(n)
  Playground(n)     = REPL.focus(n.path) ⊕ Examples(n) ⊕ Ghosts(n)
  Teaching(n)       = AspectHints × (enabled: TeachingMode)
```

### The Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: GHOSTS (Différance Integration)                    │
│   Show alternatives after invocation                        │
│   Exploration breadcrumbs                                   │
│   "What almost was" is visible                              │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: LIVE POLYNOMIAL                                    │
│   Mini state diagram in Reference Panel                     │
│   Current position highlighted                              │
│   Click transition to invoke                                │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: ADAPTIVE HABITAT (✅ implemented)                  │
│   ConceptHomeProjection as universal fallback               │
│   Teaching hints, breathing animations                      │
│   Context badges, cultivation messaging                     │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Component | Purpose | Status |
|-------|-----------|---------|--------|
| **Layer 1** | Adaptive Habitat | Universal fallback projection for all paths | ✅ Complete |
| **Layer 2** | MiniPolynomial | State machine visualization in Reference Panel | Planned |
| **Layer 3** | Ghost Integration | Différance made visible via alternatives | Planned |

### Layer 1: Adaptive Habitat (Complete)

The foundation—every path projects into a coherent experience:

- **ConceptHomeProjection** as universal fallback
- **Teaching hints** for aspects (micro-teaching)
- **Breathing animations** on active elements
- **Context badges** (world/self/concept/void/time)
- **Warm cultivation messaging** for minimal tier

### Layer 2: Live Polynomial (Planned)

Make state machines tangible via mini diagrams in Reference Panel:

```python
@aspect
async def polynomial(self, observer: Observer) -> PolynomialManifest:
    """Return state machine structure."""
    return PolynomialManifest(
        positions=("idle", "active", "exhausted"),
        current="idle",
        directions={
            "idle": ("greet", "nurture"),
            "active": ("dialogue", "rest"),
            "exhausted": ("rest",)
        }
    )
```

Rendered as interactive mini-diagram:

```
┌─────────────────────────────┐
│  ● idle ──greet──> active   │
│    │                 │      │
│    └────<nurture─────┘      │
└─────────────────────────────┘
```

Click transition to invoke. Connection to AD-002 (Polynomial Generalization).

### Layer 3: Ghost Integration (Planned)

Différance made visible—show alternatives after invocation:

```python
@aspect
async def alternatives(
    self, observer: Observer, invoked_aspect: str = "manifest"
) -> list[Ghost]:
    """Return sibling aspects not yet invoked (ghosts)."""
    affordances = self.affordances(observer)
    return [
        Ghost(aspect=a, hint=f"try {a}")
        for a in affordances if a != invoked_aspect
    ][:5]
```

UI after successful invocation:

```
✓ manifest returned CitizenManifest

  Other possibilities:
  👻 polynomial — see state machine
  👻 greet — initiate dialogue
  👻 gossip — hear citizen rumors
```

Click ghost to explore. **Breadcrumb trail** tracks exploration.

### Progressive Enhancement Table

| Feature | Layer 1 | Layer 2 | Layer 3 |
|---------|---------|---------|---------|
| **Fallback projection** | ✅ | ✅ | ✅ |
| **Teaching hints** | ✅ | ✅ | ✅ |
| **Breathing animations** | ✅ | ✅ | ✅ |
| **One-click examples** | Planned | ✅ | ✅ |
| **State machine viz** | - | ✅ | ✅ |
| **Ghost alternatives** | - | - | ✅ |
| **Exploration trail** | - | - | ✅ |

### Connection to AD-002 and AD-006

**Layer 2 (MiniPolynomial)** IS the visualization of AD-002 (Polynomial Generalization):

- PolyAgent[S, A, B] > Agent[A, B]
- S = positions (states)
- E: S → Set(A) = direction function
- MiniPolynomial makes this VISIBLE and CLICKABLE

**Layer 3 (Ghosts)** embodies the Unified Categorical Foundation (AD-006):

- Polynomial: Current position + directions
- Operad: Valid transitions (composition grammar)
- Sheaf: Coherence across exploration trail

### Implementation References

- Layer 1: `impl/claude/web/src/shell/projections/ConceptHomeProjection.tsx`
- Layer 2: `plans/mini-polynomial.md`
- Layer 3: `plans/ghost-integration.md`
- Examples: `plans/habitat-examples.md`
- Umbrella: `plans/habitat-2.0.md`

---

## Part III: The Three Habitat Tiers

Habitats scale with available metadata. More definition → richer experience.

| Tier | Metadata Required | Experience |
|------|-------------------|------------|
| **Minimal** | Path only | Path header + context badge + warm "Coming soon" copy + REPL input |
| **Standard** | Description + aspects | Reference Panel + REPL seeded with example invocations |
| **Rich** | Custom playground specified | Full bespoke visualization (Crown Jewels) |

### Tier Detection

```typescript
type HabitatTier = 'minimal' | 'standard' | 'rich';

function getHabitatTier(metadata: HomeMetadata): HabitatTier {
  if (metadata.playground) return 'rich';
  if (metadata.description && metadata.aspects?.length > 0) return 'standard';
  return 'minimal';
}
```

### Progressive Enhancement

```
Path registered          → Minimal Habitat (warm copy, REPL input)
+ description            → Standard Habitat (Reference Panel appears)
+ aspects                → Aspect buttons in playground
+ effects                → Effects section in Reference Panel
+ examples               → Pre-seeded REPL examples
+ playground component   → Rich Habitat (bespoke visualization)
```

**Key Insight**: The system never shows a blank page. Even a path with no metadata gets a Minimal Habitat with:
- The path name, styled
- The context badge (world/self/concept/void/time)
- A warm message: "This path is being cultivated. Try invoking it directly."
- A REPL input focused on that path

---

## Part IV: The Five Home Archetypes

Each AGENTESE context has a natural experience shape. When no custom playground is specified, the default playground matches the archetype.

| Context | Archetype | Default Playground | Teaching Focus |
|---------|-----------|-------------------|----------------|
| `concept.*` | **Category Playground** | PolynomialPlayground, OperadViz, etc. | Categorical theory, mathematical foundations |
| `world.*` | **Entity Inspector** | Live invocation + entity state display | Holon hierarchy, part-whole relationships |
| `self.*` | **Introspection Panel** | Capability list, state visualization | Agent identity, memory, capability |
| `void.*` | **Entropy Sandbox** | Randomness tools, sip/pour controls | Accursed Share, surplus expenditure |
| `time.*` | **Timeline Browser** | Trace visualization, history scrubber | Différance, temporal traces |

### Context Badge

Each Habitat displays a context badge that immediately signals which domain the user is exploring:

```typescript
const CONTEXT_INFO = {
  world:   { icon: Globe,     color: 'green',  label: 'External entities' },
  self:    { icon: User,      color: 'cyan',   label: 'Internal state' },
  concept: { icon: BookOpen,  color: 'violet', label: 'Abstract definitions' },
  void:    { icon: Sparkles,  color: 'pink',   label: 'Entropy & serendipity' },
  time:    { icon: Clock,     color: 'amber',  label: 'Temporal traces' },
};
```

---

## Part V: The Habitat Layout

### The LeetCode-Style Pattern

Inspired by LeetCode's problem pages, where every problem—not just featured ones—gets a structured home:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PATH HEADER                                                                │
│  concept.polynomial                                        [concept] badge  │
├────────────────────────────────┬────────────────────────────────────────────┤
│    REFERENCE PANEL             │         PLAYGROUND AREA                    │
│    ─────────────────          │         ────────────────                   │
│                                │                                            │
│    Description                 │    ┌─────────────────────────────────┐    │
│    ────────────               │    │  [Custom Viz or Generated REPL] │    │
│    Polynomial functor agent    │    │                                 │    │
│    P(y) = Σ y^{directions(s)} │    │  Interactive experience         │    │
│                                │    │  appropriate to tier            │    │
│    Aspects                     │    │                                 │    │
│    ───────                    │    └─────────────────────────────────┘    │
│    [manifest] [transition]    │                                            │
│    [directions]               │    Output                                  │
│                                │    ──────                                 │
│    Effects                     │    { result of last invocation }          │
│    ───────                    │                                            │
│    reads: state               │                                            │
│                                │                                            │
│    Related                     │                                            │
│    ───────                    │                                            │
│    concept.operad             │                                            │
│    concept.sheaf              │                                            │
│                                │                                            │
├────────────────────────────────┴────────────────────────────────────────────┤
│    TEACHING CALLOUT (toggleable via Teaching Mode)                          │
│    PolyAgent[S,A,B] enables state-dependent inputs. Each position (state)  │
│    determines which inputs are valid. This is the foundation of kgents.    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Structure

```
ConceptHome
├── PathHeader
│   ├── PathBreadcrumb ("concept" > "polynomial")
│   ├── PathName
│   └── ContextBadge
├── HabitatLayout (density-adaptive)
│   ├── ReferencePanel (left sidebar / mobile drawer)
│   │   ├── DescriptionSection
│   │   ├── AspectsSection (clickable → invoke in playground)
│   │   ├── EffectsSection
│   │   ├── ExamplesSection
│   │   └── RelatedPathsSection (clickable → navigate)
│   └── PlaygroundArea (main content)
│       ├── CustomPlayground (if tier = rich)
│       └── GeneratedPlayground (if tier = standard/minimal)
│           ├── REPLInput (pre-focused on this path)
│           ├── AspectButtons
│           └── OutputPanel
└── TeachingCallout (footer, toggleable)
```

---

## Part VI: Density Adaptation

Following the Projection Protocol (AD-008), Habitats adapt to screen density:

### The Three Modes

| Density | Reference Panel | Playground | Teaching |
|---------|-----------------|------------|----------|
| **Spacious** (≥1024px) | Fixed sidebar, 280px | Full width minus sidebar | Inline footer |
| **Comfortable** (768-1023px) | Collapsible panel, toggle button | Full width when collapsed | Collapsible footer |
| **Compact** (<768px) | Bottom drawer, FAB trigger | Full screen | Inline in drawer |

### Layout Transformation

```
Spacious:
┌──────────────┬─────────────────────────────────┐
│  Reference   │           Playground             │
│   (280px)    │                                  │
└──────────────┴─────────────────────────────────┘

Comfortable:
┌─────────────────────────────────────────────────┐
│                  Playground                      │  [Toggle: Reference Panel]
└─────────────────────────────────────────────────┘

Compact:
┌─────────────────────────────────────────────────┐
│                  Playground                [FAB] │
├─────────────────────────────────────────────────┤
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐│
│  │          Reference (drawer)               │ │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘│
└─────────────────────────────────────────────────┘
```

---

## Part VII: The REPL Fusion

### The Insight

The AGENTESE REPL (AD-007: Liturgical CLI) and the Concept Home are not separate experiences. **The REPL becomes the playground for paths without bespoke components.**

When you enter a Concept Home for `concept.polynomial`:

1. The **Reference Panel** shows documentation, aspects, effects
2. The **Playground** is a REPL pre-focused on that path
3. Clicking an aspect button in Reference → invokes it in the Playground
4. The output appears in the Playground's output panel

### The Generated Playground

For Standard and Minimal tiers:

```typescript
function GeneratedPlayground({ path, aspects, examples }: Props) {
  const [output, setOutput] = useState<unknown>(null);

  return (
    <div>
      {/* Aspect buttons */}
      <div className="flex gap-2 mb-4">
        {aspects.map(aspect => (
          <button
            key={aspect}
            onClick={() => invoke(path, aspect)}
            className="px-3 py-1 bg-gray-700 rounded"
          >
            {aspect}
          </button>
        ))}
      </div>

      {/* REPL input */}
      <REPLInput
        defaultPath={path}
        onResult={setOutput}
        examples={examples}
      />

      {/* Output */}
      <OutputPanel data={output} />
    </div>
  );
}
```

---

## Part VIII: The @node Decorator Extension

### Home Metadata

The `@node` decorator accepts optional `home` metadata:

```python
@node(
    "concept.polynomial",
    description="Polynomial functor agent: P(y) = Σ y^{directions(s)}",
    home={
        "playground": "PolynomialPlayground",  # React component name
        "examples": [
            "concept.polynomial.manifest",
            "concept.polynomial.transition idle ACTIVE",
        ],
        "related": ["concept.operad", "concept.sheaf"],
        "teaching": """
            PolyAgent[S,A,B] enables state-dependent inputs. Each position
            (state) determines which inputs are valid—like a traffic light
            that only accepts "change" when it's been green long enough.
        """,
    }
)
class PolynomialNode:
    ...
```

### Fallback Generation

When no explicit `home` is provided, generate from available node metadata:

| Source | Generated Field |
|--------|-----------------|
| Class docstring | `description` |
| `@aspect` decorators | `aspects` list |
| `effects=` in aspects | `effects` list |
| Type annotations | Input form hints (future) |

```python
def generate_home_metadata(node_class: type) -> HomeMetadata:
    """Generate Habitat metadata from node class introspection."""

    return HomeMetadata(
        path=node_class._agentese_path,
        context=node_class._agentese_path.split('.')[0],
        description=node_class.__doc__,
        aspects=[a.name for a in get_aspects(node_class)],
        effects=[str(e) for a in get_aspects(node_class) for e in a.effects],
        # playground, examples, related, teaching default to None
    )
```

---

## Part IX: Discovery Enhancement

### /agentese/discover Response

```python
# GET /agentese/discover?include_homes=true

{
    "paths": ["self.memory", "concept.polynomial", "void.entropy", ...],
    "stats": {
        "registered_nodes": 42,
        "contexts": ["world", "self", "concept", "void", "time"]
    },
    "homes": {
        "concept.polynomial": {
            "path": "concept.polynomial",
            "context": "concept",
            "tier": "rich",
            "description": "Polynomial functor agent...",
            "aspects": ["manifest", "transition", "directions"],
            "effects": ["reads:state"],
            "playground": "PolynomialPlayground",
            "examples": ["concept.polynomial.manifest", ...],
            "related": ["concept.operad", "concept.sheaf"],
            "teaching": "PolyAgent[S,A,B] enables..."
        },
        "void.entropy": {
            "path": "void.entropy",
            "context": "void",
            "tier": "standard",
            "description": "Entropy reservoir for the Accursed Share",
            "aspects": ["sip", "pour", "tithe", "manifest"],
            "effects": ["reads:entropy", "writes:entropy"],
            "playground": null,  // Uses GeneratedPlayground
            "examples": ["void.entropy.sip 0.1"],
            "related": ["void.gratitude"],
            "teaching": null
        },
        "world.undocumented": {
            "path": "world.undocumented",
            "context": "world",
            "tier": "minimal",
            "description": null,
            "aspects": ["manifest"],
            "effects": [],
            "playground": null,
            "examples": [],
            "related": [],
            "teaching": null
        }
    }
}
```

---

## Part X: Routing Strategy

### The Fallback Route

Paths without explicit React routes fall through to the Concept Home:

```typescript
// App.tsx routes
<Routes>
  {/* Explicit Crown Jewel routes */}
  <Route path="/brain" element={<BrainPage />} />
  <Route path="/gestalt/*" element={<GestaltPage />} />
  <Route path="/town/*" element={<TownPage />} />
  <Route path="/park/*" element={<ParkPage />} />
  <Route path="/forge/*" element={<ForgePage />} />
  <Route path="/gardener/*" element={<GardenerPage />} />

  {/* NEW: Concept Home fallback */}
  <Route path="/home/*" element={<ConceptHomePage />} />

  {/* Gallery */}
  <Route path="/gallery/*" element={<GalleryPage />} />

  {/* 404 */}
  <Route path="*" element={<NotFound />} />
</Routes>
```

### NavigationTree Enhancement

```typescript
const handleNavigateToPath = (path: string) => {
  // Check for explicit route mapping
  const explicitRoute = pathToRoute[path];
  if (explicitRoute) {
    navigate(explicitRoute);
    return;
  }

  // Fallback: Concept Home
  // Transform "concept.polynomial" → "/home/concept/polynomial"
  const segments = path.split('.');
  navigate(`/home/${segments.join('/')}`);
};
```

### URL ↔ Path Mapping

```
URL: /home/concept/polynomial
↓
AGENTESE Path: concept.polynomial
↓
Fetch: GET /agentese/discover?include_homes=true
↓
Render: ConceptHome with metadata
```

---

## Part XI: Observer-Aware Rendering

Following the AGENTESE principle ("No view from nowhere"), Habitats adapt to the observer:

| Observer Archetype | Habitat Adaptation |
|-------------------|-------------------|
| **developer** | Show trace strip, full effects, debug info |
| **learner** | Teaching Mode on by default, examples prominent |
| **operator** | Emphasize effects, show invocation metrics |
| **guest** | Simplified view, hide effects, emphasize examples |

```typescript
function ReferencePanel({ metadata, observer }: Props) {
  const showEffects = observer.capabilities.has('admin') ||
                      observer.archetype === 'developer';
  const showTraces = observer.archetype === 'developer';

  return (
    <div>
      <DescriptionSection text={metadata.description} />
      <AspectsSection aspects={metadata.aspects} />
      {showEffects && <EffectsSection effects={metadata.effects} />}
      {showTraces && <TraceStrip path={metadata.path} />}
      <RelatedSection paths={metadata.related} />
    </div>
  );
}
```

---

## Part XII: Living Earth Aesthetic

Habitats use the Living Earth palette established in the visual system:

| Element | Colors | Motion |
|---------|--------|--------|
| **Reference Panel** | Warm earth (bark, wood grain) | Subtle grain texture |
| **Playground** | Sage/fern greens | Breathing pulse on active |
| **Teaching Callout** | Amber/copper highlights | Gentle fade in |
| **Context Badge** | Context-specific color | None |
| **Aspect Buttons** | Muted earth with hover glow | Lift on hover |

### The Breathing Pulse

Active elements (currently invoking, streaming) use a subtle breathing animation:

```css
@keyframes breathe {
  0%, 100% { opacity: 0.9; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
}

.habitat-active {
  animation: breathe 2s ease-in-out infinite;
}
```

---

## Part XIII: Warm Copy (Minimal Tier)

When a path has no metadata, the Minimal Habitat still feels welcoming:

```typescript
const MINIMAL_COPY = {
  heading: "This path is being cultivated",
  body: `
    Every kgents path grows from a seed. This one is young—
    its documentation and visualizations are still forming.

    You can still explore it directly via the REPL below.
  `,
  cta: "Try invoking it",
};
```

**Key Insight**: The warm copy signals intentionality, not incompleteness. "Being cultivated" is garden language—fitting for "the persona is a garden, not a museum."

---

## Part XIV: Integration Points

### Teaching Mode

Habitats integrate with the global Teaching Mode toggle:

```typescript
const { teachingEnabled } = useTeachingMode();

return (
  <ConceptHome>
    <ReferencePanel />
    <Playground />
    {teachingEnabled && metadata.teaching && (
      <TeachingCallout content={metadata.teaching} />
    )}
  </ConceptHome>
);
```

### Trace Collection

Every Habitat invocation is traced for devex visibility:

```typescript
const tracedInvoke = useTracedInvoke();

const handleInvoke = async (aspect: string) => {
  await tracedInvoke(path, aspect, async () => {
    const result = await apiClient.post(`/agentese/${path}/${aspect}`);
    return result;
  });
};
```

### Terminal Integration

The Habitat playground can sync with the Terminal:

```typescript
// Clicking aspect in Reference Panel
const handleAspectClick = (aspect: string) => {
  // Option 1: Invoke directly in playground
  invokeInPlayground(aspect);

  // Option 2: Send to Terminal (if open)
  if (terminalOpen) {
    sendToTerminal(`${path}.${aspect}`);
  }
};
```

---

## Part XV: Anti-Patterns

| Anti-Pattern | Why Bad | Correct Pattern |
|--------------|---------|-----------------|
| **Blank 404 for unmapped paths** | Violates Habitat Guarantee | Always render at least Minimal Habitat |
| **Custom component for every path** | Unsustainable | Use Generated Playground as default |
| **Effects in guest view** | Information overload | Observer-aware rendering |
| **Teaching always on** | Fatiguing | Toggleable, off by default for guests |
| **Dense copy in Minimal tier** | Feels like error page | Warm, brief copy |
| **Scattered playground components** | Maintenance nightmare | Register in `home.playground` |

---

## Part XVI: Implementation Phases

### Phase 1: Types & Backend (1-2 days)
- [ ] Define `HomeMetadata` dataclass in `protocols/agentese/home.py`
- [ ] Extend `@node` decorator to accept `home={}` parameter
- [ ] Add `generate_home_metadata()` fallback function
- [ ] Extend `/agentese/discover` with `?include_homes=true`

### Phase 2: Core Components (2-3 days)
- [ ] Create `shell/ConceptHome.tsx` main wrapper
- [ ] Create `shell/ReferencePanel.tsx` sidebar
- [ ] Create `shell/GeneratedPlayground.tsx` with REPL
- [ ] Create `shell/TeachingCallout.tsx` footer
- [ ] Add density adaptation (use ElasticSplit, BottomDrawer)

### Phase 3: Routing & Integration (1 day)
- [ ] Add `/home/*` fallback route to App.tsx
- [ ] Update NavigationTree with fallback navigation
- [ ] Connect to Teaching Mode context
- [ ] Wire trace collection

### Phase 4: Pilots (1-2 days)
- [ ] `concept.polynomial` — Test Rich tier with custom playground
- [ ] `void.entropy` — Test Standard tier with generated playground
- [ ] Undocumented path — Test Minimal tier

### Phase 5: Polish (1 day)
- [ ] Apply Living Earth palette
- [ ] Add breathing animations
- [ ] Write warm copy variants
- [ ] Accessibility audit (keyboard nav, screen reader)

---

## Part XVII: Success Criteria

### Quantitative

| Metric | Target |
|--------|--------|
| Paths with blank/404 behavior | **0** |
| ConceptHome total LOC | <500 |
| Time to Minimal Habitat render | <100ms |
| Lighthouse accessibility score | ≥90 |

### Qualitative

- [ ] Clicking any path in NavigationTree lands somewhere meaningful
- [ ] Minimal tier feels like "arriving" not "hitting a wall"
- [ ] Standard tier enables exploration without custom code
- [ ] Rich tier is indistinguishable from Crown Jewel pages
- [ ] Teaching Mode works consistently across all tiers
- [ ] Mobile drawer pattern feels natural
- [ ] Power users can invoke aspects directly from Reference Panel

---

## Part XVIII: Connection to Principles

| Principle | How Habitat Embodies It |
|-----------|------------------------|
| **Tasteful** | No blank pages; every path gets considered treatment |
| **Curated** | Three tiers ensure quality scales with investment |
| **Ethical** | Observer-aware rendering respects capability |
| **Joy-Inducing** | Warm copy, breathing animations, discovery rewards |
| **Composable** | Habitat is a morphism; composes with Projection Protocol |
| **Heterarchical** | No path is "lesser"; all project appropriately |
| **Generative** | Tier derives from metadata; implementation follows spec |

---

## Part XIX: Future Extensions

### 19.1 Ghost Paths

Show paths from spec that have no implementation yet:

```typescript
interface GhostPath {
  path: string;
  specReference: string;  // Link to spec file
  status: 'planned' | 'in-progress' | 'blocked';
}

// Render with dashed border, muted colors
<GhostHabitat path={ghostPath} />
```

### 19.2 Playground Component Registry

Allow service modules to register custom playgrounds:

```typescript
// services/brain/web/playgrounds.ts
registerPlayground('CrystalExplorer', CrystalExplorerComponent);
registerPlayground('PolynomialPlayground', PolynomialPlaygroundComponent);

// ConceptHome looks up by name
const Playground = getRegisteredPlayground(metadata.playground);
```

### 19.3 Example Invocation Presets

Pre-configured example invocations users can run with one click:

```python
home={
    "examples": [
        {"label": "Simple manifest", "invocation": "concept.polynomial.manifest"},
        {"label": "State transition", "invocation": "concept.polynomial.transition idle ACTIVE"},
    ]
}
```

---

## Appendix A: HomeMetadata TypeScript Types

```typescript
// shell/types.ts

export type HabitatTier = 'minimal' | 'standard' | 'rich';

export interface HomeMetadata {
  /** Full AGENTESE path */
  path: string;

  /** Context (world, self, concept, void, time) */
  context: 'world' | 'self' | 'concept' | 'void' | 'time';

  /** Computed tier */
  tier: HabitatTier;

  /** Node description (from docstring or explicit) */
  description: string | null;

  /** Available aspects */
  aspects: string[];

  /** Declared effects */
  effects: string[];

  /** Custom playground component name (if rich tier) */
  playground: string | null;

  /** Example invocations */
  examples: string[];

  /** Related AGENTESE paths */
  related: string[];

  /** Teaching callout content */
  teaching: string | null;
}

export function getHabitatTier(metadata: HomeMetadata): HabitatTier {
  if (metadata.playground) return 'rich';
  if (metadata.description && metadata.aspects.length > 0) return 'standard';
  return 'minimal';
}
```

---

## Appendix B: Related Specifications

| Spec | Relationship |
|------|--------------|
| `spec/protocols/projection.md` | Habitat is a projection target; uses density adaptation |
| `spec/protocols/agentese.md` | Habitat renders AGENTESE paths; uses discovery |
| `spec/protocols/os-shell.md` | Habitat integrates with Terminal, NavigationTree |
| `spec/principles.md` AD-009 | Habitat extends Metaphysical Fullstack to projection |
| `spec/principles.md` AD-010 | The Habitat Guarantee principle |
| `docs/skills/elastic-ui-patterns.md` | Density patterns used in Habitat layout |

---

*"The seams disappear when every path has somewhere to go."*

*Last updated: 2025-12-18*
