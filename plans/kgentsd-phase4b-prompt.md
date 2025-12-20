# Phase 4B: Reactive Workflows

> *Continuing from Phase 4A (kgentsd visible presence complete)*

## The Gap

Phase 4A gave the Witness a voice. But it's still passive—it observes and reports, but doesn't *react*. The "aha" moment is missing:

```
Tests fail. Within 3 seconds:
┌─ witness ─────────────────────────────────────────────────────┐
│ 14:42 🔴 Test failed: test_auth_flow_redirect                 │
│        Error: AssertionError in src/auth/flow.py:47          │
│                                                               │
│ 14:42 🔍 Analyzing... found similar failure 3 days ago        │
│        Fix was: check redirect_uri before validation          │
│                                                               │
│ 14:42 💡 Suggest: Apply similar fix?                          │
│        [Y] Yes  [N] No  [D] Show diff  [I] Ignore             │
└───────────────────────────────────────────────────────────────┘
```

This is L2 SUGGESTION in action—proposing, not acting.

## What Exists

- `TEST_FAILURE_RESPONSE` workflow template in `workflows.py`
- `ConfirmationManager` + `PendingSuggestion` in `trust/confirmation.py`
- `TestWatcherFlux` that emits `TestEvent` on pytest completion
- TUI thought stream that can display suggestions

## What's Missing

1. **Event → Workflow Triggering**
   - When `TestEvent(failed)` arrives, match to `TEST_FAILURE_RESPONSE`
   - Check trust level against `workflow.required_trust`

2. **L2 Confirmation UX in TUI**
   - Display suggestion with `[Y] [N] [D] [I]` options
   - Capture keyboard input, route to `ConfirmationManager`
   - Record accept/reject for trust escalation metrics

3. **Suggestion History for Pattern Matching**
   - Query past similar failures from persistence
   - Show "found similar failure N days ago" context

## Implementation Approach

### 1. Wire TestWatcherFlux → Workflow Engine

```python
# In daemon event handler
async def _handle_event(self, event: WitnessEvent) -> None:
    thought = event_to_thought(event)
    await self._send_thought(thought)

    # NEW: Check for matching workflow
    if workflow := match_workflow(event):
        if self._trust_level >= workflow.required_trust:
            await self._trigger_workflow(workflow, event)
```

### 2. Add Suggestion Widget to TUI

```python
class SuggestionPrompt(Static):
    """L2 confirmation prompt with keyboard handling."""

    async def on_key(self, event: Key) -> None:
        if event.key == "y":
            await self._accept()
        elif event.key == "n":
            await self._reject()
        elif event.key == "d":
            await self._show_diff()
        elif event.key == "i":
            await self._ignore()
```

### 3. Trust Escalation Feedback

Show progress toward next level in StatusPanel:
```
Trust: 👁️ L1 BOUNDED [████████░░] 80% to L2
Suggestions: 8 accepted / 10 total (80%)
```

## Files to Modify

| File | Changes |
|------|---------|
| `services/witness/daemon.py` | Add `match_workflow()`, `_trigger_workflow()` |
| `services/witness/tui.py` | Add `SuggestionPrompt` widget, keyboard handlers |
| `services/witness/trust/confirmation.py` | Wire to TUI callbacks |
| `services/witness/cli.py` | Simple console fallback for non-TUI mode |

## Success Criteria

1. `kgentsd summon` running, pytest fails → suggestion appears within 3s
2. User presses `Y` → action executes, recorded to audit trail
3. User presses `N` → rejection recorded, trust metrics updated
4. StatusPanel shows trust escalation progress

## The Daring Move

Don't just show suggestions—make them *feel* helpful. The pattern matching ("found similar failure 3 days ago") is what transforms a notification into a pair programmer moment.

---

*"L2 SUGGESTION: The ghost proposes, the human disposes."*
