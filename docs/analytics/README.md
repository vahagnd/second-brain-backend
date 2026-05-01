# Second Brain — Analytics

This directory contains analytical documentation for the **second-brain** project. It covers architecture, API contracts, data flows, configuration, and internal package design.

## Structure

```
analytics/
├── README.md                          ← you are here
├── gateway/
│   ├── overview.md                    ← architecture & component map
│   ├── api-endpoints.md               ← full API reference
│   ├── configuration.md               ← environment variables & settings
│   └── database.md                    ← DB schema & migration history
```

## Quick Links

| Document | Description |
|---|---|
| [gateway/overview.md](gateway/overview.md) | High-level architecture, layers, tech stack |
| [gateway/api-endpoints.md](gateway/api-endpoints.md) | All REST endpoints, schemas, status codes |
| [gateway/configuration.md](gateway/configuration.md) | All environment variables with defaults and types |
| [gateway/database.md](gateway/database.md) | Notes table schema and Alembic migration history |
