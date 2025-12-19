/**
 * Town - Agent Town Simulation (Projection-first, SSE streaming)
 *
 * A projection-first page using StreamPathProjection for SSE-based data.
 * All business logic delegated to hooks and visualization components.
 *
 * AGENTESE Route: /world.town.simulation?townId=demo
 *
 * @see spec/protocols/os-shell.md - Part III: Projection-First Rendering
 * @see docs/skills/crown-jewel-patterns.md
 */
import { useSearchParams } from 'react-router-dom';
import { useTownLoader, useTownStreamWidget } from '../hooks';
import { StreamPathProjection } from '../shell/StreamPathProjection';
import { TownVisualization } from '../components/town/TownVisualization';

export default function TownPage() {
  // AGENTESE style: parameters flow through query strings
  const [searchParams] = useSearchParams();
  const paramTownId = searchParams.get('townId') || 'demo';
  const loader = useTownLoader(paramTownId);
  const stream = useTownStreamWidget({ townId: loader.townId || '', autoConnect: !!loader.townId });

  return (
    <StreamPathProjection
      jewel="coalition"
      loader={loader}
      stream={stream}
      notFoundAction="Create Demo Town"
      onNotFoundAction={() => (window.location.href = '/world.town.simulation?townId=demo')}
    >
      {(s, ctx) => (
        <TownVisualization
          townId={ctx.entityId}
          dashboard={s.dashboard}
          events={s.events}
          isConnected={s.isConnected}
          isPlaying={s.isPlaying}
          speed={1}
          density={ctx.density}
          isMobile={ctx.isMobile}
          isTablet={ctx.isTablet}
          isDesktop={ctx.isDesktop}
          onConnect={s.connect}
          onDisconnect={s.disconnect}
          onSpeedChange={() => {}}
        />
      )}
    </StreamPathProjection>
  );
}
