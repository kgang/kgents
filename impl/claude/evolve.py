"""
evolve.py - Experimental Improvement Framework

A creative framework for experimentally testing, synthesizing, and
incorporating improvements into kgents.

Philosophy:
- Evolution through dialectic: thesis (current) + antithesis (improvement) → synthesis
- Experiments are cheap, production is sacred
- Fix pattern: iterate until stable
- Conflicts are data: log tensions, don't hide them

Stages:
1. EXPERIMENT - Generate code improvements via LLM
2. TEST - Validate syntax, types, tests pass
3. SYNTHESIZE - Dialectic resolution of improvements vs current
4. INCORPORATE - Apply changes with git safety

Usage:
    python evolve.py [--target runtime|agents|bootstrap|all] [FLAGS]

Flags:
    --dry-run: Preview improvements without applying
    --auto-apply: Automatically apply improvements that pass tests
    --quick: Skip dialectic synthesis for faster iteration
    --hypotheses=N: Number of hypotheses per module (default: 4)
    --max-improvements=N: Max improvements per module (default: 4)

Performance:
    Modules are processed in parallel for 2-5x speedup
    Large files (>500 lines) send previews to reduce token usage
    AST analysis is cached to avoid redundant parsing
"""

import ast
import asyncio
import json
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Match, Optional

# Bootstrap imports
from bootstrap import make_default_principles
from bootstrap.types import (
    Verdict,
    VerdictType,
    Synthesis,
    SublateInput,
    Tension,
    HoldTension,
)
from bootstrap.fix import Fix, FixResult, FixConfig
from bootstrap.sublate import Sublate

# Runtime
from runtime.base import LLMAgent, AgentContext, AgentResult

# Agents
from agents.b.hypothesis import HypothesisEngine, HypothesisInput
from agents.h.hegel import HegelAgent, DialecticInput, DialecticOutput


# ============================================================================
# Configuration
# ============================================================================

def log(msg: str = "", prefix: str = "", file: Optional[Any] = None) -> None:
    """Print with immediate flush for real-time output.

    Args:
        msg: Message to log
        prefix: Optional prefix (e.g., emoji)
        file: Optional file object to also write to
    """
    output = f"{prefix} {msg}" if prefix else msg
    print(output, flush=True)
    if file:
        file.write(output + "\n")
        file.flush()


@dataclass
class EvolveConfig:
    """Configuration for the evolution process."""
    target: str = "all"
    dry_run: bool = False
    auto_apply: bool = False
    max_improvements_per_module: int = 4
    experiment_branch_prefix: str = "evolve"
    require_tests_pass: bool = True
    require_type_check: bool = True
    quick_mode: bool = False  # Skip dialectic synthesis for speed
    hypothesis_count: int = 4  # Number of hypotheses to generate per module


@dataclass
class CodeModule:
    """A module in the codebase to evolve."""
    name: str
    category: str
    path: Path

    def __post_init__(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Module not found: {self.path}")


@dataclass
class CodeImprovement:
    """A proposed improvement to code."""
    description: str
    rationale: str
    improvement_type: str  # "refactor" | "fix" | "feature" | "test"
    code: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


class ExperimentStatus(Enum):
    """Status of an experiment."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    HELD = "held"  # Productive tension requiring human judgment


@dataclass
class Experiment:
    """A single experimental improvement."""
    id: str
    module: CodeModule
    improvement: CodeImprovement
    hypothesis: str  # The hypothesis that generated this experiment
    status: ExperimentStatus = ExperimentStatus.PENDING
    test_results: Optional[dict] = None
    verdict: Optional[Verdict] = None
    synthesis: Optional[Synthesis] = None
    error: Optional[str] = None


@dataclass
class EvolutionReport:
    """Summary of evolution run."""
    experiments: list[Experiment]
    incorporated: list[Experiment]
    rejected: list[Experiment]
    held: list[Experiment]
    summary: str


# ============================================================================
# Improvement Memory (Avoid Re-proposing Rejected Ideas)
# ============================================================================


@dataclass
class ImprovementRecord:
    """A record of a past improvement attempt."""
    module: str
    hypothesis_hash: str
    description: str
    outcome: str  # "accepted", "rejected", "held"
    timestamp: str
    rejection_reason: Optional[str] = None


class ImprovementMemory:
    """
    Persistent memory of past improvements.

    Stores accepted/rejected improvements to:
    1. Avoid re-proposing similar rejected ideas
    2. Track patterns of successful improvements
    3. Enable learning from history
    """

    def __init__(self, history_path: Optional[Path] = None):
        self._history_path = history_path or (
            Path(__file__).parent / ".evolve_logs" / "improvement_history.json"
        )
        self._records: list[ImprovementRecord] = []
        self._load()

    def _load(self) -> None:
        """Load history from disk."""
        if self._history_path.exists():
            try:
                with open(self._history_path) as f:
                    data = json.load(f)
                self._records = [
                    ImprovementRecord(**r) for r in data.get("records", [])
                ]
            except (json.JSONDecodeError, KeyError):
                self._records = []

    def _save(self) -> None:
        """Save history to disk."""
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "records": [
                {
                    "module": r.module,
                    "hypothesis_hash": r.hypothesis_hash,
                    "description": r.description,
                    "outcome": r.outcome,
                    "timestamp": r.timestamp,
                    "rejection_reason": r.rejection_reason,
                }
                for r in self._records
            ]
        }
        with open(self._history_path, "w") as f:
            json.dump(data, f, indent=2)

    def _hash_hypothesis(self, hypothesis: str) -> str:
        """Create a normalized hash of a hypothesis."""
        # Normalize: lowercase, remove extra whitespace, hash
        normalized = " ".join(hypothesis.lower().split())
        return f"{hash(normalized) & 0xFFFFFFFF:08x}"

    def was_rejected(self, module: str, hypothesis: str) -> Optional[ImprovementRecord]:
        """Check if a similar hypothesis was previously rejected."""
        h = self._hash_hypothesis(hypothesis)
        for r in self._records:
            if r.module == module and r.hypothesis_hash == h and r.outcome == "rejected":
                return r
        return None

    def was_recently_accepted(self, module: str, hypothesis: str, days: int = 7) -> bool:
        """Check if a similar improvement was recently accepted."""
        h = self._hash_hypothesis(hypothesis)
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        for r in self._records:
            if (r.module == module and
                r.hypothesis_hash == h and
                r.outcome == "accepted" and
                r.timestamp > cutoff):
                return True
        return False

    def record(
        self,
        module: str,
        hypothesis: str,
        description: str,
        outcome: str,
        rejection_reason: Optional[str] = None
    ) -> None:
        """Record an improvement attempt."""
        record = ImprovementRecord(
            module=module,
            hypothesis_hash=self._hash_hypothesis(hypothesis),
            description=description,
            outcome=outcome,
            timestamp=datetime.now().isoformat(),
            rejection_reason=rejection_reason,
        )
        self._records.append(record)
        self._save()

    def get_success_patterns(self, module: str) -> dict[str, int]:
        """Get counts of successful improvement types for a module."""
        patterns: dict[str, int] = {}
        for r in self._records:
            if r.module == module and r.outcome == "accepted":
                # Extract type from description if possible
                patterns[r.description[:50]] = patterns.get(r.description[:50], 0) + 1
        return patterns


# ============================================================================
# AST Analysis (Targeted Hypothesis Generation)
# ============================================================================


@dataclass
class CodeStructure:
    """Extracted structure of a Python module."""
    module_name: str
    classes: list[dict[str, Any]]
    functions: list[dict[str, Any]]
    imports: list[str]
    docstring: Optional[str]
    line_count: int
    complexity_hints: list[str]


def analyze_module_ast(path: Path) -> Optional[CodeStructure]:
    """
    Parse a Python module and extract its structure.

    Returns detailed information about classes, functions, and potential
    improvement targets.
    """
    try:
        with open(path) as f:
            source = f.read()
        tree = ast.parse(source)
    except (SyntaxError, FileNotFoundError):
        return None

    classes = []
    functions = []
    imports = []
    complexity_hints = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [
                {
                    "name": m.name,
                    "args": len(m.args.args),
                    "lineno": m.lineno,
                    "is_async": isinstance(m, ast.AsyncFunctionDef),
                }
                for m in node.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            classes.append({
                "name": node.name,
                "lineno": node.lineno,
                "methods": methods,
                "method_count": len(methods),
                "bases": [ast.unparse(b) for b in node.bases] if node.bases else [],
            })

            # Complexity hint: large classes
            if len(methods) > 10:
                complexity_hints.append(
                    f"Class {node.name} has {len(methods)} methods - consider splitting"
                )

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Skip methods (already captured in classes)
            if any(isinstance(p, ast.ClassDef) for p in ast.walk(tree)):
                parent_is_class = False
                for cls in ast.walk(tree):
                    if isinstance(cls, ast.ClassDef) and node in ast.walk(cls):
                        parent_is_class = True
                        break
                if parent_is_class:
                    continue

            func_info = {
                "name": node.name,
                "lineno": node.lineno,
                "args": [a.arg for a in node.args.args],
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "is_private": node.name.startswith("_"),
            }
            functions.append(func_info)

            # Complexity hint: long functions
            if hasattr(node, 'end_lineno') and node.end_lineno:
                length = node.end_lineno - node.lineno
                if length > 50:
                    complexity_hints.append(
                        f"Function {node.name} is {length} lines - consider refactoring"
                    )

        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            else:
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

    # Module-level docstring
    docstring: Optional[str] = None
    if (tree.body and
        isinstance(tree.body[0], ast.Expr) and
        isinstance(tree.body[0].value, ast.Constant)):
        raw_docstring = tree.body[0].value.value
        if isinstance(raw_docstring, str):
            docstring = raw_docstring[:200]

    return CodeStructure(
        module_name=path.stem,
        classes=classes,
        functions=functions,
        imports=imports,
        docstring=docstring,
        line_count=len(source.splitlines()),
        complexity_hints=complexity_hints,
    )


def generate_targeted_hypotheses(structure: CodeStructure, max_targets: int = 3) -> list[str]:
    """
    Generate targeted improvement hypotheses based on AST analysis.

    Instead of generic "improve this file", generates specific hypotheses
    like "Refactor the _extract_code method to reduce complexity".
    """
    hypotheses = []

    # Target large classes
    for cls in structure.classes:
        if cls["method_count"] > 8:
            hypotheses.append(
                f"Refactor class {cls['name']} ({cls['method_count']} methods) - "
                f"consider extracting cohesive method groups into separate classes"
            )
        if not cls["bases"]:
            hypotheses.append(
                f"Review class {cls['name']} - should it inherit from a Protocol or ABC?"
            )

    # Target complex functions
    for func in structure.functions:
        if len(func["args"]) > 5:
            hypotheses.append(
                f"Function {func['name']} has {len(func['args'])} parameters - "
                f"consider using a dataclass to group related arguments"
            )
        if func["is_private"] and not func["name"].startswith("__"):
            hypotheses.append(
                f"Private function {func['name']} - is it tested? Consider adding test cases"
            )

    # Add complexity hints as hypotheses
    for hint in structure.complexity_hints[:2]:
        hypotheses.append(hint)

    # Generic but structure-aware hypotheses
    if len(structure.imports) > 15:
        hypotheses.append(
            f"Module has {len(structure.imports)} imports - review for unused imports"
        )

    if structure.line_count > 400:
        hypotheses.append(
            f"Module is {structure.line_count} lines - consider splitting into submodules"
        )

    return hypotheses[:max_targets]


# ============================================================================
# Code-Based Principle Judging
# ============================================================================


def judge_code_improvement(
    improvement: "CodeImprovement",
    original_code: str,
    module_name: str,
) -> tuple[Verdict, list[str]]:
    """
    Judge a code improvement against the 7 principles.

    Returns (verdict, detailed_reasons).

    Unlike the bootstrap Judge which evaluates Agent objects, this evaluates
    code improvements using heuristics tailored for evolution.
    """
    reasons: list[str] = []
    scores: dict[str, float] = {}

    new_code = improvement.code

    # 1. TASTEFUL: Clear purpose, no bloat
    original_lines = len(original_code.splitlines())
    new_lines = len(new_code.splitlines())
    line_delta = new_lines - original_lines

    if line_delta > original_lines * 0.3:  # >30% increase
        reasons.append(f"⚠ Tasteful: +{line_delta} lines ({line_delta/original_lines*100:.0f}% increase) - may be bloat")
        scores["tasteful"] = 0.5
    elif line_delta < 0:
        reasons.append(f"✓ Tasteful: {abs(line_delta)} fewer lines - leaner")
        scores["tasteful"] = 1.0
    else:
        scores["tasteful"] = 0.8

    # 2. CURATED: Quality over quantity
    if improvement.confidence < 0.5:
        reasons.append(f"⚠ Curated: Low confidence ({improvement.confidence}) - uncertain value")
        scores["curated"] = 0.4
    else:
        scores["curated"] = improvement.confidence

    # 3. ETHICAL: No concerning patterns
    concerning = ["eval(", "exec(", "__import__", "os.system", "subprocess.call"]
    new_concerning = sum(1 for c in concerning if c in new_code and c not in original_code)
    if new_concerning > 0:
        reasons.append(f"⚠ Ethical: Introduces {new_concerning} potentially unsafe pattern(s)")
        scores["ethical"] = 0.3
    else:
        scores["ethical"] = 1.0

    # 4. JOYFUL: Readable, well-structured
    # Heuristic: docstrings, clear names
    has_docstrings = '"""' in new_code or "'''" in new_code
    scores["joyful"] = 0.8 if has_docstrings else 0.6

    # 5. COMPOSABLE: Follows agent patterns
    composable_patterns = ["async def", "def invoke", "Agent[", ">> "]
    pattern_count = sum(1 for p in composable_patterns if p in new_code)
    original_pattern_count = sum(1 for p in composable_patterns if p in original_code)

    if pattern_count >= original_pattern_count:
        scores["composable"] = 1.0
    else:
        reasons.append("⚠ Composable: May break composition patterns")
        scores["composable"] = 0.6

    # 6. HETERARCHICAL: Not creating god objects
    class_count = new_code.count("class ")
    if class_count > 5 and class_count > original_code.count("class ") + 2:
        reasons.append(f"⚠ Heterarchical: Adds {class_count - original_code.count('class ')} new classes")
        scores["heterarchical"] = 0.7
    else:
        scores["heterarchical"] = 1.0

    # 7. GENERATIVE: Could be regenerated from spec
    # Heuristic: code comments referencing spec
    spec_refs = ["spec/", "See ", "per spec", "as specified"]
    has_spec_ref = any(ref in new_code for ref in spec_refs)
    scores["generative"] = 1.0 if has_spec_ref else 0.7

    # Aggregate
    avg_score = sum(scores.values()) / len(scores)

    if avg_score >= 0.75 and scores["ethical"] >= 0.8:
        verdict = Verdict.accept(reasons or ["Passes all principle checks"])
    elif avg_score < 0.5 or scores["ethical"] < 0.5:
        verdict = Verdict.reject(reasons or ["Failed critical principle checks"])
    else:
        revisions = [r for r in reasons if r.startswith("⚠")]
        verdict = Verdict.revise(revisions, ["Needs refinement"])

    # Add score summary
    score_summary = ", ".join(f"{k}={v:.1f}" for k, v in scores.items())
    reasons.append(f"Scores: [{score_summary}] avg={avg_score:.2f}")

    return verdict, reasons


# ============================================================================
# Core Logic
# ============================================================================

class EvolutionPipeline:
    """Main pipeline for evolving code."""

    def __init__(self, config: EvolveConfig, runtime: Optional[LLMAgent] = None):
        """
        Initialize the evolution pipeline.

        Args:
            config: Evolution configuration
            runtime: Optional runtime to use. If None, creates ClaudeCLIRuntime.
        """
        self._config = config
        self._runtime = runtime
        self._principles = make_default_principles()

        # Agents (instantiated on first use)
        self._hypothesis_engine: Optional[HypothesisEngine] = None
        self._hegel: Optional[HegelAgent] = None
        self._sublate: Optional[Sublate] = None

        # Improvement memory for avoiding re-proposals
        self._memory = ImprovementMemory()

        # AST cache for module analysis
        self._ast_cache: dict[str, Optional[CodeStructure]] = {}

    def _get_runtime(self) -> LLMAgent:
        """Get or create the runtime instance."""
        if self._runtime is None:
            # Lazy import to avoid circular dependency
            from runtime import ClaudeCLIRuntime
            self._runtime = ClaudeCLIRuntime()
        return self._runtime

    def _get_hypothesis_engine(self) -> HypothesisEngine:
        """Lazy instantiation of hypothesis engine."""
        if self._hypothesis_engine is None:
            self._hypothesis_engine = HypothesisEngine()
        return self._hypothesis_engine


    def _get_hegel(self) -> HegelAgent:
        """Lazy instantiation of Hegel."""
        if self._hegel is None:
            self._hegel = HegelAgent(runtime=self._get_runtime())
        return self._hegel

    def _get_sublate(self) -> Sublate:
        """Lazy instantiation of Sublate for tension resolution."""
        if self._sublate is None:
            self._sublate = Sublate()
        return self._sublate

    def _get_ast_structure(self, module: CodeModule) -> Optional[CodeStructure]:
        """Get cached AST structure for a module."""
        key = str(module.path)
        if key not in self._ast_cache:
            self._ast_cache[key] = analyze_module_ast(module.path)
        return self._ast_cache[key]

    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes in git."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False

    def discover_modules(self) -> list[CodeModule]:
        """Discover modules to evolve based on target."""
        base = Path(__file__).parent
        modules = []

        if self._config.target in ["runtime", "all"]:
            runtime_dir = base / "runtime"
            for py_file in runtime_dir.glob("*.py"):
                if py_file.name != "__init__.py":
                    modules.append(CodeModule(
                        name=py_file.stem,
                        category="runtime",
                        path=py_file
                    ))

        if self._config.target in ["agents", "all"]:
            agents_dir = base / "agents"
            for letter_dir in agents_dir.iterdir():
                if letter_dir.is_dir() and not letter_dir.name.startswith("_"):
                    for py_file in letter_dir.glob("*.py"):
                        if py_file.name != "__init__.py":
                            modules.append(CodeModule(
                                name=py_file.stem,
                                category=f"agents/{letter_dir.name}",
                                path=py_file
                            ))

        if self._config.target in ["bootstrap", "all"]:
            bootstrap_dir = base / "bootstrap"
            for py_file in bootstrap_dir.glob("*.py"):
                if py_file.name != "__init__.py":
                    modules.append(CodeModule(
                        name=py_file.stem,
                        category="bootstrap",
                        path=py_file
                    ))

        if self._config.target in ["meta", "all"]:
            # Evolve evolve.py itself (meta!)
            modules.append(CodeModule(
                name="evolve",
                category="meta",
                path=base / "evolve.py"
            ))

        return modules

    def _get_code_preview(self, path: Path, max_lines: int = 200) -> str:
        """
        Get code preview for large files to reduce token usage.
        
        For files > 500 lines, return first max_lines with omission notice.
        """
        with open(path) as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        if total_lines <= 500:
            return "".join(lines)
        
        preview_lines = lines[:max_lines]
        omitted = total_lines - max_lines
        
        return (
            "".join(preview_lines) +
            f"\n... ({omitted} lines omitted) ...\n"
        )

    async def generate_hypotheses(self, module: CodeModule) -> list[str]:
        """Generate improvement hypotheses for a module.

        Uses AST analysis for targeted hypotheses and filters out
        previously rejected ideas using improvement memory.
        """
        log(f"[{module.name}] Generating hypotheses...")

        # Phase 1: AST-based targeted hypotheses
        ast_hypotheses: list[str] = []
        structure = self._get_ast_structure(module)
        if structure:
            ast_hypotheses = generate_targeted_hypotheses(
                structure,
                max_targets=max(2, self._config.hypothesis_count // 2)
            )
            if ast_hypotheses:
                log(f"[{module.name}] AST analysis found {len(ast_hypotheses)} targets:")
                for i, h in enumerate(ast_hypotheses, 1):
                    log(f"  🎯 AST{i}: {h}")

        # Phase 2: LLM-generated hypotheses (informed by AST)
        code_content = self._get_code_preview(module.path)

        # Include AST insights in the prompt
        ast_context = ""
        if structure:
            ast_context = f"""
AST ANALYSIS:
- Classes: {', '.join(c['name'] for c in structure.classes) or 'None'}
- Functions: {', '.join(f['name'] for f in structure.functions[:10]) or 'None'}
- Imports: {len(structure.imports)} total
- Complexity hints: {structure.complexity_hints[:2] if structure.complexity_hints else 'None'}
"""

        hypothesis_input = HypothesisInput(
            observations=[
                f"Module: {module.name}",
                f"Category: {module.category}",
                f"Path: {module.path}",
                ast_context,
                f"Code preview:\n{code_content}",
            ],
            domain=f"Code improvement for {module.category}/{module.name}",
            question=f"What are {self._config.hypothesis_count} specific improvements to make this code more robust, composable, and maintainable?",
            constraints=[
                "Agents are morphisms with clear A → B types",
                "Composable via >> operator",
                "Use Fix pattern for iteration/retry",
                "Conflicts are data - log tensions",
                "Tasteful: less is more",
            ],
        )

        llm_hypotheses: list[str] = []
        try:
            engine = self._get_hypothesis_engine()
            runtime = self._get_runtime()
            result = await runtime.execute(engine, hypothesis_input)

            hypotheses_output = result.output
            if not hasattr(hypotheses_output, 'hypotheses'):
                error_msg = str(hypotheses_output) if hasattr(hypotheses_output, 'message') else "Unknown error"
                log(f"[{module.name}] LLM hypothesis generation failed: {error_msg}")
            else:
                llm_hypotheses = [h.statement for h in hypotheses_output.hypotheses]

        except Exception as e:
            log(f"[{module.name}] LLM hypothesis generation error: {e}")

        # Combine AST and LLM hypotheses
        all_hypotheses = ast_hypotheses + llm_hypotheses

        # Phase 3: Filter out previously rejected hypotheses
        filtered_hypotheses: list[str] = []
        skipped_count = 0

        for h in all_hypotheses:
            rejection = self._memory.was_rejected(module.name, h)
            if rejection:
                log(f"[{module.name}] ⏭ Skipping previously rejected: {h[:60]}...")
                skipped_count += 1
                continue

            if self._memory.was_recently_accepted(module.name, h):
                log(f"[{module.name}] ⏭ Skipping recently accepted: {h[:60]}...")
                skipped_count += 1
                continue

            filtered_hypotheses.append(h)

        log(f"[{module.name}] Generated {len(filtered_hypotheses)} hypotheses ({skipped_count} filtered by memory)")
        for i, h in enumerate(filtered_hypotheses, 1):
            log(f"  💡 H{i}: {h}")

        return filtered_hypotheses

    async def experiment(self, module: CodeModule, hypothesis: str) -> Optional[Experiment]:
        """Run a single experiment: generate improvement from hypothesis."""
        exp_id = f"{module.name}_{hash(hypothesis) & 0xFFFF:04x}"
        log(f"[{exp_id}] Experimenting with hypothesis...")

        # Generate improvement code
        improvement = await self._generate_improvement(module, hypothesis)
        if not improvement:
            return None

        experiment = Experiment(
            id=exp_id,
            module=module,
            improvement=improvement,
            hypothesis=hypothesis,
        )

        # Rich logging for decision-making
        log(f"[{exp_id}] ✨ Generated Improvement:")
        log(f"  📋 Type: {improvement.improvement_type}")
        log(f"  🎯 Confidence: {improvement.confidence}")
        log(f"  💡 Description: {improvement.description}")
        log(f"  📝 Rationale: {improvement.rationale[:150]}...")
        return experiment

    async def _generate_improvement(
        self, module: CodeModule, hypothesis: str
    ) -> Optional[CodeImprovement]:
        """Generate code improvement using LLM."""
        code_content = self._get_code_preview(module.path)

        prompt = f"""You are a code improvement agent for kgents, a spec-first agent framework.

Your task is to generate ONE CONCRETE, WORKING code improvement based on a single hypothesis.

PRINCIPLES YOU MUST FOLLOW:
1. Agents are morphisms: A → B (clear input/output types)
2. Composable: Use >> for pipelines, wrap with Maybe/Either for error handling
3. Fix pattern: For retries, use the Fix agent pattern
4. Conflicts are data: Log tensions, don't swallow exceptions
5. Tasteful: Less is more. Don't over-engineer.
6. Generative: Code should be regenerable from spec

IMPROVEMENT TYPES:
- "refactor": Restructure without changing behavior
- "fix": Address a bug or tension
- "feature": Add missing capability
- "test": Add test coverage

OUTPUT FORMAT (TWO SECTIONS):

## METADATA
{{"description": "Brief description", "rationale": "Why", "improvement_type": "refactor|fix|feature|test", "confidence": 0.8}}

## CODE
```python
# Complete file content here
```

CRITICAL:
- METADATA section contains simple JSON (no code, no newlines in strings)
- CODE section contains the complete Python file in a markdown block
- Generate ONE focused improvement per invocation
- Don't make changes that require external dependencies not already imported
- Preserve existing functionality unless explicitly improving it

Analyze this module and generate ONE improvement based on the hypothesis:

MODULE: {module.name}
CATEGORY: {module.category}
PATH: {module.path}

CURRENT CODE (Preview - {len(code_content.splitlines())} lines total):
```python
{code_content}
```

HYPOTHESIS TO EXPLORE:
{hypothesis}

CONSTRAINTS:
- kgents principles: tasteful, curated, composable
- Agents are morphisms with clear A → B types
- Use Fix for iteration/retry patterns
- Don't introduce new dependencies

Generate ONE concrete improvement. Return ONLY valid JSON."""

        # Execute LLM to generate improvement
        try:
            runtime = self._get_runtime()
            # Create a simple agent context for the improvement generation
            context = AgentContext(
                system_prompt="You are a code improvement agent for kgents.",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=16000,
            )

            # Execute using raw_completion
            response_text, model = await runtime.raw_completion(context)

        except Exception as e:
            log(f"[{module.name}] Failed to generate improvement: {e}")
            return None

        # Parse response
        try:
            response = response_text.strip()

            # Extract METADATA section (flexible matching)
            metadata = self._extract_metadata(response, module.name)
            if metadata is None:
                return None

            # Extract CODE section (flexible matching)
            code = self._extract_code(response, module.name)
            if code is None:
                return None

            return CodeImprovement(
                description=metadata.get("description", "No description"),
                rationale=metadata.get("rationale", "No rationale"),
                improvement_type=metadata.get("improvement_type", "refactor"),
                code=code,
                confidence=metadata.get("confidence", 0.5),
                metadata=metadata,
            )

        except Exception as e:
            log(f"[{module.name}] Failed to parse LLM response: {e}")
            return None

    def _extract_metadata(self, response: str, module_name: str) -> Optional[dict]:
        """Extract metadata JSON from LLM response with flexible parsing."""
        # Try multiple patterns for metadata section
        patterns = [
            r"##\s*METADATA\s*\n(.*?)(?=##\s*CODE|$)",  # Standard format
            r"METADATA[:\s]*\n(.*?)(?=CODE|```python|$)",  # Relaxed format
            r"\{[^{}]*\"description\"[^{}]*\}",  # Direct JSON object
        ]

        metadata_text = None
        for pattern in patterns[:2]:  # Try section-based patterns first
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                metadata_text = match.group(1).strip()
                break

        # Extract JSON from metadata text (may have surrounding prose)
        if metadata_text:
            json_obj = self._extract_json_object(metadata_text)
            if json_obj:
                return json_obj

        # Fallback: find any JSON with required keys anywhere in response
        match = re.search(patterns[2], response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        log(f"[{module_name}] Could not extract metadata from response")
        return None

    def _extract_json_object(self, text: str) -> Optional[dict]:
        """Extract a JSON object from text that may have surrounding content."""
        # Find JSON object boundaries
        start = text.find("{")
        if start == -1:
            return None

        # Find matching closing brace (handle nested braces)
        depth = 0
        for i, char in enumerate(text[start:], start):
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    json_str = text[start : i + 1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # Try cleaning common issues
                        cleaned = self._clean_json_string(json_str)
                        try:
                            return json.loads(cleaned)
                        except json.JSONDecodeError:
                            return None
        return None

    def _clean_json_string(self, json_str: str) -> str:
        """Clean common JSON issues from LLM output."""
        # Remove trailing commas before } or ]
        cleaned = re.sub(r",\s*([}\]])", r"\1", json_str)

        # Fix unescaped newlines in string values
        # This is tricky - only fix within quoted strings
        def fix_newlines(match: re.Match) -> str:
            content = match.group(1)
            return '"' + content.replace("\n", "\\n") + '"'

        cleaned = re.sub(r'"([^"]*\n[^"]*)"', fix_newlines, cleaned)

        return cleaned

    def _extract_code(self, response: str, module_name: str) -> Optional[str]:
        """Extract Python code from LLM response with flexible parsing."""
        # Try multiple patterns for code extraction
        patterns = [
            # Standard markdown python block after CODE section
            r"##\s*CODE.*?```python\s*\n(.*?)```",
            # Any python block after CODE header
            r"CODE.*?```python\s*\n(.*?)```",
            # Python block with language tag variations
            r"```(?:python|py)\s*\n(.*?)```",
            # Generic code block (last resort)
            r"```\s*\n(.*?)```",
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                # Validate it looks like Python
                if self._looks_like_python(code):
                    return code

        log(f"[{module_name}] Could not extract code from response")
        return None

    def _looks_like_python(self, code: str) -> bool:
        """Quick heuristic check if code looks like valid Python."""
        if not code or len(code) < 20:
            return False

        # Check for common Python patterns
        python_indicators = [
            "import ", "from ", "def ", "class ", "async def ",
            "if __name__", "return ", "self.", "@dataclass", "@"
        ]
        return any(indicator in code for indicator in python_indicators)

    async def test(self, experiment: Experiment) -> bool:
        """Test an experimental improvement."""
        log(f"[{experiment.id}] Testing improvement...")
        experiment.status = ExperimentStatus.RUNNING

        # Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp:
            tmp.write(experiment.improvement.code)
            tmp_path = Path(tmp.name)

        try:
            # 1. Syntax check
            result = subprocess.run(
                ["python", "-m", "py_compile", str(tmp_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                experiment.status = ExperimentStatus.FAILED
                experiment.error = f"Syntax error: {result.stderr}"
                log(f"[{experiment.id}] ✗ Syntax error")
                return False

            # 2. Type check (if required)
            if self._config.require_type_check:
                result = subprocess.run(
                    [sys.executable, "-m", "mypy", str(tmp_path), "--ignore-missing-imports"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    experiment.status = ExperimentStatus.FAILED
                    experiment.error = f"Type error: {result.stdout}"
                    log(f"[{experiment.id}] ✗ Type check failed")
                    return False

            # 3. Run tests (if exist and required)
            if self._config.require_tests_pass:
                test_path = experiment.module.path.parent / f"test_{experiment.module.name}.py"
                if test_path.exists():
                    # Replace module with experimental version temporarily
                    original_code = experiment.module.path.read_text()
                    try:
                        experiment.module.path.write_text(experiment.improvement.code)
                        result = subprocess.run(
                            ["python", "-m", "pytest", str(test_path), "-v"],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode != 0:
                            experiment.status = ExperimentStatus.FAILED
                            experiment.error = f"Tests failed: {result.stdout}"
                            log(f"[{experiment.id}] ✗ Tests failed")
                            return False
                    finally:
                        experiment.module.path.write_text(original_code)

            experiment.status = ExperimentStatus.PASSED
            experiment.test_results = {"syntax": "✓", "types": "✓", "tests": "✓"}
            log(f"[{experiment.id}] ✓ All tests passed")
            return True

        except Exception as e:
            experiment.status = ExperimentStatus.FAILED
            experiment.error = str(e)
            log(f"[{experiment.id}] ✗ Error: {e}")
            return False

        finally:
            tmp_path.unlink()

    async def judge_experiment(self, experiment: Experiment) -> Verdict:
        """Judge if improvement should proceed using principle-based evaluation.

        Evaluates the improvement against the 7 kgents principles:
        tasteful, curated, ethical, joyful, composable, heterarchical, generative.
        """
        log(f"[{experiment.id}] Judging improvement against 7 principles...")

        # Read original code for comparison
        original_code = experiment.module.path.read_text()

        # Apply principle-based judging
        verdict, reasons = judge_code_improvement(
            improvement=experiment.improvement,
            original_code=original_code,
            module_name=experiment.module.name,
        )
        experiment.verdict = verdict

        # Log detailed judgment
        verdict_symbols = {
            VerdictType.ACCEPT: "✓",
            VerdictType.REVISE: "⚠",
            VerdictType.REJECT: "✗",
        }
        symbol = verdict_symbols.get(verdict.type, "?")

        log(f"[{experiment.id}] {symbol} {verdict.type.value.upper()}")
        for reason in reasons:
            log(f"    {reason}")

        return verdict

    async def synthesize(self, experiment: Experiment) -> Optional[Synthesis]:
        """Dialectic synthesis of improvement vs current code."""
        if self._config.quick_mode:
            log(f"[{experiment.id}] Skipping synthesis (quick mode)")
            return None

        log(f"[{experiment.id}] Synthesizing via dialectic...")

        current_code = experiment.module.path.read_text()

        dialectic_input = DialecticInput(
            thesis=current_code,
            antithesis=experiment.improvement.code,
            context={
                "module": experiment.module.name,
                "improvement": experiment.improvement.description,
                "rationale": experiment.improvement.rationale,
            },
        )

        hegel = self._get_hegel()
        result = await hegel(dialectic_input)

        if not result.success:
            log(f"[{experiment.id}] Synthesis failed: {result.error}")
            return None

        dialectic_output: DialecticOutput = result.output

        # Check for productive tension
        if dialectic_output.tensions:
            log(f"[{experiment.id}] ⚡ Productive tensions detected")
            for tension in dialectic_output.tensions:
                log(f"      {tension.description}")

            # Use Sublate to resolve
            sublate_agent = self._get_sublate()
            sublate_input = SublateInput(tensions=tuple(dialectic_output.tensions))
            sublate_result = await sublate_agent.invoke(sublate_input)

            # Check if result is HoldTension or Synthesis
            if isinstance(sublate_result, HoldTension):
                experiment.status = ExperimentStatus.HELD
                log(f"[{experiment.id}] ⊙ Tension held: {sublate_result.why_held}")
                return None
            elif isinstance(sublate_result, Synthesis):
                experiment.synthesis = sublate_result
                log(f"[{experiment.id}] ✓ Synthesized: {sublate_result.explanation}")
                return sublate_result

        log(f"[{experiment.id}] ✓ Synthesis complete")
        return experiment.synthesis

    async def incorporate(self, experiment: Experiment) -> bool:
        """Incorporate approved improvement into codebase."""
        log(f"[{experiment.id}] Incorporating improvement...")

        if self._config.dry_run:
            log(f"[{experiment.id}] (dry-run) Would write to {experiment.module.path}")
            return True

        try:
            # Write improved code
            experiment.module.path.write_text(experiment.improvement.code)

            # Git commit
            subprocess.run(
                ["git", "add", str(experiment.module.path)],
                check=True,
            )
            commit_msg = f"evolve: {experiment.improvement.description}\n\n{experiment.improvement.rationale}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                check=True,
            )

            log(f"[{experiment.id}] ✓ Incorporated and committed")
            return True

        except Exception as e:
            log(f"[{experiment.id}] ✗ Failed to incorporate: {e}")
            return False

    async def _process_module(self, module: CodeModule) -> list[Experiment]:
        """Process a single module (for parallel execution)."""
        log(f"\n{'='*60}")
        log(f"MODULE: {module.category}/{module.name}")
        log(f"{'='*60}")

        # Generate hypotheses
        hypotheses = await self.generate_hypotheses(module)
        if not hypotheses:
            return []

        # Run experiments for each hypothesis
        experiments = []
        for hypothesis in hypotheses[: self._config.max_improvements_per_module]:
            exp = await self.experiment(module, hypothesis)
            if exp:
                experiments.append(exp)

        # Test experiments
        for exp in experiments:
            passed = await self.test(exp)
            if not passed:
                # Record test failure in memory
                self._memory.record(
                    module=module.name,
                    hypothesis=exp.hypothesis,
                    description=exp.improvement.description,
                    outcome="rejected",
                    rejection_reason=exp.error or "Test failure",
                )
                continue

            # Judge using principle-based evaluation
            verdict = await self.judge_experiment(exp)
            if verdict.type == VerdictType.REJECT:
                exp.status = ExperimentStatus.FAILED
                # Record rejection in memory
                self._memory.record(
                    module=module.name,
                    hypothesis=exp.hypothesis,
                    description=exp.improvement.description,
                    outcome="rejected",
                    rejection_reason=verdict.reasoning,
                )
                continue

            # Synthesize (dialectic)
            await self.synthesize(exp)

            # Record outcome based on final status
            if exp.status == ExperimentStatus.HELD:
                self._memory.record(
                    module=module.name,
                    hypothesis=exp.hypothesis,
                    description=exp.improvement.description,
                    outcome="held",
                )
            elif exp.status == ExperimentStatus.PASSED:
                self._memory.record(
                    module=module.name,
                    hypothesis=exp.hypothesis,
                    description=exp.improvement.description,
                    outcome="accepted",
                )

        return experiments

    async def run(self) -> EvolutionReport:
        """Run the full evolution pipeline."""
        # Create log file
        log_dir = Path(__file__).parent / ".evolve_logs"
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = log_dir / f"evolve_{self._config.target}_{timestamp}.log"
        log_file = open(log_path, "w")

        log(f"{'='*60}")
        log(f"KGENTS EVOLUTION", file=log_file)
        log(f"Target: {self._config.target}", file=log_file)
        log(f"Dry run: {self._config.dry_run}", file=log_file)
        log(f"Auto-apply: {self._config.auto_apply}", file=log_file)
        log(f"Quick mode: {'True ⚡' if self._config.quick_mode else 'False'}", file=log_file)
        log(f"{'='*60}", file=log_file)
        log(f"⚠️ WARNING: Working tree is not clean. Use --dry-run or commit changes first." if self._has_uncommitted_changes() else "✓ Working tree is clean")
        log(f"", file=log_file)
        log(f"Loaded {len(self.discover_modules())} modules to evolve", file=log_file)
        log(f"Log file: {log_path}", prefix="📝")

        # Discover modules
        modules = self.discover_modules()
        log(f"\nDiscovered {len(modules)} modules to evolve")

        # Process modules in parallel
        start_time = time.time()
        results = await asyncio.gather(
            *[self._process_module(module) for module in modules],
            return_exceptions=True,
        )
        elapsed = time.time() - start_time

        # Flatten results
        all_experiments = []
        for result in results:
            if isinstance(result, list):
                all_experiments.extend(result)
            elif isinstance(result, Exception):
                log(f"⚠ Module processing error: {result}")

        log(f"\nProcessed {len(modules)} modules in {elapsed:.1f}s")

        # Collect results
        incorporated = []
        rejected = [e for e in all_experiments if e.status == ExperimentStatus.FAILED]
        held = [e for e in all_experiments if e.status == ExperimentStatus.HELD]
        passed = [e for e in all_experiments if e.status == ExperimentStatus.PASSED and e not in held]

        # Apply passed experiments if auto-apply
        if self._config.auto_apply and not self._config.dry_run:
            log(f"\n{'='*60}")
            log("INCORPORATING IMPROVEMENTS")
            log(f"{'='*60}")

            for experiment in passed:
                if await self.incorporate(experiment):
                    incorporated.append(experiment)

        # Summary
        log(f"\n{'='*60}", file=log_file)
        log("EVOLUTION SUMMARY", file=log_file)
        log(f"{'='*60}", file=log_file)
        log(f"Experiments run: {len(all_experiments)}", file=log_file)
        log(f"  Passed: {len(passed)}", file=log_file)
        log(f"  Failed: {len(rejected)}", file=log_file)
        log(f"  Held (productive tension): {len(held)}", file=log_file)
        log(f"  Incorporated: {len(incorporated)}", file=log_file)
        log(f"", file=log_file)

        if passed and not self._config.auto_apply:
            log(f"\n{'-'*60}", file=log_file)
            log("READY TO INCORPORATE", file=log_file)
            log(f"{'-'*60}", file=log_file)
            for exp in passed:
                log(f"  [{exp.id}] {exp.improvement.description}", file=log_file)
            log(f"\nRun with --auto-apply to incorporate these improvements.", file=log_file)

        if held:
            log(f"\n{'-'*60}", file=log_file)
            log("HELD TENSIONS (require human judgment)", file=log_file)
            log(f"{'-'*60}", file=log_file)
            for exp in held:
                log(f"  [{exp.id}] {exp.improvement.description}", file=log_file)
                if exp.synthesis:
                    log(f"      Reason: {exp.synthesis.sublation_notes}", file=log_file)

        # Final status banner (always visible even with tail)
        log(f"\n")
        log(f"╔{'═'*58}╗")
        log(f"║{' '*58}║")
        log(f"║  🎯 EVOLUTION COMPLETE - {self._config.target.upper():^32}  ║")
        log(f"║{' '*58}║")
        log(f"║  ✓ Passed: {len(passed):3d}   ✗ Failed: {len(rejected):3d}   ⏸ Held: {len(held):3d}   ✅ Applied: {len(incorporated):3d}  ║")
        log(f"║{' '*58}║")
        log(f"║  📝 Full log: {str(log_path)[-42:]:42}  ║")
        log(f"║{' '*58}║")
        log(f"╚{'═'*58}╝")
        log(f"")

        summary = f"Evolved {len(modules)} modules: {len(incorporated)} incorporated, {len(rejected)} rejected, {len(held)} held"

        # Save structured results for decision-making
        results_path = log_path.with_suffix('.json')
        results_data = {
            "timestamp": timestamp,
            "config": {
                "target": self._config.target,
                "dry_run": self._config.dry_run,
                "auto_apply": self._config.auto_apply,
                "quick_mode": self._config.quick_mode,
            },
            "summary": {
                "total_experiments": len(all_experiments),
                "passed": len(passed),
                "failed": len(rejected),
                "held": len(held),
                "incorporated": len(incorporated),
                "elapsed_seconds": elapsed,
            },
            "passed_experiments": [
                {
                    "id": exp.id,
                    "module": exp.module.name,
                    "category": exp.module.category,
                    "improvement": {
                        "type": exp.improvement.improvement_type,
                        "description": exp.improvement.description,
                        "rationale": exp.improvement.rationale,
                        "confidence": exp.improvement.confidence,
                    },
                    "status": exp.status.value,
                }
                for exp in passed
            ],
            "held_experiments": [
                {
                    "id": exp.id,
                    "module": exp.module.name,
                    "improvement": {
                        "description": exp.improvement.description,
                        "rationale": exp.improvement.rationale,
                    },
                    "synthesis_notes": exp.synthesis.sublation_notes if exp.synthesis else None,
                }
                for exp in held
            ],
        }

        with open(results_path, 'w') as f:
            json.dump(results_data, f, indent=2)

        log(f"📊 Decision data saved: {results_path}")

        # Close log file
        log_file.close()

        return EvolutionReport(
            experiments=all_experiments,
            incorporated=incorporated,
            rejected=rejected,
            held=held,
            summary=summary,
        )


# ============================================================================
# Main
# ============================================================================

def parse_args() -> EvolveConfig:
    """Parse command line arguments."""
    config = EvolveConfig()

    for arg in sys.argv[1:]:
        if arg.startswith("--target="):
            config.target = arg.split("=")[1]
        elif arg in ["runtime", "agents", "bootstrap", "meta", "all"]:
            config.target = arg
        elif arg == "--dry-run":
            config.dry_run = True
        elif arg == "--auto-apply":
            config.auto_apply = True
        elif arg == "--quick":
            config.quick_mode = True
        elif arg.startswith("--hypotheses="):
            config.hypothesis_count = int(arg.split("=")[1])
        elif arg.startswith("--max-improvements="):
            config.max_improvements_per_module = int(arg.split("=")[1])

    return config


async def main():
    config = parse_args()

    if config.target not in ["runtime", "agents", "bootstrap", "meta", "all"]:
        log(f"Unknown target: {config.target}")
        log("Usage: python evolve.py [runtime|agents|bootstrap|meta|all] [FLAGS]")
        log("")
        log("Flags:")
        log("  --dry-run              Preview improvements without applying")
        log("  --auto-apply           Automatically apply improvements that pass tests")
        log("  --quick                Skip dialectic synthesis for faster iteration")
        log("  --hypotheses=N         Number of hypotheses per module (default: 4)")
        log("  --max-improvements=N   Max improvements per module (default: 4)")
        sys.exit(1)

    pipeline = EvolutionPipeline(config)
    report = await pipeline.run()

    log(f"\n{report.summary}")


if __name__ == "__main__":
    asyncio.run(main())
