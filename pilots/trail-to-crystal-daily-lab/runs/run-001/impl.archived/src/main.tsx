/**
 * Pilots Web Application Entry Point
 *
 * Wraps the app with ThemeProvider and LayoutProvider for
 * consistent theming and responsive layout context.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { ThemeProvider } from './shell/ThemeProvider';
import { LayoutProvider } from './shell/LayoutProvider';
import { router } from './router';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider defaultMode="dark">
      <LayoutProvider>
        <RouterProvider router={router} />
      </LayoutProvider>
    </ThemeProvider>
  </React.StrictMode>
);
