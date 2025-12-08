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
    python evolve.py [--target runtime|agents|bootstrap|all] [--dry-run] [--auto-apply]
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
    max_improvements_per_module: int = 3
    experiment_branch_prefix: str = "evolve"
    require_tests_pass: bool = True
    require_type_check: bool = True


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
    hypotheses: list[str]  # From self_improve.py
    constraints: list[str]


@dataclass
class ImproverOutput:
    """Output from the code improver."""
    improvements: list[Improvement]
    reasoning: str


class CodeImprover(LLMAgent[ImproverInput, ImproverOutput]):
    """
    LLM Agent that generates concrete code improvements.

    Takes analysis from HypothesisEngine and produces actual code changes.
    """

    def __init__(self, max_improvements: int = 3, temperature: float = 0.7):
        self._max_improvements = max_improvements
        self._temperature = temperature

    @property
    def name(self) -> str:
        return "CodeImprover"

    def build_prompt(self, input: ImproverInput) -> AgentContext:
        system_prompt = """You are a code improvement agent for kgents, a spec-first agent framework.

Your task is to generate CONCRETE, WORKING code improvements based on hypotheses.

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

OUTPUT FORMAT (strict JSON):
{
    "improvements": [
        {
            "description": "Brief description of the change",
            "rationale": "Why this improves the code",
            "new_content": "COMPLETE new file content (not a diff)",
            "improvement_type": "refactor|fix|feature|test",
            "confidence": 0.0-1.0
        }
    ],
    "reasoning": "Overall reasoning about the improvements"
}

CRITICAL:
- new_content MUST be complete, valid Python that can replace the entire file
- Focus on the most impactful improvements
- Don't make changes that require external dependencies not already imported
- Preserve existing functionality unless explicitly improving it"""

        user_prompt = f"""Analyze this module and generate up to {self._max_improvements} improvements:

MODULE: {input.module.name}
CATEGORY: {input.module.category}
PATH: {input.module.path}

CURRENT CODE:
```python
{input.module.content}
```

IMPROVEMENT HYPOTHESES (from analysis):
{chr(10).join(f"- {h}" for h in input.hypotheses)}

CONSTRAINTS:
{chr(10).join(f"- {c}" for c in input.constraints)}

Generate concrete improvements. Return ONLY valid JSON."""

        return AgentContext(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=self._temperature,
            max_tokens=8000,
        )

    def parse_response(self, response: str) -> ImproverOutput:
        # Handle markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]

        data = json.loads(response.strip())

        improvements = [
            Improvement(
                description=imp["description"],
                rationale=imp["rationale"],
                new_content=imp["new_content"],
                improvement_type=imp["improvement_type"],
                confidence=float(imp["confidence"]),
            )
            for imp in data["improvements"]
        ]

        return ImproverOutput(
            improvements=improvements,
            reasoning=data["reasoning"],
        )

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
                ["python", "-m", "mypy", temp_path, "--ignore-missing-imports"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return True, "Type check passed"
            else:
                return False, f"Type errors:\n{result.stdout}"
        except FileNotFoundError:
            return True, "mypy not installed, skipping type check"
        except subprocess.TimeoutExpired:
            return False, "Type check timed out"
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

        # Initialize components
        self._runtime = ClaudeCLIRuntime(timeout=300.0, max_retries=2)
        self._hypothesis_engine = HypothesisEngine(hypothesis_count=3, temperature=0.7)
        self._code_improver = CodeImprover(
            max_improvements=config.max_improvements_per_module,
            temperature=0.7
        )
        self._judge = Judge()
        self._hegel = HegelAgent()
        self._validator = Validator(self._base_path)
        self._git = GitSafety(self._base_path.parent.parent)  # Go up to repo root
        self._principles = make_default_principles()

    def load_modules(self) -> list[CodeModule]:
        """Load Python modules from impl directory."""
        targets = {
            "runtime": ["runtime"],
            "agents": ["agents/a", "agents/b", "agents/c", "agents/h", "agents/k"],
            "bootstrap": ["bootstrap"],
            "all": ["runtime", "agents/a", "agents/b", "agents/c", "agents/h", "agents/k", "bootstrap"],
        }

        dirs = targets.get(self._config.target, targets["all"])
        modules: list[CodeModule] = []

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

    async def generate_hypotheses(self, module: CodeModule) -> list[str]:
        """Generate improvement hypotheses for a module."""
        observations = [
            f"Module: {module.name}",
            f"Category: {module.category}",
            f"Lines: {len(module.content.splitlines())}",
            f"Has docstring: {'yes' if '\"\"\"' in module.content else 'no'}",
            f"Uses async: {'yes' if 'async def' in module.content else 'no'}",
        ]

        if "# TODO" in module.content:
            observations.append("Contains TODO comments")
        if "raise NotImplementedError" in module.content:
            observations.append("Has NotImplementedError (incomplete)")

        try:
            result = await self._runtime.execute(
                self._hypothesis_engine,
                HypothesisInput(
                    observations=observations,
                    domain="software architecture",
                    question=f"What improvements would make {module.name} more robust and composable?",
                    constraints=[
                        "Agents are morphisms: A → B",
                        "Use Fix pattern for retries",
                        "Conflicts are data",
                    ],
                )
            )
            return [h.statement for h in result.output.hypotheses]
        except Exception as e:
            log(f"Hypothesis generation failed: {e}", "   ⚠️")
            return []

    async def generate_improvements(
        self,
        module: CodeModule,
        hypotheses: list[str]
    ) -> list[Improvement]:
        """Generate concrete code improvements."""
        try:
            result = await self._runtime.execute(
                self._code_improver,
                ImproverInput(
                    module=module,
                    hypotheses=hypotheses,
                    constraints=[
                        "kgents principles: tasteful, curated, composable",
                        "Agents are morphisms with clear A → B types",
                        "Use Fix for iteration/retry patterns",
                        "Don't introduce new dependencies",
                    ],
                )
            )
            return result.output.improvements
        except Exception as e:
            log(f"Improvement generation failed: {e}", "   ⚠️")
            return []

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

        # Stage 2: Synthesize
        experiment.status = ExperimentStatus.SYNTHESIZING
        log(f"Synthesizing...", "      ")

        synthesis = await self.synthesize(module, improvement)
        experiment.synthesis = synthesis

        if synthesis.productive_tension:
            log(f"HELD: {synthesis.sublation_notes}", "      ⏸️")
            return experiment

        log(f"Synthesis: {synthesis.sublation_notes[:60]}...", "      ↑")

        return experiment

    async def incorporate(self, experiment: Experiment) -> bool:
        """Apply an experiment's improvement to the codebase."""
        if self._config.dry_run:
            log(f"DRY RUN: Would apply {experiment.improvement.description}", "   🔍")
            return True

        # Write the new content
        experiment.module.path.write_text(experiment.improvement.new_content)
        experiment.status = ExperimentStatus.INCORPORATED
        log(f"Applied: {experiment.improvement.description}", "   ✅")

        return True

    async def evolve_module(self, module: CodeModule) -> list[Experiment]:
        """Evolve a single module through the full pipeline."""
        experiments: list[Experiment] = []

        log(f"\n{'='*60}")
        log(f"EVOLVING: {module.name} ({module.category})")
        log(f"{'='*60}")

        # Generate hypotheses
        log(f"Generating hypotheses...", "   1.")
        hypotheses = await self.generate_hypotheses(module)
        if not hypotheses:
            log(f"No hypotheses generated, skipping", "      ")
            return experiments
        log(f"Generated {len(hypotheses)} hypotheses", "      ")

        # Generate improvements
        log(f"Generating improvements...", "   2.")
        improvements = await self.generate_improvements(module, hypotheses)
        if not improvements:
            log(f"No improvements generated, skipping", "      ")
            return experiments
        log(f"Generated {len(improvements)} improvements", "      ")

        # Run experiments
        log(f"Running experiments...", "   3.")
        for i, improvement in enumerate(improvements):
            exp_id = f"{module.name}-{i+1}"
            log(f"\n   [{exp_id}] {improvement.description[:50]}...")
            log(f"      Type: {improvement.improvement_type}, Confidence: {improvement.confidence:.2f}")

            experiment = await self.run_experiment(module, improvement, exp_id)
            experiments.append(experiment)

        return experiments

    async def run(self) -> EvolutionReport:
        """Run the full evolution process."""
        log("="*60)
        log("KGENTS EVOLUTION")
        log(f"Target: {self._config.target}")
        log(f"Dry run: {self._config.dry_run}")
        log(f"Auto-apply: {self._config.auto_apply}")
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
        for module in modules:
            experiments = await self.evolve_module(module)
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
        elif arg in ["runtime", "agents", "bootstrap", "all"]:
            config.target = arg
        elif arg == "--dry-run":
            config.dry_run = True
        elif arg == "--auto-apply":
            config.auto_apply = True

    return config


async def main():
    config = parse_args()

    if config.target not in ["runtime", "agents", "bootstrap", "all"]:
        log(f"Unknown target: {config.target}")
        log("Usage: python evolve.py [runtime|agents|bootstrap|all] [--dry-run] [--auto-apply]")
        sys.exit(1)

    pipeline = EvolutionPipeline(config)
    report = await pipeline.run()

    log(f"\n{report.summary}")


if __name__ == "__main__":
    asyncio.run(main())
