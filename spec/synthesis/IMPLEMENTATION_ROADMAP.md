# Implementation Roadmap: Witness Architecture

> *From theory to code in 6 phases.*

---

## Phase 0: Verify Current State (1 session)

Before building, verify what exists:

```bash
# Backend health
cd impl/claude
uv run pytest -q  # Should pass

# Frontend health
cd impl/claude/web
npm run typecheck && npm run lint  # Should pass

# Categorical laws
kg probe health --all  # Should show green
```

**Checklist**:
- [ ] All 678+ witness tests passing
- [ ] 92 validation tests passing
- [ ] 41 categorical probe tests passing
- [ ] Frontend typecheck clean

---

## Phase 1: Unify Mark Types (2 sessions)

Currently we have multiple mark types:
- `Mark` (generic)
- `ChatMark` (chat-specific)
- `WitnessMark` (witness-specific)

**Goal**: Single `Mark` type with domain-specific extensions.

### Task 1.1: Define Core Mark Schema

```python
# services/witness/mark.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

@dataclass(frozen=True)
class Mark:
    """The atomic unit of justification."""

    # Core fields (all marks have these)
    id: str
    action: str
    reasoning: str
    principles: tuple[str, ...]
    timestamp: datetime

    # Optional extensions
    layer: Literal[1, 2, 3, 4, 5, 6, 7] | None = None
    confidence: float = 1.0
    evidence: dict = field(default_factory=dict)
    parent_id: str | None = None

    # Domain-specific (use None for non-applicable)
    constitutional_scores: "PrincipleScore | None" = None  # Chat
    portal_state: "PortalState | None" = None  # Navigation
    node_path: str | None = None  # Hypergraph
```

### Task 1.2: Update ChatMark to Use Core Mark

```python
# services/chat/witness.py

@dataclass(frozen=True)
class ChatMark(Mark):
    """Chat-specific mark with turn metadata."""

    session_id: str = ""
    turn_number: int = 0
    user_message: str = ""
    assistant_response: str = ""
    tools_used: tuple[str, ...] = ()
```

### Task 1.3: Update Trace to Be Generic

```python
# services/witness/trace.py

from typing import TypeVar, Generic

M = TypeVar("M", bound=Mark)

@dataclass(frozen=True)
class Trace(Generic[M]):
    """Immutable, append-only sequence of marks."""

    marks: tuple[M, ...] = ()

    def add(self, mark: M) -> "Trace[M]":
        return Trace(marks=self.marks + (mark,))

    def filter(self, predicate: Callable[[M], bool]) -> "Trace[M]":
        return Trace(marks=tuple(m for m in self.marks if predicate(m)))
```

**Files to modify**:
- `services/witness/mark.py` (new)
- `services/witness/trace.py` (new)
- `services/chat/witness.py` (update ChatMark)
- `services/chat/session.py` (update to use Trace[ChatMark])

**Tests**:
- [ ] Mark immutability
- [ ] Trace immutable append
- [ ] ChatMark backward compatibility
- [ ] Generic Trace with different mark types

---

## Phase 2: Wire Portal Witnessing (2 sessions)

Currently portals expand/collapse without creating marks.

**Goal**: Every portal state change creates a mark.

### Task 2.1: Add Portal State to Mark

```typescript
// web/src/components/tokens/types.ts

export interface PortalMark extends Mark {
  portal_id: string;
  edge_type: string;
  destination: string;
  old_state: PortalState;
  new_state: PortalState;
}
```

### Task 2.2: Create Witness Hook for Portals

```typescript
// web/src/hooks/usePortalWitness.ts

import { useCallback } from 'react';
import { PortalMark, PortalState } from '../types';

export function usePortalWitness() {
  const witnessTransition = useCallback(
    async (
      portalId: string,
      oldState: PortalState,
      newState: PortalState,
      reasoning: string
    ) => {
      const mark: PortalMark = {
        id: crypto.randomUUID(),
        action: `portal_${newState.toLowerCase()}`,
        reasoning,
        principles: ['composable', 'joy_inducing'],
        timestamp: new Date(),
        portal_id: portalId,
        old_state: oldState,
        new_state: newState,
      };

      await fetch('/api/witness/marks', {
        method: 'POST',
        body: JSON.stringify(mark),
      });

      return mark;
    },
    []
  );

  return { witnessTransition };
}
```

### Task 2.3: Integrate into PortalToken

```typescript
// web/src/components/tokens/PortalToken.tsx

const { witnessTransition } = usePortalWitness();

const handleExpand = async () => {
  const oldState = portalState;
  setPortalState(PortalState.LOADING);

  // Fetch content...
  const content = await fetchPortalContent(destination);

  setPortalState(PortalState.EXPANDED);

  // Witness the transition
  await witnessTransition(
    portalId,
    oldState,
    PortalState.EXPANDED,
    `User expanded portal to view ${destination}`
  );
};
```

**Files to modify**:
- `web/src/components/tokens/types.ts`
- `web/src/hooks/usePortalWitness.ts` (new)
- `web/src/components/tokens/PortalToken.tsx`

**Tests**:
- [ ] Portal expand creates mark
- [ ] Portal collapse creates mark
- [ ] Marks appear in witness stream
- [ ] Portal marks have correct principles

---

## Phase 3: Wire Hypergraph Navigation Witnessing (2 sessions)

Currently navigation in the hypergraph editor doesn't create marks.

**Goal**: Every significant navigation creates a mark.

### Task 3.1: Define Navigation Marks

```typescript
// web/src/hypergraph/types/navigation-mark.ts

export interface NavigationMark extends Mark {
  from_path: string | null;
  to_path: string;
  navigation_type: 'derivation' | 'loss_gradient' | 'sibling' | 'direct';
  key_sequence: string;  // e.g., "gD", "gl", "j"
}
```

### Task 3.2: Create Navigation Witness Hook

```typescript
// web/src/hypergraph/useNavigationWitness.ts

export function useNavigationWitness() {
  const witnessNavigation = useCallback(
    async (
      fromPath: string | null,
      toPath: string,
      navType: NavigationType,
      keySequence: string
    ) => {
      const principles = getPrinciplesForNavType(navType);

      const mark: NavigationMark = {
        id: crypto.randomUUID(),
        action: `navigate_${navType}`,
        reasoning: `Navigated via ${keySequence}`,
        principles,
        timestamp: new Date(),
        from_path: fromPath,
        to_path: toPath,
        navigation_type: navType,
        key_sequence: keySequence,
      };

      await fetch('/api/witness/marks', {
        method: 'POST',
        body: JSON.stringify(mark),
      });

      return mark;
    },
    []
  );

  return { witnessNavigation };
}

function getPrinciplesForNavType(navType: NavigationType): string[] {
  switch (navType) {
    case 'derivation': return ['generative'];  // Following proof chains
    case 'loss_gradient': return ['ethical'];  // Seeking truth
    case 'sibling': return ['composable'];     // Exploring related
    case 'direct': return ['tasteful'];        // Intentional jump
  }
}
```

### Task 3.3: Integrate into useNavigation

```typescript
// web/src/hypergraph/useNavigation.ts

const { witnessNavigation } = useNavigationWitness();

const navigateToNode = useCallback(async (path: string, keySequence: string) => {
  const fromPath = state.currentNode?.path ?? null;

  // Perform navigation
  dispatch({ type: 'NAVIGATE', payload: { path } });

  // Witness it
  await witnessNavigation(
    fromPath,
    path,
    determineNavType(keySequence),
    keySequence
  );
}, [state.currentNode, witnessNavigation]);
```

**Files to modify**:
- `web/src/hypergraph/types/navigation-mark.ts` (new)
- `web/src/hypergraph/useNavigationWitness.ts` (new)
- `web/src/hypergraph/useNavigation.ts`
- `web/src/hypergraph/useKeyHandler.ts`

**Tests**:
- [ ] gD creates derivation mark
- [ ] gl/gh creates loss_gradient mark
- [ ] j/k creates sibling mark
- [ ] Direct path entry creates direct mark

---

## Phase 4: Constitutional Scoring Everywhere (2 sessions)

Currently only chat has constitutional scoring.

**Goal**: Apply constitutional reward to all mark types.

### Task 4.1: Generalize Constitutional Reward

```python
# services/constitutional/reward.py (new location, generalized)

def constitutional_reward(
    action: str,
    context: dict[str, Any],
    domain: Literal["chat", "navigation", "portal", "edit"]
) -> PrincipleScore:
    """
    Compute constitutional scores for any action.

    Domain-specific rules:
    - chat: Tool count, response length, mutations
    - navigation: Derivation depth, loss gradient following
    - portal: Expansion depth, destination reachability
    - edit: Change size, spec alignment
    """
    scores = {
        Principle.TASTEFUL: 1.0,
        Principle.CURATED: 1.0,
        Principle.ETHICAL: 1.0,
        Principle.JOY_INDUCING: 1.0,
        Principle.COMPOSABLE: 1.0,
        Principle.HETERARCHICAL: 1.0,
        Principle.GENERATIVE: 1.0,
    }

    if domain == "chat":
        scores = _apply_chat_rules(scores, context)
    elif domain == "navigation":
        scores = _apply_navigation_rules(scores, context)
    elif domain == "portal":
        scores = _apply_portal_rules(scores, context)
    elif domain == "edit":
        scores = _apply_edit_rules(scores, context)

    return PrincipleScore(**scores)


def _apply_navigation_rules(scores: dict, context: dict) -> dict:
    """Navigation-specific scoring."""

    # GENERATIVE: Following derivation chains is generative
    if context.get("navigation_type") == "derivation":
        scores[Principle.GENERATIVE] = 1.0
    else:
        scores[Principle.GENERATIVE] = 0.8

    # COMPOSABLE: Direct jumps break composition flow
    if context.get("navigation_type") == "direct":
        scores[Principle.COMPOSABLE] = 0.9

    # ETHICAL: Loss gradient navigation seeks truth
    if context.get("navigation_type") == "loss_gradient":
        scores[Principle.ETHICAL] = 1.0

    return scores
```

### Task 4.2: Apply Scores to All Marks

```python
# services/witness/mark.py

def create_mark(
    action: str,
    reasoning: str,
    principles: list[str],
    domain: Literal["chat", "navigation", "portal", "edit"],
    context: dict[str, Any],
    **kwargs
) -> Mark:
    """Factory function that computes constitutional scores."""

    constitutional_scores = constitutional_reward(action, context, domain)

    return Mark(
        id=str(uuid4()),
        action=action,
        reasoning=reasoning,
        principles=tuple(principles),
        timestamp=datetime.now(),
        constitutional_scores=constitutional_scores,
        **kwargs
    )
```

**Files to modify**:
- `services/constitutional/reward.py` (move from chat, generalize)
- `services/witness/mark.py` (add factory function)
- Update all mark creation sites

**Tests**:
- [ ] Navigation marks get scores
- [ ] Portal marks get scores
- [ ] Edit marks get scores
- [ ] Domain-specific rules apply correctly

---

## Phase 5: Crystal Compression (3 sessions)

Marks accumulate. Crystals compress them.

**Goal**: Implement SESSION → DAY → WEEK → EPOCH crystallization.

### Task 5.1: Define Crystal Schema

```python
# services/witness/crystal.py

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

@dataclass
class Crystal:
    """Compressed insight from marks."""

    id: str
    level: Literal["SESSION", "DAY", "WEEK", "EPOCH"]

    # The insight
    insight: str           # What we learned
    significance: str      # Why it matters

    # Source tracking
    source_mark_ids: list[str]
    source_crystal_ids: list[str]  # For higher-level crystals

    # Metadata
    confidence: float
    principles: list[str]  # Which principles this crystal embodies
    topics: list[str]      # Semantic tags

    # Mood (the vibe)
    mood: MoodVector

    # Temporal
    crystallized_at: datetime
    period_start: datetime
    period_end: datetime


@dataclass
class MoodVector:
    """7D emotional/aesthetic vector."""

    warmth: float      # -1 (cold) to 1 (warm)
    weight: float      # -1 (light) to 1 (heavy)
    tempo: float       # -1 (slow) to 1 (fast)
    texture: float     # -1 (smooth) to 1 (rough)
    brightness: float  # -1 (dark) to 1 (bright)
    saturation: float  # -1 (muted) to 1 (vivid)
    complexity: float  # -1 (simple) to 1 (complex)
```

### Task 5.2: Implement Crystallization Service

```python
# services/witness/crystallization.py

class CrystallizationService:
    """Compress marks into crystals."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def crystallize_session(
        self,
        marks: list[Mark],
        session_id: str
    ) -> Crystal:
        """Compress session marks into SESSION crystal."""

        # Extract key actions and reasonings
        actions = [m.action for m in marks]
        reasonings = [m.reasoning for m in marks]

        # Use LLM to synthesize insight
        prompt = f"""
        Given these actions and reasonings from a session:

        Actions: {actions}
        Reasonings: {reasonings}

        Synthesize into:
        1. One sentence insight (what was learned)
        2. One sentence significance (why it matters)
        3. Mood vector (7 floats from -1 to 1)
        4. Key topics (3-5 tags)

        Format as JSON.
        """

        synthesis = await self.llm.generate(prompt)
        data = json.loads(synthesis)

        return Crystal(
            id=str(uuid4()),
            level="SESSION",
            insight=data["insight"],
            significance=data["significance"],
            source_mark_ids=[m.id for m in marks],
            source_crystal_ids=[],
            confidence=self._compute_confidence(marks),
            principles=self._extract_principles(marks),
            topics=data["topics"],
            mood=MoodVector(**data["mood"]),
            crystallized_at=datetime.now(),
            period_start=min(m.timestamp for m in marks),
            period_end=max(m.timestamp for m in marks),
        )

    async def crystallize_day(
        self,
        session_crystals: list[Crystal]
    ) -> Crystal:
        """Compress SESSION crystals into DAY crystal."""
        # Similar pattern, but source is crystals not marks
        ...

    async def crystallize_week(
        self,
        day_crystals: list[Crystal]
    ) -> Crystal:
        """Compress DAY crystals into WEEK crystal."""
        ...

    async def crystallize_epoch(
        self,
        week_crystals: list[Crystal]
    ) -> Crystal:
        """Compress WEEK crystals into EPOCH crystal."""
        ...
```

### Task 5.3: Add /crystallize Command

```python
# protocols/cli/commands/crystallize.py

@app.command()
async def crystallize(
    level: str = typer.Argument("session"),
    force: bool = typer.Option(False, "--force", "-f"),
):
    """Compress current marks into a crystal."""

    service = CrystallizationService(get_llm())

    if level == "session":
        marks = await get_session_marks()
        crystal = await service.crystallize_session(marks, session_id())
    elif level == "day":
        crystals = await get_today_session_crystals()
        crystal = await service.crystallize_day(crystals)
    # etc.

    await store_crystal(crystal)

    print(f"✨ Crystallized {len(marks)} marks into: {crystal.insight}")
```

**Files to create**:
- `services/witness/crystal.py`
- `services/witness/crystallization.py`
- `protocols/cli/commands/crystallize.py`

**Tests**:
- [ ] SESSION crystallization works
- [ ] DAY crystallization compresses sessions
- [ ] WEEK crystallization compresses days
- [ ] EPOCH crystallization compresses weeks
- [ ] Mood vectors are reasonable
- [ ] Confidence propagates correctly

---

## Phase 6: Visual Integration (3 sessions)

The witness architecture should be visible.

### Task 6.1: Trail Component (Derivation Breadcrumb)

```typescript
// web/src/primitives/Trail/Trail.tsx

interface TrailProps {
  marks: Mark[];
  crystals: Crystal[];
  currentPosition: number;
  onNavigate: (position: number) => void;
}

export function Trail({ marks, crystals, currentPosition, onNavigate }: TrailProps) {
  const compressionRatio = marks.length > 0
    ? crystals.length / marks.length
    : 0;

  return (
    <div className="trail">
      <div className="trail-breadcrumb">
        {marks.slice(-10).map((mark, i) => (
          <TrailNode
            key={mark.id}
            mark={mark}
            isCurrent={i === currentPosition}
            onClick={() => onNavigate(i)}
          />
        ))}
      </div>

      <div className="trail-compression">
        Compression: {compressionRatio.toFixed(2)}
      </div>

      <div className="trail-principles">
        {/* Show principle scores as mini-bars */}
        <PrincipleBar principle="ethical" score={avgScore(marks, 'ethical')} />
        <PrincipleBar principle="composable" score={avgScore(marks, 'composable')} />
        <PrincipleBar principle="joy_inducing" score={avgScore(marks, 'joy_inducing')} />
      </div>
    </div>
  );
}
```

### Task 6.2: ValueCompass (Constitutional Radar)

Already implemented in Phase 1-2 of Frontend Renaissance. Verify integration.

### Task 6.3: Crystal Hierarchy Visualization

```typescript
// web/src/components/CrystalHierarchy.tsx

interface CrystalHierarchyProps {
  crystals: Crystal[];
  level: CrystalLevel;
  onExpand: (crystalId: string) => void;
}

export function CrystalHierarchy({ crystals, level, onExpand }: CrystalHierarchyProps) {
  return (
    <div className={`crystal-hierarchy crystal-hierarchy--${level.toLowerCase()}`}>
      {crystals.map(crystal => (
        <CrystalNode
          key={crystal.id}
          crystal={crystal}
          onClick={() => onExpand(crystal.id)}
        >
          <MoodIndicator mood={crystal.mood} />
          <ConfidenceBadge confidence={crystal.confidence} />
          <InsightPreview text={crystal.insight} />
        </CrystalNode>
      ))}
    </div>
  );
}
```

**Files to create/modify**:
- `web/src/primitives/Trail/Trail.tsx`
- `web/src/primitives/Trail/TrailNode.tsx`
- `web/src/primitives/Trail/PrincipleBar.tsx`
- `web/src/components/CrystalHierarchy.tsx`
- `web/src/components/CrystalNode.tsx`
- `web/src/components/MoodIndicator.tsx`

**Tests**:
- [ ] Trail shows last N marks
- [ ] Trail shows compression ratio
- [ ] ValueCompass updates with new marks
- [ ] Crystal hierarchy expands correctly

---

## Verification Checklist

At the end of all phases:

```bash
# Backend
cd impl/claude
uv run pytest -q                    # All tests pass
uv run mypy .                       # No type errors
kg probe health --all               # Laws verified

# Frontend
cd impl/claude/web
npm run typecheck                   # No type errors
npm run lint                        # No lint errors
npm run test                        # All tests pass

# Integration
kg witness show --today             # Marks visible
kg constitutional --session current # Scores computed
/crystallize                        # Crystal created

# Manual verification
- [ ] Portal expand creates mark
- [ ] Navigation creates mark
- [ ] Chat turn creates mark with scores
- [ ] Trail shows derivation breadcrumb
- [ ] ValueCompass shows principle radar
- [ ] Crystals compress marks
```

---

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 0. Verify | 1 session | Baseline confirmed |
| 1. Unify Marks | 2 sessions | Single Mark type |
| 2. Portal Witnessing | 2 sessions | Portal marks |
| 3. Navigation Witnessing | 2 sessions | Navigation marks |
| 4. Constitutional Everywhere | 2 sessions | Universal scoring |
| 5. Crystal Compression | 3 sessions | Crystallization service |
| 6. Visual Integration | 3 sessions | Trail + Crystal UI |
| **Total** | **15 sessions** | **Witness Architecture** |

---

*"The proof IS the decision. The mark IS the witness."*
