# D33P-SP34K Transcriber

A real-time transcription tool designed for cybersecurity classes in Italian, with multilingual support and technical term recognition.

## Features

- **Real-time transcription** of live speech using Deepgram's powerful API
- **Primary Italian support** with ability to switch to other languages
- **Automatic saving of transcripts** with timestamps for later review
- **Technical term highlighting** specifically for cybersecurity terminology
- **Simple, clean terminal interface** for distraction-free note-taking
- **Session management** to organize transcripts by class or topic

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/D33P-SP34K-transcriber.git
cd D33P-SP34K-transcriber

# Create and activate virtual environment (recommended)
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up your Deepgram API key
# Either create a .env file or set environment variable:
echo "DEEPGRAM_API_KEY=your_api_key_here" > .env
```

## Project Structure

```
d33p-sp34k-transcriber/
├── README.md                  # Project documentation
├── requirements.txt           # Project dependencies
├── main.py                    # Entry point
├── config.py                  # Configuration settings
├── src/
│   ├── transcriber.py         # Deepgram integration
│   ├── translator.py          # Translation services
│   ├── utils.py               # Helper functions
│   └── ui/
│       └── terminal_ui.py     # Terminal interface
├── data/
│   └── tech_glossary.json     # Cybersecurity terminology
└── sessions/                  # Saved transcription sessions
```

## Quick Start

```bash
# Start a new transcription session
python main.py

# Start with specific language
python main.py --language italian

# List available languages
python main.py --list-languages

# View saved sessions
python main.py --list-sessions
```

## Requirements

- Python 3.8+
- Working microphone
- Internet connection
- Deepgram API key
- PortAudio (for microphone access)

## Code Implementation

Here's the implementation of the core components:

### main.py

```python
#!/usr/bin/env python3
# filepath: main.py
import argparse
import asyncio
import os
import signal
import sys
from datetime import datetime
from src.transcriber import DeepgramTranscriber
from src.ui.terminal_ui import TerminalUI
from config import Config

def parse_arguments():
    parser = argparse.ArgumentParser(description="D33P-SP34K Transcriber - Real-time transcription tool")
    parser.add_argument("--language", "-l", default="italian", help="Language for transcription (default: italian)")
    parser.add_argument("--list-languages", action="store_true", help="List available languages")
    parser.add_argument("--list-sessions", action="store_true", help="List saved sessions")
    parser.add_argument("--session", "-s", help="Name for this session (default: timestamp)")
    return parser.parse_args()

async def main():
    args = parse_arguments()
    config = Config()
    
    # Handle utility commands
    if args.list_languages:
        print("Available languages:")
        for code, name in config.SUPPORTED_LANGUAGES.items():
            print(f"  - {name} ({code})")
        return
        
    if args.list_sessions:
        sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
        if not os.path.exists(sessions_dir):
            print("No sessions found.")
            return
            
        sessions = [f for f in os.listdir(sessions_dir) if f.endswith('.md')]
        if not sessions:
            print("No sessions found.")
            return
            
        print("Available sessions:")
        for session in sorted(sessions):
            print(f"  - {session}")
        return

    # Set up session name
    if args.session:
        session_name = args.session
    else:
        session_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Initialize components
    ui = TerminalUI()
    
    # Language setup
    language = args.language.lower()
    language_code = None
    for code, name in config.SUPPORTED_LANGUAGES.items():
        if language == name.lower() or language == code.lower():
            language_code = code
            break
    
    if not language_code:
        ui.display_error(f"Language '{language}' not recognized. Using default (Italian).")
        language_code = "it"
    
    # Initialize transcriber
    transcriber = DeepgramTranscriber(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        language=language_code,
        ui=ui,
        session_name=session_name
    )
    
    # Set up signal handlers
    def signal_handler(sig, frame):
        ui.display_message("\nShutting down transcription...")
        asyncio.create_task(transcriber.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start UI
    ui.display_welcome(language_code)
    ui.display_message(f"Starting transcription session: {session_name}")
    ui.display_message("Press Ctrl+C to end the session\n")
    
    # Start transcription
    await transcriber.start()
    
    # Wait until transcription is stopped
    await transcriber.wait_for_completion()
    
    ui.display_message(f"\nSession saved to: sessions/{session_name}.md")
    ui.display_message("Thank you for using D33P-SP34K Transcriber!")

if __name__ == "__main__":
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("Error: DEEPGRAM_API_KEY environment variable not set")
        print("Please set your Deepgram API key with:")
        print("  export DEEPGRAM_API_KEY=your_api_key_here")
        sys.exit(1)
        
    asyncio.run(main())
```

### config.py

```python
class Config:
    # Deepgram configuration
    DEEPGRAM_URL = "wss://api.deepgram.com/v1/listen"
    
    # Transcription settings
    DEFAULT_LANGUAGE = "it"
    ENCODING = "linear16"  # Raw PCM audio
    SAMPLE_RATE = 16000   # 16 kHz
    CHANNELS = 1          # Mono audio
    
    # UI Settings
    TERMINAL_WIDTH = 80
    
    # Supported languages with ISO codes
    SUPPORTED_LANGUAGES = {
        "it": "Italian",
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "zh": "Chinese",
        "ja": "Japanese",
        "ru": "Russian"
    }
    
    # Technical terms glossary file
    TECH_GLOSSARY_PATH = "data/tech_glossary.json"
```

### src/transcriber.py

```python
import asyncio
import json
import os
import pyaudio
import wave
import websockets
from datetime import datetime
from deepgram import Deepgram
from src.utils import ensure_dir_exists

class DeepgramTranscriber:
    def __init__(self, api_key, language="it", ui=None, session_name=None):
        self.api_key = api_key
        self.language = language
        self.ui = ui
        self.session_name = session_name or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        self.deepgram = Deepgram(api_key)
        self.websocket = None
        self.running = False
        self.completion_event = asyncio.Event()
        
        # Audio settings
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        
        # Session data
        self.transcript_data = []
        self.current_timestamp = 0
        
        # Create sessions directory
        self.sessions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sessions")
        ensure_dir_exists(self.sessions_dir)
        
    async def start(self):
        """Start the transcription process"""
        # Setup websocket connection
        self.running = True
        
        # Connect to Deepgram
        try:
            connection_params = {
                "language": self.language,
                "encoding": "linear16",
                "sample_rate": self.RATE,
                "channels": self.CHANNELS,
                "model": "nova-3",
                "smart_format": "true",
                "interim_results": "true",
                "utterance_end_ms": "1000"
            }
            
            # Create the websocket connection
            self.websocket = await self.deepgram.transcription.live(connection_params)
            
            # Register event handlers
            self.websocket.registerHandler("open", self._on_open)
            self.websocket.registerHandler("close", self._on_close)
            self.websocket.registerHandler("transcriptReceived", self._on_transcript)
            self.websocket.registerHandler("utteranceEnd", self._on_utterance_end)
            self.websocket.registerHandler("error", self._on_error)
            
            # Start audio streaming
            await self._stream_microphone()
            
        except Exception as e:
            if self.ui:
                self.ui.display_error(f"Failed to start transcription: {str(e)}")
            self.running = False
            self.completion_event.set()
    
    async def stop(self):
        """Stop the transcription process"""
        self.running = False
        if self.websocket:
            await self.websocket.finish()
            self.websocket = None
        
        # Save transcript to file
        await self._save_transcript()
        self.completion_event.set()
    
    async def wait_for_completion(self):
        """Wait until the transcription is completed"""
        await self.completion_event.wait()
    
    async def _stream_microphone(self):
        """Stream microphone audio to Deepgram"""
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            if self.ui:
                self.ui.display_message("Microphone is now active and streaming to Deepgram")
            
            while self.running:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                if self.websocket and data:
                    await self.websocket.send(data)
                await asyncio.sleep(0.01)  # Small delay to prevent CPU overuse
                
        except Exception as e:
            if self.ui:
                self.ui.display_error(f"Error in audio stream: {str(e)}")
            self.running = False
            
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
    
    def _on_open(self):
        """Handle websocket open event"""
        if self.ui:
            self.ui.display_message("Connected to Deepgram")
    
    def _on_close(self):
        """Handle websocket close event"""
        if self.ui:
            self.ui.display_message("Disconnected from Deepgram")
        self.running = False
    
    def _on_transcript(self, transcript):
        """Handle incoming transcript"""
        if not transcript or not transcript.get('channel', {}).get('alternatives'):
            return
        
        # Extract transcript text
        result = transcript['channel']['alternatives'][0]
        text = result.get('transcript', '')
        is_final = transcript.get('is_final', False)
        
        if not text.strip():
            return
        
        # Get timing information
        if 'words' in result and result['words']:
            start = result['words'][0]['start']
            end = result['words'][-1]['end']
            duration = end - start
            # Update timestamp for complete transcripts
            if is_final:
                self.current_timestamp = end
        else:
            start = self.current_timestamp
            duration = 0
        
        # Format timestamp
        timestamp_str = self._format_timestamp(start)
        
        # Store and display transcript
        if is_final:
            self.transcript_data.append({
                "text": text,
                "start": start,
                "end": start + duration,
                "timestamp": timestamp_str
            })
            
            if self.ui:
                self.ui.display_transcript(timestamp_str, text, is_final)
    
    def _on_utterance_end(self, data):
        """Handle utterance end event"""
        if self.ui:
            channel_info = data.get("channel", [0, 1])
            last_word_end = data.get("last_word_end", 0)
            self.ui.display_message(f"[Utterance End Detected at {self._format_timestamp(last_word_end)}]")
    
    def _on_error(self, error):
        """Handle error event"""
        if self.ui:
            self.ui.display_error(f"Deepgram Error: {error}")
    
    def _format_timestamp(self, seconds):
        """Format seconds into MM:SS format"""
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    async def _save_transcript(self):
        """Save the transcript to a markdown file"""
        if not self.transcript_data:
            return
            
        filename = os.path.join(self.sessions_dir, f"{self.session_name}.md")
        
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Transcription Session: {self.session_name}\n\n")
            f.write(f"- **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **Language:** {self.language}\n\n")
            f.write("## Transcript\n\n")
            
            # Write transcript entries
            for entry in self.transcript_data:
                f.write(f"**[{entry['timestamp']}]** {entry['text']}\n\n")
```

### src/ui/terminal_ui.py

```python
import os
import sys
import re
from datetime import datetime

class TerminalUI:
    """Simple terminal UI for displaying transcripts and messages"""
    
    def __init__(self):
        """Initialize the terminal UI"""
        self.width = min(os.get_terminal_size().columns, 80)
        self.transcript_count = 0
        
        # Clear the terminal
        self._clear_screen()
    
    def display_welcome(self, language_code):
        """Display welcome message"""
        language_names = {
            "it": "Italian",
            "en": "English",
            "fr": "French",
            "es": "Spanish",
            "de": "German",
            "zh": "Chinese",
            "ja": "Japanese",
            "ru": "Russian"
        }
        language = language_names.get(language_code, language_code)
        
        print("=" * self.width)
        title = "D33P-SP34K TRANSCRIBER"
        padding = (self.width - len(title)) // 2
        print(" " * padding + title)
        print("=" * self.width)
        print(f"Active language: {language}")
        print("=" * self.width)
        print()
    
    def display_transcript(self, timestamp, text, is_final=False):
        """Display a transcript entry"""
        self.transcript_count += 1
        
        # If final, add formatting
        prefix = "📝 "
        color = "\033[1m" if is_final else ""  # Bold for final transcripts
        reset = "\033[0m" if is_final else ""
        
        # Format and print
        print(f"{color}{prefix}[{timestamp}] {text}{reset}")
        
        # Add spacing every few transcripts
        if self.transcript_count % 10 == 0:
            print()
    
    def display_message(self, message):
        """Display a status message"""
        print(f"ℹ️  {message}")
    
    def display_error(self, message):
        """Display an error message"""
        print(f"❌ ERROR: {message}", file=sys.stderr)
    
    def _clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
```

### src/utils.py

```python
import os
import json

def ensure_dir_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_json_file(filepath, default=None):
    """Load a JSON file, return default if file doesn't exist"""
    if not os.path.exists(filepath):
        return default or {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {filepath}: {str(e)}")
        return default or {}

def save_json_file(filepath, data):
    """Save data to a JSON file"""
    directory = os.path.dirname(filepath)
    ensure_dir_exists(directory)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### data/tech_glossary.json

```json
{
  "cybersecurity": {
    "en": "Protection of computer systems and networks",
    "it": "Protezione di sistemi informatici e reti"
  },
  "malware": {
    "en": "Software designed to harm or exploit systems",
    "it": "Software progettato per danneggiare o sfruttare i sistemi"
  },
  "phishing": {
    "en": "Fraudulent attempt to obtain sensitive information",
    "it": "Tentativo fraudolento di ottenere informazioni sensibili"
  },
  "firewall": {
    "en": "Network security system that monitors traffic",
    "it": "Sistema di sicurezza di rete che monitora il traffico"
  },
  "encryption": {
    "en": "Process of encoding information",
    "it": "Processo di codifica delle informazioni"
  },
  "vulnerability": {
    "en": "Weakness that can be exploited",
    "it": "Debolezza che può essere sfruttata"
  },
  "ransomware": {
    "en": "Malware that encrypts data and demands payment",
    "it": "Malware che cifra i dati e richiede un pagamento"
  },
  "penetration testing": {
    "en": "Authorized simulated attack to evaluate security",
    "it": "Attacco simulato autorizzato per valutare la sicurezza"
  },
  "zero-day": {
    "en": "Previously unknown software vulnerability",
    "it": "Vulnerabilità software precedentemente sconosciuta"
  },
  "backdoor": {
    "en": "Method to bypass authentication",
    "it": "Metodo per bypassare l'autenticazione"
  }
}
```

### requirements.txt

```
deepgram-sdk>=2.12.0
pyaudio>=0.2.13
websockets>=10.4
python-dotenv>=1.0.0
```

## Usage Guide

### Basic Usage

1. Start a transcription session:
   ```bash
   python main.py
   ```

2. Speak clearly into your microphone. The transcription will appear in real-time in the terminal.

3. Press `Ctrl+C` to end the session. The transcript will be saved 