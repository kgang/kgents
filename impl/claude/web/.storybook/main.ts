import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  stories: [
    // Exclude journey MDX files - they're pure docs, not stories
    '../src/**/!(journeys)/*.mdx',
    '../src/**/*.stories.@(js|jsx|mjs|ts|tsx)',
  ],
  addons: [
    '@storybook/addon-a11y',
    '@storybook/addon-docs',
    '@storybook/addon-onboarding',
  ],
  framework: '@storybook/react-vite',
  docs: {
    autodocs: 'tag',
  },
  staticDirs: ['../public'],
  viteFinal: async (config) => {
    // Ensure CSS is processed correctly
    return config;
  },
  // Chromatic-specific configuration
  // See: https://www.chromatic.com/docs/storybook/
  core: {
    disableTelemetry: true,
  },
};

export default config;
