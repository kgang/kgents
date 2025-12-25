# KGENTS ICON/GLYPH SYSTEM

> *"Mathematical notation meets ancient glyphs. Stillness, then life."*

## Philosophy

The kgents icon system replaces emojis with authentic, whimsical glyphs that feel like **mathematical notation** and **ancient inscriptions**.

### Design Principles

- **Flat geometric precision** — no 3D, gradients, or glassmorphism
- **Steel surfaces** — monochrome foundation with single accent
- **Stillness then breath** — 4-7-8 asymmetric animation timing
- **Mathematical aesthetic** — proof-engine notation, categorical precision
- **Earned glow** — movement and color are rewards, not defaults

### Anti-Patterns (AVOID)

- 3D clay effects
- Glassmorphism
- Y2K metallic gradients
- Bouncy spring animations
- Saturated colors
- Symmetric breathing animations

---

## Quick Start

```tsx
import { Glyph, GLYPHS } from '@/components/icons';

// Basic usage
<Glyph name="status.healthy" />

// With size variant
<Glyph name="actions.witness" size="lg" />

// With breathing animation (4-7-8 timing)
<Glyph name="jewels.brain" breathing />

// With custom color
<Glyph name="contexts.world" color="var(--life-sage)" />

// Direct glyph access
const healthyGlyph = GLYPHS.status.healthy; // '●'
```

---

## Glyph Categories

### Status (`GLYPHS.status`)

Geometric precision for state indication:

| Name | Glyph | Meaning |
|------|-------|---------|
| `healthy` | `●` | Active, healthy, operational |
| `degraded` | `◐` | Partially functional |
| `dormant` | `○` | Inactive, dormant |
| `error` | `◆` | Error, attention required |
| `warning` | `◇` | Warning, caution |
| `pending` | `◎` | Pending, processing |

**Usage**:
```tsx
<Glyph name="status.healthy" className="glyph--healthy" />
<Glyph name="status.degraded" className="glyph--degraded" />
<Glyph name="status.error" className="glyph--critical" />
```

---

### AGENTESE Contexts (`GLYPHS.contexts`)

The five-fold ontology:

| Context | Glyph | Meaning |
|---------|-------|---------|
| `world` | `∴` | The External (therefore — external causality) |
| `self` | `∵` | The Internal (because — internal causality) |
| `concept` | `⟨⟩` | The Abstract (angle brackets) |
| `void` | `∅` | The Accursed Share (empty set) |
| `time` | `⟳` | The Temporal (cyclical flow) |

**Usage**:
```tsx
<Glyph name="contexts.world" />
<Glyph name="contexts.self" />
<Glyph name="contexts.concept" />
```

---

### Actions (`GLYPHS.actions`)

Proof-engine operations:

| Action | Glyph | Meaning |
|--------|-------|---------|
| `witness` | `⊢` | Witness, proof (turnstile) |
| `decide` | `⊨` | Decide, semantic consequence |
| `compose` | `∘` | Compose (ring operator) |
| `save` | `⊕` | Save, add (circled plus) |
| `search` | `⌕` | Search (telephone location) |
| `analyze` | `⊛` | Analyze (circled asterisk) |
| `edit` | `⎔` | Edit (software function) |
| `delete` | `⊖` | Delete (circled minus) |

**Usage**:
```tsx
<button onClick={handleWitness}>
  <Glyph name="actions.witness" size="sm" />
  Witness
</button>
```

---

### Axioms (`GLYPHS.axioms`)

The seven principles:

| Axiom | Glyph | Principle |
|-------|-------|-----------|
| `entity` | `◇` | Entity |
| `morphism` | `◈` | Morphism |
| `mirror` | `◉` | Mirror Test |
| `tasteful` | `✧` | Tasteful |
| `composable` | `⊛` | Composable |
| `heterarchical` | `⥮` | Heterarchical |
| `generative` | `⟐` | Generative |

---

### Navigation (`GLYPHS.navigation`)

Simple directional glyphs:

| Name | Glyph |
|------|-------|
| `back` | `←` |
| `forward` | `→` |
| `up` | `↑` |
| `down` | `↓` |
| `expand` | `⌄` |
| `collapse` | `⌃` |
| `menu` | `☰` |

---

### Files (`GLYPHS.files`)

Document types:

| Type | Glyph |
|------|-------|
| `file` | `▫` |
| `folder` | `▪` |
| `spec` | `◈` |
| `code` | `⟨⟩` |

---

### Crown Jewels (`GLYPHS.jewels`)

Service identities:

| Jewel | Glyph |
|-------|-------|
| `brain` | `◬` |
| `witness` | `⊢` |
| `atelier` | `⌬` |
| `liminal` | `◭` |

---

### Hypergraph Modes (`GLYPHS.modes`)

Modal editing states:

| Mode | Glyph |
|------|-------|
| `normal` | `◇` |
| `insert` | `◈` |
| `edge` | `⟡` |
| `visual` | `◉` |
| `witness` | `⊢` |

---

## Size Variants

| Size | Font Size | Use Case |
|------|-----------|----------|
| `xs` | 10px | Inline text, compact UI |
| `sm` | 12px | Default inline size |
| `md` | 14px | Standard glyph size |
| `lg` | 18px | Prominent glyphs, headers |

```tsx
<Glyph name="status.healthy" size="xs" />
<Glyph name="status.healthy" size="sm" />
<Glyph name="status.healthy" size="md" />
<Glyph name="status.healthy" size="lg" />
```

---

## Breathing Animation

The 4-7-8 asymmetric breathing animation (6.75s cycle) follows STARK BIOME philosophy:

**Timing breakdown**:
- **Rest** (0-15%): 0.985 opacity — stillness before inhale
- **Gentle Rise** (15-40%): 0.985 → 1.0 — soft inhale
- **Brief Hold** (40-50%): 1.0 — moment of fullness
- **Slow Release** (50-95%): 1.0 → 0.985 — long, calming exhale
- **Return** (95-100%): 0.985 — back to rest

**When to use**:
- Health indicators (active, healthy state)
- User presence markers
- Active connections
- Living elements (explicitly marked as "alive")

**When NOT to use**:
- Navigation
- Buttons (until hover)
- Text
- Static content
- Inactive elements

```tsx
// Earned breathing on healthy status
<Glyph name="status.healthy" breathing className="glyph--healthy" />

// Living jewel (brain service active)
<Glyph name="jewels.brain" breathing />
```

---

## Color Utilities

CSS utility classes for semantic colors:

```tsx
// Steel (muted)
<Glyph name="status.dormant" className="glyph--steel" />

// Life (organic accent)
<Glyph name="actions.witness" className="glyph--life" />

// Glow (earned moment)
<Glyph name="axioms.tasteful" className="glyph--glow" />

// Health states
<Glyph name="status.healthy" className="glyph--healthy" />
<Glyph name="status.degraded" className="glyph--degraded" />
<Glyph name="status.warning" className="glyph--warning" />
<Glyph name="status.error" className="glyph--critical" />

// Hover glow (earned interaction)
<Glyph name="actions.compose" className="glyph--hover-glow" />
```

---

## Lucide Icon Allowlist

For cases where glyphs aren't sufficient, use the curated Lucide subset:

```tsx
import { ArrowLeft, Check, Folder } from '@/components/icons';

<ArrowLeft size={16} />
<Check size={14} />
<Folder size={18} />
```

**Available categories**:
- **Navigation**: ArrowLeft, ArrowRight, ArrowUp, ArrowDown, ChevronDown, etc.
- **Files**: File, FileText, Folder, FolderOpen
- **Actions**: Save, Search, Settings, Filter, Plus, Minus, X, Check
- **Graph**: GitBranch, Network, Link, Unlink
- **Witness**: Eye, EyeOff, Sparkles, Crosshair
- **UI**: Menu, MoreHorizontal, MoreVertical, Maximize2, Minimize2

---

## Advanced Usage

### Helper Functions

```tsx
import { getGlyph, getGlyphCategory, GLYPH_CATEGORIES } from '@/components/icons';

// Get glyph by path
const glyph = getGlyph('status.healthy'); // '●'

// Get all glyphs in category
const statusGlyphs = getGlyphCategory('status');
// { healthy: '●', degraded: '◐', ... }

// Iterate categories
GLYPH_CATEGORIES.forEach(category => {
  console.log(category, getGlyphCategory(category));
});
```

### Dynamic Glyphs

```tsx
const StatusIndicator = ({ status }: { status: string }) => {
  const glyphName = `status.${status}`;
  return <Glyph name={glyphName} className={`glyph--${status}`} />;
};

<StatusIndicator status="healthy" />
<StatusIndicator status="degraded" />
```

---

## Design Tokens

All glyphs use STARK BIOME design tokens:

```css
/* From globals.css and design-system.css */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
--steel-300: #a0a0a0;
--life-sage: #4a6b4a;
--glow-spore: #c4a77d;
--health-healthy: #22c55e;
--health-degraded: #facc15;
--health-warning: #f97316;
--health-critical: #ef4444;
```

---

## Accessibility

All glyphs include proper ARIA labels:

```tsx
// Default: uses glyph name
<Glyph name="status.healthy" />
// aria-label="status healthy"

// Custom label
<Glyph name="status.healthy" aria-label="Service is operational" />
```

Reduced motion support is built-in:

```css
@media (prefers-reduced-motion: reduce) {
  .glyph--breathing {
    animation: none !important;
  }
}
```

---

## Migration from Emojis

**Before**:
```tsx
<span>🟢</span> Healthy
<span>⚠️</span> Warning
<span>❌</span> Error
```

**After**:
```tsx
<Glyph name="status.healthy" className="glyph--healthy" /> Healthy
<Glyph name="status.warning" className="glyph--warning" /> Warning
<Glyph name="status.error" className="glyph--critical" /> Error
```

---

## Connection to Principles

| Principle | How Glyphs Embody It |
|-----------|----------------------|
| **Tasteful** | Mathematical precision, not decorative |
| **Curated** | Limited set, each glyph earns its place |
| **Ethical** | Accessible, reduced motion support |
| **Joy-Inducing** | Breathing animation, earned glow |
| **Composable** | Type-safe helpers, consistent API |
| **Heterarchical** | No fixed hierarchy, context determines use |
| **Generative** | Categories generate consistent patterns |

---

*"The glyph is notation. The breath is life. The steel is humble. The glow is earned."*

*Created: 2025-12-24*
