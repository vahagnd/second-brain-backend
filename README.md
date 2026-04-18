## Development Setup

To set up the project for development, use the following `Makefile` commands:

Initialize the project for development:
   ```bash
   make project-init-dev
   ```

Install only necessary packages:
   ```bash
   make project-init-run
   ```

## Docker

Start the full stack:
```bash
make start
```

Start with rebuild (after code changes):
```bash
make start-build
```

Stop the stack:
```bash
make stop
```

Restart:
```bash
make restart
```

## Linting

```bash
make lint
```
