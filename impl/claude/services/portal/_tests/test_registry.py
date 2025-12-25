"""
Tests for PortalResolverRegistry.

Tests:
- Resolver registration
- Resolver lookup
- Resolution through registry
- Error handling

See: spec/protocols/portal-resource-system.md §IV, §VIII
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from services.portal import (
    FileResolver,
    PermissionDenied,
    PortalResolverRegistry,
    PortalURI,
    ResolvedResource,
    ResourceNotFound,
    UnknownResourceType,
)


class MockChatResolver:
    """Mock resolver for chat: resources."""

    @property
    def resource_type(self) -> str:
        return "chat"

    def can_resolve(self, uri: PortalURI) -> bool:
        return uri.resource_type == "chat"

    async def resolve(self, uri: PortalURI, observer: Any) -> ResolvedResource:
        # Simple mock: just return a resolved resource
        return ResolvedResource(
            uri=uri.render(),
            resource_type="chat",
            exists=True,
            title=f"Chat: {uri.resource_path}",
            preview=f"Mock chat session {uri.resource_path}",
            content={"session_id": uri.resource_path},
            actions=["expand", "fork", "resume"],
            metadata={"session_id": uri.resource_path},
        )


class TestResolverRegistration:
    """Test resolver registration."""

    def test_register_resolver(self):
        """Register a resolver."""
        registry = PortalResolverRegistry()
        resolver = MockChatResolver()

        registry.register(resolver)

        assert registry.has_resolver("chat")
        assert "chat" in registry.list_resource_types()

    def test_register_multiple_resolvers(self):
        """Register multiple resolvers."""
        registry = PortalResolverRegistry()

        registry.register(MockChatResolver())
        registry.register(FileResolver())

        assert registry.has_resolver("chat")
        assert registry.has_resolver("file")
        assert set(registry.list_resource_types()) == {"chat", "file"}

    def test_register_duplicate_raises_error(self):
        """Registering duplicate resolver raises error."""
        registry = PortalResolverRegistry()
        resolver1 = MockChatResolver()
        resolver2 = MockChatResolver()

        registry.register(resolver1)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(resolver2)

    def test_list_resource_types_empty(self):
        """List resource types when empty."""
        registry = PortalResolverRegistry()
        assert registry.list_resource_types() == []

    def test_list_resource_types_sorted(self):
        """Resource types are sorted alphabetically."""
        registry = PortalResolverRegistry()

        registry.register(MockChatResolver())
        registry.register(FileResolver())

        types = registry.list_resource_types()
        assert types == ["chat", "file"]


class TestResolverLookup:
    """Test resolver lookup."""

    def test_get_resolver_by_uri(self):
        """Get resolver by URI."""
        registry = PortalResolverRegistry()
        resolver = MockChatResolver()
        registry.register(resolver)

        uri = PortalURI.parse("chat:session-abc123")
        found = registry.get_resolver(uri)

        assert found is resolver

    def test_get_resolver_not_found(self):
        """Get resolver returns None if not found."""
        registry = PortalResolverRegistry()

        uri = PortalURI.parse("chat:session-abc123")
        found = registry.get_resolver(uri)

        assert found is None

    def test_has_resolver(self):
        """Check if resolver exists."""
        registry = PortalResolverRegistry()
        registry.register(MockChatResolver())

        assert registry.has_resolver("chat")
        assert not registry.has_resolver("crystal")


@pytest.mark.asyncio
class TestResolution:
    """Test resolution through registry."""

    async def test_resolve_string_uri(self):
        """Resolve URI passed as string."""
        registry = PortalResolverRegistry()
        registry.register(MockChatResolver())

        resource = await registry.resolve("chat:session-abc123", observer=None)

        assert resource.resource_type == "chat"
        assert resource.exists
        assert resource.title == "Chat: session-abc123"

    async def test_resolve_parsed_uri(self):
        """Resolve URI passed as PortalURI."""
        registry = PortalResolverRegistry()
        registry.register(MockChatResolver())

        uri = PortalURI.parse("chat:session-abc123")
        resource = await registry.resolve(uri, observer=None)

        assert resource.resource_type == "chat"
        assert resource.exists

    async def test_resolve_unknown_type(self):
        """Resolve unknown type raises error."""
        registry = PortalResolverRegistry()

        with pytest.raises(UnknownResourceType, match="No resolver registered"):
            await registry.resolve("crystal:some-crystal", observer=None)

    async def test_resolve_with_fragment(self):
        """Resolve URI with fragment."""
        registry = PortalResolverRegistry()
        registry.register(MockChatResolver())

        resource = await registry.resolve("chat:session-abc123#turn-5", observer=None)

        # Fragment parsing should work (though MockChatResolver ignores it)
        assert resource.exists


@pytest.mark.asyncio
class TestFileResolver:
    """Test FileResolver integration."""

    async def test_resolve_existing_file(self, tmp_path: Path):
        """Resolve existing file."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, portal!")

        # Set up resolver
        resolver = FileResolver(base_path=tmp_path)
        uri = PortalURI.parse("file:test.txt")

        # Resolve
        resource = await resolver.resolve(uri, observer=None)

        assert resource.exists
        assert resource.title == "test.txt"
        assert resource.content == "Hello, portal!"
        assert "expand" in resource.actions
        assert "view" in resource.actions
        assert resource.metadata["size"] == 14

    async def test_resolve_nonexistent_file(self, tmp_path: Path):
        """Resolve nonexistent file raises error."""
        resolver = FileResolver(base_path=tmp_path)
        uri = PortalURI.parse("file:nonexistent.txt")

        with pytest.raises(ResourceNotFound, match="File not found"):
            await resolver.resolve(uri, observer=None)

    async def test_resolve_directory_raises_error(self, tmp_path: Path):
        """Resolve directory raises error."""
        # Create directory
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        resolver = FileResolver(base_path=tmp_path)
        uri = PortalURI.parse("file:testdir")

        with pytest.raises(ResourceNotFound, match="not a file"):
            await resolver.resolve(uri, observer=None)

    async def test_resolve_binary_file(self, tmp_path: Path):
        """Resolve binary file."""
        # Create binary file with invalid UTF-8 bytes
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"\xff\xfe\xfd\xfc")

        resolver = FileResolver(base_path=tmp_path)
        uri = PortalURI.parse("file:test.bin")

        resource = await resolver.resolve(uri, observer=None)

        assert resource.exists
        assert resource.metadata["is_binary"]
        assert resource.content == b"\xff\xfe\xfd\xfc"
        assert "[Binary file" in resource.preview

    async def test_file_resolver_through_registry(self, tmp_path: Path):
        """Use FileResolver through registry."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, world!")

        # Set up registry
        registry = PortalResolverRegistry()
        registry.register(FileResolver(base_path=tmp_path))

        # Resolve through registry
        resource = await registry.resolve("file:test.txt", observer=None)

        assert resource.exists
        assert resource.content == "Hello, world!"

    async def test_implicit_file_prefix(self, tmp_path: Path):
        """Implicit file: prefix works."""
        # Create test file
        test_file = tmp_path / "README.md"
        test_file.write_text("# README")

        # Set up registry
        registry = PortalResolverRegistry()
        registry.register(FileResolver(base_path=tmp_path))

        # Resolve with implicit file: prefix (won't work through registry)
        # because registry needs the parsed URI
        uri = PortalURI.parse("README.md")  # Becomes file:README.md
        resource = await registry.resolve(uri, observer=None)

        assert resource.exists
        assert resource.resource_type == "file"


class TestLaws:
    """Test categorical laws from spec §VIII."""

    def test_law_resolver_completeness(self):
        """Law §8.3: Every registered resource type has a resolver."""
        registry = PortalResolverRegistry()
        registry.register(MockChatResolver())
        registry.register(FileResolver())

        # For every resource type, there's a resolver
        for resource_type in registry.list_resource_types():
            uri = PortalURI.parse(f"{resource_type}:test-resource")
            resolver = registry.get_resolver(uri)
            assert resolver is not None
            assert resolver.resource_type == resource_type
