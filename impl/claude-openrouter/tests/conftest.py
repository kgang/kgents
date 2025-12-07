"""Pytest configuration and fixtures"""

import pytest
import sys
from pathlib import Path

# Add the package root to path so we can import runtime and bootstrap
package_root = Path(__file__).parent.parent
sys.path.insert(0, str(package_root))


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all singletons between tests"""
    from runtime import reset_all
    reset_all()
    yield
    reset_all()
