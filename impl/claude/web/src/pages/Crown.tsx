/**
 * Crown Landing Page - The Hero Path
 *
 * Wave 4: The unified entry point for kgents Crown Jewels.
 *
 * Guides users through the Hero Path:
 * 1. "Scan your codebase" -> /gestalt
 * 2. "See what we learned" -> /brain
 * 3. "Start improving it" -> /gardener
 *
 * The synergy toasts make cross-jewel connections visible.
 * Time to "wow moment": < 5 minutes.
 *
 * @see plans/crown-jewels-enlightened.md Wave 4
 */

import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Crown as CrownIcon, Check } from 'lucide-react';
import { brainApi, gestaltApi, gardenerApi } from '../api/client';
import { Breathe } from '../components/joy';
import { JEWEL_COLORS, JEWEL_ICONS, type JewelName } from '../constants/jewels';

interface CrownStatus {
  gestalt: { scanned: boolean; health?: string };
  brain: { crystals: number };
  gardener: { season?: string };
  loading: boolean;
  error?: string;
}

/**
 * Hero path step configuration.
 * Uses JEWEL_ICONS (Lucide) instead of emojis per visual-system.md.
 */
const HERO_STEPS = [
  {
    step: 1,
    jewel: 'gestalt' as JewelName,
    title: 'Scan Your Codebase',
    subtitle: 'Understand the shape of your code',
    description:
      "Gestalt analyzes your codebase's architecture, dependencies, and health in seconds.",
    href: '/gestalt',
    action: 'Start Scan',
    icon: JEWEL_ICONS.gestalt,
    color: JEWEL_COLORS.gestalt.primary,
    path: 'world.codebase.*',
  },
  {
    step: 2,
    jewel: 'brain' as JewelName,
    title: 'See What We Learned',
    subtitle: 'Knowledge crystallizes automatically',
    description:
      'Brain captures insights from your scan. Every analysis becomes a searchable memory crystal.',
    href: '/brain',
    action: 'View Crystals',
    icon: JEWEL_ICONS.brain,
    color: JEWEL_COLORS.brain.primary,
    path: 'self.memory.*',
  },
  {
    step: 3,
    jewel: 'gardener' as JewelName,
    title: 'Start Improving It',
    subtitle: 'Cultivate better code',
    description:
      'The Gardener helps you plan, act, and reflect on improvements with context from Brain and Gestalt.',
    href: '/gardener',
    action: 'Open Gardener',
    icon: JEWEL_ICONS.gardener,
    color: JEWEL_COLORS.gardener.primary,
    path: 'concept.gardener.*',
  },
];

/**
 * Arrow connector between steps.
 */
function StepArrow() {
  return (
    <div className="hidden lg:flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.3 }}
        className="text-gray-600 text-2xl"
      >
        →
      </motion.div>
    </div>
  );
}

/**
 * Hero step card component.
 */
function HeroStepCard({
  step,
  delay = 0,
  completed = false,
  current = false,
}: {
  step: (typeof HERO_STEPS)[0];
  delay?: number;
  completed?: boolean;
  current?: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`
        relative flex-1 rounded-2xl p-6 border transition-all
        ${current ? 'border-2 shadow-lg' : 'border-gray-700'}
        bg-gray-800/50 hover:bg-gray-800/80
      `}
      style={{
        borderColor: current ? step.color : undefined,
      }}
    >
      {/* Step number badge */}
      <div
        className="absolute -top-3 left-4 px-3 py-1 rounded-full text-xs font-bold"
        style={{ backgroundColor: step.color }}
      >
        Step {step.step}
      </div>

      {/* Completed checkmark */}
      {completed && (
        <div className="absolute -top-3 right-4 w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-white">
          <Check className="w-4 h-4" />
        </div>
      )}

      {/* Jewel Icon */}
      <div className="mb-4 mt-2">
        <step.icon className="w-10 h-10" style={{ color: step.color }} />
      </div>

      {/* Title */}
      <h3 className="text-lg font-bold text-white mb-1">{step.title}</h3>

      {/* Subtitle */}
      <p className="text-sm text-gray-400 mb-3">{step.subtitle}</p>

      {/* Description */}
      <p className="text-sm text-gray-500 mb-4">{step.description}</p>

      {/* AGENTESE path */}
      <code className="text-xs text-gray-600 font-mono block mb-4">{step.path}</code>

      {/* Action button */}
      <Link
        to={step.href}
        className="block w-full py-2 px-4 rounded-lg text-center text-sm font-medium transition-all hover:opacity-90"
        style={{ backgroundColor: step.color }}
      >
        {step.action}
      </Link>
    </motion.div>
  );
}

/**
 * Extension jewels preview.
 * Uses JEWEL_ICONS (Lucide) instead of emojis per visual-system.md.
 */
function ExtensionJewels() {
  const extensions = [
    {
      name: 'Atelier',
      jewel: 'atelier' as JewelName,
      icon: JEWEL_ICONS.atelier,
      color: JEWEL_COLORS.atelier.primary,
      href: '/atelier',
      description: 'Creative collaboration',
    },
    {
      name: 'Coalition',
      jewel: 'coalition' as JewelName,
      icon: JEWEL_ICONS.coalition,
      color: JEWEL_COLORS.coalition.primary,
      href: '/town',
      description: 'Agent orchestration',
    },
    {
      name: 'Park',
      jewel: 'park' as JewelName,
      icon: JEWEL_ICONS.park,
      color: JEWEL_COLORS.park.primary,
      href: '/park',
      description: 'Crisis practice',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.8 }}
      className="mt-12 pt-8 border-t border-gray-800"
    >
      <h2 className="text-sm uppercase tracking-wide text-gray-500 mb-4 text-center">
        Extension Jewels
      </h2>
      <div className="flex justify-center gap-4 flex-wrap">
        {extensions.map((ext) => (
          <Link
            key={ext.name}
            to={ext.href}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors border border-gray-700"
          >
            <ext.icon className="w-5 h-5" style={{ color: ext.color }} />
            <div>
              <span className="text-sm font-medium text-gray-300">{ext.name}</span>
              <span className="text-xs text-gray-500 block">{ext.description}</span>
            </div>
          </Link>
        ))}
      </div>
    </motion.div>
  );
}

/**
 * Demo mode banner for when backend is unavailable.
 */
function DemoModeBanner() {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8 p-4 rounded-lg bg-amber-900/20 border border-amber-700/50 text-center"
    >
      <p className="text-amber-300 text-sm">
        <span className="font-bold">Demo Mode</span> - Backend not connected. Start the API server
        to enable full functionality:
      </p>
      <code className="text-xs text-amber-400/70 mt-2 block">
        cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
      </code>
    </motion.div>
  );
}

/**
 * Crown Landing Page.
 */
export default function Crown() {
  const navigate = useNavigate();
  const [status, setStatus] = useState<CrownStatus>({
    gestalt: { scanned: false },
    brain: { crystals: 0 },
    gardener: {},
    loading: true,
  });
  const [demoMode, setDemoMode] = useState(false);

  // Fetch status from all jewels
  // All APIs now return unwrapped data (AGENTESE pattern)
  const fetchStatus = useCallback(async () => {
    try {
      const [gestaltRes, brainRes, gardenRes] = await Promise.allSettled([
        gestaltApi.getHealth(),
        brainApi.getStatus(),
        gardenerApi.getGarden(),
      ]);

      const newStatus: CrownStatus = {
        gestalt: { scanned: false },
        brain: { crystals: 0 },
        gardener: {},
        loading: false,
      };

      // Check Gestalt status (now returns unwrapped data)
      if (gestaltRes.status === 'fulfilled' && gestaltRes.value) {
        newStatus.gestalt = {
          scanned: true,
          health: gestaltRes.value.overall_grade,
        };
      }

      // Check Brain status (already unwrapped)
      if (brainRes.status === 'fulfilled' && brainRes.value) {
        newStatus.brain = {
          crystals: brainRes.value.concept_count,
        };
      }

      // Check Garden status (already unwrapped)
      if (gardenRes.status === 'fulfilled' && gardenRes.value) {
        newStatus.gardener = {
          season: gardenRes.value.season,
        };
      }

      // Determine if we're in demo mode (all APIs failed)
      const allFailed =
        gestaltRes.status === 'rejected' &&
        brainRes.status === 'rejected' &&
        gardenRes.status === 'rejected';

      setDemoMode(allFailed);
      setStatus(newStatus);
    } catch (error) {
      console.debug('Crown: API not available', error);
      setDemoMode(true);
      setStatus((s) => ({ ...s, loading: false }));
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Determine which step is current
  const currentStep = status.gestalt.scanned
    ? status.brain.crystals > 0
      ? 3
      : 2
    : 1;

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <Breathe intensity={0.3} speed="slow">
            <h1 className="text-4xl font-bold mb-2 flex items-center justify-center gap-3">
              <CrownIcon className="w-8 h-8 text-amber-400" />
              kgents Crown
            </h1>
          </Breathe>
          <p className="text-gray-400 text-lg">
            7 jewels. 1 unified experience. Start here.
          </p>
        </motion.header>

        {/* Demo mode banner */}
        {demoMode && <DemoModeBanner />}

        {/* Hero Path Introduction */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-8"
        >
          <h2 className="text-xl font-semibold text-gray-300 mb-2">The Hero Path</h2>
          <p className="text-gray-500 max-w-2xl mx-auto">
            Experience the power of kgents in 3 steps. Each jewel builds on the last, creating
            synergies that make the whole greater than the sum of parts.
          </p>
        </motion.div>

        {/* Hero Steps */}
        <div className="flex flex-col lg:flex-row gap-6 lg:gap-0 items-stretch">
          <HeroStepCard
            step={HERO_STEPS[0]}
            delay={0.3}
            completed={status.gestalt.scanned}
            current={currentStep === 1}
          />
          <StepArrow />
          <HeroStepCard
            step={HERO_STEPS[1]}
            delay={0.4}
            completed={status.brain.crystals > 0}
            current={currentStep === 2}
          />
          <StepArrow />
          <HeroStepCard
            step={HERO_STEPS[2]}
            delay={0.5}
            completed={!!status.gardener.season}
            current={currentStep === 3}
          />
        </div>

        {/* Status Summary */}
        {!demoMode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-8 p-4 rounded-lg bg-gray-800/30 flex justify-center gap-8 text-sm"
          >
            {status.gestalt.scanned && status.gestalt.health && (
              <div className="flex items-center gap-2">
                <span style={{ color: JEWEL_COLORS.gestalt.primary }}>●</span>
                <span className="text-gray-400">Health Grade:</span>
                <span className="font-bold text-white">{status.gestalt.health}</span>
              </div>
            )}
            {status.brain.crystals > 0 && (
              <div className="flex items-center gap-2">
                <span style={{ color: JEWEL_COLORS.brain.primary }}>●</span>
                <span className="text-gray-400">Crystals:</span>
                <span className="font-bold text-white">{status.brain.crystals}</span>
              </div>
            )}
            {status.gardener.season && (
              <div className="flex items-center gap-2">
                <span style={{ color: JEWEL_COLORS.gardener.primary }}>●</span>
                <span className="text-gray-400">Season:</span>
                <span className="font-bold text-white">{status.gardener.season}</span>
              </div>
            )}
          </motion.div>
        )}

        {/* Quick Start CTA for Demo Mode */}
        {demoMode && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-8 text-center"
          >
            <button
              onClick={() => navigate('/gestalt')}
              className="px-8 py-3 rounded-lg font-medium text-white transition-colors"
              style={{ backgroundColor: JEWEL_COLORS.gestalt.primary }}
            >
              Explore Demo Mode
            </button>
            <p className="text-gray-500 text-xs mt-2">
              Some features available without backend
            </p>
          </motion.div>
        )}

        {/* Extension Jewels */}
        <ExtensionJewels />

        {/* AGENTESE Teaser */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.0 }}
          className="mt-12 text-center"
        >
          <p className="text-gray-600 text-sm">
            All jewels speak{' '}
            <code className="text-cyan-400 bg-gray-800 px-2 py-1 rounded">AGENTESE</code> - a
            verb-first protocol for agent-world interaction.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
