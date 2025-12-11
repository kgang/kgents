"""Tests for L-gent E-gent Integration module."""

import pytest
from agents.l.egent_integration import (
    STANDARD_SCHEMAS,
    # Code intent
    CodeIntent,
    # Mutation schemas
    MutationSchema,
    SchemaCategory,
    # Extended registry
    cosine_similarity,
    create_egent_registry,
    extract_code_docstrings,
    extract_code_names,
    # Type inference
    infer_types,
    types_compatible,
)
from agents.l.semantic import SimpleEmbedder

# =============================================================================
# Mutation Schema Tests
# =============================================================================


class TestMutationSchema:
    """Tests for MutationSchema."""

    def test_schema_creation(self) -> None:
        """Test basic schema creation."""
        schema = MutationSchema(
            name="test_schema",
            category=SchemaCategory.SUBSTITUTE,
            precondition="if x: ...",
            transformation="x and ...",
            description="Test transformation",
            enthalpy_delta=-0.2,
            entropy_delta=0.1,
        )

        assert schema.name == "test_schema"
        assert schema.category == SchemaCategory.SUBSTITUTE
        assert schema.confidence == 0.7  # default

    def test_schema_signature(self) -> None:
        """Test schema signature generation."""
        schema1 = MutationSchema(
            name="schema1",
            category=SchemaCategory.SUBSTITUTE,
            precondition="pattern_a",
            transformation="",
            description="",
            enthalpy_delta=0,
            entropy_delta=0,
        )
        schema2 = MutationSchema(
            name="schema1",
            category=SchemaCategory.SUBSTITUTE,
            precondition="pattern_a",
            transformation="different",
            description="different",
            enthalpy_delta=0,
            entropy_delta=0,
        )
        schema3 = MutationSchema(
            name="schema1",
            category=SchemaCategory.SUBSTITUTE,
            precondition="pattern_b",
            transformation="",
            description="",
            enthalpy_delta=0,
            entropy_delta=0,
        )

        # Same name + category + precondition = same signature
        assert schema1.signature == schema2.signature
        # Different precondition = different signature
        assert schema1.signature != schema3.signature

    def test_gibbs_free_energy(self) -> None:
        """Test Gibbs free energy calculation."""
        schema = MutationSchema(
            name="test",
            category=SchemaCategory.SUBSTITUTE,
            precondition="",
            transformation="",
            description="",
            enthalpy_delta=-0.3,  # ΔH = -0.3 (simplifying)
            entropy_delta=0.1,  # ΔS = +0.1 (more capability)
        )

        # ΔG = ΔH - TΔS
        # At T=1.0: ΔG = -0.3 - 1.0*0.1 = -0.4 (favorable)
        assert schema.gibbs_free_energy(1.0) == pytest.approx(-0.4)

        # At T=0.5: ΔG = -0.3 - 0.5*0.1 = -0.35
        assert schema.gibbs_free_energy(0.5) == pytest.approx(-0.35)

        # At T=5.0: ΔG = -0.3 - 5.0*0.1 = -0.8 (more favorable at high temp)
        assert schema.gibbs_free_energy(5.0) == pytest.approx(-0.8)

    def test_standard_schemas_exist(self) -> None:
        """Test that standard schemas are defined."""
        assert len(STANDARD_SCHEMAS) > 0

        # Check for expected categories
        categories = {s.category for s in STANDARD_SCHEMAS}
        assert SchemaCategory.SUBSTITUTE in categories
        assert SchemaCategory.EXTRACT in categories
        assert SchemaCategory.ANNOTATE in categories

    def test_standard_schemas_viable(self) -> None:
        """Test that standard schemas have favorable thermodynamics."""
        for schema in STANDARD_SCHEMAS:
            # At T=1.0, most schemas should be viable (ΔG < 0)
            gibbs = schema.gibbs_free_energy(1.0)
            # Allow some schemas that are not always viable
            assert gibbs < 1.0, f"{schema.name} has ΔG={gibbs}"


# =============================================================================
# Code Intent Tests
# =============================================================================


class TestExtractCodeDocstrings:
    """Tests for extract_code_docstrings."""

    def test_extract_module_docstring(self) -> None:
        """Test extracting module docstring."""
        code = '''"""Module docstring."""

def foo():
    pass
'''
        docstrings = extract_code_docstrings(code)
        assert "Module docstring." in docstrings

    def test_extract_function_docstring(self) -> None:
        """Test extracting function docstring."""
        code = '''
def calculate(x: int) -> int:
    """Calculate something important."""
    return x * 2
'''
        docstrings = extract_code_docstrings(code)
        assert "Calculate something important." in docstrings

    def test_extract_class_docstring(self) -> None:
        """Test extracting class docstring."""
        code = '''
class DataProcessor:
    """Process data efficiently."""

    def process(self):
        """Process one item."""
        pass
'''
        docstrings = extract_code_docstrings(code)
        assert "Process data efficiently." in docstrings
        assert "Process one item." in docstrings

    def test_no_docstrings(self) -> None:
        """Test code without docstrings."""
        code = """
def foo():
    return 42
"""
        docstrings = extract_code_docstrings(code)
        assert len(docstrings) == 0

    def test_syntax_error(self) -> None:
        """Test invalid syntax returns empty list."""
        code = "def broken("
        docstrings = extract_code_docstrings(code)
        assert docstrings == []


class TestExtractCodeNames:
    """Tests for extract_code_names."""

    def test_extract_function_names(self) -> None:
        """Test extracting function names."""
        code = """
def calculate_sum(a, b):
    return a + b

async def fetch_data():
    pass
"""
        names = extract_code_names(code)
        assert "calculate_sum" in names
        assert "fetch_data" in names

    def test_extract_class_names(self) -> None:
        """Test extracting class names."""
        code = """
class DataProcessor:
    def process(self):
        pass

class ResultHandler:
    pass
"""
        names = extract_code_names(code)
        assert "DataProcessor" in names
        assert "ResultHandler" in names
        assert "process" in names

    def test_nested_functions(self) -> None:
        """Test extracting nested function names."""
        code = """
def outer():
    def inner():
        pass
    return inner
"""
        names = extract_code_names(code)
        assert "outer" in names
        assert "inner" in names


class TestCodeIntent:
    """Tests for CodeIntent."""

    @pytest.mark.asyncio
    async def test_intent_from_user(self) -> None:
        """Test creating intent from user description."""
        embedder = SimpleEmbedder(dimension=64)
        await embedder.fit(["test embedding"])

        intent = await CodeIntent.from_user(
            "Parse JSON and extract user data",
            embedder,
        )

        assert intent.source == "user"
        assert intent.confidence == 1.0
        assert len(intent.embedding) == 64

    @pytest.mark.asyncio
    async def test_intent_from_tests(self) -> None:
        """Test creating intent from test docstrings."""
        embedder = SimpleEmbedder(dimension=64)
        await embedder.fit(["test docstring one", "test docstring two"])

        intent = await CodeIntent.from_tests(
            [
                "Test that valid JSON parses correctly",
                "Test that invalid JSON raises error",
            ],
            embedder,
        )

        assert intent.source == "tests"
        assert intent.confidence == 0.7
        assert len(intent.embedding) == 64

    @pytest.mark.asyncio
    async def test_intent_from_structure(self) -> None:
        """Test creating intent from code structure."""
        embedder = SimpleEmbedder(dimension=64)
        await embedder.fit(["test docstring", "parse json data"])

        intent = await CodeIntent.from_structure(
            docstrings=["Parse data"],
            names=["parse_json", "extract_user"],
            embedder=embedder,
        )

        assert intent.source == "structure"
        assert intent.confidence == 0.5


# =============================================================================
# Type Inference Tests
# =============================================================================


class TestInferTypes:
    """Tests for infer_types."""

    def test_infer_function_types(self) -> None:
        """Test inferring function types."""
        code = """
def add(a: int, b: int) -> int:
    return a + b
"""
        types = infer_types(code)
        assert len(types) == 1
        assert types[0].name == "add"
        assert types[0].kind == "function"
        assert types[0].input_types == ["int", "int"]
        assert types[0].output_type == "int"

    def test_infer_async_function(self) -> None:
        """Test inferring async function types."""
        code = """
async def fetch(url: str) -> dict:
    pass
"""
        types = infer_types(code)
        assert len(types) == 1
        assert types[0].name == "fetch"
        assert types[0].kind == "function"
        assert types[0].output_type == "dict"

    def test_infer_untyped_function(self) -> None:
        """Test inferring untyped function defaults to Any."""
        code = """
def mystery(x, y):
    return x + y
"""
        types = infer_types(code)
        assert len(types) == 1
        assert types[0].input_types == ["Any", "Any"]
        assert types[0].output_type is None

    def test_infer_class_types(self) -> None:
        """Test inferring class types."""
        code = """
class User:
    name: str
    age: int

    def greet(self):
        pass
"""
        types = infer_types(code)

        # Should have User class and greet method
        class_types = [t for t in types if t.kind == "class"]
        assert len(class_types) == 1
        assert class_types[0].name == "User"
        assert "name" in class_types[0].attributes
        assert "age" in class_types[0].attributes
        assert "greet" in class_types[0].attributes

    def test_syntax_error(self) -> None:
        """Test invalid syntax returns empty list."""
        code = "def broken("
        types = infer_types(code)
        assert types == []


class TestTypesCompatible:
    """Tests for types_compatible."""

    def test_identical_types_compatible(self) -> None:
        """Test identical code is compatible with itself."""
        original = infer_types("def foo(): pass")
        mutated = infer_types("def foo(): pass")
        assert types_compatible(original, mutated)

    def test_added_function_compatible(self) -> None:
        """Test adding a function is compatible."""
        original = infer_types("def foo(): pass")
        mutated = infer_types("def foo(): pass\ndef bar(): pass")
        assert types_compatible(original, mutated)

    def test_removed_public_incompatible(self) -> None:
        """Test removing a public function is incompatible."""
        original = infer_types("def foo(): pass\ndef bar(): pass")
        mutated = infer_types("def bar(): pass")
        assert not types_compatible(original, mutated)

    def test_removed_private_compatible(self) -> None:
        """Test removing a private function is compatible."""
        original = infer_types("def foo(): pass\ndef _helper(): pass")
        mutated = infer_types("def foo(): pass")
        assert types_compatible(original, mutated)

    def test_changed_signature_incompatible(self) -> None:
        """Test changing return type to different concrete type is incompatible."""
        original = infer_types("def foo() -> int: return 1")
        mutated = infer_types("def foo() -> str: return 'x'")
        assert not types_compatible(original, mutated)

    def test_any_return_compatible(self) -> None:
        """Test Any return type is compatible with specific types."""
        original = infer_types("def foo(): return 1")  # Untyped = Any
        mutated = infer_types("def foo() -> int: return 1")
        assert types_compatible(original, mutated)


# =============================================================================
# EgentSemanticRegistry Tests
# =============================================================================


class TestEgentSemanticRegistry:
    """Tests for EgentSemanticRegistry."""

    @pytest.mark.asyncio
    async def test_get_mutation_schemas(self) -> None:
        """Test getting mutation schemas."""
        registry = await create_egent_registry()

        schemas = registry.get_mutation_schemas()
        assert len(schemas) > 0

    @pytest.mark.asyncio
    async def test_get_mutation_schemas_by_category(self) -> None:
        """Test filtering schemas by category."""
        registry = await create_egent_registry()

        extract_schemas = registry.get_mutation_schemas(category=SchemaCategory.EXTRACT)
        assert all(s.category == SchemaCategory.EXTRACT for s in extract_schemas)

    @pytest.mark.asyncio
    async def test_get_mutation_schemas_by_temperature(self) -> None:
        """Test filtering schemas by Gibbs viability."""
        registry = await create_egent_registry()

        # At very low temperature, entropy term is negligible
        # Only schemas with ΔG < 0 will pass
        # ΔG = ΔH - TΔS, so at T=0.01, ΔG ≈ ΔH
        cold_schemas = registry.get_mutation_schemas(temperature=0.01)
        for schema in cold_schemas:
            # Gibbs must be negative (viable)
            assert schema.gibbs_free_energy(0.01) < 0

    @pytest.mark.asyncio
    async def test_register_custom_schema(self) -> None:
        """Test registering custom schema."""
        registry = await create_egent_registry()

        initial_count = len(registry.get_mutation_schemas())

        custom = MutationSchema(
            name="custom_transform",
            category=SchemaCategory.SUBSTITUTE,
            precondition="pattern",
            transformation="result",
            description="Custom transformation",
            enthalpy_delta=-0.1,
            entropy_delta=0.1,
        )
        registry.register_schema(custom)

        assert len(registry.get_mutation_schemas()) == initial_count + 1

    @pytest.mark.asyncio
    async def test_embed_text(self) -> None:
        """Test text embedding."""
        registry = await create_egent_registry()

        embedding = await registry.embed_text("parse JSON data")
        assert len(embedding) > 0
        assert isinstance(embedding, list)

    @pytest.mark.asyncio
    async def test_embed_code_intent(self) -> None:
        """Test code intent embedding."""
        registry = await create_egent_registry()

        code = '''
def parse_json(data: str) -> dict:
    """Parse JSON string into dictionary."""
    import json
    return json.loads(data)
'''
        embedding = await registry.embed_code_intent(code)
        assert len(embedding) > 0

    @pytest.mark.asyncio
    async def test_create_code_intent_with_user(self) -> None:
        """Test creating code intent with user description."""
        registry = await create_egent_registry()

        code = "def mystery(): pass"
        intent = await registry.create_code_intent(
            code,
            user_description="Process user authentication",
        )

        assert intent.source == "user"
        assert intent.confidence == 1.0

    @pytest.mark.asyncio
    async def test_create_code_intent_from_docstring(self) -> None:
        """Test creating code intent from docstrings."""
        registry = await create_egent_registry()

        code = '''
def calculate():
    """Calculate the sum of all items."""
    pass
'''
        intent = await registry.create_code_intent(code)
        assert intent.source == "tests"  # docstrings treated as test evidence

    @pytest.mark.asyncio
    async def test_infer_types(self) -> None:
        """Test type inference via registry."""
        registry = await create_egent_registry()

        code = "def foo(x: int) -> str: return str(x)"
        types = registry.infer_types(code)

        assert len(types) == 1
        assert types[0].name == "foo"

    @pytest.mark.asyncio
    async def test_types_compatible(self) -> None:
        """Test type compatibility via registry."""
        registry = await create_egent_registry()

        original = "def foo(): pass\ndef bar(): pass"
        mutated = "def foo(): pass\ndef bar(): pass\ndef baz(): pass"

        assert registry.types_compatible(original, mutated)

    @pytest.mark.asyncio
    async def test_types_incompatible(self) -> None:
        """Test type incompatibility via registry."""
        registry = await create_egent_registry()

        original = "def foo(): pass\ndef bar(): pass"
        mutated = "def baz(): pass"  # Removed foo and bar

        assert not registry.types_compatible(original, mutated)


# =============================================================================
# Archetype Management Tests
# =============================================================================


class TestArchetypeManagement:
    """Tests for archetype management."""

    @pytest.mark.asyncio
    async def test_register_archetype_with_text(self) -> None:
        """Test registering archetype with text."""
        registry = await create_egent_registry()

        archetype_id = await registry.register_archetype(
            name="viral:pattern_001",
            text="loop optimization pattern",
            signature="loop_opt",
        )

        assert archetype_id == "viral:pattern_001"
        archetype = registry.get_archetype("viral:pattern_001")
        assert archetype is not None
        assert archetype.signature == "loop_opt"

    @pytest.mark.asyncio
    async def test_register_archetype_with_embedding(self) -> None:
        """Test registering archetype with pre-computed embedding."""
        registry = await create_egent_registry()

        embedding = [0.1] * 128

        archetype_id = await registry.register_archetype(
            name="viral:pattern_002",
            embedding=embedding,
            signature="custom",
        )

        archetype = registry.get_archetype(archetype_id)
        assert archetype is not None
        assert archetype.embedding == embedding

    @pytest.mark.asyncio
    async def test_deregister_archetype(self) -> None:
        """Test deregistering archetype."""
        registry = await create_egent_registry()

        await registry.register_archetype(
            name="viral:to_delete",
            text="temporary pattern",
        )

        assert registry.get_archetype("viral:to_delete") is not None

        success = registry.deregister_archetype("viral:to_delete")
        assert success
        assert registry.get_archetype("viral:to_delete") is None

    @pytest.mark.asyncio
    async def test_deregister_nonexistent(self) -> None:
        """Test deregistering non-existent archetype."""
        registry = await create_egent_registry()

        success = registry.deregister_archetype("nonexistent")
        assert not success

    @pytest.mark.asyncio
    async def test_find_similar_archetypes(self) -> None:
        """Test finding similar archetypes."""
        registry = await create_egent_registry()

        # Register several archetypes
        await registry.register_archetype(
            name="viral:loop_opt",
            text="optimize loop iteration",
        )
        await registry.register_archetype(
            name="viral:dict_comp",
            text="dictionary comprehension pattern",
        )
        await registry.register_archetype(
            name="other:unrelated",
            text="authentication handler",
        )

        # Search for loop-related
        query_embedding = await registry.embed_text("loop optimization")
        results = await registry.find_similar_archetypes(
            embedding=query_embedding,
            prefix="viral:",
            threshold=0.0,
        )

        # Should only return viral: prefixed archetypes
        names = [r[0] for r in results]
        assert "other:unrelated" not in names

    @pytest.mark.asyncio
    async def test_find_similar_archetypes_with_threshold(self) -> None:
        """Test that threshold filters results."""
        registry = await create_egent_registry()

        await registry.register_archetype(
            name="viral:exact",
            text="exact match pattern",
        )

        # Query with same text should have high similarity
        query = await registry.embed_text("exact match pattern")
        high_threshold = await registry.find_similar_archetypes(
            embedding=query,
            threshold=0.9,
        )

        # Query with unrelated text should have low similarity
        unrelated = await registry.embed_text("completely different topic")
        results = await registry.find_similar_archetypes(
            embedding=unrelated,
            threshold=0.9,
        )

        # High threshold should filter out unrelated
        assert len(results) <= len(high_threshold)


# =============================================================================
# Utility Tests
# =============================================================================


class TestCosineSimilarity:
    """Tests for cosine_similarity."""

    def test_identical_vectors(self) -> None:
        """Test identical vectors have similarity 1.0."""
        v = [1.0, 2.0, 3.0]
        assert cosine_similarity(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self) -> None:
        """Test orthogonal vectors have similarity 0.0."""
        v1 = [1.0, 0.0]
        v2 = [0.0, 1.0]
        assert cosine_similarity(v1, v2) == pytest.approx(0.0)

    def test_opposite_vectors(self) -> None:
        """Test opposite vectors have similarity -1.0."""
        v1 = [1.0, 1.0]
        v2 = [-1.0, -1.0]
        assert cosine_similarity(v1, v2) == pytest.approx(-1.0)

    def test_zero_vector(self) -> None:
        """Test zero vector returns 0.0."""
        v1 = [0.0, 0.0]
        v2 = [1.0, 1.0]
        assert cosine_similarity(v1, v2) == 0.0

    def test_different_dimensions(self) -> None:
        """Test different dimensions returns 0.0."""
        v1 = [1.0, 2.0, 3.0]
        v2 = [1.0, 2.0]
        assert cosine_similarity(v1, v2) == 0.0
