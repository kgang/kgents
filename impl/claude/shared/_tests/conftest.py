"""
Conftest for shared module tests.

Skip these tests if hypothesis is not installed (WIP module).
"""

import pytest

try:
    import hypothesis  # noqa: F401
except ImportError:
    pytest.skip("hypothesis not installed", allow_module_level=True)
