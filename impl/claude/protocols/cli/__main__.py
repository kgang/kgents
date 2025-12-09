"""
Make protocols.cli runnable with python -m protocols.cli
"""

from .main import main
import sys

if __name__ == "__main__":
    sys.exit(main())
