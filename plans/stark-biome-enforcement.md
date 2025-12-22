# Stark Biome Enforcement Plan

> *"The frame is humble. The content glows."*

**Status**: READY TO IMPLEMENT
**Goal**: Eliminate `bg-gray-*` drift, enforce semantic tokens

---

## Current State

| Asset | Status |
|-------|--------|
| `tailwind.config.js` | ✅ Full Stark Biome palette (steel/soil/life/glow/jewel) |
| `globals.css` | ✅ CSS variables defined |
| Shell components | ✅ Migrated (Terminal, NavigationTree, ElasticCard) |
| Remaining `bg-gray-*` | 338 occurrences across 50+ files |

**Gap**: Tokens exist but aren't enforced. Old code uses Tailwind defaults.

---

## The Boundary Decision

Not everything needs Stark Biome treatment.

| Layer | Treatment | Rationale |
|-------|-----------|-----------|
| **Shell** (frame) | Full Stark Biome | The identity. Steel obsidian/carbon/gunmetal. |
| **Crown Jewels** (Brain, Witness, Atelier) | Jewel-specific accent | Earned glow. jewel-brain cyan, etc. |
| **Content pages** (Canvas, Trail, Docs) | Selective | Can inherit from shell or stay generic. |
| **Galleries/Debug** | Skip | Not user-facing. |

---

## Phase 1: Enforcement Layer (1 hour)

### 1.1 ESLint Rule

```bash
npm install -D eslint-plugin-regex
```

Add to `.eslintrc`:
```json
{
  "plugins": ["regex"],
  "rules": {
    "regex/invalid": ["warn", [
      {
        "regex": "bg-gray-[0-9]+",
        "replacement": "bg-steel-* (see tailwind.config.js)",
        "message": "Use Stark Biome tokens: steel-obsidian/carbon/slate/gunmetal/zinc"
      }
    ]]
  }
}
```

This surfaces violations as warnings, not blockers.

### 1.2 Pre-commit Hook (Optional)

```bash
# .husky/pre-commit
grep -r "bg-gray-" impl/claude/web/src --include="*.tsx" && echo "⚠️  Stark Biome: use steel-* tokens" && exit 1 || exit 0
```

---

## Phase 2: Token Mapping (Reference)

Already in `tailwind.config.js`:

| Old (gray) | New (Stark) | Semantic |
|------------|-------------|----------|
| `bg-gray-900` | `bg-steel-obsidian` | Deepest background |
| `bg-gray-800` | `bg-steel-carbon` | Card/elevated |
| `bg-gray-700` | `bg-steel-slate` | Secondary surfaces |
| `bg-gray-600` | `bg-steel-gunmetal` | Borders, interactive |
| `bg-gray-500` | `bg-steel-zinc` | Muted text |
| `text-gray-*` | `text-steel-zinc` or `text-glow-light` | Muted → emphasis |
| `text-white` | `text-glow-light` | Warm emphasis, not pure white |
| `rounded-lg` | `rounded-bare` (2px) | Bare Edge system |

---

## Phase 3: Selective Migration

Priority order (high-impact, user-facing first):

### Tier 1: Shell (DONE)
- [x] Terminal.tsx
- [x] Shell.tsx
- [x] NavigationTree.tsx
- [x] ElasticCard.tsx

### Tier 2: Crown Jewel Surfaces (DO NEXT)
These are the main content areas users interact with:

| File | Occurrences | Notes |
|------|-------------|-------|
| ObserverDrawer.tsx | 9 | User context, high visibility |
| PathSearch.tsx | 8 | Command palette UX |
| CommandPalette.tsx | 7 | Power user interface |
| CrystalDetail.tsx | 9 | Brain jewel identity |
| AspectPanel.tsx | 7 | AGENTESE interaction |

### Tier 3: Content (OPTIONAL)
Can stay gray or migrate gradually:
- Canvas.tsx (12)
- TrailPanel.tsx (12)
- RequestBuilder/*.tsx (16)
- LayoutGallery.tsx (28) — skip, debug tool

---

## Phase 4: CSS Variable Bridge

For dynamic theming, ensure Tailwind tokens map to CSS variables:

```js
// tailwind.config.js extend
colors: {
  steel: {
    obsidian: 'var(--color-steel-obsidian)',
    carbon: 'var(--color-steel-carbon)',
    slate: 'var(--color-steel-slate)',
    gunmetal: 'var(--color-steel-gunmetal)',
    zinc: 'var(--color-steel-zinc)',
  }
}
```

This enables:
- Runtime theme switching
- Component-level overrides
- Future light mode

---

## Phase 5: Verification Script

```bash
# scripts/verify-stark-biome.sh
#!/bin/bash

echo "🔬 Stark Biome Drift Report"
echo "=========================="

SHELL_FILES="Shell.tsx NavigationTree.tsx ElasticCard.tsx Terminal.tsx"
TOTAL=0

for pattern in "bg-gray-" "text-gray-" "border-gray-"; do
  COUNT=$(grep -r "$pattern" impl/claude/web/src --include="*.tsx" | wc -l)
  echo "$pattern: $COUNT occurrences"
  TOTAL=$((TOTAL + COUNT))
done

echo "=========================="
echo "Total drift: $TOTAL"

if [ $TOTAL -gt 0 ]; then
  echo ""
  echo "Top offenders:"
  grep -r "bg-gray-" impl/claude/web/src --include="*.tsx" -c | sort -t: -k2 -rn | head -10
fi
```

---

## The 90/10 Enforcement

**Rule**: New code MUST use semantic tokens. Old code migrates when touched.

- `bg-steel-*` for 90% (frame, containers, backgrounds)
- `bg-life-*`, `glow-*`, `jewel-*` for 10% (living accents, earned glow)
- `text-glow-light` for emphasis (not `text-white`)
- `rounded-bare` for edges (not `rounded-lg`)

---

## Quick Start

```bash
# 1. See the current state
grep -r "bg-gray-" impl/claude/web/src --include="*.tsx" | wc -l

# 2. Migrate a file
# Replace: bg-gray-900 → bg-steel-obsidian
# Replace: bg-gray-800 → bg-steel-carbon
# Replace: bg-gray-700 → bg-steel-gunmetal
# Replace: text-gray-* → text-steel-zinc

# 3. Verify
cd impl/claude/web && npm run typecheck
```

---

*"The coldness is the point. Don't add warmth back."*

Filed: 2025-12-22
