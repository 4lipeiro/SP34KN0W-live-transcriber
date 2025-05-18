# Project Overview

## What is SP34KN0W?

SP34KN0W Live Transcriber is a Python-based command line application that provides real-time speech transcription capabilities. Using the Deepgram API, it converts audio input from a microphone into text with minimal latency, supporting multiple languages and offering translation features.

## Key Features

- **Real-time Transcription**: Convert speech to text with minimal delay
- **Multi-language Support**: Transcribe in various languages including Italian, English, Spanish, French, German, and more
- **Translation**: Optionally translate transcriptions to English in real-time
- **Microphone Selection**: Choose from available audio input devices
- **Session Management**: Save transcription sessions with timestamps and metadata
- **Terminal UI**: Clean, informative user interface with status indicators
- **Latency Tracking**: Monitor and report transcription delay times

## Use Cases

SP34KN0W is designed for:

- **Meetings and Lectures**: Capture spoken content in real-time
- **Multilingual Environments**: Transcribe and translate multiple languages
- **Accessibility**: Provide text alternatives to audio content
- **Documentation**: Generate text records of spoken discussions
- **Research**: Analyze spoken content with text processing tools

## Project Structure

```
SP34KN0W-live-transcriber/
├── api-docs/               # Deepgram API reference documentation
├── data/                   # Data files (e.g., glossaries)
├── docs/                   # Project documentation
├── sessions/               # Saved transcription sessions
├── src/                    # Source code
│   ├── ui/                 # User interface components
│   ├── transcriber.py      # Core transcription functionality
│   ├── translator.py       # Translation utilities
│   └── utils.py            # Helper functions
├── config.py               # Configuration settings
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```

## Technology Stack

- **Python 3.6+**: Core programming language
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

For a complete list, see the [requirements.txt](../requirements.txt) file.
