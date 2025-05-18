# Terminal UI Component

The Terminal UI component provides an enhanced text-based user interface for SP34KN0W Live Transcriber v3.0, handling the display of transcriptions, messages, status indicators, and user interactions.

## File Location

`src/ui/terminal_ui.py`

## Dependencies

- `os`: For terminal size detection and system operations
- `sys`: For system-level functions
- `re`: For text processing
- `curses`: For advanced terminal control
- `datetime`: For timestamp formatting
- `threading`: For thread-safe UI updates
- `sys`: For error output handling
- `re`: For text processing
- `datetime`: For timestamp formatting

## Main Class: `TerminalUI`

A class that manages the terminal-based user interface with enhanced features in v3.0.

### Constructor

```python
def __init__(self, use_timestamps=True, bilingual_mode=False)
```

- **Parameters**:
  - `use_timestamps` (bool, optional): Whether to display timestamps (default: True)
  - `bilingual_mode` (bool, optional): Whether to enable bilingual display for translations (default: False)

### Core Display Methods

#### `initialize_screen()`

Initializes the curses screen and sets up the UI structure.

- **Parameters**: None
- **Returns**: None
- **Behavior**:
  - Initializes the curses library
  - Configures color pairs
  - Creates UI layout with header, body, and footer sections
  - Draws ASCII banner and initial UI elements

#### `display_welcome(language_code, mic_device=None, translate=False)`

Displays welcome information in the header.

- **Parameters**:
  - `language_code` (str): Language code for transcription
  - `mic_device` (str, optional): Microphone device name
  - `translate` (bool, optional): Whether translation is enabled
- **Returns**: None
- **Behavior**:
  - Updates header with language, microphone, and model information
  - Sets translation indicator if enabled

#### `display_transcript(timestamp, text, is_final=False, translation=None)`

Displays a transcript entry with optional translation.

- **Parameters**:
  - `timestamp` (str): Formatted timestamp
  - `text` (str): Transcribed text
  - `is_final` (bool): Whether this is a final transcript
  - `translation` (str, optional): Translated text
- **Returns**: None
- **Behavior**:
  - In standard mode: Displays transcript with timestamp
  - In bilingual mode: Shows original and translation side by side
  - Updates or replaces interim results for cleaner display
  - Uses color-coding to differentiate final and interim transcripts

#### `update_status(current_latency=None, avg_latency=None, min_latency=None, max_latency=None)`

Updates the status bar with latency information.

- **Parameters**:
  - `current_latency` (float, optional): Current latency in seconds
  - `avg_latency` (float, optional): Average latency in seconds
  - `min_latency` (float, optional): Minimum latency in seconds
  - `max_latency` (float, optional): Maximum latency in seconds
- **Returns**: None
- **Behavior**:
  - Updates footer with date, application name, and latency statistics
  - Color-codes latency indicator based on performance

#### `display_message(message)`

Displays a general information message.

- **Parameters**:
  - `message` (str): The message to display
- **Returns**: None
- **Behavior**:
  - Prefixes the message with an info indicator
  - Adds message to the transcript area

#### `display_error(message)`

Displays an error message.

- **Parameters**:
  - `message` (str): The error message to display
- **Returns**: None
- **Behavior**:
  - Prefixes the message with an error indicator
  - Highlights in red for visibility

### Control Flow Methods

#### `display_confirmation_prompt()`

Displays a prompt asking for confirmation before starting transcription.

- **Parameters**: None
- **Returns**: bool - True if user confirms, False otherwise
- **Behavior**:
  - Shows prompt in the transcript area
  - Waits for user input (Y/N)
  - Returns result

#### `set_session_state(state)`

Sets the session state indicator in the UI.

- **Parameters**:
  - `state` (str): Session state ("ACTIVE", "PAUSED", or "STOPPED")
- **Returns**: None
- **Behavior**:
  - Updates session state indicator in header
  - Changes color based on state (green for active, yellow for paused, red for stopped)### Event Handling Methods

#### `register_keyboard_handler(pause_callback, resume_callback)`

Registers callbacks for keyboard events.

- **Parameters**:
  - `pause_callback` (callable): Function to call when Ctrl+S is pressed
  - `resume_callback` (callable): Function to call when Ctrl+R is pressed
- **Returns**: None

#### `_keyboard_listener()`

Background thread that listens for keyboard input.

- **Parameters**: None
- **Returns**: None
- **Behavior**:
  - Runs in a separate thread
  - Captures keyboard input
  - Calls appropriate callbacks for Ctrl+S and Ctrl+R

### Helper Methods

#### `_draw_ascii_banner()`

Draws the SP34KN0W ASCII art banner in the header.

- **Parameters**: None
- **Returns**: None

#### `_draw_header(language_code, mic_device, model, latency=None)`

Draws the header with session information.

- **Parameters**:
  - `language_code` (str): Language code for transcription
  - `mic_device` (str): Microphone device name
  - `model` (str): Transcription model name
  - `latency` (float, optional): Current latency for indicator
- **Returns**: None

#### `_draw_footer()`

Draws the footer with keyboard shortcuts and status information.

- **Parameters**: None
- **Returns**: None

#### `_setup_colors()`

Sets up color pairs for the UI.

- **Parameters**: None
- **Returns**: None

#### `_get_latency_color(latency)`

Determines the color for latency display based on value.

- **Parameters**:
  - `latency` (float): Latency in seconds
- **Returns**: curses color pair

#### `cleanup()`

Cleans up the terminal state when exiting.

- **Parameters**: None
- **Returns**: None
- **Behavior**:
  - Restores terminal to original state
  - Closes curses

## Visual Elements

The Terminal UI uses visual elements for clarity:

| Element | Meaning |
|---------|---------|
| 📝 | Final transcript |
| 🔄 | Interim/ongoing transcript |
| 🌐 | Translation |
| ℹ️ | Informational message |
| ❌ | Error message |
| ✅ | Good latency (< 0.5s) |
| ⚠️ | Acceptable latency (0.5s - 1.0s) |
| ⛔ | Poor latency (> 1.0s) |
| [ACTIVE] | Session is active |
| [PAUSED] | Session is paused |
| [STOPPED] | Session is stopped |

## Example Output

```
+-----------------------------------------------------------------------------------+
|   _____ ____ _____ _  _   _  ___   _____      _                                  |
|  / ____/ __ \__  /| |/ | / |/ / | / / _ \    | |                                 |
| | |   | |__) |/ / |   /|   /| |/ // /_\ \   | |                                  |
| | |   |  ___// /_ |  / |  / |   // _____ \  | |                                  |
| | |___| |   /__/ || |  | |  | |\ \/_/   \_\ | |___                               |
|  \____/_|  /____/ |_|  |_|  |_| \_\        |_____|                               |
|                                                                                   |
+============================= LIVE TRANSCRIBER v3.0 ==============================+
| Language: English  |  Microphone: External  |  Model: nova-2  |  Latency: ✅ 0.31s |
+-----------------------------------------------------------------------------------+
| Session: Meeting-2025-05-18                                             [ACTIVE] |
+-----------------------------------------------------------------------------------+

[00:03] This is a test of the SP34KN0W transcription system.

[00:06] The quick brown fox jumps over the lazy dog.

+-----------------------------------------------------------------------------------+
| 2025-05-18 14:12  |  SP34KN0W LIVE  |  Avg: 0.34s  |  Min: 0.15s  |  Max: 0.51s  |
+-----------------------------------------------------------------------------------+
| [Ctrl+S]: Pause  |  [Ctrl+R]: Resume  |  [Ctrl+C]: End Session                   |
+-----------------------------------------------------------------------------------+
```

## Usage Example

```python
# Initialize UI with timestamps and bilingual mode
ui = TerminalUI(use_timestamps=True, bilingual_mode=True)

# Initialize screen
ui.initialize_screen()

# Display welcome information
ui.display_welcome("fr", mic_device="External Microphone", translate=True)

# Register keyboard handlers
ui.register_keyboard_handlers(
    pause_callback=lambda: print("Paused"),
    resume_callback=lambda: print("Resumed")
)

# Display transcript
ui.display_transcript(
    timestamp="00:03",
    text="Bonjour, comment ça va?",
    is_final=True,
    translation="Hello, how are you?"
)

# Update status with latency information
ui.update_status(
    current_latency=0.325,
    avg_latency=0.412,
    min_latency=0.215,
    max_latency=0.623
)

# Set session state
ui.set_session_state("ACTIVE")

# When done
ui.cleanup()
```

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
