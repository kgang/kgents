# mypy: ignore-errors
"""
ASHC Bootstrap Regenerator

The main pipeline for regenerating bootstrap agents from spec
and verifying behavioral isomorphism.

Usage:
    regenerator = BootstrapRegenerator()
    result = await regenerator.regenerate()

    if result.is_isomorphic:
        print("Bootstrap can be regenerated from spec! ✓")
    else:
        print(f"Differences found: {result.summary()}")

> "The kernel that proves itself is the kernel that trusts itself."
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from ..harness import (
    GenerationResult,
    TokenBudget,
    VoidHarness,
    VoidHarnessConfig,
)
from .isomorphism import (
    BehaviorComparison,
    BootstrapIsomorphism,
    check_isomorphism,
)
from .parser import (
    AGENT_NAMES,
    BootstrapAgentSpec,
    parse_bootstrap_spec,
)

# =============================================================================
# Configuration
# =============================================================================


@dataclass
class RegenerationConfig:
    """Configuration for bootstrap regeneration."""

    # Generation settings
    n_variations: int = 3  # Generate multiple for confidence
    select_best: bool = True  # Pick best variation per agent

    # Verification settings
    run_tests: bool = True
    run_types: bool = True
    verify_laws: bool = True

    # Token budget
    max_tokens: int = 100_000
    warn_at_tokens: int = 50_000

    # Harness settings
    harness_config: VoidHarnessConfig | None = None


# =============================================================================
# Generation Prompts
# =============================================================================


def make_generation_prompt(spec: BootstrapAgentSpec) -> str:
    """
    Build generation prompt from agent spec.

    The prompt is self-contained since we're running in a void directory
    with no CLAUDE.md context.
    """
    laws_text = "\n".join(f"- {law}" for law in spec.laws) if spec.laws else "None specified"

    return f'''You are generating a Python implementation for the {spec.name} bootstrap agent.

## Type Signature
{spec.signature}

## Laws That MUST Be Satisfied
{laws_text}

## Required Interface

The agent MUST:
1. Inherit from Agent[A, B] base class
2. Implement async def invoke(self, input: A) -> B
3. Have a @property name that returns the agent's name as string
4. Be importable as: from module import {spec.name}

## Base Class (use this exact pattern)

```python
from typing import TypeVar, Generic

A = TypeVar("A")
B = TypeVar("B")

class Agent(Generic[A, B]):
    """Base agent type."""

    @property
    def name(self) -> str:
        raise NotImplementedError

    async def invoke(self, input: A) -> B:
        raise NotImplementedError
```

## Specification Details
{spec.description}

## Full Specification Context
{spec.section_content}

## Output Instructions
Generate ONLY the Python code. Include:
- All necessary imports
- The Agent base class definition (as shown above)
- The {spec.name} class implementing Agent
- Proper type hints throughout
- Docstrings explaining the implementation

Do NOT include:
- Markdown formatting
- Explanations outside the code
- Test code

```python
'''


def make_simple_prompt(spec: BootstrapAgentSpec) -> str:
    """
    Simplified prompt for basic agents like Id.

    Less verbose, works well for straightforward implementations.
    """
    return f'''Generate a Python {spec.name} agent.

Signature: {spec.signature}

Requirements:
1. Class {spec.name} with async invoke(self, input) method
2. Property name returning "{spec.name}"
3. Must satisfy: {", ".join(spec.laws[:3]) if spec.laws else "basic functionality"}

Example structure:
```python
from typing import TypeVar, Generic

A = TypeVar("A")
B = TypeVar("B")

class Agent(Generic[A, B]):
    @property
    def name(self) -> str:
        raise NotImplementedError

    async def invoke(self, input: A) -> B:
        raise NotImplementedError

class {spec.name}(Agent[...]):
    # Your implementation
```

Output only Python code:
```python
'''


# =============================================================================
# Bootstrap Regenerator
# =============================================================================


class BootstrapRegenerator:
    """
    Regenerate bootstrap from spec using VoidHarness.

    This is the main entry point for Phase 5 bootstrap regeneration.
    """

    def __init__(
        self,
        spec_path: Path | None = None,
        config: RegenerationConfig | None = None,
    ):
        """
        Initialize the regenerator.

        Args:
            spec_path: Path to spec/bootstrap.md
            config: Regeneration configuration
        """
        self.spec_path = spec_path
        self.config = config or RegenerationConfig()

        # Initialize harness with budget
        budget = TokenBudget(
            max_tokens=self.config.max_tokens,
            warn_at_tokens=self.config.warn_at_tokens,
        )
        harness_config = self.config.harness_config or VoidHarnessConfig()
        self._harness = VoidHarness(harness_config, budget)

        # Cache for specs
        self._specs: tuple[BootstrapAgentSpec, ...] | None = None

    @property
    def specs(self) -> tuple[BootstrapAgentSpec, ...]:
        """Lazy-loaded parsed specs."""
        if self._specs is None:
            self._specs = parse_bootstrap_spec(self.spec_path)
        return self._specs

    async def regenerate(
        self,
        agents: list[str] | None = None,
    ) -> BootstrapIsomorphism:
        """
        Regenerate bootstrap and check isomorphism.

        Args:
            agents: List of agent names to regenerate. None = all 7.

        Returns:
            BootstrapIsomorphism with all comparison results
        """
        start_time = time.monotonic()

        # Determine which agents to regenerate
        agent_names = agents or AGENT_NAMES

        comparisons: list[BehaviorComparison] = []

        for name in agent_names:
            # Get spec for this agent
            spec = next((s for s in self.specs if s.name == name), None)
            if spec is None:
                comparisons.append(
                    BehaviorComparison(
                        agent_name=name,
                        test_pass_rate=0.0,
                        type_compatible=False,
                        laws_satisfied=False,
                        property_tests_pass=False,
                        error=f"No spec found for {name}",
                    )
                )
                continue

            # Generate variations
            generated = await self._generate_agent(spec)

            if not generated:
                comparisons.append(
                    BehaviorComparison(
                        agent_name=name,
                        test_pass_rate=0.0,
                        type_compatible=False,
                        laws_satisfied=False,
                        property_tests_pass=False,
                        error="Generation failed",
                    )
                )
                continue

            # Check isomorphism
            comparison = await check_isomorphism(
                generated_code=generated,
                agent_name=name,
                run_tests=self.config.run_tests,
                run_types=self.config.run_types,
            )
            comparisons.append(comparison)

        elapsed_ms = (time.monotonic() - start_time) * 1000

        return BootstrapIsomorphism(
            comparisons=tuple(comparisons),
            regeneration_time_ms=elapsed_ms,
            tokens_used=self._harness.tokens_used,
            generation_count=self._harness.generation_count,
        )

    async def regenerate_agent(
        self,
        name: str,
    ) -> BehaviorComparison:
        """
        Regenerate a single agent.

        Convenience method for testing individual agents.
        """
        result = await self.regenerate(agents=[name])
        return (
            result.comparisons[0]
            if result.comparisons
            else BehaviorComparison(
                agent_name=name,
                test_pass_rate=0.0,
                type_compatible=False,
                laws_satisfied=False,
                property_tests_pass=False,
                error="Regeneration failed",
            )
        )

    async def _generate_agent(
        self,
        spec: BootstrapAgentSpec,
    ) -> str | None:
        """
        Generate implementation for an agent spec.

        Generates n_variations and selects the best one.
        """
        # Use simple prompt for basic agents
        if spec.name in ["Id", "Compose"]:
            prompt = make_simple_prompt(spec)
        else:
            prompt = make_generation_prompt(spec)

        if self.config.n_variations == 1:
            # Single generation
            try:
                return await self._harness.generate(prompt)
            except Exception:
                return None

        # Multiple variations
        results = await self._harness.generate_n(prompt, self.config.n_variations)

        # Filter successful generations
        successful: list[str] = []
        for result in results:
            if isinstance(result, GenerationResult) and result.success:
                successful.append(result.code)

        if not successful:
            return None

        if self.config.select_best and len(successful) > 1:
            # Select best based on quick heuristics
            return self._select_best(successful, spec)

        return successful[0]

    def _select_best(
        self,
        codes: list[str],
        spec: BootstrapAgentSpec,
    ) -> str:
        """
        Select the best code from multiple generations.

        Uses heuristics like:
        - Contains agent class name
        - Has invoke method
        - Has name property
        - Reasonable length (not too short, not too long)
        """

        def score(code: str) -> float:
            s = 0.0
            # Contains class definition
            if f"class {spec.name}" in code:
                s += 2.0
            # Contains invoke
            if "async def invoke" in code or "def invoke" in code:
                s += 1.0
            # Contains name property
            if "@property" in code and "name" in code:
                s += 1.0
            # Has docstring
            if '"""' in code or "'''" in code:
                s += 0.5
            # Reasonable length (prefer medium-length)
            length = len(code)
            if 200 < length < 2000:
                s += 0.5
            elif length < 100:
                s -= 1.0  # Too short
            elif length > 5000:
                s -= 0.5  # Too long
            return s

        return max(codes, key=score)


# =============================================================================
# Convenience Functions
# =============================================================================


async def regenerate_bootstrap(
    agents: list[str] | None = None,
    config: RegenerationConfig | None = None,
) -> BootstrapIsomorphism:
    """
    Quick regeneration of bootstrap.

    Args:
        agents: List of agent names to regenerate. None = all 7.
        config: Optional configuration.

    Returns:
        BootstrapIsomorphism result.
    """
    regenerator = BootstrapRegenerator(config=config)
    return await regenerator.regenerate(agents)


async def regenerate_single(
    agent_name: str,
    config: RegenerationConfig | None = None,
) -> BehaviorComparison:
    """
    Regenerate a single agent.

    Args:
        agent_name: Name of agent to regenerate (Id, Compose, etc.)
        config: Optional configuration.

    Returns:
        BehaviorComparison for the agent.
    """
    regenerator = BootstrapRegenerator(config=config)
    return await regenerator.regenerate_agent(agent_name)


# =============================================================================
# CLI Entry Point
# =============================================================================


def main() -> None:
    """CLI entry point for bootstrap regeneration."""
    import asyncio

    print("ASHC Bootstrap Regeneration")
    print("=" * 40)

    # Check if harness is available
    if not VoidHarness.is_available():
        print("ERROR: Claude CLI not available")
        print("Install with: npm install -g @anthropic/claude")
        return 1

    # Run regeneration
    result = asyncio.run(regenerate_bootstrap(agents=["Id"]))  # Start with Id

    print(result.summary())

    return 0 if result.is_isomorphic else 1


if __name__ == "__main__":
    exit(main())


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "RegenerationConfig",
    "BootstrapRegenerator",
    "regenerate_bootstrap",
    "regenerate_single",
    "make_generation_prompt",
    "make_simple_prompt",
]
