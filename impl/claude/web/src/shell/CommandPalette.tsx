/**
 * CommandPalette - Quick navigation and actions (Cmd+K)
 *
 * A tasteful command palette for:
 * - Quick navigation to AGENTESE paths
 * - Running terminal commands
 * - Triggering actions
 *
 * @see spec/protocols/os-shell.md
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  ArrowRight,
  Terminal,
  User,
  Clock,
  Brain,
  Network,
  Palette,
  Users,
  Theater,
  Building,
  Command,
  type LucideIcon,
} from 'lucide-react';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { JEWEL_COLORS } from '@/constants/jewels';

// =============================================================================
// Types
// =============================================================================

export interface CommandPaletteProps {
  /** Whether the palette is open */
  isOpen: boolean;
  /** Callback to close the palette */
  onClose: () => void;
  /** Callback to focus terminal with a command */
  onTerminalCommand?: (command: string) => void;
}

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon: LucideIcon;
  iconColor?: string;
  category: 'navigation' | 'action' | 'terminal';
  action: () => void;
  keywords?: string[];
}

// =============================================================================
// Component
// =============================================================================

export function CommandPalette({ isOpen, onClose, onTerminalCommand }: CommandPaletteProps) {
  const navigate = useNavigate();
  const { shouldAnimate } = useMotionPreferences();
  const inputRef = useRef<HTMLInputElement>(null);

  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Build command items
  const commands = useMemo<CommandItem[]>(() => {
    const nav = (
      path: string,
      label: string,
      icon: LucideIcon,
      iconColor?: string,
      description?: string
    ): CommandItem => ({
      id: `nav-${path}`,
      label,
      description: description || path,
      icon,
      iconColor,
      category: 'navigation',
      action: () => {
        navigate(`/${path}`);
        onClose();
      },
      keywords: [path, label.toLowerCase()],
    });

    const action = (
      id: string,
      label: string,
      icon: LucideIcon,
      actionFn: () => void,
      description?: string
    ): CommandItem => ({
      id,
      label,
      description,
      icon,
      category: 'action',
      action: () => {
        actionFn();
        onClose();
      },
      keywords: [label.toLowerCase()],
    });

    const terminalCmd = (cmd: string, label: string, description?: string): CommandItem => ({
      id: `term-${cmd}`,
      label,
      description: description || `Run: ${cmd}`,
      icon: Terminal,
      iconColor: 'text-cyan-400',
      category: 'terminal',
      action: () => {
        onTerminalCommand?.(cmd);
        onClose();
      },
      keywords: [cmd, label.toLowerCase()],
    });

    return [
      // Navigation - Crown Jewels
      nav('self.memory', 'Brain', Brain, JEWEL_COLORS.brain.primary, 'Memory & crystallization'),
      nav('world.codebase', 'Gestalt', Network, JEWEL_COLORS.gestalt.primary, 'Codebase analysis'),
      nav('world.forge', 'Forge', Palette, JEWEL_COLORS.forge.primary, 'Design workshop'),
      nav('world.town', 'Town', Users, JEWEL_COLORS.coalition.primary, 'Agent simulation'),
      nav('world.park', 'Park', Theater, JEWEL_COLORS.park.primary, 'Roleplay scenarios'),
      nav('world.domain', 'Domain', Building, JEWEL_COLORS.domain.primary, 'Domain modeling'),

      // Navigation - Contexts
      nav('self.cockpit', 'Cockpit', User, 'text-cyan-400', 'Developer dashboard'),
      nav('time.differance', 'Differance', Clock, 'text-amber-400', 'Trace visualization'),

      // Terminal commands
      terminalCmd('help', 'Help', 'Show terminal commands'),
      terminalCmd('clear', 'Clear Terminal', 'Clear terminal output'),
      terminalCmd('discover', 'Discover Paths', 'List all AGENTESE paths'),

      // Actions
      action(
        'toggle-nav',
        'Toggle Navigation',
        Command,
        () => {
          // This will be handled by the shell
          document.dispatchEvent(new CustomEvent('shell:toggle-nav'));
        },
        'Show/hide sidebar'
      ),
    ];
  }, [navigate, onClose, onTerminalCommand]);

  // Filter commands based on query
  const filteredCommands = useMemo(() => {
    if (!query.trim()) return commands;

    const q = query.toLowerCase();
    return commands.filter((cmd) => {
      if (cmd.label.toLowerCase().includes(q)) return true;
      if (cmd.description?.toLowerCase().includes(q)) return true;
      if (cmd.keywords?.some((k) => k.includes(q))) return true;
      return false;
    });
  }, [commands, query]);

  // Reset state when opened
  useEffect(() => {
    if (isOpen) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          setSelectedIndex((prev) => (prev < filteredCommands.length - 1 ? prev + 1 : 0));
          break;
        case 'ArrowUp':
          event.preventDefault();
          setSelectedIndex((prev) => (prev > 0 ? prev - 1 : filteredCommands.length - 1));
          break;
        case 'Enter':
          event.preventDefault();
          if (filteredCommands[selectedIndex]) {
            filteredCommands[selectedIndex].action();
          }
          break;
        case 'Escape':
          event.preventDefault();
          onClose();
          break;
      }
    },
    [filteredCommands, selectedIndex, onClose]
  );

  // Keep selected index in bounds
  useEffect(() => {
    if (selectedIndex >= filteredCommands.length) {
      setSelectedIndex(Math.max(0, filteredCommands.length - 1));
    }
  }, [filteredCommands.length, selectedIndex]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: shouldAnimate ? 0.15 : 0 }}
            className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Palette */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{
              duration: shouldAnimate ? 0.2 : 0,
              ease: [0.4, 0, 0.2, 1],
            }}
            className="fixed z-50 top-[15%] left-1/2 -translate-x-1/2 w-full max-w-lg"
          >
            <div className="bg-steel-carbon/95 backdrop-blur-md rounded-xl border border-steel-gunmetal/50 shadow-2xl overflow-hidden">
              {/* Search input */}
              <div className="flex items-center gap-3 px-4 py-3 border-b border-steel-gunmetal/50">
                <Search className="w-5 h-5 text-steel-zinc flex-shrink-0" />
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type a command or search..."
                  className="flex-1 bg-transparent text-white placeholder-steel-zinc outline-none text-sm"
                  autoComplete="off"
                  autoCapitalize="off"
                  spellCheck={false}
                />
                <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded text-steel-zinc">
                  Esc
                </kbd>
              </div>

              {/* Results */}
              <div className="max-h-[50vh] overflow-auto py-2">
                {filteredCommands.length === 0 ? (
                  <div className="px-4 py-8 text-center text-steel-zinc text-sm">
                    No commands found for "{query}"
                  </div>
                ) : (
                  filteredCommands.map((cmd, index) => {
                    const Icon = cmd.icon;
                    const isSelected = index === selectedIndex;

                    return (
                      <button
                        key={cmd.id}
                        onClick={cmd.action}
                        onMouseEnter={() => setSelectedIndex(index)}
                        className={`
                          w-full flex items-center gap-3 px-4 py-2.5 text-left
                          transition-colors
                          ${isSelected ? 'bg-steel-slate/50' : 'hover:bg-steel-slate/30'}
                        `}
                      >
                        <Icon
                          className="w-4 h-4 flex-shrink-0"
                          style={{ color: cmd.iconColor || 'rgb(156, 163, 175)' }}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm text-white">{cmd.label}</div>
                          {cmd.description && (
                            <div className="text-xs text-steel-zinc truncate">
                              {cmd.description}
                            </div>
                          )}
                        </div>
                        {isSelected && (
                          <ArrowRight className="w-4 h-4 text-steel-zinc flex-shrink-0" />
                        )}
                      </button>
                    );
                  })
                )}
              </div>

              {/* Footer hints */}
              <div className="px-4 py-2 border-t border-steel-gunmetal/50 bg-steel-carbon/50 flex items-center justify-between text-xs text-steel-zinc">
                <div className="flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    <kbd className="px-1 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded">
                      ↑
                    </kbd>
                    <kbd className="px-1 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded">
                      ↓
                    </kbd>
                    navigate
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-steel-slate/50 border border-steel-gunmetal/50 rounded">
                      Enter
                    </kbd>
                    select
                  </span>
                </div>
                <span>{filteredCommands.length} commands</span>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

export default CommandPalette;
