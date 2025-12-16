# Continuation: Creative Direction Polish

> *"The garden grows not by force, but by invitation."*

## Context

Sessions 1-6 complete. Design tokens, Joy components, and voice constants are fully applied across all priority pages.

**Built Infrastructure**:
- `constants/colors.ts` - Full color system (jewels, states, seasons, health, archetypes)
- `constants/timing.ts` - Motion tokens (timing, easing, keyframes)
- `constants/messages.ts` - Voice constants (loading, errors, empty states, tooltips)
- `components/joy/` - Breathe, Pop, Shake, Shimmer, PersonalityLoading, EmpathyError
- `docs/creative/` - 8 creative direction documents

**Session 6 (2025-12-16)**: Applied voice constants across 5 pages:
- `Inhabit.tsx` - PersonalityLoading (coalition/inhabit), getEmptyState, TOOLTIPS.consentDebt
- `Workshop.tsx` - PersonalityLoading (atelier/create), getEmptyState for artisans/artifacts
- `Brain.tsx` - getEmptyState (noResults, noData), getLoadingMessage
- `GestaltLive.tsx` - getEmptyState for events, getLoadingMessage
- `Town.tsx` - getEmptyState for event feeds

---

## ✅ Completed: Voice Constants Applied

All priority pages now use semantic message constants:
- ✅ Empty states use `getEmptyState()` invitations
- ✅ Loading states use `PersonalityLoading` with jewel context
- ✅ Loading messages use `getLoadingMessage()` per jewel
- ✅ Tooltips use `TOOLTIPS` helpers (e.g., consentDebt)

---

## Next Session: Error State Polish

**Goal**: Replace remaining error states with `EmpathyError` component.

### Priority 1: Connection Errors

Find pages with manual error rendering:

```bash
# Find candidates
rg "error.*message|setError|connectionError" impl/claude/web/src/pages/ --type tsx
```

Replace with:
```tsx
import { EmpathyError } from '../components/joy';

{connectionError && (
  <EmpathyError
    type="network"
    onRetry={loadAllData}
    context="brain"
  />
)}
```

### Priority 2: Form Validation

Standardize validation error display using empathetic messages:

```tsx
import { getErrorMessage } from '../constants';

const { title, suggestions } = getErrorMessage('validation');
```

---

## Voice Checklist Per Page (Updated)

```markdown
### Voice Checklist
- [x] Empty states use `getEmptyState()` invitations
- [x] Loading uses `PersonalityLoading` with jewel context
- [ ] Errors use `EmpathyError` or empathetic titles ← NEXT
- [ ] Button labels are verbs (from `BUTTON_LABELS`)
- [ ] Tooltips are helpful, not redundant
```

---

## Quick Commands

```bash
# Find remaining error patterns
rg 'Failed to|Error:|Something went wrong' impl/claude/web/src/ --type tsx

# Typecheck after changes
cd impl/claude/web && npm run typecheck
```

---

## Audit Status

| Page | Empty States | Loading | Errors | Tooltips |
|------|--------------|---------|--------|----------|
| `Crown.tsx` | ✅ N/A | ✅ | ⬜ | ⬜ |
| `Brain.tsx` | ✅ | ✅ | ⬜ | ⬜ |
| `Inhabit.tsx` | ✅ | ✅ | ⬜ | ✅ |
| `Workshop.tsx` | ✅ | ✅ | ⬜ | ⬜ |
| `GestaltLive.tsx` | ✅ | ✅ | ⬜ | ⬜ |
| `Town.tsx` | ✅ | ✅ | ⬜ | ⬜ |

---

*"Assume intelligence. Errors are opportunities for empathy."*
