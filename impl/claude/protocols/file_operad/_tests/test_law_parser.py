"""
Tests for Law Parser (Session 6a).

"The proof IS the decision. The mark IS the witness."
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from ..law_parser import (
    LawDefinition,
    LawStatus,
    extract_verification_code,
    list_laws_in_operad,
    parse_law_file,
    parse_law_markdown,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_law_content() -> str:
    """Sample .law file content."""
    return """# Law: create_read_identity

> *"Created content is immediately readable."*

**Status**: ✅ VERIFIED
**Operations**: `create`, `read`
**Category**: Identity

---

## Statement

```
read(create(p, c)) ≡ c
```

For all paths p and content c.

---

## Verification

```python
def test_create_read_identity():
    content = "test"
    path = "test.op"
    write(path, content)
    assert read(path) == content
```

---

## Last Verified

- **Date**: 2025-12-22
- **By**: Session 6a bootstrap
- **Result**: PASSED

---

## Wires To

- [creates] `FILE_OPERAD/create`
- [verifies] `FILE_OPERAD/read`
"""


@pytest.fixture
def minimal_law_content() -> str:
    """Minimal valid .law file."""
    return """# Law: minimal_law

**Status**: ⏸ UNVERIFIED
**Category**: Test

## Statement

x == x
"""


@pytest.fixture
def failed_law_content() -> str:
    """Law with FAILED status."""
    return """# Law: failed_law

**Status**: ❌ FAILED
**Operations**: `broken`
**Category**: Error

## Statement

1 == 2

## Verification

```python
def test_fails():
    assert 1 == 2
```
"""


# =============================================================================
# LawStatus Tests
# =============================================================================


class TestLawStatus:
    """Tests for LawStatus enum."""

    def test_status_values_exist(self):
        """All required status values exist."""
        assert LawStatus.VERIFIED
        assert LawStatus.UNVERIFIED
        assert LawStatus.FAILED

    def test_status_is_enum(self):
        """LawStatus is a proper enum."""
        assert LawStatus.VERIFIED.name == "VERIFIED"
        assert LawStatus.UNVERIFIED.name == "UNVERIFIED"
        assert LawStatus.FAILED.name == "FAILED"


# =============================================================================
# LawDefinition Tests
# =============================================================================


class TestLawDefinition:
    """Tests for LawDefinition dataclass."""

    def test_create_law_definition(self):
        """Create a basic LawDefinition."""
        law = LawDefinition(
            name="test_law",
            equation="a == a",
            operations=("op1", "op2"),
            category="Identity",
            status=LawStatus.VERIFIED,
            verification_code="def test(): pass",
        )

        assert law.name == "test_law"
        assert law.equation == "a == a"
        assert law.operations == ("op1", "op2")
        assert law.status == LawStatus.VERIFIED

    def test_law_definition_is_frozen(self):
        """LawDefinition is immutable."""
        law = LawDefinition(
            name="frozen_law",
            equation="x == x",
            operations=(),
            category="Test",
            status=LawStatus.UNVERIFIED,
            verification_code="",
        )

        with pytest.raises(AttributeError):
            law.name = "modified"  # type: ignore

    def test_is_verified_property(self):
        """is_verified property works correctly."""
        verified = LawDefinition(
            name="v",
            equation="",
            operations=(),
            category="",
            status=LawStatus.VERIFIED,
            verification_code="",
        )
        unverified = LawDefinition(
            name="u",
            equation="",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="",
        )

        assert verified.is_verified is True
        assert unverified.is_verified is False

    def test_status_emoji_property(self):
        """status_emoji returns correct emoji."""
        verified = LawDefinition(
            name="v",
            equation="",
            operations=(),
            category="",
            status=LawStatus.VERIFIED,
            verification_code="",
        )
        unverified = LawDefinition(
            name="u",
            equation="",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="",
        )
        failed = LawDefinition(
            name="f",
            equation="",
            operations=(),
            category="",
            status=LawStatus.FAILED,
            verification_code="",
        )

        assert verified.status_emoji == "✅"
        assert unverified.status_emoji == "⏸"
        assert failed.status_emoji == "❌"

    def test_to_dict(self):
        """Serialization to dict works."""
        law = LawDefinition(
            name="test",
            equation="x == x",
            operations=("a", "b"),
            category="Test",
            status=LawStatus.VERIFIED,
            verification_code="code",
            description="A test law",
            wires_to=("path1", "path2"),
            last_verified=datetime(2025, 12, 22),
            verified_by="test",
            source_path="/path/to/law.law",
        )

        d = law.to_dict()

        assert d["name"] == "test"
        assert d["equation"] == "x == x"
        assert d["operations"] == ["a", "b"]
        assert d["status"] == "VERIFIED"
        assert d["wires_to"] == ["path1", "path2"]
        assert d["last_verified"] == "2025-12-22T00:00:00"

    def test_from_dict(self):
        """Deserialization from dict works."""
        data = {
            "name": "restored",
            "equation": "y == y",
            "operations": ["c"],
            "category": "Restored",
            "status": "FAILED",
            "verification_code": "test code",
            "last_verified": "2025-12-22T10:30:00",
            "verified_by": "tester",
        }

        law = LawDefinition.from_dict(data)

        assert law.name == "restored"
        assert law.status == LawStatus.FAILED
        assert law.last_verified == datetime(2025, 12, 22, 10, 30)

    def test_roundtrip_serialization(self):
        """to_dict -> from_dict preserves all fields."""
        original = LawDefinition(
            name="roundtrip",
            equation="a >> b == b >> a",
            operations=("seq",),
            category="Composition",
            status=LawStatus.VERIFIED,
            verification_code="```python\ntest\n```",
            description="Test roundtrip",
            wires_to=("op1", "op2"),
            last_verified=datetime(2025, 12, 22, 15, 30, 45),
            verified_by="session6a",
            source_path="/test/path.law",
        )

        restored = LawDefinition.from_dict(original.to_dict())

        assert restored.name == original.name
        assert restored.equation == original.equation
        assert restored.operations == original.operations
        assert restored.status == original.status
        assert restored.last_verified == original.last_verified


# =============================================================================
# Parsing Tests
# =============================================================================


class TestParseLawMarkdown:
    """Tests for parse_law_markdown function."""

    def test_parse_full_law(self, sample_law_content):
        """Parse a complete .law file."""
        law = parse_law_markdown(sample_law_content)

        assert law.name == "create_read_identity"
        assert law.status == LawStatus.VERIFIED
        assert law.category == "Identity"
        assert "create" in law.operations
        assert "read" in law.operations
        assert "read(create(p, c)) ≡ c" in law.equation
        assert law.description == "Created content is immediately readable."

    def test_parse_verification_code(self, sample_law_content):
        """Verification code is extracted correctly."""
        law = parse_law_markdown(sample_law_content)

        assert "def test_create_read_identity" in law.verification_code
        assert "```python" in law.verification_code

    def test_parse_wires_to(self, sample_law_content):
        """Wires To section is parsed correctly."""
        law = parse_law_markdown(sample_law_content)

        assert "FILE_OPERAD/create" in law.wires_to
        assert "FILE_OPERAD/read" in law.wires_to

    def test_parse_last_verified(self, sample_law_content):
        """Last Verified section is parsed correctly."""
        law = parse_law_markdown(sample_law_content)

        assert law.last_verified is not None
        assert law.last_verified.year == 2025
        assert law.last_verified.month == 12
        assert law.last_verified.day == 22
        assert law.verified_by == "Session 6a bootstrap"

    def test_parse_minimal_law(self, minimal_law_content):
        """Parse minimal valid .law file."""
        law = parse_law_markdown(minimal_law_content)

        assert law.name == "minimal_law"
        assert law.status == LawStatus.UNVERIFIED
        assert law.category == "Test"

    def test_parse_failed_status(self, failed_law_content):
        """Parse law with FAILED status."""
        law = parse_law_markdown(failed_law_content)

        assert law.name == "failed_law"
        assert law.status == LawStatus.FAILED
        assert "broken" in law.operations

    def test_parse_missing_name_raises(self):
        """Missing name raises ValueError."""
        content = """
**Status**: ✅ VERIFIED

## Statement
x == x
"""
        with pytest.raises(ValueError, match="must have"):
            parse_law_markdown(content)

    def test_parse_with_source_path(self, sample_law_content):
        """source_path is set when provided."""
        law = parse_law_markdown(sample_law_content, source_path="/test/path.law")

        assert law.source_path == "/test/path.law"


class TestParseLawFile:
    """Tests for parse_law_file function."""

    def test_parse_file_not_found(self, tmp_path):
        """Non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_law_file(tmp_path / "nonexistent.law")

    def test_parse_file_sets_source_path(self, tmp_path, sample_law_content):
        """parse_law_file sets source_path correctly."""
        law_file = tmp_path / "test.law"
        law_file.write_text(sample_law_content)

        law = parse_law_file(law_file)

        assert law.source_path == str(law_file)


class TestListLawsInOperad:
    """Tests for list_laws_in_operad function."""

    def test_list_empty_operad(self, tmp_path):
        """Empty operad returns empty list."""
        operad_dir = tmp_path / "TEST_OPERAD"
        operad_dir.mkdir()

        laws = list_laws_in_operad(operad_dir)

        assert laws == []

    def test_list_operad_without_laws_dir(self, tmp_path):
        """Operad without _laws dir returns empty list."""
        operad_dir = tmp_path / "TEST_OPERAD"
        operad_dir.mkdir()
        (operad_dir / "op1.op").write_text("# op1")

        laws = list_laws_in_operad(operad_dir)

        assert laws == []

    def test_list_laws_in_operad(self, tmp_path, sample_law_content, minimal_law_content):
        """list_laws_in_operad returns all laws."""
        operad_dir = tmp_path / "TEST_OPERAD"
        laws_dir = operad_dir / "_laws"
        laws_dir.mkdir(parents=True)

        (laws_dir / "law1.law").write_text(sample_law_content)
        (laws_dir / "law2.law").write_text(minimal_law_content)

        laws = list_laws_in_operad(operad_dir)

        assert len(laws) == 2
        names = {law.name for law in laws}
        assert "create_read_identity" in names
        assert "minimal_law" in names

    def test_list_laws_sorted(self, tmp_path, sample_law_content):
        """Laws are returned in sorted order."""
        operad_dir = tmp_path / "TEST_OPERAD"
        laws_dir = operad_dir / "_laws"
        laws_dir.mkdir(parents=True)

        # Create with non-alphabetical names
        (laws_dir / "z_law.law").write_text(
            sample_law_content.replace("create_read_identity", "z_law")
        )
        (laws_dir / "a_law.law").write_text(
            sample_law_content.replace("create_read_identity", "a_law")
        )

        laws = list_laws_in_operad(operad_dir)

        # Should be alphabetically sorted by filename
        assert laws[0].name == "a_law"
        assert laws[1].name == "z_law"


class TestExtractVerificationCode:
    """Tests for extract_verification_code function."""

    def test_extract_strips_fences(self, sample_law_content):
        """Code fences are stripped."""
        law = parse_law_markdown(sample_law_content)
        code = extract_verification_code(law)

        assert "```python" not in code
        assert "```" not in code
        assert "def test_create_read_identity" in code

    def test_extract_empty_code(self):
        """Empty verification code returns empty string."""
        law = LawDefinition(
            name="no_code",
            equation="",
            operations=(),
            category="",
            status=LawStatus.UNVERIFIED,
            verification_code="",
        )

        code = extract_verification_code(law)

        assert code == ""


# =============================================================================
# Integration Tests
# =============================================================================


class TestFileOperadLaws:
    """Integration tests with actual FILE_OPERAD laws."""

    @pytest.fixture
    def file_operad_dir(self) -> Path:
        """Get FILE_OPERAD directory (may not exist in test env)."""
        return Path.home() / ".kgents" / "operads" / "FILE_OPERAD"

    def test_parse_create_read_identity_law(self, file_operad_dir):
        """Parse the create_read_identity.law file if it exists."""
        law_path = file_operad_dir / "_laws" / "create_read_identity.law"

        if not law_path.exists():
            pytest.skip("FILE_OPERAD laws not installed")

        law = parse_law_file(law_path)

        assert law.name == "create_read_identity"
        assert law.status == LawStatus.VERIFIED
        assert "create" in law.operations
        assert "read" in law.operations
        assert "≡" in law.equation

    def test_list_file_operad_laws(self, file_operad_dir):
        """List all FILE_OPERAD laws if they exist."""
        if not (file_operad_dir / "_laws").exists():
            pytest.skip("FILE_OPERAD laws not installed")

        laws = list_laws_in_operad(file_operad_dir)

        # Should have our 4 laws
        assert len(laws) >= 4

        # Check expected laws exist
        names = {law.name for law in laws}
        assert "create_read_identity" in names
        assert "empty_update_identity" in names
        assert "sandbox_equivalence" in names
        assert "annotate_preservation" in names


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""

    def test_unicode_in_law(self):
        """Unicode content is handled correctly."""
        content = """# Law: unicode_law

> *"测试 → 通过"*

**Status**: ✅ VERIFIED
**Category**: 国际化

## Statement

α ≡ α
"""
        law = parse_law_markdown(content)

        assert law.name == "unicode_law"
        assert law.description == "测试 → 通过"
        assert "α ≡ α" in law.equation

    def test_multiline_equation(self):
        """Multiline equations in code block."""
        content = """# Law: multiline_law

**Status**: ✅ VERIFIED
**Category**: Complex

## Statement

```
(a >> b) >> c
  ≡
a >> (b >> c)
```
"""
        law = parse_law_markdown(content)

        assert "a >> b" in law.equation
        assert "b >> c" in law.equation

    def test_missing_optional_sections(self):
        """Missing optional sections don't cause errors."""
        content = """# Law: sparse_law

**Status**: ⏸ UNVERIFIED
**Category**: Minimal

## Statement

x
"""
        law = parse_law_markdown(content)

        assert law.name == "sparse_law"
        assert law.wires_to == ()
        assert law.last_verified is None
        assert law.verified_by is None
        assert law.verification_code == ""
