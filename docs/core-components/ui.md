# Terminal UI Component

The Terminal UI component provides a clean, text-based user interface for the SP34KN0W Live Transcriber, handling the display of transcriptions, messages, and status indicators.

## File Location

`src/ui/terminal_ui.py`

## Dependencies

- `os`: For terminal size detection
- `sys`: For error output handling
- `re`: For text processing
- `datetime`: For timestamp formatting

## Main Class: `TerminalUI`

A class providing methods for displaying formatted text and status information in the terminal.

### Constructor

```python
def __init__(self)
```

- **Parameters**: None
- **Behavior**:
  - Detects terminal width
  - Initializes counters
  - Clears the terminal screen

### Display Methods

#### `display_welcome(language_code, mic_device=None, translate=False)`

Displays a welcome message with application information.

- **Parameters**:
  - `language_code` (str): The selected language code
  - `mic_device` (str, optional): The selected microphone device
  - `translate` (bool, optional): Whether translation is enabled
- **Returns**: None
- **Behavior**:
  - Prints a formatted header with application name
  - Shows active language
  - Shows microphone information if provided
  - Shows translation status if enabled

#### `display_transcript(timestamp, text, is_final=False, translation=None)`

Displays a transcription entry.

- **Parameters**:
  - `timestamp` (str): Formatted timestamp for the transcript
  - `text` (str): The transcribed text
  - `is_final` (bool, optional): Whether this is a final or interim result
  - `translation` (str, optional): Translated text, if available
- **Returns**: None
- **Behavior**:
  - Formats and displays the transcript with appropriate indicators
  - Uses different formatting for final vs. interim results
  - Shows translation if provided
  - Adds spacing after every few final transcripts

#### `display_message(message)`

Displays a general information message.

- **Parameters**:
  - `message` (str): The message to display
- **Returns**: None
- **Behavior**:
  - Prefixes the message with an info indicator (ℹ️)

#### `display_error(message)`

Displays an error message.

- **Parameters**:
  - `message` (str): The error message to display
- **Returns**: None
- **Behavior**:
  - Prefixes the message with an error indicator (❌)
  - Outputs to stderr instead of stdout

#### `display_latency(current_latency, avg_latency)`

Displays latency information with visual indicators.

- **Parameters**:
  - `current_latency` (float): Current latency measurement in seconds
  - `avg_latency` (float): Average latency measurement in seconds
- **Returns**: None
- **Behavior**:
  - Displays latency values with formatting
  - Includes visual indicators based on latency level:
    - ✅ Good latency (< 1.0s)
    - ⚠️ Acceptable latency (1.0s - 2.0s)
    - ⛔ Poor latency (> 2.0s)

### Utility Methods

#### `_clear_screen()`

Clears the terminal screen.

- **Parameters**: None
- **Returns**: None
- **Behavior**:
  - Uses the appropriate command based on the operating system (cls for Windows, clear for Unix-like)

## Visual Elements

The Terminal UI uses several visual elements for clarity:

| Element | Meaning |
|---------|---------|
| 📝 | Final transcript |
| 🔄 | Interim/ongoing transcript |
| 🌐 | Translation |
| ℹ️ | Informational message |
| ❌ | Error message |
| ✅ | Good latency |
| ⚠️ | Acceptable latency |
| ⛔ | Poor latency |

## Example Output

```
====================================================================
                   SP34K-N0W TRANSCRIBER
====================================================================
Active language: English
Microphone: External Microphone
Translation: Enabled (to English)
====================================================================

ℹ️ Starting transcription session: 2025-05-18_13-45-22
ℹ️ Using nova-2 model for English
ℹ️ Press Ctrl+C to end the session

ℹ️ Connected to Deepgram
ℹ️ Checking microphone levels (please speak now for 3 seconds)...
ℹ️ Microphone level: 42.5%
ℹ️ Microphone active: External Microphone

🔄 [00:01] This is a test of the SP34KN0W transcription system.
📝 [00:03] This is a test of the SP34KN0W transcription system.
🌐 [EN] This is a test of the SP34KN0W transcription system.

✅ Latency: 0.342s (Avg: 0.356s)
```

## Usage Example

```python
# Initialize the Terminal UI
ui = TerminalUI()

# Display welcome message
ui.display_welcome("en", mic_device="External Microphone", translate=True)

# Display informational messages
ui.display_message("Starting transcription session: 2025-05-18_13-45-22")
ui.display_message("Using nova-2 model for English")

# Display transcripts
ui.display_transcript("00:01", "This is a test.", is_final=False)
ui.display_transcript("00:03", "This is a test.", is_final=True, 
                     translation="This is a test.")

# Display latency
ui.display_latency(0.342, 0.356)

# Display error if needed
ui.display_error("Connection lost to Deepgram API")
```

## Implementation Notes

- Uses standard terminal escape sequences for formatting (bold text)
- Adapts to terminal width for proper display
- Provides visual differentiation between different types of content
- Uses stderr for error messages to allow proper logging and redirection
- Adds visual spacing to improve readability of transcripts

## Limitations

- Limited to text-based display (no graphical elements)
- Formatting depends on terminal capabilities
- Fixed-width layout may not adapt well to very narrow terminals
- Does not implement scrollback or history navigation
