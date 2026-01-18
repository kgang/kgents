/**
 * WorkspaceHeader — Dense navigation bar
 *
 * Grounded in: spec/ui/severe-stark.md (Yahoo Japan Density)
 * "50+ links visible, 11px text, every pixel used."
 *
 * Shows: Context tabs + status indicators
 */

// No type imports needed - using primitive props

interface WorkspaceHeaderProps {
  /** Current AGENTESE path */
  currentPath?: string;

  /** Current density mode */
  density?: 'compact' | 'comfortable' | 'spacious';

  /** Garden health summary */
  gardenHealth?: number;

  /** Handler for path navigation */
  onNavigate?: (path: string) => void;
}

/**
 * Dense header with AGENTESE context navigation.
 */
export function WorkspaceHeader({
  currentPath = 'workspace',
  density = 'spacious',
  gardenHealth = 1,
  onNavigate,
}: WorkspaceHeaderProps) {
  const contexts = [
    { key: 'world', label: 'world', path: 'world.document' },
    { key: 'self', label: 'self', path: 'self.constitution' },
    { key: 'concept', label: 'concept', path: 'concept.axiom' },
    { key: 'void', label: 'void', path: 'void.entropy' },
    { key: 'time', label: 'time', path: 'time.witness' },
  ];

  const healthColor =
    gardenHealth >= 0.8
      ? 'var(--collapse-pass)'
      : gardenHealth >= 0.5
        ? 'var(--collapse-partial)'
        : 'var(--collapse-fail)';

  return (
    <header className="workspace-header">
      {/* Logo */}
      <span className="workspace-header__logo">kgents</span>
      <span className="workspace-header__divider">|</span>

      {/* Context navigation */}
      <nav className="workspace-header__nav nav-dense">
        {contexts.map((ctx) => (
          <a
            key={ctx.key}
            href={`/${ctx.path}`}
            className={`workspace-header__context ${currentPath.startsWith(ctx.key) ? 'workspace-header__context--active' : ''}`}
            onClick={(e) => {
              if (onNavigate) {
                e.preventDefault();
                onNavigate(ctx.path);
              }
            }}
          >
            [{ctx.label}]
          </a>
        ))}
      </nav>

      {/* Spacer */}
      <div className="workspace-header__spacer" />

      {/* Status indicators */}
      <div className="workspace-header__status">
        <span className="workspace-header__user">KENT</span>
        <span className="workspace-header__divider">|</span>
        <span className="workspace-header__density">density:{density}</span>
        <span className="workspace-header__divider">|</span>
        <span className="workspace-header__garden" style={{ color: healthColor }}>
          garden:{Math.round(gardenHealth * 100)}%
        </span>
      </div>
    </header>
  );
}

export default WorkspaceHeader;
