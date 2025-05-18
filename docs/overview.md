# Project Overview

## What is SP34KN0W?

SP34KN0W Live Transcriber (v3.0) is a Python-based command line application that provides real-time speech transcription capabilities. Using the Deepgram API, it converts audio input from a microphone into text with minimal latency, supporting multiple languages and offering translation features. Version 3.0 introduces an enhanced UI, improved control flow, and additional customization options.

## Key Features

### Core Functionality
- **Real-time Transcription**: Convert speech to text with minimal delay
- **Multi-language Support**: Transcribe in various languages including Italian, English, Spanish, French, German, and more
- **Translation**: Optionally translate transcriptions to English in real-time with bilingual display (under dev)
- **Microphone Selection**: Choose from available audio input devices
- **Session Management**: Save transcription sessions with timestamps and metadata
- **Latency Tracking**: Monitor and report transcription delay times

### Enhanced UI and Visualization (v3.0)
- **ASCII Banner**: Professional-looking ASCII banner at startup
- **Structured Layout**: Interface with dedicated header, transcript, and footer areas
- **Status Bar**: Shows date, tool name, and real-time latency statistics
- **Dynamic Latency Display**: Color-coded latency indicator in the header
- **Cleaner Transcript View**: Replaces interim results rather than adding new lines
- **Bilingual Support**: Optional split-screen view for original text and translations

### Control Flow Enhancements (v3.0)
- **Initial Confirmation**: Asks for confirmation before starting audio transmission
- **Pause/Resume**: Added Ctrl+S to pause and Ctrl+R to resume transcription
- **Automatic Saving**: Transcripts are saved when paused and at the end of sessions
- **Session Snapshots**: Partial transcripts saved during pause with timestamps

### Additional Parameters (v3.0)
- **--no-timestamp**: Hides timestamps in transcript display and saved files
- **--no-confirmation**: Skips the initial confirmation prompt
- **--translate**: Activates translation mode with bilingual display

## Use Cases

SP34KN0W is designed for:

- **Meetings and Lectures**: Capture spoken content in real-time with the ability to pause/resume
- **Multilingual Environments**: Transcribe and translate multiple languages with side-by-side bilingual display (under dev)
- **Accessibility**: Provide text alternatives to audio content
- **Documentation**: Generate text records of spoken discussions with automatic snapshots
- **Research**: Analyze spoken content with text processing tools
- **Note-taking**: Capture important points with the ability to pause and resume as needed

## Project Structure

```
SP34KN0W-live-transcriber/
├── api-docs/               # Deepgram API reference documentation
├── data/                   # Data files (e.g., glossaries)
├── docs/                   # Project documentation
├── sessions/               # Saved transcription sessions and snapshots
├── src/                    # Source code
│   ├── ui/                 # User interface components
│   │   └── terminal_ui.py  # Enhanced terminal UI with curses
│   ├── transcriber.py      # Core transcription functionality
│   ├── translator.py       # Translation utilities
│   └── utils.py            # Helper functions
├── config.py               # Configuration settings
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```

## Technology Stack

- **Python 3.6+**: Core programming language
- **Curses Library**: Advanced terminal interface control
- **Deepgram SDK**: Speech-to-text API integration
- **PyAudio**: Audio input handling
- **Python-dotenv**: Environment variable management
- **Websockets**: Real-time communication

## Dependencies

The project relies on the following main dependencies:

- `deepgram-sdk`: API client for Deepgram speech recognition
- `pyaudio`: Cross-platform audio I/O library
- `websockets`: WebSocket protocol implementation
- `python-dotenv`: Management of environment variables
- `curses`: Terminal screen handling library

For a complete list, see the [requirements.txt](../requirements.txt) file.

## Keyboard Controls

SP34KN0W v3.0 adds the following keyboard controls:

- **Ctrl+S**: Pause transcription and save a snapshot
- **Ctrl+R**: Resume transcription
- **Ctrl+C**: End session and save the complete transcript

## Future Development

SP34KN0W has several planned improvements:

- Interactive transcript editing during the session
- Word-level confidence highlighting
- Specialized technical term recognition
- Support for custom glossaries and vocabulary
