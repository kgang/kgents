---
context: self
---

# Terminal Integration Learnings

> *Synthesized from tmux mouse event audit (2025-12-19)*

---

## The Problem: Tmux + Raw Mode = Event Storm

When attaching to a tmux session while raw mode is active:
1. Tmux mouse events arrive as escape sequences (`\033[M...` or `\033[<...M`)
2. `sys.stdin.read(1)` reads one byte at a time
3. Multi-byte sequences fragment into garbage
4. Each byte triggers key handlers with invalid input
5. If events stream to chat, garbage floods the UI

---

## Root Cause Analysis

### Critical Files

| File | Line | Vulnerability |
|------|------|--------------|
| `agents/i/tui.py` | 420 | `sys.stdin.read(1)` fragments mouse sequences |
| `agents/i/tui.py` | 432 | `tty.setraw()` without mouse disable |
| `protocols/cli/repl.py` | 2017 | `_get_key_nonblocking()` same 1-byte issue |
| `protocols/cli/repl.py` | 2222 | Raw mode without mouse protocol disable |

### Why 1-Byte Reads Fail

```
Mouse click = "\033[M abc" (6 bytes minimum)
Read(1) → \033 (processed as escape? partial?)
Read(1) → [ (processed as bracket? garbage?)
Read(1) → M (processed as 'M' key!)
...
```

Each byte processed independently = 6+ spurious "key presses" per mouse click.

---

## The Fix: Three-Part Defense

### 1. Disable Mouse Before Raw Mode

```python
# BEFORE entering raw mode:
print("\033[?1000l", end="", flush=True)  # Disable X10 mouse
print("\033[?1002l", end="", flush=True)  # Disable button tracking
print("\033[?1003l", end="", flush=True)  # Disable all motion
print("\033[?1006l", end="", flush=True)  # Disable SGR extended

tty.setraw(sys.stdin.fileno())

# AFTER restoring:
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
# Re-enable mouse if needed by parent (tmux handles this)
```

### 2. Read Complete Escape Sequences

```python
def _get_key_complete() -> Optional[str]:
    """Read complete key or escape sequence (non-blocking)."""
    import select

    if not select.select([sys.stdin], [], [], 0.0)[0]:
        return None

    char = sys.stdin.read(1)

    # Not escape? Return single char
    if char != '\033':
        return char

    # Escape sequence: read until terminator or timeout
    seq = char
    for _ in range(10):  # Max 10 chars for safety
        if select.select([sys.stdin], [], [], 0.01)[0]:
            next_char = sys.stdin.read(1)
            seq += next_char
            # CSI sequences terminate on letter
            if next_char.isalpha():
                break
        else:
            break  # No more input

    return seq
```

### 3. Validate Before Processing

```python
VALID_KEYS = set('hjklq?:r')  # Known commands
ESCAPE_SEQUENCES = {
    '\033[A': 'up',
    '\033[B': 'down',
    '\033[C': 'right',
    '\033[D': 'left',
}

def _handle_key(key: str, state) -> bool:
    """Handle key with validation."""
    # Known single key?
    if key in VALID_KEYS:
        return _process_command(key, state)

    # Known escape sequence?
    if key in ESCAPE_SEQUENCES:
        return _process_arrow(ESCAPE_SEQUENCES[key], state)

    # Mouse event? Ignore silently
    if key.startswith('\033[M') or key.startswith('\033[<'):
        return False  # Swallow mouse, don't propagate

    # Unknown: log and ignore
    logger.debug(f"Ignored: {repr(key)}")
    return False
```

---

## User Workaround (Immediate)

If experiencing mouse event storms in tmux:

```bash
# Option 1: Disable tmux mouse entirely
tmux set-option -g mouse off

# Option 2: In ~/.tmux.conf (permanent)
set-option -g mouse off

# Option 3: Detach/reattach after disabling
tmux set-option -g mouse off
# Ctrl-B d (detach), then tmux attach
```

---

## Architecture Insight

The **TerminalService** (web) doesn't have this problem because:
1. Browser handles input events natively
2. No raw mode needed
3. Terminal input is via React controlled input

The problem is **CLI-only** in:
- `agents/i/tui.py` (I-gent TUI)
- `protocols/cli/repl.py` (ambient mode)

---

## Related Systems

| System | Uses Raw Mode | Mouse Risk |
|--------|--------------|------------|
| I-gent TUI | Yes (`tui.py:432`) | HIGH |
| REPL ambient | Yes (`repl.py:2222`) | HIGH |
| Web Shell | No (browser) | NONE |
| Reflector | No (output only) | NONE |
| SSE streaming | No (server → client) | NONE |

---

## Testing Checklist

```bash
# Test 1: Tmux mouse event handling
tmux new-session -d -s test
tmux send-keys -t test "cd impl/claude && python -c \"import tty, sys, termios; old=termios.tcgetattr(sys.stdin); tty.setraw(sys.stdin.fileno()); print('raw mode'); termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)\"" Enter
tmux attach -t test
# Move mouse - should NOT flood with garbage

# Test 2: Escape sequence validation
python -c "
key = '\033[M abc'  # Mouse event
valid = key in {'h','j','k','l','q'}
print(f'Valid key: {valid}')  # Should be False
"

# Test 3: Complete sequence reading
echo -e '\033[Mtest' | python -c "
import sys
data = sys.stdin.read()
print(f'Received {len(data)} chars: {repr(data)}')"
```

---

## Pattern: Terminal Discipline

**Entering raw mode is a contract**:
1. Save terminal state (`termios.tcgetattr`)
2. Disable unwanted protocols (mouse, bracketed paste)
3. Set raw mode
4. Read complete sequences (not byte-by-byte)
5. Validate before processing
6. Restore terminal state in `finally`

---

*Lines: 140. Topic: Terminal/Tmux integration.*
*Audit date: 2025-12-19*
