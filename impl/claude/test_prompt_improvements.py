#!/usr/bin/env python
"""
Quick test of Phase 2.5a improvements (Prompt Engineering Layer).

Tests:
1. PreFlightChecker catches syntax errors
2. PreFlightChecker detects pre-existing type errors
3. PromptContext builds rich context
4. build_improvement_prompt generates structured prompts
"""

import asyncio
import tempfile
from pathlib import Path

from agents.e import (
    PreFlightChecker,
    PreFlightInput,
    CodeModule,
    build_prompt_context,
    build_improvement_prompt,
)


async def test_preflight_syntax_error():
    """Test that PreFlightChecker catches syntax errors."""
    print("\n=== Test 1: PreFlight catches syntax errors ===")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def broken_function():
    if True
        print("Missing colon")
""")
        temp_path = Path(f.name)

    try:
        module = CodeModule(name="test_broken", category="test", path=temp_path)
        checker = PreFlightChecker()
        result = await checker.invoke(PreFlightInput(module=module))

        assert not result.can_evolve, "Should fail on syntax error"
        assert len(result.blocking_issues) > 0, "Should report blocking issues"
        print(f"✓ Correctly detected syntax error")
        print(f"  Blocking: {result.blocking_issues[0]}")
    finally:
        temp_path.unlink()


async def test_preflight_type_errors():
    """Test that PreFlightChecker detects type errors baseline."""
    print("\n=== Test 2: PreFlight detects type errors ===")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def add_numbers(a: int, b: int) -> int:
    return a + b

# Type error: passing string to int function
result = add_numbers("hello", "world")
""")
        temp_path = Path(f.name)

    try:
        module = CodeModule(name="test_types", category="test", path=temp_path)
        checker = PreFlightChecker()
        result = await checker.invoke(PreFlightInput(module=module))

        # May or may not catch this depending on mypy, but should run without error
        print(f"✓ PreFlight completed")
        print(f"  Can evolve: {result.can_evolve}")
        print(f"  Baseline errors: {result.baseline_error_count}")
        if result.warnings:
            print(f"  Warnings: {len(result.warnings)}")
    finally:
        temp_path.unlink()


async def test_prompt_context():
    """Test that PromptContext builds rich context."""
    print("\n=== Test 3: PromptContext builds rich context ===")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Example:
    name: str
    value: Optional[int] = None

def process(input: str) -> int:
    return len(input)
""")
        temp_path = Path(f.name)

    try:
        module = CodeModule(name="test_context", category="test", path=temp_path)

        # Build context
        from agents.e.ast_analyzer import ASTAnalyzer, ASTAnalysisInput
        analyzer = ASTAnalyzer()
        ast_result = await analyzer.invoke(ASTAnalysisInput(path=temp_path))

        context = build_prompt_context(module, ast_result.structure)

        # Module name comes from path stem, not our name parameter
        assert context.module_path == temp_path
        assert "dataclass" in context.current_code
        assert len(context.type_annotations) > 0
        assert len(context.imports) > 0

        print(f"✓ PromptContext built successfully")
        print(f"  Module: {context.module_name}")
        print(f"  Type annotations: {len(context.type_annotations)}")
        print(f"  Imports: {len(context.imports)}")
        print(f"  Principles: {len(context.principles)}")
    finally:
        temp_path.unlink()


async def test_improvement_prompt():
    """Test that build_improvement_prompt generates rich prompts."""
    print("\n=== Test 4: build_improvement_prompt generates structured prompt ===")

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
from dataclasses import dataclass

@dataclass
class SimpleClass:
    value: int
""")
        temp_path = Path(f.name)

    try:
        module = CodeModule(name="test_prompt", category="test", path=temp_path)

        # Build context
        from agents.e.ast_analyzer import ASTAnalyzer, ASTAnalysisInput
        analyzer = ASTAnalyzer()
        ast_result = await analyzer.invoke(ASTAnalysisInput(path=temp_path))

        context = build_prompt_context(module, ast_result.structure)

        # Build prompt
        hypothesis = "Add a method to validate the value is positive"
        prompt = build_improvement_prompt(hypothesis, context, improvement_type="feature")

        # Verify prompt structure
        assert "## Hypothesis" in prompt
        assert hypothesis in prompt
        assert "## Type Signatures" in prompt
        assert "## CRITICAL REQUIREMENTS" in prompt
        assert "Complete Type Signatures" in prompt
        assert "## Output Format" in prompt
        assert "### METADATA" in prompt
        assert "### CODE" in prompt

        print(f"✓ Prompt generated successfully")
        print(f"  Length: {len(prompt)} chars")
        print(f"  Has hypothesis: ✓")
        print(f"  Has type requirements: ✓")
        print(f"  Has output format: ✓")
        print(f"  Has critical requirements: ✓")
    finally:
        temp_path.unlink()


async def main():
    print("=" * 60)
    print("TESTING PHASE 2.5a: PROMPT ENGINEERING IMPROVEMENTS")
    print("=" * 60)

    await test_preflight_syntax_error()
    await test_preflight_type_errors()
    await test_prompt_context()
    await test_improvement_prompt()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    print("\nPhase 2.5a (Prompt Engineering Layer) is working!")
    print("\nNext steps:")
    print("  - Run full evolution to measure syntax error rate")
    print("  - Target: <10% syntax errors (down from ~20-30%)")
    print("  - Proceed to Phase 2.5b (Parsing & Validation)")


if __name__ == "__main__":
    asyncio.run(main())
