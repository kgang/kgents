import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { enableMapSet } from 'immer';
import App from './App';
import './styles/globals.css';

// Enable Immer's MapSet plugin for stores that use Map/Set
enableMapSet();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
