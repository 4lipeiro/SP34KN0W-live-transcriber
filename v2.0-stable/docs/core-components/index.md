# Core Components

This section provides detailed documentation for the core components of the SP34KN0W Live Transcriber.

## Component Overview

The SP34KN0W system consists of several key components, each with specific responsibilities:

| Component | File | Description |
|-----------|------|-------------|
| [Transcriber](./transcriber.md) | `src/transcriber.py` | Core speech-to-text functionality |
| [Terminal UI](./ui.md) | `src/ui/terminal_ui.py` | User interface and display formatting |
| [Utilities](./utils.md) | `src/utils.py` | Helper functions for file operations and data handling |
| [Translator](./translator.md) | `src/translator.py` | Translation functionality (currently a placeholder) |

## Component Relationships

The components interact in the following way:

1. The **main application** (`main.py`) initializes all components and handles program flow
2. The **Transcriber** captures audio and processes it through the Deepgram API
3. The **Terminal UI** displays transcription results and status messages
4. The **Utilities** provide support functions for file handling and data processing

## Component Details

For detailed information about each component, including classes, methods, and function signatures, please refer to the individual component documentation:

- [Transcriber Documentation](./transcriber.md)
- [Terminal UI Documentation](./ui.md)
- [Utilities Documentation](./utils.md)
- [Translator Documentation](./translator.md)

## Component Diagrams

### Dependency Diagram

```
main.py
  ├── config.py
  ├── src/transcriber.py
  │     └── src/ui/terminal_ui.py
  └── src/ui/terminal_ui.py
```

### Data Flow

```
Microphone → Transcriber → Deepgram API → Transcriber → Terminal UI → User
                   │                          │
                   └───────────────────────────→ Session Files
```
