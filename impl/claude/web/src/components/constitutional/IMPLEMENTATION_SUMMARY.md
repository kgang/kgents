# Constitutional Dashboard - Implementation Summary

## Overview

Production-quality React components for visualizing constitutional alignment and trust levels, following the established brutalist design patterns from the kgents codebase.

**Total Lines of Code**: 1,548 LOC
**Components**: 4 React components + 1 hook + type definitions
**Pattern**: Pure SVG visualization (no chart libraries)
**Style**: Brutalist design (steel colors, monospace fonts, minimal decoration)

## File Structure

```
src/components/constitutional/
├── ConstitutionalDashboard.tsx      (173 lines) - Main composite component
├── ConstitutionalDashboard.css      (192 lines) - Dashboard styles
├── ConstitutionalRadar.tsx          (232 lines) - 7-principle radar chart
├── ConstitutionalRadar.css          (66 lines)  - Radar chart styles
├── ConstitutionalScorecard.tsx      (237 lines) - Per-principle table
├── ConstitutionalScorecard.css      (200 lines) - Scorecard styles
├── TrustLevelBadge.tsx              (68 lines)  - Trust level indicator
├── TrustLevelBadge.css              (90 lines)  - Badge styles
├── useConstitutional.ts             (116 lines) - Data fetching hook
├── types.ts                         (96 lines)  - TypeScript definitions
├── index.ts                         (44 lines)  - Public exports
└── README.md                        (230 lines) - Usage documentation
```

## Components Implemented

### 1. ConstitutionalDashboard (Main)

**File**: `ConstitutionalDashboard.tsx`

Composite component that combines radar, scorecard, and trust badge. Fetches data via `useConstitutional` hook.

**Key Features**:
- Responsive layout (vertical/horizontal modes)
- Loading, error, and empty states
- Trust metrics display
- Dominant principles list
- Trust assessment reasoning

**Props**:
```typescript
{
  agentId: string;                    // Required
  layout?: 'horizontal' | 'vertical'; // Default: 'vertical'
  showRadar?: boolean;                // Default: true
  showScorecard?: boolean;            // Default: true
  showTrust?: boolean;                // Default: true
  subscribe?: boolean;                // Default: false (SSE)
}
```

### 2. ConstitutionalRadar (Visualization)

**File**: `ConstitutionalRadar.tsx`

Pure SVG heptagonal radar chart for the 7 constitutional principles.

**Key Features**:
- Pure SVG implementation (no dependencies)
- Color-coded by score (green >0.8, yellow 0.5-0.8, red <0.5)
- Tooltips on hover
- Grid circles (0.2, 0.4, 0.6, 0.8, 1.0)
- Axis lines and labels
- Summary score display

**Visual Encoding**:
- Area fill: Overall satisfaction
- Color gradient: Health status
- Dots on vertices: Individual principle scores

**Pattern Match**: Follows `components/dp/ValueFunctionChart.tsx` (250 LOC radar chart)

### 3. ConstitutionalScorecard (Table)

**File**: `ConstitutionalScorecard.tsx`

Detailed table showing per-principle scores with health indicators.

**Key Features**:
- Score bars (0-100%)
- Health color coding
- Trust averages (when available)
- Dominant/weakest principle insights
- Violation count display
- Tier indicator (EMPIRICAL, NOETHERIAN, GALOIS)

**Pattern Match**: Follows `components/dp/ConstitutionScorecard.tsx`

### 4. TrustLevelBadge (Indicator)

**File**: `TrustLevelBadge.tsx`

Color-coded badge for trust levels (L0-L3).

**Trust Levels**:
- **L0** (Gray): Read-Only (default)
- **L1** (Blue): Bounded (earned trust)
- **L2** (Green): Suggestion (high trust)
- **L3** (Gold): Autonomous (maximum trust)

**Features**:
- Three sizes (sm, md, lg)
- Hover tooltip with reasoning
- Smooth transitions

### 5. useConstitutional (Hook)

**File**: `useConstitutional.ts`

Data fetching hook following the `useDirector` pattern.

**Features**:
- Auto-fetch on mount
- SSE subscription support
- Loading/error states
- Refresh function

**Pattern Match**: Follows `hooks/useDirector.ts` (264 LOC)

## Type Definitions

**File**: `types.ts`

Complete TypeScript definitions matching backend structures:

```typescript
// Core types
ConstitutionalAlignment    // Mark evaluation scores
ConstitutionalTrustResult  // Trust computation result
ConstitutionalData         // Combined dashboard data

// Enums
Principle                  // 7 constitutional principles
TrustLevel                 // L0-L3 trust levels

// Constants
PRINCIPLE_LABELS           // Human-readable names
PRINCIPLE_DESCRIPTIONS     // Descriptions
```

**Backend Sources**:
- `services/witness/mark.py` → `ConstitutionalAlignment`
- `services/witness/trust/constitutional_trust.py` → `ConstitutionalTrustResult`

## Design System Compliance

### Color Palette

**Steel Colors** (from `design/tokens.css`):
```css
--steel-950  /* Background */
--steel-900  /* Panels */
--steel-800  /* Borders */
--steel-700  /* Grid lines */
--steel-500  /* Muted text */
--steel-400  /* Secondary text */
--steel-300  /* Labels */
--steel-200  /* Primary text */
```

**Health Colors** (from `design/tokens.css`):
```css
--health-healthy: #22c55e;   /* >= 80% — green-500 */
--health-degraded: #facc15;  /* 60-80% — yellow-400 */
--health-warning: #f97316;   /* 40-60% — orange-500 */
--health-critical: #ef4444;  /* < 40% — red-500 */
```

### Typography

- **Monospace**: `var(--font-mono)` for all text
- **Font sizes**: `var(--font-size-{xs,sm,base,lg,xl,2xl})`
- **Line heights**: Minimal, function-first

### Spacing

- **Gaps**: `var(--space-{xs,sm,md,lg})`
- **Padding**: Consistent with other dashboards
- **Border radius**: `var(--radius-{sm,md,lg,full})`

## API Integration

**Endpoint**: `GET /api/witness/constitutional/{agentId}`

**Response**:
```typescript
{
  alignment: ConstitutionalAlignment | null;
  trust: ConstitutionalTrustResult | null;
  agent_id: string;
  updated_at: string;
}
```

**SSE Subscription**: `/api/witness/stream?agent_id={agentId}&type=constitutional`

## The 7 Constitutional Principles

1. **TASTEFUL** - Clear, justified purpose
2. **CURATED** - Intentional selection
3. **ETHICAL** - Augments, never replaces
4. **JOY_INDUCING** - Delight in interaction
5. **COMPOSABLE** - Morphisms in a category
6. **HETERARCHICAL** - Flux, not hierarchy
7. **GENERATIVE** - Spec as compression

See: `spec/principles.md` and `CLAUDE.md` → Core Principles

## Pattern Adherence

### ✓ Follows Established Patterns

- **Pure SVG**: Like `ValueFunctionChart.tsx` (no recharts/d3)
- **Hook pattern**: Like `useDirector.ts` (state + actions)
- **Brutalist design**: Steel colors, monospace fonts
- **CSS co-location**: Each component has its own CSS file
- **TypeScript strict**: All types defined, no `any`
- **Empty states**: Loading, error, empty placeholders
- **Keyboard nav**: Accessible, semantic HTML

### ✓ References Used

1. **`components/dp/DPDashboard.tsx`** - Composite layout pattern
2. **`components/dp/ValueFunctionChart.tsx`** - SVG radar chart (250 LOC)
3. **`components/dp/ConstitutionScorecard.tsx`** - Table visualization
4. **`components/chat/ConstitutionalRadar.tsx`** - 7-principle radar
5. **`hooks/useDirector.ts`** - Data fetching hook pattern

## Quality Checklist

- ✅ TypeScript: No errors, all types defined
- ✅ Linting: No errors (eslint passes)
- ✅ Brutalist design: Steel colors, monospace fonts
- ✅ Pure SVG: No external chart dependencies
- ✅ Responsive: Vertical/horizontal layouts
- ✅ Accessible: Semantic HTML, ARIA labels
- ✅ Co-located CSS: Each component has styles
- ✅ Empty states: Loading, error, empty placeholders
- ✅ Documentation: README.md with examples
- ✅ Pattern match: Follows existing DP dashboard

## Usage Example

```tsx
import { ConstitutionalDashboard } from '@/components/constitutional';

export default function ConstitutionalPage() {
  return (
    <div className="page-container">
      <h1>Constitutional Alignment</h1>
      <ConstitutionalDashboard
        agentId="claude"
        layout="vertical"
        subscribe={true}
      />
    </div>
  );
}
```

## Next Steps (Backend Integration)

To make this fully functional, the backend needs:

1. **API Endpoint**: `protocols/api/witness.py`
   ```python
   @router.get("/constitutional/{agent_id}")
   async def get_constitutional(agent_id: str):
       # Fetch latest alignment + trust for agent
       return ConstitutionalData(...)
   ```

2. **SSE Stream**: Add constitutional event type to existing `/api/witness/stream`

3. **Service Integration**:
   - Use `MarkConstitutionalEvaluator` for alignment
   - Use `ConstitutionalTrustComputer` for trust

The frontend is **ready to integrate** once the endpoint is live.

## Files Changed

**New Files** (13 total):
```
impl/claude/web/src/components/constitutional/
  ConstitutionalDashboard.tsx
  ConstitutionalDashboard.css
  ConstitutionalRadar.tsx
  ConstitutionalRadar.css
  ConstitutionalScorecard.tsx
  ConstitutionalScorecard.css
  TrustLevelBadge.tsx
  TrustLevelBadge.css
  useConstitutional.ts
  types.ts
  index.ts
  README.md
  IMPLEMENTATION_SUMMARY.md
```

**No modifications** to existing files.

---

**Implementation Date**: 2025-12-25
**Total LOC**: 1,548
**Status**: ✅ Complete, awaiting backend endpoint
