"""
Property-Based Tests for Interactive Text System.

This module contains property-based tests that validate the correctness
properties defined in the design document. Each test is tagged with the
property number and requirements it validates.

Feature: meaning-token-frontend
Testing Framework: Hypothesis
Minimum Iterations: 100 per property
"""

from __future__ import annotations

import re
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    Observer,
    ObserverDensity,
    ObserverRole,
    TokenDefinition,
    TokenPattern,
)
from services.interactive_text.registry import (
    CORE_TOKEN_DEFINITIONS,
    TokenRegistry,
)

# =============================================================================
# Hypothesis Strategies for Token Generation
# =============================================================================


@st.composite
def agentese_path_strategy(draw: st.DrawFn) -> str:
    """Generate valid AGENTESE paths."""
    context = draw(st.sampled_from(["world", "self", "concept", "void", "time"]))
    # Generate valid identifier segments
    first_char = draw(st.sampled_from("abcdefghijklmnopqrstuvwxyz_"))
    rest_chars = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
        min_size=0,
        max_size=10,
    ))
    first_segment = first_char + rest_chars

    # Optionally add more segments
    additional_segments = draw(st.lists(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
            min_size=1,
            max_size=10,
        ).filter(lambda s: s[0].isalpha() or s[0] == "_"),
        min_size=0,
        max_size=3,
    ))

    segments = [first_segment] + additional_segments
    return f"`{context}.{'.'.join(segments)}`"


@st.composite
def task_checkbox_strategy(draw: st.DrawFn) -> str:
    """Generate valid task checkboxes."""
    checked = draw(st.sampled_from([" ", "x", "X"]))
    # Generate description without newlines
    description = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?-_",
        min_size=1,
        max_size=50,
    ))
    return f"- [{checked}] {description}\n"


@st.composite
def image_token_strategy(draw: st.DrawFn) -> str:
    """Generate valid markdown images."""
    alt_text = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        min_size=0,
        max_size=30,
    ))
    # Generate valid path without special chars
    path = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789/_.-",
        min_size=1,
        max_size=30,
    ))
    extension = draw(st.sampled_from([".png", ".jpg", ".gif", ".svg"]))
    return f"![{alt_text}]({path}{extension})"


@st.composite
def code_block_strategy(draw: st.DrawFn) -> str:
    """Generate valid fenced code blocks."""
    language = draw(st.sampled_from(["", "python", "javascript", "typescript", "rust", "go"]))
    # Generate code content without triple backticks
    code = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789(){}[].,;:=+-*/<>!@#$%^&|\\'\"\n\t",
        min_size=1,
        max_size=100,
    ).filter(lambda s: "```" not in s))
    return f"```{language}\n{code}\n```"


@st.composite
def principle_ref_strategy(draw: st.DrawFn) -> str:
    """Generate valid principle references."""
    number = draw(st.integers(min_value=1, max_value=99))
    return f"[P{number}]"


@st.composite
def requirement_ref_strategy(draw: st.DrawFn) -> str:
    """Generate valid requirement references."""
    major = draw(st.integers(min_value=1, max_value=99))
    has_minor = draw(st.booleans())
    if has_minor:
        minor = draw(st.integers(min_value=1, max_value=99))
        return f"[R{major}.{minor}]"
    return f"[R{major}]"


@st.composite
def observer_strategy(draw: st.DrawFn) -> Observer:
    """Generate valid observers with different umwelts."""
    capabilities = draw(st.frozensets(
        st.sampled_from(["llm", "verification", "network", "storage"]),
        min_size=0,
        max_size=4,
    ))
    density = draw(st.sampled_from(list(ObserverDensity)))
    role = draw(st.sampled_from(list(ObserverRole)))

    return Observer.create(
        capabilities=capabilities,
        density=density,
        role=role,
    )


@st.composite
def mixed_document_strategy(draw: st.DrawFn) -> tuple[str, dict[str, int]]:
    """Generate documents with mixed token types.
    
    Returns:
        Tuple of (document_text, expected_token_counts)
    """
    parts: list[str] = []
    counts: dict[str, int] = {
        "agentese_path": 0,
        "task_checkbox": 0,
        "image": 0,
        "code_block": 0,
        "principle_ref": 0,
        "requirement_ref": 0,
    }

    # Generate 1-5 tokens of various types
    num_tokens = draw(st.integers(min_value=1, max_value=5))

    for _ in range(num_tokens):
        token_type = draw(st.sampled_from([
            "agentese_path",
            "task_checkbox",
            "image",
            "principle_ref",
            "requirement_ref",
        ]))

        # Add some plain text before
        prefix = draw(st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz ",
            min_size=0,
            max_size=20,
        ))
        parts.append(prefix)

        if token_type == "agentese_path":
            parts.append(draw(agentese_path_strategy()))
            counts["agentese_path"] += 1
        elif token_type == "task_checkbox":
            parts.append(draw(task_checkbox_strategy()))
            counts["task_checkbox"] += 1
        elif token_type == "image":
            parts.append(draw(image_token_strategy()))
            counts["image"] += 1
        elif token_type == "principle_ref":
            parts.append(draw(principle_ref_strategy()))
            counts["principle_ref"] += 1
        elif token_type == "requirement_ref":
            parts.append(draw(requirement_ref_strategy()))
            counts["requirement_ref"] += 1

    # Add trailing text
    suffix = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ",
        min_size=0,
        max_size=20,
    ))
    parts.append(suffix)

    return "".join(parts), counts


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def clean_registry() -> None:
    """Clear registry before each test to ensure clean state."""
    TokenRegistry.clear()


# =============================================================================
# Property 1: Token Recognition Completeness
# =============================================================================


class TestProperty1TokenRecognitionCompleteness:
    """
    Property 1: Token Recognition Completeness
    
    *For any* text containing patterns matching the six core token types
    (AGENTESEPath, TaskCheckbox, Image, CodeBlock, PrincipleRef, RequirementRef),
    the parser SHALL correctly identify and extract all matching tokens with
    accurate source positions.
    
    **Validates: Requirements 1.1, 5.1, 6.1, 7.1, 8.1**
    """

    @given(path=agentese_path_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_agentese_paths_always_recognized(self, path: str) -> None:
        """
        Feature: meaning-token-frontend, Property 1: Token Recognition Completeness
        
        AGENTESE paths are always recognized when present in text.
        Validates: Requirements 1.1, 5.1
        """
        text = f"Some text {path} more text"
        matches = TokenRegistry.recognize(text)

        agentese_matches = [m for m in matches if m.definition.name == "agentese_path"]
        assert len(agentese_matches) >= 1, f"Failed to recognize AGENTESE path: {path}"

        # Verify the match contains the path
        assert any(path in m.text for m in agentese_matches)

    @given(checkbox=task_checkbox_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_task_checkboxes_always_recognized(self, checkbox: str) -> None:
        """
        Feature: meaning-token-frontend, Property 1: Token Recognition Completeness
        
        Task checkboxes are always recognized when present in text.
        Validates: Requirements 1.1, 6.1
        """
        text = f"Tasks:\n{checkbox}End of tasks"
        matches = TokenRegistry.recognize(text)

        task_matches = [m for m in matches if m.definition.name == "task_checkbox"]
        assert len(task_matches) >= 1, f"Failed to recognize task checkbox: {checkbox!r}"

    @given(image=image_token_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_images_always_recognized(self, image: str) -> None:
        """
        Feature: meaning-token-frontend, Property 1: Token Recognition Completeness
        
        Markdown images are always recognized when present in text.
        Validates: Requirements 1.1, 7.1
        """
        text = f"Here is an image: {image} and more text"
        matches = TokenRegistry.recognize(text)

        image_matches = [m for m in matches if m.definition.name == "image"]
        assert len(image_matches) >= 1, f"Failed to recognize image: {image}"

    @given(code=code_block_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_code_blocks_always_recognized(self, code: str) -> None:
        """
        Feature: meaning-token-frontend, Property 1: Token Recognition Completeness
        
        Fenced code blocks are always recognized when present in text.
        Validates: Requirements 1.1, 8.1
        """
        text = f"Code example:\n{code}\nEnd of code"
        matches = TokenRegistry.recognize(text)

        code_matches = [m for m in matches if m.definition.name == "code_block"]
        assert len(code_matches) >= 1, f"Failed to recognize code block: {code!r}"

    @given(ref=principle_ref_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_principle_refs_always_recognized(self, ref: str) -> None:
        """
        Feature: meaning-token-frontend, Property 1: Token Recognition Completeness
        
        Principle references are always recognized when present in text.
        Validates: Requirements 1.1
        """
        text = f"See principle {ref} for details"
        matches = TokenRegistry.recognize(text)

        principle_matches = [m for m in matches if m.definition.name == "principle_ref"]
        assert len(principle_matches) >= 1, f"Failed to recognize principle ref: {ref}"

    @given(ref=requirement_ref_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_requirement_refs_always_recognized(self, ref: str) -> None:
        """
        Feature: meaning-token-frontend, Property 1: Token Recognition Completeness
        
        Requirement references are always recognized when present in text.
        Validates: Requirements 1.1
        """
        text = f"See requirement {ref} for details"
        matches = TokenRegistry.recognize(text)

        req_matches = [m for m in matches if m.definition.name == "requirement_ref"]
        assert len(req_matches) >= 1, f"Failed to recognize requirement ref: {ref}"

    @given(data=mixed_document_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_mixed_tokens_all_recognized(self, data: tuple[str, dict[str, int]]) -> None:
        """
        Feature: meaning-token-frontend, Property 1: Token Recognition Completeness
        
        All token types in a mixed document are recognized.
        Validates: Requirements 1.1, 5.1, 6.1, 7.1, 8.1
        """
        text, expected_counts = data
        matches = TokenRegistry.recognize(text)

        # Count matches by type
        actual_counts: dict[str, int] = {}
        for match in matches:
            name = match.definition.name
            actual_counts[name] = actual_counts.get(name, 0) + 1

        # Verify each expected token type was found
        for token_type, expected in expected_counts.items():
            if expected > 0:
                actual = actual_counts.get(token_type, 0)
                assert actual >= expected, (
                    f"Expected at least {expected} {token_type} tokens, "
                    f"found {actual} in: {text!r}"
                )

    @given(text=st.text(min_size=0, max_size=500))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_source_positions_accurate(self, text: str) -> None:
        """
        Feature: meaning-token-frontend, Property 1: Token Recognition Completeness
        
        All recognized tokens have accurate source positions.
        Validates: Requirements 1.1
        """
        matches = TokenRegistry.recognize(text)

        for match in matches:
            # Position must be within text bounds
            assert 0 <= match.start <= len(text), f"Start position out of bounds: {match.start}"
            assert 0 <= match.end <= len(text), f"End position out of bounds: {match.end}"
            assert match.start <= match.end, f"Start > end: {match.start} > {match.end}"

            # Matched text must equal substring at position
            if match.start < match.end:
                expected_text = text[match.start:match.end]
                assert match.text == expected_text, (
                    f"Position mismatch: match.text={match.text!r}, "
                    f"text[{match.start}:{match.end}]={expected_text!r}"
                )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TestProperty1TokenRecognitionCompleteness",
    # Strategies for use in other test modules
    "agentese_path_strategy",
    "task_checkbox_strategy",
    "image_token_strategy",
    "code_block_strategy",
    "principle_ref_strategy",
    "requirement_ref_strategy",
    "observer_strategy",
    "mixed_document_strategy",
]



# =============================================================================
# Property 10: AGENTESE Path Affordances
# =============================================================================


class TestProperty10AGENTESEPathAffordances:
    """
    Property 10: AGENTESE Path Affordances
    
    *For any* recognized AGENTESE path token, hover SHALL return polynomial
    state information, click SHALL produce navigation action, right-click
    SHALL produce context menu, and drag SHALL produce REPL pre-fill.
    
    **Validates: Requirements 5.2, 5.3, 5.4, 5.5**
    """

    @given(path=agentese_path_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_hover_returns_polynomial_state(
        self, path: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 10: AGENTESE Path Affordances
        
        Hover on AGENTESE path returns polynomial state information.
        Validates: Requirements 5.2
        """
        from services.interactive_text.tokens.agentese_path import (
            AGENTESEPathToken,
            HoverInfo,
            PolynomialState,
        )

        # Create token from path
        token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=True,
        )

        result = await token.on_interact(AffordanceAction.HOVER, observer)

        assert result.success is True
        assert isinstance(result.data, HoverInfo)
        assert result.data.title == path.strip("`")
        assert isinstance(result.data.content, PolynomialState)

    @given(path=agentese_path_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_click_produces_navigation(
        self, path: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 10: AGENTESE Path Affordances
        
        Click on AGENTESE path produces navigation action.
        Validates: Requirements 5.3
        """
        from services.interactive_text.tokens.agentese_path import (
            AGENTESEPathToken,
            NavigationResult,
        )

        token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=True,
        )

        result = await token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is True
        assert isinstance(result.data, NavigationResult)
        assert result.data.path == path.strip("`")

    @given(path=agentese_path_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_right_click_produces_context_menu(
        self, path: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 10: AGENTESE Path Affordances
        
        Right-click on AGENTESE path produces context menu.
        Validates: Requirements 5.4
        """
        from services.interactive_text.tokens.agentese_path import (
            AGENTESEPathToken,
            ContextMenuResult,
        )

        token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=True,
        )

        result = await token.on_interact(AffordanceAction.RIGHT_CLICK, observer)

        assert result.success is True
        assert isinstance(result.data, ContextMenuResult)
        assert result.data.path == path.strip("`")
        assert len(result.data.options) > 0

    @given(path=agentese_path_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_drag_produces_repl_prefill(
        self, path: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 10: AGENTESE Path Affordances
        
        Drag on AGENTESE path produces REPL pre-fill.
        Validates: Requirements 5.5
        """
        from services.interactive_text.tokens.agentese_path import (
            AGENTESEPathToken,
            DragResult,
        )

        token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=True,
        )

        result = await token.on_interact(AffordanceAction.DRAG, observer)

        assert result.success is True
        assert isinstance(result.data, DragResult)
        assert result.data.path == path.strip("`")
        assert path.strip("`") in result.data.template


# =============================================================================
# Property 11: Ghost Token Rendering
# =============================================================================


class TestProperty11GhostTokenRendering:
    """
    Property 11: Ghost Token Rendering
    
    *For any* AGENTESE path token referencing a non-existent node, the system
    SHALL render it as a ghost token with reduced affordances. Ghost tokens
    should still be recognizable but indicate their non-existent status.
    
    **Validates: Requirements 5.6**
    """

    @given(path=agentese_path_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_ghost_token_has_reduced_affordances(
        self, path: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 11: Ghost Token Rendering
        
        Ghost tokens (non-existent paths) have reduced affordances compared to existing paths.
        Validates: Requirements 5.6
        """
        from services.interactive_text.tokens.agentese_path import AGENTESEPathToken

        # Create existing token
        existing_token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=True,
        )

        # Create ghost token (non-existent)
        ghost_token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=False,
        )

        existing_affordances = await existing_token.get_affordances(observer)
        ghost_affordances = await ghost_token.get_affordances(observer)

        # Ghost tokens should have fewer or equal affordances
        assert len(ghost_affordances) <= len(existing_affordances), (
            f"Ghost token has more affordances ({len(ghost_affordances)}) "
            f"than existing token ({len(existing_affordances)})"
        )

    @given(path=agentese_path_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_ghost_token_is_identifiable(
        self, path: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 11: Ghost Token Rendering
        
        Ghost tokens are identifiable as non-existent.
        Validates: Requirements 5.6
        """
        from services.interactive_text.tokens.agentese_path import AGENTESEPathToken

        ghost_token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=False,
        )

        # Ghost token should be identifiable
        assert ghost_token.exists is False
        assert ghost_token.is_ghost is True

    @given(path=agentese_path_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_ghost_token_hover_indicates_non_existence(
        self, path: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 11: Ghost Token Rendering
        
        Hovering a ghost token indicates the path does not exist.
        Validates: Requirements 5.6
        """
        from services.interactive_text.tokens.agentese_path import (
            AGENTESEPathToken,
            HoverInfo,
        )

        ghost_token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=False,
        )

        result = await ghost_token.on_interact(AffordanceAction.HOVER, observer)

        assert result.success is True
        assert isinstance(result.data, HoverInfo)
        # Hover info should indicate ghost status
        assert result.data.is_ghost is True

    @given(path=agentese_path_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_ghost_token_click_offers_creation(
        self, path: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 11: Ghost Token Rendering
        
        Clicking a ghost token offers to create the path.
        Validates: Requirements 5.6
        """
        from services.interactive_text.tokens.agentese_path import (
            AGENTESEPathToken,
            NavigationResult,
        )

        ghost_token = AGENTESEPathToken(
            source_text=path,
            source_position=(0, len(path)),
            path=path.strip("`"),
            exists=False,
        )

        result = await ghost_token.on_interact(AffordanceAction.CLICK, observer)

        # Click on ghost should still succeed but indicate ghost status
        assert result.success is True
        assert isinstance(result.data, NavigationResult)
        assert result.data.is_ghost is True
        # Should offer creation option
        assert result.data.can_create is True


__all__ = [
    "TestProperty1TokenRecognitionCompleteness",
    "TestProperty10AGENTESEPathAffordances",
    "TestProperty11GhostTokenRendering",
    "TestProperty12TaskCheckboxToggleWithTrace",
    # Strategies for use in other test modules
    "agentese_path_strategy",
    "task_checkbox_strategy",
    "image_token_strategy",
    "code_block_strategy",
    "principle_ref_strategy",
    "requirement_ref_strategy",
    "observer_strategy",
    "mixed_document_strategy",
]


# =============================================================================
# Property 12: Task Checkbox Toggle with Trace
# =============================================================================


class TestProperty12TaskCheckboxToggleWithTrace:
    """
    Property 12: Task Checkbox Toggle with Trace
    
    *For any* task checkbox toggle, the system SHALL capture a Trace_Witness
    with constructive proof, toggle the state, and persist to the source file.
    
    **Validates: Requirements 6.2, 6.3, 12.1**
    """

    @given(checkbox=task_checkbox_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_toggle_changes_state(
        self, checkbox: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 12: Task Checkbox Toggle with Trace
        
        Toggling a task checkbox changes its state.
        Validates: Requirements 6.2
        """
        from services.interactive_text.tokens.task_checkbox import (
            TaskCheckboxToken,
            ToggleResult,
        )

        # Parse the checkbox
        match = TaskCheckboxToken.PATTERN.search(checkbox)
        if match is None:
            return  # Skip invalid checkboxes

        token = TaskCheckboxToken.from_match(match)
        original_state = token.checked

        result = await token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is True
        assert isinstance(result.data, ToggleResult)
        assert result.data.new_state != original_state

    @given(checkbox=task_checkbox_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_toggle_captures_trace_witness(
        self, checkbox: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 12: Task Checkbox Toggle with Trace
        
        Toggling a task checkbox captures a Trace_Witness.
        Validates: Requirements 6.3, 12.1
        """
        from services.interactive_text.tokens.base import TraceWitness
        from services.interactive_text.tokens.task_checkbox import (
            TaskCheckboxToken,
            ToggleResult,
        )

        match = TaskCheckboxToken.PATTERN.search(checkbox)
        if match is None:
            return

        token = TaskCheckboxToken.from_match(match)

        result = await token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is True
        assert isinstance(result.data, ToggleResult)
        assert result.data.trace_witness is not None
        assert isinstance(result.data.trace_witness, TraceWitness)

    @given(checkbox=task_checkbox_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_trace_witness_contains_action_data(
        self, checkbox: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 12: Task Checkbox Toggle with Trace
        
        Trace witness contains action data for verification.
        Validates: Requirements 6.3, 12.1
        """
        from services.interactive_text.tokens.task_checkbox import (
            TaskCheckboxToken,
            ToggleResult,
        )

        match = TaskCheckboxToken.PATTERN.search(checkbox)
        if match is None:
            return

        token = TaskCheckboxToken.from_match(match)
        original_state = token.checked

        result = await token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is True
        witness = result.data.trace_witness
        assert witness is not None

        # Trace should contain action data
        trace = witness.trace
        assert trace.operation == "toggle"
        assert trace.input_data["previous_state"] == original_state
        assert trace.output_data["new_state"] != original_state
        assert trace.observer_id == observer.id

    @given(observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_toggle_with_file_path_updates_file(
        self, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 12: Task Checkbox Toggle with Trace
        
        Toggling a task with file_path indicates file update.
        Validates: Requirements 6.2
        """
        from services.interactive_text.tokens.task_checkbox import (
            TaskCheckboxToken,
            ToggleResult,
        )

        # Create token with file path
        token = TaskCheckboxToken(
            source_text="- [ ] Test task",
            source_position=(0, 15),
            checked=False,
            description="Test task",
            file_path="/path/to/file.md",
            line_number=1,
        )

        result = await token.on_interact(AffordanceAction.CLICK, observer)

        assert result.success is True
        assert isinstance(result.data, ToggleResult)
        assert result.data.file_updated is True



# =============================================================================
# Property 14: Image Token Graceful Degradation
# =============================================================================


class TestProperty14ImageTokenGracefulDegradation:
    """
    Property 14: Image Token Graceful Degradation
    
    *For any* image token, when LLM is unavailable, the system SHALL display
    the image without analysis and show "requires connection" tooltip.
    
    **Validates: Requirements 7.2, 7.5, 14.1**
    """

    @given(image=image_token_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_image_hover_without_llm_indicates_requires_connection(
        self, image: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 14: Image Token Graceful Degradation
        
        Hovering an image without LLM capability indicates requires connection.
        Validates: Requirements 7.2, 7.5
        """
        from services.interactive_text.tokens.image import (
            ImageHoverInfo,
            ImageToken,
        )

        match = ImageToken.PATTERN.search(image)
        if match is None:
            return

        # Create token with LLM unavailable
        token = ImageToken.from_match(match, llm_available=False)

        # Create observer without LLM capability
        observer_no_llm = Observer.create(
            capabilities=frozenset(),  # No LLM
            density=observer.density,
            role=observer.role,
        )

        result = await token.on_interact(AffordanceAction.HOVER, observer_no_llm)

        assert result.success is True
        assert isinstance(result.data, ImageHoverInfo)
        assert result.data.requires_connection is True
        assert result.data.analysis is None

    @given(image=image_token_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_image_hover_with_llm_provides_analysis(
        self, image: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 14: Image Token Graceful Degradation
        
        Hovering an image with LLM capability provides analysis.
        Validates: Requirements 7.2
        """
        from services.interactive_text.tokens.image import (
            ImageAnalysis,
            ImageHoverInfo,
            ImageToken,
        )

        match = ImageToken.PATTERN.search(image)
        if match is None:
            return

        # Create token with LLM available
        token = ImageToken.from_match(match, llm_available=True)

        # Create observer with LLM capability
        observer_with_llm = Observer.create(
            capabilities=frozenset(["llm"]),
            density=observer.density,
            role=observer.role,
        )

        result = await token.on_interact(AffordanceAction.HOVER, observer_with_llm)

        assert result.success is True
        assert isinstance(result.data, ImageHoverInfo)
        assert result.data.requires_connection is False
        assert result.data.analysis is not None
        assert isinstance(result.data.analysis, ImageAnalysis)

    @given(image=image_token_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_image_still_displays_without_llm(
        self, image: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 14: Image Token Graceful Degradation
        
        Images still display and can be interacted with without LLM.
        Validates: Requirements 7.5, 14.1
        """
        from services.interactive_text.tokens.image import (
            ImageHoverInfo,
            ImageToken,
        )

        match = ImageToken.PATTERN.search(image)
        if match is None:
            return

        # Create token with LLM unavailable
        token = ImageToken.from_match(match, llm_available=False)

        # Observer without LLM
        observer_no_llm = Observer.create(
            capabilities=frozenset(),
            density=observer.density,
            role=observer.role,
        )

        # Hover should still work
        result = await token.on_interact(AffordanceAction.HOVER, observer_no_llm)
        assert result.success is True

        # Should still have alt_text and path
        assert result.data.alt_text is not None
        assert result.data.path is not None

    @given(image=image_token_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_image_drag_works_without_llm(
        self, image: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 14: Image Token Graceful Degradation
        
        Dragging images to context works without LLM.
        Validates: Requirements 7.4, 14.1
        """
        from services.interactive_text.tokens.image import (
            ImageDragResult,
            ImageToken,
        )

        match = ImageToken.PATTERN.search(image)
        if match is None:
            return

        # Create token with LLM unavailable
        token = ImageToken.from_match(match, llm_available=False)

        result = await token.on_interact(AffordanceAction.DRAG, observer)

        assert result.success is True
        assert isinstance(result.data, ImageDragResult)
        assert result.data.context_added is True



# =============================================================================
# Property 15: Code Block Execution Sandboxing
# =============================================================================


class TestProperty15CodeBlockExecutionSandboxing:
    """
    Property 15: Code Block Execution Sandboxing
    
    *For any* code block execution, the system SHALL run in a sandboxed
    environment, capture AGENTESE invocation traces, and display output.
    
    **Validates: Requirements 8.3, 8.4, 8.6**
    """

    @given(code=code_block_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_code_block_execution_is_sandboxed(
        self, code: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 15: Code Block Execution Sandboxing
        
        Code block execution is sandboxed by default.
        Validates: Requirements 8.3
        """
        from services.interactive_text.tokens.code_block import (
            CodeBlockHoverInfo,
            CodeBlockToken,
        )

        match = CodeBlockToken.PATTERN.search(code)
        if match is None:
            return

        token = CodeBlockToken.from_match(match)

        # Hover should indicate sandboxed execution
        result = await token.on_interact(AffordanceAction.HOVER, observer)

        assert result.success is True
        assert isinstance(result.data, CodeBlockHoverInfo)
        assert result.data.is_sandboxed is True

    @given(observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_code_block_captures_agentese_traces(
        self, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 15: Code Block Execution Sandboxing
        
        Code block execution captures AGENTESE invocation traces.
        Validates: Requirements 8.6
        """
        from services.interactive_text.tokens.code_block import (
            CodeBlockToken,
            ExecutionResult,
        )

        # Create code block with AGENTESE invocations
        code_with_agentese = '''```python
result = world.town.citizen.greet("Hello")
data = self.memory.recall("test")
```'''

        match = CodeBlockToken.PATTERN.search(code_with_agentese)
        assert match is not None

        token = CodeBlockToken.from_match(match)

        # Execute the code
        result = await token.execute(observer, sandboxed=True)

        assert result.success is True
        assert isinstance(result, ExecutionResult)
        # Should have captured traces for AGENTESE invocations
        assert len(result.traces) >= 2  # world.town.citizen.greet and self.memory.recall

    @given(observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_code_block_execution_returns_output(
        self, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 15: Code Block Execution Sandboxing
        
        Code block execution returns output.
        Validates: Requirements 8.4
        """
        from services.interactive_text.tokens.code_block import (
            CodeBlockToken,
            ExecutionResult,
        )

        code = '''```python
print("Hello, World!")
```'''

        match = CodeBlockToken.PATTERN.search(code)
        assert match is not None

        token = CodeBlockToken.from_match(match)

        result = await token.execute(observer, sandboxed=True)

        assert result.success is True
        assert isinstance(result, ExecutionResult)
        assert result.output is not None
        assert len(result.output) > 0

    @given(observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_non_executable_language_fails_gracefully(
        self, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 15: Code Block Execution Sandboxing
        
        Non-executable languages fail gracefully.
        Validates: Requirements 8.3
        """
        from services.interactive_text.tokens.code_block import (
            CodeBlockToken,
            ExecutionResult,
        )

        # Create code block with non-executable language
        code = '''```markdown
# This is markdown
Not executable
```'''

        match = CodeBlockToken.PATTERN.search(code)
        assert match is not None

        token = CodeBlockToken.from_match(match)

        # Should not be executable
        assert token.can_execute is False

        # Execution should fail gracefully
        result = await token.execute(observer, sandboxed=True)

        assert result.success is False
        assert result.error is not None
        assert "not executable" in result.error.lower()

    @given(code=code_block_strategy(), observer=observer_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_code_block_context_menu_shows_run_option(
        self, code: str, observer: Observer
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 15: Code Block Execution Sandboxing
        
        Context menu shows run option for executable languages.
        Validates: Requirements 8.3
        """
        from services.interactive_text.tokens.code_block import (
            CodeBlockContextMenuResult,
            CodeBlockToken,
        )

        match = CodeBlockToken.PATTERN.search(code)
        if match is None:
            return

        token = CodeBlockToken.from_match(match)

        result = await token.on_interact(AffordanceAction.RIGHT_CLICK, observer)

        assert result.success is True
        assert isinstance(result.data, CodeBlockContextMenuResult)

        # If executable, should have run option
        if token.can_execute:
            run_options = [o for o in result.data.options if o["action"] == "run"]
            assert len(run_options) > 0


# =============================================================================
# Property 6: Document Polynomial State Validity
# =============================================================================

# Import DocumentState for the polynomial tests
from services.interactive_text.contracts import DocumentState


class TestProperty6DocumentPolynomialStateValidity:
    """
    Property 6: Document Polynomial State Validity
    
    *For any* document state and valid input, the polynomial SHALL produce
    a deterministic transition to a valid state with appropriate output.
    The polynomial implements four positions (VIEWING, EDITING, SYNCING,
    CONFLICTING) with state-dependent valid inputs.
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
    """

    @given(st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_all_states_have_valid_directions(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        All states have at least one valid input direction.
        Validates: Requirements 3.1
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        directions = DocumentPolynomial.directions(state)

        assert len(directions) > 0, f"State {state} has no valid directions"
        assert isinstance(directions, frozenset)

    @given(st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_viewing_state_accepts_correct_inputs(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        VIEWING state accepts: edit, refresh, hover, click, drag.
        Validates: Requirements 3.2
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        if state != DocumentState.VIEWING:
            return

        expected_inputs = {"edit", "refresh", "hover", "click", "drag"}
        actual_inputs = DocumentPolynomial.directions(state)

        assert actual_inputs == expected_inputs, (
            f"VIEWING state should accept {expected_inputs}, got {actual_inputs}"
        )

    @given(st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_editing_state_accepts_correct_inputs(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        EDITING state accepts: save, cancel, continue_edit, hover.
        Validates: Requirements 3.3
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        if state != DocumentState.EDITING:
            return

        expected_inputs = {"save", "cancel", "continue_edit", "hover"}
        actual_inputs = DocumentPolynomial.directions(state)

        assert actual_inputs == expected_inputs, (
            f"EDITING state should accept {expected_inputs}, got {actual_inputs}"
        )

    @given(st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_syncing_state_accepts_correct_inputs(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        SYNCING state accepts: wait, force_local, force_remote.
        Validates: Requirements 3.4
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        if state != DocumentState.SYNCING:
            return

        expected_inputs = {"wait", "force_local", "force_remote"}
        actual_inputs = DocumentPolynomial.directions(state)

        assert actual_inputs == expected_inputs, (
            f"SYNCING state should accept {expected_inputs}, got {actual_inputs}"
        )

    @given(st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_conflicting_state_accepts_correct_inputs(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        CONFLICTING state accepts: resolve, abort, view_diff.
        Validates: Requirements 3.5
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        if state != DocumentState.CONFLICTING:
            return

        expected_inputs = {"resolve", "abort", "view_diff"}
        actual_inputs = DocumentPolynomial.directions(state)

        assert actual_inputs == expected_inputs, (
            f"CONFLICTING state should accept {expected_inputs}, got {actual_inputs}"
        )

    @given(
        state=st.sampled_from(list(DocumentState)),
        input_action=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz_"),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_transitions_are_deterministic(
        self, state: DocumentState, input_action: str
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        Same (state, input) always produces same (new_state, output_type).
        Validates: Requirements 3.1
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        result1 = DocumentPolynomial.transition(state, input_action)
        result2 = DocumentPolynomial.transition(state, input_action)

        # Same new state
        assert result1[0] == result2[0], (
            f"Non-deterministic state: {result1[0]} != {result2[0]}"
        )

        # Same output type
        assert type(result1[1]) == type(result2[1]), (
            f"Non-deterministic output type: {type(result1[1])} != {type(result2[1])}"
        )

    @given(state=st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_valid_inputs_produce_valid_transitions(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        Valid inputs always produce valid state transitions (not NoOp).
        Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5
        """
        from services.interactive_text.polynomial import DocumentPolynomial, NoOp

        for input_action in DocumentPolynomial.directions(state):
            new_state, output = DocumentPolynomial.transition(state, input_action)

            # Should not be NoOp for valid inputs
            assert not isinstance(output, NoOp), (
                f"Valid input '{input_action}' for state {state} produced NoOp"
            )

            # New state should be a valid state
            assert new_state in DocumentPolynomial.positions, (
                f"Transition produced invalid state: {new_state}"
            )

    @given(
        state=st.sampled_from(list(DocumentState)),
        invalid_input=st.text(min_size=1, max_size=20, alphabet="0123456789"),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_invalid_inputs_produce_noop(
        self, state: DocumentState, invalid_input: str
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        Invalid inputs produce NoOp and preserve state.
        Validates: Requirements 3.1
        """
        from services.interactive_text.polynomial import DocumentPolynomial, NoOp

        # Numeric strings are never valid inputs
        new_state, output = DocumentPolynomial.transition(state, invalid_input)

        # Should be NoOp
        assert isinstance(output, NoOp), (
            f"Invalid input '{invalid_input}' should produce NoOp, got {type(output)}"
        )

        # State should be preserved
        assert new_state == state, (
            f"Invalid input should preserve state, got {new_state} instead of {state}"
        )

    def test_polynomial_laws_hold(self) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        Polynomial laws (determinism, completeness, closure) all hold.
        Validates: Requirements 3.1
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        assert DocumentPolynomial.verify_laws() is True

    def test_all_four_states_exist(self) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        All four states (VIEWING, EDITING, SYNCING, CONFLICTING) exist.
        Validates: Requirements 3.1
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        assert DocumentState.VIEWING in DocumentPolynomial.positions
        assert DocumentState.EDITING in DocumentPolynomial.positions
        assert DocumentState.SYNCING in DocumentPolynomial.positions
        assert DocumentState.CONFLICTING in DocumentPolynomial.positions
        assert len(DocumentPolynomial.positions) == 4

    @given(state=st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_transition_outputs_are_serializable(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 6: Document Polynomial State Validity
        
        All transition outputs can be serialized to dict.
        Validates: Requirements 3.1
        """
        from services.interactive_text.polynomial import DocumentPolynomial

        for input_action in DocumentPolynomial.directions(state):
            _, output = DocumentPolynomial.transition(state, input_action)

            # Should be serializable
            output_dict = output.to_dict()
            assert isinstance(output_dict, dict)
            assert "output_type" in output_dict



# =============================================================================
# Property 7: Document Polynomial Event Emission
# =============================================================================


class TestProperty7DocumentPolynomialEventEmission:
    """
    Property 7: Document Polynomial Event Emission
    
    *For any* valid state transition in the Document Polynomial, the system
    SHALL emit a corresponding event through the DataBus. Events must contain
    the previous state, new state, input action, and transition output.
    
    **Validates: Requirements 3.6, 11.1**
    """

    @pytest.fixture(autouse=True)
    def reset_event_bus(self) -> None:
        """Reset the event bus before each test."""
        from services.interactive_text.events import reset_document_event_bus
        reset_document_event_bus()

    @given(state=st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_valid_transitions_emit_events(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 7: Document Polynomial Event Emission
        
        Valid state transitions emit events through the event bus.
        Validates: Requirements 3.6, 11.1
        """
        from services.interactive_text.events import (
            DocumentEvent,
            DocumentEventBus,
            EventEmittingPolynomial,
        )
        from services.interactive_text.polynomial import DocumentPolynomial

        bus = DocumentEventBus()
        poly = EventEmittingPolynomial(bus, document_path="/test/doc.md")

        # Track emitted events
        emitted_events: list[DocumentEvent] = []

        async def handler(event: DocumentEvent) -> None:
            emitted_events.append(event)

        bus.subscribe_all(handler)

        # Perform all valid transitions for this state
        for input_action in DocumentPolynomial.directions(state):
            emitted_events.clear()

            new_state, output, event = await poly.transition(state, input_action)

            # Wait for async handlers
            await asyncio.sleep(0.01)

            # Should have emitted exactly one event
            assert len(emitted_events) == 1, (
                f"Expected 1 event for {state} + {input_action}, got {len(emitted_events)}"
            )

            # Event should match the transition
            emitted = emitted_events[0]
            assert emitted.previous_state == state
            assert emitted.new_state == new_state
            assert emitted.input_action == input_action

    @given(state=st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_events_contain_required_fields(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 7: Document Polynomial Event Emission
        
        Emitted events contain all required fields.
        Validates: Requirements 3.6, 11.1
        """
        from services.interactive_text.events import (
            DocumentEvent,
            DocumentEventBus,
            EventEmittingPolynomial,
        )
        from services.interactive_text.polynomial import DocumentPolynomial

        bus = DocumentEventBus()
        poly = EventEmittingPolynomial(bus, document_path="/test/doc.md")

        emitted_events: list[DocumentEvent] = []

        async def handler(event: DocumentEvent) -> None:
            emitted_events.append(event)

        bus.subscribe_all(handler)

        # Get first valid input for this state
        valid_inputs = list(DocumentPolynomial.directions(state))
        if not valid_inputs:
            return

        input_action = valid_inputs[0]
        await poly.transition(state, input_action)
        await asyncio.sleep(0.01)

        assert len(emitted_events) == 1
        event = emitted_events[0]

        # Check required fields
        assert event.event_id is not None
        assert len(event.event_id) > 0
        assert event.event_type is not None
        assert event.previous_state is not None
        assert event.new_state is not None
        assert event.input_action is not None
        assert event.output is not None
        assert isinstance(event.output, dict)
        assert event.timestamp > 0
        assert event.source == "document_polynomial"

    @given(state=st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_events_have_correct_event_type(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 7: Document Polynomial Event Emission
        
        Events have the correct event type for the transition.
        Validates: Requirements 3.6
        """
        from services.interactive_text.events import (
            DocumentEvent,
            DocumentEventBus,
            DocumentEventType,
            EventEmittingPolynomial,
        )
        from services.interactive_text.polynomial import DocumentPolynomial

        bus = DocumentEventBus()
        poly = EventEmittingPolynomial(bus, document_path="/test/doc.md")

        emitted_events: list[DocumentEvent] = []

        async def handler(event: DocumentEvent) -> None:
            emitted_events.append(event)

        bus.subscribe_all(handler)

        for input_action in DocumentPolynomial.directions(state):
            emitted_events.clear()

            await poly.transition(state, input_action)
            await asyncio.sleep(0.01)

            assert len(emitted_events) == 1
            event = emitted_events[0]

            # Event type should be a valid DocumentEventType
            assert isinstance(event.event_type, DocumentEventType)

            # Event type should not be STATE_CHANGED for known transitions
            # (STATE_CHANGED is fallback for unknown transitions)
            if (state, input_action) in [
                (DocumentState.VIEWING, "edit"),
                (DocumentState.VIEWING, "refresh"),
                (DocumentState.EDITING, "save"),
                (DocumentState.EDITING, "cancel"),
            ]:
                assert event.event_type != DocumentEventType.STATE_CHANGED

    @given(state=st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_events_maintain_causal_ordering(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 7: Document Polynomial Event Emission
        
        Sequential events maintain causal ordering through causal_parent.
        Validates: Requirements 11.1
        """
        from services.interactive_text.events import (
            DocumentEvent,
            DocumentEventBus,
            EventEmittingPolynomial,
        )
        from services.interactive_text.polynomial import DocumentPolynomial

        bus = DocumentEventBus()
        poly = EventEmittingPolynomial(bus, document_path="/test/doc.md")

        emitted_events: list[DocumentEvent] = []

        async def handler(event: DocumentEvent) -> None:
            emitted_events.append(event)

        bus.subscribe_all(handler)

        # Perform multiple transitions
        current_state = state
        for _ in range(3):
            valid_inputs = list(DocumentPolynomial.directions(current_state))
            if not valid_inputs:
                break

            input_action = valid_inputs[0]
            new_state, _, _ = await poly.transition(current_state, input_action)
            current_state = new_state

        await asyncio.sleep(0.01)

        # Check causal ordering
        if len(emitted_events) >= 2:
            for i in range(1, len(emitted_events)):
                # Each event (except first) should have causal_parent
                # pointing to the previous event
                assert emitted_events[i].causal_parent == emitted_events[i - 1].event_id, (
                    f"Event {i} causal_parent mismatch: "
                    f"expected {emitted_events[i - 1].event_id}, "
                    f"got {emitted_events[i].causal_parent}"
                )

    @given(state=st.sampled_from(list(DocumentState)))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_events_are_serializable(self, state: DocumentState) -> None:
        """
        Feature: meaning-token-frontend, Property 7: Document Polynomial Event Emission
        
        All emitted events can be serialized to dict.
        Validates: Requirements 3.6
        """
        from services.interactive_text.events import (
            DocumentEvent,
            DocumentEventBus,
            EventEmittingPolynomial,
        )
        from services.interactive_text.polynomial import DocumentPolynomial

        bus = DocumentEventBus()
        poly = EventEmittingPolynomial(bus, document_path="/test/doc.md")

        emitted_events: list[DocumentEvent] = []

        async def handler(event: DocumentEvent) -> None:
            emitted_events.append(event)

        bus.subscribe_all(handler)

        for input_action in DocumentPolynomial.directions(state):
            emitted_events.clear()

            await poly.transition(state, input_action)
            await asyncio.sleep(0.01)

            assert len(emitted_events) == 1
            event = emitted_events[0]

            # Should be serializable
            event_dict = event.to_dict()
            assert isinstance(event_dict, dict)
            assert "event_id" in event_dict
            assert "event_type" in event_dict
            assert "previous_state" in event_dict
            assert "new_state" in event_dict
            assert "input_action" in event_dict
            assert "output" in event_dict
            assert "timestamp" in event_dict

    @given(
        event_type=st.sampled_from([
            "EDIT_STARTED",
            "SAVE_REQUESTED",
            "SYNC_COMPLETED",
            "CONFLICT_RESOLVED",
        ])
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_subscribers_receive_filtered_events(self, event_type: str) -> None:
        """
        Feature: meaning-token-frontend, Property 7: Document Polynomial Event Emission
        
        Subscribers can filter events by type.
        Validates: Requirements 11.1
        """
        from services.interactive_text.events import (
            DocumentEvent,
            DocumentEventBus,
            DocumentEventType,
            EventEmittingPolynomial,
        )

        bus = DocumentEventBus()
        poly = EventEmittingPolynomial(bus, document_path="/test/doc.md")

        target_type = DocumentEventType[event_type]
        filtered_events: list[DocumentEvent] = []
        all_events: list[DocumentEvent] = []

        async def filtered_handler(event: DocumentEvent) -> None:
            filtered_events.append(event)

        async def all_handler(event: DocumentEvent) -> None:
            all_events.append(event)

        bus.subscribe(target_type, filtered_handler)
        bus.subscribe_all(all_handler)

        # Perform the transition that produces this event type
        if event_type == "EDIT_STARTED":
            await poly.transition(DocumentState.VIEWING, "edit")
        elif event_type == "SAVE_REQUESTED":
            await poly.transition(DocumentState.EDITING, "save")
        elif event_type == "SYNC_COMPLETED":
            await poly.transition(DocumentState.SYNCING, "wait")
        elif event_type == "CONFLICT_RESOLVED":
            await poly.transition(DocumentState.CONFLICTING, "resolve")

        await asyncio.sleep(0.01)

        # All handler should receive the event
        assert len(all_events) == 1

        # Filtered handler should receive only matching events
        assert len(filtered_events) == 1
        assert filtered_events[0].event_type == target_type

    @pytest.mark.asyncio
    async def test_event_bus_stats_track_emissions(self) -> None:
        """
        Feature: meaning-token-frontend, Property 7: Document Polynomial Event Emission
        
        Event bus statistics track emissions correctly.
        Validates: Requirements 11.1
        """
        from services.interactive_text.events import (
            DocumentEventBus,
            EventEmittingPolynomial,
        )

        bus = DocumentEventBus()
        poly = EventEmittingPolynomial(bus, document_path="/test/doc.md")

        initial_stats = bus.stats
        assert initial_stats["total_emitted"] == 0

        # Perform some transitions
        await poly.transition(DocumentState.VIEWING, "edit")
        await poly.transition(DocumentState.EDITING, "save")
        await poly.transition(DocumentState.SYNCING, "wait")

        await asyncio.sleep(0.01)

        final_stats = bus.stats
        assert final_stats["total_emitted"] == 3
        assert final_stats["buffer_size"] == 3


# Import asyncio for the tests
import asyncio

# =============================================================================
# Property 8: Document Sheaf Coherence
# =============================================================================


@st.composite
def token_state_strategy(draw: st.DrawFn) -> "TokenState":
    """Generate valid token states."""
    from services.interactive_text.sheaf import TokenState

    token_type = draw(st.sampled_from([
        "agentese_path", "task_checkbox", "image", "code_block",
        "principle_ref", "requirement_ref",
    ]))

    # Generate unique token ID
    token_id = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
        min_size=8,
        max_size=16,
    ))

    # Generate content based on type
    content = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-",
        min_size=1,
        max_size=50,
    ))

    # Generate valid position
    start = draw(st.integers(min_value=0, max_value=1000))
    length = draw(st.integers(min_value=1, max_value=100))

    return TokenState(
        token_id=token_id,
        token_type=token_type,
        content=content,
        position=(start, start + length),
    )


@st.composite
def document_view_strategy(
    draw: st.DrawFn,
    document_path: str = "/test/document.md",
) -> "SimpleDocumentView":
    """Generate valid document views with tokens."""
    from pathlib import Path

    from services.interactive_text.sheaf import SimpleDocumentView, TokenState

    # Generate 0-5 tokens
    num_tokens = draw(st.integers(min_value=0, max_value=5))
    tokens = [draw(token_state_strategy()) for _ in range(num_tokens)]

    return SimpleDocumentView.create(
        document_path=Path(document_path),
        tokens=tokens,
    )


@st.composite
def compatible_views_strategy(draw: st.DrawFn) -> tuple["SimpleDocumentView", "SimpleDocumentView"]:
    """Generate two compatible views (agree on overlapping tokens).
    
    Key insight: We must ensure that:
    1. Shared tokens are the SAME object instances in both views
    2. Unique tokens have IDs that don't collide with shared or each other
    """
    from pathlib import Path

    from services.interactive_text.sheaf import SimpleDocumentView, TokenState

    document_path = Path("/test/document.md")

    # Generate shared tokens with prefix to avoid collisions
    num_shared = draw(st.integers(min_value=0, max_value=3))
    shared_tokens: list[TokenState] = []
    for i in range(num_shared):
        base = draw(token_state_strategy())
        # Use prefixed ID to ensure uniqueness
        shared_tokens.append(TokenState(
            token_id=f"shared_{i}_{base.token_id}",
            token_type=base.token_type,
            content=base.content,
            position=base.position,
        ))

    # Generate unique tokens for view 1 with distinct prefix
    num_unique_v1 = draw(st.integers(min_value=0, max_value=3))
    unique_v1: list[TokenState] = []
    for i in range(num_unique_v1):
        base = draw(token_state_strategy())
        unique_v1.append(TokenState(
            token_id=f"v1_unique_{i}_{base.token_id}",
            token_type=base.token_type,
            content=base.content,
            position=base.position,
        ))

    # Generate unique tokens for view 2 with distinct prefix
    num_unique_v2 = draw(st.integers(min_value=0, max_value=3))
    unique_v2: list[TokenState] = []
    for i in range(num_unique_v2):
        base = draw(token_state_strategy())
        unique_v2.append(TokenState(
            token_id=f"v2_unique_{i}_{base.token_id}",
            token_type=base.token_type,
            content=base.content,
            position=base.position,
        ))

    # Create views with shared tokens having SAME state (same object instances)
    view1 = SimpleDocumentView.create(
        document_path=document_path,
        tokens=shared_tokens + unique_v1,
    )

    view2 = SimpleDocumentView.create(
        document_path=document_path,
        tokens=shared_tokens + unique_v2,
    )

    return view1, view2


@st.composite
def incompatible_views_strategy(draw: st.DrawFn) -> tuple["SimpleDocumentView", "SimpleDocumentView"]:
    """Generate two incompatible views (disagree on at least one overlapping token).
    
    Key insight: We must ensure the modified content is ALWAYS different from original,
    even after Hypothesis shrinking.
    """
    from pathlib import Path

    from services.interactive_text.sheaf import SimpleDocumentView, TokenState

    document_path = Path("/test/document.md")

    # Generate a shared token with DIFFERENT content in each view
    base_token = draw(token_state_strategy())

    # Use a unique ID for the conflicting token
    conflict_id = f"conflict_{base_token.token_id}"

    # Create the original token
    original_token = TokenState(
        token_id=conflict_id,
        token_type=base_token.token_type,
        content=base_token.content,
        position=base_token.position,
    )

    # Create modified version with GUARANTEED different content
    # Use a suffix that cannot be shrunk away
    modified_content = f"MODIFIED_{base_token.content}_END"
    modified_token = TokenState(
        token_id=conflict_id,  # Same ID
        token_type=base_token.token_type,
        content=modified_content,  # Different content (guaranteed)
        position=base_token.position,
    )

    # Generate unique tokens for each view with distinct prefixes
    num_unique_v1 = draw(st.integers(min_value=0, max_value=2))
    unique_v1: list[TokenState] = []
    for i in range(num_unique_v1):
        base = draw(token_state_strategy())
        unique_v1.append(TokenState(
            token_id=f"v1_incompat_{i}_{base.token_id}",
            token_type=base.token_type,
            content=base.content,
            position=base.position,
        ))

    num_unique_v2 = draw(st.integers(min_value=0, max_value=2))
    unique_v2: list[TokenState] = []
    for i in range(num_unique_v2):
        base = draw(token_state_strategy())
        unique_v2.append(TokenState(
            token_id=f"v2_incompat_{i}_{base.token_id}",
            token_type=base.token_type,
            content=base.content,
            position=base.position,
        ))

    # Create views with conflicting token states
    view1 = SimpleDocumentView.create(
        document_path=document_path,
        tokens=[original_token] + unique_v1,
    )

    view2 = SimpleDocumentView.create(
        document_path=document_path,
        tokens=[modified_token] + unique_v2,
    )

    return view1, view2


class TestProperty8DocumentSheafCoherence:
    """
    Property 8: Document Sheaf Coherence
    
    *For any* document opened in multiple views, the sheaf condition SHALL hold:
    all views with overlapping tokens agree on token state, and compatible views
    can be glued into a consistent global document.
    
    **Validates: Requirements 4.1, 4.4, 4.5, 4.6**
    """

    @given(views=compatible_views_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_compatible_views_satisfy_sheaf_condition(
        self, views: tuple["SimpleDocumentView", "SimpleDocumentView"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        Compatible views satisfy the sheaf condition.
        Validates: Requirements 4.4
        """
        from services.interactive_text.sheaf import DocumentSheaf

        view1, view2 = views
        sheaf = DocumentSheaf.create(view1.document_path)
        sheaf.add_view(view1)
        sheaf.add_view(view2)

        # Views should be compatible
        assert sheaf.compatible(view1, view2) is True

        # Sheaf condition should pass
        verification = sheaf.verify_sheaf_condition()
        assert verification.passed is True
        assert len(verification.conflicts) == 0

    @given(views=incompatible_views_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_incompatible_views_fail_sheaf_condition(
        self, views: tuple["SimpleDocumentView", "SimpleDocumentView"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        Incompatible views fail the sheaf condition.
        Validates: Requirements 4.4, 4.5
        """
        from services.interactive_text.sheaf import DocumentSheaf

        view1, view2 = views
        sheaf = DocumentSheaf.create(view1.document_path)
        sheaf.add_view(view1)
        sheaf.add_view(view2)

        # Views should be incompatible
        assert sheaf.compatible(view1, view2) is False

        # Sheaf condition should fail
        verification = sheaf.verify_sheaf_condition()
        assert verification.passed is False
        assert len(verification.conflicts) > 0

    @given(views=compatible_views_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_compatible_views_can_be_glued(
        self, views: tuple["SimpleDocumentView", "SimpleDocumentView"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        Compatible views can be glued into a consistent global document.
        Validates: Requirements 4.6
        """
        from services.interactive_text.sheaf import DocumentSheaf

        view1, view2 = views
        sheaf = DocumentSheaf.create(view1.document_path)
        sheaf.add_view(view1)
        sheaf.add_view(view2)

        # Glue should succeed
        global_state = sheaf.glue()

        # Global state should contain all tokens from both views
        all_token_ids = view1.tokens | view2.tokens
        assert set(global_state.keys()) == all_token_ids

    @given(views=incompatible_views_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_incompatible_views_cannot_be_glued(
        self, views: tuple["SimpleDocumentView", "SimpleDocumentView"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        Incompatible views cannot be glued.
        Validates: Requirements 4.6
        """
        from services.interactive_text.sheaf import DocumentSheaf, SheafConditionError

        view1, view2 = views
        sheaf = DocumentSheaf.create(view1.document_path)
        sheaf.add_view(view1)
        sheaf.add_view(view2)

        # Glue should raise SheafConditionError
        with pytest.raises(SheafConditionError) as exc_info:
            sheaf.glue()

        # Error should contain conflict information
        assert len(exc_info.value.conflicts) > 0

    @given(view=document_view_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_single_view_always_coherent(
        self, view: "SimpleDocumentView"
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        A single view is always coherent (trivially satisfies sheaf condition).
        Validates: Requirements 4.1
        """
        from services.interactive_text.sheaf import DocumentSheaf

        sheaf = DocumentSheaf.create(view.document_path)
        sheaf.add_view(view)

        # Single view should always pass sheaf condition
        verification = sheaf.verify_sheaf_condition()
        assert verification.passed is True
        assert verification.checked_pairs == 0  # No pairs to check

    @given(views=compatible_views_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_overlap_is_symmetric(
        self, views: tuple["SimpleDocumentView", "SimpleDocumentView"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        Overlap operation is symmetric: overlap(v1, v2) == overlap(v2, v1).
        Validates: Requirements 4.4
        """
        from services.interactive_text.sheaf import DocumentSheaf

        view1, view2 = views
        sheaf = DocumentSheaf.create(view1.document_path)

        overlap_1_2 = sheaf.overlap(view1, view2)
        overlap_2_1 = sheaf.overlap(view2, view1)

        assert overlap_1_2 == overlap_2_1

    @given(views=compatible_views_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_compatible_is_symmetric(
        self, views: tuple["SimpleDocumentView", "SimpleDocumentView"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        Compatible operation is symmetric: compatible(v1, v2) == compatible(v2, v1).
        Validates: Requirements 4.4
        """
        from services.interactive_text.sheaf import DocumentSheaf

        view1, view2 = views
        sheaf = DocumentSheaf.create(view1.document_path)

        compat_1_2 = sheaf.compatible(view1, view2)
        compat_2_1 = sheaf.compatible(view2, view1)

        assert compat_1_2 == compat_2_1

    @given(token=token_state_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_token_state_equality(self, token: "TokenState") -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        Token states with same observable properties are equal.
        Validates: Requirements 4.4
        """
        from services.interactive_text.sheaf import TokenState

        # Create identical token
        identical = TokenState(
            token_id=token.token_id,
            token_type=token.token_type,
            content=token.content,
            position=token.position,
        )

        assert token == identical
        assert hash(token) == hash(identical)

    @given(token=token_state_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_token_state_inequality_on_content_change(self, token: "TokenState") -> None:
        """
        Feature: meaning-token-frontend, Property 8: Document Sheaf Coherence
        
        Token states with different content are not equal.
        Validates: Requirements 4.4
        """
        from services.interactive_text.sheaf import TokenState

        # Create token with different content
        different = TokenState(
            token_id=token.token_id,
            token_type=token.token_type,
            content=token.content + "_different",
            position=token.position,
        )

        assert token != different


# =============================================================================
# Property 9: Document Sheaf Propagation
# =============================================================================


@st.composite
def edit_strategy(draw: st.DrawFn, source_view_id: str = "test_view") -> "Edit":
    """Generate valid edit operations."""
    from services.interactive_text.sheaf import Edit

    start = draw(st.integers(min_value=0, max_value=100))
    end = draw(st.integers(min_value=start, max_value=start + 50))
    new_text = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n",
        min_size=0,
        max_size=50,
    ))

    return Edit(
        start=start,
        end=end,
        new_text=new_text,
        source_view_id=source_view_id,
    )


@st.composite
def token_change_strategy(draw: st.DrawFn) -> "TokenChange":
    """Generate valid token changes."""
    from services.interactive_text.sheaf import TokenChange, TokenState

    change_type = draw(st.sampled_from(["created", "modified", "deleted"]))
    base_token = draw(token_state_strategy())

    if change_type == "created":
        return TokenChange.created(base_token)
    elif change_type == "deleted":
        return TokenChange.deleted(base_token)
    else:  # modified
        new_content = base_token.content + "_modified"
        new_token = TokenState(
            token_id=base_token.token_id,
            token_type=base_token.token_type,
            content=new_content,
            position=base_token.position,
        )
        return TokenChange.modified(base_token, new_token)


class TestProperty9DocumentSheafPropagation:
    """
    Property 9: Document Sheaf Propagation
    
    *For any* edit in any view of a document, the change SHALL propagate to all
    other views, and the file on disk SHALL reflect the canonical state.
    
    **Validates: Requirements 4.2, 4.3**
    """

    @given(edit=edit_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_edit_applies_correctly(self, edit: "Edit") -> None:
        """
        Feature: meaning-token-frontend, Property 9: Document Sheaf Propagation
        
        Edit operations apply correctly to content.
        Validates: Requirements 4.2
        """
        # Create content long enough for the edit
        content = "x" * max(edit.end + 10, 200)

        result = edit.apply(content)

        # Verify the edit was applied correctly
        assert result[:edit.start] == content[:edit.start]
        assert result[edit.start:edit.start + len(edit.new_text)] == edit.new_text
        assert result[edit.start + len(edit.new_text):] == content[edit.end:]

    @given(changes=st.lists(token_change_strategy(), min_size=1, max_size=5))
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_changes_propagate_to_views(
        self, changes: list["TokenChange"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 9: Document Sheaf Propagation
        
        Token changes propagate to all views in the sheaf.
        Validates: Requirements 4.2
        """
        from pathlib import Path

        from services.interactive_text.sheaf import (
            DocumentSheaf,
            SimpleDocumentView,
            TokenChange,
        )

        document_path = Path("/test/propagation.md")
        sheaf = DocumentSheaf.create(document_path)

        # Create multiple views
        view1 = SimpleDocumentView.create(document_path)
        view2 = SimpleDocumentView.create(document_path)
        view3 = SimpleDocumentView.create(document_path)

        sheaf.add_view(view1)
        sheaf.add_view(view2)
        sheaf.add_view(view3)

        # Propagate changes
        await sheaf._propagate_changes(changes)

        # Build expected final state by applying changes in order
        # (same logic as SimpleDocumentView.update)
        expected_state: dict[str, "TokenState"] = {}
        for change in changes:
            if change.change_type == "deleted":
                expected_state.pop(change.token_id, None)
            elif change.new_state is not None:
                expected_state[change.token_id] = change.new_state

        # Verify all views have the same final state
        for token_id, expected_token in expected_state.items():
            assert view1.state_of(token_id) == expected_token
            assert view2.state_of(token_id) == expected_token
            assert view3.state_of(token_id) == expected_token

        # Verify deleted tokens are not present
        all_token_ids = {c.token_id for c in changes}
        for token_id in all_token_ids:
            if token_id not in expected_state:
                assert view1.state_of(token_id) is None
                assert view2.state_of(token_id) is None
                assert view3.state_of(token_id) is None

    @given(view=document_view_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_change_handler_registration(self, view: "SimpleDocumentView") -> None:
        """
        Feature: meaning-token-frontend, Property 9: Document Sheaf Propagation
        
        Change handlers can be registered and unregistered.
        Validates: Requirements 4.2
        """
        from services.interactive_text.sheaf import DocumentSheaf

        sheaf = DocumentSheaf.create(view.document_path)
        sheaf.add_view(view)

        # Track handler calls
        handler_calls: list[list] = []

        def handler(changes: list) -> None:
            handler_calls.append(changes)

        # Register handler
        unsubscribe = sheaf.on_change(handler)

        # Verify handler is registered
        assert handler in sheaf._change_handlers

        # Unsubscribe
        unsubscribe()

        # Verify handler is removed
        assert handler not in sheaf._change_handlers

    @given(
        changes=st.lists(token_change_strategy(), min_size=1, max_size=3),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_change_handlers_are_notified(
        self, changes: list["TokenChange"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 9: Document Sheaf Propagation
        
        Registered change handlers are notified when changes propagate.
        Validates: Requirements 4.2
        """
        from pathlib import Path

        from services.interactive_text.sheaf import (
            DocumentSheaf,
            SimpleDocumentView,
        )

        document_path = Path("/test/handlers.md")
        sheaf = DocumentSheaf.create(document_path)

        view = SimpleDocumentView.create(document_path)
        sheaf.add_view(view)

        # Track handler calls
        received_changes: list[list] = []

        def handler(changes: list) -> None:
            received_changes.append(changes)

        sheaf.on_change(handler)

        # Propagate changes
        await sheaf._propagate_changes(changes)

        # Verify handler was called with the changes
        assert len(received_changes) == 1
        assert received_changes[0] == changes

    @given(token=token_state_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_token_change_factory_methods(self, token: "TokenState") -> None:
        """
        Feature: meaning-token-frontend, Property 9: Document Sheaf Propagation
        
        TokenChange factory methods create correct change types.
        Validates: Requirements 4.2
        """
        from services.interactive_text.sheaf import TokenChange, TokenState

        # Test created
        created = TokenChange.created(token)
        assert created.change_type == "created"
        assert created.old_state is None
        assert created.new_state == token
        assert created.token_id == token.token_id

        # Test deleted
        deleted = TokenChange.deleted(token)
        assert deleted.change_type == "deleted"
        assert deleted.old_state == token
        assert deleted.new_state is None
        assert deleted.token_id == token.token_id

        # Test modified
        new_token = TokenState(
            token_id=token.token_id,
            token_type=token.token_type,
            content=token.content + "_new",
            position=token.position,
        )
        modified = TokenChange.modified(token, new_token)
        assert modified.change_type == "modified"
        assert modified.old_state == token
        assert modified.new_state == new_token
        assert modified.token_id == token.token_id

    @given(view=document_view_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_file_change_creation(self, view: "SimpleDocumentView") -> None:
        """
        Feature: meaning-token-frontend, Property 9: Document Sheaf Propagation
        
        FileChange objects are created correctly.
        Validates: Requirements 4.3
        """
        import time

        from services.interactive_text.sheaf import FileChange

        before = time.time()
        change = FileChange(
            path=view.document_path,
            change_type="modified",
        )
        after = time.time()

        assert change.path == view.document_path
        assert change.change_type == "modified"
        assert before <= change.timestamp <= after

    @given(views=compatible_views_strategy())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_sheaf_maintains_coherence_after_glue(
        self, views: tuple["SimpleDocumentView", "SimpleDocumentView"]
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 9: Document Sheaf Propagation
        
        After gluing, the global state contains all tokens from all views.
        Validates: Requirements 4.3
        """
        from services.interactive_text.sheaf import DocumentSheaf

        view1, view2 = views
        sheaf = DocumentSheaf.create(view1.document_path)
        sheaf.add_view(view1)
        sheaf.add_view(view2)

        # Glue views
        global_state = sheaf.glue()

        # Verify global state contains all tokens
        all_tokens = view1.tokens | view2.tokens
        assert set(global_state.keys()) == all_tokens

        # Verify each token's state matches the view's state
        for token_id in view1.tokens:
            assert global_state[token_id] == view1.state_of(token_id)
        for token_id in view2.tokens:
            assert global_state[token_id] == view2.state_of(token_id)
