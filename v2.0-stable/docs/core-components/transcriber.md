# Transcriber Component

The Transcriber is the core component of the SP34KN0W Live Transcriber, responsible for capturing audio, processing it through the Deepgram API, and managing the transcription results.

## File Location

`src/transcriber.py`

## Dependencies

- `asyncio`: For asynchronous operations
- `json`: For data serialization
- `os`: For file and directory operations
- `time`: For timing and performance tracking
- `logging`: For application logging
- `pyaudio`: For audio capture
- `numpy`: For audio data processing
- `deepgram`: For speech-to-text API integration

## Helper Functions

### `ensure_dir_exists(path)`

Ensures a directory exists, creating it if necessary.

- **Parameters**:
  - `path` (str): Path to the directory
- **Returns**: None

### `get_available_microphones()`

Gets a list of available microphone devices on the system.

- **Parameters**: None
- **Returns**: List of dictionaries with device information:
  - `index`: Device index
  - `name`: Device name
  - `channels`: Number of channels
  - `default`: Boolean indicating if this is the default device

## Main Class: `DeepgramTranscriber`

The primary class that handles all transcription functionality.

### Constructor

```python
def __init__(self, api_key, language="it", ui=None, session_name=None, model="nova-2", translate=False, mic_device=None)
```

- **Parameters**:
  - `api_key` (str): Deepgram API key
  - `language` (str, optional): Language code (default: "it" for Italian)
  - `ui` (object, optional): UI component for displaying results
  - `session_name` (str, optional): Name for the transcription session
  - `model` (str, optional): Deepgram model to use (default: "nova-2")
  - `translate` (bool, optional): Whether to translate results to English (default: False)
  - `mic_device` (int or str, optional): Microphone device index or name (default: None, uses system default)

### Core Methods

#### `start()`

Starts the transcription process.

- **Parameters**: None
- **Returns**: None
- **Behavior**: 
  - Initializes the Deepgram connection
  - Sets up event handlers
  - Configures and starts the microphone stream
  - Begins processing audio

#### `stop()`

Stops the transcription process.

- **Parameters**: None
- **Returns**: None
- **Behavior**:
  - Stops the audio stream
  - Closes the Deepgram connection
  - Reports latency statistics
  - Saves the transcript to file

#### `wait_for_completion()`

Waits for the transcription process to complete.

- **Parameters**: None
- **Returns**: None
- **Behavior**: Blocks until the completion event is set

### Event Handlers

#### `_on_open()`

Handles the websocket connection open event.

- **Parameters**: None
- **Returns**: None

#### `_on_close()`

Handles the websocket connection close event.

- **Parameters**: None
- **Returns**: None

#### `_on_transcript(transcript)`

Processes incoming transcript data.

- **Parameters**:
  - `transcript` (dict): Transcript data from Deepgram
- **Returns**: None
- **Behavior**:
  - Extracts transcript text and metadata
  - Calculates and tracks latency
  - Formats and displays results through the UI
  - Stores data for session recording

#### `_on_utterance_end(utterance)`

Handles the end of an utterance event.

- **Parameters**:
  - `utterance` (dict): Utterance data from Deepgram
- **Returns**: None

#### `_on_error(error)`

Handles error events from the Deepgram connection.

- **Parameters**:
  - `error` (Exception): The error that occurred
- **Returns**: None

### Audio Streaming Methods

#### `_stream_microphone_deepgram()`

Streams microphone audio using Deepgram's Microphone class.

- **Parameters**: None
- **Returns**: None

#### `_stream_microphone_custom()`

Streams microphone audio using a custom implementation with PyAudio.

- **Parameters**: None
- **Returns**: None
- **Behavior**:
  - Opens an audio stream with the specified device
  - Reads audio data in chunks
  - Processes and sends audio to the Deepgram API
  - Calculates average audio levels

### Utility Methods

#### `_check_audio_levels()`

Checks microphone audio levels to ensure proper capture.

- **Parameters**: None
- **Returns**: None
- **Behavior**:
  - Captures a short audio sample
  - Calculates and reports audio levels
  - Warns if levels are too low

#### `_format_timestamp(seconds)`

Formats a timestamp in seconds to a human-readable format.

- **Parameters**:
  - `seconds` (float): Time in seconds
- **Returns**: String in MM:SS format

#### `_calculate_latency(transcript_end_time)`

Calculates the latency between speech and transcription.

- **Parameters**:
  - `transcript_end_time` (float): End time of the transcribed audio
- **Returns**: Latency in seconds

#### `_report_latency_stats()`

Reports final latency statistics for the session.

- **Parameters**: None
- **Returns**: None

#### `_save_transcript()`

Saves the complete transcript to a file.

- **Parameters**: None
- **Returns**: None
- **Behavior**:
  - Creates a markdown file with session metadata
  - Includes latency statistics
  - Formats and writes all transcribed text

## Usage Example

```python
# Initialize the transcriber
transcriber = DeepgramTranscriber(
    api_key="your_api_key",
    language="en",
    ui=terminal_ui,
    session_name="Meeting_2025_05_18",
    translate=True
)

# Start transcription
await transcriber.start()

# Wait for completion (e.g., until Ctrl+C is pressed)
await transcriber.wait_for_completion()
```

## Implementation Notes

- Uses `asyncio` for non-blocking operation
- Handles microphone selection based on name or index
- Supports both built-in and custom audio streaming methods
- Calculates and reports detailed latency statistics
- Saves session data in a readable markdown format
- Gracefully handles errors and connection issues

## Error Handling

The Transcriber implements robust error handling for:
- API connection issues
- Audio device problems
- Processing errors
- File I/O operations

## Performance Considerations

- Audio is captured and processed in small chunks for low latency
- Interim results provide real-time feedback
- Statistics are tracked for performance monitoring
- Audio levels are checked to ensure proper capture
