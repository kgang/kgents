# Graph Composition

> *"Linear thought is a subset of graph thought."*

This document extends C-gent's composition capabilities from linear pipelines to **directed acyclic graphs (DAGs)**, enabling non-linear reasoning through branching, merging, and controlled recursion.

## Derivation from Bootstrap

Graph composition does not require new primitives. It is **already derivable**:

```
Graph Composition = Compose + Fix + Conditional
```

| Pattern | Bootstrap Source |
|---------|-----------------|
| Sequential | `Compose` (`A >> B >> C`) |
| Branching | `Compose` + conditional (`A >> (B | C)`) |
| Merging | `Compose` with aggregation |
| Recursion | `Fix` with termination |

This extension formalizes these existing capabilities into graph structures.

## Why Not Y-gent?

An earlier proposal suggested "Y-gent" as a separate genus for graph composition. Analysis revealed:

1. **Y-combinator IS Fix** - The bootstrap `Fix` agent already handles recursion
2. **Branch/merge exist** - `spec/c-gents/parallel.md` already defines parallel composition
3. **Graph is just DAG of Compose** - No new primitive needed

**Decision**: Merge graph patterns into C-gent rather than create new genus.

## Graph of Thoughts

Research shows Graph of Thoughts (GoT) outperforms Chain of Thoughts (CoT) on complex tasks:

```
Chain of Thought (Linear):      Graph of Thoughts (DAG):
┌───┐   ┌───┐   ┌───┐           ┌───┐
│ A │ → │ B │ → │ C │           │ A │
└───┘   └───┘   └───┘           └─┬─┘
                                  │
O(n) sequential                 ┌─┴─┐
                                ▼   ▼
                              ┌───┐ ┌───┐
                              │ B │ │ C │  (parallel)
                              └─┬─┘ └─┬─┘
                                └──┬──┘
                                   ▼
                                 ┌───┐
                                 │ D │  (merge)
                                 └───┘

                              O(depth) with parallelism
```

## Thought Graph Structure

### Nodes

```python
@dataclass
class ThoughtNode:
    """A single node in the reasoning graph."""

    id: str
    type: NodeType
    agent: Agent | None = None
    input: Any = None
    output: Any = None

    # Graph structure
    children: list["ThoughtNode"] = field(default_factory=list)
    parents: list["ThoughtNode"] = field(default_factory=list)

    depth: int = 0
    status: NodeStatus = NodeStatus.PENDING


class NodeType(Enum):
    EXECUTE = "execute"      # Run an agent
    BRANCH = "branch"        # Fork into multiple paths
    MERGE = "merge"          # Aggregate multiple paths
    TERMINATE = "terminate"  # End of path


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BACKTRACKED = "backtracked"
```

### Graph

```python
@dataclass
class ThoughtGraph:
    """A DAG of reasoning steps."""

    root: ThoughtNode
    nodes: dict[str, ThoughtNode] = field(default_factory=dict)

    # Limits (enforce termination)
    max_depth: int = 10
    max_branches: int = 5
    max_nodes: int = 100

    def branch(self, parent_id: str, agents: list[Agent]) -> list[ThoughtNode]:
        """Create a branch point with multiple child paths."""
        # Enforces max_branches limit
        ...

    def merge(self, child_ids: list[str], aggregator: Agent) -> ThoughtNode:
        """Create a merge point that aggregates child outputs."""
        ...

    def backtrack(self, node_id: str) -> None:
        """Mark a path as backtracked and try alternatives."""
        ...
```

## Recursion via Fix

The "Y-combinator" pattern is simply Fix with explicit recursion:

```python
# This is what Y-combinator does:
async def recursive_solve(transform, initial, max_depth=10):
    """Apply transform recursively until stable or max_depth."""
    return await fix(
        transform=transform,
        initial=initial,
        max_iterations=max_depth,
        equality_check=lambda a, b: a == b
    )
```

For controlled recursion with termination checking (using V-gent):

```python
async def recursive_with_validation(transform, initial, v_gent, context):
    """Recurse until V-gent approves or max iterations."""
    async def validated_transform(value):
        result = await transform(value)
        verdict = await v_gent.validate(result, context)
        if verdict.approved:
            return result  # Stable: terminates Fix
        return result  # Continue iterating

    return await fix(validated_transform, initial)
```

## Branch-Merge Pattern

The common branch-merge pattern uses existing C-gent parallel composition:

```python
async def branch_merge(
    input: Any,
    branches: list[Agent],
    aggregator: Agent | None = None
) -> Any:
    """
    Branch to multiple agents in parallel, then merge results.

    This is C-gent parallel composition with aggregation.
    """
    # Execute branches in parallel (from parallel.md)
    results = await asyncio.gather(
        *[branch.invoke(input) for branch in branches]
    )

    # Merge results
    if aggregator:
        return await aggregator.invoke(results)
    return results
```

## Graph Executor

```python
@dataclass
class GraphExecutor:
    """Executes a ThoughtGraph with parallel branch processing."""

    graph: ThoughtGraph
    max_parallel: int = 4

    async def execute(self) -> GraphResult:
        """Execute the graph from root to all leaves."""
        results: dict[str, Any] = {}
        execution_order = self._topological_sort()

        for node_id in execution_order:
            node = self.graph.nodes[node_id]

            match node.type:
                case NodeType.EXECUTE:
                    results[node_id] = await node.agent.invoke(node.input)
                case NodeType.BRANCH:
                    results[node_id] = await self._execute_branch(node, results)
                case NodeType.MERGE:
                    results[node_id] = await self._execute_merge(node, results)
                case NodeType.TERMINATE:
                    results[node_id] = node.input

            node.status = NodeStatus.COMPLETED
            node.output = results[node_id]

        return GraphResult(outputs=results)

    def _topological_sort(self) -> list[str]:
        """Return node IDs in valid execution order."""
        # Standard topological sort ensuring parents execute before children
        ...
```

## Common Patterns

### Divide and Conquer

```python
# Decompose problem, solve in parallel, aggregate
graph = ThoughtGraph(root=ThoughtNode(id="problem", type=NodeType.EXECUTE))
graph.branch("problem", [solver_a, solver_b, solver_c])
graph.merge(["solver_a_out", "solver_b_out", "solver_c_out"], aggregator)
```

### Beam Search

```python
# Generate N candidates, prune to best K, repeat
async def beam_search(initial, generate, evaluate, beam_width=3, depth=3):
    candidates = [initial]

    for _ in range(depth):
        # Branch: generate variations
        all_variants = []
        for c in candidates:
            variants = await generate.invoke(c)
            all_variants.extend(variants)

        # Merge: evaluate and keep top K
        scored = [(v, await evaluate.invoke(v)) for v in all_variants]
        scored.sort(key=lambda x: x[1], reverse=True)
        candidates = [v for v, s in scored[:beam_width]]

    return candidates[0]  # Best
```

### Iterative Refinement

```python
# Generate → Validate → Refine (via Fix)
async def iterative_refine(initial, refiner, validator, max_iter=5):
    return await fix(
        transform=lambda x: refiner.invoke((x, await validator.invoke(x))),
        initial=initial,
        max_iterations=max_iter
    )
```

## Integration with Existing C-gents

| Existing | Graph Extension |
|----------|-----------------|
| `A >> B` | Sequential path in graph |
| `parallel(A, B, C)` | Branch node |
| `fix(transform)` | Recursive node |
| `conditional(pred, A, B)` | Branch with predicate |

Graph composition **extends** these primitives, it doesn't replace them.

## Anti-Patterns

1. ❌ Cyclic graphs (must be DAGs for termination)
2. ❌ Unbounded recursion (use max_depth)
3. ❌ Over-parallelization (respect resource limits)
4. ❌ Using graphs for linear tasks (overhead)
5. ❌ Merging incompatible types without validation

## Principles Alignment

| Principle | How Graph Composition Satisfies |
|-----------|--------------------------------|
| **Tasteful** | Extends existing patterns, doesn't replace |
| **Composable** | Graphs compose via node connection |
| **Generative** | Derivable from Compose + Fix |
| **Heterarchical** | Branches are peers; no fixed hierarchy |

## See Also

- [composition.md](composition.md) - Linear composition
- [parallel.md](parallel.md) - Parallel execution
- [../bootstrap.md](../bootstrap.md) - Fix primitive
