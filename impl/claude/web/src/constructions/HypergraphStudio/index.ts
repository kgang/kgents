/**
 * HypergraphStudio: Graph + Trail + ValueCompass
 *
 * A construction composing three primitives for the hypergraph editing experience:
 * - Graph (HypergraphEditor): Modal editing with K-Block isolation
 * - Trail: Derivation breadcrumb showing navigation path
 * - ValueCompass: Constitutional alignment visualization
 *
 * Usage:
 * ======
 *
 * ```typescript
 * import { HypergraphStudio } from '@/constructions/HypergraphStudio';
 *
 * function MyPage() {
 *   const [scores, setScores] = useState<ConstitutionScores>({
 *     tasteful: 0.8,
 *     curated: 0.9,
 *     ethical: 1.0,
 *     joyInducing: 0.7,
 *     composable: 0.85,
 *     heterarchical: 0.6,
 *     generative: 0.75,
 *   });
 *
 *   return (
 *     <HypergraphStudio
 *       initialPath="spec/protocols/witness.md"
 *       showTheory={true}
 *       constitutionScores={scores}
 *       onNavigate={(path) => console.log('Navigated to:', path)}
 *       onZeroSeed={(tab) => navigateToZeroSeed(tab)}
 *     />
 *   );
 * }
 * ```
 *
 * Props:
 * ======
 *
 * - `initialPath`: Initial file to open in editor
 * - `showTheory`: Show ValueCompass panel (default: false)
 * - `constitutionScores`: Current principle scores (0-1 for each)
 * - `policyTrace`: Decision trajectory over time
 * - `onSave`: Callback when file is saved
 * - `onNavigate`: Callback when navigation occurs
 * - `onZeroSeed`: Callback to navigate to Zero Seed page
 * - `loadNode`: Custom node loader (optional, uses default GraphNode API)
 * - `loadSiblings`: Custom sibling loader (optional)
 *
 * Keyboard Shortcuts:
 * ===================
 *
 * - `Cmd+Shift+V`: Toggle ValueCompass panel
 * - All HypergraphEditor shortcuts (see docs/skills/hypergraph-editor.md)
 *
 * Architecture:
 * =============
 *
 * HypergraphStudio maintains minimal state:
 * - Current node (from HypergraphEditor)
 * - Navigation path (for Trail)
 * - Compass open/closed (UI state)
 *
 * All heavy lifting is delegated to primitives:
 * - Graph handles modal editing, K-Block isolation, keybindings
 * - Trail handles breadcrumb rendering and navigation
 * - ValueCompass handles principle visualization
 *
 * This construction is GLUE CODE - it orchestrates primitives but contains
 * no business logic of its own.
 *
 * @see docs/skills/hypergraph-editor.md
 * @see spec/protocols/zero-seed.md (PolicyTrace compression)
 */

export { HypergraphStudio } from './HypergraphStudio';
export type { HypergraphStudioProps } from './HypergraphStudio';
