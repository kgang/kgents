import { createBrowserRouter } from 'react-router-dom';
import { Shell } from '../shell/Shell';
import { PilotSelector } from '../shell/PilotSelector';
import { DailyLabLayout } from '../pilots/daily-lab';
import { ZeroSeedLayout } from '../pilots/zero-seed';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Shell />,
    children: [
      { index: true, element: <PilotSelector /> },
      {
        path: 'daily-lab/*',
        element: <DailyLabLayout />,
      },
      {
        path: 'zero-seed/*',
        element: <ZeroSeedLayout />,
      },
    ],
  },
]);
