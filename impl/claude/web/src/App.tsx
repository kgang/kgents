import { AppShell } from './components/layout/AppShell';
import { AgenteseRouter } from './router';
import { ModeProvider } from './context/ModeContext';

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
 *
 * MODE SYSTEM:
 * - Six-mode editing system (NORMAL, INSERT, EDGE, VISUAL, COMMAND, WITNESS)
 * - ModeProvider wraps entire app for global keyboard handling
 * - Mode indicator integrated into WitnessFooter (right side when collapsed)
 */

function App() {
  return (
    <ModeProvider initialMode="NORMAL" enableKeyboard={true}>
      <AppShell>
        <AgenteseRouter />
      </AppShell>
    </ModeProvider>
  );
}

export default App;
