# K-Block Boundary Detection

## Overview

The `BoundaryDetector` service identifies natural boundaries for aggregating `FunctionCrystal` artifacts into coherent K-blocks.

**Philosophy**: K-blocks are "coherence windows"—not too small (inane), not too large (incomprehensible). Target: 500-5000 tokens per K-block, ideal ~2000 (short essay length).

## Quick Start

```python
from services.code import BoundaryDetector, BoundaryStrategy, FunctionCrystal

# Create detector with default heuristics
detector = BoundaryDetector(
    min_tokens=500,
    max_tokens=5000,
    target_tokens=2000,
)

# Detect boundaries using HYBRID strategy (recommended)
functions: list[FunctionCrystal] = [...]  # Your function crystals
candidates = await detector.detect_boundaries(functions, BoundaryStrategy.HYBRID)

# Check which candidates fall within size heuristic
good_candidates = [c for c in candidates if c.within_size_heuristic]
```

## Strategies

### FILE (Baseline)
- **Signal**: Filesystem structure
- **Output**: One K-block per file
- **Use Case**: Simplest baseline, respects existing file organization
- **Confidence**: 1.0 (trivial boundary)

### CLASS
- **Signal**: Object-oriented boundaries
- **Output**: One K-block per class, standalone functions get individual blocks
- **Use Case**: Respect class encapsulation boundaries
- **Confidence**: 0.85

### IMPORT
- **Signal**: Semantic import graph
- **Output**: Clusters of functions with similar import profiles (Jaccard similarity ≥ 0.3)
- **Use Case**: Group functions by shared dependencies
- **Confidence**: 0.7

### CALLGRAPH
- **Signal**: Control flow analysis
- **Output**: Strongly connected components (Tarjan's algorithm)
- **Use Case**: Group functions that call each other cyclically
- **Confidence**: 0.8

### HYBRID (Recommended)
- **Signal**: Multi-signal fusion
- **Algorithm**:
  1. Start with FILE boundaries
  2. Split if > max_tokens using CLASS
  3. Further split using CALLGRAPH if still too large
  4. (Future) Merge if < min_tokens and high coupling
- **Use Case**: Production use—balances all signals
- **Confidence**: 0.85

### SEMANTIC (Future)
- **Signal**: Embedding similarity (LLM-based)
- **Status**: Not yet implemented
- **Use Case**: Group semantically related functions

### GALOIS (Future)
- **Signal**: Categorical restructuring (D-gent integration)
- **Status**: Not yet implemented
- **Use Case**: Restructuring fixed points

## Metrics

### Token Estimation
```python
tokens = detector.estimate_tokens(functions)
```

Rough heuristic: 1 token ≈ 4 characters. Considers:
- Signature length
- Docstring length
- Estimated body length (line_range × 40 chars/line)

**Note**: For production accuracy, integrate `tiktoken` library.

### Coherence (Internal)
```python
coherence = detector.compute_coherence(functions)
```

Measures how much functions within a set call each other:
- **Formula**: `internal_calls / max_possible_calls`
- **Range**: [0.0, 1.0]
- **High coherence** → Functions are tightly coupled (good for a K-block)

### Coupling (External)
```python
coupling = detector.compute_coupling(inside_funcs, outside_funcs)
```

Measures how much two sets of functions call each other:
- **Formula**: `cross_calls / max_possible_cross_calls`
- **Range**: [0.0, 1.0]
- **High coupling** → Sets should merge

## Split Suggestions

When a K-block exceeds `max_tokens`, the detector suggests splits:

```python
suggestions = await detector.suggest_splits(kblock_id, oversized_functions)

for suggestion in suggestions:
    print(f"Current size: {suggestion.current_size} tokens")
    print(f"Rationale: {suggestion.rationale}")
    for split in suggestion.proposed_splits:
        print(f"  - Split: {len(split.function_ids)} functions, {split.estimated_tokens} tokens")
```

**Split Strategies** (in order of preference):
1. **By class**: If all resulting classes fall within heuristic
2. **By call graph**: If SCCs fall within heuristic
3. **Manual split**: Fallback—split into equal halves

## Merge Suggestions

When K-blocks are small and highly coupled, the detector suggests merges:

```python
kblocks = [
    ("kb_a", funcs_a),
    ("kb_b", funcs_b),
]

suggestions = await detector.suggest_merges(kblocks)

for suggestion in suggestions:
    print(f"Merge {suggestion.kblock_ids}")
    print(f"Coupling: {suggestion.coupling_score:.2f}")
    print(f"Merged size: {suggestion.merged_size} tokens")
```

**Merge Criteria**:
- Both blocks < `max_tokens`
- Merged size ≤ `max_tokens`
- Coupling ≥ 0.3 (high coupling threshold)

## Data Structures

### FunctionCrystal
Atomic unit of code analysis:
```python
@dataclass(frozen=True)
class FunctionCrystal:
    id: str                       # "file.py:ClassName.method_name"
    name: str                     # "method_name"
    file_path: str                # Absolute path
    line_range: tuple[int, int]   # (start_line, end_line)
    signature: str                # Full signature
    docstring: str | None
    class_name: str | None        # Parent class if method
    imports: frozenset[str]       # Imported modules
    calls: frozenset[str]         # IDs of called functions
    called_by: frozenset[str]     # IDs of callers
    is_test: bool = False
    is_private: bool = False      # Starts with _
    is_async: bool = False
```

### KBlockCandidate
Proposed K-block boundary:
```python
@dataclass(frozen=True)
class KBlockCandidate:
    function_ids: frozenset[str]
    boundary_type: str            # "FILE", "CLASS", "IMPORT_CLUSTER", "SCC", "HYBRID"
    confidence: float             # 0.0-1.0
    rationale: str
    estimated_tokens: int

    @property
    def within_size_heuristic(self) -> bool:
        return 500 <= self.estimated_tokens <= 5000
```

## Example: Full Workflow

```python
from services.code import BoundaryDetector, BoundaryStrategy, FunctionCrystal

# 1. Parse code and create FunctionCrystals
functions = [
    FunctionCrystal(
        id="service.py:ClassA.method1",
        name="method1",
        file_path="service.py",
        line_range=(10, 20),
        signature="def method1(self) -> None",
        docstring="Method docs",
        class_name="ClassA",
        imports=frozenset(["os", "sys"]),
        calls=frozenset(["service.py:ClassA.method2"]),
        called_by=frozenset(),
    ),
    # ... more functions
]

# 2. Detect boundaries
detector = BoundaryDetector()
candidates = await detector.detect_boundaries(functions, BoundaryStrategy.HYBRID)

# 3. Filter for good candidates
good_candidates = [c for c in candidates if c.within_size_heuristic]

# 4. Check for splits needed
for candidate in candidates:
    if candidate.is_too_large:
        funcs = [f for f in functions if f.id in candidate.function_ids]
        suggestions = await detector.suggest_splits(candidate.function_ids, funcs)
        print(f"Split suggestion: {suggestions[0].rationale}")

# 5. Check for merges
kblocks = [(f"kb_{i}", [f for f in functions if f.id in c.function_ids])
           for i, c in enumerate(candidates)]
merge_suggestions = await detector.suggest_merges(kblocks)

for suggestion in merge_suggestions:
    print(f"Consider merging: {suggestion.kblock_ids}")
```

## Testing

Comprehensive test suite in `_tests/test_boundary.py`:
```bash
uv run pytest services/code/_tests/test_boundary.py -v
```

**Coverage**:
- All strategies (FILE, CLASS, IMPORT, CALLGRAPH, HYBRID)
- Token estimation
- Coherence and coupling metrics
- Split suggestions for oversized blocks
- Merge suggestions for coupled blocks
- Edge cases (empty input, no calls, no imports)

## Future Work

### Short Term
- Integrate `tiktoken` for accurate token counting
- Implement merge logic in HYBRID strategy
- Add visualization of call graph clusters

### Long Term
- SEMANTIC strategy using embeddings
- GALOIS strategy using categorical restructuring
- Machine learning to tune thresholds (min/max tokens, coupling threshold)
- Interactive boundary adjustment UI

## Philosophy

K-blocks are **airtight bulkheads**:
- **Internally coherent**: High internal coupling (functions call each other)
- **Externally decoupled**: Low external coupling (minimal cross-boundary calls)
- **Right-sized**: Not too small (inane), not too large (incomprehensible)

The boundary detector automates Kent's guidance:
> "Automatically identify code domains or airtight bulkhead abstraction boundaries."

## References

- Kent's guidance on K-blocks (context window coherence)
- K-Block implementation: `services/k_block/core/kblock.py`
- Code service: `services/code/service.py`
- Tarjan's SCC algorithm: [Wikipedia](https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm)
