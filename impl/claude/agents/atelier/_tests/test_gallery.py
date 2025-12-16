"""
Tests for gallery persistence layer.
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from agents.atelier.artisan import Choice, Piece, Provenance
from agents.atelier.gallery.lineage import LineageGraph, LineageNode
from agents.atelier.gallery.store import Gallery


class TestGallery:
    """Tests for Gallery persistence."""

    @pytest.fixture
    def temp_gallery(self) -> Generator[Gallery, None, None]:
        """Create a gallery in a temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Gallery(storage_path=Path(tmpdir))

    def make_piece(
        self, id: str = "test", inspirations: list[str] | None = None
    ) -> Piece:
        """Create a test piece."""
        return Piece(
            id=id,
            content="test content",
            artisan="Test Artisan",
            commission_id="comm1",
            form="test",
            provenance=Provenance(
                interpretation="test interpretation",
                considerations=["a", "b"],
                choices=[Choice(decision="d", reason="r", alternatives=[])],
                inspirations=inspirations or [],
            ),
        )

    @pytest.mark.asyncio
    async def test_store_and_get(self, temp_gallery: Gallery) -> None:
        """Can store and retrieve a piece."""
        piece = self.make_piece("abc123")
        await temp_gallery.store(piece)

        retrieved = await temp_gallery.get("abc123")
        assert retrieved is not None
        assert retrieved.id == "abc123"
        assert retrieved.content == "test content"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, temp_gallery: Gallery) -> None:
        """Getting nonexistent piece returns None."""
        result = await temp_gallery.get("doesnotexist")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_pieces(self, temp_gallery: Gallery) -> None:
        """Can list pieces."""
        await temp_gallery.store(self.make_piece("a"))
        await temp_gallery.store(self.make_piece("b"))
        await temp_gallery.store(self.make_piece("c"))

        pieces = await temp_gallery.list_pieces()
        assert len(pieces) == 3

    @pytest.mark.asyncio
    async def test_list_with_limit(self, temp_gallery: Gallery) -> None:
        """List respects limit."""
        for i in range(10):
            await temp_gallery.store(self.make_piece(f"piece{i}"))

        pieces = await temp_gallery.list_pieces(limit=5)
        assert len(pieces) == 5

    @pytest.mark.asyncio
    async def test_list_filter_by_artisan(self, temp_gallery: Gallery) -> None:
        """Can filter by artisan."""
        piece1 = self.make_piece("a")
        piece1.artisan = "Artisan A"
        piece2 = self.make_piece("b")
        piece2.artisan = "Artisan B"

        await temp_gallery.store(piece1)
        await temp_gallery.store(piece2)

        results = await temp_gallery.list_pieces(artisan="Artisan A")
        assert len(results) == 1
        assert results[0].artisan == "Artisan A"

    @pytest.mark.asyncio
    async def test_delete(self, temp_gallery: Gallery) -> None:
        """Can delete a piece."""
        await temp_gallery.store(self.make_piece("deleteme"))
        assert await temp_gallery.get("deleteme") is not None

        deleted = await temp_gallery.delete("deleteme")
        assert deleted is True
        assert await temp_gallery.get("deleteme") is None

    @pytest.mark.asyncio
    async def test_count(self, temp_gallery: Gallery) -> None:
        """Can count pieces."""
        await temp_gallery.store(self.make_piece("a"))
        await temp_gallery.store(self.make_piece("b"))

        count = await temp_gallery.count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_search_content(self, temp_gallery: Gallery) -> None:
        """Can search by content."""
        piece1 = self.make_piece("a")
        piece1.content = "haiku about persistence"
        piece2 = self.make_piece("b")
        piece2.content = "letter about change"

        await temp_gallery.store(piece1)
        await temp_gallery.store(piece2)

        results = await temp_gallery.search_content("persistence")
        assert len(results) == 1
        assert results[0].id == "a"

    @pytest.mark.asyncio
    async def test_stream_pieces(self, temp_gallery: Gallery) -> None:
        """Can stream pieces."""
        for i in range(3):
            await temp_gallery.store(self.make_piece(f"p{i}"))

        pieces = []
        async for piece in temp_gallery.stream_pieces():
            pieces.append(piece)

        assert len(pieces) == 3


class TestLineageGraph:
    """Tests for lineage tracking."""

    def make_piece(
        self,
        id: str = "test",
        artisan: str = "Test",
        inspirations: list[str] | None = None,
    ) -> Piece:
        """Create a test piece."""
        return Piece(
            id=id,
            content=f"content of {id}",
            artisan=artisan,
            commission_id="comm",
            form="test",
            provenance=Provenance(
                interpretation=f"interpretation of {id}",
                considerations=[],
                choices=[],
                inspirations=inspirations or [],
            ),
        )

    def test_add_piece(self) -> None:
        """Can add pieces to graph."""
        graph = LineageGraph()
        piece = self.make_piece("a")
        node = graph.add_piece(piece)

        assert node.piece_id == "a"
        assert "a" in graph.nodes

    def test_parent_child_relationship(self) -> None:
        """Adding piece updates parent's children."""
        graph = LineageGraph()

        parent = self.make_piece("parent")
        child = self.make_piece("child", inspirations=["parent"])

        graph.add_piece(parent)
        graph.add_piece(child)

        assert "child" in graph.nodes["parent"].children
        assert "parent" in graph.nodes["child"].parents

    def test_get_ancestors(self) -> None:
        """Can get all ancestors."""
        graph = LineageGraph()

        # grandparent -> parent -> child
        graph.add_piece(self.make_piece("grandparent"))
        graph.add_piece(self.make_piece("parent", inspirations=["grandparent"]))
        graph.add_piece(self.make_piece("child", inspirations=["parent"]))

        ancestors = graph.get_ancestors("child")
        ancestor_ids = {a.piece_id for a in ancestors}

        assert "parent" in ancestor_ids
        assert "grandparent" in ancestor_ids

    def test_get_descendants(self) -> None:
        """Can get all descendants."""
        graph = LineageGraph()

        graph.add_piece(self.make_piece("root"))
        graph.add_piece(self.make_piece("child1", inspirations=["root"]))
        graph.add_piece(self.make_piece("child2", inspirations=["root"]))
        graph.add_piece(self.make_piece("grandchild", inspirations=["child1"]))

        descendants = graph.get_descendants("root")
        desc_ids = {d.piece_id for d in descendants}

        assert "child1" in desc_ids
        assert "child2" in desc_ids
        assert "grandchild" in desc_ids

    def test_get_roots(self) -> None:
        """Can get root nodes."""
        graph = LineageGraph()

        graph.add_piece(self.make_piece("root1"))
        graph.add_piece(self.make_piece("root2"))
        graph.add_piece(self.make_piece("child", inspirations=["root1"]))

        roots = graph.get_roots()
        root_ids = {r.piece_id for r in roots}

        assert "root1" in root_ids
        assert "root2" in root_ids
        assert "child" not in root_ids

    def test_common_ancestors(self) -> None:
        """Can find common ancestors."""
        graph = LineageGraph()

        graph.add_piece(self.make_piece("common_ancestor"))
        graph.add_piece(self.make_piece("branch_a", inspirations=["common_ancestor"]))
        graph.add_piece(self.make_piece("branch_b", inspirations=["common_ancestor"]))
        graph.add_piece(self.make_piece("leaf_a", inspirations=["branch_a"]))
        graph.add_piece(self.make_piece("leaf_b", inspirations=["branch_b"]))

        common = graph.common_ancestors("leaf_a", "leaf_b")
        common_ids = {c.piece_id for c in common}

        assert "common_ancestor" in common_ids

    def test_from_pieces(self) -> None:
        """Can build graph from piece list."""
        pieces = [
            self.make_piece("a"),
            self.make_piece("b", inspirations=["a"]),
            self.make_piece("c", inspirations=["a", "b"]),
        ]

        graph = LineageGraph.from_pieces(pieces)

        assert len(graph.nodes) == 3
        assert "b" in graph.nodes["a"].children
        assert "c" in graph.nodes["a"].children

    def test_render_tree(self) -> None:
        """Can render tree as ASCII."""
        graph = LineageGraph()

        graph.add_piece(self.make_piece("root", artisan="Writer"))
        graph.add_piece(
            self.make_piece("child", artisan="Editor", inspirations=["root"])
        )

        tree = graph.render_tree("root")

        assert "Writer" in tree
        assert "Editor" in tree
