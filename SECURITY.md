# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in kgents, please report it responsibly:

1. **Do NOT** open a public issue
2. Email security concerns to the maintainer directly
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes

We will acknowledge receipt within 48 hours and provide a timeline for resolution.

---

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.x   | :white_check_mark: |

---

## Security Best Practices

### Environment Variables

**Never commit secrets to git.** Use environment variables:

```bash
# Database
KGENTS_DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db

# CORS (production)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# CORS (local development only)
CORS_ALLOW_ALL=1
```

### Local Development

1. Copy `.env.example` to `.env`
2. Never commit `.env` files
3. Use Docker for PostgreSQL (credentials stay local)

### API Keys

- Store API keys in environment variables, not code
- Use separate keys for development and production
- Rotate keys periodically

---

## Known Security Considerations

### CORS Configuration

By default, CORS allows only `http://localhost:3000`. To change:

```bash
# Production: explicit origins
CORS_ORIGINS=https://yourdomain.com

# Development: allow all (disables credentials for safety)
CORS_ALLOW_ALL=1
```

### Database Credentials

Default development credentials (`kgents:kgents`) are for local Docker only. In production:

- Use strong, unique passwords
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- Never expose database ports publicly

---

## Security Checklist for Contributors

- [ ] No hardcoded credentials in code
- [ ] No API keys in commits
- [ ] No `.env` files committed
- [ ] CORS configured appropriately
- [ ] Input validation on all endpoints
- [ ] Dependencies regularly updated

---

*Last updated: 2025-12-23*
