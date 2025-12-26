/**
 * Joy Animation Components Stories
 *
 * STARK BIOME: "Stillness, then life."
 * Demonstrates the "Everything Breathes" philosophy through animation primitives.
 *
 * Motion Laws:
 * - M-01: Asymmetric breathing uses 4-7-8 timing (not symmetric)
 * - M-02: Default is still, animation is earned
 * - M-04: Respects prefers-reduced-motion
 * - M-05: Every animation has semantic reason
 */

import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { Breathe } from './Breathe';
import { Pop, PopOnMount } from './Pop';
import { Shake } from './Shake';
import { Shimmer, ShimmerBlock, ShimmerText } from './Shimmer';
import { OrganicToast } from './OrganicToast';
import { PersonalityLoading } from './PersonalityLoading';
import { EmpathyError, InlineError } from './EmpathyError';
import { PageTransition } from './PageTransition';
import { LIVING_EARTH } from '@/constants';

// =============================================================================
// Meta
// =============================================================================

const meta: Meta = {
  title: 'Joy/Animation Primitives',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: `
## Motion Laws

| Law | Principle | Implementation |
|-----|-----------|----------------|
| **M-01** | Asymmetric 4-7-8 breathing | 4s inhale, 7s hold, 8s exhale (19s total) |
| **M-02** | Stillness is default | Animation is earned through interaction/state |
| **M-04** | Respect accessibility | Honors \`prefers-reduced-motion\` |
| **M-05** | Semantic animation | Every animation has a justified reason |

> "The frame is humble. The content glows." Animation is earned, not given.
        `,
      },
    },
  },
};

export default meta;

// =============================================================================
// Breathe Stories
// =============================================================================

export const BreatheDefault: StoryObj = {
  name: 'Breathe - 4-7-8 Cycle',
  render: () => (
    <div className="flex items-center gap-8">
      <Breathe>
        <div
          className="w-24 h-24 rounded-lg flex items-center justify-center"
          style={{ background: LIVING_EARTH.sage, color: LIVING_EARTH.lantern }}
        >
          Breathing
        </div>
      </Breathe>
      <div className="text-sm text-gray-400 max-w-xs">
        <p className="mb-2 font-medium">M-01: 4-7-8 Pattern</p>
        <p>4s inhale, 7s hold, 8s exhale = 19s cycle. Calming, not mechanical.</p>
      </div>
    </div>
  ),
};

export const BreatheVariants: StoryObj = {
  name: 'Breathe - Intensity & Speed',
  render: () => (
    <div className="flex flex-col gap-6">
      <div className="flex gap-6 items-end">
        <div className="text-center">
          <Breathe intensity={0.15}>
            <div className="w-16 h-16 rounded-full" style={{ background: LIVING_EARTH.moss }} />
          </Breathe>
          <p className="mt-2 text-xs text-gray-500">Subtle (50%)</p>
        </div>
        <div className="text-center">
          <Breathe intensity={0.3}>
            <div className="w-20 h-20 rounded-full" style={{ background: LIVING_EARTH.sage }} />
          </Breathe>
          <p className="mt-2 text-xs text-gray-500">Normal</p>
        </div>
        <div className="text-center">
          <Breathe intensity={0.45}>
            <div className="w-24 h-24 rounded-full" style={{ background: LIVING_EARTH.amber }} />
          </Breathe>
          <p className="mt-2 text-xs text-gray-500">Intense (150%)</p>
        </div>
      </div>
      <div className="flex gap-8 items-center">
        <div className="text-center">
          <Breathe speed="slow">
            <div className="w-12 h-12 rounded-lg" style={{ background: LIVING_EARTH.clay }} />
          </Breathe>
          <p className="mt-2 text-xs text-gray-500">Slow (25.3s)</p>
        </div>
        <div className="text-center">
          <Breathe speed="normal">
            <div className="w-12 h-12 rounded-lg" style={{ background: LIVING_EARTH.sand }} />
          </Breathe>
          <p className="mt-2 text-xs text-gray-500">Normal (19s)</p>
        </div>
        <div className="text-center">
          <Breathe speed="fast">
            <div className="w-12 h-12 rounded-lg" style={{ background: LIVING_EARTH.amber }} />
          </Breathe>
          <p className="mt-2 text-xs text-gray-500">Fast (14.25s)</p>
        </div>
      </div>
    </div>
  ),
};

export const BreatheStaggered: StoryObj = {
  name: 'Breathe - Staggered (Golden Ratio)',
  render: () => (
    <div className="flex gap-2">
      {[0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875].map((offset, i) => (
        <Breathe key={i} intensity={0.3}>
          <div
            className="w-8 h-8 rounded-full"
            style={{ background: LIVING_EARTH.sage, animationDelay: `${offset * 19}s` }}
          />
        </Breathe>
      ))}
    </div>
  ),
};

// =============================================================================
// Pop Stories
// =============================================================================

export const PopDemo: StoryObj = {
  name: 'Pop - Selection Feedback',
  render: () => {
    const [trigger, setTrigger] = useState(false);
    const [key, setKey] = useState(0);
    return (
      <div className="flex gap-8 items-start">
        <div className="flex flex-col gap-2">
          <Pop trigger={trigger}>
            <button
              onClick={() => { setTrigger(true); setTimeout(() => setTrigger(false), 300); }}
              className="px-4 py-2 rounded-lg text-white"
              style={{ background: LIVING_EARTH.sage }}
            >
              Click to Pop
            </button>
          </Pop>
          <p className="text-xs text-gray-500">Triggered</p>
        </div>
        <div className="flex flex-col gap-2">
          <button onClick={() => setKey((k) => k + 1)} className="px-4 py-2 rounded bg-gray-700 text-gray-200">
            Remount
          </button>
          <PopOnMount key={key} scale={1.08} duration={400}>
            <div className="p-3 rounded-lg" style={{ background: LIVING_EARTH.bark }}>
              <p style={{ color: LIVING_EARTH.lantern }} className="text-sm">Pop on mount</p>
            </div>
          </PopOnMount>
        </div>
      </div>
    );
  },
};

// =============================================================================
// Shake Stories
// =============================================================================

export const ShakeDemo: StoryObj = {
  name: 'Shake - Error Feedback',
  render: () => {
    const [shakes, setShakes] = useState({ gentle: false, normal: false, urgent: false });
    return (
      <div className="flex gap-6">
        {(['gentle', 'normal', 'urgent'] as const).map((intensity) => (
          <Shake key={intensity} trigger={shakes[intensity]} intensity={intensity}>
            <button
              onClick={() => { setShakes((s) => ({ ...s, [intensity]: true })); setTimeout(() => setShakes((s) => ({ ...s, [intensity]: false })), 500); }}
              className="px-4 py-2 rounded-lg bg-gray-700 text-gray-200"
            >
              {intensity}
            </button>
          </Shake>
        ))}
      </div>
    );
  },
};

// =============================================================================
// Shimmer Stories
// =============================================================================

export const ShimmerDemo: StoryObj = {
  name: 'Shimmer - Loading States',
  render: () => (
    <div className="flex gap-8">
      <div className="flex flex-col gap-3 w-48">
        <Shimmer><div className="h-4 bg-gray-700 rounded" /></Shimmer>
        <Shimmer><div className="h-4 bg-gray-700 rounded w-3/4" /></Shimmer>
        <Shimmer><div className="h-4 bg-gray-700 rounded w-1/2" /></Shimmer>
      </div>
      <div className="flex gap-4">
        <ShimmerBlock width="w-24" height="h-24" rounded="lg" />
        <ShimmerBlock width="w-10" height="h-10" rounded="full" />
        <div className="w-32"><ShimmerText lines={3} /></div>
      </div>
    </div>
  ),
};

// =============================================================================
// OrganicToast Stories
// =============================================================================

export const ToastDemo: StoryObj = {
  name: 'OrganicToast - Types',
  render: () => {
    const [visible, setVisible] = useState<Record<string, boolean>>({});
    const types = ['success', 'info', 'warning', 'error', 'token'] as const;
    return (
      <div className="flex flex-col gap-4">
        <div className="flex gap-2">
          {types.map((type) => (
            <button key={type} onClick={() => setVisible((v) => ({ ...v, [type]: true }))}
              className="px-3 py-1 rounded bg-gray-700 text-gray-200 text-sm capitalize">{type}</button>
          ))}
        </div>
        {types.map((type) => (
          <OrganicToast key={type} id={type} type={type} title={`${type.charAt(0).toUpperCase() + type.slice(1)} Toast`}
            description="Click to dismiss." isVisible={visible[type] ?? false}
            onDismiss={(id) => setVisible((v) => ({ ...v, [id]: false }))} position="top-right" />
        ))}
      </div>
    );
  },
};

// =============================================================================
// PersonalityLoading Stories
// =============================================================================

export const PersonalityLoadingDemo: StoryObj = {
  name: 'PersonalityLoading - Jewels',
  render: () => (
    <div className="grid grid-cols-2 gap-8">
      <PersonalityLoading jewel="brain" size="md" />
      <PersonalityLoading jewel="gardener" size="md" />
      <PersonalityLoading jewel="forge" size="md" />
      <PersonalityLoading jewel="domain" size="md" />
    </div>
  ),
};

// =============================================================================
// EmpathyError Stories
// =============================================================================

export const ErrorDemo: StoryObj = {
  name: 'EmpathyError - Types',
  render: () => {
    const [shake, setShake] = useState(false);
    return (
      <div className="flex flex-col gap-6">
        <div className="grid grid-cols-2 gap-4">
          <EmpathyError type="network" size="sm" onAction={() => {}} />
          <EmpathyError type="notfound" size="sm" onAction={() => {}} />
        </div>
        <div className="flex items-center gap-4">
          <button onClick={() => { setShake(true); setTimeout(() => setShake(false), 500); }}
            className="px-4 py-2 rounded bg-gray-700 text-gray-200">Trigger Shake</button>
          <InlineError message="This field is required" shake={shake} />
        </div>
      </div>
    );
  },
};

// =============================================================================
// PageTransition Stories
// =============================================================================

export const PageTransitionDemo: StoryObj = {
  name: 'PageTransition - Variants',
  render: () => {
    const [key, setKey] = useState(0);
    const [variant, setVariant] = useState<'fade' | 'slide' | 'scale'>('fade');
    return (
      <div className="flex flex-col gap-4">
        <div className="flex gap-2">
          {(['fade', 'slide', 'scale'] as const).map((v) => (
            <button key={v} onClick={() => { setVariant(v); setKey((k) => k + 1); }}
              className={`px-3 py-1 rounded text-sm ${variant === v ? 'bg-cyan-600 text-white' : 'bg-gray-700 text-gray-200'}`}>
              {v}
            </button>
          ))}
        </div>
        <PageTransition key={key} variant={variant}>
          <div className="p-6 rounded-lg" style={{ background: LIVING_EARTH.bark }}>
            <p style={{ color: LIVING_EARTH.lantern }}>{variant} transition</p>
          </div>
        </PageTransition>
      </div>
    );
  },
};

// =============================================================================
// Reduced Motion + Philosophy
// =============================================================================

export const ReducedMotionDemo: StoryObj = {
  name: 'M-04: Reduced Motion',
  render: () => (
    <div className="p-6 rounded-lg" style={{ background: LIVING_EARTH.bark }}>
      <h3 className="text-lg font-medium mb-4" style={{ color: LIVING_EARTH.lantern }}>
        prefers-reduced-motion Support
      </h3>
      <div className="flex gap-6 items-start">
        <Breathe>
          <div className="w-16 h-16 rounded-lg" style={{ background: LIVING_EARTH.sage }} />
        </Breathe>
        <div className="text-sm" style={{ color: LIVING_EARTH.sand }}>
          <p className="mb-2">When reduced motion is enabled:</p>
          <ul className="list-disc list-inside space-y-1 text-gray-400">
            <li>Breathing stops</li>
            <li>Pop/Shake become instant</li>
            <li>Shimmer becomes static</li>
          </ul>
        </div>
      </div>
    </div>
  ),
};

export const PhilosophyOverview: StoryObj = {
  name: 'Motion Philosophy',
  render: () => (
    <div className="p-8 rounded-lg max-w-2xl" style={{ background: '#141418' }}>
      <h2 className="text-xl font-medium mb-6" style={{ color: LIVING_EARTH.lantern }}>
        The Motion Laws
      </h2>
      <div className="space-y-4" style={{ color: LIVING_EARTH.sand }}>
        {[
          { code: 'M-01', title: 'Asymmetric 4-7-8 Breathing', desc: '4s inhale, 7s hold, 8s exhale. Calming rhythm.' },
          { code: 'M-02', title: 'Stillness is Default', desc: 'Animation is earned through interaction or state.' },
          { code: 'M-04', title: 'Respect Accessibility', desc: 'Honor prefers-reduced-motion. No exceptions.' },
          { code: 'M-05', title: 'Semantic Animation', desc: 'Every animation has a reason: life, selection, error, loading.' },
        ].map(({ code, title, desc }) => (
          <div key={code} className="flex gap-4">
            <span className="text-amber-500 font-mono">{code}</span>
            <div>
              <p className="font-medium text-white">{title}</p>
              <p className="text-sm text-gray-400">{desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  ),
  parameters: { layout: 'centered' },
};
