# Constitutional Visualization Components — Integration Guide

## Overview

Frontend components for visualizing constitutional adherence scores in chat UI.

**Components**:
- `ConstitutionalBadge` — Compact badge showing aggregated score (0-100)
- `ConstitutionalRadar` — 7-point radar chart showing all principle scores
- `ConstitutionalExample` — Example usage patterns

**Location**: `impl/claude/web/src/components/chat/`

## Type Definition

```typescript
// Added to impl/claude/web/src/types/chat.ts

export interface PrincipleScore {
  tasteful: number;       // 0-1 range
  curated: number;
  ethical: number;
  joy_inducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}

export interface Turn {
  // ... existing fields
  constitutional_score?: PrincipleScore;  // NEW: Optional constitutional scores
}
```

## Component API

### ConstitutionalBadge

```tsx
import { ConstitutionalBadge } from './components/chat';

<ConstitutionalBadge
  scores={principleScore}
  onClick={() => setShowRadar(true)}
  size="md"  // 'sm' | 'md' | 'lg'
/>
```

**Features**:
- Aggregates 7 scores into single 0-100 value
- Color codes: green (>80), yellow (50-80), red (<50)
- Click expands to show radar view
- Brutalist design (minimal, non-intrusive)

### ConstitutionalRadar

```tsx
import { ConstitutionalRadar } from './components/chat';

<ConstitutionalRadar
  scores={principleScore}
  size="md"
  showLabels={true}
/>
```

**Features**:
- 7-point heptagonal radar chart
- Pure SVG (no dependencies)
- Shows all principles with individual color coding
- Includes legend with numeric scores

## Integration Steps

### 1. Backend: Add Scoring to Turn Response

**File**: `impl/claude/protocols/api/chat.py` (or equivalent)

```python
from services.categorical.constitution import evaluate_turn_constitutional

# In turn completion handler
constitutional_score = evaluate_turn_constitutional(
    turn_content=turn.assistant_response.content,
    tools_used=turn.tools_used,
    context=session_context
)

turn_response = {
    # ... existing fields
    "constitutional_score": constitutional_score.to_dict() if constitutional_score else None
}
```

### 2. Frontend: Add to AssistantMessage

**File**: `impl/claude/web/src/components/chat/AssistantMessage.tsx`

```tsx
import { ConstitutionalBadge } from './ConstitutionalBadge';
import { ConstitutionalRadar } from './ConstitutionalRadar';

export function AssistantMessage({ turn, ... }: AssistantMessageProps) {
  const [showRadar, setShowRadar] = useState(false);

  return (
    <div className="assistant-message">
      {/* Header with indicators */}
      <div className="assistant-message__header">
        <ConfidenceIndicator ... />

        {/* NEW: Constitutional badge */}
        {turn.constitutional_score && (
          <ConstitutionalBadge
            scores={turn.constitutional_score}
            onClick={() => setShowRadar(!showRadar)}
            size="sm"
          />
        )}
      </div>

      {/* Message content */}
      <div className="assistant-message__content">
        {turn.assistant_response.content}
      </div>

      {/* Expanded radar */}
      {showRadar && turn.constitutional_score && (
        <div className="assistant-message__radar">
          <ConstitutionalRadar
            scores={turn.constitutional_score}
            size="md"
            showLabels={true}
          />
        </div>
      )}
    </div>
  );
}
```

### 3. CSS: Add Layout Styles

**File**: `impl/claude/web/src/components/chat/AssistantMessage.css`

```css
/* Header with indicators */
.assistant-message__header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

/* Radar expansion */
.assistant-message__radar {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--brutalist-border, #333);
}
```

### 4. Optional: Session-Level Aggregation

**File**: `impl/claude/web/src/components/chat/ChatPanel.tsx`

```tsx
import { aggregateConstitutionalScores } from './ConstitutionalExample';

export function ChatPanel({ session, ... }: ChatPanelProps) {
  const sessionScores = aggregateConstitutionalScores(session.turns);

  return (
    <div className="chat-panel">
      {/* Context indicator with session health */}
      {sessionScores && (
        <div className="chat-panel__constitutional">
          <ConstitutionalBadge
            scores={sessionScores}
            onClick={() => setShowSessionRadar(true)}
            size="md"
          />
        </div>
      )}

      {/* ... rest of chat UI */}
    </div>
  );
}
```

## Design Principles

### Brutalist Aesthetic
- No rounded corners
- No gradients or glows
- Monospace font (Berkeley Mono / JetBrains Mono)
- Minimal color (grayscale + subtle highlights)
- Text-based differentiation

### Color Coding (Subtle)
```css
--brutalist-success: #fff      /* High (>80) */
--brutalist-warning: #ccc      /* Medium (50-80) */
--brutalist-error: #999        /* Low (<50) */
```

### Responsive Sizing
- Small: 120px radar, 10px font
- Medium: 180px radar, 11px font
- Large: 240px radar, 12px font

### Accessibility
- ARIA labels on all interactive elements
- Keyboard navigation support
- Focus indicators
- Color is not sole differentiator (uses text values)

## Backend Implementation Notes

### Constitutional Scoring Service

**File**: `impl/claude/services/categorical/constitution.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class PrincipleScore:
    tasteful: float
    curated: float
    ethical: float
    joy_inducing: float
    composable: float
    heterarchical: float
    generative: float

    def to_dict(self) -> dict:
        return {
            "tasteful": self.tasteful,
            "curated": self.curated,
            "ethical": self.ethical,
            "joy_inducing": self.joy_inducing,
            "composable": self.composable,
            "heterarchical": self.heterarchical,
            "generative": self.generative,
        }

def evaluate_turn_constitutional(
    turn_content: str,
    tools_used: list,
    context: dict
) -> Optional[PrincipleScore]:
    """
    Evaluate turn adherence to 7 constitutional principles.

    Returns PrincipleScore with values 0-1 for each principle.
    Returns None if scoring not applicable for this turn.
    """
    # TODO: Implement scoring logic
    # - Analyze content for principle adherence
    # - Consider tools used (composability, ethical checks)
    # - Weight by context (some turns more critical than others)

    pass
```

### Scoring Strategy

**Principle Definitions**:
1. **Tasteful**: Clear, well-structured, appropriate abstraction
2. **Curated**: Intentional choices, no bloat
3. **Ethical**: Transparency, user autonomy, safety
4. **Joy-Inducing**: Delightful interaction, positive UX
5. **Composable**: Modular, reusable, well-factored
6. **Heterarchical**: Flexible organization, no rigid hierarchy
7. **Generative**: Creates new possibilities, enables growth

**Scoring Approaches**:
- Rule-based heuristics (fast, deterministic)
- LLM-based evaluation (slower, more nuanced)
- Hybrid: heuristics for common cases, LLM for edge cases

## Testing Checklist

- [ ] TypeScript compilation passes
- [ ] ESLint passes (no warnings in Constitutional files)
- [ ] Badge renders with high/medium/low scores
- [ ] Radar chart renders correctly (heptagon)
- [ ] Badge click toggles radar view
- [ ] Responsive sizing (sm/md/lg) works
- [ ] Graceful degradation when scores missing
- [ ] Keyboard navigation works
- [ ] ARIA labels present and accurate
- [ ] Session aggregation calculates correctly
- [ ] Backend returns constitutional_score in Turn
- [ ] Integration with AssistantMessage header

## Files Created

```
impl/claude/web/src/
  types/chat.ts                                  # MODIFIED: Added PrincipleScore, updated Turn
  components/chat/
    ConstitutionalBadge.tsx                     # NEW: Compact badge component
    ConstitutionalBadge.css                     # NEW: Brutalist styles
    ConstitutionalRadar.tsx                     # NEW: Radar chart component
    ConstitutionalRadar.css                     # NEW: Radar styles
    ConstitutionalExample.tsx                   # NEW: Example usage patterns
    CONSTITUTIONAL_INTEGRATION.md               # NEW: This file
    index.ts                                     # MODIFIED: Export new components
```

## Next Steps

1. **Backend**: Implement constitutional scoring in `services/categorical/constitution.py`
2. **API**: Add `constitutional_score` to Turn response
3. **Integration**: Add components to AssistantMessage
4. **Testing**: Test with real chat sessions
5. **Iteration**: Refine scoring based on user feedback

---

**Design Philosophy**: *"The radar is a mirror. It shows not what we built, but what we aspired to build."*
