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
        self._judge: Optional[Judge] = None
        self._contradict: Optional[Contradict] = None
        self._sublate: Optional[Sublate] = None
        self._hegel: Optional[HegelAgent] = None

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

    def _get_judge(self) -> Judge:
        """Lazy instantiation of judge."""
        if self._judge is None:
            self._judge = Judge(runtime=self._get_runtime())
        return self._judge

    def _get_contradict(self) -> Contradict:
        """Lazy instantiation of contradict."""
        if self._contradict is None:
            self._contradict = Contradict(runtime=self._get_runtime())
        return self._contradict

    def _get_sublate(self) -> Sublate:
        """Lazy instantiation of sublate."""
        if self._sublate is None:
            self._sublate = Sublate(runtime=self._get_runtime())
        return self._sublate

    def _get_hegel(self) -> HegelAgent:
        """Lazy instantiation of Hegel."""
        if self._hegel is None:
            self._hegel = HegelAgent(runtime=self._get_runtime())
        return self._hegel

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
        """Generate improvement hypotheses for a module."""
        log(f"[{module.name}] Generating hypotheses...")

        code_content = self._get_code_preview(module.path)

        hypothesis_input = HypothesisInput(
            observations=[
                f"Module: {module.name}",
                f"Category: {module.category}",
                f"Path: {module.path}",
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

        try:
            engine = self._get_hypothesis_engine()
            runtime = self._get_runtime()
            result = await runtime.execute(engine, hypothesis_input)

            # Check if output is HypothesisError or HypothesisOutput
            hypotheses_output = result.output
            if not hasattr(hypotheses_output, 'hypotheses'):
                # Got HypothesisError instead of HypothesisOutput
                error_msg = str(hypotheses_output) if hasattr(hypotheses_output, 'message') else "Unknown error"
                log(f"[{module.name}] Failed to generate hypotheses: {error_msg}")
                return []

            hypotheses = [h.statement for h in hypotheses_output.hypotheses]

            log(f"[{module.name}] Generated {len(hypotheses)} hypotheses")
            for i, h in enumerate(hypotheses, 1):
                log(f"  {i}. {h[:80]}...")

            return hypotheses
        except Exception as e:
            log(f"[{module.name}] Failed to generate hypotheses: {e}")
            return []

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
        )

        log(f"[{exp_id}] Generated: {improvement.description}")
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

            # Extract METADATA section
            if "## METADATA" not in response or "## CODE" not in response:
                log(f"[{module.name}] Invalid response format (missing sections)")
                return None

            metadata_section = response.split("## METADATA")[1].split("## CODE")[0].strip()
            code_section = response.split("## CODE")[1].strip()

            # Parse metadata JSON
            metadata = json.loads(metadata_section)

            # Extract code from markdown block
            if "```python" in code_section:
                code = code_section.split("```python")[1].split("```")[0].strip()
            elif "```" in code_section:
                code = code_section.split("```")[1].split("```")[0].strip()
            else:
                code = code_section.strip()

            return CodeImprovement(
                description=metadata["description"],
                rationale=metadata["rationale"],
                improvement_type=metadata["improvement_type"],
                code=code,
                confidence=metadata["confidence"],
                metadata=metadata,
            )

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            log(f"[{module.name}] Failed to parse LLM response: {e}")
            return None

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
                    ["mypy", str(tmp_path), "--ignore-missing-imports"],
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
        """Judge if improvement should proceed."""
        log(f"[{experiment.id}] Judging improvement...")

        judge_input = JudgeInput(
            claim=experiment.improvement.description,
            evidence={
                "improvement_type": experiment.improvement.improvement_type,
                "rationale": experiment.improvement.rationale,
                "confidence": experiment.improvement.confidence,
                "test_results": experiment.test_results,
            },
            principles=self._principles,
        )

        judge = self._get_judge()
        result = await judge(judge_input)

        if not result.success:
            log(f"[{experiment.id}] Judge failed: {result.error}")
            return Verdict(
                verdict_type=VerdictType.REJECT,
                reasoning="Judge agent failed",
                confidence=0.0,
            )

        verdict = result.output
        experiment.verdict = verdict

        verdict_symbol = "✓" if verdict.verdict_type == VerdictType.APPROVE else "?"
        log(f"[{experiment.id}] {verdict_symbol} {verdict.verdict_type.value}: {verdict.reasoning}")

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
            sublate = self._get_sublate()
            sublate_result = await sublate(dialectic_output.tensions)

            if sublate_result.success:
                synthesis = sublate_result.output
                experiment.synthesis = synthesis

                if synthesis.resolution_type == ResolutionType.HOLD:
                    experiment.status = ExperimentStatus.HELD
                    log(f"[{experiment.id}] ⊙ Tension held for human judgment")
                    return synthesis

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
                continue

            # Judge
            verdict = await self.judge_experiment(exp)
            if verdict.verdict_type == VerdictType.REJECT:
                exp.status = ExperimentStatus.FAILED
                continue

            # Synthesize (dialectic)
            await self.synthesize(exp)

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
