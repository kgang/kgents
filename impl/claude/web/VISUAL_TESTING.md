# Visual Regression Testing with Chromatic

This document describes the visual regression testing setup for the kgents web frontend using [Chromatic](https://www.chromatic.com/).

## Overview

Chromatic captures screenshots of every Storybook story and compares them against a baseline. When visual changes are detected, reviewers can approve or reject them before merging.

**Philosophy**: Visual regression testing enforces STARK BIOME design system consistency. Every component change is visually verified.

## Setup

### 1. Create a Chromatic Project

1. Go to [chromatic.com](https://www.chromatic.com/) and sign in with GitHub
2. Create a new project linked to the `kgents` repository
3. Copy the project token from the project settings

### 2. Add the Project Token to GitHub Secrets

1. Go to the GitHub repository Settings
2. Navigate to **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `CHROMATIC_PROJECT_TOKEN`
5. Value: Your project token from step 1
6. Click **Add secret**

### 3. Verify the Setup

Run the setup verification script:

```bash
cd impl/claude/web
./scripts/setup-chromatic.sh
```

Or manually verify:

```bash
# Install dependencies
npm install

# Run Chromatic locally (requires token)
CHROMATIC_PROJECT_TOKEN=your-token npm run chromatic
```

## How It Works

### GitHub Actions Workflow

The `.github/workflows/chromatic.yml` workflow runs automatically:

- **On push to main**: Updates the baseline snapshots
- **On PR**: Compares changes against the baseline

### What Gets Captured

Every story in Storybook gets a snapshot. Stories are found in:

```
impl/claude/web/src/**/*.stories.tsx
impl/claude/web/src/**/*.stories.ts
```

### Viewports

Chromatic captures stories at the viewports configured in `.storybook/preview.tsx`:

- **Compact (Mobile)**: 375x667px
- **Comfortable (Tablet)**: 768x1024px
- **Spacious (Desktop)**: 1440x900px

## Reviewing Visual Changes

### In Pull Requests

1. Open the PR on GitHub
2. Find the Chromatic status check
3. Click **Details** to open the Chromatic UI
4. Review each visual change:
   - Green border = accepted
   - Red border = needs review
5. Accept or deny changes
6. Merge when all changes are approved

### Accepting Changes

- **Accept**: Click the checkmark to accept a visual change as intentional
- **Deny**: Click the X to flag a change as unintentional

### Auto-Accept on Main

Changes pushed directly to `main` are auto-accepted as the new baseline. This is intentional:
- PRs must be reviewed before merging
- Once merged, the changes become the new baseline

## Local Development

### Running Chromatic Locally

```bash
# Set the token
export CHROMATIC_PROJECT_TOKEN=your-token

# Run Chromatic
npm run chromatic

# Or for CI-like behavior
npm run chromatic:ci
```

### Skipping Chromatic

To skip Chromatic for a specific commit (e.g., documentation-only changes):

```bash
git commit -m "docs: update readme [skip chromatic]"
```

## Best Practices

### Writing Visual-Testable Stories

1. **Use deterministic data**: Avoid random values, timestamps, or dynamic content
2. **Mock external dependencies**: Network requests, timers, etc.
3. **Set explicit dimensions**: Avoid layout shifts
4. **Use stable animations**: Disable or freeze animations for snapshots

Example:

```tsx
// Good - deterministic
export const Default: Story = {
  args: {
    title: 'Test Title',
    date: new Date('2024-01-01'),
  },
};

// Bad - non-deterministic
export const Default: Story = {
  args: {
    title: 'Test Title',
    date: new Date(), // Changes every run!
  },
};
```

### Handling Animations

For components with animations, use Chromatic's delay parameter:

```tsx
export const Animated: Story = {
  parameters: {
    chromatic: {
      delay: 300, // Wait for animation to complete
    },
  },
};
```

Or disable animations entirely:

```tsx
export const Animated: Story = {
  parameters: {
    chromatic: {
      disableSnapshot: false,
      pauseAnimationAtEnd: true,
    },
  },
};
```

### Ignoring Specific Stories

To skip a story from visual testing:

```tsx
export const DevelopmentOnly: Story = {
  parameters: {
    chromatic: { disableSnapshot: true },
  },
};
```

### Testing Responsive Behavior

Capture at multiple viewports:

```tsx
export const Responsive: Story = {
  parameters: {
    chromatic: {
      viewports: [375, 768, 1440],
    },
  },
};
```

## Troubleshooting

### Build Fails

1. Check that Storybook builds locally: `npm run build-storybook`
2. Verify all dependencies are installed: `npm ci`
3. Check for TypeScript errors: `npm run typecheck`

### Flaky Snapshots

Snapshots differ between runs due to:

1. **Animations**: Add `delay` or disable animations
2. **Fonts**: Ensure fonts are loaded before snapshot
3. **Network requests**: Mock all external data
4. **Dates/times**: Use fixed dates

### Missing Stories

Stories not appearing in Chromatic:

1. Verify file extension is `.stories.tsx` or `.stories.ts`
2. Check that story is exported correctly
3. Verify story matches glob pattern in `.storybook/main.ts`

## Configuration Files

| File | Purpose |
|------|---------|
| `.github/workflows/chromatic.yml` | GitHub Actions workflow |
| `.chromatic.config.json` | Chromatic CLI configuration |
| `.storybook/main.ts` | Storybook configuration |
| `.storybook/preview.tsx` | Story decorators and viewports |

## Resources

- [Chromatic Documentation](https://www.chromatic.com/docs/)
- [Storybook Visual Testing Guide](https://storybook.js.org/docs/writing-tests/visual-testing)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
