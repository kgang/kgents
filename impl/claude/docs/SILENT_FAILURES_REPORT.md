# Silent Failures Report

**Generated**: 2026-01-16
**Severity Scale**: CRITICAL (data loss) > HIGH (unexpected behavior) > MEDIUM (degraded functionality)

---

## Executive Summary

This report documents the top 5 most critical silent failure patterns in the kgents codebase. These patterns can cause data loss, unexpected behavior, or production issues that are difficult to diagnose because they fail without visible errors.

---

## Top 5 Critical Silent Failures

### 1. CRITICAL: Database Fallback Without Warning

**Location**: `models/base.py:get_database_url()`, `agents/d/router.py`, `protocols/cli/instance_db/providers/router.py`

**The Problem**:
When `KGENTS_DATABASE_URL` is not set, the system silently falls back to SQLite at `~/.local/share/kgents/membrane.db`. This causes:
- Data stored in previous sessions appears to vanish if the SQLite path changes
- Users think they have persistence when they actually have ephemeral local storage
- No warning is logged at startup about using fallback storage

**Code Pattern**:
```python
# models/base.py:145-171
if url := os.environ.get("KGENTS_DATABASE_URL"):
    return url  # Good path

# ... silent fallback to SQLite ...
return f"sqlite+aiosqlite:///{db_path}"  # No warning!
```

**Fix Required**:
```python
# Add warning when falling back
if not os.environ.get("KGENTS_DATABASE_URL"):
    logger.warning(
        "KGENTS_DATABASE_URL not set. Using SQLite fallback at %s. "
        "Data may be lost on restart. Set KGENTS_DATABASE_URL for persistence.",
        db_path
    )
```

**Impact**: Users lose data between sessions, troubleshoot for hours

---

### 2. HIGH: Stripe Webhook Verification Silently Skipped

**Location**: `protocols/api/payments.py:398`, `protocols/api/webhooks.py:221`

**The Problem**:
When `STRIPE_WEBHOOK_SECRET` is not configured, webhook signature verification is silently skipped with only a warning log. This means:
- Webhooks can be spoofed in production
- Payment events could be forged
- No visible indication in the API response

**Code Pattern**:
```python
# protocols/api/payments.py:398
logger.warning("STRIPE_WEBHOOK_SECRET not set, skipping signature verification")
# ... continues processing webhook without verification ...
```

**Fix Required**:
- In production (`KGENTS_ENVIRONMENT=production`), raise an error if secret is not set
- Make the warning more prominent (use `logger.error` or send alert)
- Return HTTP 500 instead of processing unverified webhooks

**Impact**: Security vulnerability in production payment processing

---

### 3. HIGH: Bootstrap Swallows Migration Failures

**Location**: `infra/lifecycle.py:180-191`

**The Problem**:
Database migration failures are caught, logged to an `errors` list, and then the system continues with a "DB-less fallback". This means:
- Schema changes silently fail
- The app starts but operates without proper database structure
- Errors are buried in a list, not surfaced to the user
- Data operations fail later with confusing errors

**Code Pattern**:
```python
try:
    await storage.run_migrations()
except Exception as e:
    errors.append(f"Migration failed: {e}")  # Just appends to list!
    # Try recovery once
    try:
        await storage.run_migrations()
    except Exception as retry_e:
        errors.append(f"Migration retry failed: {retry_e}")
        # Fall back to DB-less  <-- Silent degradation!
        await storage.close()
        return self._create_db_less_state(project, errors)
```

**Fix Required**:
- Log errors at `ERROR` level, not just append to list
- Surface migration failures to CLI output
- Require explicit `--allow-db-fallback` flag for DB-less mode
- Exit with non-zero code if migrations fail

**Impact**: App appears to work but silently operates in degraded mode

---

### 4. MEDIUM: NATS Connection Failure Swallowed

**Location**: `protocols/streaming/nats_bridge.py:269-275`

**The Problem**:
NATS connection failures are logged as warnings but the code continues with "graceful degradation". Events are buffered in memory but:
- In-memory buffer has a size limit (not clear when exceeded)
- Events are lost on restart
- No indication to users that their events aren't being persisted
- `publish_soul_event` silently uses fallback without user awareness

**Code Pattern**:
```python
except ImportError:
    logger.warning("nats-py not installed, using in-memory fallback")
    self._connected = False
except Exception as e:
    logger.error(f"NATS connection failed: {e}")
    self._connected = False
    # Don't raise - graceful degradation  <-- Silent!
```

**Fix Required**:
- Track and expose metrics on fallback usage
- Warn users in CLI output when operating in fallback mode
- Provide `is_degraded()` method that CLI can check and display
- Add health check endpoint that reports NATS status

**Impact**: Events silently lost, users unaware of degraded state

---

### 5. MEDIUM: Empty API Keys Treated as Valid

**Location**: Multiple files - `protocols/api/payments.py:39-41`, `protocols/billing/stripe_client.py:48-53`, etc.

**The Problem**:
Many API keys default to empty string `""` instead of `None`, making it hard to distinguish "not configured" from "configured but empty". This causes:
- `if key:` checks pass for empty strings in some Python contexts
- Late failures when actually trying to use the API
- Confusing error messages from external services
- No startup validation

**Code Pattern**:
```python
# protocols/api/payments.py:39-41
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")  # Empty string!
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Later...
if HAS_STRIPE and STRIPE_SECRET_KEY:  # Empty string is falsy, but...
    stripe.api_key = STRIPE_SECRET_KEY
```

**Fix Required**:
- Use `None` as default instead of `""`
- Add startup validation that checks required keys for enabled features
- Provide clear error messages like "Stripe payments enabled but STRIPE_SECRET_KEY not set"
- Implement `kg setup check` command to validate configuration

**Impact**: Confusing late failures, poor debugging experience

---

## Additional Silent Failure Patterns (Lower Priority)

### Exception Swallowing in Tracing
**Location**: `weave/runtime_trace.py:268-269, 413-414, 432-433`
```python
except Exception:
    pass  # Don't fail tracing if OTEL fails
```
**Risk**: Telemetry silently lost, makes debugging harder

### Redis Fallback
**Location**: `infra/stigmergy/__init__.py:145-146`
```python
except Exception as e:
    logger.warning(f"Could not connect to Redis: {e}. Using fallback.")
    self._client = None
```
**Risk**: Caching silently disabled, performance degradation

### Callback Errors Swallowed
**Location**: `weave/yield_handler.py:368-370`
```python
except Exception:
    # Callbacks should not break the approval flow
    pass
```
**Risk**: Custom handlers fail silently

---

## Recommended Actions

### Immediate (Before Next Release)

1. **Add startup warning for SQLite fallback** - Single most impactful fix
2. **Add `kg setup check` command** - Validates environment configuration
3. **Make webhook verification failure explicit in production**

### Short-Term (Next Sprint)

4. **Add health check endpoint** that reports:
   - Database backend (Postgres vs SQLite)
   - NATS connection status
   - Redis connection status
   - LLM provider availability

5. **Improve error surfacing** in CLI output:
   - Show `errors` list from LifecycleState
   - Color-code degraded status
   - Add `--strict` flag that fails on any degradation

### Long-Term (Technical Debt)

6. **Replace empty string defaults** with `None` across all env var reads
7. **Add configuration schema validation** at startup
8. **Implement circuit breaker metrics** that are exposed via health endpoints

---

## Setup Verification Command Concept: `kg setup check`

This command should verify the development environment is correctly configured.

### What It Should Check

```
$ kg setup check

kgents Environment Check
========================

Python Environment:
  [OK] Python 3.12.0 (required: >=3.11)
  [OK] uv installed
  [OK] Dependencies installed

Database:
  [!!] KGENTS_DATABASE_URL not set - using SQLite fallback
  [OK] PostgreSQL reachable at localhost:5432
  [OK] Database 'kgents' exists
  [OK] Migrations up to date (revision: abc123)

LLM Providers:
  [--] ANTHROPIC_API_KEY not set
  [--] OPENROUTER_API_KEY not set
  [OK] MORPHEUS_URL set (http://localhost:8080/v1)
  [!!] No LLM provider available - Soul features will fail

External Services:
  [--] Redis not configured (caching disabled)
  [--] NATS not configured (events use in-memory buffer)
  [--] Qdrant not configured (vector search disabled)

Frontend:
  [OK] Node.js 20.10.0 (required: >=18)
  [OK] npm 10.2.0
  [OK] Dependencies installed

Overall Status: DEGRADED
  - Data persistence: SQLite (ephemeral)
  - LLM features: Unavailable
  - Caching: In-memory only

Recommendations:
  1. Set KGENTS_DATABASE_URL for persistent storage
  2. Set ANTHROPIC_API_KEY or OPENROUTER_API_KEY for LLM features

Run 'docker compose up -d' to start PostgreSQL.
```

### Implementation Skeleton

```python
# protocols/cli/handlers/setup.py

async def check_setup() -> SetupStatus:
    """Verify environment configuration."""
    status = SetupStatus()

    # Python checks
    status.python_version = sys.version_info
    status.python_ok = sys.version_info >= (3, 11)

    # Database checks
    db_url = os.environ.get("KGENTS_DATABASE_URL")
    status.database_configured = db_url is not None
    if db_url:
        status.database_reachable = await check_database_connection(db_url)
        status.migrations_current = await check_migrations(db_url)

    # LLM checks
    status.anthropic_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    status.openrouter_key = bool(os.environ.get("OPENROUTER_API_KEY"))
    status.morpheus_url = os.environ.get("MORPHEUS_URL")
    status.llm_available = any([
        status.anthropic_key,
        status.openrouter_key,
        status.morpheus_url,
    ])

    # External services
    status.redis_url = os.environ.get("REDIS_URL")
    status.nats_servers = os.environ.get("NATS_SERVERS")
    status.qdrant_url = os.environ.get("KGENTS_QDRANT_URL")

    # Frontend checks
    status.node_version = get_node_version()
    status.npm_installed = check_npm()

    return status
```

### Exit Codes

- `0`: All checks passed
- `1`: Critical failures (database unreachable, Python version wrong)
- `2`: Degraded mode (missing optional services)

---

## Appendix: Files Modified for This Report

Analysis covered these key files:
- `impl/claude/models/base.py`
- `impl/claude/agents/d/router.py`
- `impl/claude/protocols/cli/instance_db/providers/router.py`
- `impl/claude/protocols/api/payments.py`
- `impl/claude/protocols/api/webhooks.py`
- `impl/claude/infra/lifecycle.py`
- `impl/claude/protocols/streaming/nats_bridge.py`
- `impl/claude/infra/stigmergy/__init__.py`
- `impl/claude/weave/runtime_trace.py`
- `impl/claude/weave/yield_handler.py`
