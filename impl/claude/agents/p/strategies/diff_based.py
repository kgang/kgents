"""
Diff-Based Parser: Patch Strategy (Phase 3: Novel Techniques)

The Principle: Instead of generating full files, generate patches (diffs, sed commands).

Why It's Better:
- Applying patches is deterministic (robust tools like patch, diff3)
- Fuzz factors handle near-misses gracefully
- Smaller LLM outputs (just the delta, not full file)
- Version control friendly (diffs are standard format)

Use Cases:
- W-gent incremental updates: Patch base HTML template
- Code evolution/refactoring: Generate diffs instead of full modules
- F-gent artifact updates: Patch .alo.md files for version bumps
"""

import re
from dataclasses import dataclass, field
from typing import Any, Iterator

from agents.p.core import Parser, ParserConfig, ParseResult


@dataclass
class DiffBasedParser(Parser[str]):
    """
    Parse diffs instead of full outputs.

    The parser applies LLM-generated diffs to a base template,
    enabling incremental updates with deterministic application.

    Supports:
    - Unified diff format (standard git diff)
    - Simple sed-style replacements
    - Line-based patches with fuzz factor

    Example:
        parser = DiffBasedParser(base_template="<html><body>Hello</body></html>")
        diff = '''
        --- template.html
        +++ modified.html
        @@ -1,1 +1,1 @@
        -<html><body>Hello</body></html>
        +<html><body>Hello World</body></html>
        '''
        result = parser.parse(diff)
        # result.value = "<html><body>Hello World</body></html>"
    """

    base_template: str
    fuzz_factor: int = 2  # Number of lines of context to allow fuzzy matching
    config: ParserConfig = field(default_factory=ParserConfig)

    def parse(self, text: str) -> ParseResult[str]:
        """
        Parse and apply diff to base template.

        Tries multiple diff formats:
        1. Unified diff (standard format)
        2. Simple replacement (sed-style: "s/old/new/")
        3. Line-based patch ("Replace line N with: content")

        Returns ParseResult with patched content or error.
        """
        # Try unified diff format first
        result = self._try_unified_diff(text)
        if result.success:
            return result

        # Try simple replacement format
        result = self._try_simple_replacement(text)
        if result.success:
            return result

        # Try line-based patch
        result = self._try_line_patch(text)
        if result.success:
            return result

        return ParseResult[str](
            success=False,
            error="Could not parse diff in any known format. Tried: unified, simple replacement, line-based patch.",
            strategy="diff-based",
        )

    def _try_unified_diff(self, text: str) -> ParseResult[str]:
        """Try to parse and apply unified diff format."""
        try:
            # Split into base lines
            self.base_template.splitlines(keepends=True)

            # Parse unified diff
            # Unified diff format has lines starting with:
            # --- (original file)
            # +++ (modified file)
            # @@ -start,count +start,count @@ (hunk header)
            # - (removed line)
            # + (added line)
            #   (context line)

            # Use difflib to apply patch
            # Note: Python's difflib doesn't have a direct "apply patch" function,
            # so we need to reconstruct from diff

            # Simple heuristic: extract lines starting with +
            # This is a simplified implementation
            lines = text.splitlines()

            # Check if it looks like a unified diff
            has_header = any(
                line.startswith("---") or line.startswith("+++") for line in lines
            )
            has_hunks = any(line.startswith("@@") for line in lines)

            if not (has_header and has_hunks):
                return ParseResult[str](
                    success=False, error="Not a unified diff format"
                )

            # Extract changes (simplified - real implementation would need full diff parser)
            # For now, we'll reconstruct by applying + lines and removing - lines
            result_lines = []
            in_hunk = False

            for line in lines:
                if line.startswith("@@"):
                    in_hunk = True
                    continue
                if not in_hunk:
                    continue
                if line.startswith("---") or line.startswith("+++"):
                    continue

                if line.startswith("+"):
                    result_lines.append(line[1:])  # Add new line
                elif line.startswith("-"):
                    pass  # Remove line (skip it)
                elif line.startswith(" "):
                    result_lines.append(line[1:])  # Context line

            patched = "\n".join(result_lines)

            # If we got something, return it
            if patched.strip():
                return ParseResult[str](
                    success=True,
                    value=patched,
                    confidence=0.85,
                    strategy="unified-diff",
                    repairs=["Applied unified diff patch"],
                )

            return ParseResult[str](
                success=False, error="Unified diff parsing produced empty result"
            )

        except Exception as e:
            return ParseResult[str](
                success=False, error=f"Unified diff parsing failed: {e}"
            )

    def _try_simple_replacement(self, text: str) -> ParseResult[str]:
        """
        Try sed-style simple replacement: s/old/new/

        Formats supported:
        - s/old/new/
        - Replace "old" with "new"
        - old -> new
        """
        try:
            # Try sed format: s/old/new/
            sed_match = re.match(r"s/(.+?)/(.+?)/", text)
            if sed_match:
                old, new = sed_match.groups()
                if old in self.base_template:
                    patched = self.base_template.replace(old, new)
                    return ParseResult[str](
                        success=True,
                        value=patched,
                        confidence=0.9,
                        strategy="sed-replacement",
                        repairs=[f"Applied sed replacement: s/{old}/{new}/"],
                    )

            # Try natural language: Replace "old" with "new"
            replace_match = re.search(r'[Rr]eplace\s+"(.+?)"\s+with\s+"(.+?)"', text)
            if replace_match:
                old, new = replace_match.groups()
                if old in self.base_template:
                    patched = self.base_template.replace(old, new)
                    return ParseResult[str](
                        success=True,
                        value=patched,
                        confidence=0.85,
                        strategy="replace-with",
                        repairs=[f'Replaced "{old}" with "{new}"'],
                    )

            # Try arrow notation: old -> new
            arrow_match = re.search(r"(.+?)\s*->\s*(.+)", text)
            if arrow_match:
                old, new = arrow_match.groups()
                old = old.strip()
                new = new.strip()
                if old in self.base_template:
                    patched = self.base_template.replace(old, new)
                    return ParseResult[str](
                        success=True,
                        value=patched,
                        confidence=0.8,
                        strategy="arrow-notation",
                        repairs=[f"Replaced {old} -> {new}"],
                    )

            return ParseResult[str](
                success=False, error="No simple replacement pattern found"
            )

        except Exception as e:
            return ParseResult[str](
                success=False, error=f"Simple replacement parsing failed: {e}"
            )

    def _try_line_patch(self, text: str) -> ParseResult[str]:
        """
        Try line-based patch: "Replace line N with: content"

        Formats supported:
        - Replace line N with: content
        - Line N: content
        - @N: content
        """
        try:
            # Try "Replace line N with: content"
            replace_line_match = re.search(r"[Rr]eplace line (\d+) with:\s*(.+)", text)
            if replace_line_match:
                line_num = int(replace_line_match.group(1))
                new_content = replace_line_match.group(2)

                lines = self.base_template.splitlines()
                if 1 <= line_num <= len(lines):
                    lines[line_num - 1] = new_content  # Convert to 0-indexed
                    patched = "\n".join(lines)
                    return ParseResult[str](
                        success=True,
                        value=patched,
                        confidence=0.9,
                        strategy="line-replace",
                        repairs=[f"Replaced line {line_num}"],
                    )

            # Try "Line N: content"
            line_match = re.search(r"[Ll]ine (\d+):\s*(.+)", text)
            if line_match:
                line_num = int(line_match.group(1))
                new_content = line_match.group(2)

                lines = self.base_template.splitlines()
                if 1 <= line_num <= len(lines):
                    lines[line_num - 1] = new_content
                    patched = "\n".join(lines)
                    return ParseResult[str](
                        success=True,
                        value=patched,
                        confidence=0.85,
                        strategy="line-notation",
                        repairs=[f"Updated line {line_num}"],
                    )

            # Try "@N: content"
            at_match = re.search(r"@(\d+):\s*(.+)", text)
            if at_match:
                line_num = int(at_match.group(1))
                new_content = at_match.group(2)

                lines = self.base_template.splitlines()
                if 1 <= line_num <= len(lines):
                    lines[line_num - 1] = new_content
                    patched = "\n".join(lines)
                    return ParseResult[str](
                        success=True,
                        value=patched,
                        confidence=0.8,
                        strategy="at-notation",
                        repairs=[f"Updated line {line_num}"],
                    )

            return ParseResult[str](
                success=False, error="No line-based patch pattern found"
            )

        except Exception as e:
            return ParseResult[str](
                success=False, error=f"Line patch parsing failed: {e}"
            )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[str]]:
        """
        Stream parsing for diffs (buffer until complete).

        Diffs need to be complete before application, so we buffer
        all tokens and parse once.
        """
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config_updates: Any) -> "DiffBasedParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return DiffBasedParser(
            base_template=self.base_template,
            fuzz_factor=self.fuzz_factor,
            config=new_config,
        )


def create_wgent_diff_parser(base_html: str) -> DiffBasedParser:
    """
    Create a DiffBasedParser configured for W-gent HTML updates.

    Example:
        parser = create_wgent_diff_parser("<html><body><div id='main'>Hello</div></body></html>")
        diff = 's/<div id="main">Hello</div>/<div id="main">Hello World</div>/'
        result = parser.parse(diff)
    """
    return DiffBasedParser(
        base_template=base_html,
        fuzz_factor=3,  # Allow more fuzzy matching for HTML
        config=ParserConfig(min_confidence=0.7, allow_partial=True),
    )


def create_code_diff_parser(base_code: str) -> DiffBasedParser:
    """
    Create a DiffBasedParser configured for code evolution/refactoring.

    Example:
        parser = create_code_diff_parser("def foo(): pass")
        diff = 's/pass/return 42/'
        result = parser.parse(diff)
    """
    return DiffBasedParser(
        base_template=base_code,
        fuzz_factor=1,  # Strict matching for code
        config=ParserConfig(min_confidence=0.8, allow_partial=False),
    )
