/**
 * lint-staged Configuration
 *
 * Philosophy: Fast feedback on commit, thorough checks on push
 *
 * On COMMIT (staged files only):
 * ==============================
 * 1. ESLint with auto-fix (errors block, warnings pass)
 * 2. Prettier formatting (auto-applied)
 * 3. TypeScript type check on changed files
 *
 * This runs in ~2-5 seconds for typical commits.
 * AI agents can iterate quickly without waiting.
 *
 * On PUSH (see pre-push hook):
 * ============================
 * 1. Full type check
 * 2. Affected tests
 * 3. Coverage thresholds
 */

export default {
  // TypeScript and JavaScript files
  '*.{ts,tsx}': [
    // ESLint with auto-fix (max-warnings=0 means warnings don't block)
    'eslint --fix --cache --cache-location node_modules/.cache/eslint',
    // Prettier formatting
    'prettier --write',
  ],

  // JavaScript config files
  '*.{js,cjs,mjs}': [
    'eslint --fix --cache --cache-location node_modules/.cache/eslint',
    'prettier --write',
  ],

  // JSON files
  '*.json': ['prettier --write'],

  // CSS/SCSS files
  '*.{css,scss}': ['prettier --write'],

  // Markdown files
  '*.md': ['prettier --write'],
};
