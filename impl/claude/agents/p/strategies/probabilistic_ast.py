"""
Probabilistic AST Parser: Confidence-Scored Tree Nodes (Phase 3: Novel Techniques)

The Principle: Instead of binary AST (valid/invalid), build an AST where every node
has a confidence score.

Why It's Better:
- Partial trust: Use high-confidence fields, ignore low-confidence ones
- Explainable: Know which parts of the parse are uncertain
- Adaptive: Adjust min_confidence threshold based on use case

Use Cases:
- E-gent code validation: Mark repaired imports as low-confidence
- B-gent hypothesis parsing: Track confidence of inferred fields
- L-gent catalog metadata: Mark auto-inferred tags as low-confidence
"""

import json
from dataclasses import dataclass, field
from typing import Any, Optional

from agents.p.core import Parser, ParserConfig, ParseResult


@dataclass
class ProbabilisticASTNode:
    """
    AST node with confidence score.

    Every node tracks:
    - type: The node type (object, array, string, number, etc.)
    - value: The parsed value
    - confidence: Confidence score 0.0-1.0
    - children: Child nodes (for objects/arrays)
    - repair_applied: What repair was applied (if any)
    """

    type: str  # "object", "array", "string", "number", "boolean", "null"
    value: Any
    confidence: float  # 0.0-1.0
    children: list["ProbabilisticASTNode"] = field(default_factory=list)
    repair_applied: Optional[str] = None
    path: str = "root"  # Path in AST (e.g., "root.data.items[0].name")

    def to_dict(self) -> dict:
        """Convert node to dict representation."""
        result = {
            "type": self.type,
            "value": self.value
            if self.type != "object" and self.type != "array"
            else None,
            "confidence": self.confidence,
            "path": self.path,
        }

        if self.repair_applied:
            result["repair_applied"] = self.repair_applied

        if self.children:
            result["children"] = [child.to_dict() for child in self.children]

        return result

    def get_confident_value(self, min_confidence: float = 0.8) -> Any:
        """
        Extract value only if confidence meets threshold.

        Returns None if confidence too low.
        """
        if self.confidence < min_confidence:
            return None

        if self.type == "object":
            # For objects, recursively get confident children
            result = {}
            for child in self.children:
                if child.confidence >= min_confidence:
                    key = child.path.split(".")[-1]
                    result[key] = child.get_confident_value(min_confidence)
            return result

        elif self.type == "array":
            # For arrays, filter confident children
            result = []
            for child in self.children:
                confident_val = child.get_confident_value(min_confidence)
                if confident_val is not None:
                    result.append(confident_val)
            return result

        else:
            return self.value


@dataclass
class ProbabilisticASTParser(Parser[ProbabilisticASTNode]):
    """
    Parse text into probabilistic AST with per-node confidence scores.

    The parser tries to parse JSON/YAML, applies repairs if needed,
    and builds an AST where each node has a confidence score.

    Lower confidence indicates:
    - Repairs were applied
    - Heuristic inference was used
    - Structure was incomplete

    Example:
        parser = ProbabilisticASTParser()
        result = parser.parse('{"name": "test", "count": "42"}')  # count should be int
        ast = result.value

        # Get only high-confidence fields
        confident = ast.get_confident_value(min_confidence=0.8)
    """

    config: ParserConfig = field(default_factory=ParserConfig)

    def parse(self, text: str) -> ParseResult[ProbabilisticASTNode]:
        """
        Parse text into probabilistic AST.

        Tries:
        1. Direct JSON parse (confidence=1.0)
        2. Repaired JSON parse (confidence=0.6)
        3. Heuristic extraction (confidence=0.3)
        """
        # Try direct parse first
        try:
            data = json.loads(text)
            ast = self._build_ast(data, confidence=1.0, path="root")
            return ParseResult[ProbabilisticASTNode](
                success=True,
                value=ast,
                confidence=1.0,
                strategy="probabilistic-ast-direct",
            )
        except json.JSONDecodeError:
            pass

        # Try with repairs
        repaired, repairs = self._repair_json(text)
        if repaired:
            try:
                data = json.loads(repaired)
                ast = self._build_ast(
                    data,
                    confidence=0.6,
                    path="root",
                    repair="Applied repairs: " + ", ".join(repairs),
                )
                return ParseResult[ProbabilisticASTNode](
                    success=True,
                    value=ast,
                    confidence=0.6,
                    strategy="probabilistic-ast-repaired",
                    repairs=repairs,
                )
            except json.JSONDecodeError:
                pass

        # Try heuristic extraction
        extracted = self._heuristic_extract(text)
        if extracted:
            return ParseResult[ProbabilisticASTNode](
                success=True,
                value=extracted,
                confidence=0.3,
                strategy="probabilistic-ast-heuristic",
                repairs=["Heuristic extraction applied"],
            )

        return ParseResult[ProbabilisticASTNode](
            success=False, error="Failed to parse as probabilistic AST"
        )

    def _build_ast(
        self,
        data: Any,
        confidence: float,
        path: str,
        repair: Optional[str] = None,
    ) -> ProbabilisticASTNode:
        """Build probabilistic AST from parsed data."""
        if isinstance(data, dict):
            children = []
            for key, value in data.items():
                child_path = f"{path}.{key}"
                child_confidence = confidence
                child_repair = repair

                # Type coercion lowers confidence
                if isinstance(value, str) and value.isdigit():
                    child_confidence *= 0.9
                    child_repair = "String looks like number"

                child = self._build_ast(
                    value, child_confidence, child_path, child_repair
                )
                children.append(child)

            return ProbabilisticASTNode(
                type="object",
                value=data,
                confidence=confidence,
                children=children,
                repair_applied=repair,
                path=path,
            )

        elif isinstance(data, list):
            children = []
            for i, item in enumerate(data):
                child_path = f"{path}[{i}]"
                child = self._build_ast(item, confidence, child_path, repair)
                children.append(child)

            return ProbabilisticASTNode(
                type="array",
                value=data,
                confidence=confidence,
                children=children,
                repair_applied=repair,
                path=path,
            )

        elif isinstance(data, str):
            return ProbabilisticASTNode(
                type="string",
                value=data,
                confidence=confidence,
                repair_applied=repair,
                path=path,
            )

        elif isinstance(data, (int, float)):
            return ProbabilisticASTNode(
                type="number",
                value=data,
                confidence=confidence,
                repair_applied=repair,
                path=path,
            )

        elif isinstance(data, bool):
            return ProbabilisticASTNode(
                type="boolean",
                value=data,
                confidence=confidence,
                repair_applied=repair,
                path=path,
            )

        else:
            return ProbabilisticASTNode(
                type="null",
                value=None,
                confidence=confidence,
                repair_applied=repair,
                path=path,
            )

    def _repair_json(self, text: str) -> tuple[Optional[str], list[str]]:
        """
        Attempt to repair malformed JSON.

        Returns (repaired_text, list_of_repairs) or (None, []) if repair failed.
        """
        repairs = []
        repaired = text.strip()

        # Remove trailing commas
        if repaired.endswith(",}") or repaired.endswith(",]"):
            repaired = repaired[:-2] + repaired[-1]
            repairs.append("Removed trailing comma")

        # Add missing closing braces
        open_braces = repaired.count("{") - repaired.count("}")
        open_brackets = repaired.count("[") - repaired.count("]")

        if open_braces > 0:
            repaired += "}" * open_braces
            repairs.append(f"Added {open_braces} closing braces")

        if open_brackets > 0:
            repaired += "]" * open_brackets
            repairs.append(f"Added {open_brackets} closing brackets")

        # Fix unquoted keys (simple heuristic)
        # This is a simplified version - real implementation would need proper parser
        import re

        unquoted_key_pattern = r"(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:"
        if re.search(unquoted_key_pattern, repaired):
            repaired = re.sub(unquoted_key_pattern, r'\1 "\2":', repaired)
            repairs.append("Quoted unquoted keys")

        if repairs:
            return repaired, repairs
        return None, []

    def _heuristic_extract(self, text: str) -> Optional[ProbabilisticASTNode]:
        """
        Heuristic extraction when JSON parsing fails entirely.

        Looks for key-value pairs using regex.
        """
        import re

        # Try to extract key-value pairs
        # Pattern: "key": value or key: value
        pattern = r'["\']?(\w+)["\']?\s*:\s*([^,\}\]]+)'
        matches = re.findall(pattern, text)

        if matches:
            data = {}
            for key, value in matches:
                # Clean up value
                value = value.strip().strip('"').strip("'")
                data[key] = value

            return self._build_ast(
                data,
                confidence=0.3,
                path="root",
                repair="Heuristic key-value extraction",
            )

        return None

    def parse_stream(
        self, tokens: list[str]
    ) -> list[ParseResult[ProbabilisticASTNode]]:
        """
        Stream parsing for probabilistic AST.

        Buffers tokens and parses when sufficient for a node.
        """
        text = "".join(tokens)
        return [self.parse(text)]

    def configure(self, **config_updates) -> "ProbabilisticASTParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return ProbabilisticASTParser(config=new_config)


def query_confident_fields(
    ast: ProbabilisticASTNode, min_confidence: float = 0.8
) -> dict:
    """
    Extract only high-confidence fields from probabilistic AST.

    This is the primary way to use probabilistic ASTs:
    1. Parse with repairs (gets low-confidence nodes)
    2. Query for confident fields (filters by threshold)
    3. Use only the data you trust

    Example:
        result = parser.parse(malformed_json)
        confident = query_confident_fields(result.value, min_confidence=0.7)
        # Only fields with confidence >= 0.7
    """
    return ast.get_confident_value(min_confidence)


def get_low_confidence_paths(
    ast: ProbabilisticASTNode, max_confidence: float = 0.5
) -> list[str]:
    """
    Find all paths in the AST with confidence below threshold.

    Useful for debugging and understanding what was repaired.

    Example:
        result = parser.parse(malformed_json)
        uncertain = get_low_confidence_paths(result.value, max_confidence=0.6)
        # ["root.data.count", "root.items[2].name"]
    """
    paths = []

    def traverse(node: ProbabilisticASTNode):
        if node.confidence <= max_confidence:
            paths.append(node.path)
        for child in node.children:
            traverse(child)

    traverse(ast)
    return paths
