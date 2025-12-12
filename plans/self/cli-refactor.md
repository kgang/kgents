---
path: self/cli-refactor
status: archived-partial
progress: 75
last_touched: 2025-12-12
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  CRITICAL REVIEW: See docs/cli-refactor-assessment.md
  75% complete (Reflector, FD3, ctx.output all done).
  Remaining: ProposalQueue (kgents inbox). Other features discarded.
---

# CLI Enhancements (Refocused)

> *"The goal is not 'Collaborative Runtime Environment.' The goal is 'good CLI that works with agents.'"*

**Assessment**: See `docs/cli-refactor-assessment.md` for detailed critique.

---

## Done (Archived)

| Feature | Status | Location |
|---------|--------|----------|
| Reflector Protocol | ✅ Done | `protocols/cli/reflector/` |
| FD3 Protocol | ✅ Done | `KGENTS_FD3` env var |
| ctx.output() API | ✅ Done | `protocol.py:140-149` |
| Dynamic Prompt | ✅ Done | PromptState enum |
| TerminalReflector | ✅ Done | `reflector/terminal.py` |
| HeadlessReflector | ✅ Done | `reflector/headless.py` |
| FluxReflector | ✅ Done | `agents/i/reflector/` |

**Tests**: 36 passing for Reflector pattern.

---

## Active: Proposal Queue

**Goal**: View and manage agent proposals from CLI.

```bash
kgents inbox              # List pending proposals
kgents inbox approve 1    # Approve proposal
kgents inbox reject 1     # Reject with reason
```

**Implementation**:
1. `protocols/cli/proposals.py`: ProposalQueue backed by K8s Proposal CRD
2. `handlers/inbox.py`: Command handler
3. Wire to existing PromptState for dynamic prompt

**Exit criteria**:
- `kgents inbox` shows pending proposals
- Approval/rejection works
- Prompt shows `kgents [2 proposals] >` when proposals exist

---

## Discarded (See Assessment)

| Feature | Reason |
|---------|--------|
| Merkle Session State | Wrong abstraction—CLI commands affect external state (K8s, etcd), not internal state. Use structured logging for audit trails. |
| Ghost Text | Conflicts with shell conventions. Use bash/zsh completion scripts instead. |
| Ephemeral TUI | Confuses CLI/TUI boundary. Use `kgents garden` for rich interface. |

---

## Background Guideline: Handler Decomposition

When modifying large handlers (>200 lines), consider splitting:
- Subcommand routing in `__init__.py`
- Implementation in separate files
- ~200 lines per file guideline

This is ongoing maintenance, not a project phase.

---

## Historical Context

<details>
<summary>Original Plan (870 lines, archived)</summary>

The original plan "The Collaborative Runtime Environment" expanded from
"Conversational CLI" into a six-feature manifesto including:

- FD3 Protocol (now done)
- Merkle Session State (discarded)
- Pre-Emptive Signal Layer (simplified to ProposalQueue)
- Ghost Text (discarded)
- Reflector Pattern (now done)
- Handler Decomposition (kept as guideline)

See git history for the full original document, or `docs/cli-refactor-assessment.md`
for the critical review that led to this refocusing.

The key insight: the Reflector pattern was already implemented when the plan was
written. 75% of the work was done; the plan just didn't know it.

</details>

---

*"We're closer than the plan admits."*
