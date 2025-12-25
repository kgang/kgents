import { AppShell } from './components/layout/AppShell';
import { AgenteseRouter } from './router';

/**
 * kgents Web — UX TRANSFORMATION (2025-12-25)
 *
 * "The Hypergraph Editor IS the app. Everything else is a sidebar."
 *
 * SIMPLIFIED ROUTING:
 * - / → redirects to /world.document (the editor)
 * - /world.document → Hypergraph Editor (THE app)
 * - /self.chat → Chat (becoming right sidebar)
 * - /self.director → Director (becoming left sidebar)
 *
 * DELETED:
 * - TelescopeShell (void.telescope no longer exists)
 * - WelcomePage (no welcome, open directly to editor)
 * - ZeroSeedPage, ChartPage, FeedPage (features deleted)
 *
 * All routes now use AppShell.
 */

function App() {
  return (
    <AppShell>
      <AgenteseRouter />
    </AppShell>
  );
}

export default App;
