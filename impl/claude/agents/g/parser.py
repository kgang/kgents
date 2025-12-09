"""
G-gent Phase 3: Simplified P-gent Parser Integration

This module provides simplified parsing capabilities for G-gent Tongues.
This is NOT the full P-gent implementation - it's a focused subset to enable
G-gent Phase 3 (parse → execute → render pipeline).

Full P-gent will be implemented later as a separate genus with the complete
Prevention → Correction → Novel spectrum from spec/p-gents/README.md.
"""

from __future__ import annotations

import re
from dataclasses import field
from typing import Any

try:
    from lark import Lark, Tree

    HAS_LARK = True
except ImportError:
    HAS_LARK = False

try:
    from pydantic import BaseModel, ValidationError

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

from agents.g.types import ParseResult, ParserConfig, GrammarFormat


# ============================================================================
# Parser Strategy Protocol
# ============================================================================


class ParserStrategy:
    """Base class for parsing strategies."""

    def parse(self, text: str, config: ParserConfig) -> ParseResult[Any]:
        """
        Parse text according to configuration.

        Returns ParseResult with:
        - success: bool
        - value: parsed AST/structure (if successful)
        - confidence: 0.0-1.0
        - error: error message (if failed)
        - repairs: list of repairs applied
        """
        raise NotImplementedError


# ============================================================================
# Strategy 1: Pydantic Schema Parsing
# ============================================================================


class PydanticParser(ParserStrategy):
    """
    Parse text as Python code that instantiates a Pydantic model.

    Grammar should be Pydantic model definition as string.
    Text should be Python code that creates an instance.
    """

    def parse(self, text: str, config: ParserConfig) -> ParseResult[Any]:
        if not HAS_PYDANTIC:
            return ParseResult(
                success=False, error="Pydantic not installed (pip install pydantic)"
            )

        grammar = config.grammar_spec

        try:
            # Execute grammar to get model class
            local_scope: dict[str, Any] = {}
            exec(grammar, {"BaseModel": BaseModel, "Field": field}, local_scope)

            # Find the model class (not BaseModel itself)
            model_class = None
            for value in local_scope.values():
                if (
                    isinstance(value, type)
                    and issubclass(value, BaseModel)
                    and value is not BaseModel
                ):
                    model_class = value
                    break

            if model_class is None:
                return ParseResult(
                    success=False, error="No Pydantic model found in grammar"
                )

            # Parse text as Python code or JSON
            import json

            cleaned_text = text.strip()

            # Try to parse as JSON first (most common case)
            try:
                data = json.loads(cleaned_text)
                result = model_class(**data)
            except json.JSONDecodeError:
                # Try to eval as Python code
                try:
                    result = eval(
                        cleaned_text,
                        {"BaseModel": BaseModel, model_class.__name__: model_class},
                        local_scope,
                    )
                except (SyntaxError, NameError) as e:
                    # Try wrapping in model class name
                    try:
                        result = eval(
                            f"{model_class.__name__}({cleaned_text})",
                            {"BaseModel": BaseModel, model_class.__name__: model_class},
                            local_scope,
                        )
                    except Exception:
                        return ParseResult(
                            success=False, error=f"Failed to parse as Pydantic: {e}"
                        )

            # Validate
            if not isinstance(result, model_class):
                return ParseResult(
                    success=False,
                    error=f"Result is not instance of {model_class.__name__}",
                )

            return ParseResult(
                success=True,
                ast=result.model_dump(),
                confidence=config.confidence_threshold,
            )

        except ValidationError as e:
            return ParseResult(
                success=False, error=f"Pydantic validation failed: {e}", confidence=0.0
            )
        except Exception as e:
            return ParseResult(
                success=False, error=f"Pydantic parsing error: {e}", confidence=0.0
            )


# ============================================================================
# Strategy 2: BNF Command Parsing (Regex-based)
# ============================================================================


class BNFCommandParser(ParserStrategy):
    """
    Parse verb-noun commands using regex patterns derived from BNF.

    Grammar format: BNF with simple verb-noun structure
    Example: <command> ::= <verb> <noun>
    """

    def parse(self, text: str, config: ParserConfig) -> ParseResult[Any]:
        grammar = config.grammar_spec

        # Extract verbs from grammar
        verbs = self._extract_verbs(grammar)

        if not verbs:
            return ParseResult(success=False, error="No verbs found in BNF grammar")

        # Try to match verb-noun pattern
        cleaned = text.strip()
        verb_pattern = "|".join(re.escape(v) for v in verbs)
        pattern = rf"^({verb_pattern})\s+(.+)$"

        match = re.match(pattern, cleaned, re.IGNORECASE)

        if match:
            verb, noun = match.groups()
            return ParseResult(
                success=True,
                ast={"verb": verb.upper(), "noun": noun.strip()},
                confidence=config.confidence_threshold,
            )

        # Try just verb (no noun)
        if cleaned.upper() in verbs:
            return ParseResult(
                success=True,
                ast={"verb": cleaned.upper(), "noun": None},
                confidence=config.confidence_threshold * 0.9,
            )

        return ParseResult(
            success=False,
            error=f"No valid command found. Expected verb from {verbs}",
            confidence=0.0,
        )

    def _extract_verbs(self, grammar: str) -> list[str]:
        """Extract verb tokens from BNF grammar."""
        # Simple extraction: look for quoted strings or UPPERCASE tokens
        verbs = []

        # Pattern 1: "VERB"
        quoted = re.findall(r'"([A-Z]+)"', grammar)
        verbs.extend(quoted)

        # Pattern 2: VERB (unquoted uppercase)
        unquoted = re.findall(r"\b([A-Z]{2,})\b", grammar)
        verbs.extend(unquoted)

        return sorted(set(verbs))


# ============================================================================
# Strategy 3: Lark Recursive Parsing
# ============================================================================


class LarkRecursiveParser(ParserStrategy):
    """
    Parse S-expressions or recursive structures using Lark parser.

    Grammar: Lark EBNF format
    """

    def parse(self, text: str, config: ParserConfig) -> ParseResult[Any]:
        if not HAS_LARK:
            return ParseResult(
                success=False, error="Lark not installed (pip install lark)"
            )

        grammar = config.grammar_spec

        try:
            # Create Lark parser
            parser = Lark(grammar, start="start")

            # Parse text
            tree = parser.parse(text)

            # Convert to dict
            result = self._tree_to_dict(tree)

            return ParseResult(
                success=True,
                ast=result,
                confidence=config.confidence_threshold,
            )

        except Exception as e:
            return ParseResult(
                success=False, error=f"Lark parsing failed: {e}", confidence=0.0
            )

    def _tree_to_dict(self, tree: Any) -> dict[str, Any]:
        """Convert Lark tree to dict representation."""
        if not isinstance(tree, Tree):
            return str(tree)

        return {
            "type": tree.data,
            "children": [self._tree_to_dict(child) for child in tree.children],
        }


# ============================================================================
# Master Parser Factory
# ============================================================================


def create_parser(config: ParserConfig) -> ParserStrategy:
    """
    Create appropriate parser strategy based on configuration.

    Maps GrammarFormat to parser implementation:
    - PYDANTIC → PydanticParser
    - BNF/EBNF → BNFCommandParser (if simple) or LarkRecursiveParser (if complex)
    - LARK → LarkRecursiveParser
    """
    strategy_map = {
        GrammarFormat.PYDANTIC: PydanticParser,
        GrammarFormat.BNF: BNFCommandParser,
        GrammarFormat.EBNF: LarkRecursiveParser,
        GrammarFormat.LARK: LarkRecursiveParser,
    }

    # Map by format
    parser_class = strategy_map.get(config.format, BNFCommandParser)

    return parser_class()


# ============================================================================
# High-level API
# ============================================================================


def parse_with_tongue(text: str, config: ParserConfig) -> ParseResult[Any]:
    """
    Parse text using Tongue's parser configuration.

    This is the main entry point for G-gent Phase 3 parsing.

    Args:
        text: Input text to parse
        config: Parser configuration from Tongue

    Returns:
        ParseResult with success, value, confidence, errors
    """
    parser = create_parser(config)
    return parser.parse(text, config)
