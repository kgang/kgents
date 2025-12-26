/**
 * STARK BIOME Theme for CodeMirror 6
 *
 * "The frame is humble. The content glows."
 * 90% Steel (cool industrial) / 10% Life (organic accents)
 *
 * Matches the STARK BIOME color system from Membrane.css
 */

import { EditorView } from '@codemirror/view';
import { Extension } from '@codemirror/state';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';

// STARK BIOME colors (from Membrane.css)
const colors = {
  // Steel foundation
  surface0: '#0a0a0c',
  surface1: '#141418',
  surface2: '#1c1c22',
  surface3: '#28282f',

  // Text
  textPrimary: '#e5e7eb',
  textSecondary: '#8a8a94',
  textMuted: '#5a5a64',

  // Accents
  accentPrimary: '#c4a77d',
  accentSecondaryGreen: '#8ba98b',
  accentGold: '#d4b88c',
  accentSuccess: '#4a6b4a',
  accentError: '#a65d4a',

  // Life colors
  lifeSage: '#4a6b4a',
  lifeMint: '#6b8b6b',
  lifeSprout: '#8bab8b',

  // Syntax
  keyword: '#88C0D0',
  string: '#A3BE8C',
  number: '#B48EAD',
  comment: '#5a5a64',
  heading: '#c4a77d',
  link: '#8ba98b',
  emphasis: '#d4b88c',
};

/**
 * The editor theme styling (backgrounds, gutters, selection)
 */
export const starkBiomeTheme = EditorView.theme(
  {
    '&': {
      color: colors.textPrimary,
      backgroundColor: colors.surface1,
      fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
      fontSize: '14px',
    },
    '.cm-content': {
      caretColor: colors.accentPrimary,
      padding: '8px 0',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: colors.accentPrimary,
      borderLeftWidth: '2px',
    },
    '&.cm-focused .cm-cursor': {
      borderLeftColor: colors.accentGold,
    },
    '.cm-selectionBackground, ::selection': {
      backgroundColor: colors.surface3,
    },
    '&.cm-focused .cm-selectionBackground': {
      backgroundColor: `${colors.lifeSage}44`,
    },
    '.cm-activeLine': {
      backgroundColor: `${colors.surface2}80`,
    },
    '.cm-activeLineGutter': {
      backgroundColor: colors.surface2,
    },
    '.cm-gutters': {
      backgroundColor: colors.surface0,
      color: colors.textMuted,
      border: 'none',
      borderRight: `1px solid ${colors.surface3}`,
    },
    '.cm-lineNumbers .cm-gutterElement': {
      padding: '0 8px 0 16px',
    },
    '.cm-foldGutter': {
      color: colors.textMuted,
    },
    '.cm-tooltip': {
      backgroundColor: colors.surface2,
      border: `1px solid ${colors.surface3}`,
      color: colors.textPrimary,
    },
    '.cm-tooltip-autocomplete': {
      '& > ul > li[aria-selected]': {
        backgroundColor: colors.surface3,
        color: colors.textPrimary,
      },
    },
    '.cm-searchMatch': {
      backgroundColor: `${colors.accentGold}33`,
      outline: `1px solid ${colors.accentGold}66`,
    },
    '.cm-searchMatch.cm-searchMatch-selected': {
      backgroundColor: `${colors.accentGold}55`,
    },
    '.cm-matchingBracket, .cm-nonmatchingBracket': {
      backgroundColor: `${colors.lifeSage}44`,
      outline: `1px solid ${colors.lifeSage}`,
    },
    '.cm-panels': {
      backgroundColor: colors.surface0,
      color: colors.textPrimary,
    },
    '.cm-panels-top': {
      borderBottom: `1px solid ${colors.surface3}`,
    },
    '.cm-panels-bottom': {
      borderTop: `1px solid ${colors.surface3}`,
    },
    '.cm-textfield': {
      backgroundColor: colors.surface1,
      border: `1px solid ${colors.surface3}`,
      color: colors.textPrimary,
    },
    '.cm-button': {
      backgroundColor: colors.surface2,
      border: `1px solid ${colors.surface3}`,
      color: colors.textPrimary,
    },
  },
  { dark: true }
);

/**
 * Syntax highlighting for markdown and code
 */
export const starkBiomeHighlighting = HighlightStyle.define([
  // Markdown
  { tag: t.heading1, color: colors.heading, fontWeight: 'bold', fontSize: '1.4em' },
  { tag: t.heading2, color: colors.heading, fontWeight: 'bold', fontSize: '1.2em' },
  { tag: t.heading3, color: colors.heading, fontWeight: 'bold', fontSize: '1.1em' },
  { tag: [t.heading4, t.heading5, t.heading6], color: colors.heading, fontWeight: 'bold' },
  { tag: t.emphasis, fontStyle: 'italic', color: colors.emphasis },
  { tag: t.strong, fontWeight: 'bold', color: colors.textPrimary },
  { tag: t.link, color: colors.link, textDecoration: 'underline' },
  { tag: t.url, color: colors.textMuted },
  { tag: t.quote, color: colors.textSecondary, fontStyle: 'italic' },
  { tag: t.monospace, color: colors.accentSecondaryGreen, fontFamily: 'monospace' },
  { tag: t.list, color: colors.textSecondary },

  // Code
  { tag: t.keyword, color: colors.keyword },
  { tag: t.operator, color: colors.textSecondary },
  { tag: t.definitionKeyword, color: colors.keyword, fontWeight: 'bold' },
  { tag: t.typeName, color: colors.accentGold },
  { tag: t.propertyName, color: colors.textPrimary },
  { tag: t.variableName, color: colors.textPrimary },
  { tag: t.function(t.variableName), color: colors.accentSecondaryGreen },
  { tag: t.definition(t.variableName), color: colors.accentSecondaryGreen },
  { tag: t.string, color: colors.string },
  { tag: t.number, color: colors.number },
  { tag: t.bool, color: colors.number },
  { tag: t.null, color: colors.number },
  { tag: t.comment, color: colors.comment, fontStyle: 'italic' },
  { tag: t.invalid, color: colors.accentError },
  { tag: t.meta, color: colors.textMuted },
  { tag: t.processingInstruction, color: colors.textMuted },
]);

/**
 * Complete STARK BIOME extension for CodeMirror
 */
export const starkBiome: Extension = [starkBiomeTheme, syntaxHighlighting(starkBiomeHighlighting)];

export default starkBiome;
