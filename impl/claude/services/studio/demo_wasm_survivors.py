#!/usr/bin/env python3
"""
Demo: Creative Production Studio on WASM Survivors

This script demonstrates the full creative production pipeline:
1. Archaeology - Extract patterns from WASM Survivors specs
2. Vision - Synthesize creative direction
3. Production - Generate minimal asset set

Run with: uv run python -m services.studio.demo_wasm_survivors
"""

import asyncio
import json

# Add impl/claude to path for imports
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.studio.core import CreativeStudioService
from services.studio.llm import has_llm_credentials
from services.studio.types import (
    ArchaeologyFocus,
    AssetRequirement,
    AssetSpec,
    AssetType,
    DesignPrinciple,
    InterpretationLens,
    Source,
    SourceType,
)


async def demo_archaeology(studio: CreativeStudioService) -> dict[str, Any]:
    """Phase 1: Archaeological excavation of WASM Survivors specs."""
    print("\n" + "=" * 60)
    print("PHASE 1: AESTHETIC ARCHAEOLOGY")
    print("=" * 60)

    # Define sources
    base_path = Path(__file__).parent.parent.parent.parent.parent / "pilots" / "wasm-survivors-game"

    sources = []
    spec_files = [
        "PROTO_SPEC.md",
        "PROTO_SPEC_ENLIGHTENED.md",
        "ART_PIPELINE.md",
        "SYSTEM_REQUIREMENTS.md",
    ]

    for spec_file in spec_files:
        path = base_path / spec_file
        if path.exists():
            content = path.read_text()
            sources.append(
                Source(
                    path=str(path),
                    type=SourceType.SPEC,
                    content=content,
                    metadata={"filename": spec_file},
                )
            )
            print(f"  📄 Loaded: {spec_file} ({len(content):,} chars)")
        else:
            print(f"  ⚠️  Missing: {spec_file}")

    if not sources:
        print("  ❌ No sources found!")
        return {}

    # Excavate visual patterns
    print(f"\n  🔍 Excavating VISUAL patterns from {len(sources)} sources...")
    findings = await studio.excavate(
        sources=sources,
        focus=ArchaeologyFocus.VISUAL,
        depth="deep",
    )

    print(f"\n  ✅ Found {len(findings.patterns)} patterns:")
    for i, pattern in enumerate(findings.patterns[:10], 1):
        print(f"     {i}. {pattern.name}: {pattern.description[:60]}...")

    if len(findings.patterns) > 10:
        print(f"     ... and {len(findings.patterns) - 10} more")

    # Interpret through aesthetic lens
    print("\n  🎨 Interpreting through AESTHETIC lens...")
    meaning = await studio.interpret(
        findings=findings,
        lens=InterpretationLens.AESTHETIC,
    )

    print(f"\n  ✅ Interpreted {len(meaning.interpretations)} patterns")
    for interp in meaning.interpretations[:5]:
        print(f"     • {interp.pattern_name}: {interp.meaning[:80]}...")

    return {
        "findings": findings,
        "meaning": meaning,
    }


async def demo_vision(
    studio: CreativeStudioService, archaeology_result: dict[str, Any]
) -> dict[str, Any]:
    """Phase 2: Vision synthesis from findings + principles."""
    print("\n" + "=" * 60)
    print("PHASE 2: VISION SYNTHESIS")
    print("=" * 60)

    findings = archaeology_result.get("findings")
    if not findings:
        print("  ❌ No findings to synthesize from!")
        return {}

    # Define design principles (from kgents Constitution)
    principles = [
        DesignPrinciple(
            statement="Geometric arcade aesthetic with biological undertones",
            rationale="Hornet vs Bees - angular player, rounded enemies",
            priority=1,
        ),
        DesignPrinciple(
            statement="High contrast: player (electric blue) vs enemies (corrupted red/orange)",
            rationale="Immediate visual clarity in chaotic situations",
            priority=1,
        ),
        DesignPrinciple(
            statement="Daring, bold, creative, opinionated but not gaudy",
            rationale="Kent's Mirror Test - does it feel like me on my best day?",
            priority=2,
        ),
        DesignPrinciple(
            statement="Motion is earned, stillness is default",
            rationale="90% Steel, 10% Life - the STARK BIOME principle",
            priority=2,
        ),
        DesignPrinciple(
            statement="Metamorphosis as dread: pulsing enemies threaten to combine",
            rationale="The hive mind is the true enemy, not individual bees",
            priority=1,
        ),
    ]

    print(f"\n  📜 Applying {len(principles)} design principles:")
    for p in principles:
        print(f"     • {p.statement[:60]}...")

    # Synthesize vision
    print("\n  ✨ Synthesizing creative vision...")
    vision = await studio.synthesize(
        findings=findings,
        principles=principles,
    )

    print("\n  ✅ Vision synthesized!")
    print("\n  💡 Core Insight:")
    print(f"     {vision.core_insight}")

    print("\n  🎨 Color Palette:")
    print(f"     Primary:   {vision.color_palette.primary}")
    print(f"     Secondary: {vision.color_palette.secondary}")
    print(f"     Accent:    {vision.color_palette.accent}")

    print("\n  📝 Typography:")
    print(f"     Heading: {vision.typography.heading_font}")
    print(f"     Body:    {vision.typography.body_font}")
    print(f"     Mono:    {vision.typography.mono_font}")

    print("\n  🎬 Motion:")
    print(f"     Timing:  {vision.motion.timing_function}")
    print(f"     Easing:  {vision.motion.easing}")

    print("\n  🗣️ Tone:")
    print(f"     Voice:       {vision.tone.voice}")
    print(f"     Personality: {vision.tone.personality}")

    # Generate style guide
    print("\n  📖 Generating style guide...")
    style_guide = await studio.codify(vision)

    print(f"\n  ✅ Style guide with {len(style_guide.rules)} rules:")
    for rule in style_guide.rules[:5]:
        print(f"     • [{rule.category}] {rule.rule[:50]}...")

    return {
        "vision": vision,
        "style_guide": style_guide,
    }


async def demo_production(
    studio: CreativeStudioService, vision_result: dict[str, Any]
) -> dict[str, Any]:
    """Phase 3: Asset production from vision."""
    print("\n" + "=" * 60)
    print("PHASE 3: ASSET PRODUCTION")
    print("=" * 60)

    vision = vision_result.get("vision")
    if not vision:
        print("  ❌ No vision to produce from!")
        return {}

    # Define minimal asset requirements
    requirements = [
        AssetRequirement(
            type=AssetType.SPRITE,
            name="hornet_player",
            description="Main player character - the hornet. Angular, aggressive silhouette with electric blue glow. 64x64 pixels.",
            specs=AssetSpec(format="PNG-32", dimensions=(64, 64)),
            constraints=(),
            priority=1,
            tags=("player", "character", "core"),
        ),
        AssetRequirement(
            type=AssetType.SPRITE,
            name="bee_worker",
            description="Basic enemy - worker bee. Rounded, fuzzy, yellow-black stripes. 32x32 pixels.",
            specs=AssetSpec(format="PNG-32", dimensions=(32, 32)),
            constraints=(),
            priority=1,
            tags=("enemy", "character", "basic"),
        ),
        AssetRequirement(
            type=AssetType.ANIMATION,
            name="metamorphosis_effect",
            description="Visual effect for bee metamorphosis - pulsing glow that intensifies as enemies prepare to combine into Colossals.",
            specs=AssetSpec(format="PNG-32", dimensions=(64, 64), fps=6),
            constraints=(),
            priority=2,
            tags=("effect", "vfx", "metamorphosis"),
        ),
        AssetRequirement(
            type=AssetType.WRITING,
            name="death_screen_flavor",
            description="Flavor text for the death/game-over screen. Should convey 'so close...' grief while encouraging another run.",
            specs=AssetSpec(format="markdown"),
            constraints=(),
            priority=2,
            tags=("ui", "text", "death"),
        ),
        AssetRequirement(
            type=AssetType.WRITING,
            name="colossal_names",
            description="Names and taglines for the 5 Colossal enemy types: THE TIDE, THE RAMPAGE, THE ARTILLERY, THE FORTRESS, THE LEGION.",
            specs=AssetSpec(format="json"),
            constraints=(),
            priority=2,
            tags=("enemy", "text", "lore"),
        ),
    ]

    print(f"\n  📦 Producing {len(requirements)} assets:")

    assets = []
    for req in requirements:
        print(f"\n  🔨 Producing: {req.name} ({req.type.value})...")

        asset = await studio.produce(
            vision=vision,
            requirement=req,
        )

        assets.append(asset)

        print(f"     ✅ Produced! Quality: {asset.quality_score:.2f}")

        # Show preview of content
        if asset.content:
            content_str = (
                asset.content
                if isinstance(asset.content, str)
                else json.dumps(asset.content, indent=2)
            )
            preview = content_str[:300] + "..." if len(content_str) > 300 else content_str
            print("     📝 Preview:")
            for line in preview.split("\n")[:8]:
                print(f"        {line}")

    return {
        "assets": assets,
    }


async def save_results(
    archaeology: dict[str, Any], vision: dict[str, Any], production: dict[str, Any]
) -> None:
    """Save all results to JSON for inspection."""
    output_dir = Path(__file__).parent / "demo_output"
    output_dir.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)

    # Save findings summary
    if archaeology.get("findings"):
        findings = archaeology["findings"]
        findings_data = {
            "pattern_count": len(findings.patterns),
            "patterns": [
                {
                    "name": p.name,
                    "description": p.description,
                    "confidence": p.confidence,
                    "focus": p.focus.value if p.focus else None,
                }
                for p in findings.patterns
            ],
            "sources_analyzed": findings.sources_analyzed,
        }
        path = output_dir / "1_archaeology_findings.json"
        path.write_text(json.dumps(findings_data, indent=2))
        print(f"  📁 Saved: {path}")

    # Save vision
    if vision.get("vision"):
        v = vision["vision"]
        vision_data = {
            "core_insight": v.core_insight,
            "color_palette": {
                "primary": v.color_palette.primary,
                "secondary": v.color_palette.secondary,
                "accent": v.color_palette.accent,
            },
            "typography": {
                "heading": v.typography.heading_font,
                "body": v.typography.body_font,
                "mono": v.typography.mono_font,
            },
            "motion": {
                "timing": v.motion.timing_function,
                "easing": v.motion.easing,
            },
            "tone": {
                "voice": v.tone.voice,
                "personality": v.tone.personality,
                "keywords": list(v.tone.keywords) if v.tone.keywords else [],
            },
        }
        path = output_dir / "2_creative_vision.json"
        path.write_text(json.dumps(vision_data, indent=2))
        print(f"  📁 Saved: {path}")

    # Save style guide
    if vision.get("style_guide"):
        sg = vision["style_guide"]
        guide_data = {
            "rules": [
                {
                    "category": r.category,
                    "rule": r.rule,
                    "rationale": r.rationale,
                }
                for r in sg.rules
            ],
            "examples": [
                {
                    "title": e.title,
                    "description": e.description,
                    "do": e.do_example,
                    "dont": e.dont_example,
                }
                for e in sg.examples
            ]
            if sg.examples
            else [],
        }
        path = output_dir / "3_style_guide.json"
        path.write_text(json.dumps(guide_data, indent=2))
        print(f"  📁 Saved: {path}")

    # Save assets
    if production.get("assets"):
        for asset in production["assets"]:
            asset_data = {
                "id": asset.id,
                "type": asset.type.value,
                "name": asset.name,
                "quality_score": asset.quality_score,
                "content": asset.content,
                "metadata": asset.metadata,
            }
            safe_name = asset.name.replace("/", "_").replace(" ", "_")
            path = output_dir / f"4_asset_{safe_name}.json"
            path.write_text(json.dumps(asset_data, indent=2))
            print(f"  📁 Saved: {path}")

    print(f"\n  🎉 All results saved to: {output_dir}")


async def main() -> None:
    """Run the full demo."""
    print("\n" + "=" * 60)
    print("🎨 CREATIVE PRODUCTION STUDIO DEMO")
    print("    Target: WASM Survivors - Hornet Siege")
    print("=" * 60)

    # Check LLM credentials
    if not has_llm_credentials():
        print("\n❌ No LLM credentials found!")
        print("   Set up Claude CLI or Morpheus Gateway to run this demo.")
        print("   The studio will fall back to scaffold mode (placeholder outputs).")
        print("\n   Continuing with scaffold mode for demonstration...")
    else:
        print("\n✅ LLM credentials found - using real AI generation")

    # Create studio
    studio = CreativeStudioService(use_llm=True)
    print(f"\n📍 Studio created (LLM active: {studio.use_llm})")

    # Phase 1: Archaeology
    archaeology_result = await demo_archaeology(studio)

    # Phase 2: Vision
    vision_result = await demo_vision(studio, archaeology_result)

    # Phase 3: Production
    production_result = await demo_production(studio, vision_result)

    # Save results
    await save_results(archaeology_result, vision_result, production_result)

    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
