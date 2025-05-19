# Utilities Component

The Utilities component provides helper functions for file operations and data processing used throughout the SP34KN0W Live Transcriber application.

## File Location

`src/utils.py`

## Dependencies

- `os`: For file and directory operations
- `json`: For data serialization and deserialization

## Functions

### `ensure_dir_exists(directory)`

Creates a directory if it doesn't already exist.

- **Parameters**:
  - `directory` (str): Path to the directory to create
- **Returns**: None
- **Behavior**:
  - Checks if the directory exists
  - Creates the directory and any necessary parent directories if it doesn't exist

### `load_json_file(filepath, default=None)`

Loads and parses a JSON file, with graceful error handling.

- **Parameters**:
  - `filepath` (str): Path to the JSON file to load
  - `default` (dict or None, optional): Default value to return if the file doesn't exist or cannot be parsed
- **Returns**: 
  - The parsed JSON data as a Python object
  - The default value if the file doesn't exist or an error occurs
- **Behavior**:
  - Checks if the file exists
  - Attempts to load and parse the JSON content
  - Returns the default value (empty dict by default) if any errors occur
  - Prints an error message if loading fails

### `save_json_file(filepath, data)`

Saves data to a JSON file.

- **Parameters**:
  - `filepath` (str): Path where the JSON file should be saved
  - `data` (object): Data to save (must be JSON-serializable)
- **Returns**: None
- **Behavior**:
  - Ensures the parent directory exists
  - Serializes the data to JSON format
  - Writes the JSON data to the file
  - Uses UTF-8 encoding and proper indentation for readability
  - Preserves non-ASCII characters with `ensure_ascii=False`

## Usage Examples

### Directory Management

```python
from src.utils import ensure_dir_exists

# Create a directory for storing user data
user_data_dir = os.path.join(os.path.dirname(__file__), "user_data")
ensure_dir_exists(user_data_dir)
```

### Working with JSON Configuration

```python
from src.utils import load_json_file, save_json_file

# Load user preferences
preferences_path = os.path.join(user_data_dir, "preferences.json")
preferences = load_json_file(preferences_path, default={"theme": "dark", "volume": 80})

# Modify preferences
preferences["volume"] = 85

# Save preferences
save_json_file(preferences_path, preferences)
```

## Implementation Notes

- All functions include error handling to prevent crashes
- The `load_json_file` function provides a convenient default value if loading fails
- UTF-8 encoding is used for proper handling of international characters
- JSON files are formatted with indentation for human readability

## Usage in the Project

The utility functions are used throughout the SP34KN0W project for:

1. **Session Directory Management**: Creating directories for session files
2. **Configuration Handling**: Loading and saving configuration data
3. **Technical Glossary**: Managing specialized term definitions
4. **User Preferences**: Handling user preference settings

## Error Handling

- **File Not Found**: Returns the default value
- **Permission Issues**: Prints an error message
- **Invalid JSON**: Returns the default value with an error message

## Best Practices

- Always provide a meaningful default value when using `load_json_file`
- Use appropriate directory paths with `os.path.join` for cross-platform compatibility
- Check the return value from `load_json_file` for expected structure before using
