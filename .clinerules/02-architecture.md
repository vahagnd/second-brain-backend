# Architecture Rules

## Layers

- API layer: routing only
- Service layer: business logic only
- Models: database schema only
- Schemas: validation only

## Data flow

Request → API → Service → DB → Service → API → Response

## Constraints
- No logic in routes
- No circular dependencies
- Keep functions small and single-purpose
