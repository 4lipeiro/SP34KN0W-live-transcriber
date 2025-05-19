# SP34KN0W Live Transcriber

## 🎤 Real-time Speech Transcription Tool

SP34KN0W is a powerful, command-line based live transcription tool that converts spoken words into text in real-time. Whether you're in a meeting, lecture, or any situation where you need accurate transcription, SP34KN0W has you covered.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

- **Live Transcription**: Convert speech to text in real-time with minimal latency
- **Multiple Languages**: Support for various languages including Italian, English, French, Spanish, German, and more
- **Translation**: Translate transcriptions to English on-the-fly
- **Session Management**: Automatically save transcripts with detailed metadata
- **Microphone Selection**: Choose from available audio input devices
- **Low Latency**: Optimized for minimal delay between speech and transcription
- **Terminal UI**: Clean, intuitive command-line interface with status indicators
- **Latency Tracking**: Monitor and report transcription delay times

---
## 📝 Version History Note

> **Important:** After v2.0, Linux and Windows versions were developed separately. The documentation referenced throughout this README (located in the `linux` folder) pertains specifically to the Linux version of SP34KN0W.


## 🔄 Latest Versions

| Platform | Version | Status |
|----------|---------|--------|
| Linux & Windows    | v2.0    | Stable |
| Windows  | v2.6    | Beta   |


## Updates v2.6 (windows-v2.6-beta)

Here are the key features and improvements added in this version:

### Display Mode Enhancements

1. **New Side-by-Side Display Mode**
   - Added two-column layout for transcript display
   - Interim transcripts appear on the left side
   - Final transcripts display on the right side
   - Automatic text truncation to fit terminal width

2. **Display Mode Selection**
   - Side-by-side mode is now the default display option
   - Added `--inline` command-line argument to use the traditional inline display instead
   - Toggle between modes using the `set_display_mode()` method
   - improved printing of the interim and final treanscript
   
3. **Improved Visual Formatting**
   - Column separation with vertical line separator (│)
   - Proper alignment of translations under final transcripts
   - Better use of terminal space with dynamic column sizing

4. **Transcript Visibility Improvements**
   - Both interim and final transcripts remain visible on screen
   - Clear visual distinction between interim (🔄) and final (📝) transcripts
   - Translations (🌐) properly aligned with their source text

### How to Use

```
# Use the new default side-by-side display mode
python main.py

# Use the traditional inline display mode
python main.py --inline
```

---

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

Enable translation to English:

```bash
python main.py --language italian --translate
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
====================================================================
                   SP34K-N0W TRANSCRIBER
====================================================================
Active language: English
Microphone: External Microphone
====================================================================

ℹ️ Starting transcription session: 2025-05-18_13-45-22
ℹ️ Using nova-2 model for English
ℹ️ Press Ctrl+C to end the session

ℹ️ Connected to Deepgram
ℹ️ Checking microphone levels (please speak now for 3 seconds)...
ℹ️ Microphone level: 42.5%
ℹ️ Microphone active: External Microphone

🔄 [00:01] This is a test of the SP34KN0W transcription system.
📝 [00:03] This is a test of the SP34KN0W transcription system.

✅ Latency: 0.342s (Avg: 0.356s)
```

## 📝 Session Storage

Transcripts are saved as markdown files in the `sessions` directory, with timestamps and metadata:

```markdown
# Transcription Session: 2025-05-18_13-45-22

- **Date:** 2025-05-18 13:58:33
- **Language:** en
- **Model:** nova-2
- **Microphone:** External Microphone
- **Translation:** Disabled

## Latency Statistics

- **Average:** 0.342 seconds
- **Minimum:** 0.156 seconds
- **Maximum:** 0.897 seconds

## Transcript

**[00:03]** This is a test of the SP34KN0W transcription system.

**[00:06]** The quick brown fox jumps over the lazy dog.
```

## 🔧 Advanced Configuration

SP34KN0W can be configured through command line parameters or by editing the `config.py` file for permanent changes. See the [Configuration Guide](linux/docsconfiguration.md) for detailed information.

## 📚 Comprehensive Documentation

For detailed documentation of all aspects of SP34KN0W, see the [documentation directory](linux/docs).

- [Project Overview](linux/docsoverview.md): High-level overview of SP34KN0W
- [Architecture](linux/docsarchitecture.md): System design and component interactions
- [Installation Guide](linux/docsinstallation.md): Detailed installation instructions
- [Configuration](linux/docsconfiguration.md): Configuration options and customization
- [Core Components](linux/docscore-components/index.md): Detailed documentation of each system component
  - [Transcriber](linux/docscore-components/transcriber.md): Audio capture and transcription
  - [Terminal UI](linux/docscore-components/ui.md): User interface implementation
  - [Utilities](linux/docscore-components/utils.md): Helper functions and tools
  - [Translator](linux/docscore-components/translator.md): Translation capabilities
- [API Integration](linux/docsapi-integration.md): How SP34KN0W interfaces with Deepgram
- [Development Guide](linux/docsdevelopment-guide.md): How to modify and extend SP34KN0W
- [Troubleshooting](linux/docstroubleshooting.md): Solutions to common issues
- [Contributing](linux/docscontributing.md): Guidelines for contributing to the project

## 🤝 Contributing

Contributions are welcome! See the [Contributing Guidelines](linux/docscontributing.md) for details on how to get involved.

## 🧪 Development and Testing

For information on setting up a development environment, testing procedures, and contributing to the project, see the [Development Guide](linux/docsdevelopment-guide.md) and [Contributing Guidelines](linux/docscontributing.md).

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

For solutions to common issues, see the [Troubleshooting Guide](linux/docstroubleshooting.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Acknowledgements

- [Deepgram](https://deepgram.com/) for their excellent speech recognition API
- All contributors and supporters of this project

## 📞 Support

For assistance, please:

1. Check the [documentation](linux/docs)
2. Look through [existing issues](https://github.com/yourusername/SP34KN0W-live-transcriber/issues)
3. Create a new issue if needed

## 📊 Project Status

SP34KN0W is under active development. Check the repository for the latest updates and features.