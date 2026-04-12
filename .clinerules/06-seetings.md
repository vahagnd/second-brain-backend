# Settings & Configuration Rules

## Strict Rule
DO NOT use:
- os.getenv()
- python-dotenv

---

## Required approach
Use `pydantic-settings` for ALL configuration.

All environment configuration must live in:

app/config/settings.py

---

## Rules for Settings Design

- All environment variables must be defined as a Settings class
- Settings must be loaded once and reused (singleton pattern or cached instance)
- No direct environment variable access anywhere else in the codebase

---

## Example Structure

app/config/settings.py:
- Settings(BaseSettings)
- DATABASE_URL
- OPENAI_API_KEY
- DB_HOST, DB_PORT, DB_USER, DB_PASSWORD

---

## Usage Rule

- Only import Settings object from settings.py
- Never read env vars directly in services, api, or models

---

## Reason
This ensures:
- type safety
- central configuration control
- easier scaling
- clean separation of concerns