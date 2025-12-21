"""
Tests for Token-to-SceneGraph Bridge.

Verifies that MeaningTokens from Interactive Text correctly
convert to SceneGraph nodes for Servo rendering.

See: protocols/agentese/projection/tokens_to_scene.py
"""

import pytest

from protocols.agentese.projection.scene import (
    LayoutMode,
    SceneGraph,
    SceneNode,
    SceneNodeKind,
)
from protocols.agentese.projection.tokens_to_scene import (
    MeaningTokenContent,
    MeaningTokenKind,
    markdown_to_scene_graph,
    text_span_to_scene_node,
    tokens_to_scene_graph,
)
from services.interactive_text.parser import parse_markdown


class TestMeaningTokenContent:
    """Tests for MeaningTokenContent dataclass."""

    def test_to_dict(self) -> None:
        """MeaningTokenContent serializes correctly."""
        content = MeaningTokenContent(
            token_type="agentese_path",
            source_text="`self.brain.capture`",
            source_position=(0, 20),
            token_id="agentese_path:0:20",
            token_data={"path": "self.brain.capture"},
            affordances=[{"name": "hover", "action": "hover", "handler": "...", "enabled": True}],
        )

        d = content.to_dict()

        assert d["token_type"] == "agentese_path"
        assert d["source_position"] == [0, 20]
        assert d["token_data"]["path"] == "self.brain.capture"
        assert len(d["affordances"]) == 1


class TestTextSpanToSceneNode:
    """Tests for text_span_to_scene_node converter."""

    @pytest.mark.asyncio
    async def test_plain_text_span(self) -> None:
        """Plain text spans become TEXT nodes."""
        doc = parse_markdown("Hello world")
        assert len(doc.spans) >= 1

        node = await text_span_to_scene_node(doc.spans[0])

        assert node.kind == SceneNodeKind.TEXT
        assert node.metadata["meaning_token_kind"] == MeaningTokenKind.PLAIN_TEXT.value
        assert node.content == "Hello world"

    @pytest.mark.asyncio
    async def test_agentese_path_span(self) -> None:
        """AGENTESE path tokens become nodes with AGENTESE_PORTAL kind."""
        doc = parse_markdown("Check `self.brain.capture` for details")
        tokens = doc.tokens

        assert len(tokens) >= 1
        token_span = tokens[0]

        node = await text_span_to_scene_node(token_span)

        assert node.kind == SceneNodeKind.TEXT  # Base kind
        assert node.metadata["meaning_token_kind"] == MeaningTokenKind.AGENTESE_PORTAL.value
        assert node.metadata["token_type"] == "agentese_path"

        # Content should have token data
        content = node.content
        assert isinstance(content, dict)
        assert content["token_type"] == "agentese_path"
        assert content["token_data"]["path"] == "self.brain.capture"

    @pytest.mark.asyncio
    async def test_task_checkbox_span(self) -> None:
        """Task checkbox tokens become nodes with TASK_TOGGLE kind."""
        doc = parse_markdown("- [ ] First task\n- [x] Done task")
        tokens = doc.tokens

        assert len(tokens) >= 2

        # First task (unchecked)
        node1 = await text_span_to_scene_node(tokens[0])
        assert node1.metadata["meaning_token_kind"] == MeaningTokenKind.TASK_TOGGLE.value
        content1 = node1.content
        assert isinstance(content1, dict)
        assert content1["token_data"]["checked"] is False
        assert content1["token_data"]["description"] == "First task"

        # Second task (checked)
        node2 = await text_span_to_scene_node(tokens[1])
        content2 = node2.content
        assert isinstance(content2, dict)
        assert content2["token_data"]["checked"] is True
        assert content2["token_data"]["description"] == "Done task"

    @pytest.mark.asyncio
    async def test_code_block_span(self) -> None:
        """Code block tokens become nodes with CODE_REGION kind."""
        doc = parse_markdown("```python\nprint('hello')\n```")
        tokens = doc.tokens

        assert len(tokens) >= 1

        node = await text_span_to_scene_node(tokens[0])
        assert node.metadata["meaning_token_kind"] == MeaningTokenKind.CODE_REGION.value

        content = node.content
        assert isinstance(content, dict)
        assert content["token_data"]["language"] == "python"
        assert "print" in content["token_data"]["code"]

    @pytest.mark.asyncio
    async def test_image_span(self) -> None:
        """Image tokens become nodes with IMAGE_EMBED kind."""
        doc = parse_markdown("![Alt text](image.png)")
        tokens = doc.tokens

        assert len(tokens) >= 1

        node = await text_span_to_scene_node(tokens[0])
        assert node.metadata["meaning_token_kind"] == MeaningTokenKind.IMAGE_EMBED.value

        content = node.content
        assert isinstance(content, dict)
        assert content["token_data"]["alt_text"] == "Alt text"
        assert content["token_data"]["src"] == "image.png"

    @pytest.mark.asyncio
    async def test_principle_ref_span(self) -> None:
        """Principle reference tokens become PRINCIPLE_ANCHOR nodes."""
        doc = parse_markdown("Per [P3] we must...")
        tokens = doc.tokens

        assert len(tokens) >= 1

        node = await text_span_to_scene_node(tokens[0])
        assert node.metadata["meaning_token_kind"] == MeaningTokenKind.PRINCIPLE_ANCHOR.value

        content = node.content
        assert isinstance(content, dict)
        assert content["token_data"]["principle_number"] == 3

    @pytest.mark.asyncio
    async def test_requirement_ref_span(self) -> None:
        """Requirement reference tokens become REQUIREMENT_TRACE nodes."""
        doc = parse_markdown("See [R5.1] for spec")
        tokens = doc.tokens

        assert len(tokens) >= 1

        node = await text_span_to_scene_node(tokens[0])
        assert node.metadata["meaning_token_kind"] == MeaningTokenKind.REQUIREMENT_TRACE.value

        content = node.content
        assert isinstance(content, dict)
        assert content["token_data"]["requirement_id"] == "5.1"


class TestTokensToSceneGraph:
    """Tests for tokens_to_scene_graph converter."""

    @pytest.mark.asyncio
    async def test_empty_document(self) -> None:
        """Empty document produces empty scene graph."""
        doc = parse_markdown("")

        scene = await tokens_to_scene_graph(doc)

        assert isinstance(scene, SceneGraph)
        assert len(scene.nodes) == 0

    @pytest.mark.asyncio
    async def test_simple_document(self) -> None:
        """Simple document produces scene graph with nodes."""
        doc = parse_markdown("Hello `self.test` world")

        scene = await tokens_to_scene_graph(doc)

        assert isinstance(scene, SceneGraph)
        assert len(scene.nodes) == 3  # "Hello ", `self.test`, " world"

        # Layout should be vertical
        assert scene.layout.direction == "vertical"

    @pytest.mark.asyncio
    async def test_layout_mode(self) -> None:
        """Layout mode is configurable."""
        doc = parse_markdown("Test")

        compact = await tokens_to_scene_graph(doc, layout_mode=LayoutMode.COMPACT)
        spacious = await tokens_to_scene_graph(doc, layout_mode=LayoutMode.SPACIOUS)

        assert compact.layout.mode == LayoutMode.COMPACT
        assert spacious.layout.mode == LayoutMode.SPACIOUS

    @pytest.mark.asyncio
    async def test_mixed_tokens(self) -> None:
        """Document with multiple token types produces correct nodes."""
        doc = parse_markdown("Check `self.brain.capture` and [P1]\n- [ ] Do this task")

        scene = await tokens_to_scene_graph(doc)

        # Extract meaning token kinds
        kinds = [
            node.metadata.get("meaning_token_kind")
            for node in scene.nodes
            if node.metadata.get("meaning_token_kind")
        ]

        assert MeaningTokenKind.AGENTESE_PORTAL.value in kinds
        assert MeaningTokenKind.PRINCIPLE_ANCHOR.value in kinds
        assert MeaningTokenKind.TASK_TOGGLE.value in kinds


class TestMarkdownToSceneGraph:
    """Tests for markdown_to_scene_graph convenience function."""

    @pytest.mark.asyncio
    async def test_convenience_function(self) -> None:
        """markdown_to_scene_graph parses and converts in one call."""
        scene = await markdown_to_scene_graph("Hello `world.test`")

        assert isinstance(scene, SceneGraph)
        assert len(scene.nodes) >= 2


class TestNodeProperties:
    """Tests for SceneNode properties from token conversion."""

    @pytest.mark.asyncio
    async def test_node_style(self) -> None:
        """Nodes have appropriate styles for token type."""
        doc = parse_markdown("`self.brain.capture`")
        tokens = doc.tokens
        assert len(tokens) >= 1

        node = await text_span_to_scene_node(tokens[0])

        # AGENTESE paths should have breathing style
        assert node.style.breathing is True
        assert node.style.foreground == "living_green"

    @pytest.mark.asyncio
    async def test_node_interactions(self) -> None:
        """Nodes have interactions from affordances."""
        doc = parse_markdown("`self.brain.capture`")
        tokens = doc.tokens
        assert len(tokens) >= 1

        node = await text_span_to_scene_node(tokens[0])

        # Should have interactions from affordances
        assert len(node.interactions) > 0
        # Check that at least hover and click are present
        interaction_kinds = [i.kind for i in node.interactions]
        assert "hover" in interaction_kinds
        assert "click" in interaction_kinds

    @pytest.mark.asyncio
    async def test_node_label(self) -> None:
        """Nodes have human-readable labels."""
        doc = parse_markdown("- [x] Complete the task")
        tokens = doc.tokens
        assert len(tokens) >= 1

        node = await text_span_to_scene_node(tokens[0])

        # Task toggle should have check mark and description in label
        assert "✓" in node.label
        assert "Complete the task" in node.label


class TestRoundtrip:
    """Tests for roundtrip fidelity through the bridge."""

    @pytest.mark.asyncio
    async def test_source_position_preserved(self) -> None:
        """Source positions are preserved through conversion."""
        text = "Check `self.brain` for details"
        doc = parse_markdown(text)
        tokens = doc.tokens
        assert len(tokens) >= 1

        node = await text_span_to_scene_node(tokens[0])
        content = node.content
        assert isinstance(content, dict)

        start, end = content["source_position"]
        assert text[start:end] == "`self.brain`"

    @pytest.mark.asyncio
    async def test_token_id_unique(self) -> None:
        """Each token gets a unique token_id."""
        doc = parse_markdown("`self.a` and `self.b`")
        tokens = doc.tokens
        assert len(tokens) >= 2

        node1 = await text_span_to_scene_node(tokens[0])
        node2 = await text_span_to_scene_node(tokens[1])

        content1 = node1.content
        content2 = node2.content
        assert isinstance(content1, dict)
        assert isinstance(content2, dict)

        assert content1["token_id"] != content2["token_id"]
