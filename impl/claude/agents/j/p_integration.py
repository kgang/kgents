"""
J-gents × P-gents Integration: Parse JIT agent intents and outputs

This module provides P-gent parsers specialized for J-gent (JIT agent) workflows:
- Intent parsing: Natural language → AgentIntent
- Source code parsing: Generated code → AgentSource validation
- Output schema parsing: Agent outputs → Structured data

Philosophy: J-gents produce code dynamically. P-gents ensure that code is well-formed
and type-safe before execution.
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional
from agents.p.core import ParseResult, Parser, ParserConfig
from agents.p.strategies.anchor import AnchorBasedParser
from agents.p.strategies.reflection import ReflectionParser
from agents.p.strategies.probabilistic_ast import ProbabilisticASTParser


@dataclass
class IntentParser(Parser[dict]):
    """
    Parse natural language intent into structured AgentIntent.

    Uses anchor-based extraction for robustness against conversational filler.

    Example:
        parser = IntentParser()
        result = parser.parse('''
            ###BEHAVIOR: Parse JSON logs and extract errors
            ###CONSTRAINT: Must handle malformed JSON gracefully
            ###INPUT: String (log line)
            ###OUTPUT: ErrorRecord or None
        ''')

        intent = result.value
        # {"behavior": "...", "constraint": "...", "input_type": "...", "output_type": "..."}
    """

    config: ParserConfig = ParserConfig()

    def parse(self, text: str) -> ParseResult[dict]:
        """Parse intent from text with anchors."""
        # Use anchor-based extraction for each field
        behavior_parser = AnchorBasedParser(anchor="###BEHAVIOR:")
        constraint_parser = AnchorBasedParser(anchor="###CONSTRAINT:")
        input_parser = AnchorBasedParser(anchor="###INPUT:")
        output_parser = AnchorBasedParser(anchor="###OUTPUT:")

        intent = {}
        confidence_scores = []

        # Extract behavior
        behavior_result = behavior_parser.parse(text)
        if behavior_result.success:
            intent["behavior"] = (
                behavior_result.value[0] if behavior_result.value else ""
            )
            confidence_scores.append(behavior_result.confidence)

        # Extract constraints (optional, multiple)
        constraint_result = constraint_parser.parse(text)
        if constraint_result.success:
            intent["constraints"] = constraint_result.value
            confidence_scores.append(constraint_result.confidence)
        else:
            intent["constraints"] = []

        # Extract input type
        input_result = input_parser.parse(text)
        if input_result.success:
            intent["input_type"] = (
                input_result.value[0] if input_result.value else "Any"
            )
            confidence_scores.append(input_result.confidence)
        else:
            intent["input_type"] = "Any"

        # Extract output type
        output_result = output_parser.parse(text)
        if output_result.success:
            intent["output_type"] = (
                output_result.value[0] if output_result.value else "Any"
            )
            confidence_scores.append(output_result.confidence)
        else:
            intent["output_type"] = "Any"

        if not intent.get("behavior"):
            return ParseResult[dict](
                success=False, error="No behavior specified in intent"
            )

        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.5
        )

        return ParseResult[dict](
            success=True,
            value=intent,
            confidence=avg_confidence,
            strategy="intent-anchored",
            metadata={"fields_extracted": len(intent)},
        )

    def parse_stream(self, tokens: list[str]) -> list[ParseResult[dict]]:
        """Stream parsing (buffer and parse once)."""
        text = "".join(tokens)
        return [self.parse(text)]

    def configure(self, **config_updates) -> "IntentParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return IntentParser(config=new_config)


@dataclass
class SourceCodeParser(Parser[str]):
    """
    Parse and validate generated Python source code.

    Uses probabilistic AST to detect potential issues in generated code.

    Example:
        parser = SourceCodeParser()
        result = parser.parse('''
        def process(data):
            return [x * 2 for x in data]
        ''')

        if result.confidence < 0.8:
            print("Generated code may have issues")
    """

    config: ParserConfig = ParserConfig()

    def parse(self, text: str) -> ParseResult[str]:
        """
        Parse Python source code.

        Checks:
        - Valid Python syntax (ast.parse)
        - No obvious security issues (imports, exec, eval)
        - Reasonable structure
        """
        import ast

        # Try to parse as Python AST
        try:
            tree = ast.parse(text)

            # Check for security concerns
            repairs = []
            confidence = 1.0

            for node in ast.walk(tree):
                # Flag dangerous imports
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name in ("os", "subprocess", "sys"):
                            repairs.append(f"Potentially dangerous import: {name.name}")
                            confidence *= 0.8

                # Flag exec/eval calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ("exec", "eval", "compile"):
                            repairs.append(f"Dangerous function call: {node.func.id}")
                            confidence *= 0.6

            return ParseResult[str](
                success=True,
                value=text,
                confidence=confidence,
                strategy="python-ast",
                repairs=repairs,
                metadata={
                    "node_count": len(list(ast.walk(tree))),
                    "has_functions": any(
                        isinstance(n, ast.FunctionDef) for n in ast.walk(tree)
                    ),
                },
            )

        except SyntaxError as e:
            return ParseResult[str](
                success=False, error=f"Python syntax error: {e}", strategy="python-ast"
            )

    def parse_stream(self, tokens: list[str]) -> list[ParseResult[str]]:
        """Stream parsing (buffer until valid Python)."""
        text = "".join(tokens)
        return [self.parse(text)]

    def configure(self, **config_updates) -> "SourceCodeParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return SourceCodeParser(config=new_config)


@dataclass
class AgentOutputParser(Parser[Any]):
    """
    Parse agent output into expected schema.

    Uses probabilistic AST + reflection for robust parsing with self-correction.

    Example:
        parser = AgentOutputParser()
        output = '{"result": "success", "data": [1, 2, 3]}'
        result = parser.parse(output)
    """

    config: ParserConfig = ParserConfig()
    llm_func: Optional[Callable[[str], str]] = None

    def parse(self, text: str) -> ParseResult[Any]:
        """
        Parse agent output with fallback strategies.

        Tries:
        1. Direct JSON parse (probabilistic AST)
        2. Reflection-based repair (if LLM provided)
        3. Heuristic extraction
        """
        # Try probabilistic AST first
        prob_parser = ProbabilisticASTParser(config=self.config)
        result = prob_parser.parse(text)

        if result.success and result.confidence >= self.config.min_confidence:
            # Extract the actual value from the AST node
            return ParseResult[Any](
                success=True,
                value=result.value.value
                if hasattr(result.value, "value")
                else result.value,
                confidence=result.confidence,
                strategy="probabilistic-ast",
                repairs=result.repairs,
            )

        # Try reflection if LLM available
        if self.llm_func:
            reflection_parser = ReflectionParser(
                base_parser=prob_parser, llm_func=self.llm_func, config=self.config
            )
            result = reflection_parser.parse(text)

            if result.success:
                return ParseResult[Any](
                    success=True,
                    value=result.value.value
                    if hasattr(result.value, "value")
                    else result.value,
                    confidence=result.confidence,
                    strategy="reflection",
                    repairs=result.repairs,
                )

        # Fallback: return original text with low confidence
        return ParseResult[Any](
            success=True,
            value=text,
            confidence=0.3,
            strategy="raw-text",
            repairs=["Could not parse, returning raw text"],
        )

    def parse_stream(self, tokens: list[str]) -> list[ParseResult[Any]]:
        """Stream parsing."""
        text = "".join(tokens)
        return [self.parse(text)]

    def configure(self, **config_updates) -> "AgentOutputParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return AgentOutputParser(config=new_config, llm_func=self.llm_func)


# Convenience constructors


def create_jgent_intent_parser() -> IntentParser:
    """
    Create a parser for J-gent intents.

    Example:
        parser = create_jgent_intent_parser()
        result = parser.parse(user_intent)
    """
    return IntentParser(config=ParserConfig(min_confidence=0.7, allow_partial=True))


def create_jgent_source_parser() -> SourceCodeParser:
    """
    Create a parser for J-gent generated source code.

    Example:
        parser = create_jgent_source_parser()
        result = parser.parse(generated_code)
    """
    return SourceCodeParser(
        config=ParserConfig(
            min_confidence=0.8,  # Higher bar for code
            allow_partial=False,
        )
    )


def create_jgent_output_parser(
    llm_func: Optional[Callable[[str], str]] = None,
) -> AgentOutputParser:
    """
    Create a parser for J-gent agent outputs.

    Args:
        llm_func: Optional LLM function for reflection-based repair

    Example:
        parser = create_jgent_output_parser(llm_func=my_llm.generate)
        result = parser.parse(agent_output)
    """
    return AgentOutputParser(
        config=ParserConfig(
            min_confidence=0.6,
            allow_partial=True,
            enable_reflection=llm_func is not None,
        ),
        llm_func=llm_func,
    )
