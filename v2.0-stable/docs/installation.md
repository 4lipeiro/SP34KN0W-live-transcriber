# Installation Guide

This guide provides detailed instructions for installing and setting up the SP34KN0W Live Transcriber on different operating systems.

## Prerequisites

Before installing SP34KN0W, ensure you have the following prerequisites:

- **Python 3.6 or newer**
- **PortAudio** (required for PyAudio and microphone access)
- **Git** (for cloning the repository)
- **Deepgram API Key** ([Sign up for free](https://console.deepgram.com/signup))

## Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/SP34KN0W-live-transcriber.git
cd SP34KN0W-live-transcriber
```

## Step 2: Set Up Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid conflicts with other Python projects:

### On Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### On macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

### Installing PortAudio (for PyAudio)

PyAudio requires PortAudio as a system dependency.

#### On Windows

The PyAudio wheel should include PortAudio. If you encounter issues, you can find pre-compiled wheels at:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

```powershell
pip install [downloaded wheel file]
```

#### On macOS

Using Homebrew:

```bash
brew install portaudio
pip install pyaudio
```

#### On Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip
sudo apt-get install portaudio19-dev
pip install pyaudio
```

#### On Fedora/RHEL/CentOS

```bash
sudo dnf install portaudio-devel
pip install pyaudio
```

## Step 4: Set Up Deepgram API Key

1. Sign up for a Deepgram account at [console.deepgram.com](https://console.deepgram.com/signup)
2. Create a new API key in the Deepgram console
3. Create a `.env` file in the project root directory:

```
DEEPGRAM_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual Deepgram API key.

## Step 5: Verify Installation

Run a quick test to ensure everything is working:

```bash
python main.py --list-languages
```

This should display a list of supported languages without errors.

Next, check your microphone setup:

```bash
python main.py --list-mics
```

This will show available microphone devices.

## Troubleshooting Common Installation Issues

### PyAudio Installation Failures

If you encounter issues installing PyAudio:

1. Ensure PortAudio is properly installed
2. Try installing a pre-compiled wheel (Windows)
3. Check compiler settings if building from source

### API Key Issues

If you get authentication errors:

1. Verify your API key is correct
2. Check that the `.env` file is in the correct location
3. Ensure the environment variable is being loaded properly

### Microphone Not Detected

If your microphone isn't showing up:

1. Check system permissions for microphone access
2. Verify the device is connected and enabled
3. Try a different microphone if available

### Other Issues

For other installation problems:

1. Check the console output for specific error messages
2. Verify that all prerequisites are properly installed
3. See the [Troubleshooting](./troubleshooting.md) guide

## Next Steps

After successful installation:

1. Follow the [Configuration Guide](./configuration.md) to customize settings
2. Check the [Core Components](./core-components/index.md) documentation to understand the system
3. Run your first transcription with `python main.py`
