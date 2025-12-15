"""
Advanced Monograph Generation System - Multi-agent scholarly writing with dialectical feedback.

This package implements a sophisticated system for generating PhD-level monographs
using the PolyAgent + Operad + Sheaf pattern (AD-006).

Usage:
    from monograph.generator import MonographGenerator, MonographConfig

    config = MonographConfig(
        title="Your Title",
        theme="Your Theme",
        parts=5,
    )

    generator = MonographGenerator(config)
    monograph = await generator.generate()
"""

__version__ = "1.0.0"
__author__ = "kgents system"

from monograph.generator import MonographGenerator, MonographConfig

__all__ = ["MonographGenerator", "MonographConfig"]
