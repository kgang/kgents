"""
Contract Test: Frontend-Backend Enum Synchronization.

This test ensures that Python enums and TypeScript types stay in sync.
It parses the TypeScript source and compares against Python definitions.

FAIL-HARD PHILOSOPHY: We want drift to break CI, not silently fail at runtime.

When this test fails:
1. Check which values are missing
2. Add to BOTH Python enum AND TypeScript type AND TypeScript config
3. This is intentionally annoying to ensure you update all three

When this test passes but runtime still crashes:
- Backend server may be running stale code → restart uvicorn
- Browser may have cached API response → hard refresh (Cmd+Shift+R)

Pattern: Contract tests bridge type gaps between languages.
See: plans/meta.md "Contract tests bridge type gaps"
"""

import re
from pathlib import Path

import pytest
from protocols.projection.gallery.pilots import PilotCategory

# Path to TypeScript types file (relative to impl/claude)
TS_TYPES_PATH = (
    Path(__file__).parent.parent.parent.parent.parent / "web/src/api/types.ts"
)


def extract_typescript_union(ts_content: str, type_name: str) -> set[str]:
    """
    Extract values from a TypeScript union type definition.

    Handles format like:
        export type GalleryCategory =
          | 'PRIMITIVES'
          | 'CARDS'
          ...
    """
    # Find the type definition
    pattern = rf"export type {type_name}\s*=\s*([\s\S]*?)(?:;|export)"
    match = re.search(pattern, ts_content)
    if not match:
        raise ValueError(f"Could not find type {type_name} in TypeScript file")

    type_body = match.group(1)

    # Extract quoted string values
    values = re.findall(r"['\"](\w+)['\"]", type_body)
    return set(values)


def extract_typescript_record_keys(ts_content: str, const_name: str) -> set[str]:
    """
    Extract keys from a TypeScript Record const definition.

    Handles format like:
        export const GALLERY_CATEGORY_CONFIG: Record<GalleryCategory, ...> = {
          PRIMITIVES: ...,
          CARDS: ...,
        };
    """
    # Find the const definition
    pattern = rf"export const {const_name}[^=]*=\s*\{{([\s\S]*?)\}};"
    match = re.search(pattern, ts_content)
    if not match:
        raise ValueError(f"Could not find const {const_name} in TypeScript file")

    body = match.group(1)

    # Extract keys (identifiers before colons)
    keys = re.findall(r"^\s*(\w+)\s*:", body, re.MULTILINE)
    return set(keys)


class TestGalleryCategoryContract:
    """
    Contract tests ensuring Python PilotCategory and TypeScript GalleryCategory
    remain synchronized.
    """

    @pytest.fixture
    def ts_content(self) -> str:
        """Load TypeScript types file."""
        if not TS_TYPES_PATH.exists():
            pytest.skip(f"TypeScript file not found: {TS_TYPES_PATH}")
        return TS_TYPES_PATH.read_text()

    @pytest.fixture
    def python_categories(self) -> set[str]:
        """Get all Python PilotCategory enum values."""
        return {member.name for member in PilotCategory}

    @pytest.fixture
    def typescript_type_values(self, ts_content: str) -> set[str]:
        """Get all TypeScript GalleryCategory union values."""
        return extract_typescript_union(ts_content, "GalleryCategory")

    @pytest.fixture
    def typescript_config_keys(self, ts_content: str) -> set[str]:
        """Get all keys in GALLERY_CATEGORY_CONFIG."""
        return extract_typescript_record_keys(ts_content, "GALLERY_CATEGORY_CONFIG")

    def test_python_matches_typescript_type(
        self, python_categories: set[str], typescript_type_values: set[str]
    ) -> None:
        """
        Python PilotCategory must exactly match TypeScript GalleryCategory type.

        If this fails:
        - In Python only: Add to web/src/api/types.ts GalleryCategory type
        - In TypeScript only: Add to protocols/projection/gallery/pilots.py PilotCategory
        """
        missing_in_ts = python_categories - typescript_type_values
        missing_in_py = typescript_type_values - python_categories

        errors = []
        if missing_in_ts:
            errors.append(
                f"Python has categories not in TypeScript type: {sorted(missing_in_ts)}\n"
                f"  → Add to web/src/api/types.ts GalleryCategory"
            )
        if missing_in_py:
            errors.append(
                f"TypeScript type has categories not in Python: {sorted(missing_in_py)}\n"
                f"  → Add to protocols/projection/gallery/pilots.py PilotCategory"
            )

        assert not errors, "\n\n".join(errors)

    def test_typescript_type_matches_config(
        self, typescript_type_values: set[str], typescript_config_keys: set[str]
    ) -> None:
        """
        TypeScript GalleryCategory type must exactly match GALLERY_CATEGORY_CONFIG keys.

        If this fails:
        - In type only: Add to GALLERY_CATEGORY_CONFIG in web/src/api/types.ts
        - In config only: Add to GalleryCategory type in web/src/api/types.ts
        """
        missing_in_config = typescript_type_values - typescript_config_keys
        missing_in_type = typescript_config_keys - typescript_type_values

        errors = []
        if missing_in_config:
            errors.append(
                f"GalleryCategory type has values not in GALLERY_CATEGORY_CONFIG: {sorted(missing_in_config)}\n"
                f"  → Add entries to GALLERY_CATEGORY_CONFIG in web/src/api/types.ts"
            )
        if missing_in_type:
            errors.append(
                f"GALLERY_CATEGORY_CONFIG has keys not in GalleryCategory type: {sorted(missing_in_type)}\n"
                f"  → This should be caught by TypeScript, check for type errors"
            )

        assert not errors, "\n\n".join(errors)

    def test_all_three_in_sync(
        self,
        python_categories: set[str],
        typescript_type_values: set[str],
        typescript_config_keys: set[str],
    ) -> None:
        """
        All three definitions must be identical.

        This is the master check that ensures complete synchronization.
        """
        all_values = python_categories | typescript_type_values | typescript_config_keys

        # Check each source has all values
        py_missing = all_values - python_categories
        ts_type_missing = all_values - typescript_type_values
        ts_config_missing = all_values - typescript_config_keys

        if py_missing or ts_type_missing or ts_config_missing:
            msg = "Category definitions are out of sync:\n\n"
            msg += f"All categories (union): {sorted(all_values)}\n\n"

            if py_missing:
                msg += f"Missing from Python PilotCategory: {sorted(py_missing)}\n"
            if ts_type_missing:
                msg += f"Missing from TypeScript GalleryCategory: {sorted(ts_type_missing)}\n"
            if ts_config_missing:
                msg += f"Missing from GALLERY_CATEGORY_CONFIG: {sorted(ts_config_missing)}\n"

            msg += "\nTo fix: Update all three locations to have the same values."
            pytest.fail(msg)
