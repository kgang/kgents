"""
JIT Agent Sandbox: Safe execution environment for dynamically compiled agents.

Split into:
- namespace: SandboxedNamespace class for restricted execution
- executor: execute_in_sandbox, jit_compile_and_execute
- validation: validate_jit_safety, type_check_source

Philosophy:
> "Trust, but verify. Then sandbox anyway."
"""

from .executor import execute_in_sandbox, jit_compile_and_execute, type_check_source
from .namespace import SandboxConfig, SandboxedNamespace, SandboxResult
from .validation import validate_jit_safety

__all__ = [
    # namespace
    "SandboxedNamespace",
    "SandboxConfig",
    "SandboxResult",
    # executor
    "execute_in_sandbox",
    "jit_compile_and_execute",
    "type_check_source",
    # validation
    "validate_jit_safety",
]
