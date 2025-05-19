# Development Guide

This guide provides information for developers who want to contribute to or modify the SP34KN0W Live Transcriber project.

## Development Environment Setup

### Prerequisites

- **Python 3.6+**: Required for running the application
- **Git**: For version control
- **Text Editor/IDE**: VS Code, PyCharm, or similar
- **PortAudio**: System dependency for audio capture
- **Deepgram API Key**: For testing transcription functionality

### Setting Up a Development Environment

1. **Clone the Repository**

```powershell
git clone https://github.com/yourusername/SP34KN0W-live-transcriber.git
cd SP34KN0W-live-transcriber
```

2. **Create a Virtual Environment**

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. **Install Dependencies**

```powershell
pip install -r requirements.txt
```

4. **Setup Environment Variables**

Create a `.env` file in the project root:

```
DEEPGRAM_API_KEY=your_api_key_here
```

5. **Install Development Tools (Optional)**

```powershell
pip install black pytest pytest-asyncio pylint
```

## Project Structure

```
SP34KN0W-live-transcriber/
├── api-docs/               # Deepgram API reference documentation
├── data/                   # Data files (e.g., glossaries)
│   └── tech_glossary.json  # Technical term definitions
├── docs/                   # Project documentation
├── sessions/               # Saved transcription sessions
├── src/                    # Source code
│   ├── ui/                 # User interface components
│   │   └── terminal_ui.py  # Terminal-based UI
│   ├── transcriber.py      # Core transcription functionality
│   ├── translator.py       # Translation utilities (placeholder)
│   └── utils.py            # Helper functions
├── config.py               # Configuration settings
├── main.py                 # Application entry point
└── requirements.txt        # Dependencies
```

## Development Workflow

### 1. Making Changes

1. Create a new branch for your feature or fix:

```powershell
git checkout -b feature/your-feature-name
```

2. Make your changes, following the coding standards
3. Test your changes thoroughly
4. Commit your changes with clear messages:

```powershell
git commit -m "Add feature: brief description of the change"
```

### 2. Testing

Manual testing can be performed by running the application with debug mode:

```powershell
python main.py --debug
```

#### Writing Tests

Create test files in a `tests` directory (to be created) with naming convention `test_*.py`. For example:

```python
# tests/test_transcriber.py
import pytest
import asyncio
from src.transcriber import DeepgramTranscriber

@pytest.mark.asyncio
async def test_format_timestamp():
    transcriber = DeepgramTranscriber(api_key="dummy_key")
    assert transcriber._format_timestamp(65.5) == "01:05"
    assert transcriber._format_timestamp(3661) == "61:01"
```

#### Running Tests

```powershell
pytest
```

For asyncio tests:

```powershell
pytest tests/test_transcriber.py -v
```

### 3. Code Style

SP34KN0W follows PEP 8 guidelines with some specific preferences:

- **Line Length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Naming**:
  - `snake_case` for functions and variables
  - `CamelCase` for classes

You can use Black for automatic formatting:

```powershell
black src/ main.py config.py
```

### 4. Documentation

When adding or modifying features:

1. Update inline code comments
2. Update relevant documentation in the `docs` directory
3. Update the README if necessary
4. Add your changes to the project's CHANGELOG (if applicable)

## Core Component Modification Guidelines

### Modifying the Transcriber

The `transcriber.py` file contains the core functionality. When modifying:

1. Maintain backward compatibility where possible
2. Add thorough error handling
3. Test with multiple languages
4. Monitor and report performance impact

Example extension - adding speech detection threshold:

```python
def __init__(self, api_key, language="it", ui=None, session_name=None, model="nova-2", translate=False, mic_device=None, speech_threshold=0.2):
    # Existing initialization code...
    self.speech_threshold = speech_threshold
    
    # ...
    
def _check_audio_levels(self):
    # Existing code...
    
    if audio_level < self.speech_threshold:
        self.ui.display_warning(f"Audio level ({audio_level:.1%}) is below threshold ({self.speech_threshold:.1%})")
```

### Modifying the UI

When changing the `terminal_ui.py` file:

1. Ensure all display methods maintain a consistent style
2. Test in different terminal sizes
3. Consider accessibility implications
4. Maintain backward compatibility

Example extension - adding a warning method:

```python
def display_warning(self, message):
    """Display a warning message"""
    print(f"⚠️  WARNING: {message}")
```

### Adding New Components

When adding entirely new components:

1. Create the new module in the appropriate directory
2. Follow existing patterns for initialization and error handling
3. Add appropriate documentation
4. Update the main application to integrate the new component

## Building and Packaging

To create a distributable package:

```powershell
pip install setuptools wheel
python setup.py sdist bdist_wheel
```

## Debugging Tips

### Enabling Verbose Mode

Run with both debug and verbose flags for maximum information:

```powershell
python main.py --debug --verbose
```

### Common Issues

1. **Microphone Access Problems**:
   - Check permissions
   - List available devices with `--list-mics`
   - Try a different microphone

2. **API Connection Issues**:
   - Verify your API key is correct
   - Check your internet connection
   - Verify the Deepgram service status

3. **Audio Processing Problems**:
   - Check microphone levels
   - Ensure proper audio device selection
   - Validate audio format configuration

## Performance Optimization

When working on performance improvements:

1. **Measure First**: Always benchmark before and after changes
2. **Focus Areas**:
   - Audio processing efficiency
   - Latency reduction
   - Memory usage
   - CPU utilization

3. **Optimization Techniques**:
   - Buffer size tuning
   - Asynchronous processing
   - Reducing unnecessary processing
   - Proper resource cleanup

## Contributing Guidelines

1. **Pull Requests**: Submit PRs with clear descriptions of changes
2. **Issues**: Use the issue tracker for bug reports and feature requests
3. **Documentation**: Update documentation for all significant changes
4. **Testing**: Include tests for new functionality
5. **Code Style**: Follow the established patterns and conventions

## Release Process

1. **Version Update**: Update version in appropriate files
2. **CHANGELOG**: Update with list of changes
3. **Documentation**: Ensure docs are up-to-date
4. **Testing**: Perform final testing
5. **Release**: Tag the release in Git
6. **Publication**: Update release packages as needed

## Roadmap and Future Development

Areas for potential development:

1. **GUI Interface**: Develop a graphical user interface
2. **Offline Functionality**: Add offline transcription capabilities
3. **Enhanced Translation**: Implement more robust translation features
4. **Speaker Diarization**: Add support for identifying different speakers
5. **Custom Vocabulary**: Improve handling of specialized terminology
6. **Mobile Support**: Adapt for mobile platforms
7. **Cloud Integration**: Add cloud storage options for transcripts

## Resources for Developers

- [Deepgram API Documentation](https://developers.deepgram.com/docs/)
- [PyAudio Documentation](http://people.csail.mit.edu/hubert/pyaudio/docs/)
- [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [Python Speech Recognition Resources](https://realpython.com/python-speech-recognition/)
