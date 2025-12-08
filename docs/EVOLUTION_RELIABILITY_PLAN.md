# Evolution Pipeline Reliability Improvement Plan

**Created**: Dec 8, 2025
**Status**: Phase 2.5 - Reliability Enhancement
**Goal**: Achieve >90% incorporation success rate with robust error handling

---

## Problem Statement

Current evolution pipeline (`evolve.py` + `agents/e/`) suffers from low incorporation rates due to:

### Failure Categories

| Failure Type | Examples | Impact | Frequency |
|-------------|----------|---------|-----------|
| **Type mismatches** | `Maybe[str` (incomplete type), wrong generic params | Syntax/import errors | High |
| **Missing arguments** | `Tension()` missing `severity`, constructors incomplete | Runtime errors | Medium |
| **Signature mismatches** | `Hypothesis` missing `supporting_observations` field | Type errors | Medium |
| **Pre-existing errors** | `base.py`, `openrouter.py`, `cli.py` propagate to experiments | Cascade failures | High |
| **Syntax errors** | Malformed LLM-generated code blocks, unclosed strings | Parse failures | Medium |
| **Incomplete code** | LLM returns partial files, truncated functions | Invalid modules | Low |

**Current success rate**: ~30-50% incorporation
**Target success rate**: >90% incorporation

---

## Root Cause Analysis

### 1. **Prompt Quality Issues**

Current prompts lack:
- **Explicit type signature requirements** (no validation guidance)
- **Complete signature examples** (constructors, dataclass fields)
- **Context about pre-existing errors** (blind to cascade issues)
- **Structural constraints** (complete files, not fragments)
- **Error-aware iteration** (no feedback loop from failures)

### 2. **Parsing Fragility**

Current parsing (`agents/e/experiment.py:extract_code()`):
- **Regex-based extraction** - brittle with malformed markdown
- **No syntax recovery** - single parse failure = total failure
- **No schema validation** - missing fields detected late (at mypy time)
- **No partial success** - can't extract well-formed portions
- **Limited format support** - assumes specific markdown structure

### 3. **Validation Gaps**

Current validation (`agents/e/experiment.py:TestAgent`):
- **Late validation** - errors found after full generation (expensive)
- **Binary pass/fail** - no incremental repair attempts
- **No pre-flight checks** - doesn't validate input context first
- **No delta validation** - doesn't check if change is minimal/safe
- **No type-aware diffing** - can't isolate type errors from logic changes

### 4. **Missing Error Recovery**

Current system:
- **No retry with refinement** - fails once, gives up
- **No fallback strategies** - can't try simpler improvements
- **No error categorization** - all failures look the same
- **No learning from failures** - same mistakes repeated
- **No human-in-the-loop** - can't ask clarifying questions

---

## Solution Architecture

### Three-Layer Reliability Stack

```
┌──────────────────────────────────────────────┐
│  Layer 3: Recovery & Learning                │  ← Handle failures gracefully
│  - Retry with refined prompts                │
│  - Fallback strategies                       │
│  - Error memory & pattern learning           │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  Layer 2: Robust Parsing & Validation       │  ← Parse anything, validate early
│  - Multi-strategy parsing                   │
│  - Schema validation (pre-mypy)             │
│  - AST-based validation                     │
│  - Incremental repair                       │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│  Layer 1: High-Quality Prompts              │  ← Prevent errors at source
│  - Type-aware code generation               │
│  - Complete signature scaffolding           │
│  - Pre-existing error context               │
│  - Structural constraints                   │
└──────────────────────────────────────────────┘
```

---

## Layer 1: Prompt Engineering Improvements

### 1.1 Type-Aware Prompting

**New**: `agents/e/prompts.py` - Centralized prompt templates

```python
@dataclass
class PromptContext:
    """Rich context for code generation prompts."""
    module_path: Path
    current_code: str
    ast_structure: CodeStructure
    type_annotations: dict[str, str]  # name → type signature
    imports: list[str]
    pre_existing_errors: list[str]  # from mypy
    similar_patterns: list[str]  # from codebase grep
    principles: list[str]  # kgents principles to follow

def build_improvement_prompt(
    hypothesis: str,
    context: PromptContext,
    improvement_type: str
) -> str:
    """
    Build a prompt with:
    1. Clear type signature requirements
    2. Complete constructor examples
    3. Pre-existing error warnings
    4. Structural validation rules
    """
    return f"""
# Code Improvement Task

## Hypothesis
{hypothesis}

## Current Code Structure
File: {context.module_path}
Classes: {', '.join(context.ast_structure.classes)}
Functions: {', '.join(context.ast_structure.functions)}

## Type Signatures (MUST PRESERVE)
{format_type_signatures(context.type_annotations)}

## Pre-Existing Issues (DO NOT INTRODUCE MORE)
{format_errors(context.pre_existing_errors)}

## Patterns from Similar Code
{format_patterns(context.similar_patterns)}

## CRITICAL REQUIREMENTS

1. **Complete type signatures**: All function params and return types MUST be annotated
2. **Valid constructors**: All dataclass fields MUST have default values or be provided in __init__
3. **Preserve imports**: Return complete import block from original file
4. **Complete file**: Return ENTIRE file contents, not fragments
5. **Syntax validation**: Code must parse with `ast.parse()`
6. **Mypy compliance**: Code must pass `mypy --strict` (or match existing error count)

## Output Format

### METADATA (JSON)
```json
{{
  "description": "Brief description",
  "rationale": "Why this improves the code",
  "improvement_type": "{improvement_type}",
  "confidence": 0.0-1.0,
  "changed_symbols": ["symbol1", "symbol2"],
  "risk_level": "low|medium|high"
}}
```

### CODE (Complete Python file)
```python
# Complete file contents here
# MUST include all imports
# MUST include all classes/functions (even unchanged ones)
# MUST have valid type signatures
```

## Principles to Follow
{format_principles(context.principles)}

Generate the improvement following these requirements EXACTLY.
"""
```

**Key improvements**:
- ✅ Explicit type signature requirements
- ✅ Pre-existing error awareness
- ✅ Complete file requirement (not fragments)
- ✅ Structured output format
- ✅ Risk level self-assessment

### 1.2 Scaffolding & Examples

**New**: Include concrete examples in prompts

```python
def add_scaffolding_examples(context: PromptContext) -> str:
    """Add examples of correct patterns from the codebase."""

    # Extract similar patterns from successful modules
    patterns = grep_codebase_for_patterns(
        class_names=context.ast_structure.classes,
        function_signatures=context.type_annotations
    )

    return f"""
## Examples from Codebase

### Correct Dataclass Pattern
{patterns['dataclass_example']}

### Correct Agent Pattern
{patterns['agent_example']}

### Correct Type Annotation Pattern
{patterns['type_annotation_example']}

Use these patterns as templates.
"""
```

### 1.3 Error-Aware Context

**New**: `PreFlightChecker` - validates context before generation

```python
class PreFlightChecker(Agent[CodeModule, PreFlightReport]):
    """
    Check module health before attempting evolution.

    Prevents wasted LLM calls on modules with fundamental issues.
    """

    async def invoke(self, module: CodeModule) -> PreFlightReport:
        """Run pre-flight checks."""
        issues = []

        # 1. Parse current code
        try:
            tree = ast.parse(module.path.read_text())
        except SyntaxError as e:
            issues.append(f"BLOCKER: Syntax error at line {e.lineno}")
            return PreFlightReport(
                can_evolve=False,
                blocking_issues=issues
            )

        # 2. Check for pre-existing type errors
        type_errors = await self._check_types(module.path)
        if len(type_errors) > 10:
            issues.append(f"WARNING: {len(type_errors)} pre-existing type errors")

        # 3. Check for incomplete definitions
        incomplete = find_incomplete_definitions(tree)
        if incomplete:
            issues.append(f"WARNING: Incomplete definitions: {incomplete}")

        # 4. Check for missing imports
        missing = find_missing_imports(tree, module.path.parent)
        if missing:
            issues.append(f"BLOCKER: Missing imports: {missing}")
            return PreFlightReport(
                can_evolve=False,
                blocking_issues=issues
            )

        return PreFlightReport(
            can_evolve=True,
            warnings=issues,
            baseline_error_count=len(type_errors)
        )
```

**Integration**: Run before hypothesis generation, skip or adjust strategy for problematic modules.

---

## Layer 2: Robust Parsing & Validation

### 2.1 Multi-Strategy Parser

**Replace**: `agents/e/experiment.py:extract_code()` (fragile regex)
**With**: `agents/e/parser.py` - Multi-strategy parsing

```python
class CodeParser:
    """
    Robust parser with multiple fallback strategies.

    Strategy priority:
    1. Structured markdown (## METADATA / ## CODE blocks)
    2. JSON + code block extraction
    3. Pure code block (```python ... ```)
    4. AST-based extraction (find valid Python spans)
    5. LLM-based repair (ask LLM to fix malformed output)
    """

    def parse(self, llm_response: str) -> ParseResult:
        """Parse LLM response with fallback strategies."""

        # Strategy 1: Structured markdown
        result = self._parse_structured(llm_response)
        if result.success:
            return result

        # Strategy 2: JSON + code blocks
        result = self._parse_json_code(llm_response)
        if result.success:
            return result

        # Strategy 3: Pure code block
        result = self._parse_code_block(llm_response)
        if result.success:
            return result

        # Strategy 4: AST-based extraction
        result = self._parse_ast_spans(llm_response)
        if result.success:
            return result

        # Strategy 5: LLM repair (expensive, last resort)
        return await self._llm_repair(llm_response)

    def _parse_structured(self, response: str) -> ParseResult:
        """Parse structured response with ## headers."""
        metadata_match = re.search(
            r'##\s*METADATA.*?```(?:json)?\s*\n(.*?)```',
            response,
            re.DOTALL | re.IGNORECASE
        )

        code_match = re.search(
            r'##\s*CODE.*?```(?:python)?\s*\n(.*?)```',
            response,
            re.DOTALL | re.IGNORECASE
        )

        if metadata_match and code_match:
            try:
                metadata = json.loads(metadata_match.group(1))
                code = code_match.group(1)

                # Validate extracted code
                ast.parse(code)  # Syntax check

                return ParseResult(
                    success=True,
                    metadata=metadata,
                    code=code,
                    strategy="structured"
                )
            except (json.JSONDecodeError, SyntaxError) as e:
                return ParseResult(
                    success=False,
                    error=f"Structured parse failed: {e}"
                )

        return ParseResult(success=False, error="No structured blocks found")

    def _parse_ast_spans(self, response: str) -> ParseResult:
        """
        Extract code by finding valid Python AST spans.

        Tolerates markdown noise, partial responses, etc.
        """
        lines = response.split('\n')

        # Try every contiguous span of lines
        for start in range(len(lines)):
            for end in range(start + 10, len(lines) + 1):
                code_candidate = '\n'.join(lines[start:end])

                try:
                    tree = ast.parse(code_candidate)

                    # Validate it looks like a complete module
                    if self._is_complete_module(tree):
                        return ParseResult(
                            success=True,
                            code=code_candidate,
                            strategy="ast_span",
                            metadata=self._infer_metadata(tree)
                        )
                except SyntaxError:
                    continue

        return ParseResult(success=False, error="No valid AST spans found")

    def _is_complete_module(self, tree: ast.Module) -> bool:
        """Check if AST represents a complete module."""
        # Has imports
        has_imports = any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in tree.body)

        # Has meaningful content (classes or functions)
        has_content = any(
            isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            for n in tree.body
        )

        # Not too short
        source_lines = ast.unparse(tree).split('\n')
        is_substantial = len(source_lines) > 20

        return has_imports and has_content and is_substantial
```

**Key features**:
- ✅ Multiple parsing strategies with fallbacks
- ✅ AST-based validation (not just regex)
- ✅ Tolerates malformed markdown
- ✅ Can extract partial but valid code
- ✅ LLM repair as last resort

### 2.2 Schema Validation (Pre-Mypy)

**New**: `agents/e/validator.py` - Fast, early validation

```python
class SchemaValidator:
    """
    Validate code structure before expensive type checking.

    Catches common errors that mypy would catch, but faster.
    """

    def validate(self, code: str, module: CodeModule) -> ValidationReport:
        """Validate code structure and common patterns."""
        tree = ast.parse(code)
        issues = []

        # 1. Check all classes have complete __init__ or dataclass decorator
        issues.extend(self._check_class_constructors(tree))

        # 2. Check all function signatures have type annotations
        issues.extend(self._check_type_annotations(tree))

        # 3. Check imports are valid
        issues.extend(self._check_imports(tree, module.path.parent))

        # 4. Check for common type errors (generic params, etc.)
        issues.extend(self._check_common_type_errors(tree))

        # 5. Check for incomplete code (pass statements, TODO comments)
        issues.extend(self._check_completeness(tree))

        return ValidationReport(
            is_valid=len(issues) == 0,
            issues=issues,
            severity=self._max_severity(issues)
        )

    def _check_class_constructors(self, tree: ast.Module) -> list[Issue]:
        """Check all classes have valid constructors."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_init = any(
                    isinstance(n, ast.FunctionDef) and n.name == '__init__'
                    for n in node.body
                )

                has_dataclass = any(
                    isinstance(d, ast.Name) and d.id == 'dataclass'
                    for d in node.decorator_list
                )

                if not (has_init or has_dataclass):
                    issues.append(Issue(
                        severity="error",
                        message=f"Class {node.name} has no __init__ or @dataclass",
                        line=node.lineno
                    ))

        return issues

    def _check_common_type_errors(self, tree: ast.Module) -> list[Issue]:
        """Check for common type annotation errors."""
        issues = []

        for node in ast.walk(tree):
            # Check for incomplete generic types (Maybe[, Fix[A,B], etc.)
            if isinstance(node, ast.Subscript):
                # Get the source for this subscript
                try:
                    source = ast.unparse(node)

                    # Check for unclosed brackets
                    if source.count('[') != source.count(']'):
                        issues.append(Issue(
                            severity="error",
                            message=f"Incomplete generic type: {source}",
                            line=node.lineno
                        ))

                    # Check for wrong number of type params
                    known_types = {
                        'Agent': 2,  # Agent[A, B]
                        'Fix': 1,    # Fix[A]
                        'Result': 1, # Result[A]
                        # ... etc
                    }

                    if isinstance(node.value, ast.Name):
                        expected_params = known_types.get(node.value.id)
                        if expected_params:
                            actual_params = self._count_type_params(node.slice)
                            if actual_params != expected_params:
                                issues.append(Issue(
                                    severity="error",
                                    message=f"{node.value.id} expects {expected_params} type params, got {actual_params}",
                                    line=node.lineno
                                ))
                except Exception:
                    pass

        return issues
```

**Key features**:
- ✅ Catches type errors before mypy (faster feedback)
- ✅ Checks for incomplete constructors
- ✅ Validates generic type parameter counts
- ✅ Detects incomplete code (TODO, pass, etc.)

### 2.3 Incremental Repair

**New**: `agents/e/repair.py` - Attempt to fix common issues

```python
class CodeRepairer:
    """
    Attempt to repair common code generation errors.

    Uses AST manipulation + heuristics.
    """

    def repair(self, code: str, validation_report: ValidationReport) -> RepairResult:
        """Attempt to repair validation issues."""
        tree = ast.parse(code)

        # Categorize issues by repairability
        repairable = [i for i in validation_report.issues if self._can_repair(i)]
        unrepairable = [i for i in validation_report.issues if not self._can_repair(i)]

        if not repairable:
            return RepairResult(success=False, unrepairable=unrepairable)

        # Apply repairs
        for issue in repairable:
            if issue.category == "missing_import":
                tree = self._add_missing_import(tree, issue)
            elif issue.category == "incomplete_generic":
                tree = self._fix_generic_type(tree, issue)
            elif issue.category == "missing_default":
                tree = self._add_default_value(tree, issue)
            # ... more repair strategies

        # Regenerate code
        repaired_code = ast.unparse(tree)

        # Validate repaired code
        new_report = SchemaValidator().validate(repaired_code, ...)

        return RepairResult(
            success=new_report.is_valid,
            code=repaired_code,
            repairs_applied=repairable,
            remaining_issues=new_report.issues
        )

    def _add_missing_import(self, tree: ast.Module, issue: Issue) -> ast.Module:
        """Add a missing import to the AST."""
        # Infer the import from the undefined name
        name = issue.metadata['name']
        import_source = self._infer_import_source(name)

        if import_source:
            import_node = ast.ImportFrom(
                module=import_source,
                names=[ast.alias(name=name, asname=None)],
                level=0
            )
            tree.body.insert(0, import_node)

        return tree

    def _fix_generic_type(self, tree: ast.Module, issue: Issue) -> ast.Module:
        """Fix incomplete generic type annotations."""
        # Example: Maybe[ → Maybe[str]
        # Use heuristics or context to infer missing type param

        line_no = issue.line
        # Find the subscript node at this line
        for node in ast.walk(tree):
            if hasattr(node, 'lineno') and node.lineno == line_no:
                if isinstance(node, ast.Subscript):
                    # Attempt repair based on context
                    node.slice = self._infer_missing_type_param(node)

        return tree
```

**Key features**:
- ✅ Automatic repair of common errors
- ✅ AST-based (not string manipulation)
- ✅ Heuristic-based inference
- ✅ Validation after repair

---

## Layer 3: Recovery & Learning

### 3.1 Retry with Refinement

**New**: `agents/e/retry.py` - Intelligent retry logic

```python
class RetryStrategy:
    """
    Retry failed experiments with refined prompts.

    Learns from failure and adjusts approach.
    """

    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    async def retry_with_refinement(
        self,
        experiment: Experiment,
        failure_reason: str,
        context: PromptContext
    ) -> Optional[Experiment]:
        """Retry experiment with refined prompt based on failure."""

        for attempt in range(self.max_retries):
            # Refine prompt based on failure
            refined_prompt = self._refine_prompt(
                original_hypothesis=experiment.hypothesis,
                failure_reason=failure_reason,
                attempt=attempt,
                context=context
            )

            # Generate new experiment with refined prompt
            new_experiment = await self._generate_experiment(refined_prompt, context)

            # Validate
            validation = SchemaValidator().validate(
                new_experiment.improvement.code,
                experiment.module
            )

            if validation.is_valid:
                return new_experiment

            # Update failure reason for next iteration
            failure_reason = self._summarize_issues(validation.issues)

        return None  # All retries exhausted

    def _refine_prompt(
        self,
        original_hypothesis: str,
        failure_reason: str,
        attempt: int,
        context: PromptContext
    ) -> str:
        """Refine prompt based on failure reason."""

        # Categorize failure
        if "syntax error" in failure_reason.lower():
            constraint = """
CRITICAL: Previous attempt had syntax errors.
- Ensure all brackets/parens/quotes are closed
- Validate Python syntax before returning
- Do not use placeholder code (TODO, pass, ...)
"""
        elif "type error" in failure_reason.lower():
            constraint = f"""
CRITICAL: Previous attempt had type errors.
- Error details: {failure_reason}
- Double-check all type annotations
- Ensure generic types have correct parameter counts
- Preserve existing type signatures from original code
"""
        elif "missing import" in failure_reason.lower():
            constraint = """
CRITICAL: Previous attempt had missing imports.
- Include ALL necessary imports at the top
- Copy imports from original code if unsure
- Check that imported names match usage
"""
        else:
            constraint = f"""
CRITICAL: Previous attempt failed validation.
- Failure reason: {failure_reason}
- Address this specific issue
"""

        return f"""
{original_hypothesis}

## Previous Attempt Failed (Attempt {attempt + 1}/{self.max_retries})

{constraint}

## Requirements (MUST FOLLOW)
{build_improvement_prompt(original_hypothesis, context, "fix")}
"""
```

**Key features**:
- ✅ Failure-aware prompt refinement
- ✅ Multiple retry attempts with increasing specificity
- ✅ Categorizes failures to adjust strategy
- ✅ Gives up after max retries (avoids infinite loops)

### 3.2 Fallback Strategies

**New**: When experiments fail, try simpler approaches

```python
class FallbackStrategy:
    """
    When primary improvement fails, try progressively simpler approaches.

    Strategy waterfall:
    1. Original hypothesis (full improvement)
    2. Minimal version (single function/class)
    3. Type-only fix (just add/fix type annotations)
    4. Comment-only (add documentation)
    5. Skip (record as "too complex")
    """

    async def try_with_fallback(
        self,
        original_experiment: Experiment,
        context: PromptContext
    ) -> Optional[Experiment]:
        """Try progressively simpler versions of improvement."""

        strategies = [
            self._try_minimal_version,
            self._try_type_only_fix,
            self._try_documentation_only,
        ]

        for strategy in strategies:
            result = await strategy(original_experiment, context)
            if result and result.status == ExperimentStatus.PASSED:
                return result

        # All fallbacks failed
        return None

    async def _try_minimal_version(
        self,
        experiment: Experiment,
        context: PromptContext
    ) -> Optional[Experiment]:
        """Try a minimal version: improve just one function/class."""

        # Identify the most relevant symbol from original hypothesis
        target_symbol = self._identify_primary_target(
            experiment.hypothesis,
            context.ast_structure
        )

        if not target_symbol:
            return None

        # Generate minimal improvement prompt
        minimal_prompt = f"""
Improve ONLY the `{target_symbol}` function/class.

Original hypothesis: {experiment.hypothesis}

CONSTRAINTS:
- Change ONLY `{target_symbol}`
- Preserve all other code exactly as-is
- Ensure change is minimal and safe
- Return complete file with only `{target_symbol}` modified

This is a fallback after larger change failed.
Focus on making a small, safe improvement.
"""

        return await generate_experiment(minimal_prompt, context)
```

### 3.3 Error Memory & Learning

**New**: `agents/e/error_memory.py` - Track and learn from failures

```python
class ErrorMemory:
    """
    Track error patterns and learn what to avoid.

    Integrated with ImprovementMemory (agents/e/memory.py).
    """

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.error_patterns: dict[str, list[ErrorPattern]] = {}

    def record_failure(
        self,
        module: CodeModule,
        hypothesis: str,
        failure_type: str,
        failure_details: str
    ):
        """Record a failure for future learning."""

        pattern = ErrorPattern(
            module_category=module.category,
            hypothesis_type=self._categorize_hypothesis(hypothesis),
            failure_type=failure_type,
            failure_details=failure_details,
            timestamp=datetime.now()
        )

        key = f"{module.category}:{failure_type}"
        if key not in self.error_patterns:
            self.error_patterns[key] = []

        self.error_patterns[key].append(pattern)
        self._persist()

    def get_warnings_for_module(self, module: CodeModule) -> list[str]:
        """Get warnings based on past failures for this module type."""

        warnings = []
        key_prefix = f"{module.category}:"

        for key, patterns in self.error_patterns.items():
            if key.startswith(key_prefix):
                if len(patterns) >= 3:  # Pattern seen 3+ times
                    failure_type = key.split(':')[1]
                    common_detail = self._find_common_pattern(patterns)

                    warnings.append(f"""
⚠️ COMMON FAILURE for {module.category} modules:
   Type: {failure_type}
   Pattern: {common_detail}
   Occurrences: {len(patterns)}

   AVOID THIS in your improvement.
""")

        return warnings

    def _find_common_pattern(self, patterns: list[ErrorPattern]) -> str:
        """Find common substring in failure details."""
        if not patterns:
            return ""

        # Simple heuristic: most common error message substring
        from collections import Counter

        words = []
        for p in patterns:
            words.extend(p.failure_details.split())

        common_words = Counter(words).most_common(5)
        return ' '.join(word for word, _ in common_words)
```

**Integration**: Add error memory warnings to prompts

```python
def build_improvement_prompt_with_memory(
    hypothesis: str,
    context: PromptContext,
    error_memory: ErrorMemory
) -> str:
    """Build prompt with error memory warnings."""

    base_prompt = build_improvement_prompt(hypothesis, context, "refactor")

    warnings = error_memory.get_warnings_for_module(context.module)

    if warnings:
        warning_section = f"""
## ⚠️ COMMON PITFALLS (Learn from past failures)

{chr(10).join(warnings)}

IMPORTANT: These errors have occurred multiple times on {context.module.category} modules.
Take extra care to avoid them in your improvement.
"""
        return warning_section + "\n\n" + base_prompt

    return base_prompt
```

---

## Implementation Roadmap

### Phase 2.5a: Prompt Improvements (Week 1)

**Goal**: Increase generation quality at source

- [ ] Create `agents/e/prompts.py` with rich context builders
- [ ] Add `PromptContext` with type annotations, pre-existing errors
- [ ] Implement `PreFlightChecker` for early module validation
- [ ] Add scaffolding examples to prompts (grep similar patterns)
- [ ] Update `EvolutionPipeline` to use new prompt system
- [ ] **Validation**: Measure syntax error rate before/after
- [ ] **Target**: <10% syntax errors (down from ~20-30%)

**Files to create**:
- `impl/claude/agents/e/prompts.py` (~300 lines)
- `impl/claude/agents/e/preflight.py` (~200 lines)

**Files to modify**:
- `impl/claude/agents/e/evolution.py` (integrate new prompts)
- `impl/claude/agents/e/experiment.py` (use PromptContext)

### Phase 2.5b: Parsing & Validation (Week 2)

**Goal**: Handle LLM output robustly

- [ ] Create `agents/e/parser.py` with multi-strategy parsing
- [ ] Implement `CodeParser` with 5 fallback strategies
- [ ] Create `agents/e/validator.py` with schema validation
- [ ] Implement `SchemaValidator` (pre-mypy checks)
- [ ] Create `agents/e/repair.py` with incremental repair
- [ ] Replace `extract_code()` with new parser in `experiment.py`
- [ ] **Validation**: Measure parse success rate before/after
- [ ] **Target**: >95% parse success (up from ~70%)

**Files to create**:
- `impl/claude/agents/e/parser.py` (~400 lines)
- `impl/claude/agents/e/validator.py` (~300 lines)
- `impl/claude/agents/e/repair.py` (~250 lines)

**Files to modify**:
- `impl/claude/agents/e/experiment.py` (use new parser)
- `impl/claude/agents/e/__init__.py` (export new components)

### Phase 2.5c: Recovery & Learning (Week 3)

**Goal**: Gracefully handle failures, learn from patterns

- [ ] Create `agents/e/retry.py` with intelligent retry logic
- [ ] Implement `RetryStrategy` with failure-aware refinement
- [ ] Create `agents/e/fallback.py` with progressive simplification
- [ ] Implement `FallbackStrategy` (minimal → type-only → docs)
- [ ] Create `agents/e/error_memory.py` for pattern learning
- [ ] Integrate `ErrorMemory` with prompts (add warnings)
- [ ] Update `EvolutionPipeline` to use retry/fallback
- [ ] **Validation**: Measure incorporation rate before/after
- [ ] **Target**: >90% incorporation rate (up from ~30-50%)

**Files to create**:
- `impl/claude/agents/e/retry.py` (~250 lines)
- `impl/claude/agents/e/fallback.py` (~200 lines)
- `impl/claude/agents/e/error_memory.py` (~300 lines)

**Files to modify**:
- `impl/claude/agents/e/evolution.py` (orchestrate retry/fallback)
- `impl/claude/agents/e/memory.py` (integrate with error_memory)

### Phase 2.5d: Testing & Refinement (Week 4)

**Goal**: Validate improvements, iterate

- [ ] Create test suite for each new component
- [ ] Run evolution on full codebase with new system
- [ ] Measure success metrics (syntax errors, parse rate, incorporation rate)
- [ ] Analyze remaining failure modes
- [ ] Refine prompts/parsers/validators based on data
- [ ] Document new components
- [ ] **Validation**: Full evolution run with >90% success
- [ ] **Target**: 0 regressions, improved reliability

---

## Success Metrics

### Before (Current State)
- **Syntax error rate**: ~20-30%
- **Parse success rate**: ~70%
- **Incorporation rate**: ~30-50%
- **Retry strategy**: None (fail once = give up)
- **Error learning**: None (same mistakes repeated)

### After (Target State)
- **Syntax error rate**: <10% (3x better)
- **Parse success rate**: >95% (1.4x better)
- **Incorporation rate**: >90% (2-3x better)
- **Retry strategy**: 3 attempts with refinement
- **Error learning**: Active (warnings in prompts)

### Measurement Approach

```python
class EvolutionMetrics:
    """Track evolution pipeline metrics."""

    def __init__(self):
        self.total_hypotheses = 0
        self.syntax_errors = 0
        self.parse_failures = 0
        self.validation_failures = 0
        self.test_failures = 0
        self.incorporations = 0
        self.retries_attempted = 0
        self.retries_succeeded = 0
        self.fallbacks_used = 0

    def report(self) -> str:
        """Generate metrics report."""
        return f"""
## Evolution Pipeline Metrics

**Generation Quality**:
- Syntax error rate: {self.syntax_errors / self.total_hypotheses:.1%}
- Parse success rate: {(self.total_hypotheses - self.parse_failures) / self.total_hypotheses:.1%}

**Validation**:
- Schema validation pass rate: {(self.total_hypotheses - self.validation_failures) / self.total_hypotheses:.1%}
- Test pass rate: {(self.total_hypotheses - self.test_failures) / self.total_hypotheses:.1%}

**Incorporation**:
- Incorporation rate: {self.incorporations / self.total_hypotheses:.1%}

**Recovery**:
- Retry success rate: {self.retries_succeeded / max(1, self.retries_attempted):.1%}
- Fallback usage: {self.fallbacks_used} times
"""
```

---

## Testing Strategy

### Unit Tests

```python
# Test parser robustness
def test_parser_handles_malformed_markdown():
    parser = CodeParser()

    # Missing code fence close
    result = parser.parse("```python\nprint('hello')\n")
    assert result.success

    # Extra markdown noise
    result = parser.parse("Here's the code:\n```python\nprint('hello')\n```\nThat's it!")
    assert result.success

    # Incomplete generic type in metadata
    result = parser.parse("""
## METADATA
{"description": "Fix", "type": "Maybe["}

## CODE
```python
def foo(): pass
```
""")
    assert result.success  # Should still extract code

# Test validator catches errors
def test_validator_catches_incomplete_types():
    validator = SchemaValidator()

    code = """
class Foo(Agent[A,]):  # Incomplete generic
    pass
"""

    report = validator.validate(code, mock_module)
    assert not report.is_valid
    assert any("generic type" in i.message.lower() for i in report.issues)

# Test retry refines prompts
def test_retry_refines_based_on_failure():
    strategy = RetryStrategy(max_retries=2)

    # Simulate syntax error failure
    refined = strategy._refine_prompt(
        "Improve function foo",
        failure_reason="Syntax error: unclosed bracket on line 10",
        attempt=0,
        context=mock_context
    )

    # Should add syntax-specific constraints
    assert "syntax" in refined.lower()
    assert "bracket" in refined.lower()
```

### Integration Tests

```python
# Test full pipeline on known-problematic module
async def test_evolution_on_problematic_module():
    """Test that new reliability features handle known-hard cases."""

    # Use a module that previously failed often
    module = CodeModule(
        name="base",
        category="runtime",
        path=Path("impl/claude/runtime/base.py")
    )

    pipeline = EvolutionPipeline(config=test_config)
    report = await pipeline.evolve_module(module)

    # Should achieve >80% incorporation rate even on hard module
    incorporation_rate = len(report.incorporated) / len(report.experiments)
    assert incorporation_rate > 0.8, f"Only {incorporation_rate:.1%} incorporated"

# Test error memory learns
async def test_error_memory_learns_patterns():
    memory = ErrorMemory(test_storage_path)

    # Record same failure 3 times
    for _ in range(3):
        memory.record_failure(
            module=mock_module,
            hypothesis="Add type hints",
            failure_type="type_error",
            failure_details="Maybe[ is incomplete generic type"
        )

    # Should generate warning
    warnings = memory.get_warnings_for_module(mock_module)
    assert len(warnings) > 0
    assert "Maybe[" in warnings[0] or "generic" in warnings[0].lower()
```

---

## Backward Compatibility

All changes are **additive** - existing evolution pipeline continues to work:

- `evolve.py` CLI unchanged
- Existing `agents/e/` modules extended, not replaced
- New components opt-in via config flags
- Gradual rollout: Phase 2.5a → 2.5b → 2.5c

### Migration Path

```python
# Old way (still works)
pipeline = EvolutionPipeline(config=EvolutionConfig(target="all"))

# New way (opt-in to reliability features)
pipeline = EvolutionPipeline(
    config=EvolutionConfig(
        target="all",
        enable_retry=True,        # Layer 3: Retry with refinement
        enable_fallback=True,     # Layer 3: Fallback strategies
        enable_error_memory=True, # Layer 3: Learn from failures
        enable_schema_validation=True,  # Layer 2: Pre-mypy validation
        enable_repair=True,       # Layer 2: Incremental repair
    )
)
```

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Slower evolution** (more validation) | Longer runs | Use fast pre-checks, parallel validation |
| **False positives** (over-zealous validation) | Good code rejected | Make validators configurable, log decisions |
| **Prompt bloat** (too much context) | Token limit exceeded | Prioritize context, truncate less relevant parts |
| **Complexity creep** | Harder to maintain | Keep each component <300 lines, clear interfaces |
| **Retry loops** (bad prompts never succeed) | Wasted LLM calls | Max retries = 3, fallback strategies |

---

## Open Questions

### 1. Should we use LLM for repair?

**Option A**: Use LLM to fix malformed code (expensive but flexible)
**Option B**: Use AST manipulation + heuristics (fast but limited)

**Recommendation**: Start with B, add A as fallback for complex cases.

### 2. How aggressive should retry be?

**Option A**: Retry every failure (may waste tokens on hard cases)
**Option B**: Only retry if validation suggests likely success

**Recommendation**: B - use pre-flight validation to decide if retry is worthwhile.

### 3. Should error memory be global or per-module?

**Option A**: Global (learn across all modules)
**Option B**: Per-module (avoid false pattern matches)

**Recommendation**: Per-category (e.g., "bootstrap", "agents", "runtime") - balance specificity and generalization.

---

## Conclusion

This plan addresses evolution pipeline reliability through a **three-layer approach**:

1. **Prompt Engineering**: Prevent errors at source with rich context, examples, constraints
2. **Robust Parsing**: Handle any LLM output with multi-strategy parsing, validation, repair
3. **Recovery & Learning**: Retry with refinement, fallback strategies, learn from failures

**Expected impact**:
- ✅ **3x better** syntax error rate (<10% from ~20-30%)
- ✅ **1.4x better** parse success rate (>95% from ~70%)
- ✅ **2-3x better** incorporation rate (>90% from ~30-50%)

**Implementation**: 4-week phased rollout, backward compatible, measurable at each phase.

**Next steps**: Begin Phase 2.5a (Prompt Improvements) - create `agents/e/prompts.py` and `PreFlightChecker`.
