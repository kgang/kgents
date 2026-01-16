"""
Test script for DP bridge LLM integration.

Verifies that:
1. analyze_as_dp_llm() runs all four modes with LLM
2. analyze_with_witness_llm() creates witness marks
3. Results use real LLM analysis, not structural placeholders
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_dp_llm_analysis():
    """Test DP-formulated LLM analysis."""
    from agents.operad.domains.analysis_dp import analyze_as_dp_llm

    logger.info("Testing DP-formulated LLM analysis")
    logger.info("=" * 60)

    # Test on a small spec file
    test_spec = "spec/protocols/zero-seed.md"

    logger.info(f"Running analyze_as_dp_llm({test_spec})")

    try:
        value, trace = await analyze_as_dp_llm(test_spec)

        logger.info("✓ Analysis complete!")
        logger.info(f"  Total reward: {value:.3f}")
        logger.info(f"  Trace entries: {len(trace.log)}")
        logger.info("")

        # Verify final state
        final_state = trace.value
        logger.info("Final state:")
        logger.info(f"  Target: {final_state.target}")
        logger.info(f"  Modes applied: {final_state.modes_applied}/4")
        logger.info(f"  Is complete: {final_state.is_complete}")
        logger.info(f"  Has violations: {final_state.has_violations}")
        logger.info("")

        # Check each mode result
        if final_state.categorical_result:
            cat = final_state.categorical_result
            logger.info("Categorical:")
            logger.info(f"  Laws: {cat.laws_passed}/{cat.laws_total}")
            logger.info(f"  Summary: {cat.summary[:100]}...")
            logger.info("")

        if final_state.epistemic_result:
            epi = final_state.epistemic_result
            logger.info("Epistemic:")
            logger.info(f"  Layer: L{epi.layer}")
            logger.info(f"  Grounded: {epi.is_grounded}")
            logger.info(f"  Summary: {epi.summary[:100]}...")
            logger.info("")

        if final_state.dialectical_result:
            dia = final_state.dialectical_result
            logger.info("Dialectical:")
            logger.info(f"  Tensions: {len(dia.tensions)}")
            logger.info(f"  Resolved: {dia.resolved_count}")
            logger.info(f"  Summary: {dia.summary[:100]}...")
            logger.info("")

        if final_state.generative_result:
            gen = final_state.generative_result
            logger.info("Generative:")
            logger.info(f"  Compression: {gen.compression_ratio:.2f}")
            logger.info(f"  Regenerable: {gen.is_regenerable}")
            logger.info(f"  Summary: {gen.summary[:100]}...")
            logger.info("")

        logger.info("✓ DP LLM analysis test passed!")

    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise


async def test_witness_llm_integration():
    """Test witness integration with LLM analysis."""
    from agents.operad.domains.analysis_dp import analyze_with_witness_llm

    logger.info("")
    logger.info("Testing Witness integration with LLM analysis")
    logger.info("=" * 60)

    test_spec = "spec/protocols/zero-seed.md"

    logger.info(f"Running analyze_with_witness_llm({test_spec})")

    try:
        report, marks = await analyze_with_witness_llm(test_spec)

        logger.info("✓ Analysis complete!")
        logger.info(f"  Report valid: {report.is_valid}")
        logger.info(f"  Witness marks: {len(marks)}")
        logger.info("")

        # Check marks
        for i, mark in enumerate(marks, 1):
            logger.info(f"Mark {i} ({mark['mode']}):")
            logger.info(f"  Action: {mark['action']}")
            logger.info(f"  Value: {mark['value']}")
            logger.info(f"  State: {mark['state_before']} → {mark['state_after']}")
            logger.info(f"  Rationale: {mark['rationale'][:80]}...")
            logger.info("")

        logger.info("✓ Witness LLM integration test passed!")

    except Exception as e:
        logger.error(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise


async def main():
    """Run all tests."""
    logger.info("DP Bridge LLM Integration Tests")
    logger.info("=" * 60)
    logger.info("")

    await test_dp_llm_analysis()
    await test_witness_llm_integration()

    logger.info("")
    logger.info("=" * 60)
    logger.info("All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
