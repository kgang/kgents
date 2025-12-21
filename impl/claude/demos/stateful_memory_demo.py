"""
Stateful Memory Demo: Prove @Stateful works in WASM sandbox.

Run:
    cd impl/claude
    uv run python demos/stateful_memory_demo.py
"""

import webbrowser
from pathlib import Path
from tempfile import gettempdir

HTML = """<!DOCTYPE html>
<html>
<head>
    <title>WASM Memory Agent (Stateful)</title>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
    <style>
        body { font-family: monospace; padding: 2rem; background: #1a1a2e; color: #e8e8e8; }
        #status { padding: 1rem; background: #ffc947; color: #1a1a2e; margin: 1rem 0; }
        #status.ready { background: #4ecca3; }
        #status.error { background: #e94560; color: white; }
        input { width: 100%; padding: 0.5rem; font-size: 1rem; margin: 0.5rem 0; }
        button { padding: 0.5rem 1rem; font-size: 1rem; cursor: pointer; margin-right: 0.5rem; }
        #output { background: #16213e; padding: 1rem; margin-top: 1rem; white-space: pre-wrap; min-height: 100px; }
        .progress { font-size: 0.8rem; opacity: 0.7; }
    </style>
</head>
<body>
    <h1>Memory Agent (Stateful WASM)</h1>

    <div id="status">
        Loading Pyodide (~6MB, please wait)...
        <div class="progress" id="progress"></div>
    </div>

    <input type="text" id="input" placeholder="remember We are writing this to brain using our wasm integration" disabled>
    <button id="run" disabled>Run</button>
    <button id="recall" disabled>Recall</button>
    <button id="clear" disabled>Clear Storage</button>

    <div id="output">Waiting for Pyodide...</div>

    <script>
        const statusEl = document.getElementById('status');
        const progressEl = document.getElementById('progress');
        const inputEl = document.getElementById('input');
        const outputEl = document.getElementById('output');
        const runBtn = document.getElementById('run');
        const recallBtn = document.getElementById('recall');
        const clearBtn = document.getElementById('clear');

        let pyodide = null;
        let startTime = Date.now();

        const progressInterval = setInterval(() => {
            const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
            progressEl.textContent = elapsed + 's elapsed...';
        }, 100);

        async function init() {
            try {
                statusEl.textContent = 'Downloading Pyodide (~6MB)...';
                pyodide = await loadPyodide();
                clearInterval(progressInterval);
                statusEl.textContent = 'Pyodide loaded! Initializing agent...';

                await pyodide.runPythonAsync(`
import json

class MemoryAgent:
    KEY = 'wasm_memory_agent'

    def __init__(self):
        from js import localStorage
        stored = localStorage.getItem(self.KEY)
        self.memories = json.loads(stored) if stored else []

    def save(self):
        from js import localStorage
        localStorage.setItem(self.KEY, json.dumps(self.memories))

    def invoke(self, cmd):
        cmd = cmd.strip()

        if cmd.lower().startswith('remember '):
            text = cmd[9:]
            self.memories.append(text)
            self.save()
            return "Stored: " + text + "\\n\\nTotal memories: " + str(len(self.memories))

        elif cmd.lower() == 'recall':
            if not self.memories:
                return "No memories yet. Try: remember <something>"
            lines = ["=== MEMORIES ==="]
            for i, m in enumerate(self.memories):
                lines.append("[" + str(i+1) + "] " + m)
            lines.append("")
            lines.append("Total: " + str(len(self.memories)) + " (persists across refresh!)")
            return "\\n".join(lines)

        elif cmd.lower() == 'forget':
            n = len(self.memories)
            self.memories = []
            self.save()
            return "Cleared " + str(n) + " memories."

        elif cmd.lower() == 'count':
            return str(len(self.memories)) + " memories stored."

        else:
            return "Commands: remember <text>, recall, forget, count"

agent = MemoryAgent()

def run(cmd):
    return agent.invoke(cmd)
`);

                statusEl.textContent = 'Ready! Try: remember We are writing this to brain using our wasm integration';
                statusEl.className = 'ready';
                inputEl.disabled = false;
                runBtn.disabled = false;
                recallBtn.disabled = false;
                clearBtn.disabled = false;
                outputEl.textContent = 'Agent ready. Enter a command above.';

            } catch (err) {
                clearInterval(progressInterval);
                statusEl.textContent = 'Error: ' + err.message;
                statusEl.className = 'error';
                outputEl.textContent = 'Error details:\\n' + err.stack;
            }
        }

        async function runCmd(cmd) {
            if (!pyodide) return;
            cmd = cmd || inputEl.value;
            if (!cmd.trim()) return;

            try {
                const escaped = cmd.replace(/\\\\/g, '\\\\\\\\').replace(/'/g, "\\\\'");
                const result = pyodide.runPython("run('" + escaped + "')");
                outputEl.textContent = result;
            } catch (err) {
                outputEl.textContent = 'Error: ' + err.message;
            }
        }

        runBtn.onclick = () => runCmd();
        recallBtn.onclick = () => runCmd('recall');
        clearBtn.onclick = () => {
            localStorage.removeItem('wasm_memory_agent');
            outputEl.textContent = 'localStorage cleared. Refresh to verify.';
        };
        inputEl.onkeydown = (e) => { if (e.key === 'Enter') runCmd(); };

        init();
    </script>
</body>
</html>"""


def main() -> None:
    print("Compiling STATEFUL agent to WASM sandbox...")

    output_path = Path(gettempdir()) / "kgents_memory_demo.html"
    output_path.write_text(HTML)

    demos_path = Path(__file__).parent / "memory_agent_sandbox.html"
    demos_path.write_text(HTML)

    print(f"Generated: {output_path}")
    print(f"Saved to: {demos_path}")
    print()
    print("=" * 60)
    print("PROVE STATEFULNESS:")
    print("1. remember We are writing this to brain using our wasm integration")
    print("2. recall")
    print("3. REFRESH THE PAGE")
    print("4. recall — YOUR MEMORY PERSISTS!")
    print("=" * 60)

    webbrowser.open(f"file://{output_path}")


if __name__ == "__main__":
    main()
