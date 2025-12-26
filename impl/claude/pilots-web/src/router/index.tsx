/**
 * Router Configuration for Pilots Web
 *
 * Routes:
 * - /pilots/daily-lab - Daily Lab pilot (Trail to Crystal)
 * - /pilots/zero-seed - Zero Seed Personal Governance Lab
 * - / - Redirect to daily-lab (for now)
 */

import { createBrowserRouter, Navigate } from 'react-router-dom';
import { DailyLabPilot } from '@/pilots/daily-lab';
import { ZeroSeedLabPilot } from '@/pilots/zero-seed';

/**
 * Application router
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/pilots/daily-lab" replace />,
  },
  {
    path: '/pilots/daily-lab',
    element: <DailyLabPilot />,
  },
  {
    path: '/pilots/zero-seed',
    element: <ZeroSeedLabPilot />,
  },
]);

export default router;
