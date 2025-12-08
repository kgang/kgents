"""
Incorporate Agent: Apply approved improvements to the codebase.

This agent handles the final stage of evolution:
1. Write improved code to the file
2. Create a git commit with descriptive message
3. Return incorporation result

Morphism: IncorporateInput → IncorporateResult

Safety features:
- Dry-run mode (preview without changes)
- Git safety (commit with message)
- Rollback support (via git)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from bootstrap.types import Agent

from .experiment import Experiment


@dataclass(frozen=True)
class IncorporateInput:
    """Input for incorporating an improvement."""
    experiment: Experiment
    dry_run: bool = False
    commit: bool = True
    commit_message_prefix: str = "evolve"


@dataclass(frozen=True)
class IncorporateResult:
    """Result of incorporating an improvement."""
    success: bool
    experiment: Experiment
    commit_sha: Optional[str] = None
    error: Optional[str] = None


class IncorporateAgent(Agent[IncorporateInput, IncorporateResult]):
    """
    Agent that incorporates approved improvements into the codebase.

    Morphism: IncorporateInput → IncorporateResult

    Usage:
        agent = IncorporateAgent()
        result = await agent.invoke(IncorporateInput(
            experiment=passed_experiment,
            dry_run=False,
            commit=True
        ))
        if result.success:
            print(f"Committed as {result.commit_sha}")
    """

    @property
    def name(self) -> str:
        return "IncorporateAgent"

    async def invoke(self, input: IncorporateInput) -> IncorporateResult:
        """Incorporate an approved improvement."""
        experiment = input.experiment

        if input.dry_run:
            return IncorporateResult(
                success=True,
                experiment=experiment,
                error=f"(dry-run) Would write to {experiment.module.path}",
            )

        try:
            # Write improved code
            experiment.module.path.write_text(experiment.improvement.code)

            commit_sha: Optional[str] = None

            if input.commit:
                # Git add
                subprocess.run(
                    ["git", "add", str(experiment.module.path)],
                    check=True,
                    capture_output=True,
                )

                # Git commit
                commit_msg = (
                    f"{input.commit_message_prefix}: {experiment.improvement.description}\n\n"
                    f"{experiment.improvement.rationale}"
                )
                subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    check=True,
                    capture_output=True,
                )

                # Get commit SHA
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                commit_sha = result.stdout.strip()[:8]

            return IncorporateResult(
                success=True,
                experiment=experiment,
                commit_sha=commit_sha,
            )

        except subprocess.CalledProcessError as e:
            return IncorporateResult(
                success=False,
                experiment=experiment,
                error=f"Git error: {e.stderr.decode() if e.stderr else str(e)}",
            )
        except Exception as e:
            return IncorporateResult(
                success=False,
                experiment=experiment,
                error=str(e),
            )


@dataclass(frozen=True)
class RollbackInput:
    """Input for rolling back changes."""
    file_path: Path
    commit_count: int = 1


@dataclass(frozen=True)
class RollbackResult:
    """Result of rollback."""
    success: bool
    error: Optional[str] = None


class RollbackAgent(Agent[RollbackInput, RollbackResult]):
    """
    Agent that rolls back changes using git.

    Morphism: RollbackInput → RollbackResult

    Usage:
        agent = RollbackAgent()
        result = await agent.invoke(RollbackInput(
            file_path=Path("module.py"),
            commit_count=1
        ))
    """

    @property
    def name(self) -> str:
        return "RollbackAgent"

    async def invoke(self, input: RollbackInput) -> RollbackResult:
        """Roll back changes to a file."""
        try:
            # Checkout file from HEAD~N
            subprocess.run(
                ["git", "checkout", f"HEAD~{input.commit_count}", "--", str(input.file_path)],
                check=True,
                capture_output=True,
            )
            return RollbackResult(success=True)
        except subprocess.CalledProcessError as e:
            return RollbackResult(
                success=False,
                error=f"Git error: {e.stderr.decode() if e.stderr else str(e)}",
            )
        except Exception as e:
            return RollbackResult(success=False, error=str(e))


# Convenience factories

def incorporate_agent() -> IncorporateAgent:
    """Create an incorporate agent."""
    return IncorporateAgent()


def rollback_agent() -> RollbackAgent:
    """Create a rollback agent."""
    return RollbackAgent()
