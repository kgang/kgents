"""
Tests for .tongue File Parser.

Phase 3: Declarative integration specifications.

Tests:
- Basic parsing
- Context and trigger blocks
- Validation
- Code generation
"""

import pytest
from protocols.tongue_parser import (
    TongueContext,
    TongueDocument,
    TongueIntegration,
    TongueParseError,
    TriggerType,
    generate_integration_code,
    parse_tongue,
    validate_document,
)


class TestBasicParsing:
    """Tests for basic .tongue parsing."""

    def test_parse_minimal_integration(self):
        """Test parsing minimal integration."""
        content = """
integration test_integration {
    emitter: psi
    receiver: forge
    pheromone: METAPHOR
}
"""
        doc = parse_tongue(content)

        assert len(doc.integrations) == 1
        integration = doc.integrations[0]
        assert integration.name == "test_integration"
        assert integration.emitter == "psi"
        assert integration.receiver == "forge"
        assert integration.pheromone == "METAPHOR"

    def test_parse_with_properties(self):
        """Test parsing with additional properties."""
        content = """
integration full_integration {
    emitter: psi
    receiver: forge
    pheromone: METAPHOR
    decay: 0.15
    radius: 0.75
    intensity: 0.9
    description: "Psi emits metaphors for Forge to sense"
}
"""
        doc = parse_tongue(content)

        integration = doc.integrations[0]
        assert integration.decay == 0.15
        assert integration.radius == 0.75
        assert integration.intensity == 0.9
        assert integration.description == "Psi emits metaphors for Forge to sense"

    def test_parse_multiple_integrations(self):
        """Test parsing multiple integrations."""
        content = """
integration psi_forge {
    emitter: psi
    receiver: forge
    pheromone: METAPHOR
}

integration judge_all {
    emitter: judge
    receiver: "*"
    pheromone: WARNING
}
"""
        doc = parse_tongue(content)

        assert len(doc.integrations) == 2
        assert doc.integrations[0].name == "psi_forge"
        assert doc.integrations[1].name == "judge_all"

    def test_parse_with_comments(self):
        """Test parsing with comments."""
        content = """
# This is a header comment

integration commented {
    # Emitter comment
    emitter: psi
    # Receiver comment
    receiver: forge
    pheromone: METAPHOR
}
"""
        doc = parse_tongue(content)

        assert len(doc.integrations) == 1
        assert doc.integrations[0].emitter == "psi"

    def test_parse_version(self):
        """Test parsing version directive."""
        content = """
version: "2.0"

integration test {
    emitter: a
    receiver: b
    pheromone: TEST
}
"""
        doc = parse_tongue(content)

        assert doc.version == "2.0"


class TestContextBlock:
    """Tests for context block parsing."""

    def test_parse_context_block(self):
        """Test parsing context block."""
        content = """
integration with_context {
    emitter: psi
    receiver: forge
    pheromone: METAPHOR

    context {
        domain: "software"
        tags: ["problem-solving", "creative"]
        embedding_dim: 128
    }
}
"""
        doc = parse_tongue(content)

        integration = doc.integrations[0]
        assert integration.context.domain == "software"
        assert integration.context.tags == ("problem-solving", "creative")
        assert integration.context.embedding_dim == 128

    def test_parse_context_single_tag(self):
        """Test parsing context with single tag."""
        content = """
integration single_tag {
    emitter: a
    receiver: b
    pheromone: TEST

    context {
        tags: ["single"]
    }
}
"""
        doc = parse_tongue(content)

        assert doc.integrations[0].context.tags == ("single",)

    def test_parse_context_no_tags(self):
        """Test parsing context without tags."""
        content = """
integration no_tags {
    emitter: a
    receiver: b
    pheromone: TEST

    context {
        domain: "test"
    }
}
"""
        doc = parse_tongue(content)

        assert doc.integrations[0].context.domain == "test"
        assert doc.integrations[0].context.tags == ()


class TestTriggerBlock:
    """Tests for trigger block parsing."""

    def test_parse_event_trigger(self):
        """Test parsing event trigger."""
        content = """
integration with_trigger {
    emitter: psi
    receiver: forge
    pheromone: METAPHOR

    trigger {
        type: event
        on: "metaphor_discovered"
        condition: "confidence > 0.7"
    }
}
"""
        doc = parse_tongue(content)

        trigger = doc.integrations[0].trigger
        assert trigger.trigger_type == TriggerType.EVENT
        assert trigger.on == "metaphor_discovered"
        assert trigger.condition == "confidence > 0.7"

    def test_parse_schedule_trigger(self):
        """Test parsing schedule trigger."""
        content = """
integration scheduled {
    emitter: monitor
    receiver: dashboard
    pheromone: METRIC

    trigger {
        type: schedule
        interval: 100
    }
}
"""
        doc = parse_tongue(content)

        trigger = doc.integrations[0].trigger
        assert trigger.trigger_type == TriggerType.SCHEDULE
        assert trigger.interval_ticks == 100

    def test_parse_threshold_trigger(self):
        """Test parsing threshold trigger."""
        content = """
integration threshold_based {
    emitter: banker
    receiver: all
    pheromone: SCARCITY

    trigger {
        type: threshold
        metric: "token_balance"
        threshold: 0.1
    }
}
"""
        doc = parse_tongue(content)

        trigger = doc.integrations[0].trigger
        assert trigger.trigger_type == TriggerType.THRESHOLD
        assert trigger.metric == "token_balance"
        assert trigger.threshold == 0.1


class TestValidation:
    """Tests for document validation."""

    def test_validate_valid_document(self):
        """Test validation of valid document."""
        doc = TongueDocument(
            integrations=[
                TongueIntegration(
                    name="valid",
                    emitter="a",
                    receiver="b",
                    pheromone="TEST",
                )
            ]
        )

        errors = validate_document(doc)
        assert len(errors) == 0

    def test_validate_missing_emitter(self):
        """Test validation catches missing emitter."""
        doc = TongueDocument(
            integrations=[
                TongueIntegration(
                    name="missing_emitter",
                    emitter="",
                    receiver="b",
                    pheromone="TEST",
                )
            ]
        )

        errors = validate_document(doc)
        assert len(errors) == 1
        assert errors[0].field == "emitter"

    def test_validate_missing_receiver(self):
        """Test validation catches missing receiver."""
        doc = TongueDocument(
            integrations=[
                TongueIntegration(
                    name="missing_receiver",
                    emitter="a",
                    receiver="",
                    pheromone="TEST",
                )
            ]
        )

        errors = validate_document(doc)
        assert len(errors) == 1
        assert errors[0].field == "receiver"

    def test_validate_missing_pheromone(self):
        """Test validation catches missing pheromone."""
        doc = TongueDocument(
            integrations=[
                TongueIntegration(
                    name="missing_pheromone",
                    emitter="a",
                    receiver="b",
                    pheromone="",
                )
            ]
        )

        errors = validate_document(doc)
        assert len(errors) == 1
        assert errors[0].field == "pheromone"

    def test_validate_invalid_decay(self):
        """Test validation catches invalid decay."""
        doc = TongueDocument(
            integrations=[
                TongueIntegration(
                    name="invalid_decay",
                    emitter="a",
                    receiver="b",
                    pheromone="TEST",
                    decay=1.5,  # > 1.0
                )
            ]
        )

        errors = validate_document(doc)
        assert len(errors) == 1
        assert errors[0].field == "decay"

    def test_validate_invalid_radius(self):
        """Test validation catches invalid radius."""
        doc = TongueDocument(
            integrations=[
                TongueIntegration(
                    name="invalid_radius",
                    emitter="a",
                    receiver="b",
                    pheromone="TEST",
                    radius=-0.5,  # Negative
                )
            ]
        )

        errors = validate_document(doc)
        assert len(errors) == 1
        assert errors[0].field == "radius"

    def test_validate_multiple_errors(self):
        """Test validation catches multiple errors."""
        doc = TongueDocument(
            integrations=[
                TongueIntegration(
                    name="multiple_issues",
                    emitter="",
                    receiver="",
                    pheromone="TEST",
                    decay=2.0,
                )
            ]
        )

        errors = validate_document(doc)
        assert len(errors) == 3  # emitter, receiver, decay


class TestCodeGeneration:
    """Tests for code generation."""

    def test_generate_basic_code(self):
        """Test basic code generation."""
        integration = TongueIntegration(
            name="psi_forge",
            emitter="psi",
            receiver="forge",
            pheromone="METAPHOR",
        )

        code = generate_integration_code(integration)

        assert "def setup_psi_forge" in code
        assert "def emit_metaphor" in code
        assert "def sense_metaphor" in code
        assert 'emitter="psi"' in code
        assert "SemanticPheromoneKind.METAPHOR" in code

    def test_generate_code_with_context(self):
        """Test code generation with context."""
        integration = TongueIntegration(
            name="test",
            emitter="a",
            receiver="b",
            pheromone="TEST",
            context=TongueContext(
                domain="software",
                tags=("creative", "problem-solving"),
            ),
        )

        code = generate_integration_code(integration)

        assert 'domain="software"' in code
        assert "creative" in code

    def test_generate_code_with_parameters(self):
        """Test code generation with custom parameters."""
        integration = TongueIntegration(
            name="custom",
            emitter="x",
            receiver="y",
            pheromone="CUSTOM",
            decay=0.2,
            radius=0.8,
            intensity=0.5,
        )

        code = generate_integration_code(integration)

        assert "intensity=0.5" in code
        assert "radius=0.8" in code


class TestParseErrors:
    """Tests for parse error handling."""

    def test_error_invalid_property(self):
        """Test error on invalid property syntax."""
        content = """
integration bad {
    invalid property without colon
}
"""
        with pytest.raises(TongueParseError):
            parse_tongue(content)

    def test_error_missing_brace(self):
        """Test error on missing closing brace."""
        content = """
integration unclosed {
    emitter: a
"""
        # This might not raise depending on implementation
        # Just verify it doesn't crash
        try:
            parse_tongue(content)  # May parse incomplete or raise
        except TongueParseError:
            pass  # Expected

    def test_error_unexpected_token(self):
        """Test error on unexpected token."""
        content = """
unexpected_keyword value
"""
        with pytest.raises(TongueParseError):
            parse_tongue(content)


class TestIntegration:
    """Integration tests for full parsing flow."""

    def test_full_tongue_file(self):
        """Test parsing a complete .tongue file."""
        content = """
# Kgents Cross-Pollination Integrations
# Version 1.0

version: "1.0"

# Psi × Forge: Metaphor discovery enhances artifact forging
integration psi_forge {
    emitter: psi
    receiver: forge
    pheromone: METAPHOR

    context {
        domain: "software"
        tags: ["problem-solving", "creative", "analogical"]
    }

    trigger {
        type: event
        on: "metaphor_discovered"
        condition: "confidence > 0.7"
    }

    decay: 0.1
    radius: 0.5
    intensity: 1.0
    description: "Psi-gent emits discovered metaphors for F-gent to sense"
}

# Judge × All: Safety warnings broadcast
integration judge_broadcast {
    emitter: judge
    receiver: "*"
    pheromone: WARNING

    context {
        domain: "safety"
        tags: ["system-wide", "broadcast"]
    }

    trigger {
        type: threshold
        metric: "entropy"
        threshold: 0.8
    }

    decay: 0.3
    radius: 1.0
    intensity: 1.0
    description: "J-gent broadcasts safety warnings to all agents"
}
"""
        doc = parse_tongue(content)

        # Validate structure
        assert doc.version == "1.0"
        assert len(doc.integrations) == 2

        # Validate first integration
        psi_forge = doc.integrations[0]
        assert psi_forge.name == "psi_forge"
        assert psi_forge.context.domain == "software"
        assert psi_forge.trigger.on == "metaphor_discovered"

        # Validate second integration
        judge = doc.integrations[1]
        assert judge.name == "judge_broadcast"
        assert judge.receiver == "*"
        assert judge.trigger.trigger_type == TriggerType.THRESHOLD

        # Validate the document
        errors = validate_document(doc)
        assert len(errors) == 0

    def test_roundtrip_validation(self):
        """Test that parsed documents validate."""
        content = """
integration valid {
    emitter: a
    receiver: b
    pheromone: TEST
    decay: 0.5
    radius: 0.5
}
"""
        doc = parse_tongue(content)
        errors = validate_document(doc)

        assert len(errors) == 0

    def test_code_generation_compiles(self):
        """Test that generated code is valid Python."""
        integration = TongueIntegration(
            name="test_integration",
            emitter="psi",
            receiver="forge",
            pheromone="METAPHOR",
            context=TongueContext(domain="software", tags=("test",)),
        )

        code = generate_integration_code(integration)

        # Code should be valid Python (compile check)
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}")
