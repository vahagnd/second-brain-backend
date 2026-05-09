# AI Agent Rules

## Get information about project structure and existing microservices from:
 - Docker compose file - [docker-compose.yml](docker-compose.yml)

## Get more detailed information about existing apps from analytics files:
- Gateway Service, API - [docs/analytics/API_ANALYTICS.md](docs/analytics/API_ANALYTICS.md)

## Before starting any implementation or coding task load rules from file:
- Development rules [docs/DEV_RULES.md](docs/DEV_RULES.md)

## After adding new features
- Add new changes to [docs/CHANGELOG.md](docs/CHANGELOG.md) under `## [Unreleased]`. Use this format for each entry:
```
  - Short summary line
    <details>
    Detailed description: inputs, outputs, error cases, side effects.
    </details>
```
- Update API analytics at [docs/analytics/API_ANALYTICS.md](docs/analytics/API_ANALYTICS.md)
- DO NOT add tests, if not told explicitly
