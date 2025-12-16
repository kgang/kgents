# UI Isomorphism Detection

> *"When the same conditional appears three times, you've found a dimension hiding in plain sight."*

## When to Use

- Noticing repeated `if/switch` statements on the same condition
- Seeing parallel code paths for different modes/screens/roles
- Drowning in boolean props (`isMobile`, `isCompact`, `showLabels`, `isAdmin`)
- Feeling like components "should" be simpler but keep growing

This is a **meta-skill**—it teaches you to find patterns that become first-class abstractions.

---

## Signs You've Found an Isomorphism

### 1. Repeated Conditionals

The same `if` condition appearing in 3+ places:

```tsx
// Signal: "isMobile" appears everywhere
{isMobile && <MobileHeader />}
{isMobile ? 15 : 50}
{isMobile && <FloatingAction />}
className={isMobile ? 'p-2' : 'p-4'}
```

**Insight**: `isMobile` is not a boolean—it's a **dimension** (density) in disguise.

### 2. Parallel Structures

Similar code for different cases:

```tsx
// Signal: Same structure, different values
if (screenSize === 'mobile') {
  return { nodeSize: 0.2, fontSize: 14, maxLabels: 15 };
} else if (screenSize === 'tablet') {
  return { nodeSize: 0.25, fontSize: 16, maxLabels: 30 };
} else {
  return { nodeSize: 0.3, fontSize: 18, maxLabels: 50 };
}
```

**Insight**: These aren't three cases—they're three points on a `density` manifold.

### 3. Configuration Explosion

Too many boolean/enum props:

```tsx
<Panel
  isMobile={isMobile}
  isCompact={isCompact}
  showLabels={showLabels}
  showLegend={showLegend}
  isDrawer={isDrawer}
  minimalMode={minimalMode}
/>
```

**Insight**: These booleans aren't independent—they cluster along hidden dimensions.

### 4. Cross-Cutting Concerns

Same logic needed at multiple component levels:

```tsx
// In Header.tsx
const fontSize = isMobile ? 'text-sm' : 'text-lg';

// In Card.tsx
const padding = isMobile ? 'p-2' : 'p-4';

// In Chart.tsx
const dataPoints = isMobile ? 50 : 200;
```

**Insight**: These components share a dimension (`density`) that should flow through context.

---

## The Extraction Algorithm

When you detect an isomorphism, follow this algorithm:

### Step 1: Name the Dimension

Give the hidden dimension an explicit name:

| Scattered Conditionals | Named Dimension |
|------------------------|-----------------|
| `isMobile`, `isSmall`, `!isDesktop` | `density` |
| `isAdmin`, `isEditor`, `!isViewer` | `role` |
| `isPro`, `isEnterprise`, `!isFree` | `tier` |
| `isDark`, `isLight`, `!isSystem` | `theme` |
| `isLoading`, `isError`, `isSuccess` | `loadState` |

### Step 2: Define the Values

List all possible values (must be exhaustive and mutually exclusive):

```typescript
type Density = 'compact' | 'comfortable' | 'spacious';
type Role = 'viewer' | 'editor' | 'admin';
type Tier = 'free' | 'pro' | 'enterprise';
type LoadState = 'idle' | 'loading' | 'success' | 'error';
```

### Step 3: Create a Context/Hook

Provide the dimension at the appropriate level:

```typescript
// Window-level dimension
function useWindowLayout(): { density: Density; ... } {
  const width = useWindowWidth();
  return {
    density: width < 640 ? 'compact' : width < 1024 ? 'comfortable' : 'spacious',
    // ...
  };
}

// User-level dimension
const RoleContext = createContext<Role>('viewer');
function useRole(): Role {
  return useContext(RoleContext);
}
```

### Step 4: Define Constants Parameterized by Dimension

Replace scattered values with lookup tables:

```typescript
// Before: Scattered magic numbers
const fontSize = isMobile ? 14 : 18;

// After: Parameterized constants
const FONT_SIZE = {
  compact: 14,
  comfortable: 16,
  spacious: 18,
} as const;

const fontSize = FONT_SIZE[density];
```

### Step 5: Update Components to Receive Dimension

Components adapt internally, not externally:

```tsx
// Before: External conditionals
{isMobile ? <CompactPanel {...props} /> : <FullPanel {...props} />}

// After: Internal adaptation
<Panel density={density} {...props} />

// Panel.tsx
function Panel({ density, ...props }) {
  const isCompact = density === 'compact';
  // Component decides what density means for it
  return (
    <div className={isCompact ? 'p-2' : 'p-4'}>
      {/* ... */}
    </div>
  );
}
```

### Step 6: Remove All Ad-Hoc Conditionals

Audit the codebase for remaining scattered conditionals:

```bash
# Find remaining isMobile checks
grep -r "isMobile" src/components/

# Should find ZERO occurrences outside hooks
# All isMobile → density translation happens in useWindowLayout()
```

---

## Validation Checklist

Use this checklist to verify a successful extraction:

- [ ] **Dimension has a clear name** (not "mode" or "type" — be specific)
- [ ] **Values are exhaustive** (no "other" case needed)
- [ ] **Values are mutually exclusive** (can only be one at a time)
- [ ] **Context provided at appropriate level** (window/page/component)
- [ ] **Components adapt internally** (receive dimension, decide behavior)
- [ ] **No remaining ad-hoc conditionals** for this dimension
- [ ] **Constants are parameterized** (lookup tables, not switch statements)

---

## Common Isomorphisms in kgents

| Hidden in... | Revealed as... | Context |
|--------------|----------------|---------|
| `isMobile`, `isTablet`, `isDesktop` | `density: 'compact' \| 'comfortable' \| 'spacious'` | `useWindowLayout()` |
| `isViewer`, `isEditor`, `isAdmin` | `role: Role` | `RoleContext` |
| `isFree`, `isPro`, `isEnterprise` | `tier: LicenseTier` | `useLicensing()` |
| `isLoading`, `hasError` | `loadState: LoadState` | Component state |
| `isConnected`, `isDisconnected` | `connectionState: ConnectionState` | `useConnection()` |
| Observer-specific rendering | `umwelt: Umwelt` | AGENTESE |

---

## Advanced: Dimension Composition

Sometimes dimensions compose orthogonally:

```typescript
// Two independent dimensions
type Density = 'compact' | 'comfortable' | 'spacious';
type Theme = 'light' | 'dark';

// Cross-product yields valid combinations
// compact × light, compact × dark, comfortable × light, ...
```

Sometimes they collapse:

```typescript
// mobile + viewer ≅ compact (for our purposes)
// The isomorphism lets us ignore the distinction
```

Recognize when dimensions are **truly independent** vs. when they're **secretly the same**.

---

## The Isomorphism Test

Ask yourself: "Can I describe the behavior without mentioning the original condition?"

**Before** (fails test):
> "On mobile, we show fewer labels and use a drawer for the control panel."

**After** (passes test):
> "In compact density, we show fewer labels and use a drawer for panels."

If you can describe behavior in terms of the named dimension, the extraction succeeded.

---

## Anti-Patterns

### Premature Extraction

Don't extract until you see 3+ occurrences:

```tsx
// Only one conditional? Just use it directly.
{isAdmin && <AdminBadge />}

// Three+ occurrences? Extract the dimension.
```

### Over-Abstraction

Not every boolean needs to become a dimension:

```tsx
// Simple toggle state is fine as boolean
const [isOpen, setIsOpen] = useState(false);

// Don't create: type OpenState = 'open' | 'closed';
```

### Leaky Abstractions

If components still need the original condition, extraction failed:

```tsx
// BAD: Component receives density but still checks isMobile
function Panel({ density }) {
  const { isMobile } = useWindowLayout(); // Leaking!
  // ...
}

// GOOD: Component only knows about density
function Panel({ density }) {
  const isDrawer = density === 'compact';
  // ...
}
```

---

## The Categorical Perspective

Isomorphism detection is **functor discovery**:

```
Functor F: Condition → Behavior

Before: Many scattered F₁, F₂, F₃ (each conditional)
After:  One F (parameterized by dimension)
```

When you name the dimension, you're naming the **domain** of the functor. When you create constants parameterized by that dimension, you're defining the functor's **action**.

The extraction succeeds when:
- `F(compact) → CompactBehavior`
- `F(comfortable) → ComfortableBehavior`
- `F(spacious) → SpaciousBehavior`

And these three cases **compose** correctly with the rest of the system.

---

## Page Audit Workflow

When auditing a codebase for missing isomorphisms (based on the Session 8 elastic audit):

### Step 1: Create Audit Checklist

For each page, check:

```markdown
- [ ] Uses `useWindowLayout()` for density/breakpoint info
- [ ] Passes `density` to child components (not `isMobile`)
- [ ] No scattered `isMobile` / `isTablet` / `isDesktop` conditionals in components
- [ ] Constants parameterized by density (lookup tables, not ternaries)
- [ ] Uses `ElasticSplit` for two-pane layouts
- [ ] Has dedicated mobile layout (not just "squished desktop")
- [ ] Uses `BottomDrawer` for panels on mobile
- [ ] Uses `FloatingActions` for action buttons on mobile
- [ ] Touch targets minimum 48px (w-12 h-12)
- [ ] Smart defaults: labels off, fewer items on mobile
- [ ] Loading/error states are density-aware
```

### Step 2: Categorize Violations

| Severity | Description | Examples |
|----------|-------------|----------|
| **Critical** | Page completely lacks responsive support | No `useWindowLayout`, fixed widths |
| **Major** | Has some patterns but inconsistent | Uses ElasticSplit but no mobile layout |
| **Minor** | Missing polish or optimization | Constants not parameterized |

### Step 3: Document Findings

Create an audit report with:

```markdown
## Page: Brain.tsx

**Status**: NEEDS REFACTOR

### Checklist Assessment
- [ ] Uses `useWindowLayout()` — **MISSING**
- [x] Uses `ElasticSplit` — **YES**
- [ ] Has dedicated mobile layout — **MISSING**

### Critical Issues
1. **No responsive layout** (line 258)
   - Sidebar fixed at `w-80`
   - No collapse behavior
   - Recommendation: Replace with ElasticSplit

### Major Issues
1. **No useWindowLayout** - Components can't adapt to density
```

### Step 4: Prioritize Refactoring

Order by:
1. **Critical issues first** — Pages with no responsiveness
2. **User-facing pages** — Most visited pages
3. **Consistency** — Pages that feel different from others

### Step 5: Apply Patterns Systematically

For each page:
1. Add `useWindowLayout()` to get density context
2. Add mobile layout branch with drawers/floating actions
3. Update ElasticSplit to use `resizable={isDesktop}`
4. Pass `density` to all sub-components
5. Extract constants to density lookup tables
6. Test at 375px, 768px, 1024px, 1440px

### Common Issues Found in Audits

| Issue | Where Found | Fix |
|-------|-------------|-----|
| Hook called but values unused | Workshop.tsx | Destructure and use values |
| Only using `isMobile`, ignoring density | Inhabit.tsx | Use full density context |
| Fixed widths (`w-80`, `w-64`) | Brain.tsx | Replace with ElasticSplit |
| No mobile layout at all | Brain.tsx | Add `if (isMobile)` branch |
| `resizable={true}` always | Town.tsx | Change to `resizable={isDesktop}` |

---

## Audit Report Template

```markdown
# Elastic UI Audit Report

**Date**: YYYY-MM-DD
**Auditor**: [name]
**Reference**: Gestalt.tsx (gold standard)

## Executive Summary

| Page | Status | Critical | Major | Minor |
|------|--------|----------|-------|-------|
| Page1.tsx | NEEDS REFACTOR | 2 | 3 | 1 |
| Page2.tsx | PARTIAL | 0 | 2 | 2 |

## Detailed Findings

### Page1.tsx

**Checklist**:
- [ ] item1
- [x] item2

**Issues**:
1. Description (line number)
   - Code example
   - Recommendation

## Recommended Fix Order

1. Page1 — Critical issues
2. Page2 — Major issues
3. Page3 — Minor polish
```

---

## Related

- `docs/skills/elastic-ui-patterns.md` — Using the density isomorphism
- `spec/principles.md` — AD-008 Simplifying Isomorphisms
- `spec/protocols/agentese.md` — Observer-dependent perception (the original isomorphism)
- `plans/web-refactor/elastic-audit-report.md` — Real audit report example

---

*"The noun is a lie. There is only the rate of change."*
— AGENTESE, applying equally to UI and ontology
