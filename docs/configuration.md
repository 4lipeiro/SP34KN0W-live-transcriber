# Configuration Guide

This guide explains how to configure the SP34KN0W Live Transcriber to suit your needs through both command-line parameters and configuration files.

## Command-Line Parameters

SP34KN0W offers a variety of command-line parameters for flexible configuration:

| Parameter | Shorthand | Description | Default |
|-----------|-----------|-------------|---------|
| `--language` | `-l` | Language for transcription | `italian` |
| `--translate` | `-t` | Enable translation to English | `False` |
| `--session` | `-s` | Name for the transcription session | Timestamp |
| `--mic` | `-m` | Microphone device name or index | System default |
| `--debug` | `-d` | Enable debug logging | `False` |
| `--verbose` | `-v` | Enable verbose transcript data output | `False` |
| `--list-languages` | | List available languages | - |
| `--list-mics` | | List available microphone devices | - |
| `--list-sessions` | | List saved transcription sessions | - |

### Examples

Basic usage with Italian language:
```bash
python main.py
```

Specifying a different language:
```bash
python main.py --language english
```

Enabling translation:
```bash
python main.py --language french --translate
```

Specifying a microphone by name:
```bash
python main.py --mic "External Microphone"
```

Specifying a microphone by index:
```bash
python main.py --mic 2
```

Custom session name:
```bash
python main.py --session "Board Meeting May 18"
```

Enabling debug mode:
```bash
python main.py --debug
```

## Configuration File

The `config.py` file contains default settings and configurations that can be modified for permanent changes.

### Key Configuration Settings

Here are the main settings you can modify in `config.py`:

#### Supported Languages

The `SUPPORTED_LANGUAGES` dictionary maps language codes to their names:

```python
SUPPORTED_LANGUAGES = {
    "en": "English",
    "it": "Italian",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    # Additional languages...
}
```

To add a new language, include it in this dictionary.

#### Language Models

The `LANGUAGE_MODELS` dictionary maps language codes to the appropriate Deepgram models:

```python
LANGUAGE_MODELS = {
    "en": "nova-2",
    "it": "nova-2",
    "fr": "nova-2",
    # Additional language models...
}
```

#### Default Model

The fallback model to use for languages not explicitly defined:

```python
DEFAULT_MODEL = "nova-2"
```

#### Audio Settings

Default audio settings for the transcription process:

```python
# In the DeepgramTranscriber.__init__ method
self.CHANNELS = 1  # Mono audio
self.RATE = 16000  # Sample rate in Hz
```

## Environment Variables

SP34KN0W uses environment variables for sensitive configuration:

| Variable | Description | Required |
|----------|-------------|----------|
| `DEEPGRAM_API_KEY` | Your Deepgram API key | Yes |

These can be set in your system environment or in a `.env` file at the project root.

### Setting Up .env File

Create a file named `.env` in the project root:

```
DEEPGRAM_API_KEY=your_api_key_here
```

## Advanced Configuration

### Custom Directories

You can modify the location where session files are saved by changing:

```python
# In the DeepgramTranscriber.__init__ method
self.sessions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sessions")
```

### Transcription Parameters

Adjust the transcription parameters for different needs:

```python
# In the DeepgramTranscriber.start method
options = LiveOptions(
    language=self.language,
    encoding="linear16",
    channels=self.CHANNELS,
    sample_rate=self.RATE,
    model=self.model,
    smart_format=True,
    interim_results=True,
    utterance_end_ms=1000  # Adjust this value to change how quickly utterances are marked as complete
)
```

### Technical Glossary

The `data/tech_glossary.json` file contains specialized terms with translations. Add or modify terms as needed:

```json
{
  "cybersecurity": {
    "en": "Protection of computer systems and networks",
    "it": "Protezione di sistemi informatici e reti"
  },
  // Add your terms here
}
```

## Configuration Best Practices

1. **API Keys**: Never commit your `.env` file to version control
2. **Custom Sessions**: Use descriptive session names for easier identification
3. **Microphone Selection**: List and test available microphones before starting important sessions
4. **Language Selection**: Verify language support with `--list-languages` before use
5. **Debugging**: Use `--debug` or `--verbose` when troubleshooting issues

## Related Documentation

- [Installation Guide](./installation.md)
- [Core Components](./core-components/index.md)
- [Troubleshooting](./troubleshooting.md)
