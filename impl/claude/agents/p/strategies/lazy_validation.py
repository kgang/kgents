"""
Lazy Validation Parser (Strategy 2.4)

The Principle: Parse optimistically, validate only when fields are accessed.

Benefits:
- Fast initial parse (no upfront validation cost)
- Tolerant of extra fields (ignores unknown keys until accessed)
- Clear error messages (errors tied to specific field access)
- Memory efficient (doesn't construct full validated objects upfront)

Use Cases:
- D-gent state deserialization: Only validate fields actually used
- L-gent catalog entries: Defer validation of optional metadata
- Performance optimization: Skip validation for debug-only fields
"""

import json
from typing import Optional, Any, Callable, TypeVar, Generic

from agents.p.core import ParseResult, ParserConfig


T = TypeVar("T")


class LazyValidatedDict(Generic[T]):
    """
    Dict that validates fields lazily on access.

    Unlike eager validation (validate all fields upfront), lazy validation
    defers type coercion and validation until a field is accessed.

    This provides:
    - Fast initial parse (O(1) instead of O(n) in field count)
    - Graceful handling of malformed fields (errors only when accessed)
    - Support for partial data (missing fields detected on access)
    """

    def __init__(
        self,
        raw_data: dict,
        schema: dict[str, type],
        coercers: Optional[dict[str, Callable[[Any], Any]]] = None,
    ):
        """
        Initialize lazy validated dict.

        Args:
            raw_data: Raw dictionary data (unvalidated)
            schema: Type schema {field_name: expected_type}
            coercers: Optional custom coercion functions {field_name: coercer}
        """
        self._data = raw_data
        self._schema = schema
        self._coercers = coercers or {}
        self._validated = {}  # Cache validated values
        self._access_log = []  # Track which fields were accessed

    def __getitem__(self, key: str) -> Any:
        """
        Get field value, validating on first access.

        Args:
            key: Field name

        Returns:
            Validated value

        Raises:
            KeyError: If field missing or validation fails
        """
        # Log access
        self._access_log.append(key)

        # Check cache
        if key in self._validated:
            return self._validated[key]

        # Check if field exists
        if key not in self._data:
            if key in self._schema:
                raise KeyError(f"Required field '{key}' missing from data")
            else:
                raise KeyError(f"Unknown field '{key}'")

        # Get raw value
        raw_value = self._data[key]

        # Get expected type
        expected_type = self._schema.get(key, str)

        # Validate and coerce
        try:
            if key in self._coercers:
                # Custom coercer
                validated = self._coercers[key](raw_value)
            else:
                # Default coercion
                validated = self._coerce(raw_value, expected_type)

            # Cache validated value
            self._validated[key] = validated
            return validated

        except (ValueError, TypeError) as e:
            raise KeyError(f"Field '{key}' validation failed: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get field value with default (no validation error if missing)."""
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key: str) -> bool:
        """Check if key exists in raw data."""
        return key in self._data

    def keys(self):
        """Return keys from raw data."""
        return self._data.keys()

    def _coerce(self, value: Any, expected_type: type) -> Any:
        """
        Coerce value to expected type.

        Args:
            value: Raw value
            expected_type: Target type

        Returns:
            Coerced value

        Raises:
            ValueError: If coercion fails
        """
        # Handle None
        if value is None:
            if expected_type in (type(None), Optional):
                return None
            else:
                raise ValueError(f"Cannot coerce None to {expected_type}")

        # Handle numeric types
        if expected_type == float:
            return float(value)
        elif expected_type == int:
            # Coerce from string or float
            if isinstance(value, str):
                return int(value)
            elif isinstance(value, float):
                return int(value)
            return int(value)

        # Handle boolean
        elif expected_type == bool:
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                return value.lower() in ("true", "yes", "1", "t", "y")
            else:
                return bool(value)

        # Handle string
        elif expected_type == str:
            return str(value)

        # Handle list
        elif expected_type == list:
            if isinstance(value, list):
                return value
            else:
                raise ValueError(f"Expected list, got {type(value)}")

        # Handle dict
        elif expected_type == dict:
            if isinstance(value, dict):
                return value
            else:
                raise ValueError(f"Expected dict, got {type(value)}")

        # Default: return as-is
        else:
            return value

    def to_dict(self) -> dict:
        """
        Convert to plain dict (validates all schema fields).

        Note: This triggers validation for all schema fields.
        """
        result = {}
        for key in self._schema.keys():
            try:
                result[key] = self[key]
            except KeyError:
                # Skip missing fields
                pass
        return result

    def access_log(self) -> list[str]:
        """Return list of fields that were accessed."""
        return self._access_log.copy()


class LazyValidationParser:
    """
    Parser that returns LazyValidatedDict for deferred validation.

    Strategy:
    1. Parse JSON optimistically (no validation)
    2. Wrap in LazyValidatedDict with schema
    3. Validation happens on field access
    4. Confidence based on parse success (not validation)
    """

    def __init__(
        self,
        schema: dict[str, type],
        coercers: Optional[dict[str, Callable[[Any], Any]]] = None,
        config: Optional[ParserConfig] = None,
    ):
        """
        Initialize lazy validation parser.

        Args:
            schema: Type schema {field_name: expected_type}
            coercers: Optional custom coercion functions
            config: Parser configuration
        """
        self.schema = schema
        self.coercers = coercers or {}
        self.config = config or ParserConfig()

    def parse(self, text: str) -> ParseResult[LazyValidatedDict]:
        """
        Parse text into LazyValidatedDict.

        Args:
            text: Text to parse (JSON)

        Returns:
            ParseResult[LazyValidatedDict]

        Note:
            Initial parse is fast (no validation).
            Validation errors surface when fields are accessed.
        """
        # Try to parse JSON
        try:
            data = json.loads(text)

            if not isinstance(data, dict):
                return ParseResult(
                    success=False,
                    error=f"Expected JSON object, got {type(data).__name__}",
                    strategy="lazy-validation",
                )

            # Wrap in LazyValidatedDict (no validation yet)
            lazy_dict = LazyValidatedDict(
                raw_data=data,
                schema=self.schema,
                coercers=self.coercers,
            )

            # Check for extra fields (warning, not error)
            extra_fields = set(data.keys()) - set(self.schema.keys())
            repairs = []
            if extra_fields:
                repairs.append(
                    f"Ignoring {len(extra_fields)} extra fields: {', '.join(list(extra_fields)[:3])}"
                )

            # Check for missing required fields (warning, errors on access)
            missing_fields = set(self.schema.keys()) - set(data.keys())
            if missing_fields:
                repairs.append(
                    f"Missing {len(missing_fields)} schema fields (will error on access)"
                )

            # Confidence based on field coverage
            field_coverage = len(set(data.keys()) & set(self.schema.keys())) / max(
                len(self.schema), 1
            )
            confidence = 0.5 + 0.5 * field_coverage  # 0.5-1.0 range

            return ParseResult(
                success=True,
                value=lazy_dict,
                confidence=confidence,
                strategy="lazy-validation",
                repairs=repairs,
                metadata={
                    "total_fields": len(data),
                    "schema_fields": len(self.schema),
                    "extra_fields": len(extra_fields),
                    "missing_fields": len(missing_fields),
                    "field_coverage": field_coverage,
                },
            )

        except json.JSONDecodeError as e:
            return ParseResult(
                success=False,
                error=f"JSON parse error: {e}",
                strategy="lazy-validation",
            )

    def parse_stream(self, tokens):
        """
        Stream parsing (buffer and parse complete).

        Note: Lazy validation requires complete input to wrap in LazyValidatedDict.
        """
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config) -> "LazyValidationParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return LazyValidationParser(
            schema=self.schema,
            coercers=self.coercers,
            config=new_config,
        )


# Convenience constructors


def lazy_validation_parser(
    schema: dict[str, type],
    coercers: Optional[dict[str, Callable[[Any], Any]]] = None,
    config: Optional[ParserConfig] = None,
) -> LazyValidationParser:
    """
    Create lazy validation parser.

    Perfect for D-gent state deserialization and L-gent catalog parsing
    where you only need a subset of fields.

    Args:
        schema: Type schema {field_name: expected_type}
        coercers: Optional custom coercion functions
        config: Parser configuration

    Returns:
        LazyValidationParser

    Example:
        >>> schema = {
        ...     "name": str,
        ...     "age": int,
        ...     "active": bool,
        ...     "confidence": float,
        ... }
        >>> parser = lazy_validation_parser(schema)
        >>> result = parser.parse('{"name": "Alice", "age": "25", "extra": "ignored"}')
        >>> lazy_dict = result.value
        >>> lazy_dict["name"]  # "Alice" (validated on access)
        >>> lazy_dict["age"]   # 25 (coerced from string)
    """
    return LazyValidationParser(
        schema=schema,
        coercers=coercers,
        config=config,
    )


# Example custom coercers


def datetime_coercer(value: Any) -> Any:
    """Example coercer for datetime fields."""
    from datetime import datetime

    if isinstance(value, str):
        # Try multiple formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"Cannot parse datetime: {value}")
    return value


def list_of_strings_coercer(value: Any) -> list[str]:
    """Example coercer for list[str] fields."""
    if isinstance(value, list):
        return [str(item) for item in value]
    elif isinstance(value, str):
        # Split by comma
        return [item.strip() for item in value.split(",")]
    else:
        raise ValueError(f"Cannot coerce {type(value)} to list[str]")
