# Skill: Projection Gallery Pattern

> Build showcase galleries for multi-target widget systems.

**Difficulty**: Medium
**Prerequisites**: KgentsWidget, FastAPI, React
**Files**: `protocols/projection/gallery/`, `protocols/api/gallery.py`, `web/src/pages/GalleryPage.tsx`
**References**: `spec/protocols/projection.md`

---

## Overview

The Projection Gallery pattern creates a dense, interactive showcase of all widgets rendered to all projection targets. It serves three purposes:

1. **Developer iteration** - Rapid visual feedback on widget changes
2. **Protocol proof** - Demonstrates projection guarantees hold
3. **Documentation** - Living reference of available components

---

## The Three Layers

### Layer 1: Pilots (Backend)

A **Pilot** is a pre-configured widget demonstration with override hooks:

```python
from protocols.projection.gallery import Pilot, PilotCategory, register_pilot

@dataclass
class Pilot:
    name: str                     # Unique identifier
    category: PilotCategory       # Organization bucket
    description: str              # One-liner
    widget_factory: Callable[[dict], KgentsWidget]  # Creates widget
    tags: list[str]               # Searchable metadata
    variations: list[dict]        # Interactive presets

# Register a pilot
register_pilot(Pilot(
    name="bar_gradient",
    category=PilotCategory.PRIMITIVES,
    description="Gradient bar at 90%",
    widget_factory=lambda overrides: BarWidget(
        BarState(
            value=overrides.get("value", 0.9),
            style="gradient",
        )
    ),
    tags=["bar", "gradient", "health"],
))
```

**Key insight**: The factory receives overrides, enabling surgical state manipulation.

### Layer 2: API (REST Bridge)

The API layer serves pilots with their projections:

```python
from fastapi import APIRouter, Query
from protocols.projection.gallery import Gallery, PILOT_REGISTRY

router = APIRouter(prefix="/api/gallery")

@router.get("")
async def get_gallery(
    entropy: float | None = Query(None, ge=0.0, le=1.0),
    seed: int | None = Query(None),
    category: str | None = Query(None),
) -> GalleryResponse:
    gallery = Gallery(GalleryOverrides(entropy=entropy, seed=seed))

    pilots = []
    for name in PILOT_REGISTRY:
        pilot = PILOT_REGISTRY[name]
        projections = PilotProjections(
            cli=gallery.render(name, RenderTarget.CLI).output,
            html=gallery.render(name, RenderTarget.MARIMO).output,
            json=gallery.render(name, RenderTarget.JSON).output,
        )
        pilots.append(PilotResponse(
            name=name,
            category=pilot.category.name,
            projections=projections,
        ))

    return GalleryResponse(pilots=pilots, total=len(pilots))
```

**Response shape** ensures frontend can render any projection:

```json
{
  "pilots": [{
    "name": "glyph_idle",
    "category": "PRIMITIVES",
    "projections": {
      "cli": "○",
      "html": "<span class=\"kgents-glyph\">○</span>",
      "json": {"type": "glyph", "char": "○"}
    }
  }]
}
```

### Layer 3: Frontend (React Gallery)

The React frontend consumes the API and renders all pilots:

```tsx
// GalleryPage.tsx
export default function GalleryPage() {
  const [gallery, setGallery] = useState<GalleryResponse | null>(null);
  const [overrides, setOverrides] = useState<GalleryOverrides>({});
  const [category, setCategory] = useState<string>('ALL');

  // Fetch on override change
  useEffect(() => {
    galleryApi.getAll(overrides, category !== 'ALL' ? category : undefined)
      .then(r => setGallery(r.data));
  }, [overrides, category]);

  return (
    <div>
      <OverrideControls overrides={overrides} onChange={setOverrides} />
      <CategoryFilter active={category} onChange={setCategory} />
      <div className="grid grid-cols-4 gap-4">
        {gallery?.pilots.map(pilot => (
          <PilotCard key={pilot.name} pilot={pilot} />
        ))}
      </div>
    </div>
  );
}
```

---

## Override Injection

The override system enables rapid iteration without code changes:

### Hierarchy

```
CLI flags > Environment vars > Widget defaults
```

### Environment Variables

```bash
export KGENTS_GALLERY_ENTROPY=0.5     # Global entropy
export KGENTS_GALLERY_SEED=42         # Deterministic chaos
export KGENTS_GALLERY_PHASE=error     # Force phase
export KGENTS_GALLERY_TIME=1000       # Fixed time (ms)
```

### API Query Parameters

```
GET /api/gallery?entropy=0.5&seed=42&category=CARDS
```

### Programmatic

```python
gallery = Gallery(GalleryOverrides(
    entropy=0.3,
    seed=123,
    phase="active",
    widget_overrides={"agent_card_active": {"breathing": False}},
))
```

---

## Component Patterns

### PilotCard

Renders a single pilot with tab-based projection views:

```tsx
function PilotCard({ pilot }: { pilot: PilotResponse }) {
  const [tab, setTab] = useState<'cli' | 'html' | 'json'>('cli');

  return (
    <div className="card">
      <header>{pilot.name}</header>
      <div className="tabs">
        <button onClick={() => setTab('cli')}>CLI</button>
        <button onClick={() => setTab('html')}>HTML</button>
        <button onClick={() => setTab('json')}>JSON</button>
      </div>
      <div className="content">
        {tab === 'cli' && <pre>{pilot.projections.cli}</pre>}
        {tab === 'html' && <div dangerouslySetInnerHTML={{__html: pilot.projections.html}} />}
        {tab === 'json' && <pre>{JSON.stringify(pilot.projections.json, null, 2)}</pre>}
      </div>
    </div>
  );
}
```

### CategoryFilter

Tabs for filtering by category:

```tsx
function CategoryFilter({ categories, active, onChange }) {
  return (
    <div className="flex gap-2">
      <button onClick={() => onChange('ALL')}>All</button>
      {categories.map(cat => (
        <button key={cat} onClick={() => onChange(cat)}>{cat}</button>
      ))}
    </div>
  );
}
```

### OverrideControls

Real-time manipulation:

```tsx
function OverrideControls({ overrides, onChange }) {
  return (
    <div className="flex gap-4">
      <label>
        Entropy:
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={overrides.entropy ?? 0}
          onChange={e => onChange({...overrides, entropy: parseFloat(e.target.value)})}
        />
        {overrides.entropy?.toFixed(2)}
      </label>
      <label>
        Seed:
        <input
          type="number"
          value={overrides.seed ?? ''}
          onChange={e => onChange({...overrides, seed: parseInt(e.target.value) || undefined})}
        />
      </label>
    </div>
  );
}
```

---

## Adding New Pilots

1. **Create widget factory** in `pilots.py`:

```python
def _create_my_widget(overrides: dict[str, Any]) -> KgentsWidget[Any]:
    return MyWidget(MyState(
        value=overrides.get("value", 0.5),
        entropy=_get_entropy(overrides),
    ))
```

2. **Register the pilot**:

```python
register_pilot(Pilot(
    name="my_widget_demo",
    category=PilotCategory.SPECIALIZED,
    description="My widget with customizable value",
    widget_factory=_create_my_widget,
    tags=["custom", "demo"],
))
```

3. **Test locally**:

```bash
python -m protocols.projection.gallery --widget=my_widget_demo
```

---

## Verification

```bash
# Run gallery API tests
cd impl/claude
uv run pytest protocols/api/_tests/test_gallery.py -v

# Check CLI gallery works
python -m protocols.projection.gallery --all

# Verify web build
cd impl/claude/web
npm run build
```

---

## Best Practices

### 1. Cover All Widget States

Create pilots for normal, error, and edge cases:

```python
register_pilot(Pilot(name="agent_card_active", ...))
register_pilot(Pilot(name="agent_card_error", ...))
register_pilot(Pilot(name="agent_card_compact", ...))
```

### 2. Use Variations for Interactive Sweeps

```python
Pilot(
    name="bar_value_sweep",
    variations=[{"value": v} for v in [0.0, 0.25, 0.5, 0.75, 1.0]],
)
```

### 3. Tag Thoughtfully

Tags enable search and filtering:

```python
tags=["card", "agent", "error", "entropy", "streaming"]
```

### 4. Keep Factories Pure

Widget factories should be deterministic given overrides:

```python
# Good: deterministic
def factory(overrides):
    return Widget(State(seed=overrides.get("seed", 42)))

# Bad: non-deterministic
def factory(overrides):
    return Widget(State(seed=random.randint(0, 1000)))
```

---

## Related Skills

- [reactive-primitives](reactive-primitives.md) - Signal/Computed/Effect
- [turn-projectors](turn-projectors.md) - Multi-target rendering
- [saas-patterns](saas-patterns.md) - API endpoint patterns

---

## Source Reference

- `protocols/projection/gallery/` - Gallery module
- `protocols/api/gallery.py` - REST endpoints
- `web/src/pages/GalleryPage.tsx` - React page
- `web/src/components/gallery/` - React components

---

*Skill created: 2025-12-15 | Projection Protocol Phase*
