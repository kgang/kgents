"""Tests for session templates."""

import pytest
from zen_agents.templates import (
    SessionTemplate,
    BUILT_IN_TEMPLATES,
    get_templates,
    get_template,
    get_templates_for_type,
)
from zen_agents.types import SessionType


class TestSessionTemplate:
    """Tests for SessionTemplate."""

    def test_create_template(self):
        """Can create a basic template."""
        t = SessionTemplate(
            name="test",
            display_name="Test",
            description="A test template",
            session_type=SessionType.SHELL,
        )
        assert t.name == "test"
        assert t.display_name == "Test"
        assert t.session_type == SessionType.SHELL

    def test_template_to_config(self):
        """Template produces valid SessionConfig."""
        t = SessionTemplate(
            name="test",
            display_name="Test",
            description="A test",
            session_type=SessionType.CLAUDE,
            model="opus",
            tags=("test", "demo"),
        )
        config = t.to_config("my-session", "/tmp")
        assert config.name == "my-session"
        assert config.session_type == SessionType.CLAUDE
        assert config.working_dir == "/tmp"
        assert config.model == "opus"
        assert config.tags == ["test", "demo"]


class TestTemplateRegistry:
    """Tests for template registry functions."""

    def test_builtin_templates_exist(self):
        """Built-in templates are available."""
        assert len(BUILT_IN_TEMPLATES) > 0

    def test_get_templates(self):
        """get_templates returns all templates."""
        templates = get_templates()
        assert len(templates) == len(BUILT_IN_TEMPLATES)
        # Returns a copy
        templates.append(None)
        assert len(get_templates()) == len(BUILT_IN_TEMPLATES)

    def test_get_template_by_name(self):
        """Can retrieve template by name."""
        t = get_template("claude_default")
        assert t is not None
        assert t.name == "claude_default"
        assert t.session_type == SessionType.CLAUDE

    def test_get_template_not_found(self):
        """Returns None for unknown template."""
        t = get_template("nonexistent")
        assert t is None

    def test_get_templates_for_type(self):
        """Can filter templates by session type."""
        claude_templates = get_templates_for_type(SessionType.CLAUDE)
        assert len(claude_templates) > 0
        for t in claude_templates:
            assert t.session_type == SessionType.CLAUDE

    def test_all_types_have_default(self):
        """Each major type has at least one template."""
        for session_type in [SessionType.CLAUDE, SessionType.SHELL]:
            templates = get_templates_for_type(session_type)
            assert len(templates) > 0, f"No templates for {session_type}"
