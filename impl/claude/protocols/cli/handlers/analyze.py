"""
Analysis Handler: Four-mode spec analysis (categorical, epistemic, dialectical, generative).

AGENTESE Path Mapping:
    kg analyze <path>               -> concept.analysis.full.{target}
    kg analyze <path> --mode cat    -> concept.analysis.categorical.{target}
    kg analyze <path> --mode epi    -> concept.analysis.epistemic.{target}
    kg analyze <path> --mode dia    -> concept.analysis.dialectical.{target}
    kg analyze <path> --mode gen    -> concept.analysis.generative.{target}
    kg analyze --self               -> concept.analysis.meta.self

Usage:
    kg analyze <path>                      # Full 4-mode analysis
    kg analyze <path> --mode categorical   # Single mode (cat, epi, dia, gen)
    kg analyze <path> --mode cat,epi       # Multiple modes
    kg analyze <path> --structural         # Use structural (non-LLM) analysis
    kg analyze <path> --json               # JSON output
    kg analyze <path> --rich               # Rich terminal output (default)
    kg analyze --self                      # Self-analysis of Analysis Operad
    kg analyze --help                      # Help message

Philosophy:
    "Analysis is not one thing but four: verification of laws, grounding of claims,
    resolution of tensions, and regeneration from axioms."

    "Analysis that can analyze itself is the only analysis worth having."

See: spec/theory/analysis-operad.md, agents/operad/domains/analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


@handler("analyze", is_async=True, tier=1, timeout=180.0, description="Four-mode spec analysis")
async def cmd_analyze(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Four-Mode Spec Analysis: Categorical, Epistemic, Dialectical, Generative.

    The Analysis Operad provides four lenses for rigorous inquiry:
    - Categorical: Does X satisfy its own composition laws?
    - Epistemic: What layer IS X? How is it justified?
    - Dialectical: What tensions exist? How are they resolved?
    - Generative: Can X be regenerated from its axioms?

    These modes are composable operations in an operad. Full analysis
    applies all four and synthesizes insights.

    Witness Integration:
    - By default, full analysis emits a Witness mark capturing the results
    - Mark includes: target, mode (llm/structural), pass/fail per mode, findings
    - Use --witness to force emission, --no-witness to skip
    - Marks tagged with: analysis, llm/structural, target filename
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Handle self-analysis
    if "--self" in args:
        return await _handle_self_analysis(args)

    # Parse target path
    target = _parse_target(args)
    if target is None:
        print("Error: No target specified")
        print()
        print("Usage: kg analyze <path> [options]")
        print("   or: kg analyze --self")
        print()
        print("Run 'kg analyze --help' for details")
        return 1

    # Parse modes
    modes = _parse_modes(args)
    if modes is None:
        print("Error: Invalid mode specified")
        print()
        print("Valid modes: categorical (cat), epistemic (epi), dialectical (dia), generative (gen), constitutional (const)")
        print()
        return 1

    # Check if target file exists
    target_path = Path(target)
    if not target_path.exists():
        print(f"Error: File not found: {target}")
        print()
        print(f"Searched at: {target_path.absolute()}")
        return 1

    # Determine if using LLM or structural analysis
    # Default is LLM; use --structural to disable
    use_structural = "--structural" in args or "--struct" in args
    use_llm = "--llm" in args or not use_structural  # LLM is default unless --structural
    use_json = "--json" in args
    use_rich = "--rich" in args or not use_json  # Rich is default

    # Determine if we should emit Witness marks
    # Default: emit marks for full analysis, skip for single modes
    emit_witness = "--witness" in args or (modes == "full" and "--no-witness" not in args)

    # Execute analysis
    try:
        from agents.operad.domains.analysis import (
            ANALYSIS_OPERAD,
            CategoricalReport,
            DialecticalReport,
            EpistemicReport,
            GenerativeReport,
            ConstitutionalReport,
            FullAnalysisReport,
        )

        target_str = str(target_path.absolute())

        # Choose between LLM and structural analysis
        if use_llm:
            # Import async LLM-backed functions
            from agents.operad.domains.analysis import (
                analyze_categorical_llm,
                analyze_epistemic_llm,
                analyze_dialectical_llm,
                analyze_generative_llm,
                analyze_constitutional_llm,
                analyze_full_llm,
            )

            # Run requested modes (async)
            if modes == "full":
                print("Running full LLM-backed analysis...")
                report = await analyze_full_llm(target_str)

                # Emit witness marks if requested
                if emit_witness:
                    await _emit_analysis_marks(report, target_str, "llm")

                if use_json:
                    _print_json_full(report)
                else:
                    _print_rich_full(report, target_str)

                return 0 if report.is_valid else 1

            # Run individual or multiple modes
            results = {}

            if "categorical" in modes or "cat" in modes:
                print("Running categorical LLM analysis...")
                results["categorical"] = await analyze_categorical_llm(target_str)

            if "epistemic" in modes or "epi" in modes:
                print("Running epistemic LLM analysis...")
                results["epistemic"] = await analyze_epistemic_llm(target_str)

            if "dialectical" in modes or "dia" in modes:
                print("Running dialectical LLM analysis...")
                results["dialectical"] = await analyze_dialectical_llm(target_str)

            if "generative" in modes or "gen" in modes:
                print("Running generative LLM analysis...")
                results["generative"] = await analyze_generative_llm(target_str)

            if "constitutional" in modes or "const" in modes:
                print("Running constitutional LLM analysis...")
                results["constitutional"] = await analyze_constitutional_llm(target_str)

        else:
            # Structural (non-LLM) analysis
            from agents.operad.domains.analysis import (
                _categorical_analysis,
                _epistemic_analysis,
                _dialectical_analysis,
                _generative_analysis,
                _constitutional_analysis,
                _full_analysis,
            )

            print("Running structural analysis (no LLM)...")

            if modes == "full":
                report = _full_analysis(target_str)

                # Emit witness marks if requested
                if emit_witness:
                    await _emit_analysis_marks(report, target_str, "structural")

                if use_json:
                    _print_json_full(report)
                else:
                    _print_rich_full(report, target_str)

                return 0 if report.is_valid else 1

            # Run individual or multiple modes
            results = {}

            if "categorical" in modes or "cat" in modes:
                results["categorical"] = _categorical_analysis(target_str)

            if "epistemic" in modes or "epi" in modes:
                results["epistemic"] = _epistemic_analysis(target_str)

            if "dialectical" in modes or "dia" in modes:
                results["dialectical"] = _dialectical_analysis(target_str)

            if "generative" in modes or "gen" in modes:
                results["generative"] = _generative_analysis(target_str)

            if "constitutional" in modes or "const" in modes:
                results["constitutional"] = _constitutional_analysis(target_str)

        if use_json:
            _print_json_modes(results)
        else:
            _print_rich_modes(results, target_str)

        # Return 0 if all passed, 1 if any issues
        has_issues = _check_for_issues(results)
        return 1 if has_issues else 0

    except ImportError as e:
        print(f"Error: Analysis Operad not fully implemented: {e}")
        print()
        print("The Analysis Operad is defined at:")
        print("  agents/operad/domains/analysis.py")
        print()
        print("To implement LLM-based analysis, see:")
        print("  plans/analysis-operad-llm.md")
        return 1
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


def _parse_target(args: list[str]) -> str | None:
    """Extract target path from args."""
    for arg in args:
        if not arg.startswith("-") and arg != "analyze":
            return arg
    return None


def _parse_modes(args: list[str]) -> str | list[str] | None:
    """
    Parse --mode argument.

    Returns:
        "full" if no mode specified (default)
        list[str] of mode names if specified
        None if invalid mode
    """
    # Find --mode argument
    mode_arg = None
    for i, arg in enumerate(args):
        if arg == "--mode" and i + 1 < len(args):
            mode_arg = args[i + 1]
            break
        elif arg.startswith("--mode="):
            mode_arg = arg.split("=", 1)[1]
            break

    if mode_arg is None:
        return "full"

    # Parse comma-separated modes
    modes = [m.strip().lower() for m in mode_arg.split(",")]

    # Validate modes
    valid_modes = {"categorical", "cat", "epistemic", "epi", "dialectical", "dia", "generative", "gen", "constitutional", "const"}
    for mode in modes:
        if mode not in valid_modes:
            return None

    return modes


async def _handle_self_analysis(args: list[str]) -> int:
    """Analyze the Analysis Operad itself (meta-application)."""
    try:
        use_structural = "--structural" in args or "--struct" in args
        use_json = "--json" in args

        print("Analyzing the Analysis Operad itself...")
        print("=" * 60)
        print()

        if use_structural:
            from agents.operad.domains.analysis import self_analyze
            print("Mode: Structural (no LLM)")
            report = self_analyze()
        else:
            from agents.operad.domains.analysis import self_analyze_llm
            print("Mode: LLM-backed (Claude)")
            print("This will honestly evaluate the spec, including any issues...")
            print()
            report = await self_analyze_llm()

        if use_json:
            _print_json_full(report)
        else:
            _print_rich_full(report, "spec/theory/analysis-operad.md")

        print()
        if report.is_valid:
            print("Meta-Applicability Law: ✓ PASSED")
            print("The Analysis Operad successfully analyzed itself.")
            print("This validates the meta-applicability law (Lawvere fixed-point).")
        else:
            print("Meta-Applicability Law: ⚠️ ISSUES DETECTED")
            print("The Analysis Operad analyzed itself and found issues.")
            print("This is honest self-analysis — the spec has room for improvement.")
            print()
            print("See synthesis for details.")

        return 0 if report.is_valid else 1

    except ImportError as e:
        print(f"Error: Analysis Operad not fully implemented: {e}")
        print()
        print("To use structural analysis: kg analyze --self --structural")
        return 1
    except Exception as e:
        print(f"Error during self-analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


def _check_for_issues(results: dict) -> bool:
    """Check if any analysis mode detected issues."""
    for mode, report in results.items():
        if mode == "categorical" and report.has_violations:
            return True
        if mode == "epistemic" and not report.is_grounded:
            return True
        if mode == "dialectical" and report.problematic_count > 0:
            return True
        if mode == "generative" and not report.is_regenerable:
            return True
        if mode == "constitutional" and not report.is_aligned:
            return True
    return False


# =============================================================================
# JSON Output
# =============================================================================


def _print_json_full(report) -> None:
    """Print full analysis report as JSON."""
    output = {
        "target": report.target,
        "is_valid": report.is_valid,
        "categorical": {
            "laws_extracted": len(report.categorical.laws_extracted),
            "laws_verified": report.categorical.laws_total,
            "laws_passed": report.categorical.laws_passed,
            "has_violations": report.categorical.has_violations,
            "summary": report.categorical.summary,
        },
        "epistemic": {
            "layer": report.epistemic.layer,
            "is_grounded": report.epistemic.is_grounded,
            "has_valid_bootstrap": report.epistemic.has_valid_bootstrap,
            "summary": report.epistemic.summary,
        },
        "dialectical": {
            "tensions_total": len(report.dialectical.tensions),
            "tensions_resolved": report.dialectical.resolved_count,
            "problematic_count": report.dialectical.problematic_count,
            "paraconsistent_count": report.dialectical.paraconsistent_count,
            "summary": report.dialectical.summary,
        },
        "generative": {
            "compression_ratio": report.generative.compression_ratio,
            "is_compressed": report.generative.is_compressed,
            "is_regenerable": report.generative.is_regenerable,
            "minimal_kernel_size": len(report.generative.minimal_kernel),
            "summary": report.generative.summary,
        },
        "synthesis": report.synthesis,
    }
    print(json.dumps(output, indent=2))


def _print_json_modes(results: dict) -> None:
    """Print individual mode results as JSON."""
    output = {}

    for mode, report in results.items():
        if mode == "categorical":
            output[mode] = {
                "laws_extracted": len(report.laws_extracted),
                "laws_verified": report.laws_total,
                "laws_passed": report.laws_passed,
                "has_violations": report.has_violations,
                "summary": report.summary,
            }
        elif mode == "epistemic":
            output[mode] = {
                "layer": report.layer,
                "is_grounded": report.is_grounded,
                "has_valid_bootstrap": report.has_valid_bootstrap,
                "summary": report.summary,
            }
        elif mode == "dialectical":
            output[mode] = {
                "tensions_total": len(report.tensions),
                "tensions_resolved": report.resolved_count,
                "problematic_count": report.problematic_count,
                "paraconsistent_count": report.paraconsistent_count,
                "summary": report.summary,
            }
        elif mode == "generative":
            output[mode] = {
                "compression_ratio": report.compression_ratio,
                "is_compressed": report.is_compressed,
                "is_regenerable": report.is_regenerable,
                "minimal_kernel_size": len(report.minimal_kernel),
                "summary": report.summary,
            }
        elif mode == "constitutional":
            output[mode] = {
                "is_aligned": report.is_aligned,
                "alignment_score": report.alignment_score,
                "violation_count": report.violation_count,
                "violations": list(report.violations),
                "principle_scores": report.alignment.principle_scores,
                "summary": report.summary,
            }

    print(json.dumps(output, indent=2))


# =============================================================================
# Rich Terminal Output
# =============================================================================


def _print_rich_full(report, target: str) -> None:
    """Print full analysis report with rich terminal formatting."""
    print()
    print("=" * 60)
    print(f"FULL ANALYSIS: {Path(target).name}")
    print("=" * 60)
    print()

    # Categorical
    print("┌─ CATEGORICAL ANALYSIS")
    print("│")
    cat = report.categorical
    status = "✓ PASS" if not cat.has_violations else "✗ FAIL"
    print(f"│  Status: {status}")
    print(f"│  Laws: {cat.laws_passed}/{cat.laws_total} verified")
    if cat.fixed_point and cat.fixed_point.is_self_referential:
        fp_status = "✓ valid" if cat.fixed_point.is_valid else "✗ invalid"
        print(f"│  Fixed Point: {fp_status} — {cat.fixed_point.fixed_point_description}")
    print(f"│  Summary: {cat.summary}")
    print("│")

    # Epistemic
    print("├─ EPISTEMIC ANALYSIS")
    print("│")
    epi = report.epistemic
    status = "✓ PASS" if epi.is_grounded else "✗ FAIL"
    print(f"│  Status: {status}")
    print(f"│  Layer: L{epi.layer}")
    print(f"│  Grounded: {'Yes' if epi.is_grounded else 'No'}")
    if epi.bootstrap:
        boot_status = "✓ valid" if epi.bootstrap.is_valid else "✗ invalid"
        print(f"│  Bootstrap: {boot_status}")
    print(f"│  Summary: {epi.summary}")
    print("│")

    # Dialectical
    print("├─ DIALECTICAL ANALYSIS")
    print("│")
    dia = report.dialectical
    status = "✓ PASS" if dia.problematic_count == 0 else "✗ FAIL"
    print(f"│  Status: {status}")
    print(f"│  Tensions: {len(dia.tensions)} total, {dia.resolved_count} resolved")
    print(f"│  Problematic: {dia.problematic_count}")
    print(f"│  Paraconsistent: {dia.paraconsistent_count}")
    print(f"│  Summary: {dia.summary}")
    print("│")

    # Generative
    print("└─ GENERATIVE ANALYSIS")
    print()
    gen = report.generative
    status = "✓ PASS" if gen.is_regenerable else "✗ FAIL"
    print(f"   Status: {status}")
    print(f"   Compression: {gen.compression_ratio:.2f} ({'compressed' if gen.is_compressed else 'not compressed'})")
    print(f"   Regenerable: {'Yes' if gen.is_regenerable else 'No'}")
    print(f"   Minimal Kernel: {len(gen.minimal_kernel)} axioms")
    print(f"   Summary: {gen.summary}")
    print()

    # Synthesis
    print("─" * 60)
    print("SYNTHESIS")
    print("─" * 60)
    print()
    overall = "✓ VALID" if report.is_valid else "✗ ISSUES DETECTED"
    print(f"Overall: {overall}")
    print()
    print(report.synthesis)
    print()
    print("=" * 60)


def _print_rich_modes(results: dict, target: str) -> None:
    """Print individual mode results with rich terminal formatting."""
    print()
    print("=" * 60)
    print(f"ANALYSIS: {Path(target).name}")
    print("=" * 60)
    print()

    for mode, report in results.items():
        if mode == "categorical":
            print("CATEGORICAL ANALYSIS")
            print("─" * 60)
            status = "✓ PASS" if not report.has_violations else "✗ FAIL"
            print(f"Status: {status}")
            print(f"Laws: {report.laws_passed}/{report.laws_total} verified")
            print()
            for law in report.law_verifications:
                symbol = "✓" if law.passed else "✗"
                print(f"  {symbol} {law.law_name}: {law.message}")
            print()
            if report.fixed_point and report.fixed_point.is_self_referential:
                print("Fixed Point Analysis:")
                fp_status = "✓ valid" if report.fixed_point.is_valid else "✗ invalid"
                print(f"  {fp_status}: {report.fixed_point.fixed_point_description}")
                for impl in report.fixed_point.implications:
                    print(f"    → {impl}")
                print()
            print(f"Summary: {report.summary}")
            print()

        elif mode == "epistemic":
            print("EPISTEMIC ANALYSIS")
            print("─" * 60)
            status = "✓ PASS" if report.is_grounded else "✗ FAIL"
            print(f"Status: {status}")
            print(f"Layer: L{report.layer}")
            print()
            print("Toulmin Structure:")
            print(f"  Claim: {report.toulmin.claim}")
            print(f"  Grounds: {', '.join(report.toulmin.grounds)}")
            print(f"  Warrant: {report.toulmin.warrant}")
            print(f"  Backing: {report.toulmin.backing}")
            print(f"  Qualifier: {report.toulmin.qualifier}")
            print()
            print("Grounding Chain:")
            grounded = "✓ terminates at axiom" if report.grounding.terminates_at_axiom else "✗ not grounded"
            print(f"  {grounded}")
            for layer, node, edge in report.grounding.steps:
                print(f"    L{layer}: {node} ({edge})")
            print()
            if report.bootstrap:
                boot_status = "✓ valid" if report.bootstrap.is_valid else "✗ invalid"
                print(f"Bootstrap: {boot_status}")
                print(f"  {report.bootstrap.explanation}")
                print()
            print(f"Summary: {report.summary}")
            print()

        elif mode == "dialectical":
            print("DIALECTICAL ANALYSIS")
            print("─" * 60)
            status = "✓ PASS" if report.problematic_count == 0 else "✗ FAIL"
            print(f"Status: {status}")
            print(f"Tensions: {len(report.tensions)} total, {report.resolved_count} resolved")
            print()
            for i, tension in enumerate(report.tensions, 1):
                status_icon = "✓" if tension.is_resolved else "✗"
                print(f"{i}. {status_icon} {tension.classification.name}")
                print(f"   Thesis: {tension.thesis}")
                print(f"   Antithesis: {tension.antithesis}")
                if tension.synthesis:
                    print(f"   Synthesis: {tension.synthesis}")
                print()
            print(f"Summary: {report.summary}")
            print()

        elif mode == "generative":
            print("GENERATIVE ANALYSIS")
            print("─" * 60)
            status = "✓ PASS" if report.is_regenerable else "✗ FAIL"
            print(f"Status: {status}")
            print(f"Compression: {report.compression_ratio:.2f}")
            print()
            print("Grammar:")
            print(f"  Primitives: {len(report.grammar.primitives)}")
            print(f"  Operations: {len(report.grammar.operations)}")
            print(f"  Laws: {len(report.grammar.laws)}")
            print()
            print("Regeneration Test:")
            regen_status = "✓ PASSED" if report.regeneration.passed else "✗ FAILED"
            print(f"  {regen_status}")
            print(f"  Axioms used: {len(report.regeneration.axioms_used)}")
            for axiom in report.regeneration.axioms_used:
                print(f"    - {axiom}")
            if report.regeneration.missing_elements:
                print(f"  Missing: {', '.join(report.regeneration.missing_elements)}")
            print()
            print(f"Minimal Kernel: {len(report.minimal_kernel)} axioms")
            for axiom in report.minimal_kernel:
                print(f"  - {axiom}")
            print()
            print(f"Summary: {report.summary}")
            print()

        elif mode == "constitutional":
            print("CONSTITUTIONAL ANALYSIS")
            print("─" * 60)
            status = "✓ PASS" if report.is_aligned else "✗ FAIL"
            print(f"Status: {status}")
            print(f"Alignment Score: {report.alignment_score:.2f}")
            print()
            print("Principle Scores:")
            for principle, score in sorted(report.alignment.principle_scores.items()):
                symbol = "✓" if score >= report.alignment.threshold else "✗"
                print(f"  {symbol} {principle}: {score:.2f}")
            print()
            if report.violations:
                print(f"Violations ({len(report.violations)}):")
                for violation in report.violations:
                    print(f"  ✗ {violation}")
                print()
            if report.remediation_suggestions:
                print("Remediation Suggestions:")
                for suggestion in report.remediation_suggestions:
                    print(f"  → {suggestion}")
                print()
            print(f"Summary: {report.summary}")
            print()

    print("=" * 60)


# =============================================================================
# Help Text
# =============================================================================


async def _emit_analysis_marks(report: "FullAnalysisReport", target: str, mode: str) -> None:
    """
    Emit Witness marks for completed analysis.

    Emits a summary mark with:
    - Target file analyzed
    - Mode (llm/structural)
    - Pass/fail status for each mode
    - Overall validity

    Args:
        report: Full analysis report
        target: Target file path
        mode: "llm" or "structural"
    """
    try:
        from pathlib import Path
        from protocols.cli.handlers.witness.marks import _create_mark_async

        # Extract target filename for brevity
        target_name = Path(target).name

        # Build summary
        cat_status = "✓" if not report.categorical.has_violations else "✗"
        epi_status = "✓" if report.epistemic.is_grounded else "✗"
        dia_status = "✓" if report.dialectical.problematic_count == 0 else "✗"
        gen_status = "✓" if report.generative.is_regenerable else "✗"

        action = f"Analyzed {target_name} ({mode}): cat{cat_status} epi{epi_status} dia{dia_status} gen{gen_status}"

        # Build reasoning with key findings
        findings = []
        if report.categorical.has_violations:
            findings.append(f"categorical: {report.categorical.laws_passed}/{report.categorical.laws_total} laws")
        if not report.epistemic.is_grounded:
            findings.append(f"epistemic: L{report.epistemic.layer} not grounded")
        if report.dialectical.problematic_count > 0:
            findings.append(f"dialectical: {report.dialectical.problematic_count} problematic")
        if not report.generative.is_regenerable:
            findings.append(f"generative: not regenerable")

        reasoning = "; ".join(findings) if findings else "All modes passed"

        # Determine principles based on analysis results
        principles = []
        if report.is_valid:
            principles.append("generative")  # Spec is regenerable
        if report.categorical.laws_passed == report.categorical.laws_total:
            principles.append("composable")  # Laws compose correctly
        if report.epistemic.is_grounded:
            principles.append("ethical")  # Transparent grounding

        # Tags for retrieval
        tags = ["analysis", mode, target_name.replace(".", "_")]

        # Emit the mark
        await _create_mark_async(
            action=action,
            reasoning=reasoning,
            principles=principles,
            tags=tags,
            author="analysis_operad",
        )

        print(f"  [Witness mark emitted]")

    except Exception as e:
        # Don't fail the analysis if mark emission fails
        print(f"  [Warning: Could not emit witness mark: {e}]")


def _print_help() -> None:
    """Print comprehensive help text."""
    help_text = """
kg analyze - Four-mode spec analysis

Description:
  The Analysis Operad provides four lenses for rigorous inquiry into
  specifications and implementations. Each mode illuminates what others
  cannot see:

  • Categorical: Does X satisfy its own composition laws?
  • Epistemic: What layer IS X? How is it justified?
  • Dialectical: What tensions exist? How are they resolved?
  • Generative: Can X be regenerated from its axioms?

Commands:
  kg analyze <path>                Full analysis (all four modes)
  kg analyze <path> --mode <mode>  Specific mode(s)
  kg analyze --self                Analyze the Analysis Operad itself

Modes:
  categorical, cat       Verify composition laws via Lawvere fixed-point
  epistemic, epi         Analyze justification structure and grounding
  dialectical, dia       Identify tensions and synthesize resolutions
  generative, gen        Test regenerability from axioms
  constitutional, const  Verify alignment with 7 kgents principles

Options:
  --mode <modes>      Comma-separated list of modes (default: full)
                      Examples: --mode cat, --mode cat,epi,dia
  --structural        Use structural analysis (no LLM)
  --json              Output as JSON (for pipelines)
  --rich              Rich terminal output (default)
  --witness           Emit Witness marks after analysis (default for full mode)
  --no-witness        Skip Witness mark emission
  --self              Analyze the Analysis Operad itself
  --help, -h          Show this help message

Examples:
  # Full analysis of a spec
  kg analyze spec/theory/analysis-operad.md

  # Categorical analysis only
  kg analyze spec/protocols/zero-seed.md --mode categorical

  # Multiple modes
  kg analyze spec/agents/operad.md --mode cat,epi

  # JSON output for pipelines
  kg analyze spec/theory/dp-native-kgents.md --json

  # Self-analysis (meta-applicability)
  kg analyze --self

  # Full analysis with Witness marks (default)
  kg analyze spec/protocols/witness.md
  kg witness show --today --grep "witness.md"

  # Skip Witness marks
  kg analyze spec/protocols/witness.md --no-witness

Output Interpretation:
  Categorical:
    ✓ PASS    All laws verified, no violations
    ✗ FAIL    Law violations detected

  Epistemic:
    ✓ PASS    Grounded at L1-L2 axioms, valid bootstrap
    ✗ FAIL    Floating (not grounded) or invalid bootstrap

  Dialectical:
    ✓ PASS    No problematic contradictions
    ✗ FAIL    Unresolved problematic tensions

  Generative:
    ✓ PASS    Regenerable from axioms, compressed
    ✗ FAIL    Cannot regenerate or not compressed

Philosophy:
  "Analysis is not one thing but four: verification of laws,
   grounding of claims, resolution of tensions, and regeneration
   from axioms."

  "Analysis that can analyze itself is the only analysis worth having."

  The four modes are composable operations in an operad. Full analysis
  runs: seq(par(categorical, epistemic), par(dialectical, generative))

AGENTESE Paths:
  concept.analysis.categorical.{target}    Categorical analysis
  concept.analysis.epistemic.{target}      Epistemic analysis
  concept.analysis.dialectical.{target}    Dialectical analysis
  concept.analysis.generative.{target}     Generative analysis
  concept.analysis.full.{target}           Full four-mode analysis
  concept.analysis.meta.self               Self-analysis

Integration:
  Use with kg audit for spec hygiene:
    kg analyze <spec> --mode cat          # Verify laws
    kg audit <spec>                       # Check against principles
    kg annotate <spec> --link <impl>      # Link spec to impl

See: spec/theory/analysis-operad.md, agents/operad/domains/analysis.py
"""
    print(help_text.strip())


__all__ = ["cmd_analyze"]
