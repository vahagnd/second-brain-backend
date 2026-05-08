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

## 4. Tests (Check this section ONLY if adding tests)
- All tests should be inside folder /tests
- Tests should be INDEPENDENT and should NOT leave anything behind, proper cleanup IS REQUIRED
- For tests use `pytest`, its already added into dependencies dont worry about it
- Test names should include case name from case files - for example test_11_something_soemthing
- Dont use classes, tests should be grouped in modules
- Try to use common fixtures inside root tests/conftest.py, create new conftests if nececcary
- Test cases files are here - [tests/cases/](tests/cases/)
- Tests should be grouped by cases inside subfolders
- E2E tests should be added in [tests/e2e-tests/](tests/e2e-tests/) directory
