"""Tests for TypeRegistry type mapping."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Optional, cast

from protocols.cli.prism import TypeRegistry


class Color(Enum):
    """Test enum for type mapping."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class TestTypeRegistryBuiltins:
    """Tests for built-in type mappings."""

    def test_str_mapping(self) -> None:
        """str maps to type=str."""
        result = TypeRegistry.map(str)
        assert result["type"] is str

    def test_int_mapping(self) -> None:
        """int maps to type=int."""
        result = TypeRegistry.map(int)
        assert result["type"] is int

    def test_float_mapping(self) -> None:
        """float maps to type=float."""
        result = TypeRegistry.map(float)
        assert result["type"] is float

    def test_bool_mapping(self) -> None:
        """bool maps to action=store_true."""
        result = TypeRegistry.map(bool)
        assert result["action"] == "store_true"
        assert result["default"] is False

    def test_path_mapping(self) -> None:
        """Path maps to type=Path."""
        result = TypeRegistry.map(Path)
        assert result["type"] is Path


class TestTypeRegistryOptional:
    """Tests for Optional type mappings."""

    def test_optional_str(self) -> None:
        """Optional[str] is not required."""
        result = TypeRegistry.map(cast(type, str | None))
        assert result.get("required") is False

    def test_optional_int(self) -> None:
        """Optional[int] maps inner type."""
        result = TypeRegistry.map(cast(type, int | None))
        assert result["type"] is int
        assert result.get("required") is False

    def test_optional_with_typing(self) -> None:
        """Optional from typing module works."""
        result = TypeRegistry.map(cast(type, Optional[str]))
        assert result.get("required") is False


class TestTypeRegistryList:
    """Tests for list type mappings."""

    def test_list_str(self) -> None:
        """list[str] maps to nargs='*'."""
        result = TypeRegistry.map(list[str])
        assert result["nargs"] == "*"
        assert result["type"] is str

    def test_list_int(self) -> None:
        """list[int] maps inner type."""
        result = TypeRegistry.map(list[int])
        assert result["nargs"] == "*"
        assert result["type"] is int

    def test_list_default_empty(self) -> None:
        """list types default to empty list."""
        result = TypeRegistry.map(list[str])
        assert result["default"] == []


class TestTypeRegistryEnum:
    """Tests for Enum type mappings."""

    def test_enum_choices(self) -> None:
        """Enum maps to choices."""
        result = TypeRegistry.map(Color)
        assert "choices" in result
        assert set(result["choices"]) == {"red", "green", "blue"}

    def test_enum_type_str(self) -> None:
        """Enum uses str type for parsing."""
        result = TypeRegistry.map(Color)
        assert result["type"] is str


class TestTypeRegistryCustom:
    """Tests for custom type registration."""

    def test_register_custom_type(self) -> None:
        """Custom types can be registered."""

        class CustomType:
            pass

        def custom_mapper(t: type) -> dict[str, Any]:
            return {"type": str, "metavar": "CUSTOM"}

        TypeRegistry.register(CustomType, custom_mapper)

        try:
            result = TypeRegistry.map(CustomType)
            assert result["metavar"] == "CUSTOM"
        finally:
            TypeRegistry.unregister(CustomType)

    def test_unregister_custom_type(self) -> None:
        """Custom types can be unregistered."""

        class TempType:
            pass

        TypeRegistry.register(TempType, lambda t: {"type": int})
        TypeRegistry.unregister(TempType)

        # Should fall back to default (str)
        result = TypeRegistry.map(TempType)
        assert result["type"] is str

    def test_custom_overrides_builtin(self) -> None:
        """Custom registration overrides builtins."""

        def custom_int_mapper(t: type) -> dict[str, Any]:
            return {"type": str, "help": "Custom int"}

        TypeRegistry.register(int, custom_int_mapper)

        try:
            result = TypeRegistry.map(int)
            assert result["type"] is str
            assert result["help"] == "Custom int"
        finally:
            TypeRegistry.unregister(int)

        # Back to default
        result = TypeRegistry.map(int)
        assert result["type"] is int


class TestTypeRegistryHelpers:
    """Tests for TypeRegistry helper methods."""

    def test_is_flag_type_bool(self) -> None:
        """is_flag_type returns True for bool."""
        assert TypeRegistry.is_flag_type(bool) is True

    def test_is_flag_type_non_bool(self) -> None:
        """is_flag_type returns False for non-bool."""
        assert TypeRegistry.is_flag_type(str) is False
        assert TypeRegistry.is_flag_type(int) is False

    def test_is_optional_union_none(self) -> None:
        """is_optional detects T | None."""
        assert TypeRegistry.is_optional(cast(type, str | None)) is True
        assert TypeRegistry.is_optional(cast(type, int | None)) is True

    def test_is_optional_non_optional(self) -> None:
        """is_optional returns False for non-optional."""
        assert TypeRegistry.is_optional(str) is False
        assert TypeRegistry.is_optional(int) is False

    def test_get_inner_type_optional(self) -> None:
        """get_inner_type extracts from Optional."""
        assert TypeRegistry.get_inner_type(cast(type, str | None)) is str
        assert TypeRegistry.get_inner_type(cast(type, int | None)) is int

    def test_get_inner_type_list(self) -> None:
        """get_inner_type extracts from list."""
        assert TypeRegistry.get_inner_type(list[str]) is str
        assert TypeRegistry.get_inner_type(list[int]) is int

    def test_get_inner_type_plain(self) -> None:
        """get_inner_type returns type for plain types."""
        assert TypeRegistry.get_inner_type(str) is str
        assert TypeRegistry.get_inner_type(int) is int


class TestTypeRegistryEdgeCases:
    """Tests for edge cases in type mapping."""

    def test_unknown_type_defaults_to_str(self) -> None:
        """Unknown types default to str."""

        class UnknownType:
            pass

        result = TypeRegistry.map(UnknownType)
        assert result["type"] is str

    def test_none_type(self) -> None:
        """NoneType handled gracefully."""
        result = TypeRegistry.map(type(None))
        assert result["type"] is str
        assert result["default"] is None

    def test_has_default_parameter(self) -> None:
        """has_default parameter affects mapping."""
        # With default
        result_with = TypeRegistry.map(str, has_default=True)
        # Without default
        result_without = TypeRegistry.map(str, has_default=False)

        # Both should return str type
        assert result_with["type"] is str
        assert result_without["type"] is str
