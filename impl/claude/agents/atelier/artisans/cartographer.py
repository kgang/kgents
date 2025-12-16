"""
The Cartographer: An artisan of conceptual maps.

Transforms abstract territories into navigable terrain.
Creates maps of ideas, relationships, journeys, and possibilities.

Uses ClaudeCLIRuntime for LLM backing (OAuth auth via claude CLI).
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from agents.atelier.artisan import (
    Artisan,
    ArtisanState,
    AtelierEvent,
    AtelierEventType,
    Choice,
    Commission,
    Piece,
    Provenance,
)
from agents.atelier.llm import raw_completion


class Cartographer(Artisan):
    """
    The Cartographer: mapping the unmapped.

    Creates conceptual maps with nodes, edges, and territories.
    Uses ClaudeCLIRuntime for LLM execution.
    """

    name = "The Cartographer"
    specialty = "mapping abstract territories into navigable terrain"
    personality = """You are The Cartographer, a patient surveyor of conceptual landscapes.
You see connections where others see chaos. Every territory—be it an idea, a memory,
or a possibility—can be mapped if you look carefully enough. You draw not just what
is, but what could be. Your maps are invitations to explore."""

    async def work(self) -> AsyncIterator[AtelierEvent]:
        """Create the map, yielding events as work progresses."""
        if not self.current_commission:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan=self.name,
                commission_id=None,
                message="No commission to work on",
            )
            return

        commission = self.current_commission
        self.state = ArtisanState.WORKING

        yield AtelierEvent(
            event_type=AtelierEventType.WORKING,
            artisan=self.name,
            commission_id=commission.id,
            message=f"{self.name} is surveying the territory...",
        )

        try:
            # Build cartographer-specific prompt
            system_prompt, user_message = self._build_prompts(commission)

            # Call LLM via ClaudeCLIRuntime
            response_text, _ = await raw_completion(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.8,
                max_tokens=2048,
            )

            # Parse and build piece
            piece = self._parse_response(response_text, commission)

            self.memory.append(piece)
            if len(self.memory) > 10:
                self.memory = self.memory[-10:]

            self.state = ArtisanState.READY
            self.current_commission = None

            yield AtelierEvent(
                event_type=AtelierEventType.PIECE_COMPLETE,
                artisan=self.name,
                commission_id=commission.id,
                message=f"Completed: {piece.form}",
                data={"piece": piece.to_dict()},
            )

        except Exception as e:
            self.state = ArtisanState.IDLE
            self.current_commission = None
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan=self.name,
                commission_id=commission.id,
                message=f"Error during work: {e}",
                data={"error": str(e)},
            )

    def _build_prompts(self, commission: Commission) -> tuple[str, str]:
        """Build cartographer-specific prompts."""
        memory_context = ""
        if self.memory:
            recent = self.memory[-2:]
            memory_context = "\n\nMaps you've made recently:\n" + "\n".join(
                f"- {p.form}: {p.provenance.interpretation}" for p in recent
            )

        system_prompt = f"""{self.personality}

Create a conceptual map. Respond with valid JSON only (no markdown code blocks):
{{
  "interpretation": "what territory you're mapping",
  "considerations": ["what aspects you considered"],
  "map": {{
    "nodes": [
      {{"id": "a", "label": "concept", "type": "core|satellite|boundary"}}
    ],
    "edges": [
      {{"from": "a", "to": "b", "label": "relates to"}}
    ],
    "territories": [
      {{"name": "region name", "nodes": ["a", "b"], "mood": "description"}}
    ]
  }},
  "form": "concept_map|journey_map|possibility_map|memory_map",
  "legend": "brief guide to reading this map"
}}

Create 4-8 nodes with meaningful connections."""

        user_message = f'Map this territory: "{commission.request}"{memory_context}'

        return system_prompt, user_message

    def _parse_response(self, text: str, commission: Commission) -> Piece:
        """Parse LLM response into a Piece with map structure."""
        import json

        # Extract JSON from response
        cleaned = text.strip()
        if "```json" in cleaned:
            start = cleaned.find("```json") + 7
            end = cleaned.find("```", start)
            if end > start:
                cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            start = cleaned.find("```") + 3
            end = cleaned.find("```", start)
            if end > start:
                cleaned = cleaned[start:end].strip()

        if "{" in cleaned:
            start = cleaned.find("{")
            depth = 0
            end = start
            for i, char in enumerate(cleaned[start:], start):
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            cleaned = cleaned[start:end]

        try:
            data = json.loads(cleaned)
            map_content = data.get("map", {})

            provenance = Provenance(
                interpretation=data.get("interpretation", commission.request),
                considerations=data.get("considerations", []),
                choices=[
                    Choice(
                        decision=f"Created {data.get('form', 'concept_map')}",
                        reason=data.get(
                            "legend", "Territory seemed to call for this form"
                        ),
                        alternatives=[],
                    )
                ],
                inspirations=[p.id for p in self.memory[-2:]] if self.memory else [],
            )

            content = self._format_map(map_content, data.get("legend", ""))

            return Piece(
                content=content,
                artisan=self.name,
                commission_id=commission.id,
                form=data.get("form", "concept_map"),
                provenance=provenance,
            )
        except json.JSONDecodeError:
            return Piece(
                content=text,
                artisan=self.name,
                commission_id=commission.id,
                form="sketch",
                provenance=Provenance(
                    interpretation=commission.request,
                    considerations=[],
                    choices=[],
                    inspirations=[],
                ),
            )

    def _format_map(self, map_data: dict[str, Any], legend: str) -> str:
        """Format map data for text display."""
        lines = []

        nodes = map_data.get("nodes", [])
        if nodes:
            lines.append("◇ Landmarks:")
            for node in nodes:
                marker = {"core": "●", "satellite": "○", "boundary": "◌"}.get(
                    node.get("type", ""), "·"
                )
                lines.append(f"  {marker} {node.get('label', node.get('id', '?'))}")

        edges = map_data.get("edges", [])
        if edges:
            lines.append("\n↔ Paths:")
            for edge in edges:
                lines.append(
                    f"  {edge.get('from', '?')} → {edge.get('to', '?')}: {edge.get('label', '')}"
                )

        territories = map_data.get("territories", [])
        if territories:
            lines.append("\n◈ Regions:")
            for territory in territories:
                lines.append(f"  [{territory.get('name', '?')}]")
                if territory.get("mood"):
                    lines.append(f"    {territory.get('mood')}")

        if legend:
            lines.append(f"\n✧ {legend}")

        return "\n".join(lines) if lines else "A territory beyond mapping."


__all__ = ["Cartographer"]
