# UI Isomorphism Detection

> *"When the same conditional appears three times, you've found a dimension hiding in plain sight."*

**Theory**: See `spec/protocols/projection.md` (AD-008 Applied section)
**Patterns**: See `docs/skills/elastic-ui-patterns.md`

This skill provides **practical audit workflows** for applying AD-008 to codebases.

---

## Page Audit Workflow

When auditing a codebase for missing isomorphisms:

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

## Common Issues Found in Audits

| Issue | Where Found | Fix |
|-------|-------------|-----|
| Hook called but values unused | Workshop.tsx | Destructure and use values |
| Only using `isMobile`, ignoring density | Inhabit.tsx | Use full density context |
| Fixed widths (`w-80`, `w-64`) | Brain.tsx | Replace with ElasticSplit |
| No mobile layout at all | Brain.tsx | Add `if (isMobile)` branch |
| `resizable={true}` always | Town.tsx | Change to `resizable={isDesktop}` |

---

## Related

- `spec/protocols/projection.md` — AD-008 Applied section (theory + core insight)
- `docs/skills/elastic-ui-patterns.md` — Using the density isomorphism
- `spec/principles.md` — AD-008 Simplifying Isomorphisms
- `agents/design/` — Design operads (LAYOUT, CONTENT, MOTION)

---

*Lines: ~125 (trimmed from 450)*
