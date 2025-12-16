/**
 * Agent Creation: Wizard for creating new citizens.
 *
 * Three modes:
 * - Simple: Pick archetype, auto-generate name → Create (3 clicks)
 * - Custom: Pick archetype, adjust eigenvectors, name → Create
 * - Advanced: Full JSON/YAML editing for power users
 *
 * @see plans/web-refactor/user-flows.md
 */

export {
  AgentCreationWizard,
  type AgentCreationWizardProps,
  type CreationMode,
} from './AgentCreationWizard';

export {
  ArchetypePalette,
  type ArchetypePaletteProps,
} from './ArchetypePalette';

export {
  EigenvectorSliders,
  type EigenvectorSlidersProps,
} from './EigenvectorSliders';

export {
  AgentPreview,
  type AgentPreviewProps,
} from './AgentPreview';

export {
  AdvancedEditor,
  type AdvancedEditorProps,
} from './AdvancedEditor';
