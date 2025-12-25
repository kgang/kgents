# CodeService Usage Examples

Real-world examples of using CodeService for explicit code sync flows.

## Example 1: Upload Single File

```python
from services.code import CodeService

# Initialize service
service = CodeService()

# Upload a file
result = await service.upload_file(
    file_path="src/calculator.py",
    create_kblock=True,
)

print(f"File: {result.file_path}")
print(f"Functions: {result.functions_created}")
print(f"Ghosts: {result.ghosts_created}")
print(f"K-Block: {result.kblock_id}")
```

**Output:**
```
File: src/calculator.py
Functions: ['fn_add_a3f2', 'fn_multiply_b7e1', 'fn_divide_c9d4']
Ghosts: ['validate_input', 'log_operation']
K-Block: kb_f4a8d3e1b2c7
```

## Example 2: Sync Directory with Incremental Mode

```python
# First sync - creates all functions
result = await service.sync_directory(
    directory="src/",
    pattern="**/*.py",
    incremental=True,
)

print(f"Files: {result.files_processed}")
print(f"Created: {result.functions_created}")
print(f"Updated: {result.functions_updated}")

# Second sync - only processes changed files
result = await service.sync_directory(
    directory="src/",
    incremental=True,
)

print(f"Unchanged: {result.functions_unchanged}")
```

**Output (first run):**
```
Files: 12
Created: 45
Updated: 0
```

**Output (second run, no changes):**
```
Files: 12
Created: 0
Updated: 0
Unchanged: 45
```

## Example 3: Bootstrap Spec+Impl for QA

Kent's workflow - bootstrap trivial toy specs and implementations:

```python
# Trivial spec
spec = """
# String Utils

## reverse
Reverses a string.

## capitalize_words
Capitalizes each word.
"""

# Trivial impl
impl = """
def reverse(s: str) -> str:
    \"\"\"Reverse a string.\"\"\"
    return s[::-1]

def capitalize_words(s: str) -> str:
    \"\"\"Capitalize each word.\"\"\"
    return s.title()
"""

# Bootstrap the pair
result = await service.bootstrap_spec_impl_pair(
    spec_content=spec,
    impl_content=impl,
    name="string_utils",
)

print(f"Spec: {result.spec_id}")
print(f"Functions: {result.impl_functions}")
print(f"Edges: {result.derivation_edges}")
```

**Output:**
```
Spec: spec_string_utils
Functions: ['fn_reverse_a1b2', 'fn_capitalize_words_c3d4']
Edges: ['edge_spec_string_utils_fn_reverse_a1b2',
        'edge_spec_string_utils_fn_capitalize_words_c3d4']
```

## Example 4: Ghost Detection

```python
# File with undefined calls
code = """
def process_data(data):
    validated = validate(data)  # Ghost!
    cleaned = clean(validated)  # Ghost!
    return transform(cleaned)   # Ghost!

def save_data(data):
    return persist(data)  # Ghost!
"""

# Write to temp file and upload
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(code)
    temp_path = f.name

result = await service.upload_file(temp_path)

print(f"Functions: {len(result.functions_created)}")
print(f"Ghosts detected: {result.ghosts_created}")
```

**Output:**
```
Functions: 2
Ghosts detected: ['validate', 'clean', 'transform', 'persist']
```

## Example 5: Sync with Error Handling

```python
result = await service.sync_directory("src/")

if result.errors:
    print("Errors encountered:")
    for error in result.errors:
        print(f"  - {error}")
else:
    print("Sync completed successfully!")
    print(f"  Files: {result.files_processed}")
    print(f"  Functions: {result.functions_created}")
    print(f"  K-Blocks: {result.kblocks_created}")
```

**Output (with errors):**
```
Errors encountered:
  - No functions found in src/empty.py
  - Error processing src/broken.py: invalid syntax
```

## Example 6: Link to Spec

```python
# Upload impl and link to existing spec
result = await service.upload_file(
    file_path="impl/auth.py",
    spec_id="spec_auth_protocol",  # Link to spec
)

print(f"Linked {len(result.functions_created)} functions to {spec_id}")
```

## Example 7: Disable Auto-Extract

```python
# Upload file but don't extract functions
result = await service.upload_file(
    file_path="config.py",
    auto_extract_functions=False,
)

print(f"Functions: {len(result.functions_created)}")  # → 0
```

## Example 8: Full QA Flow

```python
# 1. Upload spec
spec_result = await service.bootstrap_spec_impl_pair(
    spec_content=open("spec/calculator.md").read(),
    impl_content=open("impl/calculator.py").read(),
    name="calculator",
)

# 2. Verify derivation chain
print(f"Spec: {spec_result.spec_id}")
print(f"Functions: {len(spec_result.impl_functions)}")
print(f"Edges: {len(spec_result.derivation_edges)}")

# 3. Sync impl directory
sync_result = await service.sync_directory("impl/")

# 4. Check for ghosts
if sync_result.ghosts_created > 0:
    print(f"Warning: {sync_result.ghosts_created} undefined functions")

# 5. Verify K-blocks
print(f"K-Blocks created: {sync_result.kblocks_created}")
```

## Testing Examples

All examples are testable. Run:

```bash
uv run pytest services/code/_tests/test_service.py::test_upload_file_creates_functions -v
uv run pytest services/code/_tests/test_service.py::test_full_flow_bootstrap -v
```
