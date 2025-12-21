import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { enableMapSet } from 'immer';
import App from './App';
import { LayoutSheafProvider } from './components/layout-sheaf';
import './styles/globals.css';
import './styles/animations.css';
import { reportWebVitalsToConsole } from './lib/reportWebVitals';

// Enable Immer's MapSet plugin for stores that use Map/Set
enableMapSet();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <LayoutSheafProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </LayoutSheafProvider>
  </StrictMode>,
);

// Report Core Web Vitals in development
if (import.meta.env.DEV) {
  reportWebVitalsToConsole();
}
