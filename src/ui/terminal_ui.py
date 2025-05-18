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