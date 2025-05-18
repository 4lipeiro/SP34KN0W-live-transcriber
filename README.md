# SP34KN0W Live Transcriber v3.0

![SP34KN0W Logo](https://via.placeholder.com/150x150.png?text=SP34KN0W)

## 🎤 Real-time Speech Transcription Tool

SP34KN0W is a powerful, command-line based live transcription tool that converts spoken words into text in real-time. Whether you're in a meeting, lecture, or any situation where you need accurate transcription, SP34KN0W has you covered.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **Live Transcription**: Convert speech to text in real-time with minimal latency
- **Multiple Languages**: Support for various languages including Italian, English, French, Spanish, German, and more
- **Session Management**: Automatically save transcripts with detailed metadata
- **Microphone Selection**: Choose from available audio input devices
- **Low Latency**: Optimized for minimal delay between speech and transcription
- **Enhanced UI**: Professional ASCII banner, structured layout with dedicated areas, and dynamic status bar
- **Control Features**: Pause/Resume functionality (Ctrl+S/Ctrl+R) with automatic session saving
- **Customization Options**: Configure timestamp display and startup confirmation
- **Latency Tracking**: Monitor and report transcription delay times with color-coded indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or newer
- [PortAudio](http://portaudio.com/) (required for microphone access)
- Deepgram API Key ([Sign up for free](https://console.deepgram.com/signup))

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/SP34KN0W-live-transcriber.git
cd SP34KN0W-live-transcriber
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your Deepgram API key:

Create a `.env` file in the project root:

```
DEEPGRAM_API_KEY=your_api_key_here
```

### Usage

Start a basic transcription session:

```bash
python main.py
```

Specify a language:

```bash
python main.py --language english
```

Enable translation with bilingual display (under dev):

```bash
python main.py --language italian --translate
```

Hide timestamps in display and saved transcripts:

```bash
python main.py --no-timestamp
```

Skip the initial confirmation prompt:

```bash
python main.py --no-confirmation
```

Combine multiple options:

```bash
python main.py --language french --translate --no-timestamp --no-confirmation
```

List available languages:

```bash
python main.py --list-languages
```

List available microphone devices:

```bash
python main.py --list-mics
```

Select a specific microphone:

```bash
python main.py --mic "Microphone Name"
# or by index
python main.py --mic 1
```

Custom session name:

```bash
python main.py --session "Meeting Notes May 2025"
```

For more options:

```bash
python main.py --help
```

## 📊 Sample Output

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

### Bilingual Mode Example

```
+-----------------------------------------------------------------------------------+
| Session: Italian-Lecture-2025-05-18                                     [ACTIVE] |
+-----------------------------------------------------------------------------------+
| ORIGINAL (ITALIAN)                   | TRANSLATION (ENGLISH)                     |
+--------------------------------------+------------------------------------------+
| [00:03] Questo è un test del         | [00:03] This is a test of the SP34KN0W    |
| sistema di trascrizione SP34KN0W.    | transcription system.                     |
|                                      |                                           |
| [00:06] La volpe marrone rapida      | [00:06] The quick brown fox jumps over    |
| salta sul cane pigro.                | the lazy dog.                             |
+--------------------------------------+------------------------------------------+
```

## 📝 Session Storage

Transcripts are saved as markdown files in the `sessions` directory with detailed metadata:

```markdown
# Transcription Session: Meeting-2025-05-18

- **Date:** 2025-05-18 14:15:33
- **Language:** en
- **Model:** nova-2
- **Microphone:** External Microphone
- **Translation:** Disabled
- **Duration:** 12 minutes 38 seconds
- **Status:** Completed

## Latency Statistics

- **Average:** 0.342 seconds
- **Minimum:** 0.156 seconds
- **Maximum:** 0.897 seconds

## Session Snapshots

- **14:08:22** - Pause snapshot (4 min 12 sec)
- **14:12:57** - Pause snapshot (8 min 47 sec)

## Transcript

**[00:03]** This is a test of the SP34KN0W transcription system.

**[00:06]** The quick brown fox jumps over the lazy dog.
```

### Session Snapshots

When you pause a session (using Ctrl+S), SP34KN0W automatically saves the current transcript as a snapshot with a timestamp:

```
sessions/
├── Meeting-2025-05-18.md                 # Complete session
├── Meeting-2025-05-18_14-08-22.md        # First pause snapshot
└── Meeting-2025-05-18_14-12-57.md        # Second pause snapshot
```

## 🔧 Advanced Configuration

SP34KN0W can be configured through command line parameters or by editing the `config.py` file for permanent changes. See the [Configuration Guide](docs/configuration.md) for detailed information.

## 📚 Comprehensive Documentation

For detailed documentation of all aspects of SP34KN0W, see the [documentation directory](docs/).

- [Project Overview](docs/overview.md): High-level overview of SP34KN0W
- [Architecture](docs/architecture.md): System design and component interactions
- [Installation Guide](docs/installation.md): Detailed installation instructions
- [Configuration](docs/configuration.md): Configuration options and customization
- [Core Components](docs/core-components/index.md): Detailed documentation of each system component
  - [Transcriber](docs/core-components/transcriber.md): Audio capture and transcription
  - [Terminal UI](docs/core-components/ui.md): User interface implementation
  - [Utilities](docs/core-components/utils.md): Helper functions and tools
  - [Translator](docs/core-components/translator.md): Translation capabilities
- [API Integration](docs/api-integration.md): How SP34KN0W interfaces with Deepgram
- [Development Guide](docs/development-guide.md): How to modify and extend SP34KN0W
- [Troubleshooting](docs/troubleshooting.md): Solutions to common issues
- [Contributing](docs/contributing.md): Guidelines for contributing to the project

## 🤝 Contributing

Contributions are welcome! See the [Contributing Guidelines](docs/contributing.md) for details on how to get involved.

## 🧪 Development and Testing

For information on setting up a development environment, testing procedures, and contributing to the project, see the [Development Guide](docs/development-guide.md) and [Contributing Guidelines](docs/contributing.md).

## 🔬 Technical Details

SP34KN0W is built with:

- **Python 3.6+**: Core programming language
- **Deepgram SDK**: State-of-the-art speech recognition API
- **PyAudio**: Cross-platform audio I/O
- **Asyncio**: Asynchronous I/O for responsive performance
- **Websockets**: Real-time communication protocol

The system implements:

- **Streaming Architecture**: Real-time audio processing
- **Event-Driven Design**: Responsive to speech events
- **Modular Components**: Easily extensible
- **Error Resilience**: Robust error handling and recovery

## 🔍 Use Cases

SP34KN0W is ideal for:

- **Meetings and Conferences**: Capture discussions in real-time
- **Lectures and Presentations**: Create text records of spoken content
- **Multilingual Environments**: Transcribe and translate multiple languages
- **Accessibility**: Provide text alternatives to audio content
- **Research**: Analyze spoken content with text processing tools
- **Documentation**: Generate text records of verbal discussions

## 💻 System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Processor**: 1.6 GHz or faster
- **Memory**: 2 GB RAM minimum, 4 GB recommended
- **Storage**: 50 MB available space
- **Internet**: Broadband connection required
- **Audio**: Working microphone

## 🛠️ Troubleshooting

For solutions to common issues, see the [Troubleshooting Guide](docs/troubleshooting.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Acknowledgements

- [Deepgram](https://deepgram.com/) for their excellent speech recognition API
- All contributors and supporters of this project

## 📞 Support

For assistance, please:

1. Check the [documentation](docs/)
2. Look through [existing issues](https://github.com/yourusername/SP34KN0W-live-transcriber/issues)
3. Create a new issue if needed

## 🔮 Future Development

Planned enhancements include:

- Graphical user interface
- Enhanced translation capabilities
- Offline mode
- Speaker diarization (identifying different speakers)
- Custom vocabulary training
- Mobile support

## 📊 Project Status

SP34KN0W is under active development. Check the repository for the latest updates and features.