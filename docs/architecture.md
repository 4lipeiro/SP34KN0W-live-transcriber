# Architecture

This document provides a comprehensive overview of the SP34KN0W Live Transcriber's architecture, explaining how different components interact and the data flow through the system.

## High-Level Architecture

The SP34KN0W Live Transcriber follows a modular architecture with clearly defined components:

```
┌───────────────┐      ┌───────────────┐      ┌────────────────┐
│               │      │               │      │                │
│  User Input   ├─────▶│  Transcriber  ├─────▶│  Terminal UI   │
│  (Microphone) │      │   Component   │      │                │
│               │      │               │      │                │
└───────────────┘      └───────┬───────┘      └────────────────┘
                               │
                               ▼
                       ┌───────────────┐
                       │               │
                       │  Deepgram API │
                       │               │
                       └───────────────┘
                               │
                               ▼
                       ┌───────────────┐
                       │               │
                       │  Session File │
                       │               │
                       └───────────────┘
```

## Component Descriptions

### Main Application (`main.py`)

The entry point of the application that:
- Parses command-line arguments
- Initializes components based on user configuration
- Handles application lifecycle (start, execution, and shutdown)
- Manages signal handling for graceful termination

### Configuration (`config.py`)

Defines application-wide settings:
- Language mappings and codes
- Model configuration for different languages
- Default values for various parameters
- Command-line argument parsing

### Transcriber (`src/transcriber.py`)

The core component responsible for:
- Initializing the Deepgram client and connection
- Managing microphone input and audio streaming
- Processing transcription responses
- Handling events (open, close, transcript, error)
- Tracking latency and performance metrics
- Saving transcription data to session files

### Terminal UI (`src/ui/terminal_ui.py`)

Provides the user interface for the application:
- Displaying welcome and status messages
- Formatting and presenting transcription results
- Showing error messages and notifications
- Providing visual feedback on latency and performance

### Utilities (`src/utils.py`)

Offers helper functions for various operations:
- File and directory management
- JSON file handling (loading and saving)
- Other utility functions

### Translator (Placeholder) (`src/translator.py`)

Currently a placeholder module, potentially for future enhancements to translation functionality beyond what Deepgram provides.

## Data Flow

1. **User Input**: Audio is captured from the user's microphone
2. **Audio Streaming**: Raw audio data is streamed to the Deepgram API
3. **Transcription Processing**: Deepgram converts speech to text and returns results
4. **Display**: Results are formatted and displayed in the terminal UI
5. **Storage**: Final transcriptions are saved to session files with metadata

## Key Processes

### Initialization

1. Parse command-line arguments
2. Set up configuration based on user inputs
3. Initialize UI component
4. Create and configure Transcriber with appropriate settings
5. Set up signal handlers for graceful termination

### Transcription Cycle

1. Capture audio from microphone
2. Stream audio to Deepgram API
3. Receive interim and final transcription results
4. Process and display results in UI
5. Measure and report latency
6. Save final transcripts and metadata

### Shutdown

1. Handle termination signal (typically Ctrl+C)
2. Close connections gracefully
3. Calculate and display final statistics
4. Save session data to file
5. Display closing messages

## Error Handling

The application implements robust error handling:
- Connection issues with Deepgram API
- Audio device errors
- Invalid configuration parameters
- Runtime exceptions

## Design Patterns

The application utilizes several design patterns:
- **Observer Pattern**: For event handling in the transcription process
- **Dependency Injection**: UI component is passed to the Transcriber
- **Command Pattern**: For processing command-line arguments

## Future Architecture Considerations

Areas for potential architecture improvements:
- Full implementation of the Translator component
- GUI interface in addition to the Terminal UI
- Pluggable backend support for different transcription services
- Enhanced session management and search capabilities
