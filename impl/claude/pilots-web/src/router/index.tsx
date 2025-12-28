/**
 * Router Configuration for Pilots Web
 *
 * Active Pilots:
 * - /pilots/wasm-survivors - WASM Survivors Witnessed Run Lab
 * - /pilots/sprite-procedural-taste-lab - Sprite Procedural Taste Lab
 * - / - Redirect to wasm-survivors (current focus)
 *
 * Pending Pilots (not yet implemented in pilots-web):
 * - /pilots/daily-lab - Trail to Crystal Daily Lab
 * - /pilots/zero-seed - Zero Seed Personal Governance Lab
 * - /pilots/disney-portal-planner - Disney Portal Planner
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { WASMSurvivors } from '@/pilots/wasm-survivors';
import { SpriteTasteLab } from '@/pilots/sprite-procedural-taste-lab';

/**
 * Application router
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/pilots/wasm-survivors" replace />,
  },
  {
    path: '/pilots/wasm-survivors',
    element: <WASMSurvivors />,
  },
  {
    path: '/pilots/sprite-procedural-taste-lab',
    element: <SpriteTasteLab />,
  },
]);

export default router;
