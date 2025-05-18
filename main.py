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