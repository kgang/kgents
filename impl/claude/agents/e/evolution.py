"""
Evolution Agent: Composed pipeline for code evolution.

This module implements the evolution pipeline as a composition of agents:

    EvolutionAgent = Ground >> Hypothesis >> Experiment >> Judge >> Sublate >> Incorporate

The pipeline follows kgents principles:
- Composable: Each stage is an agent, composed via >>
- Heterarchical: No fixed orchestrator, agents in flux
- Generative: Pipeline can be regenerated from this spec

Morphism: EvolutionInput → EvolutionReport
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from bootstrap.types import Agent, VerdictType

from .ast_analyzer import ASTAnalyzer, ASTAnalysisInput, CodeStructure, generate_targeted_hypotheses
from .experiment import (
    CodeModule,
    CodeImprovement,
    Experiment,
    ExperimentStatus,
    TestAgent,
    TestInput,
    get_code_preview,
)
from .incorporate import IncorporateAgent, IncorporateInput
from .judge import CodeJudge, JudgeInput
from .memory import ImprovementMemory, MemoryAgent


@dataclass
class EvolutionConfig:
    """Configuration for the evolution pipeline."""
    target: str = "all"
    dry_run: bool = False
    auto_apply: bool = False
    max_improvements_per_module: int = 4
    hypothesis_count: int = 4
    quick_mode: bool = False
    require_tests_pass: bool = True
    require_type_check: bool = True


@dataclass
class EvolutionReport:
    """Summary of evolution run."""
    experiments: list[Experiment]
    incorporated: list[Experiment]
    rejected: list[Experiment]
    held: list[Experiment]
    summary: str
    elapsed_seconds: float = 0.0


@dataclass(frozen=True)
class EvolutionInput:
    """Input for the evolution pipeline."""
    modules: tuple[CodeModule, ...]
    config: EvolutionConfig


class EvolutionPipeline:
    """
    The main evolution pipeline, implemented as a composition of agents.

    Architecture:
        Ground (codebase facts)
        >> ASTAnalyzer (code structure)
        >> HypothesisEngine (improvement ideas)
        >> ExperimentAgent (test hypotheses)
        >> Judge (evaluate against principles)
        >> Sublate (resolve tensions)
        >> Incorporate (apply changes)

    Each stage is independently testable and composable.
    """

    def __init__(
        self,
        config: EvolutionConfig,
        runtime: Optional[Any] = None,
    ):
        self._config = config
        self._runtime = runtime

        # Composable agents
        self._ast_analyzer = ASTAnalyzer(max_hypothesis_targets=3)
        self._memory = ImprovementMemory()
        self._memory_agent = MemoryAgent(self._memory)
        self._test_agent = TestAgent()
        self._judge = CodeJudge()
        self._incorporate = IncorporateAgent()

        # Lazy-loaded agents (require runtime)
        self._hypothesis_engine: Optional[Any] = None
        self._hegel: Optional[Any] = None
        self._sublate: Optional[Any] = None

        # AST cache
        self._ast_cache: dict[str, Optional[CodeStructure]] = {}

    def _get_runtime(self) -> Any:
        """Get or create the runtime instance."""
        if self._runtime is None:
            from runtime import ClaudeCLIRuntime
            self._runtime = ClaudeCLIRuntime()
        return self._runtime

    def _get_hypothesis_engine(self) -> Any:
        """Lazy instantiation of hypothesis engine."""
        if self._hypothesis_engine is None:
            from agents.b.hypothesis import HypothesisEngine
            self._hypothesis_engine = HypothesisEngine()
        return self._hypothesis_engine

    def _get_hegel(self) -> Any:
        """Lazy instantiation of Hegel."""
        if self._hegel is None:
            from agents.h.hegel import HegelAgent
            self._hegel = HegelAgent()
        return self._hegel

    def _get_sublate(self) -> Any:
        """Lazy instantiation of Sublate."""
        if self._sublate is None:
            from bootstrap.sublate import Sublate
            self._sublate = Sublate()
        return self._sublate

    async def analyze_module(self, module: CodeModule) -> Optional[CodeStructure]:
        """Analyze module AST structure."""
        key = str(module.path)
        if key not in self._ast_cache:
            result = await self._ast_analyzer.invoke(ASTAnalysisInput(path=module.path))
            self._ast_cache[key] = result.structure
        return self._ast_cache[key]

    async def generate_hypotheses(
        self,
        module: CodeModule,
        log_fn: Optional[Any] = None,
    ) -> list[str]:
        """
        Generate improvement hypotheses for a module.

        Combines AST-based and LLM-generated hypotheses,
        filtered by memory to avoid re-proposing rejected ideas.
        """
        log = log_fn or print

        # Phase 1: AST-based targeted hypotheses
        ast_hypotheses: list[str] = []
        structure = await self.analyze_module(module)
        if structure:
            ast_hypotheses = generate_targeted_hypotheses(
                structure,
                max_targets=max(2, self._config.hypothesis_count // 2)
            )

        # Phase 2: LLM-generated hypotheses
        llm_hypotheses: list[str] = []
        try:
            from agents.b.hypothesis import HypothesisInput

            code_content = get_code_preview(module.path)
            ast_context = ""
            if structure:
                ast_context = f"""
AST ANALYSIS:
- Classes: {', '.join(c['name'] for c in structure.classes) or 'None'}
- Functions: {', '.join(f['name'] for f in structure.functions[:10]) or 'None'}
- Imports: {len(structure.imports)} total
"""

            hypothesis_input = HypothesisInput(
                observations=[
                    f"Module: {module.name}",
                    f"Category: {module.category}",
                    ast_context,
                    f"Code preview:\n{code_content}",
                ],
                domain=f"Code improvement for {module.category}/{module.name}",
                question=f"What are {self._config.hypothesis_count} specific improvements?",
                constraints=[
                    "Agents are morphisms with clear A → B types",
                    "Composable via >> operator",
                    "Use Fix pattern for iteration/retry",
                    "Tasteful: less is more",
                ],
            )

            engine = self._get_hypothesis_engine()
            runtime = self._get_runtime()
            result = await runtime.execute(engine, hypothesis_input)

            if hasattr(result.output, 'hypotheses'):
                llm_hypotheses = [h.statement for h in result.output.hypotheses]
        except Exception as e:
            log(f"[{module.name}] LLM hypothesis error: {e}")

        # Combine and filter
        all_hypotheses = ast_hypotheses + llm_hypotheses
        filtered: list[str] = []

        for h in all_hypotheses:
            rejection = self._memory.was_rejected(module.name, h)
            if rejection:
                continue
            if self._memory.was_recently_accepted(module.name, h):
                continue
            filtered.append(h)

        return filtered

    async def run_experiment(
        self,
        module: CodeModule,
        hypothesis: str,
        log_fn: Optional[Any] = None,
    ) -> Optional[Experiment]:
        """Run a single experiment: generate and test an improvement."""
        log = log_fn or print
        exp_id = f"{module.name}_{hash(hypothesis) & 0xFFFF:04x}"

        # Generate improvement via LLM
        improvement = await self._generate_improvement(module, hypothesis)
        if not improvement:
            return None

        experiment = Experiment(
            id=exp_id,
            module=module,
            improvement=improvement,
            hypothesis=hypothesis,
        )

        # Test the improvement
        test_result = await self._test_agent.invoke(TestInput(
            experiment=experiment,
            require_type_check=self._config.require_type_check,
            require_tests_pass=self._config.require_tests_pass,
        ))

        if not test_result.passed:
            self._memory.record(
                module=module.name,
                hypothesis=hypothesis,
                description=improvement.description,
                outcome="rejected",
                rejection_reason=test_result.error,
            )
            return test_result.experiment

        # Judge against principles
        original_code = module.path.read_text()
        judge_result = await self._judge.invoke(JudgeInput(
            improvement=improvement,
            original_code=original_code,
            module_name=module.name,
        ))

        experiment.verdict = judge_result.verdict

        if judge_result.verdict.type == VerdictType.REJECT:
            experiment.status = ExperimentStatus.FAILED
            self._memory.record(
                module=module.name,
                hypothesis=hypothesis,
                description=improvement.description,
                outcome="rejected",
                rejection_reason=judge_result.verdict.reasoning,
            )
        elif judge_result.verdict.type == VerdictType.ACCEPT:
            self._memory.record(
                module=module.name,
                hypothesis=hypothesis,
                description=improvement.description,
                outcome="accepted",
            )

        return experiment

    async def _generate_improvement(
        self,
        module: CodeModule,
        hypothesis: str,
    ) -> Optional[CodeImprovement]:
        """Generate code improvement using LLM."""
        from runtime.base import AgentContext
        from .experiment import extract_metadata, extract_code

        code_content = get_code_preview(module.path)

        prompt = f"""You are a code improvement agent for kgents, a spec-first agent framework.

Your task is to generate ONE CONCRETE, WORKING code improvement based on a single hypothesis.

PRINCIPLES:
1. Agents are morphisms: A → B (clear input/output types)
2. Composable: Use >> for pipelines
3. Fix pattern: For retries
4. Tasteful: Less is more

OUTPUT FORMAT:

## METADATA
{{"description": "Brief description", "rationale": "Why", "improvement_type": "refactor|fix|feature|test", "confidence": 0.8}}

## CODE
```python
# Complete file content here
```

MODULE: {module.name}
CATEGORY: {module.category}

CURRENT CODE:
```python
{code_content}
```

HYPOTHESIS:
{hypothesis}

Generate ONE concrete improvement."""

        try:
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

        except Exception:
            return None

    async def process_module(
        self,
        module: CodeModule,
        log_fn: Optional[Any] = None,
    ) -> list[Experiment]:
        """Process a single module through the pipeline."""
        log = log_fn or print

        hypotheses = await self.generate_hypotheses(module, log_fn)
        if not hypotheses:
            return []

        experiments: list[Experiment] = []
        for hypothesis in hypotheses[:self._config.max_improvements_per_module]:
            exp = await self.run_experiment(module, hypothesis, log_fn)
            if exp:
                experiments.append(exp)

        return experiments

    async def run(
        self,
        modules: list[CodeModule],
        log_fn: Optional[Any] = None,
    ) -> EvolutionReport:
        """Run the full evolution pipeline on multiple modules."""
        log = log_fn or print
        start_time = time.time()

        # Process modules in parallel
        results = await asyncio.gather(
            *[self.process_module(module, log_fn) for module in modules],
            return_exceptions=True,
        )

        # Flatten results
        all_experiments: list[Experiment] = []
        for result in results:
            if isinstance(result, list):
                all_experiments.extend(result)
            elif isinstance(result, Exception):
                log(f"Module error: {result}")

        elapsed = time.time() - start_time

        # Categorize results
        incorporated: list[Experiment] = []
        rejected = [e for e in all_experiments if e.status == ExperimentStatus.FAILED]
        held = [e for e in all_experiments if e.status == ExperimentStatus.HELD]
        passed = [e for e in all_experiments if e.status == ExperimentStatus.PASSED]

        # Auto-apply if configured
        if self._config.auto_apply and not self._config.dry_run:
            for exp in passed:
                incorporate_result = await self._incorporate.invoke(IncorporateInput(
                    experiment=exp,
                    dry_run=self._config.dry_run,
                ))
                if incorporate_result.success:
                    incorporated.append(exp)

        summary = (
            f"Evolved {len(modules)} modules: "
            f"{len(incorporated)} incorporated, {len(rejected)} rejected, {len(held)} held"
        )

        return EvolutionReport(
            experiments=all_experiments,
            incorporated=incorporated,
            rejected=rejected,
            held=held,
            summary=summary,
            elapsed_seconds=elapsed,
        )


class EvolutionAgent(Agent[EvolutionInput, EvolutionReport]):
    """
    Evolution agent that wraps the pipeline for composition.

    Morphism: EvolutionInput → EvolutionReport

    This allows evolution to be composed with other agents:

        PreCheck >> Evolution >> PostCheck
    """

    def __init__(self, runtime: Optional[Any] = None):
        self._runtime = runtime

    @property
    def name(self) -> str:
        return "EvolutionAgent"

    async def invoke(self, input: EvolutionInput) -> EvolutionReport:
        """Run evolution pipeline."""
        pipeline = EvolutionPipeline(
            config=input.config,
            runtime=self._runtime,
        )
        return await pipeline.run(list(input.modules))


# Convenience factories

def evolution_agent(runtime: Optional[Any] = None) -> EvolutionAgent:
    """Create an evolution agent."""
    return EvolutionAgent(runtime)


def evolution_pipeline(config: Optional[EvolutionConfig] = None) -> EvolutionPipeline:
    """Create an evolution pipeline with default config."""
    return EvolutionPipeline(config or EvolutionConfig())
