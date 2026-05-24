# Arachne Utilities

A collection of stateless helper functions used across the project to maintain consistency and reduce code duplication.

## Modules

### `normalization.py`
Shared logic for cleaning up data from external APIs.
- **URL Building**: Safely joins base URLs and paths.
- **Date Parsing**: Converts various string date formats into standard Python `datetime` objects.
- **JSON Helpers**: Safe wrappers for parsing JSON strings found inside other data fields.

### `type_casts.py`
Utilities for safely converting types (e.g., strings to booleans or integers) with fallback values to prevent runtime crashes during normalization.

## Principles
- **Side-Effect Free**: Functions in this directory should be "pure"—given the same input, they always return the same output without modifying global state.
- **Strictly Typed**: Every utility uses Python type hints and is validated by `mypy`.
