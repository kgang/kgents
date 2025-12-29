/**
 * Router Configuration for Pilots Web
 *
 * Active Pilots:
 * - /pilots/wasm-survivors-game - WASM Survivors Game
 * - / - Redirect to wasm-survivors-game (current focus)
 *
 * Pending Pilots (not yet implemented in pilots-web):
 * - /pilots/daily-lab - Trail to Crystal Daily Lab
 * - /pilots/zero-seed - Zero Seed Personal Governance Lab
 * - /pilots/disney-portal-planner - Disney Portal Planner
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { WASMSurvivors } from '@/pilots/wasm-survivors-game';

/**
 * Application router
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/pilots/wasm-survivors-game" replace />,
  },
  {
    path: '/pilots/wasm-survivors-game',
    element: <WASMSurvivors />,
  },
]);

export default router;
