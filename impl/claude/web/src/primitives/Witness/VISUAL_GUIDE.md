# Witness Primitive - Visual Guide

## Full Mode (Confident)

```
┌─────────────────────────────────────────────────────────────┐
│ ● HIGH CONFIDENCE              > 0.80          3 items      │ <- Green border
├─────────────────────────────────────────────────────────────┤
│ ┌─ P=0.95                                          ASHC ─┐ │
│ │ Equivalence score: 95% (spec↔impl verified)           │ │
│ └───────────────────────────────────────────────────────────┘ │
│ ┌─ P=0.93                                          ASHC ─┐ │
│ │ 14/15 verification runs passed                        │ │
│ └───────────────────────────────────────────────────────────┘ │
│ ┌─ P=0.92                                          ASHC ─┐ │
│ │ Chaos stability: 92% (robust under perturbation)      │ │
│ └───────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Causal Influence Graph                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Equivalence score... → (85%) → Chaos stability...     │ │ <- Breathing animation
│ │ 14/15 verification... → (78%) → Equivalence score...  │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Full Mode (Uncertain)

```
┌─────────────────────────────────────────────────────────────┐
│ ◐ MEDIUM CONFIDENCE            0.50-0.80       2 items     │ <- Yellow border
├─────────────────────────────────────────────────────────────┤
│ ┌─ P=0.67                                      Bayesian ─┐ │
│ │ Bayesian posterior: P=0.67 (α=20, β=10)               │ │
│ └───────────────────────────────────────────────────────────┘ │
│ ┌─ P=0.80                                         Tools ─┐ │
│ │ Tools executed: 8 succeeded, 2 failed                 │ │
│ └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Full Mode (Speculative)

```
┌─────────────────────────────────────────────────────────────┐
│ ◯ LOW CONFIDENCE               < 0.50          2 items     │ <- Red border
├─────────────────────────────────────────────────────────────┤
│ ┌─ P=0.30                                         Tests ─┐ │
│ │ Only 3/10 test cases passed                           │ │
│ └───────────────────────────────────────────────────────────┘ │
│ ┌─ P=0.25                                         Stats ─┐ │
│ │ High variance in results (±35%)                       │ │
│ └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Compact Mode

```
This response has ┌────────────────────────────────┐ based on
                  │ ● High Confidence (3)         │ multiple sources.
                  └────────────────────────────────┘
                         ↑ Green border, inline display
```

## Hover States

### Evidence Item Hover
```
┌─ P=0.95                                          ASHC ─┐
│ Equivalence score: 95% (spec↔impl verified)           │ <- Background lightens
└─────────────────────────────────────────────────────────┘   Border → white
     ↑ Subtle glow effect
```

### High-Influence Edge (Breathing Animation)
```
┌───────────────────────────────────────────────────────┐
│ Equivalence... → (85%) → Stability...                │
└─────────────────────────────────────────────────────────┘
   ↑ Border pulses: 2px → 3px → 2px (2s cycle)
   ↑ Opacity: 1.0 → 0.7 → 1.0
```

## Color Palette

### Confident (Green)
- Border: `#00ff00`
- Glow: `rgba(0, 255, 0, 0.3)`
- Icon: `●`

### Uncertain (Yellow)
- Border: `#ffa500`
- Glow: `rgba(255, 165, 0, 0.3)`
- Icon: `◐`

### Speculative (Red)
- Border: `#ff0000`
- Glow: `rgba(255, 0, 0, 0.3)`
- Icon: `◯`

### Surfaces (Steel)
- Background: `#1a1a1a` (--surface-1)
- Items: `#0f0f0f` (--surface-2)
- Hover: `#252525` (--surface-3)

### Text
- Primary: `#e0e0e0` (--text-1)
- Secondary: `#999999` (--text-2)
- Accent: `#ffffff` (--accent)

## Typography

- **Family**: Berkeley Mono, JetBrains Mono (monospace)
- **Base Size**: 12px
- **Header**: 700 weight, uppercase, 0.05em letter-spacing
- **Content**: 400 weight, 1.6 line-height
- **Meta**: 10px, uppercase, 700 weight

## Spacing

- **Container**: 16px padding, 12px gap
- **Items**: 8px gap, 8px padding
- **Compact**: 6px padding, 8px gap
- **Small**: 8px padding, 8px gap
- **Large**: 20px padding, 16px gap

## Responsive Breakpoints

### Mobile (< 640px)
- Padding: 12px → 6px (sm)
- Font size: 12px → 11px
- Causal edges: horizontal → vertical stack
- Item padding: 8px → 6px

## State Machine

```
┌──────────┐
│ Compact  │ ─(click)─> ┌──────────┐
└──────────┘            │ Expanded │
                        └──────────┘
                             │
                         (showCausal)
                             ↓
                        ┌────────────────┐
                        │ With Causal    │
                        │ Graph          │
                        └────────────────┘
```

## Accessibility

- **Role**: `button` (when clickable)
- **Tabindex**: `0` (keyboard navigation)
- **ARIA**: Labels for screen readers
- **Focus**: White outline, 2px solid

## Animation Timings

- Border color: `0.2s ease`
- Box shadow: `0.2s ease`
- Background: `0.2s ease`
- Breathing: `2s ease-in-out infinite`

## Usage Context

### In Chat Messages
```
┌─────────────────────────────────────────────────┐
│ User: What's the confidence on this?            │
├─────────────────────────────────────────────────┤
│ Assistant: Based on the evidence...             │
│                                                 │
│ ┌───────────────────────────────────────────┐   │
│ │ ● HIGH CONFIDENCE      > 0.80   3 items   │   │ <- Witness inline
│ │ ...                                       │   │
│ └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### In ASHC Results
```
┌─────────────────────────────────────────────────┐
│ ASHC Verification Complete                      │
├─────────────────────────────────────────────────┤
│ ● HIGH CONFIDENCE                               │
│                                                 │
│ Equivalence score: 95%                          │
│ 14/15 runs passed                               │
│ Chaos stability: 92%                            │
│                                                 │
│ [Causal Influence Graph]                        │
└─────────────────────────────────────────────────┘
```

### Inline in Text
```
This implementation has ● High Confidence (3) based
on ASHC verification and Bayesian analysis.
```
