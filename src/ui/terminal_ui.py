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
    
    def display_welcome(self, language_code, mic_device=None, translate=False):
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
        title = "SP34K-N0W TRANSCRIBER"
        padding = (self.width - len(title)) // 2
        print(" " * padding + title)
        print("=" * self.width)
        print(f"Active language: {language}")
        
         # Display microphone device if available
        if mic_device:
            print(f"Microphone: {mic_device}")
        else:
            print("Microphone: Default")
            
        # Display translation status if specified
        if translate:
            print("Translation: Enabled (to English)")
        
        print("=" * self.width)
        print()
    
    def display_transcript(self, timestamp, text, is_final=False, translation=None):
        """Display a transcript entry with optional translation"""
        self.transcript_count += 1
        
        # If final, add formatting
        prefix = "📝 " if is_final else "🔄 "
        color = "\033[1m" if is_final else ""  # Bold for final transcripts
        reset = "\033[0m" if is_final else ""
        
        # Format and print transcript
        print(f"{color}{prefix}[{timestamp}] {text}{reset}")
        
        # Show translation if available
        if translation:
            trans_prefix = "🌐 "
            print(f"{color}{trans_prefix}[EN] {translation}{reset}")
        
        # Add spacing every few transcripts
        if is_final and self.transcript_count % 5 == 0:
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
        
        
    def display_latency(self, current_latency, avg_latency):
        """Display latency information"""
        if current_latency < 1.0:
            indicator = "✅"  # Good latency
        elif current_latency < 2.0:
            indicator = "⚠️"  # Acceptable latency
        else:
            indicator = "⛔"  # Poor latency
            
        print(f"{indicator} Latency: {current_latency:.3f}s (Avg: {avg_latency:.3f}s)")