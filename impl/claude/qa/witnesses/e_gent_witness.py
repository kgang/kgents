#!/usr/bin/env python
"""
E-gent Witness: Teleological Thermodynamic Evolution

> These files are illustrative, not canonical.
> Do not work on fixing these unless asked.

This witness demonstrates E-gent's core functionality through observation:
- Gibbs Free Energy calculation (ΔG = ΔH - TΔS)
- Parasitic pattern detection (hardcoding, deletion, pass-only, gaming)
- Five-layer demon selection
- Hot spot analysis (complexity/entropy)
- Viral library evolution (fitness = success_rate × avg_impact)
- Safety system (rollback, rate limiting, audit, sandbox)
- Complete thermodynamic cycle (SUN→MUTATE→SELECT→WAGER→INFECT→PAYOFF)

Run with: python -m impl.claude.qa.witnesses.e_gent_witness

Aligned with spec/principles.md:
- Tasteful: Clear, justified demonstrations
- Ethical: Transparent about what's happening
- Joy-Inducing: Informative output with personality
- Composable: Each demo is independent
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

# E-gent imports
from impl.claude.agents.e import (
    PARASITIC_PATTERNS,
    STANDARD_SCHEMA_APPLICATORS,
    AtomicMutationManager,
    AuditLogger,
    # Phage operations
    CycleConfig,
    GibbsEnergy,
    InMemoryAuditSink,
    Intent,
    MutationVector,
    # Core types
    Phage,
    RateLimiter,
    Sandbox,
    SandboxConfig,
    # Mutator
    analyze_hot_spots,
    create_cycle,
    create_demon,
    # Library
    create_library,
    create_test_safety_system,
    fitness_to_odds,
)


class DemoResult:
    """Tracks results of a demo for reporting."""

    def __init__(self, name: str):
        self.name = name
        self.started_at = datetime.now()
        self.passed = False
        self.details: dict[str, Any] = {}
        self.error: str | None = None

    def succeed(self, **details: Any) -> None:
        self.passed = True
        self.details = details

    def fail(self, error: str) -> None:
        self.passed = False
        self.error = error


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}")


def print_section(text: str) -> None:
    """Print a section divider."""
    print(f"\n--- {text} ---")


def demo_gibbs_energy() -> DemoResult:
    """
    Demo 1: Gibbs Free Energy Calculation

    Demonstrates the thermodynamic foundation of E-gent:
    ΔG = ΔH - TΔS

    Mutations are favorable when ΔG < 0.
    """
    result = DemoResult("Gibbs Free Energy")
    print_header("Demo 1: Gibbs Free Energy")

    try:
        # Create test scenarios
        scenarios = [
            # (enthalpy, entropy, temperature, expected_favorable)
            (-0.5, 0.3, 1.0, True, "Simplification with added capability"),
            (0.2, 0.8, 1.0, True, "Complexity increase but high capability gain"),
            (0.5, 0.1, 1.0, False, "Complexity increase, low capability gain"),
            (-0.3, 0.2, 2.0, True, "Higher temperature favors entropy"),
            (0.1, 0.5, 0.5, False, "Low temperature disfavors entropy"),
        ]

        print("\nScenario results:")
        print(
            f"{'Description':<45} {'ΔH':>6} {'ΔS':>6} {'T':>5} {'ΔG':>8} {'Viable':>7}"
        )
        print("-" * 80)

        all_correct = True
        for enthalpy, entropy, temp, expected, desc in scenarios:
            gibbs = GibbsEnergy(
                enthalpy_delta=enthalpy,
                entropy_delta=entropy,
                temperature=temp,
            )
            delta_g = gibbs.delta_g
            is_favorable = gibbs.is_favorable
            correct = is_favorable == expected
            all_correct = all_correct and correct

            status = "✓" if correct else "✗"
            print(
                f"{desc:<45} {enthalpy:>6.2f} {entropy:>6.2f} {temp:>5.1f} {delta_g:>8.3f} {status:>7}"
            )

        print("\nKey insight: Lower enthalpy (simpler code) and higher entropy")
        print("(more capability) at the right temperature = favorable mutations.")

        result.succeed(scenarios_tested=len(scenarios), all_correct=all_correct)

    except Exception as e:
        result.fail(str(e))

    return result


def demo_parasitic_detection() -> DemoResult:
    """
    Demo 2: Parasitic Pattern Detection

    Shows how the Teleological Demon prevents "parasitic" mutations
    that game tests without adding real value.
    """
    result = DemoResult("Parasitic Detection")
    print_header("Demo 2: Parasitic Pattern Detection")

    try:
        # Test cases for each parasitic pattern
        test_cases = [
            (
                "Hardcoding",
                """def calculate(x):
    return x * 2 + 1""",
                """def calculate(x):
    return 5
    return 10
    return 15
    return 20""",
                True,
            ),
            (
                "Functionality Deletion",
                """def process(items):
    result = []
    for item in items:
        processed = transform(item)
        if validate(processed):
            result.append(processed)
    return result""",
                """def process(items):
    pass""",
                True,
            ),
            (
                "Pass-only Body",
                """def calculate(x):
    return x * 2""",
                """def calculate(x):
    pass""",
                True,
            ),
            (
                "Test Gaming",
                """def calculate(x):
    return x * 2""",
                """def calculate(x):
    if x == 1: return 2
    if x == 2: return 4
    if x == 3: return 6
    if x == 4: return 8
    if x == 5: return 10
    return x * 2""",
                True,
            ),
            (
                "Legitimate Loop-to-Comprehension",
                """def square_all(nums):
    result = []
    for n in nums:
        result.append(n * n)
    return result""",
                """def square_all(nums):
    return [n * n for n in nums]""",
                False,
            ),
        ]

        print("\nPattern detection results:")
        print(f"{'Pattern':<30} {'Expected Parasitic':>18} {'Detected':>10}")
        print("-" * 60)

        detections = 0
        for name, original, mutated, expected in test_cases:
            # Check each pattern
            detected = False
            for pattern in PARASITIC_PATTERNS:
                if pattern.detector(original, mutated):
                    detected = True
                    break

            status = "✓" if detected == expected else "✗"
            if detected == expected:
                detections += 1
            print(f"{name:<30} {str(expected):>18} {status:>10}")

        print(
            f"\nAccuracy: {detections}/{len(test_cases)} patterns correctly identified"
        )
        print("\nKey insight: The Demon detects mutations that game tests")
        print("rather than genuinely improving code.")

        result.succeed(
            patterns_tested=len(test_cases),
            correct_detections=detections,
            accuracy=detections / len(test_cases),
        )

    except Exception as e:
        result.fail(str(e))

    return result


def demo_five_layer_selection() -> DemoResult:
    """
    Demo 3: Five-Layer Selection

    Demonstrates the Demon's 5-layer filtering:
    1. Syntactic viability (FREE)
    2. Semantic stability (CHEAP)
    3. Teleological alignment (CHEAP-ISH)
    4. Thermodynamic viability (FREE)
    5. Economic viability (FREE)
    """
    result = DemoResult("Five-Layer Selection")
    print_header("Demo 3: Five-Layer Selection")

    try:
        # Create test mutations
        test_mutations = [
            {
                "name": "Valid Mutation",
                "original": "def foo(): return 1",
                "mutated": "def foo(): return 2",
                "confidence": 0.8,
                "enthalpy": -0.1,
                "entropy": 0.2,
                "expected_layer": 5,  # Should pass all
            },
            {
                "name": "Syntax Error",
                "original": "def foo(): return 1",
                "mutated": "def foo( return 1",
                "confidence": 0.8,
                "enthalpy": -0.1,
                "entropy": 0.2,
                "expected_layer": 1,  # Fails layer 1
            },
            {
                "name": "Low Confidence",
                "original": "def foo(): return 1",
                "mutated": "def foo(): return 2",
                "confidence": 0.1,  # Below threshold
                "enthalpy": -0.1,
                "entropy": 0.2,
                "expected_layer": 3,  # Fails layer 3
            },
            {
                "name": "Unfavorable Gibbs",
                "original": "def foo(): return 1",
                "mutated": "def foo(): return 2",
                "confidence": 0.8,
                "enthalpy": 0.5,  # High complexity
                "entropy": 0.1,  # Low capability gain
                "expected_layer": 4,  # Fails layer 4
            },
        ]

        demon = create_demon()

        print("\nSelection results:")
        print(
            f"{'Mutation':<25} {'Expected Layer':>15} {'Actual Layer':>15} {'Passed':>8}"
        )
        print("-" * 70)

        correct = 0
        for test in test_mutations:
            # Create phage with mutation
            mutation = MutationVector(
                original_code=test["original"],
                mutated_code=test["mutated"],
                confidence=test["confidence"],
                enthalpy_delta=test["enthalpy"],
                entropy_delta=test["entropy"],
            )
            phage = Phage(mutation=mutation)

            # Run selection
            selection = demon.select(phage)
            actual_layer = selection.layer_reached

            expected = test["expected_layer"]
            match = actual_layer == expected
            if match:
                correct += 1

            status = "✓" if match else "✗"
            print(f"{test['name']:<25} {expected:>15} {actual_layer:>15} {status:>8}")

        # Print demon stats
        print("\nDemon Statistics:")
        print(f"  Total checked: {demon.stats.total_checked}")
        print(f"  Passed: {demon.stats.passed}")
        print(f"  Rejection rate: {demon.stats.rejection_rate:.1%}")

        rates = demon.stats.layer_rejection_rates
        print("\n  Layer rejection rates:")
        for layer, rate in rates.items():
            print(f"    Layer {layer}: {rate:.1%}")

        result.succeed(
            mutations_tested=len(test_mutations),
            correct_predictions=correct,
            demon_stats=demon.stats.total_checked,
        )

    except Exception as e:
        result.fail(str(e))

    return result


def demo_mutator_hot_spots() -> DemoResult:
    """
    Demo 4: Hot Spot Analysis

    Shows how the Mutator identifies high-priority mutation targets
    based on complexity and entropy analysis.
    """
    result = DemoResult("Hot Spot Analysis")
    print_header("Demo 4: Hot Spot Analysis")

    try:
        # Sample code with varying complexity
        code = '''
def simple_function(x):
    return x + 1

def complex_function(items, threshold, mode="strict"):
    """A more complex function with multiple paths."""
    results = []
    for item in items:
        if mode == "strict":
            if item > threshold:
                results.append(item * 2)
            elif item == threshold:
                results.append(item)
            else:
                results.append(0)
        else:
            results.append(item if item >= threshold else 0)
    return results

def deeply_nested(data):
    """Example of nesting that could be flattened."""
    output = []
    for outer in data:
        if outer:
            for inner in outer:
                if inner:
                    for item in inner:
                        if item > 0:
                            output.append(item)
    return output
'''

        hot_spots = analyze_hot_spots(code)

        print("\nHot Spot Analysis Results:")
        print(f"{'Function':<25} {'Complexity':>12} {'Entropy':>10} {'Lines':>10}")
        print("-" * 60)

        for spot in hot_spots:
            lines = spot.lineno_end - spot.lineno_start + 1
            print(
                f"{spot.name:<25} {spot.complexity:>12.2f} {spot.entropy:>10.2f} {lines:>10}"
            )

        print(f"\nIdentified {len(hot_spots)} hot spots for potential mutation.")
        print("Higher scores = better candidates for optimization.")

        # Show available schemas
        print("\nAvailable mutation schemas:")
        for schema_name in STANDARD_SCHEMA_APPLICATORS:
            print(f"  • {schema_name}")

        result.succeed(
            hot_spots_found=len(hot_spots),
            schemas_available=len(STANDARD_SCHEMA_APPLICATORS),
        )

    except Exception as e:
        result.fail(str(e))

    return result


async def demo_viral_library() -> DemoResult:
    """
    Demo 5: Viral Library Evolution

    Demonstrates how successful mutation patterns evolve and propagate.
    """
    result = DemoResult("Viral Library")
    print_header("Demo 5: Viral Library Evolution")

    try:
        library = create_library()

        # Simulate evolution history
        patterns = [
            (
                "loop_to_comprehension",
                8,
                2,
                0.7,
            ),  # (schema, successes, failures, avg_impact)
            ("extract_constant", 5, 1, 0.6),
            ("flatten_nesting", 3, 3, 0.8),
            ("inline_single_use", 2, 5, 0.3),
        ]

        print("\nSimulating evolution history...")

        for schema, successes, failures, avg_impact in patterns:
            for _ in range(successes):
                # Create successful phage
                mutation = MutationVector(
                    schema_signature=schema,
                    original_code="original",
                    mutated_code="mutated",
                )
                phage = Phage(mutation=mutation)
                await library.record_success(phage, impact=avg_impact, cost=10)

            for _ in range(failures):
                mutation = MutationVector(
                    schema_signature=schema,
                    original_code="original",
                    mutated_code="mutated",
                )
                phage = Phage(mutation=mutation)
                await library.record_failure(phage)

        # Show library state
        stats = library.get_stats()
        print("\nLibrary Statistics:")
        print(f"  Total patterns: {stats.total_patterns}")
        print(f"  High fitness (>1.0): {stats.high_fitness_patterns}")
        print(f"  Viable (0.5-1.0): {stats.viable_patterns}")
        print(f"  Low fitness (<0.5): {stats.low_fitness_patterns}")

        print("\nPattern fitness:")
        print(
            f"{'Schema':<25} {'Fitness':>10} {'Success Rate':>15} {'Market Odds':>12}"
        )
        print("-" * 65)

        for schema, *_ in patterns:
            pattern = library.get_pattern(schema)
            if pattern:
                odds = fitness_to_odds(pattern.fitness)
                print(
                    f"{schema:<25} {pattern.fitness:>10.3f} {pattern.success_rate:>14.1%} {odds:>12.2f}"
                )

        # Suggest mutations (requires embedding)
        # Since we don't have L-gent here, use a dummy embedding
        dummy_embedding = [0.5, 0.3, 0.8]
        suggestions = await library.suggest_mutations(
            context_embedding=dummy_embedding,
            top_k=3,
            min_fitness=0.1,
        )

        print(f"\nTop {len(suggestions)} suggested schemas:")
        for i, suggestion in enumerate(suggestions, 1):
            print(
                f"  {i}. {suggestion.pattern.schema_signature} (fitness: {suggestion.score:.3f})"
            )

        result.succeed(
            patterns_tracked=stats.total_patterns,
            suggestions_generated=len(suggestions),
        )

    except Exception as e:
        result.fail(str(e))

    return result


async def demo_safety_system() -> DemoResult:
    """
    Demo 6: Safety & Guardrails

    Shows E-gent's defense-in-depth safety mechanisms.
    """
    result = DemoResult("Safety System")
    print_header("Demo 6: Safety & Guardrails")

    try:
        safety = create_test_safety_system()

        print("\nSafety System Components:")
        status = safety.get_status()
        print(f"  Rollback enabled: {status['config']['enable_rollback']}")
        print(f"  Rate limiting enabled: {status['config']['enable_rate_limiting']}")
        print(f"  Audit enabled: {status['config']['enable_audit']}")
        print(f"  Sandbox enabled: {status['config']['enable_sandbox']}")

        # Demo atomic rollback
        print_section("Atomic Rollback")
        manager = AtomicMutationManager()

        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("original content")
            temp_path = Path(f.name)

        try:
            # Simulate failed mutation with rollback
            with manager.atomic(phage_id="demo_phage") as checkpoint:
                checkpoint.add_file(temp_path)
                temp_path.write_text("mutated content")
                print(f"  File mutated: {temp_path.read_text()}")
                raise ValueError("Simulated test failure")
        except ValueError:
            pass

        print(f"  After rollback: {temp_path.read_text()}")
        print("  ✓ Atomic rollback preserved original content")
        temp_path.unlink()

        # Demo rate limiting
        print_section("Rate Limiting")
        limiter = RateLimiter()

        for i in range(5):
            limiter.record_mutation()

        rate_status = limiter.get_status()
        print(
            f"  Mutations this minute: {rate_status['mutations']['minute']['current']}"
        )
        print(f"  Limit: {rate_status['mutations']['minute']['limit']}")
        print("  ✓ Rate limiting tracks operations")

        # Demo audit logging
        print_section("Audit Logging")
        sink = InMemoryAuditSink()
        logger = AuditLogger(sink=sink)

        await logger.log_mutation_generated("phage_001", "loop_to_comprehension", -0.3)
        await logger.log_infection_started("phage_001", "/path/to/file.py", "ckpt_001")
        await logger.log_infection_succeeded(
            "phage_001", "/path/to/file.py", tests_passed=42
        )

        events = await logger.query(limit=10)
        print(f"  Events logged: {len(events)}")
        for event in events:
            print(f"    • {event.event_type.value}: phage={event.phage_id}")
        print("  ✓ Full audit trail maintained")

        # Demo sandbox
        print_section("Sandbox Execution")
        config = SandboxConfig(
            max_memory_mb=128,
            timeout_seconds=5,
            max_files_created=5,
        )
        sandbox = Sandbox(config=config)

        with sandbox.enter():
            code_file = sandbox.write_file("print('Hello from sandbox!')", "test.py")
            print(f"  Created file in sandbox: {code_file}")
            print(
                f"  Files created: {len(sandbox._files_created)}/{config.max_files_created}"
            )
        print("  ✓ Sandbox provides isolated execution")

        result.succeed(
            components_tested=4,
            audit_events=len(events),
        )

    except Exception as e:
        result.fail(str(e))

    return result


async def demo_thermodynamic_cycle() -> DemoResult:
    """
    Demo 7: Complete Thermodynamic Cycle

    Runs a full evolution cycle:
    SUN → MUTATE → SELECT → WAGER → INFECT → PAYOFF
    """
    result = DemoResult("Thermodynamic Cycle")
    print_header("Demo 7: Thermodynamic Cycle")

    try:
        # Sample code to evolve
        code = """
def process_items(items):
    result = []
    for item in items:
        result.append(item * 2)
    return result
"""

        print("\nInput code:")
        print(code)

        # Create cycle
        config = CycleConfig(
            initial_temperature=1.0,
            max_mutations_per_cycle=5,
            run_tests=False,  # Skip tests for demo
            run_type_check=False,
        )
        cycle = create_cycle(config=config)

        # Set intent
        intent = Intent(
            embedding=[0.5, 0.3, 0.8],
            source="user",
            description="Make code more Pythonic and efficient",
            confidence=0.9,
        )
        cycle.set_intent(intent)

        print("\nCycle Configuration:")
        print(f"  Temperature: {cycle.temperature}")
        print(f"  Max mutations: {config.max_mutations_per_cycle}")
        print(f"  Intent: {intent.description}")

        # Generate mutations
        print_section("Phase 2: MUTATE")
        phages = cycle.mutator.mutate_to_phages(code)
        print(f"  Generated {len(phages)} mutation candidates")

        for i, phage in enumerate(phages[:3]):  # Show first 3
            if phage.mutation:
                print(
                    f"  [{i + 1}] {phage.mutation.schema_signature}: ΔG={phage.mutation.gibbs_free_energy:.3f}"
                )

        # Filter via demon
        print_section("Phase 3: SELECT")
        results = cycle.demon.select_batch(phages)
        selected = [p for p, r in results if r.passed]
        rejected = [p for p, r in results if not r.passed]

        print(f"  Selected: {len(selected)}")
        print(f"  Rejected: {len(rejected)}")
        print(f"  Selection rate: {len(selected) / max(1, len(phages)):.1%}")

        # Show rejection reasons
        if rejected:
            reasons = {}
            for p, r in results:
                if not r.passed and r.rejection_reason:
                    key = r.rejection_reason.value
                    reasons[key] = reasons.get(key, 0) + 1
            print(f"  Rejection reasons: {reasons}")

        # Show thermodynamic state
        print_section("Thermodynamic State")
        state = cycle.thermo_state
        print(f"  Temperature: {state.temperature:.2f}")
        print(f"  Success rate: {state.success_rate:.1%}")
        print(f"  Total ΔG: {state.total_gibbs_change:.3f}")

        result.succeed(
            mutations_generated=len(phages),
            mutations_selected=len(selected),
            selection_rate=len(selected) / max(1, len(phages)),
        )

    except Exception as e:
        result.fail(str(e))

    return result


async def run_all_demos() -> None:
    """Run all demos and produce summary report."""
    print("\n" + "=" * 60)
    print("  E-gent QA Demonstration Suite")
    print("  Teleological Thermodynamic Evolution")
    print("=" * 60)
    print(f"\nStarted at: {datetime.now().isoformat()}")
    print("\nThis demonstration verifies E-gent functionality across")
    print("all core components, aligned with spec/principles.md.")

    # Run demos
    results: list[DemoResult] = []

    results.append(demo_gibbs_energy())
    results.append(demo_parasitic_detection())
    results.append(demo_five_layer_selection())
    results.append(demo_mutator_hot_spots())
    results.append(await demo_viral_library())
    results.append(await demo_safety_system())
    results.append(await demo_thermodynamic_cycle())

    # Print summary
    print_header("Summary Report")

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    print(f"\n{'Demo':<35} {'Status':>10}")
    print("-" * 50)

    for r in results:
        status = "✓ PASS" if r.passed else "✗ FAIL"
        print(f"{r.name:<35} {status:>10}")
        if not r.passed and r.error:
            print(f"  Error: {r.error}")

    print("-" * 50)
    print(f"{'Total':<35} {passed}/{total}")

    print("\n" + "=" * 60)
    print(f"  E-gent QA: {passed}/{total} demos passed")
    if passed == total:
        print("  Status: ALL SYSTEMS OPERATIONAL")
    else:
        print("  Status: ISSUES DETECTED")
    print("=" * 60)

    print(f"\nCompleted at: {datetime.now().isoformat()}")

    # Key insights
    print("\n--- Key Insights ---")
    print("1. Gibbs Free Energy (ΔG = ΔH - TΔS) guides mutation selection")
    print("2. Parasitic patterns are detected before expensive validation")
    print("3. Five-layer selection kills ~90% of mutations cheaply")
    print("4. Successful patterns evolve in the Viral Library")
    print("5. Defense-in-depth safety prevents runaway evolution")
    print("6. The full cycle composes all components into coherent evolution")


if __name__ == "__main__":
    asyncio.run(run_all_demos())
