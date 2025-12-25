import { useLocation } from 'react-router-dom';
import { TelescopeShell } from './components/layout/TelescopeShell';
import { AppShell } from './components/layout/AppShell';
import { AgenteseRouter } from './router';
import { parseAgentesePath } from './router';

/**
 * kgents Web — Pure AGENTESE Navigation (Phase 3)
 *
 * AGENTESE-ONLY ROUTING:
 * URLs are AGENTESE paths directly:
 * - /self.chat → Chat page
 * - /self.memory → Memory feed
 * - /self.director → Director canvas
 * - /world.document → Hypergraph Editor
 * - /world.chart → Astronomical chart
 * - /void.telescope → Proof Engine with telescope
 *
 * Legacy routes (/chat, /editor, /brain, etc.) redirect with deprecation warnings.
 *
 * Shell Selection:
 * - void.telescope → TelescopeShell (7-layer epistemic navigation)
 * - All other AGENTESE → AppShell (standard app chrome)
 * - Root path → Welcome screen
 */

function App() {
  const location = useLocation();

  // Determine shell based on AGENTESE context
  let shell: 'telescope' | 'app' | 'none' = 'none';

  try {
    const path = parseAgentesePath(location.pathname);

    // void.telescope gets TelescopeShell
    if (path.fullPath.startsWith('void.telescope')) {
      shell = 'telescope';
    }
    // All other AGENTESE paths get AppShell
    else if (path.context) {
      shell = 'app';
    }
  } catch {
    // Root path or invalid AGENTESE path
    shell = 'none';
  }

  return (
    <>
      {shell === 'telescope' ? (
        <TelescopeShell>
          <AgenteseRouter />
        </TelescopeShell>
      ) : shell === 'app' ? (
        <AppShell>
          <AgenteseRouter />
        </AppShell>
      ) : (
        <AgenteseRouter />
      )}
    </>
  );
}

export default App;
