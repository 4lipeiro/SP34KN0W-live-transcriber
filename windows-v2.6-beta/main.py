#!/usr/bin/env python3
import argparse
import asyncio
import os
import signal
import sys
import logging
import threading
import time
import msvcrt  # For Windows keyboard handling
from datetime import datetime
from src.transcriber import DeepgramTranscriber, get_available_microphones
from src.ui.terminal_ui import TerminalUI, BANNER
from config import Config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('sp34kn0w')

def parse_arguments():
    parser = argparse.ArgumentParser(description="SP34KN0W Live Transcriber - Real-time transcription tool")
    parser.add_argument("--language", "-l", default="italian", help="Language for transcription (default: italian)")
    parser.add_argument("--list-languages", action="store_true", help="List available languages")
    parser.add_argument("--list-sessions", action="store_true", help="List saved sessions")
    parser.add_argument("--list-mics", action="store_true", help="List available microphone devices")
    parser.add_argument("--session", "-s", help="Name for this session (default: timestamp)")
    parser.add_argument("--inline", action="store_true", help="Use inline transcript display instead of side-by-side")
    parser.add_argument("--translate", "-t", action="store_true", help="Enable translation to English")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug logging")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output of transcript data")
    parser.add_argument("--mic", "-m", help="Microphone device name or index to use")
    parser.add_argument("--no-timestamp", action="store_true", help="Hide timestamps in transcript")
    parser.add_argument("--no-confirmation", action="store_true", help="Skip initial confirmation prompt")
    return parser.parse_args()

def setup_keyboard_handlers(transcriber):
    """Set up keyboard handling for pause/resume"""
    def keyboard_listener():
        try:
            while transcriber.running:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    # Check for Ctrl+S (ASCII 19) and Ctrl+R (ASCII 18)
                    if key == b'\x13':  # Ctrl+S
                        transcriber.pause()
                    elif key == b'\x12':  # Ctrl+R
                        transcriber.resume()
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in keyboard handler: {e}")
    
    # Start keyboard listener in a separate thread
    keyboard_thread = threading.Thread(target=keyboard_listener)
    keyboard_thread.daemon = True
    keyboard_thread.start()

async def main():
    args = parse_arguments()
    config = Config()
    
    # Set debug logging if requested
    if args.debug or args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        if args.verbose:
            logger.debug("Verbose mode enabled - showing all transcript data")
        else:
            logger.debug("Debug logging enabled")
    
    # Handle utility commands
    if args.list_languages:
        print(BANNER)
        print("Available languages:")
        for code, name in config.SUPPORTED_LANGUAGES.items():
            model = config.LANGUAGE_MODELS.get(code, config.DEFAULT_MODEL)
            print(f"  - {name} ({code}) - Model: {model}")
        return
        
    if args.list_sessions:
        print(BANNER)
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
            
    if args.list_mics:
        print(BANNER)
        devices = get_available_microphones()
        print("Available microphone devices:")
        for device in devices:
            default_mark = " (Default)" if device['default'] else ""
            print(f"  {device['index']}: {device['name']}{default_mark} - {device['channels']} channels")
        return

    # Set up session name
    if args.session:
        session_name = args.session
    else:
        session_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Initialize components
    ui = TerminalUI()
    ui.set_show_timestamps(not args.no_timestamp)
    ui.set_display_mode(not args.inline)  # Use side-by-side display unless --inline is provided
    
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
    
    # Get appropriate model for language
    model = config.LANGUAGE_MODELS.get(language_code, config.DEFAULT_MODEL)
    logger.info(f"Using {model} model for {config.SUPPORTED_LANGUAGES[language_code]}")
    
    # Process microphone selection
    mic_device = None
    if args.mic:
        # Try to convert to integer for index-based selection
        try:
            mic_device = int(args.mic)
        except ValueError:
            mic_device = args.mic  # Use as a name
    
    # Display welcome header
    ui.display_welcome(language_code, mic_device=None, translate=args.translate)
    ui.display_message(f"Starting transcription session: {session_name}")
    ui.display_message(f"Using model: {model}")
    if args.translate:
        ui.display_message("Translation to English: ENABLED")
    
    # Initialize transcriber
    transcriber = DeepgramTranscriber(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        language=language_code,
        ui=ui,
        session_name=session_name,
        model=model,
        translate=args.translate,
        mic_device=mic_device
    )
    
    # CHECK AUDIO LEVELS BEFORE CONFIRMATION
    try:
        audio_check = await transcriber.check_microphone()
        if audio_check is None:
            audio_check = {"level": 0.0, "is_low": True, "message": "Failed to check audio levels"}
    except Exception as e:
        logger.error(f"Error during audio check: {e}")
        audio_check = {"level": 0.0, "is_low": True, "message": f"Error: {str(e)}"}
    
    # Get user confirmation after seeing mic levels
    mic_level = audio_check.get("level", 0.0)
    if not args.no_confirmation:
        if not ui.request_confirmation(f"Ready to start transcription with {mic_level:.1f}% mic level. Press 'y' to begin or 'n' to cancel: "):
            print("Transcription cancelled by user.")
            return
    
    # Start the UI
    ui.start()
    
    # Setup keyboard handlers with our custom implementation
    setup_keyboard_handlers(transcriber)
    
    # Set up signal handlers
    def signal_handler(sig, frame):
        ui.display_message("\nShutting down transcription...")
        asyncio.create_task(transcriber.stop())

    signal.signal(signal.SIGINT, signal_handler)
    
    ui.display_message("Press Ctrl+C to end the session, Ctrl+S to pause, Ctrl+R to resume\n")
    
    # Start transcription
    await transcriber.start()
    
    # Wait until transcription is stopped
    await transcriber.wait_for_completion()
    
    ui.display_message(f"\nSession saved to: sessions/{session_name}.md")
    ui.display_message("Thank you for using SP34KN0W Live Transcriber!")

if __name__ == "__main__":
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("Error: DEEPGRAM_API_KEY environment variable not set")
        print("Please set your Deepgram API key with:")
        print("  export DEEPGRAM_API_KEY=your_api_key_here")
        sys.exit(1)
        
    asyncio.run(main())