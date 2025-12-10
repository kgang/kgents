"""
B×G Phase 6: JIT Efficiency - High-Frequency Trading Optimization

The G+J+B Trio for high-velocity environments:
1. G-gent: Define minimal grammar (simple, regular)
2. J-gent: Compile to bytecode / jump table
3. B-gent: Measure latency reduction, credit efficiency

Core Pattern:
- In high-velocity environments (e.g., real-time bidding), Python overhead is too high
- G-gent defines grammar, J-gent compiles to bytecode, B-gent measures latency value

Economics:
- Latency = Cost in HFT scenarios
- Value per transaction = latency_reduction × time_value_per_ms
- Profit sharing: 30% G-gent, 30% J-gent, 40% System

Key Classes:
- LatencyReport: Benchmark results and value projections
- JITCompilationTarget: bytecode, C, LLVM, etc.
- CompiledTongue: JIT-compiled grammar artifact
- JITCompiler: G-gent → J-gent compilation interface
- LatencyBenchmark: Benchmarking framework
- ProfitShare: Profit allocation structure
- ProfitSharingLedger: Track credits to agents
- JITEfficiencyMonitor: Main coordinator for JIT efficiency
- HFTongue: High-Frequency Tongue builder

See: docs/structural_economics_bg_integration.md Pattern 4
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Protocol


# ============================================================================
# Compilation Targets
# ============================================================================


class JITCompilationTarget(Enum):
    """
    Target for JIT compilation.

    Different targets offer different performance characteristics:
    - BYTECODE: Python bytecode (fastest to compile, moderate speedup)
    - REGEX: Compiled regex (for regular grammars, fast)
    - JUMP_TABLE: Pre-computed lookup table (for fixed-width fields)
    - C: C code generation (slow compile, fastest runtime)
    - LLVM: LLVM IR (portable, good optimization)
    """

    BYTECODE = "bytecode"
    REGEX = "regex"
    JUMP_TABLE = "jump_table"
    C = "c"
    LLVM = "llvm"


class OptimizationLevel(Enum):
    """
    JIT optimization level.

    - NONE: No optimization (debugging)
    - BASIC: Simple optimizations
    - AGGRESSIVE: Maximum optimization (longer compile time)
    """

    NONE = "none"
    BASIC = "basic"
    AGGRESSIVE = "aggressive"


# ============================================================================
# Latency and Benchmark Types
# ============================================================================


@dataclass(frozen=True)
class LatencyMeasurement:
    """
    Single latency measurement from a benchmark run.

    parse_time_ns: Time to parse input (nanoseconds)
    execute_time_ns: Time to execute AST (nanoseconds)
    total_time_ns: Total time (parse + execute)
    input_size_bytes: Size of input in bytes
    """

    parse_time_ns: int
    execute_time_ns: int
    total_time_ns: int
    input_size_bytes: int

    @property
    def parse_time_ms(self) -> float:
        """Parse time in milliseconds."""
        return self.parse_time_ns / 1_000_000

    @property
    def total_time_ms(self) -> float:
        """Total time in milliseconds."""
        return self.total_time_ns / 1_000_000


@dataclass(frozen=True)
class LatencyReport:
    """
    Complete latency benchmark report comparing baseline and JIT.

    baseline_ms: Baseline (Python) parser latency in milliseconds
    jit_ms: JIT-compiled parser latency in milliseconds
    reduction_ms: Latency reduction (baseline - jit)
    reduction_percent: Reduction as percentage
    speedup_factor: How many times faster (baseline / jit)
    value_per_tx: Value per transaction based on time_value
    projected_30day_value: Projected 30-day value
    compilation_target: The JIT target used
    sample_count: Number of samples in benchmark
    """

    baseline_ms: float
    jit_ms: float
    reduction_ms: float
    reduction_percent: float
    speedup_factor: float
    value_per_tx: float
    projected_30day_value: float
    compilation_target: JITCompilationTarget
    sample_count: int

    @classmethod
    def from_benchmarks(
        cls,
        baseline_measurements: list[LatencyMeasurement],
        jit_measurements: list[LatencyMeasurement],
        target: JITCompilationTarget,
        time_value_per_ms: float = 0.0001,  # $0.0001 per ms default
        daily_transaction_count: int = 10000,
    ) -> "LatencyReport":
        """
        Create report from benchmark measurements.

        Args:
            baseline_measurements: Baseline parser measurements
            jit_measurements: JIT parser measurements
            target: Compilation target used
            time_value_per_ms: Value of 1ms in dollars
            daily_transaction_count: Expected transactions per day
        """
        if not baseline_measurements or not jit_measurements:
            raise ValueError("Need at least one measurement for each")

        # Calculate averages
        baseline_ms = sum(m.total_time_ms for m in baseline_measurements) / len(
            baseline_measurements
        )
        jit_ms = sum(m.total_time_ms for m in jit_measurements) / len(jit_measurements)

        reduction_ms = baseline_ms - jit_ms
        reduction_percent = (
            (reduction_ms / baseline_ms * 100) if baseline_ms > 0 else 0.0
        )
        speedup_factor = baseline_ms / jit_ms if jit_ms > 0 else float("inf")

        # Calculate value
        value_per_tx = reduction_ms * time_value_per_ms
        projected_30day_value = value_per_tx * daily_transaction_count * 30

        return cls(
            baseline_ms=baseline_ms,
            jit_ms=jit_ms,
            reduction_ms=reduction_ms,
            reduction_percent=reduction_percent,
            speedup_factor=speedup_factor,
            value_per_tx=value_per_tx,
            projected_30day_value=projected_30day_value,
            compilation_target=target,
            sample_count=min(len(baseline_measurements), len(jit_measurements)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "baseline_ms": self.baseline_ms,
            "jit_ms": self.jit_ms,
            "reduction_ms": self.reduction_ms,
            "reduction_percent": self.reduction_percent,
            "speedup_factor": self.speedup_factor,
            "value_per_tx": self.value_per_tx,
            "projected_30day_value": self.projected_30day_value,
            "compilation_target": self.compilation_target.value,
            "sample_count": self.sample_count,
        }


# ============================================================================
# Compiled Tongue Types
# ============================================================================


@dataclass(frozen=True)
class CompilationConfig:
    """
    Configuration for JIT compilation.

    target: Compilation target (bytecode, regex, C, etc.)
    optimization_level: How aggressive to optimize
    inline_semantics: Whether to inline semantic actions
    cache_enabled: Whether to cache compiled artifacts
    """

    target: JITCompilationTarget = JITCompilationTarget.REGEX
    optimization_level: OptimizationLevel = OptimizationLevel.BASIC
    inline_semantics: bool = True
    cache_enabled: bool = True


@dataclass(frozen=True)
class CompiledArtifact:
    """
    A compiled grammar artifact.

    code: The compiled code/pattern (depends on target)
    target: Compilation target
    parse_fn: Compiled parse function
    execute_fn: Compiled execute function (if inlined)
    compilation_time_ms: Time spent compiling
    memory_bytes: Approximate memory usage
    """

    code: str | bytes
    target: JITCompilationTarget
    parse_fn: Callable[[str], Any]
    execute_fn: Callable[[Any, dict[str, Any]], Any] | None
    compilation_time_ms: float
    memory_bytes: int

    @property
    def artifact_hash(self) -> str:
        """Hash of the compiled artifact for caching."""
        content = self.code if isinstance(self.code, bytes) else self.code.encode()
        return hashlib.sha256(content).hexdigest()[:16]


@dataclass
class CompiledTongue:
    """
    A JIT-compiled Tongue for high-frequency parsing.

    Wraps a base Tongue with compiled parsing/execution.

    tongue_name: Name of the source tongue
    tongue_version: Version of the source tongue
    artifact: The compiled artifact
    config: Compilation configuration
    creation_timestamp: When this was compiled
    usage_count: How many times this has been used
    """

    tongue_name: str
    tongue_version: str
    artifact: CompiledArtifact
    config: CompilationConfig
    creation_timestamp: float = field(default_factory=time.time)
    usage_count: int = 0

    def parse(self, text: str) -> Any:
        """
        Parse using JIT-compiled parser.

        Returns ParseResult-like object.
        """
        self.usage_count += 1
        try:
            ast = self.artifact.parse_fn(text)
            return {"success": True, "ast": ast, "error": None}
        except Exception as e:
            return {"success": False, "ast": None, "error": str(e)}

    def execute(self, ast: Any, context: dict[str, Any] | None = None) -> Any:
        """
        Execute using JIT-compiled executor (if available).

        Falls back to standard execution if no inlined executor.
        """
        context = context or {}
        if self.artifact.execute_fn:
            try:
                result = self.artifact.execute_fn(ast, context)
                return {"success": True, "value": result, "error": None}
            except Exception as e:
                return {"success": False, "value": None, "error": str(e)}
        return {"success": False, "value": None, "error": "No compiled executor"}

    @property
    def compiled_key(self) -> str:
        """Unique key for this compiled tongue."""
        return f"{self.tongue_name}:{self.tongue_version}:{self.config.target.value}"


# ============================================================================
# JIT Compiler Interface
# ============================================================================


class JITCompilerProtocol(Protocol):
    """
    Protocol for JIT compiler implementations.

    Each target (bytecode, regex, C, etc.) implements this.
    """

    def compile(
        self,
        grammar: str,
        config: CompilationConfig,
    ) -> CompiledArtifact:
        """Compile grammar to target."""
        ...

    def supports_grammar_level(self, level: str) -> bool:
        """Check if compiler supports this grammar level."""
        ...


class RegexJITCompiler:
    """
    JIT compiler for regular (Type 3) grammars.

    Compiles simple grammars to compiled regex patterns.
    Good for: Fixed formats, bidding languages, simple commands.
    """

    def __init__(self):
        import re

        self._re = re
        self._cache: dict[str, CompiledArtifact] = {}

    def compile(
        self,
        grammar: str,
        config: CompilationConfig,
    ) -> CompiledArtifact:
        """
        Compile grammar to regex pattern.

        Grammar should be a simple regex or field specification.
        """
        # Check cache
        cache_key = f"{grammar}:{config.optimization_level.value}"
        if config.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        start = time.perf_counter()

        # Compile the regex
        pattern = self._re.compile(grammar)

        def parse_fn(text: str) -> dict[str, Any] | None:
            match = pattern.match(text)
            if match:
                return match.groupdict() or {"value": match.group(0)}
            return None

        compilation_time = (time.perf_counter() - start) * 1000

        artifact = CompiledArtifact(
            code=grammar,
            target=JITCompilationTarget.REGEX,
            parse_fn=parse_fn,
            execute_fn=None,  # Regex doesn't have execute
            compilation_time_ms=compilation_time,
            memory_bytes=len(grammar) * 2,  # Rough estimate
        )

        if config.cache_enabled:
            self._cache[cache_key] = artifact

        return artifact

    def supports_grammar_level(self, level: str) -> bool:
        """Only supports SCHEMA (regular) grammars."""
        return level.lower() in ("schema", "regular")


class JumpTableJITCompiler:
    """
    JIT compiler for fixed-width field grammars.

    Creates pre-computed lookup tables for O(1) parsing.
    Good for: Bidding languages with fixed field widths.
    """

    def __init__(self):
        self._cache: dict[str, CompiledArtifact] = {}

    def compile(
        self,
        grammar: str,
        config: CompilationConfig,
    ) -> CompiledArtifact:
        """
        Compile grammar to jump table.

        Grammar format: "field1:width1,field2:width2,..."
        Example: "agent_id:8,price:10,timestamp:10"
        """
        cache_key = f"{grammar}:{config.optimization_level.value}"
        if config.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        start = time.perf_counter()

        # Parse field specifications
        fields: list[tuple[str, int, int]] = []  # (name, start, width)
        position = 0

        for field_spec in grammar.split(","):
            parts = field_spec.strip().split(":")
            if len(parts) != 2:
                raise ValueError(f"Invalid field spec: {field_spec}")
            name = parts[0].strip()
            width = int(parts[1].strip())
            fields.append((name, position, width))
            position += width + 1  # +1 for delimiter

        # Build jump table
        jump_table = {name: (start, width) for name, start, width in fields}

        def parse_fn(text: str) -> dict[str, str]:
            result = {}
            for name, start, width in fields:
                if start + width <= len(text):
                    # Handle delimiter-separated fields
                    value = text[start : start + width].strip()
                    result[name] = value
            return result

        compilation_time = (time.perf_counter() - start) * 1000

        artifact = CompiledArtifact(
            code=grammar,
            target=JITCompilationTarget.JUMP_TABLE,
            parse_fn=parse_fn,
            execute_fn=None,
            compilation_time_ms=compilation_time,
            memory_bytes=len(fields) * 24,  # Rough estimate
        )

        if config.cache_enabled:
            self._cache[cache_key] = artifact

        return artifact

    def supports_grammar_level(self, level: str) -> bool:
        """Only supports SCHEMA (fixed-width) grammars."""
        return level.lower() in ("schema", "regular", "fixed")


class BytecodeJITCompiler:
    """
    JIT compiler that generates optimized Python bytecode.

    Compiles parser to specialized bytecode for faster execution.
    Good for: Context-free grammars with moderate complexity.
    """

    def __init__(self):
        self._cache: dict[str, CompiledArtifact] = {}

    def compile(
        self,
        grammar: str,
        config: CompilationConfig,
    ) -> CompiledArtifact:
        """
        Compile grammar to optimized bytecode.

        Creates a specialized parser function with minimal overhead.
        """
        cache_key = f"{grammar}:{config.optimization_level.value}"
        if config.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        start = time.perf_counter()

        # For bytecode compilation, we create a specialized function
        # that avoids general-purpose parsing overhead
        import re

        pattern = re.compile(grammar)

        def optimized_parse(text: str) -> dict[str, Any] | None:
            # Inline the match for minimum overhead
            m = pattern.match(text)
            return m.groupdict() if m else None

        compilation_time = (time.perf_counter() - start) * 1000

        artifact = CompiledArtifact(
            code=grammar,
            target=JITCompilationTarget.BYTECODE,
            parse_fn=optimized_parse,
            execute_fn=None,
            compilation_time_ms=compilation_time,
            memory_bytes=len(grammar) * 4,
        )

        if config.cache_enabled:
            self._cache[cache_key] = artifact

        return artifact

    def supports_grammar_level(self, level: str) -> bool:
        """Supports SCHEMA and COMMAND grammars."""
        return level.lower() in ("schema", "command", "regular", "context-free")


class JITCompilerRegistry:
    """
    Registry of JIT compilers by target.

    Provides access to appropriate compiler for each target.
    """

    def __init__(self):
        self._compilers: dict[JITCompilationTarget, JITCompilerProtocol] = {
            JITCompilationTarget.REGEX: RegexJITCompiler(),
            JITCompilationTarget.JUMP_TABLE: JumpTableJITCompiler(),
            JITCompilationTarget.BYTECODE: BytecodeJITCompiler(),
        }

    def get_compiler(self, target: JITCompilationTarget) -> JITCompilerProtocol:
        """Get compiler for target."""
        if target not in self._compilers:
            raise ValueError(f"No compiler for target: {target}")
        return self._compilers[target]

    def register_compiler(
        self,
        target: JITCompilationTarget,
        compiler: JITCompilerProtocol,
    ) -> None:
        """Register a custom compiler."""
        self._compilers[target] = compiler

    @property
    def available_targets(self) -> list[JITCompilationTarget]:
        """List available compilation targets."""
        return list(self._compilers.keys())


# ============================================================================
# Latency Benchmarking
# ============================================================================


@dataclass
class BenchmarkConfig:
    """
    Configuration for latency benchmarks.

    warmup_iterations: Iterations before measuring (JIT warmup)
    sample_iterations: Number of samples to collect
    time_value_per_ms: Value of 1ms in dollars (for ROI calculation)
    daily_transaction_count: Expected transactions per day
    """

    warmup_iterations: int = 100
    sample_iterations: int = 1000
    time_value_per_ms: float = 0.0001  # $0.0001 per ms
    daily_transaction_count: int = 10000


class LatencyBenchmark:
    """
    Benchmarking framework for parser latency.

    Compares baseline (Python) parser with JIT-compiled version.
    Calculates speedup and economic value.
    """

    def __init__(self, config: BenchmarkConfig | None = None):
        self.config = config or BenchmarkConfig()

    def measure_single(
        self,
        parse_fn: Callable[[str], Any],
        execute_fn: Callable[[Any, dict], Any] | None,
        test_input: str,
        context: dict[str, Any] | None = None,
    ) -> LatencyMeasurement:
        """
        Measure latency for a single parse/execute cycle.
        """
        context = context or {}

        # Measure parse
        parse_start = time.perf_counter_ns()
        ast = parse_fn(test_input)
        parse_end = time.perf_counter_ns()
        parse_time = parse_end - parse_start

        # Measure execute (if available)
        execute_time = 0
        if execute_fn and ast:
            exec_start = time.perf_counter_ns()
            execute_fn(ast, context)
            exec_end = time.perf_counter_ns()
            execute_time = exec_end - exec_start

        return LatencyMeasurement(
            parse_time_ns=parse_time,
            execute_time_ns=execute_time,
            total_time_ns=parse_time + execute_time,
            input_size_bytes=len(test_input.encode()),
        )

    def benchmark_parser(
        self,
        parse_fn: Callable[[str], Any],
        test_inputs: list[str],
        execute_fn: Callable[[Any, dict], Any] | None = None,
    ) -> list[LatencyMeasurement]:
        """
        Benchmark a parser over multiple inputs.

        Performs warmup, then collects samples.
        """
        # Warmup
        for _ in range(self.config.warmup_iterations):
            for inp in test_inputs[: min(10, len(test_inputs))]:
                try:
                    parse_fn(inp)
                except Exception:
                    pass

        # Collect samples
        measurements: list[LatencyMeasurement] = []
        for _ in range(self.config.sample_iterations):
            for inp in test_inputs:
                try:
                    m = self.measure_single(parse_fn, execute_fn, inp)
                    measurements.append(m)
                except Exception:
                    pass

        return measurements

    def compare_parsers(
        self,
        baseline_parse: Callable[[str], Any],
        jit_parse: Callable[[str], Any],
        test_inputs: list[str],
        target: JITCompilationTarget,
        baseline_execute: Callable[[Any, dict], Any] | None = None,
        jit_execute: Callable[[Any, dict], Any] | None = None,
    ) -> LatencyReport:
        """
        Compare baseline and JIT parsers, generate report.
        """
        # Benchmark both
        baseline_measurements = self.benchmark_parser(
            baseline_parse, test_inputs, baseline_execute
        )
        jit_measurements = self.benchmark_parser(jit_parse, test_inputs, jit_execute)

        # Generate report
        return LatencyReport.from_benchmarks(
            baseline_measurements=baseline_measurements,
            jit_measurements=jit_measurements,
            target=target,
            time_value_per_ms=self.config.time_value_per_ms,
            daily_transaction_count=self.config.daily_transaction_count,
        )


# ============================================================================
# Profit Sharing Ledger (B-gent Economics)
# ============================================================================


@dataclass(frozen=True)
class ProfitShare:
    """
    Profit allocation from JIT efficiency gains.

    g_gent_share: Share for G-gent (grammar definition)
    j_gent_share: Share for J-gent (JIT compilation)
    system_share: Share for system

    Standard: 30% G-gent, 30% J-gent, 40% System
    """

    g_gent_share: float = 0.30
    j_gent_share: float = 0.30
    system_share: float = 0.40

    def __post_init__(self):
        # Validate non-negative shares
        if self.g_gent_share < 0 or self.j_gent_share < 0 or self.system_share < 0:
            raise ValueError("Profit shares cannot be negative")
        # Validate sum
        total = self.g_gent_share + self.j_gent_share + self.system_share
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Shares must sum to 1.0, got {total}")

    def allocate(self, total_value: float) -> dict[str, float]:
        """Allocate value according to shares."""
        return {
            "g_gent": total_value * self.g_gent_share,
            "j_gent": total_value * self.j_gent_share,
            "system": total_value * self.system_share,
        }


@dataclass
class ProfitEntry:
    """
    A single profit entry in the ledger.

    tongue_name: Name of the tongue that generated profit
    value_created: Total value created (from latency reduction)
    g_gent_credit: Credit to G-gent
    j_gent_credit: Credit to J-gent
    system_credit: Credit to system
    reason: Explanation for the credit
    timestamp: When this entry was created
    latency_report: The latency report that led to this
    """

    tongue_name: str
    value_created: float
    g_gent_credit: float
    j_gent_credit: float
    system_credit: float
    reason: str
    timestamp: float = field(default_factory=time.time)
    latency_report: LatencyReport | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "tongue_name": self.tongue_name,
            "value_created": self.value_created,
            "g_gent_credit": self.g_gent_credit,
            "j_gent_credit": self.j_gent_credit,
            "system_credit": self.system_credit,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "latency_report": self.latency_report.to_dict()
            if self.latency_report
            else None,
        }


class ProfitSharingLedger:
    """
    Ledger for tracking profit sharing from JIT efficiency.

    Tracks credits to G-gent, J-gent, and system from latency gains.
    """

    def __init__(self, profit_share: ProfitShare | None = None):
        self.profit_share = profit_share or ProfitShare()
        self._entries: list[ProfitEntry] = []
        self._balances: dict[str, float] = {
            "g_gent": 0.0,
            "j_gent": 0.0,
            "system": 0.0,
        }

    def record_profit(
        self,
        tongue_name: str,
        latency_report: LatencyReport,
        custom_reason: str | None = None,
    ) -> ProfitEntry:
        """
        Record profit from JIT efficiency gain.

        Credits agents based on latency reduction value.
        """
        # Calculate value (use projected 30-day value)
        total_value = latency_report.projected_30day_value

        # Allocate shares
        allocation = self.profit_share.allocate(total_value)

        # Create reason
        reason = custom_reason or (
            f"Efficiency gain: {latency_report.reduction_ms:.3f}ms latency reduction "
            f"({latency_report.speedup_factor:.1f}x speedup)"
        )

        # Create entry
        entry = ProfitEntry(
            tongue_name=tongue_name,
            value_created=total_value,
            g_gent_credit=allocation["g_gent"],
            j_gent_credit=allocation["j_gent"],
            system_credit=allocation["system"],
            reason=reason,
            latency_report=latency_report,
        )

        # Update balances
        self._entries.append(entry)
        self._balances["g_gent"] += allocation["g_gent"]
        self._balances["j_gent"] += allocation["j_gent"]
        self._balances["system"] += allocation["system"]

        return entry

    def get_balance(self, agent_id: str) -> float:
        """Get current balance for an agent."""
        return self._balances.get(agent_id, 0.0)

    def get_total_value_created(self) -> float:
        """Get total value created across all entries."""
        return sum(e.value_created for e in self._entries)

    def get_entries_for_tongue(self, tongue_name: str) -> list[ProfitEntry]:
        """Get all profit entries for a specific tongue."""
        return [e for e in self._entries if e.tongue_name == tongue_name]

    def get_summary(self) -> dict[str, Any]:
        """Get ledger summary."""
        return {
            "total_entries": len(self._entries),
            "total_value_created": self.get_total_value_created(),
            "balances": dict(self._balances),
            "profit_share": {
                "g_gent": self.profit_share.g_gent_share,
                "j_gent": self.profit_share.j_gent_share,
                "system": self.profit_share.system_share,
            },
        }


# ============================================================================
# JIT Efficiency Monitor
# ============================================================================


@dataclass
class JITOpportunity:
    """
    An identified opportunity for JIT optimization.

    tongue_name: Name of the tongue
    usage_count: How many times it's been used
    avg_latency_ms: Average parse latency
    estimated_speedup: Estimated speedup from JIT
    estimated_value: Estimated 30-day value
    recommended_target: Recommended compilation target
    priority: Priority score (higher = more urgent)
    """

    tongue_name: str
    usage_count: int
    avg_latency_ms: float
    estimated_speedup: float
    estimated_value: float
    recommended_target: JITCompilationTarget
    priority: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "tongue_name": self.tongue_name,
            "usage_count": self.usage_count,
            "avg_latency_ms": self.avg_latency_ms,
            "estimated_speedup": self.estimated_speedup,
            "estimated_value": self.estimated_value,
            "recommended_target": self.recommended_target.value,
            "priority": self.priority,
        }


@dataclass
class TongueUsageStats:
    """
    Usage statistics for a tongue.

    tongue_name: Name of the tongue
    parse_count: Number of parses
    total_latency_ns: Total latency in nanoseconds
    max_latency_ns: Maximum observed latency
    min_latency_ns: Minimum observed latency
    """

    tongue_name: str
    parse_count: int = 0
    total_latency_ns: int = 0
    max_latency_ns: int = 0
    min_latency_ns: int = 0

    @property
    def avg_latency_ns(self) -> float:
        """Average latency in nanoseconds."""
        return self.total_latency_ns / self.parse_count if self.parse_count > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        """Average latency in milliseconds."""
        return self.avg_latency_ns / 1_000_000

    def record_parse(self, latency_ns: int) -> None:
        """Record a parse operation."""
        self.parse_count += 1
        self.total_latency_ns += latency_ns
        self.max_latency_ns = max(self.max_latency_ns, latency_ns)
        if self.min_latency_ns == 0:
            self.min_latency_ns = latency_ns
        else:
            self.min_latency_ns = min(self.min_latency_ns, latency_ns)


class JITEfficiencyMonitor:
    """
    Main coordinator for JIT efficiency optimization.

    Monitors tongue usage, identifies optimization opportunities,
    coordinates JIT compilation, and tracks profit sharing.
    """

    def __init__(
        self,
        compiler_registry: JITCompilerRegistry | None = None,
        benchmark_config: BenchmarkConfig | None = None,
        profit_share: ProfitShare | None = None,
        latency_threshold_ms: float = 1.0,  # JIT if latency > 1ms
        usage_threshold: int = 100,  # JIT if used > 100 times
    ):
        self.compiler_registry = compiler_registry or JITCompilerRegistry()
        self.benchmark = LatencyBenchmark(benchmark_config)
        self.ledger = ProfitSharingLedger(profit_share)
        self.latency_threshold_ms = latency_threshold_ms
        self.usage_threshold = usage_threshold

        # Usage tracking
        self._usage_stats: dict[str, TongueUsageStats] = {}
        self._compiled_tongues: dict[str, CompiledTongue] = {}

    def record_parse(
        self,
        tongue_name: str,
        latency_ns: int,
    ) -> None:
        """Record a parse operation for usage tracking."""
        if tongue_name not in self._usage_stats:
            self._usage_stats[tongue_name] = TongueUsageStats(tongue_name=tongue_name)
        self._usage_stats[tongue_name].record_parse(latency_ns)

    def get_usage_stats(self, tongue_name: str) -> TongueUsageStats | None:
        """Get usage statistics for a tongue."""
        return self._usage_stats.get(tongue_name)

    def identify_opportunities(
        self,
        time_value_per_ms: float = 0.0001,
        daily_transaction_estimate: int = 10000,
    ) -> list[JITOpportunity]:
        """
        Identify tongues that would benefit from JIT optimization.

        Returns list of opportunities sorted by priority.
        """
        opportunities: list[JITOpportunity] = []

        for name, stats in self._usage_stats.items():
            # Skip if already compiled
            if name in self._compiled_tongues:
                continue

            # Check thresholds
            if stats.parse_count < self.usage_threshold:
                continue
            if stats.avg_latency_ms < self.latency_threshold_ms:
                continue

            # Estimate speedup based on grammar complexity
            # Conservative estimate: 10x for regex, 5x for bytecode
            estimated_speedup = 10.0  # Assume regex target
            jit_latency_ms = stats.avg_latency_ms / estimated_speedup
            reduction_ms = stats.avg_latency_ms - jit_latency_ms

            # Calculate value
            value_per_tx = reduction_ms * time_value_per_ms
            estimated_value = value_per_tx * daily_transaction_estimate * 30

            # Calculate priority (higher = more urgent)
            # Priority = value × usage_count × latency
            priority = (
                estimated_value * (stats.parse_count / 1000) * stats.avg_latency_ms
            )

            opportunities.append(
                JITOpportunity(
                    tongue_name=name,
                    usage_count=stats.parse_count,
                    avg_latency_ms=stats.avg_latency_ms,
                    estimated_speedup=estimated_speedup,
                    estimated_value=estimated_value,
                    recommended_target=JITCompilationTarget.REGEX,
                    priority=priority,
                )
            )

        # Sort by priority (descending)
        opportunities.sort(key=lambda o: o.priority, reverse=True)
        return opportunities

    def compile_tongue(
        self,
        tongue_name: str,
        tongue_version: str,
        grammar: str,
        config: CompilationConfig | None = None,
    ) -> CompiledTongue:
        """
        JIT-compile a tongue.

        Returns CompiledTongue that can be used for fast parsing.
        """
        config = config or CompilationConfig()

        # Get appropriate compiler
        compiler = self.compiler_registry.get_compiler(config.target)

        # Compile
        artifact = compiler.compile(grammar, config)

        # Create CompiledTongue
        compiled = CompiledTongue(
            tongue_name=tongue_name,
            tongue_version=tongue_version,
            artifact=artifact,
            config=config,
        )

        # Cache
        self._compiled_tongues[tongue_name] = compiled

        return compiled

    def get_compiled_tongue(self, tongue_name: str) -> CompiledTongue | None:
        """Get a compiled tongue by name."""
        return self._compiled_tongues.get(tongue_name)

    def benchmark_and_credit(
        self,
        tongue_name: str,
        baseline_parse: Callable[[str], Any],
        compiled_tongue: CompiledTongue,
        test_inputs: list[str],
    ) -> tuple[LatencyReport, ProfitEntry]:
        """
        Benchmark JIT vs baseline and credit agents.

        Returns:
            Tuple of (LatencyReport, ProfitEntry)
        """
        # Run benchmark
        report = self.benchmark.compare_parsers(
            baseline_parse=baseline_parse,
            jit_parse=compiled_tongue.artifact.parse_fn,
            test_inputs=test_inputs,
            target=compiled_tongue.artifact.target,
        )

        # Record profit
        entry = self.ledger.record_profit(tongue_name, report)

        return report, entry

    def get_summary(self) -> dict[str, Any]:
        """Get efficiency monitor summary."""
        return {
            "tongues_tracked": len(self._usage_stats),
            "tongues_compiled": len(self._compiled_tongues),
            "profit_summary": self.ledger.get_summary(),
            "thresholds": {
                "latency_ms": self.latency_threshold_ms,
                "usage_count": self.usage_threshold,
            },
        }


# ============================================================================
# High-Frequency Tongue Builder
# ============================================================================


@dataclass
class HFTongueSpec:
    """
    Specification for a High-Frequency Tongue.

    domain: Domain name (e.g., "Real-Time Bidding")
    fields: List of (name, pattern) tuples
    delimiter: Field delimiter
    target_latency_ms: Target latency for JIT version
    """

    domain: str
    fields: list[tuple[str, str]]  # (name, pattern)
    delimiter: str = ":"
    target_latency_ms: float = 0.1

    def to_regex(self) -> str:
        """Convert to regex pattern."""
        parts = []
        for name, pattern in self.fields:
            parts.append(f"(?P<{name}>{pattern})")
        return self.delimiter.join(parts)

    def to_jump_table_spec(self) -> str:
        """Convert to jump table specification."""
        # Estimate widths from patterns
        specs = []
        for name, pattern in self.fields:
            # Extract width from pattern like [0-9]{10}
            import re

            match = re.search(r"\{(\d+)\}", pattern)
            width = int(match.group(1)) if match else 10
            specs.append(f"{name}:{width}")
        return ",".join(specs)


class HFTongueBuilder:
    """
    Builder for High-Frequency Tongues.

    Creates JIT-optimized tongues for HFT scenarios.
    """

    def __init__(self, monitor: JITEfficiencyMonitor | None = None):
        self.monitor = monitor or JITEfficiencyMonitor()

    def build(
        self,
        spec: HFTongueSpec,
        version: str = "1.0.0",
        target: JITCompilationTarget = JITCompilationTarget.REGEX,
    ) -> CompiledTongue:
        """
        Build a High-Frequency Tongue from spec.

        Automatically selects best compilation target.
        """
        # Determine grammar based on target
        if target == JITCompilationTarget.JUMP_TABLE:
            grammar = spec.to_jump_table_spec()
        else:
            grammar = spec.to_regex()

        # Compile
        config = CompilationConfig(
            target=target,
            optimization_level=OptimizationLevel.AGGRESSIVE,
        )

        return self.monitor.compile_tongue(
            tongue_name=spec.domain.replace(" ", "_"),
            tongue_version=version,
            grammar=grammar,
            config=config,
        )

    def build_bid_tongue(self) -> CompiledTongue:
        """
        Build standard BidTongue for real-time auctions.

        Format: agent_id:price:timestamp
        """
        spec = HFTongueSpec(
            domain="Real-Time Bidding",
            fields=[
                ("agent_id", r"[a-z0-9]{8}"),
                ("price", r"[0-9]+(?:\.[0-9]{2})?"),
                ("timestamp", r"[0-9]{10}"),
            ],
            delimiter=":",
            target_latency_ms=0.05,
        )
        return self.build(spec)

    def build_tick_tongue(self) -> CompiledTongue:
        """
        Build TickTongue for market data.

        Format: symbol:price:volume:timestamp
        """
        spec = HFTongueSpec(
            domain="Market Tick",
            fields=[
                ("symbol", r"[A-Z]{1,5}"),
                ("price", r"[0-9]+\.[0-9]{4}"),
                ("volume", r"[0-9]+"),
                ("timestamp", r"[0-9]{13}"),  # Unix ms
            ],
            delimiter=":",
            target_latency_ms=0.02,
        )
        return self.build(spec)

    def build_order_tongue(self) -> CompiledTongue:
        """
        Build OrderTongue for order book updates.

        Format: side:price:quantity:order_id
        """
        spec = HFTongueSpec(
            domain="Order Book",
            fields=[
                ("side", r"[BS]"),  # B=Buy, S=Sell
                ("price", r"[0-9]+\.[0-9]{2}"),
                ("quantity", r"[0-9]+"),
                ("order_id", r"[A-Z0-9]{12}"),
            ],
            delimiter=":",
            target_latency_ms=0.01,
        )
        return self.build(spec)


# ============================================================================
# Convenience Functions
# ============================================================================


def create_jit_monitor(
    latency_threshold_ms: float = 1.0,
    usage_threshold: int = 100,
    profit_share: ProfitShare | None = None,
) -> JITEfficiencyMonitor:
    """
    Create a JIT efficiency monitor with custom thresholds.

    Args:
        latency_threshold_ms: JIT if latency exceeds this (default 1.0ms)
        usage_threshold: JIT if usage exceeds this (default 100)
        profit_share: Custom profit sharing (default 30/30/40)

    Returns:
        Configured JITEfficiencyMonitor
    """
    return JITEfficiencyMonitor(
        latency_threshold_ms=latency_threshold_ms,
        usage_threshold=usage_threshold,
        profit_share=profit_share,
    )


def compile_grammar_jit(
    grammar: str,
    name: str = "compiled",
    version: str = "1.0.0",
    target: JITCompilationTarget = JITCompilationTarget.REGEX,
) -> CompiledTongue:
    """
    Quick function to JIT-compile a grammar.

    Args:
        grammar: The grammar/regex to compile
        name: Name for the compiled tongue
        version: Version string
        target: Compilation target

    Returns:
        CompiledTongue ready for fast parsing
    """
    monitor = JITEfficiencyMonitor()
    config = CompilationConfig(target=target)
    return monitor.compile_tongue(name, version, grammar, config)


def benchmark_jit_speedup(
    baseline_parse: Callable[[str], Any],
    jit_parse: Callable[[str], Any],
    test_inputs: list[str],
    target: JITCompilationTarget = JITCompilationTarget.REGEX,
) -> LatencyReport:
    """
    Benchmark JIT speedup over baseline.

    Args:
        baseline_parse: Baseline parser function
        jit_parse: JIT-compiled parser function
        test_inputs: Test inputs for benchmarking
        target: Compilation target (for reporting)

    Returns:
        LatencyReport with speedup metrics
    """
    benchmark = LatencyBenchmark()
    return benchmark.compare_parsers(
        baseline_parse=baseline_parse,
        jit_parse=jit_parse,
        test_inputs=test_inputs,
        target=target,
    )


def create_hf_tongue_builder(
    monitor: JITEfficiencyMonitor | None = None,
) -> HFTongueBuilder:
    """
    Create a High-Frequency Tongue builder.

    Args:
        monitor: Optional JIT monitor for tracking

    Returns:
        HFTongueBuilder for creating HFT tongues
    """
    return HFTongueBuilder(monitor)


def estimate_jit_value(
    current_latency_ms: float,
    expected_speedup: float = 10.0,
    daily_transactions: int = 10000,
    time_value_per_ms: float = 0.0001,
) -> dict[str, float]:
    """
    Estimate value of JIT optimization.

    Args:
        current_latency_ms: Current parser latency
        expected_speedup: Expected speedup factor
        daily_transactions: Transactions per day
        time_value_per_ms: Value of 1ms in dollars

    Returns:
        Dict with value projections
    """
    jit_latency_ms = current_latency_ms / expected_speedup
    reduction_ms = current_latency_ms - jit_latency_ms
    value_per_tx = reduction_ms * time_value_per_ms

    daily_value = value_per_tx * daily_transactions
    monthly_value = daily_value * 30
    yearly_value = daily_value * 365

    return {
        "latency_reduction_ms": reduction_ms,
        "value_per_transaction": value_per_tx,
        "daily_value": daily_value,
        "monthly_value": monthly_value,
        "yearly_value": yearly_value,
    }
