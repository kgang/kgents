"""
evolve.py - Experimental Improvement Framework

A creative framework for experimentally testing, synthesizing, and
incorporating improvements into kgents.

Philosophy:
- Evolution through dialectic: thesis (current) + antithesis (improvement) → synthesis
- Experiments are cheap, production is sacred
- Fix pattern: iterate until stable
- Conflicts are data: log tensions, don't hide them

Architecture (Phase 1 - Composable Agents):
    EvolutionAgent = Ground >> Hypothesis >> Experiment >> Judge >> Sublate >> Incorporate

    Each stage is now a separate agent in agents/e/:
    - ASTAnalyzer: Static analysis for targeted hypotheses
    - MemoryAgent: Track rejected/accepted improvements
    - TestAgent: Validate syntax, types, tests
    - CodeJudge: Evaluate against 7 principles
    - IncorporateAgent: Apply with git safety

Usage (New Default: Test Mode):
    python evolve.py                      # Test mode (fast, safe, single module)
    python evolve.py status               # Check current status (AI agent friendly)
    python evolve.py suggest              # Get improvement suggestions
    python evolve.py meta --auto-apply    # Self-improve evolve.py
    python evolve.py full --auto-apply    # Full codebase evolution

Modes:
    test (default): Fast testing on single module (dry-run, quick, 2 hypotheses)
    status: Show current evolution state and recommendations
    suggest: Analyze and suggest improvements without running experiments
    full: Thorough evolution (all modules, 4 hypotheses, dialectic synthesis)

Flags:
    --dry-run: Preview improvements without applying (default in test mode)
    --auto-apply: Automatically apply improvements that pass tests
    --quick: Skip dialectic synthesis for faster iteration
    --thorough: Use full dialectic synthesis
    --hypotheses=N: Number of hypotheses per module
    --max-improvements=N: Max improvements per module

AI Agent Interface:
    The 'status' and 'suggest' modes are designed for AI agents to query
    the current state and get actionable recommendations without making changes.
    This supports periodic checks via /hydrate command.

Performance:
    Modules are processed in parallel for 2-5x speedup
    Large files (>500 lines) send previews to reduce token usage
    AST analysis is cached to avoid redundant parsing
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

# TYPE_CHECKING: Import types only during type-checking to reduce startup time
if TYPE_CHECKING:
    from agents.b.hypothesis import HypothesisEngine, HypothesisInput
    from agents.h.hegel import HegelAgent, DialecticInput, DialecticOutput
    from bootstrap.sublate import Sublate
    from runtime.base import LLMAgent, AgentContext, AgentResult

# E-gents: Evolution agents (Phase 1 extraction)
from agents.e import (
    # Core types
    CodeModule,
    CodeImprovement,
    Experiment,
    ExperimentStatus,
    # Agents
    ASTAnalyzer,
    ASTAnalysisInput,
    ImprovementMemory,
    TestAgent,
    TestInput,
    CodeJudge,
    JudgeInput,
    IncorporateAgent,
    IncorporateInput,
    # Utilities
    analyze_module_ast,
    generate_targeted_hypotheses,
    get_code_preview,
    extract_metadata,
    extract_code,
    # Safety (Phase 2)
    SafetyConfig,
    SelfEvolutionAgent,
    SafeEvolutionInput,
    compute_code_similarity,
    # Recovery Layer (Phase 2.5c)
    RetryStrategy,
    RetryConfig,
    FallbackStrategy,
    FallbackConfig,
    ErrorMemory,
    # Status Agents (Phase 2.5e)
    create_status_reporter,
)

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


# ============================================================================
# Configuration
# ============================================================================

def log(msg: str = "", prefix: str = "", file: Optional[Any] = None) -> None:
    """Print with immediate flush for real-time output."""
    output = f"{prefix} {msg}" if prefix else msg
    print(output, flush=True)
    if file:
        file.write(output + "\n")
        file.flush()


@dataclass
class EvolveConfig:
    """Configuration for the evolution process."""
    target: str = "meta"  # Default to single module for testing
    mode: str = "test"  # test|status|suggest|full
    dry_run: bool = True  # Safe by default
    auto_apply: bool = False
    max_improvements_per_module: int = 1  # Reduced for testing
    experiment_branch_prefix: str = "evolve"
    require_tests_pass: bool = True
    require_type_check: bool = True
    quick_mode: bool = True  # Fast by default for testing
    hypothesis_count: int = 2  # Reduced for testing
    # Phase 2: Safe self-evolution
    safe_mode: bool = False
    max_iterations: int = 3
    convergence_threshold: float = 0.95
    # Phase 2.5c: Recovery layer
    enable_retry: bool = True
    max_retries: int = 2
    enable_fallback: bool = True
    enable_error_memory: bool = True


@dataclass
class EvolutionReport:
    """Summary of evolution run."""
    experiments: list[Experiment]
    incorporated: list[Experiment]
    rejected: list[Experiment]
    held: list[Experiment]
    summary: str


# ============================================================================
# Core Logic (using agents/e components)
# ============================================================================

class EvolutionPipeline:
    """
    Main pipeline for evolving code.

    Now delegates to composable agents in agents/e/:
    - ASTAnalyzer for code structure analysis
    - ImprovementMemory for avoiding re-proposals
    - TestAgent for validation
    - CodeJudge for principle-based evaluation
    - IncorporateAgent for applying changes
    """

    def __init__(self, config: EvolveConfig, runtime: Optional[Any] = None):
        self._config = config
        self._runtime = runtime
        self._principles = make_default_principles()

        # Composable agents from agents/e
        self._ast_analyzer = ASTAnalyzer(max_hypothesis_targets=3)
        self._memory = ImprovementMemory()
        self._test_agent = TestAgent()
        self._judge = CodeJudge()
        self._incorporate = IncorporateAgent()

        # Recovery layer (Phase 2.5c)
        self._retry_strategy = RetryStrategy(RetryConfig(
            max_retries=config.max_retries,
            verbose=False
        )) if config.enable_retry else None
        self._fallback_strategy = FallbackStrategy(FallbackConfig(
            verbose=False
        )) if config.enable_fallback else None
        self._error_memory = ErrorMemory() if config.enable_error_memory else None

        # Agents requiring runtime (lazy instantiation)
        self._hypothesis_engine: Optional["HypothesisEngine"] = None
        self._hegel: Optional["HegelAgent"] = None
        self._sublate: Optional["Sublate"] = None

        # AST cache
        self._ast_cache: dict[str, Any] = {}

    def _get_runtime(self) -> Any:
        """Get or create the runtime instance."""
        if self._runtime is None:
            from runtime import ClaudeCLIRuntime
            self._runtime = ClaudeCLIRuntime()
        return self._runtime

    def _get_hypothesis_engine(self) -> "HypothesisEngine":
        """Lazy instantiation of hypothesis engine."""
        if self._hypothesis_engine is None:
            from agents.b.hypothesis import HypothesisEngine
            self._hypothesis_engine = HypothesisEngine()
        return self._hypothesis_engine

    def _get_hegel(self) -> "HegelAgent":
        """Lazy instantiation of Hegel."""
        if self._hegel is None:
            from agents.h.hegel import HegelAgent
            self._hegel = HegelAgent()
        return self._hegel

    def _get_sublate(self) -> "Sublate":
        """Lazy instantiation of Sublate for tension resolution."""
        if self._sublate is None:
            from bootstrap.sublate import Sublate
            self._sublate = Sublate()
        return self._sublate

    async def _get_ast_structure(self, module: CodeModule) -> Any:
        """Get cached AST structure for a module."""
        key = str(module.path)
        if key not in self._ast_cache:
            result = await self._ast_analyzer.invoke(ASTAnalysisInput(path=module.path))
            self._ast_cache[key] = result.structure
        return self._ast_cache[key]

    def _has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes in git."""
        import subprocess
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
            modules.append(CodeModule(
                name="evolve",
                category="meta",
                path=base / "evolve.py"
            ))

        return modules

    async def generate_hypotheses(self, module: CodeModule) -> list[str]:
        """Generate improvement hypotheses for a module."""
        log(f"[{module.name}] Generating hypotheses...")

        # Phase 1: AST-based targeted hypotheses
        ast_hypotheses: list[str] = []
        structure = await self._get_ast_structure(module)
        if structure:
            ast_hypotheses = generate_targeted_hypotheses(
                structure,
                max_targets=max(2, self._config.hypothesis_count // 2)
            )
            if ast_hypotheses:
                log(f"[{module.name}] AST analysis found {len(ast_hypotheses)} targets:")
                for i, h in enumerate(ast_hypotheses, 1):
                    log(f"  🎯 AST{i}: {h}")

        # Phase 2: LLM-generated hypotheses
        code_content = get_code_preview(module.path)
        ast_context = ""
        if structure:
            ast_context = f"""
AST ANALYSIS:
- Classes: {', '.join(c['name'] for c in structure.classes) or 'None'}
- Functions: {', '.join(f['name'] for f in structure.functions[:10]) or 'None'}
- Imports: {len(structure.imports)} total
- Complexity hints: {structure.complexity_hints[:2] if structure.complexity_hints else 'None'}
"""

        from agents.b.hypothesis import HypothesisInput

        hypothesis_input = HypothesisInput(
            observations=[
                f"Module: {module.name}",
                f"Category: {module.category}",
                f"Path: {module.path}",
                ast_context,
                f"Code preview:\n{code_content}",
            ],
            domain=f"Code improvement for {module.category}/{module.name}",
            question=f"What are {self._config.hypothesis_count} specific improvements?",
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
            if hasattr(hypotheses_output, 'hypotheses'):
                llm_hypotheses = [h.statement for h in hypotheses_output.hypotheses]
        except Exception as e:
            log(f"[{module.name}] LLM hypothesis generation error: {e}")

        # Combine and filter by memory
        all_hypotheses = ast_hypotheses + llm_hypotheses
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

        log(f"[{module.name}] Generated {len(filtered_hypotheses)} hypotheses ({skipped_count} filtered)")
        for i, h in enumerate(filtered_hypotheses, 1):
            log(f"  💡 H{i}: {h}")

        return filtered_hypotheses

    async def experiment(self, module: CodeModule, hypothesis: str) -> Optional[Experiment]:
        """Run a single experiment: generate improvement from hypothesis."""
        exp_id = f"{module.name}_{hash(hypothesis) & 0xFFFF:04x}"
        log(f"[{exp_id}] Experimenting with hypothesis...")

        improvement = await self._generate_improvement(module, hypothesis)
        if not improvement:
            return None

        experiment = Experiment(
            id=exp_id,
            module=module,
            improvement=improvement,
            hypothesis=hypothesis,
        )

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
        code_content = get_code_preview(module.path)

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

MODULE: {module.name}
CATEGORY: {module.category}
PATH: {module.path}

CURRENT CODE (Preview - {len(code_content.splitlines())} lines total):
```python
{code_content}
```

HYPOTHESIS TO EXPLORE:
{hypothesis}

Generate ONE concrete improvement. Return ONLY valid JSON."""

        try:
            from runtime.base import AgentContext

            runtime = self._get_runtime()
            context = AgentContext(
                system_prompt="You are a code improvement agent for kgents.",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=16000,
            )

            response_text, _ = await runtime.raw_completion(context)
            response = response_text.strip()

            metadata = extract_metadata(response, module.name)
            if metadata is None:
                return None

            code = extract_code(response, module.name)
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
            log(f"[{module.name}] Failed to generate improvement: {e}")
            return None

    async def test(self, experiment: Experiment) -> bool:
        """Test an experimental improvement using TestAgent."""
        log(f"[{experiment.id}] Testing improvement...")

        result = await self._test_agent.invoke(TestInput(
            experiment=experiment,
            require_type_check=self._config.require_type_check,
            require_tests_pass=self._config.require_tests_pass,
        ))

        if result.passed:
            log(f"[{experiment.id}] ✓ All tests passed")
        else:
            log(f"[{experiment.id}] ✗ {result.error}")

        return result.passed

    async def judge_experiment(self, experiment: Experiment) -> Verdict:
        """Judge if improvement should proceed using CodeJudge agent."""
        log(f"[{experiment.id}] Judging improvement against 7 principles...")

        original_code = experiment.module.path.read_text()
        result = await self._judge.invoke(JudgeInput(
            improvement=experiment.improvement,
            original_code=original_code,
            module_name=experiment.module.name,
        ))

        experiment.verdict = result.verdict

        verdict_symbols = {
            VerdictType.ACCEPT: "✓",
            VerdictType.REVISE: "⚠",
            VerdictType.REJECT: "✗",
        }
        symbol = verdict_symbols.get(result.verdict.type, "?")

        log(f"[{experiment.id}] {symbol} {result.verdict.type.value.upper()}")
        for reason in result.reasons:
            log(f"    {reason}")

        return result.verdict

    async def synthesize(self, experiment: Experiment) -> Optional[Synthesis]:
        """Dialectic synthesis of improvement vs current code."""
        if self._config.quick_mode:
            log(f"[{experiment.id}] Skipping synthesis (quick mode)")
            return None

        log(f"[{experiment.id}] Synthesizing via dialectic...")

        from agents.h.hegel import DialecticInput

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
        dialectic_output = await hegel.invoke(dialectic_input)

        if dialectic_output.tension:
            log(f"[{experiment.id}] ⚡ Productive tension detected")
            log(f"      {dialectic_output.tension.description}")

            sublate_agent = self._get_sublate()
            sublate_input = SublateInput(tensions=(dialectic_output.tension,))
            sublate_result = await sublate_agent.invoke(sublate_input)

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
        """Incorporate approved improvement using IncorporateAgent."""
        log(f"[{experiment.id}] Incorporating improvement...")

        result = await self._incorporate.invoke(IncorporateInput(
            experiment=experiment,
            dry_run=self._config.dry_run,
            commit=not self._config.dry_run,
        ))

        if result.success:
            if self._config.dry_run:
                log(f"[{experiment.id}] (dry-run) Would write to {experiment.module.path}")
            else:
                log(f"[{experiment.id}] ✓ Incorporated (commit: {result.commit_sha})")
        else:
            log(f"[{experiment.id}] ✗ Failed: {result.error}")

        return result.success

    async def _test_with_recovery(
        self,
        experiment: Experiment,
        module: CodeModule,
        hypothesis: str
    ) -> tuple[bool, Optional[Experiment]]:
        """
        Test experiment with retry and fallback recovery strategies.

        Returns: (success, final_experiment)
        - success: Whether any version passed
        - final_experiment: The successful experiment or None
        """
        # Test initial experiment
        passed = await self.test(experiment)
        if passed:
            return (True, experiment)

        # Record initial failure in error memory
        if self._error_memory and experiment.error:
            self._error_memory.record_failure(
                module_category=module.category,
                module_name=module.name,
                hypothesis=hypothesis,
                failure_type=self._categorize_test_failure(experiment.error),
                failure_details=experiment.error
            )

        # Try retry strategy
        if self._retry_strategy and self._retry_strategy.should_retry(experiment):
            log(f"[{experiment.id}] Attempting retry with refined prompt...")

            for attempt in range(self._config.max_retries):
                # Build prompt context for retry
                from agents.e.prompts import build_prompt_context
                context = build_prompt_context(module)

                # Generate refined prompt
                refined_prompt = self._retry_strategy.refine_prompt(
                    original_hypothesis=hypothesis,
                    failure_reason=experiment.error or "Unknown failure",
                    attempt=attempt,
                    context=context,
                    validation_report=None  # Could extract from test result
                )

                # Generate new improvement with refined prompt
                log(f"[{experiment.id}] Retry {attempt + 1}/{self._config.max_retries}")
                retry_improvement = await self._generate_improvement(module, refined_prompt)
                if not retry_improvement:
                    continue

                # Create retry experiment
                retry_exp = Experiment(
                    id=f"{experiment.id}_r{attempt + 1}",
                    module=module,
                    improvement=retry_improvement,
                    hypothesis=hypothesis,
                )

                # Test retry
                retry_passed = await self.test(retry_exp)
                if retry_passed:
                    log(f"[{experiment.id}] ✓ Retry {attempt + 1} succeeded!")
                    return (True, retry_exp)
                else:
                    log(f"[{experiment.id}] ✗ Retry {attempt + 1} failed: {retry_exp.error}")
                    if self._error_memory and retry_exp.error:
                        self._error_memory.record_failure(
                            module_category=module.category,
                            module_name=module.name,
                            hypothesis=hypothesis,
                            failure_type=self._categorize_test_failure(retry_exp.error),
                            failure_details=retry_exp.error
                        )

        # Try fallback strategy
        if self._fallback_strategy and self._fallback_strategy.should_fallback(
            experiment,
            retry_exhausted=True
        ):
            log(f"[{experiment.id}] Attempting fallback strategies...")

            # Try minimal version
            if self._config.enable_fallback:
                from agents.e.prompts import build_prompt_context
                context = build_prompt_context(module)

                minimal_prompt = self._fallback_strategy.generate_minimal_prompt(
                    original_hypothesis=hypothesis,
                    context=context
                )

                log(f"[{experiment.id}] Trying minimal fallback...")
                fallback_improvement = await self._generate_improvement(module, minimal_prompt)
                if fallback_improvement:
                    fallback_exp = Experiment(
                        id=f"{experiment.id}_fb",
                        module=module,
                        improvement=fallback_improvement,
                        hypothesis=hypothesis,
                    )

                    fallback_passed = await self.test(fallback_exp)
                    if fallback_passed:
                        log(f"[{experiment.id}] ✓ Fallback succeeded!")
                        return (True, fallback_exp)

        # All recovery attempts failed
        return (False, None)

    def _categorize_test_failure(self, error: str) -> str:
        """Categorize test failure type for error memory."""
        error_lower = error.lower()
        if "syntax" in error_lower or "parse" in error_lower:
            return "syntax"
        if "type" in error_lower or "mypy" in error_lower:
            return "type"
        if "import" in error_lower or "modulenotfound" in error_lower:
            return "import"
        if "test" in error_lower or "pytest" in error_lower:
            return "test"
        return "unknown"

    async def _process_module(self, module: CodeModule) -> list[Experiment]:
        """Process a single module (for parallel execution)."""
        log(f"\n{'='*60}")
        log(f"MODULE: {module.category}/{module.name}")
        log(f"{'='*60}")

        hypotheses = await self.generate_hypotheses(module)
        if not hypotheses:
            return []

        experiments = []
        for hypothesis in hypotheses[:self._config.max_improvements_per_module]:
            exp = await self.experiment(module, hypothesis)
            if exp:
                experiments.append(exp)

        # Process each experiment with recovery strategies
        processed_experiments = []
        for exp in experiments:
            # Use recovery layer if enabled, otherwise fallback to simple test
            if self._config.enable_retry or self._config.enable_fallback:
                passed, final_exp = await self._test_with_recovery(exp, module, exp.hypothesis)
                if not passed:
                    # All recovery attempts failed
                    self._memory.record(
                        module=module.name,
                        hypothesis=exp.hypothesis,
                        description=exp.improvement.description,
                        outcome="rejected",
                        rejection_reason=exp.error or "Test failure (all retries exhausted)",
                    )
                    continue
                # Use the successful experiment (could be original, retry, or fallback)
                exp = final_exp  # type: ignore
                processed_experiments.append(exp)
            else:
                # Legacy path: simple test without recovery
                passed = await self.test(exp)
                if not passed:
                    self._memory.record(
                        module=module.name,
                        hypothesis=exp.hypothesis,
                        description=exp.improvement.description,
                        outcome="rejected",
                        rejection_reason=exp.error or "Test failure",
                    )
                    continue
                processed_experiments.append(exp)

        # Continue with judge/synthesize/incorporate for passed experiments
        for exp in processed_experiments:

            verdict = await self.judge_experiment(exp)
            if verdict.type == VerdictType.REJECT:
                exp.status = ExperimentStatus.FAILED
                self._memory.record(
                    module=module.name,
                    hypothesis=exp.hypothesis,
                    description=exp.improvement.description,
                    outcome="rejected",
                    rejection_reason=verdict.reasoning,
                )
                continue

            await self.synthesize(exp)

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
        log_dir = Path(__file__).parent / ".evolve_logs"
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = log_dir / f"evolve_{self._config.target}_{timestamp}.log"
        log_file = open(log_path, "w")

        log(f"{'='*60}")
        log(f"KGENTS EVOLUTION (Phase 1: Composable Agents)", file=log_file)
        log(f"Target: {self._config.target}", file=log_file)
        log(f"Dry run: {self._config.dry_run}", file=log_file)
        log(f"Auto-apply: {self._config.auto_apply}", file=log_file)
        log(f"Quick mode: {'True ⚡' if self._config.quick_mode else 'False'}", file=log_file)
        log(f"{'='*60}", file=log_file)
        log(f"⚠️ WARNING: Working tree is not clean." if self._has_uncommitted_changes() else "✓ Working tree is clean")
        log(f"", file=log_file)
        log(f"Loaded {len(self.discover_modules())} modules to evolve", file=log_file)
        log(f"Log file: {log_path}", prefix="📝")

        modules = self.discover_modules()
        log(f"\nDiscovered {len(modules)} modules to evolve")

        start_time = time.time()
        results = await asyncio.gather(
            *[self._process_module(module) for module in modules],
            return_exceptions=True,
        )
        elapsed = time.time() - start_time

        all_experiments: list[Experiment] = []
        for result in results:
            if isinstance(result, list):
                all_experiments.extend(result)
            elif isinstance(result, Exception):
                log(f"⚠ Module processing error: {result}")

        log(f"\nProcessed {len(modules)} modules in {elapsed:.1f}s")

        incorporated: list[Experiment] = []
        rejected = [e for e in all_experiments if e.status == ExperimentStatus.FAILED]
        held = [e for e in all_experiments if e.status == ExperimentStatus.HELD]
        passed = [e for e in all_experiments if e.status == ExperimentStatus.PASSED and e not in held]

        if self._config.auto_apply and not self._config.dry_run:
            log(f"\n{'='*60}")
            log("INCORPORATING IMPROVEMENTS")
            log(f"{'='*60}")

            for experiment in passed:
                if await self.incorporate(experiment):
                    incorporated.append(experiment)

        log(f"\n{'='*60}", file=log_file)
        log("EVOLUTION SUMMARY", file=log_file)
        log(f"{'='*60}", file=log_file)
        log(f"Experiments run: {len(all_experiments)}", file=log_file)
        log(f"  Passed: {len(passed)}", file=log_file)
        log(f"  Failed: {len(rejected)}", file=log_file)
        log(f"  Held (productive tension): {len(held)}", file=log_file)
        log(f"  Incorporated: {len(incorporated)}", file=log_file)

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

        summary = f"Evolved {len(modules)} modules: {len(incorporated)} incorporated, {len(rejected)} rejected, {len(held)} held"

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
            "failed_experiments": [
                {
                    "id": exp.id,
                    "module": exp.module.name,
                    "category": exp.module.category,
                    "hypothesis": exp.hypothesis,
                    "error": exp.error,
                    "improvement": {
                        "type": exp.improvement.improvement_type,
                        "description": exp.improvement.description,
                    } if exp.improvement else None,
                    "test_results": exp.test_results,
                }
                for exp in rejected
            ],
        }

        with open(results_path, 'w') as f:
            json.dump(results_data, f, indent=2)

        log(f"📊 Decision data saved: {results_path}")

        log_file.close()

        return EvolutionReport(
            experiments=all_experiments,
            incorporated=incorporated,
            rejected=rejected,
            held=held,
            summary=summary,
        )


# ============================================================================
# Status & Suggestion Modes (for AI agent interface)
# ============================================================================

async def show_status() -> None:
    """
    Show current evolution status - ideal for AI agents checking state.

    Refactored (Phase 2.5e) to use composable status agents:
        StatusReporter = GitStatusAgent >> EvolutionLogAgent >> HydrateStatusAgent >> StatusPresenter

    This demonstrates the morphism principle by decomposing an 83-line monolithic
    function into 4 composable agents with clear input/output types.
    """
    base = Path(__file__).parent
    reporter = create_status_reporter()
    await reporter.invoke(base)


async def show_suggestions(config: EvolveConfig) -> None:
    """Show improvement suggestions without running experiments."""
    log("=" * 60)
    log("EVOLUTION SUGGESTIONS")
    log("=" * 60)

    pipeline = EvolutionPipeline(config)
    modules = pipeline.discover_modules()

    log(f"\nAnalyzing {len(modules)} modules for improvement opportunities...\n")

    for module in modules[:5]:  # Limit to first 5
        log(f"Module: {module.category}/{module.name}")
        log("-" * 40)

        # Use AST analyzer to get quick insights
        structure = await pipeline._get_ast_structure(module)
        if structure:
            # Check for missing type annotations
            code = get_code_preview(module.path)
            lines = code.split("\n")

            suggestions = []

            # Check complexity
            if structure.complexity_hints:
                suggestions.append(f"  💡 Complexity hints: {', '.join(structure.complexity_hints[:2])}")

            # Check for long functions (>50 lines)
            for func in structure.functions[:3]:
                if "long" in str(func).lower():
                    suggestions.append(f"  📏 Consider refactoring long function: {func.get('name', 'unknown')}")

            # Check for missing docstrings
            if not structure.docstring:
                suggestions.append("  📝 Missing module docstring")

            # Generic suggestions based on category
            if module.category == "runtime":
                suggestions.append("  ⚡ Runtime modules: Focus on performance and error handling")
            elif "agents" in module.category:
                suggestions.append("  🤖 Agent modules: Ensure clear A → B type signatures")

            if suggestions:
                for s in suggestions[:3]:
                    log(s)
            else:
                log("  ✓ No obvious improvements needed")

        log("")

    log(f"{'=' * 60}")
    log("To run experiments, use:")
    log("  python evolve.py meta --auto-apply  (for self-improvement)")
    log("  python evolve.py full --auto-apply  (for full codebase)")
    log("")


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
        elif arg.startswith("--mode="):
            config.mode = arg.split("=")[1]
        elif arg in ["test", "status", "suggest", "full"]:
            config.mode = arg
        elif arg == "--dry-run":
            config.dry_run = True
        elif arg == "--no-dry-run":
            config.dry_run = False
        elif arg == "--auto-apply":
            config.auto_apply = True
            config.dry_run = False
        elif arg == "--quick":
            config.quick_mode = True
        elif arg == "--thorough":
            config.quick_mode = False
        elif arg.startswith("--hypotheses="):
            config.hypothesis_count = int(arg.split("=")[1])
        elif arg.startswith("--max-improvements="):
            config.max_improvements_per_module = int(arg.split("=")[1])
        elif arg == "--safe-mode":
            config.safe_mode = True
        elif arg.startswith("--max-iterations="):
            config.max_iterations = int(arg.split("=")[1])
        elif arg.startswith("--convergence="):
            config.convergence_threshold = float(arg.split("=")[1])

    # Mode-specific defaults
    if config.mode == "full":
        config.target = config.target if config.target != "meta" else "all"
        config.quick_mode = False
        config.hypothesis_count = 4
        config.max_improvements_per_module = 4
    elif config.mode == "test":
        # Keep test defaults (fast, single module)
        pass

    return config


async def main() -> None:
    config = parse_args()

    # Show help if needed
    if config.target not in ["runtime", "agents", "bootstrap", "meta", "all"]:
        log(f"Unknown target: {config.target}")
        log("Usage: python evolve.py [MODE] [TARGET] [FLAGS]")
        log("")
        log("Modes (default: test):")
        log("  test                   Fast test on single module (dry-run, quick)")
        log("  status                 Show current evolution status (AI agent friendly)")
        log("  suggest                Show improvement suggestions without running")
        log("  full                   Full evolution run (all modules, thorough)")
        log("")
        log("Targets (default: meta):")
        log("  runtime                Runtime modules")
        log("  agents                 All agent modules")
        log("  bootstrap              Bootstrap modules")
        log("  meta                   evolve.py itself")
        log("  all                    All modules")
        log("")
        log("Flags:")
        log("  --dry-run              Preview improvements without applying (default)")
        log("  --no-dry-run           Disable dry-run mode")
        log("  --auto-apply           Automatically apply improvements that pass tests")
        log("  --quick                Skip dialectic synthesis for faster iteration")
        log("  --thorough             Use full dialectic synthesis")
        log("  --hypotheses=N         Number of hypotheses per module (default: 2)")
        log("  --max-improvements=N   Max improvements per module (default: 1)")
        log("")
        log("Safe self-evolution (Phase 2):")
        log("  --safe-mode            Enable safe self-evolution with fixed-point iteration")
        log("  --max-iterations=N     Max fixed-point iterations (default: 3)")
        log("  --convergence=F        Convergence threshold 0.0-1.0 (default: 0.95)")
        log("")
        log("Examples:")
        log("  python evolve.py                        # Test mode (fast, safe)")
        log("  python evolve.py status                 # Check current status")
        log("  python evolve.py suggest                # Get suggestions")
        log("  python evolve.py meta --auto-apply      # Improve evolve.py")
        log("  python evolve.py full --auto-apply      # Full evolution")
        sys.exit(1)

    # Status mode - show current state
    if config.mode == "status":
        await show_status()
        return

    # Suggest mode - show suggestions without running
    if config.mode == "suggest":
        await show_suggestions(config)
        return

    # Phase 2: Safe self-evolution mode
    if config.safe_mode:
        await run_safe_evolution(config)
        return

    # Test or full mode - run the pipeline
    pipeline = EvolutionPipeline(config)
    report = await pipeline.run()

    log(f"\n{report.summary}")


async def run_safe_evolution(config: EvolveConfig) -> None:
    """
    Run safe self-evolution using fixed-point iteration.

    This mode is specifically for evolving evolve.py and related
    infrastructure. It uses multiple safety layers:

    1. Sandbox testing (syntax, types, self-test)
    2. Fixed-point convergence (iterate until stable)
    3. Human approval (for meta-changes)

    Usage:
        python evolve.py meta --safe-mode --dry-run
    """
    log("=" * 60)
    log("SAFE SELF-EVOLUTION MODE (Phase 2)")
    log("=" * 60)
    log(f"Target: {config.target}")
    log(f"Max iterations: {config.max_iterations}")
    log(f"Convergence threshold: {config.convergence_threshold}")
    log(f"Dry run: {config.dry_run}")
    log("")

    # Create safety config
    safety_config = SafetyConfig(
        read_only=config.dry_run,
        require_syntax_valid=True,
        require_mypy_strict=config.require_type_check,
        require_self_test=True,
        max_iterations=config.max_iterations,
        convergence_threshold=config.convergence_threshold,
        require_human_approval=not config.auto_apply,
    )

    # Determine target files
    base = Path(__file__).parent
    if config.target == "meta":
        targets = [base / "evolve.py"]
    elif config.target == "bootstrap":
        targets = list((base / "bootstrap").glob("*.py"))
    elif config.target == "agents":
        targets = []
        for letter_dir in (base / "agents").iterdir():
            if letter_dir.is_dir() and not letter_dir.name.startswith("_"):
                targets.extend(letter_dir.glob("*.py"))
    else:
        targets = [base / "evolve.py"]

    log(f"Targets: {len(targets)} files")
    for t in targets[:5]:
        log(f"  - {t.name}")
    if len(targets) > 5:
        log(f"  ... and {len(targets) - 5} more")
    log("")

    # Run self-evolution agent on each target
    agent = SelfEvolutionAgent(config=safety_config)

    for target in targets:
        log(f"\n{'='*60}")
        log(f"EVOLVING: {target.name}")
        log(f"{'='*60}")

        if not target.exists():
            log(f"  Skip: file not found")
            continue

        original_code = target.read_text()
        log(f"  Original: {len(original_code.splitlines())} lines")

        result = await agent.invoke(SafeEvolutionInput(
            target=target,
            config=safety_config,
        ))

        if result.success:
            log(f"  Status: SUCCESS")
            log(f"  Converged: {result.converged}")
            log(f"  Iterations: {result.iterations}")
            log(f"  Final similarity: {result.final_similarity:.2%}")

            if result.evolved_code and not config.dry_run:
                # Apply the evolved code
                target.write_text(result.evolved_code)
                log(f"  Applied: {len(result.evolved_code.splitlines())} lines")
            elif result.evolved_code:
                log(f"  (dry-run) Would write {len(result.evolved_code.splitlines())} lines")
        else:
            log(f"  Status: FAILED")
            log(f"  Error: {result.error}")

        # Show sandbox results
        if result.sandbox_results:
            log(f"  Sandbox tests: {len(result.sandbox_results)}")
            for i, sr in enumerate(result.sandbox_results, 1):
                status = "PASS" if sr.passed else "FAIL"
                log(f"    [{i}] {status}")
                if not sr.passed and sr.error:
                    log(f"        Error: {sr.error[:80]}...")

    log(f"\n{'='*60}")
    log("SAFE SELF-EVOLUTION COMPLETE")
    log(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
