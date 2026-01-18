import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

// SEVERE STARK styles
import './design/severe-tokens.css';
import './styles/severe-base.css';
import './styles/components.css';
import './styles/workspace.css';

/**
 * Entry point — Minimal.
 *
 * SEVERE STARK: No animations, no web vitals, no extras.
 */
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
