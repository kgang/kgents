#!/usr/bin/env python3
"""
Phase 2.5d: Evolution Pipeline Testing & Metrics Collection

Tests the full evolution pipeline with new reliability layer and collects metrics:
- Syntax error rate (target: <10%)
- Parse success rate (target: >95%)
- Incorporation rate (target: >90%)
- Retry success rate
- Fallback usage

Usage:
    python test_evolution_metrics.py [--module MODULE] [--quick]
"""

import asyncio
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from agents.e import (
    CodeModule,
    EvolutionPipeline,
    EvolutionConfig,
    EvolutionMetrics,
    ErrorMemory,
)
from meta.evolve import discover_modules


@dataclass
class MetricsReport:
    """Comprehensive metrics report for evolution pipeline."""

    # Generation quality
    total_hypotheses: int = 0
    syntax_errors: int = 0
    parse_failures: int = 0

    # Validation
    validation_failures: int = 0
    type_errors: int = 0

    # Testing
    test_failures: int = 0

    # Incorporation
    incorporations: int = 0

    # Recovery
    retries_attempted: int = 0
    retries_succeeded: int = 0
    fallbacks_used: int = 0

    # Timing
    total_time_seconds: float = 0.0
    avg_time_per_hypothesis: float = 0.0

    # Details
    failed_modules: list[str] = field(default_factory=list)
    success_modules: list[str] = field(default_factory=list)

    @property
    def syntax_error_rate(self) -> float:
        """Syntax error rate (target: <10%)."""
        if self.total_hypotheses == 0:
            return 0.0
        return self.syntax_errors / self.total_hypotheses

    @property
    def parse_success_rate(self) -> float:
        """Parse success rate (target: >95%)."""
        if self.total_hypotheses == 0:
            return 0.0
        return (self.total_hypotheses - self.parse_failures) / self.total_hypotheses

    @property
    def incorporation_rate(self) -> float:
        """Incorporation rate (target: >90%)."""
        if self.total_hypotheses == 0:
            return 0.0
        return self.incorporations / self.total_hypotheses

    @property
    def retry_success_rate(self) -> float:
        """Retry success rate."""
        if self.retries_attempted == 0:
            return 0.0
        return self.retries_succeeded / self.retries_attempted

    def format_report(self) -> str:
        """Format report with target comparisons."""
        target_met = "✅" if self.syntax_error_rate < 0.10 else "❌"
        parse_met = "✅" if self.parse_success_rate > 0.95 else "❌"
        incorp_met = "✅" if self.incorporation_rate > 0.90 else "❌"

        return f"""
╔══════════════════════════════════════════════════════════╗
║          EVOLUTION PIPELINE METRICS REPORT               ║
╚══════════════════════════════════════════════════════════╝

📊 GENERATION QUALITY
────────────────────────────────────────────────────────────
  Total hypotheses:      {self.total_hypotheses}
  Syntax errors:         {self.syntax_errors} ({self.syntax_error_rate:.1%}) {target_met} Target: <10%
  Parse failures:        {self.parse_failures} ({(self.parse_failures/max(1,self.total_hypotheses)):.1%})
  Parse success rate:    {self.parse_success_rate:.1%} {parse_met} Target: >95%

✅ VALIDATION
────────────────────────────────────────────────────────────
  Validation failures:   {self.validation_failures}
  Type errors:           {self.type_errors}

🧪 TESTING
────────────────────────────────────────────────────────────
  Test failures:         {self.test_failures}

📦 INCORPORATION
────────────────────────────────────────────────────────────
  Incorporations:        {self.incorporations} ({self.incorporation_rate:.1%}) {incorp_met} Target: >90%

🔄 RECOVERY
────────────────────────────────────────────────────────────
  Retries attempted:     {self.retries_attempted}
  Retries succeeded:     {self.retries_succeeded} ({self.retry_success_rate:.1%})
  Fallbacks used:        {self.fallbacks_used}

⏱️  PERFORMANCE
────────────────────────────────────────────────────────────
  Total time:            {self.total_time_seconds:.1f}s
  Avg per hypothesis:    {self.avg_time_per_hypothesis:.1f}s

📈 SUMMARY
────────────────────────────────────────────────────────────
  Success modules:       {len(self.success_modules)}
  Failed modules:        {len(self.failed_modules)}

{self._format_recommendations()}
"""

    def _format_recommendations(self) -> str:
        """Generate recommendations based on metrics."""
        recommendations = []

        if self.syntax_error_rate >= 0.10:
            recommendations.append(
                "⚠️  SYNTAX ERROR RATE TOO HIGH\n"
                f"   Current: {self.syntax_error_rate:.1%}, Target: <10%\n"
                "   → Review prompts.py: add more syntax constraints\n"
                "   → Check parser.py: improve extraction robustness"
            )

        if self.parse_success_rate <= 0.95:
            recommendations.append(
                "⚠️  PARSE SUCCESS RATE TOO LOW\n"
                f"   Current: {self.parse_success_rate:.1%}, Target: >95%\n"
                "   → Review parser.py: add more fallback strategies\n"
                "   → Consider enabling LLM repair fallback"
            )

        if self.incorporation_rate <= 0.90:
            recommendations.append(
                "⚠️  INCORPORATION RATE TOO LOW\n"
                f"   Current: {self.incorporation_rate:.1%}, Target: >90%\n"
                "   → Review validator.py: are checks too strict?\n"
                "   → Review retry.py: increase max_retries?\n"
                "   → Enable fallback strategies"
            )

        if not recommendations:
            recommendations.append("✅ ALL TARGETS MET! Pipeline performing well.")

        return "\n".join(recommendations)

    def save_json(self, path: Path):
        """Save metrics as JSON for analysis."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_hypotheses": self.total_hypotheses,
                "syntax_errors": self.syntax_errors,
                "syntax_error_rate": self.syntax_error_rate,
                "parse_failures": self.parse_failures,
                "parse_success_rate": self.parse_success_rate,
                "validation_failures": self.validation_failures,
                "type_errors": self.type_errors,
                "test_failures": self.test_failures,
                "incorporations": self.incorporations,
                "incorporation_rate": self.incorporation_rate,
                "retries_attempted": self.retries_attempted,
                "retries_succeeded": self.retries_succeeded,
                "retry_success_rate": self.retry_success_rate,
                "fallbacks_used": self.fallbacks_used,
                "total_time_seconds": self.total_time_seconds,
                "avg_time_per_hypothesis": self.avg_time_per_hypothesis,
            },
            "modules": {
                "success": self.success_modules,
                "failed": self.failed_modules,
            }
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
        print(f"\n📊 Metrics saved to: {path}")


async def test_single_module(
    module: CodeModule,
    config: EvolutionConfig
) -> MetricsReport:
    """Test evolution pipeline on a single module."""
    print(f"\n{'='*60}")
    print(f"Testing module: {module.category}/{module.name}")
    print(f"{'='*60}")

    report = MetricsReport()
    start_time = datetime.now()

    try:
        # Run evolution pipeline
        pipeline = EvolutionPipeline(config)
        result = await pipeline.evolve_module(module)

        # Collect metrics from result
        report.total_hypotheses = len(result.experiments)

        for exp in result.experiments:
            # Check for syntax errors
            if hasattr(exp, 'syntax_error') and exp.syntax_error:
                report.syntax_errors += 1

            # Check for parse failures
            if hasattr(exp, 'parse_failed') and exp.parse_failed:
                report.parse_failures += 1

            # Check for validation failures
            if hasattr(exp, 'validation_failed') and exp.validation_failed:
                report.validation_failures += 1

            # Check for type errors
            if hasattr(exp, 'type_errors') and exp.type_errors:
                report.type_errors += len(exp.type_errors)

            # Check for test failures
            if hasattr(exp, 'test_failed') and exp.test_failed:
                report.test_failures += 1

        # Count incorporations
        report.incorporations = len(result.incorporated)

        # Recovery metrics
        if hasattr(result, 'retries_attempted'):
            report.retries_attempted = result.retries_attempted
            report.retries_succeeded = result.retries_succeeded
        if hasattr(result, 'fallbacks_used'):
            report.fallbacks_used = result.fallbacks_used

        # Timing
        end_time = datetime.now()
        report.total_time_seconds = (end_time - start_time).total_seconds()
        if report.total_hypotheses > 0:
            report.avg_time_per_hypothesis = (
                report.total_time_seconds / report.total_hypotheses
            )

        # Module status
        if report.incorporations > 0:
            report.success_modules.append(f"{module.category}/{module.name}")
        else:
            report.failed_modules.append(f"{module.category}/{module.name}")

        print(f"\n✅ Module test complete:")
        print(f"   Hypotheses: {report.total_hypotheses}")
        print(f"   Incorporated: {report.incorporations}")
        print(f"   Time: {report.total_time_seconds:.1f}s")

    except Exception as e:
        print(f"\n❌ Module test failed: {e}")
        report.failed_modules.append(f"{module.category}/{module.name}")

    return report


async def test_all_modules(
    modules: list[CodeModule],
    config: EvolutionConfig
) -> MetricsReport:
    """Test evolution pipeline on all modules."""
    print(f"\n🧪 TESTING {len(modules)} MODULES")
    print(f"{'='*60}")

    total_report = MetricsReport()

    for module in modules:
        module_report = await test_single_module(module, config)

        # Aggregate metrics
        total_report.total_hypotheses += module_report.total_hypotheses
        total_report.syntax_errors += module_report.syntax_errors
        total_report.parse_failures += module_report.parse_failures
        total_report.validation_failures += module_report.validation_failures
        total_report.type_errors += module_report.type_errors
        total_report.test_failures += module_report.test_failures
        total_report.incorporations += module_report.incorporations
        total_report.retries_attempted += module_report.retries_attempted
        total_report.retries_succeeded += module_report.retries_succeeded
        total_report.fallbacks_used += module_report.fallbacks_used
        total_report.total_time_seconds += module_report.total_time_seconds
        total_report.success_modules.extend(module_report.success_modules)
        total_report.failed_modules.extend(module_report.failed_modules)

    # Calculate average time per hypothesis
    if total_report.total_hypotheses > 0:
        total_report.avg_time_per_hypothesis = (
            total_report.total_time_seconds / total_report.total_hypotheses
        )

    return total_report


async def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test evolution pipeline and collect metrics"
    )
    parser.add_argument(
        "--module",
        help="Test specific module (e.g., 'meta/evolve')",
        default=None
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: fewer hypotheses per module"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file for metrics",
        default=".evolve_logs/metrics_report.json"
    )

    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════════╗")
    print("║     PHASE 2.5d: EVOLUTION PIPELINE METRICS TEST          ║")
    print("╚══════════════════════════════════════════════════════════╝")

    # Configure evolution pipeline with reliability features enabled
    config = EvolutionConfig(
        target=args.module or "all",
        dry_run=True,  # Don't actually apply changes
        auto_apply=False,
        quick_mode=args.quick,
        # Enable all reliability features
        enable_retry=True,
        enable_fallback=True,
        enable_error_memory=True,
        enable_schema_validation=True,
        enable_repair=True,
        max_hypotheses=3 if args.quick else 5,
    )

    # Discover modules to test
    if args.module:
        # Test specific module
        category, name = args.module.split("/")
        modules = [
            CodeModule(
                name=name,
                category=category,
                path=Path(f"agents/{category}/{name}.py")
            )
        ]
    else:
        # Test all modules
        modules = discover_modules()
        if args.quick:
            # In quick mode, just test a few representative modules
            modules = modules[:5]

    print(f"\n📋 Configuration:")
    print(f"   Modules to test: {len(modules)}")
    print(f"   Quick mode: {args.quick}")
    print(f"   Max hypotheses per module: {config.max_hypotheses}")
    print(f"   Retry enabled: {config.enable_retry}")
    print(f"   Fallback enabled: {config.enable_fallback}")
    print(f"   Error memory enabled: {config.enable_error_memory}")

    # Run tests
    report = await test_all_modules(modules, config)

    # Display report
    print(report.format_report())

    # Save JSON
    output_path = Path(args.output)
    report.save_json(output_path)

    # Exit with error code if targets not met
    targets_met = (
        report.syntax_error_rate < 0.10
        and report.parse_success_rate > 0.95
        and report.incorporation_rate > 0.90
    )

    if targets_met:
        print("\n✅ ALL TARGETS MET!")
        sys.exit(0)
    else:
        print("\n❌ TARGETS NOT MET - see recommendations above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
