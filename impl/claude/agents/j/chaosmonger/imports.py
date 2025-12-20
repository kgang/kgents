"""
Import analysis and safety checking.

Extracts imports from AST and checks against whitelist/blacklist.
"""

from __future__ import annotations

import ast

from .types import DEFAULT_IMPORT_RISK, IMPORT_RISK, StabilityConfig


def extract_imports(tree: ast.AST) -> list[str]:
    """Extract all imported module names from AST."""
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Get the base module (e.g., "os" from "os.path")
                base = alias.name.split(".")[0]
                imports.append(base)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                base = node.module.split(".")[0]
                imports.append(base)

    return imports


def check_imports(
    imports: list[str],
    config: StabilityConfig,
    budget: float,
) -> tuple[bool, float, list[str]]:
    """
    Check imports against whitelist/blacklist and calculate risk.

    Returns (is_safe, total_risk, violations).
    """
    violations: list[str] = []
    total_risk = 0.0

    for imp in imports:
        # Check forbidden list first
        if imp in config.forbidden_imports:
            violations.append(f"Import '{imp}' is forbidden")
            continue

        # Check if in allowed list
        if imp not in config.allowed_imports:
            # Not in whitelist - check risk
            risk = IMPORT_RISK.get(imp, DEFAULT_IMPORT_RISK)
            if risk > 0.5:
                violations.append(f"Import '{imp}' not in allowed list (risk={risk:.1f})")
            total_risk += risk
        else:
            total_risk += IMPORT_RISK.get(imp, 0.0)

    # Check total risk against budget-scaled threshold
    threshold = budget * config.max_import_risk
    if total_risk > threshold and not violations:
        violations.append(
            f"Total import risk ({total_risk:.2f}) exceeds threshold ({threshold:.2f})"
        )

    is_safe = len(violations) == 0
    return is_safe, total_risk, violations
