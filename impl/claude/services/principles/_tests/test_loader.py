"""
Tests for PrincipleLoader.

Type I (Identity): Loader returns same content for same file.
Type III (Coherence): Stance slices are consistent.
Type V (Performance): Loader caching is effective.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from services.principles import (
    ADRendering,
    ConstitutionRendering,
    MetaPrincipleRendering,
    OperationalRendering,
    PrincipleLoader,
    create_principle_loader,
)

# === Fixtures ===


@pytest.fixture
def loader() -> PrincipleLoader:
    """Create a loader with default path."""
    return create_principle_loader()


@pytest.fixture
def loader_no_cache() -> PrincipleLoader:
    """Create a loader without caching."""
    return create_principle_loader(cache=False)


# === Type I: Identity Tests ===


@pytest.mark.asyncio
async def test_load_returns_same_content_for_same_file(loader: PrincipleLoader) -> None:
    """Loader returns identical content on repeated reads."""
    content1 = await loader.load("CONSTITUTION.md")
    content2 = await loader.load("CONSTITUTION.md")

    assert content1 == content2


@pytest.mark.asyncio
async def test_constitution_immutability(loader: PrincipleLoader) -> None:
    """Constitution returns identical content across calls."""
    rendering1 = await loader.load_constitution()
    rendering2 = await loader.load_constitution()

    assert rendering1.content == rendering2.content
    assert len(rendering1.principles) == 7


# === Type III: Coherence Tests ===


@pytest.mark.asyncio
async def test_load_slices_combines_files(loader: PrincipleLoader) -> None:
    """load_slices combines multiple files with separators."""
    slices = ("CONSTITUTION.md", "meta.md")
    content = await loader.load_slices(slices)

    # Should contain content from both files
    assert "Tasteful" in content
    assert "Accursed Share" in content
    # Should have separator
    assert "---" in content


@pytest.mark.asyncio
async def test_ad_loading(loader: PrincipleLoader) -> None:
    """Can load specific ADs by ID."""
    rendering = await loader.load_ad(1)

    assert rendering.ad_id == 1
    assert rendering.content  # Not empty


@pytest.mark.asyncio
async def test_ad_category_loading(loader: PrincipleLoader) -> None:
    """Can load ADs by category."""
    rendering = await loader.load_ads_by_category("categorical")

    assert rendering.category == "categorical"
    # Categorical includes AD-001, AD-002, AD-006
    assert len(rendering.ads) >= 1


@pytest.mark.asyncio
async def test_meta_section_loading(loader: PrincipleLoader) -> None:
    """Can load specific section from meta.md."""
    rendering = await loader.load_meta(section="The Accursed Share")

    assert "Accursed Share" in rendering.content


# === Type V: Performance Tests ===


@pytest.mark.asyncio
async def test_cache_effectiveness(loader: PrincipleLoader) -> None:
    """Cache prevents repeated file reads."""
    # First load populates cache
    await loader.load("CONSTITUTION.md")

    # Check cache is populated
    assert "CONSTITUTION.md" in loader._cache


@pytest.mark.asyncio
async def test_clear_cache(loader: PrincipleLoader) -> None:
    """clear_cache empties all caches."""
    await loader.load("CONSTITUTION.md")
    await loader.load_ad(1)

    loader.clear_cache()

    assert len(loader._cache) == 0
    assert len(loader._ad_cache) == 0


# === Edge Cases ===


@pytest.mark.asyncio
async def test_missing_file_returns_placeholder(loader: PrincipleLoader) -> None:
    """Missing file returns placeholder, not error."""
    content = await loader.load("NONEXISTENT.md")

    assert "not found" in content.lower()


@pytest.mark.asyncio
async def test_missing_ad_returns_placeholder(loader: PrincipleLoader) -> None:
    """Missing AD returns placeholder."""
    rendering = await loader.load_ad(999)

    assert "not found" in rendering.content.lower()


@pytest.mark.asyncio
async def test_missing_section_returns_placeholder(loader: PrincipleLoader) -> None:
    """Missing section returns placeholder."""
    rendering = await loader.load_meta(section="Nonexistent Section")

    assert "not found" in rendering.content.lower()


# === Anti-Patterns / Puppets ===


@pytest.mark.asyncio
async def test_load_anti_patterns(loader: PrincipleLoader) -> None:
    """Can load anti-patterns for a principle."""
    anti_patterns = await loader.load_anti_patterns(1)  # Tasteful

    assert len(anti_patterns) > 0
    assert any("everything" in ap.lower() for ap in anti_patterns)


@pytest.mark.asyncio
async def test_load_puppets(loader: PrincipleLoader) -> None:
    """Can load puppets for a principle."""
    puppets = await loader.load_puppets_for_principle(5)  # Composable

    assert len(puppets) > 0


@pytest.mark.asyncio
async def test_load_related_ads(loader: PrincipleLoader) -> None:
    """Can load related ADs for a principle."""
    ads = await loader.load_related_ads(5)  # Composable

    assert len(ads) > 0
    # Composable maps to AD-001, AD-002, AD-006
    assert 1 in ads or 2 in ads or 6 in ads
