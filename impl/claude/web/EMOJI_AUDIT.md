# Emoji Audit Report

**Date:** 2025-12-17
**Status:** Phase 2 Complete
**Policy:** Per `docs/creative/visual-system.md` and `spec/protocols/os-shell.md`, kgents uses Lucide icons exclusively for semantic iconography. Emojis are NOT used in kgents-authored copy.

---

## Executive Summary

This audit identifies all emoji usage in the kgents web codebase and provides a migration path to Lucide icons. The audit found **~150 emoji instances** across **25+ files**.

**Migration Status:** Core infrastructure complete. All primary components migrated to Lucide icons.

---

## Phase 1: Foundation (COMPLETED)

### Created: JEWEL_ICONS Constant

**File:** `src/constants/jewels.ts`

```typescript
import { Brain, Network, Leaf, Palette, Users, Theater, Building } from 'lucide-react';

export const JEWEL_ICONS: Record<JewelName, LucideIcon> = {
  brain: Brain,       // Cyan family - Knowledge, memory
  gestalt: Network,   // Green family - Growth, health
  gardener: Leaf,     // Lime family - Cultivation, nurturing
  atelier: Palette,   // Amber family - Creation, creativity
  coalition: Users,   // Violet family - Collaboration, synthesis
  park: Theater,      // Pink family - Drama, narrative
  domain: Building,   // Red family - Urgency, crisis
} as const;
```

### Updated: PersonalityLoading.tsx

- Removed emoji from `JEWEL_CONFIG`
- Now uses `JEWEL_ICONS` and `JEWEL_COLORS` from constants
- Icon sizes: sm=24px, md=40px, lg=64px
- TreeIcon (Leaf) used for organic/forest mode

### Updated: EmpathyError.tsx

- Created `ERROR_CONFIG` with Lucide icons:
  - `network` -> Wifi
  - `notfound` -> MapPin
  - `permission` -> Lock
  - `timeout` -> Clock
  - `validation` -> FileText
  - `unknown` -> HelpCircle
- `InlineError` now uses `AlertTriangle` icon

---

## Phase 2: Core Migration (COMPLETED)

### Created: Centralized Icons Constants

**File:** `src/constants/icons.ts` (NEW)

Comprehensive icon mappings for all semantic contexts:

```typescript
// Phase/Lifecycle Icons
export const PHASE_ICONS: Record<string, LucideIcon> = {
  PLAN: ClipboardList, RESEARCH: Search, DEVELOP: Wrench,
  STRATEGIZE: Target, 'CROSS-SYNERGIZE': Link, IMPLEMENT: Cog,
  QA: Microscope, TEST: TestTube, EDUCATE: GraduationCap,
  MEASURE: BarChart3, REFLECT: BookOpen, SENSE: Eye, ACT: Zap,
};

// Gardener Phase Icons
export const GARDENER_PHASE_ICONS = { SENSE: Eye, ACT: Zap, REFLECT: MessageCircle };

// Citizen Phase Icons
export const CITIZEN_PHASE_ICONS = {
  IDLE: CircleDot, SOCIALIZING: MessageCircle, WORKING: Wrench,
  REFLECTING: BookOpen, RESTING: Cloud,
};

// Builder Icons (Workshop)
export const BUILDER_ICONS_LUCIDE = {
  Scout: Compass, Sage: GraduationCap, Spark: Zap, Steady: Hammer, Sync: Link,
};

// Crisis Phase Icons (Park)
export const CRISIS_PHASE_ICONS = {
  NORMAL: CheckCircle, INCIDENT: AlertTriangle, RESPONSE: Zap, RECOVERY: RefreshCw,
};

// Timer Status Icons (Park)
export const TIMER_STATUS_ICONS = {
  PENDING: Circle, ACTIVE: Play, WARNING: AlertTriangle,
  CRITICAL: XCircle, EXPIRED: XCircle, COMPLETED: CheckCircle, PAUSED: Pause,
};

// Mask Archetype Icons (Park)
export const MASK_ARCHETYPE_ICONS = {
  TRICKSTER: Sparkles, DREAMER: Cloud, SKEPTIC: Search, ARCHITECT: Building2,
  CHILD: Star, SAGE: Bird, WARRIOR: Swords, HEALER: Heart,
};

// Infrastructure Entity Icons (GestaltLive)
export const INFRA_ENTITY_ICONS = {
  namespace: Box, node: Monitor, pod: Server, service: Link,
  deployment: Play, container: Box, nats_subject: Mail, nats_stream: Wind,
  database: Database, volume: HardDrive, custom: Cog,
};

// Severity Icons
export const SEVERITY_ICONS = {
  info: Info, warning: AlertTriangle, error: XCircle, critical: AlertTriangle,
};
```

### Updated: Crown.tsx

- Replaced `JEWEL_EMOJI` imports with `JEWEL_ICONS`
- Changed emoji properties to `icon` properties
- Hero steps now render `<step.icon />` components
- Extension jewels use `<ext.icon />` components
- Crown header uses `<CrownIcon />` from Lucide
- Checkmarks use `<Check />` from Lucide

### Updated: PlotCard.tsx

- Removed `CROWN_JEWEL_EMOJI` constant
- Added `getJewelIconForPlot()` function using `JEWEL_ICONS`
- Both `PlotCard` and `PlotListItem` now render Lucide icons
- Fallback to `FolderOpen` icon for non-jewel plots

### Updated: api/types.ts

- Added deprecation notices to emoji-based configs
- Updated all config objects to use icon names (strings):
  - `BUILDER_ICONS` - now string icon names
  - `NPHASE_CONFIG.icons` - now Lucide icon names
  - `POLYNOMIAL_CONFIG` - changed `emoji` to `icon` fields
  - `PARK_PHASE_CONFIG` - changed `emoji` to `icon`
  - `PARK_TIMER_CONFIG` - changed `emoji` to `icon`
  - `PARK_MASK_CONFIG` - changed `emoji` to `icon`
  - `INFRA_ENTITY_CONFIG` - changed `icon` from emoji to Lucide name
  - `INFRA_SEVERITY_CONFIG` - changed `icon` from emoji to Lucide name
- Added `icon?: string` field to `PolynomialPosition` interface
- Marked `emoji` field as deprecated

### Updated: polynomial/visualizations.ts

- Changed all phase configs from `emoji` to `icon` field
- `GARDENER_PHASES`, `NPHASE_PHASES`, `CITIZEN_PHASES` now use Lucide icon names
- Visualization factory functions use `icon` instead of `emoji`

### Updated: Park Components

**MaskSelector.tsx:**
- Imports `getMaskArchetypeIcon` from constants
- `MaskCard` renders `<MaskIcon />` component
- `CurrentMaskBadge` uses Lucide icons
- Empty state uses `<Theater />` icon
- Active indicator uses `<Check />` icon

**PhaseTransition.tsx:**
- Imports `getCrisisPhaseIcon` from constants
- `PhaseNode` renders `<PhaseIcon />` component
- `PhaseIndicator` uses Lucide icons

**TimerDisplay.tsx:**
- Imports `TIMER_STATUS_ICONS` from constants
- Renders `<StatusIcon />` component based on timer status

---

## Migration Pattern

Components now follow this pattern:

```tsx
// Before (deprecated)
const config = SOME_CONFIG[type];
return <span>{config.emoji}</span>;

// After (current)
import { getSomeIcon } from '@/constants';
const Icon = getSomeIcon(type);
return <Icon className="w-5 h-5" style={{ color: config.color }} />;
```

Or using config icon strings:

```tsx
// For data files (api/types.ts), icons are stored as Lucide names
const config = { icon: 'check-circle', color: '#22c55e' };

// Components look up the actual icon
import { CRISIS_PHASE_ICONS } from '@/constants';
const Icon = CRISIS_PHASE_ICONS[phase];
return <Icon className="w-5 h-5" />;
```

---

## Phase 3: Garden & Supporting Components (COMPLETED)

### Updated: SeasonIndicator.tsx

- Removed emoji from `SEASON_CONFIG`
- Now uses `getSeasonIcon()` from `@/constants`
- Both `SeasonIndicator` and `SeasonBadge` render Lucide icons

### Updated: GestureHistory.tsx

- Removed emoji from `VERB_CONFIG`
- Now uses `getVerbIcon()` from `@/constants`
- Both `GestureItem` and `GestureList` render Lucide icons
- Empty state uses `<Sprout />` icon

### Updated: BrainCanvas.tsx

- Replaced emoji strings in `FloatingActions` with Lucide components
- Uses `Network`, `LayoutGrid`, `Sparkles`, `Settings` icons

### Updated: constants/icons.ts

Added new icon exports:
```typescript
// Garden season icons
export const SEASON_ICONS: Record<string, LucideIcon> = {
  DORMANT: Moon,
  SPROUTING: Sprout,
  BLOOMING: Flower2,
  HARVEST: Wheat,
  COMPOSTING: Leaf,
};

// Tending verb icons
export const VERB_ICONS: Record<string, LucideIcon> = {
  OBSERVE: Eye,
  PRUNE: Scissors,
  GRAFT: GitBranch,
  WATER: Droplets,
  ROTATE: RotateCw,
  WAIT: Hourglass,
};

// Action icons (for FloatingActions)
export const ACTION_ICONS = {
  refresh: RefreshCw,
  settings: Settings,
  capture: Sparkles,
  topology: Network,
  panels: LayoutGrid,
  chart: BarChart3,
};
```

---

## Remaining Files (Lower Priority)

Files with emoji usage that are lower priority for migration:

| File | Status | Notes |
|------|--------|-------|
| `src/pages/Workshop.tsx` | LOW | Builder personality display - decorative |
| `src/pages/LayoutGallery.tsx` | LOW | Demo/gallery - example code only |
| `src/pages/GestaltLive.tsx` | LOW | Loading/refresh icons |
| `src/reactive/schema.ts` | LOW | Error type emojis (2 instances) |
| `src/components/error/FriendlyError.tsx` | LOW | Uses emoji for visual impact |
| `src/components/synergy/types.ts` | LOW | Toast notification icons |
| `src/components/garden/TransitionSuggestionBanner.tsx` | LOW | Season display |
| `src/components/garden/GardenVisualization.tsx` | LOW | Verb action buttons |
| `src/components/three/QualitySelector.tsx` | LOW | Quality indicators |
| `src/components/eigenvector/EigenvectorRadar.tsx` | LOW | Dimension labels |
| `src/components/brain/CrystalDetail.tsx` | LOW | Security warnings |
| `src/components/gestalt/types.ts` | LOW | Default config icons |
| `src/components/elastic/*.tsx` | LOW | Example/placeholder code |

### Test Files (Update As Needed)

Test files should be updated when their corresponding components change:
- `tests/unit/joy/joy-components.test.tsx`
- `tests/unit/polynomial/PolynomialDiagram.test.tsx`
- `tests/unit/components/CitizenPanel.test.tsx`

---

## Allowed Emoji Exceptions

Per `docs/creative/visual-system.md`, emojis ARE allowed in:

1. **User-generated content** - Users may use emojis in their messages
2. **Explicit personality moments** - Loading state messages (sparingly)
3. **Data display** - Where emojis are part of the data being displayed

---

## Verification Commands

```bash
# Verify typecheck passes
cd impl/claude/web && npm run typecheck

# Find remaining emoji usage (if any)
grep -r '[\U0001F300-\U0001F9FF]' impl/claude/web/src --include="*.tsx" --include="*.ts"

# Run tests
cd impl/claude/web && npm run test:run
```

---

## Summary of Changes

| Category | Files Changed | Description |
|----------|--------------|-------------|
| Constants | `jewels.ts`, `icons.ts` (new), `index.ts` | Icon infrastructure |
| Types | `api/types.ts` | Config fields, deprecation notices |
| Pages | `Crown.tsx` | Hero path icons |
| Components | `PlotCard.tsx`, `MaskSelector.tsx`, `PhaseTransition.tsx`, `TimerDisplay.tsx` | Icon rendering |
| Visualizations | `polynomial/visualizations.ts` | Phase icon names |
| Joy | `PersonalityLoading.tsx`, `EmpathyError.tsx` | Error/loading icons |
| Garden | `SeasonIndicator.tsx`, `GestureHistory.tsx` | Season/verb icons |
| Brain | `BrainCanvas.tsx` | FloatingActions icons |

---

## Track B Completion Checklist

### Core Infrastructure ✅
- [x] `JEWEL_ICONS` constant in `constants/jewels.ts`
- [x] `JEWEL_COLORS` constant in `constants/jewels.ts`
- [x] Icon helper functions (`getJewelIcon`, `getPhaseIcon`, etc.)
- [x] Exports from `constants/index.ts`

### Phase Icons ✅
- [x] `PHASE_ICONS` - Development lifecycle
- [x] `GARDENER_PHASE_ICONS` - Gardener session phases
- [x] `CITIZEN_PHASE_ICONS` - Citizen polynomial phases
- [x] `CRISIS_PHASE_ICONS` - Park crisis phases
- [x] `TIMER_STATUS_ICONS` - Park timer states
- [x] `MASK_ARCHETYPE_ICONS` - Park dialogue masks

### Garden Icons ✅
- [x] `SEASON_ICONS` - Garden seasons
- [x] `VERB_ICONS` - Tending verbs
- [x] `ACTION_ICONS` - FloatingActions

### Crown Jewel Pages ✅
- [x] Brain.tsx - Projection-first (45 LOC)
- [x] Gestalt.tsx - Projection-first (59 LOC)
- [x] Gardener.tsx - Projection-first (64 LOC)
- [x] Atelier.tsx - Projection-first (65 LOC)
- [x] Town.tsx - StreamPathProjection (48 LOC)
- [x] ParkScenario.tsx - Projection-first (30 LOC)

### Shell Integration ✅
- [x] PathProjection component
- [x] StreamPathProjection component
- [x] ShellProvider context
- [x] Shell tests

### Remaining (Lower Priority)
- [ ] Workshop.tsx emojis
- [ ] FriendlyError.tsx emojis
- [ ] Synergy toast icons
- [ ] Example/placeholder code

---

*Generated by emoji-audit phase of OS Shell implementation*
*Last Updated: 2025-12-17*
