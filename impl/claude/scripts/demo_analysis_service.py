#!/usr/bin/env python3
"""
Demo: LLM-backed Analysis Service

This script demonstrates the four-mode analysis service analyzing
the Analysis Operad specification itself (meta-analysis).

Usage:
    cd impl/claude
    uv run python scripts/demo_analysis_service.py

Requirements:
    - ANTHROPIC_API_KEY environment variable set
    - spec/theory/analysis-operad.md exists

Output:
    - Full analysis report with all four modes
    - Synthesis verdict
    - Individual mode summaries
"""

from __future__ import annotations

import asyncio
import logging

from agents.k.soul import create_llm_client
from services.analysis import AnalysisService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def demo_self_analysis():
    """
    Demonstrate self-analysis: Analysis Operad analyzing itself.

    This is the ultimate test of meta-applicability.
    """
    logger.info("=== LLM-Backed Analysis Service Demo ===")
    logger.info("Target: spec/theory/analysis-operad.md (self-analysis)")

    # Create LLM client
    logger.info("Creating LLM client...")
    llm = create_llm_client()

    # Create analysis service
    service = AnalysisService(llm)

    # Perform full four-mode analysis
    logger.info("Starting full analysis (this may take 30-60 seconds)...")
    report = await service.analyze_full("spec/theory/analysis-operad.md")

    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("FULL ANALYSIS REPORT")
    logger.info("=" * 80)

    logger.info(f"\nTarget: {report.target}")
    logger.info(f"Valid: {report.is_valid}")

    logger.info("\n--- Synthesis ---")
    logger.info(report.synthesis)

    logger.info("\n--- Categorical Analysis ---")
    logger.info(f"Laws Extracted: {len(report.categorical.laws_extracted)}")
    logger.info(f"Laws Verified: {report.categorical.laws_passed}/{report.categorical.laws_total}")
    logger.info(
        f"Fixed Point: {report.categorical.fixed_point.description if report.categorical.fixed_point else 'None'}"
    )
    logger.info(f"Summary: {report.categorical.summary}")

    logger.info("\n--- Epistemic Analysis ---")
    logger.info(f"Layer: L{report.epistemic.layer}")
    logger.info(f"Grounded: {report.epistemic.is_grounded}")
    logger.info(f"Claim: {report.epistemic.toulmin.claim}")
    logger.info(f"Bootstrap Valid: {report.epistemic.has_valid_bootstrap}")
    logger.info(f"Summary: {report.epistemic.summary}")

    logger.info("\n--- Dialectical Analysis ---")
    logger.info(f"Tensions Found: {len(report.dialectical.tensions)}")
    logger.info(f"Resolved: {report.dialectical.resolved_count}")
    logger.info(f"Problematic: {report.dialectical.problematic_count}")
    logger.info(f"Paraconsistent: {report.dialectical.paraconsistent_count}")
    logger.info(f"Summary: {report.dialectical.summary}")

    logger.info("\n--- Generative Analysis ---")
    logger.info(f"Compression Ratio: {report.generative.compression_ratio:.2f}")
    logger.info(f"Compressed: {report.generative.is_compressed}")
    logger.info(f"Regenerable: {report.generative.is_regenerable}")
    logger.info(f"Primitives: {', '.join(sorted(report.generative.grammar.primitives)[:5])}")
    logger.info(f"Minimal Kernel: {len(report.generative.minimal_kernel)} axioms")
    logger.info(f"Summary: {report.generative.summary}")

    logger.info("\n" + "=" * 80)

    return report


async def demo_single_mode():
    """
    Demonstrate single-mode analysis (categorical only).

    Faster than full analysis, useful for targeted inspection.
    """
    logger.info("\n=== Single Mode Analysis Demo ===")
    logger.info("Target: spec/theory/analysis-operad.md (categorical only)")

    llm = create_llm_client()
    service = AnalysisService(llm)

    logger.info("Running categorical analysis...")
    report = await service.analyze_categorical("spec/theory/analysis-operad.md")

    logger.info(f"\nLaws Extracted: {len(report.laws_extracted)}")
    for law in report.laws_extracted[:3]:  # Show first 3
        logger.info(f"  - {law.name}: {law.equation}")

    logger.info(f"\nVerifications: {report.laws_passed}/{report.laws_total} passed")
    for v in report.law_verifications[:3]:  # Show first 3
        logger.info(f"  - {v.law_name}: {v.status.name}")

    if report.fixed_point:
        logger.info(f"\nFixed Point: {report.fixed_point.description}")

    logger.info(f"\n{report.summary}")

    return report


async def main():
    """Run all demos."""
    try:
        # Full analysis (meta-applicability test)
        await demo_self_analysis()

        # Single mode analysis
        await demo_single_mode()

        logger.info("\n✅ Demo complete!")

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        logger.error("Make sure you're running from impl/claude and spec files exist")
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
