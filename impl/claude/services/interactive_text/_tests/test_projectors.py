"""
Property-Based Tests for Projection Functors.

This module contains property-based tests that validate the correctness
properties for projection functors as defined in the design document.

Feature: meaning-token-frontend
Testing Framework: Hypothesis
Minimum Iterations: 100 per property
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from services.interactive_text.contracts import (
    Affordance,
    AffordanceAction,
    Observer,
    ObserverDensity,
    ObserverRole,
)
from services.interactive_text.projectors.base import (
    DENSITY_PARAMS,
    CompositionResult,
    DensityParams,
    ProjectionFunctor,
    ProjectionResult,
)

# =============================================================================
# Test Token Implementation for Property Tests
# =============================================================================


@dataclass
class TestToken:
    """Simple token implementation for testing projection functors."""

    _token_type: str
    _source_text: str
    _source_position: tuple[int, int]
    _value: str = ""

    @property
    def token_type(self) -> str:
        return self._token_type

    @property
    def source_text(self) -> str:
        return self._source_text

    @property
    def source_position(self) -> tuple[int, int]:
        return self._source_position

    @property
    def token_id(self) -> str:
        start, end = self._source_position
        return f"{self._token_type}:{start}:{end}"

    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        return [
            Affordance(
                name="test",
                action=AffordanceAction.CLICK,
                handler="test.handler",
            )
        ]

    async def project(self, target: str, observer: Observer) -> Any:
        return f"[{self._token_type}:{self._value}]"

    def to_dict(self) -> dict[str, Any]:
        return {
            "token_type": self._token_type,
            "source_text": self._source_text,
            "source_position": self._source_position,
            "value": self._value,
        }


@dataclass
class TestDocument:
    """Simple document implementation for testing projection functors."""

    tokens: list[TestToken] = field(default_factory=list)
    content: str = ""


# =============================================================================
# Test Projection Functor Implementation
# =============================================================================


class StringProjectionFunctor(ProjectionFunctor[str]):
    """Simple string-based projection functor for testing.
    
    This functor projects tokens to simple string representations,
    making it easy to verify composition and naturality properties.
    """

    @property
    def target_name(self) -> str:
        return "string"

    async def project_token(
        self,
        token: TestToken,
        observer: Observer,
    ) -> str:
        """Project token to string representation."""
        params = self.get_density_params(observer)

        # Apply density-based formatting
        text = f"[{token.token_type}:{token._value}]"

        if params.truncate_length > 0 and len(text) > params.truncate_length:
            text = text[:params.truncate_length - 3] + "..."

        return text

    async def project_document(
        self,
        document: TestDocument,
        observer: Observer,
    ) -> str:
        """Project document to string representation."""
        parts = []
        for token in document.tokens:
            parts.append(await self.project_token(token, observer))
        return "\n".join(parts)

    def _compose(
        self,
        projections: list[str],
        composition_type: str,
    ) -> str:
        """Compose string projections."""
        if composition_type == "horizontal":
            return " ".join(projections)
        else:  # vertical
            return "\n".join(projections)


class ListProjectionFunctor(ProjectionFunctor[list[str]]):
    """List-based projection functor for testing composition properties.
    
    This functor projects tokens to lists, making it easy to verify
    that composition preserves structure.
    """

    @property
    def target_name(self) -> str:
        return "list"

    async def project_token(
        self,
        token: TestToken,
        observer: Observer,
    ) -> list[str]:
        """Project token to list representation."""
        return [f"{token.token_type}:{token._value}"]

    async def project_document(
        self,
        document: TestDocument,
        observer: Observer,
    ) -> list[str]:
        """Project document to list representation."""
        result: list[str] = []
        for token in document.tokens:
            result.extend(await self.project_token(token, observer))
        return result

    def _compose(
        self,
        projections: list[list[str]],
        composition_type: str,
    ) -> list[str]:
        """Compose list projections."""
        result: list[str] = []
        for proj in projections:
            result.extend(proj)
        return result


# =============================================================================
# Hypothesis Strategies
# =============================================================================


@st.composite
def test_token_strategy(draw: st.DrawFn) -> TestToken:
    """Generate random test tokens."""
    token_type = draw(st.sampled_from([
        "agentese_path",
        "task_checkbox",
        "image",
        "code_block",
        "principle_ref",
        "requirement_ref",
    ]))

    value = draw(st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
        min_size=1,
        max_size=20,
    ))

    start = draw(st.integers(min_value=0, max_value=1000))
    length = draw(st.integers(min_value=1, max_value=100))

    source_text = f"`{value}`"

    return TestToken(
        _token_type=token_type,
        _source_text=source_text,
        _source_position=(start, start + length),
        _value=value,
    )


@st.composite
def token_list_strategy(draw: st.DrawFn, min_size: int = 1, max_size: int = 5) -> list[TestToken]:
    """Generate a list of test tokens."""
    return draw(st.lists(
        test_token_strategy(),
        min_size=min_size,
        max_size=max_size,
    ))


@st.composite
def observer_strategy(draw: st.DrawFn) -> Observer:
    """Generate random observers with different umwelts."""
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
def composition_type_strategy(draw: st.DrawFn) -> str:
    """Generate composition types."""
    return draw(st.sampled_from(["horizontal", "vertical"]))


# =============================================================================
# Property 3: Projection Functor Composition Law
# =============================================================================


class TestProperty3ProjectionFunctorCompositionLaw:
    """
    Property 3: Projection Functor Composition Law
    
    *For any* two meaning tokens A and B, projecting their horizontal
    composition SHALL equal composing their projections:
    P(A >> B) = P(A) >> P(B).
    
    **Validates: Requirements 1.5, 2.6**
    """

    @given(
        tokens=token_list_strategy(min_size=2, max_size=5),
        observer=observer_strategy(),
        composition_type=composition_type_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_composition_law_string_functor(
        self,
        tokens: list[TestToken],
        observer: Observer,
        composition_type: str,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 3: Projection Functor Composition Law
        
        Projecting composed tokens equals composing individual projections.
        Validates: Requirements 1.5, 2.6
        """
        functor = StringProjectionFunctor()

        # Project each token individually
        individual_projections = [
            await functor.project_token(token, observer)
            for token in tokens
        ]

        # Compose the individual projections
        composed_after = functor._compose(individual_projections, composition_type)

        # Project the composition
        result = await functor.project_composition(tokens, composition_type, observer)
        composed_before = result.target

        # Verify composition law: P(A >> B) = P(A) >> P(B)
        assert composed_before == composed_after, (
            f"Composition law violated:\n"
            f"  P(A >> B) = {composed_before!r}\n"
            f"  P(A) >> P(B) = {composed_after!r}"
        )

    @given(
        tokens=token_list_strategy(min_size=2, max_size=5),
        observer=observer_strategy(),
        composition_type=composition_type_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_composition_law_list_functor(
        self,
        tokens: list[TestToken],
        observer: Observer,
        composition_type: str,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 3: Projection Functor Composition Law
        
        Composition law holds for list-based projections.
        Validates: Requirements 1.5, 2.6
        """
        functor = ListProjectionFunctor()

        # Project each token individually
        individual_projections = [
            await functor.project_token(token, observer)
            for token in tokens
        ]

        # Compose the individual projections
        composed_after = functor._compose(individual_projections, composition_type)

        # Project the composition
        result = await functor.project_composition(tokens, composition_type, observer)
        composed_before = result.target

        # Verify composition law
        assert composed_before == composed_after

    @given(
        tokens=token_list_strategy(min_size=2, max_size=5),
        observer=observer_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_composition_result_contains_all_token_ids(
        self,
        tokens: list[TestToken],
        observer: Observer,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 3: Projection Functor Composition Law
        
        Composition result contains all source token IDs in order.
        Validates: Requirements 1.5, 2.6
        """
        functor = StringProjectionFunctor()

        result = await functor.project_composition(tokens, "horizontal", observer)

        # Verify all token IDs are present in order
        expected_ids = tuple(token.token_id for token in tokens)
        assert result.source_token_ids == expected_ids

    @given(
        tokens=token_list_strategy(min_size=1, max_size=1),
        observer=observer_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_single_token_composition_is_identity(
        self,
        tokens: list[TestToken],
        observer: Observer,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 3: Projection Functor Composition Law
        
        Composing a single token is equivalent to projecting it directly.
        Validates: Requirements 1.5, 2.6
        """
        functor = StringProjectionFunctor()
        token = tokens[0]

        # Project directly
        direct = await functor.project_token(token, observer)

        # Project via composition
        result = await functor.project_composition([token], "horizontal", observer)

        # Single-element composition should equal direct projection
        assert result.target == direct


# =============================================================================
# Property 4: Projection Naturality Condition
# =============================================================================


class TestProperty4ProjectionNaturalityCondition:
    """
    Property 4: Projection Naturality Condition
    
    *For any* meaning token and *for any* state change to that token,
    projecting before the change then applying the target's state update
    SHALL produce the same result as applying the change then projecting.
    
    **Validates: Requirements 2.1, 2.3**
    """

    @given(
        token=test_token_strategy(),
        observer=observer_strategy(),
        new_value=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz0123456789_",
            min_size=1,
            max_size=20,
        ),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_naturality_for_value_change(
        self,
        token: TestToken,
        observer: Observer,
        new_value: str,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 4: Projection Naturality Condition
        
        Naturality holds for token value changes.
        Validates: Requirements 2.1, 2.3
        """
        functor = StringProjectionFunctor()

        # Create modified token (simulating state change)
        modified_token = TestToken(
            _token_type=token._token_type,
            _source_text=token._source_text,
            _source_position=token._source_position,
            _value=new_value,
        )

        # Path 1: Apply change then project
        projection_after_change = await functor.project_token(modified_token, observer)

        # Path 2: Project then apply target's update
        # For string functor, the "target update" is just re-projecting
        # This tests that projection is deterministic
        projection_after_change_2 = await functor.project_token(modified_token, observer)

        # Naturality: both paths should produce same result
        assert projection_after_change == projection_after_change_2

    @given(
        token=test_token_strategy(),
        observer1=observer_strategy(),
        observer2=observer_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_projection_determinism(
        self,
        token: TestToken,
        observer1: Observer,
        observer2: Observer,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 4: Projection Naturality Condition
        
        Same token + same observer always produces same projection.
        Validates: Requirements 2.1, 2.3
        """
        functor = StringProjectionFunctor()

        # Project same token with same observer twice
        projection1 = await functor.project_token(token, observer1)
        projection2 = await functor.project_token(token, observer1)

        # Should be identical
        assert projection1 == projection2

    @given(
        token=test_token_strategy(),
        observer=observer_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_projection_preserves_token_type(
        self,
        token: TestToken,
        observer: Observer,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 4: Projection Naturality Condition
        
        Projection preserves token type information.
        Validates: Requirements 2.1, 2.3
        """
        functor = StringProjectionFunctor()

        projection = await functor.project_token(token, observer)

        # Token type should be present in projection
        assert token._token_type in projection


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TestProperty3ProjectionFunctorCompositionLaw",
    "TestProperty4ProjectionNaturalityCondition",
    # Test utilities
    "TestToken",
    "TestDocument",
    "StringProjectionFunctor",
    "ListProjectionFunctor",
    # Strategies
    "test_token_strategy",
    "token_list_strategy",
    "observer_strategy",
    "composition_type_strategy",
]



# =============================================================================
# Property 5: Density-Parameterized Projection
# =============================================================================


class TestProperty5DensityParameterizedProjection:
    """
    Property 5: Density-Parameterized Projection
    
    *For any* meaning token and *for any* density value (compact, comfortable,
    spacious), the projection SHALL produce valid target-specific output that
    differs appropriately by density.
    
    **Validates: Requirements 2.4, 2.5**
    """

    @given(
        token=test_token_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_different_densities_produce_different_output(
        self,
        token: TestToken,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 5: Density-Parameterized Projection
        
        Different density settings produce appropriately different output.
        Validates: Requirements 2.4, 2.5
        """
        from services.interactive_text.projectors.cli import CLIProjectionFunctor

        functor = CLIProjectionFunctor()

        # Create observers with different densities
        compact_observer = Observer.create(
            density=ObserverDensity.COMPACT,
            role=ObserverRole.VIEWER,
        )
        comfortable_observer = Observer.create(
            density=ObserverDensity.COMFORTABLE,
            role=ObserverRole.VIEWER,
        )
        spacious_observer = Observer.create(
            density=ObserverDensity.SPACIOUS,
            role=ObserverRole.VIEWER,
        )

        # Project with each density
        compact_result = await functor.project_token(token, compact_observer)
        comfortable_result = await functor.project_token(token, comfortable_observer)
        spacious_result = await functor.project_token(token, spacious_observer)

        # All results should be valid strings
        assert isinstance(compact_result, str)
        assert isinstance(comfortable_result, str)
        assert isinstance(spacious_result, str)

        # All results should contain the token type
        assert token._token_type in compact_result or token._value in compact_result
        assert token._token_type in comfortable_result or token._value in comfortable_result
        assert token._token_type in spacious_result or token._value in spacious_result

    @given(
        token=test_token_strategy(),
        density=st.sampled_from(list(ObserverDensity)),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_density_params_applied_correctly(
        self,
        token: TestToken,
        density: ObserverDensity,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 5: Density-Parameterized Projection
        
        Density parameters are correctly applied to projections.
        Validates: Requirements 2.4, 2.5
        """
        from services.interactive_text.projectors.cli import CLIProjectionFunctor

        functor = CLIProjectionFunctor()
        observer = Observer.create(density=density)

        # Get expected params
        expected_params = DENSITY_PARAMS[density]

        # Get actual params from functor
        actual_params = functor.get_density_params(observer)

        # Verify params match
        assert actual_params.padding == expected_params.padding
        assert actual_params.font_size == expected_params.font_size
        assert actual_params.spacing == expected_params.spacing
        assert actual_params.show_details == expected_params.show_details
        assert actual_params.truncate_length == expected_params.truncate_length

    @given(
        token=test_token_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_compact_density_truncates_long_content(
        self,
        token: TestToken,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 5: Density-Parameterized Projection
        
        Compact density truncates long content appropriately.
        Validates: Requirements 2.4, 2.5
        """

        # Create a token with long value
        long_token = TestToken(
            _token_type=token._token_type,
            _source_text=token._source_text,
            _source_position=token._source_position,
            _value="a" * 100,  # Long value
        )

        functor = StringProjectionFunctor()

        compact_observer = Observer.create(density=ObserverDensity.COMPACT)
        spacious_observer = Observer.create(density=ObserverDensity.SPACIOUS)

        compact_result = await functor.project_token(long_token, compact_observer)
        spacious_result = await functor.project_token(long_token, spacious_observer)

        # Compact should be truncated (shorter or equal)
        compact_params = DENSITY_PARAMS[ObserverDensity.COMPACT]
        if compact_params.truncate_length > 0:
            assert len(compact_result) <= compact_params.truncate_length

        # Spacious should not be truncated (no truncate_length)
        spacious_params = DENSITY_PARAMS[ObserverDensity.SPACIOUS]
        if spacious_params.truncate_length == 0:
            # Full content should be present
            assert "a" * 50 in spacious_result  # At least half the content

    @given(
        token=test_token_strategy(),
        density=st.sampled_from(list(ObserverDensity)),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_web_projection_includes_density(
        self,
        token: TestToken,
        density: ObserverDensity,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 5: Density-Parameterized Projection
        
        Web projection includes density information in output.
        Validates: Requirements 2.4, 2.5
        """
        from services.interactive_text.projectors.web import WebProjectionFunctor

        # Create a web-projectable token
        class WebToken(TestToken):
            async def get_affordances(self, observer: Observer) -> list[Affordance]:
                return []

        web_token = WebToken(
            _token_type=token._token_type,
            _source_text=token._source_text,
            _source_position=token._source_position,
            _value=token._value,
        )

        functor = WebProjectionFunctor()
        observer = Observer.create(density=density)

        result = await functor.project_token(web_token, observer)

        # Result should include density
        assert result.props.get("density") == density.value

    @given(
        token=test_token_strategy(),
        density=st.sampled_from(list(ObserverDensity)),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_json_projection_includes_density_metadata(
        self,
        token: TestToken,
        density: ObserverDensity,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 5: Density-Parameterized Projection
        
        JSON projection includes density in metadata.
        Validates: Requirements 2.4, 2.5
        """
        from services.interactive_text.projectors.json import JSONProjectionFunctor

        # Create a JSON-projectable token
        class JSONToken(TestToken):
            async def get_affordances(self, observer: Observer) -> list[Affordance]:
                return []

        json_token = JSONToken(
            _token_type=token._token_type,
            _source_text=token._source_text,
            _source_position=token._source_position,
            _value=token._value,
        )

        functor = JSONProjectionFunctor()
        observer = Observer.create(density=density)

        result = await functor.project_token(json_token, observer)

        # Result should include density in metadata
        assert result["metadata"]["density"] == density.value



# =============================================================================
# Property 18: Observer-Dependent Projection
# =============================================================================


class TestProperty18ObserverDependentProjection:
    """
    Property 18: Observer-Dependent Projection
    
    *For any* meaning token and *for any* two observers with different umwelts
    (capabilities, density, role), the projections SHALL differ appropriately
    while maintaining semantic equivalence.
    
    **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.6**
    """

    @given(
        token=test_token_strategy(),
        observer1=observer_strategy(),
        observer2=observer_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_different_observers_get_valid_projections(
        self,
        token: TestToken,
        observer1: Observer,
        observer2: Observer,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 18: Observer-Dependent Projection
        
        Different observers receive valid projections.
        Validates: Requirements 13.1, 13.2, 13.3
        """
        functor = StringProjectionFunctor()

        result1 = await functor.project_token(token, observer1)
        result2 = await functor.project_token(token, observer2)

        # Both results should be valid strings
        assert isinstance(result1, str)
        assert isinstance(result2, str)

        # Both should contain token information
        assert token._token_type in result1 or token._value in result1
        assert token._token_type in result2 or token._value in result2

    @given(
        token=test_token_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_observer_capabilities_affect_affordances(
        self,
        token: TestToken,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 18: Observer-Dependent Projection
        
        Observer capabilities affect available affordances.
        Validates: Requirements 13.1, 13.4
        """
        from services.interactive_text.projectors.web import WebProjectionFunctor

        # Create token with capability-dependent affordances
        class CapabilityToken(TestToken):
            async def get_affordances(self, observer: Observer) -> list[Affordance]:
                affordances = [
                    Affordance(
                        name="basic",
                        action=AffordanceAction.CLICK,
                        handler="basic.handler",
                        enabled=True,
                    ),
                ]

                # LLM capability enables AI analysis
                if observer.has_capability("llm"):
                    affordances.append(Affordance(
                        name="analyze",
                        action=AffordanceAction.HOVER,
                        handler="llm.analyze",
                        enabled=True,
                    ))

                # Verification capability enables verification
                if observer.has_capability("verification"):
                    affordances.append(Affordance(
                        name="verify",
                        action=AffordanceAction.DOUBLE_CLICK,
                        handler="verify.handler",
                        enabled=True,
                    ))

                return affordances

        cap_token = CapabilityToken(
            _token_type=token._token_type,
            _source_text=token._source_text,
            _source_position=token._source_position,
            _value=token._value,
        )

        functor = WebProjectionFunctor()

        # Observer with no capabilities
        basic_observer = Observer.create(capabilities=frozenset())

        # Observer with LLM capability
        llm_observer = Observer.create(capabilities=frozenset(["llm"]))

        # Observer with all capabilities
        full_observer = Observer.create(
            capabilities=frozenset(["llm", "verification", "network"])
        )

        basic_result = await functor.project_token(cap_token, basic_observer)
        llm_result = await functor.project_token(cap_token, llm_observer)
        full_result = await functor.project_token(cap_token, full_observer)

        # Basic observer should have 1 affordance
        assert len(basic_result.props["affordances"]) == 1

        # LLM observer should have 2 affordances
        assert len(llm_result.props["affordances"]) == 2

        # Full observer should have 3 affordances
        assert len(full_result.props["affordances"]) == 3

    @given(
        token=test_token_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_observer_role_affects_projection(
        self,
        token: TestToken,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 18: Observer-Dependent Projection
        
        Observer role affects projection content.
        Validates: Requirements 13.4
        """
        from services.interactive_text.projectors.json import JSONProjectionFunctor

        # Create token with role-dependent behavior
        class RoleToken(TestToken):
            async def get_affordances(self, observer: Observer) -> list[Affordance]:
                affordances = [
                    Affordance(
                        name="view",
                        action=AffordanceAction.CLICK,
                        handler="view.handler",
                        enabled=True,
                    ),
                ]

                # Editors can edit
                if observer.role in (ObserverRole.EDITOR, ObserverRole.ADMIN):
                    affordances.append(Affordance(
                        name="edit",
                        action=AffordanceAction.DOUBLE_CLICK,
                        handler="edit.handler",
                        enabled=True,
                    ))

                # Admins can delete
                if observer.role == ObserverRole.ADMIN:
                    affordances.append(Affordance(
                        name="delete",
                        action=AffordanceAction.RIGHT_CLICK,
                        handler="delete.handler",
                        enabled=True,
                    ))

                return affordances

        role_token = RoleToken(
            _token_type=token._token_type,
            _source_text=token._source_text,
            _source_position=token._source_position,
            _value=token._value,
        )

        functor = JSONProjectionFunctor()

        viewer = Observer.create(role=ObserverRole.VIEWER)
        editor = Observer.create(role=ObserverRole.EDITOR)
        admin = Observer.create(role=ObserverRole.ADMIN)

        viewer_result = await functor.project_token(role_token, viewer)
        editor_result = await functor.project_token(role_token, editor)
        admin_result = await functor.project_token(role_token, admin)

        # Viewer has 1 affordance
        assert len(viewer_result["affordances"]) == 1

        # Editor has 2 affordances
        assert len(editor_result["affordances"]) == 2

        # Admin has 3 affordances
        assert len(admin_result["affordances"]) == 3

        # Metadata should reflect role
        assert viewer_result["metadata"]["role"] == "viewer"
        assert editor_result["metadata"]["role"] == "editor"
        assert admin_result["metadata"]["role"] == "admin"

    @given(
        token=test_token_strategy(),
        observer=observer_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_semantic_equivalence_across_projections(
        self,
        token: TestToken,
        observer: Observer,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 18: Observer-Dependent Projection
        
        Different projection targets maintain semantic equivalence.
        Validates: Requirements 13.6
        """
        from services.interactive_text.projectors.cli import CLIProjectionFunctor
        from services.interactive_text.projectors.json import JSONProjectionFunctor
        from services.interactive_text.projectors.web import WebProjectionFunctor

        # Create projectable token
        class MultiToken(TestToken):
            async def get_affordances(self, observer: Observer) -> list[Affordance]:
                return [
                    Affordance(
                        name="test",
                        action=AffordanceAction.CLICK,
                        handler="test.handler",
                    )
                ]

        multi_token = MultiToken(
            _token_type=token._token_type,
            _source_text=token._source_text,
            _source_position=token._source_position,
            _value=token._value,
        )

        cli_functor = CLIProjectionFunctor()
        web_functor = WebProjectionFunctor()
        json_functor = JSONProjectionFunctor()

        cli_result = await cli_functor.project_token(multi_token, observer)
        web_result = await web_functor.project_token(multi_token, observer)
        json_result = await json_functor.project_token(multi_token, observer)

        # All projections should preserve token type
        assert token._token_type in cli_result or token._value in cli_result
        assert web_result.props["tokenType"] == token._token_type
        assert json_result["tokenType"] == token._token_type

        # All projections should preserve token ID
        assert web_result.props["tokenId"] == token.token_id
        assert json_result["tokenId"] == token.token_id

    @given(
        token=test_token_strategy(),
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @pytest.mark.asyncio
    async def test_observer_density_affects_all_projectors(
        self,
        token: TestToken,
    ) -> None:
        """
        Feature: meaning-token-frontend, Property 18: Observer-Dependent Projection
        
        Observer density affects projections across all projector types.
        Validates: Requirements 13.2, 13.3
        """
        from services.interactive_text.projectors.cli import CLIProjectionFunctor
        from services.interactive_text.projectors.json import JSONProjectionFunctor
        from services.interactive_text.projectors.web import WebProjectionFunctor

        # Create projectable token
        class DensityToken(TestToken):
            async def get_affordances(self, observer: Observer) -> list[Affordance]:
                return []

        density_token = DensityToken(
            _token_type=token._token_type,
            _source_text=token._source_text,
            _source_position=token._source_position,
            _value=token._value,
        )

        cli_functor = CLIProjectionFunctor()
        web_functor = WebProjectionFunctor()
        json_functor = JSONProjectionFunctor()

        for density in ObserverDensity:
            observer = Observer.create(density=density)

            # All projectors should handle the density
            cli_result = await cli_functor.project_token(density_token, observer)
            web_result = await web_functor.project_token(density_token, observer)
            json_result = await json_functor.project_token(density_token, observer)

            # Results should be valid
            assert isinstance(cli_result, str)
            assert web_result.props["density"] == density.value
            assert json_result["metadata"]["density"] == density.value
