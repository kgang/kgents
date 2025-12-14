# Skill: Creating Anywidget Widgets for Marimo

> *"The widget is a 2-way binding between Python and browser—state made visible."*

## Overview

Marimo has standardized on [anywidget](https://anywidget.dev/) as their third-party plugin API. This skill covers the **correct** patterns for creating custom widgets that work in marimo notebooks.

## Root Cause of Common Errors

### "Module does not appear to be a valid anywidget" Error

**Cause**: JavaScript ESM uses wrong export pattern.

| ❌ WRONG | ✅ CORRECT |
|----------|-----------|
| `export function render(...)` | `export default { render }` |
| Named export | Default export with object |

The AFM (Anywidget Front-End Module) specification requires a **default export** that is an object (or function returning an object) with lifecycle methods.

## JavaScript ESM Requirements

### Minimal Valid Pattern

```javascript
// widget.js - CORRECT pattern
function render({ model, el }) {
  // Create DOM elements
  const div = document.createElement('div');
  div.textContent = model.get('value');
  el.appendChild(div);

  // Listen for changes
  model.on('change:value', () => {
    div.textContent = model.get('value');
  });

  // Optional: return cleanup function
  return () => {
    // cleanup logic
  };
}

// REQUIRED: default export with object
export default { render };
```

### With Initialize Hook

```javascript
export default {
  initialize({ model }) {
    // Called once per widget instance
    // Setup shared state
    console.log('Widget initialized');
  },

  render({ model, el }) {
    // Called once per view
    // Build DOM
  }
};
```

### Function Export (Advanced)

```javascript
// For widgets needing shared front-end state
export default async () => {
  const sharedState = {};

  return {
    initialize({ model }) {
      // Access sharedState here
    },
    render({ model, el }) {
      // Access sharedState here
    }
  };
};
```

## Python Widget Class

```python
from pathlib import Path
import anywidget
import traitlets

# Use pathlib.Path for external files (NOT string paths)
_JS_DIR = Path(__file__).parent / "js"

class MyWidget(anywidget.AnyWidget):
    # Point to external JS file
    _esm = _JS_DIR / "my_widget.js"

    # Optional CSS (can be string or Path)
    _css = """
    .my-widget {
        background: #1a1a2e;
        color: #e0e0e0;
    }
    """

    # Synced traits (bidirectional Python ↔ JS)
    value = traitlets.Unicode("").tag(sync=True)
    count = traitlets.Int(0).tag(sync=True)
```

### Inline ESM Alternative (for simple widgets)

```python
class SimpleWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
      el.textContent = model.get('value');
      model.on('change:value', () => {
        el.textContent = model.get('value');
      });
    }
    export default { render };
    """

    value = traitlets.Unicode("Hello").tag(sync=True)
```

## Marimo Integration

### REQUIRED: Wrap with mo.ui.anywidget()

```python
import marimo as mo
from mypackage.widgets import MyWidget

# Create raw widget
raw_widget = MyWidget(value="test")

# REQUIRED: Wrap for marimo reactivity
widget = mo.ui.anywidget(raw_widget)

# Display
widget
```

### Accessing Widget Value

```python
# In a dependent cell
widget.value  # Returns dict of synced traits

# For method calls, use raw widget
raw_widget.some_method()
```

## Model API (JavaScript Side)

| Method | Usage |
|--------|-------|
| `model.get('prop')` | Read Python-synced property |
| `model.set('prop', value)` | Set property (Python notified) |
| `model.save_changes()` | Batch commit changes to Python |
| `model.on('change:prop', fn)` | Listen to property changes |
| `model.off('change:prop', fn)` | Remove listener |

### Save Changes Pattern

```javascript
// For interactive updates (click handlers, etc.)
button.onclick = () => {
  model.set('clicked', true);
  model.set('count', model.get('count') + 1);
  model.save_changes();  // Commit both changes
};
```

## File Structure

```
mypackage/
├── __init__.py
├── widgets/
│   ├── __init__.py
│   ├── base.py           # Base widget class
│   ├── my_widget.py      # Widget Python code
│   └── js/
│       ├── my_widget.js  # Widget JavaScript
│       └── shared.js     # Shared utilities
```

## Common Pitfalls

### 1. Wrong Export Pattern (Most Common!)

```javascript
// ❌ WRONG - causes "not valid anywidget" error
export function render({ model, el }) { ... }

// ✅ CORRECT
function render({ model, el }) { ... }
export default { render };
```

### 2. String Path Instead of pathlib.Path

```python
# ❌ WRONG - may cause path resolution issues
_esm = "js/widget.js"

# ✅ CORRECT
_esm = Path(__file__).parent / "js" / "widget.js"
```

### 3. Missing mo.ui.anywidget() Wrapper

```python
# ❌ WRONG - won't be reactive in marimo
widget = MyWidget()
widget  # Direct display

# ✅ CORRECT
raw = MyWidget()
widget = mo.ui.anywidget(raw)
widget
```

### 4. Calling Methods on Wrapped Widget

```python
# ❌ WRONG - wrapper doesn't proxy methods
widget = mo.ui.anywidget(MyWidget())
widget.update_data(new_data)  # Error!

# ✅ CORRECT - keep reference to raw widget
raw = MyWidget()
widget = mo.ui.anywidget(raw)
raw.update_data(new_data)  # Works
```

### 5. Static Assets (Workers, WASM, Images)

External static assets beyond the main JS file are an **open problem**.
See [marimo#3279](https://github.com/marimo-team/marimo/issues/3279).

Workarounds:
- Inline scripts when possible
- Use CDN URLs for dependencies
- Avoid web workers if possible

## Development Workflow

### Hot Module Replacement (HMR)

```bash
# Enable HMR for live reload during development
ANYWIDGET_HMR=1 marimo edit notebooks/demo.py
```

### Bundling (for complex widgets)

```bash
# Using esbuild (recommended for simplicity)
npx esbuild --bundle --format=esm --outdir=mypackage/static src/index.js

# Using Vite (for React/Vue widgets)
npx vite build
```

### Vite Development URL

```python
# During development with Vite
class DevWidget(anywidget.AnyWidget):
    _esm = "http://localhost:5173/src/index.js?anywidget"
```

## Best Practices

1. **Check existing widgets first**: Browse [marimo gallery](https://marimo.io/gallery/widgets) and [anywidget.dev](https://anywidget.dev/)

2. **Start with wigglystuff**: The [wigglystuff repo](https://github.com/koaning/wigglystuff) has simple widget examples

3. **Use JSDoc for types** (avoid TypeScript unless bundling):
   ```javascript
   /** @param {{ model: any, el: HTMLElement }} context */
   function render({ model, el }) { ... }
   ```

4. **Return cleanup functions** for animations/intervals:
   ```javascript
   function render({ model, el }) {
     const id = setInterval(update, 100);
     return () => clearInterval(id);
   }
   export default { render };
   ```

5. **Namespace CSS** to avoid global conflicts:
   ```css
   .mywidget-container { ... }
   .mywidget-button { ... }
   ```

## Fixing Existing Widgets

To fix the kgents widgets, update each JS file:

```javascript
// Before (WRONG)
export function render({ model, el }) {
  // ... widget code ...
}

// After (CORRECT)
function render({ model, el }) {
  // ... widget code ...
}
export default { render };
```

Files to update:
- `impl/claude/agents/i/marimo/widgets/js/stigmergic_field.js`
- `impl/claude/agents/i/marimo/widgets/js/dialectic.js`
- `impl/claude/agents/i/marimo/widgets/js/timeline.js`

## Resources

- [Marimo AnyWidget Docs](https://docs.marimo.io/api/inputs/anywidget/)
- [AnyWidget Getting Started](https://anywidget.dev/en/getting-started/)
- [AFM Specification](https://anywidget.dev/en/afm/)
- [Bundling Guide](https://anywidget.dev/en/bundling/)
- [Marimo Blog: Build plugins with anywidget](https://marimo.io/blog/anywidget)

---

*"The noun is a lie. There is only the rate of change. And now, the rate of change is wrapped in `mo.ui.anywidget()`."*
