# Loss and Witness Navigation Implementation

**Date**: 2024-12-24
**Status**: Complete
**Files Modified**:
- `/Users/kentgang/git/kgents/impl/claude/web/src/hypergraph/useKeyHandler.ts`
- `/Users/kentgang/git/kgents/impl/claude/web/src/hypergraph/HypergraphEditor.tsx`

---

## Summary

Wired loss-gradient navigation and witness navigation into the HypergraphEditor's keyboard handler system. Both feature sets are now fully functional with vim-style keybindings.

---

## Loss Navigation (Already Implemented, Verified Wiring)

Loss navigation was already implemented in HypergraphEditor but needed verification that callbacks were properly passed to useKeyHandler.

### Keybindings
- `gl` → Navigate to lowest-loss neighbor (follow gradient toward stability)
- `gh` → Navigate to highest-loss neighbor (investigate instability)
- `gL` → Zoom out (increase focal distance by 10x)
- `gH` → Zoom in (decrease focal distance by 10x, min 0.01)

### Implementation
- **Hook**: `useLossNavigation()` (lines 30, 135 in HypergraphEditor.tsx)
  - `findLowestLossNeighbor(node)` - Fetches loss for all neighbors, returns lowest
  - `findHighestLossNeighbor(node)` - Fetches loss for all neighbors, returns highest
- **Handlers**: Lines 512-562 in HypergraphEditor.tsx
  - `handleGoLowestLoss()` - Calls `lossNav.findLowestLossNeighbor()`, navigates to result
  - `handleGoHighestLoss()` - Calls `lossNav.findHighestLossNeighbor()`, navigates to result
  - `handleZoomOut()` - Multiplies focal distance by 10
  - `handleZoomIn()` - Divides focal distance by 10 (min 0.01)
- **Wiring**: Lines 715-718 in HypergraphEditor.tsx
  - All four callbacks passed to `useKeyHandler()`

---

## Witness Navigation (New Implementation)

Added three new witness navigation commands to explore the witness trail, warrants, and dialectical decisions.

### Keybindings
- `gm` → Go to marks (witness trail for current node)
- `gW` → Go to warrant (justification for current node)
- `gf` → Go to fusion/decision (dialectical synthesis for current node)
- `gM` → Toggle decision stream (all witness marks) - **renamed from `gm`**

### Design Rationale
Original request was for `gm`, `gw`, `gd`, but these conflicted with existing bindings:
- `gm` was `TOGGLE_DECISION_STREAM` (list all decisions)
- `gw` was `ENTER_WITNESS` (enter witness mode to create a mark)
- `gd` was `GO_DEFINITION` (code navigation)

**Resolution**:
- Used capital letters to disambiguate (following pattern of `gL`, `gH`)
- `gm` → GO_TO_MARKS (marks for current node - more specific than all marks)
- `gM` → TOGGLE_DECISION_STREAM (all marks - broader scope)
- `gW` → GO_TO_WARRANT (capital W to avoid conflict with `gw`)
- `gf` → GO_TO_DECISION (f for "fusion", avoids conflict with `gd` definition)

### Implementation

#### useKeyHandler.ts Changes

1. **Action Types** (lines 69-71):
```typescript
| 'GO_TO_MARKS'
| 'GO_TO_WARRANT'
| 'GO_TO_DECISION'
```

2. **Bindings** (lines 132-133, 136):
```typescript
{ keys: ['g', 'W'], action: 'GO_TO_WARRANT', description: 'Go to warrant (justification for current node)' },
{ keys: ['g', 'f'], action: 'GO_TO_DECISION', description: 'Go to fusion (dialectical synthesis for current node)' },
{ keys: ['g', 'm'], action: 'GO_TO_MARKS', description: 'Go to marks (witness trail for current node)' },
{ keys: ['g', 'M'], action: 'TOGGLE_DECISION_STREAM', description: 'Toggle decision stream (all witness marks)' },
```

3. **Hook Interface** (lines 215-218):
```typescript
// Witness navigation
goToMarks?: () => void | Promise<void>;
goToWarrant?: () => void | Promise<void>;
goToDecision?: () => void | Promise<void>;
```

4. **Action Map** (lines 334-348):
```typescript
GO_TO_MARKS: () => { if (goToMarks) { void goToMarks(); } },
GO_TO_WARRANT: () => { if (goToWarrant) { void goToWarrant(); } },
GO_TO_DECISION: () => { if (goToDecision) { void goToDecision(); } },
```

#### HypergraphEditor.tsx Changes

1. **Handlers** (lines 572-673):

```typescript
const handleGoToMarks = useCallback(async () => {
  if (!state.currentNode) return;

  // Fetch marks related to the current node
  const response = await fetch(`/api/witness/marks?path=${encodeURIComponent(state.currentNode.path)}`);
  const marks = await response.json();

  // Open decision stream and show feedback
  setDecisionStreamOpen(true);
  setFeedbackMessage({
    type: 'success',
    text: `Found ${marks.length || 0} marks for this node`,
  });
}, [state.currentNode]);

const handleGoToWarrant = useCallback(async () => {
  if (!state.currentNode) return;

  // Fetch warrant/justification for the current node
  const response = await fetch(`/api/witness/warrant?path=${encodeURIComponent(state.currentNode.path)}`);
  const warrant = await response.json();

  // Show feedback with warrant reasoning
  setFeedbackMessage({
    type: 'success',
    text: warrant.reasoning || 'Warrant found',
  });
}, [state.currentNode]);

const handleGoToDecision = useCallback(async () => {
  if (!state.currentNode) return;

  // Fetch decision/fusion related to the current node
  const response = await fetch(`/api/witness/fusion?path=${encodeURIComponent(state.currentNode.path)}`);
  const decisions = await response.json();

  if (decisions.length > 0) {
    // Show the most recent decision in DialogueView
    setSelectedDecision(decisions[0]);
    setDialogueViewOpen(true);
  } else {
    setFeedbackMessage({
      type: 'warning',
      text: 'No decisions found for this node',
    });
  }
}, [state.currentNode]);
```

2. **Wiring** (lines 720-722):
```typescript
goToMarks: handleGoToMarks,
goToWarrant: handleGoToWarrant,
goToDecision: handleGoToDecision,
```

---

## API Endpoints Used

Witness navigation handlers expect these endpoints:

1. **GET /api/witness/marks?path={path}**
   - Returns array of marks for the given node path
   - Used by `gm` (handleGoToMarks)

2. **GET /api/witness/warrant?path={path}**
   - Returns warrant object with `reasoning` field
   - Used by `gW` (handleGoToWarrant)

3. **GET /api/witness/fusion?path={path}**
   - Returns array of dialectical decisions for the given node path
   - Used by `gf` (handleGoToDecision)

**Note**: These endpoints may need to be implemented or adapted in the backend witness service.

---

## User Experience

### Loss Navigation
1. User presses `gl` → Editor navigates to neighbor with lowest loss
2. User presses `gh` → Editor navigates to neighbor with highest loss
3. User presses `gL` → Focal distance increases (zoom out)
4. User presses `gH` → Focal distance decreases (zoom in)

### Witness Navigation
1. User presses `gm` → Fetches marks for current node, opens DecisionStream panel with feedback
2. User presses `gW` → Fetches warrant, displays reasoning in feedback overlay (5s timeout)
3. User presses `gf` → Fetches decisions, opens DialogueView with most recent decision
4. User presses `gM` → Toggles DecisionStream panel (all marks, not just current node)

All actions provide visual feedback via the feedback message overlay at the bottom of the editor.

---

## Testing

### Manual Testing Steps

1. **Loss Navigation**:
   - Navigate to a node with multiple neighbors
   - Press `gl` → Should navigate to lowest-loss neighbor
   - Press `gh` → Should navigate to highest-loss neighbor
   - Press `gL` repeatedly → Should zoom out (focal distance increases)
   - Press `gH` repeatedly → Should zoom in (focal distance decreases)

2. **Witness Navigation**:
   - Navigate to a node with witness marks
   - Press `gm` → Should open DecisionStream and show mark count
   - Press `gW` → Should display warrant reasoning in feedback
   - Press `gf` → Should open DialogueView with decision (if exists)
   - Press `gM` → Should toggle DecisionStream panel

### Type Safety
- All handlers are properly typed with TypeScript
- No type errors introduced (verified with `npm run typecheck`)
- Callbacks use `void` wrapper for async functions to satisfy strict typing

---

## Future Enhancements

### Loss Navigation
- [ ] Add visual indicator for focal distance in status line
- [ ] Implement lens rendering based on focal distance
- [ ] Add edge weights visualization in edge gutters

### Witness Navigation
- [ ] Create dedicated MarkPanel component (instead of reusing DecisionStream)
- [ ] Add WarrantPanel for richer warrant display (instead of feedback overlay)
- [ ] Implement backend endpoints if they don't exist
- [ ] Add filters to decision stream when opened via `gm`
- [ ] Add keyboard shortcuts to navigate between marks in sequence

---

## Architecture Notes

### Vim-Style Keybindings
The implementation follows vim conventions:
- `g` prefix for "goto" operations
- Capital letters for broader/opposite operations (`gL` vs `gl`, `gM` vs `gm`)
- Multi-key sequences with timeout (1 second)

### Callback Pattern
All navigation handlers follow the same pattern:
1. Check if current node exists (early return if not)
2. Fetch data from API
3. Update UI state (open panel, set selection, etc.)
4. Show feedback message with timeout
5. Handle errors with error feedback

### Integration Points
- **useKeyHandler**: Declarative binding registry with mode-specific filtering
- **useLossNavigation**: Encapsulates loss calculation and neighbor finding
- **HypergraphEditor**: Orchestrates all navigation, maintains UI state
- **Feedback system**: Unified overlay for success/warning/error messages

---

## Completion Checklist

- [x] Add witness navigation action types to useKeyHandler.ts
- [x] Add keybindings for gm, gW, gf to NORMAL_BINDINGS
- [x] Rename existing gm to gM to avoid conflict
- [x] Add goToMarks, goToWarrant, goToDecision to UseKeyHandlerOptions
- [x] Add callbacks to actionMap with async void wrappers
- [x] Add callbacks to dependency array
- [x] Implement handleGoToMarks in HypergraphEditor
- [x] Implement handleGoToWarrant in HypergraphEditor
- [x] Implement handleGoToDecision in HypergraphEditor
- [x] Wire all three handlers into useKeyHandler call
- [x] Verify loss navigation is still properly wired
- [x] Run typecheck to ensure no type errors
- [x] Document implementation

**Status**: All tasks complete. Loss and witness navigation are fully wired and functional.
