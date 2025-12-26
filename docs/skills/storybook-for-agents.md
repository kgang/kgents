# Skill: Storybook for Agents

> *"Stories are component truth tables. Human-browsable, agent-indexable."*

## Overview

Storybook serves dual purpose: **human gallery** (visual, interactive) and **agent registry** (structured, queryable). Every story is a witnessed fact about component behavior—stories express the component algebra.

```
Story = Component × Args → Rendered Truth
```

| Story Type | Proves |
|------------|--------|
| Default | Component exists and renders |
| Size variants | Component scales correctly |
| State variants | Component handles all states |
| Responsive | Component adapts to density |
| Composition | Component composes with others |

---

## When to Use

- **After creating new UI components** — Story is the component's birth certificate
- **When documenting component behavior** — Stories are living documentation
- **For visual regression testing** — Chromatic/Percy can diff stories
- **When AI needs to understand capabilities** — Stories are machine-parseable

---

## Story Generation Protocol

1. **Analyze props/types** — Each prop axis = story variants needed
2. **Generate Default** — Sensible baseline args
3. **Add variants**: size, state, responsive (compact/comfortable/spacious)
4. **Add composition** — Show how it combines with other components

```typescript
// 1. Start from type signature
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

// 2-4. Generate stories for each axis
export const Default: Story = { args: { variant: 'primary', size: 'md' } };
export const Small: Story = { args: { size: 'sm' } };
export const Disabled: Story = { args: { disabled: true } };
export const WithIcon: Story = {
  render: () => <Button><IconPlus /> Add</Button>,
};
```

---

## Required Story Variants by Type

| Component Type | Required Stories |
|----------------|------------------|
| **Primitive** | Default, Size variants, State variants, Responsive |
| **Composed** | Default, With children, Edge cases, Loading/Error |
| **Page** | Default, Loading, Error, Empty state |

---

## Story File Structure

```tsx
import type { Meta, StoryObj } from '@storybook/react-vite';
import { ComponentName } from './ComponentName';
import './ComponentName.css';  // Required for isolated rendering

const meta: Meta<typeof ComponentName> = {
  title: 'Primitives/ComponentName',  // or Components/, Pages/
  component: ComponentName,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: { description: { component: 'Description + STARK BIOME notes' } },
  },
  argTypes: {
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
  },
};
export default meta;
type Story = StoryObj<typeof ComponentName>;

export const Default: Story = { args: { /* default props */ } };
export const Variant: Story = { args: { /* variant props */ } };
```

---

## STARK BIOME Integration

Stories must demonstrate the design system: **90% steel / 10% earned glow**.

```tsx
// Document token usage in meta
parameters: {
  docs: {
    description: {
      component: `
**Colors:** \`steel-carbon\` bg, \`glow-spore\` accent
**Radius:** \`--radius-sm\` (2px Bare Edge)
      `,
    },
  },
},
```

For breathing animations:

```tsx
export const Breathing: Story = {
  args: { breathing: true, breathingIntensity: 'subtle' },
};
```

---

## Responsive Testing

Use the preconfigured density viewports:

```tsx
export const Mobile: Story = {
  parameters: { viewport: { defaultViewport: 'compact' } },    // 375px
};
export const Tablet: Story = {
  parameters: { viewport: { defaultViewport: 'comfortable' } }, // 768px
};
export const Desktop: Story = {
  parameters: { viewport: { defaultViewport: 'spacious' } },   // 1440px
};
```

---

## Agent Commands (Planned)

```bash
kg storybook list --json              # List all stories
kg storybook coverage                  # Check coverage
kg storybook generate <component>      # Scaffold story
```

Future AGENTESE paths:
```
concept.storybook.components.list       → List all stories
concept.storybook.component.coverage    → Check coverage gaps
```

---

## Anti-Patterns

```tsx
// BAD: Only Default story (no variants)
export const Default: Story = { args: { label: 'Hello' } };

// BAD: No responsive testing
// Missing viewport parameters

// BAD: No composition stories for primitives
// Only showing component in isolation

// BAD: No documentation
const meta: Meta = { title: 'X', component: X };  // No docs.description
```

**GOOD**: Complete coverage with Default + Size + State + Responsive + Composition stories, all with documentation.

---

## Integration with Witness

```bash
km "Generated stories for ComponentName" --tag storybook
```

---

## Checklist

- [ ] Meta with `title`, `component`, `tags: ['autodocs']`
- [ ] Component description in `parameters.docs`
- [ ] Default story with sensible args
- [ ] Size variants (if applicable)
- [ ] State variants (disabled, loading, error)
- [ ] Responsive stories (compact, comfortable, spacious)
- [ ] Composition stories (real usage patterns)
- [ ] CSS import for isolated rendering

---

## Running Storybook

```bash
cd impl/claude/web && npm run storybook  # Opens at http://localhost:6006
```

---

## Related

- `impl/claude/web/.storybook/` — Storybook configuration
- `impl/claude/web/src/design/tokens.css` — STARK BIOME tokens
- `docs/skills/elastic-ui-patterns.md` — Responsive patterns

---

*"The frame is humble. The content glows. The story is the proof."*
