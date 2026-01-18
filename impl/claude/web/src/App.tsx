import { BrowserRouter } from 'react-router-dom';
import { AgenteseRouter } from './router';
import './styles/globals.css';
import './styles/layout-constraints.css';

/**
 * kgents Web — SEVERE STARK
 *
 * Post-deletion: 88% reduction.
 * One page. No shell. No mode provider. Rebuild from here.
 */
function App() {
  return (
    <BrowserRouter>
      <AgenteseRouter />
    </BrowserRouter>
  );
}

export default App;
