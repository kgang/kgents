# P-gents: Parser Agents

**Status**: Specification v2.0 (Frontier Research Integration)
**Session**: 2025-12-08 - Parser Analysis + Stochastic-Structural Gap Architecture

---

## The Stochastic-Structural Gap

> **The fundamental challenge**: LLMs produce **probability distributions over token sequences**. Compilers and renderers demand **deterministic syntactic structures**. P-gents bridge this gap.

### The Problem Statement

Traditional parsers fail on LLM outputs because they were designed for **deterministic programs** written by humans who understand syntax rules. LLMs don't "know" syntax—they sample from learned distributions. The result:

- **Unclosed brackets** when the model truncates mid-generation
- **Trailing commas** from training on permissive JavaScript
- **Malformed nesting** when context windows fill up
- **Format drift** when prompts evolve but parsers stay rigid

Standard "retry logic" is **expensive** (multiple LLM calls). "Reducing complexity" **limits capability** (dumbed-down outputs). **P-gents solve this at the architectural level.**

---

## Philosophy

> **Fuzzy coercion without opinion**

P-gents transform probabilistic text into structured data by operating across the **Prevention ← → Correction** spectrum:

- **Prevention** (left): Constrain generation to make invalid outputs mathematically impossible
- **Correction** (center): Repair malformed outputs with high-confidence heuristics
- **Novel** (right): First-principles techniques that reframe the problem entirely

**The dual nature of parsing**:
- **Traditional Parsing**: Exact syntax → AST (binary: success or exception)
- **P-genting**: Fuzzy text → ParseResult[A] (graduated: confidence ∈ [0.0, 1.0])

---

## Design Principles (Grounded in kgents Philosophy)

### 1. **Tasteful** - Each parser serves ONE extraction purpose
- A parser extracts ONE data shape, not multiple formats
- Parsing strategy != Parser (strategy is composable unit)
- No "universal parser" that handles everything

### 2. **Curated** - Prefer composition over configuration
- Few excellent strategies > many mediocre ones
- Dead strategies should be removed, not accumulated
- Configuration should guide behavior, not replace design

### 3. **Ethical** - Honest about uncertainty
- Parsers return **confidence scores** (0.0-1.0), not just success/fail
- Partial parses are valid when confidence-scored
- Never silently drop data—signal what was lost
- Track **repairs** applied (transparency about coercion)

### 4. **Joy-Inducing** - Parsing shouldn't feel like fighting
- Fallback chains feel like "oh, it just worked"
- Stream-repair creates "live wire" experiences (W-gent)
- Error messages explain what was expected, what was found
- Repair strategies feel like gentle guidance, not hacks

### 5. **Composable** - Parsers are morphisms
```
Parser[Text, A] : Text → ParseResult[A]
```

**The Minimal Output Principle applies**:
- A parser extracts ONE unit of A, not `[A]`
- To parse N items, invoke parser N times (or map over list)
- Composition happens at pipeline level, not parser level

**Composition patterns**:
```python
# Sequential fallback (try strategies in order)
parser = Fallback(ConstrainedGeneration(), StreamRepair(), AnchorExtraction())

# Parallel fusion (merge multiple parsers' results)
parser = Fuse(StructureParser(), ContentParser())

# Conditional selection (choose parser based on input)
parser = Switch({
    "code": CodeParser(),
    "json": JsonParser(),
    "hypothesis": HypothesisParser()
})
```

### 6. **Heterarchical** - Strategies can be autonomous or invoked
- A parsing strategy can **run autonomously** (streaming mode for W-gent)
- Same strategy can be **invoked functionally** (single parse)
- No fixed "orchestrator" strategy—context determines leader

### 7. **Generative** - Spec compresses parsing wisdom
- This spec regenerates ~2,400 lines of parsing code + frontier research
- Target: ~800 lines of implementation (67% compression)
- Implementation follows from understanding the Stochastic-Structural Gap

---

## Core Types

### ParseResult[A]
```python
@dataclass
class ParseResult[A]:
    """Result of parsing operation with full transparency."""
    success: bool
    value: Optional[A] = None
    strategy: Optional[str] = None      # Which strategy succeeded
    confidence: float = 0.0              # 0.0-1.0
    error: Optional[str] = None          # What went wrong
    partial: bool = False                # Is this a partial parse?
    repairs: list[str] = field(default_factory=list)  # Applied repairs (ethical transparency)
    stream_position: Optional[int] = None  # For incremental parsing
    metadata: dict[str, Any] = field(default_factory=dict)  # Strategy-specific info
```

**Invariants**:
- `success=True` implies `value is not None`
- `success=True` implies `confidence > 0.0`
- `success=False` implies `error is not None`
- `partial=True` implies `confidence < 1.0`
- `repairs` non-empty implies `confidence` penalty applied

### Parser[A] Protocol
```python
class Parser[A](Protocol):
    """
    Parser transforms fuzzy text into structured data.

    Unlike traditional parsers, P-gents:
    - Accept ANY text (no syntax errors, only parse failures)
    - Return confidence scores (quantify uncertainty)
    - Support partial parsing (degrade gracefully)
    - Support streaming (heterarchical: autonomous mode)
    - Compose via fallback/fusion/switch
    """

    def parse(self, text: str) -> ParseResult[A]:
        """Parse complete text into structured data."""
        ...

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[A]]:
        """Parse token stream incrementally (optional, for streaming)."""
        ...

    def configure(self, **config) -> "Parser[A]":
        """Return new parser with updated configuration."""
        ...
```

**Categorical Structure**:
- **Objects**: Types `A`, `B`, `C`, ...
- **Morphisms**: `Parser[A]` is a morphism `Text → ParseResult[A]`
- **Identity**: `IdentityParser` (returns text as-is, confidence=1.0)
- **Composition**: See composition patterns below

---

## The Prevention ← → Correction ← → Novel Spectrum

P-gent strategies span from **prevention** (constrain generation) to **correction** (repair outputs) to **novel** (reframe the problem).

---

## Phase 1: Prevention (Logit-Level Constraint)

> **The most efficient way to handle fuzzy output is to make it mathematically impossible for the output to be fuzzy.**

Instead of generating text and hoping it parses, we intervene at the **generation step** (the forward pass) inside the inference engine.

### Strategy 1.1: Context-Free Grammar (CFG) Logit Masking

**The Principle**: At every token generation step, calculate which tokens would violate a formal grammar and set their logits to −∞.

**Python Implementation**:
```python
from outlines import models, generate

# Define grammar
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "count": {"type": "integer"}
    },
    "required": ["name", "count"]
}

# Constrained generation
model = models.transformers("meta-llama/Llama-3.1-8B")
generator = generate.json(model, json_schema)

result = generator("Generate a person object:")
# result is GUARANTEED to be valid JSON matching schema
```

**Libraries**:
- **`Outlines`**: CFG-constrained generation for any LLM
- **`Guidance`**: Microsoft's constrained generation library
- **`llama-cpp-python` (GBNF grammars)**: For local GGUF models

**When to Use**:
- Output format is **known ahead of time** (JSON schema, HTML structure)
- You control the inference engine (local models or API supports grammar)
- Performance is critical (prevents retry loops)

**Limitations**:
- Requires access to logits (not all APIs expose this)
- Grammar must be **context-free** (can't encode semantic constraints)
- Reduces LLM creativity (sometimes you want free-form content)

**kgents Use Cases**:
- **F-gent contract generation**: Guarantee valid contract structure
- **B-gent hypothesis format**: Enforce HYPOTHESES / REASONING / TESTS sections
- **W-gent HTML generation**: Prevent unclosed tags at generation time

---

### Strategy 1.2: Fill-in-the-Middle (FIM) Sandwich

**The Principle**: Provide the `prefix` (opening structure) and `suffix` (closing structure), force LLM to generate only the content.

**Implementation**:
```python
prefix = '{"name": "'
suffix = '", "age": 42}'

# Use FIM-trained model (CodeLlama, StarCoder)
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("codellama/CodeLlama-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("codellama/CodeLlama-7b-hf")

# FIM format: <PRE> prefix <SUF> suffix <MID>
fim_prompt = f"<PRE>{prefix}<SUF>{suffix}<MID>"
tokens = tokenizer(fim_prompt, return_tensors="pt")
output = model.generate(**tokens, max_new_tokens=50)

# Result: prefix + <generated content> + suffix
# Parser NEVER fails on root structure (you hardcoded it)
```

**When to Use**:
- Root structure is **predictable** (JSON object, HTML document)
- Content is **free-form** (user description, narrative text)
- Using FIM-capable models (CodeLlama, StarCoder, Qwen-Coder)

**kgents Use Cases**:
- **W-gent live dashboards**: Hardcode `<html><body><div id="main">` ... `</div></body></html>`, LLM fills content
- **F-gent .alo.md format**: Hardcode YAML frontmatter delimiters `---\n` ... `---`, LLM fills metadata
- **D-gent state serialization**: Hardcode JSON structure, LLM fills state values

---

### Strategy 1.3: Type-Guided Generation (Pydantic Constraints)

**The Principle**: Use Pydantic models to define output structure, instruct LLM to generate Python code that instantiates the model.

**Implementation**:
```python
from pydantic import BaseModel, Field

class HypothesisOutput(BaseModel):
    statement: str = Field(..., min_length=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    falsifiable_by: list[str] = Field(..., min_items=1)

# Prompt: "Write Python code that creates a HypothesisOutput object"
llm_response = '''
HypothesisOutput(
    statement="The system exhibits chaotic behavior under high load",
    confidence=0.75,
    falsifiable_by=["Load test with >1000 concurrent users shows stable latency"]
)
'''

# Parse via exec (sandboxed)
result = eval(llm_response, {"HypothesisOutput": HypothesisOutput})
# Pydantic validates types automatically, raises ValidationError if wrong
```

**Why It's Better**:
- LLMs are better at **code** than **JSON** (code is more represented in training data)
- Pydantic provides **precise error messages** ("confidence must be ≤ 1.0")
- Errors can be **fed back to LLM** for targeted fixes (reflection)

**Security Note**: Use `ast.literal_eval()` or restricted `exec()` with limited globals to prevent code injection.

**kgents Use Cases**:
- **B-gent hypothesis generation**: Define `Hypothesis` Pydantic model, LLM writes instantiation code
- **F-gent contract synthesis**: Define `Contract` model, LLM generates conforming code
- **Reflection loops**: If Pydantic raises ValidationError, feed error back to LLM for repair

---

## Phase 2: Correction (Stream-Repair & Partial Parsing)

> **If we must allow free-form generation, we need parsers that don't crash on incomplete data.**

Standard Python `json.loads()` or `xml.etree` are binary: success or exception. For streaming experiences (W-gent "Live Wire"), we need **fault-tolerant streaming parsers**.

### Strategy 2.1: Stack-Balancing Stream Processor

**The Algorithm**:
1. Create a Python generator that yields chunks of tokens
2. Maintain a **Tag Stack** (LIFO) in memory for HTML/XML, **Bracket Stack** for JSON
3. When stream ends or pauses, **virtually append closing delimiters** before rendering
4. Keep stream open for more tokens

**Implementation**:
```python
class StackBalancingParser:
    """Stream parser that auto-closes unclosed structures."""

    def __init__(self, opener: str = "{", closer: str = "}"):
        self.opener = opener
        self.closer = closer
        self.stack = []
        self.buffer = ""

    def parse_stream(self, token_stream: Iterator[str]) -> Iterator[ParseResult[dict]]:
        for token in token_stream:
            self.buffer += token

            # Update stack
            self.stack.extend([opener for opener in self.buffer if opener == self.opener])
            self.stack = self.stack[:len(self.stack) - self.buffer.count(self.closer)]

            # Try to parse current buffer
            # If incomplete, auto-close for rendering
            balanced = self.buffer + (self.closer * len(self.stack))

            try:
                value = json.loads(balanced)
                yield ParseResult(
                    success=True,
                    value=value,
                    confidence=0.8 if self.stack else 1.0,  # Reduced if auto-closed
                    partial=bool(self.stack),
                    stream_position=len(self.buffer)
                )
            except json.JSONDecodeError:
                continue  # Wait for more tokens
```

**Use Cases**:
- **W-gent real-time dashboards**: Render partial HTML while LLM streams
- **Live JSON API responses**: Show progressive results as they arrive
- **F-gent prototype streaming**: Display code as it's generated

---

### Strategy 2.2: Structural Decoupling (Jsonformer Approach)

**The Principle**: Decouple **value generation** (LLM's job) from **structural generation** (parser's job).

**Don't ask for**: `{"key": "value"}`
**Instead**:
1. Parser prints `{"key": "`
2. LLM generates `value`
3. Parser prints `"}`

**Implementation**:
```python
class StructuralDecouplingParser:
    """Parser controls structure, LLM controls content."""

    def parse_with_schema(self, schema: dict, llm_func: Callable[[str], str]) -> dict:
        result = {}

        for key, value_type in schema.items():
            # Parser controls the structure
            prompt = f"Generate a {value_type} for field '{key}':"

            # LLM controls only the value
            raw_value = llm_func(prompt)

            # Parser coerces to type
            if value_type == "string":
                result[key] = raw_value.strip().strip('"')
            elif value_type == "number":
                result[key] = float(raw_value.strip())
            elif value_type == "boolean":
                result[key] = raw_value.strip().lower() in ("true", "yes", "1")

        return result

# Usage
schema = {"name": "string", "age": "number", "active": "boolean"}
parser = StructuralDecouplingParser()
result = parser.parse_with_schema(schema, llm_generate_function)
# Result is GUARANTEED to match schema structure
```

**Guarantees**:
- Parser **never** receives malformed structure (it created the structure)
- LLM can't hallucinate extra fields or wrong types
- Suitable for **W-gent**: W-gent controls HTML tags, LLM fills text content

**kgents Use Cases**:
- **W-gent HTML generation**: W-gent: `<div class="card">`, LLM: `content`, W-gent: `</div>`
- **F-gent artifact assembly**: F-gent controls .alo.md structure, LLM fills sections
- **B-gent hypothesis fields**: Parser controls format, LLM fills statement/reasoning

---

### Strategy 2.3: Incremental Parsing (Build AST as Tokens Arrive)

**The Principle**: Build AST incrementally, mark nodes as "incomplete" until closing tokens arrive.

**Implementation** (Simplified):
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class IncrementalNode:
    """AST node with completion status."""
    type: str  # "object", "array", "string", etc.
    value: Any
    complete: bool = False
    confidence: float = 0.5
    children: list["IncrementalNode"] = field(default_factory=list)

class IncrementalJsonParser:
    """Build JSON AST incrementally as tokens arrive."""

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[IncrementalNode]:
        buffer = ""
        stack = [IncrementalNode(type="root", value=None)]

        for token in tokens:
            buffer += token

            # Try to parse current buffer
            try:
                parsed = json.loads(buffer)
                root = self._build_incremental_ast(parsed, complete=True)
                yield root
                return
            except json.JSONDecodeError:
                # Build partial AST
                partial_ast = self._parse_partial(buffer)
                yield partial_ast

    def _parse_partial(self, text: str) -> IncrementalNode:
        # Simplified: Use regex to identify incomplete structures
        if text.strip().startswith("{"):
            return IncrementalNode(
                type="object",
                value={},  # Partial value
                complete=False,
                confidence=0.3
            )
        # ... handle other cases
```

**Benefits**:
- **Progressive rendering**: Show partial results immediately
- **Early validation**: Detect errors before full generation completes
- **Confidence tracking**: Nodes have individual confidence scores

**kgents Use Cases**:
- **W-gent**: Render partial visualizations as data arrives
- **E-gent code generation**: Highlight complete functions while others are still generating
- **B-gent hypothesis streaming**: Show hypotheses as they're generated

---

### Strategy 2.4: Lazy Validation (Defer Until Access)

**The Principle**: Parse optimistically, validate only when fields are accessed.

**Implementation**:
```python
class LazyValidatedDict:
    """Dict that validates fields lazily on access."""

    def __init__(self, raw_data: dict, schema: dict):
        self._data = raw_data
        self._schema = schema
        self._validated = {}

    def __getitem__(self, key: str):
        if key not in self._validated:
            # Validate on first access
            raw_value = self._data.get(key)
            expected_type = self._schema.get(key, str)

            try:
                validated = self._coerce(raw_value, expected_type)
                self._validated[key] = validated
            except ValueError as e:
                raise KeyError(f"Field '{key}' validation failed: {e}")

        return self._validated[key]

    def _coerce(self, value, expected_type):
        if expected_type == float:
            return float(value)
        elif expected_type == int:
            return int(value)
        elif expected_type == bool:
            return str(value).lower() in ("true", "yes", "1")
        return str(value)

# Usage
raw = {"confidence": "0.75", "name": "Test"}  # Malformed (string instead of float)
lazy = LazyValidatedDict(raw, {"confidence": float, "name": str})

lazy["name"]  # Works fine, returns "Test"
lazy["confidence"]  # Auto-coerces "0.75" → 0.75
```

**Benefits**:
- **Fast initial parse**: No upfront validation cost
- **Tolerant of extra fields**: Ignores unknown keys until accessed
- **Clear error messages**: Errors tied to specific field access

**kgents Use Cases**:
- **D-gent state deserialization**: Only validate fields actually used
- **L-gent catalog entries**: Defer validation of optional metadata
- **Performance optimization**: Skip validation for debug-only fields

---

## Phase 3: Code-as-Schema (Hybrid Prevention + Correction)

> **LLMs are often better at writing Python code than they are at writing strict JSON/YAML.**

### Strategy 3.1: Executable Coercion (Pydantic Method)

**Expanded from 1.3**: Instead of asking for configuration files, ask for **Python scripts that define configurations**.

**Advanced Pattern** - Reflection Loop:
```python
from pydantic import BaseModel, ValidationError

class Contract(BaseModel):
    agent_name: str
    input_type: str
    output_type: str
    invariants: list[str]

def parse_with_reflection(llm_func: Callable, max_retries: int = 3) -> Contract:
    """Parse with automatic reflection on validation errors."""

    prompt = "Generate a Contract object for a sorting agent"

    for attempt in range(max_retries):
        code = llm_func(prompt)

        try:
            # Execute code (sandboxed)
            result = eval(code, {"Contract": Contract})
            return result
        except ValidationError as e:
            # Feed error back to LLM for targeted fix
            prompt = f"""
            Your previous code:
            {code}

            Caused validation error:
            {e}

            Fix the code to satisfy the Contract schema.
            """

    raise ValueError(f"Failed to generate valid Contract after {max_retries} attempts")
```

**Why Reflection Works**:
- Validation errors are **precise** ("field 'confidence' must be ≤ 1.0")
- LLMs can **fix specific issues** without regenerating everything
- Cheaper than full retry (only re-generate failing fields)

**kgents Use Cases**:
- **F-gent contract synthesis**: Reflection to fix type mismatches
- **B-gent hypothesis validation**: Reflection to add missing falsifiability criteria
- **E-gent code generation**: Reflection to fix import errors

---

### Strategy 3.2: Graduated Prompting (Start Strict, Relax on Failure)

**The Principle**: Try constrained generation first, relax constraints on failure.

**Implementation**:
```python
class GraduatedPromptParser:
    """Try strict format, fall back to loose format."""

    def parse(self, llm_func: Callable, data: str) -> ParseResult:
        # Attempt 1: Strict JSON schema
        try:
            result = self._parse_with_schema(llm_func, strict=True)
            return ParseResult(success=True, value=result, confidence=1.0)
        except ValidationError:
            pass

        # Attempt 2: Loose JSON schema (optional fields)
        try:
            result = self._parse_with_schema(llm_func, strict=False)
            return ParseResult(success=True, value=result, confidence=0.8)
        except ValidationError:
            pass

        # Attempt 3: Free-form text extraction
        result = self._extract_with_regex(llm_func)
        return ParseResult(success=True, value=result, confidence=0.5)
```

**Benefits**:
- **Optimizes for best case**: Tries for perfect output first
- **Degrades gracefully**: Falls back to looser formats
- **Confidence-scored**: User knows which strategy succeeded

---

## Phase 4: Novel / First-Principles Techniques

> **Reframe the problem entirely**

### Strategy 4.1: Differential Diffing (The Patch Strategy)

**The Principle**: Instead of generating full files, generate **patches** (diffs, sed commands).

**Scenario**: W-gent HTML generation

**Implementation**:
```python
import difflib

class DiffBasedParser:
    """Parse diffs instead of full outputs."""

    def __init__(self, base_template: str):
        self.base = base_template

    def parse_diff(self, diff_text: str) -> ParseResult[str]:
        """Apply LLM-generated diff to base template."""

        try:
            # Parse unified diff
            base_lines = self.base.splitlines(keepends=True)
            patch_lines = diff_text.splitlines(keepends=True)

            # Apply patch
            patched = difflib._mdiff(base_lines, patch_lines)
            result = ''.join(line for line, _, _ in patched)

            return ParseResult(
                success=True,
                value=result,
                confidence=0.9,
                repairs=["Applied unified diff patch"]
            )
        except Exception as e:
            return ParseResult(success=False, error=str(e))

# Usage
parser = DiffBasedParser(base_template='''
<html>
<body>
  <div id="main"></div>
</body>
</html>
''')

# LLM generates: "Replace line 3 with: <div id='main'>Hello World</div>"
# Or: Unified diff format
diff = '''
--- template.html
+++ modified.html
@@ -2,1 +2,1 @@
-  <div id="main"></div>
+  <div id="main">Hello World</div>
'''

result = parser.parse_diff(diff)
```

**Why It's Better**:
- **Applying patches is deterministic** (robust tools like `patch`, `diff3`)
- **Fuzz factors** handle near-misses gracefully
- **Smaller LLM outputs** (just the delta, not full file)
- **Version control friendly** (diffs are standard format)

**kgents Use Cases**:
- **W-gent incremental updates**: Patch base HTML template
- **E-gent code evolution**: Generate diffs instead of full modules
- **F-gent artifact updates**: Patch .alo.md files for version bumps

---

### Strategy 4.2: Anchor-Based Reconstruction (Islands of Stability)

**The Principle**: Don't parse the whole structure. Find **anchors** (known markers) and extract content between them.

**Implementation**:
```python
import re

class AnchorBasedParser:
    """Extract content using anchor markers, ignore structure."""

    def parse(self, text: str, anchor: str = "###ITEM:") -> ParseResult[list[str]]:
        """
        Extract items prefixed with anchor, discard everything else.

        Immune to:
        - Conversational filler ("Sure, here are the items:")
        - Malformed JSON structure
        - Extra markdown/formatting
        """

        # Find all anchor markers
        items = text.split(anchor)[1:]  # Skip text before first anchor
        items = [item.split("\n")[0].strip() for item in items]  # Take first line after anchor

        if not items:
            return ParseResult(success=False, error=f"No anchors '{anchor}' found")

        return ParseResult(
            success=True,
            value=items,
            confidence=0.9,  # High confidence (structure-independent)
            strategy="anchor-based"
        )

# Usage
response = '''
Sure, here's your list! Let me format it nicely:

{
  "items": [  // Malformed JSON starts here
###ITEM: First hypothesis
###ITEM: Second hypothesis
###ITEM: Third hypothesis
  ]  // Missing closing brace

Hope this helps!
'''

parser = AnchorBasedParser()
result = parser.parse(response)
# result.value = ["First hypothesis", "Second hypothesis", "Third hypothesis"]
# Ignored all the malformed JSON and conversational text
```

**Prompt Engineering**:
```
Generate 3 hypotheses. Prefix each with "###ITEM:" on its own line.
```

**Benefits**:
- **Structure-independent**: Doesn't care about JSON/XML validity
- **Ignores filler text**: Skips "Sure, here you go" preambles
- **Simple implementation**: Just string splitting
- **High confidence**: Anchors are unambiguous markers

**kgents Use Cases**:
- **B-gent hypothesis extraction**: Use `###HYPOTHESIS:` anchor
- **F-gent intent parsing**: Use `###BEHAVIOR:`, `###CONSTRAINT:` anchors
- **L-gent catalog search**: Use `###ARTIFACT:` anchor for results

---

### Strategy 4.3: Visual Feedback Loop (Multimodal Validation)

**The Principle**: For visual outputs (HTML, diagrams), validate using **vision** not **syntax**.

**Specific to W-gent**:

**Implementation**:
```python
from playwright.sync_api import sync_playwright
from anthropic import Anthropic

class VisualValidationParser:
    """Validate HTML by rendering and checking visual correctness."""

    def __init__(self, vlm_client):
        self.vlm = vlm_client  # Vision-Language Model (Claude 3.5 Sonnet, GPT-4V)

    def parse_with_visual_validation(self, html: str) -> ParseResult[str]:
        """Parse HTML and validate visually."""

        # Step 1: Render HTML to screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html)
            screenshot = page.screenshot()
            browser.close()

        # Step 2: VLM validates visual correctness
        response = self.vlm.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "data": screenshot}},
                    {"type": "text", "text": "Does this page look broken? Check for: (1) collapsed divs (height=0), (2) overlapping text, (3) missing content. Respond with JSON: {\"is_broken\": bool, \"issues\": [str]}"}
                ]
            }]
        )

        validation = json.loads(response.content[0].text)

        if validation["is_broken"]:
            # Step 3: If broken, ask VLM to fix the HTML
            fix_response = self.vlm.messages.create(
                model="claude-3-5-sonnet-20241022",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "data": screenshot}},
                        {"type": "text", "text": f"This page has issues: {validation['issues']}. Here's the HTML:\n\n{html}\n\nFix the HTML to resolve these visual issues."}
                    ]
                }]
            )

            fixed_html = extract_code_block(fix_response.content[0].text)

            return ParseResult(
                success=True,
                value=fixed_html,
                confidence=0.7,
                repairs=[f"Visual validation found issues: {validation['issues']}"],
                strategy="visual-feedback-loop"
            )

        return ParseResult(success=True, value=html, confidence=1.0)
```

**Innovation**: This moves validation from **syntax** ("does it parse?") to **semantics** ("does it look right?").

**kgents Use Cases**:
- **W-gent real-time dashboards**: Validate rendered dashboard looks correct
- **F-gent artifact visualization**: Ensure .alo.md renders correctly in markdown viewers
- **Documentation generation**: Validate generated docs are readable

---

### Strategy 4.4: Probabilistic AST (Confidence-Scored Tree Nodes)

**The Principle**: Instead of binary AST (valid/invalid), build an AST where **every node has a confidence score**.

**Implementation**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProbabilisticASTNode:
    """AST node with confidence score."""
    type: str
    value: Any
    confidence: float  # 0.0-1.0
    children: list["ProbabilisticASTNode"]
    repair_applied: Optional[str] = None

class ProbabilisticParser:
    """Build AST with per-node confidence scores."""

    def parse(self, text: str) -> ProbabilisticASTNode:
        """Parse text into probabilistic AST."""

        # Try to parse as JSON
        try:
            data = json.loads(text)
            return self._build_confident_ast(data, confidence=1.0)
        except json.JSONDecodeError:
            # Repair and build low-confidence AST
            repaired, repairs = self._repair_json(text)
            data = json.loads(repaired)
            return self._build_repaired_ast(data, confidence=0.6, repairs=repairs)

    def _build_confident_ast(self, data, confidence) -> ProbabilisticASTNode:
        """Build AST from successfully parsed data."""
        if isinstance(data, dict):
            children = [
                self._build_confident_ast(v, confidence)
                for k, v in data.items()
            ]
            return ProbabilisticASTNode(
                type="object",
                value=data,
                confidence=confidence,
                children=children
            )
        # Handle other types...

    def query_confident_fields(self, root: ProbabilisticASTNode, min_confidence: float = 0.8) -> dict:
        """Extract only high-confidence fields from probabilistic AST."""
        if root.confidence < min_confidence:
            return {}

        result = {}
        for child in root.children:
            if child.confidence >= min_confidence:
                result.update(self.query_confident_fields(child, min_confidence))

        return result
```

**Benefits**:
- **Partial trust**: Use high-confidence fields, ignore low-confidence ones
- **Explainable**: Know which parts of the parse are uncertain
- **Adaptive**: Adjust `min_confidence` threshold based on use case

**kgents Use Cases**:
- **E-gent code validation**: Mark repaired imports as low-confidence
- **B-gent hypothesis parsing**: Track confidence of inferred fields
- **L-gent catalog metadata**: Mark auto-inferred tags as low-confidence

---

### Strategy 4.5: Schema Evolution (Parsers That Adapt)

**The Principle**: LLM output formats **drift over time**. Parsers should track format changes and adapt.

**Implementation**:
```python
from collections import Counter

class EvolvingParser:
    """Parser that learns from observed formats over time."""

    def __init__(self):
        self.observed_formats = Counter()
        self.strategies = {
            "format_a": StrategyA(),
            "format_b": StrategyB(),
            "format_c": StrategyC()
        }

    def parse_with_evolution(self, text: str) -> ParseResult:
        """Parse and track which format succeeded."""

        # Try strategies in order of historical success
        ranked_strategies = [
            (name, strategy)
            for name, strategy in sorted(
                self.strategies.items(),
                key=lambda x: self.observed_formats[x[0]],
                reverse=True
            )
        ]

        for name, strategy in ranked_strategies:
            result = strategy.parse(text)
            if result.success:
                # Track successful format
                self.observed_formats[name] += 1
                result.metadata["format"] = name
                return result

        return ParseResult(success=False, error="All formats failed")

    def report_drift(self) -> dict:
        """Report which formats are becoming more/less common."""
        total = sum(self.observed_formats.values())
        return {
            name: count / total
            for name, count in self.observed_formats.items()
        }

# Usage over time
parser = EvolvingParser()

# Week 1: Format A dominates
for _ in range(100):
    parser.parse_with_evolution(llm_output_format_a)

# Week 2: Format B starts appearing
for _ in range(50):
    parser.parse_with_evolution(llm_output_format_b)

# Check drift
print(parser.report_drift())
# {"format_a": 0.67, "format_b": 0.33}
# Parser automatically prioritizes format_a (faster on average)
```

**Benefits**:
- **Self-optimizing**: Faster over time as it learns common formats
- **Drift detection**: Know when LLM behavior changes
- **Data-driven**: No manual reordering of fallback chains

**kgents Use Cases**:
- **Long-running E-gent evolution**: Track code generation format drift
- **B-gent hypothesis format**: Detect when LLM starts using new section headers
- **Cross-LLM compatibility**: Different LLMs prefer different formats

---

### Strategy 4.6: Multi-Model Ensembles (Structure + Content Specialists)

**The Principle**: Use **small fast models** for structure, **large capable models** for content.

**Implementation**:
```python
class EnsembleParser:
    """Use different models for structure vs content."""

    def __init__(self, structure_model, content_model):
        self.structure_model = structure_model  # Fast, cheap (GPT-3.5, Llama-3-8B)
        self.content_model = content_model      # Capable, expensive (GPT-4, Claude Opus)

    def parse_with_ensemble(self, user_input: str) -> ParseResult:
        """Structure from fast model, content from capable model."""

        # Step 1: Fast model generates structure
        structure_prompt = f"""
        Generate a JSON structure (keys only, empty values) for this request:
        {user_input}

        Output ONLY the JSON structure, no explanations.
        """

        structure = self.structure_model.generate(structure_prompt)
        parsed_structure = json.loads(structure)

        # Step 2: Capable model fills content
        result = {}
        for key, _ in parsed_structure.items():
            content_prompt = f"""
            For the field '{key}' in response to:
            {user_input}

            Generate the content (just the value, no JSON formatting).
            """

            result[key] = self.content_model.generate(content_prompt)

        return ParseResult(
            success=True,
            value=result,
            confidence=0.9,
            strategy="ensemble",
            metadata={
                "structure_model": "gpt-3.5-turbo",
                "content_model": "gpt-4"
            }
        )
```

**Benefits**:
- **Cost optimization**: Expensive model only generates content, not structure
- **Speed**: Fast model returns structure quickly (progressive rendering)
- **Quality**: Capable model ensures high-quality content

**kgents Use Cases**:
- **F-gent artifact generation**: Fast model for contract structure, capable model for invariants
- **B-gent hypothesis generation**: Fast model for format, capable model for reasoning
- **Cost-conscious pipelines**: Optimize LLM costs across the system

---

## Composition Patterns (Enhanced for Streaming)

### Sequential Fallback (Chain of Responsibility)
```python
class FallbackParser[A](Parser[A]):
    """Try strategies in order until one succeeds."""

    def __init__(self, *strategies: Parser[A]):
        self.strategies = strategies

    def parse(self, text: str) -> ParseResult[A]:
        for i, strategy in enumerate(self.strategies):
            result = strategy.parse(text)
            if result.success:
                # Penalize for fallback depth
                result.confidence *= max(0.5, 1.0 - 0.1 * i)
                result.metadata["fallback_depth"] = i
                return result

        return ParseResult(
            success=False,
            error=f"All {len(self.strategies)} strategies failed"
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[A]]:
        """Stream parsing with fallback."""
        # Try first strategy that supports streaming
        for strategy in self.strategies:
            if hasattr(strategy, "parse_stream"):
                yield from strategy.parse_stream(tokens)
                return

        # Fallback: Buffer and parse complete
        text = "".join(tokens)
        yield self.parse(text)
```

### Parallel Fusion (Merge Multiple Parsers)
```python
class FusionParser[A](Parser[A]):
    """Run multiple parsers and merge results."""

    def __init__(self, *parsers: Parser[A], merge_fn: Callable):
        self.parsers = parsers
        self.merge_fn = merge_fn

    def parse(self, text: str) -> ParseResult[A]:
        results = [p.parse(text) for p in self.parsers]
        successful = [r for r in results if r.success]

        if not successful:
            return ParseResult(success=False, error="All parsers failed")

        # Merge successful results
        merged_value = self.merge_fn([r.value for r in successful])
        avg_confidence = sum(r.confidence for r in successful) / len(successful)

        all_repairs = []
        for r in successful:
            all_repairs.extend(r.repairs)

        return ParseResult(
            success=True,
            value=merged_value,
            confidence=avg_confidence,
            repairs=all_repairs,
            strategy="fusion",
            metadata={
                "parsers_succeeded": len(successful),
                "parsers_total": len(self.parsers)
            }
        )
```

### Conditional Switch (Route by Input)
```python
class SwitchParser[A](Parser[A]):
    """Choose parser based on input characteristics."""

    def __init__(self, routes: dict[Callable[[str], bool], Parser[A]]):
        self.routes = routes

    def parse(self, text: str) -> ParseResult[A]:
        for condition, parser in self.routes.items():
            if condition(text):
                result = parser.parse(text)
                result.metadata["switch_condition"] = condition.__name__
                return result

        return ParseResult(
            success=False,
            error="No matching parser for input"
        )
```

---

## Recommended Strategy Combinations

### For W-gent (Wire Observation - HTML Dashboards)

**Challenge**: Stream HTML from LLM, render live without breaking.

**Recommended Stack**:
1. **Prevention**: FIM Sandwich (hardcode `<html><body>...</body></html>`)
2. **Correction**: Stack-Balancing Stream Parser (auto-close tags while streaming)
3. **Novel**: Anchor-Based Reconstruction (LLM emits `<|UPDATE|>` markers, W-gent controls structure)

**Implementation**:
```python
class WgentFuzzyHtmlParser:
    """W-gent specialized parser for streaming HTML."""

    def __init__(self, base_template: str):
        self.base_template = base_template
        self.stack_parser = StackBalancingParser(opener="<", closer=">")
        self.anchor = "<|UPDATE|>"

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[str]:
        """
        Stream HTML updates with automatic healing.

        Protocol:
        1. LLM emits: <|UPDATE|><div class="card">content</div>
        2. W-gent extracts content between anchors
        3. W-gent injects into base_template
        4. Stack-balancing auto-closes unclosed tags
        """

        buffer = ""
        for token in tokens:
            buffer += token

            # Look for update anchors
            if self.anchor in buffer:
                updates = buffer.split(self.anchor)[1:]

                for update in updates:
                    # Stack-balance the update
                    balanced = self.stack_parser.balance_tags(update)

                    # Inject into base template
                    rendered = self.base_template.replace(
                        '<div id="main"></div>',
                        f'<div id="main">{balanced}</div>'
                    )

                    yield rendered

                buffer = ""  # Clear buffer after processing updates
```

**User Experience**:
- User watches **raw stream** (txt) and **rendered server** (HTML) simultaneously
- HTML heals automatically via stack-balancing
- Anchors prevent structural hallucination

---

### For F-gent (Forge - Code Generation)

**Challenge**: Generate Python code with high confidence, validate before execution.

**Recommended Stack**:
1. **Prevention**: Type-Guided Generation (Pydantic models)
2. **Correction**: Reflection Loop (validate → fix errors → retry)
3. **Novel**: Probabilistic AST (confidence-scored imports/functions)

**Implementation**:
```python
from pydantic import BaseModel

class CodeArtifact(BaseModel):
    module_name: str
    imports: list[str]
    functions: list[str]

class FgentCodeParser:
    """F-gent parser with reflection and probabilistic AST."""

    def parse_with_reflection(self, llm_func, intent: str) -> ParseResult[str]:
        prompt = f"Write a CodeArtifact for: {intent}"

        for attempt in range(3):
            code = llm_func(prompt)

            try:
                # Validate via Pydantic
                artifact = eval(code, {"CodeArtifact": CodeArtifact})

                # Build probabilistic AST
                prob_ast = self._analyze_code(artifact)

                # Check confidence
                avg_confidence = self._avg_node_confidence(prob_ast)

                return ParseResult(
                    success=True,
                    value=str(artifact),
                    confidence=avg_confidence,
                    strategy="pydantic-reflection"
                )
            except ValidationError as e:
                prompt = f"Fix this error: {e}\n\nPrevious code:\n{code}"

        return ParseResult(success=False, error="Reflection failed")
```

---

### For B-gent (Bio/Scientific - Hypothesis Generation)

**Challenge**: Parse structured scientific hypotheses with epistemic requirements.

**Recommended Stack**:
1. **Prevention**: CFG Masking (enforce HYPOTHESES / REASONING / TESTS sections)
2. **Correction**: Heuristic Section Parsing (flexible item extraction)
3. **Novel**: Anchor-Based + Lazy Validation (defer falsifiability check until needed)

**Implementation**:
```python
class BgentHypothesisParser:
    """B-gent parser with CFG constraint and lazy validation."""

    def parse(self, text: str) -> ParseResult[list[Hypothesis]]:
        # Use anchor-based extraction for robustness
        anchor_parser = AnchorBasedParser(anchor="###HYPOTHESIS:")
        result = anchor_parser.parse(text)

        if not result.success:
            return result

        # Build lazy-validated hypotheses
        hypotheses = []
        for hypothesis_text in result.value:
            # Parse fields with defaults
            h = self._parse_hypothesis_fields(hypothesis_text)

            # Lazy validation: Don't check falsifiability until accessed
            lazy_h = LazyValidatedHypothesis(h)
            hypotheses.append(lazy_h)

        return ParseResult(
            success=True,
            value=hypotheses,
            confidence=result.confidence,
            strategy="anchor-based-lazy"
        )
```

---

## Configuration Philosophy

**Guideline**: Configuration should **tune behavior**, not replace design.

### Good Configuration (Behavioral Tuning)
```python
@dataclass
class ParserConfig:
    """Configuration for parser behavior."""
    min_confidence: float = 0.5        # Reject low-confidence parses
    allow_partial: bool = True         # Accept partial parses
    max_attempts: int = 1000           # Limit search iterations
    enable_repair: bool = True         # Try repair strategies
    timeout_ms: int = 5000             # Parsing timeout
    stream_chunk_size: int = 128       # Tokens per stream chunk
    enable_reflection: bool = True     # Use LLM-based error correction
    max_reflection_retries: int = 3    # Reflection loop limit
```

### Bad Configuration (Structural)
```python
@dataclass
class BadConfig:
    """Anti-pattern: Configuration replaces design."""
    strategies: list[str]              # ❌ Strategies should be composed
    custom_regex: str                  # ❌ Regex should be in strategy
    output_format: str                 # ❌ Output type should be in Parser[A]
```

---

## Confidence Scoring (Enhanced)

### Confidence Heuristics

**Base Confidence by Strategy**:
- CFG-constrained generation: 1.0 (mathematically guaranteed)
- FIM sandwich: 0.95 (root structure guaranteed)
- Type-guided (Pydantic): 0.9 (validated at runtime)
- Direct parse (no repairs): 0.85
- Stack-balancing stream: 0.75 (partial/incomplete)
- Single repair applied: 0.6
- Multiple repairs: 0.4
- Anchor-based extraction: 0.7 (structure-independent)
- Visual validation (VLM): 0.8 (semantic validation)
- Reflection loop (1 retry): 0.7
- Reflection loop (2+ retries): 0.5
- Field extraction fallback: 0.3

### Confidence Combination Rules

**Sequential operations** (multiply):
```python
# Parse → Repair → Validate
confidence = 0.8 * 0.6 * 0.9 = 0.432
```

**Parallel operations** (average):
```python
# Fusion of 3 parsers
confidence = (0.7 + 0.8 + 0.6) / 3 = 0.7
```

**Probabilistic AST** (min of node confidences):
```python
# Confidence = lowest confidence node in critical path
confidence = min(node.confidence for node in critical_path)
```

---

## Error Handling Philosophy

### Principle: **Degrade Gracefully**

P-gents NEVER throw exceptions on malformed input. Instead:

1. **Try all strategies** (fallback chain)
2. **Return ParseResult with success=False** (not exception)
3. **Include helpful error message** (what was expected vs found)
4. **Optionally return partial parse** with low confidence
5. **Track repairs applied** (ethical transparency)
6. **Support reflection loops** (LLM fixes its own errors)

---

## Integration with Other Genuses (Updated)

### E-gent (Evolution) - Parse evolved code with reflection
```python
evolution_result = evolve_agent.invoke(target_agent)
parsed = code_parser.parse_with_reflection(
    llm_func=evolution_result.llm,
    intent=evolution_result.intent
)

if parsed.confidence < 0.7:
    # Reflection: LLM fixes its own errors
    fixed = parsed.metadata["reflection_result"]
```

### W-gent (Wire) - Stream HTML with stack-balancing
```python
html_stream = wgent_parser.parse_stream(llm_token_stream)

for snapshot in html_stream:
    render_to_browser(snapshot.value)  # Live updates
    if snapshot.partial:
        show_indicator("Streaming...")  # User knows it's incomplete
```

### F-gent (Forge) - CFG-constrained contract generation
```python
contract_parser = CFGConstrainedParser(schema=contract_schema)
contract = contract_parser.parse_with_constraint(llm, intent)
# Guaranteed valid contract structure
```

### B-gent (Bio) - Anchor-based hypothesis extraction
```python
hypothesis_parser = AnchorBasedParser(anchor="###HYPOTHESIS:")
hypotheses = hypothesis_parser.parse(llm_response)
# Immune to conversational filler and malformed structure
```

---

## Anti-Patterns (Updated)

### ❌ Retry Without Reflection
**Problem**: Expensive, no learning

**Bad**:
```python
for _ in range(5):
    try:
        return json.loads(llm.generate(prompt))
    except:
        continue  # Just retry with same prompt
```

**Good**:
```python
for attempt in range(3):
    try:
        return json.loads(llm.generate(prompt))
    except JSONDecodeError as e:
        # Reflection: feed error back to LLM
        prompt = f"Fix this JSON error: {e}\n\n{llm.last_response}"
```

### ❌ Ignoring Streaming
**Problem**: Violates Heterarchical principle, poor UX

**Bad**:
```python
text = "".join(llm_stream)  # Buffer entire stream
return parse(text)           # Parse at end
```

**Good**:
```python
for chunk in llm_stream:
    partial_result = parser.parse_stream([chunk])
    yield partial_result  # Progressive rendering
```

### ❌ Binary Confidence
**Problem**: Loses information about parse quality

**Bad**:
```python
return {"success": True, "value": data}  # No confidence score
```

**Good**:
```python
return ParseResult(
    success=True,
    value=data,
    confidence=0.75,  # Quantified uncertainty
    repairs=["Balanced brackets", "Removed trailing comma"]
)
```

---

## Success Criteria (Updated)

A P-gent implementation is successful if:

1. **Compression achieved**: ~2,400 lines of parsing code → ~800 lines (67% reduction)
2. **Zero regressions**: All existing tests pass
3. **Confidence scoring**: All parsers return meaningful confidence ∈ [0.0, 1.0]
4. **Composition works**: Fallback/Fusion/Switch demonstrated
5. **Streaming support**: At least one parser supports `parse_stream()`
6. **Graceful degradation**: No exceptions on malformed input
7. **Frontier techniques**: At least 3 Phase 1-4 strategies implemented
8. **Reflection capability**: Parser can invoke LLM to fix its own errors
9. **Transparency**: All repairs tracked in `ParseResult.repairs`
10. **Bootstrappable**: Can regenerate from spec + examples

---

## Implementation Roadmap (Updated)

### Phase 1: Core Types + Prevention
- [ ] Define `ParseResult[A]` with stream_position, metadata
- [ ] Define `Parser[A]` protocol with `parse_stream()`
- [ ] Define `ParserConfig` with reflection settings
- [ ] Implement CFG-constrained parser (Outlines integration)
- [ ] Implement FIM sandwich parser
- [ ] Implement Type-Guided parser (Pydantic)

### Phase 2: Correction + Streaming
- [ ] `StackBalancingParser` (stream HTML/JSON)
- [ ] `StructuralDecouplingParser` (Jsonformer approach)
- [ ] `IncrementalParser` (build AST incrementally)
- [ ] `LazyValidationParser` (defer validation)
- [ ] `ReflectionParser` (LLM fixes errors)

### Phase 3: Novel Techniques
- [ ] `DiffBasedParser` (patch strategy)
- [ ] `AnchorBasedParser` (islands of stability)
- [ ] `VisualValidationParser` (VLM validation for W-gent)
- [ ] `ProbabilisticASTParser` (confidence-scored nodes)
- [ ] `EvolvingParser` (schema drift tracking)
- [ ] `EnsembleParser` (multi-model structure+content)

### Phase 4: Composition + Integration
- [ ] `FallbackParser` with streaming support
- [ ] `FusionParser` with confidence merging
- [ ] `SwitchParser` with format detection
- [ ] `GraduatedPromptParser` (strict → loose fallback)

### Phase 5: Migration + Testing
- [ ] Migrate E-gent parser → CFG + Reflection
- [ ] Migrate B-gent parser → Anchor-based + Lazy
- [ ] Migrate Runtime JSON → Stack-balancing stream
- [ ] Migrate F-gent parsers → Type-guided
- [ ] Create W-gent fuzzy-HTML parser (FIM + Stack + Anchor)
- [ ] Verify output equivalence
- [ ] Benchmark performance
- [ ] Document migration guide

---

## Open Questions (Updated)

1. **CFG vs Reflection trade-off?**
   - CFG prevents errors (fast, guaranteed)
   - Reflection fixes errors (flexible, learns)
   - **Recommendation**: Use CFG when format is known, Reflection when exploratory

2. **Stream chunk size optimization?**
   - Smaller chunks: More responsive, more parser invocations
   - Larger chunks: Less overhead, delayed rendering
   - **Recommendation**: Adaptive chunk size based on parse latency

3. **Confidence calibration?**
   - Current: Hand-tuned heuristics
   - Future: Learn from labeled data?
   - **Recommendation**: A/B test confidence thresholds in production

4. **Visual validation cost?**
   - VLM calls are expensive (screenshot + vision model)
   - Only for critical visual correctness (W-gent dashboards)
   - **Recommendation**: Cache screenshots, batch validations

5. **Multi-model ensemble cost optimization?**
   - When is structure+content split worth it?
   - **Recommendation**: Benchmark on real workloads, optimize for cost/quality Pareto frontier

6. **Schema evolution trigger?**
   - When to retrain/reorder strategies?
   - **Recommendation**: Trigger on >10% drift in format distribution

---

## References

### Empirical Sources (kgents codebase)
- `impl/claude/agents/e/parser/` - Multi-strategy code parser
- `impl/claude/agents/b/hypothesis_parser.py` - Scientific hypothesis parser
- `impl/claude/runtime/json_utils.py` - Robust JSON parsing
- `impl/claude/agents/f/` - Intent, version, code generation parsers
- `impl/claude/agents/shared/ast_utils.py` - AST extraction utilities

### Theoretical Foundations
- **Stochastic-Structural Gap**: LLM probability distributions vs deterministic parsers
- **Prevention → Correction → Novel spectrum**: Architectural organization
- **Probabilistic parsing**: Treat LLM output as distribution, not program
- **Graceful degradation**: Partial correctness with confidence scoring
- **Composition over configuration**: Build complex parsers from simple ones

### Frontier Research (2024-2025)
- **CFG Logit Masking**: [Outlines](https://github.com/outlines-dev/outlines), [Guidance](https://github.com/guidance-ai/guidance)
- **Fill-in-the-Middle**: [CodeLlama](https://arxiv.org/abs/2308.12950), [StarCoder](https://arxiv.org/abs/2305.06161)
- **Jsonformer**: [Structured Generation](https://github.com/1rgs/jsonformer)
- **Visual Validation**: Multimodal LLMs (Claude 3.5 Sonnet, GPT-4V)
- **Reflection Loops**: [Self-Refine](https://arxiv.org/abs/2303.17651), [ReAct](https://arxiv.org/abs/2210.03629)

### Design Principles (kgents)
- `spec/principles.md` - Seven core principles
- **Minimal Output Principle**: Single outputs, composed at pipeline level
- **Heterarchical**: Dual autonomous/functional modes (streaming support)
- **Generative**: Spec compresses implementation
- **Ethical**: Transparency about repairs and confidence

---

## W-gent Specific Guidance: The "Fuzzy-HTML" Parser

**Challenge**: W-gent needs to stream HTML visualizations from LLM outputs without breaking the page.

**Recommended Architecture**:

```python
class WgentFuzzyHtmlParser:
    """
    The optimal W-gent parser combines:
    1. FIM Sandwich (prevention)
    2. Stack-Balancing Stream (correction)
    3. Anchor-Based Reconstruction (novel)
    """

    def __init__(self):
        self.base_template = '''
        <html>
        <head><style>/* W-gent styles */</style></head>
        <body>
          <div id="main"></div>
        </body>
        </html>
        '''
        self.stack_balancer = StackBalancingParser(opener="<", closer=">")
        self.anchor = "<|UPDATE|>"

    async def parse_llm_stream(
        self,
        llm_stream: AsyncIterator[str]
    ) -> AsyncIterator[tuple[str, str]]:
        """
        Parse LLM stream into (raw, healed) HTML pairs.

        Returns:
            (raw_html, healed_html) - User sees both simultaneously
        """
        buffer = ""

        async for token in llm_stream:
            buffer += token

            # Look for update anchors
            if self.anchor in buffer:
                updates = buffer.split(self.anchor)[1:]

                for update_fragment in updates:
                    # Raw: Show what LLM actually generated
                    raw = update_fragment

                    # Healed: Stack-balance for safe rendering
                    healed = self.stack_balancer.balance_tags(update_fragment)

                    # Inject into base template
                    full_html = self.base_template.replace(
                        '<div id="main"></div>',
                        f'<div id="main">{healed}</div>'
                    )

                    yield (raw, full_html)

                buffer = ""  # Clear after processing

# Usage
parser = WgentFuzzyHtmlParser()

async for raw, healed in parser.parse_llm_stream(llm_stream):
    # User sees TWO views:
    # 1. "txt" view: raw (exactly what LLM generated)
    # 2. "server" view: healed (safe to render)

    display_raw_panel(raw)
    render_browser_panel(healed)
```

**Protocol**:
1. **LLM emits**: `<|UPDATE|><div class="card">Agent is running...</div>`
2. **W-gent extracts**: Content between `<|UPDATE|>` anchors
3. **W-gent heals**: Stack-balances unclosed tags
4. **W-gent injects**: Into base HTML template
5. **User sees**: Raw stream + Healed projection simultaneously

**Benefits**:
- **Live updates**: Streaming experience
- **Never breaks**: Stack-balancing auto-closes tags
- **Transparent**: User sees raw LLM output
- **Educational**: User learns how healing works

---

**End of P-gents Specification v2.0**

*The most future-proof, elegant, and scientifically sound parser architecture for bridging the Stochastic-Structural Gap.*
