"""
P-gents Composition Patterns

Parsers are morphisms Text → ParseResult[A] that compose in three ways:

1. Sequential Fallback (Chain of Responsibility)
   - Try strategies in order until one succeeds
   - Penalize confidence for fallback depth
   - Most common pattern

2. Parallel Fusion (Merge Multiple Parsers)
   - Run multiple parsers and merge results
   - Average confidence scores
   - Used when parsers extract complementary data

3. Conditional Switch (Route by Input)
   - Choose parser based on input characteristics
   - No confidence penalty
   - Used when input format is detectable
"""

from typing import Callable, Generic, Iterator, Optional, TypeVar

from agents.p.core import Parser, ParserConfig, ParseResult

A = TypeVar("A")


class FallbackParser(Generic[A]):
    """
    Try strategies in order until one succeeds (Chain of Responsibility).

    Categorical interpretation:
    - Tries parsers p1, p2, ..., pn in sequence
    - Returns first success with confidence penalty for depth
    - If all fail, returns failure with aggregated errors

    Confidence penalty:
    - Strategy 0 (first): confidence *= 1.0 (no penalty)
    - Strategy 1: confidence *= 0.9
    - Strategy 2: confidence *= 0.8
    - Strategy i: confidence *= max(0.5, 1.0 - 0.1 * i)
    """

    def __init__(self, *strategies: Parser[A], config: Optional[ParserConfig] = None):
        """
        Initialize fallback parser.

        Args:
            *strategies: Parsers to try in order
            config: Parser configuration
        """
        if not strategies:
            raise ValueError("FallbackParser requires at least one strategy")

        self.strategies = strategies
        self.config = config or ParserConfig()

    def parse(self, text: str) -> ParseResult[A]:
        """
        Try strategies in order until one succeeds.

        Args:
            text: Text to parse

        Returns:
            ParseResult[A] from first successful strategy

        Note:
            Confidence is penalized based on fallback depth.
        """
        errors = []

        for i, strategy in enumerate(self.strategies):
            result = strategy.parse(text)

            if result.success:
                # Penalize for fallback depth
                penalty = max(0.5, 1.0 - 0.1 * i)
                result.confidence *= penalty
                result.metadata["fallback_depth"] = i
                result.metadata["fallback_penalty"] = penalty
                result.strategy = f"fallback[{i}]:{result.strategy}"
                return result
            else:
                errors.append(f"Strategy {i} ({result.strategy}): {result.error}")

        # All strategies failed
        return ParseResult(
            success=False,
            error=f"All {len(self.strategies)} strategies failed:\n"
            + "\n".join(errors),
            strategy="fallback",
            metadata={"strategies_tried": len(self.strategies)},
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[A]]:
        """
        Stream parsing with fallback.

        Strategy:
        - Try first strategy that supports streaming
        - If none support streaming, buffer and parse complete
        """
        # Try first strategy that supports streaming
        for i, strategy in enumerate(self.strategies):
            if hasattr(strategy, "parse_stream"):
                for result in strategy.parse_stream(tokens):
                    # Apply fallback penalty
                    penalty = max(0.5, 1.0 - 0.1 * i)
                    result.confidence *= penalty
                    result.metadata["fallback_depth"] = i
                    result.metadata["fallback_penalty"] = penalty
                    result.strategy = f"fallback-stream[{i}]:{result.strategy}"
                    yield result
                return

        # Fallback: Buffer and parse complete
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config) -> "FallbackParser[A]":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return FallbackParser(*self.strategies, config=new_config)


class FusionParser(Generic[A]):
    """
    Run multiple parsers and merge results (Parallel Fusion).

    Requires:
    - merge_fn: Function to combine multiple successful parses

    Use cases:
    - Extract complementary data from different parsers
    - Validate consistency across parsers
    - Boost confidence when multiple parsers agree
    """

    def __init__(
        self,
        *parsers: Parser[A],
        merge_fn: Callable[[list[A]], A],
        config: Optional[ParserConfig] = None,
    ):
        """
        Initialize fusion parser.

        Args:
            *parsers: Parsers to run in parallel
            merge_fn: Function to merge successful results
            config: Parser configuration
        """
        if not parsers:
            raise ValueError("FusionParser requires at least one parser")

        self.parsers = parsers
        self.merge_fn = merge_fn
        self.config = config or ParserConfig()

    def parse(self, text: str) -> ParseResult[A]:
        """
        Run all parsers and merge successful results.

        Args:
            text: Text to parse

        Returns:
            ParseResult[A] with merged value

        Confidence:
            Average of all successful parsers' confidence scores
        """
        results = [p.parse(text) for p in self.parsers]
        successful = [r for r in results if r.success]

        if not successful:
            errors = [f"{r.strategy}: {r.error}" for r in results]
            return ParseResult(
                success=False,
                error=f"All {len(self.parsers)} parsers failed:\n" + "\n".join(errors),
                strategy="fusion",
                metadata={"parsers_total": len(self.parsers)},
            )

        # Merge successful results
        try:
            merged_value = self.merge_fn([r.value for r in successful])
        except Exception as e:
            return ParseResult(
                success=False,
                error=f"Merge function failed: {e}",
                strategy="fusion",
                metadata={
                    "parsers_succeeded": len(successful),
                    "parsers_total": len(self.parsers),
                },
            )

        # Average confidence
        avg_confidence = sum(r.confidence for r in successful) / len(successful)

        # Collect all repairs
        all_repairs = []
        for r in successful:
            all_repairs.extend(r.repairs)

        return ParseResult(
            success=True,
            value=merged_value,
            confidence=avg_confidence,
            repairs=all_repairs,
            strategy="fusion",
            metadata={
                "parsers_succeeded": len(successful),
                "parsers_total": len(self.parsers),
                "strategies": [r.strategy for r in successful],
            },
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[A]]:
        """
        Stream parsing not supported for fusion (requires complete input).

        Fallback: Buffer and parse complete.
        """
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config) -> "FusionParser[A]":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return FusionParser(*self.parsers, merge_fn=self.merge_fn, config=new_config)


class SwitchParser(Generic[A]):
    """
    Choose parser based on input characteristics (Conditional Switch).

    Strategy:
    - Define conditions as predicates: str -> bool
    - Map conditions to parsers
    - Choose first matching parser

    No confidence penalty (correct parser for input).
    """

    def __init__(
        self,
        routes: dict[Callable[[str], bool], Parser[A]],
        config: Optional[ParserConfig] = None,
    ):
        """
        Initialize switch parser.

        Args:
            routes: Mapping from condition (str -> bool) to parser
            config: Parser configuration

        Example:
            >>> routes = {
            ...     lambda t: t.startswith("{"): JsonParser(),
            ...     lambda t: "###" in t: AnchorBasedParser(),
            ...     lambda t: True: FallbackParser(...),  # Default
            ... }
            >>> parser = SwitchParser(routes)
        """
        if not routes:
            raise ValueError("SwitchParser requires at least one route")

        self.routes = routes
        self.config = config or ParserConfig()

    def parse(self, text: str) -> ParseResult[A]:
        """
        Choose parser based on input characteristics.

        Args:
            text: Text to parse

        Returns:
            ParseResult[A] from matched parser

        Note:
            No confidence penalty (correct parser for input).
        """
        for condition, parser in self.routes.items():
            try:
                if condition(text):
                    result = parser.parse(text)
                    result.metadata["switch_condition"] = condition.__name__
                    result.strategy = f"switch[{condition.__name__}]:{result.strategy}"
                    return result
            except Exception:
                # Condition evaluation failed, skip
                continue

        return ParseResult(
            success=False,
            error="No matching parser for input",
            strategy="switch",
            metadata={"routes_checked": len(self.routes)},
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[A]]:
        """
        Stream parsing for switch parser.

        Strategy:
        - Buffer initial tokens to detect format
        - Switch to appropriate parser
        - Yield results
        """
        # Buffer initial tokens for format detection
        buffer = []
        for i, token in enumerate(tokens):
            buffer.append(token)

            # Check if we can detect format (after 10 tokens or "\n")
            if i >= 10 or "\n" in token:
                text_so_far = "".join(buffer)

                # Try to match condition
                for condition, parser in self.routes.items():
                    try:
                        if condition(text_so_far):
                            # Found match, switch to this parser
                            # Reconstruct stream
                            from itertools import chain

                            stream = chain(buffer, tokens)

                            if hasattr(parser, "parse_stream"):
                                for result in parser.parse_stream(stream):
                                    result.metadata["switch_condition"] = (
                                        condition.__name__
                                    )
                                    result.strategy = f"switch[{condition.__name__}]:{result.strategy}"
                                    yield result
                            else:
                                # Fallback: buffer and parse
                                text = "".join(stream)
                                yield parser.parse(text)
                            return
                    except Exception:
                        continue

        # No match found, return error
        yield ParseResult(
            success=False,
            error="No matching parser for stream",
            strategy="switch-stream",
        )

    def configure(self, **config) -> "SwitchParser[A]":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return SwitchParser(self.routes, config=new_config)
