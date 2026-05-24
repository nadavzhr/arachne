# Arachne Configuration Implementation

This package handles the loading, validation, and internal representation of the application's configuration.

## Key Components

### `loader.py`
The "factory" for configuration.
- Uses `PyYAML` to parse files in the `config/` directory.
- Maps raw YAML data into `GlobalConfig` and `SourceConfig` Pydantic models.
- **Fail-Fast**: If the configuration is invalid, it raises a `ValidationError` at startup.

### `profile.py`
Dedicated logic for the `profiles/` directory.
- Handles the inheritance/override logic where source-specific settings take precedence over global profile settings.

## Data Models
We use Pydantic models to represent configuration:
- **`GlobalConfig`**: System-level settings.
- **`SourceConfig`**: Per-source registry settings (URL, enabled status).
- **`SearchProfile`**: Criteria for a specific search run.

## Why this approach?
By using Pydantic for configuration, we get:
1. **Schema Validation**: No more `KeyError` at runtime because a config field was misspelled.
2. **Type Casting**: Automatically converts string values from YAML into integers or floats.
3. **Autocompletion**: Modern IDEs can "see" the configuration structure.
