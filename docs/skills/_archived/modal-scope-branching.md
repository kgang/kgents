# Skill: ModalScope Branching Pattern

> Git-like branching for context exploration with merge strategies and budget enforcement.

**Difficulty**: Medium
**Prerequisites**: Reactive primitives, async/await
**Files**: `impl/claude/agents/d/modal_scope.py`
**References**: `agents/d/_tests/test_modal_scope.py`, `agents/d/context_window.py`

---

## Overview

ModalScope provides git-like branching for conversation context. Agents can:
- Branch to explore speculative paths
- Merge branches back with different strategies
- Discard branches, returning entropy budget
- Track budget to limit exploration scope

| Operation | Git Equivalent | Description |
|-----------|----------------|-------------|
| `branch()` | `git checkout -b` | Create isolated child scope |
| `merge()` | `git merge` | Integrate branch back to parent |
| `discard()` | `git branch -D` | Compost branch, return entropy |
| `duplicate()` | `git clone` | Independent copy (no parent tracking) |

---

## Create Root Scope

```python
from agents.d.modal_scope import ModalScope

root = ModalScope.create_root(
    max_tokens=100_000,
    initial_system="You are a helpful assistant.",
)
```

The root scope has full entropy budget (1.0) and no parent.

---

## Branching

### Create a Branch

```python
branch = root.branch(
    name="explore-option-a",
    budget=0.1,  # 10% of parent tokens allowed
)
```

**Parameters**:
- `name`: Human-readable branch name (must be unique)
- `budget`: Fraction of parent tokens allowed for growth (0, 1.0]
- `strategy`: Default merge strategy (optional)
- `commit_message`: Purpose description (optional)

### Add Content to Branch

```python
from agents.d.context_window import TurnRole

branch.window.append(TurnRole.ASSISTANT, "Let me try approach A...")
branch.window.append(TurnRole.USER, "What are the tradeoffs?")
branch.window.append(TurnRole.ASSISTANT, "Approach A is faster but uses more memory...")
```

### Multiple Branches (Parallel Exploration)

```python
branch_a = root.branch("option-a", budget=0.1)
branch_b = root.branch("option-b", budget=0.1)
branch_c = root.branch("option-c", budget=0.1)

# Each branch is isolated
branch_a.window.append(TurnRole.ASSISTANT, "Path A: Use recursion")
branch_b.window.append(TurnRole.ASSISTANT, "Path B: Use iteration")
branch_c.window.append(TurnRole.ASSISTANT, "Path C: Use dynamic programming")
```

---

## Merge Strategies

### SUMMARIZE (Default)

Compresses branch turns into a summary system message:

```python
from agents.d.modal_scope import MergeStrategy

result = root.merge(branch_a, strategy=MergeStrategy.SUMMARIZE)

# Result contains summary of branch exploration
print(result.summary)
```

### SQUASH

Creates a single turn with key assistant decisions:

```python
result = root.merge(branch_a, strategy=MergeStrategy.SQUASH)
# Single assistant turn with "Key outputs:" prefix
```

### REBASE

Replays all branch turns onto parent:

```python
result = root.merge(branch_a, strategy=MergeStrategy.REBASE)
# All turns added to parent in order
print(f"Added {result.merged_turns} turns")
```

### Merge Result

```python
from agents.d.modal_scope import MergeResult

result: MergeResult = root.merge(branch)
if result.success:
    print(f"Merged {result.merged_turns} turns")
    print(f"Strategy: {result.strategy.value}")
    print(f"Tokens added: {result.tokens_added}")
else:
    print(f"Merge failed: {result.error}")
```

---

## Discard Branches

When exploration isn't fruitful, discard the branch:

```python
from agents.d.modal_scope import DiscardResult

result: DiscardResult = root.discard(branch_b)
if result.success:
    print(f"Discarded {result.discarded_turns} turns")
    print(f"Entropy returned: {result.entropy_returned:.3f}")
```

The entropy budget is returned to the parent.

---

## Budget Enforcement

Branches have entropy budgets to limit exploration scope.

### Check Budget Status

```python
print(f"Budget remaining: {branch.budget_remaining:.1%}")
print(f"Tokens remaining: {branch.tokens_remaining}")
print(f"Over budget: {branch.is_over_budget}")
```

### Budget Calculation

```
allowed_growth = parent_tokens * entropy_budget
budget_remaining = 1.0 - (current_growth / allowed_growth)
```

Example: With parent at 1000 tokens and budget=0.1, branch can grow by 100 tokens.

---

## Duplicate (Independent Copy)

Unlike `branch()`, `duplicate()` creates a completely independent scope:

```python
scope_b = scope_a.duplicate()

# Both can evolve independently
# No merge/discard semantics needed
```

Use `duplicate()` when you don't need to merge back.

---

## State Queries

```python
# Check scope status
print(scope.is_root)      # True if no parent
print(scope.is_active)    # True if not merged/discarded
print(scope.depth)        # Nesting level (root = 0)

# List children
for child in scope.children:
    print(f"  {child.branch_name}: {child.depth}")

# Get specific child
option_a = scope.get_child("option-a")
```

---

## Serialization

```python
# Save scope tree
data = root.to_dict()

# Restore later
restored = ModalScope.from_dict(data)
```

Children are serialized recursively.

---

## Full Example

```python
from agents.d.modal_scope import ModalScope, MergeStrategy
from agents.d.context_window import TurnRole

# Create root
root = ModalScope.create_root(max_tokens=8000)
root.window.append(TurnRole.USER, "What's the best sorting algorithm?")

# Branch for two approaches
quick_sort = root.branch("quick-sort", budget=0.15)
quick_sort.window.append(
    TurnRole.ASSISTANT,
    "QuickSort: O(n log n) average, O(n^2) worst case. In-place."
)

merge_sort = root.branch("merge-sort", budget=0.15)
merge_sort.window.append(
    TurnRole.ASSISTANT,
    "MergeSort: O(n log n) guaranteed. Stable but uses O(n) space."
)

# Evaluate and decide
# ... (some evaluation logic)

# Merge the better option
result = root.merge(quick_sort, strategy=MergeStrategy.SUMMARIZE)
print(f"Merged quick-sort: {result.summary[:100]}...")

# Discard the other
root.discard(merge_sort)

# Continue conversation
root.window.append(TurnRole.USER, "Thanks! Can you show me the code?")
```

---

## Verification

```bash
cd impl/claude
uv run pytest agents/d/_tests/test_modal_scope.py -v
```

---

## Common Pitfalls

### 1. Branching from Merged/Discarded Scope

```python
# This raises ValueError
root.merge(branch)
branch.branch("sub")  # Error: Cannot branch from merged scope
```

### 2. Duplicate Branch Names

```python
root.branch("explore")
root.branch("explore")  # Error: Branch 'explore' already exists
```

### 3. Merging Non-Child

```python
# This fails
other_root = ModalScope.create_root()
result = root.merge(other_root)  # Error: not a child
```

---

## AGENTESE Integration

ModalScope maps to AGENTESE void.entropy paths:

```
void.entropy.sip branch_name=explore → ModalScope.branch()
void.entropy.pour action=merge → ModalScope.merge()
void.entropy.pour action=discard → ModalScope.discard()
```

---

## Related Skills

- [reactive-primitives](reactive-primitives.md) - Signal/Computed for state
- [test-patterns](test-patterns.md) - Testing branch scenarios
- [building-agent](building-agent.md) - Agent composition

---

## Source Reference

`impl/claude/agents/d/modal_scope.py:72-615`

---

*Skill created: 2025-12-14 | Wave 1 EDUCATE Phase*
