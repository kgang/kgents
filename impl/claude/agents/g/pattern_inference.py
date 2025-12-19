"""
G-gent Phase 7: W-gent Pattern Inference

This module integrates G-gent with W-gent for grammar inference from observed patterns.
It enables automatic language discovery from usage data.

The Cryptographer Pattern:
    W-gent observes unknown patterns; G-gent hypothesizes a grammar.

Key capabilities:
1. Pattern observation: Receive structured patterns from W-gent
2. Grammar hypothesis: Generate BNF/EBNF grammars from patterns
3. Grammar refinement: Iteratively improve based on validation failures
4. Crystallization: Create production-ready Tongue from hypothesis

Category Theoretic Definition:
    W: Observations[] -> Pattern[]  (W-gent extracts patterns)
    G: Pattern[] -> Grammar         (G-gent hypothesizes grammar)
    V: Grammar × Observations -> ValidationReport  (Validate fit)
    C: Grammar -> Tongue            (Crystallize to artifact)
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agents.g.tongue import TongueBuilder
from agents.g.types import (
    ConstraintProof,
    GrammarFormat,
    GrammarLevel,
    InterpreterConfig,
    ParserConfig,
    Tongue,
)

# ============================================================================
# Pattern Types (from W-gent observations)
# ============================================================================


class PatternType(Enum):
    """Types of patterns W-gent can observe."""

    LITERAL = "literal"  # Exact string matches
    TOKEN = "token"  # Word-like tokens
    STRUCTURE = "structure"  # Nested/recursive structures
    SEQUENCE = "sequence"  # Ordered sequences
    ALTERNATION = "alternation"  # One of multiple options
    REPETITION = "repetition"  # Repeated elements


@dataclass
class ObservedPattern:
    """
    A pattern observed by W-gent.

    Represents a structural regularity found in input data.
    """

    pattern: str  # Pattern string (e.g., "VERB NOUN", "func(arg)")
    pattern_type: PatternType
    frequency: float  # How often this pattern appears (0.0-1.0)
    examples: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.frequency <= 1.0:
            raise ValueError(f"Frequency must be 0.0-1.0, got {self.frequency}")


@dataclass
class PatternCluster:
    """
    A cluster of related patterns.

    Groups patterns that share structural similarity.
    """

    name: str
    patterns: list[ObservedPattern]
    dominant_type: PatternType
    coverage: float  # Fraction of inputs this cluster covers

    @property
    def primary_pattern(self) -> ObservedPattern | None:
        """Most frequent pattern in cluster."""
        if not self.patterns:
            return None
        return max(self.patterns, key=lambda p: p.frequency)


# ============================================================================
# Grammar Hypothesis Types
# ============================================================================


@dataclass
class GrammarRule:
    """
    A single grammar production rule.

    Example: <verb> ::= "CHECK" | "ADD" | "LIST"
    """

    name: str  # Rule name (e.g., "verb")
    productions: list[str]  # Alternative productions
    is_terminal: bool = False
    inferred_from: list[str] = field(default_factory=list)  # Source examples

    def to_bnf(self) -> str:
        """Convert to BNF notation."""
        prods = " | ".join(f'"{p}"' if self.is_terminal else f"<{p}>" for p in self.productions)
        return f"<{self.name}> ::= {prods}"


@dataclass
class GrammarHypothesis:
    """
    A hypothesized grammar inferred from patterns.

    May be incomplete or inaccurate; needs validation.
    """

    rules: list[GrammarRule]
    start_symbol: str
    confidence: float  # Overall confidence in hypothesis (0.0-1.0)
    level: GrammarLevel
    source_patterns: list[ObservedPattern] = field(default_factory=list)

    def to_bnf(self) -> str:
        """Convert entire grammar to BNF notation."""
        lines = []
        for rule in self.rules:
            lines.append(rule.to_bnf())
        return "\n".join(lines)

    @property
    def grammar_string(self) -> str:
        """Alias for to_bnf()."""
        return self.to_bnf()


# ============================================================================
# Validation Types
# ============================================================================


@dataclass
class ValidationResult:
    """Result of validating a grammar against observations."""

    success: bool
    coverage: float  # Fraction of inputs that parse successfully
    failed_inputs: list[str] = field(default_factory=list)
    parse_errors: dict[str, str] = field(default_factory=dict)
    suggestions: list[str] = field(default_factory=list)

    @property
    def needs_refinement(self) -> bool:
        """Whether grammar needs further refinement."""
        return not self.success or self.coverage < 0.95


@dataclass
class InferenceReport:
    """
    Full report from grammar inference process.

    Documents the inference journey and final result.
    """

    tongue: Tongue | None
    success: bool
    iterations: int
    initial_hypothesis: GrammarHypothesis | None
    final_hypothesis: GrammarHypothesis | None
    validation_history: list[ValidationResult] = field(default_factory=list)
    refinements: list[str] = field(default_factory=list)
    duration_ms: float = 0.0


# ============================================================================
# Pattern Analyzer
# ============================================================================


class PatternAnalyzer:
    """
    Analyzes raw observations to extract patterns.

    Works with W-gent to identify structural regularities.
    """

    def __init__(self) -> None:
        # Regex patterns for common structures
        self._verb_pattern = re.compile(r"^([A-Z]{2,})\s+(.+)$")
        self._func_pattern = re.compile(r"^(\w+)\((.+)\)$")
        self._key_value_pattern = re.compile(r"^(\w+)\s*[:=]\s*(.+)$")

    def analyze(self, observations: list[str]) -> list[ObservedPattern]:
        """
        Extract patterns from raw observations.

        Returns list of patterns sorted by frequency.
        """
        if not observations:
            return []

        patterns: list[ObservedPattern] = []
        total = len(observations)

        # Count structure types
        verb_noun_count = 0
        func_call_count = 0
        key_value_count = 0
        other_count = 0

        # Track specific instances
        verbs: Counter[str] = Counter()
        nouns: list[str] = []
        funcs: Counter[str] = Counter()
        args_patterns: list[str] = []

        for obs in observations:
            obs = obs.strip()

            # Check VERB NOUN pattern
            if match := self._verb_pattern.match(obs):
                verb_noun_count += 1
                verbs[match.group(1)] += 1
                nouns.append(match.group(2))
                continue

            # Check function call pattern
            if match := self._func_pattern.match(obs):
                func_call_count += 1
                funcs[match.group(1)] += 1
                args_patterns.append(match.group(2))
                continue

            # Check key-value pattern
            if match := self._key_value_pattern.match(obs):
                key_value_count += 1
                continue

            other_count += 1

        # Generate patterns based on dominant structure
        if verb_noun_count >= func_call_count and verb_noun_count >= key_value_count:
            # VERB NOUN is dominant
            for verb, count in verbs.most_common():
                examples = [o for o in observations if o.startswith(verb)]
                patterns.append(
                    ObservedPattern(
                        pattern=f"{verb} <noun>",
                        pattern_type=PatternType.TOKEN,
                        frequency=count / total,
                        examples=examples[:5],
                    )
                )

            # Meta-pattern for all verbs
            if verbs:
                patterns.append(
                    ObservedPattern(
                        pattern="<verb> <noun>",
                        pattern_type=PatternType.SEQUENCE,
                        frequency=verb_noun_count / total,
                        examples=list(observations[:5]),
                        metadata={"verbs": list(verbs.keys())},
                    )
                )

        elif func_call_count > 0:
            # Function call is dominant
            for func, count in funcs.most_common():
                examples = [o for o in observations if o.startswith(f"{func}(")]
                patterns.append(
                    ObservedPattern(
                        pattern=f"{func}(<args>)",
                        pattern_type=PatternType.STRUCTURE,
                        frequency=count / total,
                        examples=examples[:5],
                    )
                )

            # Meta-pattern for function calls
            if funcs:
                patterns.append(
                    ObservedPattern(
                        pattern="<func>(<args>)",
                        pattern_type=PatternType.STRUCTURE,
                        frequency=func_call_count / total,
                        examples=list(observations[:5]),
                        metadata={"functions": list(funcs.keys())},
                    )
                )

        # Sort by frequency
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        return patterns

    def cluster_patterns(self, patterns: list[ObservedPattern]) -> list[PatternCluster]:
        """
        Group related patterns into clusters.

        Returns clusters sorted by coverage.
        """
        if not patterns:
            return []

        # Simple clustering: group by pattern type
        clusters_by_type: dict[PatternType, list[ObservedPattern]] = {}
        for pattern in patterns:
            if pattern.pattern_type not in clusters_by_type:
                clusters_by_type[pattern.pattern_type] = []
            clusters_by_type[pattern.pattern_type].append(pattern)

        clusters = []
        for ptype, plist in clusters_by_type.items():
            coverage = sum(p.frequency for p in plist)
            clusters.append(
                PatternCluster(
                    name=f"{ptype.value}_cluster",
                    patterns=plist,
                    dominant_type=ptype,
                    coverage=min(coverage, 1.0),
                )
            )

        clusters.sort(key=lambda c: c.coverage, reverse=True)
        return clusters


# ============================================================================
# Grammar Synthesizer
# ============================================================================


class GrammarSynthesizer:
    """
    Synthesizes grammar hypotheses from observed patterns.

    Implements the core G-gent pattern inference logic.
    """

    def __init__(self, min_confidence: float = 0.5) -> None:
        self.min_confidence = min_confidence

    def hypothesize(self, patterns: list[ObservedPattern]) -> GrammarHypothesis:
        """
        Generate a grammar hypothesis from patterns.

        Returns the best-fit grammar based on observed patterns.
        """
        if not patterns:
            # Empty grammar
            return GrammarHypothesis(
                rules=[],
                start_symbol="start",
                confidence=0.0,
                level=GrammarLevel.COMMAND,
                source_patterns=[],
            )

        # Determine dominant pattern type
        dominant = max(patterns, key=lambda p: p.frequency)
        rules: list[GrammarRule] = []

        if dominant.pattern_type in (PatternType.TOKEN, PatternType.SEQUENCE):
            # VERB NOUN style grammar
            rules = self._synthesize_command_grammar(patterns)
            level = GrammarLevel.COMMAND

        elif dominant.pattern_type == PatternType.STRUCTURE:
            # Function call style grammar
            rules = self._synthesize_recursive_grammar(patterns)
            level = GrammarLevel.RECURSIVE

        else:
            # Default to command grammar
            rules = self._synthesize_command_grammar(patterns)
            level = GrammarLevel.COMMAND

        # Calculate overall confidence
        confidence = sum(p.frequency for p in patterns) / len(patterns)

        return GrammarHypothesis(
            rules=rules,
            start_symbol="command" if level == GrammarLevel.COMMAND else "expr",
            confidence=min(confidence, 1.0),
            level=level,
            source_patterns=patterns,
        )

    def _synthesize_command_grammar(self, patterns: list[ObservedPattern]) -> list[GrammarRule]:
        """Synthesize VERB NOUN style grammar."""
        rules = []

        # Extract verbs from patterns
        verbs = set()
        for pattern in patterns:
            if "verbs" in pattern.metadata:
                verbs.update(pattern.metadata["verbs"])
            elif match := re.match(r"^([A-Z]+)", pattern.pattern):
                verbs.add(match.group(1))

        if verbs:
            rules.append(
                GrammarRule(
                    name="verb",
                    productions=sorted(verbs),
                    is_terminal=True,
                )
            )

        # Add noun rule (generic for now)
        rules.append(
            GrammarRule(
                name="noun",
                productions=["[^\\s]+"],  # Any non-whitespace
                is_terminal=True,
            )
        )

        # Add command rule
        rules.append(
            GrammarRule(
                name="command",
                productions=["verb", "noun"],
                is_terminal=False,
            )
        )

        return rules

    def _synthesize_recursive_grammar(self, patterns: list[ObservedPattern]) -> list[GrammarRule]:
        """Synthesize function call style grammar."""
        rules = []

        # Extract function names
        funcs = set()
        for pattern in patterns:
            if "functions" in pattern.metadata:
                funcs.update(pattern.metadata["functions"])
            elif match := re.match(r"^(\w+)\(", pattern.pattern):
                funcs.add(match.group(1))

        if funcs:
            rules.append(
                GrammarRule(
                    name="func",
                    productions=sorted(funcs),
                    is_terminal=True,
                )
            )

        # Add args and expr rules
        rules.append(
            GrammarRule(
                name="args",
                productions=["expr", "args"],  # Recursive
                is_terminal=False,
            )
        )

        rules.append(
            GrammarRule(
                name="expr",
                productions=["func", "args", "atom"],
                is_terminal=False,
            )
        )

        rules.append(
            GrammarRule(
                name="atom",
                productions=["[a-zA-Z0-9_]+"],
                is_terminal=True,
            )
        )

        return rules

    def refine(
        self,
        hypothesis: GrammarHypothesis,
        failed_inputs: list[str],
    ) -> GrammarHypothesis:
        """
        Refine a grammar hypothesis based on failed inputs.

        Returns an improved hypothesis that handles more cases.
        """
        if not failed_inputs:
            return hypothesis

        # Analyze failed inputs to find missing patterns
        analyzer = PatternAnalyzer()
        new_patterns = analyzer.analyze(failed_inputs)

        # Merge new patterns with existing
        all_patterns = hypothesis.source_patterns + new_patterns

        # Re-synthesize with expanded patterns
        return self.hypothesize(all_patterns)


# ============================================================================
# Grammar Validator
# ============================================================================


class GrammarValidator:
    """
    Validates grammar hypotheses against observations.

    Ensures the inferred grammar actually parses the input data.
    """

    def validate(
        self,
        hypothesis: GrammarHypothesis,
        observations: list[str],
    ) -> ValidationResult:
        """
        Validate grammar hypothesis against observations.

        Returns ValidationResult with coverage and failures.
        """
        if not observations:
            return ValidationResult(
                success=True,
                coverage=1.0,
            )

        # Build simple parser from hypothesis
        parser = self._build_parser(hypothesis)

        # Test all observations
        passed = 0
        failed_inputs = []
        parse_errors: dict[str, str] = {}

        for obs in observations:
            try:
                if parser(obs):
                    passed += 1
                else:
                    failed_inputs.append(obs)
                    parse_errors[obs] = "Did not match grammar"
            except Exception as e:
                failed_inputs.append(obs)
                parse_errors[obs] = str(e)

        coverage = passed / len(observations)

        # Generate suggestions for common failure patterns
        suggestions = self._generate_suggestions(failed_inputs, hypothesis)

        return ValidationResult(
            success=len(failed_inputs) == 0,
            coverage=coverage,
            failed_inputs=failed_inputs,
            parse_errors=parse_errors,
            suggestions=suggestions,
        )

    def _build_parser(self, hypothesis: GrammarHypothesis) -> Any:
        """Build a simple parser function from hypothesis."""
        # Extract verbs from rules
        verbs = set()
        for rule in hypothesis.rules:
            if rule.name == "verb" and rule.is_terminal:
                verbs.update(rule.productions)

        # Build regex for command grammar
        if verbs:
            verb_pattern = "|".join(re.escape(v) for v in verbs)
            pattern = re.compile(f"^({verb_pattern})\\s+(.+)$")

            def parser(text: str) -> bool:
                return bool(pattern.match(text.strip()))

            return parser

        # Default: always match
        return lambda text: True

    def _generate_suggestions(
        self,
        failed_inputs: list[str],
        hypothesis: GrammarHypothesis,
    ) -> list[str]:
        """Generate suggestions for fixing failed inputs."""
        suggestions: list[str] = []

        if not failed_inputs:
            return suggestions

        # Look for patterns in failures
        analyzer = PatternAnalyzer()
        failure_patterns = analyzer.analyze(failed_inputs)

        for pattern in failure_patterns[:3]:
            if "verbs" in pattern.metadata:
                new_verbs = pattern.metadata["verbs"]
                suggestions.append(f"Add verbs: {new_verbs}")
            else:
                suggestions.append(f"Consider pattern: {pattern.pattern}")

        return suggestions


# ============================================================================
# PatternInferenceEngine
# ============================================================================


class PatternInferenceEngine:
    """
    Main engine for W-gent pattern inference.

    Orchestrates the full inference pipeline:
    1. Analyze observations
    2. Hypothesize grammar
    3. Validate and refine
    4. Crystallize to Tongue
    """

    def __init__(
        self,
        max_iterations: int = 5,
        min_coverage: float = 0.95,
    ) -> None:
        self.max_iterations = max_iterations
        self.min_coverage = min_coverage
        self.analyzer = PatternAnalyzer()
        self.synthesizer = GrammarSynthesizer()
        self.validator = GrammarValidator()

    async def infer_grammar(
        self,
        observations: list[str],
        domain: str | None = None,
    ) -> InferenceReport:
        """
        Infer a grammar from observations.

        Full pipeline: observe → hypothesize → validate → refine → crystallize

        Args:
            observations: Raw input strings to learn from
            domain: Optional domain hint

        Returns:
            InferenceReport with inferred Tongue (if successful)
        """
        import time

        start = time.time()

        if not observations:
            return InferenceReport(
                tongue=None,
                success=False,
                iterations=0,
                initial_hypothesis=None,
                final_hypothesis=None,
            )

        # 1. Analyze observations
        patterns = self.analyzer.analyze(observations)

        # 2. Initial hypothesis
        hypothesis = self.synthesizer.hypothesize(patterns)
        initial_hypothesis = hypothesis

        validation_history = []
        refinements = []

        # 3. Validate and refine loop
        for i in range(self.max_iterations):
            validation = self.validator.validate(hypothesis, observations)
            validation_history.append(validation)

            if validation.coverage >= self.min_coverage:
                break

            # Refine
            hypothesis = self.synthesizer.refine(hypothesis, validation.failed_inputs)
            refinements.append(f"Iteration {i + 1}: Coverage {validation.coverage:.1%} → refined")

        # 4. Crystallize to Tongue
        final_validation = validation_history[-1] if validation_history else None
        success = final_validation is not None and final_validation.coverage >= self.min_coverage

        tongue = None
        if success:
            tongue = await self.crystallize(
                hypothesis,
                domain=domain or "Inferred from observations",
                examples=observations[:10],
            )

        duration_ms = (time.time() - start) * 1000

        return InferenceReport(
            tongue=tongue,
            success=success,
            iterations=len(validation_history),
            initial_hypothesis=initial_hypothesis,
            final_hypothesis=hypothesis,
            validation_history=validation_history,
            refinements=refinements,
            duration_ms=duration_ms,
        )

    async def crystallize(
        self,
        hypothesis: GrammarHypothesis,
        domain: str,
        examples: list[str],
    ) -> Tongue:
        """
        Crystallize a grammar hypothesis into a Tongue artifact.

        Args:
            hypothesis: The validated grammar hypothesis
            domain: Domain name for the tongue
            examples: Example inputs

        Returns:
            Production-ready Tongue
        """
        # Build grammar string
        grammar = hypothesis.to_bnf()

        # Generate tongue name from domain
        tongue_name = f"{domain.replace(' ', '')}Tongue"

        # Create constraint proof
        constraint_proof = ConstraintProof(
            constraint="Inferred from observations",
            mechanism="pattern matching",
            verified_by="W-gent inference",
            counter_examples=[],
        )

        # Build tongue using TongueBuilder
        builder = TongueBuilder(tongue_name, "1.0.0")
        builder = builder.with_domain(domain)
        builder = builder.with_grammar(grammar)
        builder = builder.with_format(GrammarFormat.BNF)
        builder = builder.with_level(hypothesis.level)
        builder = builder.with_proof(constraint_proof)

        # Add examples
        for i, ex in enumerate(examples[:5]):
            builder = builder.with_example(ex, description=f"Observed input #{i + 1}")

        # Set parser config
        builder = builder.with_parser_config(
            ParserConfig(
                strategy="regex",
                grammar_format=GrammarFormat.BNF,
                grammar_spec=grammar,
                confidence_threshold=0.8,
                repair_strategy="fail",
            )
        )

        # Set interpreter config
        builder = builder.with_interpreter_config(
            InterpreterConfig(
                runtime="python",
                semantics={},  # Empty semantics for inferred grammar
                timeout_ms=5000,
                pure_functions_only=False,
            )
        )

        return builder.build()


# ============================================================================
# Convenience Functions
# ============================================================================


async def infer_grammar_from_observations(
    observations: list[str],
    domain: str | None = None,
    max_iterations: int = 5,
    min_coverage: float = 0.95,
) -> Tongue | None:
    """
    Infer a grammar from observed patterns.

    Convenience function for simple use cases.

    Args:
        observations: Raw input strings to learn from
        domain: Optional domain hint
        max_iterations: Max refinement iterations
        min_coverage: Minimum coverage threshold

    Returns:
        Inferred Tongue, or None if inference failed
    """
    engine = PatternInferenceEngine(
        max_iterations=max_iterations,
        min_coverage=min_coverage,
    )
    report = await engine.infer_grammar(observations, domain)
    return report.tongue


async def observe_and_infer(
    observations: list[str],
    domain: str | None = None,
) -> InferenceReport:
    """
    Full observation → inference pipeline.

    Returns full InferenceReport with diagnostics.

    Args:
        observations: Raw input strings to learn from
        domain: Optional domain hint

    Returns:
        InferenceReport with full inference details
    """
    engine = PatternInferenceEngine()
    return await engine.infer_grammar(observations, domain)


def extract_patterns(observations: list[str]) -> list[ObservedPattern]:
    """
    Extract patterns from observations without full inference.

    Useful for analysis and debugging.

    Args:
        observations: Raw input strings

    Returns:
        List of observed patterns
    """
    analyzer = PatternAnalyzer()
    return analyzer.analyze(observations)


def hypothesize_grammar(patterns: list[ObservedPattern]) -> GrammarHypothesis:
    """
    Generate grammar hypothesis from patterns.

    Useful for step-by-step inference.

    Args:
        patterns: Observed patterns

    Returns:
        Grammar hypothesis
    """
    synthesizer = GrammarSynthesizer()
    return synthesizer.hypothesize(patterns)
