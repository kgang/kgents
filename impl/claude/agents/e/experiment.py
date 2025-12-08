"""
Experiment Agent: Generate and test code improvements.

This agent handles the experiment phase of evolution:
1. Generate code improvements from hypotheses
2. Test improvements (syntax, types, tests)
3. Return structured experiment results

Morphism: ExperimentInput → ExperimentResult
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, cast

from bootstrap.types import Agent, Verdict


@dataclass(frozen=True)
class CodeModule:
    """A module in the codebase to evolve."""
    name: str
    category: str
    path: Path

    def __post_init__(self) -> None:
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
    test_results: Optional[dict[str, str]] = None
    verdict: Optional[Verdict] = None
    synthesis: Optional[Any] = None  # Synthesis from sublate
    error: Optional[str] = None


@dataclass(frozen=True)
class ExperimentInput:
    """Input for experiment generation."""
    module: CodeModule
    hypothesis: str
    code_preview: str  # Preview of current code
    ast_context: str = ""  # Optional AST analysis context


@dataclass(frozen=True)
class ExperimentResult:
    """Result of an experiment."""
    experiment: Optional[Experiment]
    error: Optional[str] = None


@dataclass(frozen=True)
class TestInput:
    """Input for testing an experiment."""
    experiment: Experiment
    require_type_check: bool = True
    require_tests_pass: bool = True


@dataclass(frozen=True)
class TestResult:
    """Result of testing an experiment."""
    passed: bool
    experiment: Experiment  # Updated experiment with results
    error: Optional[str] = None


# Code extraction utilities

def extract_metadata(response: str, module_name: str) -> Optional[dict[str, Any]]:
    """Extract metadata JSON from LLM response with flexible parsing."""
    patterns = [
        r"##\s*METADATA\s*\n(.*?)(?=##\s*CODE|$)",
        r"METADATA[:\s]*\n(.*?)(?=CODE|```python|$)",
        r"\{[^{}]*\"description\"[^{}]*\}",
    ]

    metadata_text = None
    for pattern in patterns[:2]:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            metadata_text = match.group(1).strip()
            break

    if metadata_text:
        json_obj = _extract_json_object(metadata_text)
        if json_obj:
            return json_obj

    match = re.search(patterns[2], response, re.DOTALL)
    if match:
        try:
            return cast(dict[str, Any], json.loads(match.group(0)))
        except json.JSONDecodeError:
            pass

    return None


def _extract_json_object(text: str) -> Optional[dict[str, Any]]:
    """Extract a JSON object from text that may have surrounding content."""
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i, char in enumerate(text[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                json_str = text[start: i + 1]
                try:
                    return cast(dict[str, Any], json.loads(json_str))
                except json.JSONDecodeError:
                    cleaned = _clean_json_string(json_str)
                    try:
                        return cast(dict[str, Any], json.loads(cleaned))
                    except json.JSONDecodeError:
                        return None
    return None


def _clean_json_string(json_str: str) -> str:
    """Clean common JSON issues from LLM output."""
    cleaned = re.sub(r",\s*([}\]])", r"\1", json_str)

    def fix_newlines(match: re.Match[str]) -> str:
        content = match.group(1)
        return '"' + content.replace("\n", "\\n") + '"'

    cleaned = re.sub(r'"([^"]*\n[^"]*)"', fix_newlines, cleaned)
    return cleaned


def extract_code(response: str, module_name: str) -> Optional[str]:
    """Extract Python code from LLM response with flexible parsing."""
    patterns = [
        r"##\s*CODE.*?```python\s*\n(.*?)```",
        r"CODE.*?```python\s*\n(.*?)```",
        r"```(?:python|py)\s*\n(.*?)```",
        r"```\s*\n(.*?)```",
    ]

    for pattern in patterns:
        match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
        if match:
            code = match.group(1).strip()
            if _looks_like_python(code):
                return code

    return None


def _looks_like_python(code: str) -> bool:
    """Quick heuristic check if code looks like valid Python."""
    if not code or len(code) < 20:
        return False

    python_indicators = [
        "import ", "from ", "def ", "class ", "async def ",
        "if __name__", "return ", "self.", "@dataclass", "@"
    ]
    return any(indicator in code for indicator in python_indicators)


def get_code_preview(path: Path, max_lines: int = 200) -> str:
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


class TestAgent(Agent[TestInput, TestResult]):
    """
    Agent that tests experimental improvements.

    Morphism: TestInput → TestResult

    Runs:
    1. Syntax check (py_compile)
    2. Type check (mypy --ignore-missing-imports)
    3. Unit tests (if exist)
    """

    @property
    def name(self) -> str:
        return "TestAgent"

    async def invoke(self, input: TestInput) -> TestResult:
        """Test an experimental improvement."""
        experiment = input.experiment
        experiment.status = ExperimentStatus.RUNNING

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
                return TestResult(passed=False, experiment=experiment, error=experiment.error)

            # 2. Type check (if required)
            if input.require_type_check:
                result = subprocess.run(
                    [sys.executable, "-m", "mypy", str(tmp_path), "--ignore-missing-imports"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    experiment.status = ExperimentStatus.FAILED
                    experiment.error = f"Type error: {result.stdout}"
                    return TestResult(passed=False, experiment=experiment, error=experiment.error)

            # 3. Run tests (if exist and required)
            if input.require_tests_pass:
                test_path = experiment.module.path.parent / f"test_{experiment.module.name}.py"
                if test_path.exists():
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
                            return TestResult(passed=False, experiment=experiment, error=experiment.error)
                    finally:
                        experiment.module.path.write_text(original_code)

            experiment.status = ExperimentStatus.PASSED
            experiment.test_results = {"syntax": "pass", "types": "pass", "tests": "pass"}
            return TestResult(passed=True, experiment=experiment)

        except Exception as e:
            experiment.status = ExperimentStatus.FAILED
            experiment.error = str(e)
            return TestResult(passed=False, experiment=experiment, error=str(e))

        finally:
            tmp_path.unlink()


# Convenience factories

def test_agent() -> TestAgent:
    """Create a test agent."""
    return TestAgent()
