# API Integration

This document details how SP34KN0W Live Transcriber integrates with the Deepgram API for speech recognition and provides information for developers looking to understand or modify this integration.

## Deepgram API Overview

SP34KN0W uses [Deepgram](https://deepgram.com/), a powerful AI speech recognition platform that offers:

- Real-time audio transcription
- Multiple language support
- High accuracy speech recognition
- Low latency processing
- Translation capabilities

## Authentication

SP34KN0W authenticates with Deepgram using an API key, which should be provided as an environment variable:

```
DEEPGRAM_API_KEY=your_api_key_here
```

This API key is loaded from the `.env` file or system environment variables and passed to the Deepgram client during initialization.

## Client Initialization

The Deepgram client is initialized in the `DeepgramTranscriber` class:

```python
from deepgram import DeepgramClient

# Initialize the Deepgram client with the API key
self.deepgram = DeepgramClient(api_key)
```

## Live Transcription Setup

SP34KN0W configures a live transcription connection with specific options:

```python
# Configure the live transcription options
options = LiveOptions(
    language=self.language,
    encoding="linear16",
    channels=self.CHANNELS,
    sample_rate=self.RATE,
    model=self.model,
    smart_format=True,
    interim_results=True,
    utterance_end_ms=1000
)

# Add translation if requested
if self.translate:
    options["translate"] = True

# Create the live transcription connection
self.connection = self.deepgram.listen.live.v("1")
```

### Key Configuration Options

| Option | Description | SP34KN0W Setting |
|--------|-------------|------------------|
| `language` | Language code for transcription | User-selected (default: "it") |
| `encoding` | Audio encoding format | "linear16" (16-bit PCM) |
| `channels` | Number of audio channels | 1 (mono) |
| `sample_rate` | Audio sample rate in Hz | 16000 |
| `model` | Deepgram model to use | Varies by language (typically "nova-2") |
| `smart_format` | Enable formatting of numbers, punctuation, etc. | `True` |
| `interim_results` | Provide partial results while speaking | `True` |
| `utterance_end_ms` | Time of silence to mark end of an utterance | 1000 (1 second) |
| `translate` | Enable translation (optional) | Based on user flag |

## Event Handling

SP34KN0W sets up event handlers for different transcription events:

```python
# Set up event handlers
self.connection.on(LiveTranscriptionEvents.Open, self._on_open)
self.connection.on(LiveTranscriptionEvents.Close, self._on_close)
self.connection.on(LiveTranscriptionEvents.Transcript, self._on_transcript)
self.connection.on(LiveTranscriptionEvents.UtteranceEnd, self._on_utterance_end)
self.connection.on(LiveTranscriptionEvents.Error, self._on_error)
```

### Event Types

| Event | Handler | Purpose |
|-------|---------|---------|
| `Open` | `_on_open` | Connection established |
| `Close` | `_on_close` | Connection closed |
| `Transcript` | `_on_transcript` | Received transcription result |
| `UtteranceEnd` | `_on_utterance_end` | End of a speech segment |
| `Error` | `_on_error` | Error occurred during transcription |

## Audio Streaming

SP34KN0W offers two methods for streaming audio to Deepgram:

### 1. Using Deepgram's Microphone Class

```python
# Create microphone instance
microphone = Microphone(
    push_callback=self.connection.send,
    rate=self.RATE,
    channels=self.CHANNELS
)

# Start streaming from microphone
microphone.start()
```

### 2. Using Custom PyAudio Implementation

```python
# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream with specific device if provided
stream = p.open(
    format=pyaudio.paInt16,
    channels=self.CHANNELS,
    rate=self.RATE,
    input=True,
    input_device_index=self.mic_device_index,
    frames_per_buffer=4096,
    stream_callback=self._audio_callback
)

# Start the stream
stream.start_stream()
```

## Processing Transcription Results

When transcription data is received, SP34KN0W processes it as follows:

```python
def _on_transcript(self, transcript):
    try:
        # Extract data from the transcript
        transcript_data = transcript

        # Get the alternative with the highest confidence
        alternatives = transcript_data.get("channel", {}).get("alternatives", [])
        if not alternatives:
            return
            
        # Extract text, confidence, words, etc.
        transcript_text = alternatives[0].get("transcript", "")
        is_final = transcript_data.get("is_final", False)
        
        # Get translation if available
        translation = None
        if "translation" in alternatives[0] and self.translate:
            translation = alternatives[0].get("translation", {}).get("transcript", "")
        
        # Process and display the transcript
        # ...
    except Exception as e:
        logger.error(f"Error processing transcript: {e}")
```

## Translation Functionality

Translation is handled directly through the Deepgram API by setting the `translate` option to `True`. When enabled, SP34KN0W extracts and displays the translated text:

```python
# Get translation if available
translation = None
if "translation" in alternatives[0] and self.translate:
    translation = alternatives[0].get("translation", {}).get("transcript", "")
    
# Display the translation alongside the transcript
if self.ui and transcript_text:
    self.ui.display_transcript(
        timestamp=self._format_timestamp(current_time), 
        text=transcript_text,
        is_final=is_final,
        translation=translation
    )
```

## Session Data Storage

SP34KN0W saves transcription session data to markdown files, including metadata about the API configuration:

```markdown
# Transcription Session: 2025-05-18_13-45-22

- **Date:** 2025-05-18 13:58:33
- **Language:** en
- **Model:** nova-2
- **Microphone:** External Microphone
- **Translation:** Enabled

## Latency Statistics

- **Average:** 0.342 seconds
- **Minimum:** 0.156 seconds
- **Maximum:** 0.897 seconds

## Transcript

**[00:03]** This is a test of the SP34KN0W transcription system.
```

## API Response Structure

The Deepgram API returns transcript data in the following format:

```json
{
  "channel": {
    "alternatives": [
      {
        "transcript": "This is a test of the SP34KN0W transcription system.",
        "confidence": 0.98,
        "words": [
          {
            "word": "this",
            "start": 0.01,
            "end": 0.25,
            "confidence": 0.99
          },
          // Additional words...
        ],
        "translation": {
          "transcript": "Questo è un test del sistema di trascrizione SP34KN0W."
        }
      }
    ]
  },
  "is_final": true,
  "speech_final": true,
  "channel_index": 0,
  "start": 0.0,
  "duration": 3.5
}
```

## Latency Tracking

SP34KN0W measures and reports the latency between when audio is spoken and when transcription is received:

```python
def _calculate_latency(self, transcript_end_time):
    # Calculate the latency between when audio was spoken and when transcript was received
    now = time.time()
    audio_time = transcript_end_time - self.start_time
    processing_latency = now - (self.start_time + audio_time)
    
    # Store for statistics
    self.latency_measurements.append(processing_latency)
    
    return processing_latency
```

## API Resource Usage

SP34KN0W is designed to use Deepgram resources efficiently:

1. **Connection Management**: The connection is established once per session
2. **Audio Format**: Uses efficient linear PCM audio encoding
3. **Graceful Shutdown**: Properly closes the connection when finished
4. **Error Handling**: Robust handling of API errors

## API Documentation References

For more information about the Deepgram API, refer to the provided API documentation files in the `api-docs` directory:

- `Getting Started.md`: Basic Deepgram API introduction
- `Live Streaming Starter Kit.md`: Guide to real-time transcription
- `Using Interim Results.md`: How to work with partial transcriptions
- `Measuring Streaming Latency.md`: Understanding and optimizing latency
- `End of Speech Detection While Live Streaming.md`: Identifying speech boundaries

## Development Considerations

When modifying the API integration:

1. **API Versioning**: SP34KN0W uses API version "1" (`deepgram.listen.live.v("1")`)
2. **Rate Limits**: Be aware of Deepgram API rate limits for your account
3. **Error Handling**: Always implement robust error handling for API calls
4. **Audio Quality**: Microphone audio quality significantly affects transcription accuracy
5. **Model Selection**: Different language models have varying levels of accuracy and features
