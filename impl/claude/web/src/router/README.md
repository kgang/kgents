# AGENTESE Router

**"The route is a lie. There is only the AGENTESE path and its projection."**

This is a radical rethinking of web routing where URLs become semantic AGENTESE invocations rather than traditional routes.

## Philosophy

Traditional web apps have two disconnected systems:
- **API Routes**: `POST /api/town/citizen { id: "kent_001" }`
- **UI Routes**: `GET /town/citizens/kent_001`

AGENTESE Router unifies them:
- **AGENTESE URLs**: `/world.town.citizen.kent_001`

The URL IS the AGENTESE invocation. One grammar, one source of truth.

## URL Grammar

```
/{context}.{entity}.{sub}...[:aspect][?params]
```

### Examples

```
# Crown Jewel entry points
/self.memory              → Brain overview
/world.town               → Town overview
/void.telescope           → Proof Engine

# Entity views
/world.town.citizen.kent_001       → Kent's citizen profile
/self.memory.crystal.abc123        → Memory crystal detail

# Aspect variations
/world.town.citizen.kent_001:polynomial  → Kent's polynomial state
/self.memory.crystal.abc123:heritage     → Crystal's ghost heritage

# Parameterized queries
/self.chat:stream?limit=20         → Chat stream with limit
/world.town.coalition?member=kent  → Coalitions containing Kent
```

## Basic Usage

### Navigation with Hooks

```typescript
import { useNavigateTo } from './router';

function MyComponent() {
  const goTo = useNavigateTo();

  return (
    <button onClick={() => goTo('world.town')}>
      Go to Town
    </button>
  );
}
```

### Navigation with Links

```typescript
import { AgentLink } from './components/navigation/AgentLink';

function MyComponent() {
  return (
    <AgentLink path="world.town.citizen.kent_001">
      View Kent's Profile
    </AgentLink>
  );
}
```

### Current Path Detection

```typescript
import { useAgentesePath, usePathMatch } from './router';

function MyComponent() {
  const path = useAgentesePath();
  const isInTown = usePathMatch('world.town');

  if (!path) {
    return null; // Not on an AGENTESE path
  }

  return (
    <div>
      <p>Context: {path.context}</p>
      <p>Full path: {path.fullPath}</p>
      {isInTown && <p>You're in the town!</p>}
    </div>
  );
}
```

## Advanced Usage

### Aspect Navigation

```typescript
import { useAgenteseNavigate } from './router';

function CitizenCard({ citizenId }: { citizenId: string }) {
  const navigate = useAgenteseNavigate();

  return (
    <div>
      <button onClick={() =>
        navigate('world.town.citizen', {
          segments: [citizenId],
          aspect: 'polynomial'
        })
      }>
        View Polynomial State
      </button>
    </div>
  );
}
```

### Parameters

```typescript
import { useAgenteseParams } from './router';

function ChatStream() {
  const params = useAgenteseParams();
  const limit = parseInt(params.limit || '50', 10);

  return <div>Showing {limit} messages</div>;
}
```

### Breadcrumbs

```typescript
import { useBreadcrumbs } from './router';
import { AgentLink } from './components/navigation/AgentLink';

function Breadcrumbs() {
  const breadcrumbs = useBreadcrumbs();

  return (
    <nav>
      {breadcrumbs.map((crumb, i) => (
        <span key={crumb.path}>
          {i > 0 && ' / '}
          <AgentLink path={crumb.path}>
            {crumb.label}
          </AgentLink>
        </span>
      ))}
    </nav>
  );
}
```

### Navigate Up

```typescript
import { useNavigateUp } from './router';

function BackButton() {
  const goUp = useNavigateUp();

  return (
    <button onClick={goUp}>
      ← Back to Parent
    </button>
  );
}
```

## Path Mappings

Current AGENTESE paths mapped to components:

| AGENTESE Path | Component | Shell |
|---------------|-----------|-------|
| `self.chat` | ChatPage | AppShell |
| `self.memory` | FeedPage | AppShell |
| `self.director` | DirectorPage | AppShell |
| `world.document` | HypergraphEditorPage | AppShell |
| `world.chart` | ChartPage | AppShell |
| `void.telescope` | ZeroSeedPage | TelescopeShell |

## Legacy Redirects

Legacy paths redirect to AGENTESE:

| Legacy | AGENTESE |
|--------|----------|
| `/brain` | `/self.memory` |
| `/chat` | `/self.chat` |
| `/director` | `/self.director` |
| `/editor` | `/world.document` |
| `/chart` | `/world.chart` |
| `/proof-engine` | `/void.telescope` |

## Migration Guide

### Phase 1: Update Navigation

Replace all `navigate()` calls:

```typescript
// Before
navigate('/chat?session=abc123');

// After
import { useNavigateTo } from './router';
const goTo = useNavigateTo();
goTo('self.chat.session.abc123');
```

### Phase 2: Update Links

Replace all `<Link>` components:

```typescript
// Before
<Link to="/town/citizens/kent_001">Kent</Link>

// After
import { AgentLink } from './components/navigation/AgentLink';
<AgentLink path="world.town.citizen.kent_001">Kent</AgentLink>
```

### Phase 3: Update Route Detection

Replace path checks:

```typescript
// Before
const isChat = location.pathname.startsWith('/chat');

// After
import { usePathMatch } from './router';
const isChat = usePathMatch('self.chat');
```

## API Reference

### Parsing & Generation

```typescript
// Parse URL to AGENTESE path
const path = parseAgentesePath('/self.chat.session.abc123');
// { context: 'self', path: ['chat', 'session', 'abc123'], ... }

// Generate URL from path
const url = toUrl('self.chat', { aspect: 'stream' });
// '/self.chat:stream'

// Build complex paths
const url = buildAgentesePath('world.town.citizen', {
  segments: ['kent_001'],
  aspect: 'polynomial',
  params: { view: 'graph' }
});
// '/world.town.citizen.kent_001:polynomial?view=graph'
```

### Hooks

```typescript
// Get current AGENTESE path
const path = useAgentesePath();

// Navigate with full options
const navigate = useAgenteseNavigate();
navigate('self.chat', { segments: ['session', 'abc'], aspect: 'stream' });

// Simple navigation
const goTo = useNavigateTo();
goTo('world.town', 'manifest');

// Match path pattern
const isInTown = usePathMatch('world.town');

// Get query parameters
const params = useAgenteseParams();

// Get current aspect
const aspect = useCurrentAspect();

// Get entity ID
const entityId = useEntityId();

// Navigate to parent
const goUp = useNavigateUp();

// Get breadcrumb trail
const breadcrumbs = useBreadcrumbs();
```

### Components

```typescript
// Basic link
<AgentLink path="world.town">Town</AgentLink>

// Link with aspect
<AgentLink path="self.chat" aspect="stream">Stream</AgentLink>

// Link with params
<AgentLink path="self.chat" params={{ limit: '20' }}>Recent Chat</AgentLink>

// Navigation link with active state
<AgentNavLink
  path="world.town"
  activeClassName="border-accent-primary"
>
  Town
</AgentNavLink>
```

## Testing

```typescript
import { parseAgentesePath, isAgentesePath } from './router';

// Check if URL is valid AGENTESE
if (isAgentesePath('/self.chat')) {
  const path = parseAgentesePath('/self.chat');
  // Safe to use
}

// Format path for display
import { formatPathLabel } from './router';
formatPathLabel('world.town.citizen.kent_001');
// → 'Citizen: kent_001'

// Get entity type
import { getEntityType } from './router';
getEntityType('world.town.citizen.kent_001');
// → 'citizen'
```

## Error Handling

```typescript
import { AgentesePathError } from './router';

try {
  const path = parseAgentesePath('/invalid');
} catch (error) {
  if (error instanceof AgentesePathError) {
    console.error(`Invalid path: ${error.url}`);
    console.error(error.message);
  }
}
```

## Architecture

```
URL: /self.chat.session.abc123
    │
    ▼
parseAgentesePath()
    │
    ▼
AgentesePath {
  context: 'self',
  path: ['chat', 'session', 'abc123'],
  fullPath: 'self.chat.session.abc123'
}
    │
    ▼
AgenteseRouter
    │
    ▼
Find PATH_MAPPINGS match
    │
    ▼
Render ChatPage with agenteseContext
```

## Files

- `AgentesePath.ts` - Path parsing and URL generation
- `useAgentesePath.ts` - React hooks for navigation
- `AgenteseRouter.tsx` - Universal projection handler
- `index.ts` - Public API exports
- `../components/navigation/AgentLink.tsx` - Navigation components

## Philosophy

This approach embodies Kent's principles:

> "Daring, bold, creative, opinionated but not gaudy"

Breaking web conventions, but making it SIMPLER, not more complex.

> "The Mirror Test: Does K-gent feel like me on my best day?"

Unification that makes you say "why didn't we always do this?"

> "Depth over breadth"

Eliminates routing as a concept rather than building more infrastructure.

> "Tasteful > feature-complete"

One grammar replaces two.

---

**The URL IS the thought. The page IS the answer.**
