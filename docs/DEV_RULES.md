# Development rules

## 1. Environment setup
- The environment must be configured via a `.env` file
- Variables from `.env` should be read using the **pydantic-settings** framework

## 2. Module constraints
- Individual files (modules) must not exceed **400 lines**
- Minimize **code duplication**

## 3. Package manager
- Use **uv** from Astral to install dependencies
- Never use pip directly
