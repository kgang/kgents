"""
Structural Decoupling Parser (Strategy 2.2 / Jsonformer Approach)

The Principle: Decouple value generation (LLM's job) from structural
generation (parser's job).

Instead of asking LLM for: {"key": "value"}
1. Parser prints: {"key": "
2. LLM generates: value
3. Parser prints: "}

Benefits:
- Parser NEVER receives malformed structure (it created the structure)
- LLM can't hallucinate extra fields or wrong types
- Guaranteed schema conformance
- Cheaper LLM calls (only generate content, not structure)

Use Cases:
- W-gent HTML generation: W-gent controls tags, LLM fills content
- F-gent artifact assembly: F-gent controls .alo.md structure, LLM fills sections
- B-gent hypothesis fields: Parser controls format, LLM fills statement/reasoning
"""

from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional

from agents.p.core import ParserConfig, ParseResult


@dataclass
class StructuredField:
    """
    Field definition for structural decoupling.

    Defines:
    - Field name
    - Expected type
    - Optional prompt template for LLM
    - Optional validation function
    """

    name: str
    type: Literal["string", "number", "boolean", "array", "object"]
    prompt_template: Optional[str] = None
    validator: Optional[Callable[[Any], bool]] = None
    array_item_type: Optional[str] = None  # For arrays
    nested_schema: Optional[dict[str, "StructuredField"]] = None  # For objects


class StructuralDecouplingParser:
    """
    Parser that controls structure, delegates value generation to LLM.

    The key insight: If the parser generates the JSON structure and
    only asks the LLM to fill values, parsing can never fail.

    Protocol:
    1. Parser defines schema (fields + types)
    2. For each field:
       a. Parser generates structure: {"field_name": "
       b. LLM generates value: content
       c. Parser closes structure: "}
    3. Parser assembles final JSON (guaranteed valid)
    """

    def __init__(
        self,
        schema: dict[str, StructuredField],
        llm_generate: Callable[[str], str],
        config: Optional[ParserConfig] = None,
    ):
        """
        Initialize structural decoupling parser.

        Args:
            schema: Field definitions {field_name: StructuredField}
            llm_generate: Function that takes prompt and returns LLM response
                         Signature: (prompt: str) -> str
            config: Parser configuration
        """
        self.schema = schema
        self.llm_generate = llm_generate
        self.config = config or ParserConfig()

    def parse(self, prompt_context: str) -> ParseResult[dict]:
        """
        Parse by generating structure and filling with LLM values.

        Args:
            prompt_context: Context for LLM (what are we generating?)

        Returns:
            ParseResult[dict] with guaranteed valid structure

        Note:
            Unlike traditional parsing, this doesn't parse existing text.
            Instead, it generates structured data by:
            1. Parser controls JSON structure
            2. LLM fills in values
            3. Parser assembles final JSON
        """
        result = {}
        repairs = []
        total_confidence = 0.0

        for field_name, field_def in self.schema.items():
            try:
                # Generate prompt for this field
                if field_def.prompt_template:
                    prompt = field_def.prompt_template.format(
                        context=prompt_context,
                        field_name=field_name,
                    )
                else:
                    prompt = f"Generate a {field_def.type} value for field '{field_name}' in context: {prompt_context}"

                # LLM generates value
                raw_value = self.llm_generate(prompt)

                # Coerce to expected type (parser controls this)
                coerced_value, field_confidence = self._coerce_value(
                    raw_value,
                    field_def,
                )

                # Validate if validator provided
                if field_def.validator and not field_def.validator(coerced_value):
                    repairs.append(
                        f"Field '{field_name}' failed validation, using default"
                    )
                    coerced_value = self._get_default_value(field_def.type)
                    field_confidence *= 0.5

                result[field_name] = coerced_value
                total_confidence += field_confidence

            except Exception as e:
                # Field generation failed, use default
                repairs.append(f"Field '{field_name}' generation failed: {e}")
                result[field_name] = self._get_default_value(field_def.type)
                total_confidence += 0.3  # Low confidence for defaults

        # Calculate average confidence
        avg_confidence = total_confidence / max(len(self.schema), 1)

        return ParseResult(
            success=True,
            value=result,
            confidence=avg_confidence,
            strategy="structural-decoupling",
            repairs=repairs,
            metadata={
                "total_fields": len(self.schema),
                "generated_fields": len(result),
                "llm_calls": len(self.schema),
            },
        )

    def _coerce_value(
        self,
        raw_value: str,
        field_def: StructuredField,
    ) -> tuple[Any, float]:
        """
        Coerce LLM output to expected type.

        Args:
            raw_value: Raw LLM response
            field_def: Field definition

        Returns:
            (coerced_value, confidence)
        """
        raw_value = raw_value.strip()

        if field_def.type == "string":
            # Remove quotes if present
            value = raw_value.strip("\"'")
            return value, 0.95

        elif field_def.type == "number":
            try:
                # Try to parse as number
                if "." in raw_value or "e" in raw_value.lower():
                    value = float(raw_value)
                else:
                    value = int(raw_value)
                return value, 0.95
            except ValueError:
                # Extract first number from text
                import re

                match = re.search(r"-?\d+\.?\d*", raw_value)
                if match:
                    num_str = match.group()
                    value = float(num_str) if "." in num_str else int(num_str)
                    return value, 0.7
                else:
                    # Default to 0
                    return 0, 0.3

        elif field_def.type == "boolean":
            # Parse boolean
            lower = raw_value.lower()
            if lower in ("true", "yes", "1", "t", "y"):
                return True, 0.95
            elif lower in ("false", "no", "0", "f", "n"):
                return False, 0.95
            else:
                # Ambiguous, default to False
                return False, 0.5

        elif field_def.type == "array":
            # Try to parse as array
            import json

            try:
                # Try direct JSON parse
                value = json.loads(raw_value)
                if isinstance(value, list):
                    return value, 0.9
            except json.JSONDecodeError:
                pass

            # Fallback: split by common delimiters
            if "," in raw_value:
                items = [item.strip().strip("\"'") for item in raw_value.split(",")]
                return items, 0.7
            elif "\n" in raw_value:
                items = [
                    item.strip().strip("\"'")
                    for item in raw_value.split("\n")
                    if item.strip()
                ]
                return items, 0.7
            else:
                # Single item array
                return [raw_value], 0.6

        elif field_def.type == "object":
            # Try to parse as object
            import json

            try:
                value = json.loads(raw_value)
                if isinstance(value, dict):
                    return value, 0.9
            except json.JSONDecodeError:
                pass

            # Fallback: empty object
            return {}, 0.3

        else:
            # Unknown type, return as string
            return raw_value, 0.5

    def _get_default_value(self, field_type: str) -> Any:
        """Get default value for type."""
        defaults = {
            "string": "",
            "number": 0,
            "boolean": False,
            "array": [],
            "object": {},
        }
        return defaults.get(field_type, None)

    def parse_stream(self, tokens):
        """
        Stream parsing not applicable for structural decoupling.

        Structural decoupling generates data, doesn't parse streams.
        """
        raise NotImplementedError(
            "Structural decoupling doesn't support streaming input"
        )

    def configure(self, **config) -> "StructuralDecouplingParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return StructuralDecouplingParser(
            schema=self.schema,
            llm_generate=self.llm_generate,
            config=new_config,
        )


# Convenience constructors and builders


def structural_decoupling_parser(
    schema: dict[str, StructuredField],
    llm_generate: Callable[[str], str],
    config: Optional[ParserConfig] = None,
) -> StructuralDecouplingParser:
    """
    Create structural decoupling parser.

    Perfect for W-gent HTML generation and F-gent artifact assembly where
    you want to guarantee structure but let LLM generate content.

    Args:
        schema: Field definitions
        llm_generate: LLM generation function
        config: Parser configuration

    Returns:
        StructuralDecouplingParser

    Example:
        >>> schema = {
        ...     "title": StructuredField(name="title", type="string"),
        ...     "count": StructuredField(name="count", type="number"),
        ...     "active": StructuredField(name="active", type="boolean"),
        ... }
        >>> parser = structural_decoupling_parser(schema, llm_generate)
        >>> result = parser.parse("Generate a user profile")
        >>> result.value  # Guaranteed valid structure
    """
    return StructuralDecouplingParser(
        schema=schema,
        llm_generate=llm_generate,
        config=config,
    )


# Helper builders for common schemas


def simple_schema(**field_types) -> dict[str, StructuredField]:
    """
    Build simple schema from field names and types.

    Args:
        **field_types: field_name=type pairs

    Returns:
        Schema dict

    Example:
        >>> schema = simple_schema(
        ...     title="string",
        ...     count="number",
        ...     active="boolean",
        ... )
    """
    return {
        name: StructuredField(name=name, type=type_)
        for name, type_ in field_types.items()
    }


def field_with_prompt(
    name: str,
    type: str,
    prompt_template: str,
    validator: Optional[Callable[[Any], bool]] = None,
) -> StructuredField:
    """
    Create field with custom prompt template.

    Args:
        name: Field name
        type: Field type
        prompt_template: Prompt template (use {context}, {field_name})
        validator: Optional validation function

    Returns:
        StructuredField

    Example:
        >>> field = field_with_prompt(
        ...     name="hypothesis",
        ...     type="string",
        ...     prompt_template="Generate a scientific hypothesis for: {context}",
        ...     validator=lambda h: len(h) > 10,
        ... )
    """
    return StructuredField(
        name=name,
        type=type,
        prompt_template=prompt_template,
        validator=validator,
    )


# Mock LLM for testing (deterministic)


def mock_llm_generate(prompt: str) -> str:
    """
    Mock LLM generator for testing (no actual LLM calls).

    Extracts field name from prompt and generates deterministic value.
    """
    prompt_lower = prompt.lower()

    # Extract field name
    import re

    match = re.search(r"'([^']+)'", prompt)
    if not match:
        return "default_value"

    field_name = match.group(1)

    # Generate deterministic value based on type
    if "string" in prompt_lower:
        return f"Generated {field_name}"
    elif "number" in prompt_lower:
        return "42"
    elif "boolean" in prompt_lower:
        return "true"
    elif "array" in prompt_lower:
        return '["item1", "item2", "item3"]'
    elif "object" in prompt_lower:
        return '{"key": "value"}'
    else:
        return f"value_{field_name}"
