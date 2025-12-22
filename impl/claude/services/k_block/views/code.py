"""CodeView: Type definitions view for K-Block content.

Extracts field definitions from markdown and renders them
as Python dataclass code.
"""

from dataclasses import dataclass, field
from typing import Any, FrozenSet

from .base import ViewType
from .tokens import SemanticToken, TokenKind


@dataclass(frozen=True)
class FieldDef:
    """A field definition extracted from content."""

    name: str
    type_hint: str
    default: str | None = None


@dataclass
class CodeView:
    """Python dataclass view of K-Block content.

    Extracts type/field definitions and renders as Python code:
    - Headings become class names
    - Fields (- name: type) become dataclass fields
    """

    _content: str = ""
    _tokens: FrozenSet[SemanticToken] = field(default_factory=frozenset)
    _class_name: str = "GeneratedType"
    _fields: list[FieldDef] = field(default_factory=list)

    @property
    def view_type(self) -> ViewType:
        """Return CODE view type."""
        return ViewType.CODE

    @property
    def fields(self) -> list[FieldDef]:
        """Return extracted field definitions."""
        return self._fields

    def render(self, content: str, *args: Any, **kwargs: Any) -> str:
        """Parse content and extract type definitions.

        Args:
            content: Markdown content to parse

        Returns:
            Python dataclass code as string
        """
        self._content = content
        self._extract_types(content)
        self._tokens = self._extract_tokens()
        return self._to_python()

    def tokens(self) -> FrozenSet[SemanticToken]:
        """Return semantic tokens (fields as tokens)."""
        return self._tokens

    def to_canonical(self) -> str:
        """Return original content (code cannot be converted back)."""
        return self._content

    def _extract_types(self, content: str) -> None:
        """Extract class name and fields from markdown."""
        self._fields = []
        self._class_name = "GeneratedType"

        for line in content.split("\n"):
            stripped = line.strip()

            # First heading becomes class name
            if stripped.startswith("#") and self._class_name == "GeneratedType":
                text = stripped.lstrip("#").strip()
                # Convert to valid Python identifier
                self._class_name = "".join(c if c.isalnum() else "_" for c in text).strip("_")
                if self._class_name and self._class_name[0].isdigit():
                    self._class_name = "_" + self._class_name

            # Fields: "- name: type" or "- name: type = default"
            elif stripped.startswith(("-", "*")) and ":" in stripped:
                field_part = stripped.lstrip("-*").strip()
                if ":" in field_part:
                    parts = field_part.split(":", 1)
                    field_name = parts[0].strip()
                    type_and_default = parts[1].strip()

                    # Skip URLs
                    if field_name.startswith("http"):
                        continue

                    # Parse type and optional default
                    if "=" in type_and_default:
                        type_hint, default = type_and_default.split("=", 1)
                        type_hint = type_hint.strip()
                        default = default.strip()
                    else:
                        type_hint = type_and_default
                        default = None

                    # Normalize type hints
                    type_hint = self._normalize_type(type_hint)

                    # Valid field name
                    safe_name = "".join(c if c.isalnum() or c == "_" else "_" for c in field_name)
                    if safe_name and not safe_name[0].isdigit():
                        self._fields.append(
                            FieldDef(name=safe_name, type_hint=type_hint, default=default)
                        )

    def _normalize_type(self, type_hint: str) -> str:
        """Normalize type hints to Python types."""
        type_map = {
            "string": "str",
            "String": "str",
            "integer": "int",
            "Integer": "int",
            "number": "float",
            "Number": "float",
            "boolean": "bool",
            "Boolean": "bool",
            "array": "list",
            "Array": "list",
            "object": "dict",
            "Object": "dict",
        }
        return type_map.get(type_hint, type_hint)

    def _extract_tokens(self) -> FrozenSet[SemanticToken]:
        """Convert fields to semantic tokens."""
        tokens: set[SemanticToken] = set()

        # Class name as type token
        if self._class_name != "GeneratedType":
            tokens.add(
                SemanticToken(
                    id=f"t-{self._class_name}",
                    kind=TokenKind.TYPE,
                    value=self._class_name,
                    position=None,
                )
            )

        # Fields as field tokens
        for f in self._fields:
            tokens.add(
                SemanticToken(id=f"f-{f.name}", kind=TokenKind.FIELD, value=f.name, position=None)
            )

        return frozenset(tokens)

    def _to_python(self) -> str:
        """Render as Python dataclass code."""
        lines = [
            "from dataclasses import dataclass",
            "",
            "",
            "@dataclass",
            f"class {self._class_name}:",
        ]

        if not self._fields:
            lines.append("    pass")
        else:
            for f in self._fields:
                if f.default is not None:
                    lines.append(f"    {f.name}: {f.type_hint} = {f.default}")
                else:
                    lines.append(f"    {f.name}: {f.type_hint}")

        return "\n".join(lines)
