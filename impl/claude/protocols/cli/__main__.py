"""
Make protocols.cli runnable with python -m protocols.cli

Uses the Hollow Shell pattern for fast startup.
"""

import sys

from .hollow import main

if __name__ == "__main__":
    sys.exit(main())
