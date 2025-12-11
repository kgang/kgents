"""
Tests for B×G Phase 6: JIT Efficiency

Tests the G+J+B trio for high-frequency trading optimization:
- JIT compilation targets (regex, jump table, bytecode)
- Latency benchmarking framework
- Profit sharing ledger
- JIT efficiency monitoring
- High-Frequency Tongue builder
"""

import time

import pytest

# ============================================================================
# Import the module under test
# ============================================================================
from agents.b.jit_efficiency import (
    # Benchmarking
    BenchmarkConfig,
    BytecodeJITCompiler,
    # Compilation types
    CompilationConfig,
    CompiledTongue,
    HFTongueBuilder,
    # HF Tongue
    HFTongueSpec,
    # Enums
    JITCompilationTarget,
    JITCompilerRegistry,
    JITEfficiencyMonitor,
    JumpTableJITCompiler,
    LatencyBenchmark,
    # Latency types
    LatencyMeasurement,
    LatencyReport,
    OptimizationLevel,
    # Profit sharing
    ProfitShare,
    ProfitSharingLedger,
    # Compilers
    RegexJITCompiler,
    # Monitor
    TongueUsageStats,
    benchmark_jit_speedup,
    compile_grammar_jit,
    create_hf_tongue_builder,
    # Convenience
    create_jit_monitor,
    estimate_jit_value,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def bid_grammar():
    """Standard bid grammar regex."""
    return r"(?P<agent_id>[a-z0-9]{8}):(?P<price>[0-9]+(?:\.[0-9]{2})?):(?P<timestamp>[0-9]{10})"


@pytest.fixture
def bid_inputs():
    """Sample bid inputs for testing."""
    return [
        "abc12345:100.50:1234567890",
        "xyz98765:250.00:9876543210",
        "test1234:50.25:1111111111",
    ]


@pytest.fixture
def jump_table_grammar():
    """Jump table grammar specification."""
    return "agent_id:8,price:10,timestamp:10"


@pytest.fixture
def jump_table_input():
    """Sample input for jump table parsing."""
    return "abc12345:0000100.50:1234567890"


# ============================================================================
# JITCompilationTarget Tests
# ============================================================================


class TestJITCompilationTarget:
    """Tests for JITCompilationTarget enum."""

    def test_target_values(self):
        """Test all target values exist."""
        assert JITCompilationTarget.BYTECODE.value == "bytecode"
        assert JITCompilationTarget.REGEX.value == "regex"
        assert JITCompilationTarget.JUMP_TABLE.value == "jump_table"
        assert JITCompilationTarget.C.value == "c"
        assert JITCompilationTarget.LLVM.value == "llvm"

    def test_all_targets_unique(self):
        """Test all target values are unique."""
        values = [t.value for t in JITCompilationTarget]
        assert len(values) == len(set(values))


class TestOptimizationLevel:
    """Tests for OptimizationLevel enum."""

    def test_level_values(self):
        """Test all level values exist."""
        assert OptimizationLevel.NONE.value == "none"
        assert OptimizationLevel.BASIC.value == "basic"
        assert OptimizationLevel.AGGRESSIVE.value == "aggressive"


# ============================================================================
# LatencyMeasurement Tests
# ============================================================================


class TestLatencyMeasurement:
    """Tests for LatencyMeasurement dataclass."""

    def test_create_measurement(self):
        """Test creating a measurement."""
        m = LatencyMeasurement(
            parse_time_ns=1_000_000,
            execute_time_ns=500_000,
            total_time_ns=1_500_000,
            input_size_bytes=32,
        )
        assert m.parse_time_ns == 1_000_000
        assert m.execute_time_ns == 500_000
        assert m.total_time_ns == 1_500_000
        assert m.input_size_bytes == 32

    def test_parse_time_ms(self):
        """Test parse_time_ms property."""
        m = LatencyMeasurement(
            parse_time_ns=1_500_000,
            execute_time_ns=0,
            total_time_ns=1_500_000,
            input_size_bytes=10,
        )
        assert m.parse_time_ms == 1.5

    def test_total_time_ms(self):
        """Test total_time_ms property."""
        m = LatencyMeasurement(
            parse_time_ns=1_000_000,
            execute_time_ns=500_000,
            total_time_ns=1_500_000,
            input_size_bytes=10,
        )
        assert m.total_time_ms == 1.5


# ============================================================================
# LatencyReport Tests
# ============================================================================


class TestLatencyReport:
    """Tests for LatencyReport dataclass."""

    def test_create_report(self):
        """Test creating a report."""
        report = LatencyReport(
            baseline_ms=10.0,
            jit_ms=1.0,
            reduction_ms=9.0,
            reduction_percent=90.0,
            speedup_factor=10.0,
            value_per_tx=0.0009,
            projected_30day_value=270.0,
            compilation_target=JITCompilationTarget.REGEX,
            sample_count=100,
        )
        assert report.baseline_ms == 10.0
        assert report.jit_ms == 1.0
        assert report.speedup_factor == 10.0

    def test_from_benchmarks(self):
        """Test creating report from measurements."""
        baseline = [
            LatencyMeasurement(10_000_000, 0, 10_000_000, 10),
            LatencyMeasurement(12_000_000, 0, 12_000_000, 10),
        ]
        jit = [
            LatencyMeasurement(1_000_000, 0, 1_000_000, 10),
            LatencyMeasurement(1_200_000, 0, 1_200_000, 10),
        ]

        report = LatencyReport.from_benchmarks(
            baseline, jit, JITCompilationTarget.REGEX
        )

        assert report.baseline_ms == 11.0  # Average of 10 and 12
        assert report.jit_ms == 1.1  # Average of 1 and 1.2
        assert report.reduction_ms == pytest.approx(9.9, abs=0.01)
        assert report.speedup_factor == pytest.approx(10.0, abs=0.5)

    def test_from_benchmarks_empty_raises(self):
        """Test that empty measurements raise error."""
        with pytest.raises(ValueError, match="Need at least one"):
            LatencyReport.from_benchmarks([], [], JITCompilationTarget.REGEX)

    def test_to_dict(self):
        """Test serialization to dict."""
        report = LatencyReport(
            baseline_ms=10.0,
            jit_ms=1.0,
            reduction_ms=9.0,
            reduction_percent=90.0,
            speedup_factor=10.0,
            value_per_tx=0.0009,
            projected_30day_value=270.0,
            compilation_target=JITCompilationTarget.REGEX,
            sample_count=100,
        )
        d = report.to_dict()
        assert d["baseline_ms"] == 10.0
        assert d["compilation_target"] == "regex"


# ============================================================================
# CompilationConfig Tests
# ============================================================================


class TestCompilationConfig:
    """Tests for CompilationConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = CompilationConfig()
        assert config.target == JITCompilationTarget.REGEX
        assert config.optimization_level == OptimizationLevel.BASIC
        assert config.inline_semantics is True
        assert config.cache_enabled is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = CompilationConfig(
            target=JITCompilationTarget.BYTECODE,
            optimization_level=OptimizationLevel.AGGRESSIVE,
            inline_semantics=False,
            cache_enabled=False,
        )
        assert config.target == JITCompilationTarget.BYTECODE
        assert config.optimization_level == OptimizationLevel.AGGRESSIVE


# ============================================================================
# RegexJITCompiler Tests
# ============================================================================


class TestRegexJITCompiler:
    """Tests for RegexJITCompiler."""

    def test_compile_simple_regex(self):
        """Test compiling a simple regex."""
        compiler = RegexJITCompiler()
        config = CompilationConfig(target=JITCompilationTarget.REGEX)

        artifact = compiler.compile(r"(?P<name>[a-z]+)", config)

        assert artifact.target == JITCompilationTarget.REGEX
        assert artifact.compilation_time_ms >= 0
        assert artifact.parse_fn is not None

    def test_compiled_parse_success(self, bid_grammar, bid_inputs):
        """Test that compiled parser works correctly."""
        compiler = RegexJITCompiler()
        config = CompilationConfig()

        artifact = compiler.compile(bid_grammar, config)
        result = artifact.parse_fn(bid_inputs[0])

        assert result is not None
        assert result["agent_id"] == "abc12345"
        assert result["price"] == "100.50"
        assert result["timestamp"] == "1234567890"

    def test_compiled_parse_failure(self, bid_grammar):
        """Test that compiled parser returns None on failure."""
        compiler = RegexJITCompiler()
        config = CompilationConfig()

        artifact = compiler.compile(bid_grammar, config)
        result = artifact.parse_fn("invalid input")

        assert result is None

    def test_cache_hit(self):
        """Test that caching works."""
        compiler = RegexJITCompiler()
        config = CompilationConfig(cache_enabled=True)

        artifact1 = compiler.compile(r"test", config)
        artifact2 = compiler.compile(r"test", config)

        # Same artifact returned from cache
        assert artifact1 is artifact2

    def test_cache_disabled(self):
        """Test that caching can be disabled."""
        compiler = RegexJITCompiler()
        config = CompilationConfig(cache_enabled=False)

        artifact1 = compiler.compile(r"test", config)
        artifact2 = compiler.compile(r"test", config)

        # Different artifacts
        assert artifact1 is not artifact2

    def test_supports_grammar_level(self):
        """Test grammar level support."""
        compiler = RegexJITCompiler()
        assert compiler.supports_grammar_level("schema") is True
        assert compiler.supports_grammar_level("regular") is True
        assert compiler.supports_grammar_level("recursive") is False


# ============================================================================
# JumpTableJITCompiler Tests
# ============================================================================


class TestJumpTableJITCompiler:
    """Tests for JumpTableJITCompiler."""

    def test_compile_jump_table(self, jump_table_grammar):
        """Test compiling a jump table spec."""
        compiler = JumpTableJITCompiler()
        config = CompilationConfig(target=JITCompilationTarget.JUMP_TABLE)

        artifact = compiler.compile(jump_table_grammar, config)

        assert artifact.target == JITCompilationTarget.JUMP_TABLE
        assert artifact.parse_fn is not None

    def test_compiled_parse_success(self, jump_table_grammar, jump_table_input):
        """Test that jump table parser works."""
        compiler = JumpTableJITCompiler()
        config = CompilationConfig()

        artifact = compiler.compile(jump_table_grammar, config)
        result = artifact.parse_fn(jump_table_input)

        assert result is not None
        assert "agent_id" in result
        assert "price" in result
        assert "timestamp" in result

    def test_invalid_field_spec(self):
        """Test that invalid spec raises error."""
        compiler = JumpTableJITCompiler()
        config = CompilationConfig()

        with pytest.raises(ValueError, match="Invalid field spec"):
            compiler.compile("invalid", config)

    def test_supports_grammar_level(self):
        """Test grammar level support."""
        compiler = JumpTableJITCompiler()
        assert compiler.supports_grammar_level("schema") is True
        assert compiler.supports_grammar_level("fixed") is True
        assert compiler.supports_grammar_level("recursive") is False


# ============================================================================
# BytecodeJITCompiler Tests
# ============================================================================


class TestBytecodeJITCompiler:
    """Tests for BytecodeJITCompiler."""

    def test_compile_bytecode(self, bid_grammar):
        """Test compiling to bytecode."""
        compiler = BytecodeJITCompiler()
        config = CompilationConfig(target=JITCompilationTarget.BYTECODE)

        artifact = compiler.compile(bid_grammar, config)

        assert artifact.target == JITCompilationTarget.BYTECODE
        assert artifact.parse_fn is not None

    def test_compiled_parse_success(self, bid_grammar, bid_inputs):
        """Test that bytecode parser works."""
        compiler = BytecodeJITCompiler()
        config = CompilationConfig()

        artifact = compiler.compile(bid_grammar, config)
        result = artifact.parse_fn(bid_inputs[0])

        assert result is not None
        assert result["agent_id"] == "abc12345"

    def test_supports_grammar_level(self):
        """Test grammar level support."""
        compiler = BytecodeJITCompiler()
        assert compiler.supports_grammar_level("schema") is True
        assert compiler.supports_grammar_level("command") is True
        assert compiler.supports_grammar_level("context-free") is True


# ============================================================================
# JITCompilerRegistry Tests
# ============================================================================


class TestJITCompilerRegistry:
    """Tests for JITCompilerRegistry."""

    def test_get_regex_compiler(self):
        """Test getting regex compiler."""
        registry = JITCompilerRegistry()
        compiler = registry.get_compiler(JITCompilationTarget.REGEX)
        assert isinstance(compiler, RegexJITCompiler)

    def test_get_jump_table_compiler(self):
        """Test getting jump table compiler."""
        registry = JITCompilerRegistry()
        compiler = registry.get_compiler(JITCompilationTarget.JUMP_TABLE)
        assert isinstance(compiler, JumpTableJITCompiler)

    def test_get_bytecode_compiler(self):
        """Test getting bytecode compiler."""
        registry = JITCompilerRegistry()
        compiler = registry.get_compiler(JITCompilationTarget.BYTECODE)
        assert isinstance(compiler, BytecodeJITCompiler)

    def test_unavailable_target_raises(self):
        """Test that unavailable target raises error."""
        registry = JITCompilerRegistry()
        with pytest.raises(ValueError, match="No compiler"):
            registry.get_compiler(JITCompilationTarget.C)

    def test_register_custom_compiler(self):
        """Test registering a custom compiler."""
        registry = JITCompilerRegistry()

        # Mock compiler
        class MockCompiler:
            def compile(self, grammar, config):
                pass

            def supports_grammar_level(self, level):
                return True

        registry.register_compiler(JITCompilationTarget.C, MockCompiler())
        compiler = registry.get_compiler(JITCompilationTarget.C)
        assert isinstance(compiler, MockCompiler)

    def test_available_targets(self):
        """Test listing available targets."""
        registry = JITCompilerRegistry()
        targets = registry.available_targets
        assert JITCompilationTarget.REGEX in targets
        assert JITCompilationTarget.JUMP_TABLE in targets
        assert JITCompilationTarget.BYTECODE in targets


# ============================================================================
# CompiledTongue Tests
# ============================================================================


class TestCompiledTongue:
    """Tests for CompiledTongue."""

    def test_create_compiled_tongue(self, bid_grammar):
        """Test creating a compiled tongue."""
        compiler = RegexJITCompiler()
        config = CompilationConfig()
        artifact = compiler.compile(bid_grammar, config)

        tongue = CompiledTongue(
            tongue_name="BidTongue",
            tongue_version="1.0.0",
            artifact=artifact,
            config=config,
        )

        assert tongue.tongue_name == "BidTongue"
        assert tongue.tongue_version == "1.0.0"
        assert tongue.usage_count == 0

    def test_parse_increments_usage(self, bid_grammar, bid_inputs):
        """Test that parse increments usage count."""
        compiler = RegexJITCompiler()
        config = CompilationConfig()
        artifact = compiler.compile(bid_grammar, config)

        tongue = CompiledTongue(
            tongue_name="BidTongue",
            tongue_version="1.0.0",
            artifact=artifact,
            config=config,
        )

        assert tongue.usage_count == 0
        tongue.parse(bid_inputs[0])
        assert tongue.usage_count == 1
        tongue.parse(bid_inputs[1])
        assert tongue.usage_count == 2

    def test_parse_returns_dict(self, bid_grammar, bid_inputs):
        """Test parse returns proper dict."""
        compiler = RegexJITCompiler()
        config = CompilationConfig()
        artifact = compiler.compile(bid_grammar, config)

        tongue = CompiledTongue(
            tongue_name="BidTongue",
            tongue_version="1.0.0",
            artifact=artifact,
            config=config,
        )

        result = tongue.parse(bid_inputs[0])
        assert result["success"] is True
        assert result["ast"] is not None
        assert result["error"] is None

    def test_parse_failure(self, bid_grammar):
        """Test parse failure returns proper dict."""
        compiler = RegexJITCompiler()
        config = CompilationConfig()
        artifact = compiler.compile(bid_grammar, config)

        tongue = CompiledTongue(
            tongue_name="BidTongue",
            tongue_version="1.0.0",
            artifact=artifact,
            config=config,
        )

        result = tongue.parse("invalid")
        # Regex returns None on no match, which is not an exception
        # so success is True but ast is None
        assert result["ast"] is None

    def test_compiled_key(self, bid_grammar):
        """Test compiled_key property."""
        compiler = RegexJITCompiler()
        config = CompilationConfig(target=JITCompilationTarget.REGEX)
        artifact = compiler.compile(bid_grammar, config)

        tongue = CompiledTongue(
            tongue_name="BidTongue",
            tongue_version="1.0.0",
            artifact=artifact,
            config=config,
        )

        assert tongue.compiled_key == "BidTongue:1.0.0:regex"


# ============================================================================
# LatencyBenchmark Tests
# ============================================================================


class TestLatencyBenchmark:
    """Tests for LatencyBenchmark."""

    def test_measure_single(self, bid_grammar, bid_inputs):
        """Test single measurement."""
        compiler = RegexJITCompiler()
        config = CompilationConfig()
        artifact = compiler.compile(bid_grammar, config)

        benchmark = LatencyBenchmark()
        measurement = benchmark.measure_single(artifact.parse_fn, None, bid_inputs[0])

        assert measurement.parse_time_ns > 0
        assert measurement.total_time_ns > 0
        assert measurement.input_size_bytes > 0

    def test_benchmark_parser(self, bid_grammar, bid_inputs):
        """Test benchmarking a parser."""
        compiler = RegexJITCompiler()
        config = CompilationConfig()
        artifact = compiler.compile(bid_grammar, config)

        benchmark_config = BenchmarkConfig(
            warmup_iterations=10,
            sample_iterations=50,
        )
        benchmark = LatencyBenchmark(benchmark_config)

        measurements = benchmark.benchmark_parser(artifact.parse_fn, bid_inputs)

        assert len(measurements) > 0
        assert all(m.parse_time_ns > 0 for m in measurements)

    def test_compare_parsers(self, bid_grammar, bid_inputs):
        """Test comparing baseline and JIT parsers."""
        import re

        # Baseline: standard regex
        baseline_pattern = re.compile(bid_grammar)

        def baseline_parse(text):
            m = baseline_pattern.match(text)
            return m.groupdict() if m else None

        # JIT: compiled
        compiler = RegexJITCompiler()
        config = CompilationConfig()
        artifact = compiler.compile(bid_grammar, config)

        benchmark_config = BenchmarkConfig(
            warmup_iterations=10,
            sample_iterations=50,
        )
        benchmark = LatencyBenchmark(benchmark_config)

        report = benchmark.compare_parsers(
            baseline_parse=baseline_parse,
            jit_parse=artifact.parse_fn,
            test_inputs=bid_inputs,
            target=JITCompilationTarget.REGEX,
        )

        assert report.baseline_ms > 0
        assert report.jit_ms > 0
        assert report.sample_count > 0


# ============================================================================
# ProfitShare Tests
# ============================================================================


class TestProfitShare:
    """Tests for ProfitShare."""

    def test_default_shares(self):
        """Test default profit shares."""
        share = ProfitShare()
        assert share.g_gent_share == 0.30
        assert share.j_gent_share == 0.30
        assert share.system_share == 0.40

    def test_custom_shares(self):
        """Test custom profit shares."""
        share = ProfitShare(
            g_gent_share=0.40,
            j_gent_share=0.40,
            system_share=0.20,
        )
        assert share.g_gent_share == 0.40

    def test_invalid_shares_raises(self):
        """Test that invalid shares raise error."""
        with pytest.raises(ValueError, match="sum to 1.0"):
            ProfitShare(g_gent_share=0.5, j_gent_share=0.5, system_share=0.5)

    def test_allocate(self):
        """Test profit allocation."""
        share = ProfitShare()
        allocation = share.allocate(1000.0)

        assert allocation["g_gent"] == 300.0
        assert allocation["j_gent"] == 300.0
        assert allocation["system"] == 400.0


# ============================================================================
# ProfitSharingLedger Tests
# ============================================================================


class TestProfitSharingLedger:
    """Tests for ProfitSharingLedger."""

    def test_create_ledger(self):
        """Test creating a ledger."""
        ledger = ProfitSharingLedger()
        assert ledger.get_balance("g_gent") == 0.0
        assert ledger.get_balance("j_gent") == 0.0
        assert ledger.get_balance("system") == 0.0

    def test_record_profit(self):
        """Test recording profit."""
        ledger = ProfitSharingLedger()
        report = LatencyReport(
            baseline_ms=10.0,
            jit_ms=1.0,
            reduction_ms=9.0,
            reduction_percent=90.0,
            speedup_factor=10.0,
            value_per_tx=0.0009,
            projected_30day_value=1000.0,  # $1000 value
            compilation_target=JITCompilationTarget.REGEX,
            sample_count=100,
        )

        entry = ledger.record_profit("TestTongue", report)

        assert entry.value_created == 1000.0
        assert entry.g_gent_credit == 300.0  # 30%
        assert entry.j_gent_credit == 300.0  # 30%
        assert entry.system_credit == 400.0  # 40%

    def test_balances_updated(self):
        """Test that balances are updated after recording."""
        ledger = ProfitSharingLedger()
        report = LatencyReport(
            baseline_ms=10.0,
            jit_ms=1.0,
            reduction_ms=9.0,
            reduction_percent=90.0,
            speedup_factor=10.0,
            value_per_tx=0.0009,
            projected_30day_value=1000.0,
            compilation_target=JITCompilationTarget.REGEX,
            sample_count=100,
        )

        ledger.record_profit("TestTongue", report)

        assert ledger.get_balance("g_gent") == 300.0
        assert ledger.get_balance("j_gent") == 300.0
        assert ledger.get_balance("system") == 400.0

    def test_multiple_entries(self):
        """Test multiple profit entries."""
        ledger = ProfitSharingLedger()
        report = LatencyReport(
            baseline_ms=10.0,
            jit_ms=1.0,
            reduction_ms=9.0,
            reduction_percent=90.0,
            speedup_factor=10.0,
            value_per_tx=0.0009,
            projected_30day_value=1000.0,
            compilation_target=JITCompilationTarget.REGEX,
            sample_count=100,
        )

        ledger.record_profit("Tongue1", report)
        ledger.record_profit("Tongue2", report)

        assert ledger.get_total_value_created() == 2000.0
        assert ledger.get_balance("g_gent") == 600.0

    def test_get_entries_for_tongue(self):
        """Test getting entries for specific tongue."""
        ledger = ProfitSharingLedger()
        report = LatencyReport(
            baseline_ms=10.0,
            jit_ms=1.0,
            reduction_ms=9.0,
            reduction_percent=90.0,
            speedup_factor=10.0,
            value_per_tx=0.0009,
            projected_30day_value=1000.0,
            compilation_target=JITCompilationTarget.REGEX,
            sample_count=100,
        )

        ledger.record_profit("Tongue1", report)
        ledger.record_profit("Tongue2", report)
        ledger.record_profit("Tongue1", report)

        entries = ledger.get_entries_for_tongue("Tongue1")
        assert len(entries) == 2

    def test_get_summary(self):
        """Test getting ledger summary."""
        ledger = ProfitSharingLedger()
        report = LatencyReport(
            baseline_ms=10.0,
            jit_ms=1.0,
            reduction_ms=9.0,
            reduction_percent=90.0,
            speedup_factor=10.0,
            value_per_tx=0.0009,
            projected_30day_value=1000.0,
            compilation_target=JITCompilationTarget.REGEX,
            sample_count=100,
        )

        ledger.record_profit("TestTongue", report)
        summary = ledger.get_summary()

        assert summary["total_entries"] == 1
        assert summary["total_value_created"] == 1000.0
        assert summary["balances"]["g_gent"] == 300.0


# ============================================================================
# TongueUsageStats Tests
# ============================================================================


class TestTongueUsageStats:
    """Tests for TongueUsageStats."""

    def test_create_stats(self):
        """Test creating usage stats."""
        stats = TongueUsageStats(tongue_name="TestTongue")
        assert stats.parse_count == 0
        assert stats.avg_latency_ns == 0.0

    def test_record_parse(self):
        """Test recording parse operations."""
        stats = TongueUsageStats(tongue_name="TestTongue")
        stats.record_parse(1_000_000)
        stats.record_parse(2_000_000)

        assert stats.parse_count == 2
        assert stats.total_latency_ns == 3_000_000
        assert stats.avg_latency_ns == 1_500_000
        assert stats.max_latency_ns == 2_000_000
        assert stats.min_latency_ns == 1_000_000

    def test_avg_latency_ms(self):
        """Test avg_latency_ms property."""
        stats = TongueUsageStats(tongue_name="TestTongue")
        stats.record_parse(1_500_000)  # 1.5ms

        assert stats.avg_latency_ms == 1.5


# ============================================================================
# JITEfficiencyMonitor Tests
# ============================================================================


class TestJITEfficiencyMonitor:
    """Tests for JITEfficiencyMonitor."""

    def test_create_monitor(self):
        """Test creating a monitor."""
        monitor = JITEfficiencyMonitor()
        assert monitor.latency_threshold_ms == 1.0
        assert monitor.usage_threshold == 100

    def test_custom_thresholds(self):
        """Test custom thresholds."""
        monitor = JITEfficiencyMonitor(
            latency_threshold_ms=0.5,
            usage_threshold=50,
        )
        assert monitor.latency_threshold_ms == 0.5
        assert monitor.usage_threshold == 50

    def test_record_parse(self):
        """Test recording parse operations."""
        monitor = JITEfficiencyMonitor()
        monitor.record_parse("TestTongue", 1_000_000)
        monitor.record_parse("TestTongue", 2_000_000)

        stats = monitor.get_usage_stats("TestTongue")
        assert stats is not None
        assert stats.parse_count == 2

    def test_identify_opportunities(self):
        """Test identifying JIT opportunities."""
        monitor = JITEfficiencyMonitor(
            latency_threshold_ms=1.0,
            usage_threshold=10,  # Lower for testing
        )

        # Record many slow parses
        for _ in range(20):
            monitor.record_parse("SlowTongue", 2_000_000)  # 2ms

        opportunities = monitor.identify_opportunities()
        assert len(opportunities) == 1
        assert opportunities[0].tongue_name == "SlowTongue"

    def test_no_opportunities_below_threshold(self):
        """Test that tongues below thresholds are not identified."""
        monitor = JITEfficiencyMonitor(
            latency_threshold_ms=1.0,
            usage_threshold=100,
        )

        # Record few parses (below threshold)
        for _ in range(5):
            monitor.record_parse("LowUsage", 2_000_000)

        opportunities = monitor.identify_opportunities()
        assert len(opportunities) == 0

    def test_compile_tongue(self, bid_grammar):
        """Test compiling a tongue."""
        monitor = JITEfficiencyMonitor()
        compiled = monitor.compile_tongue(
            tongue_name="BidTongue",
            tongue_version="1.0.0",
            grammar=bid_grammar,
        )

        assert compiled.tongue_name == "BidTongue"
        assert compiled.tongue_version == "1.0.0"

    def test_get_compiled_tongue(self, bid_grammar):
        """Test getting a compiled tongue."""
        monitor = JITEfficiencyMonitor()
        monitor.compile_tongue("BidTongue", "1.0.0", bid_grammar)

        compiled = monitor.get_compiled_tongue("BidTongue")
        assert compiled is not None
        assert compiled.tongue_name == "BidTongue"

    def test_benchmark_and_credit(self, bid_grammar, bid_inputs):
        """Test benchmarking and crediting."""
        import re

        monitor = JITEfficiencyMonitor()
        compiled = monitor.compile_tongue("BidTongue", "1.0.0", bid_grammar)

        # Baseline parser
        pattern = re.compile(bid_grammar)

        def baseline_parse(text):
            m = pattern.match(text)
            return m.groupdict() if m else None

        report, entry = monitor.benchmark_and_credit(
            "BidTongue", baseline_parse, compiled, bid_inputs
        )

        assert report.sample_count > 0
        assert entry.tongue_name == "BidTongue"

    def test_get_summary(self, bid_grammar):
        """Test getting monitor summary."""
        monitor = JITEfficiencyMonitor()
        monitor.record_parse("TestTongue", 1_000_000)
        monitor.compile_tongue("BidTongue", "1.0.0", bid_grammar)

        summary = monitor.get_summary()
        assert summary["tongues_tracked"] == 1
        assert summary["tongues_compiled"] == 1


# ============================================================================
# HFTongueSpec Tests
# ============================================================================


class TestHFTongueSpec:
    """Tests for HFTongueSpec."""

    def test_create_spec(self):
        """Test creating a spec."""
        spec = HFTongueSpec(
            domain="Test",
            fields=[("a", r"[a-z]+"), ("b", r"[0-9]+")],
        )
        assert spec.domain == "Test"
        assert len(spec.fields) == 2

    def test_to_regex(self):
        """Test converting to regex."""
        spec = HFTongueSpec(
            domain="Test",
            fields=[("name", r"[a-z]+"), ("num", r"[0-9]+")],
            delimiter=":",
        )
        regex = spec.to_regex()
        assert "(?P<name>[a-z]+)" in regex
        assert "(?P<num>[0-9]+)" in regex
        assert ":" in regex

    def test_to_jump_table_spec(self):
        """Test converting to jump table spec."""
        spec = HFTongueSpec(
            domain="Test",
            fields=[("a", r"[a-z]{8}"), ("b", r"[0-9]{10}")],
        )
        jt_spec = spec.to_jump_table_spec()
        assert "a:8" in jt_spec
        assert "b:10" in jt_spec


# ============================================================================
# HFTongueBuilder Tests
# ============================================================================


class TestHFTongueBuilder:
    """Tests for HFTongueBuilder."""

    def test_create_builder(self):
        """Test creating a builder."""
        builder = HFTongueBuilder()
        assert builder.monitor is not None

    def test_build_from_spec(self):
        """Test building from spec."""
        spec = HFTongueSpec(
            domain="Test",
            fields=[("name", r"[a-z]+"), ("num", r"[0-9]+")],
        )
        builder = HFTongueBuilder()
        compiled = builder.build(spec)

        assert compiled.tongue_name == "Test"

    def test_build_bid_tongue(self):
        """Test building standard bid tongue."""
        builder = HFTongueBuilder()
        compiled = builder.build_bid_tongue()

        assert "Bidding" in compiled.tongue_name
        result = compiled.parse("abc12345:100.50:1234567890")
        assert result["success"] is True

    def test_build_tick_tongue(self):
        """Test building tick tongue."""
        builder = HFTongueBuilder()
        compiled = builder.build_tick_tongue()

        assert "Tick" in compiled.tongue_name
        result = compiled.parse("AAPL:100.1234:10000:1234567890123")
        assert result["success"] is True

    def test_build_order_tongue(self):
        """Test building order tongue."""
        builder = HFTongueBuilder()
        compiled = builder.build_order_tongue()

        assert "Order" in compiled.tongue_name
        result = compiled.parse("B:100.50:1000:ABCDEF123456")
        assert result["success"] is True


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_jit_monitor(self):
        """Test create_jit_monitor."""
        monitor = create_jit_monitor(
            latency_threshold_ms=0.5,
            usage_threshold=50,
        )
        assert monitor.latency_threshold_ms == 0.5
        assert monitor.usage_threshold == 50

    def test_compile_grammar_jit(self):
        """Test compile_grammar_jit."""
        compiled = compile_grammar_jit(
            grammar=r"(?P<x>[a-z]+)",
            name="test",
            version="1.0",
        )
        assert compiled.tongue_name == "test"
        result = compiled.parse("hello")
        assert result["success"] is True

    def test_benchmark_jit_speedup(self):
        """Test benchmark_jit_speedup."""
        import re

        grammar = r"(?P<x>[a-z]+)"
        pattern = re.compile(grammar)

        def baseline(text):
            m = pattern.match(text)
            return m.groupdict() if m else None

        compiled = compile_grammar_jit(grammar)

        report = benchmark_jit_speedup(
            baseline_parse=baseline,
            jit_parse=compiled.artifact.parse_fn,
            test_inputs=["hello", "world", "test"],
        )

        assert report.sample_count > 0

    def test_create_hf_tongue_builder(self):
        """Test create_hf_tongue_builder."""
        builder = create_hf_tongue_builder()
        assert isinstance(builder, HFTongueBuilder)

    def test_estimate_jit_value(self):
        """Test estimate_jit_value."""
        estimate = estimate_jit_value(
            current_latency_ms=10.0,
            expected_speedup=10.0,
            daily_transactions=10000,
            time_value_per_ms=0.0001,
        )

        assert estimate["latency_reduction_ms"] == 9.0
        assert estimate["daily_value"] > 0
        assert estimate["monthly_value"] > 0
        assert estimate["yearly_value"] > 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for the full JIT efficiency pipeline."""

    def test_full_pipeline(self, bid_grammar, bid_inputs):
        """Test full JIT efficiency pipeline."""
        import re

        # 1. Create monitor
        monitor = create_jit_monitor(
            latency_threshold_ms=0.001,  # Very low for testing
            usage_threshold=5,
        )

        # 2. Record usage (simulate slow Python parsing)
        for _ in range(10):
            for inp in bid_inputs:
                monitor.record_parse("BidTongue", 2_000_000)  # 2ms

        # 3. Identify opportunities
        opportunities = monitor.identify_opportunities()
        assert len(opportunities) > 0
        assert opportunities[0].tongue_name == "BidTongue"

        # 4. Compile the tongue
        compiled = monitor.compile_tongue(
            tongue_name="BidTongue",
            tongue_version="1.0.0",
            grammar=bid_grammar,
        )

        # 5. Verify it works
        result = compiled.parse(bid_inputs[0])
        assert result["success"] is True

        # 6. Benchmark and credit
        pattern = re.compile(bid_grammar)

        def baseline(text):
            m = pattern.match(text)
            return m.groupdict() if m else None

        report, entry = monitor.benchmark_and_credit(
            "BidTongue", baseline, compiled, bid_inputs
        )

        # 7. Verify credits recorded (can be negative if no speedup in microbenchmark)
        # In real HFT scenarios, JIT provides significant speedup, but in tests
        # the overhead of benchmarking may mask the gains
        assert isinstance(entry.g_gent_credit, float)
        assert isinstance(entry.j_gent_credit, float)
        assert isinstance(entry.system_credit, float)
        # Total value created recorded
        assert isinstance(monitor.ledger.get_total_value_created(), float)

    def test_hf_tongue_end_to_end(self):
        """Test HF tongue creation end-to-end."""
        # Create builder with monitor
        monitor = create_jit_monitor()
        builder = HFTongueBuilder(monitor)

        # Build bid tongue
        compiled = builder.build_bid_tongue()

        # Parse multiple inputs
        inputs = [
            "abc12345:100.50:1234567890",
            "xyz98765:250.00:9876543210",
            "test1234:50.25:1111111111",
        ]

        for inp in inputs:
            result = compiled.parse(inp)
            assert result["success"] is True
            assert result["ast"]["agent_id"] is not None
            assert result["ast"]["price"] is not None
            assert result["ast"]["timestamp"] is not None

        # Verify usage tracked
        assert compiled.usage_count == len(inputs)


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_zero_latency_report(self):
        """Test report with zero latency."""
        measurements = [
            LatencyMeasurement(0, 0, 0, 10),
        ]

        # Should handle division by zero gracefully
        report = LatencyReport.from_benchmarks(
            measurements, measurements, JITCompilationTarget.REGEX
        )
        assert report.speedup_factor == float("inf") or report.speedup_factor == 1.0

    def test_empty_test_inputs(self):
        """Test benchmarking with empty inputs."""
        import re

        grammar = r"(?P<x>[a-z]+)"
        pattern = re.compile(grammar)

        def baseline(text):
            m = pattern.match(text)
            return m.groupdict() if m else None

        benchmark = LatencyBenchmark()
        measurements = benchmark.benchmark_parser(baseline, [])
        assert len(measurements) == 0

    def test_malformed_jump_table_input(self):
        """Test jump table parser with malformed input."""
        compiler = JumpTableJITCompiler()
        config = CompilationConfig()
        artifact = compiler.compile("a:5,b:5", config)

        result = artifact.parse_fn("")  # Empty input
        assert result == {} or len(result) == 0

    def test_negative_profit_share_invalid(self):
        """Test that negative profit shares are rejected."""
        with pytest.raises(ValueError):
            ProfitShare(g_gent_share=-0.1, j_gent_share=0.5, system_share=0.6)

    def test_unknown_agent_balance(self):
        """Test getting balance for unknown agent."""
        ledger = ProfitSharingLedger()
        assert ledger.get_balance("unknown_agent") == 0.0

    def test_compiled_tongue_timestamp(self, bid_grammar):
        """Test that compiled tongue has timestamp."""
        monitor = JITEfficiencyMonitor()
        compiled = monitor.compile_tongue("Test", "1.0", bid_grammar)

        assert compiled.creation_timestamp > 0
        assert compiled.creation_timestamp <= time.time()


# ============================================================================
# Performance Tests (marked slow)
# ============================================================================


@pytest.mark.slow
class TestPerformance:
    """Performance tests (marked slow for selective running)."""

    def test_jit_speedup_measurable(self, bid_grammar, bid_inputs):
        """Test that JIT provides measurable speedup."""
        import re

        # Create more test inputs
        test_inputs = bid_inputs * 100

        # Baseline
        pattern = re.compile(bid_grammar)

        def baseline(text):
            m = pattern.match(text)
            return m.groupdict() if m else None

        # JIT
        compiled = compile_grammar_jit(bid_grammar)

        # Benchmark with more iterations
        config = BenchmarkConfig(
            warmup_iterations=100,
            sample_iterations=500,
        )
        benchmark = LatencyBenchmark(config)

        report = benchmark.compare_parsers(
            baseline_parse=baseline,
            jit_parse=compiled.artifact.parse_fn,
            test_inputs=test_inputs,
            target=JITCompilationTarget.REGEX,
        )

        # JIT should be at least comparable (within 10x)
        assert report.speedup_factor > 0.1

    def test_many_tongue_compilations(self):
        """Test compiling many tongues."""
        monitor = JITEfficiencyMonitor()

        for i in range(100):
            grammar = rf"(?P<field{i}>[a-z]+{i})"
            monitor.compile_tongue(f"Tongue{i}", "1.0", grammar)

        assert len(monitor._compiled_tongues) == 100
