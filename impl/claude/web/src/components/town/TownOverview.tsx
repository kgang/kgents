/**
 * TownOverview - Dashboard for Agent Town
 *
 * Contract-driven dashboard showing Town health, citizens, and coalitions.
 * Uses React Query hooks with AGENTESE contract types.
 *
 * Design Language:
 * - Organic/crystalline aesthetic
 * - Violet theme (Coalition Crown Jewel)
 * - Subtle animations for data loading states
 *
 * @see docs/skills/elastic-ui-patterns.md
 * @see docs/skills/crown-jewel-patterns.md
 */

import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Users,
  MessageCircle,
  Network,
  Activity,
  UserPlus,
  Sparkles,
  ChevronRight,
  AlertCircle,
  TrendingUp,
} from 'lucide-react';
import { useTownManifest, useCitizens, useCoalitionManifest, useCoalitions } from '../../hooks';
import { useShell } from '../../shell/ShellProvider';
import { JEWEL_COLORS } from '../../constants/jewels';
import { TeachingCallout } from '../categorical';
import { TeachingToggle, WhenTeaching } from '../../hooks/useTeachingMode';

// =============================================================================
// Constants
// =============================================================================

const VIOLET = JEWEL_COLORS.coalition;

// =============================================================================
// Sub-components
// =============================================================================

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number | string;
  subtext?: string;
  trend?: 'up' | 'down' | 'stable';
  color?: string;
  onClick?: () => void;
}

function StatCard({ icon, label, value, subtext, trend, color = VIOLET.primary, onClick }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={onClick ? { scale: 1.02 } : undefined}
      onClick={onClick}
      className={`
        bg-violet-950/50 border border-violet-500/30 rounded-xl p-4
        ${onClick ? 'cursor-pointer hover:border-violet-400/50 hover:bg-violet-900/30 transition-colors' : ''}
      `}
    >
      <div className="flex items-start justify-between">
        <div className="p-2 rounded-lg bg-violet-500/20" style={{ color }}>
          {icon}
        </div>
        {trend && (
          <span className={`text-xs ${trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-400'}`}>
            {trend === 'up' && <TrendingUp className="w-4 h-4" />}
          </span>
        )}
      </div>
      <div className="mt-3">
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="text-sm text-gray-400">{label}</p>
        {subtext && <p className="text-xs text-gray-500 mt-1">{subtext}</p>}
      </div>
      {onClick && (
        <div className="mt-3 flex items-center text-xs text-violet-400">
          <span>View details</span>
          <ChevronRight className="w-3 h-3 ml-1" />
        </div>
      )}
    </motion.div>
  );
}

interface SectionHeaderProps {
  icon: React.ReactNode;
  title: string;
  action?: React.ReactNode;
}

function SectionHeader({ icon, title, action }: SectionHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <span className="text-violet-400">{icon}</span>
        <h2 className="text-lg font-semibold text-white">{title}</h2>
      </div>
      {action}
    </div>
  );
}

interface CitizenCardProps {
  name: string;
  archetype: string;
  isActive: boolean;
  interactionCount: number;
  onClick: () => void;
}

function CitizenCard({ name, archetype, isActive, interactionCount, onClick }: CitizenCardProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
      className="w-full p-3 bg-violet-950/30 border border-violet-500/20 rounded-lg text-left hover:border-violet-400/40 transition-colors"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-2 h-2 rounded-full ${isActive ? 'bg-green-400' : 'bg-gray-500'}`} />
          <div>
            <p className="font-medium text-white">{name}</p>
            <p className="text-xs text-gray-400 capitalize">{archetype}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-violet-400">{interactionCount}</p>
          <p className="text-xs text-gray-500">interactions</p>
        </div>
      </div>
    </motion.button>
  );
}

interface CoalitionCardProps {
  name: string;
  memberCount: number;
  strength: number;
  purpose: string;
  onClick: () => void;
}

function CoalitionCard({ name, memberCount, strength, purpose, onClick }: CoalitionCardProps) {
  const strengthPercent = Math.round(strength * 100);
  const strengthColor = strengthPercent > 70 ? 'bg-green-500' : strengthPercent > 40 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <motion.button
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
      className="w-full p-3 bg-violet-950/30 border border-violet-500/20 rounded-lg text-left hover:border-violet-400/40 transition-colors"
    >
      <div className="flex items-center justify-between mb-2">
        <p className="font-medium text-white">{name}</p>
        <span className="text-xs text-violet-400">{memberCount} members</span>
      </div>
      <p className="text-xs text-gray-400 mb-2 line-clamp-1">{purpose}</p>
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1.5 bg-violet-950 rounded-full overflow-hidden">
          <div
            className={`h-full ${strengthColor} transition-all`}
            style={{ width: `${strengthPercent}%` }}
          />
        </div>
        <span className="text-xs text-gray-400">{strengthPercent}%</span>
      </div>
    </motion.button>
  );
}

interface ErrorBannerProps {
  message: string;
}

function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <div className="bg-red-950/50 border border-red-500/30 rounded-lg p-4 flex items-center gap-3">
      <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
      <div>
        <p className="text-red-400 font-medium">Error loading data</p>
        <p className="text-sm text-red-300/70">{message}</p>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-violet-950/50 rounded-xl" />
        ))}
      </div>
      <div className="grid lg:grid-cols-2 gap-8">
        <div className="space-y-3">
          <div className="h-8 w-40 bg-violet-950/50 rounded" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-violet-950/50 rounded-lg" />
          ))}
        </div>
        <div className="space-y-3">
          <div className="h-8 w-40 bg-violet-950/50 rounded" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-violet-950/50 rounded-lg" />
          ))}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function TownOverview() {
  const navigate = useNavigate();
  const { density } = useShell();
  const isCompact = density === 'compact';

  // Fetch data using contract-driven hooks
  const manifest = useTownManifest();
  const citizens = useCitizens();
  const coalitionManifest = useCoalitionManifest();
  const coalitions = useCoalitions();

  // Loading state
  if (manifest.isLoading || citizens.isLoading) {
    return (
      <div className="p-4 lg:p-6">
        <LoadingSkeleton />
      </div>
    );
  }

  // Error state
  const error = manifest.error || citizens.error || coalitionManifest.error;
  if (error) {
    return (
      <div className="p-4 lg:p-6">
        <ErrorBanner message={(error as Error).message} />
      </div>
    );
  }

  const manifestData = manifest.data;
  const citizensData = citizens.data?.citizens ?? [];
  const coalitionManifestData = coalitionManifest.data;
  const coalitionsData = coalitions.data?.coalitions ?? [];

  return (
    <div className={`${isCompact ? 'p-3' : 'p-4 lg:p-6'} space-y-6`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-violet-500/20">
            <Users className="w-6 h-6 text-violet-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Agent Town</h1>
            <p className="text-sm text-gray-400">Coalition Crown Jewel</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <TeachingToggle compact />
          <button
            onClick={() => navigate('/town/simulation')}
            className="flex items-center gap-2 px-4 py-2 bg-violet-500 hover:bg-violet-400 rounded-lg text-white font-medium transition-colors"
          >
            <Sparkles className="w-4 h-4" />
            <span>Run Simulation</span>
          </button>
        </div>
      </div>

      {/* Teaching Mode Introduction */}
      <WhenTeaching>
        <TeachingCallout category="categorical" title="Town Architecture">
          <p className="mb-2">
            <strong>Agent Town</strong> is built on three categorical layers:
          </p>
          <ul className="list-disc list-inside space-y-1 text-sm">
            <li><strong>Polynomial Agents</strong>: Each citizen follows a 5-phase state machine (Idle → Socializing → Working → Reflecting → Resting)</li>
            <li><strong>Operad Grammar</strong>: TOWN_OPERAD defines valid operations (greet, gossip, trade, coalition_form)</li>
            <li><strong>Sheaf Coherence</strong>: Individual citizen views glue into consistent town state</li>
          </ul>
          <p className="mt-2 text-xs text-gray-400">Toggle teaching mode OFF for a cleaner interface.</p>
        </TeachingCallout>
      </WhenTeaching>

      {/* Stats Grid */}
      <div className={`grid ${isCompact ? 'grid-cols-2 gap-3' : 'grid-cols-2 lg:grid-cols-4 gap-4'}`}>
        <StatCard
          icon={<Users className="w-5 h-5" />}
          label="Total Citizens"
          value={manifestData?.total_citizens ?? 0}
          subtext={`${manifestData?.active_citizens ?? 0} active`}
          onClick={() => navigate('/town/citizens')}
        />
        <StatCard
          icon={<MessageCircle className="w-5 h-5" />}
          label="Conversations"
          value={manifestData?.total_conversations ?? 0}
          subtext={`${manifestData?.active_conversations ?? 0} active`}
        />
        <StatCard
          icon={<Network className="w-5 h-5" />}
          label="Coalitions"
          value={coalitionManifestData?.total_coalitions ?? 0}
          subtext={`${coalitionManifestData?.bridge_citizens ?? 0} bridges`}
          onClick={() => navigate('/town/coalitions')}
        />
        <StatCard
          icon={<Activity className="w-5 h-5" />}
          label="Relationships"
          value={manifestData?.total_relationships ?? 0}
          subtext={`Avg strength: ${((coalitionManifestData?.avg_strength ?? 0) * 100).toFixed(0)}%`}
        />
      </div>

      {/* Content Grid */}
      <div className={`grid ${isCompact ? 'gap-6' : 'lg:grid-cols-2 gap-8'}`}>
        {/* Citizens Section */}
        <div>
          <SectionHeader
            icon={<Users className="w-5 h-5" />}
            title="Citizens"
            action={
              <button
                onClick={() => navigate('/town/citizens')}
                className="text-sm text-violet-400 hover:text-violet-300 flex items-center gap-1"
              >
                View all <ChevronRight className="w-4 h-4" />
              </button>
            }
          />
          <div className="space-y-2">
            {citizensData.length > 0 ? (
              citizensData.slice(0, 5).map((citizen) => (
                <CitizenCard
                  key={citizen.id}
                  name={citizen.name}
                  archetype={citizen.archetype}
                  isActive={citizen.is_active}
                  interactionCount={citizen.interaction_count}
                  onClick={() => navigate(`/town/citizens/${citizen.id}`)}
                />
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <UserPlus className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No citizens yet</p>
                <p className="text-sm">Run a simulation to create citizens</p>
              </div>
            )}
          </div>
        </div>

        {/* Coalitions Section */}
        <div>
          <SectionHeader
            icon={<Network className="w-5 h-5" />}
            title="Coalitions"
            action={
              <button
                onClick={() => navigate('/town/coalitions')}
                className="text-sm text-violet-400 hover:text-violet-300 flex items-center gap-1"
              >
                View all <ChevronRight className="w-4 h-4" />
              </button>
            }
          />
          <div className="space-y-2">
            {coalitionsData.length > 0 ? (
              coalitionsData.slice(0, 4).map((coalition) => (
                <CoalitionCard
                  key={coalition.id}
                  name={coalition.name}
                  memberCount={coalition.member_count}
                  strength={coalition.strength}
                  purpose={coalition.purpose}
                  onClick={() => navigate(`/town/coalitions/${coalition.id}`)}
                />
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Network className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No coalitions detected</p>
                <p className="text-sm">Coalitions form from citizen interactions</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Storage Info */}
      <div className="pt-4 border-t border-violet-500/20">
        <p className="text-xs text-gray-500">
          Storage: <span className="text-gray-400">{manifestData?.storage_backend ?? 'unknown'}</span>
        </p>
      </div>
    </div>
  );
}

export default TownOverview;
