# Testing & Linting Framework

> An enlightened balance between strictness and enablement for AI agent development.

## Philosophy

### The Enlightened Balance

This framework is designed for **AI agent development** where:
- **Speed matters**: AI agents iterate rapidly, feedback must be sub-second
- **Clarity matters**: Error messages must be actionable, not cryptic
- **Flow matters**: Don't block progress for stylistic preferences

### The Three-Tier Model

```
┌─────────────────────────────────────────────────────────────────┐
│                         ON COMMIT                               │
│                         (~2-5 seconds)                          │
│                                                                 │
│  ✓ ESLint on staged files only (auto-fix applied)              │
│  ✓ Prettier formatting (auto-applied)                          │
│  ✓ Blocks on: errors only                                       │
│  ✓ Passes on: warnings (addressed later)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          ON PUSH                                │
│                         (~20 seconds)                           │
│                                                                 │
│  ✓ Full TypeScript type check                                  │
│  ✓ Unit tests (all tests, fast)                                │
│  ✓ Build verification                                          │
│  ✓ Blocks on: any failure                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                           IN CI                                 │
│                         (~2-5 minutes)                          │
│                                                                 │
│  ✓ E2E tests (Playwright)                                      │
│  ✓ Coverage reports                                            │
│  ✓ Security audits                                             │
│  ✓ Bundle size analysis                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Install dependencies (includes Husky setup)
npm install

# Development workflow
npm run dev              # Start dev server
npm test                 # Watch mode (re-runs on change)
npm run lint             # Check for issues
npm run lint:fix         # Auto-fix issues
npm run format           # Format all files

# Full validation
npm run validate         # Type check + lint + test
npm run validate:fix     # Fix + validate

# Git hooks (automatic)
git commit               # Runs pre-commit hook
git push                 # Runs pre-push hook
```

## ESLint Rules Philosophy

### ERROR (blocks commit)

These catch **real bugs** that will break in production:

| Rule | Why |
|------|-----|
| `no-debugger` | Left-in debuggers break production |
| `no-eval` | Security vulnerability |
| `no-unreachable` | Dead code indicates logic error |
| React hooks rules | Violating these causes subtle bugs |

### WARN (visible, doesn't block)

These are **code smells** to address when convenient:

| Rule | Why |
|------|-----|
| `no-console` | Should use proper logging in prod |
| `no-unused-vars` | Cleanup, but might be WIP |
| `@typescript-eslint/no-explicit-any` | Reduce, but sometimes needed |
| `max-depth: 4` | Deep nesting hurts readability |

### OFF (handled elsewhere)

These are **not valuable** for our workflow:

| Rule | Why |
|------|-----|
| All formatting rules | Prettier handles this |
| `sort-imports` | Noisy, auto-fixable elsewhere |
| `no-magic-numbers` | Too pedantic for rapid iteration |

## Test Organization

```
tests/
├── setup.ts              # Global test setup (mocks, cleanup)
├── unit/                 # Fast, isolated tests (<100ms each)
│   ├── components/       # React component tests
│   ├── hooks/            # Custom hook tests
│   ├── stores/           # Zustand store tests
│   └── lib/              # Utility function tests
└── integration/          # Tests with real dependencies

e2e/                      # Playwright E2E tests
├── fixtures/             # Shared test data & mocks
└── *.spec.ts             # E2E test files
```

## Writing Tests for AI Agents

### Best Practices

```typescript
// ✅ GOOD: Clear, isolated, fast
describe('LODGate', () => {
  it('should render children when LOD is included', () => {
    // Arrange
    const props = { level: 1, children: <div>Content</div> };

    // Act
    render(<LODGate {...props} />);

    // Assert
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
});

// ❌ BAD: Vague, slow, brittle
describe('LODGate', () => {
  it('works', async () => {
    // Don't do this - unclear what's being tested
    render(<LODGate level={1}><div>Content</div></LODGate>);
    await waitFor(() => expect(true).toBe(true));
  });
});
```

### Test Naming

```typescript
// ✅ GOOD: Describes behavior
it('should show upgrade prompt when user lacks credits')
it('should call API with correct parameters when form submits')
it('should handle network error gracefully')

// ❌ BAD: Vague or implementation-focused
it('works')
it('test LODGate')
it('calls setCredits')
```

### Mocking Strategy

```typescript
// ✅ GOOD: Mock at boundaries (APIs, external services)
vi.mock('@/api/client', () => ({
  townApi: {
    getCitizen: vi.fn().mockResolvedValue({ data: mockCitizen }),
  },
}));

// ❌ BAD: Mock internal implementation details
vi.mock('@/lib/utils', () => ({
  cn: vi.fn(), // Don't mock utility functions
}));
```

## Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `npm test` | Watch mode | During development |
| `npm run test:run` | Single run | CI, pre-push |
| `npm run test:ui` | Visual UI | Debugging tests |
| `npm run test:coverage` | Coverage report | Before PR |
| `npm run test:e2e` | E2E tests | Full validation |
| `npm run lint` | Check issues | Quick check |
| `npm run lint:fix` | Auto-fix | Before commit |
| `npm run format` | Format code | Before commit |
| `npm run typecheck` | Type check | Verify types |
| `npm run validate` | Full validation | Before push |

## Bypassing Hooks (Emergency Only)

```bash
# Skip pre-commit (NOT RECOMMENDED)
git commit --no-verify

# Skip pre-push (NOT RECOMMENDED)
git push --no-verify
```

Use these **only** for:
- Reverting broken code quickly
- Emergency fixes
- Documentation-only changes

## Troubleshooting

### "ESLint is slow"

```bash
# Clear cache and retry
rm -rf node_modules/.cache/eslint
npm run lint
```

### "Tests are flaky"

```bash
# Run with retry
npm test -- --retry 3

# Run specific test in isolation
npm test -- tests/unit/components/LODGate.test.tsx
```

### "Husky hooks not running"

```bash
# Reinstall hooks
npm run prepare

# Verify hooks are executable
ls -la .husky/
```

### "Type errors in tests"

Tests have relaxed type rules. If you're seeing errors:

```typescript
// Use type assertion when testing edge cases
const badInput = { invalid: true } as unknown as ValidType;
```

## Configuration Files

| File | Purpose |
|------|---------|
| `eslint.config.js` | ESLint rules (flat config) |
| `.prettierrc` | Prettier formatting options |
| `.prettierignore` | Files to skip formatting |
| `vitest.config.ts` | Test runner configuration |
| `playwright.config.ts` | E2E test configuration |
| `.lintstagedrc.js` | Pre-commit file processing |
| `.husky/pre-commit` | Commit hook script |
| `.husky/pre-push` | Push hook script |
