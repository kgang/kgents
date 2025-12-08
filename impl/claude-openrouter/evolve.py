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
    python evolve.py [--target runtime|agents|bootstrap|all] [--dry-run] [--auto-apply] [--quick]

Flags:
    --dry-run: Preview improvements without applying
    --auto-apply: Automatically apply improvements that pass tests
    --quick: Skip dialectic synthesis for faster iteration
"""

import asyncio
import json
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

# Bootstrap imports
from bootstrap import (
    Judge,
    JudgeInput,
    Contradict,
    ContradictInput,
    Sublate,
    make_default_principles,
)
from bootstrap.types import (
    Agent,
    Tension,
    TensionMode,
    Verdict,
    VerdictType,
    HoldTension,
    Synthesis,
    ResolutionType,
)
from bootstrap.fix import Fix, FixResult, FixConfig

# Runtime
from runtime import ClaudeCLIRuntime
from runtime.base import LLMAgent, AgentContext, AgentResult

# Agents
from agents.b.hypothesis import HypothesisEngine, HypothesisInput
from agents.h.hegel import HegelAgent, DialecticInput, DialecticOutput


# ============================================================================
# Configuration
# ============================================================================

def log(msg: str = "", prefix: str = "") -> None:
    """Print with immediate flush for real-time output."""
    if prefix:
        print(f"{prefix} {msg}", flush=True)
    else:
        print(msg, flush=True)


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


# ============================================================================
# Types
# ============================================================================

class ExperimentStatus(Enum):
    """Status of an experiment."""
    PENDING = "pending"
    GENERATING = "generating"
    TESTING = "testing"
    PASSED = "passed"
    FAILED = "failed"
    SYNTHESIZING = "synthesizing"
    INCORPORATED = "incorporated"
    REJECTED = "rejected"


@dataclass
class CodeModule:
    """A module to evolve."""
    name: str
    path: Path
    content: str
    category: str


@dataclass
class Improvement:
    """A proposed improvement to a module."""
    description: str
    rationale: str
    new_content: str
    improvement_type: str  # "refactor", "fix", "feature", "test"
    confidence: float


@dataclass
class Experiment:
    """An experiment applying an improvement."""
    id: str
    module: CodeModule
    improvement: Improvement
    status: ExperimentStatus = ExperimentStatus.PENDING
    test_results: Optional[dict] = None
    synthesis: Optional[DialecticOutput] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EvolutionReport:
    """Final report of the evolution process."""
    experiments: list[Experiment]
    incorporated: list[Experiment]
    rejected: list[Experiment]
    held: list[Experiment]
    summary: str


# ============================================================================
# CodeImprover: LLM Agent for generating improvements
# ============================================================================

@dataclass
class ImproverInput:
    """Input for the code improver."""
    module: CodeModule
    hypothesis: str  # Single hypothesis to explore
    constraints: list[str]


@dataclass
class ImproverOutput:
    """Output from the code improver."""
    improvement: Improvement  # Single improvement per invocation


class CodeImprover(LLMAgent[ImproverInput, ImproverOutput]):
    """
    LLM Agent that generates concrete code improvements.

    Takes a SINGLE hypothesis and produces ONE concrete improvement.
    Composable: call multiple times for multiple improvements.
    """

    def __init__(self, temperature: float = 0.7):
        self._temperature = temperature

    @property
    def name(self) -> str:
        return "CodeImprover"

    def build_prompt(self, input: ImproverInput) -> AgentContext:
        system_prompt = """You are a code improvement agent for kgents, a spec-first agent framework.

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
{"description": "Brief description", "rationale": "Why", "improvement_type": "refactor|fix|feature|test", "confidence": 0.8}

## CODE
```python
# Complete file content here
```

CRITICAL:
- METADATA section contains simple JSON (no code, no newlines in strings)
- CODE section contains the complete Python file in a markdown block
- Generate ONE focused improvement per invocation
- Don't make changes that require external dependencies not already imported
- Preserve existing functionality unless explicitly improving it"""

        user_prompt = f"""Analyze this module and generate ONE improvement based on the hypothesis:

MODULE: {input.module.name}
CATEGORY: {input.module.category}
PATH: {input.module.path}

CURRENT CODE:
```python
{input.module.content}
```

HYPOTHESIS TO EXPLORE:
{input.hypothesis}

CONSTRAINTS:
{chr(10).join(f"- {c}" for c in input.constraints)}

Generate ONE concrete improvement. Return ONLY valid JSON."""

        return AgentContext(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=self._temperature,
            max_tokens=16000,  # Large enough for ~30k char files
        )

    def parse_response(self, response: str) -> ImproverOutput:
        """
        Parse two-section response: METADATA (JSON) + CODE (markdown block).

        This format avoids JSON escaping issues for code.
        """
        import re

        # Extract METADATA section
        metadata_match = re.search(
            r'##\s*METADATA\s*\n(.*?)(?=##\s*CODE|$)',
            response,
            re.DOTALL | re.IGNORECASE
        )

        # Extract CODE section (markdown block)
        # Use greedy matching anchored to end of response to handle code containing ```
        code_match = re.search(
            r'##\s*CODE\s*\n```(?:python)?\s*\n(.*)```\s*$',
            response,
            re.DOTALL | re.IGNORECASE
        )

        # Parse metadata JSON
        if metadata_match:
            metadata_text = metadata_match.group(1).strip()
            # Find JSON in metadata section
            json_match = re.search(r'\{[^}]+\}', metadata_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    # Fallback: extract fields with regex
                    data = self._extract_metadata_fields(metadata_text)
            else:
                data = self._extract_metadata_fields(metadata_text)
        else:
            # Legacy fallback: try robust_json_parse on whole response
            from runtime.base import robust_json_parse
            data = robust_json_parse(response, allow_partial=True)

        # Get code from CODE section or fallback
        if code_match:
            new_content = code_match.group(1)
        else:
            # Fallback: try to extract code after ## CODE even if truncated (no closing ```)
            truncated_match = re.search(
                r'##\s*CODE\s*\n```(?:python)?\s*\n(.*)',
                response,
                re.DOTALL | re.IGNORECASE
            )
            if truncated_match:
                # Take everything after the code block start
                new_content = truncated_match.group(1).rstrip('`').strip()
            elif 'new_content' in data:
                new_content = data['new_content']
            else:
                raise ValueError("No code content found in response")

        improvement = Improvement(
            description=data.get("description", ""),
            rationale=data.get("rationale", ""),
            new_content=new_content,
            improvement_type=data.get("improvement_type", "refactor"),
            confidence=float(data.get("confidence", 0.5)),
        )

        return ImproverOutput(improvement=improvement)

    def _extract_metadata_fields(self, text: str) -> dict:
        """Extract metadata fields using regex when JSON parsing fails."""
        import re
        result = {}

        # Extract each field
        patterns = {
            'description': r'"description"\s*:\s*"([^"]*)"',
            'rationale': r'"rationale"\s*:\s*"([^"]*)"',
            'improvement_type': r'"improvement_type"\s*:\s*"([^"]*)"',
            'confidence': r'"confidence"\s*:\s*([\d.]+)',
        }

        for field, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                result[field] = match.group(1)

        return result

    async def invoke(self, input: ImproverInput) -> ImproverOutput:
        """
        LLMAgents require a runtime for execution.

        Use: await runtime.execute(improver, input)
        """
        raise NotImplementedError(
            "CodeImprover requires a runtime. Use: await runtime.execute(improver, input)"
        )


# ============================================================================
# Validators: Test improvements before synthesis
# ============================================================================

class Validator:
    """Validates code improvements."""

    def __init__(self, base_path: Path):
        self._base_path = base_path

    async def validate_syntax(self, content: str) -> tuple[bool, str]:
        """Check if Python syntax is valid."""
        try:
            compile(content, "<string>", "exec")
            return True, "Syntax OK"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

    async def validate_types(self, path: Path, content: str) -> tuple[bool, str]:
        """Run mypy type checking on the content."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["python", "-m", "mypy", temp_path, "--ignore-missing-imports", "--no-error-summary"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            # Check for actual errors in output, not just return code
            # mypy returns non-zero for many reasons (missing stubs, etc.)
            output = (result.stdout + result.stderr).strip()

            # Filter out non-error lines
            error_lines = [
                line for line in output.split('\n')
                if line and ': error:' in line
            ]

            if not error_lines:
                return True, "Type check passed"
            else:
                return False, f"Type errors:\n" + "\n".join(error_lines[:5])  # Limit to 5 errors
        except FileNotFoundError:
            return True, "mypy not installed, skipping type check"
        except subprocess.TimeoutExpired:
            return False, "Type check timed out"
        except Exception as e:
            # Don't fail on mypy issues - it's optional
            return True, f"Type check skipped: {e}"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def validate_imports(self, content: str) -> tuple[bool, str]:
        """Check if all imports are resolvable."""
        # Write to temp file and try to import
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            result = subprocess.run(
                ["python", "-c", f"import ast; ast.parse(open('{temp_path}').read())"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return True, "Imports OK (AST check)"
        except Exception as e:
            return False, f"Import error: {e}"
        finally:
            Path(temp_path).unlink(missing_ok=True)

    async def validate_all(
        self,
        path: Path,
        content: str,
        config: EvolveConfig
    ) -> tuple[bool, dict]:
        """Run all validators."""
        results = {}

        # Syntax is always required
        ok, msg = await self.validate_syntax(content)
        results["syntax"] = {"passed": ok, "message": msg}
        if not ok:
            return False, results

        # Type check if configured
        if config.require_type_check:
            ok, msg = await self.validate_types(path, content)
            results["types"] = {"passed": ok, "message": msg}
            if not ok:
                return False, results

        # Import check
        ok, msg = await self.validate_imports(content)
        results["imports"] = {"passed": ok, "message": msg}
        if not ok:
            return False, results

        return True, results


# ============================================================================
# Git Integration: Safe experimentation
# ============================================================================

class GitSafety:
    """Git operations for safe experimentation."""

    def __init__(self, repo_path: Path):
        self._repo_path = repo_path

    def _run_git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self._repo_path), *args],
            capture_output=True,
            text=True,
        )

    def is_clean(self) -> bool:
        """Check if working tree is clean."""
        result = self._run_git("status", "--porcelain")
        return result.stdout.strip() == ""

    def current_branch(self) -> str:
        """Get current branch name."""
        result = self._run_git("branch", "--show-current")
        return result.stdout.strip()

    def create_experiment_branch(self, name: str) -> bool:
        """Create a new experiment branch."""
        result = self._run_git("checkout", "-b", name)
        return result.returncode == 0

    def checkout(self, branch: str) -> bool:
        """Checkout a branch."""
        result = self._run_git("checkout", branch)
        return result.returncode == 0

    def commit(self, message: str) -> bool:
        """Stage all and commit."""
        self._run_git("add", "-A")
        result = self._run_git("commit", "-m", message)
        return result.returncode == 0

    def diff_stat(self) -> str:
        """Get diff stat."""
        result = self._run_git("diff", "--stat")
        return result.stdout


# ============================================================================
# Evolution Pipeline
# ============================================================================

class EvolutionPipeline:
    """
    The main evolution pipeline.

    Compose: HypothesisEngine >> CodeImprover >> Validator >> Hegel >> Apply
    """

    def __init__(self, config: EvolveConfig):
        self._config = config
        self._base_path = Path(__file__).parent

        # Initialize components with verbose mode
        self._runtime = ClaudeCLIRuntime(timeout=300.0, max_retries=2, verbose=True)
        self._hypothesis_engine = HypothesisEngine(hypothesis_count=4, temperature=0.95)
        self._code_improver = CodeImprover(temperature=0.95)
        self._judge = Judge()
        self._hegel = HegelAgent()
        self._validator = Validator(self._base_path)
        self._git = GitSafety(self._base_path.parent.parent)  # Go up to repo root
        self._principles = make_default_principles()

        # Performance optimization: Cache AST analysis
        self._ast_cache: dict[str, list[str]] = {}

    def load_modules(self) -> list[CodeModule]:
        """Load Python modules from impl directory."""
        targets = {
            "runtime": ["runtime"],
            "agents": ["agents/a", "agents/b", "agents/c", "agents/h", "agents/k"],
            "bootstrap": ["bootstrap"],
            "meta": [],  # Special: root-level meta files
            "all": ["runtime", "agents/a", "agents/b", "agents/c", "agents/h", "agents/k", "bootstrap"],
        }

        modules: list[CodeModule] = []

        # Handle meta target (root-level files)
        if self._config.target == "meta":
            meta_files = ["evolve.py", "autopoiesis.py", "self_improve.py"]
            for filename in meta_files:
                py_file = self._base_path / filename
                if py_file.exists():
                    content = py_file.read_text()
                    modules.append(CodeModule(
                        name=py_file.stem,
                        path=py_file,
                        content=content,
                        category="meta",
                    ))
            return modules

        dirs = targets.get(self._config.target, targets["all"])

        for subdir in dirs:
            dir_path = self._base_path / subdir
            if not dir_path.exists():
                continue

            for py_file in dir_path.glob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                content = py_file.read_text()
                modules.append(CodeModule(
                    name=py_file.stem,
                    path=py_file,
                    content=content,
                    category=subdir.split("/")[0],
                ))

        return modules

    def _analyze_code_structure(self, module: CodeModule) -> list[str]:
        """Deep code analysis using AST parsing."""
        import ast
        observations = []

        try:
            tree = ast.parse(module.content)

            # Count different elements
            classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            async_functions = [n for n in functions if n in [x for x in ast.walk(tree) if isinstance(x, ast.AsyncFunctionDef)]]
            imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]

            # Exception handling
            try_blocks = [n for n in ast.walk(tree) if isinstance(n, ast.Try)]
            raises = [n for n in ast.walk(tree) if isinstance(n, ast.Raise)]

            # Type annotations
            annotated_args = sum(1 for f in functions for arg in getattr(f.args, 'args', []) if arg.annotation)
            total_args = sum(len(getattr(f.args, 'args', [])) for f in functions)

            observations.append(f"Structure: {len(classes)} classes, {len(functions)} functions ({len(async_functions)} async)")
            observations.append(f"Imports: {len(imports)} import statements")
            observations.append(f"Error handling: {len(try_blocks)} try blocks, {len(raises)} raises")

            if total_args > 0:
                type_coverage = (annotated_args / total_args) * 100
                observations.append(f"Type annotations: {type_coverage:.0f}% of function arguments")

            # Look for patterns
            if len(try_blocks) == 0 and len(raises) > 0:
                observations.append("⚠ Raises exceptions but has no error handling")

            if len(async_functions) > 0 and "asyncio" not in module.content:
                observations.append("⚠ Uses async but doesn't import asyncio")

        except SyntaxError:
            observations.append("⚠ Syntax error - cannot parse AST")

        return observations

    async def generate_hypotheses(self, module: CodeModule) -> list[str]:
        """Generate improvement hypotheses for a module."""
        # Deep structural analysis
        structural_obs = self._analyze_code_structure(module)

        # Additional pattern observations
        pattern_obs = []
        if "# TODO" in module.content:
            todos = [line.strip() for line in module.content.split('\n') if '# TODO' in line]
            pattern_obs.append(f"Has {len(todos)} TODO comments: {todos[0][:50] if todos else ''}")
        if "raise NotImplementedError" in module.content:
            pattern_obs.append("Contains NotImplementedError (incomplete implementation)")
        if '"""' not in module.content and "'''" not in module.content:
            pattern_obs.append("⚠ Missing module-level docstring")

        observations = [
            f"Module: {module.name} ({module.category})",
            f"Size: {len(module.content.splitlines())} lines",
        ] + structural_obs + pattern_obs

        try:
            result = await self._runtime.execute(
                self._hypothesis_engine,
                HypothesisInput(
                    observations=observations,
                    domain="software architecture",
                    question=f"What specific, actionable improvements would make {module.name} more robust, composable, and production-ready?",
                    constraints=[
                        "Focus on concrete, implementable changes",
                        "Agents are morphisms: A → B",
                        "Use Fix pattern for retries",
                        "Prioritize error handling and type safety",
                    ],
                )
            )
            hypotheses = [h.statement for h in result.output.hypotheses]
            # Log each hypothesis for visibility
            for i, h in enumerate(hypotheses, 1):
                log(f"   H{i}: {h[:100]}...", "      💡")
            return hypotheses
        except Exception as e:
            log(f"Hypothesis generation failed: {e}", "   ⚠️")
            return []

    async def generate_improvements(
        self,
        module: CodeModule,
        hypotheses: list[str]
    ) -> list[Improvement]:
        """
        Generate concrete code improvements in parallel.

        Calls CodeImprover once per hypothesis for composability.
        Each agent invocation produces ONE improvement.
        """
        improvements: list[Improvement] = []

        # Limit to max_improvements_per_module
        hypotheses_to_explore = hypotheses[:self._config.max_improvements_per_module]

        log(f"   Exploring {len(hypotheses_to_explore)} hypotheses in parallel...", "      🔬")

        # Create tasks for parallel execution
        async def generate_one(i: int, hypothesis: str) -> Optional[tuple[int, Improvement]]:
            try:
                result = await self._runtime.execute(
                    self._code_improver,
                    ImproverInput(
                        module=module,
                        hypothesis=hypothesis,
                        constraints=[
                            "kgents principles: tasteful, curated, composable",
                            "Agents are morphisms with clear A → B types",
                            "Use Fix for iteration/retry patterns",
                            "Don't introduce new dependencies",
                        ],
                    )
                )
                imp = result.output.improvement
                log(f"   ✓ H{i+1}: {imp.description[:70]}... (conf: {imp.confidence:.2f})", "      ")
                return (i, imp)
            except Exception as e:
                log(f"   ✗ H{i+1} failed: {str(e)[:50]}...", "      ")
                return None

        # Execute all improvement generations in parallel
        tasks = [generate_one(i, h) for i, h in enumerate(hypotheses_to_explore)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful improvements (preserving order)
        for result in results:
            if result and not isinstance(result, Exception):
                i, imp = result
                improvements.append(imp)

        return improvements

    async def test_improvement(
        self,
        module: CodeModule,
        improvement: Improvement
    ) -> tuple[bool, dict]:
        """Test an improvement for validity."""
        return await self._validator.validate_all(
            module.path,
            improvement.new_content,
            self._config
        )

    async def synthesize(
        self,
        module: CodeModule,
        improvement: Improvement
    ) -> DialecticOutput:
        """Use dialectic to synthesize improvement with current code."""
        return await self._hegel.invoke(DialecticInput(
            thesis=f"Current {module.name}: {module.content[:200]}...",
            antithesis=f"Proposed improvement: {improvement.description}",
            context={
                "module": module.name,
                "improvement_type": improvement.improvement_type,
                "confidence": improvement.confidence,
            }
        ))

    async def run_experiment(
        self,
        module: CodeModule,
        improvement: Improvement,
        experiment_id: str
    ) -> Experiment:
        """Run a single experiment."""
        experiment = Experiment(
            id=experiment_id,
            module=module,
            improvement=improvement,
        )

        # Stage 1: Test
        experiment.status = ExperimentStatus.TESTING
        log(f"Testing...", "      ")

        passed, results = await self.test_improvement(module, improvement)
        experiment.test_results = results

        if not passed:
            experiment.status = ExperimentStatus.FAILED
            experiment.error = str(results)
            log(f"FAILED: {results}", "      ❌")
            return experiment

        log(f"Tests passed", "      ✓")
        experiment.status = ExperimentStatus.PASSED

        # Stage 2: Synthesize (skip in quick mode)
        if not self._config.quick_mode:
            experiment.status = ExperimentStatus.SYNTHESIZING
            log(f"Synthesizing...", "      ")

            synthesis = await self.synthesize(module, improvement)
            experiment.synthesis = synthesis

            if synthesis.productive_tension:
                log(f"HELD: {synthesis.sublation_notes}", "      ⏸️")
                return experiment

            log(f"Synthesis: {synthesis.sublation_notes[:60]}...", "      ↑")
        else:
            log(f"Skipping synthesis (quick mode)", "      ⚡")

        return experiment

    async def incorporate(self, experiment: Experiment) -> bool:
        """Apply an experiment's improvement to the codebase."""
        if self._config.dry_run:
            log(f"DRY RUN: Would apply {experiment.improvement.description}", "   🔍")
            # Show a brief preview of changes
            old_lines = len(experiment.module.content.splitlines())
            new_lines = len(experiment.improvement.new_content.splitlines())
            delta = new_lines - old_lines
            log(f"         Lines: {old_lines} → {new_lines} ({delta:+d})", "         ")
            log(f"         Rationale: {experiment.improvement.rationale[:80]}...", "         ")
            return True

        # Write the new content
        experiment.module.path.write_text(experiment.improvement.new_content)
        experiment.status = ExperimentStatus.INCORPORATED
        log(f"Applied: {experiment.improvement.description}", "   ✅")

        return True

    async def evolve_module(self, module: CodeModule, module_idx: int, total_modules: int) -> list[Experiment]:
        """Evolve a single module through the full pipeline."""
        experiments: list[Experiment] = []
        start_time = time.time()

        log(f"\n{'='*60}")
        log(f"[{module_idx}/{total_modules}] EVOLVING: {module.name} ({module.category})")
        log(f"{'='*60}")

        # Generate hypotheses
        log(f"Generating hypotheses...", "   1.")
        hyp_start = time.time()
        hypotheses = await self.generate_hypotheses(module)
        hyp_time = time.time() - hyp_start
        if not hypotheses:
            log(f"No hypotheses generated, skipping", "      ")
            return experiments
        log(f"Generated {len(hypotheses)} hypotheses ({hyp_time:.1f}s)", "      ✓")

        # Generate improvements (parallel)
        log(f"Generating improvements (parallel)...", "   2.")
        imp_start = time.time()
        improvements = await self.generate_improvements(module, hypotheses)
        imp_time = time.time() - imp_start
        if not improvements:
            log(f"No improvements generated, skipping", "      ")
            return experiments
        log(f"Generated {len(improvements)} improvements ({imp_time:.1f}s)", "      ✓")

        # Run experiments
        log(f"Running experiments...", "   3.")
        for i, improvement in enumerate(improvements):
            exp_id = f"{module.name}-{i+1}"
            log(f"\n   [{exp_id}] {improvement.description[:70]}...")
            log(f"      Type: {improvement.improvement_type}, Confidence: {improvement.confidence:.2f}")

            exp_start = time.time()
            experiment = await self.run_experiment(module, improvement, exp_id)
            exp_time = time.time() - exp_start
            experiments.append(experiment)

            # Show result with timing
            if experiment.status == ExperimentStatus.PASSED:
                log(f"      Result: PASSED ({exp_time:.1f}s)", "      ")
            elif experiment.status == ExperimentStatus.FAILED:
                log(f"      Result: FAILED ({exp_time:.1f}s)", "      ")

        total_time = time.time() - start_time
        log(f"\n   Module completed in {total_time:.1f}s ({len(experiments)} experiments)")

        return experiments

    async def run(self) -> EvolutionReport:
        """Run the full evolution process."""
        log("="*60)
        log("KGENTS EVOLUTION")
        log(f"Target: {self._config.target}")
        log(f"Dry run: {self._config.dry_run}")
        log(f"Auto-apply: {self._config.auto_apply}")
        log(f"Quick mode: {self._config.quick_mode} {'⚡' if self._config.quick_mode else ''}")
        log("="*60)

        # Safety check
        if not self._config.dry_run and not self._git.is_clean():
            log("WARNING: Working tree is not clean. Use --dry-run or commit changes first.", "⚠️")
            if not self._config.auto_apply:
                log("Exiting. Use --auto-apply to proceed anyway.")
                return EvolutionReport(
                    experiments=[],
                    incorporated=[],
                    rejected=[],
                    held=[],
                    summary="Aborted: working tree not clean"
                )

        # Load modules
        modules = self.load_modules()
        log(f"\nLoaded {len(modules)} modules to evolve")

        # Evolve each module
        all_experiments: list[Experiment] = []
        for idx, module in enumerate(modules, 1):
            experiments = await self.evolve_module(module, idx, len(modules))
            all_experiments.extend(experiments)

        # Categorize results
        incorporated = [e for e in all_experiments if e.status == ExperimentStatus.INCORPORATED]
        rejected = [e for e in all_experiments if e.status == ExperimentStatus.FAILED]
        held = [e for e in all_experiments if e.synthesis and e.synthesis.productive_tension]
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
        log(f"\n{'='*60}")
        log("EVOLUTION SUMMARY")
        log(f"{'='*60}")
        log(f"Experiments run: {len(all_experiments)}")
        log(f"  Passed: {len(passed)}")
        log(f"  Failed: {len(rejected)}")
        log(f"  Held (productive tension): {len(held)}")
        log(f"  Incorporated: {len(incorporated)}")

        if passed and not self._config.auto_apply:
            log(f"\n{'-'*60}")
            log("READY TO INCORPORATE")
            log(f"{'-'*60}")
            for exp in passed:
                log(f"  [{exp.id}] {exp.improvement.description}")
            log(f"\nRun with --auto-apply to incorporate these improvements.")

        if held:
            log(f"\n{'-'*60}")
            log("HELD TENSIONS (require human judgment)")
            log(f"{'-'*60}")
            for exp in held:
                log(f"  [{exp.id}] {exp.improvement.description}")
                if exp.synthesis:
                    log(f"      Reason: {exp.synthesis.sublation_notes}")

        summary = f"Evolved {len(modules)} modules: {len(incorporated)} incorporated, {len(rejected)} rejected, {len(held)} held"

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

    return config


async def main():
    config = parse_args()

    if config.target not in ["runtime", "agents", "bootstrap", "meta", "all"]:
        log(f"Unknown target: {config.target}")
        log("Usage: python evolve.py [runtime|agents|bootstrap|meta|all] [--dry-run] [--auto-apply] [--quick]")
        log("")
        log("Flags:")
        log("  --dry-run     Preview improvements without applying")
        log("  --auto-apply  Automatically apply improvements that pass tests")
        log("  --quick       Skip dialectic synthesis for faster iteration")
        sys.exit(1)

    pipeline = EvolutionPipeline(config)
    report = await pipeline.run()

    log(f"\n{report.summary}")


if __name__ == "__main__":
    asyncio.run(main())
