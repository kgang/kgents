/**
 * Editor Components
 *
 * CodeMirror 6 based editors with STARK BIOME theming.
 */

export { MarkdownEditor } from './MarkdownEditor';
export type { MarkdownEditorProps, MarkdownEditorRef } from './MarkdownEditor';

export { useCodeMirror, configureVimDefaults } from './useCodeMirror';
export type { UseCodeMirrorOptions, UseCodeMirrorReturn } from './useCodeMirror';

export { starkBiome, starkBiomeTheme, starkBiomeHighlighting } from './starkBiomeTheme';
