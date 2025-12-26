import type { Preview } from '@storybook/react-vite';
import React from 'react';

// Import STARK BIOME design system
import '../src/styles/globals.css';
import '../src/design/tokens.css';

/**
 * STARK BIOME Storybook Preview Configuration
 *
 * Philosophy: "90% Steel (cool industrial) / 10% Earned Glow (organic accents)"
 *
 * All stories render on the STARK obsidian background by default.
 * Use the backgrounds toolbar to test light mode if needed.
 */
const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    // STARK BIOME dark background
    backgrounds: {
      default: 'stark-obsidian',
      values: [
        {
          name: 'stark-obsidian',
          value: '#0A0A0C', // steel-obsidian
        },
        {
          name: 'stark-carbon',
          value: '#141418', // steel-carbon
        },
        {
          name: 'stark-slate',
          value: '#1C1C22', // steel-slate
        },
        {
          name: 'light',
          value: '#F5F5F5', // for contrast testing
        },
      ],
    },
    // Layout options
    layout: 'centered',
    // Viewport presets
    viewport: {
      viewports: {
        compact: {
          name: 'Compact (Mobile)',
          styles: { width: '375px', height: '667px' },
        },
        comfortable: {
          name: 'Comfortable (Tablet)',
          styles: { width: '768px', height: '1024px' },
        },
        spacious: {
          name: 'Spacious (Desktop)',
          styles: { width: '1440px', height: '900px' },
        },
      },
    },
    // Docs theme
    docs: {
      toc: true,
    },
  },
  // Global decorators
  decorators: [
    (Story) => (
      <div
        style={{
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
          color: '#E5E7EB', // text-primary
        }}
      >
        <Story />
      </div>
    ),
  ],
};

export default preview;
