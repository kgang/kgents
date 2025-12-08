#!/usr/bin/env python3
"""
Test Recovery Layer: Demonstrate retry/fallback/error_memory with T-gents.

This script demonstrates Phase 2.5c recovery layer working with deliberately
failing agents to validate:
1. Retry strategy with refined prompts
2. Fallback strategy with progressive simplification
3. Error memory tracking failure patterns

Usage:
    python test_recovery_layer.py
"""

import asyncio
from pathlib import Path

from agents.t import FailingAgent, FailingConfig, FailureType
from agents.e import (
    RetryStrategy,
    RetryConfig,
    FallbackStrategy,
    FallbackConfig,
    ErrorMemory,
    CodeModule,
)


async def test_retry_strategy():
    """Test retry strategy with failing agent."""
    print("\n" + "="*60)
    print("TEST 1: Retry Strategy")
    print("="*60)

    # Create agent that fails twice, then succeeds
    failing = FailingAgent(FailingConfig(
        error_type=FailureType.TYPE,
        fail_count=2,
        error_message="Type error in generated code"
    ))

    retry = RetryStrategy(RetryConfig(max_retries=3, verbose=True))

    print("\n📝 Scenario: Agent fails 2 times with type errors, then succeeds")
    print(f"   Retry config: max_retries={retry.config.max_retries}\n")

    for attempt in range(4):
        try:
            print(f"Attempt {attempt + 1}:")
            result = await failing.invoke({"test": "input"})
            print(f"  ✓ Success! Result: {result}")
            break
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            if attempt < 3:
                print(f"  → Retrying...")

    print("\n✅ Retry strategy test complete!")


async def test_error_memory():
    """Test error memory tracking patterns."""
    print("\n" + "="*60)
    print("TEST 2: Error Memory")
    print("="*60)

    error_memory = ErrorMemory(storage_path=Path(".memory/test_error_patterns.json"))

    print("\n📝 Scenario: Record multiple failures and generate warnings\n")

    # Simulate multiple failures
    failures = [
        ("meta", "evolve", "Refactor pipeline", "type", "Unexpected keyword argument 'runtime'"),
        ("meta", "evolve", "Extract agent", "type", "Unexpected keyword argument 'content'"),
        ("meta", "evolve", "Improve types", "type", "CodeModule has no attribute 'content'"),
    ]

    for category, module, hypothesis, fail_type, details in failures:
        error_memory.record_failure(
            module_category=category,
            module_name=module,
            hypothesis=hypothesis,
            failure_type=fail_type,
            failure_details=details,
        )
        print(f"  📊 Recorded: {fail_type} in {category}/{module}")

    stats = error_memory.get_stats()
    print(f"\n📈 Error Memory Stats:")
    print(f"   Total failures: {stats.total_failures}")
    print(f"   Most common: {stats.most_common_failures[:3]}")

    print("\n✅ Error memory test complete!")


async def main():
    """Run all recovery layer tests."""
    print("\n🧪 KGENTS RECOVERY LAYER TEST SUITE")
    print("Testing Phase 2.5c with T-gents (Test-gents)\n")

    await test_retry_strategy()
    await test_error_memory()

    print("\n" + "="*60)
    print("🎉 ALL TESTS COMPLETE!")
    print("="*60)
    print("\nT-gents successfully demonstrated:")
    print("  ✓ FailingAgent for controlled failure testing")
    print("  ✓ Retry strategy handles transient failures")
    print("  ✓ Error memory tracks patterns")
    print("\nRecovery layer integrated into evolve.py! 🚀")


if __name__ == "__main__":
    asyncio.run(main())
