# Grounding Agents

**Static analysis for targeted hypothesis generation**

## Purpose

Grounding agents analyze code **structure** (not semantics) to:

1. **Ground hypotheses in facts**: AST analysis provides concrete improvement targets
2. **Reduce hallucination**: LLM hypotheses informed by actual code structure
3. **Target complexity**: Identify high-complexity functions, missing types, etc.
4. **Accelerate generation**: Pre-computed structure avoids redundant parsing

Grounding is the **thesis** in the dialectical evolution process—it represents "what currently exists" as a factual foundation.

## What It Does

- Parse Python source code into Abstract Syntax Tree (AST)
- Extract structural information (classes, functions, imports)
- Compute complexity metrics (cyclomatic, nesting depth)
- Identify missing type annotations
- Detect documentation gaps (missing docstrings)
- Generate **targeted** improvement hypotheses from structure

## What It Doesn't Do

- ❌ Execute code (static analysis only)
- ❌ Understand semantics (what the code means, only what it is)
- ❌ Make value judgments (reports structure, doesn't judge)
- ❌ Generate improved code (that's the Experiment stage)

## Specification: AST Analyzer

```yaml
identity:
  name: ASTAnalyzer
  genus: e
  version: "1.0.0"
  purpose: Analyze Python code structure to ground hypothesis generation

interface:
  input:
    type: ASTAnalysisInput
    description: Path to Python module to analyze
  output:
    type: ASTAnalysisOutput
    description: Structural information and improvement targets
  errors:
    - code: FILE_NOT_FOUND
      description: Module path does not exist
    - code: PARSE_ERROR
      description: File is not valid Python (syntax error)
    - code: EMPTY_MODULE
      description: Module has no analyzable content

behavior:
  description: |
    Parse Python source file into AST and extract:
    - Class definitions (name, methods, base classes)
    - Function definitions (name, args, returns, complexity)
    - Import statements (standard lib, third-party, local)
    - Type annotation coverage
    - Docstring coverage
    - Complexity metrics (cyclomatic, nesting)

    Results are cached for reuse during hypothesis generation.

  guarantees:
    - Returns null structure if parsing fails (never raises on bad syntax)
    - Complexity metrics are deterministic (same code → same metrics)
    - Analysis is read-only (never modifies source)
    - Results are serializable (can cache to disk)

  constraints:
    - Python 3.10+ syntax required
    - Cannot analyze non-Python files
    - Cannot understand runtime behavior (static only)
    - Complexity metrics are heuristics (not proofs)

  side_effects:
    - None (pure function, read-only analysis)

types:
  ASTAnalysisInput:
    path: Path

  ASTAnalysisOutput:
    structure: CodeStructure | null
    error: string | null

  CodeStructure:
    classes: array<ClassInfo>
    functions: array<FunctionInfo>
    imports: array<ImportInfo>
    complexity_hints: array<string>
    docstring: string | null
    total_lines: number
    code_lines: number  # Excluding blanks and comments

  ClassInfo:
    name: string
    bases: array<string>
    methods: array<FunctionInfo>
    docstring: string | null
    line_number: number

  FunctionInfo:
    name: string
    args: array<string>
    returns: string | null  # Return type annotation if present
    is_async: boolean
    cyclomatic_complexity: number
    nesting_depth: number
    has_type_annotations: boolean
    has_docstring: boolean
    line_number: number
    line_count: number

  ImportInfo:
    module: string
    names: array<string>  # Empty for "import foo", populated for "from foo import bar"
    alias: string | null
    is_standard_lib: boolean
    line_number: number
```

## Complexity Metrics

### Cyclomatic Complexity

**Definition**: Number of linearly independent paths through code

**Calculation**:
```
complexity = 1  # Base
+ count(if, elif)
+ count(for, while)
+ count(and, or)  # In boolean expressions
+ count(except)
+ count(assert)
+ count(with)
```

**Interpretation**:
- 1-5: Simple, easy to test
- 6-10: Moderate, consider refactoring
- 11-20: Complex, should refactor
- 21+: Very complex, must refactor

### Nesting Depth

**Definition**: Maximum depth of nested control structures

**Calculation**: Track depth as AST is traversed, record maximum.

**Interpretation**:
- 1-2: Flat, readable
- 3-4: Moderate nesting, acceptable
- 5+: Deep nesting, hard to follow

## Targeted Hypothesis Generation

From structure analysis, generate **specific, actionable** hypotheses:

### Missing Type Annotations

```python
# Structure shows:
FunctionInfo(
    name="calculate",
    args=["x", "y"],
    returns=None,
    has_type_annotations=False
)

# Generated hypothesis:
"Add type annotations to function `calculate` (currently untyped)"
```

### High Complexity

```python
# Structure shows:
FunctionInfo(
    name="process_data",
    cyclomatic_complexity=15,
    nesting_depth=6
)

# Generated hypothesis:
"Refactor `process_data` (complexity 15, nesting 6) into smaller functions"
```

### Missing Docstrings

```python
# Structure shows:
ClassInfo(
    name="DataProcessor",
    docstring=None,
    methods=[...]
)

# Generated hypothesis:
"Add docstring to class `DataProcessor` to document its purpose"
```

### Long Functions

```python
# Structure shows:
FunctionInfo(
    name="handle_request",
    line_count=85
)

# Generated hypothesis:
"Split `handle_request` (85 lines) into focused, composable functions"
```

### Deep Nesting

```python
# Structure shows:
FunctionInfo(
    name="validate_input",
    nesting_depth=7
)

# Generated hypothesis:
"Flatten `validate_input` (nesting depth 7) using early returns or composition"
```

## Example: Analyzing a Real Module

### Input Code

```python
# data_processor.py
import json
from pathlib import Path
from typing import Any

class DataProcessor:
    def __init__(self, config_path):
        self.config = json.loads(Path(config_path).read_text())

    def process(self, data, mode, validate=True, transform=True, save=True):
        result = data
        if validate:
            if not self._validate(result):
                if mode == "strict":
                    raise ValueError("Validation failed")
                elif mode == "lenient":
                    result = self._fix(result)
                else:
                    return None

        if transform:
            for transformer in self.config.get("transformers", []):
                if transformer["enabled"]:
                    if transformer["type"] == "normalize":
                        result = self._normalize(result)
                    elif transformer["type"] == "enrich":
                        result = self._enrich(result)

        if save:
            output_path = self.config.get("output_path", "output.json")
            Path(output_path).write_text(json.dumps(result))

        return result

    def _validate(self, data):
        return isinstance(data, dict)

    def _fix(self, data):
        return {"data": data}

    def _normalize(self, data):
        return {k.lower(): v for k, v in data.items()}

    def _enrich(self, data):
        data["processed"] = True
        return data
```

### Analysis Output

```yaml
structure:
  classes:
    - name: DataProcessor
      bases: []
      docstring: null
      line_number: 5
      methods:
        - name: __init__
          args: [self, config_path]
          returns: null
          has_type_annotations: false
          has_docstring: false
          cyclomatic_complexity: 1
          nesting_depth: 1
          line_number: 6
          line_count: 2

        - name: process
          args: [self, data, mode, validate, transform, save]
          returns: null
          has_type_annotations: false
          has_docstring: false
          cyclomatic_complexity: 11
          nesting_depth: 5
          line_number: 9
          line_count: 25

        - name: _validate
          args: [self, data]
          returns: null
          has_type_annotations: false
          has_docstring: false
          cyclomatic_complexity: 1
          nesting_depth: 1
          line_number: 35

        - name: _fix
          args: [self, data]
          returns: null
          has_type_annotations: false
          has_docstring: false
          cyclomatic_complexity: 1
          nesting_depth: 1
          line_number: 38

        - name: _normalize
          args: [self, data]
          returns: null
          has_type_annotations: false
          has_docstring: false
          cyclomatic_complexity: 1
          nesting_depth: 1
          line_number: 41

        - name: _enrich
          args: [self, data]
          returns: null
          has_type_annotations: false
          has_docstring: false
          cyclomatic_complexity: 1
          nesting_depth: 1
          line_number: 44

  functions: []

  imports:
    - module: json
      names: []
      is_standard_lib: true
      line_number: 2

    - module: pathlib
      names: [Path]
      is_standard_lib: true
      line_number: 3

    - module: typing
      names: [Any]
      is_standard_lib: true
      line_number: 4

  complexity_hints:
    - "DataProcessor.process has cyclomatic complexity 11 (complex)"
    - "DataProcessor.process has nesting depth 5 (deep)"
    - "DataProcessor.process has 25 lines (long function)"
    - "DataProcessor has no docstring"
    - "6 methods have no type annotations"

  docstring: null
  total_lines: 48
  code_lines: 38
```

### Generated Targeted Hypotheses

Based on the analysis above:

1. **"Refactor `DataProcessor.process` (complexity 11, nesting 5, 25 lines) into smaller, composable functions"**
   - Target: High complexity + deep nesting + long function

2. **"Add type annotations to `DataProcessor` methods (6 untyped methods)"**
   - Target: Missing type annotations across class

3. **"Add docstring to class `DataProcessor` to document its purpose and usage"**
   - Target: Missing class docstring

4. **"Extract validation, transformation, and persistence logic from `process` into separate methods"**
   - Target: Single Responsibility Principle violation (long function doing multiple things)

5. **"Flatten `process` method using early returns or guard clauses"**
   - Target: Deep nesting (5 levels)

## Integration with Evolution Pipeline

```python
# Stage 1: Analyze structure
ast_analyzer = ASTAnalyzer()
analysis = await ast_analyzer.invoke(ASTAnalysisInput(path=module.path))

if not analysis.structure:
    # Skip module if parsing failed
    return []

# Stage 2a: Generate AST-based hypotheses
ast_hypotheses = generate_targeted_hypotheses(
    analysis.structure,
    max_targets=3
)
# Result: ["Refactor DataProcessor.process...", "Add type annotations...", ...]

# Stage 2b: Provide structure to LLM for context-aware hypotheses
llm_hypotheses = await hypothesis_engine.invoke(HypothesisInput(
    observations=[
        f"Module has {len(analysis.structure.classes)} classes",
        f"Complexity hints: {analysis.structure.complexity_hints}",
        f"Code preview:\n{get_code_preview(module.path)}",
    ],
    domain="Code quality improvement",
))

# Combine AST-based (targeted) + LLM-based (creative)
all_hypotheses = ast_hypotheses + llm_hypotheses
```

## Caching Strategy

AST analysis results are **cached** during evolution pipeline:

```python
class EvolutionPipeline:
    def __init__(self):
        self._ast_cache: dict[str, CodeStructure | None] = {}

    async def analyze_module(self, module: CodeModule) -> CodeStructure | None:
        key = str(module.path)
        if key not in self._ast_cache:
            result = await self._ast_analyzer.invoke(
                ASTAnalysisInput(path=module.path)
            )
            self._ast_cache[key] = result.structure
        return self._ast_cache[key]
```

This avoids redundant parsing when:
- Generating multiple hypotheses for same module
- Running multiple experiments on same module
- Providing structure context to LLM

## Anti-Patterns

❌ **Don't use AST analysis to make semantic judgments**

```python
# WRONG: AST doesn't understand meaning
if function.name == "calculate":
    hypothesis = "This should use numpy"  # How would AST know this?

# RIGHT: Use structure-based signals
if function.cyclomatic_complexity > 10:
    hypothesis = f"Refactor {function.name} (complexity {function.cyclomatic_complexity})"
```

❌ **Don't trust complexity metrics as absolute truth**

```python
# WRONG: Complexity is a heuristic, not a law
if complexity > 10:
    raise Error("Must refactor!")  # Too rigid

# RIGHT: Use as a signal for hypothesis generation
if complexity > 10:
    hypotheses.append(f"Consider refactoring {name} (complexity {complexity})")
```

❌ **Don't generate hypotheses for every signal**

```python
# WRONG: Hypothesis spam
for func in structure.functions:
    if not func.has_docstring:
        hypotheses.append(f"Add docstring to {func.name}")
    if not func.has_type_annotations:
        hypotheses.append(f"Add types to {func.name}")
    # ... 10 more hypotheses per function

# RIGHT: Prioritize by impact
high_priority = [
    f for f in structure.functions
    if f.cyclomatic_complexity > 10 or f.line_count > 50
]
for func in high_priority[:max_targets]:
    hypotheses.append(f"Refactor {func.name} (complexity {func.cyclomatic_complexity})")
```

❌ **Don't generate vague hypotheses**

```python
# WRONG: Too vague to be actionable
"Improve code quality"
"Make DataProcessor better"
"Fix the issues"

# RIGHT: Specific, testable, grounded in structure
"Refactor DataProcessor.process (complexity 11, nesting 5) into 3-4 focused functions"
"Add type annotations to 6 untyped methods in DataProcessor"
"Extract nested validation logic from process method to reduce nesting from 5 to 2"
```

## Composability

AST Analyzer is a pure morphism:

```yaml
ASTAnalyzer: Path → CodeStructure | null
```

It composes naturally with:

### Hypothesis Generators

```python
structure = await ast_analyzer.invoke(ASTAnalysisInput(path))
hypotheses = generate_targeted_hypotheses(structure)
```

### Pre-Flight Checkers

```python
structure = await ast_analyzer.invoke(ASTAnalysisInput(path))
if not structure:
    return PreFlightReport(can_evolve=False, blocking_issues=["Parse error"])
```

### Prompt Context Builders

```python
structure = await ast_analyzer.invoke(ASTAnalysisInput(path))
context = build_prompt_context(module, structure)
```

## See Also

- **[evolution-agent.md](./evolution-agent.md)** - Full pipeline using grounding
- **[memory.md](./memory.md)** - How grounding interacts with memory
- **[B-gents/hypothesis-engine.md](../b-gents/hypothesis-engine.md)** - LLM-based hypothesis generation
- **[spec/anatomy.md](../anatomy.md)** - What constitutes an agent

---

*"Ground your dreams in structure, then let creativity soar."*
