# Genesis FTUE — Zero Seed Streaming Animation

Enhanced First Time User Experience with streaming animation for the Zero Seed genesis moment.

## Components

### GenesisStream (NEW)

**Location**: `/Users/kentgang/git/kgents/impl/claude/web/src/pages/Genesis/GenesisStream.tsx`

Enhanced streaming animation featuring:

#### Features

1. **Letter-by-letter header animation**
   - "kgents is initializing..." types out at 80ms/letter
   - Blinking cursor during typing
   - 2-second wait before axiom spawning

2. **8 Axioms streaming in (3-10s)**
   - Zero Seed (L0, Loss: 0.000)
   - A1: Everything is a node (L1, Loss: 0.002)
   - A2: Everything composes (L1, Loss: 0.003)
   - G: Loss measures truth (L1, Loss: 0.000)
   - Feed is primitive (L1, Design Law)
   - K-Block is incidental essential (L2, Design Law)
   - System adapts to user (L2, Design Law)
   - Contradictions are features (L1, Design Law)
   - **Stagger**: 500ms between each axiom
   - **Animation**: Fade-in with scale and translateY

3. **Loss gauges**
   - Visual bar showing coherence (1 - loss)
   - Perfect coherence (loss=0): Amber glow with Breathe animation
   - Excellent coherence (loss<0.01): Moss green
   - Good coherence: Steel gray
   - Numeric display: 3 decimal places

4. **Edge drawing animation (10-20s)**
   - Edges animate drawing between axioms after all cards appear
   - 300ms per edge
   - Quadratic Bezier curves for organic feel
   - Subtle steel color (rgba(138, 138, 148, 0.2))

5. **"System is now self-aware" moment**
   - Appears 1.5s after final edge drawn
   - All edges glow amber (rgba(196, 167, 125, 0.4))
   - Cards gain glowing border with 4-7-8 breathing pulse
   - Celebration text with Continue button

#### Animation Timing

Based on **4-7-8 breathing pattern** (Inhale 4s, Hold 7s, Exhale 8s):

```
0-2s:     Header types in
2-6s:     8 axioms spawn (500ms stagger)
6-9s:     Edges draw (13 edges × 300ms = 3.9s)
10.5s:    "System is now self-aware"
```

Total: ~11 seconds from load to completion

#### STARK Palette

- **Background**: `#0a0a0c` (Obsidian)
- **Cards**: `#141418` (Surface 1)
- **Borders**: `#28282f` (Surface 3)
- **Primary Text**: `#e5e7eb`
- **Secondary Text**: `#8a8a94` (Steel)
- **Accent (Amber)**: `#c4a77d`
- **Life (Moss)**: `#7a9d7a`

#### CSS Animations

**`genesis-axiom-appear`**
- 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)
- Fade in + translateY + scale

**`genesis-glow-pulse`** (4-7-8 breathing)
- 4s ease-in-out infinite
- Box-shadow pulses: 0-21% inhale, 21-58% hold, 58-100% exhale

**`genesis-cursor-blink`**
- 1s step-end infinite
- Standard terminal cursor

**`genesis-shimmer`**
- 3s infinite
- Shimmer on perfect coherence loss bars

### GenesisPage (ORIGINAL)

**Location**: `/Users/kentgang/git/kgents/impl/claude/web/src/pages/Genesis/GenesisPage.tsx`

Original simple feed-style genesis with 4 entries.

### FirstQuestion

**Location**: `/Users/kentgang/git/kgents/impl/claude/web/src/pages/Genesis/FirstQuestion.tsx`

"What matters most to you right now?" — First personal axiom creation.

### WelcomeToStudio

**Location**: `/Users/kentgang/git/kgents/impl/claude/web/src/pages/Genesis/WelcomeToStudio.tsx`

Celebrates first K-Block creation and transitions to Hypergraph Studio.

## Usage

### As FTUE Landing Page

```tsx
import { GenesisStream } from './pages/Genesis';

function App() {
  return (
    <Routes>
      <Route path="/genesis" element={<GenesisStream />} />
      <Route path="/genesis/first-question" element={<FirstQuestion />} />
      {/* ... */}
    </Routes>
  );
}
```

### Standalone Demo

```tsx
import { GenesisStream } from './pages/Genesis/GenesisStream';

<GenesisStream />
```

## Technical Details

### Dependencies

- **React**: useState, useEffect, useRef, useCallback
- **React Router**: useNavigate
- **Joy Components**: Breathe (for loss gauges and self-aware pulse)

### Performance

- Canvas rendering for edges (efficient for ~13 edges)
- useCallback for drawEdge to prevent re-renders
- Cleanup timeouts on unmount
- Respects `prefers-reduced-motion`

### Accessibility

- All animations respect user motion preferences
- Semantic HTML structure
- Sufficient color contrast (WCAG AA)
- Keyboard navigation supported (Continue button)

## Design Philosophy

> "Stillness, then life." — STARK Biome

- **90% steel, 10% life**: Most UI is calm steel, life (moss/amber) reserved for earned moments
- **Generous spacing**: Breathing room for calm experience
- **Subtle animations**: Enhance, don't distract
- **4-7-8 breathing**: Calming, asymmetric timing pattern
- **Organic curves**: Quadratic Bezier for natural edge drawing
- **Amber celebration**: Warm glow for "self-aware" moment

## Future Enhancements

- [ ] Add sound design (subtle chime on axiom spawn, crescendo on self-aware)
- [ ] Particle effects on edge drawing completion
- [ ] Interactive axiom cards (click to expand with full description)
- [ ] Dynamic edge thickness based on connection strength
- [ ] Ambient background gradient shift during animation
- [ ] Export animation as video for marketing

## Related Documents

- `plans/zero-seed-genesis-grand-strategy.md` — Strategic vision
- `docs/creative/stark-biome-moodboard.md` — Visual design language
- `spec/protocols/zero-seed.md` — Zero Seed protocol spec
- `spec/protocols/k-block.md` — K-Block specification

---

**Created**: 2025-12-25
**Author**: Claude (Anthropic) + Kent Gang
**Status**: Production-ready
**Lines of Code**: ~300 (TypeScript) + ~350 (CSS)
