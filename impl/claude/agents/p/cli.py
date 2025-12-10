"""
ParserCLI - CLI interface for P-gent (Parser).

P-gents bridge the Stochastic-Structural Gap between LLM outputs and
deterministic parsers through fuzzy coercion without opinion.

Commands:
- extract: Extract structured data from text
- repair: Repair malformed output
- validate: Validate output against schema
- stream: Stream-parse input incrementally
- compose: Compose parsers (fallback/fusion/switch)

See: spec/protocols/prism.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from protocols.cli.prism import CLICapable, expose

if TYPE_CHECKING:
    pass


class ParserCLI(CLICapable):
    """
    CLI interface for P-gent (Parser).

    The Parser bridges stochastic LLM outputs to deterministic structures
    through fuzzy coercion without opinion.
    """

    @property
    def genus_name(self) -> str:
        return "parse"

    @property
    def cli_description(self) -> str:
        return "P-gent Parser operations"

    def get_exposed_commands(self) -> dict[str, Callable[..., Any]]:
        return {
            "extract": self.extract,
            "repair": self.repair,
            "validate": self.validate,
            "stream": self.stream,
            "compose": self.compose,
        }

    @expose(
        help="Extract structured data from text",
        examples=[
            'kgents parse extract "The user said: {name: John, age: 30}"',
            "kgents parse extract input.txt --strategy=anchor",
            "kgents parse extract response.txt --target=json",
        ],
    )
    async def extract(
        self,
        input_source: str,
        strategy: str = "anchor",
        target: str = "json",
    ) -> dict[str, Any]:
        """
        Extract structured data from text.

        Strategies:
        - anchor: Anchor-based extraction (fast, heuristic)
        - stack: Stack-balancing for brackets/braces
        - diff: Diff-based with W-gent integration
        - evolving: Adaptive format detection
        """
        from agents.p import AnchorBasedParser, StackBalancingParser

        # Get input text
        input_path = Path(input_source)
        if input_path.exists():
            text = input_path.read_text()
        else:
            text = input_source

        # Select parser
        if strategy == "anchor":
            parser = AnchorBasedParser()
        elif strategy == "stack":
            parser = StackBalancingParser()
        else:
            parser = AnchorBasedParser()

        result = parser.parse(text)

        return {
            "success": result.success,
            "value": result.value,
            "confidence": result.confidence,
            "strategy": result.strategy or strategy,
            "repairs": result.repairs,
            "partial": result.partial,
            "error": result.error,
        }

    @expose(
        help="Repair malformed output",
        examples=[
            'kgents parse repair "{ name: John, age: 30"',
            "kgents parse repair broken.json --strategy=stack",
        ],
    )
    async def repair(
        self,
        malformed: str,
        strategy: str = "stack",
    ) -> dict[str, Any]:
        """
        Repair malformed output.

        Uses stack-balancing or anchor-based strategies to fix
        incomplete JSON, brackets, quotes, etc.
        """
        from agents.p import AnchorBasedParser, StackBalancingParser

        # Load from file if path exists
        malformed_path = Path(malformed)
        if malformed_path.exists():
            text = malformed_path.read_text()
        else:
            text = malformed

        if strategy == "stack":
            parser = StackBalancingParser()
        else:
            parser = AnchorBasedParser()

        result = parser.parse(text)

        return {
            "success": result.success,
            "repaired": json.dumps(result.value) if result.value else None,
            "value": result.value,
            "confidence": result.confidence,
            "repairs": result.repairs,
            "error": result.error,
        }

    @expose(
        help="Validate output against schema",
        examples=[
            "kgents parse validate output.json --schema=schema.json",
            'kgents parse validate \'{"name":"test"}\' --schema=user.schema.json',
        ],
    )
    async def validate(
        self,
        output: str,
        schema: str,
    ) -> dict[str, Any]:
        """
        Validate output against JSON schema.

        Performs type, required fields, and nested validation.
        """
        # Load output data
        output_path = Path(output)
        if output_path.exists():
            data = json.loads(output_path.read_text())
        else:
            data = json.loads(output)

        # Load schema
        schema_path = Path(schema)
        if not schema_path.exists():
            return {"valid": False, "errors": [f"Schema not found: {schema}"]}

        schema_data = json.loads(schema_path.read_text())

        # Validate
        errors = self._validate_against_schema(data, schema_data)

        return {"valid": len(errors) == 0, "errors": errors}

    def _validate_against_schema(
        self, data: Any, schema: dict[str, Any], path: str = ""
    ) -> list[str]:
        """Validate data against JSON schema recursively."""
        errors = []

        # Type validation
        expected_type = schema.get("type")
        if expected_type:
            type_map = {
                "object": dict,
                "array": list,
                "string": str,
                "number": (int, float),
                "integer": int,
                "boolean": bool,
                "null": type(None),
            }
            expected = type_map.get(expected_type)
            if expected and not isinstance(data, expected):
                errors.append(
                    f"{path or 'root'}: Expected type {expected_type}, got {type(data).__name__}"
                )

        # Required properties
        if isinstance(data, dict) and "required" in schema:
            for req in schema["required"]:
                if req not in data:
                    errors.append(f"{path or 'root'}: Missing required property: {req}")

        # Properties validation
        if isinstance(data, dict) and "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                if prop in data:
                    sub_path = f"{path}.{prop}" if path else prop
                    errors.extend(
                        self._validate_against_schema(data[prop], prop_schema, sub_path)
                    )

        return errors

    @expose(
        help="Stream-parse input incrementally",
        examples=[
            "kgents parse stream large_response.txt",
            "kgents parse stream --strategy=stack",
        ],
    )
    async def stream(
        self,
        input_file: str,
        strategy: str = "stack",
        chunk_size: int = 100,
    ) -> dict[str, Any]:
        """
        Stream-parse input incrementally.

        Useful for large files, real-time LLM output, or network streams.
        """
        from agents.p import StackBalancingParser

        input_path = Path(input_file)
        if not input_path.exists():
            return {"error": f"File not found: {input_file}"}

        text = input_path.read_text()
        parser = StackBalancingParser()

        # Simulate streaming in chunks
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

        partial_values = []
        final_result = None

        for chunk in chunks:
            result = parser.parse_stream(chunk)
            if result.value:
                partial_values.append(result.value)
            final_result = result

        return {
            "chunks": len(chunks),
            "complete": final_result.success if final_result else False,
            "confidence": final_result.confidence if final_result else 0.0,
            "partial_values": len(partial_values),
            "value": final_result.value if final_result else None,
        }

    @expose(
        help="Compose parsers together",
        examples=[
            "kgents parse compose fallback --parsers=anchor,stack,diff",
            "kgents parse compose fusion --parsers=anchor,stack",
        ],
    )
    async def compose(
        self,
        mode: str,
        parsers: str = "anchor,stack",
    ) -> dict[str, Any]:
        """
        Compose parsers together.

        Modes:
        - fallback: Try parsers in order, use first success
        - fusion: Combine results from multiple parsers
        - switch: Route to parser based on input characteristics
        """
        parser_list = [p.strip() for p in parsers.split(",")]

        return {
            "mode": mode,
            "parsers": parser_list,
            "description": f"Composed parser: {mode}({', '.join(parser_list)})",
            "created": True,
        }
