# Agent Prompt: STARK BIOME Visual Enhancement

> *"The frame is humble. The content glows."*

**Mission**: Systematically enhance the kgents visual and creative strategy to fully realize the dialectic between beautiful organic interactions (Life) and cold industrial precision (Steel).

---

## Context

You are working on the kgents project — a specification for tasteful, curated, ethical, joy-inducing agents. The visual system follows **STARK BIOME** philosophy:

```
90% STEEL (cool industrial)  ←→  10% LIFE (organic accents)
         ↓                              ↓
   The frame is humble          The content glows
```

This is a dialectic, not a palette. Steel provides the disciplined foundation; Life emerges as earned moments of warmth.

---

## Phase 1: Audit and Understand

### 1.1 Read the Foundation Documents

```bash
# Core philosophy
Read: plans/SYNTHESIS-UI.md           # The UI synthesis vision
Read: impl/claude/web/tailwind.config.js  # Current STARK BIOME tokens

# Existing creative artifacts (if they exist)
Glob: docs/creative/*.md
Glob: creative/*.md
Read: any mood board files you find
```

### 1.2 Inventory Current State

Audit these token systems and note gaps between vision and implementation:

| System | Files | Questions to Answer |
|--------|-------|---------------------|
| **Colors** | `tailwind.config.js` | Are steel/life/glow ratios honored? Any saturated outliers? |
| **Animation** | `tailwind.config.js`, `tokens.css` | Is breathing asymmetric (4-7-8)? Is motion earned or decorative? |
| **Tokens** | `membrane/tokens/*.tsx` | Do all tokens follow STARK styling? Any inconsistencies? |
| **Joy Components** | `components/joy/*.tsx` | Are they being used? Or sitting unused in galleries? |

---

## Phase 2: Update the Mood Board

### 2.1 Create or Update the Mood Board

Create/update `docs/creative/stark-biome-moodboard.md` with:

```markdown
# STARK BIOME Mood Board

## The Dialectic

Steel (90%)                    Life (10%)
─────────────────────────────────────────────────
Cold, industrial               Warm, organic
Precision, discipline          Growth, emergence
Background, frame              Foreground, content
Always present                 Earned through action
Obsidian → Gunmetal            Moss → Sage → Sprout
"The frame"                    "The glow"

## Visual References

### Steel Foundation
- [Describe: Dark concrete, industrial lofts, machined metal]
- [Describe: Terminal aesthetics, monospace typography]
- [Describe: Blueprint precision, engineering drawings]

### Life Emergence
- [Describe: Bioluminescent organisms, deep sea creatures]
- [Describe: Moss on stone, lichen on bark]
- [Describe: First light through forest canopy]
- [Describe: Breath visible in cold air]

### The Tension
- [Describe: Plants growing through concrete]
- [Describe: Rust patterns on steel]
- [Describe: Green circuit boards]
- [Describe: Server rooms with grow lights]

## Micro-Interactions

| Moment | Steel Aspect | Life Aspect |
|--------|--------------|-------------|
| Hover | Subtle brightness | Earned glow, breathing begins |
| Click | Mechanical precision | Warmth spreads |
| Success | Clean transition | Sprout color, celebration |
| Error | Steel frame | Rust/muted warning (not alarm) |
| Loading | Stillness | Calming breath (4-7-8) |

## Typography

- **Headers**: Clean, mechanical, slightly condensed
- **Body**: Readable, neutral, recedes
- **Code**: JetBrains Mono — precision without coldness
- **Accent**: When text "glows" — life-mint on dark

## Spacing Philosophy ("Tight Frame")

- Compact but not cramped
- Breathing room is earned
- Dense information, not dense pixels
- Margins serve function, not decoration
```

### 2.2 Add Concrete Visual Examples

For each section, add specific examples with hex codes and CSS:

```css
/* Example: The earned glow on hover */
.element {
  background: #141418;  /* steel-carbon: humble frame */
  transition: all 200ms ease;
}

.element:hover {
  background: rgba(74, 107, 74, 0.15);  /* life-sage: emergence */
  box-shadow: 0 0 8px rgba(139, 169, 139, 0.3);  /* glow-lichen: earned */
}
```

---

## Phase 3: Update Styling Implementation

### 3.1 Audit and Fix Color Usage

Search for violations:

```bash
# Find non-STARK colors in CSS
Grep: pattern="#[0-9a-fA-F]{6}" in *.css files
# Check each one — is it from the STARK palette?

# Find arbitrary Tailwind colors
Grep: pattern="(bg|text|border)-(red|green|blue|yellow|purple|pink|indigo|cyan|teal|orange)-" in *.tsx files
# These should use STARK semantic colors instead
```

Create fixes:

| Found | Replace With | Rationale |
|-------|--------------|-----------|
| `bg-green-600` | `bg-life-sage` | Constitutional green |
| `text-amber-500` | `text-glow-spore` | Earned warmth |
| `border-gray-700` | `border-steel-gunmetal` | STARK steel |

### 3.2 Enhance Animation System

Update `tailwind.config.js` animations if needed:

**Calming Breath (4-7-8 pattern)**:
- 15% rest (stillness before inhale)
- 25% gentle rise (soft inhale)
- 10% brief hold (moment of fullness)
- 50% slow release (long, calming exhale)

**Ensure all breathing animations use**:
- Linear timing (easing baked into keyframes)
- Asymmetric patterns (not symmetric pulses)
- Subtle amplitude (1.5% for ambient, 6% for living elements)

### 3.3 Update Token Styles

Review each token in `membrane/tokens/tokens.css`:

| Token | Steel Aspect | Life Aspect | Check |
|-------|--------------|-------------|-------|
| AGENTESE | Code background | Sage text, breathing hover | ✓ |
| Task | Carbon bg | Moss when checked | ✓ |
| Portal | Gunmetal border | Sage edge type | ✓ |
| Code | Carbon bg, slate header | Language badge in sage | ✓ |
| Principle | — | Spore (arch) / Sage (const) | ✓ |
| Image | Gunmetal border | Sage AI label | ✓ |

Fix any tokens that don't follow the pattern.

### 3.4 Update Component Defaults

Ensure joy components have correct defaults:

```typescript
// Breathe.tsx — should use asymmetric 4-7-8 timing
const SPEED_DURATION = {
  slow: 8.1,    // Full calming cycle
  normal: 6.75, // Standard living breath
  fast: 5.4,    // Quicker but still calming
};

// PersonalityLoading — jewel colors should be STARK-muted
const JEWEL_COLORS = {
  brain: '#4A6B6B',    // Teal moss, not bright teal
  witness: '#6B6B4A',  // Olive, not bright yellow
  atelier: '#8B7355',  // Umber, not bright orange
  // ...
};
```

---

## Phase 4: Document the Enhancement

### 4.1 Update SYNTHESIS-UI.md

Add a section on any new patterns discovered:

```markdown
## New Patterns from Enhancement Session

### [Pattern Name]
- When to use
- Steel aspect
- Life aspect
- Code example
```

### 4.2 Create Migration Checklist

If breaking changes were made, document:

```markdown
## Migration Notes

### Color Changes
- `bg-sage-600` → `bg-life-sage` (semantic naming)

### Animation Changes
- Breathing now uses 4-7-8 asymmetric pattern

### Component Changes
- [List any prop changes]
```

---

## Deliverables

1. **Updated mood board**: `docs/creative/stark-biome-moodboard.md`
2. **Fixed styling violations**: Any non-STARK colors replaced
3. **Enhanced animations**: 4-7-8 breathing consistently applied
4. **Token audit**: All tokens follow Steel/Life dialectic
5. **Documentation**: SYNTHESIS-UI.md updated with findings

---

## Voice Anchors (Quote Directly)

- *"The frame is humble. The content glows."*
- *"90% Steel / 10% Life"*
- *"Stillness, then life"*
- *"Motion is earned, not decorative"*
- *"Daring, bold, creative, opinionated but not gaudy"*

---

## Anti-Patterns to Fix

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| Saturated colors | Screams instead of glows | Muted STARK palette |
| Symmetric breathing | Mechanical, not organic | 4-7-8 asymmetric |
| Animation everywhere | Decorative, exhausting | Earned moments only |
| White text on dark | Too stark contrast | Zinc/mint spectrum |
| Bright error reds | Alarming, not empathetic | Muted rust (#A65D4A) |

---

## Success Criteria

- [ ] Mood board captures the dialectic with concrete examples
- [ ] No arbitrary hex colors remain (all from STARK palette)
- [ ] All breathing animations use asymmetric 4-7-8 timing
- [ ] Token styles consistently apply Steel frame / Life glow
- [ ] Joy components have correct STARK-muted defaults
- [ ] SYNTHESIS-UI.md reflects any new patterns

---

*"The persona is a garden, not a museum."*
*Let the steel frame recede. Let the life emerge where earned.*
