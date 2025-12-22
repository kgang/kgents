# Witness Fusion UX: Implementation Plan

> *"The arena breathes. The marks accumulate. The synthesis blooms. The veto thunders."*

**Status:** 📋 Ready for Implementation
**Design Spec:** `plans/witness-fusion-ux-design.md`
**Priority:** HIGH (joy-inducing daily workflow)
**Effort:** 5-7 sessions
**Filed:** 2025-12-22

---

## Overview

This plan implements the visual UX for Witness + Fusion—the "Living Arena" where Kent and Claude propose, challenge, and synthesize decisions. The backend (`km`, `kg witness`, `kg decide`) already works. This plan builds the **web frontend experience**.

**Prerequisites (all complete):**
- Agent-as-Witness conceptual framework ✅
- `km` CLI command ✅
- `kg witness` commands ✅
- `kg decide` / fusion CLI ✅
- Witness crystallization (678 tests) ✅

---

## Session Plan

| Session | Name | Tests | Key Deliverables |
|---------|------|-------|------------------|
| 1 | Witness Components | 25+ | MarkCard, MarkTimeline, QuickMarkForm |
| 2 | Witness Dashboard | 20+ | WitnessDashboard page, filtering, API hooks |
| 3 | Arena Primitives | 30+ | ProposalCard, SynthesisOrb, ChallengeFlow |
| 4 | Dialectical Arena | 25+ | DialecticalArena layout, VetoButton |
| 5 | Integration & Polish | 20+ | SSE streaming, mobile, teaching mode |

**Total:** ~120+ frontend tests

---

## Session 1: Witness Components (2-3 hrs)

**Goal:** Build the atomic components for displaying and creating marks.

### 1.1 MarkCard Component

**File:** `impl/claude/web/src/components/witness/MarkCard.tsx`

```typescript
interface MarkCardProps {
  mark: Mark;
  density?: 'compact' | 'comfortable' | 'spacious';
  onRetract?: (markId: string) => void;
}

// Display a single mark with:
// - Leaf emoji (🍂) timestamp
// - Action text
// - Reasoning (expandable in comfortable/spacious)
// - Principle chips
// - Author badge (kent/claude/system)
```

**Styling:**
- Use Living Earth palette (Soil background, Wood text)
- Breathing animation on hover (subtle scale 1.0 → 1.02)
- Density-aware: compact shows one line, spacious shows full reasoning

**Tests:**
- [ ] Renders mark action and timestamp
- [ ] Shows reasoning when expanded
- [ ] Displays principle chips
- [ ] Adapts to density modes
- [ ] Retract button calls onRetract

### 1.2 MarkTimeline Component

**File:** `impl/claude/web/src/components/witness/MarkTimeline.tsx`

```typescript
interface MarkTimelineProps {
  marks: Mark[];
  groupBy?: 'day' | 'session' | 'none';
  density?: 'compact' | 'comfortable' | 'spacious';
}

// Chronological display with:
// - Day/session separators
// - Virtualized list for performance
// - Loading states
```

**Tests:**
- [ ] Groups marks by day with separators
- [ ] Groups marks by session
- [ ] Handles empty state gracefully
- [ ] Virtualized for 1000+ marks
- [ ] Shows loading skeleton

### 1.3 QuickMarkForm Component

**File:** `impl/claude/web/src/components/witness/QuickMarkForm.tsx`

```typescript
interface QuickMarkFormProps {
  onSubmit: (mark: CreateMarkRequest) => Promise<void>;
  defaultPrinciples?: string[];
}

// Minimal friction mark creation:
// - Action input (required)
// - Reasoning input (optional, collapsed by default)
// - Principle chips (optional)
// - Submit on Enter
```

**Keyboard shortcuts:**
- `Enter` → Submit (action only)
- `Shift+Enter` → Expand reasoning field
- `Cmd+Enter` → Submit with reasoning

**Tests:**
- [ ] Submits on Enter
- [ ] Expands reasoning on Shift+Enter
- [ ] Shows principle chip selector
- [ ] Clears form after submit
- [ ] Shows loading state during submit
- [ ] Handles errors gracefully

### 1.4 API Types

**File:** `impl/claude/web/src/api/witness.ts`

```typescript
export interface Mark {
  id: string;
  action: string;
  reasoning?: string;
  principles: string[];
  author: 'kent' | 'claude' | 'system';
  session_id?: string;
  timestamp: string;
  retracted_at?: string;
  retracted_by?: string;
}

export interface CreateMarkRequest {
  action: string;
  reasoning?: string;
  principles?: string[];
}

export async function createMark(req: CreateMarkRequest): Promise<Mark>;
export async function getRecentMarks(limit?: number): Promise<Mark[]>;
export async function getMarksBySession(sessionId: string): Promise<Mark[]>;
export async function retractMark(markId: string, reason: string): Promise<Mark>;
```

### Exit Criteria

- [ ] All 3 components render correctly
- [ ] 25+ tests passing
- [ ] TypeScript strict mode passes
- [ ] Storybook stories for each component (optional)

---

## Session 2: Witness Dashboard (2-3 hrs)

**Goal:** Build the full Witness dashboard page with filtering and real-time updates.

### 2.1 WitnessDashboard Page

**File:** `impl/claude/web/src/pages/Witness.tsx`

```typescript
// Layout:
// ┌─────────────────────────────────────────────────────────────┐
// │  WITNESS: THE GARDEN OF MARKS                               │
// ├─────────────────────────────────────────────────────────────┤
// │  [QuickMarkForm]                                            │
// ├─────────────────────────────────────────────────────────────┤
// │  Filters: [Author ▼] [Principle ▼] [Date Range ▼]          │
// ├─────────────────────────────────────────────────────────────┤
// │  [MarkTimeline - grouped by day]                            │
// └─────────────────────────────────────────────────────────────┘
```

**Features:**
- Real-time updates via SSE (new marks appear at top)
- Filter by author (kent/claude/system/all)
- Filter by principle
- Date range picker
- Export to JSON

### 2.2 useWitness Hook

**File:** `impl/claude/web/src/hooks/useWitness.ts`

```typescript
interface UseWitnessOptions {
  limit?: number;
  author?: 'kent' | 'claude' | 'system';
  principles?: string[];
  sessionId?: string;
}

interface UseWitnessResult {
  marks: Mark[];
  isLoading: boolean;
  error: Error | null;
  createMark: (req: CreateMarkRequest) => Promise<Mark>;
  retractMark: (markId: string, reason: string) => Promise<void>;
  refetch: () => Promise<void>;
}

export function useWitness(options?: UseWitnessOptions): UseWitnessResult;
```

### 2.3 SSE Integration for Real-time Marks

**File:** `impl/claude/web/src/hooks/useMarkStream.ts`

```typescript
// Subscribe to /api/witness/stream for real-time mark events
// Uses EventSource with reconnection logic
// Integrates with React Query for cache updates

export function useMarkStream(onMark: (mark: Mark) => void): void;
```

### 2.4 Filter Components

**File:** `impl/claude/web/src/components/witness/MarkFilters.tsx`

```typescript
interface MarkFiltersProps {
  filters: MarkFilterState;
  onChange: (filters: MarkFilterState) => void;
}

interface MarkFilterState {
  author?: 'kent' | 'claude' | 'system';
  principles?: string[];
  dateRange?: { start: Date; end: Date };
}
```

### 2.5 Backend API Endpoint

**File:** `impl/claude/protocols/api/witness.py`

```python
# Ensure these endpoints exist:
# GET  /api/witness/marks?limit=N&author=X&principles=Y
# POST /api/witness/marks
# POST /api/witness/marks/{id}/retract
# GET  /api/witness/stream (SSE)
```

### Exit Criteria

- [ ] Dashboard page renders with all components
- [ ] Filtering works (author, principle, date)
- [ ] Real-time updates via SSE
- [ ] 20+ tests passing
- [ ] Mobile responsive

---

## Session 3: Arena Primitives (2-3 hrs)

**Goal:** Build the atomic components for the Dialectical Arena.

### 3.1 ProposalCard Component

**File:** `impl/claude/web/src/components/fusion/ProposalCard.tsx`

```typescript
interface ProposalCardProps {
  proposal: Proposal;
  position: 'top' | 'bottom';  // Vertical layout
  isActive?: boolean;
  onClick?: () => void;
}

interface Proposal {
  id: string;
  content: string;
  reasoning?: string;
  principles: string[];
  author: 'kent' | 'claude';
  created_at: string;
}
```

**Styling:**
- Copper (#C08552) for Kent, Sage (#4A6B4A) for Claude
- Breathing animation: subtle scale pulse (1.0 → 1.02 → 1.0, 3s loop)
- Entry animation: grow from seed (0 → 1 scale, 400ms)
- Rounded corners, soft shadow

**Tests:**
- [ ] Renders proposal content
- [ ] Shows correct color for author
- [ ] Breathing animation plays
- [ ] Entry animation on mount
- [ ] Expands reasoning on click

### 3.2 SynthesisOrb Component

**File:** `impl/claude/web/src/components/fusion/SynthesisOrb.tsx`

```typescript
interface SynthesisOrbProps {
  synthesis?: Synthesis;
  status: 'empty' | 'forming' | 'synthesized' | 'vetoed';
  onEdit?: (content: string) => void;
}

interface Synthesis {
  id: string;
  content: string;
  reasoning?: string;
  source_proposals: string[];
  created_at: string;
}
```

**Styling:**
- Empty: subtle dashed border
- Forming: ripple animation, Honey color (#E8C4A0)
- Synthesized: gentle glow pulse, Lantern color (#F5E6D3)
- Vetoed: red flash, then greyed out

**Tests:**
- [ ] Shows placeholder when empty
- [ ] Ripple animation when forming
- [ ] Glow animation when synthesized
- [ ] Flash animation when vetoed
- [ ] Editable content in forming state

### 3.3 ChallengeFlow Component

**File:** `impl/claude/web/src/components/fusion/ChallengeFlow.tsx`

```typescript
interface ChallengeFlowProps {
  challenges: Challenge[];
  onAddChallenge: (challenge: CreateChallengeRequest) => void;
}

interface Challenge {
  id: string;
  from: 'kent' | 'claude';
  to: 'A' | 'B';  // Which proposal is challenged
  content: string;
  created_at: string;
}
```

**Styling:**
- Amber glow (#D4A574) particles
- Flow animation: particles travel along bezier curve
- Challenges appear as cards in the flow

**Tests:**
- [ ] Renders challenge cards
- [ ] Add challenge form works
- [ ] Animation plays on new challenge
- [ ] Shows empty state

### 3.4 AgentBadge Component

**File:** `impl/claude/web/src/components/shared/AgentBadge.tsx`

```typescript
interface AgentBadgeProps {
  agent: 'kent' | 'claude' | 'system';
  size?: 'sm' | 'md' | 'lg';
}

// Kent: 🧑 with Copper background
// Claude: 🤖 with Sage background
// System: ⚙️ with Wood background
```

### Exit Criteria

- [ ] All 4 components render correctly
- [ ] Animations are smooth (60fps)
- [ ] 30+ tests passing
- [ ] TypeScript strict mode passes

---

## Session 4: Dialectical Arena (2-3 hrs)

**Goal:** Compose primitives into the full arena experience with veto.

### 4.1 DialecticalArena Component

**File:** `impl/claude/web/src/components/fusion/DialecticalArena.tsx`

```typescript
interface DialecticalArenaProps {
  fusion: Fusion;
  onChallenge: (challenge: CreateChallengeRequest) => void;
  onSynthesize: (synthesis: string) => void;
  onVeto: (reason: string) => void;
}

interface Fusion {
  id: string;
  proposal_a: Proposal;
  proposal_b: Proposal;
  challenges: Challenge[];
  synthesis?: Synthesis;
  status: 'open' | 'synthesized' | 'vetoed';
}
```

**Layout (Vertical-First):**
```
┌─────────────────────────────────────────────────────────────┐
│                      PROPOSAL A (Kent)                       │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                         ↓                                    │
│                   CHALLENGE FLOW                             │
│                         ↓                                    │
├─────────────────────────────────────────────────────────────┤
│                      PROPOSAL B (Claude)                     │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                         ↓                                    │
│                    SYNTHESIS ORB                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Tests:**
- [ ] Renders all proposals
- [ ] Challenge flow connects proposals
- [ ] Synthesis orb at bottom
- [ ] Status transitions work
- [ ] Responsive layout

### 4.2 VetoButton Component

**File:** `impl/claude/web/src/components/fusion/VetoButton.tsx`

```typescript
interface VetoButtonProps {
  fusionId: string;
  onVeto: (reason: string) => void;
  disabled?: boolean;
}

// Big, red-brown (#8B4513), unmistakable
// Hover: subtle shake animation
// Click: opens VetoConfirmDialog
```

### 4.3 VetoConfirmDialog Component

**File:** `impl/claude/web/src/components/fusion/VetoConfirmDialog.tsx`

```typescript
interface VetoConfirmDialogProps {
  isOpen: boolean;
  onConfirm: (reason: string) => void;
  onCancel: () => void;
}

// CRITICAL UX REQUIREMENT:
// User must type exactly "I feel disgust" to confirm
// Then provide a reason (somatic signal description)
// This is INTENTIONAL FRICTION - do not simplify
```

**Dialog Content:**
```
╔══════════════════════════════════════════════════════════════╗
║                         ⚡ VETO ⚡                             ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  You are about to apply the DISGUST VETO.                    ║
║                                                               ║
║  This is the ethical floor. It cannot be argued away.        ║
║  The synthesis will be rejected.                             ║
║                                                               ║
║  To confirm, type exactly: I feel disgust                    ║
║  [_________________________________]                         ║
║                                                               ║
║  Why? (describe the somatic signal):                         ║
║  [_________________________________]                         ║
║                                                               ║
║              [Cancel]              [Apply Veto]              ║
╚══════════════════════════════════════════════════════════════╝
```

**Tests:**
- [ ] Dialog opens on button click
- [ ] Submit disabled until "I feel disgust" typed exactly
- [ ] Reason field required
- [ ] Thunderclap animation on confirm
- [ ] Calls onVeto with reason

### 4.4 Arena Page

**File:** `impl/claude/web/src/pages/Arena.tsx`

```typescript
// Route: /arena/:fusionId
// Loads fusion data, renders DialecticalArena
// Includes WitnessTrace panel at bottom
```

### 4.5 useFusion Hook

**File:** `impl/claude/web/src/hooks/useFusion.ts`

```typescript
interface UseFusionResult {
  fusion: Fusion | null;
  isLoading: boolean;
  error: Error | null;
  addChallenge: (challenge: CreateChallengeRequest) => Promise<void>;
  synthesize: (content: string) => Promise<void>;
  veto: (reason: string) => Promise<void>;
}

export function useFusion(fusionId: string): UseFusionResult;
```

### Exit Criteria

- [ ] Full arena renders with all components
- [ ] Veto flow works with typed confirmation
- [ ] Marks created for all actions
- [ ] 25+ tests passing
- [ ] Mobile responsive

---

## Session 5: Integration & Polish (2-3 hrs)

**Goal:** Wire everything together, add SSE streaming, mobile polish, teaching mode.

### 5.1 SSE Streaming for Arena

**File:** `impl/claude/web/src/hooks/useFusionStream.ts`

```typescript
// Subscribe to /api/fusion/{id}/stream for real-time updates
// Events: challenge_added, synthesis_updated, veto_applied
// Auto-reconnect on disconnect
```

### 5.2 Teaching Mode Callouts

**File:** `impl/claude/web/src/components/teaching/FusionTeaching.tsx`

```typescript
// Contextual teaching callouts for:
// - Symmetric Supersession explanation
// - What is a mark?
// - How the veto works
// - Why challenges matter

// Shows on first use, dismissible, can be re-enabled in settings
```

### 5.3 Mobile Optimization

**Files:**
- `impl/claude/web/src/components/fusion/ArenaBottomSheet.tsx` — Challenge stream as bottom drawer
- `impl/claude/web/src/components/fusion/MobileArena.tsx` — Mobile-first layout

**Mobile Layout:**
```
╔═════════════════════════════════════╗
║  DIALECTICAL ARENA          ≡       ║
╠═════════════════════════════════════╣
║                                     ║
║   [PROPOSAL A - swipe to expand]    ║
║                 ↕                   ║
║   [PROPOSAL B - swipe to expand]    ║
║                 ↓                   ║
║   [SYNTHESIS ORB]                   ║
║                                     ║
╠═════════════════════════════════════╣
║  [Challenge] [Synthesize]  [⚡VETO] ║
╚═════════════════════════════════════╝
        ▲
        │ Swipe up for Challenge Stream
```

### 5.4 Navigation Integration

**File:** `impl/claude/web/src/App.tsx`

```typescript
// Add routes:
// /witness — Witness Dashboard
// /arena — Arena list (active fusions)
// /arena/:id — Specific fusion arena
```

### 5.5 End-to-End Flow Test

**File:** `impl/claude/web/e2e/fusion.spec.ts`

```typescript
// Full flow test:
// 1. Create mark from witness dashboard
// 2. Navigate to arena
// 3. Add challenge
// 4. Create synthesis
// 5. Verify marks created
// 6. (Optional) Apply veto
```

### Exit Criteria

- [ ] SSE streaming works for arena updates
- [ ] Teaching mode shows on first use
- [ ] Mobile layout works on 375px width
- [ ] E2E test passes
- [ ] 20+ tests passing
- [ ] All TypeScript strict, ESLint clean

---

## API Endpoints Required

Verify these exist or create them:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/witness/marks` | GET | List marks with filters |
| `/api/witness/marks` | POST | Create mark |
| `/api/witness/marks/{id}/retract` | POST | Retract mark |
| `/api/witness/stream` | GET (SSE) | Real-time mark events |
| `/api/fusion` | GET | List active fusions |
| `/api/fusion` | POST | Create fusion |
| `/api/fusion/{id}` | GET | Get fusion details |
| `/api/fusion/{id}/challenge` | POST | Add challenge |
| `/api/fusion/{id}/synthesize` | POST | Set synthesis |
| `/api/fusion/{id}/veto` | POST | Apply veto |
| `/api/fusion/{id}/stream` | GET (SSE) | Real-time fusion events |

---

## Component File Structure

```
impl/claude/web/src/
├── api/
│   ├── witness.ts           # Witness API client
│   └── fusion.ts            # Fusion API client
├── components/
│   ├── witness/
│   │   ├── MarkCard.tsx
│   │   ├── MarkTimeline.tsx
│   │   ├── QuickMarkForm.tsx
│   │   └── MarkFilters.tsx
│   ├── fusion/
│   │   ├── ProposalCard.tsx
│   │   ├── SynthesisOrb.tsx
│   │   ├── ChallengeFlow.tsx
│   │   ├── VetoButton.tsx
│   │   ├── VetoConfirmDialog.tsx
│   │   ├── DialecticalArena.tsx
│   │   ├── ArenaBottomSheet.tsx
│   │   └── MobileArena.tsx
│   ├── shared/
│   │   └── AgentBadge.tsx
│   └── teaching/
│       └── FusionTeaching.tsx
├── hooks/
│   ├── useWitness.ts
│   ├── useMarkStream.ts
│   ├── useFusion.ts
│   └── useFusionStream.ts
├── pages/
│   ├── Witness.tsx
│   └── Arena.tsx
└── styles/
    └── fusion.css           # Living Earth palette, animations
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Time to create mark (Web) | <5 seconds |
| Dialectic completion (happy path) | <5 minutes |
| Veto response time | <1 second (instant feel) |
| Animation smoothness | 60fps |
| Mobile usability | Works on 375px width |
| Test coverage | 120+ tests |
| TypeScript | Strict mode, no errors |
| Kent smiles while using it | Yes |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| Mechanical animations | Organic, breathing animations |
| Simple confirm dialog for veto | Typed "I feel disgust" confirmation |
| Desktop-only design | Mobile-first with progressive enhancement |
| Separate witness and fusion | Integrated—dialectic creates marks |
| Hidden veto button | Prominent, sacred veto |

---

## Verification Commands

```bash
# TypeScript check
cd impl/claude/web && npm run typecheck

# Run tests
cd impl/claude/web && npm test

# E2E tests
cd impl/claude/web && npm run e2e

# Lint
cd impl/claude/web && npm run lint

# Visual check
cd impl/claude/web && npm run dev
# Visit http://localhost:3000/witness and http://localhost:3000/arena
```

---

## Notes for Executing Agent

1. **Read the design spec first:** `plans/witness-fusion-ux-design.md` has the full aesthetic vision
2. **Living Earth palette is non-negotiable:** Copper, Sage, Soil, Wood, Honey, Lantern
3. **Animations must breathe:** No mechanical slides—everything grows, pulses, flows
4. **Veto friction is intentional:** Do NOT simplify the typed confirmation
5. **Mobile-first:** Start with 375px, expand up
6. **Marks are created for everything:** Every action in the arena creates a witness mark

---

*"The arena breathes. The marks accumulate. The synthesis blooms. The veto thunders."*

---

**Filed:** 2025-12-22
**Author:** Claude (for next Claude)
**Voice Anchor:** *"Daring, bold, creative, opinionated but not gaudy"*
