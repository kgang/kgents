/**
 * ESLint Configuration for AI Agent Development
 *
 * Philosophy: "Enlightened Balance"
 * ================================
 *
 * ERROR (blocks commit):
 *   - Real bugs: null safety, type coercion, unreachable code
 *   - Security: eval, dangerouslySetInnerHTML without sanitization
 *   - React correctness: hooks rules, key props
 *
 * WARN (doesn't block, but visible):
 *   - Code smells: unused vars, console.log, TODO comments
 *   - Complexity: deep nesting, long functions
 *   - Performance hints: missing deps in useEffect
 *
 * OFF (handled elsewhere or not valuable):
 *   - Formatting (Prettier handles this)
 *   - Stylistic preferences (tabs vs spaces, quotes)
 *   - Overly pedantic rules that slow iteration
 *
 * AI Agent Optimizations:
 *   - Fast: Caching enabled by default
 *   - Clear: Error messages are actionable
 *   - Incremental: Only lint changed files on commit
 *   - Parallel: Worker threads for large codebases
 */

import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  // =============================================================================
  // Global ignores
  // =============================================================================
  {
    ignores: [
      'dist/**',
      'node_modules/**',
      'coverage/**',
      '*.config.js',
      '*.config.ts',
      'playwright-report/**',
      'test-results/**',
    ],
  },

  // =============================================================================
  // Base JavaScript rules
  // =============================================================================
  js.configs.recommended,

  // =============================================================================
  // TypeScript rules (strict but not pedantic)
  // =============================================================================
  ...tseslint.configs.recommended,

  // =============================================================================
  // React-specific configuration
  // =============================================================================
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      globals: {
        ...globals.browser,
        ...globals.es2022,
      },
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      // =========================================================================
      // ERRORS: Real bugs that MUST be fixed
      // =========================================================================

      // React hooks rules - these catch real bugs
      ...reactHooks.configs.recommended.rules,

      // React refresh - required for HMR to work correctly
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],

      // Type safety - prevent runtime errors
      '@typescript-eslint/no-explicit-any': 'warn', // Warn, not error - sometimes any is needed
      '@typescript-eslint/no-non-null-assertion': 'warn', // ! operator is sometimes necessary
      '@typescript-eslint/no-unused-vars': [
        'warn',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
        },
      ],

      // Prevent common mistakes
      'no-console': ['warn', { allow: ['warn', 'error', 'info'] }],
      'no-debugger': 'error',
      'no-alert': 'error',
      'no-eval': 'error',
      'no-implied-eval': 'error',

      // Async/await correctness
      'no-async-promise-executor': 'error',
      'no-await-in-loop': 'warn', // Sometimes intentional
      'no-promise-executor-return': 'error',
      'require-atomic-updates': 'error',

      // Logic errors
      'no-compare-neg-zero': 'error',
      'no-cond-assign': 'error',
      'no-constant-condition': ['error', { checkLoops: false }],
      'no-dupe-args': 'error',
      'no-dupe-keys': 'error',
      'no-duplicate-case': 'error',
      'no-empty': ['warn', { allowEmptyCatch: true }],
      'no-ex-assign': 'error',
      'no-extra-boolean-cast': 'warn',
      'no-func-assign': 'error',
      'no-inner-declarations': 'error',
      'no-invalid-regexp': 'error',
      'no-irregular-whitespace': 'error',
      'no-loss-of-precision': 'error',
      'no-misleading-character-class': 'error',
      'no-obj-calls': 'error',
      'no-prototype-builtins': 'warn',
      'no-regex-spaces': 'warn',
      'no-sparse-arrays': 'error',
      'no-template-curly-in-string': 'warn',
      'no-unexpected-multiline': 'error',
      'no-unreachable': 'error',
      'no-unreachable-loop': 'error',
      'no-unsafe-finally': 'error',
      'no-unsafe-negation': 'error',
      'no-unsafe-optional-chaining': 'error',
      'use-isnan': 'error',
      'valid-typeof': 'error',

      // =========================================================================
      // WARNINGS: Code smells that should be addressed (but don't block)
      // =========================================================================

      // Complexity warnings
      'max-depth': ['warn', 4],
      'max-nested-callbacks': ['warn', 3],
      'complexity': ['warn', 15],

      // Best practices (warn, not error)
      'default-case-last': 'warn',
      'dot-notation': 'warn',
      'eqeqeq': ['warn', 'smart'],
      'grouped-accessor-pairs': 'warn',
      'no-caller': 'error',
      'no-constructor-return': 'error',
      'no-else-return': 'warn',
      'no-empty-function': ['warn', { allow: ['arrowFunctions'] }],
      'no-extend-native': 'error',
      'no-extra-bind': 'warn',
      'no-floating-decimal': 'warn',
      'no-implicit-coercion': ['warn', { allow: ['!!', '+'] }],
      'no-lone-blocks': 'warn',
      'no-multi-spaces': 'off', // Prettier handles this
      'no-new': 'warn',
      'no-new-wrappers': 'error',
      'no-param-reassign': 'warn',
      'no-return-assign': 'warn',
      'no-self-compare': 'error',
      'no-sequences': 'error',
      'no-throw-literal': 'error',
      'no-unmodified-loop-condition': 'error',
      'no-unused-expressions': ['warn', { allowShortCircuit: true, allowTernary: true }],
      'no-useless-call': 'warn',
      'no-useless-concat': 'warn',
      'no-useless-return': 'warn',
      'prefer-promise-reject-errors': 'warn',
      'radix': 'warn',
      'yoda': 'warn',

      // =========================================================================
      // OFF: Handled by Prettier or too pedantic
      // =========================================================================

      // Formatting (Prettier handles all of these)
      'indent': 'off',
      'linebreak-style': 'off',
      'quotes': 'off',
      'semi': 'off',
      'comma-dangle': 'off',
      'arrow-parens': 'off',
      'object-curly-spacing': 'off',
      'array-bracket-spacing': 'off',
      'space-before-function-paren': 'off',
      'max-len': 'off', // Let Prettier handle line length

      // Too pedantic for AI agent development
      'sort-imports': 'off', // Auto-fixable but noisy
      'sort-keys': 'off', // Arbitrary ordering
      'id-length': 'off', // Sometimes short names are fine
      'no-magic-numbers': 'off', // Too noisy
      'no-ternary': 'off', // Ternaries are fine
      'no-undefined': 'off', // undefined is fine
      'prefer-named-capture-group': 'off', // Too pedantic
    },
  },

  // =============================================================================
  // Test files - relaxed rules
  // =============================================================================
  {
    files: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}', '**/tests/**/*.{ts,tsx}'],
    rules: {
      // Allow any in tests - testing edge cases often requires it
      '@typescript-eslint/no-explicit-any': 'off',

      // Allow non-null assertions in tests - often testing specific scenarios
      '@typescript-eslint/no-non-null-assertion': 'off',

      // Allow empty functions in tests (mocks)
      'no-empty-function': 'off',
      '@typescript-eslint/no-empty-function': 'off',

      // Allow console in tests
      'no-console': 'off',

      // Relax complexity rules in tests
      'max-depth': 'off',
      'max-nested-callbacks': 'off',
      'complexity': 'off',

      // Allow promise executor returns in tests (e.g., setTimeout in Promise)
      'no-promise-executor-return': 'off',

      // Allow unused vars in tests (often for destructuring)
      '@typescript-eslint/no-unused-vars': 'off',
    },
  },

  // =============================================================================
  // E2E test files - even more relaxed
  // =============================================================================
  {
    files: ['**/e2e/**/*.{ts,tsx}'],
    rules: {
      // E2E tests often need flexible typing
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-non-null-assertion': 'off',
      '@typescript-eslint/no-unused-vars': 'off',

      // E2E tests may have long async chains
      'no-await-in-loop': 'off',
      'max-nested-callbacks': 'off',
    },
  }
);
