/**
 * Workspace Construction
 *
 * Three-panel IDE-like layout for kgents:
 * - Left: Files/Director sidebar
 * - Center: EditorPane (subscribes to navigation state)
 * - Right: Chat sidebar
 *
 * "The Hypergraph Editor IS the app. Everything else is a sidebar."
 *
 * Re-render Isolation:
 * - EditorPane is the ONLY component that re-renders on navigation
 * - Sidebars remain stable when clicking K-Blocks
 */

export { Workspace, type WorkspaceProps } from './Workspace';
export { EditorPane } from './EditorPane';
export { default } from './Workspace';
