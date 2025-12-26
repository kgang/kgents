# Design Law Tests

> "Every design decision is traceable to a law, every law is testable as code, every test is witnessable as a mark."

This directory contains **comprehensive test coverage for the 30 UI/UX Design Laws** from Zero Seed Creative Strategy (`plans/zero-seed-creative-strategy.md`).

## Overview

The 30 design laws are organized into 6 categories:

| Category | Laws | File |
|----------|------|------|
| **Layout** | L-01 through L-05 | `layout.test.tsx` |
| **Navigation** | N-01 through N-05 | `navigation.test.tsx` |
| **Feedback** | F-01 through F-05 | `feedback.test.tsx` |
| **Content** | C-01 through C-05 | `content.test.tsx` |
| **Motion** | M-01 through M-05 | `motion.test.tsx` |
| **Coherence** | H-01 through H-05 | `coherence.test.tsx` |

## Running Tests

```bash
# Run all design law tests
npm run test:design-laws

# Watch mode (auto-rerun on changes)
npm run test:design-laws:watch

# Run specific category
npm run test:design-laws -- layout.test
npm run test:design-laws -- motion.test

# Run with UI
npm run test:ui -- tests/design-laws
```

## Law Summary

### Layout Laws (L-01 through L-05)

**L-01: Density-Content Isomorphism**
- Content detail maps to observer capacity (density)
- Spacious shows more than comfortable shows more than compact
- Anti-pattern: `{isMobile ? <CompactThing /> : <FullThing />}`
- Good pattern: `<Thing density={density} />`

**L-02: Three-Mode Preservation**
- Same affordances across all densities (compact/comfortable/spacious)
- Features transform, don't disappear
- Mobile views must not drop features

**L-03: Touch Target Invariance**
- ≥48px interactive elements on all densities
- Physical constraint that does not scale
- Enforced via `PHYSICAL_CONSTRAINTS.minTouchTarget`

**L-04: Tight Frame Breathing Content**
- Frame (nav, chrome) is tight and precise
- Content area is generous and spacious
- Creates "steel biome" aesthetic

**L-05: Overlay Over Reflow**
- Navigation floats (fixed/absolute), doesn't push (static/relative)
- Prevents layout shift on compact mode
- Secondary content becomes overlay (drawer/modal)

### Navigation Laws (N-01 through N-05)

**N-01: Home-Row Primary Arrow Alias**
- j/k navigation is primary, arrows are alias
- Documentation shows j/k first
- Both work, but home-row keys documented

**N-02: Edge Traversal Not Directory**
- Navigate graph relationships, not filesystem
- Trail shows: `principle --enables--> goal --synthesizes--> decision`
- Anti-pattern: `/folder/subfolder/file.md`

**N-03: Mode Return to NORMAL**
- Escape always returns to NORMAL mode
- Universal "get me out" key
- Works from INSERT, VISUAL, EDGE, COMMAND, WITNESS

**N-04: Trail Is Semantic**
- Trail records edges and relationships, not just positions
- Captures metadata for reconstruction
- Anti-pattern: Just Block A → Block B

**N-05: Jump Stack Preservation**
- Jumps preserve return path for back navigation
- Linear navigation (j/k) doesn't push to stack
- Jumps (search, portal, link) push to stack

### Feedback Laws (F-01 through F-05)

**F-01: Multiple Channel Confirmation**
- Significant actions use 2+ feedback channels
- Channels: visual (toast/color), state change, sound (optional), haptic (mobile)
- Example: Commit shows toast AND button state change

**F-02: Contradiction as Information**
- Contradictions are info, not errors
- Use amber/blue styling, not red
- Frame as "productive tension" or "creative opportunity"

**F-03: Tone Matches Observer**
- Message tone adapts to user archetype
- Developer: precise, technical ("Coherence: 0.87")
- Creator: organic, nurturing ("Your garden is thriving!")

**F-04: Earned Glow Not Decoration**
- 90% steel, 10% earned glow
- Default state is neutral (steel colors)
- Color appears only on interaction, achievement, significance

**F-05: Non-Blocking Notification**
- Notifications use toast/banner, not blocking modal
- Positioned in peripheral vision (bottom-right)
- Allow dismissing without blocking interaction

### Content Laws (C-01 through C-05)

**C-01: Five-Level Degradation**
- icon → title → summary → detail → full
- Each level contains previous level's information
- Compact: icon + title, Spacious: full detail

**C-02: Schema Single Source**
- Frontend types generated from Python Pydantic models
- No manual type duplication
- Use `npm run sync-types`

**C-03: Feed Is Primitive**
- Feed is first-class component, not a view
- Has unique affordances (infinite scroll, algorithmic ranking, contradiction surfacing)
- Import from `@/primitives/Feed`, not `@/views/FeedView`

**C-04: Portal Token Interactivity**
- Portal tokens (@principle, #goal) are interactive buttons
- Provide hover preview, click actions
- Anti-pattern: `<a href="#principle-1">`
- Good pattern: `<button data-portal="principle-1">`

**C-05: Witness Required for Commit**
- Every commit needs witness message explaining "why"
- Commit button disabled until message provided
- No silent commits

### Motion Laws (M-01 through M-05)

**M-01: Asymmetric Breathing**
- 4-7-8 timing (4s ease-in, 7s hold, 8s ease-out)
- Creates calming, organic feel
- Anti-pattern: Symmetric 5-5-5 timing

**M-02: Stillness Then Life**
- Default is still, animation is earned
- No gratuitous animation on page load
- Animate only on interaction or significant state change

**M-03: Mechanical Precision Organic Life**
- Structural layouts: linear, precise, fast (200ms)
- Content animations: ease/spring, bouncy, slower (400ms)
- "Steel frame, living content" aesthetic

**M-04: Reduced Motion Respected**
- Check `prefers-reduced-motion` media query
- Disable animations when set
- Accessibility > aesthetics

**M-05: Animation Justification**
- Every animation has semantic reason
- Purpose: state change, feedback, guidance
- Document purpose in code/constants

### Coherence Laws (H-01 through H-05)

**H-01: Linear Adaptation**
- System adapts to user, not vice versa
- Learn from behavior over time
- No extensive upfront configuration

**H-02: Quarantine Not Block**
- High-loss K-Blocks quarantined, not rejected
- Permissive, not punitive
- Provide refine/link/accept options

**H-03: Cross-Layer Edge Allowed**
- Distant layer edges allowed but flagged
- Advisory metadata, not blocking error
- Suggest intermediate steps

**H-04: K-Block Isolation**
- INSERT mode creates isolated K-Block
- Changes don't affect main graph until commit
- Safe sandbox for experimentation

**H-05: AGENTESE Is API**
- Forms invoke `logos.invoke('context.resource.action', observer, data)`
- No REST endpoints like `/api/kblocks`
- Contexts: self, world, concept, void, time

## Test Philosophy

1. **Law as Contract**: Each law is a testable contract, not aspirational documentation
2. **Anti-Patterns**: Tests explicitly reject anti-patterns with examples
3. **Implementation Guidance**: Tests show both bad and good patterns
4. **Categorical Proofs**: Laws are verified like composition laws (identity, associativity)
5. **Witnessable**: Test runs should integrate with witness system

## Adding New Laws

When a pattern appears 3+ times, codify it:

1. **Name it** - Short, memorable (e.g., "Density-Content Isomorphism")
2. **State it** - One sentence (e.g., "Content detail maps to observer capacity")
3. **Justify it** - Why this matters for kgents
4. **Test it** - How to verify compliance (add to appropriate test file)
5. **Anti-pattern** - What violation looks like
6. **Categorize it** - Which section it belongs to

## Integration with Development Workflow

### Pre-commit Hook

```bash
# Add to pre-commit workflow
npm run test:design-laws
```

### CI/CD

```yaml
- name: Run design law tests
  run: npm run test:design-laws
```

### Design Review Checklist

Before PR approval, ensure new components:
- [ ] Implement applicable layout laws (L-01 through L-05)
- [ ] Follow navigation patterns (N-01 through N-05)
- [ ] Provide appropriate feedback (F-01 through F-05)
- [ ] Handle content degradation (C-01 through C-05)
- [ ] Respect motion preferences (M-01 through M-05)
- [ ] Maintain coherence (H-01 through H-05)

## Coverage

Current coverage: **30/30 laws tested** (100%)

- Layout: 5/5 laws
- Navigation: 5/5 laws
- Feedback: 5/5 laws
- Content: 5/5 laws
- Motion: 5/5 laws
- Coherence: 5/5 laws

## References

- **Creative Strategy**: `plans/zero-seed-creative-strategy.md`
- **Elastic Primitives**: `docs/skills/elastic-ui-patterns.md`
- **Metaphysical Fullstack**: `docs/skills/metaphysical-fullstack.md`
- **AGENTESE Protocol**: `docs/skills/agentese-path.md`

---

*"The proof IS the decision. The mark IS the witness. The persona is a garden, not a museum."*
