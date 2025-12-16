# Skip all tests in _archived directory
# These are preserved for reference but have broken imports
import pytest

collect_ignore_glob = ["**/*.py"]
