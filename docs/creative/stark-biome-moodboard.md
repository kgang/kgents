# STARK BIOME Mood Board

> *"The frame is humble. The content glows."*

**Created**: 2025-12-22
**Supersedes**: crown-jewels-genesis-moodboard.md (kept for reference)
**Status**: Living Document — Implementation Guide

---

## The Dialectic

```
Steel (90%)                    Life (10%)
─────────────────────────────────────────────────
Cold, industrial               Warm, organic
Precision, discipline          Growth, emergence
Background, frame              Foreground, content
Always present                 Earned through action
Obsidian → Gunmetal            Moss → Sage → Sprout
"The frame"                    "The glow"
```

**The Rule**: Most things are still. Movement is earned.

---

## Color System (STARK Palette)

### Steel Foundation (90% — backgrounds, frames, containers)

| Name | Hex | Usage |
|------|-----|-------|
| `steel-obsidian` | `#0A0A0C` | Deepest background (canvas) |
| `steel-carbon` | `#141418` | Card backgrounds |
| `steel-slate` | `#1C1C22` | Elevated surfaces |
| `steel-gunmetal` | `#28282F` | Borders, dividers |
| `steel-zinc` | `#3A3A44` | Muted text, inactive states |

### Living Accent (10% — success, growth, life emerging)

| Name | Hex | Usage |
|------|-----|-------|
| `life-moss` | `#1A2E1A` | Deep living background |
| `life-fern` | `#2E4A2E` | Living surface |
| `life-sage` | `#4A6B4A` | Primary living accent (buttons, links) |
| `life-mint` | `#6B8B6B` | Living text |
| `life-sprout` | `#8BAB8B` | Living highlight |

### Bioluminescent (earned — highlights, focus, precious moments)

| Name | Hex | Usage |
|------|-----|-------|
| `glow-spore` | `#C4A77D` | Warm accent (focus states) |
| `glow-amber` | `#D4B88C` | Warning, attention |
| `glow-light` | `#E5C99D` | Brightest earned glow |
| `glow-lichen` | `#8BA98B` | Organic highlight |
| `glow-bloom` | `#9CBDA0` | Success glow |

### Semantic States (constrained to 4)

| Name | Hex | Usage |
|------|-----|-------|
| `state-healthy` | `#4A6B4A` | Success, completion |
| `state-pending` | `#C4A77D` | In progress, loading |
| `state-alert` | `#A65D4A` | Error (muted rust, not alarm) |
| `state-dormant` | `#3A3A44` | Inactive, disabled |

### Jewel Identities (STARK-muted — earned, not given)

**IMPORTANT**: These replace the saturated original colors.

| Jewel | Color | Hex | Rationale |
|-------|-------|-----|-----------|
| Brain | Teal Moss | `#4A6B6B` | Knowledge growing quietly |
| Witness | Olive | `#6B6B4A` | Memory preserved in amber |
| Atelier | Umber | `#8B7355` | Creative warmth, earned glow |
| Liminal | Pewter | `#5A5A6B` | Threshold between states |

---

## Visual References

### Steel Foundation

- **Concrete brutalism**: Tadao Ando, Louis Kahn — raw materials, honest surfaces
- **Terminal aesthetics**: Monospace typography, grid precision, cursor blinking
- **Industrial lofts**: Exposed pipes, steel beams, utilitarian beauty
- **Blade Runner**: Rain-soaked concrete, neon bleeding through moisture

### Life Emergence

- **Bioluminescence**: Deep sea creatures, glowing fungi, fireflies
- **Moss on stone**: Ancient walls, temple steps, patient growth
- **Forest understory**: Dappled light, fern unfurling, morning mist
- **Breath visible in cold air**: Warmth making itself visible

### The Tension (Life Through Steel)

- **Plants growing through concrete**: Life finding cracks
- **Rust patterns on steel**: Time's organic signature
- **Server room with grow lights**: Technology nurturing life
- **Lichen on gravestones**: Persistence through stillness

---

## Micro-Interactions

| Moment | Steel Aspect | Life Aspect |
|--------|--------------|-------------|
| **Hover** | Subtle brightness increase | Earned glow, breathing begins |
| **Click** | Mechanical precision feedback | Warmth spreads from epicenter |
| **Success** | Clean transition, no bounce | Sprout color emerges, gentle celebration |
| **Error** | Steel frame maintained | Muted rust appears (not alarming) |
| **Loading** | Stillness | Calming breath (4-7-8 rhythm) |
| **Focus** | Sharp outline | Spore glow, living border |

### Concrete CSS Examples

```css
/* The earned glow on hover */
.element {
  background: var(--steel-carbon);  /* #141418 — humble frame */
  transition: all 200ms ease;
}

.element:hover {
  background: rgba(74, 107, 74, 0.15);  /* life-sage emergence */
  box-shadow: 0 0 8px rgba(139, 169, 139, 0.3);  /* glow-lichen */
}

/* Muted error — attention without alarm */
.error-state {
  color: var(--state-alert);  /* #A65D4A — muted rust */
  background: rgba(166, 93, 74, 0.15);  /* NOT bright red */
}

/* Success — life emerging */
.success-state {
  color: var(--life-sage);  /* #4A6B4A */
  background: rgba(74, 107, 74, 0.15);
}
```

---

## Animation Philosophy: Calming Breath (4-7-8)

> *"Stillness, then life."*

### The Asymmetric Pattern

Traditional breathing animations are symmetric (in-out-in-out). STARK BIOME uses **asymmetric timing** inspired by 4-7-8 breathing:

```
   Opacity
   1.0 ─────────────────────────────────────────────────────
        .
        .    ╭──────────────╮
   0.97 .   ╱                ╲
        .  ╱                  ╲
        . ╱                    ╲
   0.94 ─╱                      ╲─────────────────────────
        │                                              │
        │ rest  gentle   hold      slow release  rest  │
        │ 15%   rise 25%  10%         50%       15%    │
        └──────────────────────────────────────────────┘
                         6.75 seconds
```

### Timing Breakdown

| Phase | Duration | Keyframes | Description |
|-------|----------|-----------|-------------|
| **Rest** | 0-15% | 0.985 opacity | Stillness before inhale |
| **Gentle Rise** | 15-40% | 0.985 → 1.0 | Soft inhale |
| **Brief Hold** | 40-50% | 1.0 | Moment of fullness |
| **Slow Release** | 50-95% | 1.0 → 0.985 | Long, calming exhale |
| **Return** | 95-100% | 0.985 | Back to rest |

### Animation Speeds (STARK)

| Speed | Duration | Use Case |
|-------|----------|----------|
| Slow | 8.1s | Ambient elements, whisper presence |
| Normal | 6.75s | Living elements, active status |
| Fast | 5.4s | Quick feedback, brief attention |

### What May Breathe

- Health indicators (active, healthy state)
- User presence markers
- Active connections
- Living elements (explicitly marked as "alive")

### What Must Stay Still

- Navigation
- Buttons (until hover)
- Text
- Static content
- Inactive elements

---

## Typography: Steel & Spore

### Font Stack

```css
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

### Scale

| Element | Size | Weight | Color | Usage |
|---------|------|--------|-------|-------|
| **H1** | 1.6em | 700 | `rgb(230 230 240)` | Major sections, `border-bottom: life-sage` |
| **H2** | 1.3em | 600 | `rgb(210 210 220)` | Subsections, `border-left: life-sage` |
| **H3** | 1.1em | 600 | `rgb(190 190 200)` | Minor headers |
| **H4** | 0.9em | 600 | `rgb(160 160 170)` | Uppercase, label-like |
| **Body** | 0.9rem | 400 | `rgb(180 180 190)` | Primary text |
| **Muted** | 0.85em | 400 | `rgb(140 140 150)` | Hints, timestamps |
| **Code** | 0.9em | 400 | `#6B8B6B` | life-mint for living code |

### The Rule

Same font family (Inter) for unity. Variation through:
- **Weight**: SemiBold → Regular → Light
- **Case**: UPPERCASE for steel, Sentence for organic
- **Color**: cool grays vs warm accents
- **Spacing**: tight for precision, generous for breath

---

## Spacing Philosophy: "Tight Frame"

> *"Compact but not cramped. Breathing room is earned."*

### Semantic Tokens

```css
--tight-xs: 3px;   /* Minimal separation */
--tight-sm: 6px;   /* Inline elements */
--tight-md: 10px;  /* Default padding */
--tight-lg: 16px;  /* Card padding */
--tight-xl: 24px;  /* Section separation */
```

### Density Modes

| Mode | Gap | Padding | Use Case |
|------|-----|---------|----------|
| **Compact** | 8px | 12px | Mobile, dense info |
| **Comfortable** | 12px | 16px | Default |
| **Spacious** | 16px | 24px | Wide screens, focus |

---

## Borders & Shadows: Bare Edge

### Border Radius Scale

```css
--radius-none: 0px;
--radius-bare: 2px;    /* Default — almost sharp */
--radius-subtle: 3px;  /* Slightly softened */
--radius-md: 4px;      /* Containers */
--radius-lg: 6px;      /* Prominent elements */
--radius-pill: 9999px; /* Pills, badges */
```

### Shadow Philosophy

Shadows are earned, not decorative:

```css
/* Steel has no shadow — it's flat */
.steel-surface {
  box-shadow: none;
}

/* Life glows when activated */
.life-element:hover {
  box-shadow: 0 0 8px rgba(139, 169, 139, 0.3);  /* glow-lichen */
}

/* Focus states use spore glow */
.element:focus-visible {
  outline: 2px solid var(--life-sage);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(196, 167, 125, 0.2);  /* glow-spore aura */
}
```

---

## Token Styling Reference

### AGENTESE Paths — Life Emerging

```css
.agentese-path-token {
  color: #6b8b6b;  /* life-mint */
  background: none;
}

.agentese-path-token:hover {
  background-color: rgba(74, 107, 74, 0.15);  /* life-sage */
  box-shadow: 0 0 8px rgba(139, 169, 139, 0.3);  /* earned glow */
  animation: token-breathe 6.75s linear infinite;
}
```

### Tasks — Grounded in Soil

```css
.task-checkbox-token:hover {
  background-color: rgba(26, 21, 18, 0.5);  /* soil-loam */
}

.task-checkbox-token--checked .task-checkbox-token__box {
  background-color: rgba(26, 46, 26, 0.4);  /* life-moss */
  border-color: #4a6b4a;  /* life-sage */
}
```

### Code Blocks — Steel Precision

```css
.code-block-token {
  background-color: #141418;  /* steel-carbon */
  border: 1px solid #28282f;  /* steel-gunmetal */
}

.code-block-token__language {
  color: #6b8b6b;  /* life-sage — life in the code */
}
```

### Principles — Earned Wisdom

```css
/* Architectural decisions — gold/spore accent */
.principle-token--architectural {
  background-color: rgba(196, 167, 125, 0.15);  /* glow-spore */
  color: #c4a77d;
}

/* Constitutional — life accent */
.principle-token--constitutional {
  background-color: rgba(74, 107, 74, 0.15);  /* life-sage */
  color: #6b8b6b;
}
```

---

## Anti-Patterns (AVOID THESE)

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Saturated colors | Screams instead of glows | Use STARK muted palette |
| Symmetric breathing | Mechanical, not organic | Use 4-7-8 asymmetric |
| Animation everywhere | Decorative, exhausting | Earned moments only |
| White text on dark | Too stark contrast | Use zinc/mint spectrum |
| Bright error reds | Alarming, not empathetic | Use muted rust `#A65D4A` |
| Bounce/spring easing | Too playful for stark | Use ease-out, no overshoot |
| Continuous loops on static | Decorative motion | Only living elements breathe |

---

## Audit Findings (2025-12-22)

### Critical Violations Found

1. **JEWEL_COLORS in `constants/jewels.ts`** use saturated Tailwind colors (`#06B6D4`, `#22C55E`, etc.) — should use STARK-muted palette

2. **Breathe component** uses symmetric 2-4 second timing, not 4-7-8 asymmetric calming breath

3. **EmpathyError** uses `text-red-400`, `bg-cyan-600` — non-STARK colors

4. **EditPane.css** uses `#3b82f6` (blue-500) for accent — should use STARK colors

5. **globals.css** line 720: `#f87171` (red-400), line 820-824: blue-500, red-500

6. **Various components** use Tailwind arbitrary colors: `text-red-500`, `bg-green-600`, `bg-blue-500`, etc.

### Files Requiring Migration

**High Priority:**
- `src/constants/jewels.ts` — Replace saturated jewel colors
- `src/components/joy/Breathe.tsx` — Implement 4-7-8 timing
- `src/membrane/views/EditPane.css` — Replace blue accent

**Medium Priority:**
- `src/components/joy/EmpathyError.tsx` — Replace red/cyan with STARK
- `src/components/elastic/FloatingActions.tsx` — Replace colored buttons
- `src/components/synergy/SynergyToaster.tsx` — Replace blue/red backgrounds

**Low Priority (Gallery/Demo files):**
- `src/pages/LayoutGallery.tsx` — Demo file, less critical
- `src/widgets/cards/CitizenCard.tsx` — Legacy widget

---

## Migration Checklist

- [ ] Replace JEWEL_COLORS with STARK-muted versions
- [ ] Update Breathe.tsx to use 4-7-8 timing (6.75s default)
- [ ] Audit all CSS files for non-STARK hex colors
- [ ] Replace Tailwind arbitrary colors with STARK semantic classes
- [ ] Ensure all breathing only on living elements
- [ ] Verify animations respect prefers-reduced-motion
- [ ] Test hover states don't cause layout shift

---

## Connection to Principles

| Principle | How STARK BIOME Embodies It |
|-----------|------------------------------|
| **Tasteful** | 90% steel restraint; earned color moments |
| **Curated** | Four state colors, not twelve |
| **Ethical** | Empathetic errors, not alarming reds |
| **Joy-Inducing** | Calming breath, not frantic pulse |
| **Composable** | Consistent tokens compose visually |
| **Heterarchical** | No fixed visual hierarchy; context determines emphasis |
| **Generative** | Palette generates consistent UI from rules |

---

*"The frame is humble. The content glows. The austerity makes the warmth more precious."*

*Updated: 2025-12-22*
