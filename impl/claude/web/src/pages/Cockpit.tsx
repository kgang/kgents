/**
 * Cockpit — Kent's Developer Portal
 *
 * The Anti-Sausage Protocol manifest as UI. This is Kent's daily entry point
 * into kgents — not a user-facing dashboard, but a developer's cockpit.
 *
 * "The cockpit is where Kent meets himself at the start of each day."
 *
 * Features:
 * - Voice anchors (rotating quotes from _focus.md)
 * - Session ritual checklist
 * - Crown Jewel status with ghost badges
 * - Quick launch buttons
 * - Recent traces (Différance Engine)
 * - Anti-Sausage end-of-session check
 *
 * @see CLAUDE.md Anti-Sausage Protocol
 * @see plans/_focus.md Kent's wishes
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Compass, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { Breathe } from '@/components/joy';
import { VoiceAnchor } from '@/components/cockpit/VoiceAnchor';
import { RecentTracesPanel, GhostBadge } from '@/components/differance';
import { brainApi, gestaltApi, gardenerApi } from '@/api/client';
import { useGhosts } from '@/hooks/useDifferanceQuery';
import { JEWEL_COLORS, JEWEL_ICONS, type JewelName } from '@/constants/jewels';
import { SESSION_RITUAL_ITEMS, ANTI_SAUSAGE_QUESTIONS } from '@/constants/voiceAnchors';
import { useShell } from '@/shell/ShellProvider';

// =============================================================================
// Types
// =============================================================================

interface JewelStatus {
  jewel: JewelName;
  label: string;
  value: string | number;
  subtext?: string;
  route: string;
  ghostCount?: number;
}

interface CockpitState {
  loading: boolean;
  error?: string;
  brain: { crystals: number } | null;
  gestalt: { grade: string; healthy: boolean } | null;
  gardener: { season: string; plots: number } | null;
}

// =============================================================================
// Session Storage Keys
// =============================================================================

const RITUAL_STORAGE_KEY = 'kgents-cockpit-ritual';
const ANTI_SAUSAGE_STORAGE_KEY = 'kgents-cockpit-antisausage';

// =============================================================================
// Sub-Components
// =============================================================================

/**
 * Session timestamp showing current date/time.
 */
function SessionTimestamp() {
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex items-center gap-2 text-gray-400 text-sm">
      <Clock className="w-4 h-4" />
      <span>
        {now.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
        })}{' '}
        •{' '}
        {now.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </span>
    </div>
  );
}

/**
 * Collapsible checklist panel.
 */
function ChecklistPanel({
  title,
  items,
  storageKey,
  defaultExpanded = false,
  variant = 'default',
}: {
  title: string;
  items: readonly { id: string; label?: string; question?: string; detail?: string }[];
  storageKey: string;
  defaultExpanded?: boolean;
  variant?: 'default' | 'warning';
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [checked, setChecked] = useState<Record<string, boolean>>(() => {
    try {
      const stored = sessionStorage.getItem(storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  });

  // Persist to session storage
  useEffect(() => {
    sessionStorage.setItem(storageKey, JSON.stringify(checked));
  }, [checked, storageKey]);

  const toggleItem = (id: string) => {
    setChecked((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const completedCount = items.filter((item) => checked[item.id]).length;
  const allComplete = completedCount === items.length;

  const borderColor = variant === 'warning' ? 'border-amber-700/50' : 'border-gray-700/50';
  const headerBg = variant === 'warning' ? 'bg-amber-900/20' : 'bg-gray-800/40';

  return (
    <div className={`rounded-xl border ${borderColor} overflow-hidden`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className={`w-full flex items-center justify-between px-4 py-3 ${headerBg} hover:bg-gray-700/30 transition-colors`}
      >
        <div className="flex items-center gap-3">
          <span className="font-medium text-gray-200">{title}</span>
          {allComplete && (
            <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
              Complete
            </span>
          )}
          {!allComplete && completedCount > 0 && (
            <span className="text-xs text-gray-500">
              {completedCount}/{items.length}
            </span>
          )}
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        )}
      </button>

      {expanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="px-4 py-3 space-y-2"
        >
          {items.map((item) => (
            <label key={item.id} className="flex items-start gap-3 cursor-pointer group">
              <input
                type="checkbox"
                checked={checked[item.id] ?? false}
                onChange={() => toggleItem(item.id)}
                className="mt-1 w-4 h-4 rounded border-gray-600 bg-gray-700 text-cyan-500 focus:ring-cyan-500/50"
              />
              <div className="flex-1">
                <span
                  className={`text-sm ${
                    checked[item.id] ? 'text-gray-500 line-through' : 'text-gray-300'
                  } group-hover:text-gray-200 transition-colors`}
                >
                  {item.label || item.question}
                </span>
                {item.detail && <p className="text-xs text-gray-500 mt-0.5">{item.detail}</p>}
              </div>
            </label>
          ))}
        </motion.div>
      )}
    </div>
  );
}

/**
 * Crown Jewel status card with integrated GhostBadge.
 */
function JewelCard({ status }: { status: JewelStatus }) {
  const navigate = useNavigate();
  const Icon = JEWEL_ICONS[status.jewel];
  const colors = JEWEL_COLORS[status.jewel];

  return (
    <motion.button
      onClick={() => navigate(status.route)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="flex flex-col items-start p-4 rounded-xl bg-gray-800/50 border border-gray-700/50 hover:border-gray-600 transition-colors text-left w-full"
    >
      <div className="flex items-center justify-between w-full mb-2">
        <Icon className="w-5 h-5" style={{ color: colors.primary }} />
        {status.ghostCount !== undefined && status.ghostCount > 0 && (
          <GhostBadge count={status.ghostCount} size="sm" />
        )}
      </div>
      <span className="text-sm font-medium text-gray-300">{status.label}</span>
      <span className="text-lg font-bold text-white">{status.value}</span>
      {status.subtext && <span className="text-xs text-gray-500 mt-1">{status.subtext}</span>}
    </motion.button>
  );
}

/**
 * Quick launch button for a jewel.
 *
 * IMPORTANT: All paths MUST be registered in the AGENTESE registry.
 * The registry (@node decorator) is the single source of truth.
 */
function QuickLaunchButton({ jewel, label }: { jewel: JewelName; label: string }) {
  const navigate = useNavigate();
  const Icon = JEWEL_ICONS[jewel];
  const colors = JEWEL_COLORS[jewel];

  // AGENTESE-as-Route: The URL IS the AGENTESE path
  // Only include paths that have @node registered
  const routes: Partial<Record<JewelName, string>> = {
    brain: '/self.memory',
    gestalt: '/world.codebase',
    gardener: '/concept.gardener',
    forge: '/world.forge',
    coalition: '/world.town',
    park: '/world.park',
    // domain: Not yet implemented - no @node registered
  };

  const route = routes[jewel];
  if (!route) return null; // Skip unregistered jewels

  return (
    <Breathe intensity={0.15} speed="slow">
      <motion.button
        onClick={() => navigate(route)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800/60 border border-gray-700/50 hover:border-gray-600 transition-colors"
      >
        <Icon className="w-4 h-4" style={{ color: colors.primary }} />
        <span className="text-sm text-gray-300">{label}</span>
      </motion.button>
    </Breathe>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Cockpit — Kent's daily developer portal.
 *
 * Replaces the user-facing Crown page with a developer-first experience
 * that manifests the Anti-Sausage Protocol.
 */
export default function Cockpit() {
  const navigate = useNavigate();
  const { density } = useShell();
  const [state, setState] = useState<CockpitState>({
    loading: true,
    brain: null,
    gestalt: null,
    gardener: null,
  });

  // Fetch ghost counts from Différance Engine
  const { data: ghostsData } = useGhosts({
    enabled: true,
    explorableOnly: false,
    limit: 100,
  });

  // Calculate ghost counts per jewel (based on operation prefixes in context)
  const ghostCounts = useMemo(() => {
    if (!ghostsData) return { brain: 0, gestalt: 0, gardener: 0, forge: 0 };

    const counts = { brain: 0, gestalt: 0, gardener: 0, forge: 0 };
    for (const ghost of ghostsData.ghosts) {
      // Infer jewel from operation name patterns
      const op = ghost.operation.toLowerCase();
      if (op.includes('capture') || op.includes('surface') || op.includes('crystal')) {
        counts.brain++;
      } else if (op.includes('gesture') || op.includes('plant') || op.includes('nurture')) {
        counts.gardener++;
      } else if (op.includes('scan') || op.includes('health') || op.includes('drift')) {
        counts.gestalt++;
      } else if (op.includes('commission') || op.includes('bid') || op.includes('exhibit')) {
        counts.forge++;
      }
    }
    return counts;
  }, [ghostsData]);

  // Fetch status from all jewels
  const fetchStatus = useCallback(async () => {
    try {
      const [brainRes, gestaltRes, gardenerRes] = await Promise.allSettled([
        brainApi.getStatus(),
        gestaltApi.getHealth(),
        gardenerApi.getGarden(),
      ]);

      setState({
        loading: false,
        brain:
          brainRes.status === 'fulfilled' && brainRes.value
            ? { crystals: brainRes.value.concept_count }
            : null,
        gestalt:
          gestaltRes.status === 'fulfilled' && gestaltRes.value
            ? {
                grade: gestaltRes.value.overall_grade,
                healthy:
                  gestaltRes.value.overall_grade === 'A' || gestaltRes.value.overall_grade === 'A+',
              }
            : null,
        gardener:
          gardenerRes.status === 'fulfilled' && gardenerRes.value
            ? {
                season: gardenerRes.value.season,
                plots: Object.keys(gardenerRes.value.plots ?? {}).length,
              }
            : null,
      });
    } catch (error) {
      console.debug('Cockpit: Failed to fetch status', error);
      setState((s) => ({ ...s, loading: false, error: 'Backend not connected' }));
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Navigate to heritage exploration
  const handleExploreHeritage = useCallback(
    (traceId: string) => {
      // Navigate to Différance page with trace selected (AGENTESE path)
      navigate(`/time.differance?trace=${traceId}`);
    },
    [navigate]
  );

  // Navigate to full Différance view
  const handleViewAllTraces = useCallback(() => {
    navigate('/time.differance');
  }, [navigate]);

  // Build jewel status cards with real ghost counts (AGENTESE paths)
  const jewelStatuses: JewelStatus[] = useMemo(() => {
    const statuses: JewelStatus[] = [
      {
        jewel: 'brain',
        label: 'Brain',
        value: state.brain?.crystals ?? '—',
        subtext: 'crystals',
        route: '/self.memory',
        ghostCount: ghostCounts.brain,
      },
      {
        jewel: 'gestalt',
        label: 'Gestalt',
        value: state.gestalt?.grade ?? '—',
        subtext: state.gestalt?.healthy ? 'healthy' : 'needs attention',
        route: '/world.codebase',
        ghostCount: ghostCounts.gestalt,
      },
      {
        jewel: 'gardener',
        label: 'Gardener',
        value: state.gardener?.season ?? '—',
        subtext: state.gardener ? `${state.gardener.plots} plots` : undefined,
        route: '/concept.gardener',
        ghostCount: ghostCounts.gardener,
      },
      {
        jewel: 'forge',
        label: 'Forge',
        value: 'Ready',
        subtext: 'awaiting commission',
        route: '/world.forge',
        ghostCount: ghostCounts.forge,
      },
    ];
    return statuses;
  }, [state, ghostCounts]);

  const isMobile = density === 'compact';

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div className="flex items-center gap-3">
            <Breathe intensity={0.3} speed="slow">
              <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                <Compass className="w-6 h-6 text-cyan-400" />
              </div>
            </Breathe>
            <div>
              <h1 className="text-xl font-bold text-white">Kent's Cockpit</h1>
              <p className="text-xs text-gray-500">The garden awaits</p>
            </div>
          </div>
          <SessionTimestamp />
        </motion.header>

        {/* Voice Anchor — Prominent */}
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <VoiceAnchor rotationInterval={25000} />
        </motion.section>

        {/* Session Start Ritual */}
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-6"
        >
          <ChecklistPanel
            title="Session Start Ritual"
            items={SESSION_RITUAL_ITEMS}
            storageKey={RITUAL_STORAGE_KEY}
            defaultExpanded={true}
          />
        </motion.section>

        {/* Crown Jewel Status */}
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
            Crown Jewels
          </h2>
          <div className={`grid gap-3 ${isMobile ? 'grid-cols-2' : 'grid-cols-4'}`}>
            {jewelStatuses.map((status) => (
              <JewelCard key={status.jewel} status={status} />
            ))}
          </div>
        </motion.section>

        {/* Quick Launch */}
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-8"
        >
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
            Quick Launch
          </h2>
          <div className="flex flex-wrap gap-2">
            <QuickLaunchButton jewel="brain" label="Brain" />
            <QuickLaunchButton jewel="gestalt" label="Gestalt" />
            <QuickLaunchButton jewel="gardener" label="Gardener" />
            <QuickLaunchButton jewel="forge" label="Forge" />
            <QuickLaunchButton jewel="coalition" label="Town" />
            <QuickLaunchButton jewel="park" label="Park" />
          </div>
        </motion.section>

        {/* Recent Traces — Différance Engine Integration */}
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-8"
        >
          <RecentTracesPanel
            limit={10}
            onViewAll={handleViewAllTraces}
            onExploreHeritage={handleExploreHeritage}
            compact={isMobile}
          />
        </motion.section>

        {/* Anti-Sausage Check — End of session */}
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mb-8"
        >
          <ChecklistPanel
            title="Anti-Sausage Check (Before Ending)"
            items={ANTI_SAUSAGE_QUESTIONS}
            storageKey={ANTI_SAUSAGE_STORAGE_KEY}
            defaultExpanded={false}
            variant="warning"
          />
        </motion.section>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="text-center text-gray-600 text-xs pt-4 border-t border-gray-800"
        >
          <p>"The persona is a garden, not a museum."</p>
        </motion.footer>
      </div>
    </div>
  );
}
