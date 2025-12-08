"""
Regeneration Validation Test Harness

This test harness validates that BOOTSTRAP_PROMPT.md contains sufficient
information to regenerate the bootstrap system with behavior equivalence.

Philosophy:
- Test behavior, not implementation
- Allow style differences (names, comments, formatting)
- Require functional equivalence (same inputs → same outputs)
- Use Contradict agent to detect semantic tensions

Usage:
    # Phase 1: Capture reference behavior
    python test_regeneration.py capture

    # Phase 2: Regenerate bootstrap agents from docs
    # (Manual step: follow BOOTSTRAP_PROMPT.md)

    # Phase 3: Validate regenerated agents
    python test_regeneration.py validate

    # Phase 4: Generate report
    python test_regeneration.py report
"""

import asyncio
import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Bootstrap imports (current implementation)
from bootstrap import (
    make_default_principles,
    Id,
    compose,
    ComposedAgent,
    Ground,
    Contradict,
    Judge,
    JudgeInput,
    Sublate,
    Fix,
    FixConfig,
)
from bootstrap.types import (
    Agent,
    Tension,
    Verdict,
    Synthesis,
)


@dataclass
class TestCase:
    """A single test case for an agent."""
    agent_name: str
    input_data: Any
    expected_output_type: str
    description: str


@dataclass
class BehaviorSnapshot:
    """Captured behavior of an agent for a test case."""
    test_case: TestCase
    output: Any
    success: bool
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """Result of validating regenerated agent against reference."""
    test_case: TestCase
    reference_output: Any
    regenerated_output: Any
    passed: bool
    differences: List[str] = field(default_factory=list)
    tensions: List[Tension] = field(default_factory=list)


class RegenerationValidator:
    """Validates regenerated bootstrap agents against reference behavior."""

    def __init__(self, reference_dir: Path = Path("bootstrap_reference")):
        self.reference_dir = reference_dir
        self.reference_dir.mkdir(exist_ok=True)

    def get_test_cases(self) -> List[TestCase]:
        """Define test cases for each bootstrap agent."""
        return [
            # Id agent tests
            TestCase(
                agent_name="id",
                input_data="test_value",
                expected_output_type="str",
                description="Id should return input unchanged",
            ),
            TestCase(
                agent_name="id",
                input_data={"key": "value"},
                expected_output_type="dict",
                description="Id should handle dict inputs",
            ),

            # Compose agent tests
            TestCase(
                agent_name="compose",
                input_data=(Id[str](), Id[str]()),
                expected_output_type="Agent",
                description="Compose two Id agents",
            ),

            # Ground agent tests
            TestCase(
                agent_name="ground",
                input_data=None,
                expected_output_type="Facts",
                description="Ground should return Facts",
            ),

            # Judge agent tests
            TestCase(
                agent_name="judge",
                input_data=(Id[str](), make_default_principles()),
                expected_output_type="Verdict",
                description="Judge should evaluate Id agent",
            ),

            # Contradict agent tests
            TestCase(
                agent_name="contradict",
                input_data=("test1", "test1"),
                expected_output_type="Optional[Tension]",
                description="Contradict identical values (should be None)",
            ),
            TestCase(
                agent_name="contradict",
                input_data=("test1", "test2"),
                expected_output_type="Optional[Tension]",
                description="Contradict different values (may detect tension)",
            ),

            # Sublate agent tests
            # (Requires Tension input, will be tested in integration)

            # Fix agent tests
            TestCase(
                agent_name="fix",
                input_data=(lambda x: x if x > 10 else x + 1, 5, {"max_iterations": 10}),
                expected_output_type="Any",
                description="Fix should iterate until convergence",
            ),
        ]

    async def capture_reference_behavior(self) -> List[BehaviorSnapshot]:
        """Capture behavior of current bootstrap implementation."""
        print("="*60)
        print("CAPTURING REFERENCE BEHAVIOR")
        print("="*60)

        test_cases = self.get_test_cases()
        snapshots = []

        for test_case in test_cases:
            print(f"\n[{test_case.agent_name}] {test_case.description}")

            try:
                output = await self._execute_test_case(test_case)
                snapshot = BehaviorSnapshot(
                    test_case=test_case,
                    output=output,
                    success=True,
                )
                print(f"  ✓ Captured: {type(output).__name__}")

            except Exception as e:
                snapshot = BehaviorSnapshot(
                    test_case=test_case,
                    output=None,
                    success=False,
                    error=str(e),
                )
                print(f"  ✗ Error: {e}")

            snapshots.append(snapshot)

        # Save snapshots
        snapshot_file = self.reference_dir / "behavior_snapshots.pkl"
        with open(snapshot_file, "wb") as f:
            pickle.dump(snapshots, f)

        print(f"\n✓ Saved {len(snapshots)} snapshots to {snapshot_file}")
        return snapshots

    async def _execute_test_case(self, test_case: TestCase) -> Any:
        """Execute a single test case."""
        if test_case.agent_name == "id":
            agent = Id[type(test_case.input_data)]()
            return await agent.invoke(test_case.input_data)

        elif test_case.agent_name == "compose":
            agent1, agent2 = test_case.input_data
            composed = compose(agent1, agent2)
            return composed

        elif test_case.agent_name == "ground":
            agent = Ground()
            result = await agent.invoke(None)
            return result

        elif test_case.agent_name == "judge":
            agent_to_judge, principles = test_case.input_data
            judge = Judge()
            result = await judge.invoke(JudgeInput(agent=agent_to_judge, principles=principles))
            return result

        elif test_case.agent_name == "contradict":
            val1, val2 = test_case.input_data
            contradict = Contradict[type(val1), type(val2)]()
            result = await contradict.invoke((val1, val2))
            return result

        elif test_case.agent_name == "fix":
            transform, initial, config = test_case.input_data
            fix_agent = Fix[type(initial)](
                transform=transform,
                config=FixConfig(**config) if isinstance(config, dict) else config,
            )
            result = await fix_agent.invoke(initial)
            return result

        else:
            raise ValueError(f"Unknown agent: {test_case.agent_name}")

    async def validate_regenerated(self) -> List[ValidationResult]:
        """Validate regenerated agents against reference behavior."""
        print("="*60)
        print("VALIDATING REGENERATED AGENTS")
        print("="*60)

        # Load reference snapshots
        snapshot_file = self.reference_dir / "behavior_snapshots.pkl"
        if not snapshot_file.exists():
            raise FileNotFoundError(
                f"No reference snapshots found at {snapshot_file}. "
                "Run 'capture' first."
            )

        with open(snapshot_file, "rb") as f:
            reference_snapshots: List[BehaviorSnapshot] = pickle.load(f)

        print(f"Loaded {len(reference_snapshots)} reference snapshots")

        results = []
        for ref_snapshot in reference_snapshots:
            if not ref_snapshot.success:
                print(f"\n[{ref_snapshot.test_case.agent_name}] Skipping (reference failed)")
                continue

            print(f"\n[{ref_snapshot.test_case.agent_name}] {ref_snapshot.test_case.description}")

            try:
                regen_output = await self._execute_test_case(ref_snapshot.test_case)

                # Compare outputs
                passed, differences = self._compare_outputs(
                    ref_snapshot.output,
                    regen_output,
                )

                result = ValidationResult(
                    test_case=ref_snapshot.test_case,
                    reference_output=ref_snapshot.output,
                    regenerated_output=regen_output,
                    passed=passed,
                    differences=differences,
                )

                if passed:
                    print(f"  ✓ Behavior matches")
                else:
                    print(f"  ✗ Behavior differs:")
                    for diff in differences:
                        print(f"    - {diff}")

            except Exception as e:
                result = ValidationResult(
                    test_case=ref_snapshot.test_case,
                    reference_output=ref_snapshot.output,
                    regenerated_output=None,
                    passed=False,
                    differences=[f"Execution failed: {e}"],
                )
                print(f"  ✗ Error: {e}")

            results.append(result)

        return results

    def _compare_outputs(self, reference: Any, regenerated: Any) -> tuple[bool, List[str]]:
        """Compare two outputs for behavior equivalence."""
        differences = []

        # Type check
        if type(reference) != type(regenerated):
            differences.append(
                f"Type mismatch: {type(reference).__name__} vs {type(regenerated).__name__}"
            )
            return False, differences

        # Value equivalence (basic cases)
        if isinstance(reference, (str, int, float, bool, type(None))):
            if reference != regenerated:
                differences.append(f"Value mismatch: {reference} vs {regenerated}")
                return False, differences

        # Dict comparison
        elif isinstance(reference, dict):
            ref_keys = set(reference.keys())
            regen_keys = set(regenerated.keys())
            if ref_keys != regen_keys:
                differences.append(f"Dict keys differ: {ref_keys} vs {regen_keys}")
                return False, differences

            for key in ref_keys:
                if reference[key] != regenerated[key]:
                    differences.append(f"Dict value at '{key}': {reference[key]} vs {regenerated[key]}")
                    return False, differences

        # Agent comparison (check type and name)
        elif hasattr(reference, '__class__') and hasattr(reference, 'name'):
            if reference.__class__.__name__ != regenerated.__class__.__name__:
                differences.append(
                    f"Agent type: {reference.__class__.__name__} vs {regenerated.__class__.__name__}"
                )
                return False, differences

        # Verdict comparison
        elif hasattr(reference, 'type') and hasattr(reference, 'reasons'):
            if reference.type != regenerated.type:
                differences.append(f"Verdict type: {reference.type} vs {regenerated.type}")
                return False, differences

        # Default: structural equality
        else:
            if str(reference) != str(regenerated):
                differences.append(f"String repr differs: {str(reference)[:100]} vs {str(regenerated)[:100]}")
                return False, differences

        return True, differences

    def generate_report(self, results: List[ValidationResult]) -> str:
        """Generate validation report."""
        report = []
        report.append("="*60)
        report.append("REGENERATION VALIDATION REPORT")
        report.append("="*60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        report.append(f"Total tests: {total}")
        report.append(f"Passed: {passed} ({100*passed//total if total > 0 else 0}%)")
        report.append(f"Failed: {failed}")
        report.append("")

        if failed > 0:
            report.append("FAILURES:")
            report.append("-"*60)
            for result in results:
                if not result.passed:
                    report.append(f"\n[{result.test_case.agent_name}] {result.test_case.description}")
                    for diff in result.differences:
                        report.append(f"  - {diff}")
            report.append("")

        report.append("SUCCESS CRITERIA:")
        report.append(f"  {'✓' if passed == total else '✗'} All tests pass")
        report.append(f"  {'✓' if passed/total >= 0.9 else '✗'} >90% pass rate")
        report.append("")

        if passed == total:
            report.append("✓ REGENERATION VALIDATION PASSED")
            report.append("Documentation is sufficient to regenerate bootstrap system.")
        else:
            report.append("✗ REGENERATION VALIDATION FAILED")
            report.append("Documentation needs improvement for failed test cases.")

        return "\n".join(report)


async def main():
    """Main entry point."""
    import sys

    validator = RegenerationValidator()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_regeneration.py capture    # Capture reference behavior")
        print("  python test_regeneration.py validate   # Validate regenerated agents")
        print("  python test_regeneration.py report     # Generate report from last validation")
        return

    command = sys.argv[1]

    if command == "capture":
        await validator.capture_reference_behavior()

    elif command == "validate":
        results = await validator.validate_regenerated()

        # Save results
        results_file = validator.reference_dir / "validation_results.pkl"
        with open(results_file, "wb") as f:
            pickle.dump(results, f)

        print(f"\n✓ Saved {len(results)} results to {results_file}")

        # Generate and display report
        report = validator.generate_report(results)
        print("\n" + report)

        # Save report
        report_file = validator.reference_dir / "validation_report.txt"
        report_file.write_text(report)
        print(f"\n✓ Saved report to {report_file}")

    elif command == "report":
        results_file = validator.reference_dir / "validation_results.pkl"
        if not results_file.exists():
            print(f"No validation results found at {results_file}")
            print("Run 'validate' first.")
            return

        with open(results_file, "rb") as f:
            results = pickle.load(f)

        report = validator.generate_report(results)
        print(report)

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())
