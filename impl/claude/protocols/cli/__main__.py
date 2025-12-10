"""
Make protocols.cli runnable with python -m protocols.cli

Uses the Hollow Shell pattern for fast startup.
"""

from .hollow import main
import sys

if __name__ == "__main__":
    sys.exit(main())
