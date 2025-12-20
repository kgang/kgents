"""
Token type implementations.

This module contains concrete implementations of MeaningToken for each
of the six core token types:
- AGENTESEPath: Portal to the agent system
- TaskCheckbox: Proof of completion with trace witness
- Image: Multimodal context with AI analysis
- CodeBlock: Executable action with sandboxed execution
- PrincipleRef: Anchor to design principles
- RequirementRef: Trace to requirements with verification status

Each token type implements the MeaningToken abstract base class and
provides affordances appropriate to its semantic meaning.
"""

from .agentese_path import (
    AGENTESEPathToken,
    ContextMenuResult,
    DragResult,
    HoverInfo,
    NavigationResult,
    PolynomialState,
    create_agentese_path_token,
)
from .base import (
    BaseMeaningToken,
    ExecutionTrace,
    TraceWitness,
    filter_affordances_by_observer,
)
from .code_block import (
    CodeBlockContextMenuResult,
    CodeBlockHoverInfo,
    CodeBlockToken,
    EditFocusResult,
    ExecutionResult,
    create_code_block_token,
)
from .image import (
    ImageAnalysis,
    ImageDragResult,
    ImageExpandResult,
    ImageHoverInfo,
    ImageToken,
    create_image_token,
)
from .principle_ref import (
    PrincipleContextMenuResult,
    PrincipleHoverInfo,
    PrincipleInfo,
    PrincipleNavigationResult,
    PrincipleRefToken,
    create_principle_ref_token,
)
from .requirement_ref import (
    RequirementContextMenuResult,
    RequirementHoverInfo,
    RequirementInfo,
    RequirementNavigationResult,
    RequirementRefToken,
    create_requirement_ref_token,
)
from .task_checkbox import (
    TaskCheckboxToken,
    TaskContextMenuResult,
    TaskHoverInfo,
    ToggleResult,
    VerificationStatus,
    create_task_checkbox_token,
)

__all__ = [
    # Base classes
    "BaseMeaningToken",
    "ExecutionTrace",
    "TraceWitness",
    "filter_affordances_by_observer",
    # AGENTESEPath token
    "AGENTESEPathToken",
    "PolynomialState",
    "HoverInfo",
    "NavigationResult",
    "ContextMenuResult",
    "DragResult",
    "create_agentese_path_token",
    # TaskCheckbox token
    "TaskCheckboxToken",
    "VerificationStatus",
    "TaskHoverInfo",
    "ToggleResult",
    "TaskContextMenuResult",
    "create_task_checkbox_token",
    # Image token
    "ImageToken",
    "ImageAnalysis",
    "ImageHoverInfo",
    "ImageExpandResult",
    "ImageDragResult",
    "create_image_token",
    # CodeBlock token
    "CodeBlockToken",
    "ExecutionResult",
    "CodeBlockHoverInfo",
    "CodeBlockContextMenuResult",
    "EditFocusResult",
    "create_code_block_token",
    # PrincipleRef token
    "PrincipleRefToken",
    "PrincipleInfo",
    "PrincipleHoverInfo",
    "PrincipleNavigationResult",
    "PrincipleContextMenuResult",
    "create_principle_ref_token",
    # RequirementRef token
    "RequirementRefToken",
    "RequirementInfo",
    "RequirementHoverInfo",
    "RequirementNavigationResult",
    "RequirementContextMenuResult",
    "create_requirement_ref_token",
]
